from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from engine.system_b.decision_work_receipt import (
    DECISION_WORK_RECEIPT_SCHEMA_VERSION,
    DecisionWorkReceiptInputError,
    build_decision_work_receipt,
    render_decision_work_receipt_json,
    validate_output_path,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _minimal_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "runs" / "sample-case" / "20260630T000000Z_test"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "agent_result.json",
        {
            "schema_version": "lolla_agent_result.v1",
            "case_id": "sample-case",
            "run_id": "20260630T000000Z_test",
            "status": "ok",
        },
    )
    _write_json(
        run_dir / "evaluation.json",
        {
            "schema_version": "lolla.evaluation.v0",
            "case_id": "sample-case",
            "run_id": "20260630T000000Z_test",
            "overall": "pass",
        },
    )
    _write_json(
        run_dir / "reasoning_trace.json",
        {
            "schema_version": "lolla.reasoning_trace.v0.2",
            "case": {
                "case_id": "sample-case",
                "run_id": "20260630T000000Z_test",
            },
        },
    )
    _write_json(run_dir / "extraction_adequacy_report.json", {"status": "good"})
    _write_json(
        run_dir / "extraction.json",
        {
            "schema_version": "lolla.extraction.v0",
            "turns": [
                {
                    "turn_index": 1,
                    "speaker": "user",
                    "text": "STRUCTURED TURN TEXT NOT COPIED",
                },
                {
                    "turn_index": 2,
                    "speaker": "assistant",
                    "text": "STRUCTURED ASSISTANT TEXT NOT COPIED",
                },
                {"turn_index": 3, "speaker": "user", "text": "follow-up"},
                {"turn_index": 4, "speaker": "assistant", "text": "revision"},
            ],
            "capture_manifest": {
                "actual_user_turns": 2,
                "actual_assistant_turns": 2,
                "declared_turns": 4,
                "declared_user": 2,
                "declared_assistant": 2,
                "char_length": 2400,
                "last_turn_role": "ASSISTANT",
            },
            "capture_adequacy": {
                "schema_version": "lolla.capture_adequacy.v0",
                "status": "good",
                "capture_strategy": "full",
                "declared_turn_count": 4,
                "captured_turn_count": 4,
                "omitted_turn_count": 0,
                "risk_flags": [],
                "notes": [],
            },
            "capture_health": "good",
            "extraction": {
                "decision_situation": "Whether to use the revised recommendation.",
                "live_constraints": [],
                "dropped_threads": [],
            },
        },
    )
    _write_json(run_dir / "result.json", {"schema_version": "lolla.pipeline_result.v0"})
    _write_json(run_dir / "memo_note.json", {"schema_version": "lolla.memo_note.v0"})
    _write_json(run_dir / "run_events.json", {"schema_version": "lolla.run_events.v0"})
    return run_dir


def _add_challenge_artifacts(run_dir: Path, *, degraded_health: bool = False) -> None:
    run_health = {
        "overall": "healthy",
        "capture": "good",
        "substrate": "ok",
        "embeddings": "active",
        "fingerprint": "ok",
        "findings_produced": True,
        "issues": [],
        "warnings": [],
        "capture_truncated": False,
    }
    if degraded_health:
        run_health.update(
            {
                "overall": "degraded",
                "capture": "degraded",
                "fingerprint": "empty",
                "findings_produced": False,
                "issues": ["capture_truncated", "lane3_all_dropped"],
                "warnings": ["safe warning text"],
                "capture_truncated": True,
                "omitted_turns": 12,
                "capture_adequacy": {
                    "schema_version": "lolla.capture_adequacy.v0",
                    "status": "warn",
                    "capture_strategy": "first_n_plus_last_n",
                    "omitted_turn_count": 12,
                    "risk_flags": ["middle_turns_omitted"],
                },
            }
        )
    _write_json(
        run_dir / "result.json",
        {
            "schema_version": "lolla.pipeline_result.v0",
            "delta_card": {"findings": [{"tendency_name": "Overoptimism"}]},
            "companion_cheat_sheet": {"anchors": [{"display_name": "Inversion"}]},
            "companion_card": {"accepted": ["inversion"]},
            "frame_pressure_card": {"reframings": [{"reframed_question": "What could break?"}]},
            "structural_coverage_card": {
                "gap_questions": [{"dimension_id": "risk-response"}]
            },
            "bullshit_profile": {"summary": {"total_passages": 2}},
            "audit_summary": {
                "triggered_tendencies": ["overoptimism"],
                "boundary_call_count": 4,
                "warnings": [],
            },
            "v60_enrichment": {
                "status": "active",
                "telemetry": {"selected_chunk_count": 2},
            },
            "pressure_check_mode": "rested",
            "has_gap_check": False,
            "run_health": run_health,
        },
    )
    _write_json(run_dir / "gapcheck_lanes.json", {"lanes": [{"lane_name": "DeltaCard"}]})
    _write_json(
        run_dir / "graph_survival_report.json",
        {"schema_version": "lolla.graph_survival_report.v0"},
    )
    (run_dir / "pre_step6_private_table.json").write_text(
        "PRIVATE TABLE CONTENT NOT READ",
        encoding="utf-8",
    )


