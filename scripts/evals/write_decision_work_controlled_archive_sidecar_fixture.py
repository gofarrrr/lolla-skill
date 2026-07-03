#!/usr/bin/env python3
"""Write Decision Work sidecar files to a controlled archive-shaped fixture."""
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
    from engine.system_b.decision_work_controlled_archive_sidecar_write_fixture import (
        DecisionWorkControlledArchiveSidecarWriteFixtureError,
        build_controlled_archive_sidecar_write_fixture,
        render_controlled_archive_sidecar_write_fixture_json,
        write_controlled_archive_sidecar_write_fixture_receipt,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Write Decision Work sidecar-shaped files to a controlled "
            "synthetic archive-like fixture directory only. This command does "
            "not write real archives, mutate historical archives, wire "
            "runtime, approve resolver refs, score advice, or authorize action."
        )
    )
    parser.add_argument("--sidecar-update-packet", required=True, type=Path)
    parser.add_argument("--dry-run-result", required=True, type=Path)
    parser.add_argument("--fixture-archive-dir", required=True, type=Path)
    parser.add_argument(
        "--source-sidecar-update-packet-ref",
        help="Optional stable source ref to record instead of deriving one.",
    )
    parser.add_argument(
        "--source-dry-run-result-ref",
        help="Optional stable dry-run result ref to record instead of deriving one.",
    )
    parser.add_argument(
        "--mode",
        default="controlled_archive_fixture_write",
        choices=("controlled_archive_fixture_write",),
        help="Only controlled_archive_fixture_write is supported in PR214.",
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        receipt = build_controlled_archive_sidecar_write_fixture(
            sidecar_update_packet_path=args.sidecar_update_packet,
            dry_run_result_path=args.dry_run_result,
            fixture_archive_dir=args.fixture_archive_dir,
            source_sidecar_update_packet_ref=args.source_sidecar_update_packet_ref,
            source_dry_run_result_ref=args.source_dry_run_result_ref,
            mode=args.mode,
        )
        payload = render_controlled_archive_sidecar_write_fixture_json(
            receipt,
            pretty=args.pretty,
        )
        write_controlled_archive_sidecar_write_fixture_receipt(args.out, payload)
    except DecisionWorkControlledArchiveSidecarWriteFixtureError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
