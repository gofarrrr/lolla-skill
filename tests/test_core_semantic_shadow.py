from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.conversation_loader import load_conversation_context
from engine.system_b.core_semantic_shadow import (
    OPTION_EVIDENCE_SYSTEM_PROMPT,
    QUESTION_TRAJECTORY_SYSTEM_PROMPT,
    USER_COUNTERPRESSURE_KINDS,
    USER_COUNTERPRESSURE_SYSTEM_PROMPT,
    USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT,
    USER_PRESSURE_SYSTEM_PROMPT,
    build_core_semantic_shadow,
    build_user_counterpressure_shadow,
    build_user_counterpressure_temporal_shadow,
)
from engine.system_b.dropped_threads_extraction import DROPPED_THREADS_SYSTEM_PROMPT
from engine.system_b.live_constraints_extraction import LIVE_CONSTRAINTS_SYSTEM_PROMPT
from engine.system_b.semantic_candidate_ledger import (
    reconstruct_current_semantic_view,
)
from engine.system_b.stance_extraction import STANCE_EXTRACTION_SYSTEM_PROMPT


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta"
ONCOLOGIST_CONVERSATION = REPO_ROOT / "research/test-cases/case_oncologist_conversation.txt"
ONCOLOGIST_EXTRACTION = (
    REPO_ROOT
    / "research/test-cases/phase2a-lane3-equivalence-2026-04-23/_scratch/oncologist_extraction.json"
)


class FakeBoundary:
    def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        del user_prompt
        if "LIVE CONSTRAINTS" in system_prompt:
            return {
                "live_constraints": [
                    {"mode": "span", "kind": "constraint", "kind_ambiguity": False, "text": "They have not signed anything", "turn_index": 3}
                ]
            }
        if "STANCE EVENT" in system_prompt:
            return {
                "stance_events": [
                    {"relation": "commitment", "text": "I would announce a limited public beta and make this prospect the flagship design partner.", "turn_index": 2, "relation_ambiguity": False}
                ]
            }
        if "DROPPED THREADS" in system_prompt:
            return {
                "dropped_threads": [
                    {"text": "the board is excited mainly because of the company's name", "turn_index": 3, "speaker": "user", "kind": "open_loop", "kind_ambiguity": False, "superseded_by": "prestige upside"}
                ]
            }
        if "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
            return {"question_events": [
                {"stage": "initial", "question_function": "decision_choice", "quote": "Should we launch publicly and use its logo to attract other customers?", "turn_index": 1, "changes_prior_question": False},
                {"stage": "current", "question_function": "evidence_gate", "quote": "What evidence should we require before announcing?", "turn_index": 5, "changes_prior_question": True}
            ]}
        if "USER PRESSURE SEMANTICS" in system_prompt:
            return {
                "user_pressure_events": [
                {"kind": "evidence_request", "quote": "What evidence should we require before announcing?", "turn_index": 5},
                {"kind": "timing_pressure", "quote": "I am also worried that waiting will make us lose the opportunity", "turn_index": 5}
                ]
            }
        if "OPTION AND EVIDENCE SEMANTICS" in system_prompt:
            return {
            "option_events": [
                {"kind": "decision_threshold", "status": "current", "quote": "Ask the prospect to confirm participation by email, then announce a 30-day beta next month.", "turn_index": 6, "speaker": "assistant"}
            ],
            "evidence_boundary_events": [
                {"kind": "deferred_criterion", "claim": "Success criteria are deferred until after launch.", "quote": "You can define detailed success criteria after the first week once you see actual usage.", "turn_index": 6, "speaker": "assistant"}
            ]
            }
        raise AssertionError("unexpected semantic prompt")


def _context(tmp_path: Path):
    conversation = FIXTURE_DIR / "conversation.txt"
    extraction = tmp_path / "extraction.json"
    extraction.write_text(
        json.dumps(
            {
                "status": "ok",
                "extraction": {
                    "is_strategic": True,
                    "decision_situation": "Whether to launch the beta.",
                    "live_constraints": [],
                    "synthesized_position": "Launch after email confirmation.",
                    "reasoning_passages": [],
                    "original_framing": "Whether to launch publicly.",
                    "dropped_threads": []
                }
            }
        ),
        encoding="utf-8"
    )
    return load_conversation_context(extraction, conversation)


