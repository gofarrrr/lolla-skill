"""Detail a qualification only after a source-linked model review says it exists."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .reasoning_process_position_role_first_v23 import (
    build_position_role_packet_v23,
    compile_position_role_response_v23,
    position_role_response_schema_v23,
)
from .reasoning_process_qualification_review_v1 import RESPONSE_SCHEMA as REVIEW_SCHEMA
from .reasoning_process_view_specific import ViewSpecificInterfaceError
from .reasoning_process_views import canonical_json_bytes, sha256_bytes


DETAIL_PACKET_SCHEMA = "lolla.reasoning_process_qualification_detail_packet.v1"
BRANCH_SCHEMA = "lolla.reasoning_process_qualification_branch.v1"


def qualification_branch_from_review_v1(review: Mapping[str, Any]) -> dict[str, Any]:
    if review.get("schema_version") != REVIEW_SCHEMA:
        raise ViewSpecificInterfaceError("qualification branch review is invalid")
    outcome = review.get("outcome")
    if outcome == "unresolved_qualification_present":
        branch = "detail_required"
    elif outcome == "no_unresolved_qualification_observed":
        branch = "stand_down"
    elif outcome == "ambiguous_qualification_review":
        branch = "preserve_ambiguous_without_detail"
    else:
        raise ViewSpecificInterfaceError("qualification branch outcome is invalid")
    return {
        "schema_version": BRANCH_SCHEMA,
        "status": "qualification_branch_declared",
        "review_outcome": outcome,
        "branch": branch,
        "review_evidence_ids": list(review.get("evidence_ids", [])),
        "boundary": {
            "branch_source": "provider_authored_semantic_outcome",
            "keyword_or_chronology_gate_added": False,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }


def build_qualification_detail_packet_v1(
    *, wrapper: Mapping[str, Any], review: Mapping[str, Any]
) -> dict[str, Any]:
    branch = qualification_branch_from_review_v1(review)
    if branch["branch"] != "detail_required":
        raise ViewSpecificInterfaceError("qualification detail is not authorized by review")
    source_evidence = review.get("source_evidence")
    if not isinstance(source_evidence, list) or not source_evidence:
        raise ViewSpecificInterfaceError("qualification detail lacks reviewed source evidence")
    expected_ids = list(review["evidence_ids"])
    observed_ids = [row.get("alias") for row in source_evidence if isinstance(row, Mapping)]
    if observed_ids != expected_ids:
        raise ViewSpecificInterfaceError("qualification detail review evidence drifted")
    packet = build_position_role_packet_v23(wrapper=wrapper, role="qualification")
    selected_text = "\n".join(
        f"{row['alias']}\t{row['text']}" for row in source_evidence
    )
    packet["schema_version"] = DETAIL_PACKET_SCHEMA
    packet["focal_region"] = {
        "annotated_sentence_text": selected_text,
        "evidence_aliases": expected_ids,
        "citation_allowed": True,
    }
    packet["prior_context"] = {
        "included": False,
        "annotated_sentence_text": "",
        "evidence_aliases": [],
        "citation_allowed": False,
        "role_limited_citation_policy": "none",
    }
    packet["maximum_records"] = 1
    packet["review_context"] = {
        "outcome": review["outcome"],
        "evidence_ids": expected_ids,
        "interpretation": review["interpretation"],
        "limitations": review["limitations"],
        "instruction": (
            "The review already decided that a qualification is present. Detail that reviewed meaning "
            "only; do not search for additional risks or expand beyond the selected evidence."
        ),
    }
    packet["boundary"].update(
        {
            "provider_review_required_before_detail": True,
            "review_outcome_provider_authored": True,
            "selected_review_evidence_only": True,
            "full_conversation_repeated_in_detail_task": False,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
            "keyword_or_chronology_gate_added": False,
        }
    )
    return packet


def qualification_detail_response_schema_v1() -> dict[str, Any]:
    return position_role_response_schema_v23("qualification")


def build_qualification_detail_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != DETAIL_PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid qualification detail packet")
    system_prompt = (
        "Detail one already-reviewed qualification from only the selected source evidence. Preserve "
        "speaker ownership and modal force. Return exactly one coherent qualification record with "
        "atomic source-linked components. Do not invent another risk or revisit whether a qualification "
        "exists. Return schema-valid JSON."
    )
    user_prompt = (
        "QUALIFICATION DETAIL PACKET\n"
        + canonical_json_bytes(packet).decode("utf-8")
        + "\n\nReturn status supported and exactly one qualification record grounded only in review_context.evidence_ids."
    )
    return {
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": sha256_bytes(system_prompt.encode("utf-8")),
        "user_prompt_sha256": sha256_bytes(user_prompt.encode("utf-8")),
    }


def compile_qualification_detail_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
) -> dict[str, Any]:
    if packet.get("schema_version") != DETAIL_PACKET_SCHEMA:
        raise ViewSpecificInterfaceError("invalid qualification detail packet")
    if response.get("status") != "supported" or len(response.get("records", [])) != 1:
        raise ViewSpecificInterfaceError("qualification detail requires one supported record")
    projected = dict(packet)
    projected["schema_version"] = "lolla.reasoning_process_position_role_packet.v2_3"
    compiled = compile_position_role_response_v23(
        response=response,
        packet=projected,
        producer_kind=producer_kind,
        producer_id=producer_id,
    )
    if len(compiled.get("observations", [])) != 1:
        raise ViewSpecificInterfaceError("qualification detail record was not admitted")
    compiled["schema_version"] = "lolla.reasoning_process_qualification_detail_response.v1"
    compiled["review_context"] = dict(packet["review_context"])
    compiled["boundary"].update(
        {
            "provider_review_required_before_detail": True,
            "review_outcome_provider_authored": True,
            "selected_review_evidence_only": True,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
        }
    )
    return compiled


def materialize_quiet_qualification_role_v1(
    *, wrapper: Mapping[str, Any], review: Mapping[str, Any]
) -> dict[str, Any]:
    branch = qualification_branch_from_review_v1(review)
    if branch["branch"] != "stand_down":
        raise ViewSpecificInterfaceError("quiet qualification role lacks stand-down review")
    packet = build_position_role_packet_v23(wrapper=wrapper, role="qualification")
    compiled = compile_position_role_response_v23(
        response={
            "status": "not_found",
            "records": [],
            "global_limitations": (
                "Empty qualification custody materialized from the separate provider-authored, "
                "source-linked no-unresolved review; absence was not inferred from omission."
            ),
        },
        packet=packet,
        producer_kind="qualification_review_bookkeeping_v1",
        producer_id=str(review.get("producer_id", "")),
    )
    compiled["qualification_review"] = dict(review)
    compiled["boundary"].update(
        {
            "empty_role_from_explicit_provider_review": True,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
        }
    )
    return compiled
