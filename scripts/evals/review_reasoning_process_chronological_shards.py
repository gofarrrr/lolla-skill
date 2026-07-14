#!/usr/bin/env python3
"""Check protected-target co-location in provider-free chronological shards."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
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


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _target(case_id: str, view: str) -> tuple[str, list[str], str]:
    if view in {"position_and_decision_trajectory", "challenge_and_revision_response"}:
        path = ROOT / "research/reasoning-process-view-specific-v2-2026-07-11/fixtures" / case_id / f"{view}.json"
        fixture = _load(path)
        observation = fixture["compiled"]["model_addendum"]["observations"][0]
    else:
        path = ROOT / "research/reasoning-process-view-specific-interface-2026-07-11/cases" / case_id / view / "compiled-fixture.json"
        fixture = _load(path)
        observation = fixture["fixture_addendum"]["observations"][0]
    return fixture["target_id"], observation["source_span_ids"], str(path.relative_to(ROOT))


def review(report: dict[str, Any]) -> dict[str, Any]:
    cases = []
    colocated = 0
    for case in report["cases"]:
        targets = []
        for view in VIEWS:
            target_id, spans, fixture_path = _target(case["case_id"], view)
            matches = []
            for artifact in case["artifacts"]:
                if artifact["view_kind"] != view:
                    continue
                wrapper = _load(ROOT / artifact["path"])
                available = {item["span_id"] for item in wrapper["focal_alias_map"]}
                if set(spans).issubset(available):
                    matches.append(artifact["path"])
            target_colocated = len(matches) == 1
            colocated += target_colocated
            targets.append(
                {
                    "target_id": target_id,
                    "view_kind": view,
                    "source_span_ids": spans,
                    "fixture_path": fixture_path,
                    "co_located_in_exactly_one_focal_shard": target_colocated,
                    "matching_shard_paths": matches,
                }
            )
        cases.append({"case_id": case["case_id"], "targets": targets, "co_located_count": sum(item["co_located_in_exactly_one_focal_shard"] for item in targets)})
    return {
        "schema_version": "lolla.reasoning_process_chronological_shards_review.v1",
        "status": "provider_free_target_representation_pass" if colocated == 20 else "provider_free_target_representation_fail",
        "date": "2026-07-11",
        "shard_report_sha256": _sha(ROOT / "research/reasoning-process-chronological-shards-2026-07-11/report.json"),
        "cases": cases,
        "summary": {
            "protected_target_count": 20,
            "protected_targets_colocated": colocated,
            "provider_calls": 0,
            "semantic_model_behavior_validated": False,
        },
        "decision": {
            "packet_representation_gate": "pass" if colocated == 20 else "fail",
            "prompt_schema_and_record_custody_design_authorized": colocated == 20,
            "provider_probe_authorized": False,
        },
        "nonclaim": "Target co-location shows representability, not that a model will select or interpret the target.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = review(_load(args.report.resolve()))
    _write(args.output.resolve(), value)
    print(json.dumps(value["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
