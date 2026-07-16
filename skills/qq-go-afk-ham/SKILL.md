---
name: qq-go-afk-ham
description: The unbounded end of the AFK spectrum: spend whatever it takes for quality, budget isn’t the constraint. Stand up a self-healing, fully-autonomous “kitchen-sink max-effort” campaign for a big multi-day initiative: resilience first, creative meta strategy, workflows spawning workflows, audit-gated quality, a phone-glanceable status surface with a proud wins list, and a long living tasklist. Invoke when you say “go HAM”, “go-ham”, “go afk ham”, “qq-go-afk-ham”, “kitchen sink”, “blow me away”, “use all the quota”, or hand it a large ambitious build to run autonomously for hours or days. For the frugal end, use `qq-go-afk-lean`; for the adaptive middle, use `qq-go-afk-smart`.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Go AFK HAM: max-effort autonomous campaigns

**The gap this closes:** a big, ambitious, multi-day build either needs you at the keyboard the whole time, or it runs unattended and you come back to a session that died five hours in, a queue nobody touched since, and no reliable way to tell what actually got built versus what an agent merely claimed. Go HAM is the answer when the initiative is worth maximum quality and maximum quota: a resilience layer so the campaign survives caps and session death and resumes in minutes rather than hours, real strategic thinking instead of a flat task dump, and an audit gate on every key step so nothing ships on a self-report. The result is a campaign you can point at something genuinely ambitious and walk away from, and come back to real, verified progress instead of a stalled session or a pile of unverified claims.

**When to reach for HAM over SMART:** the work is open-ended, ambitious, or exploratory, you want maximum quality and are fine spending real quota to get it, and the value is in finding a compounding advantage and building a system rather than grinding a fixed list. If the backlog is finite and mostly mechanical instead, use `qq-go-afk-smart`.

**The order is not negotiable: resilience first, then strategy, then surfaces, then execution.** Set up the ability to survive the night before you plan what to build with it.

---

## Step 0: frame it

Capture the goal, the deadline (convert it to an absolute timestamp), the budget or quota signal you’re working within, and the autonomy level, usually: full, nobody’s watching.

Pick a session-unique slug for the campaign, never a fixed name reused across runs, since two concurrent HAM lanes sharing a slug will clobber each other’s state directory, LaunchAgent label, and keepalive. The `ww-keepalive` skill in this collection covers the actual slug mechanics (derive it from the session id plus a short lane name) and the state-directory layout; use its pattern rather than inventing your own.

## Step 1: resilience first

Stand up the kept-alive via the `ww-keepalive` skill in this collection before anything else. It owns the fresh-`claude -p` mechanism (never `--resume`), the gates, pgrep-banner liveness, the interactive interlock, dual-account failover, and `--permission-mode auto`, plus the `queue.md` / `done.md` tasklist standard. HAM supplies only the posture for the resume brain: **max effort, workflows spawning workflows, audit-gated, spend whatever it takes for quality.**

Also keep an in-session scheduled wakeup running between chunks so you keep grinding while the LaunchAgent stays the cross-session backstop. Together, no long stalls.

## Step 2: the meta, get creative

Before building anything, write a real plan with actual strategic thinking, not a task dump. Find the point that compounds: where’s the system instead of a pile of disconnected islands, the multiplier, the thing that makes everything after it easier? Sequence phases for compounding effect, not chronology: build the shared foundation before the twenty leaf features that depend on it. State a non-negotiable quality bar. This is the part that gets judged hardest; make it sharp and specific.

## Step 3: surfaces

A phone-glanceable status surface (a Notion working doc, see `ww-notion-docs` in this collection for the actual formatting patterns, or your own dashboard): a glance section, then immediately a pinned wins callout holding the pithy, proud-of-this list, the things worth telling someone about. Rewrite that callout in place as wins accumulate; don’t let new rounds push it down the page. Below that, the plan plus an activity log.

A long living tasklist: phase-level tasks and per-item tasks. Let it grow long, update status every chunk so the thread never gets lost.

## Step 4: ideate, if the scope includes deciding what to build

Run parallel ideation across a few distinct lenses, each one externalizing to a free or cheap model for genuine divergence rather than one model talking to itself, then a top-tier synthesis pass that dedupes, scores, and prioritizes into a real build queue. Write the queue into state and mint tasks from it.

