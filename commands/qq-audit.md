Run the master audit orchestrator. Load the skill file at `~/.claude/skills/qq-audit-master/SKILL.md` and follow its instructions.

Args: $ARGUMENTS

If no args: analyze project context and recommend the right combination of audit domains.
If args name specific domains: run those domains in recommended order.
If args name a preset (quick, pre-launch, post-build, deep, code, user-facing, marketing): run that combo.
If args are a question about what's available: show all 13 domains with framework counts.

Interpret args loosely — fuzzy match domain names and presets, don't require exact phrasing.
