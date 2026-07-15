---
name: qq-audit-data
description: Serialized data quality audit using 15 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 3.0.0
author: Lee Fuhr
triggers:
  - "data audit"
  - "data quality audit"
  - "analytics audit"
  - "tracking audit"
  - "data review"
  - "run data audit"
---

# Audit data quality with expert personas

Audit data quality by running 15 expert personas in serial, fixing critical issues per framework before verifying.

15 data quality frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

Expert lens: Is the data trustworthy? Are decisions being informed?

Supersedes: ad-hoc analytics reviews, one-off tracking audits.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-data`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-data funnel instrumentation`, "just run dashboard accuracy on the metrics page", "check event taxonomy", etc.

Match the framework name fuzzily — "funnel", "conversion", "drop-off" should all match Funnel Instrumentation. "dashboard", "metrics", "accuracy" should all match Dashboard Accuracy Audit. If ambiguous, show the 2-3 closest matches and ask.

### Mode 3: List frameworks (help/list/discovery)

Triggers: "list", "what do you have", "what frameworks", "help", "which ones", "show me", etc.

Show the framework table from the framework inventory below, then ask which one(s) to run.

---

## Smart interview (runs before any audit)

**DO NOT ask dumb questions.** Before asking anything, gather what you already know:

1. **Check conversation context** — What product are we working on? What files have been discussed? What has the user been complaining about?
2. **Check project CLAUDE.md** — Product description, tech stack, target audience.
3. **Check recent session state** — What was just built or changed?

**Pre-fill and present assumptions:**

> "Here’s what I know going in:
> - **Product:** [name] — [description from context]
> - **Analytics stack:** [GA4 / Mixpanel / PostHog / custom — inferred from project]
> - **Data layer:** [GTM / Segment / custom dataLayer — inferred from code]
> - **Known data concerns:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full tracking / specific funnel / specific dashboard]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can’t tell what analytics platform is in use, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product’s analytics config, event tracking code, and data layer implementation to understand scope
3. Map the data surface: events tracked, funnels defined, dashboards deployed, third-party integrations

### Phase 2: Serial framework execution

For each framework (in order 1-15):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-data/frameworks/[NN-name].md`"
   - "You ARE the expert described in that document. Think like them, not like a generalist."
   - "Audit [product name] focusing on [scope]. Context: [interview output]"
   - "Previous frameworks found these issues: [cumulative findings list]. Do NOT re-report duplicates."
   - "Score 1-10, list findings with file:line references, fix critical issues (score < 7), write report."

2. **Collect the agent’s output:**
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
1. Run framework #15 (Real-Time vs Batch Freshness) as the final timeliness review
2. Compile consolidated report:
   - Overall data quality score
   - Per-framework scores
   - All findings grouped by severity (critical / high / medium / low)
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project’s data directory:
- `data/audit-data-[date].md` — full report
- `data/audit-data-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Analytics Implementation Completeness | Measurement coverage — are you tracking every key user action, funnel step, and business event that drives decisions? | `01-analytics-completeness.md` |
| 2 | Data Layer Architecture | Data plumbing — is event data flowing through a clean, centralized data layer instead of scattered vendor-specific calls? | `02-data-layer.md` |
| 3 | Event Taxonomy Consistency | Naming discipline — do events follow a consistent, documented naming convention that makes querying intuitive and reliable? | `03-event-taxonomy.md` |
| 4 | Data Validation and Integrity | Data correctness — do integrity constraints, validation rules, and automated checks catch data corruption before it reaches dashboards and decisions? | `04-data-validation.md` |
| 5 | Privacy-Compliant Tracking | Consent and privacy — does tracking respect user choices, anonymize where required, and comply with GDPR/CCPA requirements? | `05-privacy-compliant-tracking.md` |
| 6 | Funnel Instrumentation | Conversion path visibility — does every critical funnel have events at every step with drop-off visibility between steps? | `06-funnel-instrumentation.md` |
| 7 | A/B Testing Infrastructure | Experimentation rigor — can you run controlled experiments with proper randomization, sufficient sample sizes, and statistically valid conclusions? | `07-ab-testing-infra.md` |
| 8 | Data Retention and Lifecycle | Data lifecycle hygiene — are retention periods defined, automated cleanup running, and old data properly archived or deleted? | `08-data-retention.md` |
| 9 | Dashboard Accuracy Audit | Metric trustworthiness — do dashboard numbers match their source data, are calculations correct, and can stakeholders trust what they see? | `09-dashboard-accuracy.md` |
| 10 | Error Tracking Coverage | Failure visibility — are client and server errors captured with enough context to diagnose the problem and understand its user impact? | `10-error-tracking.md` |
| 11 | Search Analytics | Search intelligence — are search queries tracked, zero-results visible, and search quality measured so you know what users want but can’t find? | `11-search-analytics.md` |
| 12 | Attribution Modeling | Conversion credit — does your attribution model match business reality, or is it giving credit to the wrong channels? | `12-attribution-modeling.md` |
| 13 | Data Export and Portability | Data freedom — can users get their data out in standard formats, and is the system a partner rather than a data roach motel? | `13-data-export.md` |
| 14 | Schema Evolution Management | Schema change safety — can you add, modify, or remove event properties and data fields without breaking existing queries, dashboards, and pipelines? | `14-schema-evolution.md` |
| 15 | Real-Time vs Batch Freshness | Data timeliness — does data freshness match business needs, and is the freshness clearly labeled so stakeholders know what they’re looking at? | `15-data-freshness.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don’t accumulate a findings list. Fix each framework’s criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code + live data** — code audits miss data quality issues. Always check actual event payloads, dashboard outputs, and query results when possible.
- **Multi-round** — after all 15 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don’t re-report known issues.
