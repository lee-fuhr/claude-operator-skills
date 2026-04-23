---
name: qq-smart-next-move
description: After completing a build or reaching a milestone, steps back to ask the smart strategic questions before planning next. Data-backed, assumption-interrogating, combines options rather than picking one.
version: 1.0.0
triggers:
  - "what's next"
  - "smart next move"
  - "what should I do"
  - "next steps"
  - "what now"
---

# Smart next move

You just finished something **in this session**. Before jumping to the next task, stop and ask the questions that prevent building the wrong thing next.

This skill is scoped to the **current thread's work**. Options should be things Claude can do right now, in this session, continuing the momentum of what was just completed. This is NOT a cross-project strategic review or a prompt to step away — it's "what's the smartest next move in THIS conversation?"

---

## The process

### Step 1: Inventory what just happened

Before asking forward-looking questions, establish the ground truth:

- **What was built/completed?** (Specific deliverables, not vague descriptions)
- **What data do we have now that we didn't before?** (Usage patterns, test results, user feedback, performance numbers, business metrics)
- **What surprised us during the build?** (Unexpected complexity, scope changes, things that were easier/harder than expected)
- **What assumptions were validated or invalidated?** (Did the thing we built confirm what we thought, or did reality differ?)

Pull this from conversation context, recent session history, project state, and any available data. Don't ask the user for what you can find.

### Step 2: Ask the smart questions

These aren't generic "what should we do next" questions. They're assumption-interrogating, data-grounded questions specific to what just happened.

**Framework — 5 categories of smart questions:**

**1. Validation questions** — Is the thing we built actually working?
- "We built X, but do we have evidence it's actually being used/useful?"
- "What would tell us this was a mistake?"
- "If we deleted this tomorrow, what would break? What wouldn't?"
- "Are we measuring the right thing, or are we measuring what's easy?"

**2. Leverage questions** — What does this unlock that wasn't possible before?
- "Now that X exists, what becomes trivially easy that was hard before?"
- "What other problems does this solve as a side effect?"
- "Who else could use this? What would they need changed?"
- "What's the 80/20 extension — smallest addition, biggest new capability?"

**3. Risk questions** — What could go wrong that we're not thinking about?
- "What's the maintenance burden we just created?"
- "If the user has a bad week, does this thing break or keep running?"
- "What dependency did we just introduce that could fail?"
- "Is this creating technical debt we'll regret in 3 months?"

**4. Opportunity cost questions** — Is there something higher-value we could do next in this session?
- "Given what we just finished, what's the natural next step vs. the highest-value next step?"
- "Are we continuing this because it's important or because we have momentum?"
- "Is there a follow-on task from what we just built that's time-sensitive?"
- "What would make the work we just did MORE valuable if we did it right now?"

**5. Strategic alignment questions** — Does this move the needle on what matters?
- "How does this connect to revenue / client acquisition / the pipeline?"
- "Would a prospect care about this? Would a client?"
- "Are we building for the business or building because it's interesting?"
- "What's the simplest version of 'next' that a paying customer would value?"

### Step 3: Present options as combinations

The user doesn't pick A or B — they pick "A for sure, but maybe also B." Present options as combinable, not mutually exclusive.

**Scope:** Options must be things that can be done in this session, continuing from what was just completed. Don't suggest "go look at a completely different project" — that's not a next move, that's an exit.

**Format:**

> **Based on what we just built and the data we have, here are the moves I see:**
>
> **A. [Option]** — [1-2 sentences on what it is and why it matters]
> - Data point supporting this: [specific evidence]
> - Risk: [what could go wrong]
>
> **B. [Option]** — [1-2 sentences]
> - Data point: [evidence]
> - Risk: [risk]
>
> **C. [Option]** — [1-2 sentences]
> - Data point: [evidence]
> - Risk: [risk]
>
> **My recommendation:** A + C together, skip B for now because [reason].
>
> **The question I'd want answered before committing:** [the one data point or decision that would change the recommendation]

### Step 4: Interview on gaps

Use AskUserQuestion (multiple choice) for any genuine gaps in your analysis. Don't ask about things you can look up.

---

## What this is NOT

- **Not a task list.** Your task manager has the task list. This is strategic questioning.
- **Not "what's in the backlog."** The backlog is full of things that seemed important when they were written. This asks what's important NOW.
- **Not planning.** This is pre-planning — the questions that determine whether the plan is worth writing.
- **Not a cross-project review.** Stay scoped to what this session has been working on.
- **Not an exit ramp.** "Call it a day" or "do nothing" are never options. This skill is for when you want to KEEP GOING and need the smartest direction.

---

## When to use

- After finishing a build (natural pause point)
- After a milestone (launch, release, audit completion)
- When the user says "what's next" or "what now"
- At the start of a session when the last session completed a major deliverable
- When momentum is high but direction is unclear ("we're cooking but where are we going?")

---

## Key principles

- **Data over theory.** If you can check a number, check it before opining.
- **Challenge momentum.** "We should keep going" is often inertia, not strategy.
- **Revenue proximity matters.** All else equal, the thing closer to money wins.
- **Resilience filter.** If the user can't maintain it during a bad week, it shouldn't be the next priority.
- **Combine, don't choose.** Present options as combinable — the instinct to combine is usually right.
