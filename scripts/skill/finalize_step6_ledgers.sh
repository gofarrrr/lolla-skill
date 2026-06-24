#!/usr/bin/env bash
set -euo pipefail

MODE="all"
REQUESTED_RUN_ID=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pre-step6-only)
      MODE="pre"
      shift
      ;;
    --v60-only)
      MODE="v60"
      shift
      ;;
    --all)
      MODE="all"
      shift
      ;;
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --help|-h)
      cat <<'EOF'
Usage:
  bash scripts/skill/finalize_step6_ledgers.sh --pre-step6-only
  bash scripts/skill/finalize_step6_ledgers.sh --v60-only
  bash scripts/skill/finalize_step6_ledgers.sh --all

Finalizes Step 6b custody ledgers for the current Lolla run.
EOF
      exit 0
      ;;
    *)
      echo "FATAL: unknown argument to finalize_step6_ledgers.sh: $1" >&2
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
  echo "FATAL: SKILL_DIR is not set. Re-run /lolla setup before Step 6b." >&2
  exit 1
fi
if [ -z "${LOLLA_RUN_ID:-}" ]; then
  echo "FATAL: LOLLA_RUN_ID is not set. Re-run /lolla setup before Step 6b." >&2
  exit 1
fi

case "$MODE" in
  pre)
    python3 "$SKILL_DIR/scripts/finalize_pre_step6_private_table_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    echo "STEP6_LEDGER_STATUS: pre_step6 finalized"
    ;;
  v60)
    python3 "$SKILL_DIR/scripts/finalize_v60_telemetry.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    echo "STEP6_LEDGER_STATUS: v60 finalized"
    ;;
  all)
    python3 "$SKILL_DIR/scripts/finalize_pre_step6_private_table_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    python3 "$SKILL_DIR/scripts/finalize_v60_telemetry.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    echo "STEP6_LEDGER_STATUS: all finalized"
    ;;
esac
