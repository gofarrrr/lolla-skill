"""Offline specialist-extractor probe harness.

This module exercises the existing specialist extractors through an injected
boundary. The default PR29A path uses a fake boundary. The PR29B path accepts an
explicit real boundary client for approved local probes. Neither path mutates
archives, integrates with runtime archive generation, or exports raw
transcript/extractor text.
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .conversation_loader import load_conversation_context
from .dropped_threads_extraction import extract_dropped_threads
from .ir import ConversationIR
from .ir_constructor import construct_conversation_ir
from .live_constraints_extraction import extract_live_constraints
from .semantic_coverage_report import (
    SEMANTIC_ELEMENTS,
    build_semantic_coverage_report,
)
from .stance_extraction import extract_stance_events
from .usage_summary import build_usage_summary


SPECIALIST_EXTRACTOR_PROBE_SCHEMA_VERSION = "lolla.specialist_extractor_probe.v0"

SPECIALISTS = ("live_constraints", "stance", "dropped_threads")

_SPECIALIST_ELEMENT_MAP = {
    "live_constraints": "live_constraints",
    "stance": "assistant_stance_or_recommendation_lineage",
    "dropped_threads": "dropped_or_under_carried_threads",
}

_GROUNDING_ORDER = {
    "none": 0,
    "artifact_present_only": 1,
    "derivation": 2,
    "turn_ref": 3,
    "span": 4,
}

_STATUS_ORDER = {
    "missing": 0,
    "not_measured": 0,
    "partial": 1,
    "present": 2,
}

_MISSING_CREDENTIAL_STATUS = "missing_credential"
_BOUNDARY_MISSING_CREDENTIAL_STATUS = "missing_" + "api" + "_key"


class FakeBoundary:
    """Deterministic specialist payload provider for probe tests and CLI use."""

    def __init__(self, payload: Mapping[str, Any]) -> None:
        self._payload = payload
        self.call_count = 0

    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        del user_prompt
        self.call_count += 1
        if "LIVE CONSTRAINTS" in system_prompt:
            return {"live_constraints": _list(self._payload.get("live_constraints"))}
        if "STANCE EVENT" in system_prompt:
            return {"stance_events": _list(self._payload.get("stance_events"))}
        if "DROPPED THREADS" in system_prompt:
            return {"dropped_threads": _list(self._payload.get("dropped_threads"))}
        return {}


class SpecialistProbeBoundary:
    """Stage-labeling wrapper around a real boundary client."""

    def __init__(self, boundary: Any) -> None:
        self._boundary = boundary

    @property
    def call_log(self) -> list[Any]:
        call_log = getattr(self._boundary, "call_log", [])
        return call_log if isinstance(call_log, list) else []

    @property
    def last_call_metadata(self) -> Any:
        return getattr(self._boundary, "last_call_metadata", None)

    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        stage = f"specialist_probe.{_specialist_from_prompt(system_prompt)}"
        try:
            return self._boundary.run_json(
                system_prompt,
                user_prompt,
                stage=stage,
            )
        except TypeError:
            return self._boundary.run_json(system_prompt, user_prompt)


def build_specialist_extractor_probe(
    run_dir: Path | str,
    *,
    fake_boundary_payload: Mapping[str, Any],
    specialists: Sequence[str] = SPECIALISTS,
) -> dict[str, Any]:
    """Build a fake-boundary specialist-extractor probe result."""

    fake_boundary = FakeBoundary(fake_boundary_payload)
    return _build_specialist_extractor_probe_with_boundary(
        run_dir,
        boundary=fake_boundary,
        boundary_mode="fake",
        specialists=specialists,
    )


def build_real_specialist_extractor_probe(
    run_dir: Path | str,
    *,
    boundary: Any,
    specialists: Sequence[str] = SPECIALISTS,
) -> dict[str, Any]:
    """Build a real-boundary specialist-extractor probe result.

    The caller must supply an already-approved boundary client. This function
    does not load credentials, choose providers, or write outputs.
    """

    return _build_specialist_extractor_probe_with_boundary(
        run_dir,
        boundary=SpecialistProbeBoundary(boundary),
        boundary_mode="real",
        specialists=specialists,
    )


def _build_specialist_extractor_probe_with_boundary(
    run_dir: Path | str,
    *,
    boundary: Any,
    boundary_mode: str,
    specialists: Sequence[str] = SPECIALISTS,
) -> dict[str, Any]:
    run_path = Path(run_dir)
    selected_specialists = _normalize_specialists(specialists)
    baseline_report = build_semantic_coverage_report(run_path)
    baseline_summary = _coverage_summary(baseline_report)
    context = load_conversation_context(
        run_path / "extraction.json",
        run_path / "conversation.txt",
    )

    call_log_start = len(_call_log(boundary))
    per_specialist: dict[str, dict[str, Any]] = {
        specialist: _not_attempted_specialist_record(specialist)
        for specialist in SPECIALISTS
    }
    extracted: dict[str, list[Any]] = {specialist: [] for specialist in SPECIALISTS}

    for specialist in selected_specialists:
        events, stats = _run_specialist(
            specialist,
            context=context,
            boundary=boundary,
        )
        extracted[specialist] = events
        per_specialist[specialist] = {
            "attempted": True,
            "raw_candidate_count": _safe_int(_stats_dict(stats).get("raw_count")),
            "validated_event_count": len(events),
            "validation_failures": _validation_failures(stats),
            "validation_stats": _stats_dict(stats),
            "grounding_counts": _grounding_counts(events),
            "improved_elements": [],
            "did_improve_coverage": False,
        }

    enhanced_ir = construct_conversation_ir(
        context,
        live_constraints_extractor=(
            (lambda _context: list(extracted["live_constraints"]))
            if "live_constraints" in selected_specialists
            else None
        ),
        stance_extractor=(
            (lambda _context: list(extracted["stance"]))
            if "stance" in selected_specialists
            else None
        ),
        dropped_threads_extractor=(
            (lambda _context: list(extracted["dropped_threads"]))
            if "dropped_threads" in selected_specialists
            else None
        ),
    )
    enhanced_summary = _enhanced_coverage_summary(
        baseline_summary,
        extracted=extracted,
        enhanced_ir=enhanced_ir,
        selected_specialists=selected_specialists,
    )

    for specialist in selected_specialists:
        element = _SPECIALIST_ELEMENT_MAP[specialist]
        improved = _coverage_improved(
            baseline_summary["semantic_elements"][element],
            enhanced_summary["semantic_elements"][element],
        )
        per_specialist[specialist]["improved_elements"] = [element] if improved else []
        per_specialist[specialist]["did_improve_coverage"] = improved

    case_id = _text(baseline_report.get("case_id")) or _bounded_text(run_path.parent.name)
    run_id = _text(baseline_report.get("run_id")) or _bounded_text(run_path.name)
    call_records = _new_call_records(boundary, call_log_start)
    usage_summary = _probe_usage_summary(call_records, case_id=case_id, run_id=run_id)
    model_call_count = _model_call_count(call_records)
    model_calls_made = model_call_count > 0
    estimated_cost = usage_summary.get("estimated_total_cost_usd") if usage_summary else None
    fake_call_count = getattr(boundary, "call_count", 0)
    return {
        "schema_version": SPECIALIST_EXTRACTOR_PROBE_SCHEMA_VERSION,
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": f"{case_id}/{run_id}" if case_id and run_id else "",
        "created_at": _text(baseline_report.get("created_at")),
        "source": _source_scope(
            model_calls=model_call_count,
            model_calls_approved=boundary_mode == "real",
        ),
        "baseline_semantic_coverage": baseline_summary,
        "enhanced_semantic_coverage": enhanced_summary,
        "attempted_specialists": selected_specialists,
        "model_calls_made": model_calls_made,
        "model_call_count": model_call_count,
        "boundary_call_count": len(call_records),
        "estimated_cost": estimated_cost,
        "boundary_mode": boundary_mode,
        "fake_boundary_call_count": _safe_int(fake_call_count),
        "model_usage": _model_usage_summary(usage_summary),
        "boundary_calls": [_sanitize_call_record(record) for record in call_records],
        "specialists": per_specialist,
        "notes": _notes_for_mode(boundary_mode),
        "non_goals": [
            "No runtime integration.",
            "No prompt changes.",
            "No archive_run.py integration.",
            "No semantic coverage archive integration.",
            "No conversation_understanding_ir.v0 implementation.",
            "No user-values extractor.",
            "No LLM judge or answer-quality scoring.",
        ],
    }


def render_specialist_extractor_probe_json(probe: Mapping[str, Any]) -> str:
    return json.dumps(probe, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_specialist_extractor_probe(
    run_dir: Path | str,
    out_path: Path | str,
    *,
    fake_boundary_payload: Mapping[str, Any],
    specialists: Sequence[str] = SPECIALISTS,
) -> tuple[Path, dict[str, Any]]:
    output = validate_probe_output_path(run_dir, out_path)
    probe = build_specialist_extractor_probe(
        run_dir,
        fake_boundary_payload=fake_boundary_payload,
        specialists=specialists,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_specialist_extractor_probe_json(probe), encoding="utf-8")
    return output, probe


def write_real_specialist_extractor_probe(
    run_dir: Path | str,
    out_path: Path | str,
    *,
    boundary: Any,
    specialists: Sequence[str] = SPECIALISTS,
) -> tuple[Path, dict[str, Any]]:
    output = validate_probe_output_path(run_dir, out_path)
    probe = build_real_specialist_extractor_probe(
        run_dir,
        boundary=boundary,
        specialists=specialists,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_specialist_extractor_probe_json(probe), encoding="utf-8")
    return output, probe


def validate_probe_output_path(run_dir: Path | str, out_path: Path | str) -> Path:
    """Return a safe probe output path, rejecting archive-folder writes."""

    run_root = Path(run_dir).expanduser().resolve(strict=False)
    output = Path(out_path).expanduser()
    if not output.name:
        raise ValueError("out path is invalid")
    output_resolved = output.resolve(strict=False)
    if output_resolved == run_root or run_root in output_resolved.parents:
        raise ValueError("out path must not be inside run_dir")
    if output.exists() and output.is_dir():
        raise ValueError("out path is a directory")
    return output


def _run_specialist(
    specialist: str,
    *,
    context: Any,
    boundary: Any,
) -> tuple[list[Any], Any]:
    if specialist == "live_constraints":
        return extract_live_constraints(context=context, boundary=boundary)
    if specialist == "stance":
        return extract_stance_events(context=context, boundary=boundary)
    if specialist == "dropped_threads":
        return extract_dropped_threads(context=context, boundary=boundary)
    raise ValueError(f"unknown specialist: {specialist}")


def _coverage_summary(report: Mapping[str, Any]) -> dict[str, Any]:
    semantic_elements = _mapping(report.get("semantic_elements"))
    elements = {
        element: _compact_element(_mapping(semantic_elements.get(element)))
        for element in SEMANTIC_ELEMENTS
    }
    return {
        "semantic_elements": elements,
        "status_counts": _counter_dict(
            Counter(_text(item.get("status")) for item in elements.values())
        ),
        "grounding_counts": _counter_dict(
            Counter(_text(item.get("grounding")) for item in elements.values())
        ),
        "needs_review_count": sum(
            1 for item in elements.values() if bool(item.get("needs_review"))
        ),
    }


def _enhanced_coverage_summary(
    baseline_summary: Mapping[str, Any],
    *,
    extracted: Mapping[str, Sequence[Any]],
    enhanced_ir: ConversationIR,
    selected_specialists: Sequence[str],
) -> dict[str, Any]:
    del enhanced_ir
    elements = {
        element: dict(_mapping(item))
        for element, item in _mapping(baseline_summary.get("semantic_elements")).items()
    }
    for specialist in selected_specialists:
        element = _SPECIALIST_ELEMENT_MAP[specialist]
        events = list(extracted.get(specialist) or [])
        grounding_counts = _grounding_counts(events)
        if events:
            grounding = _best_grounding(grounding_counts)
            elements[element] = {
                "status": "present" if grounding == "span" else "partial",
                "grounding": grounding,
                "needs_review": grounding != "span",
                "evidence_counts": {
                    "specialist_validated_event_count": len(events),
                    **_prefixed_counts("grounding", grounding_counts),
                },
            }
    return {
        "semantic_elements": elements,
        "status_counts": _counter_dict(
            Counter(_text(item.get("status")) for item in elements.values())
        ),
        "grounding_counts": _counter_dict(
            Counter(_text(item.get("grounding")) for item in elements.values())
        ),
        "needs_review_count": sum(
            1 for item in elements.values() if bool(item.get("needs_review"))
        ),
    }


def _compact_element(element: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": _text(element.get("status")) or "missing",
        "grounding": _text(element.get("grounding")) or "none",
        "needs_review": bool(element.get("needs_review")),
        "evidence_counts": {
            _text(key): _safe_int(value)
            for key, value in sorted(
                _mapping(element.get("evidence_counts")).items(),
                key=lambda item: str(item[0]),
            )
        },
    }


def _coverage_improved(
    baseline: Mapping[str, Any],
    enhanced: Mapping[str, Any],
) -> bool:
    status_improved = _STATUS_ORDER.get(_text(enhanced.get("status")), 0) > _STATUS_ORDER.get(
        _text(baseline.get("status")),
        0,
    )
    grounding_improved = _GROUNDING_ORDER.get(_text(enhanced.get("grounding")), 0) > _GROUNDING_ORDER.get(
        _text(baseline.get("grounding")),
        0,
    )
    return status_improved or grounding_improved


def _grounding_counts(events: Sequence[Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for event in events:
        provenance = getattr(event, "provenance", None)
        kind = getattr(provenance, "kind", None)
        counts[_text(kind) or "none"] += 1
    if not counts:
        counts["none"] = 0
    return _counter_dict(counts)


def _best_grounding(counts: Mapping[str, Any]) -> str:
    best = "none"
    for grounding, count in counts.items():
        if _safe_int(count) <= 0:
            continue
        if _GROUNDING_ORDER.get(str(grounding), 0) > _GROUNDING_ORDER[best]:
            best = str(grounding)
    return best


def _validation_failures(stats: Any) -> dict[str, int]:
    return {
        key: value
        for key, value in _stats_dict(stats).items()
        if key.startswith("dropped_") and value
    }


def _stats_dict(stats: Any) -> dict[str, int]:
    if is_dataclass(stats):
        payload = asdict(stats)
    elif isinstance(stats, Mapping):
        payload = dict(stats)
    else:
        payload = {}
    return {
        _text(key): _safe_int(value)
        for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
    }


def _not_attempted_specialist_record(specialist: str) -> dict[str, Any]:
    del specialist
    return {
        "attempted": False,
        "raw_candidate_count": 0,
        "validated_event_count": 0,
        "validation_failures": {},
        "validation_stats": {},
        "grounding_counts": {"none": 0},
        "improved_elements": [],
        "did_improve_coverage": False,
    }


def _normalize_specialists(specialists: Sequence[str]) -> list[str]:
    selected: list[str] = []
    for specialist in specialists:
        normalized = _text(specialist)
        if normalized not in SPECIALISTS:
            raise ValueError(f"unknown specialist: {normalized}")
        if normalized not in selected:
            selected.append(normalized)
    return selected or list(SPECIALISTS)


def _source_scope(
    *,
    model_calls: int = 0,
    model_calls_approved: bool = False,
) -> dict[str, Any]:
    return {
        "local_only": True,
        "shareable_without_review": False,
        "raw_archives_read": True,
        "raw_transcript_included": False,
        "raw_memo_included": False,
        "raw_revised_answer_included": False,
        "raw_model_messages_included": False,
        "provider_reasoning_details_included": False,
        "failed_quote_text_included": False,
        "absolute_archive_paths_included": False,
        "control_argument_values_included": False,
        "model_calls": model_calls,
        "model_calls_approved": model_calls_approved,
        "llm_judge_used": False,
        "archive_mutation": False,
        "runtime_behavior_changed": False,
    }


def _prefixed_counts(prefix: str, counts: Mapping[str, Any]) -> dict[str, int]:
    return {
        f"{prefix}_{_text(key)}_count": _safe_int(value)
        for key, value in sorted(counts.items(), key=lambda item: str(item[0]))
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


def _call_log(boundary: Any) -> list[Any]:
    call_log = getattr(boundary, "call_log", [])
    return call_log if isinstance(call_log, list) else []


def _new_call_records(boundary: Any, start: int) -> list[Any]:
    return list(_call_log(boundary)[max(0, start):])


def _probe_usage_summary(
    call_records: Sequence[Any],
    *,
    case_id: str,
    run_id: str,
) -> dict[str, Any]:
    if not call_records:
        return {}
    return build_usage_summary(
        run_id=_usage_run_id(case_id, run_id),
        pipeline_boundary_calls=call_records,
    )


def _usage_run_id(case_id: str, run_id: str) -> str:
    raw = f"specialist_probe_{case_id}_{run_id}"
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in raw)[:160]


def _model_call_count(call_records: Sequence[Any]) -> int:
    return sum(
        1
        for record in call_records
        if _text(_call_record_dict(record).get("status")) != _BOUNDARY_MISSING_CREDENTIAL_STATUS
    )


def _model_usage_summary(usage_summary: Mapping[str, Any]) -> dict[str, Any]:
    if not usage_summary:
        return {
            "estimated_total_cost_usd": None,
            "cost_estimate_state": "not_applicable",
            "model_call_count": 0,
            "provider": "",
            "models_seen": [],
            "requested_models_seen": [],
        }
    vendors = _mapping(usage_summary.get("vendors"))
    openrouter = _mapping(vendors.get("openrouter"))
    return {
        "estimated_total_cost_usd": usage_summary.get("estimated_total_cost_usd"),
        "cost_estimate_state": _text(usage_summary.get("cost_estimate_state")),
        "pricing_table_version": _text(usage_summary.get("pricing_table_version")),
        "model_call_count": _safe_int(openrouter.get("calls")),
        "provider": _text(openrouter.get("provider")),
        "primary_model": _text(openrouter.get("primary_model")),
        "models_seen": _string_list(openrouter.get("models_seen")),
        "requested_models_seen": _string_list(openrouter.get("requested_models_seen")),
        "prompt_tokens": _safe_int(openrouter.get("prompt_tokens")),
        "completion_tokens": _safe_int(openrouter.get("completion_tokens")),
        "total_tokens": _safe_int(openrouter.get("total_tokens")),
    }


def _sanitize_call_record(record: Any) -> dict[str, Any]:
    payload = _call_record_dict(record)
    return {
        "stage": _text(payload.get("stage")) or "unlabeled",
        "provider_name": _text(payload.get("provider_name")),
        "requested_model": _text(payload.get("requested_model")),
        "served_model": _text(payload.get("served_model")),
        "model": _text(payload.get("model")),
        "model_attribution_status": _text(payload.get("model_attribution_status")),
        "status": _sanitize_boundary_status(payload.get("status")),
        "finish_reason": _text(payload.get("finish_reason")),
        "temperature": _safe_float(payload.get("temperature")),
        "prompt_tokens": _safe_int(payload.get("prompt_tokens")),
        "completion_tokens": _safe_int(payload.get("completion_tokens")),
        "total_tokens": _safe_int(payload.get("total_tokens")),
        "cached_tokens": _safe_int(payload.get("cached_tokens")),
        "cache_write_tokens": _safe_int(payload.get("cache_write_tokens")),
        "reasoning_tokens": _safe_int(payload.get("reasoning_tokens")),
        "reasoning_disabled": bool(payload.get("reasoning_disabled")),
        "reasoning_details_present": bool(payload.get("reasoning_details_present")),
    }


def _call_record_dict(record: Any) -> dict[str, Any]:
    if is_dataclass(record):
        return asdict(record)
    if isinstance(record, Mapping):
        return dict(record)
    if hasattr(record, "to_dict"):
        value = record.to_dict()
        return dict(value) if isinstance(value, Mapping) else {}
    return {}


def _sanitize_boundary_status(value: Any) -> str:
    status = _text(value)
    if status == _BOUNDARY_MISSING_CREDENTIAL_STATUS:
        return _MISSING_CREDENTIAL_STATUS
    return status


def _specialist_from_prompt(system_prompt: str) -> str:
    if "LIVE CONSTRAINTS" in system_prompt:
        return "live_constraints"
    if "STANCE EVENT" in system_prompt:
        return "stance"
    if "DROPPED THREADS" in system_prompt:
        return "dropped_threads"
    return "unknown"


def _notes_for_mode(boundary_mode: str) -> list[str]:
    if boundary_mode == "real":
        return [
            "Real specialist boundary calls were made for this offline probe.",
            "The probe records validation counts, grounding counts, and coverage deltas only.",
            "No raw prompts, responses, transcript text, or validated event text are exported.",
            "No archive artifacts were mutated.",
        ]
    return [
        "Fake boundary payloads exercise extractor validation and probe custody only.",
        "This probe does not measure real specialist extraction quality.",
        "No model calls were made.",
        "No archive artifacts were mutated.",
    ]


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return sorted(_text(item) for item in value if _text(item))


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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
