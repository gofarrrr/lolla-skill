#!/usr/bin/env python3
"""Seal the first R4 complementary-reader execution without semantic rescue."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals.run_r4_complementary_reader_experiment import (
    _validate_authorization,
    _validate_contract,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json"
AUTHORIZATION = ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-authorization-a1.json"
OUTPUT = ROOT / "research/lolla-r4-complementary-reader-execution-2026-07-14-a1"
RUN_RESULT = OUTPUT / "result.json"
MANIFEST = OUTPUT / "evidence-manifest.json"
SOURCE_REVIEW = OUTPUT / "source-first-review.json"
CLOSEOUT = OUTPUT / "execution-closeout.json"

MODEL = "google/gemini-3.1-flash-lite"
PROVIDER = "Google"
EXPECTED = {
    "v1-case02-discharge-transport": {
        "ordinal": 1,
        "cost": 0.004387,
        "completion_tokens": 885,
        "reasoning_tokens": 865,
        "raw_content_sha256": "819c037b2060bf45ea7cafd99d806e166c7e90a089dd9210731fd473c9117f6b",
    },
    "v1-case03-executive-hire": {
        "ordinal": 2,
        "cost": 0.004649,
        "completion_tokens": 886,
        "reasoning_tokens": 861,
        "raw_content_sha256": "9f48aaebc8d1bacd9466646760a3753b24528c6d5c2cbc9a91e3227b75abb2d6",
    },
}
EVIDENCE_FILES = (
    CONTRACT,
    AUTHORIZATION,
    RUN_RESULT,
    *(
        path
        for case_id, expected in EXPECTED.items()
        for path in (
            OUTPUT / case_id / "uncertainty-request.json",
            OUTPUT
            / case_id
            / f"call-{expected['ordinal']:02d}-uncertainty-started.json",
            OUTPUT
            / case_id
            / f"call-{expected['ordinal']:02d}-uncertainty-result.json",
            OUTPUT / case_id / "final-fan-in.json",
        )
    ),
)


class R4ExecutionCloseoutError(RuntimeError):
    """Raised when the frozen execution evidence no longer matches the closeout."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4ExecutionCloseoutError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_render(value))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _call_observation(case_id: str, expected: Mapping[str, Any]) -> dict[str, Any]:
    ordinal = int(expected["ordinal"])
    case_dir = OUTPUT / case_id
    started_path = case_dir / f"call-{ordinal:02d}-uncertainty-started.json"
    result_path = case_dir / f"call-{ordinal:02d}-uncertainty-result.json"
    request_path = case_dir / "uncertainty-request.json"
    started = _load(started_path)
    result = _load(result_path)
    request = _load(request_path)
    usage = result.get("usage")
    if not isinstance(usage, Mapping):
        raise R4ExecutionCloseoutError(f"usage missing: {case_id}")
    details = usage.get("completion_tokens_details")
    if not isinstance(details, Mapping):
        raise R4ExecutionCloseoutError(f"completion details missing: {case_id}")
    completion_tokens = usage.get("completion_tokens")
    reasoning_tokens = details.get("reasoning_tokens")
    raw_content = result.get("raw_content")
    if not isinstance(raw_content, str):
        raise R4ExecutionCloseoutError(f"raw content missing: {case_id}")
    if (
        started.get("status") != "started_before_network_transport"
        or result.get("operational_status") != "candidate_parse_failed"
        or result.get("provider_calls") != 1
        or result.get("served_model") != MODEL
        or result.get("served_provider") != PROVIDER
        or result.get("operator_attribution_ok") is not True
        or result.get("finish_reason") != "length"
        or result.get("candidate") is not None
        or not str(result.get("parse_error", "")).startswith("JSONDecodeError:")
        or result.get("provider_reported_cost_usd") != expected["cost"]
        or usage.get("cost") != expected["cost"]
        or completion_tokens != expected["completion_tokens"]
        or reasoning_tokens != expected["reasoning_tokens"]
        or result.get("raw_content_sha256") != expected["raw_content_sha256"]
        or hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
        != expected["raw_content_sha256"]
        or result.get("reasoning_effort") != "low"
        or result.get("max_output_tokens") != 900
        or result.get("reasoning_content_excluded") is not True
        or result.get("reasoning_content_returned") is not False
        or request.get("body_sha256") != result.get("request_body_sha256")
        or started.get("request_body_sha256") != result.get("request_body_sha256")
    ):
        raise R4ExecutionCloseoutError(f"frozen call evidence drifted: {case_id}")
    remainder = int(completion_tokens) - int(reasoning_tokens)
    return {
        "case_id": case_id,
        "selection_role": (
            "exposed_false_stand_down_target"
            if case_id == "v1-case02-discharge-transport"
            else "matched_restraint_control"
        ),
        "call_ordinal": ordinal,
        "requested_and_served_model": MODEL,
        "served_provider": PROVIDER,
        "operator_attribution_ok": True,
        "finish_reason": "length",
        "operational_status": "candidate_parse_failed",
        "candidate_admitted": False,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "non_reasoning_completion_token_remainder": remainder,
        "reasoning_share_of_completion": round(
            int(reasoning_tokens) / int(completion_tokens), 6
        ),
        "provider_reported_cost_usd": expected["cost"],
        "request_body_sha256": result["request_body_sha256"],
        "raw_content_sha256": expected["raw_content_sha256"],
        "raw_partial_content_used_as_semantic_evidence": False,
    }


