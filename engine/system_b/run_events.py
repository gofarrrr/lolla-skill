"""Append-only recovery/event ledger for Lolla runs."""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Mapping

from .run_state import is_valid_run_id, runtime_tmp_dir


RUN_EVENTS_SCHEMA_VERSION = "lolla.run_events.v0.1"


def append_run_event(
    *,
    run_id: str,
    event_type: str,
    details: Mapping[str, Any] | None = None,
    actor: str = "operator",
    path: Path | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    """Append a run event and return the full ledger payload."""
    if not is_valid_run_id(run_id):
        raise ValueError(f"Invalid run_id for run event ledger: {run_id!r}")
    ledger_path = path or runtime_tmp_dir() / f"lolla_{run_id}_run_events.json"
    payload = _load_payload(ledger_path, run_id=run_id)
    events = payload.setdefault("events", [])
    if not isinstance(events, list):
        events = []
        payload["events"] = events
    event = {
        "event_id": f"event_{len(events) + 1:03d}",
        "event_type": str(event_type or "unspecified"),
        "occurred_at": occurred_at or _utc_now_iso(),
        "actor": str(actor or "operator"),
        "details": dict(details or {}),
    }
    events.append(event)
    ledger_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    ledger_path.chmod(0o600)
    return payload


def load_run_events(run_dir: Path) -> dict[str, Any]:
    """Load archived ``run_events.json`` if present."""
    path = Path(run_dir) / "run_events.json"
    if not path.exists():
        return {
            "schema_version": RUN_EVENTS_SCHEMA_VERSION,
            "status": "not_recorded",
            "event_count": 0,
            "artifact_path": "",
            "events": [],
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "schema_version": RUN_EVENTS_SCHEMA_VERSION,
            "status": "unreadable",
            "event_count": 0,
            "artifact_path": "run_events.json",
            "events": [],
        }
    events = payload.get("events") if isinstance(payload, dict) else []
    if not isinstance(events, list):
        events = []
    return {
        "schema_version": str(
            (payload if isinstance(payload, dict) else {}).get("schema_version")
            or RUN_EVENTS_SCHEMA_VERSION
        ),
        "status": "recorded" if events else "empty",
        "event_count": len(events),
        "artifact_path": "run_events.json",
        "events": [event for event in events if isinstance(event, dict)],
    }


def _load_payload(path: Path, *, run_id: str) -> dict[str, Any]:
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                payload.setdefault("schema_version", RUN_EVENTS_SCHEMA_VERSION)
                payload.setdefault("run_id", run_id)
                payload.setdefault("events", [])
                return payload
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "schema_version": RUN_EVENTS_SCHEMA_VERSION,
        "run_id": run_id,
        "events": [],
    }


def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
