#!/usr/bin/env python3
"""Build or validate the agent-only direct-vs-current-one-hop rehearsal."""
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
    from engine.system_b.product_delta_graph_increment_rehearsal import (
        ProductDeltaGraphIncrementRehearsalError,
        build_graph_increment_rehearsal,
        render_json,
        validate_checked_in_rehearsal,
        write_checked_in_rehearsal,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Freeze or validate source-first, post-seal reference, and neutrally "
            "aliased direct/current-one-hop rehearsal packets. This command makes "
            "no repository provider API, graph, runtime, private-archive, or "
            "human-authority call."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--write", action="store_true")
    action.add_argument(
        "--print",
        dest="print_artifact",
        choices=("source-first", "post-seal", "generation", "sealed"),
    )
    args = parser.parse_args(argv)

    try:
        if args.validate_only:
            errors = validate_checked_in_rehearsal(repo_root=REPO_ROOT)
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Product Delta graph-increment rehearsal artifacts are current.")
            return 0
        if args.write:
            write_checked_in_rehearsal(repo_root=REPO_ROOT)
            print("Product Delta graph-increment rehearsal artifacts written.")
            return 0
        payloads = build_graph_increment_rehearsal(repo_root=REPO_ROOT)
        selection = {
            "source-first": payloads[0],
            "post-seal": payloads[1],
            "generation": payloads[2],
            "sealed": payloads[3],
        }
        print(render_json(selection[args.print_artifact]), end="")
        return 0
    except ProductDeltaGraphIncrementRehearsalError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
