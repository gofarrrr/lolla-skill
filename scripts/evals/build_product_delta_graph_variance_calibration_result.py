#!/usr/bin/env python3
"""Build or validate the bounded graph-variance calibration result."""
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
    from engine.system_b.product_delta_graph_variance_calibration_result import (
        ProductDeltaGraphVarianceResultError,
        build_blind_review_inputs,
        build_review_consolidation,
        import_frozen_review,
        render_json,
        validate_checked_in_blind_review_inputs,
        validate_checked_in_review_consolidation,
        write_blind_review_inputs,
        write_review_consolidation,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Freeze or validate first-terminal generation states, blind review "
            "inputs, and non-scalar graph-variance consolidation. No provider, "
            "graph, runtime, private archive, or human-authority call is made."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--write-consolidation", action="store_true")
    action.add_argument("--validate-complete", action="store_true")
    action.add_argument(
        "--import-review",
        choices=("primary", "skeptical"),
    )
    action.add_argument(
        "--print",
        dest="print_artifact",
        choices=("blind", "sealed", "consolidation"),
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="External first-terminal JSON path used only with --import-review.",
    )
    args = parser.parse_args(argv)
    try:
        if args.import_review:
            if args.source is None:
                parser.error("--source is required with --import-review")
            import_frozen_review(
                repo_root=REPO_ROOT,
                lane=args.import_review,
                source_path=args.source,
            )
            print(f"Graph-variance {args.import_review} review frozen.")
            return 0
        if args.source is not None:
            parser.error("--source is valid only with --import-review")
        if args.write:
            write_blind_review_inputs(repo_root=REPO_ROOT)
            print("Graph-variance blind review inputs written.")
            return 0
        if args.validate_only:
            errors = validate_checked_in_blind_review_inputs(
                repo_root=REPO_ROOT
            )
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Graph-variance blind review inputs are current.")
            return 0
        if args.write_consolidation:
            write_review_consolidation(repo_root=REPO_ROOT)
            print("Graph-variance review consolidation written.")
            return 0
        if args.validate_complete:
            errors = validate_checked_in_blind_review_inputs(
                repo_root=REPO_ROOT
            )
            errors.extend(
                validate_checked_in_review_consolidation(
                    repo_root=REPO_ROOT
                )
            )
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Graph-variance calibration result is current.")
            return 0
        if args.print_artifact == "consolidation":
            payload, errors = build_review_consolidation(repo_root=REPO_ROOT)
            if errors:
                raise ProductDeltaGraphVarianceResultError(
                    f"review validation failed with {len(errors)} error(s)"
                )
            print(render_json(payload), end="")
            return 0
        blind, sealed = build_blind_review_inputs(repo_root=REPO_ROOT)
        print(
            render_json(
                blind if args.print_artifact == "blind" else sealed
            ),
            end="",
        )
        return 0
    except ProductDeltaGraphVarianceResultError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
