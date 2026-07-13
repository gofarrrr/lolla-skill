#!/usr/bin/env python3
"""Compile one pre-written paired v2.4 source-review target."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v24 import (  # noqa: E402
    build_position_relation_packet_v24, build_position_starting_packet_v24,
    compile_position_current_qualification_response_v24,
    compile_position_relation_response_v24, compile_position_starting_response_v24,
    join_position_role_first_v24,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(output: Path) -> dict:
    packet_path, target_path = output / "position-endpoint.json", output / "source-review-target.json"
    wrapper, target = _load(packet_path), _load(target_path)
    starting_packet = build_position_starting_packet_v24(wrapper=wrapper, role="starting")
    starting = compile_position_starting_response_v24(response=target["starting_response"], packet=starting_packet, producer_kind="source_reviewer", producer_id="pre-execution-v24-target")
    paired = compile_position_current_qualification_response_v24(response=target["paired_response"], wrapper=wrapper, producer_kind="source_reviewer", producer_id="pre-execution-v24-target")
    roles = {"starting": starting, **paired["role_compiled"]}
    relation_packet = build_position_relation_packet_v24(role_compiled_by_role=roles)
    relationship = target["relationship_target"]
    ids = {role: {item["source_record_index"]: item["role_record_id"] for item in roles[role]["observations"]} for role in roles}
    relation_response = {"status": "supported", "records": [{"status": "supported", "starting_role_record_id": ids["starting"][1], "current_role_record_id": ids["current"][1], "qualification_role_record_id": ids["qualification"][1], "relationship_interpretation": relationship["relationship_interpretation"], "limitations": relationship["limitations"]}], "global_limitations": "One reviewed endpoint relationship; other valid records may exist."}
    relation = compile_position_relation_response_v24(response=relation_response, packet=relation_packet, producer_kind="source_reviewer", producer_id="pre-execution-v24-target")
    joined = join_position_role_first_v24(role_compiled_by_role=roles, relation_compiled=relation)
    quarantined = sum(item["terminal_state"] == "quarantined" for value in [*roles.values(), relation] for item in value["records"])
    gate = all(len(roles[role]["observations"]) == 1 for role in roles) and len(relation["observations"]) == 1 and quarantined == 0 and joined["status"] == "position_role_first_join_complete"
    fixture = {"schema_version": "lolla.reasoning_process_position_role_first_v24_target_fixture.v1", "status": "pre_execution_source_review_target_compiled" if gate else "pre_execution_source_review_target_failed", "case_id": target["case_id"], "starting_compiled": starting, "paired_compiled": paired, "role_compiled": roles, "relation_packet": relation_packet, "relation_response": relation_response, "relation_compiled": relation, "joined": joined, "source_review_gates": target["source_first_gates"], "protected_target": target["protected_target"], "boundary": target["boundary"]}
    fixture_path = output / "compiled-source-review-target.json"
    _write(fixture_path, fixture)
    report = {"schema_version": "lolla.reasoning_process_position_role_first_v24_target_report.v1", "status": "pre_execution_target_gate_pass" if gate else "pre_execution_target_gate_fail", "case_id": target["case_id"], "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(), "target_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(), "compiled_target_sha256": hashlib.sha256(fixture_path.read_bytes()).hexdigest(), "admitted_role_record_count": sum(len(value["observations"]) for value in roles.values()), "admitted_relation_record_count": len(relation["observations"]), "quarantined_record_count": quarantined, "join_status": joined["status"], "provider_calls": 0, "provider_probe_authorized": False}
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
