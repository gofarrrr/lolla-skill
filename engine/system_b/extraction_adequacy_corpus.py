"""Corpus-level survey helpers for extraction/provenance adequacy.

This module builds a deterministic, local-only index over archived Lolla runs
using ``extraction_adequacy_report.json`` when present, or an in-memory report
for older archives when the source artifacts still exist. It does not mutate
archives, call models, score answer quality, or copy raw transcript/memo text
into the export.
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from .extraction_adequacy_report import (
    EXTRACTION_ADEQUACY_REPORT_FILENAME,
    build_extraction_adequacy_report,
)
from .reasoning_trace_dataset import DEFAULT_ARCHIVE_ROOT


EXTRACTION_ADEQUACY_CORPUS_RECORD_SCHEMA_VERSION = (
    "lolla.extraction_adequacy_corpus_record.v0"
)
EXTRACTION_ADEQUACY_CORPUS_MANIFEST_SCHEMA_VERSION = (
    "lolla.extraction_adequacy_corpus_manifest.v0"
)

RECOMMENDED_REVIEW_BUCKETS = (
    "critical_extraction_review",
    "warning_extraction_review",
    "legacy_missing_report_review",
    "clean_baseline_sample",
    "not_reviewable",
)

_RECOGNIZED_ARTIFACTS = (
    "conversation.txt",
    "extraction.json",
    "result.json",
    "revised.txt",
    "memo.md",
    "agent_result.json",
    "reasoning_trace.json",
    "run_events.json",
    "evaluation.json",
    EXTRACTION_ADEQUACY_REPORT_FILENAME,
)

_SPECIALIST_KEYS = (
    "live_constraints_extraction",
    "dropped_threads_extraction",
    "stance_extraction",
)


def build_extraction_adequacy_corpus_records(
    archive_root: Path | str,
) -> list[dict[str, Any]]:
    """Build one deterministic extraction-adequacy record per archived run."""

    root = Path(archive_root).expanduser()
    if not root.exists():
        return []
    records = [
        build_extraction_adequacy_corpus_record(run_dir, archive_root=root)
        for run_dir in _iter_run_dirs(root)
    ]
    return sorted(
        records,
        key=lambda record: (
            _text(record.get("case_id")),
            _text(record.get("run_id")),
            _text(record.get("archive_path")),
        ),
    )


def build_extraction_adequacy_corpus_record(
    run_dir: Path | str,
    *,
    archive_root: Path | str | None = None,
) -> dict[str, Any]:
    """Build a compact extraction/provenance survey record for one run."""

    run_path = Path(run_dir)
    root = Path(archive_root).expanduser() if archive_root is not None else None
    case_id = run_path.parent.name
    run_id = run_path.name
    errors: list[str] = []

    report_path = run_path / EXTRACTION_ADEQUACY_REPORT_FILENAME
    existing_report = _read_json_object(
        report_path,
        errors,
        EXTRACTION_ADEQUACY_REPORT_FILENAME,
    )
    report_available = bool(existing_report)
    report_built_in_memory = False
    report = existing_report
    if not report and _can_build_report(run_path):
        try:
            report = build_extraction_adequacy_report(
                run_path,
                run_id=run_id,
                case_id=case_id,
            )
            report_built_in_memory = True
        except Exception as exc:  # noqa: BLE001 - corpus export must not crash
            errors.append(f"extraction adequacy report build failed:{type(exc).__name__}")
            report = {}

    has_recognized_artifact = _has_recognized_artifact(run_path)
    if not has_recognized_artifact:
        errors.append("no recognized Lolla run artifacts found")

    extraction = _read_json_object(run_path / "extraction.json", errors, "extraction.json")
    _read_json_object(run_path / "result.json", errors, "result.json")
    agent_result = _read_json_object(run_path / "agent_result.json", errors, "agent_result.json")
    evaluation = _read_json_object(run_path / "evaluation.json", errors, "evaluation.json")

    capture_summary = _mapping(report.get("capture_summary"))
    field_summary = _mapping(report.get("extraction_field_summary"))
    context_summary = _mapping(report.get("conversation_context_summary"))
    ir_summary = _mapping(report.get("conversation_ir_provenance_summary"))
    gap_summary = _mapping(report.get("provenance_gap_findings"))
    opportunities = _specialist_opportunities(
        _mapping(report.get("specialist_extractor_opportunities"))
    )
    adequacy_status = _text(report.get("adequacy_status")) or "unknown"
    record_status = "valid" if report and has_recognized_artifact and not errors else "invalid"

    return {
        "schema_version": EXTRACTION_ADEQUACY_CORPUS_RECORD_SCHEMA_VERSION,
        "case_id": case_id,
        "run_id": run_id,
        "archive_path": str(run_path),
        "archive_relpath": _relative_or_absolute(run_path, root),
        "record_status": record_status,
        "record_errors": sorted(set(errors)),
        "report_available": report_available,
        "report_built_in_memory": report_built_in_memory,
        "adequacy_status": adequacy_status,
        "capture_adequacy_status": _text(capture_summary.get("capture_adequacy_status"))
        or "unknown",
        "capture_strategy": _text(capture_summary.get("capture_strategy")) or "unknown",
        "declared_turn_count": _nullable_int(capture_summary.get("declared_turn_count")),
        "captured_turn_count": _nullable_int(capture_summary.get("captured_turn_count")),
        "omitted_turn_count": _safe_int(capture_summary.get("omitted_turn_count")),
        "invalid_turn_ref_count": _safe_int(gap_summary.get("invalid_turn_ref_count")),
        "missing_turn_ref_count": _safe_int(gap_summary.get("missing_turn_ref_count")),
        "speaker_mismatch_count": _safe_int(gap_summary.get("speaker_mismatch_count")),
        "quote_fabrication_count": _safe_int(gap_summary.get("quote_fabrication_count")),
        "conversation_context_available": bool(context_summary.get("available")),
        "conversation_ir_available": bool(ir_summary.get("available")),
        "conversation_ir_provenance_counts": _provenance_counts(ir_summary),
        "fields_present_but_not_span_grounded": _strings(
            gap_summary.get("fields_present_but_not_span_grounded")
        ),
        "fields_only_turn_ref_grounded": _strings(
            gap_summary.get("fields_only_turn_ref_grounded")
        ),
        "fields_with_no_source_grounding": _strings(
            gap_summary.get("fields_with_no_source_grounding")
        ),
        "specialist_extractor_opportunities": opportunities,
        "evaluation_overall": _text(evaluation.get("overall")) or "unavailable",
        "agent_result_status": _text(agent_result.get("status")) or "unavailable",
        "caller_action": _text(agent_result.get("caller_action")) or "unavailable",
        "report_field_counts": {
            "live_constraints": _safe_int(field_summary.get("live_constraints_count")),
            "dropped_threads": _safe_int(field_summary.get("dropped_threads_count")),
            "reasoning_passages": _safe_int(field_summary.get("reasoning_passages_count")),
        },
        "recommended_review_bucket": _recommended_review_bucket(
            record_status=record_status,
            adequacy_status=adequacy_status,
            report_available=report_available,
            report_built_in_memory=report_built_in_memory,
        ),
        "scope": _export_scope("extraction_adequacy_corpus"),
    }


def build_extraction_adequacy_corpus_manifest(
    archive_root: Path | str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build an aggregate manifest for an extraction adequacy corpus export."""

    adequacy_statuses: Counter[str] = Counter()
    capture_statuses: Counter[str] = Counter()
    capture_strategies: Counter[str] = Counter()
    review_buckets: Counter[str] = Counter()
    specialist_counts: Counter[str] = Counter()
    valid_record_count = 0
    report_available_count = 0
    report_built_in_memory_count = 0
    context_available_count = 0
    ir_available_count = 0
    invalid_turn_ref_total = 0
    missing_turn_ref_total = 0
    speaker_mismatch_total = 0
    quote_fabrication_total = 0
    omitted_turn_total = 0

    for record in records:
        if _text(record.get("record_status")) == "valid":
            valid_record_count += 1
        if record.get("report_available"):
            report_available_count += 1
        if record.get("report_built_in_memory"):
            report_built_in_memory_count += 1
        if record.get("conversation_context_available"):
            context_available_count += 1
        if record.get("conversation_ir_available"):
            ir_available_count += 1

        adequacy_statuses[_text(record.get("adequacy_status")) or "unknown"] += 1
        capture_statuses[_text(record.get("capture_adequacy_status")) or "unknown"] += 1
        capture_strategies[_text(record.get("capture_strategy")) or "unknown"] += 1
        review_buckets[_text(record.get("recommended_review_bucket")) or "not_reviewable"] += 1

        invalid_turn_ref_total += _safe_int(record.get("invalid_turn_ref_count"))
        missing_turn_ref_total += _safe_int(record.get("missing_turn_ref_count"))
        speaker_mismatch_total += _safe_int(record.get("speaker_mismatch_count"))
        quote_fabrication_total += _safe_int(record.get("quote_fabrication_count"))
        omitted_turn_total += _safe_int(record.get("omitted_turn_count"))

        for key, item in _mapping(record.get("specialist_extractor_opportunities")).items():
            if _mapping(item).get("could_improve_grounding") or _mapping(item).get(
                "could_cover_assistant_recommendations"
            ):
                specialist_counts[_text(key)] += 1

    return {
        "schema_version": EXTRACTION_ADEQUACY_CORPUS_MANIFEST_SCHEMA_VERSION,
        "archive_root": str(Path(archive_root).expanduser()),
        "record_schema_version": EXTRACTION_ADEQUACY_CORPUS_RECORD_SCHEMA_VERSION,
        "record_count": len(records),
        "valid_record_count": valid_record_count,
        "invalid_record_count": len(records) - valid_record_count,
        "adequacy_status_counts": _counter_dict(adequacy_statuses),
        "capture_adequacy_status_counts": _counter_dict(capture_statuses),
        "capture_strategy_counts": _counter_dict(capture_strategies),
        "report_available_count": report_available_count,
        "report_missing_count": len(records) - report_available_count,
        "report_built_in_memory_count": report_built_in_memory_count,
        "invalid_turn_ref_total": invalid_turn_ref_total,
        "missing_turn_ref_total": missing_turn_ref_total,
        "speaker_mismatch_total": speaker_mismatch_total,
        "quote_fabrication_total": quote_fabrication_total,
        "omitted_turn_total": omitted_turn_total,
        "conversation_context_available_count": context_available_count,
        "conversation_ir_available_count": ir_available_count,
        "specialist_opportunity_counts": _counter_dict(specialist_counts),
        "recommended_review_buckets": _counter_dict(review_buckets),
        "scope": _export_scope("extraction_adequacy_corpus_manifest"),
    }


