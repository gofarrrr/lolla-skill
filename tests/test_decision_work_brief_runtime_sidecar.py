from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-sidecar-v0.md"
)
JSON_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-sidecar-v0.json"
)
CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-contract-v0.json"
)
SCHEMA_VERSION = "lolla.decision_work_brief_runtime_sidecar.v0"
REQUIRED_ARTIFACT_IDS = {
    "attachment_status",
    "decision_work_brief_json",
    "decision_work_brief_markdown",
    "decision_work_brief_enriched_markdown",
    "automatic_triage_packet",
    "automatic_triage_read",
    "agent_handoff_packet",
    "user_receipt",
}
REQUIRED_FALSE_FLAGS = {
    "human_validated",
    "human_review_completed",
    "product_proof",
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "answer_quality_scored",
    "agent_action_authorized",
    "automatic_action_authorized",
    "raw_private_content_included",
    "provider_text_included",
    "local_absolute_paths_included",
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


def _sidecar() -> dict[str, Any]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def test_sidecar_schema_and_contract_ref() -> None:
    sidecar = _sidecar()

    assert sidecar["schema_version"] == SCHEMA_VERSION
    assert sidecar["sidecar_metadata"]["status"] == "contract_only"
    assert sidecar["sidecar_metadata"]["decision_gate"] == (
        "proceed_to_manual_runtime_bundle_generator"
    )
    assert sidecar["sidecar_metadata"]["runtime_attachment_contract_ref"] == str(
        CONTRACT_PATH.relative_to(REPO_ROOT)
    )
    assert CONTRACT_PATH.exists()


def test_artifact_layout_is_explicit_and_status_is_required() -> None:
    sidecar = _sidecar()
    artifacts = {item["artifact_id"]: item for item in sidecar["artifact_layout"]}

    assert sidecar["sidecar_root"] == "decision_work"
    assert set(artifacts) == REQUIRED_ARTIFACT_IDS
    assert artifacts["attachment_status"]["required"] is True
    assert artifacts["attachment_status"]["relative_path"] == (
        "decision_work/attachment_status.json"
    )
    for item in artifacts.values():
        assert item["relative_path"].startswith("decision_work/")
        assert not Path(item["relative_path"]).is_absolute()


def test_manual_and_runtime_path_policies_are_safe() -> None:
    sidecar = _sidecar()
    manual = sidecar["manual_output_policy"]
    runtime = sidecar["runtime_sidecar_policy"]
    output = sidecar["output_path_safety"]

    assert manual["must_refuse_output_inside_input_run_by_default"] is True
    assert manual["may_write_archive_sidecar_only_in_future_flagged_runtime_hook"] is True
    assert runtime["post_archive_only"] is True
    assert runtime["default_off"] is True
    assert runtime["must_not_rewrite_source_artifacts"] is True
    assert runtime["must_not_block_revised_answer"] is True
    assert runtime["must_fail_closed"] is True
    assert output["checked_in_or_agent_facing_refs_must_be_relative"] is True
    assert output["local_absolute_paths_must_not_be_exported"] is True
    assert output["archive_sidecar_write_requires_future_flagged_hook"] is True


def test_attachment_status_shape_covers_missing_and_failure_states() -> None:
    shape = _sidecar()["attachment_status_shape"]

    for required in (
        "missing_artifacts",
        "blocked_reasons",
        "deferred_reasons",
        "failed_closed_reasons",
        "custody_flags",
        "non_claims",
    ):
        assert required in shape["required_fields"]
    assert "failed_closed" in shape["allowed_attachment_states"]
    assert "generated_agent_only" in shape["allowed_attachment_states"]


def test_custody_privacy_and_non_claims_are_conservative() -> None:
    sidecar = _sidecar()
    custody = sidecar["custody_flags"]
    privacy = sidecar["privacy_export_policy"]

    assert custody["model_calls"] == 0
    for field in REQUIRED_FALSE_FLAGS:
        assert custody[field] is False
    assert custody["sidecar_contract_only"] is True
    assert privacy["source_refs_only_by_default"] is True
    for field in (
        "raw_conversation_text_included",
        "raw_revised_answer_text_included",
        "raw_memo_text_included",
        "provider_text_included",
        "private_ledgers_included",
        "local_absolute_paths_included",
        "secrets_included",
    ):
        assert privacy[field] is False
    assert "not_archive_mutation" in sidecar["non_claims"]
    assert "not_action_authorization" in sidecar["non_claims"]


def test_sidecar_docs_have_no_private_markers_or_forbidden_refs() -> None:
    text = DOC_PATH.read_text(encoding="utf-8") + "\n" + JSON_PATH.read_text(
        encoding="utf-8"
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
    for forbidden in (
        '"human_validated": true',
        '"product_proof": true',
        '"answer_quality_scored": true',
        '"agent_action_authorized": true',
        "safe_for_agent_use",
    ):
        assert forbidden not in text


def test_sidecar_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths([DOC_PATH, JSON_PATH, CONTRACT_PATH])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
