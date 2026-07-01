from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from engine.system_b.decision_work_conversation_interpretation_packets import (
    CONTRACT_FIELD_PACKET_STATUSES,
    CONTRACT_SOURCE_STATUSES,
    DECISION_WORK_CONVERSATION_INTERPRETATION_CONTRACT_SCHEMA_VERSION,
    DECISION_WORK_CONVERSATION_INTERPRETATION_PACKETS_SCHEMA_VERSION,
    FUTURE_INTERPRETATION_READ_SCHEMA_VERSION,
    NON_CLAIMS,
    DecisionWorkConversationInterpretationPacketInputError,
    build_decision_work_conversation_interpretation_packets,
    render_decision_work_conversation_interpretation_packets_json,
    validate_output_path,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_REL = Path(
    "docs/conversation-understanding/decision-work-conversation-interpretation-contract-v0.json"
)
CONTRACT_PATH = REPO_ROOT / CONTRACT_REL
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-offline-packet-v0.md"
)
PRD_PATH = (
    REPO_ROOT / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)
PACKET_REVIEW_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-conversation-interpretation-contract-packet-review-v0.md"
)
SCRIPT_PATH = (
    REPO_ROOT / "scripts/evals/build_decision_work_conversation_interpretation_packets.py"
)

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "packet_metadata",
    "mode",
    "source_run",
    "source_contract",
    "source_inventory",
    "custody_flags",
    "contract_field_groups",
    "future_interpretation_tasks",
    "required_future_output",
    "non_claims",
}
REQUIRED_CUSTODY_FALSE_FIELDS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "semantic_fields_filled",
    "semantic_interpretation_performed",
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "brief_generated",
    "runtime_extraction_implemented",
    "raw_private_content_included",
    "provider_text_included",
    "raw_transcript_included",
    "raw_revised_answer_included",
    "raw_memo_included",
    "private_ledger_content_included",
    "local_absolute_paths_included",
    "secrets_included",
    "automatic_labels_created",
    "broad_judge_used",
}
REQUIRED_FIELD_PACKET_FIELDS = {
    "field_group",
    "field_name",
    "purpose",
    "owner",
    "interpretation_required",
    "deterministic_allowed",
    "human_review_required_when",
    "source_refs_required",
    "empty_meaning",
    "privacy_handling",
    "checked_in_safe_policy",
    "local_private_policy",
    "should_feed_brief",
    "should_feed_agent_inspection",
    "must_not_be_used_as_quality_label",
    "current_packet_status",
    "source_status",
    "source_refs",
    "unavailable_or_redacted_sources",
    "future_interpretation_question",
    "interpretation_task_status",
    "semantic_field_filled",
    "value",
    "required_output_contract_ref",
    "known_limits",
}
REQUIRED_NON_CLAIMS = {
    "packet_is_not_interpretation",
    "packet_is_not_a_decision_work_brief",
    "packet_is_not_product_proof",
    "packet_does_not_score_answer_quality",
    "packet_does_not_authorize_agent_action",
    "packet_does_not_validate_decision_correctness",
    "packet_does_not_run_lolla",
    "packet_does_not_call_models",
    "packet_does_not_change_runtime",
    "packet_does_not_fill_pr128_fields",
    "clean_artifacts_do_not_imply_good_advice",
    "future_interpretation_required",
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
FUTURE_IMPLEMENTATION_FILES = (
    REPO_ROOT / "engine/system_b/decision_work_conversation_interpretation_read.py",
    REPO_ROOT / "scripts/evals/run_decision_work_conversation_interpretation_read.py",
    REPO_ROOT / "scripts/evals/interpret_decision_work_conversation.py",
    REPO_ROOT / "scripts/skill/build_decision_work_conversation_interpretation_packets.py",
)


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _minimal_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "runs" / "sample-case" / "20260701T000000Z_packet"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "agent_result.json",
        {
            "schema_version": "lolla.agent_result.v1",
            "case_id": "sample-case",
            "run_id": "20260701T000000Z_packet",
            "main_counter_pressure": "STRUCTURED PRESSURE TEXT NOT COPIED",
        },
    )
    _write_json(
        run_dir / "evaluation.json",
        {
            "schema_version": "lolla.evaluation.v0",
            "case_id": "sample-case",
            "run_id": "20260701T000000Z_packet",
            "scope": {"model_calls": 0},
        },
    )
    _write_json(
        run_dir / "reasoning_trace.json",
        {
            "schema_version": "lolla.reasoning_trace.v0.2",
            "case": {
                "case_id": "sample-case",
                "run_id": "20260701T000000Z_packet",
                "decision_situation": "Whether to use a smaller launch gate.",
            },
        },
    )
    _write_json(
        run_dir / "extraction.json",
        {
            "schema_version": "lolla.extraction.v0",
            "extraction": {
                "decision_situation": "Whether to use a smaller launch gate.",
                "live_constraints": ["STRUCTURED CONSTRAINT TEXT NOT COPIED"],
            },
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "schema_version": "lolla.pipeline_result.v0",
            "run_health": {"overall": "healthy"},
        },
    )
    _write_json(run_dir / "memo_note.json", {"schema_version": "lolla.memo_note.v0"})
    _write_json(
        run_dir / "graph_survival_report.json",
        {"schema_version": "lolla.graph_survival_report.v0"},
    )
    return run_dir


