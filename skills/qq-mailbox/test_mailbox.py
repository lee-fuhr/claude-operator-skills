#!/usr/bin/env python3
"""TDD for mailbox.py — hardened two-role coordination mailbox (core cases).

Hardens the ad-hoc pattern of two named roles passing JSONL messages back and
forth, first proven in a real live coordination lane between an overseer and
a build session.

Concurrency-race and real-production-data tests live in
test_mailbox_concurrency.py (kept separate to stay under the 500-line file
cap, Bible §6.7).

Tests are pure I/O against tmp_path — never touch a real lane directory.
"""
import json
from pathlib import Path

import pytest


# ── send() ──────────────────────────────────────────────────────────────────


def test_send_creates_sync_dir_and_file(tmp_path):
    from mailbox import send

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="hi")

    out = tmp_path / "_sync" / "builder-to-overseer.jsonl"
    assert out.exists()
    lines = out.read_text().splitlines()
    assert len(lines) == 1
    envelope = json.loads(lines[0])
    assert envelope["from"] == "builder"
    assert envelope["to"] == "overseer"
    assert envelope["kind"] == "reconnect"
    assert envelope["msg"] == "hi"


def test_send_generates_unique_id_and_iso_ts(tmp_path):
    from mailbox import send
    from datetime import datetime

    e1 = send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="a")
    e2 = send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="b")

    assert e1["id"] != e2["id"]
    assert e1["id"] and e2["id"]
    # ts must be real, parseable ISO8601 -- not a guess/placeholder
    datetime.fromisoformat(e1["ts"])
    datetime.fromisoformat(e2["ts"])


def test_send_appends_multiple_messages_in_order(tmp_path):
    from mailbox import send

    for i in range(5):
        send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg=f"msg-{i}")

    out = tmp_path / "_sync" / "builder-to-overseer.jsonl"
    lines = [json.loads(l) for l in out.read_text().splitlines()]
    assert [e["msg"] for e in lines] == [f"msg-{i}" for i in range(5)]


def test_send_omits_optional_fields_when_not_provided(tmp_path):
    from mailbox import send

    envelope = send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="hi")
    assert "ref" not in envelope
    assert "artifacts" not in envelope


def test_send_includes_optional_fields_when_provided(tmp_path):
    from mailbox import send

    envelope = send(
        tmp_path,
        from_role="builder",
        to_role="overseer",
        kind="build-delivered",
        msg="done",
        needs_reply=True,
        ref="abc123",
        artifacts=["spec.md", "done.md"],
    )
    assert envelope["ref"] == "abc123"
    assert envelope["artifacts"] == ["spec.md", "done.md"]
    assert envelope["needs_reply"] is True


def test_send_writes_one_line_per_call_single_write_syscall(tmp_path, monkeypatch):
    """Crash-safety requirement: the JSONL append must be ONE write() call
    carrying the whole line (json + newline), never multiple writes that could
    interleave with a concurrent appender or leave a torn line on a crash."""
    import mailbox

    write_calls = []
    real_open = open

    class TrackingFile:
        def __init__(self, f):
            self._f = f

        def write(self, data):
            write_calls.append(data)
            return self._f.write(data)

        def __enter__(self):
            return self

        def __exit__(self, *a):
            self._f.close()

    def fake_open(path, mode="r", encoding=None):
        f = real_open(path, mode, encoding=encoding)
        if mode == "a":
            return TrackingFile(f)
        return f

    monkeypatch.setattr(mailbox, "open", fake_open, raising=False)
    mailbox.send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="hi")

    assert len(write_calls) == 1
    assert write_calls[0].endswith("\n")


# ── check() — basic read + grouping ─────────────────────────────────────────


def test_check_reads_unread_messages_from_single_sender(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="hi")
    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="hi again")

    result = check(tmp_path, role="overseer", from_role="builder")
    assert len(result["unread"]) == 2
    assert result["unread"][0]["msg"] == "hi"
    assert result["unread"][1]["msg"] == "hi again"


def test_check_returns_empty_when_no_new_messages(tmp_path):
    from mailbox import check

    result = check(tmp_path, role="overseer", from_role="builder")
    assert result["unread"] == []
    assert result["by_kind"] == {}
    assert result["action_needed"] == []


def test_check_second_call_only_returns_new_messages(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="first")
    first = check(tmp_path, role="overseer", from_role="builder")
    assert len(first["unread"]) == 1

    second_empty = check(tmp_path, role="overseer", from_role="builder")
    assert second_empty["unread"] == []

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="second")
    second = check(tmp_path, role="overseer", from_role="builder")
    assert len(second["unread"]) == 1
    assert second["unread"][0]["msg"] == "second"


