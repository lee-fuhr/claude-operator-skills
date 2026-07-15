---
name: ww-plan-audit
description: The full gauntlet for plans. Runs automatically before exiting plan mode on any multi-phase plan, rather than waiting to be invoked by name. Combines interviewing, a principles deep read, multi-domain audit, steelman, pre-mortem, convergence, and prophylactic guardrails into one comprehensive quality process.
version: 1.0.0
triggers:
  - "audit this plan"
  - "full gauntlet"
  - "plan audit"
  - "is this plan ready"
  - "stress test the plan"
  - "plan quality check"
  - "run the gauntlet"
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# Audit a plan with the full gauntlet

Run a 10-dimension quality gauntlet on implementation plans to produce bulletproof guardrails before building. This is a gate, not a favor you ask for: run it automatically before exiting plan mode on any multi-phase plan, the same way a linter runs before a commit rather than waiting for someone to remember to ask for it.

**When to run:** Before exiting plan mode on any multi-phase plan. Non-optional for builds spanning more than one session.

**What it produces:** Not just “are there bugs in the plan?” but “will this be built right? What wisdom should get front-loaded so whoever builds it doesn’t have to discover it mid-build?”

---

## The 10 dimensions

| # | Dimension | What it asks | Source |
|---|-----------|-------------|--------|
| 1 | **Interview** | What’s in your head that isn’t in the plan? | Direct questions, before mechanical auditing starts |
| 2 | **Principles deep read** | Does the plan honor your own core engineering principles? | Your own standards doc, if you keep one (starter set below if you don’t) |
| 3 | **Anti-pattern hunt** | Are we about to repeat a known mistake? | An anti-pattern catalog (starter set below) |
| 4 | **Multi-domain audit** | What would 13 domain experts say about this plan? | A domain-audit skill, if you have one installed |
| 5 | **Steelman** | Which criticisms are real vs. fear-driven? | Adversarial self-review via external models |
| 6 | **Pre-mortem** | It’s 6 months out, this failed. Why? | Risk analysis |
| 7 | **Spec consistency** | Does the plan match the hardened spec? | Parent spec file |
| 8 | **Enforcement traceability** | For every rule in the plan, what enforces it at runtime? | The advisory/blocking/deterministic ladder |
| 9 | **Structural checks** | Failure plans, test targets, long-absence resilience, known debt | Checklist below |
| 10 | **Convergence** | Loop all of the above until no new criticals surface | Convergence loop pattern |

---

## Execution flow

### Phase 0: Context gathering (before anything else)

1. **Read the plan file.** Understand scope, milestones, deliverables.
2. **Read the parent spec** (if one exists). This is the hardened reference the plan must honor.
3. **Read the task notes** (if they exist): a context doc, a decisions log, an open-questions list, whatever you call them.
4. **Identify the project type**: internal tool, SaaS, marketing site, API service, and so on.

### Phase 1: Interview (the juicy direction)

**This is NOT a checkbox exercise.** The goal is to surface what’s in the plan owner’s head that the plan itself doesn’t capture: hidden requirements, aesthetic preferences, workflow assumptions, deal-breakers, analogies from tools they already use.

**Use multiple-choice questions where you can.** 2-8 rounds (6 is typical, 2 only for dead-simple plans), 2-3 questions per round. Each round builds on the previous answers. More rounds means a better plan; don’t rush this.

**Round 1: vision alignment**
- “The plan proposes building [X] before [Y]. Does that sequence match your instinct? Or did you expect a different order?”
- “The plan says [X]. When you imagine using this daily, does that match what’s in your head? Or were you picturing something different?”
- “What existing tool does this feel most like to you? (Not functionality, but the FEELING of using it)”
- “What would make you stop using this after a week?”

**Round 2: workflow probing**
- “Walk me through a typical day where you’d use this. When does it come up? What triggers you to open it?”
- “The plan defers [Y] to a later phase. Is that a deal-breaker, or are you fine without it for now?”
- “What’s the thing you’re most nervous about in this plan?”

**Round 3: edge cases and taste**
- “What’s the worst version of this that technically meets the spec but you’d hate?”
- “Any strong feelings about [specific technical decision]? Or do you trust the approach?”
- “What’s the one thing that, if we nail it, makes everything else forgivable?”

