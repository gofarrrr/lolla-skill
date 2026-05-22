from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_false_standdown_bridge_probe import build_bridge_probe_contract  # noqa: E402
from pre_step6_bridge_step6_ledger_replay import (  # noqa: E402
    build_static_bridge_step6_replay,
    build_bridge_step6_replay_prompts,
    build_bridge_step6_replay_result,
    derive_answer_delta_specificity,
    normalize_bridge_step6_output,
    load_bridge_step6_replay_payload,
    load_bridge_step6_replay_result,
    validate_bridge_step6_replay_payload,
    validate_bridge_step6_replay_result,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_bridge_step6_replay_prompt_asks_step6_for_answer_and_private_ledger() -> None:
    contract = build_bridge_probe_contract()

    prompts = build_bridge_step6_replay_prompts(
        contract=contract,
        case_id="bridge-sensitive-anchor-misses-tripwire",
    )

    assert "You are Step 6" in prompts["system_prompt"]
    assert "anchor_visible_candidate" in prompts["user_prompt"]
    assert "deck_pressure_candidate" in prompts["user_prompt"]
    assert "private_bridge_consideration_ledger" in prompts["user_prompt"]
    assert "additive_pressure" in prompts["user_prompt"]
    assert "confirming_support" in prompts["user_prompt"]
    assert "private_guardrail" in prompts["user_prompt"]
    assert "Do not expose private labels" in prompts["user_prompt"]
    assert "concrete tripwires" in prompts["user_prompt"]
    assert "Step 6's own judgment" in prompts["user_prompt"]
    assert "answer_delta" in prompts["user_prompt"]
    assert "added_entities" in prompts["user_prompt"]
    assert "structural_delta" in prompts["user_prompt"]
    assert "reframed_emphasis" in prompts["user_prompt"]


def test_bridge_step6_replay_payload_derives_additive_signal_from_step6_ledger() -> None:
    contract = build_bridge_probe_contract()

    payload = build_static_bridge_step6_replay(
        contract=contract,
        case_id="bridge-sensitive-anchor-misses-tripwire",
        deck_novelty_role="additive_pressure",
        deck_disposition="used",
    )

    validate_bridge_step6_replay_payload(payload)

    assert payload["schema_version"] == "pre_step6_bridge_step6_ledger_replay.v1"
    assert payload["status"] == "research_only"
    assert payload["runtime_policy"] == "runtime_dormant"
    assert payload["experiment_id"] == "bridge_step6_ledger_replay_v0"
    assert payload["ledger_signal"] == "additive_pressure_present"
    assert payload["answer_delta_specificity"] == "concrete_delta_present"
    assert payload["visibility_redesign_read"] == {
        "would_unlock_redesigned_policy": True,
        "would_unlock_answer_delta_guarded_policy": True,
        "policy_dependency": (
            "cache_hit plus additive Step 6 ledger plus preserved payload can make "
            "deck-aware output visible; this replay only tests the ledger dependency."
        ),
        "answer_delta_dependency": (
            "The answer-delta guarded policy additionally requires Step 6 to name "
            "a concrete or specific structural visible-answer delta."
        ),
    }
    assert payload["deterministic_role"] == [
        "validate_bridge_contract_case",
        "validate_step6_ledger_schema",
        "derive_ledger_signal",
        "derive_answer_delta_specificity",
        "preserve_audit_custody",
    ]
    assert payload["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
    }


def test_confirming_or_private_deck_ledger_does_not_unlock_redesigned_policy() -> None:
    contract = build_bridge_probe_contract()

    payload = build_static_bridge_step6_replay(
        contract=contract,
        case_id="bridge-high-clutter-sensitive-overlay",
        deck_novelty_role="confirming_support",
        deck_disposition="deferred",
    )

    validate_bridge_step6_replay_payload(payload)

    assert payload["ledger_signal"] == "all_private_or_confirming"
    assert payload["answer_delta_specificity"] == "not_applicable"
    assert payload["visibility_redesign_read"]["would_unlock_redesigned_policy"] is False
    assert (
        payload["visibility_redesign_read"]["would_unlock_answer_delta_guarded_policy"]
        is False
    )


def test_live_output_normalization_preserves_step6_additive_deck_signal() -> None:
    normalized = normalize_bridge_step6_output(
        {
            "answer_core": (
                "Use the slow-repair plan only while the safety floor holds. The "
                "tripwires are concrete: meeting requests, sexual images, threats, "
                "other minors, hidden channels, or fear."
            ),
            "private_bridge_consideration_ledger": [
                {
                    "source_id": "deck_pressure_candidate",
                    "disposition": "combined",
                    "novelty_role": "additive_pressure",
                    "why": "It added concrete tripwires missing from the anchor.",
                    "visible_effect": "Added tripwires.",
                    "answer_delta": {
                        "added_entities": ["explicit tripwires"],
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "reframed_emphasis": [],
                    },
                }
            ],
        }
    )

    assert normalized["private_bridge_consideration_ledger"] == [
        {
            "source_id": "anchor_visible_candidate",
            "disposition": "deferred",
            "novelty_role": "visible_backbone",
            "why": "Model did not explain this source.",
            "visible_effect": "none",
            "answer_delta": {
                "added_entities": [],
                "reframed_emphasis": [],
                "removed_entities": [],
                "reordered_sequences": [],
                "structural_delta": [],
            },
        },
        {
            "source_id": "deck_pressure_candidate",
            "disposition": "combined",
            "novelty_role": "additive_pressure",
            "why": "It added concrete tripwires missing from the anchor.",
            "visible_effect": "Added tripwires.",
            "answer_delta": {
                "added_entities": ["explicit tripwires"],
                "reframed_emphasis": [],
                "removed_entities": [],
                "reordered_sequences": [],
                "structural_delta": [],
            },
        },
    ]


def test_answer_delta_specificity_blocks_additive_bridge_replay_without_concrete_delta() -> None:
    output = normalize_bridge_step6_output(
        {
            "answer_core": "Use a clearer frame, but keep the public answer concise.",
            "private_bridge_consideration_ledger": [
                {
                    "source_id": "deck_pressure_candidate",
                    "disposition": "used",
                    "novelty_role": "additive_pressure",
                    "why": "It sharpened the framing.",
                    "visible_effect": "Sharper framing.",
                    "answer_delta": {
                        "added_entities": [],
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "reframed_emphasis": ["sharper framing"],
                    },
                }
            ],
        }
    )

    assert derive_answer_delta_specificity(output) == "reframe_only"


def test_structural_delta_specificity_is_distinct_from_generic_reframing() -> None:
    output = normalize_bridge_step6_output(
        {
            "answer_core": "Use the probe only while the stop condition holds.",
            "private_bridge_consideration_ledger": [
                {
                    "source_id": "deck_pressure_candidate",
                    "disposition": "used",
                    "novelty_role": "additive_pressure",
                    "why": "It added a concrete structural decision boundary.",
                    "visible_effect": "Added stop condition.",
                    "answer_delta": {
                        "added_entities": [],
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "structural_delta": [
                            "added stop condition: exit the Silva probe if no data access by Friday"
                        ],
                        "reframed_emphasis": ["clearer process"],
                    },
                }
            ],
        }
    )

    assert derive_answer_delta_specificity(output) == "structural_delta_present"

    vague_output = normalize_bridge_step6_output(
        {
            "answer_core": "Use a better structural frame.",
            "private_bridge_consideration_ledger": [
                {
                    "source_id": "deck_pressure_candidate",
                    "disposition": "used",
                    "novelty_role": "additive_pressure",
                    "why": "It added a vague structure claim.",
                    "visible_effect": "Sharper framing.",
                    "answer_delta": {
                        "added_entities": [],
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "structural_delta": ["added structural framing"],
                        "reframed_emphasis": ["structural framing"],
                    },
                }
            ],
        }
    )

    assert derive_answer_delta_specificity(vague_output) == "reframe_only"


def test_bridge_step6_replay_result_reports_supported_when_all_bridge_cases_are_additive() -> None:
    contract = build_bridge_probe_contract()
    replays = [
        build_static_bridge_step6_replay(
            contract=contract,
            case_id=case["case_id"],
            deck_novelty_role="additive_pressure",
            deck_disposition="used",
        )
        for case in contract["probe_cases"]
    ]

    result = build_bridge_step6_replay_result(replays=replays)

    validate_bridge_step6_replay_result(result)

    assert result["replay_result"] == "step6_additive_signal_supported"
    assert result["promotion_effect"] == "none_research_only"
    assert result["case_results"] == [
        {
            "case_id": "bridge-high-clutter-sensitive-overlay",
            "ledger_signal": "additive_pressure_present",
            "answer_delta_specificity": "concrete_delta_present",
            "would_unlock_redesigned_policy": True,
            "would_unlock_answer_delta_guarded_policy": True,
        },
        {
            "case_id": "bridge-sensitive-anchor-misses-tripwire",
            "ledger_signal": "additive_pressure_present",
            "answer_delta_specificity": "concrete_delta_present",
            "would_unlock_redesigned_policy": True,
            "would_unlock_answer_delta_guarded_policy": True,
        },
        {
            "case_id": "bridge-sequencing-sensitive-boundary",
            "ledger_signal": "additive_pressure_present",
            "answer_delta_specificity": "concrete_delta_present",
            "would_unlock_redesigned_policy": True,
            "would_unlock_answer_delta_guarded_policy": True,
        },
    ]
    assert result["answer_delta_replay_result"] == "answer_delta_bridge_support_preserved"
    assert result["gates"]["runtime_wiring_allowed"] is False
    assert result["gates"]["skill_update_allowed"] is False


def test_bridge_step6_replay_fixture_suite_validates() -> None:
    fixture_dir = REPO_ROOT / "research" / "pre-step6-bridge-step6-ledger-replays"
    paths = sorted(fixture_dir.glob("*.bridge-step6-ledger-replay.v1.json"))

    assert [path.name for path in paths] == [
        "bridge-high-clutter-sensitive-overlay.bridge-step6-ledger-replay.v1.json",
        "bridge-sensitive-anchor-misses-tripwire.bridge-step6-ledger-replay.v1.json",
        "bridge-sequencing-sensitive-boundary.bridge-step6-ledger-replay.v1.json",
    ]
    for path in paths:
        validate_bridge_step6_replay_payload(
            load_bridge_step6_replay_payload(path),
            path=path,
        )

    result_path = fixture_dir / "bridge-step6-ledger-replay-result.v1.json"
    validate_bridge_step6_replay_result(
        load_bridge_step6_replay_result(result_path),
        path=result_path,
    )
