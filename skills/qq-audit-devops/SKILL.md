---
name: qq-audit-devops
description: Serialized DevOps audit using 15 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 3.0.0
author: Lee Fuhr
triggers:
  - "devops audit"
  - "infrastructure audit"
  - "deployment audit"
  - "ops review"
  - "12 factor"
  - "run devops audit"
---

# Audit DevOps with expert personas

Audit DevOps by running 15 expert personas in serial, fixing critical issues per framework before verifying.

15 DevOps frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

Expert lens: Is it deployable, operable, and resilient?

Supersedes: ad-hoc infrastructure reviews, one-off uptime checks.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-devops`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-devops 12-factor`, "just run monitoring on the production stack", "check CI/CD pipeline", etc.

Match the framework name fuzzily — "12 factor", "twelve factor", "12factor" should all match 12-Factor App. "ci", "cicd", "pipeline", "github actions" should all match CI/CD Pipeline Maturity. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Hosting:** [Vercel / AWS / GCP / self-hosted — inferred from project]
> - **CI/CD:** [GitHub Actions / CircleCI / none — inferred from config files]
> - **Known ops concerns:** [what the user has mentioned or what recent incidents suggest]
> - **Scope:** [full infrastructure / specific service / specific pipeline]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can’t tell what the hosting platform is, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product’s deployment config, CI/CD pipelines, and infrastructure definitions to understand scope
3. Map the operational surface: hosting, databases, caches, queues, scheduled jobs, external services

### Phase 2: Serial framework execution

For each framework (in order 1-15):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-devops/frameworks/[NN-name].md`"
   - "You ARE the expert described in that document. Think like them, not like a generalist."
   - "Audit [product name] focusing on [scope]. Context: [interview output]"
   - "Previous frameworks found these issues: [cumulative findings list]. Do NOT re-report duplicates."
   - "Score 1-10, list findings with file:line references, fix critical issues (score < 7), write report."

2. **Collect the agent’s output:**
   - Score for this framework
   - Findings (new, not duplicates)
   - Fixes applied
   - Items flagged for downstream frameworks

3. **Verify build** if fixes were applied (rebuild container, re-run pipeline, etc.)

4. **Update cumulative state:**
   - Add findings to the dedup list
   - Update the running score card
   - Note cross-framework flags for upcoming frameworks

5. **Move to next framework**

### Phase 3: Synthesis
1. Run framework #15 (Dependency Update Cadence) as the final maintenance review
2. Compile consolidated report:
   - Overall operational readiness score
   - Per-framework scores
   - All findings grouped by severity (critical / high / medium / low)
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project’s data directory:
- `data/audit-devops-[date].md` — full report
- `data/audit-devops-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | 12-Factor App | Application architecture fundamentals — does this app follow the patterns that make deployment, scaling, and maintenance predictable? | `01-twelve-factor.md` |
| 2 | Infrastructure as Code | Infrastructure reproducibility — is every piece of infrastructure version-controlled, reviewable, and rebuildable from scratch? | `02-iac-audit.md` |
| 3 | CI/CD Pipeline Maturity | Deployment pipeline health — are you shipping frequently, reliably, and with confidence that nothing is broken? | `03-cicd-maturity.md` |
| 4 | Deployment Strategy | Release mechanics — can you ship to production with zero downtime, instant rollback, and controlled blast radius? | `04-deployment-strategy.md` |
| 5 | Monitoring and Alerting Coverage | Operational visibility — do you know when something is broken before your users tell you, and does the alert tell you what to do about it? | `05-monitoring-alerting.md` |
| 6 | Incident Response Readiness | Incident management — when production breaks at 3 AM, does the team know who responds, what to do, and how to communicate? | `06-incident-response.md` |
| 7 | Backup and Disaster Recovery | Data protection and recovery — if you lost everything right now, how long until you’re back, and how much data is gone? | `07-backup-disaster-recovery.md` |
| 8 | Log Aggregation and Search | Centralized logging — can you find the needle in the haystack when debugging a production issue at 3 AM? | `08-log-aggregation.md` |
| 9 | Container/Runtime Health | Container hygiene — are your containers minimal, secure, health-checked, and resource-bounded? | `09-container-health.md` |
| 10 | Secret Rotation and Management | Credential hygiene — can you rotate every secret in your system without downtime or redeployment? | `10-secret-rotation.md` |
| 11 | Cost Optimization/Resource Efficiency | Cloud spend hygiene — are resources right-sized, unused resources cleaned up, and cost allocation visible to the teams that control it? | `11-cost-optimization.md` |
| 12 | Observability Depth | Diagnostic capability — when something breaks, can you answer "why?" from your telemetry alone, without guessing or adding instrumentation? | `12-observability-depth.md` |
| 13 | DNS and Domain Management | Name resolution reliability — are your DNS records correct, redundant, monitored, and managed as code? | `13-dns-management.md` |
| 14 | SSL/TLS Configuration | Transport security — are connections encrypted with modern protocols, valid certificates, and secure defaults? | `14-tls-configuration.md` |
| 15 | Dependency Update Cadence | Dependency freshness — are third-party libraries kept current, vulnerabilities patched promptly, and update costs kept low through regular small increments? | `15-dependency-update-cadence.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don’t accumulate a findings list. Fix each framework’s criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Config + runtime** — config audits miss runtime behavior. Always check actual deployed state, running processes, and live metrics when possible.
- **Multi-round** — after all 15 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don’t re-report known issues.
