from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from engine.system_b.decision_work_brief_packets import (
    BRIEF_SECTIONS,
    DECISION_WORK_BRIEF_PACKETS_SCHEMA_VERSION,
    DECISION_WORK_BRIEF_SCHEMA_VERSION,
    NON_CLAIMS,
    DecisionWorkBriefPacketInputError,
    build_decision_work_brief_packets,
    render_decision_work_brief_packets_json,
    validate_output_path,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-packet-builder-v0.md"
)
PRD_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-prd-v0.md"
)
SCHEMA_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-v0.json"
)
SCHEMA_DOC_PATH = (
    REPO_ROOT
    / "docs/conversation-understanding/decision-work-brief-schema-v0.md"
)

REQUIRED_CUSTODY_FALSE_FIELDS = {
    "runtime_invoked",
    "skill_invoked",
    "archive_mutated",
    "brief_generated",
    "semantic_interpretation_performed",
    "human_validated",
    "product_proof",
    "answer_quality_scored",
    "agent_action_authorized",
    "provider_text_included",
}
SECTION_REQUIRED_FIELDS = {
    "future_question",
    "allowed_sources",
    "available_source_refs",
    "unavailable_or_redacted_sources",
    "known_limits",
    "interpretation_required",
    "required_output_contract_ref",
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
    REPO_ROOT / "engine" / "system_b" / "decision_work_brief_draft_pilot.py",
    REPO_ROOT / "scripts" / "evals" / "draft_decision_work_brief.py",
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


def test_default_metadata_only_packet_has_conservative_custody(
    tmp_path: Path,
) -> None:
    packet = build_decision_work_brief_packets(run_dir=_minimal_run_dir(tmp_path))

    assert packet["schema_version"] == DECISION_WORK_BRIEF_PACKETS_SCHEMA_VERSION
    assert packet["mode"] == "metadata_only"
    assert packet["packet_metadata"]["case_id"] == "sample-case"
    assert packet["packet_metadata"]["run_id"] == "20260701T000000Z_packet"
    assert packet["required_future_output"]["schema_version"] == (
        DECISION_WORK_BRIEF_SCHEMA_VERSION
    )
    assert set(packet["required_future_output"]["target_sections"]) == set(
        BRIEF_SECTIONS
    )

    custody = packet["custody_flags"]
    assert custody["checked_in_safe"] is True
    assert custody["unsafe_for_commit"] is False
    assert custody["raw_private_content_included"] is False
    assert custody["model_calls"] == 0
    for field in REQUIRED_CUSTODY_FALSE_FIELDS:
        assert custody[field] is False
    assert set(packet["non_claims"]) >= set(NON_CLAIMS)


def test_all_brief_packet_sections_are_present_and_require_future_output(
    tmp_path: Path,
) -> None:
    packet = build_decision_work_brief_packets(run_dir=_minimal_run_dir(tmp_path))

    assert set(packet["packet_sections"]) == set(BRIEF_SECTIONS)
    for section_id, section in packet["packet_sections"].items():
        assert section["section_id"] == section_id
        assert section["target_brief_section"] == section_id
        assert SECTION_REQUIRED_FIELDS <= set(section)
        assert section["future_question"]
        assert section["allowed_sources"]
        assert section["interpretation_required"] is True
        assert section["required_output_contract_ref"]["schema_version"] == (
            DECISION_WORK_BRIEF_SCHEMA_VERSION
        )
        assert section["required_output_contract_ref"]["brief_section"] == section_id


def test_metadata_only_records_raw_private_availability_without_reading_text(
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
        packet = build_decision_work_brief_packets(run_dir=run_dir)

    rendered = render_decision_work_brief_packets_json(packet, pretty=True)
    for marker in raw_markers.values():
        assert marker not in rendered
    assert str(run_dir) not in rendered
    assert "/User" + "s/" not in rendered

    refs = {record["artifact"]: record for record in packet["input_refs"]}
    assert refs["conversation.txt"]["status"] == "available_but_redacted_in_safe_mode"
    assert refs["conversation.txt"]["read_status"] == "not_read_redacted_safe_mode"
    assert refs["operator.log"]["status"] == "available_in_private_artifact_not_exported"
    assert refs["operator.log"]["read_status"] == "not_read_private_not_exported"
    assert all(record["content_included"] is False for record in packet["input_refs"])
    assert all(
        record["local_absolute_path_included"] is False
        for record in packet["input_refs"]
    )


def test_external_reports_link_by_metadata_without_path_or_content_leak(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    receipt_path = reports_dir / "decision-work-receipt.json"
    trail_path = reports_dir / "decision-trail-report.json"
    product_path = reports_dir / "product-delta-report.json"
    _write_json(
        receipt_path,
        {
            "schema_version": "lolla.decision_work_receipt.v0",
            "private_marker": "DO_NOT_COPY_RECEIPT_BODY",
        },
    )
    _write_json(
        trail_path,
        {
            "schema_version": "lolla.decision_trail_report.v0",
            "private_marker": "DO_NOT_COPY_TRAIL_BODY",
        },
    )
    _write_json(
        product_path,
        {
            "schema_version": "lolla.product_delta_report.v0",
            "private_marker": "DO_NOT_COPY_PRODUCT_BODY",
        },
    )

    packet = build_decision_work_brief_packets(
        run_dir=run_dir,
        decision_work_receipt_path=receipt_path,
        decision_trail_report_path=trail_path,
        product_delta_report_path=product_path,
    )
    rendered = render_decision_work_brief_packets_json(packet, pretty=True)
    report_refs = [
        record
        for record in packet["input_refs"]
        if record["source_kind"]
        in {"decision_work_receipt", "decision_trail_report", "product_delta_artifact"}
    ]

    assert all(
        record["status"] == "available_from_structured_artifact"
        for record in report_refs
    )
    assert all(record["content_included"] is False for record in report_refs)
    assert all(record["local_absolute_path_included"] is False for record in report_refs)
    assert str(reports_dir) not in rendered
    assert "DO_NOT_COPY_RECEIPT_BODY" not in rendered
    assert "DO_NOT_COPY_TRAIL_BODY" not in rendered
    assert "DO_NOT_COPY_PRODUCT_BODY" not in rendered
    assert packet["packet_sections"]["evidence_receipt"]["available_source_refs"]


def test_missing_optional_report_path_is_source_status_not_semantic_finding(
    tmp_path: Path,
) -> None:
    missing_report = tmp_path / "missing-decision-trail-report.json"

    packet = build_decision_work_brief_packets(
        run_dir=_minimal_run_dir(tmp_path),
        decision_trail_report_path=missing_report,
    )

    missing_refs = [
        record
        for record in packet["input_refs"]
        if record["source_kind"] == "decision_trail_report"
    ]
    assert len(missing_refs) == 1
    assert missing_refs[0]["status"] == "unavailable_missing_artifact"
    assert missing_refs[0]["read_status"] == "unavailable_missing_artifact"
    assert missing_refs[0]["content_included"] is False
    assert missing_refs[0]["local_absolute_path_included"] is False
    assert any("not a semantic finding" in note for note in missing_refs[0]["notes"])
    decision_section = packet["packet_sections"]["decision"]
    assert any(
        ref["source_status"] == "unavailable_missing_artifact"
        for ref in decision_section["unavailable_or_redacted_sources"]
    )


def test_output_path_inside_run_directory_is_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(DecisionWorkBriefPacketInputError, match="outside run directory"):
        validate_output_path(output_path=run_dir / "packets.json", run_dir=run_dir)


def test_include_private_text_requires_local_private_mode(tmp_path: Path) -> None:
    with pytest.raises(DecisionWorkBriefPacketInputError, match="local_private"):
        build_decision_work_brief_packets(
            run_dir=_minimal_run_dir(tmp_path),
            include_private_text=True,
        )


def test_local_private_include_text_marks_output_unsafe_and_includes_capped_text(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    raw_markers = _add_raw_private_artifacts(run_dir)

    packet = build_decision_work_brief_packets(
        run_dir=run_dir,
        mode="local_private",
        include_private_text=True,
        max_text_chars=32,
    )

    custody = packet["custody_flags"]
    assert custody["checked_in_safe"] is False
    assert custody["unsafe_for_commit"] is True
    assert custody["requires_operator_review_before_share"] is True
    assert custody["raw_private_content_included"] is True
    assert custody["raw_transcript_included"] is True
    assert custody["raw_revised_answer_included"] is True
    assert custody["raw_memo_included"] is True

    conversation = next(
        record for record in packet["input_refs"] if record["artifact"] == "conversation.txt"
    )
    assert conversation["content_included"] is True
    assert conversation["raw_private_content_included"] is True
    assert conversation["text_truncated"] is True
    assert "PRIVATE CONVERSATION MARKER" in conversation["content_excerpt"]

    rendered = render_decision_work_brief_packets_json(packet, pretty=True)
    assert "PRIVATE CONVERSATION MARKER" in rendered
    assert raw_markers["operator.log"][:20] in rendered
    assert str(run_dir) not in rendered


def test_cli_writes_metadata_only_packet_and_rejects_run_dir_output(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    output_path = tmp_path / "packets.json"

    ok = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_work_brief_packets.py",
            "--run-dir",
            str(run_dir),
            "--out",
            str(output_path),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ok.returncode == 0, ok.stderr
    packet = json.loads(output_path.read_text(encoding="utf-8"))
    assert packet["schema_version"] == DECISION_WORK_BRIEF_PACKETS_SCHEMA_VERSION
    assert packet["mode"] == "metadata_only"
    assert packet["custody_flags"]["checked_in_safe"] is True

    bad = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_work_brief_packets.py",
            "--run-dir",
            str(run_dir),
            "--out",
            str(run_dir / "packets.json"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert bad.returncode == 2
    assert "outside run directory" in bad.stderr


def test_cli_local_private_include_text_rejects_repo_output(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    _add_raw_private_artifacts(run_dir)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_work_brief_packets.py",
            "--run-dir",
            str(run_dir),
            "--mode",
            "local_private",
            "--include-private-text",
            "--out",
            str(REPO_ROOT / "decision-work-brief-private-packets.json"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "outside repository" in result.stderr


def test_pr115_product_delta_boundary_lint_accepts_doc_and_metadata_packet(
    tmp_path: Path,
) -> None:
    packet_path = tmp_path / "metadata-only-packet.json"
    packet = build_decision_work_brief_packets(run_dir=_minimal_run_dir(tmp_path))
    packet_path.write_text(
        render_decision_work_brief_packets_json(packet, pretty=True),
        encoding="utf-8",
    )

    report = lint_product_delta_paths([DOC_PATH, packet_path])

    assert report["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }


def test_packet_builder_does_not_add_production_brief_generator() -> None:
    for path in FUTURE_IMPLEMENTATION_FILES:
        assert not path.exists()


def test_pr115_artifacts_have_no_privacy_markers() -> None:
    text = "\n".join(
        [
            DOC_PATH.read_text(encoding="utf-8"),
            PRD_PATH.read_text(encoding="utf-8"),
            SCHEMA_PATH.read_text(encoding="utf-8"),
            SCHEMA_DOC_PATH.read_text(encoding="utf-8"),
            Path(__file__).read_text(encoding="utf-8"),
        ]
    )

    for marker in PRIVACY_MARKERS:
        assert marker not in text
