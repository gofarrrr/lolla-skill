"""Provider-free view-specific semantic interfaces after Phase-3 failure.

This module keeps semantic interpretation probabilistic while making each
bounded job declare the evidence roles its question actually needs.  Models
select visible aliases from a complete annotated sentence table; deterministic
code maps aliases to stable source spans, validates role completeness, expands
dispositions, and preserves append-only custody.
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from .conversation_state_candidates import SourceCatalog, SourceSpan, build_source_catalog
from .reasoning_process_contracts import (
    BOUNDED_VIEW_SCHEMA_VERSION,
    OBSERVATION_FAMILIES,
    VIEW_STATUS,
    phase0_contract,
    validate_bounded_view,
)
from .reasoning_process_views import (
    canonical_json_bytes,
    sha256_bytes,
)


INPUT_SCHEMA_VERSION = "lolla.reasoning_process_view_specific_input.v1"
RESPONSE_SCHEMA_VERSION = "lolla.reasoning_process_view_specific_response.v1"
FIXTURE_OBSERVATION_SCHEMA_VERSION = (
    "lolla.reasoning_process_view_specific_fixture_addendum.v1"
)
MODEL_OBSERVATION_SCHEMA_VERSION = (
    "lolla.reasoning_process_view_specific_model_addendum.v1"
)
COMPILED_FIXTURE_SCHEMA_VERSION = "lolla.reasoning_process_view_specific_fixture.v1"

RESPONSE_STATUSES = ("supported", "mixed", "unclear", "not_found")
ITEM_STATUSES = ("supported", "mixed", "unclear")
CHALLENGE_RESPONSE_TYPES = (
    "acknowledge",
    "qualify",
    "revise",
    "defer",
    "reject",
    "no_response",
    "mixed",
)

VIEW_QUESTIONS = {
    "position_and_decision_trajectory": "How did the working position or decision change, and what qualification remains capable of changing it?",
    "exploration_and_alternatives": "Which materially distinct alternatives were explored, and what limitation accompanied each one?",
    "evidence_and_assumption_discipline": "Which claims or inputs were considered, and what evidence-strength boundary kept each from becoming a stronger claim?",
    "uncertainty_and_unresolved_state": "What remained unresolved, and what preserved it as open or capable of reopening the direction?",
    "challenge_and_revision_response": "Which material challenge was raised, how did the reasoning respond, and what changed or did not change?",
}

VIEW_INSTRUCTIONS = {
    "position_and_decision_trajectory": (
        "Return up to four materially distinct working positions or decisions. "
        "For each record, cite position evidence separately from evidence that "
        "qualifies, limits, or could still change that position."
    ),
    "exploration_and_alternatives": (
        "Return up to four materially distinct alternatives that the conversation "
        "actually explored. For each record, cite the alternative separately from "
        "its condition, limit, tradeoff, or failure condition."
    ),
    "evidence_and_assumption_discipline": (
        "Return up to four claims, inputs, or observations whose evidential status "
        "matters. For each record, cite the claim or input separately from the "
        "language that bounds its strength or keeps it from becoming a stronger claim."
    ),
    "uncertainty_and_unresolved_state": (
        "Return up to four unresolved matters. For each record, cite the unresolved "
        "matter separately from evidence that preserves it as open or states how it "
        "could reopen the direction."
    ),
    "challenge_and_revision_response": (
        "Return up to four material challenges or corrections. For each record, cite "
        "the challenge separately from the response and, when the response revised "
        "the reasoning, from evidence of the revision. Use no_response only when the "
        "visible conversation contains no response."
    ),
}

ROLE_FIELDS = {
    "position_and_decision_trajectory": (
        "position_evidence_ids",
        "qualification_evidence_ids",
    ),
    "exploration_and_alternatives": (
        "alternative_evidence_ids",
        "limitation_evidence_ids",
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
        "challenge_evidence_ids",
        "response_evidence_ids",
        "revision_evidence_ids",
    ),
}

_BASE_RECORD_FIELDS = {
    "interpretation",
    "status",
    "auxiliary_observation_ids",
    "limitations",
}
_TOP_FIELDS = {
    "status",
    "records",
    "park_unselected_auxiliary_observations",
    "global_limitations",
}
_ALIAS_RE = re.compile(r"^e[0-9]{3}$")


class ViewSpecificInterfaceError(ValueError):
    """Raised when a view-specific packet, response, or fixture is invalid."""


def _normalize_ws(value: str) -> str:
    return " ".join(value.split())


def _compact_observations(
    observations: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "observation_id": item["observation_id"],
            "family": item["family"],
            "interpretation": item["interpretation"],
            "semantic_status": item["semantic_status"],
            "source_span_ids": item["source_span_ids"],
        }
        for item in observations
    ]


def build_annotated_reader_packet(
    *,
    case_id: str,
    view_kind: str,
    question: str,
    source_path: str,
    source_text: str,
    base_observations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build complete sentence content with compact visible evidence aliases."""

    if view_kind not in OBSERVATION_FAMILIES:
        raise ViewSpecificInterfaceError("invalid view kind")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    sentences = [span for span in catalog.spans if span.kind == "sentence"]
    turns = [span for span in catalog.spans if span.kind == "turn"]
    sentence_by_turn: dict[str, list[SourceSpan]] = {}
    for span in sentences:
        sentence_by_turn.setdefault(span.turn_id, []).append(span)
    for turn in turns:
        reconstructed = " ".join(
            span.text for span in sentence_by_turn.get(turn.turn_id, [])
        )
        if _normalize_ws(reconstructed) != _normalize_ws(turn.text):
            raise ViewSpecificInterfaceError(
                f"sentence table does not preserve complete turn content: {turn.turn_id}"
            )

    lines: list[str] = []
    alias_map: list[dict[str, Any]] = []
    last_turn = ""
    for index, span in enumerate(sentences, start=1):
        alias = f"e{index:03d}"
        if span.turn_id != last_turn:
            lines.append(
                f"[Turn {span.turn_index} {span.speaker.upper()}]"
            )
            last_turn = span.turn_id
        lines.append(f"{alias}\t{span.text}")
        alias_map.append(
            {
                "alias": alias,
                "span_id": span.span_id,
                "turn_index": span.turn_index,
                "speaker": span.speaker,
                "text_sha256": sha256_bytes(span.text.encode("utf-8")),
            }
        )
    compact_observations = _compact_observations(base_observations)
    source_hash = sha256_bytes(source_text.encode("utf-8"))

    def packet(*, include_auxiliary: bool) -> dict[str, Any]:
        return {
            "schema_version": INPUT_SCHEMA_VERSION,
            "status": "provider_free_target_blind_view_specific_fixture",
            "case_id": case_id,
            "view_kind": view_kind,
            "question": question,
            "source": {
                "source_path": source_path,
                "source_sha256": "sha256:" + source_hash,
                "message_count": catalog.message_count,
                "sentence_count": len(sentences),
                "annotated_sentence_text": "\n".join(lines),
            },
            "auxiliary_phase1_ledger": {
                "policy": "include_whole_or_omit_whole_by_mechanical_byte_budget",
                "included": include_auxiliary,
                "observations": compact_observations if include_auxiliary else [],
                **(
                    {}
                    if include_auxiliary
                    else {
                        "omission_reason": "complete auxiliary ledger would exceed the frozen input-byte ceiling; no semantic subset was selected"
                    }
                ),
            },
            "response_contract": {
                "select_visible_evidence_aliases_only": True,
                "free_form_source_quotes_allowed": False,
                "view_specific_semantic_roles_required": True,
                "valid_empty_output_allowed": True,
            },
            "boundary": {
                "authoritative_source_referenced": True,
                "complete_message_content_visible": True,
                "protected_target_included": False,
                "source_review_addendum_included": False,
                "semantic_prefilter_performed": False,
                "final_output_evaluated": False,
                "direct_graph_routing_allowed": False,
            },
        }

    hard_bytes = phase0_contract()["numeric_gates"]["max_view_input_utf8_bytes"]
    reader_packet = packet(include_auxiliary=True)
    full_bytes = len(canonical_json_bytes(reader_packet))
    auxiliary_omitted = False
    if full_bytes > hard_bytes:
        reader_packet = packet(include_auxiliary=False)
        auxiliary_omitted = True
    observed_bytes = len(canonical_json_bytes(reader_packet))
    if observed_bytes > hard_bytes:
        raise ViewSpecificInterfaceError(
            "complete annotated sentence source exceeds frozen byte ceiling"
        )
    wrapper = {
        "reader_packet": reader_packet,
        "evidence_alias_map": alias_map,
        "metrics": {
            "source_message_count": catalog.message_count,
            "source_sentence_count": len(sentences),
            "source_content_complete": True,
            "observed_input_utf8_bytes": observed_bytes,
            "max_input_utf8_bytes": hard_bytes,
            "budget_exceeded": False,
            "auxiliary_observation_count_available": len(compact_observations),
            "auxiliary_observation_count_included": (
                0 if auxiliary_omitted else len(compact_observations)
            ),
            "auxiliary_ledger_omitted_whole": auxiliary_omitted,
        },
    }
    validate_annotated_reader_packet(wrapper, source_text=source_text)
    return wrapper