**Round 4 (if needed): contrarian pressure**
- “The plan assumes [Z]. What if that assumption is wrong?”
- “If you could only build 2 of these 5 deliverables, which 2?”
- “Is there anything in the plan that feels like it’s there because it’s ‘supposed to be’ rather than because you actually need it?”

**Adapt questions to the specific plan.** These templates are starting points. The best questions reference specific plan decisions and probe whether the plan’s owner actually agrees with them.

**Plain language over jargon.** Translate technical concepts into outcome language before asking: “the learning engine,” “when enough signal accumulates,” not internal variable or loop names. Someone gives a better answer when the question doesn’t require decoding your own architecture first.

**After interview:** incorporate answers into the plan. Update the decisions log. Some answers may invalidate plan sections; that’s the point.

**If the plan’s owner isn’t available to interview:** skip the interactive interview, continue with the remaining phases, embed the unanswered questions into the plan file under an “Interview questions (pending)” section, and note in the final summary that the interview is outstanding. The external-model steelman in Phase 4 doesn’t require anyone to be present.

### Phase 2: Principles deep read (code plans only)

**Mode gate.** This phase applies to **code plans** (building or refactoring software). For **content or strategy plans** (a messaging framework, a content calendar, positioning, a client deliverable), skip this phase entirely: citing engineering principles is empty ritual on a content plan. Instead, run a content-risk pass: does the intended voice hold, is every claim grounded and true (no fabrication), is the positioning defensible (no overclaim, no badmouthing a partner), is the scope right? Then proceed to the interview/steelman/pre-mortem phases, which apply to content plans as written.

For code plans:

If you maintain a living engineering-standards doc (a CONTRIBUTING.md, an architecture decision record, a house style guide, whatever you call it), actually read it with a file-read tool, not a cached summary of it and not your memory of what it probably says. A summary drifts from the source over time; the actual document is the ground truth.

**Read these sections for every plan**: use whatever your own doc calls them.
- Core principles: check each one against the plan
- Anti-pattern catalog: is the plan about to trigger one? (a starter catalog is below if you don’t have your own yet)
- Known debt: are we creating acknowledged debt, or accidentally recreating debt someone already paid down?

**Read the rest only when relevant:** architecture-placement rules (when placing new components), your own patterns catalog (when the plan uses a cataloged pattern), your project playbook (when sequencing phases), your agent- or task-delegation doc (when the plan hands work to sub-agents or other people).

**If you don’t have a standards doc yet**, use this starter set of principles instead: delegate rather than solo-execute wherever a clear split exists; keep one single source of truth per concept (no two stores that have to be kept in sync by a background job); don’t trust code that hasn’t been tested; use atomic operations (write to a temp file, then rename, never leave partial state on disk); delete dead code instead of commenting it out (version control remembers it); justify every new dependency; name things for what they actually are, not `data`/`temp`/`stuff`.

**For each principle, ask:** “If someone ignored this while executing the plan, would the plan’s own instructions actually stop them? Or is it advisory only?”

**Output:** a compliance table:

| Principle | Status | Notes |
|-----------|--------|-------|
| Delegate rather than solo-execute | Cited, enforced | Task assignments named per milestone |
| Test-first (red/green/refactor) | Cited, advisory | Test targets stated, but no red-phase gate |
| Checkpoint gates have failure plans | Cited, enforced | Every gate has a documented “what if no” |
| Atomic writes | Missing | No transaction guidance for multi-table writes |
| ... | | |

**Scale the depth of this read by plan complexity.** A quick fix only needs a summary pass. A standard build needs the summary plus a spot-read of whatever sections come up. A major architecture change earns a full read of the core-principles and anti-pattern sections, plus whatever else is relevant.

#### Starter anti-pattern catalog

If you’re building your own catalog from scratch, this is a reasonable starting set. Each one is a shape of failure that recurs across projects, not a one-off bug.

