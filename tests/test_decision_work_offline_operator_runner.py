from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_offline_operator_runner import (
    BLOCKED_PRIVACY_RISK,
    BLOCKED_SCHEMA_OR_CUSTODY_FAILURE,
    DEFERRED_MISSING_SEMANTIC_READ,
    DEFERRED_MISSING_TRIAGE,
    OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION,
    SIDECAR_READY_BLOCKED_STATE,
    SIDECAR_READY_FOR_EXPLICIT_WRITE,
    STOPPED_BEFORE_EXPLICIT_WRITE,
    render_offline_operator_runner_summary_json,
    run_decision_work_offline_operator,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "engine/system_b/decision_work_offline_operator_runner.py"
SCRIPT_PATH = REPO_ROOT / "scripts/evals/run_decision_work_offline_operator.py"
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-operator-runner-plan-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-prd-v0.md"
)
AUTOMATIC_SUPPLY_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
LAUNCH_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
LAUNCH_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/triage.json"
)
DEPLOY_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0/read.json"
)
DEPLOY_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-triage-pilot-v0/triage.json"
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


def _archive_dir(tmp_path: Path, name: str = "archive") -> Path:
    path = tmp_path / name / "completed-run"
    path.mkdir(parents=True)
    return path


def _safe_output(tmp_path: Path, name: str = "runner-output") -> Path:
    return tmp_path / name


def _run_launch(tmp_path: Path, **kwargs: Any) -> dict[str, Any]:
    return run_decision_work_offline_operator(
        completed_run_archive_dir=_archive_dir(tmp_path),
        generated_read_path=LAUNCH_READ,
        generated_triage_path=LAUNCH_TRIAGE,
        case_id="launch-public-enterprise-beta",
        safe_output_dir=_safe_output(tmp_path),
        created_at="2026-07-04T00:00:00Z",
        **kwargs,
    )


def test_launch_path_reaches_sidecar_ready_without_write(tmp_path: Path) -> None:
    summary = _run_launch(tmp_path)

    assert summary["schema_version"] == OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION
    assert summary["final_status"] == SIDECAR_READY_FOR_EXPLICIT_WRITE
    assert summary["case_id"] == "launch-public-enterprise-beta"
    assert summary["completed_steps"] == [
        "generated_read_intake",
        "brief_supply",
        "rendered_brief",
        "triage_supply",
        "resolver_supply",
        "sidecar_update_packet",
        "sidecar_write_dry_run",
    ]
    assert summary["skipped_steps"] == []
    assert summary["stopped_at"] == "dry_run_complete"
    assert summary["write_attempted"] is False
    assert summary["actual_sidecar_write_performed"] is False
    assert summary["archive_mutated"] is False
    assert summary["historical_archive_mutated"] is False
    assert summary["resolver_refs_approved"] is False
    assert summary["runtime_wiring_changed"] is False
    assert summary["can_authorize_agent_action"] is False
    assert summary["can_be_used_as_quality_label"] is False
    assert "manual_explicit_write_available_as_next_step" in (
        summary["operator_attention_items"]
    )
    for artifact in (
        "intake",
        "brief_supply",
        "rendered_brief",
        "triage_supply",
        "resolver_supply",
        "sidecar_update_packet",
        "dry_run",
    ):
        assert artifact in summary["artifact_refs"]
    assert not (tmp_path / "decision_work").exists()


def test_deploy_path_preserves_blocked_state_without_write(tmp_path: Path) -> None:
    summary = run_decision_work_offline_operator(
        completed_run_archive_dir=_archive_dir(tmp_path),
        generated_read_path=DEPLOY_READ,
        generated_triage_path=DEPLOY_TRIAGE,
        case_id="deploy-assisted-intake-routing",
        safe_output_dir=_safe_output(tmp_path),
        created_at="2026-07-04T00:00:00Z",
    )

    assert summary["final_status"] == SIDECAR_READY_BLOCKED_STATE
    assert summary["runtime_use_status"]["status"] == "blocked"
    assert summary["user_surface_status"]["status"] == "blocked"
    assert "runtime_or_user_surface_block_preserved" in (
        summary["operator_attention_items"]
    )
    assert summary["actual_sidecar_write_performed"] is False
    assert summary["archive_mutated"] is False
    assert summary["resolver_refs_approved"] is False


def test_missing_generated_read_defers_without_running_chain(tmp_path: Path) -> None:
    summary = run_decision_work_offline_operator(
        completed_run_archive_dir=_archive_dir(tmp_path),
        generated_read_path=tmp_path / "missing_read.json",
        generated_triage_path=LAUNCH_TRIAGE,
        case_id="launch-public-enterprise-beta",
        safe_output_dir=_safe_output(tmp_path),
        created_at="2026-07-04T00:00:00Z",
    )

    assert summary["final_status"] == DEFERRED_MISSING_SEMANTIC_READ
    assert summary["missing_required_inputs"] == ["generated_read"]
    assert summary["deferred_reasons"] == ["generated_read_missing"]
    assert summary["completed_steps"] == []
    assert "generated_read_intake" in summary["skipped_steps"]


