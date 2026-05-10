from __future__ import annotations

from scripts.run_v60_system_bound_enrichment_replay import (
    build_composer_prompt,
    build_system_profile,
    validate_composer_output,
)


class _Case:
    explicit_nominations = ()


def test_system_profile_maps_private_opportunities_to_lane_and_embedding_sources() -> None:
    case_artifact = {
        "case_id": "startup_pivot",
        "query": "Should we pivot?",
        "vanilla_answer": "Run a pre-buy test.",
        "conversation_excerpt": "Three customers asked for a workflow tool.",
        "result": {
            "companion_cheat_sheet": {
                "anchors": [
                    {
                        "model_id": "base-rates",
                        "presence_explanation": "The answer asks for outside evidence.",
                    }
                ]
            }
        },
    }
    embedding_row = {
        "lane_selected_cap8": ["base-rates"],
        "top_embedding_models": [
            {
                "model_id": "optionality",
                "best_chunk_id": "aff::optionality.expand-before-evaluating",
                "score": 0.81,
            }
        ],
        "top_absence_models": [],
        "hybrid_rrf_top8": [],
    }
    packet = {
        "chunk_cards": [
            {
                "card_id": "card-001-base-rates",
                "model_id": "base-rates",
                "selection_source": "lane_preserved",
                "selected_affordance_cards": [
                    {"chunk_id": "aff::base-rates.outside-view-reference-class-anchor"}
                ],
                "selected_absence_records": [
                    {"chunk_id": "abs::base-rates::advertising-message-targeting-affordance"}
                ],
            },
            {
                "card_id": "card-002-optionality",
                "model_id": "optionality",
                "selection_source": "embedding_affordance_exact",
                "selected_affordance_cards": [
                    {"chunk_id": "aff::optionality.expand-before-evaluating"}
                ],
                "selected_absence_records": [
                    {"chunk_id": "abs::optionality::fake-options"}
                ],
            },
        ]
    }
    private_trace = {
        "packet_usefulness": "useful",
        "chunk_assessments": [
            {
                "chunk_id": "aff::optionality.expand-before-evaluating",
                "route": "public_delta_candidate",
                "usefulness_to_consider": "high",
            },
            {
                "chunk_id": "abs::optionality::fake-options",
                "route": "guardrail",
                "usefulness_to_consider": "medium",
            },
        ],
        "selected_opportunities": [
            {
                "opportunity_id": "hybrid-option",
                "route": "public_delta_candidate",
                "source_chunk_ids": ["aff::optionality.expand-before-evaluating"],
                "source_card_ids": ["card-002-optionality"],
                "private_value": "The binary frame may be too narrow.",
                "public_candidate": "Consider a hybrid option.",
                "public_admission_risk": "Could add complexity.",
            }
        ],
        "retrieval_feedback": ["Optionality was useful."],
    }

    profile = build_system_profile(
        case=_Case(),
        case_artifact=case_artifact,
        embedding_row=embedding_row,
        packet=packet,
        private_trace=private_trace,
        private_validation={"status": "valid"},
        max_nominations=8,
    )

    assert profile["lane_profile"]["nominated_model_ids"] == ["base-rates"]
    assert profile["packet_source_counts"] == {
        "embedding_affordance_exact": 1,
        "lane_preserved": 1,
    }
    opportunity = profile["composer_opportunities"][0]
    assert opportunity["source_mix"] == ["embedding_affordance_exact"]
    assert opportunity["chunk_kind_mix"] == ["affordance"]
    assert opportunity["model_ids"] == ["optionality"]


