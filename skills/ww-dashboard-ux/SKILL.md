---
name: ww-dashboard-ux
description: “Rules for operational dashboard UX/UI: actionable error states, drill-down architecture, notification design, data visualization, progressive disclosure, performance perception, and accessibility. Load when building, reviewing, or auditing any operational or monitoring dashboard.”
version: 1.0.0
triggers:
  - “dashboard audit”
  - “dashboard UX”
  - “dashboard best practices”
  - “review this dashboard”
  - “operational dashboard”
  - “monitoring UI”
when_to_use: “Any dashboard or monitoring interface, new build, code review, pre-launch QA, or post-build audit.”
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Dashboard UX skill

An operational dashboard is different from a marketing page or a settings screen: someone reaches for it specifically because something might be wrong, often while stressed, often mid-incident. The rules below exist because dashboards built without them fail in the same handful of predictable ways: errors with no path to resolution, status dots nobody colorblind can read, metrics with no idea how stale they are, buttons that silently do nothing.

These rules were produced through an adversarial synthesis process: several proposer passes generated candidate principles against a real production dashboard, then a dedicated skeptic pass challenged every one of them. What survived below is only what passed three bars: **unconditional, falsifiable, and enforceable at build or review time.** Everything that was situational, subjective, or unenforceable got cut, so what’s left is meant to be applied without “it depends.”

---

## How to invoke this skill

| Mode | Trigger | What it does |
|------|---------|-------------|
| **1: Full audit** | No args, “full audit”, “review everything” | Runs all 10 frameworks against the target, serial with proposed fixes |
| **2: Focused area** | Framework name or area (fuzzy matched) | Runs one framework; shows 2–3 matches if ambiguous |
| **3: Checklist** | “checklist”, “pre-launch”, “quick check” | Runs the 40-item checklist against the target |
| **4: Patterns reference** | “patterns”, “how do I…”, “what’s the right way to…” | Returns relevant pattern(s) without running an audit |

**Default:** If invoked without args and no target is provided, ask which mode is wanted and what dashboard to audit.

---

## Iron laws

**These are unconditional.** No exceptions. No “it depends.” A dashboard that violates any of these is incomplete regardless of everything else it does well.

### Iron law 1: Error and alert messages have three parts

**Every error state and every alert must contain:**
1. **What happened**: specific, not “an error occurred”
2. **Why it matters**: consequence to the user, service, or data
3. **What you can do right now**: at least one inline action, not a link to docs

**Enforcement:** Code review checklist. Screenshot review: does the error message answer all three? If “Error: null” appears anywhere in production, this law is violated.

**Positive example:** a crash notification for a background job: “Price-feed scanner crashed (exit 1). This stops live data collection. [Restart] [View logs].” All three parts present.

**Anti-pattern:** One metrics panel shows a spinner indefinitely with no error state at all. The user has no idea what happened, why, or what to do.

**Scope:** all error states: API failures, timeout, rate limit, permission denied, empty state (zero results), and partial failure (some data loaded, some failed). Transient errors (auto-resolving in under 3 seconds) may omit parts 2 and 3, but must still name part 1.

---

### Iron law 2: Status never relies on color alone

**Every status indicator must use at minimum two independent encodings.** Color alone is insufficient. Required combinations:

- Color + text label (e.g., red circle + “Error”)
- Color + shape (e.g., red triangle vs. green circle)
- Color + icon (e.g., red ✕ vs. green ✓)

**Enforcement:** Automated test: convert screenshots to grayscale. All status distinctions must remain readable in grayscale. Any status indistinguishable without color fails.

**Positive example:** Grafana alert states: an “Alerting” badge uses red background + text label + bell icon. A colorblind user has two other signals.

**Anti-pattern:** Agent status dots using green/red with no label. A colorblind user loses all status information.

**Standard:** WCAG 2.1 AA minimum. 4.5:1 contrast ratio for text on colored backgrounds. 3:1 for large text.

---

### Iron law 3: Every metric displays its age

**Any metric that could be stale must show how old it is.** “Stale” is defined as: data older than 5 minutes, OR data from a batch job with a known freshness window.

Required display:
- Age label if data is 5–60 minutes old: “as of 12 min ago”
- Freshness warning if data is over 60 minutes old: visual differentiation + age label
- “Live” badge only if data is genuinely streaming (WebSocket, SSE) with under 30 second latency

