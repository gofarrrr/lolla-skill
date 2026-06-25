"""Archive corpus export helpers for human review and stability analysis.

This module builds a deterministic, local-only index over archived Lolla runs.
It deliberately summarizes custody/readiness metadata instead of copying raw
conversation, memo, revised-answer, or control-action argument values into the
export.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from .control_plane import control_input_summary
from .human_review import HUMAN_REVIEW_SCHEMA_VERSION, blank_human_review_template
from .reasoning_trace_dataset import DEFAULT_ARCHIVE_ROOT


REVIEW_CORPUS_RECORD_SCHEMA_VERSION = "lolla.review_corpus_record.v0"
REVIEW_CORPUS_MANIFEST_SCHEMA_VERSION = "lolla.review_corpus_manifest.v0"

REQUIRED_ARTIFACTS = (
    "conversation.txt",
    "extraction.json",
    "result.json",
    "revised.txt",
    "memo.md",
    "agent_result.json",
    "reasoning_trace.json",
    "run_events.json",
)

OPTIONAL_ARTIFACTS = (
    "evaluation.json",
    "graph_survival_report.json",
    "graph_survival_report.md",
    "control_input.json",
    "control_result.json",
)

ARTIFACT_FILENAMES = REQUIRED_ARTIFACTS + OPTIONAL_ARTIFACTS
RUN_ID_TIMESTAMP_RE = re.compile(r"^(?P<date>\d{8})T(?P<time>\d{6})Z")


def build_review_corpus_records(archive_root: Path | str) -> list[dict[str, Any]]:
    """Build one deterministic, JSON-safe corpus record per archived run."""

    root = Path(archive_root).expanduser()
    if not root.exists():
        return []
    records = [
        build_review_corpus_record(run_dir, archive_root=root)
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


def build_review_corpus_record(
    run_dir: Path | str,
    *,
    archive_root: Path | str | None = None,
) -> dict[str, Any]:
    """Build a compact human-review/stability record for one run directory."""

    run_path = Path(run_dir)
    root = Path(archive_root).expanduser() if archive_root is not None else None
    case_id = run_path.parent.name
    run_id = run_path.name
    errors: list[str] = []

    extraction = _read_json_object(run_path / "extraction.json", errors, "extraction.json")
    result = _read_json_object(run_path / "result.json", errors, "result.json")
    agent_result = _read_json_object(run_path / "agent_result.json", errors, "agent_result.json")
    reasoning_trace = _read_json_object(
        run_path / "reasoning_trace.json",
        errors,
        "reasoning_trace.json",
    )
    evaluation = _read_json_object(run_path / "evaluation.json", errors, "evaluation.json")
    run_events = _read_json_object(run_path / "run_events.json", errors, "run_events.json")
    control_result = _read_json_object(
        run_path / "control_result.json",
        errors,
        "control_result.json",
    )
    control_input = _read_json_object(
        run_path / "control_input.json",
        errors,
        "control_input.json",
    )

    artifacts = _artifact_availability(run_path, reasoning_trace)
    capture_adequacy = _capture_adequacy(extraction=extraction, result=result, reasoning_trace=reasoning_trace)
    run_health = _run_health(result=result, agent_result=agent_result, reasoning_trace=reasoning_trace)
    provider_boundary_health = _provider_boundary_health(
        run_health=run_health,
        agent_result=agent_result,
    )
    trace_model_calls = [_mapping(item) for item in _list(reasoning_trace.get("model_calls"))]

    if not any((result, agent_result, reasoning_trace, evaluation)):
        errors.append("no recognized Lolla run artifacts found")

    return {
        "schema_version": REVIEW_CORPUS_RECORD_SCHEMA_VERSION,
        "case_id": case_id,
        "run_id": run_id,
        "archive_path": str(run_path),
        "archive_relpath": _relative_or_absolute(run_path, root),
        "valid_archive": not errors or any((result, agent_result, reasoning_trace, evaluation)),
        "archive_errors": sorted(set(errors)),
        "timestamps": _timestamps(
            run_id=run_id,
            agent_result=agent_result,
            reasoning_trace=reasoning_trace,
            evaluation=evaluation,
            run_events=run_events,
        ),
        "schema_versions": _schema_versions(
            extraction=extraction,
            agent_result=agent_result,
            reasoning_trace=reasoning_trace,
            evaluation=evaluation,
            capture_adequacy=capture_adequacy,
            control_input=control_input,
            control_result=control_result,
        ),
        "agent_result": {
            "available": bool(agent_result),
            "status": _text(agent_result.get("status")) or "unknown",
            "status_reason": _text(agent_result.get("status_reason")),
            "caller_action": _text(agent_result.get("caller_action")) or "unknown",
        },
        "risk_mode": _risk_mode(result=result, agent_result=agent_result, reasoning_trace=reasoning_trace),
        "run_health": {
            "overall": _text(run_health.get("overall")) or "unknown",
            "major_causes": _major_causes(run_health),
            "issue_details": _issue_details(run_health),
            "product_output_health": _text(run_health.get("product_output_health")) or "unknown",
            "live_output_health": _text(run_health.get("live_output_health")) or "unknown",
        },
        "capture_adequacy": {
            "available": bool(capture_adequacy),
            "status": _text(capture_adequacy.get("status")) or "unknown",
            "capture_strategy": _text(capture_adequacy.get("capture_strategy")) or "unknown",
            "omitted_turn_count": _safe_int(capture_adequacy.get("omitted_turn_count")),
            "captured_windows": _list(capture_adequacy.get("captured_windows")),
            "omitted_windows": _list(capture_adequacy.get("omitted_windows")),
            "risk_flags": _strings(capture_adequacy.get("risk_flags")),
        },
        "provider_boundary_health": {
            "available": bool(provider_boundary_health),
            "status": _text(provider_boundary_health.get("status")) or "unknown",
        },
        "evaluation": {
            "available": bool(evaluation),
            "overall": _text(evaluation.get("overall")) or "unavailable",
            "caller_readiness": _text(evaluation.get("caller_readiness")) or "unavailable",
        },
        "hygiene": {
            "product_output_health": _text(run_health.get("product_output_health")) or _text(agent_result.get("product_output_health")) or "unknown",
            "live_output_health": _text(run_health.get("live_output_health")) or _text(agent_result.get("live_output_health")) or "unknown",
        },
        "usage": _usage_summary(
            result=result,
            agent_result=agent_result,
            reasoning_trace=reasoning_trace,
        ),
        "model_provider_summary": _model_provider_summary(
            model_calls=trace_model_calls,
            result=result,
        ),
        "control_plane": _control_plane_summary(
            run_path=run_path,
            agent_result=agent_result,
            control_result=control_result,
        ),
        "artifacts": artifacts,
        "artifact_counts": _artifact_counts(artifacts),
        "human_review": blank_human_review_template(),
        "scope": _export_scope("review_corpus"),
    }


def build_review_corpus_manifest(
    archive_root: Path | str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build an aggregate manifest for a review corpus export."""

    statuses: Counter[str] = Counter()
    caller_actions: Counter[str] = Counter()
    risk_modes: Counter[str] = Counter()
    capture_statuses: Counter[str] = Counter()
    evaluation_overalls: Counter[str] = Counter()
    readiness: Counter[str] = Counter()
    provider_statuses: Counter[str] = Counter()
    invalid_count = 0
    control_input_count = 0
    control_result_count = 0
    total_cost = 0.0
    cost_known_count = 0

    for record in records:
        statuses[_text(_mapping(record.get("run_health")).get("overall")) or "unknown"] += 1
        caller_actions[_text(_mapping(record.get("agent_result")).get("caller_action")) or "unknown"] += 1
        risk_modes[_text(record.get("risk_mode")) or "unknown"] += 1
        capture_statuses[_text(_mapping(record.get("capture_adequacy")).get("status")) or "unknown"] += 1
        evaluation_overalls[_text(_mapping(record.get("evaluation")).get("overall")) or "unavailable"] += 1
        readiness[_text(_mapping(record.get("evaluation")).get("caller_readiness")) or "unavailable"] += 1
        provider_statuses[_text(_mapping(record.get("provider_boundary_health")).get("status")) or "unknown"] += 1
        if not record.get("valid_archive"):
            invalid_count += 1
        control = _mapping(record.get("control_plane"))
        if control.get("control_input_available"):
            control_input_count += 1
        if control.get("control_result_available"):
            control_result_count += 1
        cost = _mapping(record.get("usage")).get("estimated_total_cost_usd")
        if isinstance(cost, (int, float)):
            total_cost += float(cost)
            cost_known_count += 1

    return {
        "schema_version": REVIEW_CORPUS_MANIFEST_SCHEMA_VERSION,
        "archive_root": str(Path(archive_root).expanduser()),
        "record_schema_version": REVIEW_CORPUS_RECORD_SCHEMA_VERSION,
        "human_review_schema_version": HUMAN_REVIEW_SCHEMA_VERSION,
        "record_count": len(records),
        "valid_record_count": len(records) - invalid_count,
        "invalid_record_count": invalid_count,
        "control_input_record_count": control_input_count,
        "control_result_record_count": control_result_count,
        "cost_known_record_count": cost_known_count,
        "estimated_total_cost_usd": round(total_cost, 6) if cost_known_count else None,
        "run_health_status_counts": _counter_dict(statuses),
        "caller_action_counts": _counter_dict(caller_actions),
        "risk_mode_counts": _counter_dict(risk_modes),
        "capture_adequacy_status_counts": _counter_dict(capture_statuses),
        "evaluation_overall_counts": _counter_dict(evaluation_overalls),
        "caller_readiness_counts": _counter_dict(readiness),
        "provider_boundary_health_status_counts": _counter_dict(provider_statuses),
        "scope": _export_scope("review_corpus_manifest"),
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
    }


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


