"""Offline tests for the stakeholder-assumption check spike.

These tests deliberately avoid running the full /lolla skill loop or any live
LLM calls. They exercise the public harness functions against minimized
archived-run-shaped artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.stakeholder_assumption_check import (
    evaluate_trigger,
    gate_surface,
    load_annotation,
    run_stakeholder_assumption_check,
    score_check,
)


SPIKE_DIR = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "spikes"
    / "tom-evidence-study-2026-04-29"
)
ANNOTATION_DIR = SPIKE_DIR / "02-annotations"


def _result_with_gap(dimension_id: str, question: str) -> dict:
    return {
        "structural_coverage_card": {
            "dimensions": [
                {
                    "dimension_id": dimension_id,
                    "covered": False,
                    "gap_questions": [{"question": question}],
                }
            ]
        },
        "frame_pressure_card": {"reframings": []},
        "delta_card": {"findings": []},
        "companion_cheat_sheet": {"anchors": []},
    }


def test_named_third_parties_do_not_trigger_without_plan_dependency() -> None:
    extraction = {
        "decision_situation": "Founder choosing between two product metrics; Alice and Ben are background examples.",
        "live_constraints": ["deadline this month", "dashboard already built"],
        "synthesized_position": "Use retention as the primary metric and review revenue weekly.",
        "dropped_threads": [],
    }
    result = {
        "structural_coverage_card": {
            "dimensions": [
                {"dimension_id": "information-quality", "covered": True, "gap_questions": []}
            ]
        }
    }

    decision = evaluate_trigger(extraction=extraction, result=result)

    assert decision["triggered"] is False
    assert decision["skip_reason"] == "no material stakeholder dependency detected"
    assert decision["candidate_actors"] == []


def test_stakeholder_alignment_gap_triggers_with_concrete_reason() -> None:
    extraction = {
        "decision_situation": "Mother deciding how to handle daughter, ex-husband, and therapist.",
        "live_constraints": ["ex has 50% custody", "daughter may shut down"],
        "synthesized_position": "Tell the ex the facts and ask him not to minimize the situation.",
        "dropped_threads": [],
    }
    result = _result_with_gap(
        "stakeholder-alignment",
        "What does the ex know, and what could he do with the evidence after receiving it?",
    )

    decision = evaluate_trigger(extraction=extraction, result=result)

    assert decision["triggered"] is True
    assert "stakeholder-alignment" in decision["trigger_reason"]
    assert "ex" in decision["candidate_actors"]


def test_phd_advisor_terms_trigger_material_stakeholder_check() -> None:
    extraction = {
        "decision_situation": "Third-year PhD choosing dissertation direction.",
        "live_constraints": [
            "advisor retiring in 2-3 years",
            "Dr. Silva collaboration would carry the data access risk",
        ],
        "synthesized_position": (
            "Advisor conversation next week for buy-in on direction, funding, "
            "and co-advising, then Dr. Silva outreach with a specific proposal "
            "if greenlit."
        ),
        "dropped_threads": [],
    }
    result = _result_with_gap(
        "incentive-alignment",
        "What would make the advisor actively support the co-advising handoff?",
    )

    decision = evaluate_trigger(extraction=extraction, result=result)

    assert decision["triggered"] is True
    assert "incentive-alignment" in decision["trigger_reason"]
    assert "advisor" in decision["candidate_actors"]


def test_short_actor_aliases_do_not_match_inside_words() -> None:
    extraction = {
        "decision_situation": "Next existing pipeline choice for the advisor.",
        "live_constraints": ["advisor retiring soon"],
        "synthesized_position": "Ask the advisor for support before committing.",
        "dropped_threads": [],
    }
    result = _result_with_gap(
        "stakeholder-alignment",
        "Who can support or block the plan?",
    )

    decision = evaluate_trigger(extraction=extraction, result=result)

    assert decision["triggered"] is True
    assert "advisor" in decision["candidate_actors"]
    assert "ex" not in decision["candidate_actors"]


def test_material_gap_with_dependency_triggers_even_when_actor_name_is_unusual() -> None:
    extraction = {
        "decision_situation": "Team deciding whether to ask the archive custodian for access.",
        "live_constraints": ["access depends on an unnamed archive custodian"],
        "synthesized_position": "Ask for access before committing the research plan.",
        "dropped_threads": [],
    }
    result = _result_with_gap(
        "stakeholder-alignment",
        "Who can approve or block access?",
    )

    decision = evaluate_trigger(extraction=extraction, result=result)

    assert decision["triggered"] is True
    assert decision["candidate_actors"] == ["actor_from_structural_gap"]


def test_surface_requires_concrete_plan_change() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "ex-husband",
                "advice_assumption": "He will use the evidence constructively.",
                "grounding": "plausible",
                "risk_if_wrong": "He reframes it as overreaction.",
                "plan_change": "",
            }
        ],
    }

    gated = gate_surface(raw_check)

    assert gated["surface"] is False
    assert gated["surface_reason"] == "no surfaced actor has a concrete plan_change"


def test_speculative_assumptions_cannot_surface() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "retiring advisor",
                "advice_assumption": "He secretly wants legacy continuity.",
                "grounding": "speculative",
                "risk_if_wrong": "Advisor conversation opens with the wrong premise.",
                "plan_change": "Ask what sponsorship structure he can actually support.",
            }
        ],
    }

    gated = gate_surface(raw_check)

    assert gated["surface"] is False
    assert gated["surface_reason"] == "all surfaced assumptions are speculative"
    assert gated["chat_actors"] == []
    assert gated["critical_actors"][0]["surface_in_chat"] is False


def test_speculative_actor_does_not_ride_along_with_surface_payload() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "general counsel",
                "advice_assumption": "GC can create a protected internal record.",
                "grounding": "plausible",
                "risk_if_wrong": "Internal disclosure becomes a warning shot.",
                "plan_change": "Have counsel test formal internal disclosure before filing externally.",
            },
            {
                "display_name": "wife",
                "advice_assumption": "She will support a high-level disclosure tonight.",
                "grounding": "speculative",
                "risk_if_wrong": "The financial plan is not actually shared.",
                "plan_change": "Make tonight's talk a joint go/no-go on financial terms.",
            },
        ],
    }

    gated = gate_surface(raw_check)

    assert gated["surface"] is True
    assert [a["display_name"] for a in gated["chat_actors"]] == ["general counsel"]
    assert gated["critical_actors"][0]["surface_in_chat"] is True
    assert gated["critical_actors"][1]["surface_in_chat"] is False
    assert gated["critical_actors"][1]["surface_block_reason"] == "speculative"


def test_role_closeness_future_behavior_stays_out_of_chat() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "wife",
                "advice_assumption": "Wife will accept high-level disclosure and support lawyer calls.",
                "grounding": "plausible",
                "grounding_source": "role_closeness",
                "known_to_actor": ["family financial stakes"],
                "unsafe_inferences": ["wife's risk tolerance matches user's"],
                "risk_if_wrong": "The plan is not jointly viable.",
                "plan_change": "Make tonight a joint financial go/no-go conversation.",
            }
        ],
    }

    gated = gate_surface(raw_check)

    assert gated["surface"] is False
    assert gated["chat_actors"] == []
    assert gated["critical_actors"][0]["surface_in_chat"] is False
    assert gated["critical_actors"][0]["surface_block_reason"] == "role_closeness_open_question"


def test_role_closeness_knowledge_is_downgraded_to_plausible() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "Lina",
                "advice_assumption": "Lina knows Marcus's exact equity ask.",
                "grounding": "grounded",
                "grounding_source": "role_closeness",
                "risk_if_wrong": "Founder overestimates how much the engineering team understands.",
                "plan_change": "Treat team knowledge as unverified and avoid naming Lina as aligned.",
            }
        ],
    }

    gated = gate_surface(raw_check)
    actor = gated["critical_actors"][0]

    assert actor["grounding"] == "plausible"
    assert actor["grounding_note"] == "role/closeness inference downgraded from grounded"
    assert gated["surface"] is True


def test_grounded_likely_access_claim_is_downgraded_without_metadata() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "14-year-old daughter",
                "advice_assumption": "Low-stakes routine will re-open communication without pushback.",
                "grounding": "grounded",
                "known_to_actor": [],
                "bridging_facts": [
                    "Likely access inferred from role closeness and family relationship."
                ],
                "risk_if_wrong": "The repair plan is too slow for the current risk.",
                "plan_change": "Treat routine repair as a test, not proof, and add tripwires.",
            }
        ],
    }

    gated = gate_surface(raw_check)
    actor = gated["critical_actors"][0]

    assert actor["grounding"] == "plausible"
    assert actor["grounding_note"] == "role/closeness inference downgraded from grounded"
    assert gated["surface"] is True


def test_grounded_future_behavior_claim_is_downgraded_to_plausible() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "14-year-old daughter",
                "advice_assumption": "Daughter will thaw via low-stakes routine without pushback.",
                "grounding": "grounded",
                "grounding_source": "transcript_fact",
                "known_to_actor": [
                    "confrontation led to 3-day shutdown",
                    "recent dinner appearance and nod as progress",
                ],
                "bridging_facts": ["shutdown and nod are transcript facts"],
                "risk_if_wrong": "The repair plan is too slow for the current risk.",
                "plan_change": "Replace time-based triggers with behavioral ones.",
            }
        ],
    }

    gated = gate_surface(raw_check)
    actor = gated["critical_actors"][0]

    assert actor["grounding"] == "plausible"
    assert actor["grounding_note"] == "behavior prediction downgraded from grounded"
    assert gated["surface"] is True


def test_duplicate_plan_change_stays_in_panel_but_not_chat() -> None:
    raw_check = {
        "status": "completed",
        "triggered": True,
        "surface": True,
        "critical_actors": [
            {
                "display_name": "wife",
                "advice_assumption": "She needs to be included in the financial decision.",
                "grounding": "plausible",
                "risk_if_wrong": "Negotiation plan ignores the household constraint.",
                "plan_change": (
                    "Ask your wife directly how she is holding the financial picture "
                    "before negotiating or signing."
                ),
            }
        ],
    }

    gated = gate_surface(
        raw_check,
        existing_plan_texts=[
            "Ask your wife how she's holding it before you decide whether to negotiate."
        ],
    )

    assert gated["surface"] is False
    assert gated["chat_actors"] == []
    assert gated["critical_actors"][0]["surface_in_chat"] is False
    assert gated["critical_actors"][0]["surface_block_reason"] == "duplicate_existing_advice"


def test_annotation_scoring_distinguishes_new_correction_from_duplicate() -> None:
    annotation = load_annotation(ANNOTATION_DIR / "mother-ex-evidence-boundary.json")
    trigger = {"triggered": True, "candidate_actors": ["ex"]}
    check = {
        "status": "completed",
        "surface": True,
        "critical_actors": [
            {
                "display_name": "ex-husband",
                "advice_assumption": annotation["expected"]["advice_assumption"],
                "grounding": "plausible",
                "risk_if_wrong": annotation["expected"]["risk_if_wrong"],
                "plan_change": annotation["expected"]["plan_change"],
            }
        ],
    }

    score = score_check(annotation=annotation, trigger=trigger, check=gate_surface(check))

    assert score["trigger_match"] is True
    assert score["actor_match"] is True
    assert score["plan_change_match"] is True
    assert score["non_duplicative"] is True
    assert score["speculative_surface_violation"] is False


def test_annotation_pack_has_positive_and_negative_controls() -> None:
    annotations = [
        json.loads(path.read_text())
        for path in ANNOTATION_DIR.glob("*.json")
        if path.name != "schema.json"
    ]

    assert len(annotations) >= 4
    assert any(a["control"] == "negative" for a in annotations)
    positives = [a for a in annotations if a["control"] == "positive"]
    assert positives
    for annotation in positives:
        expected = annotation["expected"]
        assert expected["triggered"] is True
        assert expected["actor"]
        assert expected["advice_assumption"]
        assert expected["plan_change"]


def test_triggered_runtime_check_calls_boundary_and_gates_payload() -> None:
    class _FakeBoundary:
        def __init__(self) -> None:
            self.call_log = [
                {
                    "stage": "stakeholder_assumption_check",
                    "provider_name": "openrouter",
                    "model": "fake-model",
                    "status": "ok",
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                }
            ]
            self.user_prompt = ""

        def run_json(self, system_prompt: str, user_prompt: str, **kwargs) -> dict:
            assert "psychology profile" in system_prompt
            assert kwargs["stage"] == "stakeholder_assumption_check"
            self.user_prompt = user_prompt
            return {
                "status": "completed",
                "surface": True,
                "summary": "Do not forward screenshots.",
                "critical_actors": [
                    {
                        "display_name": "ex-husband",
                        "advice_assumption": "He will use evidence constructively.",
                        "grounding": "plausible",
                        "risk_if_wrong": "He weaponizes it.",
                        "plan_change": "Share general facts, not screenshots.",
                    }
                ],
            }

    extraction = {
        "decision_situation": "Mother deciding how to handle ex-husband.",
        "live_constraints": ["ex has 50% custody"],
        "synthesized_position": "Tell the ex the facts.",
        "dropped_threads": [],
    }
    result = _result_with_gap(
        "stakeholder-alignment",
        "What can the ex do with the evidence after receiving it?",
    )
    boundary = _FakeBoundary()

    payload, call_log = run_stakeholder_assumption_check(
        extraction=extraction,
        result=result,
        conversation_text="[Turn 1] USER: ex has 50% custody",
        boundary=boundary,
    )

    assert payload["status"] == "completed"
    assert payload["surface"] is True
    assert payload["surface_reason"] == "plan-changing grounded-or-plausible assumption"
    assert payload["triggered"] is True
    assert "stakeholder-alignment" in payload["trigger_reason"]
    assert call_log == boundary.call_log
    assert "conversation_excerpt" in boundary.user_prompt


def test_runtime_suppresses_duplicate_against_synthesized_position() -> None:
    class _FakeBoundary:
        call_log: list = []

        def run_json(self, system_prompt: str, user_prompt: str, **kwargs) -> dict:
            return {
                "status": "completed",
                "surface": True,
                "summary": "Ask wife directly.",
                "critical_actors": [
                    {
                        "display_name": "wife",
                        "advice_assumption": "She needs to be included in the financial decision.",
                        "grounding": "plausible",
                        "risk_if_wrong": "The plan ignores the household constraint.",
                        "plan_change": (
                            "Ask wife explicitly: 'How are you holding the $20K "
                            "take-home drop and 7-month runway with your partial leave?' "
                            "before accepting."
                        ),
                    }
                ],
            }

    extraction = {
        "decision_situation": "Senior PM deciding whether to accept a Director offer.",
        "live_constraints": ["wife on partial leave", "7 months runway"],
        "synthesized_position": (
            "Take the Director offer. Verify the title and ask wife how she's "
            "holding the financial picture. Negotiate signing bonus."
        ),
        "dropped_threads": [],
    }
    result = _result_with_gap(
        "stakeholder-alignment",
        "Has the user actually asked the wife, or only inferred her stance?",
    )

    payload, _ = run_stakeholder_assumption_check(
        extraction=extraction,
        result=result,
        conversation_text="[Turn 1] USER: wife on partial leave",
        boundary=_FakeBoundary(),
    )

    assert payload["surface"] is False
    assert payload["chat_actors"] == []
    assert payload["critical_actors"][0]["surface_block_reason"] == "duplicate_existing_advice"


def test_triggered_runtime_check_without_boundary_is_visible_error() -> None:
    extraction = {
        "decision_situation": "Mother deciding how to handle ex-husband.",
        "live_constraints": ["ex has 50% custody"],
        "synthesized_position": "Tell the ex the facts.",
        "dropped_threads": [],
    }
    result = _result_with_gap(
        "stakeholder-alignment",
        "What can the ex do with the evidence after receiving it?",
    )

    payload, call_log = run_stakeholder_assumption_check(
        extraction=extraction,
        result=result,
        boundary=None,
    )

    assert payload["status"] == "skipped_error"
    assert payload["triggered"] is True
    assert payload["surface"] is False
    assert "boundary client required" in payload["error"]
    assert call_log == []
