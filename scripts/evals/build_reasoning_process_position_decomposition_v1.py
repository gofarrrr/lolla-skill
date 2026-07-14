#!/usr/bin/env python3
"""Replay reviewed position fixtures through the provider-free decomposition."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader_v43 import (  # noqa: E402
    shard_response_schema_v43,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_position_decomposition_v1 import (  # noqa: E402
    ROLE_EVIDENCE_FIELDS,
    build_role_trajectory_prompts_v1,
    build_stance_role_packet_v1,
    build_stance_role_prompts_v1,
    compile_role_trajectory_response_v1,
    compile_stance_role_response_v1,
    join_position_decomposition_v1,
    role_trajectory_response_schema_v1,
    stance_role_response_schema_v1,
)

COMBINED_STANCE_FIELDS = {
    "stance_temporal_roles",
    "stance_object_kinds",
    "stance_object_interpretations",
    "stance_expression_kinds",
    "stance_source_evidence_ids",
    "stance_object_fidelity_note",
}
RESERVED_CASE_ID = "amb2-case03-agency-acquisition"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _display_path(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def _property_count(value: object) -> int:
    if isinstance(value, dict):
        return len(value.get("properties", {})) + sum(
            _property_count(child) for child in value.values()
        )
    if isinstance(value, list):
        return sum(_property_count(child) for child in value)
    return 0


def _trajectory_projection(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": response["status"],
        "records": [
            {key: value for key, value in record.items() if key not in COMBINED_STANCE_FIELDS}
            for record in response["records"]
        ],
        "global_limitations": response["global_limitations"],
    }


def _stance_projection(
    *,
    response: dict[str, Any],
    trajectory_compiled: dict[str, Any],
    role: str,
) -> dict[str, Any] | None:
    projected_records = []
    trajectory_by_index = {
        item["raw_record"]["record_index"]: item["trajectory_record_id"]
        for item in trajectory_compiled["observations"]
    }
    for index, record in enumerate(response["records"], 1):
        component_indices = [
            component_index
            for component_index, component_role in enumerate(record["stance_temporal_roles"])
            if component_role == role
        ]
        if not component_indices:
            continue
        projected_records.append(
            {
                "trajectory_record_id": trajectory_by_index[index],
                "role": role,
                "status": record["status"],
                "object_kinds": [record["stance_object_kinds"][i] for i in component_indices],
                "object_interpretations": [
                    record["stance_object_interpretations"][i] for i in component_indices
                ],
                "expression_kinds": [
                    record["stance_expression_kinds"][i] for i in component_indices
                ],
                "source_evidence_ids": [
                    record["stance_source_evidence_ids"][i] for i in component_indices
                ],
                "fidelity_note": record["stance_object_fidelity_note"],
                "limitations": record["limitations"],
            }
        )
    if not projected_records:
        return None
    return {
        "status": response["status"],
        "records": projected_records,
        "global_limitations": response["global_limitations"],
    }


def build(output: Path) -> dict[str, Any]:
    source_report_path = (
        ROOT / "research/reasoning-process-stance-object-v42-2026-07-12/report.json"
    )
    source_report = _load(source_report_path)
    protected = [
        artifact for artifact in source_report["artifacts"]
        if artifact["protected_fixture_path"] is not None
    ]
    position = [
        artifact for artifact in protected
        if artifact["view_kind"] == "position_and_decision_trajectory"
    ]
    eligible = [artifact for artifact in position if artifact["case_id"] != RESERVED_CASE_ID]

    monolithic_schema = shard_response_schema_v43("position_and_decision_trajectory")
    schema_inventory = {
        "v43_monolithic": {
            **schema_metrics(monolithic_schema),
            "property_count": _property_count(monolithic_schema),
        },
        "role_trajectory": {
            **schema_metrics(role_trajectory_response_schema_v1()),
            "property_count": _property_count(role_trajectory_response_schema_v1()),
        },
        **{
            f"stance_{role}": {
                **schema_metrics(stance_role_response_schema_v1(role)),
                "property_count": _property_count(stance_role_response_schema_v1(role)),
            }
            for role in ROLE_EVIDENCE_FIELDS
        },
    }

    artifacts = []
    admitted_trajectories = admitted_stance_records = 0
    quarantined = missing = 0
    max_planned_calls = max_user_prompt_bytes = 0
    for artifact in eligible:
        packet_path = ROOT / artifact["packet_path"]
        fixture_path = ROOT / artifact["protected_fixture_path"]
        wrapper = _load(packet_path)
        fixture = _load(fixture_path)
        combined_response = fixture["response"]
        trajectory_response = _trajectory_projection(combined_response)
        trajectory_compiled = compile_role_trajectory_response_v1(
            response=trajectory_response,
            wrapper=wrapper,
            producer_kind="source_reviewer",
            producer_id="decomposition-v1-mechanical-projection-of-reviewed-v41-fixture",
            record_identity=artifact["case_id"],
        )
        trajectory_prompt = build_role_trajectory_prompts_v1(wrapper)
        max_user_prompt_bytes = max(
            max_user_prompt_bytes,
            len(trajectory_prompt["user_prompt"].encode("utf-8")),
        )
        stance_packets = {}
        stance_responses = {}
        stance_compiled = {}
        for role in ROLE_EVIDENCE_FIELDS:
            role_packet = build_stance_role_packet_v1(
                trajectory_compiled=trajectory_compiled,
                wrapper=wrapper,
                role=role,
            )
            stance_packets[role] = role_packet
            if not role_packet["call_required"]:
                stance_responses[role] = None
                stance_compiled[role] = None
                continue
            role_response = _stance_projection(
                response=combined_response,
                trajectory_compiled=trajectory_compiled,
                role=role,
            )
            if role_response is None:
                raise RuntimeError("reviewed fixture lacks a component for an applicable role")
            stance_responses[role] = role_response
            stance_compiled[role] = compile_stance_role_response_v1(
                response=role_response,
                packet=role_packet,
                producer_kind="source_reviewer",
                producer_id="decomposition-v1-mechanical-projection-of-reviewed-v41-fixture",
            )
            role_prompt = build_stance_role_prompts_v1(role_packet)
            max_user_prompt_bytes = max(
                max_user_prompt_bytes,
                len(role_prompt["user_prompt"].encode("utf-8")),
            )
        joined = join_position_decomposition_v1(
            trajectory_compiled=trajectory_compiled,
            stance_compiled_by_role=stance_compiled,
        )
        case_output = {
            "schema_version": "lolla.reasoning_process_position_decomposition_fixture.v1",
            "case_id": artifact["case_id"],
            "source": {
                "packet_path": artifact["packet_path"],
                "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
                "reviewed_fixture_path": artifact["protected_fixture_path"],
                "reviewed_fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
            },
            "trajectory_response": trajectory_response,
            "trajectory_compiled": trajectory_compiled,
            "stance_packets": stance_packets,
            "stance_responses": stance_responses,
            "stance_compiled": stance_compiled,
            "joined": joined,
        }
        case_path = output / "fixtures" / f"{artifact['case_id']}.json"
        _write(case_path, case_output)
        artifacts.append(
            {
                "case_id": artifact["case_id"],
                "source_fixture_path": artifact["protected_fixture_path"],
                "decomposition_fixture_path": _display_path(case_path),
                "status": joined["status"],
                "planned_call_count": joined["fan_in"]["planned_call_count"],
            }
        )
        admitted_trajectories += len(trajectory_compiled["observations"])
        for compiled in stance_compiled.values():
            if compiled:
                admitted_stance_records += len(compiled["observations"])
                quarantined += sum(
                    item["terminal_state"] == "quarantined" for item in compiled["records"]
                )
                missing += len(compiled["missing_trajectory_record_ids"])
        max_planned_calls = max(max_planned_calls, joined["fan_in"]["planned_call_count"])

    per_call_schemas = [value for key, value in schema_inventory.items() if key != "v43_monolithic"]
    max_decomposed_schema_bytes = max(item["bytes"] for item in per_call_schemas)
    max_decomposed_property_count = max(item["property_count"] for item in per_call_schemas)
    complete = sum(item["status"] == "position_decomposition_complete" for item in artifacts)
    gate = (
        len(protected) == 23
        and len(position) == 8
        and len(eligible) == 7
        and complete == 7
        and quarantined == 0
        and missing == 0
        and max_planned_calls <= 4
        and max_decomposed_schema_bytes < schema_inventory["v43_monolithic"]["bytes"]
        and max_decomposed_property_count < schema_inventory["v43_monolithic"]["property_count"]
    )
    report = {
        "schema_version": "lolla.reasoning_process_position_decomposition_report.v1",
        "status": "provider_free_position_decomposition_pass" if gate else "provider_free_position_decomposition_fail",
        "date": "2026-07-12",
        "source_report_path": str(source_report_path.relative_to(ROOT)),
        "artifacts": artifacts,
        "reserved_case": {
            "case_id": RESERVED_CASE_ID,
            "reason": "preserve the existing fresh agency-acquisition fixture from this new development replay",
            "provider_calls": 0,
            "projection_performed": False,
        },
        "schema_inventory": schema_inventory,
        "summary": {
            "reviewed_input_fixture_count": len(protected),
            "reviewed_position_fixture_count": len(position),
            "provider_free_decomposition_fixture_count": len(eligible),
            "reserved_position_fixture_count": len(position) - len(eligible),
            "complete_join_count": complete,
            "admitted_trajectory_record_count": admitted_trajectories,
            "admitted_stance_record_count": admitted_stance_records,
            "quarantined_record_count": quarantined,
            "missing_role_record_count": missing,
            "maximum_planned_calls_per_shard": max_planned_calls,
            "maximum_user_prompt_utf8_bytes": max_user_prompt_bytes,
            "maximum_decomposed_schema_bytes": max_decomposed_schema_bytes,
            "maximum_decomposed_property_count": max_decomposed_property_count,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "provider_free_contract_gate": "pass" if gate else "fail",
            "provider_probe_authorized": False,
            "source_review_authorized": gate,
            "next_required_evidence": (
                "adversarial local contract review, then a separately frozen one-case provider probe"
                if gate else "repair local decomposition contract without a provider call"
            ),
        },
        "claims": {
            "representational_capacity_preserved_on_reviewed_position_fixtures": gate,
            "automatic_extraction_improved": False,
            "provider_acceptance_proven": False,
            "semantic_quality_improved": False,
            "production_integration_authorized": False,
        },
        "boundary": {
            "reviewed_combined_semantics_mechanically_projected": True,
            "new_semantic_labels_created": False,
            "deterministic_semantic_gate_added": False,
            "semantic_join_performed": False,
            "fan_in_measured": True,
            "reserved_case_untouched": True,
        },
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps({"status": report["status"], "summary": report["summary"]}, indent=2))
    return 0 if report["decision"]["provider_free_contract_gate"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
