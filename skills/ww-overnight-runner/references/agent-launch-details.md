# Agent launch details

The agent-type routing table and the “not a failure” patterns for the overnight agent launch protocol in SKILL.md.

### How many agents

| Work queue size | Agent strategy |
|----------------|----------------|
| 1-3 tasks | Sequential, single thread |
| 4-7 tasks | 2-3 parallel threads, grouped by dependency |
| 8+ tasks | Full parallel: group by type, assign thread leaders |

### Agent types to use

Match agent type to task type. If your setup has specialized agents for these, use them; otherwise handle directly with a general-purpose agent.

| Task type | Agent type |
|-----------|------------|
| Code, infrastructure scripting | A tiered build setup if you have one (architect → senior → junior), otherwise a single capable code agent |
| Documentation, write-ups | Content/writing specialist |
| File organization, routing | Solo execution (fast, no agent overhead) |
| Research, analysis | Research agent + synthesis |
| Docs-platform formatting (Google Docs, Notion, etc.) | A dedicated docs-formatting agent if you have one, otherwise handle directly via the platform’s API/extension |
| QA, testing | QA agent |
| Multiple subsystems | Conductor (meta-orchestrator) |


### Expected patterns (not failures)

**Agents combining tasks:** When two adjacent tasks are closely related, a single agent will often handle both in one pass. This is efficient. Log the combined result as “Task N+M” in the results file. Do not treat it as scope creep.

**Two-pass tasks:** A complex task may get a structural pass (one agent) then a formatting or quality pass (a second agent). The second agent should read the results file and pick up exactly where the first left off. This is a valid pattern — do not re-do the structural work.
