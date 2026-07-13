from pathlib import Path

from engine.system_b.conversation_event_harvesting import (
    SpanSelection,
    build_turn_pair_windows,
)
from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.conversation_turn_records import (
    ConversationTurnRecord,
    InputDisposition,
    LocalAtomicClaim,
    LocalDirectionalMove,
    LocalThreadSignal,
    build_consolidator_contract,
    build_single_reader_contract,
    build_turn_record_ledger,
    parse_turn_record,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/amb1-case01-product-scope.txt"


def _source():
    text = SOURCE.read_text()
    catalog = build_source_catalog(source_text=text, source_path=str(SOURCE.relative_to(ROOT)))
    return catalog, build_turn_pair_windows(catalog)


def test_single_reader_contract_is_bounded_and_source_id_only():
    _catalog, windows = _source()
    contract = build_single_reader_contract(window=windows[0])
    schema = contract["schema"]
    assert schema["properties"]["directional_moves"]["maxItems"] == 2
    assert schema["properties"]["thread_signals"]["maxItems"] == 2
    assert schema["properties"]["claims"]["maxItems"] == 4
    assert set(schema["$defs"]["SpanSelection"]["properties"]["span_id"]["enum"]) == set(windows[0].span_ids)
    assert "global ownership" in contract["system_prompt"]
    assert "excerpt" not in str(schema).lower()
    assert contract["provider_calls"] == 0


def test_consolidator_contract_accounts_for_only_current_window_inputs():
    _catalog, windows = _source()
    inputs = [
        {"event_id": "event-a", "family": "contributions", "event_snapshot": {"text": "a"}},
        {"event_id": "event-b", "family": "thread_events", "event_snapshot": {"text": "b"}},
    ]
    contract = build_consolidator_contract(window=windows[0], input_events=inputs)
    enum = contract["schema"]["$defs"]["InputDisposition"]["properties"]["input_event_id"]["enum"]
    assert enum == ["event-a", "event-b"]
    assert contract["input_event_ids"] == enum
    assert "Account for every input event exactly once" in contract["system_prompt"]


def test_turn_record_parses_local_claim_strength_without_global_labels():
    catalog, windows = _source()
    span_id = windows[0].span_ids[1]
    payload = {
        "status": "supported",
        "directional_moves": [{"text": "Investigate first.", "evidence": [{"span_id": span_id}]}],
        "thread_signals": [],
        "claims": [{"text": "The team has nine people.", "claim_mode": "stated_condition", "evidence": {"span_id": span_id}}],
        "input_dispositions": [],
    }
    parsed, issues = parse_turn_record(payload)
    assert issues == []
    assert parsed is not None
    ledger = build_turn_record_ledger(
        architecture="single_reader",
        case_id="case",
        catalog=catalog,
        windows=windows,
        records={windows[0].window_id: parsed},
    )
    assert ledger["metrics"]["item_count"] == 2
    assert ledger["metrics"]["invalid_item_count"] == 0
    assert all(item["graph_routing_eligible"] is False for item in ledger["items"])


def test_cross_window_evidence_and_incomplete_input_custody_fail_closed():
    catalog, windows = _source()
    wrong_span = windows[1].span_ids[0]
    record = ConversationTurnRecord(
        status="supported",
        directional_moves=(LocalDirectionalMove("candidate", (SpanSelection(wrong_span),)),),
        thread_signals=(),
        claims=(),
        input_dispositions=(
            InputDisposition("event-a", "preserved", ("directional-1",)),
        ),
    )
    inputs = {
        windows[0].window_id: (
            {"event_id": "event-a"},
            {"event_id": "event-b"},
        )
    }
    ledger = build_turn_record_ledger(
        architecture="three_lens_consolidation",
        case_id="case",
        catalog=catalog,
        windows=windows,
        records={windows[0].window_id: record},
        input_events_by_window=inputs,
    )
    assert ledger["metrics"]["invalid_item_count"] == 1
    assert ledger["metrics"]["input_custody_invalid_window_count"] == 1
    assert ledger["items"][0]["event_snapshot"] is None


def test_not_found_and_unclear_records_remain_observed_without_items():
    catalog, windows = _source()
    records = {
        windows[0].window_id: ConversationTurnRecord("not_found", (), (), (), ()),
        windows[1].window_id: ConversationTurnRecord("unclear", (), (), (), ()),
    }
    ledger = build_turn_record_ledger(
        architecture="single_reader", case_id="case", catalog=catalog, windows=windows, records=records
    )
    assert ledger["records"][0]["absence_is_observed"] is True
    assert ledger["records"][1]["ambiguity_is_observed"] is True
    assert ledger["metrics"]["candidate_custody_complete"] is True
