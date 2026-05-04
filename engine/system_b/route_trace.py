from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any


ROUTE_TRACE_SCHEMA_VERSION = "route_trace.v1"


def build_route_trace_payload(result_payload: Mapping[str, Any]) -> dict[str, Any]:
    """Build a versioned route trace from already-recorded runtime artifacts.

    This module is intentionally a serializer/normalizer. It does not infer
    why a model was selected; it copies reasons, candidates, route tables, and
    exclusions that runtime lanes already emitted.
    """

    audit = _mapping(result_payload.get("audit_summary"))
    trace = {
        "schema_version": ROUTE_TRACE_SCHEMA_VERSION,
        "lanes": {
            "lane1": _lane1_trace(result_payload, audit),
            "lane2": _lane2_trace(result_payload, audit),
            "lane3": _lane3_trace(result_payload),
            "lane4": _lane4_trace(result_payload),
        },
    }
    trace["anti_echo"] = _anti_echo_trace(trace["lanes"], result_payload)
    trace["summary"] = _summary(trace)
    return trace


def _lane1_trace(result_payload: Mapping[str, Any], audit: Mapping[str, Any]) -> dict[str, Any]:
    decisions = [_mapping(item) for item in _list(audit.get("routing_decisions"))]
    findings = {
        str(item.get("tendency_id", "")): item
        for item in (_mapping(row) for row in _list(_mapping(result_payload.get("delta_card")).get("findings")))
        if item.get("tendency_id")
    }
    rows: list[dict[str, Any]] = []
    for decision in decisions:
        tendency_id = str(decision.get("tendency_id", ""))
        finding = findings.get(tendency_id, {})
        selected_from_finding = [
            str(model_id)
            for model_id in _list(finding.get("selected_model_ids"))
            if str(model_id).strip()
        ]
        selected_model_ids = selected_from_finding or _dedupe(
            [
                str(decision.get("primary_model_id", "")),
                *_list(decision.get("supporting_model_ids")),
                *_list(decision.get("risk_model_ids")),
            ]
        )
        supporting_trace = [
            _candidate_trace_item(item, candidate_type="supporting")
            for item in _list(decision.get("supporting_candidate_trace"))
        ]
        risk_trace = [
            _candidate_trace_item(item, candidate_type="risk")
            for item in _list(decision.get("risk_candidate_trace"))
        ]
        rejected = [
            item
            for item in [*supporting_trace, *risk_trace]
            if not item.get("selected")
        ]
        rows.append(
            {
                "tendency_id": tendency_id,
                "route_source": "tendency_binding",
                "sub_pattern": decision.get("sub_pattern", ""),
                "primary_model_id": decision.get("primary_model_id", ""),
                "selected_model_ids": selected_model_ids,
                "antidote_model_ids": _list(decision.get("antidote_model_ids")),
                "supporting_model_ids": _list(decision.get("supporting_model_ids")),
                "risk_model_ids": _list(decision.get("risk_model_ids")),
                "supporting_candidates": supporting_trace,
                "risk_candidates": risk_trace,
                "rejected_candidates": rejected,
                "close_alternatives": _close_alternatives(decision),
            }
        )
    return {
        "lane_id": "lane1",
        "label": "Lane 1 Route",
        "route_source": "tendency_binding",
        "routes": rows,
    }


def _lane2_trace(result_payload: Mapping[str, Any], audit: Mapping[str, Any]) -> dict[str, Any]:
    companion = _mapping(result_payload.get("companion_cheat_sheet"))
    anchors = [_mapping(item) for item in _list(companion.get("anchors"))]
    selected_model_ids = _dedupe(str(anchor.get("model_id", "")) for anchor in anchors)
    candidates = [_mapping(item) for item in _list(audit.get("companion_candidates"))]
    accepted = [_mapping(item) for item in _list(audit.get("companion_verification_accepted_before_cap"))]
    rejected = [_mapping(item) for item in _list(audit.get("companion_rejected_models"))]
    capped = [_mapping(item) for item in _list(audit.get("companion_verification_capped_models"))]
    duplicates = [_mapping(item) for item in _list(audit.get("companion_verification_duplicate_accepts"))]
    quote_repairs = [_mapping(item) for item in _list(audit.get("companion_verification_quote_repairs"))]
    silently_omitted = [
        _mapping(item) for item in _list(audit.get("companion_verification_silently_omitted"))
    ]

    # These fallback reasons label the source list only. Do not extend this
    # block into semantic explanation of why the verifier made a decision.
    rejected_candidates: list[dict[str, Any]] = []
    for item in rejected:
        rejected_candidates.append(
            {
                "model_id": item.get("model_id", ""),
                "rejection_reason": item.get("rejection_reason") or "verifier_rejected",
                "stage": "verification",
            }
        )
    for item in capped:
        rejected_candidates.append(
            {
                "model_id": item.get("model_id", ""),
                "rejection_reason": item.get("drop_reason") or "capped_at_top_5",
                "stage": "surfacing_budget",
            }
        )
    for item in duplicates:
        rejected_candidates.append(
            {
                "model_id": item.get("model_id", ""),
                "rejection_reason": item.get("drop_reason") or "duplicate_accept_dedupe",
                "stage": "verification_dedupe",
            }
        )
    for item in silently_omitted:
        rejected_candidates.append(
            {
                "model_id": item.get("model_id", ""),
                "rejection_reason": item.get("drop_reason") or "not_in_verifier_response",
                "stage": "verification_omission",
            }
        )

    return {
        "lane_id": "lane2",
        "label": "Lane 2 Route",
        "route_source": "companion_detection_verification",
        "selected_model_ids": selected_model_ids,
        "candidate_count": len(candidates),
        "candidate_cap": audit.get("companion_candidate_cap", 0),
        "candidates": candidates,
        "accepted_before_cap": accepted,
        "rejected_candidates": rejected_candidates,
        "quote_repairs": quote_repairs,
        "anti_echo_model_ids": _list(companion.get("anti_echo_model_ids")),
    }


