"""Paired current/qualification allocation over role-first v2.3.

V2.4 keeps starting as one independent semantic task, allocates current and
qualification together in one bounded task, then relates exact role record IDs.
Code splits explicit model labels and validates custody; it does not infer role
correctness, subtract aliases, score semantics, or apply keyword/chronology gates.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_position_decomposition_v1 import ROLE_COMPONENT_LIMITS
from .reasoning_process_position_role_first_v2 import ITEM_STATUSES, RESPONSE_STATUSES
from .reasoning_process_position_role_first_v23 import (
    EXPRESSION_INTERPRETATION_CONTRACT,
    ROLE_BOUNDARY_CONTRACTS,
    build_position_relation_packet_v23,
    build_position_relation_prompts_v23,
    build_position_role_packet_v23,
    build_position_role_prompts_v23,
    compile_position_relation_response_v23,
    compile_position_role_response_v23,
    join_position_role_first_v23,
    position_relation_response_schema_v23,
    position_role_response_schema_v23,
)
from .reasoning_process_position_role_first_v22 import build_position_role_packet_v22
from .reasoning_process_chronological_shard_reader_v4 import (
    STANCE_EXPRESSION_KINDS,
    STANCE_OBJECT_KINDS,
)
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

PAIRED_PACKET_SCHEMA_V24 = "lolla.reasoning_process_position_current_qualification_packet.v2_4"
PAIRED_RESPONSE_SCHEMA_V24 = "lolla.reasoning_process_position_current_qualification_response.v2_4"
PAIRED_ROLES = ("current", "qualification")


def build_position_current_qualification_packet_v24(*, wrapper: Mapping[str, Any]) -> dict[str, Any]:
    packet = build_position_role_packet_v22(wrapper=wrapper, role="current")
    packet["schema_version"] = PAIRED_PACKET_SCHEMA_V24
    packet["role"] = "current_and_qualification"
    packet["paired_roles"] = list(PAIRED_ROLES)
    packet["endpoint_definition"] = "Compare the later working answer with what still limits or could reopen it."
    packet["question"] = (
        "What is the user's later working position, and what distinct unresolved condition, "
        "counterpressure, blind spot, or reopen reason still limits it?"
    )
    packet["role_boundary_contract"] = {
        "current": (
            "The user's later working answer: what they lean toward, propose, plan, decide, commit to, "
            "refuse, or conditionally accept, including concerns converted into adopted safeguards."
        ),
        "qualification": (
            "What still limits or could reopen that answer: unresolved questions, unmet conditions, "
            "counterpressure, blind spots, side effects, or path dependence, with speaker ownership."
        ),
        "allocation": (
            "Interpret current and qualification comparatively before writing records. Allocate each "
            "meaning to the role it performs. The same source alias may support both roles only when "
            "it contains two genuinely distinct meanings; create separate role-specific components and "
            "explain the distinction. Do not duplicate one unresolved meaning into current merely because "
            "the user acknowledges it alongside the working answer."
        ),
    }
    packet["expression_interpretation_contract"] = (
        "Classify force from the source speaker's relation to the component. Reserve "
        "reported_without_endorsement for attributing a stance to someone else. Preserve the speaker's "
        "own desire, counterpressure, uncertainty, leaning, commitment, and conditional willingness "
        "without flattening or upgrading them."
    )
    packet["response_contract"] = {
        "maximum_records_total": 4,
        "maximum_records_per_role": 2,
        "valid_empty_role_allowed": True,
        "explicit_role_label_required": True,
        "global_synthesis_requested": False,
    }
    packet["boundary"].update({
        "current_and_qualification_allocated_in_one_probabilistic_task": True,
        "starting_role_included": False,
        "hard_alias_exclusivity_required": False,
        "deterministic_alias_subtraction_added": False,
        "deterministic_semantic_role_gate_added": False,
        "semantic_score_added": False,
        "keyword_or_chronology_gate_added": False,
        "maximum_pipeline_calls": 3,
    })
    return packet


def position_current_qualification_response_schema_v24() -> dict[str, Any]:
    component_properties = {
        "object_kind": {"type": "string", "enum": list(STANCE_OBJECT_KINDS)},
        "object_interpretation": {"type": "string", "minLength": 1, "maxLength": 300},
        "expression_kind": {"type": "string", "enum": list(STANCE_EXPRESSION_KINDS)},
        "source_evidence_id": {"type": "string", "pattern": "^e[0-9]{3}$"},
    }
    record_properties = {
        "role": {"type": "string", "enum": list(PAIRED_ROLES)},
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "evidence_ids": {"type": "array", "minItems": 1, "maxItems": 6, "items": {"type": "string", "pattern": "^e[0-9]{3}$"}},
        "role_interpretation": {"type": "string", "minLength": 1, "maxLength": 500},
        "stance_components": {"type": "array", "minItems": 1, "maxItems": max(ROLE_COMPONENT_LIMITS[role] for role in PAIRED_ROLES), "items": {"type": "object", "properties": component_properties, "required": list(component_properties), "additionalProperties": False}},
        "fidelity_note": {"type": "string", "minLength": 1, "maxLength": 800},
        "limitations": {"type": "string", "maxLength": 500},
    }
    return {
        "type": "object",
        "description": "Joint semantic allocation of current and qualification records.",
        "properties": {
            "current_status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "qualification_status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {"type": "array", "minItems": 0, "maxItems": 4, "items": {"type": "object", "properties": record_properties, "required": list(record_properties), "additionalProperties": False}},
            "allocation_note": {"type": "string", "minLength": 1, "maxLength": 800},
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": ["current_status", "qualification_status", "records", "allocation_note", "global_limitations"],
        "additionalProperties": False,
    }


def build_position_current_qualification_prompts_v24(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != PAIRED_PACKET_SCHEMA_V24:
        raise ViewSpecificInterfaceError("invalid v2.4 paired packet")
    system_prompt = (
        "You jointly interpret current position and qualification from one endpoint-comparison shard. "
        "Compare the roles before allocating meanings. Preserve source speaker and modal force. One "
        "record is one coherent role-specific thread; each component is one atomic object-expression-"
        "source unit. Return schema-valid JSON."
    )
    user_prompt = (
        "Paired semantic packet:\n" + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nAllocate meanings semantically, not by keywords, final-turn location, or hard alias "
        "exclusivity. Do not duplicate one unresolved meaning into current. If one alias genuinely "
        "contains both an adopted and unresolved meaning, represent the distinct meanings separately "
        "and explain why. Follow every packet contract.\nQuestion: " + str(packet["question"])
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def compile_position_current_qualification_response_v24(
    *, response: Mapping[str, Any], wrapper: Mapping[str, Any], producer_kind: str,
    producer_id: str, call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    fields = {"current_status", "qualification_status", "records", "allocation_note", "global_limitations"}
    if set(response) != fields:
        raise ViewSpecificInterfaceError("v2.4 paired response fields do not match")
    records = response.get("records")
    if not isinstance(records, list) or len(records) > 4:
        raise ViewSpecificInterfaceError("v2.4 paired records are invalid")
    if not isinstance(response.get("allocation_note"), str) or not response["allocation_note"] or len(response["allocation_note"]) > 800:
        raise ViewSpecificInterfaceError("v2.4 allocation note is invalid")
    if not isinstance(response.get("global_limitations"), str) or len(response["global_limitations"]) > 700:
        raise ViewSpecificInterfaceError("v2.4 global limitations are invalid")
    by_role = {role: [] for role in PAIRED_ROLES}
    for record in records:
        if not isinstance(record, Mapping) or record.get("role") not in PAIRED_ROLES:
            raise ViewSpecificInterfaceError("v2.4 record role is invalid")
        by_role[record["role"]].append(dict(record))
    compiled = {}
    for role in PAIRED_ROLES:
        status = response[f"{role}_status"]
        if status not in RESPONSE_STATUSES or len(by_role[role]) > 2:
            raise ViewSpecificInterfaceError(f"v2.4 {role} status or record count is invalid")
        role_response = {"status": status, "records": by_role[role], "global_limitations": response["global_limitations"]}
        packet = build_position_role_packet_v23(wrapper=wrapper, role=role)
        compiled[role] = compile_position_role_response_v23(
            response=role_response, packet=packet, producer_kind=producer_kind,
            producer_id=producer_id, call_metadata=call_metadata,
        )
    custody = [item for role in PAIRED_ROLES for item in compiled[role]["records"]]
    observations = [item for role in PAIRED_ROLES for item in compiled[role]["observations"]]
    return {
        "schema_version": PAIRED_RESPONSE_SCHEMA_V24,
        "status": "position_current_qualification_v24_custody_complete",
        "allocation_note": response["allocation_note"],
        "global_limitations": response["global_limitations"],
        "role_compiled": compiled,
        "records": custody,
        "observations": observations,
        "paired_terminal_disposition": (
            "partially_compiled" if observations and any(item["terminal_state"] == "quarantined" for item in custody)
            else "compiled" if observations
            else "reviewed_empty" if not custody
            else "quarantined"
        ),
        "boundary": {
            "model_role_labels_split_mechanically": True,
            "semantic_role_correctness_inferred_by_code": False,
            "hard_alias_exclusivity_enforced": False,
            "alias_subtraction_performed": False,
            "semantic_score_computed": False,
            "keyword_or_chronology_gate_added": False,
            "direct_graph_routing_allowed": False,
        },
    }


# Starting and relation retain v2.3 behavior.
build_position_starting_packet_v24 = build_position_role_packet_v23
build_position_starting_prompts_v24 = build_position_role_prompts_v23
compile_position_starting_response_v24 = compile_position_role_response_v23
position_starting_response_schema_v24 = position_role_response_schema_v23
build_position_relation_packet_v24 = build_position_relation_packet_v23
build_position_relation_prompts_v24 = build_position_relation_prompts_v23
compile_position_relation_response_v24 = compile_position_relation_response_v23
position_relation_response_schema_v24 = position_relation_response_schema_v23
join_position_role_first_v24 = join_position_role_first_v23
