"""Tests for frame element empty-evidence rejection and drop tracking."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.conversation_context import ConversationContext, ExtractionPayload, Turn
from engine.system_b.frame_pressure import _parse_frame_extraction_from_packet
from engine.system_b.ir_constructor import construct_conversation_ir
from engine.system_b.packet_builders.lane4 import build_lane4_packet


QUERY = "Should I invest $50k in my friend's startup?"

VALID_ELEMENT = {
    "element_text": "Assumes friend's startup is the only investment option",
    "element_type": "assumption",
    "evidence_quote": "invest $50k in my friend's startup",
    "frame_pattern": "option_space_collapse",
    "fragility_signal": "What if there are better investment options?",
    "inquiry_stage": "what_if",
    "likely_default": "social",
}


def _make_raw(*items: dict) -> dict:
    return {"frame_elements": list(items)}


def _packet(query: str):
    ctx = ConversationContext(
        turns=(Turn(turn_index=1, speaker="user", text=query),),
        extraction=ExtractionPayload(
            decision_situation=query,
            live_constraints=(),
            synthesized_position="",
            reasoning_passages=(),
            original_framing=query,
            dropped_threads=(),
        ),
    )
    return build_lane4_packet(construct_conversation_ir(ctx))


def test_empty_evidence_quote_rejected():
    """An element with empty evidence_quote is not included in results."""
    bad = {**VALID_ELEMENT, "evidence_quote": ""}
    elements, dropped = _parse_frame_extraction_from_packet(_make_raw(VALID_ELEMENT, bad), _packet(QUERY))
    assert len(elements) == 1
    assert elements[0].element_text == VALID_ELEMENT["element_text"]
    assert len(dropped) == 1
    assert dropped[0]["drop_reason"] == "missing_evidence"


def test_empty_frame_pattern_rejected():
    """An element with empty frame_pattern is not included in results."""
    bad = {**VALID_ELEMENT, "frame_pattern": ""}
    elements, dropped = _parse_frame_extraction_from_packet(_make_raw(VALID_ELEMENT, bad), _packet(QUERY))
    assert len(elements) == 1
    assert len(dropped) == 1
    assert dropped[0]["drop_reason"] == "missing_pattern"


def test_dropped_elements_carry_element_text():
    """Dropped elements include the original element_text for debugging."""
    bad_ev = {**VALID_ELEMENT, "evidence_quote": "", "element_text": "Bad evidence element"}
    bad_pat = {**VALID_ELEMENT, "frame_pattern": "", "element_text": "Bad pattern element"}
    _, dropped = _parse_frame_extraction_from_packet(_make_raw(bad_ev, bad_pat), _packet(QUERY))
    assert len(dropped) == 2
    assert dropped[0]["element_text"] == "Bad evidence element"
    assert dropped[1]["element_text"] == "Bad pattern element"


def test_frame_pressure_card_carries_dropped_elements():
    """FramePressureCard.dropped_frame_elements carries the dropped list through."""
    from engine.system_b.frame_pressure import FramePressureCard

    dropped = ({"element_text": "test", "drop_reason": "missing_evidence"},)
    card = FramePressureCard(dropped_frame_elements=dropped)
    assert card.dropped_frame_elements == dropped
    payload = card.to_payload()
    assert payload["dropped_frame_elements"] == list(dropped)
