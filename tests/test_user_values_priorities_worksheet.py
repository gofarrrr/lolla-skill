from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from engine.system_b.user_values_priorities_worksheet import (
    FORBIDDEN_MARKERS,
    InputError,
    USER_VALUES_PRIORITIES_WORKSHEET_SCHEMA_VERSION,
    build_blank_worksheet,
    render_blank_worksheet_json,
    validate_blank_worksheet,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_default_blank_worksheet() -> None:
    worksheet = build_blank_worksheet()

    assert (
        worksheet["schema_version"]
        == USER_VALUES_PRIORITIES_WORKSHEET_SCHEMA_VERSION
    )
    assert worksheet["case_id"] == ""
    assert worksheet["run_id"] == ""
    assert worksheet["archive_relpath"] == ""
    assert worksheet["review_scope"] == "human_review_only"
    assert worksheet["source"]["local_only"] is True
    assert worksheet["source"]["blank_template"] is True
    assert worksheet["source"]["human_filled"] is False
    assert worksheet["source"]["auto_extracted"] is False
    assert worksheet["source"]["model_calls"] == 0
    assert worksheet["source"]["llm_judge_used"] is False
    assert worksheet["values_items"] == []
    assert worksheet["conflicts"] == []
    assert all(value == [] for value in worksheet["answer_treatment"].values())
    assert all(value == "unfilled" for value in worksheet["reviewer_summary"].values())
    assert worksheet["reviewer_notes"] == []
    assert validate_blank_worksheet(worksheet) == []


def test_build_blank_worksheet_with_metadata() -> None:
    worksheet = build_blank_worksheet(
        case_id="case-a",
        run_id="run-b",
        archive_relpath="case-a/run-b",
    )

    assert worksheet["case_id"] == "case-a"
    assert worksheet["run_id"] == "run-b"
    assert worksheet["archive_relpath"] == "case-a/run-b"
    assert validate_blank_worksheet(worksheet) == []


def test_builder_rejects_absolute_archive_relpath() -> None:
    with pytest.raises(InputError) as exc:
        build_blank_worksheet(archive_relpath="/Users/example/runs/case/run")

    message = str(exc.value)
    assert "archive_relpath" in message
    assert "absolute path" in message
    assert "/Users/" not in message
    assert "example/runs" not in message


def test_builder_rejects_raw_or_private_marker_metadata_without_leaking_it() -> None:
    for marker in FORBIDDEN_MARKERS:
        with pytest.raises(InputError) as exc:
            build_blank_worksheet(case_id=f"case-{marker}")
        message = str(exc.value)
        assert "case_id" in message
        assert marker not in message


def test_cli_writes_json(tmp_path: Path) -> None:
    out_path = tmp_path / "worksheet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_user_values_priorities_worksheet.py",
            "--case-id",
            "case-a",
            "--run-id",
            "run-b",
            "--archive-relpath",
            "case-a/run-b",
            "--out",
            str(out_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == USER_VALUES_PRIORITIES_WORKSHEET_SCHEMA_VERSION
    assert payload["case_id"] == "case-a"
    assert payload["run_id"] == "run-b"
    assert payload["archive_relpath"] == "case-a/run-b"
    assert validate_blank_worksheet(payload) == []


def test_cli_rejects_absolute_archive_relpath_with_sanitized_stderr(
    tmp_path: Path,
) -> None:
    out_path = tmp_path / "worksheet.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_user_values_priorities_worksheet.py",
            "--archive-relpath",
            "/Users/example/runs/case/run",
            "--out",
            str(out_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert result.stdout == ""
    assert "archive_relpath" in result.stderr
    assert "absolute path" in result.stderr
    assert "/Users/" not in result.stderr
    assert "example/runs" not in result.stderr
    assert not out_path.exists()


def test_validator_catches_malformed_prefilled_or_extracted_payload() -> None:
    payload = build_blank_worksheet()
    malformed = deepcopy(payload)
    malformed["source"]["auto_extracted"] = True
    malformed["values_items"] = [{"id": "value_001"}]

    errors = validate_blank_worksheet(malformed)

    assert "source.auto_extracted must be false" in errors
    assert "values_items must be an empty list" in errors


def test_rendered_output_excludes_local_paths_and_raw_private_markers() -> None:
    rendered = render_blank_worksheet_json(
        build_blank_worksheet(
            case_id="case-a",
            run_id="run-b",
            archive_relpath="case-a/run-b",
        )
    )

    for marker in FORBIDDEN_MARKERS:
        assert marker not in rendered
    assert "raw transcript" not in rendered
    assert "raw memo" not in rendered
    assert "revised answer text" not in rendered
    assert "provider message content" not in rendered
    assert "private reasoning text" not in rendered
