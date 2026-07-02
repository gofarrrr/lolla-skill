from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from engine.system_b.decision_work_brief_runtime_attachment import (
    DECISION_WORK_RUNTIME_ATTACHMENT_FLAG,
    decision_work_runtime_attachment_enabled,
    run_post_archive_decision_work_brief_attachment,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RUN_PATH = REPO_ROOT / "scripts" / "archive_run.py"
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-brief-flagged-post-archive-runtime-hook-v0.md"
)
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


def _load_archive_run_module():
    spec = importlib.util.spec_from_file_location("archive_run", ARCHIVE_RUN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_completed_archive_run(run_dir: Path, *, include_revised: bool = True) -> None:
    run_dir.mkdir(parents=True)
    for name in (
        "agent_result.json",
        "evaluation.json",
        "reasoning_trace.json",
        "extraction.json",
        "result.json",
    ):
        (run_dir / name).write_text(
            json.dumps({"artifact": name, "status": "present"}),
            encoding="utf-8",
        )
    if include_revised:
        (run_dir / "revised.txt").write_text(
            "Safe revised-answer placeholder for fixture use only.",
            encoding="utf-8",
        )


def _seed_tmp_run(tmp_dir: Path, run_id: str, *, include_revised: bool = True) -> None:
    (tmp_dir / f"lolla_{run_id}_conversation.txt").write_text(
        "Synthetic conversation placeholder for archive fixture.",
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps(
            {
                "extraction": {
                    "decision_situation": "Whether to attach a runtime brief safely."
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_result.json").write_text(
        json.dumps(
            {
                "schema_version": "fixture.result.v0",
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {"status": "disabled"},
            }
        ),
        encoding="utf-8",
    )
    if include_revised:
        (tmp_dir / f"lolla_{run_id}_revised.txt").write_text(
            "Safe revised-answer placeholder for fixture use only.",
            encoding="utf-8",
        )


def test_flag_is_default_off() -> None:
    assert decision_work_runtime_attachment_enabled({}) is False
    assert decision_work_runtime_attachment_enabled(
        {DECISION_WORK_RUNTIME_ATTACHMENT_FLAG: "0"}
    ) is False
    assert decision_work_runtime_attachment_enabled(
        {DECISION_WORK_RUNTIME_ATTACHMENT_FLAG: "1"}
    ) is True


def test_hook_default_off_writes_no_sidecar(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)

    result = run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={},
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["enabled"] is False
    assert result["attachment_state"] == "not_requested"
    assert result["sidecar_written"] is False
    assert not (run_dir / "decision_work").exists()


def test_hook_flag_on_writes_deferred_sidecar_without_safe_brief(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)

    result = run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={DECISION_WORK_RUNTIME_ATTACHMENT_FLAG: "1"},
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["enabled"] is True
    assert result["sidecar_written"] is True
    assert result["attachment_state"] == "deferred"
    status = json.loads(
        (run_dir / "decision_work/attachment_status.json").read_text(encoding="utf-8")
    )
    assert status["attachment_metadata"]["sidecar_written_inside_archive"] is True
    assert status["custody_flags"]["model_calls"] == 0
    assert status["custody_flags"]["agent_action_authorized"] is False
    assert (run_dir / "decision_work/user_receipt.md").exists()
    assert (run_dir / "decision_work/agent_handoff_packet.json").exists()


def test_hook_flag_on_blocks_incomplete_archive_without_failing(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir, include_revised=False)

    result = run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={DECISION_WORK_RUNTIME_ATTACHMENT_FLAG: "on"},
        created_at="2026-07-02T00:00:00Z",
    )

    assert result["enabled"] is True
    assert result["sidecar_written"] is True
    assert result["attachment_state"] == "blocked"
    status = json.loads(
        (run_dir / "decision_work/attachment_status.json").read_text(encoding="utf-8")
    )
    assert "missing_required_text_artifact:revised.txt" in status["blocked_reasons"]
    receipt = (run_dir / "decision_work/user_receipt.md").read_text(encoding="utf-8")
    assert "Decision Work Brief: blocked" in receipt


def test_archive_run_calls_hook_only_when_flagged(tmp_path: Path, monkeypatch) -> None:
    archive_run = _load_archive_run_module()
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()
    _seed_tmp_run(tmp_dir, "runone_aaaaaa")

    monkeypatch.delenv(DECISION_WORK_RUNTIME_ATTACHMENT_FLAG, raising=False)
    first = archive_run.archive_run(
        "runone_aaaaaa",
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )
    first_run_dir = Path(first["run_dir"])
    assert first["decision_work_attachment"]["enabled"] is False
    assert not (first_run_dir / "decision_work").exists()

    _seed_tmp_run(tmp_dir, "runtwo_bbbbbb")
    monkeypatch.setenv(DECISION_WORK_RUNTIME_ATTACHMENT_FLAG, "1")
    second = archive_run.archive_run(
        "runtwo_bbbbbb",
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )
    second_run_dir = Path(second["run_dir"])
    assert second["decision_work_attachment"]["enabled"] is True
    assert (second_run_dir / "decision_work/attachment_status.json").exists()
    assert (second_run_dir / "decision_work/user_receipt.md").exists()


def test_hook_outputs_do_not_export_raw_private_or_authority_claims(tmp_path: Path) -> None:
    run_dir = tmp_path / "archive/case/run"
    _write_completed_archive_run(run_dir)

    run_post_archive_decision_work_brief_attachment(
        run_dir=run_dir,
        environ={DECISION_WORK_RUNTIME_ATTACHMENT_FLAG: "1"},
        created_at="2026-07-02T00:00:00Z",
    )
    rendered = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((run_dir / "decision_work").iterdir())
        if path.is_file()
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in rendered
    assert '"model_calls": 0' in rendered
    assert '"agent_action_authorized": false' in rendered
    assert '"product_proof": false' in rendered
    assert "not proof that the advice is correct" in rendered


def test_runtime_hook_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
