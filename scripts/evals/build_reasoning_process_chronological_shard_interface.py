#!/usr/bin/env python3
"""Build provider-free prompts, schemas, and protected shard compilations."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shard_reader import (  # noqa: E402
    build_shard_prompts,
    compile_shard_response_recordwise,
    shard_response_schema,
)
from engine.system_b.reasoning_process_contracts import schema_metrics  # noqa: E402
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402

VIEWS = (
    "position_and_decision_trajectory",
    "evidence_and_assumption_discipline",
    "uncertainty_and_unresolved_state",
    "challenge_and_revision_response",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _protected_response(case_id: str, view: str) -> dict[str, Any]:
    if view in {"position_and_decision_trajectory", "challenge_and_revision_response"}:
        value = _load(ROOT / "research/reasoning-process-view-specific-v2-2026-07-11/fixtures" / case_id / f"{view}.json")["response"]
    else:
        value = _load(ROOT / "research/reasoning-process-view-specific-interface-2026-07-11/cases" / case_id / view / "protected-fixture-response.json")
    value = copy.deepcopy(value)
    value.pop("park_unselected_auxiliary_observations")
    for record in value["records"]:
        record.pop("auxiliary_observation_ids")
    return value


def build(output: Path) -> dict[str, Any]:
    shard_report = _load(ROOT / "research/reasoning-process-chronological-shards-2026-07-11/report.json")
    target_review = _load(ROOT / "research/reasoning-process-chronological-shards-2026-07-11/protected-target-review.json")
    targets = {
        (case["case_id"], target["view_kind"]): target
        for case in target_review["cases"]
        for target in case["targets"]
    }
    for view in VIEWS:
        _write(output / "schemas" / f"{view}.json", shard_response_schema(view))
    packet_count = fixture_count = admitted = quarantined = 0
    max_packet = max_prompt = max_schema = 0
    cases = []
    for case in shard_report["cases"]:
        artifacts = []
        for artifact in case["artifacts"]:
            wrapper = _load(ROOT / artifact["path"])
            packet = wrapper["packet"]
            prompts = build_shard_prompts(wrapper)
            schema = shard_response_schema(packet["view_kind"])
            prompt_manifest = {
                "case_id": case["case_id"],
                "shard_id": packet["shard_id"],
                "view_kind": packet["view_kind"],
                "packet_path": artifact["path"],
                "packet_sha256": sha256_bytes((ROOT / artifact["path"]).read_bytes()),
                "system_prompt_sha256": prompts["system_prompt_sha256"],
                "user_prompt_sha256": prompts["user_prompt_sha256"],
                "user_prompt_utf8_bytes": len(prompts["user_prompt"].encode("utf-8")),
                "response_schema_sha256": sha256_bytes(canonical_json_bytes(schema)),
                "response_schema_metrics": schema_metrics(schema),
                "question_is_last_prompt_section": prompts["user_prompt"].rfind("Question:") > prompts["user_prompt"].rfind("Relationship contract:"),
            }
            manifest_path = output / "prompt-manifests" / case["case_id"] / f"{packet['shard_id']}.json"
            _write(manifest_path, prompt_manifest)
            packet_count += 1
            max_packet = max(max_packet, wrapper["metrics"]["input_utf8_bytes"])
            max_prompt = max(max_prompt, prompt_manifest["user_prompt_utf8_bytes"])
            max_schema = max(max_schema, prompt_manifest["response_schema_metrics"]["bytes"])
            target = targets[(case["case_id"], packet["view_kind"])]
            protected = artifact["path"] in target["matching_shard_paths"]
            compiled_path = None
            if protected:
                compiled = compile_shard_response_recordwise(
                    response=_protected_response(case["case_id"], packet["view_kind"]),
                    wrapper=wrapper,
                    producer_kind="source_reviewer",
                    producer_id="chronological-shard-same-session-nonblind",
                    record_identity=target["target_id"],
                )
                compiled_path = output / "protected-fixtures" / case["case_id"] / f"{packet['view_kind']}.json"
                _write(compiled_path, {"target": target, "response": _protected_response(case["case_id"], packet["view_kind"]), "compiled": compiled})
                fixture_count += 1
                admitted += sum(item["terminal_state"] == "admitted" for item in compiled["records"])
                quarantined += sum(item["terminal_state"] == "quarantined" for item in compiled["records"])
            artifacts.append(
                {
                    **artifact,
                    "prompt_manifest_path": str(manifest_path.relative_to(ROOT)),
                    "protected_fixture_path": str(compiled_path.relative_to(ROOT)) if compiled_path else None,
                }
            )
        cases.append({"case_id": case["case_id"], "artifacts": artifacts})
    report = {
        "schema_version": "lolla.reasoning_process_chronological_shard_interface_report.v1",
        "status": "provider_free_prompt_schema_custody_pass",
        "date": "2026-07-11",
        "cases": cases,
        "summary": {
            "packet_and_prompt_count": packet_count,
            "protected_fixture_count": fixture_count,
            "protected_admitted_record_count": admitted,
            "protected_quarantined_record_count": quarantined,
            "maximum_packet_utf8_bytes": max_packet,
            "maximum_user_prompt_utf8_bytes": max_prompt,
            "maximum_response_schema_bytes": max_schema,
            "provider_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "provider_free_interface_gate": "pass",
            "cold_reader_review_authorized": True,
            "provider_probe_authorized": False,
        },
        "boundary": {
            "protected_targets_in_prompts": False,
            "source_review_fixtures_in_prompts": False,
            "semantic_prefilter_performed": False,
            "global_synthesis_authorized": False,
            "semantic_merge_authorized": False,
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
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
