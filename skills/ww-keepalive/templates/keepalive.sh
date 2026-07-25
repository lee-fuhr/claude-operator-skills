#!/bin/bash
# keepalive.sh — generalized self-relaying overnight worker.
# Source of truth: ~/.claude/skills/keepalive/  (do NOT diverge per-campaign; fix the template).
#
# Each fire launches a FRESH stateless `claude -p "$(cat resume.md)"` — NEVER `--resume <SID>`.
# A live interactive session's id is NOT resumable that way (it silently no-ops → zero work all
# night, the 2026-06-22 lesson). The brain (resume.md) carries all context + tells the worker to
# reconcile against done.md / queue.md / state.json and never redo finished work. Statelessness
# is the feature: it survives caps, session death, and reboots because there is no session to lose.
#
# PARAMETERIZE before install (4 placeholders):
#   __PGREP_TAG__   a unique banner string the brain prints early each chunk (liveness probe).
#   __WORKDIR__     the dir to cd into before launching (the build target / repo). Use "$LANE" if
#                   the work is lane-local only; otherwise the repo path.
# LANE (state dir) is passed as $1 by the plist — never hardcode it (so copies can't point back
# at the original lane).

LANE="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
STATE="$LANE/state.json"
LOG="$LANE/keepalive.log"
PY="${KEEPALIVE_PYTHON:-python3}"       # point at your venv's python3 if you use one
CLAUDE="${KEEPALIVE_CLAUDE_BIN:-$(command -v claude)}"  # a native-install migration once silently broke every
                                        # keepalive pointed at a stale Homebrew symlink — hardcode the real
                                        # resolved path here if `command -v` isn't reliable in your launchd env
CAP_RE="usage limit|rate limit|5.hour|5 hour|too many requests|overloaded|reached your|quota|try again later|limit reached|session limit|hit your|resets|limit ·|temporarily limiting"
PGREP_TAG="__PGREP_TAG__"
WORKDIR="__WORKDIR__"

# --- GATES (exit cleanly on any; re-checked inside the loop too) ---
[ -f "$LANE/STOP" ] && { echo "$(date) STOP present, exit" >> "$LOG"; exit 0; }

PAST=$($PY -c "import json,time;s=json.load(open('$STATE'));print('yes' if time.time()>s.get('deadline',0) else 'no')" 2>/dev/null)
[ "$PAST" = "yes" ] && { echo "$(date) past deadline, exit" >> "$LOG"; exit 0; }

DONE=$($PY -c "import json;s=json.load(open('$STATE'));print('yes' if s.get('complete') else 'no')" 2>/dev/null)
[ "$DONE" = "yes" ] && { echo "$(date) complete, exit" >> "$LOG"; exit 0; }

HB=$($PY -c "import json,time;s=json.load(open('$STATE'));print(int(time.time()-s.get('heartbeat',0)))" 2>/dev/null)

# --- LIVENESS via pgrep-banner (real, not heartbeat) ---
# A running headless chunk prints the unique PGREP_TAG early. Present => a chunk is alive, skip.
# Absent => relaunch regardless of heartbeat age. This is more reliable than trusting state.heartbeat.
if pgrep -f "$PGREP_TAG" >/dev/null 2>&1; then
  echo "$(date) worker chunk running (heartbeat ${HB}s), skip" >> "$LOG"; exit 0
fi

# --- INTERACTIVE INTERLOCK ---
# A live cockpit session writes interactive.pid + keeps a fresh heartbeat. Stand down while it is
# alive AND productive; resurrect headless when it caps/closes (heartbeat goes stale). Two workers
# on one tree = collision (last-write-wins where there is no git).
IPID_FILE="$LANE/interactive.pid"
if [ -f "$IPID_FILE" ]; then
  IPID=$(cat "$IPID_FILE" 2>/dev/null)
  IAGE=$(( $(date +%s) - $(stat -f %m "$IPID_FILE" 2>/dev/null || echo 0) ))
  if [ -n "$IPID" ] && kill -0 "$IPID" 2>/dev/null && [ "$HB" -lt 1800 ] && [ "$IAGE" -lt 7200 ]; then
    echo "$(date) interactive cockpit $IPID alive + heartbeat ${HB}s fresh, standing down" >> "$LOG"; exit 0
  fi
