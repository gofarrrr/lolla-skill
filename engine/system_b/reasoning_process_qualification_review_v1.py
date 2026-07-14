"""Independent qualification review and exact decomposed-role custody join.

The model decides whether an unresolved qualification remains and cites the
source. Code validates only the declared outcome, evidence custody, role
portfolio bounds, and explicit consistency. It does not read prose to infer or
repair semantic meaning.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_position_role_first_v23 import ROLE_BOUNDARY_CONTRACTS
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


PACKET_SCHEMA = "lolla.reasoning_process_qualification_review_packet.v1"
RESPONSE_SCHEMA = "lolla.reasoning_process_qualification_review_response.v1"
JOIN_SCHEMA = "lolla.reasoning_process_decomposed_current_qualification_join.v1"
OUTCOMES = (
    "unresolved_qualification_present",
    "no_unresolved_qualification_observed",
    "ambiguous_qualification_review",
)


def _position_packet(wrapper: Mapping[str, Any]) -> Mapping[str, Any]:
    packet = wrapper.get("packet")
    if not isinstance(packet, Mapping) or packet.get("view_kind") != (
        "position_and_decision_trajectory"
    ):
        raise ViewSpecificInterfaceError("qualification review requires a position wrapper")
    return packet


def _alias_map(packet: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for region_name in ("focal_region", "prior_context"):
        region = packet.get(region_name, {})
        if not isinstance(region, Mapping):
            continue
        for line in str(region.get("annotated_sentence_text", "")).splitlines():
            if "\t" not in line:
                continue
            alias, text = line.split("\t", 1)
            if alias.startswith("e") and alias[1:].isdigit():
                result[alias] = text
    return result


def build_qualification_review_packet_v1(*, wrapper: Mapping[str, Any]) -> dict[str, Any]:
    source = _position_packet(wrapper)
    return {
        "schema_version": PACKET_SCHEMA,
        "case_id": source["case_id"],
        "shard_id": source["shard_id"],
        "focal_region": source["focal_region"],
        "prior_context": source["prior_context"],
        "question": (
            "After reviewing the complete source, does a distinct unresolved matter remain capable "
            "of limiting, changing, or reopening the user's current working answer?"
        ),
        "current_boundary": ROLE_BOUNDARY_CONTRACTS["current"],
        "qualification_boundary": ROLE_BOUNDARY_CONTRACTS["qualification"],
        "outcome_contract": {
            "unresolved_qualification_present": (
                "At least one source-supported unresolved matter, counterpressure, blind spot, side "
                "effect, or path dependency remains distinct from the current answer."
            ),
            "no_unresolved_qualification_observed": (
                "After checking the whole source, no distinct unresolved qualification is visible. "
                "Cite the strongest source evidence supporting closure, stand-down, or conversion "
                "of concerns into current conditions."
            ),
            "ambiguous_qualification_review": (
                "The visible source does not support a responsible present-or-absent conclusion. "
                "Cite the evidence creating the ambiguity."
            ),
        },
        "evidence_contract": (
            "Use exact visible evidence aliases. The cited evidence must justify the declared review "
            "outcome; omission alone never means absence."
        ),
        "boundary": {
            "one_semantic_decision_only": True,
            "current_record_extraction_requested": False,
            "qualification_record_extraction_requested": False,
            "relationship_extraction_requested": False,
            "model_authored_outcome_required": True,
            "source_linked_absence_required": True,
            "deterministic_semantic_inference": False,
            "keyword_or_chronology_gate_added": False,
            "direct_graph_routing_allowed": False,
        },
    }


def qualification_review_response_schema_v1() -> dict[str, Any]:
    return {
        "type": "object",
        "description": "One source-linked judgment about unresolved qualification presence.",
        "properties": {
            "outcome": {"type": "string", "enum": list(OUTCOMES)},
            "evidence_ids": {
                "type": "array",
                "minItems": 1,
                "maxItems": 6,
                "items": {"type": "string", "pattern": "^e[0-9]{3}$"},
            },
            "interpretation": {"type": "string", "minLength": 1, "maxLength": 500},
            "limitations": {"type": "string", "maxLength": 500},
        },
        "required": ["outcome", "evidence_ids", "interpretation", "limitations"],
        "additionalProperties": False,
    }


def build_qualification_review_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid qualification review packet")
    system_prompt = (
        "Judge one thing only: whether a distinct unresolved qualification remains after the complete "
        "conversation. Compare current and qualification meanings, preserve speaker ownership, and "
        "cite exact source aliases. An adopted safeguard or condition is current, not automatically "
        "unresolved. Omission is never evidence of absence. Return schema-valid JSON."
    )
    user_prompt = (
        "QUALIFICATION REVIEW PACKET\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nReturn exactly one model-authored outcome with the source evidence that justifies it."
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def compile_qualification_review_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
) -> dict[str, Any]:
    if packet.get("schema_version") != PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid qualification review packet")
    if set(response) != {"outcome", "evidence_ids", "interpretation", "limitations"}:
        raise ViewSpecificInterfaceError("qualification review fields do not match")
    if response.get("outcome") not in OUTCOMES:
        raise ViewSpecificInterfaceError("qualification review outcome is invalid")
    evidence_ids = response.get("evidence_ids")
    aliases = _alias_map(packet)
    if (
        not isinstance(evidence_ids, list)
        or not 1 <= len(evidence_ids) <= 6
        or len(evidence_ids) != len(set(evidence_ids))
        or bool(set(evidence_ids) - set(aliases))
    ):
        raise ViewSpecificInterfaceError("qualification review evidence custody is invalid")
    interpretation = response.get("interpretation")
    limitations = response.get("limitations")
    if not isinstance(interpretation, str) or not 1 <= len(interpretation) <= 500:
        raise ViewSpecificInterfaceError("qualification review interpretation is invalid")
    if not isinstance(limitations, str) or len(limitations) > 500:
        raise ViewSpecificInterfaceError("qualification review limitations are invalid")
    return {
        "schema_version": RESPONSE_SCHEMA,
        "status": "qualification_review_custody_complete",
        "outcome": response["outcome"],
        "evidence_ids": list(evidence_ids),
        "interpretation": interpretation,
        "limitations": limitations,
        "source_evidence": [
            {"alias": alias, "text": aliases[alias]} for alias in evidence_ids
        ],
        "producer_kind": producer_kind,
        "producer_id": producer_id,
        "boundary": {
            "semantic_outcome_provider_authored": True,
            "source_linked_absence_required": True,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def join_decomposed_current_qualification_v1(
    *,
    current_compiled: Mapping[str, Any],
    qualification_compiled: Mapping[str, Any],
    qualification_review: Mapping[str, Any],
) -> dict[str, Any]:
    if current_compiled.get("role") != "current":
        raise ViewSpecificInterfaceError("decomposed join current role is invalid")
    if qualification_compiled.get("role") != "qualification":
        raise ViewSpecificInterfaceError("decomposed join qualification role is invalid")
    if qualification_review.get("schema_version") != RESPONSE_SCHEMA:
        raise ViewSpecificInterfaceError("decomposed join qualification review is invalid")
    current = list(current_compiled.get("observations", []))
    qualification = list(qualification_compiled.get("observations", []))
    if not 1 <= len(current) <= 2 or len(qualification) > 2:
        raise ViewSpecificInterfaceError("decomposed join role portfolio bounds are invalid")
    outcome = qualification_review["outcome"]
    if outcome == "unresolved_qualification_present" and not qualification:
        raise ViewSpecificInterfaceError("present review lacks qualification record")
    if outcome == "no_unresolved_qualification_observed" and qualification:
        raise ViewSpecificInterfaceError("negative review conflicts with qualification record")
    custody = [
        *list(current_compiled.get("records", [])),
        *list(qualification_compiled.get("records", [])),
    ]
    observations = [*current, *qualification]
    return {
        "schema_version": JOIN_SCHEMA,
        "status": "decomposed_current_qualification_custody_complete",
        "role_compiled": {
            "current": dict(current_compiled),
            "qualification": dict(qualification_compiled),
        },
        "qualification_review": dict(qualification_review),
        "records": custody,
        "observations": observations,
        "paired_terminal_disposition": "compiled" if observations else "reviewed_empty",
        "boundary": {
            "separate_probabilistic_role_calls": True,
            "separate_probabilistic_qualification_review": True,
            "exact_role_labels_joined_mechanically": True,
            "explicit_review_consistency_validated": True,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
            "keyword_or_chronology_gate_added": False,
            "direct_graph_routing_allowed": False,
        },
    }
