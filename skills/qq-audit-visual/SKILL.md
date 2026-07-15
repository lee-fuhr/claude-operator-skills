---
name: qq-audit-visual
description: Serialized Visual UI Design audit using 22 deep framework subskills. Each framework runs in its own agent context with expert-level depth. Smart interview pre-fills from conversation context.
version: 1.0.0
author: Lee Fuhr
triggers:
  - "visual audit"
  - "design audit"
  - "visual design audit"
  - "ui design review"
  - "visual polish audit"
  - "run visual audit"
  - "run all visual frameworks"
---

# Audit visual design with expert personas

Run a full serial visual design audit using 22 deep expert persona frameworks, fixing critical issues and verifying each framework before proceeding to the next.

22 visual design frameworks, each loaded as a deep expert persona into its own agent context. Serial execution: one framework → fix critical issues → verify → next. Each agent thinks like a 20-year design specialist in that specific framework.

**Domain:** Visual. **Expert lens:** Does this look professional? Would a designer approve?

---

## Modes

This skill responds to three modes based on the args passed. Interpret intent loosely — fuzzy matching, not exact phrasing.

### Mode 1: Full serial audit (no args or "run all")

Triggers: `/qq-audit-visual`, "run all", "full audit", "everything", no args at all.

### Mode 2: Single framework (framework name + optional scope)

Triggers: `/qq-audit-visual typographic hierarchy`, "just run color contrast on the dashboard", "whitespace on the settings page", etc.

Match the framework name fuzzily — "typography", "type hierarchy", "typographic" should all match Typographic Hierarchy. "spacing", "4pt", "8pt" should all match Spacing System. If ambiguous, show the 2-3 closest matches and ask.

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
> - **Design system:** [Tailwind/custom CSS/component library — from project files]
> - **Quality bar:** [aesthetic reference points — from conversation or memory]
> - **Known pain points:** [what the user has mentioned or what recent changes suggest]
> - **Scope:** [full app / specific pages / specific component]
>
> Anything wrong or missing?"

Use AskUserQuestion with multiple choice ONLY for genuine gaps — e.g., if you truly can't tell whether there's a dark mode, ask. If you can infer it, state the inference.

**Interview output becomes the audit context** — passed to every framework agent so they audit with purpose, not generically.

---

## Execution flow (full audit)

### Phase 1: Context gathering
1. Run smart interview (above)
2. Read the product's key pages/components to understand visual scope
3. Take screenshots if browser agent is available

### Phase 2: Serial framework execution

For each framework (in order 1-22):

1. **Spawn one agent** with these instructions:
   - "Read the framework subskill file at `~/.agents/skills/qq-audit-visual/frameworks/[NN-name].md`"
   - "You ARE the expert described in that document. Think like them, not like a generalist."
   - "Audit [product name] focusing on [scope]. Context: [interview output]"
   - "Previous frameworks found these issues: [cumulative findings list]. Do NOT re-report duplicates."
   - "Score 1-10, list findings with file:line references, fix critical issues (score < 7), write report."

2. **Collect the agent's output:**
   - Score for this framework
   - Findings (new, not duplicates)
   - Fixes applied
   - Items flagged for downstream frameworks

3. **Verify build** if fixes were applied (rebuild or screenshot comparison)

4. **Update cumulative state:**
   - Add findings to the dedup list
   - Update the running score card
   - Note cross-framework flags for upcoming frameworks

5. **Move to next framework**

### Phase 3: Synthesis
1. Run framework #22 (Print and Export Visual Quality) as the final evaluation
2. Compile consolidated report:
   - Overall visual design score (average of all frameworks)
   - Per-framework scores
   - All findings grouped by severity
   - Fixes applied (with file:line)
   - Remaining items for future rounds
3. Compare to previous audit rounds if they exist

### Phase 4: Report
Save to project's data directory:
- `data/audit-visual-[date].md` — full report
- `data/audit-visual-[date]-summary.md` — scores + critical findings only

---

## Framework inventory