def test_shadow_combines_focused_specialist_events(tmp_path: Path) -> None:
    payload = build_core_semantic_shadow(context=_context(tmp_path), boundary=FakeBoundary())
    events = payload["semantic_events"]

    assert payload["schema_version"] == "lolla.core_semantic_shadow.v0"
    assert payload["semantic_candidate_ledger"]["schema_version"] == (
        "lolla.semantic_candidate_ledger.v0"
    )
    assert len(events["question_events"]) == 2
    assert len(events["live_constraint_events"]) == 1
    assert len(events["assistant_stance_events"]) == 1
    assert len(events["dropped_thread_events"]) == 1
    assert events["question_events"][1]["changes_prior_question"] is True
    assert events["question_events"][1]["question_function"] == "evidence_gate"
    assert events["evidence_boundary_events"][0]["grounding"] == "span"
    assert all(
        event.get("candidate_id")
        for family in events.values()
        for event in family
    )

    rebuilt, manifest = reconstruct_current_semantic_view(
        payload["semantic_candidate_ledger"]
    )
    assert rebuilt == events
    assert manifest == payload["current_view_manifest"]
    assert manifest["reconstructible_from_candidate_ledger"] is True


def test_focused_prompts_keep_semantic_jobs_separate() -> None:
    assert "initial, intermediate, or current" in QUESTION_TRAJECTORY_SYSTEM_PROMPT
    assert "relation_to_prior_question" in QUESTION_TRAJECTORY_SYSTEM_PROMPT
    assert "no more than 8 events" in QUESTION_TRAJECTORY_SYSTEM_PROMPT
    assert "user_pressure_events" not in QUESTION_TRAJECTORY_SYSTEM_PROMPT
    assert "question_events" not in USER_PRESSURE_SYSTEM_PROMPT
    assert "user_pressure_events" in USER_PRESSURE_SYSTEM_PROMPT
    assert "option_events" not in USER_PRESSURE_SYSTEM_PROMPT
    assert "user_pressure_events" not in OPTION_EVIDENCE_SYSTEM_PROMPT
    assert "option_events" in OPTION_EVIDENCE_SYSTEM_PROMPT
    assert "evidence_boundary_events" in OPTION_EVIDENCE_SYSTEM_PROMPT
    assert '"speaker": "user"' in OPTION_EVIDENCE_SYSTEM_PROMPT
    assert "Never insert `...`" in QUESTION_TRAJECTORY_SYSTEM_PROMPT
    assert "Never insert `...`" in USER_PRESSURE_SYSTEM_PROMPT
    assert "Never insert `...`" in OPTION_EVIDENCE_SYSTEM_PROMPT
    assert "candidate_disposition" not in QUESTION_TRAJECTORY_SYSTEM_PROMPT
    assert "candidate_disposition" not in USER_PRESSURE_SYSTEM_PROMPT
    assert "candidate_disposition" not in OPTION_EVIDENCE_SYSTEM_PROMPT


def test_counterpressure_v2_contract_is_narrower_than_failed_sk4_prompt() -> None:
    assert USER_COUNTERPRESSURE_KINDS == {
        "premise_correction",
        "material_qualification",
        "reasoning_objection",
    }
    assert "USER COUNTER-PRESSURE SEMANTICS" in (
        USER_COUNTERPRESSURE_SYSTEM_PROMPT
    )
    assert "Do not return a standalone question or request" in (
        USER_COUNTERPRESSURE_SYSTEM_PROMPT
    )
    assert "Do not return a generic emotion, downside, worry, value" in (
        USER_COUNTERPRESSURE_SYSTEM_PROMPT
    )
    assert "cross-family overlap is not" in USER_COUNTERPRESSURE_SYSTEM_PROMPT
    assert "smallest exact contiguous substring" in (
        USER_COUNTERPRESSURE_SYSTEM_PROMPT
    )
    assert "kind: correction, evidence_request, concern" in (
        USER_PRESSURE_SYSTEM_PROMPT
    )
    assert "TEMPORAL COVERAGE ADDENDUM" not in USER_COUNTERPRESSURE_SYSTEM_PROMPT


def test_counterpressure_v21_changes_only_temporal_prompt_instructions() -> None:
    temporal_base, addendum = USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT.split(
        "\n\nTEMPORAL COVERAGE ADDENDUM:",
        1,
    )
    assert temporal_base.replace(
        "USER COUNTER-PRESSURE TEMPORAL SEMANTICS",
        "USER COUNTER-PRESSURE SEMANTICS",
        1,
    ) == USER_COUNTERPRESSURE_SYSTEM_PROMPT
    assert "earliest USER span" in addendum
    assert "Always return that first introduction" in addendum
    assert "Do not replace a first introduction" in addendum
    assert "later statement from the same thread as a separate event" in addendum
    assert "Do not add relationship fields or thread labels" in addendum
    assert "premise_correction" in USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    assert "material_qualification" in USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    assert "reasoning_objection" in USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    assert "relation_to_prior" not in USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT
    assert "thread_id" not in USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT


