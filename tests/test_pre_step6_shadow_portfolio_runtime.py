from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.pre_step6_shadow_portfolio import (
    SCHEMA_VERSION,
    build_pre_step6_shadow_portfolio,
    derive_answer_delta_specificity,
    derive_step6_ledger_signal,
    validate_pre_step6_shadow_portfolio,
    write_pre_step6_shadow_portfolio_sidecar,
)


def _result_payload() -> dict[str, object]:
    return {
        "extraction": {
            "decision_situation": "Whether to grant Marcus equity",
            "original_framing": "Should I give Marcus 15 percent?",
        },
        "prompt_versions": {"lane1": "abc123"},
        "v60_enrichment": {
            "status": "active",
            "telemetry": {
                "selected_chunk_ids": [
                    "aff::opportunity-cost.displaced-alternative-commitment-gate",
                ]
            },
        },
        "revised_answer": "Existing visible answer must remain untouched.",
    }


def _additive_ledger() -> dict[str, object]:
    return {
        "schema_version": "pre_step6_shadow_step6_ledger.v1",
        "items": [
            {
                "source_id": "clean_hybrid_card",
                "disposition": "used",
                "novelty_role": "visible_backbone",
                "why": "The anchor carries the concrete answer.",
                "visible_effect": "Backbone preserved.",
            },
            {
                "source_id": "bevelin_card",
                "disposition": "combined",
                "novelty_role": "additive_pressure",
                "why": "It sharpens the dependency/incentive trap.",
                "visible_effect": "Added incentive-pressure language.",
                "answer_delta": {
                    "added_entities": ["dependency test"],
                    "removed_entities": [],
                    "reordered_sequences": [],
                    "reframed_emphasis": ["incentive pressure"],
                },
            },
        ],
    }


def test_shadow_cache_miss_records_stand_down_without_live_generation(tmp_path: Path) -> None:
    payload = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path / "missing-cache",
    )

    validate_pre_step6_shadow_portfolio(payload)

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["status"] == "shadow_cache_miss"
    assert payload["cache"]["state"] == "cache_miss"
    assert payload["cache"]["live_card_generation_allowed"] is False
    assert payload["shadow_visibility_decision"] == {
        "result": "current_step6_visible_no_deck",
        "why": "Cached card deck is unavailable; shadow mode records stand-down only.",
        "cognitive_signal_source": "not_run",
        "normal_runtime_reviewer_calls": 0,
        "applied_to_user_visible_output": False,
    }
    assert payload["gates"] == {
        "runtime_wiring_allowed": False,
        "skill_update_allowed": False,
        "visible_behavior_change_allowed": False,
    }


def test_shadow_cache_hit_additive_ledger_is_shadow_only_deck_visible(tmp_path: Path) -> None:
    first = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
    )
    deck_path = tmp_path / f"{first['compiled_card_deck_key']}.pre-step6-shadow-card-deck.v1.json"
    deck_path.write_text(
        json.dumps(
            {
                "schema_version": "pre_step6_card_deck.v1",
                "cards": [{"card_id": "clean_hybrid_card"}, {"card_id": "bevelin_card"}],
            }
        ),
        encoding="utf-8",
    )

    payload = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
        step6_ledger=_additive_ledger(),
        payload_gate={"status": "preserved"},
        custody_valid=True,
    )

    validate_pre_step6_shadow_portfolio(payload)

    assert payload["status"] == "shadow_resolved"
    assert payload["cache"]["state"] == "cache_hit"
    assert payload["step6_ledger_signal"] == "additive_pressure_present"
    assert payload["shadow_visibility_decision"]["result"] == "deck_visible_shadow_only"
    assert payload["shadow_visibility_decision"]["cognitive_signal_source"] == "step6_private_ledger"
    assert payload["shadow_visibility_decision"]["applied_to_user_visible_output"] is False
    assert payload["promotion_effect"] == "none_shadow_only"


def test_payload_omission_blocks_shadow_deck_visibility_even_with_additive_ledger(tmp_path: Path) -> None:
    first = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
    )
    (tmp_path / f"{first['compiled_card_deck_key']}.pre-step6-shadow-card-deck.v1.json").write_text(
        json.dumps({"schema_version": "pre_step6_card_deck.v1", "cards": []}),
        encoding="utf-8",
    )

    payload = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
        step6_ledger=_additive_ledger(),
        payload_gate={"status": "introduced_omission"},
    )

    validate_pre_step6_shadow_portfolio(payload)

    assert payload["shadow_visibility_decision"]["result"] == (
        "anchor_visible_payload_omission_guardrail_shadow_only"
    )
    assert payload["shadow_visibility_decision"]["applied_to_user_visible_output"] is False


def test_payload_gate_result_blocks_shadow_deck_visibility(tmp_path: Path) -> None:
    first = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
    )
    (tmp_path / f"{first['compiled_card_deck_key']}.pre-step6-shadow-card-deck.v1.json").write_text(
        json.dumps({"schema_version": "pre_step6_card_deck.v1", "cards": []}),
        encoding="utf-8",
    )

    payload = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
        step6_ledger=_additive_ledger(),
        payload_gate={
            "schema_version": "pre_step6_payload_omission.v1",
            "gate_result": "introduced_omission",
            "categories": [],
        },
    )

    validate_pre_step6_shadow_portfolio(payload)

    assert payload["shadow_visibility_decision"]["result"] == (
        "anchor_visible_payload_omission_guardrail_shadow_only"
    )


