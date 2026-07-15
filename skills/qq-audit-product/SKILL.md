---
name: qq-audit-product
description: Serialized product audit using 20 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 1.0.0
author: Lee Fuhr
triggers:
  - "product audit"
  - "product review"
  - "product strategy audit"
  - "feature audit"
  - "product-market fit"
  - "run product audit"
  - "jobs to be done"
---

# Audit product with expert personas

Audit product by running 20 expert personas in serial, fixing critical issues per framework before verifying.

20 product frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

The expert lens: **Is this the right product? Does it solve real problems? Is the investment going to the right places?** UX audits ask "is this usable?" — product audits ask "should this exist, and does it deliver value?"

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-product`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-product JTBD`, "just run kano on the pipeline", "red route on the dashboard", etc.

Match the framework name fuzzily — "jtbd", "jobs", "jobs to be done" should all match Jobs to Be Done. "kano", "kano model", "feature classification" should all match Kano Model. "pmf", "product market fit" should match Product-Market Fit Signals. If ambiguous, show the 2-3 closest matches and ask.

### Mode 3: List frameworks (help/list/discovery)

Triggers: "list", "what do you have", "what frameworks", "help", "which ones", "show me", etc.

Show the framework table from §Framework inventory below, then ask which one(s) to run.

---

## Smart interview (runs before any audit)

**DO NOT ask dumb questions.** Before asking anything, gather what you already know:

1. **Check conversation context** — What product are we working on? What features have been discussed? What has the user been frustrated about?
2. **Check project CLAUDE.md** — Product description, tech stack, target audience, business model.
3. **Check recent session state** — What was just built, launched, or changed?

**Pre-fill and present assumptions:**

> "Here's what I know going in:
> - **Product:** [name] — [description from context]
> - **Target user:** [who — inferred from project docs or conversation]
> - **Stage:** [pre-launch / early / growth / mature — inferred from context]
> - **Business model:** [how it makes money — if known]
> - **Known concerns:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full product / specific feature area / specific workflow]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can't tell the target user or product stage, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product's key pages/components to understand scope
3. Map the feature surface area — what exists, what's claimed, what's actually built

### Phase 2: Serial framework execution

For each framework (in order 1-20):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-product/frameworks/[NN-name].md`"
   - "You ARE the expert described in that document. Think like them, not like a generalist."
   - "Audit [product name] focusing on [scope]. Context: [interview output]"
   - "Previous frameworks found these issues: [cumulative findings list]. Do NOT re-report duplicates."
   - "Score 1-10, list findings with file:line references, fix critical issues (score < 7), write report."

2. **Collect the agent's output:**
   - Score for this framework
   - Findings (new, not duplicates)
   - Fixes applied
   - Items flagged for downstream frameworks

3. **Verify build** if fixes were applied (`npx next build` or equivalent)

4. **Update cumulative state:**
   - Add findings to the dedup list
   - Update the running score card
   - Note cross-framework flags for upcoming frameworks

5. **Move to next framework**

### Phase 3: Synthesis
1. Run framework #20 (Ecosystem Integration) as the final external-facing evaluation
2. Compile consolidated report:
   - Overall product health score (average of 20 frameworks)
   - Per-framework scores
   - All findings grouped by severity
   - Fixes applied (with file:line)
   - Strategic recommendations (things that can't be fixed in code alone)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project's data directory:
- `data/audit-product-[date].md` — full report
- `data/audit-product-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Jobs to Be Done | Whether each feature maps to a real job the user is hiring the product for | `01-jobs-to-be-done.md` |
| 2 | Kano Model | Classifies features as must-be, one-dimensional, attractive, indifferent, or reverse to guide investment | `02-kano-model.md` |
| 3 | User Journey Completeness | Whether every step of the end-to-end journey is supported, including edge paths and recovery | `03-user-journey-completeness.md` |
| 4 | Five States | Whether every screen handles empty, loading, error, partial, and ideal states | `04-five-states.md` |
| 5 | RICE Prioritization | Whether feature investment is allocated by reach, impact, confidence, and effort | `05-rice-prioritization.md` |
| 6 | Outcome Over Output | Whether features connect to measurable outcomes, not just shipped artifacts | `06-outcome-over-output.md` |
| 7 | Feature-Benefit Mapping | Whether every feature has a clear user benefit articulated and delivered | `07-feature-benefit-mapping.md` |
| 8 | Competitive Gap Analysis | Whether the product covers capabilities users expect from alternatives | `08-competitive-gap.md` |
| 9 | User Story Mapping | Whether the backbone is complete before details are built, keeping the big picture intact | `09-user-story-mapping.md` |
| 10 | Red Route Analysis | Whether the critical paths used by 80%+ of users are optimized above all else | `10-red-route-analysis.md` |
| 11 | Onboarding Completeness | Whether new users reach first value without external help | `11-onboarding-completeness.md` |
| 12 | Aha Moment Mapping | Whether the product reliably delivers the core value moment that converts users into believers | `12-aha-moment.md` |
| 13 | Product-Market Fit Signals | Whether usage patterns indicate real product-market fit or just polite adoption | `13-product-market-fit.md` |
| 14 | Scope Creep Detection | Whether features exist that serve no user segment and drain resources from what matters | `14-scope-creep-detection.md` |
| 15 | Information Architecture Completeness | Whether the product's conceptual model matches users' mental models | `15-ia-completeness.md` |
| 16 | Workflow Efficiency | Whether multi-step tasks have the minimum necessary steps, eliminating waste from every workflow | `16-workflow-efficiency.md` |
| 17 | Notification Completeness | Whether the product tells users what they need to know without over-notifying | `17-notification-completeness.md` |
| 18 | Permission/Role Model Completeness | Whether access control covers all user types without over-restricting or under-protecting | `18-permission-model.md` |
| 19 | Data Portability | Whether users can export their data and derive value independent of switching costs | `19-data-portability.md` |
| 20 | Ecosystem Integration | Whether the product connects to the tools users already rely on | `20-ecosystem-integration.md` |

---

## Key principles

- **Serial, not parallel** — Frameworks build on each other. JTBD informs Kano which informs RICE. Serial means each round inherits context from prior findings.
- **Fix before moving on** — Don't accumulate a findings list. Fix each framework's criticals before the next audit.
- **Expert persona, not checklist** — Each agent IS the specialist. They reason from product principles, not checklists.
- **Hold every fix to a real quality bar** — is this real data? Is the complexity earned? Are you building a scoring or ML system before you have the data volume to justify it?
- **Strategy + code** — Product audits produce two kinds of findings: code fixes (apply now) and strategic recommendations (surface to the user for decision). Both are valid outputs.
- **Multi-round** — After all 20 frameworks, run the full cycle again. Product health improves each round as fixes compound.
- **Dedup across frameworks** — Each agent receives cumulative findings so they don't re-report known issues.
- **Right product > right implementation** — UX asks "is this usable?" Product asks "should this exist?" Kill features that don't serve a job before polishing them.

---

## Relationship to UX audit

Product audit and UX audit are complementary, not overlapping:

| | Product audit | UX audit |
|---|---|---|
| **Question** | Is this the right product? | Is this product usable? |
| **Finds** | Missing features, wasted features, wrong priorities, unserved jobs | Usability issues, accessibility gaps, interaction problems |
| **Fixes** | Add/remove/reprioritize features, restructure workflows | Adjust UI, improve feedback, fix interaction patterns |
| **Run order** | Product first (kill wrong features before polishing them) | UX second (polish what survives product audit) |

When running both, product audit prunes the scope. UX audit polishes what remains.
