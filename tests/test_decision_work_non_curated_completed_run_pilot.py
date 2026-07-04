from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_offline_operator_runner import (
    DEFERRED_MISSING_SEMANTIC_READ,
    run_decision_work_offline_operator,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-non-curated-completed-run-pilot-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-non-curated-completed-run-pilot-v0/review.json"
)
PLAN_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-non-curated-completed-run-pilot-plan-v0.md"
)
RUNNER_REVIEW = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-offline-operator-runner-fixture-review-v0.md"
)
RUNNER_ADAPTER = (
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
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
CASE_ID = "non-curated-sanitized-missing-read-fixture"
ACCEPTED_STATUSES = {
    "sidecar_ready_for_explicit_write",
    "sidecar_ready_blocked_state",
    "deferred_missing_semantic_read",
    "deferred_missing_triage",
    "blocked_privacy_risk",
    "blocked_source_depth_insufficient",
    "blocked_schema_or_custody_failure",
    "blocked_runtime_or_user_surface_risk",
    "runner_failed_closed",
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


def _fixture_archive(tmp_path: Path) -> Path:
    archive = tmp_path / "synthetic_completed_run_archive"
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
        generated_read_path=tmp_path / "missing_generated_read.json",
        generated_triage_path=tmp_path / "missing_generated_triage.json",
        case_id=CASE_ID,
        safe_output_dir=tmp_path / "runner_output",
        created_at="2026-07-04T00:00:00Z",
    )


def test_review_json_schema_status_and_gate() -> None:
    review = _json(REVIEW_PATH)

    assert (
        review["schema_version"]
        == "lolla.decision_work_non_curated_completed_run_pilot_review.v0"
    )
    assert review["review_metadata"]["mode"] == "docs_tests_temp_runner_outputs_only"
    assert review["review_metadata"]["model_calls"] == 0
    assert review["review_metadata"]["lolla_invoked"] is False
    assert review["review_metadata"]["runtime_wired"] is False
    assert review["review_metadata"]["queue_worker_added"] is False
    assert review["review_metadata"]["resolver_refs_approved"] is False
    assert review["runner_outcome"]["final_status"] == DEFERRED_MISSING_SEMANTIC_READ
    assert review["decision_gate"] == "proceed_to_non_curated_pilot_review"
    assert review["recommended_next_pr"] == "PR230 Non-Curated Pilot Review v0"


def test_temp_non_curated_runner_pilot_matches_review(tmp_path: Path) -> None:
    review = _json(REVIEW_PATH)
    summary = _run_pilot(tmp_path)

    assert summary["case_id"] == CASE_ID
    assert summary["final_status"] == review["runner_outcome"]["final_status"]
    assert summary["final_status"] in ACCEPTED_STATUSES
    assert summary["stopped_at"] == review["runner_outcome"]["stopped_at"]
    assert summary["missing_required_inputs"] == ["generated_read"]
    assert summary["deferred_reasons"] == ["generated_read_missing"]
    assert summary["blocker_reasons"] == []
    assert summary["operator_attention_items"] == []
    assert summary["completed_steps"] == []
    assert summary["skipped_steps"] == review["runner_outcome"]["skipped_steps"]
    assert summary["write_attempted"] is False
    assert summary["actual_sidecar_write_performed"] is False
    assert summary["archive_mutated"] is False
    assert summary["historical_archive_mutated"] is False
    assert summary["resolver_refs_approved"] is False
    assert summary["runtime_wiring_changed"] is False
    assert not list(tmp_path.rglob("decision_work"))


def test_runner_cli_non_curated_pilot_summary_is_temp_only(tmp_path: Path) -> None:
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
            str(tmp_path / "missing_generated_read.json"),
            "--generated-triage",
            str(tmp_path / "missing_generated_triage.json"),
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
    assert payload["final_status"] == DEFERRED_MISSING_SEMANTIC_READ
    assert payload["actual_sidecar_write_performed"] is False
    assert payload["archive_mutated"] is False
    assert payload["resolver_refs_approved"] is False
    assert not list(tmp_path.rglob("decision_work"))


def test_pilot_doc_explains_non_curated_inputs_missingness_and_boundary() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    for phrase in (
        "non-curated-sanitized-missing-read-fixture",
        "not `launch-public-enterprise-beta`",
        "not `deploy-assisted-intake-routing`",
        "generated read JSON",
        "generated triage JSON",
        "deferred_missing_semantic_read",
        "missing_required_inputs",
        "deferred_reasons",
        "stopped_at",
        "operator_attention_items",
        "No source-depth status is available",
        "No runtime/user-surface status is available",
        "does not create a misleading sense of approval or readiness",
    ):
        assert phrase in text
    assert "does not infer a runtime or user-surface state" in text
    assert "does not pretend the runner knows what the conversation means" in text


def test_pilot_preserves_no_unknowns_taxonomy_and_non_claims() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    review = _json(REVIEW_PATH)

    assert review["missingness_visibility"]["new_unknowns_schema_created"] is False
    assert (
        review["missingness_visibility"][
            "known_known_known_unknown_taxonomy_created"
        ]
        is False
    )
    assert review["missingness_visibility"]["semantic_meaning_inferred"] is False
    assert "does not prove" in text
    for phrase in (
        "$lolla",
        "Lolla skill",
        "models/providers",
        "generate or repair interpretation reads",
        "queue worker",
        "wire runtime",
        "approve resolver refs",
        "write sidecars",
        "mutate archives",
        "answer quality was scored",
        "any action is authorized",
    ):
        assert phrase in text


def test_pilot_discoverability_references() -> None:
    expected = "Decision Work Non-Curated Completed-Run Pilot"
    for path in (
        DOC_PATH,
        PLAN_DOC,
        RUNNER_REVIEW,
        RUNNER_ADAPTER,
        READINESS_PRD,
        AUTOMATIC_SUPPLY_PRD,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr229_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PLAN_DOC,
            RUNNER_REVIEW,
            RUNNER_ADAPTER,
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


def test_pr229_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PLAN_DOC,
        RUNNER_REVIEW,
        RUNNER_ADAPTER,
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
