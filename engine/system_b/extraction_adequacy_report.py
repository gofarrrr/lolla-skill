"""Deterministic extraction/provenance adequacy report.

This report inspects the existing chain:

    conversation.txt -> extraction.json -> ConversationContext -> ConversationIR

It does not call models, does not run specialist extractors, and does not score
semantic correctness. Its job is to expose what provenance the current chain
already preserves, weakens, or loses.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .source_coverage import build_source_coverage

from .conversation_loader import load_conversation_context
from .ir import ConversationIR
from .ir_constructor import construct_conversation_ir


EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION = "lolla.extraction_adequacy_report.v0"
EXTRACTION_ADEQUACY_REPORT_FILENAME = "extraction_adequacy_report.json"

_PROVENANCE_KINDS = ("span", "turn_ref", "derivation", "unknown")
_SPECIALIST_EXTRACTORS = {
    "live_constraints": "live_constraints_extraction",
    "dropped_threads": "dropped_threads_extraction",
    "assistant_stance": "stance_extraction",
}


def build_extraction_adequacy_report(
    run_dir: Path,
    *,
    run_id: str = "",
    case_id: str = "",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic report for one archived run directory."""

    run_dir = Path(run_dir)
    conversation_path = run_dir / "conversation.txt"
    extraction_path = run_dir / "extraction.json"
    extraction = _read_json_object(extraction_path)
    extraction_payload = _mapping(extraction.get("extraction"))
    capture_adequacy = _mapping(extraction.get("capture_adequacy"))
    quote_validation = _mapping(extraction_payload.get("_quote_validation"))

    context = None
    ir: ConversationIR | None = None
    context_error = ""
    ir_error = ""
    if conversation_path.is_file() and extraction_path.is_file():
        try:
            context = load_conversation_context(extraction_path, conversation_path)
        except Exception as exc:  # noqa: BLE001 - report generation must not crash archive
            context_error = _sanitized_error_code(
                exc,
                code="conversation_context_load_failed",
            )
        if context is not None:
            try:
                ir = construct_conversation_ir(context)
            except Exception as exc:  # noqa: BLE001 - report generation must not crash archive
                ir_error = _sanitized_error_code(
                    exc,
                    code="conversation_ir_build_failed",
                )

    context_summary = _conversation_context_summary(context)
    extraction_summary = _extraction_field_summary(extraction_payload, quote_validation)
    ref_summary = _extraction_turn_ref_summary(context=context, extraction=extraction_payload)
    ir_summary = _conversation_ir_summary(ir)
    gap_summary = _provenance_gap_summary(
        extraction=extraction_payload,
        quote_validation=quote_validation,
        ref_summary=ref_summary,
        ir_summary=ir_summary,
        capture_adequacy=capture_adequacy,
        context_error=context_error,
        ir_error=ir_error,
        conversation_present=conversation_path.is_file(),
        extraction_present=extraction_path.is_file(),
    )
    opportunities = _specialist_opportunities(extraction_summary, ir_summary, gap_summary)
    status = _adequacy_status(
        capture_adequacy=capture_adequacy,
        quote_validation=quote_validation,
        gap_summary=gap_summary,
        context_summary=context_summary,
        conversation_present=conversation_path.is_file(),
        extraction_present=extraction_path.is_file(),
    )

    return {
        "schema_version": EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION,
        "created_at": created_at or _utc_now_iso(),
        "run_id": run_id,
        "case_id": case_id,
        "source_artifacts": {
            "conversation": _artifact_source(conversation_path, "conversation.txt"),
            "extraction": _artifact_source(extraction_path, "extraction.json"),
        },
        "capture_summary": _capture_summary(extraction),
        "extraction_field_summary": extraction_summary,
        "conversation_context_summary": context_summary,
        "extraction_turn_ref_summary": ref_summary,
        "conversation_ir_provenance_summary": ir_summary,
        "provenance_gap_findings": gap_summary,
        "specialist_extractor_opportunities": opportunities,
        "adequacy_status": status,
        "notes": [
            "Raw transcript remains the source of truth.",
            "This report does not score semantic correctness.",
            "This report does not prove all important material was captured.",
            "This report does not approve agent action.",
            "Specialist extractor opportunities are diagnostic only; specialists were not run.",
        ],
    }


