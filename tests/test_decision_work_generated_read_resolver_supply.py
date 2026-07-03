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
    READY_STATUS,
    RESOLVER_SUPPLY_SCHEMA_VERSION,
    RUNTIME_BLOCK_STATUS,
    build_generated_read_resolver_supply,
)
from engine.system_b.decision_work_generated_read_triage_supply import (
    build_generated_read_triage_supply,
    render_generated_read_triage_supply_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    REPO_ROOT / "engine/system_b/decision_work_generated_read_resolver_supply.py"
)
SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/build_decision_work_generated_read_resolver_supply.py"
)
DOC_PATH = (
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


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(tmp_path: Path, name: str, payload: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _case_paths(
    tmp_path: Path,
    *,
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
    brief_supply_path = tmp_path / "brief_supply.json"
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
    triage_supply_path = tmp_path / "triage_supply.json"
    triage_supply_path.write_text(
        render_generated_read_triage_supply_json(triage_supply, pretty=True),
        encoding="utf-8",
    )
    return brief_supply_path, triage_supply_path


def _mutable_case_paths(
    tmp_path: Path,
    *,
    read_payload: dict[str, Any] | None = None,
    intake_payload: dict[str, Any] | None = None,
    triage_payload: dict[str, Any] | None = None,
) -> tuple[Path, Path, Path]:
    read = copy.deepcopy(read_payload if read_payload is not None else _json(LAUNCH_READ))
    intake = copy.deepcopy(
        intake_payload if intake_payload is not None else _json(LAUNCH_INTAKE)
    )
    triage = copy.deepcopy(
        triage_payload if triage_payload is not None else _json(LAUNCH_TRIAGE)
    )
    read_path = _write_json(tmp_path, "read.json", read)
    intake["source_read_ref"] = read_path.name
    intake_path = _write_json(tmp_path, "intake.json", intake)
    triage["source_generated_read_ref"] = read_path.name
    triage["source_intake_ref"] = intake_path.name
    triage_path = _write_json(tmp_path, "triage.json", triage)
    return read_path, intake_path, triage_path


def test_launch_artifacts_produce_resolver_candidate_packet(tmp_path: Path) -> None:
    brief_supply_path, triage_supply_path = _case_paths(tmp_path)

    result = build_generated_read_resolver_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=LAUNCH_TRIAGE,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["schema_version"] == RESOLVER_SUPPLY_SCHEMA_VERSION
    assert result["resolver_supply_status"] == READY_STATUS
    assert result["blocker_reasons"] == []
    assert result["source_case"]["case_id"] == "launch-public-enterprise-beta"
    assert result["route_summary"]["ordinary_caveated_offline_candidate"] is True
    assert result["runtime_use_status"]["can_update_sidecar"] is False
    assert result["downstream_allowed"]["resolver_refs_approved"] is False
    assert result["downstream_allowed"]["can_update_sidecar"] is False
    assert result["downstream_allowed"]["can_write_runtime_sidecar"] is False
    assert result["downstream_allowed"]["can_be_used_as_quality_label"] is False
    assert result["downstream_allowed"]["product_proof"] is False
    assert result["downstream_allowed"]["human_validated"] is False
    assert result["downstream_allowed"]["answer_quality_scored"] is False
    assert result["downstream_allowed"]["advice_correctness_claimed"] is False
    assert result["safe_ref_candidates"]


def test_deploy_artifacts_preserve_runtime_and_user_surface_block(tmp_path: Path) -> None:
    brief_supply_path, triage_supply_path = _case_paths(
        tmp_path,
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        rendered_path=DEPLOY_RENDERED,
        triage_path=DEPLOY_TRIAGE,
    )

    result = build_generated_read_resolver_supply(
        read_path=DEPLOY_READ,
        intake_path=DEPLOY_INTAKE,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=DEPLOY_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=DEPLOY_TRIAGE,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["resolver_supply_status"] == RUNTIME_BLOCK_STATUS
    assert result["source_case"]["case_id"] == "deploy-assisted-intake-routing"
    assert "agent_inspection_only" in result["route_summary"]["route_categories"]
    assert "not_ready_for_user_surface" in result["route_summary"]["route_categories"]
    assert "legal_or_compliance_review_recommended" in result["route_summary"][
        "high_review_routes"
    ]
    assert result["runtime_use_status"]["status"] == "blocked"
    assert result["user_surface_status"]["status"] == "blocked"
    assert result["agent_inspection_status"]["status"] == "inspection_only"
    assert result["required_operator_review"]["domain_review_required"] is True
    assert result["downstream_allowed"]["resolver_refs_approved"] is False
    assert result["downstream_allowed"]["can_write_runtime_sidecar"] is False


def test_rejected_intake_is_blocked(tmp_path: Path) -> None:
    intake = _json(LAUNCH_INTAKE)
    intake["intake_status"] = "rejected_quality_label"
    intake["accepted_for_downstream"] = False
    intake["downstream_allowed"]["can_feed_brief"] = False
    read_path, intake_path, triage_path = _mutable_case_paths(
        tmp_path,
        intake_payload=intake,
    )
    brief_supply_path, triage_supply_path = _case_paths(
        tmp_path,
        read_path=read_path,
        intake_path=intake_path,
    )

    result = build_generated_read_resolver_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=triage_path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["resolver_supply_status"] == "blocked_intake_not_accepted"
    assert result["safe_ref_candidates"] == []
    assert result["downstream_allowed"]["can_feed_future_resolver_review"] is False


def test_missing_triage_is_deferred(tmp_path: Path) -> None:
    brief_supply_path, triage_supply_path = _case_paths(tmp_path)

    result = build_generated_read_resolver_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=tmp_path / "missing_triage.json",
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["resolver_supply_status"] == "deferred_missing_triage"
    assert "triage_missing" in result["blocker_reasons"]


def test_missing_rendered_brief_is_deferred(tmp_path: Path) -> None:
    brief_supply_path, triage_supply_path = _case_paths(tmp_path)

    result = build_generated_read_resolver_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=tmp_path / "missing.md",
        triage_supply_path=triage_supply_path,
        triage_path=LAUNCH_TRIAGE,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["resolver_supply_status"] == "deferred_missing_rendered_brief"
    assert "rendered_brief_missing" in result["blocker_reasons"]


def test_non_ready_brief_supply_is_blocked_or_deferred(tmp_path: Path) -> None:
    brief_supply_path, triage_supply_path = _case_paths(tmp_path)
    supply = _json(brief_supply_path)
    supply["supply_status"] = "deferred_missing_required_fields"
    supply["blocker_reasons"] = ["missing_required_fields"]
    brief_supply_path.write_text(
        json.dumps(supply, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    result = build_generated_read_resolver_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=LAUNCH_TRIAGE,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["resolver_supply_status"] == "deferred_missing_brief_supply"
    assert result["downstream_allowed"]["can_feed_future_resolver_review"] is False


def test_missing_source_refs_are_blocked(tmp_path: Path) -> None:
    read = _json(LAUNCH_READ)
    read["interpreted_fields"][0]["source_refs"] = []
    read_path, intake_path, triage_path = _mutable_case_paths(
        tmp_path,
        read_payload=read,
    )
    brief_supply_path, triage_supply_path = _case_paths(
        tmp_path,
        read_path=read_path,
        intake_path=intake_path,
    )

    result = build_generated_read_resolver_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=triage_path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["resolver_supply_status"] == "requires_operator_repair"
    assert "missing_source_refs" in result["blocker_reasons"]
    assert result["required_source_refs"]["status"] == "blocked"


def test_missing_uncertainty_is_blocked(tmp_path: Path) -> None:
    triage = _json(LAUNCH_TRIAGE)
    del triage["route_explanations"][0]["uncertainty"]
    read_path, intake_path, triage_path = _mutable_case_paths(
        tmp_path,
        triage_payload=triage,
    )
    brief_supply_path, triage_supply_path = _case_paths(
        tmp_path,
        read_path=read_path,
        intake_path=intake_path,
    )

    result = build_generated_read_resolver_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=triage_path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["resolver_supply_status"] == "requires_operator_repair"
    assert "missing_uncertainty" in result["blocker_reasons"]
    assert result["uncertainty_summary"]["status"] == "blocked"


def test_privacy_markers_local_paths_and_authority_claims_are_blocked(
    tmp_path: Path,
) -> None:
    read = _json(LAUNCH_READ)
    read["interpreted_fields"][0]["source_refs"][0]["artifact"] = (
        "/" + "Users" + "/example/private/archive/result.json"
    )
    read_path, intake_path, triage_path = _mutable_case_paths(
        tmp_path,
        read_payload=read,
    )
    brief_supply_path, triage_supply_path = _case_paths(
        tmp_path,
        read_path=read_path,
        intake_path=intake_path,
    )
    result = build_generated_read_resolver_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=triage_path,
        created_at="2026-07-03T00:00:00Z",
    )
    assert result["resolver_supply_status"] == "blocked_privacy_risk"

    triage = _json(LAUNCH_TRIAGE)
    triage["custody_flags"]["resolver_refs_marked_usable"] = True
    read_path, intake_path, triage_path = _mutable_case_paths(
        tmp_path,
        triage_payload=triage,
    )
    brief_supply_path, triage_supply_path = _case_paths(
        tmp_path,
        read_path=read_path,
        intake_path=intake_path,
    )
    result = build_generated_read_resolver_supply(
        read_path=read_path,
        intake_path=intake_path,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=triage_path,
        created_at="2026-07-03T00:00:00Z",
    )
    assert result["resolver_supply_status"] == "blocked_authority_claim"


def test_source_artifacts_are_not_modified(tmp_path: Path) -> None:
    before = LAUNCH_TRIAGE.read_text(encoding="utf-8")
    brief_supply_path, triage_supply_path = _case_paths(tmp_path)

    build_generated_read_resolver_supply(
        read_path=LAUNCH_READ,
        intake_path=LAUNCH_INTAKE,
        brief_supply_path=brief_supply_path,
        rendered_brief_path=LAUNCH_RENDERED,
        triage_supply_path=triage_supply_path,
        triage_path=LAUNCH_TRIAGE,
        created_at="2026-07-03T00:00:00Z",
    )

    assert LAUNCH_TRIAGE.read_text(encoding="utf-8") == before


def test_cli_writes_valid_json_result(tmp_path: Path) -> None:
    brief_supply_path, triage_supply_path = _case_paths(tmp_path)
    out = tmp_path / "resolver_supply.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--read",
            str(LAUNCH_READ),
            "--intake",
            str(LAUNCH_INTAKE),
            "--brief-supply",
            str(brief_supply_path),
            "--rendered-brief",
            str(LAUNCH_RENDERED),
            "--triage-supply",
            str(triage_supply_path),
            "--triage",
            str(LAUNCH_TRIAGE),
            "--out",
            str(out),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert completed.stderr == ""
    payload = _json(out)
    assert payload["schema_version"] == RESOLVER_SUPPLY_SCHEMA_VERSION
    assert payload["resolver_supply_status"] == READY_STATUS


def test_docs_and_discoverability_reference_pr198() -> None:
    expected = "Decision Work Generated Read Resolver Supply Adapter"
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


def test_pr198_docs_pass_product_delta_lint() -> None:
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


def test_pr198_artifacts_contain_no_forbidden_markers() -> None:
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
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
