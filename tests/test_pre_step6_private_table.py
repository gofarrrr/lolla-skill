from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.pre_step6_private_table import (
    SCHEMA_VERSION,
    build_pre_step6_private_table,
    finalize_pre_step6_private_table_ledger,
    validate_pre_step6_private_table,
    validate_pre_step6_private_table_ledger,
    write_pre_step6_private_table_sidecars,
)


def _result_payload() -> dict[str, object]:
    return {
        "extraction": {
            "decision_situation": "Whether to grant Marcus equity",
            "original_framing": "Should I give Marcus 15 percent?",
            "synthesized_position": "Grant it if he is important.",
            "live_constraints": [{"constraint": "Cash is tight.", "status": "active"}],
            "dropped_threads": [{"thread": "No vesting fallback was discussed."}],
        },
        "prompt_versions": {"lane1": "abc123"},
        "delta_card": {
            "top_findings": [
                {
                    "tendency_id": "doubt-avoidance-tendency",
                    "tendency_name": "Doubt Avoidance",
                    "severity": "high",
                    "specific_passage": "Marcus is too important to risk upsetting.",
                    "challenge_statement": "Equity is being used to avoid a hard dependency test.",
                    "next_move": "Define a non-equity trial first.",
                }
            ]
        },
        "companion_cheat_sheet": {
            "anchors": [
                {
                    "model_id": "opportunity-cost",
                    "display_name": "Opportunity Cost",
                    "why_it_matters": "The equity grant closes off cheaper learning paths.",
                    "chunks": [{"text": "Ask what option the commitment displaces."}],
                }
            ]
        },
        "frame_pressure_card": {
            "frame_elements": [
                {
                    "element_type": "assumption",
                    "frame_pattern": "forced binary",
                    "text": "Grant equity or lose Marcus.",
                    "fragility_signal": "A reversible trial exists.",
                }
            ],
            "reframings": [
                {
                    "reframe_move_type": "inversion",
                    "question": "What would make the equity grant a mistake?",
                }
            ],
        },
        "structural_coverage_card": {
            "dimensions": [
                {
                    "dimension_id": "commitment-reversibility",
                    "dimension_name": "Commitment Reversibility",
                    "covered": False,
                    "materiality_note": "Equity is hard to unwind.",
                }
            ],
            "gap_questions": [
                {
                    "dimension_id": "commitment-reversibility",
                    "dimension_name": "Commitment Reversibility",
                    "questions": ["What trial could prove fit before equity?"],
                }
            ],
        },
        "v60_enrichment": {
            "status": "active",
            "telemetry": {
                "selected_chunk_ids": [
                    "aff::opportunity-cost.displaced-alternative-commitment-gate"
                ]
            },
            "selected_cards": [
                {
                    "model_id": "opportunity-cost",
                    "selection_reason": "The answer may ignore displaced alternatives.",
                    "selected_affordance_cards": [
                        {
                            "chunk_id": "aff::opportunity-cost.displaced-alternative-commitment-gate",
                            "text": "Name the option displaced by the commitment.",
                        }
                    ],
                }
            ],
        },
    }


def test_private_table_renders_current_run_without_live_card_generation(tmp_path: Path) -> None:
    payload, rendered = build_pre_step6_private_table(
        result_payload=_result_payload(),
        cache_dir=tmp_path / "missing-cache",
    )

    validate_pre_step6_private_table(payload)

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["status"] == "ready"
    assert payload["promotion_effect"] == "none_private_context_only"
    assert payload["cache"]["state"] == "cache_miss"
    assert payload["cache"]["live_card_generation_allowed"] is False
    assert payload["gates"]["step6_private_context_allowed"] is True
    assert payload["gates"]["code_visible_answer_selection_allowed"] is False
    assert payload["cost_envelope"]["net_new_llm_calls"] == 0
    assert "rendered_private_table" not in payload
    assert "Pre-Step-6 Private Thinking Table" in rendered
    assert "Equity is being used to avoid a hard dependency test." in rendered
    assert "Opportunity Cost" in rendered
    assert "Commitment Reversibility" in rendered
    assert "Name the option displaced" in rendered
    source_ids = [item["source_id"] for item in payload["source_items"]]
    assert source_ids == [
        "lane1::doubt-avoidance-tendency",
        "lane2::opportunity-cost",
        "lane3::frame_element::0::forced-binary",
        "lane3::reframe::0::inversion",
        "lane4::dimension::commitment-reversibility",
        "lane4::gap_question::commitment-reversibility",
        "v60::card::opportunity-cost",
    ]
    skeleton_ids = [
        item["source_id"]
        for item in payload["consideration_ledger_skeleton"]["items"]
    ]
    assert skeleton_ids == source_ids
    assert payload["source_items"][0]["section_id"] == "lane1_structural_challenge"