def write_extraction_adequacy_report(
    run_dir: Path,
    *,
    run_id: str = "",
    case_id: str = "",
    created_at: str | None = None,
    tmp_copy_path: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Write ``extraction_adequacy_report.json`` and optional tmp copy."""

    run_dir = Path(run_dir)
    payload = build_extraction_adequacy_report(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        created_at=created_at,
    )
    path = run_dir / EXTRACTION_ADEQUACY_REPORT_FILENAME
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if tmp_copy_path is not None:
        tmp_copy_path = Path(tmp_copy_path)
        tmp_copy_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, tmp_copy_path)
    return path, payload


def extraction_adequacy_report_from_artifacts(run_dir: Path) -> dict[str, Any]:
    """Read the report from a run directory when present."""

    return _read_json_object(Path(run_dir) / EXTRACTION_ADEQUACY_REPORT_FILENAME)


def _capture_summary(extraction: Mapping[str, Any]) -> dict[str, Any]:
    capture_manifest = _mapping(extraction.get("capture_manifest"))
    capture_adequacy = _mapping(extraction.get("capture_adequacy"))
    source_coverage = build_source_coverage(
        processing_view=_mapping(extraction.get("conversation_processing_view")),
        capture_adequacy=capture_adequacy,
    )
    return {
        "capture_health": _text(extraction.get("capture_health")) or "unknown",
        "capture_strategy": _text(capture_adequacy.get("capture_strategy")) or "unknown",
        "declared_turn_count": _nullable_int(capture_adequacy.get("declared_turn_count")),
        "captured_turn_count": _nullable_int(capture_adequacy.get("captured_turn_count")),
        "omitted_turn_count": _safe_int(capture_adequacy.get("omitted_turn_count")),
        "captured_windows": _list(capture_adequacy.get("captured_windows")),
        "omitted_windows": _list(capture_adequacy.get("omitted_windows")),
        "capture_adequacy_status": _text(capture_adequacy.get("status")) or "unknown",
        "truncation_applied": bool(capture_manifest.get("truncation_applied")),
        "truncation_reason_present": bool(_text(capture_manifest.get("truncation_reason"))),
        "authoritative_conversation_preserved": source_coverage[
            "authoritative_conversation_preserved"
        ],
        "extraction_processing_view_status": source_coverage[
            "extraction_processing_view_status"
        ],
    }


def _extraction_field_summary(
    extraction: Mapping[str, Any],
    quote_validation: Mapping[str, Any],
) -> dict[str, Any]:
    reasoning_passages = _list(extraction.get("reasoning_passages"))
    fabricated_count = _safe_int(quote_validation.get("fabricated"))
    verified_count = _safe_int(quote_validation.get("verified"), len(reasoning_passages))
    return {
        "decision_situation_present": bool(_text(extraction.get("decision_situation"))),
        "synthesized_position_present": bool(_text(extraction.get("synthesized_position"))),
        "original_framing_present": bool(_text(extraction.get("original_framing"))),
        "live_constraints_count": len(_list(extraction.get("live_constraints"))),
        "dropped_threads_count": len(_list(extraction.get("dropped_threads"))),
        "reasoning_passages_count": len(reasoning_passages),
        "quote_validation": {
            "present": bool(quote_validation),
            "total": _safe_int(quote_validation.get("total"), len(reasoning_passages) + fabricated_count),
            "verified": verified_count,
            "fabricated": fabricated_count,
            "fabricated_passage_count": len(_list(quote_validation.get("fabricated_passages")))
            or fabricated_count,
            "retry_attempted": bool(quote_validation.get("retry_attempted")),
            "retry_succeeded": bool(quote_validation.get("retry_succeeded")),
        },
    }


def _conversation_context_summary(context: Any) -> dict[str, Any]:
    if context is None:
        return {
            "available": False,
            "parsed_turn_count": 0,
            "user_turn_count": 0,
            "assistant_turn_count": 0,
        }
    user_turns = [turn for turn in context.turns if turn.speaker == "user"]
    assistant_turns = [turn for turn in context.turns if turn.speaker == "assistant"]
    return {
        "available": True,
        "parsed_turn_count": len(context.turns),
        "user_turn_count": len(user_turns),
        "assistant_turn_count": len(assistant_turns),
        "capture_health": context.capture_health,
        "capture_warning_count": len(context.capture_warnings),
    }


def _extraction_turn_ref_summary(
    *,
    context: Any,
    extraction: Mapping[str, Any],
) -> dict[str, Any]:
    turn_keys = set()
    turn_indexes = set()
    if context is not None:
        for turn in context.turns:
            turn_keys.add((turn.turn_index, turn.speaker))
            turn_indexes.add(turn.turn_index)

    live_items = [_mapping(item) for item in _list(extraction.get("live_constraints"))]
    dropped_items = [_mapping(item) for item in _list(extraction.get("dropped_threads"))]
    live_invalid = 0
    live_missing = 0
    live_speaker_mismatch = 0
    for item in live_items:
        raw_turn_index = item.get("introduced_turn")
        if raw_turn_index in (None, ""):
            live_missing += 1
            continue
        turn_index = _nullable_int(raw_turn_index)
        if turn_index is None or turn_index not in turn_indexes:
            live_invalid += 1
        elif (turn_index, "user") not in turn_keys:
            live_speaker_mismatch += 1

    dropped_invalid = 0
    dropped_missing = 0
    dropped_speaker_mismatch = 0
    for item in dropped_items:
        raw_turn_index = item.get("raised_turn")
        if raw_turn_index in (None, ""):
            dropped_missing += 1
            continue
        turn_index = _nullable_int(raw_turn_index)
        speaker = _normalize_speaker(_text(item.get("raised_by")) or "user")
        if turn_index is None or turn_index not in turn_indexes:
            dropped_invalid += 1
        elif (turn_index, speaker) not in turn_keys:
            dropped_speaker_mismatch += 1

    return {
        "live_constraints": {
            "count": len(live_items),
            "valid_turn_ref_count": (
                len(live_items) - live_invalid - live_missing - live_speaker_mismatch
            ),
            "missing_turn_ref_count": live_missing,
            "invalid_turn_ref_count": live_invalid,
            "speaker_mismatch_count": live_speaker_mismatch,
        },
        "dropped_threads": {
            "count": len(dropped_items),
            "valid_turn_ref_count": (
                len(dropped_items)
                - dropped_invalid
                - dropped_missing
                - dropped_speaker_mismatch
            ),
            "missing_turn_ref_count": dropped_missing,
            "invalid_turn_ref_count": dropped_invalid,
            "speaker_mismatch_count": dropped_speaker_mismatch,
        },
    }


def _conversation_ir_summary(ir: ConversationIR | None) -> dict[str, Any]:
    if ir is None:
        return {
            "available": False,
            "turn_count": 0,
            "frame_anchors_count": 0,
            "user_issue_events_count": 0,
            "stance_events_count": 0,
            "provenance_kinds_count": {kind: 0 for kind in _PROVENANCE_KINDS},
            "item_groups": _empty_item_groups(),
        }
    counts = {kind: 0 for kind in _PROVENANCE_KINDS}
    for kind, count in ir.provenance_tier_counts().items():
        counts[kind] = count
    groups = _empty_item_groups()
    groups["constraints"] = sum(1 for item in ir.user_issue_events if item.kind == "constraint")
    groups["open_loops"] = sum(1 for item in ir.user_issue_events if item.kind == "open_loop")
    groups["concerns"] = sum(1 for item in ir.user_issue_events if item.kind == "concern")
    groups["assistant_stance"] = sum(1 for item in ir.stance_events if item.speaker == "assistant")
    for anchor in ir.frame_anchors:
        if anchor.frame_pattern == "original_framing":
            groups["original_framing"] += 1
        elif anchor.frame_pattern == "decision_situation":
            groups["decision_situation"] += 1
    return {
        "available": True,
        "turn_count": len(ir.turns),
        "frame_anchors_count": len(ir.frame_anchors),
        "user_issue_events_count": len(ir.user_issue_events),
        "stance_events_count": len(ir.stance_events),
        "provenance_kinds_count": counts,
        "item_groups": groups,
    }


def _provenance_gap_summary(
    *,
    extraction: Mapping[str, Any],
    quote_validation: Mapping[str, Any],
    ref_summary: Mapping[str, Any],
    ir_summary: Mapping[str, Any],
    capture_adequacy: Mapping[str, Any],
    context_error: str,
    ir_error: str,
    conversation_present: bool,
    extraction_present: bool,
) -> dict[str, Any]:
    fields_present_not_span_grounded: list[str] = []
    fields_only_turn_ref_grounded: list[str] = []
    fields_derivation_grounded: list[str] = []
    fields_no_source_grounding: list[str] = []

    provenance_counts = _mapping(ir_summary.get("provenance_kinds_count"))
    if _text(extraction.get("decision_situation")):
        fields_derivation_grounded.append("decision_situation")
    if _text(extraction.get("original_framing")):
        fields_derivation_grounded.append("original_framing")
    if _list(extraction.get("live_constraints")):
        fields_only_turn_ref_grounded.append("live_constraints")
    if _list(extraction.get("dropped_threads")):
        fields_only_turn_ref_grounded.append("dropped_threads")
    if _text(extraction.get("synthesized_position")):
        fields_no_source_grounding.append("synthesized_position")

    span_count = _safe_int(provenance_counts.get("span"))
    if fields_only_turn_ref_grounded and span_count == 0:
        fields_present_not_span_grounded.extend(fields_only_turn_ref_grounded)
    if fields_derivation_grounded:
        fields_present_not_span_grounded.extend(fields_derivation_grounded)

    live_refs = _mapping(ref_summary.get("live_constraints"))
    dropped_refs = _mapping(ref_summary.get("dropped_threads"))
    invalid_turn_ref_count = (
        _safe_int(live_refs.get("invalid_turn_ref_count"))
        + _safe_int(dropped_refs.get("invalid_turn_ref_count"))
    )
    speaker_mismatch_count = (
        _safe_int(live_refs.get("speaker_mismatch_count"))
        + _safe_int(dropped_refs.get("speaker_mismatch_count"))
    )
    missing_turn_ref_count = (
        _safe_int(live_refs.get("missing_turn_ref_count"))
        + _safe_int(dropped_refs.get("missing_turn_ref_count"))
    )
    omitted_windows = _list(capture_adequacy.get("omitted_windows"))
    fabricated_count = _safe_int(quote_validation.get("fabricated"))
    return {
        "fields_present_but_not_span_grounded": sorted(set(fields_present_not_span_grounded)),
        "fields_only_turn_ref_grounded": sorted(set(fields_only_turn_ref_grounded)),
        "fields_derivation_grounded": sorted(set(fields_derivation_grounded)),
        "fields_with_no_source_grounding": sorted(set(fields_no_source_grounding)),
        "missing_turn_ref_count": missing_turn_ref_count,
        "invalid_turn_ref_count": invalid_turn_ref_count,
        "speaker_mismatch_count": speaker_mismatch_count,
        "quote_fabrication_count": fabricated_count,
        "quote_retry_attempted": bool(quote_validation.get("retry_attempted")),
        "omitted_middle_window_count": len(omitted_windows),
        "omitted_turn_count": _safe_int(capture_adequacy.get("omitted_turn_count")),
        "context_load_error": context_error,
        "conversation_ir_build_error": ir_error,
        "conversation_missing": not conversation_present,
        "extraction_missing": not extraction_present,
    }


def _specialist_opportunities(
    extraction_summary: Mapping[str, Any],
    ir_summary: Mapping[str, Any],
    gap_summary: Mapping[str, Any],
) -> dict[str, Any]:
    fields_turn_ref = set(_strings(gap_summary.get("fields_only_turn_ref_grounded")))
    fields_no_grounding = set(_strings(gap_summary.get("fields_with_no_source_grounding")))
    return {
        "specialists_were_run": False,
        "live_constraints_extraction": {
            "could_improve_grounding": "live_constraints" in fields_turn_ref,
            "current_count": _safe_int(extraction_summary.get("live_constraints_count")),
            "future_use": "Could replace paraphrased live_constraints mapping with span/derivation-provenance UserIssueEvent objects.",
        },
        "dropped_threads_extraction": {
            "could_improve_grounding": "dropped_threads" in fields_turn_ref,
            "current_count": _safe_int(extraction_summary.get("dropped_threads_count")),
            "future_use": "Could replace paraphrased dropped_threads mapping with span-provenance UserIssueEvent objects.",
        },
        "stance_extraction": {
            "could_cover_assistant_recommendations": _safe_int(_mapping(ir_summary.get("item_groups")).get("assistant_stance")) == 0,
            "current_stance_event_count": _safe_int(ir_summary.get("stance_events_count")),
            "future_use": "Could add assistant recommendation/commitment/revision spans as StanceEvent objects.",
        },
        "no_source_grounding_fields": sorted(fields_no_grounding),
        "module_names": dict(_SPECIALIST_EXTRACTORS),
    }


def _adequacy_status(
    *,
    capture_adequacy: Mapping[str, Any],
    quote_validation: Mapping[str, Any],
    gap_summary: Mapping[str, Any],
    context_summary: Mapping[str, Any],
    conversation_present: bool,
    extraction_present: bool,
) -> str:
    if not conversation_present or not extraction_present:
        return "critical"
    if not context_summary.get("available"):
        return "critical"
    if _safe_int(context_summary.get("parsed_turn_count")) <= 0:
        return "critical"
    if _text(capture_adequacy.get("status")) == "critical":
        return "critical"
    if _safe_int(gap_summary.get("invalid_turn_ref_count")) > 0:
        return "critical"
    if gap_summary.get("context_load_error") or gap_summary.get("conversation_ir_build_error"):
        return "critical"
    if _text(capture_adequacy.get("status")) in {"warn", "unknown"}:
        return "warn"
    if _safe_int(gap_summary.get("missing_turn_ref_count")) > 0:
        return "warn"
    if _safe_int(gap_summary.get("speaker_mismatch_count")) > 0:
        return "warn"
    if _safe_int(capture_adequacy.get("omitted_turn_count")) > 0:
        return "warn"
    if _safe_int(quote_validation.get("fabricated")) > 0:
        return "warn"
    return "good"


def _empty_item_groups() -> dict[str, int]:
    return {
        "constraints": 0,
        "open_loops": 0,
        "concerns": 0,
        "original_framing": 0,
        "decision_situation": 0,
        "assistant_stance": 0,
    }


def _artifact_source(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        return {"path": label, "present": False, "sha256": "", "bytes": 0}
    return {
        "path": label,
        "present": True,
        "sha256": _sha256_uri(path),
        "bytes": path.stat().st_size,
    }


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sha256_uri(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [str(item) for item in _list(value) if str(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


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


def _normalize_speaker(value: str) -> str:
    return value if value in {"user", "assistant"} else "user"


def _sanitized_error_code(exc: Exception, *, code: str) -> str:
    return f"{code}:{type(exc).__name__}"
