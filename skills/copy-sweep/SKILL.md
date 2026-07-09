---
name: copy-sweep
description: A PreToolUse hook that blocks AI-tell writing before it ever lands in a file, with a budgeted em dash rule, straight quotes, Title Case headings, banned corporate-speak, throat-clearing openers, and summary-crutch headers, plus three optional model-graded checks. Fires automatically on every Write/Edit/MultiEdit to a matching file. Nothing to invoke, nothing to remember.
version: 2.0.0
---

# copy-sweep

AI-tell punctuation and phrasing creep into drafts one write at a time. The usual fix is a
cleanup pass after the fact: sweep the file, catch what you can, hope you got it all. That
pass shouldn't need to exist: the write should fail before the tell ever hits disk. That's
what this is.

`copy-sweep` is a **hook**, not a slash command. You never invoke it. Once it's installed, every
time Claude (or you, via Claude Code) writes or edits a matching file, the hook scans the new
content first. If it finds a violation, the write is blocked and Claude gets a line-numbered list
of exactly what to fix, so it fixes it inline, in the same turn, before the bad version ever
exists.

No proofreading step. No "sweep the repo for em dashes" cleanup task. The thing that would have
needed cleaning never gets written.

---

## What it catches

**Deterministic, on by default, zero model calls, sub-millisecond:**

| Check | Catches |
|-------|---------|
| `em_dash` | A *budget*, not a ban: 0 allowed under `COPY_SWEEP_LONGFORM_WORDS` (default 400), 1 allowed above it. The one you keep in a long piece still has to earn its place. See below. |
| `straight_quote` | `"` where a curly quote `“ ”` should be |
| `title_case` | Headings like `## The Big New Feature Launch` instead of `## The big new feature launch` |
| `banned_phrase` | Corporate-speak/buzzwords: `leverage`, `synergy`, `touch base`, `circle back`, `cutting-edge`, `best-in-class`, `excited to announce`, and more (full list + how to override it below) |
| `throat_clearing` | Openers like "As you know," "We're excited to announce" |
| `summary_crutch` | Headers like "Bottom line:", "Key takeaways:" |
| `we_pronoun` | **Off by default.** A bare `We` in solo-voice copy; turn on if you write alone and want `I` enforced |

