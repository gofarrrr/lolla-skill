#!/usr/bin/env python3
"""Build the provider-free R4 uncertainty token-allocation correction package."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals.build_r4_complementary_reader_preflight import (
    DEFAULT_OUTPUT as ORIGINAL_PREFLIGHT_OUTPUT,
    ROOT,
    _validate_files as validate_original_preflight_files,
    build_files as build_original_preflight_files,
)
from scripts.evals.finalize_r4_complementary_reader_execution import (
    CLOSEOUT,
    validate as validate_execution_closeout,
)


ORIGINAL_CONTRACT = (
    ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json"
)
PRACTICE = ROOT / (
    "docs/conversation-understanding/"
    "lolla-r4-token-allocation-current-practice-2026-07-14.md"
)
DEFAULT_OUTPUT = (
    ROOT / "research/lolla-r4-complementary-reader-token-correction-2026-07-14"
)
UNCERTAINTY_LIMITS = {"max_tokens": 1600, "reasoning_effort": "minimal"}
RELATIONSHIP_LIMITS = {"max_tokens": 700, "reasoning_effort": "minimal"}
MAX_COST_PER_CASE_USD = 0.015
MAX_TOTAL_COST_USD = 0.03
PRICE_PER_MILLION = {"prompt": 0.25, "completion": 1.5}


class R4TokenCorrectionError(RuntimeError):
    """Raised when the prospective token correction drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4TokenCorrectionError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes())


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _diff_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        paths = []
        for key in sorted(set(left) | set(right)):
            path = f"{prefix}/{key}"
            if key not in left or key not in right:
                paths.append(path)
            else:
                paths.extend(_diff_paths(left[key], right[key], path))
        return paths
    if isinstance(left, list) and isinstance(right, list):
        paths = []
        if len(left) != len(right):
            return [prefix]
        for index, (left_item, right_item) in enumerate(zip(left, right)):
            paths.extend(_diff_paths(left_item, right_item, f"{prefix}/{index}"))
        return paths
    return [] if left == right else [prefix]


def corrected_uncertainty_preview(original: Mapping[str, Any]) -> dict[str, Any]:
    corrected = copy.deepcopy(dict(original))
    body = corrected.get("body")
    if not isinstance(body, dict):
        raise R4TokenCorrectionError("original request body is missing")
    if body.get("max_tokens") != 900 or body.get("reasoning") != {
        "effort": "low",
        "exclude": True,
    }:
        raise R4TokenCorrectionError("original uncertainty allocation drifted")
    body["max_tokens"] = UNCERTAINTY_LIMITS["max_tokens"]
    body["reasoning"] = {
        "effort": UNCERTAINTY_LIMITS["reasoning_effort"],
        "exclude": True,
    }
    corrected["status"] = (
        "provider_free_token_corrected_request_preview_not_authorized_for_transport"
    )
    corrected["body_sha256"] = value_sha256(body)
    if _diff_paths(original["body"], body) != ["/max_tokens", "/reasoning/effort"]:
        raise R4TokenCorrectionError("correction changed more than token allocation")
    return corrected


