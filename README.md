# Claude Code operator skills

Skills I built to run my own Claude Code setup, not a generic starter pack, so if a rule in here
reads oddly specific, that's because a specific thing broke and this is how I fixed it.

Six problems these solve:

1. **You're paying premium-model prices for work a free model handles just as well.** Groq, DeepSeek, Gemini, and Ollama exist. Use them. Claude should synthesize, not research, extract, or critique.
2. **You're in flow and there's a smart next move right here: you can feel it but can't quite see it.** This skill looks at what you just built, what it unlocked, and surfaces what compounds it.
3. **Your AI-built product has quality problems it can't see.** Claude wrote the code, copy, and architecture. It can't audit its own output across UX, security, performance, or any of 13 other dimensions. You need expert lenses that don't know your intentions.
4. **A weekly Claude subscription resets whether you used it or not, and nobody's driving it on a Saturday.** That's quota gone for nothing, week after week, until something else takes the wheel.
5. **Every draft has an em dash, a straight quote, or a Title Case heading in it, and you catch it after the fact, if you catch it at all.** `copy-sweep` blocks the write before the tell ever lands, instead of proofreading for it later (this README had 55 in the intro alone before I ran the tool on itself, which is how I know the problem is real).
6. **You're running two Claude sessions that need to talk to each other, and coordinating them means pasting a prompt from one terminal into the next by hand, all night.** `qq-mailbox` gives them a shared inbox instead: append-only, no locks needed, nothing to clobber.

Six skills below, one for each of these problems: five cover a single session end to end, before you build through every week without you, and the sixth is for the moment there's more than one session running at once.

> [!NOTE]
> `copy-sweep` is a hook, not a command, and installs differently; see its own section below. `qq-mailbox` is the newest of the six and the only one built for coordinating more than one session at a time.

---

## Skills

| Command | What it does | Result |
|---------|-------------|--------|
| `/qq-externalize` | Routes research, extraction, critique, and adversarial review to free models. Claude synthesizes only. | Free models handle 70%+ of non-synthesis work |
| `/qq-smart-next-move` | When you're in flow and there's a sense of more here: surfaces the smart next move before momentum carries you somewhere obvious. | Compounds good sessions instead of wasting them |
| `/qq-audit` | Master orchestrator for 255 expert-persona audit frameworks across 13 quality domains. Smart-routes to the right domains in the right order. | SUS 57.5 → 92.5 across 3 rounds on a production app |
| `/qq-weekend-burn` | Stands up a recurring schedule that fires itself every week and burns your quota on real work, one finished thing at a time. | A weekly cadence that installs once and runs itself forever |
| `copy-sweep` (hook, not a command) | Blocks em dashes, straight quotes, and Title Case headings before they land in a file. Fires automatically on every Write/Edit. | AI-tell punctuation caught at write time, not cleaned up after |
| `qq-mailbox` (import, not a command) | Coordination primitive for two or more concurrent Claude sessions handing work back and forth: a build session and an overseer, a headless keepalive and its live counterpart. Append-only JSONL, atomic cursor, nothing to lock. | A session drops a message and moves on; the other picks it up on its own schedule, no pasted context, no clobbered state |

> [!TIP]
> New here? Start with `/qq-smart-next-move`. Zero setup, just install and use. `/qq-externalize` has the most friction of the four above since it requires at least one external model account.

---

## Install

Easiest: tell Claude to do it.

```
Install the skills from https://github.com/lee-fuhr/claude-operator-skills
```

Claude will read this file and walk you through the rest. Or manually:

```bash
git clone https://github.com/lee-fuhr/claude-operator-skills.git
cd claude-operator-skills

cp -r skills/qq-externalize skills/qq-smart-next-move skills/qq-audit-master skills/weekend-burn skills/keepalive skills/qq-mailbox ~/.claude/skills/
cp commands/qq-externalize.md commands/qq-smart-next-move.md commands/qq-audit.md commands/qq-weekend-burn.md ~/.claude/commands/
```

`keepalive` and `qq-mailbox` have no `commands/*.md` of their own. `keepalive` is the mechanism `/qq-weekend-burn` runs on under the hood; `qq-mailbox` is a Python import (`from mailbox import send, check`), not a slash command. Both just need to be present in `~/.claude/skills/` alongside the rest.

**`copy-sweep` is a hook, not a skill.** It doesn't go in `~/.claude/skills/` at all, and there's
no command to copy. See its own section below for the two-step install (copy the script, add one
block to `settings.json`).

