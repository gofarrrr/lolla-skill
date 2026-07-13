#!/usr/bin/env python3
"""V3 probe: JSON wire mode plus the unchanged typed local custody schema."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib import request


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.evals import run_conversation_state_extraction_probe as v1  # noqa: E402
from scripts.evals.run_conversation_state_extraction_probe_v2 import (  # noqa: E402
    response_schema,
)


DELTA_SCHEMA = "lolla.conversation_state_extraction_probe_contract_delta.v3"
_ORIGINAL_URLOPEN = request.urlopen
_V1_VALIDATE_CONTRACT = v1.validate_contract


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise v1.ConversationStateProbeError(f"expected JSON object: {path}")
    return value


def materialize_contract(delta: Mapping[str, Any]) -> dict[str, Any]:
    if delta.get("schema_version") != DELTA_SCHEMA:
        raise v1.ConversationStateProbeError("unexpected v3 delta schema")
    if delta.get("status") != "frozen_before_calls":
        raise v1.ConversationStateProbeError("v3 delta is not frozen")
    base_path = v1._repo_path(delta.get("base_contract_path"), label="v3 base contract")
    if not base_path.is_file() or v1._hash_file(base_path) != delta.get("base_contract_sha256"):
        raise v1.ConversationStateProbeError("v3 base contract hash mismatch")
    contract = copy.deepcopy(_load(base_path))
    contract["run_id"] = delta["run_id"]
    contract["purpose"] = delta["purpose"]
    contract["call_configuration"]["strict_structured_output"] = False
    contract["call_configuration"]["provider_response_format"] = "json_object"
    contract["call_configuration"]["local_typed_validation"] = True
    contract["artifacts"] = copy.deepcopy(delta["artifacts"])
    contract["hash_locks"] = copy.deepcopy(contract["hash_locks"])
    runner_lock = next(
        lock for lock in contract["hash_locks"] if lock["role"] == "probe_runner"
    )
    runner_lock["path"] = delta["runner_path"]
    runner_lock["sha256"] = delta["runner_sha256"]
    contract["hash_locks"].append(
        {
            "role": "v2_base_contract",
            "path": delta["base_contract_path"],
            "sha256": delta["base_contract_sha256"],
        }
    )
    return contract


def validate_materialized_contract(contract: Mapping[str, Any]) -> None:
    config = contract.get("call_configuration", {})
    if config.get("strict_structured_output") is not False:
        raise v1.ConversationStateProbeError("v3 must disable provider schema enforcement")
    if config.get("provider_response_format") != "json_object":
        raise v1.ConversationStateProbeError("v3 wire format must be json_object")
    if config.get("local_typed_validation") is not True:
        raise v1.ConversationStateProbeError("v3 must retain typed local validation")
    shadow = copy.deepcopy(dict(contract))
    shadow["call_configuration"]["strict_structured_output"] = True
    v1.response_schema = response_schema
    _V1_VALIDATE_CONTRACT(shadow)


def validate_delta(delta: Mapping[str, Any]) -> dict[str, Any]:
    required = {
        "schema_version",
        "status",
        "date",
        "run_id",
        "purpose",
        "base_contract_path",
        "base_contract_sha256",
        "runner_path",
        "runner_sha256",
        "operational_repair",
        "artifacts",
    }
    if set(delta) != required:
        raise v1.ConversationStateProbeError("v3 delta shape invalid")
    repair = delta.get("operational_repair", {})
    if repair != {
        "provider_response_format_from": "json_schema",
        "provider_response_format_to": "json_object",
        "typed_local_validation_retained": True,
        "semantic_prompt_changed": False,
        "selection_changed": False,
        "automatic_retry_of_v2": False,
    }:
        raise v1.ConversationStateProbeError("v3 operational repair drifted")
    contract = materialize_contract(delta)
    validate_materialized_contract(contract)
    return contract


def _json_object_urlopen(req: request.Request, *args: Any, **kwargs: Any):
    body = json.loads(bytes(req.data or b"{}").decode("utf-8"))
    original_format = body.get("response_format", {})
    if original_format.get("type") != "json_schema":
        raise v1.ConversationStateProbeError("expected typed v2 request before wire repair")
    body["response_format"] = {"type": "json_object"}
    rewritten = request.Request(
        req.full_url,
        data=json.dumps(body).encode("utf-8"),
        headers=dict(req.header_items()),
        method=req.get_method(),
    )
    return _ORIGINAL_URLOPEN(rewritten, *args, **kwargs)


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
            "local_response_schema_sha256": v1._json_hash(response_schema()),
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
    v1.validate_contract = validate_materialized_contract
    v1.request.urlopen = _json_object_urlopen
    summary, _custody = v1.run_probe(contract)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not summary["failed_gates"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
