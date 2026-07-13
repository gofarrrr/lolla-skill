from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.evals.build_end_to_end_evidence_bridge import build_bridge


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _archive(tmp_path: Path) -> Path:
    archive = tmp_path / "run"
    archive.mkdir()
    for name in (
        "conversation.txt",
        "revised.txt",
        "memo.md",
    ):
        (archive / name).write_text(f"private {name}", encoding="utf-8")
    _write(archive / "extraction.json", {})
    _write(archive / "result.json", {})
    _write(
        archive / "agent_result.json",
        {
            "case_id": "source-case",
            "run_id": "run-1",
            "status": "ok",
            "run_health_overall": "healthy",
            "product_output_health": "clean",
            "live_output_health": "not_checked",
            "caller_action": "use_revised_answer",
            "risk_mode": "standard",
            "capture_adequacy": {
                "status": "good",
                "declared_turn_count": 2,
                "captured_turn_count": 2,
                "omitted_turn_count": 0,
            },
            "usage": {
                "estimated_total_cost_usd": 0.02,
                "cost_estimate_state": "complete",
            },
        },
    )
    _write(archive / "evaluation.json", {"summary": {"pass": 2, "warn": 1}})
    _write(
        archive / "extraction_adequacy_report.json",
        {
            "provenance_gap_findings": {
                "quote_fabrication_count": 0,
                "fields_with_no_source_grounding": ["synthesized_position"],
                "fields_only_turn_ref_grounded": ["live_constraints"],
            }
        },
    )
    _write(
        archive / "graph_survival_report.json",
        {
            "summary": {
                "raw_lane_signal_count": 10,
                "lane_candidate_count": 5,
                "selected_card_count": 2,
                "selected_chunk_count": 4,
                "selected_model_ids": ["falsifiability"],
                "suppressed_signal_count": 8,
                "budget_suppressed_signal_count": 7,
                "unadjudicated_candidate_count": 0,
                "private_table_item_count": 2,
                "private_table_disposition_counts": {"used": 1},
                "v60_transaction_count": 4,
                "v60_disposition_counts": {"used": 2, "rejected": 2},
            }
        },
    )
    _write(
        archive / "reasoning_trace.json",
        {
            "process": {
                "usage": {
                    "vendor_calls": {"openrouter": 3, "openai_embeddings": 1},
                    "total_vendor_call_count": 4,
                }
            },
            "trace_adequacy": {
                "status": "thin",
                "future_review_ready": False,
                "error_analysis_ready": True,
                "coverage": {"source_conversation": "present"},
                "missing_context": ["live_output_health is not_checked"],
            },
            "user_usefulness_review": {"status": "not_collected"},
            "outcome_review_state": {"status": "not_started"},
        },
    )
    return archive


def test_bridge_emits_safe_capability_vector_without_private_text(tmp_path: Path) -> None:
    archive = _archive(tmp_path)
    semantic = tmp_path / "semantic.json"
    _write(
        semantic,
        {
            "contract_status": "prospective_scaffold_not_ready_for_promotion",
            "per_case": [
                {
                    "case_id": "semantic-case",
                    "runs": [
                        {
                            "evidence_matches": {"obs-a": [], "obs-b": []},
                            "concept_anywhere_observation_ids": ["obs-a"],
                            "concept_acceptable_role_observation_ids": ["obs-a"],
                            "first_introduction_observation_ids": ["obs-a"],
                            "audit_complete_observation_ids": ["obs-a"],
                        },
                        {
                            "evidence_matches": {"obs-a": [], "obs-b": []},
                            "concept_anywhere_observation_ids": ["obs-a", "obs-b"],
                            "concept_acceptable_role_observation_ids": ["obs-a"],
                            "first_introduction_observation_ids": ["obs-a"],
                            "audit_complete_observation_ids": ["obs-a"],
                        },
                    ],
                }
            ],
        },
    )
    review = tmp_path / "review.json"
    _write(
        review,
        {
            "cases": [
                {
                    "case_id": "review-case",
                    "run_id": "old-run",
                    "human_review": {
                        "review_status": "pass",
                        "useful_friction": "present",
                        "noisy_friction": "absent",
                        "missing_friction": "absent",
                        "revised_answer_improved": "yes",
                        "safe_for_agent_use": "with_human_review",
                    },
                    "action_changing_delta": "A gate changed.",
                    "artifact_sufficiency": "sufficient",
                }
            ]
        },
    )

    payload = build_bridge(
        archive=archive,
        semantic_result_path=semantic,
        semantic_case_id="semantic-case",
        human_review_path=review,
        human_review_case_id="review-case",
        review_relation="analogous_case_not_exact_run",
    )

    assert payload["schema_version"] == "lolla.end_to_end_evidence_bridge.v0"
    assert payload["raw_private_content_included"] is False
    assert payload["local_absolute_paths_included"] is False
    assert payload["archive_mutated"] is False
    assert payload["builder_model_calls"] == 0
    metric = payload["capabilities"]["c1_c3_semantic_and_temporal"][
        "reasoning_concept_anywhere"
    ]
    assert metric["weighted_recall"] == pytest.approx(0.75)
    assert metric["stable_observation_count"] == 1
    assert payload["capabilities"]["c6_reconsideration_utility"][
        "evidence_relation"
    ] == "analogous_case_not_exact_run"
    rendered = json.dumps(payload)
    assert "private conversation.txt" not in rendered
    assert str(tmp_path) not in rendered


def test_bridge_fails_closed_when_required_archive_artifact_is_missing(
    tmp_path: Path,
) -> None:
    archive = _archive(tmp_path)
    (archive / "memo.md").unlink()
    with pytest.raises(ValueError, match="archive missing required files"):
        build_bridge(
            archive=archive,
            semantic_result_path=tmp_path / "missing-semantic.json",
            semantic_case_id="semantic-case",
            human_review_path=tmp_path / "missing-review.json",
            human_review_case_id="review-case",
            review_relation="exact_run",
        )
