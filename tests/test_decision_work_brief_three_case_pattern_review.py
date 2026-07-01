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
    / "decision-work-brief-three-case-pattern-review-v0"
    / "review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md"
)
PR120_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-small-pattern-review-v0/review.json"
)
PR121A_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-third-diversity-case-pilot-v0/review.json"
)
PR120_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md"
)
PR121A_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-third-diversity-case-pilot-v0.md"
)
RENDERED_PATHS = {
    REPO_ROOT
    / "docs/conversation-understanding/"
    / "decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md",
    REPO_ROOT
    / "docs/conversation-understanding/"
    / "decision-work-brief-rendered-launch-public-enterprise-beta-v0.md",
    REPO_ROOT
    / "docs/conversation-understanding/"
    / "decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md",
}

SCHEMA_VERSION = "lolla.decision_work_brief_three_case_pattern_review.v0"
EXPECTED_CASE_FAMILIES = {
    "ceo-remove-founding-cofounder": "founder_governance",
    "launch-public-enterprise-beta": "enterprise_launch_or_gtm",
    "deploy-assisted-intake-routing": "healthcare_operations_or_deployment",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "custody_flags",
    "reviewed_cases",
    "cross_case_questions",
    "cross_case_observations",
    "action_consequence_pattern",
    "uncertainty_pattern",
    "source_context_pattern",
    "language_and_readability_pattern",
    "overclaim_risk_pattern",
    "product_usefulness_read",
    "decision_gate",
    "next_recommendation",
    "non_claims",
}
REQUIRED_CASE_FIELDS = {
    "case_id",
    "decision_family",
    "source_refs",
    "rendered_brief_ref",
    "decision_read",
    "action_consequence_read",
    "what_lolla_pressed_on_read",
    "uncertainty_read",
    "missingness_read",
    "non_claims_read",
    "readability_read",
    "overclaim_risk_read",
    "strongest_user_value_signal",
    "strongest_thinness_risk",
}
REQUIRED_QUESTION_IDS = {
    "all_name_decision_clearly",
    "all_name_concrete_action_consequence",
    "action_consequence_differs_by_family",
    "all_explain_lolla_pressure_user_usefully",
    "all_preserve_uncertainty_and_non_claims",
    "any_clean_artifacts_feel_like_proof",
    "any_too_machinery_flavored",
    "source_limits_weaken_usefulness",
    "useful_because_decision_work_not_machinery",
    "busy_decision_maker_takeaway",
}
ALLOWED_PATTERN_READS = {
    "consistent_action_consequence_signal",
    "useful_but_language_too_internal",
    "useful_but_source_context_too_thin",
    "overclaim_risk_too_high",
    "inconclusive",
    "not_useful_enough",
}
ALLOWED_GATE_OUTCOMES = {
    "proceed_to_plain_language_renderer_patch",
    "proceed_to_local_private_adequacy_check",
    "proceed_to_five_case_brief_batch",
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
    "three_cases_are_not_general_evidence",
    "no_runtime_integration_recommended",
    "future_human_review_required",
    "future_local_private_adequacy_check_required_before_customer_claims",
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


def test_all_three_expected_cases_are_reviewed_with_correct_families() -> None:
    cases = _review()["reviewed_cases"]

    assert {case["case_id"] for case in cases} == set(EXPECTED_CASE_FAMILIES)
    assert len(cases) == 3
    for case in cases:
        assert REQUIRED_CASE_FIELDS <= set(case)
        assert case["decision_family"] == EXPECTED_CASE_FAMILIES[case["case_id"]]
        assert case["action_consequence_read"]
        assert case["uncertainty_read"]
        assert case["overclaim_risk_read"]
        assert case["strongest_user_value_signal"]
        assert case["strongest_thinness_risk"]


def test_all_rendered_brief_refs_and_review_refs_resolve() -> None:
    rendered_paths = set()
    review_json_paths = set()

    for case in _review()["reviewed_cases"]:
        rendered_path = REPO_ROOT / case["rendered_brief_ref"]["path"]
        assert rendered_path.exists(), rendered_path
        rendered_paths.add(rendered_path)
        for ref in case["source_refs"]:
            path = REPO_ROOT / ref["path"]
            assert path.exists(), ref
            if path.suffix == ".json":
                review_json_paths.add(path)

    assert rendered_paths == RENDERED_PATHS
    assert {
        REPO_ROOT / "reviews/codex-assisted/decision-work-brief-draft-pilot-v0/review.json",
        REPO_ROOT
        / "reviews/codex-assisted/decision-work-brief-second-tiny-case-pilot-v0/review.json",
        PR121A_REVIEW_PATH,
    } <= review_json_paths


def test_cross_case_questions_include_required_questions() -> None:
    questions = _review()["cross_case_questions"]

    assert {item["question_id"] for item in questions} == REQUIRED_QUESTION_IDS
    for item in questions:
        assert item["question"]
        assert item["answer"]
        assert item["rationale"]


def test_pattern_read_and_decision_gate_are_allowed() -> None:
    review = _review()
    usefulness = review["product_usefulness_read"]
    gate = review["decision_gate"]

    assert usefulness["pattern_read"] in ALLOWED_PATTERN_READS
    assert usefulness["pattern_read"] == "useful_but_language_too_internal"
    assert set(usefulness["allowed_pattern_reads"]) == ALLOWED_PATTERN_READS
    assert gate["outcome"] in ALLOWED_GATE_OUTCOMES
    assert gate["outcome"] == "proceed_to_plain_language_renderer_patch"
    assert set(gate["allowed_outcomes"]) == ALLOWED_GATE_OUTCOMES
    assert gate["runtime_integration_recommended"] is False
    assert review["next_recommendation"]["recommended_next_pr"] == (
        "PR123 Decision Work Brief Plain-Language Renderer Patch v0"
    )


def test_five_case_batch_gate_requires_explicit_non_blockers_if_chosen() -> None:
    gate = _review()["decision_gate"]

    if gate["outcome"] == "proceed_to_five_case_brief_batch":
        assert "renderer_language_not_blocker" in gate
        assert "local_private_adequacy_not_blocker" in gate
    else:
        assert gate["outcome"] != "proceed_to_five_case_brief_batch"
        assert "why_not_five_case_batch" in gate


def test_required_non_claims_exist() -> None:
    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])


def test_patterns_name_useful_signal_and_risks() -> None:
    review = _review()
    usefulness = review["product_usefulness_read"]

    assert review["action_consequence_pattern"]["pattern_status"] == (
        "consistent_action_consequence_signal"
    )
    assert usefulness["strongest_useful_signal"]
    assert usefulness["strongest_missingness_thinness_risk"]
    assert usefulness["strongest_overclaim_risk"]
    assert usefulness["strongest_product_language_risk"]
    assert usefulness["strongest_reason_not_to_integrate_runtime_yet"]


def test_review_does_not_claim_lolla_improved_decisions_as_fact() -> None:
    text = json.dumps(_review(), sort_keys=True).lower()

    forbidden_claims = (
        "lolla improved the decisions",
        "proves lolla improved",
        "is product proof",
        "counts as product proof",
        "proves product readiness",
        "decision was correct",
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


def test_pr122_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR120_DOC_PATH,
            PR120_REVIEW_PATH,
            PR121A_DOC_PATH,
            PR121A_REVIEW_PATH,
            *RENDERED_PATHS,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