def _add_raw_private_artifacts(run_dir: Path) -> dict[str, str]:
    raw_markers = {
        "conversation.txt": "PRIVATE CONVERSATION MARKER DO NOT COPY",
        "memo.md": "PRIVATE MEMO MARKER DO NOT COPY",
        "revised.txt": "PRIVATE REVISED MARKER DO NOT COPY",
        "live_transcript.txt": "PRIVATE TRANSCRIPT MARKER DO NOT COPY",
        "operator.log": "PRIVATE OPERATOR MARKER DO NOT COPY",
        "pre_step6_private_table.json": "PRIVATE TABLE MARKER DO NOT COPY",
        "v60_ledger.json": "PRIVATE LEDGER MARKER DO NOT COPY",
    }
    for name, marker in raw_markers.items():
        (run_dir / name).write_text(marker, encoding="utf-8")
    return raw_markers


def _contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _contract_fields() -> set[tuple[str, str]]:
    fields = set()
    for group_id, group_fields in _contract()["field_groups"].items():
        for field in group_fields:
            fields.add((group_id, field["field_name"]))
    return fields


def _packet_fields(packet: dict[str, Any]) -> list[dict[str, Any]]:
    fields = []
    for group in packet["contract_field_groups"].values():
        fields.extend(group["fields"])
    return fields


def test_default_checked_in_safe_packet_has_contract_shape_and_conservative_custody(
    tmp_path: Path,
) -> None:
    packet = build_decision_work_conversation_interpretation_packets(
        run_dir=_minimal_run_dir(tmp_path),
        contract_path=CONTRACT_REL,
        created_at="2026-07-01T00:00:00Z",
    )

    assert packet["schema_version"] == (
        DECISION_WORK_CONVERSATION_INTERPRETATION_PACKETS_SCHEMA_VERSION
    )
    assert REQUIRED_TOP_LEVEL_FIELDS <= set(packet)
    assert packet["mode"] == "checked_in_safe"
    assert packet["source_contract"]["schema_version"] == (
        DECISION_WORK_CONVERSATION_INTERPRETATION_CONTRACT_SCHEMA_VERSION
    )
    assert packet["source_contract"]["contract_ref"] == str(CONTRACT_REL)
    assert packet["required_future_output"]["schema_version"] == (
        FUTURE_INTERPRETATION_READ_SCHEMA_VERSION
    )
    assert packet["required_future_output"]["semantic_fields_filled"] is False

    custody = packet["custody_flags"]
    assert custody["checked_in_safe"] is True
    assert custody["unsafe_for_commit"] is False
    assert custody["model_calls"] == 0
    assert custody["provider_calls"] == 0
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert set(packet["non_claims"]) >= set(NON_CLAIMS)
    assert set(packet["non_claims"]) >= REQUIRED_NON_CLAIMS


