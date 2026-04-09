from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

from .route_quality_review_status import load_route_quality_review_status


def summarize_pipeline_result(
    payload: Mapping[str, object],
    *,
    root: Path | None = None,
) -> dict[str, object]:
    audit = payload.get("audit", {}) if isinstance(payload, Mapping) else {}
    audit_dict = audit if isinstance(audit, Mapping) else {}
    traces = audit_dict.get("promoted_bundle_traces", [])
    routing_decisions = audit_dict.get("routing_decisions", [])
    warnings = _normalize_string_tuple(audit_dict.get("warnings"))
    review_root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    review_registry = load_route_quality_review_status(review_root)
    summaries = [
        summarize_promoted_bundle_trace(trace)
        for trace in traces
        if isinstance(trace, Mapping)
    ]
    routed_tendencies = [
        _attach_route_review_status(
            summarize_routing_decision(route),
            review_registry,
        )
        for route in routing_decisions
        if isinstance(route, Mapping)
    ]
    return {
        "detected_tendencies": _normalize_string_tuple(payload.get("detected_tendencies", ())),
        "warnings": warnings,
        "promoted_bundle_count": len(summaries),
        "promoted_bundles": summaries,
        "routed_tendency_count": len(routed_tendencies),
        "routed_tendencies": routed_tendencies,
        "route_quality_rollup": _route_quality_rollup(routed_tendencies),
    }


def summarize_promoted_bundle_trace(trace: Mapping[str, object]) -> dict[str, object]:
    selected_chunks = trace.get("selected_chunks", [])
    lane_summaries = tuple(
        summarize_selected_chunk(chunk)
        for chunk in selected_chunks
        if isinstance(chunk, Mapping)
    )
    activation_context = str(trace.get("primary_activation_context", "")).strip()
    advisory_quality_flags = _normalize_string_tuple(trace.get("advisory_quality_flags", ()))
    return {
        "tendency_id": str(trace.get("tendency_id", "")).strip(),
        "sub_pattern": str(trace.get("sub_pattern", "")).strip(),
        "primary_model_id": str(trace.get("primary_model_id", "")).strip(),
        "provenance_complete": bool(trace.get("provenance_complete", False)),
        "provenance_gaps": _normalize_string_tuple(trace.get("provenance_gaps", ())),
        "guardrail_tags": _normalize_string_tuple(trace.get("guardrail_tags", ())),
        "blocking_quality_flags": _normalize_string_tuple(trace.get("blocking_quality_flags", ())),
        "advisory_quality_flags": advisory_quality_flags,
        "notable_advisory_quality_flags": _notable_flags(advisory_quality_flags),
        "activation_context": {
            "text": activation_context,
            "present": bool(activation_context),
            "source_path": str(trace.get("activation_context_source_path", "")).strip(),
            "source_quote": str(trace.get("activation_context_source_quote", "")).strip(),
            "extraction_type": str(trace.get("activation_context_extraction_type", "")).strip(),
            "confidence": str(trace.get("activation_context_confidence", "")).strip(),
            "blocking_quality_flags": _normalize_string_tuple(
                trace.get("activation_context_blocking_quality_flags", ())
            ),
            "advisory_quality_flags": _normalize_string_tuple(
                trace.get("activation_context_advisory_quality_flags", ())
            ),
        },
        "lanes": lane_summaries,
        "lane_quality_rollup": _lane_quality_rollup(lane_summaries),
    }


def summarize_selected_chunk(chunk: Mapping[str, object]) -> dict[str, object]:
    advisory_quality_flags = _normalize_string_tuple(chunk.get("advisory_quality_flags", ()))
    return {
        "lane": str(chunk.get("lane", "")).strip(),
        "chunk_id": str(chunk.get("chunk_id", "")).strip(),
        "chunk_type": str(chunk.get("chunk_type", "")).strip(),
        "model_id": str(chunk.get("model_id", "")).strip(),
        "text": str(chunk.get("text", "")).strip(),
        "source_file": str(chunk.get("source_file", "")).strip(),
        "source_quote": str(chunk.get("source_quote", "")).strip(),
        "extraction_type": str(chunk.get("extraction_type", "")).strip(),
        "confidence": str(chunk.get("confidence", "")).strip(),
        "guardrail_tags": _normalize_string_tuple(chunk.get("guardrail_tags", ())),
        "blocking_quality_flags": _normalize_string_tuple(chunk.get("blocking_quality_flags", ())),
        "advisory_quality_flags": advisory_quality_flags,
        "notable_advisory_quality_flags": _notable_flags(advisory_quality_flags),
        "is_inferred_only": "inferred-only" in advisory_quality_flags,
        "is_low_confidence": "low-confidence" in advisory_quality_flags,
    }