**Semantic, off by default, needs a model call:** `vague_pronoun`, `rule_of_three`,
`pontificating`. These catch patterns a regex genuinely cannot. Read the [Semantic
checks](#semantic-checks-off-by-default-read-this-first) section below before turning any of
them on, it explains the real tradeoff (nondeterminism, latency, small API cost).

Each check is independent. Turn any of them on or off with one env var; see Configure, below.

### The em-dash budget

Zero em dashes in short-form copy (a Slack message, a DM, a short email: anything under
`COPY_SWEEP_LONGFORM_WORDS`, default 400 words). One allowed in a long-form piece (an article,
a long post). That one dash isn't pre-approved just because it's within budget. The hook can
count occurrences; it can't judge whether a specific em dash is actually earning its place versus
being a lazy default. That judgment call is still yours. A second em dash in the same piece is
over budget regardless, and gets flagged like anything else.

## Install: just tell Claude

Paste this to Claude Code, no dev experience required:

> Install copy-sweep from https://github.com/lee-fuhr/claude-operator-skills and walk me through my config options.

**If you are the Claude reading this because a user asked you to install copy-sweep, follow this
script instead of dumping the manual steps on them:**

1. Clone the repo (or fetch just this file plus `hooks/copy_sweep.py` if you can't clone) and
   copy `skills/copy-sweep/hooks/copy_sweep.py` to `~/.claude/hooks/copy_sweep.py`, `chmod +x` it.
2. Read `~/.claude/settings.json` if it exists. If it already has a `PreToolUse` hook for
   `Write|Edit|MultiEdit`, add `copy_sweep.py` as another entry in that same `hooks` array.
   Don't clobber whatever's already there. If the file doesn't exist, create it with the block
   from the manual steps below.
3. Ask the user these questions, in plain language, one at a time or as a short batch, not as
   env var names:
   - "Want this watching every markdown file, or just a specific folder like `drafts/`?" → sets
     `COPY_SWEEP_INCLUDE` if they name a folder, leave unset otherwise.
   - "Do you write solo and want me to also flag any stray 'We' that should be 'I'?" → adds
     `we_pronoun` to `COPY_SWEEP_CHECKS` if yes.
   - "Want the deeper checks too: vague pronouns, three-item-list rhythm, rambling openers
     before the point? These call an external AI model each time so they're a bit slower and
     need a free Groq API key (or DeepSeek). Want those on, or stick with the instant checks?"
     → if yes, add `vague_pronoun,rule_of_three,pontificating` to `COPY_SWEEP_CHECKS`, and check
     whether `GROQ_API_KEY` or `DEEPSEEK_API_KEY` is already set; if neither is, tell them plainly
     these three checks will just silently do nothing until a key is added (fail-open, not broken).
   - "Roughly how many words counts as 'long' for you before an em dash is allowed?" → sets
     `COPY_SWEEP_LONGFORM_WORDS` if they want something other than the 400-word default.
   - "Any words or phrases specific to your own writing you want banned, beyond the default
     corporate-speak list (leverage, synergy, touch base, and friends)?" → sets
     `COPY_SWEEP_BANNED_PHRASES` (this REPLACES the default list, so combine their additions with
     the defaults above if they want both).
4. Write the final `command` string with the resolved env vars baked in, save `settings.json`.
5. Run the [Try it](#try-it) check yourself to confirm it's wired up, then tell the user in one
   or two plain sentences what you set up: no JSON, no env var names in the summary.
6. Tell them to restart Claude Code (or start a new session) for the hook to take effect.

**Prefer to do it yourself?** The manual steps and every config flag are below.

```bash
git clone https://github.com/lee-fuhr/claude-operator-skills.git
cd claude-operator-skills

mkdir -p ~/.claude/hooks
cp skills/copy-sweep/hooks/copy_sweep.py ~/.claude/hooks/copy_sweep.py
chmod +x ~/.claude/hooks/copy_sweep.py
```

Then add the hook to your Claude Code settings: `~/.claude/settings.json` for every project, or
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

Restart Claude Code (or start a new session) so it picks up the settings change. That's it. No
skill to remember to invoke, no command to run. It just runs.

> [!NOTE]
> If you already have a `PreToolUse` hook for `Write|Edit|MultiEdit`, add `copy_sweep.py` as a
> second entry in that same `hooks` array rather than a second matcher block. Claude Code runs
> every hook that matches, in order.

## Try it

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/test.md","content":"Great copy — right here."}}' \
  | python3 ~/.claude/hooks/copy_sweep.py; echo "exit: $?"
```

`exit: 1` with a line-numbered violation list means it's wired up correctly. A clean file (or any
path outside your configured scope) exits `0` silently.

## Configure

Everything is an env var, everything has a working default; set these in your shell profile, or
directly in the `settings.json` hook `command` string (`"command": "COPY_SWEEP_CHECKS=em_dash python3 ~/.claude/hooks/copy_sweep.py"`).

| Variable | Default | What it does |
|----------|---------|---------------|
| `SKIP_COPY_SWEEP` | unset | Set to `1` to bypass entirely for one call: an intentional exception |
| `COPY_SWEEP_EXTENSIONS` | `.md,.txt` | Comma-separated file extensions to scan |
| `COPY_SWEEP_INCLUDE` | unset (scan everywhere) | Comma-separated path fragments. If set, only files whose path contains one of these are scanned. Use this to scope the hook to `drafts/,content/,copy/` instead of every `.md` file in the repo |
| `COPY_SWEEP_EXCLUDE` | `node_modules/, .git/, .claude/, .agents/, CHANGELOG.md, README.md, LICENSE` | Comma-separated path fragments to always skip |
| `COPY_SWEEP_CHECKS` | `em_dash,straight_quote,title_case,banned_phrase,throat_clearing,summary_crutch` | Comma-separated list of checks to run: that's the deterministic default set. Add `we_pronoun`, or any of the three semantic checks, to turn them on |
| `COPY_SWEEP_LONGFORM_WORDS` | `400` | Word-count threshold feeding the em-dash budget |
| `COPY_SWEEP_BANNED_PHRASES` | see `DEFAULT_BANNED_PHRASES` in the script | Comma-separated list that REPLACES the default banned-phrase list entirely; every house style has a different allergy list |

**Common setups:**

Scope it to a `drafts/` folder only, leave everything else alone:
```json
"command": "COPY_SWEEP_INCLUDE=drafts/ python3 ~/.claude/hooks/copy_sweep.py"
```

Solo-voice writer who wants `I` enforced too:
```json
"command": "COPY_SWEEP_CHECKS=em_dash,straight_quote,title_case,banned_phrase,throat_clearing,summary_crutch,we_pronoun python3 ~/.claude/hooks/copy_sweep.py"
```

Your own banned-phrase list instead of the default:
```json
"command": "COPY_SWEEP_BANNED_PHRASES='revolutionize,paradigm shift,at the end of the day' python3 ~/.claude/hooks/copy_sweep.py"
```

## Semantic checks: off by default, read this first

`vague_pronoun`, `rule_of_three`, and `pontificating` catch real AI tells that a fixed pattern
genuinely cannot:

- **`vague_pronoun`**: "this" or "that" standing in for a specific noun the reader has to
  reconstruct, with no clear antecedent nearby.
- **`rule_of_three`**: a list of exactly three items sharing identical grammatical shape
  (noun-noun-noun, verb-verb-verb) with no variation.
- **`pontificating`**: a long preamble or throat-clearing before the actual point, instead of
  getting to the substance directly.

They're off by default because turning them on is a real tradeoff, not just "more rules":

- **Nondeterministic.** A regex either matches or it doesn't. These need a model to make a
  judgment call, and judgment calls vary. The same text can get a different verdict on a
  different run.
- **Slower.** Every gated write places a real network call instead of a sub-millisecond scan.
  On a flaky connection this can visibly stall the tool call.
- **Not free.** A small API cost per call. Groq's free tier covers most use; DeepSeek Flash is
  the fallback at roughly $0.14 per million tokens either way. Cheap, but not zero like the
  regex checks above.

They're **fail-open** by design: any model error, timeout, or unparseable response means the
check silently produces nothing rather than blocking your write over a flaky API. Worst case,
they just don't catch anything that round; they never turn a working session into a stuck one.

**To turn them on**, list them explicitly in `COPY_SWEEP_CHECKS`:
```json
"command": "COPY_SWEEP_CHECKS=em_dash,straight_quote,title_case,banned_phrase,throat_clearing,summary_crutch,vague_pronoun,rule_of_three,pontificating python3 ~/.claude/hooks/copy_sweep.py"
```

Needs `GROQ_API_KEY` and/or `DEEPSEEK_API_KEY` in the environment (see the main README's [Model
setup](../../README.md#model-setup) section) and the `requests` package (`pip install requests`).
No key set means these checks silently no-op, same as a model error.

## Why a hook and not a skill

A skill needs to be invoked: you have to remember to run `/clean-up-my-copy` after the fact, on
the whole file, hoping you catch everything. A hook fires on the exact write that would have
introduced the problem, catches it in a few lines instead of a whole document, and Claude fixes
it as a two-second inline correction instead of a separate pass. The cleanup pass this replaces
never has to exist.

## Key principles

- **Prevent, don't proofread.** Block the bad write before it happens, not after.
- **Deterministic by default, model-graded is opt-in.** The default checks are regex: free,
  instant, always-consistent. Semantic judgment is a real tradeoff (see above), never silently on.
- **Budgets, not blanket bans, where a blanket ban is wrong.** A single well-placed em dash in a
  long piece isn't the tell; careless or repeated use is. The check reflects that.
- **On by default, off by one flag.** `SKIP_COPY_SWEEP=1` for the rare intentional exception; no
  config file to maintain for the common case.
- **Scoped to prose, not code.** Fenced code blocks are always exempt from every check.
