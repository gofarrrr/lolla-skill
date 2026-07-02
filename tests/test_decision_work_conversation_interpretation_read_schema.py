from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-v0.json"
)
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md"
)
PR132_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json"
)
PR132_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-second-tiny-offline-read-v0.md"
)
PR131_READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json"
)
PR131_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-tiny-offline-read-v0.md"
)
PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_conversation_interpretation_read.v0"
REQUIRED_TOP_LEVEL_FIELDS = {
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
}
OPTIONAL_TOP_LEVEL_FIELDS = {"comparison_to_prior_reads"}
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
}
REQUIRED_INTERPRETED_FIELD_KEYS = {
    "field_group",
    "field_name",
    "status",
    "value",
    "uncertainty",
    "source_refs",
    "source_status",
    "interpretation_basis",
    "privacy_limit",
    "human_review_required",
    "could_feed_brief",
    "could_feed_agent_inspection",
    "must_not_be_used_as_quality_label",
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
ALLOWED_NEXT_STEPS = {
    "run_another_tiny_offline_read",
    "compare_interpretation_reads",
    "patch_offline_packet_builder",
    "patch_decision_work_brief_schema",
    "test_brief_enrichment_from_interpretation",
    "pause_until_human_review",
    "stop_and_simplify",
}
REQUIRED_NON_CLAIMS = {
    "read_is_provisional",
    "not_human_validated",
    "not_product_proof",
    "not_answer_quality_score",
    "not_agent_action_authorization",
    "not_runtime_integration",
    "not_runtime_extraction",
    "must_not_be_used_as_quality_label",
    "clean_artifacts_do_not_imply_good_advice",
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
FORBIDDEN_RUNTIME_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_conversation_interpretation_read.py",
    REPO_ROOT / "scripts/evals/run_decision_work_conversation_interpretation_read.py",
    REPO_ROOT / "scripts/evals/interpret_decision_work_conversation.py",
)


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _defs() -> dict[str, Any]:
    return _schema()["$defs"]


def test_schema_json_parses_and_has_expected_schema_version() -> None:
    schema = _schema()

    assert schema["$id"] == SCHEMA_VERSION
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION
    assert schema["type"] == "object"


def test_required_and_optional_top_level_fields_are_declared() -> None:
    schema = _schema()

    assert set(schema["required"]) == REQUIRED_TOP_LEVEL_FIELDS
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(schema["properties"])
    assert OPTIONAL_TOP_LEVEL_FIELDS <= set(schema["properties"])


def test_custody_flags_are_constrained_conservatively() -> None:
    custody = _defs()["custody_flags"]
    props = custody["properties"]

    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert field in custody["required"]
        assert props[field]["const"] is False
    assert "semantic_read_is_provisional" in custody["required"]
    assert props["semantic_read_is_provisional"]["const"] is True
    assert props["model_calls"]["const"] == 0


def test_interpreted_fields_require_source_refs_and_non_quality_label_guard() -> None:
    interpreted = _defs()["interpreted_field"]

    assert set(interpreted["required"]) == REQUIRED_INTERPRETED_FIELD_KEYS
    assert interpreted["properties"]["source_refs"]["minItems"] == 1
    assert interpreted["properties"]["human_review_required"]["type"] == "boolean"
    assert (
        interpreted["properties"]["must_not_be_used_as_quality_label"]["const"] is True
    )


def test_vocabularies_match_pr131_pr132_read_shape() -> None:
    defs = _defs()

    assert set(defs["status"]["enum"]) == ALLOWED_STATUS
    assert set(defs["uncertainty"]["enum"]) == ALLOWED_UNCERTAINTY
    assert set(defs["source_status"]["enum"]) == ALLOWED_SOURCE_STATUS
    assert set(defs["interpretation_basis"]["enum"]) == ALLOWED_BASIS
    assert set(defs["recommended_next_step_outcome"]["enum"]) == ALLOWED_NEXT_STEPS


def test_source_packet_points_to_pr130_packet_and_pr128_contract() -> None:
    source_packet = _defs()["source_packet"]["properties"]

    assert source_packet["packet_schema_version"]["const"] == (
        "lolla.decision_work_conversation_interpretation_packets.v0"
    )
    assert source_packet["source_contract_ref"]["const"] == (
        "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
    )
    assert source_packet["source_contract_schema_version"]["const"] == (
        "lolla.decision_work_conversation_interpretation_contract.v0"
    )
    assert source_packet["raw_private_content_in_packet"]["const"] is False
    assert source_packet["provider_text_in_packet"]["const"] is False


def test_non_claims_include_required_deterministic_guards() -> None:
    non_claims = set(_defs()["non_claim"]["enum"])

    assert REQUIRED_NON_CLAIMS <= non_claims


def test_pr133_follows_pr132_gate() -> None:
    pr132 = json.loads(PR132_READ_PATH.read_text(encoding="utf-8"))

    assert pr132["recommended_next_step"]["outcome"] == (
        "define_interpretation_read_schema"
    )
    assert SCHEMA_PATH.exists()


def test_schema_and_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [SCHEMA_PATH, DOC_PATH, PR132_READ_PATH, PR132_DOC_PATH, PR131_DOC_PATH, PRD_PATH]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_schema_docs_and_tests_do_not_include_private_markers() -> None:
    for path in [
        SCHEMA_PATH,
        DOC_PATH,
        PR132_READ_PATH,
        PR132_DOC_PATH,
        PR131_READ_PATH,
        Path(__file__),
    ]:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text


def test_pr133_does_not_add_runtime_interpreter_files() -> None:
    for path in FORBIDDEN_RUNTIME_FILES:
        assert not path.exists(), path
