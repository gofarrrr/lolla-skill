from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_reframe_diagnostic_review import (  # noqa: E402
    build_reframe_diagnostic_contract,
    build_reframe_diagnostic_result,
    build_reviewer_packet,
    build_static_reframe_judgment,
    validate_reframe_diagnostic_contract,
    validate_reframe_diagnostic_judgment,
    validate_reframe_diagnostic_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_reframe_diagnostic_contract_selects_saved_samples_without_runtime_promotion() -> None:
    contract = build_reframe_diagnostic_contract(root=REPO_ROOT)

    validate_reframe_diagnostic_contract(contract)

    assert contract["schema_version"] == "pre_step6_reframe_diagnostic_contract.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["question"] == (
        "Are reframe-only Step 6 outputs genuinely useful enough to challenge "
        "the answer-delta vocabulary, or correctly suppressed?"
    )
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }

    roles = {case["diagnostic_role"] for case in contract["diagnostic_cases"]}
    assert {"stable_positive_anchor", "stable_standdown_anchor", "reframe_only_diagnostic"} <= roles
    reframe_cases = [
        case
        for case in contract["diagnostic_cases"]
        if case["diagnostic_role"] == "reframe_only_diagnostic"
    ]
    assert reframe_cases
    assert all(case["answer_delta_specificity"] == "reframe_only" for case in reframe_cases)
    assert all(case["sample_ref"].startswith("research/") for case in contract["diagnostic_cases"])


def test_reviewer_packet_hides_source_arms_but_preserves_diagnostic_role() -> None:
    contract = build_reframe_diagnostic_contract(root=REPO_ROOT)
    case_id = next(
        case["diagnostic_case_id"]
        for case in contract["diagnostic_cases"]
        if case["diagnostic_role"] == "reframe_only_diagnostic"
    )

    packet = build_reviewer_packet(contract=contract, diagnostic_case_id=case_id, seed=11)

    assert packet["diagnostic_case_id"] == case_id
    assert packet["diagnostic_role"] == "reframe_only_diagnostic"
    assert set(packet["candidates_by_label"]) == {"A", "B"}
    assert "blind_map_private" in packet
    assert set(packet["blind_map_private"].values()) == {"anchor_visible", "step6_visible"}
    public_packet = dict(packet)
    public_packet.pop("blind_map_private")
    assert "anchor_visible" not in str(public_packet["candidates_by_label"])
    assert "step6_visible" not in str(public_packet["candidates_by_label"])


def test_reframe_result_requires_consistent_two_family_reviewer_signal() -> None:
    contract = build_reframe_diagnostic_contract(root=REPO_ROOT)
    case_id = next(
        case["diagnostic_case_id"]
        for case in contract["diagnostic_cases"]
        if case["diagnostic_role"] == "reframe_only_diagnostic"
    )
    judgments = [
        build_static_reframe_judgment(
            contract=contract,
            diagnostic_case_id=case_id,
            model="openai/gpt-5.1-chat",
            diagnostic_label="step6_non_inferior",
            winner_arm="tie",
        ),
        build_static_reframe_judgment(
            contract=contract,
            diagnostic_case_id=case_id,
            model="google/gemini-3.1-flash-lite",
            diagnostic_label="step6_better",
            winner_arm="step6_visible",
        ),
    ]

    for judgment in judgments:
        validate_reframe_diagnostic_judgment(judgment)

    result = build_reframe_diagnostic_result(contract=contract, judgments=judgments)

    validate_reframe_diagnostic_result(result)

    assert result["case_results"] == [
        {
            "diagnostic_case_id": case_id,
            "source_case_id": result["case_results"][0]["source_case_id"],
            "diagnostic_role": "reframe_only_diagnostic",
            "answer_delta_specificity": "reframe_only",
            "reviewer_count": 2,
            "reviewer_model_families": ["google", "openai"],
            "diagnostic_labels": ["step6_non_inferior", "step6_better"],
            "reviewer_winner_arms": ["tie", "step6_visible"],
            "reviewer_label_consistency": "aligned",
            "confirmed_label": "reframe_useful",
        }
    ]
    assert result["aggregate"]["diagnostic_read"] == (
        "answer_delta_vocabulary_design_review_required"
    )
