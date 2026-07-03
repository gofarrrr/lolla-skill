from __future__ import annotations

import json
from pathlib import Path

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
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-sidecar-write-dry-run-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-sidecar-write-dry-run-adapter-v0.md"
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


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sidecar_update_packet_path(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path,
    intake_path: Path,
    rendered_path: Path,
    triage_path: Path,
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
    packet = build_resolver_candidate_sidecar_update_packet(
        resolver_supply_path=resolver_supply_path,
        source_resolver_supply_ref=f"temp:{name}_resolver_supply.json",
        created_at="2026-07-03T00:00:00Z",
    )
    packet_path = tmp_path / f"{name}_sidecar_update_packet.json"
    packet_path.write_text(
        render_resolver_candidate_sidecar_update_packet_json(packet, pretty=True),
        encoding="utf-8",
    )
    return packet_path


def _dry_run_result(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path,
    intake_path: Path,
    rendered_path: Path,
    triage_path: Path,
) -> dict:
    packet_path = _sidecar_update_packet_path(
        tmp_path,
        name=name,
        read_path=read_path,
        intake_path=intake_path,
        rendered_path=rendered_path,
        triage_path=triage_path,
    )
    return build_sidecar_write_dry_run(
        sidecar_update_packet_path=packet_path,
        source_sidecar_update_packet_ref=f"temp:{name}_sidecar_update_packet.json",
        preview_dir=tmp_path / f"{name}_preview",
        write_preview=True,
        created_at="2026-07-03T00:00:00Z",
    )


def test_review_json_schema_cases_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert review["schema_version"] == "lolla.decision_work_sidecar_write_dry_run_review.v0"
    assert {case["case_id"] for case in review["reviewed_cases"]} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert review["launch_dry_run_status"] == "dry_run_ready"
    assert review["deploy_dry_run_status"] == "dry_run_packet_with_runtime_block"
    assert review["decision_gate"] == "proceed_to_sidecar_write_dry_run_package_gate"
    assert review["recommended_next_pr"] == "PR208 Sidecar Write Dry-Run Package Gate v0"


def test_temp_dry_runs_match_reviewed_statuses(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)
    launch = _dry_run_result(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    deploy = _dry_run_result(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    assert launch["dry_run_status"] == review["launch_dry_run_status"]
    assert deploy["dry_run_status"] == review["deploy_dry_run_status"]
    assert launch["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert deploy["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert set(launch["preview_files_written"]) == {
        "attachment_status.json",
        "user_receipt.md",
        "agent_handoff_packet.json",
        "safe_supply_summary.json",
        "sidecar_update_packet.json",
    }
    assert set(deploy["preview_files_written"]) == set(launch["preview_files_written"])
    assert launch["actual_sidecar_write_performed"] is False
    assert deploy["actual_sidecar_write_performed"] is False
    assert launch["archive_mutated"] is False
    assert deploy["archive_mutated"] is False
    assert launch["runtime_wiring_changed"] is False
    assert deploy["runtime_wiring_changed"] is False
    assert launch["resolver_refs_approved"] is False
    assert deploy["resolver_refs_approved"] is False


def test_review_closes_write_archive_runtime_and_resolver_boundaries() -> None:
    review = _json(REVIEW_PATH)
    write = review["actual_write_forbidden_check"]
    archive = review["archive_mutation_forbidden_check"]
    runtime = review["runtime_wiring_forbidden_check"]
    resolver = review["resolver_approval_forbidden_check"]
    preview = review["preview_dir_safety_check"]

    assert write["actual_sidecar_write_performed"] is False
    assert write["can_write_runtime_sidecar"] is False
    assert write["can_write_decision_work_directory"] is False
    assert write["decision_work_directory_written"] is False
    assert write["preview_files_are_not_sidecar_writes"] is True
    assert archive["archive_mutated"] is False
    assert archive["can_mutate_archive"] is False
    assert archive["archive_sidecar_written"] is False
    assert archive["archive_paths_rejected"] is True
    assert runtime["runtime_wiring_changed"] is False
    assert runtime["can_wire_runtime"] is False
    assert runtime["runtime_hook_changed"] is False
    assert runtime["runtime_attachment_default_on"] is False
    assert resolver["resolver_refs_approved"] is False
    assert resolver["resolver_refs_marked_usable"] is False
    assert resolver["dry_run_can_approve_refs"] is False
    assert preview["preview_dir_must_be_explicit"] is True
    assert preview["preview_dir_must_not_target_decision_work"] is True
    assert preview["preview_dir_must_not_target_archive"] is True
    assert preview["preview_files_stay_inside_preview_dir"] is True


def test_review_preserves_deploy_block_and_non_claims() -> None:
    review = _json(REVIEW_PATH)
    non_claims = set(review["non_claims_preserved"])

    assert review["deploy_runtime_block_preserved"] is True
    assert review["launch_preview_coherence"] is True
    assert review["privacy_limits_preserved"] is True
    assert "not_product_proof" in non_claims
    assert "not_human_validation" in non_claims
    assert "not_answer_quality_score" in non_claims
    assert "not_advice_correctness_proof" in non_claims
    assert "not_actual_sidecar_write" in non_claims
    assert "not_archive_mutation" in non_claims
    assert "not_runtime_wiring" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_automatic_action_authorization" in non_claims


def test_review_doc_records_findings_boundaries_and_next_pr() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Sidecar Write Dry-Run Review v0" in text
    assert "review-only pass" in text
    assert "dry_run_ready" in text
    assert "dry_run_packet_with_runtime_block" in text
    assert "not a runtime sidecar write" in text
    assert "proceed_to_sidecar_write_dry_run_package_gate" in text
    assert "PR208 Sidecar Write Dry-Run Package Gate v0" in text
    assert "Do not implement actual sidecar writes" in text


def test_discoverability_docs_reference_pr207() -> None:
    expected = "Decision Work Sidecar Write Dry-Run Review"
    for path in (
        DOC_PATH,
        ADAPTER_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr207_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            ADAPTER_DOC,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr207_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        ADAPTER_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
