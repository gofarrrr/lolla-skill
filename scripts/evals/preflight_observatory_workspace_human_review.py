#!/usr/bin/env python3
"""Run a read-only Observatory workspace human-review launch preflight."""
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
    from engine.system_b.observatory_workspace_human_review_preflight import (
        DEFAULT_INTAKE_PATH,
        DEFAULT_PORT,
        DEFAULT_REVIEW_PATH,
        ObservatoryWorkspaceHumanReviewPreflightError,
        build_observatory_workspace_human_review_preflight,
        render_observatory_workspace_human_review_preflight_json,
        write_observatory_workspace_human_review_preflight_json,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Check whether an existing completed result JSON and case id are "
            "ready for Observatory workspace human review. This command is "
            "read-only except for an optional safe report file; it does not "
            "launch Observatory, run Lolla, invoke the skill, call models, "
            "create runs, write sidecars, capture human review, wire runtime, "
            "claim validation, claim proof, score correctness, or authorize "
            "action."
        )
    )
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--intake", type=Path, default=DEFAULT_INTAKE_PATH)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        payload = build_observatory_workspace_human_review_preflight(
            result_path=args.result,
            case_id=args.case_id,
            port=args.port,
            review_path=args.review,
            intake_path=args.intake,
        )
    except ObservatoryWorkspaceHumanReviewPreflightError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.out:
        write_observatory_workspace_human_review_preflight_json(
            args.out,
            payload,
            pretty=args.pretty,
        )
    else:
        print(
            render_observatory_workspace_human_review_preflight_json(
                payload,
                pretty=args.pretty,
            ),
            end="",
        )

    return 0 if payload["ready_to_launch_review"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
