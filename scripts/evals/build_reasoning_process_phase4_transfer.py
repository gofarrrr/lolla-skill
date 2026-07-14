#!/usr/bin/env python3
"""Freeze the provider-free Phase-4 two-case transfer contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_exploration_local import (  # noqa: E402
    build_local_prompts,
    local_response_schema,
)
from engine.system_b.reasoning_process_view_specific_v3 import (  # noqa: E402
    SUPPORTED_VIEWS,
    build_prompts_v3,
    response_schema_v3,
)
from engine.system_b.reasoning_process_views import (  # noqa: E402
    canonical_json_bytes,
    sha256_bytes,
)

SCHEMA = "lolla.reasoning_process_phase4_transfer_contract.v1"
MODEL = "google/gemini-3.1-flash-lite"
DEVELOPMENT_CASE = "amb1-case02-nonprofit-scale"
ELIGIBLE_CASES = (
    "amb1-case01-product-scope",
    "amb1-case03-creative-partnership",
    "amb1-case04-research-tool-release",
    "amb1-case05-family-archive",
)
SELECTED_CASES = tuple(sorted(ELIGIBLE_CASES, key=lambda value: hashlib.sha256(value.encode()).hexdigest())[:2])


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_sha(value: object) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _case_paths(case_id: str) -> dict[str, str]:
    stem = {
        "amb1-case01-product-scope": "amb1-case01-product-scope",
        "amb1-case03-creative-partnership": "amb1-case03-creative-partnership",
        "amb1-case04-research-tool-release": "amb1-case04-research-tool-release",
        "amb1-case05-family-archive": "amb1-case05-family-archive",
    }[case_id]
    return {
        "source_path": f"research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/{stem}.txt",
        "phase1_ledger_path": f"research/reasoning-process-phase1-ledger-2026-07-11/cases/{case_id}/ledger.json",
    }


def build_contract(root: Path) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    jobs: list[dict[str, Any]] = []
    local_report = _load(root / "research/reasoning-process-exploration-local-v2-2026-07-11/report.json")
    local_by_case = {item["case_id"]: item for item in local_report["cases"]}
    for case_id in SELECTED_CASES:
        paths = _case_paths(case_id)
        source = root / paths["source_path"]
        ledger = root / paths["phase1_ledger_path"]
        cases.append(
            {
                "case_id": case_id,
                "selection_sha256": hashlib.sha256(case_id.encode()).hexdigest(),
                **paths,
                "source_sha256": _sha(source),
                "phase1_ledger_sha256": _sha(ledger),
                "expected_first_attempt_jobs": 11,
            }
        )
        for view_kind in SUPPORTED_VIEWS:
            packet_rel = (
                "research/reasoning-process-view-specific-interface-2026-07-11/cases/"
                f"{case_id}/{view_kind}/reader-packet.json"
            )
            packet_path = root / packet_rel
            wrapper = _load(packet_path)
            prompts = build_prompts_v3(wrapper)
            schema = response_schema_v3(view_kind)
            jobs.append(
                {
                    "job_id": f"phase4-{case_id}-{view_kind}",
                    "case_id": case_id,
                    "mechanism": "full_conversation_reader_v3",
                    "view_kind": view_kind,
                    "packet_path": packet_rel,
                    "packet_sha256": _sha(packet_path),
                    "input_utf8_bytes": wrapper["metrics"]["observed_input_utf8_bytes"],
                    "system_prompt_sha256": prompts["system_prompt_sha256"],
                    "user_prompt_sha256": prompts["user_prompt_sha256"],
                    "response_schema_sha256": _json_sha(schema),
                    "response_schema_metrics": schema_metrics(schema),
                    "maximum_output_records": 4,
                }
            )
        for window in local_by_case[case_id]["window_artifacts"]:
            packet_path = root / window["path"]
            wrapper = _load(packet_path)
            prompts = build_local_prompts(wrapper)
            schema = local_response_schema()
            jobs.append(
                {
                    "job_id": f"phase4-{case_id}-exploration-turn-{window['focal_turn_index']:03d}",
                    "case_id": case_id,
                    "mechanism": "local_exploration_v2",
                    "view_kind": "exploration_and_alternatives",
                    "focal_turn_index": window["focal_turn_index"],
                    "packet_path": window["path"],
                    "packet_sha256": _sha(packet_path),
                    "input_utf8_bytes": wrapper["metrics"]["input_utf8_bytes"],
                    "system_prompt_sha256": prompts["system_prompt_sha256"],
                    "user_prompt_sha256": prompts["user_prompt_sha256"],
                    "response_schema_sha256": _json_sha(schema),
                    "response_schema_metrics": schema_metrics(schema),
                    "maximum_output_records": 2,
                }
            )
    frozen = []
    for rel in (
        "docs/evals/reasoning-process-phase0-contract-v0.json",
        "docs/evals/reasoning-process-phase3-model-snapshot-v1.json",
        "engine/system_b/reasoning_process_view_specific_v3.py",
        "engine/system_b/reasoning_process_exploration_local.py",
        "engine/system_b/reasoning_process_exploration_local_custody.py",
        "research/reasoning-process-view-specific-v3-replay-2026-07-11/report.json",
        "research/reasoning-process-exploration-local-terminal-2026-07-11/terminal-result.json",
    ):
        frozen.append({"path": rel, "sha256": _sha(root / rel)})
    return {
        "schema_version": SCHEMA,
        "status": "frozen_before_transfer_provider_calls",
        "date": "2026-07-11",
        "run_id": "reasoning-process-phase4-two-case-transfer-v1",
        "purpose": "Test whether the five Case-02 development mechanisms transfer without tuning to two mechanically selected reviewed conversations.",
        "selection": {
            "development_case_excluded": DEVELOPMENT_CASE,
            "eligible_case_ids": list(ELIGIBLE_CASES),
            "rule": "ascending_sha256_of_case_id_take_first_two",
            "selected_case_ids": list(SELECTED_CASES),
            "selection_was_semantic": False,
        },
        "cases": cases,
        "jobs": jobs,
        "call_configuration": {
            "provider": "openrouter",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "model": MODEL,
            "wire_mode": "strict_json_schema",
            "temperature": 0.0,
            "seed": 0,
            "reasoning_enabled": False,
            "full_reader_max_output_tokens": 2400,
            "local_reader_max_output_tokens": 1200,
            "provider_timeout_seconds": 90,
            "require_supported_parameters": True,
            "allow_provider_fallbacks": False,
            "automatic_retries": 0,
            "response_healing": False,
            "parallel_calls": False,
        },
        "budget_amendment": {
            "reason": "The failed exploration family was decomposed from one overloaded call into seven bounded chronological calls; the four other semantic jobs are unchanged.",
            "original_two_case_transfer_calls_max": 10,
            "amended_first_attempt_transfer_calls_max": 22,
            "maximum_separately_frozen_operational_retries": 2,
            "maximum_total_provider_requests": 24,
            "maximum_estimated_cost_usd": 0.1,
            "semantic_retries": 0,
            "fallback_models": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "pipeline_calls": 0,
            "runtime_calls": 0,
        },
        "retry_policy": {
            "automatic_retry": False,
            "first_attempt_failure_preserved": True,
            "eligible_only_for_operational_failure": True,
            "semantic_or_schema_retry_forbidden": True,
            "separate_retry_contract_required": True,
            "retry_after_header_must_be_preserved_when_present": True,
            "maximum_one_operational_completion_per_case": True,
        },
        "success_requirements": {
            "eventual_case_completion_rate": 1.0,
            "exact_source_reference_validity_rate": 1.0,
            "candidate_terminal_custody_rate": 1.0,
            "protected_target_visible_rate_per_case": 1.0,
            "critical_dimension_zero_count_per_case": 0,
            "invalid_admitted_record_count": 0,
            "source_strength_inflation_count": 0,
            "context_invisible_label_count": 0,
            "first_attempt_operational_success_reported_separately": True,
            "duplicates_measured_not_semantically_merged": True,
            "source_first_review_required": True,
        },
        "stop_rules": [
            "no_prompt_or_schema_change_after_first_transfer_output",
            "no_completed_case_tuning",
            "no_semantic_retry",
            "no_fallback_or_response_healing",
            "stop_if_same_load_bearing_semantic_failure_occurs_in_both_cases",
            "stop_before_stability_repeats_if_either_case_fails_semantic_floor",
        ],
        "frozen_inputs": frozen,
        "boundary": {
            "protected_targets_seen_by_model": False,
            "source_review_addenda_seen_by_model": False,
            "semantic_deduplication_authorized": False,
            "global_synthesis_authorized": False,
            "quality_or_trust_score_authorized": False,
            "final_output_evaluation_authorized": False,
            "graph_or_runtime_authorized": False,
            "stability_repeat_calls_authorized": False,
        },
    }


def validate_contract(contract: dict[str, Any], root: Path) -> dict[str, Any]:
    rebuilt = build_contract(root)
    if contract != rebuilt:
        raise ValueError("frozen Phase-4 contract differs from provider-free rebuild")
    if len(contract["jobs"]) != 22:
        raise ValueError("Phase-4 transfer must contain 22 first-attempt jobs")
    counts = {case_id: 0 for case_id in SELECTED_CASES}
    for job in contract["jobs"]:
        counts[job["case_id"]] += 1
        if job["input_utf8_bytes"] > (24000 if job["mechanism"] == "full_conversation_reader_v3" else 8000):
            raise ValueError("job input exceeds its frozen budget")
        if job["response_schema_metrics"]["bytes"] > 12000 or job["response_schema_metrics"]["depth"] > 8:
            raise ValueError("provider schema exceeds frozen budget")
    if set(counts.values()) != {11}:
        raise ValueError("each transfer case must contain eleven jobs")
    return {
        "status": "phase4_transfer_provider_free_gate_pass",
        "selected_case_ids": list(SELECTED_CASES),
        "job_count": len(contract["jobs"]),
        "jobs_per_case": counts,
        "provider_calls_made": 0,
        "calls_authorized_by_validation": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = (ROOT / args.output).resolve() if not args.output.is_absolute() else args.output
    if args.check:
        result = validate_contract(_load(output), ROOT)
    else:
        contract = build_contract(ROOT)
        _write(output, contract)
        result = validate_contract(contract, ROOT)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
