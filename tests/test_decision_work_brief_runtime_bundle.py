from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from engine.system_b.decision_work_brief_runtime_bundle import (
    ATTACHMENT_STATUS_SCHEMA_VERSION,
    DecisionWorkBriefRuntimeBundleInputError,
    build_decision_work_brief_runtime_bundle,
    validate_output_dir,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts/evals/build_decision_work_brief_runtime_bundle.py"
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-bundle-generator-v0.md"
)
LAUNCH_BRIEF = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
)
LAUNCH_ENRICHED = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md"
)
TRIAGE_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-automatic-triage-provisional-read-v0/read.json"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-contract-v0.json"
)
SIDECAR_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-sidecar-v0.json"
)
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _write_completed_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    for name in (
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "extraction.json",
        "result.json",
    ):
        (run_dir / name).write_text(
            json.dumps({"artifact": name, "run_health": "clean"}),
            encoding="utf-8",
        )
    (run_dir / "revised.txt").write_text(
        "Safe revised answer placeholder for fixture use only.",
        encoding="utf-8",
    )


def _read_status(output_dir: Path) -> dict[str, Any]:
    return json.loads(
        (output_dir / "decision_work/attachment_status.json").read_text(
            encoding="utf-8"
        )
    )


def test_manual_bundle_generates_available_bundle_from_safe_inputs(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/launch-public-enterprise-beta/20260627T104146Z_7bfe79"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        brief_markdown_path=LAUNCH_BRIEF,
        enriched_brief_path=LAUNCH_ENRICHED,
        triage_read_path=TRIAGE_READ,
        created_at="2026-07-02T00:00:00Z",
    )

    assert status["schema_version"] == ATTACHMENT_STATUS_SCHEMA_VERSION
    assert status["attachment_state"] == "generated"
    assert status["attachment_mode"] == "manual_post_archive"
    assert status["attachment_metadata"]["input_archive_mutated"] is False
    assert status["blocked_reasons"] == []
    assert status["generated_artifacts"]["decision_work_brief_markdown"] == (
        "decision_work/decision_work_brief.md"
    )
    assert status["generated_artifacts"]["decision_work_brief_enriched_markdown"] == (
        "decision_work/decision_work_brief_enriched.md"
    )
    assert status["generated_artifacts"]["automatic_triage_read"] == (
        "decision_work/automatic_triage_read.json"
    )
    assert (output_dir / "decision_work/user_receipt.md").exists()
    assert (output_dir / "decision_work/decision_work_brief_enriched.md").exists()


def test_manual_bundle_defers_when_no_safe_brief_supplied(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        created_at="2026-07-02T00:00:00Z",
    )

    assert status["attachment_state"] == "deferred"
    assert "safe_rendered_brief_not_supplied" in status["deferred_reasons"]
    receipt = (output_dir / "decision_work/user_receipt.md").read_text(
        encoding="utf-8"
    )
    assert "Decision Work Brief: deferred" in receipt
    assert "not proof that the advice is correct" in receipt


def test_manual_bundle_blocks_missing_required_artifacts(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    run_dir.mkdir(parents=True)

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        brief_markdown_path=LAUNCH_BRIEF,
        created_at="2026-07-02T00:00:00Z",
    )

    assert status["attachment_state"] == "blocked"
    assert any(reason.startswith("missing_required_structured_artifact") for reason in status["blocked_reasons"])
    assert "decision_work_brief_markdown" not in status["generated_artifacts"]


def test_manual_bundle_rejects_output_inside_input_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    _write_completed_run(run_dir)

    with pytest.raises(DecisionWorkBriefRuntimeBundleInputError):
        validate_output_dir(output_dir=run_dir / "decision_work", run_dir=run_dir)


def test_cli_generates_bundle_and_prints_status(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--run-dir",
            str(run_dir),
            "--out",
            str(output_dir),
            "--brief-markdown",
            str(LAUNCH_BRIEF),
            "--enriched-brief",
            str(LAUNCH_ENRICHED),
            "--triage-read",
            str(TRIAGE_READ),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["attachment_state"] == "generated"
    assert _read_status(output_dir)["attachment_state"] == "generated"


def test_status_and_receipt_are_conservative_and_private_safe(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs/case/run"
    output_dir = tmp_path / "bundle-output"
    _write_completed_run(run_dir)

    status = build_decision_work_brief_runtime_bundle(
        run_dir=run_dir,
        output_dir=output_dir,
        brief_markdown_path=LAUNCH_BRIEF,
        enriched_brief_path=LAUNCH_ENRICHED,
        triage_read_path=TRIAGE_READ,
        created_at="2026-07-02T00:00:00Z",
    )
    text = (
        json.dumps(status, sort_keys=True)
        + "\n"
        + (output_dir / "decision_work/user_receipt.md").read_text(encoding="utf-8")
    )

    assert status["custody_flags"]["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert status["custody_flags"][field] is False
    assert "not_agent_action_authorization" in status["non_claims"]
    assert "triage_is_routing_not_scoring" in status["non_claims"]
    for marker in PRIVACY_MARKERS:
        assert marker not in text
    assert str(tmp_path) not in text


def test_bundle_docs_and_contracts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, CONTRACT_PATH, SIDECAR_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
