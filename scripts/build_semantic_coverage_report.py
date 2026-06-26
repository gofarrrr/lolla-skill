#!/usr/bin/env python3
"""Build an offline semantic coverage report for one archived Lolla run."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


class InputError(ValueError):
    """Deterministic, sanitized user-facing input error."""


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.semantic_coverage_report import (
        write_semantic_coverage_report,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic local-only semantic coverage report from "
            "existing Lolla archive artifacts. This does not mutate archives."
        )
    )
    parser.add_argument("run_dir", type=Path, help="Archived run directory.")
    parser.add_argument("--out", required=True, type=Path, help="JSON report path.")
    args = parser.parse_args(argv)

    try:
        run_dir = args.run_dir.expanduser()
        if not run_dir.is_dir():
            raise InputError("run_dir is not a directory")
        _validate_output_path(args.out)
        write_semantic_coverage_report(run_dir, args.out)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: output could not be written:{type(exc).__name__}", file=sys.stderr)
        return 2
    return 0


def _validate_output_path(path: Path) -> None:
    if not path.name:
        raise InputError("out path is invalid")
    if path.exists() and path.is_dir():
        raise InputError("out path is a directory")


if __name__ == "__main__":
    raise SystemExit(main())