def test_private_table_appends_cached_cards_and_writes_sidecars(tmp_path: Path) -> None:
    first, _ = build_pre_step6_private_table(
        result_payload=_result_payload(),
        cache_dir=tmp_path,
    )
    deck_path = tmp_path / f"{first['compiled_card_deck_key']}.pre-step6-shadow-card-deck.v1.json"
    deck_path.write_text(
        json.dumps(
            {
                "schema_version": "pre_step6_card_deck.v1",
                "status": "research_only",
                "runtime_policy": "runtime_dormant",
                "cards": [
                    {
                        "card_id": "bevelin_card",
                        "card_label": "Bevelin private card",
                        "cognitive_role": "Edge-pressure scan.",
                        "receipts": ["Adds incentive-pressure language."],
                        "handling_rule": "Use only if it adds concrete decision pressure.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    payload, rendered = build_pre_step6_private_table(
        result_payload=_result_payload(),
        cache_dir=tmp_path,
    )
    paths = write_pre_step6_private_table_sidecars(
        payload,
        rendered,
        tmp_dir=tmp_path,
        run_id="privatetest",
    )

    validate_pre_step6_private_table(payload)

    assert payload["cache"]["state"] == "cache_hit"
    assert payload["cached_card_deck_summary"]["card_count"] == 1
    assert "Bevelin private card" in rendered
    assert "cached_card::bevelin_card" in [
        item["source_id"] for item in payload["source_items"]
    ]
    assert paths["markdown"].name == "lolla_privatetest_pre_step6_private_table.md"
    assert paths["json"].name == "lolla_privatetest_pre_step6_private_table.json"
    assert paths["markdown"].read_text(encoding="utf-8") == rendered
    written_payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert written_payload["sidecars"]["markdown"] == str(paths["markdown"])


def _completed_private_table_ledger(payload: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "pre_step6_private_table_ledger.v1",
        "status": "completed",
        "items": [
            {
                **item,
                "disposition": "confirming_support",
                "why": "Considered privately.",
                "visible_effect": "",
                "private_guardrail": "",
            }
            for item in payload["consideration_ledger_skeleton"]["items"]
        ],
        "notes": ["Private telemetry only. Not rendered in chat."],
    }


def test_private_table_ledger_validator_accepts_exact_skeleton_ids(tmp_path: Path) -> None:
    payload, _ = build_pre_step6_private_table(
        result_payload=_result_payload(),
        cache_dir=tmp_path / "missing-cache",
    )
    ledger = _completed_private_table_ledger(payload)

    validation = validate_pre_step6_private_table_ledger(
        ledger,
        private_table=payload,
    )

    assert validation["status"] == "valid"
    assert validation["item_count"] == len(payload["source_items"])
    assert validation["source_item_count"] == len(payload["source_items"])
    assert validation["missing_source_ids"] == []
    assert validation["unknown_source_ids"] == []


def test_private_table_ledger_validator_rejects_old_aggregate_ids(tmp_path: Path) -> None:
    payload, _ = build_pre_step6_private_table(
        result_payload=_result_payload(),
        cache_dir=tmp_path / "missing-cache",
    )
    ledger = {
        "schema_version": "pre_step6_private_table_ledger.v1",
        "status": "completed",
        "items": [
            {
                "source_id": "lane1_structural_challenge",
                "source_kind": "current_run_section",
                "title": "Lane 1 structural challenge",
                "disposition": "used",
                "why": "Old aggregate example.",
                "visible_effect": "",
                "private_guardrail": "",
            }
        ],
        "notes": ["Private telemetry only. Not rendered in chat."],
    }

    validation = validate_pre_step6_private_table_ledger(
        ledger,
        private_table=payload,
    )

    assert validation["status"] == "invalid"
    assert validation["unknown_source_ids"] == ["lane1_structural_challenge"]
    assert "lane1::doubt-avoidance-tendency" in validation["missing_source_ids"]
    assert any("source_id is unknown" in error for error in validation["errors"])


def test_private_table_ledger_validator_rejects_duplicates_and_bad_disposition(tmp_path: Path) -> None:
    payload, _ = build_pre_step6_private_table(
        result_payload=_result_payload(),
        cache_dir=tmp_path / "missing-cache",
    )
    ledger = _completed_private_table_ledger(payload)
    ledger["items"][0]["disposition"] = "maybe_used"
    ledger["items"][1]["source_id"] = ledger["items"][0]["source_id"]

    validation = validate_pre_step6_private_table_ledger(
        ledger,
        private_table=payload,
    )

    assert validation["status"] == "invalid"
    assert validation["duplicate_source_ids"] == [ledger["items"][0]["source_id"]]
    assert any("disposition is invalid" in error for error in validation["errors"])


def test_finalize_private_table_ledger_records_validation_in_run_health(tmp_path: Path) -> None:
    payload, _ = build_pre_step6_private_table(
        result_payload=_result_payload(),
        cache_dir=tmp_path / "missing-cache",
    )
    result = {
        "status": "ok",
        "run_health": {"overall": "healthy"},
        "pre_step6_private_table": payload,
    }
    ledger = _completed_private_table_ledger(payload)

    finalized = finalize_pre_step6_private_table_ledger(result, ledger=ledger)

    assert finalized["pre_step6_private_table_ledger"] == ledger
    assert finalized["pre_step6_private_table_ledger_validation"]["status"] == "valid"
    assert finalized["run_health"]["pre_step6_private_table_ledger"] == "valid"
    assert finalized["run_health"]["pre_step6_private_table_unaccounted_source_count"] == 0
