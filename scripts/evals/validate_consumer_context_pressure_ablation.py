#!/usr/bin/env python3
"""Validate the provider-free consumer-context pressure ablation contract."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_RELATIVE = "docs/evals/lolla-consumer-context-pressure-ablation-contract-v0.json"

EXPECTED_FRESH_ARMS = (
    "f0_fresh_transcript_only",
    "f1_fresh_current_live_bridge_plus_current_graph",
    "f2_fresh_human_controlled_fact_free_direct_only",
    "f3_fresh_human_controlled_fact_free_plus_current_graph",
)

EXPECTED_CONTEXT_CELLS = (
    "t0_trajectory_continuation_transcript_only",
    "t3_trajectory_continuation_human_controlled_plus_current_graph",
    "f0_fresh_transcript_only",
    "f3_fresh_human_controlled_fact_free_plus_current_graph",
)

EXPECTED_ALL_CELLS = EXPECTED_FRESH_ARMS + EXPECTED_CONTEXT_CELLS[:2]

EXPECTED_COMPARISONS = {
    "fresh_current_bridge_distortion": (
        "f1_fresh_current_live_bridge_plus_current_graph",
        "f3_fresh_human_controlled_fact_free_plus_current_graph",
    ),
    "fresh_graph_relationship_increment": (
        "f2_fresh_human_controlled_fact_free_direct_only",
        "f3_fresh_human_controlled_fact_free_plus_current_graph",
    ),
    "fresh_graph_pressure_increment": (
        "f0_fresh_transcript_only",
        "f3_fresh_human_controlled_fact_free_plus_current_graph",
    ),
    "trajectory_pressure_increment": (
        "t0_trajectory_continuation_transcript_only",
        "t3_trajectory_continuation_human_controlled_plus_current_graph",
    ),
    "context_by_pressure_interaction": (
        "trajectory_pressure_increment",
        "fresh_graph_pressure_increment",
    ),
}

REQUIRED_ISOLATION_RULES = {
    "freeze_all_inputs_before_any_generation",
    "run_each_cell_in_an_isolated_context",
    "never_run_control_after_treatment_in_the_same_session",
    "hold_f3_and_t3_pressure_content_order_format_and_source_label_visibility_byte_identical",
    "preserve_first_terminal_result_without_retry_fallback_or_healing",
}

REQUIRED_CUSTODY = {
    "case_id_and_authoritative_source_hash",
    "source_coverage_and_compaction_state",
    "prior_answer_hash_and_self_authorship_role_representation",
    "pre_pressure_context_checkpoint_manifest_and_hash",
    "pressure_payload_hash_and_source_label_visibility",
    "provider_model_route_seed_settings_and_output_cap",
    "cell_execution_order_and_isolation_receipts",
    "apply_reject_park_ledger_for_every_presented_candidate",
    "blind_review_state_and_arm_reveal_time",
}


def validate(
    root: Path = ROOT,
    *,
    contract_override: dict | None = None,
) -> tuple[list[str], dict]:
    errors: list[str] = []
    path = root / CONTRACT_RELATIVE
    if contract_override is not None:
        contract = contract_override
    elif not path.exists():
        contract = {}
        errors.append(f"missing consumer-context contract: {CONTRACT_RELATIVE}")
    else:
        try:
            contract = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            contract = {}
            errors.append(f"consumer-context contract is invalid JSON: {exc}")

    if contract.get("schema_version") != "lolla.consumer_context_pressure_ablation_contract.v0":
        errors.append("consumer-context contract has unexpected schema_version")
    if contract.get("status") != "provider_free_design_complete_case_and_execution_unstarted":
        errors.append("consumer-context contract must remain design-complete and execution-unstarted")

    claims = {
        item.get("claim"): item
        for item in contract.get("claim_ledger", [])
        if isinstance(item, dict)
    }
    expected_claim_statuses = {
        "ordinary_live_step6_is_same_context": "verified",
        "bounded_graph_candidates_survive_upstream_probabilistic_filtering": "verified_mechanically",
        "same_context_systematically_devalues_external_graph_pressure": "unverified_hypothesis",
        "fresh_context_eliminates_the_vanilla_frame": "not_assumed",
    }
    for claim, status in expected_claim_statuses.items():
        if claims.get(claim, {}).get("status") != status:
            errors.append(f"consumer-context claim {claim} must remain {status}")
        for relative in claims.get(claim, {}).get("evidence", []):
            if not (root / relative).exists():
                errors.append(f"consumer-context claim evidence path missing: {relative}")

    evils = contract.get("product_evil_boundary", {})
    expected_evils = {
        "upstream_probabilistic_redomestication": "mechanically_controlled_by_constitutional_graph_survival",
        "downstream_same_context_self_justification": "known_live_limitation_empirical_effect_unverified",
        "opposite_mandatory_absorption": "must_be_tested_as_a_coequal_failure",
    }
    for evil, state in expected_evils.items():
        if evils.get(evil, {}).get("current_state") != state:
            errors.append(f"consumer-context evil {evil} must remain {state}")

    hypotheses = {
        item.get("id")
        for item in contract.get("competing_hypotheses", [])
        if isinstance(item, dict) and item.get("prediction") and item.get("falsifier")
    }
    expected_hypotheses = {
        "h1_same_context_coherence_defense",
        "h2_fresh_context_overabsorption",
        "h3_graph_pressure_has_no_distinct_value",
        "h4_packet_or_label_confound",
    }
    if hypotheses != expected_hypotheses:
        errors.append("consumer-context contract must preserve four competing falsifiable hypotheses")

    design = contract.get("experiment_design", {})
    if design.get("design") != "six_output_nested_graph_supply_and_consumer_context_ablation":
        errors.append("consumer-context contract must use the six-output nested design")
    if tuple(design.get("fresh_graph_supply_arms", ())) != EXPECTED_FRESH_ARMS:
        errors.append("consumer-context contract fresh graph-supply arms drifted")
    if tuple(design.get("context_by_pressure_cells", ())) != EXPECTED_CONTEXT_CELLS:
        errors.append("consumer-context contract context-by-pressure cells drifted")

    cells = design.get("cells", [])
    cell_ids = tuple(item.get("id") for item in cells if isinstance(item, dict))
    if cell_ids != EXPECTED_ALL_CELLS:
        errors.append("consumer-context contract must define the six exact output cells once")
    if len(cell_ids) != len(set(cell_ids)):
        errors.append("consumer-context contract cell IDs must be unique")
    for item in cells:
        if not isinstance(item, dict):
            errors.append("consumer-context contract cell must be an object")
            continue
        if item.get("consumer_context_mode") not in {"fresh_reconstruction", "trajectory_continuation"}:
            errors.append(f"consumer-context cell has unknown context mode: {item.get('id')}")
        if not item.get("pressure_supply") or not item.get("job"):
            errors.append(f"consumer-context cell is incomplete: {item.get('id')}")

    context_modes = design.get("context_modes", {})
    if set(context_modes) != {"trajectory_continuation", "fresh_reconstruction"}:
        errors.append("consumer-context contract must define both declared context modes")
    if "does not mean independent truth" not in context_modes.get("fresh_reconstruction", ""):
        errors.append("fresh reconstruction must not be presented as independent truth")
    if "not a matched causal cell" not in design.get("live_host_observation", ""):
        errors.append("ordinary live host output must remain observational unless clonable")

    isolation = set(design.get("execution_isolation", []))
    if not REQUIRED_ISOLATION_RULES.issubset(isolation):
        errors.append("consumer-context contract is missing required isolation rules")

    comparisons = {
        item.get("id"): (item.get("left"), item.get("right"))
        for item in contract.get("paired_comparisons", [])
        if isinstance(item, dict) and item.get("question")
    }
    if comparisons != EXPECTED_COMPARISONS:
        errors.append("consumer-context paired comparisons drifted")

    custody = set(contract.get("required_custody_before_execution", []))
    if not REQUIRED_CUSTODY.issubset(custody):
        errors.append("consumer-context contract is missing required context or pressure custody")

    interpretation = " ".join(contract.get("interpretation_rules", [])).lower()
    for phrase in (
        "lower graph-candidate application rate is not evidence",
        "higher application rate is not evidence",
        "grounded rejection",
        "forced absorption",
        "not an independent human judgment",
    ):
        if phrase not in interpretation:
            errors.append(f"consumer-context interpretation rules missing: {phrase}")

    if not contract.get("missing_before_execution"):
        errors.append("consumer-context contract must list missing execution prerequisites")

    authorization = contract.get("authorization", {})
    expected_authorization = {
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "private_archive_inspection": False,
        "principal_human_review_completed": False,
        "live_skill_change": False,
        "runtime_change": False,
        "graph_policy_change": False,
        "fresh_context_promotion": False,
        "product_claim": False,
    }
    for key, expected in expected_authorization.items():
        if authorization.get(key) != expected:
            errors.append(f"consumer-context authorization.{key} must be {expected!r}")

    receipt = {
        "cell_count": len(cells),
        "context_ablation_cell_count": len(design.get("context_by_pressure_cells", [])),
        "fresh_graph_supply_arm_count": len(design.get("fresh_graph_supply_arms", [])),
        "provider_calls": authorization.get("provider_calls"),
        "provider_cost_usd": authorization.get("provider_cost_usd"),
        "schema_version": contract.get("schema_version"),
        "status": "valid" if not errors else "invalid",
    }
    return errors, receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors, receipt = validate(args.root.resolve())
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
