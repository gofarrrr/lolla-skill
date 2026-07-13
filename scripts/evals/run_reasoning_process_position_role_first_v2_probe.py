#!/usr/bin/env python3
"""Run one frozen new-case role-first v2 probe through OpenRouter."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v2 import (  # noqa: E402
    ROLE_ORDER,
    build_position_relation_packet_v2,
    build_position_relation_prompts_v2,
    build_position_role_packet_v2,
    build_position_role_prompts_v2,
    compile_position_relation_response_v2,
    compile_position_role_response_v2,
    join_position_role_first_v2,
    position_relation_response_schema_v2,
    position_role_response_schema_v2,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals.reasoning_process_position_decomposition_transport import (  # noqa: E402
    run_decomposed_task,
)
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha, _write  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_position_role_first_probe_contract.v2"
AUTH_SCHEMA = "lolla.reasoning_process_position_role_first_probe_authorization.v2"


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected role-first v2 probe contract")
    if contract.get("status") != "frozen_before_at_most_four_new_case_calls":
        raise RuntimeError("role-first v2 probe contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("new-case packet drifted")
    wrapper = _load(packet_path)
    role_contracts = {}
    for role in ROLE_ORDER:
        packet = build_position_role_packet_v2(wrapper=wrapper, role=role)
        prompts = build_position_role_prompts_v2(packet)
        role_contracts[role] = {
            "system_prompt_sha256": prompts["system_prompt_sha256"],
            "user_prompt_sha256": prompts["user_prompt_sha256"],
            "response_schema_sha256": sha256_bytes(
                canonical_json_bytes(position_role_response_schema_v2(role))
            ),
        }
    if job["role_request_contracts"] != role_contracts:
        raise RuntimeError("role request contracts drifted")
    relation_schema_sha = sha256_bytes(
        canonical_json_bytes(position_relation_response_schema_v2())
    )
    if job["relation_response_schema_sha256"] != relation_schema_sha:
        raise RuntimeError("relation schema drifted")
    if (
        job["case_id"] != "amb3-case01-journalism-platform-pilot"
        or job["model"] != "deepseek/deepseek-v4-flash"
        or job["provider_slug"] != "alibaba"
    ):
        raise RuntimeError("new case or exact model/operator pair drifted")
    if contract["budget"] != {
        "maximum_provider_calls": 4,
        "maximum_estimated_cost_usd": 0.01,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise RuntimeError("role-first v2 probe budget drifted")
    if contract["call_configuration"] != {
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "wire_mode": "strict_json_schema",
        "temperature": 0.0,
        "seed": 0,
        "reasoning_enabled": False,
        "max_output_tokens": 1200,
        "provider_timeout_seconds": 90,
        "require_supported_parameters": True,
        "allow_provider_fallbacks": False,
        "automatic_retries": 0,
        "response_healing": False,
        "parallel_calls": False,
    }:
        raise RuntimeError("role-first v2 call configuration drifted")
    return {
        "status": "position_role_first_v2_probe_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_new_case_target_and_role_first_local_gates",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 4,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if value != expected:
        raise RuntimeError("role-first v2 authorization drifted")


def _started(output: Path, *, contract: dict, task_id: str) -> None:
    _write(
        output,
        {
            "schema_version": "lolla.reasoning_process_role_first_call_started.v2",
            "status": "provider_call_may_have_started_do_not_rerun_if_result_missing",
            "run_id": contract["run_id"],
            "task_id": task_id,
            "model": contract["job"]["model"],
            "provider_slug": contract["job"]["provider_slug"],
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


def _call_passed(call: dict) -> bool:
    return (
        call.get("operational_status") == "ok"
        and call.get("wire_schema_accepted") is True
        and call.get("provider_attribution_status") == "matched"
        and call.get("admitted_record_count", 0) >= 1
        and call.get("quarantined_record_count", 0) == 0
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output_dir is None:
        raise RuntimeError("execution arguments are missing")
    validate_authorization(
        _load(args.authorization.resolve()), contract=contract, contract_path=contract_path
    )
    output_dir = args.output_dir.resolve()
    if not output_dir.is_dir() or (output_dir / "result.json").exists():
        raise RuntimeError("role-first output directory is absent or already complete")
    if list(output_dir.glob("call-*-started.json")) or list(output_dir.glob("call-*-result.json")):
        raise RuntimeError("a role-first call already started; rerun forbidden")
    _load_env(args.env_file.resolve())
    wrapper = _load(ROOT / contract["job"]["packet_path"])
    calls = []
    role_compiled = {}
    failed_roles = []
    next_call = 1
    for role in ROLE_ORDER:
        task_id = f"role-{role}"
        packet = build_position_role_packet_v2(wrapper=wrapper, role=role)
        prompts = build_position_role_prompts_v2(packet)
        _write(output_dir / f"role-packet-{role}.json", packet)
        _write(
            output_dir / f"role-prompt-manifest-{role}.json",
            {
                "role": role,
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
                "response_schema_sha256": sha256_bytes(
                    canonical_json_bytes(position_role_response_schema_v2(role))
                ),
            },
        )
        _started(
            output_dir / f"call-{next_call:02d}-started.json",
            contract=contract,
            task_id=task_id,
        )
        call = run_decomposed_task(
            task_id=task_id,
            contract=contract,
            prompts=prompts,
            schema=position_role_response_schema_v2(role),
            response_schema_name=f"lolla_position_role_{role}_v2",
            compile_candidate=lambda candidate, packet=packet, role=role, prompts=prompts: compile_position_role_response_v2(
                response=candidate,
                packet=packet,
                producer_kind="model_operator_eval",
                producer_id=contract["job"]["model"],
                call_metadata={
                    "call_id": f"role-{role}",
                    "model": contract["job"]["model"],
                    "prompt_sha256": "sha256:" + prompts["user_prompt_sha256"],
                },
            ),
        )
        _write(output_dir / f"call-{next_call:02d}-result.json", call)
        calls.append(call)
        if call.get("compiled") is not None:
            role_compiled[role] = call["compiled"]
        if not _call_passed(call):
            failed_roles.append(role)
        next_call += 1

    relation_call = None
    relation_compiled = None
    relation_block_reason = ""
    if failed_roles or set(role_compiled) != set(ROLE_ORDER):
        relation_block_reason = "one_or_more_role_wire_or_admission_gates_failed"
    else:
        relation_packet = build_position_relation_packet_v2(
            role_compiled_by_role=role_compiled
        )
        relation_prompts = build_position_relation_prompts_v2(relation_packet)
        _write(output_dir / "relation-packet.json", relation_packet)
        _write(
            output_dir / "relation-prompt-manifest.json",
            {
                "system_prompt_sha256": relation_prompts["system_prompt_sha256"],
                "user_prompt_sha256": relation_prompts["user_prompt_sha256"],
                "response_schema_sha256": sha256_bytes(
                    canonical_json_bytes(position_relation_response_schema_v2())
                ),
            },
        )
        _started(
            output_dir / f"call-{next_call:02d}-started.json",
            contract=contract,
            task_id="relation",
        )
        relation_call = run_decomposed_task(
            task_id="relation",
            contract=contract,
            prompts=relation_prompts,
            schema=position_relation_response_schema_v2(),
            response_schema_name="lolla_position_relation_v2",
            compile_candidate=lambda candidate: compile_position_relation_response_v2(
                response=candidate,
                packet=relation_packet,
                producer_kind="model_operator_eval",
                producer_id=contract["job"]["model"],
            ),
        )
        _write(output_dir / f"call-{next_call:02d}-result.json", relation_call)
        calls.append(relation_call)
        relation_compiled = relation_call.get("compiled")
        if not _call_passed(relation_call):
            relation_block_reason = "relation_wire_or_admission_gate_failed"

    joined = (
        join_position_role_first_v2(
            role_compiled_by_role=role_compiled,
            relation_compiled=relation_compiled,
        )
        if set(role_compiled) == set(ROLE_ORDER)
        else None
    )
    aggregate = {
        "schema_version": "lolla.reasoning_process_position_role_first_probe_result.v2",
        "status": "new_case_role_first_probe_preserved",
        "run_id": contract["run_id"],
        "calls": calls,
        "provider_request_count": sum(item.get("provider_calls", 0) for item in calls),
        "estimated_cost_usd": round(
            sum(float(item.get("estimated_cost_usd") or 0) for item in calls), 12
        ),
        "provider_reported_cost_usd": round(
            sum(float(item.get("provider_reported_cost_usd") or 0) for item in calls), 12
        ),
        "failed_roles": failed_roles,
        "relation_block_reason": relation_block_reason,
        "joined": joined,
        "semantic_review_status": (
            "source_first_review_required"
            if all(_call_passed(item) for item in calls) and joined is not None
            else "source_first_review_required_for_available_role_outputs"
        ),
        "boundary": contract["boundary"],
    }
    _write(output_dir / "result.json", aggregate)
    print(
        json.dumps(
            {
                "provider_request_count": aggregate["provider_request_count"],
                "estimated_cost_usd": aggregate["estimated_cost_usd"],
                "failed_roles": failed_roles,
                "relation_block_reason": relation_block_reason,
                "join_status": joined.get("status") if joined else "not_available",
                "calls": [
                    {
                        "task_id": item["task_id"],
                        "operational_status": item["operational_status"],
                        "admitted_record_count": item.get("admitted_record_count", 0),
                        "quarantined_record_count": item.get("quarantined_record_count", 0),
                    }
                    for item in calls
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
