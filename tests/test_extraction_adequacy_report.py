from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.extraction_adequacy_report import (
    EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION,
    build_extraction_adequacy_report,
    write_extraction_adequacy_report,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_run(
    tmp_path: Path,
    *,
    run_id: str = "adequacyrun",
    capture_adequacy: dict | None = None,
    quote_validation: dict | None = None,
    live_turn: int = 1,
    dropped_turn: int = 2,
) -> Path:
    run_dir = tmp_path / "case" / run_id
    run_dir.mkdir(parents=True)
    conversation = (
        "CONVERSATION: 2 turns, 2 user messages, 2 assistant responses\n\n"
        "[Turn 1] USER:\n"
        "Should I pivot? I have six months runway.\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Only pivot after a customer evidence gate.\n\n"
        "[Turn 2] USER:\n"
        "My spouse needs to be comfortable with the risk.\n\n"
        "[Turn 2] ASSISTANT:\n"
        "Make spouse alignment a gate before accepting the risk.\n"
    )
    (run_dir / "conversation.txt").write_text(conversation, encoding="utf-8")
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "capture_health": "good",
            "capture_manifest": {
                "declared_turns": 4,
                "actual_user_turns": 2,
                "actual_assistant_turns": 2,
                "truncation_applied": bool(
                    capture_adequacy
                    and capture_adequacy.get("capture_strategy") == "first_n_plus_last_n"
                ),
                "truncation_reason": "test truncation" if capture_adequacy else "",
            },
            "capture_adequacy": capture_adequacy
            or {
                "schema_version": "lolla.capture_adequacy.v0",
                "status": "good",
                "capture_strategy": "full",
                "declared_turn_count": 4,
                "captured_turn_count": 4,
                "omitted_turn_count": 0,
                "captured_windows": [
                    {"label": "full", "start_turn": 1, "end_turn": 4, "turn_count": 4}
                ],
                "omitted_windows": [],
                "risk_flags": [],
                "notes": [],
            },
            "extraction": {
                "decision_situation": "Founder deciding whether to pivot",
                "live_constraints": [
                    {
                        "constraint": "six months runway",
                        "introduced_turn": live_turn,
                        "status": "active",
                        "weight": "structural",
                    }
                ],
                "synthesized_position": "Pivot only after customer evidence.",
                "reasoning_passages": ["Only pivot after a customer evidence gate."],
                "original_framing": "Should the founder pivot?",
                "dropped_threads": [
                    {
                        "thread": "spouse comfort",
                        "raised_by": "user",
                        "raised_turn": dropped_turn,
                        "status": "acknowledged_then_dropped",
                    }
                ],
                "_quote_validation": quote_validation
                or {
                    "total": 1,
                    "verified": 1,
                    "fabricated": 0,
                    "fabricated_passages": [],
                    "retry_attempted": False,
                    "retry_succeeded": False,
                },
            },
        },
    )
    return run_dir


def test_clean_short_conversation_reports_current_chain_provenance(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)

    report = build_extraction_adequacy_report(
        run_dir,
        run_id="adequacyrun",
        case_id="case",
        created_at="2026-06-26T10:00:00Z",
    )

    assert report["schema_version"] == EXTRACTION_ADEQUACY_REPORT_SCHEMA_VERSION
    assert report["adequacy_status"] == "good"
    assert report["source_artifacts"]["conversation"]["present"] is True
    assert report["capture_summary"]["capture_adequacy_status"] == "good"
    assert report["extraction_field_summary"]["live_constraints_count"] == 1
    assert report["extraction_field_summary"]["dropped_threads_count"] == 1
    assert report["conversation_context_summary"]["parsed_turn_count"] == 4
    assert report["conversation_context_summary"]["user_turn_count"] == 2
    assert report["conversation_context_summary"]["assistant_turn_count"] == 2
    assert report["conversation_ir_provenance_summary"]["frame_anchors_count"] == 2
    assert report["conversation_ir_provenance_summary"]["user_issue_events_count"] == 2
    assert report["conversation_ir_provenance_summary"]["stance_events_count"] == 0
    provenance = report["conversation_ir_provenance_summary"]["provenance_kinds_count"]
    assert provenance["span"] == 0
    assert provenance["turn_ref"] == 2
    assert provenance["derivation"] == 2
    assert "live_constraints" in report["provenance_gap_findings"]["fields_only_turn_ref_grounded"]
    assert report["specialist_extractor_opportunities"]["specialists_were_run"] is False
    assert report["specialist_extractor_opportunities"]["live_constraints_extraction"][
        "could_improve_grounding"
    ] is True


