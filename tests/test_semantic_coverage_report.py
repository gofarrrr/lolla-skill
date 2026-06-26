from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.semantic_coverage_report import (
    SEMANTIC_COVERAGE_REPORT_SCHEMA_VERSION,
    build_semantic_coverage_report,
    render_semantic_coverage_report_json,
)
from scripts.build_semantic_coverage_report import main as cli_main


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_archive(
    tmp_path: Path,
    *,
    include_optional: bool = True,
    include_agent_boundaries: bool = True,
    live_constraints: list[dict] | None = None,
    dropped_threads: list[dict] | None = None,
) -> Path:
    run_dir = (
        tmp_path
        / "Users"
        / "marcin"
        / "SECRET_HOME"
        / ".local"
        / "share"
        / "lolla"
        / "runs"
        / "case-a"
        / "run-a"
    )
    run_dir.mkdir(parents=True)
    (run_dir / "conversation.txt").write_text(
        "CONVERSATION: 4 turns, 2 user messages, 2 assistant responses\n\n"
        "[Turn 1] USER:\n"
        "SECRET TRANSCRIPT TEXT. Should we launch the beta with six users?\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Wait for a customer-success gate before launching.\n\n"
        "[Turn 2] USER:\n"
        "SECRET LATER PUSHBACK. The sales team needs a proof point this week.\n\n"
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
    threads = dropped_threads
    if threads is None:
        threads = [
            {
                "thread": "customer-success launch gate",
                "raised_by": "assistant",
                "raised_turn": 1,
                "status": "acknowledged_then_dropped",
            }
        ]
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "capture_health": "good",
            "capture_manifest": {"truncation_applied": False},
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
                "reasoning_passages": ["Wait for a customer-success gate before launching."],
                "original_framing": "Launch the beta now?",
                "dropped_threads": threads,
                "_quote_validation": {
                    "total": 2,
                    "verified": 2,
                    "fabricated": 0,
                    "fabricated_passages": ["SECRET FABRICATED PASSAGE 123"],
                    "retry_attempted": False,
                    "retry_succeeded": False,
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
                "synthesized_position_present": True,
                "original_framing_present": True,
                "live_constraints_count": len(constraints),
                "dropped_threads_count": len(threads),
                "reasoning_passages_count": 1,
                "quote_validation": {
                    "present": True,
                    "total": 2,
                    "verified": 2,
                    "fabricated": 0,
                },
            },
            "provenance_gap_findings": {
                "fields_present_but_not_span_grounded": [
                    "decision_situation",
                    "live_constraints",
                    "dropped_threads",
                ],
                "fields_only_turn_ref_grounded": [
                    "live_constraints",
                    "dropped_threads",
                ],
                "fields_derivation_grounded": ["decision_situation"],
                "fields_with_no_source_grounding": ["synthesized_position"],
                "missing_turn_ref_count": 0,
                "invalid_turn_ref_count": 0,
                "speaker_mismatch_count": 0,
                "quote_fabrication_count": 0,
            },
        },
    )
    if include_optional:
        _write_json(
            run_dir / "result.json",
            {
                "audit_summary": "SECRET PROVIDER SUMMARY TEXT",
                "delta_card": {"present": True},
                "frame_pressure_card": {"present": True},
                "structural_coverage_card": {"present": True},
                "has_gap_check": True,
                "gap_check_summary": "SECRET GAP SUMMARY",
                "revised_answer_present": True,
                "revised_answer": "SECRET REVISED IN RESULT",
                "memo_substantive_title": "SECRET MEMO TITLE",
                "memo_what_changed": "SECRET CHANGE REASON",
                "memo_take_back_or_set_aside": "SECRET TAKEBACK",
                "memo_note_written_at": "2026-06-26T12:00:00Z",
            },
        )
        (run_dir / "revised.txt").write_text(
            "SECRET REVISED ANSWER TEXT",
            encoding="utf-8",
        )
        (run_dir / "memo.md").write_text("SECRET MEMO TEXT", encoding="utf-8")
        _write_json(
            run_dir / "reasoning_trace.json",
            {"artifacts": [{"path": "extraction.json"}, {"path": "result.json"}]},
        )
        _write_json(
            run_dir / "evaluation.json",
            {
                "schema_version": "lolla.evaluation.v0",
                "case_id": "case-a",
                "run_id": "run-a",
                "created_at": "2026-06-26T12:00:01Z",
                "overall": "partial",
                "caller_readiness": "do_not_use_run_degraded",
                "checks": [{"id": "extraction_adequacy"}],
            },
        )
        agent_payload = {
            "schema_version": "lolla.agent_result.v0",
            "case_id": "case-a",
            "run_id": "run-a",
            "created_at": "2026-06-26T12:00:02Z",
            "status": "partial",
            "caller_action": "do_not_use_run_degraded",
            "changed_advice_summary": "SECRET CHANGED ADVICE",
            "main_counter_pressure": "SECRET COUNTER PRESSURE",
            "do_not_act_before": [],
            "human_questions": [],
        }
        if include_agent_boundaries:
            agent_payload["do_not_act_before"] = ["SECRET DO NOT ACT"]
            agent_payload["human_questions"] = ["SECRET QUESTION"]
        _write_json(run_dir / "agent_result.json", agent_payload)
    return run_dir