## Step 5: execute, workflows spawning workflows, audit-gated

Workflows are the engine: pipeline or parallel fan-out for the work itself, and a meta-workflow can spawn sub-workflows one level deep. Default to a pipeline; use a hard barrier only when you genuinely need every result before continuing.

Externalize the grunt work, research, extraction, copy, critique, to the cheap and free model stack (see `qq-externalize` in this collection); keep synthesis and judgment on your own tier. If your main quota is tight, a second account can run a parallel builder.

**Audit gate at every key step, no exceptions.** Before any item advances, run a genuinely thorough convergent adversarial review across every dimension that matters for what you’re building, plus build and live verification with a `ww-rule15`-style PASS / PARTIAL / COSMETIC / BROKEN verdict. Surface every issue, fix everything short of the truly trivial, and re-verify until it’s clean. Nothing ships with a real issue still open.

**Verify before calling anything done.** Show the evidence, command output, a live curl, a screenshot, never “should work.”

## Step 6: autonomy guardrails

- No password-manager CLI access while you’re unattended, a biometric prompt just hangs. Use whatever token or keychain-based secrets are already set up.
- No external sends to real people, drafts only. No edits outside the campaign’s own scope, especially anything belonging to a real client or a live customer.
- No destructive operations, no new paid subscriptions.
- Deploys of the campaign’s own artifacts are fine, that’s the point, but build and verify first.
- The stop file halts everything immediately. Respect the deadline. Self-exit when the queue is genuinely done, and unload the keepalive.

## Step 7: wrap

When the queue is dry or the deadline hits: one final surface round with a proud summary, mark the state complete, unload the keepalive, and hand back a tight summary with evidence and a suggested next move.

---

## Reusable assets

- A resilience scaffold you keep across campaigns (the templates in `ww-keepalive`, or your own copy of a proven `keepalive.sh` / `resume.md` / `state.json` set).
- A second account for dual-account failover, if you have one, so a single account’s cap doesn’t stall the whole campaign.
- Whatever helper functions you’ve built for patching your status surface (a glance row, a wins callout) live once, reused by every campaign.
- Your externalize model clients (see `qq-externalize`).
- LaunchAgent registration should be mandatory and visible somewhere you’d actually notice an orphaned one.

## Self-improvement

After a HAM run, note what slowed it down or what’s worth templating for next time, generalize the scaffolding into something parameterized rather than copy-pasting a working script into the next campaign.

---

## Hard-won lessons

These came out of real multi-day, sometimes multi-session HAM campaigns. Some are mechanism-level, most are judgment calls that only show up once you’re actually running something ambitious unattended for days.

### Concurrency and pacing

**A server-side rate limit is not your usage cap, and it’s not a wall, it’s a retry.** “Temporarily limiting requests” is distinct from a hard usage limit and trips when too many agents spawn at once; workflows spawning workflows plus loose background agents running concurrently will hit it. Run major fan-outs sequentially, don’t launch a new workflow while another is still running. Treat a rate-limit failure as transient: back off a minute or two, then resume the failed stage specifically, most workflow runners can re-run only the failed units and return the cached ones instantly. Never count a rate-limited lane as dead.

**Make end-of-run synthesis resumable.** If a single final tally or synthesis step gets rate-limited, you lose the whole result unless every lane checkpoints its own count as it lands. Any “aggregate everything at the end” step should be cheap to re-run, not a single fragile point of failure.

**Recover exactly the units that died, not everything, and not nothing.** If a fifty-agent fan-out loses eighteen to throttling, you want those eighteen back, not a full rebuild and not a silent gap. A cheap resume can hand back a cached null instead of actually re-running a killed unit, so after any rate-limit recovery, reconcile: compare the expected set against what’s verified on disk, and re-run exactly the gap. Recovery isn’t done until expected equals actual; a confident-but-wrong “resumed” is the trap.

### Running several campaigns at once

If more than one HAM lane runs on the same machine, isolate everything per-session (a unique slug, a unique state directory, a unique LaunchAgent label, so two lanes can never clobber each other’s world) and throttle the things that are genuinely shared: the rate limit is global across every session on the account, so scale down your own concurrent fan-out by however many lanes are actually live, and stagger big fan-outs instead of letting them all fire at once.

