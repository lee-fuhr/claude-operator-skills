# Claude Code operator skills

Skills I built to run my own Claude Code setup, not a generic starter pack, so if a rule in here
reads oddly specific, that's because a specific thing broke and this is how I fixed it.

Eighteen problems these solve:

1. **You're paying premium-model prices for work a free model handles just as well.** Groq, DeepSeek, Gemini, and Ollama exist. Use them. Claude should synthesize, not research, extract, or critique.
2. **You're in flow and there's a smart next move right here: you can feel it but can't quite see it.** This skill looks at what you just built, what it unlocked, and surfaces what compounds it.
3. **Your AI-built product has quality problems it can't see.** Claude wrote the code, copy, and architecture. It can't audit its own output across UX, security, performance, or any of 13 other dimensions. You need expert lenses that don't know your intentions.
4. **A weekly Claude subscription resets whether you used it or not, and nobody's driving it on a Saturday.** That's quota gone for nothing, week after week, until something else takes the wheel.
5. **Every draft has an em dash, a straight quote, or a Title Case heading in it, and you catch it after the fact, if you catch it at all.** `copy-sweep` blocks the write before the tell ever lands, instead of proofreading for it later (this README had 55 in the intro alone before I ran the tool on itself, which is how I know the problem is real).
6. **Two-tier orchestration is accepted practice now, an expensive model directing cheaper ones, but nothing lets two truly separate sessions actually talk to each other.** Subagents reload their whole context on every call; `qq-mailbox` gives an overseer and a builder session a shared inbox instead, each keeping its own full context the entire time.
7. **A plan looks reasonable right up until it's half-built and the thing you forgot turns out to be load-bearing.** `ww-plan-audit` runs the gauntlet before you exit plan mode, not after: an interview, a principles read, a multi-domain audit, and a real adversarial pass from two different external models, so the wisdom gets front-loaded instead of discovered mid-build.
8. **“Done” gets said a lot more often than it's actually true.** A button changes color, nothing saved, nothing sent, nobody downstream ever sees the change, and nobody notices for three weeks. `ww-rule15` forces a stated outcome, a traced action chain, and evidence from outside your own head before the word “done” gets to land.
9. **You're about to run `npx skills add` on something a stranger wrote, and the only way to know what it actually does is to read a markdown file that's about to be dropped straight into your agent's context.** `ww-skill-auditor` reads it first: pattern scans for prompt injection, credential theft, and remote code execution, plus a cheap-model second pass, and hands back SAFE, CAUTION, UNSAFE, or UNKNOWN before you trust it.
10. **Step away for six hours with a real work queue, and everything after that moment is a gamble.** An agent that asks permission on every call burns the night waiting; one that never stops might push to main or delete something. `ww-overnight-runner` is the actual contract: what to decide alone, what to always stop for, and what a clean morning handoff looks like.
11. **An unattended session left to its own habits drifts back to the expensive model, one convenient call at a time, until the weekly quota is gone and you didn't even get that much done.** `qq-go-afk-lean` fixes the token source, not the pace: everything routine goes to Groq, Cerebras, DeepSeek, or Ollama first, and Claude gets spent only on synthesis, voice, and judgment calls nothing else can make.
12. **Another agent, or another one of your own sessions, reports “done,” and reading the transcript to check would take as long as doing the work yourself.** `ww-agent-watchdog` watches a session, PR, or transcript to completion, reconstructs what was actually asked, and checks the evidence instead of trusting the summary.
13. **A monitoring dashboard gets reached for at the worst possible moment, someone thinks something's wrong and they're often already stressed.** `ww-dashboard-ux` is a set of iron laws, three-part error messages, status that never relies on color alone, every metric shows its age, built by proposing rules against a real production dashboard, then trying to kill every one of them.
14. **A LinkedIn chart made with default matplotlib styling reads as a data science notebook, not something worth a thumb pausing on mid-scroll.** `qq-infoviz` renders HTML and CSS through Playwright instead: big serif numbers, a fixed brand system, five chart layouts, and a rule that the data itself, not the decoration, is the thing that has to be beautiful.
15. **Notion's block editor doesn't speak standard markdown, and it fails quietly.** A pipe table just doesn't render, an escaped `\n` shows up as a literal backslash-n, and you don't find out until you look at the live page. `ww-notion-docs` documents Notion's actual markdown flavor, plus the comments-based review workflow that makes a page a real collaboration surface instead of a one-way publish target.
16. **The Notion API will tell you an edit succeeded when it silently dropped half your patches, and tell you a comment anchor is unique when a phrase three paragraphs down makes it ambiguous.** `ww-notion-proposal-hardener` documents the specific ways it misleads you, and the checks that catch it before you call a revision round done.
17. **The Google Docs API defaults to Arial and Google's own spacing, and a document that's supposed to look like yours instead looks like everyone else's.** `ww-google-docs` is the repeatable pattern (copy a styled template, or push named-style requests explicitly) plus the read-back step that actually confirms the style landed.
18. **Every AI model defaults to straight typewriter quotes, and a straight quote in a paragraph of running prose is something any editor spots in about half a second.** `ww-smart-quote-fixer` converts them deterministically, including the genuinely hard cases (`'90s`, `6'2"`, nested quotes) a naive find-and-replace gets wrong, and leaves code blocks alone.

