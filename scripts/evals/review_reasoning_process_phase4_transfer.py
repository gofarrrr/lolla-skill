#!/usr/bin/env python3
"""Build a zero-call mechanical source-custody review of Phase-4 transfer output."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FULL_VIEWS = (
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


def _call_path(run: Path, case_id: str, job_id: str) -> Path:
    return run / "calls" / case_id / f"{job_id}.json"


def _protected_full(case_id: str, view: str) -> dict[str, Any]:
    if view in {"position_and_decision_trajectory", "challenge_and_revision_response"}:
        path = ROOT / "research/reasoning-process-view-specific-v2-2026-07-11/fixtures" / case_id / f"{view}.json"
        fixture = _load(path)
        observation = fixture["compiled"]["model_addendum"]["observations"][0]
    else:
        path = ROOT / "research/reasoning-process-view-specific-interface-2026-07-11/cases" / case_id / view / "compiled-fixture.json"
        fixture = _load(path)
        observation = fixture["fixture_addendum"]["observations"][0]
    return {
        "target_id": fixture["target_id"],
        "source_span_ids": observation["source_span_ids"],
        "artifact_path": str(path.relative_to(ROOT)),
        "artifact_sha256": _sha(path),
    }


def _protected_exploration(case_id: str) -> dict[str, Any]:
    path = ROOT / "research/reasoning-process-exploration-local-v2-2026-07-11/cases" / case_id / "protected-fixture.json"
    fixture = _load(path)
    observation = fixture["compiled"]["observations"][0]
    return {
        "target_id": fixture["target_id"],
        "source_span_ids": observation["source_span_ids"],
        "artifact_path": str(path.relative_to(ROOT)),
        "artifact_sha256": _sha(path),
    }


def build_review(contract: dict[str, Any], run: Path, retry: dict[str, Any] | None = None) -> dict[str, Any]:
    case_results = []
    all_observations = []
    raw_records = admitted = quarantined = 0
    for case in contract["cases"]:
        case_id = case["case_id"]
        targets = []
        completed_dimensions = set()
        for view in FULL_VIEWS:
            job_id = f"phase4-{case_id}-{view}"
            call = _load(_call_path(run, case_id, job_id))
            if retry and retry.get("call", {}).get("call_id") == job_id:
                call = retry["call"]
            protected = _protected_full(case_id, view)
            observations = call.get("compiled", {}).get("observations", []) if isinstance(call.get("compiled"), dict) else []
            matches = [
                item["observation_id"]
                for item in observations
                if set(protected["source_span_ids"]).issubset(set(item["source_span_ids"]))
            ]
            visible = bool(matches)
            if observations:
                completed_dimensions.add(view)
            targets.append({**protected, "view_kind": view, "visible": visible, "matching_observation_ids": matches, "operational_status": call["operational_status"]})
            all_observations.extend(observations)
            custody = call.get("compiled", {}).get("records", []) if isinstance(call.get("compiled"), dict) else []
            raw_records += len(custody)
            admitted += sum(item.get("terminal_state") == "admitted" for item in custody)
            quarantined += sum(item.get("terminal_state") == "quarantined" for item in custody)
        exploration = _protected_exploration(case_id)
        local_observations = []
        for turn_index in range(1, 8):
            job_id = f"phase4-{case_id}-exploration-turn-{turn_index:03d}"
            call = _load(_call_path(run, case_id, job_id))
            observations = call.get("compiled", {}).get("observations", []) if isinstance(call.get("compiled"), dict) else []
            local_observations.extend(observations)
            custody = call.get("compiled", {}).get("records", []) if isinstance(call.get("compiled"), dict) else []
            raw_records += len(custody)
            admitted += sum(item.get("terminal_state") == "admitted" for item in custody)
            quarantined += sum(item.get("terminal_state") == "quarantined" for item in custody)
        matches = [
            item["observation_id"]
            for item in local_observations
            if set(exploration["source_span_ids"]).issubset(set(item["source_span_ids"]))
        ]
        visible = bool(matches)
        if local_observations:
            completed_dimensions.add("exploration_and_alternatives")
        targets.append({**exploration, "view_kind": "exploration_and_alternatives", "visible": visible, "matching_observation_ids": matches, "operational_status": "ok"})
        all_observations.extend(local_observations)
        case_results.append(
            {
                "case_id": case_id,
                "protected_targets": targets,
                "protected_visible_count": sum(item["visible"] for item in targets),
                "protected_target_count": 5,
                "protected_target_missing_count": sum(not item["visible"] for item in targets),
                "critical_dimension_zero_count": 5 - len(completed_dimensions),
                "critical_dimension_floor_gate": "pass" if len(completed_dimensions) == 5 else "incomplete_or_fail",
                "protected_target_gate": "pass" if all(item["visible"] for item in targets) else "fail",
            }
        )
    signatures = [
        (item["family"], tuple(sorted(item["source_span_ids"])))
        for item in all_observations
    ]
    duplicate_excess = sum(count - 1 for count in Counter(signatures).values() if count > 1)
    return {
        "schema_version": "lolla.reasoning_process_phase4_transfer_mechanical_review.v1",
        "status": "mechanical_review_complete_semantic_review_pending",
        "date": "2026-07-11",
        "contract_sha256": _sha(ROOT / "research/reasoning-process-phase4-transfer-design-2026-07-11/contract.json"),
        "run_result_sha256": _sha(run / "result.json"),
        "cases": case_results,
        "summary": {
            "case_count": len(case_results),
            "protected_target_count": 10,
            "protected_visible_count": sum(item["protected_visible_count"] for item in case_results),
            "critical_dimension_zero_count": sum(item["critical_dimension_zero_count"] for item in case_results),
            "raw_record_count": raw_records,
            "admitted_record_count": admitted,
            "quarantined_record_count": quarantined,
            "exact_source_signature_duplicate_excess_count": duplicate_excess,
            "review_provider_calls": 0,
            "semantic_adequacy_decided_by_code": False,
        },
        "pending": [
            "one operationally failed Case-01 evidence reader",
            "source-first semantic role and source-strength review",
            "cross-record semantic fragmentation review without deterministic merging",
        ],
        "boundary": {
            "protected_targets_seen_by_model": False,
            "semantic_match_or_paraphrase_inferred_by_code": False,
            "quality_or_trust_score_produced": False,
            "graph_or_runtime_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retry", type=Path)
    args = parser.parse_args()
    review = build_review(
        _load(args.contract.resolve()),
        args.run.resolve(),
        _load(args.retry.resolve()) if args.retry else None,
    )
    _write(args.output.resolve(), review)
    print(json.dumps(review["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
