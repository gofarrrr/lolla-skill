"""Provider-free contracts for the simulated reliability V1 experiment.

This module deliberately contains no provider transport.  It turns controlled
mechanism identities into a custody-preserving direct portfolio, creates a
bounded one-hop graph reserve, and packages the three experimental arms.  It
does not decide whether a mechanism or mental model applies to a conversation.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any

from engine.system_b.fresh_reasoning_pressure import (
    build_control_packet_v2,
    build_control_prompts_v2,
    control_response_schema,
)
from engine.system_b.reasoning_process_position_role_first_v24 import (
    build_position_starting_packet_v24,
    build_position_starting_prompts_v24,
    position_starting_response_schema_v24,
)
from engine.system_b.reasoning_process_position_role_first_v242 import (
    build_packet_v242,
    build_prompts_v242,
    response_schema_v242,
)
from engine.system_b.reasoning_pattern_role_record_interpreter import normalize_role_observation
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS, ontology_packet
from engine.system_b.reasoning_pattern_role_record_interpreter_v2 import ALL_STATES, ROUTING_STATES
from engine.system_b.reasoning_pattern_shadow import (
    PACKET_SCHEMA as REASONING_PATTERN_PACKET_SCHEMA,
    PROJECTION_SCHEMA,
    lint_routing_projection,
)


DIRECT_ACTIVE_CAP = 10
GRAPH_ACTIVE_CAP = 3
GRAPH_ARM_ACTIVE_CAP = DIRECT_ACTIVE_CAP + GRAPH_ACTIVE_CAP
GRAPH_SLOT_ORDER = ("antagonist", "tension", "ally")

DIRECT_LEDGER_SCHEMA = "lolla.simulated_reliability_direct_ledger.v1"
GRAPH_LEDGER_SCHEMA = "lolla.simulated_reliability_graph_ledger.v1"
PRESSURE_PACKET_SCHEMA = "lolla.simulated_reliability_pressure_input.v1"
ARM_BUNDLE_SCHEMA = "lolla.simulated_reliability_three_arm_bundle.v1"
MECHANISM_INPUT_SCHEMA = "lolla.simulated_reliability_joint_mechanism_input.v1"
USER_PROCESS_STATUSES = ("unresolved", "resolved", "ambiguous", "not_observed")
VANILLA_ANSWER_COVERAGES = (
    "operationalized",
    "acknowledged_only",
    "not_covered",
    "not_applicable",
    "ambiguous",
)
ROUTING_DISPOSITIONS = ("route_uncovered_pressure", "preserve_no_route")


class SimulatedReliabilityError(ValueError):
    """Raised when a V1 custody or experiment boundary is violated."""


def _source_messages(conversation: str) -> list[tuple[int, str, str]]:
    pattern = re.compile(
        r"(?ms)^\[Turn (\d+)\] (USER|ASSISTANT):\n(.*?)(?=^\[Turn \d+\] (?:USER|ASSISTANT):\n|\Z)"
    )
    messages = [
        (int(match.group(1)), match.group(2).lower(), match.group(3).strip())
        for match in pattern.finditer(conversation)
    ]
    if not messages or any(not text for _turn, _speaker, text in messages):
        raise SimulatedReliabilityError("authoritative conversation message parsing failed")
    return messages


def _evidence_units(text: str) -> list[str]:
    """Create stable source spans without assigning semantic importance."""

    units = [
        value.strip()
        for value in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'“‘])", text)
        if value.strip()
    ]
    return units or [text]


def build_position_wrapper(
    *, case_id: str, conversation: str, source_path: str, source_sha256: str
) -> dict[str, Any]:
    """Alias every source sentence for the two-call V2.4.2 role contract.

    This mechanical projection performs no semantic windowing or selection.
    Every parsed conversation message remains represented.
    """

    messages = _source_messages(conversation)
    alias_rows: list[dict[str, Any]] = []
    annotated: list[str] = []
    alias_number = 1
    for turn, speaker, text in messages:
        annotated.append(f"[Turn {turn} {speaker.upper()}]")
        for unit in _evidence_units(text):
            alias = f"e{alias_number:03d}"
            alias_number += 1
            span_sha = hashlib.sha256(unit.encode("utf-8")).hexdigest()
            annotated.append(f"{alias}\t{unit}")
            alias_rows.append(
                {
                    "alias": alias,
                    "span_id": "span-" + hashlib.sha256(
                        f"{turn}|{speaker}|{unit}".encode("utf-8")
                    ).hexdigest()[:16],
                    "speaker": speaker,
                    "text_sha256": span_sha,
                    "turn_index": turn,
                }
            )
    annotated_text = "\n".join(annotated)
    packet = {
        "schema_version": "lolla.reasoning_process_chronological_shard_packet.v1",
        "status": "target_blind_provider_free_full_conversation_projection",
        "case_id": case_id,
        "shard_id": case_id + "-position_and_decision_trajectory-full-source",
        "shard_kind": "position_endpoint_comparison",
        "view_kind": "position_and_decision_trajectory",
        "question": "How did the working position or decision change, and does any unresolved qualification remain capable of changing it?",
        "focal_region": {
            "annotated_sentence_text": annotated_text,
            "citation_allowed": True,
            "evidence_aliases": [row["alias"] for row in alias_rows],
        },
        "focal_turn_indices": sorted({turn for turn, _speaker, _text in messages}),
        "prior_context": {
            "annotated_sentence_text": "",
            "evidence_aliases": [],
            "general_citation_allowed": False,
            "included": False,
            "role_limited_citation_policy": "none",
        },
        "response_contract": {
            "auxiliary_observation_ids_allowed": False,
            "free_form_source_quotes_allowed": False,
            "global_synthesis_requested": False,
            "maximum_records": 4,
            "relationship_roles_unchanged_from_v3": True,
            "valid_empty_output_allowed": True,
        },
        "source": {
            "conversation_message_count": len(messages),
            "source_path": source_path,
            "source_sha256": "sha256:" + source_sha256,
        },
        "boundary": {
            "auxiliary_ledger_included": False,
            "deterministic_semantic_gate_performed": False,
            "direct_graph_routing_allowed": False,
            "global_synthesis_requested": False,
            "protected_target_included": False,
            "semantic_prefilter_performed": False,
            "source_review_fixture_included": False,
            "all_conversation_messages_projected": True,
        },
    }
    wrapper = {
        "packet": packet,
        "focal_alias_map": alias_rows,
        "context_alias_map": [],
        "metrics": {
            "context_sentence_count": 0,
            "focal_sentence_count": len(alias_rows),
            "future_max_records": 4,
            "input_utf8_bytes": len(annotated_text.encode("utf-8")),
            "conversation_message_count": len(messages),
        },
    }
    wrapper["wrapper_sha256"] = _sha(wrapper)
    return wrapper


def build_role_request_bundle(*, wrapper: Mapping[str, Any]) -> dict[str, Any]:
    """Build the two provider requests without executing transport."""

    starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
    paired_packet = build_packet_v242(wrapper=wrapper)
    starting_prompts = build_position_starting_prompts_v24(starting_packet)
    paired_prompts = build_prompts_v242(paired_packet)
    bundle: dict[str, Any] = {
        "schema_version": "lolla.simulated_reliability_role_request_bundle.v1",
        "source_wrapper_sha256": wrapper["wrapper_sha256"],
        "requests": {
            "starting": {
                "packet": starting_packet,
                "prompts": starting_prompts,
                "response_schema": position_starting_response_schema_v24("starting"),
            },
            "current_qualification": {
                "packet": paired_packet,
                "prompts": paired_prompts,
                "response_schema": response_schema_v242(),
            },
        },
        "boundary": {
            "maximum_provider_calls": 2,
            "provider_calls": 0,
            "semantic_prefilter": False,
            "deterministic_role_inference": False,
            "relation_call_omitted": True,
            "relation_call_omission_reason": "V1 downstream mechanism interpretation consumes starting, current, qualification, and explicit qualification review; a separate relation classification is not required.",
        },
    }
    return _with_hash(bundle, "bundle_sha256")


def join_role_records_v1(
    *, starting_compiled: Mapping[str, Any], paired_compiled: Mapping[str, Any]
) -> dict[str, Any]:
    """Preserve a bounded portfolio of coherent records for each role."""

    starts = list(starting_compiled.get("observations", []))
    currents = list(paired_compiled.get("role_compiled", {}).get("current", {}).get("observations", []))
    qualifications = list(
        paired_compiled.get("role_compiled", {}).get("qualification", {}).get("observations", [])
    )
    review = paired_compiled.get("qualification_review")
    if not 1 <= len(starts) <= 2 or not 1 <= len(currents) <= 2 or len(qualifications) > 2:
        raise SimulatedReliabilityError("V1 role portfolio bounds are invalid")
    if not isinstance(review, Mapping):
        raise SimulatedReliabilityError("V1 role portfolio lacks qualification review")
    if review.get("outcome") == "unresolved_qualification_present" and not qualifications:
        raise SimulatedReliabilityError("V1 unresolved qualification review lacks records")
    if review.get("outcome") == "no_unresolved_qualification_observed" and qualifications:
        raise SimulatedReliabilityError("V1 negative qualification review conflicts with records")
    return {
        "schema_version": "lolla.simulated_reliability_role_portfolio_join.v1",
        "status": "bounded_role_portfolio_join_complete",
        "role_observations": {
            "starting": starts,
            "current": currents,
            "qualification": qualifications,
        },
        "qualification_review": dict(review),
        "record_counts": {
            "starting": len(starts),
            "current": len(currents),
            "qualification": len(qualifications),
        },
        "boundary": {
            "semantic_record_merge_performed": False,
            "record_selection_performed": False,
            "deterministic_semantic_inference": False,
            "direct_graph_routing_allowed": False,
        },
    }


def validate_mechanism_input_v1(packet: Mapping[str, Any]) -> None:
    if packet.get("schema_version") != MECHANISM_INPUT_SCHEMA:
        raise SimulatedReliabilityError("V1 mechanism input schema is invalid")
    supplied_hash = packet.get("packet_sha256")
    if supplied_hash != _sha({key: value for key, value in packet.items() if key != "packet_sha256"}):
        raise SimulatedReliabilityError("V1 mechanism input hash drifted")
    records = packet.get("role_records")
    if not isinstance(records, list) or not 2 <= len(records) <= 6:
        raise SimulatedReliabilityError("V1 mechanism role portfolio count is invalid")
    roles = [item.get("role") for item in records]
    if roles != sorted(roles, key=lambda role: {"starting": 0, "current": 1, "qualification": 2}.get(role, 99)):
        raise SimulatedReliabilityError("V1 mechanism role portfolio order is invalid")
    if not 1 <= roles.count("starting") <= 2 or not 1 <= roles.count("current") <= 2 or roles.count("qualification") > 2:
        raise SimulatedReliabilityError("V1 mechanism role portfolio bounds are invalid")
    review = packet.get("qualification_review", {})
    if review.get("outcome") == "unresolved_qualification_present" and not roles.count("qualification"):
        raise SimulatedReliabilityError("V1 mechanism unresolved review lacks qualification")
    if review.get("outcome") == "no_unresolved_qualification_observed" and roles.count("qualification"):
        raise SimulatedReliabilityError("V1 mechanism negative review conflicts with qualification")
    assistants = packet.get("assistant_contributions")
    if not isinstance(assistants, list) or not assistants:
        raise SimulatedReliabilityError("V1 mechanism input lacks assistant contributions")
    if len({item.get("contribution_id") for item in assistants}) != len(assistants):
        raise SimulatedReliabilityError("V1 assistant contribution identities are duplicated")


def build_mechanism_input_v1(
    *,
    case_id: str,
    arm_id: str,
    joined: Mapping[str, Any],
    conversation: str,
    source_refs: list[dict[str, str]],
) -> dict[str, Any]:
    """Add complete assistant-side custody to the quiet-capable role packet.

    User starting/current/qualification meanings remain probabilistically
    compressed by the role tasks.  Every assistant message is included without
    semantic selection so the mechanism interpreter can judge whether the
    conversation already operationalized a concern before activating pressure.
    """

    roles = joined.get("role_observations", {})
    normalized_records: list[dict[str, Any]] = []
    for role in ("starting", "current", "qualification"):
        value = roles.get(role, [])
        records = [value] if isinstance(value, Mapping) else list(value or [])
        for record in records:
            if not isinstance(record, Mapping):
                raise SimulatedReliabilityError("V1 joined role observation is invalid")
            normalized_records.append(normalize_role_observation(record))
    review = joined.get("qualification_review")
    if not isinstance(review, Mapping):
        raise SimulatedReliabilityError("V1 mechanism input lacks qualification review")
    assistant_rows = [
        {
            "contribution_id": f"assistant-turn-{turn:03d}",
            "turn_number": turn,
            "speaker": "assistant",
            "text": text,
        }
        for turn, speaker, text in _source_messages(conversation)
        if speaker == "assistant"
    ]
    if not assistant_rows:
        raise SimulatedReliabilityError("mechanism input lacks assistant contributions")
    packet = {
        "schema_version": MECHANISM_INPUT_SCHEMA,
        "case_id": case_id,
        "arm_id": arm_id,
        "source_refs": source_refs,
        "role_records": normalized_records,
        "qualification_review": {
            "outcome": str(review.get("outcome", "")),
            "evidence_ids": [str(value) for value in review.get("evidence_ids", [])],
            "interpretation": str(review.get("interpretation", "")),
            "limitations": str(review.get("limitations", "")),
        },
        "assistant_contributions": assistant_rows,
        "controlled_mechanisms": sorted(MECHANISMS),
        "ablation": {"active": False, "kind": "none", "note": ""},
        "boundary": {
            "raw_user_conversation_included": False,
            "user_role_semantic_prose_included": True,
            "assistant_source_evidence_text_included": True,
            "all_assistant_messages_included": True,
            "assistant_semantic_prefilter": False,
            "assistant_mentions_are_not_deterministic_resolution": True,
            "fact_free_routing_projection_required": True,
            "multiple_coherent_records_per_role_preserved": True,
            "deterministic_semantic_merge": False,
            "graph_model_names_included": False,
            "expected_patterns_included": False,
            "graph_runtime_effect": "none",
        },
    }
    packet["packet_sha256"] = _sha(packet)
    validate_mechanism_input_v1(packet)
    return packet


def build_mechanism_prompts_v1(packet: Mapping[str, Any]) -> dict[str, str]:
    validate_mechanism_input_v1(packet)
    if not packet.get("assistant_contributions"):
        raise SimulatedReliabilityError("V1 mechanism prompt lacks assistant-side custody")
    system = (
        "You assess the final joint reasoning trajectory without collapsing the user's reasoning "
        "state into the vanilla assistant answer's coverage. "
        "Review every controlled mechanism exactly once using its operational definition, "
        "requirements, exclusions, and near-neighbor distinction. The assistant contributions "
        "are part of the joint reasoning trajectory. "
        "First judge whether the mechanism remains in the user's reasoning process. Separately "
        "judge whether the vanilla assistant answer already turns that concern into a concrete "
        "test, boundary, alternative, or reopening condition. The user may remain unresolved "
        "while the vanilla answer operationalizes the pressure. Acknowledgment without an "
        "actionable treatment is not operationalization. Route only pressure that remains "
        "unresolved in the user process and uncovered by the vanilla answer."
    )
    user = (
        "ONTOLOGY\n"
        + _canonical(ontology_packet())
        + "\n\nJOINT TRAJECTORY PACKET\n"
        + _canonical(packet)
        + "\n\nReturn exactly nine assessments, one for every mechanism_id and no duplicates. "
        "Use user role records to assign user_process_status. Use assistant_contributions to "
        "assign vanilla_answer_coverage. operationalized means the assistant turned the concern "
        "into an actionable test, boundary, alternative, or reopening condition; acknowledged_only "
        "means it merely mentioned the concern; not_covered means it did neither. Do not require "
        "the user to repeat an assistant repair before recognizing answer coverage, and do not "
        "mistake answer coverage for user adoption. route_uncovered_pressure is allowed only when "
        "user_process_status is unresolved and vanilla_answer_coverage is acknowledged_only or "
        "not_covered. An unresolved user process requires present or missing_protection whether "
        "or not it routes; routing_disposition alone controls routing. An ambiguous user process "
        "uses tension, while resolved and not_observed use not_applicable. not_observed also "
        "requires not_applicable coverage and both "
        "source arrays empty. Cite exact role_record_ids in "
        "source_role_record_ids and exact contribution_ids in source_assistant_contribution_ids. "
        "Do not output rationale, case prose, mental-model names, or invented IDs. The downstream "
        "routing projection remains fact-free and controlled-ID-only."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
    }


def mechanism_response_schema_v1() -> dict[str, Any]:
    row = {
        "type": "object",
        "properties": {
            "mechanism_id": {
                "type": "string",
                "enum": sorted(MECHANISMS),
                "description": "One exact controlled reasoning-mechanism identity.",
            },
            "user_process_status": {
                "type": "string",
                "enum": list(USER_PROCESS_STATUSES),
                "description": "Whether the mechanism remains in the user's reasoning process, independent of assistant-answer coverage.",
            },
            "vanilla_answer_coverage": {
                "type": "string",
                "enum": list(VANILLA_ANSWER_COVERAGES),
                "description": "Whether the vanilla assistant answer operationalizes, merely acknowledges, or does not cover the pressure.",
            },
            "routing_disposition": {
                "type": "string",
                "enum": list(ROUTING_DISPOSITIONS),
                "description": "Route only unresolved user-process pressure not operationalized by the vanilla answer.",
            },
            "pattern_state": {
                "type": "string",
                "enum": list(ALL_STATES),
                "description": "Controlled routing state consistent with the joint status.",
            },
            "source_role_record_ids": {
                "type": "array",
                "minItems": 0,
                "maxItems": 3,
                "description": "Exact supplied user role-record identities supporting the status.",
                "items": {"type": "string", "minLength": 1, "maxLength": 160},
            },
            "source_assistant_contribution_ids": {
                "type": "array",
                "minItems": 0,
                "maxItems": 4,
                "description": "Exact supplied assistant-contribution identities supporting acknowledgement, repair, or an assistant-side weakness.",
                "items": {"type": "string", "pattern": "^assistant-turn-[0-9]{3}$"},
            },
        },
        "required": [
            "mechanism_id",
            "user_process_status",
            "vanilla_answer_coverage",
            "routing_disposition",
            "pattern_state",
            "source_role_record_ids",
            "source_assistant_contribution_ids",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "assessments": {
                "type": "array",
                "minItems": len(MECHANISMS),
                "maxItems": len(MECHANISMS),
                "description": "Exactly one assessment for every controlled mechanism.",
                "items": row,
            }
        },
        "required": ["assessments"],
        "additionalProperties": False,
    }


def compile_mechanism_response_v1(
    *,
    response: Mapping[str, Any],
    packet: Mapping[str, Any],
    producer_kind: str,
    producer_id: str,
) -> dict[str, Any]:
    validate_mechanism_input_v1(packet)
    rows = response.get("assessments")
    if set(response) != {"assessments"} or not isinstance(rows, list) or len(rows) != len(MECHANISMS):
        raise SimulatedReliabilityError("V1 mechanism response must contain exactly nine assessments")
    valid_role_ids = {item["role_record_id"] for item in packet["role_records"]}
    valid_assistant_ids = {item["contribution_id"] for item in packet["assistant_contributions"]}
    fields = {
        "mechanism_id",
        "user_process_status",
        "vanilla_answer_coverage",
        "routing_disposition",
        "pattern_state",
        "source_role_record_ids",
        "source_assistant_contribution_ids",
    }
    seen: set[str] = set()
    hypotheses: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != fields:
            raise SimulatedReliabilityError("V1 mechanism assessment fields are invalid")
        mechanism = row["mechanism_id"]
        user_status = row["user_process_status"]
        answer_coverage = row["vanilla_answer_coverage"]
        disposition = row["routing_disposition"]
        state = row["pattern_state"]
        role_ids = row["source_role_record_ids"]
        assistant_ids = row["source_assistant_contribution_ids"]
        if (
            mechanism not in MECHANISMS
            or mechanism in seen
            or user_status not in USER_PROCESS_STATUSES
            or answer_coverage not in VANILLA_ANSWER_COVERAGES
            or disposition not in ROUTING_DISPOSITIONS
            or state not in ALL_STATES
        ):
            raise SimulatedReliabilityError("V1 mechanism assessment identity is invalid")
        if (
            not isinstance(role_ids, list)
            or not isinstance(assistant_ids, list)
            or len(role_ids) != len(set(role_ids))
            or len(assistant_ids) != len(set(assistant_ids))
            or set(role_ids) - valid_role_ids
            or set(assistant_ids) - valid_assistant_ids
        ):
            raise SimulatedReliabilityError("V1 mechanism source custody is invalid")
        all_ids = [*role_ids, *assistant_ids]
        eligible = disposition == "route_uncovered_pressure"
        if eligible and (
            user_status != "unresolved"
            or answer_coverage not in {"acknowledged_only", "not_covered"}
            or state not in ROUTING_STATES
            or not role_ids
            or (answer_coverage == "acknowledged_only" and not assistant_ids)
        ):
            raise SimulatedReliabilityError("V1 uncovered-pressure routing contract is invalid")
        if user_status == "unresolved" and (state not in ROUTING_STATES or not role_ids):
            raise SimulatedReliabilityError("V1 unresolved user-process contract is invalid")
        if user_status == "ambiguous" and (state != "tension" or not all_ids):
            raise SimulatedReliabilityError("V1 ambiguous mechanism contract is invalid")
        if user_status in {"resolved", "not_observed"} and state != "not_applicable":
            raise SimulatedReliabilityError("V1 preserved mechanism state is invalid")
        if user_status == "not_observed" and (
            answer_coverage != "not_applicable" or all_ids or eligible
        ):
            raise SimulatedReliabilityError("V1 not-observed mechanism contract is invalid")
        if user_status != "not_observed" and not role_ids:
            raise SimulatedReliabilityError("V1 observed mechanism lacks user-process evidence")
        if answer_coverage in {"operationalized", "acknowledged_only"} and not assistant_ids:
            raise SimulatedReliabilityError("V1 covered mechanism lacks assistant evidence")
        if answer_coverage in {"not_covered", "not_applicable"} and assistant_ids:
            raise SimulatedReliabilityError("V1 uncovered mechanism cites assistant coverage")
        if user_status == "unresolved" and answer_coverage in {"acknowledged_only", "not_covered"} and not eligible:
            raise SimulatedReliabilityError("V1 uncovered unresolved pressure must route")
        seen.add(mechanism)
        pattern_id = f"rp_{len(hypotheses) + 1:03d}"
        hypotheses.append(
            {
                "pattern_id": pattern_id,
                "mechanism_id": mechanism,
                "subject_scope": "joint_process",
                "state": state,
                "user_process_status": user_status,
                "vanilla_answer_coverage": answer_coverage,
                "routing_disposition": disposition,
                "support_status": "uncovered_pressure" if eligible else "preserved_for_audit",
                "routing_eligible": eligible,
            }
        )
        sources.append(
            {
                "pattern_id": pattern_id,
                "source_semantic_item_ids": sorted(all_ids),
                "source_role_record_ids": sorted(role_ids),
                "source_assistant_contribution_ids": sorted(assistant_ids),
            }
        )
        if eligible:
            nodes.append(
                {
                    "pattern_id": pattern_id,
                    "mechanism_id": mechanism,
                    "subject_scope": "joint_process",
                    "state": state,
                }
            )
    if seen != set(MECHANISMS):
        raise SimulatedReliabilityError("V1 mechanism coverage is incomplete")
    projection = {
        "schema_version": PROJECTION_SCHEMA,
        "pattern_nodes": nodes,
        "pattern_edges": [],
        "contains_case_context": False,
    }
    violations = lint_routing_projection(projection)
    if violations:
        raise SimulatedReliabilityError("V1 mechanism projection failed fact-leak lint")
    return {
        "schema_version": REASONING_PATTERN_PACKET_SCHEMA,
        "packet_metadata": {
            "packet_id": f"reasoning_pattern_packet:{packet['arm_id']}:v1_joint",
            "interpretation_schema_version": "lolla.simulated_reliability_separated_mechanism_response.v2",
            "graph_runtime_modified": False,
        },
        "provenance": {
            "source_role_record_packet_sha256": packet["packet_sha256"],
            "pattern_sources": sources,
            "producer_kind": producer_kind,
            "producer_id": producer_id,
            "raw_role_or_assistant_prose_in_routing_projection": False,
            "qualification_review_outcome": packet["qualification_review"]["outcome"],
            "assistant_contribution_count": len(packet["assistant_contributions"]),
        },
        "pattern_hypotheses": hypotheses,
        "routing_projection": projection,
        "fact_boundary": {
            "raw_text_included": False,
            "quotes_included": False,
            "entities_included": False,
            "case_quantities_included": False,
            "dates_included": False,
            "desired_outcome_included": False,
            "topic_labels_included": False,
        },
        "lint": {"status": "passed", "violations": []},
        "non_claims": [
            "probabilistic_semantic_assessment",
            "assistant_citation_is_not_deterministic_resolution",
            "answer_coverage_is_not_user_adoption",
            "routing_disposition_is_not_mental_model_applicability_proof",
            "not_reasoning_quality_proof",
            "not_runtime_integration_authority",
        ],
    }


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _with_hash(payload: dict[str, Any], field: str) -> dict[str, Any]:
    payload[field] = _sha(payload)
    return payload


def _turn_numbers(conversation: str) -> list[int]:
    turns = {
        int(value)
        for value in re.findall(
            r"(?m)^\[Turn (\d+)\] (?:USER|ASSISTANT):", conversation
        )
    }
    if not turns:
        raise SimulatedReliabilityError("authoritative conversation has no turns")
    return sorted(turns)


def _final_assistant_message(conversation: str) -> str:
    assistants = [text for _turn, speaker, text in _source_messages(conversation) if speaker == "assistant"]
    if not assistants:
        raise SimulatedReliabilityError("authoritative conversation has no assistant response")
    return assistants[-1]


def build_direct_ledger(
    *,
    unresolved_mechanism_ids: Sequence[str],
    mechanism_seed_models: Mapping[str, Sequence[str]],
    canonical_model_ids: set[str],
    active_cap: int = DIRECT_ACTIVE_CAP,
) -> dict[str, Any]:
    """Build a deterministic direct portfolio without semantic filtering.

    A mechanism-round-robin protects structural mechanism breadth under the
    cap.  The ordering is based only on controlled IDs.  Every overflow model
    remains in the reserve with its complete mechanism provenance.
    """

    mechanisms = [str(value).strip() for value in unresolved_mechanism_ids]
    if any(not value for value in mechanisms) or len(mechanisms) != len(set(mechanisms)):
        raise SimulatedReliabilityError("unresolved mechanism identities are invalid")
    if set(mechanisms) - set(mechanism_seed_models):
        raise SimulatedReliabilityError("unknown controlled mechanism identity")
    if active_cap < 0:
        raise SimulatedReliabilityError("direct active cap is invalid")

    provenance: dict[str, set[str]] = {}
    queues: dict[str, list[str]] = {}
    for mechanism_id in sorted(mechanisms):
        model_ids = sorted({str(value).strip() for value in mechanism_seed_models[mechanism_id]})
        if not model_ids or any(not value for value in model_ids):
            raise SimulatedReliabilityError("controlled mechanism has no valid seed models")
        if set(model_ids) - canonical_model_ids:
            raise SimulatedReliabilityError("direct routing contains a noncanonical model ID")
        queues[mechanism_id] = model_ids
        for model_id in model_ids:
            provenance.setdefault(model_id, set()).add(mechanism_id)

    active_ids: list[str] = []
    positions = {mechanism_id: 0 for mechanism_id in queues}
    while len(active_ids) < active_cap:
        progressed = False
        for mechanism_id in sorted(queues):
            queue = queues[mechanism_id]
            while positions[mechanism_id] < len(queue):
                model_id = queue[positions[mechanism_id]]
                positions[mechanism_id] += 1
                if model_id in active_ids:
                    continue
                active_ids.append(model_id)
                progressed = True
                break
            if len(active_ids) >= active_cap:
                break
        if not progressed:
            break

    active_set = set(active_ids)
    all_ids = sorted(provenance)
    active = [
        {
            "model_id": model_id,
            "candidate_origin": "direct_seed",
            "recalled_by_mechanism_ids": sorted(provenance[model_id]),
            "admission_rank": rank,
        }
        for rank, model_id in enumerate(active_ids, start=1)
    ]
    reserve = [
        {
            "model_id": model_id,
            "candidate_origin": "direct_seed",
            "recalled_by_mechanism_ids": sorted(provenance[model_id]),
            "custody_status": "direct_active_capacity_overflow",
            "semantic_rejection_performed": False,
            "reactivation_condition": "a future frozen contract raises or batches the direct active cap",
        }
        for model_id in all_ids
        if model_id not in active_set
    ]
    ledger: dict[str, Any] = {
        "schema_version": DIRECT_LEDGER_SCHEMA,
        "unresolved_mechanism_ids": sorted(mechanisms),
        "all_candidate_count": len(all_ids),
        "active_cap": active_cap,
        "active_candidates": active,
        "reserve_candidates": reserve,
        "selection_policy": {
            "operation": "controlled_mechanism_round_robin",
            "mechanism_order": "mechanism_id_ascending",
            "within_mechanism_order": "model_id_ascending",
            "semantic_applicability_decision": False,
            "candidate_deletion": False,
        },
        "stand_down": not all_ids,
        "non_claims": [
            "direct_recall_is_not_applicability_proof",
            "active_cap_is_not_a_relevance_threshold",
        ],
    }
    return _with_hash(ledger, "ledger_sha256")


def _iter_edges(relation_graph: Mapping[str, Any] | Sequence[Mapping[str, Any]]):
    if isinstance(relation_graph, Mapping):
        edges = relation_graph.get("edges", [])
    else:
        edges = relation_graph
    if not isinstance(edges, Sequence) or isinstance(edges, (str, bytes)):
        raise SimulatedReliabilityError("relationship graph edge container is invalid")
    for edge in edges:
        if not isinstance(edge, Mapping):
            raise SimulatedReliabilityError("relationship graph contains a malformed edge")
        yield edge


def build_graph_ledger(
    *,
    direct_ledger: Mapping[str, Any],
    relation_graph: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    canonical_model_ids: set[str],
    slot_order: Sequence[str] = GRAPH_SLOT_ORDER,
) -> dict[str, Any]:
    """Create a complete one-hop ledger and admit structural diversity slots."""

    if direct_ledger.get("schema_version") != DIRECT_LEDGER_SCHEMA:
        raise SimulatedReliabilityError("direct ledger schema is invalid")
    if _sha({key: value for key, value in direct_ledger.items() if key != "ledger_sha256"}) != direct_ledger.get("ledger_sha256"):
        raise SimulatedReliabilityError("direct ledger hash is invalid")

    direct = {
        item["model_id"]: item
        for item in direct_ledger.get("active_candidates", [])
    }
    if len(direct) != len(direct_ledger.get("active_candidates", [])):
        raise SimulatedReliabilityError("direct active identities are duplicated")

    allowed_types = tuple(str(value).strip().lower() for value in slot_order)
    if len(allowed_types) != len(set(allowed_types)) or set(allowed_types) - set(GRAPH_SLOT_ORDER):
        raise SimulatedReliabilityError("graph relation slot identities are invalid")

    eligible_edges: list[dict[str, str]] = []
    for raw in _iter_edges(relation_graph):
        source = str(raw.get("source_model_id", "")).strip()
        if source not in direct:
            continue
        target = str(raw.get("target_model_id", "")).strip()
        edge_type = str(raw.get("edge_type", "")).strip().lower()
        if edge_type not in allowed_types:
            continue
        if source not in canonical_model_ids or target not in canonical_model_ids:
            raise SimulatedReliabilityError("eligible graph edge has noncanonical identity")
        eligible_edges.append(
            {
                "source_model_id": source,
                "target_model_id": target,
                "edge_type": edge_type,
                "source_description": str(raw.get("source_description", "") or "").strip(),
                "affinity_rationale": str(raw.get("affinity_rationale", "") or "").strip(),
                "activation_condition": str(raw.get("activation_condition", "") or "").strip(),
            }
        )
    eligible_edges.sort(
        key=lambda edge: (
            edge["edge_type"], edge["source_model_id"], edge["target_model_id"]
        )
    )

    by_target: dict[str, list[dict[str, str]]] = {}
    for edge in eligible_edges:
        by_target.setdefault(edge["target_model_id"], []).append(edge)

    selected: list[dict[str, Any]] = []
    selected_ids: set[str] = set()
    for relation_type in allowed_types:
        options = sorted(
            (
                edge
                for edge in eligible_edges
                if edge["edge_type"] == relation_type
                and edge["target_model_id"] not in direct
                and edge["target_model_id"] not in selected_ids
            ),
            key=lambda edge: (edge["source_model_id"], edge["target_model_id"]),
        )
        if not options:
            continue
        admission_edge = options[0]
        target = admission_edge["target_model_id"]
        selected_ids.add(target)
        source_ids = sorted({edge["source_model_id"] for edge in by_target[target]})
        mechanism_ids = sorted(
            {
                mechanism_id
                for source_id in source_ids
                for mechanism_id in direct[source_id]["recalled_by_mechanism_ids"]
            }
        )
        selected.append(
            {
                "model_id": target,
                "candidate_origin": "graph_expansion",
                "recalled_by_mechanism_ids": mechanism_ids,
                "selected_relation_slot": relation_type,
                "admission_edge": admission_edge,
                "all_active_source_edge_count": len(by_target[target]),
                "admission_rank": len(selected) + 1,
            }
        )

    reserve: list[dict[str, Any]] = []
    for target in sorted(by_target):
        edges = by_target[target]
        source_ids = sorted({edge["source_model_id"] for edge in edges})
        mechanism_ids = sorted(
            {
                mechanism_id
                for source_id in source_ids
                for mechanism_id in direct[source_id]["recalled_by_mechanism_ids"]
            }
        )
        if target in direct:
            status = "duplicate_of_direct_candidate"
        elif target in selected_ids:
            continue
        else:
            status = "graph_active_capacity_overflow"
        reserve.append(
            {
                "model_id": target,
                "candidate_origin": "graph_expansion",
                "recalled_by_mechanism_ids": mechanism_ids,
                "graph_provenance": edges,
                "custody_status": status,
                "semantic_rejection_performed": False,
                "reactivation_condition": "inspect the private graph ledger or use a future frozen batching contract",
            }
        )

    ledger: dict[str, Any] = {
        "schema_version": GRAPH_LEDGER_SCHEMA,
        "source_direct_ledger_sha256": direct_ledger["ledger_sha256"],
        "eligible_edge_count": len(eligible_edges),
        "unique_target_count": len(by_target),
        "active_cap": len(allowed_types),
        "active_candidates": selected,
        "reserve_candidates": reserve,
        "all_eligible_edges": eligible_edges,
        "selection_policy": {
            "operation": "one_slot_per_declared_relation_type",
            "relation_slot_order": list(allowed_types),
            "within_slot_order": ["source_model_id_ascending", "target_model_id_ascending"],
            "affinity_used_for_admission": False,
            "conversation_text_used_for_admission": False,
            "probabilistic_prefilter_used": False,
            "candidate_deletion": False,
        },
        "non_claims": [
            "graph_recall_is_not_applicability_proof",
            "active_slots_are_not_best_model_selection",
            "reserve_status_is_not_semantic_rejection",
        ],
    }
    return _with_hash(ledger, "ledger_sha256")


def _pressure_candidate(
    item: Mapping[str, Any], challenge_cards: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    model_id = item["model_id"]
    if model_id not in challenge_cards:
        raise SimulatedReliabilityError("pressure candidate is not canonical")
    candidate = {
        "model_id": model_id,
        "candidate_origin": item["candidate_origin"],
        "challenge_card": challenge_cards[model_id],
        "recalled_by_mechanism_ids": list(item["recalled_by_mechanism_ids"]),
        "portfolio_status": "intentionally_noisy_pressure_hypothesis",
    }
    if item["candidate_origin"] == "graph_expansion":
        candidate["selected_relation_slot"] = item["selected_relation_slot"]
        candidate["graph_path"] = item["admission_edge"]
    return candidate


def build_pressure_packet(
    *,
    case_id: str,
    arm_id: str,
    conversation: str,
    candidates: Sequence[Mapping[str, Any]],
    challenge_cards: Mapping[str, Mapping[str, Any]],
    portfolio_ledger_refs: Sequence[Mapping[str, str]],
    source_refs: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    if arm_id not in {"direct_pressure", "graph_expanded_pressure"}:
        raise SimulatedReliabilityError("pressure arm identity is invalid")
    if not candidates:
        raise SimulatedReliabilityError("empty pressure portfolio must stand down")
    if len(candidates) > GRAPH_ARM_ACTIVE_CAP:
        raise SimulatedReliabilityError("pressure portfolio exceeds V1 active cap")
    ids = [str(item.get("model_id", "")).strip() for item in candidates]
    if any(not value for value in ids) or len(ids) != len(set(ids)):
        raise SimulatedReliabilityError("pressure candidate identities are invalid")

    origins = {item.get("candidate_origin") for item in candidates}
    if arm_id == "direct_pressure" and origins != {"direct_seed"}:
        raise SimulatedReliabilityError("direct arm contains a graph candidate")
    if arm_id == "graph_expanded_pressure" and "graph_expansion" not in origins:
        raise SimulatedReliabilityError("graph arm contains no graph candidate")

    packet: dict[str, Any] = {
        "schema_version": PRESSURE_PACKET_SCHEMA,
        "case_id": case_id,
        "arm_id": arm_id,
        "authoritative_conversation": conversation,
        "source_turn_numbers": _turn_numbers(conversation),
        "pressure_portfolio": [
            _pressure_candidate(item, challenge_cards) for item in candidates
        ],
        "portfolio_ledger_refs": list(portfolio_ledger_refs),
        "source_refs": list(source_refs),
        "instructions": {
            "graph_recall_is_applicability_proof": False,
            "every_active_candidate_must_be_inspected": True,
            "allowed_dispositions": ["apply", "reject", "park"],
            "rejection_is_valid": True,
            "preserve_strong_original_reasoning": True,
            "unsupported_case_facts_allowed": False,
            "unsupported_quantitative_thresholds_allowed": False,
            "unknown_thresholds_must_remain_questions_or_selection_tasks": True,
            "mental_model_is_evidence_about_case": False,
            "lens_alone_may_set_risk_level_or_recommendation": False,
            "applied_lenses_remain_conditional": True,
            "applied_lenses_require_reopening_evidence": True,
            "candidate_deletion_before_reconsideration": False,
        },
        "boundary": {
            "fresh_context_required": True,
            "case_facts_reattached_after_graph_recall": True,
            "canonical_ids_only": True,
            "all_active_candidates_preserved": True,
            "reserve_preserved_by_ledger_reference": True,
            "graph_runtime_effect": "none",
            "production_authorization": False,
        },
    }
    return _with_hash(packet, "packet_sha256")


def build_pressure_prompts(packet: Mapping[str, Any]) -> dict[str, str]:
    if packet.get("schema_version") != PRESSURE_PACKET_SCHEMA:
        raise SimulatedReliabilityError("V1 pressure packet required")
    system = (
        "You are a fresh-context reasoner. Reconsider the authoritative "
        "conversation using every canonical pressure candidate as an intentionally "
        "noisy hypothesis. Apply only what changes or usefully tests the reasoning; "
        "explicitly reject or park the rest. Graph recall is not proof. Do not "
        "manufacture facts or quantitative precision. A mental model is a source "
        "of questions, alternatives, and tests; it is not evidence about the case. "
        "A lens alone cannot establish that risk is low or high, predict how a person "
        "will respond, or justify a recommendation."
    )
    user = (
        "SIMULATED RELIABILITY V1 PRESSURE PACKET\n"
        + _canonical(packet)
        + "\n\nInspect every active candidate exactly once. apply means the lens "
        "materially changes, sharpens, or supplies a concrete test for the reasoning. "
        "reject means its strongest plausible application fails in this case; name "
        "the failed condition and the risk of forcing it. park means the lens remains "
        "plausible but needs evidence or is not decision-relevant enough to use now; "
        "name the reopening condition. Cite exact source turn numbers for every "
        "disposition. Preserve strong existing reasoning. Do not invent external "
        "facts, numerical thresholds, percentages, dates, quantities, or cutoffs. "
        "If a value is unknown, state the evidence or decision process needed and "
        "leave it unresolved. Even an applied lens must remain conditional and name "
        "the source evidence, observation, or outcome that would weaken or overturn "
        "its use; 'no reopening condition' is not acceptable. Do not convert a lens "
        "into confidence that the source conversation did not earn. Then write a "
        "self-contained reconsidered answer and a "
        "concise change summary. Candidate names and the mechanical disposition "
        "checklist must remain private unless a name is genuinely useful to the user."
    )
    return {
        "system_prompt": system,
        "user_prompt": user,
        "system_prompt_sha256": hashlib.sha256(system.encode("utf-8")).hexdigest(),
        "user_prompt_sha256": hashlib.sha256(user.encode("utf-8")).hexdigest(),
    }


def pressure_response_schema(candidate_ids: Sequence[str]) -> dict[str, Any]:
    """Return the V1 accountable-disposition schema.

    The schema keeps the model's semantic explanation visible.  Deterministic
    validation checks identity and completeness; a reviewer, not code, judges
    whether an explanation is substantively grounded.
    """

    ids = [str(value).strip() for value in candidate_ids]
    if not ids or any(not value for value in ids) or len(ids) != len(set(ids)):
        raise SimulatedReliabilityError("response schema candidate identities are invalid")
    row = {
        "type": "object",
        "properties": {
            "model_id": {"type": "string", "enum": ids, "description": "The exact canonical candidate identity from the supplied portfolio."},
            "disposition": {"type": "string", "enum": ["apply", "reject", "park"], "description": "Apply a materially useful lens, reject a failed application, or park a plausible lens until a stated condition reopens it."},
            "source_turn_numbers": {
                "type": "array",
                "description": "Exact authoritative conversation turns supporting this disposition.",
                "minItems": 1,
                "maxItems": 7,
                "items": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "effect": {
                "type": "string",
                "description": "The candidate's decision-relevant effect, or no material effect when rejected.",
                "enum": [
                    "reframe",
                    "new_condition",
                    "new_alternative",
                    "uncertainty_change",
                    "reversal_rule",
                    "reinforces_existing",
                    "no_material_effect",
                ],
            },
            "strongest_plausible_application": {"type": "string", "minLength": 1, "maxLength": 700, "description": "The strongest good-faith way this lens could bear on the conversation before deciding its disposition."},
            "disposition_reason": {"type": "string", "minLength": 1, "maxLength": 700, "description": "Why the lens is applied, rejected, or parked, including the failed condition for a rejection."},
            "risk_if_forced": {"type": "string", "minLength": 1, "maxLength": 500, "description": "What would become misleading, duplicative, or harmful if this lens were forced into the reasoning."},
            "reopen_condition": {"type": "string", "minLength": 1, "maxLength": 500, "description": "The evidence, observation, or outcome that would weaken, overturn, or reopen this disposition. Applied lenses must retain a real falsifier and may not say none is needed."},
        },
        "required": [
            "model_id",
            "disposition",
            "source_turn_numbers",
            "effect",
            "strongest_plausible_application",
            "disposition_reason",
            "risk_if_forced",
            "reopen_condition",
        ],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "candidate_dispositions": {
                "type": "array",
                "description": "Exactly one accountable disposition for every active pressure candidate.",
                "minItems": len(ids),
                "maxItems": len(ids),
                "items": row,
            },
            "reconsidered_answer": {"type": "string", "minLength": 1, "maxLength": 8000, "description": "A self-contained public answer that preserves strong original reasoning and includes only earned friction."},
            "change_summary": {"type": "string", "minLength": 1, "maxLength": 1500, "description": "A concise factual account of what changed, stayed unchanged, or remained unresolved after reconsideration."},
        },
        "required": ["candidate_dispositions", "reconsidered_answer", "change_summary"],
        "additionalProperties": False,
    }


def compile_pressure_response(
    *, response: Mapping[str, Any], packet: Mapping[str, Any]
) -> dict[str, Any]:
    """Fail closed on incomplete identities, source turns, or dispositions."""

    if set(response) != {"candidate_dispositions", "reconsidered_answer", "change_summary"}:
        raise SimulatedReliabilityError("pressure response envelope is invalid")
    candidates = {item["model_id"] for item in packet["pressure_portfolio"]}
    turns = set(packet["source_turn_numbers"])
    rows = response["candidate_dispositions"]
    if not isinstance(rows, list) or len(rows) != len(candidates):
        raise SimulatedReliabilityError("pressure response candidate coverage is invalid")
    required = {
        "model_id",
        "disposition",
        "source_turn_numbers",
        "effect",
        "strongest_plausible_application",
        "disposition_reason",
        "risk_if_forced",
        "reopen_condition",
    }
    effects = {
        "reframe",
        "new_condition",
        "new_alternative",
        "uncertainty_change",
        "reversal_rule",
        "reinforces_existing",
        "no_material_effect",
    }
    seen: set[str] = set()
    compiled: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != required:
            raise SimulatedReliabilityError("pressure disposition shape is invalid")
        model_id = row["model_id"]
        disposition = row["disposition"]
        refs = row["source_turn_numbers"]
        if model_id not in candidates or model_id in seen:
            raise SimulatedReliabilityError("pressure disposition identity is invalid")
        if disposition not in {"apply", "reject", "park"} or row["effect"] not in effects:
            raise SimulatedReliabilityError("pressure disposition value is invalid")
        if disposition == "reject" and row["effect"] != "no_material_effect":
            raise SimulatedReliabilityError("rejected candidate claims a material effect")
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)) or set(refs) - turns:
            raise SimulatedReliabilityError("pressure disposition turn custody is invalid")
        for field in (
            "strongest_plausible_application",
            "disposition_reason",
            "risk_if_forced",
            "reopen_condition",
        ):
            if not isinstance(row[field], str) or not row[field].strip():
                raise SimulatedReliabilityError("pressure disposition explanation is empty")
        seen.add(model_id)
        compiled.append(dict(row))
    if seen != candidates:
        raise SimulatedReliabilityError("pressure response candidate coverage is incomplete")
    for field in ("reconsidered_answer", "change_summary"):
        if not isinstance(response[field], str) or not response[field].strip():
            raise SimulatedReliabilityError("pressure public response is empty")
    return {
        "schema_version": "lolla.simulated_reliability_pressure_response.v1",
        "case_id": packet["case_id"],
        "arm_id": packet["arm_id"],
        "source_packet_sha256": packet["packet_sha256"],
        "candidate_dispositions": sorted(compiled, key=lambda item: item["model_id"]),
        "reconsidered_answer": response["reconsidered_answer"],
        "change_summary": response["change_summary"],
        "all_active_candidates_accounted_for": True,
        "non_claims": [
            "dispositions_are_probabilistic",
            "reconsidered_answer_is_not_proven_better",
            "not_runtime_authorization",
        ],
    }


def build_three_arm_bundle(
    *,
    case_id: str,
    conversation: str,
    direct_ledger: Mapping[str, Any],
    graph_ledger: Mapping[str, Any],
    challenge_cards: Mapping[str, Mapping[str, Any]],
    source_refs: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Package matched transcript-only, direct, and graph-expanded arms."""

    if graph_ledger.get("source_direct_ledger_sha256") != direct_ledger.get("ledger_sha256"):
        raise SimulatedReliabilityError("graph ledger does not descend from direct ledger")
    if _sha({key: value for key, value in graph_ledger.items() if key != "ledger_sha256"}) != graph_ledger.get("ledger_sha256"):
        raise SimulatedReliabilityError("graph ledger hash is invalid")

    control_packet = build_control_packet_v2(
        case_id=case_id,
        conversation=conversation,
        source_refs=list(source_refs),
    )
    control_prompts = build_control_prompts_v2(control_packet)
    direct_candidates = list(direct_ledger.get("active_candidates", []))
    graph_candidates = list(graph_ledger.get("active_candidates", []))

    arms: dict[str, Any] = {
        "transcript_only": {
            "call_required": True,
            "packet": control_packet,
            "prompts": control_prompts,
            "response_schema": control_response_schema(),
        }
    }

    if not direct_candidates:
        stand_down = {
            "call_required": False,
            "terminal_status": "deterministic_stand_down",
            "terminal_reason": "no_unresolved_controlled_mechanisms",
            "provider_attempted": False,
            "public_output_source": "authoritative_final_assistant_message",
            "public_output": _final_assistant_message(conversation),
        }
        arms["direct_pressure"] = dict(stand_down)
        arms["graph_expanded_pressure"] = dict(stand_down)
    else:
        direct_packet = build_pressure_packet(
            case_id=case_id,
            arm_id="direct_pressure",
            conversation=conversation,
            candidates=direct_candidates,
            challenge_cards=challenge_cards,
            portfolio_ledger_refs=[
                {"ledger_type": "direct", "sha256": direct_ledger["ledger_sha256"]}
            ],
            source_refs=source_refs,
        )
        arms["direct_pressure"] = {
            "call_required": True,
            "packet": direct_packet,
            "prompts": build_pressure_prompts(direct_packet),
            "response_schema": pressure_response_schema(
                [item["model_id"] for item in direct_candidates]
            ),
        }

        expanded_candidates = direct_candidates + graph_candidates
        if graph_candidates:
            graph_packet = build_pressure_packet(
                case_id=case_id,
                arm_id="graph_expanded_pressure",
                conversation=conversation,
                candidates=expanded_candidates,
                challenge_cards=challenge_cards,
                portfolio_ledger_refs=[
                    {"ledger_type": "direct", "sha256": direct_ledger["ledger_sha256"]},
                    {"ledger_type": "graph", "sha256": graph_ledger["ledger_sha256"]},
                ],
                source_refs=source_refs,
            )
            arms["graph_expanded_pressure"] = {
                "call_required": True,
                "packet": graph_packet,
                "prompts": build_pressure_prompts(graph_packet),
                "response_schema": pressure_response_schema(
                    [item["model_id"] for item in expanded_candidates]
                ),
            }
        else:
            arms["graph_expanded_pressure"] = {
                "call_required": False,
                "terminal_status": "deterministic_graph_stand_down",
                "terminal_reason": "no_eligible_graph_only_candidate_in_declared_slots",
                "provider_attempted": False,
                "direct_arm_reference_packet_sha256": direct_packet["packet_sha256"],
                "public_output_source": "direct_pressure_response_after_it_is_compiled",
            }

    bundle: dict[str, Any] = {
        "schema_version": ARM_BUNDLE_SCHEMA,
        "case_id": case_id,
        "direct_ledger_sha256": direct_ledger["ledger_sha256"],
        "graph_ledger_sha256": graph_ledger["ledger_sha256"],
        "arms": arms,
        "comparison_contract": {
            "same_authoritative_conversation": True,
            "direct_candidates_identical_between_pressure_arms": bool(direct_candidates),
            "graph_only_difference_from_direct_arm": bool(graph_candidates),
            "no_provider_transport_in_builder": True,
            "no_scalar_quality_score": True,
        },
        "runtime_effect": "none",
        "production_authorization": False,
    }
    return _with_hash(bundle, "bundle_sha256")
