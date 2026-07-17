from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-offline-operator-runner-plan-v0/"
    "review.json"
)
AUTOMATION_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-prd-v0.md"
)
RUNBOOK_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-operator-runbook-v0.md"
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
EXPECTED_INPUTS = (
    "--completed-run-archive-dir",
    "--generated-read",
    "--generated-triage",
    "--case-id",
    "--safe-output-dir",
    "--operator-confirm-real-archive-write",
    "--write-sidecar",
    "--stop-before-write",
)
EXPECTED_OUTPUTS = (
    "runner_summary.json",
    "intake_result_path",
    "brief_supply_path",
    "rendered_brief_path",
    "triage_supply_path",
    "resolver_supply_path",
    "sidecar_update_packet_path",
    "dry_run_result_path",
    "optional_write_receipt_path",
    "final_status",
    "blocker_reasons",
    "non_claims",
)
RUNNER_STATUSES = (
    "sidecar_ready_for_explicit_write",
    "sidecar_ready_blocked_state",
    "deferred_missing_semantic_read",
    "deferred_missing_triage",
    "blocked_privacy_risk",
    "blocked_source_depth_insufficient",
    "blocked_schema_or_custody_failure",
    "blocked_runtime_or_user_surface_risk",
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


def test_runner_plan_review_schema_inputs_outputs_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_offline_operator_runner_plan_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_tests_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runner_implemented"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["sidecar_written"] is False
    assert review["runner_type"] == "one_shot_offline_operator_runner"
    assert review["runner_decisions"]["command_only"] is True
    assert review["runner_decisions"]["orchestrates_existing_clis"] is True
    assert review["runner_decisions"]["adds_semantic_interpretation"] is False
    assert review["runner_decisions"]["calls_models_or_providers"] is False
    assert review["expected_future_inputs"] == list(EXPECTED_INPUTS)
    assert review["expected_future_outputs"] == list(EXPECTED_OUTPUTS)
    assert review["runner_statuses"] == list(RUNNER_STATUSES)
    assert review["decision_gate"] == "proceed_to_offline_operator_runner_adapter"
    assert review["recommended_next_pr"] == "PR226 Offline Operator Runner Adapter v0"


def test_runner_plan_documents_command_only_runner_contract() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")

    assert "one-shot offline operator runner" in text
    assert "orchestrating existing" in text
    assert "deterministic CLIs" in text
    assert "not a daemon or queue worker" in text
    assert "not runtime wiring" in text
    assert "not semantic interpretation" in text
    assert "not resolver approval" in text
    assert "not default-on behavior" in text
    for value in EXPECTED_INPUTS:
        assert value in text
    for value in (
        "runner_summary.json",
        "intake result",
        "brief supply",
        "rendered generated-read brief",
        "triage supply",
        "resolver supply",
        "sidecar update packet",
        "dry-run result",
    ):
        assert value in text


def test_runner_plan_statuses_write_gate_and_case_behavior() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)

    for status in RUNNER_STATUSES:
        assert status in text
    assert review["write_gating"]["write_sidecar_default_false"] is True
    assert review["write_gating"]["operator_confirmation_required"] is True
    assert review["write_gating"]["no_overwrite"] is True
    assert review["write_gating"]["matching_packet_and_dry_run_required"] is True
    assert review["launch_behavior"]["expected_status_without_write"] == (
        "sidecar_ready_for_explicit_write"
    )
    assert review["deploy_or_high_risk_behavior"]["expected_status_without_write"] == (
        "sidecar_ready_blocked_state"
    )
    assert review["deploy_or_high_risk_behavior"]["runtime_block_preserved"] is True
    assert review["deploy_or_high_risk_behavior"]["user_surface_block_preserved"] is True
    assert "--write-sidecar false" in text
    assert "never overwrite an existing `decision_work/` sidecar" in text


def test_runner_plan_preserves_non_claims_and_refusals() -> None:
    text = PLAN_DOC.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())
    review = _json(REVIEW_PATH)

    for key, value in review["non_claims"].items():
        assert value is False, key
    for phrase in (
        "customer readiness",
        "automatic arbitrary-run correctness",
        "resolver approval",
        "answer quality",
        "product proof",
        "human validation",
        "advice correctness",
        "certification",
        "action authorization",
    ):
        assert phrase in normalized_text
    assert "privacy/private/provider markers" in text
    assert "dry-run and sidecar update packet do not match" in text
    assert "real archive write is requested without explicit confirmation" in text


def test_runner_plan_discoverability_references() -> None:
    expected = "Decision Work Offline Operator Runner Plan"
    for path in (
        PLAN_DOC,
        AUTOMATION_PRD,
        RUNBOOK_DOC,
        AUTOMATIC_SUPPLY_PRD,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr225_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            PLAN_DOC,
            REVIEW_PATH,
            AUTOMATION_PRD,
            RUNBOOK_DOC,
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


def test_pr225_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        PLAN_DOC,
        REVIEW_PATH,
        AUTOMATION_PRD,
        RUNBOOK_DOC,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
