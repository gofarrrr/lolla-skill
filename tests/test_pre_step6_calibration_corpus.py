from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_calibration_corpus import (  # noqa: E402
    build_calibration_corpus_contract,
    build_step6_calibration_stability_review,
    build_step6_calibration_prompts,
    build_step6_calibration_result,
    build_static_step6_sample,
    calibration_sample_path,
    validate_calibration_corpus_contract,
    validate_step6_calibration_result,
    validate_step6_calibration_sample,
    validate_step6_calibration_stability_review,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_calibration_corpus_meets_pre_registered_floor_without_runtime_promotion() -> None:
    contract = build_calibration_corpus_contract(root=REPO_ROOT)

    validate_calibration_corpus_contract(contract, root=REPO_ROOT)

    assert contract["schema_version"] == "pre_step6_calibration_corpus.v1"
    assert contract["runtime_policy"] == "runtime_dormant"
    assert contract["promotion_effect"] == "none_calibration_only"
    assert contract["sample_plan"]["samples_per_case"] == 3
    assert contract["sample_plan"]["step6_model"] == "moonshotai/kimi-k2.6"
    assert contract["case_count"] == 17
    assert contract["floor_status"] == "corpus_floor_met"
    assert contract["bucket_status"] == [
        {"bucket": "high_clutter", "required": 3, "observed": 5, "met": True},
        {"bucket": "sequencing_or_problem_shape", "required": 3, "observed": 6, "met": True},
        {"bucket": "sensitive_safety_legal", "required": 3, "observed": 7, "met": True},
        {"bucket": "negative_control", "required": 3, "observed": 7, "met": True},
        {"bucket": "v60_on_off_pairs", "required": 2, "observed": 2, "met": True},
    ]
    assert contract["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_calibration_corpus_contains_same_case_v60_on_off_pairs() -> None:
    contract = build_calibration_corpus_contract(root=REPO_ROOT)
    cases = {case["case_id"]: case for case in contract["cases"]}

    assert cases["founder-grant-marcus-equity.high-clutter.v60-off"]["v60_mode"] == "off"
    assert cases["founder-grant-marcus-equity.high-clutter.v60-on"]["v60_mode"] == "on"
    assert (
        cases["founder-grant-marcus-equity.high-clutter.v60-on"]["v60_toggle_pair_id"]
        == cases["founder-grant-marcus-equity.high-clutter.v60-off"]["v60_toggle_pair_id"]
    )
    assert cases["third-year-phd-student.v2.v60-off"]["v60_mode"] == "off"
    assert cases["third-year-phd-student.v2.v60-on"]["v60_mode"] == "on"
    assert "synthetic" in cases["third-year-phd-student.v2.v60-on"]["v60_evidence_source"]


def test_calibration_step6_prompt_preserves_broad_private_context_and_answer_delta() -> None:
    contract = build_calibration_corpus_contract(root=REPO_ROOT)

    prompts = build_step6_calibration_prompts(
        contract=contract,
        case_id="founder-grant-marcus-equity.high-clutter.v60-on",
        sample_index=2,
    )

    assert "You are Step 6" in prompts["system_prompt"]
    assert "anchor_visible_candidate" in prompts["user_prompt"]
    assert "deck_pressure_candidate" in prompts["user_prompt"]
    assert "v60_private_context" in prompts["user_prompt"]
    assert "answer_delta" in prompts["user_prompt"]
    assert "added_entities" in prompts["user_prompt"]
    assert "structural_delta" in prompts["user_prompt"]
    assert "reframed_emphasis" in prompts["user_prompt"]
    assert "do not overstate" in prompts["user_prompt"]


def test_static_step6_sample_and_result_measure_stability_and_reframe_frequency() -> None:
    contract = build_calibration_corpus_contract(root=REPO_ROOT)
    samples = [
        build_static_step6_sample(
            contract=contract,
            case_id="fp-bevelin-irrelevant-incentives",
            sample_index=0,
            ledger_signal="all_private_or_confirming",
            answer_delta_specificity="not_applicable",
        ),
        build_static_step6_sample(
            contract=contract,
            case_id="fp-bevelin-irrelevant-incentives",
            sample_index=1,
            ledger_signal="additive_pressure_present",
            answer_delta_specificity="reframe_only",
        ),
        build_static_step6_sample(
            contract=contract,
            case_id="fp-bevelin-irrelevant-incentives",
            sample_index=2,
            ledger_signal="all_private_or_confirming",
            answer_delta_specificity="not_applicable",
        ),
    ]

    for sample in samples:
        validate_step6_calibration_sample(sample)

    result = build_step6_calibration_result(contract=contract, samples=samples)

    validate_step6_calibration_result(result)

    assert result["case_results"] == [
        {
            "case_id": "fp-bevelin-irrelevant-incentives",
            "sample_count": 3,
            "ledger_signal_counts": {
                "additive_pressure_present": 1,
                "all_private_or_confirming": 2,
            },
            "answer_delta_specificity_counts": {
                "not_applicable": 2,
                "reframe_only": 1,
            },
            "stability_label": "unstable",
            "unlock_count": 0,
            "reframe_only_count": 1,
            "structural_delta_count": 0,
            "structural_delta_field_count": 0,
        }
    ]
    assert result["aggregate"]["unstable_case_count"] == 1
    assert result["aggregate"]["reframe_only_sample_count"] == 1
    assert result["aggregate"]["structural_delta_sample_count"] == 0
    assert result["aggregate"]["structural_delta_field_sample_count"] == 0
    assert result["aggregate"]["reviewer_tension_status"] == "not_run"


def test_calibration_sample_path_supports_resumable_live_runs(tmp_path: Path) -> None:
    assert calibration_sample_path(
        out_dir=tmp_path,
        case_id="founder-grant-marcus-equity.high-clutter.v60-off",
        sample_index=2,
    ) == (
        tmp_path
        / "founder-grant-marcus-equity.high-clutter.v60-off.sample-2.calibration-step6.v1.json"
    )


def test_calibration_result_marks_partial_cases_incomplete() -> None:
    contract = build_calibration_corpus_contract(root=REPO_ROOT)
    samples = [
        build_static_step6_sample(
            contract=contract,
            case_id="startup-pivot-new-run2",
            sample_index=0,
            ledger_signal="additive_pressure_present",
            answer_delta_specificity="concrete_delta_present",
        )
    ]

    result = build_step6_calibration_result(contract=contract, samples=samples)

    validate_step6_calibration_result(result)

    case_result = result["case_results"][0]
    assert case_result["stability_label"] == "incomplete_sampling"
    assert result["aggregate"]["incomplete_case_count"] == 1
    assert result["aggregate"]["calibration_read"] == "sampling_incomplete"


def test_stability_review_classifies_saved_samples_before_reviewer_phase() -> None:
    contract = build_calibration_corpus_contract(root=REPO_ROOT)
    samples = [
        build_static_step6_sample(
            contract=contract,
            case_id="multi-offer-new-run2",
            sample_index=index,
            ledger_signal="additive_pressure_present",
            answer_delta_specificity="concrete_delta_present",
        )
        for index in range(3)
    ]
    samples.extend(
        build_static_step6_sample(
            contract=contract,
            case_id="mother-address-year",
            sample_index=index,
            ledger_signal="all_private_or_confirming",
            answer_delta_specificity="not_applicable",
        )
        for index in range(3)
    )
    samples.extend(
        [
            build_static_step6_sample(
                contract=contract,
                case_id="bridge-high-clutter-sensitive-overlay",
                sample_index=0,
                ledger_signal="additive_pressure_present",
                answer_delta_specificity="concrete_delta_present",
            ),
            build_static_step6_sample(
                contract=contract,
                case_id="bridge-high-clutter-sensitive-overlay",
                sample_index=1,
                ledger_signal="additive_pressure_present",
                answer_delta_specificity="concrete_delta_present",
            ),
            build_static_step6_sample(
                contract=contract,
                case_id="bridge-high-clutter-sensitive-overlay",
                sample_index=2,
                ledger_signal="all_private_or_confirming",
                answer_delta_specificity="not_applicable",
            ),
        ]
    )
    samples.extend(
        [
            build_static_step6_sample(
                contract=contract,
                case_id="startup-pivot-new-run2",
                sample_index=0,
                ledger_signal="additive_pressure_present",
                answer_delta_specificity="reframe_only",
            ),
            build_static_step6_sample(
                contract=contract,
                case_id="startup-pivot-new-run2",
                sample_index=1,
                ledger_signal="additive_pressure_present",
                answer_delta_specificity="reframe_only",
            ),
            build_static_step6_sample(
                contract=contract,
                case_id="startup-pivot-new-run2",
                sample_index=2,
                ledger_signal="all_private_or_confirming",
                answer_delta_specificity="not_applicable",
            ),
        ]
    )
    samples.extend(
        [
            build_static_step6_sample(
                contract=contract,
                case_id="third-year-phd-student.v2.v60-on",
                sample_index=index,
                ledger_signal="additive_pressure_present",
                answer_delta_specificity="structural_delta_present",
            )
            for index in range(3)
        ]
    )
    samples.append(
        build_static_step6_sample(
            contract=contract,
            case_id="marker-entity-attempt-2-tripwire-compression",
            sample_index=0,
            ledger_signal="all_private_or_confirming",
            answer_delta_specificity="not_applicable",
        )
    )
    result = build_step6_calibration_result(contract=contract, samples=samples)

    review = build_step6_calibration_stability_review(
        contract=contract,
        result=result,
        samples=samples,
    )

    validate_step6_calibration_stability_review(review)

    classifications = {
        row["case_id"]: row["stability_classification"] for row in review["case_reviews"]
    }
    assert classifications == {
        "bridge-high-clutter-sensitive-overlay": "borderline_unlock",
        "marker-entity-attempt-2-tripwire-compression": "incomplete_sampling",
        "mother-address-year": "stable_standdown",
        "multi-offer-new-run2": "stable_positive",
        "startup-pivot-new-run2": "abstract_additive_only",
        "third-year-phd-student.v2.v60-on": "stable_positive",
    }
    assert review["aggregate"]["reviewer_phase_decision"] == (
        "blocked_for_full_calibration_repeat_or_partition_first"
    )
    assert review["aggregate"]["repeat_sample_case_ids"] == [
        "bridge-high-clutter-sensitive-overlay",
        "marker-entity-attempt-2-tripwire-compression",
        "startup-pivot-new-run2",
    ]
    assert review["aggregate"]["incomplete_sampling_count"] == 1
    assert review["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }
