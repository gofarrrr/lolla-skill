from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_explicit_operator_sidecar_write import (
    EXPLICIT_OPERATOR_WRITE_RECEIPT_SCHEMA_VERSION,
    WRITE_COMPLETED_BLOCKED_STATUS,
    WRITE_COMPLETED_STATUS,
    build_explicit_operator_sidecar_write,
)
from engine.system_b.decision_work_generated_read_brief_supply import (
    build_generated_read_brief_supply,
    render_generated_read_brief_supply_json,
)
from engine.system_b.decision_work_generated_read_resolver_supply import (
    build_generated_read_resolver_supply,
    render_generated_read_resolver_supply_json,
)
from engine.system_b.decision_work_generated_read_triage_supply import (
    build_generated_read_triage_supply,
    render_generated_read_triage_supply_json,
)
from engine.system_b.decision_work_resolver_candidate_sidecar_update_packet import (
    build_resolver_candidate_sidecar_update_packet,
    render_resolver_candidate_sidecar_update_packet_json,
)
from engine.system_b.decision_work_sidecar_write_dry_run import (
    build_sidecar_write_dry_run,
    render_sidecar_write_dry_run_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT / "engine/system_b/decision_work_explicit_operator_sidecar_write.py"
)
SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/write_decision_work_sidecar_explicit_operator.py"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-adapter-v0.md"
)
CONTRACT_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-runtime-sidecar-write-contract-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
LAUNCH_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
LAUNCH_INTAKE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json"
)
LAUNCH_RENDERED = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
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
DEPLOY_INTAKE = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0/intake.json"
)
DEPLOY_RENDERED = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md"
)
DEPLOY_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-triage-pilot-v0/triage.json"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
ALLOWED_FILES = {
    "attachment_status.json",
    "user_receipt.md",
    "agent_handoff_packet.json",
    "safe_supply_summary.json",
    "sidecar_update_packet.json",
    "sidecar_write_receipt.json",
}
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


def _write_json(tmp_path: Path, name: str, payload: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sidecar_update_and_dry_run_paths(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path = LAUNCH_READ,
    intake_path: Path = LAUNCH_INTAKE,
    rendered_path: Path = LAUNCH_RENDERED,
    triage_path: Path = LAUNCH_TRIAGE,
) -> tuple[Path, Path]:
    brief_supply = build_generated_read_brief_supply(
        read_path=read_path,
        intake_path=intake_path,
        created_at="2026-07-03T00:00:00Z",
    )
    brief_supply_path = tmp_path / f"{name}_brief_supply.json"
    brief_supply_path.write_text(
        render_generated_read_brief_supply_json(brief_supply, pretty=True),
        encoding="utf-8",
    )
    triage_supply = build_generated_read_triage_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=rendered_path,
        created_at="2026-07-03T00:00:00Z",
    )
    triage_supply_path = tmp_path / f"{name}_triage_supply.json"
    triage_supply_path.write_text(
        render_generated_read_triage_supply_json(triage_supply, pretty=True),
        encoding="utf-8",
    )
    resolver_supply = build_generated_read_resolver_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=rendered_path,
        triage_supply_path=triage_supply_path,
        triage_path=triage_path,
        created_at="2026-07-03T00:00:00Z",
    )
    resolver_supply_path = tmp_path / f"{name}_resolver_supply.json"
    resolver_supply_path.write_text(
        render_generated_read_resolver_supply_json(resolver_supply, pretty=True),
        encoding="utf-8",
    )
    sidecar_update_packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=resolver_supply_path,
        source_resolver_supply_ref=f"tmp/{name}_resolver_supply.json",
        created_at="2026-07-03T00:00:00Z",
    )
    packet_path = tmp_path / f"{name}_sidecar_update_packet.json"
    packet_path.write_text(
        render_resolver_candidate_sidecar_update_packet_json(
            sidecar_update_packet,
            pretty=True,
        ),
        encoding="utf-8",
    )
    dry_run = build_sidecar_write_dry_run(
        sidecar_update_packet_path=packet_path,
        source_sidecar_update_packet_ref=f"tmp/{name}_sidecar_update_packet.json",
        preview_dir=tmp_path / f"{name}_preview",
        write_preview=True,
        created_at="2026-07-03T00:00:00Z",
    )
    dry_run_path = tmp_path / f"{name}_dry_run.json"
    dry_run_path.write_text(
        render_sidecar_write_dry_run_json(dry_run, pretty=True),
        encoding="utf-8",
    )
    return packet_path, dry_run_path