| Name | Signal |
|------|--------|
| The unbounded research loop | Automation runs indefinitely with no checkpoint validation |
| The premature learning engine | Building scoring/ML at a data volume too low for it to mean anything |
| Solo execution | The planner or orchestrator writing code directly instead of delegating |
| The retrospective test | Tests written after the implementation, so they can’t fail honestly first |
| Multiple sources of truth | A sync job keeping two data stores consistent, instead of one canonical store |
| Validate-then-pray | A try/catch wrapped around a call instead of validating inputs before it |
| The god file | Any file quietly growing past a few hundred lines because nobody split it |
| The silent service | A deployed service with no monitoring or alerting, so failure is invisible |
| The silent placeholder | A dashboard showing fake data that’s indistinguishable from real data |
| The unenforceable punch list | A “still to verify” list that nobody actually verifies |
| The advisory illusion | A rule exists in a doc, but nothing checks whether it’s followed at runtime (see Phase 4 for the deeper version of this one) |
| The system-speak leak | Database columns, filenames, or internal slugs showing up in user-facing text |
| The cosmetic done | A feature marked done because it renders in the UI, not because it delivers the outcome |

### Phase 3: Multi-domain audit (prophylactic)

Run a domain-audit process against the PLAN itself, not code (there is no code yet). The goal is prophylactic: surface wisdom from every relevant domain that should be front-loaded into the plan, before it’s expensive to change.

**For each domain, the question isn’t “is there a bug?” but “what should whoever builds this know going in?”**

| Domain | Plan-time question |
|--------|-------------------|
| Product | Is this the right thing? Are we solving the right problem? |
| UX | Are the user journeys sound? Are empty states planned? |
| Visual | What design rails should the builders follow? Prophylactic constraints. |
| Copy | What voice/tone patterns apply? Error message guidelines? |
| Frontend | Is the widget architecture sound? What’s the bundle strategy? |
| Backend | Is the API design sound? Any data-model gaps? |
| Performance | Will it be fast enough? Any obvious bottlenecks? |
| Security | Is the auth model solid? Are SSRF/XSS/CSRF covered? |
| Testing | Is the test strategy complete? What’s hard to test? |
| SEO | Applicable? If this affects a public site’s SEO, flag it. |
| DevOps | What’s the deployment strategy? Is there a rollback plan? |
| Data | Any schema migrations? What’s the data lifecycle and retention? |
| Compliance | Any legal considerations? Privacy? |

**Not every domain produces findings.** That’s fine; skip domains that genuinely don’t apply (note: “skipped, not applicable for [reason]”). But don’t skip a domain just because it SEEMS irrelevant at a glance; a visual-design pass on an API-only plan might still surface “when the dashboard eventually gets built, follow these patterns.”

**Triage by project type first.** A meta-system, pipeline, or backend-only project can skip user-facing domains (frontend, visual, copy, SEO, accessibility) with a documented “skipped, backend pipeline, no UI surface” note, rather than running the full domain sweep and finding nothing.

**Use read-only research agents where you can** (a handful in parallel) to run domain scans against the plan document, each covering 3-4 domains. If you have a dedicated multi-domain audit skill installed, invoke it directly instead of re-deriving this from scratch.

### Phase 4: Steelman (adversarial self-review)

**Hard requirement: convergent adversarial review via external models.** A steelman done only in your primary model’s own voice is self-validation, not a real check, because a model reviewing its own plan shares the plan’s blind spots by construction. Every plan audit needs at least two genuinely external, cross-vendor models as adversarial voices; your primary model synthesizes, it does not self-validate.

**Mandatory flow (don’t skip steps):**

1. **First-principles critique** (a free or cheap model, e.g. Groq): “Be adversarial. Find what the author missed: wrong direction, sequencing bugs, overlooked failure modes, false premises, quality-of-life problems for whoever operates this. Cite phase/item numbers. Under 600 words.”
2. **Alternative framing** (a second, different vendor, e.g. Gemini): “Don’t critique on the plan’s own terms; step back and offer a genuinely different approach. Simpler at 80/20? Riskier but faster? Is there an implicit architectural assumption worth rejecting? If you had to collapse this to 3 items in 3 days, what would they be? Under 500 words.”
3. **Optional third voice: your own house doctrine.** If you keep a written record of your own specific, recurring anti-patterns (the mistakes you personally keep making, distinct from generic engineering anti-patterns), route the plan through a prompt built from that doc as a third, additive voice. It doesn’t replace the two generic voices above: their value is model diversity; this one’s value is that it knows your specific blind spots.
4. **Fallback:** if a model returns a rate limit, timeout, or empty response, substitute a different model for the same prompt. Do not proceed with fewer than two distinct external voices; a single voice, however good, is a second opinion, not adversarial pressure.
5. **Synthesize survivors only.** Apply a steelman test to each critique: is this real, or is it fear-driven, marginal, or over-engineering? Kill the false positives; fold the real survivors into the plan. Tag anything that came from a house-doctrine voice separately, so recurring personal blind spots stay visible as a pattern.
6. **Save the external outputs somewhere durable:** a notes folder, or an appendix in the plan file itself, never a temp directory a reboot can wipe. The external critique is the audit evidence, and evidence that disappears on reboot isn’t evidence.

