from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.human_review import blank_human_review_template
from engine.system_b.synthetic_review import (
    SYNTHETIC_REVIEW_SCHEMA_VERSION,
    synthetic_review_schema_definition,
    validate_synthetic_review,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _valid_candidate_review() -> dict:
    return {
        **blank_human_review_template(),
        "review_status": "pass",
        "primary_failure_mode": "none",
        "severity": "none",
        "useful_friction": "present",
        "noisy_friction": "absent",
        "missing_friction": "absent",
        "revised_answer_improved": "yes",
        "safe_for_agent_use": "with_human_review",
        "reviewer_notes": "Candidate only; human ratification required.",
    }


def _valid_synthetic_review() -> dict:
    return {
        "schema_version": SYNTHETIC_REVIEW_SCHEMA_VERSION,
        "reviewer_kind": "synthetic",
        "model_or_agent": "subagent-a",
        "source_corpus_manifest": "/tmp/lolla_review_corpus_manifest.json",
        "pilot_id": "pr15-modern-batch-2026-06-26",
        "generated_at": "2026-06-26T12:00:00Z",
        "notes": "Synthetic rehearsal notes only.",
        "scope": {
            "synthetic_only": True,
            "human_review_ground_truth": False,
            "requires_human_ratification": True,
            "may_populate_human_review_without_ratification": False,
            "automatic_approval": False,
        },
        "records": [
            {
                "index": 0,
                "archive_relpath": "case-a/20260625T120000Z_abcd12",
                "case_id": "case-a",
                "run_id": "20260625T120000Z_abcd12",
                "candidate_human_review": _valid_candidate_review(),
                "confidence": "medium",
                "uncertainties": [
                    "Synthetic reviewer did not inspect every raw artifact."
                ],
                "qa_notes": [
                    "Answer-level pass, but human review remains required."
                ],
            }
        ],
    }


def test_synthetic_review_schema_document_matches_code_contract() -> None:
    schema_doc = _load_json("docs/evals/lolla-synthetic-review-v0.json")

    assert schema_doc == synthetic_review_schema_definition()


def test_synthetic_review_prompt_template_uses_current_label_values() -> None:
    prompt = (REPO_ROOT / "docs/evals/synthetic-review-prompt-template.md").read_text(
        encoding="utf-8"
    )

    assert "`review_status`:" in prompt
    assert "- `pass`" in prompt
    assert "- `fail`" in prompt
    assert "- `needs_followup`" in prompt
    assert "- `exclude_from_eval`" in prompt
    assert "`severity`:" in prompt
    assert "- `none`" in prompt
    assert "- `low`" in prompt
    assert "- `medium`" in prompt
    assert "- `high`" in prompt
    assert "- `critical`" in prompt
    assert "Do not use `minor`, `material`, or `unclear` for severity." in prompt


def test_valid_synthetic_review_payload_is_accepted() -> None:
    assert validate_synthetic_review(_valid_synthetic_review()) == []


def test_blank_candidate_human_review_is_rejected_for_synthetic_output() -> None:
    payload = _valid_synthetic_review()
    payload["records"][0]["candidate_human_review"] = blank_human_review_template()

    errors = validate_synthetic_review(payload)

    assert (
        "records[0].candidate_human_review.review_status is required "
        "for synthetic review"
    ) in errors
    assert (
        "records[0].candidate_human_review.primary_failure_mode is required "
        "for synthetic review"
    ) in errors
    assert (
        "records[0].candidate_human_review.safe_for_agent_use is required "
        "for synthetic review"
    ) in errors


def test_invalid_candidate_severity_values_are_rejected() -> None:
    for invalid_severity in ("minor", "material", "unclear"):
        payload = _valid_synthetic_review()
        payload["records"][0]["candidate_human_review"]["severity"] = invalid_severity

        errors = validate_synthetic_review(payload)

        assert any(
            "candidate_human_review.severity has invalid value" in error
            and invalid_severity in error
            for error in errors
        )


def test_candidate_human_review_validation_is_delegated() -> None:
    payload = _valid_synthetic_review()
    payload["records"][0]["candidate_human_review"]["primary_failure_mode"] = (
        "made_up_failure"
    )

    errors = validate_synthetic_review(payload)

    assert any(
        "candidate_human_review.primary_failure_mode has invalid value" in error
        for error in errors
    )


def test_synthetic_review_cannot_claim_human_ground_truth() -> None:
    payload = _valid_synthetic_review()
    payload["scope"]["human_review_ground_truth"] = True
    payload["scope"]["requires_human_ratification"] = False
    payload["scope"]["may_populate_human_review_without_ratification"] = True

    errors = validate_synthetic_review(payload)

    assert "scope.human_review_ground_truth must be False" in errors
    assert "scope.requires_human_ratification must be True" in errors
    assert (
        "scope.may_populate_human_review_without_ratification must be False"
        in errors
    )


def test_synthetic_review_records_require_stable_shapes() -> None:
    payload = _valid_synthetic_review()
    payload["records"][0]["index"] = "0"
    payload["records"][0]["confidence"] = "certain"
    payload["records"][0]["uncertainties"] = "none"
    payload["records"][0]["qa_notes"] = ["ok", 7]

    errors = validate_synthetic_review(payload)

    assert "records[0].index must be a non-negative integer" in errors
    assert any(
        "records[0].confidence has invalid value 'certain'" in error
        for error in errors
    )
    assert "records[0].uncertainties must be a list of strings" in errors
    assert "records[0].qa_notes must be a list of strings" in errors
