#!/usr/bin/env python3
"""mailbox.py — hardened two-role coordination mailbox.

Hardens the ad-hoc pattern of two named roles passing JSONL messages back and
forth, first proven in a real live coordination lane between an overseer and
a build session, into a reusable primitive. Skill surface: SKILL.md in this
same directory.

NOTE on the module name: this shadows Python's stdlib `mailbox` module (mbox/
Maildir handling) for any importer whose sys.path puts this file's directory
first — the design doc specifies this exact filename, so it's kept as-is, but
nothing in this codebase currently does `import mailbox` expecting the stdlib
version. Flagged here so a future script placed in this same directory
doesn't get a confusing surprise (Bible commandment VIII: names are
documentation).

Core invariants (from the design doc):
- One append-only JSONL file PER (from_role, to_role) directed pair, at
  <lane_dir>/_sync/<from_role>-to-<to_role>.jsonl. A role only ever appends to
  files where it is the sender -- no two processes can ever collide on the
  same file's write, by construction. No lock needed for the append itself.
- Acknowledgment is a NEW message on the receiver's OWN outbound file, never
  an edit to someone else's line. Append-only holds everywhere, no exceptions.
- Cursor state (<lane_dir>/_sync/.cursor-<role>.json) is written with an
  atomic temp-file-then-rename, never a direct open-write (Bible §1.9: write
  to a temp file in the same directory, then os.replace() for a POSIX-atomic
  swap -- an operation either completes fully or doesn't happen at all).
- The cursor is monotonic -- it never moves backward, even under two
  overlapping check() calls racing on the same lane. The mechanism: before
  writing, re-read whatever the cursor file ACTUALLY holds right now and take
  the elementwise max against this call's own advances, per source file. This
  means a slow writer can never regress a fast writer's already-persisted
  progress.
- check() is safe under a race, but NOT free of a specific, deliberately
  tolerated race outcome: two check() calls that both start from the same
  cursor position can both see (and return) the same "new" messages once.
  That is the worst case -- a message is re-surfaced, never lost. Making
  re-processing of a re-surfaced message safe is the CALLER's job (e.g. make
  whatever the message triggers idempotent, or de-dupe on envelope `id`) --
  it is deliberately NOT this module's job, because a cross-process lock
  strong enough to prevent that would add real complexity for a race window
  that, in the two-cockpit/one-role usage this was built for, is rare and
  cheap to tolerate.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


# kind -> {expects_reply_kind, action_hint, [implicit_needs_reply]}
# Additive, not restrictive: a caller may use kinds outside this table --
# unknown kinds get a generic hint (see _GENERIC_HINT), never an error.
KIND_TAXONOMY: dict[str, dict[str, Any]] = {
    "design-task": {
        "expects_reply_kind": "design-delivered",
        "action_hint": "Architect the thing described, drop a spec, reply when ready.",
    },
    "design-delivered": {
        "expects_reply_kind": None,
        "action_hint": "A spec is ready -- go read the referenced file.",
    },
    "build-task": {
        "expects_reply_kind": "build-delivered",
        "action_hint": "Implement per the referenced spec.",
    },
    "build-delivered": {
        "expects_reply_kind": None,
        "action_hint": "Implementation done, evidence attached.",
    },
    "qc-verdict": {
        "expects_reply_kind": None,
        "action_hint": "Informational -- act only if needs_reply is true.",
    },
    "question": {
        "expects_reply_kind": "any",
        "action_hint": "Blocks -- needs an answer, any kind.",
        "implicit_needs_reply": True,
    },
    "reconnect": {
        "expects_reply_kind": None,
        "action_hint": "Presence ping -- no action needed.",
    },
}

_GENERIC_HINT: dict[str, Any] = {
    "expects_reply_kind": None,
    "action_hint": "No defined action for this kind -- read the message and use judgment.",
}


# ── path helpers ──────────────────────────────────────────────────────────


def _sync_dir(lane_dir: Path) -> Path:
    d = Path(lane_dir) / "_sync"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _outbound_path(lane_dir: Path, from_role: str, to_role: str) -> Path:
    return _sync_dir(lane_dir) / f"{from_role}-to-{to_role}.jsonl"


def _cursor_path(lane_dir: Path, role: str) -> Path:
    return _sync_dir(lane_dir) / f".cursor-{role}.json"


# ── send() ────────────────────────────────────────────────────────────────


def send(
    lane_dir: Path,
    *,
    from_role: str,
    to_role: str,
    kind: str,
    msg: str,
    needs_reply: bool = False,
    ref: Optional[str] = None,
    artifacts: Optional[list] = None,
) -> dict:
    """Atomically append one envelope to <lane_dir>/_sync/<from_role>-to-<to_role>.jsonl.

    Crash-safety: the whole JSON-encoded line (envelope + trailing newline) is
    built in memory first, then handed to a SINGLE f.write() call on a file
    opened in append mode. A single write() of one line is atomic enough on
    POSIX for reasonable line sizes (the syscall either lands whole or not at
    all) -- no temp+rename needed for an append-only log; temp+rename is
    reserved for files that get REPLACED wholesale (the cursor -- see
    _write_cursor_atomic below). Multiple write() calls for one envelope would
    risk a torn line if the process died between them, or interleaving with a
    concurrent appender's write -- this function never does that.

    Returns the written envelope, including a generated `id`.
    """
    path = _outbound_path(lane_dir, from_role, to_role)
    now = datetime.now(timezone.utc)
    envelope: dict[str, Any] = {
        "id": f"{int(now.timestamp() * 1000)}-{uuid.uuid4().hex[:8]}",
        "ts": now.isoformat(timespec="microseconds"),
        "from": from_role,
        "to": to_role,
        "kind": kind,
        "msg": msg,
        "needs_reply": needs_reply,
    }
    if ref is not None:
        envelope["ref"] = ref
    if artifacts is not None:
        envelope["artifacts"] = artifacts

    line = json.dumps(envelope, ensure_ascii=False) + "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)  # ONE write() call, whole line -- atomic on POSIX

    return envelope


# ── cursor: atomic read/write ────────────────────────────────────────────


def _load_cursor(cursor_path: Path) -> dict:
    """Best-effort read. A missing cursor file is normal (first-ever check()
    for this role) and stays silent. A cursor file that EXISTS but is corrupt
    or malformed is not swallowed silently -- it's a real anomaly (Bible
    commandment II: never swallow errors silently), so it's logged to stderr
    before falling back to "nothing read yet" for the unrecoverable keys."""
    try:
        with open(cursor_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        print(f"mailbox: cursor file {cursor_path} is corrupt ({exc}) -- "
              f"treating as unread-from-start", file=sys.stderr)
        return {}
    if isinstance(data, dict):
        return data
    print(f"mailbox: cursor file {cursor_path} held non-dict JSON -- "
          f"treating as unread-from-start", file=sys.stderr)
    return {}


def _write_cursor_atomic(cursor_path: Path, data: dict) -> None:
    """Bible §1.9: temp file in the same directory + os.replace() for a
    POSIX-atomic swap. Never a direct open-write -- a crash mid-write would
    leave a truncated/corrupt cursor file, which could either replay every
    message forever (if it reads as empty) or silently skip unread messages
    (if it reads as further along than it really is)."""
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(cursor_path.parent), prefix=f".{cursor_path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_name, cursor_path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def _advance_cursor(cursor_path: Path, advances: dict) -> None:
    """Merge this call's newly-computed per-file read positions into whatever
    the cursor file ACTUALLY holds right now, taking the max per key.
    Monotonic under a race: if a concurrent check() already advanced a file
    further than this call did, this write can never regress it -- the merge
    always keeps the larger of the two."""
    current = _load_cursor(cursor_path)
    merged = dict(current)
    for key, val in advances.items():
        merged[key] = max(merged.get(key, 0), val)
    _write_cursor_atomic(cursor_path, merged)


# ── reading + parsing the JSONL logs ─────────────────────────────────────


def _read_new_envelopes(path: Path, start: int) -> tuple[list[dict], int]:
    """Read lines [start:] from `path`. Returns (parsed envelopes, new cursor
    position for this file).

    Defensive against real-world messiness:
    - A malformed (non-JSON) line is never dropped silently -- it's surfaced
      as a synthetic `_parse_error` envelope so nothing vanishes, and the
      cursor still advances past it (a stuck cursor on one bad line would
      block every message behind it forever).
    - A torn/incomplete last line (no trailing newline -- a writer mid-flight)
      is NOT consumed and NOT surfaced. It's left for the next call once the
      writer's newline lands, so a reader can never observe a half-written
      envelope.
    """
    if not path.exists():
        return [], start

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = lines[start:]
    envelopes: list[dict] = []
    consumed = start

    for i, raw in enumerate(new_lines):
        is_last = i == len(new_lines) - 1
        if is_last and not raw.endswith("\n"):
            break  # torn write in flight -- stop here, don't consume it

        stripped = raw.strip()
        if not stripped:
            consumed += 1
            continue

        try:
            envelope = json.loads(stripped)
        except json.JSONDecodeError:
            envelope = {
                "from": None,
                "to": None,
                "kind": "_unparsable",
                "msg": stripped,
                "ts": None,
                "id": None,
                "_parse_error": True,
            }
        envelope["_source_file"] = path.name
        envelopes.append(envelope)
        consumed += 1

    return envelopes, consumed


def _parse_ts(ts: Optional[str]):
    if not ts:
        return None
    try:
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        # Real production data is inconsistent about this -- the ad-hoc
        # opus-to-fable.jsonl/fable-to-opus.jsonl lane has both naive
        # ("2026-07-09T19:39:49") and offset-aware ("...Z", "...-07:00")
        # timestamps in the SAME file. Comparing naive vs. aware datetimes
        # raises TypeError, which would crash the merge sort on real data.
        # Assume UTC for naive timestamps -- matches this module's own
        # convention going forward -- so every parsed value is comparable.
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _needs_action(envelope: dict, taxonomy_entry: dict) -> bool:
    if envelope.get("needs_reply"):
        return True
    if taxonomy_entry.get("implicit_needs_reply"):
        return True
    if taxonomy_entry.get("expects_reply_kind"):
        return True
    return False


# ── check() ──────────────────────────────────────────────────────────────


def check(lane_dir: Path, *, role: str, from_role: Optional[str] = None) -> dict:
    """Read every unread line from <lane_dir>/_sync/<from_role>-to-<role>.jsonl
    (or every *-to-<role>.jsonl if from_role is None, merged chronologically
    across senders), using `role`'s own cursor state. Advances that cursor
    atomically before returning.

    Race-safety property (see module docstring for the full explanation): two
    overlapping check() calls on the same lane never corrupt the cursor file
    and never permanently lose a message. Worst case, both calls return the
    same message once each -- re-processing that safely is the caller's job.

    Returns {"unread": [...], "by_kind": {...}, "action_needed": [...]},
    grouped and annotated using KIND_TAXONOMY -- not a raw text dump.
    Every envelope in "unread" gets an `_hint` key: {"action_hint": str,
    "expects_reply_kind": str | None}.
    """
    lane_dir = Path(lane_dir)
    sync_dir = _sync_dir(lane_dir)
    cursor_path = _cursor_path(lane_dir, role)

    if from_role is not None:
        candidate_paths = [_outbound_path(lane_dir, from_role, role)]
    else:
        pattern = str(sync_dir / f"*-to-{role}.jsonl")
        candidate_paths = sorted(Path(p) for p in glob.glob(pattern))

    cursor = _load_cursor(cursor_path)
    advances: dict[str, int] = {}
    collected: list[dict] = []

    for path in candidate_paths:
        start = cursor.get(path.name, 0)
        envelopes, new_position = _read_new_envelopes(path, start)
        collected.extend(envelopes)
        advances[path.name] = new_position

    # Chronological merge across senders. Stable sort: envelopes with an
    # unparseable/missing ts keep their original (file-iteration) relative
    # order rather than being compared against real timestamps.
    indexed = list(enumerate(collected))

    def _sort_key(item):
        idx, envelope = item
        ts = _parse_ts(envelope.get("ts"))
        if ts is not None:
            return (0, ts, idx)
        return (1, idx, idx)

    indexed.sort(key=_sort_key)
    ordered = [envelope for _, envelope in indexed]

    by_kind: dict[str, list[dict]] = {}
    action_needed: list[dict] = []

    for envelope in ordered:
        kind = envelope.get("kind") or "_unparsable"
        entry = KIND_TAXONOMY.get(kind, _GENERIC_HINT)
        envelope["_hint"] = {
            "action_hint": entry["action_hint"],
            "expects_reply_kind": entry.get("expects_reply_kind"),
        }
        by_kind.setdefault(kind, []).append(envelope)
        if _needs_action(envelope, entry):
            action_needed.append(envelope)

    if advances:
        _advance_cursor(cursor_path, advances)

    return {"unread": ordered, "by_kind": by_kind, "action_needed": action_needed}
