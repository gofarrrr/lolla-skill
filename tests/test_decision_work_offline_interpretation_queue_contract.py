from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.json"
)
PR178_PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR130_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md"
)
PR133_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md"
)
BRIEF_PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)
RUNTIME_PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"

SCHEMA_VERSION = "lolla.decision_work_offline_interpretation_queue_contract.v0"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "contract_metadata",
    "purpose",
    "input_refs",
    "queue_modes",
    "queue_statuses",
    "allowed_source_modes",
    "privacy_modes",
    "requested_interpretation_fields",
    "queue_item_shape",
    "queue_result_shape",
    "blocked_or_deferred_reasons",
    "validation_requirements",
    "custody_flags",
    "non_claims",
    "decision_gate",
    "recommended_next_pr",
}
REQUIRED_STATUSES = {
    "not_requested",
    "queued",
    "running",
    "completed",
    "blocked_missing_packet",
    "blocked_privacy_risk",
    "blocked_schema_invalid",
    "failed_validation",
    "requires_local_private_operator",
    "unsafe_to_export",
    "cancelled",
}
REQUIRED_MODES = {
    "disabled",
    "checked_in_safe_metadata_only",
    "local_private_operator",
    "operator_codex_prompt_packet",
    "external_interpretation_read_intake",
    "future_provider_worker_not_implemented",
}
REQUIRED_QUEUE_ITEM_FIELDS = {
    "schema_version",
    "queue_metadata",
    "queue_mode",
    "source_run_ref",
    "source_packet_ref",
    "allowed_source_refs",
    "requested_interpretation_fields",
    "privacy_mode",
    "custody_flags",
    "queue_status",
    "blocked_or_deferred_reasons",
    "output_destinations",
    "validation_requirements",
    "downstream_refs",
    "non_claims",
}
REQUIRED_QUEUE_RESULT_FIELDS = {
    "schema_version",
    "queue_item_ref",
    "status",
    "produced_refs",
    "validation_summary",
    "blocked_reasons",
    "privacy_summary",
    "custody_flags",
    "non_claims",
}
REQUIRED_FALSE_FLAGS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "private_ledgers_included",
    "local_absolute_paths_included",
}
REQUIRED_NON_CLAIMS = {
    "not_product_proof",
    "not_human_validation",
    "not_answer_quality_scoring",
    "not_advice_correctness",
    "not_lolla_improvement_proof",
    "not_action_authorization",
    "not_automatic_action_authorization",
    "not_direct_runtime_interpretation",
    "not_runtime_model_calls",
    "not_customer_ready_surface",
}
FORBIDDEN_STRINGS = (
    "/" + "Users" + "/",
    "SEC" + "RET",
    "raw_message" + "_content",
    "fabricated" + "_passages",
    "FULL ASSISTANT" + " REASONING",
    "client" + "_secret",
    "api" + "_key",
    "pass" + "word",
)


def _contract() -> dict[str, Any]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def _collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings = []
        for item in value.values():
            strings.extend(_collect_strings(item))
        return strings
    return []


def _collect_repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.endswith("_ref") or key.endswith("_refs") or key == "ref":
                refs.update(_collect_strings(child))
            refs.update(_collect_repo_refs(child))
    elif isinstance(value, list):
        for child in value:
            refs.update(_collect_repo_refs(child))
    return {ref for ref in refs if ref.startswith(("docs/", "reviews/", "tests/"))}


