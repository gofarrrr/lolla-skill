#!/usr/bin/env python3
"""Complete one preserved factored portfolio without rerunning successful calls."""

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
    value_sha,
    write,
)
from scripts.evals.run_simulated_reliability_lite_coverage_recovery_v1 import (
    provider_call_minimal,
)
from scripts.evals.run_simulated_reliability_lite_full_factored_mechanisms_v1 import (
    _row,
)


SCHEMA = "lolla.simulated_reliability_lite_factored_completion_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_factored_completion_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_factored_completion_result.v1"


def _inputs(contract: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    parent = load(ROOT / contract["inputs"]["parent_mechanism_request_path"])["packet"]
    partial = load(ROOT / contract["inputs"]["partial_full_case_result_path"])
    return parent, partial


def build_missing_user_request(contract: Mapping[str, Any]) -> dict[str, Any]:
    parent, _ = _inputs(contract)
    mechanism_id = contract["missing_user_mechanism_id"]
    packet = build_user_factor_packet_v1(
        parent_packet=parent,
        mechanism_id=mechanism_id,
    )
    return {
        "packet": packet,
        "prompts": build_user_factor_prompts_v1(packet),
        "response_schema": user_factor_response_schema_v1(mechanism_id),
    }


def request_attestation(contract: Mapping[str, Any]) -> dict[str, Any]:
    request = build_missing_user_request(contract)
    mechanism_id = contract["missing_user_mechanism_id"]
    return {
        "mechanism_id": mechanism_id,
        "packet_sha256": value_sha(request["packet"]),
        "role_record_count": len(request["packet"]["role_records"]),
        "system_prompt_sha256": request["prompts"]["system_prompt_sha256"],
        "user_prompt_sha256": request["prompts"]["user_prompt_sha256"],
        "response_schema_sha256": value_sha(request["response_schema"]),
        "coverage_response_schema_sha256_by_mechanism": {
            item: value_sha(assistant_coverage_response_schema_v1(item))
            for item in sorted(MECHANISMS)
        },
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if (
        contract.get("schema_version") != SCHEMA
        or contract.get("status") != "frozen_before_one_minimal_factored_completion"
    ):
        raise V1RunError("factored completion contract is invalid")
    budget = contract.get("budget", {})
    if budget.get("maximum_provider_calls") != 10 or budget.get("automatic_retries") != 0:
        raise V1RunError("factored completion budget drifted")
    if contract.get("task_limit", {}).get("reasoning_effort") != "minimal":
        raise V1RunError("factored completion requires minimal reasoning")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    parent, partial = _inputs(contract)
    del parent
    missing = [
        row["mechanism_id"]
        for row in partial["user_factor_tasks"]
        if not isinstance(row.get("compiled"), Mapping)
    ]
    if missing != [contract["missing_user_mechanism_id"]]:
        raise V1RunError("partial result does not contain exactly the authorized gap")
    if partial.get("assistant_coverage_tasks"):
        raise V1RunError("partial result unexpectedly contains coverage calls")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("factored completion request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_case_id": contract["case_id"],
        "authorized_missing_user_mechanism_id": contract["missing_user_mechanism_id"],
        "maximum_provider_calls": 10,
        "maximum_provider_reported_cost_usd": budget["maximum_provider_reported_cost_usd"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("factored completion authorization drifted")
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
            "reasoning_effort": "minimal",
            "wire_mode": "strict_json_schema",
        }
    runtime["seeds"]["missing_user"] = contract["seed_base"] + 1
    for index, mechanism_id in enumerate(sorted(MECHANISMS), 1):
        runtime["seeds"][f"completion_coverage_{index:02d}"] = contract["seed_base"] + 100 + index
    return runtime


def run(
    contract: Mapping[str, Any],
    *,
    output: Path,
    user_call_fn: Callable[..., dict[str, Any]] = provider_call_minimal,
    coverage_call_fn: Callable[..., dict[str, Any]] = provider_call_minimal,
) -> dict[str, Any]:
    parent, partial = _inputs(contract)
    runtime = _runtime(contract)
    operator = contract["operator"]
    mechanism_id = contract["missing_user_mechanism_id"]
    request = build_missing_user_request(contract)
    user_dir = output / "user" / mechanism_id
    user_dir.mkdir(parents=True, exist_ok=False)
    raw_user = user_call_fn(
        output=user_dir,
        ordinal=1,
        task_id="mechanism_user_factor",
        case_id=contract["case_id"],
        repeat_id="missing_user",
        contract=runtime,
        prompts=request["prompts"],
        schema=request["response_schema"],
        schema_name="lolla_v1_user_factor_completion_" + mechanism_id,
        compile_candidate=lambda candidate: compile_user_factor_response_v1(
            response=candidate,
            packet=request["packet"],
            producer_id=operator["model"],
        ),
    )
    user_row = _row(mechanism_id, raw_user)
    preserved_users = [
        row["compiled"]
        for row in partial["user_factor_tasks"]
        if isinstance(row.get("compiled"), Mapping)
    ]
    users = [*preserved_users]
    if isinstance(user_row.get("compiled"), Mapping):
        users.append(user_row["compiled"])
    plan = None
    coverage_rows: list[dict[str, Any]] = []
    joined = None
    if len(users) == len(MECHANISMS):
        plan = plan_assistant_coverage_calls_v1(users)
        write(output / "coverage-call-plan.json", plan)
        users_by_id = {row["assessment"]["mechanism_id"]: row for row in users}
        for index, coverage_id in enumerate(sorted(MECHANISMS), 1):
            if coverage_id not in plan["assistant_coverage_call_mechanism_ids"]:
                continue
            item_dir = output / "coverage" / coverage_id
            item_dir.mkdir(parents=True, exist_ok=False)
            packet = build_assistant_coverage_packet_v1(
                parent_packet=parent,
                user_status=users_by_id[coverage_id]["assessment"],
            )
            write(item_dir / "packet.json", packet)
            prompts = build_assistant_coverage_prompts_v1(packet)
            raw = coverage_call_fn(
                output=item_dir,
                ordinal=1 + index,
                task_id="mechanism_assistant_coverage",
                case_id=contract["case_id"],
                repeat_id=f"completion_coverage_{index:02d}",
                contract=runtime,
                prompts=prompts,
                schema=assistant_coverage_response_schema_v1(coverage_id),
                schema_name="lolla_v1_coverage_completion_" + coverage_id,
                compile_candidate=lambda candidate, packet=packet: compile_assistant_coverage_response_v1(
                    response=candidate,
                    packet=packet,
                    producer_id=operator["model"],
                ),
            )
            coverage_rows.append(_row(coverage_id, raw))
        compiled_coverage = [
            row["compiled"]
            for row in coverage_rows
            if isinstance(row.get("compiled"), Mapping)
        ]
        if len(compiled_coverage) == len(coverage_rows):
            joined = join_factored_mechanism_portfolio_v1(
                parent_packet=parent,
                user_results=users,
                assistant_coverage_results=compiled_coverage,
                producer_id=operator["model"],
            )
    rows = [user_row, *coverage_rows]
    calls = sum(int(row.get("provider_calls") or 0) for row in rows)
    costs = [
        float(row["provider_reported_cost_usd"])
        for row in rows
        if row.get("provider_reported_cost_usd") is not None
    ]
    total = round(sum(costs), 12) if len(costs) == calls else None
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "minimal_factored_completion_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "preserved_partial_result_path": contract["inputs"]["partial_full_case_result_path"],
        "preserved_user_factor_count": len(preserved_users),
        "recovered_user_factor_task": user_row,
        "coverage_call_plan": plan,
        "assistant_coverage_tasks": coverage_rows,
        "joined_full_portfolio": joined,
        "provider_calls": calls,
        "provider_reported_cost_usd": total,
        "combined_case_provider_calls": int(partial["provider_calls"]) + calls,
        "combined_case_provider_reported_cost_usd": (
            round(float(partial["provider_reported_cost_usd"]) + total, 12)
            if total is not None
            else None
        ),
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
        raise V1RunError("factored completion output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
