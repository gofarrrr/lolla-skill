#!/usr/bin/env python3
"""Validate the provider-free source review and seal the R3 pressure decision."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.r3_fresh_consumer import (  # noqa: E402
    validate_source_review,
    value_sha256,
)
from scripts.evals.run_r3_fresh_consumer_pressure import (  # noqa: E402
    validate_contract,
)


RESULT_SCHEMA = "lolla.r3_fresh_consumer_pressure_decision.v1"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_call_result(call: Mapping[str, Any]) -> None:
    observed = str(call.get("call_result_sha256", ""))
    material = {key: value for key, value in call.items() if key != "call_result_sha256"}
    if not observed or observed != value_sha256(material):
        raise ValueError("R3 pressure call-result hash is invalid")
    if call.get("status") != "pressure_response_mechanically_valid_source_review_required":
        raise ValueError("R3 pressure response is not eligible for source review")
    if call.get("provider_calls") != 1 or call.get("compiled") is None:
        raise ValueError("R3 pressure call custody is incomplete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path, required=True)
    parser.add_argument("--call-result", type=Path, required=True)
    parser.add_argument("--source-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    authorization_path = args.authorization.resolve()
    _contract, bundle = validate_contract(
        contract_path=contract_path,
        authorization_path=authorization_path,
    )
    call_path = args.call_result.resolve()
    review_path = args.source_review.resolve()
    call = _load(call_path)
    review = _load(review_path)
    _validate_call_result(call)
    validation = validate_source_review(
        review,
        bundle=bundle,
        call_result_sha256=call["call_result_sha256"],
    )
    _write(args.output.resolve() / "source-review-validation.json", validation)
    if validation["status"] != "valid":
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 1
    pressure_passed = bool(validation["pressure_case_passed"])
    result = {
        "schema_version": RESULT_SCHEMA,
        "status": (
            "pressure_case_passed_quiet_control_may_be_frozen"
            if pressure_passed
            else "pressure_case_failed_preserved_stop_provider_work"
        ),
        "case_id": bundle["case_id"],
        "bundle_sha256": bundle["bundle_sha256"],
        "call_result_path": str(call_path),
        "call_result_file_sha256": _file_sha(call_path),
        "call_result_sha256": call["call_result_sha256"],
        "source_review_path": str(review_path),
        "source_review_file_sha256": _file_sha(review_path),
        "source_review_validation": validation,
        "pressure_case_passed": pressure_passed,
        "quiet_control_authorized": pressure_passed,
        "provider_calls_made": 1,
        "provider_reported_cost_usd": call.get("provider_reported_cost_usd"),
        "scalar_quality_score": None,
        "runtime_effect": "none",
        "non_claims": [
            "one_pressure_case_is_not_product_reliability",
            "source_review_is_not_human_outcome_validation",
            "quiet_control_requires_a_new_frozen_contract_before_transport",
        ],
    }
    result["result_sha256"] = value_sha256(result)
    _write(args.output.resolve() / "pressure-decision.json", result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "pressure_case_passed": pressure_passed,
                "quiet_control_authorized": pressure_passed,
                "provider_calls_made": 1,
                "provider_reported_cost_usd": call.get("provider_reported_cost_usd"),
                "result_sha256": result["result_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
