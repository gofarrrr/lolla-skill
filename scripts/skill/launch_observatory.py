#!/usr/bin/env python3
"""Launch the Lolla Observatory as a durable local background process."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen


URL_RE = re.compile(r"http://localhost:\d+")


@dataclass(frozen=True)
class LaunchResult:
    status: str
    url: str
    pid: int | None


def _http_ok(url: str) -> bool:
    try:
        request = Request(url, headers={"User-Agent": "lolla-observatory-launcher/1"})
        with urlopen(request, timeout=1.5) as response:
            return response.status < 500
    except Exception:
        return False


def _latest_url(log_path: Path) -> str:
    if not log_path.exists():
        return ""
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    matches = URL_RE.findall(text)
    return matches[-1] if matches else ""


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2)


def launch_observatory(
    *,
    result_path: Path,
    log_path: Path,
    pid_file: Path,
    port: int = 8080,
    timeout_seconds: float = 15.0,
) -> LaunchResult:
    repo_root = Path(__file__).resolve().parents[2]
    server_path = repo_root / "observatory" / "serve_result.py"
    if not result_path.exists():
        return LaunchResult(status="unavailable", url="", pid=None)
    if not server_path.exists():
        return LaunchResult(status="unavailable", url="", pid=None)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as log_handle:
        process = subprocess.Popen(
            [
                sys.executable,
                "-u",
                str(server_path),
                "--result",
                str(result_path),
                "--port",
                str(port),
            ],
            stdin=subprocess.DEVNULL,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            close_fds=True,
            start_new_session=True,
        )

    pid_file.write_text(f"{process.pid}\n", encoding="utf-8")

    deadline = time.monotonic() + timeout_seconds
    observed_url = ""
    while time.monotonic() < deadline:
        observed_url = _latest_url(log_path)
        if observed_url and _http_ok(observed_url):
            return LaunchResult(status="live", url=observed_url, pid=process.pid)
        if process.poll() is not None:
            break
        time.sleep(0.25)

    _stop_process(process)
    return LaunchResult(status="unavailable", url=observed_url, pid=process.pid)


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch a durable Lolla Observatory server")
    parser.add_argument("--result", required=True, help="Path to result JSON")
    parser.add_argument("--log", required=True, help="Path to Observatory log")
    parser.add_argument("--pid-file", required=True, help="Path to write Observatory PID")
    parser.add_argument("--port", type=int, default=8080, help="Starting port")
    parser.add_argument("--timeout", type=float, default=15.0, help="Liveness wait in seconds")
    args = parser.parse_args()

    result = launch_observatory(
        result_path=Path(args.result),
        log_path=Path(args.log),
        pid_file=Path(args.pid_file),
        port=args.port,
        timeout_seconds=args.timeout,
    )
    print(f"OBSERVATORY_STATUS={result.status}")
    print(f"OBSERVATORY_URL={result.url}")
    print(f"OBSERVATORY_PID={result.pid or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
