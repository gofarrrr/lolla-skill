#!/usr/bin/env python3
"""Build or validate the provider-free graph-review envelope repair."""
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
    from engine.system_b.product_delta_graph_review_envelope_v2 import (
        CONTRACT_RELPATH,
        ProductDeltaGraphReviewEnvelopeV2Error,
        build_artifacts,
        render_json,
        validate_checked_in_artifacts,
        write_artifacts,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build or validate the prospective Product Delta graph-review "
            "structured-output envelope, schemas, and fixtures. This command "
            "does not call Codex or a provider and does not run a semantic "
            "review."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--print-contract", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.write:
            write_artifacts(repo_root=REPO_ROOT)
            print("Graph-review envelope v2 provider-free artifacts written.")
            return 0
        if args.validate_only:
            errors = validate_checked_in_artifacts(repo_root=REPO_ROOT)
            if errors:
                for error in errors:
                    print(f"error: {error}", file=sys.stderr)
                return 1
            print(
                "Graph-review envelope v2 provider-free artifacts are current."
            )
            return 0
        payload = build_artifacts(repo_root=REPO_ROOT)[CONTRACT_RELPATH]
        print(render_json(payload), end="")
        return 0
    except ProductDeltaGraphReviewEnvelopeV2Error as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
