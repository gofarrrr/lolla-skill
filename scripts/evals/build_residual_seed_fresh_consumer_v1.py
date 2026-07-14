#!/usr/bin/env python3
"""Build the corrected Case01 residual-seed fresh-consumer handoff locally."""

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
from engine.system_b.residual_seed_fresh_consumer_v1 import (
    build_residual_seed_fresh_consumer_bundle_v1,
)
from engine.system_b.residual_seed_graph_recall_v1 import (
    build_residual_seed_graph_recall_v1,
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    conversation_path = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case01-flood-infrastructure.txt"
    result_path = ROOT / "research/residual-challenge-seed-case01-probe-2026-07-13/t1/result.json"
    routing_path = ROOT / "docs/conversation-understanding/residual-challenge-seed-graph-routing-v1.json"
    knowledge_path = ROOT / "data/knowledge_graph.json"
    relation_path = ROOT / "data/relationship_graph.json"

    seed_result = load(result_path)
    seed_portfolio = seed_result["joined_seed_portfolio"]
    knowledge = load(knowledge_path)
    recall = build_residual_seed_graph_recall_v1(
        seed_portfolio=seed_portfolio,
        routing_contract=load(routing_path),
        knowledge_graph=knowledge,
        relationship_graph=load(relation_path),
    )
    refs = [
        {"path": str(conversation_path.relative_to(ROOT)), "role": "authoritative_conversation", "sha256": sha(conversation_path)},
        {"path": str(result_path.relative_to(ROOT)), "role": "residual_seed_and_coverage_receipt", "sha256": sha(result_path)},
        {"path": str(routing_path.relative_to(ROOT)), "role": "deterministic_residual_seed_routing", "sha256": sha(routing_path)},
        {"path": str(knowledge_path.relative_to(ROOT)), "role": "canonical_model_registry", "sha256": sha(knowledge_path)},
        {"path": str(relation_path.relative_to(ROOT)), "role": "relationship_graph", "sha256": sha(relation_path)},
    ]
    bundle = build_residual_seed_fresh_consumer_bundle_v1(
        case_id=seed_result["case_id"],
        conversation=conversation_path.read_text(encoding="utf-8"),
        seed_portfolio=seed_portfolio,
        recall=recall,
        challenge_cards=build_assessment_cards(knowledge["models"]),
        source_refs=refs,
    )
    output = args.output.resolve()
    write(output / "recall.json", recall)
    write(output / "bundle.json", bundle)
    summary = {
        "schema_version": "lolla.residual_seed_fresh_consumer_build_summary.v1",
        "status": bundle["status"],
        "case_id": bundle["case_id"],
        "active_candidate_ids": [
            item["model_id"] for item in bundle["packet"]["pressure_portfolio"]
        ],
        "active_candidate_count": bundle["packet"]["portfolio_structure"]["active_candidate_count"],
        "direct_reserve_count": bundle["packet"]["portfolio_structure"]["direct_reserve_count"],
        "graph_reserve_count": bundle["packet"]["portfolio_structure"]["graph_reserve_count"],
        "user_prompt_utf8_bytes": len(bundle["prompts"]["user_prompt"].encode("utf-8")),
        "response_schema_utf8_bytes": len(json.dumps(bundle["response_schema"], separators=(",", ":")).encode("utf-8")),
        "provider_calls": 0,
        "next_call_authorized": False,
        "maximum_future_calls_if_separately_authorized": 1,
        "maximum_future_provider_reported_cost_usd": 0.01,
        "bundle_sha256": bundle["bundle_sha256"],
    }
    write(output / "summary.json", summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
