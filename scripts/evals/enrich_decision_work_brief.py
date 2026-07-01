#!/usr/bin/env python3
"""Create a separate enriched Decision Work Brief Markdown file."""
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
    from engine.system_b.decision_work_brief_enrichment import (
        DecisionWorkBriefEnrichmentInputError,
        enrich_decision_work_brief_from_paths,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Apply an existing conversation interpretation read to a rendered "
            "Decision Work Brief using the PR139 enrichment rules contract."
        )
    )
    parser.add_argument(
        "--brief",
        required=True,
        type=Path,
        help="Original rendered Decision Work Brief Markdown file.",
    )
    parser.add_argument(
        "--interpretation-read",
        required=True,
        type=Path,
        help="Conversation interpretation read JSON file.",
    )
    parser.add_argument(
        "--rules",
        required=True,
        type=Path,
        help="Decision Work Brief enrichment rules contract JSON file.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Separate enriched Markdown output path.",
    )
    args = parser.parse_args(argv)

    try:
        enrich_decision_work_brief_from_paths(
            brief_path=args.brief,
            interpretation_read_path=args.interpretation_read,
            rules_path=args.rules,
            output_path=args.out,
        )
    except DecisionWorkBriefEnrichmentInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
