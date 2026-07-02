from __future__ import annotations

import json
from pathlib import Path

import engine.system_b.decision_work_brief_runtime_attachment as runtime_attachment


FLAG = runtime_attachment.DECISION_WORK_RUNTIME_ATTACHMENT_FLAG
MODE_ENV = runtime_attachment.DECISION_WORK_RESOLVER_MODE_ENV
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _write_completed_archive_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    for name in (
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "extraction.json",
        "result.json",
    ):
        (run_dir / name).write_text(
            json.dumps({"schema_version": "fixture.v0", "artifact": name}),
            encoding="utf-8",
        )
    (run_dir / "revised.txt").write_text(
        "Safe revised-answer placeholder for fixture use only.",
        encoding="utf-8",
    )


def _write_markdown(path: Path, text: str = "Safe Decision Work Brief fixture.") -> Path:
    path.write_text(text + "\n", encoding="utf-8")
    return path


def _write_json(path: Path, schema_version: str) -> Path:
    path.write_text(
        json.dumps({"schema_version": schema_version, "fixture": True}),
        encoding="utf-8",
    )
    return path


def _read_status(run_dir: Path) -> dict:
    return json.loads(
        (run_dir / "decision_work/attachment_status.json").read_text(encoding="utf-8")
    )


def _sidecar_text(run_dir: Path) -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((run_dir / "decision_work").iterdir())
        if path.is_file()
    )


def test_default_off_does_not_call_resolver_or_bundle(tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)

    def fail_if_called(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("resolver or bundle should not run when flag is off")

    monkeypatch.setattr(
        runtime_attachment,
        "resolve_decision_work_brief_safe_supply",
        fail_if_called,
    )
    monkeypatch.setattr(
        runtime_attachment,
        "build_decision_work_brief_runtime_bundle",
        fail_if_called,
    )

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={},
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["enabled"] is False
    assert result["attachment_state"] == "not_requested"
    assert result["sidecar_written"] is False
    assert not (run_dir / "decision_work").exists()


def test_flag_on_without_safe_refs_writes_resolver_deferred_sidecar(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={FLAG: "1"},
        created_at="2026-07-02T00:00:00Z",
    )
    status = _read_status(run_dir)
    receipt = (run_dir / "decision_work/user_receipt.md").read_text(encoding="utf-8")

    assert result["attachment_state"] == "deferred"
    assert status["attachment_state"] == "deferred"
    assert status["resolver_summary"]["resolver_mode"] == "archive_local_safe_resolver"
    assert status["resolver_summary"]["resolver_status"] == "no_safe_inputs"
    assert status["generated_artifacts"]["safe_supply_resolver"] == (
        "decision_work/safe_supply_resolver.json"
    )
    assert "Decision Work Brief: deferred" in receipt
    assert "decision_work_brief_markdown" not in status["generated_artifacts"]


def test_flag_on_with_safe_refs_writes_available_sidecar(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")
    enriched = _write_markdown(tmp_path / "enriched.md")
    triage_read = _write_json(
        tmp_path / "triage-read.json",
        "lolla.decision_work_automatic_triage_provisional_read.v0",
    )

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={
            FLAG: "true",
            "LOLLA_DECISION_WORK_BRIEF_REF": str(brief),
            "LOLLA_DECISION_WORK_BRIEF_ENRICHED_REF": str(enriched),
            "LOLLA_DECISION_WORK_BRIEF_TRIAGE_READ_REF": str(triage_read),
        },
        created_at="2026-07-02T00:00:00Z",
    )
    status = _read_status(run_dir)
    receipt = (run_dir / "decision_work/user_receipt.md").read_text(encoding="utf-8")

    assert result["attachment_state"] == "generated"
    assert status["attachment_state"] == "generated"
    assert status["resolver_summary"]["resolver_mode"] == "manual_ref_supply_only"
    assert status["resolver_summary"]["resolver_status"] == "resolved"
    assert status["generated_artifacts"]["decision_work_brief_markdown"] == (
        "decision_work/decision_work_brief.md"
    )
    assert status["generated_artifacts"]["decision_work_brief_enriched_markdown"] == (
        "decision_work/decision_work_brief_enriched.md"
    )
    assert status["generated_artifacts"]["automatic_triage_read"] == (
        "decision_work/automatic_triage_read.json"
    )
    assert (run_dir / "decision_work/agent_handoff_packet.json").exists()
    assert "Decision Work Brief: available" in receipt


def test_flag_on_with_partial_safe_refs_writes_agent_only_sidecar(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")

    runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={
            FLAG: "on",
            "LOLLA_DECISION_WORK_BRIEF_REF": str(brief),
        },
        created_at="2026-07-02T00:00:00Z",
    )
    status = _read_status(run_dir)
    receipt = (run_dir / "decision_work/user_receipt.md").read_text(encoding="utf-8")

    assert status["attachment_state"] == "generated_agent_only"
    assert status["resolver_summary"]["resolver_status"] == "partially_resolved"
    assert "runtime_specific_triage_read_not_supplied" in status["deferred_reasons"]
    assert "Decision Work Brief: available for agent inspection" in receipt


def test_direct_runtime_interpretation_mode_blocks(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={
            FLAG: "yes",
            MODE_ENV: "future_direct_runtime_interpretation_not_allowed",
        },
        created_at="2026-07-02T00:00:00Z",
    )
    status = _read_status(run_dir)
    receipt = (run_dir / "decision_work/user_receipt.md").read_text(encoding="utf-8")

    assert result["attachment_state"] == "blocked"
    assert status["attachment_state"] == "blocked"
    assert status["resolver_summary"]["resolver_status"] == (
        "blocked_direct_runtime_interpretation"
    )
    assert "resolver:blocked_direct_runtime_interpretation" in status["blocked_reasons"]
    assert "Decision Work Brief: blocked" in receipt


def test_unsafe_safe_ref_blocks_without_exporting_private_marker(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)
    unsafe = tmp_path / "unsafe.md"
    unsafe.write_text("unsafe " + "raw_message" + "_content\n", encoding="utf-8")

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={
            FLAG: "1",
            "LOLLA_DECISION_WORK_BRIEF_REF": str(unsafe),
        },
        created_at="2026-07-02T00:00:00Z",
    )
    status = _read_status(run_dir)
    rendered = _sidecar_text(run_dir)

    assert result["attachment_state"] == "blocked"
    assert status["resolver_summary"]["resolver_status"] == "blocked_privacy_risk"
    assert "resolver:blocked_privacy_risk" in status["blocked_reasons"]
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered


