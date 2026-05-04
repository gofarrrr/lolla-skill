"""Offline tests for the stakeholder-assumption check spike.

These tests deliberately avoid running the full /lolla skill loop or any live
LLM calls. They exercise the public harness functions against minimized
archived-run-shaped artifacts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.spikes.stakeholder_assumption_check import (
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
