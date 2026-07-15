---
name: ww-overnight-runner
description: Autonomous overnight operation protocol for when you step away for 6+ hours with a work queue. Defines what to decide alone, what to stop for, agent launch strategy, question parking, QA standards, morning handoff format, and failure handling.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Overnight runner

**The problem:** you hand off a multi-hour work queue and walk away, and everything downstream of that moment is a gamble. An agent that stops to ask permission on every judgment call burns the whole night waiting on you. An agent that never stops might quietly delete something, push to main, or send a message it shouldn’t have. Neither failure mode announces itself until morning, and by then it’s too late to redirect.

This is a real contract for working unattended for hours: what to decide alone, what to always stop for, how to launch and parallelize agents, where non-blocking questions get parked instead of asked, what QA standard applies with nobody watching, and what a clean morning handoff actually looks like.

**This is a decision contract, not a process-survival mechanism.** It governs what an agent decides on its own and how it reports back; it has nothing to say about surviving a 5-hour session cap, a closed laptop, or a reboot. If you also need the run to survive those, pair this with a resilience mechanism like the `ww-keepalive` skill (also in this repo): `ww-keepalive` keeps the process alive across interruptions, this skill governs what it does with that time.

---

## When to use

Load this skill when:
- You explicitly say “run overnight”, “work while I sleep”, or “I’ll check in the morning”
- The work queue contains 3+ tasks and you’re stepping away for 6+ hours
- A delegation brief includes “autonomous” or “no check-ins”
- You say “plow ahead”, “keep going”, “use your best judgment”, “don’t stop”, “don’t ask unless truly blocked”, or “finish while I’m away” — these invoke **autonomous mode** (below). A light ask uses on-demand autonomous mode; a 6h+ queue uses the full protocol.

Do NOT use for:
- Short sessions (< 2 hours) — just execute normally
- Tasks requiring external communication (email, chat messages to real people)
- Irreversible infrastructure changes (DNS, production deployments, data migrations)

---

## Autonomous mode (on-demand)

For a single task or short session where you say “plow ahead” / “keep going” / “use your best judgment” — run autonomously **without** the status-board or results-file ceremony. Just the contract below plus a closing recap. (A 6h+ queue uses the full protocol that follows.)

**Autonomy contract.** Treat the instruction as permission to continue through normal uncertainty. Turn routine questions into stated assumptions, pick the smallest reversible option, record why, and keep moving. Do not pause to ask which reasonable option you’d prefer — pick one and note it.

**Decision rules when choosing without you in the loop:** reuse existing patterns before inventing; prefer local, reversible, low-blast-radius changes; keep scope tight to the request; validate with the smallest meaningful test first, then broaden.

**Stop only for true blockers:** missing credentials/secrets/paid access; destructive, irreversible, or production-mutating steps; branch ops, force-push, or deletion you didn’t request; high legal/safety/privacy risk a conservative local choice can’t reduce; a decision you reserved; or a verification failure that repeats where the next fix would be speculative. If blocked, leave a self-contained handoff: what’s done, what blocks, the exact input needed, the next file or command.

**Close with a recap:** Goal · Key decisions + why · Changes · Validation + result · Remaining risk. Keep it factual — never hide skipped validation or judgment calls. End with a one-line status marker (🟢/🟡/🔴, see QA settings).

---

## Pre-flight checklist

Before you step away, confirm:
- [ ] Work queue is written down (task list with priorities)
- [ ] Results file path is established (e.g., `tonight-results.md` at project root)
- [ ] Questions parking file is created or known (see below)
- [ ] Any hard stops are noted (“don’t touch X”, “don’t send Y”)
- [ ] `tonight-results.md` is open in your markdown viewer of choice
- [ ] Status board created (Notion doc, Google Doc, or whatever surface you check from your phone) and its URL saved somewhere you’ll actually see it

---

## Agent launch protocol

### How many agents

- Read `references/agent-launch-details.md` when you need the work-queue-size → agent-strategy table or the agent-type routing table.

### Parallelization rules

- Independent tasks = parallel Task calls in single message
- Dependent tasks = sequential (wait for upstream output)
- Never parallelize tasks that write to the same file
- Each parallel agent gets: task description, results file path, questions file path, hard stops

### Expected patterns (not failures)

**Agents combining tasks:** When two adjacent tasks are closely related, a single agent will often handle both in one pass. This is efficient. Log the combined result as “Task N+M” in the results file. Do not treat it as scope creep.

**Two-pass tasks:** A complex task may get a structural pass (one agent) then a formatting or quality pass (a second agent). The second agent should read the results file and pick up exactly where the first left off. This is a valid pattern — do not re-do the structural work.

---

## Usage budget guardrail

Long parallel runs can exhaust a session’s usage window mid-task. If your platform exposes a usage-tracking command, check before substantial work and between waves. For Claude Code specifically:

```sh
npx -y ccusage@latest blocks --active --json
```

- Default throttle: **≤3 parallel subagents** per wave unless the brief says otherwise.
- Finish the in-flight wave before checking — never kill running subagents to save budget (it loses work).
- If the active usage window is **≥95%**, stop launching new work. Schedule a self-contained resume (`min(3600, secondsUntilWindowClears)`; chain wake-ups for longer waits). On wake, re-check the real window — a new active-block timestamp is stronger evidence than elapsed wall-clock.
- If you pause, note which window is over, the observed usage, when the next check is, and what work remains, in the results file.

---

## QUESTIONS-FOR-YOU protocol

### Where to park non-blocking questions

Create at project root or a shared operations/scratch directory:
```
QUESTIONS-FOR-YOU.md
```

Path convention: if working in a specific project, use that project’s root. For a system-wide overnight session that isn’t scoped to one project, pick one stable path in your own setup and keep using it every time, so it’s always the same place to check in the morning.

### Blocking vs. non-blocking questions

- **Blocking:** Agent cannot proceed without an answer. Log in “Needs answer” section, skip the task, note in results.
- **Non-blocking:** Agent made a call autonomously. Log in “FYI / decisions made” section and keep going.
- Default to non-blocking. Only escalate to blocking if the wrong choice could cause data loss or irreversible harm.

---

## Status board (client-grade)

Stand up a working doc — Notion, a Google Doc, whatever surface you actually check from your phone — at session start. This is your phone check-in interface, so it needs to read like one, not like an engineering log. If you’re building it in Notion specifically, the `notion-docs` skill (also in this repo) covers the markdown quirks (tables, callouts, escaping) you’ll otherwise trip over.

**Creation:** create the page in whatever database or folder you use for working docs. Open it (or share the link) immediately after creation.

**Update cadence:** new round at the top after each phase, or whenever status color changes. Previous rounds become collapsed/toggled sections.

### Skim rules (non-negotiable)

- **3-second glance test.** Top of the page = health callout + 3-column status row. Nothing else above the fold.
- **`Last updated` lives in the health callout.** Bump the timestamp every time you touch the doc. Without it there’s no way to tell at a glance whether the session is still alive.
- **Callouts over prose.** Every status signal, risk, and “needs you” item is a colored callout, not a paragraph. Green healthy, yellow watch, red blocked, blue info, gray log.
- **Emoji as semantic shorthand.** Section headings AND callout icons, so you can scan by emoji at a glance.
- **Tables where tables earn their place.** Scope, decisions, risks, cadence. Every cell scannable: emoji + word, not a sentence.
- **Columns for peer data.** Decisions next to risks. Content sources side-by-side. Don’t stack peers vertically.
- **Collapsible detail everywhere.** Upper doc = callouts + tables + columns. Lower doc = toggles for mass. Don’t stack 40 callouts; use toggles.
- **Dividers as rhythm.** Use them between thematic sections only. Sub-sections don’t get dividers.
- **No blank lines** between paragraphs if your platform handles spacing for you (Notion does).
- **Curly quotes only. Sentence case. First person singular.** Non-negotiable.
- **Decisions capture why, not what.** So a decision made without you can be overruled later, and you both know exactly what’s being overruled.
- **“Need from you” is explicit.** Always. Even if “nothing until morning.”

```markdown
### 🛡️ Guardrails {toggle="true"}
	<callout icon="🚫" color="red_bg">
		**Never**
		- [hard-stop bullet]
	</callout>
	<callout icon="⏲️" color="yellow_bg">
		**Budget**
		- [budget bullet]
	</callout>
```

### Update pattern (rounds 2+)

After each phase (or color change), add a new round at the top:
1. Convert the current top H1 (`# Round N — ...`) to a collapsed/toggled section and indent its content
2. Add the new round as a regular H1 above it, with a refreshed status block pinned above it
3. Keep the decisions log, risks, and “what I need from you” current in the new round — don’t make anyone scroll into an old round to learn what changed

---

## Session resume checklist

Context compaction can happen during a long overnight session. When resuming after compaction:

**The problem:** in-session task-tracking state does not persist across compactions. After resuming, it can show all tasks as pending — even completed ones. Do not trust it.

**On resume:**
1. Read the results file (`tonight-results.md` or equivalent) — this is the ground truth
2. Identify which tasks have result entries = completed
3. Identify which tasks have no result entry = pending or in-flight
4. Check the status board for any updates made after the last results file write
5. Resume from the first unfinished task — do not re-run completed tasks

**The results file is always the authoritative record.** In-session task tracking is for launch coordination only.

---

## QA settings (always-on overnight)

Overnight runs use MAX QA. No exceptions.

### Always active

