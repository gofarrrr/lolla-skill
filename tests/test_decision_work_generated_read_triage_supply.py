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
from engine.system_b.decision_work_generated_read_triage_supply import (
    READY_STATUS,
    TRIAGE_SUPPLY_SCHEMA_VERSION,
    build_generated_read_triage_supply,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT / "engine/system_b/decision_work_generated_read_triage_supply.py"
)
SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/build_decision_work_generated_read_triage_supply.py"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-supply-adapter-v0.md"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-triage-supply-plan-v0.md"
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
    / "docs/conversation-understanding/decision-work-generated-read-rendered-launch-public-enterprise-beta-v0.md"
)
DEPLOY_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/read.json"
)
DEPLOY_INTAKE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-second-brief-rendering-pilot-v0/intake.json"
)
DEPLOY_RENDERED = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-read-rendered-deploy-assisted-intake-routing-v0.md"
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(tmp_path: Path, name: str, payload: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _brief_supply_path(
    tmp_path: Path,
    *,
    read_path: Path = LAUNCH_READ,
    intake_path: Path = LAUNCH_INTAKE,
    name: str = "brief_supply.json",
) -> Path:
    supply = build_generated_read_brief_supply(
        read_path=read_path,
        intake_path=intake_path,
        created_at="2026-07-03T00:00:00Z",
    )
    path = tmp_path / name
    path.write_text(
        render_generated_read_brief_supply_json(supply, pretty=True),
        encoding="utf-8",
    )
    return path


def _mutable_case_paths(
    tmp_path: Path,
    *,
    read_payload: dict[str, Any] | None = None,
    intake_payload: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    read = copy.deepcopy(read_payload if read_payload is not None else _json(LAUNCH_READ))
    intake = copy.deepcopy(
        intake_payload if intake_payload is not None else _json(LAUNCH_INTAKE)
    )
    read_path = _write_json(tmp_path, "read.json", read)
    intake["source_read_ref"] = read_path.name
    intake_path = _write_json(tmp_path, "intake.json", intake)
    return read_path, intake_path


def test_launch_artifacts_produce_ready_triage_supply(tmp_path: Path) -> None:
    supply_path = _brief_supply_path(tmp_path, name="launch_supply.json")
    result = build_generated_read_triage_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["schema_version"] == TRIAGE_SUPPLY_SCHEMA_VERSION
    assert result["triage_supply_status"] == READY_STATUS
    assert result["blocker_reasons"] == []
    assert result["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert {item["field_name"] for item in result["allowed_routing_inputs"]} == {
        "decision_question",
        "revised_direction_or_action_consequence",
        "evidence_gates",
        "what_the_final_answer_does_not_prove",
    }
    assert result["required_source_refs"]["status"] == "passed"
    assert result["uncertainty_summary"]["status"] == "passed"
    assert result["privacy_summary"]["status"] == "passed"
    downstream = result["downstream_allowed"]
    assert downstream["can_generate_offline_triage"] is True
    assert downstream["can_update_sidecar"] is False
    assert downstream["can_approve_resolver_refs"] is False
    assert downstream["can_authorize_agent_action"] is False
    assert downstream["can_authorize_automatic_action"] is False
    assert downstream["can_be_used_as_quality_label"] is False


def test_deploy_artifacts_produce_ready_triage_supply(tmp_path: Path) -> None:
    supply_path = _brief_supply_path(
        tmp_path,
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        name="deploy_supply.json",
    )
    result = build_generated_read_triage_supply(
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        brief_supply_path=supply_path,
        rendered_brief_path=DEPLOY_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["triage_supply_status"] == READY_STATUS
    assert result["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert result["source_case"]["decision_family"] == (
        "healthcare_operations_or_deployment"
    )
    assert "legal_or_compliance_review_recommended" in result["route_categories_allowed"]
    assert "correct_advice" in result["route_categories_forbidden"]


def test_rejected_intake_is_blocked(tmp_path: Path) -> None:
    intake = _json(LAUNCH_INTAKE)
    intake["intake_status"] = "rejected_quality_label"
    intake["accepted_for_downstream"] = False
    intake["downstream_allowed"]["can_feed_brief"] = False
    read_path, intake_path = _mutable_case_paths(tmp_path, intake_payload=intake)
    supply_path = _brief_supply_path(
        tmp_path,
        read_path=read_path,
        intake_path=intake_path,
    )

    result = build_generated_read_triage_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["triage_supply_status"] == "blocked_intake_not_accepted"
    assert result["allowed_routing_inputs"] == []
    assert result["downstream_allowed"]["can_generate_offline_triage"] is False


def test_non_ready_brief_supply_is_blocked(tmp_path: Path) -> None:
    supply_path = _brief_supply_path(tmp_path)
    supply = _json(supply_path)
    supply["supply_status"] = "deferred_missing_required_fields"
    supply["blocker_reasons"] = ["missing_required_fields"]
    supply_path.write_text(json.dumps(supply, indent=2, sort_keys=True), encoding="utf-8")

    result = build_generated_read_triage_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["triage_supply_status"] == "blocked_brief_supply_not_ready"
    assert result["downstream_allowed"]["can_generate_offline_triage"] is False


def test_missing_rendered_brief_is_deferred(tmp_path: Path) -> None:
    supply_path = _brief_supply_path(tmp_path)

    result = build_generated_read_triage_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=supply_path,
        rendered_brief_path=tmp_path / "missing.md",
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["triage_supply_status"] == "deferred_missing_rendered_brief"
    assert "rendered_brief_missing" in result["blocker_reasons"]


def test_missing_brief_supply_is_deferred(tmp_path: Path) -> None:
    result = build_generated_read_triage_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=tmp_path / "missing_supply.json",
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["triage_supply_status"] == "deferred_missing_brief_supply"
    assert "brief_supply_missing" in result["blocker_reasons"]


def test_missing_source_refs_are_blocked(tmp_path: Path) -> None:
    read = _json(LAUNCH_READ)
    read["interpreted_fields"][0]["source_refs"] = []
    read_path, intake_path = _mutable_case_paths(tmp_path, read_payload=read)
    ready_supply = _brief_supply_path(tmp_path, name="ready_supply.json")

    result = build_generated_read_triage_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=ready_supply,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["triage_supply_status"] == "blocked_missing_source_refs"
    assert result["required_source_refs"]["missing_source_ref_fields"] == [
        "decision_question"
    ]


def test_missing_uncertainty_is_blocked(tmp_path: Path) -> None:
    read = _json(LAUNCH_READ)
    del read["interpreted_fields"][0]["uncertainty"]
    read_path, intake_path = _mutable_case_paths(tmp_path, read_payload=read)
    ready_supply = _brief_supply_path(tmp_path, name="ready_supply.json")

    result = build_generated_read_triage_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=ready_supply,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["triage_supply_status"] == "blocked_missing_uncertainty"
    assert result["uncertainty_summary"]["missing_uncertainty_fields"] == [
        "decision_question"
    ]


def test_privacy_markers_and_local_paths_are_blocked(tmp_path: Path) -> None:
    read = _json(LAUNCH_READ)
    read["interpreted_fields"][0]["source_refs"][0]["artifact"] = (
        "/" + "Users" + "/example/private/archive/result.json"
    )
    read_path, intake_path = _mutable_case_paths(tmp_path, read_payload=read)
    ready_supply = _brief_supply_path(tmp_path, name="ready_supply.json")
    result = build_generated_read_triage_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=ready_supply,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )
    assert result["triage_supply_status"] == "blocked_privacy_risk"
    assert result["privacy_summary"]["local_absolute_path_detected"] is True

    read = _json(LAUNCH_READ)
    read["read_metadata"]["notes"].append("SEC" + "RET")
    read_path, intake_path = _mutable_case_paths(tmp_path, read_payload=read)
    result = build_generated_read_triage_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=ready_supply,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )
    assert result["triage_supply_status"] == "blocked_privacy_risk"
    assert result["privacy_summary"]["privacy_marker_detected"] is True


def test_authority_proof_scoring_and_action_claims_are_blocked(tmp_path: Path) -> None:
    ready_supply = _brief_supply_path(tmp_path, name="ready_supply.json")
    for flag in (
        "product_proof",
        "human_validated",
        "answer_quality_scored",
        "agent_action_authorized",
        "automatic_action_authorized",
    ):
        read = _json(LAUNCH_READ)
        read["custody_flags"][flag] = True
        read_path, intake_path = _mutable_case_paths(tmp_path, read_payload=read)
        result = build_generated_read_triage_supply(
            read_path=read_path,
            intake_path=intake_path,
            brief_supply_path=ready_supply,
            rendered_brief_path=LAUNCH_RENDERED,
            created_at="2026-07-03T00:00:00Z",
        )
        assert result["triage_supply_status"] == "blocked_authority_claim", flag
        assert f"{flag}_claimed" in result["blocker_reasons"]


def test_cli_writes_valid_triage_supply_json(tmp_path: Path) -> None:
    supply_path = _brief_supply_path(tmp_path)
    out = tmp_path / "triage_supply.json"

    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--read",
            str(LAUNCH_READ),
            "--intake",
            str(LAUNCH_INTAKE),
            "--brief-supply",
            str(supply_path),
            "--rendered-brief",
            str(LAUNCH_RENDERED),
            "--out",
            str(out),
            "--pretty",
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    payload = _json(out)
    assert payload["schema_version"] == TRIAGE_SUPPLY_SCHEMA_VERSION
    assert payload["triage_supply_status"] == READY_STATUS
    assert payload["source_brief_supply_ref"] == "brief_supply.json"
    assert payload["downstream_allowed"]["can_update_sidecar"] is False
    assert payload["downstream_allowed"]["can_approve_resolver_refs"] is False


def test_source_artifacts_are_not_modified(tmp_path: Path) -> None:
    before = {
        LAUNCH_READ: LAUNCH_READ.read_text(encoding="utf-8"),
        LAUNCH_INTAKE: LAUNCH_INTAKE.read_text(encoding="utf-8"),
        LAUNCH_RENDERED: LAUNCH_RENDERED.read_text(encoding="utf-8"),
    }
    supply_path = _brief_supply_path(tmp_path)
    build_generated_read_triage_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        created_at="2026-07-03T00:00:00Z",
    )
    assert {path: path.read_text(encoding="utf-8") for path in before} == before


def test_doc_records_schema_statuses_cli_and_gate() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Triage Supply Adapter v0" in text
    assert "lolla.decision_work_generated_read_triage_supply.v0" in text
    assert "ready_for_offline_triage_generation" in text
    assert "deferred_missing_rendered_brief" in text
    assert "blocked_intake_not_accepted" in text
    assert "blocked_brief_supply_not_ready" in text
    assert "blocked_missing_source_refs" in text
    assert "blocked_missing_uncertainty" in text
    assert "blocked_privacy_risk" in text
    assert "blocked_authority_claim" in text
    assert "proceed_to_generated_read_triage_generation_pilot" in text
    assert "PR193 Decision Work Generated Read Triage Generation Pilot v0" in text
    assert "does not generate triage" in text
    assert "can_approve_resolver_refs" in text


def test_discoverability_docs_reference_pr192() -> None:
    expected = "Decision Work Generated Read Triage Supply Adapter"
    for path in (
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
        PRD_PATH,
        PLAN_DOC,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr192_docs_pass_product_delta_lint() -> None:
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


def test_pr192_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        MODULE_PATH,
        SCRIPT_PATH,
        PLAN_DOC,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
