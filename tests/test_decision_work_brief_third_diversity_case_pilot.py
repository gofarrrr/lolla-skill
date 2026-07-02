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
    / "decision-work-brief-third-diversity-case-pilot-v0"
    / "review.json"
)
PR120_REVIEW_PATH = (
    REPO_ROOT
    / "reviews"
    / "codex-assisted"
    / "decision-work-brief-small-pattern-review-v0"
    / "review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    / "decision-work-brief-third-diversity-case-pilot-v0.md"
)
PR120_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-small-pattern-review-v0.md"
)
RENDERED_EXAMPLE_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/"
    / "decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md"
)

PILOT_SCHEMA_VERSION = "lolla.decision_work_brief_third_diversity_case_pilot.v0"
BRIEF_SCHEMA_VERSION = "lolla.decision_work_brief.v0"
THIRD_CASE_ID = "deploy-assisted-intake-routing"
PRIOR_CASE_IDS = {
    "ceo-remove-founding-cofounder",
    "launch-public-enterprise-beta",
}
BRIEF_SECTIONS = {
    "decision",
    "starting_direction",
    "what_lolla_pressed_on",
    "what_changed",
    "what_this_means_for_action",
    "what_still_might_be_wrong",
    "what_was_not_proven",
    "evidence_receipt",
}
SECTION_REQUIRED_FIELDS = {
    "status",
    "source_status",
    "source_refs",
    "interpreted_by",
    "human_validated",
    "uncertainty",
    "value",
    "empty_meaning",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "pilot_metadata",
    "selected_case",
    "input_scope",
    "source_packets",
    "custody_flags",
    "third_case_brief",
    "rendered_brief_ref",
    "comparison_to_prior_cases",
    "aggregate_observations",
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
REQUIRED_BRIEF_CUSTODY_FALSE_FIELDS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "raw_transcript_included",
    "raw_revised_answer_included",
    "raw_memo_included",
    "private_reasoning_included",
    "local_absolute_paths_included",
    "secrets_included",
    "llm_judge_used",
    "automatic_labels_created",
}
REQUIRED_NON_CLAIMS = {
    "pilot_is_codex_assisted",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "clean_artifacts_do_not_imply_good_advice",
    "three_cases_are_not_general_evidence",
    "future_human_review_required",
    "no_runtime_integration_recommended_from_this_pilot_alone",
}
REQUIRED_BRIEF_NON_CLAIMS = {
    "not_correctness_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_human_validated_unless_marked",
    "clean_artifacts_do_not_imply_good_advice",
    "process_evidence_is_not_decision_certification",
    "llm_interpretation_is_provisional_unless_human_reviewed",
}
ALLOWED_GATE_OUTCOMES = {
    "proceed_to_three_case_pattern_review",
    "proceed_to_renderer_language_patch",
    "proceed_to_local_private_adequacy_check",
    "pause_until_human_review",
    "stop_and_simplify",
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
LOCAL_ABSOLUTE_PATH_MARKERS = (
    "/" + "Users" + "/",
    "/" + "tmp" + "/",
)
RUNTIME_INTEGRATION_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_brief_runtime.py",
    REPO_ROOT / "scripts/evals/integrate_decision_work_brief_runtime.py",
    REPO_ROOT / "scripts/evals/build_decision_work_brief_batch.py",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _pr120_review() -> dict[str, Any]:
    return json.loads(PR120_REVIEW_PATH.read_text(encoding="utf-8"))


def _brief() -> dict[str, Any]:
    return _review()["third_case_brief"]["brief"]


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

    assert review["schema_version"] == PILOT_SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(review)
    assert review["pilot_metadata"]["review_mode"] == (
        "codex_assisted_provisional_checked_in_safe"
    )
    assert review["pilot_metadata"]["case_count"] == 1


def test_pr121a_path_matches_pr120_gate() -> None:
    pr120_gate = _pr120_review()["decision_gate"]
    review = _review()

    assert pr120_gate["outcome"] == "proceed_to_third_diversity_case"
    assert pr120_gate["pr121_path"] == (
        "PR121A Decision Work Brief Third Diversity Case Pilot v0"
    )
    assert review["pilot_metadata"]["triggering_gate_outcome"] == pr120_gate["outcome"]


def test_selected_case_is_one_new_preferred_diversity_case() -> None:
    selected = _review()["selected_case"]

    assert selected["case_id"] == THIRD_CASE_ID
    assert selected["run_id"] == "20260627T130339Z_4cd3cb"
    assert selected["archive_relpath"] == f"{THIRD_CASE_ID}/20260627T130339Z_4cd3cb"
    assert selected["selected_case_count"] == 1
    assert set(selected["not_reused_cases"]) == PRIOR_CASE_IDS
    assert selected["case_id"] not in PRIOR_CASE_IDS


def test_pr115_packet_was_generated_locally_as_metadata_only() -> None:
    review = _review()
    packets = review["source_packets"]

    assert review["input_scope"]["pr115_packet_outputs_used"] is True
    assert review["input_scope"]["local_private_text_used_for_pr121a"] is False
    assert len(packets) == 1
    packet = packets[0]
    assert packet["packet_schema_version"] == "lolla.decision_work_brief_packets.v0"
    assert packet["packet_mode"] == "metadata_only"
    assert packet["generated_locally_for_pr121a"] is True
    assert packet["checked_in"] is False
    assert packet["local_private_text_used"] is False
    assert packet["raw_private_content_included"] is False
    assert packet["provider_text_included"] is False
    assert set(packet["target_sections"]) == BRIEF_SECTIONS


def test_custody_flags_are_conservative() -> None:
    for custody in (
        _review()["custody_flags"],
        _review()["third_case_brief"]["custody_flags"],
    ):
        for field in REQUIRED_CUSTODY_FALSE_FIELDS:
            assert custody[field] is False
        assert custody["model_calls"] == 0
        assert custody["checked_in_safe"] is True

    brief_custody = _brief()["custody_flags"]
    for field in REQUIRED_BRIEF_CUSTODY_FALSE_FIELDS:
        assert brief_custody[field] is False
    assert brief_custody["model_calls"] == 0


def test_required_non_claims_exist() -> None:
    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])
    assert REQUIRED_BRIEF_NON_CLAIMS <= set(_brief()["non_claims"]["items"])


