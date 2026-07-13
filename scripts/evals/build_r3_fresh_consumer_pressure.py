#!/usr/bin/env python3
"""Build the provider-free frozen Case 01 R3 pressure bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.constitutional_graph_survival import (  # noqa: E402
    build_constitutional_graph_survival,
)
from engine.system_b.r3_fresh_consumer import (  # noqa: E402
    build_pressure_bundle,
    canonical,
    estimated_tokens,
)
from engine.system_b.residual_seed_graph_recall_v1 import (  # noqa: E402
    build_residual_seed_graph_recall_v1,
)


CASE_ID = "v1-case01-flood-infrastructure"
CONVERSATION = Path(
    "research/simulated-reliability-corpus-v1-2026-07-12/"
    "naturalized-transfer-sources/v1-case01-flood-infrastructure.txt"
)
SEED_RESULT = Path(
    "research/residual-challenge-seed-case01-probe-2026-07-13/t1/result.json"
)
ROUTING = Path(
    "docs/conversation-understanding/residual-challenge-seed-graph-routing-v1.json"
)
KNOWLEDGE = Path("data/knowledge_graph.json")
RELATIONSHIP = Path("data/relationship_graph.json")


def _load(path: Path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _file_sha(path: Path) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build() -> tuple[dict, dict]:
    seed_result = _load(SEED_RESULT)
    if seed_result.get("case_id") != CASE_ID:
        raise RuntimeError("Case 01 seed identity drifted")
    knowledge = _load(KNOWLEDGE)
    relationship = _load(RELATIONSHIP)
    recall = build_residual_seed_graph_recall_v1(
        seed_portfolio=seed_result["joined_seed_portfolio"],
        routing_contract=_load(ROUTING),
        knowledge_graph=knowledge,
        relationship_graph=relationship,
    )
    direct_candidates = []
    for row in [
        *recall["direct_ledger"]["active_candidates"],
        *recall["direct_ledger"]["reserve_candidates"],
    ]:
        direct_candidates.append(
            {
                "model_id": row["model_id"],
                "recall_source": "case01_residual_seed_direct_replay",
                "source_mechanism_ids": list(row["recalled_by_mechanism_ids"]),
            }
        )
    portfolio = build_constitutional_graph_survival(
        candidates=direct_candidates,
        knowledge_graph=knowledge,
        relationship_graph=relationship,
    )
    refs = [
        {
            "path": str(path),
            "role": role,
            "sha256": _file_sha(path),
        }
        for path, role in (
            (CONVERSATION, "authoritative_conversation"),
            (SEED_RESULT, "case01_residual_seed_and_coverage_receipt"),
            (ROUTING, "controlled_residual_seed_routing"),
            (KNOWLEDGE, "canonical_mental_model_registry"),
            (RELATIONSHIP, "deterministic_relationship_graph"),
        )
    ]
    bundle = build_pressure_bundle(
        case_id=CASE_ID,
        conversation=(ROOT / CONVERSATION).read_text(encoding="utf-8"),
        constitutional_graph_survival=portfolio,
        source_refs=refs,
    )
    body = bundle["request_body"]
    summary = {
        "schema_version": "lolla.r3_fresh_consumer_pressure_preflight.v1",
        "status": "provider_free_preflight_ready",
        "case_id": CASE_ID,
        "active_pressure_ids": [
            item["pressure_id"] for item in portfolio["active_pressure_items"]
        ],
        "active_model_ids": [
            item["model_id"] for item in portfolio["active_pressure_items"]
        ],
        "path_counts": portfolio["path_counts"],
        "fan_in_measurement": portfolio["fan_in_measurement"],
        "authoritative_conversation_sha256": bundle["packet"][
            "authoritative_conversation_sha256"
        ],
        "constitutional_graph_portfolio_sha256": portfolio["portfolio_sha256"],
        "packet_sha256": bundle["packet"]["packet_sha256"],
        "bundle_sha256": bundle["bundle_sha256"],
        "system_prompt_sha256": bundle["hashes"]["system_prompt_sha256"],
        "user_prompt_sha256": bundle["hashes"]["user_prompt_sha256"],
        "response_schema_sha256": bundle["hashes"]["response_schema_sha256"],
        "request_body_sha256": bundle["hashes"]["request_body_sha256"],
        "user_prompt_utf8_bytes": len(
            bundle["prompts"]["user_prompt"].encode("utf-8")
        ),
        "request_estimated_input_tokens": estimated_tokens(
            {key: value for key, value in body.items() if key != "max_tokens"}
        ),
        "maximum_output_tokens": body["max_tokens"],
        "maximum_estimated_call_cost_usd": bundle["request_contract"][
            "maximum_estimated_call_cost_usd"
        ],
        "maximum_provider_reported_cost_usd": bundle["request_contract"][
            "maximum_provider_reported_cost_usd"
        ],
        "provider_calls": 0,
        "next_call_authorized": False,
        "canonical_request_bytes": len(canonical(body).encode("utf-8")),
    }
    return portfolio, bundle | {"preflight_summary": summary}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    portfolio, bundle = build()
    summary = bundle.pop("preflight_summary")
    _write(output / "constitutional-graph-portfolio.json", portfolio)
    _write(output / "pressure-bundle.json", bundle)
    _write(output / "preflight-summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
