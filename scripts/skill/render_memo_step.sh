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

Persists the exact run's private memo-note fields and renders its private memo.
EOF
      exit 0
      ;;
    *)
      echo "FATAL: unknown argument to render_memo_step.sh: $1" >&2
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
  echo "FATAL: SKILL_DIR is not set. Re-run /lolla setup before Step 8c." >&2
  exit 1
fi
if [ -z "${LOLLA_RUN_ID:-}" ]; then
  echo "FATAL: LOLLA_RUN_ID is not set. Re-run /lolla setup before Step 8c." >&2
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

RUNTIME_TMP_DIR="${LOLLA_TMP_DIR:-/tmp}"
RESULT_PATH="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_result.json"
NOTE_PATH="${REQUESTED_NOTE:-$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_memo_note.json}"
MEMO_PATH="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_memo.md"

if [ -n "$REQUESTED_RESULT" ] && [ "$REQUESTED_RESULT" != "$RESULT_PATH" ]; then
  echo "FATAL: render_memo_step.sh received a result artifact for a different run." >&2
  exit 2
fi
if [ -n "$REQUESTED_OUTPUT" ] && [ "$REQUESTED_OUTPUT" != "$MEMO_PATH" ]; then
  echo "FATAL: render_memo_step.sh received a memo target for a different run." >&2
  exit 2
fi

if [ ! -s "$RESULT_PATH" ]; then
  echo "FATAL: the exact run has no result artifact. Step 3 did not complete." >&2
  exit 1
fi
if [ ! -s "$NOTE_PATH" ]; then
  echo "FATAL: the exact run has no private memo note. Step 8c did not complete." >&2
  exit 1
fi

render_args=(python3 "$SKILL_DIR/scripts/render_memo.py" --result "$RESULT_PATH" --output "$MEMO_PATH")
if [ "$INCLUDE_APPENDIX" -eq 1 ]; then
  render_args+=(--include-audit-appendix)
fi
if ! lolla_run_logged "Step 8c render_memo.py" "${render_args[@]}"; then
  echo "FATAL: memo rendering failed. Details are in private operator custody." >&2
  exit 1
fi
record_run_event_quiet memo_rendered \
  --detail "memo_path=$MEMO_PATH" \
  --detail "include_audit_appendix=$INCLUDE_APPENDIX"
echo "MEMO_STATUS: ready"
