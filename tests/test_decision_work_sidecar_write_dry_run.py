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
from engine.system_b.decision_work_resolver_candidate_sidecar_update_packet import (
    build_resolver_candidate_sidecar_update_packet,
    render_resolver_candidate_sidecar_update_packet_json,
)
from engine.system_b.decision_work_sidecar_write_dry_run import (
    DRY_RUN_READY_STATUS,
    DRY_RUN_RUNTIME_BLOCK_STATUS,
    SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION,
    build_sidecar_write_dry_run,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "engine/system_b/decision_work_sidecar_write_dry_run.py"
SCRIPT_PATH = REPO_ROOT / "scripts/evals/dry_run_decision_work_sidecar_write.py"
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-runtime-sidecar-write-plan-v0.md"
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


def _write_json(tmp_path: Path, name: str, payload: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sidecar_update_packet_path(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path = LAUNCH_READ,
    intake_path: Path = LAUNCH_INTAKE,
    rendered_path: Path = LAUNCH_RENDERED,
    triage_path: Path = LAUNCH_TRIAGE,
) -> Path:
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
    return packet_path


def test_launch_packet_produces_dry_run_ready_and_preview(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    preview_dir = tmp_path / "preview_launch"

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=packet_path,
        source_sidecar_update_packet_ref="tmp/launch_sidecar_update_packet.json",
        preview_dir=preview_dir,
        write_preview=True,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["schema_version"] == SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION
    assert result["dry_run_status"] == DRY_RUN_READY_STATUS
    assert result["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert result["blocker_reasons"] == []
    assert result["actual_sidecar_write_performed"] is False
    assert result["archive_mutated"] is False
    assert result["runtime_wiring_changed"] is False
    assert result["resolver_refs_approved"] is False
    assert result["can_write_runtime_sidecar"] is False
    assert set(result["preview_files_written"]) == set(result["would_write_files"])
    assert (preview_dir / "attachment_status.json").exists()
    assert (preview_dir / "user_receipt.md").exists()
    assert (preview_dir / "agent_handoff_packet.json").exists()
    assert (preview_dir / "safe_supply_summary.json").exists()
    assert (preview_dir / "sidecar_update_packet.json").exists()
    assert not (tmp_path / "decision_work").exists()


def test_deploy_packet_preserves_runtime_block_in_dry_run(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=packet_path,
        preview_dir=tmp_path / "preview_deploy",
        write_preview=True,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["dry_run_status"] == DRY_RUN_RUNTIME_BLOCK_STATUS
    assert result["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    attachment = _json(tmp_path / "preview_deploy" / "attachment_status.json")
    assert attachment["runtime_use_status"]["status"] == "blocked"
    assert attachment["user_surface_status"]["status"] == "blocked"
    assert attachment["actual_sidecar_write_performed"] is False
    assert attachment["archive_mutated"] is False
    assert attachment["resolver_refs_approved"] is False


def test_preview_dir_targeting_decision_work_is_blocked(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    preview_dir = tmp_path / "archives" / "run-1" / "decision_work"

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=packet_path,
        preview_dir=preview_dir,
        write_preview=True,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["dry_run_status"] == "blocked_archive_path"
    assert "preview_dir_targets_archive_or_sidecar" in result["blocker_reasons"]
    assert result["preview_files_written"] == []
    assert not preview_dir.exists()


def test_non_sidecar_update_packet_is_blocked(tmp_path: Path) -> None:
    path = _write_json(tmp_path, "not_a_sidecar_packet.json", {"schema_version": "x"})

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["dry_run_status"] == "blocked_not_sidecar_update_packet"
    assert "sidecar_update_packet_schema_invalid" in result["blocker_reasons"]


def test_missing_required_source_refs_are_blocked(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    payload = _json(packet_path)
    payload["source_refs"]["source_triage_ref"] = ""
    path = _write_json(tmp_path, "missing_refs_packet.json", payload)

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["dry_run_status"] == "blocked_missing_required_fields"
    assert "source_triage_ref_missing" in result["blocker_reasons"]


def test_privacy_markers_and_local_paths_are_blocked(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    payload = _json(packet_path)
    payload["privacy_summary"]["local_absolute_path_detected"] = True
    path = _write_json(tmp_path, "privacy_packet.json", payload)

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["dry_run_status"] == "blocked_privacy_risk"
    assert "local_absolute_path_detected" in result["blocker_reasons"]


def test_authority_proof_scoring_and_action_claims_are_blocked(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    payload = _json(packet_path)
    payload["downstream_allowed"]["resolver_refs_approved"] = True
    payload["downstream_allowed"]["can_be_used_as_quality_label"] = True
    payload["custody_flags"]["product_proof"] = True
    path = _write_json(tmp_path, "authority_packet.json", payload)

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["dry_run_status"] == "blocked_authority_claim"
    assert "authority_claim_detected" in result["blocker_reasons"]
    assert result["resolver_refs_approved"] is False
    assert result["downstream_allowed"]["can_be_used_as_quality_label"] is False


def test_actual_write_attempts_are_blocked(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    payload = _json(packet_path)
    payload["actual_sidecar_write_performed"] = True
    payload["downstream_allowed"]["can_write_decision_work_directory"] = True
    path = _write_json(tmp_path, "write_attempt_packet.json", payload)

    result = build_sidecar_write_dry_run(
        sidecar_update_packet_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["dry_run_status"] == "blocked_actual_write_attempt"
    assert "actual_write_attempt_detected" in result["blocker_reasons"]
    assert result["actual_sidecar_write_performed"] is False
    assert result["archive_mutated"] is False


def test_cli_writes_result_and_preview_without_decision_work_sidecar(
    tmp_path: Path,
) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    output = tmp_path / "dry_run.json"
    preview_dir = tmp_path / "preview"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--sidecar-update-packet",
            str(packet_path),
            "--out",
            str(output),
            "--preview-dir",
            str(preview_dir),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    result = _json(output)
    assert result["schema_version"] == SIDECAR_WRITE_DRY_RUN_SCHEMA_VERSION
    assert result["dry_run_status"] == DRY_RUN_READY_STATUS
    assert result["actual_sidecar_write_performed"] is False
    assert set(result["preview_files_written"]) == set(result["would_write_files"])
    assert (preview_dir / "user_receipt.md").exists()
    assert not (tmp_path / "decision_work").exists()


def test_cli_refuses_decision_work_output_directory(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    output = tmp_path / "decision_work" / "dry_run.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--sidecar-update-packet",
            str(packet_path),
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
    assert "must not target an archive or decision_work sidecar directory" in (
        completed.stderr
    )
    assert not output.exists()


def test_source_sidecar_update_packet_is_not_modified(tmp_path: Path) -> None:
    packet_path = _sidecar_update_packet_path(tmp_path, name="launch")
    before = packet_path.read_text(encoding="utf-8")

    build_sidecar_write_dry_run(
        sidecar_update_packet_path=packet_path,
        preview_dir=tmp_path / "preview",
        write_preview=True,
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet_path.read_text(encoding="utf-8") == before


def test_adapter_doc_and_discoverability_docs_reference_pr206() -> None:
    expected = "Decision Work Sidecar Write Dry-Run Adapter"
    for path in (
        DOC_PATH,
        PLAN_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr206_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            PLAN_DOC,
            PRD_PATH,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr206_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        MODULE_PATH,
        SCRIPT_PATH,
        DOC_PATH,
        PLAN_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
