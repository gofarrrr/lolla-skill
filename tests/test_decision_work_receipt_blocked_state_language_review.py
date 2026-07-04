from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-receipt-blocked-state-language-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-receipt-blocked-state-language-review-v0/review.json"
)
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-package-gate-v0.md"
)
PACKAGE_MANIFEST = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-package-manifest-v0.json"
)
READINESS_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-prd-v0.md"
)
AUTOMATIC_SUPPLY_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
EXPECTED_TERMS = {
    "sidecar_ready_for_explicit_write",
    "sidecar_ready_blocked_state",
    "deferred_missing_semantic_read",
    "deferred_missing_triage",
    "blocked_runtime_or_user_surface_risk",
    "dry-run readiness",
    "automation readiness",
    "explicit write",
    "sidecar-ready",
    "blocked-state sidecar",
    "runner_summary.json",
    "operator_attention_items",
}


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_review_json_schema_gate_and_next_pr() -> None:
    review = _json(REVIEW_PATH)

    assert review["schema_version"] == (
        "lolla.decision_work_receipt_blocked_state_language_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_review_tests_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runner_behavior_changed"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["decision_gate"] == (
        "proceed_to_product_delta_evaluation_readiness_prd"
    )
    assert review["recommended_next_pr"] == (
        "Product Delta Evaluation Readiness PRD v0"
    )


def test_review_covers_requested_terms() -> None:
    review = _json(REVIEW_PATH)
    text = DOC_PATH.read_text(encoding="utf-8")

    assert EXPECTED_TERMS <= set(review["terms_reviewed"])
    for term in EXPECTED_TERMS:
        assert term in text


def test_sidecar_ready_terms_are_accepted_only_with_caveats() -> None:
    review = _json(REVIEW_PATH)
    findings = review["term_findings"]
    text = DOC_PATH.read_text(encoding="utf-8")

    ready = findings["sidecar_ready_for_explicit_write"]
    assert ready["acceptable_with_caveats"] is True
    assert ready["could_be_mistaken_for_resolver_approval_if_isolated"] is True
    assert ready["could_be_mistaken_for_automatic_write_if_isolated"] is True
    assert "resolver_refs_not_approved" in ready["required_caveats"]
    assert "runner_never_writes_sidecars_by_itself" in ready["required_caveats"]
    blocked = findings["sidecar_ready_blocked_state"]
    assert blocked["acceptable_with_caveats"] is True
    assert blocked["could_be_mistaken_for_user_surface_readiness_if_isolated"]
    assert "blocked_state_preserved" in blocked["required_caveats"]
    assert "The sidecar is approved, available, or automatically writable." in text
    assert "The case is ready for user-facing use." in text


def test_review_answers_requested_questions() -> None:
    questions = _json(REVIEW_PATH)["review_questions"]

    assert questions[
        "sidecar_ready_for_explicit_write_mistakable_for_resolver_approval"
    ] == "possible_if_isolated_but_acceptable_with_current_caveats"
    assert questions[
        "sidecar_ready_for_explicit_write_mistakable_for_automatic_write"
    ] == "possible_if_isolated_but_acceptable_with_current_caveats"
    assert questions["runner_never_writes_sidecars_by_itself_clear"] is True
    assert questions["semantic_inputs_must_already_exist_clear"] is True
    assert questions["not_arbitrary_run_semantic_generation_clear"] is True
    assert questions[
        "not_product_proof_human_validation_scoring_advice_correctness_certification_or_action_clear"
    ] is True
    assert questions["pr229_and_pr231_limitations_visible_enough"] is True
    assert questions["first_30_seconds_non_engineer_readability"] == (
        "acceptable_for_internal_readers_with_caveats_preserved"
    )


def test_review_keeps_missingness_lens_without_new_unknowns_schema() -> None:
    review = _json(REVIEW_PATH)
    missingness = review["missingness_lens"]
    text = DOC_PATH.read_text(encoding="utf-8")

    assert missingness["missing_required_inputs_preserved"] is True
    assert missingness["deferred_reasons_preserved"] is True
    assert missingness["blocker_reasons_preserved"] is True
    assert missingness["operator_attention_items_preserved"] is True
    assert missingness["source_depth_limits_preserved"] is True
    assert missingness["runtime_user_surface_blocked_state_preserved"] is True
    assert missingness["new_unknowns_schema_created"] is False
    assert missingness["known_known_known_unknown_taxonomy_created"] is False
    assert missingness["semantic_conclusions_added"] is False
    assert "does not introduce a new Unknowns Register" in text
    assert "does not add a known-known / known-unknown taxonomy" in text


def test_language_review_requires_no_code_or_behavior_change() -> None:
    review = _json(REVIEW_PATH)
    findings = review["language_findings"]
    text = DOC_PATH.read_text(encoding="utf-8")

    assert findings[
        "current_language_acceptable_with_explicit_limitations_preserved"
    ] is True
    assert findings["code_or_constant_change_needed"] is False
    assert findings["doc_only_review_sufficient"] is True
    assert findings["avoid_shortening_sidecar_ready_to_ready"] is True
    assert "No runner behavior change is needed" in text
    assert "Future docs should keep the phrase" in text


def test_boundary_flags_remain_false() -> None:
    boundary = _json(REVIEW_PATH)["boundary_checks"]

    for key in (
        "write_attempted",
        "actual_sidecar_write_performed",
        "archive_mutated",
        "historical_archive_mutated",
        "runtime_wiring_changed",
        "runtime_attachment_default_on",
        "resolver_refs_approved",
        "queue_worker_added",
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "advice_correctness_claimed",
        "approval_or_certification_added",
        "agent_action_authorized",
        "automatic_action_authorized",
    ):
        assert boundary[key] is False


def test_review_stays_separate_from_product_delta_eval_work() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "Product Delta Evaluation Readiness PRD v0" in text
    assert "should be a new evaluation phase PRD" in text
    assert "should not be mixed into this closeout review" in text
    assert "should not jump directly to a live model-judge harness" in text


def test_discoverability_docs_reference_pr234() -> None:
    expected = "Decision Work Receipt / Blocked-State Language Review"
    for path in (
        DOC_PATH,
        PACKAGE_DOC,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr234_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PACKAGE_DOC,
            PACKAGE_MANIFEST,
            READINESS_PRD,
            AUTOMATIC_SUPPLY_PRD,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_pr234_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PACKAGE_DOC,
        PACKAGE_MANIFEST,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