fi

# --- SINGLE-FLIGHT LOCK ---
LOCK="$LANE/.launch.lock"
if [ -f "$LOCK" ]; then
  AGE=$(( $(date +%s) - $(stat -f %m "$LOCK") ))
  [ "$AGE" -lt 1800 ] && { echo "$(date) launch in progress (${AGE}s), skip" >> "$LOG"; exit 0; }
fi
touch "$LOCK"
trap 'rm -f "$LOCK"' EXIT
echo "$(date) no chunk running, resurrecting (heartbeat ${HB}s)" >> "$LOG"

cd "$WORKDIR"   # the build target (loads its own .claude/CLAUDE.md + AGENTS.md if a repo)
RESUME="$(cat $LANE/resume.md)"
# --- DYNAMIC ACCOUNT ROUTING (account_router.py, 2026-07-25 sweep) ---
# Never hardcode primary/backup — resolve which account Lee is NOT using right now.
ROUTER_PY="/Users/lee/.local/venvs/lfi/bin/python3"
[ -x "$ROUTER_PY" ] || ROUTER_PY="python3"
ROUTER="/Users/lee/CC/Work/LFI/_ Operations/account_router.py"
ACCT=$("$ROUTER_PY" "$ROUTER" --prefer other 2>>"$LOG" | tail -1)
[ -n "$ACCT" ] || ACCT="backup"
LIVE_ACCT=$("$ROUTER_PY" "$ROUTER" --prefer same 2>>"$LOG" | tail -1)
if [ "$ACCT" = "$LIVE_ACCT" ]; then
  echo "$(date) resolved '$ACCT' is also the live interactive account -- standing down" >> "$LOG"; exit 0
fi
TOK=$(cat "$HOME/.claude-accounts/$ACCT" 2>/dev/null || echo "")
if [ -z "$TOK" ]; then
  echo "$(date) FATAL: no token at ~/.claude-accounts/$ACCT -- refusing to fall through to live account, exiting" >> "$LOG"; exit 0
fi
echo "$(date) using account '$ACCT' (live is '$LIVE_ACCT')" >> "$LOG"

while true; do
  [ -f "$LANE/STOP" ] && { echo "$(date) STOP mid-loop, stopping" >> "$LOG"; break; }
  PASTL=$($PY -c "import json,time;s=json.load(open('$STATE'));print('yes' if time.time()>s.get('deadline',0) else 'no')" 2>/dev/null)
  [ "$PASTL" = "yes" ] && { echo "$(date) deadline mid-loop, stopping" >> "$LOG"; break; }
  DONEL=$($PY -c "import json;s=json.load(open('$STATE'));print('yes' if s.get('complete') else 'no')" 2>/dev/null)
  [ "$DONEL" = "yes" ] && { echo "$(date) complete mid-loop, stopping" >> "$LOG"; break; }

  START=$(date +%s); RAN_OK=0
  echo "$(date) chunk on account '$ACCT' (dynamic-router pick)" >> "$LOG"
  OUT=$(env -u ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN="$TOK" $CLAUDE -p "$RESUME" --permission-mode auto 2>&1)
  RC=$?; echo "$OUT" | tail -40 >> "$LOG"
  if [ $RC -eq 0 ] && ! echo "$OUT" | grep -qiE "$CAP_RE"; then RAN_OK=1; echo "$(date) chunk done" >> "$LOG"; else echo "$(date) chunk capped/failed (rc=$RC) — pausing, interval retries" >> "$LOG"; fi
  [ $RAN_OK -eq 0 ] && break
  ELAPSED=$(( $(date +%s) - START ))
  # spin guard: a chunk that returns instantly is failing fast — pause, don't hammer.
  [ $ELAPSED -lt 45 ] && { echo "$(date) chunk returned in ${ELAPSED}s (<45s) — spin guard, pausing" >> "$LOG"; break; }
  echo "$(date) chunk ok in ${ELAPSED}s — looping immediately" >> "$LOG"
done
rm -f "$LOCK"
echo "$(date) keepalive cycle done" >> "$LOG"
