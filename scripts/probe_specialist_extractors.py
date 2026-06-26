#!/usr/bin/env python3
"""Run the fake-boundary specialist extractor probe for one archived run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


class InputError(ValueError):
    """Deterministic, sanitized user-facing input error."""


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.specialist_extractor_probe import (
        SPECIALISTS,
        validate_probe_output_path,
        write_specialist_extractor_probe,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Run a local fake-boundary specialist extractor probe. "
            "This does not call models, mutate archives, or change runtime behavior."
        )
    )
    parser.add_argument("run_dir", type=Path, help="Archived run directory.")
    parser.add_argument(
        "--fake-boundary",
        required=True,
        type=Path,
        help="JSON fixture with canned live_constraints, stance_events, and/or dropped_threads.",
    )
    parser.add_argument("--out", required=True, type=Path, help="JSON probe output path.")
    parser.add_argument(
        "--specialist",
        action="append",
        choices=SPECIALISTS,
        default=[],
        help="Specialist to run. Repeatable. Defaults to all when omitted.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all supported specialists.",
    )
    args = parser.parse_args(argv)

    try:
        run_dir = args.run_dir.expanduser()
        if not run_dir.is_dir():
            raise InputError("run_dir is not a directory")
        _validate_output_path(run_dir, args.out, validate_probe_output_path)
        fake_boundary = _load_json_object(args.fake_boundary, "fake-boundary")
        specialists = list(SPECIALISTS) if args.all or not args.specialist else args.specialist
        write_specialist_extractor_probe(
            run_dir,
            args.out,
            fake_boundary_payload=fake_boundary,
            specialists=specialists,
        )
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"error: {type(exc).__name__}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: output could not be written:{type(exc).__name__}", file=sys.stderr)
        return 2
    return 0


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError(f"{label} is not valid JSON") from exc
    except OSError as exc:
        raise InputError(f"{label} could not be read:{type(exc).__name__}") from exc
    if not isinstance(payload, dict):
        raise InputError(f"{label} is not a JSON object")
    return payload


def _validate_output_path(run_dir: Path, path: Path, validator: Any) -> None:
    try:
        validator(run_dir, path)
    except ValueError as exc:
        raise InputError(str(exc) or "out path is invalid") from exc


if __name__ == "__main__":
    raise SystemExit(main())
