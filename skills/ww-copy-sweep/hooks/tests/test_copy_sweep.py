"""Tests for copy_sweep.py — the PreToolUse hook packaged in the copy-sweep skill."""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from unittest.mock import patch

HOOKS_DIR = Path(__file__).resolve().parent.parent
if str(HOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(HOOKS_DIR))


def _load():
    if "copy_sweep" in sys.modules:
        del sys.modules["copy_sweep"]
    return importlib.import_module("copy_sweep")


def _longform(body_line: str, words: int = 420) -> str:
    filler = " ".join(["word"] * words)
    return f"{filler}\n\n{body_line}"


class TestEmDashBudget:
    def test_short_form_zero_em_dashes_allowed(self):
        m = _load()
        violations = m.scan_text("Hey — quick note.", m.DEFAULT_CHECKS)
        em = [v for v in violations if v["rule"] == "em_dash"]
        assert len(em) == 1

    def test_long_form_one_em_dash_within_budget(self):
        m = _load()
        text = _longform("This one earns it — right here.")
        violations = m.scan_text(text, m.DEFAULT_CHECKS)
        em = [v for v in violations if v["rule"] == "em_dash"]
        assert len(em) == 0

    def test_long_form_second_em_dash_over_budget(self):
        m = _load()
        text = _longform("First — earns it. Second — does not.")
        violations = m.scan_text(text, m.DEFAULT_CHECKS)
        em = [v for v in violations if v["rule"] == "em_dash"]
        assert len(em) == 1

    def test_threshold_configurable_via_env(self, monkeypatch):
        m = _load()
        monkeypatch.setenv("COPY_SWEEP_LONGFORM_WORDS", "10")
        text = _longform("This earns it — right here.", words=12)
        violations = m.scan_text(text, m.DEFAULT_CHECKS)
        em = [v for v in violations if v["rule"] == "em_dash"]
        assert len(em) == 0  # 12 words crosses the lowered threshold


class TestStraightQuote:
    def test_detects_straight_double_quote(self):
        m = _load()
        violations = m.scan_text('She said "hi" to me.', m.DEFAULT_CHECKS)
        assert any(v["rule"] == "straight_quote" for v in violations)

    def test_curly_quotes_pass(self):
        m = _load()
        violations = m.scan_text("She said “hi” to me.", m.DEFAULT_CHECKS)
        assert not any(v["rule"] == "straight_quote" for v in violations)


class TestTitleCase:
    def test_detects_title_case_heading(self):
        m = _load()
        violations = m.scan_text("## The Big New Feature Launch\n\ntext", m.DEFAULT_CHECKS)
        assert any(v["rule"] == "title_case" for v in violations)

    def test_sentence_case_passes(self):
        m = _load()
        violations = m.scan_text("## The big new feature launch\n\ntext", m.DEFAULT_CHECKS)
        assert not any(v["rule"] == "title_case" for v in violations)


class TestBannedPhrase:
    def test_detects_default_banned_word(self):
        m = _load()
        violations = m.scan_text("Let's leverage this synergy.", m.DEFAULT_CHECKS)
        assert any(v["rule"] == "banned_phrase" for v in violations)

    def test_clean_copy_passes(self):
        m = _load()
        violations = m.scan_text("Here's the update.", m.DEFAULT_CHECKS)
        assert not any(v["rule"] == "banned_phrase" for v in violations)

    def test_custom_list_overrides_default(self, monkeypatch):
        m = _load()
        monkeypatch.setenv("COPY_SWEEP_BANNED_PHRASES", "moist")
        violations = m.scan_text("Let's leverage this synergy.", m.DEFAULT_CHECKS)
        # "leverage"/"synergy" no longer banned once the env var overrides the default list
        assert not any(v["rule"] == "banned_phrase" for v in violations)
        violations2 = m.scan_text("That cake is moist.", m.DEFAULT_CHECKS)
        assert any(v["rule"] == "banned_phrase" for v in violations2)


class TestThroatClearing:
    def test_detects_as_you_know(self):
        m = _load()
        violations = m.scan_text("As you know, the launch is live.", m.DEFAULT_CHECKS)
        assert any(v["rule"] == "throat_clearing" for v in violations)

    def test_direct_opener_passes(self):
        m = _load()
        violations = m.scan_text("The launch is live.", m.DEFAULT_CHECKS)
        assert not any(v["rule"] == "throat_clearing" for v in violations)


