---
name: qq-audit-master
description: Meta-orchestrator that selects and sequences the right combination of audit domains based on project context, conversation state, and user intent. Routes to 13 domain-specific audit skills containing 255 expert-persona frameworks.
version: 2.0.0
triggers:
  - "full audit"
  - "audit everything"
  - "quality audit"
  - "what should I audit"
  - "run audits"
  - "comprehensive audit"
---

# Master audit orchestrator

Routes to 13 domain-specific audit skills (255 total expert-persona frameworks) based on what the project needs. Knows which domains matter for which kinds of work and sequences them intelligently.

**Requires:** Domain sub-skills from [audit-framework](https://github.com/lee-fuhr/audit-framework) installed alongside this skill.

---

## Modes

### Mode 1: Smart routing (no args or general request)

Triggers: `/qq-audit`, "audit this", "what should I audit", "full audit", etc.

**Analyze the project context and recommend a tailored audit plan:**

1. **Identify the project type** from conversation context, files, and CLAUDE.md:
   - Marketing/brochure site → Visual, Copy, SEO, Performance, Accessibility (via UX #13)
   - SaaS/web app → UX, Product, Visual, Frontend, Performance, Security
   - API/backend service → Backend, Security, Testing, DevOps
   - Internal tool → UX, Product, Frontend, Testing
   - E-commerce → UX, Product, Visual, Performance, SEO, Security, Compliance
   - AI/chatbot → UX, Copy (#16 conversational UI), Product, Frontend

2. **Check what's already been audited** — look for `data/audit-*` reports in the project. Don't re-run domains that were audited recently unless explicitly asked.

3. **Present the recommendation:**

   > "Based on [project type], I'd recommend these audits in this order:
   >
   > 1. **Product** (20 frameworks) — verify the product is right before polishing
   > 2. **UX** (20 frameworks) — then make sure humans can use it
   > 3. **Visual** (22 frameworks) — then make it look professional
   > 4. **Copy** (22 frameworks) — then audit the writing
   > 5. **Frontend** (22 frameworks) — then verify code quality
   >
   > Skip: Backend, DevOps, Compliance (not applicable here)
   >
   > Run all 5? Or pick specific ones?"

4. **Use AskUserQuestion** with the recommended domains as options (multiSelect).

### Mode 2: Specific domains (domain names as args)

Triggers: `/qq-audit ux + copy`, "audit product and visual", "run ux then frontend", etc.

Parse the domain names from args (fuzzy match), sequence them in the recommended order, and execute each by invoking its `/qq-audit-[domain]` skill.

### Mode 3: Preset combos (named profiles)

Triggers: `/qq-audit pre-launch`, `/qq-audit quick`, etc.

| Profile | Domains | When to use |
|---------|---------|-------------|
| **quick** | UX, Visual, Copy | Fast quality check — appearance and usability |
| **pre-launch** | Product, UX, Visual, Copy, Frontend, Performance, Security, SEO | Before going live |
| **post-build** | UX, Visual, Copy, Frontend | After completing a feature build |
| **deep** | All 13 domains | Comprehensive quality audit |
| **code** | Frontend, Backend, Testing, Security, DevOps | Engineering quality |
| **user-facing** | UX, Product, Visual, Copy, Performance | Everything the user touches |
| **marketing** | Copy, Visual, SEO, Performance | Marketing site quality |

### Mode 4: List all domains

Triggers: "list", "what domains", "show me everything", "help", etc.

Show the domain inventory table below.

---

## Domain inventory

| # | Domain | Command | Frameworks | Expert lens |
|---|--------|---------|-----------|-------------|
| 1 | UX | `/qq-audit-ux` | 20 | Does the brain work well with this? |
| 2 | Product | `/qq-audit-product` | 20 | Is this the right product? |
| 3 | Visual UI | `/qq-audit-visual` | 22 | Does this look professional? |
| 4 | Content/Copy | `/qq-audit-copy` | 22 | Is the writing good? |
| 5 | Frontend | `/qq-audit-frontend` | 22 | Is the code well-built? |
| 6 | Performance | `/qq-audit-performance` | 22 | Is it fast? |
| 7 | Security | `/qq-audit-security` | 23 | Is it safe? |
| 8 | QA/Testing | `/qq-audit-testing` | 22 | Is it tested? |
| 9 | Backend/API | `/qq-audit-backend` | 22 | Is the server-side solid? |
| 10 | SEO | `/qq-audit-seo` | 15 | Can people find it? |
| 11 | DevOps | `/qq-audit-devops` | 15 | Is it deployable and resilient? |
| 12 | Data Quality | `/qq-audit-data` | 15 | Is the data trustworthy? |
| 13 | Compliance | `/qq-audit-compliance` | 15 | Is it legally sound? |
| | **Total** | | **255** | |

---

## Build lifecycle sequencing

Domains are sequenced by the agency build lifecycle. Each phase depends on the previous being stable — auditing visual design when UX is broken wastes time because you'll redesign screens after UX fixes.

| Phase | Domain | Input | Why this order |
|-------|--------|-------|---------------|
| **Strategy** | Product | Screenshots | Is this even the right thing? Fix before building more. |
| **UX** | UX | Code + screenshots | Can humans use it? Fix before making it pretty. |
| **Design** | Visual | Screenshots (+ CSS) | Does it look professional? Fix before copy audit — copy lives in visual context. |
| **Content** | Copy | Code + screenshots | Are the words right? Fix after visual context is settled. |
| **Build** | Frontend | Code only | Is the client code well-built? |
| **Build** | Backend | Code only | Is the server code solid? |
| **Optimize** | Performance | Code + browser | Is it fast? Measure after code is clean. |
| **Harden** | Security | Code only | Is it safe? |
| **Verify** | Testing | Code only | Is it tested? |
| **Launch** | SEO | Code + rendered output | Can people find it? |
| **Ship** | DevOps | Code/config | Is it deployable? |
| **Measure** | Data | Code + dashboards | Is analytics working? |
| **Protect** | Compliance | Code + UI | Is it legally sound? |

**The rule:** Each domain converges before the next begins. Don't audit downstream until upstream is stable.

**Input types:**
- **Code only:** Read source files. Used for engineering-quality domains.
- **Screenshots:** Use agent-browser to capture rendered output. Used for visual/product domains.
- **Code + screenshots/browser:** Both. Most thorough — code reveals WHY, screenshots reveal WHAT the user actually sees.

---

## Convergence protocol

**Each domain runs a convergence loop — not a single pass.**

```
Round 1: Run all frameworks → Score → Fix criticals
Round 2: Re-run all frameworks → Score → Fix remaining
Round 3: Re-run all frameworks → Final score
```

**Convergence target:** 9.5/10 per domain (configurable via smart interview).

**Convergence rules:**
- **Move on when:** Domain score reaches target, OR round 3 is complete (whichever comes first)
- **Max 3 rounds per domain** to prevent infinite loops — if round 3 doesn't hit target, remaining issues are likely product decisions, not audit findings
- **Between rounds:** Fix all critical findings (score < 7) before re-running. Don't accumulate debt.
- **Dedup across rounds:** Each round receives the previous round's findings to avoid re-reporting fixed issues.
- **Report the trajectory:** "UX: Round 1 = 7.2, Round 2 = 8.8, Round 3 = 9.6 ✓ — moving to Visual"

**Why convergence matters:** A single pass finds ~60% of issues. Round 2 finds 25% more (because fixes from round 1 expose new issues or fix old ones). Round 3 catches the last 10–15%. Diminishing returns after round 3 — remaining gaps are architectural.

**Between domains:** After a domain converges, brief the user: "UX converged at 9.6 after 2 rounds (35 fixes). Ready for Visual?" Always pause for direction before starting the next domain.

---

## Execution flow

For each selected domain (in order):

1. **Invoke the domain's slash command** — e.g., run `/qq-audit-ux` with any scope constraints
2. **The domain orchestrator handles everything** — smart interview, serial framework execution, fixes, report
3. **Collect the domain's output** — overall assessment, critical findings, score trajectory
4. **Brief the user on results** — "UX scored 82. 3 critical findings fixed, 5 remaining. Moving to Visual."
5. **Proceed to next domain**

Between domains, ask: "Ready for [next domain]? Or adjust the plan?"

---

## Smart interview (master level)

Before selecting domains, gather context — but pre-fill everything possible from the conversation. Only ask about genuine gaps:

1. What kind of project is this? (infer from files/conversation)
2. What stage is it at? (prototype, feature-complete, pre-launch, live)
3. What's the quality bar? (internal tool, client deliverable, public product)
4. Any specific concerns? (from conversation context)
5. What's already been audited? (check for existing audit reports)

---

## Optional: project tracking doc

If your workflow uses a project tracking system (Notion, Linear, etc.), create an audit progress doc at the start of each run. Update it after every framework completes — not just per domain.

**Useful to track per domain:**
- Score trajectory (Round 1 → Round 2 → Round 3)
- Framework scores with findings/fixes counts
- Critical findings with file:line references
- Live commentary: the findings that changed how you think about the product, not dry summaries

**Live feed format:**

```
14:32 — Fitts's Law (UX, Round 2) ⬆️ 6→9
Delete button is 12px from Save on mobile. Users WILL fat-finger this.
Fixed: moved Delete to overflow menu, Save now full-width.
→ 3 fixes applied, 0 remaining
```

Lead with the finding that would make you say "oh shit" — not a report summary.

---

## Key principles

- **Product before polish** — don't optimize the wrong thing. Validate product decisions first.
- **User-facing before engineering** — fix what users see before fixing what only engineers see.
- **Fix between domains** — each domain's critical issues get fixed before the next domain starts.
- **No redundant work** — if UX #13 (WCAG) already ran, skip accessibility checks in other domains.
- **Cumulative context** — each domain receives findings from previous domains to avoid re-reporting.
- **Stay in control** — always present the plan, always pause between domains, always let the user adjust.
