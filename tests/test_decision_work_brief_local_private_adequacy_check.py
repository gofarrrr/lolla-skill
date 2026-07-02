from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-local-private-adequacy-check-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-local-private-adequacy-check-v0.md"
)
PR124_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-plain-language-rereview-v0/review.json"
)
PR124_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-plain-language-rereview-v0.md"
)
RENDERED_LAUNCH_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
)
SECOND_CASE_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-second-tiny-case-pilot-v0/review.json"
)

SCHEMA_VERSION = "lolla.decision_work_brief_local_private_adequacy_check.v0"
EXPECTED_CASES = {
    "ceo-remove-founding-cofounder",
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
}
ALLOWED_STATUSES = {
    "local_private_shadow_review_completed",
    "local_private_shadow_review_not_available",
    "local_private_shadow_review_blocked_for_privacy",
    "local_private_shadow_review_blocked_missing_artifacts",
}
ALLOWED_ADEQUACY_RESULTS = {
    "adequate_for_checked_in_safe_review",
    "adequate_but_missing_private_nuance",
    "too_thin_without_private_context",
    "misleading_without_private_context",
    "inconclusive",
}
ALLOWED_CHANGE_READS = {"yes", "no", "unclear"}
ALLOWED_GATE_OUTCOMES = {
    "proceed_to_expansion_or_runtime_decision_gate",
    "proceed_to_more_local_private_checks",
    "proceed_to_renderer_patch_round_2",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "custody_flags",
    "selected_case",
    "local_private_shadow_review_status",
    "source_scope",
    "compared_brief",
    "local_private_adequacy_read",
    "checked_in_safe_vs_local_private_delta",
    "privacy_safety_notes",
    "decision_gate",
    "next_recommendation",
    "non_claims",
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
    "checked_in_raw_private_content",
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
    "local_private_shadow_review_is_not_human_review",
    "adequacy_check_does_not_certify_customer_readiness",
    "clean_artifacts_do_not_imply_good_advice",
    "one_local_private_check_is_not_general_evidence",
    "future_human_review_required",
    "runtime_integration_not_implemented",
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


def _pr124_review() -> dict[str, Any]:
    return json.loads(PR124_REVIEW_PATH.read_text(encoding="utf-8"))


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
        "codex_assisted_provisional_local_private_shadow_read_checked_in_safe_conclusions"
    )


def test_pr125_follows_pr124_gate() -> None:
    assert _pr124_review()["decision_gate"]["outcome"] == (
        "proceed_to_local_private_adequacy_check"
    )
    assert _review()["review_metadata"]["triggering_gate"] == (
        "PR124 proceed_to_local_private_adequacy_check"
    )


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True


def test_selected_case_and_compared_refs_are_valid() -> None:
    review = _review()
    selected = review["selected_case"]
    compared = review["compared_brief"]

    assert selected["case_id"] in EXPECTED_CASES
    assert selected["case_id"] == "launch-public-enterprise-beta"
    assert selected["selected_case_count"] == 1
    assert set(selected["existing_case_set"]) == EXPECTED_CASES
    assert (REPO_ROOT / compared["rendered_brief_ref"]).resolve() == (
        RENDERED_LAUNCH_PATH.resolve()
    )
    assert (REPO_ROOT / compared["rendered_brief_ref"]).exists()
    assert (REPO_ROOT / compared["structured_brief_ref"]).resolve() == (
        SECOND_CASE_REVIEW_PATH.resolve()
    )
    assert (REPO_ROOT / compared["structured_brief_ref"]).exists()
    assert (REPO_ROOT / compared["pr124_rereview_ref"]).resolve() == (
        PR124_REVIEW_PATH.resolve()
    )


def test_local_private_shadow_review_status_and_completed_fields() -> None:
    review = _review()
    status = review["local_private_shadow_review_status"]
    adequacy = review["local_private_adequacy_read"]

    assert status in ALLOWED_STATUSES
    assert status == "local_private_shadow_review_completed"
    assert adequacy["raw_text_copied_to_repo"] is False
    assert adequacy["local_absolute_paths_checked_in"] is False
    assert adequacy["provider_text_checked_in"] is False
    assert adequacy["adequacy_result"] in ALLOWED_ADEQUACY_RESULTS
    for field in (
        "decision_read_changed",
        "starting_direction_read_changed",
        "action_consequence_read_changed",
        "uncertainty_changed",
        "lost_value_changed",
        "overclaim_risk_changed",
    ):
        assert adequacy[field] in ALLOWED_CHANGE_READS
    assert adequacy["what_became_clearer"]
    assert adequacy["what_remains_uncertain"]


def test_blocked_status_would_require_why_not_run() -> None:
    review = _review()

    if review["local_private_shadow_review_status"] != "local_private_shadow_review_completed":
        assert review["why_not_run"]
        assert review["what_would_be_needed"]
    else:
        assert "why_not_run" not in review


def test_decision_gate_is_allowed_and_supports_pr126_path() -> None:
    gate = _review()["decision_gate"]

    assert gate["outcome"] in ALLOWED_GATE_OUTCOMES
    assert gate["outcome"] == "proceed_to_expansion_or_runtime_decision_gate"
    assert set(gate["allowed_outcomes"]) == ALLOWED_GATE_OUTCOMES
    assert gate["runtime_integration_recommended"] is False
    assert _review()["next_recommendation"]["recommended_next_pr"] == (
        "PR126 Decision Work Brief Expansion / Runtime Attachment Decision Gate v0"
    )


def test_required_non_claims_exist() -> None:
    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])


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


def test_pr125_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR124_DOC_PATH,
            PR124_REVIEW_PATH,
            RENDERED_LAUNCH_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