def _lane3_trace(result_payload: Mapping[str, Any]) -> dict[str, Any]:
    card = _mapping(result_payload.get("frame_pressure_card"))
    elements = [_mapping(item) for item in _list(card.get("frame_elements"))]
    reframings = [_mapping(item) for item in _list(card.get("reframings"))]
    reframings_by_element: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in reframings:
        try:
            source_index = int(item.get("source_element_index", 0) or 0)
        except (TypeError, ValueError):
            source_index = 0
        reframings_by_element[source_index].append(item)

    rows: list[dict[str, Any]] = []
    for route in (_mapping(item) for item in _list(card.get("routes"))):
        try:
            element_index = int(route.get("element_index", 0) or 0)
        except (TypeError, ValueError):
            element_index = 0
        selected = _dedupe(
            str(item.get("grounding_model", ""))
            for item in reframings_by_element.get(element_index, [])
        )
        candidate_model_ids = _list(route.get("candidate_model_ids"))
        rejected = [
            {
                "model_id": model_id,
                "rejection_reason": "not_used_in_returned_reframing",
                "stage": "reframe_generation",
            }
            for model_id in candidate_model_ids
            if model_id not in selected
        ]
        rejected.extend(
            {
                "model_id": model_id,
                "rejection_reason": "anti_echo_lane1_overlap",
                "stage": "frame_route",
            }
            for model_id in _list(route.get("excluded_model_ids"))
        )
        element = elements[element_index] if element_index < len(elements) else {}
        rows.append(
            {
                "element_index": element_index,
                "frame_pattern": route.get("frame_pattern", ""),
                "element_text": element.get("element_text", ""),
                "route_source": "frame_pattern_routing",
                "selected_model_ids": selected,
                "candidate_model_ids": candidate_model_ids,
                "excluded_model_ids": _list(route.get("excluded_model_ids")),
                "rejected_candidates": rejected,
            }
        )

    if not rows and reframings:
        rows.append(
            {
                "element_index": 0,
                "frame_pattern": "",
                "element_text": "",
                "route_source": "frame_reframing_payload",
                "selected_model_ids": _dedupe(
                    str(item.get("grounding_model", "")) for item in reframings
                ),
                "candidate_model_ids": [],
                "excluded_model_ids": [],
                "rejected_candidates": [],
            }
        )

    return {
        "lane_id": "lane3",
        "label": "Lane 3 Route",
        "route_source": "frame_pattern_routing",
        "routes": rows,
        "anti_echo_model_ids": _list(card.get("anti_echo_model_ids")),
    }


def _lane4_trace(result_payload: Mapping[str, Any]) -> dict[str, Any]:
    card = _mapping(result_payload.get("structural_coverage_card"))
    rows: list[dict[str, Any]] = []
    for route in (_mapping(item) for item in _list(card.get("gap_routes"))):
        excluded = _list(route.get("excluded_model_ids"))
        rows.append(
            {
                "dimension_id": route.get("dimension_id", ""),
                "dimension_name": route.get("dimension_name", ""),
                "route_source": "structural_gap_routing",
                "selected_model_ids": _list(route.get("candidate_model_ids")),
                "candidate_model_ids": _list(route.get("candidate_model_ids")),
                "excluded_model_ids": excluded,
                "rejected_candidates": [
                    {
                        "model_id": model_id,
                        "rejection_reason": "anti_echo_upstream_lane_overlap",
                        "stage": "structural_gap_route",
                    }
                    for model_id in excluded
                ],
            }
        )
    return {
        "lane_id": "lane4",
        "label": "Lane 4 Route",
        "route_source": "structural_gap_routing",
        "question_type": card.get("question_type", ""),
        "routes": rows,
        "anti_echo_model_ids": _list(card.get("anti_echo_model_ids")),
    }


