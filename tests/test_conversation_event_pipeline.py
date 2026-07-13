import json
from pathlib import Path

import pytest

from engine.system_b.conversation_event_harvesting import (
    ContributionEvent,
    ContributionHarvest,
    SpanSelection,
    SynthesizedContribution,
    build_turn_pair_windows,
)
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


ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "research/conversation-state-handoff-v1-2026-07-10/cases"
MIGRATION = ROOT / "research/conversation-state-recovery-v1-2026-07-11/atomic-migration.json"


def _case(path: Path):
    packet = json.loads(path.read_text())
    source_path = ROOT / packet["source"]["path"]
    source_text = source_path.read_text()
    catalog = build_source_catalog(
        source_text=source_text, source_path=packet["source"]["path"]
    )
    return packet, source_text, catalog


def test_cross_window_source_id_is_quarantined_and_every_proposal_has_terminal_custody():
    packet, _source_text, catalog = _case(sorted(CASE_DIR.glob("*.json"))[0])
    windows = build_turn_pair_windows(catalog)
    outside_id = windows[1].span_ids[0]
    harvests = {}
    for family in ("contributions", "thread_events", "constraint_claims"):
        for window in windows:
            if family == "contributions" and window == windows[0]:
                harvests[(family, window.window_id)] = ContributionHarvest(
                    status="supported",
                    events=(
                        ContributionEvent(
                            position_fragment="candidate",
                            evidence=(SpanSelection(outside_id),),
                        ),
                    ),
                )
            else:
                classes = {
                    "contributions": __import__(
                        "engine.system_b.conversation_event_harvesting", fromlist=["ContributionHarvest"]
                    ).ContributionHarvest,
                    "thread_events": __import__(
                        "engine.system_b.conversation_event_harvesting", fromlist=["ThreadEventHarvest"]
                    ).ThreadEventHarvest,
                    "constraint_claims": __import__(
                        "engine.system_b.conversation_event_harvesting", fromlist=["ConstraintClaimHarvest"]
                    ).ConstraintClaimHarvest,
                }
                harvests[(family, window.window_id)] = classes[family](status="not_found", events=())
    ledger = build_event_ledger(
        case_id=packet["case_id"], catalog=catalog, windows=windows, harvests=harvests
    )
    assert ledger["metrics"]["proposal_count"] == 1
    assert ledger["metrics"]["terminal_record_count"] == 1
    assert ledger["metrics"]["candidate_custody_complete"] is True
    assert ledger["events"][0]["terminal_state"] == "invalid_evidence"
    assert ledger["events"][0]["event_snapshot"] is None
    assert ledger["events"][0]["validation_issues"][0]["code"] == "source_span_outside_window"


