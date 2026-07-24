#!/usr/bin/env python3
"""Seal one extraction attempt and preserve failed-run process evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

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


SCHEMA_VERSION = "lolla.extraction_terminal.v1"
MANIFEST_SCHEMA_VERSION = "lolla.failed_extraction_archive.v1"
DEFAULT_ARCHIVE_ROOT = Path.home() / ".local" / "share" / "lolla" / "runs"
PROVIDER_INTERRUPTION_RECEIPT = (
    "Lolla stopped before the graph because the model provider interrupted "
    "the conversation read. No automatic retry was made. The source and "
    "failure evidence were preserved privately. Start a new `$lolla` run "
    "when you want to try again."
)


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return default


def _atomic_private_json(path: Path, payload: dict[str, Any]) -> None:
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
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
        path.chmod(0o600)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink(missing_ok=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _append_receipt_once(path: Path, receipt: str) -> None:
    try:
        existing = path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        existing = ""
    if receipt in existing:
        return
    separator = "" if not existing or existing.endswith("\n\n") else (
        "\n" if existing.endswith("\n") else "\n\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(separator + receipt + "\n")
    path.chmod(0o600)


def _archive_failed_run(
    *,
    run_id: str,
    tmp_dir: Path,
    archive_root: Path,
) -> tuple[Path, dict[str, Any]]:
    run_dir = archive_root / "_failed-extractions" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    run_dir.chmod(0o700)
    artifact_names = (
        ("conversation.txt", "conversation.txt"),
        ("conversation_processing_view.txt", "conversation_processing_view.txt"),
        ("conversation_processing_view.json", "conversation_processing_view.json"),
        ("extraction.json", "extraction.json"),
        ("extraction_calls.json", "extraction_calls.json"),
        ("provider_budget.json", "provider_budget.json"),
        ("live_transcript.txt", "live_transcript.txt"),
        ("operator.log", "operator.log"),
        ("run_events.json", "run_events.json"),
        ("extraction_terminal.json", "extraction_terminal.json"),
    )
    copied: list[dict[str, Any]] = []
    for source_tail, archive_name in artifact_names:
        source = tmp_dir / f"lolla_{run_id}_{source_tail}"
        if not source.exists() or not source.is_file():
            continue
        destination = run_dir / archive_name
        shutil.copyfile(source, destination)
        destination.chmod(0o600)
        copied.append(
            {
                "artifact": archive_name,
                "bytes": destination.stat().st_size,
                "sha256": _sha256(destination),
            }
        )
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "run_id": run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "terminal_state": "failed",
        "graph_pipeline_started": False,
        "claim_boundary": (
            "This archive proves failed-extraction process custody only. It "
            "contains no graph result, reconsideration, quality judgment, or "
            "usefulness evidence."
        ),
        "artifacts": copied,
    }
    _atomic_private_json(run_dir / "failure_archive_manifest.json", manifest)
    return run_dir, manifest


def _failure_receipt(extraction: dict[str, Any]) -> str:
    provider_failure = extraction.get("provider_failure")
    provider_failure = (
        provider_failure if isinstance(provider_failure, dict) else {}
    )
    provider_status = str(provider_failure.get("status") or "")
    if provider_status:
        return PROVIDER_INTERRUPTION_RECEIPT
    error_text = str(extraction.get("error") or "")
    if "missing required fields" in error_text.lower():
        cause = (
            "the completed conversation read did not contain the required "
            "decision structure"
        )
    else:
        cause = "the conversation read failed its technical admission checks"
    return (
        f"Lolla stopped before the graph because {cause}. No automatic retry "
        "was made. The source and failure evidence were preserved privately. "
        "Start a new `$lolla` run when you want to try again."
    )


def _print_terminal(payload: dict[str, Any]) -> None:
    print(f"EXTRACTION_STATUS: {payload['extraction_status']}")
    print(f"EXTRACTION_TERMINAL: {payload['terminal_state']}")
    if payload["terminal_state"] == "failed":
        print("USER_FAILURE_RECEIPT_BEGIN")
        print(str(payload.get("user_failure_receipt") or ""))
        print("USER_FAILURE_RECEIPT_END")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command-exit", type=int, required=True)
    args = parser.parse_args()

    run_id = str(os.getenv("LOLLA_RUN_ID", "")).strip()
    if not is_valid_run_id(run_id):
        print("FATAL: LOLLA_RUN_ID is missing or invalid.", file=sys.stderr)
        return 2
    tmp_dir = Path(os.getenv("LOLLA_TMP_DIR", "/tmp")).expanduser()
    terminal_path = tmp_dir / f"lolla_{run_id}_extraction_terminal.json"
    extraction_path = tmp_dir / f"lolla_{run_id}_extraction.json"
    calls_path = tmp_dir / f"lolla_{run_id}_extraction_calls.json"
    budget_path = tmp_dir / f"lolla_{run_id}_provider_budget.json"
    events_path = tmp_dir / f"lolla_{run_id}_run_events.json"
    live_transcript = Path(
        os.getenv(
            "LOLLA_LIVE_TRANSCRIPT",
            str(tmp_dir / f"lolla_{run_id}_live_transcript.txt"),
        )
    )
    try:
        assert_expected_run_state(
            actual_run_id=run_id,
            artifact_paths=[
                terminal_path,
                extraction_path,
                calls_path,
                budget_path,
                events_path,
                live_transcript,
            ],
            phase="finalize_extraction_attempt",
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2

    existing_terminal = _load_json(terminal_path, {})
    if isinstance(existing_terminal, dict) and existing_terminal.get(
        "schema_version"
    ) == SCHEMA_VERSION:
        _print_terminal(existing_terminal)
        return 0

    extraction = _load_json(extraction_path, {})
    extraction = extraction if isinstance(extraction, dict) else {}
    calls = _load_json(calls_path, [])
    calls = calls if isinstance(calls, list) else []
    budget = _load_json(budget_path, {})
    budget = budget if isinstance(budget, dict) else {}
    extraction_status = str(extraction.get("status") or "missing")
    if extraction_status == "ok" and args.command_exit == 0:
        terminal_state = "completed"
        event_type = "extraction_completed"
    elif extraction_status in {"not_strategic", "capture_critical"}:
        terminal_state = "declined"
        event_type = "extraction_declined"
    else:
        terminal_state = "failed"
        event_type = "extraction_failed"

    recorded_count = len([call for call in calls if isinstance(call, dict)])
    budget_count_raw = budget.get("attempted_provider_calls")
    try:
        budget_count = int(budget_count_raw)
    except (TypeError, ValueError):
        budget_count = 0
    archive_root = Path(
        os.getenv("LOLLA_ARCHIVE_DIR", str(DEFAULT_ARCHIVE_ROOT))
    ).expanduser()
    archive_path = (
        archive_root / "_failed-extractions" / run_id
        if terminal_state == "failed"
        else None
    )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "terminal_state": terminal_state,
        "extraction_status": extraction_status,
        "command_exit": args.command_exit,
        "same_run_retry_allowed": False,
        "graph_pipeline_started": False,
        "provider_failure": extraction.get("provider_failure") or {},
        "provider_calls": {
            "recorded_call_count": recorded_count,
            "budget_attempted_call_count": budget_count,
            "history_consistent": recorded_count == budget_count,
            "accounted_cost_usd": float(
                budget.get("accounted_cost_usd") or 0.0
            ),
            "provider_reported_cost_usd": float(
                budget.get("provider_reported_cost_usd") or 0.0
            ),
        },
        "failure_archive": {
            "status": "planned" if archive_path is not None else "not_applicable",
            "path": str(archive_path) if archive_path is not None else "",
        },
        "sealed_at": dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
    }
    if terminal_state == "failed":
        payload["user_failure_receipt"] = _failure_receipt(extraction)

    append_run_event(
        run_id=run_id,
        event_type=event_type,
        actor="skill",
        path=events_path,
        details={
            "terminal_state": terminal_state,
            "extraction_status": extraction_status,
            "command_exit": args.command_exit,
            "recorded_provider_calls": recorded_count,
            "budget_attempted_provider_calls": budget_count,
        },
    )
    events_path.chmod(0o600)
    if terminal_state == "failed":
        _append_receipt_once(
            live_transcript,
            str(payload["user_failure_receipt"]),
        )
        payload["failure_archive"]["status"] = "written"
    _atomic_private_json(terminal_path, payload)

    if terminal_state == "failed":
        try:
            _archive_failed_run(
                run_id=run_id,
                tmp_dir=tmp_dir,
                archive_root=archive_root,
            )
        except OSError as exc:
            payload["failure_archive"] = {
                "status": "failed",
                "path": str(archive_path),
                "error_type": type(exc).__name__,
            }
            _atomic_private_json(terminal_path, payload)
            print(
                "FATAL: failed-extraction custody archive could not be written.",
                file=sys.stderr,
            )
            return 3

    _print_terminal(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
