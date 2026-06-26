from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.semantic_coverage_corpus import (
    SEMANTIC_COVERAGE_CORPUS_MANIFEST_SCHEMA_VERSION,
    SEMANTIC_COVERAGE_CORPUS_RECORD_SCHEMA_VERSION,
    build_semantic_coverage_corpus_manifest,
    build_semantic_coverage_corpus_records,
    write_json,
    write_jsonl,
)
from engine.system_b.semantic_coverage_report import write_semantic_coverage_report


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_run(
    archive_root: Path,
    *,
    case_id: str = "case-a",
    run_id: str = "run-a",
    include_semantic_report: bool = False,
    include_optional: bool = True,
    include_extraction: bool = True,
    live_constraints: list[dict] | None = None,
) -> Path:
    run_dir = archive_root / case_id / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "conversation.txt").write_text(
        "CONVERSATION: 4 turns, 2 user messages, 2 assistant responses\n\n"
        "[Turn 1] USER:\n"
        "SECRET TRANSCRIPT. Should we launch the beta with six users?\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Wait for a customer-success gate before launching.\n\n"
        "[Turn 2] USER:\n"
        "SECRET PUSHBACK. The sales team needs a proof point this week.\n\n"
        "[Turn 2] ASSISTANT:\n"
        "Use a smaller proof point and keep the launch gated.\n",
        encoding="utf-8",
    )
    constraints = live_constraints
    if constraints is None:
        constraints = [
            {
                "constraint": "six users are ready",
                "introduced_turn": 1,
                "status": "active",
                "weight": "structural",
            },
            {
                "constraint": "sales needs a proof point this week",
                "introduced_turn": 2,
                "status": "active",
                "weight": "structural",
            },
        ]
    if include_extraction:
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
                    "captured_windows": [],
                    "omitted_windows": [],
                    "risk_flags": [],
                    "notes": [],
                },
                "extraction": {
                    "decision_situation": "Whether to launch a beta",
                    "live_constraints": constraints,
                    "synthesized_position": "Launch only behind a gate.",
                    "reasoning_passages": [
                        "Wait for a customer-success gate before launching."
                    ],
                    "original_framing": "Launch the beta now?",
                    "dropped_threads": [
                        {
                            "thread": "customer-success launch gate",
                            "raised_by": "assistant",
                            "raised_turn": 1,
                            "status": "acknowledged_then_dropped",
                        }
                    ],
                    "_quote_validation": {
                        "total": 1,
                        "verified": 1,
                        "fabricated": 0,
                        "fabricated_passages": ["SECRET FABRICATED PASSAGE"],
                    },
                },
            },
        )
    _write_json(
        run_dir / "extraction_adequacy_report.json",
        {
            "schema_version": "lolla.extraction_adequacy_report.v0",
            "adequacy_status": "good",
            "extraction_field_summary": {
                "decision_situation_present": True,
                "live_constraints_count": len(constraints),
                "dropped_threads_count": 1,
                "reasoning_passages_count": 1,
                "quote_validation": {
                    "present": True,
                    "total": 1,
                    "verified": 1,
                    "fabricated": 0,
                },
            },
            "provenance_gap_findings": {
                "missing_turn_ref_count": 0,
                "invalid_turn_ref_count": 0,
                "speaker_mismatch_count": 0,
            },
        },
    )
    if include_optional:
        _write_json(
            run_dir / "result.json",
            {
                "audit_summary": "SECRET AUDIT SUMMARY",
                "delta_card": {"present": True},
                "frame_pressure_card": {"present": True},
                "structural_coverage_card": {"present": True},
                "has_gap_check": True,
                "gap_check_summary": "SECRET GAP SUMMARY",
                "revised_answer_present": True,
                "memo_substantive_title": "SECRET MEMO TITLE",
                "memo_what_changed": "SECRET CHANGE",
                "memo_take_back_or_set_aside": "SECRET TAKEBACK",
            },
        )
        (run_dir / "revised.txt").write_text("SECRET REVISED", encoding="utf-8")
        (run_dir / "memo.md").write_text("SECRET MEMO", encoding="utf-8")
        _write_json(run_dir / "reasoning_trace.json", {"artifacts": []})
        _write_json(run_dir / "evaluation.json", {"checks": [], "overall": "partial"})
        _write_json(
            run_dir / "agent_result.json",
            {
                "status": "partial",
                "caller_action": "do_not_use_run_degraded",
                "changed_advice_summary": "SECRET CHANGE",
                "do_not_act_before": ["SECRET GATE"],
                "human_questions": ["SECRET QUESTION"],
            },
        )
    if include_semantic_report:
        write_semantic_coverage_report(run_dir, run_dir / "semantic_coverage_report.json")
    return run_dir


def _record(records: list[dict], case_id: str) -> dict:
    for record in records:
        if record["case_id"] == case_id:
            return record
    raise AssertionError(f"missing record for {case_id}")


def _file_snapshot(run_dir: Path) -> list[str]:
    return sorted(str(path.relative_to(run_dir)) for path in run_dir.rglob("*") if path.is_file())


