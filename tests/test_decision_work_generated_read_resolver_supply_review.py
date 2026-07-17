from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.decision_work_generated_read_brief_supply import (
    build_generated_read_brief_supply,
    render_generated_read_brief_supply_json,
)
from engine.system_b.decision_work_generated_read_resolver_supply import (
    build_generated_read_resolver_supply,
)
from engine.system_b.decision_work_generated_read_triage_supply import (
    build_generated_read_triage_supply,
    render_generated_read_triage_supply_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-resolver-supply-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-resolver-supply-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-resolver-supply-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-resolver-supply-plan-v0.md"
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


def _resolver_packet(
    tmp_path: Path,
    *,
    name: str,
    read_path: Path,
    intake_path: Path,
    rendered_path: Path,
    triage_path: Path,
) -> dict:
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
    return build_generated_read_resolver_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=rendered_path,
        triage_supply_path=triage_supply_path,
        triage_path=triage_path,
        created_at="2026-07-03T00:00:00Z",
    )


def test_review_json_schema_cases_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_resolver_supply_review.v0"
    )
    assert {case["case_id"] for case in review["reviewed_cases"]} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert review["launch_status"] == "ready_for_resolver_candidate_packet"
    assert review["deploy_status"] == "candidate_packet_with_runtime_block"
    assert (
        review["decision_gate"]
        == "proceed_to_automatic_semantic_supply_pre_runtime_v1_package"
    )
    assert review["recommended_next_pr"] == (
        "PR200 Decision Work Automatic Semantic Supply Pre-Runtime v1 "
        "Package Gate v0"
    )


def test_temp_resolver_packets_match_reviewed_statuses(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)
    launch = _resolver_packet(
        tmp_path,
        name="launch",
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        rendered_path=LAUNCH_RENDERED,
        triage_path=LAUNCH_TRIAGE,
    )
    deploy = _resolver_packet(
        tmp_path,
        name="deploy",
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    assert launch["resolver_supply_status"] == review["launch_status"]
    assert deploy["resolver_supply_status"] == review["deploy_status"]
    assert launch["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert deploy["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert launch["downstream_allowed"]["resolver_refs_approved"] is False
    assert deploy["downstream_allowed"]["resolver_refs_approved"] is False
    assert launch["downstream_allowed"]["can_write_runtime_sidecar"] is False
    assert deploy["downstream_allowed"]["can_write_runtime_sidecar"] is False
    assert deploy["user_surface_status"]["status"] == "blocked"
    assert deploy["runtime_use_status"]["status"] == "blocked"
    assert "agent_inspection_only" in deploy["route_summary"]["route_categories"]
    assert "not_ready_for_user_surface" in deploy["route_summary"]["route_categories"]


def test_candidate_approval_runtime_and_user_surface_boundaries_are_closed() -> None:
    review = _json(REVIEW_PATH)
    approval = review["resolver_approval_forbidden_check"]
    runtime = review["runtime_sidecar_forbidden_check"]
    user_surface = review["user_surface_boundary_check"]
    metadata = review["review_metadata"]

    assert review["candidate_not_approval_finding"]["candidate_packet_is_approval"] is False
    assert approval["resolver_refs_approved"] is False
    assert approval["resolver_refs_marked_usable"] is False
    assert approval["candidate_packet_can_approve_refs"] is False
    assert runtime["can_update_sidecar"] is False
    assert runtime["can_write_runtime_sidecar"] is False
    assert runtime["can_wire_runtime"] is False
    assert runtime["candidate_packet_can_override_runtime_block"] is False
    assert user_surface["customer_ready"] is False
    assert user_surface["product_proof"] is False
    assert user_surface["human_validated"] is False
    assert metadata["model_calls"] == 0
    assert metadata["runtime_invoked"] is False
    assert metadata["skill_invoked"] is False
    assert metadata["archive_mutated"] is False
    assert metadata["resolver_refs_approved"] is False
    assert metadata["runtime_sidecar_updated"] is False
    assert metadata["runtime_wired"] is False


def test_review_preserves_refs_uncertainty_privacy_and_non_claims() -> None:
    review = _json(REVIEW_PATH)
    refs = review["source_refs_preserved"]
    non_claims = set(review["non_claims_preserved"])

    assert refs["generated_read"] is True
    assert refs["intake_result"] is True
    assert refs["brief_supply"] is True
    assert refs["rendered_brief"] is True
    assert refs["triage_supply"] is True
    assert refs["triage_read"] is True
    assert refs["raw_content_included"] is False
    assert review["uncertainty_preserved"] is True
    assert review["privacy_limits_preserved"] is True
    assert "not_resolver_ref_approval" in non_claims
    assert "not_runtime_sidecar_update" in non_claims
    assert "not_answer_quality_score" in non_claims
    assert "not_advice_correctness_proof" in non_claims
    assert "not_agent_action_authorization" in non_claims


def test_review_doc_records_findings_and_next_pr() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Resolver Supply Review v0" in text
    assert "resolver-supply candidate, not approved resolver refs" in text
    assert "launch-public-enterprise-beta" in text
    assert "deploy-assisted-intake-routing" in text
    assert "ready_for_resolver_candidate_packet" in text
    assert "candidate_packet_with_runtime_block" in text
    assert "proceed_to_automatic_semantic_supply_pre_runtime_v1_package" in text
    assert (
        "PR200 Decision Work Automatic Semantic Supply Pre-Runtime v1 Package Gate v0"
        in text
    )
    assert "Do not implement resolver approval" in text


def test_discoverability_docs_reference_pr199() -> None:
    expected = "Decision Work Generated Read Resolver Supply Review"
    for path in (
        DOC_PATH,
        ADAPTER_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr199_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            ADAPTER_DOC,
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


def test_pr199_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        ADAPTER_DOC,
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