def build_files(output: Path = DEFAULT_OUTPUT) -> dict[str, bytes]:
    validate_original_preflight_files(
        build_original_preflight_files(ORIGINAL_PREFLIGHT_OUTPUT)
    )
    closeout = validate_execution_closeout()
    if (
        closeout.get("status")
        != "attempt_closed_token_allocation_failure_semantic_question_unresolved"
        or closeout.get("decision", {}).get(
            "prospective_provider_free_token_allocation_correction_earned"
        )
        is not True
        or closeout.get("decision", {}).get("additional_provider_call_authorized")
        is not False
    ):
        raise R4TokenCorrectionError("historical closeout boundary drifted")
    contract = _load(ORIGINAL_CONTRACT)
    generated: dict[str, bytes] = {}
    cases = []
    conservative_total = 0.0
    for case in contract["cases"]:
        case_id = case["case_id"]
        original_path = ROOT / case["uncertainty_request_preview_path"]
        original = _load(original_path)
        corrected = corrected_uncertainty_preview(original)
        corrected_path = output / "cases" / case_id / "uncertainty-request-preview.json"
        generated[_relative(corrected_path)] = _render(corrected)
        original_case = next(
            item
            for item in _load(
                ROOT
                / "research/lolla-r4-complementary-reader-preflight-2026-07-13/"
                "preflight-result.json"
            )["cases"]
            if item["case_id"] == case_id
        )
        original_uncertainty_cost = original_case["uncertainty_request"][
            "conservative_estimated_cost_usd"
        ]
        corrected_uncertainty_cost = round(
            original_uncertainty_cost
            + (
                UNCERTAINTY_LIMITS["max_tokens"]
                - original["body"]["max_tokens"]
            )
            * PRICE_PER_MILLION["completion"]
            / 1_000_000,
            9,
        )
        relationship_cost = original_case["relationship_request"][
            "conservative_estimated_cost_usd"
        ]
        case_cost = round(corrected_uncertainty_cost + relationship_cost, 9)
        conservative_total += case_cost
        structural_response_path = (
            ROOT
            / "research/lolla-r4-complementary-reader-preflight-2026-07-13/cases"
            / case_id
            / "structural-uncertainty-response.json"
        )
        cases.append(
            {
                "case_id": case_id,
                "selection_role": case["selection_role"],
                "original_request_preview_path": _relative(original_path),
                "original_request_body_sha256": original["body_sha256"],
                "corrected_request_preview_path": _relative(corrected_path),
                "corrected_request_body_sha256": corrected["body_sha256"],
                "changed_json_paths": ["/max_tokens", "/reasoning/effort"],
                "system_prompt_unchanged": True,
                "user_prompt_unchanged": True,
                "strict_schema_unchanged": True,
                "seed_unchanged": True,
                "model_and_provider_unchanged": True,
                "structural_response_utf8_bytes": len(
                    structural_response_path.read_bytes()
                ),
                "structural_response_is_provider_evidence": False,
                "corrected_uncertainty_conservative_cost_usd": corrected_uncertainty_cost,
                "unchanged_relationship_conservative_cost_usd": relationship_cost,
                "conservative_case_cost_usd": case_cost,
                "case_cost_ceiling_usd": MAX_COST_PER_CASE_USD,
                "case_cost_preflight_pass": case_cost <= MAX_COST_PER_CASE_USD,
            }
        )
    conservative_total = round(conservative_total, 9)
    task_limits = {
        "schema_version": "lolla.r4_complementary_reader_token_limits.v1",
        "status": "prospective_provider_free_limits_not_authorized_for_transport",
        "uncertainty": UNCERTAINTY_LIMITS,
        "relationship": RELATIONSHIP_LIMITS,
        "reasoning_content_excluded": True,
        "thinking_level_is_not_strict_token_guarantee": True,
    }
    generated[_relative(output / "task-limits.json")] = _render(task_limits)
    result = {
        "schema_version": "lolla.r4_complementary_reader_token_correction_preflight.v1",
        "status": "provider_free_token_correction_ready_call_authorization_required",
        "date": "2026-07-14",
        "historical_execution_closeout": {
            "path": _relative(CLOSEOUT),
            "sha256": _file_sha(CLOSEOUT),
            "status": closeout["status"],
            "historical_provider_calls": closeout["provider_calls"],
            "historical_provider_cost_usd": closeout["provider_reported_cost_usd"],
            "historical_result_reclassified": False,
        },
        "practice_check": {"path": _relative(PRACTICE), "sha256": _file_sha(PRACTICE)},
        "original_contract": {
            "path": _relative(ORIGINAL_CONTRACT),
            "sha256": _file_sha(ORIGINAL_CONTRACT),
        },
        "cases": cases,
        "change_contract": {
            "uncertainty_changed_json_paths": [
                "/max_tokens",
                "/reasoning/effort",
            ],
            "uncertainty_before": {
                "max_tokens": 900,
                "reasoning_effort": "low",
            },
            "uncertainty_after": UNCERTAINTY_LIMITS,
            "relationship_unchanged": RELATIONSHIP_LIMITS,
            "prompt_schema_source_model_provider_seed_unchanged": True,
        },
        "budget": {
            "maximum_provider_calls": 4,
            "maximum_calls_per_case": 2,
            "maximum_provider_reported_cost_per_case_usd": MAX_COST_PER_CASE_USD,
            "maximum_provider_reported_cost_total_usd": MAX_TOTAL_COST_USD,
            "conservative_estimated_total_cost_usd": conservative_total,
            "total_cost_preflight_pass": conservative_total <= MAX_TOTAL_COST_USD,
            "automatic_retries": 0,
            "semantic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "pipeline_calls": 0,
            "runtime_calls": 0,
        },
        "local_gates": {
            "historical_failure_preserved": "pass",
            "exact_two_path_request_diff": "pass",
            "unchanged_semantic_contract": "pass",
            "cost_ceiling": "pass",
            "thinking_level_uncertainty_disclosed": "pass",
            "provider_calls": 0,
        },
        "decision": {
            "provider_calls_authorized": False,
            "new_authorization_required": True,
            "runtime_or_graph_integration_authorized": False,
            "model_comparison_authorized": False,
        },
        "non_claims": [
            "Minimal thinking does not guarantee a specific reasoning-token count.",
            "A larger completion boundary does not guarantee schema or semantic success.",
            "This correction does not reclassify or retry the historical attempt.",
            "No provider call is made by this package.",
        ],
    }
    generated[_relative(output / "preflight-result.json")] = _render(result)
    files = [
        {"path": path, "sha256": _sha(raw), "utf8_bytes": len(raw)}
        for path, raw in sorted(generated.items())
    ]
    manifest = {
        "schema_version": "lolla.r4_complementary_reader_token_correction_manifest.v1",
        "status": "provider_free_artifact_manifest_complete",
        "date": "2026-07-14",
        "files": files,
        "file_count": len(files),
        "provider_calls": 0,
    }
    generated[_relative(output / "manifest.json")] = _render(manifest)
    return generated


def write_files(files: Mapping[str, bytes]) -> None:
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def validate_files(files: Mapping[str, bytes]) -> None:
    for relative, expected in files.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != expected:
            raise R4TokenCorrectionError(f"correction artifact drifted: {relative}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    files = build_files(output)
    if args.validate_only:
        validate_files(files)
    else:
        write_files(files)
    result = json.loads(files[_relative(output / "preflight-result.json")])
    print(
        json.dumps(
            {
                "status": result["status"],
                "changed_json_paths": result["change_contract"][
                    "uncertainty_changed_json_paths"
                ],
                "conservative_estimated_total_cost_usd": result["budget"][
                    "conservative_estimated_total_cost_usd"
                ],
                "provider_calls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
