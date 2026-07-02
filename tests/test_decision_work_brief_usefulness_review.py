from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews"
    / "codex-assisted"
    / "decision-work-brief-usefulness-review-v0"
    / "review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-usefulness-review-v0.md"
)
RENDERER_DOC_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-renderer-v0.md"
)
RENDERED_EXAMPLE_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_brief_usefulness_review.v0"
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "input_refs",
    "custody_flags",
    "reviewed_artifacts",
    "usefulness_questions",
    "readability_findings",
    "overclaim_findings",
    "evidence_support_findings",
    "missingness_findings",
    "decision_gate",
    "non_claims",
    "next_recommendation",
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
    "raw_private_content_included",
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
    "clean_artifacts_do_not_imply_good_advice",
    "one_case_is_not_general_evidence",
    "future_human_review_required",
}
REQUIRED_QUESTION_IDS = {
    "name_decision_under_30_seconds",
    "name_likely_starting_direction",
    "name_what_lolla_pressed_on",
    "name_what_changed",
    "name_action_difference",
    "name_what_still_might_be_wrong",
    "name_what_was_not_proven",
    "distinguish_brief_from_receipt_appendix",
    "useful_or_merely_impressive",
    "overclaim_from_clean_receipt",
    "hide_uncertainty",
    "preserve_source_missingness_without_drowning_story",
    "avoid_internal_machinery_labels",
    "evidence_too_thin_for_customer_example",
}
ALLOWED_ANSWER_LABELS = {
    "clear",
    "partly_clear",
    "unclear",
    "overclaim_risk",
    "too_sparse",
    "too_machinery_focused",
    "requires_human_review",
}
ALLOWED_GATE_OUTCOMES = {
    "proceed_to_tiny_second_case",
    "proceed_to_schema_or_renderer_patch",
    "pause_until_human_review",
    "stop_and_simplify",
    "proceed_to_runtime_integration_plan_later",
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
        "codex_assisted_provisional_checked_in_safe"
    )


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True


def test_required_non_claims_exist() -> None:
    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])


def test_all_usefulness_questions_are_answered_with_qualitative_labels() -> None:
    questions = _review()["usefulness_questions"]

    assert {item["question_id"] for item in questions} == REQUIRED_QUESTION_IDS
    for item in questions:
        assert item["answer_label"] in ALLOWED_ANSWER_LABELS
        assert not isinstance(item["answer_label"], (int, float))
        assert item["rationale"]


def test_decision_gate_uses_allowed_outcome_and_is_conservative() -> None:
    gate = _review()["decision_gate"]

    assert gate["outcome"] in ALLOWED_GATE_OUTCOMES
    assert gate["outcome"] == "proceed_to_tiny_second_case"
    assert gate["outcome"] != "proceed_to_runtime_integration_plan_later"
    assert set(gate["allowed_outcomes"]) == ALLOWED_GATE_OUTCOMES
    assert gate["rationale"]


def test_review_names_useful_signal_missingness_and_overclaim_risk() -> None:
    review = _review()

    assert review["readability_findings"]["strongest_useful_signal"]
    assert review["missingness_findings"]["strongest_missingness_thinness_risk"]
    assert review["overclaim_findings"]["strongest_overclaim_risk"]
    assert review["evidence_support_findings"][
        "what_would_need_to_be_true_before_customer_facing"
    ]


def test_reviewed_artifacts_include_receipt_draft_and_rendered_brief() -> None:
    artifacts = {item["path"] for item in _review()["reviewed_artifacts"]}

    assert "docs/conversation-understanding/decision-work-receipt-debug-summary-v0.md" in artifacts
    assert (
        "reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json"
        in artifacts
    )
    assert (
        "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
        in artifacts
    )


def test_checked_in_files_have_no_local_paths_or_privacy_markers() -> None:
    text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            RENDERER_DOC_PATH.read_text(encoding="utf-8"),
            RENDERED_EXAMPLE_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )

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


def test_pr118_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [DOC_PATH, REVIEW_PATH, RENDERER_DOC_PATH, RENDERED_EXAMPLE_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
