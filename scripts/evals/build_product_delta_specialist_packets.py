#!/usr/bin/env python3
"""Build read-only Product Delta specialist review packets."""
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


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.product_delta_specialist_packets import (
        ProductDeltaSpecialistPacketInputError,
        build_product_delta_specialist_packets,
        load_json_object,
        render_product_delta_specialist_packets_json,
        write_text,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build checked-in safe Product Delta specialist review packets "
            "from existing eval artifacts. This command does not run Lolla, "
            "call models, mutate archives, read raw transcripts, persist "
            "revised answers, score advice, create labels, or fill specialist "
            "reviews."
        )
    )
    parser.add_argument("--case-list", required=True, type=Path)
    parser.add_argument("--provisional-review", required=True, type=Path)
    parser.add_argument("--codex-batch", required=True, type=Path)
    parser.add_argument(
        "--mode",
        choices=("checked_in_safe_mode", "local_private_mode"),
        default="checked_in_safe_mode",
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    try:
        report = build_product_delta_specialist_packets(
            seed_cases=load_json_object(args.case_list),
            provisional_review=load_json_object(args.provisional_review),
            codex_batch=load_json_object(args.codex_batch),
            case_list_relpath=_repo_relative(args.case_list),
            provisional_review_relpath=_repo_relative(args.provisional_review),
            codex_batch_relpath=_repo_relative(args.codex_batch),
            mode=args.mode,
            limit=args.limit,
            case_ids=args.case_id,
        )
        rendered = render_product_delta_specialist_packets_json(report)
        if args.out:
            write_text(args.out, rendered)
        else:
            print(rendered, end="")
    except ProductDeltaSpecialistPacketInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
