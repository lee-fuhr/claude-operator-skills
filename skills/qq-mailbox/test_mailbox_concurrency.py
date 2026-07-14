#!/usr/bin/env python3
"""TDD for mailbox.py — concurrency race safety + real-production-data smoke
test. Split out of test_mailbox.py to stay under the 500-line file cap
(Bible §6.7).

The real-data test copies the live ea-pm-consolidation lane's _sync/ files
into tmp_path first — it never reads a live cursor into the real directory
and never writes to it. check() writes a cursor file as a side effect of
every call, so calling it directly against the live lane (even read-only in
intent) would leave a stray file in a directory a live Overseer session
depends on right now. Copying first gets the identical proof value (real,
messy production content) with zero risk to the live channel.
"""
import json
import shutil
import threading
from pathlib import Path

import pytest


REAL_LANE_SYNC = Path(
    "/Users/lee/CC/Work/LFI/_ Operations/_notes/ea-pm-consolidation/_sync"
)


def test_concurrent_check_race_safety(tmp_path):
    """Two check() calls racing on the same lane must never corrupt the cursor
    file and must never permanently lose a message -- worst case is a message
    getting surfaced to more than one caller once. Uses real threads so file
    I/O (which releases the GIL) genuinely interleaves."""
    from mailbox import send, check, _cursor_path

    n_messages = 40
    for i in range(n_messages):
        send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect", msg=f"m{i}")

    n_threads = 8
    results = [None] * n_threads
    errors = []
    barrier = threading.Barrier(n_threads)

    def worker(idx):
        try:
            barrier.wait(timeout=5)
            results[idx] = check(tmp_path, role="overseer", from_role="builder")
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)

    assert not errors, f"check() raised under concurrency: {errors}"

    # Cursor file must be valid, complete JSON -- never malformed by a race.
    cursor_path = _cursor_path(tmp_path, "overseer")
    cursor_data = json.loads(cursor_path.read_text())
    assert cursor_data["builder-to-overseer.jsonl"] == n_messages

    # No message permanently lost: union of every thread's "unread" must cover
    # all n_messages (each may be seen by more than one thread under a race --
    # that's the tolerated outcome, never loss).
    seen_msgs = set()
    for r in results:
        assert r is not None
        for e in r["unread"]:
            seen_msgs.add(e["msg"])
    assert seen_msgs == {f"m{i}" for i in range(n_messages)}

    # A follow-up check() must see nothing new -- cursor genuinely converged,
    # not stuck below the true end of file.
    followup = check(tmp_path, role="overseer", from_role="builder")
    assert followup["unread"] == []


def test_concurrent_send_never_interleaves_or_corrupts_lines(tmp_path):
    """Multiple threads calling send() to the same outbound file concurrently
    must never produce a line that fails to parse as JSON (no interleaved
    writes) and must never drop a message."""
    from mailbox import send

    n_threads = 10
    n_per_thread = 20
    barrier = threading.Barrier(n_threads)
    errors = []

    def worker(idx):
        try:
            barrier.wait(timeout=5)
            for i in range(n_per_thread):
                send(tmp_path, from_role="builder", to_role="overseer", kind="reconnect",
                     msg=f"t{idx}-m{i}")
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=15)

    assert not errors

    out = tmp_path / "_sync" / "builder-to-overseer.jsonl"
    lines = out.read_text().splitlines()
    assert len(lines) == n_threads * n_per_thread

    parsed_msgs = set()
    for line in lines:
        envelope = json.loads(line)  # raises if any line got interleaved/corrupted
        parsed_msgs.add(envelope["msg"])

    expected = {f"t{i}-m{j}" for i in range(n_threads) for j in range(n_per_thread)}
    assert parsed_msgs == expected


@pytest.mark.skipif(not REAL_LANE_SYNC.exists(), reason="real ea-pm-consolidation lane not present")
def test_check_against_real_production_snapshot(tmp_path):
    """Proves the parser/grouping logic against genuinely real, messy
    production data -- long free-text messages, varied kind values that don't
    match the v1 taxonomy. Operates on a COPY of the real lane (tmp_path),
    never the live directory itself."""
    from mailbox import check

    lane_copy = tmp_path / "ea-pm-consolidation"
    shutil.copytree(REAL_LANE_SYNC, lane_copy / "_sync")

    # The real files predate this module and use short aliases in the FILENAME
    # (opus-to-fable.jsonl, fable-to-opus.jsonl) even though the "from"/"to"
    # envelope fields drifted to longer role names over the session
    # (opus-build, fable-qc, opus-cockpit-qqstatus-live, fable-qc-headless...).
    # from_role=None (glob mode) finds the file by its real name regardless.
    result = check(lane_copy, role="fable")
    assert len(result["unread"]) > 0
    # Real data has kinds far outside the v1 taxonomy (e.g. handshake,
    # plan-posted) -- must not crash, must still get a generic hint.
    known = set(result["by_kind"]) & {"design-task", "reconnect"}
    unknown = set(result["by_kind"]) - known
    assert unknown, "expected real data to contain kinds outside the v1 taxonomy"
    for env in result["unread"]:
        assert "_hint" in env
        assert "action_hint" in env["_hint"]

    # The live directory itself must be completely untouched by this test.
    assert not (REAL_LANE_SYNC / ".cursor-fable.json").exists()