def test_check_groups_by_kind(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="design-task", msg="a")
    send(tmp_path, from_role="builder", to_role="overseer", kind="design-task", msg="b")
    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="c")

    result = check(tmp_path, role="overseer", from_role="builder")
    assert len(result["by_kind"]["design-task"]) == 2
    assert len(result["by_kind"]["reconnect"]) == 1


# ── cursor atomicity + monotonicity ─────────────────────────────────────────


def test_check_writes_cursor_file_via_atomic_temp_rename(tmp_path, monkeypatch):
    """Bible §1.9: temp file in the same directory, then os.replace() -- never
    a direct open-write to the cursor file."""
    import mailbox

    replace_calls = []
    real_replace = mailbox.os.replace

    def tracking_replace(src, dst):
        # The temp file must exist and be a sibling of the real cursor path
        # at the moment of replace -- proves temp+rename, not direct write.
        assert Path(src).parent == Path(dst).parent
        assert Path(src) != Path(dst)
        replace_calls.append((src, dst))
        return real_replace(src, dst)

    monkeypatch.setattr(mailbox.os, "replace", tracking_replace)

    mailbox.send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="hi")
    mailbox.check(tmp_path, role="overseer", from_role="builder")

    assert len(replace_calls) == 1
    cursor_path = tmp_path / "_sync" / ".cursor-overseer.json"
    assert cursor_path.exists()
    # Must be valid, complete JSON -- never left truncated
    json.loads(cursor_path.read_text())


def test_check_cursor_is_monotonic_never_moves_backward(tmp_path):
    from mailbox import send, check, _load_cursor, _cursor_path

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="a")
    check(tmp_path, role="overseer", from_role="builder")
    cursor_after_1 = _load_cursor(_cursor_path(tmp_path, "overseer"))

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="b")
    check(tmp_path, role="overseer", from_role="builder")
    cursor_after_2 = _load_cursor(_cursor_path(tmp_path, "overseer"))

    key = "builder-to-overseer.jsonl"
    assert cursor_after_2[key] >= cursor_after_1[key]
    assert cursor_after_2[key] == 2


def test_check_survives_missing_cursor_file(tmp_path):
    """First-ever check() for a role: no cursor file exists yet. Must not
    crash -- must treat everything as unread."""
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="a")
    result = check(tmp_path, role="overseer", from_role="builder")
    assert len(result["unread"]) == 1


def test_check_survives_corrupt_cursor_file(tmp_path):
    """A cursor file that somehow got corrupted (e.g. a prior crash before this
    module's atomic-write discipline existed) must not crash check() -- it
    should fall back to treating that file's position as unread-from-start
    rather than raising."""
    from mailbox import send, check, _cursor_path

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="a")
    cursor_path = _cursor_path(tmp_path, "overseer")
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    cursor_path.write_text("{not valid json")

    result = check(tmp_path, role="overseer", from_role="builder")
    assert len(result["unread"]) == 1


# ── multi-sender merge ───────────────────────────────────────────────────────


def test_check_merges_multiple_senders_chronologically(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="from-builder-1")
    send(tmp_path, from_role="qc", to_role="overseer", kind="reconnect", msg="from-qc-1")
    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="from-builder-2")

    result = check(tmp_path, role="overseer")  # from_role=None -> merge all senders
    msgs = [e["msg"] for e in result["unread"]]
    assert msgs == ["from-builder-1", "from-qc-1", "from-builder-2"]
    assert set(e["from"] for e in result["unread"]) == {"builder", "qc"}


def test_check_from_role_none_only_touches_files_addressed_to_role(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="to-overseer")
    send(tmp_path, from_role="overseer", to_role="builder", kind="reconnect", msg="to-builder")

    result = check(tmp_path, role="overseer")
    assert len(result["unread"]) == 1
    assert result["unread"][0]["msg"] == "to-overseer"


# ── taxonomy + action hints ──────────────────────────────────────────────────


def test_check_attaches_taxonomy_hint_to_known_kind(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="design-task", msg="architect X")
    result = check(tmp_path, role="overseer", from_role="builder")
    hint = result["unread"][0]["_hint"]
    assert hint["expects_reply_kind"] == "design-delivered"
    assert "architect" in hint["action_hint"].lower()