def test_counterpressure_v21_preserves_first_and_later_spans_with_one_call() -> None:
    first = (
        "we haven't had the real conversation about what 3 nights a week away "
        "actually looks like for four-plus years"
    )
    later = (
        'But he said it in the way that means "I will not stop you from taking '
        'it." Which is different from "yes this is a good idea for us."'
    )

    class TemporalBoundary:
        def __init__(self) -> None:
            self.system_prompts: list[str] = []

        def run_json(
            self,
            system_prompt: str,
            user_prompt: str,
        ) -> dict[str, object]:
            self.system_prompts.append(system_prompt)
            assert first in user_prompt
            assert later in user_prompt
            return {
                "user_pressure_events": [
                    {
                        "kind": "material_qualification",
                        "quote": first,
                        "turn_index": 2,
                    },
                    {
                        "kind": "material_qualification",
                        "quote": later,
                        "turn_index": 4,
                    },
                ]
            }

    context = load_conversation_context(
        ONCOLOGIST_EXTRACTION,
        ONCOLOGIST_CONVERSATION,
    )
    boundary = TemporalBoundary()
    payload = build_user_counterpressure_temporal_shadow(
        context=context,
        boundary=boundary,
    )

    assert boundary.system_prompts == [USER_COUNTERPRESSURE_TEMPORAL_SYSTEM_PROMPT]
    assert payload["schema_version"] == (
        "lolla.user_counterpressure_temporal_shadow.v0"
    )
    events = payload["semantic_events"]["user_pressure_events"]
    assert [event["source"]["turn_index"] for event in events] == [2, 4]
    assert [event["source"]["quote"] for event in events] == [first, later]
    assert {event["kind"] for event in events} == {"material_qualification"}
    assert all("thread_id" not in event for event in events)
    assert all("relation_to_prior" not in event for event in events)
    calls = payload["semantic_candidate_ledger"]["reader_calls"]
    assert len(calls) == 1
    assert calls[0]["reader_role"] == "user_pressure"
    assert calls[0]["raw_candidate_counts"] == {"user_pressure_events": 2}
    assert "thread_identity_is_a_semantic_reader_judgment" in payload["non_claims"]


def test_counterpressure_v2_is_one_call_and_rejects_old_catch_all_kind(
    tmp_path: Path,
) -> None:
    class CounterpressureBoundary:
        def __init__(self) -> None:
            self.system_prompts: list[str] = []

        def run_json(
            self,
            system_prompt: str,
            user_prompt: str,
        ) -> dict[str, object]:
            self.system_prompts.append(system_prompt)
            assert "SOURCE CONVERSATION:" in user_prompt
            return {
                "user_pressure_events": [
                    {
                        "kind": "material_qualification",
                        "quote": "They have not signed anything",
                        "turn_index": 3,
                    },
                    {
                        "kind": "concern",
                        "quote": (
                            "I am also worried that waiting will make us lose "
                            "the opportunity"
                        ),
                        "turn_index": 5,
                    },
                ]
            }

    boundary = CounterpressureBoundary()
    payload = build_user_counterpressure_shadow(
        context=_context(tmp_path),
        boundary=boundary,
    )

    assert len(boundary.system_prompts) == 1
    assert boundary.system_prompts == [USER_COUNTERPRESSURE_SYSTEM_PROMPT]
    assert payload["schema_version"] == "lolla.user_counterpressure_shadow.v0"
    events = payload["semantic_events"]["user_pressure_events"]
    assert [event["kind"] for event in events] == ["material_qualification"]
    assert events[0]["source"]["quote"] == "They have not signed anything"
    validation = payload["validation"]["user_counterpressure"][
        "user_pressure_events"
    ]
    assert validation == {
        "raw_count": 2,
        "validated_count": 1,
        "invalid_shape": 0,
        "invalid_kind": 1,
        "invalid_status": 0,
        "invalid_source": 0,
        "invalid_quote": 0,
        "truncated_count": 0,
    }
    calls = payload["semantic_candidate_ledger"]["reader_calls"]
    assert len(calls) == 1
    assert calls[0]["reader_role"] == "user_pressure"
    assert calls[0]["raw_candidate_counts"] == {"user_pressure_events": 2}
    assert payload["semantic_candidate_ledger"]["metrics"][
        "expected_proposal_count"
    ] == 2
    assert payload["semantic_candidate_ledger"]["metrics"]["proposal_count"] == 2


