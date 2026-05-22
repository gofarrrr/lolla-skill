from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_card_deck_replays import (  # noqa: E402
    build_step6_replay_prompts,
    validate_card_deck_replay_payload,
)
from pre_step6_step6_card_deck import build_step6_card_deck  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_step6_replay_prompt_passes_full_deck_and_requires_private_ledger() -> None:
    deck = build_step6_card_deck(
        case_id="third-year-phd-student.v2",
        repo_root=REPO_ROOT,
    )

    prompts = build_step6_replay_prompts(deck)

    assert "Clean hybrid anchor" in prompts["user_prompt"]
    assert "Bevelin private card" in prompts["user_prompt"]
    assert "Polya private card" in prompts["user_prompt"]
    assert "private_card_consideration_ledger" in prompts["user_prompt"]
    assert "use, reject, defer, or combine" in prompts["user_prompt"]
    assert "do not expose these private labels" in prompts["user_prompt"].lower()
    assert "as short as possible, but no shorter" in prompts["user_prompt"]
    assert "Do not compress away" in prompts["user_prompt"]
    assert "anchor can remain the visible backbone" in prompts["user_prompt"]
    assert "additive pressure" in prompts["user_prompt"]
    assert "confirming support" in prompts["user_prompt"]
    assert "private guardrail" in prompts["user_prompt"]
    assert "novelty_role" in prompts["user_prompt"]
    assert "visible_backbone" in prompts["user_prompt"]
    assert "The ledger is where card consideration lives" in prompts["user_prompt"]
    assert "Do not lengthen the public answer" in prompts["user_prompt"]
    assert "sensitive safety or legal context" in prompts["user_prompt"]
    assert "concrete safeguard, tripwire, or channel distinction" in prompts["user_prompt"]
    assert "Do not shorten by deleting concrete anchor payload" in prompts["user_prompt"]
    assert "named channels or resources" in prompts["user_prompt"]
    assert "communication boundaries" in prompts["user_prompt"]
    assert "Preserve structural separation" in prompts["user_prompt"]
    assert "Do not use public machinery terms" in prompts["user_prompt"]
    assert "bundle" in prompts["user_prompt"]
    assert "lane" in prompts["user_prompt"]


def test_card_deck_replay_payload_validates_step6_decision_not_code_selection() -> None:
    payload = {
        "schema_version": "pre_step6_card_deck_replay.v1",
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": "third-year-phd-student.v2",
        "replay_mode": "manual_live_step6_from_card_deck",
        "source_card_deck": (
            "research/pre-step6-step6-card-decks/"
            "third-year-phd-student.v2.step6-card-deck.v1.json"
        ),
        "provider_metadata": {
            "provider": "test",
            "model": "fixture",
            "status": "ok",
            "prompt_tokens": 1,
            "completion_tokens": 1,
            "total_tokens": 2,
        },
        "step6_output": {
            "answer_core": (
                "I would not choose the Silva direction yet, and I would not default to "
                "the safer lab path. Treat both as live gates: Silva executability and "
                "fallback survivability."
            ),
            "private_card_consideration_ledger": [
                {
                    "card_id": "clean_hybrid_card",
                    "disposition": "used",
                    "novelty_role": "visible_backbone",
                    "why": "It preserved the concrete two-gate structure.",
                    "visible_effect": "Kept Silva and fallback alive together.",
                },
                {
                    "card_id": "bevelin_card",
                    "disposition": "used",
                    "novelty_role": "additive_pressure",
                    "why": "It sharpened premature commitment and inversion pressure.",
                    "visible_effect": "Added stop-loss pressure.",
                },
                {
                    "card_id": "polya_card",
                    "disposition": "deferred",
                    "novelty_role": "confirming_support",
                    "why": "Its sequencing was mostly already represented.",
                    "visible_effect": "Kept as private check only.",
                },
            ],
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Fixture replay.",
    }

    validate_card_deck_replay_payload(payload, repo_root=REPO_ROOT)
