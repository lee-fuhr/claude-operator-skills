#!/usr/bin/env python3
"""
Smart quote fixer.

Converts straight quotes (' and ") into proper typographic quotes,
apostrophes, and primes. Preserves code regions (fenced and inline)
untouched. Supports plain text, markdown, and .docx files.

Usage:
    python fix_quotes.py input.md > output.md
    python fix_quotes.py input.docx -o output.docx
    cat input.txt | python fix_quotes.py > output.txt
"""

import argparse
import re
import sys
from pathlib import Path

# Unicode typographic characters
LSQUO = "‘"  # left single quotation mark
RSQUO = "’"  # right single quotation mark / apostrophe
LDQUO = "“"  # left double quotation mark
RDQUO = "”"  # right double quotation mark
PRIME = "′"  # prime (feet, minutes)
DPRIME = "″"  # double prime (inches, seconds)

# Sentinel chars for stashed code regions. NULL bytes won't appear in
# normal prose, so they're safe placeholders.
STASH_OPEN = "\x00"
STASH_CLOSE = "\x01"


def fix_quotes_in_text(
    text: str,
    no_primes: bool = False,
    apostrophes_only: bool = False,
) -> str:
    """
    Convert straight quotes in a string of text.

    Pipeline:
      1. Stash code regions (fenced and inline) with placeholders.
      2. Convert measurements (digit + ' or ") to primes if enabled.
      3. Convert apostrophes in contractions, possessives, decades.
      4. Convert remaining double quotes (open/close by context).
      5. Convert remaining single quotes (open/close by context).
      6. Restore stashed code regions.
    """
    # --- 1. Stash code regions ---
    protected: list[str] = []

    def stash(match: re.Match) -> str:
        protected.append(match.group(0))
        return f"{STASH_OPEN}{len(protected) - 1}{STASH_CLOSE}"

    # Fenced code blocks (```...```) — multiline, non-greedy
    text = re.sub(r"```.*?```", stash, text, flags=re.DOTALL)
    # Inline code (`...`) — single line, no nested backticks
    text = re.sub(r"`[^`\n]+`", stash, text)

    # --- 2. Measurements ---
    if apostrophes_only:
        pass  # Don't touch measurements in safe mode
    elif no_primes:
        # User prefers straight quotes for measurements. Stash so they
        # survive the curly-quote conversion as straight chars.
        text = re.sub(
            r'(\d+)\'(\d+)"',
            stash,
            text,
        )
        text = re.sub(
            r'\d+\'(?=[\s.,;:!?)\]]|$)',
            stash,
            text,
        )
        text = re.sub(
            r'\d+"(?=[\s.,;:!?)\]]|$)',
            stash,
            text,
        )
    else:
        # Combined feet-and-inches: 6'2" → 6′2″
        text = re.sub(
            r"(\d+)'(\d+)\"",
            lambda m: f"{m.group(1)}{PRIME}{m.group(2)}{DPRIME}",
            text,
        )
        # Standalone feet: digit + ' followed by non-letter
        text = re.sub(
            r"(\d+)'(?=[\s.,;:!?)\]]|$)",
            lambda m: f"{m.group(1)}{PRIME}",
            text,
        )
        # Standalone inches: digit + " followed by non-letter
        text = re.sub(
            r'(\d+)"(?=[\s.,;:!?)\]]|$)',
            lambda m: f"{m.group(1)}{DPRIME}",
            text,
        )

    # --- 3. Apostrophes ---
    # Contractions and intra-word possessives: letter'letter → letter'letter
    # Restricted to letters (not digits) so measurements like 6'2 aren't matched.
    text = re.sub(
        r"([A-Za-z])'([A-Za-z])",
        lambda m: f"{m.group(1)}{RSQUO}{m.group(2)}",
        text,
    )
    # Decade abbreviations: '90s, '00s — leading ' becomes closing apostrophe
    text = re.sub(
        r"(?<!\w)'(?=\d{2}s?\b)",
        RSQUO,
        text,
    )
    # Plural possessives: writers' → writers'
    # Letters only — digit + ' is handled by the measurement pass.
    text = re.sub(
        r"([A-Za-z])'(?=[\s.,;:!?)\]]|$)",
        lambda m: f"{m.group(1)}{RSQUO}",
        text,
    )

    # --- 4. Remaining double quotes ---
    if not apostrophes_only:
        text = _convert_doubles(text)
        # --- 5. Remaining single quotes ---
        text = _convert_singles(text)

    # --- 6. Restore stashed code regions ---
    def restore(match: re.Match) -> str:
        return protected[int(match.group(1))]

    text = re.sub(rf"{STASH_OPEN}(\d+){STASH_CLOSE}", restore, text)

    return text