def validate_annotated_reader_packet(
    wrapper: Mapping[str, Any], *, source_text: str
) -> dict[str, Any]:
    packet = wrapper.get("reader_packet")
    aliases = wrapper.get("evidence_alias_map")
    metrics = wrapper.get("metrics")
    if not isinstance(packet, Mapping) or packet.get("schema_version") != INPUT_SCHEMA_VERSION:
        raise ViewSpecificInterfaceError("invalid reader packet")
    if packet.get("view_kind") not in OBSERVATION_FAMILIES:
        raise ViewSpecificInterfaceError("invalid reader packet view kind")
    source = packet.get("source")
    if not isinstance(source, Mapping):
        raise ViewSpecificInterfaceError("reader packet source is missing")
    if source.get("source_sha256") != "sha256:" + sha256_bytes(
        source_text.encode("utf-8")
    ):
        raise ViewSpecificInterfaceError("reader packet source hash drifted")
    if not isinstance(aliases, list) or not aliases:
        raise ViewSpecificInterfaceError("evidence alias map is missing")
    alias_ids = [item.get("alias") for item in aliases if isinstance(item, Mapping)]
    span_ids = [item.get("span_id") for item in aliases if isinstance(item, Mapping)]
    if len(alias_ids) != len(aliases) or len(alias_ids) != len(set(alias_ids)):
        raise ViewSpecificInterfaceError("evidence aliases must be unique")
    if len(span_ids) != len(set(span_ids)):
        raise ViewSpecificInterfaceError("evidence aliases must map one-to-one to spans")
    if any(not isinstance(alias, str) or not _ALIAS_RE.fullmatch(alias) for alias in alias_ids):
        raise ViewSpecificInterfaceError("evidence alias format is invalid")
    annotated = str(source.get("annotated_sentence_text", ""))
    for alias in alias_ids:
        if annotated.count(alias + "\t") != 1:
            raise ViewSpecificInterfaceError("annotated source and alias map differ")
    if source.get("sentence_count") != len(aliases):
        raise ViewSpecificInterfaceError("sentence count and alias map differ")
    boundary = packet.get("boundary")
    if not isinstance(boundary, Mapping) or any(
        boundary.get(key) is not expected
        for key, expected in {
            "authoritative_source_referenced": True,
            "complete_message_content_visible": True,
            "protected_target_included": False,
            "source_review_addendum_included": False,
            "semantic_prefilter_performed": False,
            "final_output_evaluated": False,
            "direct_graph_routing_allowed": False,
        }.items()
    ):
        raise ViewSpecificInterfaceError("reader packet boundary drifted")
    if not isinstance(metrics, Mapping):
        raise ViewSpecificInterfaceError("reader packet metrics are missing")
    observed_bytes = len(canonical_json_bytes(packet))
    if metrics.get("observed_input_utf8_bytes") != observed_bytes:
        raise ViewSpecificInterfaceError("reader packet byte metric drifted")
    if metrics.get("budget_exceeded") is not False or observed_bytes > 24000:
        raise ViewSpecificInterfaceError("reader packet exceeds byte budget")
    return {
        "status": "provider_free_packet_valid",
        "case_id": packet.get("case_id"),
        "view_kind": packet["view_kind"],
        "message_count": source.get("message_count"),
        "sentence_count": len(aliases),
        "input_utf8_bytes": observed_bytes,
        "auxiliary_ledger_included": packet["auxiliary_phase1_ledger"]["included"],
        "semantic_adequacy_validated": False,
    }


