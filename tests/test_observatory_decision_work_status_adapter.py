from __future__ import annotations

import json
import socket
import sys
import threading
import urllib.request
from contextlib import closing
from http.server import HTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "observatory"))

import serve_result  # noqa: E402
from engine.system_b.observatory_decision_work_status import (  # noqa: E402
    OBSERVATORY_DECISION_WORK_STATUS_SCHEMA_VERSION,
    build_observatory_decision_work_status,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _base_result(run_id: str = "run-1") -> dict:
    return {
        "usage_summary": {"run_id": run_id},
        "extraction": {"decision_situation": "A launch decision is being reviewed."},
    }


def _write_run(run_dir: Path, *, run_id: str = "run-1") -> Path:
    result_path = run_dir / "result.json"
    _write_json(result_path, _base_result(run_id))
    _write_json(run_dir / "extraction.json", {"decision_situation": "available"})
    return result_path


def _status_payload(
    attachment_state: str,
    *,
    blocked_reasons: list[str] | None = None,
    deferred_reasons: list[str] | None = None,
    missing_artifacts: dict[str, str] | None = None,
) -> dict:
    return {
        "schema_version": "lolla.decision_work_brief_runtime_attachment_status.v0",
        "attachment_state": attachment_state,
        "generated_artifacts": {"attachment_status": "decision_work/attachment_status.json"},
        "missing_artifacts": missing_artifacts or {},
        "blocked_reasons": blocked_reasons or [],
        "deferred_reasons": deferred_reasons or [],
        "custody_flags": {
            "model_calls": 0,
            "runtime_behavior_changed": False,
            "archive_mutated": False,
            "agent_action_authorized": False,
            "automatic_action_authorized": False,
        },
        "non_claims": ["not_product_proof", "not_human_validation"],
    }


def _write_sidecar(
    run_dir: Path,
    attachment_state: str,
    *,
    receipt: str | None = None,
    blocked_reasons: list[str] | None = None,
    deferred_reasons: list[str] | None = None,
    missing_artifacts: dict[str, str] | None = None,
) -> None:
    sidecar = run_dir / "decision_work"
    _write_json(
        sidecar / "attachment_status.json",
        _status_payload(
            attachment_state,
            blocked_reasons=blocked_reasons,
            deferred_reasons=deferred_reasons,
            missing_artifacts=missing_artifacts,
        ),
    )
    if receipt is not None:
        (sidecar / "user_receipt.md").write_text(receipt, encoding="utf-8")


def _payload_text(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True)


def test_absent_sidecar_reports_not_present_without_generation(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run-1"
    result_path = _write_run(run_dir)

    payload = build_observatory_decision_work_status(
        selected_case_id="archive:case:run-1",
        result=_base_result(),
        result_path=result_path,
    )

    assert payload["schema_version"] == OBSERVATORY_DECISION_WORK_STATUS_SCHEMA_VERSION
    assert payload["decision_work_status"] == "decision_work_not_present"
    assert payload["attachment_state"] == "not_present"
    assert payload["available"] is False
    assert payload["live_extraction_status"] == "available"
    assert payload["receipt"]["available"] is False
    assert payload["custody_flags"]["read_only"] is True
    assert payload["custody_flags"]["sidecar_written"] is False
    assert "decision_work_sidecar" in payload["missingness"]


def test_deferred_sidecar_reports_missing_inputs(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run-1"
    result_path = _write_run(run_dir)
    _write_sidecar(
        run_dir,
        "deferred",
        receipt="Decision Work Brief: deferred\n\nReason: safe input missing.\n",
        deferred_reasons=["safe_rendered_brief_not_supplied"],
        missing_artifacts={"decision_work_brief_markdown": "not_supplied"},
    )

    payload = build_observatory_decision_work_status(
        selected_case_id="archive:case:run-1",
        result=_base_result(),
        result_path=result_path,
    )

    assert payload["decision_work_status"] == "decision_work_deferred"
    assert payload["attachment_state"] == "deferred"
    assert payload["deferred_reasons"] == ["safe_rendered_brief_not_supplied"]
    assert "decision_work_brief_markdown" in payload["missingness"]
    assert payload["receipt"]["available"] is True
    assert payload["receipt"]["ref"] == "decision_work/user_receipt.md"


def test_blocked_sidecar_reports_blockers(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run-1"
    result_path = _write_run(run_dir)
    _write_sidecar(
        run_dir,
        "blocked",
        receipt="Decision Work Brief: blocked\n\nReason: missing revised answer.\n",
        blocked_reasons=["missing_required_text_artifact:revised.txt"],
    )

    payload = build_observatory_decision_work_status(
        selected_case_id="archive:case:run-1",
        result=_base_result(),
        result_path=result_path,
    )

    assert payload["decision_work_status"] == "decision_work_blocked"
    assert payload["attachment_state"] == "blocked"
    assert payload["blockers"] == ["missing_required_text_artifact:revised.txt"]
    assert payload["available"] is False


def test_available_sidecar_returns_safe_receipt_and_artifact_refs(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run-1"
    result_path = _write_run(run_dir)
    _write_sidecar(
        run_dir,
        "generated",
        receipt=(
            "Decision Work Brief: available\n\n"
            "What changed: the launch path became narrower.\n\n"
            "Main caveat: not proof that the advice is correct.\n"
        ),
    )

    payload = build_observatory_decision_work_status(
        selected_case_id="archive:case:run-1",
        result=_base_result(),
        result_path=result_path,
    )

    assert payload["decision_work_status"] == "decision_work_available"
    assert payload["available"] is True
    assert payload["receipt"]["available"] is True
    assert "launch path became narrower" in payload["receipt"]["markdown"]
    refs = {artifact["ref"] for artifact in payload["source_artifacts"]}
    assert "decision_work/attachment_status.json" in refs
    assert "decision_work/user_receipt.md" in refs


def test_malformed_status_is_reported_without_throwing(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run-1"
    result_path = _write_run(run_dir)
    sidecar = run_dir / "decision_work"
    sidecar.mkdir()
    (sidecar / "attachment_status.json").write_text("{not-json", encoding="utf-8")

    payload = build_observatory_decision_work_status(
        selected_case_id="archive:case:run-1",
        result=_base_result(),
        result_path=result_path,
    )

    assert payload["decision_work_status"] == "decision_work_malformed"
    assert payload["attachment_state"] == "malformed"
    assert "attachment_status_malformed_json" in payload["blockers"]
    assert "valid_attachment_status" in payload["missingness"]


def test_unsafe_receipt_is_not_returned(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run-1"
    result_path = _write_run(run_dir)
    _write_sidecar(
        run_dir,
        "generated",
        receipt="Decision Work Brief: available\n/" + "Users/private/path\n",
    )

    payload = build_observatory_decision_work_status(
        selected_case_id="archive:case:run-1",
        result=_base_result(),
        result_path=result_path,
    )

    assert payload["decision_work_status"] == "decision_work_available"
    assert payload["receipt"]["available"] is False
    assert payload["receipt"]["status"] == "blocked_unsafe_content"
    assert payload["receipt"]["markdown"] is None
    assert "user_receipt_contains_private_or_local_marker" in payload["blockers"]


def test_payload_does_not_leak_local_paths_or_authority_claims(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run-1"
    result_path = _write_run(run_dir)
    _write_sidecar(
        run_dir,
        "generated",
        receipt="Decision Work Brief: available\n\nMain caveat: not proof.\n",
    )

    payload = build_observatory_decision_work_status(
        selected_case_id="archive:case:run-1",
        result=_base_result(),
        result_path=result_path,
    )
    rendered = _payload_text(payload)

    assert "/" + "Users/" not in rendered
    assert str(tmp_path) not in rendered
    for key in [
        "product_proof",
        "human_validated",
        "answer_correctness",
        "advice_correctness",
        "agent_action_authorized",
        "automatic_action_authorized",
        "archive_mutated",
        "sidecar_written",
    ]:
        assert f'"{key}": true' not in rendered


def test_observatory_response_finds_archived_sidecar_from_current_run_events(
    tmp_path: Path,
    monkeypatch,
) -> None:
    archive_root = tmp_path / "archive"
    archive_run_dir = archive_root / "case-a" / "run-1"
    archive_run_dir.mkdir(parents=True)
    current_dir = tmp_path / "tmp"
    current_dir.mkdir()
    current_result = current_dir / "lolla_run-1_result.json"
    _write_json(current_result, _base_result("run-1"))
    _write_json(current_dir / "lolla_run-1_extraction.json", {"ok": True})
    _write_json(
        current_dir / "lolla_run-1_run_events.json",
        {"events": [{"details": {"archive_path": str(archive_run_dir)}}]},
    )
    _write_sidecar(
        archive_run_dir,
        "generated",
        receipt="Decision Work Brief: available\n\nMain caveat: not proof.\n",
    )
    monkeypatch.setenv("LOLLA_ARCHIVE_DIR", str(archive_root))

    payload = serve_result._build_decision_work_status_response(
        "lolla-audit",
        _base_result("run-1"),
        current_result,
        is_current=True,
    )

    assert payload["decision_work_status"] == "decision_work_available"
    assert payload["receipt"]["available"] is True
    assert payload["live_extraction_status"] == "available"


def test_serve_result_declares_decision_work_api_route() -> None:
    source = (REPO_ROOT / "observatory/serve_result.py").read_text(encoding="utf-8")

    assert 'parts[4] == "decision-work"' in source
    assert "_build_decision_work_status_response" in source


def test_decision_work_api_route_smoke(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    result_path = _write_run(run_dir)
    old_result = serve_result._RESULT
    old_result_path = serve_result._RESULT_PATH
    old_case_id = serve_result._CASE_ID
    old_mtime = serve_result._RESULT_MTIME

    serve_result._RESULT = _base_result()
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
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/api/case/lolla-audit/decision-work",
            timeout=3,
        ) as response:
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
        serve_result._RESULT = old_result
        serve_result._RESULT_PATH = old_result_path
        serve_result._CASE_ID = old_case_id
        serve_result._RESULT_MTIME = old_mtime

    assert payload["schema_version"] == OBSERVATORY_DECISION_WORK_STATUS_SCHEMA_VERSION
    assert payload["decision_work_status"] == "decision_work_not_present"
    assert payload["links"]["extraction_audit"] == "/audit/extraction"