Eighteen skills below. The first six cover a single session end to end, before you build through every week without you, and `qq-mailbox` was the first built for more than one session running at once. The other twelve came later: plan-quality gates, an unattended-work contract, a security check before installing someone else's skill, dashboard and chart output, and a few Notion/Docs specifics worth not re-learning by hand.

> [!NOTE]
> `copy-sweep` is a hook, not a command, and installs differently; see its own section below. `qq-mailbox` is still the only one built for coordinating more than one session at a time. Most of the eighteen are `qq-`/`ww-` skills that load themselves automatically from context rather than waiting on a typed command; see each skill's own section for how it's actually triggered.

---

## Skills

| Command | What it does | Result |
|---------|-------------|--------|
| `/qq-externalize` | Keeps your Claude subscription for judgment calls only. Routes research, extraction, critique, and adversarial review to free models automatically. | Free models handle 70%+ of non-synthesis work |
| `/qq-smart-next-move` | When you're in flow and there's a sense of more here: surfaces the smart next move before momentum carries you somewhere obvious. | Compounds good sessions instead of wasting them |
| `/qq-audit` | Gets outside eyes on your code and copy across 255 expert lenses in 13 quality domains, since Claude can't judge its own work fairly. Smart-routes to the right domains in the right order. | SUS 57.5 → 92.5 across 3 rounds on a production app |
| `/qq-weekend-burn` | Stands up a recurring schedule that fires itself every week and burns your quota on real work, one finished thing at a time. | A weekly cadence that installs once and runs itself forever |
| `copy-sweep` (hook, not a command) | Blocks em dashes, straight quotes, and Title Case headings before they land in a file. Fires automatically on every Write/Edit. | AI-tell punctuation caught at write time, not cleaned up after |
| `qq-mailbox` (import, not a command) | Lets two or more concurrent Claude sessions hand work back and forth on their own: a build session and an overseer, a headless keepalive and its live counterpart. Append-only JSONL, atomic cursor, nothing to lock. | A session drops a message and moves on; the other picks it up on its own schedule, no pasted context, no clobbered state |
| `ww-plan-audit` (loads automatically before exiting plan mode) | Runs a ten-dimension gauntlet on any multi-phase plan: an interview, a principles read, a multi-domain audit, and two external models arguing with it, before you build anything. | Wisdom that would've surfaced three weeks into the build shows up before the first commit |
| `ww-rule15` (say “is this actually done”, or run it before any DONE claim) | Forces a stated outcome, a traced action chain, and evidence from outside your own head before “done” gets to land. | A PASS without external evidence auto-downgrades to PARTIAL, so cosmetic done stops passing as done |
| `ww-skill-auditor` (`python3 audit.py "<author>/<repo>/<skill>"`, run before any third-party install) | Pattern-scans a SKILL.md for prompt injection, credential theft, and remote code execution, then runs a cheap-model second pass. | A specific, evidenced SAFE/CAUTION/UNSAFE/UNKNOWN verdict before a stranger's markdown enters your agent's context |
| `ww-overnight-runner` (loads on “run overnight” or a 6+ hour queue) | Sets the actual contract for unattended work: what to decide alone, what to always stop for, how to park non-blocking questions, and what a clean handoff looks like. | A night of real progress and a results file that tells the truth, not a guess reconstructed from a stale task list |
| `qq-go-afk-lean` (say “go lean” or “squeeze the quota”) | Fixes the token source for an autonomous or live session: routine work goes to Groq, Cerebras, DeepSeek, or Ollama first; Claude spends only on synthesis, voice, and judgment. | More total work finished per Claude token, with every step labeled by which model handled it |
| `ww-agent-watchdog` (point it at a session ID, PR, branch, or transcript) | Watches another agent's work to a terminal state, reconstructs what was actually asked, and checks the diff, tests, and CI instead of trusting the “done” summary. | A gap report you can act on, or narrow fixes once you've authorized repair |
| `ww-dashboard-ux` (loads when building, reviewing, or auditing a dashboard) | Eight iron laws (three-part error messages, status that never relies on color alone, every metric shows its age) plus ten expert-lens audit frameworks. | A dashboard that survives someone reaching for it stressed, mid-incident |
| `qq-infoviz` (say “make me a chart” or “LinkedIn image”) | Renders a branded 1200x627 chart from HTML and CSS through Playwright: bar charts, stat grids, newspaper layouts, five formats total. | A chart built to stop a scroll, not a matplotlib default nobody clicks past |
| `ww-notion-docs` (loads before any Notion content work) | Documents Notion's actual markdown flavor (HTML tables, not pipes; `<empty-block/>` for spacing) plus the comments-based review workflow. | Content that renders right the first time, and a review cycle the reviewer can actually follow |
| `ww-notion-proposal-hardener` (loads when iterating a reviewed Notion doc) | Documents the three ways the Notion API misleads you, silent patch skips, greedy comment anchors, discussion spans blocking edits, and the check for each one. | A revision round that actually lands every patch, verified, not just reported as success |
| `ww-google-docs` (loads before any Google Docs API work) | Two reliable methods, copy a styled template, or explicit named-style requests, for matching your house style instead of Google's Arial default, plus a mandatory read-back check. | A doc that actually looks like yours, confirmed, not just an API response that claims success |
| `ww-smart-quote-fixer` (loads automatically for editorial prose) | Converts straight quotes to proper typographic quotes, including the hard cases: decades, nested quotes, feet-and-inches, while leaving code blocks alone. | Copy that doesn't announce itself as machine-written from the punctuation alone |

