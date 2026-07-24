#!/usr/bin/env bash
set -euo pipefail

REQUESTED_RUN_ID=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --help|-h)
      echo "Usage: bash scripts/skill/capture_step.sh --run-id RUN_ID"
      exit 0
      ;;
    *)
      echo "FATAL: unknown capture-step argument." >&2
      exit 2
      ;;
  esac
done

_LOLLA_HELPER_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
# shellcheck source=load_run_state.sh
. "$_LOLLA_HELPER_DIR/load_run_state.sh"
lolla_load_run_state "$REQUESTED_RUN_ID"

exec python3 "$SKILL_DIR/scripts/skill/capture_conversation.py"
