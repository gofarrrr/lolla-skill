#!/usr/bin/env python3
"""Build offline Decision Work automatic triage packets."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRIAGE_CONTRACT = Path(
    "docs/conversation-understanding/decision-work-automatic-triage-contract-v0.json"
)


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_automatic_triage_packets import (
        DecisionWorkAutomaticTriagePacketInputError,
        build_decision_work_automatic_triage_packets,
        render_decision_work_automatic_triage_packets_json,
        validate_output_path,
        write_decision_work_automatic_triage_packets_output,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build lolla.decision_work_automatic_triage_packets.v0 JSON from "
            "existing checked-in Decision Work Brief, interpretation, review, "
            "and triage-contract artifacts. This command does not run Lolla, "
            "invoke the skill, call models, mutate archives, fill triage "
            "fields, score advice, create labels, or authorize action."
        )
    )
    parser.add_argument(
        "--triage-contract",
        default=DEFAULT_TRIAGE_CONTRACT,
        type=Path,
        help="PR154 automatic triage contract JSON.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output JSON path.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        output = validate_output_path(
            output_path=args.out,
            triage_contract_path=args.triage_contract,
        )
        packet = build_decision_work_automatic_triage_packets(
            triage_contract_path=args.triage_contract,
        )
        payload = render_decision_work_automatic_triage_packets_json(
            packet,
            pretty=args.pretty,
        )
        write_decision_work_automatic_triage_packets_output(output, payload)
    except DecisionWorkAutomaticTriagePacketInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
