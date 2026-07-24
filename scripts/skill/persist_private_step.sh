#!/usr/bin/env bash
set -euo pipefail

REQUESTED_RUN_ID=""
KIND=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --kind)
      KIND="${2:-}"
      shift 2
      ;;
    --help|-h)
      cat <<'EOF'
Usage: bash scripts/skill/persist_private_step.sh --run-id RUN_HANDLE --kind KIND

Loads one exact Lolla run and persists a private narration, Step 6, memo, or
receipt payload from standard input.
EOF
      exit 0
      ;;
    *)
      echo "FATAL: unknown private-persistence argument." >&2
      exit 2
      ;;
  esac
done

case "$KIND" in
  narration|step6|memo|receipt)
    ;;
  *)
    echo "FATAL: private-persistence kind is missing or invalid." >&2
    exit 2
    ;;
esac

_LOLLA_HELPER_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
# shellcheck source=load_run_state.sh
. "$_LOLLA_HELPER_DIR/load_run_state.sh"
lolla_load_run_state "$REQUESTED_RUN_ID"

exec python3 "$SKILL_DIR/scripts/skill/persist_private_artifact.py" \
  --run-id "$LOLLA_RUN_ID" \
  --kind "$KIND" \
  --tmp-dir "$LOLLA_TMP_DIR"
