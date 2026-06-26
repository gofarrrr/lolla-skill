#!/usr/bin/env python3
"""Export archived Lolla runs into an extraction-adequacy corpus."""
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
    from engine.system_b.extraction_adequacy_corpus import (
        DEFAULT_ARCHIVE_ROOT,
        build_extraction_adequacy_corpus_manifest,
        build_extraction_adequacy_corpus_records,
        write_json,
        write_jsonl,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a local JSONL survey of extraction/provenance adequacy from "
            "archived Lolla runs. The export is read-only, does not score "
            "answer quality, and does not call models."
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
        help="Write one compact extraction-adequacy corpus record per run as JSONL.",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        help="Write deterministic aggregate manifest JSON.",
    )
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Print only the manifest JSON to stdout.",
    )
    args = parser.parse_args(argv)

    archive_root = Path(args.archive_root).expanduser()
    records = build_extraction_adequacy_corpus_records(archive_root)
    manifest = build_extraction_adequacy_corpus_manifest(archive_root, records)

    if args.out:
        write_jsonl(records, args.out)
    if args.manifest_out:
        write_json(manifest, args.manifest_out)

    if args.manifest_only or not args.out:
        print(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        print(
            f"exported {len(records)} extraction adequacy records to {args.out}"
            + (f" and manifest to {args.manifest_out}" if args.manifest_out else "")
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
