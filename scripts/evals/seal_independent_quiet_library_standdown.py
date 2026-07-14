#!/usr/bin/env python3
"""Seal deterministic zero-candidate recall for the independent quiet case."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MECHANISM_RESULT = ROOT / "research/independent-quiet-library-mechanism-probe-2026-07-12/result.json"
SOURCE_REVIEW = ROOT / "research/independent-quiet-library-mechanism-probe-2026-07-12/source-review.json"
ROUTING = ROOT / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def seal(output: Path) -> dict[str, Any]:
    mechanism = load(MECHANISM_RESULT)
    review = load(SOURCE_REVIEW)
    routing = load(ROUTING)
    projection = mechanism["call"]["compiled"]["routing_projection"]
    nodes = projection["pattern_nodes"]
    if mechanism["evaluation"]["status"] != "quiet_mechanism_standdown_pass" or nodes:
        raise ValueError("mechanism result is not an empty stand-down projection")
    if review["decision"]["correct_quiet_standdown_observed"] is not True:
        raise ValueError("source review did not confirm quiet stand-down")
    if routing["selection_policy"]["operation"] != "deterministic_union_of_declared_seed_models":
        raise ValueError("routing policy drifted")
    result = {
        "schema_version": "lolla.independent_quiet_deterministic_standdown.v1",
        "status": "deterministic_empty_portfolio_standdown",
        "case_id": "phase5-independent-quiet-library-laptop-pilot",
        "inputs": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
            for path in (MECHANISM_RESULT, SOURCE_REVIEW, ROUTING)
        ],
        "unresolved_mechanism_ids": [],
        "candidate_count": 0,
        "candidates": [],
        "candidate_deletion_performed": False,
        "semantic_prefilter_performed": False,
        "graph_traversal_required": False,
        "graph_calls": 0,
        "standdown": {
            "reason": "No unresolved fact-free mechanism entered deterministic routing.",
            "fresh_pressure_call_required": False,
            "public_revision_required": False,
            "preserve_current_reasoning": True
        },
        "boundary": {
            "empty_portfolio_is_not_hidden_failure": True,
            "negative_review_was_probabilistically_interpreted": True,
            "no_forced_pressure": True,
            "graph_runtime_modified": False,
            "runtime_integration_authorized": False
        },
        "scalar_score": None
    }
    write(output / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = seal(args.output.resolve())
    print(json.dumps({"status": result["status"], "candidate_count": result["candidate_count"], "graph_calls": result["graph_calls"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
