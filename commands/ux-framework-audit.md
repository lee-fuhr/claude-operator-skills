Run 17 UX frameworks serially against the current app. Each framework audits, fixes critical issues, verifies the build, then the next framework runs against the improved codebase. Compounding quality improvements across rounds.

Load the skill file at `~/.claude/skills/ux-framework-audit/SKILL.md` and follow its instructions.

Args: $ARGUMENTS
- (no args): run all 17 frameworks in order
- [framework name]: run a single named framework (e.g. "Nielsen's heuristics", "WCAG 2.1 AA")
- round 2 / round N: run another full pass after previous fixes
- list: show all 17 frameworks with descriptions
