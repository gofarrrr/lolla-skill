from __future__ import annotations

import copy
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
    READY_STATUS,
    RUNTIME_BLOCK_STATUS,
    SIDECAR_UPDATE_PACKET_SCHEMA_VERSION,
    build_resolver_candidate_sidecar_update_packet,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT
    / "engine/system_b/decision_work_resolver_candidate_sidecar_update_packet.py"
)
SCRIPT_PATH = (
    REPO_ROOT
    / "scripts/evals/build_decision_work_resolver_candidate_sidecar_update_packet.py"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-resolver-candidate-sidecar-update-packet-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-resolver-candidate-sidecar-update-plan-v0.md"
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


def _resolver_supply_path(
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
    return resolver_supply_path


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_launch_resolver_supply_produces_ready_sidecar_update_packet(
    tmp_path: Path,
) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")

    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=resolver_supply_path,
        source_resolver_supply_ref="tmp/launch_resolver_supply.json",
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet["schema_version"] == SIDECAR_UPDATE_PACKET_SCHEMA_VERSION
    assert packet["sidecar_update_packet_status"] == READY_STATUS
    assert packet["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert packet["blocker_reasons"] == []
    assert packet["proposed_sidecar_state"]["would_write_decision_work_directory"] is False
    assert packet["proposed_sidecar_state"]["actual_sidecar_write_performed"] is False
    assert packet["proposed_receipt_state"]["receipt_state"] == (
        "candidate_packet_available_for_review"
    )
    assert packet["resolver_refs_approved"] is False
    assert packet["actual_sidecar_write_performed"] is False
    assert packet["archive_mutated"] is False
    assert packet["runtime_wiring_changed"] is False
    assert packet["downstream_allowed"]["can_write_decision_work_directory"] is False
    assert packet["downstream_allowed"]["can_update_sidecar"] is False
    assert packet["downstream_allowed"]["can_be_used_as_quality_label"] is False


def test_deploy_resolver_supply_preserves_runtime_block(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=resolver_supply_path,
        source_resolver_supply_ref="tmp/deploy_resolver_supply.json",
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet["sidecar_update_packet_status"] == RUNTIME_BLOCK_STATUS
    assert packet["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert packet["runtime_use_status"]["status"] == "blocked"
    assert packet["user_surface_status"]["status"] == "blocked"
    assert packet["agent_inspection_status"]["status"] == "inspection_only"
    assert packet["proposed_receipt_state"]["receipt_state"] == (
        "blocked_for_runtime_use"
    )
    assert packet["downstream_allowed"]["can_update_sidecar"] is False
    assert packet["downstream_allowed"]["can_write_decision_work_directory"] is False
    assert packet["downstream_allowed"]["resolver_refs_approved"] is False


def test_missing_resolver_supply_is_deferred(tmp_path: Path) -> None:
    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=tmp_path / "missing.json",
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet["sidecar_update_packet_status"] == "deferred_missing_resolver_supply"
    assert "resolver_supply_missing" in packet["blocker_reasons"]
    assert packet["downstream_allowed"]["can_feed_sidecar_update_packet_review"] is False


def test_non_candidate_resolver_supply_is_blocked(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")
    payload = _json(resolver_supply_path)
    payload["resolver_supply_status"] = "deferred_missing_triage"
    path = _write_json(tmp_path, "non_candidate_resolver_supply.json", payload)

    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet["sidecar_update_packet_status"] == (
        "blocked_resolver_supply_not_candidate"
    )
    assert "resolver_supply_not_candidate:deferred_missing_triage" in (
        packet["blocker_reasons"]
    )


def test_privacy_markers_and_local_paths_are_blocked(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")
    payload = _json(resolver_supply_path)
    payload["privacy_summary"]["local_absolute_path_detected"] = True
    path = _write_json(tmp_path, "local_path_resolver_supply.json", payload)

    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet["sidecar_update_packet_status"] == "blocked_privacy_risk"
    assert "local_absolute_path_detected" in packet["blocker_reasons"]


def test_authority_proof_scoring_and_action_claims_are_blocked(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")
    payload = _json(resolver_supply_path)
    payload["downstream_allowed"]["resolver_refs_approved"] = True
    payload["downstream_allowed"]["can_be_used_as_quality_label"] = True
    payload["custody_flags"]["product_proof"] = True
    path = _write_json(tmp_path, "authority_resolver_supply.json", payload)

    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet["sidecar_update_packet_status"] == "blocked_authority_claim"
    assert "authority_claim_detected" in packet["blocker_reasons"]
    assert packet["resolver_refs_approved"] is False
    assert packet["downstream_allowed"]["can_be_used_as_quality_label"] is False


def test_runtime_write_attempts_are_blocked(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")
    payload = _json(resolver_supply_path)
    payload["downstream_allowed"]["can_update_sidecar"] = True
    payload["runtime_use_status"]["candidate_packet_can_override_runtime_block"] = True
    path = _write_json(tmp_path, "runtime_write_resolver_supply.json", payload)

    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert packet["sidecar_update_packet_status"] == "blocked_runtime_write_attempt"
    assert "runtime_write_attempt_detected" in packet["blocker_reasons"]
    assert packet["actual_sidecar_write_performed"] is False
    assert packet["archive_mutated"] is False
    assert packet["runtime_wiring_changed"] is False


def test_cli_writes_valid_json_without_sidecar_write(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")
    output = tmp_path / "sidecar_update_packet.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--resolver-supply",
            str(resolver_supply_path),
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
    packet = _json(output)
    assert packet["schema_version"] == SIDECAR_UPDATE_PACKET_SCHEMA_VERSION
    assert packet["sidecar_update_packet_status"] == READY_STATUS
    assert packet["actual_sidecar_write_performed"] is False
    assert not (tmp_path / "decision_work").exists()


def test_cli_refuses_decision_work_output_directory(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")
    output = tmp_path / "decision_work" / "sidecar_update_packet.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--resolver-supply",
            str(resolver_supply_path),
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
    assert "must not target a decision_work sidecar directory" in completed.stderr
    assert not output.exists()


def test_source_resolver_supply_artifact_is_not_modified(tmp_path: Path) -> None:
    resolver_supply_path = _resolver_supply_path(tmp_path, name="launch")
    before = resolver_supply_path.read_text(encoding="utf-8")

    build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=resolver_supply_path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert resolver_supply_path.read_text(encoding="utf-8") == before


def test_adapter_doc_and_discoverability_docs_reference_pr202() -> None:
    expected = "Decision Work Resolver Candidate Sidecar Update Packet Adapter"
    for path in (
        DOC_PATH,
        PLAN_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr202_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            PLAN_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr202_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        MODULE_PATH,
        SCRIPT_PATH,
        DOC_PATH,
        PLAN_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
