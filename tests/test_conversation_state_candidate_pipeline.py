from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from engine.system_b.conversation_state_candidate_pipeline import (
    build_candidate_ledger,
    compile_handoff_from_ledger,
    decompose_reviewed_handoff,
)
from engine.system_b.conversation_state_candidates import (
    EvidenceRef,
    PositionExtraction,
    build_source_catalog,
)
from engine.system_b.conversation_state_handoff import (
    build_fact_free_routing_boundary,
    validate_conversation_state_handoff,
)


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "research/conversation-state-handoff-v1-2026-07-10/cases"
MIGRATION_PATH = (
    ROOT / "research/conversation-state-recovery-v1-2026-07-11/atomic-migration.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _case(packet_path: Path):
    packet = _load(packet_path)
    source_path = ROOT / packet["source"]["path"]
    source_text = source_path.read_text(encoding="utf-8")
    catalog = build_source_catalog(
        source_text=source_text,
        source_path=packet["source"]["path"],
    )
    extractions = decompose_reviewed_handoff(
        packet,
        catalog=catalog,
        atomic_migrations=_load(MIGRATION_PATH),
    )
    ledger = build_candidate_ledger(
        case_id=packet["case_id"], catalog=catalog, extractions=extractions
    )
    compiled, result = compile_handoff_from_ledger(ledger=ledger, catalog=catalog)
    return packet, source_text, catalog, extractions, ledger, compiled, result


def test_five_reviewed_cases_decompose_and_reassemble_without_custody_loss() -> None:
    total_constraints = 0
    total_invalid = 0
    for path in sorted(CASE_DIR.glob("*.json")):
        packet, source_text, _catalog, _extractions, ledger, compiled, result = _case(path)
        assert result["status"] == "compiled"
        assert result["accepted_observed_path_allowed"] is True
        assert result["graph_routing_allowed"] is False
        assert compiled is not None
        assert validate_conversation_state_handoff(compiled, source_text=source_text) == []
        assert [row["ownership"] for row in compiled["positions"]] == [
            row["ownership"] for row in packet["positions"]
        ]
        assert [row["disposition"] for row in compiled["threads"]] == [
            row["disposition"] for row in packet["threads"]
        ]
        assert build_fact_free_routing_boundary(compiled)["direct_graph_seed_count"] == 0
        total_constraints += len(compiled["constraints"])
        total_invalid += ledger["metrics"]["invalid_candidate_count"]
    assert total_constraints == 45
    assert total_invalid == 0


def test_atomic_migration_replaces_every_legacy_mixed_constraint() -> None:
    migration = _load(MIGRATION_PATH)
    assert len(migration["migrations"]) == 2
    assert all(len(row["replacement_candidates"]) == 2 for row in migration["migrations"])
    for path in sorted(CASE_DIR.glob("*.json")):
        _packet, _source, _catalog, extractions, _ledger, _compiled, _result = _case(path)
        assert all(
            item.claim_mode != "mixed"
            for item in extractions["constraints"].constraints
        )


def test_joint_position_without_both_speakers_is_quarantined() -> None:
    path = CASE_DIR / "amb1-case03-creative-partnership.json"
    _packet, _source, catalog, extractions, _ledger, _compiled, _result = _case(path)
    position = extractions["positions"].positions[0]
    user_only = tuple(
        item
        for item in position.contributions
        if catalog.by_id()[item.evidence.span_id].speaker == "user"
    )
    broken_position = replace(position, ownership="joint", contributions=user_only)
    broken = dict(extractions)
    broken["positions"] = PositionExtraction(
        status="supported",
        decision_summary=extractions["positions"].decision_summary,
        positions=(broken_position,),
    )
    ledger = build_candidate_ledger(
        case_id="amb1-case03-creative-partnership",
        catalog=catalog,
        extractions=broken,
    )
    compiled, result = compile_handoff_from_ledger(ledger=ledger, catalog=catalog)
    assert compiled is None
    assert result["status"] == "quarantined"
    assert result["accepted_observed_path_allowed"] is False
    invalid = [
        row for row in ledger["candidates"] if row["terminal_state"] == "invalid_evidence"
    ]
    assert len(invalid) == 1
    assert invalid[0]["validation_issues"][0]["code"] == (
        "joint_position_requires_both_speakers"
    )
    assert invalid[0]["event_snapshot"] is None


def test_noncontiguous_quote_never_receives_current_view_or_observed_path() -> None:
    path = CASE_DIR / "amb1-case03-creative-partnership.json"
    _packet, _source, catalog, extractions, _ledger, _compiled, _result = _case(path)
    constraint = extractions["constraints"].constraints[0]
    turn_span = next(
        span
        for span in catalog.spans
        if span.turn_index == 3 and span.speaker == "user" and span.kind == "turn"
    )
    joined = (
        "the participant approved a cut three months ago. "
        "She also told us she did not want to supervise every edit."
    )
    broken_constraint = replace(
        constraint,
        evidence=(EvidenceRef(span_id=turn_span.span_id, excerpt=joined),),
    )
    broken = dict(extractions)
    broken["constraints"] = replace(
        extractions["constraints"], constraints=(broken_constraint,)
    )
    ledger = build_candidate_ledger(
        case_id="amb1-case03-creative-partnership",
        catalog=catalog,
        extractions=broken,
    )
    compiled, result = compile_handoff_from_ledger(ledger=ledger, catalog=catalog)
    assert compiled is None
    assert result["accepted_observed_path_allowed"] is False
    invalid = next(
        row for row in ledger["candidates"] if row["terminal_state"] == "invalid_evidence"
    )
    assert invalid["event_snapshot"] is None
    assert invalid["validation_issues"][0]["code"] == "source_excerpt_not_exact"


def test_not_found_is_preserved_as_absence_and_does_not_force_compilation() -> None:
    path = CASE_DIR / "amb1-case03-creative-partnership.json"
    _packet, _source, catalog, extractions, _ledger, _compiled, _result = _case(path)
    absent = dict(extractions)
    absent["positions"] = PositionExtraction(
        status="not_found", decision_summary=None, positions=()
    )
    ledger = build_candidate_ledger(
        case_id="amb1-case03-creative-partnership",
        catalog=catalog,
        extractions=absent,
    )
    compiled, result = compile_handoff_from_ledger(ledger=ledger, catalog=catalog)
    assert compiled is None
    assert result["reason"] == "decision_or_position_projection_incomplete"
    assert ledger["family_outcomes"]["positions"]["absence_is_observed"] is True
    assert ledger["family_outcomes"]["decision_summary"]["absence_is_observed"] is True
