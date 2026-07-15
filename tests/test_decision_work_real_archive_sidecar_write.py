from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

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
from engine.system_b.decision_work_real_archive_sidecar_write import (
    REAL_ARCHIVE_SIDECAR_WRITE_RECEIPT_SCHEMA_VERSION,
    REAL_ARCHIVE_WRITE_COMPLETED_BLOCKED_STATUS,
    REAL_ARCHIVE_WRITE_COMPLETED_STATUS,
    build_real_archive_sidecar_write,
    render_real_archive_sidecar_write_json,
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
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-real-archive-sidecar-write-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-real-archive-sidecar-write-plan-v0.md"
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
ALLOWED_WRITTEN_FILES = {
    "decision_work/attachment_status.json",
    "decision_work/user_receipt.md",
    "decision_work/agent_handoff_packet.json",
    "decision_work/safe_supply_summary.json",
    "decision_work/sidecar_update_packet.json",
    "decision_work/sidecar_write_receipt.json",
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_and_dry_run(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path,
    intake_path: Path,
    rendered_path: Path,
    triage_path: Path,
) -> tuple[Path, Path]:
    brief_supply = build_generated_read_brief_supply(
        read_path=read_path,
        intake_path=intake_path,
        created_at="2026-07-04T00:00:00Z",
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
        created_at="2026-07-04T00:00:00Z",
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
        created_at="2026-07-04T00:00:00Z",
    )
    resolver_supply_path = tmp_path / f"{name}_resolver_supply.json"
    resolver_supply_path.write_text(
        render_generated_read_resolver_supply_json(resolver_supply, pretty=True),
        encoding="utf-8",
    )
    sidecar_update_packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=resolver_supply_path,
        source_resolver_supply_ref=f"tmp/{name}_resolver_supply.json",
        created_at="2026-07-04T00:00:00Z",
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
        created_at="2026-07-04T00:00:00Z",
    )
    dry_run_path = tmp_path / f"{name}_dry_run.json"
    dry_run_path.write_text(
        render_sidecar_write_dry_run_json(dry_run, pretty=True),
        encoding="utf-8",
    )
    return packet_path, dry_run_path


def _archive_dir(tmp_path: Path, name: str) -> Path:
    archive_dir = tmp_path / "archive" / "cases" / f"{name}-completed-run"
    archive_dir.mkdir(parents=True)
    (archive_dir / "agent_result.json").write_text("{}", encoding="utf-8")
    (archive_dir / "reasoning_trace.json").write_text("{}", encoding="utf-8")
    (archive_dir / "evaluation.json").write_text("{}", encoding="utf-8")
    (archive_dir / "memo.md").write_text("memo\n", encoding="utf-8")
    return archive_dir


def _write_case(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path,
    intake_path: Path,
    rendered_path: Path,
    triage_path: Path,
) -> tuple[dict[str, Any], Path]:
    packet_path, dry_run_path = _packet_and_dry_run(
        tmp_path,
        name=name,
        read_path=read_path,
        intake_path=intake_path,
        rendered_path=rendered_path,
        triage_path=triage_path,
    )
    archive_dir = _archive_dir(tmp_path, name)
    receipt = build_real_archive_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=True,
        created_at="2026-07-04T00:00:00Z",
    )
    return receipt, archive_dir


