---
name: qq-audit-performance
description: Serialized performance audit using 22 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 1.0.0
author: Lee Fuhr
triggers:
  - "performance audit"
  - "speed audit"
  - "web performance review"
  - "perf audit"
  - "lighthouse audit"
  - "run performance frameworks"
  - "run perf audit"
---

# Audit performance with expert personas

Audit performance by running 22 expert personas in serial, fixing critical issues per framework before verifying.

22 performance frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a performance engineer with 20 years of specialization in that specific domain.

Expert lens: **Is it fast? Would a performance engineer approve?**

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-performance`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-performance core web vitals`, "just run lighthouse on the homepage", "caching on the API routes", etc.

Match the framework name fuzzily — "cwv", "web vitals", "vitals" should all match Core Web Vitals. "lighthouse", "lh" should match Lighthouse Performance Audit. "images", "image opt" should match Image Optimization Pipeline. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Hosting:** [Vercel/AWS/self-hosted — inferred from config files]
> - **Performance baseline:** [from previous audits, Lighthouse scores, or conversation]
> - **Known pain points:** [what the user has mentioned — slow pages, large bundles, API latency]
> - **Scope:** [full app / specific routes / specific infrastructure layer]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can't tell whether it's SSR or SPA, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product's key config files (next.config, vercel.json, package.json) to understand deployment
3. Run `npx next build` or equivalent to establish baseline build metrics

### Phase 2: Serial framework execution

For each framework (in order 1-22):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-performance/frameworks/[NN-name].md`"
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
1. Run framework #22 (Resource Prioritization) as the final optimization check
2. Compile consolidated report:
   - Per-framework scores (1-10 each)
   - Overall weighted average
   - All findings grouped by severity
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project's data directory:
- `data/audit-performance-[date].md` — full report
- `data/audit-performance-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Core Web Vitals | LCP, INP, and CLS — are the three user-centric metrics that Google measures all within passing thresholds? | `01-core-web-vitals.md` |
| 2 | Lighthouse Performance Audit | Composite scoring with optimization recommendations — does the site pass Google's automated performance audit? | `02-lighthouse.md` |
| 3 | Critical Rendering Path | Initial render not blocked by unnecessary resources — does the browser paint meaningful content as fast as physics allows? | `03-critical-rendering-path.md` |
| 4 | Image Optimization Pipeline | Modern formats, responsive srcsets, lazy loading, and CDN delivery — are images as light and fast as they can be? | `04-image-optimization.md` |
| 5 | Font Loading Strategy | No FOIT or FOUT, font-display controlled, subsetted — do web fonts load without disrupting the user experience? | `05-font-loading.md` |
| 6 | JavaScript Execution Cost | Parse, compile, and execute time within budget — is JavaScript costing more main-thread time than the experience justifies? | `06-js-execution-cost.md` |
| 7 | Network Waterfall Analysis | Requests parallelized and critical resources prioritized — is the browser downloading what it needs in the right order? | `07-network-waterfall.md` |
| 8 | Third-Party Script Impact | Analytics, ads, and widgets loaded async with bounded cost — are third-party scripts degrading your performance? | `08-third-party-scripts.md` |
| 9 | Caching Effectiveness | Appropriate cache lifetimes, immutable hashes, and CDN hit rates — is the browser reusing resources instead of re-downloading them? | `09-caching-effectiveness.md` |
| 10 | Server Response Time (TTFB) | Server responds within 200ms for HTML — is the time-to-first-byte fast enough that everything downstream has a chance? | `10-server-response-time.md` |
| 11 | Database Query Performance | Queries within budget, no N+1, proper indexes — is the database a performance asset or a hidden bottleneck? | `11-database-query-perf.md` |
| 12 | Memory Performance | Stable footprint, no leaks, GC pauses within budget — is the application using memory efficiently without degrading over time? | `12-memory-performance.md` |
| 13 | Animation Frame Budget | Animations maintain the 16ms frame budget at 60fps — do visual transitions and motion feel smooth or janky? | `13-animation-frame-budget.md` |
| 14 | Prefetching and Preloading Strategy | Resource hints for likely-needed resources — is the browser getting a head start on resources the user will need next? | `14-prefetching-strategy.md` |
| 15 | Service Worker and Offline Strategy | Appropriate caching strategies and offline capability — does the Service Worker enhance performance without creating staleness problems? | `15-service-worker.md` |
| 16 | Compression Audit | Text assets served with Brotli compression — are responses as small as they can be over the wire? | `16-compression.md` |
| 17 | Layout Thrashing and Forced Reflow | No unnecessary style recalculations — is JavaScript triggering expensive forced reflows by interleaving reads and writes? | `17-layout-thrashing.md` |
| 18 | Lazy Loading and Virtualization | Off-screen content deferred and long lists virtualized — is the page only doing work for what the user can see? | `18-lazy-loading-virtualization.md` |
| 19 | Edge/CDN Delivery | Assets served from geographically close nodes — is the delivery infrastructure minimizing the physical distance between server and user? | `19-edge-cdn.md` |
| 20 | Performance Budget Enforcement | Defined budgets with CI enforcement — are there guardrails that prevent performance from degrading over time? | `20-performance-budget.md` |
| 21 | Real User Monitoring vs Synthetic | Performance measured from real users, not just lab conditions — do you know what your actual users experience? | `21-rum-vs-synthetic.md` |
| 22 | Resource Prioritization | Browser loading order matches application priority — does the most important content get bandwidth and processing first? | `22-resource-prioritization.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don't accumulate a findings list. Fix each framework's criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Measure, don't guess** — performance claims require numbers. Run builds, check sizes, time responses.
- **Multi-round** — after all 22 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don't re-report known issues.
