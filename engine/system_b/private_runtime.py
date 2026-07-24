"""Owner-only runtime transport for source and agent-authored private payloads."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import termios
from pathlib import Path
from typing import Any


PRIVATE_INPUT_READY = "PRIVATE_INPUT_READY"


class PrivateInputError(RuntimeError):
    """A private input channel could not be established safely."""


def read_private_stdin() -> str:
    """Read stdin only after interactive echo is disabled.

    For a pipe, the payload is already outside the terminal input echo path.
    The same readiness marker is still emitted so hosts have one protocol.
    """

    if not sys.stdin.isatty():
        print(PRIVATE_INPUT_READY, flush=True)
        return sys.stdin.read()

    fd = sys.stdin.fileno()
    try:
        original = termios.tcgetattr(fd)
        quiet = list(original)
        quiet[3] &= ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, quiet)
    except (OSError, termios.error) as exc:
        raise PrivateInputError(
            "could not disable terminal echo; private input was not read"
        ) from exc

    try:
        print(PRIVATE_INPUT_READY, flush=True)
        return sys.stdin.read()
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSANOW, original)
        except (OSError, termios.error):
            pass


def atomic_private_write_text(path: Path, text: str) -> None:
    """Atomically replace ``path`` with owner-only UTF-8 text."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            os.chmod(handle.name, 0o600)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
        path.chmod(0o600)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink(missing_ok=True)


def atomic_private_write_json(path: Path, payload: Any) -> None:
    atomic_private_write_text(
        path,
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
