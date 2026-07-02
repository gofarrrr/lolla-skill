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
    / "decision-work-brief-small-pattern-review-v0"
    / "review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md"
)
PR118_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-usefulness-review-v0.md"
)
PR119_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-second-tiny-case-pilot-v0.md"
)
COFOUNDER_RENDERED_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    / "decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
)
LAUNCH_RENDERED_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    / "decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_brief_small_pattern_review.v0"
EXPECTED_CASE_IDS = {
    "ceo-remove-founding-cofounder",
    "launch-public-enterprise-beta",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "custody_flags",
    "reviewed_cases",
    "comparison_questions",
    "cross_case_observations",
    "pattern_read",
    "risks",
    "decision_gate",
    "next_recommendation",
    "non_claims",
}
REQUIRED_CASE_FIELDS = {
    "case_id",
    "source_refs",
    "decision_type",
    "decision_read",
    "starting_direction_read",
    "pressure_read",
    "action_consequence_read",
    "uncertainty_read",
    "non_claims_read",
    "evidence_receipt_read",
    "usefulness_read",
    "readability_read",
    "overclaim_risk_read",
    "missingness_read",
    "user_value_read",
    "unresolved_questions",
}
REQUIRED_QUESTION_IDS = {
    "both_name_decision_clearly",
    "both_name_action_consequence",
    "both_explain_lolla_pressure_in_user_language",
    "both_preserve_uncertainty",
    "both_show_not_proven",
    "either_too_machinery_flavored",
    "either_clean_artifacts_feel_like_proof",
    "enough_pattern_consistency_to_continue",
    "useful_for_decision_work_not_artifacts",
    "busy_decision_maker_understands_artifact",
}
ALLOWED_PATTERN_READS = {
    "strong_enough_for_third_case",
    "useful_but_renderer_copy_needs_patch",
    "useful_but_source_context_too_thin",
    "too_machinery_flavored",
    "too_overclaim_prone",
    "inconclusive",
}
ALLOWED_GATE_OUTCOMES = {
    "proceed_to_third_diversity_case",
    "proceed_to_renderer_language_patch",
    "proceed_to_local_private_adequacy_check",
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
    "clean_artifacts_do_not_imply_good_advice",
    "two_cases_are_not_general_evidence",
    "third_case_is_not_runtime_integration",
    "future_human_review_required",
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
    assert review["review_metadata"]["case_count"] == 2


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True


def test_both_expected_cases_are_reviewed_with_required_reads() -> None:
    cases = _review()["reviewed_cases"]

    assert {case["case_id"] for case in cases} == EXPECTED_CASE_IDS
    assert len(cases) == 2
    for case in cases:
        assert REQUIRED_CASE_FIELDS <= set(case)
        assert case["action_consequence_read"]
        assert case["uncertainty_read"]
        assert case["overclaim_risk_read"]
        assert case["non_claims_read"]
        assert case["unresolved_questions"]


def test_source_refs_and_rendered_brief_refs_resolve() -> None:
    rendered_paths = set()

    for case in _review()["reviewed_cases"]:
        for ref in case["source_refs"]:
            path = REPO_ROOT / ref["path"]
            assert path.exists(), ref
            if ref["role"] == "rendered_brief":
                rendered_paths.add(path)

    assert rendered_paths == {COFOUNDER_RENDERED_PATH, LAUNCH_RENDERED_PATH}


def test_all_comparison_questions_are_answered() -> None:
    questions = _review()["comparison_questions"]

    assert {item["question_id"] for item in questions} == REQUIRED_QUESTION_IDS
    for item in questions:
        assert item["question"]
        assert item["answer"]
        assert item["rationale"]


def test_pattern_read_and_decision_gate_are_allowed_and_match_pr121_path() -> None:
    review = _review()
    pattern = review["pattern_read"]
    gate = review["decision_gate"]

    assert pattern["outcome"] in ALLOWED_PATTERN_READS
    assert pattern["outcome"] == "strong_enough_for_third_case"
    assert set(pattern["allowed_outcomes"]) == ALLOWED_PATTERN_READS
    assert gate["outcome"] in ALLOWED_GATE_OUTCOMES
    assert gate["outcome"] == "proceed_to_third_diversity_case"
    assert set(gate["allowed_outcomes"]) == ALLOWED_GATE_OUTCOMES
    assert gate["pr121_path"] == (
        "PR121A Decision Work Brief Third Diversity Case Pilot v0"
    )
    assert gate["runtime_integration_recommended"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR121 Decision Work Brief Third Diversity Case Pilot v0"
    )


def test_review_names_useful_signal_and_risks_without_product_proof() -> None:
    risks = _review()["risks"]

    assert "action consequence" in risks["strongest_useful_signal"]
    assert risks["strongest_missingness_thinness_risk"]
    assert risks["strongest_overclaim_risk"]
    assert "false confidence" in risks["strongest_overclaim_risk"]
    assert "product proof" not in risks["strongest_useful_signal"].lower()


def test_required_non_claims_exist() -> None:
    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])


def test_review_does_not_claim_lolla_improved_decisions_as_fact() -> None:
    text = json.dumps(_review(), sort_keys=True).lower()

    forbidden_claims = (
        "lolla improved the decisions",
        "proves lolla improved",
        "is product proof",
        "counts as product proof",
        "proves product readiness",
        "decision was correct",
    )
    for claim in forbidden_claims:
        assert claim not in text


def test_checked_in_files_have_no_local_paths_or_privacy_markers() -> None:
    text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            PR118_DOC_PATH.read_text(encoding="utf-8"),
            PR119_DOC_PATH.read_text(encoding="utf-8"),
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


def test_pr120_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR118_DOC_PATH,
            PR119_DOC_PATH,
            COFOUNDER_RENDERED_PATH,
            LAUNCH_RENDERED_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
