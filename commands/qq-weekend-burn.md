Stand up a new weekend-burn lane: a recurring, self-firing schedule that burns your weekly Claude quota on real work, every week, until you turn it off.

Load the skill file at `~/.claude/skills/weekend-burn/SKILL.md` and follow its instructions. It in turn depends on `~/.claude/skills/keepalive/SKILL.md` for the actual session-survival mechanism; load that too if it isn't already in context.

Args: $ARGUMENTS
- (no args): scaffold a brand-new lane from scratch: pick a directory, write the governing doc, seed the backlog from whatever's in view this session, wire the recurring window function, and hand over the one-paste install block
- [description]: use it as the seed for what this lane's first backlog items should be
