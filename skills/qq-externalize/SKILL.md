---
name: qq-externalize
description: Externalize-first audit — route research, extraction, critique, summarization, and adversarial review to Groq/DeepSeek/Gemini/Ollama (free). Cost kill switch. Claude synthesizes only. Use when routing may have drifted or to set up a convergent adversarial pass.
---

# qq-externalize — externalize everything possible

Forces maximum externalization of the current task to free/cheap models. Call when you want to pressure-test whether Claude is doing work a free model should be doing, or to set up a full convergent adversarial flow.

**Usage:**
- `/qq-externalize` — audit current task + produce routing plan, then execute
- `/qq-externalize [task]` — route a specific task to the right free model
- `/qq-externalize adversarial` — cross-model adversarial pass on whatever is in context
- `/qq-externalize help` — print this command list only (no action)

## Prerequisites

This skill assumes you have at least one cheap model callable from Bash. Adapt the invocation patterns in Step 2 to whatever clients you have installed:

- **Groq** — free tier, 14,400 calls/day, Llama 3.3 70B. Get a key at console.groq.com.
- **DeepSeek V3** — near-free ($0.14/1M input tokens). Good for structured JSON output.
- **Gemini** — free via `gemini` CLI or API. 1M context window.
- **Ollama** — fully local/free. Install at ollama.ai, pull a model (e.g. `ollama pull llama3.2`).
- **Claude Haiku** — cheapest Claude tier, for tasks that need Claude's tool-use or instruction-following.

You don't need all five. One free model (Groq) + Gemini covers the adversarial pattern.

## The mandate

Claude (Sonnet/Opus) costs real money. Groq, DeepSeek, Gemini, and Ollama are free or near-free. Any time Claude does research, extraction, classification, summarization, critique, or adversarial review that a free model could do, it's a waste AND a quality failure (no cross-model divergence = no adversarial pressure).

**Goal:** Claude synthesizes. Everything else externalizes.

## Model routing card

| Task | First choice | Fallback |
|------|-------------|---------|
| Research, fact-finding, reading | 🔀 Groq (fast, 128K) | 🔀 DeepSeek |
| Extraction, classification, structuring | 🔀 Groq | 🔀 DeepSeek (better JSON) |
| Summarization, condensing | 🔀 Groq | 🔀 Ollama (local) |
| Critique, plan stress-test | 🔀 Groq + 🔀 Gemini | — |
| Second opinion, alternative framing | 🔀 Gemini | 🔀 DeepSeek |
| Large-context analysis (>100K tokens) | 🔀 Gemini (1M ctx) | — |
| Simple transformation, private data | 🔀 Ollama (local, free) | 🔀 Groq |
| Code generation, file edits | Claude (session) | — |
| Synthesis of externalized outputs | Claude (session) | — |
| Multi-file judgment, architecture | Claude → Opus | — |

## When invoked

### Step 1: Task audit

Read the current context and identify ALL subtasks. For each, apply the routing card:
- Mark everything that CAN be externalized (research, critique, extraction, adversarial)
- Mark what MUST stay with Claude (synthesis, judgment, multi-file code)
- Flag any Claude work that should have been externalized already

Output a routing plan:
```
ROUTING PLAN
============
EXTERNALIZE (free/cheap):
  - [subtask] → Groq (reason)
  - [subtask] → Gemini (reason)
  - [subtask] → DeepSeek (reason)

KEEP (Claude only — justify):
  - [subtask] → Sonnet because: [specific reason]

ALREADY DONE BY CLAUDE THAT SHOULD HAVE BEEN EXTERNALIZED:
  - [if any — flag for user]
```

### Step 2: Execute external work

Run the externalized subtasks via Bash. **Adapt these invocation patterns to your project's client setup.** The pattern matters; the path doesn't.

**Groq:**
```bash
python3 -c "
from groq import Groq
client = Groq()  # reads GROQ_API_KEY from env
resp = client.chat.completions.create(
    model='llama-3.3-70b-versatile',
    messages=[{'role': 'user', 'content': 'PROMPT'}],
    max_tokens=2000
)
print(resp.choices[0].message.content)
"
```

**DeepSeek:**
```bash
python3 -c "
from openai import OpenAI
client = OpenAI(api_key='YOUR_KEY', base_url='https://api.deepseek.com')
resp = client.chat.completions.create(
    model='deepseek-chat',
    messages=[{'role': 'user', 'content': 'PROMPT'}],
    max_tokens=2000
)
print(resp.choices[0].message.content)
"
```

**Gemini CLI:**
```bash
gemini -p "PROMPT"
```

**Gemini via Python:**
```bash
python3 -c "
import google.generativeai as genai
genai.configure(api_key='YOUR_KEY')
model = genai.GenerativeModel('gemini-2.0-flash')
print(model.generate_content('PROMPT').text)
"
```

**Ollama (local):**
```bash
ollama run llama3.2 "PROMPT"
```

### Step 3: Adversarial mode (if `/qq-externalize adversarial`)

Run the plan/approach/content through the convergent adversarial pattern:

1. **🔀 Groq:** "Critique this from first principles. What's wrong, missing, or underspecified? Be adversarial." → [current plan/content]
2. **🔀 Gemini:** "Provide an alternative framing or approach. What would you do differently and why?" → [current plan/content]
3. **Claude (session):** Synthesize the critiques. Which survive steelman? Update the plan with only the survivors.

### Step 4: Cost scorecard

Report at the end:
```
EXTERNALIZATION SCORECARD
=========================
Externalized: [N] subtasks → Groq/DeepSeek/Gemini/Ollama
Kept in Claude: [N] subtasks (all justified)
Claude work that should have been externalized: [N] (flag)

Models used: Groq ✓ / DeepSeek ✓ / Gemini ✓ / Ollama —
```

## Trigger signals

These should automatically trigger externalization (even without `/qq-externalize`):
- "Research X" / "Find out about X" / "What do you know about X" → Groq or DeepSeek
- "Summarize this" / "Extract from this" → Groq
- "What do you think about this plan?" → Groq + Gemini before Claude weighs in
- "Second opinion" / "Alternative approach" → Gemini
- Any plan audit (steelman step) → Groq + Gemini, Claude synthesizes
- Any product definition → Groq + Gemini as adversarial voices

## Anti-patterns to catch

- Claude doing research that Groq could do → externalize
- Claude self-critiquing a plan → externalize to Groq + Gemini, Claude synthesizes
- Agent tool used for extraction/summarization → that's Groq, not a subagent
- Missing 🔀 labels → routing is happening silently, unverifiable
