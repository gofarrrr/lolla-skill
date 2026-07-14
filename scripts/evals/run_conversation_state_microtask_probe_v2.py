#!/usr/bin/env python3
"""Case 05 transfer probe with an OpenRouter-specific Gemini projection."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.conversation_state_candidates import (  # noqa: E402
    build_micro_contract as build_base_micro_contract,
    schema_metrics,
)
from scripts.evals import run_conversation_state_microtask_probe as v1  # noqa: E402


CONTRACT_SCHEMA = "lolla.conversation_state_microtask_probe_contract.v2"
AUTHORIZATION_SCHEMA = "lolla.conversation_state_microtask_probe_authorization.v2"
KINDS = ("threads", "constraints", "positions")


def _text_sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_adapted_micro_contract(
    kind: str, *, catalog: Any, provider: str = "openrouter_gemini"
) -> dict[str, Any]:
    if provider not in {"gemini", "openrouter_gemini"}:
        raise v1.MicrotaskProbeError("v2 requires openrouter_gemini projection")
    base = build_base_micro_contract(kind, catalog=catalog, provider="openai")
    schema = copy.deepcopy(base["schema"])
    evidence = schema.get("$defs", {}).get("EvidenceRef", {})
    span_property = evidence.get("properties", {}).get("span_id", {})
    allowed_ids = [span.span_id for span in catalog.spans if span.kind == "sentence"]
    span_property["enum"] = allowed_ids
    span_property["description"] = (
        "Select exactly one complete supplied source ID, including the literal "
        "span- prefix. Only enumerated IDs are valid."
    )
    system_prompt = base["system_prompt"] + (
        "\n\nCopy every source identifier in full. Never remove, add, normalize, "
        "or reconstruct an identifier. A source identifier without its literal "
        "`span-` prefix is invalid."
    )
    if kind == "positions":
        system_prompt += (
            "\nTreat a later qualification, threshold, or implementation detail as "
            "a contribution to the focal position it modifies. Do not split it into "
            "a separately owned position merely because a different speaker supplied it."
        )
    catalog_prompt = base["user_prompt"].split("\n\nTYPED OUTPUT SCHEMA\n", 1)[0]
    schema_text = json.dumps(
        schema, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    user_prompt = catalog_prompt + "\n\nTYPED OUTPUT SCHEMA\n" + schema_text
    return {
        "kind": kind,
        "provider_projection": provider,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "system_prompt_sha256": _text_sha(system_prompt),
        "user_prompt_sha256": _text_sha(user_prompt),
        "schema": schema,
        "schema_sha256": _text_sha(schema_text),
        "schema_metrics": schema_metrics(schema),
        "allowed_span_id_count": len(allowed_ids),
        "provider_calls": 0,
    }


def expected_prompt_hashes(contract: Mapping[str, Any]) -> dict[str, Any]:
    catalog = v1._catalog(contract)
    result: dict[str, Any] = {}
    for kind in KINDS:
        micro = build_adapted_micro_contract(kind, catalog=catalog)
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
        raise v1.MicrotaskProbeError("unexpected v2 contract schema")
    if contract.get("status") != "frozen_before_calls":
        raise v1.MicrotaskProbeError("v2 contract is not frozen")
    if contract.get("microtask_order") != list(KINDS):
        raise v1.MicrotaskProbeError("v2 microtask order drifted")
    case = contract.get("case")
    if not isinstance(case, Mapping) or case.get("case_id") != "amb1-case05-family-archive":
        raise v1.MicrotaskProbeError("Case 05 transfer selection drifted")
    for key in ("source_path", "reviewed_packet_path"):
        path = v1._repo_path(case.get(key), label=key)
        hash_key = key.replace("_path", "_sha256")
        if not path.is_file() or v1._file_sha(path) != case.get(hash_key):
            raise v1.MicrotaskProbeError(f"v2 case lock mismatch: {key}")
    catalog = v1._catalog(contract)
    if catalog.message_count != 14 or catalog.source_sha256 != case.get("source_sha256"):
        raise v1.MicrotaskProbeError("v2 source catalog drifted")
    config = contract.get("call_configuration", {})
    expected = {
        "provider": "openrouter",
        "model": "google/gemini-3.1-flash-lite",
        "provider_projection": "openrouter_gemini",
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
            raise v1.MicrotaskProbeError(f"v2 call configuration drifted: {key}")
    if not 1 <= int(config.get("max_output_tokens", 0)) <= 5000:
        raise v1.MicrotaskProbeError("v2 output-token cap invalid")
    budget = contract.get("call_budget", {})
    if budget.get("maximum_provider_calls") != 3:
        raise v1.MicrotaskProbeError("v2 call ceiling drifted")
    if budget.get("estimated_total_cost_ceiling_usd") != 0.02:
        raise v1.MicrotaskProbeError("v2 cost ceiling drifted")
    if contract.get("prompt_hashes") != expected_prompt_hashes(contract):
        raise v1.MicrotaskProbeError("v2 prompt or schema hashes drifted")
    roles: set[str] = set()
    for lock in contract.get("hash_locks", []):
        path = v1._repo_path(lock.get("path"), label="v2 artifact lock")
        if not path.is_file() or v1._file_sha(path) != lock.get("sha256"):
            raise v1.MicrotaskProbeError(
                f"v2 artifact lock mismatch: {lock.get('role')}"
            )
        roles.add(str(lock.get("role")))
    if not {
        "v2_runner", "v1_runner", "typed_candidates", "candidate_pipeline",
        "state_handoff", "pricing", "product_constitution",
        "structured_extraction_practices", "v1_probe_decision",
    } <= roles:
        raise v1.MicrotaskProbeError("v2 required locks missing")
    if contract.get("stop_rules") != {
        "operational_failure_stops_remaining_calls": True,
        "valid_semantic_failure_is_preserved_and_does_not_trigger_retry": True,
        "hard_stop_before_second_case": True,
    }:
        raise v1.MicrotaskProbeError("v2 stop rules drifted")


def validate_authorization(
    authorization: Mapping[str, Any], *, contract_path: Path, contract: Mapping[str, Any]
) -> None:
    if authorization.get("schema_version") != AUTHORIZATION_SCHEMA:
        raise v1.MicrotaskProbeError("unexpected v2 authorization schema")
    if authorization.get("status") != "authorized_once":
        raise v1.MicrotaskProbeError("v2 calls are not authorized")
    if authorization.get("contract_path") != str(contract_path.relative_to(REPO_ROOT)):
        raise v1.MicrotaskProbeError("v2 authorization path mismatch")
    if authorization.get("contract_sha256") != v1._file_sha(contract_path):
        raise v1.MicrotaskProbeError("v2 authorization hash mismatch")
    if authorization.get("run_id") != contract.get("run_id"):
        raise v1.MicrotaskProbeError("v2 authorization run mismatch")
    if authorization.get("maximum_provider_calls") != 3:
        raise v1.MicrotaskProbeError("v2 authorization call ceiling mismatch")
    if authorization.get("microtask_order") != list(KINDS):
        raise v1.MicrotaskProbeError("v2 authorization order mismatch")
    if any(
        authorization.get(key) != 0
        for key in ("automatic_retries", "evaluator_calls", "pipeline_calls", "graph_calls")
    ):
        raise v1.MicrotaskProbeError("v2 authorization contains forbidden calls")


def run_call(contract: Mapping[str, Any], *, kind: str) -> dict[str, Any]:
    validate_contract(contract)
    original_builder = v1.build_micro_contract
    original_validator = v1.validate_contract
    try:
        v1.build_micro_contract = build_adapted_micro_contract
        v1.validate_contract = lambda _contract: None
        return v1.run_call(contract, kind=kind)
    finally:
        v1.build_micro_contract = original_builder
        v1.validate_contract = original_validator


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
            "microtask_order": list(KINDS),
            "prompt_hashes": expected_prompt_hashes(contract),
            "maximum_provider_calls": 3,
            "automatic_retries": 0,
            "provider_calls_made_by_dry_run": 0,
            "graph_calls": 0,
            "pipeline_calls": 0,
            "evaluator_calls": 0,
        }, indent=2))
        return 0
    if args.authorization is None or args.env_file is None or args.kind is None:
        raise v1.MicrotaskProbeError(
            "--authorization, --env-file, and --kind required for v2 execution"
        )
    authorization = v1._load(args.authorization)
    validate_authorization(
        authorization, contract_path=contract_path, contract=contract
    )
    v1._load_env(args.env_file)
    print(json.dumps(run_call(contract, kind=args.kind), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
