---
name: ww-premortem
description: Ask what would make this fail before you build it, not after. A one-question design-time gate, imagine it’s already broken three months from now, work backward to the most likely cause, and let the answer change the plan instead of just getting noted and ignored. Works on code, an automation, a process, or a decision. Invoke with /ww-premortem, or say “what breaks this in three months,” “pre-mortem this,” “why would this fail,” “before I build this,” at the moment you’re about to commit to an approach, not after you’ve already started.
version: 1.0.0
triggers:
  - “what breaks this in three months”
  - “pre-mortem this”
  - “why would this fail”
  - “before I build this”
  - “what’s the most likely way this breaks”
  - “run a premortem”
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Ask what breaks this before you build it

The gap this closes: most failure only gets discussed after it happens, in a retrospective nobody enjoys writing, about a problem that was cheap to prevent and expensive to fix. By the time a bad assumption shows up as a real failure, two or three other decisions have been built on top of it, the person who made the original call has moved on to something else, and fixing it now means unwinding work instead of just choosing differently the first time. A premortem moves that same conversation to before the fact, when it still costs five minutes instead of a fire drill. Imagine the failure has already happened. Work backward to why. Then let the answer change what you build, instead of writing it down and moving on unchanged.

**A design is ready once you’ve imagined its most likely failure and changed something because of it, not once it merely sounds reasonable going in.**

## Protocol (follow every step)

### 1. State the approach before you commit to it

Get specific about what you’re about to build or decide. A vague approach produces a vague premortem, you can’t imagine a specific failure of something that isn’t specific yet.

### 2. Declare the failure as already true

This is the one counterintuitive move that makes the whole technique work. Don’t ask “might this fail?” Ask “it’s three months from now, and this failed. Why?” Treating the failure as a certainty instead of a possibility is called prospective hindsight, and it’s the actual mechanism behind the premortem, not just a framing trick. Research by Deborah Mitchell, Jay Russo, and Nancy Pennington found that imagining an outcome has already happened increases people’s ability to correctly identify the reasons for it by roughly 30%, compared with simply asking what could go wrong. Gary Klein built the premortem technique around that finding in a 2007 Harvard Business Review piece. Framing the failure in the past tense, as something that already happened, pulls specific reasons out of you instead of vague reassurance.

### 3. Generate more than one cause

The first reason you think of is usually the most obvious one, and the most obvious one is usually already something you’ve accounted for. Push for at least three genuinely different causes: a technical one (what breaks under real conditions), a people one (what happens when the person who understands this moves on, forgets, or is out sick that week), and a drift one (what happens when nobody’s looked at this in months and the world around it has quietly changed).

### 4. Test each cause: would it change the plan?

For every cause, ask directly: if I believed this was the likely failure, would I build something different right now?

- **Yes** → that’s a real finding. Change the design.
- **No**, because it’s already handled elsewhere, or because it’s a low-probability, low-severity edge case → note it and move on. Don’t pad the plan with defensive complexity for a failure mode that can’t reach you.

### 5. Change the plan, don’t just log the finding

This is the step that turns a premortem from a diary entry into a gate. A cause that survives step 4 has to change what gets built this session, not get added to a list of things to revisit later. “Noted for later” is how a real premortem finding quietly turns into the exact failure it predicted.

### 6. Write down what you decided not to fix, and why

Any cause you chose not to act on should be a deliberate, visible decision, not a silent drop. “Considered X, didn’t change the design because Y” costs one sentence and saves the next person, including a future version of you, from re-litigating a question that already got a real answer.

## What it catches

- A single point of failure nobody named out loud
- An assumption that only holds if a specific person remembers to do something
- Complexity that’s fine today and will rot the moment nobody’s watching it
- A dependency on something external that’s likely to change, with nobody tracking it

## A worked example

**Approach:** add a scheduled job that emails a weekly summary report every Monday at 8am.

**Premortem (step 2):** it’s three months from now. The Monday report never went out for two straight weeks, and nobody noticed until someone asked why. Why did it fail?

**Causes (step 3):**
- Technical: the job depends on an API key that expires, and nothing alerts when a run fails silently.
- People: the one person who knows how to restart it if it breaks is out that week.
- Drift: the report was built around this quarter’s priorities; by month three those have changed, and the report is technically still running, but nobody trusts the numbers in it anymore.

**Test each (step 4):**
- Silent failure: yes, changes the plan. Add a failure alert, don’t just add the job.
- Bus factor: yes, changes the plan. Write two lines of restart instructions somewhere findable, five minutes now.
- Drift: no, doesn’t change today’s build. It’s a real risk, but nothing today can fix a problem that hasn’t happened yet. Note it as “revisit if priorities shift” and move on.

**Revised plan:** ship the job with a failure alert wired in and a one-line runbook attached, and skip trying to future-proof against priorities that haven’t changed yet.

## When to skip or scale down

Not every five-minute task needs a formal premortem. Skip it, or compress it to a single mental sentence, when the decision is trivial, cheap to reverse, and low-consequence if wrong. Asking “what breaks this” about where to put a config variable is its own kind of failure, the ritual eating the time it was supposed to save. Run the full version when the approach is hard to reverse once started, when it’ll run unattended or get touched by someone other than you later, or when getting it wrong costs more than the five minutes the premortem itself takes.

## When to escalate beyond a solo premortem

A single pass, run by whoever’s about to build the thing, is the right default. Escalate when the decision is genuinely irreversible, spans multiple systems or sessions, or the stakes are high enough that one person’s blind spots matter. Two ways to escalate:

1. **Get more independent causes.** A premortem run by one person surfaces that person’s failure modes. If others will be affected by the outcome, have them write their own causes independently before comparing notes, the original research ran it this way for a reason: independent lists catch more than a single shared brainstorm.
2. **Pair it with a fuller review.** A premortem answers “why would this fail,” not “is this plan sound.” For a large or irreversible build, run it alongside a full adversarial review of the plan itself, then let both sets of findings shape the same revision.

## Key principles

- **Prospective, not retrospective.** A premortem happens before the failure, not after. A post-mortem, written after something has already broken, is a different and later tool, this one only works while the design is still cheap to change.
- **The failure has to be real, not decorative.** If none of the causes you generate would change anything about the plan, that’s either a genuinely solid plan or a sign step 3 didn’t go deep enough, not a reason to skip the exercise next time.
- **A gate, not a note.** The whole value collapses if the finding gets written down and then quietly ignored. Change the plan, or explicitly decide not to, out loud.
- **Proportional, not ceremonial.** Match the depth of the exercise to what’s genuinely at stake. A five-minute imagined failure that changes nothing real is worse than skipping it outright, because it looks like diligence without doing any of the work diligence is for.

Sources: [Performing a Project Premortem, Gary Klein, Harvard Business Review 2007](https://hbr.org/2007/09/performing-a-project-premortem); prospective hindsight research: Mitchell, Russo & Pennington, “Back to the future: Temporal perspective in the explanation of events,” Journal of Behavioral Decision Making, 1989.
