#!/usr/bin/env python3
"""Export archived Lolla reasoning traces into a local eval dataset."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.reasoning_trace_dataset import (
        DEFAULT_ARCHIVE_ROOT,
        build_dataset_records,
        summarize_dataset_records,
        write_json,
        write_jsonl,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a local JSONL reasoning-trace dataset and aggregate summary "
            "from archived Lolla runs."
        )
    )
    parser.add_argument(
        "archive_root",
        nargs="?",
        default=str(DEFAULT_ARCHIVE_ROOT),
        help="Archive root to scan. Defaults to ~/.local/share/lolla/runs.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Write flattened dataset records as JSONL.",
    )
    parser.add_argument(
        "--summary-out",
        type=Path,
        help="Write aggregate summary JSON.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the summary JSON to stdout.",
    )
    args = parser.parse_args(argv)

    archive_root = Path(args.archive_root).expanduser()
    records = build_dataset_records(archive_root)
    summary = summarize_dataset_records(records)

    if args.out:
        write_jsonl(records, args.out)
    if args.summary_out:
        write_json(summary, args.summary_out)

    if args.summary_only or not args.out:
        print(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(
            "exported "
            f"{len(records)} traces to {args.out}"
            + (f" and summary to {args.summary_out}" if args.summary_out else "")
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
