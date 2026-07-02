from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.md"
)
PR138_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-enriched-pattern-review-v0/review.json"
)
PR138_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enriched-pattern-review-v0.md"
)
PR134_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-read-comparison-v0/review.json"
)
PRD_PATH = REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"

SCHEMA_VERSION = "lolla.decision_work_brief_enrichment_rules_contract.v0"
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "contract_metadata",
    "custody_policy",
    "allowed_user_facing_fields",
    "evidence_only_fields",
    "forbidden_fields",
    "enrichment_section_rules",
    "source_and_uncertainty_rules",
    "non_claim_rules",
    "builder_requirements",
    "future_review_requirements",
}
EXPECTED_ALLOWED_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "what_the_final_answer_does_not_prove",
}
EXPECTED_EVIDENCE_ONLY_FIELDS = {
    "live_options",
    "abandoned_or_rejected_options",
    "noisy_friction",
    "lost_value",
    "user_values_or_priorities",
    "stakeholder_obligations",
    "assistant_influence_on_user_framing",
    "sycophancy_or_over_accommodation_risk",
    "safe_to_show_user",
    "safe_for_agent_inspection_only",
}
REQUIRED_FORBIDDEN_CONCEPTS = {
    "answer_quality_score",
    "improvement_score",
    "winner",
    "approval",
    "certification",
    "agent_action_authorization",
    "product_proof",
    "human_validated_without_actual_human_review",
}
REQUIRED_CUSTODY_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "answer_quality_scored",
    "agent_action_authorized",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
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


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_contract_json_parses_and_has_expected_top_level_fields() -> None:
    contract = _contract()

    assert contract["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(contract)
    assert contract["contract_metadata"]["source_gate_outcome"] == (
        "proceed_to_enrichment_rules_contract"
    )


def test_pr139_follows_pr138_gate() -> None:
    pr138 = json.loads(PR138_REVIEW_PATH.read_text(encoding="utf-8"))

    assert pr138["decision_gate"]["outcome"] == (
        "proceed_to_enrichment_rules_contract"
    )
    assert CONTRACT_PATH.exists()


def test_custody_policy_is_conservative() -> None:
    custody = _contract()["custody_policy"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["rules_are_provisional"] is True


def test_allowed_user_facing_fields_match_pr138_stable_fields() -> None:
    allowed = _contract()["allowed_user_facing_fields"]

    assert {field["field_name"] for field in allowed} == EXPECTED_ALLOWED_FIELDS
    for field in allowed:
        assert field["source_refs_required"] is True
        assert field["source_status_required"] is True
        assert field["uncertainty_required"] is True
        assert field["interpretation_basis_required"] is True
        assert field["privacy_limit_required"] is True
        assert field["human_review_required_flag_required"] is True
        assert field["must_not_be_used_as_quality_label"] is True

    by_name = {field["field_name"]: field for field in allowed}
    assert by_name["likely_starting_direction"]["must_show_uncertainty"] is True
    assert by_name["useful_friction"]["must_be_descriptive_not_scoring"] is True
    assert "must not say Lolla caused" in by_name[
        "revised_direction_or_action_consequence"
    ]["field_specific_rule"]


def test_evidence_only_fields_include_high_risk_interpretation_fields() -> None:
    evidence_only = _contract()["evidence_only_fields"]

    assert {field["field_name"] for field in evidence_only} == (
        EXPECTED_EVIDENCE_ONLY_FIELDS
    )
    for field in evidence_only:
        assert field["reason"]


def test_forbidden_fields_cover_authority_and_verdict_concepts() -> None:
    forbidden = _contract()["forbidden_fields"]

    assert {field["concept"] for field in forbidden} >= REQUIRED_FORBIDDEN_CONCEPTS
    for field in forbidden:
        assert field["rule"]


def test_enrichment_section_rules_require_uncertainty_and_non_claims() -> None:
    rules = _contract()["enrichment_section_rules"]

    assert rules["heading"] == "What the interpretation adds"
    assert rules["max_paragraphs"] <= 3
    assert rules["must_include_uncertainty"] is True
    assert rules["must_include_non_claim"] is True
    assert rules["must_not_include_field_dump"] is True
    assert rules["must_not_say_lolla_caused_everything"] is True
    assert rules["must_not_say_interpretation_is_more_correct"] is True


def test_source_uncertainty_and_non_claim_rules_are_required() -> None:
    source_rules = _contract()["source_and_uncertainty_rules"]
    non_claims = _contract()["non_claim_rules"]

    for key in {
        "source_refs_required",
        "source_status_required",
        "uncertainty_required",
        "interpretation_basis_required",
        "privacy_limit_required",
        "human_review_required_required",
        "must_not_be_used_as_quality_label_required",
    }:
        assert source_rules[key] is True

    assert "not_product_proof" in non_claims["must_include"]
    assert "not_answer_quality_score" in non_claims["must_include"]
    assert "not_agent_action_authorization" in non_claims["must_include"]
    assert "enrichment_does_not_prove_lolla_improved_the_decision" in non_claims[
        "must_keep_near_enrichment"
    ]


def test_builder_requirements_preserve_offline_boundary() -> None:
    requirements = _contract()["builder_requirements"]

    assert requirements["must_accept_original_rendered_brief"] is True
    assert requirements["must_accept_interpretation_read"] is True
    assert requirements["must_accept_enrichment_rules_contract"] is True
    assert requirements["must_output_separate_enriched_markdown"] is True
    assert requirements["must_preserve_original_brief_unchanged"] is True
    assert requirements["must_include_only_allowed_user_facing_fields"] is True
    assert requirements["must_preserve_non_claims"] is True
    assert requirements["must_not_call_models"] is True
    assert requirements["must_not_invoke_runtime"] is True
    assert requirements["must_not_run_lolla"] is True
    assert requirements["must_not_mutate_archives"] is True
    assert requirements["must_reject_same_input_output_path"] is True
    assert requirements["must_reject_non_conservative_interpretation_read"] is True


def test_future_review_requirements_do_not_allow_runtime_shortcut() -> None:
    review = _contract()["future_review_requirements"]

    assert review["must_compare_builder_output_to_hand_built_examples"] is True
    assert review["must_check_readability"] is True
    assert review["must_check_uncertainty_preservation"] is True
    assert review["must_check_non_claim_preservation"] is True
    assert review["must_check_evidence_only_fields_are_not_in_main_body"] is True
    assert review["must_not_recommend_runtime_integration_from_builder_output_alone"] is True


def test_contract_docs_and_related_reviews_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [CONTRACT_PATH, DOC_PATH, PR138_REVIEW_PATH, PR138_DOC_PATH, PR134_REVIEW_PATH, PRD_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_contract_docs_and_tests_do_not_include_private_markers() -> None:
    for path in [CONTRACT_PATH, DOC_PATH, Path(__file__)]:
        text = _text(path)
        for marker in PRIVACY_MARKERS:
            assert marker not in text
