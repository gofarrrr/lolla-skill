#!/usr/bin/env python3
"""Run one frozen split user-status and assistant-coverage mechanism probe."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_mechanism_submicrotask_v1 import (
    assistant_coverage_response_schema_v1,
    build_assistant_coverage_packet_v1,
    build_assistant_coverage_prompts_v1,
    build_user_status_packet_v1,
    build_user_status_prompts_v1,
    compile_assistant_coverage_response_v1,
    compile_user_status_response_v1,
    join_split_mechanism_assessment_v1,
    user_status_response_schema_v1,
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


SCHEMA = "lolla.simulated_reliability_lite_mechanism_split_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_mechanism_split_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_mechanism_split_result.v1"


def parent_packet(contract: Mapping[str, Any]) -> dict[str, Any]:
    return load(ROOT / contract["inputs"]["parent_mechanism_request_path"])["packet"]


def first_request(contract: Mapping[str, Any]) -> dict[str, Any]:
    packet = build_user_status_packet_v1(
        parent_packet=parent_packet(contract), mechanism_id=contract["mechanism_id"]
    )
    return {
        "packet": packet,
        "prompts": build_user_status_prompts_v1(packet),
        "response_schema": user_status_response_schema_v1(contract["mechanism_id"]),
    }


def request_attestation(contract: Mapping[str, Any]) -> dict[str, Any]:
    request = first_request(contract)
    return {
        "user_status_packet_sha256": value_sha(request["packet"]),
        "user_status_role_record_count": len(request["packet"]["role_records"]),
        "user_status_system_prompt_sha256": request["prompts"]["system_prompt_sha256"],
        "user_status_user_prompt_sha256": request["prompts"]["user_prompt_sha256"],
        "user_status_response_schema_sha256": value_sha(request["response_schema"]),
        "assistant_coverage_response_schema_sha256": value_sha(
            assistant_coverage_response_schema_v1(contract["mechanism_id"])
        ),
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected split-mechanism contract schema")
    if contract.get("status") != "frozen_before_failed_mechanism_split_probe":
        raise V1RunError("split-mechanism contract is not frozen")
    if contract.get("budget", {}).get("maximum_provider_calls") != 2:
        raise V1RunError("split-mechanism call ceiling drifted")
    if contract.get("budget", {}).get("automatic_retries") != 0:
        raise V1RunError("automatic retries are forbidden")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("split-mechanism request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_mechanism_id": contract["mechanism_id"],
        "maximum_provider_calls": 2,
        "maximum_provider_reported_cost_usd": contract["budget"][
            "maximum_provider_reported_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("split-mechanism authorization drifted")
    return contract


def _task_runtime(contract: Mapping[str, Any]) -> dict[str, Any]:
    runtime = copy.deepcopy(
        load_contract(ROOT / contract["base_runtime_contract"]["path"])
    )
    operator = contract["operator"]
    runtime["provider_request"]["model"] = operator["model"]
    runtime["provider_request"]["provider_order"] = [operator["provider_slug"]]
    runtime["provider_request"]["provider_only"] = [operator["provider_slug"]]
    runtime["provider_request"]["max_price_usd_per_million_tokens"] = dict(
        operator["maximum_price_usd_per_million_tokens"]
    )
    for task_id in ("mechanism_user_status", "mechanism_assistant_coverage"):
        runtime["task_limits"][task_id] = {
            "max_output_tokens": contract["task_limit"]["max_output_tokens"],
            "reasoning_effort": contract["task_limit"]["reasoning_effort"],
            "wire_mode": "strict_json_schema",
        }
    runtime["seeds"]["split_user_status"] = contract["seeds"]["user_status"]
    runtime["seeds"]["split_assistant_coverage"] = contract["seeds"][
        "assistant_coverage"
    ]
    return runtime


def _row(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "operational_status": result.get("operational_status"),
        "compiled": result.get("compiled"),
        "validation_error": result.get("validation_error", ""),
        "served_model": result.get("served_model", ""),
        "served_provider": result.get("served_provider", ""),
        "provider_calls": result.get("provider_calls", 0),
        "provider_reported_cost_usd": result.get("provider_reported_cost_usd"),
        "duration_seconds": result.get("duration_seconds"),
    }


def run(
    contract: Mapping[str, Any], *, output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call,
) -> dict[str, Any]:
    runtime = _task_runtime(contract)
    operator = contract["operator"]
    parent = parent_packet(contract)
    first = first_request(contract)
    user_raw = call_fn(
        output=output,
        ordinal=1,
        task_id="mechanism_user_status",
        case_id=contract["case_id"],
        repeat_id="split_user_status",
        contract=runtime,
        prompts=first["prompts"],
        schema=first["response_schema"],
        schema_name="lolla_v1_mechanism_user_status",
        compile_candidate=lambda candidate: compile_user_status_response_v1(
            response=candidate,
            packet=first["packet"],
            producer_id=operator["model"],
        ),
    )
    user = _row(user_raw)
    coverage: dict[str, Any] | None = None
    joined = None
    if isinstance(user.get("compiled"), Mapping):
        coverage_packet = build_assistant_coverage_packet_v1(
            parent_packet=parent,
            user_status=user["compiled"]["assessment"],
        )
        write(output / "assistant-coverage-packet.json", coverage_packet)
        coverage_prompts = build_assistant_coverage_prompts_v1(coverage_packet)
        coverage_raw = call_fn(
            output=output,
            ordinal=2,
            task_id="mechanism_assistant_coverage",
            case_id=contract["case_id"],
            repeat_id="split_assistant_coverage",
            contract=runtime,
            prompts=coverage_prompts,
            schema=assistant_coverage_response_schema_v1(contract["mechanism_id"]),
            schema_name="lolla_v1_mechanism_assistant_coverage",
            compile_candidate=lambda candidate: compile_assistant_coverage_response_v1(
                response=candidate,
                packet=coverage_packet,
                producer_id=operator["model"],
            ),
        )
        coverage = _row(coverage_raw)
        if isinstance(coverage.get("compiled"), Mapping):
            joined = join_split_mechanism_assessment_v1(
                user_result=user["compiled"], coverage_result=coverage["compiled"]
            )
    rows = [user] + ([coverage] if coverage is not None else [])
    calls = sum(int(row.get("provider_calls") or 0) for row in rows)
    costs = [
        float(row["provider_reported_cost_usd"])
        for row in rows
        if row.get("provider_reported_cost_usd") is not None
    ]
    total_cost = round(sum(costs), 12) if len(costs) == calls else None
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "split_mechanism_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "mechanism_id": contract["mechanism_id"],
        "user_status_task": user,
        "assistant_coverage_task": coverage,
        "joined": joined,
        "provider_calls": calls,
        "provider_reported_cost_usd": total_cost,
        "cost_ceiling_met": total_cost is not None
        and total_cost <= contract["budget"]["maximum_provider_reported_cost_usd"],
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
        raise V1RunError("split-mechanism output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
