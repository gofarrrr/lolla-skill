from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from engine.system_b.audit_decision_record import (
    ACTIONABLE_DELTA_BUCKET_STATUSES,
    ACTIONABLE_DELTA_LABELS,
    AUDIT_DECISION_RECORD_SCHEMA_VERSION,
    AuditDecisionRecordInputError,
    build_audit_decision_record,
    render_audit_decision_record_json,
    validate_output_path,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


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
            "changed_advice_summary": [
                "Use a narrower gate before relying on the recommendation."
            ],
            "take_backs": [
                "Do not treat artifact cleanliness as approval."
            ],
            "human_questions": [
                "Which reviewer owns the final reliance decision?"
            ],
            "caller_action": "use_revised_answer",
        },
    )
    _write_json(
        run_dir / "evaluation.json",
        {
            "schema_version": "lolla.evaluation.v0",
            "case_id": "sample-case",
            "run_id": "20260629T000000Z_test",
            "overall": "pass",
        },
    )
    _write_json(
        run_dir / "reasoning_trace.json",
        {
            "schema_version": "lolla.reasoning_trace.v0.2",
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
    _write_json(run_dir / "extraction.json", {"status": "ok"})
    _write_json(run_dir / "result.json", {"run_health": {"overall": "healthy"}})
    return run_dir


def test_builds_valid_record_from_minimal_structured_run_dir(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    record = build_audit_decision_record(run_dir=run_dir)

    assert record["schema_version"] == AUDIT_DECISION_RECORD_SCHEMA_VERSION
    assert record["case_id"] == "sample-case"
    assert record["run_id"] == "20260629T000000Z_test"
    assert record["archive_relpath"] == "sample-case/20260629T000000Z_test"
    assert record["decision_question"]["status"] == "populated_from_structured_artifact"
    assert record["revised_recommendation_summary"]["status"] == "populated_from_structured_artifact"
    unresolved = record["unresolved_questions"]
    assert unresolved["status"] == "populated_from_structured_artifact"
    assert unresolved["items"][0]["source_refs"] == [
        {"artifact": "agent_result.json", "field": "human_questions"}
    ]
    assert record["review_refs"] == []
    assert record["custody_flags"]["model_calls"] == 0
    assert record["custody_flags"]["archive_mutated"] is False


def test_output_schema_version_is_stable(tmp_path: Path) -> None:
    record = build_audit_decision_record(run_dir=_minimal_run_dir(tmp_path))

    assert record["schema_version"] == "lolla.audit_decision_record.v0"


def test_includes_every_pr31_actionable_delta_bucket(tmp_path: Path) -> None:
    record = build_audit_decision_record(run_dir=_minimal_run_dir(tmp_path))
    deltas = record["actionable_deltas"]

    assert list(deltas["bucket_status"]) == list(ACTIONABLE_DELTA_LABELS)
    assert list(deltas["buckets"]) == list(ACTIONABLE_DELTA_LABELS)
    assert all(
        status == "not_supplied"
        for status in deltas["bucket_status"].values()
    )
    assert all(value == [] for value in deltas["buckets"].values())


def test_pr31_population_policy_makes_empty_buckets_non_claims(tmp_path: Path) -> None:
    record = build_audit_decision_record(run_dir=_minimal_run_dir(tmp_path))
    policy = record["actionable_deltas"]["population_policy"]

    assert policy["owner"] == "human_review"
    assert policy["exporter_infers_from_prose"] is False
    assert policy["empty_bucket_meaning"] == "not_supplied_or_not_measured"
    assert policy["label_source_required"] is True
    assert policy["status_vocabulary"] == list(ACTIONABLE_DELTA_BUCKET_STATUSES)
    assert "Empty arrays are non-claims" in policy["notes"][1]


def test_semantic_fields_include_status_and_non_claim_metadata(tmp_path: Path) -> None:
    record = build_audit_decision_record(run_dir=_minimal_run_dir(tmp_path))

    assert record["decision_question"]["exporter_inferred_from_prose"] is False
    assert record["decision_question"]["source_refs"] == [
        {"artifact": "reasoning_trace.json", "field": "case.decision_situation"}
    ]
    assert record["original_recommendation_summary"]["status"] == "not_measured"
    assert record["original_recommendation_summary"]["source_refs"] == []
    conflicts = record["conflicts_or_unresolved_tensions"]
    assert conflicts["status"] == "not_supplied"
    assert conflicts["items"] == []
    assert "not evidence" in conflicts["empty_meaning"]
    unresolved = record["unresolved_questions"]
    assert unresolved["items"]
    assert unresolved["exporter_inferred_from_prose"] is False


def test_output_path_inside_run_dir_is_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(AuditDecisionRecordInputError, match="outside run directory"):
        validate_output_path(output_path=run_dir / "record.json", run_dir=run_dir)


def test_output_path_equal_to_run_dir_is_rejected(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)

    with pytest.raises(AuditDecisionRecordInputError, match="outside run directory"):
        validate_output_path(output_path=run_dir, run_dir=run_dir)


def test_raw_files_are_not_read_or_copied(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    raw_markers = {
        "conversation.txt": "RAW CONVERSATION DO NOT COPY",
        "memo.md": "RAW MEMO DO NOT COPY",
        "revised.txt": "RAW REVISED ANSWER DO NOT COPY",
        "live_transcript.txt": "RAW LIVE TRANSCRIPT DO NOT COPY",
    }
    for name, marker in raw_markers.items():
        (run_dir / name).write_text(marker, encoding="utf-8")

    original_read_text = Path.read_text

    def guarded_read_text(path: Path, *args: object, **kwargs: object) -> str:
        if path.name in raw_markers:
            raise AssertionError(f"raw artifact was read: {path.name}")
        return original_read_text(path, *args, **kwargs)

    with patch.object(Path, "read_text", guarded_read_text):
        record = build_audit_decision_record(run_dir=run_dir)

    rendered = render_audit_decision_record_json(record, pretty=True)
    for marker in raw_markers.values():
        assert marker not in rendered
    assert all(item["artifact"] not in raw_markers for item in record["source_artifacts"])


def test_missing_optional_artifacts_are_conservative_not_crashes(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "case" / "run"
    run_dir.mkdir(parents=True)
    _write_json(
        run_dir / "agent_result.json",
        {
            "schema_version": "lolla_agent_result.v1",
            "case_id": "case",
            "run_id": "run",
        },
    )

    record = build_audit_decision_record(run_dir=run_dir)

    statuses = {item["artifact"]: item["status"] for item in record["source_artifacts"]}
    assert statuses["evaluation.json"] == "missing"
    assert statuses["reasoning_trace.json"] == "missing"
    assert statuses["extraction_adequacy_report.json"] == "missing"
    assert record["decision_question"]["status"] == "unavailable_missing_artifact"
    assert record["revised_recommendation_summary"]["status"] == "not_supplied"
    assert record["unresolved_questions"]["status"] == "not_supplied"
    assert "Missing structured artifacts were recorded as missing rather than guessed." in record["limitations"]


def test_malformed_optional_json_is_handled_deterministically(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    (run_dir / "evaluation.json").write_text("{not-json", encoding="utf-8")

    record = build_audit_decision_record(run_dir=run_dir)

    evaluation = next(item for item in record["source_artifacts"] if item["artifact"] == "evaluation.json")
    assert evaluation["status"] == "malformed"
    assert evaluation["error"] == "invalid_json"
    assert "Malformed structured artifacts were recorded as malformed rather than guessed." in record["limitations"]


def test_malformed_semantic_source_sets_unavailable_status(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    (run_dir / "reasoning_trace.json").write_text("{not-json", encoding="utf-8")

    record = build_audit_decision_record(run_dir=run_dir)

    assert record["decision_question"]["status"] == "unavailable_malformed_artifact"


def test_custody_flags_remain_false_for_excluded_content(tmp_path: Path) -> None:
    record = build_audit_decision_record(run_dir=_minimal_run_dir(tmp_path))

    custody = record["custody_flags"]
    assert custody == {
        "raw_transcript_included": False,
        "raw_memo_included": False,
        "raw_revised_answer_included": False,
        "provider_text_included": False,
        "private_reasoning_included": False,
        "local_absolute_paths_included": False,
        "secrets_included": False,
        "model_calls": 0,
        "archive_mutated": False,
    }


def test_generated_json_contains_no_local_absolute_archive_paths(tmp_path: Path) -> None:
    record = build_audit_decision_record(run_dir=_minimal_run_dir(tmp_path))

    rendered = render_audit_decision_record_json(record, pretty=True)
    assert str(tmp_path) not in rendered
    local_users_marker = "/" + "Users" + "/"
    assert local_users_marker not in rendered
    assert "sample-case/20260629T000000Z_test" in rendered


def test_optional_review_json_adds_safe_review_reference_without_labels_or_scoring(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    review_json = tmp_path / "review.json"
    _write_json(
        review_json,
        {
            "schema_version": "lolla.audit_decision_record_fixture_review.v0",
            "reviews": [
                {
                    "fixture_id": "fixture_1",
                    "review_status": "pass",
                    "notes": "Safe paraphrase-only review note.",
                }
            ],
        },
    )

    record = build_audit_decision_record(run_dir=run_dir, review_json=review_json)

    assert record["review_refs"] == [
        {
            "ref_id": "review_json",
            "relative_path": "review.json",
            "status": "present",
            "schema_version": "lolla.audit_decision_record_fixture_review.v0",
            "review_count": 1,
            "labels_created": False,
            "answer_quality_scored": False,
            "raw_content_included": False,
        }
    ]
    deltas = record["actionable_deltas"]
    assert all(value == [] for value in deltas["buckets"].values())
    assert all(
        status == "not_supplied"
        for status in deltas["bucket_status"].values()
    )
    assert "Safe paraphrase-only review note." not in render_audit_decision_record_json(record)


def test_review_json_can_supply_explicit_pr31_labels_without_prose_inference(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    review_json = tmp_path / "review-labels.json"
    _write_json(
        review_json,
        {
            "schema_version": "lolla.safe_review_labels.v0",
            "actionable_deltas": {
                "buckets": {
                    "action_changed": [
                        {
                            "summary": "Reviewer supplied an explicit action-change label.",
                            "grounding": "review_supplied",
                            "review_note": "This note should not be copied.",
                        }
                    ],
                    "threshold_changed": [],
                }
            },
        },
    )

    record = build_audit_decision_record(run_dir=run_dir, review_json=review_json)
    deltas = record["actionable_deltas"]

    assert deltas["population_policy"]["exporter_infers_from_prose"] is False
    assert deltas["bucket_status"]["action_changed"] == "populated_from_review"
    assert deltas["bucket_status"]["threshold_changed"] == "not_supplied"
    assert deltas["buckets"]["action_changed"] == [
        {
            "summary": "Reviewer supplied an explicit action-change label.",
            "grounding": "review_supplied",
            "source": "review_json:actionable_deltas.action_changed",
        }
    ]
    rendered = render_audit_decision_record_json(record, pretty=True)
    assert "This note should not be copied." not in rendered


def test_cli_writes_only_requested_external_output_file(tmp_path: Path) -> None:
    run_dir = _minimal_run_dir(tmp_path)
    before = {path.relative_to(run_dir) for path in run_dir.rglob("*")}
    output = tmp_path / "out" / "audit_decision_record.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_audit_decision_record.py",
            "--run-dir",
            str(run_dir),
            "--out",
            str(output),
            "--pretty",
        ],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0
    assert result.stdout == ""
    assert output.is_file()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schema_version"] == AUDIT_DECISION_RECORD_SCHEMA_VERSION
    after = {path.relative_to(run_dir) for path in run_dir.rglob("*")}
    assert after == before
