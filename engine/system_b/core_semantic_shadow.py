"""Offline focused-specialist semantic shadow interpretation.

This module combines source-grounded specialist reads with deterministic
evidence custody. It is evaluation-only: it does not modify the live compact
extractor, lane input, graph routing, archives, or Decision Work sidecars.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from typing import Any, Protocol, runtime_checkable

from .conversation_context import ConversationContext
from .dropped_threads_extraction import extract_dropped_threads
from .live_constraints_extraction import extract_live_constraints
from .ir import DerivationProvenance
from .semantic_candidate_ledger import (
    SemanticCandidateLedgerRecorder,
    reconstruct_current_semantic_view,
)
from .stance_extraction import extract_stance_events
from .text_matching import find_substring_tolerant


CORE_SEMANTIC_SHADOW_SCHEMA_VERSION = "lolla.core_semantic_shadow.v0"
USER_COUNTERPRESSURE_SHADOW_SCHEMA_VERSION = (
    "lolla.user_counterpressure_shadow.v0"
)
USER_COUNTERPRESSURE_TEMPORAL_SHADOW_SCHEMA_VERSION = (
    "lolla.user_counterpressure_temporal_shadow.v0"
)


QUESTION_TRAJECTORY_SYSTEM_PROMPT = """You are extracting QUESTION TRAJECTORY SEMANTICS from a decision-support conversation.

Your single job is to preserve how the user's operative questions develop
across the interaction. Do not evaluate whether the advice was good and do not
extract constraints, options, evidence boundaries, or assistant stances.

Return JSON with exactly one array, `question_events`. For every event return:

- stage: initial, intermediate, or current
- question_function: decision_choice, evidence_gate, implementation,
  diagnosis, or other
- quote: exact contiguous substring from a USER turn that states the question
- turn_index: source turn
- changes_prior_question: boolean
- relation_to_prior_question: opens, continues, narrows, reframes, gates,
  supersedes, coexists, returns_to, or unclear
- related_question_turn_index and related_question_quote: exact source
  reference to the earlier question when a relation is declared
- relation_ambiguity: boolean
- alternative_relations: optional array drawn from the same relation vocabulary

Rules:

- Every quote and related quote must be copied character-for-character from the
  claimed user turn.
- Extract only USER-authored questions. An assistant question is not a user
  question event in this contract.
- Never insert `...` or otherwise shorten text inside a quote.
- Return every material user question that changes, narrows, reframes, gates,
  supersedes, coexists with, or returns to the decision trajectory. Do not
  reduce the trajectory to only the first and last question.
- Mark the reader's best current question as current. Preserve more than one
  current question only when they genuinely coexist.
- A changed question is not evidence that the user changed their mind.
- Preserve genuine relation ambiguity; do not manufacture alternatives.
- Return no more than 8 events, in source-turn order.

The values below illustrate shape only. Do not copy them unless the source and
semantic reading independently support them. Return JSON only in this shape:
{
  "question_events": [
    {
      "stage": "initial",
      "question_function": "decision_choice",
      "quote": "exact contiguous substring from one user turn",
      "turn_index": 1,
      "changes_prior_question": false,
      "relation_to_prior_question": "opens",
      "related_question_turn_index": null,
      "related_question_quote": "",
      "relation_ambiguity": false,
      "alternative_relations": []
    }
  ]
}
"""


USER_PRESSURE_SYSTEM_PROMPT = """You are extracting USER PRESSURE SEMANTICS from a decision-support conversation.

Your single job is to preserve how the user corrects, challenges, qualifies,
or places pressure on the reasoning process. Do not extract questions,
options, evidence boundaries, assistant stances, or dropped-thread status.

Return JSON with exactly one array, `user_pressure_events`. For every event
return:

- kind: correction, evidence_request, concern, timing_pressure, or value
- quote: exact contiguous substring from a USER turn
- turn_index: source turn

Rules:

- Every quote must be copied character-for-character from the claimed user
  turn. Never insert `...` or otherwise shorten text inside a quote.
- Emit separate events for separate facts, concerns, requests, pressures, or
  values. Cover every material user correction or counter-pressure up to the
  cap; do not select only one representative from a multi-part correction.
- Use correction for a user-provided fact that weakens or qualifies an earlier
  assumption or recommendation.
- Use evidence_request for a direct request for evidence or a decision
  standard.
- Use concern for a stated downside, failure mode, or misclassification worry.
- Use timing_pressure for an explicit worry that delay, urgency, or a deadline
  changes the decision.
- Use value for an explicit user priority not better represented by another
  pressure kind.
- One exact span may appear in more than one role only when it genuinely
  performs both roles in context. Do not manufacture duplicate labels.
- Do not treat neutral background as pressure merely because it is important.
- Return no more than 8 events, in source-turn order.

