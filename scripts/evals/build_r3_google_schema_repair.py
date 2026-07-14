#!/usr/bin/env python3
"""Build and freeze the zero-call R3 Google-schema interoperability repair."""

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

from engine.system_b.r3_fresh_consumer import value_sha256  # noqa: E402
from engine.system_b.r3_google_schema_projection import (  # noqa: E402
    PROJECTION_SCHEMA,
    R3GoogleProjectionError,
    build_projection_bundle,
    lint_google_documented_schema_subset,
    schema_metrics,
    validate_projection_bundle,
)


CONTRACT_SCHEMA = "lolla.r3_google_schema_repair_contract.v1"
BASE_BUNDLE = ROOT / (
    "research/lolla-r3-fresh-consumer-2026-07-13/preflight/pressure-bundle.json"
)
REFERENCE_ROLE_BUNDLE = ROOT / (
    "research/simulated-reliability-corpus-v1-2026-07-12/"
    "provider-free-role-input-preflight/transfer/"
    "v1-case06-industry-funded-lab/role-request-bundle.json"
)
REFERENCE_CALL_RESULT = ROOT / (
    "research/simulated-reliability-v1-model-value-probe-2026-07-13/a1/"
    "gemini-3-1-flash-lite-vertex-starting/call-01-starting-result.json"
)
ENDPOINT_VERIFICATION = ROOT / (
    "research/lolla-r3-fresh-consumer-2026-07-13/preflight/"
    "provider-endpoint-verification.json"
)
PROJECTION_MODULE = ROOT / "engine/system_b/r3_google_schema_projection.py"
BUILDER_SCRIPT = ROOT / "scripts/evals/build_r3_google_schema_repair.py"


