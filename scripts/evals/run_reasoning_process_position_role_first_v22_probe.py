#!/usr/bin/env python3
"""Run the frozen new-case role-first v2.2 nested-component probe."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v2 import ROLE_ORDER  # noqa: E402
from engine.system_b.reasoning_process_position_role_first_v22 import (  # noqa: E402
    build_position_relation_packet_v22, build_position_relation_prompts_v22,
    build_position_role_packet_v22, build_position_role_prompts_v22,
    compile_position_relation_response_v22, compile_position_role_response_v22,
    join_position_role_first_v22, position_relation_response_schema_v22,
    position_role_response_schema_v22,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals import run_reasoning_process_position_role_first_v2_probe as base  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_position_role_first_v22_probe_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_position_role_first_v22_probe_authorization.v1"


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA or contract.get("status") != "frozen_before_at_most_four_v22_new_case_calls":
        raise RuntimeError("unexpected or unfrozen role-first v2.2 probe contract")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("v2.2 new-case packet drifted")
    wrapper = _load(packet_path)
    role_contracts = {}
    for role in ROLE_ORDER:
        packet = build_position_role_packet_v22(wrapper=wrapper, role=role)
        prompts = build_position_role_prompts_v22(packet)
        role_contracts[role] = {
            "system_prompt_sha256": prompts["system_prompt_sha256"],
            "user_prompt_sha256": prompts["user_prompt_sha256"],
            "response_schema_sha256": sha256_bytes(canonical_json_bytes(position_role_response_schema_v22(role))),
        }
    if job["role_request_contracts"] != role_contracts:
        raise RuntimeError("v2.2 role request contracts drifted")
    if job["relation_response_schema_sha256"] != sha256_bytes(canonical_json_bytes(position_relation_response_schema_v22())):
        raise RuntimeError("v2.2 relation response schema drifted")
    if job["case_id"] != "amb3-case03-farm-cooperative-retail" or job["model"] != "deepseek/deepseek-v4-flash" or job["provider_slug"] != "alibaba":
        raise RuntimeError("v2.2 case or exact model/operator pair drifted")
    expected_budget = {"maximum_provider_calls": 4, "maximum_estimated_cost_usd": 0.01, "automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0, "evaluator_calls": 0, "embedding_calls": 0, "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0}
    if contract["budget"] != expected_budget:
        raise RuntimeError("v2.2 probe budget drifted")
    expected_config = {"provider": "openrouter", "endpoint": "https://openrouter.ai/api/v1/chat/completions", "wire_mode": "strict_json_schema", "temperature": 0.0, "seed": 0, "reasoning_enabled": False, "max_output_tokens": 1200, "provider_timeout_seconds": 90, "require_supported_parameters": True, "allow_provider_fallbacks": False, "automatic_retries": 0, "response_healing": False, "parallel_calls": False}
    if contract["call_configuration"] != expected_config:
        raise RuntimeError("v2.2 call configuration drifted")
    return {"status": "position_role_first_v22_probe_contract_valid", "contract_path": str(contract_path.relative_to(ROOT)), "provider_calls_made": 0}


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_v22_new_case_target_and_adversarial_gates",
        "contract_path": str(contract_path.relative_to(ROOT)), "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"], "maximum_provider_calls": 4, "automatic_retries": 0,
        "semantic_retries": 0, "fallback_models": 0, "evaluator_calls": 0, "embedding_calls": 0,
        "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0,
    }
    if value != expected:
        raise RuntimeError("v2.2 probe authorization drifted")


def main() -> int:
    base.validate_contract, base.validate_authorization = validate_contract, validate_authorization
    base.build_position_role_packet_v2 = build_position_role_packet_v22
    base.build_position_role_prompts_v2 = build_position_role_prompts_v22
    base.compile_position_role_response_v2 = compile_position_role_response_v22
    base.position_role_response_schema_v2 = position_role_response_schema_v22
    base.build_position_relation_packet_v2 = build_position_relation_packet_v22
    base.build_position_relation_prompts_v2 = build_position_relation_prompts_v22
    base.compile_position_relation_response_v2 = compile_position_relation_response_v22
    base.position_relation_response_schema_v2 = position_relation_response_schema_v22
    base.join_position_role_first_v2 = join_position_role_first_v22
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
