#!/usr/bin/env python3
"""Build the provider-free R4 residual-task contract and full-context previews."""

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
    UNCERTAINTY_PACKET_SCHEMA,
    canonical_json_bytes,
    planned_readers_v1,
    uncertainty_response_schema_v1,
    value_sha256,
)
from engine.system_b.r4_residual_task import (
    RESIDUAL_PROVIDER_SURFACES,
    RESIDUAL_SURFACE_TO_CANONICAL_ROLE,
    RESIDUAL_TASK_PROMPT_CONTRACT,
    build_residual_prompts_v1,
    compile_residual_response_v1,
    residual_response_schema_v1,
)
from engine.system_b.r4_semantic_distinction import build_uncertainty_prompts_v2


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "research/lolla-r4-residual-task-contract-2026-07-14"
FROZEN_CONTRACT_ROOT = ROOT / (
    "research/lolla-r4-semantic-distinction-contract-2026-07-14"
)
RESIDUAL_FIXTURES = ROOT / (
    "tests/fixtures/r4_residual_task/contract-fixtures-v1.json"
)
HISTORICAL_FIXTURES = ROOT / (
    "tests/fixtures/r4_semantic_distinction/contract-fixtures-v1.json"
)
MODULE = ROOT / "engine/system_b/r4_residual_task.py"
CASE_IDS = (
    "v1-case01-flood-infrastructure",
    "v1-case04-component-sourcing",
)
FROZEN_HISTORY_PATHS = (
    "engine/system_b/r4_complementary_readers.py",
    "scripts/evals/run_r4_complementary_reader_experiment.py",
    "engine/system_b/r4_semantic_distinction.py",
    "scripts/evals/run_r4_semantic_distinction_experiment.py",
    "tests/fixtures/r4_semantic_distinction/contract-fixtures-v1.json",
    "docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json",
    "docs/evals/lolla-r4-complementary-reader-experiment-authorization-a1.json",
    "docs/evals/lolla-r4-complementary-reader-token-correction-authorization-a2.json",
    "docs/evals/lolla-r4-semantic-distinction-holdout-target-v1.json",
    "docs/evals/lolla-r4-semantic-distinction-contract-v1.json",
    "docs/evals/lolla-r4-semantic-distinction-holdout-authorization-a3.json",
    "research/lolla-r4-semantic-distinction-contract-2026-07-14/manifest.json",
    "research/lolla-r4-semantic-distinction-holdout-execution-2026-07-14-a3/result.json",
    "research/lolla-r4-semantic-distinction-holdout-execution-2026-07-14-a3/evidence-manifest.json",
    "research/lolla-r4-semantic-distinction-holdout-execution-2026-07-14-a3/source-first-review.json",
    "research/lolla-r4-semantic-distinction-holdout-execution-2026-07-14-a3/execution-closeout.json",
)
RELATIONSHIP_PROMPT_PATHS = tuple(
    "research/lolla-r4-semantic-distinction-holdout-execution-2026-07-14-a3/"
    f"{case_id}/relationship-prompts.json"
    for case_id in CASE_IDS
)


