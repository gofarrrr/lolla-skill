"""Status-free paired wire for role-first v2.4 semantic allocation.

V2.4.1 removes redundant paired envelope status fields. Per-record semantic
statuses remain provider-authored. Code derives only the mechanical envelope
status from the presence and statuses of explicit role-labeled records.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_position_role_first_v2 import ITEM_STATUSES
from .reasoning_process_position_role_first_v24 import (
    PAIRED_ROLES,
    build_position_current_qualification_packet_v24,
    compile_position_current_qualification_response_v24,
    position_current_qualification_response_schema_v24,
)
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

PAIRED_PACKET_SCHEMA_V241 = "lolla.reasoning_process_position_current_qualification_packet.v2_4_1"


def build_position_current_qualification_packet_v241(*, wrapper: Mapping[str, Any]) -> dict[str, Any]:
    packet = build_position_current_qualification_packet_v24(wrapper=wrapper)
    packet["schema_version"] = PAIRED_PACKET_SCHEMA_V241
    packet["response_contract"].update({
        "per_role_envelope_status_requested": False,
    })
    packet["boundary"].update({
        "redundant_envelope_status_removed_from_v24": True,
        "record_semantic_status_retained": True,
        "envelope_status_derived_mechanically": True,
        "semantic_repair_performed": False,
    })
    return packet


def position_current_qualification_response_schema_v241() -> dict[str, Any]:
    schema = position_current_qualification_response_schema_v24()
    properties = dict(schema["properties"])
    properties.pop("current_status")
    properties.pop("qualification_status")
    return {**schema, "properties": properties, "required": ["records", "allocation_note", "global_limitations"]}


def build_position_current_qualification_prompts_v241(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != PAIRED_PACKET_SCHEMA_V241:
        raise ViewSpecificInterfaceError("invalid v2.4.1 paired packet")
    system_prompt = (
        "You jointly interpret current position and qualification from one endpoint-comparison shard. "
        "Compare roles before allocating meanings. Preserve source speaker and modal force. Return "
        "role-labeled records; omit a role only if no evidence supports it. Return schema-valid JSON."
    )
    user_prompt = (
        "Paired semantic packet:\n" + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nAllocate semantics, not keywords or position. If one alias has adopted and unresolved "
        "meanings, place each meaning in its role and explain the distinction. Return no role envelope "
        "statuses; records carry that structure.\nQuestion: " + str(packet["question"])
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt, "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")), "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8"))}


def _derived_status(records: list[Mapping[str, Any]]) -> str:
    if not records:
        return "not_found"
    statuses = {record.get("status") for record in records}
    if not statuses <= set(ITEM_STATUSES):
        raise ViewSpecificInterfaceError("v2.4.1 record status is invalid")
    return next(iter(statuses)) if len(statuses) == 1 else "mixed"


def compile_position_current_qualification_response_v241(
    *, response: Mapping[str, Any], wrapper: Mapping[str, Any], producer_kind: str,
    producer_id: str, call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if set(response) != {"records", "allocation_note", "global_limitations"}:
        raise ViewSpecificInterfaceError("v2.4.1 paired response fields do not match")
    records = response.get("records")
    if not isinstance(records, list):
        raise ViewSpecificInterfaceError("v2.4.1 records must be an array")
    by_role = {role: [] for role in PAIRED_ROLES}
    for record in records:
        if not isinstance(record, Mapping) or record.get("role") not in PAIRED_ROLES:
            raise ViewSpecificInterfaceError("v2.4.1 record role is invalid")
        by_role[record["role"]].append(record)
    projected = {
        "current_status": _derived_status(by_role["current"]),
        "qualification_status": _derived_status(by_role["qualification"]),
        "records": records,
        "allocation_note": response["allocation_note"],
        "global_limitations": response["global_limitations"],
    }
    compiled = compile_position_current_qualification_response_v24(
        response=projected, wrapper=wrapper, producer_kind=producer_kind,
        producer_id=producer_id, call_metadata=call_metadata,
    )
    compiled["schema_version"] = "lolla.reasoning_process_position_current_qualification_response.v2_4_1"
    compiled["derived_envelope_status"] = {role: projected[f"{role}_status"] for role in PAIRED_ROLES}
    compiled["boundary"].update({
        "provider_authored_envelope_status_used": False,
        "envelope_status_derived_from_record_presence_and_status": True,
        "semantic_repair_performed": False,
    })
    return compiled
