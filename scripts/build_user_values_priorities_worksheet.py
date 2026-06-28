#!/usr/bin/env python3
"""Build a blank user-values/priorities worksheet JSON artifact."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.user_values_priorities_worksheet import (
        InputError,
        build_blank_worksheet,
        write_blank_worksheet,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Create a blank Lolla user-values/priorities worksheet JSON file. "
            "This command does not read archives, inspect conversation content, "
            "call models, infer values, or populate review labels."
        )
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--run-id")
    parser.add_argument("--archive-relpath")
    args = parser.parse_args(argv)

    try:
        worksheet = build_blank_worksheet(
            case_id=args.case_id,
            run_id=args.run_id,
            archive_relpath=args.archive_relpath,
        )
        write_blank_worksheet(args.out, worksheet)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
