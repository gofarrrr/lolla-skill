"""Deterministic capture adequacy metadata for Lolla runs.

This module describes the shape of the captured conversation. It does not infer
what omitted turns contained and does not call a model.
"""
from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any


CAPTURE_ADEQUACY_SCHEMA_VERSION = "lolla.capture_adequacy.v0"

_TURN_MARKER_RE = re.compile(r"^\[Turn (\d+)\] (USER|ASSISTANT):\s*$", re.MULTILINE)
_OMITTED_MARKER_RE = re.compile(r"\[\.\.\.\s*(\d+)\s+turns?\s+omitted\b", re.IGNORECASE)


def build_capture_adequacy(
    *,
    conversation_text: str = "",
    run_id: str = "",
    capture_manifest: Mapping[str, Any] | None = None,
    capture_health: str = "",
    capture_warnings: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Return a compact, deterministic capture-shape manifest."""

    manifest = _mapping(capture_manifest)
    warnings = [str(item) for item in (capture_warnings or []) if str(item)]
    roles = [role for _turn, role in _TURN_MARKER_RE.findall(conversation_text or "")]
    actual_user = _safe_int(manifest.get("actual_user_turns"), roles.count("USER"))
    actual_assistant = _safe_int(
        manifest.get("actual_assistant_turns"),
        roles.count("ASSISTANT"),
    )
    observed_marker_count = len(roles)
    captured_marker_count = actual_user + actual_assistant

    declared_user = _nullable_int(manifest.get("declared_user"))
    declared_assistant = _nullable_int(manifest.get("declared_assistant"))
    if declared_user is not None or declared_assistant is not None:
        declared_turn_count = (declared_user or 0) + (declared_assistant or 0)
    else:
        declared_turn_count = _declared_turn_count_from_legacy_header(
            manifest.get("declared_turns"),
            actual_user=actual_user,
            actual_assistant=actual_assistant,
        )

    truncation_applied = bool(manifest.get("truncation_applied"))
    omitted_from_marker = _omitted_count_from_text(conversation_text)
    omitted_turn_count = _safe_int(manifest.get("omitted_turns"), omitted_from_marker)
    total_turns = _nullable_int(manifest.get("total_turns"))
    kept_turns = _nullable_int(manifest.get("kept_turns"))

    if truncation_applied:
        capture_strategy = "first_n_plus_last_n"
        declared_turn_count = total_turns or declared_turn_count or captured_marker_count + omitted_turn_count
        captured_turn_count = kept_turns or max((declared_turn_count or 0) - omitted_turn_count, 0)
    elif omitted_turn_count > 0:
        capture_strategy = "first_n_plus_last_n"
        declared_turn_count = declared_turn_count or captured_marker_count + omitted_turn_count
        captured_turn_count = captured_marker_count
    elif declared_turn_count is None:
        capture_strategy = "unknown"
        captured_turn_count = captured_marker_count
    else:
        capture_strategy = "full"
        captured_turn_count = captured_marker_count
        omitted_turn_count = max(declared_turn_count - captured_turn_count, 0)

    declared_for_windows = declared_turn_count or captured_turn_count
    captured_windows = _captured_windows(
        capture_strategy=capture_strategy,
        declared_turn_count=declared_for_windows,
        captured_turn_count=captured_turn_count,
        omitted_turn_count=omitted_turn_count,
        manifest=manifest,
    )
    omitted_windows = _omitted_windows(
        capture_strategy=capture_strategy,
        declared_turn_count=declared_for_windows,
        captured_turn_count=captured_turn_count,
        omitted_turn_count=omitted_turn_count,
        manifest=manifest,
    )
    status, risk_flags, notes = _status_flags_notes(
        capture_health=str(capture_health or ""),
        capture_strategy=capture_strategy,
        declared_turn_count=declared_turn_count,
        captured_turn_count=captured_turn_count,
        omitted_turn_count=omitted_turn_count,
        actual_user=actual_user,
        actual_assistant=actual_assistant,
        observed_marker_count=observed_marker_count,
        warnings=warnings,
    )

    return {
        "schema_version": CAPTURE_ADEQUACY_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "capture_strategy": capture_strategy,
        "declared_turn_count": declared_turn_count,
        "captured_turn_count": captured_turn_count,
        "omitted_turn_count": omitted_turn_count,
        "captured_windows": captured_windows,
        "omitted_windows": omitted_windows,
        "risk_flags": risk_flags,
        "notes": notes,
    }


def capture_adequacy_from_artifacts(
    *,
    extraction: Mapping[str, Any] | None = None,
    result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Read capture adequacy from extraction first, then run_health."""

    extraction_map = _mapping(extraction)
    direct = _mapping(extraction_map.get("capture_adequacy"))
    if direct:
        return dict(direct)
    run_health = _mapping(_mapping(result).get("run_health"))
    from_health = _mapping(run_health.get("capture_adequacy"))
    return dict(from_health) if from_health else {}


def _captured_windows(
    *,
    capture_strategy: str,
    declared_turn_count: int,
    captured_turn_count: int,
    omitted_turn_count: int,
    manifest: Mapping[str, Any],
) -> list[dict[str, int | str]]:
    if captured_turn_count <= 0:
        return []
    if capture_strategy != "first_n_plus_last_n" or omitted_turn_count <= 0:
        return [
            {
                "label": "full",
                "start_turn": 1,
                "end_turn": captured_turn_count,
                "turn_count": captured_turn_count,
            }
        ]

    first_count = min(_safe_int(manifest.get("keep_first_turns"), 3), captured_turn_count)
    last_count = max(captured_turn_count - first_count, 0)
    windows: list[dict[str, int | str]] = []
    if first_count:
        windows.append(
            {
                "label": "opening",
                "start_turn": 1,
                "end_turn": first_count,
                "turn_count": first_count,
            }
        )
    if last_count:
        start = max(declared_turn_count - last_count + 1, first_count + omitted_turn_count + 1)
        windows.append(
            {
                "label": "recent",
                "start_turn": start,
                "end_turn": declared_turn_count,
                "turn_count": last_count,
            }
        )
    return windows


def _omitted_windows(
    *,
    capture_strategy: str,
    declared_turn_count: int,
    captured_turn_count: int,
    omitted_turn_count: int,
    manifest: Mapping[str, Any],
) -> list[dict[str, int]]:
    if omitted_turn_count <= 0:
        return []
    if capture_strategy == "first_n_plus_last_n":
        first_count = min(_safe_int(manifest.get("keep_first_turns"), 3), captured_turn_count)
        start = first_count + 1
        end = min(start + omitted_turn_count - 1, declared_turn_count)
        return [{"start_turn": start, "end_turn": end, "turn_count": omitted_turn_count}]
    start = captured_turn_count + 1
    end = min(start + omitted_turn_count - 1, declared_turn_count)
    return [{"start_turn": start, "end_turn": end, "turn_count": omitted_turn_count}]


def _status_flags_notes(
    *,
    capture_health: str,
    capture_strategy: str,
    declared_turn_count: int | None,
    captured_turn_count: int,
    omitted_turn_count: int,
    actual_user: int,
    actual_assistant: int,
    observed_marker_count: int,
    warnings: Sequence[str],
) -> tuple[str, list[str], list[str]]:
    risk_flags: list[str] = []
    notes: list[str] = []

    if capture_health == "critical":
        risk_flags.append("capture_health_critical")
    if observed_marker_count == 0:
        risk_flags.append("no_turn_markers")
    if actual_user == 0:
        risk_flags.append("zero_user_turns_captured")
    if actual_assistant == 0:
        risk_flags.append("zero_assistant_turns_captured")
    if declared_turn_count is not None and captured_turn_count > declared_turn_count:
        risk_flags.append("captured_count_exceeds_declared")
    if declared_turn_count is not None and captured_turn_count < declared_turn_count and omitted_turn_count <= 0:
        risk_flags.append("declared_turns_missing")
    if omitted_turn_count > 0:
        risk_flags.append("middle_turns_omitted")
    if capture_strategy == "unknown":
        risk_flags.append("capture_strategy_unknown")

    if "middle_turns_omitted" in risk_flags:
        notes.append("Middle turns were omitted; constraints introduced there may be missing.")
    if "declared_turns_missing" in risk_flags:
        notes.append("Declared turn counts exceed captured markers without an explicit omitted window.")
    if "capture_strategy_unknown" in risk_flags:
        notes.append("Capture header or strategy metadata is incomplete.")
    if "zero_user_turns_captured" in risk_flags:
        notes.append("No user turns were captured.")
    if "zero_assistant_turns_captured" in risk_flags:
        notes.append("No assistant turns were captured.")
    if "captured_count_exceeds_declared" in risk_flags:
        notes.append("Captured turn count exceeds declared count; inspect Step 1 capture format.")
    notes.extend(warnings[:3])

    critical_flags = {
        "capture_health_critical",
        "no_turn_markers",
        "zero_user_turns_captured",
        "zero_assistant_turns_captured",
        "captured_count_exceeds_declared",
    }
    if any(flag in risk_flags for flag in critical_flags):
        status = "critical"
    elif risk_flags:
        status = "warn"
    else:
        status = "good"

    return status, sorted(set(risk_flags)), _dedupe(notes)


def _omitted_count_from_text(text: str) -> int:
    total = 0
    for match in _OMITTED_MARKER_RE.finditer(text or ""):
        total += _safe_int(match.group(1), 0)
    return total


def _declared_turn_count_from_legacy_header(
    value: Any,
    *,
    actual_user: int,
    actual_assistant: int,
) -> int | None:
    declared = _nullable_int(value)
    if declared is None:
        return None
    # Older tests/docs sometimes used "1 turn, 1 user message, 1 assistant
    # response" to mean one exchange, while newer live runs use marker count.
    # Treat the pair-style header as fully captured rather than contradictory.
    if actual_user and actual_assistant and declared == max(actual_user, actual_assistant):
        return actual_user + actual_assistant
    return declared


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _nullable_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _dedupe(items: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        output.append(text)
        seen.add(text)
    return output
