---
title: "qq-mailbox: coordination primitive for concurrent Claude Code sessions"
permalink: /qq-mailbox/
description: A shared inbox for two or more Claude Code sessions handing work back and forth, an overseer and a build session, a headless keepalive and its live counterpart. Append-only, no locks needed, nothing to clobber.
---

# qq-mailbox

**The problem:** Two Claude sessions need to hand work back and forth, an overseer that architects and a build session that implements, say, and there's no channel between them that survives either one restarting. The usual fix is pasting a prompt from one terminal into the other by hand, every handoff, all night.

**The result:** A session drops a message and moves on. The other picks it up on its own schedule, no pasted context, no clobbered state.

## The two calls

```python
from mailbox import send, check

send(lane, from_role="builder", to_role="overseer", kind="design-task", msg="...")
result = check(lane, role="overseer")
# result["action_needed"] -> messages that actually need a response
```

One append-only file per directed pair of roles, atomic monotonic cursor, a kind taxonomy with action hints, role names that are job titles instead of whichever model happens to be sitting in that seat this week.

Full worked example, design invariants, and install steps: [repo README → qq-mailbox](https://github.com/lee-fuhr/claude-operator-skills#qq-mailbox).

[← back to all skills](../)
