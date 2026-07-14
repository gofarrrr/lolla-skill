#!/usr/bin/env python3
"""Build the quiet-library v3 mechanism packet without provider calls."""
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

from engine.system_b.reasoning_pattern_role_record_interpreter_v3 import (
    build_input_v3,
    build_prompts_v3,
    response_schema_v2,
)
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes


ROLE_RESULT = ROOT / "research/independent-quiet-library-v242-role-probe-2026-07-12/result.json"
ROLE_REVIEW = ROOT / "research/independent-quiet-library-v242-role-probe-2026-07-12/source-review.json"
CASE_ID = "phase5-independent-quiet-library-laptop-pilot"
ARM_ID = "independent_quiet_library_provider"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def report_path(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def build(output: Path) -> dict[str, Any]:
    role_result = load(ROLE_RESULT)
    if role_result.get("evaluation", {}).get("status") != "quiet_role_gates_pass_source_review_required":
        raise ValueError("quiet role result did not pass mechanical gates")
    review = load(ROLE_REVIEW)
    if review.get("decision", {}).get("mechanism_stage_authorized_with_caveat_preserved") is not True:
        raise ValueError("quiet role source review did not authorize mechanism stage")
    refs = [
        {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
        for path in (ROLE_RESULT, ROLE_REVIEW)
    ]
    packet = build_input_v3(
        case_id=CASE_ID,
        arm_id=ARM_ID,
        joined=role_result["joined"],
        source_refs=refs,
    )
    prompts = build_prompts_v3(packet)
    packet_path = output / "packet.json"
    write(packet_path, packet)
    report = {
        "schema_version": "lolla.independent_quiet_library_mechanism_packet_report.v1",
        "status": "provider_free_quiet_mechanism_packet_pass",
        "case_id": CASE_ID,
        "arm_id": ARM_ID,
        "packet_path": report_path(packet_path),
        "packet_sha256": sha(packet_path),
        "system_prompt_sha256": prompts["system_prompt_sha256"],
        "user_prompt_sha256": prompts["user_prompt_sha256"],
        "user_prompt_utf8_bytes": len(prompts["user_prompt"].encode()),
        "response_schema_sha256": sha256_bytes(canonical_json_bytes(response_schema_v2())),
        "response_schema_metrics": schema_metrics(response_schema_v2()),
        "provider_calls": 0,
        "expected_routing_projection": "empty_if_no_unresolved_mechanism_is_observed",
        "boundary": {
            "negative_review_is_not_deterministic_veto": True,
            "source_target_excluded_from_provider": True,
            "deterministic_semantic_mapping": False,
            "graph_runtime_effect": "none",
        },
    }
    write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps({"status": report["status"], "prompt_bytes": report["user_prompt_utf8_bytes"], "provider_calls": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