def summarize_routing_decision(route: Mapping[str, object]) -> dict[str, object]:
    tendency = route.get("tendency", {}) if isinstance(route, Mapping) else {}
    tendency_dict = tendency if isinstance(tendency, Mapping) else {}
    activation_ref = route.get("primary_activation_context_ref", {})
    activation_ref_dict = activation_ref if isinstance(activation_ref, Mapping) else {}
    activation_context = str(route.get("primary_activation_context", "")).strip()
    blocking_quality_flags = _normalize_string_tuple(
        route.get("primary_activation_context_blocking_quality_flags", ())
    )
    advisory_quality_flags = _normalize_string_tuple(
        route.get("primary_activation_context_advisory_quality_flags", ())
    )
    source_path = str(activation_ref_dict.get("path", "")).strip()
    return {
        "tendency_id": str(tendency_dict.get("tendency_id", "")).strip(),
        "tendency_name": str(tendency_dict.get("display_name", "")).strip(),
        "sub_pattern": str(route.get("sub_pattern", "")).strip(),
        "primary_model_id": str(route.get("primary_model_id", "")).strip(),
        "supporting_model_ids": _normalize_string_tuple(route.get("supporting_model_ids", ())),
        "risk_model_ids": _normalize_string_tuple(route.get("risk_model_ids", ())),
        "is_source_backed": bool(source_path),
        "has_blocking_quality_flags": bool(blocking_quality_flags),
        "has_advisory_quality_flags": bool(advisory_quality_flags),
        "notable_advisory_quality_flags": _notable_flags(advisory_quality_flags),
        "review_status": "",
        "review_note_path": "",
        "review_note_summary": "",
        "next_review_lane": "",
        "is_held_thin_by_design": False,
        "activation_context": {
            "text": activation_context,
            "present": bool(activation_context),
            "source_path": source_path,
            "source_quote": str(activation_ref_dict.get("quote", "")).strip(),
            "extraction_type": str(activation_ref_dict.get("extraction_type", "")).strip(),
            "confidence": str(activation_ref_dict.get("confidence", "")).strip(),
            "blocking_quality_flags": blocking_quality_flags,
            "advisory_quality_flags": advisory_quality_flags,
        },
    }


