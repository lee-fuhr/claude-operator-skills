#!/usr/bin/env python3
"""
PreToolUse hook: catches AI-tell punctuation and formatting before it ever
lands in a file — em dashes, straight quotes, Title Case headings, banned
corporate-speak, throat-clearing openers, summary-crutch headers, and
(optionally) a bare "We" in solo-voice drafts.

Fires on Write / Edit / MultiEdit. Blocks the write (exit 1) with a specific,
line-numbered fix list. Claude sees the block message and fixes it inline
before the file ever touches disk — no separate cleanup pass.

Config — all optional, everything below is a sane default:

  SKIP_COPY_SWEEP=1
      Bypass entirely for this call (force-major / intentional violation).

  COPY_SWEEP_EXTENSIONS=".md,.txt"
      Comma-separated file extensions to scan. Default: .md,.txt

  COPY_SWEEP_INCLUDE="drafts/,content/,copy/"
      Comma-separated path fragments — if set, the file path must contain at
      least one of these to be scanned. Default: unset (scan every matching
      extension, everywhere except COPY_SWEEP_EXCLUDE).

  COPY_SWEEP_EXCLUDE="node_modules/,.git/,CHANGELOG.md,README.md"
      Comma-separated path fragments to always skip. Sensible defaults are
      baked in below; set this to override them completely, or leave unset
      and the defaults apply.

  COPY_SWEEP_CHECKS="em_dash,straight_quote,title_case,banned_phrase,throat_clearing,summary_crutch"
      Comma-separated list of checks to run. That's the default set — all
      deterministic, zero model calls, on by default. Available extras:
      we_pronoun (off by default — a "solo operator" rule, not universal)
      and the three SEMANTIC checks below (off by default, read their own
      section — they're a different kind of check, not just "more rules").

  COPY_SWEEP_LONGFORM_WORDS=400
      Word-count threshold for "this is a long-form piece, not a short
      message." Feeds the em-dash budget (below).

  COPY_SWEEP_BANNED_PHRASES="leverage,synergy,touch base,circle back,..."
      Comma-separated list that REPLACES the default banned-phrase list
      entirely (see DEFAULT_BANNED_PHRASES below for what ships). Every
      house style has a different corporate-speak allergy list — override
      this rather than fighting the default.

Em-dash policy — a budget, not a ban: zero em dashes in short-form copy
(under COPY_SWEEP_LONGFORM_WORDS), at most ONE in a long-form piece. The
one long-form dash isn't auto-approved by the hook — it's on you to make
sure it's actually earning its place, not a lazy default. A second em dash
in the same long-form piece is over budget and gets flagged like any other
violation.

SEMANTIC CHECKS — off by default, read this before turning them on:

  vague_pronoun, rule_of_three, pontificating

  These three can't be caught with a regex — they're judgment calls about
  meaning and rhythm, not fixed patterns. Enabling any of them makes this
  hook place a real model API call (Groq first, DeepSeek fallback) on every
  matching Write/Edit, which means:

    - NONDETERMINISTIC: the same text can get a different verdict on a
      different run. A regex either matches or it doesn't; a model has to
      make a judgment call, and judgment calls vary.
    - SLOWER: a network round trip on every gated write, instead of a
      sub-millisecond regex scan. On a flaky connection this can visibly
      stall the tool call.
    - NOT FREE: a small API cost per call (Groq's free tier covers most use,
      DeepSeek Flash is the fallback at ~$0.14/M tokens either way it's
      cheap, but it's not zero like the regex checks above).

  Fail-open by design: if the model errors, times out, or returns something
  unparseable, these checks silently produce no violations rather than
  blocking your write over a flaky API. They will never turn a working
  session into a stuck one — worst case, they just don't catch anything
  that round.

  Turn them on by explicitly listing them in COPY_SWEEP_CHECKS, e.g.:
    COPY_SWEEP_CHECKS="em_dash,straight_quote,title_case,banned_phrase,throat_clearing,summary_crutch,vague_pronoun,rule_of_three,pontificating"

  Requires GROQ_API_KEY and/or DEEPSEEK_API_KEY in the environment (see the
  main README's Model setup section) and the `requests` package. If neither
  key is set, these checks silently no-op — same fail-open behavior as a
  model error.

See ../SKILL.md for the install steps and the settings.json hook wiring.
"""
from __future__ import annotations

