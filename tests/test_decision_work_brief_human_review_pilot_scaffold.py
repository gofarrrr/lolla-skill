from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-pilot-scaffold-v0.md"
)
TEMPLATE_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-human-review-response-template-v0.json"
)
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-human-review-pilot-scaffold-v0/review.json"
)
INTAKE_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-human-review-intake-plan-v0/review.json"
)
SCAFFOLD_SCHEMA = "lolla.decision_work_brief_human_review_pilot_scaffold.v0"
TEMPLATE_SCHEMA = "lolla.decision_work_brief_human_review_response_template.v0"
EXPECTED_CASES = {
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
}
BUILDER_OUTPUT_REFS = {
    "docs/conversation-understanding/decision-work-brief-builder-enriched-launch-public-enterprise-beta-v0.md",
    "docs/conversation-understanding/decision-work-brief-builder-enriched-deploy-assisted-intake-routing-v0.md",
    "docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md",
}
ALLOWED_ANSWER_VALUES = {"yes", "partly", "no", "unclear", "not_reviewed"}
ALLOWED_PILOT_OUTCOMES = {
    "ready_to_run_human_review",
    "revise_review_form_first",
    "reduce_case_scope",
    "add_source_depth_materials_first",
    "stop_and_simplify",
}
ALLOWED_FINAL_RECOMMENDATIONS = {
    "useful_but_needs_source_depth",
    "useful_but_too_overtrust_inducing",
    "readable_but_not_actionable",
    "too_internal_for_user_surface",
    "ready_for_more_human_review",
    "not_ready_for_runtime",
    "needs_simplification",
    "inconclusive",
    "not_reviewed",
}
REQUIRED_FALSE_FIELDS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
}
REQUIRED_CUSTODY_FALSE_FIELDS = REQUIRED_FALSE_FIELDS | {
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "new_lolla_run_created",
    "new_interpretation_read_created",
    "new_builder_output_created",
    "human_answers_filled_by_codex",
    "runtime_attachment_implemented",
}
CASE_ANSWER_FIELDS = {
    "useful_to_decision_maker",
    "action_consequence_clear",
    "uncertainty_visible",
    "source_limits_visible",
    "overtrust_risk",
    "too_operationally_decisive",
    "should_show_to_user",
    "should_feed_agent_inspection",
}
CASE_EMPTY_LIST_FIELDS = {
    "missing_context_needed",
    "what_helped",
    "what_confused",
    "what_should_change_before_user_surface",
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
FORBIDDEN_TRUE_CLAIMS = (
    "Product proof: yes",
    "Human validation: yes",
    "Human review completed: yes",
    "Answer-quality scoring: yes",
    "Agent action authorization: yes",
    "agent_action_authorized" + ": true",
    "product_proof" + ": true",
    "human_validated" + ": true",
    "human_review_completed" + ": true",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _template() -> dict[str, Any]:
    return json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_collect_strings(item))
        return strings
    return []


def _collect_repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_ref") or key.endswith("_refs") or key == "ref":
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {ref for ref in refs if ref.startswith(("docs/", "reviews/", "tests/"))}


def test_scaffold_review_schema_and_conservative_metadata() -> None:
    review = _review()

    assert review["schema_version"] == SCAFFOLD_SCHEMA
    assert review["review_mode"] == "human_review_pilot_scaffold_only"
    assert review["model_calls"] == 0
    for field in REQUIRED_FALSE_FIELDS:
        assert review[field] is False

    custody = review["custody_flags"]
    assert custody["model_calls"] == 0
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False


def test_response_template_schema_and_blank_review_status() -> None:
    template = _template()

    assert template["schema_version"] == TEMPLATE_SCHEMA
    assert template["review_status"] == "not_started"
    assert template["human_review_completed"] is False
    assert set(template["allowed_answer_values"]) == ALLOWED_ANSWER_VALUES
    assert set(template["allowed_final_recommendation_values"]) == (
        ALLOWED_FINAL_RECOMMENDATIONS
    )
    assert template["reviewer_metadata"]["reviewer_id"] is None
    assert template["reviewer_metadata"]["review_completed_at"] is None


def test_exactly_three_target_cases_and_refs_resolve() -> None:
    review = _review()
    template = _template()

    assert set(review["pilot_scope"]["case_ids"]) == EXPECTED_CASES
    assert set(review["pilot_scope"]["target_artifacts"]) == BUILDER_OUTPUT_REFS
    assert {case["case_id"] for case in review["case_packet_summary"]} == EXPECTED_CASES
    assert {case["case_id"] for case in template["cases"]} == EXPECTED_CASES

    all_refs = _collect_repo_refs(review) | _collect_repo_refs(template)
    for ref in all_refs:
        assert (REPO_ROOT / ref).exists(), ref


def test_response_template_case_answers_are_not_codex_filled() -> None:
    for case in _template()["cases"]:
        for field in CASE_ANSWER_FIELDS:
            assert case[field] == "not_reviewed"
        for field in CASE_EMPTY_LIST_FIELDS:
            assert case[field] == []
        assert case["reviewer_notes"] is None
        assert case["known_highest_risk_uncertainty"]


def test_cross_case_and_final_recommendation_are_blank() -> None:
    template = _template()
    cross_case = template["cross_case_assessment"]
    final = template["final_recommendation"]

    assert cross_case["most_useful_case"] is None
    assert cross_case["highest_overtrust_risk_case"] is None
    assert cross_case["common_confusions"] == []
    assert cross_case["common_source_depth_questions"] == []
    assert cross_case["brief_surface_overall_useful"] == "not_reviewed"
    assert cross_case["brief_surface_overall_too_overtrust_inducing"] == (
        "not_reviewed"
    )
    assert cross_case["reviewer_notes"] is None

    assert final["recommended_outcome"] == "not_reviewed"
    assert final["should_continue_to_more_human_review"] == "not_reviewed"
    assert final["should_revise_brief_surface"] == "not_reviewed"
    assert final["should_prepare_runtime_attachment_plan"] == "not_reviewed"
    assert final["reviewer_summary"] is None


def test_stop_conditions_cover_overtrust_source_limits_and_cofounder_caution() -> None:
    review = _review()
    template = _template()

    stop_conditions = set(review["stop_conditions"])
    assert "brief_sounds_like_proof_of_good_advice" in stop_conditions
    assert "source_limits_are_unclear" in stop_conditions
    assert "cofounder_case_sounds_like_legal_or_operational_advice" in stop_conditions
    assert "response_template_forces_fake_certainty" in stop_conditions

    template_stop = template["stop_conditions"]
    for condition in stop_conditions:
        assert template_stop[condition] == "not_reviewed"
    assert template_stop["stop_notes"] == []

    joined = json.dumps(review) + json.dumps(template)
    assert "overtrust" in joined
    assert "source-limit" in joined or "source limits" in joined
    assert "cofounder" in joined
    assert "governance" in joined


def test_allowed_outcomes_and_decision_gate() -> None:
    review = _review()

    assert set(review["allowed_pilot_outcomes"]) == ALLOWED_PILOT_OUTCOMES
    assert review["decision_gate"] in ALLOWED_PILOT_OUTCOMES
    assert review["decision_gate"] == "ready_to_run_human_review"
    assert review["recommended_next_pr"] == (
        "PR152 Decision Work Brief Human Review Pilot Run v0"
    )


def test_scaffold_doc_explains_no_completed_human_review() -> None:
    markdown = SCAFFOLD_DOC_PATH.read_text(encoding="utf-8")

    assert "This is not completed human review" in markdown
    assert "reviewer should judge" in markdown
    assert "clean artifacts prove good advice" in markdown
    assert "response template forces fake certainty" in markdown
    assert "ready_to_run_human_review" in markdown
    assert "PR152 Decision Work Brief Human Review Pilot Run v0" in markdown


def test_no_private_markers_or_authority_claims() -> None:
    text = "\n".join(
        [
            SCAFFOLD_DOC_PATH.read_text(encoding="utf-8"),
            TEMPLATE_PATH.read_text(encoding="utf-8"),
            REVIEW_PATH.read_text(encoding="utf-8"),
            INTAKE_REVIEW_PATH.read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for claim in FORBIDDEN_TRUE_CLAIMS:
        assert claim not in text


def test_product_delta_boundary_lint_passes_for_pr151_artifacts() -> None:
    report = lint_product_delta_paths(
        [SCAFFOLD_DOC_PATH, TEMPLATE_PATH, REVIEW_PATH, INTAKE_REVIEW_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_skill_files_remain_untouched() -> None:
    status = subprocess.check_output(
        ["git", "status", "--short", "--", "SKILL.md", "scripts/skill"],
        cwd=REPO_ROOT,
        text=True,
    )

    assert status.strip() == ""