def render_pipeline_summary_markdown(summary: Mapping[str, object]) -> str:
    lines = [
        "# Promoted Bundle Summary",
        "",
        f"- Detected tendencies: `{', '.join(summary.get('detected_tendencies', ())) or 'none'}`",
        f"- Warnings: `{', '.join(summary.get('warnings', ())) or 'none'}`",
        f"- Promoted bundles: `{summary.get('promoted_bundle_count', 0)}`",
        f"- Routed tendencies: `{summary.get('routed_tendency_count', 0)}`",
        (
            f"- Route quality rollup: `source-backed={summary.get('route_quality_rollup', {}).get('source_backed_routes', 0)}` "
            f"`blocking-flagged={summary.get('route_quality_rollup', {}).get('blocking_flagged_routes', 0)}` "
            f"`advisory-flagged={summary.get('route_quality_rollup', {}).get('advisory_flagged_routes', 0)}` "
            f"`missing-activation-source={summary.get('route_quality_rollup', {}).get('missing_activation_source_routes', 0)}` "
            f"`held-thin-by-design={summary.get('route_quality_rollup', {}).get('held_thin_by_design_routes', 0)}` "
            f"`notable={','.join(summary.get('route_quality_rollup', {}).get('notable_advisory_quality_flags', ())) or 'none'}`"
        ),
        "",
    ]
    bundles = summary.get("promoted_bundles", [])
    if bundles:
        for bundle in bundles:
            lines.extend(render_promoted_bundle_markdown(bundle).splitlines())
            lines.append("")
    else:
        lines.append("No promoted bundles.")
        lines.append("")
    routed_tendencies = summary.get("routed_tendencies", [])
    if routed_tendencies:
        lines.append("## Routed Tendencies")
        lines.append("")
        for route in routed_tendencies:
            lines.extend(render_routing_decision_markdown(route).splitlines())
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_promoted_bundle_markdown(bundle: Mapping[str, object]) -> str:
    activation = bundle.get("activation_context", {}) if isinstance(bundle, Mapping) else {}
    lines = [
        f"## {bundle.get('tendency_id', '')}",
        "",
        f"- Route: `{bundle.get('sub_pattern', '')} -> {bundle.get('primary_model_id', '')}`",
        f"- Provenance complete: `{bundle.get('provenance_complete', False)}`",
        f"- Guardrail tags: `{', '.join(bundle.get('guardrail_tags', ())) or 'none'}`",
        f"- Blocking quality: `{', '.join(bundle.get('blocking_quality_flags', ())) or 'none'}`",
        f"- Advisory quality: `{', '.join(bundle.get('notable_advisory_quality_flags', ())) or 'none'}`",
        f"- Lane quality rollup: `low-confidence={bundle.get('lane_quality_rollup', {}).get('low_confidence_lanes', 0)}` `inferred-only={bundle.get('lane_quality_rollup', {}).get('inferred_only_lanes', 0)}` `notable={','.join(bundle.get('lane_quality_rollup', {}).get('notable_advisory_quality_flags', ())) or 'none'}`",
        f"- Activation context: `{activation.get('text', '') or 'missing'}`",
        f"- Activation source: `{activation.get('source_path', '') or 'missing'}`",
        f"- Activation quality: `blocking={','.join(activation.get('blocking_quality_flags', ())) or 'none'}` `advisory={','.join(activation.get('advisory_quality_flags', ())) or 'none'}`",
        "",
        "### Lanes",
        "",
    ]
    for lane in bundle.get("lanes", []):
        lines.append(
            f"- `{lane.get('lane', '')}` `{lane.get('model_id', '')}` `{lane.get('chunk_id', '')}` "
            f"source=`{lane.get('source_file', '') or 'missing'}` "
            f"confidence=`{lane.get('confidence', '') or 'missing'}` "
            f"blocking=`{','.join(lane.get('blocking_quality_flags', ())) or 'none'}` "
            f"advisory=`{','.join(lane.get('notable_advisory_quality_flags', ())) or 'none'}` "
            f"inferred=`{'yes' if lane.get('is_inferred_only') else 'no'}` "
            f"low_confidence=`{'yes' if lane.get('is_low_confidence') else 'no'}`"
        )
    return "\n".join(lines)


def render_routing_decision_markdown(route: Mapping[str, object]) -> str:
    activation = route.get("activation_context", {}) if isinstance(route, Mapping) else {}
    return "\n".join(
        [
            f"### {route.get('tendency_id', '')}",
            "",
            f"- Route: `{route.get('sub_pattern', '') or 'general'} -> {route.get('primary_model_id', '')}`",
            f"- Tendency: `{route.get('tendency_name', '') or 'missing'}`",
            f"- Supporting models: `{', '.join(route.get('supporting_model_ids', ())) or 'none'}`",
            f"- Risk models: `{', '.join(route.get('risk_model_ids', ())) or 'none'}`",
            (
                f"- Route quality: `source_backed={'yes' if route.get('is_source_backed') else 'no'}` "
                f"`blocking={'yes' if route.get('has_blocking_quality_flags') else 'no'}` "
                f"`advisory={'yes' if route.get('has_advisory_quality_flags') else 'no'}` "
                f"`notable={','.join(route.get('notable_advisory_quality_flags', ())) or 'none'}` "
                f"`review_status={route.get('review_status', '') or 'none'}`"
            ),
            f"- Activation context: `{activation.get('text', '') or 'missing'}`",
            f"- Activation source: `{activation.get('source_path', '') or 'missing'}`",
            f"- Activation confidence: `{activation.get('confidence', '') or 'missing'}`",
            f"- Activation quality: `blocking={','.join(activation.get('blocking_quality_flags', ())) or 'none'}` `advisory={','.join(activation.get('advisory_quality_flags', ())) or 'none'}`",
            f"- Review note: `{route.get('review_note_path', '') or 'none'}`",
            f"- Next review lane: `{route.get('next_review_lane', '') or 'none'}`",
        ]
    )


