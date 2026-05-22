from __future__ import annotations

import json
from pathlib import Path

from scripts.research.pre_step6_shadow_portfolio_evidence import (
    write_fixed_suite_shadow_evidence,
    write_result_cache_miss_shadow_evidence,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _seed_fixed_case(root: Path, case_id: str = "demo-case") -> None:
    _write_json(
        root / "research" / "pre-step6-problem-states" / f"{case_id}.problem-state.v1.json",
        {
            "schema_version": "problem_state.v1",
            "case_id": case_id,
            "user_goal": "Decide whether to use the portfolio on this case.",
            "problem_type": "decision_evaluation",
            "knowns": ["Known fact"],
            "unknowns": ["Unknown fact"],
            "constraints": ["Stay bounded"],
            "suggested_next_move": "answer_now",
        },
    )
    _write_json(
        root
        / "research"
        / "pre-step6-rendered-hybrid-answer-cores"
        / f"{case_id}.native.rendered-hybrid-answer-core.v1.json",
        {
            "schema_version": "pre_step6_rendered_hybrid_answer_core.v1",
            "case_id": case_id,
            "answer_core": "Existing anchor answer.",
        },
    )
    _write_json(
        root / "research" / "pre-step6-step6-card-decks" / f"{case_id}.step6-card-deck.v1.json",
        {
            "schema_version": "pre_step6_card_deck.v1",
            "case_id": case_id,
            "cards": [{"card_id": "clean_hybrid_card"}, {"card_id": "bevelin_card"}],
        },
    )
    _write_json(
        root
        / "research"
        / "pre-step6-card-deck-replays"
        / f"{case_id}.card-deck-replay.v1.json",
        {
            "schema_version": "pre_step6_card_deck_replay.v1",
            "case_id": case_id,
            "step6_output": {
                "private_card_consideration_ledger": [
                    {
                        "card_id": "clean_hybrid_card",
                        "disposition": "used",
                        "novelty_role": "visible_backbone",
                        "why": "Anchor was the visible backbone.",
                        "visible_effect": "Backbone preserved.",
                    },
                    {
                        "card_id": "bevelin_card",
                        "disposition": "combined",
                        "novelty_role": "additive_pressure",
                        "why": "The card sharpened dependency pressure.",
                        "visible_effect": "Added pressure.",
                        "answer_delta": {
                            "added_entities": ["dependency pressure"],
                            "removed_entities": [],
                            "reordered_sequences": [],
                            "reframed_emphasis": ["dependency"],
                        },
                    },
                ]
            },
        },
    )
    _write_json(
        root
        / "research"
        / "pre-step6-payload-omission-gates"
        / f"{case_id}.payload-omission.v1.json",
        {
            "schema_version": "pre_step6_payload_omission.v1",
            "case_id": case_id,
            "gate_result": "preserved",
            "categories": [
                {
                    "category": "dates_or_dated_windows",
                    "judgment": "preserved",
                    "missing_anchor_evidence": [],
                },
                {
                    "category": "actor_sequence",
                    "judgment": "preserved",
                    "missing_anchor_evidence": [
                        "Talk with counsel before deciding whether to escalate."
                    ],
                },
                {
                    "category": "named_resources_or_channels",
                    "judgment": "case_n_a",
                    "missing_anchor_evidence": [],
                },
            ],
        },
    )


def test_fixed_suite_shadow_evidence_materializes_cache_hit(tmp_path: Path) -> None:
    _seed_fixed_case(tmp_path)

    aggregate = write_fixed_suite_shadow_evidence(
        root=tmp_path,
        output_dir=tmp_path / "out",
        case_ids=["demo-case"],
    )

    assert aggregate["aggregate"]["total_cases"] == 1
    assert aggregate["aggregate"]["cache_states"] == {"cache_hit": 1}
    assert aggregate["aggregate"]["decisions"] == {"deck_visible_shadow_only": 1}
    assert aggregate["aggregate"]["candidate_flags"] == {
        "deck_visible_with_marker_entity_loss": 1
    }
    assert aggregate["aggregate"]["answer_delta_specificity"] == {
        "concrete_delta_present": 1
    }

    record = aggregate["case_records"][0]
    assert record["payload_gate_result"] == "preserved"
    assert record["answer_delta_specificity"] == "concrete_delta_present"
    assert record["marker_entity_loss_categories"] == ["actor_sequence"]
    assert record["candidate_flags"] == {
        "deck_visible_with_marker_entity_loss": True
    }
    assert record["payload_preservation_outcomes"] == {
        "actor_sequence": "preserved_by_marker_anchor_entities_missing",
        "dates_or_dated_windows": "preserved_marker_and_anchor_entities",
        "named_resources_or_channels": "case_n_a",
    }

    shadow_path = (
        tmp_path
        / "out"
        / "fixed-suite-cache-hit"
        / "demo-case.pre-step6-shadow-portfolio.v1.json"
    )
    shadow = json.loads(shadow_path.read_text(encoding="utf-8"))
    assert shadow["cache"]["state"] == "cache_hit"
    assert shadow["step6_ledger_signal"] == "additive_pressure_present"
    assert shadow["payload_gate"]["gate_result"] == "preserved"
    assert shadow["shadow_visibility_decision"]["applied_to_user_visible_output"] is False

    cache_path = Path(shadow["cache"]["cache_ref"])
    assert cache_path.exists()
    assert json.loads(cache_path.read_text(encoding="utf-8"))["schema_version"] == (
        "pre_step6_card_deck.v1"
    )


def test_result_cache_miss_shadow_evidence_uses_prior_result_without_deck_generation(
    tmp_path: Path,
) -> None:
    result_path = tmp_path / "prior-result.json"
    _write_json(
        result_path,
        {
            "extraction": {
                "decision_situation": "Whether to use this prior run",
                "original_framing": "Can this run be shadow evaluated?",
            },
            "prompt_versions": {"lane1": "abc123"},
            "revised_answer": "Prior visible answer.",
        },
    )

    aggregate = write_result_cache_miss_shadow_evidence(
        output_dir=tmp_path / "out",
        result_paths=[result_path],
    )

    assert aggregate["aggregate"]["total_cases"] == 1
    assert aggregate["aggregate"]["cache_states"] == {"cache_miss": 1}
    assert aggregate["aggregate"]["decisions"] == {"current_step6_visible_no_deck": 1}

    shadow_path = (
        tmp_path
        / "out"
        / "result-cache-miss"
        / "prior-result.pre-step6-shadow-portfolio.v1.json"
    )
    shadow = json.loads(shadow_path.read_text(encoding="utf-8"))
    assert shadow["cache"]["live_card_generation_allowed"] is False
    assert shadow["shadow_visibility_decision"]["normal_runtime_reviewer_calls"] == 0
