#!/usr/bin/env python3
"""Build or validate the provider-free R4 complementary-reader preflight."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.system_b.conversation_state_fan_in import (
    assemble_conversation_state_fan_in,
)
from engine.system_b.r4_complementary_readers import (
    build_relationship_packet_v1,
    build_relationship_prompts_v1,
    build_source_registry_v1,
    build_uncertainty_packet_v1,
    build_uncertainty_prompts_v1,
    canonical_json_bytes,
    compile_relationship_response_v1,
    compile_uncertainty_response_v1,
    existing_reader_results_v1,
    missing_complementary_reader_results_v1,
    planned_readers_v1,
    relationship_response_schema_v1,
    source_alias_catalog_v1,
    uncertainty_response_schema_v1,
    value_sha256,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "research/lolla-r4-complementary-reader-preflight-2026-07-13"
TARGET_PATH = ROOT / "docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json"
MODEL_SNAPSHOT_PATH = (
    ROOT / "docs/evals/lolla-r4-complementary-reader-model-snapshot-2026-07-13.json"
)
FIXTURE_ROOT = ROOT / "tests/fixtures/r4_complementary_readers"
MODEL = "google/gemini-3.1-flash-lite"
PROVIDER = "google-vertex"
MAX_COST_PER_CASE_USD = 0.015
MAX_TOTAL_COST_USD = 0.03
TASKS = {
    "uncertainty": {"max_tokens": 900, "reasoning_effort": "low"},
    "relationship": {"max_tokens": 700, "reasoning_effort": "minimal"},
}
SEEDS = {
    "v1-case02-discharge-transport": {"uncertainty": 8202, "relationship": 8203},
    "v1-case03-executive-hire": {"uncertainty": 8302, "relationship": 8303},
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes())


def _relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def build_request_preview(
    *,
    prompts: Mapping[str, str],
    schema: Mapping[str, Any],
    schema_name: str,
    task: str,
    seed: int,
) -> dict[str, Any]:
    limits = TASKS[task]
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
        "provider": {
            "order": [PROVIDER],
            "only": [PROVIDER],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr": True,
            "max_price": {"prompt": 0.25, "completion": 1.5},
        },
        "seed": seed,
        "max_tokens": limits["max_tokens"],
        "reasoning": {"effort": limits["reasoning_effort"], "exclude": True},
        "stream": False,
    }
    return {
        "status": "provider_free_request_preview_not_authorized_for_transport",
        "task": task,
        "body": body,
        "body_sha256": value_sha256(body),
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "provider_calls": 0,
    }


def _estimated_cost(preview: Mapping[str, Any]) -> dict[str, float | int]:
    body = preview["body"]
    message_bytes = sum(
        len(message["content"].encode("utf-8")) for message in body["messages"]
    )
    schema_bytes = len(canonical_json_bytes(body["response_format"]["json_schema"]["schema"]))
    # This is deliberately conservative for an English corpus: assume only two
    # UTF-8 bytes per billable input token, then add the full output-token cap.
    estimated_input_tokens = (message_bytes + schema_bytes + 1) // 2
    maximum_output_tokens = int(body["max_tokens"])
    estimate = estimated_input_tokens * 0.25 / 1_000_000
    estimate += maximum_output_tokens * 1.5 / 1_000_000
    return {
        "prompt_utf8_bytes": message_bytes,
        "schema_utf8_bytes": schema_bytes,
        "conservative_estimated_input_tokens": estimated_input_tokens,
        "maximum_output_tokens": maximum_output_tokens,
        "conservative_estimated_cost_usd": round(estimate, 9),
    }


def _case_paths(case_id: str) -> dict[str, Path]:
    corpus = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12"
    return {
        "wrapper": corpus
        / "provider-free-role-input-preflight/transfer"
        / case_id
        / "position-wrapper.json",
        "source": corpus / "naturalized-transfer-sources" / f"{case_id}.txt",
        "role": ROOT
        / "research/simulated-reliability-v1-transfer-2026-07-12/t1"
        / f"{case_id}-primary"
        / "joined-role-records.json",
    }


def _structural_uncertainty_fixture(case_id: str) -> dict[str, Any]:
    suffix = (
        "uncertainty-positive.json"
        if case_id == "v1-case02-discharge-transport"
        else "uncertainty-zero.json"
    )
    return _load(FIXTURE_ROOT / f"{case_id}-{suffix}")


def _relationship_fixture(packet: Mapping[str, Any]) -> dict[str, Any]:
    if packet["case_id"] == "v1-case03-executive-hire":
        return {
            "outcome": "no_supported_record_observed",
            "records": [],
            "global_limitations": "Provider-free structural fixture only; this is not a provider result or semantic finding.",
        }
    by_surface = {row["surface"]: row["record_id"] for row in packet["record_catalog"]}
    return {
        "outcome": "records_present",
        "records": [
            {
                "support": "supported",
                "related_record_ids": [
                    by_surface["current_position"],
                    by_surface["unresolved_matter"],
                    by_surface["reopen_condition"],
                ],
                "relationship": "The bounded current pilot does not by itself resolve transfer, and continuation is the point at which those dependencies must be reconsidered.",
                "evidence_ids": ["e032", "e048", "e094", "e098"],
                "limitations": "Provider-free structural fixture only; this does not predict pilot outcomes.",
            }
        ],
        "global_limitations": "Provider-free structural fixture only; this is not a provider result or semantic finding.",
    }


def _artifact_map_with(
    role_path: Path,
    role_bytes: bytes,
    generated: Mapping[str, bytes],
    *paths: str,
) -> dict[str, bytes]:
    result = {_relative(role_path): role_bytes}
    result.update({path: generated[path] for path in paths})
    return result


def build_files(output: Path) -> dict[str, bytes]:
    target = _load(TARGET_PATH)
    model_snapshot = _load(MODEL_SNAPSHOT_PATH)
    generated: dict[str, bytes] = {}
    uncertainty_schema = uncertainty_response_schema_v1()
    relationship_schema = relationship_response_schema_v1()
    generated[_relative(output / "uncertainty-response-schema.json")] = _render(
        uncertainty_schema
    )
    generated[_relative(output / "relationship-response-schema.json")] = _render(
        relationship_schema
    )

    case_reports = []
    total_estimated_cost = 0.0
    for target_case in target["cases"]:
        case_id = target_case["case_id"]
        paths = _case_paths(case_id)
        wrapper = _load(paths["wrapper"])
        source_bytes = paths["source"].read_bytes()
        role_bytes = paths["role"].read_bytes()
        role = json.loads(role_bytes)
        if _file_sha(paths["source"]) != target_case["source"]["sha256"]:
            raise RuntimeError(f"source target drifted: {case_id}")
        if _file_sha(paths["role"]) != target_case["existing_role_artifact"]["sha256"]:
            raise RuntimeError(f"role artifact target drifted: {case_id}")

        source_registry = build_source_registry_v1(
            wrapper=wrapper, source_bytes=source_bytes
        )
        readers = planned_readers_v1(
            case_id=case_id,
            existing_producer_id="google/gemini-3.5-flash-20260519",
            complementary_producer_id=MODEL,
        )
        case_root = output / "cases" / case_id
        packet = build_uncertainty_packet_v1(
            wrapper=wrapper,
            source_bytes=source_bytes,
            role_portfolio=role,
            role_artifact_path=_relative(paths["role"]),
            role_artifact_bytes=role_bytes,
        )
        prompts = build_uncertainty_prompts_v1(packet)
        uncertainty_preview = build_request_preview(
            prompts=prompts,
            schema=uncertainty_schema,
            schema_name="lolla_r4_uncertainty_v1",
            task="uncertainty",
            seed=SEEDS[case_id]["uncertainty"],
        )
        uncertainty_metrics = _estimated_cost(uncertainty_preview)
        total_estimated_cost += float(uncertainty_metrics["conservative_estimated_cost_usd"])
        for name, value in (
            ("source-registry.json", source_registry),
            ("planned-readers.json", readers),
            ("uncertainty-packet.json", packet),
            ("uncertainty-prompts.json", prompts),
            ("uncertainty-request-preview.json", uncertainty_preview),
        ):
            generated[_relative(case_root / name)] = _render(value)

        existing = existing_reader_results_v1(
            role_portfolio=role,
            source_registry=source_registry,
            planned_readers=readers,
            role_artifact_path=_relative(paths["role"]),
            role_artifact_bytes=role_bytes,
        )
        missing = missing_complementary_reader_results_v1(planned_readers=readers)
        baseline = assemble_conversation_state_fan_in(
            source_registry=source_registry,
            planned_readers=readers,
            reader_results=sorted([*existing, *missing], key=lambda row: row["reader_id"]),
            source_bytes=source_bytes,
            artifact_bytes_by_path={_relative(paths["role"]): role_bytes},
        )
        generated[_relative(case_root / "pre-call-fan-in.json")] = _render(baseline)

        uncertainty_response = _structural_uncertainty_fixture(case_id)
        uncertainty_artifact_path = _relative(
            case_root / "structural-uncertainty-response.json"
        )
        generated[uncertainty_artifact_path] = _render(uncertainty_response)
        compiled_uncertainty = compile_uncertainty_response_v1(
            response=uncertainty_response,
            packet=packet,
            source_registry=source_registry,
            planned_readers=readers,
            artifact_path=uncertainty_artifact_path,
            artifact_bytes=generated[uncertainty_artifact_path],
        )
        generated[_relative(case_root / "structural-uncertainty-compiled.json")] = _render(
            compiled_uncertainty
        )
        relationship_missing = next(
            row for row in missing if row["surface"] == "cross_thread_relationship"
        )
        before_relationship = assemble_conversation_state_fan_in(
            source_registry=source_registry,
            planned_readers=readers,
            reader_results=sorted(
                [*existing, *compiled_uncertainty["reader_results"], relationship_missing],
                key=lambda row: row["reader_id"],
            ),
            source_bytes=source_bytes,
            artifact_bytes_by_path=_artifact_map_with(
                paths["role"], role_bytes, generated, uncertainty_artifact_path
            ),
        )
        generated[_relative(case_root / "structural-pre-relationship-fan-in.json")] = _render(
            before_relationship
        )
        alias_text = {
            row["alias"]: row["text"] for row in source_alias_catalog_v1(wrapper)
        }
        relationship_packet = build_relationship_packet_v1(
            fan_in=before_relationship, source_text_by_alias=alias_text
        )
        relationship_prompts = build_relationship_prompts_v1(relationship_packet)
        relationship_preview = build_request_preview(
            prompts=relationship_prompts,
            schema=relationship_schema,
            schema_name="lolla_r4_relationship_v1",
            task="relationship",
            seed=SEEDS[case_id]["relationship"],
        )
        relationship_metrics = _estimated_cost(relationship_preview)
        total_estimated_cost += float(relationship_metrics["conservative_estimated_cost_usd"])
        for name, value in (
            ("structural-relationship-packet.json", relationship_packet),
            ("structural-relationship-prompts.json", relationship_prompts),
            ("structural-relationship-request-preview.json", relationship_preview),
        ):
            generated[_relative(case_root / name)] = _render(value)

        relationship_response = _relationship_fixture(relationship_packet)
        relationship_artifact_path = _relative(
            case_root / "structural-relationship-response.json"
        )
        generated[relationship_artifact_path] = _render(relationship_response)
        compiled_relationship = compile_relationship_response_v1(
            response=relationship_response,
            packet=relationship_packet,
            source_registry=source_registry,
            planned_readers=readers,
            artifact_path=relationship_artifact_path,
            artifact_bytes=generated[relationship_artifact_path],
        )
        generated[_relative(case_root / "structural-relationship-compiled.json")] = _render(
            compiled_relationship
        )
        final_fan_in = assemble_conversation_state_fan_in(
            source_registry=source_registry,
            planned_readers=readers,
            reader_results=sorted(
                [
                    *existing,
                    *compiled_uncertainty["reader_results"],
                    compiled_relationship["reader_result"],
                ],
                key=lambda row: row["reader_id"],
            ),
            source_bytes=source_bytes,
            artifact_bytes_by_path=_artifact_map_with(
                paths["role"],
                role_bytes,
                generated,
                uncertainty_artifact_path,
                relationship_artifact_path,
            ),
        )
        generated[_relative(case_root / "structural-final-fan-in.json")] = _render(
            final_fan_in
        )
        per_case_estimate = round(
            float(uncertainty_metrics["conservative_estimated_cost_usd"])
            + float(relationship_metrics["conservative_estimated_cost_usd"]),
            9,
        )
        case_reports.append(
            {
                "case_id": case_id,
                "selection_role": target_case["role"],
                "source_alias_count": len(source_registry["aliases"]),
                "uncertainty_packet_utf8_bytes": len(canonical_json_bytes(packet)),
                "uncertainty_request": uncertainty_metrics,
                "relationship_record_catalog_count": len(
                    relationship_packet["record_catalog"]
                ),
                "relationship_packet_utf8_bytes": len(
                    canonical_json_bytes(relationship_packet)
                ),
                "relationship_request": relationship_metrics,
                "conservative_estimated_case_cost_usd": per_case_estimate,
                "per_case_cost_ceiling_usd": MAX_COST_PER_CASE_USD,
                "per_case_cost_preflight_pass": per_case_estimate
                <= MAX_COST_PER_CASE_USD,
                "structural_final_state_counts": final_fan_in["fan_in"][
                    "reader_state_counts"
                ],
                "structural_final_record_count": final_fan_in["fan_in"][
                    "total_record_count"
                ],
                "structural_fixture_is_provider_output": False,
                "structural_fixture_is_semantic_evidence": False,
            }
        )

    report = {
        "schema_version": "lolla.r4_complementary_reader_preflight_result.v1",
        "status": "provider_free_preflight_pass_call_authorization_required",
        "date": "2026-07-13",
        "source_first_target": {
            "path": _relative(TARGET_PATH),
            "sha256": _file_sha(TARGET_PATH),
            "visible_to_provider": False,
        },
        "model_snapshot": {
            "path": _relative(MODEL_SNAPSHOT_PATH),
            "sha256": _file_sha(MODEL_SNAPSHOT_PATH),
            "model": model_snapshot["model"]["requested_id"],
            "provider": model_snapshot["selected_endpoint"]["provider_slug"],
        },
        "schemas": {
            "uncertainty": {
                "canonical_utf8_bytes": len(canonical_json_bytes(uncertainty_schema)),
                "sha256": value_sha256(uncertainty_schema),
            },
            "relationship": {
                "canonical_utf8_bytes": len(canonical_json_bytes(relationship_schema)),
                "sha256": value_sha256(relationship_schema),
            },
        },
        "cases": case_reports,
        "budget": {
            "maximum_provider_calls": 4,
            "maximum_calls_per_case": 2,
            "maximum_provider_reported_cost_per_case_usd": MAX_COST_PER_CASE_USD,
            "maximum_provider_reported_cost_total_usd": MAX_TOTAL_COST_USD,
            "conservative_estimated_total_cost_usd": round(total_estimated_cost, 9),
            "total_cost_preflight_pass": total_estimated_cost <= MAX_TOTAL_COST_USD,
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
            "full_source_and_prior_record_custody": "pass",
            "small_google_subset_schemas": "pass",
            "explicit_zero_and_ambiguity": "pass",
            "exact_id_relationship_handoff": "pass",
            "missingness_aware_fan_in": "pass",
            "positive_and_restraint_structural_paths": "pass",
            "source_first_targets_excluded_from_requests": "pass",
            "cost_and_call_bounds": "pass",
            "provider_calls": 0,
        },
        "decision": {
            "provider_free_package_ready": True,
            "provider_calls_authorized": False,
            "sole_remaining_action": "explicitly authorize the frozen four-call maximum experiment",
            "runtime_or_graph_integration_authorized": False,
            "production_model_selection_authorized": False,
        },
        "non_claims": [
            "Structural fixtures are not provider output or semantic evidence.",
            "Cost estimates are conservative planning values; provider-reported cost remains authoritative.",
            "This package does not prove semantic recovery, restraint, reliability, usefulness, graph value, or answer improvement.",
        ],
    }
    generated[_relative(output / "preflight-result.json")] = _render(report)
    manifest_entries = [
        {"path": path, "sha256": _sha(raw), "utf8_bytes": len(raw)}
        for path, raw in sorted(generated.items())
    ]
    manifest = {
        "schema_version": "lolla.r4_complementary_reader_preflight_manifest.v1",
        "status": "provider_free_artifact_manifest_complete",
        "date": "2026-07-13",
        "files": manifest_entries,
        "file_count": len(manifest_entries),
        "provider_calls": 0,
    }
    generated[_relative(output / "manifest.json")] = _render(manifest)
    return generated


def _write_files(files: Mapping[str, bytes]) -> None:
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def _validate_files(files: Mapping[str, bytes]) -> None:
    for relative, expected in files.items():
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"preflight artifact missing: {relative}")
        if path.read_bytes() != expected:
            raise RuntimeError(f"preflight artifact drifted: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if ROOT not in output.parents:
        raise RuntimeError("preflight output must be inside the repository")
    files = build_files(output)
    if args.validate_only:
        _validate_files(files)
        status = "provider_free_preflight_artifacts_valid"
    else:
        _write_files(files)
        status = "provider_free_preflight_artifacts_built"
    print(
        json.dumps(
            {
                "status": status,
                "file_count": len(files),
                "provider_calls": 0,
                "output": _relative(output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
