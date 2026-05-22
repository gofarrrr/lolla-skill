from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_calibration_floor_manifest import (  # noqa: E402
    build_seed_calibration_manifest,
    load_calibration_floor_manifest,
    validate_calibration_floor_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_seed_manifest_blocks_promotion_until_case_floor_is_met() -> None:
    manifest = build_seed_calibration_manifest(repo_root=REPO_ROOT)

    validate_calibration_floor_manifest(manifest)

    assert manifest["schema_version"] == "pre_step6_calibration_floor.v1"
    assert manifest["calibration_floor_met"] is False
    assert manifest["promotion_read"] == "runtime_promotion_blocked"
    assert manifest["runtime_policy"] == "runtime_dormant"
    assert manifest["required_floor"]["min_cases"] == 12
    assert manifest["required_floor"]["target_max_cases"] == 20
    assert manifest["current_suite"]["case_count"] == 4
    assert manifest["current_suite"]["suite_role"] == "seed_suite_not_calibration"
    assert manifest["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_seed_manifest_reports_bucket_gaps_without_fabricating_cases() -> None:
    manifest = build_seed_calibration_manifest(repo_root=REPO_ROOT)

    bucket_status = {
        item["bucket"]: item
        for item in manifest["bucket_status"]
    }

    assert bucket_status["high_clutter"]["observed"] == 1
    assert bucket_status["sequencing_or_problem_shape"]["observed"] == 1
    assert bucket_status["sensitive_safety_legal"]["observed"] == 2
    assert bucket_status["negative_control"]["observed"] == 1
    assert bucket_status["v60_on_off_pairs"]["observed"] == 0
    assert all(item["met"] is False for item in bucket_status.values())

    missing = {
        item["bucket"]: item["missing"]
        for item in manifest["case_curation_gaps"]
    }
    assert missing == {
        "total_cases": 8,
        "high_clutter": 2,
        "sequencing_or_problem_shape": 2,
        "sensitive_safety_legal": 1,
        "negative_control": 2,
        "v60_on_off_pairs": 2,
    }


def test_v60_pairs_mean_same_case_toggle_not_substantive_vs_minimal_curation() -> None:
    manifest = build_seed_calibration_manifest(repo_root=REPO_ROOT)

    origin = manifest["required_floor"]["v60_pair_origin"]

    assert origin == {
        "primary_definition": "same_case_run_twice_v60_on_off",
        "unit_of_pair": (
            "Same case, same prompt contract, same card deck policy; one run "
            "with V60 selected items available and one run with V60 selected "
            "items withheld."
        ),
        "substantive_vs_minimal_v60": (
            "Useful stratification label, not a substitute for same-case "
            "on/off pairs."
        ),
    }


def test_standdown_recall_is_planned_but_not_claimed_from_four_cases() -> None:
    manifest = build_seed_calibration_manifest(repo_root=REPO_ROOT)

    recall = manifest["standdown_recall"]

    assert recall["primary_runtime_failure_mode"] == "false_standdown"
    assert recall["measurement_status"] == "not_calibrated"
    assert recall["classification_values"] == [
        "true_standdown",
        "false_standdown",
        "ambiguous_standdown",
        "not_observed",
    ]
    assert recall["observed_standdowns"] == [
        {
            "case_id": "mother-address-year",
            "visible_policy_ref": (
                "research/pre-step6-card-deck-visibility-policies/"
                "mother-address-year.card-deck-visibility-policy.v1.json"
            ),
            "current_label": "true_standdown_candidate",
            "calibration_weight": "seed_only",
        }
    ]
    assert "preserved_by_marker_anchor_entities_missing" in recall["payload_preservation_outcomes"]


def test_next_bridge_probe_targets_false_standdown_before_full_curation() -> None:
    manifest = build_seed_calibration_manifest(repo_root=REPO_ROOT)

    probe = manifest["next_bridge_probe"]

    assert probe["probe_id"] == "false_standdown_bridge_probe_v0"
    assert probe["status"] == "planned_non_promotional"
    assert probe["target_case_count_min"] == 2
    assert probe["target_case_count_max"] == 3
    assert probe["promotion_effect"] == "none_bridge_only"
    assert probe["case_shapes"] == [
        {
            "shape_id": "high_clutter_sensitive_overlay",
            "why_it_matters": (
                "Tests whether runtime anchor bias suppresses useful deck "
                "pressure when clutter and tone sensitivity coexist."
            ),
        },
        {
            "shape_id": "sensitive_anchor_misses_tripwire",
            "why_it_matters": (
                "Tests the dangerous case where the deck adds a concrete "
                "tripwire the anchor missed."
            ),
        },
        {
            "shape_id": "sequencing_sensitive_boundary",
            "why_it_matters": (
                "Tests whether Polya-style sequencing survives when the "
                "answer also needs careful safety or legal boundaries."
            ),
        },
    ]


def test_calibration_manifest_fixture_validates() -> None:
    path = (
        REPO_ROOT
        / "research"
        / "pre-step6-calibration-floor"
        / "seed-suite.calibration-floor.v1.json"
    )
    payload = load_calibration_floor_manifest(path)

    validate_calibration_floor_manifest(payload)

    assert payload["calibration_floor_met"] is False
    assert payload["promotion_read"] == "runtime_promotion_blocked"
