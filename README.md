# Claude Code operator skills

Skills for people who use Claude Code seriously — not as a chat interface, but as a system.

Three problems these solve:

1. **You're burning money on work free models could do.** Groq, DeepSeek, Gemini, and Ollama exist. Use them. Claude should synthesize, not research.
2. **You finish a build and immediately start the wrong next thing.** Momentum isn't direction. Stop and ask the right questions before you plan.
3. **Your AI-built product has UX problems it can't see.** Claude wrote the code. It can't evaluate whether humans can actually use it. You need seventeen lenses, applied serially.

These skills address all three.

---

## Skills

| Skill | Command | What it does | Key result |
|-------|---------|-------------|-----------|
| **qq-externalize** | `/qq-externalize` | Routes research, extraction, critique, and adversarial review to free models. Blocks Claude from doing work Groq could do. | Free models handle 70%+ of non-synthesis work |
| **qq-smart-next-move** | `/qq-smart-next-move` | After a milestone, asks the assumption-interrogating questions before planning. Presents options as combinable, not exclusive. | Prevents building the wrong thing next |
| **ux-framework-audit** | `/ux-framework-audit` | Runs 17 usability frameworks serially. Each framework fixes issues before the next one runs — fixes compound. | SUS 57.5 → 92.5 across 3 rounds, 150+ fixes |

---

## Install

```bash
git clone https://github.com/lee-fuhr/claude-operator-skills.git
cd claude-operator-skills

# Copy skills (adapt path if yours is different)
cp -r skills/qq-externalize ~/.claude/skills/
cp -r skills/qq-smart-next-move ~/.claude/skills/
cp -r skills/ux-framework-audit ~/.claude/skills/

# Copy slash commands
cp commands/qq-externalize.md ~/.claude/commands/
cp commands/qq-smart-next-move.md ~/.claude/commands/
cp commands/ux-framework-audit.md ~/.claude/commands/
```

Restart Claude Code. All three slash commands are now available.

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
| Research, fact-finding | Groq (Llama 3.3 70B) | Free, 128K context, fast |
| Extraction, classification | Groq | Free, structured output |
| Summarization | Groq | Free, reliable |
| Critique, plan stress-test | Groq + Gemini | Cross-model divergence = real adversarial pressure |
| Second opinion | Gemini | Different training = different blind spots |
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

**The problem:** You just finished something. Momentum is high. You're about to start the next thing — and it's probably the natural next thing, not the highest-value next thing. These are almost never the same.

This skill stops you before you plan. It inventories what just happened (using session context, not asking you), asks five categories of assumption-interrogating questions, and presents options as combinable rather than forcing a choice.

### Commands

```
/qq-smart-next-move          — infer from session context, run the full analysis
/qq-smart-next-move [context] — provide explicit context for what just finished
```

### What it produces

> **Based on what we just built and the data we have, here are the moves I see:**
>
> **A. Wire up the observability hook** — The enforcement exists but there's no runtime evidence it's working. Five minutes to confirm vs. hours debugging in production.
> - Data point: zero events in routing_events.jsonl after three sessions
> - Risk: low — hook either fires or it doesn't
>
> **B. Write the morning digest integration** — Routing scorecard is invisible unless surfaced in the daily email. High leverage: you see it every day without thinking about it.
> - Data point: digest is checked every morning, dashboard is checked when something feels wrong
> - Risk: digest schema change breaks existing sections
>
> **C. Document the enforcement pattern for The Bureau** — This is the first complete three-hook enforcement implementation. High reuse value if shared before the pattern drifts.
> - Data point: enforcement gap came up in the last two sessions
> - Risk: none — documentation only
>
> **Recommendation:** A + B together (15 min each), defer C to session wrap.
>
> **The question I'd want answered first:** Is the guard actually blocking anything?

### The five question categories

The skill asks one question from each category before presenting options:

