#!/usr/bin/env python3
"""Build or validate the provider-free V3 nonclaim-custody repair."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.product_delta_graph_review_nonclaim_custody_v3 import (  # noqa: E402
    CONTRACT_RELPATH,
    build_artifacts,
    validate_checked_in_artifacts,
    write_artifacts,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the provider-free V3 graph-review nonclaim-custody "
            "contract. This command never invokes Codex or a provider."
        )
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate-only", action="store_true")
    action.add_argument("--print-contract", action="store_true")
    args = parser.parse_args(argv)

    if args.write:
        write_artifacts(repo_root=REPO_ROOT)
        print("V3 nonclaim-custody artifacts written.")
        return 0
    if args.print_contract:
        payload = build_artifacts(repo_root=REPO_ROOT)[CONTRACT_RELPATH]
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    errors = validate_checked_in_artifacts(repo_root=REPO_ROOT)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("V3 nonclaim-custody artifacts are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
