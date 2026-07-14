#!/usr/bin/env python3
"""Freeze the four-call representative chronological-shard family batch."""
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

SELECTIONS = (
    ("amb1-case01-product-scope", "evidence_and_assumption_discipline", "shard-01.json"),
    ("amb1-case05-family-archive", "position_and_decision_trajectory", "shard-01.json"),
    ("amb1-case05-family-archive", "uncertainty_and_unresolved_state", "shard-03.json"),
    ("amb1-case05-family-archive", "challenge_and_revision_response", "shard-01.json"),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, Any]:
    interface = _load(ROOT / "research/reasoning-process-chronological-shard-interface-2026-07-11/report.json")
    review = _load(ROOT / "research/reasoning-process-chronological-shards-2026-07-11/protected-target-review.json")
    artifacts = {
        (case["case_id"], artifact["view_kind"], Path(artifact["path"]).name): artifact
        for case in interface["cases"]
        for artifact in case["artifacts"]
    }
    jobs = []
    fixture_locks = []
    for case_id, view_kind, filename in SELECTIONS:
        artifact = artifacts[(case_id, view_kind, filename)]
        manifest = _load(ROOT / artifact["prompt_manifest_path"])
        job_id = f"shard-family-batch-{case_id}-{view_kind}"
        jobs.append(
            {
                "job_id": job_id,
                "case_id": case_id,
                "mechanism": "chronological_shard_v1",
                "view_kind": view_kind,
                "focal_turn_indices": artifact["focal_turn_indices"],
                "packet_path": artifact["path"],
                "packet_sha256": manifest["packet_sha256"],
                "input_utf8_bytes": artifact["input_utf8_bytes"],
                "system_prompt_sha256": manifest["system_prompt_sha256"],
                "user_prompt_sha256": manifest["user_prompt_sha256"],
                "response_schema_sha256": manifest["response_schema_sha256"],
                "maximum_output_records": 2,
            }
        )
        target_case = next(item for item in review["cases"] if item["case_id"] == case_id)
        target = next(item for item in target_case["targets"] if item["view_kind"] == view_kind)
        fixture_locks.append(
            {
                "case_id": case_id,
                "view_kind": view_kind,
                "target_id": target["target_id"],
                "fixture_path": target["fixture_path"],
                "fixture_sha256": _sha(ROOT / target["fixture_path"]),
                "visible_to_model": False,
            }
        )
    frozen = []
    for rel in (
        "engine/system_b/reasoning_process_chronological_shards.py",
        "engine/system_b/reasoning_process_chronological_shard_reader.py",
        "research/reasoning-process-chronological-shard-interface-2026-07-11/report.json",
        "research/reasoning-process-chronological-shard-probe-2026-07-11/result.json",
        "research/reasoning-process-chronological-shard-probe-2026-07-11/source-review.json",
        "docs/evals/reasoning-process-phase3-model-snapshot-v1.json",
    ):
        frozen.append({"path": rel, "sha256": _sha(ROOT / rel)})
    return {
        "schema_version": "lolla.reasoning_process_chronological_shard_family_batch_contract.v1",
        "status": "frozen_before_four_provider_calls",
        "date": "2026-07-11",
        "run_id": "reasoning-process-chronological-shard-family-batch-v1",
        "purpose": "Test every redesigned global family on the smallest shards containing Phase-4 failures before any full nineteen-call case.",
        "jobs": jobs,
        "protected_fixture_locks_for_post_call_review_only": fixture_locks,
        "frozen_inputs": frozen,
        "call_configuration": {
            "provider": "openrouter",
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "model": "google/gemini-3.1-flash-lite",
            "wire_mode": "strict_json_schema",
            "temperature": 0.0,
            "seed": 0,
            "reasoning_enabled": False,
            "full_reader_max_output_tokens": 1200,
            "local_reader_max_output_tokens": 1200,
            "provider_timeout_seconds": 90,
            "require_supported_parameters": True,
            "allow_provider_fallbacks": False,
            "automatic_retries": 0,
            "response_healing": False,
            "parallel_calls": False,
        },
        "budget": {
            "maximum_provider_calls": 4,
            "maximum_estimated_cost_usd": 0.03,
            "automatic_retries": 0,
            "semantic_retries": 0,
            "fallback_models": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "pipeline_calls": 0,
            "runtime_calls": 0,
        },
        "success_requirements": {
            "eventual_operational_completion_rate": 1.0,
            "record_level_custody_rate": 1.0,
            "invalid_admitted_record_count": 0,
            "source_strength_inflation_count": 0,
            "protected_target_visible_rate": 1.0,
            "source_first_review_required": True,
        },
        "stop_rules": [
            "no_prompt_or_schema_repair_after_output",
            "no_semantic_retry",
            "no_full_case_if_any_representative_family_target_fails",
            "no_graph_or_runtime_integration",
        ],
        "boundary": {
            "protected_targets_seen_by_model": False,
            "full_case_calls_authorized": False,
            "semantic_merge_authorized": False,
            "global_synthesis_authorized": False,
            "graph_or_runtime_authorized": False,
        },
    }


def validate(contract: dict[str, Any]) -> dict[str, Any]:
    if contract != build():
        raise RuntimeError("chronological shard family-batch contract drifted")
    if len(contract["jobs"]) != 4:
        raise RuntimeError("family batch must contain four jobs")
    return {"status": "family_batch_contract_valid", "job_count": 4, "provider_calls_made": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.check:
        result = validate(_load(output))
    else:
        contract = build()
        _write(output, contract)
        result = validate(contract)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
