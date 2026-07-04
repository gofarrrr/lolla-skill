#!/usr/bin/env python3
"""Write Decision Work sidecar files to an explicit real archive directory."""
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
    from engine.system_b.decision_work_real_archive_sidecar_write import (
        DecisionWorkRealArchiveSidecarWriteError,
        build_real_archive_sidecar_write,
        render_real_archive_sidecar_write_json,
        write_real_archive_sidecar_write_receipt,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Write Decision Work sidecar files to an explicit completed-run "
            "archive directory. This is command-only operator behavior: it "
            "does not wire runtime, edit archive hooks, approve resolver refs, "
            "score advice, call models, or authorize action."
        )
    )
    parser.add_argument("--sidecar-update-packet", required=True, type=Path)
    parser.add_argument("--dry-run-result", required=True, type=Path)
    parser.add_argument("--target-archive-dir", required=True, type=Path)
    parser.add_argument(
        "--operator-confirm-real-archive-write",
        action="store_true",
        help="Required for any real archive sidecar write to occur.",
    )
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
        default="explicit_real_archive_write",
        choices=("explicit_real_archive_write",),
        help="Only explicit_real_archive_write is supported in PR219.",
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        receipt = build_real_archive_sidecar_write(
            sidecar_update_packet_path=args.sidecar_update_packet,
            dry_run_result_path=args.dry_run_result,
            target_archive_dir=args.target_archive_dir,
            operator_confirm_real_archive_write=args.operator_confirm_real_archive_write,
            source_sidecar_update_packet_ref=args.source_sidecar_update_packet_ref,
            source_dry_run_result_ref=args.source_dry_run_result_ref,
            mode=args.mode,
        )
        payload = render_real_archive_sidecar_write_json(
            receipt,
            pretty=args.pretty,
        )
        write_real_archive_sidecar_write_receipt(args.out, payload)
    except DecisionWorkRealArchiveSidecarWriteError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
