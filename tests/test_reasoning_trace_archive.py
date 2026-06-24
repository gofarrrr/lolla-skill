from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

from engine.system_b.graph_survival_report import write_graph_survival_artifacts
from engine.system_b.reasoning_trace import build_reasoning_trace


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
    (tmp_dir / f"lolla_{run_id}_user_usefulness_review.json").write_text(
        json.dumps(
            {
                "schema_version": "lolla.user_usefulness_review.v0.1",
                "status": "collected",
                "rating": 4,
                "helped_change_view": True,
                "would_reuse": True,
                "most_useful_component": "evidence gate",
                "least_useful_component": "memo",
                "reviewed_at": "2026-06-23T09:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_outcome_review.json").write_text(
        json.dumps(
            {
                "schema_version": "lolla.outcome_review.v0.1",
                "review_id": "outcome-001",
                "status": "collected",
                "reviewed_at": "2026-07-23T09:00:00Z",
                "outcome_status": "pending",
                "decision_taken": "waited for customer evidence",
                "surprise_count": 1,
                "suppressed_lens_relevance": "unknown",
                "usefulness_rating": 4,
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_run_events.json").write_text(
        json.dumps(
            {
                "schema_version": "lolla.run_events.v0.1",
                "run_id": run_id,
                "events": [
                    {
                        "event_id": "event_001",
                        "event_type": "recovery_pinned_run_id",
                        "occurred_at": "2026-06-23T09:05:00Z",
                        "actor": "operator",
                        "details": {"reason": "latest pointer moved"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (tmp_dir / f"lolla_{run_id}_operator.log").write_text(
        "[2026-06-23T09:05:00Z] synthetic operator note\n",
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

    assert set(archived["files_generated"]) == {
        "agent_result.json",
        "graph_survival_report.json",
        "graph_survival_report.md",
        "reasoning_trace.json",
    }
    assert archived["trace_path"] == str(trace_path)
    assert trace["schema_version"] == "lolla.reasoning_trace.v0.2"
    assert trace["trace_id"] == f"trace_{run_id}"
    assert trace["source"]["adapter"] == "lolla_skill"
    assert trace["source"]["capture_hook"] == "archive_run"
    assert trace["privacy"]["mode"] == "local_only"
    assert trace["privacy"]["raw_transcript_saved"] is True
    assert trace["privacy"]["raw_text_duplicated_in_trace"] is False
    assert trace["privacy"]["selected_commitment_snippets_saved"] is True
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
    assert trace["process"]["private_custody"]["graph_survival_report_file_present"] is True
    assert trace["process"]["graph_survival"]["status"] == "ready"
    assert trace["process"]["graph_survival"]["artifact_path"] == "graph_survival_report.json"
    assert trace["process"]["run_events"]["status"] == "recorded"
    assert trace["process"]["run_events"]["event_count"] == 1
    assert trace["process"]["run_events"]["events"][0]["event_type"] == "recovery_pinned_run_id"
    assert artifact_by_path["conversation.txt"]["role"] == "source_conversation"
    assert artifact_by_path["operator.log"]["role"] == "operator_log"
    assert artifact_by_path["run_events.json"]["role"] == "run_event_ledger"
    assert artifact_by_path["user_usefulness_review.json"]["role"] == "user_usefulness_review"
    assert artifact_by_path["outcome_review.json"]["role"] == "outcome_review"
    assert artifact_by_path["agent_result.json"]["role"] == "agent_facing_result"
    assert artifact_by_path["graph_survival_report.json"]["role"] == "graph_survival_report"
    assert artifact_by_path["graph_survival_report.md"]["role"] == "graph_survival_report_markdown"
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
    commitments = trace["candidate_commitments"]
    assert len(commitments) == 1
    assert commitments[0]["candidate_id"] == f"commitment_{run_id}_001"
    assert commitments[0]["kind"] == "gate"
    assert commitments[0]["source_surface"] == "conversation"
    assert commitments[0]["source_ref"] == "conversation.txt#turn1.assistant.span1"
    assert commitments[0]["source_actor"] == "assistant"
    assert commitments[0]["actor_type"] == "ai_assistant"
    assert commitments[0]["commitment_source"] == "ai_recommendation"
    assert commitments[0]["claim"] == "Only pivot after a customer evidence gate."
    assert commitments[0]["actionability"] == "high"
    assert commitments[0]["impact"] == "medium"
    assert commitments[0]["reversibility"] == "bounded_reversible"
    assert commitments[0]["evidence_status"] == "evidence_attached_or_requested"
    assert commitments[0]["correction_status"] == "observed_uncorrected_or_carried_forward"
    assert commitments[0]["classification"]["kind"] == "gate"
    assert commitments[0]["semantic_flags"] == ["evidence_gate"]
    assert commitments[0]["audit_effect"] == "observed"
    assert commitments[0]["escalation_recommended"] is True
    assert commitments[0]["decision_packet_ready"] is False
    assert trace["decision_packets"] == []
    assert trace["user_usefulness_review"]["status"] == "collected"
    assert trace["user_usefulness_review"]["rating"] == 4
    assert trace["outcome_review_state"]["status"] == "available"
    assert trace["outcome_review_state"]["review_count"] == 1
    assert trace["outcome_reviews"][0]["review_id"] == "outcome-001"
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
    assert trace["trace_adequacy"]["commitment_detection"] == {
        "status": "heuristic_v0",
        "candidate_count": 1,
        "escalation_recommended_count": 1,
    }
    assert trace["trace_adequacy"]["outcome_review"] == {
        "status": "available",
        "review_count": 1,
    }
    assert trace["surface_divergence"]["status"] == "not_checkable"
    assert len(trace["model_calls"]) == 2
    assert trace["model_calls"][0] == {
        "index": 0,
        "record_type": "boundary_call",
        "call_count": 1,
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
    assert trace["model_calls"][1]["record_type"] == "vendor_usage_summary"
    assert trace["model_calls"][1]["provider_name"] == "openrouter"
    assert trace["model_calls"][1]["call_count"] == 2
    assert trace["tool_calls"] == []
    assert "secret launch phrase 7621" not in trace_path.read_text(encoding="utf-8")
    agent_result = json.loads((run_dir / "agent_result.json").read_text(encoding="utf-8"))
    assert agent_result["schema_version"] == "lolla_agent_result.v1"
    assert agent_result["caller_action"] == "do_not_use_run_degraded"
    assert (tmp_dir / f"lolla_{run_id}_agent_result.json").exists()


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


def test_reasoning_trace_marks_spouse_gate_as_corrected_when_revised_answer_says_not_sufficient(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "conversation.txt").write_text(
        "\n\n".join(
            [
                "CONVERSATION: 1 turn, 0 user messages, 1 assistant response",
                "[Turn 1] ASSISTANT:\nIf the wife conversation goes well, take B.",
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / "extraction.json").write_text(
        json.dumps(
            {
                "extraction": {
                    "decision_situation": "Career decision",
                    "turns": [
                        {
                            "turn_index": 1,
                            "speaker": "assistant",
                            "text": "If the wife conversation goes well, take B.",
                        }
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "result.json").write_text(
        json.dumps({"run_health": {"overall": "healthy", "issues": []}}),
        encoding="utf-8",
    )
    (run_dir / "revised.txt").write_text(
        (
            "I would take back the clean ending. "
            "A real yes from his wife is necessary, but not sufficient."
        ),
        encoding="utf-8",
    )

    trace = build_reasoning_trace(
        run_dir,
        run_id="spousegate",
        case_id="career-decision",
        fingerprint="career decision",
        how_matched="new_case",
        files_copied=["conversation.txt", "extraction.json", "result.json", "revised.txt"],
        files_missing=[],
        manifest={"run_count": 1},
        created_at="2026-06-23T09:00:00Z",
    )

    commitments = trace["candidate_commitments"]
    assert len(commitments) == 1
    assert commitments[0]["audit_effect"] == "corrected"
    assert commitments[0]["correction_status"] == "corrected"
    assert "one gate" in commitments[0]["corrected_to"].lower()


def test_reasoning_trace_surfaces_budget_suppressed_lenses_top_level(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "conversation.txt").write_text(
        "\n\n".join(
            [
                "CONVERSATION: 1 turn, 1 user message, 1 assistant response",
                "[Turn 1] USER:\nShould I take the startup role?",
                "[Turn 1] ASSISTANT:\nTreat it as a bounded wager.",
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / "extraction.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "capture_health": "good",
                "extraction": {
                    "decision_situation": "Career decision",
                    "turns": [
                        {
                            "turn_index": 1,
                            "speaker": "user",
                            "text": "Should I take the startup role?",
                        },
                        {
                            "turn_index": 1,
                            "speaker": "assistant",
                            "text": "Treat it as a bounded wager.",
                        },
                    ],
                    "live_constraints": [],
                    "reasoning_passages": ["Treat it as a bounded wager."],
                    "dropped_threads": [],
                },
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "result.json").write_text(
        json.dumps(
            {
                "run_health": {"overall": "healthy", "issues": [], "issue_details": []},
                "v60_enrichment": {
                    "status": "active",
                    "candidate_pool": {
                        "embedding_mode": "on",
                        "lane_candidate_count": 1,
                        "raw_lane_signal_count": 1,
                        "embedding_model_hits": [
                            {"model_id": "risk-vs-uncertainty", "score": 0.84}
                        ],
                    },
                    "selected_cards": [],
                    "telemetry": {
                        "selected_chunk_count": 0,
                        "skipped_candidates": [
                            {
                                "model_id": "risk-vs-uncertainty",
                                "source": "embedding_fill",
                                "reason": "not_presented_packet_cap",
                                "stage": "fill",
                                "score": 0.84,
                            }
                        ],
                        "not_presented_candidate_count": 1,
                    },
                },
                "audit_summary": {"warnings": [], "boundary_calls": []},
                "usage_summary": {"vendors": {}},
            }
        ),
        encoding="utf-8",
    )
    write_graph_survival_artifacts(run_dir)

    trace = build_reasoning_trace(
        run_dir,
        run_id="budgettrace",
        case_id="career-decision",
        fingerprint="career decision",
        how_matched="new_case",
        files_copied=[
            "conversation.txt",
            "extraction.json",
            "result.json",
            "graph_survival_report.json",
            "graph_survival_report.md",
        ],
        files_missing=[],
        manifest={"run_count": 1},
        created_at="2026-06-23T09:00:00Z",
    )

    expected = [
        {
            "model_id": "risk-vs-uncertainty",
            "reason": "not_presented_packet_cap",
            "source": "embedding_fill",
            "stage": "fill",
            "score": 0.84,
            "research_status": "plausible_budget_suppressed",
            "unknown_noise_status": True,
        }
    ]
    assert trace["budget_suppressed_lenses"] == expected
    assert trace["top_budget_suppressed_lenses"] == expected
    assert trace["process"]["graph_survival"]["top_budget_suppressed_lenses"] == expected


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