def test_invalid_live_constraint_turn_ref_is_critical(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path, live_turn=99)

    report = build_extraction_adequacy_report(run_dir)

    assert report["adequacy_status"] == "critical"
    assert report["conversation_context_summary"]["parsed_turn_count"] == 4
    assert report["provenance_gap_findings"]["invalid_turn_ref_count"] == 1
    assert report["conversation_context_summary"]


def test_invalid_dropped_thread_turn_ref_is_critical(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path, dropped_turn=99)

    report = build_extraction_adequacy_report(run_dir)

    assert report["adequacy_status"] == "critical"
    assert report["provenance_gap_findings"]["invalid_turn_ref_count"] == 1


def test_missing_live_constraint_turn_ref_warns_without_being_invalid(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction["extraction"]["live_constraints"][0].pop("introduced_turn")
    _write_json(run_dir / "extraction.json", extraction)

    report = build_extraction_adequacy_report(run_dir)

    assert report["adequacy_status"] == "warn"
    assert report["extraction_turn_ref_summary"]["live_constraints"][
        "missing_turn_ref_count"
    ] == 1
    assert report["provenance_gap_findings"]["missing_turn_ref_count"] == 1
    assert report["provenance_gap_findings"]["invalid_turn_ref_count"] == 0


def test_missing_dropped_thread_turn_ref_warns_without_being_invalid(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction["extraction"]["dropped_threads"][0].pop("raised_turn")
    _write_json(run_dir / "extraction.json", extraction)

    report = build_extraction_adequacy_report(run_dir)

    assert report["adequacy_status"] == "warn"
    assert report["extraction_turn_ref_summary"]["dropped_threads"][
        "missing_turn_ref_count"
    ] == 1
    assert report["provenance_gap_findings"]["missing_turn_ref_count"] == 1
    assert report["provenance_gap_findings"]["invalid_turn_ref_count"] == 0


def test_live_constraint_speaker_mismatch_warns_and_excludes_valid_count(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    (run_dir / "conversation.txt").write_text(
        (run_dir / "conversation.txt").read_text(encoding="utf-8")
        + "\n\n[Turn 3] ASSISTANT:\nAssistant-only turn for mismatch fixture.\n",
        encoding="utf-8",
    )
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction["extraction"]["live_constraints"][0]["introduced_turn"] = 3
    _write_json(run_dir / "extraction.json", extraction)

    report = build_extraction_adequacy_report(run_dir)

    assert report["adequacy_status"] == "warn"
    live_refs = report["extraction_turn_ref_summary"]["live_constraints"]
    assert live_refs["speaker_mismatch_count"] == 1
    assert live_refs["valid_turn_ref_count"] == 0
    assert report["provenance_gap_findings"]["speaker_mismatch_count"] == 1


def test_sanitized_context_error_does_not_leak_malformed_turn_ref(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction["extraction"]["live_constraints"][0][
        "introduced_turn"
    ] = "SECRET-TURN-LEAK-123"
    _write_json(run_dir / "extraction.json", extraction)

    report = build_extraction_adequacy_report(run_dir)
    serialized = json.dumps(report)

    assert report["adequacy_status"] == "critical"
    assert report["provenance_gap_findings"][
        "context_load_error"
    ] == "conversation_context_load_failed:ValueError"
    assert "SECRET-TURN-LEAK-123" not in serialized
    assert "invalid literal" not in serialized


def test_quote_validation_fabrication_metadata_warns_without_copying_passages(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(
        tmp_path,
        quote_validation={
            "total": 3,
            "verified": 1,
            "fabricated": 2,
            "fabricated_passages": [
                "SECRET FABRICATED PASSAGE ONE",
                "SECRET FABRICATED PASSAGE TWO",
            ],
            "retry_attempted": True,
            "retry_succeeded": False,
        },
    )

    report = build_extraction_adequacy_report(run_dir)
    serialized = json.dumps(report)

    assert report["adequacy_status"] == "warn"
    quote = report["extraction_field_summary"]["quote_validation"]
    assert quote["fabricated"] == 2
    assert quote["fabricated_passage_count"] == 2
    assert quote["retry_attempted"] is True
    assert "SECRET FABRICATED PASSAGE" not in serialized


def test_truncated_capture_records_omitted_windows_and_warns(tmp_path: Path) -> None:
    run_dir = _seed_run(
        tmp_path,
        capture_adequacy={
            "schema_version": "lolla.capture_adequacy.v0",
            "status": "warn",
            "capture_strategy": "first_n_plus_last_n",
            "declared_turn_count": 40,
            "captured_turn_count": 18,
            "omitted_turn_count": 22,
            "captured_windows": [
                {"label": "opening", "start_turn": 1, "end_turn": 3, "turn_count": 3},
                {"label": "recent", "start_turn": 26, "end_turn": 40, "turn_count": 15},
            ],
            "omitted_windows": [{"start_turn": 4, "end_turn": 25, "turn_count": 22}],
            "risk_flags": ["middle_turns_omitted"],
            "notes": ["Middle turns were omitted."],
        },
    )

    report = build_extraction_adequacy_report(run_dir)

    assert report["adequacy_status"] == "warn"
    assert report["capture_summary"]["capture_strategy"] == "first_n_plus_last_n"
    assert report["capture_summary"]["omitted_turn_count"] == 22
    assert report["provenance_gap_findings"]["omitted_middle_window_count"] == 1


def test_report_does_not_include_raw_transcript_or_provider_reasoning_details(
    tmp_path: Path,
) -> None:
    run_dir = _seed_run(tmp_path)
    (run_dir / "conversation.txt").write_text(
        (run_dir / "conversation.txt").read_text(encoding="utf-8")
        + "\n[Turn 3] USER:\nPRIVATE TRANSCRIPT MARKER 7731\n",
        encoding="utf-8",
    )
    extraction = json.loads((run_dir / "extraction.json").read_text(encoding="utf-8"))
    extraction["provider_reasoning_details"] = "PRIVATE PROVIDER REASONING 9988"
    extraction["audit_summary"] = {"raw_message_content": "PRIVATE RAW MODEL 1122"}
    _write_json(run_dir / "extraction.json", extraction)

    report = build_extraction_adequacy_report(run_dir)
    serialized = json.dumps(report)

    assert "PRIVATE TRANSCRIPT MARKER 7731" not in serialized
    assert "PRIVATE PROVIDER REASONING 9988" not in serialized
    assert "PRIVATE RAW MODEL 1122" not in serialized
    assert "raw_message_content" not in serialized
    assert "provider_reasoning_details" not in serialized


def test_write_report_creates_archive_and_tmp_copy(tmp_path: Path) -> None:
    run_dir = _seed_run(tmp_path)
    tmp_copy = tmp_path / "tmp" / "lolla_run_extraction_adequacy_report.json"

    path, payload = write_extraction_adequacy_report(
        run_dir,
        run_id="adequacyrun",
        case_id="case",
        tmp_copy_path=tmp_copy,
    )

    assert path == run_dir / "extraction_adequacy_report.json"
    assert path.exists()
    assert tmp_copy.exists()
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == payload[
        "schema_version"
    ]
