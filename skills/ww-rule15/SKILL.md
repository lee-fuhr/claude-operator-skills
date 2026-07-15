---
name: ww-rule15
description: "Mandatory end-to-end verification before claiming any feature is DONE, working, shipped, or verified. Invoke with /rule15 before marking features complete, after implementing features, or when auditing existing features for cosmetic code. Triggers: claiming something works, marking DONE in plans, before commits that close features, auditing the roadmap. A feature is DONE when its intended outcome is delivered, not when its UI renders."
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Rule 15: no cosmetic code

The gap this closes: an agent, or a teammate, says “done.” You check three weeks later and the button changes color, nothing saved, nothing sent, nobody downstream ever sees the change. The code path exists. The outcome doesn’t. This protocol makes “done” mean the outcome, every time, by forcing an explicit statement of what the user actually gets, plus a check from outside the implementer’s own head, before the word gets used.

A feature is DONE when its intended outcome is delivered to the user, not when its UI renders.

## Protocol (follow every step)

### 1. State the intended outcome

> **Intended outcome:** [one sentence — what the user gets]

If unsure, ask. Do not guess. Bad: “modal opens.” Good: “the user can create a working agent with tools and workflows.”

### 2. Trace the action chain

```
Trigger → Step 1 → Step 2 → ... → Outcome
```

Verify each step’s code path exists. If any step dead-ends, stop — it’s COSMETIC or PARTIAL.

### 3. Verify the feedback loop (success and error)

Every mutation (save, update, delete, cancel, archive, restore) MUST have:
- **Success feedback**: Toast, status change, or visible UI update confirming the action completed
- **Error feedback**: User-visible error message (toast, inline error), not just a console log
- **Loading state**: Button disabled or spinner while saving, so double-clicks don’t fire the action twice
- **State update**: Optimistic UI update OR refetch, so the user sees the change without refreshing

Check each mutation path. If any path silently succeeds or silently fails, it’s PARTIAL.

### 4. Test the real thing

Navigate to the feature. Perform the action. Screenshot or log the result. Did the outcome happen? Did you see confirmation feedback?

### 5. Verify the data (or the rendered output)

For data-changing features: query the actual store, whatever it is, SQL database, key-value store, flat file. Did the data change? Is it read downstream, or a dead end?
For display-only features: skip the data check. Verify the rendered output is correct instead.

### 6. Verdict

| Verdict | Definition |
|---------|-----------|
| **PASS** | Intended outcome achieved. User gets what they expected. |
| **PARTIAL** | Chain breaks before outcome. Document where. |
| **COSMETIC** | UI renders, outcome never achieved. Makeup on a pig. |
| **BROKEN** | Errors prevent function. |

## Effort-sizing floors (non-downgradeable)

Effort is set by feature complexity, not by who is running the check. The implementer cannot reduce their own floor — only someone with real authority over the project can explicitly accept a lower effort level.

| Condition | Minimum effort |
|-----------|----------------|
| Code change touching > 1 file | **medium** — run tests, check integration points |
| Change to a hook, scheduled job, or a shared config/instruction file | **high** — a real behavioral test, not just “the file exists” |
| Claim of “DONE” on a multi-session project | **high** — read the plan/status doc, run tests, verify against the stated outcome |

When multiple rows apply, the highest floor wins. “I built it, so I know it works” is not a floor override.

## External-verifier rule

The implementer’s own reasoning is not evidence. This is the classic “looks done, isn’t” failure, and it’s exactly what this protocol exists to catch. For any PASS verdict at **medium-or-higher effort**, at least one check must come from a source independent of the implementer’s own claims:

- A command whose **actual output is pasted**, not “I expect it would return…”
- A `grep` or `find` confirming something the implementer might have assumed
- For content or voice work: a style- or voice-check tool’s output, if the project has one
- For code: **full test suite output** shown, not cherry-picked passing tests

**PASS verdicts at medium-or-higher effort without external evidence are automatically downgraded to PARTIAL.**

## Output

```
## Rule 15: [Feature Name]
**Intended outcome:** ...
**Action chain:** Trigger → ... → [outcome or dead end]
**Feedback loop:** Success toast? Error toast? Loading state? State update?
**Test result:** [result]
**Data verification:** [result]
**Effort tier used:** [low|medium|high] (floor: [what floor applied])
**External evidence:** [what was checked externally, or "none — downgraded to PARTIAL"]
**Verdict:** PASS / PARTIAL / COSMETIC / BROKEN
**If not PASS:** What's missing.
**Plan doc update:** [what status was changed, from what to what]
```

## Rules

- Never mark DONE without running this protocol
- If not PASS, update your plan or status doc (e.g. `MASTER-PLAN.md`, `ROADMAP.md`) with the real status
- If unsure about the intended outcome, **ask**
- “Works in the code” but doesn’t deliver the outcome = COSMETIC
