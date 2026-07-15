"""Tests for check_repo.py -- each test builds a small synthetic repo under
tmp_path so nothing here ever touches the real repo root."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_repo  # noqa: E402


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


# -- denylist --------------------------------------------------------------

def test_denylist_catches_a_leaked_internal_path(tmp_path):
    write(tmp_path / "README.md", "See /Users/lee/CC for the source.\n")
    findings = check_repo.check_denylist(root=tmp_path)
    assert any("denylist hit" in f for f in findings)


def test_denylist_clean_repo_has_no_findings(tmp_path):
    write(tmp_path / "README.md", "A perfectly ordinary public readme.\n")
    assert check_repo.check_denylist(root=tmp_path) == []


def test_denylist_exempts_itself(tmp_path):
    scripts = tmp_path / "scripts"
    write(scripts / "check_repo.py", "DENYLIST = ['/Users/lee']\n")
    findings = check_repo.check_denylist(root=tmp_path)
    assert findings == []


# -- self-references ---------------------------------------------------------

def test_self_reference_catches_a_stale_pre_rename_invocation(tmp_path):
    write(
        tmp_path / "skills" / "ww-rule15" / "SKILL.md",
        "---\nname: ww-rule15\n---\nInvoke with /rule15 before marking done.\n",
    )
    findings = check_repo.check_self_references(root=tmp_path)
    assert len(findings) == 1
    assert "ww-rule15" in findings[0]
    assert "/rule15" in findings[0]


def test_self_reference_does_not_flag_the_correct_prefixed_form(tmp_path):
    write(
        tmp_path / "skills" / "ww-rule15" / "SKILL.md",
        "---\nname: ww-rule15\n---\nInvoke with /ww-rule15 before marking done.\n",
    )
    assert check_repo.check_self_references(root=tmp_path) == []


def test_self_reference_ignores_unprefixed_skill_folders(tmp_path):
    write(
        tmp_path / "skills" / "weekend-burn" / "SKILL.md",
        "Some doc that mentions /weekend-burn.\n",
    )
    # folder itself has no qq-/ww- prefix -- not this check's concern
    assert check_repo.check_self_references(root=tmp_path) == []


# -- anchors -----------------------------------------------------------------

def test_anchor_check_catches_a_broken_link(tmp_path):
    write(tmp_path / "README.md", "See [it](#nonexistent-section).\n\n## Real section\n")
    findings = check_repo.check_anchors(root=tmp_path)
    assert any("nonexistent-section" in f for f in findings)


def test_anchor_check_passes_a_matching_link(tmp_path):
    write(tmp_path / "README.md", "See [it](#real-section).\n\n## Real section\n")
    assert check_repo.check_anchors(root=tmp_path) == []


# -- straight quotes -----------------------------------------------------------

def test_straight_quotes_caught_in_prose(tmp_path):
    write(tmp_path / "README.md", "This isn't curly.\n")
    findings = check_repo.check_straight_quotes(root=tmp_path)
    assert len(findings) == 1


def test_straight_quotes_exempt_in_yaml_frontmatter(tmp_path):
    write(
        tmp_path / "docs" / "example.html",
        '---\ntitle: "A title"\n---\n<html><body>curly text’s fine here</body></html>\n',
    )
    assert check_repo.check_straight_quotes(root=tmp_path) == []


def test_straight_quotes_exempt_in_html_tag_attributes(tmp_path):
    write(
        tmp_path / "docs" / "example.html",
        '---\ntitle: "x"\n---\n<meta name="description" content="fine, curly’s here too">\n',
    )
    assert check_repo.check_straight_quotes(root=tmp_path) == []


def test_straight_quotes_exempt_in_code_spans(tmp_path):
    write(tmp_path / "README.md", "Run `python3 audit.py \"a/b/c\"` and you're set.\n")
    # the backtick span is exempt; "you're" still has a real straight apostrophe
    findings = check_repo.check_straight_quotes(root=tmp_path)
    assert len(findings) == 1


def test_straight_quotes_exempt_in_html_pre_code_block_content(tmp_path):
    write(
        tmp_path / "docs" / "example.html",
        '---\ntitle: "x"\n---\n<p>fine</p>\n<pre><code class="language-json">\n'
        '{\n  "type": "command"\n}\n</code></pre>\n<p>more, curly’s fine</p>\n',
    )
    assert check_repo.check_straight_quotes(root=tmp_path) == []


def test_straight_quotes_exempt_in_style_block_css(tmp_path):
    write(
        tmp_path / "docs" / "example.html",
        '---\ntitle: "x"\n---\n<style>\n  font: 17px sans-serif, "Segoe UI";\n</style>\n<p>curly’s fine</p>\n',
    )
    assert check_repo.check_straight_quotes(root=tmp_path) == []


def test_straight_quotes_line_numbers_survive_frontmatter_stripping(tmp_path):
    # a real straight quote on line 6 (after a 3-line frontmatter block)
    # must be reported as line 6, not shifted by however many lines the
    # frontmatter itself took up
    write(
        tmp_path / "docs" / "example.html",
        '---\ntitle: "x"\n---\n<p>one</p>\n<p>two</p>\n<p>it isn\'t curly here</p>\n',
    )
    findings = check_repo.check_straight_quotes(root=tmp_path)
    assert len(findings) == 1
    assert findings[0].endswith(":6 straight quote outside code/markup")


# -- docs parity ---------------------------------------------------------------

def test_docs_parity_flags_a_skill_with_no_doc_page(tmp_path):
    write(tmp_path / "skills" / "qq-example" / "SKILL.md", "name: qq-example\n")
    write(tmp_path / "docs" / "index.html", "<html></html>\n")
    findings = check_repo.check_docs_parity(root=tmp_path)
    assert any("qq-example" in f for f in findings)


def test_docs_parity_passes_when_doc_page_and_index_link_both_exist(tmp_path):
    write(tmp_path / "skills" / "qq-example" / "SKILL.md", "name: qq-example\n")
    write(tmp_path / "docs" / "qq-example.html", "<html></html>\n")
    write(tmp_path / "docs" / "index.html", '<a href="/qq-example/">qq-example</a>\n')
    assert check_repo.check_docs_parity(root=tmp_path) == []


def test_docs_parity_respects_the_exemptions_file(tmp_path):
    write(tmp_path / "skills" / "qq-audit-backend" / "SKILL.md", "name: qq-audit-backend\n")
    write(tmp_path / "docs" / "index.html", "<html></html>\n")
    write(
        tmp_path / "scripts" / "docs_parity_exemptions.json",
        '{"qq-audit-backend": "domain skill folded into /qq-audit"}',
    )
    assert check_repo.check_docs_parity(root=tmp_path) == []


# -- banner ---------------------------------------------------------------

def test_banner_check_catches_a_skill_missing_the_banner(tmp_path):
    write(tmp_path / "skills" / "qq-example" / "SKILL.md", "---\nname: qq-example\n---\n# Example\n")
    findings = check_repo.check_banner(root=tmp_path)
    assert any("qq-example" in f for f in findings)


def test_banner_check_passes_a_skill_with_the_banner(tmp_path):
    write(
        tmp_path / "skills" / "qq-example" / "SKILL.md",
        "---\nname: qq-example\n---\n\n> Part of [Claude Code operator skills](url).\n\n# Example\n",
    )
    assert check_repo.check_banner(root=tmp_path) == []


# -- end to end on the real repo ------------------------------------------------

def test_real_repo_is_clean():
    """The actual repo this script ships in should pass every check. If this
    fails, something regressed -- fix the repo, don't loosen the check."""
    total = sum(len(fn()) for _, fn in check_repo.CHECKS)
    assert total == 0
