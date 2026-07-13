from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.system_b.r3_google_schema_projection import (
    lint_google_documented_schema_subset,
)
from engine.system_b.r3_task_shape_counterfactual import (
    R3TaskShapeError,
    compile_collapsed_one_pass_response,
)
from scripts.evals import build_r3_collapsed_outcome_case_selection as selection


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/selection"
)


def _response(packet: dict) -> dict:
    outcomes = ["apply_new_condition", "reject", "park"]
    rows = []
    for index, item in enumerate(
        packet["constitutional_graph_survival"]["active_pressure_items"]
    ):
        outcome = outcomes[index] if index < len(outcomes) else "reject"
        rows.append(
            {
                "pressure_id": item["pressure_id"],
                "outcome": outcome,
                "source_turn_numbers": [1],
                "strongest_plausible_application": (
                    "Test the strongest source-grounded application."
                ),
                "attempted_application_condition": (
                    "The supplied conversation must establish the mechanism."
                ),
                "why": "Provider-free fixture judgment with exact source custody.",
                "disposition_boundary": (
                    "Reopen or falsify when the stated condition changes."
                ),
                "visible_effect": (
                    "Add one bounded condition."
                    if outcome.startswith("apply_")
                    else ""
                ),
                "private_guardrail": "",
            }
        )
    return {
        "candidate_dispositions": rows,
        "reconsidered_answer": "Preserve the recommendation with one condition.",
        "change_summary": "One condition added; other pressure stood down.",
        "original_answer_preservation": "preserved",
    }


def test_source_and_selection_freezes_precede_expected_targets() -> None:
    source_freeze = json.loads(selection.SOURCE_FREEZE.read_text(encoding="utf-8"))
    direct = json.loads(selection.SELECTION.read_text(encoding="utf-8"))

    assert source_freeze["status"] == (
        "source_frozen_provider_free_before_targets_or_pressure_selection"
    )
    assert source_freeze["source"]["message_count"] == 28
    assert source_freeze["source"]["word_count"] == 2468
    assert source_freeze["freeze_boundary"][
        "protected_reasoning_targets_authored_before_freeze"
    ] is False
    assert direct["status"] == (
        "direct_patterns_frozen_before_expected_dispositions"
    )
    assert direct["freeze_boundary"]["expected_candidate_dispositions_authored"] is False
    assert direct["freeze_boundary"]["source_review_target_authored"] is False
    assert direct["semantic_owner"]["deterministic_code_inferred_meaning"] is False


def test_checked_in_selection_reconstructs_exact_nine_item_request() -> None:
    summary = selection.validate(OUTPUT)
    material = selection.construct(include_runtime=True)["_runtime_material"]
    packet = material["packet"]
    request = material["request_body"]
    active = packet["constitutional_graph_survival"]["active_pressure_items"]

    assert summary["direct_model_ids"] == [
        "path-dependence",
        "incentives",
        "optionality",
        "principal-agent-problem",
        "feedback-loops",
        "commitment-bias",
    ]
    assert summary["graph_model_ids"] == [
        "confirmation-bias",
        "scientific-method-evidence-testing",
        "cognitive-dissonance",
    ]
    assert len(active) == 9
    assert summary["fan_in_measurement"]["active_within_frozen_bound"] is True
    assert summary["fan_in_measurement"]["reserve_within_frozen_bound"] is True
    assert request["model"] == "google/gemini-3.1-flash-lite"
    assert request["provider"]["order"] == ["google-vertex/global"]
    assert request["provider"]["allow_fallbacks"] is False
    assert request["provider"]["require_parameters"] is True
    assert material["request_metrics"]["maximum_estimated_cost_usd"] == (
        0.00836875
    )
    assert lint_google_documented_schema_subset(
        material["response_schema"]
    )["status"] == "pass_documented_subset"


def test_compact_contract_reconstructs_instead_of_copying_source() -> None:
    path = OUTPUT / selection.BUNDLE_NAME
    contract = json.loads(path.read_text(encoding="utf-8"))
    assert path.stat().st_size < 20_000
    assert "packet" not in contract
    assert "request_body" not in contract
    assert contract["reconstruction"]["provider_material_function"] == (
        "construct(include_runtime=True)"
    )
    assert contract["provider_calls_made"] == 0
    assert contract["next_call_authorized"] is False


def test_new_case_allows_apply_reject_and_park_without_semantic_repair() -> None:
    packet = selection.construct(include_runtime=True)["_runtime_material"]["packet"]
    response = _response(packet)
    compiled = compile_collapsed_one_pass_response(
        response=response,
        packet=packet,
    )

    assert compiled["all_active_candidates_accounted_for"] is True
    assert compiled["disposition_counts"] == {"apply": 1, "park": 1, "reject": 7}
    assert compiled["counterfactual_projection"][
        "semantic_applicability_inferred_by_code"
    ] is False

    response["candidate_dispositions"][1]["visible_effect"] = "Silent repair bait."
    with pytest.raises(R3TaskShapeError, match="reject claims effect custody"):
        compile_collapsed_one_pass_response(response=response, packet=packet)


def test_selection_rejects_quote_or_canonical_identity_tampering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    direct = json.loads(selection.SELECTION.read_text(encoding="utf-8"))
    direct["patterns"][0]["source_evidence"][0]["quote"] = "Invented quote."
    path = tmp_path / "selection.json"
    path.write_text(json.dumps(direct), encoding="utf-8")
    monkeypatch.setattr(selection, "SELECTION", path)
    with pytest.raises(selection.R3CollapsedSelectionError, match="source evidence drifted"):
        selection.construct()

    direct = json.loads(
        (ROOT / (
            "research/lolla-r3-collapsed-outcome-case-2026-07-13/selection/"
            "direct-pattern-selection.json"
        )).read_text(encoding="utf-8")
    )
    direct["patterns"][0]["canonical_model_id"] = "invented-model"
    path.write_text(json.dumps(direct), encoding="utf-8")
    with pytest.raises(selection.R3CollapsedSelectionError, match="identity is invalid"):
        selection.construct()
