Run the Security audit skill. Load the skill file at `~/.agents/skills/qq-audit-security/SKILL.md` and follow its instructions.

Args passed: $ARGUMENTS

If no args: run full serial audit (all 23 frameworks).
If args mention a framework name: run single framework mode.
If args are a question about what's available: run list mode.

Interpret args loosely — fuzzy match framework names, don't require exact phrasing.
