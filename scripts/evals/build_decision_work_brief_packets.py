#!/usr/bin/env python3
"""Build read-only Decision Work Brief interpretation packets."""
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
    from engine.system_b.decision_work_brief_packets import (
        DecisionWorkBriefPacketInputError,
        build_decision_work_brief_packets,
        render_decision_work_brief_packets_json,
        validate_output_path,
        write_decision_work_brief_packets_output,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build lolla.decision_work_brief_packets.v0 JSON from an existing "
            "completed Lolla run directory. This command does not run Lolla, "
            "invoke the skill, call models, mutate archives, generate a brief, "
            "score advice, create labels, or authorize agent action."
        )
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Completed run directory to inspect read-only.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON path. Refused if it resolves inside the run directory.",
    )
    parser.add_argument(
        "--decision-work-receipt",
        type=Path,
        help="Optional existing Decision Work Receipt JSON to link by metadata only.",
    )
    parser.add_argument(
        "--decision-trail-report",
        type=Path,
        help="Optional existing Decision Trail report JSON to link by metadata only.",
    )
    parser.add_argument(
        "--product-delta-report",
        type=Path,
        help="Optional existing Product Delta report/review JSON to link by metadata only.",
    )
    parser.add_argument(
        "--mode",
        choices=("metadata_only", "local_private"),
        default="metadata_only",
        help=(
            "metadata_only records source metadata without text. local_private "
            "may include capped text only when --include-private-text is also set."
        ),
    )
    parser.add_argument(
        "--include-private-text",
        action="store_true",
        help=(
            "Only with --mode local_private: copy capped local private text into "
            "the output and mark it unsafe for commit."
        ),
    )
    parser.add_argument("--max-text-chars", type=int, default=12000)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        output = validate_output_path(
            output_path=args.out,
            run_dir=args.run_dir,
            mode=args.mode,
            include_private_text=args.include_private_text,
            repo_root=REPO_ROOT,
        )
        packet = build_decision_work_brief_packets(
            run_dir=args.run_dir,
            mode=args.mode,
            include_private_text=args.include_private_text,
            decision_work_receipt_path=args.decision_work_receipt,
            decision_trail_report_path=args.decision_trail_report,
            product_delta_report_path=args.product_delta_report,
            max_text_chars=args.max_text_chars,
        )
        payload = render_decision_work_brief_packets_json(
            packet,
            pretty=args.pretty,
        )
        write_decision_work_brief_packets_output(output, payload)
    except DecisionWorkBriefPacketInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
