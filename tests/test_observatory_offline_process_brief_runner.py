from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.observatory_process_brief_runner import (
    NEEDS_SAFE_INPUTS,
    OBSERVATORY_PROCESS_BRIEF_RUNNER_SCHEMA_VERSION,
    OFFLINE_COMMAND_AVAILABLE,
    OFFLINE_RUNNER_SUMMARY_READY,
    PROCESS_BRIEF_ALREADY_ATTACHED,
    prepare_observatory_process_brief,
    render_observatory_process_brief_runner_json,
    write_observatory_process_brief_runner_json,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "engine/system_b/observatory_process_brief_runner.py"
SCRIPT = REPO_ROOT / "scripts/evals/prepare_observatory_process_brief.py"
DOC = REPO_ROOT / "docs/product/observatory-offline-process-brief-runner-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-offline-process-brief-runner-v0/"
    "review.json"
)
LAUNCH_READ = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/"
    "read.json"
)
LAUNCH_TRIAGE = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-generated-read-triage-generation-pilot-v0/"
    "triage.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict[str, Any]:
    return json.loads(_read(path))


def _completed_run(tmp_path: Path, name: str = "run") -> Path:
    run_dir = tmp_path / "archive" / "case" / name
    run_dir.mkdir(parents=True)
    (run_dir / "result.json").write_text(
        json.dumps(
            {
                "schema_version": "fixture.result.v0",
                "extraction": {"decision_situation": "Prepare process brief?"},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "extraction.json").write_text(
        json.dumps({"status": "available"}),
        encoding="utf-8",
    )
    (run_dir / "revised.txt").write_text(
        "Safe revised-answer placeholder for fixture use only.",
        encoding="utf-8",
    )
    return run_dir


def _safe_output(tmp_path: Path) -> Path:
    return tmp_path / "process-brief-output"


def test_runner_doc_review_and_readme_are_indexed() -> None:
    assert MODULE.exists()
    assert SCRIPT.exists()
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Offline Process Brief Runner" in readme
    assert "observatory-offline-process-brief-runner-v0.md" in readme


def test_missing_inputs_returns_needs_safe_inputs(tmp_path: Path) -> None:
    state = prepare_observatory_process_brief(
        selected_case_id="launch-public-enterprise-beta",
        completed_run_archive_dir=_completed_run(tmp_path),
        safe_output_dir=_safe_output(tmp_path),
        created_at="2026-07-06T00:00:00Z",
    )

    assert state["schema_version"] == OBSERVATORY_PROCESS_BRIEF_RUNNER_SCHEMA_VERSION
    assert state["prepare_process_brief_status"] == NEEDS_SAFE_INPUTS
    assert state["next_action"] == "supply_generated_read_and_triage"
    assert state["missing_required_inputs"] == [
        "generated_read",
        "generated_triage",
    ]
    assert state["operator_command"] is None
    assert state["runner_summary"] is None
    assert state["custody_flags"]["runs_offline_operator"] is False
    assert state["custody_flags"]["provider_or_model_calls_used"] is False
    assert state["custody_flags"]["creates_interpretation_read"] is False
    assert state["custody_flags"]["writes_sidecar"] is False


def test_existing_sidecar_stops_at_view_receipt(tmp_path: Path) -> None:
    run_dir = _completed_run(tmp_path)
    sidecar = run_dir / "decision_work"
    sidecar.mkdir()
    (sidecar / "attachment_status.json").write_text(
        json.dumps({"attachment_state": "generated"}),
        encoding="utf-8",
    )
    (sidecar / "user_receipt.md").write_text(
        "# Decision Work Brief: available\n\nNot proof that advice is correct.\n",
        encoding="utf-8",
    )

    state = prepare_observatory_process_brief(
        selected_case_id="launch-public-enterprise-beta",
        completed_run_archive_dir=run_dir,
        safe_output_dir=_safe_output(tmp_path),
        generated_read_path=LAUNCH_READ,
        generated_triage_path=LAUNCH_TRIAGE,
        run_offline_operator=True,
        created_at="2026-07-06T00:00:00Z",
    )

    assert state["prepare_process_brief_status"] == PROCESS_BRIEF_ALREADY_ATTACHED
    assert state["next_action"] == "view_receipt"
    assert state["decision_work_status"]["available"] is True
    assert state["runner_summary"] is None
    assert not (_safe_output(tmp_path) / "runner_summary.json").exists()


def test_safe_inputs_return_copyable_command_without_running(tmp_path: Path) -> None:
    state = prepare_observatory_process_brief(
        selected_case_id="launch-public-enterprise-beta",
        completed_run_archive_dir=_completed_run(tmp_path),
        safe_output_dir=_safe_output(tmp_path),
        generated_read_path=LAUNCH_READ,
        generated_triage_path=LAUNCH_TRIAGE,
        created_at="2026-07-06T00:00:00Z",
    )

    assert state["prepare_process_brief_status"] == OFFLINE_COMMAND_AVAILABLE
    assert state["next_action"] == "copy_offline_command"
    command = state["operator_command"]
    assert command["mode"] == "cli_first"
    assert "scripts/evals/run_decision_work_offline_operator.py" in command["argv"]
    assert command["writes_sidecar"] is False
    assert command["mutates_archive"] is False
    assert command["calls_provider_or_model"] is False
    assert state["runner_summary"] is None


def test_run_now_delegates_to_existing_runner_without_sidecar_write(
    tmp_path: Path,
) -> None:
    run_dir = _completed_run(tmp_path)
    output_dir = _safe_output(tmp_path)

    state = prepare_observatory_process_brief(
        selected_case_id="launch-public-enterprise-beta",
        completed_run_archive_dir=run_dir,
        safe_output_dir=output_dir,
        generated_read_path=LAUNCH_READ,
        generated_triage_path=LAUNCH_TRIAGE,
        run_offline_operator=True,
        created_at="2026-07-06T00:00:00Z",
    )

    assert state["prepare_process_brief_status"] == OFFLINE_RUNNER_SUMMARY_READY
    assert state["next_action"] == "review_runner_summary_then_explicit_attach"
    assert state["runner_summary"]["final_status"] == "sidecar_ready_for_explicit_write"
    assert state["runner_summary"]["actual_sidecar_write_performed"] is False
    assert state["runner_summary"]["archive_mutated"] is False
    assert state["runner_summary"]["runtime_wiring_changed"] is False
    assert state["runner_summary"]["resolver_refs_approved"] is False
    assert state["custody_flags"]["runs_offline_operator"] is True
    assert state["custody_flags"]["writes_sidecar"] is False
    assert (output_dir / "runner_summary.json").exists()
    assert not (run_dir / "decision_work").exists()


def test_cli_writes_state_json_without_running_when_inputs_missing(
    tmp_path: Path,
) -> None:
    output_dir = _safe_output(tmp_path)
    out = output_dir / "state.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--case-id",
            "launch-public-enterprise-beta",
            "--completed-run-archive-dir",
            str(_completed_run(tmp_path)),
            "--safe-output-dir",
            str(output_dir),
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
    assert payload["prepare_process_brief_status"] == NEEDS_SAFE_INPUTS
    assert payload["missing_required_inputs"] == [
        "generated_read",
        "generated_triage",
    ]
    assert payload["custody_flags"]["runs_offline_operator"] is False


def test_state_writer_refuses_repo_and_decision_work_outputs(tmp_path: Path) -> None:
    payload = render_observatory_process_brief_runner_json(
        {"schema_version": OBSERVATORY_PROCESS_BRIEF_RUNNER_SCHEMA_VERSION}
    )

    safe = tmp_path / "safe" / "state.json"
    write_observatory_process_brief_runner_json(safe, payload)
    assert safe.exists()

    for bad in [
        REPO_ROOT / "tmp-process-brief-state.json",
        tmp_path / "decision_work" / "state.json",
    ]:
        try:
            write_observatory_process_brief_runner_json(bad, payload)
        except Exception as exc:  # noqa: BLE001 - concrete error tested by text.
            assert "repo_path" in str(exc) or "decision_work" in str(exc)
        else:  # pragma: no cover - defensive assertion branch.
            raise AssertionError(f"expected refusal for {bad}")


def test_doc_review_and_artifacts_preserve_boundaries() -> None:
    doc = _read(DOC)
    normalized_doc = " ".join(doc.split())
    review = json.loads(_read(REVIEW))

    assert "generated interpretation read remains an explicit safe input" in doc
    assert "does not add an Observatory browser button yet" in normalized_doc
    assert review["implemented"]["observatory_browser_action_added"] is False
    assert review["implemented"]["new_observatory_api_route_added"] is False
    assert review["boundary"]["creates_interpretation_read"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["writes_sidecar"] is False
    assert review["boundary"]["mutates_archive"] is False
    assert review["boundary"]["changes_runtime_behavior"] is False
    assert review["boundary"]["touches_skill_md"] is False
    assert review["boundary"]["touches_scripts_skill"] is False
    assert review["boundary"]["touches_archive_run"] is False


def test_boundary_lint_and_private_marker_scan() -> None:
    report = lint_product_delta_paths([DOC, REVIEW])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }

    text = _read(DOC) + _read(REVIEW) + _read(MODULE) + _read(SCRIPT)
    for forbidden in [
        "/" + "Users/",
        "Desktop/" + "Apps",
        "product_proof\": true",
        "human_validated\": true",
        "answer_correctness\": true",
        "advice_correctness\": true",
        "agent_action_authorized\": true",
        "automatic_action_authorized\": true",
        "calls_provider_or_model\": true",
        "writes_sidecar\": true",
        "mutates_archive\": true",
        "changes_runtime_behavior\": true",
    ]:
        assert forbidden not in text
