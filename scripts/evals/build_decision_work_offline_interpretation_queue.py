#!/usr/bin/env python3
"""Build offline Decision Work interpretation queue items."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACT = Path(
    "docs/conversation-understanding/"
    "decision-work-offline-interpretation-queue-contract-v0.json"
)


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_offline_interpretation_queue import (
        DecisionWorkOfflineInterpretationQueueError,
        build_decision_work_offline_interpretation_queue_item,
        render_decision_work_offline_interpretation_queue_item_json,
        validate_output_path,
        write_decision_work_offline_interpretation_queue_output,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a checked-in-safe offline interpretation queue item for "
            "Decision Work automatic semantic supply. This command records refs, "
            "status, missingness, validation requirements, and non-claims only; "
            "it does not run Lolla, invoke the skill, call models, create "
            "interpretation reads, mutate archives, update runtime hooks, score "
            "advice, or authorize action."
        )
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        type=Path,
        help="Completed run directory ref to represent in the queue item.",
    )
    parser.add_argument(
        "--contract",
        default=DEFAULT_CONTRACT,
        type=Path,
        help="PR179 offline interpretation queue contract JSON.",
    )
    parser.add_argument(
        "--source-packet",
        type=Path,
        help="Optional PR130 conversation interpretation packet JSON.",
    )
    parser.add_argument(
        "--mode",
        choices=("checked_in_safe_metadata_only", "local_private_operator", "disabled"),
        default="checked_in_safe_metadata_only",
    )
    parser.add_argument(
        "--output-destination-ref",
        help=(
            "Optional future interpretation-read ref to record as a destination "
            "placeholder. The file is not created by this command."
        ),
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON path. Refused if it resolves inside the run directory.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        output = validate_output_path(output_path=args.out, run_dir=args.run_dir)
        item = build_decision_work_offline_interpretation_queue_item(
            run_dir=args.run_dir,
            contract_path=args.contract,
            source_packet_path=args.source_packet,
            mode=args.mode,
            output_destination_ref=args.output_destination_ref,
        )
        payload = render_decision_work_offline_interpretation_queue_item_json(
            item,
            pretty=args.pretty,
        )
        write_decision_work_offline_interpretation_queue_output(output, payload)
    except DecisionWorkOfflineInterpretationQueueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