**Enforcement:** code audit: grep for metric display components without an associated timestamp. Data age must be machine-readable (ISO timestamp in the data layer), not just displayable.

**Positive example:** a two-phase load pattern: cached data shows immediately with a subtle “updating…” indicator, then gets replaced with fresh data. The age of the cached data stays visible throughout.

**Anti-pattern:** Summary dashboards that show aggregate values with no indication of the aggregation window (is this last-5-minutes or last-24-hours?). Identical numbers could mean very different things.

**State age vs. refresh age are different.** “Data updated 2 hours ago” is not the same claim as “dashboard last refreshed 30 seconds ago.” Both must be visible. Refreshing a stale cache tells the user the dashboard is working, not that the data is fresh.

---

### Iron law 4: Every user-initiated action is logged

**Operational dashboards are accountability surfaces.** Every action taken from the UI must be recorded:

| Field | Required | Example |
|-------|----------|---------|
| Actor | Who | “jane@example.com” |
| Timestamp | When (UTC ISO 8601) | “2026-04-06T19:23:45Z” |
| Action | What | “restarted price-feed scanner” |
| Outcome | Success or fail | “success” / “error: exit 1” |

**Constraints:** Logs are immutable (append-only). Queryable by all four fields. Retained a minimum of 90 days. Available in-dashboard (no separate log tool required). Machine-readable (JSON) and human-readable (summary view).

**Enforcement:** Schema-level: insert-only table, no UPDATE or DELETE on log rows. Integration test: take an action, query the log, verify all four fields are present.

**Anti-pattern:** Dashboards with “restart” buttons that have no audit trail. When something breaks after a restart, there’s no way to determine who restarted it, when, or whether it succeeded. The action surface becomes a liability.

---

### Iron law 5: Modals close explicitly, never by timeout

**Every modal (overlay, drawer, dialog, popover) must close via:**
- Explicit close button (top-right, ✕, minimum 44×44px touch target), OR
- Escape key

**Never auto-close on timeout.** The user may be reading. Auto-closing while a user is acting is a data-loss risk.

**Dismissibility is gated by urgency:**
- P0 (immediate): cannot be dismissed. Must be acted upon or explicitly escalated (“I’ll handle this later, remind me in [X]”)
- P1 (within hour): dismissible with snooze: 1h / 4h / Tomorrow / Dismiss
- P2 (within day): dismissible with “never show again”
- P3 (informational): dismissible immediately, no confirmation

**Enforcement:** e2e test: open modal, press Escape, modal closes. Open modal, wait 30 seconds, modal still open. Open a P0 alert, verify no dismiss button exists, only action buttons.

**Positive example:** a notification snooze with 1h / 4h / Tomorrow / Dismiss options: P1-level gating with clear choices.

**Anti-pattern:** modal libraries left with click-outside-to-close enabled and no static backdrop: clicking outside closes the modal during form fill.

---

### Iron law 6: Alerts are triaged by urgency, not subjective severity

**Urgency and severity are different things.** A low-severity bug that blocks the user right now is P0. A high-severity outage affecting 1,000 users that can’t be fixed right now is P1.

**Urgency taxonomy (single shared definition across the UI):**

| Level | Window | Surface | Dismissibility |
|-------|--------|---------|---------------|
| P0 | Immediate block | Full-width banner + optional modal | Non-dismissible |
| P1 | Within 1 hour | Toast notification | Snooze (1h / 4h / Tomorrow / Dismiss) |
| P2 | Within 1 day | Notification center sidebar | Dismiss |
| P3 | Informational | Notification center only | Dismiss immediately |

**Distribution constraint:** P0 alerts must be ≤5% of all alerts in any 24-hour window. If P0 volume exceeds 10%, that’s a signal P0 is being over-used (urgency inflation), not that everything is truly critical.

**Enforcement:** Design system enforces surface by urgency (a P0 component maps to the full-width banner template, not a generic alert). Code review: any `priority="P0"` must be justified in a comment.

---

### Iron law 7: Drill-down paths are explicit, bounded, and closeable

