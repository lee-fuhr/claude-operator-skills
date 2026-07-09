#!/usr/bin/env python3
"""
PreToolUse hook: catches AI-tell punctuation and formatting before it ever
lands in a file — em dashes, straight quotes, title-case headings, and
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

  COPY_SWEEP_CHECKS="em_dash,straight_quote,title_case"
      Comma-separated list of checks to run. Available: em_dash,
      straight_quote, we_pronoun, title_case. Default: the first three.
      we_pronoun is off by default — it's a "solo operator" voice rule, not
      universal; add it back if you write alone and want "I" enforced.

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

DEFAULT_CHECKS = ("em_dash", "straight_quote", "title_case")

EM_DASH = "—"
WE_PRONOUN = re.compile(r"\bWe\b")
HEADING = re.compile(r"^(#{1,3})\s+(.+)$", re.M)


def _env_list(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return tuple(p.strip() for p in raw.split(",") if p.strip())


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

    if "em_dash" in checks and EM_DASH in body:
        for line_num, line in enumerate(body.splitlines(), start=1):
            if EM_DASH in line:
                violations.append({
                    "rule": "em_dash",
                    "line": line_num,
                    "snippet": line.strip()[:120],
                    "fix": "Replace — with a comma, colon, or a new sentence",
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
