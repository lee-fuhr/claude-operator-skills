# Claude Code operator skills

Two workflow skills for Claude Code power users — model routing and strategic momentum.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| qq-externalize | `/qq-externalize` | Route research, extraction, critique, and adversarial review to Groq/DeepSeek/Gemini/Ollama (free). Cost kill switch. Claude synthesizes only. |
| qq-smart-next-move | `/qq-smart-next-move` | After a milestone, ask the smart strategic questions before planning next. Data-backed, assumption-interrogating, options as combinations. |

## Installation

```bash
# Copy skills
cp -r skills/qq-externalize ~/.claude/skills/
cp -r skills/qq-smart-next-move ~/.claude/skills/

# Copy slash commands
cp commands/qq-externalize.md ~/.claude/commands/
cp commands/qq-smart-next-move.md ~/.claude/commands/
```

Adapt paths if your skills directory is different (e.g. `~/.agents/skills/`).

## Prerequisites

**qq-externalize** requires at least one cheap model callable from Bash:
- **Groq** (free, 14,400 req/day) — `pip install groq` + `GROQ_API_KEY` env var
- **Gemini** — `pip install google-generativeai` or the `gemini` CLI
- **DeepSeek**, **Ollama** — optional additional routing targets

Update the Bash invocation patterns in Step 2 of the skill to match your client setup. The routing logic is model-agnostic — any cheap callable model works.

**qq-smart-next-move** has no prerequisites beyond Claude Code.

## License

MIT
