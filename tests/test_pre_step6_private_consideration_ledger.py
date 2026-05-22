from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_private_consideration_ledger import (  # noqa: E402
    REQUIRED_LEDGER_ITEM_FIELDS,
    build_ledger_overlap_fixture,
    build_non_overlap_fixture,
    build_v60_only_fixture,
    load_ledger_overlap_payload,
    validate_ledger_overlap_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_overlap_fixture_dedupes_hot_context_but_preserves_card_and_v60_custody() -> None:
    payload = build_ledger_overlap_fixture(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
    )

    validate_ledger_overlap_payload(payload)

    assert payload["overlap_groups"] == [
        {
            "overlap_group_id": "founder_overcommitment_without_evidence_001",
            "primary_presented_item_id": "reasoning_card:bevelin_card",
            "supporting_item_refs": [
                "reasoning_card:bevelin_card",
                "v60_chunk:overcommitment_without_evidence",
            ],
            "presentation_policy": "single_representative_with_supporting_refs",
            "ledger_policy": "all_source_items_preserved",
        }
    ]
    assert [item["item_id"] for item in payload["hot_context_items"]] == [
        "reasoning_card:bevelin_card"
    ]
    assert [item["item_id"] for item in payload["ledger_items"]] == [
        "reasoning_card:bevelin_card",
        "v60_chunk:overcommitment_without_evidence",
    ]
    assert all(set(item) == REQUIRED_LEDGER_ITEM_FIELDS for item in payload["ledger_items"])
    assert payload["ledger_items"][1]["presentation_state"] == "supporting_ref_not_repeated"
    assert payload["deterministic_limit"] == (
        "Code groups overlap and preserves custody; Step 6 still decides usefulness."
    )


def test_ledger_overlap_fixed_fixture_validates() -> None:
    path = (
        REPO_ROOT
        / "research"
        / "pre-step6-private-consideration-ledgers"
        / "founder-grant-marcus-equity.high-clutter.ledger-overlap.v1.json"
    )
    payload = load_ledger_overlap_payload(path)

    validate_ledger_overlap_payload(payload, path=path)

    assert payload["status"] == "research_only"
    assert payload["runtime_policy"] == "runtime_dormant"
    assert payload["gates"]["runtime_wiring_allowed"] is False


def test_non_overlap_fixture_keeps_card_and_v60_items_in_hot_context() -> None:
    payload = build_non_overlap_fixture(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
    )

    validate_ledger_overlap_payload(payload)

    assert payload["overlap_groups"] == []
    assert [item["item_id"] for item in payload["hot_context_items"]] == [
        "reasoning_card:polya_card",
        "v60_chunk:absence_blocker_false_precision",
    ]
    assert payload["hot_context_items"] == payload["ledger_items"]
    assert all(item["overlap_group_id"] == "" for item in payload["ledger_items"])
    assert all(item["presentation_state"] == "primary_presented" for item in payload["ledger_items"])


def test_v60_only_fixture_validates_without_card_deck() -> None:
    payload = build_v60_only_fixture(case_id="synthetic-v60-only")

    validate_ledger_overlap_payload(payload)

    assert payload["source_refs"]["private_reasoning_cards"] == ""
    assert payload["overlap_groups"] == []
    assert [item["item_id"] for item in payload["ledger_items"]] == [
        "v60_chunk:standalone_margin_of_safety"
    ]
    assert payload["hot_context_items"] == payload["ledger_items"]
    assert payload["ledger_items"][0]["item_type"] == "v60_chunk"


def test_ledger_shape_fixture_files_validate() -> None:
    fixture_dir = REPO_ROOT / "research" / "pre-step6-private-consideration-ledgers"
    paths = sorted(fixture_dir.glob("*.ledger-overlap.v1.json"))

    assert [path.name for path in paths] == [
        "founder-grant-marcus-equity.high-clutter.ledger-overlap.v1.json",
        "founder-grant-marcus-equity.high-clutter.non-overlap.ledger-overlap.v1.json",
        "synthetic-v60-only.ledger-overlap.v1.json",
    ]
    for path in paths:
        validate_ledger_overlap_payload(load_ledger_overlap_payload(path), path=path)
