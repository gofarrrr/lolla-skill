#!/usr/bin/env python3
"""Run the prospective R4 token correction after new explicit authorization."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.r4_complementary_readers import (
    relationship_response_schema_v1,
    uncertainty_response_schema_v1,
    value_sha256,
)
from scripts.evals import build_r4_complementary_reader_preflight as base_preflight
from scripts.evals import run_r4_complementary_reader_experiment as frozen
from scripts.evals.build_r4_complementary_reader_token_correction import (
    DEFAULT_OUTPUT as CORRECTION_OUTPUT,
    RELATIONSHIP_LIMITS,
    UNCERTAINTY_LIMITS,
    build_files as build_correction_files,
    validate_files as validate_correction_files,
)
from scripts.evals.finalize_r4_complementary_reader_execution import (
    CLOSEOUT,
    validate as validate_historical_closeout,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_SCHEMA = "lolla.r4_complementary_reader_token_correction_contract.v1"
AUTH_SCHEMA = "lolla.r4_complementary_reader_token_correction_authorization.v1"
ORIGINAL_CONTRACT = (
    ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json"
)
DEFAULT_CONTRACT = (
    ROOT / "docs/evals/lolla-r4-complementary-reader-token-correction-contract-v1.json"
)


class R4TokenCorrectionRunError(RuntimeError):
    """Raised when the prospective correction or authorization drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4TokenCorrectionRunError(f"expected JSON object: {path}")
    return value


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def validate_contract(path: Path = DEFAULT_CONTRACT) -> dict[str, Any]:
    contract = _load(path)
    if (
        contract.get("schema_version") != CONTRACT_SCHEMA
        or contract.get("status")
        != "frozen_provider_free_call_authorization_required"
        or contract.get("run_id")
        != "lolla-r4-complementary-reader-token-correction-a2"
    ):
        raise R4TokenCorrectionRunError("token correction contract drifted")
    for row in contract.get("frozen_inputs", []):
        frozen_path = ROOT / row["path"]
        if not frozen_path.is_file() or _file_sha(frozen_path) != row["sha256"]:
            raise R4TokenCorrectionRunError(f"frozen input drifted: {row['path']}")
    base_ref = contract.get("original_contract", {})
    if (
        base_ref.get("path") != _relative(ORIGINAL_CONTRACT)
        or base_ref.get("sha256") != _file_sha(ORIGINAL_CONTRACT)
    ):
        raise R4TokenCorrectionRunError("original contract reference drifted")
    effective = copy.deepcopy(frozen._validate_contract(ORIGINAL_CONTRACT))
    historical = validate_historical_closeout()
    if (
        contract.get("historical_execution_closeout", {}).get("path")
        != _relative(CLOSEOUT)
        or contract.get("historical_execution_closeout", {}).get("sha256")
        != _file_sha(CLOSEOUT)
        or historical.get("decision", {}).get("semantic_hypothesis_resolved")
        is not False
        or historical.get("decision", {}).get("additional_provider_call_authorized")
        is not False
    ):
        raise R4TokenCorrectionRunError("historical execution boundary drifted")
    validate_correction_files(build_correction_files(CORRECTION_OUTPUT))
    preflight_path = ROOT / contract["preflight"]["path"]
    manifest_path = ROOT / contract["preflight"]["manifest_path"]
    preflight = _load(preflight_path)
    if (
        _file_sha(preflight_path) != contract["preflight"]["sha256"]
        or _file_sha(manifest_path) != contract["preflight"]["manifest_sha256"]
        or preflight.get("status")
        != "provider_free_token_correction_ready_call_authorization_required"
        or preflight.get("decision", {}).get("provider_calls_authorized") is not False
        or preflight.get("budget", {}).get("conservative_estimated_total_cost_usd")
        != 0.0181615
    ):
        raise R4TokenCorrectionRunError("correction preflight drifted")
    if contract.get("task_limits") != {
        "uncertainty": UNCERTAINTY_LIMITS,
        "relationship": RELATIONSHIP_LIMITS,
    }:
        raise R4TokenCorrectionRunError("corrected task limits drifted")
    if contract.get("budget") != effective.get("budget"):
        raise R4TokenCorrectionRunError("budget changed from original contract")
    if contract.get("operator") != effective.get("operator"):
        raise R4TokenCorrectionRunError("operator changed from original contract")
    if contract.get("schemas") != effective.get("schemas"):
        raise R4TokenCorrectionRunError("schema contract changed")
    if (
        value_sha256(uncertainty_response_schema_v1())
        != contract["schemas"]["uncertainty_sha256"]
        or value_sha256(relationship_response_schema_v1())
        != contract["schemas"]["relationship_sha256"]
    ):
        raise R4TokenCorrectionRunError("runtime schema drifted")
    base_by_id = {row["case_id"]: row for row in effective["cases"]}
    corrected_cases = []
    if [row.get("case_id") for row in contract.get("cases", [])] != list(base_by_id):
        raise R4TokenCorrectionRunError("corrected case order or identity drifted")
    for correction in contract["cases"]:
        case_id = correction["case_id"]
        base_case = copy.deepcopy(base_by_id[case_id])
        preview_path = ROOT / correction["uncertainty_request_preview_path"]
        preview = _load(preview_path)
        body = preview.get("body")
        if not isinstance(body, Mapping):
            raise R4TokenCorrectionRunError("corrected request body missing")
        original_preview = _load(ROOT / base_case["uncertainty_request_preview_path"])
        expected_body = copy.deepcopy(original_preview["body"])
        expected_body["max_tokens"] = 1600
        expected_body["reasoning"] = {"effort": "minimal", "exclude": True}
        if (
            dict(body) != expected_body
            or preview.get("body_sha256") != value_sha256(body)
            or preview.get("body_sha256")
            != correction["uncertainty_request_body_sha256"]
            or correction.get("changed_json_paths")
            != ["/max_tokens", "/reasoning/effort"]
        ):
            raise R4TokenCorrectionRunError("corrected request projection drifted")
        base_case["uncertainty_request_preview_path"] = correction[
            "uncertainty_request_preview_path"
        ]
        base_case["uncertainty_request_body_sha256"] = correction[
            "uncertainty_request_body_sha256"
        ]
        corrected_cases.append(base_case)
    effective["schema_version"] = CONTRACT_SCHEMA
    effective["run_id"] = contract["run_id"]
    effective["task_limits"] = contract["task_limits"]
    effective["cases"] = corrected_cases
    effective["decision_boundary"] = contract["decision_boundary"]
    return effective