import json
import os
import re
import sys

DEFAULT_EXTENSIONS = (".md", ".txt")

DEFAULT_EXCLUDE_FRAGMENTS = (
    "/node_modules/",
    "/.git/",
    "/.claude/",
    "/.agents/",
    "CHANGELOG.md",
    "README.md",
    "LICENSE",
)

DEFAULT_CHECKS = (
    "em_dash", "straight_quote", "title_case",
    "banned_phrase", "throat_clearing", "summary_crutch",
)

SEMANTIC_CHECKS = ("vague_pronoun", "rule_of_three", "pontificating", "staccato_cadence")

DEFAULT_LONGFORM_WORDS = 400

DEFAULT_BANNED_PHRASES = (
    "leverage", "synergy", "touch base", "circle back", "seamless",
    "hyper-personalized", "future-proof", "next-gen", "best-in-class",
    "cutting-edge", "world-class", "game-changing", "disruptive",
    "revolutionary", "transformative", "mission-driven", "holistic",
    "unlock the power of", "robust solution", "excited to announce",
    "thrilled to announce", "delighted to announce", "proud to announce",
)

EM_DASH = "—"
WE_PRONOUN = re.compile(r"\bWe\b")
HEADING = re.compile(r"^(#{1,3})\s+(.+)$", re.M)
THROAT_CLEARING = re.compile(
    r"^\s*(As you know|In today'?s .{1,40} landscape|We'?re (excited|thrilled) to announce)",
    re.M | re.I,
)
SUMMARY_CRUTCH = re.compile(
    r"^\s*(Bottom line:|Key takeaways?:|In short,|At a glance:)",
    re.M | re.I,
)

SEMANTIC_PROMPT = """Classify the TEXT below for four writing patterns. Respond with ONLY compact JSON, no prose, no markdown fences.

vague_pronoun: true if "this" or "that" stands in for a specific noun the reader has to reconstruct, with no clear antecedent nearby.
rule_of_three: true if there's a list of exactly three items sharing identical grammatical shape (noun-noun-noun or verb-verb-verb) with no variation.
pontificating: true if there's a long preamble or throat-clearing before the actual point, instead of getting to the substance directly.
staccato_cadence: true if the text runs a string of short, choppy declarative sentences back to back (a sentence, then another short sentence, a fragment, a punchline) instead of longer sentences connected by commas or parentheticals. This is the "LinkedIn beat poetry" AI pattern: short sentence. Then another. Fragment. It is distinct from genuinely concise writing, which uses fewer words, not shorter, choppier sentences.

For each true value, include a short "evidence" quote copied verbatim from TEXT.

Respond as: {{"vague_pronoun": {{"flag": bool, "evidence": ""}}, "rule_of_three": {{"flag": bool, "evidence": ""}}, "pontificating": {{"flag": bool, "evidence": ""}}, "staccato_cadence": {{"flag": bool, "evidence": ""}}}}

TEXT:
{text}
"""

SEMANTIC_FIXES = {
    "vague_pronoun": 'Replace "this"/"that" with the specific noun it refers to',
    "rule_of_three": "Break the matched three-item rhythm — vary length or structure",
    "pontificating": "Cut the preamble; open with the actual point",
    "staccato_cadence": "Combine the short sentences into fewer, longer ones connected by commas or parentheticals — flowing, not choppy",
}


