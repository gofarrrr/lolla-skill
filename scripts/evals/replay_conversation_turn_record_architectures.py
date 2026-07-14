#!/usr/bin/env python3
"""Provider-free five-case comparison of normalized turn-record architectures."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from engine.system_b.conversation_event_harvesting import (
    ConstraintSynthesis,
    ConstraintSynthesisCandidate,
    PositionSynthesis,
    PositionSynthesisCandidate,
    SpanSelection,
    SynthesizedContribution,
    SynthesizedThreadResponse,
    ThreadSynthesis,
    ThreadSynthesisCandidate,
    build_turn_pair_windows,
)
from engine.system_b.conversation_event_pipeline import (
    build_event_ledger,
    build_synthesis_ledger,
    compile_handoff_from_event_ledgers,
    reviewed_event_projection,
)
from engine.system_b.conversation_state_candidate_pipeline import decompose_reviewed_handoff
from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.conversation_state_handoff import (
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)
from engine.system_b.conversation_turn_records import (
    ConversationTurnRecord,
    InputDisposition,
    LocalAtomicClaim,
    LocalDirectionalMove,
    LocalThreadSignal,
    build_turn_record_ledger,
)


ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "research/conversation-state-handoff-v1-2026-07-10/cases"
MIGRATION = ROOT / "research/conversation-state-recovery-v1-2026-07-11/atomic-migration.json"
DEFAULT_OUTPUT = ROOT / "research/conversation-turn-record-provider-free-v1-2026-07-11"


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _records_from_review(extracted: dict[str, Any], windows: tuple[Any, ...]):
    window_by_span = {span_id: window.window_id for window in windows for span_id in window.span_ids}
    staged = {window.window_id: {"moves": [], "threads": [], "claims": []} for window in windows}
    projection: dict[str, list[dict[str, Any]]] = {"positions": [], "threads": [], "constraints": []}
    for position in extracted["positions"].positions:
        refs = []
        for contribution in position.contributions:
            ref = contribution.evidence
            item = LocalDirectionalMove(position.text, (SpanSelection(ref.span_id),))
            staged[window_by_span[ref.span_id]]["moves"].append(item)
            refs.append({"span_id": ref.span_id, "role": contribution.role})
        projection["positions"].append({"text": position.text, "ownership": position.ownership, "state": position.state, "refs": refs})
    for thread in extracted["threads"].threads:
        refs = []
        introduced = LocalThreadSignal(thread.text, "raised", (SpanSelection(thread.introduced.span_id),))
        staged[window_by_span[thread.introduced.span_id]]["threads"].append(introduced)
        refs.append({"span_id": thread.introduced.span_id, "kind": "introduced"})
        responses = []
        for response in thread.responses:
            item = LocalThreadSignal(thread.text, "engaged", (SpanSelection(response.evidence.span_id),))
            staged[window_by_span[response.evidence.span_id]]["threads"].append(item)
            refs.append({"span_id": response.evidence.span_id, "kind": "response", "engagement": response.engagement})
            responses.append({"span_id": response.evidence.span_id, "engagement": response.engagement})
        if thread.latest.span_id not in {row["span_id"] for row in refs}:
            move = {"resolved": "resolution_claim", "superseded": "superseding_signal", "addressed_unresolved": "unresolved_signal"}.get(thread.disposition, "qualified")
            staged[window_by_span[thread.latest.span_id]]["threads"].append(
                LocalThreadSignal(thread.text, move, (SpanSelection(thread.latest.span_id),))
            )
            refs.append({"span_id": thread.latest.span_id, "kind": "latest"})
        projection["threads"].append({
            "text": thread.text,
            "disposition": thread.disposition,
            "introduced": thread.introduced.span_id,
            "latest": thread.latest.span_id,
            "responses": responses,
            "superseded_by": thread.superseded_by,
            "refs": refs,
        })
    for constraint in extracted["constraints"].constraints:
        refs = []
        for ref in constraint.evidence:
            staged[window_by_span[ref.span_id]]["claims"].append(
                LocalAtomicClaim(constraint.text, constraint.claim_mode, SpanSelection(ref.span_id))
            )
            refs.append(ref.span_id)
        projection["constraints"].append({"text": constraint.text, "state": constraint.state, "claim_mode": constraint.claim_mode, "refs": refs})
    records = {}
    for window in windows:
        row = staged[window.window_id]
        records[window.window_id] = ConversationTurnRecord(
            status="supported" if any(row.values()) else "not_found",
            directional_moves=tuple(row["moves"]),
            thread_signals=tuple(row["threads"]),
            claims=tuple(row["claims"]),
            input_dispositions=(),
        )
    return records, projection


def _event_adapter(turn_ledger: dict[str, Any]) -> dict[str, Any]:
    family = {"directional_move": "contributions", "thread_signal": "thread_events", "claim": "constraint_claims"}
    events = []
    for item in turn_ledger["items"]:
        events.append({
            "event_id": item["item_id"],
            "family": family[item["kind"]],
            "window_id": item["window_id"],
            "turn_index": item["turn_index"],
            "proposal_index": 1,
            "terminal_state": item["terminal_state"],
            "validation_issues": item["validation_issues"],
            "synthesis_eligible": item["synthesis_eligible"],
            "event_snapshot": item["event_snapshot"],
        })
    return {
        "case_id": turn_ledger["case_id"],
        "source": turn_ledger["source"],
        "events": events,
        "metrics": {
            "missing_harvest_count": turn_ledger["metrics"]["missing_record_count"],
            "invalid_event_count": turn_ledger["metrics"]["invalid_item_count"],
        },
    }


def _reviewed_synthesis(event_ledger: dict[str, Any], extracted: dict[str, Any], projection: dict[str, Any]):
    by_span: dict[str, list[str]] = {}
    for event in event_ledger["events"]:
        for source in event["event_snapshot"]["resolved_source"] if event["event_snapshot"] else []:
            by_span.setdefault(source["span_id"], []).append(event["event_id"])
    def eid(span_id: str, preferred: str | None = None) -> str:
        candidates = by_span[span_id]
        if preferred:
            for candidate in candidates:
                row = next(item for item in event_ledger["events"] if item["event_id"] == candidate)
                if row["family"] == preferred:
                    return candidate
        return candidates[0]
    positions = tuple(
        PositionSynthesisCandidate(
            text=row["text"], ownership=row["ownership"], state=row["state"],
            contributions=tuple(SynthesizedContribution(eid(ref["span_id"], "contributions"), ref["role"]) for ref in row["refs"]),
        ) for row in projection["positions"]
    )
    threads = []
    for row in projection["threads"]:
        event_ids = []
        for ref in row["refs"]:
            value = eid(ref["span_id"], "thread_events")
            if value not in event_ids:
                event_ids.append(value)
        threads.append(ThreadSynthesisCandidate(
            text=row["text"], disposition=row["disposition"], event_ids=tuple(event_ids),
            introduced_event_id=eid(row["introduced"], "thread_events"), latest_event_id=eid(row["latest"], "thread_events"),
            responses=tuple(SynthesizedThreadResponse(eid(ref["span_id"], "thread_events"), ref["engagement"]) for ref in row["responses"]),
            superseded_by=row["superseded_by"],
        ))
    constraints = tuple(
        ConstraintSynthesisCandidate(
            text=row["text"], state=row["state"], claim_mode=row["claim_mode"],
            claim_event_ids=tuple(eid(span_id, "constraint_claims") for span_id in row["refs"]),
        ) for row in projection["constraints"]
    )
    decision = extracted["positions"].decision_summary
    return {
        "positions": PositionSynthesis("supported", decision.text if decision else None, positions),
        "threads": ThreadSynthesis("supported" if threads else "not_found", tuple(threads)),
        "constraints": ConstraintSynthesis("supported" if constraints else "not_found", constraints),
    }


def _expected(extracted: dict[str, Any]):
    return {
        "moves": {item.evidence.span_id for row in extracted["positions"].positions for item in row.contributions},
        "threads": {ref.span_id for row in extracted["threads"].threads for ref in (row.introduced, row.latest)} | {item.evidence.span_id for row in extracted["threads"].threads for item in row.responses},
        "claims": {(ref.span_id, row.claim_mode) for row in extracted["constraints"].constraints for ref in row.evidence},
    }


def run(output_dir: Path) -> dict[str, Any]:
    migration = json.loads(MIGRATION.read_text())
    rows = []
    for case_path in sorted(CASES.glob("*.json")):
        packet = json.loads(case_path.read_text())
        source_text = (ROOT / packet["source"]["path"]).read_text()
        catalog = build_source_catalog(source_text=source_text, source_path=packet["source"]["path"])
        windows = build_turn_pair_windows(catalog)
        extracted = decompose_reviewed_handoff(packet, catalog=catalog, atomic_migrations=migration)
        base_records, projection = _records_from_review(extracted, windows)
        reviewed_harvests, _ = reviewed_event_projection(packet=packet, catalog=catalog, windows=windows, atomic_migrations=migration)
        lens_ledger = build_event_ledger(case_id=packet["case_id"], catalog=catalog, windows=windows, harvests=reviewed_harvests)
        input_by_window = {window.window_id: [row for row in lens_ledger["events"] if row["window_id"] == window.window_id] for window in windows}
        for architecture in ("single_reader", "three_lens_consolidation"):
            records = base_records
            if architecture == "three_lens_consolidation":
                records = {
                    window.window_id: ConversationTurnRecord(
                        status=base_records[window.window_id].status,
                        directional_moves=base_records[window.window_id].directional_moves,
                        thread_signals=base_records[window.window_id].thread_signals,
                        claims=base_records[window.window_id].claims,
                        input_dispositions=tuple(
                            InputDisposition(row["event_id"], "preserved", (f"reviewed-{index}",))
                            for index, row in enumerate(input_by_window[window.window_id], start=1)
                        ),
                    ) for window in windows
                }
            ledger = build_turn_record_ledger(
                architecture=architecture, case_id=packet["case_id"], catalog=catalog, windows=windows,
                records=records, input_events_by_window=input_by_window if architecture == "three_lens_consolidation" else None,
            )
            adapter = _event_adapter(ledger)
            syntheses = _reviewed_synthesis(adapter, extracted, projection)
            synthesis_ledger = build_synthesis_ledger(case_id=packet["case_id"], event_ledger=adapter, syntheses=syntheses)
            compiled, compiler = compile_handoff_from_event_ledgers(event_ledger=adapter, synthesis_ledger=synthesis_ledger, catalog=catalog)
            violations = validate_conversation_state_handoff(compiled, source_text=source_text) if compiled else [{"code": "compiled_missing"}]
            boundary = build_fact_free_routing_boundary(compiled) if compiled and not violations else None
            expected = _expected(extracted)
            observed_moves = {source["span_id"] for item in ledger["items"] if item["kind"] == "directional_move" and item["event_snapshot"] for source in item["event_snapshot"]["resolved_source"]}
            observed_threads = {source["span_id"] for item in ledger["items"] if item["kind"] == "thread_signal" and item["event_snapshot"] for source in item["event_snapshot"]["resolved_source"]}
            observed_claims = {(source["span_id"], item["event_snapshot"]["claim_mode"]) for item in ledger["items"] if item["kind"] == "claim" and item["event_snapshot"] for source in item["event_snapshot"]["resolved_source"]}
            row = {
                "case_id": packet["case_id"], "architecture": architecture,
                "reviewed_move_survival": len(expected["moves"] & observed_moves) / len(expected["moves"]) if expected["moves"] else 1.0,
                "reviewed_thread_survival": len(expected["threads"] & observed_threads) / len(expected["threads"]) if expected["threads"] else 1.0,
                "reviewed_claim_mode_survival": len(expected["claims"] & observed_claims) / len(expected["claims"]) if expected["claims"] else 1.0,
                "item_count": ledger["metrics"]["item_count"],
                "serialized_item_bytes": ledger["metrics"]["serialized_item_bytes"],
                "within_target_item_budget": ledger["metrics"]["within_target_item_budget"],
                "within_synthesis_byte_budget": ledger["metrics"]["within_synthesis_byte_budget"],
                "invalid_item_count": ledger["metrics"]["invalid_item_count"],
                "input_custody_invalid_window_count": ledger["metrics"]["input_custody_invalid_window_count"],
                "compiled": compiled is not None and compiler["status"] == "compiled",
                "handoff_violation_count": len(violations),
                "direct_graph_seed_count": boundary["direct_graph_seed_count"] if boundary else None,
                "provider_calls": 0,
            }
            case_dir = output_dir / "cases" / packet["case_id"] / architecture
            _write(case_dir / "turn-record-ledger.json", ledger)
            _write(case_dir / "synthesis-ledger.json", synthesis_ledger)
            _write(case_dir / "compiled-handoff.json", compiled)
            _write(case_dir / "result.json", row)
            rows.append(row)
    def passes(row):
        return all(row[key] == 1.0 for key in ("reviewed_move_survival", "reviewed_thread_survival", "reviewed_claim_mode_survival")) and row["within_target_item_budget"] and row["within_synthesis_byte_budget"] and row["invalid_item_count"] == 0 and row["input_custody_invalid_window_count"] == 0 and row["compiled"] and row["handoff_violation_count"] == 0 and row["direct_graph_seed_count"] == 0
    summary = {
        "schema_version": "lolla.conversation_turn_record_provider_free_comparison.v1",
        "status": "pass" if all(passes(row) for row in rows) else "fail",
        "case_architecture_count": len(rows),
        "passing_case_architecture_count": sum(passes(row) for row in rows),
        "provider_calls": 0,
        "rows": rows,
        "non_claims": ["provider_free_replay_is_not_model_quality", "reviewed_projection_is_not_independent_gold", "no_runtime_or_graph_authority"],
    }
    _write(output_dir / "result.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), indent=2))


if __name__ == "__main__":
    main()