def _add_optional_review_artifacts(run_dir: Path) -> None:
    _write_json(
        run_dir / "decision_trail_report.json",
        {
            "schema_version": "lolla.decision_trail_report.v0",
            "report_metadata": {
                "report_id": "decision_trail_report:sample-case:20260630T000000Z_test"
            },
            "boundary": {
                "human_validated": False,
                "product_proof": False,
            },
        },
    )
    _write_json(
        run_dir / "product_delta_report.json",
        {
            "schema_version": "lolla.product_delta_provisional_report.v0",
            "review_metadata": {
                "review_id": "product_delta_report:sample-case:20260630T000000Z_test"
            },
            "human_validated": False,
            "product_proof": False,
        },
    )


def test_builds_sparse_receipt_with_source_inventory(tmp_path: Path) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))

    assert receipt["schema_version"] == DECISION_WORK_RECEIPT_SCHEMA_VERSION
    assert receipt["receipt_metadata"]["case_id"] == "sample-case"
    assert receipt["receipt_metadata"]["run_id"] == "20260630T000000Z_test"
    assert receipt["receipt_metadata"]["generated_by"] == "decision_work_receipt_exporter"
    assert receipt["source_context_inventory"]["status"] == "available_from_structured_artifact"
    assert receipt["source_context_inventory"]["receipt_mode"] == "checked_in_safe_mode"
    assert receipt["source_context_inventory"]["sources"]
    assert receipt["source_context_inventory"]["source_counts"]["total"] >= 20
    assert receipt["source_context_inventory"]["source_counts"]["structured_runtime_artifact"] >= 6
    assert receipt["source_context_inventory"]["source_counts"]["generated_runtime_artifact"] >= 5


def test_attachment_policy_records_pdf_gap_without_ingestion(tmp_path: Path) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))
    policy = receipt["source_context_inventory"]["attachment_custody_policy"]

    assert policy["attachments_are_first_class_archived_sources"] is False
    assert policy["pdf_ingestion_implemented"] is False
    assert policy["link_fetching_implemented"] is False
    assert policy["ocr_implemented"] is False
    assert policy["embeddings_or_chunking_implemented"] is False
    assert "attachments are not first-class archived sources" in policy["empty_meaning"]


