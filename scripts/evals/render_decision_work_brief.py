#!/usr/bin/env python3
"""Render a Decision Work Brief JSON artifact to Markdown."""
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
    from engine.system_b.decision_work_brief_renderer import (
        DecisionWorkBriefRendererInputError,
        extract_brief_from_pilot_review,
        load_json_object,
        render_decision_work_brief_markdown,
        write_decision_work_brief_markdown,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Render a lolla.decision_work_brief.v0 JSON artifact as Markdown "
            "without generating or inferring semantic content."
        )
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--brief",
        type=Path,
        help="Decision Work Brief JSON file to render.",
    )
    source_group.add_argument(
        "--pilot-review",
        type=Path,
        help="PR116 pilot review JSON containing an embedded brief.",
    )
    parser.add_argument(
        "--brief-index",
        type=int,
        default=0,
        help="Embedded draft brief index to render when --pilot-review is used.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output Markdown path.",
    )
    args = parser.parse_args(argv)

    try:
        if args.brief is not None:
            brief = load_json_object(args.brief)
        else:
            pilot_review = load_json_object(args.pilot_review)
            brief = extract_brief_from_pilot_review(
                pilot_review=pilot_review,
                brief_index=args.brief_index,
            )
        markdown = render_decision_work_brief_markdown(brief=brief)
        write_decision_work_brief_markdown(args.out, markdown)
    except DecisionWorkBriefRendererInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
