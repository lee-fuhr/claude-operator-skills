---
name: qq-mailbox
description: Two-role coordination mailbox for multi-Claude-session handoffs (build cockpit <-> overseer, or any two-or-more named roles). Append-only JSONL, atomic cursor, kind taxonomy with action hints. Load when building or debugging a coordination lane between concurrent Claude sessions.
triggers:
  - “mailbox skill”
  - “coordination lane”
  - “send to overseer”
  - “check the mailbox”
  - “build cockpit overseer handoff”
  - “two sessions coordinate”
metadata:
  filePattern: []
  bashPattern: []
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Mailbox — coordination between concurrent Claude sessions

Hardened, reusable version of a pattern that ran ad hoc all night in a live
build: two Claude sessions (a “build” cockpit and an “overseer”) passing
messages via append-only JSONL files. This skill turns that into something
any two (or more) concurrent sessions can reuse with functional role names,
instead of every pair inventing its own ad-hoc protocol.

**Implementation:** `mailbox.py` (this directory)
**Tests:** `test_mailbox.py` (core, pure I/O against `tmp_path`) +
`test_mailbox_concurrency.py` (race safety with real threads; one test in
here reads a real production lane and is `skipif`-gated to skip cleanly on
any machine that doesn’t have that specific path)

## Load this skill when

- Standing up a new coordination lane between two or more concurrent Claude
  sessions (a build session and a QC/overseer session, two build sessions on
  different subsystems, a headless `ww-keepalive` worker and its live counterpart)
- Debugging an existing lane’s `_sync/` directory (message ordering, cursor
  state, why a role isn’t seeing a message)
- Someone is about to hand-roll a new ad-hoc JSONL handoff file — stop them,
  point here instead
- **A human is manually relaying a message from one live session into
  another** (pasting text someone else’s session produced, because the two
  sessions have no shared lane yet). That relay is the exact cost this skill
  removes. If it looks like it’ll happen more than once for this same pair
  of sessions, say so and offer to stand up a lane instead of letting the
  human keep carrying messages by hand.

## Why not just paste a prompt between two chat windows?

That’s the whole point this skill answers. `check()` needs only the lane
directory and a role name — it finds its own inbound file(s), reads what’s
new since its own last read, and returns a categorized digest with the
taxonomy’s expected-next-action already attached. No human relaying context
between two windows, no re-explaining state on every handoff.

## The two calls

```python
from mailbox import send, check

def send(lane_dir, *, from_role, to_role, kind, msg,
         needs_reply=False, ref=None, artifacts=None) -> dict:
    """Atomically append one envelope to
    <lane_dir>/_sync/<from_role>-to-<to_role>.jsonl.
    Returns the written envelope, including a generated `id`."""

def check(lane_dir, *, role, from_role=None) -> dict:
    """Read every unread line from <lane_dir>/_sync/<from_role>-to-<role>.jsonl
    (or every *-to-<role>.jsonl if from_role is None, merged chronologically
    across senders), using `role`'s own cursor state. Returns
    {"unread": [...], "by_kind": {...}, "action_needed": [...]} -- grouped
    and annotated using KIND_TAXONOMY, not a raw text dump."""
```

### Design invariants (why it’s built this way)

1. **One append-only JSONL file per DIRECTED pair of roles, never one shared
   file.** A role only ever appends to files where it is the sender — no two
   processes can ever collide on the same file’s write, by construction, no
   lock needed for the append itself.
2. **Structured envelope wrapping free text, not replacing it.** `kind`
   labels the message’s category for triage; `msg` stays full free-form
   prose. The taxonomy adds triage, it never constrains what can be said.
3. **Acknowledgment is a NEW message, never an edit to someone else’s
   line.** The receiver, if replying, appends its own reply to ITS OWN
   outbound file, referencing the original message’s `id` via `ref=`.
   Append-only holds everywhere, no exceptions.
4. **Cursor state is atomic (temp file + `os.replace()`) and
   monotonic** — it never moves backward, even under two `check()` calls
   racing on the same lane. Worst case under a race: a message gets
   re-surfaced to more than one caller once. It is never lost, and the
   cursor file is never left malformed. Re-processing a re-surfaced message
   safely (e.g. de-dupe on `id`) is the CALLER’s job, not this module’s.
