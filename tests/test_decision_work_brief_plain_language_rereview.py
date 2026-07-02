from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-plain-language-rereview-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-plain-language-rereview-v0.md"
)
PR123_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-plain-language-renderer-patch-v0.md"
)
PR122_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md"
)
RENDERED_PATHS = {
    "ceo-remove-founding-cofounder": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md",
    "launch-public-enterprise-beta": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md",
    "deploy-assisted-intake-routing": REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md",
}

SCHEMA_VERSION = "lolla.decision_work_brief_plain_language_rereview.v0"
EXPECTED_CASE_FAMILIES = {
    "ceo-remove-founding-cofounder": "founder_governance",
    "launch-public-enterprise-beta": "enterprise_launch_or_gtm",
    "deploy-assisted-intake-routing": "healthcare_operations_or_deployment",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "custody_flags",
    "reviewed_rendered_briefs",
    "readability_questions",
    "cross_case_readability_observations",
    "product_surface_read",
    "remaining_risks",
    "decision_gate",
    "next_recommendation",
    "non_claims",
}
REQUIRED_BRIEF_FIELDS = {
    "case_id",
    "rendered_brief_ref",
    "decision_family",
    "two_minute_reader_read",
    "decision_clarity",
    "action_consequence_clarity",
    "uncertainty_clarity",
    "non_claim_clarity",
    "evidence_limits_clarity",
    "remaining_machinery_language",
    "overclaim_risk",
    "source_depth_risk",
    "product_usefulness_read",
}
REQUIRED_QUESTION_IDS = {
    "busy_reader_understands_decision_quickly",
    "busy_reader_understands_action_change",
    "busy_reader_understands_uncertainty",
    "busy_reader_understands_not_proven",
    "pr123_reduced_internal_machinery_enough",
    "evidence_limits_move_helped",
    "cleaner_prose_false_confidence",
    "source_depth_now_main_blocker",
    "another_renderer_patch_needed_first",
    "readable_enough_for_local_private_comparison",
}
ALLOWED_GATE_OUTCOMES = {
    "proceed_to_local_private_adequacy_check",
    "proceed_to_renderer_patch_round_2",
    "pause_until_human_review",
    "stop_and_simplify",
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
    "clean_briefs_do_not_imply_good_advice",
    "readability_is_not_source_adequacy",
    "three_rendered_examples_are_not_general_evidence",
    "future_local_private_adequacy_check_required",
    "future_human_review_required",
    "no_runtime_integration_recommended",
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
        "codex_assisted_provisional_checked_in_safe"
    )
    assert review["review_metadata"]["case_count"] == 3


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True


def test_all_three_rendered_briefs_are_reviewed_and_resolve() -> None:
    briefs = _review()["reviewed_rendered_briefs"]

    assert {brief["case_id"] for brief in briefs} == set(EXPECTED_CASE_FAMILIES)
    assert len(briefs) == 3
    for brief in briefs:
        assert REQUIRED_BRIEF_FIELDS <= set(brief)
        assert brief["decision_family"] == EXPECTED_CASE_FAMILIES[brief["case_id"]]
        assert brief["two_minute_reader_read"]
        assert brief["action_consequence_clarity"]
        assert brief["uncertainty_clarity"]
        assert brief["non_claim_clarity"]
        assert brief["overclaim_risk"]
        ref_path = REPO_ROOT / brief["rendered_brief_ref"]
        assert ref_path == RENDERED_PATHS[brief["case_id"]]
        assert ref_path.exists(), ref_path


def test_all_readability_questions_are_answered() -> None:
    questions = _review()["readability_questions"]

    assert {item["question_id"] for item in questions} == REQUIRED_QUESTION_IDS
    for item in questions:
        assert item["question"]
        assert item["answer"]
        assert item["rationale"]


def test_decision_gate_is_allowed_and_supports_pr125_path() -> None:
    review = _review()
    gate = review["decision_gate"]

    assert gate["outcome"] in ALLOWED_GATE_OUTCOMES
    assert gate["outcome"] == "proceed_to_local_private_adequacy_check"
    assert set(gate["allowed_outcomes"]) == ALLOWED_GATE_OUTCOMES
    assert gate["language_good_enough_for_local_private_adequacy_check"] is True
    assert gate["source_depth_is_main_blocker"] is True
    assert gate["runtime_integration_recommended"] is False
    assert review["product_surface_read"]["plain_language_surface_good_enough"] is True
    assert review["product_surface_read"]["main_remaining_blocker"] == (
        "source_depth_and_private_context"
    )
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR125 Decision Work Brief Local-Private Adequacy Check v0"
    )


def test_required_non_claims_exist() -> None:
    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])


def test_review_does_not_claim_product_proof_or_human_validation() -> None:
    text = json.dumps(_review(), sort_keys=True).lower()

    forbidden_claims = (
        "is product proof",
        "counts as product proof",
        "human validated",
        "answer-quality score",
        "agent action authorized",
        "runtime integration recommended",
        "clean briefs prove good advice",
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


def test_pr124_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR123_DOC_PATH,
            PR122_DOC_PATH,
            *RENDERED_PATHS.values(),
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