def test_bundle_exception_fails_closed_without_blocking_archive(
    tmp_path: Path,
    monkeypatch,
) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)

    def raise_bundle_error(*args, **kwargs):  # noqa: ANN002, ANN003
        raise RuntimeError("bundle failed")

    monkeypatch.setattr(
        runtime_attachment,
        "build_decision_work_brief_runtime_bundle",
        raise_bundle_error,
    )

    result = runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={FLAG: "1"},
        created_at="2026-07-02T00:00:00Z",
    )
    status = _read_status(run_dir)

    assert result["attachment_state"] == "failed_closed"
    assert result["sidecar_written"] is True
    assert result["non_blocking"] is True
    assert status["attachment_state"] == "failed_closed"
    assert status["failed_closed_reasons"] == ["runtime_attachment_hook_failed"]


def test_resolver_hook_sidecar_has_conservative_custody_and_no_local_paths(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)
    brief = _write_markdown(tmp_path / "brief.md")

    runtime_attachment.run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={
            FLAG: "1",
            "LOLLA_DECISION_WORK_BRIEF_REF": str(brief),
        },
        created_at="2026-07-02T00:00:00Z",
    )
    rendered = _sidecar_text(run_dir)
    status = _read_status(run_dir)
    custody = status["custody_flags"]

    assert custody["model_calls"] == 0
    assert custody["skill_invoked"] is False
    assert custody["product_proof"] is False
    assert custody["human_validated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False
    assert str(tmp_path) not in rendered
    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