**Check for a live campaign before starting a new one.** The bigger version of the collision above: two independent lanes each building their own resilience layer against the same target is merge hell and doubled rate-limit pressure, even with cleanly isolated slugs, because isolation protects your state directory, not the shared files you’re both about to edit. Before standing up a new keepalive, check for an existing one aimed at the same goal. If one’s already running, don’t compete with it, take a genuinely separate, complementary slice of the work instead.

### Verify the felt outcome, not the inventory

**“Tests pass” and “the thing got built” are not the same claim as “the person on the other end experienced the fix.”** A real enforcement gate can be correct in isolation and still not be wired to every path that could bypass it, so before calling a quality or output fix done, check the actual live surface it was supposed to fix, not just the code that produces it.

**A provider’s status API and the thing it’s protecting are two different questions.** A third-party integration can report itself “registered” or “healthy” while the actual endpoint it points at is dead, silently misconfigured, or pointed at a staging URL nobody redeployed. When a status check says healthy, ask whether that’s the control plane or the actual data path, then probe the data path directly with a request the target safely rejects before any real side effect, and read what actually comes back.

**A caveat written in a comment is not coverage.** If code or a doc says a case is “handled elsewhere” or “covered separately”, treat that as an open loop to close, not a fact to trust, until you’ve confirmed the elsewhere actually exists.

**A check meant to gate a deploy has to fail on the bad path, not just print a warning and exit clean.** Before handing any detector off as a gate, run it against a known-bad state and confirm its exit code is actually nonzero. A check that prints “3 issues found” and still returns success will pass every gate built on top of it forever.

**Bracket both ends of a pipeline.** A fix that hardens one end (verifying delivery, say) implies a symmetric question at the other end (can anyone actually start the flow in the first place). Turning a fix into a standing check on only one end leaves a blind spot exactly the size of the end nobody’s watching.

### When not to build a detector

Not every gap deserves a standing check. If the only safe probe you can run, non-destructive, no real side effect, can only reach a proxy for the actual failure and not the failure itself, a standing alarm on that proxy manufactures false confidence: it goes green while the real failure mode slips through underneath it. When you can’t safely verify the thing that actually matters, say so and hand the gap to whoever can check it safely (a real test-mode transaction, a controlled environment), rather than shipping a check that can only ever tell you the proxy looks fine.

### Restraint is real work

**When the whole queue is genuinely blocked, a read-only vigilance pass is a legitimate chunk of work, not a stall.** Re-confirm the last fix still holds, diff the one blocking metric against the last check, keep the status surface honest, and externalize the hold-versus-act decision to a couple of independent voices rather than deciding alone. If they converge on hold, that’s a verified result, not an excuse.

**If restraint keeps repeating with no change in state, the fix is the wake cadence, not more manufactured work.** A fixed-interval keepalive firing every fifteen minutes doesn’t mean every fire needs fifteen minutes’ worth of expensive work; separate the cheap per-wake check (touch the heartbeat, re-probe the block, look for anything new) from the expensive per-cadence one (a real adversarial pass, a synthesis writeup), and let the expensive one lag when the cheap one keeps coming back clean.

**An external model’s “this is reversible” is not the same as “this is reversible under your actual guardrails.”** A suggestion can look compliant in the abstract and still violate a specific rule you set for this run (a create-then-delete plan under a no-delete guardrail, say). Screen every external suggestion against your real constraints, not the model’s generic notion of safe.

### Trust the live state over the paper trail

By the middle of a long multi-session run, you’re inheriting a thick paper trail: prior done-log entries, handoff notes, a status surface. That record drifts from reality, and a long run is exactly where the drift compounds unnoticed. Before you rely on, cite, or build on top of a prior pass’s claimed deliverable, confirm the artifact exists on disk; a promised fix that was never actually built is worse than a known, visible gap, because everyone downstream assumes it’s covered. And a blanket “all of these are safe” conclusion inherited from an earlier pass is the most dangerous kind to inherit uncritically: re-verify the one member of the set where the reasoning could plausibly fail, not the members it already got right.

---

## Field-tested integrity floor

Autonomy guardrails above cover external sends and destructive operations. Extend the same floor to content itself: never let an unattended run fabricate credentials, invent a track record, or produce anything that corrupts safety-critical, medical, or scientific integrity in pursuit of a goal. Flag anything in that territory for review rather than pursuing it. And count only what’s verified: real assets confirmed on disk, never a number an agent merely claims, agents inflate their own results.
