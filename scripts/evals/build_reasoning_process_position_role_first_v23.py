#!/usr/bin/env python3
"""Validate the provider-free role-boundary/expression v2.3 contract."""
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
from engine.system_b.reasoning_process_position_role_first_v23 import (  # noqa: E402
    build_position_relation_packet_v23, build_position_relation_prompts_v23,
    build_position_role_packet_v23, build_position_role_prompts_v23,
    compile_position_relation_response_v23, compile_position_role_response_v23,
    join_position_role_first_v23, position_relation_response_schema_v23,
    position_role_response_schema_v23,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
    v22 = _load(ROOT / "research/reasoning-process-position-role-first-v22-2026-07-12/report.json")
    cases = []
    for artifact in v22["artifacts"]:
        fixture = _load(ROOT / artifact["fixture_path"])
        cases.append({"case_id": fixture["case_id"], "packet_path": fixture["packet_path"], "responses": fixture["role_responses"], "old_roles": fixture["role_compiled"], "relation_response": fixture["relation_response"]})
    cooperative = ROOT / "research/reasoning-process-position-role-first-v22-new-case-2026-07-12"
    target, compiled = _load(cooperative / "source-review-target.json"), _load(cooperative / "compiled-source-review-target.json")
    cases.append({"case_id": target["case_id"], "packet_path": str((cooperative / "position-endpoint.json").relative_to(ROOT)), "responses": target["role_responses"], "old_roles": compiled["role_compiled"], "relation_response": compiled["relation_response"]})

    artifacts, complete, role_count, relation_count, quarantine, max_prompt = [], 0, 0, 0, 0, 0
    for case in cases:
        wrapper, roles = _load(ROOT / case["packet_path"]), {}
        for role in ROLE_ORDER:
            packet = build_position_role_packet_v23(wrapper=wrapper, role=role)
            prompt = build_position_role_prompts_v23(packet)["user_prompt"]
            max_prompt = max(max_prompt, len(prompt.encode("utf-8")))
            roles[role] = compile_position_role_response_v23(response=case["responses"][role], packet=packet, producer_kind="source_reviewer", producer_id="v23-provider-free-reviewed-target")
            role_count += len(roles[role]["observations"])
            quarantine += sum(item["terminal_state"] == "quarantined" for item in roles[role]["records"])
        relation_packet = build_position_relation_packet_v23(role_compiled_by_role=roles)
        relation_response = _rekey(case["relation_response"], case["old_roles"], roles)
        max_prompt = max(max_prompt, len(build_position_relation_prompts_v23(relation_packet)["user_prompt"].encode("utf-8")))
        relation = compile_position_relation_response_v23(response=relation_response, packet=relation_packet, producer_kind="source_reviewer", producer_id="v23-provider-free-reviewed-target")
        relation_count += len(relation["observations"])
        quarantine += sum(item["terminal_state"] == "quarantined" for item in relation["records"])
        joined = join_position_role_first_v23(role_compiled_by_role=roles, relation_compiled=relation)
        complete += joined["status"] == "position_role_first_join_complete"
        fixture = {"schema_version": "lolla.reasoning_process_position_role_first_v23_fixture.v1", "case_id": case["case_id"], "packet_path": case["packet_path"], "role_responses": case["responses"], "role_compiled": roles, "relation_packet": relation_packet, "relation_response": relation_response, "relation_compiled": relation, "joined": joined}
        fixture_path = output / "fixtures" / f"{case['case_id']}.json"
        _write(fixture_path, fixture)
        artifacts.append({"case_id": case["case_id"], "fixture_path": str(fixture_path.relative_to(ROOT)), "join_status": joined["status"]})
    schemas = {role: schema_metrics(position_role_response_schema_v23(role)) for role in ROLE_ORDER}
    gate = len(cases) == 11 and complete == 11 and role_count == 33 and relation_count == 11 and quarantine == 0 and max_prompt <= 7000
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_v23_report.v1",
        "status": "provider_free_position_role_first_v23_pass" if gate else "provider_free_position_role_first_v23_fail",
        "date": "2026-07-12", "artifacts": artifacts,
        "schema_inventory": {**schemas, "relation": schema_metrics(position_relation_response_schema_v23())},
        "summary": {"reviewed_case_count": len(cases), "complete_join_count": complete, "admitted_role_record_count": role_count, "admitted_relation_record_count": relation_count, "quarantined_record_count": quarantine, "maximum_user_prompt_utf8_bytes": max_prompt, "maximum_provider_calls_per_case": 4, "provider_calls": 0, "evaluator_calls": 0, "graph_calls": 0, "runtime_calls": 0},
        "change": {"role_boundary_contract_added": True, "expression_interpretation_contract_added": True, "nested_component_wire_changed_from_v22": False, "response_schema_changed_from_v22": False, "validator_changed_from_v22": False, "deterministic_semantic_gate_added": False, "keyword_or_chronology_gate_added": False},
        "decision": {"provider_free_contract_gate": "pass" if gate else "fail", "provider_probe_authorized": False, "next_required_evidence": "adversarial contract review and genuinely new source-first transfer case"},
        "claims": {"contract_is_more_explicit_about_observed_v22_failures": gate, "automatic_semantic_extraction_improved": False, "provider_behavior_proven": False, "production_integration_authorized": False},
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
