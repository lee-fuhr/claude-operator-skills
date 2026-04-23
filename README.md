# Claude Code operator skills

Skills for people who use Claude Code seriously — not as a chat interface, but as a system.

Three problems these solve:

1. **You're burning money on work free models could do.** Groq, DeepSeek, Gemini, and Ollama exist. Use them. Claude should synthesize, not research.
2. **You finish a build and immediately start the wrong next thing.** Momentum isn't direction. Stop and ask the right questions before you plan.
3. **Your AI-built product has UX problems it can't see.** Claude wrote the code. It can't evaluate whether humans can actually use it. You need 255 expert lenses, applied by domain, applied serially.

---

## Skills

| Skill | Command | What it does | Key result |
|-------|---------|-------------|-----------|
| **qq-externalize** | `/qq-externalize` | Routes research, extraction, critique, and adversarial review to free models. Blocks Claude from doing work Groq could do. | Free models handle 70%+ of non-synthesis work |
| **qq-smart-next-move** | `/qq-smart-next-move` | When things are clicking and there's a sense there's more here — surfaces the smart next move before momentum carries you somewhere obvious. | Compounds good sessions instead of ending them |
| **qq-audit** | `/qq-audit` | Master orchestrator for 255 expert-persona audit frameworks across 13 quality domains. Smart-routes to the right domains in the right order. | SUS 57.5 → 92.5 across 3 rounds |

---

## Install

### qq-externalize + qq-smart-next-move

```bash
git clone https://github.com/lee-fuhr/claude-operator-skills.git
cd claude-operator-skills

cp -r skills/qq-externalize ~/.claude/skills/
cp -r skills/qq-smart-next-move ~/.claude/skills/

cp commands/qq-externalize.md ~/.claude/commands/
cp commands/qq-smart-next-move.md ~/.claude/commands/
```

### qq-audit (master + 13 domain skills)

