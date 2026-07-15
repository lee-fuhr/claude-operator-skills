---
name: qq-audit-testing
description: Serialized QA/Testing audit using 22 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 1.0.0
author: Lee Fuhr
triggers:
  - "testing audit"
  - "qa audit"
  - "test quality audit"
  - "test framework review"
  - "run testing audit"
  - "test coverage review"
  - "run all test frameworks"
---

# Audit QA and testing with expert personas

Run a full serial QA audit using 22 deep expert persona frameworks, fixing critical issues and verifying each framework before proceeding to the next.

22 testing frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year QA specialist in that specific framework.

**Domain:** Testing. **Expert lens:** Is it tested? Would a QA lead approve?

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-testing`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-testing mutation testing`, "just run boundary value on the parser", "test isolation on the API layer", etc.

Match the framework name fuzzily — "pyramid", "test pyramid", "pyramid balance" should all match Test Pyramid Balance. "flaky", "flaky tests", "quarantine" should all match Flaky Test Detection. If ambiguous, show the 2-3 closest matches and ask.

### Mode 3: List frameworks (help/list/discovery)

Triggers: "list", "what do you have", "what frameworks", "help", "which ones", "show me", etc.

Show the framework table from §Framework inventory below, then ask which one(s) to run.

---

## Smart interview (runs before any audit)

**DO NOT ask dumb questions.** Before asking anything, gather what you already know:

1. **Check conversation context** — What product are we working on? What files have been discussed? What has the user been complaining about?
2. **Check project CLAUDE.md** — Product description, tech stack, target audience.
3. **Check recent session state** — What was just built or changed?

**Pre-fill and present assumptions:**

> "Here's what I know going in:
> - **Product:** [name] — [description from context]
> - **Tech stack:** [languages, frameworks, test runners — inferred from project]
> - **Current test state:** [test count, coverage %, CI status — from recent runs]
> - **Known pain points:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full codebase / specific module / specific test suite]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can't tell what test runner is in use, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product's test files, config, and CI pipeline to understand scope
3. Run existing test suite to establish baseline

### Phase 2: Serial framework execution

For each framework (in order 1-22):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-testing/frameworks/[NN-name].md`"
   - "You ARE the expert described in that document. Think like them, not like a generalist."
   - "Audit [product name] focusing on [scope]. Context: [interview output]"
   - "Previous frameworks found these issues: [cumulative findings list]. Do NOT re-report duplicates."
   - "Score 1-10, list findings with file:line references, fix critical issues (score < 7), write report."

2. **Collect the agent's output:**
   - Score for this framework
   - Findings (new, not duplicates)
   - Fixes applied
   - Items flagged for downstream frameworks

3. **Verify build** if fixes were applied (run test suite or equivalent)

4. **Update cumulative state:**
   - Add findings to the dedup list
   - Update the running score card
   - Note cross-framework flags for upcoming frameworks

5. **Move to next framework**

### Phase 3: Synthesis
1. Run framework #22 (Data Integrity/Migration Testing) as the final evaluation
2. Compile consolidated report:
   - Overall testing health score (average of all frameworks)
   - Per-framework scores
   - All findings grouped by severity
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project's data directory:
- `data/audit-testing-[date].md` — full report
- `data/audit-testing-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Test Pyramid Balance | Healthy ratio of unit:integration:e2e — fast feedback at the base, confidence at the top | `01-test-pyramid.md` |
| 2 | Meaningful Code Coverage | Assertion density, not just line execution — does your coverage number actually mean anything? | `02-code-coverage.md` |
| 3 | Boundary Value Analysis | Off-by-one, empty, null, max, zero, negative — bugs cluster at the edges of valid input ranges | `03-boundary-value.md` |
| 4 | Equivalence Partitioning | Test cases represent input classes — one value from each partition proves the whole partition works | `04-equivalence-partitioning.md` |
| 5 | Happy Path / Sad Path Coverage | Every failure mode tested — optimistic-only testing is how bugs reach production | `05-happy-sad-paths.md` |
| 6 | Test Isolation / Independence | No shared state, any-order execution — tests that depend on each other are tests that lie to you | `06-test-isolation.md` |
| 7 | Mutation Testing | Tests that actually detect bugs — mutate the code, see if the tests catch it | `07-mutation-testing.md` |
| 8 | Contract Testing | Consumer-driven API contracts verified on both sides — no more "it works on my machine" between services | `08-contract-testing.md` |
| 9 | Visual Regression Testing | Screenshot comparison catches CSS regressions — the bugs that functional tests structurally cannot see | `09-visual-regression.md` |
| 10 | Accessibility Testing Automation | WCAG violations caught in CI — automated axe-core/pa11y scans as the first line of accessibility defense | `10-a11y-testing-automation.md` |
| 11 | Load/Stress Testing | System performs under expected and peak load — find the breaking point before your users do | `11-load-stress-testing.md` |
| 12 | Chaos/Resilience Testing | Handles infrastructure failures gracefully — break things intentionally so they don't break you in production | `12-chaos-resilience.md` |
| 13 | Smoke/Sanity Test Suite | Fast critical path verification after deployment — the 2-minute check that saves 2-hour incidents | `13-smoke-sanity.md` |
| 14 | Test Data Management | Factories over fixtures, no shared mutable state — test data strategy determines test reliability | `14-test-data-management.md` |
| 15 | Flaky Test Detection and Quarantine | Identified, quarantined, tracked — flaky tests erode trust and must be managed as defects, not nuisances | `15-flaky-test-detection.md` |
| 16 | Cross-Browser/Cross-Device Testing | Works across target browsers and devices — not just the browser on the developer's laptop | `16-cross-browser-device.md` |
| 17 | Error Scenario Simulation | Fault injection at the application level — API failures, timeouts, auth expiration, network errors, all tested deliberately | `17-error-scenario-simulation.md` |
| 18 | Regression Test Effectiveness | Historical defect escape rate measured — does the test suite actually catch regressions, or does it just feel like it does? | `18-regression-effectiveness.md` |
| 19 | Test Readability/Maintainability | Arrange-Act-Assert, descriptive names, self-documenting tests — tests are documentation that happens to be executable | `19-test-readability.md` |
| 20 | CI Pipeline Speed and Reliability | Under 10 minutes to green, failures are real — the CI pipeline is a feedback loop, and slow loops kill quality | `20-ci-pipeline-speed.md` |
| 21 | Feature Flag Testing | Both on/off states tested, conflicting combinations covered — feature flags multiply your test surface, not simplify it | `21-feature-flag-testing.md` |
| 22 | Data Integrity/Migration Testing | Schema migrations tested forward and backward — because an untested migration is a production outage waiting for Friday at 5 PM | `22-data-migration-testing.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don't accumulate a findings list. Fix each framework's criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — no retrospective-only tests, red/green/refactor discipline, and unhappy paths tested before happy paths.
- **Code-level evidence** — every finding must reference specific files and lines. No hand-waving.
- **Multi-round** — after all 22 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don't re-report known issues.