**Run this in a fresh context where you can** (a separate planning pass, a sub-agent). On top of the cross-model routing, this further reduces self-confirmation.

**Run the actual model calls yourself, directly, not delegated to a read-only research agent.** A read-only research/exploration agent typically can’t execute the scripts or API calls that reach an external model. If Phase 4 gets delegated to one of those anyway, what comes back looks like a real external critique but is actually the delegate’s own synthesized guess at what an external model would say, indistinguishable from the real thing until someone checks. That is exactly the advisory-illusion failure described below: the rule says “route to two external models,” and it looks satisfied, but the actual guard never fired.

**Gap check before Phase 5:** did at least two distinct external models actually run, with real output you can point to? If not, stop and route now. A self-steelman with no real external routing is the failure mode below, not a shortcut.

**The advisory-illusion trap, and how to actually fence it.** A rule that lives only in a process document, with nothing checking whether it happened, gets silently skipped the first time someone’s in a hurry. The rule existing in writing doesn’t stop the violation; it just makes the violation quieter and harder to notice. If a requirement like “route to two external models” matters enough to write down, it’s worth pairing with something that actually verifies it happened, rather than trusting everyone to remember every time. The strongest version of this: a pre-commit or pre-approval hook that checks a session log for at least two distinct external model calls and blocks the next step if it doesn’t find them, with an explicit, logged override for genuine exceptions, never a silent bypass.

**Specifically probe for:**
- Agent boundaries and handoff points
- Failure modes at each milestone
- Scope creep signals
- Assumptions that could be wrong
- Sequencing/dependency errors

### Phase 5: Pre-mortem

“It’s 6 months from now. This project failed. What was the most likely cause?”

Score each cause by likelihood (1-5) times severity (1-5). The top 5 risks must have both a prevention strategy and a mitigation strategy in the plan.

Focus on:
- Technical risks (will the approach actually work?)
- Motivation risks (will anyone still care about this in 3 weeks?)
- Scope risks (will this balloon?)
- Integration risks (will the pieces actually fit together?)
- Long-absence resilience (what happens if the project sits untouched for a while?)

### Phase 6: Spec consistency

If the plan has a parent spec, diff the plan against it:

- Features the spec requires that the plan omits (intentional? documented?)
- Decisions the plan makes that contradict the spec (a regression, or a deliberate evolution?)
- Security requirements the spec hardened that the plan softens
- Data model differences
- Auth model differences

**Every deviation must be intentional and documented.** “Plan deviates from spec on [X] because [Y]. Spec to be updated after phase [N].”

### Phase 7: Enforcement traceability

For every rule, constraint, or guideline in the plan, ask: **“What actually prevents someone from ignoring this?”**

Three levels, weakest to strongest:
- **Advisory**: the plan says to do it, but nothing checks. (Weakest: this is the advisory-illusion trap from Phase 4.)
- **Blocking**: a test or check fails if it’s violated. (Strong)
- **Deterministic**: the architecture makes violating it structurally impossible. (Strongest)

Flag any rule that’s advisory-only and should be blocking. Example: “test-first is stated, but there’s no test-count gate that would catch someone who skips writing tests.”

### Phase 8: Structural checks

Mechanical verification of plan completeness:

**Failure plans:**
- [ ] Every milestone gate has a “what if no” answer
- [ ] Failure plans are actionable (not “investigate further”)
- [ ] At least one failure plan involves cutting scope, not just debugging