def test_raw_private_artifacts_are_not_read_in_checked_in_safe_mode(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    raw_markers = {
        "conversation.txt": "RAW CONVERSATION DO NOT COPY",
        "memo.md": "RAW MEMO DO NOT COPY",
        "revised.txt": "RAW REVISED ANSWER DO NOT COPY",
        "live_transcript.txt": "RAW LIVE TRANSCRIPT DO NOT COPY",
        "operator.log": "RAW OPERATOR LOG DO NOT COPY",
        "pre_step6_private_table.json": "RAW PRIVATE TABLE DO NOT COPY",
        "v60_ledger.json": "RAW PRIVATE LEDGER DO NOT COPY",
    }
    for name, marker in raw_markers.items():
        (run_dir / name).write_text(marker, encoding="utf-8")

    original_read_text = Path.read_text

    def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path.name in raw_markers:
            raise AssertionError(f"raw artifact was read: {path.name}")
        return original_read_text(path, *args, **kwargs)

    with patch.object(Path, "read_text", guarded_read_text):
        receipt = build_decision_work_receipt(run_dir=run_dir)

    rendered = render_decision_work_receipt_json(receipt, pretty=True)
    for marker in raw_markers.values():
        assert marker not in rendered

    sources = {
        item["artifact_or_reference"]: item
        for item in receipt["source_context_inventory"]["sources"]
    }
    assert sources["conversation.txt"]["status"] == "available_but_redacted_in_safe_mode"
    assert sources["conversation.txt"]["read_status"] == "not_read_redacted_safe_mode"
    assert sources["operator.log"]["status"] == "available_in_private_artifact_not_exported"
    assert sources["operator.log"]["read_status"] == "not_read_private_not_exported"
    assert all(source["raw_private_content_included"] is False for source in sources.values())
    assert all(source["local_absolute_path_included"] is False for source in sources.values())


def test_missing_and_malformed_artifacts_are_statuses_not_crashes(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    (run_dir / "evaluation.json").unlink()
    (run_dir / "extraction.json").write_text("{not-json", encoding="utf-8")

    receipt = build_decision_work_receipt(run_dir=run_dir)
    sources = {
        item["artifact_or_reference"]: item
        for item in receipt["source_context_inventory"]["sources"]
    }

    assert sources["evaluation.json"]["status"] == "unavailable_missing_artifact"
    assert sources["evaluation.json"]["read_status"] == "unavailable_missing_artifact"
    assert sources["extraction.json"]["status"] == "unavailable_malformed_artifact"
    assert sources["extraction.json"]["read_status"] == "unavailable_malformed_artifact"
    assert receipt["missingness_and_redaction"]["missing_sources"]


def test_conversation_process_map_counts_structured_turns_without_text_copy(
    tmp_path: Path,
) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))
    process_map = receipt["conversation_process_map"]
    rendered = render_decision_work_receipt_json(receipt, pretty=True)

    assert process_map["status"] == "available_from_structured_artifact"
    assert process_map["source_status"] == "available_from_structured_artifact"
    assert process_map["turn_count"] == 4
    assert process_map["user_turn_count"] == 2
    assert process_map["assistant_turn_count"] == 2
    assert process_map["process_depth"] == "multi_turn_evidence"
    assert any("turn_count:4" in item for item in process_map["deterministic_process_evidence"])
    assert "raw conversation text was not read" in " ".join(
        process_map["deterministic_process_evidence"]
    )
    assert "STRUCTURED TURN TEXT NOT COPIED" not in rendered
    assert "STRUCTURED ASSISTANT TEXT NOT COPIED" not in rendered


def test_semantic_receipt_sections_remain_sparse_not_interpreted(tmp_path: Path) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))

    for field in receipt["conversation_process_map"]["semantic_process_fields"].values():
        assert field["status"] == "requires_llm_interpretation"
        assert field["requires_llm_interpretation"] is True
        assert field["exporter_inferred_from_prose"] is False
    assert receipt["challenge_coverage"]["status"] == "not_supplied"
    assert receipt["challenge_coverage"]["challenge_quality_scored"] is False
    assert receipt["decision_trail_summary"]["status"] == "not_supplied"
    assert receipt["product_delta_summary"]["status"] == "not_supplied"
    assert receipt["process_evidence_readiness"]["label"] == "multi_turn_unreviewed_process"
    assert receipt["process_evidence_readiness"]["status"] == "available_from_structured_artifact"
    assert receipt["process_evidence_readiness"]["answer_quality_scored"] is False


