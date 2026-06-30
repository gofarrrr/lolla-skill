from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    REPO_ROOT
    / "docs"
    / "conversation-understanding"
    / "decision-work-receipt-v0.json"
)
PRD_PATH = (
    REPO_ROOT
    / "docs"
    / "conversation-understanding"
    / "decision-work-receipt-prd-v0.md"
)

SCHEMA_VERSION = "lolla.decision_work_receipt.v0"
REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "receipt_metadata",
    "source_context_inventory",
    "conversation_process_map",
    "challenge_coverage",
    "decision_trail_summary",
    "product_delta_summary",
    "process_evidence_readiness",
    "missingness_and_redaction",
    "human_review",
    "non_claims",
    "boundary",
}
READINESS_LABELS = {
    "insufficient_process_evidence",
    "one_shot_or_thin_process",
    "multi_turn_unreviewed_process",
    "challenged_and_revised_process",
    "decision_trail_review_ready",
    "human_review_ready",
    "human_reviewed",
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


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


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


def test_schema_json_parses_and_uses_expected_version() -> None:
    schema = _schema()

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == SCHEMA_VERSION
    assert schema["properties"]["schema_version"]["const"] == SCHEMA_VERSION


def test_required_top_level_fields_match_pr105_contract() -> None:
    schema = _schema()

    assert set(schema["required"]) == REQUIRED_TOP_LEVEL_FIELDS
    assert set(schema["properties"]) == REQUIRED_TOP_LEVEL_FIELDS


def test_source_context_inventory_models_attachment_gap_without_ingestion() -> None:
    schema = _schema()
    inventory = schema["$defs"]["source_context_inventory"]
    source_kind_values = set(schema["$defs"]["source_kind"]["enum"])
    policy = schema["$defs"]["attachment_custody_policy"]["properties"]

    assert {
        "pasted_context_candidate",
        "file_reference_candidate",
        "pdf_reference_candidate",
        "link_reference_candidate",
        "external_context_reference",
    }.issubset(source_kind_values)
    assert policy["attachments_are_first_class_archived_sources"]["const"] is False
    assert policy["pdf_ingestion_implemented"]["const"] is False
    assert policy["link_fetching_implemented"]["const"] is False
    assert policy["ocr_implemented"]["const"] is False
    assert policy["embeddings_or_chunking_implemented"]["const"] is False
    assert {
        "status",
        "receipt_mode",
        "sources",
        "source_counts",
        "attachment_custody_policy",
        "limitations",
    } == set(inventory["required"])


def test_source_records_keep_raw_and_local_path_inclusion_const_false() -> None:
    schema = _schema()
    source_record = schema["$defs"]["source_record"]
    properties = source_record["properties"]

    assert properties["raw_private_content_included"]["const"] is False
    assert properties["local_absolute_path_included"]["const"] is False
    assert {
        "source_id",
        "source_kind",
        "artifact_or_reference",
        "status",
        "read_status",
        "content_included",
        "raw_private_content_included",
        "local_absolute_path_included",
        "source_refs",
        "notes",
    } == set(source_record["required"])


def test_conversation_process_map_splits_deterministic_metadata_from_semantics() -> None:
    schema = _schema()
    process_map = schema["$defs"]["conversation_process_map"]
    semantic_fields = process_map["properties"]["semantic_process_fields"]
    field_def = schema["$defs"]["semantic_process_field"]

    assert {
        "turn_count",
        "user_turn_count",
        "assistant_turn_count",
        "process_depth",
        "deterministic_process_evidence",
    }.issubset(process_map["properties"])
    assert set(semantic_fields["required"]) == {
        "new_context_added",
        "user_corrections_or_redirects",
        "options_explored",
        "assistant_challenge_or_pushback",
        "premortem_or_counterframe_used",
        "abandoned_paths",
        "final_output_divergence",
    }
    assert field_def["properties"]["exporter_inferred_from_prose"]["const"] is False
    assert "requires_llm_interpretation" in field_def["required"]
    assert "requires_human_review" in field_def["required"]


def test_challenge_coverage_records_presence_without_quality_claim() -> None:
    schema = _schema()
    challenge_coverage = schema["$defs"]["challenge_coverage"]
    challenge_surface = schema["$defs"]["challenge_surface"]

    assert challenge_coverage["properties"]["challenge_quality_scored"]["const"] is False
    assert challenge_surface["properties"]["quality_not_assessed"]["const"] is True
    assert {
        "surface_id",
        "surface_name",
        "status",
        "source_refs",
        "present",
        "quality_not_assessed",
        "notes",
    } == set(challenge_surface["required"])


def test_process_evidence_readiness_is_not_answer_quality_or_permission() -> None:
    schema = _schema()
    readiness = schema["$defs"]["process_evidence_readiness"]

    assert set(schema["$defs"]["process_evidence_readiness_label"]["enum"]) == READINESS_LABELS
    assert readiness["properties"]["answer_quality_scored"]["const"] is False
    assert readiness["properties"]["correctness_claimed"]["const"] is False
    assert readiness["properties"]["agent_action_authorized"]["const"] is False
    assert {
        "label",
        "status",
        "basis_refs",
        "deterministic_basis",
        "semantic_limitations",
        "answer_quality_scored",
        "correctness_claimed",
        "agent_action_authorized",
        "empty_meaning",
    } == set(readiness["required"])


def test_non_claims_and_boundary_remain_conservative() -> None:
    schema = _schema()
    non_claims = schema["$defs"]["non_claims"]["properties"]
    boundary = schema["$defs"]["boundary"]["properties"]

    for field in {
        "not_answer_quality_scoring",
        "not_correctness_proof",
        "not_product_proof",
        "not_agent_action_authorization",
        "not_runtime_integration",
        "not_llm_judge",
        "clean_artifacts_do_not_imply_good_advice",
    }:
        assert non_claims[field]["const"] is True

    assert boundary["model_calls"]["const"] == 0
    assert boundary["provider_calls"]["const"] == 0
    for field in {
        "runtime_invoked",
        "skill_invoked",
        "archive_mutated",
        "raw_private_content_included",
        "local_absolute_paths_included",
        "answer_quality_scored",
        "llm_judge_used",
        "automatic_labels_created",
        "agent_action_authorized",
        "graph_memory_or_embedding_work_added",
    }:
        assert boundary[field]["const"] is False


def test_schema_does_not_introduce_forbidden_authority_field_names() -> None:
    keys = set(_walk_keys(_schema()))

    assert not (keys & FORBIDDEN_FIELD_NAMES)


def test_schema_and_prd_pass_boundary_lint_without_findings() -> None:
    result = lint_product_delta_paths([SCHEMA_PATH, PRD_PATH])

    assert result["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
    assert result["findings"] == []


def test_schema_and_prd_do_not_contain_privacy_markers() -> None:
    combined = (
        SCHEMA_PATH.read_text(encoding="utf-8")
        + "\n"
        + PRD_PATH.read_text(encoding="utf-8")
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in combined
