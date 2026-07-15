from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_STATE_DOC = (
    REPO_ROOT / "docs/board/decision-work-sidecar-internal-v1-current-state.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-sidecar-internal-v1-current-state-v0/"
    "review.json"
)
RUNBOOK_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-operator-runbook-v0.md"
)
INTERNAL_V1_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-completion-prd-v0.md"
)
HISTORICAL_DISCOVERY_PATH = REPO_ROOT / "docs/history/decision-work-product-delta-discoverability.md"
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_state_review_schema_claim_gate_and_metadata() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_sidecar_internal_v1_current_state_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_tests_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["archive_hook_changed"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["launch_like_status"] == "real_archive_sidecar_write_completed"
    assert (
        review["deploy_or_high_risk_status"]
        == "real_archive_sidecar_write_completed_blocked_state"
    )
    assert review["decision_gate"] == "decision_work_sidecar_internal_v1_complete"
    assert (
        review["recommended_next_phase"]
        == "Decision Work Sidecar Internal v1 pause / review before automation phase"
    )


def test_current_state_doc_has_clear_internal_v1_claim_and_limits() -> None:
    text = CURRENT_STATE_DOC.read_text(encoding="utf-8")

    assert (
        "Decision Work Sidecar Internal v1 is functional as a command-only, "
        "explicit-operator, no-overwrite sidecar pipeline"
    ) in text
    assert "It can write an auditable Decision Work sidecar" in text
    assert "It preserves caveats and blocked-state outcomes." in text
    assert "It does not prove the advice was correct." in text
    assert "It does not make Lolla automatically better." in text
    assert "It is not default-on runtime behavior." in text
    assert "It is not customer-ready automation." in text
    assert "real_archive_sidecar_write_completed" in text
    assert "real_archive_sidecar_write_completed_blocked_state" in text
    assert "blocked-state sidecars are not failures" in text


def test_current_state_doc_covers_manual_missing_and_future_work() -> None:
    text = CURRENT_STATE_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)

    for item in (
        "automatic semantic generation for arbitrary runs",
        "queue worker or operator runner",
        "resolver approval policy",
        "runtime hook integration",
        "default-off runtime attachment to real generated artifacts",
        "broader case and eval coverage",
        "user-facing UI or receipt",
        "human/product calibration",
    ):
        assert item in text
    assert "automatic_semantic_generation_for_arbitrary_runs" in (
        review["still_manual_or_missing"]
    )
    assert "queue_worker_or_operator_runner" in review["still_manual_or_missing"]
    assert "resolver_approval_policy" in review["still_manual_or_missing"]
    assert "runtime_hook_integration" in review["still_manual_or_missing"]
    assert review["narrative_checks"]["recommends_pause_before_automation"] is True


def test_current_state_doc_and_discoverability_references() -> None:
    expected = "Decision Work Sidecar Internal v1 Current State"
    for path in (
        CURRENT_STATE_DOC,
        RUNBOOK_DOC,
        INTERNAL_V1_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr223_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            CURRENT_STATE_DOC,
            REVIEW_PATH,
            RUNBOOK_DOC,
            INTERNAL_V1_PRD,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_pr223_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        CURRENT_STATE_DOC,
        REVIEW_PATH,
        RUNBOOK_DOC,
        INTERNAL_V1_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
