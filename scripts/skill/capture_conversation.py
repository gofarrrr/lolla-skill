#!/usr/bin/env python3
"""Privately capture the authoritative Lolla conversation from standard input."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import termios
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
ENGINE_ROOT = REPO_ROOT / "engine"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from engine.system_b.run_events import append_run_event  # noqa: E402
from engine.system_b.run_state import (  # noqa: E402
    assert_expected_run_state,
    is_valid_run_id,
)
from validate_conversation_capture import validate_capture  # noqa: E402


class PrivateInputError(RuntimeError):
    """The helper could not establish a non-echoing interactive input channel."""


PRIVATE_INPUT_READY = "PRIVATE_INPUT_READY"


def _runtime_tmp_dir() -> Path:
    return Path(os.getenv("LOLLA_TMP_DIR", "/tmp")).expanduser()


def _atomic_private_write(path: Path, text: str) -> None:
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


def _read_private_stdin() -> str:
    """Read a supplied transcript without letting an interactive TTY echo it."""

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
            "could not disable terminal echo; source was not read"
        ) from exc

    try:
        print(PRIVATE_INPUT_READY, flush=True)
        return sys.stdin.read()
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSANOW, original)
        except (OSError, termios.error):
            pass


def _event_already_recorded(path: Path) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return False
    events = payload.get("events") if isinstance(payload, dict) else []
    return any(
        isinstance(event, dict)
        and event.get("event_type") == "conversation_captured"
        for event in (events if isinstance(events, list) else [])
    )


def main() -> int:
    run_id = str(os.getenv("LOLLA_RUN_ID", "")).strip()
    if not is_valid_run_id(run_id):
        print("FATAL: LOLLA_RUN_ID is missing or invalid.", file=sys.stderr)
        return 2

    tmp_dir = _runtime_tmp_dir()
    conversation_path = tmp_dir / f"lolla_{run_id}_conversation.txt"
    events_path = tmp_dir / f"lolla_{run_id}_run_events.json"
    try:
        assert_expected_run_state(
            actual_run_id=run_id,
            artifact_paths=[conversation_path, events_path],
            phase="capture_conversation",
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        source = _read_private_stdin()
    except PrivateInputError as exc:
        print(f"FATAL: private conversation capture unavailable: {exc}.", file=sys.stderr)
        return 2
    if not source.strip():
        print(
            "FATAL: no conversation was supplied on standard input.",
            file=sys.stderr,
        )
        return 2
    ok, errors, manifest = validate_capture(source)
    if not ok:
        print("FATAL: conversation capture is not parseable for Lolla.", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2

    if conversation_path.exists():
        existing = conversation_path.read_text(encoding="utf-8")
        if existing != source:
            print(
                "FATAL: this run already contains different source text; "
                "start a new $lolla run instead of replacing it.",
                file=sys.stderr,
            )
            return 3
        conversation_path.chmod(0o600)
    else:
        _atomic_private_write(conversation_path, source)

    if not _event_already_recorded(events_path):
        append_run_event(
            run_id=run_id,
            event_type="conversation_captured",
            actor="skill",
            path=events_path,
            details={
                "bytes": len(source.encode("utf-8")),
                "message_blocks": int(manifest["actual_user_turns"])
                + int(manifest["actual_assistant_turns"]),
                "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                "capture_surface": "private_runtime_stdin",
            },
        )
        events_path.chmod(0o600)

    print(
        "CAPTURE_STATUS: ready; "
        f"message_blocks={int(manifest['actual_user_turns']) + int(manifest['actual_assistant_turns'])}; "
        f"bytes={len(source.encode('utf-8'))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