def _artifact_availability(run_dir: Path, reasoning_trace: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    trace_artifacts = {
        _text(_mapping(item).get("path")): _mapping(item)
        for item in _list(reasoning_trace.get("artifacts"))
        if _text(_mapping(item).get("path"))
    }
    trace_missing = {
        _text(_mapping(item).get("path"))
        for item in _list(reasoning_trace.get("missing_artifacts"))
        if _text(_mapping(item).get("path"))
    }
    artifacts: dict[str, dict[str, Any]] = {}
    for filename in ARTIFACT_FILENAMES:
        trace_record = trace_artifacts.get(filename, {})
        available = (run_dir / filename).is_file()
        artifacts[filename] = {
            "available": available,
            "path": filename,
            "role": _text(trace_record.get("role")),
            "sha256": _text(trace_record.get("sha256")),
            "bytes": trace_record.get("bytes") if isinstance(trace_record.get("bytes"), int) else None,
            "content_type": _text(trace_record.get("content_type")),
            "recorded_missing_in_trace": filename in trace_missing,
        }
    return artifacts


def _artifact_counts(artifacts: Mapping[str, Mapping[str, Any]]) -> dict[str, int]:
    available = sum(1 for item in artifacts.values() if item.get("available"))
    required_missing = sum(
        1
        for filename in REQUIRED_ARTIFACTS
        if not _mapping(artifacts.get(filename)).get("available")
    )
    optional_missing = sum(
        1
        for filename in OPTIONAL_ARTIFACTS
        if not _mapping(artifacts.get(filename)).get("available")
    )
    return {
        "known_artifact_count": len(ARTIFACT_FILENAMES),
        "available_artifact_count": available,
        "required_missing_count": required_missing,
        "optional_missing_count": optional_missing,
    }


def _timestamps(
    *,
    run_id: str,
    agent_result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    run_events: Mapping[str, Any],
) -> dict[str, str | None]:
    return {
        "run_id_timestamp": _timestamp_from_run_id(run_id),
        "archived_at": _archive_completed_timestamp(run_events),
        "agent_result_created_at": _text(agent_result.get("created_at")) or None,
        "reasoning_trace_created_at": _text(reasoning_trace.get("created_at")) or None,
        "evaluation_created_at": _text(evaluation.get("created_at")) or None,
    }


def _timestamp_from_run_id(run_id: str) -> str | None:
    match = RUN_ID_TIMESTAMP_RE.match(run_id)
    if not match:
        return None
    date = match.group("date")
    time = match.group("time")
    return f"{date[:4]}-{date[4:6]}-{date[6:]}T{time[:2]}:{time[2:4]}:{time[4:]}Z"


def _archive_completed_timestamp(run_events: Mapping[str, Any]) -> str | None:
    for event in _list(run_events.get("events")):
        item = _mapping(event)
        if _text(item.get("event_type")) != "archive_completed":
            continue
        return (
            _text(item.get("created_at"))
            or _text(item.get("timestamp"))
            or _text(item.get("time"))
            or None
        )
    return None


def _schema_versions(
    *,
    extraction: Mapping[str, Any],
    agent_result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    capture_adequacy: Mapping[str, Any],
    control_input: Mapping[str, Any],
    control_result: Mapping[str, Any],
) -> dict[str, str | None]:
    return {
        "extraction": _text(extraction.get("schema_version")) or None,
        "agent_result": _text(agent_result.get("schema_version")) or None,
        "reasoning_trace": _text(reasoning_trace.get("schema_version")) or None,
        "evaluation": _text(evaluation.get("schema_version")) or None,
        "capture_adequacy": _text(capture_adequacy.get("schema_version")) or None,
        "control_input": _text(control_input.get("schema_version")) or None,
        "control_result": _text(control_result.get("schema_version")) or None,
    }


def _capture_adequacy(
    *,
    extraction: Mapping[str, Any],
    result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
) -> Mapping[str, Any]:
    direct = _mapping(extraction.get("capture_adequacy"))
    if direct:
        return direct
    health_capture = _mapping(_mapping(result.get("run_health")).get("capture_adequacy"))
    if health_capture:
        return health_capture
    return _mapping(_mapping(reasoning_trace.get("capture")).get("capture_adequacy"))


def _run_health(
    *,
    result: Mapping[str, Any],
    agent_result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
) -> Mapping[str, Any]:
    direct = _mapping(result.get("run_health"))
    if direct:
        return direct
    trace_health = _mapping(_mapping(reasoning_trace.get("process")).get("run_health"))
    if trace_health:
        return trace_health
    if agent_result:
        return {
            "overall": agent_result.get("run_health_overall"),
            "product_output_health": agent_result.get("product_output_health"),
            "live_output_health": agent_result.get("live_output_health"),
        }
    return {}


def _provider_boundary_health(
    *,
    run_health: Mapping[str, Any],
    agent_result: Mapping[str, Any],
) -> Mapping[str, Any]:
    return _mapping(run_health.get("provider_boundary_health")) or _mapping(
        agent_result.get("provider_boundary_health")
    )


def _major_causes(run_health: Mapping[str, Any]) -> list[str]:
    causes: list[str] = []
    for value in _strings(run_health.get("partial_health_causes")):
        _append_unique(causes, value)
    for value in _strings(run_health.get("issues")):
        _append_unique(causes, value)
    for detail in _list(run_health.get("issue_details")):
        code = _text(_mapping(detail).get("code"))
        if code:
            _append_unique(causes, code)
    return causes


def _issue_details(run_health: Mapping[str, Any]) -> list[dict[str, str]]:
    details: list[dict[str, str]] = []
    for detail in _list(run_health.get("issue_details")):
        item = _mapping(detail)
        compact = {
            "code": _text(item.get("code")),
            "severity": _text(item.get("severity")),
            "axis": _text(item.get("axis")),
        }
        if any(compact.values()):
            details.append(compact)
    return sorted(details, key=lambda item: (item.get("severity") or "", item.get("code") or ""))


def _risk_mode(
    *,
    result: Mapping[str, Any],
    agent_result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
) -> str:
    return (
        _text(agent_result.get("risk_mode"))
        or _text(result.get("risk_mode"))
        or _text(_mapping(reasoning_trace.get("process")).get("risk_mode"))
        or "standard"
    )


def _usage_summary(
    *,
    result: Mapping[str, Any],
    agent_result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
) -> dict[str, Any]:
    usage = (
        _mapping(agent_result.get("usage"))
        or _mapping(result.get("usage_summary"))
        or _mapping(_mapping(reasoning_trace.get("process")).get("usage"))
    )
    return {
        "estimated_total_cost_usd": _number_or_none(usage.get("estimated_total_cost_usd")),
        "cost_estimate_state": _text(usage.get("cost_estimate_state")) or None,
        "pricing_table_version": _text(usage.get("pricing_table_version")) or None,
        "total_vendor_call_count": _safe_int_or_none(usage.get("total_vendor_call_count")),
        "vendor_calls": _mapping(usage.get("vendor_calls")) or None,
    }


def _model_provider_summary(
    *,
    model_calls: Sequence[Mapping[str, Any]],
    result: Mapping[str, Any],
) -> dict[str, Any]:
    providers: list[str] = []
    requested_models: list[str] = []
    served_models: list[str] = []
    stages: list[str] = []
    call_count = 0
    for call in model_calls:
        call_count += _safe_int(call.get("call_count"), 1)
        _append_unique(providers, _text(call.get("provider_name")) or _text(call.get("provider")))
        _append_unique(requested_models, _text(call.get("requested_model")))
        _append_unique(served_models, _text(call.get("served_model")) or _text(call.get("model")))
        _append_unique(stages, _text(call.get("stage")))

    usage = _mapping(result.get("usage_summary"))
    vendors = _mapping(usage.get("vendors"))
    if vendors:
        for vendor_name, vendor in vendors.items():
            vendor_map = _mapping(vendor)
            _append_unique(providers, _text(vendor_map.get("provider")) or _text(vendor_name))
            for model in _strings(vendor_map.get("requested_models_seen")):
                _append_unique(requested_models, model)
            for model in _strings(vendor_map.get("models_seen")):
                _append_unique(served_models, model)
            if not call_count:
                call_count += _safe_int(vendor_map.get("calls"))

    return {
        "model_call_count": call_count,
        "providers": providers,
        "requested_models": requested_models,
        "served_models": served_models,
        "stages": stages,
    }


def _control_plane_summary(
    *,
    run_path: Path,
    agent_result: Mapping[str, Any],
    control_result: Mapping[str, Any],
) -> dict[str, Any]:
    control_context = _mapping(agent_result.get("control_context")) or control_input_summary(run_path)
    return {
        "control_input_available": (run_path / "control_input.json").is_file(),
        "control_result_available": (run_path / "control_result.json").is_file(),
        "control_context": dict(control_context),
        "control_result": {
            "schema_version": _text(control_result.get("schema_version")) or None,
            "control_mode": _text(control_result.get("control_mode")) or None,
            "approval_outcome": _text(control_result.get("approval_outcome")) or None,
            "lolla_approves_actions": False,
        },
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


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


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


def _safe_int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _number_or_none(value: Any) -> int | float | None:
    return value if isinstance(value, (int, float)) else None


def _append_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)
