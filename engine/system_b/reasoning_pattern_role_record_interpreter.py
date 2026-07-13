"""Research-only role-record to fact-free reasoning-pattern interpreter contract."""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .reasoning_pattern_shadow import (
    CONTROLLED_MECHANISMS, PACKET_SCHEMA, PATTERN_STATES, PROJECTION_SCHEMA,
    SUBJECT_SCOPES, lint_routing_projection,
)

INPUT_SCHEMA = "lolla.reasoning_pattern_role_record_input.v1"
OUTPUT_SCHEMA = "lolla.reasoning_pattern_role_record_response.v1"
ROLE_ORDER = ("starting", "current", "qualification")
RECORD_FIELDS = {
    "role_record_id", "role", "semantic_status", "role_interpretation",
    "evidence_ids", "stance_components", "fidelity_note", "limitations",
}
COMPONENT_FIELDS = {
    "stance_object_kind", "stance_object_interpretation",
    "stance_expression_kind", "source_evidence_id",
}


class RoleRecordPatternError(ValueError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def normalize_role_observation(observation: Mapping[str, Any]) -> dict[str, Any]:
    role = str(observation.get("role", ""))
    record_id = str(observation.get("role_record_id", ""))
    if role not in ROLE_ORDER or not record_id:
        raise RoleRecordPatternError("role observation identity is invalid")
    components = []
    for item in observation.get("stance_components", []):
        component = {field: item.get(field) for field in COMPONENT_FIELDS}
        if set(component) != COMPONENT_FIELDS or not all(isinstance(value, str) and value for value in component.values()):
            raise RoleRecordPatternError("role observation component is invalid")
        components.append(component)
    if not components:
        raise RoleRecordPatternError("role observation must contain components")
    record = {
        "role_record_id": record_id,
        "role": role,
        "semantic_status": str(observation.get("semantic_status", "")),
        "role_interpretation": str(observation.get("role_interpretation", "")),
        "evidence_ids": [
            str(value)
            for value in observation.get("source_evidence_ids", observation.get("evidence_ids", []))
        ],
        "stance_components": components,
        "fidelity_note": str(observation.get("fidelity_note", "")),
        "limitations": str(observation.get("limitations", "")),
    }
    if set(record) != RECORD_FIELDS or not record["role_interpretation"] or not record["evidence_ids"]:
        raise RoleRecordPatternError("normalized role record is invalid")
    if any(component["source_evidence_id"] not in record["evidence_ids"] for component in components):
        raise RoleRecordPatternError("component alias is not in parent evidence")
    return record


def build_role_record_pattern_input(*, case_id: str, arm_id: str, records: list[Mapping[str, Any]], source_refs: list[dict[str, str]], ablation: Mapping[str, Any] | None = None) -> dict[str, Any]:
    normalized = [normalize_role_observation(item) for item in records]
    if len(normalized) != 3 or [item["role"] for item in normalized] != list(ROLE_ORDER):
        raise RoleRecordPatternError("exactly one ordered record per role is required")
    if len({item["role_record_id"] for item in normalized}) != 3:
        raise RoleRecordPatternError("role record IDs must be unique")
    packet = {
        "schema_version": INPUT_SCHEMA,
        "case_id": case_id,
        "arm_id": arm_id,
        "source_refs": source_refs,
        "role_records": normalized,
        "controlled_mechanisms": sorted(CONTROLLED_MECHANISMS),
        "subject_scopes": sorted(SUBJECT_SCOPES),
        "pattern_states": sorted(PATTERN_STATES),
        "ablation": dict(ablation or {"active": False, "kind": "none", "note": ""}),
        "boundary": {
            "raw_conversation_included": False,
            "source_evidence_text_included": False,
            "evidence_aliases_included_for_custody": True,
            "role_semantic_prose_included_for_interpretation": True,
            "graph_model_names_included": False,
            "expected_patterns_included": False,
            "deterministic_semantic_mapping": False,
            "maximum_patterns": 6,
            "graph_runtime_effect": "none",
        },
    }
    packet["packet_sha256"] = _sha(packet)
    return packet


def role_record_pattern_response_schema() -> dict[str, Any]:
    item = {
        "type": "object",
        "properties": {
            "mechanism_id": {"type": "string", "enum": sorted(CONTROLLED_MECHANISMS)},
            "subject_scope": {"type": "string", "enum": sorted(SUBJECT_SCOPES)},
            "state": {"type": "string", "enum": sorted(PATTERN_STATES)},
            "source_role_record_ids": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"type": "string", "minLength": 1, "maxLength": 120}},
        },
        "required": ["mechanism_id", "subject_scope", "state", "source_role_record_ids"],
        "additionalProperties": False,
    }
    return {"type": "object", "properties": {"patterns": {"type": "array", "minItems": 0, "maxItems": 6, "items": item}}, "required": ["patterns"], "additionalProperties": False}


