#!/usr/bin/env python3
"""Compile a pre-written source-review target through role-first v2.2."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v2 import ROLE_ORDER  # noqa: E402
from engine.system_b.reasoning_process_position_role_first_v22 import (  # noqa: E402
    build_position_relation_packet_v22,
    build_position_role_packet_v22,
    compile_position_relation_response_v22,
    compile_position_role_response_v22,
    join_position_role_first_v22,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(output: Path) -> dict:
    packet_path = output / "position-endpoint.json"
    target_path = output / "source-review-target.json"
    wrapper, target = _load(packet_path), _load(target_path)
    roles = {}
    for role in ROLE_ORDER:
        packet = build_position_role_packet_v22(wrapper=wrapper, role=role)
        roles[role] = compile_position_role_response_v22(
            response=target["role_responses"][role], packet=packet,
            producer_kind="source_reviewer", producer_id="pre-execution-v22-target",
        )
    relation_packet = build_position_relation_packet_v22(role_compiled_by_role=roles)
    relationship = target["relationship_target"]
    role_ids = {role: {item["source_record_index"]: item["role_record_id"] for item in roles[role]["observations"]} for role in ROLE_ORDER}
    relation_response = {
        "status": relationship["status"],
        "records": [{
            "status": relationship["status"],
            **{f"{role}_role_record_id": role_ids[role][relationship[f"{role}_source_record_index"]] for role in ROLE_ORDER},
            "relationship_interpretation": relationship["relationship_interpretation"],
            "limitations": relationship["limitations"],
        }],
        "global_limitations": "One reviewed endpoint relationship; other valid records may exist.",
    }
    relation = compile_position_relation_response_v22(
        response=relation_response, packet=relation_packet,
        producer_kind="source_reviewer", producer_id="pre-execution-v22-target",
    )
    joined = join_position_role_first_v22(role_compiled_by_role=roles, relation_compiled=relation)
    quarantined = sum(item["terminal_state"] == "quarantined" for compiled in [*roles.values(), relation] for item in compiled["records"])
    gate = all(len(roles[role]["observations"]) == 1 for role in ROLE_ORDER) and len(relation["observations"]) == 1 and quarantined == 0 and joined["status"] == "position_role_first_join_complete"
    fixture = {
        "schema_version": "lolla.reasoning_process_position_role_first_v22_target_fixture.v1",
        "status": "pre_execution_source_review_target_compiled" if gate else "pre_execution_source_review_target_failed",
        "case_id": target["case_id"], "role_compiled": roles, "relation_packet": relation_packet,
        "relation_response": relation_response, "relation_compiled": relation, "joined": joined,
        "source_review_gates": target["source_first_gates"], "protected_target": target["protected_target"], "boundary": target["boundary"],
    }
    fixture_path = output / "compiled-source-review-target.json"
    _write(fixture_path, fixture)
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_v22_target_report.v1",
        "status": "pre_execution_target_gate_pass" if gate else "pre_execution_target_gate_fail",
        "case_id": target["case_id"], "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "target_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(), "compiled_target_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
        "admitted_role_record_count": sum(len(value["observations"]) for value in roles.values()),
        "admitted_relation_record_count": len(relation["observations"]), "quarantined_record_count": quarantined,
        "join_status": joined["status"], "provider_calls": 0, "provider_probe_authorized": False,
    }
    _write(output / "target-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pre_execution_target_gate_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