**Every view that reveals more detail must:**
- Have an explicit close affordance (✕ button) that returns to the exact prior state in under 300ms
- Show breadcrumbs at every nesting level, each breadcrumb clickable and returning to that level
- Bound depth at a maximum of 4 levels: overview, section, item, raw data
- End at raw data (timestamps, IDs, log lines): the raw view has no further drill-down

**Never auto-navigate.** A click on a metric should always do one thing (drill in, or navigate to a new page) and be visually differentiated (a drill-in affordance is not the same as a link). The user must know before clicking what will happen.

**Enforcement:** Count nesting depth in code (depth parameter or router stack). e2e test: navigate to depth 4, verify no further drill-down option exists. Screenshot test: every nested view has a visible breadcrumb and close button.

**Positive example:** A detail overlay that opens over the main view, has an explicit close button, and returns to the exact previous scroll position on close.

**Anti-pattern:** Notification action links pointing to dead hash anchors (`#logs/{label}`) that don’t correspond to any real element on the page. The drill-down exists in intent (the notification references logs) but the path is actually broken.

---

### Iron law 8: Action surfaces are tested, not assumed

**A button or link that does not work is worse than no button at all.** A broken action teaches the user that actions on this dashboard don’t work, which destroys trust in every other action too.

**Every interactive element in an action surface (restart, dismiss, retry, view, export) must:**
- Be tested to a live destination at build time
- Return a meaningful result or error within 5 seconds (not a spinner that never resolves)
- Show outcome immediately: success state, error state, or “in progress” state; never silent

**Enforcement:** Integration tests on all action endpoints. No CLI commands displayed as copyable text (this is not an action, it is documentation). If the action requires a CLI command, wrap it in a button that executes the command and shows the result.

**Anti-pattern:** An offline banner that shows a raw CLI command (e.g. `launchctl start com.example.price-scanner`) as a code block. This is documentation masquerading as an affordance. The user has to copy it, open a terminal, and paste it: three steps instead of one click.

---

## Framework inventory

Ten expert lenses for auditing operational dashboards. Each maps to a body section below. Run all 10 for Mode 1 (full audit); run one or two for Mode 2 (focused area).

| # | Framework | Key question | Section |
|---|-----------|-------------|---------|
| 1 | Error state patterns | Can every error be diagnosed AND fixed from the UI? | §Error states |
| 2 | Notification design | Is each alert actionable, triage-appropriate, and plain-language? | §Notification design |
| 3 | Drill-down architecture | Can every metric be traced to raw data? | §Drill-down architecture |
| 4 | Data visualization | Does chart type match data type? Is encoding accessible? | §Data visualization |
| 5 | Actionability | Is every action surface real, accessible, and audited? | §Actionability |
| 6 | Performance perception | What does the user see while data loads? | §Performance perception |
| 7 | Accessibility | Does the dashboard work without color? Without a mouse? | §Accessibility |
| 8 | Temporal patterns | Does the user know how fresh each metric is? | §Temporal patterns |
| 9 | Navigation & wayfinding | Can the user always find their way back? | §Navigation |
| 10 | Data provenance | Can the user tell real data from cached, batch, or demo data? | §Data provenance |

## References
- Read `references/error-and-notification-patterns.md` when auditing or building error states, empty states, or notification/alert UI.
- Read `references/drilldown-and-navigation-patterns.md` when auditing or building drill-down hierarchies, breadcrumbs, or overlay close behavior.
- Read `references/dataviz-and-provenance-patterns.md` when choosing a chart type, displaying data age, or distinguishing real, batch, or demo data.
- Read `references/actionability-and-performance-patterns.md` when designing action buttons, destructive-action confirmation, or loading/skeleton states.
- Read `references/accessibility-and-layout-patterns.md` when auditing accessibility, multi-role views, data-table typography, or mobile/responsive layout.
- Read `references/pre-audit-interview.md` when running Mode 1 (full audit) and the pre-audit questions aren’t already answered by inspection.
- Read `references/grounding-examples-and-learnings.md` for worked examples from a real production dashboard build, plus the full 40-item pre-launch checklist (Mode 3).

This skill pairs well with a broader UX audit process if you run one separately (for instance a general-purpose UX audit skill, if you have one installed). This skill’s frameworks are dashboard-specific and don’t try to replace a general UX pass.
