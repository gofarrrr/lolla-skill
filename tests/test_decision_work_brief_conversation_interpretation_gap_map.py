from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-conversation-interpretation-gap-map-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-conversation-interpretation-gap-map-v0.md"
)
PR126_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-expansion-runtime-decision-gate-v0/review.json"
)
PR126_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-expansion-runtime-decision-gate-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_brief_conversation_interpretation_gap_map.v0"
EXPECTED_CASES = {
    "ceo-remove-founding-cofounder",
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
}
REQUIRED_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "live_options",
    "abandoned_or_rejected_options",
    "option_status",
    "decision_thresholds",
    "stop_rules",
    "evidence_gates",
    "conversation_turn_depth",
    "user_provided_context",
    "pasted_documents_or_external_context",
    "assistant_influence_on_user_framing",
    "user_changed_mind_during_conversation",
    "assistant_sycophancy_or_over-accommodation_risk",
    "unresolved_threads",
    "dropped_threads",
    "premortem_or_counterfactual_pressure",
    "alternative_frames_considered",
    "user_values_or_priorities",
    "stakeholder_obligations",
    "relationship_or_political_constraints",
    "timing_or_runway_constraints",
    "operational_capacity_constraints",
    "legal_compliance_or_safety_constraints",
    "real_world_unknowns",
    "unknown_unknowns_or_context_not_available_to_model",
    "useful_friction",
    "noisy_friction",
    "lost_value",
    "overcorrection_risk",
    "false_precision_risk",
    "generic_caution_risk",
    "momentum_or_ambition_loss",
    "what_the_final_answer_does_not_prove",
    "source_refs",
    "private_context_available",
    "redacted_or_not_checked_in",
    "local_private_only",
    "safe_to_show_user",
    "safe_for_agent_inspection_only",
    "requires_human_review",
    "requires_llm_interpretation",
    "deterministic_only_metadata",
}
ALLOWED_AVAILABILITY = {
    "clear_from_checked_in_safe_artifacts",
    "partial_from_checked_in_safe_artifacts",
    "available_only_in_local_private_context",
    "inferable_only_by_llm",
    "requires_human_review",
    "not_currently_captured",
    "unsafe_to_check_in",
    "not_relevant_for_this_case",
    "unclear",
}
ALLOWED_HANDLING = {
    "deterministic_metadata_only",
    "llm_interpretation_required",
    "human_review_required",
    "local_private_read_required",
    "safe_checked_in_summary_allowed",
    "should_not_be_exported",
    "source_refs_required",
}
ALLOWED_LOCAL_PRIVATE_STATUS = {
    "not_attempted",
    "completed_read_only",
    "unavailable_missing_artifacts",
    "blocked_for_privacy",
    "blocked_for_safety",
    "not_needed_for_gap_map",
}
ALLOWED_NEXT_STEPS = {
    "define_interpretation_target_contract",
    "run_more_local_private_gap_checks",
    "patch_brief_schema",
    "patch_packet_builder",
    "patch_renderer_language",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "custody_flags",
    "reviewed_cases",
    "target_field_inventory",
    "per_case_gap_map",
    "cross_case_gap_summary",
    "product_impact_assessment",
    "recommended_next_step",
    "non_claims",
}
REQUIRED_CASE_FIELDS = {
    "case_id",
    "rendered_brief_ref",
    "review_json_ref",
    "local_private_review_status",
    "field_coverage",
    "most_important_missing_fields",
    "fields_that_need_llm_interpretation",
    "fields_that_need_human_review",
    "fields_available_only_privately",
    "checked_in_safe_limitations",
    "product_consequence",
}
REQUIRED_CUSTODY_FALSE_FIELDS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "broad_judge_used",
    "automatic_labels_created",
    "raw_private_content_checked_in",
    "raw_private_content_included",
    "provider_text_checked_in",
    "provider_text_included",
    "local_absolute_paths_included",
}
REQUIRED_NON_CLAIMS = {
    "review_is_codex_assisted",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "gap_map_is_not_runtime_extraction",
    "gap_map_does_not_change_live_lolla_schema",
    "clean_artifacts_do_not_imply_good_advice",
    "missingness_is_not_negative_semantic_evidence",
    "future_human_review_required",
    "future_contract_required_before_runtime_planning",
}
FORBIDDEN_FIELD_NAMES = {
    "safe_for_" + "agent_use",
    "approved",
    "approval",
    "approval_status",
    "certified",
    "passed",
    "pass",
    "pass_fail",
    "score",
    "quality_score",
    "answer_quality_score",
    "improvement_score",
    "decision_quality_score",
    "confidence_score",
    "judge_score",
    "rating",
    "winner",
    "llm_judge_winner",
}
PRIVACY_MARKERS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
RUNTIME_INTEGRATION_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_brief_runtime.py",
    REPO_ROOT / "scripts/evals/integrate_decision_work_brief_runtime.py",
    REPO_ROOT / "scripts/evals/build_decision_work_brief_batch.py",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(_walk_keys(child))
    return keys