def _normalize_string_tuple(payload: object) -> tuple[str, ...]:
    if isinstance(payload, (str, bytes)):
        values = [payload]
    elif isinstance(payload, Sequence):
        values = list(payload)
    else:
        values = []
    normalized: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text:
            normalized.append(text)
    return tuple(normalized)


def _notable_flags(flags: Sequence[str]) -> tuple[str, ...]:
    return tuple(flag for flag in _normalize_string_tuple(flags) if not flag.endswith("inferred-only") and flag != "inferred-only")


def _lane_quality_rollup(lanes: Sequence[Mapping[str, object]]) -> dict[str, object]:
    low_confidence_lanes = 0
    inferred_only_lanes = 0
    notable: list[str] = []
    seen: set[str] = set()
    for lane in lanes:
        advisories = _normalize_string_tuple(lane.get("advisory_quality_flags", ()))
        if "low-confidence" in advisories:
            low_confidence_lanes += 1
        if "inferred-only" in advisories:
            inferred_only_lanes += 1
        for flag in _notable_flags(advisories):
            if flag in seen:
                continue
            seen.add(flag)
            notable.append(flag)
    return {
        "low_confidence_lanes": low_confidence_lanes,
        "inferred_only_lanes": inferred_only_lanes,
        "notable_advisory_quality_flags": tuple(notable),
    }


def _route_quality_rollup(routes: Sequence[Mapping[str, object]]) -> dict[str, object]:
    source_backed_routes = 0
    blocking_flagged_routes = 0
    advisory_flagged_routes = 0
    missing_activation_source_routes = 0
    notable: list[str] = []
    seen: set[str] = set()
    for route in routes:
        activation = route.get("activation_context", {}) if isinstance(route, Mapping) else {}
        activation_dict = activation if isinstance(activation, Mapping) else {}
        source_path = str(activation_dict.get("source_path", "")).strip()
        if source_path:
            source_backed_routes += 1
        else:
            missing_activation_source_routes += 1
        blocking = _normalize_string_tuple(activation_dict.get("blocking_quality_flags", ()))
        advisory = _normalize_string_tuple(activation_dict.get("advisory_quality_flags", ()))
        if blocking:
            blocking_flagged_routes += 1
        if advisory:
            advisory_flagged_routes += 1
        for flag in _notable_flags(advisory):
            if flag in seen:
                continue
            seen.add(flag)
            notable.append(flag)
    return {
        "source_backed_routes": source_backed_routes,
        "blocking_flagged_routes": blocking_flagged_routes,
        "advisory_flagged_routes": advisory_flagged_routes,
        "missing_activation_source_routes": missing_activation_source_routes,
        "notable_advisory_quality_flags": tuple(notable),
        "held_thin_by_design_routes": sum(
            1 for route in routes if route.get("is_held_thin_by_design")
        ),
    }


def _attach_route_review_status(
    route_summary: Mapping[str, object],
    review_registry: Mapping[str, Mapping[str, str]],
) -> dict[str, object]:
    tendency_id = str(route_summary.get("tendency_id", "")).strip()
    review_entry = review_registry.get(tendency_id, {})
    review_status = str(review_entry.get("review_status", "") or "").strip()
    review_note_path = str(review_entry.get("review_note_path", "") or "").strip()
    review_note_summary = str(review_entry.get("review_note_summary", "") or "").strip()
    next_review_lane = str(review_entry.get("next_review_lane", "") or "").strip()
    return {
        **route_summary,
        "review_status": review_status,
        "review_note_path": review_note_path,
        "review_note_summary": review_note_summary,
        "next_review_lane": next_review_lane,
        "is_held_thin_by_design": review_status == "held-thin-by-design",
    }