def _anti_echo_trace(
    lanes: Mapping[str, Any],
    result_payload: Mapping[str, Any],
) -> dict[str, Any]:
    lane_sources = _lane_sources(result_payload)
    exclusions: list[dict[str, Any]] = []
    lane3 = _mapping(lanes.get("lane3"))
    for route in (_mapping(item) for item in _list(lane3.get("routes"))):
        for model_id in _list(route.get("excluded_model_ids")):
            exclusions.append(
                {
                    "model_id": model_id,
                    "excluded_from": "lane3",
                    "reason": "anti_echo_lane1_overlap",
                    "source_lanes": lane_sources.get(model_id, []),
                }
            )
    lane4 = _mapping(lanes.get("lane4"))
    for route in (_mapping(item) for item in _list(lane4.get("routes"))):
        for model_id in _list(route.get("excluded_model_ids")):
            exclusions.append(
                {
                    "model_id": model_id,
                    "excluded_from": "lane4",
                    "reason": "anti_echo_upstream_lane_overlap",
                    "source_lanes": lane_sources.get(model_id, []),
                }
            )
    return {
        "lane_sources": lane_sources,
        "exclusions": exclusions,
    }


def _summary(trace: Mapping[str, Any]) -> dict[str, int]:
    lanes = _mapping(trace.get("lanes"))
    lane1_routes = _list(_mapping(lanes.get("lane1")).get("routes"))
    lane2_rejected = _list(_mapping(lanes.get("lane2")).get("rejected_candidates"))
    lane3_routes = _list(_mapping(lanes.get("lane3")).get("routes"))
    lane4_routes = _list(_mapping(lanes.get("lane4")).get("routes"))
    anti_echo = _mapping(trace.get("anti_echo"))
    return {
        "lane1_route_count": len(lane1_routes),
        "lane2_rejected_candidate_count": len(lane2_rejected),
        "lane3_route_count": len(lane3_routes),
        "lane4_route_count": len(lane4_routes),
        "anti_echo_exclusion_count": len(_list(anti_echo.get("exclusions"))),
    }


def _candidate_trace_item(item: Any, *, candidate_type: str) -> dict[str, Any]:
    payload = _mapping(item)
    return {
        "candidate_type": candidate_type,
        "model_id": payload.get("model_id", ""),
        "source_model_id": payload.get("source_model_id", ""),
        "edge_type": payload.get("edge_type", ""),
        "raw_affinity": payload.get("raw_affinity", 0.0),
        "fan_adjusted_affinity": payload.get("fan_adjusted_affinity", 0.0),
        "relevance_score": payload.get("relevance_score", 0.0),
        "selected": bool(payload.get("selected", False)),
        "rejection_reason": payload.get("rejection_reason", ""),
    }


def _close_alternatives(decision: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate_type, key in (
        ("supporting", "tiebreaker_supporting"),
        ("risk", "tiebreaker_risk"),
    ):
        trace = _mapping(decision.get(key))
        top1 = trace.get("top1_model") or trace.get("top1_model_id")
        top2 = trace.get("top2_model") or trace.get("top2_model_id")
        if not top1 and not top2:
            continue
        rows.append(
            {
                "candidate_type": candidate_type,
                "top1_model_id": top1 or "",
                "top2_model_id": top2 or "",
                "margin": trace.get("delta", 0.0),
                "tiebreaker_fired": bool(trace.get("fired", False)),
                "abort_reason": trace.get("abort_reason", ""),
            }
        )
    return rows


def _lane_sources(result_payload: Mapping[str, Any]) -> dict[str, list[str]]:
    sources: dict[str, set[str]] = defaultdict(set)
    for finding in (_mapping(item) for item in _list(_mapping(result_payload.get("delta_card")).get("findings"))):
        for model_id in _list(finding.get("selected_model_ids")):
            if model_id:
                sources[str(model_id)].add("lane1")
    for anchor in (
        _mapping(item)
        for item in _list(_mapping(result_payload.get("companion_cheat_sheet")).get("anchors"))
    ):
        model_id = anchor.get("model_id")
        if model_id:
            sources[str(model_id)].add("lane2")
    for reframing in (
        _mapping(item)
        for item in _list(_mapping(result_payload.get("frame_pressure_card")).get("reframings"))
    ):
        model_id = reframing.get("grounding_model")
        if model_id:
            sources[str(model_id)].add("lane3")
    return {model_id: sorted(values) for model_id, values in sorted(sources.items())}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dedupe(values: Any) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result
