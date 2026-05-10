from __future__ import annotations

from scripts.run_v60_chunk_exact_private_replay import (
    build_exact_chunk_packet,
    build_v60_index,
    validate_private_trace,
)


def _affordance(model_id: str, affordance_id: str) -> dict[str, object]:
    return {
        "model_id": model_id,
        "affordance_id": affordance_id,
        "status": "supported",
        "confidence": "high",
        "mechanism": f"{model_id} mechanism",
        "activation_shape": {
            "use_when": [f"use {model_id}"],
            "case_evidence_needed": [f"evidence {model_id}"],
            "do_not_use_when": [f"do not use {model_id}"],
        },
        "diagnostic_questions": [f"question {model_id}?"],
        "misuse_guards": [f"guard {model_id}"],
        "source_evidence": [
            {
                "source_file": f"{model_id}.md",
                "source_quote": f"{model_id} source quote",
            }
        ],
    }


def _absence(model_id: str, attempted_field: str) -> dict[str, object]:
    return {
        "model_id": model_id,
        "attempted_field": attempted_field,
        "status": "not_supported_by_source",
        "runtime_policy": "do_not_promote",
        "reason": f"{attempted_field} is not supported",
        "source_evidence": [
            {
                "source_file": f"{model_id}.md",
                "source_quote": f"{model_id} absence quote",
            }
        ],
    }


def test_exact_chunk_packet_preserves_embedding_affordance_and_absence_hits() -> None:
    payload = {
        "affordances": [
            _affordance("lane-a", "lane-a.primary"),
            _affordance("lane-b", "lane-b.primary"),
            _affordance("lane-c", "lane-c.primary"),
            _affordance("lane-d", "lane-d.primary"),
            _affordance("embed-x", "embed-x.fallback"),
            _affordance("embed-x", "embed-x.exact-hit"),
            _affordance("embed-y", "embed-y.exact-hit"),
            _affordance("absence-z", "absence-z.primary"),
            _affordance("hybrid-h", "hybrid-h.primary"),
        ],
        "absence_records": [
            _absence("lane-a", "lane-a-default-absence"),
            _absence("lane-b", "lane-b-default-absence"),
            _absence("lane-c", "lane-c-default-absence"),
            _absence("lane-d", "lane-d-default-absence"),
            _absence("embed-x", "embed-x-default-absence"),
            _absence("embed-y", "embed-y-default-absence"),
            _absence("absence-z", "absence-z-fallback-absence"),
            _absence("absence-z", "absence-z-exact-absence"),
            _absence("hybrid-h", "hybrid-h-default-absence"),
        ],
    }
    embedding_row = {
        "lane_selected_cap8": ["lane-a", "lane-b", "lane-c", "lane-d"],
        "top_embedding_models": [
            {
                "model_id": "embed-x",
                "best_affordance_id": "embed-x.exact-hit",
                "best_chunk_id": "aff::embed-x.exact-hit",
                "score": 0.91,
            },
            {
                "model_id": "embed-y",
                "best_affordance_id": "embed-y.exact-hit",
                "best_chunk_id": "aff::embed-y.exact-hit",
                "score": 0.87,
            },
        ],
        "top_absence_models": [
            {
                "model_id": "absence-z",
                "best_absence_field": "absence-z-exact-absence",
                "best_chunk_id": "abs::absence-z::absence-z-exact-absence",
                "score": 0.73,
            }
        ],
        "hybrid_rrf_top8": ["hybrid-h"],
    }

    packet = build_exact_chunk_packet(
        case_id="case",
        case_stem="case",
        embedding_row=embedding_row,
        index=build_v60_index(payload),
    )

    cards = {card["model_id"]: card for card in packet["chunk_cards"]}
    assert [card["selection_source"] for card in packet["chunk_cards"]] == [
        "lane_preserved",
        "lane_preserved",
        "lane_preserved",
        "lane_preserved",
        "embedding_affordance_exact",
        "embedding_affordance_exact",
        "embedding_absence_exact",
        "hybrid_rrf_exact",
    ]
    assert cards["embed-x"]["selected_affordance_cards"][0]["affordance_id"] == "embed-x.exact-hit"
    assert cards["embed-x"]["retrieval_trace"]["embedding_best_chunk_id"] == "aff::embed-x.exact-hit"
    assert (
        cards["absence-z"]["selected_absence_records"][0]["attempted_field"]
        == "absence-z-exact-absence"
    )
    assert (
        cards["absence-z"]["retrieval_trace"]["absence_best_chunk_id"]
        == "abs::absence-z::absence-z-exact-absence"
    )


