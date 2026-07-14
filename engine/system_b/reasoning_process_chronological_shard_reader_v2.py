"""Role-explicit semantic envelopes for chronological reasoning-process shards.

Version 2 keeps evidence-family behavior unchanged and replaces one generic
interpretation string with role-specific semantic text for position,
uncertainty, and challenge. Deterministic validation checks shape, visible
source regions, and role-consistency only; it does not decide whether the
model's semantic paraphrases are correct.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_chronological_shard_reader import (
    OBSERVATION_SCHEMA_VERSION,
    RESPONSE_SCHEMA_VERSION,
    TOP_FIELDS,
    SHARD_INSTRUCTIONS,
    build_shard_prompts,
    shard_response_schema,
    validate_shard_record,
    validate_shard_response_envelope,
)
from .reasoning_process_chronological_shards import PACKET_SCHEMA
from .reasoning_process_view_specific import (
    CHALLENGE_RESPONSE_TYPES,
    ITEM_STATUSES,
    RESPONSE_STATUSES,
    ViewSpecificInterfaceError,
)
from .reasoning_process_view_specific_v2 import (
    CHALLENGE_TYPES,
    ROLE_FIELDS,
    TRAJECTORY_TYPES,
)
from .reasoning_process_views import canonical_json_bytes, sha256_bytes

RESPONSE_SCHEMA_VERSION_V2 = "lolla.reasoning_process_chronological_shard_response.v2"
OBSERVATION_SCHEMA_VERSION_V2 = "lolla.reasoning_process_chronological_shard_observation.v2"

ROLE_TEXT_FIELDS = {
    "position_and_decision_trajectory": (
        "starting_position_interpretation",
        "current_position_interpretation",
        "qualification_interpretation",
        "trajectory_interpretation",
    ),
    "uncertainty_and_unresolved_state": (
        "unresolved_matter_interpretation",
        "preservation_or_reopen_interpretation",
        "relationship_interpretation",
    ),
    "challenge_and_revision_response": (
        "prior_frame_interpretation",
        "challenge_interpretation",
        "response_interpretation",
        "revision_interpretation",
        "relationship_interpretation",
    ),
}

ROLE_EXPLICIT_INSTRUCTIONS = {
    "position_and_decision_trajectory": (
        "Return at most two trajectory records. State the starting position, current position, "
        "remaining qualification, and the transition between them in separate fields. Every field "
        "must describe its own evidence role. If no starting state is visible, use "
        "qualified_current_only and leave starting_position_interpretation and starting evidence empty."
    ),
    "uncertainty_and_unresolved_state": (
        "Return at most two complete unresolved-plus-reopen relationships. State the unresolved matter, "
        "the condition or evidence that preserves or reopens it, and their specific relationship in "
        "separate fields. Do not split the two halves of one relationship across records."
    ),
    "challenge_and_revision_response": (
        "Return at most two actual challenge relationships. State the prior frame, challenge, response, "
        "revision, and how they relate in separate fields. Assign aliases by semantic role, not merely "
        "surface sentence order. Retrospective or reported challenges are allowed, but every role must "
        "be explained. A new proposal, self-contained tension, or later stance is not automatically a challenge."
    ),
    "evidence_and_assumption_discipline": SHARD_INSTRUCTIONS[
        "evidence_and_assumption_discipline"
    ],
}


def _text(*, allow_empty: bool = False) -> dict[str, Any]:
    return {
        "type": "string",
        "minLength": 0 if allow_empty else 1,
        "maxLength": 500,
    }


def _evidence_array(*, allow_empty: bool = False) -> dict[str, Any]:
    return {
        "type": "array",
        "minItems": 0 if allow_empty else 1,
        "maxItems": 6,
        "uniqueItems": True,
        "items": {"type": "string", "pattern": "^e[0-9]{3}$"},
    }


def shard_response_schema_v2(view_kind: str) -> dict[str, Any]:
    if view_kind == "evidence_and_assumption_discipline":
        return shard_response_schema(view_kind)
    if view_kind not in ROLE_TEXT_FIELDS:
        raise ViewSpecificInterfaceError("unsupported role-explicit shard family")
    properties: dict[str, Any] = {
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "limitations": {"type": "string", "maxLength": 500},
    }
    for role in ROLE_FIELDS[view_kind]:
        allow_empty = (
            view_kind == "position_and_decision_trajectory"
            and role == "starting_state_evidence_ids"
        ) or (
            view_kind == "challenge_and_revision_response"
            and role in {"response_evidence_ids", "revision_evidence_ids"}
        )
        properties[role] = _evidence_array(allow_empty=allow_empty)
    for field in ROLE_TEXT_FIELDS[view_kind]:
        allow_empty = field in {
            "starting_position_interpretation",
            "response_interpretation",
            "revision_interpretation",
        }
        properties[field] = _text(allow_empty=allow_empty)
    if view_kind == "position_and_decision_trajectory":
        properties["trajectory_type"] = {
            "type": "string",
            "enum": list(TRAJECTORY_TYPES),
        }
    if view_kind == "challenge_and_revision_response":
        properties["challenge_type"] = {
            "type": "string",
            "enum": list(CHALLENGE_TYPES),
        }
        properties["response_type"] = {
            "type": "string",
            "enum": list(CHALLENGE_RESPONSE_TYPES),
        }
    record = {
        "type": "object",
        "description": f"Role-explicit {view_kind} relationship.",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "description": f"Two-record role-explicit chronological shard response for {view_kind}.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 2,
                "items": record,
            },
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": ["status", "records", "global_limitations"],
        "additionalProperties": False,
    }


def build_shard_prompts_v2(wrapper: Mapping[str, Any]) -> dict[str, str]:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("schema_version") != PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid role-explicit shard prompt packet")
    view_kind = str(packet["view_kind"])
    if view_kind not in ROLE_EXPLICIT_INSTRUCTIONS:
        raise ViewSpecificInterfaceError("unsupported role-explicit shard prompt family")
    base = build_shard_prompts(wrapper)
    if view_kind == "evidence_and_assumption_discipline":
        return base
    # Keep the tested system boundary and place visible source before the exact
    # relationship task, following the frozen July-2026 practice decision.
    user_prompt = (
        "Chronological shard packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nRole-explicit relationship contract: "
        + ROLE_EXPLICIT_INSTRUCTIONS[view_kind]
        + "\nQuestion: "
        + str(packet["question"])
    )
    return {
        "system_prompt": base["system_prompt"],
        "user_prompt": user_prompt,
        "system_prompt_sha256": base["system_prompt_sha256"],
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def _expected_fields(view_kind: str) -> set[str]:
    if view_kind == "evidence_and_assumption_discipline":
        return {
            "interpretation",
            "status",
            "limitations",
            *ROLE_FIELDS[view_kind],
        }
    fields = {
        "status",
        "limitations",
        *ROLE_FIELDS[view_kind],
        *ROLE_TEXT_FIELDS[view_kind],
    }
    if view_kind == "position_and_decision_trajectory":
        fields.add("trajectory_type")
    if view_kind == "challenge_and_revision_response":
        fields.update({"challenge_type", "response_type"})
    return fields


def _role_allowed_aliases(
    *, wrapper: Mapping[str, Any], view_kind: str, role: str
) -> dict[str, str]:
    focal = {item["alias"]: item["span_id"] for item in wrapper["focal_alias_map"]}
    context = {item["alias"]: item["span_id"] for item in wrapper["context_alias_map"]}
    policy = wrapper["packet"]["prior_context"]["role_limited_citation_policy"]
    context_allowed = (
        policy == "prior_claim_or_frame_only"
        and role == "prior_claim_or_frame_evidence_ids"
    ) or (
        policy == "starting_state_only" and role == "starting_state_evidence_ids"
    )
    return focal | context if context_allowed else focal


def _validate_text(
    record: Mapping[str, Any], field: str, *, allow_empty: bool, errors: list[str]
) -> str:
    value = record.get(field)
    if not isinstance(value, str) or len(value) > 500 or (not allow_empty and not value.strip()):
        errors.append(f"{field} is invalid")
        return ""
    return value


def validate_shard_record_v2(
    record: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    view_kind = str(wrapper["packet"]["view_kind"])
    if view_kind == "evidence_and_assumption_discipline":
        validated = validate_shard_record(record, wrapper=wrapper)
        return {
            **validated,
            "role_interpretations": {"relationship": validated["interpretation"]},
            "display_interpretation": validated["interpretation"],
            "contract_version": "evidence_reference_v1_unchanged",
        }
    if view_kind not in ROLE_TEXT_FIELDS:
        raise ViewSpecificInterfaceError("unsupported role-explicit record family")
    errors: list[str] = []
    if set(record) != _expected_fields(view_kind):
        errors.append("record fields do not match role-explicit contract")
    if record.get("status") not in ITEM_STATUSES:
        errors.append("semantic status is invalid")
    if not isinstance(record.get("limitations"), str) or len(record.get("limitations", "")) > 500:
        errors.append("limitations are invalid")
    role_spans: dict[str, list[str]] = {}
    for role in ROLE_FIELDS[view_kind]:
        values = record.get(role)
        allow_empty = (
            view_kind == "position_and_decision_trajectory"
            and role == "starting_state_evidence_ids"
        ) or (
            view_kind == "challenge_and_revision_response"
            and role in {"response_evidence_ids", "revision_evidence_ids"}
        )
        if not isinstance(values, list) or len(values) > 6 or any(not isinstance(value, str) for value in values):
            errors.append(f"{role} is invalid")
            values = []
        if not allow_empty and not values:
            errors.append(f"{role} must not be empty")
        allowed = _role_allowed_aliases(wrapper=wrapper, view_kind=view_kind, role=role)
        if len(values) != len(set(values)) or not set(values).issubset(allowed):
            errors.append(f"{role} contains duplicate or role-forbidden aliases")
        role_spans[role] = [allowed[value] for value in values if value in allowed]
    role_texts: dict[str, str] = {}
    for field in ROLE_TEXT_FIELDS[view_kind]:
        role_texts[field] = _validate_text(
            record,
            field,
            allow_empty=field
            in {
                "starting_position_interpretation",
                "response_interpretation",
                "revision_interpretation",
            },
            errors=errors,
        )
    if view_kind == "position_and_decision_trajectory":
        trajectory = record.get("trajectory_type")
        starting_ids = record.get("starting_state_evidence_ids") or []
        starting_text = role_texts["starting_position_interpretation"]
        if trajectory not in TRAJECTORY_TYPES:
            errors.append("trajectory type is invalid")
        if bool(starting_ids) != bool(starting_text.strip()):
            errors.append("starting interpretation and evidence must be empty or present together")
        if trajectory in {"changed", "emerged_from_uncertainty"} and not starting_ids:
            errors.append("trajectory claim requires starting-state evidence and interpretation")
        if trajectory == "qualified_current_only" and starting_ids:
            errors.append("qualified_current_only cannot claim a starting state")
    if view_kind == "challenge_and_revision_response":
        if record.get("challenge_type") not in CHALLENGE_TYPES:
            errors.append("challenge type is invalid")
        response_type = record.get("response_type")
        response_ids = record.get("response_evidence_ids") or []
        revision_ids = record.get("revision_evidence_ids") or []
        response_text = role_texts["response_interpretation"]
        revision_text = role_texts["revision_interpretation"]
        if response_type not in CHALLENGE_RESPONSE_TYPES:
            errors.append("response type is invalid")
        if bool(response_ids) != bool(response_text.strip()):
            errors.append("response interpretation and evidence must be empty or present together")
        if bool(revision_ids) != bool(revision_text.strip()):
            errors.append("revision interpretation and evidence must be empty or present together")
        if response_type == "no_response" and response_ids:
            errors.append("no_response cannot include response evidence or interpretation")
        if response_type != "no_response" and not response_ids:
            errors.append("response type requires response evidence and interpretation")
        if response_type == "revise" and not revision_ids:
            errors.append("revise requires revision evidence and interpretation")
    if errors:
        raise ViewSpecificInterfaceError("; ".join(errors))
    labels = {
        "position_and_decision_trajectory": (
            ("Starting", "starting_position_interpretation"),
            ("Current", "current_position_interpretation"),
            ("Qualification", "qualification_interpretation"),
            ("Trajectory", "trajectory_interpretation"),
        ),
        "uncertainty_and_unresolved_state": (
            ("Unresolved", "unresolved_matter_interpretation"),
            ("Preservation/reopen", "preservation_or_reopen_interpretation"),
            ("Relationship", "relationship_interpretation"),
        ),
        "challenge_and_revision_response": (
            ("Prior frame", "prior_frame_interpretation"),
            ("Challenge", "challenge_interpretation"),
            ("Response", "response_interpretation"),
            ("Revision", "revision_interpretation"),
            ("Relationship", "relationship_interpretation"),
        ),
    }[view_kind]
    display = " | ".join(
        f"{label}: {role_texts[field]}" for label, field in labels if role_texts[field]
    )
    return {
        "interpretation": display,
        "display_interpretation": display,
        "role_interpretations": role_texts,
        "status": record["status"],
        "role_source_span_ids": role_spans,
        "source_span_ids": list(
            dict.fromkeys(span for spans in role_spans.values() for span in spans)
        ),
        "contract_version": "role_explicit_v2",
    }


def compile_shard_response_recordwise_v2(
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
            validated = validate_shard_record_v2(record, wrapper=wrapper)
            observation_id = (
                f"rpshardv2-{wrapper['packet']['case_id']}-"
                f"{wrapper['packet']['view_kind']}-{index:02d}-{digest[:10]}"
            )
            observations.append(
                {
                    "schema_version": OBSERVATION_SCHEMA_VERSION_V2,
                    "observation_id": observation_id,
                    "case_id": wrapper["packet"]["case_id"],
                    "shard_id": wrapper["packet"]["shard_id"],
                    "family": wrapper["packet"]["view_kind"],
                    "interpretation": validated["display_interpretation"],
                    "role_interpretations": validated["role_interpretations"],
                    "semantic_status": validated["status"],
                    "role_source_span_ids": validated["role_source_span_ids"],
                    "source_span_ids": validated["source_span_ids"],
                    "raw_record": {
                        "record_identity": record_identity,
                        "record_index": index,
                        "record": record,
                    },
                    "raw_record_sha256": "sha256:" + digest,
                    "provenance": {
                        "producer_kind": producer_kind,
                        "producer_id": producer_id,
                        "call_id": (call_metadata or {}).get("call_id", ""),
                        "model": (call_metadata or {}).get("model", ""),
                        "prompt_sha256": (call_metadata or {}).get(
                            "prompt_sha256", ""
                        ),
                    },
                    "terminal_state": "admitted",
                    "graph_routing_eligible": False,
                }
            )
            custody.append(
                {
                    "record_index": index,
                    "terminal_state": "admitted",
                    "observation_id": observation_id,
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
    admitted = sum(item["terminal_state"] == "admitted" for item in custody)
    quarantined = len(custody) - admitted
    return {
        "schema_version": RESPONSE_SCHEMA_VERSION_V2,
        "status": "chronological_shard_v2_record_custody_complete",
        "envelope": envelope,
        "records": custody,
        "observations": observations,
        "shard_terminal_disposition": (
            "reviewed_empty"
            if not custody and response["status"] == "not_found"
            else "partially_compiled"
            if admitted and quarantined
            else "compiled"
            if admitted
            else "quarantined"
        ),
        "boundary": {
            "model_records_changed": False,
            "display_interpretation_mechanically_formatted": True,
            "semantic_role_correctness_inferred_by_code": False,
            "record_level_validation_weakened": False,
            "semantic_merge_performed": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
