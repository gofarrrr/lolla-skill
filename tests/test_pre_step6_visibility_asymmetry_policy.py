from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_visibility_asymmetry_policy import (  # noqa: E402
    build_visibility_asymmetry_policy,
    load_visibility_asymmetry_payload,
    validate_visibility_asymmetry_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_tie_or_unresolved_defaults_anchor_visible_without_reviewer_loop() -> None:
    payload = build_visibility_asymmetry_policy(
        case_id="runtime-unresolved",
        mode="runtime",
        ledger_signal="additive_pressure_present",
        reviewer_signal="not_run",
    )

    validate_visibility_asymmetry_payload(payload)

    assert payload["runtime_asymmetry"]["private_default"] == "deck_private"
    assert payload["runtime_asymmetry"]["public_bias"] == "anchor_visible_when_unresolved"
    assert payload["retest_policy"]["allowed"] is False
    assert payload["retest_policy"]["normal_runtime_reviewer_calls"] == 0
    assert payload["visible_policy"]["result"] == "anchor_visible_deck_private"
    assert payload["visible_policy"]["false_standdown_risk"] == "primary_runtime_failure_mode"


def test_research_tie_gets_one_bounded_retest_with_second_reviewer_spec() -> None:
    payload = build_visibility_asymmetry_policy(
        case_id="research-tie",
        mode="research",
        ledger_signal="additive_pressure_present",
        reviewer_signal="tie",
    )

    validate_visibility_asymmetry_payload(payload)

    assert payload["visible_policy"]["result"] == "retest_required"
    assert payload["retest_policy"]["allowed"] is True
    assert payload["retest_policy"]["max_retests"] == 1
    assert payload["retest_policy"]["deck_visible_threshold"] == "second_reviewer_prefers_deck"
    assert payload["retest_policy"]["non_inferior_deck_result"] == "keep_for_research_only"


def test_research_deck_visible_requires_additive_ledger_and_deck_confirmation() -> None:
    payload = build_visibility_asymmetry_policy(
        case_id="research-deck-confirmed",
        mode="research",
        ledger_signal="additive_pressure_present",
        reviewer_signal="deck_confirmed",
    )

    validate_visibility_asymmetry_payload(payload)

    assert payload["visible_policy"]["result"] == "card_deck_visible_after_aligned_signals"
    assert payload["visible_policy"]["why"] == (
        "Step 6 found additive pressure and cognitive comparison preferred the deck."
    )


def test_research_ledger_reviewer_disagreement_retests_instead_of_selecting() -> None:
    payload = build_visibility_asymmetry_policy(
        case_id="research-disagreement",
        mode="research",
        ledger_signal="all_private_or_confirming",
        reviewer_signal="deck_confirmed",
    )

    validate_visibility_asymmetry_payload(payload)

    assert payload["visible_policy"]["result"] == "retest_required"
    assert payload["visible_policy"]["why"] == (
        "Ledger and cognitive comparison disagree; research mode may retest once."
    )


def test_visibility_asymmetry_fixture_suite_validates() -> None:
    fixture_dir = REPO_ROOT / "research" / "pre-step6-visibility-asymmetry-policies"
    paths = sorted(fixture_dir.glob("*.visibility-asymmetry.v1.json"))

    assert [path.name for path in paths] == [
        "anchor-confirmed.visibility-asymmetry.v1.json",
        "deck-confirmed.visibility-asymmetry.v1.json",
        "ledger-reviewer-disagreement.visibility-asymmetry.v1.json",
        "runtime-unresolved.visibility-asymmetry.v1.json",
        "tie-retest.visibility-asymmetry.v1.json",
    ]
    for path in paths:
        validate_visibility_asymmetry_payload(load_visibility_asymmetry_payload(path), path=path)