def test_check_unknown_kind_gets_generic_hint_not_error(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer",
         kind="some-brand-new-kind-nobody-taxonomized", msg="whatever")
    result = check(tmp_path, role="overseer", from_role="builder")
    assert len(result["unread"]) == 1
    hint = result["unread"][0]["_hint"]
    assert hint["expects_reply_kind"] is None
    assert "no defined action" in hint["action_hint"].lower()


def test_check_action_needed_includes_design_task_and_question(tmp_path):
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="design-task", msg="a")
    send(tmp_path, from_role="builder", to_role="overseer", kind="question", msg="b")
    send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg="c")

    result = check(tmp_path, role="overseer", from_role="builder")
    kinds_needing_action = {e["kind"] for e in result["action_needed"]}
    assert kinds_needing_action == {"design-task", "question"}


def test_check_action_needed_respects_explicit_needs_reply_flag(tmp_path):
    """qc-verdict is informational by default (terminal, no expected reply),
    but an explicit needs_reply=True on the envelope still surfaces it."""
    from mailbox import send, check

    send(tmp_path, from_role="builder", to_role="overseer", kind="qc-verdict", msg="fyi",
         needs_reply=False)
    send(tmp_path, from_role="builder", to_role="overseer", kind="qc-verdict", msg="please respond",
         needs_reply=True)

    result = check(tmp_path, role="overseer", from_role="builder")
    action_msgs = {e["msg"] for e in result["action_needed"]}
    assert action_msgs == {"please respond"}


def test_check_terminal_kinds_not_in_action_needed_by_default(tmp_path):
    from mailbox import send, check

    for kind in ("design-delivered", "build-delivered", "reconnect"):
        send(tmp_path, from_role="builder", to_role="overseer", kind=kind, msg=kind)

    result = check(tmp_path, role="overseer", from_role="builder")
    assert result["action_needed"] == []


# ── defensive parsing of messy/real data ────────────────────────────────────


def test_check_handles_torn_last_line_without_consuming_it(tmp_path):
    """A line with no trailing newline is an in-flight/torn write -- must not
    be surfaced yet and must not advance the cursor past it. It should appear
    on a later check() once the newline lands."""
    from mailbox import check, _outbound_path

    path = _outbound_path(tmp_path, "builder", "overseer")
    path.parent.mkdir(parents=True, exist_ok=True)
    complete = json.dumps({"from": "builder", "to": "overseer", "kind": "reconnect",
                            "msg": "complete", "ts": "2026-07-14T12:00:00+00:00", "id": "1"})
    torn = json.dumps({"from": "builder", "to": "overseer", "kind": "reconnect",
                        "msg": "torn", "ts": "2026-07-14T12:00:01+00:00", "id": "2"})
    path.write_text(complete + "\n" + torn)  # NOTE: no trailing newline on the torn line

    result = check(tmp_path, role="overseer", from_role="builder")
    assert [e["msg"] for e in result["unread"]] == ["complete"]

    # "Complete" the torn write and check again -- the torn line must now surface.
    path.write_text(complete + "\n" + torn + "\n")
    result2 = check(tmp_path, role="overseer", from_role="builder")
    assert [e["msg"] for e in result2["unread"]] == ["torn"]


def test_check_handles_malformed_json_line_without_crashing(tmp_path):
    """A genuinely corrupt line (not just torn) must not crash check() and
    must not be lost forever -- it's surfaced as an unparsable envelope and
    the cursor still advances past it (a stuck cursor would block every
    message behind it forever)."""
    from mailbox import check, _outbound_path

    path = _outbound_path(tmp_path, "builder", "overseer")
    path.parent.mkdir(parents=True, exist_ok=True)
    good_before = json.dumps({"from": "builder", "to": "overseer", "kind": "reconnect",
                               "msg": "before", "ts": "2026-07-14T12:00:00+00:00", "id": "1"})
    good_after = json.dumps({"from": "builder", "to": "overseer", "kind": "reconnect",
                              "msg": "after", "ts": "2026-07-14T12:00:02+00:00", "id": "3"})
    path.write_text(good_before + "\n" + "{this is not valid json at all" + "\n" + good_after + "\n")

    result = check(tmp_path, role="overseer", from_role="builder")
    msgs = [e.get("msg") for e in result["unread"]]
    assert "before" in msgs
    assert "after" in msgs
    unparsable = [e for e in result["unread"] if e.get("_parse_error")]
    assert len(unparsable) == 1

    # Cursor must have advanced past all three lines -- not stuck on the bad one.
    result2 = check(tmp_path, role="overseer", from_role="builder")
    assert result2["unread"] == []
