"""One-mechanism semantic assessment with deterministic routing policy custody."""

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
    compile_mechanism_response_v1,
    validate_mechanism_input_v1,
)


PACKET_SCHEMA = "lolla.reasoning_mechanism_microtask_packet.v1"
RESPONSE_SCHEMA = "lolla.reasoning_mechanism_microtask_response.v1"
BUNDLE_SCHEMA = "lolla.reasoning_mechanism_microtask_bundle.v1"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def build_mechanism_microtask_packet_v1(
    *, parent_packet: Mapping[str, Any], mechanism_id: str
) -> dict[str, Any]:
    validate_mechanism_input_v1(parent_packet)
    if mechanism_id not in MECHANISMS:
        raise SimulatedReliabilityError("unknown mechanism microtask identity")
    packet: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA,
        "case_id": parent_packet["case_id"],
        "arm_id": parent_packet["arm_id"],
        "mechanism_id": mechanism_id,
        "mechanism_contract": MECHANISMS[mechanism_id],
        "user_process_status_contract": {
            "unresolved": "The mechanism remains operative in the latest user reasoning.",
            "resolved": "The mechanism appeared or was relevant but the user later integrated or repaired it.",
            "ambiguous": "The role records support competing responsible readings.",
            "not_observed": "The supplied role records do not support this mechanism.",
        },
        "assistant_coverage_contract": {
            "operationalized": "The assistant turned the pressure into an actionable test, boundary, alternative, or reopening condition.",
            "acknowledged_only": "The assistant noticed the pressure but did not operationalize it.",
            "not_covered": "No supplied assistant contribution covers the pressure.",
            "not_applicable": "The mechanism is not observed and no coverage judgment is needed.",
            "ambiguous": "The assistant evidence supports competing coverage readings.",
        },
        "pattern_state_contract": {
            "present": "A positively exhibited unresolved mechanism.",
            "missing_protection": "A required safeguard is not observed after bounded inspection.",
            "tension": "Competing readings remain.",
            "not_applicable": "Use for resolved or not-observed user-process status.",
        },
        "role_records": list(parent_packet["role_records"]),
        "qualification_review": dict(parent_packet["qualification_review"]),
        "assistant_contributions": list(parent_packet["assistant_contributions"]),
        "evidence_contract": (
            "Cite exact supplied role_record_ids for every observed, resolved, unresolved, or ambiguous "
            "user-process status. Cite exact assistant contribution IDs only for acknowledged, "
            "operationalized, or ambiguous answer coverage."
        ),
        "routing_note": (
            "Do not choose routing. Deterministic policy will route only explicit unresolved status "
            "with acknowledged_only or not_covered answer coverage."
        ),
        "boundary": {
            "one_controlled_mechanism_only": True,
            "user_process_status_model_authored": True,
            "assistant_coverage_model_authored": True,
            "pattern_state_model_authored": True,
            "routing_disposition_model_authored": False,
            "routing_disposition_derived_from_explicit_statuses": True,
            "keyword_or_chronology_gate_added": False,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
    packet["packet_sha256"] = _hash(packet)
    return packet


def mechanism_microtask_response_schema_v1(mechanism_id: str) -> dict[str, Any]:
    if mechanism_id not in MECHANISMS:
        raise SimulatedReliabilityError("unknown mechanism microtask identity")
    properties = {
        "mechanism_id": {"type": "string", "enum": [mechanism_id]},
        "user_process_status": {
            "type": "string",
            "enum": sorted(USER_PROCESS_STATUSES),
        },
        "vanilla_answer_coverage": {
            "type": "string",
            "enum": sorted(VANILLA_ANSWER_COVERAGES),
        },
        "pattern_state": {"type": "string", "enum": sorted(ALL_STATES)},
        "source_role_record_ids": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 1, "maxLength": 160},
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
        "description": "One semantic assessment for one controlled reasoning mechanism.",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def build_mechanism_microtask_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise SimulatedReliabilityError("invalid mechanism microtask packet")
    system = (
        "Assess one controlled reasoning mechanism only. Judge the user's final process status from "
        "role records and the assistant's coverage from assistant contributions. Preserve exact IDs. "
        "Do not treat a remaining qualification as automatic proof of this mechanism. Do not choose "
        "routing; return schema-valid JSON."
    )
    user = (
        "MECHANISM MICROTASK\n"
        + _canonical(packet)
        + "\n\nApply mechanism_contract requires, excludes, and near_neighbor. Every non-not_observed "
        "user status needs role evidence. Coverage needs assistant evidence unless it is not_covered or "
        "not_applicable. resolved and not_observed use pattern_state not_applicable; ambiguous uses "
        "tension; unresolved uses present or missing_protection."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
    }


def compile_mechanism_microtask_response_v1(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], producer_kind: str,
    producer_id: str,
) -> dict[str, Any]:
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise SimulatedReliabilityError("invalid mechanism microtask packet")
    supplied_hash = packet.get("packet_sha256")
    if supplied_hash != _hash({key: value for key, value in packet.items() if key != "packet_sha256"}):
        raise SimulatedReliabilityError("mechanism microtask packet hash drifted")
    fields = {
        "mechanism_id",
        "user_process_status",
        "vanilla_answer_coverage",
        "pattern_state",
        "source_role_record_ids",
        "source_assistant_contribution_ids",
    }
    if set(response) != fields or response.get("mechanism_id") != packet["mechanism_id"]:
        raise SimulatedReliabilityError("mechanism microtask response fields are invalid")
    user_status = response["user_process_status"]
    coverage = response["vanilla_answer_coverage"]
    state = response["pattern_state"]
    role_ids = response["source_role_record_ids"]
    assistant_ids = response["source_assistant_contribution_ids"]
    valid_role_ids = {row["role_record_id"] for row in packet["role_records"]}
    valid_assistant_ids = {
        row["contribution_id"] for row in packet["assistant_contributions"]
    }
    if (
        user_status not in USER_PROCESS_STATUSES
        or coverage not in VANILLA_ANSWER_COVERAGES
        or state not in ALL_STATES
        or not isinstance(role_ids, list)
        or not isinstance(assistant_ids, list)
        or len(role_ids) != len(set(role_ids))
        or len(assistant_ids) != len(set(assistant_ids))
        or bool(set(role_ids) - valid_role_ids)
        or bool(set(assistant_ids) - valid_assistant_ids)
    ):
        raise SimulatedReliabilityError("mechanism microtask value or custody is invalid")
    if user_status == "unresolved" and (state not in ROUTING_STATES or not role_ids):
        raise SimulatedReliabilityError("unresolved microtask lacks state or role evidence")
    if user_status == "ambiguous" and (state != "tension" or not role_ids):
        raise SimulatedReliabilityError("ambiguous microtask lacks tension or role evidence")
    if user_status in {"resolved", "not_observed"} and state != "not_applicable":
        raise SimulatedReliabilityError("preserved microtask state is invalid")
    if user_status == "not_observed" and (
        coverage != "not_applicable" or role_ids or assistant_ids
    ):
        raise SimulatedReliabilityError("not-observed microtask contract is invalid")
    if user_status != "not_observed" and not role_ids:
        raise SimulatedReliabilityError("observed microtask lacks user-process evidence")
    if coverage in {"operationalized", "acknowledged_only", "ambiguous"} and not assistant_ids:
        raise SimulatedReliabilityError("covered microtask lacks assistant evidence")
    if coverage in {"not_covered", "not_applicable"} and assistant_ids:
        raise SimulatedReliabilityError("uncovered microtask cites assistant evidence")
    routing_disposition = (
        "route_uncovered_pressure"
        if user_status == "unresolved"
        and coverage in {"acknowledged_only", "not_covered"}
        else "preserve_no_route"
    )
    if routing_disposition not in ROUTING_DISPOSITIONS:
        raise SimulatedReliabilityError("derived routing disposition is invalid")
    assessment = {
        **dict(response),
        "routing_disposition": routing_disposition,
    }
    return {
        "schema_version": RESPONSE_SCHEMA,
        "status": "mechanism_microtask_custody_complete",
        "assessment": assessment,
        "producer_kind": producer_kind,
        "producer_id": producer_id,
        "boundary": {
            "semantic_fields_model_authored": True,
            "routing_disposition_model_authored": False,
            "routing_disposition_derived_from_explicit_statuses": True,
            "keyword_or_chronology_gate_added": False,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def join_mechanism_microtasks_v1(
    *, parent_packet: Mapping[str, Any], compiled_microtasks: list[Mapping[str, Any]],
    producer_kind: str, producer_id: str,
) -> dict[str, Any]:
    validate_mechanism_input_v1(parent_packet)
    if len(compiled_microtasks) != len(MECHANISMS):
        raise SimulatedReliabilityError("mechanism microtask join requires all mechanisms")
    rows = []
    for item in compiled_microtasks:
        if item.get("schema_version") != RESPONSE_SCHEMA:
            raise SimulatedReliabilityError("mechanism microtask join input is invalid")
        rows.append(dict(item["assessment"]))
    rows.sort(key=lambda row: row["mechanism_id"])
    if [row["mechanism_id"] for row in rows] != sorted(MECHANISMS):
        raise SimulatedReliabilityError("mechanism microtask identities are incomplete")
    compiled = compile_mechanism_response_v1(
        response={"assessments": rows},
        packet=parent_packet,
        producer_kind=producer_kind,
        producer_id=producer_id,
    )
    compiled["schema_version"] = BUNDLE_SCHEMA
    compiled["boundary"] = {
        "nine_independent_semantic_microtasks": True,
        "routing_dispositions_derived_from_explicit_statuses": True,
        "deterministic_semantic_inference": False,
        "semantic_repair_performed": False,
        "direct_graph_routing_allowed": False,
    }
    return compiled