def test_launch_and_deploy_write_real_archive_sidecars_in_synthetic_archives(
    tmp_path: Path,
) -> None:
    launch, launch_dir = _write_case(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    deploy, deploy_dir = _write_case(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    assert launch["schema_version"] == REAL_ARCHIVE_SIDECAR_WRITE_RECEIPT_SCHEMA_VERSION
    assert deploy["schema_version"] == REAL_ARCHIVE_SIDECAR_WRITE_RECEIPT_SCHEMA_VERSION
    assert launch["real_archive_write_status"] == REAL_ARCHIVE_WRITE_COMPLETED_STATUS
    assert deploy["real_archive_write_status"] == REAL_ARCHIVE_WRITE_COMPLETED_BLOCKED_STATUS
    assert set(launch["files_written"]) == ALLOWED_WRITTEN_FILES
    assert set(deploy["files_written"]) == ALLOWED_WRITTEN_FILES
    assert {path.name for path in (launch_dir / "decision_work").iterdir()} == {
        Path(item).name for item in ALLOWED_WRITTEN_FILES
    }
    assert {path.name for path in (deploy_dir / "decision_work").iterdir()} == {
        Path(item).name for item in ALLOWED_WRITTEN_FILES
    }
    for receipt in (launch, deploy):
        assert receipt["actual_sidecar_write_performed"] is True
        assert receipt["real_archive_mutated"] is True
        assert receipt["historical_archive_mutated"] is True
        assert receipt["archive_hook_changed"] is False
        assert receipt["runtime_wiring_changed"] is False
        assert receipt["resolver_refs_approved"] is False
        assert receipt["product_proof"] is False
        assert receipt["human_validated"] is False
        assert receipt["answer_quality_scored"] is False
        assert receipt["advice_correctness_validated"] is False


def test_deploy_write_preserves_blocked_runtime_and_user_surface(
    tmp_path: Path,
) -> None:
    deploy, deploy_dir = _write_case(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )
    attachment = _json(deploy_dir / "decision_work" / "attachment_status.json")

    assert deploy["real_archive_write_status"] == REAL_ARCHIVE_WRITE_COMPLETED_BLOCKED_STATUS
    assert deploy["runtime_use_status"]["status"] == "blocked"
    assert deploy["user_surface_status"]["status"] == "blocked"
    assert attachment["runtime_use_status"]["status"] == "blocked"
    assert attachment["user_surface_status"]["status"] == "blocked"
    assert attachment["real_archive_mutated"] is True
    assert attachment["historical_archive_mutated"] is True
    assert attachment["runtime_wiring_changed"] is False
    assert attachment["resolver_refs_approved"] is False


def test_confirmation_markers_existing_sidecar_and_repo_paths_are_blocked(
    tmp_path: Path,
) -> None:
    packet_path, dry_run_path = _packet_and_dry_run(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    archive_dir = _archive_dir(tmp_path, "launch")
    missing_markers = tmp_path / "archive" / "cases" / "missing-markers-run"
    missing_markers.mkdir(parents=True)
    existing_sidecar = _archive_dir(tmp_path, "existing-sidecar")
    (existing_sidecar / "decision_work").mkdir()
    repo_path = REPO_ROOT / "archive" / "cases" / "repo-run"

    no_confirm = build_real_archive_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=False,
    )
    missing = build_real_archive_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_archive_dir=missing_markers,
        operator_confirm_real_archive_write=True,
    )
    existing = build_real_archive_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_archive_dir=existing_sidecar,
        operator_confirm_real_archive_write=True,
    )
    repo = build_real_archive_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_archive_dir=repo_path,
        operator_confirm_real_archive_write=True,
    )

    assert no_confirm["real_archive_write_status"] == "blocked_operator_confirmation_missing"
    assert missing["real_archive_write_status"] == "blocked_archive_markers_missing"
    assert existing["real_archive_write_status"] == "blocked_existing_decision_work_sidecar"
    assert repo["real_archive_write_status"] == "blocked_repo_path"
    assert not (missing_markers / "decision_work").exists()
    assert not (repo_path / "decision_work").exists()