| # | Framework | Expert lens | Subskill file |
|---|-----------|-------------|---------------|
| 1 | Typographic Hierarchy | Whether type sizes, weights, and styles create a clear, scannable reading order | `01-typographic-hierarchy.md` |
| 2 | Vertical Rhythm and Baseline Grid | Whether text and elements align to a consistent vertical beat, creating visual harmony down the page | `02-vertical-rhythm.md` |
| 3 | Horizontal Grid and Column System | Whether layout uses a consistent column grid to create alignment, proportion, and structural coherence | `03-grid-system.md` |
| 4 | Spacing System / 4pt-8pt Scale | Whether padding, margins, and gaps use a consistent mathematical scale rather than ad-hoc values | `04-spacing-system.md` |
| 5 | Color Theory and Palette Coherence | Whether the color palette has intentional relationships and creates a unified visual identity | `05-color-theory.md` |
| 6 | Color Contrast and Accessibility / APCA | Whether text and interactive elements meet perceptual readability thresholds across all contexts | `06-color-contrast.md` |
| 7 | Visual Weight and Balance | Whether the page feels balanced through intentional distribution of visual weight across the composition | `07-visual-weight-balance.md` |
| 8 | Whitespace as Design Element | Whether negative space is used intentionally to create structure, breathing room, and visual hierarchy | `08-whitespace.md` |
| 9 | Icon System Consistency | Whether icons share consistent style, size grid, stroke weight, and metaphor family across the interface | `09-icon-consistency.md` |
| 10 | Illustration and Imagery Style Coherence | Whether photos, illustrations, and graphic elements share a unified visual language across the product | `10-imagery-coherence.md` |
| 11 | Motion and Animation Purposefulness | Whether animations serve a clear functional purpose — orienting, confirming, or guiding — rather than decorating | `11-motion-animation.md` |
| 12 | Visual Density and Information Density | Whether the content-to-chrome ratio is high — maximizing useful information per pixel while maintaining clarity | `12-information-density.md` |
| 13 | Component Visual Consistency | Whether buttons, cards, inputs, and other UI components look like they belong to the same design family | `13-component-consistency.md` |
| 14 | Elevation and Depth System | Whether shadows, borders, and layering create a consistent, meaningful z-axis that communicates hierarchy and interactivity | `14-elevation-depth.md` |
| 15 | Responsive Visual Integrity | Whether the design holds together at every viewport size — maintaining hierarchy, proportion, and usability from mobile to ultrawide | `15-responsive-integrity.md` |
| 16 | Dark Mode and Theme Consistency | Whether alternate themes maintain visual hierarchy, brand identity, and usability without degrading the design | `16-dark-mode.md` |
| 17 | Border and Divider System | Whether lines, borders, and separators follow a consistent pattern that supports visual structure without adding noise | `17-border-divider-system.md` |
| 18 | Form Design Aesthetics | Whether forms are visually clean, consistently structured, and aesthetically inviting rather than intimidating | `18-form-aesthetics.md` |
| 19 | Visual Hierarchy Scanning and F/Z Patterns | Whether layout structure supports natural eye-scanning patterns — F-pattern for text, Z-pattern for sparse layouts | `19-visual-hierarchy-scanning.md` |
| 20 | Brand Expression Fidelity | Whether the implementation faithfully represents the brand identity — not just using brand assets, but embodying brand personality | `20-brand-expression.md` |
| 21 | Pixel-Level Polish | Whether subpixel alignment, border-radius consistency, anti-aliasing, and the "last 5%" finishing problems are resolved | `21-pixel-polish.md` |
| 22 | Print and Export Visual Quality | Whether exported, printed, or downloaded versions of the interface maintain visual quality and informational integrity | `22-print-export.md` |

---

## Key principles

- **Serial, not parallel** — 70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after fixes.
- **Fix before moving on** — don't accumulate a findings list. Fix each framework's criticals before the next audit.
- **Expert persona, not checklist** — each agent IS the specialist. They reason from principles, not rules.
- **Hold every fix to a real quality bar** — is this real data? Is the complexity earned? Does it prevent errors?
- **Code + screenshots** — code audits miss visual issues. Always audit rendered output when possible.
- **Multi-round** — after all 22 frameworks, run the full cycle again. Scores increase each round until plateau.
- **Dedup across frameworks** — each agent receives cumulative findings so they don't re-report known issues.
