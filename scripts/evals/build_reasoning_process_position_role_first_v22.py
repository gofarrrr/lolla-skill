#!/usr/bin/env python3
"""Validate the provider-free nested-component role-first v2.2 contract."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_position_role_first_v2 import ROLE_ORDER  # noqa: E402
from engine.system_b.reasoning_process_position_role_first_v22 import (  # noqa: E402
    build_position_relation_packet_v22,
    build_position_relation_prompts_v22,
    build_position_role_packet_v22,
    build_position_role_prompts_v22,
    compile_position_relation_response_v22,
    compile_position_role_response_v22,
    join_position_role_first_v22,
    position_relation_response_schema_v22,
    position_role_response_schema_v22,
    project_parallel_role_response_v22,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _rekey_relation_response(
    *, old_response: dict, old_roles: dict, new_roles: dict
) -> dict:
    old_index = {
        role: {
            item["role_record_id"]: item["source_record_index"]
            for item in old_roles[role]["observations"]
        }
        for role in ROLE_ORDER
    }
    new_ids = {
        role: {
            item["source_record_index"]: item["role_record_id"]
            for item in new_roles[role]["observations"]
        }
        for role in ROLE_ORDER
    }
    records = []
    for record in old_response["records"]:
        updated = dict(record)
        for role in ROLE_ORDER:
            field = f"{role}_role_record_id"
            old_id = record[field]
            updated[field] = new_ids[role][old_index[role][old_id]] if old_id else ""
        records.append(updated)
    return {
        "status": old_response["status"],
        "records": records,
        "global_limitations": old_response["global_limitations"],
    }


def build(output: Path) -> dict:
    v2_report = _load(
        ROOT / "research/reasoning-process-position-role-first-v2-2026-07-12/report.json"
    )
    cases = []
    for artifact in v2_report["artifacts"]:
        fixture = _load(ROOT / artifact["fixture_path"])
        cases.append(
            {
                "case_id": fixture["case_id"],
                "packet_path": fixture["source"]["packet_path"],
                "role_responses": fixture["role_responses"],
                "old_roles": fixture["role_compiled"],
                "relation_response": fixture["relation_response"],
            }
        )
    for relative_root in (
        "research/reasoning-process-position-role-first-v2-new-case-2026-07-12",
        "research/reasoning-process-position-role-first-v21-new-case-2026-07-12",
    ):
        case_root = ROOT / relative_root
        target = _load(case_root / "source-review-target.json")
        compiled = _load(case_root / "compiled-source-review-target.json")
        cases.append(
            {
                "case_id": target["case_id"],
                "packet_path": str((case_root / "position-endpoint.json").relative_to(ROOT)),
                "role_responses": target["role_responses"],
                "old_roles": compiled["role_compiled"],
                "relation_response": compiled["relation_response"],
            }
        )

    artifacts = []
    complete = role_admitted = relation_admitted = quarantine = 0
    max_prompt_bytes = 0
    for case in cases:
        wrapper = _load(ROOT / case["packet_path"])
        roles = {}
        projected_responses = {}
        for role in ROLE_ORDER:
            packet = build_position_role_packet_v22(wrapper=wrapper, role=role)
            response = project_parallel_role_response_v22(case["role_responses"][role])
            projected_responses[role] = response
            prompts = build_position_role_prompts_v22(packet)
            max_prompt_bytes = max(
                max_prompt_bytes, len(prompts["user_prompt"].encode("utf-8"))
            )
            roles[role] = compile_position_role_response_v22(
                response=response,
                packet=packet,
                producer_kind="source_reviewer",
                producer_id="v22-provider-free-reviewed-target-projection",
            )
            role_admitted += len(roles[role]["observations"])
            quarantine += sum(
                item["terminal_state"] == "quarantined" for item in roles[role]["records"]
            )
        relation_packet = build_position_relation_packet_v22(
            role_compiled_by_role=roles
        )
        relation_response = _rekey_relation_response(
            old_response=case["relation_response"],
            old_roles=case["old_roles"],
            new_roles=roles,
        )
        relation_prompts = build_position_relation_prompts_v22(relation_packet)
        max_prompt_bytes = max(
            max_prompt_bytes, len(relation_prompts["user_prompt"].encode("utf-8"))
        )
        relation = compile_position_relation_response_v22(
            response=relation_response,
            packet=relation_packet,
            producer_kind="source_reviewer",
            producer_id="v22-provider-free-reviewed-target-projection",
        )
        relation_admitted += len(relation["observations"])
        quarantine += sum(
            item["terminal_state"] == "quarantined" for item in relation["records"]
        )
        joined = join_position_role_first_v22(
            role_compiled_by_role=roles,
            relation_compiled=relation,
        )
        complete += joined["status"] == "position_role_first_join_complete"
        fixture = {
            "schema_version": "lolla.reasoning_process_position_role_first_v22_fixture.v1",
            "case_id": case["case_id"],
            "packet_path": case["packet_path"],
            "role_responses": projected_responses,
            "role_compiled": roles,
            "relation_packet": relation_packet,
            "relation_response": relation_response,
            "relation_compiled": relation,
            "joined": joined,
        }
        fixture_path = output / "fixtures" / f"{case['case_id']}.json"
        _write(fixture_path, fixture)
        artifacts.append(
            {
                "case_id": case["case_id"],
                "fixture_path": str(fixture_path.relative_to(ROOT)),
                "join_status": joined["status"],
            }
        )
    schema_inventory = {
        role: schema_metrics(position_role_response_schema_v22(role))
        for role in ROLE_ORDER
    }
    relation_metrics = schema_metrics(position_relation_response_schema_v22())
    max_role_schema_bytes = max(item["bytes"] for item in schema_inventory.values())
    max_role_schema_depth = max(item["depth"] for item in schema_inventory.values())
    gate = (
        len(cases) == 10
        and complete == 10
        and role_admitted == 30
        and relation_admitted == 10
        and quarantine == 0
        and max_role_schema_bytes <= 2600
        and max_role_schema_depth <= 11
        and max_prompt_bytes <= 5700
    )
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_v22_report.v1",
        "status": "provider_free_position_role_first_v22_pass" if gate else "provider_free_position_role_first_v22_fail",
        "date": "2026-07-12",
        "artifacts": artifacts,
        "schema_inventory": {**schema_inventory, "relation": relation_metrics},
        "summary": {
            "reviewed_case_count": len(cases),
            "complete_join_count": complete,
            "admitted_role_record_count": role_admitted,
            "admitted_relation_record_count": relation_admitted,
            "quarantined_record_count": quarantine,
            "maximum_role_schema_bytes": max_role_schema_bytes,
            "maximum_role_schema_depth": max_role_schema_depth,
            "maximum_user_prompt_utf8_bytes": max_prompt_bytes,
            "maximum_provider_calls_per_case": 4,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0
        },
        "change": {
            "parallel_component_columns_removed": True,
            "nested_atomic_component_array_added": True,
            "semantic_contract_changed_from_v21": False,
            "relation_contract_changed_from_v21": False,
            "deterministic_semantic_gate_added": False
        },
        "decision": {
            "provider_free_contract_gate": "pass" if gate else "fail",
            "provider_probe_authorized": False,
            "next_required_evidence": "adversarial nested-component review, then a newly frozen ambiguous case"
        },
        "claims": {
            "parallel_alignment_failure_removed_by_construction": gate,
            "automatic_semantic_extraction_improved": False,
            "provider_acceptance_proven": False,
            "production_integration_authorized": False
        }
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
