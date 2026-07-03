from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from engine.system_b.decision_work_generated_interpretation_read_intake import (
    INTAKE_SCHEMA_VERSION,
    validate_generated_interpretation_read,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-generated-read-pilot-v0.md"
)
READ_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/read.json"
)
INTAKE_PATH = (
    REPO_ROOT
    / "reviews/codex-assisted/decision-work-operator-codex-generated-read-pilot-v0/intake.json"
)
PROMPT_PACKET_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.json"
)
INTAKE_REVIEW_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-interpretation-read-intake-review-v0.md"
)
INTAKE_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
SCRIPT_PATH = (
    REPO_ROOT
    / "scripts/evals/validate_decision_work_generated_interpretation_read.py"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

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


def _read_payload() -> dict[str, Any]:
    return json.loads(READ_PATH.read_text())


def _intake_payload() -> dict[str, Any]:
    return json.loads(INTAKE_PATH.read_text())


def test_pilot_read_uses_formal_read_schema_and_safe_case() -> None:
    read = _read_payload()

    assert (
        read["schema_version"]
        == "lolla.decision_work_conversation_interpretation_read.v0"
    )
    assert read["read_metadata"]["read_mode"] == (
        "operator_codex_generated_provisional_checked_in_safe_pilot_read"
    )
    assert read["selected_case"]["case_id"] == "launch-public-enterprise-beta"
    assert read["selected_case"]["decision_family"] == "enterprise_launch_or_gtm"
    assert read["interpretation_scope"]["full_contract_interpreted"] is False
    assert read["interpretation_scope"]["broad_batch_created"] is False
    assert len(read["interpreted_fields"]) == 4
    assert {field["field_name"] for field in read["interpreted_fields"]} == {
        "decision_question",
        "revised_direction_or_action_consequence",
        "evidence_gates",
        "what_the_final_answer_does_not_prove",
    }


def test_pilot_read_preserves_sources_uncertainty_and_quality_boundary() -> None:
    read = _read_payload()

    for field in read["interpreted_fields"]:
        assert field["source_refs"], field["field_name"]
        assert field["uncertainty"] in {
            "low",
            "medium",
            "high",
            "insufficient_context",
        }
        assert field["privacy_limit"]
        assert field["human_review_required"] is True
        assert field["must_not_be_used_as_quality_label"] is True

        for source_ref in field["source_refs"]:
            artifact = source_ref["artifact"]
            assert not artifact.startswith("/")
            assert (REPO_ROOT / artifact).exists(), artifact


def test_pilot_read_custody_flags_and_non_claims_are_conservative() -> None:
    read = _read_payload()
    custody = read["custody_flags"]

    assert custody["human_validated"] is False
    assert custody["product_proof"] is False
    assert custody["model_calls"] == 0
    assert custody["archive_mutated"] is False
    assert custody["runtime_invoked"] is False
    assert custody["skill_invoked"] is False
    assert custody["answer_quality_scored"] is False
    assert custody["agent_action_authorized"] is False
    assert custody["raw_private_content_checked_in"] is False
    assert custody["provider_text_checked_in"] is False
    assert custody["local_absolute_paths_checked_in"] is False
    assert custody["semantic_read_is_provisional"] is True

    non_claims = set(read["non_claims"])
    assert "not_human_validated" in non_claims
    assert "not_product_proof" in non_claims
    assert "not_answer_quality_score" in non_claims
    assert "not_agent_action_authorization" in non_claims
    assert "not_correctness_proof" in non_claims
    assert "must_not_be_used_as_quality_label" in non_claims


def test_checked_in_intake_matches_validator_result() -> None:
    expected = validate_generated_interpretation_read(
        read_path=READ_PATH,
        prompt_packet_path=PROMPT_PACKET_PATH,
        created_at="2026-07-03T00:00:00Z",
    )

    assert _intake_payload() == expected
    assert expected["schema_version"] == INTAKE_SCHEMA_VERSION
    assert expected["intake_status"] == "accepted"
    assert expected["accepted_for_downstream"] is True
    assert expected["source_prompt_packet_ref"]["status"] == "available"
    assert expected["source_queue_item_ref"]["status"] == "not_supplied"


def test_intake_keeps_runtime_and_authority_boundaries_closed() -> None:
    intake = _intake_payload()

    assert intake["downstream_allowed"]["can_feed_brief"] is True
    assert intake["downstream_allowed"]["can_feed_enrichment"] is True
    assert intake["downstream_allowed"]["can_feed_triage_packet"] is True
    assert intake["downstream_allowed"]["can_feed_resolver"] is True
    assert intake["downstream_allowed"]["can_update_sidecar"] is False
    assert intake["downstream_allowed"]["can_authorize_agent_action"] is False
    assert intake["downstream_allowed"]["can_be_used_as_quality_label"] is False
    assert intake["output_refs"]["brief_generated"] is False
    assert intake["output_refs"]["enriched_brief_generated"] is False
    assert intake["output_refs"]["triage_generated"] is False
    assert intake["output_refs"]["resolver_refs_updated"] is False
    assert intake["output_refs"]["runtime_sidecar_updated"] is False
    assert "intake_does_not_call_models" in intake["non_claims"]
    assert "intake_does_not_update_runtime_sidecars" in intake["non_claims"]


def test_cli_validates_pilot_read_to_temp_intake(tmp_path: Path) -> None:
    out = tmp_path / "pilot_intake.json"
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--read",
            str(READ_PATH),
            "--prompt-packet",
            str(PROMPT_PACKET_PATH),
            "--out",
            str(out),
            "--pretty",
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    payload = json.loads(out.read_text())
    assert payload["schema_version"] == INTAKE_SCHEMA_VERSION
    assert payload["intake_status"] == "accepted"
    assert payload["accepted_for_downstream"] is True
    assert payload["downstream_allowed"]["can_update_sidecar"] is False


def test_pilot_doc_records_decision_gate_and_non_claims() -> None:
    doc = DOC_PATH.read_text()

    assert "proceed_to_generated_read_to_brief_supply_plan" in doc
    assert "PR185 Decision Work Generated Read To Brief Supply Plan v0" in doc
    assert "Acceptance means" in doc
    assert "does not mean the interpretation is" in doc
    assert "semantically true" in doc
    assert "does not call providers or model APIs" in doc
    assert "can_update_sidecar: false" in doc
    assert "can_authorize_agent_action: false" in doc
    assert "can_be_used_as_quality_label: false" in doc


def test_discoverability_docs_reference_pr184() -> None:
    docs = {
        "README": README_PATH.read_text(),
        "HOW_IT_WORKS": HOW_IT_WORKS_PATH.read_text(),
        "PROGRESS": PROGRESS_PATH.read_text(),
        "board": BOARD_README_PATH.read_text(),
        "prd": PRD_PATH.read_text(),
        "intake_review": INTAKE_REVIEW_DOC_PATH.read_text(),
        "intake": INTAKE_DOC_PATH.read_text(),
    }

    for name, text in docs.items():
        lower = text.lower()
        assert "operator/codex generated" in lower, name
        assert "pilot" in lower, name


def test_product_delta_boundary_lint_accepts_pr184_docs() -> None:
    result = lint_product_delta_paths(
        [
            DOC_PATH,
            READ_PATH,
            INTAKE_PATH,
            INTAKE_REVIEW_DOC_PATH,
            INTAKE_DOC_PATH,
            PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert result["summary"]["blocking_error_count"] == 0
    assert result["summary"]["warning_count"] == 0


def test_pilot_artifacts_contain_no_forbidden_markers() -> None:
    for path in (
        DOC_PATH,
        READ_PATH,
        INTAKE_PATH,
        INTAKE_REVIEW_DOC_PATH,
        INTAKE_DOC_PATH,
        PRD_PATH,
        README_PATH,
        HOW_IT_WORKS_PATH,
        PROGRESS_PATH,
        BOARD_README_PATH,
    ):
        text = path.read_text()
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text, f"{path}:{marker}"
