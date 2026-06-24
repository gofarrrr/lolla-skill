from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.skill import launch_observatory


class FakeProcess:
    def __init__(self, pid: int = 1234) -> None:
        self.pid = pid
        self.terminated = False
        self.killed = False

    def poll(self) -> int | None:
        return None if not self.terminated and not self.killed else 0

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float | None = None) -> int:
        return 0


def test_launch_observatory_starts_server_in_new_session(
    tmp_path: Path, monkeypatch
) -> None:
    result_path = tmp_path / "result.json"
    log_path = tmp_path / "observatory.log"
    pid_file = tmp_path / "observatory.pid"
    result_path.write_text("{}", encoding="utf-8")
    fake_process = FakeProcess(pid=4321)

    def fake_popen(cmd, **kwargs):
        assert "-u" in cmd
        assert "--result" in cmd
        assert str(result_path) in cmd
        assert kwargs["stdin"] is subprocess.DEVNULL
        assert kwargs["stderr"] is subprocess.STDOUT
        assert kwargs["close_fds"] is True
        assert kwargs["start_new_session"] is True
        kwargs["stdout"].write(b"Lolla Observatory at http://localhost:19001\n")
        kwargs["stdout"].flush()
        return fake_process

    monkeypatch.setattr(launch_observatory.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(launch_observatory, "_http_ok", lambda url: True)

    result = launch_observatory.launch_observatory(
        result_path=result_path,
        log_path=log_path,
        pid_file=pid_file,
        port=19001,
        timeout_seconds=0.5,
    )

    assert result.status == "live"
    assert result.url == "http://localhost:19001"
    assert result.pid == 4321
    assert pid_file.read_text(encoding="utf-8") == "4321\n"
    assert fake_process.terminated is False


def test_launch_observatory_stops_unreachable_process(tmp_path: Path, monkeypatch) -> None:
    result_path = tmp_path / "result.json"
    log_path = tmp_path / "observatory.log"
    pid_file = tmp_path / "observatory.pid"
    result_path.write_text("{}", encoding="utf-8")
    fake_process = FakeProcess(pid=9876)

    def fake_popen(cmd, **kwargs):
        kwargs["stdout"].write(b"Lolla Observatory at http://localhost:19002\n")
        kwargs["stdout"].flush()
        return fake_process

    monkeypatch.setattr(launch_observatory.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(launch_observatory, "_http_ok", lambda url: False)
    monkeypatch.setattr(launch_observatory.time, "sleep", lambda seconds: None)

    result = launch_observatory.launch_observatory(
        result_path=result_path,
        log_path=log_path,
        pid_file=pid_file,
        port=19002,
        timeout_seconds=0.01,
    )

    assert result.status == "unavailable"
    assert result.url == "http://localhost:19002"
    assert result.pid == 9876
    assert fake_process.terminated is True
