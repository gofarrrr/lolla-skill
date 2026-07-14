"""Research-only joint-process reasoning target, sealing, and seed routing."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from .reasoning_pattern_shadow import CONTROLLED_MECHANISMS


PACKET_SCHEMA = "lolla.joint_process_reasoning_packet.v0"
PROJECTION_SCHEMA = "lolla.joint_process_reasoning_projection.v0"
ROUTING_SCHEMA = "lolla.joint_process_reasoning_shadow_routing.v0"
JOINT_STATUSES = {
    "unresolved",
    "resolved_in_conversation",
    "ambiguous",
    "not_observed",
}
_REVIEW_FIELDS = {
    "mechanism_id",
    "joint_status",
    "source_turns",
    "resolution_turns",
}
_NODE_FIELDS = {"mechanism_id", "joint_status"}
_PROJECTION_FIELDS = {
    "schema_version",
    "active_nodes",
    "edge_nodes",
    "manual_review_nodes",
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


class JointProcessReasoningShadowError(ValueError):
    """Raised when a joint-process shadow artifact violates its contract."""


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _signature(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def lint_joint_projection(projection: object) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    if not isinstance(projection, Mapping):
        return [{"code": "projection_not_object", "json_pointer": "/routing_projection"}]
    if set(projection) != _PROJECTION_FIELDS:
        violations.append(
            {"code": "projection_fields_invalid", "json_pointer": "/routing_projection"}
        )
    if projection.get("schema_version") != PROJECTION_SCHEMA:
        violations.append(
            {
                "code": "projection_schema_invalid",
                "json_pointer": "/routing_projection/schema_version",
            }
        )
    if projection.get("contains_case_context") is not False:
        violations.append(
            {
                "code": "case_context_flag_true",
                "json_pointer": "/routing_projection/contains_case_context",
            }
        )
    seen: list[str] = []
    for field, expected_statuses in (
        ("active_nodes", {"unresolved"}),
        ("edge_nodes", {"ambiguous"}),
        ("manual_review_nodes", {"unresolved", "ambiguous"}),
    ):
        nodes = projection.get(field, [])
        if not isinstance(nodes, list):
            violations.append(
                {"code": f"{field}_not_array", "json_pointer": f"/routing_projection/{field}"}
            )
            continue
        for index, node in enumerate(nodes):
            pointer = f"/routing_projection/{field}/{index}"
            if not isinstance(node, Mapping) or set(node) != _NODE_FIELDS:
                violations.append({"code": "routing_node_shape_invalid", "json_pointer": pointer})
                continue
            mechanism = str(node.get("mechanism_id", ""))
            seen.append(mechanism)
            if mechanism not in CONTROLLED_MECHANISMS:
                violations.append(
                    {"code": "mechanism_not_controlled", "json_pointer": pointer + "/mechanism_id"}
                )
            if node.get("joint_status") not in expected_statuses:
                violations.append(
                    {"code": "node_status_wrong_surface", "json_pointer": pointer + "/joint_status"}
                )
    duplicates = [item for item, count in Counter(seen).items() if count > 1]
    if duplicates:
        violations.append(
            {"code": "mechanism_routed_twice", "json_pointer": "/routing_projection"}
        )
    return violations


def seal_joint_process_response(
    response: Mapping[str, Any],
    *,
    packet_id: str,
    source_ref: str,
    source_sha256: str,
    valid_turn_numbers: set[int],
) -> dict[str, Any]:
    if set(response) != {"mechanisms"} or not isinstance(
        response.get("mechanisms"), list
    ):
        raise JointProcessReasoningShadowError(
            "response must contain only a mechanisms array"
        )
    reviews = response["mechanisms"]
    observed_mechanisms: list[str] = []
    normalized: list[dict[str, Any]] = []
    for index, row in enumerate(reviews):
        if not isinstance(row, Mapping) or set(row) != _REVIEW_FIELDS:
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] has invalid shape"
            )
        mechanism = str(row["mechanism_id"])
        status = str(row["joint_status"])
        source_turns = row["source_turns"]
        resolution_turns = row["resolution_turns"]
        if mechanism not in CONTROLLED_MECHANISMS:
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] mechanism is not controlled"
            )
        if status not in JOINT_STATUSES:
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] joint_status is invalid"
            )
        if not isinstance(source_turns, list) or not isinstance(
            resolution_turns, list
        ):
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] turn references must be arrays"
            )
        source_set = {int(turn) for turn in source_turns}
        resolution_set = {int(turn) for turn in resolution_turns}
        if source_set - valid_turn_numbers or resolution_set - valid_turn_numbers:
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] references an unknown turn"
            )
        if status == "not_observed" and (source_set or resolution_set):
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] not_observed must have empty turns"
            )
        if status in {"unresolved", "resolved_in_conversation", "ambiguous"} and not source_set:
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] {status} requires source_turns"
            )
        if status == "resolved_in_conversation" and not resolution_set:
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] resolved status requires resolution_turns"
            )
        if status == "unresolved" and resolution_set:
            raise JointProcessReasoningShadowError(
                f"mechanisms[{index}] unresolved must have empty resolution_turns"
            )
        observed_mechanisms.append(mechanism)
        normalized.append(
            {
                "mechanism_id": mechanism,
                "joint_status": status,
                "source_semantic_item_ids": [
                    f"turn:{turn}" for turn in sorted(source_set)
                ],
                "resolution_semantic_item_ids": [
                    f"turn:{turn}" for turn in sorted(resolution_set)
                ],
            }
        )
    if len(observed_mechanisms) != len(set(observed_mechanisms)):
        raise JointProcessReasoningShadowError("mechanisms contains duplicate IDs")
    if set(observed_mechanisms) != CONTROLLED_MECHANISMS:
        missing = sorted(CONTROLLED_MECHANISMS - set(observed_mechanisms))
        extra = sorted(set(observed_mechanisms) - CONTROLLED_MECHANISMS)
        raise JointProcessReasoningShadowError(
            f"mechanisms must cover controlled vocabulary exactly; missing={missing}, extra={extra}"
        )
    normalized.sort(key=lambda item: item["mechanism_id"])
    active_nodes = [
        {"mechanism_id": item["mechanism_id"], "joint_status": "unresolved"}
        for item in normalized
        if item["joint_status"] == "unresolved"
        and item["mechanism_id"] != "other_review_required"
    ]
    edge_nodes = [
        {"mechanism_id": item["mechanism_id"], "joint_status": "ambiguous"}
        for item in normalized
        if item["joint_status"] == "ambiguous"
        and item["mechanism_id"] != "other_review_required"
    ]
    manual_review_nodes = [
        {
            "mechanism_id": item["mechanism_id"],
            "joint_status": item["joint_status"],
        }
        for item in normalized
        if item["mechanism_id"] == "other_review_required"
        and item["joint_status"] in {"unresolved", "ambiguous"}
    ]
    projection = {
        "schema_version": PROJECTION_SCHEMA,
        "active_nodes": active_nodes,
        "edge_nodes": edge_nodes,
        "manual_review_nodes": manual_review_nodes,
        "contains_case_context": False,
    }
    violations = lint_joint_projection(projection)
    if violations:
        raise JointProcessReasoningShadowError(
            "sealed joint-process projection failed deterministic lint"
        )
    return {
        "schema_version": PACKET_SCHEMA,
        "packet_metadata": {
            "packet_id": f"joint_process_reasoning_packet:{packet_id}",
            "target": "unresolved_joint_conversation_trajectory",
            "graph_runtime_modified": False,
        },
        "provenance": {
            "source_interpretation_ref": source_ref,
            "source_interpretation_sha256": source_sha256,
            "raw_text_included": False,
        },
        "mechanism_reviews": normalized,
        "routing_projection": projection,
        "fact_boundary": dict(_FACT_BOUNDARY),
        "lint": {"status": "passed", "violations": []},
        "non_claims": [
            "mechanism_reviews_are_probabilistic_interpretations",
            "resolved_does_not_mean_never_present",
            "ambiguous_is_preserved_not_erased",
            "not_graph_applicability",
            "not_reasoning_quality_proof",
            "not_runtime_integration_authority",
        ],
    }


def normalized_joint_projection_signature(packet: Mapping[str, Any]) -> str:
    projection = packet.get("routing_projection", {})
    if lint_joint_projection(projection):
        raise JointProcessReasoningShadowError("cannot sign invalid projection")
    return _signature(projection)


def route_joint_projection(
    packet: Mapping[str, Any],
    *,
    routing_contract: Mapping[str, Any],
    known_model_ids: set[str],
) -> dict[str, Any]:
    projection = packet.get("routing_projection", {})
    if lint_joint_projection(projection):
        raise JointProcessReasoningShadowError("routing projection is invalid")
    if routing_contract.get("status") != "research_only_runtime_dormant":
        raise JointProcessReasoningShadowError("routing contract is not research-only")
    mapping = routing_contract.get("mechanism_seed_models", {})
    if not isinstance(mapping, Mapping):
        raise JointProcessReasoningShadowError("mechanism_seed_models must be an object")

    def candidates(nodes: object) -> list[dict[str, Any]]:
        pulls: dict[str, set[str]] = {}
        for node in nodes if isinstance(nodes, Sequence) else []:
            mechanism = str(node["mechanism_id"])
            seeds = mapping.get(mechanism, [])
            if not isinstance(seeds, Sequence) or isinstance(seeds, (str, bytes)):
                raise JointProcessReasoningShadowError(
                    f"seed mapping is invalid: {mechanism}"
                )
            for model_id in seeds:
                model = str(model_id)
                if model not in known_model_ids:
                    raise JointProcessReasoningShadowError(
                        f"seed model is unknown: {model}"
                    )
                pulls.setdefault(model, set()).add(mechanism)
        return [
            {"model_id": model, "pulled_by_mechanisms": sorted(mechanisms)}
            for model, mechanisms in sorted(pulls.items())
        ]

    active_candidates = candidates(projection.get("active_nodes", []))
    edge_candidates = candidates(projection.get("edge_nodes", []))
    return {
        "schema_version": ROUTING_SCHEMA,
        "status": "research_only",
        "projection_signature": normalized_joint_projection_signature(packet),
        "active_seed_candidates": active_candidates,
        "edge_reserve_candidates": edge_candidates,
        "active_candidate_count": len(active_candidates),
        "edge_candidate_count": len(edge_candidates),
        "manual_review_required": bool(projection.get("manual_review_nodes", [])),
        "graph_runtime_modified": False,
        "semantic_applicability_validated": False,
        "non_claims": [
            "active_seed_recall_is_not_applicability",
            "edge_reserve_is_not_public_pressure",
            "fixture_behavior_is_not_production_stability",
            "not_runtime_integration_authority",
        ],
    }
