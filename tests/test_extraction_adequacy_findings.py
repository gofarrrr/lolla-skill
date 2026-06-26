from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from scripts.analyze_extraction_adequacy_corpus import (
    FINDINGS_SCHEMA_VERSION,
    build_findings,
    main,
    render_json,
    render_markdown,
)


def _record(
    case_id: str,
    run_id: str,
    *,
    adequacy_status: str = "good",
    record_status: str = "valid",
    invalid_turn_ref_count: int = 0,
    missing_turn_ref_count: int = 0,
    speaker_mismatch_count: int = 0,
    quote_fabrication_count: int = 0,
    conversation_context_available: bool = True,
    conversation_ir_available: bool = True,
    fields_only_turn_ref_grounded: list[str] | None = None,
    fields_with_no_source_grounding: list[str] | None = None,
    record_errors: list[str] | None = None,
) -> dict:
    return {
        "schema_version": "lolla.extraction_adequacy_corpus_record.v0",
        "case_id": case_id,
        "run_id": run_id,
        "archive_path": f"/archive/{case_id}/{run_id}",
        "archive_relpath": f"{case_id}/{run_id}",
        "record_status": record_status,
        "record_errors": record_errors or [],
        "report_available": False,
        "report_built_in_memory": True,
        "adequacy_status": adequacy_status,
        "capture_adequacy_status": "unknown",
        "capture_strategy": "unknown",
        "invalid_turn_ref_count": invalid_turn_ref_count,
        "missing_turn_ref_count": missing_turn_ref_count,
        "speaker_mismatch_count": speaker_mismatch_count,
        "quote_fabrication_count": quote_fabrication_count,
        "omitted_turn_count": 0,
        "conversation_context_available": conversation_context_available,
        "conversation_ir_available": conversation_ir_available,
        "fields_only_turn_ref_grounded": fields_only_turn_ref_grounded or ["live_constraints"],
        "fields_with_no_source_grounding": fields_with_no_source_grounding
        or ["synthesized_position"],
        "specialist_extractor_opportunities": {
            "live_constraints_extraction": {
                "could_improve_grounding": True,
                "could_cover_assistant_recommendations": False,
                "current_count": 2,
            }
        },
        "recommended_review_bucket": (
            "critical_extraction_review"
            if adequacy_status == "critical"
            else "warning_extraction_review"
            if adequacy_status == "warn"
            else "legacy_missing_report_review"
        ),
    }


def _manifest(records: list[dict]) -> dict:
    adequacy_counts = Counter(record["adequacy_status"] for record in records)
    bucket_counts = Counter(record["recommended_review_bucket"] for record in records)
    return {
        "schema_version": "lolla.extraction_adequacy_corpus_manifest.v0",
        "record_count": len(records),
        "valid_record_count": sum(1 for record in records if record["record_status"] == "valid"),
        "invalid_record_count": sum(1 for record in records if record["record_status"] == "invalid"),
        "adequacy_status_counts": dict(adequacy_counts),
        "capture_adequacy_status_counts": {"unknown": len(records)},
        "capture_strategy_counts": {"unknown": len(records)},
        "report_available_count": 0,
        "report_missing_count": len(records),
        "report_built_in_memory_count": len(records),
        "invalid_turn_ref_total": sum(record["invalid_turn_ref_count"] for record in records),
        "missing_turn_ref_total": sum(record["missing_turn_ref_count"] for record in records),
        "speaker_mismatch_total": sum(record["speaker_mismatch_count"] for record in records),
        "quote_fabrication_total": sum(record["quote_fabrication_count"] for record in records),
        "omitted_turn_total": 0,
        "conversation_context_available_count": sum(
            1 for record in records if record["conversation_context_available"]
        ),
        "conversation_ir_available_count": sum(
            1 for record in records if record["conversation_ir_available"]
        ),
        "specialist_opportunity_counts": {
            "live_constraints_extraction": len(records),
            "stance_extraction": len(records),
            "dropped_threads_extraction": max(0, len(records) - 1),
        },
        "recommended_review_buckets": dict(bucket_counts),
    }


def test_findings_groups_good_warning_and_critical_records() -> None:
    records = [
        _record("case-c", "run-3", adequacy_status="critical", invalid_turn_ref_count=2),
        _record("case-a", "run-1"),
        _record("case-b", "run-2", adequacy_status="warn", quote_fabrication_count=3),
    ]

    findings = build_findings(records, _manifest(records))

    assert findings["schema_version"] == FINDINGS_SCHEMA_VERSION
    assert findings["corpus_summary"]["adequacy_status_counts"] == {
        "critical": 1,
        "good": 1,
        "warn": 1,
    }
    assert [record["id"] for record in findings["critical_records"]] == ["case-c/run-3"]
    assert [record["id"] for record in findings["warning_records"]] == ["case-b/run-2"]
    assert findings["warning_cause_counts"] == {"quote_validation": 1}
    assert findings["critical_cause_counts"] == {"turn_refs": 1}


