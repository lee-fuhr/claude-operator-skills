---
name: qq-audit-copy
description: Serialized content/copy audit using 22 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 1.0.0
author: Lee Fuhr
triggers:
  - "copy audit"
  - "content audit"
  - "copy review"
  - "microcopy review"
  - "content quality audit"
  - "run copy audit"
  - "editorial review"
---

# Audit copy with expert personas

Audit copy by running 22 expert personas in serial, fixing critical issues per framework before verifying.

22 content and copy frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

The expert lens: **Is the writing good? Would an editor approve?** Every framework asks whether the copy is doing its job — informing, guiding, persuading, or reassuring — without wasting the reader's time or trust.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-copy`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-copy voice tone`, "just run microcopy on the settings page", "error messages on the form", etc.

Match the framework name fuzzily — "voice", "tone", "voice consistency" should all match Voice and Tone Consistency. "errors", "error msgs", "error messages" should all match Error Message Helpfulness. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Audience:** [who reads this copy — inferred from product type]
> - **Voice/brand docs:** [existing style guide, voice bank, or none detected]
> - **Known copy pain points:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full app / specific pages / specific component / marketing site]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can't tell whether this is a consumer app or B2B enterprise tool, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product's key pages/components to understand scope
3. Identify any existing voice/style documentation

### Phase 2: Serial framework execution

For each framework (in order 1-22):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-copy/frameworks/[NN-name].md`"
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
1. Run framework #22 (Localization Readiness) as the final forward-looking evaluation
2. Compile consolidated report:
   - Overall copy quality score (average across frameworks)
   - Per-framework scores
   - All findings grouped by severity
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project's data directory:
- `data/audit-copy-[date].md` — full report
- `data/audit-copy-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Readability Scoring | Reading level calibration — does the complexity of the language match the capacity and patience of the audience? | `01-readability-scoring.md` |
| 2 | Voice and Tone Consistency | Brand coherence — does the writing sound like one person across every screen, state, and context? | `02-voice-tone-consistency.md` |
| 3 | Microcopy Quality | The invisible text — are button labels, tooltips, placeholders, and inline help doing the work of a good concierge? | `03-microcopy-quality.md` |
| 4 | Error Message Helpfulness | Recovery language — do error messages explain what happened, why it happened, and what to do now? | `04-error-message-design.md` |
| 5 | CTA Clarity and Hierarchy | Conversion architecture — are calls to action clear, differentiated, verb-first, and visually ranked by importance? | `05-cta-hierarchy.md` |
| 6 | Empty State Copy | First-impression content design — do empty states guide users toward their first action or just confirm that nothing exists? | `06-empty-state-copy.md` |
| 7 | Onboarding Copy Progression | Progressive instructional design — does copy teach users up front and then get out of the way, or does it treat experts like beginners forever? | `07-onboarding-copy.md` |
| 8 | Terminology Consistency | Lexical coherence — does the same concept use the same word everywhere, or does the product speak three dialects at once? | `08-terminology-consistency.md` |
| 9 | Scanning / Scanability | Content structure for rapid comprehension — is the copy structured so users who scan instead of read still get the message? | `09-scanability.md` |
| 10 | Inclusive Language | Language equity and representation — does the copy avoid ableist, gendered, culturally biased, or exclusionary terms? | `10-inclusive-language.md` |
| 11 | Legal/Compliance Copy | Whether privacy policies, terms, cookie notices, and compliance copy are comprehensible to the humans they're supposed to protect. | `11-legal-compliance-copy.md` |
| 12 | Notification/Email Copy | Whether system-generated messages — transactional emails, push notifications, in-app alerts — are useful, branded, and clear. | `12-notification-copy.md` |
| 13 | Help/Documentation Completeness | Whether the documentation system serves all four Diataxis modes — tutorials, how-to guides, reference, explanation. | `13-help-documentation.md` |
| 14 | SEO Content Fundamentals | Whether page titles, meta descriptions, headings, and body content are discoverable without sacrificing readability. | `14-seo-content.md` |
| 15 | Content Hierarchy / Information Scent | Whether users can predict what they'll find before clicking — whether labels, links, and headings accurately signal what's behind them. | `15-information-scent.md` |
| 16 | Conversational UI Copy | Chatbot and AI dialog writing — does the interface talk like a competent human or a confused script? | `16-conversational-ui-copy.md` |
| 17 | Confirmation/Success Messages | Success and confirmation states — does the system tell users what happened, what's next, and what to do now? | `17-confirmation-copy.md` |
| 18 | Placeholder/Instructional Text | Form placeholders and helper text — does the input guidance clarify expectations without creating new problems? | `18-placeholder-text.md` |
| 19 | Loading State Copy | Loading and wait state messaging — does the system turn dead time into informed time? | `19-loading-state-copy.md` |
| 20 | Truncation and Overflow | Content engineering for variable-length text — does long content degrade gracefully or destroy the layout? | `20-truncation-overflow.md` |
| 21 | Content Freshness and Accuracy | Content governance and temporal integrity — are dates, numbers, screenshots, and referenced features still true? | `21-content-freshness.md` |
| 22 | Localization Readiness | i18n content strategy — will this copy survive translation into 30 languages without breaking meaning, layout, or trust? | `22-localization-readiness.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don't accumulate a findings list. Fix each framework's criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from editorial principles, not rules.
- **Voice consistency across screens** — the most common copy failure is not bad writing on any one screen, it's different writing on every screen. Voice/tone should feel like one author.
- **Microcopy over macrocopy** — button labels, error messages, tooltips, empty states, and placeholders do more work than any paragraph of body copy. Audit the small text hardest.
- **The reader never reads** — 79% scan. Copy must work for scanners first and readers second. Headings, labels, and first sentences carry the entire load.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code + rendered output** — code audits miss how copy actually reads in context. Always audit rendered output when possible.
- **Multi-round** — after all 22 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don't re-report known issues.
- **Would an editor approve?** — the ultimate test for every piece of copy. Not "is it technically correct" but "is it good writing that serves the reader."
