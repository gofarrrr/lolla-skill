#!/usr/bin/env bash
set -euo pipefail

RECEIPT_FILE=""
SKIP_OBSERVATORY=0
REQUESTED_RUN_ID=""
TRUSTED_TRANSCRIPT=""
REQUIRE_LIVE_OUTPUT_CLEAN=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --receipt-file)
      RECEIPT_FILE="${2:-}"
      shift 2
      ;;
    --skip-observatory)
      SKIP_OBSERVATORY=1
      shift
      ;;
    --trusted-transcript)
      TRUSTED_TRANSCRIPT="${2:-}"
      shift 2
      ;;
    --require-live-output-clean)
      REQUIRE_LIVE_OUTPUT_CLEAN=1
      shift
      ;;
    *)
      echo "FATAL: unknown argument to finalize_and_archive.sh: $1" >&2
      exit 2
      ;;
  esac
done

append_receipt_to_transcript() {
  local receipt_file="$1"
  local transcript_path="$2"
  if [ ! -s "$receipt_file" ]; then
    echo "FATAL: receipt file missing or empty at $receipt_file" >&2
    exit 1
  fi
  touch "$transcript_path"
  python3 - "$receipt_file" "$transcript_path" <<'PY'
import sys
from pathlib import Path

receipt_path = Path(sys.argv[1])
transcript_path = Path(sys.argv[2])
receipt = receipt_path.read_text(encoding="utf-8").strip()
transcript = transcript_path.read_text(encoding="utf-8") if transcript_path.exists() else ""
if receipt and receipt not in transcript:
    with transcript_path.open("a", encoding="utf-8") as handle:
        if transcript and not transcript.endswith("\n\n"):
            handle.write("\n\n")
        handle.write(receipt + "\n")
PY
}

observatory_http_ok() {
  local url="$1"
  if [ -z "$url" ]; then
    return 1
  fi
  python3 - "$url" <<'PY'
import sys
from urllib.request import Request, urlopen

url = sys.argv[1]
try:
    request = Request(url, headers={"User-Agent": "lolla-finalizer/1"})
    with urlopen(request, timeout=1.5) as response:
        raise SystemExit(0 if response.status < 500 else 1)
except Exception:
    raise SystemExit(1)
PY
}

sync_trusted_transcript_to_default() {
  if [ -z "${TRUSTED_TRANSCRIPT:-}" ] || [ "$TRANSCRIPT_PATH" = "$DEFAULT_TRANSCRIPT_PATH" ]; then
    return 0
  fi
  cp "$TRANSCRIPT_PATH" "$DEFAULT_TRANSCRIPT_PATH"
}

finalize_live_output_hygiene_current() {
  local args=(
    python3 "$SKILL_DIR/scripts/finalize_live_output_hygiene.py"
    --run-id "${LOLLA_RUN_ID}"
    --quiet
  )
  if [ -n "${TRUSTED_TRANSCRIPT:-}" ]; then
    args+=(--transcript "$TRANSCRIPT_PATH" --trusted-transcript)
  fi
  if [ "$REQUIRE_LIVE_OUTPUT_CLEAN" -eq 1 ]; then
    args+=(--require-live-output-clean)
  fi
  "${args[@]}"
}

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
  echo "FATAL: SKILL_DIR is not set. Re-run /lolla setup before finalization." >&2
  exit 1
fi
if [ -z "${LOLLA_RUN_ID:-}" ]; then
  echo "FATAL: LOLLA_RUN_ID is not set. Re-run /lolla setup before finalization." >&2
  exit 1
fi

# shellcheck source=/dev/null
. "$SKILL_DIR/scripts/skill/operator_log.sh"
lolla_operator_log_init

record_run_event_quiet() {
  local event_type="$1"
  shift
  python3 "$SKILL_DIR/scripts/record_run_event.py" \
    --run-id "$LOLLA_RUN_ID" \
    --event-type "$event_type" \
    "$@" \
    --quiet || true
}

RESULT_PATH="/tmp/lolla_${LOLLA_RUN_ID}_result.json"
DEFAULT_TRANSCRIPT_PATH="${LOLLA_LIVE_TRANSCRIPT:-/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt}"
TRANSCRIPT_PATH="$DEFAULT_TRANSCRIPT_PATH"
if [ -n "$TRUSTED_TRANSCRIPT" ]; then
  if [ ! -s "$TRUSTED_TRANSCRIPT" ]; then
    echo "FATAL: trusted transcript missing or empty at $TRUSTED_TRANSCRIPT" >&2
    exit 1
  fi
  TRANSCRIPT_PATH="$TRUSTED_TRANSCRIPT"
fi
if [ ! -s "$RESULT_PATH" ]; then
  echo "FATAL: result JSON missing at $RESULT_PATH. Cannot finalize." >&2
  exit 1
fi

if [ -n "$RECEIPT_FILE" ]; then
  append_receipt_to_transcript "$RECEIPT_FILE" "$TRANSCRIPT_PATH"
  sync_trusted_transcript_to_default
fi

python3 "$SKILL_DIR/scripts/finalize_pre_step6_private_table_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
python3 "$SKILL_DIR/scripts/finalize_v60_telemetry.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
sync_trusted_transcript_to_default
finalize_live_output_hygiene_current

