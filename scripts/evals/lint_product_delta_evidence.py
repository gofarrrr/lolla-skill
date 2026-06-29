#!/usr/bin/env python3
"""Lint Product Delta Evidence artifacts for boundary and non-claim drift."""
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
    from engine.system_b.product_delta_boundary_lint import (
        ProductDeltaBoundaryLintInputError,
        lint_product_delta_paths,
        render_boundary_lint_json,
        render_boundary_lint_text,
        write_text,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Deterministically lint Product Delta Evidence artifacts for "
            "boundary and non-claim drift. This command reads only supplied "
            "local files; it does not run Lolla, call models, mutate archives, "
            "score answers, or create labels."
        )
    )
    parser.add_argument("--paths", required=True, nargs="+", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on-warning", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = lint_product_delta_paths(args.paths)
        json_payload = render_boundary_lint_json(report)
        if args.json_out:
            write_text(args.json_out, json_payload)
        if args.format == "json":
            print(json_payload, end="")
        else:
            print(render_boundary_lint_text(report), end="")
    except ProductDeltaBoundaryLintInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    summary = report["summary"]
    if summary["blocking_error_count"] > 0:
        return 1
    if args.fail_on_warning and summary["warning_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
