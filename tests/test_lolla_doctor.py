from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from engine.system_b.lolla_doctor import (
    DOCTOR_REPORT_SCHEMA_VERSION,
    build_doctor_report,
    render_doctor_report_json,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _runtime_root(tmp_path: Path, *, include_required_helpers: bool = True) -> Path:
    root = tmp_path / "runtime"
    (root / "engine/system_b").mkdir(parents=True)
    (root / "scripts/skill").mkdir(parents=True)
    (root / "scripts").mkdir(exist_ok=True)
    (root / "SKILL.md").write_text("name: lolla\n", encoding="utf-8")
    if include_required_helpers:
        for rel in (
            "scripts/skill/setup.sh",
            "scripts/skill/run_extract_step.sh",
            "scripts/skill/run_pipeline_step.sh",
        ):
            (root / rel).write_text("#!/usr/bin/env bash\n", encoding="utf-8")
    for rel in (
        "scripts/export_review_corpus.py",
        "scripts/analyze_review_corpus_evidence_readiness.py",
    ):
        (root / rel).write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    return root


def _manifest(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "lolla.review_corpus_manifest.v0",
        "record_schema_version": "lolla.review_corpus_record.v0",
        "record_count": 80,
        "risk_mode_counts": {"standard": 80},
        "risk_mode_reliance_present_counts": {"false": 80, "true": 0},
        "risk_mode_reliance_by_risk_mode_counts": {"standard|false": 80},
        "risk_mode_reliance_check_status_counts": {"unavailable": 80},
    }
    payload.update(overrides)
    return payload


def _write_manifest(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _check(report: dict[str, object], check_id: str) -> dict[str, object]:
    checks = report["checks"]
    assert isinstance(checks, list)
    for item in checks:
        assert isinstance(item, dict)
        if item.get("check_id") == check_id:
            return item
    raise AssertionError(f"missing check {check_id}")


def test_json_report_schema_is_stable(tmp_path: Path) -> None:
    runtime = _runtime_root(tmp_path)
    archive = tmp_path / "runs"
    archive.mkdir()
    manifest = _write_manifest(tmp_path, _manifest())

    report = build_doctor_report(
        runtime_root=runtime,
        archive_root=archive,
        manifest_path=manifest,
        env={},
        cwd=tmp_path,
    )

    assert report["schema_version"] == DOCTOR_REPORT_SCHEMA_VERSION
    assert set(report) == {
        "schema_version",
        "status",
        "checks",
        "summary",
        "custody_flags",
    }
    assert report["status"] == "warn"
    assert report["summary"]["model_calls"] == 0
    assert report["summary"]["archives_mutated"] is False
    assert report["custody_flags"]["reads_archives"] is False
    assert report["custody_flags"]["writes_archives"] is False
    assert report["custody_flags"]["model_calls"] == 0
    assert all(check["safe_to_print"] is True for check in report["checks"])


def test_missing_explicit_archive_root_is_deterministic(tmp_path: Path) -> None:
    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=tmp_path / "missing-runs",
        env={},
        cwd=tmp_path,
    )

    check = _check(report, "archive_root.discovery")
    assert report["status"] == "fail"
    assert check["status"] == "fail"
    assert check["details"]["path_state"] == "missing"


def test_file_as_archive_root_fails(tmp_path: Path) -> None:
    archive_file = tmp_path / "runs-file"
    archive_file.write_text("not a directory", encoding="utf-8")

    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=archive_file,
        env={},
        cwd=tmp_path,
    )

    check = _check(report, "archive_root.discovery")
    assert report["status"] == "fail"
    assert check["status"] == "fail"
    assert check["details"]["path_state"] == "file"


def test_output_inside_archive_root_is_rejected(tmp_path: Path) -> None:
    archive = tmp_path / "runs"
    archive.mkdir()

    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=archive,
        output_path=archive / "doctor.json",
        env={},
        cwd=tmp_path,
    )

    check = _check(report, "output.path_safety")
    assert report["status"] == "fail"
    assert check["status"] == "fail"
    assert check["details"]["inside_archive_root"] is True


def test_manifest_with_pr44_fields_reports_reliance_counts(tmp_path: Path) -> None:
    manifest = _write_manifest(
        tmp_path,
        _manifest(
            record_count=2,
            risk_mode_counts={"standard": 1, "high_stakes": 1},
            risk_mode_reliance_present_counts={"false": 1, "true": 1},
            risk_mode_reliance_by_risk_mode_counts={
                "standard|false": 1,
                "high_stakes|true": 1,
            },
            risk_mode_reliance_check_status_counts={
                "unavailable": 1,
                "pass": 1,
            },
        ),
    )
    archive = tmp_path / "runs"
    archive.mkdir()

    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=archive,
        manifest_path=manifest,
        env={"LOLLA_OPENROUTER_API_KEY": "dont-print-this-token"},
        cwd=tmp_path,
    )

    counts = _check(report, "risk_mode.reliance_counts")
    high_stakes = _check(report, "high_stakes.evidence_visibility")
    assert counts["status"] == "pass"
    assert counts["details"]["risk_mode_counts"] == {
        "standard": 1,
        "high_stakes": 1,
    }
    assert counts["details"]["risk_mode_reliance_present_counts"] == {
        "false": 1,
        "true": 1,
    }
    assert high_stakes["status"] == "pass"
    assert high_stakes["details"]["high_stakes_reliance_present_count"] == 1


