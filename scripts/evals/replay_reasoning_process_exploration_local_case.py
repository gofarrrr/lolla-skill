#!/usr/bin/env python3
"""Build record-level custody from preserved local exploration calls, with no calls."""
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

from engine.system_b.reasoning_process_exploration_local import (  # noqa: E402
    compile_local_response,
    validate_local_response,
)
from engine.system_b.reasoning_process_views import canonical_json_bytes, sha256_bytes  # noqa: E402


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(*, root: Path, output: Path) -> dict[str, Any]:
    packet_root = (
        root
        / "research/reasoning-process-exploration-local-v2-2026-07-11/cases/amb1-case02-nonprofit-scale/windows"
    )
    call_paths = {
        1: root / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-001.json",
        2: root / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-002.json",
        3: root / "research/reasoning-process-exploration-local-probe-2026-07-11/call.json",
        4: root / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-004.json",
        5: root / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-005.json",
        6: root / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-006.json",
        7: root / "research/reasoning-process-exploration-local-case02-2026-07-11/calls/turn-007.json",
    }
    original_hashes = {turn: _sha(path) for turn, path in call_paths.items()}
    windows = []
    admitted_observations = []
    record_custody = []
    role_pair_owner: dict[tuple[tuple[str, ...], tuple[str, ...]], str] = {}
    total_cost = 0.0
    operational_success = 0
    for turn_index in range(1, 8):
        call_path = call_paths[turn_index]
        call = _load(call_path)
        wrapper = _load(packet_root / f"turn-{turn_index:03d}.json")
        if isinstance(call.get("estimated_cost_usd"), (int, float)):
            total_cost += float(call["estimated_cost_usd"])
        if call.get("operational_status") != "ok":
            windows.append(
                {
                    "focal_turn_index": turn_index,
                    "window_id": wrapper["packet"]["window_id"],
                    "terminal_disposition": "failed_operationally",
                    "provider_diagnostic": call.get("provider_diagnostic", {}),
                    "record_count": 0,
                }
            )
            continue
        operational_success += 1
        payload = call.get("candidate_payload")
        records = payload.get("records", []) if isinstance(payload, dict) else []
        admitted_this_window = 0
        quarantined_this_window = 0
        for record_index, record in enumerate(records, start=1):
            singleton = {
                "status": "supported",
                "records": [record],
                "global_limitations": payload.get("global_limitations", ""),
            }
            pair = (
                tuple(record.get("alternative_evidence_ids", [])),
                tuple(record.get("attached_condition_or_limit_evidence_ids", [])),
            )
            duplicate_of = role_pair_owner.get(pair, "")
            try:
                validate_local_response(singleton, wrapper=wrapper)
                compiled = compile_local_response(
                    response=singleton,
                    wrapper=wrapper,
                    producer_kind="model",
                    producer_id=call["requested_model"],
                    record_identity=f"replay-turn-{turn_index:03d}-record-{record_index:02d}",
                    call_metadata={
                        "call_id": call["call_id"],
                        "model": call["served_model"],
                        "prompt_sha256": "sha256:" + call["user_prompt_sha256"],
                    },
                )
                observation = compiled["observations"][0]
                if duplicate_of:
                    observation["exact_role_alias_duplicate_of"] = duplicate_of
                else:
                    role_pair_owner[pair] = observation["observation_id"]
                admitted_observations.append(observation)
                admitted_this_window += 1
                record_custody.append(
                    {
                        "focal_turn_index": turn_index,
                        "record_index": record_index,
                        "terminal_state": "admitted",
                        "observation_id": observation["observation_id"],
                        "exact_role_alias_duplicate_of": duplicate_of,
                        "raw_record_sha256": "sha256:"
                        + sha256_bytes(canonical_json_bytes(record)),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                quarantined_this_window += 1
                record_custody.append(
                    {
                        "focal_turn_index": turn_index,
                        "record_index": record_index,
                        "terminal_state": "quarantined",
                        "reason": f"{type(exc).__name__}: {exc}",
                        "exact_role_alias_duplicate_of": duplicate_of,
                        "raw_record_sha256": "sha256:"
                        + sha256_bytes(canonical_json_bytes(record)),
                    }
                )
        windows.append(
            {
                "focal_turn_index": turn_index,
                "window_id": wrapper["packet"]["window_id"],
                "terminal_disposition": (
                    "partially_compiled"
                    if admitted_this_window and quarantined_this_window
                    else "compiled"
                    if admitted_this_window
                    else "reviewed_empty"
                    if not records
                    else "quarantined"
                ),
                "record_count": len(records),
                "admitted_record_count": admitted_this_window,
                "quarantined_record_count": quarantined_this_window,
            }
        )
    for turn, path in call_paths.items():
        if _sha(path) != original_hashes[turn]:
            raise RuntimeError(f"preserved call changed during replay: turn {turn}")
    report = {
        "schema_version": "lolla.reasoning_process_exploration_local_case_replay.v1",
        "status": "record_level_custody_replay_complete",
        "case_id": "amb1-case02-nonprofit-scale",
        "source_call_artifacts": [
            {
                "focal_turn_index": turn,
                "path": str(path.relative_to(root)),
                "sha256": original_hashes[turn],
            }
            for turn, path in call_paths.items()
        ],
        "windows": windows,
        "record_custody": record_custody,
        "chronological_admitted_observations": admitted_observations,
        "summary": {
            "expected_window_count": 7,
            "provider_call_count": 7,
            "operational_success_count": operational_success,
            "operational_failure_count": 7 - operational_success,
            "raw_model_record_count": len(record_custody),
            "admitted_record_count": sum(
                item["terminal_state"] == "admitted" for item in record_custody
            ),
            "quarantined_record_count": sum(
                item["terminal_state"] == "quarantined" for item in record_custody
            ),
            "exact_role_alias_duplicate_count": sum(
                bool(item.get("exact_role_alias_duplicate_of"))
                for item in record_custody
            ),
            "estimated_cost_usd": round(total_cost, 9),
            "replay_provider_calls": 0,
            "automatic_retries": 0,
            "fallback_models": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "boundary": {
            "model_records_changed": False,
            "record_level_validation_weakened": False,
            "semantic_deduplication_performed": False,
            "global_synthesis_performed": False,
            "phase4_transfer_authorized": False,
        },
    }
    _write(output / "replay-report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-exploration-local-case02-replay-2026-07-11"),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    report = replay(root=root, output=root / args.output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
