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
    --graph-only)
      MODE="graph"
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
  bash scripts/skill/finalize_step6_ledgers.sh --graph-only
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

_LOLLA_HELPER_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
# shellcheck source=load_run_state.sh
. "$_LOLLA_HELPER_DIR/load_run_state.sh"
lolla_load_run_state "$REQUESTED_RUN_ID"
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

record_run_event_quiet() {
  local event_type="$1"
  shift
  python3 "$SKILL_DIR/scripts/record_run_event.py" \
    --run-id "$LOLLA_RUN_ID" \
    --event-type "$event_type" \
    "$@" \
    --quiet || true
}

case "$MODE" in
  pre)
    python3 "$SKILL_DIR/scripts/finalize_pre_step6_private_table_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    record_run_event_quiet step6_ledgers_finalized --detail "mode=pre_step6"
    echo "STEP6_LEDGER_STATUS: pre_step6 finalized"
    ;;
  v60)
    python3 "$SKILL_DIR/scripts/finalize_v60_telemetry.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    record_run_event_quiet step6_ledgers_finalized --detail "mode=v60"
    echo "STEP6_LEDGER_STATUS: v60 finalized"
    ;;
  graph)
    python3 "$SKILL_DIR/scripts/finalize_constitutional_graph_survival_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    record_run_event_quiet step6_ledgers_finalized --detail "mode=constitutional_graph_survival"
    echo "STEP6_LEDGER_STATUS: constitutional graph survival finalized"
    ;;
  all)
    python3 "$SKILL_DIR/scripts/finalize_constitutional_graph_survival_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    python3 "$SKILL_DIR/scripts/finalize_pre_step6_private_table_ledger.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    python3 "$SKILL_DIR/scripts/finalize_v60_telemetry.py" --run-id "${LOLLA_RUN_ID}" --quiet --require-valid
    record_run_event_quiet step6_ledgers_finalized --detail "mode=all"
    echo "STEP6_LEDGER_STATUS: all finalized"
    ;;
esac