@pytest.mark.parametrize("case_path", sorted(CASE_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_reviewed_projection_survives_harvest_synthesis_and_compile_without_graph_leak(case_path):
    packet, source_text, catalog = _case(case_path)
    migration = json.loads(MIGRATION.read_text())
    windows = build_turn_pair_windows(catalog)
    harvests, projection = reviewed_event_projection(
        packet=packet,
        catalog=catalog,
        windows=windows,
        atomic_migrations=migration,
    )
    assert len(harvests) == len(windows) * 3
    event_ledger = build_event_ledger(
        case_id=packet["case_id"], catalog=catalog, windows=windows, harvests=harvests
    )
    assert event_ledger["metrics"]["missing_harvest_count"] == 0
    assert event_ledger["metrics"]["invalid_event_count"] == 0
    assert event_ledger["metrics"]["candidate_custody_complete"] is True
    assert all(row["terminal_state"] for row in event_ledger["events"])

    syntheses = reviewed_fresh_syntheses(
        event_ledger=event_ledger, projection=projection
    )
    synthesis_ledger = build_synthesis_ledger(
        case_id=packet["case_id"], event_ledger=event_ledger, syntheses=syntheses
    )
    assert synthesis_ledger["metrics"]["invalid_synthesis_count"] == 0
    assert synthesis_ledger["metrics"]["candidate_custody_complete"] is True
    compiled, result = compile_handoff_from_event_ledgers(
        event_ledger=event_ledger,
        synthesis_ledger=synthesis_ledger,
        catalog=catalog,
    )
    assert result["status"] == "compiled"
    assert result["graph_routing_allowed"] is False
    assert compiled is not None
    assert validate_conversation_state_handoff(compiled, source_text=source_text) == []
    boundary = build_fact_free_routing_boundary(compiled)
    assert boundary["direct_graph_seed_count"] == 0
    assert boundary["reasoning_pattern_inputs"] == []
    assert [row["text"] for row in compiled["positions"]] == [row["text"] for row in packet["positions"]]
    assert [row["ownership"] for row in compiled["positions"]] == [row["ownership"] for row in packet["positions"]]
    assert [row["disposition"] for row in compiled["threads"]] == [row["disposition"] for row in packet["threads"]]
    expected_constraints = len(packet["constraints"]) + sum(
        len(row["replacement_candidates"]) - 1
        for row in migration["migrations"]
        if row["case_id"] == packet["case_id"]
    )
    assert len(compiled["constraints"]) == expected_constraints
    assert all(row["claim_mode"] != "mixed" for row in compiled["constraints"])


def test_unknown_synthesis_event_reference_is_quarantined():
    packet, _source_text, catalog = _case(sorted(CASE_DIR.glob("*.json"))[0])
    migration = json.loads(MIGRATION.read_text())
    windows = build_turn_pair_windows(catalog)
    harvests, projection = reviewed_event_projection(
        packet=packet, catalog=catalog, windows=windows, atomic_migrations=migration
    )
    event_ledger = build_event_ledger(
        case_id=packet["case_id"], catalog=catalog, windows=windows, harvests=harvests
    )
    syntheses = reviewed_fresh_syntheses(event_ledger=event_ledger, projection=projection)
    position = syntheses["positions"].positions[0]
    bad = type(position)(
        text=position.text,
        ownership=position.ownership,
        state=position.state,
        contributions=(
            SynthesizedContribution(
                event_id="not-a-ledger-event", role="originated"
            ),
        ),
    )
    syntheses["positions"] = type(syntheses["positions"])(
        status="supported",
        decision_summary=syntheses["positions"].decision_summary,
        positions=(bad,),
    )
    synthesis_ledger = build_synthesis_ledger(
        case_id=packet["case_id"], event_ledger=event_ledger, syntheses=syntheses
    )
    assert synthesis_ledger["metrics"]["invalid_synthesis_count"] == 1
    compiled, result = compile_handoff_from_event_ledgers(
        event_ledger=event_ledger, synthesis_ledger=synthesis_ledger, catalog=catalog
    )
    assert compiled is None
    assert result["status"] == "quarantined"
    assert result["reason"] == "invalid_synthesis_references_present"


def test_absence_and_ambiguity_are_explicit_observed_outcomes():
    packet, _source_text, catalog = _case(sorted(CASE_DIR.glob("*.json"))[0])
    windows = build_turn_pair_windows(catalog)
    from engine.system_b.conversation_event_harvesting import (
        ConstraintClaimHarvest,
        ThreadEventHarvest,
    )

    harvests = {}
    for family in ("contributions", "thread_events", "constraint_claims"):
        for window in windows:
            if family == "contributions":
                value = ContributionHarvest(status="unclear", events=())
            elif family == "thread_events":
                value = ThreadEventHarvest(status="not_found", events=())
            else:
                value = ConstraintClaimHarvest(status="not_found", events=())
            harvests[(family, window.window_id)] = value
    ledger = build_event_ledger(
        case_id=packet["case_id"], catalog=catalog, windows=windows, harvests=harvests
    )
    assert sum(row["ambiguity_is_observed"] for row in ledger["family_window_outcomes"]) == 7
    assert sum(row["absence_is_observed"] for row in ledger["family_window_outcomes"]) == 14
    assert ledger["metrics"]["proposal_count"] == 0
    assert ledger["metrics"]["candidate_custody_complete"] is True


def test_compiler_quarantines_an_incomplete_synthesis_matrix():
    packet, _source_text, catalog = _case(sorted(CASE_DIR.glob("*.json"))[0])
    migration = json.loads(MIGRATION.read_text())
    windows = build_turn_pair_windows(catalog)
    harvests, projection = reviewed_event_projection(
        packet=packet, catalog=catalog, windows=windows, atomic_migrations=migration
    )
    event_ledger = build_event_ledger(
        case_id=packet["case_id"], catalog=catalog, windows=windows, harvests=harvests
    )
    syntheses = reviewed_fresh_syntheses(event_ledger=event_ledger, projection=projection)
    del syntheses["threads"]
    synthesis_ledger = build_synthesis_ledger(
        case_id=packet["case_id"], event_ledger=event_ledger, syntheses=syntheses
    )
    compiled, result = compile_handoff_from_event_ledgers(
        event_ledger=event_ledger, synthesis_ledger=synthesis_ledger, catalog=catalog
    )
    assert compiled is None
    assert result["reason"] == "synthesis_matrix_incomplete"
