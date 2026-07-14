"""Quiet-capable role-record to fact-free mechanism interpreter."""
from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from .reasoning_mechanism_ontology import JOINT_STATUSES, MECHANISMS, ontology_packet
from .reasoning_pattern_role_record_interpreter import (
    RoleRecordPatternError,
    _canonical,
    _sha,
    normalize_role_observation,
)
from .reasoning_pattern_role_record_interpreter_v2 import ALL_STATES, ROUTING_STATES, response_schema_v2
from .reasoning_pattern_shadow import PACKET_SCHEMA, PROJECTION_SCHEMA, lint_routing_projection


INPUT_SCHEMA = "lolla.reasoning_pattern_role_record_input.v3"
OUTPUT_SCHEMA = "lolla.reasoning_pattern_role_record_response.v3"
QUALIFICATION_OUTCOMES = {
    "unresolved_qualification_present",
    "no_unresolved_qualification_observed",
    "ambiguous_qualification_review",
}


def build_input_v3(
    *,
    case_id: str,
    arm_id: str,
    joined: Mapping[str, Any],
    source_refs: list[dict[str, str]],
) -> dict[str, Any]:
    roles = joined.get("role_observations", {})
    starting, current, qualification = roles.get("starting"), roles.get("current"), roles.get("qualification")
    if not isinstance(starting, Mapping) or not isinstance(current, Mapping):
        raise RoleRecordPatternError("v3 input requires starting and current observations")
    records = [normalize_role_observation(starting), normalize_role_observation(current)]
    if qualification is not None:
        if not isinstance(qualification, Mapping):
            raise RoleRecordPatternError("v3 qualification observation is invalid")
        records.append(normalize_role_observation(qualification))
    review = joined.get("qualification_review")
    if not isinstance(review, Mapping) or review.get("outcome") not in QUALIFICATION_OUTCOMES:
        raise RoleRecordPatternError("v3 qualification review is invalid")
    evidence_ids = [str(value) for value in review.get("evidence_ids", [])]
    if not evidence_ids or len(evidence_ids) != len(set(evidence_ids)):
        raise RoleRecordPatternError("v3 qualification review custody is invalid")
    normalized_review = {
        "outcome": str(review["outcome"]),
        "evidence_ids": evidence_ids,
        "interpretation": str(review.get("interpretation", "")),
        "limitations": str(review.get("limitations", "")),
    }
    if not normalized_review["interpretation"]:
        raise RoleRecordPatternError("v3 qualification review interpretation is empty")
    if normalized_review["outcome"] == "unresolved_qualification_present" and len(records) != 3:
        raise RoleRecordPatternError("v3 unresolved review lacks qualification record")
    if normalized_review["outcome"] == "no_unresolved_qualification_observed" and len(records) != 2:
        raise RoleRecordPatternError("v3 negative review conflicts with qualification record")
    packet = {
        "schema_version": INPUT_SCHEMA,
        "case_id": case_id,
        "arm_id": arm_id,
        "source_refs": source_refs,
        "role_records": records,
        "qualification_review": normalized_review,
        "controlled_mechanisms": sorted(MECHANISMS),
        "ablation": {"active": False, "kind": "none", "note": ""},
        "boundary": {
            "raw_conversation_included": False,
            "source_evidence_text_included": False,
            "review_evidence_aliases_included_for_custody": True,
            "role_semantic_prose_included_for_interpretation": True,
            "qualification_review_semantic_prose_included": True,
            "negative_review_is_not_a_deterministic_veto": True,
            "graph_model_names_included": False,
            "expected_patterns_included": False,
            "deterministic_semantic_mapping": False,
            "graph_runtime_effect": "none",
        },
    }
    packet["packet_sha256"] = _sha(packet)
    return packet


def validate_input_v3(packet: Mapping[str, Any]) -> None:
    if packet.get("schema_version") != INPUT_SCHEMA:
        raise RoleRecordPatternError("invalid v3 role-record input")
    supplied_hash = packet.get("packet_sha256")
    unhashed = {key: value for key, value in packet.items() if key != "packet_sha256"}
    if supplied_hash != _sha(unhashed):
        raise RoleRecordPatternError("v3 role-record input hash drifted")
    records = packet.get("role_records")
    if not isinstance(records, list) or len(records) not in {2, 3}:
        raise RoleRecordPatternError("v3 role count is invalid")
    expected_roles = ["starting", "current"] + (["qualification"] if len(records) == 3 else [])
    if [record.get("role") for record in records] != expected_roles:
        raise RoleRecordPatternError("v3 role order drifted")
    review = packet.get("qualification_review", {})
    if review.get("outcome") == "no_unresolved_qualification_observed" and len(records) != 2:
        raise RoleRecordPatternError("v3 negative review role count conflicts")
    if review.get("outcome") == "unresolved_qualification_present" and len(records) != 3:
        raise RoleRecordPatternError("v3 present review role count conflicts")


