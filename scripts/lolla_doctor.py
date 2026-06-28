#!/usr/bin/env python3
"""Run the read-only Lolla doctor/preflight report."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.lolla_doctor import (
        DoctorInputError,
        build_doctor_report,
        render_doctor_report_json,
        render_doctor_report_text,
        report_allows_output_write,
        write_report_output,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Inspect local Lolla wiring before running Lolla. The doctor is "
            "read-only, does not call models, and does not mutate archives."
        )
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        help="Optional explicit Lolla runtime/repo root.",
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        help="Optional archive root to check read-only.",
    )
    parser.add_argument(
        "--manifest",
        "--review-manifest",
        dest="manifest_path",
        type=Path,
        help="Optional review-corpus manifest JSON to parse read-only.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional output path. Refused if it resolves inside archive root.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Render machine-readable lolla.doctor_report.v0 JSON.",
    )
    args = parser.parse_args(argv)

    report = build_doctor_report(
        runtime_root=args.runtime_root,
        archive_root=args.archive_root,
        manifest_path=args.manifest_path,
        output_path=args.out,
        default_runtime_root=REPO_ROOT,
    )
    payload = (
        render_doctor_report_json(report)
        if args.json
        else render_doctor_report_text(report)
    )

    if args.out and report_allows_output_write(report):
        try:
            write_report_output(args.out, payload)
        except DoctorInputError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    else:
        print(payload, end="")

    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