**For `/qq-audit`:** The 255 domain frameworks live in [audit-framework](https://github.com/lee-fuhr/audit-framework). Install them too:

```bash
git clone https://github.com/lee-fuhr/audit-framework.git
cp -r audit-framework/skills/qq-audit-* ~/.claude/skills/
cp audit-framework/commands/qq-audit-*.md ~/.claude/commands/
```

Restart Claude Code after copying.

> [!NOTE]
> If your skills directory is `~/.agents/skills/` rather than `~/.claude/skills/`, adapt the paths above.

---

## Model setup

`/qq-externalize` routes to free/cheap models. You need at least one; Groq is the easiest start.

### Groq

**Cost:** Free, 14,400 calls/day  
**Best for:** Research, extraction, summarization, fast first pass  
**Model:** Llama 3.3 70B

Not Elon's Grok. The other one, spelled differently, with 14,400 free calls a day. Take the free compute.

```bash
pip install groq
export GROQ_API_KEY=gsk_...   # console.groq.com → API Keys
```

### Cerebras

**Cost:** Free, 1M tokens/day  
**Best for:** Third adversarial voice, biggest free model available  
**Model:** Qwen 3 235B

Wafer-scale hardware, absurdly fast, and the largest model you can call for free. OpenAI-compatible API.

```bash
pip install openai
export CEREBRAS_API_KEY=...   # cloud.cerebras.ai → API Keys
```

### DeepSeek

**Cost:** ~$0.14/1M input tokens, effectively free  
**Best for:** Structured JSON output, detailed multi-step analysis, the fallback that never rate-limits  
**Model:** DeepSeek V4 Flash

Chinese research lab, best-in-class structured output, costs almost nothing. It's a secret weapon.

```bash
pip install openai   # DeepSeek uses the OpenAI-compatible API
export DEEPSEEK_API_KEY=sk-...   # platform.deepseek.com → API keys
```

### Gemini

**Cost:** Free via Google auth  
**Best for:** Large context (1M tokens), second opinions, alternative framing  
**Model:** Gemini 2.0 Flash

The best free option when you need a different perspective or a massive context window.

**Option A (API key):**
```bash
pip install google-generativeai
export GEMINI_API_KEY=...   # aistudio.google.com → Get API key
```

**Option B (CLI, no key needed):**
```bash
npm install -g @google/gemini-cli && gemini auth
```

### Ollama

**Cost:** Free, runs on your hardware  
**Best for:** Private data, anything you don't want leaving your machine  
**Model:** Your choice

```bash
# Download at ollama.ai, then:
ollama pull llama3.2
```

No API key. No rate limits. Nothing leaves your machine.

---

## qq-externalize

**The problem:** You ask Claude to research a topic, summarize a document, critique a plan, give a second opinion. Claude does it, and bills your subscription. Groq would have done it free.

This skill audits the current task, routes everything externalizable to a free model, and flags anything Claude did that it shouldn't have. In adversarial mode, it runs your plan through Groq (first-principles critique) + Gemini (alternative framing), then has Claude synthesize only the criticisms that survive.

### Commands

```
/qq-externalize              — audit current task, produce routing plan, execute
/qq-externalize [task]       — route a specific task to the right free model
/qq-externalize adversarial  — cross-model adversarial pass on what's in context
/qq-externalize help         — print command list only
```

### What it produces

```
ROUTING PLAN
============
EXTERNALIZE (free/cheap):
  - Research Stripe API rate limits → Groq (fact-finding, no judgment needed)
  - Summarize this 8,000-word spec → Groq (extraction)
  - Critique the architecture plan → Groq + Gemini (adversarial)

KEEP (Claude only):
  - Synthesize critique outputs → Sonnet (judgment required)
  - Write the implementation → Sonnet (multi-file code)

EXTERNALIZATION SCORECARD
=========================
Externalized: 3 subtasks → Groq ×2, Gemini ×1
Kept in Claude: 2 subtasks (justified)
Claude work that should have been externalized: 0
```

### Model routing card

| Task | Route to | Why |
|------|---------|-----|
| Research, fact-finding | Groq (Llama 3.3 70B) | Free, 128K context, fastest |
| Extraction, classification | Groq | Free, structured output |
| Summarization | Groq | Free, reliable |
| Structured JSON, detailed analysis | DeepSeek V3 | Best-in-class structured output, near-free |
| Critique, plan stress-test | Groq + Gemini | Cross-model divergence = real adversarial pressure |
| Second opinion, alternative framing | DeepSeek or Gemini | Different training = different blind spots |
| Large context (>100K tokens) | Gemini | 1M token context window |
| Private data, simple transforms | Ollama | Local, nothing leaves your machine |
| Synthesis, multi-file code | Claude | Worth paying for |
| Irreversible decisions | Claude Opus | Worth paying for |

> [!NOTE]
> The invocation patterns in Step 2 of the skill file use generic API calls. Adapt them to match whatever client libraries you've installed.

---

## qq-smart-next-move

**The feeling:** Things are clicking. You're in flow. There's a sense that you're not done: there's a smart next move right here you don't want to miss.

This skill captures that. It looks at what just happened, what it unlocked, and asks: what's the thing that compounds this? Not “which of my backlog items is highest priority”: that's a different question. This is “I'm cooking right now, what's the smart thing to do next?”

### Commands

```
/qq-smart-next-move           — infer from session context, surface the options
/qq-smart-next-move [context] — provide explicit context for what just finished
```

### What it produces

> **Based on what we just built and the data we have, here are the moves I see:**
>
> **A. Wire up the observability hook.** Enforcement exists but there's no runtime evidence it's working. Five minutes to confirm vs. hours debugging in production.
> - Data point: zero events in log after three sessions
> - Risk: low; hook either fires or it doesn't
>
> **B. Wire the scorecard into the morning digest.** Invisible unless surfaced daily. High leverage: you see it every morning without thinking about it.
> - Data point: digest is checked daily; dashboard is only checked when something feels wrong
> - Risk: schema change could break existing sections
>
> **Recommendation:** A + B together (15 min each).
>
> **The question I'd want answered first:** Is the guard actually blocking anything?

### The five lenses

1. **What did we just build?** Specific deliverables, surprises, assumptions validated or broken
2. **What did this unlock?** What's trivially easy now that was hard before?
3. **What risk did we just create?** Maintenance burden, dependencies, debt introduced
4. **What compounds this?** The move that makes what we just built more valuable, right now
5. **Does this move the needle?** Revenue proximity, client value, building for the business vs. building because it's interesting

### Key principles

- Data over theory: if a number can be checked, it checks before opining
- Capitalize on momentum: what you just built is context; use it
- Revenue proximity matters: all else equal, the thing closer to money wins
- Combine, don't choose: options are presented as combinable, not mutually exclusive

---

## qq-audit

**The problem:** Claude wrote your code. It can't objectively audit its own output: it knows what the code is supposed to do, what the copy is trying to say, how the architecture was intended. You need expert lenses that don't know your intentions, applied domain by domain.

This is the master command for [audit-framework](https://github.com/lee-fuhr/audit-framework): 255 expert-persona frameworks across 13 quality dimensions. It analyzes your project, picks the right domains in the right order, and runs each serially, fixing issues before moving to the next domain so fixes compound.

### Commands

```
/qq-audit                   — smart routing: picks the right domains for your project
/qq-audit [domains]         — run specific domains (e.g. "ux + copy")
/qq-audit pre-launch        — 8 domains before going live
/qq-audit quick             — UX + Visual + Copy fast check
/qq-audit post-build        — UX + Visual + Copy + Frontend after a feature
/qq-audit deep              — all 13 domains
/qq-audit list              — show all 13 domains with framework counts
```

### The 13 domains

| Domain | Command | Frameworks | Expert lens |
|--------|---------|-----------|-------------|
| UX | `/qq-audit-ux` | 20 | Does the brain work well with this? |
| Product | `/qq-audit-product` | 20 | Is this the right product? |
| Visual UI | `/qq-audit-visual` | 22 | Does this look professional? |
| Content/Copy | `/qq-audit-copy` | 22 | Is the writing good? |
| Frontend | `/qq-audit-frontend` | 22 | Is the code well-built? |
| Performance | `/qq-audit-performance` | 22 | Is it fast? |
| Security | `/qq-audit-security` | 23 | Is it safe? |
| QA/Testing | `/qq-audit-testing` | 22 | Is it tested? |
| Backend/API | `/qq-audit-backend` | 22 | Is the server-side solid? |
| SEO | `/qq-audit-seo` | 15 | Can people find it? |
| DevOps | `/qq-audit-devops` | 15 | Is it deployable and resilient? |
| Data Quality | `/qq-audit-data` | 15 | Is the data trustworthy? |
| Compliance | `/qq-audit-compliance` | 15 | Is it legally sound? |
| **Total** | | **255** | |

### Convergence protocol

Each domain runs up to 3 rounds. Round 1 finds ~60% of issues. Round 2 finds 25% more: fixes from round 1 expose new problems. Round 3 catches the last 10–15%. Move on when a domain hits 9.5/10 or exhausts 3 rounds.

```
UX: Round 1 = 7.2 → Round 2 = 8.8 → Round 3 = 9.6 ✓ — moving to Visual
Visual: Round 1 = 8.1 → Round 2 = 9.7 ✓ — moving to Copy
```

### Results

Measured on a production Next.js dashboard (170+ components, UX domain):

| | Score | Fixes |
|-|-------|-------|
| Baseline | SUS 57.5 | 0 |
| After round 1 | SUS 77.5 | 100+ |
| After round 2 | SUS 90.0 | 45 |
| After round 3 | SUS 92.5 | 8 |
| Ceiling | ~93–95 | Remaining issues are product decisions |

### Domain sequencing

No point auditing visual design when UX is broken: you'll redesign those screens anyway. Domains run in dependency order:

```
Product → UX → Visual → Copy → Frontend → Backend → Performance
       → Security → Testing → SEO → DevOps → Data → Compliance
```

---

## qq-weekend-burn

**The value:** A Claude subscription resets its quota every week whether you used it or not. Driving a long autonomous session yourself, every single Saturday, forever, isn't something you actually do by hand. This turns “burn the quota on real work” from a thing you meant to get around to into a standing decision you make exactly once.

**The benefit:** Install it and walk away. It fires itself inside a recurring window you choose (Friday evening through Sunday night, say), works one real capability at a time to an actual finished state, and stands down the moment you're back at the keyboard. You come back Monday to shipped things, not a pile of half-touched projects and a wasted week of quota.

**The features:**

- A recurring calendar schedule that fires itself, every week, with no re-invocation: install once
- A finish-discipline doctrine: one project worked to a real terminal state before the next starts, so a long unattended run ships finished things instead of a dozen started ones
- An intake standard: a fuzzy backlog item is never dropped; it's tagged `needs-definition` and gets your single most capable model for exactly one job (writing a clear definition of done), then drops straight back to normal cheap-model execution
- A kill switch where the word you write decides the failure mode: `PAUSE` self-heals after a TTL, `STOP` holds until you clear it, anything else gets flagged loudly instead of silently obeyed
- Built on `keepalive` (also in this repo) for the actual session-survival mechanism: the fresh-process-per-fire trick that means a 5-hour cap, a closed laptop, or a reboot never stops the schedule. You don't invoke `keepalive` yourself; `/qq-weekend-burn` does it for you.

### Commands

```
/qq-weekend-burn   — stand up a new weekend-burn lane: write the governing doc, seed the
                      backlog, wire the recurring window function, and hand you the
                      one-paste install block for the actual schedule
```

### How to invoke it

Deterministic, not a phrase Claude has to guess at: run `/qq-weekend-burn`. Claude scaffolds every file the schedule needs (the governing doc, the backlog, the window function, the state) and hands you a one-paste block to install the actual recurring trigger yourself. That last step is always yours: the platform's safety classifier blocks an agent installing its own unattended loop, on purpose.

### Key principles

- Sequence, not a cap: a productive burn finishes many things, just one at a time
- “The code ran” is not done; done is the observable finish line, verified
- A human-gated step doesn't block the run: stage it, mark it, move to the next project
- Unused quota at reset is wasted, not saved

---

## copy-sweep

**The problem:** AI-tell punctuation and phrasing creep into drafts one write at a time. The
usual fix is a cleanup sweep after the fact: catch what you can, hope you got it all.
copy-sweep skips the sweep: the write fails before the tell ever exists.

`copy-sweep` is a `PreToolUse` hook. It has no command because you never invoke it; it fires on
every `Write`/`Edit`/`MultiEdit` to a matching file, scans the new content before it's saved, and
blocks the write if it finds a violation, and Claude gets a line-numbered list of exactly what's
wrong and fixes it inline, same turn, before the bad version ever exists on disk. Which is a good
moment to admit that I built this, then ran it on the repo you're reading, and found 272 em
dashes I'd apparently written myself without noticing across every file in here, so any rule in
this doc that sounds strict is strict because I've already been on the wrong end of it.

### What it catches

Deterministic, on by default, zero model calls:

| Check | Catches |
|-------|---------|
| `em_dash` | A budget, not a ban: 0 allowed under 400 words, 1 allowed above it, and that one still has to earn its place |
| `straight_quote` | `"` where a curly quote `“ ”` belongs |
| `title_case` | `## The Big New Feature Launch` instead of `## The big new feature launch` |
| `banned_phrase` | Corporate-speak: leverage, synergy, touch base, cutting-edge, excited to announce, and more |
| `throat_clearing` | “As you know,” “We're excited to announce” |
| `summary_crutch` | “Bottom line:”, “Key takeaways:” |
| `we_pronoun` | Off by default: a bare `We` in solo-voice copy, opt in if you write alone |

Semantic, off by default, needs a model call: `vague_pronoun`, `rule_of_three`, `pontificating`,
`staccato_cadence`.
These catch patterns a regex genuinely can't; full explanation of the tradeoff (nondeterminism,
latency, small API cost, fail-open by design) is in [the skill's own
doc](skills/copy-sweep/SKILL.md#semantic-checks-off-by-default-read-this-first).

### Install

**Easiest, just tell Claude:**

> Install copy-sweep from https://github.com/lee-fuhr/claude-operator-skills and walk me through my config options.

Claude does the file copy and the `settings.json` edit itself, then asks a handful of plain
questions instead of handing you env var names to memorize: scope it to one folder or the
whole repo, catch stray “We”s or not, turn on the deeper AI-graded checks or skip them, what
counts as “long” for you. Full walkthrough script for Claude to follow is in [the skill's own
doc](skills/copy-sweep/SKILL.md#install-just-tell-claude).

**Manual, if you'd rather do it yourself:**

```bash
mkdir -p ~/.claude/hooks
cp skills/copy-sweep/hooks/copy_sweep.py ~/.claude/hooks/copy_sweep.py
chmod +x ~/.claude/hooks/copy_sweep.py
```

Then add this to `~/.claude/settings.json` (or `.claude/settings.json` for one repo only):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          { "type": "command", "command": "python3 ~/.claude/hooks/copy_sweep.py" }
        ]
      }
    ]
  }
}
```

Restart Claude Code. Full config reference (scoping to a `drafts/` folder, turning `we_pronoun`
on, the one-off bypass flag) is in `skills/copy-sweep/SKILL.md`.

---

## qq-mailbox

**The problem:** Two Claude sessions need to hand work back and forth, an overseer that architects and a build session that implements, say, and there's no channel between them that survives either one restarting. The usual fix is pasting a prompt from one terminal into the other by hand, every handoff, all night.

This is a coordination primitive, not a command: two named roles, each appending only to the file where it's the sender, so there's nothing to collide on and nothing to lock. `check()` needs a lane directory and a role name; it finds its own unread messages, groups them by kind, and tells you what actually needs a reply.

### The two calls

```python
from mailbox import send, check

