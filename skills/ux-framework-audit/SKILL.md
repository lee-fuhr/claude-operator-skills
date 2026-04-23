---
name: ux-framework-audit
description: Run 17 UX frameworks serially against any web app. Each framework audits, fixes critical issues, verifies build, then the next framework runs against the improved version. Proven to raise SUS scores from 57.5 to 92.5.
version: 2.0.0
triggers:
  - "ux audit"
  - "usability audit"
  - "heuristic evaluation"
  - "ux framework review"
  - "sus score"
  - "run all frameworks"
---

# Serialized UX framework audit

Run 17 usability frameworks against a product serially. Each framework: evaluate source code + screenshots → fix critical issues → verify build → next framework.

## Results

Proven on a production Next.js dashboard (170+ components):
- **Round 1:** SUS 57.5 → 77.5 (100+ fixes)
- **Round 2:** SUS 77.5 → 90.0 (45+ fixes)
- **Round 3:** SUS 90.0 → 92.5 (8 fixes, diminishing returns)
- **Ceiling:** ~93-95 without visual redesign

## Installation

```bash
npx skills add lee-fuhr/ux-framework-audit
```

Or manually copy `SKILL.md` to `~/.agents/skills/ux-framework-audit/SKILL.md`.

## Usage

### Run all 17 frameworks
```
Run the full UX framework audit on this app
```

### Run a single framework
```
Run Nielsen's heuristics audit on this app
Run WCAG 2.1 AA audit
Run Fitts's Law evaluation
```

### Run another round (after fixes)
```
Run the UX framework audit again — round 2
```

## The 17 frameworks

Run in this order — surface issues first, then deeper cognitive and accessibility problems:

| # | Framework | What it catches |
|---|-----------|----------------|
| 1 | **Nielsen's 10 heuristics** | Visibility, error prevention, consistency, help |
| 2 | **Gestalt principles** | Visual grouping, similarity, figure-ground |
| 3 | **Fitts's Law** | Touch targets too small, primary actions too far |
| 4 | **Hick's Law** | Too many choices, decision paralysis |
| 5 | **Miller's Law** | Cognitive overload, chunking failures |
| 6 | **Jakob's Law** | Violating patterns users already know |
| 7 | **Aesthetic-usability** | Visual polish, perceived reliability |
| 8 | **Von Restorff effect** | Primary actions don't stand out |
| 9 | **Zeigarnik effect** | Missing progress indicators, no completion signals |
| 10 | **WCAG 2.1 AA** | Contrast, keyboard nav, screen readers, focus states |
| 11 | **Emotional design** | Cold/functional feel, no delight moments |
| 12 | **Progressive disclosure** | Complexity shown all at once |
| 13 | **Error tolerance** | No undo, silent failures, missing confirmation |
| 14 | **Consistency audit** | Visual/behavioral/semantic inconsistency |
| 15 | **Information architecture** | Navigation confusion, mislabeling |
| 16 | **Responsive design** | Mobile/tablet breakpoint failures |
| 17 | **SUS (final score)** | System Usability Scale — the measuring stick |

## Process per framework

1. **Read the codebase** — all page components, navigation, modals, CSS
2. **Score each criterion** (1-10)
3. **Fix critical issues** (score < 7) directly in the code
4. **Verify build** compiles clean
5. **Write report** to `data/audit-{framework}.md`
6. **Move to next framework**

## Key principles

### Serial, not parallel
70% of findings duplicate across frameworks. Serial means each round finds genuinely new issues after the previous round's fixes.

### Fix before moving on
Don't accumulate a findings list. Fix each framework's critical issues before the next audit runs. This compounds — framework 5 audits code that already has fixes from frameworks 1-4.

### Code + screenshots
Code audits miss visual hierarchy, spacing, and contrast. Use screenshots or browser automation when possible.

### Multi-round
After all 17 frameworks, run the full cycle again. Scores increase each round until diminishing returns (~round 3).

## Report format

Each framework produces a report:

```markdown
### [Framework name]
**Score:** X/10

**Findings:**
- [Finding] — [file:line] — [severity: critical/minor]

**Fixes applied:**
- [What was fixed] — [file:line]

**Remaining (nice to have):**
- [Minor issues for future rounds]
```

## What this catches that single-framework audits miss

| Issue type | Found by | Missed by |
|-----------|---------|-----------|
| Fake data displayed as real | Nielsen H1 | SUS |
| Touch targets under 44px | Fitts | Nielsen |
| No undo on destructive actions | Error tolerance | Gestalt |
| Agent jargon instead of user language | Nielsen H2 | WCAG |
| 10+ nav items without grouping | Hick + Miller | Aesthetic |
| Primary CTA same visual weight as secondary | Von Restorff | Consistency |
| No progress indicator on long tasks | Zeigarnik | Fitts |
| Mobile layout completely broken | Responsive | SUS |

## Insights from 3 rounds of audits

1. **Honesty is the hardest principle.** Fake data persists across multiple cleanup rounds. "Looks like it works" is not "works."

2. **Help docs reveal product problems.** When help is hard to write, the feature is confusing. Fix the tool until the docs are easy to write.

3. **Error tolerance is universally undertested.** Most apps have exactly 1 undo point. Users need recovery at every destructive action.

4. **SUS 85+ requires fixing things that don't feel broken.** Touch targets, contrast ratios, and focus indicators aren't exciting but they add up.

5. **Diminishing returns hit at round 3.** Round 1: 100+ fixes. Round 2: 45 fixes. Round 3: 8 fixes. The remaining issues are product decisions, not UX deficiencies.

## License

MIT
