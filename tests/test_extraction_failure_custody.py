from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _conversation() -> str:
    return (
        "CONVERSATION: 2 turns, 1 user messages, 1 assistant responses\n\n"
        "[Turn 1] USER:\nShould I accept this offer?\n\n"
        "[Turn 1] ASSISTANT:\nAccept only if the downside is bounded.\n"
    )


def test_private_capture_helper_writes_valid_runtime_artifact_without_echoing_source(
    tmp_path: Path,
) -> None:
    run_id = "quiet_capture_test"
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_TMP_DIR": str(tmp_path),
        "PYTHONPATH": str(REPO_ROOT),
    }
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/skill/capture_conversation.py"),
        ],
        input=_conversation(),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "CAPTURE_STATUS: ready" in result.stdout
    assert "Should I accept this offer?" not in result.stdout
    assert "conversation.txt" not in result.stdout
    captured = tmp_path / f"lolla_{run_id}_conversation.txt"
    assert captured.read_text(encoding="utf-8") == _conversation()
    assert captured.stat().st_mode & 0o777 == 0o600
    events = json.loads(
        (tmp_path / f"lolla_{run_id}_run_events.json").read_text(encoding="utf-8")
    )
    assert [event["event_type"] for event in events["events"]] == [
        "conversation_captured"
    ]


