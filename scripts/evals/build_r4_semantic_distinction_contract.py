#!/usr/bin/env python3
"""Build the provider-free R4 semantic-distinction contract and preflight."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.conversation_state_fan_in import build_source_registry
from engine.system_b.r4_complementary_readers import (
    RELATIONSHIP_PACKET_SCHEMA,
    UNCERTAINTY_PACKET_SCHEMA,
    build_source_registry_v1,
    build_uncertainty_packet_v1,
    canonical_json_bytes,
    compile_relationship_response_v1,
    compile_uncertainty_response_v1,
    planned_readers_v1,
    relationship_response_schema_v1,
    uncertainty_response_schema_v1,
    value_sha256,
)
from engine.system_b.r4_semantic_distinction import (
    SEMANTIC_DISTINCTION_PROMPT_CONTRACT,
    build_relationship_prompts_v2,
    build_uncertainty_prompts_v2,
    inspect_r4_reasoning_exclusion_v1,
)
from scripts.evals import build_r4_complementary_reader_preflight as base


ROOT = Path(__file__).resolve().parents[2]
HOLDOUT = ROOT / "docs/evals/lolla-r4-semantic-distinction-holdout-target-v1.json"
FIXTURES = ROOT / "tests/fixtures/r4_semantic_distinction/contract-fixtures-v1.json"
PRACTICE = ROOT / (
    "docs/conversation-understanding/"
    "lolla-r4-semantic-distinction-current-practice-2026-07-14.md"
)
MODULE = ROOT / "engine/system_b/r4_semantic_distinction.py"
RUNNER = ROOT / "scripts/evals/run_r4_semantic_distinction_experiment.py"
HISTORICAL_REVIEW = ROOT / (
    "research/lolla-r4-complementary-reader-token-correction-execution-2026-07-14-a2/"
    "source-first-review.json"
)
DEFAULT_OUTPUT = ROOT / "research/lolla-r4-semantic-distinction-contract-2026-07-14"
CONTRACT = ROOT / "docs/evals/lolla-r4-semantic-distinction-contract-v1.json"

MODEL = "google/gemini-3.1-flash-lite"
PROVIDER = "google-vertex"
TASK_LIMITS = {
    "uncertainty": {"max_tokens": 1600, "reasoning_effort": "minimal"},
    "relationship": {"max_tokens": 700, "reasoning_effort": "minimal"},
}
SEEDS = {
    "v1-case01-flood-infrastructure": {"uncertainty": 8102, "relationship": 8103},
    "v1-case04-component-sourcing": {"uncertainty": 8402, "relationship": 8403},
}
# Relationship prompts are built only after local admission, so a 50 KB ceiling
# leaves ample room for exact-ID records while keeping the prospective call under
# the per-case budget even at the deliberately conservative two-bytes/token ratio.
MAX_RELATIONSHIP_PROMPT_UTF8_BYTES = 50_000
MAX_COST_PER_CASE_USD = 0.015
MAX_TOTAL_COST_USD = 0.03
PROMPT_PRICE_PER_MILLION = 0.25
COMPLETION_PRICE_PER_MILLION = 1.5


class R4SemanticDistinctionContractError(RuntimeError):
    """Raised when the provider-free contract or its evidence drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SemanticDistinctionContractError(f"expected JSON object: {path}")
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


def _fixture_source_registry(case: Mapping[str, Any]) -> dict[str, Any]:
    source_rows = case.get("source_evidence")
    if not isinstance(source_rows, list) or not source_rows:
        raise R4SemanticDistinctionContractError("fixture source evidence missing")
    source_bytes = (
        "\n".join(str(row["text"]) for row in source_rows) + "\n"
    ).encode("utf-8")
    aliases = [
        {
            "alias": row["alias"],
            "span_id": f"span-{case['case_id']}-{index:02d}",
            "speaker": row["speaker"],
            "turn_index": row["turn_index"],
            "text_sha256": _sha(str(row["text"]).encode("utf-8")),
        }
        for index, row in enumerate(source_rows, 1)
    ]
    return build_source_registry(
        case_id=str(case["case_id"]),
        source_path=f"development-fixtures/{case['case_id']}.txt",
        source_bytes=source_bytes,
        message_count=max(int(row["turn_index"]) for row in source_rows),
        aliases=aliases,
    )


def _fixture_readers(case_id: str) -> list[dict[str, str]]:
    return planned_readers_v1(
        case_id=case_id,
        existing_producer_id="human-authored-development-fixture",
        complementary_producer_id=MODEL,
    )


