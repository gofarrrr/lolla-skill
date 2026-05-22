from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_step6_card_deck import (  # noqa: E402
    CARD_DECK_RENDER_MAX_CHARS,
    build_step6_card_deck,
    render_step6_card_deck,
    validate_step6_card_deck_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_card_deck_passes_clean_hybrid_bevelin_and_polya_without_selecting() -> None:
    payload = build_step6_card_deck(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
    )

    validate_step6_card_deck_payload(payload)
    cards = payload["cards"]
    assert [card["card_id"] for card in cards] == [
        "clean_hybrid_card",
        "bevelin_card",
        "polya_card",
    ]
    assert payload["deterministic_limit"] == (
        "Code validates custody, labels sources, and renders the deck; it does not decide cognitive usefulness."
    )
    assert payload["problem_read"]["user_goal"]
    assert payload["problem_read"]["knowns"]
    assert payload["problem_read"]["constraints"]
    assert payload["step6_consideration_contract"]["decision_authority"] == (
        "Step 6 may use, reject, defer, or combine any card after serious consideration."
    )
    novelty_discipline = payload["step6_consideration_contract"]["novelty_discipline"]
    assert "additive pressure" in novelty_discipline
    assert "confirming support" in novelty_discipline
    assert "keep it private" in novelty_discipline
    assert all(card["selection_status"] == "presented_not_selected" for card in cards)
    assert "winner" not in json.dumps(payload).lower()
    assert "best option" not in json.dumps(payload).lower()


def test_card_deck_renderer_makes_step6_aware_and_preserves_private_labels() -> None:
    payload = build_step6_card_deck(
        case_id="third-year-phd-student.v2",
        repo_root=REPO_ROOT,
    )

    rendered = render_step6_card_deck(payload)

    assert len(rendered) <= CARD_DECK_RENDER_MAX_CHARS
    assert "STEP 6 PRIVATE CARD DECK" in rendered
    assert "Clean hybrid anchor" in rendered
    assert "PROBLEM READ" in rendered
    assert "Choose a PhD path" in rendered
    assert "Bevelin private card" in rendered
    assert "Polya private card" in rendered
    assert "hints, not commands" in rendered
    assert "strongest plausible application" in rendered
    assert "go beyond the obvious" in rendered
    assert "additive pressure" in rendered
    assert "confirming support" in rendered
    assert "Do not expose these private labels" in rendered


def test_card_deck_preserves_all_lens_receipts_instead_of_pruning_by_overlap() -> None:
    payload = build_step6_card_deck(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
    )
    by_id = {card["card_id"]: card for card in payload["cards"]}

    assert by_id["bevelin_card"]["receipts"] == [
        "Makes incentive and dependency-system pressure more explicit.",
        "Adds the test of whether Marcus makes the company stronger beyond himself.",
        "Sharpens irreversible commitment before proof as the central danger.",
    ]
    assert by_id["polya_card"]["receipts"] == [
        "Frames the problem as defining what evidence would justify irreversible rights.",
        "Simplifies Friday into the next real test rather than a full instrument design.",
        "Adds a look-back check on what kind of company would be sold.",
    ]
    assert all(
        receipt["deterministic_overlap_hint"]
        in {"literal_phrase_present_in_anchor", "not_a_literal_phrase_match"}
        for card in payload["cards"]
        for receipt in card.get("receipt_annotations", [])
    )