def test_composer_prompt_keeps_public_policy_and_validator_blocks_private_leaks() -> None:
    system_profile = {
        "lane_profile": {"nominated_model_ids": ["optionality"]},
        "embedding_profile": {},
        "packet_source_counts": {"embedding_affordance_exact": 1},
        "private_trace_summary": {"packet_usefulness": "useful"},
        "composer_opportunities": [
            {
                "opportunity_id": "hybrid-option",
                "route": "public_delta_candidate",
                "private_value": "The binary frame may be too narrow.",
                "public_candidate": "Consider a hybrid option.",
                "public_admission_risk": "Could add complexity.",
                "source_mix": ["embedding_affordance_exact"],
            }
        ],
    }
    prompt = build_composer_prompt(
        case_artifact={
            "case_id": "case",
            "query": "Should we pivot?",
            "vanilla_answer": "Run a pre-buy test.",
            "conversation_excerpt": "conversation",
        },
        system_profile=system_profile,
        max_admitted=2,
        conversation_chars=100,
        vanilla_chars=100,
    )

    assert prompt["composer_policy"]["do_not_explain_internal_mechanism_to_user"] is True
    assert prompt["composer_policy"]["max_admitted_public_deltas"] == 2

    valid_output = {
        "admission_decision": "admit_delta",
        "admitted_items": [
            {
                "item_id": "delta-1",
                "source_opportunity_ids": ["hybrid-option"],
                "delta_type": "option_space_expansion",
                "public_delta": "Consider a hybrid option before treating this as all-or-nothing.",
                "why_admitted": "It adds a concrete missing option.",
                "quality_value": "high",
                "friction_cost": "low",
                "risk_if_added": "Could distract if no real hybrid exists.",
            }
        ],
        "rejected_items": [],
        "private_guardrails_preserved": [],
        "user_visible_delta": "Consider a hybrid option before treating this as all-or-nothing.",
        "no_delta_reason": "",
        "integration_feedback": ["Useful with low friction."],
    }

    assert validate_composer_output(valid_output, system_profile=system_profile, max_admitted=2)[
        "status"
    ] == "valid"

    invalid_output = {
        **valid_output,
        "user_visible_delta": "Use the v60 affordance card to consider a hybrid.",
    }
    validation = validate_composer_output(
        invalid_output,
        system_profile=system_profile,
        max_admitted=2,
    )

    assert validation["status"] == "invalid"
    assert any("leaks private language" in error for error in validation["errors"])


def test_composer_validator_blocks_novel_public_numbers() -> None:
    system_profile = {
        "composer_opportunities": [
            {
                "opportunity_id": "buffer",
                "route": "public_delta_candidate",
                "source_mix": ["lane_preserved"],
            }
        ],
    }
    output = {
        "admission_decision": "admit_delta",
        "admitted_items": [
            {
                "item_id": "delta-1",
                "source_opportunity_ids": ["buffer"],
                "delta_type": "risk_caveat",
                "public_delta": "Keep the $950K ceiling because a $24K miss breaks the buffer.",
                "why_admitted": "It sharpens the caveat.",
                "quality_value": "high",
                "friction_cost": "low",
                "risk_if_added": "It could overstate precision.",
            }
        ],
        "rejected_items": [],
        "private_guardrails_preserved": [],
        "user_visible_delta": "Keep the $950K ceiling because a $24K miss breaks the buffer.",
        "no_delta_reason": "",
        "integration_feedback": [],
    }

    validation = validate_composer_output(
        output,
        system_profile=system_profile,
        max_admitted=2,
        allowed_numeric_text="The user has a $950K ceiling.",
    )

    assert validation["status"] == "invalid"
    assert any("24" in error for error in validation["errors"])


def test_composer_validator_treats_money_and_percent_numbers_separately() -> None:
    system_profile = {
        "composer_opportunities": [
            {
                "opportunity_id": "buffer",
                "route": "public_delta_candidate",
                "source_mix": ["lane_preserved"],
            }
        ],
    }
    output = {
        "admission_decision": "admit_delta",
        "admitted_items": [
            {
                "item_id": "delta-1",
                "source_opportunity_ids": ["buffer"],
                "delta_type": "risk_caveat",
                "public_delta": "Inspector misses can add 20-30% more deferred issues.",
                "why_admitted": "It sharpens the caveat.",
                "quality_value": "high",
                "friction_cost": "low",
                "risk_if_added": "It could overstate precision.",
            }
        ],
        "rejected_items": [],
        "private_guardrails_preserved": [],
        "user_visible_delta": "Inspector misses can add 20-30% more deferred issues.",
        "no_delta_reason": "",
        "integration_feedback": [],
    }

    validation = validate_composer_output(
        output,
        system_profile=system_profile,
        max_admitted=2,
        allowed_numeric_text="The repair could be $20K or $60K.",
    )

    assert validation["status"] == "invalid"
    assert any("20%" in error for error in validation["errors"])
    assert any("30%" in error for error in validation["errors"])
