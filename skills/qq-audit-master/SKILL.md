---
name: qq-audit-master
description: Meta-orchestrator that selects and sequences the right combination of audit domains based on project context, conversation state, and user intent. Routes to 13 domain-specific audit skills containing 255 expert-persona frameworks.
version: 2.0.0
author: Lee Fuhr
triggers:
  - "full audit"
  - "audit everything"
  - "quality audit"
  - "what should I audit"
  - "run audits"
  - "comprehensive audit"
---

# Run the full audit suite

Route to 13 domain-specific audit skills intelligently based on project needs and sequence them.

Routes to 13 domain-specific audit skills (255 total expert-persona frameworks) based on what the project needs. Knows which domains matter for which kinds of work and sequences them intelligently.

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

For domains requiring screenshots: if agent-browser is available, capture screenshots at the start of each domain audit. If not, instruct the framework agents to read the rendered component code and reason about visual output.

---

## Convergence protocol

**Each domain runs a convergence loop — not a single pass.**

```
Round 1: Run all frameworks → Score → Fix criticals
Round 2: Re-run all frameworks → Score → Fix remaining
Round 3: Re-run all frameworks → Final score
```

**Convergence target:** Configurable via smart interview (see below). Default 9.5/10. Internal tools typically 9+, client projects with buy-in 7-8.

**Convergence rules:**
- **Move on when:** Domain score reaches target, OR round 3 is complete (whichever comes first)
- **Max 3 rounds per domain** to prevent infinite loops — if round 3 doesn't hit target, remaining issues are likely product decisions, not audit findings
- **Between rounds:** Fix all critical findings (score < 7) before re-running. Don't accumulate debt.
- **Dedup across rounds:** Each round receives the previous round's findings to avoid re-reporting fixed issues.
- **Report the trajectory:** "UX: Round 1 = 7.2, Round 2 = 8.8, Round 3 = 9.6 ✓ — moving to Visual"

**Why convergence matters:** A single pass finds ~60% of issues. Round 2 finds 25% more (because fixes from round 1 expose new issues or fix old ones). Round 3 catches the last 10-15%. Diminishing returns after round 3 — remaining gaps are architectural.

**Between domains:** After a domain converges, brief the user: "UX converged at 9.6 after 2 rounds (35 fixes). Ready for Visual?" Always pause for direction before starting the next domain.

---

## Execution flow

For each selected domain (in order):

1. **Invoke the domain's slash command** — e.g., run `/qq-audit-ux` with any scope constraints
2. **The domain orchestrator handles everything** — smart interview, serial framework execution, fixes, report
3. **Collect the domain's output** — SUS score (for UX), overall assessment, critical findings
4. **Brief the user on results** — "UX scored 82. 3 critical findings fixed, 5 remaining. Moving to Visual."
5. **Proceed to next domain**

Between domains, ask: "Ready for [next domain]? Or adjust the plan?"

---

## Smart interview (master level)

Before selecting domains, gather context the same way domain orchestrators do — but at the project level:

