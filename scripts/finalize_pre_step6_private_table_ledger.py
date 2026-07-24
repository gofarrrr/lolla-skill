#!/usr/bin/env python3
"""Finalize pre-Step-6 private-table ledger telemetry for an in-flight run."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.pre_step6_private_table import (  # noqa: E402
    finalize_pre_step6_private_table_ledger,
)
from engine.system_b.run_state import (  # noqa: E402
    assert_expected_run_state,
    runtime_tmp_dir,
)

_RESULT_RE = re.compile(r"^lolla_(?P<run_id>.+)_result\.json$")


def _infer_result_path(run_id: str | None, result: str | None) -> Path:
    if result:
        return Path(result)
    if not run_id:
        raise SystemExit("Either --result or --run-id is required")
    return runtime_tmp_dir() / f"lolla_{run_id}_result.json"


def _infer_ledger_path(result_path: Path, run_id: str | None, ledger: str | None) -> Path | None:
    if ledger:
        return Path(ledger)
    if run_id:
        return runtime_tmp_dir() / (
            f"lolla_{run_id}_pre_step6_private_table_ledger.json"
        )
    match = _RESULT_RE.match(result_path.name)
    if not match:
        return None
    return result_path.with_name(
        f"lolla_{match.group('run_id')}_pre_step6_private_table_ledger.json"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--run-id", default=None, help="Run ID used for /tmp/lolla_{RUN_ID}_*.json")
    parser.add_argument("--result", default=None, help="Explicit result JSON path")
    parser.add_argument("--ledger", default=None, help="Explicit private-table ledger JSON path")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output")
    parser.add_argument(
        "--require-valid",
        action="store_true",
        help="Return non-zero unless the private-table ledger is valid or not required.",
    )
    args = parser.parse_args()

    result_path = _infer_result_path(args.run_id, args.result)
    if not result_path.exists():
        print(f"Pre-Step-6 private-table finalization skipped: missing result {result_path}", file=sys.stderr)
        return 1

    ledger_path = _infer_ledger_path(result_path, args.run_id, args.ledger)
    inferred_run_id = args.run_id
    if not inferred_run_id:
        match = _RESULT_RE.match(result_path.name)
        inferred_run_id = match.group("run_id") if match else None
    try:
        assert_expected_run_state(
            actual_run_id=inferred_run_id,
            artifact_paths=[result_path, ledger_path],
            phase="finalize_pre_step6_private_table_ledger",
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1
    result = json.loads(result_path.read_text(encoding="utf-8"))
    ledger = None
    if ledger_path and ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

    finalized = finalize_pre_step6_private_table_ledger(result, ledger=ledger)
    result_path.write_text(json.dumps(finalized, indent=2, ensure_ascii=False), encoding="utf-8")

    health = finalized.get("run_health") or {}
    status = health.get("pre_step6_private_table_ledger", "unknown")
    if not args.quiet:
        if ledger_path:
            print(f"Pre-Step-6 private-table ledger finalized: {status} ({ledger_path})")
        else:
            print(f"Pre-Step-6 private-table ledger finalized: {status}")
    if args.require_valid and status not in {"valid", "not_required"}:
        validation = finalized.get("pre_step6_private_table_ledger_validation") or {}
        errors = validation.get("errors") or []
        print(
            f"Pre-Step-6 private-table ledger is {status}; repair it before continuing.",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