def test_review_json_has_expected_schema_and_top_level_fields() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(review)
    assert review["review_metadata"]["review_mode"] == (
        "codex_assisted_provisional_checked_in_safe_gap_map"
    )
    assert review["review_metadata"]["case_count"] == 3


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True


def test_all_three_expected_cases_are_reviewed_and_refs_resolve() -> None:
    cases = _review()["reviewed_cases"]

    assert {case["case_id"] for case in cases} == EXPECTED_CASES
    assert len(cases) == 3
    for case in cases:
        assert REQUIRED_CASE_FIELDS <= set(case)
        assert case["local_private_review_status"] in ALLOWED_LOCAL_PRIVATE_STATUS
        assert case["field_coverage"]
        assert case["most_important_missing_fields"]
        assert case["fields_that_need_llm_interpretation"]
        assert case["fields_that_need_human_review"]
        assert case["checked_in_safe_limitations"]
        assert (REPO_ROOT / case["rendered_brief_ref"]).exists()
        assert (REPO_ROOT / case["review_json_ref"]).exists()


def test_target_field_inventory_includes_required_fields_with_classifications() -> None:
    inventory = _review()["target_field_inventory"]

    assert {field["field_name"] for field in inventory} == REQUIRED_FIELDS
    for field in inventory:
        assert field["availability_classification"] in ALLOWED_AVAILABILITY
        assert field["desired_handling"] in ALLOWED_HANDLING
        for handling in field.get("supporting_handling", []):
            assert handling in ALLOWED_HANDLING
        assert field["field_group"]
        assert field["why_it_matters"]


def test_cross_case_summary_names_repeated_gaps_and_ownership_boundary() -> None:
    summary = _review()["cross_case_gap_summary"]

    assert summary["repeated_contract_need"] is True
    assert "option_status" in summary["repeated_missing_or_weak_fields"]
    assert "lost_value" in summary["repeated_missing_or_weak_fields"]
    assert "source_refs" in summary["deterministic_code_should_own"]
    assert "requires_llm_interpretation" in summary["deterministic_code_should_own"]
    assert "likely_starting_direction" in summary["requires_llm_interpretation"]
    assert "stakeholder_obligations" in summary["requires_human_review"]


def test_recommended_next_step_is_allowed_and_gates_to_pr128() -> None:
    next_step = _review()["recommended_next_step"]

    assert next_step["outcome"] in ALLOWED_NEXT_STEPS
    assert next_step["outcome"] == "define_interpretation_target_contract"
    assert set(next_step["allowed_outcomes"]) == ALLOWED_NEXT_STEPS
    assert next_step["runtime_integration_recommended"] is False


def test_required_non_claims_exist() -> None:
    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])


def test_review_does_not_claim_product_proof_or_runtime_readiness() -> None:
    text = json.dumps(_review(), sort_keys=True).lower()

    forbidden_claims = (
        "is product proof",
        "counts as product proof",
        "human validated",
        "answer-quality score",
        "agent action authorized",
        "runtime integration recommended",
        "clean artifacts prove good advice",
    )
    for claim in forbidden_claims:
        assert claim not in text


def test_checked_in_files_have_no_local_paths_or_privacy_markers() -> None:
    text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )

    assert "/" + "tmp" + "/" not in text
    for marker in PRIVACY_MARKERS:
        assert marker not in text


def test_forbidden_authority_or_score_fields_do_not_appear() -> None:
    keys = {key.lower() for key in _walk_keys(_review())}

    assert not keys.intersection(FORBIDDEN_FIELD_NAMES)
    assert not any(key.endswith("_score") and key != "not_a_score" for key in keys)


def test_no_runtime_integration_or_skill_surface_changes() -> None:
    for path in RUNTIME_INTEGRATION_FILES:
        assert not path.exists()

    result = subprocess.run(
        ["git", "status", "--short", "--", "SKILL.md", "scripts/skill"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_pr127_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, REVIEW_PATH, PR126_DOC_PATH, PR126_REVIEW_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
