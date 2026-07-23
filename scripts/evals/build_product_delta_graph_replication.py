#!/usr/bin/env python3
"""Build or validate the provider-free graph-replication packets."""
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
    from engine.system_b.product_delta_graph_replication import (
        ProductDeltaGraphReplicationError,
        build_graph_replication,
        render_json,
        validate_checked_in_replication,
        write_checked_in_replication,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Freeze or validate eight exact, neutrally aliased Product Delta "
            "replication packets. This command generates no semantic output "
            "and makes no provider, graph, runtime, skill, private-archive, "
            "or human-authority call."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--write", action="store_true")
    action.add_argument(
        "--print",
        dest="print_artifact",
        choices=("generation", "sealed"),
    )
    args = parser.parse_args(argv)

    try:
        if args.validate_only:
            errors = validate_checked_in_replication(repo_root=REPO_ROOT)
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Product Delta graph-replication artifacts are current.")
            return 0
        if args.write:
            write_checked_in_replication(repo_root=REPO_ROOT)
            print("Product Delta graph-replication artifacts written.")
            return 0
        generation, sealed = build_graph_replication(repo_root=REPO_ROOT)
        selection = {"generation": generation, "sealed": sealed}
        print(render_json(selection[args.print_artifact]), end="")
        return 0
    except ProductDeltaGraphReplicationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