def _build_values() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = _validate_contract(CONTRACT)
    _validate_authorization(
        AUTHORIZATION, contract=contract, contract_path=CONTRACT
    )
    result = _load(RUN_RESULT)
    if (
        result.get("status")
        != "provider_calls_preserved_source_first_review_required"
        or result.get("provider_calls") != 2
        or result.get("provider_reported_cost_usd") != 0.009036
        or result.get("cost_ceiling_met") is not True
        or result.get("cost_custody_known") is not True
        or result.get("fallback_models") != 0
        or result.get("automatic_retries") != 0
        or result.get("semantic_retries") != 0
        or result.get("response_healing") is not False
        or result.get("evaluator_calls") != 0
        or result.get("embedding_calls") != 0
        or result.get("graph_calls") != 0
        or result.get("pipeline_calls") != 0
        or result.get("runtime_calls") != 0
    ):
        raise R4ExecutionCloseoutError("terminal runner result drifted")
    observations = [
        _call_observation(case_id, expected)
        for case_id, expected in EXPECTED.items()
    ]
    if any(OUTPUT.glob("*/call-*-relationship-*.json")):
        raise R4ExecutionCloseoutError("unexpected relationship call artifact")
    evidence_rows = []
    for path in EVIDENCE_FILES:
        if not path.is_file():
            raise R4ExecutionCloseoutError(f"evidence missing: {_relative(path)}")
        evidence_rows.append(
            {
                "path": _relative(path),
                "sha256": _file_sha(path),
                "utf8_bytes": len(path.read_bytes()),
            }
        )
    manifest: dict[str, Any] = {
        "schema_version": "lolla.r4_complementary_reader_execution_manifest.v1",
        "status": "exact_execution_evidence_preserved",
        "date": "2026-07-14",
        "files": evidence_rows,
        "file_count": len(evidence_rows),
        "provider_calls": 2,
        "provider_reported_cost_usd": 0.009036,
    }
    manifest["manifest_sha256"] = value_sha256(manifest)
    dimensions = [
        {
            "dimension": dimension,
            "verdict": "not_evaluable_no_admitted_uncertainty_candidate",
            "why": (
                "Both uncertainty responses ended at the completion limit before "
                "a JSON object could be parsed or locally admitted. Partial raw "
                "text is preserved but is not treated as semantic evidence."
            ),
        }
        for dimension in (
            "material_pressure_recovered",
            "false_positive_restraint",
            "evidence_precision",
            "role_placement",
            "relationship_fidelity",
        )
    ]
    dimensions.append(
        {
            "dimension": "operational_load_and_cost",
            "verdict": "observed_exactly",
            "why": (
                "Two attributable calls cost $0.009036; both exhausted the "
                "uncertainty completion boundary and the relationship stage was "
                "correctly skipped."
            ),
        }
    )
    source_review: dict[str, Any] = {
        "schema_version": "lolla.r4_complementary_reader_source_first_review.v1",
        "status": "semantic_question_unresolved_operational_gate_failed",
        "date": "2026-07-14",
        "source_first_target_path": _relative(
            ROOT / contract["source_first_target"]["path"]
        ),
        "source_first_target_visible_to_provider": False,
        "evidence_manifest_sha256": manifest["manifest_sha256"],
        "dimensions": dimensions,
        "semantic_review_performed": False,
        "partial_raw_content_reviewed_for_semantic_pass": False,
        "relationship_review_performed": False,
        "scalar_quality_score": None,
        "conclusion": (
            "The run is an operational negative result. It cannot support a "
            "discovery, restraint, relationship, usefulness, or model-quality claim."
        ),
    }
    source_review["result_sha256"] = value_sha256(source_review)
    closeout: dict[str, Any] = {
        "schema_version": "lolla.r4_complementary_reader_execution_closeout.v1",
        "status": "attempt_closed_token_allocation_failure_semantic_question_unresolved",
        "date": "2026-07-14",
        "run_id": contract["run_id"],
        "contract_sha256": _file_sha(CONTRACT),
        "authorization_sha256": _file_sha(AUTHORIZATION),
        "evidence_manifest_sha256": manifest["manifest_sha256"],
        "source_first_review_sha256": source_review["result_sha256"],
        "provider_calls": 2,
        "maximum_provider_calls": 4,
        "relationship_calls": 0,
        "provider_reported_cost_usd": 0.009036,
        "maximum_provider_reported_cost_total_usd": 0.03,
        "cost_ceiling_met": True,
        "call_observations": observations,
        "mechanical_conclusion": {
            "request_schema_and_operator_reached": True,
            "strict_json_candidate_parsed": False,
            "uncertainty_candidate_admitted": False,
            "relationship_dependency_opened": False,
            "stop_rule_worked": True,
        },
        "bounded_diagnosis": {
            "observed": (
                "The low-thinking uncertainty calls used 865/885 and 861/886 "
                "completion tokens for reasoning, then ended with finish_reason "
                "length and unterminated JSON."
            ),
            "inference": (
                "The 900-token completion ceiling did not leave adequate final-JSON "
                "capacity for this full-source task."
            ),
            "not_established": [
                "that the schema is too complex",
                "that the full-source packet is semantically too difficult",
                "that Gemini 3.1 Flash-Lite cannot perform the reader",
                "that either partial record was source-grounded or materially useful",
                "that the restraint control would have passed or failed",
            ],
        },
        "preserved_boundaries": {
            "automatic_retry_performed": False,
            "semantic_retry_performed": False,
            "fallback_or_model_switch_performed": False,
            "response_healing_performed": False,
            "partial_json_rescued": False,
            "runtime_or_graph_integration_performed": False,
        },
        "decision": {
            "this_attempt_may_be_retried": False,
            "additional_provider_call_authorized": False,
            "prospective_provider_free_token_allocation_correction_earned": True,
            "semantic_hypothesis_resolved": False,
        },
    }
    closeout["result_sha256"] = value_sha256(closeout)
    return manifest, source_review, closeout


