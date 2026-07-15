from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-real-archive-sidecar-write-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-real-archive-sidecar-write-plan-v0/review.json"
)
INTERNAL_V1_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-completion-prd-v0.md"
)
AUTOMATIC_SUPPLY_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
HISTORICAL_DISCOVERY_PATH = REPO_ROOT / "docs/history/decision-work-product-delta-discoverability.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = "lolla.decision_work_real_archive_sidecar_write_plan_review.v0"
EXPECTED_GATE = "proceed_to_real_archive_sidecar_write_adapter"
ALLOWED_FILES = {
    "attachment_status.json",
    "user_receipt.md",
    "agent_handoff_packet.json",
    "safe_supply_summary.json",
    "sidecar_update_packet.json",
    "sidecar_write_receipt.json",
}
PRIVATE_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def test_plan_doc_records_scope_target_preconditions_and_gate() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Real Archive Sidecar Write Plan v0" in text
    assert "plan/review/test gate only" in text
    assert "explicit operator-supplied completed-run" in text
    assert "archive directory" in text
    assert "contain required archive markers or artifacts before write" in text
    assert "operator-confirm-real-archive-write" in text
    assert "The v0 policy is no-overwrite" in text
    assert "real_archive_sidecar_write_completed" in text
    assert "real_archive_sidecar_write_completed_blocked_state" in text
    assert "proceed_to_real_archive_sidecar_write_adapter" in text
    assert "PR219 Real Archive Sidecar Write Adapter v0" in text
    assert "Do not implement PR220 from this plan" in text


def test_review_schema_target_policy_and_preconditions() -> None:
    review = _review()
    target = review["allowed_write_target"]
    preconditions = set(review["required_preconditions"])

    assert review["schema_version"] == EXPECTED_SCHEMA
    assert review["review_metadata"]["plan_only"] is True
    assert review["review_metadata"]["adapter_implemented"] is False
    assert review["review_metadata"]["sidecar_files_written"] is False
    assert review["review_metadata"]["real_archive_mutated"] is False
    assert review["review_metadata"]["historical_archive_mutated"] is False
    assert review["review_metadata"]["runtime_wiring_changed"] is False
    assert review["review_metadata"]["archive_hook_changed"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert target["operator_supplied_target_required"] is True
    assert target["target_must_be_absolute"] is True
    assert target["target_must_exist_before_write"] is True
    assert target["target_must_look_like_completed_run_archive"] is True
    assert target["target_must_contain_archive_markers"] is True
    assert target["repo_source_docs_tests_review_paths_forbidden"] is True
    assert target["existing_decision_work_forbidden_in_v0"] is True
    assert "matching_sidecar_update_packet" in preconditions
    assert "matching_dry_run_result" in preconditions
    assert "operator_confirmation_flag" in preconditions
    assert "resolver_refs_approved_false" in preconditions


def test_review_file_set_statuses_cases_and_receipt_policy() -> None:
    review = _review()
    receipt = review["receipt_policy"]
    statuses = set(review["planned_statuses"])
    cases = {case["case_id"]: case for case in review["expected_case_behavior"]}

    assert set(review["allowed_sidecar_files"]) == ALLOWED_FILES
    assert "real_archive_sidecar_write_completed" in statuses
    assert "real_archive_sidecar_write_completed_blocked_state" in statuses
    assert "blocked_operator_confirmation_missing" in statuses
    assert "blocked_archive_markers_missing" in statuses
    assert "blocked_existing_decision_work_sidecar" in statuses
    assert "blocked_dry_run_mismatch" in statuses
    assert "blocked_privacy_risk" in statuses
    assert "blocked_authority_claim" in statuses
    assert receipt["schema_version"] == (
        "lolla.decision_work_real_archive_sidecar_write_receipt.v0"
    )
    assert receipt["runtime_wiring_changed"] is False
    assert receipt["archive_hook_changed"] is False
    assert receipt["resolver_refs_approved"] is False
    assert receipt["product_proof"] is False
    assert receipt["human_validated"] is False
    assert receipt["answer_quality_scored"] is False
    assert receipt["advice_correctness_validated"] is False
    assert receipt["agent_action_authorized"] is False
    assert receipt["automatic_action_authorized"] is False
    assert (
        cases["launch-public-enterprise-beta"]["expected_status"]
        == "real_archive_sidecar_write_completed"
    )
    assert (
        cases["deploy-assisted-intake-routing"]["expected_status"]
        == "real_archive_sidecar_write_completed_blocked_state"
    )
    assert cases["deploy-assisted-intake-routing"]["runtime_block_preserved"] is True
    assert cases["deploy-assisted-intake-routing"]["user_surface_block_preserved"] is True


def test_review_no_overwrite_and_refusal_rules() -> None:
    review = _review()
    overwrite = review["backup_idempotency_overwrite_policy"]
    blocked = set(review["blocked_or_forbidden_inputs"])
    validation = set(review["validation_requirements"])

    assert overwrite["v0_policy"] == "no_overwrite"
    assert overwrite["existing_decision_work_sidecar_must_block"] is True
    assert overwrite["future_overwrite_requires_separate_plan"] is True
    assert overwrite["pr219_should_implement_no_overwrite_only"] is True
    for item in (
        "missing_archive_markers",
        "unsafe_target_path",
        "repo_source_docs_tests_review_or_plans_path",
        "existing_decision_work_sidecar",
        "sidecar_update_packet_dry_run_mismatch",
        "privacy_private_provider_or_secret_marker",
        "local_absolute_path_leak",
        "resolver_approval_claim",
        "product_proof_claim",
        "human_validation_claim",
        "answer_quality_scoring_claim",
        "advice_correctness_claim",
        "action_authorization_claim",
        "runtime_wiring_attempt",
        "archive_hook_edit_attempt",
    ):
        assert item in blocked
    for item in (
        "missing_operator_confirmation_blocked",
        "missing_archive_markers_blocked",
        "existing_decision_work_sidecar_blocked",
        "packet_dry_run_mismatch_blocked",
        "only_allowed_file_set_written",
        "no_repo_decision_work_sidecar_written",
        "protected_files_untouched",
    ):
        assert item in validation


def test_decision_gate_and_non_claims() -> None:
    review = _review()
    non_claims = set(review["explicit_non_claims"])

    assert review["decision_gate"] == EXPECTED_GATE
    assert review["recommended_next_pr"] == "PR219 Real Archive Sidecar Write Adapter v0"
    for item in (
        "not_a_write_adapter",
        "not_archive_mutation",
        "not_runtime_wiring",
        "not_archive_hook_integration",
        "not_default_on_behavior",
        "not_resolver_approval",
        "not_product_proof",
        "not_human_validation",
        "not_answer_quality_scoring",
        "not_advice_correctness",
        "not_action_authorization",
    ):
        assert item in non_claims


def test_discoverability_docs_reference_pr218() -> None:
    expected = "Decision Work Real Archive Sidecar Write Plan"
    for path in (
        DOC_PATH,
        INTERNAL_V1_PRD,
        AUTOMATIC_SUPPLY_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr218_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            INTERNAL_V1_PRD,
            AUTOMATIC_SUPPLY_PRD,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr218_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        INTERNAL_V1_PRD,
        AUTOMATIC_SUPPLY_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in PRIVATE_MARKERS:
            assert forbidden not in text, (path, forbidden)
