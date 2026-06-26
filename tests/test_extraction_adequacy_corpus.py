from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.extraction_adequacy_corpus import (
    EXTRACTION_ADEQUACY_CORPUS_MANIFEST_SCHEMA_VERSION,
    EXTRACTION_ADEQUACY_CORPUS_RECORD_SCHEMA_VERSION,
    build_extraction_adequacy_corpus_manifest,
    build_extraction_adequacy_corpus_records,
    write_json,
    write_jsonl,
)
from engine.system_b.extraction_adequacy_report import write_extraction_adequacy_report


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_run(
    archive_root: Path,
    *,
    case_id: str = "case-a",
    run_id: str = "20260626T120000Z_abcd12",
    include_report: bool = True,
    include_conversation: bool = True,
    include_extraction: bool = True,
    introduced_turn: object = 1,
    dropped_turn: object = 2,
    omit_live_turn_ref: bool = False,
    omit_dropped_turn_ref: bool = False,
    assistant_only_live_turn: bool = False,
    quote_validation: dict | None = None,
) -> Path:
    run_dir = archive_root / case_id / run_id
    run_dir.mkdir(parents=True)
    if include_conversation:
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
        if assistant_only_live_turn:
            conversation += (
                "\n\n[Turn 3] ASSISTANT:\n"
                "Assistant-only turn for speaker mismatch fixture.\n"
            )
        (run_dir / "conversation.txt").write_text(conversation, encoding="utf-8")

    if include_extraction:
        live_constraint = {
            "constraint": "six months runway",
            "introduced_turn": introduced_turn,
            "status": "active",
            "weight": "structural",
        }
        if omit_live_turn_ref:
            live_constraint.pop("introduced_turn")
        dropped_thread = {
            "thread": "spouse comfort",
            "raised_by": "user",
            "raised_turn": dropped_turn,
            "status": "acknowledged_then_dropped",
        }
        if omit_dropped_turn_ref:
            dropped_thread.pop("raised_turn")
        _write_json(
            run_dir / "extraction.json",
            {
                "status": "ok",
                "capture_health": "good",
                "capture_adequacy": {
                    "schema_version": "lolla.capture_adequacy.v0",
                    "status": "good",
                    "capture_strategy": "full",
                    "declared_turn_count": 4,
                    "captured_turn_count": 4,
                    "omitted_turn_count": 0,
                    "captured_windows": [
                        {
                            "label": "full",
                            "start_turn": 1,
                            "end_turn": 4,
                            "turn_count": 4,
                        }
                    ],
                    "omitted_windows": [],
                    "risk_flags": [],
                    "notes": [],
                },
                "extraction": {
                    "decision_situation": "Founder deciding whether to pivot",
                    "live_constraints": [live_constraint],
                    "synthesized_position": "Pivot only after customer evidence.",
                    "reasoning_passages": ["Only pivot after a customer evidence gate."],
                    "original_framing": "Should the founder pivot?",
                    "dropped_threads": [dropped_thread],
                    "_quote_validation": quote_validation
                    or {
                        "total": 1,
                        "verified": 1,
                        "fabricated": 0,
                        "fabricated_passages": [],
                    },
                },
            },
        )

    _write_json(
        run_dir / "agent_result.json",
        {
            "schema_version": "lolla_agent_result.v1",
            "status": "ok",
            "caller_action": "use_revised_answer",
        },
    )
    _write_json(
        run_dir / "evaluation.json",
        {
            "schema_version": "lolla.evaluation.v0",
            "overall": "pass",
            "caller_readiness": "ready",
        },
    )
    if include_report:
        write_extraction_adequacy_report(run_dir, run_id=run_id, case_id=case_id)
    return run_dir


def _record(records: list[dict], case_id: str) -> dict:
    for record in records:
        if record["case_id"] == case_id:
            return record
    raise AssertionError(f"missing record for {case_id}")


