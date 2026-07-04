from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_offline_operator_runner import (
    SIDECAR_READY_FOR_EXPLICIT_WRITE,
    run_decision_work_offline_operator,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-second-non-curated-completed-run-pilot-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-second-non-curated-completed-run-pilot-v0/review.json"
)
PR230_REVIEW_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-non-curated-pilot-review-v0.md"
)
PR229_PILOT_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-non-curated-completed-run-pilot-v0.md"
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
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
CASE_ID = "second-non-curated-existing-semantic-input-fixture"
ACCEPTED_STATUSES = {
    "sidecar_ready_for_explicit_write",
    "sidecar_ready_blocked_state",
    "blocked_runtime_or_user_surface_risk",
    "blocked_source_depth_insufficient",
    "blocked_schema_or_custody_failure",
    "runner_failed_closed",
}
EXPECTED_STEPS = [
    "generated_read_intake",
    "brief_supply",
    "rendered_brief",
    "triage_supply",
    "resolver_supply",
    "sidecar_update_packet",
    "sidecar_write_dry_run",
]
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


def _fixture_archive(tmp_path: Path) -> Path:
    archive = tmp_path / "second_non_curated_archive_fixture"
    archive.mkdir()
    (archive / "metadata.json").write_text(
        json.dumps(
            {
                "case_id": CASE_ID,
                "fixture_kind": "synthetic_completed_run_like_fixture",
                "raw_private_content_included": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (archive / "completed.json").write_text(
        json.dumps(
            {
                "completed": True,
                "fixture_only": True,
                "real_historical_archive": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return archive


def _run_pilot(tmp_path: Path) -> dict[str, Any]:
    return run_decision_work_offline_operator(
        completed_run_archive_dir=_fixture_archive(tmp_path),
        generated_read_path=LAUNCH_READ,
        generated_triage_path=LAUNCH_TRIAGE,
        case_id=CASE_ID,
        safe_output_dir=tmp_path / "runner_output",
        created_at="2026-07-04T00:00:00Z",
    )


def test_review_json_schema_status_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert review["schema_version"] == (
        "lolla.decision_work_second_non_curated_completed_run_pilot_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_tests_temp_runner_outputs_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["runner_outcome"]["final_status"] == SIDECAR_READY_FOR_EXPLICIT_WRITE
    assert review["decision_gate"] == "proceed_to_second_non_curated_pilot_review"
    assert review["recommended_next_pr"] == "PR232 Second Non-Curated Pilot Review v0"


def test_temp_second_non_curated_runner_pilot_matches_review(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)
    summary = _run_pilot(tmp_path)

    assert summary["case_id"] == CASE_ID
    assert summary["final_status"] == review["runner_outcome"]["final_status"]
    assert summary["final_status"] in ACCEPTED_STATUSES
    assert summary["final_status"] == SIDECAR_READY_FOR_EXPLICIT_WRITE
    assert summary["stopped_at"] == review["runner_outcome"]["stopped_at"]
    assert summary["completed_steps"] == EXPECTED_STEPS
    assert summary["skipped_steps"] == []
    assert summary["missing_required_inputs"] == []
    assert summary["blocker_reasons"] == []
    assert summary["deferred_reasons"] == []
    assert "manual_explicit_write_available_as_next_step" in (
        summary["operator_attention_items"]
    )
    assert summary["actual_sidecar_write_performed"] is False
    assert summary["archive_mutated"] is False
    assert summary["historical_archive_mutated"] is False
    assert summary["resolver_refs_approved"] is False
    assert summary["runtime_wiring_changed"] is False
    assert summary["runtime_use_status"]["status"] == "blocked"
    assert summary["user_surface_status"]["status"] == "not_established"
    assert not list(tmp_path.rglob("decision_work"))


def test_runner_cli_second_non_curated_summary_is_temp_only(tmp_path: Path) -> None:
    archive = _fixture_archive(tmp_path)
    out_dir = tmp_path / "runner_cli_output"
    out = out_dir / "runner_summary.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/run_decision_work_offline_operator.py",
            "--completed-run-archive-dir",
            str(archive),
            "--generated-read",
            str(LAUNCH_READ),
            "--generated-triage",
            str(LAUNCH_TRIAGE),
            "--case-id",
            CASE_ID,
            "--safe-output-dir",
            str(out_dir),
            "--out",
            str(out),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = _json(out)
    assert payload["final_status"] == SIDECAR_READY_FOR_EXPLICIT_WRITE
    assert payload["stopped_at"] == "dry_run_complete"
    assert payload["completed_steps"] == EXPECTED_STEPS
    assert payload["actual_sidecar_write_performed"] is False
    assert payload["archive_mutated"] is False
    assert payload["resolver_refs_approved"] is False
    assert not list(tmp_path.rglob("decision_work"))


def test_pilot_doc_explains_fixture_inputs_depth_and_boundary() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in (
        CASE_ID,
        "synthetic and temp-only",
        "existing checked-in-safe semantic inputs",
        "inputs are existing checked-in-safe launch-like artifacts",
        "tests runner orchestration depth",
        "does not prove that a new non-curated conversation has been semantically understood",
        "sidecar_ready_for_explicit_write",
        "generated_read_intake",
        "brief_supply",
        "rendered_brief",
        "triage_supply",
        "resolver_supply",
        "sidecar_update_packet",
        "sidecar_write_dry_run",
        "dry_run_complete",
        "actual_sidecar_write_performed: false",
        "runtime use remains blocked",
        "user-surface readiness is not established",
        "enough to justify a review, not a package gate",
        "proceed_to_second_non_curated_pilot_review",
    ):
        assert phrase in text


def test_review_records_limitation_and_non_claims() -> None:
    review = _json(REVIEW_PATH)

    assert review["semantic_inputs"]["inputs_existing_checked_in_safe"] is True
    assert review["semantic_inputs"]["inputs_reused_from_existing_launch_like_pair"]
    assert review["semantic_inputs"]["new_semantic_material_created"] is False
    assert "tests runner depth" in review["semantic_inputs"]["limitation"]
    assert review["review_questions"]["runner_progressed_beyond_generated_read"] is True
    assert review["review_questions"]["deterministic_downstream_steps_temp_only"] is True
    assert review["review_questions"]["enough_for_package_gate"] is False
    assert review["review_questions"]["needs_review_before_package_gate"] is True
    assert review["fabrication_checks"]["semantic_meaning_inferred"] is False
    assert review["fabrication_checks"]["generated_read_created_or_repaired"] is False
    assert review["fabrication_checks"]["generated_triage_created_or_repaired"] is False
    assert review["write_and_archive_boundary"]["actual_sidecar_write_performed"] is False
    assert review["write_and_archive_boundary"]["archive_mutated"] is False
    assert review["write_and_archive_boundary"]["checked_in_decision_work_directory_created"] is False


def test_pilot_discoverability_references() -> None:
    expected = "Decision Work Second Non-Curated Completed-Run Pilot"
    for path in (
        DOC_PATH,
        PR230_REVIEW_DOC,
        PR229_PILOT_DOC,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr231_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR230_REVIEW_DOC,
            PR229_PILOT_DOC,
            READINESS_PRD,
            AUTOMATIC_SUPPLY_PRD,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0
    assert result["summary"]["info_count"] == 0


def test_pr231_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR230_REVIEW_DOC,
        PR229_PILOT_DOC,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_STRINGS:
            assert forbidden not in text, (path, forbidden)
