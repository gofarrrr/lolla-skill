"""Research-only sealing and routing for fact-free reasoning patterns."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any


PACKET_SCHEMA = "lolla.reasoning_pattern_packet.v0"
PROJECTION_SCHEMA = "lolla.graph_reasoning_pattern_projection.v0"
ROUTING_RESULT_SCHEMA = "lolla.reasoning_pattern_shadow_routing_result.v0"
CONTROLLED_MECHANISMS = {
    "status_signal_used_as_evidence",
    "ambiguous_signal_treated_as_commitment",
    "acknowledged_constraint_not_gated",
    "criteria_defined_after_commitment",
    "initial_frame_persists_after_question_change",
    "counterpressure_acknowledged_not_integrated",
    "reversible_path_not_considered",
    "upside_downside_evidence_asymmetry",
    "missing_reversal_condition",
    "other_review_required",
}
SUBJECT_SCOPES = {"user", "assistant", "joint_process"}
PATTERN_STATES = {"present", "missing_protection", "tension"}
_PATTERN_FIELDS = {"mechanism_id", "subject_scope", "state", "source_turns"}
_NODE_FIELDS = {"pattern_id", "mechanism_id", "subject_scope", "state"}
_PROJECTION_FIELDS = {
    "schema_version",
    "pattern_nodes",
    "pattern_edges",
    "contains_case_context",
}
_FACT_BOUNDARY = {
    "raw_text_included": False,
    "quotes_included": False,
    "entities_included": False,
    "case_quantities_included": False,
    "dates_included": False,
    "desired_outcome_included": False,
    "topic_labels_included": False,
}


class ReasoningPatternShadowError(ValueError):
    """Raised when a shadow pattern artifact violates deterministic custody."""


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def conversation_turn_numbers(conversation: str) -> set[int]:
    return {
        int(match.group(1))
        for match in re.finditer(r"(?m)^\[Turn\s+(\d+)\]\s+(?:USER|ASSISTANT):", conversation)
    }


def lint_routing_projection(projection: object) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    if not isinstance(projection, Mapping):
        return [{"code": "projection_not_object", "json_pointer": "/routing_projection"}]
    if set(projection) != _PROJECTION_FIELDS:
        violations.append(
            {"code": "projection_fields_invalid", "json_pointer": "/routing_projection"}
        )
    if projection.get("schema_version") != PROJECTION_SCHEMA:
        violations.append(
            {"code": "projection_schema_invalid", "json_pointer": "/routing_projection/schema_version"}
        )
    if projection.get("contains_case_context") is not False:
        violations.append(
            {"code": "case_context_flag_true", "json_pointer": "/routing_projection/contains_case_context"}
        )
    nodes = projection.get("pattern_nodes", [])
    if not isinstance(nodes, list):
        violations.append(
            {"code": "pattern_nodes_not_array", "json_pointer": "/routing_projection/pattern_nodes"}
        )
        nodes = []
    seen_ids: set[str] = set()
    for index, node in enumerate(nodes):
        pointer = f"/routing_projection/pattern_nodes/{index}"
        if not isinstance(node, Mapping) or set(node) != _NODE_FIELDS:
            violations.append({"code": "routing_node_shape_invalid", "json_pointer": pointer})
            continue
        pattern_id = str(node.get("pattern_id", ""))
        if not re.fullmatch(r"rp_\d{3}", pattern_id):
            violations.append({"code": "pattern_id_invalid", "json_pointer": pointer + "/pattern_id"})
        elif pattern_id in seen_ids:
            violations.append({"code": "pattern_id_duplicate", "json_pointer": pointer + "/pattern_id"})
        seen_ids.add(pattern_id)
        if node.get("mechanism_id") not in CONTROLLED_MECHANISMS - {"other_review_required"}:
            violations.append({"code": "mechanism_not_routing_eligible", "json_pointer": pointer + "/mechanism_id"})
        if node.get("subject_scope") not in SUBJECT_SCOPES:
            violations.append({"code": "subject_scope_invalid", "json_pointer": pointer + "/subject_scope"})
        if node.get("state") not in PATTERN_STATES:
            violations.append({"code": "pattern_state_invalid", "json_pointer": pointer + "/state"})
    edges = projection.get("pattern_edges", [])
    if not isinstance(edges, list):
        violations.append(
            {"code": "pattern_edges_not_array", "json_pointer": "/routing_projection/pattern_edges"}
        )
    elif edges:
        violations.append(
            {"code": "shadow_v0_edges_must_be_empty", "json_pointer": "/routing_projection/pattern_edges"}
        )
    return violations


def seal_pattern_response(
    response: Mapping[str, Any],
    *,
    packet_id: str,
    source_ref: str,
    source_sha256: str,
    valid_turn_numbers: set[int],
) -> dict[str, Any]:
    if set(response) != {"patterns"} or not isinstance(response.get("patterns"), list):
        raise ReasoningPatternShadowError("response must contain only a patterns array")
    raw_patterns = response["patterns"]
    if len(raw_patterns) > 6:
        raise ReasoningPatternShadowError("patterns exceeds six-item shadow cap")
    merged: dict[tuple[str, str, str], set[int]] = {}
    for index, item in enumerate(raw_patterns):
        if not isinstance(item, Mapping) or set(item) != _PATTERN_FIELDS:
            raise ReasoningPatternShadowError(f"patterns[{index}] has invalid shape")
        mechanism = str(item["mechanism_id"])
        scope = str(item["subject_scope"])
        state = str(item["state"])
        turns = item["source_turns"]
        if mechanism not in CONTROLLED_MECHANISMS:
            raise ReasoningPatternShadowError(f"patterns[{index}] mechanism is not controlled")
        if scope not in SUBJECT_SCOPES or state not in PATTERN_STATES:
            raise ReasoningPatternShadowError(f"patterns[{index}] enum is invalid")
        if not isinstance(turns, list) or not turns:
            raise ReasoningPatternShadowError(f"patterns[{index}] source_turns is empty")
        turn_set = {int(turn) for turn in turns}
        if turn_set - valid_turn_numbers:
            raise ReasoningPatternShadowError(f"patterns[{index}] references an unknown turn")
        merged.setdefault((mechanism, scope, state), set()).update(turn_set)

    pattern_hypotheses: list[dict[str, Any]] = []
    pattern_sources: list[dict[str, Any]] = []
    routing_nodes: list[dict[str, str]] = []
    for ordinal, ((mechanism, scope, state), turns) in enumerate(
        sorted(merged.items()), start=1
    ):
        pattern_id = f"rp_{ordinal:03d}"
        routing_eligible = mechanism != "other_review_required"
        pattern_hypotheses.append(
            {
                "pattern_id": pattern_id,
                "mechanism_id": mechanism,
                "subject_scope": scope,
                "state": state,
                "support_status": "provisional_source_linked",
                "routing_eligible": routing_eligible,
            }
        )
        pattern_sources.append(
            {
                "pattern_id": pattern_id,
                "source_semantic_item_ids": [f"turn:{turn}" for turn in sorted(turns)],
            }
        )
        if routing_eligible:
            routing_nodes.append(
                {
                    "pattern_id": pattern_id,
                    "mechanism_id": mechanism,
                    "subject_scope": scope,
                    "state": state,
                }
            )
    projection = {
        "schema_version": PROJECTION_SCHEMA,
        "pattern_nodes": routing_nodes,
        "pattern_edges": [],
        "contains_case_context": False,
    }
    violations = lint_routing_projection(projection)
    packet = {
        "schema_version": PACKET_SCHEMA,
        "packet_metadata": {
            "packet_id": f"reasoning_pattern_packet:{packet_id}",
            "interpretation_schema_version": "lolla.reasoning_pattern_shadow_interpreter.v0",
            "graph_runtime_modified": False,
        },
        "provenance": {
            "source_interpretation_ref": source_ref,
            "source_interpretation_sha256": source_sha256,
            "pattern_sources": pattern_sources,
            "raw_text_included": False,
        },
        "pattern_hypotheses": pattern_hypotheses,
        "routing_projection": projection,
        "fact_boundary": dict(_FACT_BOUNDARY),
        "lint": {"status": "passed" if not violations else "failed", "violations": violations},
        "non_claims": [
            "pattern_hypotheses_are_provisional",
            "not_human_validation",
            "not_reasoning_quality_proof",
            "not_advice_correctness_proof",
            "not_end_to_end_determinism",
            "missing_in_capture_is_not_missing_in_reality",
        ],
    }
    if violations:
        raise ReasoningPatternShadowError("sealed routing projection failed fact-leak lint")
    return packet


def normalized_projection_signature(packet: Mapping[str, Any]) -> str:
    projection = packet.get("routing_projection", {})
    violations = lint_routing_projection(projection)
    if violations:
        raise ReasoningPatternShadowError("cannot sign an invalid routing projection")
    nodes = sorted(
        (
            str(node["mechanism_id"]),
            str(node["subject_scope"]),
            str(node["state"]),
        )
        for node in projection.get("pattern_nodes", [])
    )
    return _sha256_text(_canonical_json({"nodes": nodes, "edges": []}))


def route_projection(
    packet: Mapping[str, Any],
    *,
    routing_contract: Mapping[str, Any],
    known_model_ids: set[str],
) -> dict[str, Any]:
    if routing_contract.get("status") != "research_only_runtime_dormant":
        raise ReasoningPatternShadowError("routing contract is not research-only")
    mapping = routing_contract.get("mechanism_seed_models", {})
    if not isinstance(mapping, Mapping):
        raise ReasoningPatternShadowError("mechanism_seed_models must be an object")
    projection = packet.get("routing_projection", {})
    violations = lint_routing_projection(projection)
    if violations:
        raise ReasoningPatternShadowError("routing projection is invalid")
    pulls: dict[str, set[str]] = {}
    for node in projection.get("pattern_nodes", []):
        mechanism = str(node["mechanism_id"])
        seeds = mapping.get(mechanism, [])
        if not isinstance(seeds, Sequence) or isinstance(seeds, (str, bytes)):
            raise ReasoningPatternShadowError(f"seed mapping is invalid: {mechanism}")
        for model_id in seeds:
            model = str(model_id)
            if model not in known_model_ids:
                raise ReasoningPatternShadowError(f"seed model is unknown: {model}")
            pulls.setdefault(model, set()).add(mechanism)
    candidates = [
        {"model_id": model_id, "pulled_by_mechanisms": sorted(mechanisms)}
        for model_id, mechanisms in sorted(pulls.items())
    ]
    return {
        "schema_version": ROUTING_RESULT_SCHEMA,
        "status": "research_only",
        "projection_signature": normalized_projection_signature(packet),
        "candidate_count": len(candidates),
        "seed_candidates": candidates,
        "graph_runtime_modified": False,
        "semantic_relevance_validated": False,
        "non_claims": [
            "seed_recall_is_not_applicability",
            "fixture_invariance_is_not_production_stability",
            "not_runtime_integration_authority",
        ],
    }
