#!/usr/bin/env python3
"""Run the smaller seed-only residual discovery and conditional coverage probe."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.system_b.residual_challenge_representation_v1 import (
    CANDIDATE_IDS,
    build_residual_coverage_packet_v1,
    build_residual_coverage_prompts_v1,
    compile_residual_coverage_response_v1,
    residual_coverage_response_schema_v1,
)
from engine.system_b.residual_challenge_seed_v1 import (
    build_residual_seed_prompts_v1,
    compile_residual_seed_response_v1,
    join_residual_seed_portfolio_v1,
    residual_seed_response_schema_v1,
)
from scripts.evals.run_residual_challenge_probe_v1 import (
    _row,
    _source,
    build_discovery_request,
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
from scripts.evals.run_simulated_reliability_lite_coverage_recovery_v1 import (
    provider_call_minimal,
)


SCHEMA = "lolla.residual_challenge_seed_probe_contract.v1"
AUTH_SCHEMA = "lolla.residual_challenge_seed_probe_authorization.v1"
RESULT_SCHEMA = "lolla.residual_challenge_seed_probe_result.v1"


def build_seed_request(contract: Mapping[str, Any]) -> dict[str, Any]:
    packet = build_discovery_request(contract)["packet"]
    return {
        "packet": packet,
        "prompts": build_residual_seed_prompts_v1(packet),
        "response_schema": residual_seed_response_schema_v1(),
    }


def request_attestation(contract: Mapping[str, Any]) -> dict[str, Any]:
    request = build_seed_request(contract)
    return {
        "packet_sha256": value_sha(request["packet"]),
        "user_evidence_count": len(request["packet"]["user_evidence"]),
        "system_prompt_sha256": request["prompts"]["system_prompt_sha256"],
        "user_prompt_sha256": request["prompts"]["user_prompt_sha256"],
        "response_schema_sha256": value_sha(request["response_schema"]),
        "coverage_response_schema_sha256_by_candidate": {
            candidate_id: value_sha(residual_coverage_response_schema_v1(candidate_id))
            for candidate_id in CANDIDATE_IDS
        },
    }


def _validate(contract_path: Path, authorization_path: Path) -> dict[str, Any]:
    contract = load(contract_path)
    if (
        contract.get("schema_version") != SCHEMA
        or contract.get("status") != "frozen_before_one_affordable_residual_seed_probe"
    ):
        raise V1RunError("residual seed contract is invalid")
    budget = contract.get("budget", {})
    if budget.get("maximum_provider_calls") != 4 or budget.get("automatic_retries") != 0:
        raise V1RunError("residual seed budget drifted")
    limits = contract.get("task_limits", {})
    if (
        limits.get("discovery", {}).get("reasoning_effort") != "low"
        or limits.get("coverage", {}).get("reasoning_effort") != "minimal"
    ):
        raise V1RunError("residual seed reasoning policy drifted")
    for row in contract["frozen_inputs"]:
        path = ROOT / row["path"]
        if not path.is_file() or file_sha(path) != row["sha256"]:
            raise V1RunError(f"frozen input drifted: {row['path']}")
    if request_attestation(contract) != contract["request_attestation"]:
        raise V1RunError("residual seed request bytes drifted")
    authorization = load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_by_founder_for_affordable_model_selection",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": file_sha(contract_path),
        "authorized_case_id": contract["case_id"],
        "maximum_provider_calls": 4,
        "maximum_provider_reported_cost_usd": budget["maximum_provider_reported_cost_usd"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
    }
    if authorization != expected:
        raise V1RunError("residual seed authorization drifted")
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
    runtime["task_limits"]["residual_seed_discovery"] = {
        **contract["task_limits"]["discovery"],
        "wire_mode": "strict_json_schema",
    }
    runtime["task_limits"]["residual_seed_coverage"] = {
        **contract["task_limits"]["coverage"],
        "wire_mode": "strict_json_schema",
    }
    runtime["seeds"]["residual_seed_discovery"] = contract["seed_base"] + 1
    for index, candidate_id in enumerate(CANDIDATE_IDS, 1):
        runtime["seeds"][f"residual_seed_coverage_{candidate_id}"] = contract["seed_base"] + 100 + index
    return runtime


def run(
    contract: Mapping[str, Any],
    *,
    output: Path,
    discovery_call_fn: Callable[..., dict[str, Any]] = provider_call,
    coverage_call_fn: Callable[..., dict[str, Any]] = provider_call_minimal,
) -> dict[str, Any]:
    runtime = _runtime(contract)
    operator = contract["operator"]
    request = build_seed_request(contract)
    discovery_dir = output / "discovery"
    discovery_dir.mkdir(parents=True, exist_ok=False)
    raw_discovery = discovery_call_fn(
        output=discovery_dir,
        ordinal=1,
        task_id="residual_seed_discovery",
        case_id=contract["case_id"],
        repeat_id="residual_seed_discovery",
        contract=runtime,
        prompts=request["prompts"],
        schema=request["response_schema"],
        schema_name="lolla_residual_seed_discovery_v1",
        compile_candidate=lambda candidate: compile_residual_seed_response_v1(
            response=candidate,
            packet=request["packet"],
            producer_id=operator["model"],
        ),
    )
    discovery_row = _row(raw_discovery)
    coverage_rows = []
    joined = None
    compiled_discovery = discovery_row.get("compiled")
    if isinstance(compiled_discovery, Mapping):
        _, evidence = _source(contract)
        compiled_coverage = []
        for index, candidate in enumerate(compiled_discovery["candidates"], 1):
            candidate_id = candidate["candidate_id"]
            item_dir = output / "coverage" / candidate_id
            item_dir.mkdir(parents=True, exist_ok=False)
            packet = build_residual_coverage_packet_v1(
                case_id=contract["case_id"],
                candidate=candidate,
                evidence_records=evidence,
            )
            write(item_dir / "packet.json", packet)
            prompts = build_residual_coverage_prompts_v1(packet)
            raw = coverage_call_fn(
                output=item_dir,
                ordinal=1 + index,
                task_id="residual_seed_coverage",
                case_id=contract["case_id"],
                repeat_id=f"residual_seed_coverage_{candidate_id}",
                contract=runtime,
                prompts=prompts,
                schema=residual_coverage_response_schema_v1(candidate_id),
                schema_name="lolla_residual_seed_coverage_" + candidate_id,
                compile_candidate=lambda response, packet=packet: compile_residual_coverage_response_v1(
                    response=response,
                    packet=packet,
                    producer_id=operator["model"],
                ),
            )
            row = {"candidate_id": candidate_id, **_row(raw)}
            coverage_rows.append(row)
            if isinstance(row.get("compiled"), Mapping):
                compiled_coverage.append(row["compiled"])
        if len(compiled_coverage) == len(coverage_rows):
            joined = join_residual_seed_portfolio_v1(
                seed_result=compiled_discovery,
                coverage_results=compiled_coverage,
            )
    rows = [discovery_row, *coverage_rows]
    calls = sum(int(row.get("provider_calls") or 0) for row in rows)
    costs = [
        float(row["provider_reported_cost_usd"])
        for row in rows
        if row.get("provider_reported_cost_usd") is not None
    ]
    total = round(sum(costs), 12) if len(costs) == calls else None
    report = {
        "schema_version": RESULT_SCHEMA,
        "status": "residual_seed_probe_preserved_source_review_required",
        "run_id": contract["run_id"],
        "case_id": contract["case_id"],
        "discovery_task": discovery_row,
        "coverage_tasks": coverage_rows,
        "joined_seed_portfolio": joined,
        "provider_calls": calls,
        "provider_reported_cost_usd": total,
        "cost_ceiling_met": total is not None and total <= contract["budget"]["maximum_provider_reported_cost_usd"],
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "enrichment_calls": 0,
        "source_review_status": "required",
        "runtime_effect": "none",
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
        raise V1RunError("residual seed output path must not exist")
    output.mkdir(parents=True)
    load_env(args.env_file.resolve())
    report = run(contract, output=output)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
