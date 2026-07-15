---
name: qq-externalize
description: Externalize-first audit. Routes research, extraction, critique, summarization, and adversarial review to free/cheap models. Three-tier adversarial stack (cheap/mid/top) with cross-model voices. Cost kill switch. Claude synthesizes only. Use when routing may have drifted or to set up a convergent adversarial pass.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills) — a collection of skills for running a real Claude Code setup.

# qq-externalize: externalize everything possible

Forces maximum externalization of the current task to the cheapest model that fits. Call when you want to pressure-test whether Claude is doing work a free model should be doing, or to set up a full convergent adversarial flow.

**Usage:**
- `/qq-externalize`: audit current task + produce routing plan, then execute
- `/qq-externalize [task]`: route a specific task to the right model
- `/qq-externalize adversarial`: cross-model adversarial pass on whatever is in context
- `/qq-externalize help`: print this command list only (no action)

## Prerequisites

This skill assumes you have at least one cheap model callable from Bash. Adapt the invocation patterns in Step 2 to whatever clients you have installed:

- **Groq**: free tier, 14,400 calls/day, Llama 3.3 70B. Get a key at console.groq.com.
- **Cerebras**: free tier, 1M tokens/day, Qwen 3 235B (biggest free voice available). Key at cloud.cerebras.ai.
- **DeepSeek V4 Flash**: near-free ($0.14/$0.28 per M tokens). Good for structured JSON. Doesn't rate-limit at typical volume, making it the reliable end-of-chain anchor.
- **Gemini**: free via `gemini` CLI or API. 1M context window.
- **Ollama**: fully local/free. Install at ollama.ai, pull a model (e.g. `ollama pull llama3.2`).

You don't need all five. One free model (Groq) + Gemini covers the adversarial pattern. DeepSeek as a paid fallback makes the failure-mode rule below much easier to honor.

## The mandate

Claude (Sonnet/Opus) costs real money AND subscription plans have usage caps that, when hit, silently force more expensive routing. Free models (Groq, Gemini Flash, Cerebras, Ollama) and cheap paid (DeepSeek V4 Flash) cover most actual work. Any time Claude does research, extraction, classification, summarization, critique, or adversarial review that a cheaper model could do, it's a triple loss: cost burn, quota burn, AND quality loss (no cross-model divergence).

**Goal:** maximum performance per dollar, matching each task to the cheapest model that can produce the right quality, so Claude only synthesizes and everything else gets externalized.

**Cost ladder (always start at the top, escalate only with justification):**

| Tier | Models | Cost | Use when |
|------|--------|------|----------|
| **0. Free** | Groq, Gemini Flash CLI, Cerebras (1M tok/day), Ollama (local) | $0 | Research, extraction, critique, summarization (default) |
| **1. Cheap paid** | DeepSeek V4 Flash | $0.14/$0.28 per M | Free choked or higher quality needed |
| **2. Mid paid** | DeepSeek V4 Pro, Gemini 3 Pro | $0.44–$2 / $0.87–$12 per M | Plan audits, mid-stakes adversarial |
| **3. Sonnet** | Claude Sonnet (session) | $3/$15 per M, subscription-capped | Synthesis, multi-file judgment |
| **4. Top paid** | Gemini 3 Pro (mid-adversary), GPT-5 (Opus-adversary) | $2–$5 / $12–$30 per M | High-stakes audits, architectural review |
| **5. Opus** | Claude Opus | $5/$25 per M | Irreversible architectural decisions only |

Never escalate past Tier 0 without a reason. Never escalate to Tier 3+ when Tier 1 or 2 produces the right answer. Never let Claude self-validate; always pair with a cross-model voice from a lower tier.

## Failure-mode rule (non-negotiable)

**When a routed model fails (429, timeout, empty return, hard error), the answer is NEVER "skip the externalization." It is ALWAYS "use a different model."**

Always-available fallbacks (use these when the primary chokes):
- **DeepSeek V4 Flash**: paid API at $0.14/$0.28 per M, doesn't rate-limit at typical volume
- **Cerebras (free)**: 1M tokens/day on the free tier, qwen-3-235b is the biggest free voice available
- **Ollama (local)**: runs on the local machine, no rate limit, no network dependency. May time out on long prompts under load; retry with a longer timeout (600s) before giving up

Never report "skipped, quota tight" or "fell through to Sonnet because the external model failed." If Groq 429s, route to Cerebras or DeepSeek Flash. If Gemini returns empty, route to DeepSeek. If Ollama times out at 120s, retry once at 600s, then fall to DeepSeek. The convergent adversarial pattern (two voices) MUST produce two actual voices, so substitute models instead of dropping to one.

