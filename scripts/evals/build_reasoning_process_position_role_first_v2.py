#!/usr/bin/env python3
"""Project reviewed position fixtures into the provider-free role-first v2 design."""
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
from engine.system_b.reasoning_process_position_role_first_v2 import (  # noqa: E402
    ROLE_ORDER,
    build_position_relation_packet_v2,
    build_position_relation_prompts_v2,
    build_position_role_packet_v2,
    build_position_role_prompts_v2,
    compile_position_relation_response_v2,
    compile_position_role_response_v2,
    join_position_role_first_v2,
    position_relation_response_schema_v2,
    position_role_response_schema_v2,
)
from engine.system_b.reasoning_process_position_decomposition_v1 import (  # noqa: E402
    ROLE_EVIDENCE_FIELDS,
    ROLE_INTERPRETATION_FIELDS,
)


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


def _role_projection(*, response: dict[str, Any], role: str) -> dict[str, Any]:
    records = []
    evidence_field = ROLE_EVIDENCE_FIELDS[role]
    interpretation_field = ROLE_INTERPRETATION_FIELDS[role]
    for combined in response["records"]:
        evidence = combined[evidence_field]
        if not evidence:
            continue
        indices = [
            index for index, value in enumerate(combined["stance_temporal_roles"])
            if value == role
        ]
        if not indices:
            raise RuntimeError("reviewed combined fixture lacks stance coverage for a visible role")
        records.append(
            {
                "role": role,
                "status": combined["status"],
                "evidence_ids": evidence,
                "role_interpretation": combined[interpretation_field],
                "object_kinds": [combined["stance_object_kinds"][i] for i in indices],
                "object_interpretations": [
                    combined["stance_object_interpretations"][i] for i in indices
                ],
                "expression_kinds": [
                    combined["stance_expression_kinds"][i] for i in indices
                ],
                "source_evidence_ids": [
                    combined["stance_source_evidence_ids"][i] for i in indices
                ],
                "fidelity_note": combined["stance_object_fidelity_note"],
                "limitations": combined["limitations"],
            }
        )
    return {
        "status": response["status"] if records else "not_found",
        "records": records,
        "global_limitations": response["global_limitations"],
    }


