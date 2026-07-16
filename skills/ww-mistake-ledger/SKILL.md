---
name: ww-mistake-ledger
description: The moment a real, avoidable mistake happens, name it plainly, root-cause the general class of it rather than just this one instance, and fix it at a level that prevents a repeat, not a note that gets written and forgotten. Then, before starting work that looks like it could repeat that shape, check the log first. A second occurrence of the same mistake means the note wasn’t enough, and it needs to become a real check instead of a reminder. Invoke with /ww-mistake-ledger, or say “log this mistake,” “close the loop on this,” “add this to the mistake log,” “check the mistake log first,” right after a preventable error, or right before starting work that resembles one already logged.
version: 1.0.0
triggers:
  - “log this mistake”
  - “close the loop on this”
  - “add this to the mistake log”
  - “check the mistake log first”
  - “has this happened before”
  - “root-cause this”
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Log the mistake, close the loop

The gap this closes: the same mistake gets made twice, sometimes three times, each time with the same surprised reaction, because it got written down once and then never looked at again. A mistakes doc that only ever gets appended to isn’t a safety net, it’s a diary nobody rereads. The actual failure usually isn’t forgetting to write the note, most people are decent about writing the note right after something breaks. The failure is that the note sits there, correct and unread, while the exact same shape of mistake happens again three weeks later, on a different piece of work that never got checked against it. Closing the loop means the log gets read before the next matching decision, not just added to after the last one.

**A mistake is closed when the next matching situation doesn’t repeat it, not when it’s been written down.**

## Protocol (follow every step)

### 1. Confirm it’s a real mistake, not just friction

Reserve this for a genuine, avoidable error with a real consequence: wrong output, lost work, a broken process, actual cost to someone. Normal iteration isn’t a mistake. A first draft needing a second pass, an honest “I don’t know yet,” a plan that changed because you learned something mid-task, none of that qualifies. Treating every rough edge as a logged mistake turns the ledger into noise, and noise is what gets skipped on the next read-through.

### 2. Name it plainly as preventable

State what happened in one direct sentence, no hedging, no softening it into a wall of “here’s what I did instead.” “I deleted the file before checking whether anything else referenced it” is a mistake sentence. Three paragraphs explaining the good intentions behind the deletion is not.

### 3. Root-cause the class, not the instance

The specific mistake, “deleted that one file,” isn’t the useful part, the general shape of it is. Ask what category of situation this belongs to, and what would have caught it regardless of which specific file, which specific command, which specific day it happened on. “Deleted a file without checking references first” generalizes. “Deleted `config.old.json` on a Tuesday” doesn’t; you’ll never match on those exact specifics again, but you’ll absolutely hit “about to delete something without checking references” again.

### 4. Fix it at the enforcement layer, same sitting

This is the step that’s easiest to skip, and it does most of the work. A root cause without a fix is just a well-written diagnosis. Before moving on, add something that catches this on its own next time: a checklist item you’ll genuinely follow, a lint rule, a pre-flight check, a config change, a test. “I’ll remember” is not an enforcement layer, it’s the thing that failed last time.

### 5. Write the entry down somewhere you’ll check

Keep a running log, a file, a doc, whatever already fits how you work. Each entry needs three things: what happened, the general class it belongs to, and how to prevent it, the fix from step 4. Skip the temptation to build an elaborate taxonomy before you’ve even logged five entries; a plain running list beats a perfect system nobody maintains.

### 6. Check the log before matching work starts

This is the loop-closing step, and it’s the one most mistake-logging habits skip. Before starting work that resembles a past entry’s shape, look. Not from memory. Check the file. A log that only gets written to and never read is doing half the job.

### 7. Escalate on repeat

If the same class of mistake happens a second time, the fix from step 4 wasn’t enough. That’s the signal, not a reason to just write a second, more detailed entry. Move the fix up a level: a checklist item that got missed becomes a hook that runs automatically; a “remember to verify” becomes a test that fails if you don’t. The escalation ladder exists because a written reminder and an enforced check catch different failure rates, and a repeat mistake is proof you needed the stronger one the first time.

## Why this differs from a generic mistakes doc

Plenty of habits already say “keep a running list of mistakes.” Two things separate this one from that: the log gets checked before matching work starts, not just added to after it ends, and a second occurrence of the same class is treated as proof the fix was too weak, triggering an upgrade to something enforced, rather than just another entry in the list. Without both of those, a mistakes doc is a nice idea that quietly stops getting read after the first few weeks.

## A worked example

**First occurrence:** a cleanup script runs directly against a real, shared folder with no dry-run flag. A wildcard pattern matches more files than intended, and it deletes things nobody meant to touch. Logged: “ran a destructive script against real data without a preview step or a scoped test first. General class: any script with a wildcard delete needs a preview before it’s allowed to run for real.” Fix at the enforcement layer: the script’s delete function now defaults to preview-only, and requires an explicit flag to delete anything.

**Three weeks later:** a different script, a different purpose, same general shape, a bulk-rename step with a wildcard match, gets written. Because the log gets checked before this kind of work starts, the rename script ships with a preview step from the first draft, not after it renames the wrong files. The mistake never happens a second time, not because everyone remembered the first one, but because the log was consulted before building the second one.

## What it’s not

- **Not a ritual for every hiccup.** Save it for mistakes with a real, avoidable consequence, not routine iteration.
- **Not a blame document.** The class matters, not the person or the specific moment it happened.
- **Not finished at the write-up.** Writing it down is step five of seven, not the finish line.

## Key principles

- **Prevention is the finish line, not documentation.** A written mistake that recurs unchanged has not been closed, whatever the log says.
- **Generalize one level up.** The specific instance rarely repeats; the class almost always does.
- **A second occurrence is data, not bad luck.** It means the fix was underpowered, not that you got unlucky twice.
- **Cheap and constant beats rare and heavy.** A short entry logged the moment it happens, checked before the next similar task, does more than an occasional deep audit of everything that’s gone wrong.
