from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_false_standdown_bridge_probe import (  # noqa: E402
    build_bridge_probe_contract,
    build_bridge_probe_result,
    build_static_reviewer_judgment,
    load_bridge_probe_contract,
    validate_bridge_probe_contract,
    validate_bridge_probe_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_probe_contract_pins_confirmed_false_standdown_and_pre_run_labels() -> None:
    contract = build_bridge_probe_contract()

    validate_bridge_probe_contract(contract)

    assert contract["schema_version"] == "pre_step6_false_standdown_bridge_probe.v1"
    assert contract["probe_id"] == "false_standdown_bridge_probe_v0"
    assert contract["status"] == "planned_non_promotional"
    assert contract["confirmation_rule"] == {
        "confirmed_false_standdown": (
            "Two reviewer judgments label the same case false_standdown under "
            "the same rubric, fresh blind shuffles, and different model families."
        ),
        "single_reviewer_false_standdown": "not_confirmed",
        "human_spot_check_only": "not_confirmed",
    }
    for case in contract["probe_cases"]:
        assert case["selection_timing"] == "pre_run"
        assert case["pre_run_failure_hypothesis"].startswith("If runtime shows the anchor")
        assert case["expected_deck_adds"]
        assert case["anchor_risk_if_hidden"]
        assert case["answer_candidates"]["anchor_visible"]
        assert case["answer_candidates"]["deck_visible"]


def test_confirmed_false_standdown_requires_two_reviewer_families() -> None:
    contract = build_bridge_probe_contract()
    case_id = "bridge-sensitive-anchor-misses-tripwire"
    reviewer_a = build_static_reviewer_judgment(
        contract=contract,
        case_id=case_id,
        model="openai/gpt-5.1-chat",
        standdown_label="false_standdown",
        winner_arm="deck_visible",
    )
    reviewer_b = build_static_reviewer_judgment(
        contract=contract,
        case_id=case_id,
        model="google/gemini-3.1-flash-lite",
        standdown_label="false_standdown",
        winner_arm="deck_visible",
    )

    result = build_bridge_probe_result(contract=contract, judgments=[reviewer_a, reviewer_b])

    validate_bridge_probe_result(result)

    assert result["case_results"] == [
        {
            "case_id": case_id,
            "reviewer_count": 2,
            "reviewer_model_families": ["google", "openai"],
            "standdown_labels": ["false_standdown", "false_standdown"],
            "confirmed_label": "false_standdown",
            "stop_condition_triggered": True,
        }
    ]
    assert result["probe_result"] == "design_review_required"
    assert result["promotion_effect"] == "none_bridge_only"


def test_single_family_double_false_is_not_confirmed() -> None:
    contract = build_bridge_probe_contract()
    case_id = "bridge-sensitive-anchor-misses-tripwire"
    reviewer_a = build_static_reviewer_judgment(
        contract=contract,
        case_id=case_id,
        model="openai/gpt-5.1-chat",
        standdown_label="false_standdown",
        winner_arm="deck_visible",
    )
    reviewer_b = build_static_reviewer_judgment(
        contract=contract,
        case_id=case_id,
        model="openai/gpt-5.2-mini",
        standdown_label="false_standdown",
        winner_arm="deck_visible",
    )

    result = build_bridge_probe_result(contract=contract, judgments=[reviewer_a, reviewer_b])

    validate_bridge_probe_result(result)

    assert result["case_results"][0]["confirmed_label"] == "ambiguous_standdown"
    assert result["case_results"][0]["stop_condition_triggered"] is False
    assert result["probe_result"] == "continue_bridge_probe"


def test_bridge_probe_contract_fixture_validates() -> None:
    path = (
        REPO_ROOT
        / "research"
        / "pre-step6-false-standdown-bridge-probe"
        / "false-standdown-bridge-probe.v1.json"
    )
    payload = load_bridge_probe_contract(path)

    validate_bridge_probe_contract(payload)

    assert len(payload["probe_cases"]) == 3
