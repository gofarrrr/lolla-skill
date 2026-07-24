from __future__ import annotations

import json
import os
import pty
import select
import subprocess
import sys
import termios
import time
from pathlib import Path

import pytest


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
    assert "PRIVATE_INPUT_READY" in result.stdout
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


def test_private_capture_disables_terminal_echo_while_reading(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "skill"))
    from engine.system_b import private_runtime

    original = [0, 0, 0, termios.ECHO | 0x20, 0, 0, []]
    transitions: list[tuple[int, int, list]] = []

    class _FakeTTY:
        def fileno(self) -> int:
            return 91

        def isatty(self) -> bool:
            return True

        def read(self) -> str:
            assert transitions
            assert transitions[-1][2][3] & termios.ECHO == 0
            return _conversation()

    monkeypatch.setattr(private_runtime.sys, "stdin", _FakeTTY())
    monkeypatch.setattr(
        private_runtime.termios,
        "tcgetattr",
        lambda _fd: list(original),
    )
    monkeypatch.setattr(
        private_runtime.termios,
        "tcsetattr",
        lambda fd, when, attrs: transitions.append((fd, when, list(attrs))),
    )

    assert private_runtime.read_private_stdin() == _conversation()
    assert transitions[0][0] == 91
    assert transitions[0][2][3] & termios.ECHO == 0
    assert transitions[-1] == (91, termios.TCSANOW, original)


def test_private_capture_true_pty_waits_for_ready_before_source_is_sent(
    tmp_path: Path,
) -> None:
    """The host gets a deterministic signal only after terminal echo is off."""

    run_id = "quiet_capture_true_pty"
    marker = "PRIVATE_SOURCE_MUST_NOT_ECHO_4f9b"
    source = _conversation().replace("Should I accept this offer?", marker)
    env = {
        **os.environ,
        "LOLLA_RUN_ID": run_id,
        "LOLLA_EXPECTED_RUN_ID": run_id,
        "LOLLA_TMP_DIR": str(tmp_path),
        "PYTHONPATH": str(REPO_ROOT),
        "PYTHONUNBUFFERED": "1",
    }
    master_fd, slave_fd = pty.openpty()
    process = subprocess.Popen(
        [
            sys.executable,
            str(REPO_ROOT / "scripts/skill/capture_conversation.py"),
        ],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        env=env,
        close_fds=True,
    )
    os.close(slave_fd)
    output = bytearray()
    deadline = time.monotonic() + 5
    try:
        while b"PRIVATE_INPUT_READY" not in output:
            remaining = deadline - time.monotonic()
            assert remaining > 0, output.decode("utf-8", errors="replace")
            readable, _, _ = select.select([master_fd], [], [], remaining)
            assert readable, output.decode("utf-8", errors="replace")
            output.extend(os.read(master_fd, 4096))

        os.write(master_fd, source.encode("utf-8"))
        os.write(master_fd, b"\x04")

        while process.poll() is None:
            readable, _, _ = select.select([master_fd], [], [], 0.1)
            if readable:
                try:
                    output.extend(os.read(master_fd, 4096))
                except OSError:
                    break
        process.wait(timeout=5)
        while True:
            readable, _, _ = select.select([master_fd], [], [], 0)
            if not readable:
                break
            try:
                chunk = os.read(master_fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            output.extend(chunk)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        os.close(master_fd)

    rendered = output.decode("utf-8", errors="replace")
    assert process.returncode == 0, rendered
    assert "PRIVATE_INPUT_READY" in rendered
    assert "CAPTURE_STATUS: ready" in rendered
    assert marker not in rendered
    captured = tmp_path / f"lolla_{run_id}_conversation.txt"
    assert captured.read_text(encoding="utf-8") == source


def test_private_capture_fails_closed_when_tty_echo_cannot_be_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "skill"))
    from engine.system_b import private_runtime

    class _UnreadableTTY:
        def fileno(self) -> int:
            return 91

        def isatty(self) -> bool:
            return True

        def read(self) -> str:
            raise AssertionError("source must not be read while terminal echo may be on")

    monkeypatch.setattr(private_runtime.sys, "stdin", _UnreadableTTY())
    monkeypatch.setattr(
        private_runtime.termios,
        "tcgetattr",
        lambda _fd: (_ for _ in ()).throw(termios.error("not a tty")),
    )

    with pytest.raises(private_runtime.PrivateInputError):
        private_runtime.read_private_stdin()


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
    assert archive.stat().st_mode & 0o777 == 0o700
    assert (archive / "_failed-extractions").stat().st_mode & 0o777 == 0o700
    assert run_archive.stat().st_mode & 0o777 == 0o700
    assert all(
        path.stat().st_mode & 0o777 == 0o600
        for path in run_archive.iterdir()
        if path.is_file()
    )
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