def test_modern_archive_fixture_exports_valid_existing_report(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root, include_semantic_report=True)

    records = build_semantic_coverage_corpus_records(archive_root)
    record = records[0]

    assert record["schema_version"] == SEMANTIC_COVERAGE_CORPUS_RECORD_SCHEMA_VERSION
    assert record["valid"] is True
    assert record["record_status"] == "valid"
    assert record["report_available"] is True
    assert record["report_built_in_memory"] is False
    assert record["archive_relpath"] == "case-a/run-a"
    assert record["semantic_element_statuses"]["decision"] == "present"
    assert record["semantic_element_statuses"]["live_constraints"] == "partial"
    assert record["semantic_element_grounding"]["live_constraints"] == "turn_ref"
    assert record["semantic_element_statuses"][
        "user_values_or_priorities_signal"
    ] == "not_measured"
    assert record["recommended_review_bucket"] == "semantic_gap_review"
    assert record["source"]["absolute_archive_paths_included"] is False


def test_missing_optional_artifacts_degrade_without_invalidating_record(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root, include_optional=False)

    record = build_semantic_coverage_corpus_records(archive_root)[0]

    assert record["valid"] is True
    assert record["report_available"] is False
    assert record["report_built_in_memory"] is True
    assert record["semantic_element_statuses"]["counter_pressure"] == "missing"
    assert record["artifact_availability"]["missing_artifact_count"] > 0
    assert record["recommended_review_bucket"] == "legacy_semantic_backfill"


def test_malformed_run_becomes_invalid_deterministically(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = archive_root / "bad-case" / "bad-run"
    run_dir.mkdir(parents=True)
    (run_dir / "result.json").write_text("{not-json", encoding="utf-8")

    record = build_semantic_coverage_corpus_records(archive_root)[0]
    serialized = json.dumps(record)

    assert record["valid"] is False
    assert record["record_status"] == "invalid"
    assert record["recommended_review_bucket"] == "invalid_or_unreadable"
    assert record["record_errors"] == ["invalid json artifacts present"]
    assert "JSONDecodeError" not in serialized
    assert "Expecting" not in serialized


def test_output_is_deterministic(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root, case_id="z-case")
    _seed_run(archive_root, case_id="a-case")

    first_records = build_semantic_coverage_corpus_records(archive_root)
    second_records = build_semantic_coverage_corpus_records(archive_root)
    first_manifest = build_semantic_coverage_corpus_manifest(archive_root, first_records)
    second_manifest = build_semantic_coverage_corpus_manifest(archive_root, second_records)

    assert [record["case_id"] for record in first_records] == ["a-case", "z-case"]
    assert json.dumps(first_records, sort_keys=True) == json.dumps(
        second_records,
        sort_keys=True,
    )
    assert json.dumps(first_manifest, sort_keys=True) == json.dumps(
        second_manifest,
        sort_keys=True,
    )


def test_no_raw_text_or_absolute_paths_leak(tmp_path: Path) -> None:
    archive_root = tmp_path / "Users" / "marcin" / "SECRET_HOME" / "runs"
    _seed_run(archive_root)

    records = build_semantic_coverage_corpus_records(archive_root)
    manifest = build_semantic_coverage_corpus_manifest(archive_root, records)
    rendered = json.dumps(records, sort_keys=True) + json.dumps(manifest, sort_keys=True)

    assert "SECRET" not in rendered
    assert "SECRET_HOME" not in rendered
    assert "/Users/" not in rendered
    assert "SECRET FABRICATED PASSAGE" not in rendered
    assert "case-a/run-a" in rendered


def test_archive_folders_are_not_mutated(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    run_dir = _seed_run(archive_root, include_semantic_report=False)
    before = _file_snapshot(run_dir)

    records = build_semantic_coverage_corpus_records(archive_root)
    after = _file_snapshot(run_dir)

    assert records[0]["report_built_in_memory"] is True
    assert before == after
    assert not (run_dir / "semantic_coverage_report.json").exists()


def test_manifest_aggregates_element_statuses_correctly(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root, case_id="modern-a")
    _seed_run(archive_root, case_id="legacy-b", include_optional=False)
    bad_run = archive_root / "bad-case" / "bad-run"
    bad_run.mkdir(parents=True)
    (bad_run / "result.json").write_text("{not-json", encoding="utf-8")

    records = build_semantic_coverage_corpus_records(archive_root)
    manifest = build_semantic_coverage_corpus_manifest(archive_root, records)

    assert manifest["schema_version"] == SEMANTIC_COVERAGE_CORPUS_MANIFEST_SCHEMA_VERSION
    assert manifest["record_count"] == 3
    assert manifest["valid_record_count"] == 2
    assert manifest["invalid_record_count"] == 1
    assert manifest["report_available_count"] == 0
    assert manifest["report_built_in_memory_count"] == 3
    assert manifest["semantic_element_status_counts"]["decision"] == {
        "missing": 1,
        "present": 2,
    }
    assert manifest["semantic_element_status_counts"]["counter_pressure"] == {
        "missing": 2,
        "present": 1,
    }
    assert manifest["semantic_element_grounding_counts"]["live_constraints"] == {
        "none": 1,
        "turn_ref": 2,
    }
    assert manifest["recommended_review_bucket_counts"] == {
        "invalid_or_unreadable": 1,
        "legacy_semantic_backfill": 1,
        "semantic_gap_review": 1,
    }

    jsonl_path = tmp_path / "semantic_coverage.jsonl"
    manifest_path = tmp_path / "semantic_coverage.manifest.json"
    write_jsonl(records, jsonl_path)
    write_json(manifest, manifest_path)

    assert len(jsonl_path.read_text(encoding="utf-8").splitlines()) == 3
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["record_count"] == 3
