#!/usr/bin/env python3
"""Freeze the human source-first review of R4 matched-holdout v2 A1."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals import seal_r4_matched_holdout_v2_execution_a1 as raw_seal
from scripts.evals.run_r4_matched_holdout_v2_experiment import validate_contract


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = raw_seal.OUTPUT
RUN_RESULT = OUTPUT / "result.json"
RAW_MANIFEST = OUTPUT / "raw-evidence-manifest.json"
AUTHORIZATION_CONSUMPTION = OUTPUT / "authorization-consumption.json"
SOURCE_REVIEW = OUTPUT / "source-first-review.json"
EVIDENCE_MANIFEST = OUTPUT / "evidence-manifest.json"
CLOSEOUT = OUTPUT / "execution-closeout.json"
CONTRACT = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
TARGET = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target.json"
TARGET_REVIEW = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target-review.json"
RUNNER = ROOT / "scripts/evals/run_r4_matched_holdout_v2_experiment.py"
RAW_CHECKPOINT_COMMIT = "e2f83561686172538c8ac8876a53da2a804dc503"
CANONICAL_BASE_COMMIT = "b7d1d62c05bdf05f91401c25ceb0a2cc73ffe307"
CONTRACT_SHA256 = raw_seal.CONTRACT_SHA256
TARGET_SHA256 = (
    "9630699de23f1782dc7761938d5912ec62ad12b64a2380678a3dffcfd11b3aa1"
)
TARGET_REVIEW_SHA256 = (
    "f6ecbeced6d8ec29f44fbd5fe3a2035409abb3ae71366a6b25aaa619cc6960ce"
)
TOTAL_COST_USD = raw_seal.TOTAL_COST_USD
ESTIMATED_COST_USD = 0.040521


class R4MatchedExecutionA1CloseoutError(RuntimeError):
    """Raised when the sealed execution or fixed human review drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4MatchedExecutionA1CloseoutError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_render(value))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _record_index(run: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for call in run["calls"]:
        for reader in call["compiled"]["reader_results"]:
            for record in reader["records"]:
                record_id = record["record_id"]
                if record_id in index:
                    raise R4MatchedExecutionA1CloseoutError(
                        f"duplicate record id: {record_id}"
                    )
                semantic = record["semantic_payload"]["record"]
                canonical_surface = record["surface"]
                provider_surface = canonical_surface
                if call["arm"] == "B_frozen_residual_task":
                    provider_surface = {
                        "unresolved_matter": "residual_decision_gap",
                        "reopen_condition": "residual_reconsideration_dependency",
                    }[canonical_surface]
                index[record_id] = {
                    "record_id": record_id,
                    "call_ordinal": call["ordinal"],
                    "case_id": call["case_id"],
                    "arm": call["arm"],
                    "provider_surface": provider_surface,
                    "canonical_surface": canonical_surface,
                    "provider_aliases": semantic["evidence_ids"],
                    "interpretation": semantic["interpretation"],
                    "provider_limitations": semantic["limitations"],
                }
    return index


def _target_index(target: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["case_id"]: row for row in target["cases"]}


REVIEW_SPECS: tuple[dict[str, Any], ...] = (
    {
        "record_id": "r4u-r4h2-case01-community-audio-archive-unresolved_matter-01-47d58696e1d1",
        "source_first_verdict": "false_positive_governed_pending_inventory",
        "false_positive": True,
        "false_positive_class": "governed_casework_inventory",
        "support_verdict": "facts_supported_but_residual_placement_not_supported",
        "semantic_surface_placement": "incorrect_on_quiet_unresolved_surface",
        "evidence_precision_verdict": "endpoint_aliases_show_adoption_but_omit_the_governing_procedures",
        "inside_or_outside_adopted_machinery": "inside_adopted_permission_ledger_calendar_and_capacity_machinery",
        "speaker_ownership_verdict": "broad_library_ownership_obscures_the_named_role_allocation",
        "modal_fidelity_verdict": "ongoing_work_is_real_but_must_navigate_does_not_create_an_unowned_question",
        "prior_anchoring_verdict": "consistent_with_the_broad_unresolved_prior_anchor",
        "late_evidence_verdict": "late_endpoints_used_but_interpreted_as_inventory_instead_of_subtraction",
        "rationale": "The record expressly acknowledges active administration. The signed calendar, staffed ledger, and thresholds make the remaining file reviews governed work rather than a material decision gap.",
    },
    {
        "record_id": "r4u-r4h2-case01-community-audio-archive-unresolved_matter-02-34e492186d3a",
        "source_first_verdict": "false_positive_governed_pending_inventory",
        "false_positive": True,
        "false_positive_class": "governed_casework_inventory",
        "support_verdict": "pending_cases_supported_but_residual_placement_not_supported",
        "semantic_surface_placement": "incorrect_on_quiet_unresolved_surface",
        "evidence_precision_verdict": "aliases_identify_cases_and_their_existing_routes",
        "inside_or_outside_adopted_machinery": "inside_embargo_alert_current_state_preservation_and_conflict_rotation",
        "speaker_ownership_verdict": "library_level_wording_is_less_precise_than_the_associate_curator_and_rotation_owners",
        "modal_fidelity_verdict": "completion_is_pending_but_not_unassigned",
        "prior_anchoring_verdict": "consistent_with_the_broad_unresolved_prior_anchor",
        "late_evidence_verdict": "mid_late_case_evidence_used_without_the_final_owner_confirmation",
        "rationale": "The address search and reviewer conflict are concrete pending cases, but e024 says both follow the existing calendar and current-state rules. Pending does not establish a residual gap.",
    },
    {
        "record_id": "r4u-r4h2-case01-community-audio-archive-reopen_condition-01-3560e119a08c",
        "source_first_verdict": "false_positive_governed_threshold",
        "false_positive": True,
        "false_positive_class": "governed_capacity_threshold",
        "support_verdict": "threshold_facts_supported_but_dependency_placement_not_supported",
        "semantic_surface_placement": "incorrect_on_quiet_reopen_surface",
        "evidence_precision_verdict": "aliases_prove_predefined_responses_not_an_unhandled_dependency",
        "inside_or_outside_adopted_machinery": "inside_board_funding_batch_and_editor_reallocation_rules",
        "speaker_ownership_verdict": "board_and_curator_responses_are_conflated",
        "modal_fidelity_verdict": "mandate_overstates_the_boards_can_fund_or_reduce_language",
        "prior_anchoring_verdict": "not_explained_by_a_matching_capacity_gap_in_the_prior",
        "late_evidence_verdict": "threshold_evidence_used_but_final_immediate_effect_confirmation_omitted",
        "rationale": "The capacity triggers already specify who may act and what responses are available. They are adopted operational controls, not a distinct premise that defeats the collection policy.",
    },
    {
        "record_id": "r4u-r4h2-case01-community-audio-archive-reopen_condition-02-5d1847d35750",
        "source_first_verdict": "false_positive_existing_safeguard",
        "false_positive": True,
        "false_positive_class": "governed_complaint_safeguard",
        "support_verdict": "complaint_process_supported_but_dependency_placement_not_supported",
        "semantic_surface_placement": "incorrect_on_quiet_reopen_surface",
        "evidence_precision_verdict": "proposal_aliases_omit_later_adoption_deadline_and_owner_evidence",
        "inside_or_outside_adopted_machinery": "inside_temporary_removal_and_dated_complaint_review",
        "speaker_ownership_verdict": "assistant_proposal_is_elevated_without_the_later_user_adoption_aliases",
        "modal_fidelity_verdict": "effectively_reopens_relabels_a_bounded_safeguard_as_a_reader_dependency",
        "prior_anchoring_verdict": "later_objections_are_named_in_the_broad_prior_but_the_prior_does_not_override_the_policy",
        "late_evidence_verdict": "late_adoption_and_owner_evidence_not_used",
        "rationale": "A credible complaint triggers the policy's named temporary action and twenty-day review. The record cites the proposal rather than the later adoption and mistakes a safeguard for a residual dependency.",
    },
    {
        "record_id": "r4u-r4h2-case01-community-audio-archive-reopen_condition-01-3a4f1bf885b7",
        "source_first_verdict": "false_positive_governed_threshold",
        "false_positive": True,
        "false_positive_class": "governed_capacity_threshold",
        "support_verdict": "trigger_and_response_supported_but_residual_dependency_not_supported",
        "semantic_surface_placement": "incorrect_residual_dependency_on_quiet_reopen_surface",
        "evidence_precision_verdict": "single_alias_proves_the_machinery_handles_the_trigger",
        "inside_or_outside_adopted_machinery": "inside_predefined_editor_reallocation_rule",
        "speaker_ownership_verdict": "associate_curator_ownership_preserved",
        "modal_fidelity_verdict": "trigger_force_is_faithful_but_its_reader_role_is_not",
        "prior_anchoring_verdict": "residual_arm_resists_the_broad_unresolved_anchor_but_not_threshold_completion_pressure",
        "late_evidence_verdict": "does_not_use_e027_confirmation_that_thresholds_took_effect",
        "rationale": "The threshold and editor shift are fully operationalized in the current policy. The cited alias establishes the adopted response and therefore defeats rather than supports residual status.",
    },
    {
        "record_id": "r4u-r4h2-case01-community-audio-archive-reopen_condition-02-1424ecb4abc5",
        "source_first_verdict": "false_positive_governed_threshold",
        "false_positive": True,
        "false_positive_class": "governed_capacity_threshold",
        "support_verdict": "trigger_and_options_supported_but_residual_dependency_not_supported",
        "semantic_surface_placement": "incorrect_residual_dependency_on_quiet_reopen_surface",
        "evidence_precision_verdict": "single_alias_proves_board_authority_and_predefined_responses",
        "inside_or_outside_adopted_machinery": "inside_board_funding_or_batch_reduction_rule",
        "speaker_ownership_verdict": "board_ownership_preserved",
        "modal_fidelity_verdict": "can_fund_or_reduce_is_preserved_without_creating_a_defeating_dependency",
        "prior_anchoring_verdict": "not_a_direct_copy_of_the_broad_unresolved_prior",
        "late_evidence_verdict": "does_not_use_e025_staffing_or_e027_effective_threshold_confirmation",
        "rationale": "Legal-review delay activates a declared board choice. It is governed capacity variation, precisely the class the residual contract says to subtract.",
    },
    {
        "record_id": "r4u-r4h2-case02-serialized-essay-pilot-reopen_condition-01-32d266f01bfa",
        "source_first_verdict": "false_positive_scheduled_decision",
        "false_positive": True,
        "false_positive_class": "scheduled_decision_machinery",
        "support_verdict": "calendar_and_evidence_window_supported_but_failure_threshold_not_supported",
        "semantic_surface_placement": "incorrect_residual_dependency_on_quiet_reopen_surface",
        "evidence_precision_verdict": "aliases_show_the_scheduled_board_process_and_do_not_show_an_unhandled_remainder",
        "inside_or_outside_adopted_machinery": "inside_fixed_evidence_close_submission_and_board_choice",
        "speaker_ownership_verdict": "board_authority_preserved_but_assistant_planning_aliases_are_overused",
        "modal_fidelity_verdict": "invents_a_failure_of_defined_conversions_that_the_source_does_not_define",
        "prior_anchoring_verdict": "false_positive_occurs_without_a_matching_prior_gap_anchor",
        "late_evidence_verdict": "uses_late_calendar_evidence_but_omits_signed_charter_and_final_authority_confirmation",
        "rationale": "The final format is deliberately unselected and assigned to October 22. Evidence collection and a scheduled decision are operationalized work, not a reconsideration dependency; no conversion failure threshold is stated.",
    },
    {
        "record_id": "r4u-r4h2-case03-research-workspace-service-unresolved_matter-01-004fcba136ba",
        "source_first_verdict": "supported_genuine_residual_decision_gap",
        "false_positive": False,
        "false_positive_class": None,
        "support_verdict": "supported",
        "semantic_surface_placement": "correct_residual_decision_gap_mapping_to_unresolved_matter",
        "evidence_precision_verdict": "sufficient_distributed_evidence_but_omits_early_launch_and_workload_aliases",
        "inside_or_outside_adopted_machinery": "outside_the_two_semester_launch_and_unfunded_after_june",
        "speaker_ownership_verdict": "unit_refusals_council_limits_and_chair_limits_are_preserved",
        "modal_fidelity_verdict": "faithful_present_absence_of_owner_and_funded_mechanism",
        "prior_anchoring_verdict": "discovers_the_gap_without_a_matching_prior_anchor",
        "late_evidence_verdict": "integrates_e017_with_e025_and_e027_endpoints",
        "rationale": "The record correctly separates the authorized launch from recurring service stewardship after June. Its aliases collectively establish explicit refusals, unapproved options, the grant boundary, and the chair's lack of authority.",
    },
    {
        "record_id": "r4u-r4h2-case03-research-workspace-service-reopen_condition-01-22db4eb78e69",
        "source_first_verdict": "false_positive_duplicative_future_dependency",
        "false_positive": True,
        "false_positive_class": "duplicated_current_gap_as_future_dependency",
        "support_verdict": "funding_process_supported_but_separate_dependency_not_supported",
        "semantic_surface_placement": "incorrect_duplicate_on_reopen_surface",
        "evidence_precision_verdict": "proposal_aliases_do_not_establish_a_current_post_june_model_to_revisit",
        "inside_or_outside_adopted_machinery": "the_february_process_surrounds_the_current_gap_and_does_not_defeat_the_authorized_launch",
        "speaker_ownership_verdict": "budget_and_unit_authority_are_blurred_into_generic_viability",
        "modal_fidelity_verdict": "depends_and_requires_revisiting_overstate_the_effect_on_the_fixed_two_semester_position",
        "prior_anchoring_verdict": "not_driven_by_the_prior_but_by_paired_completion_of_the_same_gap",
        "late_evidence_verdict": "late_options_packet_evidence_used_but_signed_launch_boundary_not_cited",
        "rationale": "No post-June service model has been adopted, so failure of the proposal cycle does not reopen it. This duplicates the supported present ownership and funding gap on the wrong surface.",
    },
    {
        "record_id": "r4u-r4h2-case03-research-workspace-service-unresolved_matter-01-b7d31b3ac866",
        "source_first_verdict": "supported_genuine_unresolved_matter",
        "false_positive": False,
        "false_positive_class": None,
        "support_verdict": "supported",
        "semantic_surface_placement": "correct_unresolved_matter",
        "evidence_precision_verdict": "sufficient_distributed_evidence_but_omits_early_launch_and_workload_aliases",
        "inside_or_outside_adopted_machinery": "outside_the_two_semester_launch_and_unfunded_after_june",
        "speaker_ownership_verdict": "unit_council_budget_and_chair_limits_preserved",
        "modal_fidelity_verdict": "faithful_present_unassigned_and_unfunded_status",
        "prior_anchoring_verdict": "discovers_the_gap_without_a_matching_prior_anchor",
        "late_evidence_verdict": "integrates_e017_with_e025_and_e027_endpoints",
        "rationale": "This matches the target's recurring post-June application and service stewardship gap and does not confuse it with Central IT's continuing infrastructure agreement.",
    },
    {
        "record_id": "r4u-r4h2-case03-research-workspace-service-reopen_condition-01-b1ee9645e364",
        "source_first_verdict": "false_positive_duplicative_future_dependency",
        "false_positive": True,
        "false_positive_class": "duplicated_current_gap_as_future_dependency",
        "support_verdict": "proposal_risk_supported_but_separate_dependency_not_supported",
        "semantic_surface_placement": "incorrect_duplicate_on_reopen_surface",
        "evidence_precision_verdict": "aliases_omit_that_the_current_launch_is_signed_and_independent_of_february",
        "inside_or_outside_adopted_machinery": "the_february_process_addresses_the_current_gap_without_reopening_the_launch",
        "speaker_ownership_verdict": "budget_and_unit_authority_are_only_partly_preserved",
        "modal_fidelity_verdict": "would_require_reconsidering_a_post_june_model_that_does_not_yet_exist",
        "prior_anchoring_verdict": "not_prior_anchored_and_appears_as_paired_surface_completion",
        "late_evidence_verdict": "uses_e027_but_omits_e025_signed_launch_boundary",
        "rationale": "The February outcome matters to resolving the present gap, but the authorized two-semester launch does not depend on it. The record duplicates the gap rather than identifying a distinct future defeater.",
    },
    {
        "record_id": "r4u-r4h2-case03-research-workspace-service-reopen_condition-02-ae2563a3b47d",
        "source_first_verdict": "false_positive_existing_safeguard",
        "false_positive": True,
        "false_positive_class": "governed_incident_safeguard",
        "support_verdict": "incident_response_supported_but_dependency_placement_not_supported",
        "semantic_surface_placement": "incorrect_on_quiet_reopen_surface",
        "evidence_precision_verdict": "proposal_aliases_omit_acceptance_test_and_signed_memorandum_adoption",
        "inside_or_outside_adopted_machinery": "inside_project_pause_logs_restoration_and_resumption_authority",
        "speaker_ownership_verdict": "research_office_and_principal_investigator_ownership_preserved",
        "modal_fidelity_verdict": "may_trigger_is_faithful_but_is_an_existing_protocol_not_a_residual",
        "prior_anchoring_verdict": "consistent_with_prior_incident_controls_not_a_prior_gap",
        "late_evidence_verdict": "late_adoption_e021_and_e025_not_used",
        "rationale": "The record's own limitation says the event follows the agreed protocol and does not invalidate launch. It is a governed safeguard and should remain quiet.",
    },
    {
        "record_id": "r4u-r4h2-case04-shared-language-course-reopen_condition-01-8e0087de5906",
        "source_first_verdict": "supported_core_dependency_with_precision_qualification",
        "false_positive": False,
        "false_positive_class": None,
        "support_verdict": "core_dependency_supported",
        "semantic_surface_placement": "correct_reopen_condition",
        "evidence_precision_verdict": "insufficient_for_full_target_because_credit_reliance_and_no_replacement_authority_are_not_cited",
        "inside_or_outside_adopted_machinery": "outside_ordinary_course_controls_but_only_after_board_withdrawal",
        "speaker_ownership_verdict": "board_withdrawal_authority_and_registrar_verification_are_not_fully_preserved",
        "modal_fidelity_verdict": "loss_of_predicate_is_treated_too_directly_and_immediate_effect_is_softened_to_reconsideration",
        "prior_anchoring_verdict": "discovers_dependency_absent_from_prior",
        "late_evidence_verdict": "uses_e023_notice_but_omits_e025_and_e027_current_endpoint",
        "rationale": "The core State Academic Board dependency is recovered, but the record needs e005, e017, and e025 to establish recognized-credit impact and the absence of locally conferrable replacement authority.",
    },
    {
        "record_id": "r4u-r4h2-case04-shared-language-course-reopen_condition-02-e9a0ef627cd5",
        "source_first_verdict": "false_positive_governed_threshold",
        "false_positive": True,
        "false_positive_class": "governed_enrollment_threshold",
        "support_verdict": "threshold_and_dean_authority_supported_but_dependency_placement_not_supported",
        "semantic_surface_placement": "incorrect_extra_record_on_supported_reopen_surface",
        "evidence_precision_verdict": "aliases_prove_the_threshold_is_codified",
        "inside_or_outside_adopted_machinery": "inside_enrollment_monitoring_and_dean_cancellation_authority",
        "speaker_ownership_verdict": "dean_ownership_preserved",
        "modal_fidelity_verdict": "decision_trigger_is_faithful_but_not_a_residual_dependency",
        "prior_anchoring_verdict": "prior_mentions_viable_enrollment_but_also_says_controls_are_assigned",
        "late_evidence_verdict": "does_not_integrate_final_signed_memorandum_endpoint",
        "rationale": "The fifteen-student threshold is an adopted cancellation rule. It is the exact governed threshold class the experiment expected both readers to suppress.",
    },
    {
        "record_id": "r4u-r4h2-case04-shared-language-course-unresolved_matter-01-9597f7abdfd5",
        "source_first_verdict": "false_positive_assistant_proposal_elevated_to_gap",
        "false_positive": True,
        "false_positive_class": "assistant_proposal_elevated_to_present_gap",
        "support_verdict": "assistant_suggests_legal_review_but_source_does_not_adopt_a_present_gap",
        "semantic_surface_placement": "incorrect_residual_decision_gap_on_quiet_unresolved_surface",
        "evidence_precision_verdict": "both_aliases_are_assistant_instructions_and_no_user_alias_confirms_assignment_or_open_status",
        "inside_or_outside_adopted_machinery": "not_affirmatively_established_as_a_present_matter_outside_the_current_course_approval",
        "speaker_ownership_verdict": "fails_by_attributing_assistant_advice_to_legal_counsel_and_the_institution",
        "modal_fidelity_verdict": "must_determine_overstates_ask_and_have_counsel_record_suggestions",
        "prior_anchoring_verdict": "not_prior_anchored",
        "late_evidence_verdict": "uses_late_assistant_advice_but_omits_active_certificate_and_approved_course_endpoint",
        "rationale": "The source contains assistant recommendations to seek legal treatment of prior contact hours, not a user-adopted present assignment or affirmative unresolved status. Omission of an answer is not evidence of a current decision gap.",
    },
    {
        "record_id": "r4u-r4h2-case04-shared-language-course-reopen_condition-01-57d36fd5717c",
        "source_first_verdict": "supported_core_residual_dependency_with_precision_qualification",
        "false_positive": False,
        "false_positive_class": None,
        "support_verdict": "core_dependency_supported",
        "semantic_surface_placement": "correct_residual_dependency_mapping_to_reopen_condition",
        "evidence_precision_verdict": "insufficient_for_full_target_because_credit_reliance_and_no_backup_authority_are_not_cited",
        "inside_or_outside_adopted_machinery": "outside_ordinary_course_controls_but_conditioned_on_board_withdrawal",
        "speaker_ownership_verdict": "external_board_dependency_is_noted_but_board_registrar_and_provost_roles_are_incomplete",
        "modal_fidelity_verdict": "any_change_in_standing_is_broader_than_board_withdrawal_and_recalculation_understates_immediate_loss_of_future_hours",
        "prior_anchoring_verdict": "discovers_dependency_absent_from_prior",
        "late_evidence_verdict": "uses_e023_notice_but_omits_e025_and_e027_current_endpoint",
        "rationale": "The record recovers the external designation dependency and places it on the correct residual surface, but its two aliases do not prove why existing machinery cannot replace the authority and its trigger wording is broader than the source.",
    },
)


def _build_record_reviews(
    run: Mapping[str, Any], target: Mapping[str, Any]
) -> list[dict[str, Any]]:
    records = _record_index(run)
    targets = _target_index(target)
    expected_ids = {row["record_id"] for row in REVIEW_SPECS}
    if set(records) != expected_ids:
        raise R4MatchedExecutionA1CloseoutError(
            "human record-review set does not match admitted provider records"
        )
    result = []
    for spec in REVIEW_SPECS:
        record = records[spec["record_id"]]
        surface_target = targets[record["case_id"]]["canonical_surface_targets"][
            record["canonical_surface"]
        ]
        result.append(
            {
                **record,
                "target_disposition": surface_target["disposition"],
                "strongest_target_aliases": surface_target[
                    "strongest_source_aliases"
                ],
                **{key: value for key, value in spec.items() if key != "record_id"},
            }
        )
    return result


def _surface_states(run: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    values = {}
    for call in run["calls"]:
        values[(call["case_id"], call["arm"])] = {
            reader["surface"]: {
                "state": reader["state"],
                "record_count": reader["declared_record_count"],
            }
            for reader in call["compiled"]["reader_results"]
        }
    return values


def _build_review() -> dict[str, Any]:
    raw_seal.validate_raw()
    contract = validate_contract(CONTRACT)
    if _file_sha(CONTRACT) != CONTRACT_SHA256:
        raise R4MatchedExecutionA1CloseoutError("contract hash drifted")
    if _file_sha(TARGET) != TARGET_SHA256:
        raise R4MatchedExecutionA1CloseoutError("protected target hash drifted")
    if _file_sha(TARGET_REVIEW) != TARGET_REVIEW_SHA256:
        raise R4MatchedExecutionA1CloseoutError("target review hash drifted")
    run = _load(RUN_RESULT)
    target = _load(TARGET)
    records = _build_record_reviews(run, target)
    states = _surface_states(run)

    cases = [
        {
            "case_id": "r4h2-case01-community-audio-archive",
            "target_role": "governed_pending_restraint_control_with_broad_prior_anchor",
            "target": {"unresolved_matter": "quiet", "reopen_condition": "quiet"},
            "arm_a": {
                "surface_states": states[("r4h2-case01-community-audio-archive", "A_frozen_v2_semantic_distinction")],
                "false_positive_records": 4,
                "correct_zero_surfaces": 0,
                "genuine_target_recovered": None,
                "all_surface_targets_passed": False,
                "verdict": "broad_inventory_and_governed_trigger_restraint_failed",
            },
            "arm_b": {
                "surface_states": states[("r4h2-case01-community-audio-archive", "B_frozen_residual_task")],
                "false_positive_records": 2,
                "correct_zero_surfaces": 1,
                "genuine_target_recovered": None,
                "all_surface_targets_passed": False,
                "verdict": "unresolved_prior_anchor_resisted_but_capacity_threshold_restraint_failed",
            },
            "matched_finding": "Arm B removed the broad unresolved inventory but still emitted both predefined capacity responses as residual dependencies, so the quiet control failed in both arms.",
        },
        {
            "case_id": "r4h2-case02-serialized-essay-pilot",
            "target_role": "governed_pending_restraint_control_without_matching_prior_gap_anchor",
            "target": {"unresolved_matter": "quiet", "reopen_condition": "quiet"},
            "arm_a": {
                "surface_states": states[("r4h2-case02-serialized-essay-pilot", "A_frozen_v2_semantic_distinction")],
                "false_positive_records": 0,
                "correct_zero_surfaces": 2,
                "genuine_target_recovered": None,
                "all_surface_targets_passed": True,
                "verdict": "quiet_control_passed",
            },
            "arm_b": {
                "surface_states": states[("r4h2-case02-serialized-essay-pilot", "B_frozen_residual_task")],
                "false_positive_records": 1,
                "correct_zero_surfaces": 1,
                "genuine_target_recovered": None,
                "all_surface_targets_passed": False,
                "verdict": "scheduled_board_decision_misread_as_residual_dependency",
            },
            "matched_finding": "Arm A was correctly quiet. Arm B converted the fixed evidence window and October board choice into a residual dependency despite no matching prior gap anchor.",
        },
        {
            "case_id": "r4h2-case03-research-workspace-service",
            "target_role": "genuine_recurring_ownership_funding_capacity_gap",
            "target": {"unresolved_matter": "supported", "reopen_condition": "quiet"},
            "arm_a": {
                "surface_states": states[("r4h2-case03-research-workspace-service", "A_frozen_v2_semantic_distinction")],
                "false_positive_records": 2,
                "correct_zero_surfaces": 0,
                "genuine_target_recovered": True,
                "all_surface_targets_passed": False,
                "verdict": "genuine_gap_recovered_with_duplicate_and_incident_false_positives",
            },
            "arm_b": {
                "surface_states": states[("r4h2-case03-research-workspace-service", "B_frozen_residual_task")],
                "false_positive_records": 1,
                "correct_zero_surfaces": 0,
                "genuine_target_recovered": True,
                "all_surface_targets_passed": False,
                "verdict": "genuine_gap_recovered_but_duplicated_as_future_dependency",
            },
            "matched_finding": "Both arms recovered the post-June ownership and funding gap from distributed evidence. Arm B removed the governed incident false positive but still duplicated the same current gap on the reopen surface.",
        },
        {
            "case_id": "r4h2-case04-shared-language-course",
            "target_role": "genuine_later_premise_breaking_dependency",
            "target": {"unresolved_matter": "quiet", "reopen_condition": "supported"},
            "arm_a": {
                "surface_states": states[("r4h2-case04-shared-language-course", "A_frozen_v2_semantic_distinction")],
                "false_positive_records": 1,
                "correct_zero_surfaces": 1,
                "genuine_target_recovered": True,
                "all_surface_targets_passed": False,
                "verdict": "dependency_recovered_with_governed_enrollment_threshold_false_positive_and_incomplete_evidence",
            },
            "arm_b": {
                "surface_states": states[("r4h2-case04-shared-language-course", "B_frozen_residual_task")],
                "false_positive_records": 1,
                "correct_zero_surfaces": 0,
                "genuine_target_recovered": True,
                "all_surface_targets_passed": False,
                "verdict": "dependency_recovered_with_assistant_proposal_false_positive_and_incomplete_evidence",
            },
            "matched_finding": "Both arms found the Board-designation dependency but cited only two of six decisive aliases. Arm A added the governed enrollment threshold; Arm B instead elevated assistant legal-review suggestions into a present decision gap.",
        },
    ]
    review: dict[str, Any] = {
        "schema_version": "lolla.r4_matched_residual_execution_source_review.v2",
        "status": "residual_task_repair_insufficient",
        "date": "2026-07-14",
        "run_id": contract["run_id"],
        "semantic_judgment_owner": "human_source_first_review_after_terminal_execution",
        "raw_checkpoint_commit": RAW_CHECKPOINT_COMMIT,
        "raw_checkpoint_preceded_review": True,
        "target_opened_only_after_terminal_execution_and_raw_checkpoint": True,
        "target_visible_to_provider": False,
        "target_accessible_to_runner": False,
        "target_sha256": TARGET_SHA256,
        "target_review_sha256": TARGET_REVIEW_SHA256,
        "scalar_quality_score": None,
        "record_reviews": records,
        "case_reviews": cases,
        "dimensions": [
            {
                "dimension": "mechanical_execution_and_attribution",
                "verdict": "pass",
                "finding": "All eight exact requests completed once through Google with the allowed served model, strict local admission, zero reasoning tokens, exact usage and cost, and no retry or prohibited call.",
            },
            {
                "dimension": "false_positive_restraint",
                "verdict": "fail",
                "finding": "Arm B reduced false-positive records from seven to five but passed only two of six quiet surface targets. It failed both restraint cases and repeated capacity-threshold and scheduled-decision errors.",
            },
            {
                "dimension": "genuine_residual_sensitivity",
                "verdict": "pass_with_evidence_precision_qualifications",
                "finding": "Both arms recovered the Case 03 continuing service gap and the Case 04 Board-designation dependency. The Case 04 records omit decisive credit-impact and no-replacement aliases.",
            },
            {
                "dimension": "zero_versus_ambiguity_behavior",
                "verdict": "fail_quiet_surface_restraint",
                "finding": "No arm returned ambiguity, which the targets did not require. Arm A completed three of six quiet surfaces at zero; Arm B completed only two of six because it emitted records on four quiet surfaces.",
            },
            {
                "dimension": "evidence_precision",
                "verdict": "fail",
                "finding": "Many aliases prove the adopted safeguard or decision machinery rather than a remainder. Both Case 04 dependency records omit aliases establishing recognized-credit impact and absence of replacement authority; Arm B's Case 04 gap cites assistant turns only.",
            },
            {
                "dimension": "semantic_surface_placement",
                "verdict": "fail",
                "finding": "Both arms duplicate the Case 03 current decision gap onto the reopen surface. Arm B additionally places a non-adopted legal-review suggestion on the Case 04 unresolved surface.",
            },
            {
                "dimension": "speaker_and_modal_fidelity",
                "verdict": "mixed",
                "finding": "Core user-owned positive records are mostly faithful. Several false positives elevate assistant suggestions, merge distinct owners, strengthen can into mandate, or broaden Board withdrawal into any status change.",
            },
            {
                "dimension": "prior_anchoring_resistance",
                "verdict": "mixed",
                "finding": "Arm B suppresses Case 01's broad unresolved inventory and both arms find positives absent from the priors. Arm B nevertheless invents a scheduled-decision dependency in Case 02 without a matching prior anchor.",
            },
            {
                "dimension": "long_context_and_late_evidence_use",
                "verdict": "mixed",
                "finding": "Both arms use late aliases e023 through e027 and recover both genuine targets. They repeatedly omit decisive final adoption, authority, or continuity aliases when assigning false-positive or incomplete records.",
            },
            {
                "dimension": "operational_cost_and_custody",
                "verdict": "pass",
                "finding": "Exact provider-reported cost was $0.01408165, below every case ceiling and the $0.12 total ceiling. Raw bytes, request and response hashes, generation identities, and authorization consumption are preserved.",
            },
        ],
        "decision_matrix_application": {
            "category": "residual_task_repair_insufficient",
            "residual_passed_all_restraint_gates": False,
            "residual_preserved_both_genuine_targets": True,
            "residual_repeated_governed_pending_false_positives": True,
            "residual_materially_worse_than_v2_overall": False,
            "mechanical_or_custody_failure": False,
            "why": "The residual arm preserves both genuine targets and removes some broad inventory, but it still emits governed capacity thresholds, a scheduled board decision, a duplicate of the current Case 03 gap, and an assistant-proposed legal question. That is the frozen repair-insufficient condition.",
            "evidence_against_a_stronger_negative": "Arm B reduces total false-positive records from seven to five, quiets the broad Case 01 unresolved surface, removes the Case 03 incident false positive, and preserves both genuine targets. The result is insufficient rather than overcorrected, regressed overall, or mechanically unevaluable.",
        },
        "decision": "residual_task_repair_insufficient",
        "limitations": [
            "Cases 01 and 02 include recent summaries of adopted controls, so this is not a pure test of recovering every fact only from distant context.",
            "The four conversations are simulated reliability evidence, not real-user product evidence.",
            "One matched execution cannot establish model reliability, production readiness, or product usefulness.",
            "Record-count reduction is descriptive only and is not a scalar quality score.",
        ],
    }
    review["result_sha256"] = value_sha256(review)
    return review


def _evidence_paths(contract: Mapping[str, Any]) -> list[Path]:
    paths: set[Path] = {
        CONTRACT,
        TARGET,
        TARGET_REVIEW,
        RUNNER,
        Path(__file__),
        Path(raw_seal.__file__),
        RAW_MANIFEST,
        AUTHORIZATION_CONSUMPTION,
        SOURCE_REVIEW,
        RUN_RESULT,
        ROOT / contract["execution_envelope"]["execution_manifest_path"],
        ROOT
        / "research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/leakage-audit.json",
        ROOT
        / "research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14/freeze-manifest.json",
        ROOT / "scripts/evals/build_r4_provider_free_corpus_replay.py",
        ROOT / "tests/test_r4_matched_holdout_v2_execution_a1.py",
        ROOT / "tests/test_r4_provider_free_corpus_replay.py",
    }
    paths.update(OUTPUT.glob("call-*"))
    for case in contract["cases"]:
        paths.update(
            {
                ROOT / case["source_path"],
                ROOT / case["prior_path"],
                ROOT / case["packet_path"],
                ROOT / case["source_registry_path"],
                ROOT / case["matched_request_delta_path"],
            }
        )
        for arm in case["arms"].values():
            paths.add(ROOT / arm["context_manifest_path"])
            paths.add(ROOT / arm["request_preview_path"])
    return sorted(paths, key=_relative)


def _build_manifest(review: Mapping[str, Any]) -> dict[str, Any]:
    contract = validate_contract(CONTRACT)
    files = []
    for path in _evidence_paths(contract):
        if not path.is_file():
            raise R4MatchedExecutionA1CloseoutError(
                f"evidence file missing: {_relative(path)}"
            )
        files.append(
            {
                "path": _relative(path),
                "sha256": _file_sha(path),
                "utf8_bytes": len(path.read_bytes()),
            }
        )
    raw = _load(RAW_MANIFEST)
    manifest: dict[str, Any] = {
        "schema_version": "lolla.r4_matched_residual_execution_evidence_manifest.v2",
        "status": "terminal_execution_and_source_first_review_preserved",
        "date": "2026-07-14",
        "run_id": contract["run_id"],
        "canonical_base_commit": CANONICAL_BASE_COMMIT,
        "raw_checkpoint_commit": RAW_CHECKPOINT_COMMIT,
        "contract_sha256": CONTRACT_SHA256,
        "authorization_sha256": raw_seal.AUTHORIZATION_SHA256,
        "authorization_consumed": True,
        "raw_evidence_manifest_sha256": raw["manifest_sha256"],
        "source_first_review_sha256": review["result_sha256"],
        "files": files,
        "file_count": len(files),
        "provider_calls": 8,
        "provider_reported_cost_usd": TOTAL_COST_USD,
        "request_response_inventory": [
            {
                "ordinal": row["ordinal"],
                "case_id": row["case_id"],
                "arm": row["arm"],
                "request_body_sha256": row["request_body_sha256"],
                "raw_response_sha256": row["raw_response_sha256"],
                "generation_id": row["generation_id"],
            }
            for row in raw["calls"]
        ],
        "temporary_authorization_committed": False,
        "provider_secret_committed": False,
    }
    manifest["manifest_sha256"] = value_sha256(manifest)
    return manifest


def _build_closeout(
    review: Mapping[str, Any], manifest: Mapping[str, Any]
) -> dict[str, Any]:
    raw = _load(RAW_MANIFEST)
    closeout: dict[str, Any] = {
        "schema_version": "lolla.r4_matched_residual_execution_closeout.v2",
        "status": "execution_complete_residual_task_repair_insufficient",
        "date": "2026-07-14",
        "run_id": "lolla-r4-matched-residual-holdout-v2",
        "canonical_base_commit": CANONICAL_BASE_COMMIT,
        "raw_checkpoint_commit": RAW_CHECKPOINT_COMMIT,
        "contract_sha256": CONTRACT_SHA256,
        "authorization_sha256": raw_seal.AUTHORIZATION_SHA256,
        "authorization_consumed": True,
        "provider_calls": 8,
        "provider_calls_completed": 8,
        "provider_reported_cost_usd": TOTAL_COST_USD,
        "conservative_estimated_cost_usd": ESTIMATED_COST_USD,
        "estimate_minus_actual_usd": round(
            ESTIMATED_COST_USD - TOTAL_COST_USD, 12
        ),
        "hard_provider_reported_cost_per_case_usd": 0.03,
        "hard_provider_reported_cost_total_usd": 0.12,
        "case_costs_usd": raw["case_costs_usd"],
        "call_observations": raw["calls"],
        "requested_model": "google/gemini-3.1-flash-lite",
        "served_models": ["google/gemini-3.1-flash-lite"],
        "served_providers": ["Google"],
        "operator_recheck_before_transport": {
            "date": "2026-07-14",
            "status": "exact_operator_remained_available_within_frozen_price_controls",
            "official_sources": [
                "https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite",
                "https://ai.google.dev/gemini-api/docs/changelog",
                "https://openrouter.ai/google/gemini-3.1-flash-lite-20260507/providers",
                "https://openrouter.ai/docs/guides/routing/provider-selection",
                "https://openrouter.ai/docs/guides/features/structured-outputs",
                "https://openrouter.ai/docs/guides/best-practices/reasoning-tokens",
                "https://openrouter.ai/docs/cookbook/administration/usage-accounting",
            ],
            "frozen_contract_modified": False,
        },
        "mechanical_conclusion": {
            "all_eight_calls_completed": True,
            "stop_on_first_failure_triggered": False,
            "strict_json_and_local_admission_passed": True,
            "operator_attribution_passed": True,
            "reasoning_exclusion_passed": True,
            "raw_terminal_bytes_preserved_before_review": True,
            "raw_execution_committed_before_review": True,
        },
        "preserved_boundaries": {
            "automatic_retry_performed": False,
            "manual_retry_performed": False,
            "semantic_retry_performed": False,
            "fallback_performed": False,
            "response_healing_performed": False,
            "model_substitution_performed": False,
            "relationship_call_performed": False,
            "evaluator_call_performed": False,
            "embedding_call_performed": False,
            "graph_call_performed": False,
            "pipeline_call_performed": False,
            "runtime_call_performed": False,
            "publication_performed": False,
            "scalar_quality_score_created": False,
        },
        "source_first_review_sha256": review["result_sha256"],
        "evidence_manifest_sha256": manifest["manifest_sha256"],
        "scalar_quality_score": None,
        "decision": "residual_task_repair_insufficient",
        "decision_summary": "The residual-task arm preserved both genuine targets and removed some broad inventory, but it failed both quiet controls and repeated governed capacity, scheduled-decision, duplicate-gap, and assistant-proposal false positives.",
        "verification": {
            "exact_contract_validation": "passed",
            "raw_execution_validation": "passed",
            "source_first_closeout_validation": "passed",
            "focused_tests": {"passed": 111, "failed": 0},
            "full_repository_suite": {
                "passed": 4939,
                "failed": 0,
                "subtests_passed": 93,
                "warnings": 1,
                "warning_scope": "pre_existing_datetime_utcnow_deprecation",
            },
            "frozen_replay": {
                "case_count": 12,
                "case_artifact_links": 543,
                "unique_frozen_json_artifacts": 400,
            },
            "changed_execution_json_parsed": 22,
            "changed_python_compilation": "passed",
            "git_diff_check": "passed",
            "added_material_secret_pattern_hits": 0,
            "git_object_integrity": "passed",
            "temporary_authorization_path_absent": True,
        },
        "additional_provider_call_authorized": False,
        "this_execution_may_be_retried": False,
        "runtime_or_graph_integration_authorized": False,
        "r5_authorized": False,
        "product_usefulness_established": False,
        "next_causal_question": "Before any integration or another paid run, decide provider-free whether the remaining failure is primarily paired two-surface completion pressure or whether the R4 reader architecture should stop. Do not combine that question with a model, prior-authority, runtime, graph, or relationship change.",
    }
    closeout["result_sha256"] = value_sha256(closeout)
    return closeout


def build() -> dict[str, Any]:
    review = _build_review()
    _write(SOURCE_REVIEW, review)
    manifest = _build_manifest(review)
    _write(EVIDENCE_MANIFEST, manifest)
    closeout = _build_closeout(review, manifest)
    _write(CLOSEOUT, closeout)
    return closeout


def validate() -> dict[str, Any]:
    expected_review = _build_review()
    if not SOURCE_REVIEW.is_file() or SOURCE_REVIEW.read_bytes() != _render(
        expected_review
    ):
        raise R4MatchedExecutionA1CloseoutError("source-first review drifted")
    expected_manifest = _build_manifest(expected_review)
    if not EVIDENCE_MANIFEST.is_file() or EVIDENCE_MANIFEST.read_bytes() != _render(
        expected_manifest
    ):
        raise R4MatchedExecutionA1CloseoutError("evidence manifest drifted")
    expected_closeout = _build_closeout(expected_review, expected_manifest)
    if not CLOSEOUT.is_file() or CLOSEOUT.read_bytes() != _render(
        expected_closeout
    ):
        raise R4MatchedExecutionA1CloseoutError("execution closeout drifted")
    for path, field in (
        (SOURCE_REVIEW, "result_sha256"),
        (EVIDENCE_MANIFEST, "manifest_sha256"),
        (CLOSEOUT, "result_sha256"),
    ):
        value = _load(path)
        if value[field] != value_sha256(_without(value, field)):
            raise R4MatchedExecutionA1CloseoutError(
                f"self-hash drifted: {_relative(path)}"
            )
    return expected_closeout


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    result = validate() if args.validate_only else build()
    print(
        json.dumps(
            {
                "status": result["status"],
                "provider_calls": result["provider_calls"],
                "provider_reported_cost_usd": result[
                    "provider_reported_cost_usd"
                ],
                "decision": result["decision"],
                "additional_provider_call_authorized": result[
                    "additional_provider_call_authorized"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
