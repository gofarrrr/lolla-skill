#!/usr/bin/env python3
"""Build deterministic Decision Work generated-read brief supply."""
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
    from engine.system_b.decision_work_generated_read_brief_supply import (
        DecisionWorkGeneratedReadBriefSupplyError,
        build_generated_read_brief_supply,
        render_generated_read_brief_supply_json,
        write_generated_read_brief_supply,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic brief-supply packet from an accepted "
            "Decision Work generated interpretation read and PR182 intake "
            "result. This command validates, normalizes, and copies allowed "
            "fields only; it does not generate interpretation, render briefs, "
            "create triage, update sidecars, score advice, or authorize action."
        )
    )
    parser.add_argument(
        "--read",
        required=True,
        type=Path,
        help="Generated interpretation read JSON.",
    )
    parser.add_argument(
        "--intake",
        required=True,
        type=Path,
        help="PR182 generated-read intake result JSON.",
    )
    parser.add_argument(
        "--queue-item",
        type=Path,
        help="Optional queue item ref to record by safe ref only.",
    )
    parser.add_argument(
        "--prompt-packet",
        type=Path,
        help="Optional prompt packet ref to record by safe ref only.",
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = build_generated_read_brief_supply(
            read_path=args.read,
            intake_path=args.intake,
            queue_item_path=args.queue_item,
            prompt_packet_path=args.prompt_packet,
        )
        payload = render_generated_read_brief_supply_json(
            result,
            pretty=args.pretty,
        )
        write_generated_read_brief_supply(args.out, payload)
    except DecisionWorkGeneratedReadBriefSupplyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