5. **Role names are functional, never model names.** Use seat/job names
   (`builder`, `overseer`, `qc`) so the lane survives a model rotation —
   don’t hardcode which model happens to sit in which seat this week.
6. **`check()` needs only the lane.** Given a lane directory and a role, it
   finds its own inbound file(s) and its own cursor — no config, no prompt
   pasting.

## Kind taxonomy (v1 — extend as needed, never restrictive)

| kind | expects a reply of | action hint |
|---|---|---|
| `design-task` | `design-delivered` | architect the thing described, drop a spec, reply when ready |
| `design-delivered` | — (terminal) | a spec is ready, go read the referenced file |
| `build-task` | `build-delivered` | implement per the referenced spec |
| `build-delivered` | — (terminal) | implementation done, evidence attached |
| `qc-verdict` | — (unless `needs_reply`) | informational; act only if `needs_reply: true` |
| `question` | an answer, any kind | blocks — `needs_reply` is implicitly true |
| `reconnect` | — (terminal) | presence ping, no action |

A `kind` outside this table is never an error — it gets a generic hint
(“No defined action for this kind — read the message and use judgment.”)
and is fully readable via `check()`‘s `by_kind` grouping. The real lane this
was built for used 60+ distinct ad-hoc kind values across one night
(`headless-cycle`, `qc-catch-fixed`, `overseer-role-breach-standdown`,
`dossier-redesign-handoff`...) — the taxonomy is meant to grow with real
usage, not gate it.

`action_needed` (part of `check()`’s return) surfaces a message if ANY of:
the envelope sets `needs_reply: true` explicitly, the kind’s taxonomy entry
marks it as implicitly needing a reply (`question`), or the kind expects a
specific reply kind (`design-task`, `build-task`). Terminal kinds
(`design-delivered`, `build-delivered`, `reconnect`) and `qc-verdict` without
an explicit `needs_reply: true` are informational only.

## Worked example — a real concurrency-redesign handoff

This is a lightly-formatted real exchange from the night this skill was
extracted from, showing the pattern it hardens: a `design-task` sent by the
builder, a `design-delivered`-shaped reply from the overseer once the spec
was ready.

**1. Builder sends a design task** (`opus-build` -> `fable-qc-headless`):

```python
send(
    lane_dir="ea-pm-consolidation",
    from_role="opus-build",
    to_role="fable-qc-headless",
    kind="design-task-concurrency-redesign",
    msg=(
        "DESIGN TASK (you architect; a build session implements from your "
        "spec -- do not build/test/deploy anything yourself).\n\n"
        "The concurrency + role-lock design has now failed TWO independent "
        "adversarial rounds. This is genuine high-level architecture work... "
        "[full context, open questions, and the deliverable spec follow]"
    ),
    needs_reply=False,
)
```

(Real production used a bespoke kind name,
`design-task-concurrency-redesign`, rather than the taxonomy’s generic
`design-task` — that’s fine. `check()` falls back to the generic hint for
any kind it doesn’t recognize; it never blocks or errors on an unfamiliar
kind. If you want the taxonomy’s specific `design-task` action hint, use
that exact kind string.)

**2. Overseer checks the lane and sees it:**

```python
result = check(lane_dir="ea-pm-consolidation", role="fable-qc-headless")
# result["by_kind"]["design-task-concurrency-redesign"] -> [the envelope above]
# result["unread"][0]["_hint"] -> generic hint (bespoke kind, not in v1 taxonomy)
```

**3. Overseer replies on its OWN outbound file once the spec is ready**
(`fable-qc` -> `opus-build`):

```python
send(
    lane_dir="ea-pm-consolidation",
    from_role="fable-qc",
    to_role="opus-build",
    kind="concurrency-v05-design-ready",
    msg=(
        "CONCURRENCY + ROLE-LOCK v0.5 DESIGN READY: "
        "concurrency-rolelock-v0.5.md (fresh doc, supersedes the parked "
        "spec; the earlier failure's lessons are its spine). The "
        "architecture in one line: THREE STATE PLANES that never mix -- "
        "work in git (worktree-isolated), COORDINATION entirely OUTSIDE "
        "git... [full architecture summary, adversarial-review notes, and "
        "rollout plan follow]"
    ),
    needs_reply=False,
)
```

