# Actionability and performance perception patterns

Detailed patterns and anti-patterns for action surfaces and perceived loading performance.

## Actionability patterns

### Pattern: inline action on every critical state

Every error state, warning state, or “action required” notification must surface at least one action inline (same screen, no navigation required). The action must:
- Be labeled with a verb (not “OK,” not “Close”)
- Complete in under 5 seconds or show an in-progress state
- Show outcome: success message or error message, never silent

### Pattern: contextual action (surfaces only when relevant)

Actions that are destructive or irreversible appear only when contextually appropriate, not in every row or view by default. Showing “Delete” on every row of a 50-item table is visual noise; showing “Delete” on a selected item is contextual.

### Pattern: optimistic update

For actions where failure is rare (restart, dismiss, snooze), show success immediately and roll back on failure. Do not make the user wait for server confirmation before showing feedback. If rollback is needed, show the failure clearly.

### Pattern: confirm-then-act for destructive actions

Any action that cannot be undone requires one confirmation step:
1. Primary button triggers a confirmation dialog
2. Dialog names specifically what will be destroyed
3. Confirmation button is labeled with the specific action (“Delete position,” not “Confirm”)
4. Cancel is the default focused element (not Confirm)

### Anti-pattern: silent action

Action button clicked, spinner shown, nothing visible changes. The user does not know if the action succeeded, failed, or is still running.

### Anti-pattern: action that requires CLI

See Iron Law 8.

---

## Performance perception patterns

### Pattern: skeleton screen (conditional)

Show a skeleton screen when estimated fetch + render time exceeds 100ms. For payloads estimated under 100ms, show cached data immediately.

Skeleton screens must:
- Match the layout of the content they replace (not a generic spinner)
- Animate subtly (pulse, not spin)
- Be replaced without content instability (no layout shift on content arrival)

### Pattern: stale-while-revalidate

On load, serve cached data immediately. Fetch fresh data in the background. Show:
- Cached data with an “as of [X] ago” label
- Refresh indicator (pulsing dot, not spinner, since the SLA is known)
- Silent update on fresh data arrival (no layout flash; diff and update changed values only)

### Pattern: two-phase load

Phase 1: cached data, instantly. Phase 2: network data, as it arrives. Phases must not cause content instability. New data is appended (“3 new items”), not replacing (the full list does not re-render).

### Pattern: activity indicator vs. spinner

- **Pulsing dot / activity indicator:** operation with a known SLA (an API with a 2-second timeout, polling with a retry limit). The user knows this will resolve.
- **Spinner:** operation without a known SLA (user upload, background job). The user does not know when this will finish.

If an operation exceeds its SLA, upgrade the dot to a spinner.