def test_mismatched_missing_privacy_and_authority_inputs_are_blocked(
    tmp_path: Path,
) -> None:
    launch_packet, launch_dry = _packet_and_dry_run(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    _deploy_packet, deploy_dry = _packet_and_dry_run(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )
    archive_dir = _archive_dir(tmp_path, "blocked")
    privacy_packet = tmp_path / "privacy_packet.json"
    payload = _json(launch_packet)
    payload["notes"] = "SEC" + "RET"
    privacy_packet.write_text(json.dumps(payload), encoding="utf-8")
    authority_packet = tmp_path / "authority_packet.json"
    payload = _json(launch_packet)
    payload["resolver_refs_approved"] = True
    authority_packet.write_text(json.dumps(payload), encoding="utf-8")

    missing = build_real_archive_sidecar_write(
        sidecar_update_packet_path=launch_packet,
        dry_run_result_path=None,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=True,
    )
    mismatch = build_real_archive_sidecar_write(
        sidecar_update_packet_path=launch_packet,
        dry_run_result_path=deploy_dry,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=True,
    )
    privacy = build_real_archive_sidecar_write(
        sidecar_update_packet_path=privacy_packet,
        dry_run_result_path=launch_dry,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=True,
    )
    authority = build_real_archive_sidecar_write(
        sidecar_update_packet_path=authority_packet,
        dry_run_result_path=launch_dry,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=True,
    )

    assert missing["real_archive_write_status"] == "blocked_dry_run_missing"
    assert mismatch["real_archive_write_status"] == "blocked_dry_run_mismatch"
    assert privacy["real_archive_write_status"] == "blocked_privacy_risk"
    assert authority["real_archive_write_status"] == "blocked_authority_claim"
    assert not (archive_dir / "decision_work").exists()


def test_cli_writes_receipt_and_real_archive_sidecar_files(tmp_path: Path) -> None:
    packet_path, dry_run_path = _packet_and_dry_run(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    archive_dir = _archive_dir(tmp_path, "launch-cli")
    out = tmp_path / "real_archive_sidecar_write_receipt.json"

    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/evals/write_decision_work_real_archive_sidecar.py"),
            "--sidecar-update-packet",
            str(packet_path),
            "--dry-run-result",
            str(dry_run_path),
            "--target-archive-dir",
            str(archive_dir),
            "--operator-confirm-real-archive-write",
            "--out",
            str(out),
            "--pretty",
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    receipt = _json(out)
    assert receipt["real_archive_write_status"] == REAL_ARCHIVE_WRITE_COMPLETED_STATUS
    assert set(receipt["files_written"]) == ALLOWED_WRITTEN_FILES
    assert {path.name for path in (archive_dir / "decision_work").iterdir()} == {
        Path(item).name for item in ALLOWED_WRITTEN_FILES
    }


def test_renderer_does_not_modify_source_packet_or_dry_run(tmp_path: Path) -> None:
    packet_path, dry_run_path = _packet_and_dry_run(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    before = (
        packet_path.read_text(encoding="utf-8"),
        dry_run_path.read_text(encoding="utf-8"),
    )
    archive_dir = _archive_dir(tmp_path, "launch-no-modify")
    receipt = build_real_archive_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=True,
    )
    rendered = render_real_archive_sidecar_write_json(receipt, pretty=True)

    assert json.loads(rendered)["schema_version"] == REAL_ARCHIVE_SIDECAR_WRITE_RECEIPT_SCHEMA_VERSION
    assert (
        packet_path.read_text(encoding="utf-8"),
        dry_run_path.read_text(encoding="utf-8"),
    ) == before


def test_adapter_doc_and_discoverability_docs_reference_pr219() -> None:
    expected = "Decision Work Real Archive Sidecar Write Adapter"
    for path in (
        DOC_PATH,
        PLAN_DOC,
        INTERNAL_V1_PRD,
        AUTOMATIC_SUPPLY_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr219_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            PLAN_DOC,
            INTERNAL_V1_PRD,
            AUTOMATIC_SUPPLY_PRD,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr219_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        PLAN_DOC,
        INTERNAL_V1_PRD,
        AUTOMATIC_SUPPLY_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in PRIVATE_MARKERS:
            assert forbidden not in text, (path, forbidden)
