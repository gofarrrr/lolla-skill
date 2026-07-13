from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import pytest

from scripts.evals import run_reasoning_portfolio_stage_a as stage_a


REQUIRED_ROLES = {
    "selection",
    "source",
    "stage_a_runner",
    "stage_a_execution_contract",
    "extractor",
    "pipeline_runner",
    "pipeline_engine",
    "pipeline_prompts",
    "companion_routing",
    "frame_pressure",
    "structural_coverage",
    "bullshit_index",
    "embedding_retriever",
    "v60_enrichment",
    "affordances_v60",
    "knowledge_graph",
    "relationship_graph",
    "compiled_chunks",
    "reasoning_signals",
    "subpattern_catalog",
    "structural_signal_lexicon",
    "quote_matcher",
    "boundary_provider",
    "capture_adequacy",
    "audit_mode",
    "run_state",
    "usage_summary",
    "pricing",
    "pipeline_sealer",
    "two_stage_protocol",
}


def _write(path: Path, value: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, Path, Path]:
    monkeypatch.setattr(stage_a, "REPO_ROOT", tmp_path)
    source = tmp_path / "source.txt"
    source_hash = _write(
        source,
        "CONVERSATION: 2 turns, 1 user message, 1 assistant response\n\n"
        "[Turn 1] USER:\nThink.\n\n[Turn 1] ASSISTANT:\nReason.\n",
    )
    selection = tmp_path / "selection.json"
    selection_hash = _write(
        selection,
        json.dumps(
            {"selection_rule": {"selected_case_id": "case-test"}},
            sort_keys=True,
        ),
    )
    locks = []
    for role in sorted(REQUIRED_ROLES):
        if role == "selection":
            path, digest = selection, selection_hash
        elif role == "source":
            path, digest = source, source_hash
        elif role == "knowledge_graph":
            path = tmp_path / "locks" / "knowledge_graph.json"
            digest = _write(
                path,
                json.dumps({"tendencies": {f"tendency-{index}": {} for index in range(25)}}),
            )
        else:
            path = tmp_path / "locks" / f"{role}.txt"
            digest = _write(path, role)
        locks.append(
            {"role": role, "path": str(path.relative_to(tmp_path)), "sha256": digest}
        )
    run_id = "stage_a_test_once"
    run_dir = Path("research/run")
    lock_by_role = {item["role"]: item for item in locks}
    contract = {
        "schema_version": stage_a.CONTRACT_SCHEMA,
        "status": "frozen_before_calls",
        "run_id": run_id,
        "execution_runtime": {
            "minimum_python_version": [3, 10],
            "required_python_version": platform.python_version(),
            "executable_path": str(Path(sys.executable).resolve()),
            "executable_sha256": hashlib.sha256(
                Path(sys.executable).resolve().read_bytes()
            ).hexdigest(),
        },
        "selection": {"path": "selection.json", "sha256": selection_hash},
        "case": {
            "case_id": "case-test",
            "source_path": "source.txt",
            "source_sha256": source_hash,
        },
        "prompt_hashes": stage_a._prompt_hashes(source.read_text(encoding="utf-8")),
        "fresh_extraction": {
            "script_path": lock_by_role["extractor"]["path"],
            "script_sha256": lock_by_role["extractor"]["sha256"],
            "provider": "openrouter",
            "model": "google/gemini-3.1-flash-lite",
            "provider_timeout_seconds": 5,
            "wall_clock_timeout_seconds": 10,
            "maximum_builtin_quote_repair_calls": 1,
            "required_captured_message_count": 2,
            "minimum_reasoning_passages": 1,
            "required_status": "ok",
            "required_capture_health": "good",
            "required_fabricated_quote_count": 0,
            "required_captured_turn_count": 2,
        },
        "pipeline": {
            "script_path": lock_by_role["pipeline_runner"]["path"],
            "script_sha256": lock_by_role["pipeline_runner"]["sha256"],
            "bullshit_index_path": lock_by_role["bullshit_index"]["path"],
            "bullshit_index_sha256": lock_by_role["bullshit_index"]["sha256"],
            "v60_contract_path": lock_by_role["v60_enrichment"]["path"],
            "v60_contract_sha256": lock_by_role["v60_enrichment"]["sha256"],
            "affordances_sha256": lock_by_role["affordances_v60"]["sha256"],
            "provider": "openrouter",
            "model": "google/gemini-3.1-flash-lite",
            "provider_timeout_seconds": 5,
            "wall_clock_timeout_seconds": 20,
            "embedding_policy": "on_direct_openai_only",
            "skip_revision": True,
            "pre_step6_portfolio": "step6_private",
            "audit_mode": "standard",
            "companion_candidate_cap": 60,
            "v60_max_cards": 8,
            "affordances_path": "locks/affordances_v60.txt",
            "allowed_run_health": ["healthy", "partial"],
        },
        "pipeline_call_budget": {
            "budget_kind": "theoretical_custody_envelope",
            "derivation": {
                "pass1_fixed_calls": 6,
                "hash_locked_tendency_count": 25,
                "companion_fixed_calls": 2,
                "frame_fixed_calls": 2,
                "structural_coverage_maximum_calls": 3,
            },
            "extraction_openrouter_call_ceiling": 2,
            "core_pressure_openrouter_call_ceiling": 38,
            "bullshit_index_openrouter_call_ceiling": 12,
            "total_openrouter_call_ceiling": 52,
            "openai_embedding_and_expansion_call_ceiling": 8,
            "estimated_total_cost_ceiling_usd": 0.15,
            "bullshit_index_evaluation_failure_ceiling": 1,
            "pricing_table_version": "2026-05-25",
        },
        "experiment_retries": 0,
        "hash_locks": locks,
        "artifacts": {
            "run_dir": str(run_dir),
            "extraction_path": str(run_dir / f"lolla_{run_id}_extraction.json"),
            "pipeline_result_path": str(run_dir / "pipeline-result.json"),
            "execution_result_path": str(run_dir / "execution-result.json"),
            "sealed_output_dir": "research/sealed",
            "extraction_call_sidecar_path": f"/tmp/lolla_{run_id}_extraction_calls.json",
            "private_table_json_sidecar_path": f"/tmp/lolla_{run_id}_pre_step6_private_table.json",
            "private_table_markdown_sidecar_path": f"/tmp/lolla_{run_id}_pre_step6_private_table.md",
            "v60_ledger_sidecar_path": f"/tmp/lolla_{run_id}_v60_ledger_skeleton.json",
        },
    }
    contract_path = tmp_path / "contract.json"
    _write(contract_path, json.dumps(contract))
    env_path = tmp_path / "env"
    _write(env_path, "OPENROUTER_API_KEY=fake\nOPENAI_API_KEY=fake\n")
    return contract, contract_path, env_path


