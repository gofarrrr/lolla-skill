"""Factor observed-vs-integrated before deriving one mechanism's user-process status."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .reasoning_mechanism_ontology import MECHANISMS
from .reasoning_mechanism_submicrotask_v1 import USER_RESPONSE_SCHEMA
from .reasoning_pattern_role_record_interpreter_v2 import ALL_STATES, ROUTING_STATES
from .simulated_reliability_v1 import SimulatedReliabilityError


PACKET_SCHEMA = "lolla.reasoning_mechanism_user_factor_packet.v1"
FACTOR_RESPONSE_SCHEMA = "lolla.reasoning_mechanism_user_factor_response.v1"
OBSERVATION_VALUES = {"observed", "not_observed", "ambiguous"}
INTEGRATION_VALUES = {"integrated", "not_integrated", "ambiguous", "not_applicable"}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _verify(packet: Mapping[str, Any]) -> None:
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise SimulatedReliabilityError("invalid user-factor packet")
    supplied = packet.get("packet_sha256")
    payload = {key: value for key, value in packet.items() if key != "packet_sha256"}
    if supplied != _hash(payload):
        raise SimulatedReliabilityError("user-factor packet hash drifted")


def build_user_factor_packet_v1(
    *, parent_packet: Mapping[str, Any], mechanism_id: str
) -> dict[str, Any]:
    if mechanism_id not in MECHANISMS:
        raise SimulatedReliabilityError("unknown user-factor mechanism")
    records = list(parent_packet.get("role_records", []))
    if not records:
        raise SimulatedReliabilityError("user-factor packet requires role records")
    packet = {
        "schema_version": PACKET_SCHEMA,
        "case_id": parent_packet["case_id"],
        "mechanism_id": mechanism_id,
        "mechanism_contract": MECHANISMS[mechanism_id],
        "factor_contract": {
            "mechanism_observation": {
                "observed": "The mechanism was relevant or exhibited somewhere in the bounded user trajectory, even if repaired later.",
                "not_observed": "The bounded role records do not support that the mechanism was relevant or exhibited.",
                "ambiguous": "Responsible readings disagree about whether the mechanism was relevant or exhibited."
            },
            "integration_status": {
                "integrated": "Later user reasoning changed a plan, confidence, test, boundary, safeguard, or decision condition in response.",
                "not_integrated": "The observed mechanism remains operative without such a repair.",
                "ambiguous": "Responsible readings disagree about whether later reasoning integrated it.",
                "not_applicable": "Use only when mechanism_observation is not_observed."
            }
        },
        "derivation_contract": {
            "observed_plus_integrated": "resolved",
            "observed_plus_not_integrated": "unresolved",
            "not_observed_plus_not_applicable": "not_observed",
            "any_ambiguous_factor": "ambiguous"
        },
        "pattern_state_contract": {
            "present": "A positively exhibited unresolved mechanism.",
            "missing_protection": "A safeguard required by an unresolved mechanism is not observed.",
            "tension": "Use when either factor is ambiguous.",
            "not_applicable": "Use for resolved or not_observed derived status."
        },
        "role_records": records,
        "boundary": {
            "factors_model_authored": True,
            "user_process_status_model_authored": False,
            "remaining_real_world_risk_is_not_failure_to_integrate": True,
            "qualification_review_conclusion_included": False,
            "raw_conversation_included": False,
            "keyword_or_chronology_gate_added": False,
            "deterministic_semantic_inference": False
        }
    }
    packet["packet_sha256"] = _hash(packet)
    return packet


def user_factor_response_schema_v1(mechanism_id: str) -> dict[str, Any]:
    properties = {
        "mechanism_id": {"type": "string", "enum": [mechanism_id]},
        "mechanism_observation": {"type": "string", "enum": sorted(OBSERVATION_VALUES)},
        "integration_status": {"type": "string", "enum": sorted(INTEGRATION_VALUES)},
        "pattern_state": {"type": "string", "enum": sorted(ALL_STATES)},
        "source_role_record_ids": {
            "type": "array",
            "minItems": 0,
            "maxItems": 3,
            "items": {"type": "string", "minLength": 1, "maxLength": 160}
        }
    }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False
    }


def build_user_factor_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    _verify(packet)
    system = (
        "Assess two explicit factors for one reasoning-process mechanism. First ask whether the "
        "mechanism appeared or was relevant anywhere in the bounded user trajectory, even if later "
        "repaired. Then ask whether later user reasoning integrated it by changing a plan, confidence, "
        "test, boundary, safeguard, or decision condition. A remaining real-world risk does not mean "
        "the reasoning failed to integrate it. Apply the mechanism's requires and excludes. Return "
        "schema-valid JSON with exact role-record IDs; do not derive the final status."
    )
    user = (
        "USER-PROCESS FACTOR MICROTASK\n"
        + _canonical(packet)
        + "\n\nUse only the supplied role records. observed or ambiguous needs exact role evidence. "
        "not_observed uses integration_status not_applicable, pattern_state not_applicable, and no "
        "role IDs. observed plus integrated uses pattern_state not_applicable; observed plus "
        "not_integrated uses present or missing_protection; any ambiguous factor uses tension."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode()).hexdigest()
    }


def compile_user_factor_response_v1(
    *, response: Mapping[str, Any], packet: Mapping[str, Any], producer_id: str
) -> dict[str, Any]:
    _verify(packet)
    expected = {
        "mechanism_id", "mechanism_observation", "integration_status",
        "pattern_state", "source_role_record_ids"
    }
    if set(response) != expected or response.get("mechanism_id") != packet["mechanism_id"]:
        raise SimulatedReliabilityError("invalid user-factor response fields")
    observation = response["mechanism_observation"]
    integration = response["integration_status"]
    state = response["pattern_state"]
    ids = response["source_role_record_ids"]
    valid_ids = {row["role_record_id"] for row in packet["role_records"]}
    if (
        observation not in OBSERVATION_VALUES
        or integration not in INTEGRATION_VALUES
        or state not in ALL_STATES
        or not isinstance(ids, list)
        or len(ids) != len(set(ids))
        or bool(set(ids) - valid_ids)
    ):
        raise SimulatedReliabilityError("invalid user-factor value or evidence custody")
    if observation == "not_observed":
        if integration != "not_applicable" or state != "not_applicable" or ids:
            raise SimulatedReliabilityError("not-observed factor contract is invalid")
        derived_status = "not_observed"
    elif observation == "ambiguous" or integration == "ambiguous":
        if state != "tension" or not ids:
            raise SimulatedReliabilityError("ambiguous factor contract is invalid")
        derived_status = "ambiguous"
    elif observation == "observed" and integration == "integrated":
        if state != "not_applicable" or not ids:
            raise SimulatedReliabilityError("integrated factor contract is invalid")
        derived_status = "resolved"
    elif observation == "observed" and integration == "not_integrated":
        if state not in ROUTING_STATES or not ids:
            raise SimulatedReliabilityError("unintegrated factor contract is invalid")
        derived_status = "unresolved"
    else:
        raise SimulatedReliabilityError("unsupported user-factor combination")
    assessment = {
        "mechanism_id": response["mechanism_id"],
        "user_process_status": derived_status,
        "pattern_state": state,
        "source_role_record_ids": list(ids)
    }
    return {
        "schema_version": USER_RESPONSE_SCHEMA,
        "status": "user_status_custody_complete_from_explicit_factors",
        "assessment": assessment,
        "factor_assessment": dict(response),
        "producer_id": producer_id,
        "boundary": {
            "factor_semantics_model_authored": True,
            "user_process_status_derived_from_explicit_factors": True,
            "deterministic_semantic_inference": False,
            "keyword_or_chronology_gate_added": False,
            "semantic_repair_performed": False,
            "routing_disposition_authored": False
        }
    }