- **TDD**: tests written before implementation. Red phase must be confirmed.
- Read `references/qa-and-failure-handling.md` when you need the full “always active” QA gate list (steelman, verification agent, QA swarm, TDD, completion-language ban, audit convergence, status-line format).

### Visual verification at breakpoints (UI builds)

For any build that produces visual output (marketing sites, dashboards, landing pages, email templates):

- **Desktop / tablet / mobile screenshots are mandatory at every audit gate.** Standard breakpoints: `1440` / `768` / `390`. Use a headless screenshot tool against the staging URL, save PNGs into `<project>/content/screenshots/<gate>/<page>-<breakpoint>.png`.
- **Screenshots get embedded in the status doc** at each gate via whatever image host you use, so you can review from mobile. Never attach local file paths — they don’t render.
- **A browser MCP’s snapshot tool can be dangerous** on many setups — oversized images (>2000px) have crashed sessions. Prefer a standalone screenshot tool against a published staging URL. If you must use an MCP snapshot tool, scope it to a single element, never the whole page body.
- **If a screenshot returns oversized or fails**, abandon that snapshot and move on. Do NOT retry the same element — that’s how sessions crash.

- Read `references/qa-and-failure-handling.md` when running the per-agent pre-task/post-task checklists.

---

## Morning handoff format

The results file (`tonight-results.md` or equivalent) must render cleanly in whatever markdown viewer you actually use.

**The results file is the ground truth — not in-session task tracking.** That state does not survive context compaction and should not be treated as authoritative. Any reconciliation between task-tracking state and reality should always defer to the results file.

---

## Failure handling

### When an agent fails

1. **Log the failure** in results file: what was attempted, what error occurred, what was tried
2. **Retry once** with a modified approach (not the same approach)
3. **If retry fails**: log it as Failed, skip, move on. Do NOT loop.
4. **If the failure blocks downstream tasks**: note blocked tasks in results, park a question for morning

### Retry strategy

- Read `references/qa-and-failure-handling.md` when you need the before-retry checklist or the after-retry-fails write-up format.

### What constitutes a hard stop (never retry, never skip)

- Writing to production databases without explicit instruction
- Sending messages to real people (email, chat, SMS)
- Deleting files without a backup plan
- Making commits to main/master without flagging
- Exceeding a cost threshold (if visible)

---

## Anti-patterns (overnight-specific)

These are the things that go wrong during autonomous sessions. Avoid them.

### Do not delete data

Never delete files, database records, or git history during an overnight run unless:
- The task explicitly says “delete X”
- A backup exists and its path is logged in results

### Do not send external messages

No emails. No chat messages to real people. No SMS. No calendar invites.
Exception: sending yourself a push notification through whatever tool you already use for that is fine — that’s a note to yourself, not outbound communication.

### Do not commit without flagging

If code changes are ready to commit, create the commit but log it in results. Do not push.
Write the commit message but note: “Ready to push — needs your review.”

### Do not spin without checkpoint

If a task is taking longer than expected, checkpoint:
- Write interim results to the results file
- Note what’s done, what’s remaining
- Continue — but don’t run silently for hours with nothing in the log

### Do not run steelman on yourself

Steelman requires a fresh agent context when used overnight (spawn a separate planning agent, not self-review). Self-steelman introduces self-confirmation bias.

### Do not parallelize writes to the same file

Two agents writing to the same file = race condition = corrupted output. If tasks share an output file, serialize them.

### Do not assume silence means approval

If a task would benefit from your input and the agent chose to proceed autonomously, LOG THAT DECISION. Silence is not a green light — it’s an absence. Autonomous choices should be explicit in results, not buried in the diff.

---

## Quick reference card

```
PRE-FLIGHT
[ ] Hard stops documented ("don't X")

DURING
[ ] Park blocking questions (don't guess on irreversible)
[ ] Never parallelize same-file writes
```

## References

- Read `references/agent-launch-details.md` when picking an agent type for a task, or when an agent naturally combines or two-passes tasks and you want to confirm that’s an expected pattern, not scope creep.
- Read `references/questions-template.md` when you are about to create or write into `QUESTIONS-FOR-YOU.md` and need the exact fill-in-the-blank format.
- Read `references/notion-status-board.md` when you are creating the kickoff round of a Notion-flavored status board, naming its page title, or adding a round 2+ update, and need the exact markup.
- Read `references/morning-handoff-template.md` when you are creating or writing into `tonight-results.md` and need the exact file structure and status emoji key.
- Read `references/real-example.md` when you want a worked example of the overnight protocol run end to end.
- Read `references/quick-reference-card.md` when you want a single condensed checklist covering the whole session lifecycle instead of re-reading each section’s own checklist.
- Read `references/qa-and-failure-handling.md` when verifying a UI build at an audit gate, running the per-agent pre/post-task checklists, or retrying a failed task.
