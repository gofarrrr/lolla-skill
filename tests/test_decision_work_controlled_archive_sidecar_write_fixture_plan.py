from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-controlled-archive-sidecar-write-fixture-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-controlled-archive-sidecar-write-fixture-plan-v0/review.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR212_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-package-gate-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
EXPECTED_SCHEMA = "lolla.decision_work_controlled_archive_sidecar_write_fixture_plan.v0"
EXPECTED_GATE = "proceed_to_controlled_archive_sidecar_write_fixture_adapter"
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


def test_review_schema_boundary_and_gate() -> None:
    review = _review()
    boundary = review["boundary_definition"]

    assert review["schema_version"] == EXPECTED_SCHEMA
    assert review["review_metadata"]["adapter_implemented"] is False
    assert review["review_metadata"]["fixture_files_written"] is False
    assert review["review_metadata"]["real_archive_mutated"] is False
    assert review["review_metadata"]["historical_archive_mutated"] is False
    assert review["review_metadata"]["runtime_wiring_changed"] is False
    assert review["review_metadata"]["archive_hook_changed"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert boundary["to_layer"] == "synthetic_archive_shaped_fixture_dirs"
    assert boundary["real_archive_dirs_remain_forbidden"] is True
    assert boundary["historical_archive_mutation_forbidden"] is True
    assert boundary["runtime_wiring_forbidden"] is True
    assert boundary["archive_hook_edit_forbidden"] is True
    assert boundary["resolver_approval_forbidden"] is True
    assert review["decision_gate"] == EXPECTED_GATE
    assert (
        review["recommended_next_pr"]
        == "PR214 Controlled Archive Sidecar Write Fixture Adapter v0"
    )


def test_planned_statuses_case_behavior_and_file_set() -> None:
    review = _review()
    statuses = set(review["planned_statuses"])
    cases = {case["case_id"]: case for case in review["expected_case_behavior"]}

    assert {
        "fixture_write_completed",
        "fixture_write_completed_blocked_state",
        "blocked_real_archive_path",
        "blocked_repo_path",
        "blocked_existing_archive_path",
        "blocked_target_path_unsafe",
        "blocked_packet_not_write_eligible",
        "blocked_dry_run_missing",
        "blocked_dry_run_mismatch",
        "blocked_privacy_risk",
        "blocked_authority_claim",
        "failed_closed",
    } <= statuses
    assert set(review["allowed_sidecar_files"]) == ALLOWED_FILES
    assert (
        cases["launch-public-enterprise-beta"]["expected_status"]
        == "fixture_write_completed"
    )
    assert cases["launch-public-enterprise-beta"]["runtime_ready_claim_allowed"] is False
    assert (
        cases["deploy-assisted-intake-routing"]["expected_status"]
        == "fixture_write_completed_blocked_state"
    )
    assert cases["deploy-assisted-intake-routing"]["runtime_block_preserved"] is True
    assert cases["deploy-assisted-intake-routing"]["user_surface_block_preserved"] is True
    for case in cases.values():
        assert case["resolver_refs_approved"] is False


def test_path_safety_and_required_receipt_flags_fail_closed() -> None:
    review = _review()
    path_safety = review["path_safety_requirements"]
    flags = review["required_receipt_flags"]
    blocked = set(review["blocked_or_forbidden_inputs"])

    assert path_safety["target_fixture_archive_dir_must_be_absolute"] is True
    assert (
        path_safety[
            "target_fixture_archive_dir_must_be_under_safe_temp_or_operator_output_root"
        ]
        is True
    )
    assert path_safety["target_fixture_archive_dir_must_not_be_inside_repo"] is True
    assert path_safety["target_fixture_archive_dir_must_not_be_real_archive"] is True
    assert (
        path_safety["target_fixture_archive_dir_must_not_be_existing_historical_archive"]
        is True
    )
    assert path_safety["target_fixture_archive_dir_must_not_be_runtime_path"] is True
    assert path_safety["target_fixture_archive_dir_must_not_escape_supplied_root"] is True
    for field in (
        "real_archive_mutated",
        "historical_archive_mutated",
        "runtime_wiring_changed",
        "archive_hook_changed",
        "resolver_refs_approved",
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "advice_correctness_claimed",
        "agent_action_authorized",
        "automatic_action_authorized",
    ):
        assert flags[field] is False
    assert "real_archive_path" in blocked
    assert "existing_historical_archive_path" in blocked
    assert "repo_path" in blocked
    assert "runtime_path" in blocked
    assert "dry_run_packet_mismatch" in blocked
    assert "resolver_approval_claim" in blocked
    assert "proof_claim" in blocked
    assert "action_authorization_claim" in blocked


def test_doc_records_plan_scope_boundary_and_stop_line() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Controlled Archive Sidecar Write Fixture Plan v0" in text
    assert "plan/review/test gate only" in text
    assert "synthetic archive-shaped fixture" in text
    assert "real completed-run archive" in text
    assert "fixture_write_completed" in text
    assert "fixture_write_completed_blocked_state" in text
    assert "proceed_to_controlled_archive_sidecar_write_fixture_adapter" in text
    assert "PR214 Controlled Archive Sidecar Write Fixture Adapter v0" in text
    assert "Do not implement real archive writes" in text


def test_discoverability_docs_reference_pr213() -> None:
    expected = "Decision Work Controlled Archive Sidecar Write Fixture Plan"
    for path in (
        DOC_PATH,
        PR212_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr213_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR212_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr213_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR212_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in PRIVATE_MARKERS:
            assert forbidden not in text, (path, forbidden)