def test_missing_generated_triage_defers_without_inference(tmp_path: Path) -> None:
    summary = run_decision_work_offline_operator(
        completed_run_archive_dir=_archive_dir(tmp_path),
        generated_read_path=LAUNCH_READ,
        generated_triage_path=tmp_path / "missing_triage.json",
        case_id="launch-public-enterprise-beta",
        safe_output_dir=_safe_output(tmp_path),
        created_at="2026-07-04T00:00:00Z",
    )

    assert summary["final_status"] == DEFERRED_MISSING_TRIAGE
    assert summary["missing_required_inputs"] == ["generated_triage"]
    assert summary["deferred_reasons"] == ["generated_triage_missing"]
    assert summary["completed_steps"] == []
    assert "resolver_supply" in summary["skipped_steps"]


def test_rejected_intake_blocks_schema_or_custody(tmp_path: Path) -> None:
    read = copy.deepcopy(_json(LAUNCH_READ))
    read["custody_flags"]["product_proof"] = True
    read_path = tmp_path / "product_proof_read.json"
    read_path.write_text(json.dumps(read, indent=2), encoding="utf-8")

    summary = run_decision_work_offline_operator(
        completed_run_archive_dir=_archive_dir(tmp_path),
        generated_read_path=read_path,
        generated_triage_path=LAUNCH_TRIAGE,
        case_id="launch-public-enterprise-beta",
        safe_output_dir=_safe_output(tmp_path),
        created_at="2026-07-04T00:00:00Z",
    )

    assert summary["final_status"] == BLOCKED_SCHEMA_OR_CUSTODY_FAILURE
    assert "product_proof_claimed" in summary["blocker_reasons"]
    assert any(
        reason.startswith("intake_not_accepted:")
        for reason in summary["blocker_reasons"]
    )
    assert "generated_read_intake" in summary["completed_steps"]
    assert "brief_supply" in summary["skipped_steps"]


def test_privacy_marker_and_local_absolute_path_block_before_chain(
    tmp_path: Path,
) -> None:
    read = copy.deepcopy(_json(LAUNCH_READ))
    read["operator_note"] = "SEC" + "RET"
    privacy_read = tmp_path / "privacy_read.json"
    privacy_read.write_text(json.dumps(read), encoding="utf-8")

    privacy = run_decision_work_offline_operator(
        completed_run_archive_dir=_archive_dir(tmp_path, "privacy_archive"),
        generated_read_path=privacy_read,
        generated_triage_path=LAUNCH_TRIAGE,
        case_id="launch-public-enterprise-beta",
        safe_output_dir=_safe_output(tmp_path, "privacy_output"),
        created_at="2026-07-04T00:00:00Z",
    )

    read["operator_note"] = "/" + "Users" + "/example/private"
    local_path_read = tmp_path / "local_path_read.json"
    local_path_read.write_text(json.dumps(read), encoding="utf-8")
    local_path = run_decision_work_offline_operator(
        completed_run_archive_dir=_archive_dir(tmp_path, "local_path_archive"),
        generated_read_path=local_path_read,
        generated_triage_path=LAUNCH_TRIAGE,
        case_id="launch-public-enterprise-beta",
        safe_output_dir=_safe_output(tmp_path, "local_path_output"),
        created_at="2026-07-04T00:00:00Z",
    )

    assert privacy["final_status"] == BLOCKED_PRIVACY_RISK
    assert privacy["blocker_reasons"] == ["privacy_marker_detected"]
    assert privacy["completed_steps"] == []
    assert local_path["final_status"] == BLOCKED_PRIVACY_RISK
    assert local_path["blocker_reasons"] == ["local_absolute_path_detected"]
    assert local_path["completed_steps"] == []


def test_write_attempt_stops_before_explicit_write(tmp_path: Path) -> None:
    summary = _run_launch(tmp_path, write_sidecar=True)

    assert summary["final_status"] == STOPPED_BEFORE_EXPLICIT_WRITE
    assert summary["write_attempted"] is False
    assert summary["actual_sidecar_write_performed"] is False
    assert summary["archive_mutated"] is False
    assert summary["historical_archive_mutated"] is False
    assert "write_mode_not_supported_in_runner_v0" in summary["blocker_reasons"]
    assert "explicit_write_not_performed_by_runner_v0" in (
        summary["operator_attention_items"]
    )


def test_cli_writes_runner_summary_json(tmp_path: Path) -> None:
    out = tmp_path / "runner_summary.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--completed-run-archive-dir",
            str(_archive_dir(tmp_path)),
            "--generated-read",
            str(LAUNCH_READ),
            "--generated-triage",
            str(LAUNCH_TRIAGE),
            "--case-id",
            "launch-public-enterprise-beta",
            "--safe-output-dir",
            str(_safe_output(tmp_path)),
            "--out",
            str(out),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = _json(out)
    assert payload["final_status"] == SIDECAR_READY_FOR_EXPLICIT_WRITE
    assert payload["actual_sidecar_write_performed"] is False
    assert payload["archive_mutated"] is False


def test_runner_output_is_valid_json() -> None:
    summary = {
        "schema_version": OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION,
        "final_status": SIDECAR_READY_FOR_EXPLICIT_WRITE,
    }

    payload = render_offline_operator_runner_summary_json(summary, pretty=True)

    assert json.loads(payload)["schema_version"] == OFFLINE_OPERATOR_RUNNER_SCHEMA_VERSION


def test_pr226_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            PLAN_DOC,
            PRD_PATH,
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


def test_pr226_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        MODULE_PATH,
        SCRIPT_PATH,
        PLAN_DOC,
        PRD_PATH,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