**4. Builder checks and picks it up:**

```python
result = check(lane_dir="ea-pm-consolidation", role="opus-build")
# result["unread"][0]["msg"] -> the design-ready summary above
# result["unread"][0]["from"] -> "fable-qc"
```

Note the real lane also shows why role-name-vs-filename consistency matters
going forward: the FILES were named by short aliases (`opus`, `fable`) fixed
early, while the `from`/`to` FIELD values inside envelopes drifted to
longer, more specific role names over the session (`opus-build` ->
`opus-cockpit-qqstatus-live`, `fable-qc` -> `fable-qc-headless`).
`send()`/`check()` derive the filename directly from whatever
`from_role`/`to_role` you pass — pick role names once, per lane, and keep
using them, rather than letting them drift the way the ad-hoc version did.

## Common mistakes this skill prevents

- **Don’t** invent a new shared JSONL file both roles append to — that’s the
  exact collision risk the directed-pair-of-files design eliminates by
  construction.
- **Don’t** edit an existing line to “mark it read” or “update its status” —
  append-only is load-bearing for crash safety and for the atomic-write
  guarantee. A reply is always a new message.
- **Don’t** hardcode a model name as a role (`opus`, `fable-qc`) if the lane
  might outlive a model rotation — use a functional seat name instead
  (`builder`, `overseer`).
- **Don’t** assume an unfamiliar `kind` will error — it won’t. Extend
  `KIND_TAXONOMY` in `mailbox.py` when a new kind recurs enough to deserve a
  real action hint; until then the generic hint is enough to keep working.

## Getting notified without polling by hand

`check()` on its own is pull-only — nothing tells you a message arrived until
you call it. That's a real gap, found in production use: a session doesn't
know to check unless something external prompts it to.

**Don't fix this with a `UserPromptSubmit` hook.** That only fires when the
human user types something to the session — it does nothing for the actual
need, which is the session noticing on its own and coming to the human. A hook
keyed to the user's own input can't do that by construction.

**Use a persistent background monitor over a poll loop instead** (Claude
Code's `Monitor` tool, if your environment has one, or any equivalent
long-running-process-with-notifications mechanism) — each new-mail event
becomes a real, unprompted notification, not something surfaced only on the
session's next turn:

```bash
cd /path/to/mailbox.py's/directory && while true; do
  python3 -c "
from mailbox import check
r = check(lane_dir='/path/to/lane', role='your-role')
for m in r['unread']:
    first_line = m['msg'].splitlines()[0][:180] if m['msg'] else ''
    flag = ' [NEEDS REPLY]' if m.get('needs_reply') else ''
    print(f\"[qq-mailbox] {m['from']} -> your-role ({m['kind']}){flag}: {first_line}\")
"
  sleep 15
done
```

**The event firing is the trigger to actually work, not just a log line to
glance at.** Found this needed spelling out explicitly: a first pass at this
treated the poll loop's output as a passive notification — print a summary,
leave it for later. That's not the point. When this fires, read the full
message (`check()` again, or keep the envelope from the loop), do whatever
it actually calls for, and reply on your own outbound file if warranted — in
that same turn, visibly, the same way you'd act on anything the human said
to you directly. A monitor that only ever prints a preview line is barely
better than pure polling; the value is in treating "mail arrived" as
equivalent to "someone just spoke to you," not in having a nicer log.

This works cleanly because `check()`'s cursor is already idempotent and
monotonic (see the design invariants above) — polling it on a loop never
re-surfaces an already-seen message, so no separate "last seen" bookkeeping is
needed. Run it as a persistent watch so it survives for the length of the
session. This is a session-scoped fix, not a standing system service — it
stops when the session ends. If mail needs to be surfaced even when no
session is active, that's a different, bigger ask (a real background service)
and shouldn't be reached for by default.
