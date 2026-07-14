"""Ontology-guided, research-only joint-process pattern interpreter."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_mechanism_ontology import JOINT_STATUSES, MECHANISMS, ontology_packet
from .reasoning_pattern_role_record_interpreter import (
    RoleRecordPatternError, _canonical, _sha, validate_role_record_pattern_input,
)
from .reasoning_pattern_shadow import PACKET_SCHEMA, PROJECTION_SCHEMA, lint_routing_projection

OUTPUT_SCHEMA = "lolla.reasoning_pattern_role_record_response.v2"
ROUTING_STATES = {"present", "missing_protection"}
ALL_STATES = ROUTING_STATES | {"tension", "not_applicable"}


def response_schema_v2() -> dict[str, Any]:
    row = {
        "type": "object",
        "properties": {
            "mechanism_id": {"type": "string", "enum": sorted(MECHANISMS)},
            "joint_status": {"type": "string", "enum": sorted(JOINT_STATUSES)},
            "pattern_state": {"type": "string", "enum": sorted(ALL_STATES)},
            "source_role_record_ids": {"type": "array", "minItems": 0, "maxItems": 3, "items": {"type": "string", "minLength": 1, "maxLength": 120}},
        },
        "required": ["mechanism_id", "joint_status", "pattern_state", "source_role_record_ids"],
        "additionalProperties": False,
    }
    return {"type": "object", "properties": {"assessments": {"type": "array", "minItems": 9, "maxItems": 9, "items": row}}, "required": ["assessments"], "additionalProperties": False}


def build_prompts_v2(packet: Mapping[str, Any]) -> dict[str, str]:
    validate_role_record_pattern_input(packet)
    system = (
        "You assess the final joint reasoning trajectory, not isolated actor mistakes. "
        "Review every mechanism exactly once using its operational definition, requirements, "
        "exclusions, and near-neighbor distinction. Case topic similarity is irrelevant."
    )
    user = (
        "ONTOLOGY\n" + _canonical(ontology_packet()).decode("utf-8")
        + "\n\nROLE RECORDS\n" + _canonical(packet).decode("utf-8")
        + "\n\nReturn exactly nine assessments, one for every mechanism_id and no duplicates. "
        "Use unresolved only when the weakness remains operative after the latest captured reasoning; "
        "resolved_in_conversation when later reasoning repaired it; ambiguous for genuinely competing "
        "readings; otherwise not_observed. unresolved requires present or missing_protection. ambiguous "
        "requires tension. resolved_in_conversation or not_observed requires not_applicable. Cite exact "
        "role_record_ids that support unresolved, resolved, or ambiguous; not_observed uses an empty list. "
        "Do not output rationale, case prose, user/assistant blame, or mental-model names. The nine-row "
        "requirement is exhaustive review, not an instruction to find nine weaknesses."
    )
    import hashlib
    return {"system_prompt": system, "user_prompt": user, "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(), "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest()}


def compile_response_v2(*, response: Mapping[str, Any], packet: Mapping[str, Any], producer_kind: str, producer_id: str) -> dict[str, Any]:
    validate_role_record_pattern_input(packet)
    rows = response.get("assessments")
    if set(response) != {"assessments"} or not isinstance(rows, list) or len(rows) != len(MECHANISMS):
        raise RoleRecordPatternError("response must contain exactly nine assessments")
    valid_ids = {item["role_record_id"] for item in packet["role_records"]}
    seen, hypotheses, sources, nodes = set(), [], [], []
    for row in rows:
        fields = {"mechanism_id", "joint_status", "pattern_state", "source_role_record_ids"}
        if not isinstance(row, Mapping) or set(row) != fields:
            raise RoleRecordPatternError("assessment fields are invalid")
        mechanism, status, state = row["mechanism_id"], row["joint_status"], row["pattern_state"]
        ids = row["source_role_record_ids"]
        if mechanism not in MECHANISMS or mechanism in seen or status not in JOINT_STATUSES or state not in ALL_STATES:
            raise RoleRecordPatternError("assessment ontology identity is invalid")
        seen.add(mechanism)
        if not isinstance(ids, list) or len(ids) > 3 or len(ids) != len(set(ids)) or set(ids) - valid_ids:
            raise RoleRecordPatternError("assessment role-record custody is invalid")
        if status == "unresolved" and (state not in ROUTING_STATES or not ids):
            raise RoleRecordPatternError("unresolved assessment contract is invalid")
        if status == "ambiguous" and (state != "tension" or not ids):
            raise RoleRecordPatternError("ambiguous assessment contract is invalid")
        if status in {"resolved_in_conversation"} and (state != "not_applicable" or not ids):
            raise RoleRecordPatternError("resolved assessment contract is invalid")
        if status == "not_observed" and (state != "not_applicable" or ids):
            raise RoleRecordPatternError("not-observed assessment contract is invalid")
        pattern_id = f"rp_{len(hypotheses)+1:03d}"
        eligible = status == "unresolved"
        hypotheses.append({"pattern_id": pattern_id, "mechanism_id": mechanism, "subject_scope": "joint_process", "state": state if eligible else ("tension" if status == "ambiguous" else "present"), "support_status": status, "routing_eligible": eligible})
        sources.append({"pattern_id": pattern_id, "source_semantic_item_ids": sorted(ids)})
        if eligible:
            nodes.append({"pattern_id": pattern_id, "mechanism_id": mechanism, "subject_scope": "joint_process", "state": state})
    if seen != set(MECHANISMS):
        raise RoleRecordPatternError("assessment mechanism coverage is incomplete")
    projection = {"schema_version": PROJECTION_SCHEMA, "pattern_nodes": nodes, "pattern_edges": [], "contains_case_context": False}
    violations = lint_routing_projection(projection)
    if violations:
        raise RoleRecordPatternError("v2 projection failed fact-leak lint")
    return {
        "schema_version": PACKET_SCHEMA,
        "packet_metadata": {"packet_id": f"reasoning_pattern_packet:{packet['arm_id']}:v2", "interpretation_schema_version": OUTPUT_SCHEMA, "graph_runtime_modified": False},
        "provenance": {"source_role_record_packet_sha256": packet["packet_sha256"], "pattern_sources": sources, "producer_kind": producer_kind, "producer_id": producer_id, "raw_role_record_prose_in_routing_projection": False},
        "pattern_hypotheses": hypotheses, "routing_projection": projection,
        "fact_boundary": {"raw_text_included": False, "quotes_included": False, "entities_included": False, "case_quantities_included": False, "dates_included": False, "desired_outcome_included": False, "topic_labels_included": False},
        "lint": {"status": "passed", "violations": []},
        "non_claims": ["probabilistic_semantic_assessment", "bounded_capture_only", "not_reasoning_quality_proof", "not_runtime_integration_authority"],
    }