def write_jsonl(records: Iterable[Mapping[str, Any]], path: Path | str) -> None:
    """Write corpus records as deterministic JSONL."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(payload: Mapping[str, Any], path: Path | str) -> None:
    """Write a deterministic JSON document."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _iter_run_dirs(root: Path) -> list[Path]:
    run_dirs: list[Path] = []
    for case_dir in sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name):
        run_dirs.extend(
            sorted(
                (path for path in case_dir.iterdir() if path.is_dir()),
                key=lambda path: path.name,
            )
        )
    return run_dirs


def _read_json_object(path: Path, errors: list[str], artifact_name: str) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        errors.append(f"{artifact_name} is not valid JSON")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"{artifact_name} is not a JSON object")
        return {}
    return payload


def _can_build_report(run_dir: Path) -> bool:
    return (run_dir / "conversation.txt").is_file() or (run_dir / "extraction.json").is_file()


def _has_recognized_artifact(run_dir: Path) -> bool:
    return any((run_dir / filename).is_file() for filename in _RECOGNIZED_ARTIFACTS)


def _provenance_counts(ir_summary: Mapping[str, Any]) -> dict[str, int]:
    counts = _mapping(ir_summary.get("provenance_kinds_count"))
    return {
        "span": _safe_int(counts.get("span")),
        "turn_ref": _safe_int(counts.get("turn_ref")),
        "derivation": _safe_int(counts.get("derivation")),
        "unknown": _safe_int(counts.get("unknown")),
    }


