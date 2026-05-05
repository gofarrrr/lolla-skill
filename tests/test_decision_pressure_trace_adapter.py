from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.decision_pressure_trace_adapter import (  # noqa: E402
    build_decision_pressure_trace_review_report,
)
from system_b.decision_pressure_trace_validation import (  # noqa: E402
    DecisionPressureTraceValidationError,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "decision_pressure_trace"
    / "gate4_3case_pr18_valid.json"
)
AFFORDANCES_V4_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v4.json"
)
SCRIPT_PATH = REPO_ROOT / "scripts" / "smoke_decision_pressure_trace_adapter.py"


def test_valid_pr19_fixture_produces_passed_review_report() -> None:
    report = build_decision_pressure_trace_review_report(
        fixture_path=FIXTURE_PATH,
        compiled_affordances_path=AFFORDANCES_V4_PATH,
    )

    assert report["validation_status"] == "passed"
    assert report["adapter_policy"] == "fixture_only_review_report"
    assert report["schema_version"] == "decision_pressure_trace.v1"
    assert report["trace_id"] == "gate4-3case-pr18-observatory-prototype-2026-05-05"
    assert report["status"] == "draft_review_only"
    assert report["runtime_policy"] == "runtime_dormant"
    assert report["selected_pressure_count"] == 3
    assert report["coverage_transparency_panel_count"] == 1
    assert report["suppressed_candidate_count"] == 6
    assert report["selected_pressure_ids"] == [
        "equity-governance-deadlock-before-vesting",
        "mother-safety-plan-gameable-signal",
        "phd-shaping-phase-without-stop-condition",
    ]
    assert report["source_affordance_count"] == 13
    assert len(report["unique_source_affordance_ids"]) == 13
    assert "live-observatory-rendering" in report["blocked_surfaces"]


def test_adapter_rejects_non_dormant_trace(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["runtime_policy"] = "observatory_live"
    broken_fixture = tmp_path / "non_dormant_trace.json"
    broken_fixture.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="runtime_policy must be runtime_dormant",
    ):
        build_decision_pressure_trace_review_report(
            fixture_path=broken_fixture,
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_adapter_rejects_unknown_source_affordance_id(tmp_path: Path) -> None:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    payload["selected_pressures"][0]["source_affordances"].append(
        "imaginary-model.imaginary-affordance"
    )
    broken_fixture = tmp_path / "unknown_affordance_trace.json"
    broken_fixture.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="unknown source_affordance",
    ):
        build_decision_pressure_trace_review_report(
            fixture_path=broken_fixture,
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_cli_prints_summary_without_writing_report(tmp_path: Path) -> None:
    report_out = tmp_path / "should_not_exist.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--fixture",
            str(FIXTURE_PATH),
            "--affordances",
            str(AFFORDANCES_V4_PATH),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "decision_pressure_trace adapter smoke: passed" in result.stdout
    assert "selected_pressures: 3" in result.stdout
    assert not report_out.exists()


def test_cli_writes_report_only_when_report_out_is_provided(tmp_path: Path) -> None:
    report_out = tmp_path / "adapter_report.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--fixture",
            str(FIXTURE_PATH),
            "--affordances",
            str(AFFORDANCES_V4_PATH),
            "--report-out",
            str(report_out),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    report = json.loads(report_out.read_text(encoding="utf-8"))
    assert report["adapter_policy"] == "fixture_only_review_report"
    assert report["validation_status"] == "passed"


def test_cli_refuses_html_or_observatory_report_path(tmp_path: Path) -> None:
    report_out = tmp_path / "observatory_trace.html"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--fixture",
            str(FIXTURE_PATH),
            "--affordances",
            str(AFFORDANCES_V4_PATH),
            "--report-out",
            str(report_out),
        ],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "review-only JSON report" in result.stderr
    assert not report_out.exists()


def test_adapter_report_excludes_generated_or_user_facing_output_fields() -> None:
    report = build_decision_pressure_trace_review_report(
        fixture_path=FIXTURE_PATH,
        compiled_affordances_path=AFFORDANCES_V4_PATH,
    )

    forbidden_fields = {
        "pressure",
        "what_to_verify",
        "why_it_matters",
        "dismiss_if",
        "tripwire_or_next_action",
        "operator_note",
        "user_facing_copy",
        "rendered_html",
        "observatory_html",
    }

    assert forbidden_fields.isdisjoint(report)
    assert "<html" not in json.dumps(report).lower()


def test_adapter_report_preserves_competitive_dynamics_coverage_blank_id() -> None:
    report = build_decision_pressure_trace_review_report(
        fixture_path=FIXTURE_PATH,
        compiled_affordances_path=AFFORDANCES_V4_PATH,
    )

    assert report["coverage_panel_ids"] == [
        "phd-competitive-dynamics-coverage-gap"
    ]
