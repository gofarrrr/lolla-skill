from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals.seal_reasoning_portfolio_pipeline_result import (
    seal_pipeline_result,
)
from engine.system_b.stage_a_execution_contract import (
    validate_stage_a_execution_gates,
)


def _write(path: Path, value: object) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path, *, calls: int = 8) -> tuple[Path, Path]:
    paths = {}
    for name in ("source", "extraction", "pipeline", "v60", "affordances", "control"):
        path = tmp_path / f"{name}.json"
        paths[name] = (path, _write(path, {"name": name}))
    contract = {
        "case": {
            "case_id": "case-x",
            "source_path": paths["source"][0].name,
            "source_sha256": paths["source"][1],
        },
        "frozen_extraction": {
            "path": paths["extraction"][0].name,
            "sha256": paths["extraction"][1],
        },
        "pipeline": {
            "script_path": paths["pipeline"][0].name,
            "script_sha256": paths["pipeline"][1],
            "v60_contract_path": paths["v60"][0].name,
            "v60_contract_sha256": paths["v60"][1],
            "affordances_path": paths["affordances"][0].name,
            "affordances_sha256": paths["affordances"][1],
        },
        "existing_control_reuse": {
            "artifact_path": paths["control"][0].name,
            "artifact_sha256": paths["control"][1],
        },
        "call_budget": {
            "recorded_pipeline_and_postprocessing_chat_call_ceiling": 10,
            "estimated_cost_ceiling_usd": 0.2,
        },
    }
    contract_path = tmp_path / "contract.json"
    _write(contract_path, contract)
    result = {
        "status": "ok",
        "run_health": {
            "overall": "healthy",
            "capture_truncated": False,
            "quote_fabrication_count": 0,
        },
        "usage_summary": {
            "estimated_total_cost_usd": 0.05,
            "vendors": {"openrouter": {"calls": calls}},
            "cost_estimate_coverage": {"calls_with_known_price": calls + 2},
        },
        "pre_step6_private_table": {
            "schema_version": "table.v1",
            "status": "ready",
            "runtime_policy": "private",
            "promotion_effect": "none",
            "compiled_card_deck_key": "key",
            "key_material": {},
            "cache": {"state": "cache_miss", "cache_dir": "/private/path"},
            "table_char_count": 1000,
            "table_section_count": 1,
            "source_items": [{"source_id": "one"}],
            "consideration_ledger_skeleton": {"items": []},
            "sidecars": {"markdown": "/tmp/private.md"},
        },
        "v60_enrichment": {
            "schema_version": "v60.v1",
            "status": "active",
            "selected_cards": [
                {
                    "card_id": "card-1",
                    "model_id": "model-1",
                    "selection_source": "lane",
                    "selection_reason": "reason",
                    "source_file": "/private/source.md",
                    "selected_affordance_cards": [{"chunk_id": "aff-1"}],
                    "selected_absence_records": [{"chunk_id": "abs-1"}],
                }
            ],
            "consideration_ledger_skeleton": {
                "schema_version": "v60_skill_consideration_ledger.v2",
                "transactions": [{"chunk_id": "aff-1"}],
            },
        },
    }
    result_path = tmp_path / "result.json"
    _write(result_path, result)
    return contract_path, result_path


def test_sealer_passes_in_budget_result_and_strips_paths(tmp_path: Path) -> None:
    contract, result = _fixture(tmp_path)
    gate, table, v60 = seal_pipeline_result(
        contract_path=contract,
        pipeline_result_path=result,
        repo_root=tmp_path,
    )
    assert gate["status"] == "passed"
    assert gate["consumer_call_authorized"] is False
    assert gate["consumer_call_authorization_reason"] == (
        "separate_semantic_novelty_review_required"
    )
    assert table["absolute_paths_included"] is False
    assert "sidecars" not in table
    assert "cache" not in table
    assert v60["selected_cards"][0]["affordance_chunk_ids"] == ["aff-1"]
    assert "source_file" not in v60["selected_cards"][0]


def test_sealer_blocks_over_call_ceiling_without_moving_goalpost(
    tmp_path: Path,
) -> None:
    contract, result = _fixture(tmp_path, calls=11)
    gate, _, _ = seal_pipeline_result(
        contract_path=contract,
        pipeline_result_path=result,
        repo_root=tmp_path,
    )
    assert gate["status"] == "failed"
    assert gate["failed_gates"] == ["openrouter_call_ceiling_met"]
    assert gate["consumer_call_authorization_reason"] == "pipeline_admission_failed"


