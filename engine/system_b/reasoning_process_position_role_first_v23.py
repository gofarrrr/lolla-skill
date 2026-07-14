"""Role-boundary and expression clarification over role-first v2.2.

V2.3 changes only model-visible packet and prompt semantics. Nested component
schemas, validators, custody, joins, and call ceilings remain unchanged. The
LLM interprets whether evidence is a working position or a qualification;
deterministic code does not classify prose or enforce semantic exclusivity.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_position_role_first_v2 import ROLE_ORDER
from .reasoning_process_position_role_first_v22 import (
    ROLE_PACKET_SCHEMA_V22,
    build_position_relation_packet_v22,
    build_position_relation_prompts_v22,
    build_position_role_packet_v22,
    compile_position_relation_response_v22,
    compile_position_role_response_v22,
    join_position_role_first_v22,
    position_relation_response_schema_v22,
    position_role_response_schema_v22,
)
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

ROLE_PACKET_SCHEMA_V23 = "lolla.reasoning_process_position_role_packet.v2_3"

ROLE_BOUNDARY_CONTRACTS = {
    "starting": (
        "Extract the earliest visible working position: the user's own attractions, preferences, "
        "hesitations, assessments, and unresolved stance at the first endpoint. Context about an "
        "external offer or another person's position is evidence only when it helps express the "
        "user's own starting stance; do not mistake mere situation description for endorsement."
    ),
    "current": (
        "Extract the later working answer the user is leaning toward, proposing, planning, deciding, "
        "committing to, refusing, or conditionally willing to accept. A concern can be part of current "
        "when it is converted into an adopted condition or action. Do not include a merely unresolved "
        "question, counterpressure, blind spot, or reopen reason just because it appears in the final "
        "user turn; those meanings belong to qualification."
    ),
    "qualification": (
        "Extract what still limits, destabilizes, or could reopen the current working answer: unresolved "
        "questions, unmet conditions, counterpressure, blind spots, side effects, or path dependence. "
        "Include user-authored uncertainty and assistant-authored pressure while preserving speaker "
        "ownership. Do not treat an adopted safeguard or chosen condition as unresolved merely because "
        "it is conditional; focus on what remains capable of changing or limiting the answer."
    ),
}

EXPRESSION_INTERPRETATION_CONTRACT = (
    "Classify expression from the source speaker's relationship to that component, not from the role "
    "name or the fact that a situation was mentioned. Use reported_without_endorsement only when the "
    "speaker attributes a position, proposal, or assessment to someone else without adopting it. The "
    "speaker's own excitement or desire is preference_or_desire; own worry that pushes against an "
    "option is counterpressure; 'cannot tell', 'not resolved', or equivalent open judgment is "
    "uncertain_or_undecided; leaning, proposals, commitments, and conditional willingness retain their "
    "specific force. Do not upgrade or flatten modal strength."
)


def build_position_role_packet_v23(*, wrapper: Mapping[str, Any], role: str) -> dict[str, Any]:
    packet = build_position_role_packet_v22(wrapper=wrapper, role=role)
    packet["schema_version"] = ROLE_PACKET_SCHEMA_V23
    packet["endpoint_definition"] = "Apply role_boundary_contract to the visible early or later endpoint."
    packet["role_boundary_contract"] = ROLE_BOUNDARY_CONTRACTS[role]
    packet["expression_interpretation_contract"] = EXPRESSION_INTERPRETATION_CONTRACT
    packet["boundary"].update({
        "semantic_contract_changed_from_v22": True,
        "response_schema_changed_from_v22": False,
        "validator_changed_from_v22": False,
        "deterministic_role_exclusivity_gate_added": False,
        "deterministic_expression_gate_added": False,
        "chronological_gate_added": False,
        "keyword_gate_added": False,
    })
    return packet


def build_position_role_prompts_v23(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA_V23 or packet.get("role") not in ROLE_ORDER:
        raise ViewSpecificInterfaceError("invalid v2.3 position role packet")
    system_prompt = (
        "You interpret one assigned semantic role from a chronological endpoint-comparison shard. "
        "Use only visible evidence aliases and preserve speaker ownership and modal force. One record "
        "is one coherent position thread; each stance component is one atomic object-expression-source "
        "unit. Apply the packet's role boundary and expression contract. Return schema-valid JSON."
    )
    user_prompt = (
        "Single-role packet:\n" + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nInterpret semantics, not keywords, surface position, or chronology alone. Keep unresolved "
        "qualification out of current and preserve the speaker's own attitude. Follow every packet "
        "contract.\nQuestion: " + str(packet["question"])
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def compile_position_role_response_v23(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], producer_kind: str,
    producer_id: str, call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    if packet.get("schema_version") != ROLE_PACKET_SCHEMA_V23:
        raise ViewSpecificInterfaceError("invalid v2.3 position role packet")
    projected = dict(packet)
    projected["schema_version"] = ROLE_PACKET_SCHEMA_V22
    compiled = compile_position_role_response_v22(
        response=response, packet=projected, producer_kind=producer_kind,
        producer_id=producer_id, call_metadata=call_metadata,
    )
    compiled["boundary"].update({
        "v23_prompt_packet_contract": True,
        "response_schema_changed_from_v22": False,
        "validator_changed_from_v22": False,
        "deterministic_role_exclusivity_gate_added": False,
        "deterministic_expression_gate_added": False,
        "chronological_gate_added": False,
        "keyword_gate_added": False,
    })
    return compiled


# Relation meaning and every wire/validator remain unchanged from v2.2.
build_position_relation_packet_v23 = build_position_relation_packet_v22
build_position_relation_prompts_v23 = build_position_relation_prompts_v22
compile_position_relation_response_v23 = compile_position_relation_response_v22
position_role_response_schema_v23 = position_role_response_schema_v22
position_relation_response_schema_v23 = position_relation_response_schema_v22
join_position_role_first_v23 = join_position_role_first_v22