def _relation_projection(
    *, response: dict[str, Any], role_compiled: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    by_role_and_index = {
        role: {
            item["source_record_index"]: item["role_record_id"]
            for item in compiled["observations"]
        }
        for role, compiled in role_compiled.items()
    }
    records = []
    for index, combined in enumerate(response["records"], 1):
        records.append(
            {
                "status": combined["status"],
                "starting_role_record_id": by_role_and_index["starting"].get(index, ""),
                "current_role_record_id": by_role_and_index["current"][index],
                "qualification_role_record_id": by_role_and_index["qualification"].get(index, ""),
                "relationship_interpretation": combined["trajectory_interpretation"],
                "limitations": combined["limitations"],
            }
        )
    return {
        "status": response["status"] if records else "not_found",
        "records": records,
        "global_limitations": response["global_limitations"],
    }


def build(output: Path) -> dict[str, Any]:
    source_report = _load(
        ROOT / "research/reasoning-process-stance-object-v42-2026-07-12/report.json"
    )
    positions = [
        artifact for artifact in source_report["artifacts"]
        if artifact["view_kind"] == "position_and_decision_trajectory"
        and artifact["protected_fixture_path"] is not None
    ]
    artifacts = []
    role_admitted = relation_admitted = quarantine = 0
    complete = 0
    max_prompt_bytes = 0
    for artifact in positions:
        wrapper_path = ROOT / artifact["packet_path"]
        fixture_path = ROOT / artifact["protected_fixture_path"]
        wrapper = _load(wrapper_path)
        response = _load(fixture_path)["response"]
        role_packets = {}
        role_responses = {}
        role_compiled = {}
        for role in ROLE_ORDER:
            packet = build_position_role_packet_v2(wrapper=wrapper, role=role)
            projected = _role_projection(response=response, role=role)
            compiled = compile_position_role_response_v2(
                response=projected,
                packet=packet,
                producer_kind="source_reviewer",
                producer_id="role-first-v2-mechanical-projection-of-reviewed-v41-fixture",
            )
            role_packets[role] = packet
            role_responses[role] = projected
            role_compiled[role] = compiled
            prompt = build_position_role_prompts_v2(packet)
            max_prompt_bytes = max(
                max_prompt_bytes, len(prompt["user_prompt"].encode("utf-8"))
            )
            role_admitted += len(compiled["observations"])
            quarantine += sum(
                item["terminal_state"] == "quarantined" for item in compiled["records"]
            )
        relation_packet = build_position_relation_packet_v2(
            role_compiled_by_role=role_compiled
        )
        relation_response = _relation_projection(
            response=response, role_compiled=role_compiled
        )
        relation_compiled = compile_position_relation_response_v2(
            response=relation_response,
            packet=relation_packet,
            producer_kind="source_reviewer",
            producer_id="role-first-v2-mechanical-projection-of-reviewed-v41-fixture",
        )
        relation_prompt = build_position_relation_prompts_v2(relation_packet)
        max_prompt_bytes = max(
            max_prompt_bytes, len(relation_prompt["user_prompt"].encode("utf-8"))
        )
        relation_admitted += len(relation_compiled["observations"])
        quarantine += sum(
            item["terminal_state"] == "quarantined"
            for item in relation_compiled["records"]
        )
        joined = join_position_role_first_v2(
            role_compiled_by_role=role_compiled,
            relation_compiled=relation_compiled,
        )
        complete += joined["status"] == "position_role_first_join_complete"
        case_output = {
            "schema_version": "lolla.reasoning_process_position_role_first_fixture.v2",
            "case_id": artifact["case_id"],
            "source": {
                "packet_path": artifact["packet_path"],
                "packet_sha256": hashlib.sha256(wrapper_path.read_bytes()).hexdigest(),
                "reviewed_fixture_path": artifact["protected_fixture_path"],
                "reviewed_fixture_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
            },
            "role_packets": role_packets,
            "role_responses": role_responses,
            "role_compiled": role_compiled,
            "relation_packet": relation_packet,
            "relation_response": relation_response,
            "relation_compiled": relation_compiled,
            "joined": joined,
        }
        case_path = output / "fixtures" / f"{artifact['case_id']}.json"
        _write(case_path, case_output)
        artifacts.append(
            {
                "case_id": artifact["case_id"],
                "fixture_path": _display_path(case_path),
                "status": joined["status"],
            }
        )
    schemas = {
        **{f"role_{role}": position_role_response_schema_v2(role) for role in ROLE_ORDER},
        "relation": position_relation_response_schema_v2(),
    }
    schema_inventory = {
        name: {
            **schema_metrics(schema),
            "property_count": _property_count(schema),
        }
        for name, schema in schemas.items()
    }
    monolithic = shard_response_schema_v43("position_and_decision_trajectory")
    monolithic_metrics = {
        **schema_metrics(monolithic),
        "property_count": _property_count(monolithic),
    }
    gate = (
        len(positions) == 8
        and complete == 8
        and role_admitted == 24
        and relation_admitted == 8
        and quarantine == 0
        and max(item["bytes"] for item in schema_inventory.values()) < monolithic_metrics["bytes"]
        and max(item["property_count"] for item in schema_inventory.values())
        < monolithic_metrics["property_count"]
    )
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_report.v2",
        "status": "provider_free_position_role_first_pass" if gate else "provider_free_position_role_first_fail",
        "date": "2026-07-12",
        "artifacts": artifacts,
        "schema_inventory": {"v43_monolithic": monolithic_metrics, **schema_inventory},
        "summary": {
            "reviewed_position_fixture_count": len(positions),
            "complete_join_count": complete,
            "admitted_role_record_count": role_admitted,
            "admitted_relation_record_count": relation_admitted,
            "quarantined_record_count": quarantine,
            "maximum_provider_calls_per_shard": 4,
            "maximum_role_records_at_relation_fan_in": 6,
            "maximum_user_prompt_utf8_bytes": max_prompt_bytes,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "failure_driven_changes": {
            "three_roles_are_independent_jobs": True,
            "trajectory_category_removed": True,
            "relationship_is_a_fourth_exact_id_job": True,
            "quarantined_or_unreferenced_records_make_join_incomplete": True,
            "reason": "v1 live probe contradicted its categorical trajectory label, omitted protected qualification evidence, and exposed a false-complete empty join",
        },
        "decision": {
            "provider_free_contract_gate": "pass" if gate else "fail",
            "provider_probe_authorized": False,
            "next_required_evidence": (
                "adversarial local review, then a newly frozen development case; all existing position cases are now exposed"
                if gate else "repair provider-free role-first contract"
            ),
        },
        "claims": {
            "reviewed_semantics_are_representable": gate,
            "automatic_role_extraction_improved": False,
            "automatic_relation_extraction_improved": False,
            "provider_acceptance_proven": False,
            "production_integration_authorized": False,
        },
        "boundary": {
            "reviewed_semantics_mechanically_projected": True,
            "new_semantic_labels_created": False,
            "deterministic_semantic_gate_added": False,
            "categorical_trajectory_gate_removed": True,
            "fan_in_measured": True,
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
