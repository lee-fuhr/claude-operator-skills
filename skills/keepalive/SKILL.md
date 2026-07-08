---
name: keepalive
description: The single source of truth for standing up a self-relaying overnight worker — a kept-alive `claude -p` loop that survives 5h caps, session death, and reboots and grinds a campaign autonomously while you're away from the keyboard. Stand one up in ~60 seconds for ANY campaign that needs to outlive a single session. This skill OWNS the mechanism (fresh `claude -p`, NEVER `--resume`; the keepalive.sh gates + pgrep-banner liveness + interactive interlock + dual-account failover + `--permission-mode auto`; the user-run one-paste plist install; and THE TASKLIST.MD STANDARD — every campaign scaffolds queue.md + done.md in its lane). Bounded and max-effort AFK-style skills should supply only the POSTURE of the brain and call this skill for the mechanism. Invoke when you say "keepalive", "keep it alive", "stand up a worker", "self-relaying worker", "overnight worker", "make it survive caps", or any autonomous-run skill needs the resilience backbone.
---

# keepalive — the self-relaying overnight worker (single source of truth)

This skill is the ONE place the kept-alive mechanism lives. Before consolidating it here, several
different autonomous-run skills each re-described the same fresh-`claude -p` loop, the same gates,
the same plist install, the same dual-account failover, the same tasklist files — and they drifted
out of sync with each other. Consolidate per skill: any bounded-vs-max-effort sibling skill supplies
only its POSTURE (the brain's personality) and references THIS skill for the mechanism. Fix a
mechanism bug here, once, and every sibling inherits it.

## 🏛 THE ENGINE — one implementation, campaigns are conf files

**The mechanism is code, not a pattern to copy: one canonical `engine.sh`, kept in a stable location
(e.g. `~/.claude/kept-alive/engine.sh`).** Standing up a campaign = write a small `<campaign>.conf`
in the lane + a 4-line shim the plist calls (`exec /bin/bash /path/to/engine.sh /lane/<campaign>.conf`).
NEVER copy-paste a keepalive script again — the copy-drift disease is what this kills. Several
independent lanes needing the *same* binary-path fix or hand-wired quota gate, one at a time, is the
signal that a shared engine was overdue; with the engine, one fix lands everywhere at once.

**Hard-won lesson — bash 3.2 unbound-variable trap.** `launch_once()`'s `"${sp[@]}"` (an optional
`--system-prompt` array) throws `unbound variable` under `set -u` on macOS's default bash 3.2
whenever the optional system-prompt var is unset — true of most real confs. This aborts BEFORE
`claude` is ever invoked, but the nonzero exit can get misread by the retry loop as an ordinary
account cap and retried forever, silently — one production campaign did zero real work for 5
straight days while its own log read as merely "capped." Fix: `"${sp[@]}"` → `${sp[@]+"${sp[@]}"}`,
the standard bash-<4.4-safe idiom. If a campaign is stuck repeating "capped/failed" for many cycles,
check the raw stderr of a manual (non-dry) fire before assuming it's really quota — a silent script
crash reads identically to a cap in this log format.

Conf keys: `KA_LANE KA_BRAIN KA_STATE KA_TAG` (required) · `KA_MODEL` · `KA_PACE`
(single | continuous) · `KA_ACCOUNTS` (main | main,backup | backup,main) · `KA_QUOTA_GATE`
(default 1 — point this at your own deterministic quota-ceiling check, e.g. an 80%-workday /
95%-weekend rule, or whatever cadence fits your subscription) · `KA_INTERLOCK` ·
`KA_LOG/KA_OUTLOG/KA_MIN_CYCLE_SECS`. State json contract: `{not_before?, deadline, complete, heartbeat}`.

**Campaign lane contract (scaffold ALL of these):** `queue.md` (priority tasks) + `done.md`
(dense evidence log, worker-facing) + `CHANGELOG.md` (your primary read) + the conf + state json.
If you keep a broader "what document goes where" standard for projects, treat a campaign lane as
one instance of it — every role, every audience, every update moment should already have a home.

