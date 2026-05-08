#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.decision_pressure_trace_adapter import (  # noqa: E402
    build_decision_pressure_trace_review_report,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fixture-only smoke check for reviewed Decision Pressure traces."
    )
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--affordances", required=True, type=Path)
    parser.add_argument("--report-out", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    report = build_decision_pressure_trace_review_report(
        fixture_path=args.fixture,
        compiled_affordances_path=args.affordances,
    )

    if args.report_out is not None:
        if args.report_out.suffix != ".json":
            raise SystemExit(
                "--report-out must point to a review-only JSON report, not "
                "HTML or user-facing output"
            )
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print("decision_pressure_trace adapter smoke: passed")
    print(f"trace_id: {report['trace_id']}")
    print(f"selected_pressures: {report['selected_pressure_count']}")
    print(f"coverage_panels: {report['coverage_transparency_panel_count']}")
    print(f"suppressed_candidates: {report['suppressed_candidate_count']}")
    print(f"runtime_policy: {report['runtime_policy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
