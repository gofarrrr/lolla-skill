#!/usr/bin/env python3
"""Aggregate fixed per-case core-semantic comparisons."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from engine.system_b.core_semantic_corpus_comparison import (
        build_core_semantic_corpus_comparison,
        render_core_semantic_corpus_comparison_json,
        render_core_semantic_corpus_comparison_markdown,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--comparison", required=True, action="append", type=Path)
    parser.add_argument("--artifact-dir", required=True, action="append", type=Path)
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--md-out", required=True, type=Path)
    args = parser.parse_args()

    payload = build_core_semantic_corpus_comparison(
        manifest_path=args.manifest,
        comparison_paths=args.comparison,
        artifact_dirs=args.artifact_dir,
        repo_root=REPO_ROOT,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        render_core_semantic_corpus_comparison_json(payload), encoding="utf-8"
    )
    args.md_out.write_text(
        render_core_semantic_corpus_comparison_markdown(payload), encoding="utf-8"
    )
    print(f"Corpus comparison JSON written to {args.json_out}")
    print(f"Corpus comparison Markdown written to {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
