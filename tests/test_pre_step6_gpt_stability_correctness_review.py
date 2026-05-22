from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_gpt_stability_correctness_review import (  # noqa: E402
    build_gpt_stability_correctness_contract,
    build_gpt_stability_correctness_result,
    build_reviewer_packet,
    build_static_gpt_stability_judgment,
    validate_gpt_stability_correctness_contract,
    validate_gpt_stability_correctness_judgment,
    validate_gpt_stability_correctness_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gpt_stability_contract_selects_stable_gpt_outputs_only() -> None:
    contract = build_gpt_stability_correctness_contract(root=REPO_ROOT)

    validate_gpt_stability_correctness_contract(contract)

    assert contract["schema_version"] == "pre_step6_gpt_stability_correctness_contract.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }

    source_ids = {case["source_case_id"] for case in contract["review_cases"]}
    assert source_ids == {
        "mid-level-consultant-report-2",
        "third-year-phd-student.v2.v60-off",
        "third-year-phd-student.v2.v60-on",
    }
    assert len(contract["review_cases"]) == 9
    assert contract["excluded_case_ids"] == [
        "founder-grant-marcus-equity.high-clutter.v60-on"
    ]
    assert {case["expected_visibility_decision"] for case in contract["review_cases"]} == {
        "anchor_visible",
        "step6_visible",
    }
    assert any(case["pure_structural_delta_only"] for case in contract["review_cases"])
    assert all(case["model_under_review"] == "openai/gpt-5.1-chat" for case in contract["review_cases"])


def test_gpt_stability_reviewer_packet_splits_output_and_visibility_questions() -> None:
    contract = build_gpt_stability_correctness_contract(root=REPO_ROOT)
    review_case_id = contract["review_cases"][0]["review_case_id"]

    packet = build_reviewer_packet(contract=contract, review_case_id=review_case_id, seed=11)

    assert set(packet["candidates_by_label"]) == {"A", "B"}
    assert set(packet["blind_map_private"].values()) == {
        "anchor_visible",
        "step6_visible",
    }
    assert "output_label" in packet["response_schema"]
    assert "visibility_judgment" in packet["response_schema"]
    assert "model-family stability" in packet["reviewer_task"]


def test_gpt_stability_result_tracks_visibility_correctness_and_structural_delta() -> None:
    contract = build_gpt_stability_correctness_contract(root=REPO_ROOT)
    anchor_case_id = next(
        case["review_case_id"]
        for case in contract["review_cases"]
        if case["expected_visibility_decision"] == "anchor_visible"
    )
    visible_case_id = next(
        case["review_case_id"]
        for case in contract["review_cases"]
        if case["expected_visibility_decision"] == "step6_visible"
        and case["pure_structural_delta_only"] is True
    )
    judgments = [
        build_static_gpt_stability_judgment(
            contract=contract,
            review_case_id=anchor_case_id,
            model="openai/gpt-5.1-chat",
            output_label="tie",
            winner_arm="tie",
            visibility_judgment="correct_anchor",
        ),
        build_static_gpt_stability_judgment(
            contract=contract,
            review_case_id=anchor_case_id,
            model="google/gemini-3.1-flash-lite",
            output_label="non_inferior",
            winner_arm="anchor_visible",
            visibility_judgment="correct_anchor",
        ),
        build_static_gpt_stability_judgment(
            contract=contract,
            review_case_id=visible_case_id,
            model="openai/gpt-5.1-chat",
            output_label="better",
            winner_arm="step6_visible",
            visibility_judgment="correct_visible",
        ),
        build_static_gpt_stability_judgment(
            contract=contract,
            review_case_id=visible_case_id,
            model="google/gemini-3.1-flash-lite",
            output_label="non_inferior",
            winner_arm="tie",
            visibility_judgment="correct_visible",
        ),
    ]

    for judgment in judgments:
        validate_gpt_stability_correctness_judgment(judgment)

    result = build_gpt_stability_correctness_result(contract=contract, judgments=judgments)

    validate_gpt_stability_correctness_result(result)

    confirmed = {row["review_case_id"]: row["confirmed_visibility_label"] for row in result["case_results"]}
    assert confirmed[anchor_case_id] == "gpt_anchor_supported"
    assert confirmed[visible_case_id] == "gpt_visible_supported"
    assert result["aggregate"]["structural_delta_only_reviewed_count"] == 1
    assert result["aggregate"]["reviewer_read"] == "gpt_stability_partial_or_incomplete"


def test_gpt_anchor_rejected_when_reviewers_say_visible_should_have_fired() -> None:
    contract = build_gpt_stability_correctness_contract(root=REPO_ROOT)
    anchor_case_id = next(
        case["review_case_id"]
        for case in contract["review_cases"]
        if case["expected_visibility_decision"] == "anchor_visible"
    )
    judgments = [
        build_static_gpt_stability_judgment(
            contract=contract,
            review_case_id=anchor_case_id,
            model="openai/gpt-5.1-chat",
            output_label="better",
            winner_arm="step6_visible",
            visibility_judgment="correct_visible",
        ),
        build_static_gpt_stability_judgment(
            contract=contract,
            review_case_id=anchor_case_id,
            model="google/gemini-3.1-flash-lite",
            output_label="non_inferior",
            winner_arm="step6_visible",
            visibility_judgment="wrong_anchor",
        ),
    ]

    result = build_gpt_stability_correctness_result(contract=contract, judgments=judgments)

    assert result["case_results"][0]["confirmed_visibility_label"] == "gpt_anchor_rejected"
    assert result["aggregate"]["gpt_anchor_rejected_count"] == 1
    assert result["aggregate"]["reviewer_read"] == "gpt_stability_design_review_required"