def test_shadow_adds_only_focused_stance_linking_to_shared_prompts(
    tmp_path: Path,
) -> None:
    assert "candidate_disposition" not in LIVE_CONSTRAINTS_SYSTEM_PROMPT
    assert "candidate_disposition" not in STANCE_EXTRACTION_SYSTEM_PROMPT
    assert "candidate_disposition" not in DROPPED_THREADS_SYSTEM_PROMPT
    assert "related_stance_turn_index" not in STANCE_EXTRACTION_SYSTEM_PROMPT
    assert "related_stance_event_index" not in STANCE_EXTRACTION_SYSTEM_PROMPT

    class PromptRecordingBoundary(FakeBoundary):
        def __init__(self) -> None:
            self.system_prompts: list[str] = []

        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            self.system_prompts.append(system_prompt)
            return super().run_json(system_prompt, user_prompt)

    boundary = PromptRecordingBoundary()
    build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=boundary,
    )

    assert len(boundary.system_prompts) == 6
    assert all("candidate_disposition" not in prompt for prompt in boundary.system_prompts)
    stance_prompt = next(
        prompt for prompt in boundary.system_prompts if "STANCE EVENT" in prompt
    )
    assert "related_stance_turn_index" not in stance_prompt
    assert "related_stance_event_index" in stance_prompt
    assert '"related_stance_event_index": null' in stance_prompt


def test_user_pressure_reader_preserves_genuine_multi_role_span(
    tmp_path: Path,
) -> None:
    quote = "I am also worried that waiting will make us lose the opportunity"

    class MultiRolePressureBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "USER PRESSURE SEMANTICS" in system_prompt:
                return {
                    "user_pressure_events": [
                        {"kind": "timing_pressure", "quote": quote, "turn_index": 5},
                        {"kind": "concern", "quote": quote, "turn_index": 5},
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=MultiRolePressureBoundary(),
    )
    events = payload["semantic_events"]["user_pressure_events"]

    assert len(events) == 2
    assert {event["kind"] for event in events} == {"timing_pressure", "concern"}
    assert len({event["candidate_id"] for event in events}) == 2


def test_exact_duplicate_pressure_stays_in_ledger_but_not_current_view(
    tmp_path: Path,
) -> None:
    item = {
        "kind": "timing_pressure",
        "quote": "I am also worried that waiting will make us lose the opportunity",
        "turn_index": 5,
    }

    class DuplicatePressureBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "USER PRESSURE SEMANTICS" in system_prompt:
                return {"user_pressure_events": [dict(item), dict(item)]}
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=DuplicatePressureBoundary(),
    )
    events = payload["semantic_events"]["user_pressure_events"]
    candidates = [
        record
        for record in payload["semantic_candidate_ledger"]["candidates"]
        if record["family"] == "user_pressure_events"
    ]

    assert len(events) == 1
    assert len(candidates) == 2
    assert [record["terminal_state"] for record in candidates] == [
        "selected_for_current_view",
        "duplicate_identity",
    ]
    assert candidates[1]["terminal_reason"] == (
        "exact_event_identity_already_selected"
    )


def test_question_trajectory_resolves_reader_declared_source_reference(
    tmp_path: Path,
) -> None:
    initial_quote = (
        "Should we launch publicly and use its logo to attract other customers?"
    )

    class QuestionTrajectoryBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            payload = super().run_json(system_prompt, user_prompt)
            if "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
                payload["question_events"] = [
                    {
                        "stage": "initial",
                        "question_function": "decision_choice",
                        "quote": initial_quote,
                        "turn_index": 1,
                        "changes_prior_question": False,
                        "relation_to_prior_question": "opens",
                    },
                    {
                        "stage": "current",
                        "question_function": "evidence_gate",
                        "quote": "What evidence should we require before announcing?",
                        "turn_index": 5,
                        "changes_prior_question": True,
                        "relation_to_prior_question": "gates",
                        "related_question_turn_index": 1,
                        "related_question_quote": initial_quote,
                        "relation_ambiguity": True,
                        "alternative_relations": ["narrows"],
                    },
                ]
            return payload

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=QuestionTrajectoryBoundary(),
    )
    questions = payload["semantic_events"]["question_events"]
    initial, current = questions
    trajectory = current["trajectory"]

    assert trajectory["primary_relation"] == "gates"
    assert trajectory["relation_ambiguity"] is True
    assert trajectory["alternative_relations"] == ["narrows"]
    assert current["candidate_state"] == "ambiguous_competing_read"
    assert trajectory["reference_status"] == "resolved"
    assert trajectory["target_candidate_ids"] == [initial["candidate_id"]]
    assert trajectory["chronology_status"] == "prior_or_same_position"
    metrics = payload["semantic_candidate_ledger"]["metrics"][
        "trajectory_references"
    ]
    assert metrics["counts_by_reference_status"] == {
        "not_declared": 2,
        "resolved": 1,
    }
    assert metrics["ambiguous_relation_count"] == 1
    assert metrics["must_not_be_used_as_quality_label"] is True


