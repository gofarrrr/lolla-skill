#!/usr/bin/env python3
"""Build or validate the provider-free prospective portfolio custody sweep."""
from __future__ import annotations

import argparse
import hashlib
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


DEFAULT_OUTPUT = Path(
    "docs/evals/lolla-prospective-portfolio-custody-baseline-v1.json"
)
SOURCE_BASELINE = Path("docs/evals/lolla-graph-substrate-baseline-v1.json")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build(root: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    snapshot = PublishedKnowledgeSubstrate.open(root).require_snapshot()
    source_baseline_path = root / SOURCE_BASELINE
    source_baseline = json.loads(source_baseline_path.read_text(encoding="utf-8"))
    frozen = source_baseline["current_portfolio_characterization"]
    model_ids = sorted(snapshot.models)
    window_size = int(frozen["window_size"])
    rows: list[dict[str, Any]] = []
    total_exact_paths = 0
    total_serialized_paths = 0
    total_additional_active_paths = 0
    total_targets = 0
    disposition_counts: dict[str, int] = {}

    for expected in frozen["windows"]:
        start = int(expected["window_index"])
        window_ids = model_ids[start : start + window_size]
        custody = build_prospective_portfolio_custody(
            candidates=[{"model_id": model_id} for model_id in window_ids],
            substrate=snapshot,
        )
        accounting = custody["path_accounting"]
        if custody["status"] != "complete":
            raise ValueError(f"window {start} prospective custody is not complete")
        if custody["live_equivalence"]["live_portfolio_sha256"] != expected["portfolio_sha256"]:
            raise ValueError(f"window {start} live portfolio identity drift")
        for target in custody["enumerated_graph_targets"]:
            disposition = str(target["disposition"])
            disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
        total_exact_paths += int(accounting["exact_path_count"])
        total_serialized_paths += int(accounting["serialized_path_count"])
        total_additional_active_paths += int(
            accounting["graph_active_additional_nonadmission_path_count"]
        )
        total_targets += int(accounting["enumerated_target_count"])
        rows.append(
            {
                "window_index": start,
                "candidate_sha256": custody["candidate_sha256"],
                "live_portfolio_sha256": custody["live_equivalence"][
                    "live_portfolio_sha256"
                ],
                "expanded_seed_count": len(
                    custody["scope"]["expanded_direct_active_seed_ids"]
                ),
                "unexpanded_direct_reserve_count": custody["scope"][
                    "unexpanded_direct_reserve_count"
                ],
                "enumerated_target_count": accounting["enumerated_target_count"],
                "exact_path_count": accounting["exact_path_count"],
                "serialized_path_count": accounting["serialized_path_count"],
                "graph_active_additional_nonadmission_path_count": accounting[
                    "graph_active_additional_nonadmission_path_count"
                ],
            }
        )

    expected_lost_paths = int(
        frozen["additional_exact_paths_not_on_outer_active_item_count"]
    )
    if total_additional_active_paths != expected_lost_paths:
        raise ValueError(
            "prospective custody does not account for the frozen convergent path total"
        )
    return {
        "schema_version": "lolla.prospective_portfolio_custody_baseline.v1",
        "created_date": "2026-07-22",
        "status": "complete",
        "evidence_type": "provider_free_deterministic_corpus_sweep",
        "candidate_only": True,
        "live_connection_performed": False,
        "provider_calls": 0,
        "source_baseline": {
            "path": SOURCE_BASELINE.as_posix(),
            "sha256": _sha256(source_baseline_path),
        },
        "policy_identity": rows and build_prospective_portfolio_custody(
            candidates=[{"model_id": model_id} for model_id in model_ids[:window_size]],
            substrate=snapshot,
        )["policy_identity"],
        "substrate_release_id": snapshot.release_id,
        "scope": {
            "window_size": window_size,
            "window_count": len(rows),
            "expansion_seed_rule": "direct_active_only",
            "direction": "outgoing_authored_relations",
            "hop_depth": 1,
        },
        "aggregate": {
            "enumerated_target_count": total_targets,
            "exact_path_count": total_exact_paths,
            "serialized_path_count": total_serialized_paths,
            "omitted_path_count": total_exact_paths - total_serialized_paths,
            "graph_active_additional_nonadmission_path_count": (
                total_additional_active_paths
            ),
            "frozen_previously_unserialized_additional_path_count": expected_lost_paths,
            "previously_unserialized_paths_accounted_for": (
                total_additional_active_paths == expected_lost_paths
            ),
            "target_disposition_counts": dict(sorted(disposition_counts.items())),
            "all_windows_live_active_equivalent": True,
        },
        "windows": rows,
        "non_claims": [
            "path_accounting_is_not_relevance_proof",
            "convergent_paths_are_not_causation",
            "candidate_baseline_is_not_live_integration",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    payload = build(root)
    expected = _canonical_bytes(payload)
    if args.validate_only:
        if not output.is_file() or output.read_bytes() != expected:
            raise SystemExit("prospective portfolio custody baseline is missing or stale")
        status = "valid"
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(expected)
        status = "written"
    print(
        json.dumps(
            {
                "status": status,
                "window_count": payload["scope"]["window_count"],
                "serialized_path_count": payload["aggregate"]["serialized_path_count"],
                "previously_unserialized_paths_accounted_for": payload["aggregate"][
                    "previously_unserialized_paths_accounted_for"
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
