#!/usr/bin/env python3
"""Build offline Decision Work conversation interpretation packets."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = Path(
    "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
)


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_conversation_interpretation_packets import (
        DecisionWorkConversationInterpretationPacketInputError,
        build_decision_work_conversation_interpretation_packets,
        render_decision_work_conversation_interpretation_packets_json,
        validate_output_path,
        write_decision_work_conversation_interpretation_packets_output,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build lolla.decision_work_conversation_interpretation_packets.v0 "
            "JSON from an existing completed Lolla run directory. This command "
            "does not run Lolla, invoke the skill, call models, mutate archives, "
            "fill semantic contract fields, score advice, create labels, or "
            "authorize agent action."
        )
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Completed run directory to inspect read-only.",
    )
    parser.add_argument(
        "--contract",
        default=DEFAULT_CONTRACT,
        type=Path,
        help="PR128 conversation interpretation contract JSON.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON path. Refused if it resolves inside the run directory.",
    )
    parser.add_argument(
        "--mode",
        choices=("checked_in_safe", "local_private_metadata"),
        default="checked_in_safe",
        help=(
            "checked_in_safe records source refs/status only for shareable "
            "metadata packets. local_private_metadata may point at local/private "
            "availability but still does not copy raw text."
        ),
    )
    parser.add_argument(
        "--decision-work-brief-packet",
        type=Path,
        help="Optional existing PR115 brief packet JSON to reference by metadata.",
    )
    parser.add_argument(
        "--decision-work-brief",
        type=Path,
        help="Optional existing Decision Work Brief JSON to reference by metadata.",
    )
    parser.add_argument(
        "--rendered-decision-work-brief",
        type=Path,
        help="Optional rendered brief Markdown to reference by metadata.",
    )
    parser.add_argument(
        "--decision-work-receipt",
        type=Path,
        help="Optional Decision Work Receipt JSON to link by metadata only.",
    )
    parser.add_argument(
        "--decision-trail-report",
        type=Path,
        help="Optional Decision Trail report JSON to link by metadata only.",
    )
    parser.add_argument(
        "--product-delta-report",
        type=Path,
        help="Optional Product Delta report/review JSON to link by metadata only.",
    )
    parser.add_argument(
        "--limit-fields",
        type=int,
        help="Optional test/debug limit for the number of contract fields emitted.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        output = validate_output_path(output_path=args.out, run_dir=args.run_dir)
        packet = build_decision_work_conversation_interpretation_packets(
            run_dir=args.run_dir,
            contract_path=args.contract,
            mode=args.mode,
            decision_work_brief_packet_path=args.decision_work_brief_packet,
            decision_work_brief_path=args.decision_work_brief,
            rendered_decision_work_brief_path=args.rendered_decision_work_brief,
            decision_work_receipt_path=args.decision_work_receipt,
            decision_trail_report_path=args.decision_trail_report,
            product_delta_report_path=args.product_delta_report,
            limit_fields=args.limit_fields,
        )
        payload = render_decision_work_conversation_interpretation_packets_json(
            packet,
            pretty=args.pretty,
        )
        write_decision_work_conversation_interpretation_packets_output(output, payload)
    except DecisionWorkConversationInterpretationPacketInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
