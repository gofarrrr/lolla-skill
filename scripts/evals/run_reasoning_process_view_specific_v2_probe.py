#!/usr/bin/env python3
"""Execute the relationship-explicit v2 probe via Gemini on OpenRouter."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_view_specific_v2 import (
    build_prompts_v2,
    response_schema_v2,
    validate_response_v2,
)
from engine.system_b.reasoning_process_view_specific_v2_compile import (
    compile_response_v2,
)
from scripts.evals import run_reasoning_process_view_specific_probe as base


CONTRACT_SCHEMA = "lolla.reasoning_process_view_specific_v2_probe_contract.v1"
AUTHORIZATION_SCHEMA = "lolla.reasoning_process_view_specific_v2_probe_authorization.v1"
RESULT_SCHEMA = "lolla.reasoning_process_view_specific_v2_probe_result.v1"


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
    metadata = call_metadata or {}
    return compile_response_v2(
        response=response,
        wrapper=wrapper,
        base_ledger=base_ledger,
        catalog=catalog,
        record_identity=str(target["target_id"]),
        producer_kind=producer_kind,
        producer_id=producer_id,
        call_metadata={
            "call_id": metadata.get("call_id", ""),
            "model": metadata.get("model", ""),
            "prompt_sha256": metadata.get("prompt_sha256", ""),
        },
    )


def _activate_v2() -> None:
    base.CONTRACT_SCHEMA = CONTRACT_SCHEMA
    base.AUTHORIZATION_SCHEMA = AUTHORIZATION_SCHEMA
    base.RESULT_SCHEMA = RESULT_SCHEMA
    base.build_view_specific_prompts = build_prompts_v2
    base.view_specific_response_schema = response_schema_v2
    base.validate_view_specific_response = validate_response_v2
    base.compile_protected_fixture = _compile_adapter


def main() -> int:
    _activate_v2()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    contract = base._load(contract_path)
    validation = base.validate_contract(contract)
    if args.dry_run:
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0
    if args.authorization is None or args.env_file is None or args.output is None:
        raise base.ViewSpecificProbeRunnerError(
            "--authorization, --env-file, and --output are required for execution"
        )
    authorization = base._load(args.authorization.resolve())
    base.validate_authorization(
        authorization, contract=contract, contract_path=contract_path
    )
    base._load_env(args.env_file.resolve())
    result = base.execute(contract=contract, output_dir=args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