def test_contract_json_schema_and_top_level_shape() -> None:
    contract = _contract()

    assert contract["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL <= set(contract)
    assert contract["contract_metadata"]["contract_mode"] == "docs_schema_tests_only"
    assert "queue_runner" in contract["contract_metadata"]["not_implemented_here"]
    assert "model_calls" in contract["contract_metadata"]["not_implemented_here"]
    assert contract["decision_gate"] == "proceed_to_queue_packet_builder"


def test_contract_refs_pr178_pr130_and_pr133() -> None:
    contract = _contract()

    refs = contract["input_refs"]
    assert (REPO_ROOT / refs["automatic_semantic_supply_prd_ref"]) == PR178_PRD_PATH
    assert (REPO_ROOT / refs["source_packet_shape_ref"]) == PR130_DOC_PATH
    assert (REPO_ROOT / refs["target_interpretation_read_schema_ref"]) == PR133_DOC_PATH
    assert refs["source_packet_schema"] == (
        "lolla.decision_work_conversation_interpretation_packets.v0"
    )
    assert refs["target_interpretation_read_schema"] == (
        "lolla.decision_work_conversation_interpretation_read.v0"
    )
    for ref in _collect_repo_refs(contract):
        assert (REPO_ROOT / ref).exists(), ref


def test_statuses_and_modes_include_required_vocabularies() -> None:
    contract = _contract()
    modes = {item["mode"] for item in contract["queue_modes"]}

    assert REQUIRED_STATUSES <= set(contract["queue_statuses"])
    assert REQUIRED_MODES <= modes
    for mode in contract["queue_modes"]:
        assert mode["may_call_models"] is False
        assert mode["may_mutate_archive"] is False
    assert "direct_runtime_interpretation_requested" in contract[
        "blocked_or_deferred_reasons"
    ]


def test_queue_item_and_result_shapes_are_complete() -> None:
    contract = _contract()

    assert contract["queue_item_shape"]["schema_version"] == (
        "lolla.decision_work_offline_interpretation_queue_item.v0"
    )
    assert REQUIRED_QUEUE_ITEM_FIELDS <= set(
        contract["queue_item_shape"]["required_fields"]
    )
    assert contract["queue_result_shape"]["schema_version"] == (
        "lolla.decision_work_offline_interpretation_queue_result.v0"
    )
    assert REQUIRED_QUEUE_RESULT_FIELDS <= set(
        contract["queue_result_shape"]["required_fields"]
    )


def test_requested_fields_are_bounded_and_not_quality_labels() -> None:
    fields = _contract()["requested_interpretation_fields"]
    names = {field["field_name"] for field in fields}

    assert "decision_question" in names
    assert "revised_direction_or_action_consequence" in names
    assert "what_the_final_answer_does_not_prove" in names
    for field in fields:
        assert field["target_schema_ref"] == (
            "lolla.decision_work_conversation_interpretation_read.v0"
        )
        assert field["source_refs_required"] is True
        assert field["uncertainty_required"] is True
        assert field["must_not_be_used_as_quality_label"] is True


def test_custody_flags_are_conservative() -> None:
    custody = _contract()["custody_flags"]

    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False
    assert custody["queue_contract_only"] is True


def test_non_claims_exclude_authority_and_runtime_interpretation() -> None:
    non_claims = set(_contract()["non_claims"])

    assert REQUIRED_NON_CLAIMS <= non_claims
    forbidden = {
        "approval",
        "certified",
        "safe_for_action",
        "advice_correct",
        "quality_score",
    }
    assert forbidden.isdisjoint(non_claims)


def test_historical_indexes_link_the_queue_contract() -> None:
    rel = (
        "docs/conversation-understanding/"
        "decision-work-offline-interpretation-queue-contract-v0.md"
    )
    conversation_rel = "decision-work-offline-interpretation-queue-contract-v0.md"
    board_rel = (
        "../conversation-understanding/"
        "decision-work-offline-interpretation-queue-contract-v0.md"
    )

    assert conversation_rel in PR178_PRD_PATH.read_text(encoding="utf-8")
    assert conversation_rel in BRIEF_PRD_PATH.read_text(encoding="utf-8")
    assert conversation_rel in RUNTIME_PRD_PATH.read_text(encoding="utf-8")
    assert board_rel in BOARD_README_PATH.read_text(encoding="utf-8")
    assert rel in PROGRESS_PATH.read_text(encoding="utf-8")


def test_contract_docs_pass_product_delta_boundary_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            JSON_PATH,
            PR178_PRD_PATH,
            BRIEF_PRD_PATH,
            RUNTIME_PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            BOARD_README_PATH,
            PROGRESS_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_contract_contains_no_private_markers_or_local_absolute_paths() -> None:
    combined = JSON_PATH.read_text(encoding="utf-8") + DOC_PATH.read_text(
        encoding="utf-8"
    )

    for marker in FORBIDDEN_STRINGS:
        assert marker not in combined
