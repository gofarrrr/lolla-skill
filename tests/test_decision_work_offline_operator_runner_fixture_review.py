from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.decision_work_offline_operator_runner import (
    BLOCKED_PRIVACY_RISK,
    BLOCKED_SCHEMA_OR_CUSTODY_FAILURE,
    DEFERRED_MISSING_SEMANTIC_READ,
    DEFERRED_MISSING_TRIAGE,
    SIDECAR_READY_BLOCKED_STATE,
    SIDECAR_READY_FOR_EXPLICIT_WRITE,
    STOPPED_BEFORE_EXPLICIT_WRITE,
    run_decision_work_offline_operator,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-fixture-review-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-offline-operator-runner-fixture-review-v0/review.json"
)
ADAPTER_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-adapter-v0.md"
)
READINESS_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-sidecar-automation-readiness-prd-v0.md"
)
AUTOMATIC_SUPPLY_PRD = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
)
LAUNCH_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
LAUNCH_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-triage-generation-pilot-v0/triage.json"
)
DEPLOY_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-brief-rendering-pilot-v0/read.json"
)
DEPLOY_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-second-triage-pilot-v0/triage.json"
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


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _run(
    tmp_path: Path,
    *,
    case_id: str = "launch-public-enterprise-beta",
    read_path: Path = LAUNCH_READ,
    triage_path: Path = LAUNCH_TRIAGE,
    write_sidecar: bool = False,
) -> dict:
    return run_decision_work_offline_operator(
        completed_run_archive_dir=tmp_path / f"{case_id}_archive",
        generated_read_path=read_path,
        generated_triage_path=triage_path,
        case_id=case_id,
        safe_output_dir=tmp_path / f"{case_id}_runner_out",
        write_sidecar=write_sidecar,
        created_at="2026-07-04T00:00:00Z",
    )


def test_review_json_schema_gate_and_cases() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_offline_operator_runner_fixture_review.v0"
    )
    assert {case["case_id"] for case in review["reviewed_cases"]} == {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
    }
    assert review["decision_gate"] == "proceed_to_non_curated_completed_run_pilot_plan"
    assert review["recommended_next_pr"] == "PR228 Non-Curated Completed-Run Pilot Plan v0"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False


def test_launch_and_deploy_fixture_statuses_match_review(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)
    expected = {
        case["case_id"]: case["expected_runner_status"]
        for case in review["reviewed_cases"]
    }
    launch = _run(tmp_path)
    deploy = _run(
        tmp_path,
        case_id="deploy-assisted-intake-routing",
        read_path=DEPLOY_READ,
        triage_path=DEPLOY_TRIAGE,
    )

    assert launch["final_status"] == expected["launch-public-enterprise-beta"]
    assert launch["final_status"] == SIDECAR_READY_FOR_EXPLICIT_WRITE
    assert deploy["final_status"] == expected["deploy-assisted-intake-routing"]
    assert deploy["final_status"] == SIDECAR_READY_BLOCKED_STATE
    assert deploy["runtime_use_status"]["status"] == "blocked"
    assert deploy["user_surface_status"]["status"] == "blocked"
    for summary in (launch, deploy):
        assert summary["write_attempted"] is False
        assert summary["actual_sidecar_write_performed"] is False
        assert summary["archive_mutated"] is False
        assert summary["historical_archive_mutated"] is False
        assert summary["resolver_refs_approved"] is False
        assert summary["runtime_wiring_changed"] is False


def test_blocker_fixture_states_match_review(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)["reviewed_blocker_fixture_states"]
    missing_read = _run(tmp_path, read_path=tmp_path / "missing_read.json")
    missing_triage = _run(tmp_path, triage_path=tmp_path / "missing_triage.json")

    rejected_read_path = tmp_path / "rejected_read.json"
    rejected_payload = _json(LAUNCH_READ)
    rejected_payload.setdefault("custody_flags", {})["product_proof"] = True
    rejected_read_path.write_text(
        json.dumps(rejected_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rejected = _run(tmp_path, read_path=rejected_read_path)

    privacy_read_path = tmp_path / "privacy_read.json"
    privacy_payload = _json(LAUNCH_READ)
    privacy_payload["operator_note"] = "SEC" + "RET"
    privacy_read_path.write_text(
        json.dumps(privacy_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    privacy = _run(tmp_path, read_path=privacy_read_path)

    local_path_read = tmp_path / "local_path_read.json"
    local_path_payload = _json(LAUNCH_READ)
    local_path_payload["operator_note"] = "/" + "Users" + "/example/private"
    local_path_read.write_text(
        json.dumps(local_path_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    local_path = _run(tmp_path, read_path=local_path_read)

    write_attempt = _run(tmp_path, write_sidecar=True)

    assert missing_read["final_status"] == review["missing_generated_read"]
    assert missing_read["final_status"] == DEFERRED_MISSING_SEMANTIC_READ
    assert missing_triage["final_status"] == review["missing_generated_triage"]
    assert missing_triage["final_status"] == DEFERRED_MISSING_TRIAGE
    assert rejected["final_status"] == review["rejected_intake"]
    assert rejected["final_status"] == BLOCKED_SCHEMA_OR_CUSTODY_FAILURE
    assert privacy["final_status"] == review["privacy_marker"]
    assert privacy["final_status"] == BLOCKED_PRIVACY_RISK
    assert local_path["final_status"] == review["local_absolute_path_marker"]
    assert local_path["final_status"] == BLOCKED_PRIVACY_RISK
    assert write_attempt["final_status"] == review["write_attempt"]
    assert write_attempt["final_status"] == STOPPED_BEFORE_EXPLICIT_WRITE
    assert "write_mode_not_supported_in_runner_v0" in write_attempt["blocker_reasons"]


def test_runner_fixture_review_checks_no_sidecar_outputs(tmp_path: Path) -> None:
    _run(tmp_path)
    _run(
        tmp_path,
        case_id="deploy-assisted-intake-routing",
        read_path=DEPLOY_READ,
        triage_path=DEPLOY_TRIAGE,
    )

    assert not list(tmp_path.rglob("decision_work"))


def test_runner_fixture_review_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            ADAPTER_DOC,
            READINESS_PRD,
            AUTOMATIC_SUPPLY_PRD,
            HISTORICAL_DISCOVERY_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_runner_fixture_review_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        ADAPTER_DOC,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        HISTORICAL_DISCOVERY_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