The values below illustrate shape only. Do not copy them unless the source and
semantic reading independently support them. Return JSON only in this shape:
{
  "user_pressure_events": [
    {
      "kind": "concern",
      "quote": "exact contiguous substring from one user turn",
      "turn_index": 1
    }
  ]
}
"""


USER_COUNTERPRESSURE_SYSTEM_PROMPT = """You are extracting USER COUNTER-PRESSURE SEMANTICS from a decision-support conversation.

Your single job is to preserve user statements that materially change how the
reasoning should be understood. Extract a statement only when it corrects a
premise or frame, qualifies evidence or feasibility in a decision-relevant
way, or objects to the reasoning being used. This is reasoning about the
reasoning process, not a list of every concern in the underlying decision.

Return JSON with exactly one array, `user_pressure_events`. For every event
return:

- kind: premise_correction, material_qualification, or reasoning_objection
- quote: the smallest exact contiguous substring from one USER turn that
  expresses the event without losing necessary meaning
- turn_index: source turn

Inclusion test:

- If omitting the statement would make a future reader misunderstand why the
  reasoning was revised, became less certain, became conditional, or was
  contested, include it.
- Use premise_correction when the user rejects or repairs a factual premise,
  interpretation, decision frame, or self-supplied assumption.
- Use material_qualification when the user adds a fact or limitation that
  weakens evidence, conditions a recommendation, or changes an option's
  feasibility.
- Use reasoning_objection when the user directly disputes the sufficiency,
  applicability, or direction of the reasoning or advice.

Exclusions:

- Do not return a standalone question or request. Question trajectory readers
  preserve those elsewhere.
- Do not return mere agreement, acknowledgement, gratitude, or an assistant's
  conclusion repeated back by the user.
- Do not return a generic emotion, downside, worry, value, or neutral
  background fact unless it performs one of the three inclusion roles above.
- Do not return every important decision factor. Importance to the decision is
  not enough; the statement must put counter-pressure on the reasoning.

Evidence and overlap rules:

- Every quote must be copied character-for-character from the claimed user
  turn. Never insert `...` or otherwise shorten text inside a quote.
- Split compound turns into the smallest independent counter-pressure spans.
- A statement may also be a constraint or evidence boundary. Include it here
  when it independently passes the inclusion test; cross-family overlap is not
  a reason to omit it.
- Return no more than 8 events. If more than 8 pass, prioritize direct premise
  corrections, then qualifications that reverse or condition a recommendation,
  then explicit reasoning objections. Return selected events in source order.

The values below illustrate shape only. Do not copy them unless the source and
semantic reading independently support them. Return JSON only in this shape:
{
  "user_pressure_events": [
    {
      "kind": "material_qualification",
      "quote": "smallest exact contiguous substring from one user turn",
      "turn_index": 1
    }
  ]
}
"""


USER_COUNTERPRESSURE_KINDS = {
    "premise_correction",
    "material_qualification",
    "reasoning_objection",
}


USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT = (
    USER_COUNTERPRESSURE_SYSTEM_PROMPT.replace(
        "USER COUNTER-PRESSURE SEMANTICS",
        "USER COUNTER-PRESSURE TEMPORAL SEMANTICS",
        1,
    )
    + """

TEMPORAL COVERAGE ADDENDUM:

- Review the qualifying counter-pressure chronologically as distinct semantic
  threads.
- For each material thread, preserve the earliest USER span where that thread
  first enters the reasoning. Always return that first introduction even when
  a later statement is clearer, stronger, or easier to quote.
- Return a later statement from the same thread as a separate event only when
  it materially strengthens the evidence, makes an ambiguity explicit, or
  changes the implication for the reasoning. Do not return mere repetition.
- Do not replace a first introduction with its later strengthening. When both
  qualify, return both events with the same three-label vocabulary already
  defined above. Do not add relationship fields or thread labels.
- When the eight-event cap requires prioritization, preserve first
  introductions across distinct material threads before later strengthenings.
  Keep the final array in source-turn order.

Thread identity, first introduction, and material strengthening are semantic
judgments for this reader. Return only the JSON shape defined above.
"""
)


OPTION_EVIDENCE_SYSTEM_PROMPT = """You are extracting OPTION AND EVIDENCE SEMANTICS from a decision-support conversation.

Your job is to preserve two connected parts of the decision structure: live
options or action gates, and the boundaries of the available evidence. Do not
extract user-pressure events, question trajectories, assistant stance
trajectories, or dropped-thread status.

Return JSON with exactly two arrays:

1. option_events
   - kind: option, decision_threshold, evidence_gate, or stop_rule
   - status: proposed, current, rejected, deferred, or unresolved
   - quote: exact contiguous substring from one USER or ASSISTANT turn
   - turn_index and speaker: source location

2. evidence_boundary_events
   - kind: stated_unknown, weak_evidence, unsupported_assistant_claim, or deferred_criterion
   - claim: short neutral description of the boundary
   - quote: exact contiguous substring from one USER or ASSISTANT turn
   - turn_index and speaker: source location

