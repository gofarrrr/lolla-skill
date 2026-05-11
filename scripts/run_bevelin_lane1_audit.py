#!/usr/bin/env python3
"""Run a deterministic Bevelin/Lane 1 audit over Lolla result artifacts."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.bevelin_lane1_audit import (  # noqa: E402
    build_bevelin_lane1_audit,
    build_collection_report,
    load_result,
    render_json,
    render_markdown,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument(
        "--result",
        type=Path,
        action="append",
        default=[],
        help="Path to a result.json file. Can be provided more than once.",
    )
    parser.add_argument(
        "--archive-root",
        type=Path,
        default=None,
        help="Archive root containing case/timestamp/result.json runs.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of archive-root result files to audit.",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    result_paths = list(args.result)
    if args.archive_root is not None:
        result_paths.extend(_archive_result_paths(args.archive_root, limit=args.limit))

    if not result_paths:
        print("ERROR: provide --result or --archive-root", file=sys.stderr)
        return 2

    audits = []
    for path in result_paths:
        if not path.exists():
            print(f"ERROR: result file not found: {path}", file=sys.stderr)
            return 1
        result = load_result(path)
        audits.append(build_bevelin_lane1_audit(result, result_path=path))

    payload = audits[0] if len(audits) == 1 else build_collection_report(audits)
    rendered = render_json(payload) if args.format == "json" else render_markdown(payload)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


def _archive_result_paths(root: Path, *, limit: int | None) -> list[Path]:
    paths = sorted(root.glob("*/*/result.json"), key=lambda path: path.parent.name, reverse=True)
    if limit is not None:
        return paths[:limit]
    return paths


if __name__ == "__main__":
    sys.exit(main())
