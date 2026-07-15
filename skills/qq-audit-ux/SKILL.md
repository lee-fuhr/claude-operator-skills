---
name: qq-audit-ux
description: Serialized UX audit using 20 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 3.0.0
author: Lee Fuhr
triggers:
  - "ux audit"
  - "usability audit"
  - "heuristic evaluation"
  - "ux framework review"
  - "sus score"
  - "run all frameworks"
  - "run ux audit"
---

# Audit UX with expert personas

Run a full serial UX audit using 20 deep expert persona frameworks, fixing critical issues and verifying each framework before proceeding to the next.

20 usability frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year specialist in that specific framework.

Supersedes: ux-framework-audit v2, deep-product-sweep v1, product-qa suite.

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-ux`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-ux Fitts's Law`, "just run gestalt on the sidebar", "nielsen's on the settings page", etc.

Match the framework name fuzzily — "fitts", "fitt's law", "target sizes" should all match Fitts's Law. "nielsen", "heuristics", "10 heuristics" should all match Nielsen's. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Platform:** [desktop/mobile/both — inferred from tech stack]
> - **Quality bar:** [SUS target — from previous audits or conversation]
> - **Known pain points:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full app / specific pages / specific component]
>
> Anything wrong or missing?"

**Always ask the target score** using AskUserQuestion:
- "What score are you targeting per heuristic?"
  - **9+ (internal tool, chase perfection)** — fix everything below target
  - **8 (client project, good buy-in)** — fix criticals, note the rest
  - **7 (client project, conservative)** — don't risk changing things they like
- The target determines which findings get fixed vs. noted. Only fix findings that bring a heuristic below the target.

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can't tell whether it's desktop-only or responsive, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product's key pages/components to understand scope
3. Take screenshots if browser agent is available

### Phase 2: Serial framework execution

For each framework (in order 1-20):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-ux/frameworks/[NN-name].md`"
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
1. Run framework #20 (SUS Scoring) as the final meta-evaluation
2. Compile consolidated report:
   - Overall SUS score
   - Per-framework scores
   - All findings grouped by severity
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report

**Exec summary is MANDATORY** — every report starts with a 3-5 sentence executive summary at the very top. No jargon, no framework names. Just: what was audited, what the score is, what the biggest problem is, and whether it improved from last time.

**Per-framework exec summaries too** — after each framework completes, present a 1-2 sentence summary before the detailed findings. Lead with the score change and the single most important finding.

Save to project's data directory:
- `data/audit-ux-[date].md` — full report (exec summary at top)
- `data/audit-ux-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Nielsen's 10 Heuristics | Broad usability sweep — visibility, consistency, error prevention, recognition, flexibility, minimalism | `01-nielsens-heuristics.md` |
| 2 | Gestalt Principles | Visual grouping — proximity, similarity, continuity, closure, figure-ground | `02-gestalt-principles.md` |
| 3 | Fitts's Law | Motor control — target sizes, distances, touch targets, click area geometry | `03-fitts-law.md` |
| 4 | Hick's Law | Decision complexity — option counts, defaults, progressive narrowing | `04-hicks-law.md` |
| 5 | Miller's Law | Working memory — chunking, information density, cross-screen recall | `05-millers-law.md` |
| 6 | Jakob's Law | Convention compliance — does this match patterns users already know? | `06-jakobs-law.md` |
| 7 | Aesthetic-Usability Effect | Polish and trust — beauty creates perceived usability (and can mask real problems) | `07-aesthetic-usability.md` |
| 8 | Von Restorff Effect | Visual salience — does the most important thing actually stand out? | `08-von-restorff.md` |
| 9 | Zeigarnik Effect | Progress and completion — open loops, progress indicators, completion feedback | `09-zeigarnik-effect.md` |
| 10 | Progressive Disclosure | Complexity management — what's visible vs. what's behind interaction | `10-progressive-disclosure.md` |
| 11 | Error Tolerance | Recovery and forgiveness — undo, confirmation, form data persistence | `11-error-tolerance.md` |
| 12 | Emotional Design | Feeling — visceral, behavioral, reflective (Don Norman's three levels) | `12-emotional-design.md` |
| 13 | WCAG 2.1 AA | Accessibility — perceivable, operable, understandable, robust | `13-wcag-accessibility.md` |
| 14 | Doherty Threshold | Response time — <400ms for flow, <100ms for instantaneous feel | `14-doherty-threshold.md` |
| 15 | Peak-End Rule | Memory — users judge by the peak moment and the ending | `15-peak-end-rule.md` |
| 16 | Tesler's Law | Complexity budget — who bears the irreducible complexity, user or system? | `16-teslers-law.md` |
| 17 | Cognitive Load Theory | Mental bandwidth — intrinsic, extraneous, germane load management | `17-cognitive-load-theory.md` |
| 18 | Serial Position Effect | Placement — primacy and recency, the forgotten middle | `18-serial-position-effect.md` |
| 19 | Goal-Gradient Effect | Momentum — progress visibility, acceleration near completion | `19-goal-gradient-effect.md` |
| 20 | SUS Scoring | Synthesis — 10-item usability scale, maps score to framework-specific diagnosis | `20-sus-scoring.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don't accumulate a findings list. Fix each framework's criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Does it prevent errors? Is the complexity earned?
- **Code + screenshots** — code audits miss visual issues. Always audit rendered output when possible.
- **Multi-round** — after all 20 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don't re-report known issues.

---

## Proven results

| Product | Round | SUS | Fixes | Key improvement |
|---------|-------|-----|-------|-----------------|
| Internal dashboard (example run) | 1 | 57.5 → 77.5 | 100+ | Basic interactivity, real data, help |
| Internal dashboard (example run) | 2 | 77.5 → 85+ | 45+ | Convergence UX, WCAG, mobile |
| Internal dashboard (example run) | 3 | 85+ → 92.5 | 30+ | Polish, emotional design, peak moments |