**Changelog format.** If you already have a house changelog standard, use it — the addition THIS
contract needs on top is enforcement: **the changelog entry is part of the chunk-close ritual — a
shipped unit without its entry is NOT complete, and any status line is refreshed in the same
motion.** Any glance surface (a dashboard, a shared doc) should lead with the newest changelog lines,
never read better than the changelog itself.

Test any conf for free: `KA_DRY_RUN=1 engine.sh /lane/<campaign>.conf` — evaluates every gate and
prints the resolved launch command, burns nothing. Deploy engine/conf changes via `mv` (atomic — a
running bash script must never be edited in place while a fire could be mid-read of it).

---

## ⚠️ THE ONE NON-NEGOTIABLE MECHANISM LESSON (read this first)

**The kept-alive must launch a FRESH `claude -p "$(cat resume.md)"` each fire — NOT `claude -p --resume <SESSION_ID>`.**

Two campaigns were once stood up with a session-resume scaffolder instead. Both **failed silently
on every single fire** with `No conversation found with session ID …` → `exit 0` → **zero work all
night**. Root cause: `claude -p --resume <SID>` cannot reattach to a **live interactive session's**
id (only headless-spawned sessions are resumable that way), and it couples the loop to fragile
session state regardless.

**The robust pattern:** the loop re-reads a **brain file** (`resume.md`) and starts a fresh stateless
`claude -p` with that brain as the prompt every fire. The brain carries ALL context and tells the
worker to **reconcile against `done.md` / `queue.md` / `state.json` and never redo finished work.**
Statelessness IS the feature — it survives caps, session death, and reboots, because there is no
session to lose.

(Exception, if you have a strong in-thread preference: `claude -p --resume <SID> --permission-mode auto`
can resume the SAME session in-thread for full-context continuity — but ONLY on a session you KNOW
was headless-spawned and resumable, never a live interactive session's id, and it loses dual-account
failover, since a different account can't resume another account's session. Default to fresh-`claude -p`
for resilience.)

---

## The mechanism (what this skill owns)

### 1. The keepalive.sh gates — exit cleanly, in order, on any
`templates/keepalive.sh` checks, in this order, and exits 0 on any (re-checked inside the loop too —
one early bug had a fallback path skip the STOP re-check and spin chunks overnight):
1. `STOP` file present → exit (the kill-switch; you can drop it to halt everything).
2. `time.time() > state.deadline` → exit (deadline is an absolute epoch timestamp).
3. `state.complete` → exit (the worker sets this true when the queue is dry).

### 2. pgrep-banner liveness (real, not heartbeat)
The brain prints a unique `__PGREP_TAG__` banner at the very start of every chunk. The keepalive
does `pgrep -f __PGREP_TAG__`: **present → a chunk is genuinely running, skip; absent → relaunch
regardless of heartbeat age.** This is more reliable than trusting `state.heartbeat`, which a long
dense tool-run can let go stale and trigger a double-drive. The banner is load-bearing — the brain
template instructs the worker to print it first thing.

### 3. Interactive interlock
A live cockpit session writes `interactive.pid` + keeps a fresh heartbeat. The keepalive **stands
down** while that PID is alive AND its heartbeat is fresh (<1800s) AND the pid-file is recent
(<7200s); it **resurrects headless** the instant the cockpit caps/closes (heartbeat goes stale). The
deal: tab open → you drive; tab closed → the headless worker carries on; reopen → back in control.
Two workers on one non-git tree = last-write-wins collision, so this interlock is mandatory.

