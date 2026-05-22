from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_consultant_anchor_boundary_patch_probe import (  # noqa: E402
    build_consultant_anchor_boundary_patch_probe_contract,
    build_consultant_anchor_boundary_patch_probe_prompts,
    build_consultant_anchor_boundary_patch_probe_result,
    build_static_consultant_anchor_boundary_patch_probe_sample,
    validate_consultant_anchor_boundary_patch_probe_contract,
    validate_consultant_anchor_boundary_patch_probe_result,
    validate_consultant_anchor_boundary_patch_probe_sample,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_anchor_boundary_patch_contract_is_hypothesis_test_not_architecture() -> None:
    contract = build_consultant_anchor_boundary_patch_probe_contract(root=REPO_ROOT)

    validate_consultant_anchor_boundary_patch_probe_contract(contract, root=REPO_ROOT)

    assert (
        contract["schema_version"]
        == "pre_step6_consultant_anchor_boundary_patch_probe_contract.v1"
    )
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["case_id"] == "mid-level-consultant-report-2"
    assert contract["patch"]["patch_phrase"] == (
        "keep the first moves reversible until counsel guides the next action"
    )
    assert contract["patch"]["placement"] == "hypothesis_test_not_architecture"
    assert contract["sample_plan"] == {
        "step6_model": "moonshotai/kimi-k2.6",
        "sample_count": 6,
        "max_wording_reruns_on_unobserved": 1,
        "success_read": (
            "Test whether the recurring reversibility-until-counsel pressure is "
            "carried by the patched anchor so the same micro-card can stand down."
        ),
    }
    assert contract["preflight_checklist"] == [
        "makes_step6_table_better",
        "preserves_broad_private_edge",
        "keeps_cognition_in_step6_or_human_review",
        "avoids_automatic_wisdom_from_recurrence",
        "learns_upstream_rather_than_suppressing_context",
    ]
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_anchor_boundary_patch_prompt_is_minimal_and_keeps_same_micro_cards() -> None:
    contract = build_consultant_anchor_boundary_patch_probe_contract(root=REPO_ROOT)

    prompts = build_consultant_anchor_boundary_patch_probe_prompts(
        contract=contract,
        sample_index=0,
    )

    assert "You are Step 6" in prompts["system_prompt"]
    assert "patched_anchor_visible_candidate" in prompts["user_prompt"]
    assert "keep the first moves reversible until counsel guides the next action" in prompts[
        "user_prompt"
    ]
    assert "cleaning_micro_cards" in prompts["user_prompt"]
    assert "counsel_independence_and_channel_bias_card" in prompts["user_prompt"]
    assert "wednesday_tripwire_preservation_card" in prompts["user_prompt"]
    assert "reversibility_until_counsel_boundary_card" in prompts["user_prompt"]
    assert "private_micro_card_ledger" in prompts["user_prompt"]
    assert "hypothesis test, not a patch architecture" in prompts["user_prompt"]
    assert "Bevelin" not in prompts["user_prompt"]
    assert "Polya" not in prompts["user_prompt"]


def test_static_patch_probe_result_classifies_upstream_pressure_carried() -> None:
    contract = build_consultant_anchor_boundary_patch_probe_contract(root=REPO_ROOT)
    samples = [
        build_static_consultant_anchor_boundary_patch_probe_sample(
            contract=contract,
            sample_index=0,
            micro_card_signal="all_private_or_confirming",
            reversibility_card_additive=False,
            patched_boundary_in_answer=True,
        ),
        build_static_consultant_anchor_boundary_patch_probe_sample(
            contract=contract,
            sample_index=1,
            micro_card_signal="all_private_or_confirming",
            reversibility_card_additive=False,
            patched_boundary_in_answer=True,
        ),
        build_static_consultant_anchor_boundary_patch_probe_sample(
            contract=contract,
            sample_index=2,
            micro_card_signal="all_private_or_confirming",
            reversibility_card_additive=False,
            patched_boundary_in_answer=True,
        ),
    ]

    for sample in samples:
        validate_consultant_anchor_boundary_patch_probe_sample(sample)

    result = build_consultant_anchor_boundary_patch_probe_result(
        contract=contract,
        samples=samples,
    )

    validate_consultant_anchor_boundary_patch_probe_result(result)

    assert result["aggregate"]["sample_count"] == 3
    assert result["aggregate"]["upstream_pressure_carried"] == "yes"
    assert result["aggregate"]["micro_card_standdown_rate"] == 1.0
    assert result["aggregate"]["reversibility_card_additive_rate"] == 0.0
    assert result["aggregate"]["protected_payload_preserved"] is True
    assert result["aggregate"]["next_investigation"] == "synthesis"
    assert result["aggregate"]["consultant_classification"] == "graduation_candidate"
    assert result["aggregate"]["runtime_promotion"] == "blocked"
    assert result["aggregate"]["skill_update"] == "blocked"
