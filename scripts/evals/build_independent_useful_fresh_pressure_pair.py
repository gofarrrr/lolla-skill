#!/usr/bin/env python3
"""Build the independent retailer control/pressure pair without provider calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.canonical_model_selection import build_assessment_cards
from engine.system_b.fresh_reasoning_pressure import (
    build_control_packet,
    build_control_prompts,
    build_packet,
    build_prompts,
    control_response_schema,
    response_schema,
)
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes


CONVERSATION = ROOT / "research/independent-phase5-cases-2026-07-12/useful-pressure-case.txt"
MECHANISM_RESULT = ROOT / "research/independent-useful-mechanism-probe-2026-07-12/result.json"
ROUTING = ROOT / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json"
GRAPH = ROOT / "data/knowledge_graph.json"
TASK_ID = "independent_useful_provider"
CASE_ID = "phase5-independent-useful-retailer-pilot"


class IndependentUsefulPairError(ValueError):
    """Raised when preserved evidence cannot produce the frozen pair."""


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise IndependentUsefulPairError(f"expected JSON object: {path}")
    return value


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def report_path(path: Path) -> str:
    """Use repository-relative custody paths when possible, absolute paths in tests."""
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def build_portfolio(
    mechanism_result: dict[str, Any],
    routing: dict[str, Any],
    graph: dict[str, Any],
) -> dict[str, Any]:
    calls = [call for call in mechanism_result.get("calls", []) if call.get("task_id") == TASK_ID]
    if len(calls) != 1:
        raise IndependentUsefulPairError("provider mechanism arm is not unique")
    call = calls[0]
    if call.get("operational_status") != "ok" or not call.get("compiled"):
        raise IndependentUsefulPairError("provider mechanism arm is not operational")
    projection = call["compiled"].get("routing_projection", {})
    if projection.get("contains_case_context") is not False:
        raise IndependentUsefulPairError("routing projection contains case context")
    nodes = projection.get("pattern_nodes")
    if not isinstance(nodes, list) or not nodes:
        raise IndependentUsefulPairError("provider projection has no mechanisms")
    mechanisms = sorted({str(node.get("mechanism_id") or "") for node in nodes})
    if "" in mechanisms or len(mechanisms) != len(nodes):
        raise IndependentUsefulPairError("mechanism identities are empty or duplicated")

    policy = routing.get("selection_policy", {})
    if policy.get("operation") != "deterministic_union_of_declared_seed_models":
        raise IndependentUsefulPairError("routing policy is not deterministic union")
    seeds = routing.get("mechanism_seed_models", {})
    model_sources: dict[str, list[str]] = {}
    for mechanism_id in mechanisms:
        model_ids = seeds.get(mechanism_id)
        if not isinstance(model_ids, list) or not model_ids:
            raise IndependentUsefulPairError(f"mechanism has no declared seeds: {mechanism_id}")
        for model_id in model_ids:
            if model_id not in graph.get("models", {}):
                raise IndependentUsefulPairError(f"seed is not canonical: {model_id}")
            model_sources.setdefault(str(model_id), []).append(mechanism_id)
    if not model_sources or len(model_sources) > 10:
        raise IndependentUsefulPairError("candidate portfolio is outside the 1..10 bound")

    evaluation = mechanism_result.get("evaluation", {})
    gates = evaluation.get("gates", {})
    if gates.get("protected_source_provider") is not True or gates.get("protected_removed_ablation") is not True:
        raise IndependentUsefulPairError("protected causal mechanism gates did not pass")

    return {
        "schema_version": "lolla.independent_useful_pressure_portfolio.v1",
        "case_id": CASE_ID,
        "source_task_id": TASK_ID,
        "source_routing_projection_sha256": sha256_bytes(canonical_json_bytes(projection)),
        "unresolved_mechanism_ids": mechanisms,
        "candidate_count": len(model_sources),
        "candidates": [
            {
                "model_id": model_id,
                "recalled_by_mechanism_ids": sorted(source_mechanisms),
                "disposition": "unreviewed_pressure_hypothesis",
            }
            for model_id, source_mechanisms in sorted(model_sources.items())
        ],
        "candidate_deletion_performed": False,
        "semantic_applicability_certified": False,
        "fact_free_routing_projection": True,
        "graph_runtime_modified": False,
        "non_claims": [
            "graph_recall_is_not_relevance",
            "failed_secondary_invariance_gate_is_preserved",
            "not_runtime_authorization",
        ],
    }


def build(output: Path) -> dict[str, Any]:
    mechanism_result = load(MECHANISM_RESULT)
    routing = load(ROUTING)
    graph = load(GRAPH)
    portfolio = build_portfolio(mechanism_result, routing, graph)
    cards = build_assessment_cards(graph["models"])
    sources = [CONVERSATION, MECHANISM_RESULT, ROUTING, GRAPH]
    refs = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in sources]
    conversation = CONVERSATION.read_text(encoding="utf-8")
    pressure = build_packet(
        case_id=CASE_ID,
        conversation=conversation,
        portfolio=portfolio,
        challenge_cards=cards,
        source_refs=refs,
    )
    control = build_control_packet(
        case_id=CASE_ID,
        conversation=conversation,
        source_refs=[refs[0]],
    )
    pressure_prompts = build_prompts(pressure)
    control_prompts = build_control_prompts(control)
    candidate_ids = [row["model_id"] for row in pressure["pressure_portfolio"]]

    portfolio_path = output / "portfolio.json"
    pressure_path = output / "pressure-packet.json"
    control_path = output / "control-packet.json"
    write(portfolio_path, portfolio)
    write(pressure_path, pressure)
    write(control_path, control)
    report = {
        "schema_version": "lolla.independent_useful_fresh_pressure_pair_report.v1",
        "status": "provider_free_independent_useful_pair_pass",
        "case_id": CASE_ID,
        "portfolio": {
            "path": report_path(portfolio_path),
            "sha256": sha(portfolio_path),
            "unresolved_mechanism_ids": portfolio["unresolved_mechanism_ids"],
            "candidate_count": portfolio["candidate_count"],
            "candidate_ids": candidate_ids,
            "candidate_deletion_performed": False,
            "semantic_applicability_certified": False,
        },
        "arms": {
            "control": {
                "packet_path": report_path(control_path),
                "packet_sha256": sha(control_path),
                "system_prompt_sha256": control_prompts["system_prompt_sha256"],
                "user_prompt_sha256": control_prompts["user_prompt_sha256"],
                "user_prompt_utf8_bytes": len(control_prompts["user_prompt"].encode()),
                "response_schema_sha256": sha256_bytes(canonical_json_bytes(control_response_schema())),
                "response_schema_metrics": schema_metrics(control_response_schema()),
            },
            "pressure": {
                "packet_path": report_path(pressure_path),
                "packet_sha256": sha(pressure_path),
                "system_prompt_sha256": pressure_prompts["system_prompt_sha256"],
                "user_prompt_sha256": pressure_prompts["user_prompt_sha256"],
                "user_prompt_utf8_bytes": len(pressure_prompts["user_prompt"].encode()),
                "response_schema_sha256": sha256_bytes(canonical_json_bytes(response_schema(candidate_ids))),
                "response_schema_metrics": schema_metrics(response_schema(candidate_ids)),
            },
        },
        "maximum_provider_calls": 2,
        "provider_calls": 0,
        "mechanism_probe_context": {
            "frozen_status": mechanism_result["evaluation"]["status"],
            "protected_source_provider": True,
            "protected_removed_ablation": True,
            "broad_mechanism_invariance_claimed": False,
        },
        "boundary": {
            "same_authoritative_conversation": True,
            "fresh_context_both_arms": True,
            "control_has_no_graph_candidates": True,
            "pressure_preserves_all_candidates": True,
            "fact_free_deterministic_routing": True,
            "runtime_effect": "none",
        },
    }
    write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(
        json.dumps(
            {
                "status": report["status"],
                "mechanism_count": len(report["portfolio"]["unresolved_mechanism_ids"]),
                "candidate_count": report["portfolio"]["candidate_count"],
                "candidate_ids": report["portfolio"]["candidate_ids"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
