#!/usr/bin/env bash
set -euo pipefail

RECEIPT_FILE=""
SKIP_OBSERVATORY=0
REQUESTED_RUN_ID=""

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

RESULT_PATH="/tmp/lolla_${LOLLA_RUN_ID}_result.json"
TRANSCRIPT_PATH="${LOLLA_LIVE_TRANSCRIPT:-/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt}"
if [ ! -s "$RESULT_PATH" ]; then
  echo "FATAL: result JSON missing at $RESULT_PATH. Cannot finalize." >&2
  exit 1
fi

if [ -n "$RECEIPT_FILE" ]; then
  append_receipt_to_transcript "$RECEIPT_FILE" "$TRANSCRIPT_PATH"
fi

python3 "$SKILL_DIR/scripts/finalize_pre_step6_private_table_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
python3 "$SKILL_DIR/scripts/finalize_v60_telemetry.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
python3 "$SKILL_DIR/scripts/finalize_live_output_hygiene.py" --run-id "${LOLLA_RUN_ID}" --quiet

OBSERVATORY_URL=""
if [ "$SKIP_OBSERVATORY" -eq 0 ]; then
  OBS_LOG="/tmp/lolla_${LOLLA_RUN_ID}_observatory.log"
  python3 -u "$SKILL_DIR/observatory/serve_result.py" --result "$RESULT_PATH" >"$OBS_LOG" 2>&1 &
  for _ in {1..15}; do
    OBSERVATORY_URL="$(grep -Eo 'http://localhost:[0-9]+' "$OBS_LOG" | tail -1 || true)"
    if [ -n "$OBSERVATORY_URL" ]; then
      break
    fi
    sleep 1
  done
  if [ -n "$OBSERVATORY_URL" ]; then
    echo "OBSERVATORY_URL: $OBSERVATORY_URL"
  else
    echo "OBSERVATORY_URL: pending (see $OBS_LOG)"
  fi
fi

ARCHIVE_OUTPUT="$(python3 "$SKILL_DIR/scripts/archive_run.py" --run-id "${LOLLA_RUN_ID}")"
printf '%s\n' "$ARCHIVE_OUTPUT"
ARCHIVE_PATH="$(printf '%s\n' "$ARCHIVE_OUTPUT" | awk -F'path:[[:space:]]*' '/path:/ {print $2; exit}')"
if [ -n "$ARCHIVE_PATH" ]; then
  echo "ARCHIVE_PATH: $ARCHIVE_PATH"
fi

python3 - "$RESULT_PATH" <<'PY'
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

USER_RECEIPT=""
if [ -z "$RECEIPT_FILE" ] && [ -n "$ARCHIVE_PATH" ]; then
  AUTO_RECEIPT_FILE="/tmp/lolla_${LOLLA_RUN_ID}_final_receipt.txt"
  python3 - "$RESULT_PATH" "${OBSERVATORY_URL:-}" "$ARCHIVE_PATH" "$AUTO_RECEIPT_FILE" <<'PY'
import json
import sys
from pathlib import Path

result_path = Path(sys.argv[1])
observatory_url = sys.argv[2] or "pending"
archive_path = sys.argv[3]
receipt_path = Path(sys.argv[4])

payload = json.loads(result_path.read_text(encoding="utf-8"))
usage = payload.get("usage_summary") or {}
cost = usage.get("estimated_total_cost_usd")
cost_text = f"${float(cost):.2f}" if cost is not None else "unavailable"
run_health = payload.get("run_health") or {}
overall = str(run_health.get("overall") or "unknown")
memo_path = result_path.with_name(result_path.name.replace("_result.json", "_memo.md"))

prefix = ""
issues = set(run_health.get("issues") or [])
if overall not in {"healthy", "ok"}:
    if "quote_fabrication" in issues:
        prefix = (
            "Run health is degraded: one extraction quote failed literal validation "
            "after retry; inspect the Observatory before treating this as decision-grade. "
        )
    elif "pipeline_warnings" in issues:
        prefix = (
            "Run health is partial: vendor boundary warnings were emitted; substantive "
            "artifacts are present. "
        )
    else:
        prefix = f"Run health is {overall}; inspect the Observatory for details. "

receipt = (
    f"{prefix}Observatory is live at {observatory_url}. "
    f"Memo at {memo_path}. Cost estimate: {cost_text}. "
    f"Archived to {archive_path}."
)
receipt_path.write_text(receipt + "\n", encoding="utf-8")
PY
  append_receipt_to_transcript "$AUTO_RECEIPT_FILE" "$TRANSCRIPT_PATH"
  python3 "$SKILL_DIR/scripts/finalize_live_output_hygiene.py" --run-id "${LOLLA_RUN_ID}" --quiet
  ARCHIVE_OUTPUT="$(python3 "$SKILL_DIR/scripts/archive_run.py" --run-id "${LOLLA_RUN_ID}")"
  printf '%s\n' "$ARCHIVE_OUTPUT"
  ARCHIVE_PATH="$(printf '%s\n' "$ARCHIVE_OUTPUT" | awk -F'path:[[:space:]]*' '/path:/ {print $2; exit}')"
  if [ -n "$ARCHIVE_PATH" ]; then
    echo "ARCHIVE_PATH: $ARCHIVE_PATH"
  fi
  USER_RECEIPT="$(cat "$AUTO_RECEIPT_FILE")"
fi

if [ -n "$USER_RECEIPT" ]; then
  echo "USER_RECEIPT_BEGIN"
  printf '%s\n' "$USER_RECEIPT"
  echo "USER_RECEIPT_END"
fi
