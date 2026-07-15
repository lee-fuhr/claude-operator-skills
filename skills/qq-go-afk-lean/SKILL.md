---
name: qq-go-afk-lean
description: The token-source posture for an autonomous or AFK session. LEAN’s defining move is MAXIMAL EXTERNALIZATION: push every drop of work it can onto the rest of the model stack (Groq, Cerebras, DeepSeek, Gemini, Ollama) so the scarce Claude subscription quota lasts as long as possible and does the most total work per Claude token. Builds on the `ww-keepalive` skill for the resilience mechanism when run unattended; the difference LEAN adds is the token-SOURCE posture, Claude is a precious reserve, spent only on the irreducible (final synthesis, voice/copy, irreversible judgment). Apply it as a standing per-session posture, interactive or autonomous, at any pace (one bounded task at a time, or a wide fan-out). Invoke when you say “go afk lean”, “go-afk-lean”, “qq-go-afk-lean”, “go lean”, “lean mode”, “squeeze the quota”, “stretch the main quota”, “conserve the main quota”, “push to the stack”, “max externalize”, or want a session to run while burning the minimum Claude quota.
---

> Part of [Claude Code operator skills](https://github.com/lee-fuhr/claude-operator-skills): a collection of skills for running a real Claude Code setup.

# Go AFK Lean: squeeze the main quota, push maximally to the stack

The token-source posture for an autonomous or AFK session. Pace (a wide fan-out vs. one bounded task at a time) is a separate decision from token source. **LEAN decides the TOKEN SOURCE:** it treats the Claude subscription quota (the weekly cap, usually the binding constraint) as something to *conserve*, and pushes the maximum possible work onto the rest of the model stack, so the main quota stretches as far as it can and the session gets the most total work done per Claude token spent.

**When to reach for LEAN:** the Claude weekly cap is the binding constraint (or you want it to stop being one); the work has a lot of grunt (research, extraction, transformation, mechanical edits, critique) that external models do fine; you’d rather do MORE total work on free/cheap models than fewer things on Claude. Apply LEAN to a live session, or stand up an autonomous LEAN campaign.

---

## The one rule: external by default, Claude only for the irreducible

Default EVERY unit of work to the cheapest capable model. The bar to spend a Claude (Sonnet/Opus) token is HIGH: you must be able to say *why no external model could do it*. Reserve Claude for:
- **Final synthesis** of externalized outputs (taste, integration, the last mile).
- **Voice / copy / positioning / messaging** generation AND critique. Cheap models are the one place quality doesn’t scale with price: they inject corporate-speak and miss your own voice. Never externalize this.
- **Irreversible / architectural judgment.**
- **Deep multi-file reasoning externals demonstrably fail at.** Escalate only AFTER an external actually fails, not preemptively.

Everything else goes to the stack: research, web-fetch, fact-finding, extraction, classification, summarization, transformation, log-reduction, structured-data work, adversarial critique of plans, first-draft code analysis, repetitive edits.

## The stack + failover (never block, never fall back to Claude)

Route to whatever cheap/free model clients you have installed, ordered by cost then capability:
- **Free first:** Groq (Llama 3.3 70B, fast) · Cerebras (Qwen 3 235B / GPT-OSS, biggest free option) · Ollama (local, no limit, private, offline).
- **Cheap paid anchor:** DeepSeek Flash (near-free, 1M context), the always-available workhorse that essentially never rate-limits at normal volume.
- **Harder:** a stronger paid tier (e.g. DeepSeek Pro, Gemini Pro) for cross-vendor divergence on audits and higher-stakes critique.

**Failure-mode rule (non-negotiable):** on a 429, empty response, or timeout, substitute ANOTHER EXTERNAL, never “skip it,” and **never fall back to Claude to just-get-it-done** (that defeats the whole posture). Chain: Groq → DeepSeek Flash → Cerebras → Ollama (retry at a longer timeout) → DeepSeek Flash. DeepSeek Flash and a local Ollama model are good end-of-chain anchors that should always answer.

## When Claude is genuinely unavoidable, still tier down

Your cheapest Claude tier for cheap Claude-semantic tasks → **your mid tier first** → your top tier only for the truly irreversible/architectural. **Default to the cheaper Claude tier over the top tier even for synthesis, voice, and copy under LEAN**: the top tier is the last resort, not the safe default. The most expensive model should never read every file itself. Fan bounded, token-heavy work to the cheapest Claude tier when it can’t leave Claude at all.

## Aggression knobs (squeeze harder)

- **Batch** grunt work into single large external calls (large-context external models) instead of many small Claude calls.
- **Pre-reduce before synthesis:** a free model summarizes/extracts, Claude integrates the *summary*, never the raw corpus.
- **External workers, Claude judge:** for any fan-out, make the workers external and keep only the final taste/judgment on Claude.
- **Cache and reuse** external outputs; never re-run the same extraction.
- **Watch for routing drift back toward Claude** on a recurring cadence if the session runs long, since habit pulls work back onto the expensive model over time.

## Apply LEAN to a live session (the per-session posture)

When applied to a session (not a campaign), LEAN is a standing directive for the rest of the session:
1. Before EVERY action, ask: *can a free/cheap model do this?* If yes, route it out.
2. Label every externalized step with its routing source (which model handled it) so the routing is auditable; silence on routing is non-compliance.
3. Synthesize and decide on Claude only, and show the routing rationale whenever escalating to Claude.
4. If asked, report Claude quota saved-vs-spent for the session.

## Resilience backbone (for autonomous LEAN)

Stand up the kept-alive via the `ww-keepalive` skill (`~/.claude/skills/ww-keepalive/SKILL.md`). It owns the fresh-`claude -p` mechanism (never `--resume`), the keepalive.sh gates plus pgrep-banner liveness plus interactive interlock plus dual-account failover plus `--permission-mode auto`, the user-run one-paste plist install, and the tasklist standard (`queue.md` + `done.md` scaffolded in the lane). LEAN supplies ONLY the brain’s token-source posture for the resume.md template’s posture slot, on top of whatever pace posture (bounded one-task-at-a-time, or a wide fan-out) the campaign is otherwise running at: **maximize external offload; Claude is the reserve.** That is the one thing LEAN changes versus a Claude-default posture at the same pace; everything else (the gates, the liveness check, the failover, the tasklist) is identical.

## Composing LEAN with pace

LEAN is a token-source decision, independent of pace. It composes with either:

| axis | question it answers | LEAN’s answer |
|---|---|---|
| **pace** | how much fans out at once: one bounded task per cycle, or a wide, ambitious fan-out | unchanged by LEAN, set this separately for the session or campaign |
| **token source** | which models actually do the work | **minimize Claude quota; maximize external offload** |

A bounded-and-lean run is a calm, one-task-at-a-time cadence where the workers doing each task are external and Claude only checks the result. A wide-and-lean run fans out broadly but the fanned-out workers are external models, with Claude reserved as the final judge. The constant across both: Claude is the scarce reserve, the stack does the work.

## Overnight questions, never a blocked stall

For any unattended overnight run, never let a decision that needs you stall the worker. Keep a running `morning-questions.md` in the lane: any decision that needs a human call gets appended there with one line of context and 2-4 concrete options, and the worker immediately takes the next unblocked unit instead of stopping or pinging anyone at night. Whoever is supervising compiles that file into one batched interview the next time they engage, dropping any question whose trigger condition never actually fired.
