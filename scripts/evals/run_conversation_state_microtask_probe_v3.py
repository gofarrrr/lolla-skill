#!/usr/bin/env python3
"""JSON-mode Case 05 microtask probe with local typed admission."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib import request

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evals import run_conversation_state_microtask_probe as v1  # noqa: E402
from scripts.evals import run_conversation_state_microtask_probe_v2 as v2  # noqa: E402


CONTRACT_SCHEMA = "lolla.conversation_state_microtask_probe_contract.v3"
AUTHORIZATION_SCHEMA = "lolla.conversation_state_microtask_probe_authorization.v3"
KINDS = ("threads", "constraints", "positions")


def expected_prompt_hashes(contract: Mapping[str, Any]) -> dict[str, Any]:
    catalog = v1._catalog(contract)
    result: dict[str, Any] = {}
    for kind in KINDS:
        micro = v2.build_adapted_micro_contract(kind, catalog=catalog)
        result[kind] = {
            "system_prompt_sha256": micro["system_prompt_sha256"],
            "user_prompt_sha256": micro["user_prompt_sha256"],
            "schema_sha256": micro["schema_sha256"],
            "schema_metrics": micro["schema_metrics"],
            "allowed_span_id_count": micro["allowed_span_id_count"],
        }
    return result


def validate_contract(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise v1.MicrotaskProbeError("unexpected v3 contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise v1.MicrotaskProbeError("v3 contract is not frozen")
    if contract.get("microtask_order") != list(KINDS):
        raise v1.MicrotaskProbeError("v3 microtask order drifted")
    case = contract.get("case")
    if not isinstance(case, Mapping) or case.get("case_id") != "amb1-case05-family-archive":
        raise v1.MicrotaskProbeError("v3 Case 05 selection drifted")
    for key in ("source_path", "reviewed_packet_path"):
        path = v1._repo_path(case.get(key), label=key)
        if not path.is_file() or v1._file_sha(path) != case.get(
            key.replace("_path", "_sha256")
        ):
            raise v1.MicrotaskProbeError(f"v3 case lock mismatch: {key}")
    config = contract.get("call_configuration", {})
    expected = {
        "provider": "openrouter",
        "model": "google/gemini-3.1-flash-lite",
        "wire_mode": "json_object",
        "provider_projection": "openrouter_gemini_prompt_only",
        "typed_schema_in_prompt": True,
        "local_typed_validation": True,
        "temperature": 0.0,
        "reasoning": {"enabled": False},
        "require_supported_parameters": True,
        "calls_per_microtask": 1,
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "pipeline_calls": 0,
        "graph_calls": 0,
    }
    for key, value in expected.items():
        if config.get(key) != value:
            raise v1.MicrotaskProbeError(f"v3 call configuration drifted: {key}")
    if contract.get("prompt_hashes") != expected_prompt_hashes(contract):
        raise v1.MicrotaskProbeError("v3 prompt or schema hashes drifted")
    budget = contract.get("call_budget", {})
    if budget.get("maximum_provider_calls") != 3:
        raise v1.MicrotaskProbeError("v3 call ceiling drifted")
    if budget.get("estimated_total_cost_ceiling_usd") != 0.02:
        raise v1.MicrotaskProbeError("v3 cost ceiling drifted")
    roles: set[str] = set()
    for lock in contract.get("hash_locks", []):
        path = v1._repo_path(lock.get("path"), label="v3 artifact lock")
        if not path.is_file() or v1._file_sha(path) != lock.get("sha256"):
            raise v1.MicrotaskProbeError(
                f"v3 artifact lock mismatch: {lock.get('role')}"
            )
        roles.add(str(lock.get("role")))
    if not {
        "v3_runner", "v1_runner", "v2_runner", "typed_candidates",
        "candidate_pipeline", "state_handoff", "pricing",
        "experiment_program", "v2_probe_decision",
    } <= roles:
        raise v1.MicrotaskProbeError("v3 required locks missing")
    if contract.get("stop_rules") != {
        "operational_failure_stops_remaining_calls": True,
        "valid_semantic_failure_is_preserved_and_does_not_trigger_retry": True,
        "hard_stop_before_second_case": True,
    }:
        raise v1.MicrotaskProbeError("v3 stop rules drifted")


def validate_authorization(
    authorization: Mapping[str, Any], *, contract_path: Path, contract: Mapping[str, Any]
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise v1.MicrotaskProbeError("unexpected v3 authorization schema")
    if authorization.get("status") != "authorized_under_program":
        raise v1.MicrotaskProbeError("v3 calls are not program-authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(REPO_ROOT)):
        raise v1.MicrotaskProbeError("v3 authorization path mismatch")
    if authorization.get("contract_sha256") != v1._file_sha(contract_path):
        raise v1.MicrotaskProbeError("v3 authorization hash mismatch")
    if authorization.get("maximum_provider_calls") != 3:
        raise v1.MicrotaskProbeError("v3 authorization call ceiling mismatch")
    if authorization.get("microtask_order") != list(KINDS):
        raise v1.MicrotaskProbeError("v3 authorization order mismatch")
    if any(
        authorization.get(key) != 0
        for key in ("automatic_retries", "evaluator_calls", "pipeline_calls", "graph_calls")
    ):
        raise v1.MicrotaskProbeError("v3 authorization contains forbidden calls")


def _json_object_urlopen(req: request.Request, timeout: float):
    body = json.loads(bytes(req.data or b"{}").decode("utf-8"))
    response_format = body.get("response_format", {})
    if response_format.get("type") != "json_schema":
        raise v1.MicrotaskProbeError("v3 expected internal json_schema request")
    body["response_format"] = {"type": "json_object"}
    adapted = request.Request(
        req.full_url,
        data=json.dumps(body).encode("utf-8"),
        headers=dict(req.header_items()),
        method=req.get_method(),
    )
    return _ORIGINAL_URLOPEN(adapted, timeout=timeout)


_ORIGINAL_URLOPEN = v1.request.urlopen


def run_call(contract: Mapping[str, Any], *, kind: str) -> dict[str, Any]:
    validate_contract(contract)
    original_builder = v1.build_micro_contract
    original_validator = v1.validate_contract
    original_urlopen = v1.request.urlopen
    try:
        v1.build_micro_contract = v2.build_adapted_micro_contract
        v1.validate_contract = lambda _contract: None
        v1.request.urlopen = _json_object_urlopen
        result = v1.run_call(contract, kind=kind)
        result["provider_projection"] = "openrouter_gemini_prompt_only"
        result["wire_mode"] = "json_object"
        result["provider_schema_enforcement"] = False
        result["local_typed_validation"] = True
        return result
    finally:
        v1.build_micro_contract = original_builder
        v1.validate_contract = original_validator
        v1.request.urlopen = original_urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--kind", choices=KINDS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = v1._load(contract_path)
    validate_contract(contract)
    if args.dry_run:
        print(json.dumps({
            "status": "dry_run_valid",
            "run_id": contract["run_id"],
            "case_id": contract["case"]["case_id"],
            "wire_mode": "json_object",
            "typed_schema_in_prompt": True,
            "local_typed_validation": True,
            "microtask_order": list(KINDS),
            "prompt_hashes": expected_prompt_hashes(contract),
            "maximum_provider_calls": 3,
            "automatic_retries": 0,
            "provider_calls_made_by_dry_run": 0,
        }, indent=2))
        return 0
    if args.authorization is None or args.env_file is None or args.kind is None:
        raise v1.MicrotaskProbeError("v3 execution arguments missing")
    validate_authorization(
        v1._load(args.authorization), contract_path=contract_path, contract=contract
    )
    v1._load_env(args.env_file)
    print(json.dumps(run_call(contract, kind=args.kind), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
