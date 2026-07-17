from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-triage-supply-plan-v0.md"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-triage-supply-plan-v0/review.json"
)
PR190_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-generated-read-brief-two-case-pattern-review-v0.md"
)
PR190_REVIEW = (
    REPO_ROOT
    / "reviews/codex-assisted/"
    "decision-work-generated-read-brief-two-case-pattern-review-v0/review.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    "decision-work-automatic-semantic-supply-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)
REQUIRED_ALLOWED_ROUTES = {
    "source_depth_insufficient",
    "private_context_required",
    "high_overtrust_risk",
    "domain_review_recommended",
    "legal_or_compliance_review_recommended",
    "relationship_or_governance_sensitive",
    "lost_value_risk_unresolved",
    "agent_inspection_only",
    "not_ready_for_user_surface",
    "runtime_attachment_blocked",
}
REQUIRED_FORBIDDEN_ROUTES = {
    "good_answer",
    "bad_answer",
    "approved",
    "certified",
    "safe_to_act",
    "correct_advice",
    "lolla_improved_decision",
    "human_validated",
    "product_proof",
    "agent_action_authorized",
    "automatic_action_authorized",
}
REQUIRED_STATUSES = {
    "ready_for_offline_triage_generation",
    "deferred_missing_rendered_brief",
    "deferred_missing_brief_supply",
    "blocked_intake_not_accepted",
    "blocked_brief_supply_not_ready",
    "blocked_missing_source_refs",
    "blocked_missing_uncertainty",
    "blocked_privacy_risk",
    "blocked_authority_claim",
    "requires_operator_repair",
}


def _review() -> dict:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def test_review_json_schema_inputs_and_gate() -> None:
    review = _review()

    assert (
        review["schema_version"]
        == "lolla.decision_work_generated_read_triage_supply_plan.v0"
    )
    assert "generated_interpretation_read_json" in review[
        "allowed_triage_supply_inputs"
    ]
    assert "pr182_intake_result_json" in review["allowed_triage_supply_inputs"]
    assert "pr186_brief_supply_json" in review["allowed_triage_supply_inputs"]
    assert "generated_read_rendered_brief_markdown" in review[
        "allowed_triage_supply_inputs"
    ]
    assert review["decision_gate"] == (
        "proceed_to_generated_read_triage_supply_adapter"
    )
    assert (
        review["recommended_next_pr"]
        == "PR192 Decision Work Generated Read Triage Supply Adapter v0"
    )


def test_route_categories_separate_attention_routing_from_quality_labels() -> None:
    review = _review()

    assert REQUIRED_ALLOWED_ROUTES.issubset(set(review["route_categories_allowed"]))
    assert REQUIRED_FORBIDDEN_ROUTES.issubset(
        set(review["route_categories_forbidden"])
    )
    assert not REQUIRED_FORBIDDEN_ROUTES.intersection(
        set(review["route_categories_allowed"])
    )
    assert "answer_quality_judgment" in review["blocked_fields"]
    assert "advice_correctness_judgment" in review["blocked_fields"]
    assert "resolver_ref_usability" in review["blocked_fields"]


def test_statuses_and_requirements_are_conservative() -> None:
    review = _review()

    assert REQUIRED_STATUSES.issubset(set(review["planned_statuses"]))
    assert review["required_source_refs"]["generated_read"] is True
    assert review["required_source_refs"]["intake_result"] is True
    assert review["required_source_refs"]["brief_supply"] is True
    assert review["required_source_refs"]["rendered_brief"] is True
    assert review["required_source_refs"]["content_included"] is False
    assert review["required_uncertainty"]["field_uncertainty_required"] is True
    assert review["required_uncertainty"]["missing_uncertainty_blocks"] is True
    assert review["privacy_requirements"]["raw_private_content_included"] is False
    assert review["privacy_requirements"]["provider_text_included"] is False
    assert review["privacy_requirements"]["local_absolute_paths_included"] is False


def test_custody_flags_and_non_claims_remain_closed() -> None:
    review = _review()
    custody = review["custody_requirements"]

    assert custody["model_calls"] == 0
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["archive_mutated"] is False
    assert custody["runtime_behavior_changed"] is False
    assert custody["triage_generated"] is False
    assert custody["resolver_refs_marked_usable"] is False
    assert custody["runtime_sidecar_updated"] is False
    assert custody["product_proof"] is False
    assert custody["human_validated"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["automatic_action_authorized"] is False
    non_claims = set(review["non_claims"])
    assert "plan_does_not_generate_triage" in non_claims
    assert "plan_does_not_mark_resolver_refs_usable" in non_claims
    assert "plan_does_not_update_runtime_sidecars" in non_claims
    assert "plan_does_not_prove_lolla_improved_the_decision" in non_claims


def test_doc_answers_triage_supply_questions_and_gate() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")

    assert "# Decision Work Generated Read Triage Supply Plan v0" in text
    assert "generated interpretation read JSON" in text
    assert "PR182 intake result JSON" in text
    assert "PR186 generated-read brief supply JSON" in text
    assert "generated-read rendered brief Markdown" in text
    assert "Allowed Routing Fields" in text
    assert "Evidence-Only And Blocked Fields" in text
    assert "Forbidden route concepts" in text
    assert "They are not answer-quality labels" in text
    assert "proceed_to_generated_read_triage_supply_adapter" in text
    assert "PR192 Decision Work Generated Read Triage Supply Adapter v0" in text
    assert "does not generate triage" in text


def test_discoverability_docs_reference_pr191() -> None:
    expected = "Decision Work Generated Read Triage Supply Plan"
    for path in (
        DOC_PATH,
        PR190_DOC,
        PRD_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        assert expected in path.read_text(encoding="utf-8"), str(path)


def test_pr191_docs_pass_product_delta_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR190_DOC,
            PR190_REVIEW,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pr191_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        REVIEW_PATH,
        PR190_DOC,
        PR190_REVIEW,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
