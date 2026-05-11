from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.bevelin_lane1_audit import (  # noqa: E402
    build_bevelin_lane1_audit,
    build_collection_report,
)


def _base_result() -> dict:
    return {
        "run_id": "unit-run",
        "revised_answer": "Move forward with the recommendation.",
        "audit_summary": {
            "embedding_swiss_cheese_active": True,
            "triggered_tendencies": ["overoptimism-tendency"],
            "triage_scores": [
                {
                    "tendency_id": "overoptimism-tendency",
                    "score": 4,
                    "evidence": "The assistant accepts a small sample without a denominator.",
                },
            ],
            "deep_check_results": [
                {
                    "tendency_id": "overoptimism-tendency",
                    "tendency_name": "Overoptimism Tendency",
                    "detected": True,
                    "evidence": "The answer lacks a representative sample and denominator.",
                    "sub_pattern": "missing-denominator",
                    "specific_passage": "Three customers asked for it.",
                    "severity": "material",
                    "reason": "No base rate or reference class was requested.",
                },
            ],
            "routing_decisions": [
                {
                    "tendency_id": "overoptimism-tendency",
                    "sub_pattern": "missing-denominator",
                    "selected_model_ids": ["base-rates"],
                    "challenge_statement": "Ask for a denominator and reference class.",
                }
            ],
            "boundary_calls": [
                {
                    "stage": "pass1_cluster_projection",
                    "provider_name": "openrouter",
                    "model": "test-pass1",
                    "status": "ok",
                    "prompt_tokens": 10,
                    "completion_tokens": 4,
                    "total_tokens": 14,
                },
                {
                    "stage": "pass2_overoptimism-tendency",
                    "provider_name": "openrouter",
                    "model": "test-pass2",
                    "status": "ok",
                    "prompt_tokens": 20,
                    "completion_tokens": 8,
                    "total_tokens": 28,
                },
            ],
        },
        "delta_card": {
            "findings": [
                {
                    "tendency_id": "overoptimism-tendency",
                    "selected_model_ids": ["base-rates"],
                    "challenge_statement": "Missing denominator and reference class.",
                    "next_move": "Ask for base rates before committing.",
                }
            ]
        },
        "v60_enrichment": {
            "status": "active",
            "candidate_pool": {"embedding_mode": "off"},
            "telemetry": {"selected_chunk_count": 0, "selected_model_ids": []},
        },
        "v60_consideration_ledger": {"transactions": []},
    }


def _probe(audit: dict, probe_id: str) -> dict:
    for row in audit["probe_results"]:
        if row["probe_id"] == probe_id:
            return row
    raise AssertionError(f"missing probe {probe_id}")


def test_lane1_finding_without_public_conversion_is_pressure_only() -> None:
    audit = build_bevelin_lane1_audit(_base_result())

    representative = _probe(audit, "representative_evidence")

    assert representative["status"] == "lane1_pressure_only"
    assert "overoptimism-tendency" in representative["lane1"]["tendency_hits"]["detected_or_routed"]
    assert audit["win_signals"]["lane1_unconverted_probe_count"] >= 1
    assert audit["lane1"]["findings_present"] is True


def test_silent_lane1_supported_by_public_and_v60_pressure() -> None:
    result = _base_result()
    result["revised_answer"] = (
        "Compare the fallback option and opportunity cost before deciding. "
        "Set a stop rule if the test is wrong."
    )
    result["audit_summary"]["deep_check_results"][0]["detected"] = False
    result["audit_summary"]["routing_decisions"] = []
    result["delta_card"]["findings"] = []
    result["v60_enrichment"]["telemetry"] = {
        "selected_chunk_count": 2,
        "selected_model_ids": ["opportunity-cost", "optionality"],
        "selected_chunk_effect_types": {"missing_option": 1, "executable_test": 1},
    }
    result["v60_consideration_ledger"] = {
        "transactions": [
            {
                "model_id": "opportunity-cost",
                "chunk_id": "aff::opportunity-cost.visible-next-best-alternative",
                "disposition": "used",
                "route": "updated_position",
                "visible_effect": "Added a comparison to the fallback option.",
                "why": "The answer needed the next best alternative.",
            }
        ]
    }

    audit = build_bevelin_lane1_audit(result)

    alternatives = _probe(audit, "alternatives_opportunity_cost")
    assert alternatives["status"] == "publicly_treated"
    assert "opportunity cost" in alternatives["public"]["matched_terms"]
    assert audit["lane1"]["findings_present"] is False
    assert audit["win_signals"]["silent_lane1_supported_by_other_lanes_probe_count"] >= 1


def test_runtime_map_separates_llm_embeddings_and_deterministic_outputs() -> None:
    audit = build_bevelin_lane1_audit(_base_result())
    runtime = audit["runtime_map"]

    assert runtime["llm"]["boundary_call_count"] == 2
    assert runtime["llm"]["stage_counts"] == {"pass1": 1, "pass2": 1}
    assert runtime["llm"]["token_usage"]["total_tokens"] == 42
    assert runtime["embeddings"]["lane1_swiss_cheese_active"] is True
    assert runtime["embeddings"]["v60_embedding_mode"] == "off"
    assert runtime["deterministic"]["routing_decision_count"] == 1
    assert runtime["deterministic"]["delta_finding_count"] == 1


def test_collection_report_aggregates_probe_statuses() -> None:
    first = build_bevelin_lane1_audit(_base_result())
    second = build_bevelin_lane1_audit(_base_result())

    collection = build_collection_report([first, second])

    assert collection["schema_version"] == "bevelin_lane1_audit_collection.v1"
    assert collection["audit_count"] == 2
    assert collection["aggregate_win_signals"]["lane1_unconverted_probe_count"] >= 2


def test_bevelin_lane1_audit_cli_emits_json(tmp_path: Path) -> None:
    run_dir = tmp_path / "case" / "run"
    run_dir.mkdir(parents=True)
    result_path = run_dir / "result.json"
    result_path.write_text(json.dumps(_base_result()), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "run_bevelin_lane1_audit.py"),
            "--result",
            str(result_path),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["schema_version"] == "bevelin_lane1_audit.v1"
    assert payload["runtime_map"]["llm"]["boundary_call_count"] == 2
    assert payload["source"]["run_dir"] == str(run_dir)
