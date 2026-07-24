#!/usr/bin/env bash
set -euo pipefail

REQUESTED_RUN_ID=""
REQUESTED_CONVERSATION=""
REQUESTED_OUTPUT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --help|-h)
      cat <<'EOF'
Usage: bash scripts/skill/run_extract_step.sh

Runs Step 2 using the current Lolla environment. Extra run IDs or file paths
are not needed; if provided, they must match the current run.
EOF
      exit 0
      ;;
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --conversation-file)
      REQUESTED_CONVERSATION="${2:-}"
      shift 2
      ;;
    --output-file)
      REQUESTED_OUTPUT="${2:-}"
      shift 2
      ;;
    *)
      case "$1" in
        /tmp/lolla_*_conversation.txt)
          if [ -n "$REQUESTED_CONVERSATION" ]; then
            echo "FATAL: run_extract_step.sh received multiple conversation paths." >&2
            exit 2
          fi
          REQUESTED_CONVERSATION="$1"
          shift
          ;;
        /tmp/lolla_*_extraction.json)
          if [ -n "$REQUESTED_OUTPUT" ]; then
            echo "FATAL: run_extract_step.sh received multiple extraction paths." >&2
            exit 2
          fi
          REQUESTED_OUTPUT="$1"
          shift
          ;;
        *)
          echo "FATAL: unknown argument to run_extract_step.sh: $1" >&2
          exit 2
          ;;
      esac
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

if [ -z "${SKILL_DIR:-}" ] || [ ! -f "$SKILL_DIR/scripts/run_extract.py" ]; then
  echo "FATAL: SKILL_DIR is not set or run_extract.py is missing. Re-run /lolla setup before Step 2." >&2
  exit 1
fi
if [ -z "${LOLLA_RUN_ID:-}" ]; then
  echo "FATAL: LOLLA_RUN_ID is not set. Re-run /lolla setup before Step 2." >&2
  exit 1
fi

if ! LOLLA_AUDIT_MODE="$(PYTHONPATH="$SKILL_DIR" python3 "$SKILL_DIR/scripts/skill/validate_audit_mode.py")"; then
  exit 1
fi
export LOLLA_AUDIT_MODE

# shellcheck source=/dev/null
. "$SKILL_DIR/scripts/skill/operator_log.sh"
lolla_operator_log_init

RUNTIME_TMP_DIR="${LOLLA_TMP_DIR:-/tmp}"
CONVERSATION_PATH="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_conversation.txt"
EXTRACTION_PATH="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_extraction.json"
EXTRACTION_TERMINAL_PATH="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_extraction_terminal.json"

if [ -n "$REQUESTED_CONVERSATION" ] && [ "$REQUESTED_CONVERSATION" != "$CONVERSATION_PATH" ]; then
  echo "FATAL: run_extract_step.sh received unexpected --conversation-file. Use the current run path: $CONVERSATION_PATH" >&2
  exit 2
fi
if [ -n "$REQUESTED_OUTPUT" ] && [ "$REQUESTED_OUTPUT" != "$EXTRACTION_PATH" ]; then
  echo "FATAL: run_extract_step.sh received unexpected --output-file. Use the current run path: $EXTRACTION_PATH" >&2
  exit 2
fi

if [ -f "$EXTRACTION_TERMINAL_PATH" ]; then
  echo "FATAL: this extraction run is already terminal; start a new \$lolla run instead of retrying the same run." >&2
  exit 1
fi

if [ ! -s "$CONVERSATION_PATH" ]; then
  echo "FATAL: conversation file missing or empty at $CONVERSATION_PATH. Step 1 capture failed." >&2
  exit 1
fi

CONVERSATION_BYTES="$(wc -c < "$CONVERSATION_PATH")"
lolla_operator_note "Step 2 pre-extraction guard: conversation file present (${CONVERSATION_BYTES} bytes)."
if ! lolla_run_logged "Step 2 validate_conversation_capture.py" \
  python3 "$SKILL_DIR/scripts/skill/validate_conversation_capture.py" \
    --conversation-file "$CONVERSATION_PATH"; then
  echo "FATAL: conversation capture is not parseable for Lolla. See operator log: $LOLLA_OPERATOR_LOG" >&2
  exit 2
fi

set +e
lolla_run_logged "Step 2 run_extract.py" \
  python3 "$SKILL_DIR/scripts/run_extract.py" \
    --conversation-file "$CONVERSATION_PATH" \
    --output-file "$EXTRACTION_PATH"
EXTRACTION_COMMAND_EXIT="$?"
set -e

set +e
FINALIZE_OUTPUT="$(
  python3 "$SKILL_DIR/scripts/skill/finalize_extraction_attempt.py" \
    --command-exit "$EXTRACTION_COMMAND_EXIT"
)"
FINALIZE_EXIT="$?"
set -e
lolla_operator_block "Step 2 finalize_extraction_attempt.py" "$FINALIZE_OUTPUT"
if [ "$FINALIZE_EXIT" -ne 0 ]; then
  echo "FATAL: extraction closeout failed. See operator log: $LOLLA_OPERATOR_LOG" >&2
  exit 1
fi
printf '%s\n' "$FINALIZE_OUTPUT"

set +e
python3 - <<'PY'
import json
import os
from pathlib import Path

run_id = os.environ.get("LOLLA_RUN_ID", "")
tmp_dir = Path(os.environ.get("LOLLA_TMP_DIR", "/tmp")).expanduser()
path = tmp_dir / f"lolla_{run_id}_extraction.json"
if not run_id or not path.exists():
    raise SystemExit("FATAL: extraction JSON was not written.")

payload = json.loads(path.read_text(encoding="utf-8"))
status = payload.get("status", "missing")
manifest = payload.get("capture_manifest") or {}
if manifest:
    print(
        "CAPTURE_MANIFEST: "
        f"user_turns={manifest.get('actual_user_turns', 'unknown')} "
        f"assistant_turns={manifest.get('actual_assistant_turns', 'unknown')} "
        f"chars={manifest.get('char_length', 'unknown')}"
    )
if status == "not_strategic":
    reason = (
        payload.get("decline_reason")
        or (payload.get("extraction") or {}).get("decline_reason")
        or "The conversation was not classified as a strategic decision."
    )
    print(f"DECLINE_REASON: {reason}")
    raise SystemExit(3)
if status == "capture_critical":
    reason = (
        payload.get("decline_reason")
        or "The authoritative conversation capture was critically incomplete."
    )
    print(f"DECLINE_REASON: {reason}")
    raise SystemExit(4)
if status == "ok":
    raise SystemExit(0)
raise SystemExit(5)
PY
EXTRACTION_EXIT="$?"
set -e
# finalize_extraction_attempt.py records extraction_completed,
# extraction_declined, or extraction_failed and seals this run against retries.
echo "OPERATOR_LOG: $LOLLA_OPERATOR_LOG"
exit "$EXTRACTION_EXIT"
