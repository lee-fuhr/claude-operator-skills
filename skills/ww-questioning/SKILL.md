---
name: ww-questioning
description: Before filling a gap in what you know with a guess, check whether the guess is load-bearing. If getting it wrong would mean redoing real work, or building on a false premise, ask a real question with concrete options instead of assuming silently. If it’s genuinely low-stakes, state the assumption out loud and keep moving rather than stalling on it. Works on any ambiguous request, with or without an AI agent involved. Invoke with /ww-questioning, or say “wait, let me ask first,” “is this load-bearing,” “check before I guess,” “clarify before building,” whenever a request has more than one reasonable reading and you’re about to just pick one.
version: 1.0.0
triggers:
  - “wait, let me ask first”
  - “is this load-bearing”
  - “check before I guess”
  - “clarify before building”
  - “what am I assuming here”
  - “ask instead of guessing”
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Ask instead of guess

The gap this closes: an ambiguous request gets a confident-sounding answer anyway, because stopping to ask feels like it slows things down, and guessing feels like progress. The guess turns into an assumption, the assumption turns into two hours of work, and the work answers a question nobody asked. Those two hours weren’t wasted because the guess was unreasonable, they were wasted because nobody checked, before betting on it, whether being wrong here was cheap or expensive. This protocol is one test, run at the moment the guess would get made: is this load-bearing? If yes, ask. If no, say the assumption out loud and keep moving.

**A guess is fine the moment it’s cheap to be wrong about. The only job here is telling, before you commit to it, which kind of guess you’re making.**

## Protocol (follow every step)

### 1. Catch the moment you’re about to guess

The trigger isn’t “this request is vague,” it’s the specific instant you notice yourself filling a gap with an assumption: picking an interpretation, choosing a default, deciding what someone probably meant. That moment is small and easy to miss, because it doesn’t feel like a decision, it feels like just getting started.

### 2. Run the load-bearing test

Ask one question: if this guess turns out wrong, does the cost stay small, or does it compound?

- **Compounds → ask.** Other decisions get built on top of this one. It’s slow or awkward to undo. It touches something outside your own draft: another person’s time, a shared system, money, data that can’t be un-deleted.
- **Stays small → don’t ask, just state it and move.** The wrong guess costs a quick edit. Nothing else depends on it yet. Reversing it is a five-minute fix, not a redo.

This is the whole test. Most requests are a mix, some genuinely ambiguous parts are load-bearing, some aren’t, and only the load-bearing ones earn a question.

### 3. Ask with options, not open air

An open-ended question (“what do you want here?”) hands the ambiguity right back, unresolved, and now there are two people confused instead of one. Give two to four concrete interpretations, each specific enough that picking one is a real decision rather than a guess about a guess. Always leave a genuine escape hatch, “something else, tell me what I’m missing,” instead of forcing a choice between two options that might both be wrong.

**Bad:** “What kind of search do you want?”

**Good:** “Three ways this could work: (A) exact match on names only, ships today. (B) fuzzy match across every field, needs a real search index. (C) a simple filter dropdown, no search box at all, might be all you need. Which one, or something else?”

### 4. State the assumption out loud when you don’t ask

For guesses that pass the load-bearing test as safe, don’t go silent either. Say what you’re assuming and why, right where you make the call, “assuming X because Y,” surfaced as it happens rather than saved up for a debrief at the end. A silent low-stakes assumption is fine to make. A silent unstated one is how a small guess quietly turns into a load-bearing one nobody flagged in time.

### 5. Don’t ask what you should already know

The test cuts both ways. Asking permission to do obviously correct work, or asking a question you could answer yourself by looking, is its own failure mode, it just wears diligence as a costume. “Should I check the existing code first?” isn’t a question, it’s stalling. Look, then act. Save the actual questions for the ones only the other person can answer.

## When to escalate: grill mode

For genuinely high-stakes calls, irreversible actions, or decisions that touch multiple systems, one question usually isn’t enough. Escalate to a fuller pass: restate the plan back, challenge the approach directly (“why this instead of the obvious alternative?”), push on edge cases, and don’t proceed until the other person owns the trade-off instead of passively accepting your default. It’s the same load-bearing test, just run harder, for the requests where being wrong is expensive enough to earn the extra five minutes.

## A worked example

**Request:** “Add search to the dashboard.”

**Guess-first version:** builds full-text fuzzy search across every field, in real time, because that’s the most complete version of “search.” Two days later, the actual need was a filter dropdown with maybe twelve options. The two days weren’t lost to a hard problem, they were lost to a guess nobody checked.

**Question-first version, asked before writing anything:** “What are people searching for, names, dates, tags, or something else? How much data, a hundred rows or a hundred thousand? And does it need to be a real search box, or would a filter dropdown cover it?” Three short answers later, the actual build is an afternoon, not two days, because it’s building the right thing instead of the most impressive-sounding thing.

## What it catches

- Building the technically correct answer to a question nobody asked
- Two people quietly building two different things off the same vague sentence
- A wrong default that only gets discovered after other work is already stacked on it
- The awkward “wait, that’s not what I meant” conversation, arriving after the work instead of before it

## Key principles

- **The test is about cost, not confidence.** Being unsure isn’t the trigger, being wrong and it mattering is.
- **Options beat open questions.** A concrete choice is answerable in one line; an open question just relocates the ambiguity to the other person.
- **Silence isn’t the same as agreement.** An assumption that never gets said out loud can’t get corrected, even when it was fine to make in the first place.
- **This works with or without a tool.** If you’re working inside something with a structured way to ask a question and wait for an answer, use it, it makes options and escape hatches easy to render cleanly. But the underlying discipline, catch the guess, test it, ask or state it, works the same over a chat message, an email, or out loud across a desk.