def test_sealer_supports_fresh_extraction_and_stage_budgets(tmp_path: Path) -> None:
    paths = {}
    for name in (
        "source",
        "rejected",
        "extract_script",
        "pipeline",
        "bullshit_index",
        "v60",
        "affordances",
    ):
        path = tmp_path / f"{name}.json"
        paths[name] = (path, _write(path, {"name": name}))
    contract = {
        "case": {
            "case_id": "case-holdout",
            "source_path": paths["source"][0].name,
            "source_sha256": paths["source"][1],
        },
        "rejected_historical_extraction": {
            "path": paths["rejected"][0].name,
            "sha256": paths["rejected"][1],
        },
        "fresh_extraction": {
            "script_path": paths["extract_script"][0].name,
            "script_sha256": paths["extract_script"][1],
            "required_status": "ok",
            "required_capture_health": "good",
            "required_fabricated_quote_count": 0,
            "required_captured_turn_count": 44,
        },
        "pipeline": {
            "script_path": paths["pipeline"][0].name,
            "script_sha256": paths["pipeline"][1],
            "bullshit_index_path": paths["bullshit_index"][0].name,
            "bullshit_index_sha256": paths["bullshit_index"][1],
            "v60_contract_path": paths["v60"][0].name,
            "v60_contract_sha256": paths["v60"][1],
            "affordances_path": paths["affordances"][0].name,
            "affordances_sha256": paths["affordances"][1],
        },
        "pipeline_call_budget": {
            "extraction_openrouter_call_ceiling": 2,
            "core_pressure_openrouter_call_ceiling": 22,
            "bullshit_index_openrouter_call_ceiling": 12,
            "total_openrouter_call_ceiling": 36,
            "openai_embedding_and_expansion_call_ceiling": 8,
            "estimated_total_cost_ceiling_usd": 0.15,
        },
    }
    contract_path = tmp_path / "holdout-contract.json"
    _write(contract_path, contract)
    extraction_path = tmp_path / "fresh-extraction.json"
    _write(
        extraction_path,
        {
            "status": "ok",
            "capture_health": "good",
            "capture_adequacy": {"captured_turn_count": 44},
            "extraction": {"_quote_validation": {"fabricated": 0}},
        },
    )
    result_path = tmp_path / "holdout-result.json"
    _write(
        result_path,
        {
            "status": "ok",
            "detected_tendencies": ["a", "b", "c", "d"],
            "run_health": {
                "overall": "partial",
                "capture_truncated": False,
                "quote_fabrication_count": 0,
                "bullshit_index_evaluation_failures": 1,
            },
            "usage_summary": {
                "estimated_total_cost_usd": 0.06,
                "vendors": {
                    "openrouter": {
                        "calls": 32,
                        "stages": {
                            "extraction": {"calls": 1},
                            "bullshit_index": {"calls": 12},
                            "pass2": {"calls": 10},
                        },
                    },
                    "openai_embeddings": {"calls": 7},
                },
                "cost_estimate_coverage": {"calls_with_known_price": 39},
            },
            "pre_step6_private_table": {"status": "ready", "source_items": []},
            "v60_enrichment": {
                "status": "active",
                "selected_cards": [],
                "consideration_ledger_skeleton": {
                    "schema_version": "v60_skill_consideration_ledger.v2",
                    "transactions": [],
                },
            },
        },
    )
    gate, _, _ = seal_pipeline_result(
        contract_path=contract_path,
        pipeline_result_path=result_path,
        repo_root=tmp_path,
        fresh_extraction_result_path=extraction_path,
    )
    assert gate["status"] == "passed"
    assert gate["observed"]["core_pressure_openrouter_calls"] == 19
    assert gate["observed"]["pass2_openrouter_calls"] == 10
    assert gate["observed"]["detected_tendency_count"] == 4
    assert gate["observed"]["pass2_detection_yield"] == 0.4
    assert gate["observed"]["bullshit_index_evaluation_failures"] == 1
    assert gate["gates"]["fresh_extraction_turn_count_preserved"] is True