`/qq-audit` is the command that drives [audit-framework](https://github.com/lee-fuhr/audit-framework) — 255 expert-persona frameworks already published in its own repo. Install the master skill here, then install the domain skills from there:

```bash
# Master orchestrator (this repo)
cp -r skills/qq-audit-master ~/.claude/skills/
cp commands/qq-audit.md ~/.claude/commands/

# 13 domain skills + domain commands (audit-framework)
git clone https://github.com/lee-fuhr/audit-framework.git
cp -r audit-framework/skills/qq-audit-* ~/.claude/skills/
cp audit-framework/commands/qq-audit-*.md ~/.claude/commands/
```

Adapt paths if your skills directory is different (e.g. `~/.agents/skills/`). Restart Claude Code after copying.

---

## Model setup

`qq-externalize` routes to free/cheap models. Set up whichever ones you want — you need at least one, Groq is the easiest start.

### Groq — free, fast, 14,400 calls/day (recommended)

1. Create account at [console.groq.com](https://console.groq.com)
2. Go to API Keys → Create API key
3. Add to your shell: `export GROQ_API_KEY=gsk_...`
4. `pip install groq`

### DeepSeek — near-free (~$0.14/1M tokens), best for structured JSON and detailed analysis

1. Create account at [platform.deepseek.com](https://platform.deepseek.com)
2. Go to API keys → Create new API key
3. Add to your shell: `export DEEPSEEK_API_KEY=sk-...`
4. `pip install openai` (DeepSeek uses the OpenAI-compatible API)

### Gemini — free, best for large context (1M tokens) and second opinions

**Option A — API:**
1. Get a key at [aistudio.google.com](https://aistudio.google.com) → Get API key
2. Add to your shell: `export GEMINI_API_KEY=...`
3. `pip install google-generativeai`

**Option B — CLI:**
1. `npm install -g @google/gemini-cli`
2. `gemini auth` (uses your Google account, no key needed)

### Ollama — free, fully local, no data leaves your machine

1. Download at [ollama.ai](https://ollama.ai)
2. `ollama pull llama3.2` (or any model you prefer)
3. No API key needed — runs on your hardware

After setup, update the Bash invocation patterns in Step 2 of `skills/qq-externalize/SKILL.md` to match your clients.

---

## qq-externalize

**The problem:** You ask Claude to research a topic, summarize a document, critique a plan, or give a second opinion. Claude does it — and bills your subscription. Groq would have done it free.

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
| Structured JSON, detailed analysis | DeepSeek V3 | Best-in-class for structured output, near-free |
| Critique, plan stress-test | Groq + Gemini | Cross-model divergence = real adversarial pressure |
| Second opinion, alternative framing | DeepSeek or Gemini | Different training = different blind spots |
| Large context (>100K tokens) | Gemini | 1M token context window |
| Private data, simple transforms | Ollama | Local, no data leaves your machine |
| Synthesis, multi-file code | Claude | Worth paying for |
| Irreversible decisions | Claude Opus | Worth paying for |

### Prerequisites

At least one free model callable from Bash:

- **Groq** — `pip install groq` + `GROQ_API_KEY` env var. Free tier: 14,400 calls/day.
- **Gemini** — `pip install google-generativeai` or `gemini` CLI. Free via Google auth.
- **DeepSeek** — `pip install openai` (uses OpenAI-compat API) + `DEEPSEEK_API_KEY`. ~$0.14/1M tokens.
- **Ollama** — install at ollama.ai, `ollama pull llama3.2`. Fully local, no API key.

Update the Bash invocations in Step 2 of the skill file to match your client setup. The routing logic is model-agnostic.

---

## qq-smart-next-move

**The feeling:** Things are clicking. You're in flow. There's a sense that you're not done — that there's a smart next move right here, in this session, that you don't want to miss.

This skill captures that. It pulls back for a moment, looks at what just happened and what it unlocked, and asks: what's the thing that compounds this? Not "which of my 15 backlog items is highest priority" — that's a different question. This is "I'm cooking right now, what's the smart thing to do next with this momentum?"

### Commands

```
/qq-smart-next-move           — infer from session context, run the full analysis
/qq-smart-next-move [context] — provide explicit context for what just finished
```

### What it produces

> **Based on what we just built and the data we have, here are the moves I see:**
>
> **A. Wire up the observability hook** — Enforcement exists but there's no runtime evidence it's working. Five minutes to confirm vs. hours debugging in production.
> - Data point: zero events in log after three sessions
> - Risk: low — hook either fires or it doesn't
>
> **B. Write the morning digest integration** — Scorecard is invisible unless surfaced daily. High leverage: you see it every morning without thinking about it.
> - Data point: digest is checked daily; dashboard is checked when something feels wrong
> - Risk: schema change could break existing sections
>
> **Recommendation:** A + B together (15 min each), defer C to session wrap.
>
> **The question I'd want answered first:** Is the guard actually blocking anything?

### The five question categories

1. **Validation** — Is the thing we built actually working?
2. **Leverage** — What does this unlock that wasn't possible before?
3. **Risk** — What could go wrong that we're not thinking about?
4. **Opportunity cost** — Is there something higher-value we could do next in this session?
5. **Strategic alignment** — Does this move the needle on what matters?

### Key principles

- Data over theory — if a number can be checked, it checks before opining
- Challenge momentum — "we should keep going" is often inertia, not strategy
- Revenue proximity matters — all else equal, the thing closer to money wins
- Combine, don't choose — options are presented as combinable, not mutually exclusive

---

## qq-audit

**The problem:** Claude wrote your code. It can't objectively evaluate whether humans can use it — it knows what the code is supposed to do. You need external frameworks applied by an evaluator that doesn't know your intentions.

This skill is the master orchestrator for [audit-framework](https://github.com/lee-fuhr/audit-framework): 255 expert-persona frameworks across 13 quality domains. It analyzes project context, picks the right domains in the right order, and runs each domain's frameworks serially — fixing issues before moving to the next domain, so fixes compound.

### Commands

```
/qq-audit                   — smart routing: picks the right domains for your project
/qq-audit [domains]         — run specific domains (e.g. "ux + copy")
/qq-audit pre-launch        — preset: 8 domains before going live
/qq-audit quick             — preset: UX + Visual + Copy fast check
/qq-audit post-build        — preset: UX + Visual + Copy + Frontend after a feature
/qq-audit deep              — all 13 domains
/qq-audit list              — show all 13 domains with framework counts
```

### The 13 domains

| # | Domain | Command | Frameworks | Expert lens |
|---|--------|---------|-----------|-------------|
| 1 | UX | `/qq-audit-ux` | 20 | Does the brain work well with this? |
| 2 | Product | `/qq-audit-product` | 20 | Is this the right product? |
| 3 | Visual UI | `/qq-audit-visual` | 22 | Does this look professional? |
| 4 | Content/Copy | `/qq-audit-copy` | 22 | Is the writing good? |
| 5 | Frontend | `/qq-audit-frontend` | 22 | Is the code well-built? |
| 6 | Performance | `/qq-audit-performance` | 22 | Is it fast? |
| 7 | Security | `/qq-audit-security` | 23 | Is it safe? |
| 8 | QA/Testing | `/qq-audit-testing` | 22 | Is it tested? |
| 9 | Backend/API | `/qq-audit-backend` | 22 | Is the server-side solid? |
| 10 | SEO | `/qq-audit-seo` | 15 | Can people find it? |
| 11 | DevOps | `/qq-audit-devops` | 15 | Is it deployable and resilient? |
| 12 | Data Quality | `/qq-audit-data` | 15 | Is the data trustworthy? |
| 13 | Compliance | `/qq-audit-compliance` | 15 | Is it legally sound? |
| | **Total** | | **255** | |

### Convergence protocol

Each domain runs 3 rounds maximum. Round 1 finds ~60% of issues. Round 2 finds 25% more (fixes from round 1 expose new issues). Round 3 catches the last 10–15%. The skill moves to the next domain only when the current domain hits 9.5/10 or exhausts 3 rounds.

```
UX: Round 1 = 7.2 → Round 2 = 8.8 → Round 3 = 9.6 ✓ — moving to Visual
Visual: Round 1 = 8.1 → Round 2 = 9.7 ✓ — moving to Copy
```

### Results

Measured on a production Next.js dashboard (170+ components):

| Round | Score | Fixes applied |
|-------|-------|--------------|
| Baseline | SUS 57.5 | — |
| Round 1 | SUS 77.5 | 100+ fixes |
| Round 2 | SUS 90.0 | 45 fixes |
| Round 3 | SUS 92.5 | 8 fixes |
| Ceiling | ~93–95 | Remaining issues are product decisions |

### Build lifecycle sequencing

The master skill sequences domains in dependency order — no point auditing visual design when UX is broken, because you'll redesign those screens after UX fixes.

```
Product → UX → Visual → Copy → Frontend → Backend → Performance
→ Security → Testing → SEO → DevOps → Data → Compliance
```

---

## How these work together

Designed to be used in sequence within a session:

1. **`/qq-externalize`** at the start — audit the task and route cheaply before burning Claude on things Groq can do
2. **Build the thing** — with Claude handling only synthesis and judgment
3. **`/qq-audit`** after a build — evaluate quality with 255 expert frameworks across the right domains
4. **`/qq-smart-next-move`** at the milestone — ask the right questions before planning what's next

---

## License

MIT
