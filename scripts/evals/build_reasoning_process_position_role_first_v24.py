#!/usr/bin/env python3
"""Validate provider-free paired current/qualification role-first v2.4."""
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
from engine.system_b.reasoning_process_position_role_first_v24 import (  # noqa: E402
    build_position_current_qualification_packet_v24,
    build_position_current_qualification_prompts_v24,
    build_position_relation_packet_v24, build_position_relation_prompts_v24,
    build_position_starting_packet_v24, build_position_starting_prompts_v24,
    compile_position_current_qualification_response_v24,
    compile_position_relation_response_v24, compile_position_starting_response_v24,
    join_position_role_first_v24, position_current_qualification_response_schema_v24,
    position_relation_response_schema_v24, position_starting_response_schema_v24,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _paired(current: dict, qualification: dict) -> dict:
    return {
        "current_status": current["status"], "qualification_status": qualification["status"],
        "records": [*current["records"], *qualification["records"]],
        "allocation_note": "Source reviewer allocated current and qualification comparatively; shared aliases are allowed only for distinct meanings.",
        "global_limitations": "Source-reviewed prospective target; other valid allocations may exist.",
    }


def _rekey(old_response: dict, old_roles: dict, new_roles: dict) -> dict:
    old_index = {role: {item["role_record_id"]: item["source_record_index"] for item in old_roles[role]["observations"]} for role in ROLE_ORDER}
    new_ids = {role: {item["source_record_index"]: item["role_record_id"] for item in new_roles[role]["observations"]} for role in ROLE_ORDER}
    records = []
    for record in old_response["records"]:
        updated = dict(record)
        for role in ROLE_ORDER:
            field = f"{role}_role_record_id"
            old_id = record[field]
            updated[field] = new_ids[role][old_index[role][old_id]] if old_id else ""
        records.append(updated)
    return {"status": old_response["status"], "records": records, "global_limitations": old_response["global_limitations"]}


def build(output: Path) -> dict:
    v23 = _load(ROOT / "research/reasoning-process-position-role-first-v23-2026-07-12/report.json")
    cases = []
    for artifact in v23["artifacts"]:
        fixture = _load(ROOT / artifact["fixture_path"])
        cases.append({"case_id": fixture["case_id"], "packet_path": fixture["packet_path"], "responses": fixture["role_responses"], "old_roles": fixture["role_compiled"], "relation_response": fixture["relation_response"]})
    museum = ROOT / "research/reasoning-process-position-role-first-v23-new-case-2026-07-12"
    target, compiled = _load(museum / "source-review-target.json"), _load(museum / "compiled-source-review-target.json")
    cases.append({"case_id": target["case_id"], "packet_path": str((museum / "position-endpoint.json").relative_to(ROOT)), "responses": target["role_responses"], "old_roles": compiled["role_compiled"], "relation_response": compiled["relation_response"]})

    artifacts, complete, role_count, relation_count, quarantine, max_prompt = [], 0, 0, 0, 0, 0
    for case in cases:
        wrapper = _load(ROOT / case["packet_path"])
        starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
        starting_prompt = build_position_starting_prompts_v24(starting_packet)["user_prompt"]
        max_prompt = max(max_prompt, len(starting_prompt.encode("utf-8")))
        starting = compile_position_starting_response_v24(response=case["responses"]["starting"], packet=starting_packet, producer_kind="source_reviewer", producer_id="v24-provider-free-reviewed-target")
        paired_packet = build_position_current_qualification_packet_v24(wrapper=wrapper)
        paired_prompt = build_position_current_qualification_prompts_v24(paired_packet)["user_prompt"]
        max_prompt = max(max_prompt, len(paired_prompt.encode("utf-8")))
        paired_response = _paired(case["responses"]["current"], case["responses"]["qualification"])
        paired = compile_position_current_qualification_response_v24(response=paired_response, wrapper=wrapper, producer_kind="source_reviewer", producer_id="v24-provider-free-reviewed-target")
        roles = {"starting": starting, **paired["role_compiled"]}
        role_count += sum(len(value["observations"]) for value in roles.values())
        quarantine += sum(item["terminal_state"] == "quarantined" for value in roles.values() for item in value["records"])
        relation_packet = build_position_relation_packet_v24(role_compiled_by_role=roles)
        relation_response = _rekey(case["relation_response"], case["old_roles"], roles)
        max_prompt = max(max_prompt, len(build_position_relation_prompts_v24(relation_packet)["user_prompt"].encode("utf-8")))
        relation = compile_position_relation_response_v24(response=relation_response, packet=relation_packet, producer_kind="source_reviewer", producer_id="v24-provider-free-reviewed-target")
        relation_count += len(relation["observations"])
        quarantine += sum(item["terminal_state"] == "quarantined" for item in relation["records"])
        joined = join_position_role_first_v24(role_compiled_by_role=roles, relation_compiled=relation)
        complete += joined["status"] == "position_role_first_join_complete"
        fixture = {"schema_version": "lolla.reasoning_process_position_role_first_v24_fixture.v1", "case_id": case["case_id"], "packet_path": case["packet_path"], "starting_response": case["responses"]["starting"], "paired_response": paired_response, "starting_compiled": starting, "paired_compiled": paired, "role_compiled": roles, "relation_packet": relation_packet, "relation_response": relation_response, "relation_compiled": relation, "joined": joined}
        fixture_path = output / "fixtures" / f"{case['case_id']}.json"
        _write(fixture_path, fixture)
        artifacts.append({"case_id": case["case_id"], "fixture_path": str(fixture_path.relative_to(ROOT)), "join_status": joined["status"]})
    schema_inventory = {"starting": schema_metrics(position_starting_response_schema_v24("starting")), "paired": schema_metrics(position_current_qualification_response_schema_v24()), "relation": schema_metrics(position_relation_response_schema_v24())}
    gate = len(cases) == 12 and complete == 12 and role_count == 36 and relation_count == 12 and quarantine == 0 and max_prompt <= 7500 and schema_inventory["paired"]["depth"] <= 11 and schema_inventory["paired"]["bytes"] <= 3000
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_v24_report.v1", "status": "provider_free_position_role_first_v24_pass" if gate else "provider_free_position_role_first_v24_fail", "date": "2026-07-12", "artifacts": artifacts, "schema_inventory": schema_inventory,
        "summary": {"reviewed_case_count": len(cases), "complete_join_count": complete, "admitted_role_record_count": role_count, "admitted_relation_record_count": relation_count, "quarantined_record_count": quarantine, "maximum_user_prompt_utf8_bytes": max_prompt, "maximum_provider_calls_per_case": 3, "provider_calls": 0, "evaluator_calls": 0, "graph_calls": 0, "runtime_calls": 0},
        "change": {"starting_remains_independent": True, "current_and_qualification_paired": True, "relation_remains_exact_id_task": True, "maximum_calls_reduced_from_four_to_three": True, "nested_component_wire_retained": True, "hard_alias_exclusivity_added": False, "deterministic_alias_subtraction_added": False, "deterministic_semantic_gate_added": False, "semantic_score_added": False},
        "decision": {"provider_free_contract_gate": "pass" if gate else "fail", "provider_probe_authorized": False, "next_required_evidence": "adversarial paired-allocation review, then genuinely new source-first case"},
        "claims": {"reviewed_targets_representable_in_paired_contract": gate, "automatic_semantic_allocation_improved": False, "provider_behavior_proven": False, "production_integration_authorized": False},
    }
    _write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps({"status": report["status"], "summary": report["summary"], "schema_inventory": report["schema_inventory"]}, indent=2))
    return 0 if report["decision"]["provider_free_contract_gate"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
