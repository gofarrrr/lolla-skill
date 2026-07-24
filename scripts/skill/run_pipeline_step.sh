#!/usr/bin/env bash
set -euo pipefail

REQUESTED_RUN_ID=""
REQUESTED_EXTRACTION=""
REQUESTED_CONVERSATION=""
REQUESTED_OUTPUT=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --help|-h)
      cat <<'EOF'
Usage: bash scripts/skill/run_pipeline_step.sh

Runs Step 3 using the current Lolla environment. Extra file/path arguments are
not needed; the helper derives paths from the run-specific environment state.
EOF
      exit 0
      ;;
    --run-id)
      REQUESTED_RUN_ID="${2:-}"
      shift 2
      ;;
    --extraction-file)
      REQUESTED_EXTRACTION="${2:-}"
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
    --skip-revision)
      shift
      ;;
    *)
      case "$1" in
        */lolla_*_extraction.json)
          if [ -n "$REQUESTED_EXTRACTION" ]; then
            echo "FATAL: run_pipeline_step.sh received multiple extraction paths." >&2
            exit 2
          fi
          REQUESTED_EXTRACTION="$1"
          shift
          ;;
        */lolla_*_conversation.txt)
          if [ -n "$REQUESTED_CONVERSATION" ]; then
            echo "FATAL: run_pipeline_step.sh received multiple conversation paths." >&2
            exit 2
          fi
          REQUESTED_CONVERSATION="$1"
          shift
          ;;
        */lolla_*_result.json)
          if [ -n "$REQUESTED_OUTPUT" ]; then
            echo "FATAL: run_pipeline_step.sh received multiple result paths." >&2
            exit 2
          fi
          REQUESTED_OUTPUT="$1"
          shift
          ;;
        *)
          echo "FATAL: unknown argument to run_pipeline_step.sh." >&2
          exit 2
          ;;
      esac
      ;;
  esac
done

_LOLLA_HELPER_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
# shellcheck source=load_run_state.sh
. "$_LOLLA_HELPER_DIR/load_run_state.sh"
lolla_load_run_state "$REQUESTED_RUN_ID"

if [ -z "${SKILL_DIR:-}" ] || [ ! -f "$SKILL_DIR/scripts/run_pipeline.py" ]; then
  echo "FATAL: Lolla runtime is incomplete. Re-run /lolla setup before Step 3." >&2
  exit 1
fi
if [ -n "${LOLLA_EXPECTED_RUN_ID:-}" ] && [ "${LOLLA_RUN_ID:-}" != "$LOLLA_EXPECTED_RUN_ID" ]; then
  echo "FATAL: exact Lolla run state mismatch." >&2
  exit 1
fi

if ! LOLLA_AUDIT_MODE="$(PYTHONPATH="$SKILL_DIR" python3 "$SKILL_DIR/scripts/skill/validate_audit_mode.py")"; then
  exit 1
fi
export LOLLA_AUDIT_MODE

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
EXPECTED_EXTRACTION="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_extraction.json"
EXPECTED_CONVERSATION="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_conversation.txt"
EXPECTED_RESULT="$RUNTIME_TMP_DIR/lolla_${LOLLA_RUN_ID}_result.json"

if [ -n "$REQUESTED_EXTRACTION" ] && [ "$REQUESTED_EXTRACTION" != "$EXPECTED_EXTRACTION" ]; then
  echo "FATAL: unexpected extraction artifact for the exact run." >&2
  exit 2
fi
if [ -n "$REQUESTED_CONVERSATION" ] && [ "$REQUESTED_CONVERSATION" != "$EXPECTED_CONVERSATION" ]; then
  echo "FATAL: unexpected conversation artifact for the exact run." >&2
  exit 2
fi
if [ -n "$REQUESTED_OUTPUT" ] && [ "$REQUESTED_OUTPUT" != "$EXPECTED_RESULT" ]; then
  echo "FATAL: unexpected result artifact for the exact run." >&2
  exit 2
fi

if [ ! -s "$EXPECTED_EXTRACTION" ]; then
  echo "FATAL: extraction JSON missing or empty for the exact run. Step 2 failed." >&2
  exit 1
fi
if [ ! -s "$EXPECTED_CONVERSATION" ]; then
  echo "FATAL: conversation source is missing or empty for the exact run. Step 1 failed." >&2
  exit 1
fi

if ! lolla_run_logged "Step 3 validate_conversation_capture.py" \
  python3 "$SKILL_DIR/scripts/skill/validate_conversation_capture.py" \
    --conversation-file "$EXPECTED_CONVERSATION"; then
  echo "FATAL: conversation capture is not parseable for Lolla. Details are in private operator custody." >&2
  exit 2
fi

