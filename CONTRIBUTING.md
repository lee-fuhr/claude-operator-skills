# Contributing

Adding or editing a skill here (by hand or as an AI agent working on this repo):

1. **Naming.** `qq-` = a human types this to invoke it. `ww-` = it loads itself from
   context, no typed command needed. Renaming a skill means grepping the WHOLE repo for
   its old name first, not just its own folder, its own docs page still has to say the
   new name too.
2. **Every skill gets:** the parent-repo banner blockquote at the top of its `SKILL.md`,
   a standalone `docs/<name>.html` page (copy an existing one as a template, don’t
   redirect), an entry in `docs/index.html`, and a Contents + Skills-table row in
   `README.md`. If a skill genuinely doesn’t need its own docs page (a domain sub-skill
   folded into a bigger one, say), register the exemption with a reason in
   `scripts/docs_parity_exemptions.json` instead of just leaving it uncovered.
3. **Never invent a stat or an incident.** If a skill’s value claim can’t be backed by
   something real, say that plainly instead of padding it.
4. **Before every commit:**
   ```bash
   python3 scripts/check_repo.py
   ```
   Checks: no leaked internal paths or names, no stale self-reference left over from a
   rename, every README anchor link resolves, no straight quotes in prose, every skill
   has a docs page (or a registered exemption). Exit 0 and silent means clean. This is
   the actual enforcement. This file is just the explanation of why the checks exist.
   Read `scripts/check_repo.py` and `scripts/test_check_repo.py` before extending it;
   it’s small, add a check the same way the existing ones are built (a function, a test
   proving it catches the bug and doesn’t false-positive on legitimate content).