def test_holdout_sealer_blocks_missing_fresh_extraction_artifact(
    tmp_path: Path,
) -> None:
    contract, result = _fixture(tmp_path)
    payload = json.loads(contract.read_text(encoding="utf-8"))
    payload["pipeline_call_budget"] = {
        "extraction_openrouter_call_ceiling": 2,
        "core_pressure_openrouter_call_ceiling": 22,
        "bullshit_index_openrouter_call_ceiling": 12,
        "total_openrouter_call_ceiling": 36,
        "openai_embedding_and_expansion_call_ceiling": 8,
        "estimated_total_cost_ceiling_usd": 0.15,
    }
    payload["fresh_extraction"] = {
        "script_path": payload["frozen_extraction"]["path"],
        "script_sha256": payload["frozen_extraction"]["sha256"],
        "required_status": "ok",
        "required_capture_health": "good",
        "required_captured_turn_count": 44,
        "required_fabricated_quote_count": 0,
    }
    del payload["call_budget"]
    _write(contract, payload)
    gate, _, _ = seal_pipeline_result(
        contract_path=contract,
        pipeline_result_path=result,
        repo_root=tmp_path,
    )
    assert gate["status"] == "failed"
    assert "fresh_extraction_artifact_supplied" in gate["failed_gates"]


def test_sealer_verifies_additional_transitive_hash_locks(tmp_path: Path) -> None:
    contract_path, result_path = _fixture(tmp_path)
    matcher_path = tmp_path / "text_matching.py"
    matcher_hash = _write(matcher_path, {"version": 1})
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["additional_hash_locks"] = [
        {
            "path": matcher_path.name,
            "sha256": matcher_hash,
            "reason": "quote matcher changes extraction admission semantics",
        }
    ]
    _write(contract_path, contract)

    gate, _, _ = seal_pipeline_result(
        contract_path=contract_path,
        pipeline_result_path=result_path,
        repo_root=tmp_path,
    )
    assert gate["status"] == "passed"
    assert gate["contract_hash_checks"][matcher_path.name] is True

    matcher_path.write_text("changed", encoding="utf-8")
    gate, _, _ = seal_pipeline_result(
        contract_path=contract_path,
        pipeline_result_path=result_path,
        repo_root=tmp_path,
    )
    assert gate["status"] == "failed"
    assert gate["contract_hash_checks"][matcher_path.name] is False
    assert "frozen_hashes_match" in gate["failed_gates"]


