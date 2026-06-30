#!/usr/bin/env python3
"""Build read-only Decision Trail specialist input packets."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _repo_relative_required(path: Path, *, label: str) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError(
            f"local_private_mode requires {label} inside repository"
        ) from exc


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_trail_specialist_packets import (
        DecisionTrailSpecialistPacketInputError,
        build_decision_trail_specialist_packets,
        load_json_object,
        render_decision_trail_specialist_packets_json,
        write_text,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build Decision Trail specialist input packets from existing "
            "fixture-review artifacts or explicit local-private run directories. "
            "This command does not run "
            "Lolla, invoke the skill, call models, mutate archives, read raw "
            "transcripts unless local_private_mode include_text is explicitly "
            "requested, fill specialist reads, execute fan-in, score advice, "
            "create labels, or authorize agent action."
        )
    )
    parser.add_argument("--fixture-review", required=True, type=Path)
    parser.add_argument("--contract-schema", required=True, type=Path)
    parser.add_argument(
        "--mode",
        choices=("checked_in_safe_mode", "local_private_mode"),
        default="checked_in_safe_mode",
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--report-id", action="append", default=[])
    parser.add_argument(
        "--local-run-dir",
        action="append",
        default=[],
        type=Path,
        help=(
            "Operator-selected completed run directory for local_private_mode. "
            "May be repeated. Absolute paths are not copied into output."
        ),
    )
    parser.add_argument(
        "--content-inclusion",
        choices=("metadata_only", "include_text"),
        default="metadata_only",
        help=(
            "local_private_mode only: metadata_only records presence/byte "
            "counts; include_text copies local private text into the output, "
            "which is unsafe for commit by default."
        ),
    )
    parser.add_argument("--max-text-chars", type=int, default=12000)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.mode == "local_private_mode" and args.out is None:
            raise DecisionTrailSpecialistPacketInputError(
                "local_private_mode requires an explicit output path"
            )
        if args.mode == "local_private_mode":
            try:
                fixture_review_ref = _repo_relative_required(
                    args.fixture_review,
                    label="fixture review",
                )
                contract_schema_ref = _repo_relative_required(
                    args.contract_schema,
                    label="contract schema",
                )
            except ValueError as exc:
                raise DecisionTrailSpecialistPacketInputError(str(exc)) from exc
        else:
            fixture_review_ref = _repo_relative(args.fixture_review)
            contract_schema_ref = _repo_relative(args.contract_schema)
        report = build_decision_trail_specialist_packets(
            fixture_review=load_json_object(args.fixture_review),
            contract_schema=load_json_object(args.contract_schema),
            fixture_review_relpath=fixture_review_ref,
            contract_schema_relpath=contract_schema_ref,
            mode=args.mode,
            limit=args.limit,
            report_ids=args.report_id,
            local_run_dirs=args.local_run_dir,
            content_inclusion_mode=args.content_inclusion,
            output_path=args.out,
            repo_root=REPO_ROOT,
            max_text_chars=args.max_text_chars,
        )
        rendered = render_decision_trail_specialist_packets_json(report)
        if args.out:
            write_text(args.out, rendered)
        else:
            print(rendered, end="")
    except DecisionTrailSpecialistPacketInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