class TestSummaryCrutch:
    def test_detects_bottom_line(self):
        m = _load()
        violations = m.scan_text("Bottom line: it shipped.", m.DEFAULT_CHECKS)
        assert any(v["rule"] == "summary_crutch" for v in violations)

    def test_plain_text_passes(self):
        m = _load()
        violations = m.scan_text("It shipped.", m.DEFAULT_CHECKS)
        assert not any(v["rule"] == "summary_crutch" for v in violations)


class TestSemanticChecksOffByDefault:
    def test_not_run_without_being_listed(self, monkeypatch):
        m = _load()
        called = {"n": 0}

        def fake_classify(text, checks):
            called["n"] += 1
            return []

        monkeypatch.setattr(m, "_classify_semantic", fake_classify)
        m.scan_text("This is a thing.", m.DEFAULT_CHECKS)
        assert called["n"] == 0

    def test_runs_when_explicitly_listed(self, monkeypatch):
        m = _load()
        called = {"n": 0}

        def fake_classify(text, checks):
            called["n"] += 1
            return [{"rule": "vague_pronoun", "line": 0, "snippet": "x", "fix": "y"}]

        monkeypatch.setattr(m, "_classify_semantic", fake_classify)
        checks = m.DEFAULT_CHECKS + ("vague_pronoun",)
        violations = m.scan_text("This is a thing.", checks)
        assert called["n"] == 1
        assert any(v["rule"] == "vague_pronoun" for v in violations)

    def test_staccato_cadence_in_semantic_schema(self, monkeypatch):
        m = _load()
        captured = {}

        def fake_groq(prompt):
            captured["prompt"] = prompt
            return '{"vague_pronoun": {"flag": false, "evidence": ""}, "rule_of_three": {"flag": false, "evidence": ""}, "pontificating": {"flag": false, "evidence": ""}, "staccato_cadence": {"flag": true, "evidence": "Short. Punchy."}}'

        monkeypatch.setattr(m, "_call_groq", fake_groq)
        checks = m.DEFAULT_CHECKS + ("staccato_cadence",)
        violations = m.scan_text("Things are clicking. Short. Punchy.", checks)
        assert "staccato_cadence" in captured["prompt"]
        assert any(v["rule"] == "staccato_cadence" for v in violations)

    def test_fail_open_with_no_api_keys(self, monkeypatch):
        m = _load()
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        result = m._classify_semantic("Some text.", ("vague_pronoun",))
        assert result == []

    def test_fail_open_on_network_error(self, monkeypatch):
        m = _load()
        monkeypatch.setenv("GROQ_API_KEY", "fake")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "fake")

        def broken(prompt):
            return None

        monkeypatch.setattr(m, "_call_groq", broken)
        monkeypatch.setattr(m, "_call_deepseek", broken)
        result = m._classify_semantic("Some text.", ("vague_pronoun",))
        assert result == []


class TestPathAndBypass:
    def test_excluded_path_returns_true_extensions_false(self):
        m = _load()
        assert m._is_target_path("/tmp/README.md") is False
        assert m._is_target_path("/tmp/notes.md") is True
        assert m._is_target_path("/tmp/notes.py") is False

    def test_include_scopes_to_fragment(self, monkeypatch):
        m = _load()
        monkeypatch.setenv("COPY_SWEEP_INCLUDE", "drafts/")
        assert m._is_target_path("/tmp/drafts/a.md") is True
        assert m._is_target_path("/tmp/other/a.md") is False

    def test_bypass_env_var(self, monkeypatch):
        import io
        import json as jsonlib

        monkeypatch.setenv("SKIP_COPY_SWEEP", "1")
        m = _load()
        payload = jsonlib.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/notes.md", "content": "Hey — short."},
        })

        class NonTty(io.StringIO):
            def isatty(self):
                return False

        code = 0
        with patch.object(sys, "stdin", NonTty(payload)):
            try:
                m.main()
            except SystemExit as e:
                code = e.code or 0
        assert code == 0
