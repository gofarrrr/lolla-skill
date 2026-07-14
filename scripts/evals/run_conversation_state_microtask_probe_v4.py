#!/usr/bin/env python3
"""Single-repair-round JSON-mode transfer runner for conversation state."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.conversation_state_candidates import schema_metrics  # noqa: E402
from scripts.evals import run_conversation_state_microtask_probe as v1  # noqa: E402
from scripts.evals import run_conversation_state_microtask_probe_v2 as v2  # noqa: E402
from scripts.evals import run_conversation_state_microtask_probe_v3 as v3  # noqa: E402


CONTRACT_SCHEMA = "lolla.conversation_state_microtask_probe_contract.v4"
AUTHORIZATION_SCHEMA = "lolla.conversation_state_microtask_probe_authorization.v4"
KINDS = ("threads", "constraints", "positions")
ALLOWED_CASES = {
    "amb1-case01-product-scope",
    "amb1-case04-research-tool-release",
    "amb1-case05-family-archive",
}

_REPAIRS = {
    "threads": """Before returning, make a second pass from the final turn backward. For every focal thread, the latest reference must be the latest material statement that governs that thread, including a later general policy that applies to an earlier specific dispute. Do not stop at the first local response.""",
    "constraints": """Before returning, sweep every user turn in order for load-bearing stated conditions, reported statements, possibilities, preferences, concerns, and accepted inferences. Coverage is more important than brevity. Preserve the source speaker's epistemic strength. An assistant suggestion, warning, or option is not a case constraint unless the user accepts it or it becomes part of the current decision state.""",
    "positions": """Return one composed focal current direction when its conditions, thresholds, implementation details, and later qualifications are compatible parts of the same plan. Include material contributions from every speaker who shaped it, especially late qualifications. Split positions only when they are materially independent or competing, not merely because different speakers supplied different parts.""",
}


def build_repaired_micro_contract(
    kind: str, *, catalog: Any, provider: str = "openrouter_gemini"
) -> dict[str, Any]:
    base = v2.build_adapted_micro_contract(kind, catalog=catalog, provider=provider)
    system_prompt = base["system_prompt"] + "\n\n" + _REPAIRS[kind]
    result = dict(base)
    result["system_prompt"] = system_prompt
    result["system_prompt_sha256"] = hashlib.sha256(
        system_prompt.encode("utf-8")
    ).hexdigest()
    result["schema_metrics"] = schema_metrics(result["schema"])
    return result


def expected_prompt_hashes(contract: Mapping[str, Any]) -> dict[str, Any]:
    catalog = v1._catalog(contract)
    result: dict[str, Any] = {}
    for kind in KINDS:
        micro = build_repaired_micro_contract(kind, catalog=catalog)
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
        raise v1.MicrotaskProbeError("unexpected v4 contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise v1.MicrotaskProbeError("v4 contract is not frozen")
    case = contract.get("case", {})
    if case.get("case_id") not in ALLOWED_CASES:
        raise v1.MicrotaskProbeError("v4 case is outside repair program")
    if contract.get("microtask_order") != list(KINDS):
        raise v1.MicrotaskProbeError("v4 order drifted")
    for key in ("source_path", "reviewed_packet_path"):
        path = v1._repo_path(case.get(key), label=key)
        if not path.is_file() or v1._file_sha(path) != case.get(
            key.replace("_path", "_sha256")
        ):
            raise v1.MicrotaskProbeError(f"v4 case lock mismatch: {key}")
    config = contract.get("call_configuration", {})
    for key, expected in {
        "provider": "openrouter",
        "model": "google/gemini-3.1-flash-lite",
        "wire_mode": "json_object",
        "temperature": 0.0,
        "reasoning": {"enabled": False},
        "automatic_retries": 0,
        "evaluator_calls": 0,
        "pipeline_calls": 0,
        "graph_calls": 0,
    }.items():
        if config.get(key) != expected:
            raise v1.MicrotaskProbeError(f"v4 config drifted: {key}")
    if contract.get("prompt_hashes") != expected_prompt_hashes(contract):
        raise v1.MicrotaskProbeError("v4 prompt hashes drifted")
    if contract.get("repair_round") != {
        "round": 1,
        "maximum_rounds": 1,
        "case_specific_language": False,
        "thresholds_changed": False,
    }:
        raise v1.MicrotaskProbeError("v4 repair boundary drifted")
    for lock in contract.get("hash_locks", []):
        path = v1._repo_path(lock.get("path"), label="v4 artifact lock")
        if not path.is_file() or v1._file_sha(path) != lock.get("sha256"):
            raise v1.MicrotaskProbeError(f"v4 lock mismatch: {lock.get('role')}")


def validate_authorization(
    authorization: Mapping[str, Any], *, contract_path: Path, contract: Mapping[str, Any]
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise v1.MicrotaskProbeError("unexpected v4 authorization")
    if authorization.get("status") != "authorized_under_program":
        raise v1.MicrotaskProbeError("v4 not program-authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(REPO_ROOT)):
        raise v1.MicrotaskProbeError("v4 authorization path mismatch")
    if authorization.get("contract_sha256") != v1._file_sha(contract_path):
        raise v1.MicrotaskProbeError("v4 authorization hash mismatch")
    if authorization.get("maximum_provider_calls") != 3:
        raise v1.MicrotaskProbeError("v4 call ceiling mismatch")
    if any(authorization.get(k) != 0 for k in (
        "automatic_retries", "evaluator_calls", "pipeline_calls", "graph_calls"
    )):
        raise v1.MicrotaskProbeError("v4 forbidden calls")


def run_call(contract: Mapping[str, Any], *, kind: str) -> dict[str, Any]:
    validate_contract(contract)
    original_builder = v1.build_micro_contract
    original_validator = v1.validate_contract
    original_urlopen = v1.request.urlopen
    try:
        v1.build_micro_contract = build_repaired_micro_contract
        v1.validate_contract = lambda _contract: None
        v1.request.urlopen = v3._json_object_urlopen
        result = v1.run_call(contract, kind=kind)
        result.update({
            "provider_projection": "openrouter_gemini_prompt_only_repair1",
            "wire_mode": "json_object",
            "provider_schema_enforcement": False,
            "local_typed_validation": True,
            "semantic_repair_round": 1,
        })
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
            "repair_round": 1,
            "prompt_hashes": expected_prompt_hashes(contract),
            "provider_calls": 0,
        }, indent=2))
        return 0
    if args.authorization is None or args.env_file is None or args.kind is None:
        raise v1.MicrotaskProbeError("v4 execution arguments missing")
    validate_authorization(
        v1._load(args.authorization), contract_path=contract_path, contract=contract
    )
    v1._load_env(args.env_file)
    print(json.dumps(run_call(contract, kind=args.kind), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
