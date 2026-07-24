#!/usr/bin/env bash

# Shared operator-only logging helpers for skill shell wrappers.
# Source this after the run-specific environment state is loaded.

lolla_operator_log_init() {
  if [ -z "${LOLLA_RUN_ID:-}" ]; then
    return 0
  fi
  if [ -z "${LOLLA_OPERATOR_LOG:-}" ]; then
    LOLLA_OPERATOR_LOG="${LOLLA_TMP_DIR:-/tmp}/lolla_${LOLLA_RUN_ID}_operator.log"
    export LOLLA_OPERATOR_LOG
  fi
  touch "$LOLLA_OPERATOR_LOG" 2>/dev/null || true
}

lolla_operator_timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

lolla_operator_note() {
  local message="$*"
  lolla_operator_log_init
  if [ -z "${LOLLA_OPERATOR_LOG:-}" ]; then
    return 0
  fi
  printf '[%s] %s\n' "$(lolla_operator_timestamp)" "$message" >> "$LOLLA_OPERATOR_LOG" 2>/dev/null || true
}

lolla_operator_block() {
  local label="$1"
  local text="${2:-}"
  lolla_operator_log_init
  if [ -z "${LOLLA_OPERATOR_LOG:-}" ]; then
    return 0
  fi
  {
    printf '\n[%s] BEGIN %s\n' "$(lolla_operator_timestamp)" "$label"
    printf '%s\n' "$text"
    printf '[%s] END %s\n' "$(lolla_operator_timestamp)" "$label"
  } >> "$LOLLA_OPERATOR_LOG" 2>/dev/null || true
}

lolla_run_logged() {
  local label="$1"
  shift
  lolla_operator_log_init
  if [ -z "${LOLLA_OPERATOR_LOG:-}" ]; then
    "$@"
    return "$?"
  fi

  {
    printf '\n[%s] BEGIN %s\n' "$(lolla_operator_timestamp)" "$label"
  } >> "$LOLLA_OPERATOR_LOG" 2>/dev/null || true

  local had_errexit=0
  case "$-" in
    *e*)
      had_errexit=1
      set +e
      ;;
  esac

  "$@" >> "$LOLLA_OPERATOR_LOG" 2>&1
  local status="$?"

  if [ "$had_errexit" -eq 1 ]; then
    set -e
  fi

  {
    printf '[%s] END %s exit=%s\n' "$(lolla_operator_timestamp)" "$label" "$status"
  } >> "$LOLLA_OPERATOR_LOG" 2>/dev/null || true

  return "$status"
}