def test_optional_review_artifact_refs_make_receipt_review_ready_without_validation(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    _add_challenge_artifacts(run_dir)
    _add_optional_review_artifacts(run_dir)

    receipt = build_decision_work_receipt(run_dir=run_dir)
    sources = {
        item["artifact_or_reference"]: item
        for item in receipt["source_context_inventory"]["sources"]
    }

    assert sources["decision_trail_report.json"]["source_kind"] == "decision_trail_report"
    assert sources["decision_trail_report.json"]["status"] == "available_from_structured_artifact"
    assert sources["product_delta_report.json"]["source_kind"] == "product_delta_artifact"
    assert sources["product_delta_report.json"]["status"] == "available_from_structured_artifact"
    assert receipt["decision_trail_summary"]["status"] == "available_from_structured_artifact"
    assert receipt["product_delta_summary"]["status"] == "available_from_structured_artifact"
    assert receipt["decision_trail_summary"]["content_included"] is False
    assert receipt["product_delta_summary"]["content_included"] is False
    assert receipt["decision_trail_summary"]["human_validated"] is False
    assert receipt["product_delta_summary"]["human_validated"] is False
    assert receipt["decision_trail_summary"]["product_proof"] is False
    assert receipt["product_delta_summary"]["product_proof"] is False
    assert receipt["process_evidence_readiness"]["label"] == "decision_trail_review_ready"
    assert receipt["process_evidence_readiness"]["answer_quality_scored"] is False
    assert receipt["process_evidence_readiness"]["correctness_claimed"] is False
    assert receipt["process_evidence_readiness"]["agent_action_authorized"] is False
    assert any(
        item == "decision_trail_summary_reference_present:true"
        for item in receipt["process_evidence_readiness"]["deterministic_basis"]
    )
    assert any(
        item == "product_delta_summary_reference_present:true"
        for item in receipt["process_evidence_readiness"]["deterministic_basis"]
    )


def test_external_report_refs_make_receipt_review_ready_without_path_or_content_leak(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    _add_challenge_artifacts(run_dir)
    reports_dir = tmp_path / "external-reports"
    reports_dir.mkdir()
    decision_trail_report = reports_dir / "decision-trail-local-private.json"
    product_delta_report = reports_dir / "product-delta-review.json"
    _write_json(
        decision_trail_report,
        {
            "schema_version": "lolla.decision_trail_report.v0",
            "report_metadata": {"report_id": "dt:sample-case"},
            "private_marker": "DO_NOT_COPY_DECISION_TRAIL_CONTENT",
        },
    )
    _write_json(
        product_delta_report,
        {
            "schema_version": "lolla.product_delta_provisional_report.v0",
            "review_metadata": {"review_id": "pd:sample-case"},
            "private_marker": "DO_NOT_COPY_PRODUCT_DELTA_CONTENT",
        },
    )

    receipt = build_decision_work_receipt(
        run_dir=run_dir,
        decision_trail_report_paths=[decision_trail_report],
        product_delta_report_paths=[product_delta_report],
    )
    rendered = render_decision_work_receipt_json(receipt, pretty=True)
    sources = {
        item["artifact_or_reference"]: item
        for item in receipt["source_context_inventory"]["sources"]
    }
    external_decision_sources = [
        source for name, source in sources.items()
        if name.startswith("external_decision_trail_report_")
    ]
    external_product_sources = [
        source for name, source in sources.items()
        if name.startswith("external_product_delta_report_")
    ]

    assert len(external_decision_sources) == 1
    assert len(external_product_sources) == 1
    assert external_decision_sources[0]["source_kind"] == "decision_trail_report"
    assert external_product_sources[0]["source_kind"] == "product_delta_artifact"
    assert external_decision_sources[0]["status"] == "available_from_structured_artifact"
    assert external_product_sources[0]["status"] == "available_from_structured_artifact"
    assert external_decision_sources[0]["content_included"] is False
    assert external_product_sources[0]["content_included"] is False
    assert external_decision_sources[0]["local_absolute_path_included"] is False
    assert external_product_sources[0]["local_absolute_path_included"] is False
    assert str(reports_dir) not in rendered
    assert "DO_NOT_COPY_DECISION_TRAIL_CONTENT" not in rendered
    assert "DO_NOT_COPY_PRODUCT_DELTA_CONTENT" not in rendered
    assert receipt["decision_trail_summary"]["status"] == "available_from_structured_artifact"
    assert receipt["product_delta_summary"]["status"] == "available_from_structured_artifact"
    assert receipt["decision_trail_summary"]["content_included"] is False
    assert receipt["product_delta_summary"]["content_included"] is False
    assert receipt["decision_trail_summary"]["human_validated"] is False
    assert receipt["product_delta_summary"]["human_validated"] is False
    assert receipt["process_evidence_readiness"]["label"] == "decision_trail_review_ready"
    assert receipt["process_evidence_readiness"]["answer_quality_scored"] is False
    assert receipt["process_evidence_readiness"]["agent_action_authorized"] is False


def test_missing_external_report_path_is_status_not_crash(tmp_path: Path) -> None:
    missing_report = tmp_path / "missing-decision-trail-report.json"

    receipt = build_decision_work_receipt(
        run_dir=_minimal_run_dir(tmp_path),
        decision_trail_report_paths=[missing_report],
    )
    sources = {
        item["artifact_or_reference"]: item
        for item in receipt["source_context_inventory"]["sources"]
    }
    external_sources = [
        source for name, source in sources.items()
        if name.startswith("external_decision_trail_report_")
    ]

    assert len(external_sources) == 1
    assert external_sources[0]["status"] == "unavailable_missing_artifact"
    assert external_sources[0]["read_status"] == "unavailable_missing_artifact"
    assert external_sources[0]["local_absolute_path_included"] is False
    assert receipt["decision_trail_summary"]["status"] == "unavailable_missing_artifact"
    assert receipt["decision_trail_summary"]["summary"] is None
    assert receipt["process_evidence_readiness"]["label"] == "multi_turn_unreviewed_process"


def test_absent_optional_review_artifacts_are_not_listed_as_missing_sources(
    tmp_path: Path,
) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))
    missing_names = {
        item["artifact_or_reference"]
        for item in receipt["missingness_and_redaction"]["missing_sources"]
    }
    source_names = {
        item["artifact_or_reference"]
        for item in receipt["source_context_inventory"]["sources"]
    }

    assert "decision_trail_report.json" not in source_names
    assert "product_delta_report.json" not in source_names
    assert "decision_trail_report.json" not in missing_names
    assert "product_delta_report.json" not in missing_names
    assert any(
        "normally generated outside archive run folders" in limitation
        for limitation in receipt["decision_trail_summary"]["limitations"]
    )
    assert any(
        "offline eval-lane outputs" in limitation
        for limitation in receipt["product_delta_summary"]["limitations"]
    )


