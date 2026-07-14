"""Nested-component wire for the role-first v2.1 semantic contract.

V2.2 changes only the role response wire: each stance component is one object
containing its kind, interpretation, expression, and exact source alias. This
removes ambiguous parallel-array alignment. Relation schemas, semantic prompt
meaning, deterministic custody boundaries, and call ceilings remain unchanged.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_chronological_shard_reader_v4 import (
    STANCE_EXPRESSION_KINDS,
    STANCE_OBJECT_KINDS,
)
from .reasoning_process_position_decomposition_v1 import ROLE_COMPONENT_LIMITS
from .reasoning_process_position_role_first_v2 import (
    ITEM_STATUSES,
    RESPONSE_STATUSES,
    ROLE_OBSERVATION_SCHEMA,
    ROLE_ORDER,
    ROLE_PACKET_SCHEMA,
    ROLE_RESPONSE_SCHEMA,
    _validate_role_record_v2,
)
from .reasoning_process_position_role_first_v21 import (
    RELATION_PACKET_SCHEMA_V21,
    build_position_relation_packet_v21,
    build_position_relation_prompts_v21,
    build_position_role_packet_v21,
    compile_position_relation_response_v21,
    join_position_role_first_v21,
    position_relation_response_schema_v21,
)
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

ROLE_PACKET_SCHEMA_V22 = "lolla.reasoning_process_position_role_packet.v2_2"
ROLE_COMPONENT_FIELDS_V22 = {
    "object_kind",
    "object_interpretation",
    "expression_kind",
    "source_evidence_id",
}


def build_position_role_packet_v22(
    *, wrapper: Mapping[str, Any], role: str
) -> dict[str, Any]:
    packet = build_position_role_packet_v21(wrapper=wrapper, role=role)
    packet["schema_version"] = ROLE_PACKET_SCHEMA_V22
    packet["component_identity_contract"] = (
        "Return stance_components as one array. Each array item is one atomic component object whose "
        "object kind, object interpretation, expression kind, and one source alias belong together. "
        "Never return parallel component columns and never combine two source aliases in one component."
    )
    packet["boundary"].update(
        {
            "semantic_contract_changed_from_v21": False,
            "role_response_wire_changed_from_v21": True,
            "parallel_component_columns_used": False,
        }
    )
    return packet


def position_role_response_schema_v22(role: str) -> dict[str, Any]:
    if role not in ROLE_ORDER:
        raise ViewSpecificInterfaceError("unsupported position role")
    component_properties = {
        "object_kind": {"type": "string", "enum": list(STANCE_OBJECT_KINDS)},
        "object_interpretation": {"type": "string", "minLength": 1, "maxLength": 300},
        "expression_kind": {"type": "string", "enum": list(STANCE_EXPRESSION_KINDS)},
        "source_evidence_id": {"type": "string", "pattern": "^e[0-9]{3}$"},
    }
    record_properties = {
        "role": {"type": "string", "enum": [role]},
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "evidence_ids": {
            "type": "array",
            "minItems": 1,
            "maxItems": 6,
            "items": {"type": "string", "pattern": "^e[0-9]{3}$"},
        },
        "role_interpretation": {"type": "string", "minLength": 1, "maxLength": 500},
        "stance_components": {
            "type": "array",
            "minItems": 1,
            "maxItems": ROLE_COMPONENT_LIMITS[role],
            "description": "Atomic source-linked components; all attributes in one item belong together.",
            "items": {
                "type": "object",
                "properties": component_properties,
                "required": list(component_properties),
                "additionalProperties": False,
            },
        },
        "fidelity_note": {"type": "string", "minLength": 1, "maxLength": 800},
        "limitations": {"type": "string", "maxLength": 500},
    }
    return {
        "type": "object",
        "description": f"At most two coherent {role} role records with nested atomic components.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 2,
                "items": {
                    "type": "object",
                    "properties": record_properties,
                    "required": list(record_properties),
                    "additionalProperties": False,
                },
            },
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": ["status", "records", "global_limitations"],
        "additionalProperties": False,
    }


def build_position_role_prompts_v22(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA_V22 or packet.get("role") not in ROLE_ORDER:
        raise ViewSpecificInterfaceError("invalid v2.2 position role packet")
    system_prompt = (
        "You extract one assigned semantic role from a chronological endpoint-comparison shard. "
        "Use only visible evidence aliases and preserve speaker ownership. One record is one coherent "
        "position thread. Each stance_components item is one atomic object-expression-source unit. "
        "Return JSON matching the supplied schema."
    )
    user_prompt = (
        "Single-role packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nFollow every packet contract exactly. A belief is not a decision, and a proposal is not "
        "acceptance of its outcome.\nQuestion: "
        + str(packet["question"])
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def _parallel_projection(record: Mapping[str, Any]) -> dict[str, Any]:
    fields = {
        "role",
        "status",
        "evidence_ids",
        "role_interpretation",
        "stance_components",
        "fidelity_note",
        "limitations",
    }
    if set(record) != fields:
        raise ViewSpecificInterfaceError("v2.2 role record fields do not match contract")
    components = record.get("stance_components")
    if not isinstance(components, list):
        raise ViewSpecificInterfaceError("v2.2 stance_components must be an array")
    for component in components:
        if not isinstance(component, Mapping) or set(component) != ROLE_COMPONENT_FIELDS_V22:
            raise ViewSpecificInterfaceError("v2.2 stance component fields do not match contract")
    return {
        "role": record["role"],
        "status": record["status"],
        "evidence_ids": record["evidence_ids"],
        "role_interpretation": record["role_interpretation"],
        "object_kinds": [item["object_kind"] for item in components],
        "object_interpretations": [item["object_interpretation"] for item in components],
        "expression_kinds": [item["expression_kind"] for item in components],
        "source_evidence_ids": [item["source_evidence_id"] for item in components],
        "fidelity_note": record["fidelity_note"],
        "limitations": record["limitations"],
    }


def compile_position_role_response_v22(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA_V22:
        raise ViewSpecificInterfaceError("invalid v2.2 position role packet")
    if set(response) != {"status", "records", "global_limitations"}:
        raise ViewSpecificInterfaceError("v2.2 role response envelope fields do not match")
    status = response.get("status")
    records = response.get("records")
    if status not in RESPONSE_STATUSES:
        raise ViewSpecificInterfaceError("v2.2 role response status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("v2.2 role response records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("v2.2 not_found response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("v2.2 non-empty status requires records")
    if not isinstance(response.get("global_limitations"), str) or len(response["global_limitations"]) > 700:
        raise ViewSpecificInterfaceError("v2.2 role global limitations are invalid")
    validation_packet = dict(packet)
    validation_packet["schema_version"] = ROLE_PACKET_SCHEMA
    observations = []
    custody = []
    for index, record in enumerate(records, 1):
        digest = sha256_bytes(canonical_json_bytes(record))
        try:
            if not isinstance(record, Mapping):
                raise ViewSpecificInterfaceError("v2.2 role record must be an object")
            projected = _parallel_projection(record)
            validated = _validate_role_record_v2(
                record=projected, packet=validation_packet
            )
            record_id = f"rprolev22-{packet['role']}-{index:02d}-{digest[:14]}"
            observations.append(
                {
                    "schema_version": ROLE_OBSERVATION_SCHEMA,
                    "observation_id": record_id,
                    "role_record_id": record_id,
                    "source_record_index": index,
                    "case_id": packet["case_id"],
                    "shard_id": packet["shard_id"],
                    **validated,
                    "raw_record_sha256": "sha256:" + digest,
                    "provenance": {
                        "producer_kind": producer_kind,
                        "producer_id": producer_id,
                        "call_id": (call_metadata or {}).get("call_id", ""),
                        "model": (call_metadata or {}).get("model", ""),
                        "prompt_sha256": (call_metadata or {}).get("prompt_sha256", ""),
                    },
                    "terminal_state": "admitted",
                    "graph_routing_eligible": False,
                }
            )
            custody.append(
                {
                    "record_index": index,
                    "role_record_id": record_id,
                    "terminal_state": "admitted",
                    "raw_record_sha256": "sha256:" + digest,
                }
            )
        except Exception as exc:  # noqa: BLE001
            custody.append(
                {
                    "record_index": index,
                    "terminal_state": "quarantined",
                    "reason": f"{type(exc).__name__}: {exc}",
                    "raw_record_sha256": "sha256:" + digest,
                }
            )
    admitted = len(observations)
    quarantined = sum(item["terminal_state"] == "quarantined" for item in custody)
    return {
        "schema_version": ROLE_RESPONSE_SCHEMA,
        "status": "position_role_response_v22_custody_complete",
        "role": packet["role"],
        "response_status": status,
        "global_limitations": response["global_limitations"],
        "records": custody,
        "observations": observations,
        "role_terminal_disposition": (
            "reviewed_empty" if not custody and status == "not_found"
            else "partially_compiled" if admitted and quarantined
            else "compiled" if admitted
            else "quarantined"
        ),
        "boundary": {
            "semantic_role_or_category_correctness_inferred_by_code": False,
            "object_expression_compatibility_gate_added": False,
            "prose_keyword_gate_added": False,
            "one_alias_per_component_enforced": True,
            "parallel_component_columns_used": False,
            "provider_raw_record_hash_preserved": True,
            "semantic_merge_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def project_parallel_role_response_v22(response: Mapping[str, Any]) -> dict[str, Any]:
    """Mechanical provider-free projection of reviewed v2/v2.1 fixtures."""
    projected_records = []
    for record in response["records"]:
        components = [
            {
                "object_kind": object_kind,
                "object_interpretation": object_text,
                "expression_kind": expression_kind,
                "source_evidence_id": source_id,
            }
            for object_kind, object_text, expression_kind, source_id in zip(
                record["object_kinds"],
                record["object_interpretations"],
                record["expression_kinds"],
                record["source_evidence_ids"],
                strict=True,
            )
        ]
        projected_records.append(
            {
                "role": record["role"],
                "status": record["status"],
                "evidence_ids": record["evidence_ids"],
                "role_interpretation": record["role_interpretation"],
                "stance_components": components,
                "fidelity_note": record["fidelity_note"],
                "limitations": record["limitations"],
            }
        )
    return {
        "status": response["status"],
        "records": projected_records,
        "global_limitations": response["global_limitations"],
    }


# Relation behavior is unchanged from v2.1.
build_position_relation_packet_v22 = build_position_relation_packet_v21
build_position_relation_prompts_v22 = build_position_relation_prompts_v21
compile_position_relation_response_v22 = compile_position_relation_response_v21
position_relation_response_schema_v22 = position_relation_response_schema_v21
join_position_role_first_v22 = join_position_role_first_v21