def test_third_case_brief_embeds_pr114_brief_contract() -> None:
    brief = _brief()

    assert brief["schema_version"] == BRIEF_SCHEMA_VERSION
    assert brief["mode"] == "checked_in_safe_mode"
    assert {"brief_metadata", "source_refs", "custody_flags", "sections"} <= set(brief)
    assert brief["brief_metadata"]["case_id"] == THIRD_CASE_ID


def test_all_required_brief_sections_exist_with_shared_shape() -> None:
    sections = _brief()["sections"]

    assert set(sections) == BRIEF_SECTIONS
    for section_id, section in sections.items():
        assert SECTION_REQUIRED_FIELDS <= set(section), section_id
        assert isinstance(section["source_refs"], list)
        assert section["human_validated"] is False
        assert section["empty_meaning"]


def test_uncertainty_action_consequence_and_human_followups_are_visible() -> None:
    review = _review()
    sections = _brief()["sections"]
    uncertainties = {section["uncertainty"] for section in sections.values()}

    assert "high" in uncertainties
    assert (
        sections["what_this_means_for_action"]["value"]["action_consequence"]
        or review["third_case_brief"]["action_consequence_read"]
    )
    assert "possible_overcorrection_or_noise" in sections[
        "what_still_might_be_wrong"
    ]["value"]
    assert review["third_case_brief"]["human_followup_questions"]


def test_rendered_markdown_example_exists_and_preserves_limits() -> None:
    text = RENDERED_EXAMPLE_PATH.read_text(encoding="utf-8")

    assert text.startswith("# Decision Work Brief\n")
    assert "## The decision" in text
    assert "## What this means for action" in text
    assert "## What this does not prove" in text
    assert "## Evidence and limits" in text
    assert "`not_correctness_proof`" in text
    assert "Product proof: no" in text
    assert "Answer-quality scoring: no" in text
    assert "Agent action authorization: no" in text


def test_comparison_to_prior_cases_and_gate_are_conservative() -> None:
    review = _review()
    comparison = review["comparison_to_prior_cases"]
    gate = review["decision_gate"]

    assert set(comparison["prior_case_refs"]) == PRIOR_CASE_IDS
    assert comparison["third_case_ref"] == THIRD_CASE_ID
    assert comparison["did_all_cases_produce_concrete_action_consequence"][
        "answer"
    ] == "yes"
    assert comparison["did_third_case_test_different_decision_type"]["answer"] == "yes"
    assert gate["outcome"] in ALLOWED_GATE_OUTCOMES
    assert gate["outcome"] == "proceed_to_three_case_pattern_review"
    assert set(gate["allowed_outcomes"]) == ALLOWED_GATE_OUTCOMES
    assert gate["runtime_integration_recommended"] is False


def test_review_names_signal_missingness_and_overclaim_risk() -> None:
    observations = _review()["aggregate_observations"]

    assert observations["strongest_useful_signal"]
    assert observations["strongest_missingness_thinness_risk"]
    assert observations["strongest_overclaim_risk"]
    assert _review()["next_recommendation"]["recommended_next_pr"] == (
        "PR122 Decision Work Brief Three-Case Pattern Review v0"
    )


def test_checked_in_files_have_no_local_paths_or_privacy_markers() -> None:
    text = "\n".join(
        [
            REVIEW_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            RENDERED_EXAMPLE_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS + LOCAL_ABSOLUTE_PATH_MARKERS:
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


def test_pr121a_artifacts_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            REVIEW_PATH,
            PR120_DOC_PATH,
            PR120_REVIEW_PATH,
            RENDERED_EXAMPLE_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
