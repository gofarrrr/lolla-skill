"""Provider-free local chronological exploration harvesting contracts."""
from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

from .conversation_state_candidates import SourceCatalog, build_source_catalog
from .reasoning_process_view_specific import (
    VIEW_QUESTIONS,
    ViewSpecificInterfaceError,
)
from .reasoning_process_view_specific_v2 import aliases_for_evidence
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


PACKET_SCHEMA = "lolla.reasoning_process_exploration_local_packet.v1"
RESPONSE_SCHEMA = "lolla.reasoning_process_exploration_local_response.v1"
OBSERVATION_SCHEMA = "lolla.reasoning_process_exploration_local_observation.v1"
CASE_RECEIPT_SCHEMA = "lolla.reasoning_process_exploration_local_case_receipt.v1"

RESPONSE_STATUSES = ("supported", "unclear", "not_found")
ITEM_STATUSES = ("supported", "mixed", "unclear")
RELATIONSHIP_TYPES = ("condition", "limit", "tradeoff", "failure_condition", "unclear")

RECORD_FIELD_ORDER = (
    "alternative_interpretation",
    "alternative_evidence_ids",
    "attached_condition_or_limit_interpretation",
    "attached_condition_or_limit_evidence_ids",
    "relationship_type",
    "status",
    "limitations",
)
RECORD_FIELDS = set(RECORD_FIELD_ORDER)
TOP_FIELD_ORDER = ("status", "records", "global_limitations")
TOP_FIELDS = set(TOP_FIELD_ORDER)


def _annotated_lines(
    *, catalog: SourceCatalog, span_to_alias: Mapping[str, str], turn_index: int
) -> tuple[str, list[str]]:
    lines: list[str] = []
    aliases: list[str] = []
    for speaker in ("user", "assistant"):
        sentences = [
            span
            for span in catalog.spans
            if span.kind == "sentence"
            and span.turn_index == turn_index
            and span.speaker == speaker
        ]
        if not sentences:
            continue
        lines.append(f"[Turn {turn_index} {speaker.upper()}]")
        for span in sentences:
            alias = span_to_alias[span.span_id]
            lines.append(f"{alias}\t{span.text}")
            aliases.append(alias)
    return "\n".join(lines), aliases


def build_local_packets(
    *,
    case_id: str,
    source_path: str,
    source_text: str,
    global_alias_map: Sequence[Mapping[str, Any]],
    allow_prior_alternative_citation: bool = False,
) -> list[dict[str, Any]]:
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    span_to_alias = {item["span_id"]: item["alias"] for item in global_alias_map}
    sentence_spans = [span for span in catalog.spans if span.kind == "sentence"]
    if set(span_to_alias) != {span.span_id for span in sentence_spans}:
        raise ViewSpecificInterfaceError("global alias map and source sentences differ")
    turn_indices = sorted({span.turn_index for span in catalog.spans if span.kind == "turn"})
    packets: list[dict[str, Any]] = []
    for turn_index in turn_indices:
        focal_text, focal_aliases = _annotated_lines(
            catalog=catalog, span_to_alias=span_to_alias, turn_index=turn_index
        )
        context_text, context_aliases = (
            _annotated_lines(
                catalog=catalog,
                span_to_alias=span_to_alias,
                turn_index=turn_index - 1,
            )
            if turn_index > turn_indices[0]
            else ("", [])
        )
        if not focal_aliases:
            raise ViewSpecificInterfaceError("local focal pair has no sentence aliases")
        packet = {
            "schema_version": PACKET_SCHEMA,
            "status": "target_blind_provider_free_local_exploration_packet",
            "case_id": case_id,
            "window_id": f"{case_id}-exploration-turn-{turn_index:03d}",
            "view_kind": "exploration_and_alternatives",
            "question": VIEW_QUESTIONS["exploration_and_alternatives"],
            "focal_turn_index": turn_index,
            "source": {
                "source_path": source_path,
                "source_sha256": "sha256:" + sha256_bytes(source_text.encode("utf-8")),
                "conversation_message_count": catalog.message_count,
            },
            "prior_context": {
                "included": bool(context_aliases),
                "citation_allowed": False,
                "alternative_citation_allowed": bool(context_aliases)
                and allow_prior_alternative_citation,
                "attached_limit_citation_allowed": False,
                "annotated_sentence_text": context_text,
                "evidence_aliases": context_aliases,
            },
            "focal_pair": {
                "citation_allowed": True,
                "annotated_sentence_text": focal_text,
                "evidence_aliases": focal_aliases,
            },
            "response_contract": {
                "maximum_records": 2,
                "alternative_and_attached_limit_roles_required": True,
                "prior_context_alternative_citation_allowed": bool(
                    context_aliases
                )
                and allow_prior_alternative_citation,
                "attached_limit_must_be_focal": True,
                "valid_empty_output_allowed": True,
                "free_form_source_quotes_allowed": False,
                "auxiliary_observation_ids_allowed": False,
            },
            "boundary": {
                "protected_target_included": False,
                "source_review_fixture_included": False,
                "auxiliary_ledger_included": False,
                "semantic_prefilter_performed": False,
                "global_synthesis_requested": False,
                "direct_graph_routing_allowed": False,
            },
        }
        wrapper = {
            "packet": packet,
            "focal_alias_map": [
                item for item in global_alias_map if item["alias"] in focal_aliases
            ],
            "context_alias_map": [
                item for item in global_alias_map if item["alias"] in context_aliases
            ],
            "metrics": {
                "input_utf8_bytes": len(canonical_json_bytes(packet)),
                "focal_sentence_count": len(focal_aliases),
                "context_sentence_count": len(context_aliases),
                "focal_message_count": sum(
                    1
                    for span in catalog.spans
                    if span.kind == "turn" and span.turn_index == turn_index
                ),
                "future_max_records": 2,
            },
        }
        validate_local_packet(wrapper, source_text=source_text)
        packets.append(wrapper)
    focal_partition = [
        alias
        for wrapper in packets
        for alias in wrapper["packet"]["focal_pair"]["evidence_aliases"]
    ]
    expected_aliases = [item["alias"] for item in global_alias_map]
    if len(focal_partition) != len(set(focal_partition)) or set(focal_partition) != set(
        expected_aliases
    ):
        raise ViewSpecificInterfaceError("local focal aliases do not partition the source")
    return packets


