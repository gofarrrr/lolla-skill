#!/usr/bin/env python3
"""Seal the exact raw evidence from R4 matched-holdout v2 execution A1."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals.run_r4_matched_holdout_v2_experiment import (
    expected_authorization,
    validate_authorization,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
OUTPUT = ROOT / (
    "research/lolla-r4-matched-holdout-v2-execution-2026-07-14-a1"
)
RUN_RESULT = OUTPUT / "result.json"
RAW_MANIFEST = OUTPUT / "raw-evidence-manifest.json"
AUTHORIZATION_CONSUMPTION = OUTPUT / "authorization-consumption.json"
AUTHORIZATION_SHA256 = (
    "3cfe4f0fa5d4be3b8941ca54e9f0fcc4f25c17f354788ff9db8c995366ddd49d"
)
CONTRACT_SHA256 = (
    "92b7a52a3f05905b6b6ab2d45016d3cabf2841261ac41d8479d82477d9179a5f"
)
CANONICAL_BASE_COMMIT = "b7d1d62c05bdf05f91401c25ceb0a2cc73ffe307"
TOTAL_COST_USD = 0.01408165


class R4MatchedExecutionA1SealError(RuntimeError):
    """Raised when the terminal A1 execution evidence drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4MatchedExecutionA1SealError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_render(value))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise R4MatchedExecutionA1SealError(message)


