# Accessibility, role, typography, and mobile patterns

Detailed patterns for accessibility, multi-role audiences, typography/data density, and mobile/responsive layout.

## Accessibility patterns

### WCAG 2.1 AA minimum

Operational dashboards are critical infrastructure used during incidents, often by stressed users in unfamiliar environments. AA compliance is the floor, not aspirational.

Mandatory:
- 4.5:1 contrast ratio for body text and data labels
- 3:1 contrast ratio for large text (18pt+ or 14pt bold)
- No time limits on user actions
- No content that flashes more than 3 times per second

### Pattern: keyboard navigation completeness

Every interactive element reachable by Tab in logical order (left-to-right, top-to-bottom). Required:
- Tab: next interactive element
- Shift+Tab: previous
- Escape: close modal / cancel action
- Enter: confirm focused action
- Arrow keys: navigate within component (dropdowns, tabs, radio groups)

Tab focus indicator must be visible (never hidden with `outline: none`). Focus must not become trapped inside a component unless it is a modal.

### Pattern: ARIA for dynamic content

- Status indicators that change value: `aria-live="polite"` + `aria-atomic="true"`
- Icon-only buttons: `aria-label` required (not empty)
- Progress indicators: `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`
- Error messages: `role="alert"` for automatic announcement

### Pattern: color-independent status

Test: convert to grayscale. All status distinctions must remain readable. Every status uses two or more independent encodings. See Iron Law 2.

---

## Multi-role and audience patterns

### Pattern: implicit role inference

Better than explicit mode switching. If the system knows who is logged in and what their role is, default their view to the role-appropriate layout: an operator sees immediate issues, a manager sees trends, an engineer sees log density. No “which role are you?” prompt.

### Pattern: disabled actions with visible explanation

When an action is disabled because the user lacks permission, show the explanation without requiring a hover tooltip. Inline text (“Requires admin role”) or an info icon with a visible label. Do not show a grayed-out button with no explanation.

### Anti-pattern: the “show everything” universal view

A dashboard where operators, managers, and engineers all see the same screen. The result is too much information for any single role. If one dashboard serves three roles, three separate default views should exist, even if built on the same components.

---

## Typography and data density patterns

### Pattern: monospaced figures in data tables

Numbers in tables and dashboards must use tabular (monospaced) figures so columns align vertically. Variable-width figures cause misalignment when scanning a column.

Use `font-variant-numeric: tabular-nums` in CSS. Verify: a column of numbers with different digit counts should have all digits perfectly left-aligned.

### Pattern: label size hierarchy

Use relative units, not absolute pixels. Recommended hierarchy:
- **Primary label:** 1rem (scales with root font-size)
- **Secondary label:** 0.875rem
- **Tertiary / metadata:** 0.75rem

Root font-size: 16px on desktop, 14px on screens under 600px. All labels scale together.

### Pattern: minimum row height for data tables

Minimum 12px top + 12px bottom padding on data table rows, plus line-height of 1.5 or greater. Measured from actual rendered output.

---

## Mobile and responsive patterns

### Pattern: touch target minimum

All interactive elements (buttons, links, checkboxes, icons) must have a minimum 44×44px touch target. For small icons, use invisible padding to extend the tap area without changing the visual size.

### Pattern: viewport-aware prioritization

Mobile views do not simply reflow desktop views. They prioritize:
- Critical status at top (most important alert, most critical metric)
- Secondary actions collapsed (accessible via tap, not visible by default)
- Side-by-side layouts stack vertically only when both columns are equally important

Breakpoints:
- Under 600px: single column, secondary actions collapsed
- 600–1024px: two column, critical actions in first column
- Over 1024px: full layout

### Pattern: orientation change handling

Scroll position and state preserved on orientation change. Modal state preserved. Form input preserved. Exception: charts may resize and re-render, which is acceptable if the re-render is under 200ms.
