import json
from dataclasses import asdict
from pathlib import Path

from engine.system_b.conversation_event_harvesting import (
    FAMILIES,
    ContributionHarvest,
    build_harvest_contract,
    build_synthesis_contract,
    build_turn_pair_windows,
    harvest_schema,
    parse_harvest,
    synthesis_schema,
)
from engine.system_b.conversation_state_candidates import build_source_catalog


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/amb1-case01-product-scope.txt"


def _catalog():
    text = SOURCE.read_text()
    return build_source_catalog(source_text=text, source_path=str(SOURCE.relative_to(ROOT)))


def test_turn_pair_windows_cover_all_sentence_spans_without_overlap():
    catalog = _catalog()
    windows = build_turn_pair_windows(catalog)
    expected = [span.span_id for span in catalog.spans]
    observed = [span_id for window in windows for span_id in window.span_ids]
    assert len(windows) == 7
    assert observed == expected
    assert len(observed) == len(set(observed))
    assert all("USER [" in window.source_text and "ASSISTANT [" in window.source_text for window in windows)


def test_harvest_schemas_constrain_span_ids_to_one_window_and_never_request_excerpts():
    window = build_turn_pair_windows(_catalog())[0]
    for family in FAMILIES:
        schema = harvest_schema(family, window=window)
        encoded = json.dumps(schema, sort_keys=True)
        assert '"enum": ' in encoded
        assert set(window.span_ids) <= set(encoded.split('"'))
        assert "excerpt" not in encoded.lower()
        assert "source_text" not in encoded
        contract = build_harvest_contract(family, window=window)
        assert contract["provider_calls"] == 0
        assert "Return stable span IDs only" in contract["system_prompt"]
        assert contract["window_id"] == window.window_id


def test_synthesis_schemas_only_accept_current_ledger_event_ids():
    event_ids = ["event-a", "event-b"]
    for family in ("positions", "threads", "constraints"):
        schema = synthesis_schema(family, event_ids=event_ids)
        encoded = json.dumps(schema, sort_keys=True)
        assert '"event-a"' in encoded and '"event-b"' in encoded
        assert "span_id" not in encoded
        assert "excerpt" not in encoded.lower()


def test_not_found_is_a_valid_typed_harvest_outcome():
    parsed, issues = parse_harvest(
        "contributions", {"status": "not_found", "events": []}
    )
    assert issues == []
    assert parsed == ContributionHarvest(status="not_found", events=())
    assert asdict(parsed) == {"status": "not_found", "events": ()}


def test_fresh_synthesis_contract_uses_ordered_ledger_and_constraints_stay_claim_scoped():
    ledger = {
        "events": [
            {
                "event_id": "event-contribution",
                "family": "contributions",
                "window_id": "window-001",
                "turn_index": 1,
                "synthesis_eligible": True,
                "event_snapshot": {
                    "position_fragment": "try the option",
                    "evidence": [{"span_id": "span-a"}],
                    "resolved_source": [{"span_id": "span-a", "speaker": "user", "turn_index": 1, "text": "Try the option."}],
                },
            },
            {
                "event_id": "event-claim",
                "family": "constraint_claims",
                "window_id": "window-001",
                "turn_index": 1,
                "synthesis_eligible": True,
                "event_snapshot": {
                    "claim_text": "The deadline is Friday.",
                    "evidence": {"span_id": "span-b"},
                    "resolved_source": [{"span_id": "span-b", "speaker": "user", "turn_index": 1, "text": "The deadline is Friday."}],
                },
            },
        ]
    }
    positions = build_synthesis_contract("positions", event_ledger=ledger)
    constraints = build_synthesis_contract("constraints", event_ledger=ledger)
    assert positions["event_ids"] == ["event-contribution", "event-claim"]
    assert constraints["event_ids"] == ["event-claim"]
    assert "prior model prose" not in positions["user_prompt"].lower()
    assert positions["provider_calls"] == 0
