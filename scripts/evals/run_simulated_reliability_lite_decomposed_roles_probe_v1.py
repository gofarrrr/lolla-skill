#!/usr/bin/env python3
"""Run two frozen single-role Gemini Lite V1 extraction probes."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.reasoning_process_position_role_first_v23 import (
    build_position_role_packet_v23,
    build_position_role_prompts_v23,
    compile_position_role_response_v23,
    position_role_response_schema_v23,
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


SCHEMA = "lolla.simulated_reliability_lite_decomposed_roles_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_decomposed_roles_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_decomposed_roles_result.v1"
ROLES = ("current", "qualification")


def build_requests(contract: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    wrapper = load(ROOT / contract["source"]["position_wrapper_path"])
    result = {}
    for role in ROLES:
        packet = build_position_role_packet_v23(wrapper=wrapper, role=role)
        prompts = build_position_role_prompts_v23(packet)
        schema = position_role_response_schema_v23(role)
        result[role] = {"packet": packet, "prompts": prompts, "response_schema": schema}
    return result


def _request_attestation(requests: Mapping[str, Any]) -> dict[str, Any]:
    return {
        role: {
            "packet_sha256": value_sha(requests[role]["packet"]),
            "system_prompt_sha256": requests[role]["prompts"]["system_prompt_sha256"],
            "user_prompt_sha256": requests[role]["prompts"]["user_prompt_sha256"],
            "response_schema_sha256": value_sha(requests[role]["response_schema"]),
        }
        for role in ROLES
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected decomposed-role contract schema")
    if contract.get("status") != "frozen_before_two_single_role_calls":
        raise V1RunError("decomposed-role contract is not frozen")
    if contract.get("roles") != list(ROLES):
        raise V1RunError("decomposed-role assignment drifted")
    if contract.get("budget", {}).get("maximum_provider_calls") != 2:
        raise V1RunError("decomposed-role call ceiling drifted")
    if contract.get("budget", {}).get("automatic_retries") != 0:
        raise V1RunError("automatic retries are forbidden")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if _request_attestation(build_requests(contract)) != contract["request_attestation"]:
        raise V1RunError("decomposed-role request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_roles": list(ROLES),
        "maximum_provider_calls": 2,
        "maximum_provider_reported_cost_usd": contract["budget"][
            "maximum_provider_reported_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("decomposed-role authorization drifted")
    return contract


def run(
    contract: Mapping[str, Any],
    *,
    output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call,
) -> dict[str, Any]:
    requests = build_requests(contract)
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
    rows = []
    for ordinal, role in enumerate(ROLES, 1):
        role_dir = output / role
        role_dir.mkdir(parents=True, exist_ok=False)
        runtime["task_limits"][role] = {
            "max_output_tokens": contract["task_limits"][role]["max_output_tokens"],
            "reasoning_effort": contract["task_limits"][role]["reasoning_effort"],
            "wire_mode": "strict_json_schema",
        }
        repeat_id = contract["task_limits"][role]["repeat_id"]
        runtime["seeds"][repeat_id] = contract["task_limits"][role]["seed"]
        spec = requests[role]
        result = call_fn(
            output=role_dir,
            ordinal=ordinal,
            task_id=role,
            case_id=contract["source"]["case_id"],
            repeat_id=repeat_id,
            contract=runtime,
            prompts=spec["prompts"],
            schema=spec["response_schema"],
            schema_name=f"lolla_v1_{role}",
            compile_candidate=lambda candidate, packet=spec["packet"]: compile_position_role_response_v23(
                response=candidate,
                packet=packet,
                producer_kind="simulated_reliability_lite_decomposed_roles_probe_v1",
                producer_id=operator["model"],
            ),
        )
        compiled = result.get("compiled")
        observations = compiled.get("observations", []) if isinstance(compiled, Mapping) else []
        rows.append(
            {
                "role": role,
                "operational_status": result.get("operational_status"),
                "compiled": compiled,
                "admitted_observation_count": len(observations),
                "validation_error": result.get("validation_error", ""),
                "served_model": result.get("served_model", ""),
                "served_provider": result.get("served_provider", ""),
                "provider_calls": result.get("provider_calls", 0),
                "provider_reported_cost_usd": result.get(
                    "provider_reported_cost_usd"
                ),
                "duration_seconds": result.get("duration_seconds"),
            }
        )
    total_calls = sum(int(row["provider_calls"] or 0) for row in rows)
    known_costs = [
        float(row["provider_reported_cost_usd"])
        for row in rows
        if row["provider_reported_cost_usd"] is not None
    ]
    total_cost = round(sum(known_costs), 12) if len(known_costs) == total_calls else None
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "two_single_role_calls_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["source"]["case_id"],
        "roles": rows,
        "provider_calls": total_calls,
        "provider_reported_cost_usd": total_cost,
        "cost_ceiling_met": total_cost is not None
        and total_cost
        <= float(contract["budget"]["maximum_provider_reported_cost_usd"]),
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "deterministic_semantic_inference": False,
        "joined_for_runtime": False,
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
    parser.add_argument("--print-attestation", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.print_attestation:
        contract = load(args.contract.resolve())
        print(json.dumps(_request_attestation(build_requests(contract)), indent=2))
        return 0
    contract = _validate(args.contract.resolve(), args.authorization.resolve())
    if args.dry_run:
        print(json.dumps({"status": "dry_run_valid", "provider_calls": 0}, indent=2))
        return 0
    output = args.output.resolve()
    if output.exists():
        raise V1RunError("decomposed-role output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
