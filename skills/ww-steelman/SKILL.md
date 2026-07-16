---
name: ww-steelman
description: Argue against your own plan before you build it. A five-step protocol, write the plan, critique it like an outsider would, then defend it against that critique, keep only what survives, apply the rest. Works on any plan, code or content. Invoke with /ww-steelman, or say “steelman this,” “poke holes in this,” “what am I missing,” “play devil’s advocate,” before locking in a plan, a draft, or a decision.
version: 1.0.0
triggers:
  - “steelman this”
  - “poke holes in this”
  - “what am I missing”
  - “play devil’s advocate”
  - “stress-test this plan”
  - “before I commit to this”
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Steelman your plan before you build it

The gap this closes: you finish a plan, read it back, and it sounds right, because you already believe it. That’s not a review, it’s a rerun of the same thinking that produced the plan in the first place. The real failure modes (the assumption nobody said out loud, the edge case that only shows up in week three, the “add rate limiting” line that’s really just fear wearing a to-do item) all pass a self-read clean, because a self-read never actually disagrees with you. This protocol forces a real fight: attack the plan like an outsider would, then defend it like you wrote it, because you did, and only let a criticism change anything once it’s survived you trying to kill it. Do this before the build, the draft, or the decision locks in, and the blind spot costs five minutes instead of a scrapped week.

**A plan is ready once its criticisms have survived a real argument against them, not once it merely sounds right on a re-read.**

## Protocol (follow every step)

### 1. Write the plan

Get the whole thing down before attacking it. A half-written plan is too easy to defend, there’s nothing concrete enough to find fault with yet.

### 2. Critique it like an outsider would

Turn on the outsider you’d actually want reviewing this and ask, plainly:

- What’s ambiguous? Where would two people read this plan and build two different things?
- What could fail? Walk each step and ask what happens if the input is empty, the network is down, the user does the unexpected thing.
- What’s underspecified? Where did “handle errors” or “make it fast” stand in for an actual decision?
- What assumptions am I smuggling in? What am I treating as obviously true that I never actually said out loud?

Write these down as a real list, not a vibe. A critique you can’t point to a specific line for isn’t a critique yet.

### 3. Steelman the critique

For every item on that list, argue *against* it. Defend the original plan the way you’d defend a colleague’s work you actually respected.

Ask, for each one: is this criticism real, or is it fear-driven, marginal, or solving a problem that doesn’t exist yet? “What if traffic spikes 100x” is a real question for a payments endpoint and a wasted afternoon for an internal admin tool nobody but you will ever open.

Watch for the failure mode hiding inside this step itself: it’s easy to wave away every criticism just to avoid the extra work, which is the same self-serving bias this whole protocol exists to catch, one step later. If every single item dies here, that’s a signal to double-check you actually argued each one, not a sign the plan was flawless.

### 4. Keep only what survives

A criticism that beats its own steelman is real. Fold it into the plan. A criticism that doesn’t survive gets killed, explicitly, not just quietly dropped, so the next read of this plan doesn’t re-raise the same question from scratch.

### 5. Apply and note

Update the plan with the survivors. If you keep any kind of running log for the project, note what you considered and rejected, not just what you kept. The next person (including future you) benefits from seeing what was already argued through.

## The track record

In this system’s own experience, something close to half of the “critical issues” a first self-critique turns up end up marginal once you actually argue against them: fear-driven, already handled elsewhere, or defending against a scenario that won’t happen. The rest are real, and they’re real precisely because they survived you trying to kill them. Your own ratio may land differently, but the shape holds: without step 3, you either ship every anxious “what if” as a requirement, bloating the plan with unneeded complexity, or you skip the critique step entirely because half of it feels like noise. Steelmanning is what separates the noise from the real half.

## What it catches

- **False urgency.** “This is critical,” is it, actually, or does it just feel that way mid-plan?
- **Over-engineering.** A defensive feature for a failure mode that structurally can’t happen here.
- **Ambiguous instructions.** A step that reads fine to you but hands a collaborator (human or agent) genuine uncertainty about what to do.
- **Missing failure modes.** What happens when a call returns null, times out, or throws, and the plan never says?
- **Scope creep disguised as thoroughness.** Extra work that sounds responsible but doesn’t serve the actual goal.
- **Homogenization risk, the subtle one.** Ask yourself directly: am I rejecting this approach because it’s actually bad, or because it doesn’t look like what I’d normally do? A review process that only ever approves the familiar shape of thing quietly kills experimentation over time. If a genuinely novel idea is losing to “that’s not how we usually do this,” that’s a false positive on the critique side, not a win.