def test_every_contract_field_is_present_but_unfilled(tmp_path: Path) -> None:
    packet = build_decision_work_conversation_interpretation_packets(
        run_dir=_minimal_run_dir(tmp_path),
        contract_path=CONTRACT_REL,
    )

    expected_fields = _contract_fields()
    observed_fields = {
        (field["field_group"], field["field_name"]) for field in _packet_fields(packet)
    }
    assert observed_fields == expected_fields

    for field in _packet_fields(packet):
        assert REQUIRED_FIELD_PACKET_FIELDS <= set(field)
        assert field["current_packet_status"] in CONTRACT_FIELD_PACKET_STATUSES
        assert field["source_status"] in CONTRACT_SOURCE_STATUSES
        assert field["interpretation_task_status"] == "not_answered"
        assert field["semantic_field_filled"] is False
        assert field["value"] is None
        assert field["must_not_be_used_as_quality_label"] is True
        assert field["future_interpretation_question"]
        assert field["known_limits"]
        assert field["required_output_contract_ref"]["schema_path"] == str(
            CONTRACT_REL
        )
        for ref in field["source_refs"]:
            assert ref["content_included"] is False
            assert ref["raw_private_content_included"] is False
            assert ref["provider_text_included"] is False
            assert ref["local_absolute_path_included"] is False


def test_future_interpretation_tasks_exist_and_are_unanswered(
    tmp_path: Path,
) -> None:
    packet = build_decision_work_conversation_interpretation_packets(
        run_dir=_minimal_run_dir(tmp_path),
        contract_path=CONTRACT_REL,
    )

    expected_group_ids = set(_contract()["field_groups"])
    observed_group_ids = {task["field_group"] for task in packet["future_interpretation_tasks"]}
    assert observed_group_ids == expected_group_ids
    for task in packet["future_interpretation_tasks"]:
        assert task["status"] == "not_answered"
        assert task["future_question"]
        assert task["target_fields"]
        assert task["required_future_output_schema"] == (
            FUTURE_INTERPRETATION_READ_SCHEMA_VERSION
        )
        assert task["must_preserve_source_refs"] is True
        assert task["must_not_score_answer_quality"] is True
        assert task["must_not_authorize_agent_action"] is True
        assert task["must_not_claim_product_proof"] is True
        assert task["semantic_output_filled_by_packet_builder"] is False


