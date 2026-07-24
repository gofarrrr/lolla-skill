#!/usr/bin/env python3
"""Persist the default-off Step 8b pressure-check state for a Lolla run."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.run_events import append_run_event  # noqa: E402
from engine.system_b.private_runtime import (  # noqa: E402
    atomic_private_write_json,
    atomic_private_write_text,
)
from engine.system_b.run_state import (  # noqa: E402
    assert_expected_run_state,
    runtime_tmp_dir,
)


def _run_id_from_args(value: str | None) -> str:
    run_id = value or os.environ.get("LOLLA_RUN_ID", "")
    if not run_id:
        raise SystemExit("FATAL: LOLLA_RUN_ID is not set. Re-run /lolla setup before Step 8b.")
    return run_id


def persist_default_off(run_id: str, *, tmp_dir: Path | None = None) -> Path:
    tmp_dir = tmp_dir or runtime_tmp_dir()
    result_path = tmp_dir / f"lolla_{run_id}_result.json"
    assert_expected_run_state(
        actual_run_id=run_id,
        artifact_paths=[result_path],
        phase="step8b_pressure_check_state",
    )
    if not result_path.exists():
        raise SystemExit(
            "FATAL: the exact run has no result artifact. Step 3 did not complete."
        )

    summary = "No additional pressure check was run in the default flow."
    gap_check = {
        "schema_version": "lolla_gap_check.v2",
        "status": "not_run_default_off",
        "reason": "post_step6_pressure_check_default_off",
        "lanes": [],
    }
    written_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    atomic_private_write_text(
        tmp_dir / f"lolla_{run_id}_gapcheck.txt",
        summary + "\n",
    )
    atomic_private_write_json(
        tmp_dir / f"lolla_{run_id}_gapcheck_lanes.json",
        gap_check,
    )

    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["gap_check_summary"] = summary
    payload["gap_check"] = gap_check
    payload["has_gap_check"] = True
    payload["pressure_check_mode"] = "default_off"
    payload["gap_check_written_at"] = written_at
    payload["pressure_check_state"] = {
        "status": "not_run_default_off",
        "summary": summary,
        "gap_check": gap_check,
        "sub_agent_usage": [],
        "written_at": written_at,
    }
    atomic_private_write_json(result_path, payload)
    try:
        append_run_event(
            run_id=run_id,
            event_type="pressure_check_state_persisted",
            details={"status": "not_run_default_off", "mode": "default_off"},
        )
    except Exception:
        pass
    return result_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    persist_default_off(_run_id_from_args(args.run_id))
    print("PRESSURE_CHECK_STATUS: default_off ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