OBSERVATORY_URL=""
OBSERVATORY_STATUS="skipped"
if [ "$SKIP_OBSERVATORY" -eq 0 ]; then
  OBS_LOG="/tmp/lolla_${LOLLA_RUN_ID}_observatory.log"
  OBS_PID_FILE="/tmp/lolla_${LOLLA_RUN_ID}_observatory.pid"
  OBSERVATORY_STATUS="unavailable"
  record_run_event_quiet observatory_launch_attempted --detail "log=$OBS_LOG"
  : > "$OBS_LOG"
  LAUNCH_OUTPUT="$(python3 "$SKILL_DIR/scripts/skill/launch_observatory.py" \
    --result "$RESULT_PATH" \
    --log "$OBS_LOG" \
    --pid-file "$OBS_PID_FILE")"
  lolla_operator_block "launch_observatory.py" "$LAUNCH_OUTPUT"
  OBSERVATORY_STATUS="$(printf '%s\n' "$LAUNCH_OUTPUT" | awk -F= '/^OBSERVATORY_STATUS=/ {print $2; exit}')"
  OBSERVATORY_URL="$(printf '%s\n' "$LAUNCH_OUTPUT" | awk -F= '/^OBSERVATORY_URL=/ {print $2; exit}')"
  OBSERVATORY_PID="$(printf '%s\n' "$LAUNCH_OUTPUT" | awk -F= '/^OBSERVATORY_PID=/ {print $2; exit}')"
  if [ "$OBSERVATORY_STATUS" = "live" ]; then
    lolla_operator_note "OBSERVATORY_URL: $OBSERVATORY_URL"
    lolla_operator_note "OBSERVATORY_PID: $OBSERVATORY_PID"
  else
    lolla_operator_note "OBSERVATORY_URL: unavailable (see $OBS_LOG)"
  fi
  lolla_operator_note "OBSERVATORY_STATUS: $OBSERVATORY_STATUS"
  record_run_event_quiet "observatory_$OBSERVATORY_STATUS" \
    --detail "url=${OBSERVATORY_URL:-}" \
    --detail "pid=${OBSERVATORY_PID:-}" \
    --detail "log=$OBS_LOG"
else
  record_run_event_quiet observatory_launch_skipped
fi
export LOLLA_OBSERVATORY_URL="$OBSERVATORY_URL"
export LOLLA_OBSERVATORY_STATUS="$OBSERVATORY_STATUS"

ARCHIVE_OUTPUT="$(python3 "$SKILL_DIR/scripts/archive_run.py" --run-id "${LOLLA_RUN_ID}")"
lolla_operator_block "archive_run initial" "$ARCHIVE_OUTPUT"
ARCHIVE_PATH="$(printf '%s\n' "$ARCHIVE_OUTPUT" | awk -F'path:[[:space:]]*' '/path:/ {print $2; exit}')"
if [ -n "$ARCHIVE_PATH" ]; then
  lolla_operator_note "ARCHIVE_PATH: $ARCHIVE_PATH"
  record_run_event_quiet archive_completed --detail "archive_path=$ARCHIVE_PATH"
fi

COST_HEALTH_OUTPUT="$(python3 - "$RESULT_PATH" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
usage = payload.get("usage_summary") or {}
cost = usage.get("estimated_total_cost_usd")
state = usage.get("cost_estimate_state", "unknown")
if cost is not None:
    print(f"COST_ESTIMATE: ${float(cost):.4f} ({state})")
else:
    print(f"COST_ESTIMATE: unavailable ({state})")
print(f"RUN_HEALTH: {(payload.get('run_health') or {}).get('overall', 'unknown')}")
PY
)"
lolla_operator_block "final cost and health" "$COST_HEALTH_OUTPUT"

USER_RECEIPT=""
if [ -z "$RECEIPT_FILE" ] && [ -n "$ARCHIVE_PATH" ]; then
  AUTO_RECEIPT_FILE="/tmp/lolla_${LOLLA_RUN_ID}_final_receipt.txt"
  python3 "$SKILL_DIR/scripts/skill/render_final_receipt.py" \
    --result "$RESULT_PATH" \
    --observatory-url "${OBSERVATORY_URL:-}" \
    --observatory-status "$OBSERVATORY_STATUS" \
    --archive-path "$ARCHIVE_PATH" \
    --output "$AUTO_RECEIPT_FILE"
  append_receipt_to_transcript "$AUTO_RECEIPT_FILE" "$TRANSCRIPT_PATH"
  sync_trusted_transcript_to_default
  record_run_event_quiet final_receipt_written \
    --detail "receipt_file=$AUTO_RECEIPT_FILE" \
    --detail "observatory_status=$OBSERVATORY_STATUS"
  finalize_live_output_hygiene_current
  ARCHIVE_OUTPUT="$(python3 "$SKILL_DIR/scripts/archive_run.py" --run-id "${LOLLA_RUN_ID}")"
  lolla_operator_block "archive_run final" "$ARCHIVE_OUTPUT"
  ARCHIVE_PATH="$(printf '%s\n' "$ARCHIVE_OUTPUT" | awk -F'path:[[:space:]]*' '/path:/ {print $2; exit}')"
  if [ -n "$ARCHIVE_PATH" ]; then
    lolla_operator_note "ARCHIVE_PATH: $ARCHIVE_PATH"
  fi
  USER_RECEIPT="$(cat "$AUTO_RECEIPT_FILE")"
fi

if [ -n "${ARCHIVE_PATH:-}" ] && [ -s "${LOLLA_OPERATOR_LOG:-}" ]; then
  python3 "$SKILL_DIR/scripts/archive_run.py" --run-id "${LOLLA_RUN_ID}" --quiet || true
fi

echo "OPERATOR_LOG: $LOLLA_OPERATOR_LOG"
if [ -n "$USER_RECEIPT" ]; then
  echo "USER_RECEIPT_BEGIN"
  printf '%s\n' "$USER_RECEIPT"
  echo "USER_RECEIPT_END"
fi