def test_malformed_optional_review_artifact_is_status_not_crash(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    (run_dir / "decision_trail_report.json").write_text("{not-json", encoding="utf-8")

    receipt = build_decision_work_receipt(run_dir=run_dir)

    assert receipt["decision_trail_summary"]["status"] == "unavailable_malformed_artifact"
    assert receipt["decision_trail_summary"]["summary"] is None
    assert receipt["process_evidence_readiness"]["label"] == "multi_turn_unreviewed_process"


def test_challenge_coverage_maps_present_surfaces_without_quality_claim(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    _add_challenge_artifacts(run_dir)

    receipt = build_decision_work_receipt(run_dir=run_dir)
    coverage = receipt["challenge_coverage"]
    surfaces = {surface["surface_id"]: surface for surface in coverage["surfaces"]}
    rendered = render_decision_work_receipt_json(receipt, pretty=True)

    assert coverage["status"] == "available_from_structured_artifact"
    assert coverage["challenge_quality_scored"] is False
    assert surfaces["lane1_structural_pressure"]["present"] is True
    assert surfaces["lane2_model_companion"]["present"] is True
    assert surfaces["lane3_frame_pressure"]["present"] is True
    assert surfaces["lane4_structural_coverage"]["present"] is True
    assert surfaces["delivery_bullshit_index"]["present"] is True
    assert surfaces["audit_summary_trace"]["present"] is True
    assert surfaces["v60_private_enrichment"]["present"] is True
    assert surfaces["optional_pressure_check_state"]["present"] is True
    assert surfaces["pre_step6_private_table"]["status"] == "available_in_private_artifact_not_exported"
    assert surfaces["pre_step6_private_table"]["present"] is True
    assert surfaces["graph_survival_report"]["present"] is True
    assert all(surface["quality_not_assessed"] is True for surface in coverage["surfaces"])
    assert receipt["process_evidence_readiness"]["label"] == "challenged_and_revised_process"
    assert receipt["process_evidence_readiness"]["answer_quality_scored"] is False
    assert "PRIVATE TABLE CONTENT NOT READ" not in rendered


def test_challenge_coverage_exposes_missing_or_malformed_lane_artifacts(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    (run_dir / "result.json").unlink()

    receipt = build_decision_work_receipt(run_dir=run_dir)
    surfaces = {surface["surface_id"]: surface for surface in receipt["challenge_coverage"]["surfaces"]}

    assert surfaces["lane1_structural_pressure"]["status"] == "unavailable_missing_artifact"
    assert surfaces["lane1_structural_pressure"]["present"] is False
    assert surfaces["lane2_model_companion"]["status"] == "unavailable_missing_artifact"
    assert receipt["process_evidence_readiness"]["label"] == "multi_turn_unreviewed_process"


def test_run_health_caveats_weaken_challenge_coverage_without_scoring(
    tmp_path: Path,
) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    _add_challenge_artifacts(run_dir, degraded_health=True)

    receipt = build_decision_work_receipt(run_dir=run_dir)
    caveats = receipt["challenge_coverage"]["run_health_caveats"]

    assert "run_health.overall:degraded" in caveats
    assert "run_health.capture:degraded" in caveats
    assert "run_health.fingerprint:empty" in caveats
    assert "run_health.findings_produced:false" in caveats
    assert "run_health.issue:capture_truncated" in caveats
    assert "run_health.issue:lane3_all_dropped" in caveats
    assert "run_health.warnings_count:1" in caveats
    assert "capture_adequacy.status:warn" in caveats
    assert "capture_adequacy.omitted_turn_count:12" in caveats
    assert "capture_adequacy.risk_flag:middle_turns_omitted" in caveats
    assert receipt["challenge_coverage"]["challenge_quality_scored"] is False
    assert receipt["process_evidence_readiness"]["label"] == "challenged_and_revised_process"


def test_capture_manifest_fallback_populates_process_map(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction.pop("turns")
    extraction["capture_manifest"]["truncation_applied"] = True
    extraction["capture_manifest"]["kept_turns"] = 18
    extraction["capture_manifest"]["omitted_turns"] = 12
    _write_json(run_dir / "extraction.json", extraction)

    receipt = build_decision_work_receipt(run_dir=run_dir)
    process_map = receipt["conversation_process_map"]

    assert process_map["turn_count"] == 4
    assert process_map["user_turn_count"] == 2
    assert process_map["assistant_turn_count"] == 2
    assert process_map["process_depth"] == "multi_turn_evidence"
    assert any("capture_manifest.omitted_turns:12" == item for item in process_map["deterministic_process_evidence"])


def test_one_shot_process_depth_is_not_quality_claim(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction["turns"] = [
        {"turn_index": 1, "speaker": "user", "text": "question"},
        {"turn_index": 2, "speaker": "assistant", "text": "answer"},
    ]
    extraction["capture_manifest"] = {
        "actual_user_turns": 1,
        "actual_assistant_turns": 1,
        "declared_turns": 2,
    }
    _write_json(run_dir / "extraction.json", extraction)

    receipt = build_decision_work_receipt(run_dir=run_dir)

    assert receipt["conversation_process_map"]["process_depth"] == "one_shot_candidate"
    assert receipt["process_evidence_readiness"]["label"] == "one_shot_or_thin_process"
    assert receipt["process_evidence_readiness"]["answer_quality_scored"] is False
    assert receipt["process_evidence_readiness"]["correctness_claimed"] is False
    assert "not a finding" in receipt["process_evidence_readiness"]["empty_meaning"]


def test_missing_process_metadata_stays_insufficient(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction.pop("turns")
    extraction.pop("capture_manifest")
    extraction.pop("capture_adequacy")
    extraction.pop("capture_health")
    _write_json(run_dir / "extraction.json", extraction)

    receipt = build_decision_work_receipt(run_dir=run_dir)

    assert receipt["conversation_process_map"]["status"] == "not_measured"
    assert receipt["conversation_process_map"]["turn_count"] is None
    assert receipt["conversation_process_map"]["process_depth"] == "not_measured"
    assert receipt["process_evidence_readiness"]["label"] == "insufficient_process_evidence"


def test_boundary_and_non_claims_are_conservative(tmp_path: Path) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))

    assert receipt["boundary"]["model_calls"] == 0
    assert receipt["boundary"]["provider_calls"] == 0
    for key, value in receipt["boundary"].items():
        if key not in {"model_calls", "provider_calls"}:
            assert value is False
    assert receipt["non_claims"]["not_answer_quality_scoring"] is True
    assert receipt["non_claims"]["not_correctness_proof"] is True
    assert receipt["non_claims"]["clean_artifacts_do_not_imply_good_advice"] is True


def test_output_path_inside_run_dir_is_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(DecisionWorkReceiptInputError, match="outside run directory"):
        validate_output_path(output_path=run_dir / "decision_work_receipt.json", run_dir=run_dir)


def test_unsupported_modes_are_rejected_with_sanitized_error(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(DecisionWorkReceiptInputError, match="checked_in_safe_mode"):
        build_decision_work_receipt(
            run_dir=run_dir,
            receipt_mode="local_private_mode",
        )


def test_cli_writes_json_and_rejects_output_inside_run_dir(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    output_path = tmp_path / "receipt.json"

    ok = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_work_receipt.py",
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
    receipt = json.loads(output_path.read_text(encoding="utf-8"))
    assert receipt["schema_version"] == DECISION_WORK_RECEIPT_SCHEMA_VERSION

    bad = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_work_receipt.py",
            "--run-dir",
            str(run_dir),
            "--out",
            str(run_dir / "receipt.json"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert bad.returncode == 2
    assert "outside run directory" in bad.stderr


def test_cli_links_external_reports_without_copying_content(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    output_path = tmp_path / "receipt.json"
    report_path = tmp_path / "decision-trail-report.json"
    _write_json(
        report_path,
        {
            "schema_version": "lolla.decision_trail_report.v0",
            "private_marker": "DO_NOT_COPY_CLI_REPORT_CONTENT",
        },
    )

    ok = subprocess.run(
        [
            sys.executable,
            "scripts/evals/build_decision_work_receipt.py",
            "--run-dir",
            str(run_dir),
            "--decision-trail-report",
            str(report_path),
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
    rendered = output_path.read_text(encoding="utf-8")
    receipt = json.loads(rendered)
    assert receipt["decision_trail_summary"]["status"] == "available_from_structured_artifact"
    assert receipt["process_evidence_readiness"]["label"] == "decision_trail_review_ready"
    assert str(report_path.parent) not in rendered
    assert "DO_NOT_COPY_CLI_REPORT_CONTENT" not in rendered


def test_generated_receipt_passes_boundary_lint(tmp_path: Path) -> None:
    output_path = tmp_path / "receipt.json"
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))
    output_path.write_text(
        render_decision_work_receipt_json(receipt, pretty=True),
        encoding="utf-8",
    )

    result = lint_product_delta_paths(
        [
            output_path,
            REPO_ROOT / "docs/conversation-understanding/decision-work-receipt-source-inventory-v0.md",
            REPO_ROOT / "docs/conversation-understanding/decision-work-receipt-v0.json",
        ]
    )

    assert result["summary"] == {
        "blocking_error_count": 0,
        "warning_count": 0,
        "info_count": 0,
    }
    assert result["findings"] == []
