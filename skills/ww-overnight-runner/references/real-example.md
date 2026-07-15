# Worked example

A composite worked example of the overnight protocol run in practice, kept for reference.

## Worked example

A representative overnight run against a well-scoped, 10-task self-improvement queue:

- **Results file:** `tonight-results.md`, at the project root
- **Questions file:** Not needed (tasks were well-specified)
- **Agent strategy:** Parallel threads grouped by dependency (infra code together, file ops together, etc.)
- **QA approach:** Verification notes appended per task, steelman run during planning phase
- **Morning handoff:** Results file opened in a markdown viewer for quick review

Key lesson: Well-specified tasks with clear success criteria produce clean results. Ambiguous tasks need `QUESTIONS-FOR-YOU.md` seeded before the session starts, not during.
