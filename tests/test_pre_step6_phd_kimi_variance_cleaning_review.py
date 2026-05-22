from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_phd_kimi_variance_cleaning_review import (  # noqa: E402
    build_phd_kimi_variance_cleaning_review_contract,
    build_phd_kimi_variance_cleaning_review_prompts,
    build_phd_kimi_variance_cleaning_review_result,
    build_static_phd_kimi_variance_cleaning_review_sample,
    validate_phd_kimi_variance_cleaning_review_contract,
    validate_phd_kimi_variance_cleaning_review_result,
    validate_phd_kimi_variance_cleaning_review_sample,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_phd_cleaning_review_contract_is_single_case_and_runtime_dormant() -> None:
    contract = build_phd_kimi_variance_cleaning_review_contract(root=REPO_ROOT)

    validate_phd_kimi_variance_cleaning_review_contract(contract, root=REPO_ROOT)

    assert contract["schema_version"] == "pre_step6_phd_kimi_variance_cleaning_review.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["case_id"] == "third-year-phd-student.v2.v60-off"
    assert contract["scope"] == {
        "primary_question": (
            "Does atomic decomposition explain Kimi's PhD variance without "
            "adding a gate or changing model family?"
        ),
        "v60_mode": "off",
        "reason": "Avoid conflating atomic-deck discrimination with V60 effects.",
    }
    assert contract["sample_plan"]["step6_model"] == "moonshotai/kimi-k2.6"
    assert contract["sample_plan"]["sample_count"] == 6
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_phd_cleaning_prompt_passes_atomic_cards_without_lens_labels() -> None:
    contract = build_phd_kimi_variance_cleaning_review_contract(root=REPO_ROOT)

    prompts = build_phd_kimi_variance_cleaning_review_prompts(
        contract=contract,
        sample_index=0,
    )

    assert "You are Step 6" in prompts["system_prompt"]
    assert "phd_cleaning_micro_cards" in prompts["user_prompt"]
    assert "bounded_probe_not_commitment_card" in prompts["user_prompt"]
    assert "single_cell_collaborator_feasibility_card" in prompts["user_prompt"]
    assert "fallback_reentry_readiness_card" in prompts["user_prompt"]
    assert "visible_stop_date_conditions_card" in prompts["user_prompt"]
    assert "short, low-cost test" in prompts["user_prompt"]
    assert "single-cell gaps" in prompts["user_prompt"]
    assert "ready for you to re-enter" in prompts["user_prompt"]
    assert "clear stop date with visible conditions" in prompts["user_prompt"]
    assert "Bevelin" not in prompts["user_prompt"]
    assert "Polya" not in prompts["user_prompt"]


def test_static_phd_cleaning_result_counts_atomic_card_discrimination() -> None:
    contract = build_phd_kimi_variance_cleaning_review_contract(root=REPO_ROOT)
    samples = [
        build_static_phd_kimi_variance_cleaning_review_sample(
            contract=contract,
            sample_index=0,
            additive_cards=[
                "single_cell_collaborator_feasibility_card",
                "visible_stop_date_conditions_card",
            ],
        ),
        build_static_phd_kimi_variance_cleaning_review_sample(
            contract=contract,
            sample_index=1,
            additive_cards=[],
        ),
        build_static_phd_kimi_variance_cleaning_review_sample(
            contract=contract,
            sample_index=2,
            additive_cards=["visible_stop_date_conditions_card"],
        ),
    ]

    for sample in samples:
        validate_phd_kimi_variance_cleaning_review_sample(sample)

    result = build_phd_kimi_variance_cleaning_review_result(
        contract=contract,
        samples=samples,
    )

    validate_phd_kimi_variance_cleaning_review_result(result)

    assert result["aggregate"]["sample_count"] == 3
    assert result["aggregate"]["micro_card_additive_count"] == 2
    assert result["aggregate"]["all_private_or_confirming_count"] == 1
    assert result["aggregate"]["card_additive_counts"] == {
        "bounded_probe_not_commitment_card": 0,
        "single_cell_collaborator_feasibility_card": 1,
        "fallback_reentry_readiness_card": 0,
        "visible_stop_date_conditions_card": 2,
    }
    assert result["aggregate"]["atomic_discrimination_read"] == "discriminated"
    assert result["aggregate"]["runtime_promotion"] == "blocked"
    assert result["aggregate"]["skill_update"] == "blocked"


def test_static_phd_cleaning_result_treats_cross_sample_card_spread_as_discrimination() -> None:
    contract = build_phd_kimi_variance_cleaning_review_contract(root=REPO_ROOT)
    samples = [
        build_static_phd_kimi_variance_cleaning_review_sample(
            contract=contract,
            sample_index=0,
            additive_cards=[
                "bounded_probe_not_commitment_card",
                "visible_stop_date_conditions_card",
            ],
        ),
        build_static_phd_kimi_variance_cleaning_review_sample(
            contract=contract,
            sample_index=1,
            additive_cards=[
                "single_cell_collaborator_feasibility_card",
                "fallback_reentry_readiness_card",
            ],
        ),
    ]

    result = build_phd_kimi_variance_cleaning_review_result(
        contract=contract,
        samples=samples,
    )

    assert result["aggregate"]["card_additive_counts"] == {
        "bounded_probe_not_commitment_card": 1,
        "single_cell_collaborator_feasibility_card": 1,
        "fallback_reentry_readiness_card": 1,
        "visible_stop_date_conditions_card": 1,
    }
    assert result["aggregate"]["atomic_discrimination_read"] == "discriminated"
