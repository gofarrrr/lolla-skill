#!/usr/bin/env python3
"""Run the frozen four-call chronological-shard representative batch."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evals.build_reasoning_process_chronological_shard_family_batch import validate  # noqa: E402
from scripts.evals.run_conversation_state_microtask_probe import _load_env  # noqa: E402
from scripts.evals.run_reasoning_process_phase4_transfer import _load, _sha, _write, run_job  # noqa: E402


def validate_authorization(value: dict, *, contract: dict, contract_path: Path) -> None:
    expected = {
        "schema_version": "lolla.reasoning_process_chronological_shard_family_batch_authorization.v1",
        "status": "authorized_once_under_founder_continuation_mandate",
        "contract_path": str(contract_path.relative_to(ROOT)),
        "contract_sha256": _sha(contract_path),
        "run_id": contract["run_id"],
        "maximum_provider_calls": 4,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
    }
    if value != expected:
        raise RuntimeError("family-batch authorization drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = _load(contract_path)
    validation = validate(contract)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise RuntimeError("execution arguments are missing")
    validate_authorization(_load(args.authorization.resolve()), contract=contract, contract_path=contract_path)
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("family-batch output already exists")
    _load_env(args.env_file.resolve())
    snapshot = _load(ROOT / "docs/evals/reasoning-process-phase3-model-snapshot-v1.json")
    calls = []
    cost = 0.0
    for job in contract["jobs"]:
        call = run_job(contract=contract, job=job, snapshot=snapshot)
        calls.append(call)
        _write(output / "calls" / f"{job['job_id']}.json", call)
        if isinstance(call.get("estimated_cost_usd"), (int, float)):
            cost += float(call["estimated_cost_usd"])
        if call["operational_status"] == "missing_api_key" or cost > contract["budget"]["maximum_estimated_cost_usd"]:
            break
    result = {
        "schema_version": "lolla.reasoning_process_chronological_shard_family_batch_result.v1",
        "status": "representative_batch_preserved" if len(calls) == 4 else "representative_batch_stopped",
        "run_id": contract["run_id"],
        "expected_call_count": 4,
        "attempted_job_count": len(calls),
        "provider_request_count": sum(call.get("provider_calls", 0) for call in calls),
        "operational_success_count": sum(call["operational_status"] == "ok" for call in calls),
        "typed_admission_count": sum(call["typed_status"] in {"admitted", "admitted_with_quarantine"} for call in calls),
        "admitted_record_count": sum(call.get("admitted_record_count", 0) for call in calls),
        "quarantined_record_count": sum(call.get("quarantined_record_count", 0) for call in calls),
        "estimated_cost_usd": round(cost, 9),
        "semantic_review_status": "pending_source_first_review",
        "calls": {"automatic_retries": 0, "semantic_retries": 0, "fallback_models": 0, "evaluator": 0, "embedding": 0, "graph": 0, "pipeline": 0, "runtime": 0},
        "boundary": contract["boundary"],
    }
    _write(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
