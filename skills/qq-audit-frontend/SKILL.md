---
name: qq-audit-frontend
description: Serialized frontend build quality audit using 22 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 1.0.0
author: Lee Fuhr
triggers:
  - "frontend audit"
  - "code quality audit"
  - "build quality audit"
  - "frontend review"
  - "run frontend frameworks"
  - "run frontend audit"
---

# Audit frontend with expert personas

Audit frontend by running 22 expert personas in serial, fixing critical issues per framework before verifying.

22 code quality frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a senior frontend engineer with 20 years of specialization in that specific domain.

Expert lens: **Is the code well-built? Would a senior frontend engineer approve?**

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-frontend`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-frontend component architecture`, "just run state management on the dashboard", "typescript strictness on the API layer", etc.

Match the framework name fuzzily — "components", "component arch" should match Component Architecture. "state", "state mgmt" should match State Management Patterns. "ts strict", "typescript" should match TypeScript Strictness. If ambiguous, show the 2-3 closest matches and ask.

### Mode 3: List frameworks (help/list/discovery)

Triggers: "list", "what do you have", "what frameworks", "help", "which ones", "show me", etc.

Show the framework table from the Framework inventory section below, then ask which one(s) to run.

---

## Smart interview (runs before any audit)

**DO NOT ask dumb questions.** Before asking anything, gather what you already know:

1. **Check conversation context** — What product are we working on? What files have been discussed? What has the user been complaining about?
2. **Check project CLAUDE.md** — Product description, tech stack, target audience.
3. **Check recent session state** — What was just built or changed?

**Pre-fill and present assumptions:**

> "Here's what I know going in:
> - **Product:** [name] — [description from context]
> - **Tech stack:** [framework, language, build tool — inferred from project files]
> - **Quality bar:** [from previous audits or conversation]
> - **Known pain points:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full app / specific modules / specific component tree]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can't tell whether it's a Next.js or Vite project, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product's key modules/components to understand scope
3. Run `npx next build` or equivalent to establish baseline build state

### Phase 2: Serial framework execution

For each framework (in order 1-22):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-frontend/frameworks/[NN-name].md`"
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
1. Run framework #22 (Console/Runtime Error Hygiene) as the final cleanliness check
2. Compile consolidated report:
   - Per-framework scores (1-10 each)
   - Overall weighted average
   - All findings grouped by severity
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project's data directory:
- `data/audit-frontend-[date].md` — full report
- `data/audit-frontend-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Component Architecture | Atomic design and composability — are components structured in coherent, reusable layers with single responsibilities? | `01-component-architecture.md` |
| 2 | State Management Patterns | State architecture — is state minimal, derived where possible, and scoped to the narrowest boundary that needs it? | `02-state-management.md` |
| 3 | Render Performance | Render efficiency — do components re-render only when their actual dependencies change, without wasted cycles? | `03-render-performance.md` |
| 4 | Bundle Size / Code Splitting | Payload discipline — is the initial bundle lean, are routes lazy-loaded, and is every kilobyte justified? | `04-bundle-size.md` |
| 5 | TypeScript Strictness | Type safety discipline — is strict mode enabled, is `any` eliminated, and do types model the actual domain correctly? | `05-typescript-strictness.md` |
| 6 | Error Boundary Coverage | Runtime error containment — are errors caught at meaningful boundaries with useful fallback UI instead of white screens? | `06-error-boundaries.md` |
| 7 | API Integration Patterns | Data fetching discipline — are loading/error states handled, requests cached and deduplicated, and mutations optimistic where appropriate? | `07-api-integration.md` |
| 8 | CSS Architecture | Style organization — are styles scoped, non-conflicting, maintainable, and following a consistent methodology? | `08-css-architecture.md` |
| 9 | Dependency Health | Supply chain discipline — are dependencies maintained, minimal, justified, and free of duplication or known vulnerabilities? | `09-dependency-health.md` |
| 10 | Accessibility Implementation | Semantic correctness — are the right HTML elements used, ARIA roles applied correctly, and keyboard navigation complete? | `10-semantic-html-aria.md` |
| 11 | Form Handling Patterns | Form discipline — are validation, submission states, dirty tracking, and error recovery handled completely and consistently? | `11-form-handling.md` |
| 12 | Routing Architecture | Navigation structure — are routes nested correctly, guards enforced, deep links supported, and 404s handled? | `12-routing-architecture.md` |
| 13 | Environment/Configuration Management | Twelve-factor config — are environment-specific values externalized, secrets excluded from bundles, and builds identical across environments? | `13-env-configuration.md` |
| 14 | Code Organization / File Structure | Project structure — is the codebase organized for navigability, feature cohesion, and clear ownership boundaries? | `14-code-organization.md` |
| 15 | Client-Side Data Validation | Boundary defense — is all external data validated before the application trusts and renders it? | `15-data-validation.md` |
| 16 | Memory Leak Detection | Cleanup discipline — are subscriptions, listeners, timers, and references properly disposed when components unmount? | `16-memory-leaks.md` |
| 17 | Internationalization Readiness | Locale readiness — are strings externalized, formatting locale-aware, and layouts prepared for text expansion and RTL? | `17-i18n-readiness.md` |
| 18 | Build Pipeline Health | Build system integrity — is the build fast, reproducible, warning-free, and producing optimized output? | `18-build-pipeline.md` |
| 19 | Technical Debt Density | Debt inventory — are complexity thresholds monitored, TODOs tracked, and debt accumulation visible and intentional? | `19-technical-debt.md` |
| 20 | SSR/Hydration Correctness | Server/client parity — does the server-rendered HTML match the client-rendered output without mismatches or hydration errors? | `20-ssr-hydration.md` |
| 21 | Feature Flag / Progressive Rollout | Deployment decoupling — can features be toggled independently of deployment, with clean flag lifecycle management? | `21-feature-flags.md` |
| 22 | Console/Runtime Error Hygiene | Runtime cleanliness — is the console free of errors, warnings, and unhandled rejections in all application states? | `22-console-hygiene.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don't accumulate a findings list. Fix each framework's criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code, not screenshots** — this audit reads source code. Visual output is the UX audit's domain.
- **Multi-round** — after all 22 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don't re-report known issues.
