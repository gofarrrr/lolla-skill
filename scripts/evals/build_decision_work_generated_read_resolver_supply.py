#!/usr/bin/env python3
"""Build deterministic Decision Work generated-read resolver supply."""
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
    from engine.system_b.decision_work_generated_read_resolver_supply import (
        DecisionWorkGeneratedReadResolverSupplyError,
        build_generated_read_resolver_supply,
        render_generated_read_resolver_supply_json,
        write_generated_read_resolver_supply,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic resolver-candidate packet from generated-read "
            "artifacts. This command validates and normalizes refs/status only; "
            "it does not approve resolver refs, update sidecars, wire runtime, "
            "score advice, or authorize action."
        )
    )
    parser.add_argument("--read", required=True, type=Path)
    parser.add_argument("--intake", required=True, type=Path)
    parser.add_argument("--brief-supply", required=True, type=Path)
    parser.add_argument("--rendered-brief", required=True, type=Path)
    parser.add_argument("--triage-supply", required=True, type=Path)
    parser.add_argument("--triage", required=True, type=Path)
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
        result = build_generated_read_resolver_supply(
            read_path=args.read,
            intake_path=args.intake,
            brief_supply_path=args.brief_supply,
            rendered_brief_path=args.rendered_brief,
            triage_supply_path=args.triage_supply,
            triage_path=args.triage,
            queue_item_path=args.queue_item,
            prompt_packet_path=args.prompt_packet,
        )
        payload = render_generated_read_resolver_supply_json(
            result,
            pretty=args.pretty,
        )
        write_generated_read_resolver_supply(args.out, payload)
    except DecisionWorkGeneratedReadResolverSupplyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