def _env_list(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return tuple(p.strip() for p in raw.split(",") if p.strip())


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _is_target_path(file_path: str) -> bool:
    extensions = _env_list("COPY_SWEEP_EXTENSIONS", DEFAULT_EXTENSIONS)
    if not file_path.endswith(extensions):
        return False

    exclude = _env_list("COPY_SWEEP_EXCLUDE", DEFAULT_EXCLUDE_FRAGMENTS)
    if any(frag in file_path for frag in exclude):
        return False

    include = _env_list("COPY_SWEEP_INCLUDE", ())
    if include and not any(frag in file_path for frag in include):
        return False

    return True


def _strip_code_blocks(text: str) -> str:
    """Drop fenced code blocks so quotes/dashes inside code don't false-positive."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def _is_title_case(heading_text: str) -> bool:
    """A heading reads as 'Title Case' if 2+ content words are capitalized."""
    stripped = re.sub(r"[^\w\s]", "", heading_text)
    words = stripped.split()
    if len(words) < 3:
        return False  # short headings are ambiguous either way
    stop = {"a", "an", "the", "and", "but", "or", "for", "nor", "of", "to",
            "in", "on", "at", "by", "with", "is"}
    content = [w for w in words if w and w.lower() not in stop]
    if not content:
        return False
    capitalized = [w for w in content if w[0].isupper()]
    return len(capitalized) >= 2 and len(capitalized) / len(content) >= 0.5


def scan_text(text: str, checks: tuple[str, ...]) -> list[dict]:
    """Return every violation found in text, for the enabled checks only."""
    violations: list[dict] = []
    body = _strip_code_blocks(text)

    if "em_dash" in checks:
        em_dash_occurrences = []  # (line_num, line_text) per occurrence, in order
        for line_num, line in enumerate(body.splitlines(), start=1):
            em_dash_occurrences.extend((line_num, line) for _ in range(line.count(EM_DASH)))
        if em_dash_occurrences:
            longform_words = _env_int("COPY_SWEEP_LONGFORM_WORDS", DEFAULT_LONGFORM_WORDS)
            is_longform = len(body.split()) >= longform_words
            allowed = 1 if is_longform else 0
            for line_num, line in em_dash_occurrences[allowed:]:
                if is_longform:
                    fix = (
                        f"Over budget: 1 em dash allowed per long-form piece "
                        f"(>={longform_words} words), {len(em_dash_occurrences)} used here. "
                        "Keep only the one that's well earned — worth the AI-tell read — "
                        "cut the rest (comma, colon, or a new sentence)."
                    )
                else:
                    fix = (
                        "No em dashes in short-form copy (under "
                        f"{longform_words} words) — use a comma, colon, or a new sentence."
                    )
                violations.append({
                    "rule": "em_dash", "line": line_num,
                    "snippet": line.strip()[:120], "fix": fix,
                })

    if "straight_quote" in checks and '"' in body:
        for line_num, line in enumerate(body.splitlines(), start=1):
            if '"' in line:
                violations.append({
                    "rule": "straight_quote",
                    "line": line_num,
                    "snippet": line.strip()[:120],
                    "fix": "Use curly quotes “ ” ‘ ’ instead of straight \" '",
                })
                break  # one report per file is enough to make the point

    if "we_pronoun" in checks:
        for m in WE_PRONOUN.finditer(body):
            line_start = body.rfind("\n", 0, m.start()) + 1
            line_end = body.find("\n", m.end())
            line = body[line_start:line_end if line_end > 0 else len(body)]
            if line.strip().startswith(">"):  # blockquote / quoted speech
                continue
            violations.append({
                "rule": "we_pronoun",
                "line": body[:m.start()].count("\n") + 1,
                "snippet": line.strip()[:120],
                "fix": 'Use "I" instead of "We" in solo-voice copy',
            })
            break  # one report per file is enough

    if "title_case" in checks:
        for m in HEADING.finditer(body):
            heading_text = m.group(2).strip()
            if _is_title_case(heading_text):
                violations.append({
                    "rule": "title_case",
                    "line": body[:m.start()].count("\n") + 1,
                    "snippet": m.group(0).strip()[:120],
                    "fix": "Use sentence case in headings",
                })

    if "banned_phrase" in checks:
        banned = _env_list("COPY_SWEEP_BANNED_PHRASES", DEFAULT_BANNED_PHRASES)
        low = body.lower()
        for phrase in banned:
            if phrase.lower() in low:
                violations.append({
                    "rule": "banned_phrase",
                    "line": 0,
                    "snippet": phrase,
                    "fix": "Cut it or say the plain-English version",
                })

    if "throat_clearing" in checks:
        for m in THROAT_CLEARING.finditer(body):
            violations.append({
                "rule": "throat_clearing",
                "line": body[:m.start()].count("\n") + 1,
                "snippet": m.group(0).strip()[:120],
                "fix": "Open with the actual point, cut the wind-up",
            })
            break  # one per file is enough to make the point

    if "summary_crutch" in checks:
        for m in SUMMARY_CRUTCH.finditer(body):
            violations.append({
                "rule": "summary_crutch",
                "line": body[:m.start()].count("\n") + 1,
                "snippet": m.group(0).strip()[:120],
                "fix": "Drop the header, just say the thing",
            })
            break

    if any(c in checks for c in SEMANTIC_CHECKS):
        violations.extend(_classify_semantic(body, checks))

    return violations


def _call_groq(prompt: str) -> str | None:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        import requests
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip() or None
    except Exception:
        return None


def _call_deepseek(prompt: str) -> str | None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return None
    try:
        import requests
        resp = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
            },
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip() or None
    except Exception:
        return None


def _classify_semantic(text: str, checks: tuple[str, ...]) -> list[dict]:
    """Model-graded checks. Fail-open: any problem returns no violations
    rather than blocking the write — see the SEMANTIC CHECKS docs above."""
    prompt = SEMANTIC_PROMPT.format(text=text[:4000])
    raw = _call_groq(prompt) or _call_deepseek(prompt)
    if not raw:
        return []

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    candidate = fence.group(1) if fence else raw
    try:
        parsed = json.loads(candidate)
    except Exception:
        span = re.search(r"\{.*\}", candidate, re.DOTALL)
        if not span:
            return []
        try:
            parsed = json.loads(span.group(0))
        except Exception:
            return []

    violations = []
    for check in SEMANTIC_CHECKS:
        if check not in checks:
            continue
        entry = parsed.get(check) or {}
        if entry.get("flag"):
            violations.append({
                "rule": check,
                "line": 0,
                "snippet": str(entry.get("evidence", ""))[:120],
                "fix": SEMANTIC_FIXES[check],
            })
    return violations


def _format_block_message(file_path: str, violations: list[dict]) -> str:
    by_rule: dict[str, int] = {}
    for v in violations:
        by_rule[v["rule"]] = by_rule.get(v["rule"], 0) + 1
    counts = ", ".join(f"{n} {rule.replace('_', ' ')}" for rule, n in by_rule.items())

    lines = [
        f"copy-sweep blocked: {file_path}",
        f"Violations: {counts}",
        "",
        "Specific issues:",
    ]
    for v in violations[:8]:
        lines.append(f"  line {v['line']}: {v['snippet']!r}")
        lines.append(f"    -> {v['fix']}")
    if len(violations) > 8:
        lines.append(f"  ... and {len(violations) - 8} more")
    lines.append("")
    lines.append("Bypass: SKIP_COPY_SWEEP=1 if this is intentional (rare).")
    return "\n".join(lines)


def _extract_content(tool: str, tool_input: dict) -> str:
    if tool == "Write":
        return tool_input.get("content", "") or ""
    if tool == "Edit":
        return tool_input.get("new_string", "") or ""
    if tool == "MultiEdit":
        edits = tool_input.get("edits") or []
        return "\n".join(e.get("new_string", "") or "" for e in edits)
    return ""


def main() -> None:
    if os.environ.get("SKIP_COPY_SWEEP"):
        sys.exit(0)
    if sys.stdin.isatty():
        sys.exit(0)

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    tool = data.get("tool_name", "")
    if tool not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path", "")
    if not _is_target_path(file_path):
        sys.exit(0)

    content = _extract_content(tool, tool_input)
    if not content:
        sys.exit(0)

    checks = _env_list("COPY_SWEEP_CHECKS", DEFAULT_CHECKS)
    violations = scan_text(content, checks)
    if not violations:
        sys.exit(0)

    print(_format_block_message(file_path, violations), file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
