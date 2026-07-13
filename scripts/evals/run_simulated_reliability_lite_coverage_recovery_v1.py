#!/usr/bin/env python3
"""Run one frozen minimal-reasoning coverage recovery and provider-free portfolio join."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib import error, request

from engine.system_b.reasoning_mechanism_factored_portfolio_v1 import (
    join_factored_mechanism_portfolio_v1,
)
from engine.system_b.reasoning_mechanism_submicrotask_v1 import (
    assistant_coverage_response_schema_v1,
    build_assistant_coverage_packet_v1,
    build_assistant_coverage_prompts_v1,
    compile_assistant_coverage_response_v1,
)
from scripts.evals.run_simulated_reliability_case_v1 import (
    ROOT,
    V1RunError,
    file_sha,
    extract_object,
    load,
    load_contract,
    load_env,
    value_sha,
    write,
)


SCHEMA = "lolla.simulated_reliability_lite_coverage_recovery_contract.v1"
AUTH_SCHEMA = "lolla.simulated_reliability_lite_coverage_recovery_authorization.v1"
RESULT_SCHEMA = "lolla.simulated_reliability_lite_coverage_recovery_result.v1"


def provider_call_minimal(
    *, output: Path, ordinal: int, task_id: str, case_id: str, repeat_id: str,
    contract: Mapping[str, Any], prompts: Mapping[str, str], schema: Mapping[str, Any],
    schema_name: str, compile_candidate: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    """Preserved provider-call shape with the current minimal effort added locally."""

    config = contract["provider_request"]
    task = contract["task_limits"][task_id]
    if task.get("reasoning_effort") != "minimal":
        raise V1RunError("coverage recovery requires minimal reasoning")
    if task.get("wire_mode") != "strict_json_schema":
        raise V1RunError("coverage recovery requires strict JSON schema")
    seed = int(contract["seeds"][repeat_id])
    provider = {
        "order": list(config["provider_order"]),
        "only": list(config["provider_only"]),
        "allow_fallbacks": False,
        "require_parameters": True,
        "data_collection": "deny",
        "zdr": True,
        "max_price": dict(config["max_price_usd_per_million_tokens"]),
    }
    body = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
        "provider": provider,
        "seed": seed,
        "max_tokens": task["max_output_tokens"],
        "reasoning": {"effort": "minimal", "exclude": True},
        "stream": False,
    }
    prefix = f"call-{ordinal:02d}-{task_id}"
    started_path = output / f"{prefix}-started.json"
    result_path = output / f"{prefix}-result.json"
    if started_path.exists() or result_path.exists():
        raise V1RunError(f"call artifact already exists: {prefix}")
    base = {
        "task_id": task_id,
        "case_id": case_id,
        "repeat_id": repeat_id,
        "requested_model": config["model"],
        "provider_order": provider["order"],
        "provider_only": provider["only"],
        "zdr": True,
        "data_collection": "deny",
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "temperature_supplied": False,
        "top_p_supplied": False,
        "seed": seed,
        "reasoning_effort": "minimal",
        "reasoning_content_excluded": True,
        "max_output_tokens": task["max_output_tokens"],
        "wire_mode": "strict_json_schema",
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "base_user_prompt_sha256": prompts["user_prompt_sha256"],
        "effective_user_prompt_sha256": prompts["user_prompt_sha256"],
        "response_schema_sha256": value_sha(schema),
        "request_body_sha256": value_sha(body),
    }
    write(started_path, {**base, "status": "started_before_network_transport", "started_at_unix": time.time()})
    api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        result = {**base, "operational_status": "missing_api_key", "provider_calls": 0}
        write(result_path, result)
        return result
    req = request.Request(
        config["endpoint"],
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.monotonic()
    try:
        with request.urlopen(req, timeout=config["timeout_seconds"]) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            error_payload = json.loads(raw)
        except json.JSONDecodeError:
            error_payload = {"message": raw[:3000]}
        result = {
            **base, "operational_status": f"http_error_{exc.code}", "http_status": exc.code,
            "provider_calls": 1, "provider_error": error_payload,
            "provider_payload_sha256": value_sha(error_payload),
            "duration_seconds": round(time.monotonic() - started, 3),
        }
        write(result_path, result)
        return result
    except Exception as exc:  # noqa: BLE001
        result = {
            **base, "operational_status": "transport_error", "provider_calls": 1,
            "error_type": type(exc).__name__, "error_message": str(exc)[:1000],
            "duration_seconds": round(time.monotonic() - started, 3),
        }
        write(result_path, result)
        return result
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    choice = choices[0] if choices and isinstance(choices[0], Mapping) else {}
    message = choice.get("message") if isinstance(choice.get("message"), Mapping) else {}
    content = str(message.get("content", ""))
    candidate = None
    compiled = None
    validation_error = ""
    try:
        candidate = extract_object(content)
        compiled = compile_candidate(candidate)
    except Exception as exc:  # noqa: BLE001
        validation_error = f"{type(exc).__name__}: {exc}"
    usage = payload.get("usage") if isinstance(payload.get("usage"), Mapping) else {}
    result = {
        **base,
        "operational_status": "ok" if compiled is not None else "local_validation_failed",
        "provider_calls": 1,
        "served_model": str(payload.get("model", "")),
        "served_provider": str(payload.get("provider", "")),
        "generation_id": str(payload.get("id", "")),
        "finish_reason": str(choice.get("finish_reason", "")),
        "usage": dict(usage),
        "provider_reported_cost_usd": usage.get("cost"),
        "raw_content": content,
        "raw_content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "candidate": candidate,
        "compiled": compiled,
        "validation_error": validation_error,
        "provider_payload_sha256": value_sha(payload),
        "reasoning_content_returned": bool(message.get("reasoning") or message.get("reasoning_details")),
        "duration_seconds": round(time.monotonic() - started, 3),
    }
    write(result_path, result)
    return result


def _inputs(contract: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    parent = load(ROOT / contract["inputs"]["parent_mechanism_request_path"])["packet"]
    full = load(ROOT / contract["inputs"]["failed_full_case_result_path"])
    return parent, full


def build_request(contract: Mapping[str, Any]) -> dict[str, Any]:
    parent, full = _inputs(contract)
    mechanism_id = contract["mechanism_id"]
    row = next(
        item for item in full["user_factor_tasks"] if item["mechanism_id"] == mechanism_id
    )
    if not isinstance(row.get("compiled"), Mapping):
        raise V1RunError("coverage recovery lacks compiled user factor")
    packet = build_assistant_coverage_packet_v1(
        parent_packet=parent, user_status=row["compiled"]["assessment"]
    )
    return {
        "packet": packet,
        "prompts": build_assistant_coverage_prompts_v1(packet),
        "response_schema": assistant_coverage_response_schema_v1(mechanism_id),
    }


def request_attestation(contract: Mapping[str, Any]) -> dict[str, Any]:
    request = build_request(contract)
    return {
        "packet_sha256": value_sha(request["packet"]),
        "assistant_contribution_count": len(request["packet"]["assistant_contributions"]),
        "system_prompt_sha256": request["prompts"]["system_prompt_sha256"],
        "user_prompt_sha256": request["prompts"]["user_prompt_sha256"],
        "response_schema_sha256": value_sha(request["response_schema"]),
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if contract.get("schema_version") != SCHEMA or contract.get("status") != "frozen_before_one_minimal_coverage_recovery":
        raise V1RunError("coverage recovery contract is invalid")
    if contract.get("budget", {}).get("maximum_provider_calls") != 1:
        raise V1RunError("coverage recovery call ceiling drifted")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("coverage recovery request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_case_id": contract["case_id"],
        "authorized_mechanism_id": contract["mechanism_id"],
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": contract["budget"]["maximum_provider_reported_cost_usd"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("coverage recovery authorization drifted")
    return contract


def run(
    contract: Mapping[str, Any], *, output: Path,
    call_fn: Callable[..., dict[str, Any]] = provider_call_minimal,
) -> dict[str, Any]:
    parent, full = _inputs(contract)
    runtime = copy.deepcopy(load_contract(ROOT / contract["base_runtime_contract"]["path"]))
    operator = contract["operator"]
    runtime["provider_request"]["model"] = operator["model"]
    runtime["provider_request"]["provider_order"] = [operator["provider_slug"]]
    runtime["provider_request"]["provider_only"] = [operator["provider_slug"]]
    runtime["provider_request"]["max_price_usd_per_million_tokens"] = dict(operator["maximum_price_usd_per_million_tokens"])
    runtime["task_limits"]["mechanism_assistant_coverage"] = {
        "max_output_tokens": contract["task_limit"]["max_output_tokens"],
        "reasoning_effort": contract["task_limit"]["reasoning_effort"],
        "wire_mode": "strict_json_schema",
    }
    runtime["seeds"]["coverage_recovery"] = contract["seed"]
    request = build_request(contract)
    raw = call_fn(
        output=output,
        ordinal=1,
        task_id="mechanism_assistant_coverage",
        case_id=contract["case_id"],
        repeat_id="coverage_recovery",
        contract=runtime,
        prompts=request["prompts"],
        schema=request["response_schema"],
        schema_name="lolla_v1_coverage_recovery",
        compile_candidate=lambda candidate: compile_assistant_coverage_response_v1(
            response=candidate,
            packet=request["packet"],
            producer_id=operator["model"],
        ),
    )
    recovered = raw.get("compiled")
    joined = None
    if isinstance(recovered, Mapping):
        user_results = [
            row["compiled"] for row in full["user_factor_tasks"]
            if isinstance(row.get("compiled"), Mapping)
        ]
        existing_coverage = [
            row["compiled"] for row in full["assistant_coverage_tasks"]
            if isinstance(row.get("compiled"), Mapping)
        ]
        joined = join_factored_mechanism_portfolio_v1(
            parent_packet=parent,
            user_results=user_results,
            assistant_coverage_results=[*existing_coverage, recovered],
            producer_id=operator["model"],
        )
    cost = raw.get("provider_reported_cost_usd")
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "coverage_recovery_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "mechanism_id": contract["mechanism_id"],
        "operational_status": raw.get("operational_status"),
        "compiled": recovered,
        "validation_error": raw.get("validation_error", ""),
        "usage": raw.get("usage"),
        "provider_calls": raw.get("provider_calls", 0),
        "provider_reported_cost_usd": cost,
        "cost_ceiling_met": cost is not None and cost <= contract["budget"]["maximum_provider_reported_cost_usd"],
        "joined_full_portfolio": joined,
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
        raise V1RunError("coverage recovery output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
