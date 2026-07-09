---
name: weekend-burn
description: The SCHEDULED / RECURRING sibling of the on-demand AFK family (keepalive = the resilience mechanism; go-ham = on-demand unbounded max-effort; qq-go-afk-smart = on-demand bounded delegate-and-verify; go-lean = token-source posture). Weekend burn is a standing, every-weekend cadence (not a one-off campaign) that fires automatically inside a recurring window (e.g. Friday evening through Sunday night) and burns the full weekly Claude subscription quota before it resets, finishing ONE real capability completely before starting the next so a productive weekend ships many finished things and never a pile of half-done ones. Builds on the `keepalive` skill for the actual resilience mechanism (fresh `claude -p`, gates, dual-account failover) and adds the recurring-schedule + self-healing kill-switch layer on top. Invoke when you say "weekend burn", "set up a weekend burn", "burn the quota", "run every weekend", "standing weekly cadence", "recurring autonomous campaign", "use the whole week's quota", or want a repeating (not one-off) autonomous run that finishes real, categorical capabilities on a schedule instead of running once and stopping.
---

# Weekend burn: the recurring, quota-burning cadence

**One-line pitch:** a subscription-quota-based Claude plan resets weekly. Most of that quota goes unused because nobody is driving it on a Saturday. Weekend burn is a standing schedule that drives it anyway: automatically, every week, inside a recurring window, with enough discipline that it produces *finished capabilities*, not a pile of half-touched projects.

This skill does not reinvent the resilience mechanism. It is a thin, opinionated layer on top of `keepalive` (fresh `claude -p` each fire, the gate order, dual-account failover, the queue.md/done.md tasklist standard) that adds two things keepalive doesn't own: **a recurring calendar schedule** (so it fires itself every week without being re-invoked) and **a finish-discipline doctrine** (so a long unattended run produces done things instead of many started things).

---

## Where this sits in the family

| Skill | Shape | Decides | Use when |
|---|---|---|---|
| **keepalive** | mechanism | how a loop survives caps, session death, reboots | any campaign below needs the actual resilience engine |
| **go-ham** | on-demand, one-off | pace = unbounded max-effort | a single big ambitious build, run once, "blow me away" |
| **qq-go-afk-smart** | on-demand, one-off | pace = bounded, one task/cycle | a single finite punch-list, run once, calm and cheap |
| **go-lean** | posture, either pace | token source = external stack over Claude | the Claude cap is the binding constraint on any run above |
| **weekend-burn (this skill)** | **standing, recurring** | **when the whole thing fires, and what "done" means across a long unattended run** | **you want a schedule installed once that then runs itself every week, spending the full weekly quota, until you turn it off** |

