#!/usr/bin/env python3
"""Build provider-free v4.2 wire-only manifests and fixture replay."""
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
    shard_response_schema_v41,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v42 import (  # noqa: E402
    build_shard_prompts_v42,
    compile_shard_response_recordwise_v42,
    shard_response_schema_v42,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402

CLOSED_POSITION_CASES = (
    "amb1-case01-product-scope",
    "amb1-case02-nonprofit-scale",
    "amb1-case03-creative-partnership",
    "amb1-case04-research-tool-release",
    "amb1-case05-family-archive",
    "amb2-case01-career-transition",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _strip_unique_items(value: object) -> int:
    removed = 0
    if isinstance(value, dict):
        if "uniqueItems" in value:
            value.pop("uniqueItems")
            removed += 1
        for child in value.values():
            removed += _strip_unique_items(child)
    elif isinstance(value, list):
        for child in value:
            removed += _strip_unique_items(child)
    return removed


def _manifest(*, wrapper: dict[str, Any], packet_path: str) -> dict[str, Any]:
    view = wrapper["packet"]["view_kind"]
    prompts = build_shard_prompts_v42(wrapper)
    schema = shard_response_schema_v42(view)
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
        "response_schema_metrics": schema_metrics(schema),
        "question_is_last_prompt_section": prompts["user_prompt"].rfind("Question:")
        > prompts["user_prompt"].rfind("contract:"),
    }


def build(output: Path) -> dict[str, Any]:
    v41 = _load(ROOT / "research/reasoning-process-stance-object-v41-2026-07-12/report.json")
    preflight_path = (
        ROOT / "research/reasoning-process-stance-object-v42-2026-07-12/google-schema-preflight.json"
    )
    preflight = _load(preflight_path)
    prompt_count = fixture_count = admitted = quarantined = 0
    all_prompts_unchanged = True
    non_position_schemas_unchanged = True
    position_schema_wire_only_change = True
    artifacts = []
    sources = [
        *(artifact for case in v41["legacy_cases"] for artifact in case["artifacts"]),
        *v41["fresh_cases"],
    ]
    for artifact in sources:
        wrapper = _load(ROOT / artifact["packet_path"])
        view = wrapper["packet"]["view_kind"]
        manifest = _manifest(wrapper=wrapper, packet_path=artifact["packet_path"])
        previous_manifest = _load(ROOT / artifact["prompt_manifest_path"])
        all_prompts_unchanged &= (
            manifest["system_prompt_sha256"] == previous_manifest["system_prompt_sha256"]
            and manifest["user_prompt_sha256"] == previous_manifest["user_prompt_sha256"]
            and build_shard_prompts_v42(wrapper) == build_shard_prompts_v41(wrapper)
        )
        v41_schema = shard_response_schema_v41(view)
        v42_schema = shard_response_schema_v42(view)
        if view == "position_and_decision_trajectory":
            projected = copy.deepcopy(v41_schema)
            removed = _strip_unique_items(projected)
            position_schema_wire_only_change &= removed == 3 and projected == v42_schema
        else:
            non_position_schemas_unchanged &= v41_schema == v42_schema
        manifest_path = output / "prompt-manifests" / f"{wrapper['packet']['shard_id']}.json"
        _write(manifest_path, manifest)
        prompt_count += 1
        fixture_path = None
        if artifact["protected_fixture_path"]:
            previous_fixture = _load(ROOT / artifact["protected_fixture_path"])
            compiled = compile_shard_response_recordwise_v42(
                response=previous_fixture["response"],
                wrapper=wrapper,
                producer_kind="source_reviewer",
                producer_id="v42-wire-only-replay-of-v41-reviewed-fixture",
                record_identity=(
                    previous_fixture.get("target", {}).get("target_id")
                    or previous_fixture.get("target_id")
                    or wrapper["packet"]["case_id"]
                ),
            )
            fixture_path = output / "protected-fixtures" / f"{wrapper['packet']['shard_id']}.json"
            _write(
                fixture_path,
                {
                    "response": previous_fixture["response"],
                    "compiled": compiled,
                    "source_fixture_path": artifact["protected_fixture_path"],
                },
            )
            fixture_count += 1
            admitted += sum(item["terminal_state"] == "admitted" for item in compiled["records"])
            quarantined += sum(item["terminal_state"] == "quarantined" for item in compiled["records"])
        artifacts.append(
            {
                "case_id": wrapper["packet"]["case_id"],
                "view_kind": view,
                "packet_path": artifact["packet_path"],
                "prompt_manifest_path": str(manifest_path.relative_to(ROOT)),
                "protected_fixture_path": str(fixture_path.relative_to(ROOT))
                if fixture_path
                else None,
            }
        )
    reserved = [
        item
        for item in v41["fresh_case_selection"]["eligible_case_ranking"]
        if item["case_id"] != "amb2-case01-career-transition"
    ]
    reserved.sort(key=lambda item: item["selection_sha256"])
    position_metrics = schema_metrics(
        shard_response_schema_v42("position_and_decision_trajectory")
    )
    gate = (
        prompt_count == 63
        and fixture_count == 23
        and admitted == 23
        and quarantined == 0
        and all_prompts_unchanged
        and non_position_schemas_unchanged
        and position_schema_wire_only_change
        and preflight["status"] == "pass"
        and preflight["v42"]["native_schema_status"] == "pass"
    )
    report = {
        "schema_version": "lolla.reasoning_process_stance_object_v42_report.v1",
        "status": "provider_free_stance_object_v42_pass" if gate else "provider_free_stance_object_v42_fail",
        "date": "2026-07-12",
        "artifacts": artifacts,
        "reserved_case_selection": {
            "rule": "remove_closed_career_case_then_ascending_existing_frozen_sha256_ranking",
            "excluded_closed_position_cases": list(CLOSED_POSITION_CASES),
            "eligible_case_ranking": reserved,
            "selected_case_id": reserved[0]["case_id"],
            "selection_was_semantic": False,
        },
        "summary": {
            "prompt_count": prompt_count,
            "protected_fixture_count": fixture_count,
            "protected_admitted_record_count": admitted,
            "protected_quarantined_record_count": quarantined,
            "all_prompts_byte_identical_to_v41": all_prompts_unchanged,
            "all_non_position_schemas_byte_identical_to_v41": non_position_schemas_unchanged,
            "position_schema_change_is_only_three_unique_items_removals": position_schema_wire_only_change,
            "position_response_schema_bytes": position_metrics["bytes"],
            "position_response_schema_depth": position_metrics["depth"],
            "google_sdk_native_schema_status": preflight["v42"]["native_schema_status"],
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "provider_free_stance_object_v42_gate": "pass" if gate else "fail",
            "google_sdk_preflight_gate": "pass" if preflight["status"] == "pass" else "fail",
            "adversarial_review_authorized": gate,
            "provider_probe_authorized": False,
        },
        "boundary": {
            "semantic_contract_changed": False,
            "prompt_changed": False,
            "record_validator_changed": False,
            "deterministic_duplicate_validation_retained": True,
            "provider_wire_unique_items_removed": 3,
            "semantic_case_selection": False,
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
    print(json.dumps({"selection": report["reserved_case_selection"], "summary": report["summary"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
