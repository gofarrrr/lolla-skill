from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_brief_enrichment import (
    enrich_decision_work_brief_markdown,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-third-tiny-offline-read-v0.md"
)
SOURCE_PACKET_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/source-packet.json"
)
RENDERED_BRIEF_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
)
RULES_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-enrichment-rules-contract-v0.json"
)

SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_read.v0"
EXPECTED_CASE = "ceo-remove-founding-cofounder"
EXPECTED_RUN = "20260627T093131Z_59d153"
ALLOWED_SCOPE_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "live_options",
    "abandoned_or_rejected_options",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "noisy_friction",
    "lost_value",
    "what_the_final_answer_does_not_prove",
}
ALLOWED_STATUS = {
    "interpreted_provisional",
    "partial_interpretation",
    "insufficient_context",
    "not_interpreted",
    "not_applicable",
}
ALLOWED_UNCERTAINTY = {"low", "medium", "high", "insufficient_context"}
ALLOWED_SOURCE_STATUS = {
    "checked_in_safe_summary_only",
    "local_private_metadata_only",
    "local_private_context_not_checked_in",
    "mixed_safe_and_private_status",
    "missing_source",
    "unclear",
}
ALLOWED_BASIS = {
    "checked_in_brief_and_reviews",
    "pr130_packet_source_refs",
    "local_private_metadata_status",
    "inferred_from_safe_summary",
    "insufficient_context",
}
REQUIRED_CUSTODY_FALSE_FIELDS = {
    "human_validated",
    "product_proof",
    "archive_mutated",
    "runtime_invoked",
    "skill_invoked",
    "answer_quality_scored",
    "agent_action_authorized",
    "raw_private_content_checked_in",
    "provider_text_checked_in",
    "local_absolute_paths_checked_in",
    "broad_judge_used",
    "automatic_labels_created",
    "runtime_extraction_implemented",
}
REQUIRED_NON_CLAIMS = {
    "read_is_codex_assisted",
    "read_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_correctness_proof",
    "not_runtime_integration",
    "not_runtime_extraction",
    "not_lolla_runtime_change",
    "not_live_lolla_schema_change",
    "must_not_be_used_as_quality_label",
    "checked_in_safe_context_is_not_full_conversation_context",
    "clean_artifacts_do_not_imply_good_advice",
    "future_human_review_required",
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
FORBIDDEN_AUTHORITY_SNIPPETS = (
    '"agent_action_authorized": true',
    '"product_proof": true',
    '"human_validated": true',
    '"quality_score"',
    '"improvement_score"',
    '"winner"',
)


def _read() -> dict[str, Any]:
    return json.loads(READ_PATH.read_text(encoding="utf-8"))


def _repo_ref_exists(ref: str) -> bool:
    if not ref.endswith((".md", ".json")):
        return True
    return (REPO_ROOT / ref).exists()


def test_read_uses_formal_pr133_schema_and_expected_case() -> None:
    read = _read()

    assert read["schema_version"] == SCHEMA_VERSION
    assert read["read_metadata"]["case_count"] == 1
    assert read["read_metadata"]["source_packet_fixture_checked_in"] is False
    assert not SOURCE_PACKET_PATH.exists()

    selected = read["selected_case"]
    assert selected["case_id"] == EXPECTED_CASE
    assert selected["run_id"] == EXPECTED_RUN
    assert selected["decision_family"] == "founder_governance_or_authority_transition"
    assert selected["rendered_brief_ref"] == (
        "docs/conversation-understanding/decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
    )
    assert _repo_ref_exists(selected["rendered_brief_ref"])
    for ref in selected["prior_review_refs"]:
        assert _repo_ref_exists(ref)


def test_custody_flags_are_conservative_and_provisional() -> None:
    custody = _read()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["semantic_read_is_provisional"] is True


def test_source_packet_is_not_checked_in_and_contains_no_private_text() -> None:
    source_packet = _read()["source_packet"]

    assert source_packet["packet_schema_version"] == (
        "lolla.decision_work_conversation_interpretation_packets.v0"
    )
    assert source_packet["packet_generated_locally"] is False
    assert source_packet["packet_checked_in"] is False
    assert source_packet["packet_ref"] is None
    assert source_packet["packet_generation_mode"] == "checked_in_safe"
    assert source_packet["source_contract_ref"] == (
        "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
    )
    assert source_packet["source_contract_schema_version"] == (
        "lolla.decision_work_conversation_interpretation_contract.v0"
    )
    assert source_packet["packet_content_checked_in"] is False
    assert source_packet["raw_private_content_in_packet"] is False
    assert source_packet["provider_text_in_packet"] is False


def test_interpretation_scope_is_same_tiny_subset_as_prior_reads() -> None:
    read = _read()
    scope = read["interpretation_scope"]

    assert set(scope["fields_selected"]) == ALLOWED_SCOPE_FIELDS
    assert scope["full_contract_interpreted"] is False
    assert scope["broad_batch_created"] is False

    observed = {field["field_name"] for field in read["interpreted_fields"]}
    assert observed == ALLOWED_SCOPE_FIELDS


def test_interpreted_fields_use_allowed_vocabularies_and_source_refs() -> None:
    for field in _read()["interpreted_fields"]:
        assert field["field_name"] in ALLOWED_SCOPE_FIELDS
        assert field["status"] in ALLOWED_STATUS
        assert field["uncertainty"] in ALLOWED_UNCERTAINTY
        assert field["source_status"] in ALLOWED_SOURCE_STATUS
        assert field["interpretation_basis"] in ALLOWED_BASIS
        assert field["source_refs"]
        assert field["privacy_limit"]
        assert isinstance(field["human_review_required"], bool)
        assert field["could_feed_brief"] is True
        assert field["could_feed_agent_inspection"] is True
        assert field["must_not_be_used_as_quality_label"] is True
        for source_ref in field["source_refs"]:
            assert source_ref["source_status"] in ALLOWED_SOURCE_STATUS
            assert source_ref["artifact"]
            assert _repo_ref_exists(source_ref["artifact"])


def test_expected_cofounder_fields_stay_partial_or_insufficient_context() -> None:
    fields = {field["field_name"]: field for field in _read()["interpreted_fields"]}

    assert fields["decision_question"]["status"] == "interpreted_provisional"
    assert fields["revised_direction_or_action_consequence"]["status"] == (
        "interpreted_provisional"
    )
    assert fields["likely_starting_direction"]["status"] == "partial_interpretation"
    assert fields["likely_starting_direction"]["uncertainty"] == "high"
    assert fields["abandoned_or_rejected_options"]["status"] == "partial_interpretation"
    assert fields["noisy_friction"]["uncertainty"] == "high"
    assert fields["lost_value"]["status"] == "insufficient_context"
    assert fields["lost_value"]["uncertainty"] == "insufficient_context"
    assert fields["lost_value"]["human_review_required"] is True
    assert "quality score" in fields["useful_friction"]["value"].lower()


def test_unresolved_fields_source_limits_and_next_step_are_explicit() -> None:
    read = _read()

    unresolved = {field["field_name"] for field in read["unresolved_fields"]}
    assert {
        "option_status",
        "assistant_influence_on_user_framing",
        "user_values_or_priorities",
        "stakeholder_obligations",
        "safe_to_show_user",
        "safe_for_agent_inspection_only",
    } <= unresolved

    limits = read["source_limitations"]
    assert limits["raw_conversation_was_not_checked_in"] is True
    assert limits["raw_revised_answer_was_not_checked_in"] is True
    assert limits["raw_memo_was_not_checked_in"] is True
    assert limits["provider_text_was_not_checked_in"] is True
    assert limits["private_ledgers_were_not_checked_in"] is True
    assert limits["human_validation_is_absent"] is True
    assert limits["private_nuance_may_change_the_read"] is True

    next_step = read["recommended_next_step"]
    assert next_step["outcome"] == "test_brief_enrichment_from_interpretation"
    assert next_step["recommended_next_pr"] == (
        "PR148 Decision Work Brief Third Builder Case Output v0"
    )


def test_read_is_builder_compatible_without_writing_builder_output() -> None:
    read = _read()
    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    brief = RENDERED_BRIEF_PATH.read_text(encoding="utf-8")

    enriched = enrich_decision_work_brief_markdown(
        brief_markdown=brief,
        interpretation_read=read,
        rules_contract=rules,
    )

    assert enriched.count("## What the interpretation adds") == 1
    assert "## What this does not prove" in enriched
    assert "## Evidence and limits" in enriched
    assert "move product execution authority first" in enriched
    assert "does not prove" in enriched.lower()
    assert not (
        REPO_ROOT
        / "docs/conversation-understanding/decision-work-brief-builder-enriched-ceo-remove-founding-cofounder-v0.md"
    ).exists()


def test_non_claims_and_comparison_to_prior_reads_are_present() -> None:
    read = _read()

    assert REQUIRED_NON_CLAIMS <= set(read["non_claims"])
    comparison = read["comparison_to_prior_reads"]
    assert comparison["same_field_set_used"] is True
    for ref in comparison["prior_read_refs"]:
        assert _repo_ref_exists(ref)
    assert {
        "likely_starting_direction",
        "abandoned_or_rejected_options",
        "lost_value",
    } <= set(comparison["recurring_source_limited_fields"])


def test_checked_in_pr147a_artifacts_have_no_private_markers_or_authority_claims() -> None:
    text = READ_PATH.read_text(encoding="utf-8") + "\n" + DOC_PATH.read_text(
        encoding="utf-8"
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for snippet in FORBIDDEN_AUTHORITY_SNIPPETS:
        assert snippet not in text


def test_product_delta_boundary_lint_passes_for_pr147a_artifacts() -> None:
    report = lint_product_delta_paths([DOC_PATH, READ_PATH])

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
