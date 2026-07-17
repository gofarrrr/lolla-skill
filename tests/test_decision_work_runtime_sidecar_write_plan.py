from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-runtime-sidecar-write-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-runtime-sidecar-write-plan-v0/review.json"
)
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-update-packet-prewrite-package-gate-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
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


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_review_json_schema_gate_and_metadata() -> None:
    review = _json(REVIEW_PATH)
    metadata = review["review_metadata"]

    assert review["schema_version"] == "lolla.decision_work_runtime_sidecar_write_plan.v0"
    assert metadata["mode"] == "plan_docs_tests_only"
    assert metadata["model_calls"] == 0
    assert metadata["runtime_invoked"] is False
    assert metadata["skill_invoked"] is False
    assert metadata["archive_mutated"] is False
    assert metadata["actual_sidecar_write_performed"] is False
    assert metadata["runtime_wiring_changed"] is False
    assert metadata["resolver_refs_approved"] is False
    assert review["decision_gate"] == "proceed_to_default_off_sidecar_write_dry_run_adapter"
    assert review["recommended_next_pr"] == (
        "PR206 Default-Off Sidecar Write Dry-Run Adapter v0"
    )


def test_plan_status_handling_and_deploy_boundary() -> None:
    review = _json(REVIEW_PATH)
    eligible = {item["status"] for item in review["eligible_packet_statuses"]}
    blocked = set(review["blocked_or_deferred_packet_statuses"])
    deploy = review["deploy_packet_with_runtime_block_handling"]

    assert eligible == {"ready_for_sidecar_update_packet"}
    assert "packet_with_runtime_block" in blocked
    assert "blocked_privacy_risk" in blocked
    assert "blocked_authority_claim" in blocked
    assert "blocked_runtime_write_attempt" in blocked
    assert deploy["normal_available_sidecar_write_allowed"] is False
    assert deploy["blocked_or_deferred_state_only"] is True
    assert deploy["runtime_use_status"] == "blocked"
    assert deploy["user_surface_status"] == "blocked"
    assert deploy["agent_inspection_status"] == "agent_inspection_only"
    assert deploy["domain_compliance_caveats_required"] is True
    assert deploy["deployment_authorization"] is False
    assert deploy["legal_compliance_clinical_clearance"] is False


def test_write_plan_preserves_hard_boundaries() -> None:
    review = _json(REVIEW_PATH)
    resolver = review["resolver_approval_prevention"]
    archive = review["archive_mutation_boundary"]
    runtime = review["runtime_hook_boundary"]

    assert resolver["sidecar_update_packet_is_approved_refs"] is False
    assert resolver["resolver_refs_approved_must_remain_false"] is True
    assert resolver["resolver_refs_marked_usable_must_remain_false"] is True
    assert resolver["candidate_refs_must_be_labeled_candidate_or_proposed"] is True
    assert archive["pr205_mutates_archives"] is False
    assert archive["future_actual_write_requires_separate_implementation_pr"] is True
    assert archive["first_next_step_should_be_dry_run_adapter"] is True
    assert archive["dry_run_writes_decision_work_directory"] is False
    assert runtime["runtime_hook_changed"] is False
    assert runtime["LOLLA_DECISION_WORK_BRIEF_AFTER_ARCHIVE_changed"] is False
    assert runtime["runtime_attachment_default_on"] is False
    assert runtime["runtime_wiring_allowed"] is False
    assert review["semantic_interpretation_not_allowed"] is True
    assert review["actual_sidecar_write_implementation_not_allowed"] is True
    assert review["archive_mutation_forbidden"] is True
    assert review["runtime_wiring_forbidden"] is True
    assert review["resolver_approval_forbidden"] is True


def test_never_copy_and_non_claims_are_conservative() -> None:
    review = _json(REVIEW_PATH)
    never_copy = set(review["never_copy"])
    non_claims = set(review["non_claims"])

    assert "raw_conversation_text" in never_copy
    assert "raw_revised_answer_text" in never_copy
    assert "raw_memo_text" in never_copy
    assert "provider_text" in never_copy
    assert "private_ledgers" in never_copy
    assert "local_absolute_paths" in never_copy
    assert "secrets" in never_copy
    assert "answer_quality_scores" in never_copy
    assert "advice_correctness_claims" in never_copy
    assert "action_authorization" in never_copy
    assert "plan_does_not_write_sidecars" in non_claims
    assert "plan_does_not_mutate_archives" in non_claims
    assert "plan_does_not_wire_runtime" in non_claims
    assert "plan_does_not_approve_resolver_refs" in non_claims
    assert "plan_does_not_score_answer_quality" in non_claims
    assert "plan_does_not_authorize_agent_action" in non_claims


def test_plan_doc_records_questions_boundaries_and_next_pr() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Runtime Sidecar Write Plan v0" in text
    assert "This is docs/review/tests only" in text
    assert "Do not implement PR206" in text
    assert "What Would Be Allowed To Write" in text
    assert "Deploy-Intake Handling" in text
    assert "Never Copy" in text
    assert "Preventing Approved-Ref Confusion" in text
    assert "proceed_to_default_off_sidecar_write_dry_run_adapter" in text
    assert "PR206 Default-Off Sidecar Write Dry-Run Adapter v0" in text
    assert "Do not implement PR206" in text


def test_discoverability_docs_reference_pr205() -> None:
    expected = "Decision Work Runtime Sidecar Write Plan"
    for path in (
        DOC_PATH,
        PACKAGE_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr205_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PACKAGE_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr205_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PACKAGE_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