args=(
  python3 "$SKILL_DIR/scripts/run_pipeline.py"
  --extraction-file "$EXPECTED_EXTRACTION"
  --conversation-file "$EXPECTED_CONVERSATION"
  --output-file "$EXPECTED_RESULT"
  --skip-revision
  --pre-step6-portfolio step6_private
)

if [ -n "${LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR:-}" ]; then
  args+=(--pre-step6-portfolio-cache-dir "$LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR")
fi
if [ -n "${LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF:-}" ]; then
  args+=(--pre-step6-portfolio-cache-ref "$LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF")
fi

if ! lolla_run_logged "Step 3 run_pipeline.py" "${args[@]}"; then
  echo "FATAL: pipeline command failed. Details are in private operator custody." >&2
  exit 1
fi

if ! lolla_run_logged "Step 3 pre-Step-6 private table receipt" python3 - <<'PY'
import json
import os
from pathlib import Path

run_id = os.environ.get("LOLLA_RUN_ID", "")
tmp_dir = Path(os.environ.get("LOLLA_TMP_DIR", "/tmp")).expanduser()
result_path = tmp_dir / f"lolla_{run_id}_result.json"
if not run_id or not result_path.exists():
    raise SystemExit("FATAL: cannot render pre-Step-6 receipt; result.json is missing.")

result = json.loads(result_path.read_text(encoding="utf-8"))
table = result.get("pre_step6_private_table") or {}
cache = table.get("cache") or {}
source_items = table.get("source_items") or []
cached_sources = [
    item.get("source_id", "")
    for item in source_items
    if str(item.get("source_id", "")).startswith("cached_card::")
]
cache_dir = str(cache.get("cache_dir") or "")
compiled_key = str(table.get("compiled_card_deck_key") or "")
expected_ref = ""
if cache_dir and compiled_key:
    expected_ref = str(Path(cache_dir) / f"{compiled_key}.pre-step6-shadow-card-deck.v1.json")

print("Pre-Step-6 private table receipt:")
print(f"  status: {table.get('status', 'missing')}")
print(f"  source atoms: {len(source_items)}")
print(f"  cached cards: {len(cached_sources)}")
print(f"  cache state: {cache.get('state', 'not_checked')}")
print(f"  cache resolution: {cache.get('resolution', 'not_available')}")
print(f"  cache dir: {cache_dir or 'not configured'}")
if cache.get("operator_cache_ref"):
    print(f"  operator cache ref: {cache.get('operator_cache_ref')}")
if cache.get("cache_ref"):
    print(f"  loaded cache ref: {cache.get('cache_ref')}")
print(f"  compiled key: {compiled_key or 'not available'}")
if expected_ref:
    print(f"  expected cache file: {expected_ref}")
print("  Step 7: rested by default")

require_hit = os.environ.get("LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT", "").lower() in {
    "1",
    "true",
    "on",
    "yes",
}
if require_hit and cache.get("state") != "cache_hit":
    raise SystemExit("FATAL: required pre-Step-6 cache hit, but cached cards were not loaded.")
PY
then
  echo "FATAL: pre-Step-6 validation failed. Details are in private operator custody." >&2
  exit 1
fi

PIPELINE_HEALTH="$(python3 - <<'PY'
import json
import os
from pathlib import Path

run_id = os.environ.get("LOLLA_RUN_ID", "")
tmp_dir = Path(os.environ.get("LOLLA_TMP_DIR", "/tmp")).expanduser()
path = tmp_dir / f"lolla_{run_id}_result.json"
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    print("unknown")
else:
    print((payload.get("run_health") or {}).get("overall", "unknown"))
PY
)"
record_run_event_quiet pipeline_completed \
  --detail "status=ok" \
  --detail "run_health=$PIPELINE_HEALTH" \
  --detail "result_path=$EXPECTED_RESULT"
python3 - <<'PY'
import json
import os
from pathlib import Path

run_id = os.environ.get("LOLLA_RUN_ID", "")
tmp_dir = Path(os.environ.get("LOLLA_TMP_DIR", "/tmp")).expanduser()
result_path = tmp_dir / f"lolla_{run_id}_result.json"
result = json.loads(result_path.read_text(encoding="utf-8"))
table = result.get("pre_step6_private_table") or {}
source_items = table.get("source_items") or []
cached_sources = [
    item.get("source_id", "")
    for item in source_items
    if str(item.get("source_id", "")).startswith("cached_card::")
]
cache = table.get("cache") or {}
health = (result.get("run_health") or {}).get("overall", "unknown")
print(f"PIPELINE_STATUS: ok")
print(f"RUN_HEALTH: {health}")
print(
    "PRE_STEP6_PRIVATE_TABLE: "
    f"status={table.get('status', 'missing')} "
    f"source_atoms={len(source_items)} "
    f"cached_cards={len(cached_sources)} "
    f"cache_state={cache.get('state', 'not_checked')}"
)
PY
