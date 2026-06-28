#!/usr/bin/env python3
"""Analyze review-corpus manifest readiness for high-stakes evidence."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.review_corpus_evidence_readiness import (
        InputError,
        build_evidence_readiness,
        load_manifest,
        render_evidence_readiness_json,
        render_evidence_readiness_markdown,
        write_text,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Read a Lolla review-corpus manifest and report whether it contains "
            "high-stakes reliance-present archive evidence. This command reads "
            "only manifest JSON and does not inspect archives or call models."
        )
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="Markdown report output path.")
    parser.add_argument("--json-out", type=Path, help="JSON report output path.")
    args = parser.parse_args(argv)

    try:
        manifest = load_manifest(args.manifest)
        readiness = build_evidence_readiness(manifest)
        json_payload = render_evidence_readiness_json(readiness)
        if args.out:
            write_text(args.out, render_evidence_readiness_markdown(readiness))
        if args.json_out:
            write_text(args.json_out, json_payload)
        if not args.out and not args.json_out:
            print(json_payload, end="")
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
