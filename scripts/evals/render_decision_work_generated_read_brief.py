#!/usr/bin/env python3
"""Render a PR186 generated-read brief supply packet to Markdown."""
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
    from engine.system_b.decision_work_generated_read_brief_renderer import (
        DecisionWorkGeneratedReadBriefRendererError,
        load_generated_read_brief_supply,
        render_generated_read_brief_markdown,
        write_generated_read_brief_markdown,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Render a PR186 generated-read brief supply packet to Markdown. "
            "This command formats supplied fields only; it does not generate "
            "semantic interpretation, enrich briefs, create triage, update "
            "sidecars, score advice, claim proof, or authorize action."
        )
    )
    parser.add_argument(
        "--supply",
        required=True,
        type=Path,
        help="PR186 generated-read brief supply JSON packet.",
    )
    parser.add_argument(
        "--case-id",
        default="launch-public-enterprise-beta",
        help="Case id to print in the rendered brief.",
    )
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    try:
        supply = load_generated_read_brief_supply(args.supply)
        markdown = render_generated_read_brief_markdown(
            supply=supply,
            case_id=args.case_id,
        )
        write_generated_read_brief_markdown(args.out, markdown)
    except DecisionWorkGeneratedReadBriefRendererError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
