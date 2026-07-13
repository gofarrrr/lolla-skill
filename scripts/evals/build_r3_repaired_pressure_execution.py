#!/usr/bin/env python3
"""Freeze the one-call repaired R3 pressure execution and authorization."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.r3_fresh_consumer import (  # noqa: E402
    MAX_PROVIDER_CALLS,
    MAX_PROVIDER_COST_USD,
    MODEL,
)
from scripts.evals.build_r3_google_schema_repair import (  # noqa: E402
    validate_contract as validate_repair_contract,
)
from scripts.evals.run_r3_repaired_pressure import (  # noqa: E402
    AUTHORIZATION_SCHEMA,
    EXECUTION_CONTRACT_SCHEMA,
    validate_execution_contract,
)


REPAIR_CONTRACT = ROOT / "docs/evals/lolla-r3-google-schema-repair-contract-v1.json"
PROJECTION_MODULE = ROOT / "engine/system_b/r3_google_schema_projection.py"
PROVIDER_BUDGET = ROOT / "engine/system_b/provider_budget.py"
RUNNER = ROOT / "scripts/evals/run_r3_repaired_pressure.py"
BUILDER = ROOT / "scripts/evals/build_r3_repaired_pressure_execution.py"


class R3RepairedExecutionBuildError(RuntimeError):
    """Raised when the repaired execution freeze cannot be established."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3RepairedExecutionBuildError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def build(
    *, contract_path: Path, authorization_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    repair_contract, bundle = validate_repair_contract(REPAIR_CONTRACT)
    if repair_contract["provider_boundary"]["provider_calls_made"] != 0:
        raise R3RepairedExecutionBuildError("repair contract already records provider work")
    if bundle["request_contract"]["maximum_estimated_call_cost_usd"] > 0.01:
        raise R3RepairedExecutionBuildError("repaired pressure exceeds one-cent estimate")
    frozen_inputs = [
        REPAIR_CONTRACT,
        ROOT / repair_contract["prospective_bundle"]["path"],
        PROJECTION_MODULE,
        PROVIDER_BUDGET,
        RUNNER,
        BUILDER,
    ]
    contract = {
        "schema_version": EXECUTION_CONTRACT_SCHEMA,
        "status": "frozen_before_one_repaired_pressure_call",
        "run_id": "lolla-r3-fresh-consumer-case01-pressure-r2-repaired",
        "case_id": bundle["case_id"],
        "repair_contract": {
            "path": _relative(REPAIR_CONTRACT),
            "file_sha256": _file_sha(REPAIR_CONTRACT),
        },
        "bundle": {
            "path": repair_contract["prospective_bundle"]["path"],
            "file_sha256": repair_contract["prospective_bundle"]["file_sha256"],
            "bundle_sha256": bundle["bundle_sha256"],
        },
        "frozen_inputs": [
            {"path": _relative(path), "sha256": _file_sha(path)}
            for path in frozen_inputs
        ],
        "request_attestation": {
            **bundle["hashes"],
            "wire_projection": bundle["request_contract"]["wire_projection"],
        },
        "operator": {
            "model": MODEL,
            "provider_order": ["google-vertex/global"],
            "provider_only": ["google-vertex"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr_claimed": False,
            "wire_mode": "strict_json_schema",
            "reasoning_effort": "low",
            "reasoning_content_excluded": True,
            "seed": 3101,
            "maximum_output_tokens": 4000,
        },
        "budget": {
            "maximum_provider_calls": MAX_PROVIDER_CALLS,
            "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
            "maximum_estimated_call_cost_usd": bundle["request_contract"][
                "maximum_estimated_call_cost_usd"
            ],
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
        },
        "execution_policy": {
            "started_record_before_transport": True,
            "durable_budget_reservation_before_transport": True,
            "exact_json_only": True,
            "canonical_projection_compiler_required": True,
            "raw_payload_or_failure_preserved": True,
            "private_provider_identifiers_excluded_from_git": True,
            "source_review_only_after_mechanical_pass": True,
            "quiet_control_authorized_now": False,
            "quiet_control_condition": (
                "all_pressure_axes_pass_and_separate_contract_frozen"
            ),
        },
        "non_claims": [
            "provider_acceptance_is_not_known_before_execution",
            "mechanical_validity_is_not_semantic_quality",
            "one_semantic_pass_would_not_prove_product_reliability",
            "available_account_balance_does_not_expand_this_budget",
        ],
    }
    authorization = {
        "schema_version": AUTHORIZATION_SCHEMA,
        "status": "authorized_once_by_founder_for_repaired_r3_pressure",
        "authorization_context": (
            "Founder confirmed the available account balance should be used wisely "
            "after being asked to authorize exactly one repaired pressure attempt."
        ),
        "contract_path": _relative(contract_path),
        "contract_sha256": "",
        "authorized_case_id": contract["case_id"],
        "maximum_provider_calls": MAX_PROVIDER_CALLS,
        "maximum_provider_reported_cost_usd": MAX_PROVIDER_COST_USD,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models_authorized": False,
        "quiet_control_authorized_now": False,
        "quiet_control_condition": "all_pressure_axes_pass_and_separate_contract_frozen",
    }
    _write(contract_path, contract)
    authorization["contract_sha256"] = _file_sha(contract_path)
    _write(authorization_path, authorization)
    validate_execution_contract(
        contract_path=contract_path,
        authorization_path=authorization_path,
    )
    return contract, authorization


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    contract_path = args.contract.resolve()
    authorization_path = args.authorization.resolve()
    if args.validate_only:
        contract, bundle = validate_execution_contract(
            contract_path=contract_path,
            authorization_path=authorization_path,
        )
        print(
            json.dumps(
                {
                    "status": "repaired_pressure_execution_contract_valid",
                    "run_id": contract["run_id"],
                    "provider_calls": 0,
                    "maximum_provider_calls": contract["budget"][
                        "maximum_provider_calls"
                    ],
                    "maximum_estimated_call_cost_usd": bundle["request_contract"][
                        "maximum_estimated_call_cost_usd"
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    build(contract_path=contract_path, authorization_path=authorization_path)
    print(
        json.dumps(
            {
                "status": "repaired_pressure_execution_frozen",
                "provider_calls": 0,
                "contract_path": _relative(contract_path),
                "authorization_path": _relative(authorization_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