def validate_local_packet(
    wrapper: Mapping[str, Any], *, source_text: str
) -> dict[str, Any]:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("schema_version") != PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid local exploration packet")
    expected_hash = "sha256:" + sha256_bytes(source_text.encode("utf-8"))
    if packet.get("source", {}).get("source_sha256") != expected_hash:
        raise ViewSpecificInterfaceError("local packet source hash drifted")
    focal = packet.get("focal_pair")
    context = packet.get("prior_context")
    if not isinstance(focal, Mapping) or not isinstance(context, Mapping):
        raise ViewSpecificInterfaceError("local packet evidence regions are missing")
    focal_aliases = focal.get("evidence_aliases")
    context_aliases = context.get("evidence_aliases")
    if not isinstance(focal_aliases, list) or not focal_aliases:
        raise ViewSpecificInterfaceError("local focal aliases are missing")
    if not isinstance(context_aliases, list):
        raise ViewSpecificInterfaceError("local context aliases are invalid")
    if set(focal_aliases) & set(context_aliases):
        raise ViewSpecificInterfaceError("focal and context aliases overlap")
    if focal.get("citation_allowed") is not True or context.get("citation_allowed") is not False:
        raise ViewSpecificInterfaceError("local citation boundary drifted")
    if context.get("attached_limit_citation_allowed") is not False:
        raise ViewSpecificInterfaceError("prior context cannot supply the focal attached limit")
    if context.get("alternative_citation_allowed") not in {True, False}:
        raise ViewSpecificInterfaceError("prior alternative citation policy is invalid")
    if context.get("alternative_citation_allowed") is True and not context_aliases:
        raise ViewSpecificInterfaceError("empty prior context cannot be citable")
    if {item["alias"] for item in wrapper.get("focal_alias_map", [])} != set(focal_aliases):
        raise ViewSpecificInterfaceError("local focal alias map drifted")
    if {item["alias"] for item in wrapper.get("context_alias_map", [])} != set(context_aliases):
        raise ViewSpecificInterfaceError("local context alias map drifted")
    if packet.get("boundary") != {
        "protected_target_included": False,
        "source_review_fixture_included": False,
        "auxiliary_ledger_included": False,
        "semantic_prefilter_performed": False,
        "global_synthesis_requested": False,
        "direct_graph_routing_allowed": False,
    }:
        raise ViewSpecificInterfaceError("local packet product boundary drifted")
    if len(canonical_json_bytes(packet)) > 8000:
        raise ViewSpecificInterfaceError("local packet exceeds frozen byte budget")
    return {
        "status": "local_packet_valid",
        "window_id": packet["window_id"],
        "focal_turn_index": packet["focal_turn_index"],
        "focal_sentence_count": len(focal_aliases),
        "context_sentence_count": len(context_aliases),
        "semantic_adequacy_validated": False,
    }


