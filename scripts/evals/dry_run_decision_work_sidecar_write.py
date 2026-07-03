#!/usr/bin/env python3
"""Run a deterministic Decision Work sidecar write dry-run."""
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
    from engine.system_b.decision_work_sidecar_write_dry_run import (
        DecisionWorkSidecarWriteDryRunError,
        build_sidecar_write_dry_run,
        render_sidecar_write_dry_run_json,
        write_sidecar_write_dry_run_result,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Dry-run a future Decision Work sidecar write from a proposed "
            "sidecar update packet. This command does not write archive "
            "sidecars, mutate archives, approve resolver refs, wire runtime, "
            "score advice, or authorize action."
        )
    )
    parser.add_argument("--sidecar-update-packet", required=True, type=Path)
    parser.add_argument(
        "--source-sidecar-update-packet-ref",
        help="Optional stable source ref to record instead of deriving one.",
    )
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--preview-dir",
        type=Path,
        help=(
            "Optional explicit directory for dry-run preview files. Must not "
            "target an archive or decision_work sidecar path."
        ),
    )
    parser.add_argument(
        "--mode",
        default="dry_run_only",
        choices=("dry_run_only",),
        help="Only dry_run_only is supported in PR206.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        result = build_sidecar_write_dry_run(
            sidecar_update_packet_path=args.sidecar_update_packet,
            source_sidecar_update_packet_ref=args.source_sidecar_update_packet_ref,
            preview_dir=args.preview_dir,
            write_preview=args.preview_dir is not None,
        )
        payload = render_sidecar_write_dry_run_json(result, pretty=args.pretty)
        write_sidecar_write_dry_run_result(args.out, payload)
    except DecisionWorkSidecarWriteDryRunError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
