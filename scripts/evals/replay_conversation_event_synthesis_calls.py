#!/usr/bin/env python3
"""Provider-free replay of preserved synthesis call payloads through current custody."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from engine.system_b.conversation_event_harvesting import parse_synthesis
from engine.system_b.conversation_event_pipeline import (
    build_synthesis_ledger,
    compile_handoff_from_event_ledgers,
)
from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.conversation_state_handoff import (
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)


ROOT = Path(__file__).resolve().parents[2]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def replay(*, input_dir: Path, output_dir: Path) -> dict:
    input_dir, output_dir = input_dir.resolve(), output_dir.resolve()
    contract_path = input_dir / "contract.json"
    contract = json.loads(contract_path.read_text())
    rows = []
    for case in contract["cases"]:
        case_id = case["case_id"]
        event_path = ROOT / case["event_ledger_path"]
        event_ledger = json.loads(event_path.read_text())
        syntheses = {}
        calls = []
        for family in ("positions", "threads", "constraints"):
            call_path = input_dir / "calls" / f"{case_id}--{family}.json"
            call = json.loads(call_path.read_text())
            calls.append({"family": family, "path": str(call_path.relative_to(ROOT)), "sha256": _sha(call_path)})
            typed, issues = parse_synthesis(family, call.get("candidate_payload"))
            if typed is not None and not issues:
                syntheses[family] = typed
        ledger = build_synthesis_ledger(
            case_id=case_id, event_ledger=event_ledger, syntheses=syntheses
        )
        source_text = (ROOT / case["source_path"]).read_text()
        catalog = build_source_catalog(source_text=source_text, source_path=case["source_path"])
        compiled, compiler = compile_handoff_from_event_ledgers(
            event_ledger=event_ledger,
            synthesis_ledger=ledger,
            catalog=catalog,
            handoff_status="model_probe_unreviewed",
        )
        violations = validate_conversation_state_handoff(compiled, source_text=source_text) if compiled else []
        boundary = build_fact_free_routing_boundary(compiled) if compiled and not violations else None
        case_dir = output_dir / "cases" / case_id
        _write(case_dir / "synthesis-ledger.json", ledger)
        _write(case_dir / "compiled-handoff.json", compiled)
        _write(case_dir / "compiler-result.json", compiler)
        row = {
            "case_id": case_id,
            "admitted_family_count": len(syntheses),
            "missing_families": sorted(set(("positions", "threads", "constraints")) - set(syntheses)),
            "invalid_synthesis_count": ledger["metrics"]["invalid_synthesis_count"],
            "compiled": compiled is not None,
            "compiler_status": compiler["status"],
            "compiler_reason": compiler["reason"],
            "handoff_violation_count": len(violations),
            "direct_graph_seed_count": boundary["direct_graph_seed_count"] if boundary else None,
            "call_evidence": calls,
            "event_ledger_sha256": _sha(event_path),
        }
        _write(case_dir / "result.json", row)
        rows.append(row)
    summary = {
        "schema_version": "lolla.conversation_event_synthesis_replay.v1",
        "status": "pass" if all(row["compiled"] for row in rows) else "fail_closed",
        "source_contract_path": str(contract_path.relative_to(ROOT)),
        "source_contract_sha256": _sha(contract_path),
        "provider_calls": 0,
        "automatic_retries": 0,
        "compiled_case_count": sum(row["compiled"] for row in rows),
        "quarantined_case_count": sum(not row["compiled"] for row in rows),
        "direct_graph_seed_count": sum(row["direct_graph_seed_count"] or 0 for row in rows),
        "cases": rows,
        "non_claims": [
            "replay_does_not_change_or_heal_model_outputs",
            "current_deterministic_custody_is_applied_to_preserved_payloads",
            "no_graph_or_runtime_authority",
        ],
    }
    _write(output_dir / "result.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(replay(input_dir=args.input_dir, output_dir=args.output_dir), indent=2))


if __name__ == "__main__":
    main()