def local_response_schema() -> dict[str, Any]:
    evidence = {
        "type": "array",
        "minItems": 1,
        "maxItems": 6,
        "uniqueItems": True,
        "items": {"type": "string", "minLength": 4, "maxLength": 4},
    }
    record = {
        "type": "object",
        "properties": {
            "alternative_interpretation": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500,
            },
            "alternative_evidence_ids": evidence,
            "attached_condition_or_limit_interpretation": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500,
            },
            "attached_condition_or_limit_evidence_ids": evidence,
            "relationship_type": {
                "type": "string",
                "enum": list(RELATIONSHIP_TYPES),
            },
            "status": {"type": "string", "enum": list(ITEM_STATUSES)},
            "limitations": {"type": "string", "maxLength": 400},
        },
        "required": list(RECORD_FIELD_ORDER),
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "description": "Alternatives introduced or materially developed in one focal turn pair.",
        "properties": {
            "status": {"type": "string", "enum": list(RESPONSE_STATUSES)},
            "records": {
                "type": "array",
                "minItems": 0,
                "maxItems": 2,
                "items": record,
            },
            "global_limitations": {"type": "string", "maxLength": 500},
        },
        "required": list(TOP_FIELD_ORDER),
        "additionalProperties": False,
    }


def build_local_prompts(wrapper: Mapping[str, Any]) -> dict[str, str]:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("schema_version") != PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid packet for local prompt")
    prior_alternative_allowed = packet["prior_context"][
        "alternative_citation_allowed"
    ]
    prior_policy = (
        "Prior-context aliases may be cited only in alternative_evidence_ids when "
        "the focal pair materially qualifies that earlier alternative; the attached "
        "condition or limit must always use focal aliases. "
        if prior_alternative_allowed
        else "The preceding pair is read-only context and its aliases may never be cited. "
    )
    system_prompt = (
        "You are a local reasoning-process exploration harvester. Interpret messy "
        "conversation semantically, but only for the focal user-assistant turn pair. "
        + prior_policy
        +
        "Return at most two materially distinct alternatives introduced or developed "
        "in the focal pair. For each alternative, identify the specifically attached "
        "condition, limit, tradeoff, or failure condition; inspect adjacent focal "
        "sentences and do not substitute a different general risk. Use only visible "
        "focal aliases such as e001, never quotes. Return not_found when no complete "
        "alternative-plus-attached-limit pair is supported. Do not rank options, judge "
        "reasoning quality, evaluate the final answer, merge across windows, or infer "
        "anything from an auxiliary ledger because none is supplied."
    )
    user_prompt = "Local exploration packet:\n" + canonical_json_bytes(packet).decode(
        "utf-8"
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def validate_local_response(
    payload: Mapping[str, Any], *, wrapper: Mapping[str, Any]
) -> dict[str, Any]:
    errors: list[str] = []
    if set(payload) != TOP_FIELDS:
        errors.append("local response fields do not match contract")
    status = payload.get("status")
    records = payload.get("records")
    if status not in RESPONSE_STATUSES:
        errors.append("local response status is invalid")
    if not isinstance(records, list) or len(records) > 2:
        errors.append("local records must be an array of at most two items")
        records = []
    if status == "not_found" and records:
        errors.append("not_found local response must be empty")
    if status == "supported" and not records:
        errors.append("supported local response requires records")
    if not isinstance(payload.get("global_limitations"), str):
        errors.append("local global limitations must be a string")
    focal_aliases = set(wrapper["packet"]["focal_pair"]["evidence_aliases"])
    context_aliases = set(wrapper["packet"]["prior_context"]["evidence_aliases"])
    focal_alias_to_span = {
        item["alias"]: item["span_id"] for item in wrapper["focal_alias_map"]
    }
    context_alias_to_span = {
        item["alias"]: item["span_id"] for item in wrapper["context_alias_map"]
    }
    normalized: list[dict[str, Any]] = []
    evidence_pairs: list[tuple[tuple[str, ...], tuple[str, ...]]] = []
    interpretations: list[str] = []
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, Mapping) or set(record) != RECORD_FIELDS:
            errors.append(f"{prefix} fields do not match contract")
            continue
        alternative = record.get("alternative_interpretation")
        attached = record.get("attached_condition_or_limit_interpretation")
        if not isinstance(alternative, str) or not alternative.strip():
            errors.append(f"{prefix} alternative interpretation is empty")
        else:
            interpretations.append(alternative.strip())
        if not isinstance(attached, str) or not attached.strip():
            errors.append(f"{prefix} attached interpretation is empty")
        if record.get("relationship_type") not in RELATIONSHIP_TYPES:
            errors.append(f"{prefix} relationship type is invalid")
        if record.get("status") not in ITEM_STATUSES:
            errors.append(f"{prefix} status is invalid")
        if not isinstance(record.get("limitations"), str):
            errors.append(f"{prefix} limitations must be a string")
        role_spans: dict[str, list[str]] = {}
        role_aliases: list[tuple[str, ...]] = []
        for role in (
            "alternative_evidence_ids",
            "attached_condition_or_limit_evidence_ids",
        ):
            values = record.get(role)
            if (
                not isinstance(values, list)
                or not values
                or len(values) > 6
                or any(not isinstance(item, str) for item in values)
            ):
                errors.append(f"{prefix}.{role} is invalid")
                values = []
            if len(values) != len(set(values)):
                errors.append(f"{prefix}.{role} contains duplicates")
            role_allows_context = (
                role == "alternative_evidence_ids"
                and wrapper["packet"]["prior_context"][
                    "alternative_citation_allowed"
                ]
                is True
            )
            allowed_aliases = (
                focal_aliases | context_aliases
                if role_allows_context
                else focal_aliases
            )
            if set(values) & context_aliases and not role_allows_context:
                errors.append(f"{prefix}.{role} cites read-only context")
            if not set(values).issubset(allowed_aliases):
                errors.append(f"{prefix}.{role} contains unknown or non-focal aliases")
            role_aliases.append(tuple(values))
            role_spans[role] = [
                (focal_alias_to_span | context_alias_to_span)[item]
                for item in values
                if item in (focal_alias_to_span | context_alias_to_span)
            ]
        evidence_pairs.append((role_aliases[0], role_aliases[1]))
        normalized.append(
            {
                "alternative_interpretation": alternative,
                "attached_condition_or_limit_interpretation": attached,
                "relationship_type": record.get("relationship_type"),
                "status": record.get("status"),
                "limitations": record.get("limitations"),
                "role_source_span_ids": role_spans,
                "source_span_ids": list(
                    dict.fromkeys(span for values in role_spans.values() for span in values)
                ),
            }
        )
    if len(evidence_pairs) != len(set(evidence_pairs)):
        errors.append("local response contains duplicate evidence-role pairs")
    if len(interpretations) != len(set(interpretations)):
        errors.append("local response contains duplicate alternatives")
    if errors:
        raise ViewSpecificInterfaceError("; ".join(errors))
    return {
        "schema_version": RESPONSE_SCHEMA,
        "status": status,
        "window_id": wrapper["packet"]["window_id"],
        "records": normalized,
        "source_alias_custody_validated": True,
        "semantic_adequacy_validated": False,
    }


