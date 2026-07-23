#!/usr/bin/env python3
"""Validate and consolidate frozen fresh-agent paired-screen reviews."""
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
    from engine.system_b.product_delta_paired_screen_review import (
        ProductDeltaPairedScreenReviewError,
        build_review_consolidation,
        render_json,
        validate_checked_in_consolidation,
        write_checked_in_consolidation,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Validate frozen fresh-agent Product Delta reviews and build a "
            "non-voting lineage fan-in. No provider, graph, runtime, or private "
            "archive call is made."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--write", action="store_true")
    action.add_argument("--print", dest="print_output", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.validate_only:
            errors = validate_checked_in_consolidation(repo_root=REPO_ROOT)
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Product Delta paired-screen reviews and consolidation are valid.")
            return 0
        if args.write:
            write_checked_in_consolidation(repo_root=REPO_ROOT)
            print("Product Delta paired-screen consolidation written.")
            return 0
        consolidation, errors = build_review_consolidation(repo_root=REPO_ROOT)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        print(render_json(consolidation), end="")
        return 0
    except ProductDeltaPairedScreenReviewError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
