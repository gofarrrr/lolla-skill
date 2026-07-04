from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PRD_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-prd-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-sidecar-automation-readiness-prd-v0/"
    "review.json"
)
CURRENT_STATE_DOC = (
    REPO_ROOT / "docs/board/decision-work-sidecar-internal-v1-current-state.md"
)
INTERNAL_V1_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-completion-prd-v0.md"
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
TARGET_STATUSES = (
    "sidecar_ready_for_explicit_write",
    "sidecar_ready_blocked_state",
    "deferred_missing_semantic_read",
    "deferred_missing_triage",
    "blocked_privacy_risk",
    "blocked_source_depth_insufficient",
    "blocked_schema_or_custody_failure",
    "blocked_runtime_or_user_surface_risk",
)
ROADMAP_ITEMS = (
    "PR224 Automation Readiness PRD",
    "PR225 Offline Operator Runner Plan",
    "PR226 Offline Operator Runner Adapter",
    "PR227 Runner Fixture Review",
    "PR228 Non-Curated Completed-Run Pilot Plan",
    "PR229 Non-Curated Completed-Run Pilot",
    "PR230 Non-Curated Pilot Review",
    "PR231 Automation Readiness Package Gate",
    "PR232 Receipt / Blocked-State Language Review",
    "optional PR233 Second Non-Curated Pilot",
    "optional PR234 Runtime Hook Integration Plan",
    "optional PR235 Automation Phase Closure / Next Decision Gate",
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


def test_automation_readiness_review_schema_statuses_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_sidecar_automation_readiness_prd_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_tests_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["runner_implemented"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["current_internal_v1_status"]["gate"] == (
        "decision_work_sidecar_internal_v1_complete"
    )
    assert review["automation_readiness_scope"]["not_runtime_automation"] is True
    assert review["automation_readiness_scope"]["queue_worker_allowed"] is False
    assert review["target_statuses"] == list(TARGET_STATUSES)
    assert review["roadmap"] == list(ROADMAP_ITEMS)
    assert review["decision_gate"] == "proceed_to_offline_operator_runner_plan"
    assert review["recommended_next_pr"] == "PR225 Offline Operator Runner Plan v0"


def test_automation_readiness_prd_documents_scope_roadmap_and_bundles() -> None:
    text = PRD_DOC.read_text(encoding="utf-8")

    assert "Decision Work Sidecar Internal v1 is complete" in text
    assert "automation readiness as a conservative offline phase" in text
    assert "Why Automation Readiness, Not Runtime Automation" in text
    assert "Target Outcome For Newly Completed Runs" in text
    for status in TARGET_STATUSES:
        assert status in text
    for item in ROADMAP_ITEMS:
        assert item in text or item.replace("optional ", "Optional ") in text
    for bundle in ("Bundle A", "Bundle B", "Bundle C", "Bundle D", "Optional Bundle E"):
        assert bundle in text
    assert "proceed_to_offline_operator_runner_plan" in text


def test_automation_readiness_prd_preserves_non_goals() -> None:
    text = PRD_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)
    non_goals = set(review["explicit_non_goals"])

    for phrase in (
        "customer readiness",
        "default-on runtime behavior",
        "direct runtime interpretation",
        "runtime model/provider calls",
        "automatic arbitrary-run correctness",
        "resolver approval",
        "answer-quality scoring",
        "product proof",
        "human validation",
        "advice correctness",
        "certification",
        "action authorization",
    ):
        assert phrase in text
    assert "default_on_runtime_behavior" in non_goals
    assert "runtime_model_provider_calls" in non_goals
    assert "resolver_approval" in non_goals
    assert "answer_quality_scoring" in non_goals
    assert "action_authorization" in non_goals


def test_automation_readiness_discoverability_references() -> None:
    expected = "Decision Work Sidecar Automation Readiness PRD"
    for path in (
        PRD_DOC,
        CURRENT_STATE_DOC,
        INTERNAL_V1_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr224_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PRD_DOC,
            REVIEW_PATH,
            CURRENT_STATE_DOC,
            INTERNAL_V1_PRD,
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


def test_pr224_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        PRD_DOC,
        REVIEW_PATH,
        CURRENT_STATE_DOC,
        INTERNAL_V1_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
