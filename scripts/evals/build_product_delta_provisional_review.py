#!/usr/bin/env python3
"""Build read-only Product Delta Evidence readiness and shell output."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def _repo_relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return None


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.product_delta_readiness import (
        ProductDeltaReadinessInputError,
        build_product_delta_readiness_report,
        load_review_json,
        load_seed_cases,
        render_product_delta_readiness_json,
        render_product_delta_readiness_markdown,
        write_text,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a read-only Product Delta Evidence readiness report and "
            "PR72-shaped provisional review shells from existing safe case "
            "metadata. This command does not run Lolla, call models, mutate "
            "archives, read raw transcript/memo/revised-answer content, score "
            "answers, or create human labels."
        )
    )
    parser.add_argument("--case-list", required=True, type=Path)
    parser.add_argument("--archive-root", type=Path)
    parser.add_argument("--review-json", type=Path)
    parser.add_argument("--out", type=Path, help="Markdown report output path.")
    parser.add_argument("--json-out", type=Path, help="JSON report output path.")
    args = parser.parse_args(argv)

    try:
        seed_cases = load_seed_cases(args.case_list)
        review_json = load_review_json(args.review_json)
        report = build_product_delta_readiness_report(
            seed_cases=seed_cases,
            archive_root=args.archive_root,
            review_json=review_json,
            review_json_relpath=_repo_relative(args.review_json),
        )
        json_payload = render_product_delta_readiness_json(report)
        if args.out:
            write_text(args.out, render_product_delta_readiness_markdown(report))
        if args.json_out:
            write_text(args.json_out, json_payload)
        if not args.out and not args.json_out:
            print(json_payload, end="")
    except ProductDeltaReadinessInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
