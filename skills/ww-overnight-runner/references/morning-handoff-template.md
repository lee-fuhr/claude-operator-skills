# Morning handoff file structure

The tonight-results.md scaffold and status emoji key referenced by SKILL.md’s morning handoff format section.

### File structure

```markdown
# Tonight's session
*Started: [datetime]*

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | [Task name] | [emoji status] | [brief note] |

Status key: Complete / In progress / Blocked / Skipped / Failed

---

## Results

## Task N: [Name]
**Status:** [Complete / Blocked / Failed / Skipped]
**What was built/done:**
- [bullet: specific output]
- [bullet: file path if applicable]

**Files created/modified:** [paths]
**Needs you:** [anything requiring human judgment or review]

---

## Overnight summary
**Tasks completed:** X of Y
**Files created:** N
**Questions parked:** [path to QUESTIONS-FOR-YOU.md or "none"]
**Needs immediate attention:** [anything time-sensitive]
**Suggested first action:** [what you should do first]
```

### Status emoji key

| Emoji | Meaning |
|-------|---------|
| Complete | Verified complete |
| In progress | Still running at session end |
| Blocked | Waiting on your answer |
| Skipped | Skipped due to blocker or hard stop |
| Failed | Attempted, failed, logged |