**Test targets:**
- [ ] Every milestone with new code has a test-count target
- [ ] Tests are specified to be written first (red phase)
- [ ] An integration/end-to-end test covers the full flow

**Long-absence resilience:**
- [ ] Every milestone produces a genuinely working stopping point
- [ ] If the project sits untouched for weeks, what exists so far is still usable
- [ ] No milestone depends on completing the next milestone to be useful

**Known debt:**
- [ ] Any intentional shortcuts are documented as debt
- [ ] Debt has a “revisit in phase N” note
- [ ] No debt is hidden or assumed to be fine forever

**UX convergence gates (mandatory for any phase touching UI):**
- [ ] Every phase that touches UI has its own convergence gate
- [ ] The gate specifies what to audit and what states to verify
- [ ] The final phase includes a full-app convergence pass
- [ ] Backend-only phases explicitly note “no UX gate, backend only”

**Documentation:**
- [ ] The plan includes “initialize a decisions log” in its first milestone
- [ ] A task-notes structure exists or will be created

### Phase 9: Convergence loop

Run phases 2-8 as a convergence loop:

```
Round 1: principles + audit + steelman + pre-mortem + checks → findings
         Fix all CRITICAL findings in the plan
Round 2: re-run principles + steelman on the REVISED plan → new findings?
         Fix any new CRITICALs
Round 3: final steelman pass → any survivors?
         Apply. Done.
```

**Max 3 rounds** to prevent infinite loops. If round 3 still has CRITICALs, they’re probably fundamental design decisions that need direct human input, escalate rather than looping again.

**Convergence target:** zero CRITICALs, zero HIGH findings that are fixable at plan time.

### Phase 10: Final report

Present the results:

```
## Plan audit, full gauntlet results

**Rounds:** [N] convergence rounds
**Interview:** [N] rounds, [N] questions, [key insight]

### Principles compliance
[table from Phase 2]

### Domain audit findings
| Domain | Findings | Prophylactic rails | Applied to plan? |
|--------|----------|-------------------|-----------------|
| Product | 2 | ... | ✅ |
| Security | 3 | ... | ✅ |
| ... | | | |

### Steelman survivors
[list of findings that survived adversarial defense]

### Pre-mortem top 5 risks
[risk table with prevention/mitigation]

### Enforcement gaps
[advisory rules that should be blocking]

### Structural checks
[pass/fail on each checkbox]

### Changes made to plan
[list of plan modifications from this audit]

**Verdict:** plan is [READY / NEEDS WORK on X]
```

Then: exit plan mode.

---

## When NOT to run the full gauntlet

- **Single-file changes, bug fixes, trivial tasks**: overkill. Steelman alone is sufficient.
- **Plans with fewer than 2 milestones**: run phases 1-5 only (interview, principles, steelman, pre-mortem, spec check). Skip the full domain audit and convergence loop.
- **Plans already audited**: if running a second time (e.g., after major revisions), skip the interview and only re-run phases affected by the changes.

## Scaling by plan complexity

| Plan type | What to run |
|-----------|-------------|
| **Quick fix** (1 milestone) | Steelman only |
| **Small build** (2-3 milestones) | Interview + principles + steelman + pre-mortem |
| **Standard build** (4-6 milestones) | Full gauntlet, all 10 phases |
| **Major architecture** (7+ milestones, novel territory) | Full gauntlet + an adversarial team (a few different perspectives run in parallel) |

---

## Key principles

- **Interview is phase 1**: surface what’s in the plan owner’s head BEFORE auditing the plan mechanically. The best plans fail because they solved the wrong problem, not because they had technical gaps.
- **Prophylactic, not just corrective**: domain audits on plans aren’t bug-finding. They’re wisdom front-loading. “When you build the next phase, here are the accessibility patterns to follow.”
- **Convergence, not single-pass**: one audit pass finds roughly 60% of issues. Loop until clean.
- **Every criticism is steelmanned**: roughly half of “critical issues” from a first pass are fear-driven. Kill the false positives.
- **The plan’s owner stays in control**: present findings, let them decide what to fix. Don’t silently modify the plan.
- **The plan is the deliverable**: the gauntlet produces a BETTER PLAN, not a report about the plan.
