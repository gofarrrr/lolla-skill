#!/usr/bin/env python3
"""Run one frozen Gemini Lite mechanism-stage probe from the sealed role portfolio."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.simulated_reliability_v1 import (
    build_mechanism_input_v1,
    build_mechanism_prompts_v1,
    compile_mechanism_response_v1,
    mechanism_response_schema_v1,
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


SCHEMA = "lolla.simulated_reliability_lite_mechanism_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_mechanism_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_mechanism_result.v1"


def _stable_schema(value: Any, *, parent_key: str = "") -> Any:
    """Canonicalize unordered enum members without changing schema meaning."""

    if isinstance(value, Mapping):
        return {
            key: _stable_schema(item, parent_key=key) for key, item in value.items()
        }
    if isinstance(value, list):
        items = [_stable_schema(item) for item in value]
        return sorted(items) if parent_key == "enum" else items
    return value


def build_request(contract: Mapping[str, Any]) -> dict[str, Any]:
    joined = load(ROOT / contract["inputs"]["role_portfolio_path"])
    source_path = ROOT / contract["inputs"]["source_path"]
    packet = build_mechanism_input_v1(
        case_id=contract["case_id"],
        arm_id=contract["arm_id"],
        joined=joined,
        conversation=source_path.read_text(encoding="utf-8"),
        source_refs=[
            {
                "path": contract["inputs"]["source_path"],
                "sha256": contract["inputs"]["source_sha256"],
            }
        ],
    )
    prompts = build_mechanism_prompts_v1(packet)
    response_schema = _stable_schema(mechanism_response_schema_v1())
    return {"packet": packet, "prompts": prompts, "response_schema": response_schema}


def request_attestation(contract: Mapping[str, Any]) -> dict[str, Any]:
    request = build_request(contract)
    return {
        "packet_sha256": value_sha(request["packet"]),
        "controlled_mechanism_count": len(request["packet"]["controlled_mechanisms"]),
        "assistant_contribution_count": len(request["packet"]["assistant_contributions"]),
        "role_record_count": len(request["packet"]["role_records"]),
        "system_prompt_sha256": request["prompts"]["system_prompt_sha256"],
        "user_prompt_sha256": request["prompts"]["user_prompt_sha256"],
        "response_schema_sha256": value_sha(request["response_schema"]),
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA:
        raise V1RunError("unexpected Lite mechanism contract schema")
    if contract.get("status") != "frozen_before_one_mechanism_call":
        raise V1RunError("Lite mechanism contract is not frozen")
    if contract.get("budget", {}).get("maximum_provider_calls") != 1:
        raise V1RunError("Lite mechanism call ceiling drifted")
    if contract.get("budget", {}).get("automatic_retries") != 0:
        raise V1RunError("automatic retries are forbidden")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("Lite mechanism request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": contract["budget"][
            "maximum_provider_reported_cost_usd"
        ],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("Lite mechanism authorization drifted")
    return contract


def run(
    contract: Mapping[str, Any],
    *,
    output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call,
) -> dict[str, Any]:
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
    runtime["task_limits"]["mechanism"] = {
        "max_output_tokens": contract["task_limit"]["max_output_tokens"],
        "reasoning_effort": contract["task_limit"]["reasoning_effort"],
        "wire_mode": "json_object_schema_in_prompt",
    }
    runtime["seeds"][contract["repeat_id"]] = contract["seed"]
    request = build_request(contract)
    result = call_fn(
        output=output,
        ordinal=1,
        task_id="mechanism",
        case_id=contract["case_id"],
        repeat_id=contract["repeat_id"],
        contract=runtime,
        prompts=request["prompts"],
        schema=request["response_schema"],
        schema_name="lolla_v1_mechanism",
        compile_candidate=lambda candidate: compile_mechanism_response_v1(
            response=candidate,
            packet=request["packet"],
            producer_kind="simulated_reliability_lite_mechanism_probe_v1",
            producer_id=operator["model"],
        ),
    )
    cost = result.get("provider_reported_cost_usd")
    compiled = result.get("compiled")
    routing_nodes = (
        compiled.get("routing_projection", {}).get("pattern_nodes", [])
        if isinstance(compiled, Mapping)
        else []
    )
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "one_mechanism_call_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "operational_status": result.get("operational_status"),
        "compiled": compiled,
        "validation_error": result.get("validation_error", ""),
        "served_model": result.get("served_model", ""),
        "served_provider": result.get("served_provider", ""),
        "provider_calls": result.get("provider_calls", 0),
        "provider_reported_cost_usd": cost,
        "duration_seconds": result.get("duration_seconds"),
        "routing_node_count": len(routing_nodes),
        "routing_mechanism_ids": [row["mechanism_id"] for row in routing_nodes],
        "cost_ceiling_met": cost is not None
        and float(cost)
        <= float(contract["budget"]["maximum_provider_reported_cost_usd"]),
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "runtime_effect": "none",
        "source_review_status": "required",
        "production_model_selected": False,
        "scalar_quality_score": None,
    }
    write(output / "mechanism-request.json", request)
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
        raise V1RunError("Lite mechanism output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
