#!/usr/bin/env bash
set -euo pipefail

REQUESTED_RUN_ID=""
REQUESTED_RESULT=""
REQUESTED_OUTPUT=""
REQUESTED_NOTE=""
INCLUDE_APPENDIX=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --result)
      REQUESTED_RESULT="${2:-}"
      shift 2
      ;;
    --output)
      REQUESTED_OUTPUT="${2:-}"
      shift 2
      ;;
    --memo-note-file)
      REQUESTED_NOTE="${2:-}"
      shift 2
      ;;
    --include-audit-appendix)
      INCLUDE_APPENDIX=1
      shift
      ;;
    --help|-h)
      cat <<'EOF'
Usage: bash scripts/skill/render_memo_step.sh

Persists /tmp/lolla_${LOLLA_RUN_ID}_memo_note.json into result.json and renders
/tmp/lolla_${LOLLA_RUN_ID}_memo.md.
EOF
      exit 0
      ;;
    *)
      echo "FATAL: unknown argument to render_memo_step.sh: $1" >&2
      exit 2
      ;;
  esac
done

if [ -n "${LOLLA_ENV_STATE:-}" ] && [ -f "$LOLLA_ENV_STATE" ]; then
  # shellcheck source=/dev/null
  . "$LOLLA_ENV_STATE"
elif [ -f /tmp/lolla_latest_env.sh ]; then
  # shellcheck source=/dev/null
  . /tmp/lolla_latest_env.sh
fi

if [ -n "$REQUESTED_RUN_ID" ]; then
  export LOLLA_RUN_ID="$REQUESTED_RUN_ID"
fi
if [ -n "${LOLLA_EXPECTED_RUN_ID:-}" ] && [ "${LOLLA_RUN_ID:-}" != "$LOLLA_EXPECTED_RUN_ID" ]; then
  echo "FATAL: run state mismatch: expected $LOLLA_EXPECTED_RUN_ID but active run is ${LOLLA_RUN_ID:-unset}" >&2
  exit 1
fi

if [ -z "${SKILL_DIR:-}" ] || [ ! -d "$SKILL_DIR" ]; then
  echo "FATAL: SKILL_DIR is not set. Re-run /lolla setup before Step 8c." >&2
  exit 1
fi
if [ -z "${LOLLA_RUN_ID:-}" ]; then
  echo "FATAL: LOLLA_RUN_ID is not set. Re-run /lolla setup before Step 8c." >&2
  exit 1
fi

RESULT_PATH="/tmp/lolla_${LOLLA_RUN_ID}_result.json"
NOTE_PATH="${REQUESTED_NOTE:-/tmp/lolla_${LOLLA_RUN_ID}_memo_note.json}"
MEMO_PATH="/tmp/lolla_${LOLLA_RUN_ID}_memo.md"

if [ -n "$REQUESTED_RESULT" ] && [ "$REQUESTED_RESULT" != "$RESULT_PATH" ]; then
  echo "FATAL: render_memo_step.sh received unexpected --result. Use the current run path: $RESULT_PATH" >&2
  exit 2
fi
if [ -n "$REQUESTED_OUTPUT" ] && [ "$REQUESTED_OUTPUT" != "$MEMO_PATH" ]; then
  echo "FATAL: render_memo_step.sh received unexpected --output. Use the current run path: $MEMO_PATH" >&2
  exit 2
fi

if [ ! -s "$RESULT_PATH" ]; then
  echo "FATAL: result JSON missing at $RESULT_PATH. Step 3 did not complete." >&2
  exit 1
fi
if [ ! -s "$NOTE_PATH" ]; then
  echo "FATAL: memo note JSON missing at $NOTE_PATH. Step 8c memo fields were not written." >&2
  exit 1
fi

python3 - "$RESULT_PATH" "$NOTE_PATH" <<'PY'
import datetime as dt
import json
import sys
from pathlib import Path

result_path = Path(sys.argv[1])
note_path = Path(sys.argv[2])
payload = json.loads(result_path.read_text(encoding="utf-8"))
note = json.loads(note_path.read_text(encoding="utf-8"))
for key in [
    "memo_substantive_title",
    "memo_orientation_note",
    "memo_what_changed",
    "memo_what_still_holds",
    "memo_take_back_or_set_aside",
    "memo_pressure_check",
]:
    payload[key] = str(note.get(key, "")).strip()
payload["memo_note_written_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Memo note fields persisted to {result_path}")
PY

render_args=(python3 "$SKILL_DIR/scripts/render_memo.py" --result "$RESULT_PATH" --output "$MEMO_PATH")
if [ "$INCLUDE_APPENDIX" -eq 1 ]; then
  render_args+=(--include-audit-appendix)
fi
"${render_args[@]}"
