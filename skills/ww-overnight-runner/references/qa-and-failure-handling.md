# QA and failure handling details

The full “always active” QA gate list, the visual-verification workflow for UI builds, the per-agent pre/post-task checklists, and the retry strategy after a failure.

### Always active

1. **Steelman every plan** before execution — even for small tasks
2. **Verification agent** runs after each significant task: reads output, confirms it meets success criteria
3. **For any build > 1 hour**: run a QA swarm (parallel critique agents) before declaring done
4. **TDD**: tests written before implementation. Red phase must be confirmed.
5. **No completion language** (“done”, “fixed”, “working”) without verification evidence
6. **Audit gates are convergence loops to 9.5, not single passes.** For any UI or site build, schedule gates at logical checkpoints (first page, all pages, pre-publish). At each gate: run your audit process, iterate audit → fix → re-audit until every relevant pillar scores ≥9.5/10. Single-pass audits under-deliver; the plateau pattern is chase-9.5-against-live-code.
7. **Every response and status update ends with one status line:** `🟢` done · `🟡` non-routine follow-up remains (name the item) · `🔴` blocked on you. Under 100 chars, at the very end, nothing after it.

### Visual verification at breakpoints (UI builds)

For any build that produces visual output (marketing sites, dashboards, landing pages, email templates):

- **Desktop / tablet / mobile screenshots are mandatory at every audit gate.** Standard breakpoints: `1440` / `768` / `390`. Use a headless screenshot tool against the staging URL, save PNGs into `<project>/content/screenshots/<gate>/<page>-<breakpoint>.png`.
- **Screenshots get embedded in the status doc** at each gate via whatever free image host you use, so you can review from your phone. Never attach local file paths — they don’t render.
- **A browser MCP’s snapshot tool can be dangerous** on many setups — it has crashed sessions with oversized images (>2000px). Prefer a standalone screenshot tool against a published staging URL. If you must use an MCP snapshot tool, scope to a single element ID, never the body.
- **If a screenshot returns oversized or fails**, abandon that snapshot and move on. Do NOT retry the same element — that’s how sessions crash.

### Pre-task checklist (each agent runs before starting)

- [ ] Is the success criterion clear and measurable?
- [ ] Are there hard stops that apply to this task?
- [ ] Does this task write to files that another parallel agent is also writing? (If yes: serialize)
- [ ] Is there a test I should write first?
- [ ] What’s the failure mode? How will I detect it?

### Post-task verification (each agent runs after completing)

- [ ] Read the output. Does it match the success criterion?
- [ ] Run any relevant tests
- [ ] Check for side effects (unexpected file changes, DB mutations)
- [ ] Append result to tonight-results.md

### Retry strategy

Before retrying:
- Re-read the task description
- Check if the approach had a flawed assumption
- Try a simpler approach first

After retry fails:
- Write clear failure notes: error message, what was tried, what would be needed to unblock
- Suggest a path forward in the results file
- Move on
