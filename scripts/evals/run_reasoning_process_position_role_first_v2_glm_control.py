#!/usr/bin/env python3
"""Run the unchanged role-first v2 contract with the frozen GLM control route."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v2 import (  # noqa: E402
    ROLE_ORDER,
    build_position_role_packet_v2,
    build_position_role_prompts_v2,
    position_relation_response_schema_v2,
    position_role_response_schema_v2,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals import run_reasoning_process_position_role_first_v2_probe as base  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_position_role_first_glm_control_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_position_role_first_glm_control_authorization.v1"


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise RuntimeError("unexpected GLM role-first control contract")
    if contract.get("status") != "frozen_before_at_most_four_unchanged_contract_calls":
        raise RuntimeError("GLM role-first control contract is not frozen")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("GLM control packet drifted")
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
        raise RuntimeError("GLM role request contracts drifted")
    if job["relation_response_schema_sha256"] != sha256_bytes(
        canonical_json_bytes(position_relation_response_schema_v2())
    ):
        raise RuntimeError("GLM relation schema drifted")
    if (
        job["case_id"] != "amb3-case01-journalism-platform-pilot"
        or job["model"] != "z-ai/glm-5.2"
        or job["provider_slug"] != "deepinfra"
    ):
        raise RuntimeError("GLM exact model/operator control drifted")
    if contract["budget"] != {
        "maximum_provider_calls": 4,
        "maximum_estimated_cost_usd": 0.02,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }:
        raise RuntimeError("GLM role-first control budget drifted")
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
        raise RuntimeError("GLM call configuration drifted")
    return {
        "status": "position_role_first_glm_control_contract_valid",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "provider_calls_made": 0,
    }


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_fragmentation_problem_class_review",
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
        raise RuntimeError("GLM role-first control authorization drifted")


def main() -> int:
    base.validate_contract = validate_contract
    base.validate_authorization = validate_authorization
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
