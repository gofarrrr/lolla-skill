"""Failure-derived relationship contracts for bounded process views, version 2."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .conversation_state_candidates import SourceCatalog
from .reasoning_process_contracts import OBSERVATION_FAMILIES
from .reasoning_process_view_specific import (
    CHALLENGE_RESPONSE_TYPES,
    ITEM_STATUSES,
    RESPONSE_STATUSES,
    ViewSpecificInterfaceError,
)
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


RESPONSE_SCHEMA_VERSION = "lolla.reasoning_process_view_specific_response.v2"
TRAJECTORY_TYPES = (
    "changed",
    "emerged_from_uncertainty",
    "qualified_current_only",
    "unclear",
)
RELATIONSHIP_TYPES = ("condition", "limit", "tradeoff", "failure_condition", "unclear")
CHALLENGE_TYPES = ("correction", "objection", "counterexample", "reconsideration_request")

VIEW_INSTRUCTIONS = {
    "position_and_decision_trajectory": (
        "Return up to four positions. Use changed or emerged_from_uncertainty only "
        "when starting-state evidence and current-position evidence both support the "
        "trajectory. Otherwise use qualified_current_only and do not claim a shift."
    ),
    "exploration_and_alternatives": (
        "Return up to four alternatives. State the alternative separately from the "
        "specific condition, limit, tradeoff, or failure condition attached to it. "
        "Do not replace the cited attached limit with a different general risk."
    ),
    "evidence_and_assumption_discipline": (
        "Return up to four claims or inputs, each paired with the evidence-strength "
        "boundary that prevents a stronger claim."
    ),
    "uncertainty_and_unresolved_state": (
        "Return up to four unresolved matters, each paired with evidence that keeps "
        "it open or explains how it can reopen the direction."
    ),
    "challenge_and_revision_response": (
        "Return up to four actual challenges or corrections. Cite the earlier claim "
        "or frame being contested, the challenge, and any response or revision. A new "
        "proposal or unresolved condition is not a challenge merely because it creates tension."
    ),
}

ROLE_FIELDS = {
    "position_and_decision_trajectory": (
        "starting_state_evidence_ids",
        "current_position_evidence_ids",
        "qualification_evidence_ids",
    ),
    "exploration_and_alternatives": (
        "alternative_evidence_ids",
        "attached_condition_or_limit_evidence_ids",
    ),
    "evidence_and_assumption_discipline": (
        "claim_or_input_evidence_ids",
        "boundary_evidence_ids",
    ),
    "uncertainty_and_unresolved_state": (
        "unresolved_evidence_ids",
        "preservation_or_reopen_evidence_ids",
    ),
    "challenge_and_revision_response": (
        "prior_claim_or_frame_evidence_ids",
        "challenge_evidence_ids",
        "response_evidence_ids",
        "revision_evidence_ids",
    ),
}


def _evidence_array(*, allow_empty: bool = False) -> dict[str, Any]:
    return {
        "type": "array",
        "minItems": 0 if allow_empty else 1,
        "maxItems": 6,
        "uniqueItems": True,
        "items": {"type": "string", "minLength": 4, "maxLength": 4},
    }


def response_schema_v2(view_kind: str) -> dict[str, Any]:
    if view_kind not in OBSERVATION_FAMILIES:
        raise ViewSpecificInterfaceError("invalid v2 view kind")
    properties: dict[str, Any] = {
        "interpretation": {"type": "string", "minLength": 1, "maxLength": 700},
        "status": {"type": "string", "enum": list(ITEM_STATUSES)},
        "auxiliary_observation_ids": {
            "type": "array",
            "minItems": 0,
            "maxItems": 8,
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1, "maxLength": 120},
        },
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
    if view_kind == "position_and_decision_trajectory":
        properties["trajectory_type"] = {
            "type": "string",
            "enum": list(TRAJECTORY_TYPES),
        }
    elif view_kind == "exploration_and_alternatives":
        properties["relationship_type"] = {
            "type": "string",
            "enum": list(RELATIONSHIP_TYPES),
        }
        properties["attached_condition_or_limit_interpretation"] = {
            "type": "string",
            "minLength": 1,
            "maxLength": 500,
        }
    elif view_kind == "challenge_and_revision_response":
        properties["challenge_type"] = {
            "type": "string",
            "enum": list(CHALLENGE_TYPES),
        }
        properties["response_type"] = {
            "type": "string",
            "enum": list(CHALLENGE_RESPONSE_TYPES),
        }
    return {
        "type": "object",
        "description": f"Relationship-explicit bounded {view_kind} response.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "properties": properties,
                    "required": list(properties),
                    "additionalProperties": False,
                },
            },
            "park_unselected_auxiliary_observations": {"type": "boolean", "const": True},
            "global_limitations": {"type": "string", "maxLength": 700},
        },
        "required": [
            "status",
            "records",
            "park_unselected_auxiliary_observations",
            "global_limitations",
        ],
        "additionalProperties": False,
    }


def build_prompts_v2(wrapper: Mapping[str, Any]) -> dict[str, str]:
    packet = wrapper.get("reader_packet")
    if not isinstance(packet, Mapping):
        raise ViewSpecificInterfaceError("reader packet is missing")
    view_kind = str(packet.get("view_kind", ""))
    if view_kind not in VIEW_INSTRUCTIONS:
        raise ViewSpecificInterfaceError("invalid v2 prompt view kind")
    system_prompt = (
        "You are a bounded reasoning-process reader. Interpret messy conversation "
        "semantically; do not score quality, effort, trust, or the final recommendation. "
        "Scan the complete annotated conversation chronologically. Use only visible "
        "sentence aliases such as e001 and never invent or reproduce source quotes. "
        "Every relationship you claim must be supported by the evidence role assigned "
        "to it. The auxiliary ledger is fallible context, not authority. Preserve "
        "uncertainty and use not_found when the requested process relationship is absent."
    )
    user_prompt = (
        f"Question: {packet['question']}\n\n"
        f"Relationship contract: {VIEW_INSTRUCTIONS[view_kind]}\n\n"
        "Reader packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def _expected_record_fields(view_kind: str) -> set[str]:
    fields = {
        "interpretation",
        "status",
        "auxiliary_observation_ids",
        "limitations",
        *ROLE_FIELDS[view_kind],
    }
    if view_kind == "position_and_decision_trajectory":
        fields.add("trajectory_type")
    elif view_kind == "exploration_and_alternatives":
        fields.update(
            {"relationship_type", "attached_condition_or_limit_interpretation"}
        )
    elif view_kind == "challenge_and_revision_response":
        fields.update({"challenge_type", "response_type"})
    return fields


def validate_response_v2(
    payload: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    packet = wrapper["reader_packet"]
    view_kind = str(packet["view_kind"])
    errors: list[str] = []
    expected_top = {
        "status",
        "records",
        "park_unselected_auxiliary_observations",
        "global_limitations",
    }
    if set(payload) != expected_top:
        errors.append("response fields do not match the v2 contract")
    status = payload.get("status")
    records = payload.get("records")
    if status not in RESPONSE_STATUSES:
        errors.append("response status is invalid")
    if not isinstance(records, list) or len(records) > 4:
        errors.append("records must be an array of at most four items")
        records = []
    if status == "not_found" and records:
        errors.append("not_found response must have no records")
    if status != "not_found" and not records:
        errors.append("non-empty status requires records")
    if payload.get("park_unselected_auxiliary_observations") is not True:
        errors.append("unselected auxiliary observations must remain parked")
    if not isinstance(payload.get("global_limitations"), str) or len(
        payload.get("global_limitations", "")
    ) > 700:
        errors.append("global limitations must be a string")
    aliases = {item["alias"]: item["span_id"] for item in wrapper["evidence_alias_map"]}
    auxiliary = {
        item["observation_id"]
        for item in packet["auxiliary_phase1_ledger"]["observations"]
    }
    normalized: list[dict[str, Any]] = []
    interpretations: list[str] = []
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, Mapping) or set(record) != _expected_record_fields(view_kind):
            errors.append(f"{prefix} fields do not match the v2 contract")
            continue
        interpretation = record.get("interpretation")
        if (
            not isinstance(interpretation, str)
            or not interpretation.strip()
            or len(interpretation) > 700
        ):
            errors.append(f"{prefix}.interpretation is empty")
        else:
            interpretations.append(interpretation.strip())
        if record.get("status") not in ITEM_STATUSES:
            errors.append(f"{prefix}.status is invalid")
        if not isinstance(record.get("limitations"), str) or len(
            record.get("limitations", "")
        ) > 500:
            errors.append(f"{prefix}.limitations must be a string")
        aux_ids = record.get("auxiliary_observation_ids")
        if (
            not isinstance(aux_ids, list)
            or len(aux_ids) > 8
            or any(not isinstance(item, str) for item in aux_ids)
        ):
            errors.append(f"{prefix}.auxiliary_observation_ids is invalid")
            aux_ids = []
        if len(aux_ids) != len(set(aux_ids)) or not set(aux_ids).issubset(auxiliary):
            errors.append(f"{prefix}.auxiliary_observation_ids contains duplicates or unknown IDs")
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
            if (
                not isinstance(values, list)
                or len(values) > 6
                or any(not isinstance(item, str) for item in values)
            ):
                errors.append(f"{prefix}.{role} is invalid")
                values = []
            if not allow_empty and not values:
                errors.append(f"{prefix}.{role} must not be empty")
            if len(values) != len(set(values)) or not set(values).issubset(aliases):
                errors.append(f"{prefix}.{role} contains duplicates or unknown aliases")
            role_spans[role] = [aliases[item] for item in values if item in aliases]
        if view_kind == "position_and_decision_trajectory":
            trajectory = record.get("trajectory_type")
            if trajectory not in TRAJECTORY_TYPES:
                errors.append(f"{prefix}.trajectory_type is invalid")
            if trajectory in {"changed", "emerged_from_uncertainty"} and not record.get(
                "starting_state_evidence_ids"
            ):
                errors.append(f"{prefix} trajectory claim requires starting-state evidence")
        elif view_kind == "exploration_and_alternatives":
            if record.get("relationship_type") not in RELATIONSHIP_TYPES:
                errors.append(f"{prefix}.relationship_type is invalid")
            attached = record.get("attached_condition_or_limit_interpretation")
            if not isinstance(attached, str) or not attached.strip():
                errors.append(f"{prefix} attached condition or limit must be stated")
        elif view_kind == "challenge_and_revision_response":
            if record.get("challenge_type") not in CHALLENGE_TYPES:
                errors.append(f"{prefix}.challenge_type is invalid")
            response_type = record.get("response_type")
            if response_type not in CHALLENGE_RESPONSE_TYPES:
                errors.append(f"{prefix}.response_type is invalid")
            if response_type == "no_response" and record.get("response_evidence_ids"):
                errors.append(f"{prefix} no_response cannot cite response evidence")
            if response_type != "no_response" and not record.get("response_evidence_ids"):
                errors.append(f"{prefix} response type requires response evidence")
            if response_type == "revise" and not record.get("revision_evidence_ids"):
                errors.append(f"{prefix} revise requires revision evidence")
        normalized.append(
            {
                "interpretation": interpretation,
                "status": record.get("status"),
                "role_source_span_ids": role_spans,
                "source_span_ids": list(
                    dict.fromkeys(span for values in role_spans.values() for span in values)
                ),
            }
        )
    if len(interpretations) != len(set(interpretations)):
        errors.append("response contains duplicate interpretations")
    if errors:
        raise ViewSpecificInterfaceError("; ".join(errors))
    return {
        "schema_version": RESPONSE_SCHEMA_VERSION,
        "status": status,
        "view_kind": view_kind,
        "records": normalized,
        "source_alias_custody_validated": True,
        "semantic_adequacy_validated": False,
    }


def aliases_for_evidence(
    *,
    evidence: Sequence[Mapping[str, Any]],
    wrapper: Mapping[str, Any],
    catalog: SourceCatalog,
) -> list[str]:
    span_to_alias = {item["span_id"]: item["alias"] for item in wrapper["evidence_alias_map"]}
    aliases: list[str] = []
    for item in evidence:
        turns = [
            span
            for span in catalog.spans
            if span.kind == "turn"
            and span.speaker == item["speaker"]
            and span.turn_index == item["turn_index"]
            and item["quote"] in span.text
        ]
        if len(turns) != 1:
            raise ViewSpecificInterfaceError("v2 reviewed quote does not resolve to one turn")
        turn = turns[0]
        start = turn.text.index(item["quote"])
        end = start + len(item["quote"])
        spans = [
            span
            for span in catalog.spans
            if span.kind == "sentence"
            and span.turn_id == turn.turn_id
            and span.char_start < end
            and span.char_end > start
        ]
        if not spans:
            raise ViewSpecificInterfaceError("v2 reviewed quote has no sentence alias")
        aliases.extend(span_to_alias[span.span_id] for span in spans)
    return list(dict.fromkeys(aliases))


def protected_relationship_fixture_response(
    *,
    target: Mapping[str, Any],
    relationship_review: Mapping[str, Any] | None,
    wrapper: Mapping[str, Any],
    catalog: SourceCatalog,
) -> dict[str, Any]:
    """Build one source-reviewed v2 fixture for a failure-derived relationship."""

    view_kind = str(target["view_kind"])
    if view_kind not in {
        "position_and_decision_trajectory",
        "exploration_and_alternatives",
        "challenge_and_revision_response",
    }:
        raise ViewSpecificInterfaceError("v2 relationship fixture only covers changed views")
    role_aliases: dict[str, list[str]] = {}
    for item in target["source_evidence"]:
        role_aliases.setdefault(str(item["role"]), []).extend(
            aliases_for_evidence(evidence=[item], wrapper=wrapper, catalog=catalog)
        )
    record: dict[str, Any] = {
        "interpretation": target["description"],
        "status": "supported",
        "auxiliary_observation_ids": [],
        "limitations": "Same-session source-reviewed development fixture; not independent or exhaustive gold.",
    }
    if view_kind == "position_and_decision_trajectory":
        if not isinstance(relationship_review, Mapping):
            raise ViewSpecificInterfaceError("position relationship review is required")
        record.update(
            {
                "trajectory_type": relationship_review["trajectory_type"],
                "starting_state_evidence_ids": aliases_for_evidence(
                    evidence=relationship_review["starting_state_evidence"],
                    wrapper=wrapper,
                    catalog=catalog,
                ),
                "current_position_evidence_ids": role_aliases.get(
                    "current_position", []
                ),
                "qualification_evidence_ids": role_aliases.get(
                    "qualification", []
                ),
            }
        )
    elif view_kind == "exploration_and_alternatives":
        limit_evidence = [
            item
            for item in target["source_evidence"]
            if item["role"] in {"limit", "conditional_alternative"}
        ]
        record.update(
            {
                "relationship_type": "limit",
                "alternative_evidence_ids": role_aliases.get("alternative", []),
                "attached_condition_or_limit_evidence_ids": aliases_for_evidence(
                    evidence=limit_evidence, wrapper=wrapper, catalog=catalog
                ),
                "attached_condition_or_limit_interpretation": "The alternative is bounded by the source-reviewed condition or limit stated in the cited evidence.",
            }
        )
    else:
        if not isinstance(relationship_review, Mapping):
            raise ViewSpecificInterfaceError("challenge relationship review is required")
        response = [
            *role_aliases.get("response", []),
            *role_aliases.get("revision", []),
        ]
        record.update(
            {
                "challenge_type": relationship_review["challenge_type"],
                "response_type": (
                    "revise" if role_aliases.get("revision") else "acknowledge"
                ),
                "prior_claim_or_frame_evidence_ids": aliases_for_evidence(
                    evidence=relationship_review["prior_claim_or_frame_evidence"],
                    wrapper=wrapper,
                    catalog=catalog,
                ),
                "challenge_evidence_ids": role_aliases.get("challenge", []),
                "response_evidence_ids": list(dict.fromkeys(response)),
                "revision_evidence_ids": role_aliases.get("revision", []),
            }
        )
    payload = {
        "status": "supported",
        "records": [record],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": "One protected development relationship; no quality or final-answer judgment.",
    }
    validate_response_v2(payload, wrapper=wrapper)
    return payload