def _validate_development_fixtures(fixtures: Mapping[str, Any]) -> dict[str, Any]:
    if (
        fixtures.get("schema_version")
        != "lolla.r4_semantic_distinction_fixture_catalog.v1"
        or fixtures.get("partition") != "exposed_development_only"
        or fixtures.get("provider_output") is not False
        or fixtures.get("semantic_reliability_claim") is not False
    ):
        raise R4SemanticDistinctionContractError("development fixture boundary drifted")
    uncertainty_rows = fixtures.get("uncertainty_cases")
    relationship_rows = fixtures.get("relationship_cases")
    if not isinstance(uncertainty_rows, list) or len(uncertainty_rows) != 7:
        raise R4SemanticDistinctionContractError("uncertainty fixture count drifted")
    if not isinstance(relationship_rows, list) or len(relationship_rows) != 2:
        raise R4SemanticDistinctionContractError("relationship fixture count drifted")
    observations = []
    for case in uncertainty_rows:
        registry = _fixture_source_registry(case)
        response = case["expected_response"]
        raw = canonical_json_bytes(response)
        compiled = compile_uncertainty_response_v1(
            response=response,
            packet={
                "schema_version": UNCERTAINTY_PACKET_SCHEMA,
                "case_id": case["case_id"],
            },
            source_registry=registry,
            planned_readers=_fixture_readers(str(case["case_id"])),
            artifact_path=f"development-fixtures/{case['case_id']}-expected.json",
            artifact_bytes=raw,
        )
        prompt_packet = {
            "schema_version": UNCERTAINTY_PACKET_SCHEMA,
            "case_id": case["case_id"],
            "source": {
                "path": registry["source_path"],
                "aliases": copy.deepcopy(case["source_evidence"]),
            },
            "prior_interpretation_context": {
                "authority": "fallible_prior_interpretation_not_source_truth",
                "records": [],
            },
        }
        prompts = build_uncertainty_prompts_v2(prompt_packet)
        observations.append(
            {
                "case_id": case["case_id"],
                "task": "uncertainty",
                "category": case["category"],
                "compiled_status": compiled["status"],
                "compiled_record_count": len(compiled["record_ids"]),
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
            }
        )
    for case in relationship_rows:
        registry = _fixture_source_registry(case)
        response = case["expected_response"]
        raw = canonical_json_bytes(response)
        packet = {
            "schema_version": RELATIONSHIP_PACKET_SCHEMA,
            "case_id": case["case_id"],
            "record_catalog": copy.deepcopy(case["record_catalog"]),
        }
        compiled = compile_relationship_response_v1(
            response=response,
            packet=packet,
            source_registry=registry,
            planned_readers=_fixture_readers(str(case["case_id"])),
            artifact_path=f"development-fixtures/{case['case_id']}-expected.json",
            artifact_bytes=raw,
        )
        prompts = build_relationship_prompts_v2(packet)
        observations.append(
            {
                "case_id": case["case_id"],
                "task": "relationship",
                "category": case["category"],
                "compiled_status": compiled["status"],
                "compiled_record_count": len(compiled["record_ids"]),
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
            }
        )
    reasoning_shapes = [
        {},
        {"reasoning": ""},
        {
            "reasoning_details": [
                {
                    "type": "reasoning.text",
                    "format": "google-gemini-v1",
                    "index": 0,
                    "signature": "opaque-not-preserved",
                }
            ]
        },
        {"reasoning": "content-not-preserved"},
        {"reasoning_details": [{"type": "reasoning.future"}]},
    ]
    custody = [inspect_r4_reasoning_exclusion_v1(row) for row in reasoning_shapes]
    if [row["status"] for row in custody] != [
        "reasoning_absent",
        "reasoning_empty",
        "reasoning_metadata_only",
        "reasoning_content_present",
        "reasoning_shape_malformed",
    ]:
        raise R4SemanticDistinctionContractError("reasoning custody adapter drifted")
    return {
        "schema_version": "lolla.r4_semantic_distinction_fixture_validation.v1",
        "status": "development_contract_shapes_compile_provider_free",
        "provider_calls": 0,
        "semantic_reliability_claim": False,
        "observations": observations,
        "reasoning_custody_statuses": [row["status"] for row in custody],
        "provider_values_preserved": False,
    }


