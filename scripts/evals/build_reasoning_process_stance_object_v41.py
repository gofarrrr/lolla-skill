#!/usr/bin/env python3
"""Build provider-free v4.1 prompts, legacy replay, and fresh reviewed fixtures."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader_v41 import (  # noqa: E402
    build_shard_prompts_v41,
    compile_shard_response_recordwise_v41,
    shard_response_schema_v41,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _manifest(*, wrapper: dict[str, Any], packet_path: str) -> dict[str, Any]:
    view = wrapper["packet"]["view_kind"]
    prompts = build_shard_prompts_v41(wrapper)
    schema = shard_response_schema_v41(view)
    metrics = schema_metrics(schema)
    return {
        "case_id": wrapper["packet"]["case_id"],
        "view_kind": view,
        "shard_id": wrapper["packet"]["shard_id"],
        "packet_path": packet_path,
        "packet_sha256": hashlib.sha256((ROOT / packet_path).read_bytes()).hexdigest(),
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "user_prompt_utf8_bytes": len(prompts["user_prompt"].encode("utf-8")),
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
        "response_schema_metrics": metrics,
        "question_is_last_prompt_section": prompts["user_prompt"].rfind("Question:")
        > prompts["user_prompt"].rfind("contract:"),
    }


def _components_to_columns(record: dict[str, Any], components: list[dict[str, Any]]) -> None:
    record["stance_temporal_roles"] = [item["temporal_role"] for item in components]
    record["stance_object_kinds"] = [item["stance_object_kind"] for item in components]
    record["stance_object_interpretations"] = [
        item["stance_object_interpretation"] for item in components
    ]
    record["stance_expression_kinds"] = [item["stance_expression_kind"] for item in components]
    record["stance_source_evidence_ids"] = [item["source_evidence_id"] for item in components]


def _atomic_projection(response: dict[str, Any]) -> dict[str, Any]:
    projected = copy.deepcopy(response)
    for record in projected["records"]:
        old_components = record.pop("stance_components")
        note = record.pop("stance_object_fidelity_note")
        atomic = []
        for component in old_components:
            for evidence_id in component["source_evidence_ids"]:
                atomic.append(
                    {
                        "temporal_role": component["temporal_role"],
                        "stance_object_kind": component["stance_object_kind"],
                        "stance_object_interpretation": component[
                            "stance_object_interpretation"
                        ],
                        "stance_expression_kind": component["stance_expression_kind"],
                        "source_evidence_id": evidence_id,
                    }
                )
        _components_to_columns(record, atomic)
        record["stance_object_fidelity_note"] = note
    return projected


def _fresh_projection(response: dict[str, Any]) -> dict[str, Any]:
    projected = copy.deepcopy(response)
    for record in projected["records"]:
        components = record.pop("stance_components")
        _components_to_columns(record, components)
    return projected


def _new_component_keywords(schema: dict[str, Any]) -> set[str]:
    properties = schema["properties"]["records"]["items"]["properties"]
    component = {
        field: properties[field]
        for field in (
            "stance_temporal_roles",
            "stance_object_kinds",
            "stance_object_interpretations",
            "stance_expression_kinds",
            "stance_source_evidence_ids",
            "stance_object_fidelity_note",
        )
    }
    found: set[str] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            found.update(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(component)
    return found


def build(output: Path) -> dict[str, Any]:
    v4 = _load(ROOT / "research/reasoning-process-stance-object-v4-2026-07-12/report.json")
    fresh_corpus = _load(
        ROOT / "research/reasoning-process-stance-object-v41-fresh-corpus-2026-07-12/report.json"
    )
    fresh_fixtures = _load(
        ROOT / "docs/evals/reasoning-process-stance-object-v41-fresh-fixtures-v1.json"
    )
    fixture_by_case = {item["case_id"]: item for item in fresh_fixtures["fixtures"]}
    prompt_count = legacy_fixture_count = fresh_fixture_count = admitted = quarantined = 0
    max_prompt = max_schema_bytes = max_schema_depth = 0
    non_position_unchanged = True
    position_changed = True
    legacy_cases = []
    for case in v4["cases"]:
        artifacts = []
        for artifact in case["artifacts"]:
            wrapper = _load(ROOT / artifact["packet_path"])
            manifest = _manifest(wrapper=wrapper, packet_path=artifact["packet_path"])
            previous_manifest = _load(ROOT / artifact["prompt_manifest_path"])
            if artifact["view_kind"] == "position_and_decision_trajectory":
                position_changed &= (
                    manifest["user_prompt_sha256"] != previous_manifest["user_prompt_sha256"]
                    and manifest["response_schema_sha256"]
                    != previous_manifest["response_schema_sha256"]
                )
            else:
                non_position_unchanged &= manifest == previous_manifest
            manifest_path = (
                output
                / "prompt-manifests"
                / case["case_id"]
                / f"{wrapper['packet']['shard_id']}.json"
            )
            _write(manifest_path, manifest)
            prompt_count += 1
            max_prompt = max(max_prompt, manifest["user_prompt_utf8_bytes"])
            max_schema_bytes = max(max_schema_bytes, manifest["response_schema_metrics"]["bytes"])
            max_schema_depth = max(max_schema_depth, manifest["response_schema_metrics"]["depth"])
            fixture_path = None
            if artifact["protected_fixture_path"]:
                previous = _load(ROOT / artifact["protected_fixture_path"])
                response = (
                    _atomic_projection(previous["response"])
                    if artifact["view_kind"] == "position_and_decision_trajectory"
                    else copy.deepcopy(previous["response"])
                )
                compiled = compile_shard_response_recordwise_v41(
                    response=response,
                    wrapper=wrapper,
                    producer_kind="source_reviewer",
                    producer_id="v41-atomic-projection-of-reviewed-v4-fixture",
                    record_identity=previous["target"]["target_id"],
                )
                fixture_path = (
                    output
                    / "legacy-protected-fixtures"
                    / case["case_id"]
                    / f"{artifact['view_kind']}.json"
                )
                _write(
                    fixture_path,
                    {
                        "target": previous["target"],
                        "response": response,
                        "compiled": compiled,
                    },
                )
                legacy_fixture_count += 1
                admitted += sum(item["terminal_state"] == "admitted" for item in compiled["records"])
                quarantined += sum(item["terminal_state"] == "quarantined" for item in compiled["records"])
            artifacts.append(
                {
                    **artifact,
                    "prompt_manifest_path": str(manifest_path.relative_to(ROOT)),
                    "protected_fixture_path": str(fixture_path.relative_to(ROOT))
                    if fixture_path
                    else None,
                }
            )
        legacy_cases.append({"case_id": case["case_id"], "artifacts": artifacts})
    fresh_cases = []
    for case in fresh_corpus["cases"]:
        wrapper = _load(ROOT / case["packet_path"])
        manifest = _manifest(wrapper=wrapper, packet_path=case["packet_path"])
        manifest_path = output / "fresh-prompt-manifests" / f"{case['case_id']}.json"
        _write(manifest_path, manifest)
        prompt_count += 1
        max_prompt = max(max_prompt, manifest["user_prompt_utf8_bytes"])
        max_schema_bytes = max(max_schema_bytes, manifest["response_schema_metrics"]["bytes"])
        max_schema_depth = max(max_schema_depth, manifest["response_schema_metrics"]["depth"])
        fixture = fixture_by_case[case["case_id"]]
        response = _fresh_projection(fixture["response"])
        compiled = compile_shard_response_recordwise_v41(
            response=response,
            wrapper=wrapper,
            producer_kind="source_reviewer",
            producer_id="v41-fresh-source-reviewed-fixture",
            record_identity=fixture["target_id"],
        )
        fixture_path = output / "fresh-protected-fixtures" / f"{case['case_id']}.json"
        _write(
            fixture_path,
            {
                "target_id": fixture["target_id"],
                "protected_target": fixture["protected_target"],
                "response": response,
                "compiled": compiled,
            },
        )
        fresh_fixture_count += 1
        admitted += sum(item["terminal_state"] == "admitted" for item in compiled["records"])
        quarantined += sum(item["terminal_state"] == "quarantined" for item in compiled["records"])
        fresh_cases.append(
            {
                "case_id": case["case_id"],
                "source_path": case["source_path"],
                "packet_path": case["packet_path"],
                "prompt_manifest_path": str(manifest_path.relative_to(ROOT)),
                "protected_fixture_path": str(fixture_path.relative_to(ROOT)),
            }
        )
    position_schema = shard_response_schema_v41("position_and_decision_trajectory")
    component_keywords = _new_component_keywords(position_schema)
    forbidden_new_keywords = sorted(
        component_keywords & {"oneOf", "anyOf", "allOf", "$ref", "$defs", "pattern", "uniqueItems"}
    )
    metrics = schema_metrics(position_schema)
    compatibility_gate = (
        metrics["bytes"] < 4000 and metrics["depth"] <= 9 and not forbidden_new_keywords
    )
    provider_free_gate = (
        legacy_fixture_count == 20
        and fresh_fixture_count == 3
        and admitted == 23
        and quarantined == 0
        and non_position_unchanged
        and position_changed
        and compatibility_gate
    )
    report = {
        "schema_version": "lolla.reasoning_process_stance_object_v41_report.v1",
        "status": "provider_free_stance_object_v41_pass" if provider_free_gate else "provider_free_stance_object_v41_fail",
        "date": "2026-07-12",
        "legacy_cases": legacy_cases,
        "fresh_cases": fresh_cases,
        "fresh_case_selection": fresh_corpus["selection"],
        "summary": {
            "prompt_count": prompt_count,
            "legacy_prompt_count": 60,
            "fresh_prompt_count": 3,
            "legacy_protected_fixture_count": legacy_fixture_count,
            "fresh_protected_fixture_count": fresh_fixture_count,
            "protected_admitted_record_count": admitted,
            "protected_quarantined_record_count": quarantined,
            "maximum_user_prompt_utf8_bytes": max_prompt,
            "maximum_response_schema_bytes": max_schema_bytes,
            "maximum_response_schema_depth": max_schema_depth,
            "position_response_schema_bytes": metrics["bytes"],
            "position_response_schema_depth": metrics["depth"],
            "new_component_forbidden_schema_keywords": forbidden_new_keywords,
            "non_position_prompt_and_schema_unchanged": non_position_unchanged,
            "position_prompt_and_schema_changed": position_changed,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "provider_free_stance_object_v41_gate": "pass" if provider_free_gate else "fail",
            "documented_subset_compatibility_gate": "pass" if compatibility_gate else "fail",
            "adversarial_review_authorized": provider_free_gate,
            "provider_probe_authorized": False,
        },
        "boundary": {
            "one_alias_per_component": True,
            "deterministic_object_or_expression_inference": False,
            "deterministic_compatibility_matrix": False,
            "semantic_case_selection": False,
            "source_review_fixtures_seen_by_model": False,
            "global_synthesis_authorized": False,
            "graph_or_runtime_authorized": False,
        },
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps({"selection": report["fresh_case_selection"], "summary": report["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
