from __future__ import annotations

import json
import socket
import sys
import threading
import urllib.request
from contextlib import closing
from http.server import HTTPServer
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402


DOC = REPO_ROOT / "docs/product/observatory-prepare-process-brief-action-v0.md"
README = REPO_ROOT / "docs/product/README.md"
REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/observatory-prepare-process-brief-action-v0/"
    "review.json"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_run(run_dir: Path) -> Path:
    result_path = run_dir / "result.json"
    _write_json(
        result_path,
        {
            "usage_summary": {"run_id": "run-1"},
            "extraction": {"decision_situation": "Prepare a process brief?"},
        },
    )
    _write_json(run_dir / "extraction.json", {"status": "available"})
    return result_path


def _with_server(result_path: Path, callback):
    old_result = serve_result._RESULT
    old_result_path = serve_result._RESULT_PATH
    old_case_id = serve_result._CASE_ID
    old_mtime = serve_result._RESULT_MTIME

    serve_result._RESULT = json.loads(result_path.read_text(encoding="utf-8"))
    serve_result._RESULT_PATH = result_path
    serve_result._CASE_ID = "lolla-audit"
    serve_result._RESULT_MTIME = result_path.stat().st_mtime

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = HTTPServer(("127.0.0.1", port), serve_result.ResultHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        return callback(port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        serve_result._RESULT = old_result
        serve_result._RESULT_PATH = old_result_path
        serve_result._CASE_ID = old_case_id
        serve_result._RESULT_MTIME = old_mtime


def test_prepare_action_doc_review_and_readme_are_indexed() -> None:
    assert DOC.exists()
    assert REVIEW.exists()

    readme = _read(README)
    assert "Observatory Prepare Process Brief Action" in readme
    assert "observatory-prepare-process-brief-action-v0.md" in readme


def test_prepare_endpoint_returns_needs_safe_inputs_for_completed_run(
    tmp_path: Path,
) -> None:
    result_path = _write_run(tmp_path / "archive" / "case" / "run-1")

    payload = serve_result._build_process_brief_prepare_response(
        "lolla-audit",
        result_path,
        is_current=True,
    )

    assert payload["prepare_process_brief_status"] == "needs_safe_inputs"
    assert payload["next_action"] == "supply_generated_read_and_triage"
    assert payload["missing_required_inputs"] == [
        "generated_read",
        "generated_triage",
    ]
    assert payload["requested"]["run_offline_operator"] is False
    assert payload["custody_flags"]["runs_offline_operator"] is False
    assert payload["custody_flags"]["provider_or_model_calls_used"] is False
    assert payload["custody_flags"]["writes_sidecar"] is False
    assert payload["custody_flags"]["mutates_archive"] is False


def test_prepare_endpoint_detects_existing_sidecar(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive" / "case" / "run-1"
    result_path = _write_run(run_dir)
    sidecar = run_dir / "decision_work"
    sidecar.mkdir()
    _write_json(sidecar / "attachment_status.json", {"attachment_state": "generated"})
    (sidecar / "user_receipt.md").write_text(
        "# Decision Work Brief: available\n\nNot proof.\n",
        encoding="utf-8",
    )

    payload = serve_result._build_process_brief_prepare_response(
        "lolla-audit",
        result_path,
        is_current=True,
    )

    assert payload["prepare_process_brief_status"] == "process_brief_already_attached"
    assert payload["next_action"] == "view_receipt"
    assert payload["runner_summary"] is None


def test_prepare_api_route_smoke(tmp_path: Path) -> None:
    result_path = _write_run(tmp_path / "archive" / "case" / "run-1")

    def _fetch(port: int) -> dict:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/case/lolla-audit/decision-work/prepare",
            timeout=3,
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    payload = _with_server(result_path, _fetch)

    assert payload["schema_version"] == "lolla.observatory_process_brief_runner.v0"
    assert payload["prepare_process_brief_status"] == "needs_safe_inputs"
    assert payload["links"]["decision_work_api"] == (
        "/api/case/lolla-audit/decision-work"
    )


def test_injected_card_contains_prepare_action_without_compiled_bundle_change() -> None:
    html = serve_result._inject_telemetry_fab(b"<html><body></body></html>").decode(
        "utf-8"
    )

    assert "Prepare process brief" in html
    assert "processBriefEndpointFor" in html
    assert "data-lolla-prepare-process-brief" in html
    assert "/decision-work/prepare" in html
    assert "Prepare JSON" in html
    assert "run_offline_operator=True" not in html


def test_review_records_no_runtime_or_generation_boundary() -> None:
    review = json.loads(_read(REVIEW))

    assert review["implemented"]["compiled_spa_bundle_changed"] is False
    assert review["implemented"]["run_offline_operator"] is False
    assert review["boundary"]["creates_interpretation_read"] is False
    assert review["boundary"]["calls_provider_or_model"] is False
    assert review["boundary"]["runs_offline_operator_from_browser"] is False
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

    text = _read(DOC) + _read(REVIEW) + _read(REPO_ROOT / "observatory/serve_result.py")
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
