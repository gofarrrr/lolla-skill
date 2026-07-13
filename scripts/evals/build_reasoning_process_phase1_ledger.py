#!/usr/bin/env python3
"""Build the five Phase-1 canonical ledgers without provider calls."""
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

from engine.system_b.reasoning_process_ledger import (
    build_case_ledger,
    build_phase1_aggregate,
    load_case_inputs,
)


DEFAULT_CONTRACT = ROOT / "docs/evals/reasoning-process-phase1-ledger-contract-v1.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    contract_path = args.contract.resolve()
    out = args.out.resolve()
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    _validate_contract(contract)
    out.mkdir(parents=True, exist_ok=True)
    cases_out = out / "cases"
    cases_out.mkdir(parents=True, exist_ok=True)

    reports: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []
    for case in contract["cases"]:
        _validate_input_locks(case)
        case_id = case["case_id"]
        source_text, event_ledger, event_ref, synthesis_ledger, synthesis_ref = (
            load_case_inputs(
                root=ROOT,
                case_id=case_id,
                source_path=case["source_path"],
                event_ledger_path=case["event_ledger_path"],
                synthesis_ledger_path=case["synthesis_ledger_path"],
            )
        )
        ledger, report = build_case_ledger(
            case_id=case_id,
            source_text=source_text,
            source_path=case["source_path"],
            event_ledger=event_ledger,
            event_artifact=event_ref,
            synthesis_ledger=synthesis_ledger,
            synthesis_artifact=synthesis_ref,
        )
        case_dir = cases_out / case_id
        case_dir.mkdir(parents=True, exist_ok=True)
        ledger_path = case_dir / "ledger.json"
        report_path = case_dir / "report.json"
        _write_json(ledger_path, ledger)
        _write_json(report_path, report)
        reports.append(report)
        case_rows.append(
            {
                "case_id": case_id,
                "ledger_path": _display_path(ledger_path),
                "ledger_sha256": _sha256(ledger_path),
                "report_path": _display_path(report_path),
                "report_sha256": _sha256(report_path),
            }
        )

    aggregate = build_phase1_aggregate(reports)
    _validate_aggregate(contract, aggregate, reports)
    aggregate["contract"] = {
        "path": str(contract_path.relative_to(ROOT)),
        "sha256": _sha256(contract_path),
    }
    aggregate["case_artifacts"] = case_rows
    _write_json(out / "aggregate.json", aggregate)
    print(json.dumps(aggregate, indent=2, ensure_ascii=False))
    return 0


def _validate_contract(contract: dict[str, Any]) -> None:
    if contract.get("schema_version") != "lolla.reasoning_process_phase1_contract.v1":
        raise ValueError("Phase-1 contract schema version mismatch")
    if contract.get("status") != "frozen_provider_free":
        raise ValueError("Phase-1 contract is not frozen")
    if len(contract.get("cases", [])) != 5:
        raise ValueError("Phase-1 contract must contain five cases")
    calls = contract.get("exit_gates", {})
    for field in (
        "provider_calls",
        "embedding_calls",
        "evaluator_calls",
        "graph_calls",
        "pipeline_calls",
        "runtime_calls",
    ):
        if calls.get(field) != 0:
            raise ValueError(f"Phase-1 contract {field} must be zero")


def _validate_input_locks(case: dict[str, Any]) -> None:
    locks = (
        (case["source_path"], case["source_sha256"]),
        (case["event_ledger_path"], case["event_ledger_sha256"]),
        (case["synthesis_ledger_path"], case["synthesis_ledger_sha256"]),
    )
    for relative, expected in locks:
        path = ROOT / relative
        actual = _sha256(path)
        if actual != expected:
            raise ValueError(f"input hash drift: {relative}")
    event = json.loads((ROOT / case["event_ledger_path"]).read_text(encoding="utf-8"))
    synthesis = json.loads(
        (ROOT / case["synthesis_ledger_path"]).read_text(encoding="utf-8")
    )
    if len(event.get("events", [])) != case["event_count"]:
        raise ValueError(f"event count mismatch: {case['case_id']}")
    if len(synthesis.get("syntheses", [])) != case["synthesis_count"]:
        raise ValueError(f"synthesis count mismatch: {case['case_id']}")


def _validate_aggregate(
    contract: dict[str, Any], aggregate: dict[str, Any], reports: list[dict[str, Any]]
) -> None:
    required = contract["required_aggregate"]
    if aggregate["case_count"] != required["case_count"]:
        raise ValueError("aggregate case count mismatch")
    for field in ("observation_count", "scope_outcome_count", "failure_count"):
        if aggregate["totals"].get(field) != required[field]:
            raise ValueError(f"aggregate {field} mismatch")
    if aggregate["counts_by_family"] != required["counts_by_family"]:
        raise ValueError("aggregate family counts mismatch")
    if aggregate["known_family_gaps"] != required["known_family_gaps"]:
        raise ValueError("aggregate known family gaps mismatch")
    if aggregate["direct_graph_seed_count"] != required["direct_graph_seed_count"]:
        raise ValueError("aggregate graph boundary mismatch")
    if sum(report["metrics"]["source_artifact_count"] for report in reports) != required[
        "source_artifact_count"
    ]:
        raise ValueError("aggregate source artifact count mismatch")
    message_count = sum(
        int(case["message_count"]) for case in contract.get("cases", [])
    )
    if message_count != required["message_count"]:
        raise ValueError("aggregate message count mismatch")
    if aggregate["status"] != "provider_free_pass":
        raise ValueError("Phase-1 aggregate did not pass")


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
