"""Deterministic semantic-coverage report over archived Lolla artifacts.

This report is intentionally offline and observational. It reads existing
archive artifacts, records where semantic evidence appears to live, and avoids
copying raw transcript, memo, revised-answer, model-message, provider-reasoning,
or quote-validation failure text into the output.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .conversation_loader import load_conversation_context
from .ir import ConversationIR
from .ir_constructor import construct_conversation_ir


SEMANTIC_COVERAGE_REPORT_SCHEMA_VERSION = "lolla.semantic_coverage_report.v0"

SEMANTIC_ELEMENTS = (
    "decision",
    "live_constraints",
    "user_values_or_priorities_signal",
    "changed_constraints_or_later_pushback",
    "dropped_or_under_carried_threads",
    "assistant_stance_or_recommendation_lineage",
    "counter_pressure",
    "revised_answer_change_reason",
    "unanswered_dimensions",
    "actionability_boundaries",
)

_ARTIFACT_NAMES = (
    "conversation.txt",
    "extraction.json",
    "extraction_adequacy_report.json",
    "result.json",
    "revised.txt",
    "memo.md",
    "reasoning_trace.json",
    "evaluation.json",
    "agent_result.json",
)

_JSON_ARTIFACT_NAMES = {
    "extraction.json",
    "extraction_adequacy_report.json",
    "result.json",
    "reasoning_trace.json",
    "evaluation.json",
    "agent_result.json",
}

_GROUNDING_ORDER = {
    "span": 5,
    "turn_ref": 4,
    "derivation": 3,
    "artifact_present_only": 2,
    "none": 1,
}


def build_semantic_coverage_report(
    run_dir: Path | str,
    *,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic semantic coverage report for one run directory."""

    run_path = Path(run_dir)
    source_artifacts = {
        name: _artifact_source(run_path / name, json_artifact=name in _JSON_ARTIFACT_NAMES)
        for name in _ARTIFACT_NAMES
    }
    json_artifacts = {
        name: _read_json_object(run_path / name)
        for name in _JSON_ARTIFACT_NAMES
    }

    extraction = json_artifacts["extraction.json"]
    extraction_payload = _mapping(extraction.get("extraction"))
    adequacy = json_artifacts["extraction_adequacy_report.json"]
    result = json_artifacts["result.json"]
    reasoning_trace = json_artifacts["reasoning_trace.json"]
    evaluation = json_artifacts["evaluation.json"]
    agent_result = json_artifacts["agent_result.json"]

    context, ir, build_errors = _build_context_and_ir(run_path)
    signal_summary = _signal_summary(
        context=context,
        ir=ir,
        extraction_payload=extraction_payload,
        adequacy=adequacy,
        result=result,
        reasoning_trace=reasoning_trace,
        evaluation=evaluation,
        agent_result=agent_result,
    )
    semantic_elements = _semantic_elements(
        source_artifacts=source_artifacts,
        signal_summary=signal_summary,
    )
    case_id, run_id = _identity(run_path, agent_result=agent_result, evaluation=evaluation)

    return {
        "schema_version": SEMANTIC_COVERAGE_REPORT_SCHEMA_VERSION,
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": f"{case_id}/{run_id}" if case_id and run_id else "",
        "created_at": created_at
        if created_at is not None
        else _stable_created_at(agent_result=agent_result, evaluation=evaluation, result=result),
        "source": {
            "local_only": True,
            "shareable_without_review": False,
            "raw_archives_read": True,
            "raw_transcript_included": False,
            "raw_memo_included": False,
            "raw_revised_answer_included": False,
            "raw_model_messages_included": False,
            "provider_reasoning_details_included": False,
            "raw_failed_quote_text_included": False,
            "absolute_archive_paths_included": False,
            "model_calls": 0,
            "llm_judge_used": False,
            "runtime_behavior_changed": False,
        },
        "source_artifacts": source_artifacts,
        "deterministic_signal_summary": signal_summary,
        "semantic_elements": semantic_elements,
        "overall_coverage_summary": _overall_coverage_summary(
            source_artifacts=source_artifacts,
            semantic_elements=semantic_elements,
            build_errors=build_errors,
        ),
        "notes": [
            "This report measures artifact coverage, not semantic correctness.",
            "Raw archive text remains local source material and is not exported.",
            "Partial coverage means evidence is weakly grounded, scattered, or artifact-level only.",
            "Not-measured means current artifacts do not expose a deterministic field for the element.",
            "This report does not approve agent action or change runtime behavior.",
        ],
        "non_goals": [
            "No runtime integration.",
            "No prompt change.",
            "No model calls or LLM judge.",
            "No answer-quality scoring.",
            "No graph DB, embeddings, or chunking.",
            "No conversation_understanding_ir.v0 implementation.",
            "No provider-boundary policy change.",
        ],
    }


