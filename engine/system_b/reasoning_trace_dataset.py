"""Local dataset helpers for archived Lolla reasoning traces.

The dataset layer deliberately reads ``reasoning_trace.json`` manifests rather
than raw conversations. That keeps corpus analytics focused on local custody,
route IDs, adequacy, and outcomes while preserving drill-back to archived
artifacts when a human reviewer needs context.
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


DATASET_RECORD_SCHEMA_VERSION = "lolla.reasoning_trace_dataset_record.v0.1"
DATASET_SUMMARY_SCHEMA_VERSION = "lolla.reasoning_trace_dataset_summary.v0.1"
REASONING_TRACE_FILENAME = "reasoning_trace.json"
DEFAULT_ARCHIVE_ROOT = Path.home() / ".local" / "share" / "lolla" / "runs"


def find_reasoning_trace_paths(archive_root: Path | str) -> list[Path]:
    """Return all archived ``reasoning_trace.json`` files under ``archive_root``."""
    root = Path(archive_root).expanduser()
    if not root.exists():
        return []
    return sorted(path for path in root.rglob(REASONING_TRACE_FILENAME) if path.is_file())


def build_dataset_records(archive_root: Path | str) -> list[dict[str, Any]]:
    """Build flattened JSON-safe records for every trace under ``archive_root``."""
    root = Path(archive_root).expanduser()
    records: list[dict[str, Any]] = []
    for trace_path in find_reasoning_trace_paths(root):
        trace = load_reasoning_trace(trace_path)
        records.append(build_dataset_record(trace_path, trace, archive_root=root))
    return records


def load_reasoning_trace(path: Path | str) -> dict[str, Any]:
    """Load one reasoning trace manifest."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_dataset_record(
    trace_path: Path | str,
    trace: Mapping[str, Any],
    *,
    archive_root: Path | str | None = None,
) -> dict[str, Any]:
    """Flatten one reasoning trace into a corpus-analysis record."""
    path = Path(trace_path)
    root = Path(archive_root).expanduser() if archive_root is not None else None
    source_trace_path = _relative_or_absolute(path, root)
    case = _mapping(trace.get("case"))
    capture = _mapping(trace.get("capture"))
    process = _mapping(trace.get("process"))
    audit = _mapping(process.get("audit_summary"))
    run_health = _mapping(process.get("run_health"))
    adequacy = _mapping(trace.get("trace_adequacy"))
    usage = _mapping(process.get("usage"))
    lenses = [_mapping(item) for item in _list(trace.get("reasoning_lenses"))]
    selected_lens_ids = _sorted_unique(
        _text(item.get("lens_id")) for item in lenses if item.get("selected")
    )
    rejected_lens_ids = _sorted_unique(
        _text(item.get("lens_id")) for item in lenses if item.get("rejection_reasons")
    )
    surfaced_lens_ids = _sorted_unique(
        _text(item.get("lens_id")) for item in lenses if item.get("surfaced")
    )

    return {
        "schema_version": DATASET_RECORD_SCHEMA_VERSION,
        "source_trace_path": source_trace_path,
        "trace_id": _text(trace.get("trace_id")),
        "created_at": _text(trace.get("created_at")),
        "case_id": _text(case.get("case_id")),
        "run_id": _text(case.get("run_id")),
        "decision_situation": _text(case.get("decision_situation")),
        "capture_health": _text(capture.get("capture_health")) or "unknown",
        "run_health_overall": _text(run_health.get("overall")) or "unknown",
        "trace_adequacy_status": _text(adequacy.get("status")) or "unknown",
        "future_review_ready": bool(adequacy.get("future_review_ready")),
        "error_analysis_ready": bool(adequacy.get("error_analysis_ready")),
        "missing_context_count": len(_list(adequacy.get("missing_context"))),
        "artifact_count": len(_list(trace.get("artifacts"))),
        "missing_artifact_count": len(_list(trace.get("missing_artifacts"))),
        "model_call_count": len(_list(trace.get("model_calls"))),
        "candidate_commitment_count": len(_list(trace.get("candidate_commitments"))),
        "decision_packet_count": len(_list(trace.get("decision_packets"))),
        "outcome_review_count": len(_list(trace.get("outcome_reviews"))),
        "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
        "reasoning_lens_count": len(lenses),
        "reasoning_lens_ids": _sorted_unique(_text(item.get("lens_id")) for item in lenses),
        "selected_reasoning_lens_count": len(selected_lens_ids),
        "selected_reasoning_lens_ids": selected_lens_ids,
        "surfaced_reasoning_lens_ids": surfaced_lens_ids,
        "rejected_reasoning_lens_ids": rejected_lens_ids,
        "triggered_tendency_ids": _sorted_unique(_text(item) for item in _list(audit.get("triggered_tendency_ids"))),
        "detected_tendency_ids": _sorted_unique(_text(item) for item in _list(audit.get("detected_tendency_ids"))),
        "reasoning_lenses": [dict(item) for item in lenses],
    }


