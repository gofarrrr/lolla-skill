from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json"
)
SOURCE_PACKET_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/source-packet.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-tiny-offline-read-v0.md"
)
PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)
PR130_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
)

SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_tiny_offline_read.v0"
)
PACKET_SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_packets.v0"
CONTRACT_SCHEMA_VERSION = (
    "lolla.decision_work_conversation_interpretation_contract.v0"
)
EXPECTED_CASE = "launch-public-enterprise-beta"
EXPECTED_RUN = "20260627T104146Z_7bfe79"
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
ALLOWED_UNCERTAINTY = {
    "low",
    "medium",
    "high",
    "insufficient_context",
}
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
ALLOWED_NEXT_STEPS = {
    "run_second_tiny_offline_read",
    "define_interpretation_read_schema",
    "patch_offline_packet_builder",
    "patch_decision_work_brief_schema",
    "pause_until_human_review",
    "stop_and_simplify",
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
    "not_runtime_extraction",
    "not_lolla_runtime_change",
    "not_live_lolla_schema_change",
    "one_case_is_not_general_evidence",
    "clean_artifacts_do_not_imply_good_advice",
    "checked_in_safe_context_is_not_full_conversation_context",
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
RUNTIME_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_conversation_interpretation_read.py",
    REPO_ROOT / "scripts/evals/run_decision_work_conversation_interpretation_read.py",
    REPO_ROOT / "scripts/evals/interpret_decision_work_conversation.py",
    REPO_ROOT / "scripts/skill/decision_work_conversation_interpretation_read.py",
)


def _read() -> dict[str, Any]:
    return json.loads(READ_PATH.read_text(encoding="utf-8"))


def _repo_ref_exists(ref: str) -> bool:
    if not ref.endswith((".md", ".json")):
        return True
    return (REPO_ROOT / ref).exists()


def test_read_json_has_expected_schema_and_top_level_fields() -> None:
    read = _read()

    assert read["schema_version"] == SCHEMA_VERSION
    assert {
        "schema_version",
        "read_metadata",
        "custody_flags",
        "source_packet",
        "selected_case",
        "interpretation_scope",
        "interpreted_fields",
        "unresolved_fields",
        "source_limitations",
        "brief_implications",
        "overclaim_risk",
        "recommended_next_step",
        "non_claims",
    } <= set(read)
    assert read["read_metadata"]["case_count"] == 1
    assert read["read_metadata"]["source_packet_fixture_checked_in"] is False
    assert not SOURCE_PACKET_PATH.exists()


