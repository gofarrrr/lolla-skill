from __future__ import annotations

import copy
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
    / "docs/conversation-understanding/decision-work-generated-interpretation-read-intake-v0.md"
)
SCRIPT_PATH = (
    REPO_ROOT
    / "scripts/evals/validate_decision_work_generated_interpretation_read.py"
)
READ_SCHEMA_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-read-v0.json"
)
QUEUE_CONTRACT_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.json"
)
PROMPT_PACKET_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.json"
)
PR178_PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-automatic-semantic-supply-prd-v0.md"
)
QUEUE_CONTRACT_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-offline-interpretation-queue-contract-v0.md"
)
PROMPT_PACKET_DOC = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-operator-codex-interpretation-prompt-packet-v0.md"
)
BRIEF_PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)
RUNTIME_ATTACHMENT_PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-runtime-attachment-prd-v0.md"
)
README_PATH = REPO_ROOT / "README.md"
HOW_IT_WORKS_PATH = REPO_ROOT / "HOW_IT_WORKS.md"
PROGRESS_PATH = REPO_ROOT / "PROGRESS.md"
BOARD_README_PATH = REPO_ROOT / "docs/board/README.md"

EXISTING_READS = {
    "launch-public-enterprise-beta": REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-tiny-offline-read-v0/read.json",
    "deploy-assisted-intake-routing": REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-second-tiny-offline-read-v0/read.json",
    "ceo-remove-founding-cofounder": REPO_ROOT
    / "reviews/codex-assisted/decision-work-conversation-interpretation-third-tiny-offline-read-v0/read.json",
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


def _read_payload(case_id: str = "launch-public-enterprise-beta") -> dict[str, Any]:
    return json.loads(EXISTING_READS[case_id].read_text())


def _write_payload(tmp_path: Path, payload: dict[str, Any]) -> Path:
    path = tmp_path / "candidate_read.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _validate_payload(tmp_path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    return validate_generated_interpretation_read(
        read_path=_write_payload(tmp_path, payload),
        created_at="2026-07-03T00:00:00Z",
    )


def _assert_rejected(
    tmp_path: Path,
    payload: dict[str, Any],
    expected_status: str,
) -> dict[str, Any]:
    result = _validate_payload(tmp_path, payload)
    assert result["schema_version"] == INTAKE_SCHEMA_VERSION
    assert result["intake_status"] == expected_status
    assert result["accepted_for_downstream"] is False
    assert result["downstream_allowed"]["can_feed_brief"] is False
    assert result["downstream_allowed"]["can_update_sidecar"] is False
    assert result["downstream_allowed"]["can_authorize_agent_action"] is False
    assert result["downstream_allowed"]["can_be_used_as_quality_label"] is False
    return result


def test_existing_checked_in_interpretation_reads_are_accepted() -> None:
    for case_id, path in EXISTING_READS.items():
        result = validate_generated_interpretation_read(
            read_path=path,
            created_at="2026-07-03T00:00:00Z",
        )

        assert result["schema_version"] == INTAKE_SCHEMA_VERSION
        assert result["intake_status"] == "accepted", case_id
        assert result["accepted_for_downstream"] is True
        assert result["read_schema_detected"] in {
            "lolla.decision_work_conversation_interpretation_read.v0",
            "lolla.decision_work_conversation_interpretation_tiny_offline_read.v0",
            "lolla.decision_work_conversation_interpretation_second_tiny_offline_read.v0",
        }
        assert result["field_validation_summary"]["field_count"] >= 1
        assert result["source_ref_validation"]["status"] == "passed"
        assert result["uncertainty_validation"]["status"] == "passed"
        assert result["privacy_validation"]["status"] == "passed"
        assert result["custody_validation"]["human_validated"] is False
        assert result["custody_validation"]["product_proof"] is False
        assert result["custody_validation"]["answer_quality_scored"] is False
        assert result["custody_validation"]["agent_action_authorized"] is False
        assert result["downstream_allowed"]["can_feed_brief"] is True
        assert result["downstream_allowed"]["can_feed_enrichment"] is True
        assert result["downstream_allowed"]["can_feed_triage_packet"] is True
        assert result["downstream_allowed"]["can_feed_resolver"] is True
        assert result["downstream_allowed"]["can_update_sidecar"] is False
        assert result["downstream_allowed"]["can_authorize_agent_action"] is False
        assert result["downstream_allowed"]["can_be_used_as_quality_label"] is False
        assert "intake_does_not_call_models" in result["non_claims"]


def test_unsupported_schema_is_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["schema_version"] = "lolla.unsupported_read.v0"

    result = _assert_rejected(tmp_path, payload, "unsupported_schema")

    assert "unsupported_schema" in result["blocker_reasons"]


def test_missing_source_refs_are_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["interpreted_fields"][0]["source_refs"] = []

    result = _assert_rejected(tmp_path, payload, "rejected_missing_source_refs")

    assert result["source_ref_validation"]["missing_source_ref_fields"] == [
        "decision_question"
    ]


def test_missing_uncertainty_is_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    del payload["interpreted_fields"][0]["uncertainty"]

    result = _assert_rejected(tmp_path, payload, "rejected_missing_uncertainty")

    assert result["uncertainty_validation"]["missing_uncertainty_fields"] == [
        "decision_question"
    ]


def test_product_proof_claim_is_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["custody_flags"]["product_proof"] = True

    result = _assert_rejected(tmp_path, payload, "rejected_product_proof_claim")

    assert "product_proof_claimed" in result["blocker_reasons"]


def test_human_validation_claim_is_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["custody_flags"]["human_validated"] = True

    result = _assert_rejected(tmp_path, payload, "rejected_human_validation_claim")

    assert "human_validation_claimed" in result["blocker_reasons"]


