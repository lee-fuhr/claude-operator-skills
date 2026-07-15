# Drill-down and navigation patterns

Detailed patterns and anti-patterns for drill-down architecture and navigation/wayfinding.

## Drill-down architecture patterns

### Pattern: four-level hierarchy

Overview → Section → Item → Raw data

- **Overview:** top-level metrics, aggregate status, recent activity summary
- **Section:** one subsystem or category expanded (e.g., all open orders)
- **Item:** one specific entity with full context (e.g., one order with status, timing, and outcome)
- **Raw:** logs, timestamps, IDs, API responses, database rows

Each level is accessible by explicit user action. Each level has a clear return path (close or breadcrumb). Max 4 levels: raw data is always the end.

### Pattern: progressive disclosure by decision need

Only show what is needed to make the current decision. The user drilling to item level needs entity-specific context. The user at overview level needs trend and status. Do not force overview users to process item-level detail.

### Pattern: explicit close affordance on every overlay

Every overlay (modal, drawer, slide-in panel) has:
- ✕ button at top-right, minimum 44×44px
- Escape key support
- Returns to exact prior state (including scroll position) in under 300ms

### Anti-pattern: drill-down dead end

A metric badge with no drill-down path. The user sees “Error” but cannot get to the error details. Every status indicator must be tappable/clickable and must lead somewhere useful.

### Anti-pattern: the infinite nested stack

Modals that open modals. Panels that open panels. After two levels, the user cannot find their way back. Max 4 levels of nesting total, and only when each level genuinely requires the prior level’s context.

---

## Navigation patterns

### Pattern: explicit close on all overlays

See Iron Law 5. ✕ button + Escape always. Never auto-close.

### Pattern: clickable breadcrumbs

Breadcrumbs are not decorative. Every crumb in the breadcrumb trail is a link. Clicking any crumb returns to that exact level (not just “back”). Breadcrumbs must appear on every nested view (depth ≥ 2).

### Pattern: navigation intent clarity

Two distinct visual treatments:
- **Link** (navigates to a new page, changes URL): underlined text or a “→”-style affordance
- **Expand/reveal** (opens an overlay, same URL, same context): chevron ▾ or ⊕ affordance

The user must be able to predict which will happen before clicking.

### Pattern: scroll position preservation

After refresh, orientation change, or tab switch, scroll position is preserved. The user does not return to the top of the page. Exception: destructive navigation (full page reload) is acceptable, but should be labeled as such.