def test_contract_validates_selection_prompts_and_transitive_locks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract, _contract_path, _env = _fixture(tmp_path, monkeypatch)
    stage_a.validate_contract(contract)


def test_runner_stops_after_failed_extraction_without_pipeline_or_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract, contract_path, env_path = _fixture(tmp_path, monkeypatch)
    calls = []

    def failed(command: list[str], **_kwargs: object) -> dict[str, object]:
        calls.append(command)
        return {
            "exit_code": 1,
            "timed_out": False,
            "wall_time_seconds": 0.01,
            "stdout_sha256": "a" * 64,
            "stderr_sha256": "b" * 64,
        }

    monkeypatch.setattr(stage_a, "_run_command", failed)
    result = stage_a.run_stage_a(
        contract,
        contract_path=contract_path,
        env_file=env_path,
    )

    assert result["status"] == "stopped_after_extraction"
    assert len(calls) == 1
    assert result["pipeline"] == {"not_run": True}
    assert result["experiment_retry_count"] == 0
    assert result["gates"]["extraction_exit_zero"] is False
    assert "extractor_exit_zero" not in result["gates"]
    execution_path = tmp_path / contract["artifacts"]["execution_result_path"]
    assert execution_path.is_file()


def test_contract_rejects_embedding_policy_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract, _contract_path, _env = _fixture(tmp_path, monkeypatch)
    contract["pipeline"]["embedding_policy"] = "auto"
    with pytest.raises(stage_a.StageAContractError, match="direct-OpenAI"):
        stage_a.validate_contract(contract)


def test_contract_rejects_arbitrary_understated_core_call_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract, _contract_path, _env = _fixture(tmp_path, monkeypatch)
    contract["pipeline_call_budget"]["core_pressure_openrouter_call_ceiling"] = 22
    contract["pipeline_call_budget"]["total_openrouter_call_ceiling"] = 36
    with pytest.raises(stage_a.StageAContractError, match="pipeline-derived"):
        stage_a.validate_contract(contract)


def test_contract_rejects_incompatible_python_before_any_provider_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract, _contract_path, _env = _fixture(tmp_path, monkeypatch)
    contract["execution_runtime"]["minimum_python_version"] = [99, 0]
    with pytest.raises(stage_a.StageAContractError, match="older than"):
        stage_a.validate_contract(contract)


