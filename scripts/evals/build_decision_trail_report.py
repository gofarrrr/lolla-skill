#!/usr/bin/env python3
"""Build a read-only Lolla Decision Trail report."""
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
    from engine.system_b.decision_trail_report import (
        DecisionTrailReportInputError,
        build_decision_trail_report,
        render_decision_trail_report_json,
        validate_output_path,
        write_decision_trail_report_output,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a read-only lolla.decision_trail_report.v0 JSON artifact "
            "from an existing Lolla run archive directory."
        )
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Existing Lolla run archive directory to inspect read-only.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON path. Refused if it resolves inside the run directory.",
    )
    parser.add_argument(
        "--report-mode",
        default="checked_in_safe_mode",
        help="Report mode. PR87 implements checked_in_safe_mode only.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    args = parser.parse_args(argv)

    try:
        output = validate_output_path(output_path=args.out, run_dir=args.run_dir)
        report = build_decision_trail_report(
            run_dir=args.run_dir,
            report_mode=args.report_mode,
        )
        payload = render_decision_trail_report_json(report, pretty=args.pretty)
        write_decision_trail_report_output(output, payload)
    except DecisionTrailReportInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
