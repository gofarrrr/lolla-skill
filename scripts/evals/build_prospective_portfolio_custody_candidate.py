#!/usr/bin/env python3
"""Build one candidate-only complete portfolio-custody artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.prospective_portfolio_custody import (  # noqa: E402
    build_prospective_portfolio_custody,
)
from engine.system_b.published_knowledge_substrate import (  # noqa: E402
    PublishedKnowledgeSubstrate,
)


def _candidate_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("candidate input must be a JSON array")
    rows: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, str):
            rows.append({"model_id": item})
        elif isinstance(item, dict):
            rows.append(dict(item))
        else:
            raise ValueError("candidate entries must be model ID strings or objects")
    return rows


def _bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--candidate-ids-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-serialized-paths", type=int)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    input_path = (
        args.candidate_ids_json
        if args.candidate_ids_json.is_absolute()
        else root / args.candidate_ids_json
    )
    output_path = args.output if args.output.is_absolute() else root / args.output
    snapshot = PublishedKnowledgeSubstrate.open(root).require_snapshot()
    payload = build_prospective_portfolio_custody(
        candidates=_candidate_rows(input_path),
        substrate=snapshot,
        max_serialized_paths=args.max_serialized_paths,
    )
    expected = _bytes(payload)
    if args.validate_only:
        if not output_path.is_file() or output_path.read_bytes() != expected:
            raise SystemExit("prospective custody candidate is missing or stale")
        status = "valid"
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(expected)
        status = "written"
    print(
        json.dumps(
            {
                "status": status,
                "candidate_only": True,
                "candidate_sha256": payload["candidate_sha256"],
                "exact_path_count": payload["path_accounting"]["exact_path_count"],
                "omitted_path_count": payload["path_accounting"]["omitted_path_count"],
                "live_active_equivalent": payload["live_equivalence"][
                    "active_identities_and_order_equal"
                ],
                "provider_calls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