def _maximum_relationship_cost() -> dict[str, Any]:
    estimated_input_tokens = (MAX_RELATIONSHIP_PROMPT_UTF8_BYTES + 1) // 2
    output_tokens = TASK_LIMITS["relationship"]["max_tokens"]
    cost = estimated_input_tokens * PROMPT_PRICE_PER_MILLION / 1_000_000
    cost += output_tokens * COMPLETION_PRICE_PER_MILLION / 1_000_000
    return {
        "maximum_prompt_utf8_bytes_before_stop": MAX_RELATIONSHIP_PROMPT_UTF8_BYTES,
        "conservative_estimated_input_tokens": estimated_input_tokens,
        "maximum_output_tokens": output_tokens,
        "conservative_maximum_cost_usd": round(cost, 9),
        "future_runner_must_stop_before_transport_above_byte_limit": True,
    }


def build_files(output: Path = DEFAULT_OUTPUT) -> dict[str, bytes]:
    holdout = _load(HOLDOUT)
    fixtures = _load(FIXTURES)
    if (
        holdout.get("status")
        != "frozen_before_request_previews_contract_and_provider_calls"
        or holdout.get("review_method", {}).get("target_visible_to_provider")
        is not False
        or holdout.get("review_method", {}).get("scalar_quality_score") is not None
    ):
        raise R4SemanticDistinctionContractError("holdout boundary drifted")
    for case in holdout["cases"]:
        for field in ("source", "existing_role_artifact"):
            path = ROOT / case[field]["path"]
            if not path.is_file() or _file_sha(path) != case[field]["sha256"]:
                raise R4SemanticDistinctionContractError(
                    f"holdout {field} drifted: {case['case_id']}"
                )
    fixture_validation = _validate_development_fixtures(fixtures)
    generated: dict[str, bytes] = {}
    generated[_relative(output / "fixture-validation.json")] = _render(
        fixture_validation
    )
    uncertainty_schema = uncertainty_response_schema_v1()
    relationship_schema = relationship_response_schema_v1()
    generated[_relative(output / "uncertainty-response-schema.json")] = _render(
        uncertainty_schema
    )
    generated[_relative(output / "relationship-response-schema.json")] = _render(
        relationship_schema
    )
    previous_tasks = copy.deepcopy(base.TASKS)
    case_reports = []
    total_estimate = 0.0
    try:
        base.TASKS.clear()
        base.TASKS.update(copy.deepcopy(TASK_LIMITS))
        for target_case in holdout["cases"]:
            case_id = target_case["case_id"]
            paths = base._case_paths(case_id)
            wrapper = _load(paths["wrapper"])
            source_bytes = paths["source"].read_bytes()
            role_bytes = paths["role"].read_bytes()
            role = json.loads(role_bytes)
            source_registry = build_source_registry_v1(
                wrapper=wrapper, source_bytes=source_bytes
            )
            packet = build_uncertainty_packet_v1(
                wrapper=wrapper,
                source_bytes=source_bytes,
                role_portfolio=role,
                role_artifact_path=_relative(paths["role"]),
                role_artifact_bytes=role_bytes,
            )
            prompts = build_uncertainty_prompts_v2(packet)
            preview = base.build_request_preview(
                prompts=prompts,
                schema=uncertainty_schema,
                schema_name="lolla_r4_uncertainty_v1",
                task="uncertainty",
                seed=SEEDS[case_id]["uncertainty"],
            )
            preview["status"] = (
                "provider_free_semantic_distinction_request_preview_not_authorized"
            )
            metrics = base._estimated_cost(preview)
            relation_max = _maximum_relationship_cost()
            case_estimate = round(
                float(metrics["conservative_estimated_cost_usd"])
                + float(relation_max["conservative_maximum_cost_usd"]),
                9,
            )
            if case_estimate > MAX_COST_PER_CASE_USD:
                raise R4SemanticDistinctionContractError(
                    f"prospective case cost exceeds ceiling: {case_id}"
                )
            target_text = target_case["frozen_source_first_target"]
            prompt_text = prompts["system_prompt"] + prompts["user_prompt"]
            for value in target_text.values():
                if isinstance(value, str) and value in prompt_text:
                    raise R4SemanticDistinctionContractError(
                        f"holdout target leaked into prompt: {case_id}"
                    )
            case_root = output / "cases" / case_id
            for name, value in (
                ("source-registry.json", source_registry),
                ("uncertainty-packet.json", packet),
                ("uncertainty-prompts.json", prompts),
                ("uncertainty-request-preview.json", preview),
            ):
                generated[_relative(case_root / name)] = _render(value)
            case_reports.append(
                {
                    "case_id": case_id,
                    "selection_role": target_case["role"],
                    "wrapper_path": _relative(paths["wrapper"]),
                    "source_path": _relative(paths["source"]),
                    "source_sha256": _file_sha(paths["source"]),
                    "role_artifact_path": _relative(paths["role"]),
                    "role_artifact_sha256": _file_sha(paths["role"]),
                    "uncertainty_packet_path": _relative(
                        case_root / "uncertainty-packet.json"
                    ),
                    "uncertainty_prompts_path": _relative(
                        case_root / "uncertainty-prompts.json"
                    ),
                    "uncertainty_request_preview_path": _relative(
                        case_root / "uncertainty-request-preview.json"
                    ),
                    "uncertainty_request_body_sha256": preview["body_sha256"],
                    "seeds": copy.deepcopy(SEEDS[case_id]),
                    "uncertainty_request": metrics,
                    "relationship_request_conservative_maximum": relation_max,
                    "conservative_case_cost_usd": case_estimate,
                    "case_cost_ceiling_usd": MAX_COST_PER_CASE_USD,
                    "case_cost_preflight_pass": True,
                    "relationship_seed": SEEDS[case_id]["relationship"],
                    "relationship_request_is_dynamic": True,
                }
            )
            total_estimate += case_estimate
    finally:
        base.TASKS.clear()
        base.TASKS.update(previous_tasks)
    total_estimate = round(total_estimate, 9)
    if total_estimate > MAX_TOTAL_COST_USD:
        raise R4SemanticDistinctionContractError("total estimate exceeds ceiling")

    preflight = {
        "schema_version": "lolla.r4_semantic_distinction_preflight.v1",
        "status": "provider_free_contract_ready_new_call_authorization_required",
        "date": "2026-07-14",
        "run_id": "lolla-r4-semantic-distinction-holdout-a3",
        "prompt_contract_version": SEMANTIC_DISTINCTION_PROMPT_CONTRACT,
        "holdout_target": {"path": _relative(HOLDOUT), "sha256": _file_sha(HOLDOUT)},
        "development_fixture_validation_path": _relative(
            output / "fixture-validation.json"
        ),
        "current_practice": {"path": _relative(PRACTICE), "sha256": _file_sha(PRACTICE)},
        "cases": case_reports,
        "budget": {
            "maximum_provider_calls": 4,
            "maximum_calls_per_case": 2,
            "maximum_provider_reported_cost_per_case_usd": MAX_COST_PER_CASE_USD,
            "maximum_provider_reported_cost_total_usd": MAX_TOTAL_COST_USD,
            "conservative_estimated_total_cost_usd": total_estimate,
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
        "reasoning_custody": {
            "adapter": "engine.system_b.r4_semantic_distinction.inspect_r4_reasoning_exclusion_v1",
            "metadata_only_satisfies_exclusion": True,
            "content_or_malformed_shape_fails_closed": True,
            "provider_values_preserved": False,
            "historical_result_reclassified": False,
        },
        "decision": {
            "provider_calls_authorized": False,
            "runtime_or_graph_integration_authorized": False,
            "production_model_selected": False,
            "next_decision": "founder authorization or deferral of the frozen four-call maximum holdout diagnostic",
        },
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "scalar_quality_score": None,
    }
    generated[_relative(output / "preflight-result.json")] = _render(preflight)
    manifest_rows = [
        {"path": path, "sha256": _sha(raw), "utf8_bytes": len(raw)}
        for path, raw in sorted(generated.items())
    ]
    manifest_body = {
        "schema_version": "lolla.r4_semantic_distinction_preflight_manifest.v1",
        "status": "provider_free_preflight_exact_files_frozen",
        "date": "2026-07-14",
        "files": manifest_rows,
        "file_count": len(manifest_rows),
        "provider_calls": 0,
    }
    manifest = {**manifest_body, "manifest_sha256": value_sha256(manifest_body)}
    generated[_relative(output / "manifest.json")] = _render(manifest)

    operator = _load(
        ROOT / "docs/evals/lolla-r4-complementary-reader-token-correction-contract-v1.json"
    )["operator"]
    contract = {
        "schema_version": "lolla.r4_semantic_distinction_contract.v1",
        "status": "frozen_provider_free_new_call_authorization_required",
        "date": "2026-07-14",
        "run_id": preflight["run_id"],
        "purpose": "Test whether the additive v2 probabilistic prompt contract preserves one unseen material uncertainty while restraining one unseen already-operationalized control.",
        "holdout_target": preflight["holdout_target"],
        "current_practice": preflight["current_practice"],
        "development_fixtures": {
            "path": _relative(FIXTURES),
            "sha256": _file_sha(FIXTURES),
            "partition": "exposed_development_only",
            "provider_output": False,
        },
        "historical_source_first_review": {
            "path": _relative(HISTORICAL_REVIEW),
            "sha256": _file_sha(HISTORICAL_REVIEW),
            "historical_result_reclassified": False,
        },
        "prompt_contract": {
            "version": SEMANTIC_DISTINCTION_PROMPT_CONTRACT,
            "module_path": _relative(MODULE),
            "module_sha256": _file_sha(MODULE),
            "v1_historical_prompt_and_runner_changed": False,
        },
        "preflight": {
            "path": _relative(output / "preflight-result.json"),
            "sha256": _sha(generated[_relative(output / "preflight-result.json")]),
            "manifest_path": _relative(output / "manifest.json"),
            "manifest_sha256": _sha(generated[_relative(output / "manifest.json")]),
        },
        "operator": operator,
        "task_limits": TASK_LIMITS,
        "schemas": {
            "uncertainty_sha256": value_sha256(uncertainty_schema),
            "relationship_sha256": value_sha256(relationship_schema),
            "wire_mode": "strict_json_schema",
            "strict": True,
            "schemas_unchanged_from_corrected_r4": True,
            "local_admission_required": True,
        },
        "cases": case_reports,
        "budget": preflight["budget"],
        "execution_contract": {
            "runner_path": _relative(RUNNER),
            "runner_sha256": _file_sha(RUNNER),
            "one_attempt_per_task": True,
            "relationship_request_built_only_from_newly_admitted_exact_id_records": True,
            "maximum_relationship_prompt_utf8_bytes": MAX_RELATIONSHIP_PROMPT_UTF8_BYTES,
            "stop_relationship_on_uncertainty_failure": True,
            "stop_when_reasoning_exclusion_not_satisfied": True,
            "strict_reasoning_shape_adapter_required": True,
            "durable_started_marker_before_every_network_transport": True,
            "stop_further_calls_when_provider_cost_is_unknown": True,
            "stop_at_case_or_total_cost_boundary": True,
            "preserve_length_schema_custody_and_budget_failures": True,
            "holdout_target_never_loaded_by_runner": True,
            "automatic_retry_or_response_healing": False,
        },
        "review_contract": {
            "source_first_human_review_required": True,
            "dimensions": holdout["review_method"]["dimensions_reviewed_separately"],
            "scalar_quality_score": None,
        },
        "decision_boundary": {
            "provider_calls_authorized": False,
            "authorization_file_present": False,
            "runtime_or_graph_integration_authorized": False,
            "production_model_selection_authorized": False,
            "model_comparison_authorized": False,
            "wider_corpus_authorized": False,
            "next_decision": preflight["decision"]["next_decision"],
        },
        "frozen_inputs": [
            {"path": _relative(path), "sha256": _file_sha(path)}
            for path in (
                HOLDOUT,
                FIXTURES,
                PRACTICE,
                MODULE,
                RUNNER,
                HISTORICAL_REVIEW,
            )
        ],
        "non_claims": [
            "This contract does not authorize a provider call by itself.",
            "Development fixture success does not prove provider compliance.",
            "The holdout remains simulated reliability evidence, not real-user usefulness evidence.",
            "No deterministic code decides conversational meaning, materiality, relationship meaning, pressure, or quality.",
            "A future two-case result cannot select a production model or authorize runtime integration.",
        ],
    }
    generated[_relative(CONTRACT)] = _render(contract)
    return generated


def _validate_files(files: Mapping[str, bytes]) -> dict[str, Any]:
    for relative, expected in files.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != expected:
            raise R4SemanticDistinctionContractError(
                f"semantic-distinction artifact drifted: {relative}"
            )
    contract = _load(CONTRACT)
    if (
        contract.get("status")
        != "frozen_provider_free_new_call_authorization_required"
        or contract.get("decision_boundary", {}).get("provider_calls_authorized")
        is not False
        or contract.get("review_contract", {}).get("scalar_quality_score") is not None
        or contract.get("budget", {}).get("maximum_provider_calls") != 4
    ):
        raise R4SemanticDistinctionContractError("contract decision boundary drifted")
    return contract


def build(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    files = build_files(output)
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return _validate_files(files)


def validate(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    return _validate_files(build_files(output))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    result = validate(args.output.resolve()) if args.validate_only else build(args.output.resolve())
    print(
        json.dumps(
            {
                "status": result["status"],
                "run_id": result["run_id"],
                "provider_calls_authorized": result["decision_boundary"][
                    "provider_calls_authorized"
                ],
                "conservative_estimated_total_cost_usd": result["budget"][
                    "conservative_estimated_total_cost_usd"
                ],
                "next_decision": result["decision_boundary"]["next_decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
