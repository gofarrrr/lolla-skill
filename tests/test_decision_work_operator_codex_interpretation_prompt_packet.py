from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.json"
)
PR178_PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
PR179_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md"
)
PR180_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-builder-v0.md"
)
PR133_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-schema-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"

SCHEMA_VERSION = "lolla.decision_work_operator_codex_interpretation_prompt_packet.v0"
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "packet_metadata",
    "purpose",
    "source_queue_item",
    "target_output_schema",
    "allowed_source_refs_policy",
    "fields_to_fill",
    "operator_instructions",
    "privacy_rules",
    "forbidden_claims",
    "example_refs",
    "required_output",
    "validation_checklist",
    "custody_flags",
    "non_claims",
    "decision_gate",
    "recommended_next_pr",
}
REQUIRED_FIELDS = {
    "decision_question",
    "likely_starting_direction",
    "revised_direction_or_action_consequence",
    "decision_thresholds",
    "evidence_gates",
    "useful_friction",
    "what_the_final_answer_does_not_prove",
}
REQUIRED_FORBIDDEN_CLAIMS = {
    "product_proof",
    "human_validation",
    "answer_quality_score",
    "advice_correctness",
    "lolla_improved_decision_proof",
    "agent_action_authorization",
    "automatic_action_authorization",
    "customer_readiness",
    "default_on_runtime_behavior",
    "direct_runtime_interpretation",
}
REQUIRED_FALSE_FLAGS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "repo_provider_call_code_added",
    "generated_interpretation_read_created",
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


def _packet() -> dict[str, Any]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def _repo_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, str):
        if value.startswith(("docs/", "reviews/")):
            refs.add(value)
    elif isinstance(value, list):
        for item in value:
            refs.update(_repo_refs(item))
    elif isinstance(value, dict):
        for child in value.values():
            refs.update(_repo_refs(child))
    return refs


def test_prompt_packet_schema_and_shape() -> None:
    packet = _packet()

    assert packet["schema_version"] == SCHEMA_VERSION
    assert REQUIRED_TOP_LEVEL <= set(packet)
    assert packet["packet_metadata"]["packet_mode"] == "docs_schema_tests_only"
    assert "generated_interpretation_read" in packet["packet_metadata"][
        "not_implemented_here"
    ]
    assert packet["decision_gate"] == "proceed_to_generated_read_intake_validator"
    assert packet["recommended_next_pr"] == (
        "PR182 Generated Interpretation Read Intake And Validator v0"
    )


def test_prompt_packet_refs_existing_prd_queue_and_read_schema() -> None:
    packet = _packet()
    metadata = packet["packet_metadata"]

    assert (REPO_ROOT / metadata["source_prd_ref"]) == PR178_PRD_PATH
    assert (REPO_ROOT / metadata["queue_contract_ref"]) == PR179_DOC_PATH
    assert (REPO_ROOT / metadata["queue_builder_ref"]) == PR180_DOC_PATH
    assert (REPO_ROOT / metadata["target_read_schema_ref"]) == PR133_DOC_PATH
    for ref in _repo_refs(packet):
        assert (REPO_ROOT / ref).exists(), ref


def test_source_queue_and_target_output_are_bounded() -> None:
    packet = _packet()

    assert packet["source_queue_item"]["required_schema_version"] == (
        "lolla.decision_work_offline_interpretation_queue_item.v0"
    )
    assert packet["source_queue_item"]["allowed_queue_statuses"] == ["queued"]
    blocked = set(packet["source_queue_item"]["blocked_statuses_must_not_prompt"])
    assert {"running", "completed", "blocked_privacy_risk"} <= blocked
    assert "status_policy_note" in packet["source_queue_item"]
    assert packet["target_output_schema"]["schema_version"] == (
        "lolla.decision_work_conversation_interpretation_read.v0"
    )
    assert packet["target_output_schema"][
        "generated_read_created_by_this_pr"
    ] is False
    assert packet["required_output"]["output_created_by_this_pr"] is False
    assert packet["required_output"]["must_be_validated_by_future_intake"] is True


def test_fields_to_fill_require_sources_uncertainty_and_missingness() -> None:
    fields = _packet()["fields_to_fill"]
    names = {field["field_name"] for field in fields}

    assert REQUIRED_FIELDS <= names
    for field in fields:
        assert field["source_refs_required"] is True
        assert field["uncertainty_required"] is True
        assert field["missingness_allowed"] is True
        assert field["must_not_be_used_as_quality_label"] is True


def test_privacy_rules_and_forbidden_claims_are_conservative() -> None:
    packet = _packet()
    privacy = packet["privacy_rules"]

    assert privacy["raw_conversation_text_allowed"] is False
    assert privacy["raw_revised_answer_text_allowed"] is False
    assert privacy["raw_memo_text_allowed"] is False
    assert privacy["provider_text_allowed"] is False
    assert privacy["private_ledgers_allowed"] is False
    assert privacy["local_absolute_paths_allowed"] is False
    assert privacy["secrets_allowed"] is False
    assert privacy["checked_in_safe_refs_only_by_default"] is True
    assert REQUIRED_FORBIDDEN_CLAIMS <= set(packet["forbidden_claims"])


def test_custody_flags_and_non_claims_are_conservative() -> None:
    packet = _packet()
    custody = packet["custody_flags"]

    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False
    assert "prompt_packet_is_not_interpretation" in packet["non_claims"]
    assert "prompt_packet_does_not_call_models_from_repo_code" in packet[
        "non_claims"
    ]
    assert "prompt_packet_does_not_authorize_agent_action" in packet["non_claims"]


def test_three_checked_in_safe_examples_are_referenced() -> None:
    examples = _packet()["example_refs"]
    case_ids = {example["case_id"] for example in examples}

    assert {
        "launch-public-enterprise-beta",
        "deploy-assisted-intake-routing",
        "ceo-remove-founding-cofounder",
    } <= case_ids
    cofounder = next(
        example
        for example in examples
        if example["case_id"] == "ceo-remove-founding-cofounder"
    )
    assert "high_risk_caveats_required" in cofounder["example_status"]


def test_front_door_docs_link_prompt_packet() -> None:
    conversation_rel = (
        "decision-work-operator-codex-interpretation-prompt-packet-v0.md"
    )
    repo_rel = (
        "docs/conversation-understanding/"
        "decision-work-operator-codex-interpretation-prompt-packet-v0.md"
    )
    board_rel = (
        "../conversation-understanding/"
        "decision-work-operator-codex-interpretation-prompt-packet-v0.md"
    )

    assert conversation_rel in PR180_DOC_PATH.read_text(encoding="utf-8")
    assert conversation_rel in PR178_PRD_PATH.read_text(encoding="utf-8")
    assert repo_rel in README_PATH.read_text(encoding="utf-8")
    assert repo_rel in HOW_IT_WORKS_PATH.read_text(encoding="utf-8")
    assert repo_rel in PROGRESS_PATH.read_text(encoding="utf-8")
    assert board_rel in BOARD_README_PATH.read_text(encoding="utf-8")


def test_prompt_packet_docs_pass_product_delta_boundary_lint() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            JSON_PATH,
            PR180_DOC_PATH,
            PR178_PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            BOARD_README_PATH,
            PROGRESS_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_prompt_packet_contains_no_private_markers_or_local_paths() -> None:
    combined = JSON_PATH.read_text(encoding="utf-8") + DOC_PATH.read_text(
        encoding="utf-8"
    )

    for marker in FORBIDDEN_STRINGS:
        assert marker not in combined
