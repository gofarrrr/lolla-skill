#!/usr/bin/env python3
"""Validate the provider-free consumer-context pressure ablation contract."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_RELATIVE = "docs/evals/lolla-consumer-context-pressure-ablation-contract-v1.json"
PREDECESSOR_RELATIVE = "docs/evals/lolla-consumer-context-pressure-ablation-contract-v0.json"

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
    "consumer_context_representation_interaction": (
        "trajectory_pressure_increment",
        "fresh_graph_pressure_increment",
    ),
}

REQUIRED_ISOLATION_RULES = {
    "freeze_all_inputs_before_any_generation",
    "run_each_cell_in_an_isolated_context",
    "never_run_control_after_treatment_in_the_same_session",
    "choose_exactly_one_context_implementation_and_label_its_claim_boundary",
    "place_any_true_host_checkpoint_before_all_experimental_pressure_exposure",
    "freeze_complete_serialized_message_arrays_roles_order_wrappers_schema_and_pressure_injection_position_per_cell",
    "hold_f3_and_t3_pressure_content_order_format_and_source_label_visibility_byte_identical",
    "hold_f2_direct_candidate_ids_content_order_format_and_source_label_visibility_byte_identical_to_the_direct_component_of_f3",
    "map_every_active_planner_pressure_id_to_exactly_one_presented_pressure_item_with_zero_missing_extra_merged_or_duplicate_items",
    "hold_f0_and_t0_answer_contract_byte_identical_with_an_explicit_null_pressure_block_except_for_the_declared_context_representation",
    "preserve_first_terminal_result_without_retry_fallback_or_healing",
    "label_one_output_per_cell_as_single_draw_case_diagnostic_unless_deterministic_replay_or_prospective_repeats_are_authorized",
    "review_source_first_under_anonymized_randomized_output_ids_and_record_arm_identity_guess_before_reveal",
}

REQUIRED_CUSTODY = {
    "case_id_and_authoritative_source_hash",
    "source_coverage_compaction_and_omission_state",
    "source_first_target_reviewer_identity_and_signature",
    "reference_packet_author_identity_source_set_authoring_order_and_prior_graph_model_or_output_exposure",
    "prior_answer_hash_and_role_attribution_representation",
    "selected_context_implementation_and_claim_boundary",
    "pre_pressure_context_checkpoint_or_prompt_representation_manifest_and_hash",
    "complete_serialized_message_arrays_roles_order_wrappers_and_hashes_per_cell",
    "system_developer_user_prompt_output_schema_and_injection_position_hashes_per_cell",
    "f2_to_f3_direct_component_byte_identity_receipt",
    "active_planner_candidate_to_presented_payload_bijection_receipt",
    "pressure_payload_hash_order_format_and_source_label_visibility",
    "input_token_counts_candidate_fan_in_and_output_caps_per_cell",
    "provider_model_interface_route_seed_settings_and_version_identity",
    "cell_execution_order_randomization_isolation_and_provider_drift_receipts",
    "apply_reject_park_ledger_for_every_presented_candidate",
    "blind_review_anonymized_order_arm_guess_and_reveal_time",
}

EXPECTED_REJECTION_JUDGMENTS = {
    "strongest_plausible_application_was_attempted",
    "failed_condition_is_specific_and_source_supported",
    "forcing_risk_or_harm_is_concrete",
    "rationale_adds_a_source_grounded_test_rather_than_repeating_the_prior_answer",
    "park_condition_is_actionable_and_genuinely_reopenable",
    "semantic_non_consideration_laundering_is_absent_or_named",
    "reviewer_uncertainty_and_disagreement_are_preserved",
}

EXPECTED_NON_SCALAR_CATEGORIES = {
    "new_source_grounded_leverage",
    "grounded_rejection",
    "grounded_park",
    "circular_restatement_or_coherence_defense_candidate",
    "forced_absorption",
    "unsupported_fact_or_causation",
    "useful_original_value_preserved",
    "useful_original_value_lost",
    "public_friction_or_cognitive_burden",
    "reviewer_uncertainty_and_disagreement",
}

REQUIRED_MISSING_PREREQUISITES = {
    "exact_case_and_authoritative_source_hash",
    "signed_principal_human_source_first_target",
    "grounded_rejection_vs_coherence_defense_human_rubric",
    "selected_honest_context_implementation",
    "clonable_pre_pressure_checkpoint_or_exact_prompt_level_representation_manifests",
    "complete_serialized_request_envelopes_for_all_six_cells",
    "f2_f3_direct_component_identity_receipt",
    "active_candidate_to_presented_payload_bijection_receipt",
    "predeclared_non_scalar_pairwise_review_form",
    "stochasticity_and_execution_order_policy",
    "anonymized_blind_review_and_cell_reveal_protocol",
    "separate_founder_authorization",
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

    if contract.get("schema_version") != "lolla.consumer_context_pressure_ablation_contract.v1":
        errors.append("consumer-context contract has unexpected schema_version")
    if contract.get("predecessor") != PREDECESSOR_RELATIVE:
        errors.append("consumer-context contract must preserve the v0 predecessor boundary")
    if not (root / PREDECESSOR_RELATIVE).exists():
        errors.append(f"consumer-context predecessor is missing: {PREDECESSOR_RELATIVE}")
    if contract.get("status") != "provider_free_design_shape_valid_execution_not_ready":
        errors.append("consumer-context contract must remain design-shape-valid and execution-not-ready")

    readiness = contract.get("readiness", {})
    expected_readiness = {
        "design_shape_valid": True,
        "execution_ready": False,
        "single_draw_evidence_class": "single_draw_case_diagnostic",
        "causal_interaction_identified": False,
        "self_justification_mechanism_identified": False,
    }
    for key, expected in expected_readiness.items():
        if readiness.get(key) != expected:
            errors.append(f"consumer-context readiness.{key} must be {expected!r}")

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
        "context_interaction_establishes_self_justification": "not_assumed",
        "one_stochastic_draw_per_cell_identifies_an_expected_causal_interaction": "not_assumed",
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
        "evaluation_payload_redomestication": "must_be_controlled_by_active_candidate_to_payload_bijection",
        "downstream_same_context_self_justification": "known_live_limitation_empirical_effect_unverified",
        "semantic_non_consideration_laundering": "requires_source_first_principal_human_rubric",
        "opposite_mandatory_absorption": "must_be_tested_symmetrically_with_fresh_context_amplification_only_a_hypothesis",
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
        "h4_packet_label_or_context_packaging_confound",
        "h5_stochastic_call_variance",
        "h6_generic_augmentation_or_authority_effect",
        "h7_fresh_reconstruction_lost_information",
        "h8_case_selection_or_evaluator_expectancy",
    }
    if hypotheses != expected_hypotheses:
        errors.append("consumer-context contract must preserve eight competing falsifiable hypotheses")

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
    primary_estimand = design.get("primary_estimand", {})
    if primary_estimand.get("id") != "consumer_context_representation_interaction":
        errors.append("consumer-context contract must name the representation interaction estimand")
    if "does_not_by_itself_identify_self_justification" not in primary_estimand.get("non_claim", ""):
        errors.append("consumer-context estimand must not identify self-justification by itself")
    context_choice = design.get("context_implementation_choice", {})
    if context_choice.get("selected") != "unselected":
        errors.append("consumer-context implementation must remain unselected before case freeze")
    if not context_choice.get("true_host_trajectory_fork") or not context_choice.get(
        "prompt_level_role_attribution_representation"
    ):
        errors.append("consumer-context contract must preserve both honest context implementation options")

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

    rejection_rubric = contract.get("grounded_rejection_vs_coherence_defense_human_rubric", {})
    if rejection_rubric.get("authority") != "principal_human_source_first_review_required":
        errors.append("consumer-context rejection rubric must require principal-human source-first review")
    if set(rejection_rubric.get("required_judgments", ())) != EXPECTED_REJECTION_JUDGMENTS:
        errors.append("consumer-context rejection rubric judgments drifted")
    if "not serious semantic consideration" not in rejection_rubric.get("non_claim", ""):
        errors.append("consumer-context rejection ledger must not certify serious consideration")

    comparison_operator = contract.get("non_scalar_comparison_operator", {})
    if set(comparison_operator.get("required_categories", ())) != EXPECTED_NON_SCALAR_CATEGORIES:
        errors.append("consumer-context non-scalar comparison categories drifted")
    if "do not reduce them to one winner score" not in comparison_operator.get("rule", ""):
        errors.append("consumer-context comparison must preserve disagreement without a winner score")

    quiet_boundary = contract.get("quiet_case_boundary", {})
    if quiet_boundary.get("name") != "supply_stand_down_negative_control":
        errors.append("consumer-context quiet case must remain a supply stand-down negative control")
    if quiet_boundary.get("cannot_test") != "consumer_absorption_when_no_pressure_payload_is_present":
        errors.append("consumer-context quiet case must not claim to test absent-payload absorption")

    reference_boundary = contract.get("reference_condition_boundary", {})
    if reference_boundary.get("name") != "source_reviewed_human_controlled_reference_condition":
        errors.append("consumer-context human packet must be a source-reviewed reference condition")
    if reference_boundary.get("not_an_oracle") is not True:
        errors.append("consumer-context human reference condition must not be called an oracle")

    interpretation = " ".join(contract.get("interpretation_rules", [])).lower()
    for phrase in (
        "lower graph-candidate application rate is not evidence",
        "higher application rate is not evidence",
        "grounded rejection",
        "forced absorption",
        "not an independent human judgment",
        "context interaction alone does not establish self-justification",
        "single-draw case diagnostic",
        "complete disposition ledger proves custody",
    ):
        if phrase not in interpretation:
            errors.append(f"consumer-context interpretation rules missing: {phrase}")

    missing = set(contract.get("missing_before_execution", []))
    if not REQUIRED_MISSING_PREREQUISITES.issubset(missing):
        errors.append("consumer-context contract must preserve unresolved execution prerequisites")

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
        "design_shape_valid": readiness.get("design_shape_valid"),
        "execution_ready": readiness.get("execution_ready"),
        "single_draw_evidence_class": readiness.get("single_draw_evidence_class"),
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
