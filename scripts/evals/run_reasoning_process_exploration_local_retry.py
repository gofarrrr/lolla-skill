#!/usr/bin/env python3
"""Run one preserved, cooled-off operational retry with record-level custody."""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_exploration_local_custody import (
    compile_local_response_recordwise,
    validate_local_response_envelope,
)
from scripts.evals import run_reasoning_process_view_specific_probe as base
from scripts.evals.run_reasoning_process_exploration_local_probe import (
    _activate,
    _validate_contract,
)


def _compile_adapter(
    *,
    target: Mapping[str, Any],
    response: Mapping[str, Any],
    wrapper: Mapping[str, Any],
    base_ledger: Mapping[str, Any],
    catalog,
    producer_kind: str,
    producer_id: str,
    call_metadata: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    del base_ledger, catalog
    metadata = call_metadata or {}
    return compile_local_response_recordwise(
        response=response,
        wrapper=wrapper,
        producer_kind=producer_kind,
        producer_id=producer_id,
        record_identity=str(target["target_id"]),
        call_metadata={
            "call_id": metadata.get("call_id", ""),
            "model": metadata.get("model", ""),
            "prompt_sha256": metadata.get("prompt_sha256", ""),
        },
    )


def main() -> int:
    _activate()
    base.validate_view_specific_response = validate_local_response_envelope
    base.compile_protected_fixture = _compile_adapter
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = base._load(contract_path)
    validation = _validate_contract(contract)
    original_failure = base._repo_path(
        contract["operational_retry"]["original_failure_path"],
        label="original failure",
    )
    elapsed = time.time() - original_failure.stat().st_mtime
    required = contract["operational_retry"]["minimum_cooloff_seconds"]
    if elapsed < required:
        raise base.ViewSpecificProbeRunnerError("operational retry cool-off not satisfied")
    validation["observed_cooloff_seconds"] = round(elapsed, 3)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise base.ViewSpecificProbeRunnerError("execution arguments are missing")
    authorization = base._load(args.authorization.resolve())
    if authorization.get("contract_sha256") != base._file_sha(contract_path):
        raise base.ViewSpecificProbeRunnerError("authorization contract hash drifted")
    if authorization.get("maximum_provider_calls") != 1:
        raise base.ViewSpecificProbeRunnerError("authorization call ceiling drifted")
    base._load_env(args.env_file.resolve())
    snapshot = base._load(
        base._repo_path(contract["model_snapshot"]["path"], label="model snapshot")
    )
    call = base.run_job(contract=contract, job=contract["jobs"][0], snapshot=snapshot)
    output = args.output.resolve()
    base._write(output / "call.json", call)
    result = {
        "schema_version": "lolla.reasoning_process_exploration_local_retry_result.v1",
        "status": "operational_retry_preserved",
        "run_id": contract["run_id"],
        "original_failure_path": contract["operational_retry"]["original_failure_path"],
        "original_failure_sha256": contract["operational_retry"][
            "original_failure_sha256"
        ],
        "observed_cooloff_seconds": round(elapsed, 3),
        "operational_status": call["operational_status"],
        "typed_status": call["typed_status"],
        "provider_calls": call["provider_calls"],
        "estimated_cost_usd": call.get("estimated_cost_usd"),
        "semantic_review_status": "pending_source_first_review",
        "boundary": {
            "prompt_schema_model_or_packet_changed": False,
            "automatic_retry": False,
            "other_window_repeated": False,
            "phase4_transfer_authorized": False,
        },
    }
    base._write(output / "result.json", result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