def summarize_dataset_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate a local reasoning-trace dataset."""
    adequacy_statuses: Counter[str] = Counter()
    run_health_statuses: Counter[str] = Counter()
    capture_health_statuses: Counter[str] = Counter()
    lens_mentions: Counter[str] = Counter()
    selected_lenses: Counter[str] = Counter()
    surfaced_lenses: Counter[str] = Counter()
    rejected_lenses: Counter[str] = Counter()
    triggered_tendencies: Counter[str] = Counter()
    detected_tendencies: Counter[str] = Counter()

    review_ready = 0
    error_analysis_ready = 0
    traces_with_lenses = 0
    traces_with_model_calls = 0
    total_model_calls = 0
    total_cost = 0.0
    cost_known_count = 0

    for record in records:
        adequacy_statuses[_text(record.get("trace_adequacy_status")) or "unknown"] += 1
        run_health_statuses[_text(record.get("run_health_overall")) or "unknown"] += 1
        capture_health_statuses[_text(record.get("capture_health")) or "unknown"] += 1
        if record.get("future_review_ready"):
            review_ready += 1
        if record.get("error_analysis_ready"):
            error_analysis_ready += 1
        lens_ids = _list(record.get("reasoning_lens_ids"))
        if lens_ids:
            traces_with_lenses += 1
        if _safe_int(record.get("model_call_count")):
            traces_with_model_calls += 1
        total_model_calls += _safe_int(record.get("model_call_count"))
        cost = record.get("estimated_total_cost_usd")
        if isinstance(cost, (int, float)):
            total_cost += float(cost)
            cost_known_count += 1
        for lens_id in lens_ids:
            lens_mentions[_text(lens_id)] += 1
        for lens_id in _list(record.get("selected_reasoning_lens_ids")):
            selected_lenses[_text(lens_id)] += 1
        for lens_id in _list(record.get("surfaced_reasoning_lens_ids")):
            surfaced_lenses[_text(lens_id)] += 1
        for lens_id in _list(record.get("rejected_reasoning_lens_ids")):
            rejected_lenses[_text(lens_id)] += 1
        for tendency_id in _list(record.get("triggered_tendency_ids")):
            triggered_tendencies[_text(tendency_id)] += 1
        for tendency_id in _list(record.get("detected_tendency_ids")):
            detected_tendencies[_text(tendency_id)] += 1

    trace_count = len(records)
    return {
        "schema_version": DATASET_SUMMARY_SCHEMA_VERSION,
        "trace_count": trace_count,
        "future_review_ready_count": review_ready,
        "error_analysis_ready_count": error_analysis_ready,
        "traces_with_reasoning_lenses_count": traces_with_lenses,
        "traces_with_model_calls_count": traces_with_model_calls,
        "total_model_call_count": total_model_calls,
        "estimated_total_cost_usd": round(total_cost, 6) if cost_known_count else None,
        "cost_known_trace_count": cost_known_count,
        "trace_adequacy_status_counts": _counter_dict(adequacy_statuses),
        "run_health_status_counts": _counter_dict(run_health_statuses),
        "capture_health_status_counts": _counter_dict(capture_health_statuses),
        "reasoning_lens_trace_counts": _counter_dict(lens_mentions),
        "selected_reasoning_lens_trace_counts": _counter_dict(selected_lenses),
        "surfaced_reasoning_lens_trace_counts": _counter_dict(surfaced_lenses),
        "rejected_reasoning_lens_trace_counts": _counter_dict(rejected_lenses),
        "triggered_tendency_trace_counts": _counter_dict(triggered_tendencies),
        "detected_tendency_trace_counts": _counter_dict(detected_tendencies),
    }


def write_jsonl(records: Iterable[Mapping[str, Any]], path: Path | str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(payload: Mapping[str, Any], path: Path | str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


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


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})
