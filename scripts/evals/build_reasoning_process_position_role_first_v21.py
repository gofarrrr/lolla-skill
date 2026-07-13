#!/usr/bin/env python3
"""Validate the provider-free role-first v2.1 prompt/packet amendment."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_position_role_first_v2 import (  # noqa: E402
    ROLE_ORDER,
    position_relation_response_schema_v2,
    position_role_response_schema_v2,
)
from engine.system_b.reasoning_process_position_role_first_v21 import (  # noqa: E402
    build_position_relation_packet_v21,
    build_position_relation_prompts_v21,
    build_position_role_packet_v21,
    build_position_role_prompts_v21,
    compile_position_relation_response_v21,
    compile_position_role_response_v21,
    join_position_role_first_v21,
    position_relation_response_schema_v21,
    position_role_response_schema_v21,
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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
                "relation_response": fixture["relation_response"],
            }
        )
    new_root = ROOT / "research/reasoning-process-position-role-first-v2-new-case-2026-07-12"
    new_target = _load(new_root / "source-review-target.json")
    new_compiled = _load(new_root / "compiled-source-review-target.json")
    cases.append(
        {
            "case_id": new_target["case_id"],
            "packet_path": str((new_root / "position-endpoint.json").relative_to(ROOT)),
            "role_responses": new_target["role_responses"],
            "relation_response": new_compiled["relation_response"],
        }
    )

    manifests = []
    complete = role_admitted = relation_admitted = quarantine = 0
    max_prompt_bytes = 0
    for case in cases:
        wrapper = _load(ROOT / case["packet_path"])
        roles = {}
        role_manifests = {}
        for role in ROLE_ORDER:
            packet = build_position_role_packet_v21(wrapper=wrapper, role=role)
            prompts = build_position_role_prompts_v21(packet)
            compiled = compile_position_role_response_v21(
                response=case["role_responses"][role],
                packet=packet,
                producer_kind="source_reviewer",
                producer_id="v21-provider-free-reviewed-target-replay",
            )
            roles[role] = compiled
            role_manifests[role] = {
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
                "user_prompt_utf8_bytes": len(prompts["user_prompt"].encode("utf-8")),
            }
            max_prompt_bytes = max(
                max_prompt_bytes, role_manifests[role]["user_prompt_utf8_bytes"]
            )
            role_admitted += len(compiled["observations"])
            quarantine += sum(
                item["terminal_state"] == "quarantined" for item in compiled["records"]
            )
        relation_packet = build_position_relation_packet_v21(
            role_compiled_by_role=roles
        )
        relation_prompts = build_position_relation_prompts_v21(relation_packet)
        relation = compile_position_relation_response_v21(
            response=case["relation_response"],
            packet=relation_packet,
            producer_kind="source_reviewer",
            producer_id="v21-provider-free-reviewed-target-replay",
        )
        joined = join_position_role_first_v21(
            role_compiled_by_role=roles,
            relation_compiled=relation,
        )
        complete += joined["status"] == "position_role_first_join_complete"
        relation_admitted += len(relation["observations"])
        quarantine += sum(
            item["terminal_state"] == "quarantined" for item in relation["records"]
        )
        relation_bytes = len(relation_prompts["user_prompt"].encode("utf-8"))
        max_prompt_bytes = max(max_prompt_bytes, relation_bytes)
        manifests.append(
            {
                "case_id": case["case_id"],
                "packet_path": case["packet_path"],
                "roles": role_manifests,
                "relation": {
                    "system_prompt_sha256": relation_prompts["system_prompt_sha256"],
                    "user_prompt_sha256": relation_prompts["user_prompt_sha256"],
                    "user_prompt_utf8_bytes": relation_bytes,
                },
                "join_status": joined["status"],
            }
        )
    schemas_unchanged = all(
        position_role_response_schema_v21(role) == position_role_response_schema_v2(role)
        for role in ROLE_ORDER
    ) and position_relation_response_schema_v21() == position_relation_response_schema_v2()
    gate = (
        len(cases) == 9
        and complete == 9
        and role_admitted == 27
        and relation_admitted == 9
        and quarantine == 0
        and schemas_unchanged
        and max_prompt_bytes <= 5500
    )
    report = {
        "schema_version": "lolla.reasoning_process_position_role_first_v21_report.v1",
        "status": "provider_free_position_role_first_v21_pass" if gate else "provider_free_position_role_first_v21_fail",
        "date": "2026-07-12",
        "manifests": manifests,
        "summary": {
            "reviewed_case_count": len(cases),
            "complete_join_count": complete,
            "admitted_role_record_count": role_admitted,
            "admitted_relation_record_count": relation_admitted,
            "quarantined_record_count": quarantine,
            "response_schemas_byte_identical_to_v2": schemas_unchanged,
            "maximum_user_prompt_utf8_bytes": max_prompt_bytes,
            "maximum_provider_calls_per_case": 4,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "clarifications": {
            "starting_is_earliest_visible_endpoint": True,
            "one_record_is_one_coherent_position_thread": True,
            "distinct_objects_are_aligned_components_not_records": True,
            "all_focal_aliases_reviewed_before_valid_empty": True,
            "assistant_pressure_preserves_speaker_ownership_without_implying_user_adoption": True,
            "relationship_records_are_thread_based_not_array_order_based": True,
        },
        "decision": {
            "provider_free_contract_gate": "pass" if gate else "fail",
            "provider_probe_authorized": False,
            "next_required_evidence": "new pre-frozen ambiguous multi-turn case after adversarial prompt review",
        },
        "claims": {
            "contract_ambiguities_removed_from_visible_prompt": gate,
            "automatic_extraction_improved": False,
            "provider_acceptance_proven": False,
            "production_integration_authorized": False,
        },
        "boundary": {
            "response_schema_changed": False,
            "validator_changed": False,
            "deterministic_semantic_gate_added": False,
            "provider_calls": 0,
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
