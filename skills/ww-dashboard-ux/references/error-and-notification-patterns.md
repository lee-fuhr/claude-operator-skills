# Error and notification patterns

Detailed patterns and anti-patterns for error states and notification design, referenced from the dashboard-ux Iron Laws and framework inventory.

## Error state patterns

### Pattern: four-part error structure

Every error message contains: **what happened + why it matters + consequence + what you can do right now.**

```
[Component name] [what happened].
This [why it matters, consequence to user or service].
[Inline action button] or [inline action link]
```

Example:
```
Price-feed scanner stopped (exit code 1).
Live data collection has paused: no new records will be captured.
[Restart scanner]  [View error log]
```

### Pattern: inline vs. notification vs. page-level error placement

- **Inline** (next to the affected component): component-scoped errors (one chart failed to load, one item action failed)
- **Toast notification**: transient system events not specific to the current view
- **Page-level banner**: systemic failures that affect the entire dashboard or primary workflow
- **Modal**: errors requiring immediate decision before proceeding (destructive action failed, data loss risk)

### Pattern: diagnostic depth

Every error has a depth ladder available:
1. **Summary label**, “Scanner stopped”
2. **Plain language**, “The scanner crashed because it ran out of memory”
3. **Consequence**, “No new records will be collected until it restarts”
4. **Action**, “[Restart] [View full log]”
5. **Raw**: link to the full log file, not embedded

Show levels 1–3 by default. Level 4 as buttons. Level 5 behind “View full log.”

### Anti-pattern: the passive error

**Signal:** error state shows what broke but offers no path to resolution.

```
❌ "Upstream API connection failed."
✅ "Upstream API connection failed (timeout after 30s). Processing is paused. [Retry connection] [View status page]"
```

### Anti-pattern: the dead action

**Signal:** button or link appears to work but does nothing (or navigates to a 404/broken anchor).

**Test:** click every action button in an error state. Does it do something in under 5 seconds? If not, it’s a dead action.

**Real-world example:** notification action links using a `#logs/{label}` anchor format that doesn’t correspond to any element ID in the DOM.

### Anti-pattern: the CLI-as-UI

**Signal:** dashboard shows a command the user should run in their own terminal as the recovery action.

```
❌ Run: launchctl start com.example.price-scanner
✅ [Start scanner] (button that executes this command and shows the result)
```

A CLI command displayed in a UI is documentation, not an action. If the user has to open a terminal, the dashboard failed.

---

## Notification design patterns

### Urgency taxonomy (canonical definition)

See Iron Law 6. One taxonomy, used everywhere. Do not define custom urgency levels per feature.

### Pattern: plain-language notification content

Every notification answers:
1. What happened (system or component name + what changed)
2. Why it matters (consequence to the user’s workflow)
3. What to do (inline action, or “no action needed” if truly informational)

### Pattern: snooze model

P1 alerts support snooze. Snooze options:
- 1 hour
- 4 hours
- Tomorrow (9:00am local)
- Dismiss (don’t show again for this instance)

Snooze is not the same as resolve. A snoozed alert re-surfaces at the selected time, still unresolved.

### Pattern: notification detail view

Every notification must expand to a detail view containing:
- Full timestamp (ISO 8601, local time shown with UTC offset)
- Component affected
- What happened (verbose, not truncated)
- History of this alert (how many times has this fired in the last 7 days?)
- Recommended action with a deep link to the relevant log or config

### Anti-pattern: notification without context

```
❌ "Service health degraded"
✅ "Price-feed scanner health degraded (CPU at 94% for 12 min). Scanner may stop responding. [View process details] [Restart]"
```

### Anti-pattern: urgency inflation

P0 alerts that appear more than 5% of the time in any 24-hour window indicate urgency inflation. When everything is urgent, nothing is. Review alert thresholds when P0 volume is high.