def test_unresolved_question_reference_is_preserved_without_semantic_rejection(
    tmp_path: Path,
) -> None:
    class UnresolvedQuestionBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            payload = super().run_json(system_prompt, user_prompt)
            if "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
                payload["question_events"] = [
                    {
                        "stage": "current",
                        "question_function": "evidence_gate",
                        "quote": "What evidence should we require before announcing?",
                        "turn_index": 5,
                        "changes_prior_question": True,
                        "relation_to_prior_question": "gates",
                        "related_question_turn_index": 1,
                        "related_question_quote": "A question that was never asked",
                    }
                ]
            return payload

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=UnresolvedQuestionBoundary(),
    )
    current = payload["semantic_events"]["question_events"][0]

    assert current["candidate_state"] == "selected_for_current_view"
    assert current["trajectory"]["reference_status"] == "unresolved"
    assert current["trajectory"]["target_candidate_ids"] == []


def test_stance_trajectory_resolves_reader_declared_prior_stance(
    tmp_path: Path,
) -> None:
    initial_quote = (
        "I would announce a limited public beta and make this prospect the "
        "flagship design partner."
    )
    later_quote = (
        "Keep the beta limited to three companies, avoid promising a "
        "service-level agreement, and use the announcement to test demand."
    )

    class StanceTrajectoryBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "STANCE EVENT" in system_prompt:
                return {
                    "stance_events": [
                        {
                            "relation": "commitment",
                            "text": initial_quote,
                            "turn_index": 2,
                            "relation_ambiguity": False,
                        },
                        {
                            "relation": "qualification",
                            "text": later_quote,
                            "turn_index": 4,
                            "relation_ambiguity": True,
                            "alternative_relations": ["condition"],
                            "related_stance_event_index": 0,
                        },
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=StanceTrajectoryBoundary(),
    )
    stances = payload["semantic_events"]["assistant_stance_events"]
    initial, later = stances
    trajectory = later["trajectory"]

    assert trajectory["primary_relation"] == "qualification"
    assert trajectory["alternative_relations"] == ["condition"]
    assert trajectory["reference_mode"] == "candidate_index"
    assert trajectory["declared_target"]["proposal_index"] == 0
    assert trajectory["reference_status"] == "resolved"
    assert trajectory["target_candidate_ids"] == [initial["candidate_id"]]
    assert trajectory["chronology_status"] == "prior_or_same_position"
    assert trajectory["index_order_status"] == "prior_candidate_index"


def test_declared_future_trajectory_target_is_flagged_not_rejected(
    tmp_path: Path,
) -> None:
    initial_quote = (
        "I would announce a limited public beta and make this prospect the "
        "flagship design partner."
    )
    later_quote = (
        "Keep the beta limited to three companies, avoid promising a "
        "service-level agreement, and use the announcement to test demand."
    )

    class FutureReferenceBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "STANCE EVENT" in system_prompt:
                return {
                    "stance_events": [
                        {
                            "relation": "commitment",
                            "text": initial_quote,
                            "turn_index": 2,
                            "related_stance_event_index": 1,
                        },
                        {
                            "relation": "qualification",
                            "text": later_quote,
                            "turn_index": 4,
                        },
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=FutureReferenceBoundary(),
    )
    first = payload["semantic_events"]["assistant_stance_events"][0]

    assert first["candidate_state"] == "selected_for_current_view"
    assert first["trajectory"]["reference_status"] == "resolved"
    assert first["trajectory"]["chronology_status"] == "target_after_event"
    assert first["trajectory"]["index_order_status"] == "future_candidate_index"


def test_invalid_stance_candidate_index_is_visible_without_semantic_rejection(
    tmp_path: Path,
) -> None:
    class InvalidIndexBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "STANCE EVENT" in system_prompt:
                return {
                    "stance_events": [
                        {
                            "relation": "commitment",
                            "text": (
                                "I would announce a limited public beta and make "
                                "this prospect the flagship design partner."
                            ),
                            "turn_index": 2,
                            "related_stance_event_index": "not-an-index",
                        }
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=InvalidIndexBoundary(),
    )
    stance = payload["semantic_events"]["assistant_stance_events"][0]

    assert stance["candidate_state"] == "selected_for_current_view"
    assert stance["trajectory"]["reference_status"] == "invalid_reference_shape"
    assert stance["trajectory"]["index_order_status"] == "invalid"


def test_explicit_null_stance_link_is_distinct_from_missing_link_field(
    tmp_path: Path,
) -> None:
    class ExplicitNullBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            payload = super().run_json(system_prompt, user_prompt)
            if "STANCE EVENT" in system_prompt:
                payload["stance_events"][0]["related_stance_event_index"] = None
            return payload

    explicit_payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=ExplicitNullBoundary(),
    )
    missing_payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=FakeBoundary(),
    )
    explicit = explicit_payload["semantic_events"]["assistant_stance_events"][0]
    missing = missing_payload["semantic_events"]["assistant_stance_events"][0]

    assert explicit["trajectory"]["reference_mode"] == (
        "candidate_index_explicit_null"
    )
    assert missing["trajectory"]["reference_mode"] == (
        "candidate_index_field_missing"
    )


def test_shadow_projection_keeps_question_change_distinct_from_mind_change(tmp_path: Path) -> None:
    payload = build_core_semantic_shadow(context=_context(tmp_path), boundary=FakeBoundary())
    projection = {
        item["field_name"]: item for item in payload["decision_work_projection"]
    }

    assert projection["decision_question"]["item_count"] == 2
    assert projection["evidence_gates"]["item_count"] == 2
    assert projection["assistant_stance_trajectory"]["item_count"] == 1
    assert "user_changed_mind_during_conversation" not in projection
    assert "question_change_is_not_user_mind_change" in payload["non_claims"]


def test_shadow_drops_non_source_quotes(tmp_path: Path) -> None:
    class InvalidJointBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            payload = super().run_json(system_prompt, user_prompt)
            if "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
                payload["question_events"] = [
                    {"stage": "current", "quote": "A fabricated current question", "turn_index": 5, "changes_prior_question": True}
                ]
            return payload

    payload = build_core_semantic_shadow(
        context=_context(tmp_path), boundary=InvalidJointBoundary()
    )

    assert payload["semantic_events"]["question_events"] == []
    assert payload["validation"]["question_trajectory"]["question_events"]["invalid_quote"] == 1
    question_candidates = [
        item
        for item in payload["semantic_candidate_ledger"]["candidates"]
        if item["family"] == "question_events"
    ]
    assert len(question_candidates) == 1
    assert question_candidates[0]["raw_proposal"]["quote"] == (
        "A fabricated current question"
    )
    assert question_candidates[0]["terminal_state"] == "not_supported_by_source"
    assert question_candidates[0]["current_view_eligible"] is False


def test_shadow_serializes_derivation_components_and_routing_status(
    tmp_path: Path,
) -> None:
    class DerivationBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "LIVE CONSTRAINTS" in system_prompt:
                return {
                    "live_constraints": [
                        {
                            "mode": "derivation",
                            "text": "Interest remains weaker than a purchase commitment",
                            "turn_refs": [
                                {
                                    "turn_index": 3,
                                    "span_excerpt": "They have not signed anything.",
                                },
                                {
                                    "turn_index": 5,
                                    "span_excerpt": (
                                        "I am worried we are treating their interest "
                                        "as a purchase commitment"
                                    ),
                                },
                            ],
                            "kind": "constraint",
                            "kind_ambiguity": False,
                        }
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=DerivationBoundary(),
    )
    event = payload["semantic_events"]["live_constraint_events"][0]
    projection = {
        item["field_name"]: item for item in payload["decision_work_projection"]
    }

    assert event["provenance_status"] == "component_evidence_complete"
    assert event["routing_eligible"] is True
    assert len(event["provenance"]["components"]) == 2
    assert event["provenance"]["components"][0]["quote"] == (
        "They have not signed anything."
    )
    assert projection["user_provided_context"]["item_count"] == 1
    assert projection["user_provided_context"]["excluded_item_count"] == 0


def test_shadow_excludes_incomplete_derivation_from_projection(
    tmp_path: Path,
) -> None:
    class IncompleteDerivationBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "LIVE CONSTRAINTS" in system_prompt:
                return {
                    "live_constraints": [
                        {
                            "mode": "derivation",
                            "text": "Unsupported combined constraint",
                            "turn_refs": [
                                {
                                    "turn_index": 3,
                                    "span_excerpt": "They have not signed anything.",
                                },
                                {
                                    "turn_index": 5,
                                    "span_excerpt": "This quote is not in the conversation",
                                },
                            ],
                            "kind": "constraint",
                            "kind_ambiguity": False,
                        }
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=IncompleteDerivationBoundary(),
    )
    assert payload["semantic_events"]["live_constraint_events"] == []
    candidates = [
        item
        for item in payload["semantic_candidate_ledger"]["candidates"]
        if item["family"] == "live_constraint_events"
    ]
    assert len(candidates) == 1
    candidate = candidates[0]
    event = candidate["event_snapshot"]
    projection = {
        item["field_name"]: item for item in payload["decision_work_projection"]
    }

    assert event["provenance_status"] == "component_evidence_incomplete"
    assert event["routing_eligible"] is False
    assert candidate["terminal_state"] == "not_supported_by_source"
    assert candidate["current_view_eligible"] is False
    assert [item["state"] for item in candidate["state_history"]] == [
        "proposed",
        "not_supported_by_source",
    ]
    assert projection["user_provided_context"]["item_count"] == 0
    assert projection["user_provided_context"]["observed_item_count"] == 0
    assert projection["user_provided_context"]["excluded_item_count"] == 0
    assert projection["user_provided_context"]["status"] == "not_observed"


def test_candidate_ledger_records_reader_identity_without_prompt_text(
    tmp_path: Path,
) -> None:
    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=FakeBoundary(),
    )
    ledger = payload["semantic_candidate_ledger"]

    assert len(ledger["reader_calls"]) == 6
    assert [call["reader_role"] for call in ledger["reader_calls"]] == [
        "live_constraints",
        "assistant_stances",
        "dropped_threads",
        "question_trajectory",
        "user_pressure",
        "option_evidence",
    ]
    for call in ledger["reader_calls"]:
        assert call["system_prompt_sha256"]
        assert call["user_prompt_sha256"]
        assert call["prompt_text_persisted"] is False
        assert "system_prompt" not in call
        assert "user_prompt" not in call

    metrics = ledger["metrics"]
    assert metrics["candidate_custody_complete"] is True
    assert metrics["expected_proposal_count"] == metrics["proposal_count"]
    assert metrics["proposal_count"] == metrics["terminal_record_count"]
    assert metrics["unterminated_record_count"] == 0
    disposition = metrics["semantic_disposition_observability"]
    assert disposition["explicit_disposition_is_optional"] is True
    assert disposition["explicit_disposition_count"] == 0
    assert disposition["unobserved_disposition_count"] == metrics["proposal_count"]
    assert disposition["emitted_candidates_are_not_a_complete_hypothesis_set"] is True


def test_multiple_reader_designated_current_questions_remain_ambiguous(
    tmp_path: Path,
) -> None:
    class CompetingCurrentBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            payload = super().run_json(system_prompt, user_prompt)
            if "QUESTION TRAJECTORY SEMANTICS" in system_prompt:
                payload["question_events"] = [
                    {
                        "stage": "current",
                        "question_function": "decision_choice",
                        "quote": (
                            "Should we launch publicly and use its logo to attract "
                            "other customers?"
                        ),
                        "turn_index": 1,
                        "changes_prior_question": False,
                    },
                    {
                        "stage": "current",
                        "question_function": "evidence_gate",
                        "quote": "What evidence should we require before announcing?",
                        "turn_index": 5,
                        "changes_prior_question": True,
                    },
                ]
            return payload

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=CompetingCurrentBoundary(),
    )
    questions = payload["semantic_events"]["question_events"]
    candidates = [
        item
        for item in payload["semantic_candidate_ledger"]["candidates"]
        if item["family"] == "question_events"
    ]

    assert len(questions) == 2
    assert {item["candidate_state"] for item in questions} == {
        "ambiguous_competing_read"
    }
    assert {item["terminal_state"] for item in candidates} == {
        "ambiguous_competing_read"
    }
    assert payload["semantic_candidate_ledger"]["metrics"][
        "ambiguous_candidate_count"
    ] == 2


def test_invalid_specialist_proposals_receive_terminal_records(
    tmp_path: Path,
) -> None:
    class MixedValidityBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "LIVE CONSTRAINTS" in system_prompt:
                return {
                    "live_constraints": [
                        {
                            "mode": "span",
                            "kind": "constraint",
                            "text": "They have not signed anything",
                            "turn_index": 3,
                        },
                        {
                            "mode": "span",
                            "kind": "constraint",
                            "text": "Fabricated constraint quote",
                            "turn_index": 3,
                        },
                    ]
                }
            if "STANCE EVENT" in system_prompt:
                return {
                    "stance_events": [
                        {
                            "relation": "commitment",
                            "text": (
                                "I would announce a limited public beta and make "
                                "this prospect the flagship design partner."
                            ),
                            "turn_index": 2,
                        },
                        {
                            "relation": "not_a_relation",
                            "text": "Yes.",
                            "turn_index": 2,
                        },
                    ]
                }
            if "DROPPED THREADS" in system_prompt:
                return {
                    "dropped_threads": [
                        {
                            "text": (
                                "the board is excited mainly because of the "
                                "company's name"
                            ),
                            "turn_index": 3,
                            "speaker": "user",
                            "kind": "open_loop",
                        },
                        {
                            "text": "They have not signed anything.",
                            "turn_index": 3,
                            "speaker": "system",
                            "kind": "open_loop",
                        },
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=MixedValidityBoundary(),
    )
    records = payload["semantic_candidate_ledger"]["candidates"]
    by_family = {
        family: [record for record in records if record["family"] == family]
        for family in (
            "live_constraint_events",
            "assistant_stance_events",
            "dropped_thread_events",
        )
    }

    assert {family: len(items) for family, items in by_family.items()} == {
        "live_constraint_events": 2,
        "assistant_stance_events": 2,
        "dropped_thread_events": 2,
    }
    assert [item["terminal_state"] for item in by_family["live_constraint_events"]] == [
        "selected_for_current_view",
        "not_supported_by_source",
    ]
    assert [item["terminal_state"] for item in by_family["assistant_stance_events"]] == [
        "selected_for_current_view",
        "invalid_evidence",
    ]
    assert [item["terminal_state"] for item in by_family["dropped_thread_events"]] == [
        "selected_for_current_view",
        "invalid_evidence",
    ]
    assert all(item["terminal_reason"] for items in by_family.values() for item in items)


def test_reader_set_aside_candidate_is_preserved_but_not_selected(
    tmp_path: Path,
) -> None:
    class SetAsideBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "LIVE CONSTRAINTS" in system_prompt:
                return {
                    "live_constraints": [
                        {
                            "mode": "span",
                            "kind": "constraint",
                            "text": "They have not signed anything",
                            "turn_index": 3,
                            "candidate_disposition": "set_aside_semantically",
                            "disposition_reason": (
                                "The reader considered this source-grounded item "
                                "but did not include it in its current view."
                            ),
                        }
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=SetAsideBoundary(),
    )
    candidates = [
        item
        for item in payload["semantic_candidate_ledger"]["candidates"]
        if item["family"] == "live_constraint_events"
    ]

    assert payload["semantic_events"]["live_constraint_events"] == []
    assert len(candidates) == 1
    assert candidates[0]["terminal_state"] == "set_aside_semantically"
    assert candidates[0]["current_view_eligible"] is False
    assert [item["state"] for item in candidates[0]["state_history"]] == [
        "proposed",
        "validated",
        "set_aside_semantically",
    ]
    assert candidates[0]["state_history"][-1]["actor"] == "semantic_reader"


def test_unhandled_non_object_proposal_is_backfilled_without_disappearing(
    tmp_path: Path,
) -> None:
    class NonObjectProposalBoundary(FakeBoundary):
        def run_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
            if "LIVE CONSTRAINTS" in system_prompt:
                return {
                    "live_constraints": [
                        "not an object",
                        {
                            "mode": "span",
                            "kind": "constraint",
                            "text": "They have not signed anything",
                            "turn_index": 3,
                        },
                    ]
                }
            return super().run_json(system_prompt, user_prompt)

    payload = build_core_semantic_shadow(
        context=_context(tmp_path),
        boundary=NonObjectProposalBoundary(),
    )
    candidates = [
        item
        for item in payload["semantic_candidate_ledger"]["candidates"]
        if item["family"] == "live_constraint_events"
    ]

    assert len(candidates) == 2
    assert any(item["raw_proposal"] == "not an object" for item in candidates)
    assert {item["terminal_state"] for item in candidates} == {
        "invalid_evidence",
        "selected_for_current_view",
    }
    assert payload["semantic_candidate_ledger"]["metrics"][
        "candidate_custody_complete"
    ] is True
