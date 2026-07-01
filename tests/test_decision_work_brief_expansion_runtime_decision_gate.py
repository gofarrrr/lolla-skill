from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-expansion-runtime-decision-gate-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-expansion-runtime-decision-gate-v0.md"
)
PR124_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-plain-language-rereview-v0/review.json"
)
PR125_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-local-private-adequacy-check-v0/review.json"
)
PR122_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-three-case-pattern-review-v0/review.json"
)
PR124_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-plain-language-rereview-v0.md"
)
PR125_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-local-private-adequacy-check-v0.md"
)
PR122_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-three-case-pattern-review-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_brief_expansion_runtime_decision_gate.v0"
ALLOWED_SELECTED_NEXT_STEPS = {
    "run_five_case_checked_in_safe_batch",
    "run_more_local_private_adequacy_checks",
    "plan_runtime_attachment_only",
    "patch_renderer_again",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "custody_flags",
    "evidence_inputs",
    "readiness_assessment",
    "decision_options",
    "selected_next_step",
    "rationale",
    "explicit_non_decisions",
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
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
}
REQUIRED_NON_DECISIONS = {
    "runtime integration is not implemented",
    "no lolla runtime changes were made",
    "no SKILL.md changes were made",
    "no scripts/skill changes were made",
    "no provider or model calls were added",
    "no product proof is claimed",
    "no human validation is claimed",
    "no answer-quality scoring is performed",
    "no agent action is authorized",
}
REQUIRED_NON_CLAIMS = {
    "review_is_codex_assisted",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "runtime_integration_not_implemented",
    "runtime_attachment_planning_not_selected",
    "clean_artifacts_do_not_imply_good_advice",
    "one_local_private_check_is_not_general_evidence",
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


def _pr125_review() -> dict[str, Any]:
    return json.loads(PR125_REVIEW_PATH.read_text(encoding="utf-8"))


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
        "codex_assisted_provisional_checked_in_safe_decision_gate"
    )


def test_pr126_follows_pr125_gate() -> None:
    assert _pr125_review()["decision_gate"]["outcome"] == (
        "proceed_to_expansion_or_runtime_decision_gate"
    )
    assert _review()["review_metadata"]["triggering_gate"] == (
        "PR125 proceed_to_expansion_or_runtime_decision_gate"
    )


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True


def test_evidence_inputs_reference_pr124_pr125_and_pr122() -> None:
    inputs = _review()["evidence_inputs"]
    review_refs = {REPO_ROOT / item["review_ref"] for item in inputs}
    artifact_refs = {REPO_ROOT / item["artifact_ref"] for item in inputs}

    assert {PR124_REVIEW_PATH, PR125_REVIEW_PATH, PR122_REVIEW_PATH} <= review_refs
    assert {PR124_DOC_PATH, PR125_DOC_PATH, PR122_DOC_PATH} <= artifact_refs
    for path in review_refs | artifact_refs:
        assert path.exists(), path


def test_selected_next_step_is_allowed_and_avoids_runtime_integration() -> None:
    selected = _review()["selected_next_step"]

    assert selected["outcome"] in ALLOWED_SELECTED_NEXT_STEPS
    assert selected["outcome"] == "run_more_local_private_adequacy_checks"
    assert set(selected["allowed_outcomes"]) == ALLOWED_SELECTED_NEXT_STEPS
    assert selected["runtime_integration_recommended"] is False
    assert selected["planning_only"] is True


def test_runtime_attachment_option_is_planning_only_if_ever_selected() -> None:
    selected = _review()["selected_next_step"]

    if selected["outcome"] == "plan_runtime_attachment_only":
        assert selected["planning_only"] is True
        assert selected["runtime_integration_recommended"] is False
    else:
        assert selected["outcome"] != "plan_runtime_attachment_only"


def test_explicit_non_decisions_and_non_claims_are_present() -> None:
    review = _review()

    assert REQUIRED_NON_DECISIONS <= set(review["explicit_non_decisions"])
    assert REQUIRED_NON_CLAIMS <= set(review["non_claims"])


def test_readiness_assessment_and_rationale_name_key_risks() -> None:
    review = _review()
    readiness = review["readiness_assessment"]
    rationale = review["rationale"]

    assert readiness["readability_result"] == "good_enough_for_source_depth_review"
    assert readiness["local_private_adequacy_result"] == (
        "one_case_adequate_but_missing_private_nuance"
    )
    assert readiness["runtime_attachment_readiness"] == "premature"
    assert rationale["strongest_useful_signal"]
    assert rationale["strongest_source_depth_risk"]
    assert rationale["strongest_overclaim_risk"]
    assert rationale["why_runtime_integration_is_premature"]
    assert rationale["recommended_next_pr"] == (
        "PR127 Decision Work Brief Additional Local-Private Adequacy Checks v0"
    )


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


def test_pr126_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR124_DOC_PATH,
            PR124_REVIEW_PATH,
            PR125_DOC_PATH,
            PR125_REVIEW_PATH,
            PR122_DOC_PATH,
            PR122_REVIEW_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
