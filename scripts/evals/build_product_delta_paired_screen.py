#!/usr/bin/env python3
"""Build or validate the provider-free Product Delta paired-screen corpus."""
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
    from engine.system_b.product_delta_paired_screen import (
        ProductDeltaPairedScreenInputError,
        build_product_delta_paired_screen,
        render_json,
        validate_checked_in_screen,
        write_checked_in_screen,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build or validate a checked-in, freshly blinded Product Delta "
            "paired-screen corpus from existing public repository artifacts. "
            "This command makes no provider, graph, runtime, or private-archive call."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--write", action="store_true")
    action.add_argument(
        "--print",
        dest="print_artifact",
        choices=("blind", "sealed"),
    )
    args = parser.parse_args(argv)

    try:
        if args.validate_only:
            errors = validate_checked_in_screen(repo_root=REPO_ROOT)
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print("Product Delta paired-screen artifacts are current.")
            return 0
        if args.write:
            write_checked_in_screen(repo_root=REPO_ROOT)
            print("Product Delta paired-screen artifacts written.")
            return 0
        blind, sealed = build_product_delta_paired_screen(repo_root=REPO_ROOT)
        print(
            render_json(blind if args.print_artifact == "blind" else sealed),
            end="",
        )
        return 0
    except ProductDeltaPairedScreenInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
