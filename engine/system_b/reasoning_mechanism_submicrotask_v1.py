"""Split one-mechanism user-status and assistant-coverage semantic custody."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .reasoning_mechanism_ontology import MECHANISMS
from .reasoning_pattern_role_record_interpreter_v2 import ALL_STATES, ROUTING_STATES
from .simulated_reliability_v1 import (
    ROUTING_DISPOSITIONS,
    USER_PROCESS_STATUSES,
    VANILLA_ANSWER_COVERAGES,
    SimulatedReliabilityError,
)


USER_PACKET_SCHEMA = "lolla.reasoning_mechanism_user_status_packet.v1"
USER_RESPONSE_SCHEMA = "lolla.reasoning_mechanism_user_status_response.v1"
COVERAGE_PACKET_SCHEMA = "lolla.reasoning_mechanism_assistant_coverage_packet.v1"
COVERAGE_RESPONSE_SCHEMA = "lolla.reasoning_mechanism_assistant_coverage_response.v1"
JOIN_SCHEMA = "lolla.reasoning_mechanism_split_assessment.v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _seal(packet: dict[str, Any]) -> dict[str, Any]:
    packet["packet_sha256"] = _hash(packet)
    return packet


def _verify_packet(packet: Mapping[str, Any], schema: str) -> None:
    if packet.get("schema_version") != schema:
        raise SimulatedReliabilityError("invalid mechanism submicrotask packet")
    supplied = packet.get("packet_sha256")
    payload = {key: value for key, value in packet.items() if key != "packet_sha256"}
    if supplied != _hash(payload):
        raise SimulatedReliabilityError("mechanism submicrotask packet hash drifted")


def build_user_status_packet_v1(
    *, parent_packet: Mapping[str, Any], mechanism_id: str
) -> dict[str, Any]:
    if mechanism_id not in MECHANISMS:
        raise SimulatedReliabilityError("unknown mechanism identity")
    role_records = list(parent_packet.get("role_records", []))
    if not role_records:
        raise SimulatedReliabilityError("user-status packet requires role records")
    return _seal(
        {
            "schema_version": USER_PACKET_SCHEMA,
            "case_id": parent_packet["case_id"],
            "mechanism_id": mechanism_id,
            "mechanism_contract": MECHANISMS[mechanism_id],
            "status_contract": {
                "unresolved": "The reasoning-process mechanism itself remains operative in the latest user reasoning.",
                "resolved": "The mechanism appeared or was relevant, but later user reasoning integrated or repaired it.",
                "ambiguous": "The bounded role records support competing responsible readings.",
                "not_observed": "The bounded role records do not support the mechanism.",
            },
            "pattern_state_contract": {
                "present": "A positively exhibited unresolved mechanism.",
                "missing_protection": "A safeguard required by the mechanism is not observed.",
                "tension": "Competing readings remain.",
                "not_applicable": "Use for resolved or not_observed status.",
            },
            "role_records": role_records,
            "judgment_boundary": {
                "reasoning_process_not_external_outcome": True,
                "remaining_real_world_risk_does_not_prove_unresolved_mechanism": True,
                "apply_excludes_before_unresolved": True,
                "qualification_review_conclusion_included": False,
                "raw_conversation_included": False,
                "keyword_or_chronology_gate": False,
            },
        }
    )


def user_status_response_schema_v1(mechanism_id: str) -> dict[str, Any]:
    properties = {
        "mechanism_id": {"type": "string", "enum": [mechanism_id]},
        "user_process_status": {
            "type": "string",
            "enum": sorted(USER_PROCESS_STATUSES),
        },
        "pattern_state": {"type": "string", "enum": sorted(ALL_STATES)},
        "source_role_record_ids": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 1, "maxLength": 160},
        },
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def build_user_status_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    _verify_packet(packet, USER_PACKET_SCHEMA)
    system = (
        "Judge one reasoning-process mechanism in the user's trajectory. Classify the mechanism, "
        "not whether the underlying real-world risk disappeared. Apply the mechanism's excludes "
        "before choosing unresolved. If a concern changed the plan, confidence, test, boundary, "
        "safeguard, or decision condition as described by the contract, preserve it as resolved even "
        "when uncertainty remains. Return schema-valid JSON with exact role-record IDs."
    )
    user = (
        "USER-PROCESS MICROTASK\n"
        + _canonical(packet)
        + "\n\nUse only the bounded role records. Every status except not_observed needs exact "
        "role-record evidence. resolved and not_observed use not_applicable; ambiguous uses tension; "
        "unresolved uses present or missing_protection."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
    }


def compile_user_status_response_v1(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], producer_id: str
) -> dict[str, Any]:
    _verify_packet(packet, USER_PACKET_SCHEMA)
    expected = {
        "mechanism_id",
        "user_process_status",
        "pattern_state",
        "source_role_record_ids",
    }
    if set(response) != expected or response.get("mechanism_id") != packet["mechanism_id"]:
        raise SimulatedReliabilityError("invalid user-status response fields")
    status = response["user_process_status"]
    state = response["pattern_state"]
    role_ids = response["source_role_record_ids"]
    valid_ids = {row["role_record_id"] for row in packet["role_records"]}
    if (
        status not in USER_PROCESS_STATUSES
        or state not in ALL_STATES
        or not isinstance(role_ids, list)
        or len(role_ids) != len(set(role_ids))
        or bool(set(role_ids) - valid_ids)
    ):
        raise SimulatedReliabilityError("invalid user-status value or evidence custody")
    if status == "unresolved" and (state not in ROUTING_STATES or not role_ids):
        raise SimulatedReliabilityError("unresolved user status lacks state or evidence")
    if status == "ambiguous" and (state != "tension" or not role_ids):
        raise SimulatedReliabilityError("ambiguous user status lacks tension or evidence")
    if status in {"resolved", "not_observed"} and state != "not_applicable":
        raise SimulatedReliabilityError("preserved user status has invalid state")
    if status == "not_observed" and role_ids:
        raise SimulatedReliabilityError("not-observed user status cites evidence")
    if status != "not_observed" and not role_ids:
        raise SimulatedReliabilityError("observed user status lacks evidence")
    return {
        "schema_version": USER_RESPONSE_SCHEMA,
        "status": "user_status_custody_complete",
        "assessment": dict(response),
        "producer_id": producer_id,
        "boundary": {
            "semantic_fields_model_authored": True,
            "semantic_repair_performed": False,
            "routing_disposition_authored": False,
        },
    }


def build_assistant_coverage_packet_v1(
    *, parent_packet: Mapping[str, Any], user_status: Mapping[str, Any]
) -> dict[str, Any]:
    mechanism_id = user_status.get("mechanism_id")
    if mechanism_id not in MECHANISMS:
        raise SimulatedReliabilityError("invalid coverage mechanism identity")
    valid_roles = {
        row["role_record_id"]: row for row in parent_packet.get("role_records", [])
    }
    cited = user_status.get("source_role_record_ids", [])
    if bool(set(cited) - set(valid_roles)):
        raise SimulatedReliabilityError("coverage packet has unknown user evidence")
    return _seal(
        {
            "schema_version": COVERAGE_PACKET_SCHEMA,
            "case_id": parent_packet["case_id"],
            "mechanism_id": mechanism_id,
            "mechanism_contract": MECHANISMS[mechanism_id],
            "user_process_assessment": dict(user_status),
            "cited_user_role_records": [valid_roles[item] for item in cited],
            "assistant_contributions": list(parent_packet.get("assistant_contributions", [])),
            "coverage_contract": {
                "operationalized": "The assistant turned the pressure into an actionable test, boundary, alternative, safeguard, or reopening condition.",
                "acknowledged_only": "The assistant noticed the pressure but did not make it actionable.",
                "not_covered": "No supplied assistant contribution covers the pressure.",
                "not_applicable": "The user mechanism is not observed, so coverage is not judged.",
                "ambiguous": "The assistant evidence supports competing responsible coverage readings.",
            },
            "judgment_boundary": {
                "assistant_coverage_not_user_adoption": True,
                "remaining_real_world_risk_does_not_reduce_operationalized_coverage": True,
                "any_cited_actionable_test_or_boundary_excludes_acknowledged_only": True,
                "routing_disposition_model_authored": False,
                "raw_conversation_included": False,
            },
        }
    )


def assistant_coverage_response_schema_v1(mechanism_id: str) -> dict[str, Any]:
    properties = {
        "mechanism_id": {"type": "string", "enum": [mechanism_id]},
        "vanilla_answer_coverage": {
            "type": "string",
            "enum": sorted(VANILLA_ANSWER_COVERAGES),
        },
        "source_assistant_contribution_ids": {
            "type": "array",
            "minItems": 0,
            "maxItems": 4,
            "items": {"type": "string", "pattern": "^assistant-turn-[0-9]{3}$"},
        },
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def build_assistant_coverage_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    _verify_packet(packet, COVERAGE_PACKET_SCHEMA)
    system = (
        "Judge only assistant coverage of one bounded user-process pressure. Do not judge whether the "
        "user adopted the advice or whether the real-world risk disappeared. Operationalized means "
        "the assistant supplied an actionable test, boundary, alternative, safeguard, or reopening "
        "condition; if a cited contribution does that, do not call it acknowledged_only. Return "
        "schema-valid JSON with exact assistant contribution IDs."
    )
    user = (
        "ASSISTANT-COVERAGE MICROTASK\n"
        + _canonical(packet)
        + "\n\nUse only the supplied assistant contributions. Covered or ambiguous results cite exact "
        "assistant IDs. not_covered and not_applicable cite none."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest(),
    }


def compile_assistant_coverage_response_v1(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], producer_id: str
) -> dict[str, Any]:
    _verify_packet(packet, COVERAGE_PACKET_SCHEMA)
    expected = {
        "mechanism_id",
        "vanilla_answer_coverage",
        "source_assistant_contribution_ids",
    }
    if set(response) != expected or response.get("mechanism_id") != packet["mechanism_id"]:
        raise SimulatedReliabilityError("invalid assistant-coverage response fields")
    coverage = response["vanilla_answer_coverage"]
    ids = response["source_assistant_contribution_ids"]
    valid_ids = {row["contribution_id"] for row in packet["assistant_contributions"]}
    if (
        coverage not in VANILLA_ANSWER_COVERAGES
        or not isinstance(ids, list)
        or len(ids) != len(set(ids))
        or bool(set(ids) - valid_ids)
    ):
        raise SimulatedReliabilityError("invalid assistant coverage or evidence custody")
    if coverage in {"operationalized", "acknowledged_only", "ambiguous"} and not ids:
        raise SimulatedReliabilityError("covered assistant result lacks evidence")
    if coverage in {"not_covered", "not_applicable"} and ids:
        raise SimulatedReliabilityError("uncovered assistant result cites evidence")
    user_not_observed = (
        packet["user_process_assessment"]["user_process_status"] == "not_observed"
    )
    if user_not_observed != (coverage == "not_applicable"):
        raise SimulatedReliabilityError("assistant coverage applicability conflicts with user status")
    return {
        "schema_version": COVERAGE_RESPONSE_SCHEMA,
        "status": "assistant_coverage_custody_complete",
        "assessment": dict(response),
        "producer_id": producer_id,
        "boundary": {
            "semantic_fields_model_authored": True,
            "semantic_repair_performed": False,
            "routing_disposition_authored": False,
        },
    }


def join_split_mechanism_assessment_v1(
    *, user_result: Mapping[str, Any], coverage_result: Mapping[str, Any]
) -> dict[str, Any]:
    if user_result.get("schema_version") != USER_RESPONSE_SCHEMA:
        raise SimulatedReliabilityError("invalid user-status join input")
    if coverage_result.get("schema_version") != COVERAGE_RESPONSE_SCHEMA:
        raise SimulatedReliabilityError("invalid assistant-coverage join input")
    user = dict(user_result["assessment"])
    coverage = dict(coverage_result["assessment"])
    if user["mechanism_id"] != coverage["mechanism_id"]:
        raise SimulatedReliabilityError("split mechanism identities differ")
    route = (
        "route_uncovered_pressure"
        if user["user_process_status"] == "unresolved"
        and coverage["vanilla_answer_coverage"] in {"acknowledged_only", "not_covered"}
        else "preserve_no_route"
    )
    if route not in ROUTING_DISPOSITIONS:
        raise SimulatedReliabilityError("invalid derived routing disposition")
    return {
        "schema_version": JOIN_SCHEMA,
        "status": "split_mechanism_assessment_joined",
        "assessment": {
            **user,
            **coverage,
            "routing_disposition": route,
        },
        "boundary": {
            "two_independent_semantic_tasks": True,
            "routing_disposition_model_authored": False,
            "routing_disposition_derived_from_explicit_statuses": True,
            "deterministic_semantic_inference": False,
            "keyword_or_chronology_gate_added": False,
            "semantic_repair_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
