from __future__ import annotations

import json
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
    REAL_ARCHIVE_WRITE_COMPLETED_BLOCKED_STATUS,
    REAL_ARCHIVE_WRITE_COMPLETED_STATUS,
    build_real_archive_sidecar_write,
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
    "decision-work-real-archive-sidecar-write-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-real-archive-sidecar-write-review-v0/"
    "review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-real-archive-sidecar-write-adapter-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
INTERNAL_V1_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-internal-v1-completion-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
LAUNCH_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/"
    "read.json"
)
LAUNCH_INTAKE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/"
    "intake.json"
)
LAUNCH_RENDERED = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
)
LAUNCH_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/"
    "triage.json"
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
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-triage-pilot-v0/triage.json"
)
ALLOWED_WRITTEN_FILES = {
    "decision_work/attachment_status.json",
    "decision_work/user_receipt.md",
    "decision_work/agent_handoff_packet.json",
    "decision_work/safe_supply_summary.json",
    "decision_work/sidecar_update_packet.json",
    "decision_work/sidecar_write_receipt.json",
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


def test_review_json_schema_cases_gate_and_non_claims() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_real_archive_sidecar_write_review.v0"
    )
    assert {case["case_id"] for case in review["reviewed_cases"]} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert review["launch_write_status"] == REAL_ARCHIVE_WRITE_COMPLETED_STATUS
    assert review["deploy_write_status"] == REAL_ARCHIVE_WRITE_COMPLETED_BLOCKED_STATUS
    assert review["deploy_runtime_block_preserved"] is True
    assert review["deploy_user_surface_block_preserved"] is True
    assert review["synthetic_validation_check"]["real_historical_archive_path_touched"] is False
    assert review["synthetic_validation_check"]["repo_decision_work_sidecar_written"] is False
    assert review["written_file_set_check"]["matches_pr209_allowed_file_set"] is True
    assert review["unsafe_rejection_checks"]["missing_operator_confirmation_rejected"] is True
    assert review["unsafe_rejection_checks"]["existing_decision_work_sidecar_rejected"] is True
    assert review["command_only_check"]["runtime_hook_changed"] is False
    assert review["command_only_check"]["scripts_archive_run_changed"] is False
    assert review["receipt_semantics_check"]["runtime_wiring_changed"] is False
    assert review["receipt_semantics_check"]["archive_hook_changed"] is False
    assert review["receipt_semantics_check"]["resolver_refs_approved"] is False
    assert review["receipt_semantics_check"]["product_proof"] is False
    assert review["receipt_semantics_check"]["human_validated"] is False
    assert review["receipt_semantics_check"]["answer_quality_scored"] is False
    assert review["receipt_semantics_check"]["advice_correctness_validated"] is False
    assert review["decision_gate"] == "proceed_to_real_archive_sidecar_write_package_gate"
    assert review["recommended_next_pr"] == "PR221 Real Archive Sidecar Write Package Gate v0"
    assert "review_does_not_approve_resolver_refs" in review["non_claims"]
    assert "review_does_not_wire_runtime" in review["non_claims"]


def test_review_regenerates_launch_and_deploy_synthetic_archive_outputs(
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

    deploy_attachment = _json(deploy_dir / "decision_work" / "attachment_status.json")
    deploy_receipt = _json(deploy_dir / "decision_work" / "sidecar_write_receipt.json")
    assert deploy_attachment["runtime_use_status"]["status"] == "blocked"
    assert deploy_attachment["user_surface_status"]["status"] == "blocked"
    assert deploy_receipt["real_archive_write_status"] == (
        REAL_ARCHIVE_WRITE_COMPLETED_BLOCKED_STATUS
    )
    for receipt in (launch, deploy, deploy_receipt):
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


def test_reviewed_refusal_cases_remain_blocked(tmp_path: Path) -> None:
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
    archive_dir = _archive_dir(tmp_path, "launch")
    missing_markers = tmp_path / "archive" / "cases" / "missing-markers-run"
    missing_markers.mkdir(parents=True)
    existing_sidecar = _archive_dir(tmp_path, "existing-sidecar")
    (existing_sidecar / "decision_work").mkdir()
    repo_path = REPO_ROOT / "archive" / "cases" / "repo-run"
    privacy_packet = tmp_path / "privacy_packet.json"
    payload = _json(launch_packet)
    payload["notes"] = "SEC" + "RET"
    privacy_packet.write_text(json.dumps(payload), encoding="utf-8")

    no_confirm = build_real_archive_sidecar_write(
        sidecar_update_packet_path=launch_packet,
        dry_run_result_path=launch_dry,
        target_archive_dir=archive_dir,
        operator_confirm_real_archive_write=False,
    )
    missing = build_real_archive_sidecar_write(
        sidecar_update_packet_path=launch_packet,
        dry_run_result_path=launch_dry,
        target_archive_dir=missing_markers,
        operator_confirm_real_archive_write=True,
    )
    existing = build_real_archive_sidecar_write(
        sidecar_update_packet_path=launch_packet,
        dry_run_result_path=launch_dry,
        target_archive_dir=existing_sidecar,
        operator_confirm_real_archive_write=True,
    )
    repo = build_real_archive_sidecar_write(
        sidecar_update_packet_path=launch_packet,
        dry_run_result_path=launch_dry,
        target_archive_dir=repo_path,
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

    assert no_confirm["real_archive_write_status"] == "blocked_operator_confirmation_missing"
    assert missing["real_archive_write_status"] == "blocked_archive_markers_missing"
    assert existing["real_archive_write_status"] == "blocked_existing_decision_work_sidecar"
    assert repo["real_archive_write_status"] == "blocked_repo_path"
    assert mismatch["real_archive_write_status"] == "blocked_dry_run_mismatch"
    assert privacy["real_archive_write_status"] == "blocked_privacy_risk"
    assert not (missing_markers / "decision_work").exists()
    assert not (repo_path / "decision_work").exists()


def test_pr220_docs_and_discoverability_references() -> None:
    expected = "Decision Work Real Archive Sidecar Write Review"
    for path in (
        DOC_PATH,
        ADAPTER_DOC,
        INTERNAL_V1_PRD,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr220_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            ADAPTER_DOC,
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


def test_pr220_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        ADAPTER_DOC,
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
