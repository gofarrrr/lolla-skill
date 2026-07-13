#!/usr/bin/env python3
"""Build a provider-free three-arm V1 experiment bundle for one conversation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.canonical_model_selection import build_assessment_cards
from engine.system_b.simulated_reliability_v1 import (
    build_direct_ledger,
    build_graph_ledger,
    build_three_arm_bundle,
)

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--conversation", type=Path, required=True)
    parser.add_argument("--unresolved-mechanism", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    routing_path = ROOT / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json"
    knowledge_path = ROOT / "data/knowledge_graph.json"
    relation_path = ROOT / "data/relationship_graph.json"
    routing = load(routing_path)["mechanism_seed_models"]
    knowledge = load(knowledge_path)
    relation = load(relation_path)
    canonical_ids = set(knowledge["models"])
    cards = build_assessment_cards(knowledge["models"])

    direct = build_direct_ledger(
        unresolved_mechanism_ids=args.unresolved_mechanism,
        mechanism_seed_models=routing,
        canonical_model_ids=canonical_ids,
    )
    graph = build_graph_ledger(
        direct_ledger=direct,
        relation_graph=relation,
        canonical_model_ids=canonical_ids,
    )
    refs = [
        {"path": str(args.conversation.resolve().relative_to(ROOT)), "role": "authoritative_conversation", "sha256": sha(args.conversation)},
        {"path": str(routing_path.relative_to(ROOT)), "role": "controlled_direct_routing", "sha256": sha(routing_path)},
        {"path": str(knowledge_path.relative_to(ROOT)), "role": "canonical_model_registry", "sha256": sha(knowledge_path)},
        {"path": str(relation_path.relative_to(ROOT)), "role": "relationship_graph", "sha256": sha(relation_path)},
    ]
    bundle = build_three_arm_bundle(
        case_id=args.case_id,
        conversation=args.conversation.read_text(encoding="utf-8"),
        direct_ledger=direct,
        graph_ledger=graph,
        challenge_cards=cards,
        source_refs=refs,
    )

    output = args.output.resolve()
    write(output / "direct-ledger.json", direct)
    write(output / "graph-ledger.json", graph)
    write(output / "three-arm-bundle.json", bundle)
    summary = {
        "status": "provider_free_three_arm_bundle_pass",
        "case_id": args.case_id,
        "unresolved_mechanism_count": len(args.unresolved_mechanism),
        "direct_all_candidates": direct["all_candidate_count"],
        "direct_active_candidates": len(direct["active_candidates"]),
        "direct_reserve_candidates": len(direct["reserve_candidates"]),
        "eligible_graph_edges": graph["eligible_edge_count"],
        "graph_active_candidates": len(graph["active_candidates"]),
        "graph_reserve_candidates": len(graph["reserve_candidates"]),
        "calls_required": {
            name: arm["call_required"] for name, arm in bundle["arms"].items()
        },
        "provider_calls": 0,
        "direct_ledger_sha256": direct["ledger_sha256"],
        "graph_ledger_sha256": graph["ledger_sha256"],
        "bundle_sha256": bundle["bundle_sha256"],
    }
    write(output / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
