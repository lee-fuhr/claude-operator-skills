---
name: copy-sweep
description: A PreToolUse hook that blocks em dashes, straight quotes, and Title Case headings before they ever land in a file. Fires automatically on every Write/Edit/MultiEdit to a matching file — nothing to invoke, nothing to remember. Catches the "AI-tell" punctuation pattern at the source instead of proofreading for it after the fact.
version: 1.0.0
---

# copy-sweep

Someone asks: "has anyone built a Claude skill that goes through a whole build and strips out
em dashes?" The honest answer is you don't need a cleanup pass at all — you need the write to
fail before the em dash ever hits disk. That's what this is.

`copy-sweep` is a **hook**, not a slash command. You never invoke it. Once it's installed, every
time Claude (or you, via Claude Code) writes or edits a matching file, the hook scans the new
content first. If it finds an em dash, a straight quote, or a Title Case heading, the write is
blocked and Claude gets a line-numbered list of exactly what to fix — so it fixes it inline, in
the same turn, before the bad version ever exists.

No proofreading step. No "sweep the repo for em dashes" cleanup task. The thing that would have
needed cleaning never gets written.

---

## What it catches

| Check | Default | Catches |
|-------|---------|---------|
| `em_dash` | on | `—` anywhere in prose (fenced code blocks are exempt) |
| `straight_quote` | on | `"` where a curly quote `“ ”` should be |
| `title_case` | on | Headings like `## The Big New Feature Launch` instead of `## The big new feature launch` |
| `we_pronoun` | **off** | A bare `We` in solo-voice copy — turn on if you write alone and want `I` enforced |

Each is independent. Turn any of them off (or on) with one env var — see Configure, below.

## Install

```bash
git clone https://github.com/lee-fuhr/claude-operator-skills.git
cd claude-operator-skills

mkdir -p ~/.claude/hooks
cp skills/copy-sweep/hooks/copy_sweep.py ~/.claude/hooks/copy_sweep.py
chmod +x ~/.claude/hooks/copy_sweep.py
```

Then add the hook to your Claude Code settings — `~/.claude/settings.json` for every project, or
`.claude/settings.json` in a single repo if you only want it there:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/copy_sweep.py"
          }
        ]
      }
    ]
  }
}
```

Restart Claude Code (or start a new session) so it picks up the settings change. That's it — no
skill to remember to invoke, no command to run. It just runs.

> [!NOTE]
> If you already have a `PreToolUse` hook for `Write|Edit|MultiEdit`, add `copy_sweep.py` as a
> second entry in that same `hooks` array rather than a second matcher block — Claude Code runs
> every hook that matches, in order.

## Try it

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/test.md","content":"Great copy — right here."}}' \
  | python3 ~/.claude/hooks/copy_sweep.py; echo "exit: $?"
```

`exit: 1` with a line-numbered violation list means it's wired up correctly. A clean file (or any
path outside your configured scope) exits `0` silently.

## Configure

Everything is an env var, everything has a working default — set these in your shell profile, or
directly in the `settings.json` hook `command` string (`"command": "COPY_SWEEP_CHECKS=em_dash python3 ~/.claude/hooks/copy_sweep.py"`).

| Variable | Default | What it does |
|----------|---------|---------------|
| `SKIP_COPY_SWEEP` | unset | Set to `1` to bypass entirely for one call — for an intentional exception |
| `COPY_SWEEP_EXTENSIONS` | `.md,.txt` | Comma-separated file extensions to scan |
| `COPY_SWEEP_INCLUDE` | unset (scan everywhere) | Comma-separated path fragments — if set, only files whose path contains one of these are scanned. Use this to scope the hook to `drafts/,content/,copy/` instead of every `.md` file in the repo |
| `COPY_SWEEP_EXCLUDE` | `node_modules/, .git/, .claude/, .agents/, CHANGELOG.md, README.md, LICENSE` | Comma-separated path fragments to always skip |
| `COPY_SWEEP_CHECKS` | `em_dash,straight_quote,title_case` | Comma-separated list of checks to run. Add `we_pronoun` if you want it |

**Two common setups:**

Scope it to a `drafts/` folder only, leave everything else alone:
```json
"command": "COPY_SWEEP_INCLUDE=drafts/ python3 ~/.claude/hooks/copy_sweep.py"
```

Solo-voice writer who wants `I` enforced too:
```json
"command": "COPY_SWEEP_CHECKS=em_dash,straight_quote,title_case,we_pronoun python3 ~/.claude/hooks/copy_sweep.py"
```

## Why a hook and not a skill

A skill needs to be invoked — you have to remember to run `/clean-up-my-copy` after the fact, on
the whole file, hoping you catch everything. A hook fires on the exact write that would have
introduced the problem, catches it in a few lines instead of a whole document, and Claude fixes
it as a two-second inline correction instead of a separate pass. The cleanup pass this replaces
never has to exist.

## Key principles

- **Prevent, don't proofread.** Block the bad write before it happens, not after.
- **Small, specific, and cheap.** No model call — it's a regex scan, sub-second, free.
- **On by default, off by one flag.** `SKIP_COPY_SWEEP=1` for the rare intentional exception; no
  config file to maintain for the common case.
- **Scoped to prose, not code.** Fenced code blocks are always exempt from every check.
