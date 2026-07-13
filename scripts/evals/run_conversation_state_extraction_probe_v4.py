#!/usr/bin/env python3
"""V4 probe: show the local typed schema in JSON-mode prompts and seal safely."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evals import run_conversation_state_extraction_probe as v1  # noqa: E402
from scripts.evals import run_conversation_state_extraction_probe_v3 as v3  # noqa: E402
from scripts.evals.run_conversation_state_extraction_probe_v2 import (  # noqa: E402
    response_schema,
)


DELTA_SCHEMA = "lolla.conversation_state_extraction_probe_contract_delta.v4"
_V1_BUILD_PROMPTS = v1.build_prompts
_V1_VALIDATE_CONTRACT = v3._V1_VALIDATE_CONTRACT


def build_prompts(contract: Mapping[str, Any], case: Mapping[str, Any]) -> dict[str, str]:
    prompts = _V1_BUILD_PROMPTS(contract, case)
    schema_text = json.dumps(
        response_schema()["schema"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    prompts["user_prompt"] += (
        "\n\nLOCAL TYPED RESPONSE SCHEMA\n"
        + schema_text
        + "\nReturn exactly one JSON object with those fields and no wrapper."
    )
    return prompts


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise v1.ConversationStateProbeError(f"expected JSON object: {path}")
    return value


def materialize_contract(delta: Mapping[str, Any]) -> dict[str, Any]:
    if delta.get("schema_version") != DELTA_SCHEMA:
        raise v1.ConversationStateProbeError("unexpected v4 delta schema")
    if delta.get("status") != "frozen_before_calls":
        raise v1.ConversationStateProbeError("v4 delta is not frozen")
    base_path = v1._repo_path(delta.get("base_contract_path"), label="v4 base contract")
    if not base_path.is_file() or v1._hash_file(base_path) != delta.get("base_contract_sha256"):
        raise v1.ConversationStateProbeError("v4 base contract hash mismatch")
    base_delta = _load(base_path)
    contract = copy.deepcopy(v3.validate_delta(base_delta))
    contract["run_id"] = delta["run_id"]
    contract["purpose"] = delta["purpose"]
    contract["call_configuration"]["schema_in_prompt"] = True
    contract["call_configuration"]["invalid_packet_persistence"] = "forbidden"
    contract["artifacts"] = copy.deepcopy(delta["artifacts"])
    runner_lock = next(
        lock for lock in contract["hash_locks"] if lock["role"] == "probe_runner"
    )
    runner_lock["path"] = delta["runner_path"]
    runner_lock["sha256"] = delta["runner_sha256"]
    contract["hash_locks"].append(
        {
            "role": "v3_base_contract_delta",
            "path": delta["base_contract_path"],
            "sha256": delta["base_contract_sha256"],
        }
    )
    v1.response_schema = response_schema
    v1.build_prompts = build_prompts
    contract["prompt_hashes"] = v1.prompt_hashes(contract)
    return contract


def validate_materialized_contract(contract: Mapping[str, Any]) -> None:
    config = contract.get("call_configuration", {})
    if config.get("provider_response_format") != "json_object":
        raise v1.ConversationStateProbeError("v4 wire format must remain json_object")
    if config.get("local_typed_validation") is not True:
        raise v1.ConversationStateProbeError("v4 must retain typed local validation")
    if config.get("schema_in_prompt") is not True:
        raise v1.ConversationStateProbeError("v4 must show the schema in the prompt")
    if config.get("invalid_packet_persistence") != "forbidden":
        raise v1.ConversationStateProbeError("v4 must forbid invalid packet persistence")
    shadow = copy.deepcopy(dict(contract))
    shadow["call_configuration"]["strict_structured_output"] = True
    v1.response_schema = response_schema
    v1.build_prompts = build_prompts
    _V1_VALIDATE_CONTRACT(shadow)


def validate_delta(delta: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "schema_version", "status", "date", "run_id", "purpose",
        "base_contract_path", "base_contract_sha256", "runner_path",
        "runner_sha256", "operational_repair", "artifacts",
    }
    if set(delta) != required:
        raise v1.ConversationStateProbeError("v4 delta shape invalid")
    if delta.get("operational_repair") != {
        "typed_schema_added_to_formatting_prompt": True,
        "semantic_extraction_instruction_changed": False,
        "invalid_packet_persistence_forbidden": True,
        "selection_changed": False,
        "automatic_retry_of_v3": False,
    }:
        raise v1.ConversationStateProbeError("v4 operational repair drifted")
    contract = materialize_contract(delta)
    validate_materialized_contract(contract)
    return contract


def _call_without_empty_packet(
    contract: Mapping[str, Any], case: Mapping[str, Any]
) -> dict[str, Any]:
    result = v1._call_openrouter(contract, case)
    if not result.get("sealed_packet"):
        result.pop("sealed_packet", None)
        result["custody_violation_count"] = None
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    delta_path = args.contract.resolve()
    delta = _load(delta_path)
    contract = validate_delta(delta)
    if args.dry_run:
        output_dir = v1._repo_path(contract["artifacts"]["output_dir"], label="output directory")
        if output_dir.exists():
            raise v1.ConversationStateProbeError("frozen output directory must be absent")
        print(json.dumps({
            "status": "dry_run_valid",
            "run_id": contract["run_id"],
            "provider_response_format": "json_object",
            "schema_in_prompt": True,
            "local_response_schema_sha256": v1._json_hash(response_schema()),
            "prompt_hashes": contract["prompt_hashes"],
            "maximum_provider_calls": 2,
            "automatic_retries": 0,
            "pipeline_calls": 0,
            "graph_calls": 0,
            "evaluator_calls": 0,
            "provider_calls_made_by_dry_run": 0,
        }, indent=2))
        return 0
    if args.env_file is None or args.authorization is None:
        raise v1.ConversationStateProbeError("--env-file and --authorization required")
    authorization = _load(args.authorization)
    v1.validate_authorization(authorization, contract_path=delta_path, contract=delta)
    v1._load_env_file(args.env_file)
    v1.response_schema = response_schema
    v1.build_prompts = build_prompts
    v1.validate_contract = validate_materialized_contract
    v1.request.urlopen = v3._json_object_urlopen
    summary, _custody = v1.run_probe(contract, call_fn=_call_without_empty_packet)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not summary["failed_gates"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
