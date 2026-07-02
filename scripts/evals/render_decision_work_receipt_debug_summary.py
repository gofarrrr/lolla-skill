#!/usr/bin/env python3
"""Render an internal Decision Work Receipt debug Markdown packet."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_receipt_debug_summary import (
        DecisionWorkReceiptDebugSummaryInputError,
        load_json_object,
        render_decision_work_receipt_debug_summary,
        write_decision_work_receipt_debug_summary,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Render an internal Markdown debug summary from a "
            "lolla.decision_work_receipt.v0 JSON artifact and optional "
            "lolla.decision_trail_report.v0 JSON artifact."
        )
    )
    parser.add_argument(
        "--receipt",
        required=True,
        type=Path,
        help="Decision Work Receipt JSON to summarize.",
    )
    parser.add_argument(
        "--decision-trail-report",
        type=Path,
        default=None,
        help="Optional Decision Trail report JSON to summarize by field status.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output Markdown path.",
    )
    args = parser.parse_args(argv)

    try:
        receipt = load_json_object(args.receipt)
        decision_trail_report = (
            load_json_object(args.decision_trail_report)
            if args.decision_trail_report is not None
            else None
        )
        markdown = render_decision_work_receipt_debug_summary(
            receipt=receipt,
            decision_trail_report=decision_trail_report,
        )
        write_decision_work_receipt_debug_summary(args.out, markdown)
    except DecisionWorkReceiptDebugSummaryInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