1. **Validation** — Is the thing we built actually working?
2. **Leverage** — What does this unlock that wasn't possible before?
3. **Risk** — What could go wrong that we're not thinking about?
4. **Opportunity cost** — Is there something higher-value we could do next in this session?
5. **Strategic alignment** — Does this move the needle on what matters?

### Key principles

- Data over theory — if you can check a number, it checks before opining
- Challenge momentum — "we should keep going" is often inertia, not strategy
- Revenue proximity matters — all else equal, the thing closer to money wins
- Combine, don't choose — options are presented as combinable, not mutually exclusive

---

## ux-framework-audit

**The problem:** Claude wrote your code. It can't objectively evaluate whether humans can use it — it knows what the code is supposed to do. You need external frameworks applied by an evaluator that doesn't know your intentions.

This skill runs 17 proven usability frameworks serially against your codebase. Each framework evaluates source code and screenshots, fixes critical issues, verifies the build is clean, then the next framework runs against the improved version. Fixes compound.

### Commands

```
/ux-framework-audit               — run all 17 frameworks in order
/ux-framework-audit [framework]   — run one framework by name
/ux-framework-audit round 2       — run a second full pass after initial fixes
/ux-framework-audit list          — show all 17 frameworks
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

### The 17 frameworks

| # | Framework | What it catches |
|---|-----------|----------------|
| 1 | Nielsen's 10 heuristics | Visibility, error prevention, consistency, help |
| 2 | Gestalt principles | Visual grouping, similarity, figure-ground |
| 3 | Fitts's Law | Touch targets too small, primary actions too far |
| 4 | Hick's Law | Too many choices, decision paralysis |
| 5 | Miller's Law | Cognitive overload, chunking failures |
| 6 | Jakob's Law | Violating patterns users already know |
| 7 | Aesthetic-usability | Visual polish, perceived reliability |
| 8 | Von Restorff effect | Primary CTA same weight as secondary |
| 9 | Zeigarnik effect | Missing progress indicators, no completion signals |
| 10 | WCAG 2.1 AA | Contrast, keyboard nav, screen readers, focus states |
| 11 | Emotional design | Cold/functional feel, no delight |
| 12 | Progressive disclosure | Complexity shown all at once |
| 13 | Error tolerance | No undo, silent failures, missing confirmation |
| 14 | Consistency audit | Visual/behavioral/semantic inconsistency |
| 15 | Information architecture | Navigation confusion, mislabeling |
| 16 | Responsive design | Mobile/tablet breakpoint failures |
| 17 | SUS scoring | System Usability Scale — the measuring stick |

### Why serial, not parallel

70% of findings duplicate across frameworks. Running serially means each framework evaluates code that already has fixes from previous frameworks — genuine new issues only, compounding rather than overlapping.

### What it catches that single-framework audits miss

| Issue type | Found by | Missed by |
|-----------|---------|-----------|
| Fake data displayed as real | Nielsen H1 | SUS |
| Touch targets under 44px | Fitts | Nielsen |
| No undo on destructive actions | Error tolerance | Gestalt |
| System jargon in UI text | Nielsen H2 | WCAG |
| 10+ nav items without grouping | Hick + Miller | Aesthetic |
| Primary CTA same weight as secondary | Von Restorff | Consistency |
| No progress indicator on long tasks | Zeigarnik | Fitts |
| Mobile layout completely broken | Responsive | SUS |

---

## How these work together

They're designed to be used in sequence within a session:

1. **`/qq-externalize`** at the start — audit the task and route cheaply before burning Claude on things Groq can do
2. **Build the thing** — whatever you were building
3. **`/ux-framework-audit`** after a UI build — evaluate quality with 17 external lenses
4. **`/qq-smart-next-move`** at the milestone — ask the right questions before planning what's next

---

## Related

**[audit-framework](https://github.com/lee-fuhr/audit-framework)** — 255 expert-persona frameworks across 13 quality domains (UX, Product, Visual, Copy, Frontend, Performance, Security, Testing, Backend, SEO, DevOps, Data, Compliance). The successor to `ux-framework-audit` with deeper personas and 12 additional domains.

---

## License

MIT
