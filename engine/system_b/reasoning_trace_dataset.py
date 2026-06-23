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
    graph_survival = _mapping(process.get("graph_survival"))
    adequacy = _mapping(trace.get("trace_adequacy"))
    usage = _mapping(process.get("usage"))
    user_usefulness = _mapping(trace.get("user_usefulness_review"))
    outcome_state = _mapping(trace.get("outcome_review_state"))
    lenses = [_mapping(item) for item in _list(trace.get("reasoning_lenses"))]
    model_calls = [_mapping(item) for item in _list(trace.get("model_calls"))]
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
        "model_call_count": _model_call_count(model_calls),
        "model_call_record_count": len(model_calls),
        "candidate_commitment_count": len(_list(trace.get("candidate_commitments"))),
        "decision_packet_count": len(_list(trace.get("decision_packets"))),
        "outcome_review_count": len(_list(trace.get("outcome_reviews"))),
        "graph_survival_status": _text(graph_survival.get("status")) or "unknown",
        "graph_lane_candidate_count": _safe_int(graph_survival.get("lane_candidate_count")),
        "graph_raw_lane_signal_count": _safe_int(graph_survival.get("raw_lane_signal_count")),
        "graph_embedding_hit_count": _safe_int(graph_survival.get("embedding_hit_count")),
        "graph_selected_card_count": _safe_int(graph_survival.get("selected_card_count")),
        "graph_answer_delta_model_count": _safe_int(
            graph_survival.get("answer_delta_model_count")
        ),
        "graph_private_guardrail_model_count": _safe_int(
            graph_survival.get("private_guardrail_model_count")
        ),
        "graph_confirming_support_model_count": _safe_int(
            graph_survival.get("confirming_support_model_count")
        ),
        "graph_suppressed_signal_count": _safe_int(graph_survival.get("suppressed_signal_count")),
        "graph_suppressed_model_count": _safe_int(graph_survival.get("suppressed_model_count")),
        "graph_budget_suppressed_signal_count": _safe_int(
            graph_survival.get("budget_suppressed_signal_count")
        ),
        "graph_budget_suppressed_model_count": _safe_int(
            graph_survival.get("budget_suppressed_model_count")
        ),
        "graph_unadjudicated_candidate_count": _safe_int(
            graph_survival.get("unadjudicated_candidate_count")
        ),
        "top_budget_suppressed_lens_ids": _sorted_unique(
            _text(item.get("model_id"))
            for item in _list(graph_survival.get("top_budget_suppressed_lenses"))
            if _mapping(item)
        ),
        "user_usefulness_status": _text(user_usefulness.get("status")) or "not_collected",
        "user_usefulness_rating": user_usefulness.get("rating"),
        "user_helped_change_view": user_usefulness.get("helped_change_view"),
        "user_would_reuse": user_usefulness.get("would_reuse"),
        "outcome_review_status": _text(outcome_state.get("status")) or "not_started",
        "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
        "surface_divergence_status": _text(
            _mapping(trace.get("surface_divergence")).get("status")
        ) or "unknown",
        "revised_artifact_found_in_live_transcript": _mapping(
            trace.get("surface_divergence")
        ).get("revised_artifact_found_in_live_transcript"),
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
    traces_with_candidate_commitments = 0
    total_candidate_commitments = 0
    total_decision_packets = 0
    total_outcome_reviews = 0
    traces_with_graph_survival = 0
    total_graph_lane_candidates = 0
    total_graph_raw_lane_signals = 0
    total_graph_embedding_hits = 0
    total_graph_selected_cards = 0
    total_graph_answer_delta_models = 0
    total_graph_private_guardrail_models = 0
    total_graph_confirming_support_models = 0
    total_graph_suppressed_signals = 0
    total_graph_suppressed_models = 0
    total_graph_budget_suppressed_signals = 0
    total_graph_budget_suppressed_models = 0
    total_graph_unadjudicated_candidates = 0
    total_cost = 0.0
    cost_known_count = 0
    usefulness_statuses: Counter[str] = Counter()
    usefulness_rating_count = 0
    usefulness_rating_total = 0.0
    outcome_review_statuses: Counter[str] = Counter()

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
        candidate_commitments = _safe_int(record.get("candidate_commitment_count"))
        decision_packets = _safe_int(record.get("decision_packet_count"))
        outcome_reviews = _safe_int(record.get("outcome_review_count"))
        if candidate_commitments:
            traces_with_candidate_commitments += 1
        total_candidate_commitments += candidate_commitments
        total_decision_packets += decision_packets
        total_outcome_reviews += outcome_reviews
        if _text(record.get("graph_survival_status")) == "ready":
            traces_with_graph_survival += 1
        total_graph_lane_candidates += _safe_int(record.get("graph_lane_candidate_count"))
        total_graph_raw_lane_signals += _safe_int(record.get("graph_raw_lane_signal_count"))
        total_graph_embedding_hits += _safe_int(record.get("graph_embedding_hit_count"))
        total_graph_selected_cards += _safe_int(record.get("graph_selected_card_count"))
        total_graph_answer_delta_models += _safe_int(record.get("graph_answer_delta_model_count"))
        total_graph_private_guardrail_models += _safe_int(
            record.get("graph_private_guardrail_model_count")
        )
        total_graph_confirming_support_models += _safe_int(
            record.get("graph_confirming_support_model_count")
        )
        total_graph_suppressed_signals += _safe_int(record.get("graph_suppressed_signal_count"))
        total_graph_suppressed_models += _safe_int(record.get("graph_suppressed_model_count"))
        total_graph_budget_suppressed_signals += _safe_int(
            record.get("graph_budget_suppressed_signal_count")
        )
        total_graph_budget_suppressed_models += _safe_int(
            record.get("graph_budget_suppressed_model_count")
        )
        total_graph_unadjudicated_candidates += _safe_int(
            record.get("graph_unadjudicated_candidate_count")
        )
        usefulness_statuses[_text(record.get("user_usefulness_status")) or "not_collected"] += 1
        outcome_review_statuses[_text(record.get("outcome_review_status")) or "not_started"] += 1
        usefulness_rating = record.get("user_usefulness_rating")
        if isinstance(usefulness_rating, (int, float)):
            usefulness_rating_total += float(usefulness_rating)
            usefulness_rating_count += 1
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
        "traces_with_candidate_commitments_count": traces_with_candidate_commitments,
        "candidate_commitment_count": total_candidate_commitments,
        "decision_packet_count": total_decision_packets,
        "outcome_review_count": total_outcome_reviews,
        "traces_with_graph_survival_count": traces_with_graph_survival,
        "graph_lane_candidate_count": total_graph_lane_candidates,
        "graph_raw_lane_signal_count": total_graph_raw_lane_signals,
        "graph_embedding_hit_count": total_graph_embedding_hits,
        "graph_selected_card_count": total_graph_selected_cards,
        "graph_answer_delta_model_count": total_graph_answer_delta_models,
        "graph_private_guardrail_model_count": total_graph_private_guardrail_models,
        "graph_confirming_support_model_count": total_graph_confirming_support_models,
        "graph_suppressed_signal_count": total_graph_suppressed_signals,
        "graph_suppressed_model_count": total_graph_suppressed_models,
        "graph_budget_suppressed_signal_count": total_graph_budget_suppressed_signals,
        "graph_budget_suppressed_model_count": total_graph_budget_suppressed_models,
        "graph_unadjudicated_candidate_count": total_graph_unadjudicated_candidates,
        "user_usefulness_status_counts": _counter_dict(usefulness_statuses),
        "outcome_review_status_counts": _counter_dict(outcome_review_statuses),
        "user_usefulness_rating_average": (
            round(usefulness_rating_total / usefulness_rating_count, 3)
            if usefulness_rating_count
            else None
        ),
        "user_usefulness_rating_count": usefulness_rating_count,
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


def _model_call_count(model_calls: Sequence[Mapping[str, Any]]) -> int:
    total = 0
    for call in model_calls:
        total += max(_safe_int(call.get("call_count")), 1)
    return total


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted({value for value in values if value})
