#!/usr/bin/env python3
"""
Deterministic consistency checks for this repo. Run before every commit that
touches skills/, docs/, or README.md:

    python3 scripts/check_repo.py

Exits 0 with no output on a clean repo. Exits 1 and prints every finding
otherwise. Encodes the checks a human did by hand, repeatedly, the night
this repo grew from 7 skills to 33+: a stale self-reference left over from
a rename, a leaked internal path, a broken anchor link, a skill with no
docs page or vice versa, a straight quote in prose.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Terms that must never appear in anything public. Seeded from what actually
# leaked this repo before: internal system names, client names, real local
# paths. Add to this list the moment a new leak class is found -- don't fix
# one instance and leave the class uncaught.
DENYLIST = [
    "/Users/lee",
    "_ Operations",
    "_ System",
    r"\bLFI\b",
    r"\bImply\b",
    r"\bSlide\b",
    "leefur@gmail.com",
]

EXEMPT_FILES = {
    "scripts/check_repo.py",  # this file quotes the denylist itself
    "scripts/test_check_repo.py",  # tests use denylist terms as fixture text
}


def find(pattern, text, flags=0):
    return list(re.finditer(pattern, text, flags))


def load_docs_parity_exemptions(root):
    path = root / "scripts" / "docs_parity_exemptions.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def check_denylist(root=ROOT):
    findings = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if rel in EXEMPT_FILES or rel.startswith(".git/"):
            continue
        if path.suffix not in {".md", ".html", ".py", ".sh", ".json"}:
            continue
        try:
            text = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        for term in DENYLIST:
            if re.search(term, text):
                findings.append(f"denylist hit '{term}' in {rel}")
    return findings


def check_self_references(root=ROOT):
    """A qq-/ww- skill's own files should never reference its bare
    (unprefixed) name as a standalone invocation string -- that's the
    signature of a stale reference left over from before a rename."""
    findings = []
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return findings
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        prefix = None
        for p in ("qq-", "ww-"):
            if name.startswith(p):
                prefix = p
                break
        if prefix is None:
            continue
        bare = name[len(prefix):]
        pattern = re.compile(r"(?<![\w/-])/" + re.escape(bare) + r"(?![\w-])")
        for path in skill_dir.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".py", ".sh"}:
                continue
            try:
                text = path.read_text()
            except (UnicodeDecodeError, OSError):
                continue
            for m in find(pattern, text):
                line_no = text[: m.start()].count("\n") + 1
                findings.append(
                    f"{path.relative_to(root)}:{line_no} references bare "
                    f"'/{bare}' -- did a rename leave this behind? Should "
                    f"probably be '/{name}'"
                )
    return findings


def check_anchors(root=ROOT):
    findings = []
    readme = root / "README.md"
    if not readme.exists():
        return findings
    text = readme.read_text()
    headers = re.findall(r"^## (.+)$", text, re.MULTILINE)

    def slugify(h):
        s = h.lower()
        s = re.sub(r"[^\w\s-]", "", s)
        s = re.sub(r"\s+", "-", s.strip())
        return s

    slugs = {slugify(h) for h in headers}
    for m in find(r"\]\(#([a-z0-9-]+)\)", text):
        anchor = m.group(1)
        if anchor not in slugs:
            line_no = text[: m.start()].count("\n") + 1
            findings.append(f"README.md:{line_no} links to #{anchor}, no matching header")
    return findings


def _blank(m):
    """Replace a match with an equal number of newlines (never fewer) so
    every later line-number calculation still lines up with the real file,
    the same way a human counting lines in an editor would."""
    return "\n" * m.group(0).count("\n")


def _strip_non_prose(text):
    """Blank out everything that legitimately uses straight quotes: YAML
    frontmatter, fenced code blocks, HTML <pre><code>/<code> block content,
    inline markdown code spans, and HTML tags themselves. Blanking (not
    deleting) keeps every remaining line number aligned with the real file."""
    no_code = text
    no_code = re.sub(r"\A---\n.*?\n---\n", _blank, no_code, flags=re.DOTALL)
    no_code = re.sub(r"```.*?```", _blank, no_code, flags=re.DOTALL)
    no_code = re.sub(r"<style>.*?</style>", _blank, no_code, flags=re.DOTALL)
    no_code = re.sub(r"<script>.*?</script>", _blank, no_code, flags=re.DOTALL)
    no_code = re.sub(r"<pre>.*?</pre>", _blank, no_code, flags=re.DOTALL)
    no_code = re.sub(r"<code[^>]*>.*?</code>", _blank, no_code, flags=re.DOTALL)
    no_code = re.sub(r"`[^`]*`", _blank, no_code)
    no_code = re.sub(r"<[^>]*>", _blank, no_code)
    return no_code


def check_straight_quotes(root=ROOT):
    findings = []
    targets = [root / "README.md"] + sorted((root / "docs").glob("*.html"))
    for path in targets:
        if not path.exists():
            continue
        no_code = _strip_non_prose(path.read_text())
        for m in find(r"['\"]", no_code):
            line_no = no_code[: m.start()].count("\n") + 1
            findings.append(f"{path.relative_to(root)}:{line_no} straight quote outside code/markup")
    return findings


def check_docs_parity(root=ROOT):
    """Every skills/ folder (except a registered exemption) should have a
    docs/<name>.html, and every docs/<name>.html should be linked from
    docs/index.html."""
    findings = []
    skills_dir = root / "skills"
    docs_dir = root / "docs"
    index = docs_dir / "index.html"
    if not skills_dir.exists() or not docs_dir.exists():
        return findings
    exemptions = load_docs_parity_exemptions(root)
    index_text = index.read_text() if index.exists() else ""
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        if name in exemptions:
            continue
        doc_page = docs_dir / f"{name}.html"
        if not doc_page.exists():
            findings.append(
                f"skills/{name}/ has no docs/{name}.html -- add one, or add "
                f"an exemption + reason to scripts/docs_parity_exemptions.json"
            )
            continue
        if f'href="/{name}/"' not in index_text:
            findings.append(f"docs/index.html has no link to /{name}/ -- add an entry")
    return findings


def check_banner(root=ROOT):
    """Every skill's SKILL.md should carry the parent-repo banner blockquote.
    Found missing on all 15 audit-domain skills after the audit-framework
    merge -- an entire family slipped through because docs-parity treats
    them as exempt sub-components, which says nothing about their own
    SKILL.md content."""
    findings = []
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return findings
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text()
        if "Part of [Claude Code operator skills]" not in text and "Part of [Operator Skills]" not in text:
            findings.append(f"skills/{skill_dir.name}/SKILL.md has no parent-repo banner")
    return findings


CHECKS = [
    ("Denylist (leaked internal names/paths)", check_denylist),
    ("Stale self-references (rename left something behind)", check_self_references),
    ("README anchor links", check_anchors),
    ("Straight quotes in prose", check_straight_quotes),
    ("Skill <-> docs page parity", check_docs_parity),
    ("Parent-repo banner on every skill", check_banner),
]


def main():
    total = 0
    for label, fn in CHECKS:
        findings = fn()
        if findings:
            print(f"\n[{label}] {len(findings)} finding(s):")
            for f in findings:
                print(f"  - {f}")
            total += len(findings)
    if total:
        print(f"\n{total} finding(s) total. Fix before committing.")
        return 1
    print("Clean: denylist, self-references, anchors, quotes, docs parity all pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