> [!TIP]
> New here? Start with `/qq-smart-next-move`. Zero setup, just install and use. `/qq-externalize` has the most friction of the four slash commands above since it requires at least one external model account.

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

Chinese research lab, cleaner structured output than most, costs almost nothing. It's a secret weapon.

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

**The problem:** Free models are genuinely good enough now for research, extraction, and critique, that's not really in dispute anymore. What's still happening is Claude does that work anyway, out of habit, and every one of those calls bills your subscription for something a free model would've handled the same way for nothing.

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
| Structured JSON, detailed analysis | DeepSeek V3 | Clean structured output, near-free |
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

**The feeling:** Things are clicking, you're in flow, and there's a sense that you're not actually done, there's a smart next move sitting right here and you don't want to lose the thread finding it.

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
> **B. Wire the scorecard into the morning digest.** Invisible unless surfaced daily. Small effort, big payoff: you see it every morning without thinking about it.
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

**The problem:** Claude wrote your code, your copy, and your architecture, which is exactly why it can't audit any of it fairly, it already believes its own intentions were the right call. You need lenses that don't know what you meant to build, only what actually got built, applied domain by domain.

This is the master command for [audit-framework](https://github.com/lee-fuhr/audit-framework): 255 expert lenses across 13 quality dimensions. It analyzes your project, picks the right domains in the right order, and runs each serially, fixing issues before moving to the next domain so fixes compound.

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

**The value:** A Claude subscription resets its quota every week whether you used it or not, that part everyone already knows. What doesn't happen on its own is someone actually sitting down and driving a long autonomous session by hand, every single Saturday, forever. `qq-weekend-burn` turns “put the unused quota to work” from a thing you keep meaning to get around to into a standing decision you make exactly once.

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

**The problem:** Nobody sits down meaning to write an em dash or a straight quote into a draft, it
just creeps in, one write at a time, until the tells are everywhere and you've stopped noticing
them. The usual fix is a cleanup pass after the fact: catch what you can, hope you got it all.
copy-sweep skips the pass entirely: the write fails before the tell ever exists.

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

**The problem:** Running an expensive model as the orchestrator over cheaper builder models is accepted practice at this point, nobody needs convincing that the two-tier setup is right. What's still unsolved is how. Subagents look like the obvious way to build it, until you notice they reload their whole context on every single call, burning tokens and losing the thread each time. The real fix is two genuinely separate sessions, an overseer and a builder, each holding its own full context the whole way through. But then you hit the actual wall: nothing lets two independent Claude Code sessions talk to each other. The usual workaround is pasting a prompt from one terminal into the other by hand, every handoff, all night.

This isn't a command, it's a Python import: two named roles, each appending only to the file where it's the sender, so there's nothing to collide on and nothing to lock. `check()` needs a lane directory and a role name; it finds its own unread messages, groups them by kind, and tells you what actually needs a reply.

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

## ww-plan-audit

**The problem:** A plan reads fine in the moment you write it. The gap you didn't think to ask about, the assumption you didn't know you were making, the domain you didn't consider: none of that shows up until you're three milestones in and it's expensive to unwind. Auditing code after it's built catches bugs. Auditing a plan before it's built catches the thing that would have made the whole build go differently.

This is the full gauntlet: ten passes over a plan before it ever becomes code. An interview surfaces what's in your head that the plan itself doesn't capture. A principles read checks it against your own standards. A multi-domain audit runs product, UX, security, and ten more lenses against the plan, not the code, so the wisdom gets front-loaded instead of discovered mid-build. A steelman routes the plan through two different external models for a real adversarial pass; Claude synthesizes, it never grades its own homework. A pre-mortem asks what kills this in six months. It converges, round after round, until nothing new survives, capped at three rounds so it can't loop forever.

### Key principles

- Interview first, before mechanical auditing starts: the best plans fail because they solved the wrong problem, not because they had technical gaps
- Domain audits on a plan are prophylactic, not corrective: “here are the accessibility patterns to follow,” not a bug report
- Every criticism gets steelmanned; roughly half of “critical issues” from a first pass are fear-driven and don't survive
- Convergence, not a single pass: one audit round finds about 60% of issues, the loop is what catches the rest
- The plan's owner stays in control throughout; findings get presented, never silently applied

---

## ww-rule15

**The problem:** “Done” gets said more often than it's true. A button changes color, nothing saved, nothing sent, nobody downstream ever sees the change, and nobody notices for three weeks, because the code path exists even though the outcome never happened.

Rule 15 forces a stated outcome in one sentence before anything else happens, traces the actual action chain from trigger to outcome, and checks the feedback loop (success state, error state, loading state) on every mutation. Effort scales with what changed: touch more than one file and the floor rises to checking integration points; touch a hook or a shared config and the floor is a real behavioral test, not “the file exists.” And the implementer's own reasoning never counts as the check: any PASS verdict at medium effort or higher needs evidence from outside the person who built it, pasted command output, a grep, a full test run, not “I expect it would return...”. A PASS without that evidence auto-downgrades to PARTIAL.

### Key principles

- The intended outcome is a sentence, stated first, never inferred after the fact
- Every mutation needs a success state, an error state, and a loading state, or it's PARTIAL
- Effort floors scale with blast radius and can't be self-downgraded by the person doing the work
- External evidence is mandatory at medium effort or higher; the implementer's own word is not evidence
- “Works in the code” but doesn't deliver the outcome is COSMETIC, not done

---

## ww-skill-auditor

**The problem:** A skill you install is a markdown file, sometimes a script too, that gets read straight into your agent's context and sometimes executed. It can ask your agent to read your `.env` file, pipe a remote script into `bash`, install a scheduled job, or quietly try to override its own instructions, and none of that is obvious from skimming the description on GitHub.

`ww-skill-auditor` reads the actual SKILL.md before it touches your system. Deterministic regex scans catch the known attack shapes: prompt-injection overrides, credential exfiltration, `curl | bash`, reverse shells, hook or LaunchAgent installation. A cheap-model second pass (Cerebras, free tier) catches paraphrased versions the regex misses. A short known-good author list lowers the bar for publishers you already trust; everyone else defaults to CAUTION even at zero pattern hits.

### Commands

```bash
python3 audit.py "<author>/<repo>/<skill>"          # npx skills add spec
python3 audit.py "https://github.com/.../SKILL.md"  # raw, or blob/tree URL
python3 audit.py --file /path/to/SKILL.md           # local file
```

| Exit code | Verdict | Meaning |
|-----:|---------|---------|
| 0 | SAFE | No signals, known-good author. Proceed. |
| 1 | CAUTION | Low-risk findings, or an unknown author. Review before approving. |
| 2 | UNSAFE | High-risk pattern hit. Do not install. |
| 3 | UNKNOWN | Could not fetch, or inconclusive. Do not install until the source is locatable. |

### Key principles

- Severity scales with blast radius: medium for skills, high for agents and plugins, critical for hooks, since a hook runs automatically with nobody in the loop
- Pattern hits always override author reputation; a known-good author can still ship a regressed skill
- The semantic check fails open, no key means it silently skips, so a missing Cerebras key never blocks the deterministic half
- Never install on inferred consent; the verdict has to be visible to whoever approves, every time

---

## ww-overnight-runner

**The problem:** You hand off a multi-hour work queue and walk away, and everything downstream of that moment is a gamble. An agent that stops to ask permission on every judgment call burns the whole night waiting on you. An agent that never stops might quietly delete something, push to main, or send a message it shouldn't have. Neither failure announces itself until morning, and by then it's too late to redirect.

This is the actual contract, not a hope. It sets decision rules for choosing without you in the loop (reuse existing patterns, prefer reversible changes, validate small then broaden), a short list of true blockers that always stop the work (missing credentials, anything destructive or irreversible, a decision you explicitly reserved), and a place for every non-blocking question to land instead of interrupting you: a `QUESTIONS-FOR-YOU.md` file, triaged in the morning instead of pinged at 2am. Status lives on a phone-checkable surface with a three-second glance test: a health callout and a status row above the fold, nothing else. And because in-session task state doesn't survive a context compaction, the results file, not the task tracker, is the ground truth on resume.

### Key principles

- Default to non-blocking; only escalate to blocking if the wrong choice risks data loss or something irreversible
- Never delete data, send external messages, or push to main without explicitly flagging it, no exceptions
- The results file is ground truth on resume; in-session task tracking does not survive compaction
- A failed task gets one retry with a different approach, then it's logged and you move on, never a silent loop
- Silence is not a green light; an autonomous choice made without you gets logged as a decision, not buried in a diff

---

## qq-go-afk-lean

**The problem:** Left to its own habits, an autonomous or long-running session drifts back to the expensive model one convenient call at a time. Nothing forces the drift, it just happens, and by the time the weekly quota is gone you didn't get nearly as much done as the quota should have bought.

`qq-go-afk-lean` is a standing posture, not a one-off routing decision. Every unit of work defaults to the cheapest capable model: Groq or Cerebras first (free), Ollama for anything private, DeepSeek Flash as the paid anchor that essentially never rate-limits. Claude is reserved for exactly four things: final synthesis of what the cheap models produced, voice and copy (the one place cheap models genuinely damage quality instead of just costing more), irreversible or architectural judgment, and deep reasoning an external model has already demonstrably failed at, never preemptively. On a 429 or a timeout, the rule is always “try a different external model,” never “fall back to Claude to just get it done,” since that defeats the entire posture. It composes with pace, not against it: a bounded one-task-at-a-time run and a wide fan-out run are both still lean as long as the workers doing the actual work are external and Claude only judges the result.

### Key principles

- The bar to spend a Claude token is high: you have to be able to say why no external model could've done it
- Escalate to Claude only after an external model actually fails, never preemptively
- Every externalized step gets labeled with which model handled it; silence on routing is non-compliance
- Token source and pace are separate decisions; lean composes with either a bounded cadence or a wide fan-out
- Overnight, a question that needs a human never stalls the worker; it goes in a running questions file while the next unblocked unit starts immediately

---

## ww-agent-watchdog

**The problem:** An agent finishes a session and reports “done,” and you have no independent way to know if that's true. Reading the whole transcript to check takes about as long as doing the work yourself. Trusting the summary means trusting the exact thing you're trying to verify.

`ww-agent-watchdog` treats the user's original request as the source of truth, not the other agent's claim about what it did. It resolves whatever artifact you point it at, a session ID, a transcript, a PR, a branch, a pasted summary, reconstructs the real contract (the request, the constraints, the implied acceptance criteria), and checks evidence instead of prose: the actual diff, the actual test output, the actual CI state, screenshots instead of a description of a screenshot. Each finding gets classified as a gap, a bug, a verification miss, scope drift, or genuinely no issue. If you've authorized repair, it fixes narrowly, the clear gaps only, and stops rather than guessing when a fix would need a product decision or a destructive action.

### Key principles

- Evidence over claims: read the diff, run the actual command, check the actual CI state
- The user's original request is the source of truth, never the watched agent's own summary of it
- Fix narrowly when authorized; a fix that needs a product decision gets reported, not guessed at
- If authority is unclear, default to audit-only and say what you would fix

---

## ww-dashboard-ux

**The problem:** An operational dashboard gets reached for at the worst possible moment: someone thinks something might be wrong, and they're often already stressed. That's exactly when a spinner with no error state, a status dot a colorblind person can't read, or a metric with no idea how stale it is does the most damage, and dashboards built without a deliberate stance on these fail in the same handful of predictable ways, over and over.

Eight iron laws, unconditional, no “it depends.” They survived an adversarial process on purpose: several passes proposed principles against a real production dashboard, then a dedicated skeptic pass tried to kill each one, and only what stayed unconditional, falsifiable, and enforceable made the final eight.

| Iron law | The one-line test |
|---|---|
| Error messages | Says what happened, why it matters, what to do right now |
| Status indicators | Never color alone; at least two independent encodings |
| Metric age | Every stale-capable metric shows how old it is |
| Action logging | Who, when, what, outcome, on every user-initiated action |
| Modals | Close explicitly (button or Escape), never by timeout |
| Alert triage | Urgency, not subjective severity |
| Drill-down | Bounded depth, breadcrumbs, an explicit close |
| Action surfaces | Tested to a live destination, never assumed to work |

Ten expert-lens frameworks (error states, notification design, drill-down architecture, data visualization, actionability, performance perception, accessibility, temporal patterns, navigation, data provenance) sit behind the table for a full audit; run one framework for a focused pass, or all ten for a pre-launch check.

---

## qq-infoviz

**The problem:** A LinkedIn chart made with default matplotlib styling reads as a data science notebook, not something worth a thumb pausing on mid-scroll. Data-heavy posts get skipped past unless the numbers are the most visually dominant thing on the canvas, and getting there by hand, in a design tool, for every post, doesn't scale.

`qq-infoviz` renders a self-contained HTML file through Playwright at a fixed 1200x627 canvas, LinkedIn's own optimal ratio, using one converged brand system: Source Serif 4 for the numbers, Inter for the labels, a dark navy background, and a small fixed palette tinted per stat. Five chart types cover most stories: horizontal bars for ranked metrics, a stat grid for equal-weight scorecards, vertical columns for descending scale, a newspaper layout for one hero stat plus supporting context, and a quote-plus-stat strip for provocative copy backed by a number.

### Commands

```bash
python3 screenshot.py /tmp/infoviz-chart.html /tmp/chart-linkedin.png 1200 627
```

Width and height have to be passed explicitly; the script's own default is a 1800x1800 square built for a different canvas.

### Key principles

- Data is the point: exaggerated sizes, big serif numbers, minimal whitespace
- Fills go bottom-up, always; a top-down fill is treated as a defect
- Sentence-flow labels (“85% don't name a single machine they run”), not a stat stacked over a caption
- Fewer, bigger stats beat more, smaller ones: three huge numbers outperform six tiny ones
- Never guess at the data, query your own source, and never skip opening the rendered image to actually look at it

---

## ww-notion-docs

**The problem:** Notion's block editor doesn't speak standard markdown, and it fails quietly. A pipe table just doesn't render. An escaped `\n` shows up as a literal backslash-n instead of a line break. Curly braces meant to set a block color turn into visible text if they're escaped wrong. None of it throws an error. You just find out later, when you look at the live page and something's broken.

This documents Notion's actual markdown flavor (HTML `<table>` tags instead of pipes, `<callout>` tags, `{color="yellow_bg"}` for backgrounds, `<empty-block/>` for the vertical space Notion otherwise strips) plus the update patterns that keep an edit from silently failing: always fetch the page before `update_content`, since a stale `old_str` just won't match, and default to `update_content` over `replace_content`, since a full rewrite destroys whatever a reviewer already left on the page. The other half is the comments-based review cycle itself: comments aren't optional decoration, they're the only way a reviewer can see what changed without re-reading the whole document, so every content update gets one, anchored to the exact text it touched.

### Key principles

- Fetch before you edit, always; a stale `old_str` fails silently, not loudly
- Default to `update_content`; `replace_content` blows away everything already on the page, including reviewer edits
- Newlines have to be real newlines; an escaped `\n` renders as literal text
- Every change gets a comment anchored to it; without one, the reviewer has to re-read the whole document to find what moved
- Set a real icon on every page you create; Notion's default blank icon is not a real default

---

## ww-notion-proposal-hardener

**The problem:** The Notion API will tell you an edit succeeded when it silently dropped half your patches. It'll tell you a comment anchor is unique when a phrase that repeats three paragraphs down makes it ambiguous. Both failures are invisible until someone reads the live document closely, usually the reviewer you were revising it for.

This names the three specific ways the API misleads you and pairs each with the check that catches it. `update_content` returns success even when an `old_str` doesn't match (a stray em dash, a bold marker, a discussion-span wrapper around the target text), so every patch gets re-verified against a fresh fetch, never trusted from the response alone. Comment anchoring searches the whole document for the closing phrase, not just your target block, so before posting a comment you count how many times that phrase appears anywhere later in the page; more than once means the anchor is ambiguous and needs tightening. And `notion-get-comments` itself can silently under-return: an open comment the UI shows plainly can come back as zero results from the API, so the API's comment count is treated as a floor, never a complete count, and confirmed against the reviewer's own screenshot when it matters.

### Key principles

- Re-fetch and verify after every `update_content` call; a success response is not proof anything actually changed
- Count occurrences of the end phrase before anchoring a comment; local uniqueness in your target block isn't enough
- A discussion-span wrapper blocks a plain `old_str` match; include the span itself in the patch, or the edit silently skips
- Treat the API's comment list as a floor, not a ceiling; confirm completeness against the reviewer's own view when it matters
- Before any `replace_content`, record every open thread's anchor text and summary first; a full rewrite destroys every inline anchor at once

---

## ww-google-docs

**The problem:** The Google Docs API defaults to Arial, default spacing, and default margins, none of which is anyone's actual house style. A document headed to a client or a teammate who's seen your other docs before reads as generic in a way that's easy to notice and hard to unsee once you've seen it.

Two reliable methods, and the API is honest about the tradeoff between them. Copying an already-styled template and pouring content into it guarantees an exact match, since the copy inherits the source doc's named styles and theme, but only works if a clean template exists to copy. Explicit named-style requests work on any fresh doc, but every style in your table has to be pushed through `updateTextStyle` and `updateParagraphStyle` by hand, since a fresh doc's named styles are still Google's defaults underneath. Either way, a successful API response is not proof the doc looks right: only a read-back, re-fetching the document and confirming the styles and links actually landed, is.

### Key principles

- Build your own house-style table once (font, size, weight, spacing per named style) before starting; everything else assumes it already exists
- Prefer copying a styled template over explicit style requests whenever a clean template exists; it's less work and less error-prone
- Hyperlink the descriptive text, never a bare “link”
- The read-back is mandatory; a successful insert or update response never proves the style actually applied

---

## ww-smart-quote-fixer

**The problem:** Every AI model defaults to straight typewriter quotes, `'` and `"`, and real typography doesn't use them. An editor spots a straight quote in a paragraph of running prose in about half a second, and it reads as unpolished, or machine-written, even when nothing else about the copy is wrong. Fixing it by hand means catching every apostrophe, every nested quote, every decade abbreviation, and every foot-and-inch mark without breaking the ones that were already right, or the ones sitting inside a code block where a straight quote is correct.

This does the conversion deterministically instead of a naive find-and-replace that gets the hard cases wrong: the decade gotcha (`'90s` is a right curly quote, not a left one, even at the start of the token), nested quotes (outer double, inner single), measurements (`6′2″`, not `6'2"`), all while leaving fenced code blocks, inline code, file paths, and regex untouched. Short text gets fixed inline by reading it carefully; anything longer runs through a bundled script that handles plain text, markdown, and `.docx` (preserving bold, italic, and links) alike.

### Commands

```bash
python scripts/fix_quotes.py input.md > output.md
python scripts/fix_quotes.py input.docx -o output.docx
```

`--no-primes` converts measurement quotes to straight marks instead of primes; `--apostrophes-only` is safe mode, apostrophes only, leaves double quotes alone.

### Key principles

- Produce curly quotes from the start when writing editorial prose; don't write straight and rely on a cleanup pass after
- Code blocks, inline code, file paths, and technical syntax are always exempt
- The decade abbreviation is a right quote, not a left one, the single most common typography mistake
- Some apostrophe cases are genuinely ambiguous (`dogs' food` vs. `dog's food`); trust editorial judgment over the script's guess

---

## How these work together

Each skill is useful alone. Together they cover the full arc of a working session, and what happens after you close the laptop:

**Before you build**: `/qq-externalize` routes research, extraction, and critique to free models so you're not burning Claude tokens on work Groq can do for free, and `ww-plan-audit` runs the full gauntlet on the plan itself before a single file gets touched.

**While you build**: `copy-sweep` blocks AI-tell punctuation the instant it would be written, so there's no cleanup pass later.

**After you build**: `/qq-audit` runs the quality check Claude can't run on itself, 255 expert lenses across whatever dimensions matter for your project, and `ww-rule15` is the last gate before the word “done” gets used at all: a stated outcome, a traced action chain, evidence from outside your own head.

**When momentum is high**, `/qq-smart-next-move` asks the question you don't stop to ask: what's the move that compounds what I just built?

**Every week, without you**: `/qq-weekend-burn` puts real work on a recurring schedule that survives caps, closed laptops, and reboots, so the quota gets spent whether or not you're at the keyboard.

**Any time you step away, scheduled or not**: `ww-overnight-runner` sets what an agent decides alone versus what always stops it, `qq-go-afk-lean` keeps the token source cheap while it runs, and `ww-agent-watchdog` checks the result afterward instead of trusting the “done” it reports.

```
/qq-externalize  →  build (copy-sweep guards every write)  →  /qq-audit  →  /qq-smart-next-move  →  /qq-weekend-burn
route cheaply        Claude handles synthesis only              check         what next?              recurring, unattended,
                                                                  quality                                every week
```

`qq-mailbox` sits outside this diagram on purpose: it's not a step in any one session's arc, it's what two sessions running that arc in parallel use to hand work to each other. `ww-skill-auditor`, `ww-dashboard-ux`, `qq-infoviz`, `ww-notion-docs`, `ww-notion-proposal-hardener`, `ww-google-docs`, and `ww-smart-quote-fixer` sit outside it too: each one is a standalone capability (a security gate, a design standard, a doc-formatting fix) you reach for on its own, not a step in this particular arc.

---

## License

MIT
