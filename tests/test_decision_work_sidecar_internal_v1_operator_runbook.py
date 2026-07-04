from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-operator-runbook-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-sidecar-internal-v1-operator-runbook-v0/"
    "review.json"
)
PACKAGE_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-real-archive-sidecar-write-package-gate-v0.md"
)
INTERNAL_V1_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-completion-prd-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
REQUIRED_COMMANDS = (
    "scripts/evals/validate_decision_work_generated_interpretation_read.py",
    "scripts/evals/build_decision_work_generated_read_brief_supply.py",
    "scripts/evals/render_decision_work_generated_read_brief.py",
    "scripts/evals/build_decision_work_generated_read_triage_supply.py",
    "scripts/evals/build_decision_work_generated_read_resolver_supply.py",
    "scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py",
    "scripts/evals/dry_run_decision_work_sidecar_write.py",
    "scripts/evals/write_decision_work_real_archive_sidecar.py",
)
REQUIRED_WRITTEN_FILES = (
    "decision_work/attachment_status.json",
    "decision_work/user_receipt.md",
    "decision_work/agent_handoff_packet.json",
    "decision_work/safe_supply_summary.json",
    "decision_work/sidecar_update_packet.json",
    "decision_work/sidecar_write_receipt.json",
)
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_runbook_review_schema_flow_gate_and_metadata() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_sidecar_internal_v1_operator_runbook_review.v0"
    )
    assert len(review["runbook_flow_steps"]) == 12
    assert set(REQUIRED_COMMANDS) <= set(review["cli_commands_documented"])
    assert review["review_metadata"]["mode"] == "docs_tests_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["archive_hook_changed"] is False
    assert review["review_metadata"]["real_archive_mutated"] is False
    assert review["review_metadata"]["historical_archive_mutated"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["review_metadata"]["checked_in_sidecar_outputs_created"] is False
    assert (
        review["decision_gate"]
        == "proceed_to_current_state_limitations_narrative_refresh"
    )
    assert (
        review["recommended_next_pr"]
        == "PR223 Current State / Limitations Narrative Refresh v0"
    )


def test_runbook_documents_commands_artifacts_and_sidecar_files() -> None:
    text = RUNBOOK_DOC.read_text(encoding="utf-8")

    for command in REQUIRED_COMMANDS:
        assert command in text
    for file_ref in REQUIRED_WRITTEN_FILES:
        assert file_ref in text
    for placeholder in (
        "<completed-run-archive-dir>",
        "<generated-read-json>",
        "<safe-output-dir>",
        "<case-id>",
        "<generated-triage-json>",
    ):
        assert placeholder in text
    assert "real_archive_sidecar_write_completed" in text
    assert "real_archive_sidecar_write_completed_blocked_state" in text
    assert "runtime_use_status.status: blocked" in text
    assert "user_surface_status.status: blocked" in text
    assert "blocked/deferred" in text
    assert "existing `decision_work/`" in text


def test_runbook_preserves_non_claims_and_boundaries() -> None:
    text = RUNBOOK_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)
    non_claims = set(review["non_claims_preserved"])

    assert "does not generate interpretation reads" in text
    assert "does not add behavior" in text
    assert "does not prove the advice is correct" in text
    assert "not proof that Lolla improved the decision" in text
    assert "not runtime availability" in text
    assert "must not be treated as safe to deploy" in text
    assert "not_runtime_wiring" in non_claims
    assert "not_resolver_approval" in non_claims
    assert "not_answer_quality_scoring" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_runbook_doc_and_discoverability_references() -> None:
    expected = "Decision Work Sidecar Internal v1 Operator Runbook"
    for path in (
        RUNBOOK_DOC,
        PACKAGE_DOC,
        INTERNAL_V1_PRD,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr222_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            RUNBOOK_DOC,
            REVIEW_PATH,
            PACKAGE_DOC,
            INTERNAL_V1_PRD,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_pr222_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        RUNBOOK_DOC,
        REVIEW_PATH,
        PACKAGE_DOC,
        INTERNAL_V1_PRD,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