send(lane, from_role="builder", to_role="overseer", kind="design-task", msg="...")
result = check(lane, role="overseer")
# result["action_needed"] -> messages that actually need a response
```

### Key principles

- One append-only file per directed pair of roles. A role only ever writes to files where it's the sender, so two processes can never collide on the same write.
- A reply is a new message, never an edit to someone else's line. Append-only holds everywhere, no exceptions.
- Cursor state is temp-file-then-rename, never a direct write, and it's monotonic under a race: two overlapping reads can double-surface a message, never lose one.
- Role names are job titles, not model names. `builder`/`overseer` survives a model swap; `opus`/`fable` doesn't (a lesson learned by shipping the second one first, then having to explain why that was a mistake in the same session).

Full worked example, kind taxonomy, and the invariants behind each design choice are in [the skill's own doc](skills/qq-mailbox/SKILL.md).

---

## How these work together

Each skill is useful alone. Together they cover the full arc of a working session, and what happens after you close the laptop:

**Before you build**: `/qq-externalize` routes research, extraction, and critique to free models so you're not burning Claude tokens on work Groq can do for free.

**While you build**: `copy-sweep` blocks AI-tell punctuation the instant it would be written, so there's no cleanup pass later.

**After you build**: `/qq-audit` runs the quality check Claude can't run on itself. 255 expert lenses across whatever dimensions matter for your project.

**When momentum is high**, `/qq-smart-next-move` asks the question you don't stop to ask: what's the move that compounds what I just built?

**Every week, without you**: `/qq-weekend-burn` puts real work on a recurring schedule that survives caps, closed laptops, and reboots, so the quota gets spent whether or not you're at the keyboard.

```
/qq-externalize  →  build (copy-sweep guards every write)  →  /qq-audit  →  /qq-smart-next-move  →  /qq-weekend-burn
route cheaply        Claude handles synthesis only              check         what next?              recurring, unattended,
                                                                  quality                                every week
```

`qq-mailbox` sits outside this diagram on purpose: it's not a step in any one session's arc, it's what two sessions running that arc in parallel use to hand work to each other.

---

## License

MIT