def test_launch_packet_writes_fixture_only_sidecar_files(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(
        tmp_path,
        name="launch",
    )
    target = tmp_path / "launch_fixture" / "decision_work"

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=target,
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["schema_version"] == EXPLICIT_OPERATOR_WRITE_RECEIPT_SCHEMA_VERSION
    assert receipt["write_status"] == WRITE_COMPLETED_STATUS
    assert receipt["blocker_reasons"] == []
    assert set(receipt["files_written"]) == ALLOWED_FILES
    assert receipt["operator_explicit_write_required"] is True
    assert receipt["fixture_only"] is True
    assert receipt["actual_sidecar_write_performed"] is True
    assert receipt["real_archive_mutated"] is False
    assert receipt["historical_archive_mutated"] is False
    assert receipt["runtime_wiring_changed"] is False
    assert receipt["resolver_refs_approved"] is False
    assert receipt["can_authorize_agent_action"] is False
    assert receipt["can_be_used_as_quality_label"] is False
    assert {path.name for path in target.iterdir()} == ALLOWED_FILES
    written_receipt = _json(target / "sidecar_write_receipt.json")
    assert written_receipt["write_status"] == WRITE_COMPLETED_STATUS
    assert written_receipt["fixture_only"] is True
    assert written_receipt["real_archive_mutated"] is False


def test_deploy_packet_writes_blocked_state_fixture_only(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )
    target = tmp_path / "deploy_fixture" / "decision_work"

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=target,
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["write_status"] == WRITE_COMPLETED_BLOCKED_STATUS
    assert receipt["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    attachment = _json(target / "attachment_status.json")
    assert attachment["runtime_use_status"]["status"] == "blocked"
    assert attachment["user_surface_status"]["status"] == "blocked"
    assert attachment["actual_sidecar_write_performed"] is True
    assert attachment["real_archive_mutated"] is False
    assert attachment["historical_archive_mutated"] is False
    assert attachment["resolver_refs_approved"] is False


def test_real_archive_looking_target_is_blocked(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    target = tmp_path / "archives" / "run-1" / "decision_work"

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=target,
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["write_status"] == "blocked_real_archive_path"
    assert "target_path_targets_real_archive" in receipt["blocker_reasons"]
    assert receipt["files_written"] == []
    assert not target.exists()
    assert receipt["actual_sidecar_write_performed"] is False


def test_target_inside_repo_is_blocked(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    target = REPO_ROOT / "tmp_fixture" / "decision_work"

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=target,
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["write_status"] == "blocked_target_path_unsafe"
    assert "target_inside_repository" in receipt["blocker_reasons"]
    assert not target.exists()


def test_missing_dry_run_is_blocked(tmp_path: Path) -> None:
    packet_path, _dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=tmp_path / "missing_dry_run.json",
        target_sidecar_dir=tmp_path / "fixture" / "decision_work",
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["write_status"] == "blocked_dry_run_missing"
    assert "dry_run_result_missing" in receipt["blocker_reasons"]
    assert receipt["actual_sidecar_write_performed"] is False


def test_mismatched_dry_run_and_packet_are_blocked(tmp_path: Path) -> None:
    launch_packet, _launch_dry = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    _deploy_packet, deploy_dry = _sidecar_update_and_dry_run_paths(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=launch_packet,
        dry_run_result_path=deploy_dry,
        target_sidecar_dir=tmp_path / "fixture" / "decision_work",
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["write_status"] == "blocked_dry_run_not_matching_packet"
    assert "dry_run_status_does_not_match_packet" in receipt["blocker_reasons"]
    assert receipt["files_written"] == []


def test_authority_proof_scoring_and_action_claims_are_blocked(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    payload = _json(packet_path)
    payload["downstream_allowed"]["resolver_refs_approved"] = True
    payload["custody_flags"]["product_proof"] = True
    bad_packet = _write_json(tmp_path, "authority_packet.json", payload)

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=bad_packet,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=tmp_path / "fixture" / "decision_work",
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["write_status"] == "blocked_authority_claim"
    assert "authority_claim_detected" in receipt["blocker_reasons"]
    assert receipt["resolver_refs_approved"] is False
    assert receipt["can_be_used_as_quality_label"] is False


def test_privacy_markers_are_blocked(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    payload = _json(packet_path)
    payload["privacy_summary"]["local_absolute_path_detected"] = True
    bad_packet = _write_json(tmp_path, "privacy_packet.json", payload)

    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=bad_packet,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=tmp_path / "fixture" / "decision_work",
        created_at="2026-07-03T00:00:00Z",
    )

    assert receipt["write_status"] == "blocked_privacy_risk"
    assert "local_absolute_path_detected" in receipt["blocker_reasons"]
    assert receipt["files_written"] == []


def test_cli_writes_receipt_and_fixture_files(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    target = tmp_path / "cli_fixture" / "decision_work"
    output = tmp_path / "receipt.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--sidecar-update-packet",
            str(packet_path),
            "--dry-run-result",
            str(dry_run_path),
            "--target-sidecar-dir",
            str(target),
            "--out",
            str(output),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    receipt = _json(output)
    assert receipt["write_status"] == WRITE_COMPLETED_STATUS
    assert set(receipt["files_written"]) == ALLOWED_FILES
    assert (target / "sidecar_write_receipt.json").exists()
    assert not (tmp_path / "archives").exists()


def test_cli_refuses_receipt_output_under_decision_work(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    target = tmp_path / "cli_fixture" / "decision_work"
    output = tmp_path / "receipt_sidecar" / "decision_work" / "receipt.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--sidecar-update-packet",
            str(packet_path),
            "--dry-run-result",
            str(dry_run_path),
            "--target-sidecar-dir",
            str(target),
            "--out",
            str(output),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 2
    assert "receipt output must not target an archive or decision_work sidecar path" in (
        completed.stderr
    )
    assert not output.exists()


def test_source_artifacts_are_not_modified(tmp_path: Path) -> None:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(tmp_path, name="launch")
    packet_before = packet_path.read_text(encoding="utf-8")
    dry_before = dry_run_path.read_text(encoding="utf-8")

    build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=tmp_path / "fixture" / "decision_work",
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet_path.read_text(encoding="utf-8") == packet_before
    assert dry_run_path.read_text(encoding="utf-8") == dry_before


def test_adapter_doc_and_discoverability_docs_reference_pr210() -> None:
    expected = "Decision Work Explicit Operator Sidecar Write Adapter"
    for path in (
        DOC_PATH,
        CONTRACT_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr210_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            CONTRACT_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr210_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        MODULE_PATH,
        SCRIPT_PATH,
        DOC_PATH,
        CONTRACT_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
