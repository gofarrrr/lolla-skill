from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from engine.system_b.decision_work_receipt_debug_summary import (
    DecisionWorkReceiptDebugSummaryInputError,
    render_decision_work_receipt_debug_summary,
)
from engine.system_b.decision_work_receipt import (
    build_decision_work_receipt,
    render_decision_work_receipt_json,
)
from engine.system_b.decision_trail_report import (
    build_decision_trail_report,
    render_decision_trail_report_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: str) -> None:
    path.write_text(payload, encoding="utf-8")


def _minimal_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "runs" / "launch-public-enterprise-beta" / "20260630T000000Z_demo"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "agent_result.json",
        """{
          "schema_version": "lolla_agent_result.v1",
          "case_id": "launch-public-enterprise-beta",
          "run_id": "20260630T000000Z_demo"
        }""",
    )
    _write_json(run_dir / "evaluation.json", """{"schema_version":"lolla.evaluation.v0"}""")
    _write_json(
        run_dir / "reasoning_trace.json",
        """{
          "schema_version": "lolla.reasoning_trace.v0.2",
          "case": {
            "case_id": "launch-public-enterprise-beta",
            "run_id": "20260630T000000Z_demo"
          }
        }""",
    )
    _write_json(run_dir / "extraction_adequacy_report.json", """{"status":"good"}""")
    _write_json(
        run_dir / "extraction.json",
        """{
          "schema_version": "lolla.extraction.v0",
          "capture_manifest": {
            "actual_user_turns": 3,
            "actual_assistant_turns": 3,
            "declared_turns": 6,
            "last_turn_role": "ASSISTANT"
          },
          "capture_adequacy": {
            "status": "good",
            "capture_strategy": "full",
            "omitted_turn_count": 0,
            "risk_flags": []
          },
          "capture_health": "good",
          "extraction": {
            "decision_situation": "Whether to launch the enterprise beta.",
            "live_constraints": ["No raw constraint text should be copied."],
            "synthesized_position": "Structured summary only.",
            "dropped_threads": []
          }
        }""",
    )
    _write_json(
        run_dir / "result.json",
        """{
          "schema_version": "lolla.pipeline_result.v0",
          "delta_card": {"findings": [{"name": "do not copy finding prose"}]},
          "companion_cheat_sheet": {"anchors": [{"name": "inversion"}]},
          "frame_pressure_card": {"reframings": [{"name": "counterframe"}]},
          "structural_coverage_card": {"gap_questions": [{"id": "gate"}]},
          "bullshit_profile": {"summary": {"total_passages": 1}},
          "audit_summary": {"triggered_tendencies": ["overoptimism"]},
          "v60_enrichment": {"status": "active"},
          "run_health": {"overall": "healthy", "capture": "good"}
        }""",
    )
    _write_json(run_dir / "memo_note.json", """{"schema_version":"lolla.memo_note.v0"}""")
    _write_json(run_dir / "gapcheck_lanes.json", """{"lanes": [{"lane_name": "DeltaCard"}]}""")
    _write_json(run_dir / "run_events.json", """{"schema_version":"lolla.run_events.v0"}""")
    _write_json(
        run_dir / "graph_survival_report.json",
        """{"schema_version":"lolla.graph_survival_report.v0"}""",
    )
    for raw_name in ("conversation.txt", "memo.md", "revised.txt", "live_transcript.txt"):
        (run_dir / raw_name).write_text("RAW_PRIVATE_MARKER_DO_NOT_COPY", encoding="utf-8")
    return run_dir


def _receipt_and_report(tmp_path: Path) -> tuple[dict, dict]:
    run_dir = _minimal_run_dir(tmp_path)
    report = build_decision_trail_report(run_dir=run_dir)
    report_path = tmp_path / "decision_trail_report.json"
    report_path.write_text(render_decision_trail_report_json(report, pretty=True), encoding="utf-8")
    receipt = build_decision_work_receipt(
        run_dir=run_dir,
        decision_trail_report_paths=[report_path],
    )
    return receipt, report


