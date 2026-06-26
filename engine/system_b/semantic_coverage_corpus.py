"""Corpus-level survey helpers for semantic coverage reports.

This module builds a deterministic, local-only JSONL survey over archived Lolla
runs. It prefers an existing ``semantic_coverage_report.json`` when present,
otherwise it builds the PR26 report in memory. It does not mutate archives,
call models, score answer quality, or copy raw transcript/memo/revised text into
the export.
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from .reasoning_trace_dataset import DEFAULT_ARCHIVE_ROOT
from .semantic_coverage_report import (
    SEMANTIC_COVERAGE_REPORT_SCHEMA_VERSION,
    SEMANTIC_ELEMENTS,
    build_semantic_coverage_report,
)


SEMANTIC_COVERAGE_REPORT_FILENAME = "semantic_coverage_report.json"
SEMANTIC_COVERAGE_CORPUS_RECORD_SCHEMA_VERSION = (
    "lolla.semantic_coverage_corpus_record.v0"
)
SEMANTIC_COVERAGE_CORPUS_MANIFEST_SCHEMA_VERSION = (
    "lolla.semantic_coverage_corpus_manifest.v0"
)

RECOMMENDED_REVIEW_BUCKETS = (
    "modern_semantic_baseline",
    "semantic_gap_review",
    "missing_artifacts_review",
    "legacy_semantic_backfill",
    "invalid_or_unreadable",
)

_RECOGNIZED_ARTIFACTS = (
    "conversation.txt",
    "extraction.json",
    "extraction_adequacy_report.json",
    "result.json",
    "revised.txt",
    "memo.md",
    "reasoning_trace.json",
    "evaluation.json",
    "agent_result.json",
    SEMANTIC_COVERAGE_REPORT_FILENAME,
)

_MODERN_CUSTODY_ARTIFACTS = (
    "extraction_adequacy_report.json",
    "reasoning_trace.json",
    "evaluation.json",
    "agent_result.json",
)

_CORE_ARTIFACTS = ("conversation.txt", "extraction.json")


def build_semantic_coverage_corpus_records(
    archive_root: Path | str,
) -> list[dict[str, Any]]:
    """Build one deterministic semantic-coverage corpus record per run."""

    root = Path(archive_root).expanduser()
    if not root.exists():
        return []
    records = [
        build_semantic_coverage_corpus_record(run_dir, archive_root=root)
        for run_dir in _iter_run_dirs(root)
    ]
    return sorted(
        records,
        key=lambda record: (
            _text(record.get("case_id")),
            _text(record.get("run_id")),
            _text(record.get("archive_relpath")),
        ),
    )


def build_semantic_coverage_corpus_record(
    run_dir: Path | str,
    *,
    archive_root: Path | str | None = None,
) -> dict[str, Any]:
    """Build a compact semantic-coverage survey record for one run."""

    run_path = Path(run_dir)
    root = Path(archive_root).expanduser() if archive_root is not None else None
    fallback_case_id = _bounded_text(run_path.parent.name) or "unknown-case"
    fallback_run_id = _bounded_text(run_path.name) or "unknown-run"
    errors: list[str] = []

    report_path = run_path / SEMANTIC_COVERAGE_REPORT_FILENAME
    existing_report = _read_json_object(
        report_path,
        errors,
        SEMANTIC_COVERAGE_REPORT_FILENAME,
    )
    report_available = bool(existing_report)
    report_built_in_memory = False
    report = existing_report
    if not report and _has_recognized_artifact(run_path):
        try:
            report = build_semantic_coverage_report(run_path)
            report_built_in_memory = True
        except Exception:  # noqa: BLE001 - corpus export must not crash
            errors.append("semantic coverage report build failed")
            report = {}

    if report and _text(report.get("schema_version")) != SEMANTIC_COVERAGE_REPORT_SCHEMA_VERSION:
        errors.append("semantic coverage report schema mismatch")

    source_artifacts = _mapping(report.get("source_artifacts"))
    artifact_summary = _artifact_availability_summary(run_path, source_artifacts)
    invalid_json_artifacts = _strings(artifact_summary.get("invalid_json_artifacts"))
    if invalid_json_artifacts:
        errors.append("invalid json artifacts present")
    if not _has_recognized_artifact(run_path):
        errors.append("no recognized Lolla run artifacts found")

    semantic_elements = _mapping(report.get("semantic_elements"))
    semantic_statuses = {
        element: _text(_mapping(semantic_elements.get(element)).get("status")) or "missing"
        for element in SEMANTIC_ELEMENTS
    }
    semantic_groundings = {
        element: _text(_mapping(semantic_elements.get(element)).get("grounding")) or "none"
        for element in SEMANTIC_ELEMENTS
    }
    status_counts = _counter_dict(Counter(semantic_statuses.values()))
    grounding_counts = _counter_dict(Counter(semantic_groundings.values()))
    needs_review_count = _safe_int(
        _mapping(report.get("overall_coverage_summary")).get("needs_review_count")
    )
    if needs_review_count == 0 and semantic_elements:
        needs_review_count = sum(
            1
            for element in semantic_elements.values()
            if bool(_mapping(element).get("needs_review"))
        )

    case_id = _bounded_text(report.get("case_id")) or fallback_case_id
    run_id = _bounded_text(report.get("run_id")) or fallback_run_id
    record_status = "valid"
    if errors or not report or not _has_recognized_artifact(run_path):
        record_status = "invalid"

    return {
        "schema_version": SEMANTIC_COVERAGE_CORPUS_RECORD_SCHEMA_VERSION,
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": _archive_relpath(run_path, root, fallback_case_id, fallback_run_id),
        "valid": record_status == "valid",
        "record_status": record_status,
        "record_errors": sorted(set(errors)),
        "report_available": report_available,
        "report_built_in_memory": report_built_in_memory,
        "source": _export_scope("semantic_coverage_corpus_record"),
        "artifact_availability": artifact_summary,
        "semantic_element_statuses": semantic_statuses,
        "semantic_element_grounding": semantic_groundings,
        "semantic_element_needs_review": {
            element: bool(_mapping(semantic_elements.get(element)).get("needs_review"))
            for element in SEMANTIC_ELEMENTS
        },
        "needs_review_count": needs_review_count,
        "status_counts": status_counts,
        "grounding_counts": grounding_counts,
        "build_error_categories": _strings(
            _mapping(report.get("overall_coverage_summary")).get("build_error_categories")
        ),
        "recommended_review_bucket": _recommended_review_bucket(
            record_status=record_status,
            artifact_summary=artifact_summary,
            semantic_statuses=semantic_statuses,
        ),
    }


def build_semantic_coverage_corpus_manifest(
    archive_root: Path | str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build an aggregate manifest for a semantic coverage corpus export."""

    valid_record_count = 0
    report_available_count = 0
    report_built_in_memory_count = 0
    needs_review_total = 0
    review_buckets: Counter[str] = Counter()
    artifact_missing_counts: Counter[str] = Counter()
    artifact_invalid_json_counts: Counter[str] = Counter()
    status_counts_by_element: dict[str, Counter[str]] = {
        element: Counter() for element in SEMANTIC_ELEMENTS
    }
    grounding_counts_by_element: dict[str, Counter[str]] = {
        element: Counter() for element in SEMANTIC_ELEMENTS
    }
    needs_review_by_element: Counter[str] = Counter()

    for record in records:
        if bool(record.get("valid")) or _text(record.get("record_status")) == "valid":
            valid_record_count += 1
        if record.get("report_available"):
            report_available_count += 1
        if record.get("report_built_in_memory"):
            report_built_in_memory_count += 1
        needs_review_total += _safe_int(record.get("needs_review_count"))
        review_buckets[_text(record.get("recommended_review_bucket")) or "invalid_or_unreadable"] += 1

        artifact_summary = _mapping(record.get("artifact_availability"))
        for artifact in _strings(artifact_summary.get("missing_artifacts")):
            artifact_missing_counts[artifact] += 1
        for artifact in _strings(artifact_summary.get("invalid_json_artifacts")):
            artifact_invalid_json_counts[artifact] += 1

        statuses = _mapping(record.get("semantic_element_statuses"))
        groundings = _mapping(record.get("semantic_element_grounding"))
        needs_review = _mapping(record.get("semantic_element_needs_review"))
        for element in SEMANTIC_ELEMENTS:
            status_counts_by_element[element][_text(statuses.get(element)) or "missing"] += 1
            grounding_counts_by_element[element][_text(groundings.get(element)) or "none"] += 1
            if bool(needs_review.get(element)):
                needs_review_by_element[element] += 1

    return {
        "schema_version": SEMANTIC_COVERAGE_CORPUS_MANIFEST_SCHEMA_VERSION,
        "record_schema_version": SEMANTIC_COVERAGE_CORPUS_RECORD_SCHEMA_VERSION,
        "record_count": len(records),
        "valid_record_count": valid_record_count,
        "invalid_record_count": len(records) - valid_record_count,
        "semantic_element_status_counts": {
            element: _counter_dict(counts)
            for element, counts in status_counts_by_element.items()
        },
        "semantic_element_grounding_counts": {
            element: _counter_dict(counts)
            for element, counts in grounding_counts_by_element.items()
        },
        "semantic_element_needs_review_counts": _counter_dict(needs_review_by_element),
        "needs_review_total": needs_review_total,
        "report_available_count": report_available_count,
        "report_missing_count": len(records) - report_available_count,
        "report_built_in_memory_count": report_built_in_memory_count,
        "artifact_missing_counts": _counter_dict(artifact_missing_counts),
        "artifact_invalid_json_counts": _counter_dict(artifact_invalid_json_counts),
        "recommended_review_bucket_counts": _counter_dict(review_buckets),
        "source": _export_scope("semantic_coverage_corpus_manifest"),
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


def _artifact_availability_summary(
    run_path: Path,
    source_artifacts: Mapping[str, Any],
) -> dict[str, Any]:
    artifact_names = [
        name
        for name in _RECOGNIZED_ARTIFACTS
        if name != SEMANTIC_COVERAGE_REPORT_FILENAME
    ]
    availability: dict[str, dict[str, Any]] = {}
    present: list[str] = []
    missing: list[str] = []
    invalid_json: list[str] = []
    for name in artifact_names:
        artifact = _mapping(source_artifacts.get(name))
        if artifact:
            is_present = bool(artifact.get("present"))
            json_valid = artifact.get("json_valid")
        else:
            path = run_path / name
            is_present = path.is_file()
            json_valid = _json_valid(path) if name.endswith(".json") and is_present else None
        availability[name] = {
            "present": is_present,
            "json_valid": json_valid,
        }
        if is_present:
            present.append(name)
        else:
            missing.append(name)
        if is_present and json_valid is False:
            invalid_json.append(name)
    return {
        "artifacts": availability,
        "present_artifact_count": len(present),
        "missing_artifact_count": len(missing),
        "present_artifacts": present,
        "missing_artifacts": missing,
        "invalid_json_artifacts": invalid_json,
        "core_artifacts_present": all(availability[name]["present"] for name in _CORE_ARTIFACTS),
        "modern_custody_artifacts_present": all(
            availability[name]["present"] for name in _MODERN_CUSTODY_ARTIFACTS
        ),
    }


def _recommended_review_bucket(
    *,
    record_status: str,
    artifact_summary: Mapping[str, Any],
    semantic_statuses: Mapping[str, str],
) -> str:
    if record_status != "valid":
        return "invalid_or_unreadable"
    if not bool(artifact_summary.get("core_artifacts_present")):
        return "missing_artifacts_review"
    if not bool(artifact_summary.get("modern_custody_artifacts_present")):
        return "legacy_semantic_backfill"
    if any(status in {"missing", "partial", "not_measured"} for status in semantic_statuses.values()):
        return "semantic_gap_review"
    return "modern_semantic_baseline"


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


def _has_recognized_artifact(run_dir: Path) -> bool:
    return any((run_dir / filename).is_file() for filename in _RECOGNIZED_ARTIFACTS)


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return True


def _archive_relpath(
    run_path: Path,
    root: Path | None,
    fallback_case_id: str,
    fallback_run_id: str,
) -> str:
    if root is not None:
        try:
            return str(run_path.relative_to(root))
        except ValueError:
            pass
    return f"{fallback_case_id}/{fallback_run_id}"


def _export_scope(artifact: str) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "local_only": True,
        "shareable_without_review": False,
        "raw_transcript_included": False,
        "raw_memo_included": False,
        "raw_revised_answer_included": False,
        "raw_model_message_content_included": False,
        "provider_reasoning_details_included": False,
        "failed_quote_text_included": False,
        "absolute_archive_paths_included": False,
        "control_argument_values_included": False,
        "advice_quality_scored": False,
        "model_calls": 0,
        "llm_judge_used": False,
        "automatic_approval": False,
        "archive_mutation": False,
    }


def _counter_dict(counter: Mapping[str, Any]) -> dict[str, int]:
    return {
        str(key): _safe_int(count)
        for key, count in sorted(
            ((key, count) for key, count in counter.items() if key),
            key=lambda item: (-_safe_int(item[1]), str(item[0])),
        )
    }


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [text for item in value if (text := _text(item))]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bounded_text(value: Any, *, limit: int = 160) -> str:
    text = _text(value)
    if len(text) > limit:
        return text[:limit]
    return text


def _safe_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
