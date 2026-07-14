#!/usr/bin/env python3
"""Run the frozen independent retailer transcript-only/pressure pair."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.fresh_reasoning_pressure import (
    build_control_prompts,
    build_prompts,
    compile_control_response,
    compile_response,
    control_response_schema,
    response_schema,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes
from scripts.evals.reasoning_process_position_decomposition_transport import run_decomposed_task
from scripts.evals.run_conversation_state_microtask_probe import _load_env


REPORT = "research/independent-useful-fresh-pressure-pair-2026-07-12/report.json"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def validate(contract: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    if contract.get("status") != "frozen_before_exactly_two_fresh_no_retry_calls":
        raise RuntimeError("contract not frozen")
    budget = contract.get("budget", {})
    if budget.get("maximum_provider_calls") != 2 or budget.get("automatic_retries") != 0:
        raise RuntimeError("call budget is not exactly two with no retries")
    for frozen in contract.get("frozen_inputs", []):
        if sha(ROOT / frozen["path"]) != frozen["sha256"]:
            raise RuntimeError("frozen input drifted")
    report = load(ROOT / REPORT)
    control = load(ROOT / report["arms"]["control"]["packet_path"])
    pressure = load(ROOT / report["arms"]["pressure"]["packet_path"])
    control_prompts = build_control_prompts(control)
    pressure_prompts = build_prompts(pressure)
    candidate_ids = [row["model_id"] for row in pressure["pressure_portfolio"]]
    requests = (
        ("control", control, control_prompts, control_response_schema()),
        ("pressure", pressure, pressure_prompts, response_schema(candidate_ids)),
    )
    for name, _packet, prompts, schema in requests:
        arm = report["arms"][name]
        if sha(ROOT / arm["packet_path"]) != arm["packet_sha256"]:
            raise RuntimeError("packet drifted")
        if prompts["system_prompt_sha256"] != arm["system_prompt_sha256"]:
            raise RuntimeError("system prompt drifted")
        if prompts["user_prompt_sha256"] != arm["user_prompt_sha256"]:
            raise RuntimeError("user prompt drifted")
        if sha256_bytes(canonical_json_bytes(schema)) != arm["response_schema_sha256"]:
            raise RuntimeError("response schema drifted")
    if control["authoritative_conversation"] != pressure["authoritative_conversation"]:
        raise RuntimeError("authoritative conversations differ")
    if report["portfolio"]["candidate_ids"] != candidate_ids:
        raise RuntimeError("candidate inventory drifted")
    return report, control, pressure, control_prompts, pressure_prompts, candidate_ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = load(contract_path)
    report, control, pressure, control_prompts, pressure_prompts, candidate_ids = validate(contract)
    if args.dry_run:
        print(json.dumps({"status": "independent_useful_pair_contract_valid", "provider_calls": 0}, indent=2))
        return 0

    authorization = load(args.authorization.resolve())
    expected_authorization = {
        "schema_version": "lolla.independent_useful_fresh_pressure_pair_authorization.v1",
        "status": "authorized_once_after_provider_free_and_source_target_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 2,
        "automatic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "runtime_calls": 0,
    }
    if authorization != expected_authorization:
        raise RuntimeError("authorization drifted")
    output = args.output_dir.resolve()
    if not output.is_dir() or (output / "result.json").exists() or list(output.glob("call-*-started.json")):
        raise RuntimeError("output absent, complete, or already started")
    _load_env(args.env_file.resolve())

    calls: list[dict[str, Any]] = []
    jobs: tuple[tuple[str, dict[str, Any], dict[str, str], dict[str, Any], Callable[[dict[str, Any]], dict[str, Any]]], ...] = (
        (
            "control",
            control,
            control_prompts,
            control_response_schema(),
            lambda candidate: compile_control_response(response=candidate, packet=control),
        ),
        (
            "pressure",
            pressure,
            pressure_prompts,
            response_schema(candidate_ids),
            lambda candidate: compile_response(response=candidate, packet=pressure),
        ),
    )
    for index, (arm, _packet, prompts, schema, compiler) in enumerate(jobs, 1):
        write(
            output / f"call-{index:02d}-started.json",
            {"run_id": contract["run_id"], "task_id": arm, "fresh_context": True, "automatic_retries": 0},
        )
        call = run_decomposed_task(
            task_id=arm,
            contract=contract,
            prompts=prompts,
            schema=schema,
            response_schema_name=f"lolla_independent_useful_fresh_{arm}",
            compile_candidate=compiler,
        )
        write(output / f"call-{index:02d}-result.json", call)
        calls.append(call)

    by_id = {call["task_id"]: call for call in calls}
    pressure_compiled = by_id["pressure"].get("compiled")
    control_compiled = by_id["control"].get("compiled")
    gates = {
        "both_operational": all(call.get("operational_status") == "ok" and call.get("compiled") for call in calls),
        "pressure_complete_dispositions": bool(pressure_compiled)
        and pressure_compiled["all_candidates_accounted_for"]
        and len(pressure_compiled["candidate_dispositions"]) == len(candidate_ids),
        "control_no_external_portfolio": bool(control_compiled)
        and control_compiled["external_pressure_portfolio_included"] is False,
        "self_contained_answers": bool(
            pressure_compiled
            and pressure_compiled["reconsidered_answer"].strip()
            and control_compiled
            and control_compiled["reconsidered_answer"].strip()
        ),
        "rejected_no_material_effect": bool(pressure_compiled)
        and all(
            row["effect"] == "no_material_effect"
            for row in pressure_compiled["candidate_dispositions"]
            if row["disposition"] == "reject"
        ),
    }
    result = {
        "schema_version": "lolla.independent_useful_fresh_pressure_pair_result.v1",
        "status": "frozen_pair_preserved",
        "calls": calls,
        "evaluation": {
            "status": "mechanical_gates_pass_source_review_required" if all(gates.values()) else "mechanical_gate_failure",
            "gates": gates,
            "disposition_counts": (
                {
                    disposition: sum(
                        row["disposition"] == disposition for row in pressure_compiled["candidate_dispositions"]
                    )
                    for disposition in ("apply", "reject", "park")
                }
                if pressure_compiled
                else {}
            ),
            "scalar_score": None,
            "independent_value_status": "source_review_required",
        },
        "provider_request_count": sum(call.get("provider_calls", 0) for call in calls),
        "estimated_cost_usd": round(sum(float(call.get("estimated_cost_usd") or 0) for call in calls), 12),
        "boundary": contract["boundary"],
    }
    write(output / "result.json", result)
    print(
        json.dumps(
            {
                "provider_request_count": result["provider_request_count"],
                "estimated_cost_usd": result["estimated_cost_usd"],
                "evaluation": result["evaluation"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