def protected_local_fixture_response(
    *, target: Mapping[str, Any], wrapper: Mapping[str, Any], catalog: SourceCatalog
) -> dict[str, Any]:
    roles: dict[str, list[str]] = {}
    for evidence in target["source_evidence"]:
        roles.setdefault(str(evidence["role"]), []).extend(
            aliases_for_evidence(evidence=[evidence], wrapper={
                "evidence_alias_map": wrapper["focal_alias_map"]
            }, catalog=catalog)
        )
    limit_aliases = [
        *roles.get("limit", []),
        *roles.get("conditional_alternative", []),
    ]
    response = {
        "status": "supported",
        "records": [
            {
                "alternative_interpretation": target["description"],
                "alternative_evidence_ids": roles.get("alternative", []),
                "attached_condition_or_limit_interpretation": (
                    "The cited focal evidence states the source-reviewed condition or limit attached to this alternative."
                ),
                "attached_condition_or_limit_evidence_ids": limit_aliases,
                "relationship_type": (
                    "condition" if roles.get("conditional_alternative") else "limit"
                ),
                "status": "supported",
                "limitations": "Same-session source-reviewed representation fixture; not independent or exhaustive gold.",
            }
        ],
        "global_limitations": "One protected local relationship; no ranking or quality judgment.",
    }
    validate_local_response(response, wrapper=wrapper)
    return response


