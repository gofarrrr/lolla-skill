#!/usr/bin/env python3
"""Diagnose the 0-gap-questions anomaly on messy_three_problems new_run2.

Reconstructs the gap-question-generation call with raw LLM response logging
to test three hypotheses:
  (A) LLM keys gap_questions by dimension_name ("Competitive Dynamics")
      instead of dimension_id ("competitive-dynamics"). Parser accepts the
      keys but `generate_gap_questions_from_context` then misses them on
      dim_id lookup. Fix: tolerant parser with name fallback.
  (B) LLM returns empty or malformed JSON (e.g., `{}` or `{"gap_questions": []}`)
      on this specific prompt. Fix: prompt improvement or retry.
  (C) Random variance — the failure is a rare LLM event with no systematic
      cause. Fix: accept the rate, add a retry.

N=5 runs on the failing case. Prints raw response on each run and classifies
which hypothesis fits.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "engine"))

# Load .env
for line in (REPO_ROOT / ".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    if line.startswith("export "):
        line = line[7:].strip()
    k, _, v = line.partition("=")
    k = k.strip()
    v = v.strip().strip('"').strip("'")
    if k and k not in os.environ:
        os.environ[k] = v

from system_b.boundary_provider import load_boundary_client_from_env
from system_b.conversation_loader import load_conversation_context
from system_b.structural_coverage import (
    DimensionRoute,
    _format_gap_question_from_context_user_prompt,
    _GAP_QUESTION_GENERATION_SYSTEM,
)


def main() -> int:
    # Load the same inputs that produced the failing run
    ext = REPO_ROOT / "research/test-cases/phase2b-lane4-equivalence-2026-04-23/_scratch/messy_three_problems_extraction.json"
    conv = REPO_ROOT / "research/test-cases/case_messy_three_problems_conversation.txt"
    ctx = load_conversation_context(ext, conv)

    # Reconstruct the gap_routes that failing run had
    gap_routes = (
        DimensionRoute(dimension_id="competitive-dynamics", dimension_name="Competitive Dynamics",
                       candidate_model_ids=("game-theory-payoffs",), excluded_model_ids=()),
        DimensionRoute(dimension_id="incentive-alignment", dimension_name="Incentive Alignment",
                       candidate_model_ids=("principal-agent-problem",), excluded_model_ids=()),
        DimensionRoute(dimension_id="information-quality", dimension_name="Information Quality",
                       candidate_model_ids=("survivorship-bias",), excluded_model_ids=()),
        DimensionRoute(dimension_id="stakeholder-alignment", dimension_name="Stakeholder Alignment",
                       candidate_model_ids=("power-dynamics",), excluded_model_ids=()),
        DimensionRoute(dimension_id="uncertainty-type", dimension_name="Uncertainty Type",
                       candidate_model_ids=("aleatory-epistemic-uncertainty-recognition",), excluded_model_ids=()),
    )

    # Build the user prompt the exact same way the production code does
    # Load the structural_coverage_routing from the companion knowledge graph
    kg_path = REPO_ROOT / "data/knowledge_graph.json"
    kg = json.loads(kg_path.read_text()) if kg_path.exists() else {}
    routing = kg.get("structural_coverage_routing") or kg.get("structural_coverage") or {"dimensions": {}}

    user_prompt = _format_gap_question_from_context_user_prompt(
        ctx, "decision-evaluation", gap_routes, routing,
    )
    print(f"=== Setup ===")
    print(f"Prompt length: {len(user_prompt)} chars")
    print(f"Gap routes expected: {[r.dimension_id for r in gap_routes]}")
    print()

    boundary = load_boundary_client_from_env("openrouter")

    outcomes = []
    for i in range(5):
        print(f"--- Run {i+1}/5 ---")
        try:
            raw = boundary.run_json(_GAP_QUESTION_GENERATION_SYSTEM, user_prompt)
        except Exception as exc:
            print(f"  EXCEPTION: {exc}")
            outcomes.append(("exception", str(exc)[:200]))
            continue

        gq = raw.get("gap_questions") if isinstance(raw, dict) else None
        print(f"  raw type: {type(raw).__name__}")
        if isinstance(raw, dict):
            print(f"  top-level keys: {list(raw.keys())}")
        if gq is None:
            print(f"  gap_questions key: MISSING")
            outcomes.append(("missing_key", json.dumps(raw)[:300]))
            continue
        if not isinstance(gq, dict):
            print(f"  gap_questions is a {type(gq).__name__} (expected dict)")
            outcomes.append(("wrong_type", json.dumps(gq)[:300]))
            continue

        keys = list(gq.keys())
        print(f"  gap_questions keys: {keys}")
        expected_ids = {r.dimension_id for r in gap_routes}
        expected_names = {r.dimension_name for r in gap_routes}
        match_by_id = [k for k in keys if k in expected_ids]
        match_by_name = [k for k in keys if k in expected_names]
        other = [k for k in keys if k not in expected_ids and k not in expected_names]

        print(f"  keyed by dim_id: {match_by_id}")
        print(f"  keyed by dim_name: {match_by_name}")
        if other:
            print(f"  other keys: {other}")

        if match_by_id:
            outcomes.append(("success_by_id", f"{len(match_by_id)} matched by id"))
        elif match_by_name:
            outcomes.append(("hypothesis_A_name_keying", f"{len(match_by_name)} keyed by name: {match_by_name}"))
        elif not keys:
            outcomes.append(("hypothesis_B_empty", "{} empty dict"))
        else:
            outcomes.append(("other", f"unexpected keys: {other}"))

    print()
    print("=== Summary ===")
    for i, (cat, detail) in enumerate(outcomes):
        print(f"  run {i+1}: {cat}  ({detail})")

    by_cat: dict[str, int] = {}
    for cat, _ in outcomes:
        by_cat[cat] = by_cat.get(cat, 0) + 1
    print()
    print(f"Categories: {by_cat}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