def _convert_doubles(text: str) -> str:
    """Convert remaining straight double quotes to curly, alternating open/close."""
    result: list[str] = []
    in_quote = False
    opening_context = set(" \t\n\r([{<-—" + LSQUO)
    closing_context = set(" \t\n\r.,;:!?)]}>-—" + RSQUO)
    for i, ch in enumerate(text):
        if ch == '"':
            prev = text[i - 1] if i > 0 else " "
            nxt = text[i + 1] if i < len(text) - 1 else " "
            if prev in opening_context or i == 0:
                result.append(LDQUO)
                in_quote = True
            elif nxt in closing_context or i == len(text) - 1:
                result.append(RDQUO)
                in_quote = False
            else:
                # Genuinely ambiguous — use state
                result.append(RDQUO if in_quote else LDQUO)
                in_quote = not in_quote
        else:
            result.append(ch)
    return "".join(result)


def _convert_singles(text: str) -> str:
    """Convert remaining straight single quotes to curly, alternating open/close."""
    result: list[str] = []
    in_quote = False
    opening_context = set(" \t\n\r([{<\"" + LDQUO)
    closing_context = set(" \t\n\r.,;:!?)]}>\"" + RDQUO)
    for i, ch in enumerate(text):
        if ch == "'":
            prev = text[i - 1] if i > 0 else " "
            nxt = text[i + 1] if i < len(text) - 1 else " "
            if prev in opening_context or i == 0:
                result.append(LSQUO)
                in_quote = True
            elif nxt in closing_context or i == len(text) - 1:
                result.append(RSQUO)
                in_quote = False
            else:
                result.append(RSQUO if in_quote else LSQUO)
                in_quote = not in_quote
        else:
            result.append(ch)
    return "".join(result)


def fix_docx(input_path: Path, output_path: Path, **kwargs) -> None:
    """Apply quote fixing to a .docx file, preserving run-level formatting."""
    try:
        from docx import Document
    except ImportError:
        sys.exit(
            "Error: python-docx is required for .docx files. "
            "Install with: pip install python-docx"
        )

    doc = Document(str(input_path))

    for para in doc.paragraphs:
        _fix_paragraph_runs(para, **kwargs)

    # Tables can contain paragraphs in cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    _fix_paragraph_runs(para, **kwargs)

    # Headers and footers
    for section in doc.sections:
        for container in (section.header, section.footer):
            for para in container.paragraphs:
                _fix_paragraph_runs(para, **kwargs)

    doc.save(str(output_path))


def _fix_paragraph_runs(para, **kwargs) -> None:
    """
    Fix quotes in a paragraph while preserving each run's formatting.

    Strategy: concatenate run text, fix the whole paragraph (so context
    is preserved across run boundaries), then redistribute character-for-
    character back to each run. Quote fixes are 1:1 character substitutions
    (one straight char → one curly char), so lengths stay aligned.
    """
    runs = para.runs
    if not runs:
        return

    full_text = "".join(run.text for run in runs)
    if not full_text:
        return

    fixed = fix_quotes_in_text(full_text, **kwargs)

    if len(fixed) == len(full_text):
        pos = 0
        for run in runs:
            run_len = len(run.text)
            run.text = fixed[pos : pos + run_len]
            pos += run_len
    else:
        # Length changed (shouldn't happen with current rules; fallback)
        runs[0].text = fixed
        for run in runs[1:]:
            run.text = ""


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert straight quotes to typographic (curly) quotes, "
            "apostrophes, and primes."
        ),
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input file (.txt, .md, .docx). Reads stdin if omitted.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Output file. Defaults to stdout for text; "
            "for .docx, defaults to <input>_fixed.docx."
        ),
    )
    parser.add_argument(
        "--no-primes",
        action="store_true",
        help="Don't convert measurements to primes; use straight quotes.",
    )
    parser.add_argument(
        "--apostrophes-only",
        action="store_true",
        help="Safe mode: only convert apostrophes, leave double quotes alone.",
    )
    args = parser.parse_args()

    kwargs = {
        "no_primes": args.no_primes,
        "apostrophes_only": args.apostrophes_only,
    }

    if args.input:
        input_path = Path(args.input)
        if input_path.suffix.lower() == ".docx":
            if args.output:
                output_path = Path(args.output)
            else:
                output_path = input_path.with_name(
                    f"{input_path.stem}_fixed{input_path.suffix}"
                )
            fix_docx(input_path, output_path, **kwargs)
            print(f"Wrote: {output_path}", file=sys.stderr)
        else:
            text = input_path.read_text(encoding="utf-8")
            fixed = fix_quotes_in_text(text, **kwargs)
            if args.output:
                Path(args.output).write_text(fixed, encoding="utf-8")
            else:
                sys.stdout.write(fixed)
    else:
        text = sys.stdin.read()
        fixed = fix_quotes_in_text(text, **kwargs)
        sys.stdout.write(fixed)


if __name__ == "__main__":
    main()
