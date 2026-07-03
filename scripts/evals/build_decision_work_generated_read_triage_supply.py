#!/usr/bin/env python3
"""Build deterministic Decision Work generated-read triage supply."""
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
    from engine.system_b.decision_work_generated_read_triage_supply import (
        DecisionWorkGeneratedReadTriageSupplyError,
        build_generated_read_triage_supply,
        render_generated_read_triage_supply_json,
        write_generated_read_triage_supply,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic triage-supply packet from generated-read "
            "artifacts. This command validates and normalizes refs/status "
            "only; it does not generate triage, mark resolver refs usable, "
            "update sidecars, score advice, or authorize action."
        )
    )
    parser.add_argument("--read", required=True, type=Path)
    parser.add_argument("--intake", required=True, type=Path)
    parser.add_argument("--brief-supply", required=True, type=Path)
    parser.add_argument("--rendered-brief", required=True, type=Path)
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
        result = build_generated_read_triage_supply(
            read_path=args.read,
            intake_path=args.intake,
            brief_supply_path=args.brief_supply,
            rendered_brief_path=args.rendered_brief,
            queue_item_path=args.queue_item,
            prompt_packet_path=args.prompt_packet,
        )
        payload = render_generated_read_triage_supply_json(
            result,
            pretty=args.pretty,
        )
        write_generated_read_triage_supply(args.out, payload)
    except DecisionWorkGeneratedReadTriageSupplyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
