from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_private_reasoning_cards import (  # noqa: E402
    REQUIRED_CARD_FIELDS,
    build_private_reasoning_card_interface,
    build_synthetic_future_card,
    load_private_reasoning_card_interface_payload,
    validate_private_reasoning_card_interface_payload,
    validate_private_reasoning_card_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_existing_card_deck_cards_validate_through_generic_interface() -> None:
    payload = build_private_reasoning_card_interface(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
    )

    validate_private_reasoning_card_interface_payload(payload)

    assert [card["card_id"] for card in payload["cards"]] == [
        "clean_hybrid_card",
        "bevelin_card",
        "polya_card",
    ]
    assert all(set(card) == REQUIRED_CARD_FIELDS for card in payload["cards"])
    by_id = {card["card_id"]: card for card in payload["cards"]}
    assert by_id["clean_hybrid_card"]["card_type"] == "anchor"
    assert by_id["bevelin_card"]["card_type"] == "lens"
    assert by_id["polya_card"]["card_type"] == "lens"
    assert by_id["bevelin_card"]["activation_scope"]
    assert by_id["bevelin_card"]["misuse_guard"]
    assert by_id["polya_card"]["standdown_condition"]
    assert payload["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_synthetic_future_card_validates_without_changing_policy_or_ledger_semantics() -> None:
    card = build_synthetic_future_card()

    validate_private_reasoning_card_payload(card)

    assert card["card_id"] == "future_decision_quality_card"
    assert card["card_type"] == "lens"
    assert card["source_kind"] == "synthetic_future_lens_fixture"
    assert "bevelin" not in card["card_id"]
    assert "polya" not in card["card_id"]
    assert "visible_policy" not in card
    assert "ledger_schema" not in card


def test_private_card_interface_fixed_suite_fixtures_validate() -> None:
    fixture_dir = REPO_ROOT / "research" / "pre-step6-private-reasoning-cards"
    paths = sorted(fixture_dir.glob("*.private-reasoning-cards.v1.json"))

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.private-reasoning-cards.v1.json",
        "mid-level-consultant-report-2.private-reasoning-cards.v1.json",
        "mother-address-year.private-reasoning-cards.v1.json",
        "third-year-phd-student.v2.private-reasoning-cards.v1.json",
    ]
    for path in paths:
        payload = load_private_reasoning_card_interface_payload(path)
        validate_private_reasoning_card_interface_payload(payload, path=path)
        assert payload["interface_read"]["bevelin_polya_special_cased"] is False
        assert payload["interface_read"]["new_card_requires_policy_change"] is False
        assert payload["interface_read"]["new_card_requires_ledger_change"] is False
