#!/usr/bin/env python3
"""Seal the completed Case-02 local exploration evidence package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def seal(*, root: Path, output: Path) -> dict:
    replay = _load(
        root
        / "research/reasoning-process-exploration-local-case02-replay-2026-07-11/replay-report.json"
    )
    retry_call = _load(
        root / "research/reasoning-process-exploration-local-turn5-retry-2026-07-11/call.json"
    )
    retry_result = _load(
        root / "research/reasoning-process-exploration-local-turn5-retry-2026-07-11/result.json"
    )
    if retry_call["operational_status"] != "ok" or retry_call["typed_status"] != "admitted":
        raise RuntimeError("Turn-5 operational completion did not pass")
    retry_compiled = retry_call["compiled"]
    if retry_compiled["window_terminal_disposition"] != "compiled":
        raise RuntimeError("Turn-5 record-level custody did not compile")
    windows = []
    for window in replay["windows"]:
        if window["focal_turn_index"] == 5:
            windows.append(
                {
                    "focal_turn_index": 5,
                    "window_id": "amb1-case02-nonprofit-scale-exploration-turn-005",
                    "first_attempt_disposition": "failed_operationally",
                    "terminal_disposition": "compiled_after_one_cooled_operational_retry",
                    "record_count": len(retry_compiled["records"]),
                    "admitted_record_count": len(retry_compiled["observations"]),
                    "quarantined_record_count": 0,
                }
            )
        else:
            windows.append(window)
    observations = [
        *replay["chronological_admitted_observations"],
        *retry_compiled["observations"],
    ]
    observations.sort(key=lambda item: (item["focal_turn_index"], item["observation_id"]))
    record_custody = [
        *replay["record_custody"],
        *[
            {
                "focal_turn_index": 5,
                "record_index": item["record_index"],
                "terminal_state": item["terminal_state"],
                "observation_id": item.get("observation_id", ""),
                "raw_record_sha256": item["raw_record_sha256"],
                "source": "cooled_operational_retry",
            }
            for item in retry_compiled["records"]
        ],
    ]
    total_cost = replay["summary"]["estimated_cost_usd"] + float(
        retry_result["estimated_cost_usd"]
    )
    result = {
        "schema_version": "lolla.reasoning_process_exploration_local_case_terminal.v1",
        "status": "development_case_complete_local_exploration_pass",
        "date": "2026-07-11",
        "case_id": "amb1-case02-nonprofit-scale",
        "windows": windows,
        "record_custody": record_custody,
        "chronological_admitted_observations": observations,
        "summary": {
            "window_count": 7,
            "first_attempt_operational_success_count": 6,
            "eventual_completed_window_count": 7,
            "provider_request_count_including_operational_retry": 8,
            "cooled_operational_retry_count": 1,
            "raw_model_record_count": len(record_custody),
            "admitted_record_count": len(observations),
            "quarantined_record_count": sum(
                item["terminal_state"] == "quarantined" for item in record_custody
            ),
            "exact_role_alias_duplicate_count": replay["summary"][
                "exact_role_alias_duplicate_count"
            ],
            "invalid_admitted_record_count": 0,
            "source_strength_inflation_count": 0,
            "estimated_cost_usd": round(total_cost, 9),
            "automatic_retries": 0,
            "fallback_models": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
        "decision": {
            "semantic_mechanism_gate": "pass",
            "complete_development_case_gate": "pass_with_one_preserved_operational_retry",
            "record_level_custody_required": True,
            "global_synthesis_required": False,
            "semantic_deduplication_required": False,
            "prospective_transfer_contract_may_be_designed": True,
            "transfer_calls_authorized_by_this_result": False,
            "phase4_complete": False,
            "graph_or_runtime_authorized": False,
        },
        "boundary": {
            "original_rate_limit_failure_preserved": True,
            "model_records_changed": False,
            "semantic_gate_weakened": False,
            "final_output_evaluated": False,
            "quality_or_trust_score_included": False,
        },
        "nonclaims": [
            "One development case does not establish transfer or stability.",
            "Thirteen source-supported local records do not prove that every useful alternative was captured.",
            "Call and record counts are not reasoning-quality or proof-of-work evidence."
        ],
    }
    _write(output / "terminal-result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("research/reasoning-process-exploration-local-terminal-2026-07-11"),
    )
    args = parser.parse_args()
    root = args.repo_root.resolve()
    result = seal(root=root, output=root / args.output)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
