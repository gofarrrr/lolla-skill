#!/usr/bin/env python3
"""Run a frozen full-nine factored mechanism portfolio with conditional coverage."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_mechanism_factored_portfolio_v1 import (
    join_factored_mechanism_portfolio_v1,
    plan_assistant_coverage_calls_v1,
)
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
from engine.system_b.reasoning_mechanism_submicrotask_v1 import (
    assistant_coverage_response_schema_v1,
    build_assistant_coverage_packet_v1,
    build_assistant_coverage_prompts_v1,
    compile_assistant_coverage_response_v1,
)
from engine.system_b.reasoning_mechanism_user_factor_v1 import (
    build_user_factor_packet_v1,
    build_user_factor_prompts_v1,
    compile_user_factor_response_v1,
    user_factor_response_schema_v1,
)
from scripts.evals.run_simulated_reliability_case_v1 import (
    ROOT,
    V1RunError,
    file_sha,
    load,
    load_contract,
    load_env,
    provider_call,
    value_sha,
    write,
)


SCHEMA = "lolla.simulated_reliability_lite_full_factored_mechanisms_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_full_factored_mechanisms_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_full_factored_mechanisms_result.v1"


def _parent(contract: Mapping[str, Any]) -> dict[str, Any]:
    return load(ROOT / contract["inputs"]["parent_mechanism_request_path"])["packet"]


def _user_requests(contract: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    parent = _parent(contract)
    result = {}
    for mechanism_id in sorted(MECHANISMS):
        packet = build_user_factor_packet_v1(
            parent_packet=parent, mechanism_id=mechanism_id
        )
        result[mechanism_id] = {
            "packet": packet,
            "prompts": build_user_factor_prompts_v1(packet),
            "response_schema": user_factor_response_schema_v1(mechanism_id),
        }
    return result


def request_attestation(contract: Mapping[str, Any]) -> dict[str, Any]:
    requests = _user_requests(contract)
    return {
        mechanism_id: {
            "packet_sha256": value_sha(item["packet"]),
            "role_record_count": len(item["packet"]["role_records"]),
            "system_prompt_sha256": item["prompts"]["system_prompt_sha256"],
            "user_prompt_sha256": item["prompts"]["user_prompt_sha256"],
            "response_schema_sha256": value_sha(item["response_schema"]),
            "coverage_response_schema_sha256": value_sha(
                assistant_coverage_response_schema_v1(mechanism_id)
            ),
        }
        for mechanism_id, item in requests.items()
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected full-factored contract schema")
    if contract.get("status") != "frozen_before_one_full_factored_case":
        raise V1RunError("full-factored contract is not frozen")
    budget = contract.get("budget", {})
    if budget.get("maximum_provider_calls") != 18 or budget.get("automatic_retries") != 0:
        raise V1RunError("full-factored call or retry ceiling drifted")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("full-factored request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_case_id": contract["case_id"],
        "maximum_provider_calls": 18,
        "maximum_provider_reported_cost_usd": budget["maximum_provider_reported_cost_usd"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("full-factored authorization drifted")
    return contract


def _runtime(contract: Mapping[str, Any]) -> dict[str, Any]:
    runtime = copy.deepcopy(load_contract(ROOT / contract["base_runtime_contract"]["path"]))
    operator = contract["operator"]
    runtime["provider_request"]["model"] = operator["model"]
    runtime["provider_request"]["provider_order"] = [operator["provider_slug"]]
    runtime["provider_request"]["provider_only"] = [operator["provider_slug"]]
    runtime["provider_request"]["max_price_usd_per_million_tokens"] = dict(
        operator["maximum_price_usd_per_million_tokens"]
    )
    for task_id in ("mechanism_user_factor", "mechanism_assistant_coverage"):
        runtime["task_limits"][task_id] = {
            "max_output_tokens": contract["task_limit"]["max_output_tokens"],
            "reasoning_effort": contract["task_limit"]["reasoning_effort"],
            "wire_mode": "strict_json_schema",
        }
    for index, mechanism_id in enumerate(sorted(MECHANISMS), 1):
        runtime["seeds"][f"full_user_{index:02d}"] = contract["seed_base"] + index
        runtime["seeds"][f"full_coverage_{index:02d}"] = contract["seed_base"] + 100 + index
    return runtime


def _row(mechanism_id: str, result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "mechanism_id": mechanism_id,
        "operational_status": result.get("operational_status"),
        "compiled": result.get("compiled"),
        "validation_error": result.get("validation_error", ""),
        "served_model": result.get("served_model", ""),
        "served_provider": result.get("served_provider", ""),
        "provider_calls": result.get("provider_calls", 0),
        "provider_reported_cost_usd": result.get("provider_reported_cost_usd"),
        "duration_seconds": result.get("duration_seconds"),
        "usage": result.get("usage"),
    }


def run(
    contract: Mapping[str, Any], *, output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call,
) -> dict[str, Any]:
    runtime = _runtime(contract)
    operator = contract["operator"]
    requests = _user_requests(contract)
    user_rows = []
    for index, mechanism_id in enumerate(sorted(MECHANISMS), 1):
        item_dir = output / "user" / mechanism_id
        item_dir.mkdir(parents=True, exist_ok=False)
        request = requests[mechanism_id]
        raw = call_fn(
            output=item_dir,
            ordinal=index,
            task_id="mechanism_user_factor",
            case_id=contract["case_id"],
            repeat_id=f"full_user_{index:02d}",
            contract=runtime,
            prompts=request["prompts"],
            schema=request["response_schema"],
            schema_name="lolla_v1_user_factor_" + mechanism_id,
            compile_candidate=lambda candidate, packet=request["packet"]: compile_user_factor_response_v1(
                response=candidate, packet=packet, producer_id=operator["model"]
            ),
        )
        user_rows.append(_row(mechanism_id, raw))
    compiled_users = [row["compiled"] for row in user_rows if isinstance(row["compiled"], Mapping)]
    coverage_rows = []
    coverage_plan = None
    joined = None
    if len(compiled_users) == len(MECHANISMS):
        coverage_plan = plan_assistant_coverage_calls_v1(compiled_users)
        write(output / "coverage-call-plan.json", coverage_plan)
        parent = _parent(contract)
        user_by_id = {row["assessment"]["mechanism_id"]: row for row in compiled_users}
        for index, mechanism_id in enumerate(sorted(MECHANISMS), 1):
            if mechanism_id not in coverage_plan["assistant_coverage_call_mechanism_ids"]:
                continue
            item_dir = output / "coverage" / mechanism_id
            item_dir.mkdir(parents=True, exist_ok=False)
            packet = build_assistant_coverage_packet_v1(
                parent_packet=parent,
                user_status=user_by_id[mechanism_id]["assessment"],
            )
            write(item_dir / "packet.json", packet)
            prompts = build_assistant_coverage_prompts_v1(packet)
            raw = call_fn(
                output=item_dir,
                ordinal=len(MECHANISMS) + index,
                task_id="mechanism_assistant_coverage",
                case_id=contract["case_id"],
                repeat_id=f"full_coverage_{index:02d}",
                contract=runtime,
                prompts=prompts,
                schema=assistant_coverage_response_schema_v1(mechanism_id),
                schema_name="lolla_v1_coverage_" + mechanism_id,
                compile_candidate=lambda candidate, packet=packet: compile_assistant_coverage_response_v1(
                    response=candidate, packet=packet, producer_id=operator["model"]
                ),
            )
            coverage_rows.append(_row(mechanism_id, raw))
        compiled_coverage = [
            row["compiled"] for row in coverage_rows if isinstance(row["compiled"], Mapping)
        ]
        if len(compiled_coverage) == len(coverage_rows):
            joined = join_factored_mechanism_portfolio_v1(
                parent_packet=parent,
                user_results=compiled_users,
                assistant_coverage_results=compiled_coverage,
                producer_id=operator["model"],
            )
    rows = user_rows + coverage_rows
    calls = sum(int(row["provider_calls"] or 0) for row in rows)
    costs = [float(row["provider_reported_cost_usd"]) for row in rows if row["provider_reported_cost_usd"] is not None]
    total = round(sum(costs), 12) if len(costs) == calls else None
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "full_factored_case_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "user_factor_tasks": user_rows,
        "coverage_call_plan": coverage_plan,
        "assistant_coverage_tasks": coverage_rows,
        "joined": joined,
        "provider_calls": calls,
        "provider_reported_cost_usd": total,
        "cost_ceiling_met": total is not None and total <= contract["budget"]["maximum_provider_reported_cost_usd"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "runtime_effect": "none",
        "source_review_status": "required",
        "production_model_selected": False,
        "scalar_quality_score": None,
    }
    write(output / "result.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract = _validate(args.contract.resolve(), args.authorization.resolve())
    if args.dry_run:
        print(json.dumps({"status": "dry_run_valid", "provider_calls": 0}, indent=2))
        return 0
    output = args.output.resolve()
    if output.exists():
        raise V1RunError("full-factored output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