def test_stage_a_v1_sealer_requires_complete_custody_model_and_embedding_evidence(
    tmp_path: Path,
) -> None:
    paths = {}
    for name in (
        "source",
        "extract_script",
        "pipeline",
        "bullshit_index",
        "v60",
        "affordances",
    ):
        path = tmp_path / f"{name}.json"
        paths[name] = (path, _write(path, {"name": name}))
    run_id = "stage_a_v1_test"
    model = "google/gemini-3.1-flash-lite"
    contract = {
        "schema_version": "lolla.reasoning_portfolio_stage_a_contract.v1",
        "run_id": run_id,
        "case": {
            "case_id": "case-stage-a",
            "source_path": paths["source"][0].name,
            "source_sha256": paths["source"][1],
        },
        "fresh_extraction": {
            "script_path": paths["extract_script"][0].name,
            "script_sha256": paths["extract_script"][1],
            "required_status": "ok",
            "required_capture_health": "good",
            "required_fabricated_quote_count": 0,
            "required_captured_turn_count": 24,
        },
        "pipeline": {
            "script_path": paths["pipeline"][0].name,
            "script_sha256": paths["pipeline"][1],
            "bullshit_index_path": paths["bullshit_index"][0].name,
            "bullshit_index_sha256": paths["bullshit_index"][1],
            "v60_contract_path": paths["v60"][0].name,
            "v60_contract_sha256": paths["v60"][1],
            "affordances_path": paths["affordances"][0].name,
            "affordances_sha256": paths["affordances"][1],
            "model": model,
            "allowed_run_health": ["healthy", "partial"],
        },
        "pipeline_call_budget": {
            "extraction_openrouter_call_ceiling": 2,
            "core_pressure_openrouter_call_ceiling": 22,
            "bullshit_index_openrouter_call_ceiling": 12,
            "total_openrouter_call_ceiling": 36,
            "openai_embedding_and_expansion_call_ceiling": 8,
            "estimated_total_cost_ceiling_usd": 0.15,
            "bullshit_index_evaluation_failure_ceiling": 1,
            "pricing_table_version": "2026-05-25",
        },
    }
    contract_path = tmp_path / "contract.json"
    _write(contract_path, contract)
    extraction_path = tmp_path / "fresh-extraction.json"
    sidecar_path = tmp_path / "calls.json"
    _write(
        sidecar_path,
        [
            {
                "stage": "extraction",
                "provider_name": "openrouter",
                "requested_model": model,
                "served_model": f"{model}-20260701",
                "model": f"{model}-20260701",
                "model_attribution_status": "served_version_alias",
                "status": "ok",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            }
        ],
    )
    _write(
        extraction_path,
        {
            "status": "ok",
            "capture_health": "good",
            "capture_adequacy": {"captured_turn_count": 24},
            "provider_call_custody": {
                "admissible_extraction": True,
                "recorded_call_count": 1,
            },
            "extraction": {"_quote_validation": {"fabricated": 0}},
        },
    )
    execution_path = tmp_path / "execution.json"
    _write(
        execution_path,
        {
            "status": "completed",
            "orchestrator_invocations": 1,
            "gates": {
                "run_directory_absent_before_run": True,
                "all_sidecars_absent_before_run": True,
                "extraction_outer_timeout_not_triggered": True,
                "pipeline_outer_timeout_not_triggered": True,
                "extraction_exit_zero": True,
                "pipeline_exit_zero": True,
            },
        },
    )
    result_path = tmp_path / "result.json"
    _write(
        result_path,
        {
            "status": "ok",
            "run_health": {
                "overall": "partial",
                "embeddings": "active",
                "capture_truncated": False,
                "quote_fabrication_count": 0,
                "bullshit_index_evaluation_failures": 1,
            },
            "usage_summary": {
                "run_id": run_id,
                "pricing_table_version": "2026-05-25",
                "cost_estimate_state": "complete",
                "estimated_total_cost_usd": 0.06,
                "vendors": {
                    "openrouter": {
                        "provider": "openrouter",
                        "calls": 32,
                        "prompt_tokens": 1000,
                        "completion_tokens": 500,
                        "models_seen": [f"{model}-20260701"],
                        "requested_models_seen": [model],
                        "model_attribution": {
                            "status_counts": {
                                "matched": 31,
                                "served_version_alias": 1,
                            },
                            "mismatch_count": 0,
                        },
                        "stages": {
                            "extraction": {"calls": 1},
                            "bullshit_index": {"calls": 12},
                        },
                    },
                    "openai_embeddings": {
                        "provider": "openai",
                        "calls": 7,
                    },
                },
                "cost_estimate_coverage": {"calls_with_known_price": 39},
            },
            "pre_step6_private_table": {"status": "ready", "source_items": []},
            "v60_enrichment": {
                "status": "active",
                "selected_cards": [],
                "consideration_ledger_skeleton": {
                    "schema_version": "v60_skill_consideration_ledger.v2",
                    "transactions": [],
                },
            },
        },
    )

    gate, _, _ = seal_pipeline_result(
        contract_path=contract_path,
        pipeline_result_path=result_path,
        repo_root=tmp_path,
        fresh_extraction_result_path=extraction_path,
        execution_result_path=execution_path,
        extraction_call_sidecar_path=sidecar_path,
    )

    assert gate["status"] == "passed"
    assert gate["gates"]["usage_cost_state_complete"] is True
    assert gate["gates"]["openrouter_model_attribution_complete"] is True
    assert gate["gates"]["direct_openai_embedding_policy_observed"] is True


def test_shared_stage_a_execution_contract_rejects_legacy_runner_field() -> None:
    with pytest.raises(ValueError, match="extraction_exit_zero"):
        validate_stage_a_execution_gates(
            {
                "run_directory_absent_before_run": True,
                "all_sidecars_absent_before_run": True,
                "extractor_exit_zero": True,
                "extraction_outer_timeout_not_triggered": True,
                "pipeline_exit_zero": True,
                "pipeline_outer_timeout_not_triggered": True,
            }
        )
