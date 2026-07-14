#!/usr/bin/env python3
"""Provider-free Phase A replay for the decomposed event architecture."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from engine.system_b.conversation_event_harvesting import build_turn_pair_windows
from engine.system_b.conversation_event_pipeline import (
    build_event_ledger,
    build_synthesis_ledger,
    compile_handoff_from_event_ledgers,
    reviewed_event_projection,
    reviewed_fresh_syntheses,
)
from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.conversation_state_handoff import (
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "research/conversation-state-handoff-v1-2026-07-10/cases"
DEFAULT_MIGRATION = ROOT / "research/conversation-state-recovery-v1-2026-07-11/atomic-migration.json"
DEFAULT_OUTPUT = ROOT / "research/conversation-event-architecture-phase-a-2026-07-11"


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def run(*, cases_dir: Path, migration_path: Path, output_dir: Path) -> dict[str, Any]:
    migration = json.loads(migration_path.read_text())
    rows: list[dict[str, Any]] = []
    for case_path in sorted(cases_dir.glob("*.json")):
        packet = json.loads(case_path.read_text())
        source_path = ROOT / packet["source"]["path"]
        source_text = source_path.read_text()
        catalog = build_source_catalog(
            source_text=source_text, source_path=packet["source"]["path"]
        )
        windows = build_turn_pair_windows(catalog)
        harvests, projection = reviewed_event_projection(
            packet=packet,
            catalog=catalog,
            windows=windows,
            atomic_migrations=migration,
        )
        event_ledger = build_event_ledger(
            case_id=packet["case_id"],
            catalog=catalog,
            windows=windows,
            harvests=harvests,
        )
        syntheses = reviewed_fresh_syntheses(
            event_ledger=event_ledger, projection=projection
        )
        synthesis_ledger = build_synthesis_ledger(
            case_id=packet["case_id"],
            event_ledger=event_ledger,
            syntheses=syntheses,
        )
        compiled, compiler = compile_handoff_from_event_ledgers(
            event_ledger=event_ledger,
            synthesis_ledger=synthesis_ledger,
            catalog=catalog,
        )
        violations = (
            validate_conversation_state_handoff(compiled, source_text=source_text)
            if compiled is not None
            else [{"code": "compiled_handoff_missing"}]
        )
        boundary = build_fact_free_routing_boundary(compiled) if not violations else None
        case_output = output_dir / "cases" / packet["case_id"]
        _write(case_output / "event-ledger.json", event_ledger)
        _write(case_output / "synthesis-ledger.json", synthesis_ledger)
        _write(case_output / "compiled-handoff.json", compiled)
        _write(case_output / "compiler-result.json", compiler)
        row = {
            "case_id": packet["case_id"],
            "window_count": len(windows),
            "harvest_contract_count": len(harvests),
            "event_count": event_ledger["metrics"]["proposal_count"],
            "invalid_event_count": event_ledger["metrics"]["invalid_event_count"],
            "synthesis_count": synthesis_ledger["metrics"]["proposal_count"],
            "invalid_synthesis_count": synthesis_ledger["metrics"]["invalid_synthesis_count"],
            "compiled": compiler["status"] == "compiled",
            "handoff_violation_count": len(violations),
            "position_text_preserved": (
                compiled is not None
                and [item["text"] for item in compiled["positions"]]
                == [item["text"] for item in packet["positions"]]
            ),
            "position_ownership_preserved": (
                compiled is not None
                and [item["ownership"] for item in compiled["positions"]]
                == [item["ownership"] for item in packet["positions"]]
            ),
            "thread_disposition_preserved": (
                compiled is not None
                and [item["disposition"] for item in compiled["threads"]]
                == [item["disposition"] for item in packet["threads"]]
            ),
            "atomic_constraint_count": len(compiled["constraints"]) if compiled else 0,
            "mixed_constraint_count": (
                sum(item["claim_mode"] == "mixed" for item in compiled["constraints"])
                if compiled else 0
            ),
            "direct_graph_seed_count": (
                boundary["direct_graph_seed_count"] if boundary else None
            ),
            "provider_calls": 0,
        }
        _write(case_output / "result.json", {**row, "handoff_violations": violations})
        rows.append(row)
    required_flags = (
        "compiled",
        "position_text_preserved",
        "position_ownership_preserved",
        "thread_disposition_preserved",
    )
    passed = all(
        all(row[name] for name in required_flags)
        and row["invalid_event_count"] == 0
        and row["invalid_synthesis_count"] == 0
        and row["handoff_violation_count"] == 0
        and row["mixed_constraint_count"] == 0
        and row["direct_graph_seed_count"] == 0
        for row in rows
    )
    summary = {
        "schema_version": "lolla.conversation_event_phase_a_result.v1",
        "status": "pass" if passed else "fail",
        "phase": "A_provider_free_representation",
        "case_count": len(rows),
        "cases_passed": sum(
            all(row[name] for name in required_flags)
            and row["invalid_event_count"] == 0
            and row["invalid_synthesis_count"] == 0
            and row["handoff_violation_count"] == 0
            and row["mixed_constraint_count"] == 0
            and row["direct_graph_seed_count"] == 0
            for row in rows
        ),
        "turn_pair_window_count": sum(row["window_count"] for row in rows),
        "harvest_contract_count": sum(row["harvest_contract_count"] for row in rows),
        "harvested_event_count": sum(row["event_count"] for row in rows),
        "synthesis_candidate_count": sum(row["synthesis_count"] for row in rows),
        "atomic_constraint_count": sum(row["atomic_constraint_count"] for row in rows),
        "invalid_event_count": sum(row["invalid_event_count"] for row in rows),
        "invalid_synthesis_count": sum(row["invalid_synthesis_count"] for row in rows),
        "handoff_violation_count": sum(row["handoff_violation_count"] for row in rows),
        "mixed_constraint_count": sum(row["mixed_constraint_count"] for row in rows),
        "direct_graph_seed_count": sum(row["direct_graph_seed_count"] or 0 for row in rows),
        "provider_calls": 0,
        "runtime_integration": False,
        "rows": rows,
        "non_claims": [
            "reviewed_projection_does_not_measure_model_quality",
            "phase_a_pass_only_proves_representation_and_custody",
            "no_live_or_graph_integration_authority",
        ],
    }
    _write(output_dir / "result.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases-dir", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--migration", type=Path, default=DEFAULT_MIGRATION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = run(
        cases_dir=args.cases_dir, migration_path=args.migration, output_dir=args.output_dir
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
