#!/usr/bin/env python3
"""Capture an Observatory workspace human review as deterministic intake JSON."""
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
    from engine.system_b.observatory_workspace_human_review_intake import (
        ObservatoryWorkspaceHumanReviewIntakeError,
        load_observatory_workspace_human_review_form,
        validate_observatory_workspace_human_review_form,
        write_observatory_workspace_human_review_intake_result,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Capture a filled Observatory workspace human review form as a "
            "sanitized intake result. This command validates and records review "
            "shape only; it does not run Lolla, invoke the skill, call models, "
            "wire runtime, write sidecars, claim human validation, claim product "
            "proof, score answer quality, or authorize action."
        )
    )
    parser.add_argument(
        "--review",
        required=True,
        type=Path,
        help="Filled Observatory workspace human review JSON form.",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output sanitized intake result JSON path.",
    )
    parser.add_argument(
        "--source-ref",
        help=(
            "Optional non-private source reference to record. Defaults to the "
            "review filename only, not the local path."
        ),
    )
    parser.add_argument(
        "--created-at",
        help="Optional ISO timestamp for deterministic tests or operator receipts.",
    )
    args = parser.parse_args(argv)

    source_ref = args.source_ref or args.review.name

    try:
        form = load_observatory_workspace_human_review_form(args.review)
        intake = validate_observatory_workspace_human_review_form(
            form,
            source_ref=source_ref,
            created_at=args.created_at,
        )
        write_observatory_workspace_human_review_intake_result(args.out, intake)
    except ObservatoryWorkspaceHumanReviewIntakeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError:
        print("error: intake result could not be written", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
