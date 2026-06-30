from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PR72_SCHEMA_PATH = REPO_ROOT / "docs/evals/vanilla-vs-lolla-provisional-review-v0.json"
PR76_BATCH_PATH = REPO_ROOT / "reviews/codex-assisted/product-delta-batch-v0/review.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_pr76_batch_preserves_non_claim_metadata() -> None:
    batch = _load_json(PR76_BATCH_PATH)

    assert batch["review_mode"] == "codex_assisted_provisional"
    assert batch["human_validated"] is False
    assert batch["ground_truth"] is False
    assert batch["judge_calibration_eligible"] is False
    assert batch["model_calls"] == 0
    assert batch["archive_mutated"] is False
    assert batch["raw_private_content_included"] is False
    assert batch["reviewer_type"] == "codex"

    for case in batch["cases"]:
        assert case["review_mode"] == "codex_assisted_provisional"
        assert case["human_validated"] is False
        assert case["ground_truth"] is False
        assert case["judge_calibration_eligible"] is False
        assert case["model_calls"] == 0
        assert case["archive_mutated"] is False
        assert case["raw_private_content_included"] is False
        assert case["reviewer_type"] == "codex"


def test_pr76_cases_match_pr72_required_shape_and_no_extra_fields() -> None:
    schema = _load_json(PR72_SCHEMA_PATH)
    batch = _load_json(PR76_BATCH_PATH)
    required = set(schema["required"])
    allowed = set(schema["properties"])

    for case in batch["cases"]:
        assert required <= set(case), case["case_id"]
        assert set(case) <= allowed, case["case_id"]
        assert "archive_relpath" in case or "case_relpath" in case
        assert case["schema_version"] == "lolla.vanilla_vs_lolla_provisional_review.v0"
        assert case["reviewed_artifacts"], case["case_id"]
        assert len(case["human_followup_questions"]) >= 3, case["case_id"]
        assert len(case["codex_uncertainty_notes"]) >= 2, case["case_id"]
        assert len(case["non_claims"]) >= 7, case["case_id"]


def test_pr76_cases_use_pr72_vocabularies() -> None:
    schema = _load_json(PR72_SCHEMA_PATH)
    batch = _load_json(PR76_BATCH_PATH)
    defs = schema["$defs"]
    review_statuses = set(defs["review_status"]["enum"])
    uncertainties = set(defs["uncertainty"]["enum"])
    friction_statuses = set(defs["friction_status"]["enum"])
    decision_labels = set(schema["properties"]["decision_leverage"]["properties"]["label"]["enum"])
    lost_categories = set(
        schema["properties"]["lost_value"]["properties"]["categories"]["items"]["enum"]
    )
    interpretation_labels = set(
        schema["properties"]["interpretation_adequacy"]["properties"]["label"]["enum"]
    )
    interpretation_failure_modes = set(
        schema["properties"]["interpretation_adequacy"]["properties"]["failure_modes"]["items"]["enum"]
    )
    upstream_surfaces = set(
        schema["properties"]["first_upstream_failure"]["properties"]["surface"]["enum"]
    )
    net_labels = set(
        schema["properties"]["net_decision_read_provisional"]["properties"]["label"]["enum"]
    )

    for case in batch["cases"]:
        assert case["vanilla_likely_next_action"]["status"] in review_statuses
        assert case["lolla_likely_next_action"]["status"] in review_statuses
        assert case["material_difference"]["status"] in review_statuses
        assert case["vanilla_likely_next_action"]["uncertainty"] in uncertainties
        assert case["lolla_likely_next_action"]["uncertainty"] in uncertainties
        assert case["material_difference"]["uncertainty"] in uncertainties
        assert case["decision_leverage"]["label"] in decision_labels
        assert case["decision_leverage"]["uncertainty"] in uncertainties
        assert case["friction_read"]["useful_friction"] in friction_statuses
        assert case["friction_read"]["noisy_friction"] in friction_statuses
        assert case["friction_read"]["missing_friction"] in friction_statuses
        assert set(case["lost_value"]["categories"]) <= lost_categories
        assert case["interpretation_adequacy"]["label"] in interpretation_labels
        assert set(case["interpretation_adequacy"]["failure_modes"]) <= (
            interpretation_failure_modes
        )
        assert case["first_upstream_failure"]["surface"] in upstream_surfaces
        assert case["net_decision_read_provisional"]["label"] in net_labels


def test_pr76_label_distribution_is_mixed_and_matches_aggregate() -> None:
    batch = _load_json(PR76_BATCH_PATH)
    labels = Counter(
        case["net_decision_read_provisional"]["label"] for case in batch["cases"]
    )
    aggregate = batch["aggregate_provisional_summary"]

    assert len(batch["cases"]) == 12
    assert labels["material_improvement_candidate"] == aggregate["material_improvement_candidate"]
    assert labels["partial_improvement_candidate"] == aggregate["partial_improvement_candidate"]
    assert labels["no_material_change_candidate"] == aggregate["no_material_change_candidate"]
    assert labels["inconclusive"] == aggregate["inconclusive"]
    assert labels["material_improvement_candidate"] < len(batch["cases"])
    assert labels["no_material_change_candidate"] >= 1
    assert labels["inconclusive"] >= 1


def test_pr76_subjective_fields_have_basis_uncertainty_and_lost_value() -> None:
    batch = _load_json(PR76_BATCH_PATH)

    for case in batch["cases"]:
        assert case["vanilla_likely_next_action"]["basis"], case["case_id"]
        assert case["lolla_likely_next_action"]["basis"], case["case_id"]
        assert case["vanilla_likely_next_action"]["uncertainty"] in {
            "low",
            "medium",
            "high",
            "unclear",
        }
        assert case["material_difference"]["uncertainty"] in {
            "low",
            "medium",
            "high",
            "unclear",
        }
        assert case["decision_leverage"]["uncertainty"] in {
            "low",
            "medium",
            "high",
            "unclear",
        }
        assert case["lost_value"]["present"] is True, case["case_id"]
        assert case["lost_value"]["categories"], case["case_id"]
        assert case["friction_read"]["rationale"], case["case_id"]
        assert case["interpretation_adequacy"]["rationale"], case["case_id"]


def test_pr76_output_does_not_include_private_markers_or_absolute_paths() -> None:
    rendered = PR76_BATCH_PATH.read_text(encoding="utf-8") + (
        REPO_ROOT / "docs/evals/codex-assisted-product-delta-batch-v0.md"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "/Users/",
        "SECRET",
        "raw_message_content",
        "fabricated_passages",
        "FULL ASSISTANT REASONING",
        "client_secret",
        "api_key",
        "password",
    ):
        assert forbidden not in rendered
