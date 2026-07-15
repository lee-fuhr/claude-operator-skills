---
name: qq-audit-backend
description: Serialized backend/API audit using 22 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 3.0.0
author: Lee Fuhr
triggers:
  - "backend audit"
  - "api audit"
  - "server audit"
  - "api review"
  - "backend review"
  - "run backend audit"
---

# Audit backend with expert personas

Audit the backend by running 22 expert personas in serial, fixing critical issues per framework before verifying.

22 backend frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

Expert lens: Is the server-side solid? Would a senior backend engineer approve?

Supersedes: ad-hoc API reviews, one-off performance audits.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-backend`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-backend RESTful Design`, "just run query efficiency on the search endpoint", "rate limiting on the public API", etc.

Match the framework name fuzzily — "rest", "restful", "richardson" should all match RESTful API Design Maturity. "n+1", "query", "database queries" should all match Database Query Efficiency. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Tech stack:** [framework, language, ORM, database — inferred from project]
> - **API style:** [REST / GraphQL / tRPC — inferred from routes]
> - **Known pain points:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full API / specific endpoints / specific service]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can’t tell whether it’s REST or GraphQL, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product’s key routes, controllers, and data models to understand scope
3. Map the API surface: endpoints, middleware, auth flows, database interactions

### Phase 2: Serial framework execution

For each framework (in order 1-22):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-backend/frameworks/[NN-name].md`"
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
1. Run framework #22 (Graceful Degradation/Circuit Breaker) as the final resilience check
2. Compile consolidated report:
   - Overall backend health score
   - Per-framework scores
   - All findings grouped by severity (critical / high / medium / low)
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project’s data directory:
- `data/audit-backend-[date].md` — full report
- `data/audit-backend-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | RESTful API Design Maturity | Richardson Maturity Model — are your APIs actually RESTful or just HTTP endpoints with JSON? | `01-restful-design.md` |
| 2 | API Contract/Schema Validation | OpenAPI and JSON Schema — are your API contracts formally defined, versioned, and enforced at runtime? | `02-api-schema-validation.md` |
| 3 | Error Handling Taxonomy | RFC 7807 Problem Details — are your error responses consistent, structured, and actionable for every failure mode? | `03-error-handling-taxonomy.md` |
| 4 | Input Validation Depth | OWASP input validation — are you validating type, range, format, and business rules at the API boundary before anything else touches the data? | `04-input-validation.md` |
| 5 | Authentication Architecture | OAuth 2.0/OIDC token lifecycle — are credentials issued, validated, refreshed, and revoked correctly at every layer? | `05-auth-architecture.md` |
| 6 | Authorization Model | RBAC/ABAC permission enforcement — are permissions checked at every endpoint, on every resource, for every operation? | `06-authorization-model.md` |
| 7 | Database Query Efficiency | Indexed, no N+1, appropriate joins — are your database queries doing the minimum work to answer each request? | `07-query-efficiency.md` |
| 8 | Data Model/Schema Design | Domain representation, relationships, and migrations — does your data model accurately represent reality and evolve safely? | `08-data-model-design.md` |
| 9 | API Rate Limiting/Throttling | Per-user, per-endpoint, global limits — are you protecting your system from abuse without punishing legitimate use? | `09-rate-limiting.md` |
| 10 | Idempotency and Retry Safety | Duplicate execution produces correct results — can clients safely retry any request without causing duplicates or corruption? | `10-idempotency.md` |
| 11 | Pagination/Bulk Data Handling | Cursor-based, stable, efficient — are your list endpoints safe to paginate through without missing records or repeating them? | `11-pagination.md` |
| 12 | Caching Strategy | HTTP and application-level caching — are cache lifetimes bounded, invalidation reliable, and stale data managed explicitly? | `12-caching-strategy.md` |
| 13 | Background Job/Async Processing | Queue-based with progress, retry, and dead letter — are your async operations reliable, observable, and recoverable? | `13-background-jobs.md` |
| 14 | Logging and Observability | OpenTelemetry end-to-end traces and structured fields — can you answer "what happened?" for any request, any time, within minutes? | `14-logging-observability.md` |
| 15 | Database Migration Safety | Reversible, zero-downtime, tested — can your schema evolve without taking the application offline or losing data? | `15-migration-safety.md` |
| 16 | API Versioning Strategy | Breaking change management — can you evolve the API without stranding existing clients or forcing synchronized upgrades? | `16-api-versioning.md` |
| 17 | Webhook/Event Architecture | Reliable delivery, retry, and signature verification — are your webhooks trustworthy for the systems that depend on them? | `17-webhook-events.md` |
| 18 | Multi-Tenancy Isolation | Tenant data properly isolated at every layer — can one tenant ever see, modify, or affect another tenant’s data or experience? | `18-multi-tenancy.md` |
| 19 | Transaction Management | ACID/saga patterns — do your succeed-or-fail-together operations actually succeed or fail together? | `19-transaction-management.md` |
| 20 | Health Check/Readiness Probe | "Alive" vs. "ready to serve" — can your infrastructure distinguish between a running process and a process that can actually handle requests? | `20-health-checks.md` |
| 21 | Configuration and Secrets Management | 12-factor external config — are your secrets external, rotatable, audited, and never, ever logged? | `21-config-secrets.md` |
| 22 | Graceful Degradation/Circuit Breaker | Michael Nygard’s stability patterns — does your system fail gracefully with fallbacks and timeout budgets, or does one failure cascade everywhere? | `22-graceful-degradation.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don’t accumulate a findings list. Fix each framework’s criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code + runtime** — code audits miss runtime behavior. Always check actual responses, headers, and query plans when possible.
- **Multi-round** — after all 22 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don’t re-report known issues.
