from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from engine.system_b.review_corpus import REVIEW_CORPUS_MANIFEST_SCHEMA_VERSION
from engine.system_b.review_corpus_evidence_readiness import (
    REVIEW_CORPUS_EVIDENCE_READINESS_SCHEMA_VERSION,
    build_evidence_readiness,
    render_evidence_readiness_json,
    render_evidence_readiness_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _manifest(**overrides: object) -> dict:
    payload: dict[str, object] = {
        "schema_version": REVIEW_CORPUS_MANIFEST_SCHEMA_VERSION,
        "record_schema_version": "lolla.review_corpus_record.v0",
        "archive_root": "/Users/example/SHOULD_NOT_EXPORT",
        "record_count": 80,
        "risk_mode_counts": {"standard": 80},
        "risk_mode_reliance_present_counts": {"false": 80, "true": 0},
        "risk_mode_reliance_by_risk_mode_counts": {"standard|false": 80},
        "risk_mode_reliance_check_status_counts": {"unavailable": 80},
    }
    payload.update(overrides)
    return payload


def test_readiness_reports_no_high_stakes_evidence() -> None:
    readiness = build_evidence_readiness(_manifest())

    assert readiness["schema_version"] == REVIEW_CORPUS_EVIDENCE_READINESS_SCHEMA_VERSION
    assert readiness["evidence_state"] == "no_high_stakes_reliance_evidence"
    assert readiness["recommendation"] == "do_not_claim_high_stakes_archive_evidence"
    assert readiness["record_count"] == 80
    assert readiness["risk_mode_counts"] == {"standard": 80}
    assert readiness["risk_mode_reliance_present_counts"] == {
        "false": 80,
        "true": 0,
    }
    assert readiness["high_stakes_reliance_present_count"] == 0
    assert readiness["missing_manifest_fields"] == []


def test_readiness_reports_high_stakes_evidence_present() -> None:
    readiness = build_evidence_readiness(
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
        )
    )

    assert readiness["evidence_state"] == "has_high_stakes_reliance_evidence"
    assert readiness["recommendation"] == "ready_for_high_stakes_review_batch"
    assert readiness["high_stakes_reliance_present_count"] == 1
    assert readiness["risk_mode_reliance_check_status_counts"] == {
        "unavailable": 1,
        "pass": 1,
    }


def test_readiness_refuses_to_infer_from_old_manifest_shape() -> None:
    manifest = _manifest()
    manifest.pop("risk_mode_reliance_present_counts")
    manifest.pop("risk_mode_reliance_by_risk_mode_counts")
    manifest.pop("risk_mode_reliance_check_status_counts")

    readiness = build_evidence_readiness(manifest)

    assert readiness["evidence_state"] == "insufficient_manifest_fields"
    assert readiness["recommendation"] == "do_not_claim_high_stakes_archive_evidence"
    assert readiness["missing_manifest_fields"] == [
        "risk_mode_reliance_present_counts",
        "risk_mode_reliance_by_risk_mode_counts",
        "risk_mode_reliance_check_status_counts",
    ]
    assert readiness["high_stakes_reliance_present_count"] == 0


def test_readiness_outputs_do_not_copy_local_paths_or_raw_markers() -> None:
    readiness = build_evidence_readiness(
        _manifest(
            archive_root="/Users/example/SECRET_HOME/runs",
            raw_message_content="RAW MODEL MESSAGE SHOULD NOT EXPORT",
            fabricated_passages=["FABRICATED"],
            notes="client_secret api_key password",
        )
    )

    rendered = (
        render_evidence_readiness_json(readiness)
        + render_evidence_readiness_markdown(readiness)
    )

    for forbidden in (
        "/Users/",
        "SECRET",
        "raw_message_content",
        "fabricated_passages",
        "RAW MODEL MESSAGE SHOULD NOT EXPORT",
        "client_secret",
        "api_key",
        "password",
    ):
        assert forbidden not in rendered


def test_cli_writes_markdown_and_json_outputs(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    out_path = tmp_path / "readiness.md"
    json_out_path = tmp_path / "readiness.json"
    manifest_path.write_text(json.dumps(_manifest()), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/analyze_review_corpus_evidence_readiness.py",
            "--manifest",
            str(manifest_path),
            "--out",
            str(out_path),
            "--json-out",
            str(json_out_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    markdown = out_path.read_text(encoding="utf-8")
    payload = json.loads(json_out_path.read_text(encoding="utf-8"))
    assert "no_high_stakes_reliance_evidence" in markdown
    assert payload["evidence_state"] == "no_high_stakes_reliance_evidence"


def test_cli_reports_sanitized_invalid_manifest_error(tmp_path: Path) -> None:
    manifest_path = tmp_path / "bad.json"
    manifest_path.write_text("{not-json", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/analyze_review_corpus_evidence_readiness.py",
            "--manifest",
            str(manifest_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.strip() == "error: manifest is not valid JSON"
    assert str(tmp_path) not in result.stderr
