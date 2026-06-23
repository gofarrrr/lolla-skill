#!/usr/bin/env python3
"""Append a recovery/operator event to a Lolla run ledger."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.run_events import append_run_event  # noqa: E402
from engine.system_b.run_state import assert_expected_run_state  # noqa: E402


def _parse_details(items: list[str]) -> dict[str, str]:
    details: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            details[item] = "true"
            continue
        key, value = item.split("=", 1)
        details[key.strip()] = value.strip()
    return details


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--event-type", required=True)
    parser.add_argument("--actor", default="operator")
    parser.add_argument(
        "--detail",
        action="append",
        default=[],
        help="Repeatable key=value detail. Bare keys are recorded as true.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    try:
        assert_expected_run_state(
            actual_run_id=args.run_id,
            artifact_paths=[Path("/tmp") / f"lolla_{args.run_id}_run_events.json"],
            phase="record_run_event",
        )
        payload = append_run_event(
            run_id=args.run_id,
            event_type=args.event_type,
            actor=args.actor,
            details=_parse_details(args.detail),
        )
    except (ValueError, SystemExit) as exc:
        print(f"Run event write failed: {exc}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(
            json.dumps(
                {
                    "status": "ok",
                    "run_id": args.run_id,
                    "event_count": len(payload.get("events") or []),
                },
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
