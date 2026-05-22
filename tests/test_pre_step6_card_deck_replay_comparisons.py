from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_card_deck_replay_comparisons import (  # noqa: E402
    ReplayComparisonValidationError,
    build_replay_comparison_packet,
    build_reviewer_packet,
    validate_replay_comparison_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_replay_comparison_packet_blinds_clean_hybrid_and_card_deck_replay() -> None:
    packet = build_replay_comparison_packet(
        case_id="third-year-phd-student.v2",
        repo_root=REPO_ROOT,
        seed=2026052003,
    )

    assert packet["case_id"] == "third-year-phd-student.v2"
    assert set(packet["candidates_by_label"]) == {"A", "B"}
    assert set(packet["blind_map"].values()) == {"clean_hybrid", "card_deck_replay"}
    candidate_blob = json.dumps(packet["candidates_by_label"]).lower()
    assert "card_deck" not in candidate_blob
    assert "clean_hybrid" not in candidate_blob
    assert "private_card_consideration_ledger" not in candidate_blob
    assert "without rewarding bloat" in json.dumps(packet).lower()

    reviewer_packet = build_reviewer_packet(packet)
    reviewer_blob = json.dumps(reviewer_packet).lower()
    assert "card_deck" not in reviewer_blob
    assert "card-deck" not in reviewer_blob
    assert "clean_hybrid" not in reviewer_blob
    assert "clean hybrid" not in reviewer_blob
    assert "deck_effect" not in reviewer_blob


def test_replay_comparison_payload_validates_cognitive_judgment() -> None:
    packet = build_replay_comparison_packet(
        case_id="third-year-phd-student.v2",
        repo_root=REPO_ROOT,
        seed=2026052003,
    )
    deck_label = next(
        label
        for label, arm in packet["blind_map"].items()
        if arm == "card_deck_replay"
    )
    payload = {
        "schema_version": "pre_step6_card_deck_replay_comparison.v1",
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": "third-year-phd-student.v2",
        "comparison_kind": "clean_hybrid_vs_card_deck_replay",
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": {
            "provider": "test",
            "model": "fixture",
            "status": "ok",
            "prompt_tokens": 1,
            "completion_tokens": 1,
            "total_tokens": 2,
        },
        "candidate_refs": packet["candidate_refs"],
        "blind_map": packet["blind_map"],
        "reviewer_output": {
            "winner_label": deck_label,
            "deck_effect": "improves",
            "confidence": "medium",
            "rationale": "The deck replay keeps the same decision but makes the test window and fallback gate sharper.",
            "visible_improvements": ["Clearer evidence gate."],
            "visible_regressions_or_bloat": ["No meaningful bloat."],
            "recommendation": "Retest the card-deck replay on adjacent cases.",
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Fixture comparison.",
    }

    validate_replay_comparison_payload(payload)


def test_replay_comparison_rejects_winner_effect_contradiction() -> None:
    packet = build_replay_comparison_packet(
        case_id="mother-address-year",
        repo_root=REPO_ROOT,
        seed=2026052003,
    )
    deck_label = next(
        label
        for label, arm in packet["blind_map"].items()
        if arm == "card_deck_replay"
    )
    payload = {
        "schema_version": "pre_step6_card_deck_replay_comparison.v1",
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": "mother-address-year",
        "comparison_kind": "clean_hybrid_vs_card_deck_replay",
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": {
            "provider": "test",
            "model": "fixture",
            "status": "ok",
        },
        "candidate_refs": packet["candidate_refs"],
        "blind_map": packet["blind_map"],
        "reviewer_output": {
            "winner_label": deck_label,
            "deck_effect": "regresses",
            "confidence": "medium",
            "rationale": "The selected answer is better, but the deck somehow regressed.",
            "visible_improvements": ["Selected answer is clearer."],
            "visible_regressions_or_bloat": ["Contradictory fixture."],
            "recommendation": "Reject this artifact.",
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
    }

    with pytest.raises(ReplayComparisonValidationError, match="deck_effect"):
        validate_replay_comparison_payload(payload)
