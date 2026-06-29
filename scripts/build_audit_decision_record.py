#!/usr/bin/env python3
"""Build a read-only Lolla audit decision record."""
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
    from engine.system_b.audit_decision_record import (
        AuditDecisionRecordInputError,
        build_audit_decision_record,
        render_audit_decision_record_json,
        validate_output_path,
        write_audit_decision_record_output,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a read-only lolla.audit_decision_record.v0 JSON artifact "
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
        "--review-json",
        type=Path,
        help="Optional structured human-review JSON reference.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    args = parser.parse_args(argv)

    try:
        output = validate_output_path(output_path=args.out, run_dir=args.run_dir)
        record = build_audit_decision_record(
            run_dir=args.run_dir,
            review_json=args.review_json,
        )
        payload = render_audit_decision_record_json(record, pretty=args.pretty)
        write_audit_decision_record_output(output, payload)
    except AuditDecisionRecordInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
