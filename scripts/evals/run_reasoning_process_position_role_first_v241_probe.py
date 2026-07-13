#!/usr/bin/env python3
"""Run the frozen status-free paired role-first v2.4.1 probe."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v24 import (  # noqa: E402
    build_position_starting_packet_v24, build_position_starting_prompts_v24,
    position_relation_response_schema_v24, position_starting_response_schema_v24,
)
from engine.system_b.reasoning_process_position_role_first_v241 import (  # noqa: E402
    build_position_current_qualification_packet_v241,
    build_position_current_qualification_prompts_v241,
    compile_position_current_qualification_response_v241,
    position_current_qualification_response_schema_v241,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402
from scripts.evals import run_reasoning_process_position_role_first_v24_probe as base  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha  # noqa: E402

CONTRACT_SCHEMA = "lolla.reasoning_process_position_role_first_v241_probe_contract.v1"
AUTH_SCHEMA = "lolla.reasoning_process_position_role_first_v241_probe_authorization.v1"


def validate_contract(contract: dict, contract_path: Path) -> dict:
    if contract.get("schema_version") != CONTRACT_SCHEMA or contract.get("status") != "frozen_before_at_most_three_v241_new_case_calls":
        raise RuntimeError("unexpected or unfrozen v2.4.1 contract")
    for item in contract["frozen_inputs"]:
        if _sha(ROOT / item["path"]) != item["sha256"]:
            raise RuntimeError(f"frozen input drifted: {item['path']}")
    job = contract["job"]
    packet_path = ROOT / job["packet_path"]
    if _sha(packet_path) != job["packet_sha256"]:
        raise RuntimeError("v2.4.1 packet drifted")
    wrapper = _load(packet_path)
    starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
    starting_prompts = build_position_starting_prompts_v24(starting_packet)
    paired_packet = build_position_current_qualification_packet_v241(wrapper=wrapper)
    paired_prompts = build_position_current_qualification_prompts_v241(paired_packet)
    expected = {
        "starting": {"system_prompt_sha256": starting_prompts["system_prompt_sha256"], "user_prompt_sha256": starting_prompts["user_prompt_sha256"], "response_schema_sha256": sha256_bytes(canonical_json_bytes(position_starting_response_schema_v24("starting")))},
        "current_qualification": {"system_prompt_sha256": paired_prompts["system_prompt_sha256"], "user_prompt_sha256": paired_prompts["user_prompt_sha256"], "response_schema_sha256": sha256_bytes(canonical_json_bytes(position_current_qualification_response_schema_v241()))},
    }
    if job["request_contracts"] != expected or job["relation_response_schema_sha256"] != sha256_bytes(canonical_json_bytes(position_relation_response_schema_v24())):
        raise RuntimeError("v2.4.1 request contracts drifted")
    if job["case_id"] != "amb3-case06-housing-retrofit-partnership" or job["model"] != "deepseek/deepseek-v4-flash" or job["provider_slug"] != "alibaba":
        raise RuntimeError("v2.4.1 case or route drifted")
    if contract["budget"] != base.BUDGET or contract["call_configuration"] != base.CONFIG:
        raise RuntimeError("v2.4.1 budget or configuration drifted")
    return {"status": "position_role_first_v241_probe_contract_valid", "contract_path": str(contract_path.relative_to(ROOT)), "provider_calls_made": 0}


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {"schema_version": AUTH_SCHEMA, "status": "authorized_once_after_v241_new_case_target_and_adversarial_gates", "contract_path": str(contract_path.relative_to(ROOT)), "contract_sha256": _sha(contract_path), "run_id": contract["run_id"], "maximum_provider_calls": 3, "automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0, "evaluator_calls": 0, "embedding_calls": 0, "graph_calls": 0, "pipeline_calls": 0, "runtime_calls": 0}
    if value != expected:
        raise RuntimeError("v2.4.1 authorization drifted")


def main() -> int:
    base.validate_contract, base.validate_authorization = validate_contract, validate_authorization
    base.build_position_current_qualification_packet_v24 = build_position_current_qualification_packet_v241
    base.build_position_current_qualification_prompts_v24 = build_position_current_qualification_prompts_v241
    base.compile_position_current_qualification_response_v24 = compile_position_current_qualification_response_v241
    base.position_current_qualification_response_schema_v24 = position_current_qualification_response_schema_v241
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
