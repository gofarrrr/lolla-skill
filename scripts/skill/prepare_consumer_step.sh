#!/usr/bin/env bash
set -euo pipefail

REQUESTED_RUN_ID=""
STAGE=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --stage)
      STAGE="${2:-}"
      shift 2
      ;;
    --help|-h)
      cat <<'EOF'
Usage: bash scripts/skill/prepare_consumer_step.sh --run-id RUN_HANDLE --stage STAGE

Loads one exact Lolla run and prepares its readback, reconsideration, or
verification consumer packet.
EOF
      exit 0
      ;;
    *)
      echo "FATAL: unknown consumer-packet argument." >&2
      exit 2
      ;;
  esac
done

case "$STAGE" in
  readback|reconsideration|verification)
    ;;
  *)
    echo "FATAL: consumer-packet stage is missing or invalid." >&2
    exit 2
    ;;
esac

_LOLLA_HELPER_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
# shellcheck source=load_run_state.sh
. "$_LOLLA_HELPER_DIR/load_run_state.sh"
lolla_load_run_state "$REQUESTED_RUN_ID"

exec python3 "$SKILL_DIR/scripts/skill/prepare_consumer_packet.py" \
  --run-id "$LOLLA_RUN_ID" \
  --stage "$STAGE" \
  --tmp-dir "$LOLLA_TMP_DIR"
