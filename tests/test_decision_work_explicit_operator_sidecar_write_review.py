from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_explicit_operator_sidecar_write import (
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
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-explicit-operator-sidecar-write-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-explicit-operator-sidecar-write-adapter-v0.md"
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sidecar_update_and_dry_run_paths(
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


def _write_receipt(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path,
    intake_path: Path,
    rendered_path: Path,
    triage_path: Path,
) -> tuple[dict[str, Any], Path]:
    packet_path, dry_run_path = _sidecar_update_and_dry_run_paths(
        tmp_path,
        name=name,
        read_path=read_path,
        intake_path=intake_path,
        rendered_path=rendered_path,
        triage_path=triage_path,
    )
    target = tmp_path / f"{name}_fixture" / "decision_work"
    receipt = build_explicit_operator_sidecar_write(
        sidecar_update_packet_path=packet_path,
        dry_run_result_path=dry_run_path,
        target_sidecar_dir=target,
        created_at="2026-07-03T00:00:00Z",
    )
    return receipt, target


def test_review_json_schema_cases_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_explicit_operator_sidecar_write_review.v0"
    )
    assert {case["case_id"] for case in review["reviewed_cases"]} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert review["launch_write_status"] == WRITE_COMPLETED_STATUS
    assert review["deploy_write_status"] == WRITE_COMPLETED_BLOCKED_STATUS
    assert (
        review["decision_gate"]
        == "proceed_to_explicit_operator_sidecar_write_package_gate"
    )
    assert (
        review["recommended_next_pr"]
        == "PR212 Explicit Operator Sidecar Write Package Gate v0"
    )


def test_temp_fixture_writes_match_reviewed_statuses(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)
    launch, launch_target = _write_receipt(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    deploy, deploy_target = _write_receipt(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    assert launch["write_status"] == review["launch_write_status"]
    assert deploy["write_status"] == review["deploy_write_status"]
    assert set(launch["files_written"]) == ALLOWED_FILES
    assert set(deploy["files_written"]) == ALLOWED_FILES
    assert {path.name for path in launch_target.iterdir()} == ALLOWED_FILES
    assert {path.name for path in deploy_target.iterdir()} == ALLOWED_FILES
    assert launch["fixture_only"] is True
    assert deploy["fixture_only"] is True
    assert launch["actual_sidecar_write_performed"] is True
    assert deploy["actual_sidecar_write_performed"] is True
    assert launch["real_archive_mutated"] is False
    assert deploy["real_archive_mutated"] is False
    assert launch["historical_archive_mutated"] is False
    assert deploy["historical_archive_mutated"] is False
    assert launch["runtime_wiring_changed"] is False
    assert deploy["runtime_wiring_changed"] is False
    assert launch["resolver_refs_approved"] is False
    assert deploy["resolver_refs_approved"] is False


def test_review_closes_fixture_archive_runtime_and_resolver_boundaries() -> None:
    review = _json(REVIEW_PATH)
    fixture = review["fixture_only_check"]
    real_archive = review["real_archive_mutation_forbidden_check"]
    historical = review["historical_archive_mutation_forbidden_check"]
    runtime = review["runtime_wiring_forbidden_check"]
    resolver = review["resolver_approval_forbidden_check"]

    assert fixture["fixture_only"] is True
    assert fixture["checked_in_sidecar_files_created"] is False
    assert fixture["target_sidecar_dir_must_be_explicit"] is True
    assert fixture["target_sidecar_dir_must_be_named_decision_work"] is True
    assert fixture["target_sidecar_dir_must_be_temp_or_output_only"] is True
    assert fixture["writes_inside_repo_blocked"] is True
    assert fixture["archive_like_targets_blocked"] is True
    assert fixture["runtime_like_targets_blocked"] is True
    assert fixture["receipt_outputs_under_decision_work_blocked"] is True
    assert fixture["generated_files_stay_inside_target_dir"] is True
    assert real_archive["real_archive_mutated"] is False
    assert real_archive["can_write_real_archive_sidecar"] is False
    assert real_archive["real_archive_paths_rejected"] is True
    assert historical["historical_archive_mutated"] is False
    assert historical["can_mutate_historical_archive"] is False
    assert historical["historical_archive_paths_rejected"] is True
    assert runtime["runtime_wiring_changed"] is False
    assert runtime["can_wire_runtime"] is False
    assert runtime["runtime_hook_changed"] is False
    assert runtime["runtime_attachment_default_on"] is False
    assert resolver["resolver_refs_approved"] is False
    assert resolver["resolver_refs_marked_usable"] is False
    assert resolver["write_adapter_can_approve_refs"] is False


def test_review_preserves_deploy_block_and_non_claims(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)
    non_claims = set(review["non_claims_preserved"])
    deploy, deploy_target = _write_receipt(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )
    attachment = _json(deploy_target / "attachment_status.json")

    assert review["deploy_runtime_block_preserved"] is True
    assert review["launch_receipt_coherence"] is True
    assert review["privacy_limits_preserved"] is True
    assert deploy["write_status"] == WRITE_COMPLETED_BLOCKED_STATUS
    assert attachment["runtime_use_status"]["status"] == "blocked"
    assert attachment["user_surface_status"]["status"] == "blocked"
    assert "not_product_proof" in non_claims
    assert "not_human_validation" in non_claims
    assert "not_answer_quality_score" in non_claims
    assert "not_advice_correctness_proof" in non_claims
    assert "not_real_archive_write" in non_claims
    assert "not_historical_archive_mutation" in non_claims
    assert "not_runtime_wiring" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_review_doc_records_findings_boundaries_and_next_pr() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Explicit Operator Sidecar Write Review v0" in text
    assert "review-only pass" in text
    assert WRITE_COMPLETED_STATUS in text
    assert WRITE_COMPLETED_BLOCKED_STATUS in text
    assert "fixture-only" in text
    assert "not check in generated sidecar files" in text
    assert "proceed_to_explicit_operator_sidecar_write_package_gate" in text
    assert "PR212 Explicit Operator Sidecar Write Package Gate v0" in text
    assert "Do not implement real archive writes" in text


def test_discoverability_docs_reference_pr211() -> None:
    expected = "Decision Work Explicit Operator Sidecar Write Review"
    for path in (
        DOC_PATH,
        ADAPTER_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr211_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            ADAPTER_DOC,
            PRD_PATH,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr211_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        ADAPTER_DOC,
        PRD_PATH,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