def write_semantic_coverage_report(
    run_dir: Path | str,
    out_path: Path | str,
    *,
    created_at: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Write a semantic coverage report JSON for one run directory."""

    report = build_semantic_coverage_report(run_dir, created_at=created_at)
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_semantic_coverage_report_json(report), encoding="utf-8")
    return path, report


def render_semantic_coverage_report_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _semantic_elements(
    *,
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        "decision": _decision_element(source_artifacts, signal_summary),
        "live_constraints": _live_constraints_element(source_artifacts, signal_summary),
        "user_values_or_priorities_signal": _user_values_element(
            source_artifacts,
            signal_summary,
        ),
        "changed_constraints_or_later_pushback": _changed_constraints_element(
            source_artifacts,
            signal_summary,
        ),
        "dropped_or_under_carried_threads": _dropped_threads_element(
            source_artifacts,
            signal_summary,
        ),
        "assistant_stance_or_recommendation_lineage": _assistant_stance_element(
            source_artifacts,
            signal_summary,
        ),
        "counter_pressure": _counter_pressure_element(source_artifacts, signal_summary),
        "revised_answer_change_reason": _revised_change_element(
            source_artifacts,
            signal_summary,
        ),
        "unanswered_dimensions": _unanswered_dimensions_element(
            source_artifacts,
            signal_summary,
        ),
        "actionability_boundaries": _actionability_boundaries_element(
            source_artifacts,
            signal_summary,
        ),
    }


def _decision_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    extraction = _mapping(signal_summary.get("extraction"))
    ir = _mapping(signal_summary.get("conversation_ir"))
    present = bool(extraction.get("decision_situation_present"))
    grounding = "none"
    if present:
        grounding = _grounding_from_counts(_mapping(ir.get("decision_frame_grounding")))
    status = "present" if present else "missing"
    return _element(
        status=status,
        artifact_owners=_present_owners(
            source_artifacts,
            ["extraction.json", "extraction_adequacy_report.json"],
        ),
        grounding=grounding,
        evidence_counts={
            "decision_situation_present": int(present),
            "decision_frame_anchor_count": _safe_int(ir.get("decision_frame_anchor_count")),
        },
        notes=(
            ["Decision situation exists as an extracted field."]
            if present
            else ["No deterministic decision_situation field was found."]
        ),
    )


def _live_constraints_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    extraction = _mapping(signal_summary.get("extraction"))
    ir = _mapping(signal_summary.get("conversation_ir"))
    adequacy = _mapping(signal_summary.get("extraction_adequacy"))
    count = _safe_int(extraction.get("live_constraints_count"))
    grounding_counts = _mapping(ir.get("constraint_grounding"))
    grounding = _grounding_from_counts(grounding_counts) if count else "none"
    if count <= 0:
        status = "missing"
    elif grounding == "span":
        status = "present"
    else:
        status = "partial"
    return _element(
        status=status,
        artifact_owners=_present_owners(
            source_artifacts,
            ["extraction.json", "extraction_adequacy_report.json"],
        ),
        grounding=grounding,
        evidence_counts={
            "live_constraints_count": count,
            "invalid_turn_ref_count": _safe_int(adequacy.get("invalid_turn_ref_count")),
            "missing_turn_ref_count": _safe_int(adequacy.get("missing_turn_ref_count")),
            "speaker_mismatch_count": _safe_int(adequacy.get("speaker_mismatch_count")),
            **_prefixed_counts("grounding", grounding_counts),
        },
        notes=[
            (
                "Live constraints are present but not span-grounded."
                if status == "partial"
                else "Live constraints have span-grounded deterministic evidence."
                if status == "present"
                else "No deterministic live_constraints entries were found."
            )
        ],
    )


def _user_values_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    del signal_summary
    return _element(
        status="not_measured",
        artifact_owners=_present_owners(source_artifacts, ["conversation.txt", "result.json", "memo.md"]),
        grounding="none",
        evidence_counts={"first_class_user_values_field_count": 0},
        notes=[
            "Current artifacts do not expose a deterministic first-class user-values field.",
            "This report does not infer values from raw transcript or memo prose.",
        ],
    )


def _changed_constraints_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    conversation = _mapping(signal_summary.get("conversation"))
    extraction = _mapping(signal_summary.get("extraction"))
    changed_count = _safe_int(extraction.get("constraints_after_first_user_turn_count"))
    later_user_turn_count = _safe_int(conversation.get("later_user_turn_count"))
    if changed_count > 0:
        status = "partial"
        grounding = "turn_ref"
        note = "Later-turn constraints are approximated from introduced_turn metadata."
    elif later_user_turn_count > 0:
        status = "not_measured"
        grounding = "none"
        note = "Later user turns exist, but no deterministic changed-constraint field is exposed."
    else:
        status = "not_measured"
        grounding = "none"
        note = "No later user turns were available for a deterministic changed-constraint approximation."
    return _element(
        status=status,
        artifact_owners=_present_owners(source_artifacts, ["conversation.txt", "extraction.json"]),
        grounding=grounding,
        evidence_counts={
            "later_user_turn_count": later_user_turn_count,
            "constraints_after_first_user_turn_count": changed_count,
        },
        notes=[note],
    )


def _dropped_threads_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    extraction = _mapping(signal_summary.get("extraction"))
    result_cards = _mapping(signal_summary.get("result_cards"))
    ir = _mapping(signal_summary.get("conversation_ir"))
    count = _safe_int(extraction.get("dropped_threads_count"))
    grounding_counts = _mapping(ir.get("open_loop_grounding"))
    grounding = _grounding_from_counts(grounding_counts) if count else "none"
    if count > 0 and grounding == "span":
        status = "present"
    elif count > 0:
        status = "partial"
    elif result_cards.get("structural_coverage_card_present"):
        status = "not_measured"
        grounding = "artifact_present_only"
    else:
        status = "missing"
    return _element(
        status=status,
        artifact_owners=_present_owners(
            source_artifacts,
            ["extraction.json", "result.json", "memo.md"],
        ),
        grounding=grounding,
        evidence_counts={
            "dropped_threads_count": count,
            "structural_coverage_card_present": int(
                bool(result_cards.get("structural_coverage_card_present"))
            ),
            **_prefixed_counts("grounding", grounding_counts),
        },
        notes=[
            (
                "Dropped or under-carried thread evidence is present but weakly grounded."
                if status == "partial"
                else "Structural coverage exists, but no deterministic dropped-thread field was found."
                if status == "not_measured"
                else "Dropped-thread evidence is span-grounded."
                if status == "present"
                else "No dropped-thread or structural-coverage signal was found."
            )
        ],
    )


def _assistant_stance_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    ir = _mapping(signal_summary.get("conversation_ir"))
    result_cards = _mapping(signal_summary.get("result_cards"))
    agent = _mapping(signal_summary.get("agent_result"))
    stance_count = _safe_int(ir.get("stance_events_count"))
    grounding_counts = _mapping(ir.get("stance_grounding"))
    lineage_artifact_count = sum(
        int(bool(value))
        for value in [
            result_cards.get("audit_summary_present"),
            result_cards.get("delta_card_present"),
            result_cards.get("frame_pressure_card_present"),
            result_cards.get("revised_answer_present"),
            agent.get("changed_advice_summary_present"),
        ]
    )
    if stance_count > 0:
        status = "present" if _grounding_from_counts(grounding_counts) == "span" else "partial"
        grounding = _grounding_from_counts(grounding_counts)
    elif lineage_artifact_count > 0:
        status = "partial"
        grounding = "artifact_present_only"
    else:
        status = "missing"
        grounding = "none"
    return _element(
        status=status,
        artifact_owners=_present_owners(
            source_artifacts,
            ["result.json", "revised.txt", "memo.md", "agent_result.json"],
        ),
        grounding=grounding,
        evidence_counts={
            "stance_events_count": stance_count,
            "lineage_artifact_count": lineage_artifact_count,
            **_prefixed_counts("grounding", grounding_counts),
        },
        notes=[
            (
                "Stance lineage is artifact-level or weakly grounded."
                if status == "partial"
                else "Span-grounded stance events are present."
                if status == "present"
                else "No deterministic assistant stance or lineage signal was found."
            )
        ],
    )


def _counter_pressure_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    result_cards = _mapping(signal_summary.get("result_cards"))
    card_count = sum(
        int(bool(result_cards.get(key)))
        for key in (
            "delta_card_present",
            "frame_pressure_card_present",
            "structural_coverage_card_present",
            "audit_summary_present",
        )
    )
    status = "present" if card_count > 0 else "missing"
    return _element(
        status=status,
        artifact_owners=_present_owners(source_artifacts, ["result.json"]),
        grounding="artifact_present_only" if card_count else "none",
        evidence_counts={"counter_pressure_artifact_count": card_count},
        notes=[
            (
                "Counter-pressure artifacts are present; this report does not copy their text."
                if card_count
                else "No counter-pressure artifact signal was found."
            )
        ],
    )


def _revised_change_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    result_cards = _mapping(signal_summary.get("result_cards"))
    agent = _mapping(signal_summary.get("agent_result"))
    explicit_count = sum(
        int(bool(value))
        for value in [
            agent.get("changed_advice_summary_present"),
            result_cards.get("memo_what_changed_present"),
            result_cards.get("memo_take_back_or_set_aside_present"),
        ]
    )
    support_artifact_count = sum(
        int(bool(value))
        for value in [
            result_cards.get("revised_answer_present"),
            result_cards.get("memo_note_present"),
        ]
    )
    if explicit_count > 0:
        status = "present"
    elif support_artifact_count > 0:
        status = "partial"
    else:
        status = "missing"
    return _element(
        status=status,
        artifact_owners=_present_owners(
            source_artifacts,
            ["agent_result.json", "result.json", "revised.txt", "memo.md"],
        ),
        grounding="artifact_present_only" if status != "missing" else "none",
        evidence_counts={
            "explicit_change_reason_artifact_count": explicit_count,
            "support_artifact_count": support_artifact_count,
        },
        notes=[
            (
                "A change-reason artifact field is present."
                if status == "present"
                else "Revised/memo artifacts exist, but no explicit change-reason field was found."
                if status == "partial"
                else "No revised-answer change-reason signal was found."
            )
        ],
    )


def _unanswered_dimensions_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    result_cards = _mapping(signal_summary.get("result_cards"))
    evidence_count = sum(
        int(bool(value))
        for value in [
            result_cards.get("structural_coverage_card_present"),
            result_cards.get("gap_check_present"),
            result_cards.get("gap_check_summary_present"),
            result_cards.get("memo_note_present"),
        ]
    )
    status = "present" if evidence_count > 0 else "missing"
    return _element(
        status=status,
        artifact_owners=_present_owners(source_artifacts, ["result.json", "memo.md"]),
        grounding="artifact_present_only" if evidence_count else "none",
        evidence_counts={"unanswered_dimension_artifact_count": evidence_count},
        notes=[
            (
                "Unanswered-dimension artifacts are present; this report does not copy their text."
                if evidence_count
                else "No unanswered-dimension artifact signal was found."
            )
        ],
    )


def _actionability_boundaries_element(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    signal_summary: Mapping[str, Any],
) -> dict[str, Any]:
    agent = _mapping(signal_summary.get("agent_result"))
    do_not_act_count = _safe_int(agent.get("do_not_act_before_count"))
    human_question_count = _safe_int(agent.get("human_questions_count"))
    explicit_count = do_not_act_count + human_question_count
    if explicit_count > 0:
        status = "present"
    elif agent.get("present"):
        status = "partial"
    else:
        status = "missing"
    return _element(
        status=status,
        artifact_owners=_present_owners(
            source_artifacts,
            ["agent_result.json", "revised.txt", "memo.md"],
        ),
        grounding="artifact_present_only" if status != "missing" else "none",
        evidence_counts={
            "do_not_act_before_count": do_not_act_count,
            "human_questions_count": human_question_count,
        },
        notes=[
            (
                "Actionability boundaries are exposed through agent_result fields."
                if status == "present"
                else "agent_result exists, but explicit boundary lists are empty."
                if status == "partial"
                else "No actionability-boundary artifact signal was found."
            )
        ],
    )


def _element(
    *,
    status: str,
    artifact_owners: Sequence[str],
    grounding: str,
    evidence_counts: Mapping[str, int],
    notes: Sequence[str],
) -> dict[str, Any]:
    return {
        "status": status,
        "artifact_owners": list(artifact_owners),
        "grounding": grounding,
        "evidence_counts": dict(evidence_counts),
        "needs_review": status != "present" or grounding in {"artifact_present_only", "derivation", "none"},
        "notes": list(notes),
    }


def _signal_summary(
    *,
    context: Any,
    ir: ConversationIR | None,
    extraction_payload: Mapping[str, Any],
    adequacy: Mapping[str, Any],
    result: Mapping[str, Any],
    reasoning_trace: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    agent_result: Mapping[str, Any],
) -> dict[str, Any]:
    live_constraints = [_mapping(item) for item in _list(extraction_payload.get("live_constraints"))]
    dropped_threads = [_mapping(item) for item in _list(extraction_payload.get("dropped_threads"))]
    first_user_turn = _first_user_turn(context)
    constraints_after_first = sum(
        1
        for item in live_constraints
        if first_user_turn is not None
        and _nullable_int(item.get("introduced_turn")) is not None
        and _nullable_int(item.get("introduced_turn")) > first_user_turn
    )
    extraction_summary = _mapping(adequacy.get("extraction_field_summary"))
    quote_validation = _mapping(extraction_summary.get("quote_validation"))
    gap_findings = _mapping(adequacy.get("provenance_gap_findings"))
    result_cards = _result_card_summary(result)
    agent_summary = _agent_result_summary(agent_result)

    return {
        "conversation": _conversation_summary(context),
        "extraction": {
            "decision_situation_present": bool(_text(extraction_payload.get("decision_situation")))
            or bool(extraction_summary.get("decision_situation_present")),
            "synthesized_position_present": bool(_text(extraction_payload.get("synthesized_position")))
            or bool(extraction_summary.get("synthesized_position_present")),
            "original_framing_present": bool(_text(extraction_payload.get("original_framing")))
            or bool(extraction_summary.get("original_framing_present")),
            "live_constraints_count": len(live_constraints)
            or _safe_int(extraction_summary.get("live_constraints_count")),
            "dropped_threads_count": len(dropped_threads)
            or _safe_int(extraction_summary.get("dropped_threads_count")),
            "reasoning_passages_count": len(_list(extraction_payload.get("reasoning_passages")))
            or _safe_int(extraction_summary.get("reasoning_passages_count")),
            "constraints_after_first_user_turn_count": constraints_after_first,
            "quote_validation_present": bool(quote_validation)
            or bool(_mapping(extraction_payload.get("_quote_validation"))),
            "quote_fabrication_count": _safe_int(quote_validation.get("fabricated"))
            or _safe_int(_mapping(extraction_payload.get("_quote_validation")).get("fabricated")),
        },
        "extraction_adequacy": {
            "present": bool(adequacy),
            "adequacy_status": _text(adequacy.get("adequacy_status")),
            "invalid_turn_ref_count": _safe_int(gap_findings.get("invalid_turn_ref_count")),
            "missing_turn_ref_count": _safe_int(gap_findings.get("missing_turn_ref_count")),
            "speaker_mismatch_count": _safe_int(gap_findings.get("speaker_mismatch_count")),
            "fields_with_no_source_grounding_count": len(
                _list(gap_findings.get("fields_with_no_source_grounding"))
            ),
            "fields_only_turn_ref_grounded_count": len(
                _list(gap_findings.get("fields_only_turn_ref_grounded"))
            ),
            "fields_derivation_grounded_count": len(
                _list(gap_findings.get("fields_derivation_grounded"))
            ),
        },
        "conversation_ir": _conversation_ir_summary(ir),
        "result_cards": result_cards,
        "agent_result": agent_summary,
        "reasoning_trace": {
            "present": bool(reasoning_trace),
            "artifact_count": len(_list(reasoning_trace.get("artifacts"))),
        },
        "evaluation": {
            "present": bool(evaluation),
            "checks_count": len(_list(evaluation.get("checks"))),
            "overall_present": bool(_text(evaluation.get("overall"))),
            "caller_readiness_present": bool(_text(evaluation.get("caller_readiness"))),
        },
    }


def _conversation_ir_summary(ir: ConversationIR | None) -> dict[str, Any]:
    if ir is None:
        return {
            "available": False,
            "frame_anchors_count": 0,
            "decision_frame_anchor_count": 0,
            "user_issue_events_count": 0,
            "constraint_events_count": 0,
            "open_loop_events_count": 0,
            "stance_events_count": 0,
            "provenance_kinds_count": {"span": 0, "turn_ref": 0, "derivation": 0},
            "decision_frame_grounding": {},
            "constraint_grounding": {},
            "open_loop_grounding": {},
            "stance_grounding": {},
        }
    decision_anchors = [
        anchor
        for anchor in ir.frame_anchors
        if anchor.frame_pattern == "decision_situation"
    ]
    constraints = [event for event in ir.user_issue_events if event.kind == "constraint"]
    open_loops = [event for event in ir.user_issue_events if event.kind == "open_loop"]
    return {
        "available": True,
        "frame_anchors_count": len(ir.frame_anchors),
        "decision_frame_anchor_count": len(decision_anchors),
        "user_issue_events_count": len(ir.user_issue_events),
        "constraint_events_count": len(constraints),
        "open_loop_events_count": len(open_loops),
        "stance_events_count": len(ir.stance_events),
        "provenance_kinds_count": _counter_dict(ir.provenance_tier_counts()),
        "decision_frame_grounding": _provenance_counts(decision_anchors),
        "constraint_grounding": _provenance_counts(constraints),
        "open_loop_grounding": _provenance_counts(open_loops),
        "stance_grounding": _provenance_counts(ir.stance_events),
    }


def _conversation_summary(context: Any) -> dict[str, Any]:
    if context is None:
        return {
            "available": False,
            "parsed_turn_count": 0,
            "user_turn_count": 0,
            "assistant_turn_count": 0,
            "later_user_turn_count": 0,
        }
    user_turns = [turn for turn in context.turns if turn.speaker == "user"]
    assistant_turns = [turn for turn in context.turns if turn.speaker == "assistant"]
    return {
        "available": True,
        "parsed_turn_count": len(context.turns),
        "user_turn_count": len(user_turns),
        "assistant_turn_count": len(assistant_turns),
        "later_user_turn_count": max(0, len(user_turns) - 1),
    }


def _result_card_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "present": bool(result),
        "delta_card_present": bool(_mapping(result.get("delta_card"))),
        "frame_pressure_card_present": bool(_mapping(result.get("frame_pressure_card"))),
        "structural_coverage_card_present": bool(_mapping(result.get("structural_coverage_card"))),
        "audit_summary_present": bool(_text(result.get("audit_summary"))),
        "gap_check_present": bool(result.get("has_gap_check")) or bool(_text(result.get("gap_check"))),
        "gap_check_summary_present": bool(_text(result.get("gap_check_summary"))),
        "revised_answer_present": bool(result.get("revised_answer_present"))
        or bool(_text(result.get("revised_answer"))),
        "memo_note_present": bool(_text(result.get("memo_substantive_title")))
        or bool(_text(result.get("memo_orientation_note"))),
        "memo_what_changed_present": bool(_text(result.get("memo_what_changed"))),
        "memo_take_back_or_set_aside_present": bool(
            _text(result.get("memo_take_back_or_set_aside"))
        ),
    }


def _agent_result_summary(agent_result: Mapping[str, Any]) -> dict[str, Any]:
    do_not_act = _list(agent_result.get("do_not_act_before"))
    human_questions = _list(agent_result.get("human_questions"))
    return {
        "present": bool(agent_result),
        "status_present": bool(_text(agent_result.get("status"))),
        "caller_action_present": bool(_text(agent_result.get("caller_action"))),
        "changed_advice_summary_present": bool(_text(agent_result.get("changed_advice_summary"))),
        "main_counter_pressure_present": bool(_text(agent_result.get("main_counter_pressure"))),
        "do_not_act_before_count": len(do_not_act),
        "human_questions_count": len(human_questions),
    }


def _overall_coverage_summary(
    *,
    source_artifacts: Mapping[str, Mapping[str, Any]],
    semantic_elements: Mapping[str, Mapping[str, Any]],
    build_errors: Sequence[str],
) -> dict[str, Any]:
    status_counts = Counter(_text(element.get("status")) for element in semantic_elements.values())
    grounding_counts = Counter(_text(element.get("grounding")) for element in semantic_elements.values())
    present_artifacts = [
        name
        for name, artifact in source_artifacts.items()
        if bool(artifact.get("present"))
    ]
    return {
        "semantic_element_count": len(semantic_elements),
        "status_counts": _counter_dict(status_counts),
        "grounding_counts": _counter_dict(grounding_counts),
        "needs_review_count": sum(
            1 for element in semantic_elements.values() if bool(element.get("needs_review"))
        ),
        "present_artifact_count": len(present_artifacts),
        "missing_artifacts": [
            name
            for name, artifact in source_artifacts.items()
            if not bool(artifact.get("present"))
        ],
        "build_error_categories": sorted(set(build_errors)),
    }


def _build_context_and_ir(run_path: Path) -> tuple[Any, ConversationIR | None, list[str]]:
    conversation_path = run_path / "conversation.txt"
    extraction_path = run_path / "extraction.json"
    errors: list[str] = []
    if not conversation_path.is_file() or not extraction_path.is_file():
        return None, None, errors
    try:
        context = load_conversation_context(extraction_path, conversation_path)
    except Exception:  # noqa: BLE001 - diagnostics should degrade, not crash
        return None, None, ["conversation_context_load_failed"]
    try:
        ir = construct_conversation_ir(context)
    except Exception:  # noqa: BLE001 - diagnostics should degrade, not crash
        errors.append("conversation_ir_build_failed")
        ir = None
    return context, ir, errors


def _artifact_source(path: Path, *, json_artifact: bool) -> dict[str, Any]:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return {
            "present": False,
            "byte_count": 0,
            "sha256": "",
            "json_valid": None if not json_artifact else False,
            "read_error": "",
        }
    except OSError:
        return {
            "present": False,
            "byte_count": 0,
            "sha256": "",
            "json_valid": None if not json_artifact else False,
            "read_error": "artifact_read_failed",
        }
    json_valid: bool | None = None
    if json_artifact:
        try:
            json.loads(data.decode("utf-8"))
            json_valid = True
        except (UnicodeDecodeError, json.JSONDecodeError):
            json_valid = False
    return {
        "present": True,
        "byte_count": len(data),
        "sha256": _sha256_uri(data),
        "json_valid": json_valid,
        "read_error": "",
    }


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _identity(
    run_path: Path,
    *,
    agent_result: Mapping[str, Any],
    evaluation: Mapping[str, Any],
) -> tuple[str, str]:
    case_id = (
        _bounded_text(agent_result.get("case_id"))
        or _bounded_text(evaluation.get("case_id"))
        or _bounded_text(run_path.parent.name)
    )
    run_id = (
        _bounded_text(agent_result.get("run_id"))
        or _bounded_text(evaluation.get("run_id"))
        or _bounded_text(run_path.name)
    )
    return case_id, run_id


def _stable_created_at(
    *,
    agent_result: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    result: Mapping[str, Any],
) -> str:
    return (
        _text(agent_result.get("created_at"))
        or _text(evaluation.get("created_at"))
        or _text(result.get("memo_note_written_at"))
        or _text(result.get("revised_answer_written_at"))
    )


def _first_user_turn(context: Any) -> int | None:
    if context is None:
        return None
    user_turns = [turn.turn_index for turn in context.turns if turn.speaker == "user"]
    return min(user_turns) if user_turns else None


def _provenance_counts(objects: Sequence[Any]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for obj in objects:
        provenance = getattr(obj, "provenance", None)
        kind = getattr(provenance, "kind", "")
        if kind:
            counts[str(kind)] += 1
    return _counter_dict(counts)


def _grounding_from_counts(counts: Mapping[str, Any]) -> str:
    best = "none"
    for grounding, value in counts.items():
        if _safe_int(value) <= 0:
            continue
        if _GROUNDING_ORDER.get(str(grounding), 0) > _GROUNDING_ORDER[best]:
            best = str(grounding)
    return best


def _present_owners(
    source_artifacts: Mapping[str, Mapping[str, Any]],
    names: Sequence[str],
) -> list[str]:
    return [
        name
        for name in names
        if bool(_mapping(source_artifacts.get(name)).get("present"))
    ]


def _prefixed_counts(prefix: str, counts: Mapping[str, Any]) -> dict[str, int]:
    return {
        f"{prefix}_{_text(key)}_count": _safe_int(value)
        for key, value in sorted(counts.items(), key=lambda item: str(item[0]))
    }


def _counter_dict(counter: Mapping[str, Any]) -> dict[str, int]:
    return {
        str(key): _safe_int(value)
        for key, value in sorted(counter.items(), key=lambda item: str(item[0]))
    }


def _sha256_uri(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bounded_text(value: Any, *, limit: int = 160) -> str:
    text = _text(value)
    if len(text) > limit:
        return text[:limit]
    return text


def _nullable_int(value: Any) -> int | None:
    if isinstance(value, bool) or value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