class R4ResidualTaskContractError(RuntimeError):
    """Raised when the provider-free residual contract or custody drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4ResidualTaskContractError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes())


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _estimated_tokens(utf8_bytes: int) -> int:
    return (utf8_bytes + 1) // 2


def _metrics(name: str, text: str) -> dict[str, Any]:
    raw = text.encode("utf-8")
    return {
        "name": name,
        "sha256": _sha(raw),
        "utf8_bytes": len(raw),
        "estimated_tokens": _estimated_tokens(len(raw)),
    }


def _value_metrics(value: Any) -> dict[str, Any]:
    raw = canonical_json_bytes(value)
    return {
        "sha256": _sha(raw),
        "utf8_bytes": len(raw),
        "estimated_tokens": _estimated_tokens(len(raw)),
    }


def _prompt_delta(packet: Mapping[str, Any]) -> dict[str, Any]:
    baseline = build_uncertainty_prompts_v2(packet)
    residual = build_residual_prompts_v1(packet)

    def delta(baseline_text: str, residual_text: str) -> dict[str, int]:
        baseline_bytes = len(baseline_text.encode("utf-8"))
        residual_bytes = len(residual_text.encode("utf-8"))
        return {
            "v2_utf8_bytes": baseline_bytes,
            "residual_utf8_bytes": residual_bytes,
            "utf8_byte_delta": residual_bytes - baseline_bytes,
            "v2_estimated_tokens": _estimated_tokens(baseline_bytes),
            "residual_estimated_tokens": _estimated_tokens(residual_bytes),
            "estimated_token_delta": (
                _estimated_tokens(residual_bytes)
                - _estimated_tokens(baseline_bytes)
            ),
        }

    system = delta(baseline["system_prompt"], residual["system_prompt"])
    user = delta(baseline["user_prompt"], residual["user_prompt"])
    total = delta(
        baseline["system_prompt"] + baseline["user_prompt"],
        residual["system_prompt"] + residual["user_prompt"],
    )
    baseline_schema_bytes = len(canonical_json_bytes(uncertainty_response_schema_v1()))
    residual_schema_bytes = len(canonical_json_bytes(residual_response_schema_v1()))
    schema = {
        "v2_utf8_bytes": baseline_schema_bytes,
        "residual_utf8_bytes": residual_schema_bytes,
        "utf8_byte_delta": residual_schema_bytes - baseline_schema_bytes,
        "v2_estimated_tokens": _estimated_tokens(baseline_schema_bytes),
        "residual_estimated_tokens": _estimated_tokens(residual_schema_bytes),
        "estimated_token_delta": (
            _estimated_tokens(residual_schema_bytes)
            - _estimated_tokens(baseline_schema_bytes)
        ),
    }
    increases = []
    if schema["utf8_byte_delta"] > 0:
        increases.append(
            {
                "component": "response_schema",
                "reason": (
                    "Longer residual surface identifiers and the exact dual-basis evidence "
                    "description add schema bytes while leaving its structure and bounds unchanged."
                ),
                "utf8_byte_increase": schema["utf8_byte_delta"],
            }
        )
    return {
        "baseline": "lolla.r4_semantic_distinction_prompt.v1",
        "prospective": RESIDUAL_TASK_PROMPT_CONTRACT,
        "estimator": (
            "ceil(utf8_bytes/2); deterministic conservative estimate, not provider tokenization"
        ),
        "system_prompt": system,
        "user_prompt": user,
        "total_prompt": total,
        "response_schema": schema,
        "material_increase_explanations": increases,
        "arbitrary_compression_threshold": None,
    }


def _fixture_registry(case: Mapping[str, Any]) -> dict[str, Any]:
    source_rows = case["source_evidence"]
    source_bytes = (
        "\n".join(str(row["text"]) for row in source_rows) + "\n"
    ).encode("utf-8")
    return build_source_registry(
        case_id=str(case["case_id"]),
        source_path=f"development-fixtures/{case['case_id']}.txt",
        source_bytes=source_bytes,
        message_count=max(int(row["turn_index"]) for row in source_rows),
        aliases=[
            {
                "alias": row["alias"],
                "span_id": f"span-{case['case_id']}-{index:02d}",
                "speaker": row["speaker"],
                "turn_index": row["turn_index"],
                "text_sha256": _sha(str(row["text"]).encode("utf-8")),
            }
            for index, row in enumerate(source_rows, 1)
        ],
    )


def _readers(case_id: str) -> list[dict[str, str]]:
    return planned_readers_v1(
        case_id=case_id,
        existing_producer_id="frozen-existing-reader",
        complementary_producer_id="prospective-provider",
    )


def _validate_fixtures() -> dict[str, Any]:
    residual = _load(RESIDUAL_FIXTURES)
    historical = _load(HISTORICAL_FIXTURES)
    reuse = residual.get("historical_fixture_reuse", {})
    if (
        residual.get("schema_version")
        != "lolla.r4_residual_task_fixture_catalog.v1"
        or residual.get("provider_output") is not False
        or residual.get("provider_calls") != 0
        or reuse.get("sha256") != _file_sha(HISTORICAL_FIXTURES)
    ):
        raise R4ResidualTaskContractError("residual fixture boundary drifted")
    historical_uncertainty = {
        row["case_id"]: row for row in historical["uncertainty_cases"]
    }
    projection = reuse["canonical_to_provider_surface_projection"]
    observations = []
    for reference in reuse["uncertainty_cases"]:
        case = historical_uncertainty[reference["case_id"]]
        response = copy.deepcopy(case["expected_response"])
        for review in response["reviews"]:
            review["surface"] = projection[review["surface"]]
        compiled = compile_residual_response_v1(
            response=response,
            packet={
                "schema_version": UNCERTAINTY_PACKET_SCHEMA,
                "case_id": case["case_id"],
            },
            source_registry=_fixture_registry(case),
            planned_readers=_readers(str(case["case_id"])),
            artifact_path=f"development-fixtures/{case['case_id']}-residual.json",
            artifact_bytes=canonical_json_bytes(response),
        )
        observations.append(
            {
                "case_id": case["case_id"],
                "category": case["category"],
                "compiled_state_by_canonical_role": {
                    row["surface"]: row["state"]
                    for row in compiled["reader_results"]
                },
            }
        )
    return {
        "schema_version": "lolla.r4_residual_task_fixture_validation.v1",
        "status": "all_additive_development_fixtures_compile_provider_free",
        "historical_uncertainty_fixture_count": len(observations),
        "historical_relationship_fixture_count": len(reuse["relationship_cases"]),
        "exposed_full_case_expectation_count": len(
            residual["exposed_case_expectations"]
        ),
        "observations": observations,
        "relationship_contract_changed": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "model_semantic_validation": False,
    }


def _build_preview(
    *,
    packet: Mapping[str, Any],
    frozen_preview: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    prompts = build_residual_prompts_v1(packet)
    body = copy.deepcopy(frozen_preview["body"])
    body["messages"] = [
        {"role": "system", "content": prompts["system_prompt"]},
        {"role": "user", "content": prompts["user_prompt"]},
    ]
    body["response_format"]["json_schema"]["name"] = "lolla_r4_residual_task_v1"
    body["response_format"]["json_schema"]["schema"] = copy.deepcopy(schema)
    preview = {
        "schema_version": "lolla.r4_residual_task_request_preview.v1",
        "status": "provider_free_full_context_preview_not_authorized_for_transport",
        "task": "paired_residual_discovery",
        "body": body,
        "body_sha256": value_sha256(body),
        "changed_body_paths": [
            "/messages/0/content",
            "/messages/1/content/task_and_surface_vocabulary_only",
            "/response_format/json_schema/name",
            "/response_format/json_schema/schema/descriptions_and_surface_enum_only",
        ],
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "transport_available": False,
        "authorization_present": False,
    }
    return preview, prompts


def _context_manifest(
    *,
    case_id: str,
    packet: Mapping[str, Any],
    prompts: Mapping[str, str],
    preview: Mapping[str, Any],
    frozen_preview: Mapping[str, Any],
    schema: Mapping[str, Any],
) -> dict[str, Any]:
    source = canonical_json_bytes(packet["source"]).decode("utf-8")
    prior = canonical_json_bytes(packet["prior_interpretation_context"]).decode(
        "utf-8"
    )
    user = prompts["user_prompt"]
    task_start = user.index("<task>\n") + len("<task>\n")
    task_end = user.index("\n</task>", task_start)
    task = user[task_start:task_end]
    delimiter_bytes = len(user.encode("utf-8")) - sum(
        len(value.encode("utf-8")) for value in (source, prior, task)
    )
    if (
        user.count(source) != 1
        or user.count(prior) != 1
        or not user.index(source) < user.index(prior) < task_start
        or not user.rstrip().endswith("</task>")
    ):
        raise R4ResidualTaskContractError(f"context ordering drifted: {case_id}")
    frozen_body = frozen_preview["body"]
    body = preview["body"]
    unchanged_controls = {
        key: body[key] == frozen_body[key]
        for key in (
            "model",
            "provider",
            "seed",
            "max_tokens",
            "reasoning",
            "stream",
        )
    }
    if not all(unchanged_controls.values()):
        raise R4ResidualTaskContractError(f"request control drifted: {case_id}")
    schema_bytes = len(canonical_json_bytes(schema))
    message_bytes = sum(
        len(row["content"].encode("utf-8")) for row in body["messages"]
    )
    prompt_components = [
        _metrics("system_instruction", prompts["system_prompt"]),
        _metrics("authoritative_source", source),
        _metrics("fallible_prior_interpretation_context", prior),
        _metrics("task", task),
        {
            "name": "user_section_delimiters",
            "sha256": None,
            "utf8_bytes": delimiter_bytes,
            "estimated_tokens": _estimated_tokens(delimiter_bytes),
        },
    ]
    return {
        "schema_version": "lolla.r4_residual_task_context_manifest.v1",
        "case_id": case_id,
        "section_order": [
            "system_instruction",
            "authoritative_source",
            "fallible_prior_interpretation_context",
            "task",
        ],
        "prompt_components": prompt_components,
        "source": {
            "artifact_path": packet["source"]["path"],
            "artifact_sha256": packet["source"]["sha256"],
            "canonical_context_sha256": _sha(source.encode("utf-8")),
            "canonical_context_utf8_bytes": len(source.encode("utf-8")),
            "estimated_tokens": _estimated_tokens(len(source.encode("utf-8"))),
            "message_count": packet["source"]["message_count"],
            "alias_count": len(packet["source"]["aliases"]),
            "included_exactly_once": True,
            "summarized_or_chunked": False,
        },
        "prior": {
            "artifact_path": packet["prior_interpretation_context"][
                "artifact_path"
            ],
            "artifact_sha256": packet["prior_interpretation_context"][
                "artifact_sha256"
            ],
            "canonical_context_sha256": _sha(prior.encode("utf-8")),
            "canonical_context_utf8_bytes": len(prior.encode("utf-8")),
            "estimated_tokens": _estimated_tokens(len(prior.encode("utf-8"))),
            "record_count": len(packet["prior_interpretation_context"]["records"]),
            "included_exactly_once": True,
            "summarized_or_reordered": False,
        },
        "complete_source_inclusion": True,
        "source_and_prior_unchanged_from_consumed_a3": True,
        "source_then_prior_order_unchanged": True,
        "task_at_end_invariant": True,
        "fallible_prior_declaration": (
            "Prior interpretations are fallible context, not source truth"
            in prompts["system_prompt"]
        ),
        "schema": {
            **_value_metrics(schema),
            "strict": body["response_format"]["json_schema"]["strict"],
            "name": body["response_format"]["json_schema"]["name"],
        },
        "request_estimate": {
            "message_utf8_bytes": message_bytes,
            "schema_utf8_bytes": schema_bytes,
            "estimated_input_tokens": _estimated_tokens(
                message_bytes + schema_bytes
            ),
            "estimator": (
                "ceil((message_utf8_bytes+schema_utf8_bytes)/2); "
                "not provider tokenization"
            ),
            "maximum_output_tokens": body["max_tokens"],
            "canonical_body_utf8_bytes": len(canonical_json_bytes(body)),
            "canonical_body_sha256": value_sha256(body),
        },
        "request_body_canonical_key_order": sorted(body),
        "request_body_top_level_components": {
            key: _value_metrics(body[key]) for key in sorted(body)
        },
        "changed_provider_visible_semantic_fields": [
            "system role",
            "residual operation",
            "surface vocabulary",
            "minimal examples",
            "output rules",
            "task surface names",
            "schema name",
            "schema surface enum",
            "schema descriptions",
        ],
        "unchanged_dimensions": {
            "complete_source_context": True,
            "prior_context": True,
            "source_prior_order": True,
            "paired_task_shape": True,
            "response_record_fields_and_bounds": True,
            "evidence_alias_shape": True,
            "relationship_reader_and_prompt": True,
            "model": unchanged_controls["model"],
            "provider_route": unchanged_controls["provider"],
            "seed": unchanged_controls["seed"],
            "maximum_output_tokens": unchanged_controls["max_tokens"],
            "reasoning_envelope": unchanged_controls["reasoning"],
            "streaming": unchanged_controls["stream"],
            "runtime": True,
        },
        "declared_omissions": [
            "no provider transport or network-capable runner",
            "no provider result or model semantic validation",
            "no new holdout, authorization, target, or evaluator",
            "no relationship request, prompt, compiler, or repair",
            "no governed-pending output surface",
            "no runtime, graph, embedding, retry, fallback, or healing",
            "no deterministic residual classification",
        ],
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def _frozen_records(paths: Sequence[str]) -> list[dict[str, Any]]:
    records = []
    for relative in paths:
        path = ROOT / relative
        if not path.is_file():
            raise R4ResidualTaskContractError(f"frozen file missing: {relative}")
        records.append(
            {
                "path": relative,
                "sha256": _file_sha(path),
                "utf8_bytes": len(path.read_bytes()),
            }
        )
    return records


def build_files(output: Path = DEFAULT_OUTPUT) -> dict[str, bytes]:
    schema = residual_response_schema_v1()
    fixture_validation = _validate_fixtures()
    residual_fixtures = _load(RESIDUAL_FIXTURES)
    expectations = {
        row["case_id"]: row
        for row in residual_fixtures["exposed_case_expectations"]
    }
    if set(expectations) != set(CASE_IDS):
        raise R4ResidualTaskContractError("exposed case expectations drifted")

    generated: dict[str, bytes] = {
        _relative(output / "residual-response-schema.json"): _render(schema),
        _relative(output / "fixture-validation.json"): _render(fixture_validation),
    }
    case_records = []
    first_packet: dict[str, Any] | None = None
    for case_id in CASE_IDS:
        frozen_case_root = FROZEN_CONTRACT_ROOT / "cases" / case_id
        packet_path = frozen_case_root / "uncertainty-packet.json"
        frozen_preview_path = frozen_case_root / "uncertainty-request-preview.json"
        registry_path = frozen_case_root / "source-registry.json"
        packet = _load(packet_path)
        frozen_preview = _load(frozen_preview_path)
        registry = _load(registry_path)
        if first_packet is None:
            first_packet = packet
        preview, prompts = _build_preview(
            packet=packet,
            frozen_preview=frozen_preview,
            schema=schema,
        )
        context = _context_manifest(
            case_id=case_id,
            packet=packet,
            prompts=prompts,
            preview=preview,
            frozen_preview=frozen_preview,
            schema=schema,
        )
        case_root = output / "cases" / case_id
        response = expectations[case_id]["expected_response"]
        response_path = case_root / "local-expected-response.json"
        response_bytes = _render(response)
        compiled = compile_residual_response_v1(
            response=response,
            packet=packet,
            source_registry=registry,
            planned_readers=_readers(case_id),
            artifact_path=_relative(response_path),
            artifact_bytes=response_bytes,
        )
        values = (
            ("residual-prompts.json", prompts),
            ("residual-request-preview.json", preview),
            ("context-manifest.json", context),
            ("local-expected-response.json", response),
            ("local-expected-compiled.json", compiled),
        )
        for name, value in values:
            generated[_relative(case_root / name)] = _render(value)
        case_records.append(
            {
                "case_id": case_id,
                "expectation_role": expectations[case_id]["expectation_role"],
                "frozen_a3_packet": {
                    "path": _relative(packet_path),
                    "sha256": _file_sha(packet_path),
                },
                "frozen_a3_request_preview": {
                    "path": _relative(frozen_preview_path),
                    "sha256": _file_sha(frozen_preview_path),
                },
                "residual_request_preview_path": _relative(
                    case_root / "residual-request-preview.json"
                ),
                "context_manifest_path": _relative(
                    case_root / "context-manifest.json"
                ),
                "local_expected_response_path": _relative(response_path),
                "local_expected_compiled_path": _relative(
                    case_root / "local-expected-compiled.json"
                ),
                "provider_calls": 0,
            }
        )
    if first_packet is None:
        raise R4ResidualTaskContractError("no exposed packets available")

    frozen_history = _frozen_records(FROZEN_HISTORY_PATHS)
    relationship_prompts = _frozen_records(RELATIONSHIP_PROMPT_PATHS)
    contract = {
        "schema_version": "lolla.r4_residual_task_contract.v1",
        "status": "provider_free_residual_contract_complete",
        "date": "2026-07-14",
        "product_question": (
            "Can one provider-ready paired contract make the complete provider-visible "
            "job residual discovery while every non-semantic R4 dimension stays fixed?"
        ),
        "prompt_contract_version": RESIDUAL_TASK_PROMPT_CONTRACT,
        "module": {
            "path": _relative(MODULE),
            "sha256": _file_sha(MODULE),
        },
        "provider_surfaces": list(RESIDUAL_PROVIDER_SURFACES),
        "deterministic_surface_to_canonical_role_mapping": copy.deepcopy(
            RESIDUAL_SURFACE_TO_CANONICAL_ROLE
        ),
        "mapping_inspects_free_text": False,
        "response_structure_and_bounds_unchanged": True,
        "prompt_delta_against_v2": _prompt_delta(first_packet),
        "fixture_catalog": {
            "path": _relative(RESIDUAL_FIXTURES),
            "sha256": _file_sha(RESIDUAL_FIXTURES),
            "historical_fixture_catalog_changed": False,
            "complete_development_catalog_kept_outside_provider_prompt": True,
        },
        "cases": case_records,
        "frozen_history": frozen_history,
        "relationship_boundary": {
            "changed": False,
            "compiler_module": next(
                row
                for row in frozen_history
                if row["path"] == "engine/system_b/r4_complementary_readers.py"
            ),
            "prompt_module": next(
                row
                for row in frozen_history
                if row["path"] == "engine/system_b/r4_semantic_distinction.py"
            ),
            "frozen_prompt_files": relationship_prompts,
            "relationship_repair_part_of_goal": False,
        },
        "unchanged_dimensions": [
            "complete source and prior context and ordering",
            "paired task shape",
            "response fields, counts, zero, ambiguity, and evidence aliases",
            "canonical downstream roles",
            "relationship reader, prompt, and compiler",
            "model, provider route, seed, reasoning, and output allowance",
            "runtime and graph",
        ],
        "declared_omissions": [
            "provider transport and network-capable runner",
            "new holdout, target, authorization, and evaluator",
            "relationship generation or repair",
            "governed-pending output surface",
            "runtime, graph, embedding, retry, fallback, and healing",
            "deterministic semantic classification",
        ],
        "stop_rule_triggered": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "provider_call_authorized": False,
        "holdout_prepared": False,
        "model_semantic_validation": False,
        "product_usefulness_claim": False,
        "runtime_or_graph_integration": False,
        "completion_decision": "residual_contract_ready_for_new_holdout_design",
        "non_claim": (
            "Provider-free contract validity is not model semantic validation."
        ),
    }
    generated[_relative(output / "contract.json")] = _render(contract)
    manifest_rows = [
        {"path": path, "sha256": _sha(raw), "utf8_bytes": len(raw)}
        for path, raw in sorted(generated.items())
    ]
    manifest_body = {
        "schema_version": "lolla.r4_residual_task_manifest.v1",
        "status": "provider_free_exact_artifacts_complete",
        "date": "2026-07-14",
        "files": manifest_rows,
        "file_count": len(manifest_rows),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    manifest = {**manifest_body, "manifest_sha256": value_sha256(manifest_body)}
    generated[_relative(output / "manifest.json")] = _render(manifest)
    return generated


def _validate_files(
    files: Mapping[str, bytes], output: Path
) -> dict[str, Any]:
    for relative, expected in files.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != expected:
            raise R4ResidualTaskContractError(
                f"residual-task artifact drifted: {relative}"
            )
    contract = _load(output / "contract.json")
    if (
        contract.get("status") != "provider_free_residual_contract_complete"
        or contract.get("provider_calls") != 0
        or contract.get("provider_cost_usd") != 0.0
        or contract.get("provider_call_authorized") is not False
        or contract.get("holdout_prepared") is not False
    ):
        raise R4ResidualTaskContractError("residual decision boundary drifted")
    return contract


def build(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    files = build_files(output)
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return _validate_files(files, output)


def validate(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    return _validate_files(build_files(output), output)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    result = validate(output) if args.validate_only else build(output)
    print(
        json.dumps(
            {
                "status": result["status"],
                "provider_calls": result["provider_calls"],
                "provider_cost_usd": result["provider_cost_usd"],
                "holdout_prepared": result["holdout_prepared"],
                "completion_decision": result["completion_decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
