from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.agent_result import write_agent_result
from engine.system_b.capture_adequacy import CAPTURE_ADEQUACY_SCHEMA_VERSION
from engine.system_b.control_plane import (
    CONTROL_INPUT_SCHEMA_VERSION,
    CONTROL_RESULT_SCHEMA_VERSION,
    write_control_result,
)
from engine.system_b.evaluation import EVALUATION_SCHEMA_VERSION, write_evaluation
from engine.system_b.extraction_adequacy_report import write_extraction_adequacy_report
from engine.system_b.provider_boundary_health import build_provider_boundary_health
from engine.system_b.reasoning_trace import REASONING_TRACE_SCHEMA_VERSION, write_reasoning_trace
from engine.system_b.review_corpus import (
    HUMAN_REVIEW_SCHEMA_VERSION,
    REVIEW_CORPUS_MANIFEST_SCHEMA_VERSION,
    REVIEW_CORPUS_RECORD_SCHEMA_VERSION,
    build_review_corpus_manifest,
    build_review_corpus_records,
    write_json,
    write_jsonl,
)


def _expected_scope(artifact: str) -> dict:
    return {
        "artifact": artifact,
        "local_only": True,
        "raw_transcript_included": False,
        "raw_memo_included": False,
        "raw_revised_answer_included": False,
        "raw_model_message_content_included": False,
        "provider_reasoning_details_included": False,
        "control_argument_values_included": False,
        "shareable_without_review": False,
        "advice_quality_scored": False,
        "model_calls": 0,
        "llm_judge_used": False,
        "automatic_approval": False,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _healthy_run_health() -> dict:
    health = {
        "overall": "healthy",
        "product_output_health": "clean",
        "live_output_health": "clean",
        "issues": [],
        "issue_details": [],
    }
    health["provider_boundary_health"] = build_provider_boundary_health(health)
    return health


def _degraded_run_health() -> dict:
    health = {
        "overall": "degraded",
        "product_output_health": "clean",
        "live_output_health": "clean",
        "issues": ["artifact_custody_failure"],
        "issue_details": [
            {
                "code": "artifact_custody_failure",
                "severity": "degraded",
                "axis": "artifact_custody",
            }
        ],
    }
    health["provider_boundary_health"] = build_provider_boundary_health(health)
    return health


def _capture_adequacy(run_id: str) -> dict:
    return {
        "schema_version": CAPTURE_ADEQUACY_SCHEMA_VERSION,
        "run_id": run_id,
        "status": "good",
        "capture_strategy": "full",
        "declared_turn_count": 2,
        "captured_turn_count": 2,
        "omitted_turn_count": 0,
        "captured_windows": [
            {
                "label": "full",
                "start_turn": 1,
                "end_turn": 2,
                "turn_count": 2,
            }
        ],
        "omitted_windows": [],
        "risk_flags": [],
        "notes": [],
    }


def _control_input() -> dict:
    return {
        "schema_version": CONTROL_INPUT_SCHEMA_VERSION,
        "mode": "pre_action_reasoning_gate",
        "external_trace_id": "trace_123",
        "external_span_ids": ["span_a"],
        "agent_run_id": "agent_run_456",
        "agent_framework": "openai_agents_sdk",
        "proposed_action": {
            "tool_name": "send_email",
            "risk_class": "external_side_effect",
            "arguments": {
                "to": "customer@example.com",
                "subject": "Account closure",
            },
        },
        "control_context": {
            "approval_id": "approval_001",
            "policy_engine": "crabtrap",
            "policy_decision": "needs_review",
            "sandbox_id": "sandbox_abc",
            "credential_scope": "gmail.send",
            "tool_call_ids": ["tool_call_1"],
        },
    }


def _seed_run(
    archive_root: Path,
    *,
    case_id: str = "case-a",
    run_id: str = "20260625T120000Z_abcd12",
    include_evaluation: bool = True,
    include_control: bool = True,
    risk_mode: str = "standard",
    run_health: dict | None = None,
) -> Path:
    run_dir = archive_root / case_id / run_id
    run_dir.mkdir(parents=True)
    raw_message_key = "raw_" + "message_content"
    (run_dir / "conversation.txt").write_text(
        "[Turn 1] USER:\nShould we send the email?\n\n[Turn 2] ASSISTANT:\nOnly after approval.\n",
        encoding="utf-8",
    )
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "capture_adequacy": _capture_adequacy(run_id),
            "extraction": {
                "decision_situation": "Whether to send an external email",
                "reasoning_passages": ["Only send after explicit approval."],
            },
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "status": "ok",
            "risk_mode": risk_mode,
            "run_health": run_health or _healthy_run_health(),
            "revised_answer": "Send only after explicit approval.",
            "usage_summary": {
                "run_id": run_id,
                "pricing_table_version": "2026-05-25",
                "estimated_total_cost_usd": 0.012345,
                "cost_estimate_state": "complete",
                "vendors": {
                    "openrouter": {
                        "provider": "openrouter",
                        "primary_model": "test/model-1",
                        "models_seen": ["test/model-1"],
                        "requested_models_seen": ["test/model"],
                        "calls": 1,
                    }
                },
            },
            "audit_summary": {
                "boundary_calls": [
                    {
                        "stage": "extraction",
                        "provider_name": "openrouter",
                        "requested_model": "test/model",
                        "served_model": "test/model-1",
                        "model": "test/model-1",
                        "status": "ok",
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                        raw_message_key: "RAW MODEL MESSAGE SHOULD NOT EXPORT",
                    }
                ]
            },
        },
    )
    (run_dir / "revised.txt").write_text(
        "Send only after explicit approval.",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Memo\n\nDo not send before approval.\n", encoding="utf-8")
    _write_json(
        run_dir / "run_events.json",
        {
            "schema_version": "lolla.run_events.v0.1",
            "run_id": run_id,
            "events": [
                {
                    "event_type": "archive_completed",
                    "timestamp": "2026-06-25T12:01:00Z",
                }
            ],
        },
    )
    _write_json(
        run_dir / "graph_survival_report.json",
        {"schema_version": "lolla.graph_survival_report.v0.1"},
    )
    (run_dir / "graph_survival_report.md").write_text("# Graph\n", encoding="utf-8")
    if include_control:
        _write_json(run_dir / "control_input.json", _control_input())

    write_agent_result(run_dir, run_id=run_id, case_id=case_id)
    if include_control:
        write_control_result(run_dir, run_id=run_id, case_id=case_id)
    write_extraction_adequacy_report(run_dir, run_id=run_id, case_id=case_id)

    files_copied = [
        "conversation.txt",
        "extraction.json",
        "result.json",
        "revised.txt",
        "memo.md",
        "run_events.json",
        "graph_survival_report.json",
        "graph_survival_report.md",
        "agent_result.json",
        "extraction_adequacy_report.json",
    ]
    if include_control:
        files_copied.extend(["control_input.json", "control_result.json"])
    write_reasoning_trace(
        run_dir,
        run_id=run_id,
        case_id=case_id,
        fingerprint="send external email",
        how_matched="new_case",
        files_copied=files_copied,
        files_missing=[],
        manifest={"run_count": 1},
    )
    if include_evaluation:
        write_evaluation(run_dir, run_id=run_id, case_id=case_id)
        write_reasoning_trace(
            run_dir,
            run_id=run_id,
            case_id=case_id,
            fingerprint="send external email",
            how_matched="new_case",
            files_copied=files_copied + ["evaluation.json"],
            files_missing=[],
            manifest={"run_count": 1},
        )
    return run_dir


def _seed_legacy_content_run(
    archive_root: Path,
    *,
    case_id: str = "legacy-case",
    run_id: str = "20260625T150000Z_mnop78",
) -> Path:
    run_dir = archive_root / case_id / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "conversation.txt").write_text(
        "[Turn 1] USER:\nShould I take the role?\n\n[Turn 2] ASSISTANT:\nOnly after diligence.\n",
        encoding="utf-8",
    )
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "extraction": {
                "decision_situation": "Whether to take a role",
                "reasoning_passages": ["Only after diligence."],
            },
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "status": "ok",
            "risk_mode": "standard",
            "revised_answer": "Take the role only after diligence.",
        },
    )
    (run_dir / "revised.txt").write_text(
        "Take the role only after diligence.",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Memo\n\nDiligence first.\n", encoding="utf-8")
    return run_dir


def test_review_corpus_exports_modern_archive_without_sensitive_control_args(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root)

    records = build_review_corpus_records(archive_root)

    assert len(records) == 1
    record = records[0]
    assert record["schema_version"] == REVIEW_CORPUS_RECORD_SCHEMA_VERSION
    assert record["case_id"] == "case-a"
    assert record["run_id"] == "20260625T120000Z_abcd12"
    assert record["archive_path"].endswith("case-a/20260625T120000Z_abcd12")
    assert record["archive_relpath"] == "case-a/20260625T120000Z_abcd12"
    assert record["valid_archive"] is True
    assert record["agent_result"]["caller_action"] == "use_revised_answer"
    assert record["run_health"]["overall"] == "healthy"
    assert record["capture_adequacy"]["status"] == "good"
    assert record["evaluation"]["overall"] == "pass"
    assert record["evaluation"]["caller_readiness"] == "ready"
    assert record["risk_mode_reliance"] == {
        "present": False,
        "risk_mode": "standard",
    }
    assert record["review_readiness_tier"] == "full_modern_reviewable"
    assert record["batch_recommendation"] == "recommended_modern_review_batch"
    assert record["content_review"] == {
        "available": True,
        "missing_artifacts": [],
        "reason": "core content artifacts are available",
    }
    assert record["custody_review"] == {
        "available": True,
        "missing_artifacts": [],
        "missing_metadata": [],
        "reason": "modern custody artifacts and capture adequacy are available",
    }
    assert record["artifacts"]["evaluation.json"]["available"] is True
    assert record["artifacts"]["agent_result.json"]["sha256"].startswith("sha256:")
    assert record["schema_versions"]["reasoning_trace"] == REASONING_TRACE_SCHEMA_VERSION
    assert record["schema_versions"]["evaluation"] == EVALUATION_SCHEMA_VERSION
    assert record["schema_versions"]["control_result"] == CONTROL_RESULT_SCHEMA_VERSION
    assert record["model_provider_summary"]["providers"] == ["openrouter"]
    assert record["usage"]["estimated_total_cost_usd"] == 0.012345

    control = record["control_plane"]
    assert control["control_input_available"] is True
    assert control["control_result_available"] is True
    assert control["control_context"]["proposed_action"] == {
        "tool_name": "send_email",
        "risk_class": "external_side_effect",
        "has_arguments": True,
        "argument_keys": ["subject", "to"],
    }
    assert record["human_review"] == {
        "schema_version": HUMAN_REVIEW_SCHEMA_VERSION,
        "reviewer_id": None,
        "review_status": None,
        "primary_failure_mode": None,
        "severity": None,
        "useful_friction": None,
        "noisy_friction": None,
        "missing_friction": None,
        "revised_answer_improved": None,
        "safe_for_agent_use": None,
        "reviewer_notes": None,
    }
    assert record["scope"] == _expected_scope("review_corpus")
    serialized = json.dumps(record, sort_keys=True)
    assert "customer@example.com" not in serialized
    assert "Account closure" not in serialized
    assert "RAW MODEL MESSAGE SHOULD NOT EXPORT" not in serialized


def test_review_corpus_exports_high_stakes_reliance_caveat(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        case_id="high-stakes-case",
        run_id="20260625T160000Z_high01",
        risk_mode="high_stakes",
    )

    record = build_review_corpus_records(archive_root)[0]

    assert record["risk_mode"] == "high_stakes"
    assert record["agent_result"]["caller_action"] == "ask_user_first"
    assert record["evaluation"]["caller_readiness"] == "inspect_first"
    assert record["risk_mode_reliance"] == {
        "present": True,
        "risk_mode": "high_stakes",
        "check_id": "risk_mode_reliance_policy",
        "status": "pass",
        "caller_action": "ask_user_first",
        "caller_readiness": "inspect_first",
        "requires_human_review": True,
        "requires_domain_review": True,
        "automatic_safe_for_agent_use": False,
    }


def test_review_corpus_standard_clean_has_no_high_stakes_reliance_caveat(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root)

    record = build_review_corpus_records(archive_root)[0]

    assert record["risk_mode"] == "standard"
    assert record["agent_result"]["caller_action"] == "use_revised_answer"
    assert record["evaluation"]["caller_readiness"] == "ready"
    assert record["risk_mode_reliance"] == {
        "present": False,
        "risk_mode": "standard",
    }


def test_review_corpus_degraded_high_stakes_reliance_stays_blocked(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        case_id="degraded-high-stakes-case",
        run_id="20260625T170000Z_high02",
        risk_mode="high_stakes",
        run_health=_degraded_run_health(),
    )

    record = build_review_corpus_records(archive_root)[0]

    assert record["risk_mode"] == "high_stakes"
    assert record["run_health"]["overall"] == "degraded"
    assert record["agent_result"]["caller_action"] == "do_not_use_run_degraded"
    assert record["evaluation"]["caller_readiness"] == "do_not_use"
    assert record["risk_mode_reliance"] == {
        "present": True,
        "risk_mode": "high_stakes",
        "check_id": "risk_mode_reliance_policy",
        "status": "pass",
        "caller_action": "do_not_use_run_degraded",
        "caller_readiness": "do_not_use",
        "requires_human_review": True,
        "requires_domain_review": True,
        "automatic_safe_for_agent_use": False,
    }


def test_review_corpus_risk_mode_reliance_surface_is_custody_safe(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        case_id="high-stakes-custody-case",
        run_id="20260625T180000Z_high03",
        risk_mode="high_stakes",
    )

    record = build_review_corpus_records(archive_root)[0]
    serialized = json.dumps(record["risk_mode_reliance"], sort_keys=True)

    assert str(archive_root) not in serialized
    for forbidden in (
        "Should we send the email?",
        "Do not send before approval.",
        "Send only after explicit approval.",
        "RAW MODEL MESSAGE SHOULD NOT EXPORT",
        "Only after approval.",
        "private reasoning",
        "credential_scope",
        "customer@example.com",
        "Account closure",
    ):
        assert forbidden not in serialized


def test_review_corpus_represents_older_archive_missing_evaluation_and_control(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(
        archive_root,
        case_id="older-case",
        run_id="20260625T130000Z_efgh34",
        include_evaluation=False,
        include_control=False,
    )

    record = build_review_corpus_records(archive_root)[0]

    assert record["valid_archive"] is True
    assert record["evaluation"] == {
        "available": False,
        "overall": "unavailable",
        "caller_readiness": "unavailable",
    }
    assert record["risk_mode_reliance"] == {
        "present": False,
        "risk_mode": "standard",
    }
    assert record["artifacts"]["evaluation.json"]["available"] is False
    assert record["control_plane"]["control_input_available"] is False
    assert record["control_plane"]["control_result_available"] is False
    assert record["control_plane"]["control_context"] == {}
    assert record["artifact_counts"]["optional_missing_count"] >= 3
    assert record["review_readiness_tier"] == "modern_partial_reviewable"
    assert record["batch_recommendation"] == "recommended_modern_review_batch"
    assert record["content_review"]["available"] is True
    assert record["custody_review"]["available"] is False
    assert record["custody_review"]["missing_artifacts"] == ["evaluation.json"]
    assert record["custody_review"]["missing_metadata"] == []


def test_review_corpus_marks_legacy_content_reviewable_without_modern_sidecars(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    _seed_legacy_content_run(archive_root)

    record = build_review_corpus_records(archive_root)[0]

    assert record["valid_archive"] is True
    assert record["review_readiness_tier"] == "legacy_content_reviewable"
    assert record["batch_recommendation"] == "recommended_legacy_rehearsal_batch"
    assert record["content_review"] == {
        "available": True,
        "missing_artifacts": [],
        "reason": "core content artifacts are available",
    }
    assert record["custody_review"]["available"] is False
    assert record["custody_review"]["missing_artifacts"] == [
        "agent_result.json",
        "reasoning_trace.json",
        "run_events.json",
        "evaluation.json",
    ]
    assert record["custody_review"]["missing_metadata"] == ["capture_adequacy"]


def test_review_corpus_marks_malformed_entries_invalid_deterministically(
    tmp_path: Path,
) -> None:
    archive_root = tmp_path / "runs"
    bad_run = archive_root / "bad-case" / "bad-run"
    bad_run.mkdir(parents=True)
    (bad_run / "result.json").write_text("{not-json", encoding="utf-8")

    first = build_review_corpus_records(archive_root)
    second = build_review_corpus_records(archive_root)

    assert first == second
    assert len(first) == 1
    assert first[0]["valid_archive"] is False
    assert first[0]["archive_errors"] == [
        "no recognized Lolla run artifacts found",
        "result.json is not valid JSON",
    ]
    assert first[0]["artifacts"]["result.json"]["available"] is True
    assert first[0]["review_readiness_tier"] == "not_reviewable"
    assert first[0]["batch_recommendation"] == "exclude_or_needs_backfill"
    assert first[0]["content_review"]["available"] is False
    assert first[0]["content_review"]["missing_artifacts"] == [
        "conversation.txt",
        "extraction.json",
        "revised.txt",
        "memo.md",
    ]


def test_review_corpus_manifest_and_jsonl_outputs_are_stable(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _seed_run(archive_root, case_id="case-b", run_id="20260625T140000Z_ijkl56")
    _seed_run(
        archive_root,
        case_id="case-a",
        run_id="20260625T130000Z_efgh34",
        include_evaluation=False,
        include_control=False,
    )
    records = build_review_corpus_records(archive_root)
    manifest = build_review_corpus_manifest(archive_root, records)

    assert [record["case_id"] for record in records] == ["case-a", "case-b"]
    assert manifest["schema_version"] == REVIEW_CORPUS_MANIFEST_SCHEMA_VERSION
    assert manifest["record_count"] == 2
    assert manifest["evaluation_overall_counts"] == {
        "pass": 1,
        "unavailable": 1,
    }
    assert manifest["review_readiness_tier_counts"] == {
        "full_modern_reviewable": 1,
        "modern_partial_reviewable": 1,
    }
    assert manifest["batch_recommendation_counts"] == {
        "recommended_modern_review_batch": 2,
    }
    assert manifest["content_review_available_count"] == 2
    assert manifest["custody_review_available_count"] == 1
    assert manifest["scope"] == _expected_scope("review_corpus_manifest")

    jsonl_path = tmp_path / "review_corpus.jsonl"
    manifest_path = tmp_path / "review_corpus.manifest.json"
    write_jsonl(records, jsonl_path)
    write_json(manifest, manifest_path)
    first_jsonl = jsonl_path.read_text(encoding="utf-8")
    first_manifest = manifest_path.read_text(encoding="utf-8")
    write_jsonl(build_review_corpus_records(archive_root), jsonl_path)
    write_json(build_review_corpus_manifest(archive_root, records), manifest_path)

    assert jsonl_path.read_text(encoding="utf-8") == first_jsonl
    assert manifest_path.read_text(encoding="utf-8") == first_manifest
    assert len(first_jsonl.splitlines()) == 2
