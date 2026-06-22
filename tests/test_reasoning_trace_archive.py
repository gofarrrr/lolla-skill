from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_RUN_PATH = REPO_ROOT / "scripts" / "archive_run.py"


def _load_archive_run_module():
    spec = importlib.util.spec_from_file_location("archive_run", ARCHIVE_RUN_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha256_uri(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def test_archive_run_writes_reasoning_trace_manifest_with_hashes(tmp_path: Path) -> None:
    run_id = "tracefull"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()

    conversation_text = (
        "CONVERSATION: 1 turn, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\n"
        "Should we pivot? secret launch phrase 7621.\n\n"
        "[Turn 1] ASSISTANT:\n"
        "Only pivot after a customer evidence gate.\n"
    )
    (tmp_dir / f"lolla_{run_id}_conversation.txt").write_text(
        conversation_text,
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "capture_health": "good",
                "capture_manifest": {"declared_turns": 1, "actual_user_turns": 1},
                "extraction": {
                    "decision_situation": "Founder deciding whether to pivot",
                    "live_constraints": [
                        {"constraint": "Budget is capped.", "status": "active"}
                    ],
                    "reasoning_passages": ["Only pivot after a customer evidence gate."],
                    "original_framing": "Should we pivot?",
                    "synthesized_position": "Pivot only after evidence.",
                    "dropped_threads": [],
                    "turns": [
                        {"turn_index": 1, "speaker": "user", "text": "Should we pivot?"},
                        {
                            "turn_index": 1,
                            "speaker": "assistant",
                            "text": "Only pivot after a customer evidence gate.",
                        },
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_result.json").write_text(
        json.dumps(
            {
                "run_health": {
                    "overall": "healthy",
                    "capture": "good",
                    "issues": [],
                    "issue_details": [],
                },
                "v60_enrichment": {"status": "disabled"},
                "companion_cheat_sheet": {
                    "anchors": [
                        {
                            "model_id": "opportunity-cost",
                            "display_name": "Opportunity Cost",
                            "presence_mode": "executed",
                            "evidence_quote": "Only pivot after a customer evidence gate.",
                            "chunks": [{"chunk_id": "opp-1", "chunk_type": "failure_mode"}],
                        }
                    ],
                    "anti_echo_model_ids": [],
                },
                "audit_summary": {
                    "triggered_tendencies": ["inconsistency-avoidance"],
                    "deep_check_results": [
                        {"tendency_id": "inconsistency-avoidance", "detected": True},
                        {"tendency_id": "authority-misinfluence", "detected": False},
                    ],
                    "routing_decisions": [{"tendency_id": "inconsistency-avoidance"}],
                    "boundary_call_count": 3,
                    "boundary_calls": [
                        {
                            "stage": "lane2.companion",
                            "tendency_id": "",
                            "provider_name": "openrouter",
                            "requested_model": "anthropic/claude-opus-4.7",
                            "served_model": "anthropic/claude-opus-4.7",
                            "model": "anthropic/claude-opus-4.7",
                            "model_attribution_status": "matched",
                            "status": "ok",
                            "finish_reason": "stop",
                            "raw_message_content": "{\"anchors\": []}",
                            "temperature": 0.2,
                            "prompt_tokens": 100,
                            "completion_tokens": 20,
                            "total_tokens": 120,
                            "cached_tokens": 10,
                            "cache_write_tokens": 0,
                            "reasoning_tokens": 0,
                            "reasoning_disabled": True,
                            "reasoning_details_present": False,
                        }
                    ],
                    "warnings": ["test warning"],
                    "companion_verification_accepted_before_cap": [
                        {"model_id": "opportunity-cost", "presence_mode": "executed"}
                    ],
                    "companion_rejected_models": [
                        {
                            "model_id": "premortem",
                            "rejection_reason": "not actually used",
                        }
                    ],
                    "route_trace": {
                        "schema_version": "route_trace.v1",
                        "lanes": {
                            "lane1": {
                                "routes": [
                                    {
                                        "primary_model_id": "inversion",
                                        "selected_model_ids": ["inversion"],
                                        "supporting_model_ids": [],
                                        "risk_model_ids": [],
                                        "rejected_candidates": [],
                                    }
                                ]
                            },
                            "lane2": {
                                "selected_model_ids": ["opportunity-cost"],
                                "rejected_candidates": [
                                    {
                                        "model_id": "premortem",
                                        "rejection_reason": "not actually used",
                                    }
                                ],
                            },
                            "lane3": {"routes": []},
                            "lane4": {"routes": []},
                        },
                        "anti_echo": {"exclusions": []},
                        "summary": {
                            "lane1_route_count": 1,
                            "lane2_rejected_candidate_count": 1,
                        },
                    },
                },
                "gap_check": {
                    "schema_version": "lolla_gap_check.v2",
                    "status": "not_run_default_off",
                    "reason": "post_step6_pressure_check_default_off",
                    "lanes": [],
                },
                "has_gap_check": True,
                "pressure_check_mode": "default_off",
                "gap_check_summary": "No additional pressure check was run.",
                "usage_summary": {
                    "run_id": run_id,
                    "pricing_table_version": "2026-05-25",
                    "estimated_total_cost_usd": 0.123,
                    "cost_estimate_state": "complete",
                    "vendors": {
                        "openrouter": {"calls": 3},
                        "openai_embeddings": {"calls": 0},
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    archive_run = _load_archive_run_module()
    archived = archive_run.archive_run(
        run_id,
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    run_dir = Path(archived["run_dir"])
    trace_path = run_dir / "reasoning_trace.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    artifact_by_path = {item["path"]: item for item in trace["artifacts"]}

    assert archived["files_generated"] == ["reasoning_trace.json"]
    assert archived["trace_path"] == str(trace_path)
    assert trace["schema_version"] == "lolla.reasoning_trace.v0.2"
    assert trace["trace_id"] == f"trace_{run_id}"
    assert trace["source"]["adapter"] == "lolla_skill"
    assert trace["source"]["capture_hook"] == "archive_run"
    assert trace["privacy"]["mode"] == "local_only"
    assert trace["privacy"]["raw_transcript_saved"] is True
    assert trace["privacy"]["raw_text_duplicated_in_trace"] is False
    assert trace["privacy"]["external_egress_by_trace_builder"] is False
    assert trace["case"]["case_id"] == archived["case_id"]
    assert trace["case"]["run_id"] == run_id
    assert trace["case"]["fingerprint"] == archived["fingerprint"]
    assert trace["case"]["how_matched"] == "new_case"
    assert trace["case"]["decision_situation"] == "Founder deciding whether to pivot"
    assert trace["participants"] == ["user", "assistant"]
    assert trace["capture"]["capture_health"] == "good"
    assert trace["capture"]["decision_structure"]["live_constraint_count"] == 1
    assert trace["capture"]["decision_structure"]["reasoning_passage_count"] == 1
    assert trace["process"]["audit_summary"]["triggered_tendency_count"] == 1
    assert trace["process"]["audit_summary"]["triggered_tendency_ids"] == [
        "inconsistency-avoidance"
    ]
    assert trace["process"]["audit_summary"]["detected_tendency_count"] == 1
    assert trace["process"]["audit_summary"]["detected_tendency_ids"] == [
        "inconsistency-avoidance"
    ]
    assert trace["process"]["pressure_check"]["status"] == "not_run_default_off"
    assert trace["process"]["usage"]["estimated_total_cost_usd"] == 0.123
    assert trace["process"]["usage"]["vendor_calls"]["openrouter"] == 3
    assert artifact_by_path["conversation.txt"]["role"] == "source_conversation"
    assert artifact_by_path["conversation.txt"]["sha256"] == _sha256_uri(
        run_dir / "conversation.txt"
    )
    assert artifact_by_path["conversation.txt"]["bytes"] == (
        run_dir / "conversation.txt"
    ).stat().st_size
    assert artifact_by_path["result.json"]["sha256"] == _sha256_uri(run_dir / "result.json")
    assert trace["content_hashes"]["conversation_sha256"] == _sha256_uri(
        run_dir / "conversation.txt"
    )
    assert trace["content_hashes"]["result_sha256"] == _sha256_uri(run_dir / "result.json")
    assert trace["content_hashes"]["artifact_index_sha256"].startswith("sha256:")
    assert trace["candidate_commitments"] == []
    assert trace["decision_packets"] == []
    assert trace["outcome_reviews"] == []
    lens_by_id = {item["lens_id"]: item for item in trace["reasoning_lenses"]}
    assert lens_by_id["opportunity-cost"]["selected"] is True
    assert lens_by_id["opportunity-cost"]["surfaced"] is True
    assert lens_by_id["opportunity-cost"]["roles"] == [
        "companion_anchor",
        "companion_verified",
    ]
    assert lens_by_id["opportunity-cost"]["evidence"]["display_name"] == "Opportunity Cost"
    assert lens_by_id["opportunity-cost"]["evidence"]["chunk_count"] == 1
    assert lens_by_id["opportunity-cost"]["evidence"]["has_evidence_quote"] is True
    assert lens_by_id["premortem"]["disposition"] == "rejected"
    assert lens_by_id["premortem"]["rejection_reasons"] == ["not actually used"]
    assert trace["trace_adequacy"]["status"] == "sufficient"
    assert trace["trace_adequacy"]["future_review_ready"] is True
    assert trace["model_calls"] == [
        {
            "index": 0,
            "stage": "lane2.companion",
            "tendency_id": "",
            "provider_name": "openrouter",
            "requested_model": "anthropic/claude-opus-4.7",
            "served_model": "anthropic/claude-opus-4.7",
            "model": "anthropic/claude-opus-4.7",
            "model_attribution_status": "matched",
            "status": "ok",
            "finish_reason": "stop",
            "temperature": 0.2,
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
            "cached_tokens": 10,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "reasoning_disabled": True,
            "reasoning_details_present": False,
            "raw_message_content_present": True,
        }
    ]
    assert trace["tool_calls"] == []
    assert "secret launch phrase 7621" not in trace_path.read_text(encoding="utf-8")


def test_archive_run_reasoning_trace_records_missing_artifacts(tmp_path: Path) -> None:
    run_id = "traceminimal"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()
    (tmp_dir / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps(
            {
                "extraction": {
                    "decision_situation": "Founder deciding whether to pivot",
                }
            }
        ),
        encoding="utf-8",
    )

    archive_run = _load_archive_run_module()
    archived = archive_run.archive_run(
        run_id,
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    trace = json.loads(Path(archived["trace_path"]).read_text(encoding="utf-8"))
    missing_by_path = {item["path"]: item for item in trace["missing_artifacts"]}

    assert "extraction.json" in archived["files_copied"]
    assert "result.json" in archived["files_missing"]
    assert trace["content_hashes"]["conversation_sha256"] is None
    assert trace["content_hashes"]["result_sha256"] is None
    assert trace["privacy"]["raw_transcript_saved"] is False
    assert missing_by_path["conversation.txt"]["role"] == "source_conversation"
    assert missing_by_path["result.json"]["role"] == "pipeline_result"
    assert trace["process"]["run_health"] == {}
    assert trace["process"]["usage"]["vendor_calls"] == {}
    assert trace["trace_adequacy"]["status"] == "insufficient"
    assert trace["trace_adequacy"]["future_review_ready"] is False


def test_reasoning_trace_reflects_archive_time_degraded_health(tmp_path: Path) -> None:
    run_id = "tracev60degraded"
    tmp_dir = tmp_path / "tmp"
    archive_root = tmp_path / "archive"
    tmp_dir.mkdir()

    (tmp_dir / f"lolla_{run_id}_extraction.json").write_text(
        json.dumps(
            {
                "extraction": {
                    "decision_situation": "Founder deciding whether to pivot",
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_result.json").write_text(
        json.dumps(
            {
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {
                    "status": "active",
                    "telemetry": {
                        "selected_chunk_ids": [
                            "aff::optionality.expand-before-evaluating",
                        ]
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    archive_run = _load_archive_run_module()
    archived = archive_run.archive_run(
        run_id,
        archive_root=archive_root,
        tmp_dir=tmp_dir,
    )

    trace = json.loads(Path(archived["trace_path"]).read_text(encoding="utf-8"))

    assert trace["process"]["run_health"]["overall"] == "degraded"
    assert (
        trace["process"]["private_custody"]["v60_consideration_ledger_status"]
        == "missing"
    )
    assert "v60_consideration_ledger_missing" in trace["process"]["run_health"]["issues"]
