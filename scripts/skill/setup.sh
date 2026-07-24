#!/usr/bin/env bash

# Every fresh Lolla artifact can contain the user's private conversation or a
# derivative of it. Keep new files owner-only even when the invoking shell has
# a permissive default.
umask 077

# Resolve the root of this bundled skill from this script's own location.
# This works from a repository clone, a copied installation, or a symlinked
# Claude Code/Codex installation and never searches for another project tree.
_LOLLA_SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd -P)"
if [ -z "$_LOLLA_SCRIPT_DIR" ]; then
  echo "FATAL: Cannot resolve the bundled lolla setup directory"
  exit 1
fi
SKILL_DIR="$(CDPATH= cd -- "$_LOLLA_SCRIPT_DIR/../.." 2>/dev/null && pwd -P)"
if [ -z "$SKILL_DIR" ] || [ ! -f "$SKILL_DIR/SKILL.md" ]; then
  echo "FATAL: Cannot resolve the lolla skill root from scripts/skill/setup.sh"
  exit 1
fi
export SKILL_DIR
echo "SKILL_DIR: $SKILL_DIR"

# Verify engine is bundled
if [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/engine/system_b/__init__.py" ]; then
  echo "ENGINE: bundled"
else
  echo "FATAL: Missing engine/system_b/ — the skill may be incomplete"
fi

# Verify data files
if [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/data/knowledge_graph.json" ]; then
  echo "DATA: $SKILL_DIR/data"
else
  echo "FATAL: Missing data/knowledge_graph.json"
fi

# Load API keys from the skill package or the documented global config. A key
# already exported by the operator remains available. Do not advertise a
# project-local env file that later fresh-shell entrypoints cannot rediscover.
# Always load so ALL keys (OPENROUTER + OPENAI) are available.
# Research-only overrides live in .env.research and are loaded only when
# LOLLA_RESEARCH_MODE=1/true/on/yes is set before setup runs, or inside .env.
_ENV_FILE=""
[ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/.env" ] && _ENV_FILE="$SKILL_DIR/.env"
[ -z "$_ENV_FILE" ] && [ -f "$HOME/.config/lolla/.env" ] && _ENV_FILE="$HOME/.config/lolla/.env"
if [ -n "$_ENV_FILE" ]; then
  set -a; source "$_ENV_FILE" 2>/dev/null; set +a
  echo "ENV: $_ENV_FILE"
fi
_RESEARCH_MODE="$(printf '%s' "${LOLLA_RESEARCH_MODE:-off}" | tr '[:upper:]' '[:lower:]')"
if [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/.env.research" ] && {
  [ "$_RESEARCH_MODE" = "1" ] || [ "$_RESEARCH_MODE" = "true" ] || [ "$_RESEARCH_MODE" = "on" ] || [ "$_RESEARCH_MODE" = "yes" ]
}; then
  set -a; source "$SKILL_DIR/.env.research" 2>/dev/null; set +a
  echo "ENV_RESEARCH: $SKILL_DIR/.env.research"
fi

if ! LOLLA_AUDIT_MODE="$(PYTHONPATH="$SKILL_DIR" python3 "$SKILL_DIR/scripts/skill/validate_audit_mode.py")"; then
  exit 1
fi
export LOLLA_AUDIT_MODE
echo "AUDIT_MODE: $LOLLA_AUDIT_MODE"

# Check API keys
if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$LOLLA_OPENROUTER_API_KEY" ]; then
  echo "FATAL: Set OPENROUTER_API_KEY. Run: mkdir -p ~/.config/lolla && echo 'OPENROUTER_API_KEY=your-key' > ~/.config/lolla/.env"
else
  echo "OPENROUTER: configured"
fi

if [ -z "$OPENAI_API_KEY" ]; then
  echo "WARNING: OPENAI_API_KEY not set — optional embedding retrieval and query expansion will be disabled; no accuracy claim is implied."
else
  echo "OPENAI: configured"
fi

# Generate a collision-resistant run ID for unique temp filenames.
# Timestamp alone is unsafe when runs start in parallel.
LOLLA_RUN_ID=$(PYTHONPATH="$SKILL_DIR" python3 - << 'PY'
from engine.system_b.run_state import make_run_id
print(make_run_id())
PY
)
export LOLLA_RUN_ID
LOLLA_EXPECTED_RUN_ID="$LOLLA_RUN_ID"
export LOLLA_EXPECTED_RUN_ID
echo "RUN_ID: $LOLLA_RUN_ID"

# Durable live transcript for user-visible Claude Code prose.
# Append every visible status/content/receipt message to this file exactly as
# sent, separated by blank lines. This is a product surface, not an operator log.
LOLLA_LIVE_TRANSCRIPT="/tmp/lolla_${LOLLA_RUN_ID}_live_transcript.txt"
export LOLLA_LIVE_TRANSCRIPT
: > "$LOLLA_LIVE_TRANSCRIPT"
chmod 600 "$LOLLA_LIVE_TRANSCRIPT"
echo "LIVE_TRANSCRIPT: $LOLLA_LIVE_TRANSCRIPT"

# Operator-only log for verbose helper output, provider warnings, validation
# receipts, and diagnostic command summaries. Do not append this to the live
# transcript; archive it as process evidence.
LOLLA_OPERATOR_LOG="/tmp/lolla_${LOLLA_RUN_ID}_operator.log"
export LOLLA_OPERATOR_LOG
: > "$LOLLA_OPERATOR_LOG"
chmod 600 "$LOLLA_OPERATOR_LOG"
echo "OPERATOR_LOG: $LOLLA_OPERATOR_LOG"

# Report config
echo "MODEL: ${LOLLA_OPENROUTER_MODEL:-google/gemini-3.1-flash-lite}"
[ -n "$OPENAI_API_KEY" ] && echo "EMBEDDINGS: enabled" || echo "EMBEDDINGS: disabled"

# Optional pre-Step-6 cached-card lookup. Cache misses never generate live
# cards; set LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT=1 only for controlled cache-hit
# tests where a miss should stop the run before Step 6.
if [ -n "${LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR:-}" ]; then
  echo "PRE_STEP6_CACHE_DIR: $LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR"
else
  echo "PRE_STEP6_CACHE_DIR: not configured"
fi
if [ -n "${LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF:-}" ]; then
  echo "PRE_STEP6_CACHE_REF: $LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF"
fi
if [ "${LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT:-off}" = "1" ] || [ "${LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT:-off}" = "true" ] || [ "${LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT:-off}" = "on" ]; then
  echo "PRE_STEP6_REQUIRE_CACHE_HIT: on"
fi

# V60 private enrichment is ON by default. Disable with:
#   export LOLLA_V60_ENRICHMENT=off
if [ "${LOLLA_V60_ENRICHMENT:-on}" = "off" ] || [ "${LOLLA_V60_ENRICHMENT:-on}" = "0" ]; then
  echo "V60: disabled"
elif [ -n "$SKILL_DIR" ] && [ -f "$SKILL_DIR/data/compiled/model_affordances/affordances_v60.json" ]; then
  echo "V60: enabled"
else
  echo "V60: missing artifact"
fi

# Persist runtime state because Claude Code Bash calls may not share shell
# exports. Later steps must source this file before using SKILL_DIR/RUN_ID.
LOLLA_ENV_STATE="/tmp/lolla_${LOLLA_RUN_ID}_env.sh"
export LOLLA_ENV_STATE
cat > "$LOLLA_ENV_STATE" << EOF
umask 077
export SKILL_DIR="$SKILL_DIR"
export LOLLA_RUN_ID="$LOLLA_RUN_ID"
export LOLLA_EXPECTED_RUN_ID="$LOLLA_EXPECTED_RUN_ID"
export LOLLA_LIVE_TRANSCRIPT="$LOLLA_LIVE_TRANSCRIPT"
export LOLLA_OPERATOR_LOG="$LOLLA_OPERATOR_LOG"
export LOLLA_ENV_STATE="$LOLLA_ENV_STATE"
export LOLLA_AUDIT_MODE="$LOLLA_AUDIT_MODE"
EOF
python3 - "$LOLLA_ENV_STATE" << 'PY'
import os
import shlex
import sys

path = sys.argv[1]
keys = [
    "LOLLA_RESEARCH_MODE",
    "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_DIR",
    "LOLLA_PRE_STEP6_PORTFOLIO_CACHE_REF",
    "LOLLA_PRE_STEP6_REQUIRE_CACHE_HIT",
]
with open(path, "a", encoding="utf-8") as handle:
    for key in keys:
        value = os.environ.get(key)
        if value:
            handle.write(f"export {key}={shlex.quote(value)}\n")
PY
chmod 600 "$LOLLA_ENV_STATE"
ln -sf "$LOLLA_ENV_STATE" /tmp/lolla_latest_env.sh
echo "ENV_STATE: $LOLLA_ENV_STATE"
python3 "$SKILL_DIR/scripts/record_run_event.py" --run-id "$LOLLA_RUN_ID" --event-type run_initialized --detail latest_env_pointer=/tmp/lolla_latest_env.sh --detail risk_mode="$LOLLA_AUDIT_MODE" --quiet || true
