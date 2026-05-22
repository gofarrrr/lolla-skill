from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_consultant_cleaning_variant_replay import (  # noqa: E402
    build_consultant_cleaning_variant_replay_contract,
    build_consultant_cleaning_variant_replay_prompts,
    build_consultant_cleaning_variant_replay_result,
    build_static_consultant_cleaning_variant_replay_sample,
    validate_consultant_cleaning_variant_replay_contract,
    validate_consultant_cleaning_variant_replay_result,
    validate_consultant_cleaning_variant_replay_sample,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cleaning_variant_replay_contract_is_research_only_and_variant_scoped() -> None:
    contract = build_consultant_cleaning_variant_replay_contract(root=REPO_ROOT)

    validate_consultant_cleaning_variant_replay_contract(contract, root=REPO_ROOT)

    assert (
        contract["schema_version"]
        == "pre_step6_consultant_cleaning_variant_replay_contract.v1"
    )
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["case_id"] == "mid-level-consultant-report-2"
    assert contract["sample_plan"] == {
        "step6_model": "moonshotai/kimi-k2.6",
        "sample_count": 6,
        "success_read": (
            "Compare consideration stability and protected payload preservation "
            "against the old Consultant deck; not a visibility-promotion gate."
        ),
    }
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_cleaning_variant_replay_prompt_passes_micro_cards_without_lens_labels() -> None:
    contract = build_consultant_cleaning_variant_replay_contract(root=REPO_ROOT)

    prompts = build_consultant_cleaning_variant_replay_prompts(
        contract=contract,
        sample_index=0,
    )

    assert "You are Step 6" in prompts["system_prompt"]
    assert "cleaning_micro_cards" in prompts["user_prompt"]
    assert "counsel_independence_and_channel_bias_card" in prompts["user_prompt"]
    assert "wednesday_tripwire_preservation_card" in prompts["user_prompt"]
    assert "reversibility_until_counsel_boundary_card" in prompts["user_prompt"]
    assert "private_micro_card_ledger" in prompts["user_prompt"]
    assert "built-in bias" in prompts["user_prompt"]
    assert "do not deny" in prompts["user_prompt"]
    assert "until counsel guides" in prompts["user_prompt"]
    assert "Bevelin" not in prompts["user_prompt"]
    assert "Polya" not in prompts["user_prompt"]


def test_static_cleaning_variant_replay_result_measures_consideration_stability() -> None:
    contract = build_consultant_cleaning_variant_replay_contract(root=REPO_ROOT)
    samples = [
        build_static_consultant_cleaning_variant_replay_sample(
            contract=contract,
            sample_index=0,
            micro_card_signal="micro_card_additive_present",
            answer_delta_specificity="concrete_delta_present",
        ),
        build_static_consultant_cleaning_variant_replay_sample(
            contract=contract,
            sample_index=1,
            micro_card_signal="micro_card_additive_present",
            answer_delta_specificity="concrete_delta_present",
        ),
        build_static_consultant_cleaning_variant_replay_sample(
            contract=contract,
            sample_index=2,
            micro_card_signal="all_private_or_confirming",
            answer_delta_specificity="not_applicable",
        ),
    ]

    for sample in samples:
        validate_consultant_cleaning_variant_replay_sample(sample)

    result = build_consultant_cleaning_variant_replay_result(
        contract=contract,
        samples=samples,
    )

    validate_consultant_cleaning_variant_replay_result(result)

    assert result["aggregate"]["sample_count"] == 3
    assert result["aggregate"]["micro_card_additive_count"] == 2
    assert result["aggregate"]["consideration_stability_read"] == "mixed"
    assert result["aggregate"]["old_kimi_unlock_ratio"] == 0.5
    assert result["aggregate"]["runtime_promotion"] == "blocked"
    assert result["aggregate"]["skill_update"] == "blocked"
