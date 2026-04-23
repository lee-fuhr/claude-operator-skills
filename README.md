# Claude Code operator skills

Skills for Claude Code power users.

Three problems these solve:

1. **You're paying Claude to do work free models could do.** Groq, DeepSeek, Gemini, and Ollama exist. Use them. Claude should synthesize — not research, extract, or critique.
2. **You're in flow and there's a smart next move right here — you can feel it but can't quite see it.** This skill looks at what you just built, what it unlocked, and surfaces what compounds it.
3. **Your AI-built product has quality problems it can't see.** Claude wrote the code, copy, and architecture. It can't audit its own output across UX, security, performance, or any of 13 other dimensions. You need expert lenses that don't know your intentions.

> [!TIP]
> New here? Start with `/qq-externalize` — lowest setup friction, immediate ROI. You need one free model API key (Groq is free). Everything else is optional.

---

## Skills

| Command | What it does | Result |
|---------|-------------|--------|
| `/qq-externalize` | Routes research, extraction, critique, and adversarial review to free models. Claude synthesizes only. | Free models handle 70%+ of non-synthesis work |
| `/qq-smart-next-move` | When you're in flow and there's a sense of more here — surfaces the smart next move before momentum carries you somewhere obvious. | Compounds good sessions instead of wasting them |
| `/qq-audit` | Master orchestrator for 255 expert-persona audit frameworks across 13 quality domains. Smart-routes to the right domains in the right order. | SUS 57.5 → 92.5 across 3 rounds on a production app |

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

cp -r skills/qq-externalize skills/qq-smart-next-move skills/qq-audit-master ~/.claude/skills/
cp commands/qq-externalize.md commands/qq-smart-next-move.md commands/qq-audit.md ~/.claude/commands/
```

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

`/qq-externalize` routes to free/cheap models. You need at least one — Groq is the easiest start.

### Groq

**Cost:** Free — 14,400 calls/day  
**Best for:** Research, extraction, summarization, fast first pass  
**Model:** Llama 3.3 70B

Not Elon's Grok — the other one, spelled differently, with 14,400 free calls a day. Take the free compute.

```bash
pip install groq
export GROQ_API_KEY=gsk_...   # console.groq.com → API Keys
```

### DeepSeek

**Cost:** ~$0.14/1M input tokens — effectively free  
**Best for:** Structured JSON output, detailed multi-step analysis  
**Model:** DeepSeek V3

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

**Option A — API key:**
```bash
pip install google-generativeai
export GEMINI_API_KEY=...   # aistudio.google.com → Get API key
```

**Option B — CLI (no key needed):**
```bash
npm install -g @google/gemini-cli && gemini auth
```

### Ollama

**Cost:** Free — runs on your hardware  
**Best for:** Private data, anything you don't want leaving your machine  
**Model:** Your choice

```bash
# Download at ollama.ai, then:
ollama pull llama3.2
```

No API key. No rate limits. Nothing leaves your machine.

---

## qq-externalize

**The problem:** You ask Claude to research a topic, summarize a document, critique a plan, give a second opinion. Claude does it — and bills your subscription. Groq would have done it free.

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

**The feeling:** Things are clicking. You're in flow. There's a sense that you're not done — that there's a smart next move right here you don't want to miss.

This skill captures that. It looks at what just happened, what it unlocked, and asks: what's the thing that compounds this? Not "which of my backlog items is highest priority" — that's a different question. This is "I'm cooking right now, what's the smart thing to do next?"

### Commands

```
/qq-smart-next-move           — infer from session context, surface the options
/qq-smart-next-move [context] — provide explicit context for what just finished
```

### What it produces

> **Based on what we just built and the data we have, here are the moves I see:**
>
> **A. Wire up the observability hook** — Enforcement exists but there's no runtime evidence it's working. Five minutes to confirm vs. hours debugging in production.
> - Data point: zero events in log after three sessions
> - Risk: low — hook either fires or it doesn't
>
> **B. Wire the scorecard into the morning digest** — Invisible unless surfaced daily. High leverage: you see it every morning without thinking about it.
> - Data point: digest is checked daily; dashboard is only checked when something feels wrong
> - Risk: schema change could break existing sections
>
> **Recommendation:** A + B together (15 min each).
>
> **The question I'd want answered first:** Is the guard actually blocking anything?

### The five lenses

1. **What did we just build?** — Specific deliverables, surprises, assumptions validated or broken
2. **What did this unlock?** — What's trivially easy now that was hard before?
3. **What risk did we just create?** — Maintenance burden, dependencies, debt introduced
4. **What compounds this?** — The move that makes what we just built more valuable, right now
5. **Does this move the needle?** — Revenue proximity, client value, building for the business vs. building because it's interesting

### Key principles

- Data over theory — if a number can be checked, it checks before opining
- Capitalize on momentum — what you just built is context; use it
- Revenue proximity matters — all else equal, the thing closer to money wins
- Combine, don't choose — options are presented as combinable, not mutually exclusive

---

## qq-audit

**The problem:** Claude wrote your code. It can't objectively audit its own output — it knows what the code is supposed to do, what the copy is trying to say, how the architecture was intended. You need expert lenses that don't know your intentions, applied domain by domain.

This is the master command for [audit-framework](https://github.com/lee-fuhr/audit-framework): 255 expert-persona frameworks across 13 quality dimensions. It analyzes your project, picks the right domains in the right order, and runs each serially — fixing issues before moving to the next domain, so fixes compound.

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

Each domain runs up to 3 rounds. Round 1 finds ~60% of issues. Round 2 finds 25% more — fixes from round 1 expose new problems. Round 3 catches the last 10–15%. Move on when a domain hits 9.5/10 or exhausts 3 rounds.

```
UX: Round 1 = 7.2 → Round 2 = 8.8 → Round 3 = 9.6 ✓ — moving to Visual
Visual: Round 1 = 8.1 → Round 2 = 9.7 ✓ — moving to Copy
```

### Results

Measured on a production Next.js dashboard (170+ components, UX domain):

| | Score | Fixes |
|-|-------|-------|
| Baseline | SUS 57.5 | — |
| After round 1 | SUS 77.5 | 100+ |
| After round 2 | SUS 90.0 | 45 |
| After round 3 | SUS 92.5 | 8 |
| Ceiling | ~93–95 | Remaining issues are product decisions |

### Domain sequencing

No point auditing visual design when UX is broken — you'll redesign those screens anyway. Domains run in dependency order:

```
Product → UX → Visual → Copy → Frontend → Backend → Performance
       → Security → Testing → SEO → DevOps → Data → Compliance
```

---

## How these work together

Each skill is useful alone. Together they cover the full arc of a working session:

**Before you build** — `/qq-externalize` routes research, extraction, and critique to free models so you're not burning Claude tokens on work Groq can do for free.

**After you build** — `/qq-audit` runs the quality check Claude can't run on itself. 255 expert lenses across whatever dimensions matter for your project.

**When momentum is high** — `/qq-smart-next-move` asks the question you don't stop to ask: what's the move that compounds what I just built?

```
/qq-externalize  →  build  →  /qq-audit  →  /qq-smart-next-move
route cheaply       Claude      check           what next?
                    handles     quality
                    synthesis
                    only
```

---

## License

MIT
