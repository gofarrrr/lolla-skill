#!/usr/bin/env python3
"""Build provider-free chronological shard packets and representation report."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.reasoning_process_chronological_shards import build_chronological_shard_packets  # noqa: E402


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(output: Path) -> dict[str, Any]:
    coverage = _load(ROOT / "docs/evals/reasoning-process-phase2-coverage-contract-v1.json")
    case_results = []
    for case in coverage["cases"]:
        case_id = case["case_id"]
        source_path = case["source_path"]
        source_text = (ROOT / source_path).read_text(encoding="utf-8")
        full_wrapper = _load(
            ROOT
            / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
            / case_id
            / "position_and_decision_trajectory/reader-packet.json"
        )
        packets = build_chronological_shard_packets(
            case_id=case_id,
            source_path=source_path,
            source_text=source_text,
            global_alias_map=full_wrapper["evidence_alias_map"],
        )
        artifacts = []
        for wrapper in packets:
            packet = wrapper["packet"]
            path = output / "cases" / case_id / packet["view_kind"] / f"shard-{packet['shard_id'].rsplit('-', 1)[-1]}.json"
            _write(path, wrapper)
            artifacts.append(
                {
                    "view_kind": packet["view_kind"],
                    "shard_kind": packet["shard_kind"],
                    "focal_turn_indices": packet["focal_turn_indices"],
                    "input_utf8_bytes": wrapper["metrics"]["input_utf8_bytes"],
                    "future_max_records": wrapper["metrics"]["future_max_records"],
                    "path": str(path.relative_to(ROOT)),
                }
            )
        case_results.append(
            {
                "case_id": case_id,
                "shard_count": len(packets),
                "future_max_records": sum(item["metrics"]["future_max_records"] for item in packets),
                "maximum_packet_utf8_bytes": max(item["metrics"]["input_utf8_bytes"] for item in packets),
                "artifacts": artifacts,
            }
        )
    report = {
        "schema_version": "lolla.reasoning_process_chronological_shards_report.v1",
        "status": "provider_free_representation_built_semantic_probe_not_authorized",
        "date": "2026-07-11",
        "cases": case_results,
        "summary": {
            "case_count": len(case_results),
            "families_per_case": 4,
            "shards_per_family": 3,
            "shards_per_case": 12,
            "future_max_records_per_case_before_existing_exploration": 24,
            "future_existing_exploration_calls_per_case": 7,
            "future_total_calls_per_case": 19,
            "future_total_max_records_per_case": 38,
            "provider_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "boundary": {
            "semantic_prefilter_performed": False,
            "deterministic_semantic_gate_performed": False,
            "global_synthesis_authorized": False,
            "semantic_deduplication_authorized": False,
            "provider_probe_authorized": False,
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
