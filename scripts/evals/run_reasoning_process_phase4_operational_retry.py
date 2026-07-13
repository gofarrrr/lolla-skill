#!/usr/bin/env python3
"""Run one separately frozen Phase-4 operational completion."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parents[2]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from scripts.evals.run_conversation_state_microtask_probe import _load_env
from scripts.evals.run_reasoning_process_phase4_transfer import (
    ROOT,
    _load,
    _sha,
    _write,
    run_job,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--retry-contract", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    retry = _load(args.retry_contract.resolve())
    if retry.get("schema_version") != "lolla.reasoning_process_phase4_operational_retry_contract.v1":
        raise RuntimeError("unexpected retry contract")
    phase4_path = ROOT / retry["phase4_contract_path"]
    original_path = ROOT / retry["original_call_path"]
    if _sha(phase4_path) != retry["phase4_contract_sha256"] or _sha(original_path) != retry["original_call_sha256"]:
        raise RuntimeError("frozen retry input drifted")
    if time.time() - original_path.stat().st_mtime < retry["minimum_observed_cooldown_seconds"]:
        raise RuntimeError("minimum operational cool-off has not elapsed")
    output = args.output.resolve()
    if output.exists():
        raise RuntimeError("operational retry output already exists")
    contract = _load(phase4_path)
    job = next(item for item in contract["jobs"] if item["job_id"] == retry["job_id"])
    snapshot = _load(ROOT / "docs/evals/reasoning-process-phase3-model-snapshot-v1.json")
    _load_env(args.env_file.resolve())
    call = run_job(contract=contract, job=job, snapshot=snapshot)
    result = {
        "schema_version": "lolla.reasoning_process_phase4_operational_retry_result.v1",
        "status": "operational_completion_preserved",
        "run_id": retry["run_id"],
        "original_call_path": retry["original_call_path"],
        "original_call_sha256": retry["original_call_sha256"],
        "observed_cooldown_seconds": round(time.time() - original_path.stat().st_mtime, 3),
        "call": call,
        "provider_request_count": call.get("provider_calls", 0),
        "automatic_retries": 0,
        "semantic_retries": 0,
        "fallback_models": 0,
        "boundary": retry["boundary"],
    }
    _write(output, result)
    print(json.dumps({key: result[key] for key in ("status", "observed_cooldown_seconds", "provider_request_count")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