def test_private_trace_validator_accepts_complete_shape_and_blocks_public_leaks() -> None:
    packet = {
        "chunk_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "selected_affordance_cards": [{"chunk_id": "aff::optionality.expand"}],
                "selected_absence_records": [{"chunk_id": "abs::optionality::fake-options"}],
            }
        ]
    }
    valid_output = {
        "packet_usefulness": "useful",
        "chunk_assessments": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "selected_chunk_ids_considered": ["aff::optionality.expand"],
                "usefulness_to_consider": "high",
                "opportunity_role": "frame_changer",
                "route": "public_delta_candidate",
                "evidence_status": "inferred_from_turn",
                "what_it_helped_notice": "The plan may be framed too narrowly.",
                "why_not_used_publicly_or_why_blocked": "",
                "risk_if_forced": "It could create fake options.",
            }
        ],
        "selected_opportunities": [
            {
                "opportunity_id": "narrow-frame",
                "route": "public_delta_candidate",
                "source_card_ids": ["card-001-optionality"],
                "private_value": "It tests whether the option set is too narrow.",
                "public_candidate": "Check whether there is a third option before choosing.",
                "public_admission_risk": "It may be generic if no third option is visible.",
            }
        ],
        "retrieval_feedback": ["The affordance was specific enough."],
        "no_public_delta_reason": "",
    }

    assert validate_private_trace(valid_output, packet=packet)["status"] == "valid"

    invalid_output = {
        **valid_output,
        "selected_opportunities": [
            {
                **valid_output["selected_opportunities"][0],
                "public_candidate": "Use the v60 affordance card as a mental model.",
            }
        ],
    }

    validation = validate_private_trace(invalid_output, packet=packet)
    assert validation["status"] == "invalid"
    assert any("leaks private language" in error for error in validation["errors"])


def test_chunk_level_validator_requires_every_exact_chunk_once() -> None:
    packet = {
        "chunk_cards": [
            {
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "selected_affordance_cards": [{"chunk_id": "aff::optionality.expand"}],
                "selected_absence_records": [{"chunk_id": "abs::optionality::fake-options"}],
            }
        ]
    }
    valid_output = {
        "packet_usefulness": "useful",
        "chunk_assessments": [
            {
                "chunk_id": "aff::optionality.expand",
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "usefulness_to_consider": "high",
                "opportunity_role": "frame_changer",
                "route": "public_delta_candidate",
                "evidence_status": "inferred_from_turn",
                "what_it_helped_notice": "The option set may be too narrow.",
                "why_not_used_publicly_or_why_blocked": "",
                "risk_if_forced": "It could invent options.",
            },
            {
                "chunk_id": "abs::optionality::fake-options",
                "card_id": "card-001-optionality",
                "model_id": "optionality",
                "usefulness_to_consider": "medium",
                "opportunity_role": "absence_blocker",
                "route": "guardrail",
                "evidence_status": "not_needed",
                "what_it_helped_notice": "It blocks fake optionality.",
                "why_not_used_publicly_or_why_blocked": "It is a private guardrail.",
                "risk_if_forced": "It could over-warn.",
            },
        ],
        "selected_opportunities": [
            {
                "opportunity_id": "narrow-frame",
                "route": "public_delta_candidate",
                "source_chunk_ids": ["aff::optionality.expand"],
                "source_card_ids": ["card-001-optionality"],
                "private_value": "It tests whether a third option exists.",
                "public_candidate": "Check whether there is a third option before choosing.",
                "public_admission_risk": "It may be generic without a real third option.",
            }
        ],
        "retrieval_feedback": ["The absence was a useful blocker."],
        "no_public_delta_reason": "",
    }

    assert (
        validate_private_trace(valid_output, packet=packet, assessment_level="chunk")["status"]
        == "valid"
    )

    invalid_output = {
        **valid_output,
        "chunk_assessments": valid_output["chunk_assessments"][:1],
    }

    validation = validate_private_trace(invalid_output, packet=packet, assessment_level="chunk")
    assert validation["status"] == "invalid"
    assert any("missing chunk IDs" in error for error in validation["errors"])
