from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_visibility_policy_redesign import (  # noqa: E402
    build_visibility_policy_redesign,
    load_visibility_policy_redesign_payload,
    validate_visibility_policy_redesign_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_bridge_cases_move_from_legacy_anchor_suppression_to_ledger_mediated_deck_visible() -> None:
    payload = build_visibility_policy_redesign(
        case_id="bridge-sensitive-anchor-misses-tripwire",
        cache_state="cache_hit",
        step6_ledger_signal="additive_pressure_present",
        payload_gate_result="preserved",
        bridge_probe_label="false_standdown",
    )

    validate_visibility_policy_redesign_payload(payload)

    assert payload["legacy_policy"]["result"] == "anchor_visible_deck_private"
    assert payload["legacy_policy"]["would_suppress_deck"] is True
    assert payload["redesigned_policy"]["result"] == "deck_visible_from_step6_additive_pressure"
    assert payload["redesigned_policy"]["normal_runtime_reviewer_calls"] == 0
    assert payload["redesigned_policy"]["cognitive_signal_source"] == "step6_private_ledger"
    assert payload["deterministic_role"] == [
        "validate_cache_state",
        "validate_step6_ledger_schema",
        "validate_payload_preservation",
        "preserve_audit_custody",
    ]
    assert payload["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_private_or_confirming_ledger_keeps_anchor_fallback() -> None:
    payload = build_visibility_policy_redesign(
        case_id="mother-address-year",
        cache_state="cache_hit",
        step6_ledger_signal="all_private_or_confirming",
        payload_gate_result="preserved",
        bridge_probe_label="not_observed",
    )

    validate_visibility_policy_redesign_payload(payload)

    assert payload["redesigned_policy"]["result"] == "anchor_visible_deck_private"
    assert payload["redesigned_policy"]["why"] == (
        "Step 6 did not record additive non-anchor pressure."
    )


def test_payload_omission_blocks_deck_visibility_even_with_additive_pressure() -> None:
    payload = build_visibility_policy_redesign(
        case_id="synthetic-payload-omission",
        cache_state="cache_hit",
        step6_ledger_signal="additive_pressure_present",
        payload_gate_result="introduced_omission",
        bridge_probe_label="false_standdown",
    )

    validate_visibility_policy_redesign_payload(payload)

    assert payload["redesigned_policy"]["result"] == "anchor_visible_payload_omission_guardrail"
    assert payload["redesigned_policy"]["why"] == (
        "Protected anchor payload was lost, so deck visibility is blocked."
    )


def test_cache_miss_stands_down_to_current_step6_without_deck_visibility() -> None:
    payload = build_visibility_policy_redesign(
        case_id="synthetic-cache-miss",
        cache_state="cache_miss",
        step6_ledger_signal="additive_pressure_present",
        payload_gate_result="preserved",
        bridge_probe_label="false_standdown",
    )

    validate_visibility_policy_redesign_payload(payload)

    assert payload["redesigned_policy"]["result"] == "current_step6_visible_no_deck"
    assert payload["redesigned_policy"]["why"] == (
        "Cached card deck is unavailable; normal runtime does not generate cards live."
    )


def test_missing_or_unclear_ledger_keeps_anchor_fallback() -> None:
    payload = build_visibility_policy_redesign(
        case_id="synthetic-missing-ledger",
        cache_state="cache_hit",
        step6_ledger_signal="missing_or_unclear",
        payload_gate_result="preserved",
        bridge_probe_label="not_observed",
    )

    validate_visibility_policy_redesign_payload(payload)

    assert payload["redesigned_policy"]["result"] == "anchor_visible_unclear_ledger_guardrail"
    assert payload["redesigned_policy"]["why"] == (
        "Step 6 ledger is missing or unclear; deterministic code cannot infer cognition."
    )


def test_visibility_policy_redesign_fixture_suite_validates() -> None:
    fixture_dir = REPO_ROOT / "research" / "pre-step6-visibility-policy-redesign"
    paths = sorted(fixture_dir.glob("*.visibility-policy-redesign.v1.json"))

    assert [path.name for path in paths] == [
        "bridge-high-clutter-sensitive-overlay.visibility-policy-redesign.v1.json",
        "bridge-sensitive-anchor-misses-tripwire.visibility-policy-redesign.v1.json",
        "bridge-sequencing-sensitive-boundary.visibility-policy-redesign.v1.json",
        "mother-address-year.visibility-policy-redesign.v1.json",
        "synthetic-cache-miss.visibility-policy-redesign.v1.json",
        "synthetic-missing-ledger.visibility-policy-redesign.v1.json",
        "synthetic-payload-omission.visibility-policy-redesign.v1.json",
    ]
    for path in paths:
        validate_visibility_policy_redesign_payload(
            load_visibility_policy_redesign_payload(path),
            path=path,
        )