def _specialist_opportunities(payload: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for key in _SPECIALIST_KEYS:
        item = _mapping(payload.get(key))
        summary[key] = {
            "could_improve_grounding": bool(item.get("could_improve_grounding")),
            "could_cover_assistant_recommendations": bool(
                item.get("could_cover_assistant_recommendations")
            ),
            "current_count": _safe_int(
                item.get("current_count") or item.get("current_stance_event_count")
            ),
        }
    return summary


def _recommended_review_bucket(
    *,
    record_status: str,
    adequacy_status: str,
    report_available: bool,
    report_built_in_memory: bool,
) -> str:
    if record_status != "valid":
        return "not_reviewable"
    if adequacy_status == "critical":
        return "critical_extraction_review"
    if adequacy_status == "warn":
        return "warning_extraction_review"
    if report_built_in_memory and not report_available:
        return "legacy_missing_report_review"
    if adequacy_status == "good":
        return "clean_baseline_sample"
    return "warning_extraction_review"


def _export_scope(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "local_only": True,
        "raw_transcript_included": False,
        "raw_memo_included": False,
        "raw_revised_answer_included": False,
        "raw_model_message_content_included": False,
        "provider_reasoning_details_included": False,
        "control_argument_values_included": False,
        "shareable_without_review": False,
        "advice_quality_scored": False,
        "model_calls": 0,
        "llm_judge_used": False,
        "automatic_approval": False,
        "archive_mutation": False,
    }


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {
        key: count
        for key, count in sorted(
            ((key, count) for key, count in counter.items() if key),
            key=lambda item: (-item[1], item[0]),
        )
    }


def _relative_or_absolute(path: Path, root: Path | None) -> str:
    if root is None:
        return str(path)
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [text for item in value if (text := _text(item))]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _nullable_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