def build_prompts_v3(packet: Mapping[str, Any]) -> dict[str, str]:
    validate_input_v3(packet)
    system = (
        "You assess the final joint reasoning trajectory, not isolated actor mistakes. "
        "Review every mechanism exactly once using its operational definition, requirements, "
        "exclusions, and near-neighbor distinction. Case topic similarity is irrelevant. "
        "A provider-authored negative qualification review is evidence about the endpoint, not a veto; "
        "still require positive support before calling any weakness unresolved."
    )
    user = (
        "ONTOLOGY\n" + _canonical(ontology_packet()).decode("utf-8")
        + "\n\nQUIET-CAPABLE ROLE RECORDS\n" + _canonical(packet).decode("utf-8")
        + "\n\nReturn exactly nine assessments, one for every mechanism_id and no duplicates. "
        "Use unresolved only when the weakness remains operative after the current position and "
        "qualification review. An adopted safeguard, gate, fallback, stop rule, or review condition "
        "is evidence of integration, not itself an unresolved qualification. Do not infer a weakness "
        "from starting-position concern when current reasoning integrated it. Use resolved_in_conversation "
        "only when the bounded records positively show a mechanism that was later repaired; otherwise use "
        "not_observed. unresolved requires present or missing_protection and exact role_record_ids. ambiguous "
        "requires tension and exact role_record_ids. resolved_in_conversation requires not_applicable and exact "
        "role_record_ids. not_observed requires not_applicable and an empty ID list. Do not output rationale, "
        "case prose, or mental-model names. Exhaustive review is not an instruction to find weaknesses."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
    }


def compile_response_v3(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
) -> dict[str, Any]:
    validate_input_v3(packet)
    rows = response.get("assessments")
    if set(response) != {"assessments"} or not isinstance(rows, list) or len(rows) != len(MECHANISMS):
        raise RoleRecordPatternError("v3 response must contain exactly nine assessments")
    valid_ids = {item["role_record_id"] for item in packet["role_records"]}
    seen: set[str] = set()
    hypotheses: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    for row in rows:
        fields = {"mechanism_id", "joint_status", "pattern_state", "source_role_record_ids"}
        if not isinstance(row, Mapping) or set(row) != fields:
            raise RoleRecordPatternError("v3 assessment fields are invalid")
        mechanism, status, state = row["mechanism_id"], row["joint_status"], row["pattern_state"]
        ids = row["source_role_record_ids"]
        if mechanism not in MECHANISMS or mechanism in seen or status not in JOINT_STATUSES or state not in ALL_STATES:
            raise RoleRecordPatternError("v3 assessment ontology identity is invalid")
        seen.add(mechanism)
        if not isinstance(ids, list) or len(ids) > 3 or len(ids) != len(set(ids)) or set(ids) - valid_ids:
            raise RoleRecordPatternError("v3 assessment role-record custody is invalid")
        if status == "unresolved" and (state not in ROUTING_STATES or not ids):
            raise RoleRecordPatternError("v3 unresolved assessment contract is invalid")
        if status == "ambiguous" and (state != "tension" or not ids):
            raise RoleRecordPatternError("v3 ambiguous assessment contract is invalid")
        if status == "resolved_in_conversation" and (state != "not_applicable" or not ids):
            raise RoleRecordPatternError("v3 resolved assessment contract is invalid")
        if status == "not_observed" and (state != "not_applicable" or ids):
            raise RoleRecordPatternError("v3 not-observed assessment contract is invalid")
        pattern_id = f"rp_{len(hypotheses)+1:03d}"
        eligible = status == "unresolved"
        hypotheses.append({"pattern_id": pattern_id, "mechanism_id": mechanism, "subject_scope": "joint_process", "state": state if eligible else ("tension" if status == "ambiguous" else "present"), "support_status": status, "routing_eligible": eligible})
        sources.append({"pattern_id": pattern_id, "source_semantic_item_ids": sorted(ids)})
        if eligible:
            nodes.append({"pattern_id": pattern_id, "mechanism_id": mechanism, "subject_scope": "joint_process", "state": state})
    if seen != set(MECHANISMS):
        raise RoleRecordPatternError("v3 assessment mechanism coverage is incomplete")
    projection = {"schema_version": PROJECTION_SCHEMA, "pattern_nodes": nodes, "pattern_edges": [], "contains_case_context": False}
    violations = lint_routing_projection(projection)
    if violations:
        raise RoleRecordPatternError("v3 projection failed fact-leak lint")
    return {
        "schema_version": PACKET_SCHEMA,
        "packet_metadata": {"packet_id": f"reasoning_pattern_packet:{packet['arm_id']}:v3", "interpretation_schema_version": OUTPUT_SCHEMA, "graph_runtime_modified": False},
        "provenance": {"source_role_record_packet_sha256": packet["packet_sha256"], "pattern_sources": sources, "producer_kind": producer_kind, "producer_id": producer_id, "raw_role_record_prose_in_routing_projection": False, "qualification_review_outcome": packet["qualification_review"]["outcome"]},
        "pattern_hypotheses": hypotheses,
        "routing_projection": projection,
        "fact_boundary": {"raw_text_included": False, "quotes_included": False, "entities_included": False, "case_quantities_included": False, "dates_included": False, "desired_outcome_included": False, "topic_labels_included": False},
        "lint": {"status": "passed", "violations": []},
        "non_claims": ["probabilistic_semantic_assessment", "negative_review_is_not_deterministic_veto", "not_reasoning_quality_proof", "not_runtime_integration_authority"],
    }


__all__ = [
    "build_input_v3",
    "build_prompts_v3",
    "compile_response_v3",
    "response_schema_v2",
    "validate_input_v3",
]