def _evidence_id_array(*, allow_empty: bool = False) -> dict[str, Any]:
    return {
        "type": "array",
        "minItems": 0 if allow_empty else 1,
        "maxItems": 6,
        "uniqueItems": True,
        "items": {"type": "string", "minLength": 4, "maxLength": 4},
    }


def view_specific_response_schema(view_kind: str) -> dict[str, Any]:
    if view_kind not in OBSERVATION_FAMILIES:
        raise ViewSpecificInterfaceError("invalid schema view kind")
    record_properties: dict[str, Any] = {
        "interpretation": {
            "type": "string",
            "minLength": 1,
            "maxLength": 700,
        },
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
    for role_field in ROLE_FIELDS[view_kind]:
        record_properties[role_field] = _evidence_id_array(
            allow_empty=(
                view_kind == "challenge_and_revision_response"
                and role_field in {"response_evidence_ids", "revision_evidence_ids"}
            )
        )
    if view_kind == "challenge_and_revision_response":
        record_properties["response_type"] = {
            "type": "string",
            "enum": list(CHALLENGE_RESPONSE_TYPES),
        }
    required = list(record_properties)
    return {
        "type": "object",
        "description": f"Bounded {view_kind} response using visible evidence aliases.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 4,
                "items": {
                    "type": "object",
                    "properties": record_properties,
                    "required": required,
                    "additionalProperties": False,
                },
            },
            "park_unselected_auxiliary_observations": {
                "type": "boolean",
                "const": True,
            },
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


def build_view_specific_prompts(wrapper: Mapping[str, Any]) -> dict[str, str]:
    """Build target-blind prompts for a later authorized model probe."""

    packet = wrapper.get("reader_packet")
    if not isinstance(packet, Mapping):
        raise ViewSpecificInterfaceError("reader packet is missing")
    view_kind = str(packet.get("view_kind", ""))
    if view_kind not in VIEW_INSTRUCTIONS:
        raise ViewSpecificInterfaceError("invalid prompt view kind")
    system_prompt = (
        "You are a bounded reasoning-process reader. Interpret messy conversation "
        "semantically; do not score its quality, effort, trustworthiness, or final "
        "recommendation. Scan the complete annotated conversation chronologically. "
        "Use only visible evidence aliases such as e001. Never copy or invent source "
        "quotes. Treat the auxiliary ledger as fallible context, not as authoritative "
        "truth. Distinguish what the conversation supports from your interpretation, "
        "preserve uncertainty, and return not_found when the requested process event "
        "is not visible. Unselected auxiliary observations remain parked and recoverable."
    )
    user_prompt = (
        f"Question: {packet['question']}\n\n"
        f"Task contract: {VIEW_INSTRUCTIONS[view_kind]}\n\n"
        "Reader packet:\n"
        + canonical_json_bytes(packet).decode("utf-8")
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def validate_view_specific_response(
    payload: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    packet = wrapper["reader_packet"]
    view_kind = str(packet["view_kind"])
    errors: list[str] = []
    if set(payload) != _TOP_FIELDS:
        errors.append("response fields do not match the view-specific contract")
    status = payload.get("status")
    if status not in RESPONSE_STATUSES:
        errors.append("response status is invalid")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) > 4:
        errors.append("records must be an array of at most four items")
        records = []
    if status == "not_found" and records:
        errors.append("not_found response must have no records")
    if status != "not_found" and not records:
        errors.append("non-empty status requires at least one record")
    if payload.get("park_unselected_auxiliary_observations") is not True:
        errors.append("reader must explicitly park unselected auxiliary observations")
    if not isinstance(payload.get("global_limitations"), str) or len(
        payload.get("global_limitations", "")
    ) > 700:
        errors.append("global limitations must be a string")
    alias_to_span = {
        item["alias"]: item["span_id"] for item in wrapper["evidence_alias_map"]
    }
    allowed_auxiliary = {
        item["observation_id"]
        for item in packet["auxiliary_phase1_ledger"]["observations"]
    }
    role_fields = ROLE_FIELDS[view_kind]
    expected_record_fields = _BASE_RECORD_FIELDS | set(role_fields)
    if view_kind == "challenge_and_revision_response":
        expected_record_fields.add("response_type")
    normalized_records: list[dict[str, Any]] = []
    interpretations: list[str] = []
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, Mapping) or set(record) != expected_record_fields:
            errors.append(f"{prefix} fields do not match the view-specific contract")
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
        auxiliary_ids = record.get("auxiliary_observation_ids")
        if (
            not isinstance(auxiliary_ids, list)
            or len(auxiliary_ids) > 8
            or any(not isinstance(item, str) for item in auxiliary_ids)
        ):
            errors.append(f"{prefix}.auxiliary_observation_ids is invalid")
            auxiliary_ids = []
        if len(auxiliary_ids) != len(set(auxiliary_ids)):
            errors.append(f"{prefix}.auxiliary_observation_ids contains duplicates")
        if not set(auxiliary_ids).issubset(allowed_auxiliary):
            errors.append(f"{prefix}.auxiliary_observation_ids contains unknown IDs")
        normalized_roles: dict[str, list[str]] = {}
        all_aliases: list[str] = []
        response_type = record.get("response_type")
        if view_kind == "challenge_and_revision_response":
            if response_type not in CHALLENGE_RESPONSE_TYPES:
                errors.append(f"{prefix}.response_type is invalid")
        for role_field in role_fields:
            aliases = record.get(role_field)
            allow_empty = (
                view_kind == "challenge_and_revision_response"
                and role_field in {"response_evidence_ids", "revision_evidence_ids"}
            )
            if (
                not isinstance(aliases, list)
                or len(aliases) > 6
                or any(not isinstance(item, str) for item in aliases)
            ):
                errors.append(f"{prefix}.{role_field} is invalid")
                aliases = []
            if not allow_empty and not aliases:
                errors.append(f"{prefix}.{role_field} must not be empty")
            if len(aliases) != len(set(aliases)):
                errors.append(f"{prefix}.{role_field} contains duplicates")
            if not set(aliases).issubset(alias_to_span):
                errors.append(f"{prefix}.{role_field} contains unknown evidence aliases")
            normalized_roles[role_field] = [alias_to_span[item] for item in aliases if item in alias_to_span]
            all_aliases.extend(aliases)
        if view_kind == "challenge_and_revision_response":
            if response_type == "no_response" and record.get("response_evidence_ids"):
                errors.append(f"{prefix} no_response cannot cite response evidence")
            if response_type != "no_response" and not record.get("response_evidence_ids"):
                errors.append(f"{prefix} response type requires response evidence")
            if response_type == "revise" and not record.get("revision_evidence_ids"):
                errors.append(f"{prefix} revise requires revision evidence")
        normalized_records.append(
            {
                "interpretation": interpretation,
                "status": record.get("status"),
                "auxiliary_observation_ids": auxiliary_ids,
                "limitations": record.get("limitations"),
                "response_type": response_type,
                "role_source_span_ids": normalized_roles,
                "source_span_ids": list(
                    dict.fromkeys(alias_to_span[item] for item in all_aliases if item in alias_to_span)
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
        "records": normalized_records,
        "park_unselected_auxiliary_observations": True,
        "global_limitations": payload["global_limitations"],
        "source_alias_custody_validated": True,
        "semantic_adequacy_validated": False,
    }


def protected_fixture_response(
    *, target: Mapping[str, Any], wrapper: Mapping[str, Any], catalog: SourceCatalog
) -> dict[str, Any]:
    """Project a frozen source-reviewed target into its matching semantic roles."""

    view_kind = str(target["view_kind"])
    span_to_alias = {
        item["span_id"]: item["alias"] for item in wrapper["evidence_alias_map"]
    }
    role_aliases: dict[str, list[str]] = {}
    for evidence in target["source_evidence"]:
        matching_turns = [
            span
            for span in catalog.spans
            if span.kind == "turn"
            and span.speaker == evidence["speaker"]
            and span.turn_index == evidence["turn_index"]
            and evidence["quote"] in span.text
        ]
        if len(matching_turns) != 1:
            raise ViewSpecificInterfaceError("protected quote does not resolve to one turn")
        turn = matching_turns[0]
        start = turn.text.index(evidence["quote"])
        end = start + len(evidence["quote"])
        supporting_sentences = [
            span
            for span in catalog.spans
            if span.kind == "sentence"
            and span.turn_id == turn.turn_id
            and span.char_start < end
            and span.char_end > start
        ]
        if not supporting_sentences:
            raise ViewSpecificInterfaceError("protected quote has no sentence aliases")
        role_aliases.setdefault(str(evidence["role"]), []).extend(
            span_to_alias[span.span_id] for span in supporting_sentences
        )

    record: dict[str, Any] = {
        "interpretation": target["description"],
        "status": "supported",
        "auxiliary_observation_ids": [],
        "limitations": "Source-reviewed same-session development fixture; not independent gold or model-quality evidence.",
    }
    if view_kind == "position_and_decision_trajectory":
        record["position_evidence_ids"] = role_aliases.get("current_position", [])
        record["qualification_evidence_ids"] = role_aliases.get("qualification", [])
    elif view_kind == "exploration_and_alternatives":
        record["alternative_evidence_ids"] = role_aliases.get("alternative", [])
        record["limitation_evidence_ids"] = [
            *role_aliases.get("limit", []),
            *role_aliases.get("conditional_alternative", []),
        ]
    elif view_kind == "evidence_and_assumption_discipline":
        claim_roles = {
            "bounded_claim",
            "reported_response",
            "confound",
            "observation",
            "evidence",
        }
        boundary_roles = {"qualification", "evidence_boundary"}
        record["claim_or_input_evidence_ids"] = [
            alias for role in claim_roles for alias in role_aliases.get(role, [])
        ]
        record["boundary_evidence_ids"] = [
            alias for role in boundary_roles for alias in role_aliases.get(role, [])
        ]
    elif view_kind == "uncertainty_and_unresolved_state":
        record["unresolved_evidence_ids"] = role_aliases.get("unresolved", [])
        record["preservation_or_reopen_evidence_ids"] = role_aliases.get(
            "preserved_uncertainty", []
        )
        record["preservation_or_reopen_evidence_ids"].extend(
            role_aliases.get("deadline_risk", [])
        )
    else:
        record["challenge_evidence_ids"] = role_aliases.get("challenge", [])
        record["response_evidence_ids"] = [
            *role_aliases.get("response", []),
            *role_aliases.get("revision", []),
        ]
        record["revision_evidence_ids"] = role_aliases.get("revision", [])
        record["response_type"] = (
            "revise" if record["revision_evidence_ids"] else "acknowledge"
        )
    response = {
        "status": "supported",
        "records": [record],
        "park_unselected_auxiliary_observations": True,
        "global_limitations": "One protected development target; not exhaustive gold and not a reasoning-quality judgment.",
    }
    validate_view_specific_response(response, wrapper=wrapper)
    return response


def compile_protected_fixture(
    *,
    target: Mapping[str, Any],
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    base_ledger: Mapping[str, Any],
    catalog: SourceCatalog,
    producer_kind: str = "source_reviewer",
    producer_id: str = "view-specific-same-session-nonblind",
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    validated = validate_view_specific_response(response, wrapper=wrapper)
    packet = wrapper["reader_packet"]
    view_kind = str(packet["view_kind"])
    case_id = str(packet["case_id"])
    base_observations = base_ledger["observations"]
    fixture_observations: list[dict[str, Any]] = []
    view_items: list[dict[str, Any]] = []
    for index, record in enumerate(validated["records"], start=1):
        model_backed = producer_kind == "model"
        id_prefix = "view-specific-model" if model_backed else "view-specific-fixture"
        observation_id = f"{id_prefix}-{target['target_id']}-{index:03d}"
        item_id = f"{id_prefix}-view-item-{target['target_id']}-{index:03d}"
        raw_record = {
            "target_id": target["target_id"],
            "view_kind": view_kind,
            "validated_record": record,
        }
        fixture_observations.append(
            {
                "observation_id": observation_id,
                "family": view_kind,
                "family_projection_status": (
                    "view_specific_model_interpretation"
                    if model_backed
                    else "view_specific_source_review_fixture"
                ),
                "interpretation": record["interpretation"],
                "semantic_status": record["status"],
                "source_span_ids": record["source_span_ids"],
                "source_artifact_id": (
                    "view-specific-model-probe"
                    if model_backed
                    else "view-specific-protected-fixtures"
                ),
                "source_record_id": str(target["target_id"]),
                "source_family": view_kind,
                "raw_record_sha256": "sha256:" + sha256_bytes(canonical_json_bytes(raw_record)),
                "raw_record": raw_record,
                "provenance": {
                    "producer_kind": producer_kind,
                    "producer_id": producer_id,
                    "call_id": (call_metadata or {}).get("call_id", ""),
                    "model": (call_metadata or {}).get("model", ""),
                    "prompt_sha256": (call_metadata or {}).get(
                        "prompt_sha256", ""
                    ),
                },
                "state_history": [
                    {
                        "state": "proposed",
                        "reason": (
                            "target-blind view-specific model proposal"
                            if model_backed
                            else "prospectively frozen view-specific protected fixture"
                        ),
                        "actor": producer_kind,
                    },
                    {
                        "state": "admitted",
                        "reason": "view-specific shape and stable source aliases validated",
                        "actor": "deterministic_validator",
                    },
                ],
                "terminal_state": "admitted",
                "terminal_reason": (
                    "model interpretation passed typed stable-alias validation"
                    if model_backed
                    else "provider-free protected fixture with exact stable source spans"
                ),
                "relations": [],
                "graph_routing_eligible": False,
            }
        )
        view_items.append(
            {
                "view_item_id": item_id,
                "interpretation": record["interpretation"],
                "status": record["status"],
                "source_observation_ids": [observation_id],
                "source_span_ids": record["source_span_ids"],
                "limitations": record["limitations"],
            }
        )
    addendum = {
        "schema_version": (
            MODEL_OBSERVATION_SCHEMA_VERSION
            if producer_kind == "model"
            else FIXTURE_OBSERVATION_SCHEMA_VERSION
        ),
        "status": (
            "model_backed_view_specific_addendum"
            if producer_kind == "model"
            else "provider_free_view_specific_fixture"
        ),
        "case_id": case_id,
        "view_kind": view_kind,
        "target_id": target["target_id"],
        "observations": fixture_observations,
        "boundary": {
            "phase1_ledger_modified": False,
            "source_review_is_independent_gold": False,
            "semantic_relevance_inferred_by_code": False,
            "direct_graph_routing_allowed": False,
        },
    }
    addendum_sha = sha256_bytes(canonical_json_bytes(addendum))
    combined = [*base_observations, *fixture_observations]
    manifest = {
        "case_id": case_id,
        "view_kind": view_kind,
        "base_ledger_sha256": "sha256:" + hashlib.sha256(
            canonical_json_bytes(base_ledger)
        ).hexdigest(),
        "fixture_addendum_sha256": "sha256:" + addendum_sha,
        "observation_ids": [item["observation_id"] for item in combined],
    }
    manifest_sha = sha256_bytes(canonical_json_bytes(manifest))
    dispositions = [
        {
            "observation_id": observation["observation_id"],
            "disposition": "parked_not_applicable",
            "authority": producer_kind,
            "reason": "This protected fixture tests the new semantic role contract; the base observation remains recoverable and was not required for its one target.",
            "view_item_ids": [],
        }
        for observation in base_observations
    ]
    dispositions.extend(
        {
            "observation_id": observation["observation_id"],
            "disposition": "included",
            "authority": producer_kind,
            "reason": (
                "This target-blind model observation produced the view item."
                if producer_kind == "model"
                else "This source-reviewed view-specific fixture observation produced the protected view item."
            ),
            "view_item_ids": [item["view_item_id"]],
        }
        for observation, item in zip(fixture_observations, view_items)
    )
    projection = _compact_observations(combined)
    input_bytes = len(canonical_json_bytes({"observations": projection}))
    gates = phase0_contract()["numeric_gates"]
    view = {
        "schema_version": BOUNDED_VIEW_SCHEMA_VERSION,
        "status": VIEW_STATUS,
        "view_id": f"view-specific-{target['target_id']}",
        "view_kind": view_kind,
        "question": str(packet["question"]),
        "source_ledger_sha256": "sha256:" + manifest_sha,
        "input": {
            "ledger_observation_ids": [item["observation_id"] for item in combined]
        },
        "items": view_items,
        "dispositions": dispositions,
        "budget": {
            "max_input_observations": gates["max_view_input_observations"],
            "max_input_utf8_bytes": gates["max_view_input_utf8_bytes"],
            "max_output_items": gates["max_view_output_items"],
            "observed_input_observations": len(combined),
            "observed_input_utf8_bytes": input_bytes,
            "observed_output_items": len(view_items),
            "budget_exceeded": (
                len(combined) > gates["max_view_input_observations"]
                or input_bytes > gates["max_view_input_utf8_bytes"]
                or len(view_items) > gates["max_view_output_items"]
            ),
        },
        "boundary": {
            "authoritative_source": False,
            "semantic_selection_performed_by_code": False,
            "omissions_recoverable_from_ledger": True,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
    }
    validation = validate_bounded_view(
        view,
        known_ledger_observation_ids=[item["observation_id"] for item in combined],
        known_span_ids=catalog.by_id(),
        expected_ledger_sha256="sha256:" + manifest_sha,
    )
    return {
        "schema_version": COMPILED_FIXTURE_SCHEMA_VERSION,
        "status": (
            "model_backed_view_specific_response_compiled"
            if producer_kind == "model"
            else "provider_free_view_specific_fixture_pass"
        ),
        "target_id": target["target_id"],
        "fixture_addendum": addendum,
        "fixture_addendum_sha256": addendum_sha,
        "combined_manifest": manifest,
        "combined_manifest_sha256": manifest_sha,
        "view": view,
        "view_validation": validation,
        "boundary": {
            "semantic_correctness_validated": False,
            "source_review_is_independent_gold": False,
            "provider_calls": 1 if producer_kind == "model" else 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
    }