def build_role_record_pattern_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    validate_role_record_pattern_input(packet)
    system = (
        "You identify abstract reasoning mechanisms from source-linked position-role records. "
        "Ignore industries, people, entities, quantities, desired outcomes, and topic similarity. "
        "Use only the controlled mechanism vocabulary. Return no rationale or case prose."
    )
    user = (
        "ROLE-RECORD PACKET\n" + _canonical(packet).decode("utf-8")
        + "\n\nReturn exactly {\"patterns\":[...]}. Each pattern has mechanism_id, subject_scope, "
        "state, and source_role_record_ids. Cite only exact IDs from the packet. Include a mechanism "
        "only when the records support it. Missing means not observed in these records, not absent in "
        "reality. Use other_review_required only for a supported mechanism outside the vocabulary; it "
        "will not route. Inspect all three roles. Return at most six patterns and no free text."
    )
    return {"system_prompt": system, "user_prompt": user, "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(), "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest()}


def validate_role_record_pattern_input(packet: Mapping[str, Any]) -> None:
    if packet.get("schema_version") != INPUT_SCHEMA:
        raise RoleRecordPatternError("invalid role-record pattern input")
    supplied_hash = packet.get("packet_sha256")
    unhashed = {key: value for key, value in packet.items() if key != "packet_sha256"}
    if supplied_hash != _sha(unhashed):
        raise RoleRecordPatternError("role-record pattern input hash drifted")
    records = packet.get("role_records")
    if not isinstance(records, list) or len(records) != 3:
        raise RoleRecordPatternError("role-record pattern input roles are invalid")
    if [item.get("role") for item in records] != list(ROLE_ORDER):
        raise RoleRecordPatternError("role-record pattern input role order drifted")
    if len({item.get("role_record_id") for item in records}) != 3:
        raise RoleRecordPatternError("role-record pattern input role IDs are invalid")


def compile_role_record_pattern_response(*, response: Mapping[str, Any], packet: Mapping[str, Any], producer_kind: str, producer_id: str, call_metadata: Mapping[str, str] | None = None) -> dict[str, Any]:
    validate_role_record_pattern_input(packet)
    if set(response) != {"patterns"} or not isinstance(response.get("patterns"), list) or len(response["patterns"]) > 6:
        raise RoleRecordPatternError("response must contain only a bounded patterns array")
    valid_ids = {item["role_record_id"] for item in packet["role_records"]}
    merged: dict[tuple[str, str, str], set[str]] = {}
    raw_hashes = []
    for index, item in enumerate(response["patterns"]):
        fields = {"mechanism_id", "subject_scope", "state", "source_role_record_ids"}
        if not isinstance(item, Mapping) or set(item) != fields:
            raise RoleRecordPatternError(f"patterns[{index}] fields are invalid")
        mechanism, scope, state = str(item["mechanism_id"]), str(item["subject_scope"]), str(item["state"])
        ids = item["source_role_record_ids"]
        if mechanism not in CONTROLLED_MECHANISMS or scope not in SUBJECT_SCOPES or state not in PATTERN_STATES:
            raise RoleRecordPatternError(f"patterns[{index}] enum is invalid")
        if not isinstance(ids, list) or not ids or len(ids) > 3 or set(ids) - valid_ids:
            raise RoleRecordPatternError(f"patterns[{index}] role record custody is invalid")
        merged.setdefault((mechanism, scope, state), set()).update(str(value) for value in ids)
        raw_hashes.append("sha256:" + _sha(item))
    hypotheses, sources, nodes = [], [], []
    for ordinal, ((mechanism, scope, state), ids) in enumerate(sorted(merged.items()), 1):
        pattern_id = f"rp_{ordinal:03d}"
        eligible = mechanism != "other_review_required"
        hypotheses.append({"pattern_id": pattern_id, "mechanism_id": mechanism, "subject_scope": scope, "state": state, "support_status": "provisional_role_record_linked", "routing_eligible": eligible})
        sources.append({"pattern_id": pattern_id, "source_semantic_item_ids": sorted(ids)})
        if eligible:
            nodes.append({"pattern_id": pattern_id, "mechanism_id": mechanism, "subject_scope": scope, "state": state})
    projection = {"schema_version": PROJECTION_SCHEMA, "pattern_nodes": nodes, "pattern_edges": [], "contains_case_context": False}
    violations = lint_routing_projection(projection)
    if violations:
        raise RoleRecordPatternError("sealed role-record projection failed fact-leak lint")
    return {
        "schema_version": PACKET_SCHEMA,
        "packet_metadata": {"packet_id": f"reasoning_pattern_packet:{packet['arm_id']}", "interpretation_schema_version": OUTPUT_SCHEMA, "graph_runtime_modified": False},
        "provenance": {"source_role_record_packet_sha256": packet["packet_sha256"], "pattern_sources": sources, "raw_role_record_prose_in_routing_projection": False, "producer_kind": producer_kind, "producer_id": producer_id, "call_id": (call_metadata or {}).get("call_id", ""), "model": (call_metadata or {}).get("model", ""), "prompt_sha256": (call_metadata or {}).get("prompt_sha256", ""), "raw_pattern_hashes": raw_hashes},
        "pattern_hypotheses": hypotheses,
        "routing_projection": projection,
        "fact_boundary": {"raw_text_included": False, "quotes_included": False, "entities_included": False, "case_quantities_included": False, "dates_included": False, "desired_outcome_included": False, "topic_labels_included": False},
        "lint": {"status": "passed", "violations": []},
        "non_claims": ["patterns_are_probabilistic_hypotheses", "not_human_validation", "not_reasoning_quality_proof", "not_advice_correctness_proof", "not_runtime_integration_authority"],
    }
