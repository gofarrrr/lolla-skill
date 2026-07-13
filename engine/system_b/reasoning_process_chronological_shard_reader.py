"""Strict provider contract and record custody for chronological shard readers."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_chronological_shards import PACKET_SCHEMA
from .reasoning_process_view_specific import (
    CHALLENGE_RESPONSE_TYPES,
    ITEM_STATUSES,
    RESPONSE_STATUSES,
    ViewSpecificInterfaceError,
)
from .reasoning_process_view_specific_v2 import (
    CHALLENGE_TYPES,
    RELATIONSHIP_TYPES,
    ROLE_FIELDS,
    TRAJECTORY_TYPES,
)
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

RESPONSE_SCHEMA_VERSION = "lolla.reasoning_process_chronological_shard_response.v1"
OBSERVATION_SCHEMA_VERSION = "lolla.reasoning_process_chronological_shard_observation.v1"
TOP_FIELDS = {"status", "records", "global_limitations"}

SHARD_INSTRUCTIONS = {
    "position_and_decision_trajectory": (
        "Return at most two positions or trajectory segments in the focal region. "
        "Use changed or emerged_from_uncertainty only with separate starting and current evidence. "
        "Use qualified_current_only when no starting state is visible."
    ),
    "evidence_and_assumption_discipline": (
        "Return at most two claims or inputs whose evidence strength matters. Pair each claim or input "
        "with the visible language that bounds its strength or prevents a stronger claim."
    ),
    "uncertainty_and_unresolved_state": (
        "Return at most two unresolved matters. Pair each with visible evidence that preserves it as "
        "open or states how it can reopen the direction."
    ),
    "challenge_and_revision_response": (
        "Return at most two actual challenges or corrections. Separate the prior frame, challenge, "
        "response, and revision roles. A new proposal or tension is not automatically a challenge."
    ),
}


def _evidence_array(*, allow_empty: bool = False) -> dict[str, Any]:
    return {
        "type": "array",
        "minItems": 0 if allow_empty else 1,
        "maxItems": 6,
        "uniqueItems": True,
        "items": {"type": "string", "pattern": "^e[0-9]{3}$"},
    }


def shard_response_schema(view_kind: str) -> dict[str, Any]:
    if view_kind not in SHARD_INSTRUCTIONS:
        raise ViewSpecificInterfaceError("unsupported shard response family")
    properties: dict[str, Any] = {
        "interpretation": {"type": "string", "minLength": 1, "maxLength": 700},
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "limitations": {"type": "string", "maxLength": 500},
    }
    for role in ROLE_FIELDS[view_kind]:
        allow_empty = (
            view_kind == "position_and_decision_trajectory" and role == "starting_state_evidence_ids"
        ) or (
            view_kind == "challenge_and_revision_response" and role in {"response_evidence_ids", "revision_evidence_ids"}
        )
        properties[role] = _evidence_array(allow_empty=allow_empty)
    if view_kind == "position_and_decision_trajectory":
        properties["trajectory_type"] = {"type": "string", "enum": list(TRAJECTORY_TYPES)}
    if view_kind == "challenge_and_revision_response":
        properties["challenge_type"] = {"type": "string", "enum": list(CHALLENGE_TYPES)}
        properties["response_type"] = {"type": "string", "enum": list(CHALLENGE_RESPONSE_TYPES)}
    record = {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "description": f"Two-record chronological shard response for {view_kind}.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {"type": "array", "minItems": 0, "maxItems": 2, "items": record},
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": ["status", "records", "global_limitations"],
        "additionalProperties": False,
    }


def build_shard_prompts(wrapper: Mapping[str, Any]) -> dict[str, str]:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("schema_version") != PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid chronological shard prompt packet")
    view_kind = str(packet["view_kind"])
    if view_kind not in SHARD_INSTRUCTIONS:
        raise ViewSpecificInterfaceError("unsupported chronological shard prompt family")
    policy = packet["prior_context"]["role_limited_citation_policy"]
    policy_text = {
        "none": "Prior context is read-only and none of its aliases may be cited.",
        "prior_claim_or_frame_only": "Prior-context aliases may be cited only in prior_claim_or_frame_evidence_ids; all other roles must cite the focal region.",
        "starting_state_only": "Prior-context aliases may be cited only in starting_state_evidence_ids; all other roles must cite the focal region.",
    }[policy]
    system_prompt = (
        "You are a bounded reasoning-process shard reader. Interpret messy conversation semantically, "
        "but only for the declared family and focal region. Use visible aliases such as e001, never "
        "quotes. Preserve uncertainty; return not_found when the relationship is absent. Do not score "
        "quality, effort, trust, or the final answer. Do not rank options, merge other shards, infer from "
        "an auxiliary ledger, or route anything to a graph. " + policy_text
    )
    user_prompt = (
        "Chronological shard packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nRelationship contract: "
        + SHARD_INSTRUCTIONS[view_kind]
        + "\nQuestion: "
        + str(packet["question"])
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def _expected_fields(view_kind: str) -> set[str]:
    fields = {"interpretation", "status", "limitations", *ROLE_FIELDS[view_kind]}
    if view_kind == "position_and_decision_trajectory":
        fields.add("trajectory_type")
    if view_kind == "challenge_and_revision_response":
        fields.update({"challenge_type", "response_type"})
    return fields


def validate_shard_response_envelope(payload: Mapping[str, Any], *, wrapper: Mapping[str, Any]) -> dict[str, Any]:
    if set(payload) != TOP_FIELDS:
        raise ViewSpecificInterfaceError("shard response envelope fields do not match")
    status = payload.get("status")
    records = payload.get("records")
    if status not in RESPONSE_STATUSES or not isinstance(records, list) or len(records) > 2:
        raise ViewSpecificInterfaceError("shard response envelope status or records are invalid")
    if status == "not_found" and records:
        raise ViewSpecificInterfaceError("not_found shard response must be empty")
    if status != "not_found" and not records:
        raise ViewSpecificInterfaceError("non-empty shard status requires records")
    if not isinstance(payload.get("global_limitations"), str) or len(payload["global_limitations"]) > 700:
        raise ViewSpecificInterfaceError("shard global limitations are invalid")
    return {"status": "shard_response_envelope_valid", "record_count": len(records), "semantic_records_validated": False}


def validate_shard_record(record: Mapping[str, Any], *, wrapper: Mapping[str, Any]) -> dict[str, Any]:
    packet = wrapper["packet"]
    view_kind = str(packet["view_kind"])
    errors: list[str] = []
    if set(record) != _expected_fields(view_kind):
        errors.append("record fields do not match shard contract")
    interpretation = record.get("interpretation")
    if not isinstance(interpretation, str) or not interpretation.strip() or len(interpretation) > 700:
        errors.append("interpretation is invalid")
    if record.get("status") not in ITEM_STATUSES:
        errors.append("semantic status is invalid")
    if not isinstance(record.get("limitations"), str) or len(record.get("limitations", "")) > 500:
        errors.append("limitations are invalid")
    focal = {item["alias"]: item["span_id"] for item in wrapper["focal_alias_map"]}
    context = {item["alias"]: item["span_id"] for item in wrapper["context_alias_map"]}
    policy = packet["prior_context"]["role_limited_citation_policy"]
    role_spans: dict[str, list[str]] = {}
    for role in ROLE_FIELDS[view_kind]:
        values = record.get(role)
        allow_empty = (
            view_kind == "position_and_decision_trajectory" and role == "starting_state_evidence_ids"
        ) or (
            view_kind == "challenge_and_revision_response" and role in {"response_evidence_ids", "revision_evidence_ids"}
        )
        if not isinstance(values, list) or len(values) > 6 or any(not isinstance(value, str) for value in values):
            errors.append(f"{role} is invalid")
            values = []
        if not allow_empty and not values:
            errors.append(f"{role} must not be empty")
        context_allowed = (
            policy == "prior_claim_or_frame_only" and role == "prior_claim_or_frame_evidence_ids"
        ) or (policy == "starting_state_only" and role == "starting_state_evidence_ids")
        allowed = focal | context if context_allowed else focal
        if len(values) != len(set(values)) or not set(values).issubset(allowed):
            errors.append(f"{role} contains duplicate or role-forbidden aliases")
        role_spans[role] = [allowed[value] for value in values if value in allowed]
    if view_kind == "position_and_decision_trajectory":
        trajectory = record.get("trajectory_type")
        if trajectory not in TRAJECTORY_TYPES:
            errors.append("trajectory type is invalid")
        if trajectory in {"changed", "emerged_from_uncertainty"} and not record.get("starting_state_evidence_ids"):
            errors.append("trajectory claim requires starting-state evidence")
    if view_kind == "challenge_and_revision_response":
        if record.get("challenge_type") not in CHALLENGE_TYPES:
            errors.append("challenge type is invalid")
        response_type = record.get("response_type")
        if response_type not in CHALLENGE_RESPONSE_TYPES:
            errors.append("response type is invalid")
        if response_type == "no_response" and record.get("response_evidence_ids"):
            errors.append("no_response cannot cite response evidence")
        if response_type != "no_response" and not record.get("response_evidence_ids"):
            errors.append("response type requires response evidence")
        if response_type == "revise" and not record.get("revision_evidence_ids"):
            errors.append("revise requires revision evidence")
    if errors:
        raise ViewSpecificInterfaceError("; ".join(errors))
    return {
        "interpretation": interpretation,
        "status": record["status"],
        "role_source_span_ids": role_spans,
        "source_span_ids": list(dict.fromkeys(span for spans in role_spans.values() for span in spans)),
    }


def compile_shard_response_recordwise(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    record_identity: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    envelope = validate_shard_response_envelope(response, wrapper=wrapper)
    observations = []
    custody = []
    for index, record in enumerate(response["records"], start=1):
        digest = sha256_bytes(canonical_json_bytes(record))
        try:
            validated = validate_shard_record(record, wrapper=wrapper)
            observation_id = f"rpshard-{wrapper['packet']['case_id']}-{wrapper['packet']['view_kind']}-{index:02d}-{digest[:10]}"
            observations.append(
                {
                    "schema_version": OBSERVATION_SCHEMA_VERSION,
                    "observation_id": observation_id,
                    "case_id": wrapper["packet"]["case_id"],
                    "shard_id": wrapper["packet"]["shard_id"],
                    "family": wrapper["packet"]["view_kind"],
                    "interpretation": validated["interpretation"],
                    "semantic_status": validated["status"],
                    "role_source_span_ids": validated["role_source_span_ids"],
                    "source_span_ids": validated["source_span_ids"],
                    "raw_record": {"record_identity": record_identity, "record_index": index, "record": record},
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
            custody.append({"record_index": index, "terminal_state": "admitted", "observation_id": observation_id, "raw_record_sha256": "sha256:" + digest})
        except Exception as exc:  # noqa: BLE001
            custody.append({"record_index": index, "terminal_state": "quarantined", "reason": f"{type(exc).__name__}: {exc}", "raw_record_sha256": "sha256:" + digest})
    admitted = sum(item["terminal_state"] == "admitted" for item in custody)
    quarantined = len(custody) - admitted
    return {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "status": "chronological_shard_record_custody_complete",
        "envelope": envelope,
        "records": custody,
        "observations": observations,
        "shard_terminal_disposition": (
            "reviewed_empty" if not custody and response["status"] == "not_found" else
            "partially_compiled" if admitted and quarantined else
            "compiled" if admitted else "quarantined"
        ),
        "boundary": {
            "model_records_changed": False,
            "record_level_validation_weakened": False,
            "semantic_merge_performed": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