def test_private_capture_helper_refuses_to_replace_different_source(
    tmp_path: Path,
) -> None:
    run_id = "quiet_capture_replace_guard"
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_TMP_DIR": str(tmp_path),
        "PYTHONPATH": str(REPO_ROOT),
    }
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts/skill/capture_conversation.py"),
    ]
    first = subprocess.run(
        command,
        input=_conversation(),
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    replacement = _conversation().replace("bounded", "unbounded")
    second = subprocess.run(
        command,
        input=replacement,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert first.returncode == 0
    assert second.returncode != 0
    assert "already contains different source text" in second.stderr
    captured = tmp_path / f"lolla_{run_id}_conversation.txt"
    assert captured.read_text(encoding="utf-8") == _conversation()


def test_failed_extraction_is_sealed_archived_and_receipted_once(
    tmp_path: Path,
) -> None:
    run_id = "failed_extraction_closeout"
    scratch = tmp_path / "scratch"
    archive = tmp_path / "archive"
    scratch.mkdir()
    conversation = scratch / f"lolla_{run_id}_conversation.txt"
    extraction = scratch / f"lolla_{run_id}_extraction.json"
    calls = scratch / f"lolla_{run_id}_extraction_calls.json"
    budget = scratch / f"lolla_{run_id}_provider_budget.json"
    transcript = scratch / f"lolla_{run_id}_live_transcript.txt"
    operator = scratch / f"lolla_{run_id}_operator.log"
    conversation.write_text(_conversation(), encoding="utf-8")
    extraction.write_text(
        json.dumps(
            {
                "status": "error",
                "error": (
                    "Extraction provider call did not complete: "
                    "provider_finish_error"
                ),
                "provider_failure": {
                    "status": "provider_finish_error",
                    "finish_reason": "error",
                    "provider_error_type": "provider_unavailable",
                },
                "provider_call_custody": {
                    "recorded_call_count": 2,
                    "terminal_status": "provider_finish_error",
                },
            }
        ),
        encoding="utf-8",
    )
    calls.write_text(
        json.dumps(
            [
                {"status": "url_error", "provider_attempted": True},
                {"status": "provider_finish_error", "provider_attempted": True},
            ]
        ),
        encoding="utf-8",
    )
    budget.write_text(
        json.dumps(
            {
                "attempted_provider_calls": 2,
                "accounted_cost_usd": 0.012,
                "provider_reported_cost_usd": 0.0,
            }
        ),
        encoding="utf-8",
    )
    transcript.write_text("", encoding="utf-8")
    operator.write_text("provider failed\n", encoding="utf-8")
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_TMP_DIR": str(scratch),
        "LOLLA_ARCHIVE_DIR": str(archive),
        "LOLLA_LIVE_TRANSCRIPT": str(transcript),
        "PYTHONPATH": str(REPO_ROOT),
    }
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts/skill/finalize_extraction_attempt.py"),
        "--command-exit",
        "1",
    ]
    first = subprocess.run(
        command,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    second = subprocess.run(
        command,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    terminal_path = scratch / f"lolla_{run_id}_extraction_terminal.json"
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    assert terminal["terminal_state"] == "failed"
    assert terminal["same_run_retry_allowed"] is False
    assert terminal["graph_pipeline_started"] is False
    assert terminal["provider_calls"]["recorded_call_count"] == 2
    assert terminal["provider_calls"]["budget_attempted_call_count"] == 2
    assert terminal["provider_calls"]["history_consistent"] is True
    run_archive = archive / "_failed-extractions" / run_id
    assert (run_archive / "failure_archive_manifest.json").exists()
    assert not (run_archive / "result.json").exists()
    assert not (run_archive / "memo.md").exists()
    receipt = (
        "Lolla stopped before the graph because the model provider interrupted "
        "the conversation read. No automatic retry was made. The source and "
        "failure evidence were preserved privately. Start a new `$lolla` run "
        "when you want to try again."
    )
    assert receipt in first.stdout
    assert transcript.read_text(encoding="utf-8").count(receipt) == 1
    events = json.loads(
        (scratch / f"lolla_{run_id}_run_events.json").read_text(encoding="utf-8")
    )
    assert [event["event_type"] for event in events["events"]] == [
        "extraction_failed"
    ]


def test_successful_extraction_is_sealed_without_failure_archive_or_receipt(
    tmp_path: Path,
) -> None:
    run_id = "successful_extraction_closeout"
    scratch = tmp_path / "scratch"
    archive = tmp_path / "archive"
    scratch.mkdir()
    (scratch / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps({"status": "ok"}),
        encoding="utf-8",
    )
    (scratch / f"lolla_{run_id}_extraction_calls.json").write_text(
        json.dumps([{"status": "ok", "provider_attempted": True}]),
        encoding="utf-8",
    )
    (scratch / f"lolla_{run_id}_provider_budget.json").write_text(
        json.dumps({"attempted_provider_calls": 1}),
        encoding="utf-8",
    )
    transcript = scratch / f"lolla_{run_id}_live_transcript.txt"
    transcript.write_text("", encoding="utf-8")
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_TMP_DIR": str(scratch),
        "LOLLA_ARCHIVE_DIR": str(archive),
        "LOLLA_LIVE_TRANSCRIPT": str(transcript),
        "PYTHONPATH": str(REPO_ROOT),
    }
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/skill/finalize_extraction_attempt.py"),
            "--command-exit",
            "0",
        ],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    terminal = json.loads(
        (
            scratch / f"lolla_{run_id}_extraction_terminal.json"
        ).read_text(encoding="utf-8")
    )
    assert terminal["terminal_state"] == "completed"
    assert terminal["same_run_retry_allowed"] is False
    assert terminal["failure_archive"]["status"] == "not_applicable"
    assert "USER_FAILURE_RECEIPT" not in result.stdout
    assert transcript.read_text(encoding="utf-8") == ""
    assert not (archive / "_failed-extractions" / run_id).exists()
    events = json.loads(
        (scratch / f"lolla_{run_id}_run_events.json").read_text(encoding="utf-8")
    )
    assert [event["event_type"] for event in events["events"]] == [
        "extraction_completed"
    ]


def test_run_extract_rejects_a_sealed_same_run_before_loading_provider(
    tmp_path: Path,
) -> None:
    run_id = "sealed_extract_guard"
    conversation = tmp_path / f"lolla_{run_id}_conversation.txt"
    output = tmp_path / f"lolla_{run_id}_extraction.json"
    terminal = tmp_path / f"lolla_{run_id}_extraction_terminal.json"
    conversation.write_text(_conversation(), encoding="utf-8")
    terminal.write_text(
        json.dumps(
            {
                "schema_version": "lolla.extraction_terminal.v1",
                "run_id": run_id,
                "same_run_retry_allowed": False,
            }
        ),
        encoding="utf-8",
    )
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_TMP_DIR": str(tmp_path),
        "OPENROUTER_API_KEY": "must-not-be-used",
        "PYTHONPATH": str(REPO_ROOT),
    }
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/run_extract.py"),
            "--conversation-file",
            str(conversation),
            "--output-file",
            str(output),
        ],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )

    assert result.returncode != 0
    assert "already terminal" in result.stdout
    assert not output.exists()
