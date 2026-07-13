#!/usr/bin/env python3
"""Validate provider-free status-free paired role-first v2.4.1."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evals import build_reasoning_process_position_role_first_v24 as base  # noqa: E402
from engine.system_b.reasoning_process_position_role_first_v241 import (  # noqa: E402
    build_position_current_qualification_packet_v241,
    build_position_current_qualification_prompts_v241,
    compile_position_current_qualification_response_v241,
    position_current_qualification_response_schema_v241,
)


def _paired(current: dict, qualification: dict) -> dict:
    return {
        "records": [*current["records"], *qualification["records"]],
        "allocation_note": "Source reviewer allocated current and qualification comparatively; shared aliases are allowed only for distinct meanings.",
        "global_limitations": "Source-reviewed prospective target; other valid allocations may exist.",
    }


def build(output: Path) -> dict:
    base.build_position_current_qualification_packet_v24 = build_position_current_qualification_packet_v241
    base.build_position_current_qualification_prompts_v24 = build_position_current_qualification_prompts_v241
    base.compile_position_current_qualification_response_v24 = compile_position_current_qualification_response_v241
    base.position_current_qualification_response_schema_v24 = position_current_qualification_response_schema_v241
    base._paired = _paired
    report = base.build(output)
    passed = report["decision"]["provider_free_contract_gate"] == "pass"
    report["schema_version"] = "lolla.reasoning_process_position_role_first_v241_report.v1"
    report["status"] = "provider_free_position_role_first_v241_pass" if passed else "provider_free_position_role_first_v241_fail"
    report["change"].update({
        "redundant_per_role_envelope_status_removed": True,
        "record_semantic_status_retained": True,
        "envelope_status_derived_mechanically": True,
        "semantic_repair_added": False,
    })
    report["claims"]["v24_status_contradiction_removed_by_construction"] = passed
    report["decision"]["provider_probe_authorized"] = False
    report["decision"]["next_required_evidence"] = "adversarial status-free review, then genuinely new source-first case"
    base._write(output / "report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build(args.output.resolve())
    print(json.dumps({"status": report["status"], "summary": report["summary"], "schema_inventory": report["schema_inventory"]}, indent=2))
    return 0 if report["decision"]["provider_free_contract_gate"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