def test_answer_quality_scoring_claim_is_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["custody_flags"]["answer_quality_scored"] = True

    result = _assert_rejected(tmp_path, payload, "rejected_quality_label")

    assert "answer_quality_scored" in result["blocker_reasons"]


def test_action_authorization_claims_are_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["custody_flags"]["agent_action_authorized"] = True
    result = _assert_rejected(tmp_path, payload, "rejected_action_authorization")
    assert "agent_action_authorized" in result["blocker_reasons"]

    payload = _read_payload()
    payload["custody_flags"]["automatic_action_authorized"] = True
    result = _assert_rejected(tmp_path, payload, "rejected_action_authorization")
    assert "automatic_action_authorized" in result["blocker_reasons"]


def test_quality_label_flag_false_is_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["interpreted_fields"][0]["must_not_be_used_as_quality_label"] = False

    result = _assert_rejected(tmp_path, payload, "rejected_quality_label")

    assert result["field_validation_summary"]["quality_label_blockers"] == [
        "quality_label_allowed:decision_question"
    ]


def test_local_absolute_paths_are_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["interpreted_fields"][0]["source_refs"][0]["artifact"] = (
        "/" + "Users" + "/example/private/archive/result.json"
    )

    result = _assert_rejected(tmp_path, payload, "rejected_local_absolute_path")

    assert "local_absolute_path_detected" in result["blocker_reasons"]


def test_raw_private_markers_are_rejected(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["read_metadata"]["notes"].append("SEC" + "RET")

    result = _assert_rejected(tmp_path, payload, "rejected_privacy_risk")

    assert "privacy_marker_detected" in result["blocker_reasons"]


def test_missing_non_claim_requires_operator_repair(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["non_claims"] = [
        claim
        for claim in payload["non_claims"]
        if claim != "not_product_proof"
    ]

    result = _assert_rejected(tmp_path, payload, "requires_operator_repair")

    assert result["repair_required"] is True
    assert "not_product_proof" in result["repair_reasons"]


def test_validator_does_not_modify_source_read(tmp_path: Path) -> None:
    payload = _read_payload()
    path = _write_payload(tmp_path, payload)
    before = path.read_text()

    result = validate_generated_interpretation_read(
        read_path=path,
        created_at="2026-07-03T00:00:00Z",
    )

    assert result["intake_status"] == "accepted"
    assert path.read_text() == before
    assert result["output_refs"]["source_read_content_modified"] is False


def test_cli_writes_valid_json_for_rejected_result(tmp_path: Path) -> None:
    payload = _read_payload()
    payload["interpreted_fields"][0]["source_refs"] = []
    read_path = _write_payload(tmp_path, payload)
    out_path = tmp_path / "intake.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--read",
            str(read_path),
            "--out",
            str(out_path),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    result = json.loads(out_path.read_text())
    assert result["schema_version"] == INTAKE_SCHEMA_VERSION
    assert result["intake_status"] == "rejected_missing_source_refs"


def test_cli_accepts_optional_queue_item_and_prompt_packet_refs(tmp_path: Path) -> None:
    read_path = EXISTING_READS["ceo-remove-founding-cofounder"]
    queue_item_path = tmp_path / "queue_item.json"
    queue_item_path.write_text(
        json.dumps(
            {
                "schema_version": "lolla.decision_work_offline_interpretation_queue_item.v0"
            }
        ),
        encoding="utf-8",
    )
    out_path = tmp_path / "intake.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--read",
            str(read_path),
            "--queue-item",
            str(queue_item_path),
            "--prompt-packet",
            str(PROMPT_PACKET_PATH),
            "--out",
            str(out_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0
    result = json.loads(out_path.read_text())
    assert result["intake_status"] == "accepted"
    assert result["source_queue_item_ref"]["status"] == "available"
    assert result["source_prompt_packet_ref"]["status"] == "available"


def test_intake_docs_and_touched_docs_pass_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            PR178_PRD_PATH,
            QUEUE_CONTRACT_DOC,
            PROMPT_PACKET_DOC,
            BRIEF_PRD_PATH,
            RUNTIME_ATTACHMENT_PRD_PATH,
            README_PATH,
            HOW_IT_WORKS_PATH,
            PROGRESS_PATH,
            BOARD_README_PATH,
        ]
    )

    assert report["summary"]["blocking_error_count"] == 0
    assert report["summary"]["warning_count"] == 0


def test_checked_files_do_not_contain_private_markers() -> None:
    checked_paths = [
        DOC_PATH,
        SCRIPT_PATH,
        REPO_ROOT / "engine/system_b/decision_work_generated_interpretation_read_intake.py",
        Path(__file__),
    ]

    for path in checked_paths:
        text = path.read_text()
        for marker in FORBIDDEN_STRINGS:
            assert marker not in text


def test_downstream_sidecar_and_action_paths_are_always_false(tmp_path: Path) -> None:
    accepted = validate_generated_interpretation_read(
        read_path=EXISTING_READS["launch-public-enterprise-beta"],
        created_at="2026-07-03T00:00:00Z",
    )
    rejected_payload = copy.deepcopy(_read_payload())
    rejected_payload["custody_flags"]["product_proof"] = True
    rejected = validate_generated_interpretation_read(
        read_path=_write_payload(tmp_path, rejected_payload),
        created_at="2026-07-03T00:00:00Z",
    )

    for result in (accepted, rejected):
        assert result["downstream_allowed"]["can_update_sidecar"] is False
        assert result["downstream_allowed"]["can_authorize_agent_action"] is False
        assert result["downstream_allowed"]["can_be_used_as_quality_label"] is False
        assert result["output_refs"]["runtime_sidecar_updated"] is False