def compile_local_response(
    *,
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
    record_identity: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    validated = validate_local_response(response, wrapper=wrapper)
    observations: list[dict[str, Any]] = []
    for index, (raw, record) in enumerate(
        zip(response["records"], validated["records"]), start=1
    ):
        raw_record = {
            "record_identity": record_identity,
            "window_id": wrapper["packet"]["window_id"],
            "record_index": index,
            "record": raw,
            "role_source_span_ids": record["role_source_span_ids"],
        }
        digest = sha256_bytes(canonical_json_bytes(raw_record))
        observation_id = f"explocal-{wrapper['packet']['case_id']}-{wrapper['packet']['focal_turn_index']:03d}-{index:02d}-{digest[:10]}"
        observations.append(
            {
                "schema_version": OBSERVATION_SCHEMA,
                "observation_id": observation_id,
                "case_id": wrapper["packet"]["case_id"],
                "window_id": wrapper["packet"]["window_id"],
                "focal_turn_index": wrapper["packet"]["focal_turn_index"],
                "family": "exploration_and_alternatives",
                "alternative_interpretation": record["alternative_interpretation"],
                "attached_condition_or_limit_interpretation": record[
                    "attached_condition_or_limit_interpretation"
                ],
                "relationship_type": record["relationship_type"],
                "semantic_status": record["status"],
                "role_source_span_ids": record["role_source_span_ids"],
                "source_span_ids": record["source_span_ids"],
                "raw_record": raw_record,
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
                "terminal_reason": "local pair roles and focal stable aliases validated",
                "cross_window_semantic_duplicate_status": "not_assessed",
                "graph_routing_eligible": False,
            }
        )
    return {
        "status": "local_response_compiled",
        "window_id": wrapper["packet"]["window_id"],
        "response_status": validated["status"],
        "observations": observations,
        "window_terminal_disposition": (
            "reviewed_empty" if validated["status"] == "not_found" else "compiled"
        ),
        "boundary": {
            "semantic_merge_performed": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def build_case_receipt(
    *,
    case_id: str,
    source_path: str,
    source_text: str,
    packets: Sequence[Mapping[str, Any]],
    protected_compilation: Mapping[str, Any],
) -> dict[str, Any]:
    protected_window = protected_compilation["window_id"]
    windows = []
    observations = []
    for wrapper in packets:
        window_id = wrapper["packet"]["window_id"]
        is_protected = window_id == protected_window
        if is_protected:
            observations.extend(protected_compilation["observations"])
        windows.append(
            {
                "window_id": window_id,
                "focal_turn_index": wrapper["packet"]["focal_turn_index"],
                "focal_aliases": wrapper["packet"]["focal_pair"]["evidence_aliases"],
                "prior_context_aliases": wrapper["packet"]["prior_context"][
                    "evidence_aliases"
                ],
                "provider_free_disposition": (
                    "source_review_fixture_compiled"
                    if is_protected
                    else "not_semantically_reviewed_under_provider_free_contract"
                ),
                "observation_ids": (
                    [item["observation_id"] for item in protected_compilation["observations"]]
                    if is_protected
                    else []
                ),
            }
        )
    return {
        "schema_version": CASE_RECEIPT_SCHEMA,
        "status": "provider_free_local_exploration_representation",
        "case_id": case_id,
        "source": {
            "source_path": source_path,
            "source_sha256": "sha256:" + hashlib.sha256(
                source_text.encode("utf-8")
            ).hexdigest(),
            "authoritative_conversation_preserved_elsewhere": True,
        },
        "windows": windows,
        "ordered_source_review_fixture_observations": observations,
        "custody": {
            "every_window_has_provider_free_disposition": True,
            "focal_aliases_partition_source": True,
            "context_aliases_are_non_citable": True,
            "unreviewed_window_is_not_claimed_empty": True,
            "cross_window_semantic_duplicates_preserved": True,
            "semantic_deduplication_performed": False,
            "global_synthesis_performed": False,
            "direct_graph_routing_allowed": False,
        },
        "boundary": {
            "semantic_exhaustiveness_validated": False,
            "source_review_fixture_is_independent_gold": False,
            "final_output_evaluated": False,
            "quality_score_included": False,
        },
    }