def test_renders_internal_debug_summary_without_raw_or_arbitrary_report_content(
    tmp_path: Path,
) -> None:
    receipt, report = _receipt_and_report(tmp_path)
    report["private_marker"] = "REPORT_MARKER_DO_NOT_COPY"

    markdown = render_decision_work_receipt_debug_summary(
        receipt=receipt,
        decision_trail_report=report,
    )

    assert markdown.startswith("# Decision Work Receipt Debug Summary")
    assert "internal diagnostic packet" in markdown
    assert "not the customer-facing decision story" in markdown
    assert "Case: `launch-public-enterprise-beta`" in markdown
    assert "Receipt readiness: `decision_trail_review_ready`" in markdown
    assert "Process shape: `multi_turn_evidence`" in markdown
    assert "structural pressure" in markdown
    assert "model companion" in markdown
    assert "Decision Trail report: `available_from_structured_artifact`" in markdown
    assert "Product Delta report: `not_supplied`" in markdown
    assert "conversation understanding summary" in markdown
    assert "vanilla likely next action" in markdown
    assert "not correctness proof" in markdown
    assert "not product proof" in markdown
    assert "not agent action authorization" in markdown
    assert "What this helps maintainers inspect" in markdown
    assert "What this does not give users" in markdown
    assert "what action changed" in markdown
    assert "customer can learn" not in markdown
    assert "RAW_PRIVATE_MARKER_DO_NOT_COPY" not in markdown
    assert "REPORT_MARKER_DO_NOT_COPY" not in markdown
    assert str(tmp_path) not in markdown


def test_renders_receipt_only_summary_when_decision_trail_is_absent(tmp_path: Path) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))

    markdown = render_decision_work_receipt_debug_summary(receipt=receipt)

    assert "No Decision Trail JSON was provided" in markdown
    assert "challenged_and_revised_process" in markdown
    assert "not answer-quality scoring" in markdown


def test_renderer_exposes_inconsistent_turn_count_metadata(tmp_path: Path) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))
    receipt["conversation_process_map"]["turn_count"] = 3
    receipt["conversation_process_map"]["user_turn_count"] = 3
    receipt["conversation_process_map"]["assistant_turn_count"] = 3

    markdown = render_decision_work_receipt_debug_summary(receipt=receipt)

    assert "role counts sum to `6`" in markdown
    assert "metadata inconsistency" in markdown
    assert "not a semantic finding" in markdown


def test_rejects_unsupported_receipt_schema() -> None:
    with pytest.raises(DecisionWorkReceiptDebugSummaryInputError, match="receipt schema"):
        render_decision_work_receipt_debug_summary(receipt={"schema_version": "wrong"})


def test_rejects_unsupported_decision_trail_schema(tmp_path: Path) -> None:
    receipt = build_decision_work_receipt(run_dir=_minimal_run_dir(tmp_path))

    with pytest.raises(DecisionWorkReceiptDebugSummaryInputError, match="Decision Trail schema"):
        render_decision_work_receipt_debug_summary(
            receipt=receipt,
            decision_trail_report={"schema_version": "wrong"},
        )


def test_cli_writes_markdown_summary(tmp_path: Path) -> None:
    receipt, report = _receipt_and_report(tmp_path)
    receipt_path = tmp_path / "receipt.json"
    report_path = tmp_path / "report.json"
    output_path = tmp_path / "summary.md"
    receipt_path.write_text(render_decision_work_receipt_json(receipt, pretty=True), encoding="utf-8")
    report_path.write_text(render_decision_trail_report_json(report, pretty=True), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/evals/render_decision_work_receipt_debug_summary.py",
            "--receipt",
            str(receipt_path),
            "--decision-trail-report",
            str(report_path),
            "--out",
            str(output_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    markdown = output_path.read_text(encoding="utf-8")
    assert "# Decision Work Receipt Debug Summary" in markdown
    assert "Receipt readiness: `decision_trail_review_ready`" in markdown
