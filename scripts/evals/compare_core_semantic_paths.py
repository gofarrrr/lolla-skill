#!/usr/bin/env python3
"""Compare repeated compact and core semantic shadow outputs."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    from engine.system_b.core_semantic_comparison import (
        build_core_semantic_comparison,
        render_core_semantic_comparison_json,
        render_core_semantic_comparison_markdown,
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="append", required=True, type=Path)
    parser.add_argument("--shadow", action="append", required=True, type=Path)
    parser.add_argument("--conversation", required=True, type=Path)
    parser.add_argument("--gold", required=True, type=Path)
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--md-out", required=True, type=Path)
    args = parser.parse_args()

    payload = build_core_semantic_comparison(
        compact_paths=args.compact,
        shadow_paths=args.shadow,
        conversation_path=args.conversation,
        gold_path=args.gold,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(render_core_semantic_comparison_json(payload), encoding="utf-8")
    args.md_out.write_text(render_core_semantic_comparison_markdown(payload), encoding="utf-8")
    print(f"Comparison JSON written to {args.json_out}")
    print(f"Comparison Markdown written to {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
