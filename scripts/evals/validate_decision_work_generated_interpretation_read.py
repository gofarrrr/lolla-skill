#!/usr/bin/env python3
"""Validate a generated Decision Work interpretation read for intake."""
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
    from engine.system_b.decision_work_generated_interpretation_read_intake import (
        DecisionWorkGeneratedInterpretationReadIntakeError,
        INTAKE_MODES,
        render_generated_interpretation_read_intake_json,
        validate_generated_interpretation_read,
        write_generated_interpretation_read_intake_result,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Validate an externally supplied Decision Work interpretation read. "
            "This command writes an intake result for accepted, rejected, or "
            "repair-required reads; it does not run Lolla, call models, generate "
            "reads, render briefs, create triage, update resolver refs, update "
            "runtime sidecars, score advice, or authorize action."
        )
    )
    parser.add_argument(
        "--read",
        required=True,
        type=Path,
        help="Candidate interpretation read JSON to validate.",
    )
    parser.add_argument(
        "--queue-item",
        type=Path,
        help="Optional PR180 offline interpretation queue item JSON.",
    )
    parser.add_argument(
        "--prompt-packet",
        type=Path,
        help="Optional PR181 operator/Codex prompt packet JSON.",
    )
    parser.add_argument(
        "--mode",
        choices=INTAKE_MODES,
        default="checked_in_safe",
    )
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output intake result JSON path.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = validate_generated_interpretation_read(
            read_path=args.read,
            queue_item_path=args.queue_item,
            prompt_packet_path=args.prompt_packet,
            mode=args.mode,
        )
        payload = render_generated_interpretation_read_intake_json(
            result,
            pretty=args.pretty,
        )
        write_generated_interpretation_read_intake_result(args.out, payload)
    except DecisionWorkGeneratedInterpretationReadIntakeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