def test_reframe_only_answer_delta_blocks_shadow_deck_visibility(tmp_path: Path) -> None:
    first = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
    )
    (tmp_path / f"{first['compiled_card_deck_key']}.pre-step6-shadow-card-deck.v1.json").write_text(
        json.dumps({"schema_version": "pre_step6_card_deck.v1", "cards": []}),
        encoding="utf-8",
    )
    ledger = _additive_ledger()
    ledger["items"][1]["answer_delta"] = {
        "added_entities": [],
        "removed_entities": [],
        "reordered_sequences": [],
        "reframed_emphasis": ["minimization", "bias-checking"],
    }

    payload = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
        step6_ledger=ledger,
        payload_gate={"status": "preserved"},
    )

    validate_pre_step6_shadow_portfolio(payload)

    assert payload["step6_ledger_signal"] == "additive_pressure_present"
    assert payload["answer_delta_specificity"] == "reframe_only"
    assert payload["shadow_visibility_decision"]["result"] == (
        "anchor_visible_answer_delta_guardrail_shadow_only"
    )


def test_structural_delta_answer_delta_unlocks_shadow_without_entity_change(tmp_path: Path) -> None:
    first = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
    )
    (tmp_path / f"{first['compiled_card_deck_key']}.pre-step6-shadow-card-deck.v1.json").write_text(
        json.dumps({"schema_version": "pre_step6_card_deck.v1", "cards": []}),
        encoding="utf-8",
    )
    ledger = _additive_ledger()
    ledger["items"][1]["answer_delta"] = {
        "added_entities": [],
        "removed_entities": [],
        "reordered_sequences": [],
        "structural_delta": [
            "added stop condition: do not grant equity unless Marcus passes a two-week sprint"
        ],
        "reframed_emphasis": ["commitment discipline"],
    }

    payload = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path,
        step6_ledger=ledger,
        payload_gate={"status": "preserved"},
    )

    validate_pre_step6_shadow_portfolio(payload)

    assert payload["step6_ledger_signal"] == "additive_pressure_present"
    assert payload["answer_delta_specificity"] == "structural_delta_present"
    assert payload["shadow_visibility_decision"]["result"] == "deck_visible_shadow_only"


def test_ledger_signal_is_cognitive_input_not_deterministic_wisdom() -> None:
    assert derive_step6_ledger_signal(_additive_ledger()) == "additive_pressure_present"
    assert derive_step6_ledger_signal(
        {
            "items": [
                {
                    "source_id": "bevelin_card",
                    "disposition": "deferred",
                    "novelty_role": "confirming_support",
                    "why": "Useful privately.",
                    "visible_effect": "none",
                }
            ]
        }
    ) == "all_private_or_confirming"
    assert derive_step6_ledger_signal({"items": []}) == "missing_or_unclear"


def test_answer_delta_specificity_is_mechanical_not_wisdom() -> None:
    assert derive_answer_delta_specificity(_additive_ledger()) == "concrete_delta_present"
    assert derive_answer_delta_specificity(
        {
            "items": [
                {
                    "source_id": "polya_card",
                    "disposition": "combined",
                    "novelty_role": "additive_pressure",
                    "answer_delta": {
                        "added_entities": [],
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "structural_delta": [
                            "added decision boundary: revisit only after two customer pre-buys"
                        ],
                        "reframed_emphasis": ["test discipline"],
                    },
                }
            ]
        }
    ) == "structural_delta_present"
    assert derive_answer_delta_specificity(
        {
            "items": [
                {
                    "source_id": "polya_card",
                    "disposition": "combined",
                    "novelty_role": "additive_pressure",
                    "answer_delta": {
                        "added_entities": [],
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "structural_delta": ["added structural framing"],
                        "reframed_emphasis": ["structural framing"],
                    },
                }
            ]
        }
    ) == "reframe_only"
    assert derive_answer_delta_specificity(
        {
            "items": [
                {
                    "source_id": "bevelin_card",
                    "disposition": "combined",
                    "novelty_role": "additive_pressure",
                    "answer_delta": {
                        "added_entities": [],
                        "removed_entities": [],
                        "reordered_sequences": [],
                        "reframed_emphasis": ["minimization"],
                    },
                }
            ]
        }
    ) == "reframe_only"
    assert derive_answer_delta_specificity({"items": []}) == "not_applicable"


def test_sidecar_writer_uses_lolla_run_id_shape(tmp_path: Path) -> None:
    payload = build_pre_step6_shadow_portfolio(
        result_payload=_result_payload(),
        mode="shadow",
        cache_dir=tmp_path / "missing-cache",
    )

    path = write_pre_step6_shadow_portfolio_sidecar(
        payload,
        tmp_dir=tmp_path,
        run_id="shadowtest",
    )

    assert path == tmp_path / "lolla_shadowtest_pre_step6_shadow_portfolio.json"
    assert json.loads(path.read_text(encoding="utf-8"))["schema_version"] == SCHEMA_VERSION