def test_clean_modern_fixture_produces_schema(tmp_path: Path) -> None:
    run_dir = _seed_archive(tmp_path)

    report = build_semantic_coverage_report(run_dir)

    assert report["schema_version"] == SEMANTIC_COVERAGE_REPORT_SCHEMA_VERSION
    assert report["case_id"] == "case-a"
    assert report["run_id"] == "run-a"
    assert report["source"]["local_only"] is True
    assert report["source"]["model_calls"] == 0
    assert report["overall_coverage_summary"]["semantic_element_count"] == 10
    assert report["source_artifacts"]["conversation.txt"]["present"] is True
    assert report["source_artifacts"]["conversation.txt"]["sha256"].startswith("sha256:")


def test_missing_optional_artifacts_degrade_without_crashing(tmp_path: Path) -> None:
    run_dir = _seed_archive(tmp_path, include_optional=False)

    report = build_semantic_coverage_report(run_dir)

    assert report["source_artifacts"]["result.json"]["present"] is False
    assert report["semantic_elements"]["counter_pressure"]["status"] == "missing"
    assert report["semantic_elements"]["revised_answer_change_reason"]["status"] == "missing"
    assert report["semantic_elements"]["actionability_boundaries"]["status"] == "missing"


def test_raw_text_and_absolute_paths_do_not_appear(tmp_path: Path) -> None:
    run_dir = _seed_archive(tmp_path)

    rendered = render_semantic_coverage_report_json(
        build_semantic_coverage_report(run_dir)
    )

    assert "SECRET" not in rendered
    assert "SECRET_HOME" not in rendered
    assert "/Users/" not in rendered
    assert "SECRET FABRICATED PASSAGE 123" not in rendered
    assert "case-a/run-a" in rendered


def test_live_constraints_turn_ref_grounding_is_not_reported_as_span(
    tmp_path: Path,
) -> None:
    run_dir = _seed_archive(tmp_path)

    report = build_semantic_coverage_report(run_dir)
    live_constraints = report["semantic_elements"]["live_constraints"]

    assert live_constraints["status"] == "partial"
    assert live_constraints["grounding"] == "turn_ref"
    assert live_constraints["grounding"] != "span"


def test_user_values_are_not_falsely_marked_present(tmp_path: Path) -> None:
    run_dir = _seed_archive(tmp_path)

    report = build_semantic_coverage_report(run_dir)
    values = report["semantic_elements"]["user_values_or_priorities_signal"]

    assert values["status"] in {"not_measured", "partial"}
    assert values["status"] != "present"
    assert values["evidence_counts"]["first_class_user_values_field_count"] == 0


def test_actionability_boundaries_use_agent_result_fields(tmp_path: Path) -> None:
    run_dir = _seed_archive(tmp_path, include_agent_boundaries=True)

    report = build_semantic_coverage_report(run_dir)
    boundaries = report["semantic_elements"]["actionability_boundaries"]

    assert boundaries["status"] == "present"
    assert boundaries["artifact_owners"] == [
        "agent_result.json",
        "revised.txt",
        "memo.md",
    ]
    assert boundaries["evidence_counts"]["do_not_act_before_count"] == 1
    assert boundaries["evidence_counts"]["human_questions_count"] == 1


def test_output_is_deterministic_across_repeated_builds(tmp_path: Path) -> None:
    run_dir = _seed_archive(tmp_path)

    first = render_semantic_coverage_report_json(build_semantic_coverage_report(run_dir))
    second = render_semantic_coverage_report_json(build_semantic_coverage_report(run_dir))

    assert first == second


def test_cli_creates_json_report(tmp_path: Path) -> None:
    run_dir = _seed_archive(tmp_path)
    out = tmp_path / "semantic_coverage_report.json"

    exit_code = cli_main([str(run_dir), "--out", str(out)])
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert out.exists()
    assert payload["schema_version"] == SEMANTIC_COVERAGE_REPORT_SCHEMA_VERSION


def test_malformed_archive_is_reported_without_crashing(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "case-b" / "run-b"
    run_dir.mkdir(parents=True)
    (run_dir / "conversation.txt").write_text(
        "CONVERSATION: 1 turn\n\n[Turn 1] USER:\nSECRET RAW TEXT\n",
        encoding="utf-8",
    )
    (run_dir / "extraction.json").write_text("{not-json", encoding="utf-8")

    report = build_semantic_coverage_report(run_dir)
    rendered = render_semantic_coverage_report_json(report)

    assert report["source_artifacts"]["extraction.json"]["json_valid"] is False
    assert report["overall_coverage_summary"]["build_error_categories"]
    assert "SECRET RAW TEXT" not in rendered