If you find yourself about to write "skipping the [X] round to save tokens," stop. The whole point of externalization is that the cheap voices ARE the savings. Drop Sonnet first, not the cheap voice.

## Model routing card

Every row has a fallback CHAIN, not a single fallback. Walk it left-to-right until something answers. DeepSeek Flash and Ollama are guaranteed-available end-of-chain anchors. **Always start at the cheapest tier that fits.**

| Task | Primary (free) | Cheap paid fallback | Mid/top adversary (only if stakes warrant) |
|------|---------------|---------------------|--------------------------------------------|
| Research, fact-finding, reading | 🔀 Groq (fast, 128K) | → DeepSeek Flash → Cerebras → Ollama | n/a |
| Extraction, classification, structuring | 🔀 Groq | → DeepSeek Flash (better JSON) → Ollama | n/a |
| Summarization, condensing | 🔀 Groq | → Ollama (local) → DeepSeek Flash | n/a |
| Routine plan critique (low stakes) | 🔀 Groq + 🔀 Gemini Flash (two free voices) | → DeepSeek Flash + Cerebras | n/a |
| **High-stakes plan audit** | 🔀 DeepSeek Flash + 🔀 Cerebras (free pair, then escalate if both agree on something dubious) | → DeepSeek Flash + Gemini Flash | 🔀 Gemini 3 Pro (mid-tier paid adversary, $2/$12) |
| **Architectural / irreversible decision** | (skip free, not enough rigor) | n/a | ⬆️ Opus + 🔀 GPT-5 ($5/$30), top-tier paired voices |
| Second opinion, alternative framing | 🔀 Gemini Flash (CLI, free) | → DeepSeek Flash → Cerebras | 🔀 Gemini 3 Pro (only if stakes warrant) |
| Fix/verdict validation against prod data | 🔀 Groq or 🔀 DeepSeek Flash | → Cerebras → Ollama | n/a |
| Large-context analysis (>100K tokens) | 🔀 Gemini Flash (CLI, free, 1M ctx) | → DeepSeek Flash (1M ctx) | 🔀 Gemini 3 Pro if reasoning depth needed |
| Simple transformation, private data | 🔀 Ollama (local, free) | → DeepSeek Flash | n/a |
| Code generation, file edits (single file) | Claude (session) | n/a | n/a |
| Synthesis of externalized outputs | Claude (session) | n/a | n/a |
| Multi-file judgment | Claude (session) | n/a | 🔀 Gemini 3 Pro for adversarial review |
| **Pre-escalation gate**: anything about to go to your most expensive model for judgment | 🔀 Groq + 🔀 Gemini Flash (two voices, package the question) | Groq 429 → 🔀 DeepSeek Flash + Cerebras. Gemini empty/quota → 🔀 DeepSeek. Always two voices. | If still unresolved AND stakes warrant: 🔀 Gemini 3 Pro before escalating |

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
  - [subtask] → Claude because: [specific reason]

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

**Cerebras (OpenAI-compatible):**
```bash
python3 -c "
from openai import OpenAI
import os
client = OpenAI(api_key=os.environ['CEREBRAS_API_KEY'], base_url='https://api.cerebras.ai/v1')
resp = client.chat.completions.create(
    model='qwen-3-235b-a22b-instruct-2507',
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
import os
client = OpenAI(api_key=os.environ['DEEPSEEK_API_KEY'], base_url='https://api.deepseek.com')
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

If Gemini's output is empty, under 20 chars, or an error string, treat it as a failure and fall through to DeepSeek with the same prompt. Gemini fails silently more often than it errors loudly.

**Ollama (local):**
```bash
ollama run llama3.2 "PROMPT"
```

### Step 3: Adversarial mode (if `/qq-externalize adversarial`)

Run the plan/approach/content through the convergent adversarial pattern:

1. **🔀 Groq:** "Critique this from first principles. What's wrong, missing, or underspecified? Be adversarial." → [current plan/content]
2. **🔀 Gemini:** "Provide an alternative framing or approach. What would you do differently and why?" → [current plan/content]
3. **Claude (session):** Synthesize the critiques. Which survive steelman? Update the plan with only the survivors.

**Brand/positioning variant** (use when task is messaging, positioning, or copy, not plans/code):
- Replace step 1 prompt with: "Does this resonate with how the target customer actually thinks about their problem, or is it rationalized around the product's feature set? What would a skeptical customer say when they read this?"
- Replace step 2 prompt with: "What enemy frame or contrast is missing? What does this positioning implicitly compete against, and is that the right battle?"

### Step 4: Cost scorecard

Report at the end:
```
EXTERNALIZATION SCORECARD
=========================
Externalized: [N] subtasks → Groq/Cerebras/DeepSeek/Gemini/Ollama
Kept in Claude: [N] subtasks (all justified)
Claude work that should have been externalized: [N] (flag)