def test_contract_rejects_headerless_source_before_any_provider_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract, _contract_path, _env = _fixture(tmp_path, monkeypatch)
    source = tmp_path / contract["case"]["source_path"]
    source.write_text(
        "[Turn 1] USER:\nThink.\n\n[Turn 1] ASSISTANT:\nReason.\n",
        encoding="utf-8",
    )
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    contract["case"]["source_sha256"] = source_hash
    contract["prompt_hashes"] = stage_a._prompt_hashes(
        source.read_text(encoding="utf-8")
    )
    for lock in contract["hash_locks"]:
        if lock["role"] == "source":
            lock["sha256"] = source_hash

    with pytest.raises(stage_a.StageAContractError, match="capture envelope"):
        stage_a.validate_contract(contract)


def test_real_runner_execution_envelope_passes_the_real_sealer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract, contract_path, env_path = _fixture(tmp_path, monkeypatch)
    artifacts = contract["artifacts"]
    extraction_path = tmp_path / artifacts["extraction_path"]
    pipeline_path = tmp_path / artifacts["pipeline_result_path"]
    sidecar_path = Path(artifacts["extraction_call_sidecar_path"])
    sidecar_path.unlink(missing_ok=True)
    model = contract["pipeline"]["model"]
    call_number = 0

    def successful(_command: list[str], **_kwargs: object) -> dict[str, object]:
        nonlocal call_number
        call_number += 1
        if call_number == 1:
            extraction_path.parent.mkdir(parents=True, exist_ok=True)
            extraction_path.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "capture_health": "good",
                        "capture_adequacy": {
                            "captured_turn_count": 2,
                            "omitted_turn_count": 0,
                        },
                        "provider_call_custody": {
                            "admissible_extraction": True,
                            "recorded_call_count": 1,
                        },
                        "extraction": {
                            "reasoning_passages": ["Reason."],
                            "_quote_validation": {"fabricated": 0},
                        },
                    }
                ),
                encoding="utf-8",
            )
            sidecar_path.write_text(
                json.dumps(
                    [
                        {
                            "stage": "extraction",
                            "provider_name": "openrouter",
                            "requested_model": model,
                            "served_model": model,
                            "model": model,
                            "model_attribution_status": "matched",
                            "status": "ok",
                            "prompt_tokens": 10,
                            "completion_tokens": 5,
                            "total_tokens": 15,
                        }
                    ]
                ),
                encoding="utf-8",
            )
        else:
            pipeline_path.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "run_health": {
                            "overall": "healthy",
                            "embeddings": "active",
                            "capture_truncated": False,
                            "quote_fabrication_count": 0,
                            "bullshit_index_evaluation_failures": 0,
                        },
                        "audit_summary": {"boundary_calls": []},
                        "usage_summary": {
                            "run_id": contract["run_id"],
                            "pricing_table_version": "2026-05-25",
                            "cost_estimate_state": "complete",
                            "estimated_total_cost_usd": 0.01,
                            "cost_estimate_coverage": {
                                "calls_with_known_price": 6
                            },
                            "vendors": {
                                "openrouter": {
                                    "provider": "openrouter",
                                    "calls": 5,
                                    "prompt_tokens": 100,
                                    "completion_tokens": 50,
                                    "models_seen": [model],
                                    "requested_models_seen": [model],
                                    "model_attribution": {
                                        "status_counts": {"matched": 5},
                                        "mismatch_count": 0,
                                    },
                                    "stages": {
                                        "extraction": {"calls": 1},
                                        "bullshit_index": {"calls": 1},
                                    },
                                },
                                "openai_embeddings": {
                                    "provider": "openai",
                                    "calls": 1,
                                },
                            },
                        },
                        "pre_step6_private_table": {
                            "status": "ready",
                            "source_items": [],
                        },
                        "v60_enrichment": {
                            "status": "active",
                            "selected_cards": [],
                            "consideration_ledger_skeleton": {
                                "schema_version": "v60_skill_consideration_ledger.v2",
                                "transactions": [],
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
        return {
            "exit_code": 0,
            "timed_out": False,
            "wall_time_seconds": 0.01,
            "stdout_sha256": "a" * 64,
            "stderr_sha256": "b" * 64,
        }

    monkeypatch.setattr(stage_a, "_run_command", successful)
    try:
        result = stage_a.run_stage_a(
            contract,
            contract_path=contract_path,
            env_file=env_path,
        )
        assert result["status"] == "passed"
        execution = json.loads(
            (tmp_path / artifacts["execution_result_path"]).read_text(
                encoding="utf-8"
            )
        )
        assert execution["gates"]["extraction_exit_zero"] is True
        assert "extractor_exit_zero" not in execution["gates"]
    finally:
        sidecar_path.unlink(missing_ok=True)
