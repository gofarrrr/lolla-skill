#!/usr/bin/env python3
"""Finalize the R2 apply/reject/park ledger for an in-flight Lolla run."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.constitutional_graph_survival import (  # noqa: E402
    finalize_constitutional_graph_survival_ledger,
)
from engine.system_b.run_state import assert_expected_run_state  # noqa: E402


_RESULT_RE = re.compile(r"^lolla_(?P<run_id>.+)_result\.json$")


def _result_path(run_id: str | None, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit)
    if not run_id:
        raise SystemExit("Either --result or --run-id is required")
    return Path("/tmp") / f"lolla_{run_id}_result.json"


def _ledger_path(result_path: Path, run_id: str | None, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    if run_id:
        return Path("/tmp") / f"lolla_{run_id}_constitutional_graph_survival_ledger.json"
    match = _RESULT_RE.match(result_path.name)
    if not match:
        return None
    return result_path.with_name(
        f"lolla_{match.group('run_id')}_constitutional_graph_survival_ledger.json"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--result", default=None)
    parser.add_argument("--ledger", default=None)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--require-valid", action="store_true")
    args = parser.parse_args()

    result_path = _result_path(args.run_id, args.result)
    if not result_path.exists():
        print(f"Graph-survival finalization skipped: missing result {result_path}", file=sys.stderr)
        return 1
    ledger_path = _ledger_path(result_path, args.run_id, args.ledger)
    inferred = args.run_id
    if not inferred:
        match = _RESULT_RE.match(result_path.name)
        inferred = match.group("run_id") if match else None
    try:
        assert_expected_run_state(
            actual_run_id=inferred,
            artifact_paths=[result_path, ledger_path],
            phase="finalize_constitutional_graph_survival_ledger",
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1

    result = json.loads(result_path.read_text(encoding="utf-8"))
    ledger = None
    if ledger_path is not None and ledger_path.exists():
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    finalized = finalize_constitutional_graph_survival_ledger(result, ledger=ledger)
    result_path.write_text(
        json.dumps(finalized, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    status = (finalized.get("run_health") or {}).get(
        "constitutional_graph_survival_ledger", "unknown"
    )
    if not args.quiet:
        print(f"Constitutional graph-survival ledger finalized: {status}")
    if args.require_valid and status not in {"valid", "not_required"}:
        validation = finalized.get("constitutional_graph_survival_ledger_validation") or {}
        print(
            f"Constitutional graph-survival ledger is {status}; repair it before continuing.",
            file=sys.stderr,
        )
        for error in validation.get("errors") or []:
            print(f"- {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