**Known gap: this interlock has NO valid signal from a pure chat session.** It assumes the cockpit is
a wrapper script with a stable, externally-`kill -0`-able PID. An interactive chat session has no
such handle — a PID captured from one shell call was confirmed alive, then a real engine fire in the
very next call proceeded straight past the check because that PID was already dead (each shell
invocation isn't guaranteed to share a process). The correct move when scaffolding a campaign FROM a
chat session (not a wrapper script): do not write a fake `interactive.pid`. Set `KA_INTERLOCK=0`
explicitly in the conf with a comment explaining why, and load the plist only when actually stepping
away from the chat, not while it's open — your own load/unload action becomes the real interlock.
Do not ship a false sense of protection.

### 4. Dual-account failover
Primary token first, fall to a backup account on cap, so a 5h limit on one account doesn't stall the
lane (e.g. two token files at stable paths, separate quotas). The template tries primary, greps the
output for cap signals, and retries the whole chunk on backup. A single-flight `.launch.lock`
(1800s stale-steal) prevents double-fire; a 45s spin-guard pauses if a chunk returns instantly
(failing fast) instead of hammering.

### 5. `--permission-mode auto` — NEVER `--dangerously-skip-permissions`
Recent Claude Code releases have the auto-mode safety classifier **BLOCK creating a
`--dangerously-skip-permissions` loop** (it reads as "create unsafe agents"), so a skip-permissions
keepalive won't even install — the write of it gets denied. `--permission-mode auto` keeps the
classifier ON: it auto-approves safe work (in-scope edits, reads, builds, tests, declared deps,
memory writes, scheduling) and auto-denies the dangerous classes (prod deploy, blind --force,
irreversible local destruction, creating more unsafe agents, credential exfil). In headless `-p` a
denied action is skipped gracefully (no hang) — the loop grinds the safe work and stages the risky
thing for you. (Some prod deploys DO proceed under auto if transcript intent is present; write the
brain to stage-and-note held deploys rather than fight the gate.)

---

## THE TASKLIST.MD STANDARD (mandatory — every campaign scaffolds this)

**Every keepalive campaign scaffolds `queue.md` + `done.md` in its lane.** This is non-negotiable and
the reason it's a STANDARD, not a per-campaign choice:

- **`queue.md`** — the durable, priority-ordered backlog. Opening it works in ANY session.
- **`done.md`** — append-only, VERIFIED units only. The worker reads it every resume and SKIPS
  anything recorded (this is the ONLY thing keeping a stateless relay from redoing finished work).

Why a standard: the worker is stateless by design, so its memory MUST live on disk in a predictable
place. Because the files are plain markdown in the lane, **they survive caps, session death, and
reboots, and opening `queue.md` / `done.md` gives you (or any fresh session) the live state from
anywhere** — no session to resume, no tool to query. queue.md is what you're working toward; done.md
is what's verified done; together they ARE the campaign's task list. `state.json` carries the
machine flags (deadline/complete/heartbeat); the two .md files carry the human-readable work. Never
let a dashboard/glance surface read better than these two files.

---

## How to stand one up in 60 seconds

Templates live in `./templates/` (this skill's dir). Pick a slug, scaffold the lane, parameterize,
hand yourself the one-paste plist install. **The agent should NOT self-install the plist** — the
auto-mode classifier blocks an agent creating an autonomous loop for itself, so `launchctl load` is a
one-paste block you run yourself. The agent scaffolds the files; you arm the loop.

```bash
# 1. Pick a SESSION-UNIQUE slug (two concurrent lanes sharing a slug clobber each other).
SID="${CLAUDE_CODE_SESSION_ID:-$(date +%s)}"
SLUG="ka-${SID:0:8}-mylane"                 # first 8 of the session id + a short lane name
LANE="$HOME/path/to/your/campaigns/_${SLUG}" # wherever this campaign's state dir should live
TAG="KEEPALIVE-${SLUG^^}-WORKER"            # unique pgrep banner the brain prints each chunk
LABEL="com.yourname.${SLUG}-keepalive"
SKILL="$HOME/.claude/skills/keepalive/templates"

# 2. Scaffold the lane from templates (THE TASKLIST STANDARD: queue.md + done.md always).
mkdir -p "$LANE"
cp "$SKILL/keepalive.sh" "$SKILL/resume.md" "$SKILL/queue.md" "$SKILL/done.md" "$SKILL/state.json" "$LANE/"

# 3. Parameterize. Replace the placeholders:
#    keepalive.sh : __PGREP_TAG__ -> $TAG ;  __WORKDIR__ -> the repo/target to cd into (or $LANE)
#    resume.md    : __PGREP_TAG__ -> $TAG ;  __MISSION__/__POSTURE__/__SCOPE__/__GROUNDING_DOCS__
#                   (a bounded-vs-max-effort sibling skill supplies POSTURE; fill MISSION + SCOPE
#                   from the campaign)
#    queue.md/done.md/state.json : __CAMPAIGN__/__PHASE__ -> real values
# 4. Seed state.json: started=now, heartbeat=now, deadline=absolute epoch (e.g. now + 18h), complete=false.
# 5. Write queue.md with the real priority-ordered backlog (each item with a Done test).
```

**Then hand yourself this one-paste plist install (you run it — the agent does not):**

```bash
LABEL="com.yourname.<slug>-keepalive"; LANE="$HOME/path/to/your/campaigns/_<slug>"
cat > ~/Library/LaunchAgents/$LABEL.plist <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>$LABEL</string>
<key>ProgramArguments</key><array><string>/bin/bash</string><string>$LANE/keepalive.sh</string><string>$LANE</string></array>
<key>StartInterval</key><integer>900</integer>
<key>RunAtLoad</key><false/>
<key>StandardOutPath</key><string>$LANE/keepalive.out</string>
<key>StandardErrorPath</key><string>$LANE/keepalive.err</string>
</dict></plist>
PLIST
launchctl unload ~/Library/LaunchAgents/$LABEL.plist 2>/dev/null; launchctl load ~/Library/LaunchAgents/$LABEL.plist
echo "loaded $LABEL — fires every 15min, RunAtLoad false"
```

Note the plist passes `$LANE` as the keepalive's `$1` (the state dir), so a copied script can never
point back at the original lane. If you keep a registry of what background services are running on
your machine, register the new LaunchAgent there at install time — an unregistered background
process is the kind of thing that gets rediscovered confused, months later.

**To STOP it:**
```bash
LABEL="com.yourname.<slug>-keepalive"; LANE="$HOME/path/to/your/campaigns/_<slug>"
touch "$LANE/STOP"                                          # halt the next fire immediately
launchctl unload ~/Library/LaunchAgents/$LABEL.plist        # tear the loop down
rm ~/Library/LaunchAgents/$LABEL.plist                      # remove it
# (or set state.json complete=true to let it self-exit on the next fire)
```

---

## The heartbeat (optional but recommended)
For the interactive interlock + a recent-activity signal, touch the heartbeat from the working
session each meaningful turn: `templates/` does not include a heartbeat script because it's a
one-liner — `python3 -c "import json,time;p='$LANE/state.json';s=json.load(open(p));s['heartbeat']=time.time();json.dump(s,open(p,'w'))"`.
The pgrep-banner is the primary liveness signal; the heartbeat is the interlock + freshness signal.

---

## How a bounded/max-effort sibling skill should call this

Any skill that runs a bounded (one-task-per-cycle, delegate-and-verify) or max-effort
(workflows-spawning-workflows) autonomous overnight worker should STOP duplicating the mechanism and
reference this skill instead. Each keeps ONLY its posture section (the brain personality) and adopts
a one-line reference for the entire resilience backbone:

> **Resilience backbone:** stand up the kept-alive via the `keepalive` skill (`~/.claude/skills/keepalive/SKILL.md`) — it owns the fresh-`claude -p` mechanism (never `--resume`), the keepalive.sh gates + pgrep-banner liveness + interactive interlock + dual-account failover + `--permission-mode auto`, the user-run one-paste plist install, and the tasklist.md standard (queue.md + done.md scaffolded in the lane). This skill supplies ONLY the brain's POSTURE for the `resume.md` template's `__POSTURE__` slot: bounded = one bounded unit/cycle, the top-tier model writes specs + QCs, cheap models execute, no fan-out. Max-effort = workflows-spawning-workflows, audit-gated, use the quota.

That single line replaces: the "THE ONE NON-NEGOTIABLE MECHANISM LESSON" block, the keepalive.sh
template, the gates list, the interlock paragraph, the dual-account paragraph, the `--permission-
mode auto` block, the plist/StartInterval instructions, and the queue.md/done.md description — all
of which now live HERE. A sibling skill shrinks to: when-to-use, Step-0 framing, and the POSTURE.

---

## Self-improvement
When a mechanism bug is found (a gate that didn't fire, a liveness false-positive, a failover that
stalled), fix it HERE in `templates/` + this doc — once — and every sibling skill inherits it. Do NOT
patch a per-campaign copy and leave the template stale; that re-creates the drift this skill exists
to kill — one canonical home per thing.
