from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-contract-packet-review-v0/review.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
)
CONTRACT_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.md"
)
PR127_REVIEW_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-brief-conversation-interpretation-gap-map-v0/review.json"
)

SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_contract_packet_review.v0"
)
CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_contract.v0"
)
EXPECTED_CASES = {
    "ceo-remove-founding-cofounder",
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
}
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "review_metadata",
    "custody_flags",
    "source_contract",
    "reviewed_cases",
    "contract_field_support_matrix",
    "per_case_packet_alignment",
    "implementation_gap_summary",
    "product_impact_summary",
    "recommended_next_step",
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
    "raw_private_content_checked_in",
    "raw_private_content_included",
    "provider_text_checked_in",
    "provider_text_included",
    "local_absolute_paths_checked_in",
}
ALLOWED_LOCAL_PRIVATE_STATUS = {
    "not_attempted",
    "completed_read_only_metadata",
    "completed_read_only_structured_context",
    "unavailable_missing_artifacts",
    "blocked_for_privacy",
    "blocked_for_safety",
}
ALLOWED_CURRENT_SUPPORT = {
    "supported_from_checked_in_safe_artifacts",
    "partial_from_checked_in_safe_artifacts",
    "supported_from_local_private_artifacts",
    "partial_from_local_private_artifacts",
    "status_only_possible",
    "requires_future_llm_interpretation",
    "requires_human_review",
    "not_currently_captured",
    "should_not_be_exported",
    "unclear",
}
ALLOWED_SUPPORT_SOURCE = {
    "decision_work_brief",
    "decision_work_brief_packet",
    "decision_work_receipt",
    "decision_trail_report",
    "product_delta_review",
    "audit_decision_record",
    "completed_run_archive_metadata",
    "local_private_structured_artifact",
    "local_private_raw_or_private_artifact_not_checked_in",
    "future_llm_interpretation",
    "future_human_review",
    "not_available",
    "mixed",
}
ALLOWED_REQUIRED_NEXT_CAPABILITY = {
    "none",
    "packet_builder_status_ref_patch",
    "offline_interpretation_packet",
    "offline_llm_specialist_read",
    "local_private_adequacy_read",
    "brief_schema_patch",
    "renderer_patch",
    "future_runtime_extraction_extension",
    "human_review_protocol",
    "do_not_build",
}
REQUIRED_MATRIX_FIELDS = {
    "field_group",
    "field_name",
    "current_support",
    "support_source",
    "required_next_capability",
    "can_current_packet_carry_status_only",
    "can_feed_decision_work_brief",
    "can_feed_agent_inspection",
    "should_remain_private_or_redacted",
    "must_not_be_quality_label",
    "notes",
}
REQUIRED_GAP_GROUPS = {
    "already_supported",
    "packet_builder_gaps",
    "offline_interpretation_gaps",
    "local_private_only_gaps",
    "future_runtime_extraction_candidates",
    "human_review_only_fields",
    "do_not_export_or_quality_label_fields",
}
REQUIRED_PRODUCT_IMPACT_FIELDS = {
    "what_current_brief_can_already_explain",
    "what_conversation_story_is_still_missing",
    "missing_fields_that_matter_most_for_user",
    "missing_fields_that_matter_most_for_agent_inspection",
    "fields_creating_biggest_overclaim_risk",
    "gaps_to_solve_before_runtime_attachment",
}
ALLOWED_NEXT_STEPS = {
    "patch_packet_builder_for_contract_status_refs",
    "build_offline_interpretation_packet",
    "build_offline_llm_specialist_read",
    "run_more_local_private_adequacy_checks",
    "patch_brief_schema",
    "plan_future_runtime_extraction_extension",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_NON_CLAIMS = {
    "review_is_codex_assisted",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_extraction",
    "not_live_lolla_schema_change",
    "not_a_contract_implementation",
    "clean_artifacts_do_not_imply_good_advice",
    "packet_status_is_not_semantic_evidence",
    "future_human_review_required",
    "future_llm_interpretation_required_before_populated_contract_fields",
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
RUNTIME_OR_EXTRACTION_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_conversation_interpreter.py",
    REPO_ROOT / "engine/system_b/decision_work_brief_runtime.py",
    REPO_ROOT / "scripts/evals/integrate_decision_work_brief_runtime.py",
    REPO_ROOT / "scripts/evals/extract_decision_work_conversation_contract.py",
)


def _review() -> dict[str, Any]:
    return json.loads(REVIEW_PATH.read_text(encoding="utf-8"))


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _contract_fields() -> set[tuple[str, str]]:
    fields: set[tuple[str, str]] = set()
    for group_name, group_fields in _contract()["field_groups"].items():
        for field in group_fields:
            fields.add((group_name, field["field_name"]))
    return fields


def _repo_ref_exists(ref: str) -> bool:
    if not ref.endswith((".md", ".json", ".py")):
        return True
    return (REPO_ROOT / ref).exists()


def test_review_json_has_expected_schema_and_top_level_fields() -> None:
    review = _review()

    assert review["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(review)
    assert review["review_metadata"]["review_mode"] == (
        "codex_assisted_provisional_checked_in_safe_contract_packet_review"
    )
    assert review["review_metadata"]["temporary_packets_checked_in"] is False


def test_custody_flags_are_conservative() -> None:
    custody = _review()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["checked_in_safe"] is True


def test_source_contract_references_pr128_contract() -> None:
    source_contract = _review()["source_contract"]

    assert source_contract["contract_ref"] == (
        "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
    )
    assert source_contract["schema_version"] == CONTRACT_SCHEMA_VERSION
    assert (REPO_ROOT / source_contract["contract_ref"]).exists()
    assert (REPO_ROOT / source_contract["contract_doc_ref"]).exists()
    assert _contract()["schema_version"] == CONTRACT_SCHEMA_VERSION


def test_all_three_expected_cases_are_reviewed_and_refs_resolve() -> None:
    cases = _review()["reviewed_cases"]

    assert {case["case_id"] for case in cases} == EXPECTED_CASES
    assert len(cases) == 3
    for case in cases:
        assert case["local_private_review_status"] in ALLOWED_LOCAL_PRIVATE_STATUS
        assert (REPO_ROOT / case["rendered_brief_ref"]).exists()
        assert case["existing_review_refs"]
        assert case["packet_or_artifact_refs_reviewed"]
        assert case["safe_checked_in_limitations"]
        for ref in case["existing_review_refs"]:
            assert _repo_ref_exists(ref), ref
        for ref in case["packet_or_artifact_refs_reviewed"]:
            assert _repo_ref_exists(ref), ref


def test_contract_field_support_matrix_covers_every_pr128_field() -> None:
    matrix = _review()["contract_field_support_matrix"]
    reviewed_fields = {
        (entry["field_group"], entry["field_name"]) for entry in matrix
    }

    assert reviewed_fields == _contract_fields()
    assert len(matrix) == len(_contract_fields())


def test_matrix_entries_use_allowed_vocabularies_and_non_label_policy() -> None:
    for entry in _review()["contract_field_support_matrix"]:
        assert REQUIRED_MATRIX_FIELDS <= set(entry)
        assert entry["current_support"] in ALLOWED_CURRENT_SUPPORT
        assert entry["support_source"] in ALLOWED_SUPPORT_SOURCE
        assert entry["required_next_capability"] in ALLOWED_REQUIRED_NEXT_CAPABILITY
        assert isinstance(entry["can_current_packet_carry_status_only"], bool)
        assert isinstance(entry["can_feed_decision_work_brief"], bool)
        assert isinstance(entry["can_feed_agent_inspection"], bool)
        assert isinstance(entry["should_remain_private_or_redacted"], bool)
        assert entry["must_not_be_quality_label"] is True
        assert entry["notes"]


def test_matrix_contains_expected_support_categories() -> None:
    supports = {
        entry["current_support"]
        for entry in _review()["contract_field_support_matrix"]
    }

    assert "partial_from_checked_in_safe_artifacts" in supports
    assert "supported_from_local_private_artifacts" in supports
    assert "status_only_possible" in supports
    assert "requires_future_llm_interpretation" in supports
    assert "requires_human_review" in supports
    assert "not_currently_captured" in supports


def test_per_case_packet_alignment_exists_for_all_cases() -> None:
    alignments = _review()["per_case_packet_alignment"]

    assert {case["case_id"] for case in alignments} == EXPECTED_CASES
    for case in alignments:
        assert case["strongest_supported_fields"]
        assert case["important_partial_fields"]
        assert case["important_missing_fields"]
        assert case["fields_available_only_privately"]
        assert case["fields_requiring_llm_interpretation"]
        assert case["fields_requiring_human_review"]
        assert case["packet_builder_limitations"]
        assert case["brief_product_impact"]


def test_gap_summary_and_product_impact_answer_required_questions() -> None:
    review = _review()

    assert REQUIRED_GAP_GROUPS <= set(review["implementation_gap_summary"])
    for group in REQUIRED_GAP_GROUPS:
        assert review["implementation_gap_summary"][group]
    assert REQUIRED_PRODUCT_IMPACT_FIELDS <= set(review["product_impact_summary"])
    for field in REQUIRED_PRODUCT_IMPACT_FIELDS:
        assert review["product_impact_summary"][field]


def test_recommended_next_step_is_allowed_and_stays_offline() -> None:
    next_step = _review()["recommended_next_step"]

    assert next_step["outcome"] in ALLOWED_NEXT_STEPS
    assert next_step["outcome"] == "build_offline_interpretation_packet"
    assert set(next_step["allowed_outcomes"]) == ALLOWED_NEXT_STEPS
    assert next_step["runtime_extraction_recommended"] is False
    assert next_step["runtime_integration_recommended"] is False
    assert next_step["rationale"]


def test_non_claims_and_pr127_contract_gate_are_present() -> None:
    pr127 = json.loads(PR127_REVIEW_PATH.read_text(encoding="utf-8"))

    assert REQUIRED_NON_CLAIMS <= set(_review()["non_claims"])
    assert pr127["recommended_next_step"]["outcome"] == (
        "define_interpretation_target_contract"
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


def test_no_runtime_or_extraction_implementation_files_were_added() -> None:
    for path in RUNTIME_OR_EXTRACTION_FILES:
        assert not path.exists(), path


def test_product_delta_boundary_lint_accepts_pr129_artifacts() -> None:
    report = lint_product_delta_paths([REVIEW_PATH, DOC_PATH, CONTRACT_DOC_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_json_and_markdown_files_parse_or_render_cleanly() -> None:
    subprocess.run(["jq", ".", str(REVIEW_PATH)], check=True, capture_output=True)
    assert DOC_PATH.read_text(encoding="utf-8").startswith(
        "# Decision Work Conversation Interpretation Contract Packet Review v0"
    )