def test_checked_in_safe_packet_records_raw_availability_without_reading_or_copying_text(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    raw_markers = _add_raw_private_artifacts(run_dir)
    original_read_text = Path.read_text

    def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path.name in raw_markers:
            raise AssertionError(f"raw artifact was read: {path.name}")
        return original_read_text(path, *args, **kwargs)

    with patch.object(Path, "read_text", guarded_read_text):
        packet = build_decision_work_conversation_interpretation_packets(
            run_dir=run_dir,
            contract_path=CONTRACT_REL,
        )

    rendered = render_decision_work_conversation_interpretation_packets_json(
        packet,
        pretty=True,
    )
    for marker in raw_markers.values():
        assert marker not in rendered
    assert str(run_dir) not in rendered
    assert "/User" + "s/" not in rendered
    raw_records = [
        record
        for record in packet["source_inventory"]
        if record["artifact"] in raw_markers
    ]
    assert raw_records
    assert {record["content_included"] for record in raw_records} == {False}


def test_local_private_metadata_mode_is_still_status_only(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    _add_raw_private_artifacts(run_dir)

    packet = build_decision_work_conversation_interpretation_packets(
        run_dir=run_dir,
        contract_path=CONTRACT_REL,
        mode="local_private_metadata",
    )

    custody = packet["custody_flags"]
    assert packet["mode"] == "local_private_metadata"
    assert custody["checked_in_safe"] is False
    assert custody["requires_operator_review_before_share"] is True
    assert custody["semantic_fields_filled"] is False
    assert custody["raw_private_content_included"] is False
    assert custody["provider_text_included"] is False
    assert custody["local_absolute_paths_included"] is False
    assert custody["model_calls"] == 0


def test_output_paths_inside_run_directory_are_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(DecisionWorkConversationInterpretationPacketInputError):
        validate_output_path(output_path=run_dir / "packet.json", run_dir=run_dir)


def test_optional_supporting_artifact_metadata_does_not_copy_absolute_paths(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    brief_path = tmp_path / "outside" / "brief.json"
    brief_path.parent.mkdir()
    _write_json(
        brief_path,
        {
            "schema_version": "lolla.decision_work_brief.v0",
            "private_marker": "OPTIONAL BRIEF CONTENT NOT COPIED",
        },
    )

    packet = build_decision_work_conversation_interpretation_packets(
        run_dir=run_dir,
        contract_path=CONTRACT_REL,
        decision_work_brief_path=brief_path,
    )
    rendered = render_decision_work_conversation_interpretation_packets_json(
        packet,
        pretty=True,
    )

    assert str(brief_path.parent) not in rendered
    assert "OPTIONAL BRIEF CONTENT NOT COPIED" not in rendered
    assert "brief.json" in rendered


def test_cli_builds_checked_in_safe_packet(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    out_path = tmp_path / "out" / "conversation_interpretation_packet.json"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--run-dir",
            str(run_dir),
            "--contract",
            str(CONTRACT_REL),
            "--out",
            str(out_path),
            "--limit-fields",
            "3",
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(out_path.read_text(encoding="utf-8"))
    assert packet["schema_version"] == (
        DECISION_WORK_CONVERSATION_INTERPRETATION_PACKETS_SCHEMA_VERSION
    )
    assert len(_packet_fields(packet)) == 3
    assert packet["custody_flags"]["model_calls"] == 0
    assert packet["custody_flags"]["semantic_fields_filled"] is False


def test_malformed_and_unsupported_contracts_are_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    unsupported = tmp_path / "unsupported.json"
    _write_json(unsupported, {"schema_version": "not.supported"})

    with pytest.raises(DecisionWorkConversationInterpretationPacketInputError):
        build_decision_work_conversation_interpretation_packets(
            run_dir=run_dir,
            contract_path=malformed,
        )
    with pytest.raises(DecisionWorkConversationInterpretationPacketInputError):
        build_decision_work_conversation_interpretation_packets(
            run_dir=run_dir,
            contract_path=unsupported,
        )


def test_repo_local_refs_resolve_and_future_runtime_work_is_not_added(
    tmp_path: Path,
) -> None:
    packet = build_decision_work_conversation_interpretation_packets(
        run_dir=_minimal_run_dir(tmp_path),
        contract_path=CONTRACT_REL,
    )

    repo_refs = {
        packet["source_contract"]["contract_ref"],
        packet["source_contract"]["contract_doc_ref"],
        packet["required_future_output"]["source_contract_schema_version"],
    }
    repo_refs.add(str(CONTRACT_REL))
    for field in _packet_fields(packet):
        repo_refs.add(field["required_output_contract_ref"]["schema_path"])
    for ref in repo_refs:
        if ref.endswith((".md", ".json")):
            assert (REPO_ROOT / ref).exists()

    for path in FUTURE_IMPLEMENTATION_FILES:
        assert not path.exists()


def test_docs_pass_product_delta_boundary_lint() -> None:
    report = lint_product_delta_paths(
        [
            DOC_PATH,
            PRD_PATH,
            PACKET_REVIEW_DOC_PATH,
        ]
    )

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_checked_in_pr130_files_do_not_include_private_markers() -> None:
    paths = [
        DOC_PATH,
        SCRIPT_PATH,
        REPO_ROOT / "engine/system_b/decision_work_conversation_interpretation_packets.py",
        Path(__file__),
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for marker in PRIVACY_MARKERS:
            assert marker not in text
