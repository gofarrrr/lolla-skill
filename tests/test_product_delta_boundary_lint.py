from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import (
    PRODUCT_DELTA_BOUNDARY_LINT_SCHEMA_VERSION,
    lint_product_delta_paths,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_PRODUCT_DELTA_ARTIFACTS = [
    REPO_ROOT / "docs/evals/vanilla-vs-lolla-provisional-review-v0.json",
    REPO_ROOT / "reviews/codex-assisted/paired-review-dry-run-v0/review.json",
    REPO_ROOT / "docs/evals/provisional-product-delta-failure-taxonomy-v0.json",
    REPO_ROOT / "reviews/codex-assisted/product-delta-provisional-run-v0/review.json",
    REPO_ROOT / "reviews/codex-assisted/product-delta-batch-v0/review.json",
    REPO_ROOT / "docs/evals/product-delta-provisional-report-v0.md",
]


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_markdown(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _review_case(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "lolla.vanilla_vs_lolla_provisional_review.v0",
        "review_mode": "codex_assisted_provisional",
        "human_validated": False,
        "ground_truth": False,
        "judge_calibration_eligible": False,
        "reviewer_type": "codex",
        "case_id": "case-1",
        "archive_relpath": "case-1/run-1",
        "reviewed_artifacts": ["docs/evals/source.md"],
        "raw_private_content_included": False,
        "model_calls": 0,
        "archive_mutated": False,
        "vanilla_likely_next_action": {
            "status": "provisional_supported",
            "summary": "Vanilla likely action candidate.",
            "basis": ["review-safe source"],
            "uncertainty": "medium",
            "reviewer_inferred": True,
        },
        "lolla_likely_next_action": {
            "status": "provisional_supported",
            "summary": "Lolla likely action candidate.",
            "basis": ["review-safe source"],
            "uncertainty": "medium",
            "reviewer_inferred": True,
        },
        "material_difference": {
            "status": "provisional_supported",
            "summary": "Candidate changed threshold.",
            "changed": True,
            "uncertainty": "medium",
        },
        "structural_delta": {
            "action_changed": False,
            "threshold_changed": True,
            "sequence_changed": False,
            "evidence_gate_added_or_changed": True,
            "stop_rule_added_or_changed": False,
            "written_term_added_or_changed": False,
            "scope_changed": False,
            "overclaim_retracted": False,
            "user_answerable_question_added": True,
            "notes": "Candidate structural delta.",
        },
        "decision_leverage": {
            "label": "medium",
            "rationale": "Could change behavior.",
            "uncertainty": "medium",
        },
        "friction_read": {
            "useful_friction": "partial",
            "noisy_friction": "unclear",
            "missing_friction": "unclear",
            "grounded": True,
            "actionable": True,
            "proportionate": None,
            "rationale": "Candidate useful friction with uncertainty.",
        },
        "lost_value": {
            "present": True,
            "categories": ["momentum"],
            "rationale": "Could slow useful momentum.",
        },
        "interpretation_adequacy": {
            "label": "partly_adequate",
            "failure_modes": ["uncertainty_collapse"],
            "rationale": "Compressed source.",
            "would_better_interpretation_change_answer": "unclear",
        },
        "first_upstream_failure": {
            "surface": "review_surface",
            "summary": "Safe surface is compressed.",
        },
        "net_decision_read_provisional": {
            "label": "partial_improvement_candidate",
            "rationale": "Candidate only.",
        },
        "codex_uncertainty_notes": ["Not human validated."],
        "human_followup_questions": ["Would this change user behavior?"],
        "non_claims": [
            "not human review",
            "not ground truth",
            "not judge calibration data",
            "not product proof",
            "not agent approval",
            "not answer-quality scoring",
            "not automatic labeling",
        ],
    }
    payload.update(overrides)
    return payload


def _codes(report: dict[str, object]) -> set[str]:
    return {
        finding["code"]
        for finding in report["findings"]
        if isinstance(finding, dict)
    }


def test_current_product_delta_artifacts_pass_without_findings() -> None:
    report = lint_product_delta_paths(CURRENT_PRODUCT_DELTA_ARTIFACTS)

    assert report["schema_version"] == PRODUCT_DELTA_BOUNDARY_LINT_SCHEMA_VERSION
    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_blocks_unsafe_metadata(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.json"
    _write_json(
        path,
        _review_case(
            human_validated=True,
            ground_truth=True,
            judge_calibration_eligible=True,
            model_calls=1,
            archive_mutated=True,
        ),
    )

    report = lint_product_delta_paths([path])

    assert report["summary"]["blocking_error_count"] >= 5
    assert {
        "human_validated_must_be_false",
        "ground_truth_must_be_false",
        "judge_calibration_eligible_must_be_false",
        "model_calls_must_be_zero",
        "archive_mutated_must_be_false",
    } <= _codes(report)


def test_blocks_forbidden_authority_fields(tmp_path: Path) -> None:
    path = tmp_path / "forbidden.json"
    _write_json(
        path,
        {
            "schema_version": "lolla.product_delta_fixture.v0",
            "safe_for_agent_use": "yes",
            "quality_score": 9,
            "approved": True,
            "winner": "lolla",
        },
    )

    report = lint_product_delta_paths([path])

    assert report["summary"]["blocking_error_count"] == 4
    assert "forbidden_safe_for_agent_use_field" in _codes(report)
    assert "forbidden_authority_field" in _codes(report)


def test_blocks_taxonomy_score_drift(tmp_path: Path) -> None:
    path = tmp_path / "taxonomy.json"
    _write_json(
        path,
        {
            "schema_version": "lolla.provisional_product_delta_failure_taxonomy.v0",
            "review_mode": "codex_assisted_provisional",
            "human_validated": False,
            "ground_truth": False,
            "judge_calibration_eligible": False,
            "not_a_score": True,
            "automatic_labels": False,
            "entries": [
                {
                    "id": "no_op_prose",
                    "category": "product_delta_failure",
                    "definition": "No action change.",
                    "why_it_matters": "No leverage.",
                    "provisional_detection_question": "Did action change?",
                    "possible_review_surface": "structural_delta",
                    "deterministic_or_subjective": "subjective",
                    "current_status": "provisional_until_human_review",
                }
            ],
        },
    )

    report = lint_product_delta_paths([path])

    assert report["summary"]["blocking_error_count"] == 1
    assert "taxonomy_entry_not_a_score_missing" in _codes(report)


def test_warns_on_unsafe_prose(tmp_path: Path) -> None:
    path = tmp_path / "report.md"
    _write_markdown(path, "# Report\n\nLolla proved it improved the decision.\n")

    report = lint_product_delta_paths([path])

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] >= 1
    assert "markdown_possible_product_proof_claim" in _codes(report)


def test_blocks_privacy_markers(tmp_path: Path) -> None:
    path = tmp_path / "private.json"
    _write_json(path, {"schema_version": "x", "note": "/Users/example api_key"})

    report = lint_product_delta_paths([path])

    assert report["summary"]["blocking_error_count"] == 2
    assert "privacy_marker_detected" in _codes(report)


def test_cli_succeeds_for_safe_fixture(tmp_path: Path) -> None:
    path = tmp_path / "safe.json"
    _write_json(path, _review_case())

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/lint_product_delta_evidence.py",
            "--paths",
            str(path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "blocking_error: 0" in result.stdout


def test_cli_exits_nonzero_for_blocking_fixture(tmp_path: Path) -> None:
    path = tmp_path / "unsafe.json"
    _write_json(path, _review_case(human_validated=True))

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/lint_product_delta_evidence.py",
            "--paths",
            str(path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "human_validated_must_be_false" in result.stdout


def test_cli_writes_json_report(tmp_path: Path) -> None:
    path = tmp_path / "safe.json"
    json_out = tmp_path / "lint.json"
    _write_json(path, _review_case())

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/lint_product_delta_evidence.py",
            "--paths",
            str(path),
            "--json-out",
            str(json_out),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    stdout_payload = json.loads(result.stdout)
    written_payload = json.loads(json_out.read_text(encoding="utf-8"))
    assert stdout_payload["schema_version"] == PRODUCT_DELTA_BOUNDARY_LINT_SCHEMA_VERSION
    assert written_payload["summary"]["blocking_error_count"] == 0
