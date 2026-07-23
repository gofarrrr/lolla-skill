#!/usr/bin/env python3
"""Build or validate blind review inputs for the graph-increment rehearsal."""
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
    from engine.system_b.product_delta_graph_increment_rehearsal_result import (
        ProductDeltaGraphIncrementResultError,
        build_blind_review_inputs,
        build_review_consolidation,
        render_json,
        validate_checked_in_blind_review_inputs,
        validate_checked_in_review_consolidation,
        write_blind_review_inputs,
        write_review_consolidation,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Freeze or validate blind review inputs from first terminal "
            "agent-only rehearsal results. No provider, graph, runtime, private "
            "archive, or human-authority call is made."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--write-consolidation", action="store_true")
    action.add_argument("--validate-complete", action="store_true")
    action.add_argument(
        "--print",
        dest="print_artifact",
        choices=("blind", "sealed", "consolidation"),
    )
    args = parser.parse_args(argv)
    try:
        if args.write:
            write_blind_review_inputs(repo_root=REPO_ROOT)
            print("Graph-increment blind review inputs written.")
            return 0
        if args.validate_only:
            errors = validate_checked_in_blind_review_inputs(
                repo_root=REPO_ROOT
            )
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Graph-increment blind review inputs are current.")
            return 0
        if args.write_consolidation:
            write_review_consolidation(repo_root=REPO_ROOT)
            print("Graph-increment review consolidation written.")
            return 0
        if args.validate_complete:
            input_errors = validate_checked_in_blind_review_inputs(
                repo_root=REPO_ROOT
            )
            result_errors = validate_checked_in_review_consolidation(
                repo_root=REPO_ROOT
            )
            errors = input_errors + result_errors
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Graph-increment rehearsal result is current.")
            return 0
        if args.print_artifact == "consolidation":
            consolidation, errors = build_review_consolidation(
                repo_root=REPO_ROOT
            )
            if errors:
                raise ProductDeltaGraphIncrementResultError(
                    f"review validation failed with {len(errors)} error(s)"
                )
            print(render_json(consolidation), end="")
            return 0
        blind, sealed = build_blind_review_inputs(repo_root=REPO_ROOT)
        print(
            render_json(blind if args.print_artifact == "blind" else sealed),
            end="",
        )
        return 0
    except ProductDeltaGraphIncrementResultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