def validate_authorization(
    authorization_path: Path, *, contract: Mapping[str, Any], contract_path: Path
) -> None:
    authorization = _load(authorization_path)
    expected = {
        "schema_version": AUTH_SCHEMA,
        "status": "authorized_once_after_provider_free_token_correction",
        "contract_path": _relative(contract_path),
        "contract_sha256": _file_sha(contract_path),
        "run_id": contract["run_id"],
        "authorized_case_ids": [row["case_id"] for row in contract["cases"]],
        "maximum_provider_calls": 4,
        "maximum_provider_reported_cost_per_case_usd": 0.015,
        "maximum_provider_reported_cost_total_usd": 0.03,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if authorization != expected:
        raise R4TokenCorrectionRunError("token correction authorization drifted")


def run(contract: Mapping[str, Any], *, output: Path) -> dict[str, Any]:
    previous = copy.deepcopy(base_preflight.TASKS)
    try:
        base_preflight.TASKS.clear()
        base_preflight.TASKS.update(
            {
                "uncertainty": dict(UNCERTAINTY_LIMITS),
                "relationship": dict(RELATIONSHIP_LIMITS),
            }
        )
        return frozen.run(contract, output=output)
    finally:
        base_preflight.TASKS.clear()
        base_preflight.TASKS.update(previous)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = validate_contract(contract_path)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "frozen_token_correction_contract_valid",
                    "provider_calls": 0,
                    "authorization_present": args.authorization is not None,
                    "uncertainty_limits": contract["task_limits"]["uncertainty"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise R4TokenCorrectionRunError(
            "live execution requires new authorization, env, and output"
        )
    validate_authorization(
        args.authorization.resolve(), contract=contract, contract_path=contract_path
    )
    output = args.output.resolve()
    if output.exists():
        raise R4TokenCorrectionRunError("experiment output path already exists")
    output.mkdir(parents=True)
    frozen._load_env(args.env_file.resolve())
    result = run(contract, output=output)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["cost_ceiling_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
