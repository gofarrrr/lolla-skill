#!/usr/bin/env bash

# Load one exact Lolla run in a fresh shell.
#
# Callers should pass the RUN_ID printed by setup. This deliberately never
# follows lolla_latest_env.sh: a convenience pointer cannot prove which of two
# concurrent or recently completed runs the caller intended.
lolla_load_run_state() {
  local requested_run_id="${1:-}"
  local runtime_tmp_dir="${LOLLA_TMP_DIR:-/tmp}"
  local state_path=""

  if [ -n "$requested_run_id" ]; then
    case "$requested_run_id" in
      *[!A-Za-z0-9_-]*)
        echo "FATAL: requested Lolla run ID is invalid." >&2
        return 2
        ;;
    esac
    if [ -n "${LOLLA_ENV_STATE:-}" ] && [ -f "$LOLLA_ENV_STATE" ]; then
      state_path="$LOLLA_ENV_STATE"
    else
      state_path="$runtime_tmp_dir/lolla_${requested_run_id}_env.sh"
    fi
  elif [ -n "${LOLLA_ENV_STATE:-}" ]; then
    state_path="$LOLLA_ENV_STATE"
  elif [ -n "${LOLLA_RUN_ID:-}" ]; then
    state_path="$runtime_tmp_dir/lolla_${LOLLA_RUN_ID}_env.sh"
    requested_run_id="$LOLLA_RUN_ID"
  else
    echo "FATAL: no exact Lolla run was requested." >&2
    return 2
  fi

  if [ ! -f "$state_path" ]; then
    echo "FATAL: exact Lolla run state is missing." >&2
    return 2
  fi

  # shellcheck source=/dev/null
  . "$state_path"

  if [ -z "${LOLLA_RUN_ID:-}" ] || [ -z "${LOLLA_EXPECTED_RUN_ID:-}" ]; then
    echo "FATAL: exact Lolla run state is incomplete." >&2
    return 2
  fi
  if [ "$LOLLA_RUN_ID" != "$LOLLA_EXPECTED_RUN_ID" ]; then
    echo "FATAL: exact Lolla run state is internally inconsistent." >&2
    return 2
  fi
  if [ -n "$requested_run_id" ] && [ "$LOLLA_RUN_ID" != "$requested_run_id" ]; then
    echo "FATAL: exact Lolla run state does not match the requested run." >&2
    return 2
  fi

  export LOLLA_ENV_STATE="$state_path"
  return 0
}