def test_custody_flags_are_conservative_and_provisional() -> None:
    custody = _read()["custody_flags"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert custody["model_calls"] == 0
    assert custody["semantic_read_is_provisional"] is True


def test_source_packet_records_pr130_packet_without_checked_in_fixture() -> None:
    source_packet = _read()["source_packet"]

    assert source_packet["packet_schema_version"] == PACKET_SCHEMA_VERSION
    assert source_packet["packet_generated_locally"] is True
    assert source_packet["packet_checked_in"] is False
    assert source_packet["packet_ref"] is None
    assert source_packet["packet_generation_mode"] == "checked_in_safe"
    assert source_packet["source_contract_ref"] == (
        "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
    )
    assert source_packet["source_contract_schema_version"] == CONTRACT_SCHEMA_VERSION
    assert source_packet["packet_content_checked_in"] is False
    assert source_packet["raw_private_content_in_packet"] is False
    assert source_packet["provider_text_in_packet"] is False


def test_selected_case_is_exactly_launch_beta() -> None:
    selected = _read()["selected_case"]

    assert selected["case_id"] == EXPECTED_CASE
    assert selected["run_id"] == EXPECTED_RUN
    assert selected["decision_family"] == "enterprise_launch_or_gtm"
    assert selected["run_ref"] == f"{EXPECTED_CASE}/{EXPECTED_RUN}"
    assert _repo_ref_exists(selected["rendered_brief_ref"])
    for ref in selected["prior_review_refs"]:
        assert _repo_ref_exists(ref)


def test_interpretation_scope_is_tiny_allowed_subset_only() -> None:
    scope = _read()["interpretation_scope"]

    assert set(scope["fields_selected"]) == ALLOWED_SCOPE_FIELDS
    assert scope["full_contract_interpreted"] is False
    assert scope["broad_batch_created"] is False

    observed = {field["field_name"] for field in _read()["interpreted_fields"]}
    assert observed == ALLOWED_SCOPE_FIELDS


def test_interpreted_fields_use_allowed_vocabularies_and_keep_source_refs() -> None:
    for field in _read()["interpreted_fields"]:
        assert field["field_name"] in ALLOWED_SCOPE_FIELDS
        assert field["status"] in ALLOWED_STATUS
        assert field["uncertainty"] in ALLOWED_UNCERTAINTY
        assert field["source_status"] in ALLOWED_SOURCE_STATUS
        assert field["interpretation_basis"] in ALLOWED_BASIS
        assert field["source_refs"]
        assert "privacy_limit" in field
        assert isinstance(field["human_review_required"], bool)
        assert isinstance(field["could_feed_brief"], bool)
        assert isinstance(field["could_feed_agent_inspection"], bool)
        assert field["must_not_be_used_as_quality_label"] is True
        for source_ref in field["source_refs"]:
            assert source_ref["source_status"] in ALLOWED_SOURCE_STATUS
            assert source_ref["artifact"]
            assert _repo_ref_exists(source_ref["artifact"])


def test_expected_fields_are_partial_or_insufficient_context() -> None:
    fields = {field["field_name"]: field for field in _read()["interpreted_fields"]}

    assert fields["decision_question"]["status"] == "interpreted_provisional"
    assert fields["revised_direction_or_action_consequence"]["status"] == (
        "interpreted_provisional"
    )
    assert fields["likely_starting_direction"]["status"] == "partial_interpretation"
    assert fields["likely_starting_direction"]["uncertainty"] in {"medium", "high"}
    assert fields["live_options"]["status"] == "partial_interpretation"
    assert fields["abandoned_or_rejected_options"]["status"] in {
        "partial_interpretation",
        "insufficient_context",
    }
    assert fields["lost_value"]["status"] == "insufficient_context"
    assert fields["lost_value"]["uncertainty"] == "insufficient_context"
    assert "quality" in fields["useful_friction"]["value"].lower()
    assert fields["useful_friction"]["must_not_be_used_as_quality_label"] is True
    assert fields["noisy_friction"]["must_not_be_used_as_quality_label"] is True


def test_unresolved_fields_and_source_limitations_are_explicit() -> None:
    read = _read()

    assert read["unresolved_fields"]
    unresolved_names = {field["field_name"] for field in read["unresolved_fields"]}
    assert "option_status" in unresolved_names
    assert "assistant_influence_on_user_framing" in unresolved_names

    limitations = read["source_limitations"]
    assert "compressed" in limitations["checked_in_safe_context_is_compressed"]
    assert limitations["raw_conversation_was_not_checked_in"] is True
    assert limitations["raw_revised_answer_was_not_checked_in"] is True
    assert limitations["raw_memo_was_not_checked_in"] is True
    assert limitations["provider_text_was_not_checked_in"] is True
    assert limitations["private_ledgers_were_not_checked_in"] is True
    assert limitations["human_validation_is_absent"] is True
    assert limitations["private_nuance_may_change_the_read"] is True


def test_brief_implications_and_overclaim_risk_are_present() -> None:
    read = _read()

    implications = read["brief_implications"]
    assert implications["would_clarify_current_decision_work_brief"] is True
    assert implications["would_require_changing_current_brief_now"] is False
    assert implications["would_add_useful_conversation_story_layer"] is True
    assert implications["would_introduce_overclaim_risk"] is True
    assert implications["do_not_modify_rendered_brief_in_pr131"] is True

    overclaim = read["overclaim_risk"]
    assert overclaim["strongest_risk"]
    assert overclaim["runtime_integration_recommended"] is False
    assert overclaim["product_readiness_claimed"] is False


def test_recommended_next_step_and_non_claims_are_conservative() -> None:
    read = _read()

    next_step = read["recommended_next_step"]
    assert next_step["outcome"] in ALLOWED_NEXT_STEPS
    assert next_step["outcome"] == "run_second_tiny_offline_read"
    assert "runtime integration" in next_step["not_recommended"]
    assert set(read["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_no_runtime_interpreter_or_skill_files_added() -> None:
    for path in RUNTIME_FILES:
        assert not path.exists(), path


def test_docs_and_read_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, READ_PATH, PR130_DOC_PATH, PRD_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr131_files_do_not_include_private_markers() -> None:
    paths = [
        READ_PATH,
        DOC_PATH,
        Path(__file__),
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text


def test_json_refs_resolve() -> None:
    assert CONTRACT_PATH.exists()
    for ref in [
        _read()["source_packet"]["source_contract_ref"],
        _read()["selected_case"]["rendered_brief_ref"],
    ]:
        assert _repo_ref_exists(ref)
