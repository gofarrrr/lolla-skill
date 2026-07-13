#!/usr/bin/env python3
"""Seal a full-surface pipeline result into review-safe research artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.stage_a_execution_contract import (
    EXTRACTION_EXIT_ZERO_GATE,
    EXTRACTION_TIMEOUT_CLEAR_GATE,
    PIPELINE_EXIT_ZERO_GATE,
    PIPELINE_TIMEOUT_CLEAR_GATE,
    RUN_DIRECTORY_ABSENT_GATE,
    SIDECARS_ABSENT_GATE,
    validate_stage_a_execution_gates,
)


GATE_SCHEMA = "lolla.reasoning_portfolio_pipeline_gate_result.v0"
TABLE_SCHEMA = "lolla.reasoning_portfolio_private_table_snapshot.v0"
V60_SCHEMA = "lolla.reasoning_portfolio_v60_snapshot.v0"


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _contract_hash_checks(contract: Mapping[str, Any], root: Path) -> dict[str, bool]:
    specs: list[tuple[Any, Any]] = [
        (contract["case"]["source_path"], contract["case"]["source_sha256"]),
        (contract["pipeline"]["script_path"], contract["pipeline"]["script_sha256"]),
        (
            contract["pipeline"]["v60_contract_path"],
            contract["pipeline"]["v60_contract_sha256"],
        ),
        (
            contract["pipeline"]["affordances_path"],
            contract["pipeline"]["affordances_sha256"],
        ),
    ]
    if "frozen_extraction" in contract:
        specs.append(
            (
                contract["frozen_extraction"]["path"],
                contract["frozen_extraction"]["sha256"],
            )
        )
    if "rejected_historical_extraction" in contract:
        specs.append(
            (
                contract["rejected_historical_extraction"]["path"],
                contract["rejected_historical_extraction"]["sha256"],
            )
        )
    if "fresh_extraction" in contract:
        specs.append(
            (
                contract["fresh_extraction"]["script_path"],
                contract["fresh_extraction"]["script_sha256"],
            )
        )
    if "bullshit_index_path" in contract["pipeline"]:
        specs.append(
            (
                contract["pipeline"]["bullshit_index_path"],
                contract["pipeline"]["bullshit_index_sha256"],
            )
        )
    if "existing_control_reuse" in contract:
        specs.append(
            (
                contract["existing_control_reuse"]["artifact_path"],
                contract["existing_control_reuse"]["artifact_sha256"],
            )
        )
    additional_locks = contract.get("additional_hash_locks", [])
    if additional_locks:
        if not isinstance(additional_locks, list):
            raise ValueError("additional_hash_locks must be an array")
        for index, lock in enumerate(additional_locks):
            if not isinstance(lock, Mapping):
                raise ValueError(f"additional_hash_locks[{index}] must be an object")
            if set(lock) != {"path", "sha256", "reason"}:
                raise ValueError(
                    f"additional_hash_locks[{index}] must contain path, sha256, and reason"
                )
            specs.append((lock["path"], lock["sha256"]))
    hash_locks = contract.get("hash_locks", [])
    if hash_locks:
        if not isinstance(hash_locks, list):
            raise ValueError("hash_locks must be an array")
        for index, lock in enumerate(hash_locks):
            if not isinstance(lock, Mapping):
                raise ValueError(f"hash_locks[{index}] must be an object")
            if set(lock) != {"role", "path", "sha256"}:
                raise ValueError(
                    f"hash_locks[{index}] must contain role, path, and sha256"
                )
            specs.append((lock["path"], lock["sha256"]))
    return {
        str(path): (root / str(path)).is_file()
        and _hash_file(root / str(path)) == str(expected)
        for path, expected in specs
    }


def seal_pipeline_result(
    *,
    contract_path: Path,
    pipeline_result_path: Path,
    repo_root: Path,
    fresh_extraction_result_path: Path | None = None,
    execution_result_path: Path | None = None,
    extraction_call_sidecar_path: Path | None = None,
    experiment_retry_count: int = 0,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = _load_object(contract_path)
    result = _load_object(pipeline_result_path)
    hash_checks = _contract_hash_checks(contract, repo_root)
    usage = result.get("usage_summary", {})
    vendors = usage.get("vendors", {}) if isinstance(usage, Mapping) else {}
    openrouter = vendors.get("openrouter", {}) if isinstance(vendors, Mapping) else {}
    openrouter_calls = int(openrouter.get("calls", 0) or 0)
    stages = openrouter.get("stages", {}) if isinstance(openrouter, Mapping) else {}
    extraction_calls = sum(
        int(stages.get(stage, {}).get("calls", 0) or 0)
        for stage in ("extraction", "extraction_retry")
    )
    bullshit_index_calls = int(
        stages.get("bullshit_index", {}).get("calls", 0) or 0
    )
    revision_calls = int(stages.get("revision", {}).get("calls", 0) or 0)
    core_pressure_calls = (
        openrouter_calls
        - extraction_calls
        - bullshit_index_calls
        - revision_calls
    )
    pass2_calls = int(stages.get("pass2", {}).get("calls", 0) or 0)
    detected_tendencies = result.get("detected_tendencies", [])
    detected_tendency_count = (
        len(detected_tendencies) if isinstance(detected_tendencies, list) else 0
    )
    pass2_detection_yield = (
        round(detected_tendency_count / pass2_calls, 6) if pass2_calls else None
    )
    openai = vendors.get("openai_embeddings", {}) if isinstance(vendors, Mapping) else {}
    openai_calls = int(openai.get("calls", 0) or 0)
    total_cost = float(usage.get("estimated_total_cost_usd", 0.0) or 0.0)
    health = result.get("run_health", {})
    table = result.get("pre_step6_private_table", {})
    v60 = result.get("v60_enrichment", {})
    skeleton = v60.get("consideration_ledger_skeleton", {})
    gates: dict[str, bool] = {
        "frozen_hashes_match": all(hash_checks.values()),
        "result_status_ok": result.get("status") == "ok",
        "capture_not_truncated": health.get("capture_truncated") is False,
        "quote_fabrication_zero": int(health.get("quote_fabrication_count", 0) or 0)
        == 0,
        "private_table_ready": table.get("status") == "ready",
        "v60_enrichment_active": v60.get("status") == "active",
        "v60_ledger_schema_v2": skeleton.get("schema_version")
        == "v60_skill_consideration_ledger.v2",
        "no_experiment_retry": experiment_retry_count == 0,
    }
    extraction_result: Mapping[str, Any] = {}
    extraction_result_sha256 = None
    if "pipeline_call_budget" in contract:
        if fresh_extraction_result_path is not None:
            extraction_result = _load_object(fresh_extraction_result_path)
            extraction_result_sha256 = _hash_file(fresh_extraction_result_path)
        fresh_contract = contract.get("fresh_extraction", {})
        extraction = extraction_result.get("extraction", {})
        quote_validation = (
            extraction.get("_quote_validation", {})
            if isinstance(extraction, Mapping)
            else {}
        )
        capture_adequacy = extraction_result.get("capture_adequacy", {})
        if not isinstance(capture_adequacy, Mapping):
            capture_adequacy = {}
        budget = contract["pipeline_call_budget"]
        gates.update(
            {
                "fresh_extraction_artifact_supplied": bool(extraction_result),
                "fresh_extraction_status_ok": extraction_result.get("status")
                == fresh_contract.get("required_status", "ok"),
                "fresh_extraction_capture_health_good": extraction_result.get(
                    "capture_health"
                )
                == fresh_contract.get("required_capture_health", "good"),
                "fresh_extraction_turn_count_preserved": int(
                    capture_adequacy.get("captured_turn_count", 0) or 0
                )
                == int(fresh_contract.get("required_captured_turn_count", 0) or 0),
                "fresh_extraction_quote_fabrication_zero": int(
                    quote_validation.get("fabricated", 0) or 0
                )
                == int(fresh_contract.get("required_fabricated_quote_count", 0) or 0),
                "fresh_extraction_call_ceiling_met": extraction_calls
                <= int(budget["extraction_openrouter_call_ceiling"]),
                "core_pressure_call_ceiling_met": core_pressure_calls
                <= int(budget["core_pressure_openrouter_call_ceiling"]),
                "bullshit_index_call_ceiling_met": bullshit_index_calls
                <= int(budget["bullshit_index_openrouter_call_ceiling"]),
                "total_openrouter_call_ceiling_met": openrouter_calls
                <= int(budget["total_openrouter_call_ceiling"]),
                "openai_call_ceiling_met": openai_calls
                <= int(budget["openai_embedding_and_expansion_call_ceiling"]),
                "estimated_cost_ceiling_met": total_cost
                <= float(budget["estimated_total_cost_ceiling_usd"]),
            }
        )

        if contract.get("schema_version") == "lolla.reasoning_portfolio_stage_a_contract.v1":
            execution_result: Mapping[str, Any] = {}
            if execution_result_path is not None:
                execution_result = _load_object(execution_result_path)
            sidecar_records: list[Mapping[str, Any]] = []
            if extraction_call_sidecar_path is not None and extraction_call_sidecar_path.is_file():
                raw_sidecar = json.loads(
                    extraction_call_sidecar_path.read_text(encoding="utf-8")
                )
                if isinstance(raw_sidecar, list):
                    sidecar_records = [
                        item for item in raw_sidecar if isinstance(item, Mapping)
                    ]
            call_custody = extraction_result.get("provider_call_custody", {})
            if not isinstance(call_custody, Mapping):
                call_custody = {}
            openrouter_attribution = openrouter.get("model_attribution", {})
            if not isinstance(openrouter_attribution, Mapping):
                openrouter_attribution = {}
            status_counts = openrouter_attribution.get("status_counts", {})
            if not isinstance(status_counts, Mapping):
                status_counts = {}
            acceptable_attribution_count = sum(
                int(status_counts.get(name, 0) or 0)
                for name in ("matched", "served_version_alias")
            )
            requested_model = str(contract["pipeline"]["model"])
            models_seen = [str(item) for item in openrouter.get("models_seen", [])]
            requested_models_seen = [
                str(item) for item in openrouter.get("requested_models_seen", [])
            ]
            model_compatible = bool(models_seen) and all(
                item == requested_model or item.startswith(f"{requested_model}-")
                for item in models_seen
            )
            allowed_health = contract["pipeline"].get(
                "allowed_run_health", ["healthy", "partial"]
            )
            openai_block = (
                vendors.get("openai_embeddings", {})
                if isinstance(vendors, Mapping)
                else {}
            )
            if not isinstance(openai_block, Mapping):
                openai_block = {}
            execution_gates = execution_result.get("gates", {})
            if not isinstance(execution_gates, Mapping):
                execution_gates = {}
            validate_stage_a_execution_gates(execution_gates)
            extraction_statuses = [
                str(item.get("status", "")) for item in sidecar_records
            ]
            gates.update(
                {
                    "execution_artifact_supplied": bool(execution_result),
                    "execution_status_completed": execution_result.get("status")
                    == "completed",
                    "single_orchestrator_invocation": int(
                        execution_result.get("orchestrator_invocations", 0) or 0
                    )
                    == 1,
                    "fresh_run_directory_preflight_passed": execution_gates.get(
                        RUN_DIRECTORY_ABSENT_GATE
                    )
                    is True,
                    "fresh_sidecar_preflight_passed": execution_gates.get(
                        SIDECARS_ABSENT_GATE
                    )
                    is True,
                    "extraction_outer_timeout_not_triggered": execution_gates.get(
                        EXTRACTION_TIMEOUT_CLEAR_GATE
                    )
                    is True,
                    "pipeline_outer_timeout_not_triggered": execution_gates.get(
                        PIPELINE_TIMEOUT_CLEAR_GATE
                    )
                    is True,
                    "extraction_exit_zero": execution_gates.get(
                        EXTRACTION_EXIT_ZERO_GATE
                    )
                    is True,
                    "pipeline_exit_zero": execution_gates.get(PIPELINE_EXIT_ZERO_GATE)
                    is True,
                    "extraction_custody_admissible": call_custody.get(
                        "admissible_extraction"
                    )
                    is True,
                    "extraction_call_record_count_consistent": int(
                        call_custody.get("recorded_call_count", -1) or 0
                    )
                    == len(sidecar_records)
                    and len(sidecar_records) == extraction_calls,
                    "extraction_call_statuses_ok": bool(extraction_statuses)
                    and all(status.startswith("ok") for status in extraction_statuses),
                    "usage_run_id_exact": usage.get("run_id")
                    == contract.get("run_id"),
                    "usage_cost_state_complete": usage.get("cost_estimate_state")
                    == "complete",
                    "pricing_table_version_exact": usage.get("pricing_table_version")
                    == contract["pipeline_call_budget"].get(
                        "pricing_table_version"
                    ),
                    "openrouter_provider_exact": openrouter.get("provider")
                    == "openrouter",
                    "openrouter_requested_model_exact": requested_models_seen
                    == [requested_model],
                    "openrouter_served_models_compatible": model_compatible,
                    "openrouter_model_attribution_complete": int(
                        openrouter_attribution.get("mismatch_count", 0) or 0
                    )
                    == 0
                    and acceptable_attribution_count == openrouter_calls,
                    "openrouter_token_usage_present": int(
                        openrouter.get("prompt_tokens", 0) or 0
                    )
                    > 0
                    and int(openrouter.get("completion_tokens", 0) or 0) > 0,
                    "direct_openai_embedding_policy_observed": result.get(
                        "run_health", {}
                    ).get("embeddings")
                    == "active"
                    and openai_block.get("provider") == "openai"
                    and int(openai_block.get("calls", 0) or 0) > 0,
                    "run_health_allowed": health.get("overall") in allowed_health,
                    "bullshit_index_failure_ceiling_met": int(
                        health.get("bullshit_index_evaluation_failures", 0) or 0
                    )
                    <= int(
                        contract["pipeline_call_budget"].get(
                            "bullshit_index_evaluation_failure_ceiling", 0
                        )
                    ),
                }
            )
    else:
        budget = contract["call_budget"]
        gates.update(
            {
                "openrouter_call_ceiling_met": openrouter_calls
                <= int(
                    budget["recorded_pipeline_and_postprocessing_chat_call_ceiling"]
                ),
                "estimated_cost_ceiling_met": total_cost
                <= float(budget["estimated_cost_ceiling_usd"]),
            }
        )
    failed_gates = [name for name, passed in gates.items() if not passed]
    gate_result = {
        "schema_version": GATE_SCHEMA,
        "status": "passed" if not failed_gates else "failed",
        "case_id": contract["case"]["case_id"],
        "contract_sha256": _hash_file(contract_path),
        "raw_pipeline_result_sha256": _hash_file(pipeline_result_path),
        "contract_hash_checks": hash_checks,
        "observed": {
            "run_health": health.get("overall"),
            "openrouter_calls": openrouter_calls,
            "extraction_openrouter_calls": extraction_calls,
            "core_pressure_openrouter_calls": core_pressure_calls,
            "pass2_openrouter_calls": pass2_calls,
            "detected_tendency_count": detected_tendency_count,
            "pass2_detection_yield": pass2_detection_yield,
            "bullshit_index_openrouter_calls": bullshit_index_calls,
            "revision_openrouter_calls": revision_calls,
            "openai_embedding_and_expansion_calls": openai_calls,
            "total_calls_with_known_price": usage.get("cost_estimate_coverage", {}).get(
                "calls_with_known_price"
            ),
            "estimated_total_cost_usd": total_cost,
            "private_table_character_count": table.get("table_char_count"),
            "private_table_source_item_count": len(table.get("source_items", [])),
            "v60_selected_model_count": len(v60.get("selected_cards", [])),
            "v60_selected_chunk_count": len(skeleton.get("transactions", [])),
            "experiment_retry_count": experiment_retry_count,
            "fresh_extraction_result_sha256": extraction_result_sha256,
            "execution_result_sha256": (
                _hash_file(execution_result_path)
                if execution_result_path is not None
                and execution_result_path.is_file()
                else None
            ),
            "extraction_call_sidecar_sha256": (
                _hash_file(extraction_call_sidecar_path)
                if extraction_call_sidecar_path is not None
                and extraction_call_sidecar_path.is_file()
                else None
            ),
            "bullshit_index_evaluation_failures": int(
                health.get("bullshit_index_evaluation_failures", 0) or 0
            ),
        },
        "gates": gates,
        "failed_gates": failed_gates,
        "consumer_call_authorized": False,
        "consumer_call_authorization_reason": (
            "pipeline_admission_failed"
            if failed_gates
            else "separate_semantic_novelty_review_required"
        ),
        "runtime_integration_authorized": False,
        "model_calls_by_sealer": 0,
        "non_claims": [
            "healthy_artifacts_are_not_reasoning_quality",
            "low_cost_is_not_operability",
            "candidate_selection_is_not_semantic_novelty",
            "not_product_proof",
        ],
    }

    safe_table = {
        "schema_version": TABLE_SCHEMA,
        "status": "review_safe_snapshot",
        "source_pipeline_sha256": _hash_file(pipeline_result_path),
        "table_schema_version": table.get("schema_version"),
        "table_status": table.get("status"),
        "runtime_policy": table.get("runtime_policy"),
        "promotion_effect": table.get("promotion_effect"),
        "compiled_card_deck_key": table.get("compiled_card_deck_key"),
        "key_material": table.get("key_material", {}),
        "cache_state": table.get("cache", {}).get("state"),
        "table_character_count": table.get("table_char_count"),
        "table_section_count": table.get("table_section_count"),
        "source_items": table.get("source_items", []),
        "consideration_ledger_skeleton": table.get(
            "consideration_ledger_skeleton", {}
        ),
        "raw_table_text_included": False,
        "absolute_paths_included": False,
    }

    cards = []
    for card in v60.get("selected_cards", []):
        if not isinstance(card, Mapping):
            continue
        cards.append(
            {
                "card_id": card.get("card_id"),
                "model_id": card.get("model_id"),
                "selection_source": card.get("selection_source"),
                "selection_reason": card.get("selection_reason"),
                "affordance_chunk_ids": [
                    item.get("chunk_id")
                    for item in card.get("selected_affordance_cards", [])
                    if isinstance(item, Mapping)
                ],
                "absence_chunk_ids": [
                    item.get("chunk_id")
                    for item in card.get("selected_absence_records", [])
                    if isinstance(item, Mapping)
                ],
            }
        )
    safe_v60 = {
        "schema_version": V60_SCHEMA,
        "status": "review_safe_snapshot",
        "source_pipeline_sha256": _hash_file(pipeline_result_path),
        "v60_schema_version": v60.get("schema_version"),
        "v60_status": v60.get("status"),
        "selected_cards": cards,
        "consideration_ledger_skeleton": skeleton,
        "raw_chunk_text_included": False,
        "absolute_paths_included": False,
    }
    return gate_result, safe_table, safe_v60


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--pipeline-result", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--fresh-extraction-result", type=Path)
    parser.add_argument("--execution-result", type=Path)
    parser.add_argument("--extraction-call-sidecar", type=Path)
    parser.add_argument("--experiment-retry-count", type=int, default=0)
    args = parser.parse_args(argv)
    gate, table, v60 = seal_pipeline_result(
        contract_path=args.contract,
        pipeline_result_path=args.pipeline_result,
        repo_root=args.repo_root,
        fresh_extraction_result_path=args.fresh_extraction_result,
        execution_result_path=args.execution_result,
        extraction_call_sidecar_path=args.extraction_call_sidecar,
        experiment_retry_count=args.experiment_retry_count,
    )
    _write_json(args.out_dir / "pipeline-gate-result.json", gate)
    _write_json(args.out_dir / "private-table-snapshot.json", table)
    _write_json(args.out_dir / "v60-snapshot.json", v60)
    return 0 if gate["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