def _build_raw_values(
    *, output: Path = OUTPUT
) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = validate_contract(CONTRACT)
    _require(_file_sha(CONTRACT) == CONTRACT_SHA256, "contract hash drifted")
    run_result_path = output / "result.json"
    run = _load(run_result_path)
    calls = run.get("calls")
    _require(
        run.get("status") == "matched_execution_complete"
        and run.get("provider_calls") == 8
        and run.get("provider_reported_cost_usd") == TOTAL_COST_USD
        and run.get("call_ordinals") == list(range(1, 9))
        and isinstance(calls, list)
        and len(calls) == 8,
        "terminal run result drifted",
    )
    _require(
        run.get("first_failure_stopped_further_transport") is False,
        "unexpected stopped-run state",
    )
    prohibited = {
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "relationship_calls": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    _require(
        all(run.get(key) == value for key, value in prohibited.items()),
        "prohibited execution count drifted",
    )

    observations: list[dict[str, Any]] = []
    for planned, call in zip(contract["call_plan"], calls, strict=True):
        ordinal = int(planned["ordinal"])
        started_path = output / f"call-{ordinal:02d}-started.json"
        result_path = output / f"call-{ordinal:02d}-result.json"
        raw_path = output / f"call-{ordinal:02d}-raw-response.bin"
        started = _load(started_path)
        call_result = _load(result_path)
        raw_sha = _file_sha(raw_path)
        raw_bytes = len(raw_path.read_bytes())
        usage = call.get("usage")
        completion_details = (
            usage.get("completion_tokens_details", {})
            if isinstance(usage, Mapping)
            else {}
        )
        _require(
            call.get("ordinal") == ordinal
            and call.get("case_id") == planned["case_id"]
            and call.get("arm") == planned["arm"]
            and call.get("request_body_sha256")
            == planned["request_body_sha256"]
            and started.get("request_body_sha256")
            == planned["request_body_sha256"]
            and call_result.get("request_body_sha256")
            == planned["request_body_sha256"],
            f"request identity drifted at ordinal {ordinal}",
        )
        _require(
            started.get("status") == "started_before_transport"
            and call.get("provider_calls") == 1
            and call.get("operational_status") == "completed"
            and call.get("terminal") is True
            and call.get("first_terminal_provider_result_preserved_exactly")
            is True
            and call.get("operator_attribution_ok") is True
            and call.get("served_provider") == "Google"
            and call.get("served_model")
            in contract["operator"]["allowed_served_model_ids"]
            and call.get("local_admission_status") == "passed"
            and call.get("finish_reason") == "stop"
            and call.get("failure_detail") == "",
            f"terminal custody drifted at ordinal {ordinal}",
        )
        _require(
            call_result == call,
            f"call result differs from aggregate result at ordinal {ordinal}",
        )
        _require(
            raw_sha == call.get("raw_response_sha256")
            and raw_bytes == call.get("raw_response_utf8_bytes"),
            f"raw response drifted at ordinal {ordinal}",
        )
        reasoning = call.get("reasoning_custody", {})
        _require(
            isinstance(reasoning, Mapping)
            and reasoning.get("status") == "reasoning_metadata_only"
            and reasoning.get("exclusion_satisfied") is True
            and reasoning.get("content_present") is False
            and reasoning.get("metadata_only") is True
            and call.get("reasoning_values_copied_to_result") is False
            and completion_details.get("reasoning_tokens") == 0,
            f"reasoning custody drifted at ordinal {ordinal}",
        )
        observations.append(
            {
                "ordinal": ordinal,
                "case_id": call["case_id"],
                "arm": call["arm"],
                "request_body_sha256": call["request_body_sha256"],
                "generation_id": call["generation_id"],
                "served_model": call["served_model"],
                "served_provider": call["served_provider"],
                "operator_attribution_ok": call["operator_attribution_ok"],
                "local_admission_status": call["local_admission_status"],
                "finish_reason": call["finish_reason"],
                "prompt_tokens": usage["prompt_tokens"],
                "completion_tokens": usage["completion_tokens"],
                "reasoning_tokens": completion_details["reasoning_tokens"],
                "total_tokens": usage["total_tokens"],
                "provider_reported_cost_usd": call[
                    "provider_reported_cost_usd"
                ],
                "raw_response_path": call["raw_response_path"],
                "raw_response_sha256": raw_sha,
                "raw_response_utf8_bytes": raw_bytes,
                "raw_response_preserved_exactly": True,
                "candidate_sha256": call["candidate_sha256"],
                "usage_sha256": call["usage_sha256"],
                "started_file_sha256": _file_sha(started_path),
                "result_file_sha256": _file_sha(result_path),
            }
        )

    runner_files = sorted(output.glob("call-*") ) + [run_result_path]
    _require(len(runner_files) == 25, "runner evidence file inventory drifted")
    files = [
        {
            "path": _relative(path),
            "sha256": _file_sha(path),
            "utf8_bytes": len(path.read_bytes()),
        }
        for path in runner_files
    ]
    consumption: dict[str, Any] = {
        "schema_version": "lolla.r4_matched_residual_authorization_consumption.v2",
        "status": "consumed_terminal_run_complete",
        "date": "2026-07-14",
        "run_id": contract["run_id"],
        "authorization_sha256": AUTHORIZATION_SHA256,
        "authorization_exact_object_validated_before_transport": True,
        "provider_transport_constructed": True,
        "provider_calls_attempted": 8,
        "provider_calls_completed": 8,
        "terminal_run_status": run["status"],
        "consumed_reason": "all_eight_authorized_calls_attempted_and_completed",
        "second_execution_authorized": False,
        "retry_or_replacement_call_authorized": False,
        "provider_reported_cost_usd": TOTAL_COST_USD,
        "hard_provider_reported_cost_total_usd": 0.12,
    }
    consumption["record_sha256"] = value_sha256(consumption)
    manifest: dict[str, Any] = {
        "schema_version": "lolla.r4_matched_residual_raw_evidence_manifest.v2",
        "status": "raw_execution_sealed_before_semantic_review",
        "date": "2026-07-14",
        "run_id": contract["run_id"],
        "canonical_base_commit": CANONICAL_BASE_COMMIT,
        "contract_sha256": CONTRACT_SHA256,
        "authorization_sha256": AUTHORIZATION_SHA256,
        "run_result_file_sha256": _file_sha(run_result_path),
        "files": files,
        "file_count": len(files),
        "calls": observations,
        "provider_calls": 8,
        "provider_reported_cost_usd": TOTAL_COST_USD,
        "case_costs_usd": run["case_costs_usd"],
        "authorization_consumed": True,
        "semantic_review_started": False,
        "scalar_score": None,
    }
    manifest["manifest_sha256"] = value_sha256(manifest)
    return manifest, consumption


def seal_raw(authorization_path: Path) -> dict[str, Any]:
    contract = validate_contract(CONTRACT)
    validate_authorization(authorization_path, contract=contract)
    if _file_sha(authorization_path) != AUTHORIZATION_SHA256:
        raise R4MatchedExecutionA1SealError("authorization byte hash drifted")
    if _load(authorization_path) != expected_authorization(contract=contract):
        raise R4MatchedExecutionA1SealError("authorization object drifted")
    manifest, consumption = _build_raw_values()
    _write(AUTHORIZATION_CONSUMPTION, consumption)
    _write(RAW_MANIFEST, manifest)
    return {
        "status": manifest["status"],
        "provider_calls": manifest["provider_calls"],
        "provider_reported_cost_usd": manifest[
            "provider_reported_cost_usd"
        ],
        "authorization_consumed": manifest["authorization_consumed"],
    }


def validate_raw() -> dict[str, Any]:
    manifest, consumption = _build_raw_values()
    for path, expected in (
        (RAW_MANIFEST, manifest),
        (AUTHORIZATION_CONSUMPTION, consumption),
    ):
        if not path.is_file() or path.read_bytes() != _render(expected):
            raise R4MatchedExecutionA1SealError(
                f"sealed custody artifact drifted: {_relative(path)}"
            )
    if manifest["manifest_sha256"] != value_sha256(
        _without(manifest, "manifest_sha256")
    ):
        raise R4MatchedExecutionA1SealError("raw manifest self-hash drifted")
    if consumption["record_sha256"] != value_sha256(
        _without(consumption, "record_sha256")
    ):
        raise R4MatchedExecutionA1SealError(
            "authorization consumption self-hash drifted"
        )
    return {
        "status": manifest["status"],
        "provider_calls": manifest["provider_calls"],
        "provider_reported_cost_usd": manifest[
            "provider_reported_cost_usd"
        ],
        "authorization_consumed": manifest["authorization_consumed"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorization-path", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if args.validate_only:
        result = validate_raw()
    else:
        if args.authorization_path is None:
            parser.error("--authorization-path is required when sealing")
        result = seal_raw(args.authorization_path)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
