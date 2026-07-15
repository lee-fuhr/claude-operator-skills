---
name: qq-audit-seo
description: Serialized SEO audit using 15 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 3.0.0
author: Lee Fuhr
triggers:
  - "seo audit"
  - "search audit"
  - "seo review"
  - "technical seo"
  - "search optimization"
  - "run seo audit"
---

# Audit SEO with expert personas

Run a full serial SEO audit using 15 deep expert persona frameworks, fixing critical issues and verifying each framework before proceeding to the next.

15 SEO frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

Expert lens: Can people find it? Would a search specialist approve?

Supersedes: ad-hoc SEO checklists, one-off Lighthouse audits.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-seo`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-seo structured data`, "just run meta tags on the blog", "check page speed on the homepage", etc.

Match the framework name fuzzily — "schema", "rich snippets", "json-ld" should all match Structured Data/schema.org. "speed", "core web vitals", "cwv", "lcp" should all match Page Speed Ranking Impact. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Tech stack:** [framework, rendering strategy — SSR/SSG/SPA from project]
> - **Target audience:** [who needs to find this via search]
> - **Known SEO concerns:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full site / specific pages / specific content type]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can’t tell whether it’s SSR or client-rendered, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product’s key pages, routing config, and head/meta components to understand scope
3. Map the site structure: pages, content types, navigation hierarchy

### Phase 2: Serial framework execution

For each framework (in order 1-15):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-seo/frameworks/[NN-name].md`"
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
1. Run framework #15 (Link Equity and Authority Flow) as the final strategic review
2. Compile consolidated report:
   - Overall SEO health score
   - Per-framework scores
   - All findings grouped by severity (critical / high / medium / low)
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project’s data directory:
- `data/audit-seo-[date].md` — full report
- `data/audit-seo-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Technical SEO Fundamentals | Crawlability, indexability, canonical URLs, and sitemap — can search engines actually find, access, and understand your pages? | `01-technical-seo.md` |
| 2 | Structured Data/schema.org | Rich snippets markup — are you giving search engines machine-readable context that earns enhanced SERP features? | `02-structured-data.md` |
| 3 | Meta Tag Completeness | Unique title tags and meta descriptions — does every page tell search engines (and users) exactly what it’s about in the SERP? | `03-meta-tags.md` |
| 4 | URL Structure and Hierarchy | Clean, hierarchical, human-readable, stable — do your URLs communicate site structure and remain permanent? | `04-url-structure.md` |
| 5 | Internal Linking Architecture | Important pages within 3 clicks, equity flowing downward — does your internal link structure match your business priorities? | `05-internal-linking.md` |
| 6 | Mobile-First Indexing | Mobile version has all content and structured data — does Google see the same site on mobile that users see on desktop? | `06-mobile-first.md` |
| 7 | Page Speed Ranking Impact | Core Web Vitals as ranking signals — are your LCP, INP, and CLS scores helping or hurting your search visibility? | `07-page-speed-ranking.md` |
| 8 | Duplicate Content Management | Canonical tags and hreflang — are you telling search engines which version of each page is authoritative? | `08-duplicate-content.md` |
| 9 | Crawl Budget Optimization | No crawl waste on low-value pages — is Googlebot spending its limited budget on the pages that matter? | `09-crawl-budget.md` |
| 10 | Image SEO | Alt text, filenames, captions, and speed — are your images discoverable by search engines and contributing to page relevance? | `10-image-seo.md` |
| 11 | Social Sharing / OG/Twitter Cards | Attractive link previews — when someone shares your URL, does it look intentional and compelling or auto-generated and broken? | `11-social-sharing.md` |
| 12 | International SEO (hreflang) | Multi-language/region signals — are search engines showing the right version of your pages to users in the right countries? | `12-international-seo.md` |
| 13 | JavaScript Rendering for SEO | SSR/SSG for search engines — can Google see the same content that users see when JavaScript is required to render the page? | `13-js-rendering-seo.md` |
| 14 | Redirect Chain Audit | Single-hop, correct codes, no loops — are your redirects clean, direct, and preserving link equity? | `14-redirect-chains.md` |
| 15 | Link Equity and Authority Flow | Nofollow where appropriate, equity to commercial pages — is your link authority flowing toward the pages that generate revenue? | `15-link-authority.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don’t accumulate a findings list. Fix each framework’s criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code + rendered output** — code audits miss runtime rendering. Always check actual HTML served to crawlers when possible.
- **Multi-round** — after all 15 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don’t re-report known issues.