## A worked example

**Plan:** “Add a caching layer in front of the search endpoint so results load faster.”

**Critique (step 2):**
- Underspecified: how stale can cached results be? A minute? An hour?
- Missing failure mode: what happens on a cache miss under load, does the origin get hammered?
- Ambiguous: “faster” compared to what baseline, and how would anyone know it worked?
- Assumption: this assumes the endpoint is actually slow because of repeated identical queries, not because of something else entirely.

**Steelman (step 3):**
- Staleness: real. A user editing a record and immediately searching for it, and seeing stale data, is a genuine, likely-to-happen bug. Survives.
- Cache-miss stampede: real only if traffic is high enough to matter. For a tool with a dozen daily users, this is defensive complexity solving a problem that will never occur. Marginal, killed, unless traffic changes.
- “Faster than what”: real. Without a baseline number, there’s no way to know the caching layer did anything at all. Survives.
- Wrong root cause: real, and the most important one. Nobody has actually profiled the endpoint yet, this plan might be solving the wrong problem. Survives, and probably should come before anything else.

**Revised plan:** profile the endpoint first to confirm the bottleneck is repeated queries, then add a short TTL cache with an explicit staleness window, and record a before/after latency number to prove it worked. The cache-stampede handling gets dropped from this pass and noted as “revisit if traffic grows,” not silently forgotten and not built anyway just in case.

## When to escalate beyond a solo steelman

A solo pass, run by the same person or agent who wrote the plan, is the right default for most day-to-day work. Escalate to a heavier process when any of these are true:

- **The decision is genuinely irreversible:** a data migration, a public API contract, anything expensive to undo.
- **The build is large:** it spans multiple sessions or multiple systems, or enough time that a wrong turn on day one compounds for days.
- **You don’t know the domain well:** unfamiliar territory is exactly where your own blind spots are least visible to you.
- **The stakes are genuinely high:** real money, real user data, or real reputational exposure on the other end of a mistake.

Two concrete ways to escalate, in increasing order of weight:

1. **Get a second, independent voice on the critique step.** If you have access to a different model or a fresh context, run step 2 (the critique) there instead of in the same conversation that wrote the plan. A model, or a person, reviewing its own output shares that output’s blind spots by construction, a genuinely separate reviewer doesn’t. This alone catches most of what a solo steelman misses.
2. **Run a full multi-phase plan audit.** For anything spanning multiple sessions or milestones, a single steelman pass is necessary but not sufficient, it only catches roughly the ambiguity-and-overreach category of problem, not sequencing risk, missing domain expertise, or a pre-mortem on how the whole thing could fail six months out. If your setup has a dedicated plan-audit process for exactly this, use it here instead of stretching a solo steelman to cover ground it wasn’t built for.

## What kind of plan you’re steelmanning changes what you’re looking for

The five steps are the same either way, but point the critique at what’s actually at risk:

- **Building something (code, infrastructure, a technical decision):** point step 2 at failure modes, edge cases, and architectural assumptions. What breaks under load, what happens on the unhappy path, what did you assume about the environment that might not hold?
- **Writing or planning something (messaging, a proposal, a piece of content, a strategic call):** point step 2 at claims and positioning instead. Is every claim actually true and defensible? Does the angle overclaim? Is the scope right, or does it reach into territory that isn’t yours to decide? A code-shaped critique (“what if the database times out”) is a category error on a plan that has no database in it.

## What it kills

- Complexity that adds no real value for the actual scenario at hand.
- Defensive handling for situations that structurally cannot occur given the actual constraints.
- Anxious “what if” items that feel responsible to include but were never actually load-bearing.

## Key principles

- **Self-review alone isn’t review.** Reading your own plan back and nodding is confirmation, not critique.
- **Every criticism gets a real trial**, not a rubber stamp in either direction. It has to survive an honest defense to count, and a real criticism should survive one.
- **The plan’s owner stays in control.** This protocol produces a sharper plan and a documented reason for every rejected criticism; it doesn’t silently rewrite anything.
- **Cheap and constant beats rare and heavy.** A five-minute solo steelman on every real plan catches more, over time, than an occasional deep audit that only fires when someone remembers to ask for it.
