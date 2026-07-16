---
name: qq-go-afk-smart
description: The BOUNDED / delegate-and-verify half of the kept-alive autonomous AFK pair (sibling = `qq-go-afk-ham`, the unbounded max-effort version). Stand up a calm, self-healing, fully-autonomous overnight worker for a well-scoped punch list: the top-tier model writes strict specs and does quality control, cheap and free models do the grunt work, one bounded task per cycle, each one deployed and live-verified, a phone-glanceable status surface, and a durable done log. Invoke when you say “go afk smart”, “go-afk-smart”, “qq-go-afk-smart”, “go smart”, “bounded overnight”, “delegate and verify overnight”, or hand it a finite, well-specified backlog (a punch list, a rollout, a sweep) to grind down autonomously while you sleep, without the kitchen-sink fan-out of go HAM. For a big, ambitious, open-ended multi-day build that should use all the quota, use `qq-go-afk-ham` instead.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Go AFK Smart: bounded delegation, one task at a time

This is the calm, bounded sibling of `qq-go-afk-ham`. Same resilience backbone, opposite posture. HAM is for an open-ended, ambitious build where you want maximum quality and maximum quota burn: workflows spawning workflows, audit-gated, creative meta strategy. SMART is for a finite, well-specified backlog, a punch list, a config rollout, a hardening sweep, that you want ground down reliably and cheaply overnight, one bounded task at a time, with the expensive model spending its tokens on specs and quality control, not grunt work.

**The gap this closes:** left alone overnight, an expensive model tends to do the grunt work itself instead of delegating it, because delegating takes an extra beat of discipline and doing it yourself doesn’t. A whole night of quota gets spent on work a free model would have handled the same way for a fraction of the cost, and nothing checks whether what got built actually matches what was asked for. SMART fixes both: the top-tier model never touches the grunt work directly, it writes the spec, hands off execution, and checks the real output against that spec before anything counts as done. You wake up to a punch list that’s actually finished, verified against the disk, at a fraction of the token cost a night of solo grinding would have spent.

**When to reach for SMART over HAM:** the work is enumerable and mostly mechanical, you can write a clear acceptance test for “done”, the risk is in correctness and regressions rather than in needing a brilliant strategy, and you want low token spend and a calm pace rather than a blowout.

---

## The posture: you are a delegation engine

You, the top-tier model, are scarce and expensive. Each cycle, delegate rather than execute:

1. **Pick one bounded task** from the queue.
2. **Write a strict spec**: inputs, exact output shape, acceptance criteria, what good and bad look like. No room for interpretation.
3. **Delegate execution** to the cheapest capable model.
4. **Quality-check the actual output** against the spec. Read what landed on disk, or the real deployed value, never trust the claim.
5. **Iterate with precise corrections**, up to three rounds. After that, do it yourself or flag it for review.
6. **Record the finished, verified unit** in the done log, then stop.

## Routing: the cliff still matters

Grunt work, research, extraction, summarization, classification, transformation, code analysis, log reduction, adversarial critique, goes to the external stack (see `qq-externalize` in this collection). Multi-file mechanical edits go to a mid-tier subagent or a small, tightly-scoped workflow carrying your strict spec.

**The one exception:** never delegate voice, copy, positioning, or messaging generation or critique to a cheap model. That’s the one place quality doesn’t scale with price, cheap models inject corporate-speak and miss whatever voice you’re actually writing in. Keep that work on your own model tier.

## Pace: calm, one task at a time

One bounded task per cycle, one delegation at a time. No fanning out, no workflows spawning workflows, that’s HAM, not this. The keepalive’s own re-fire interval is the loop; you don’t need to manufacture parallelism inside it.

**Reconcile, never redo.** Read the done log and the state file on every resume. Skip anything already recorded as finished. The whole point of a stateless worker is that this reconciliation step is what keeps it coherent across restarts.

**Deterministic code gets tests first.** A red test shown in the done log, then the fix, then a green suite, then deploy and verify live on the real URL, a health endpoint can lie.

## Resilience backbone

Stand up the kept-alive via the `ww-keepalive` skill in this collection. It owns the fresh-`claude -p` mechanism (never `--resume`), the gates, the liveness check, the interactive interlock, dual-account failover, and `--permission-mode auto`, plus the `queue.md` / `done.md` tasklist standard scaffolded into the lane. SMART supplies only the posture for the resume brain: **you are a delegation engine, one bounded unit per cycle, no fan-out.**

## Surfaces: phone-glanceable, honest

A status surface, a Notion working doc (see `ww-notion-docs` in this collection for the actual formatting patterns), a dashboard, whatever you’d actually check from your phone, patched every cycle: what’s being worked on right now, what shipped and got verified last cycle, and any question that needs you, surfaced there instead of buried. Never let that surface read better than the truth.

The real task list lives in two files that outlive any single session: a durable `done.md` (verified units only) and a `queue.md` (the bounded backlog, priority-ordered).

## Guardrails

- No password-manager CLI access while you’re away, a biometric prompt just hangs a headless process. Use whatever token or keychain-based secrets you’ve already set up.
- No external sends to real people, drafts only.
- No edits outside the campaign’s own scope, especially anything belonging to a real client or a live customer.
- No destructive operations, no new paid subscriptions.
- Deploys of the campaign’s own work are fine once built and verified.
- **When the queue is dry:** do a brief read-only health pass, keep the surface honest, then mark the state complete (the keepalive self-exits) or drop the stop file. Don’t manufacture work to look busy, honesty over motion.

## Relationship to qq-go-afk-ham

Same resilience machinery (the keepalive, the caps, dual-account failover, the surfaces, the tasklist), see `qq-go-afk-ham` for the fuller treatment of the shared backbone. The differences that matter:

1. **Pace.** SMART is one bounded task per cycle, calm. HAM is fan-out, workflows spawning workflows, use all the quota.
2. **Token posture.** SMART has the top-tier model writing specs and doing quality control while cheap models execute. HAM spends whatever it takes for maximum quality.

Both share the fresh-`claude -p` mechanism (never `--resume`) and both run under `--permission-mode auto`.

Pick SMART when the work is finite and mechanical and you want it done reliably and cheaply. Pick HAM when the work is open-ended and ambitious and you want to be surprised by what came back.

## Overnight questions, never a blocked stall

For any unattended overnight run, never let a decision that needs a human stall the worker. Keep a running `morning-questions.md` in the lane: any decision that needs your call gets appended there with one line of context and two to four concrete options, and the worker immediately takes the next unblocked unit instead of stopping or pinging anyone at night. Compile that file into one batched round of questions the next time you engage, dropping anything whose trigger never actually fired.