def test_modern_archive_uses_existing_report(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root)

    records = build_extraction_adequacy_corpus_records(archive_root)

    assert len(records) == 1
    record = records[0]
    assert record["schema_version"] == EXTRACTION_ADEQUACY_CORPUS_RECORD_SCHEMA_VERSION
    assert record["record_status"] == "valid"
    assert record["report_available"] is True
    assert record["report_built_in_memory"] is False
    assert record["adequacy_status"] == "good"
    assert record["capture_adequacy_status"] == "good"
    assert record["invalid_turn_ref_count"] == 0
    assert record["missing_turn_ref_count"] == 0
    assert record["speaker_mismatch_count"] == 0
    assert record["conversation_context_available"] is True
    assert record["conversation_ir_available"] is True
    assert record["conversation_ir_provenance_counts"]["turn_ref"] == 2
    assert record["evaluation_overall"] == "pass"
    assert record["agent_result_status"] == "ok"
    assert record["caller_action"] == "use_revised_answer"
    assert record["recommended_review_bucket"] == "clean_baseline_sample"
    assert record["scope"]["local_only"] is True
    assert record["scope"]["shareable_without_review"] is False


def test_older_archive_without_report_is_built_in_memory_read_only(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _seed_run(archive_root, case_id="legacy-case", include_report=False)

    records = build_extraction_adequacy_corpus_records(archive_root)
    record = records[0]

    assert record["record_status"] == "valid"
    assert record["report_available"] is False
    assert record["report_built_in_memory"] is True
    assert record["adequacy_status"] == "good"
    assert record["recommended_review_bucket"] == "legacy_missing_report_review"
    assert not (run_dir / "extraction_adequacy_report.json").exists()


def test_missing_conversation_and_missing_extraction_are_critical(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        case_id="missing-conversation",
        include_report=False,
        include_conversation=False,
    )
    _seed_run(
        archive_root,
        case_id="missing-extraction",
        include_report=False,
        include_extraction=False,
    )

    records = build_extraction_adequacy_corpus_records(archive_root)

    missing_conversation = _record(records, "missing-conversation")
    missing_extraction = _record(records, "missing-extraction")
    assert missing_conversation["adequacy_status"] == "critical"
    assert missing_conversation["recommended_review_bucket"] == "critical_extraction_review"
    assert missing_extraction["adequacy_status"] == "critical"
    assert missing_extraction["recommended_review_bucket"] == "critical_extraction_review"


def test_turn_ref_problem_counts_and_buckets(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        case_id="invalid-ref",
        include_report=False,
        introduced_turn=99,
    )
    _seed_run(
        archive_root,
        case_id="missing-ref",
        include_report=False,
        omit_live_turn_ref=True,
        omit_dropped_turn_ref=True,
    )
    _seed_run(
        archive_root,
        case_id="speaker-mismatch",
        include_report=False,
        introduced_turn=3,
        assistant_only_live_turn=True,
    )

    records = build_extraction_adequacy_corpus_records(archive_root)
    invalid_ref = _record(records, "invalid-ref")
    missing_ref = _record(records, "missing-ref")
    speaker_mismatch = _record(records, "speaker-mismatch")

    assert invalid_ref["adequacy_status"] == "critical"
    assert invalid_ref["invalid_turn_ref_count"] == 1
    assert invalid_ref["recommended_review_bucket"] == "critical_extraction_review"
    assert missing_ref["adequacy_status"] == "warn"
    assert missing_ref["missing_turn_ref_count"] == 2
    assert missing_ref["recommended_review_bucket"] == "warning_extraction_review"
    assert speaker_mismatch["adequacy_status"] == "warn"
    assert speaker_mismatch["speaker_mismatch_count"] == 1
    assert speaker_mismatch["recommended_review_bucket"] == "warning_extraction_review"


def test_quote_fabrication_count_does_not_copy_fabricated_passage_text(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        include_report=False,
        quote_validation={
            "total": 2,
            "verified": 1,
            "fabricated": 1,
            "fabricated_passages": ["SECRET FABRICATED PASSAGE 8821"],
        },
    )

    records = build_extraction_adequacy_corpus_records(archive_root)
    serialized = json.dumps(records)

    assert records[0]["quote_fabrication_count"] == 1
    assert "SECRET FABRICATED PASSAGE 8821" not in serialized


def test_malformed_archive_entry_is_invalid_without_crashing(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    bad_run = archive_root / "bad-case" / "bad-run"
    bad_run.mkdir(parents=True)
    (bad_run / "result.json").write_text("{not-json", encoding="utf-8")

    records = build_extraction_adequacy_corpus_records(archive_root)

    assert len(records) == 1
    assert records[0]["record_status"] == "invalid"
    assert records[0]["recommended_review_bucket"] == "not_reviewable"
    assert records[0]["record_errors"] == ["result.json is not valid JSON"]


def test_malformed_extraction_is_invalid_even_when_report_builds(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _seed_run(archive_root, case_id="bad-extraction", include_report=False)
    (run_dir / "extraction.json").write_text("{not-json", encoding="utf-8")

    records = build_extraction_adequacy_corpus_records(archive_root)
    serialized = json.dumps(records)

    assert records[0]["record_status"] == "invalid"
    assert records[0]["report_built_in_memory"] is True
    assert records[0]["record_errors"] == ["extraction.json is not valid JSON"]
    assert "JSONDecodeError" not in serialized
    assert "Expecting" not in serialized


def test_privacy_marker_in_malformed_field_does_not_enter_corpus(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        include_report=False,
        introduced_turn="SECRET-TURN-LEAK-999",
    )

    records = build_extraction_adequacy_corpus_records(archive_root)
    serialized = json.dumps(records)

    assert records[0]["adequacy_status"] == "critical"
    assert "SECRET-TURN-LEAK-999" not in serialized
    assert "invalid literal" not in serialized


def test_manifest_counts_and_json_outputs_are_deterministic(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root, case_id="modern-case")
    _seed_run(archive_root, case_id="legacy-case", include_report=False)
    bad_run = archive_root / "bad-case" / "bad-run"
    bad_run.mkdir(parents=True)
    (bad_run / "result.json").write_text("{not-json", encoding="utf-8")

    records = build_extraction_adequacy_corpus_records(archive_root)
    manifest = build_extraction_adequacy_corpus_manifest(archive_root, records)

    assert [record["case_id"] for record in records] == [
        "bad-case",
        "legacy-case",
        "modern-case",
    ]
    assert manifest["schema_version"] == EXTRACTION_ADEQUACY_CORPUS_MANIFEST_SCHEMA_VERSION
    assert manifest["record_count"] == 3
    assert manifest["valid_record_count"] == 2
    assert manifest["invalid_record_count"] == 1
    assert manifest["adequacy_status_counts"] == {"good": 2, "unknown": 1}
    assert manifest["report_available_count"] == 1
    assert manifest["report_missing_count"] == 2
    assert manifest["report_built_in_memory_count"] == 1
    assert manifest["recommended_review_buckets"] == {
        "clean_baseline_sample": 1,
        "legacy_missing_report_review": 1,
        "not_reviewable": 1,
    }
    assert manifest["scope"]["local_only"] is True
    assert manifest["scope"]["shareable_without_review"] is False

    jsonl_path = tmp_path / "extraction_adequacy.jsonl"
    manifest_path = tmp_path / "extraction_adequacy.manifest.json"
    write_jsonl(records, jsonl_path)
    write_json(manifest, manifest_path)
    first_jsonl = jsonl_path.read_text(encoding="utf-8")
    first_manifest = manifest_path.read_text(encoding="utf-8")
    write_jsonl(build_extraction_adequacy_corpus_records(archive_root), jsonl_path)
    write_json(
        build_extraction_adequacy_corpus_manifest(archive_root, records),
        manifest_path,
    )

    assert jsonl_path.read_text(encoding="utf-8") == first_jsonl
    assert manifest_path.read_text(encoding="utf-8") == first_manifest
    assert len(first_jsonl.splitlines()) == 3
