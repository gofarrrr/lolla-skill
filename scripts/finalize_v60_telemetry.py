#!/usr/bin/env python3
"""Finalize V60 consideration telemetry for an in-flight Lolla result.

This is deliberately deterministic. If a skill orchestrator fails to write the
private V60 ledger, the run should become observably incomplete instead of
silently looking like a full V60-considered run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.v60_enrichment import finalize_v60_consideration  # noqa: E402


_RESULT_RE = re.compile(r"^lolla_(?P<run_id>.+)_result\.json$")


def _infer_result_path(run_id: str | None, result: str | None) -> Path:
    if result:
        return Path(result)
    if not run_id:
        raise SystemExit("Either --result or --run-id is required")
    return Path("/tmp") / f"lolla_{run_id}_result.json"


def _infer_ledger_path(result_path: Path, run_id: str | None, ledger: str | None) -> Path | None:
    if ledger:
        return Path(ledger)
    if run_id:
        return Path("/tmp") / f"lolla_{run_id}_v60_ledger.json"
    match = _RESULT_RE.match(result_path.name)
    if not match:
        return None
    return result_path.with_name(f"lolla_{match.group('run_id')}_v60_ledger.json")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--run-id", default=None, help="Run ID used for /tmp/lolla_{RUN_ID}_*.json")
    parser.add_argument("--result", default=None, help="Explicit result JSON path")
    parser.add_argument("--ledger", default=None, help="Explicit V60 ledger JSON path")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output for user-facing skill runs")
    parser.add_argument(
        "--require-valid",
        action="store_true",
        help="Return non-zero unless the V60 ledger is valid or not required.",
    )
    args = parser.parse_args()

    result_path = _infer_result_path(args.run_id, args.result)
    if not result_path.exists():
        print(f"V60 telemetry finalization skipped: missing result {result_path}", file=sys.stderr)
        return 1

    ledger_path = _infer_ledger_path(result_path, args.run_id, args.ledger)
    result = json.loads(result_path.read_text(encoding="utf-8"))
    ledger = None
    if ledger_path and ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

    finalized = finalize_v60_consideration(result, ledger=ledger)
    result_path.write_text(json.dumps(finalized, indent=2, ensure_ascii=False), encoding="utf-8")

    health = finalized.get("run_health") or {}
    status = health.get("v60_consideration_ledger", "unknown")
    if not args.quiet:
        if ledger_path:
            print(f"V60 consideration telemetry finalized: {status} ({ledger_path})")
        else:
            print(f"V60 consideration telemetry finalized: {status}")
    if args.require_valid and status not in {"valid", "not_required"}:
        validation = finalized.get("v60_consideration_validation") or {}
        errors = validation.get("errors") or []
        print(
            f"V60 consideration ledger is {status}; repair it before continuing.",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
