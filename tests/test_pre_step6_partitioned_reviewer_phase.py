from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_partitioned_reviewer_phase import (  # noqa: E402
    build_partitioned_reviewer_contract,
    build_partitioned_reviewer_result,
    build_reviewer_packet,
    build_static_partitioned_judgment,
    validate_partitioned_reviewer_contract,
    validate_partitioned_reviewer_judgment,
    validate_partitioned_reviewer_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_partitioned_contract_selects_only_stable_cases_and_blocks_promotion() -> None:
    contract = build_partitioned_reviewer_contract(root=REPO_ROOT)

    validate_partitioned_reviewer_contract(contract)

    assert contract["schema_version"] == "pre_step6_partitioned_reviewer_contract.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_research_only"
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }

    classifications = {
        case["stability_classification"] for case in contract["stable_cases"]
    }
    assert classifications == {"stable_positive", "stable_standdown"}
    assert len(contract["stable_cases"]) == 13
    assert set(contract["excluded_variable_case_ids"]) == {
        "founder-grant-marcus-equity.high-clutter.v60-on",
        "mid-level-consultant-report-2",
        "third-year-phd-student.v2.v60-off",
        "third-year-phd-student.v2.v60-on",
    }


def test_partitioned_reviewer_packet_blinds_candidate_arms() -> None:
    contract = build_partitioned_reviewer_contract(root=REPO_ROOT)
    case_id = contract["stable_cases"][0]["partition_case_id"]

    packet = build_reviewer_packet(contract=contract, partition_case_id=case_id, seed=7)

    assert set(packet["candidates_by_label"]) == {"A", "B"}
    assert set(packet["blind_map_private"].values()) == {
        "anchor_visible",
        "step6_visible",
    }
    public_packet = dict(packet)
    public_packet.pop("blind_map_private")
    assert "anchor_visible" not in str(public_packet["candidates_by_label"])
    assert "step6_visible" not in str(public_packet["candidates_by_label"])


def test_partitioned_result_requires_two_family_consistent_support() -> None:
    contract = build_partitioned_reviewer_contract(root=REPO_ROOT)
    positive_case_id = next(
        case["partition_case_id"]
        for case in contract["stable_cases"]
        if case["stability_classification"] == "stable_positive"
    )
    standdown_case_id = next(
        case["partition_case_id"]
        for case in contract["stable_cases"]
        if case["stability_classification"] == "stable_standdown"
    )
    judgments = [
        build_static_partitioned_judgment(
            contract=contract,
            partition_case_id=positive_case_id,
            model="openai/gpt-5.1-chat",
            review_label="step6_better",
            winner_arm="step6_visible",
        ),
        build_static_partitioned_judgment(
            contract=contract,
            partition_case_id=positive_case_id,
            model="google/gemini-3.1-flash-lite",
            review_label="step6_non_inferior",
            winner_arm="tie",
        ),
        build_static_partitioned_judgment(
            contract=contract,
            partition_case_id=standdown_case_id,
            model="openai/gpt-5.1-chat",
            review_label="anchor_better",
            winner_arm="anchor_visible",
        ),
        build_static_partitioned_judgment(
            contract=contract,
            partition_case_id=standdown_case_id,
            model="google/gemini-3.1-flash-lite",
            review_label="tie",
            winner_arm="tie",
        ),
    ]

    for judgment in judgments:
        validate_partitioned_reviewer_judgment(judgment)

    result = build_partitioned_reviewer_result(contract=contract, judgments=judgments)

    validate_partitioned_reviewer_result(result)

    confirmed = {
        row["partition_case_id"]: row["confirmed_label"]
        for row in result["case_results"]
    }
    assert confirmed[positive_case_id] == "stable_positive_supported"
    assert confirmed[standdown_case_id] == "stable_standdown_supported"
    assert result["aggregate"]["reviewer_read"] == "stable_partition_supported"