def test_findings_counts_turn_refs_and_quote_fabrication() -> None:
    records = [
        _record("case-turn", "run-2", adequacy_status="critical", invalid_turn_ref_count=4),
        _record("case-quote", "run-1", adequacy_status="warn", quote_fabrication_count=2),
        _record("case-quote", "run-3", adequacy_status="warn", quote_fabrication_count=1),
    ]

    findings = build_findings(records, _manifest(records))

    assert findings["invalid_turn_ref_patterns"]["total"] == 4
    assert findings["invalid_turn_ref_patterns"]["record_count"] == 1
    assert findings["quote_fabrication_patterns"]["total"] == 3
    assert findings["quote_fabrication_patterns"]["record_count"] == 2
    assert findings["recommended_next_slice"]["slice"] == "quote_validation_repair"


def test_findings_output_order_is_deterministic() -> None:
    records = [
        _record("z-case", "run-2", adequacy_status="warn", quote_fabrication_count=1),
        _record("a-case", "run-1", adequacy_status="warn", quote_fabrication_count=1),
        _record("m-case", "run-3", adequacy_status="critical", invalid_turn_ref_count=1),
    ]

    first = build_findings(records, _manifest(records))
    second = build_findings(list(reversed(records)), _manifest(records))

    assert [record["id"] for record in first["warning_records"]] == [
        "a-case/run-1",
        "z-case/run-2",
    ]
    assert render_json(first) == render_json(second)
    assert render_markdown(first) == render_markdown(second)


def test_findings_do_not_leak_raw_or_unknown_corpus_fields() -> None:
    record = _record(
        "safe-case",
        "run-1",
        adequacy_status="warn",
        quote_fabrication_count=1,
        fields_only_turn_ref_grounded=["live_constraints", "SECRET FIELD"],
        fields_with_no_source_grounding=["synthesized_position", "SECRET OTHER FIELD"],
        record_errors=["SECRET exception message with raw user text"],
    )
    record.update(
        {
            "raw_transcript": "SECRET RAW TRANSCRIPT",
            "memo": "SECRET MEMO",
            "revised_answer": "SECRET REVISED",
            "raw_model_messages": [{"content": "SECRET MODEL MESSAGE"}],
            "fabricated_passages": ["SECRET FABRICATED PASSAGE"],
        }
    )

    findings = build_findings([record], _manifest([record]))
    rendered = render_markdown(findings) + render_json(findings)

    assert "SECRET" not in rendered
    assert findings["warning_records"][0]["fields_only_turn_ref_grounded"] == [
        "live_constraints"
    ]
    assert findings["warning_records"][0]["fields_with_no_source_grounding"] == [
        "synthesized_position"
    ]
    assert findings["warning_records"][0]["error_categories"] == ["record_error"]


def test_findings_do_not_copy_absolute_archive_paths() -> None:
    record = _record(
        "case",
        "run",
        adequacy_status="warn",
        quote_fabrication_count=1,
    )
    record["archive_path"] = "/Users/marcin/SECRET_HOME/.local/share/lolla/runs/case/run"
    record["archive_relpath"] = "case/run"

    findings = build_findings([record], _manifest([record]))
    rendered = render_markdown(findings) + render_json(findings)

    assert "SECRET_HOME" not in rendered
    assert "/Users/" not in rendered
    assert "case/run" in rendered
    assert findings["warning_records"][0]["archive_path_present"] is True
    assert "archive_path" not in findings["warning_records"][0]
    assert findings["source"]["absolute_archive_paths_included"] is False


def test_cli_handles_malformed_input_deterministically(
    tmp_path: Path,
    capsys,
) -> None:
    corpus_path = tmp_path / "bad.jsonl"
    manifest_path = tmp_path / "manifest.json"
    markdown_path = tmp_path / "findings.md"
    json_path = tmp_path / "findings.json"
    corpus_path.write_text("{not-json\n", encoding="utf-8")
    manifest_path.write_text("{}", encoding="utf-8")

    exit_code = main(
        [
            "--corpus",
            str(corpus_path),
            "--manifest",
            str(manifest_path),
            "--out",
            str(markdown_path),
            "--json-out",
            str(json_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err.strip() == "error: corpus line 1 is not valid JSON"
    assert not markdown_path.exists()
    assert not json_path.exists()


def test_cli_creates_markdown_and_json_outputs(tmp_path: Path) -> None:
    records = [
        _record("case-b", "run-2", adequacy_status="warn", quote_fabrication_count=2),
        _record("case-a", "run-1"),
    ]
    manifest = _manifest(records)
    corpus_path = tmp_path / "corpus.jsonl"
    manifest_path = tmp_path / "manifest.json"
    markdown_path = tmp_path / "findings.md"
    json_path = tmp_path / "findings.json"
    corpus_path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )
    manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")

    exit_code = main(
        [
            "--corpus",
            str(corpus_path),
            "--manifest",
            str(manifest_path),
            "--out",
            str(markdown_path),
            "--json-out",
            str(json_path),
        ]
    )

    assert exit_code == 0
    assert markdown_path.exists()
    assert json_path.exists()
    assert "# Extraction Adequacy Findings" in markdown_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["warning_records"][0]["id"] == "case-b/run-2"
    assert payload["recommended_next_slice"]["slice"] == "quote_validation_repair"