1. What kind of project is this? (infer from files/conversation)
2. What stage is it at? (prototype, feature-complete, pre-launch, live)
3. What's the quality bar? (internal tool, client deliverable, public product)
4. Any specific concerns? (from conversation — "the forms feel broken", "worried about mobile")
5. What's already been audited? (check for existing audit reports)
6. **What's the target score?** (ALWAYS ask via AskUserQuestion)
   - 9+ (internal tool, chase perfection)
   - 8 (client project, good buy-in)
   - 7 (client project, conservative — don't risk changing things they like)
   - This cascades to all domain audits as the convergence target.

Pre-fill everything possible. Only ask about genuine gaps. The target score question is ALWAYS asked — never inferred.

---

## Live Notion dashboard

**At the start of every audit run, create a Notion page in your own deliverables/tracking database** — set its data source ID in your project config rather than hardcoding one here.

**Properties:**
- Title: "Audit: [Product name] — [date]"
- Client: [if applicable]
- Type: "Audit"
- Status: "In progress" → "Complete" when done
- Session: current session name

**Page structure (update live as the audit progresses):**

### Overview section (top of page)

A domain status table showing the full audit at a glance:

```
| Phase      | Domain     | Score | Target | Rounds | Status |
|------------|------------|-------|--------|--------|--------|
| Strategy   | Product    | 9.2   | 9.5    | 2/3    | 🔄     |
| UX         | UX         | —     | 9.5    | 0/3    | ⏳     |
| Design     | Visual     | —     | 9.5    | 0/3    | ⏳     |
| Content    | Copy       | —     | 9.5    | 0/3    | ⏳     |
| Build      | Frontend   | —     | 9.5    | 0/3    | ⏳     |
...
```

Status emoji: ⏳ pending, 🔄 in progress, ✅ converged, ⚠️ hit max rounds, ⏭️ skipped

### Per-domain sections (one per active domain)

Each domain gets a toggle heading that expands to show:

1. **Score trajectory:** "Round 1: 7.2 → Round 2: 8.8 → Round 3: 9.6 ✅"
2. **Framework scores table:**
   ```
   | # | Framework           | Score | Findings | Fixes | Remaining |
   |---|---------------------|-------|----------|-------|-----------|
   | 1 | Nielsen's heuristics | 9/10  | 3        | 3     | 0         |
   | 2 | Gestalt principles   | 8/10  | 5        | 4     | 1         |
   ...
   ```
3. **Critical findings** (score < 7) with file:line references
4. **Fixes applied** this round
5. **Items deferred** (minor, not blocking convergence)

### Live feed (reverse-chron, below the overview table)

A running log of the spiciest takeaways as each framework completes. Newest at top. This is NOT a dry findings list — it's the "holy shit" moments, the surprising discoveries, the patterns that change how you think about the product.

**Format — one entry per framework:**

```
**14:32 — Fitts's Law (UX, Round 2)** ⬆️ 6→9
Delete button is 12px from Save on mobile. Users WILL fat-finger this.
Fixed: moved Delete to overflow menu, Save now full-width.
→ 3 fixes applied, 0 remaining
```

**What makes a good entry:**
- Lead with the finding that would make the user say "oh shit" or "I never thought of that"
- One sentence, sharp — not a report summary
- Include the score change (⬆️ old→new) so the trajectory is visible
- If nothing surprising, still note the most impactful fix
- Skip the bureaucratic language — this is a live commentary, not an audit report

**What to skip:**
- Findings that are just "this is fine, no issues" — only log frameworks that found something
- Generic descriptions ("several usability issues were identified")
- Anything the user would skim past

### Exec summary section (very top of page, before overview table)

**MANDATORY** — 3-5 sentences, no jargon. What was audited, current score, biggest problem, improvement from last audit. Updated after each domain converges with a cumulative view.

### Per-domain exec summaries

After each domain completes, add a 1-2 sentence summary at the top of that domain's toggle section. Lead with the score and the single most important finding. No framework names — just plain language.

### Findings summary section (bottom, populated after all domains converge)

After all domains converge:
- Total findings across all domains
- Total fixes applied
- Remaining items by severity
- Overall quality verdict

**Update frequency:** Update the Notion doc after EVERY framework completes (not just per domain). This gives the user real-time visibility into progress. Use the Notion MCP tools to update.

**Comments:** The user may leave comments on the Notion page. Before starting a new domain, check for comments via `include_all_blocks: true` and incorporate feedback into the next domain's approach.

---

## Usage tracking

After each domain audit completes, append a log line to `~/.agents/skills/qq-audit-master/usage.jsonl`:

```json
{"timestamp": "ISO-8601", "domain": "ux", "product": "example-product", "frameworks_run": 20, "findings": 12, "fixes": 8, "score": 85, "duration_min": 45}
```

This builds the data to answer: which domains find the most issues? Which frameworks are most productive? Where is quality improving over time?

---

## Domain interdependencies and sequencing

Domains are NOT independent. Findings in one domain directly influence what matters in others. The default lifecycle order (Product → UX → Visual → Copy → Frontend → Backend) can be overridden when interdependencies matter more.

**Key interdependencies:**
- **Copy ↔ Visual** — Copy hierarchy needs visual support (type weight, whitespace). Visual decisions depend on copy length and density. Run these as a pair with a revisit pass.
- **UX → Copy** — Voice/tone direction (e.g., "playful warmth") must be established in UX before copy can be evaluated for consistency.
- **Copy + Visual → Frontend** — Frontend implements both. Code quality of copy/visual changes should be caught in frontend pass.
- **Frontend ↔ Backend** — API contracts matter to both. God files on frontend may mirror god routes on backend. Fix frontend first (closer to user), then backend.
- **UX delight → Visual → Copy** — Celebration animations (UX) need visual polish (Visual) and personality copy (Copy). These three form a "delight triangle."

**Recommended sequences by project type:**
- **Internal tool (a common preference):** Copy → Visual → revisit Copy → Frontend (with back-and-forth) → Backend
- **Client project:** UX → Copy → Visual → Frontend → Backend (standard lifecycle)
- **Marketing site:** Copy → Visual → SEO → Performance (content-led)

## Key principles

- **Product before polish** — don’t optimize the wrong thing. Validate product decisions first.
- **User-facing before engineering** — fix what users see before fixing what only engineers see.
- **Fix between domains** — each domain’s critical issues get fixed before the next domain starts.
- **No redundant work** — if UX #13 (WCAG) already ran, skip accessibility checks in other domains.
- **Cumulative context** — each domain receives findings from previous domains to avoid re-reporting.
- **The user stays in control** — always present the plan, always pause between domains, always let the user adjust.