**The distinction that matters:** go-ham, qq-go-afk-smart, and go-lean are all invoked *on a task*: you hand over a campaign, a posture gets applied, it runs once (however long "once" takes) and finishes. Weekend burn is invoked *once, to install a schedule*; after that, it fires itself every week on calendar time, with no re-invocation, until you tear it down. It composes with the pace/posture skills (a weekend burn can run its cycles in a HAM-like fan-out or a SMART-like bounded style, and can wear LEAN's externalize-first posture); what it adds on top is the *when* and the *finish discipline*.

---

## The philosophy (the part that makes it produce results, not motion)

### The prime directive: finish one thing completely

> Finish one thing completely. Get to a new categorical capability. Don't spread across a dozen tasks and ship nothing.

Work one project at a time, carried to a real terminal state before the next one starts. This is about **sequence, not a cap**: a genuinely productive burn finishes *many* projects across a weekend. But each one is finished, staged, or explicitly blocked before the next begins. The single failure to avoid at all costs: handing the human a pile of slightly-advanced-but-still-unfinished things when the window closes. Every fire pulls the current project, works it to a real terminal state (shipped, staged-for-review, or genuinely blocked), then, and only then, pulls the next item from the backlog.

**A "categorical capability" is something that didn't exist before and changes what the human can do**, not "cleaned up some files" or "diagnosed an issue."

| Category | Example |
|----------|---------|
| Revenue / value | A store that earns; a billing flow that invoices automatically |
| Automation | A pipeline that runs without a human touching it |
| Quality | A system that self-heals a whole class of failure |
| Distribution | Content that publishes to a channel unattended |
| Instrumentation | A metric that exists, has a threshold, and alerts on breach |

"Diagnosed the issue" is not a capability. "Fixed the issue and it no longer occurs" is.

### Intake standard: nothing enters the queue undefined

New work doesn't land in the backlog raw. Whatever surfaces it, a session, the human, an agent, an audit, passes intake first. An item is **ready** only when it has:

- **A clear definition of done**: the observable finish line ("pages live, all N return 200, submitted to the index"), not a mood ("improve the thing"). If it can't be stated, it isn't ready.
- **A priority**: where it sits in the order, and why.
- **An autonomy tag**: fully autonomous, or which specific steps need a human decision.

**A fuzzy item is never skipped and never dropped.** It enters tagged `needs-definition`, and its *first* unit of work is to get clear: draft the definition of done, stage the 1–3 questions only the human can answer. Progressing a fuzzy item toward clarity IS progress under the prime directive above. The one thing that must never happen: identified work sitting undefined and unprioritized until it's forgotten. This is the front door that stops "someone should look into X" from rotting into a line nobody can act on.

### Definition of done: "the code ran" is not done

Before marking any project complete, confirm:

- The capability exists and is **observable** (URL live, test passes, payment received, whatever "real" looks like for this item, not "the script exited 0").
- Any human-gated steps are staged with a clear "here's what you do, takes N minutes" summary.
- The evidence log has the terminal entry.
- The backlog item is marked done.

**"The code ran" is not done.** "The pages are live, returning 200, and indexed" is done.

### Human-gated ≠ blocked

If a project has a step only a human can approve (a payment, a irreversible send, a judgment call), the agent does everything autonomous first, stages the decision so it takes under two minutes, marks the project "staged, awaiting review," and moves to the next one. It does not abandon the project, and it does not sit idle waiting; it descends the backlog. No project rotation otherwise: don't touch project B because project A is waiting on a human. Finish A's autonomous work, stage it, then start B.

### Model strategy: a lean orchestrator, not a lean output

The run should follow the efficient-frontier pattern: the top-level agent is a **lean orchestrator** doing roughly 5% of the actual work (planning, judgment, synthesis, final review) and delegating the other ~95% (research, extraction, repetitive edits, grunt work) to cheaper model tiers and external models. The expensive model orchestrates; cheaper tiers and externals execute. This is what makes "burn the whole weekly quota" compatible with "finish real things": the quota gets spent on volume of *delegated* work, reviewed and integrated by the orchestrator, not on the orchestrator doing everything itself token-by-token. See your model-routing rules for the specific tiering (typically: free/cheap external models for research, extraction, summarization, and critique; the mid-tier for harder synthesis and adversarial review; the top tier reserved for judgment calls, architecture, and voice/copy, which cheap models reliably damage).

**The one exception: `needs-definition` gets your single most capable model, once, for one job only.** A fuzzy item is by definition the most ambiguous, judgment-heavy thing in the whole backlog, that's exactly why it isn't ready yet. Don't burn the lean orchestrator's own limited judgment turning it into a spec through trial and error; call in the top-tier model for ONE narrow job: write a definition of done so clear and prescriptive that the orchestrator can afterward run the item through the normal cheap/free/orchestrator-tier pipeline with no further judgment calls of its own. That model never executes the item and never touches an already-defined backlog item; it only writes the definition, then hands off completely and the item re-enters standard routing. One pass, one job, narrow by design.

### Reflection instruments: proactive, in-flight, not an end-of-run confessional

These are worth far more used early and often than saved for a closing retrospective. A retrospective just documents the miss; using them in-flight prevents it.

- **At project start: pre-mortem before building.** "If this ships and breaks in three months, what's the single most likely reason?" Answer it about the *approach*, before writing anything, and let the answer change the design. A gate, not a note.
- **Continuously, as work happens: surface, don't stockpile.** The moment an ambiguity gets filled with a guess, write the assumption to the log ("assuming X because Y") *before* building on it, while it's still cheap to be wrong. The moment friction bites (a workaround, a repeated failure), drop a one-line note right then. Friction is captured when felt, not reconstructed later.
- **At the end of each fire: fresh eyes, not self-validation.** Route anything shipped to a *different* model than the one that built it for an independent check. A model defends its own work; a fresh one won't. A real hole found gets fixed or logged before anything is called done.
- **Track quota utilization across the run.** The point of a quota-burning cadence is to actually use the quota: record roughly how much of the week's capacity got spent, ideally approaching full utilization before the reset. Unused quota at reset is wasted, not saved.

---

## The mechanism: keepalive plus a recurring window gate

Weekend burn is `keepalive`'s mechanism (see that skill for the full mechanism: fresh `claude -p` per fire, the gate order, the interactive interlock, dual-account failover, `--permission-mode auto`) with two additions layered on top:

### 1. A pure, stateless window function

Instead of a fixed `StartInterval` loop that fires constantly, weekend burn fires on a **calendar schedule** and gates every fire on "is this actually inside the window right now." Compute the window fresh from the current weekday/hour on every call, never from a stored date. A hardcoded epoch window is a bug waiting to happen: it silently stops working the moment the first window it was written for ends, and nothing tells you.

```python
def in_window(now: datetime) -> bool:
    """True if `now` (local time) falls inside the recurring burn window.

    Recomputed from now's weekday/hour every call — correct every week,
    forever, with zero config maintenance. Example shape: Friday evening
    through Sunday night, all of Saturday in between. Adjust the exact
    bounds to taste.
    """
    dow = now.weekday()  # Monday=0 ... Sunday=6
    if dow == 5:                 # all day Saturday
        return True
    if dow == 4:                 # Friday, from the evening on
        return now.hour >= 20
    if dow == 6:                 # Sunday, until late night
        return now.hour < 23
    return False
```

Test this function directly (it's pure, no I/O, trivially unit-testable) rather than trusting three different hand-rolled bash/python copies to stay in sync across a launcher, a watchdog, and a status surface. One tested source of truth, imported everywhere the window matters.

### 2. A calendar-driven fire schedule

Schedule the launcher via `StartCalendarInterval` entries (not a bare interval) covering the window at your chosen cadence: e.g. every two hours across the whole window, plus the window's opening moment. Each fire: check the window function, check the kill switch (below), check whether the backlog has unchecked work, and only then invoke the keepalive engine for a chunk. A separate lightweight watchdog on its own interval (every few hours is plenty) checks for silent stalls: a fire that should have happened and didn't.

### 3. A governing doc every fire reads first

The pattern that makes "one project at a time" actually hold across dozens of independent, stateless fires: a single doc (call it `GOVERNING-DOC.md` in the lane) that carries the prime directive, the intake standard, the definition-of-done rules, the reflection instruments, the kill-switch semantics, and, updated every cycle, an **"active project"** pointer naming exactly what's being worked right now and what's already finished. Every fire reads this doc first, finds the active project, works only that project until it's done or staged, and only then updates the pointer and descends to the next backlog item. This is what stops a stateless relay of independent `claude -p` calls from turning into N sessions each nibbling a different unfinished thing.

This doc is a specialization of the `queue.md` + `done.md` tasklist standard keepalive already requires; the addition here is the standing doctrine (prime directive, intake, definition of done) plus the single "active project" spotlight that enforces sequencing across fires that share no memory with each other.

---

## The kill switch: self-healing, never silently dark

A recurring, unattended cadence has one structural risk keepalive's mechanism doesn't fully cover on its own: **a halt that nobody remembers to clear.** A single stray word in a kill-switch file can silently stop a weekly cadence for weeks, with every fire reading it, exiting clean, and telling nobody. A crash-only watchdog sees a clean exit and thinks all is well.

The fix is that **the word you write decides what happens if you forget it there:**

- **`PAUSE` = temporary.** Halts now, but auto-resumes after a set TTL (48 hours is a reasonable default) if the window opens again with work still queued, and it announces itself once, the moment it takes effect. Use PAUSE for "skip this instance": it self-heals so it can never go silently dark.
- **`STOP` = deliberate hold.** Halts and stays down until the file is cleared. Never auto-resumes. If it sits stale with work still queued, the guard nags once per window so a long, deliberate hold can't be forgotten either.
- **Anything else** is treated as an unrecognized halt and flagged loudly, never silently obeyed as if it meant something specific.

The invariant this buys: in a burn window with queued work, the system is **either executing, or someone has been told exactly why not.** No third state (silently doing nothing) is allowed to exist. Implement this as a small, pure `classify(content) -> decide(state, age) -> Decision` core (fully unit-testable, no I/O) plus a thin CLI wrapper the launcher and watchdog both call before doing anything else.

---

## Standing one up

1. **Pick a lane**, a directory that will hold the schedule's state: the governing doc, the backlog, `queue.md`/`done.md`, `CHANGELOG.md`, `state.json`, the kill-switch file, and logs.
2. **Write the window function** (above) and its tests. Confirm it returns true/false correctly for the boundary hours, not just the middle of the window.
3. **Scaffold the keepalive engine** into the lane per the `keepalive` skill. The campaign lane contract (`queue.md`, `done.md`, `CHANGELOG.md`, the conf/state) is identical here; weekend burn doesn't change that contract, it just adds the calendar gate and the governing doc on top.
4. **Write the governing doc**: prime directive, intake standard, definition-of-done rules, reflection instruments, kill-switch semantics, and an "active project" section that gets rewritten every cycle. Seed the backlog with real, intake-passed items (each with a definition of done, a priority, and an autonomy tag, no exceptions).
5. **Write the launcher**: checks the window function, checks the kill switch, checks whether the backlog has unchecked work, then invokes the keepalive engine for one chunk. Exits cleanly (not an error) on any negative check.
6. **Write a watchdog** on a longer interval that flags a fire that should have happened and didn't; a stale-log check is enough; it doesn't need to know anything the launcher doesn't already know.
7. **Hand off the calendar schedule for install**: same rule as keepalive. The agent scaffolds the files; the human installs the actual recurring trigger themselves (the platform's autonomous-loop safety classifier blocks an agent creating a self-triggering unattended schedule for itself). Give a one-paste install block and a matching teardown block.
8. **Confirm the loop is genuinely idle-safe.** With no kill switch present and an empty backlog, a fire inside the window should do a short, honest health pass and stop. Never manufacture work just because the schedule fired.

---

## What good looks like at the end of a burn

- A changelog entry (or equivalent) for every finished unit, in plain language, with the status line refreshed to reflect where things actually stand.
- A dense evidence log for every claimed "done": the observable proof, not the narrative claim.
- The active-project pointer in the governing doc accurately reflects what's finished, what's in flight, and what's staged for human review.
- A quota-utilization number for the week, so the next planning cycle knows whether the schedule is actually being used or quietly under-firing.
- Nothing marked done that was only "the code ran."

---

## Self-improvement

When a mechanism bug specific to the *recurring* layer turns up (a window boundary off by an hour, a kill-switch edge case, a watchdog false-positive), fix it here and in the window/guard functions, once. Mechanism bugs shared with plain on-demand campaigns belong in `keepalive` instead; don't let this skill's copy of the mechanism drift from that one.
