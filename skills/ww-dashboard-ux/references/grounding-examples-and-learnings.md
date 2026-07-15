# Grounding examples and build learnings

Worked examples from a real production operations-dashboard build, and learnings captured across several rounds of dashboard product audits. The specific system these came from is genericized below; the patterns are what matter.

## Grounding examples (from a real production build)

**Strong patterns to emulate:**
- Inline task completion via a ✓ button, action is in context, no navigation required
- One-click service-restart button, an action surface, not a CLI command
- Notification snooze (1h / 4h / Tomorrow / Dismiss), P1-appropriate dismissibility
- A detail overlay with an explicit close button, drill-down with an explicit return
- Two-phase load: cached data shown immediately, then network enrichment, perceived performance done right

**Documented gaps (anti-patterns grounded in real code):**
- Dead hash links (`#logs/{label}`) in notification actions, violates Iron Law 8
- An offline banner showing a raw CLI restart command, violates Iron Law 8
- A detail overlay’s phase-2 content disappearing with no loading state, violates Iron Law 1 (no state shown for “loading phase 2”)
- Status dots using green/red only, no label, violates Iron Law 2

---
## Learnings from a production dashboard build

Patterns discovered across three rounds of product audit on a real operational dashboard. These supplement the iron laws and framework patterns above.

### Learning 1: Independent section loading

Never gate the entire dashboard on a single API call. Each section should load independently with its own skeleton/error state. If one data source is slow, the other metric cards should still render. Implementation: separate data-fetching hooks per source, per-section loading/error branches in the page component.

### Learning 2: Causal narrative for metric movements

“Was 65, now 79” is context. “Climbed because of 23 long sessions this week” is causation. When a metric moves significantly, correlate with recent events and generate a plain-language explanation. This fills the gap between “what happened” and “why.”

### Learning 3: Delight in daily-use tools

Operational dashboards used daily need an emotional register beyond “clinical instrument panel.” Five specific patterns that work:
- **Dynamic health sentence:** replace static subtitles with computed status (“All 5 services healthy. Efficiency up 3 points.”)
- **Streak/momentum:** when a metric improves for 3+ consecutive days, acknowledge it (“3-day streak”)
- **Running tallies:** “12 fixes applied this month” gives a sense of accumulated progress
- **Warm insight tone:** “Your recent fixes are working,” not “Likely due to: applied tighten-wildcard-matchers”
- **Forward-looking empty states:** “Nothing to review. The next check runs at 6:15am daily,” not “No pending items”

### Learning 4: Tooltips must use fixed positioning

Tooltips using `position: absolute` inside scrollable containers (`overflow-y: auto`) get clipped. Always use `position: fixed` with viewport clamping via `getBoundingClientRect()`. Render invisible on the first frame, position on the second frame via `requestAnimationFrame`, then show.

### Learning 5: Batch operations for list-based actions

When a dashboard shows a list of actionable items (proposals, alerts, approvals), provide batch operations (“Approve all low-risk,” “Dismiss all”) in addition to individual actions. Without batch ops, reviewing 10+ items requires 10+ expand-read-click cycles.



*Methodology: a 20-role adversarial synthesis. 19 roles each proposed candidate principles against the real dashboard in round 1; a 20th, dedicated skeptic role challenged all 51 of them in round 2. What’s published above and in the iron laws is only what survived three bars: unconditional, falsifiable, and enforceable at review time.*

---

## Pre-launch checklist (40 items)

### Error states (8 items)

- [ ] Every error message contains: what happened, why it matters, what to do right now
- [ ] No “Error: null,” “undefined,” or raw exception messages visible in any error state
- [ ] Every error state has at least one inline action button (not just a link to docs)
- [ ] Error state placement is appropriate: inline for component errors, banner for systemic errors
- [ ] Empty states (zero results) have an explanation and a next-step action
- [ ] Timeout errors have a retry button (not just “try again” text)
- [ ] Permission-denied errors explain what role is needed, with a path to request access
- [ ] Partial failure states show what loaded and what failed separately

### Notifications and alerts (6 items)

- [ ] Every alert answers: what happened, why it matters, what to do
- [ ] P0 alerts cannot be dismissed (verified: no dismiss button on P0 component)
- [ ] P1 alerts have snooze options (1h / 4h / Tomorrow / Dismiss)
- [ ] No CLI commands displayed as recovery actions
- [ ] Alert urgency taxonomy is consistent across all notification surfaces (no custom levels)
- [ ] Notification detail view shows: timestamp, component, history, recommended action

### Drill-down architecture (5 items)

- [ ] Every status badge or metric is clickable with a drill-down path
- [ ] Maximum drill-down depth is 4 levels (verified by tracing the deepest path)
- [ ] Every nested view has a visible close button (✕) and breadcrumb trail
- [ ] Breadcrumbs are all clickable (not read-only)
- [ ] No notification action links to dead anchors or broken routes

### Data visualization (5 items)

- [ ] No pie charts used for comparisons (use stacked bar instead)
- [ ] No bar charts used for time-series (use line chart instead)
- [ ] All status indicators use two or more encodings (color + shape + text)
- [ ] Stale data (over 5 min old) shows an age label adjacent to the metric
- [ ] Aggregate / health scores expose constituent values (sortable by severity)

### Actionability (4 items)

- [ ] Every action button tested to a live destination at build time
- [ ] Every action shows outcome within 5 seconds (success, error, or in-progress state)
- [ ] Destructive actions have a one-step confirmation dialog (with a specific action label, not “OK”)
- [ ] No action surface relies on “copy this command and run it in terminal”

### Performance perception (3 items)

- [ ] Async data payloads over 100ms show skeleton screens (matching actual layout)
- [ ] Cached data shows on initial load with an “as of X” label while fresh data loads
- [ ] No layout shift when new data arrives (stable layout during two-phase load)

### Accessibility (5 items)

- [ ] All text and data labels pass a 4.5:1 contrast ratio (automated scan)
- [ ] Dashboard navigable by keyboard only (Tab, Shift+Tab, Enter, Escape verified)
- [ ] All icon-only buttons have an aria-label
- [ ] Status indicators that change have aria-live=“polite”
- [ ] Dashboard readable in grayscale (color is never the only encoding)

### Temporal patterns (2 items)

- [ ] Every metric older than 5 minutes shows an age label (“as of 12 min ago”)
- [ ] State age and refresh age are both visible for all key metrics

### Mobile (2 items)

- [ ] All interactive elements have a minimum 44×44px touch target
- [ ] Critical status is visible above the fold on a 375px-wide viewport (iPhone SE)