class R3GoogleRepairBuildError(RuntimeError):
    """Raised when the provider-free repair evidence is inconsistent."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3GoogleRepairBuildError(f"expected JSON object: {path}")
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


def _operational_reference() -> dict[str, Any]:
    role_bundle = _load(REFERENCE_ROLE_BUNDLE)
    result = _load(REFERENCE_CALL_RESULT)
    schema = role_bundle.get("requests", {}).get("starting", {}).get("response_schema")
    if not isinstance(schema, Mapping):
        raise R3GoogleRepairBuildError("successful reference schema is missing")
    schema_sha = value_sha256(schema)
    if (
        result.get("operational_status") != "ok"
        or result.get("validation_error") != ""
        or result.get("provider_calls") != 1
        or result.get("requested_model") != "google/gemini-3.1-flash-lite"
        or result.get("served_model") != "google/gemini-3.1-flash-lite"
        or result.get("served_provider") != "Google"
        or result.get("response_schema_sha256") != schema_sha
    ):
        raise R3GoogleRepairBuildError("successful Gemini reference custody drifted")
    endpoint = _load(ENDPOINT_VERIFICATION)
    selected = endpoint.get("selected_endpoint", {})
    supported = set(selected.get("supported_parameters", []))
    required_parameters = {
        "reasoning",
        "max_tokens",
        "seed",
        "response_format",
        "structured_outputs",
        "reasoning_effort",
    }
    if (
        endpoint.get("status") != "verified_before_pressure_call"
        or endpoint.get("model") != "google/gemini-3.1-flash-lite"
        or selected.get("tag") != "google-vertex/global"
        or required_parameters - supported
    ):
        raise R3GoogleRepairBuildError("current endpoint capability custody drifted")
    return {
        "status": "historical_smaller_schema_operational_success",
        "role_bundle_path": _relative(REFERENCE_ROLE_BUNDLE),
        "role_bundle_file_sha256": _file_sha(REFERENCE_ROLE_BUNDLE),
        "call_result_path": _relative(REFERENCE_CALL_RESULT),
        "call_result_file_sha256": _file_sha(REFERENCE_CALL_RESULT),
        "response_schema_sha256": schema_sha,
        "requested_model": result["requested_model"],
        "served_model": result["served_model"],
        "served_provider": result["served_provider"],
        "provider_reported_cost_usd": result.get("provider_reported_cost_usd"),
        "metrics": schema_metrics(schema),
        "documented_subset_lint": lint_google_documented_schema_subset(schema),
        "current_endpoint_verification": {
            "path": _relative(ENDPOINT_VERIFICATION),
            "file_sha256": _file_sha(ENDPOINT_VERIFICATION),
            "verified_at_date": endpoint.get("verified_at_date"),
            "model": endpoint["model"],
            "provider_tag": selected["tag"],
            "required_parameters_present": sorted(required_parameters),
            "provider_calls": endpoint.get("provider_calls"),
        },
        "non_claim": (
            "Historical provider acceptance does not prove that undocumented keywords "
            "remain accepted or identify the cause of the failed R3 request."
        ),
    }


def build() -> dict[str, Any]:
    base_bundle = _load(BASE_BUNDLE)
    operational_reference = _operational_reference()
    bundle = build_projection_bundle(
        base_bundle=base_bundle,
        operational_reference=operational_reference,
    )
    comparison = bundle["schema_comparison"]
    projected = comparison["projected_schema"]
    failed = comparison["failed_r3_schema"]
    reference = comparison["operational_smaller_reference"]["metrics"]
    if projected["total_object_properties"] > reference["total_object_properties"]:
        raise R3GoogleRepairBuildError(
            "projected schema exceeds the successful smaller reference property count"
        )
    if projected["string_length_constraint_count"] != 0:
        raise R3GoogleRepairBuildError("projected schema retained string length constraints")
    if projected["total_object_properties"] >= failed["total_object_properties"]:
        raise R3GoogleRepairBuildError("projected schema did not reduce failed R3 properties")
    summary = {
        "schema_version": "lolla.r3_google_schema_repair_preflight.v1",
        "status": "provider_free_repair_complete_no_call_authorized",
        "case_id": bundle["case_id"],
        "base_r3_bundle_sha256": bundle["base_r3_bundle_sha256"],
        "projection_bundle_sha256": bundle["bundle_sha256"],
        "projection_schema_sha256": bundle["hashes"]["response_schema_sha256"],
        "request_body_sha256": bundle["hashes"]["request_body_sha256"],
        "maximum_estimated_call_cost_usd": bundle["request_contract"][
            "maximum_estimated_call_cost_usd"
        ],
        "provider_calls": 0,
        "next_call_authorized": False,
        "custody": {
            "source_packet_unchanged": True,
            "active_pressure_count": len(
                bundle["packet"]["constitutional_graph_survival"][
                    "active_pressure_items"
                ]
            ),
            "candidate_deletion_allowed": False,
            "canonical_compiler_reused": True,
            "semantic_applicability_inferred_by_code": False,
        },
        "schema_delta": {
            "failed_r3_total_properties": failed["total_object_properties"],
            "projected_total_properties": projected["total_object_properties"],
            "successful_reference_total_properties": reference[
                "total_object_properties"
            ],
            "failed_r3_string_length_constraints": failed[
                "string_length_constraint_count"
            ],
            "projected_string_length_constraints": projected[
                "string_length_constraint_count"
            ],
            "documented_subset_lint": bundle["documented_subset_lint"]["status"],
        },
        "semantic_exit_condition_met": False,
        "reason": "No provider call or candidate exists for semantic review.",
    }
    return {
        "bundle": bundle,
        "lint": bundle["documented_subset_lint"],
        "comparison": comparison,
        "summary": summary,
    }


def build_contract(*, output: Path, bundle: Mapping[str, Any]) -> dict[str, Any]:
    bundle_path = output / "prospective-pressure-bundle.json"
    frozen_inputs = [
        BASE_BUNDLE,
        REFERENCE_ROLE_BUNDLE,
        REFERENCE_CALL_RESULT,
        ENDPOINT_VERIFICATION,
        PROJECTION_MODULE,
        BUILDER_SCRIPT,
    ]
    contract = {
        "schema_version": CONTRACT_SCHEMA,
        "status": "frozen_provider_free_repair_no_call_authorized",
        "case_id": bundle["case_id"],
        "purpose": (
            "Prospective Google documented-subset wire repair for the preserved failed R3 "
            "request; this contract does not authorize provider work."
        ),
        "failed_r3_bundle": {
            "path": _relative(BASE_BUNDLE),
            "file_sha256": _file_sha(BASE_BUNDLE),
            "bundle_sha256": bundle["base_r3_bundle_sha256"],
        },
        "frozen_inputs": [
            {"path": _relative(path), "sha256": _file_sha(path)}
            for path in frozen_inputs
        ],
        "prospective_bundle": {
            "path": _relative(bundle_path),
            "file_sha256": _file_sha(bundle_path),
            "bundle_sha256": bundle["bundle_sha256"],
        },
        "request_attestation": {
            **bundle["hashes"],
            "wire_projection": PROJECTION_SCHEMA,
        },
        "preservation_contract": {
            "source_packet_unchanged": True,
            "original_answer_unchanged": True,
            "all_nine_active_pressure_ids_required": True,
            "reserve_custody_unchanged": True,
            "apply_reject_park_required": True,
            "canonical_compiler_reused": True,
            "semantic_applicability_inferred_by_code": False,
            "keyword_or_chronology_gate_added": False,
        },
        "provider_boundary": {
            "provider_calls_made": 0,
            "provider_calls_authorized": 0,
            "next_call_authorized": False,
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "premium_models_authorized": False,
            "maximum_future_attempts_without_new_authorization": 0,
        },
        "non_claims": [
            "documented_subset_lint_is_not_provider_acceptance_proof",
            "historical_smaller_schema_success_does_not_identify_the_failed_argument",
            "provider_free_repair_is_not_semantic_product_evidence",
            "prospective_request_is_not_authorized_for_execution",
        ],
    }
    return contract


def validate_contract(contract_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = _load(contract_path)
    if (
        contract.get("schema_version") != CONTRACT_SCHEMA
        or contract.get("status") != "frozen_provider_free_repair_no_call_authorized"
    ):
        raise R3GoogleRepairBuildError("repair contract is not frozen provider-free")
    for item in contract.get("frozen_inputs", []):
        path = ROOT / str(item.get("path", ""))
        if not path.is_file() or _file_sha(path) != item.get("sha256"):
            raise R3GoogleRepairBuildError(f"repair frozen input drifted: {item.get('path')}")
    base_bundle = _load(ROOT / contract["failed_r3_bundle"]["path"])
    bundle_path = ROOT / contract["prospective_bundle"]["path"]
    if not bundle_path.is_file() or _file_sha(bundle_path) != contract[
        "prospective_bundle"
    ]["file_sha256"]:
        raise R3GoogleRepairBuildError("prospective bundle file drifted")
    bundle = _load(bundle_path)
    validate_projection_bundle(bundle, base_bundle=base_bundle)
    expected_bundle = build()["bundle"]
    if bundle != expected_bundle:
        raise R3GoogleRepairBuildError("prospective bundle drifted from provider-free build")
    if bundle["bundle_sha256"] != contract["prospective_bundle"]["bundle_sha256"]:
        raise R3GoogleRepairBuildError("prospective bundle identity drifted")
    expected_attestation = {**bundle["hashes"], "wire_projection": PROJECTION_SCHEMA}
    if contract.get("request_attestation") != expected_attestation:
        raise R3GoogleRepairBuildError("prospective request attestation drifted")
    boundary = contract.get("provider_boundary", {})
    if (
        boundary.get("provider_calls_made") != 0
        or boundary.get("provider_calls_authorized") != 0
        or boundary.get("next_call_authorized") is not False
        or boundary.get("maximum_future_attempts_without_new_authorization") != 0
    ):
        raise R3GoogleRepairBuildError("repair contract authorizes provider work")
    return contract, bundle


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    contract_path = args.contract.resolve()
    if args.validate_only:
        contract, bundle = validate_contract(contract_path)
        print(
            json.dumps(
                {
                    "status": "provider_free_repair_contract_valid",
                    "provider_calls": 0,
                    "bundle_sha256": bundle["bundle_sha256"],
                    "request_body_sha256": bundle["hashes"]["request_body_sha256"],
                    "next_call_authorized": contract["provider_boundary"][
                        "next_call_authorized"
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise R3GoogleRepairBuildError("repair output directory must be empty")
    output.mkdir(parents=True, exist_ok=True)
    artifacts = build()
    _write(output / "prospective-pressure-bundle.json", artifacts["bundle"])
    _write(output / "documented-subset-lint.json", artifacts["lint"])
    _write(output / "schema-comparison.json", artifacts["comparison"])
    _write(output / "preflight-summary.json", artifacts["summary"])
    contract = build_contract(output=output, bundle=artifacts["bundle"])
    _write(contract_path, contract)
    validate_contract(contract_path)
    print(json.dumps(artifacts["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
