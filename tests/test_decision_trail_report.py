from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from engine.system_b.decision_trail_report import (
    DECISION_TRAIL_REPORT_SCHEMA_VERSION,
    DecisionTrailReportInputError,
    build_decision_trail_report,
    render_decision_trail_report_json,
    validate_output_path,
)
from engine.system_b.product_delta_boundary_lint import lint_product_delta_paths


REPO_ROOT = Path(__file__).resolve().parents[1]
SEMANTIC_SECTIONS = {
    "conversation_understanding_summary",
    "decision_question",
    "vanilla_likely_next_action",
    "revised_likely_next_action",
    "option_map",
    "constraints",
    "stakeholders",
    "values_or_priorities",
    "assistant_influence",
    "audit_pressure_summary",
    "structural_delta",
    "useful_noisy_friction",
    "lost_value",
    "unresolved_questions",
}


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _minimal_run_dir(tmp_path: Path) -> Path:
    run_dir = tmp_path / "runs" / "sample-case" / "20260629T000000Z_test"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "agent_result.json",
        {
            "schema_version": "lolla_agent_result.v1",
            "case_id": "sample-case",
            "run_id": "20260629T000000Z_test",
            "status": "ok",
            "caller_action": "use_revised_answer",
            "main_counter_pressure": "The answer needed a narrower evidence gate before action.",
            "changed_advice_summary": [
                "Use a smaller pilot before treating the recommendation as ready."
            ],
            "take_backs": [
                "Do not treat artifact cleanliness as a reliance decision."
            ],
            "human_questions": [
                "Which reviewer owns the final reliance decision?"
            ],
        },
    )
    _write_json(
        run_dir / "evaluation.json",
        {
            "schema_version": "lolla.evaluation.v0",
            "case_id": "sample-case",
            "run_id": "20260629T000000Z_test",
            "overall": "pass",
            "scope": {
                "artifact": "run_readiness",
                "advice_quality_scored": False,
                "model_calls": 0,
                "llm_judge_used": False,
            },
        },
    )
    _write_json(
        run_dir / "reasoning_trace.json",
        {
            "schema_version": "lolla.reasoning_trace.v0.2",
            "trace_id": "trace_20260629T000000Z_test",
            "case": {
                "case_id": "sample-case",
                "run_id": "20260629T000000Z_test",
                "decision_situation": "Whether to rely on the revised recommendation after review.",
            },
        },
    )
    _write_json(
        run_dir / "extraction_adequacy_report.json",
        {
            "schema_version": "lolla.extraction_adequacy_report.v0",
            "status": "good",
        },
    )
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "schema_version": "lolla.extraction.v0",
            "extraction": {
                "decision_situation": "Whether to rely on the revised recommendation after review.",
                "live_constraints": [
                    {
                        "constraint": "The recommendation needs a narrower evidence gate.",
                        "introduced_turn": 4,
                        "status": "active",
                        "weight": "high",
                    }
                ],
                "synthesized_position": "Do the smaller pilot first.",
                "reasoning_passages": ["Short structured passage"],
                "original_framing": "Whether the advice is ready.",
                "dropped_threads": [],
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
    return run_dir


def test_builds_sparse_valid_report_from_structured_artifacts(tmp_path: Path) -> None:
    report = build_decision_trail_report(run_dir=_minimal_run_dir(tmp_path))

    assert report["schema_version"] == DECISION_TRAIL_REPORT_SCHEMA_VERSION
    assert report["report_mode"] == "checked_in_safe_mode"
    assert report["report_metadata"]["case_id"] == "sample-case"
    assert report["report_metadata"]["run_id"] == "20260629T000000Z_test"
    assert report["report_metadata"]["generated_by"] == "decision_trail_exporter"
    assert report["report_metadata"]["archive_relpath"] == (
        "sample-case/20260629T000000Z_test"
    )
    assert report["decision_question"]["status"] == "available_from_structured_artifact"
    assert report["decision_question"]["source_refs"][0]["artifact"] == "extraction.json"
    assert report["decision_question"]["exporter_inferred_from_prose"] is False
    assert report["constraints"]["items"][0]["summary"] == (
        "The recommendation needs a narrower evidence gate."
    )
    assert report["audit_pressure_summary"]["status"] == "available_from_structured_artifact"
    assert report["structural_delta"]["items"]
    assert report["unresolved_questions"]["items"][0]["owner"] == "future_human_review"


def test_every_semantic_section_has_empty_meaning_and_population_flags(tmp_path: Path) -> None:
    report = build_decision_trail_report(run_dir=_minimal_run_dir(tmp_path))

    for section_name in SEMANTIC_SECTIONS:
        section = report[section_name]
        assert section["empty_meaning"]
        assert "source_status" in section
        assert "source_refs" in section
        assert "owner" in section
        assert "requires_llm_interpretation" in section
        assert section["exporter_inferred_from_prose"] is False
        assert "value" in section or "items" in section


def test_messy_fields_remain_llm_required_not_inferred(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    _write_json(
        run_dir / "result.json",
        {
            "schema_version": "lolla.pipeline_result.v0",
            "lost_value": "DO NOT COPY LOST VALUE FROM GENERIC PROSE FIELD",
            "useful_noisy_friction": "DO NOT COPY FRICTION FIELD",
            "stakeholders": "DO NOT COPY STAKEHOLDER FIELD",
        },
    )

    report = build_decision_trail_report(run_dir=run_dir)
    rendered = render_decision_trail_report_json(report, pretty=True)

    for section_name in (
        "option_map",
        "stakeholders",
        "values_or_priorities",
        "assistant_influence",
        "useful_noisy_friction",
        "lost_value",
        "revised_likely_next_action",
    ):
        section = report[section_name]
        assert section["status"] == "requires_llm_interpretation"
        assert section["requires_llm_interpretation"] is True
        assert section["items"] == []
    assert "DO NOT COPY" not in rendered


def test_custody_flags_remain_false_or_zero(tmp_path: Path) -> None:
    report = build_decision_trail_report(run_dir=_minimal_run_dir(tmp_path))
    custody = report["custody_flags"]

    assert custody["model_calls"] == 0
    assert all(value is False for key, value in custody.items() if key != "model_calls")
    assert report["non_claims"]["human_validated"] is False
    assert report["non_claims"]["product_proof"] is False
    assert report["non_claims"]["answer_quality_scored"] is False
    assert report["non_claims"]["automatic_labels_created"] is False
    assert report["non_claims"]["agent_action_authorized"] is False


def test_raw_artifacts_are_not_read_in_checked_in_safe_mode(tmp_path: Path) -> None:
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
        report = build_decision_trail_report(run_dir=run_dir)

    rendered = render_decision_trail_report_json(report, pretty=True)
    for marker in raw_markers.values():
        assert marker not in rendered
    artifact_status = {
        item["artifact"]: item["status"]
        for item in report["source_artifacts"]
    }
    assert artifact_status["conversation.txt"] == "available_but_redacted_in_safe_mode"
    assert artifact_status["revised.txt"] == "available_but_redacted_in_safe_mode"
    assert artifact_status["operator.log"] == "available_in_private_artifact_not_exported"
    assert artifact_status["v60_ledger.json"] == "available_in_private_artifact_not_exported"
    assert all(item["raw_content_read"] is False for item in report["source_artifacts"])


def test_output_path_inside_run_dir_is_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(DecisionTrailReportInputError, match="outside run directory"):
        validate_output_path(output_path=run_dir / "decision_trail.json", run_dir=run_dir)


def test_output_path_equal_to_run_dir_is_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(DecisionTrailReportInputError, match="outside run directory"):
        validate_output_path(output_path=run_dir, run_dir=run_dir)


def test_missing_structured_artifacts_become_status_not_crash(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "case" / "run"
    run_dir.mkdir(parents=True)

    report = build_decision_trail_report(run_dir=run_dir)

    statuses = {item["artifact"]: item["status"] for item in report["source_artifacts"]}
    assert statuses["evaluation.json"] == "unavailable_missing_artifact"
    assert statuses["agent_result.json"] == "unavailable_missing_artifact"
    assert statuses["extraction.json"] == "unavailable_missing_artifact"
    assert report["decision_question"]["status"] == "unavailable_missing_artifact"
    assert report["artifact_health"]["items"]
    assert "Missing artifacts were recorded as missing rather than guessed." in report["limitations"]["items"]


def test_malformed_structured_artifact_becomes_status_not_crash(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    (run_dir / "extraction.json").write_text("{not-json", encoding="utf-8")
    (run_dir / "reasoning_trace.json").unlink()

    report = build_decision_trail_report(run_dir=run_dir)

    statuses = {item["artifact"]: item["status"] for item in report["source_artifacts"]}
    assert statuses["extraction.json"] == "unavailable_malformed_artifact"
    assert report["decision_question"]["status"] == "unavailable_malformed_artifact"
    assert "Malformed structured artifacts were recorded as malformed rather than guessed." in report["limitations"]["items"]


def test_trace_context_has_no_external_dependency(tmp_path: Path) -> None:
    report = build_decision_trail_report(run_dir=_minimal_run_dir(tmp_path))
    trace = report["trace_context"]

    assert trace["status"] == "future_compatible"
    assert trace["otel_genai_semconv_status"] == "not_used"
    assert trace["external_trace_dependency_added"] is False
    assert trace["external_trace_id"] is None


def test_local_private_mode_is_deferred(tmp_path: Path) -> None:
    with pytest.raises(DecisionTrailReportInputError, match="checked_in_safe_mode"):
        build_decision_trail_report(
            run_dir=_minimal_run_dir(tmp_path),
            report_mode="local_private_mode",
        )


def test_cli_writes_pretty_json_outside_run_dir(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    output_path = tmp_path / "decision_trail_report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "evals" / "build_decision_trail_report.py"),
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

    assert result.returncode == 0, result.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == DECISION_TRAIL_REPORT_SCHEMA_VERSION
    assert payload["custody_flags"]["archive_mutated"] is False


def test_cli_rejects_output_inside_run_dir(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "evals" / "build_decision_trail_report.py"),
            "--run-dir",
            str(run_dir),
            "--out",
            str(run_dir / "decision_trail_report.json"),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "outside run directory" in result.stderr


def test_generated_report_passes_product_delta_boundary_lint(tmp_path: Path) -> None:
    report = build_decision_trail_report(run_dir=_minimal_run_dir(tmp_path))
    output_path = tmp_path / "decision_trail_report.json"
    output_path.write_text(render_decision_trail_report_json(report, pretty=True), encoding="utf-8")

    lint = lint_product_delta_paths([output_path])

    assert lint["summary"]["blocking_error_count"] == 0