def build() -> dict[str, Any]:
    manifest, source_review, closeout = _build_values()
    _write(MANIFEST, manifest)
    _write(SOURCE_REVIEW, source_review)
    _write(CLOSEOUT, closeout)
    return closeout


def validate() -> dict[str, Any]:
    expected = _build_values()
    for path, value in zip((MANIFEST, SOURCE_REVIEW, CLOSEOUT), expected):
        if not path.is_file() or path.read_bytes() != _render(value):
            raise R4ExecutionCloseoutError(f"closeout artifact drifted: {_relative(path)}")
    for path, hash_field in (
        (MANIFEST, "manifest_sha256"),
        (SOURCE_REVIEW, "result_sha256"),
        (CLOSEOUT, "result_sha256"),
    ):
        value = _load(path)
        if value.get(hash_field) != value_sha256(_without(value, hash_field)):
            raise R4ExecutionCloseoutError(f"self-hash drifted: {_relative(path)}")
    return expected[-1]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    result = validate() if args.validate_only else build()
    print(
        json.dumps(
            {
                "status": result["status"],
                "provider_calls": result["provider_calls"],
                "provider_reported_cost_usd": result[
                    "provider_reported_cost_usd"
                ],
                "semantic_hypothesis_resolved": result["decision"][
                    "semantic_hypothesis_resolved"
                ],
                "additional_provider_call_authorized": result["decision"][
                    "additional_provider_call_authorized"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
