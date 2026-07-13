#!/usr/bin/env python3
"""Build provider-free modal-force v3 prompts, fixtures, and fresh-case selection."""
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

from engine.system_b.reasoning_process_chronological_shard_reader_v3 import (  # noqa: E402
    build_shard_prompts_v3,
    compile_shard_response_recordwise_v3,
    shard_response_schema_v3,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402

FRESH_POSITION_CANDIDATES = (
    "amb1-case03-creative-partnership",
    "amb1-case04-research-tool-release",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(output: Path) -> dict[str, Any]:
    v2 = _load(
        ROOT / "research/reasoning-process-chronological-shard-role-explicit-v2-2026-07-12/report.json"
    )
    force_contract = _load(
        ROOT / "docs/evals/reasoning-process-position-force-fixtures-v1.json"
    )
    force_by_case = {item["case_id"]: item for item in force_contract["fixtures"]}
    packet_count = fixture_count = admitted = quarantined = 0
    max_prompt = max_schema_bytes = max_schema_depth = 0
    non_position_schema_unchanged = True
    non_position_prompt_unchanged = True
    position_schema_changed = True
    position_prompt_changed = True
    cases = []
    for case in v2["cases"]:
        artifacts = []
        for artifact in case["artifacts"]:
            wrapper = _load(ROOT / artifact["packet_path"])
            view = artifact["view_kind"]
            prompts = build_shard_prompts_v3(wrapper)
            schema = shard_response_schema_v3(view)
            schema_sha = sha256_bytes(canonical_json_bytes(schema))
            prior_manifest = _load(ROOT / artifact["prompt_manifest_path"])
            if view == "position_and_decision_trajectory":
                position_schema_changed &= schema_sha != prior_manifest["response_schema_sha256"]
                position_prompt_changed &= prompts["user_prompt_sha256"] != prior_manifest["user_prompt_sha256"]
            else:
                non_position_schema_unchanged &= schema_sha == prior_manifest["response_schema_sha256"]
                non_position_prompt_unchanged &= (
                    prompts["system_prompt_sha256"] == prior_manifest["system_prompt_sha256"]
                    and prompts["user_prompt_sha256"] == prior_manifest["user_prompt_sha256"]
                )
            metrics = schema_metrics(schema)
            manifest = {
                "case_id": case["case_id"],
                "view_kind": view,
                "shard_id": wrapper["packet"]["shard_id"],
                "packet_path": artifact["packet_path"],
                "packet_sha256": hashlib.sha256((ROOT / artifact["packet_path"]).read_bytes()).hexdigest(),
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
                "user_prompt_utf8_bytes": len(prompts["user_prompt"].encode("utf-8")),
                "response_schema_sha256": schema_sha,
                "response_schema_metrics": metrics,
                "question_is_last_prompt_section": prompts["user_prompt"].rfind("Question:")
                > prompts["user_prompt"].rfind("contract:"),
            }
            manifest_path = output / "prompt-manifests" / case["case_id"] / f"{wrapper['packet']['shard_id']}.json"
            _write(manifest_path, manifest)
            packet_count += 1
            max_prompt = max(max_prompt, manifest["user_prompt_utf8_bytes"])
            max_schema_bytes = max(max_schema_bytes, metrics["bytes"])
            max_schema_depth = max(max_schema_depth, metrics["depth"])
            fixture_path = None
            if artifact["protected_fixture_path"]:
                previous_fixture = _load(ROOT / artifact["protected_fixture_path"])
                response = copy.deepcopy(previous_fixture["response"])
                if view == "position_and_decision_trajectory":
                    force = force_by_case[case["case_id"]]
                    for record in response["records"]:
                        if force.get("v3_trajectory_interpretation_override"):
                            record["trajectory_interpretation"] = force[
                                "v3_trajectory_interpretation_override"
                            ]
                        record["starting_position_force"] = force["starting_position_force"]
                        record["current_position_force"] = force["current_position_force"]
                        record["qualification_modalities"] = force["qualification_modalities"]
                        record["strength_fidelity_note"] = force["strength_fidelity_note"]
                compiled = compile_shard_response_recordwise_v3(
                    response=response,
                    wrapper=wrapper,
                    producer_kind="source_reviewer",
                    producer_id="modal-strength-v3-projection-of-reviewed-v2-fixture",
                    record_identity=previous_fixture["target"]["target_id"],
                )
                fixture_path = output / "protected-fixtures" / case["case_id"] / f"{view}.json"
                _write(
                    fixture_path,
                    {
                        "target": previous_fixture["target"],
                        "force_fixture": force_by_case.get(case["case_id"]) if view == "position_and_decision_trajectory" else None,
                        "response": response,
                        "compiled": compiled,
                    },
                )
                fixture_count += 1
                admitted += sum(item["terminal_state"] == "admitted" for item in compiled["records"])
                quarantined += sum(item["terminal_state"] == "quarantined" for item in compiled["records"])
            artifacts.append(
                {
                    "view_kind": view,
                    "shard_id": wrapper["packet"]["shard_id"],
                    "packet_path": artifact["packet_path"],
                    "prompt_manifest_path": str(manifest_path.relative_to(ROOT)),
                    "protected_fixture_path": str(fixture_path.relative_to(ROOT)) if fixture_path else None,
                }
            )
        cases.append({"case_id": case["case_id"], "artifacts": artifacts})
    ranked = sorted(
        (
            {"case_id": case_id, "selection_sha256": hashlib.sha256(case_id.encode()).hexdigest()}
            for case_id in FRESH_POSITION_CANDIDATES
        ),
        key=lambda item: item["selection_sha256"],
    )
    report = {
        "schema_version": "lolla.reasoning_process_modal_strength_v3_report.v1",
        "status": "provider_free_modal_strength_interface_pass",
        "date": "2026-07-12",
        "cases": cases,
        "fresh_case_selection": {
            "rule": "ascending_sha256_of_case_id_take_first",
            "excluded_completed_position_cases": [
                "amb1-case01-product-scope",
                "amb1-case02-nonprofit-scale",
                "amb1-case05-family-archive"
            ],
            "eligible_case_ranking": ranked,
            "selected_case_id": ranked[0]["case_id"],
            "selection_was_semantic": False,
        },
        "summary": {
            "packet_and_prompt_count": packet_count,
            "protected_fixture_count": fixture_count,
            "protected_admitted_record_count": admitted,
            "protected_quarantined_record_count": quarantined,
            "maximum_user_prompt_utf8_bytes": max_prompt,
            "maximum_response_schema_bytes": max_schema_bytes,
            "maximum_response_schema_depth": max_schema_depth,
            "non_position_schema_unchanged": non_position_schema_unchanged,
            "non_position_prompt_unchanged": non_position_prompt_unchanged,
            "position_schema_changed": position_schema_changed,
            "position_prompt_changed": position_prompt_changed,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "provider_free_modal_strength_gate": (
                "pass"
                if fixture_count == 20
                and admitted == 20
                and quarantined == 0
                and non_position_schema_unchanged
                and non_position_prompt_unchanged
                and position_schema_changed
                and position_prompt_changed
                else "fail"
            ),
            "adversarial_review_authorized": True,
            "provider_probe_authorized": False,
        },
        "boundary": {
            "force_labels_are_scores_or_ordinals": False,
            "deterministic_force_label_inference": False,
            "deterministic_force_label_comparison": False,
            "prose_keyword_gate_added": False,
            "completed_case05_prompt_changed": False,
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
    print(json.dumps({"summary": report["summary"], "selection": report["fresh_case_selection"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
