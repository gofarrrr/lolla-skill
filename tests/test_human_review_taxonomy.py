from __future__ import annotations

import json
from pathlib import Path

from engine.system_b import review_corpus
from engine.system_b.human_review import (
    HUMAN_REVIEW_SCHEMA_VERSION,
    blank_human_review_template,
    human_review_schema_definition,
    validate_human_review,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_blank_human_review_template_is_valid() -> None:
    review = blank_human_review_template()

    assert review == {
        "schema_version": HUMAN_REVIEW_SCHEMA_VERSION,
        "reviewer_id": None,
        "review_status": None,
        "primary_failure_mode": None,
        "severity": None,
        "useful_friction": None,
        "noisy_friction": None,
        "missing_friction": None,
        "revised_answer_improved": None,
        "safe_for_agent_use": None,
        "reviewer_notes": None,
    }
    assert validate_human_review(review) == []
    assert review_corpus.blank_human_review_template() == review


def test_schema_document_matches_code_contract() -> None:
    schema_doc = _load_json("docs/evals/lolla-human-review-v0.json")

    assert schema_doc == human_review_schema_definition()


def test_synthetic_review_schema_stays_outside_human_review() -> None:
    schema_doc = _load_json("docs/evals/lolla-synthetic-review-v0.json")

    assert schema_doc["schema_version"] == "lolla.synthetic_review_schema.v0"
    assert schema_doc["synthetic_review_record_schema_version"] == (
        "lolla.synthetic_review.v0"
    )
    assert schema_doc["scope"]["synthetic_only"] is True
    assert schema_doc["scope"]["human_review_ground_truth"] is False
    assert schema_doc["scope"]["requires_human_ratification"] is True
    assert schema_doc["scope"][
        "may_populate_human_review_without_ratification"
    ] is False


def test_reviewed_example_fixture_is_valid() -> None:
    example = _load_json("docs/evals/examples/human-review-example-fail.json")

    assert validate_human_review(example) == []
    assert example["review_status"] == "fail"
    assert example["primary_failure_mode"] == "constraint_drift"
    assert example["safe_for_agent_use"] == "with_human_review"


def test_invalid_review_labels_are_rejected() -> None:
    review = {
        **blank_human_review_template(),
        "review_status": "helpful",
        "primary_failure_mode": "too_much_caution",
        "severity": "severe",
        "useful_friction": "mostly",
        "unexpected": "field",
    }

    errors = validate_human_review(review)

    assert "unknown human_review field: unexpected" in errors
    assert any(
        "review_status has invalid value 'helpful'" in error
        for error in errors
    )
    assert any(
        "primary_failure_mode has invalid value 'too_much_caution'" in error
        for error in errors
    )
    assert any("severity has invalid value 'severe'" in error for error in errors)
    assert any(
        "useful_friction has invalid value 'mostly'" in error
        for error in errors
    )


def test_pass_fail_cross_field_rules_are_conservative() -> None:
    passing_review = {
        **blank_human_review_template(),
        "review_status": "pass",
        "primary_failure_mode": "none",
        "severity": "none",
        "useful_friction": "present",
        "noisy_friction": "absent",
        "missing_friction": "absent",
        "revised_answer_improved": "yes",
        "safe_for_agent_use": "yes",
    }
    failing_review = {
        **blank_human_review_template(),
        "review_status": "fail",
        "primary_failure_mode": None,
        "severity": None,
    }

    assert validate_human_review(passing_review) == []
    assert validate_human_review(failing_review) == [
        "review_status 'fail' requires a primary_failure_mode",
        "review_status 'fail' requires non-none severity",
    ]
