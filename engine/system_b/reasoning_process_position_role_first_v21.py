"""Prompt/packet-only semantic-contract clarification for role-first v2.

V2.1 leaves response schemas, validators, custody, joins, and budgets unchanged.
It defines temporal endpoints, coherent record identity, component identity,
source coverage, and speaker ownership explicitly in the model-visible packet.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_position_role_first_v2 import (
    RELATION_PACKET_SCHEMA,
    ROLE_ORDER,
    ROLE_PACKET_SCHEMA,
    build_position_relation_packet_v2,
    build_position_role_packet_v2,
    compile_position_relation_response_v2,
    compile_position_role_response_v2,
    join_position_role_first_v2,
    position_relation_response_schema_v2,
    position_role_response_schema_v2,
)
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

ROLE_PACKET_SCHEMA_V21 = "lolla.reasoning_process_position_role_packet.v2_1"
RELATION_PACKET_SCHEMA_V21 = "lolla.reasoning_process_position_relation_packet.v2_1"

ENDPOINT_CONTRACTS = {
    "starting": (
        "Starting means the earliest visible working position in this endpoint-comparison shard, "
        "usually the Turn 1 endpoint. It does not require a stance before the conversation begins. "
        "Attractions, hesitations, competing assessments, and undecided positions can be starts."
    ),
    "current": (
        "Current means the later visible working position in this endpoint-comparison shard, usually "
        "the final user endpoint. Preserve leanings, proposals, plans, decisions, commitments, and "
        "conditional willingness as different expressions."
    ),
    "qualification": (
        "Qualification means any remaining condition, uncertainty, counterpressure, blind spot, or "
        "reopen reason that limits what the current position establishes. It may be stated by the user "
        "or introduced by the assistant. Preserve who introduced it; assistant pressure is part of the "
        "conversation state and does not imply user endorsement."
    ),
}

RECORD_IDENTITY_CONTRACT = (
    "One record is one coherent position thread within the assigned role. Gather every material "
    "visible alias for that thread into evidence_ids. Put each distinct object or expression into a "
    "separate aligned component index inside that same record. Do not create one record per alias, "
    "sentence, object, or component. Use a second record only for a genuinely separate concurrent "
    "position thread about a different subject."
)
SOURCE_COVERAGE_CONTRACT = (
    "Review every focal alias before returning. A valid empty response is allowed only after checking "
    "both user and assistant evidence for the assigned role. Preserve later minority qualifications "
    "and counterpressure even when the current action is already clear."
)


def build_position_role_packet_v21(
    *, wrapper: Mapping[str, Any], role: str
) -> dict[str, Any]:
    packet = build_position_role_packet_v2(wrapper=wrapper, role=role)
    packet["schema_version"] = ROLE_PACKET_SCHEMA_V21
    packet["endpoint_definition"] = ENDPOINT_CONTRACTS[role]
    packet["record_identity_contract"] = RECORD_IDENTITY_CONTRACT
    packet["source_coverage_contract"] = SOURCE_COVERAGE_CONTRACT
    packet["boundary"].update(
        {
            "response_schema_changed_from_v2": False,
            "validator_changed_from_v2": False,
            "record_identity_semantics_made_explicit": True,
            "speaker_ownership_semantics_made_explicit": True,
        }
    )
    return packet


def build_position_role_prompts_v21(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA_V21 or packet.get("role") not in ROLE_ORDER:
        raise ViewSpecificInterfaceError("invalid v2.1 position role packet")
    role = str(packet["role"])
    system_prompt = (
        "You extract one assigned semantic role from a chronological endpoint-comparison shard. "
        "Use only visible evidence aliases and preserve speaker ownership. One record is a coherent "
        "position thread; distinct objects belong in aligned component indices inside that record. "
        "Return JSON matching the supplied schema."
    )
    user_prompt = (
        "Single-role packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nFollow the packet's endpoint, coherent-record, source-coverage, and speaker-"
        "ownership contracts exactly. A belief is not a decision, and a proposal is not acceptance "
        "of its outcome.\nQuestion: "
        + str(packet["question"])
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def compile_position_role_response_v21(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA_V21:
        raise ViewSpecificInterfaceError("invalid v2.1 position role packet")
    projected = dict(packet)
    projected["schema_version"] = ROLE_PACKET_SCHEMA
    compiled = compile_position_role_response_v2(
        response=response,
        packet=projected,
        producer_kind=producer_kind,
        producer_id=producer_id,
        call_metadata=call_metadata,
    )
    compiled["boundary"].update(
        {
            "response_schema_changed_from_v2": False,
            "validator_changed_from_v2": False,
            "v21_prompt_packet_contract": True,
        }
    )
    return compiled


def build_position_relation_packet_v21(
    *, role_compiled_by_role: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    packet = build_position_relation_packet_v2(
        role_compiled_by_role=role_compiled_by_role
    )
    packet["schema_version"] = RELATION_PACKET_SCHEMA_V21
    packet["relationship_identity_contract"] = (
        "One relationship record links the coherent starting, current, and qualification records for "
        "one position thread. Do not pair records by array order or surface proximity. Use a second "
        "relationship only for a genuinely separate concurrent position thread. Preserve missingness "
        "and speaker ownership; do not manufacture adoption or agreement."
    )
    packet["boundary"].update(
        {
            "response_schema_changed_from_v2": False,
            "validator_changed_from_v2": False,
            "relationship_identity_semantics_made_explicit": True,
        }
    )
    return packet


def build_position_relation_prompts_v21(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != RELATION_PACKET_SCHEMA_V21 or not packet.get("call_required"):
        raise ViewSpecificInterfaceError("invalid or empty v2.1 relation packet")
    system_prompt = (
        "You relate independently extracted position-role records by exact role_record_id. One "
        "relationship is one coherent position thread. Preserve speaker ownership, missingness, and "
        "disagreement. Return JSON matching the supplied schema."
    )
    user_prompt = (
        "Role records:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nFollow the packet's relationship-identity contract exactly. Do not rewrite, "
        "strengthen, merge, or silently reconcile the admitted role records. "
        "Do not return a categorical trajectory label.\nQuestion: How do the admitted role records "
        "relate over the conversation?"
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def compile_position_relation_response_v21(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], producer_kind: str, producer_id: str
) -> dict[str, Any]:
    if packet.get("schema_version") != RELATION_PACKET_SCHEMA_V21:
        raise ViewSpecificInterfaceError("invalid v2.1 relation packet")
    projected = dict(packet)
    projected["schema_version"] = RELATION_PACKET_SCHEMA
    compiled = compile_position_relation_response_v2(
        response=response,
        packet=projected,
        producer_kind=producer_kind,
        producer_id=producer_id,
    )
    compiled["boundary"].update(
        {
            "response_schema_changed_from_v2": False,
            "validator_changed_from_v2": False,
            "v21_prompt_packet_contract": True,
        }
    )
    return compiled


# These interfaces are intentionally unchanged and re-exported for callers.
position_role_response_schema_v21 = position_role_response_schema_v2
position_relation_response_schema_v21 = position_relation_response_schema_v2
join_position_role_first_v21 = join_position_role_first_v2