Models used: Groq ✓ / Cerebras — / DeepSeek ✓ / Gemini ✓ / Ollama —
```

### Step 5: Capture learnings (recommended after every run)

Append one JSON line to an `externalize-runs.jsonl` log in your project:

```json
{"date":"YYYY-MM-DD","session":"<name>","models_tried":{"groq":"ok|429|error","deepseek":"ok|error","gemini":"ok|empty|error","ollama":"ok|error"},"adversarial_changed_answer":true,"what_changed":"<one sentence>","skill_suggestion":"<improvement to routing card, steps, or anti-patterns — or null>"}
```

**What counts as "adversarial changed answer":** Did the external critique catch something Claude missed? Yes = true. Validation only = false.

**Skill suggestion field:** If the run exposed a gap in this SKILL.md (missing fallback, wrong routing, bad anti-pattern), describe the fix. Sweep these into skill updates periodically; the "Known model behavior" table below was built this way.

## Trigger signals

These should automatically trigger externalization (even without `/qq-externalize`):
- "Research X" / "Find out about X" / "What do you know about X" → Groq or DeepSeek
- "Summarize this" / "Extract from this" → Groq
- "What do you think about this plan?" → Groq + Gemini before Claude weighs in
- "Second opinion" / "Alternative approach" → Gemini
- Any plan audit (steelman step) → Groq + Gemini, Claude synthesizes
- Any product definition → Groq + Gemini as adversarial voices
- "Is this fix correct?" / validating a verdict against production data → Groq or DeepSeek before declaring PASS
- User-facing number derived from a formula multiplier (fee rate, probability, percentage) → DeepSeek to verify it represents what the user will think it means, not just that the math is correct ("right number, wrong meaning" class of bug)
- Interpersonal or political strategy tasks → route these out too; Claude defaults to direct confrontation framing, and an adversarial pass reliably finds a softer way in
- Brand/positioning critique → use customer-resonance prompt (see Step 3), not the default plan stress-test
- About to escalate to your most expensive model for judgment → externalize first: package what you're uncertain about + relevant context → Groq + Gemini (fallback: DeepSeek → Ollama, always preserve two voices) → show output with 🔀 labels → THEN escalate only if still unresolved or context too dense to package

## Anti-patterns to catch

- Claude doing research that Groq could do → externalize
- Claude self-critiquing a plan → externalize to Groq + Gemini, Claude synthesizes
- Agent tool used for extraction/summarization → that's Groq, not a subagent
- Missing 🔀 labels → routing is happening silently, unverifiable
- **Post-hoc invocation**: calling /qq-externalize after commits are done means critique is informational only, can't redirect; invoke at decision gates (before builds, before architectural choices), not after
- **Spec-driven execution skip.** If the task is spec-driven execution (handoff defines exact splits, no research or planning component), skip adversarial; it will only surface philosophical design complaints that fail steelman against the spec constraints. Low yield.
- **Pre-flight: already plan-audited.** If a cross-model adversarial audit already ran on the *plan* in this session, skip Step 3 adversarial re-review of that plan; it's redundant. Externalization during *execution* (research, extraction, validation) is unaffected, so route those normally.
- **Steelman direction vs mechanism**: don't dismiss a critique just because its cited causal mechanism is imprecise; check if the concern direction is valid even when the "why" is wrong. A critique can be right about what to fix and wrong about why it breaks.

## Known model behavior (updated from runs)

| Model | Failure mode | What to do |
|-------|-------------|---------|
| Groq | 429 rate limit under load (free tier) | DeepSeek immediately; don't retry Groq |
| Gemini | Silent empty return (no error, no output), likely auth/connection issue | DeepSeek immediately |
| Gemini | TerminalQuotaError (hard block with reset timer, e.g. 3h18m), distinct from silent empty | DeepSeek now; Gemini available again after reset, worth retrying later in session for second opinion |
| DeepSeek | Slow on large prompts | Groq for speed-sensitive tasks; otherwise wait, DeepSeek doesn't 429 at typical volume |
| Ollama | TCP read timeout under load (default 120s too short) | Retry once with timeout=600 (long-context model warm-up). If still timing out, fall to DeepSeek. NEVER skip. |
| Ollama | Local service not running | Start it (`ollama serve`) or fall to DeepSeek |