def test_manifest_missing_reliance_fields_warns(tmp_path: Path) -> None:
    manifest_payload = _manifest()
    for field in (
        "risk_mode_reliance_present_counts",
        "risk_mode_reliance_by_risk_mode_counts",
        "risk_mode_reliance_check_status_counts",
    ):
        manifest_payload.pop(field)
    manifest = _write_manifest(tmp_path, manifest_payload)

    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=tmp_path / "missing-default",
        manifest_path=manifest,
        env={},
        cwd=tmp_path,
    )

    check = _check(report, "risk_mode.reliance_counts")
    assert check["status"] == "warn"
    assert check["details"]["readiness_state"] == "insufficient_manifest_fields"
    assert check["details"]["missing_manifest_fields"] == [
        "risk_mode_reliance_present_counts",
        "risk_mode_reliance_by_risk_mode_counts",
        "risk_mode_reliance_check_status_counts",
    ]


def test_malformed_manifest_fails_deterministically(tmp_path: Path) -> None:
    manifest = tmp_path / "bad-manifest.json"
    manifest.write_text("{not-json", encoding="utf-8")

    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=tmp_path / "missing-default",
        manifest_path=manifest,
        env={},
        cwd=tmp_path,
    )

    check = _check(report, "review_corpus.manifest_readable")
    assert report["status"] == "fail"
    assert check["status"] == "fail"
    assert check["details"]["error"] == "manifest is not valid JSON"
    assert str(tmp_path) not in render_doctor_report_json(report)


def test_provider_env_values_are_never_printed(tmp_path: Path) -> None:
    token_value = "dont-print-this-token"
    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=tmp_path / "missing-default",
        env={"LOLLA_OPENROUTER_API_KEY": token_value},
        cwd=tmp_path,
    )

    rendered = render_doctor_report_json(report)
    assert token_value not in rendered
    assert "openrouter_credential_present" in rendered


def test_no_raw_private_content_fields_are_included(tmp_path: Path) -> None:
    raw_message_key = "raw" + "_message_content"
    fabricated_key = "fabricated" + "_passages"
    report = build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=tmp_path / "missing-default",
        manifest_path=_write_manifest(
            tmp_path,
            {
                **_manifest(),
                raw_message_key: "RAW MODEL MESSAGE SHOULD NOT EXPORT",
                fabricated_key: ["FABRICATED"],
            },
        ),
        env={},
        cwd=tmp_path,
    )

    rendered = render_doctor_report_json(report)
    assert report["custody_flags"]["prints_raw_transcript"] is False
    assert report["custody_flags"]["prints_raw_memo"] is False
    assert report["custody_flags"]["prints_raw_revised_answer"] is False
    assert raw_message_key not in rendered
    assert fabricated_key not in rendered
    assert "RAW MODEL MESSAGE SHOULD NOT EXPORT" not in rendered


def test_no_model_client_module_is_imported(tmp_path: Path) -> None:
    sys.modules.pop("engine.system_b.boundary_provider", None)

    build_doctor_report(
        runtime_root=_runtime_root(tmp_path),
        archive_root=tmp_path / "missing-default",
        env={},
        cwd=tmp_path,
    )

    assert "engine.system_b.boundary_provider" not in sys.modules


def test_cli_writes_only_to_explicit_external_output(tmp_path: Path) -> None:
    runtime = _runtime_root(tmp_path)
    archive = tmp_path / "runs"
    archive.mkdir()
    out = tmp_path / "doctor.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/lolla_doctor.py",
            "--runtime-root",
            str(runtime),
            "--archive-root",
            str(archive),
            "--json",
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert out.exists()
    assert list(archive.iterdir()) == []
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == DOCTOR_REPORT_SCHEMA_VERSION
    assert payload["summary"]["model_calls"] == 0
    assert payload["summary"]["archives_mutated"] is False


def test_cli_refuses_output_inside_archive_root(tmp_path: Path) -> None:
    runtime = _runtime_root(tmp_path)
    archive = tmp_path / "runs"
    archive.mkdir()
    out = archive / "doctor.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/lolla_doctor.py",
            "--runtime-root",
            str(runtime),
            "--archive-root",
            str(archive),
            "--json",
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert not out.exists()
    payload = json.loads(result.stdout)
    assert payload["status"] == "fail"
    assert _check(payload, "output.path_safety")["status"] == "fail"
    assert result.stderr == ""