Evidence rules:
- Every quote must be copied character-for-character from the claimed turn.
- Never insert `...` or otherwise shorten text inside a quote.
- Use decision_threshold only for an explicit condition stated as preceding an
  action (for example, confirm participation, then announce). Use evidence_gate
  for an explicit body of evidence that must be satisfied; do not relabel a
  single before-action condition as evidence_gate.
- In evidence_boundary_events, keep weak evidence, explicit unknowns,
  unsupported assistant claims, and deferred criteria as separate events.
  Cover every material boundary up to the stated cap rather than selecting a
  representative subset.
- Do not invent an event for something absent from the conversation.
- Do not turn an omitted alternative into a rejected option.
- Acknowledgement is not resolution.
- An assistant claim may be marked unsupported only as a provisional evidence
  boundary when the conversation itself supplies no support for that claim.
- Return no more than 8 option events and 8 evidence-boundary events.

The values below illustrate shape only. Do not copy them unless the source and
semantic reading independently support them. Return JSON only in this shape:
{
  "option_events": [
    {
      "kind": "option",
      "status": "proposed",
      "quote": "exact contiguous substring from one source turn",
      "turn_index": 1,
      "speaker": "user"
    }
  ],
  "evidence_boundary_events": [
    {
      "kind": "stated_unknown",
      "claim": "short neutral description",
      "quote": "exact contiguous substring from one source turn",
      "turn_index": 1,
      "speaker": "user"
    }
  ]
}
"""


@runtime_checkable
class BoundaryClient(Protocol):
    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]: ...


def build_core_semantic_shadow(
    *,
    context: ConversationContext,
    boundary: BoundaryClient,
) -> dict[str, Any]:
    """Build a source-grounded pre-audit shadow interpretation."""

    recording_boundary = SemanticCandidateLedgerRecorder(boundary)
    _constraints, constraint_stats = extract_live_constraints(
        context=context,
        boundary=recording_boundary,
        candidate_recorder=recording_boundary,
    )
    _stances, stance_stats = extract_stance_events(
        context=context,
        boundary=recording_boundary,
        candidate_recorder=recording_boundary,
    )
    _dropped, dropped_stats = extract_dropped_threads(
        context=context,
        boundary=recording_boundary,
        candidate_recorder=recording_boundary,
    )

    source_prompt = _semantic_reader_user_prompt(context)
    raw_questions = recording_boundary.run_json(
        QUESTION_TRAJECTORY_SYSTEM_PROMPT,
        source_prompt,
    )
    raw_pressure = recording_boundary.run_json(
        USER_PRESSURE_SYSTEM_PROMPT,
        source_prompt,
    )
    raw_option_evidence = recording_boundary.run_json(
        OPTION_EVIDENCE_SYSTEM_PROMPT,
        source_prompt,
    )
    _question_events, question_validation = _validate_simple_events(
        context=context,
        raw_items=raw_questions.get("question_events"),
        family="question",
        reader_role="question_trajectory",
        candidate_recorder=recording_boundary,
    )
    _pressure_events, pressure_validation = _validate_simple_events(
        context=context,
        raw_items=raw_pressure.get("user_pressure_events"),
        family="user_pressure",
        reader_role="user_pressure",
        candidate_recorder=recording_boundary,
    )
    _option_events, option_validation = _validate_simple_events(
        context=context,
        raw_items=raw_option_evidence.get("option_events"),
        family="option",
        reader_role="option_evidence",
        candidate_recorder=recording_boundary,
    )
    _evidence_events, evidence_validation = _validate_simple_events(
        context=context,
        raw_items=raw_option_evidence.get("evidence_boundary_events"),
        family="evidence_boundary",
        reader_role="option_evidence",
        candidate_recorder=recording_boundary,
    )

    candidate_ledger = recording_boundary.build_ledger(context=context)
    _resolve_trajectory_references(candidate_ledger)
    semantic_events, current_view_manifest = reconstruct_current_semantic_view(
        candidate_ledger
    )

    return {
        "schema_version": CORE_SEMANTIC_SHADOW_SCHEMA_VERSION,
        "source": {
            "turn_count": len(context.turns),
            "conversation_sha256": _conversation_sha256(context),
            "contains_raw_conversation": False,
            "source_refs_are_local_turn_spans": True,
        },
        "semantic_candidate_ledger": candidate_ledger,
        "semantic_events": semantic_events,
        "current_view_manifest": current_view_manifest,
        "decision_work_projection": _decision_work_projection(semantic_events),
        "validation": {
            "question_trajectory": {
                "question_events": question_validation,
            },
            "user_pressure": {
                "user_pressure_events": pressure_validation,
            },
            "option_evidence": {
                "option_events": option_validation,
                "evidence_boundary_events": evidence_validation,
            },
            "specialists": {
                "live_constraints": _stats_dict(constraint_stats),
                "assistant_stances": _stats_dict(stance_stats),
                "dropped_threads": _stats_dict(dropped_stats),
            },
        },
        "non_claims": [
            "shadow_is_not_live_lane_input",
            "shadow_does_not_modify_graph_routing",
            "shadow_is_not_decision_quality_proof",
            "shadow_is_not_human_validation",
            "question_change_is_not_user_mind_change",
            "missing_event_is_not_proof_of_real_world_absence",
            "candidate_state_is_not_semantic_truth",
            "reader_agreement_is_not_correctness",
        ],
    }


def build_user_counterpressure_shadow(
    *,
    context: ConversationContext,
    boundary: BoundaryClient,
) -> dict[str, Any]:
    """Build the one-call, evaluation-only counter-pressure ablation."""

    return _build_user_counterpressure_shadow(
        context=context,
        boundary=boundary,
        system_prompt=USER_COUNTERPRESSURE_SYSTEM_PROMPT,
        schema_version=USER_COUNTERPRESSURE_SHADOW_SCHEMA_VERSION,
        temporal_contract=False,
    )


def build_user_counterpressure_temporal_shadow(
    *,
    context: ConversationContext,
    boundary: BoundaryClient,
) -> dict[str, Any]:
    """Build the prompt-only first-introduction temporal ablation."""

    return _build_user_counterpressure_shadow(
        context=context,
        boundary=boundary,
        system_prompt=USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT,
        schema_version=USER_COUNTERPRESSURE_TEMPORAL_SHADOW_SCHEMA_VERSION,
        temporal_contract=True,
    )


def _build_user_counterpressure_shadow(
    *,
    context: ConversationContext,
    boundary: BoundaryClient,
    system_prompt: str,
    schema_version: str,
    temporal_contract: bool,
) -> dict[str, Any]:
    """Build one counter-pressure artifact under an explicit prompt contract."""

    recording_boundary = SemanticCandidateLedgerRecorder(boundary)
    raw_pressure = recording_boundary.run_json(
        system_prompt,
        _semantic_reader_user_prompt(context),
    )
    _events, validation = _validate_simple_events(
        context=context,
        raw_items=raw_pressure.get("user_pressure_events"),
        family="user_pressure",
        reader_role="user_pressure",
        candidate_recorder=recording_boundary,
        allowed_kinds=USER_COUNTERPRESSURE_KINDS,
    )
    candidate_ledger = recording_boundary.build_ledger(context=context)
    semantic_events, current_view_manifest = reconstruct_current_semantic_view(
        candidate_ledger
    )

    return {
        "schema_version": schema_version,
        "source": {
            "turn_count": len(context.turns),
            "conversation_sha256": _conversation_sha256(context),
            "contains_raw_conversation": False,
            "source_refs_are_local_turn_spans": True,
        },
        "semantic_candidate_ledger": candidate_ledger,
        "semantic_events": semantic_events,
        "current_view_manifest": current_view_manifest,
        "validation": {
            "user_counterpressure": {
                "user_pressure_events": validation,
            }
        },
        "non_claims": [
            "counterpressure_shadow_is_not_full_conversation_understanding",
            "counterpressure_shadow_is_not_live_lane_input",
            "counterpressure_shadow_does_not_modify_graph_routing",
            "counterpressure_shadow_is_not_reasoning_quality_proof",
            "candidate_state_is_not_semantic_truth",
            "missing_event_is_not_proof_of_real_world_absence",
        ]
        + (
            [
                "thread_identity_is_a_semantic_reader_judgment",
                "later_strengthening_does_not_replace_first_introduction",
            ]
            if temporal_contract
            else []
        ),
    }


def render_core_semantic_shadow_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _semantic_reader_user_prompt(context: ConversationContext) -> str:
    lines = ["SOURCE CONVERSATION:"]
    for turn in context.turns:
        lines.extend(
            [
                f"[Turn {turn.turn_index}] {turn.speaker.upper()}:",
                turn.text,
                "",
            ]
        )
    lines.append("Perform only the assigned semantic job. Respond with JSON only.")
    return "\n".join(lines)


_FAMILY_CONFIG: dict[str, dict[str, Any]] = {
    "question": {
        "kinds": {"initial", "intermediate", "current"},
        "kind_field": "stage",
        "speakers": {"user"},
        "max_items": 8,
        "question_functions": {"decision_choice", "evidence_gate", "implementation", "diagnosis", "other"},
    },
    "user_pressure": {
        "kinds": {"correction", "evidence_request", "concern", "timing_pressure", "value"},
        "kind_field": "kind",
        "speakers": {"user"},
        "max_items": 8,
    },
    "option": {
        "kinds": {"option", "decision_threshold", "evidence_gate", "stop_rule"},
        "kind_field": "kind",
        "speakers": {"user", "assistant"},
        "max_items": 8,
        "statuses": {"proposed", "current", "rejected", "deferred", "unresolved"},
    },
    "evidence_boundary": {
        "kinds": {"stated_unknown", "weak_evidence", "unsupported_assistant_claim", "deferred_criterion"},
        "kind_field": "kind",
        "speakers": {"user", "assistant"},
        "max_items": 8,
    },
}


def _validate_simple_events(
    *,
    context: ConversationContext,
    raw_items: object,
    family: str,
    reader_role: str,
    candidate_recorder: SemanticCandidateLedgerRecorder | None = None,
    allowed_kinds: set[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    config = _FAMILY_CONFIG[family]
    kinds = allowed_kinds if allowed_kinds is not None else config["kinds"]
    items = raw_items if isinstance(raw_items, list) else []
    turn_map = {(turn.turn_index, turn.speaker): turn.text for turn in context.turns}
    output: list[dict[str, Any]] = []
    invalid_shape = 0
    invalid_kind = 0
    invalid_status = 0
    invalid_source = 0
    invalid_quote = 0

    ledger_family = f"{family}_events"

    def record(
        proposal_index: int,
        raw: Any,
        state: str,
        reason: str,
        event: Any = None,
    ) -> None:
        if candidate_recorder is not None:
            candidate_recorder.record_candidate(
                reader_role=reader_role,
                family=ledger_family,
                proposal_index=proposal_index,
                raw_proposal=raw,
                mechanical_state=state,
                mechanical_reason=reason,
                event=event,
            )

    for proposal_index, item in enumerate(items):
        if proposal_index >= config["max_items"]:
            record(
                proposal_index,
                item,
                "not_evaluated_budget",
                "family_candidate_cap_exceeded",
            )
            continue
        if not isinstance(item, dict):
            invalid_shape += 1
            record(
                proposal_index,
                item,
                "invalid_evidence",
                "candidate_is_not_an_object",
            )
            continue
        kind = _text(item.get(config["kind_field"])).lower()
        if kind not in kinds:
            invalid_kind += 1
            record(
                proposal_index,
                item,
                "invalid_evidence",
                "candidate_kind_is_invalid",
            )
            continue
        speaker = _text(item.get("speaker") or ("user" if family in {"question", "user_pressure"} else "")).lower()
        if speaker not in config["speakers"]:
            invalid_source += 1
            record(
                proposal_index,
                item,
                "invalid_evidence",
                "candidate_speaker_is_invalid",
            )
            continue
        try:
            turn_index = int(item.get("turn_index"))
        except (TypeError, ValueError):
            invalid_source += 1
            record(
                proposal_index,
                item,
                "not_supported_by_source",
                "candidate_turn_is_invalid",
            )
            continue
        turn_text = turn_map.get((turn_index, speaker))
        if turn_text is None:
            invalid_source += 1
            record(
                proposal_index,
                item,
                "not_supported_by_source",
                "candidate_source_turn_not_found",
            )
            continue
        quote = _text(item.get("quote"))
        matched = find_substring_tolerant(quote, turn_text) if quote else None
        if matched is None:
            invalid_quote += 1
            record(
                proposal_index,
                item,
                "not_supported_by_source",
                "candidate_quote_not_found_in_source_turn",
            )
            continue
        start = turn_text.find(matched)
        if start < 0:
            start = turn_text.lower().find(matched.lower())
        if start < 0:
            invalid_quote += 1
            record(
                proposal_index,
                item,
                "not_supported_by_source",
                "candidate_quote_offset_not_found",
            )
            continue

        status = _text(item.get("status")).lower()
        if "statuses" in config and status not in config["statuses"]:
            invalid_status += 1
            record(
                proposal_index,
                item,
                "invalid_evidence",
                "candidate_status_is_invalid",
            )
            continue

        event: dict[str, Any] = {
            "event_id": _event_id(family, kind, turn_index, speaker, matched),
            "family": family,
            "kind": kind,
            "source": {
                "turn_index": turn_index,
                "speaker": speaker,
                "quote": matched,
                "start_char": start,
                "end_char": start + len(matched),
            },
            "grounding": "span",
            "provisional": True,
        }
        if family == "question":
            event["changes_prior_question"] = bool(item.get("changes_prior_question", False))
            event["relation_ambiguity"] = bool(
                item.get("relation_ambiguity", False)
            )
            function = _text(item.get("question_function")).lower()
            event["question_function"] = (
                function if function in config["question_functions"] else "other"
            )
        if family == "option":
            event["status"] = status
        if family == "evidence_boundary":
            event["claim"] = _text(item.get("claim"))[:240]
        output.append(event)
        record(
            proposal_index,
            item,
            "validated",
            "exact_source_and_contract_validation_passed",
            event,
        )

    return output, {
        "raw_count": len(items),
        "validated_count": len(output),
        "invalid_shape": invalid_shape,
        "invalid_kind": invalid_kind,
        "invalid_status": invalid_status,
        "invalid_source": invalid_source,
        "invalid_quote": invalid_quote,
        "truncated_count": max(0, len(items) - config["max_items"]),
    }


def _decision_work_projection(events: Mapping[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    question_events = events["question_events"]
    pressure_events = events["user_pressure_events"]
    option_events = events["option_events"]
    evidence_events = events["evidence_boundary_events"]
    constraints = events["live_constraint_events"]
    stances = events["assistant_stance_events"]
    dropped = events["dropped_thread_events"]

    return [
        _projection("decision_shape", "decision_question", question_events),
        _projection("decision_shape", "likely_starting_direction", stances[:1]),
        _projection("options_and_paths", "live_options", _kind_items(option_events, "option")),
        _projection("options_and_paths", "decision_thresholds", _kind_items(option_events, "decision_threshold")),
        _projection("options_and_paths", "stop_rules", _kind_items(option_events, "stop_rule")),
        _projection(
            "options_and_paths",
            "evidence_gates",
            _kind_items(option_events, "evidence_gate")
            + _kind_items(pressure_events, "evidence_request")
            + [
                item
                for item in question_events
                if _text(item.get("question_function")) == "evidence_gate"
            ],
        ),
        _projection("conversation_process", "unresolved_threads", pressure_events),
        _projection("conversation_process", "dropped_threads", dropped),
        _projection("provided_context_and_evidence", "user_provided_context", constraints),
        _projection(
            "stakeholders_and_values",
            "user_values_or_priorities",
            _kind_items(pressure_events, "value")
            + _kind_items(pressure_events, "timing_pressure"),
        ),
        _projection(
            "constraints_and_unknowns",
            "real_world_unknowns",
            evidence_events,
        ),
        _projection(
            "conversation_process",
            "assistant_stance_trajectory",
            stances,
            contract_field=False,
        ),
        _projection(
            "conversation_process",
            "user_corrections_and_counter_pressure",
            pressure_events,
            contract_field=False,
        ),
    ]


def _projection(
    field_group: str,
    field_name: str,
    items: list[dict[str, Any]],
    *,
    contract_field: bool = True,
) -> dict[str, Any]:
    eligible_items = [
        item for item in items if item.get("routing_eligible", True) is True
    ]
    excluded_items = [
        item for item in items if item.get("routing_eligible", True) is not True
    ]
    return {
        "field_group": field_group,
        "field_name": field_name,
        "contract_field": contract_field,
        "status": (
            "present_provisional"
            if eligible_items
            else "present_but_not_routing_eligible"
            if excluded_items
            else "not_observed"
        ),
        "grounding": "span" if eligible_items else "none",
        "item_ids": [_item_id(item) for item in eligible_items],
        "item_count": len(eligible_items),
        "observed_item_count": len(items),
        "excluded_item_ids": [_item_id(item) for item in excluded_items],
        "excluded_item_count": len(excluded_items),
        "must_not_be_used_as_quality_label": True,
    }


def _kind_items(items: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [item for item in items if _text(item.get("kind")) == kind]


def _item_id(item: Mapping[str, Any]) -> str:
    return _text(item.get("event_id") or item.get("issue_id") or item.get("stance_id"))


def _event_to_dict(item: Any) -> dict[str, Any]:
    if hasattr(item, "to_dict"):
        payload = item.to_dict()
    elif is_dataclass(item):
        payload = asdict(item)
    elif isinstance(item, Mapping):
        payload = dict(item)
    else:
        raise TypeError("semantic event is not serializable")

    provenance = getattr(item, "provenance", None)
    if isinstance(provenance, DerivationProvenance):
        provenance_payload = payload.get("provenance")
        if isinstance(provenance_payload, dict):
            provenance_payload["provenance_status"] = provenance.evidence_status
        payload["provenance_status"] = provenance.evidence_status
        payload["routing_eligible"] = provenance.routing_eligible
    else:
        payload.setdefault("routing_eligible", True)
    return payload


def _stats_dict(stats: Any) -> dict[str, Any]:
    if is_dataclass(stats):
        return asdict(stats)
    if isinstance(stats, Mapping):
        return dict(stats)
    return {}


def _conversation_sha256(context: ConversationContext) -> str:
    body = "\n".join(
        f"{turn.turn_index}|{turn.speaker}|{turn.text}" for turn in context.turns
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _event_id(family: str, kind: str, turn: int, speaker: str, quote: str) -> str:
    digest = hashlib.sha256(f"{family}|{kind}|{turn}|{speaker}|{quote}".encode("utf-8")).hexdigest()[:12]
    return f"{family}_{kind}_t{turn}_{digest}"


_QUESTION_RELATIONS = {
    "opens",
    "continues",
    "narrows",
    "reframes",
    "gates",
    "supersedes",
    "coexists",
    "returns_to",
    "unclear",
}
_STANCE_RELATIONS = {
    "commitment",
    "revision",
    "qualification",
    "condition",
    "deferral",
    "initial",
}


def _resolve_trajectory_references(ledger: Mapping[str, Any]) -> None:
    """Resolve only reader-declared references; never infer a relation."""

    candidates = ledger.get("candidates")
    if not isinstance(candidates, list):
        return
    specs = {
        "question_events": {
            "relation_field": "relation_to_prior_question",
            "reference_mode": "source_quote",
            "target_turn_field": "related_question_turn_index",
            "target_quote_field": "related_question_quote",
            "speaker": "user",
            "allowed_relations": _QUESTION_RELATIONS,
        },
        "assistant_stance_events": {
            "relation_field": "relation",
            "reference_mode": "candidate_index",
            "target_index_field": "related_stance_event_index",
            "target_turn_field": "related_stance_turn_index",
            "target_quote_field": "related_stance_quote",
            "speaker": "assistant",
            "allowed_relations": _STANCE_RELATIONS,
        },
    }

    for family, spec in specs.items():
        family_records = [
            record
            for record in candidates
            if isinstance(record, dict)
            and record.get("family") == family
            and isinstance(record.get("event_snapshot"), dict)
        ]
        source_index: dict[tuple[int, str, str], list[dict[str, Any]]] = {}
        proposal_index: dict[int, list[dict[str, Any]]] = {}
        for record in family_records:
            source_key = _trajectory_source_key(record["event_snapshot"])
            if source_key is not None:
                source_index.setdefault(source_key, []).append(record)
            index = record.get("proposal_index")
            if isinstance(index, int):
                proposal_index.setdefault(index, []).append(record)

        for record in family_records:
            raw = record.get("raw_proposal")
            snapshot = record["event_snapshot"]
            if not isinstance(raw, Mapping):
                continue
            relation = _text(raw.get(spec["relation_field"])).lower()
            alternatives_raw = raw.get("alternative_relations")
            alternatives = (
                [
                    _text(item).lower()
                    for item in alternatives_raw
                    if _text(item).lower() in spec["allowed_relations"]
                ]
                if isinstance(alternatives_raw, list)
                else []
            )
            invalid_alternatives = (
                [
                    _text(item).lower()
                    for item in alternatives_raw
                    if _text(item)
                    and _text(item).lower() not in spec["allowed_relations"]
                ]
                if isinstance(alternatives_raw, list)
                else []
            )
            relation_status = (
                "declared"
                if relation in spec["allowed_relations"]
                else "invalid_declared_relation"
                if relation
                else "not_declared"
            )
            target_index: int | None = None
            target_turn = 0
            target_quote = ""
            index_order_status = "not_applicable"
            if spec["reference_mode"] == "candidate_index":
                index_field_present = spec["target_index_field"] in raw
                raw_index = raw.get(spec["target_index_field"])
                legacy_turn = raw.get(spec["target_turn_field"])
                legacy_quote = _text(raw.get(spec["target_quote_field"]))
                if raw_index is not None:
                    reference_mode = "candidate_index"
                    try:
                        target_index = (
                            int(raw_index) if not isinstance(raw_index, bool) else None
                        )
                    except (TypeError, ValueError):
                        target_index = None
                    current_index = int(record.get("proposal_index") or 0)
                    if target_index is None or target_index < 0:
                        matches = []
                        reference_status = "invalid_reference_shape"
                        chronology_status = "not_applicable"
                        index_order_status = "invalid"
                    else:
                        matches = proposal_index.get(target_index, [])
                        index_order_status = (
                            "prior_candidate_index"
                            if target_index < current_index
                            else "same_candidate_index"
                            if target_index == current_index
                            else "future_candidate_index"
                        )
                        reference_status, chronology_status = (
                            _resolved_reference_status(
                                current=snapshot,
                                matches=matches,
                            )
                        )
                elif index_field_present:
                    reference_mode = "candidate_index_explicit_null"
                    matches = []
                    reference_status = "not_declared"
                    chronology_status = "not_applicable"
                elif legacy_turn is not None or legacy_quote:
                    reference_mode = "legacy_source_quote"
                    target_turn, target_quote = _coerce_source_target(
                        legacy_turn,
                        legacy_quote,
                    )
                    matches, reference_status, chronology_status = (
                        _resolve_source_reference(
                            current=snapshot,
                            source_index=source_index,
                            turn_index=target_turn,
                            speaker=str(spec["speaker"]),
                            quote=target_quote,
                        )
                    )
                else:
                    reference_mode = "candidate_index_field_missing"
                    matches = []
                    reference_status = "not_declared"
                    chronology_status = "not_applicable"
            else:
                reference_mode = "source_quote"
                target_turn, target_quote = _coerce_source_target(
                    raw.get(spec["target_turn_field"]),
                    _text(raw.get(spec["target_quote_field"])),
                )
                matches, reference_status, chronology_status = (
                    _resolve_source_reference(
                        current=snapshot,
                        source_index=source_index,
                        turn_index=target_turn,
                        speaker=str(spec["speaker"]),
                        quote=target_quote,
                    )
                )
            target_ids = [str(item.get("candidate_id") or "") for item in matches]

            snapshot["trajectory"] = {
                "primary_relation": relation,
                "relation_status": relation_status,
                "relation_ambiguity": bool(raw.get("relation_ambiguity", False)),
                "alternative_relations": alternatives,
                "invalid_alternative_relations": invalid_alternatives,
                "reference_mode": reference_mode,
                "declared_target": {
                    "proposal_index": target_index,
                    "turn_index": target_turn,
                    "speaker": spec["speaker"],
                    "quote": target_quote,
                },
                "reference_status": reference_status,
                "target_candidate_ids": target_ids,
                "chronology_status": chronology_status,
                "index_order_status": index_order_status,
            }

    metrics = ledger.get("metrics")
    if isinstance(metrics, dict):
        metrics["trajectory_references"] = _trajectory_reference_metrics(
            candidates
        )


def _coerce_source_target(turn: object, quote: str) -> tuple[int, str]:
    try:
        turn_index = int(turn) if turn is not None else 0
    except (TypeError, ValueError):
        turn_index = 0
    return turn_index, quote


def _resolve_source_reference(
    *,
    current: Mapping[str, Any],
    source_index: Mapping[tuple[int, str, str], list[dict[str, Any]]],
    turn_index: int,
    speaker: str,
    quote: str,
) -> tuple[list[dict[str, Any]], str, str]:
    if not turn_index and not quote:
        return [], "not_declared", "not_applicable"
    if not turn_index or not quote:
        return [], "invalid_reference_shape", "not_applicable"
    matches = source_index.get((turn_index, speaker, _normalized(quote)), [])
    status, chronology = _resolved_reference_status(
        current=current,
        matches=matches,
    )
    return list(matches), status, chronology


def _resolved_reference_status(
    *,
    current: Mapping[str, Any],
    matches: list[dict[str, Any]],
) -> tuple[str, str]:
    if not matches:
        return "unresolved", "unknown"
    if len(matches) > 1:
        return "ambiguous_target", "unknown"
    target = matches[0].get("event_snapshot")
    if not isinstance(target, Mapping):
        return "unresolved", "unknown"
    chronology = (
        "prior_or_same_position"
        if _trajectory_position(target) <= _trajectory_position(current)
        else "target_after_event"
    )
    return "resolved", chronology


def _trajectory_reference_metrics(
    candidates: list[Any],
) -> dict[str, Any]:
    """Count mechanical reference outcomes without treating them as quality."""

    by_reference_status: dict[str, int] = {}
    by_chronology_status: dict[str, int] = {}
    by_relation_status: dict[str, int] = {}
    by_reference_mode: dict[str, int] = {}
    trajectory_event_count = 0
    ambiguous_relation_count = 0
    for record in candidates:
        snapshot = record.get("event_snapshot") if isinstance(record, Mapping) else None
        trajectory = (
            snapshot.get("trajectory") if isinstance(snapshot, Mapping) else None
        )
        if not isinstance(trajectory, Mapping):
            continue
        trajectory_event_count += 1
        if trajectory.get("relation_ambiguity") is True:
            ambiguous_relation_count += 1
        for key, target in (
            ("reference_status", by_reference_status),
            ("chronology_status", by_chronology_status),
            ("relation_status", by_relation_status),
            ("reference_mode", by_reference_mode),
        ):
            value = _text(trajectory.get(key)) or "missing"
            target[value] = target.get(value, 0) + 1

    return {
        "trajectory_event_count": trajectory_event_count,
        "ambiguous_relation_count": ambiguous_relation_count,
        "counts_by_reference_status": dict(sorted(by_reference_status.items())),
        "counts_by_chronology_status": dict(sorted(by_chronology_status.items())),
        "counts_by_relation_status": dict(sorted(by_relation_status.items())),
        "counts_by_reference_mode": dict(sorted(by_reference_mode.items())),
        "must_not_be_used_as_quality_label": True,
    }


def _trajectory_source_key(
    event: Mapping[str, Any],
) -> tuple[int, str, str] | None:
    source = event.get("source")
    if isinstance(source, Mapping):
        return (
            int(source.get("turn_index") or 0),
            _text(source.get("speaker")).lower(),
            _normalized(_text(source.get("quote"))),
        )
    provenance = event.get("provenance")
    span = (
        provenance.get("span_ref")
        if isinstance(provenance, Mapping)
        and isinstance(provenance.get("span_ref"), Mapping)
        else None
    )
    if not isinstance(span, Mapping):
        return None
    return (
        int(span.get("turn_index") or event.get("turn_index") or 0),
        _text(span.get("speaker") or event.get("speaker")).lower(),
        _normalized(_text(event.get("text"))),
    )


def _trajectory_position(event: Mapping[str, Any]) -> tuple[int, int]:
    source = event.get("source")
    if isinstance(source, Mapping):
        return int(source.get("turn_index") or 0), int(source.get("start_char") or 0)
    provenance = event.get("provenance")
    span = (
        provenance.get("span_ref")
        if isinstance(provenance, Mapping)
        and isinstance(provenance.get("span_ref"), Mapping)
        else {}
    )
    return (
        int(span.get("turn_index") or event.get("turn_index") or 0),
        int(span.get("start_char") or 0),
    )


def _normalized(value: str) -> str:
    return " ".join(value.lower().split())


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""
