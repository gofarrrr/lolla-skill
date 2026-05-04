from __future__ import annotations

from engine.system_b.relation_graph import RelationGraph, RelationNeighbor
from engine.system_b.route_trace import (
    ROUTE_TRACE_SCHEMA_VERSION,
    build_route_trace_payload,
)


def test_relation_graph_records_candidate_trace_without_changing_selection() -> None:
    graph = RelationGraph(
        {
            "seed": (
                RelationNeighbor("strong-ally", "ally", 0.9),
                RelationNeighbor("budgeted-out", "ally", 0.7),
                RelationNeighbor("too-weak", "ally", 0.2),
                RelationNeighbor("risk-model", "antagonist", 0.6),
            ),
            "other-seed": (
                RelationNeighbor("budgeted-out", "ally", 0.8),
            ),
        }
    )

    neighborhood = graph.neighborhood(
        ("seed",),
        max_supporting_models=1,
        max_risk_models=1,
    )

    assert neighborhood.supporting_model_ids == ("strong-ally",)
    supporting = {item.model_id: item for item in neighborhood.supporting_candidate_trace}
    assert supporting["strong-ally"].selected is True
    assert supporting["budgeted-out"].rejection_reason == "budget_drop"
    assert supporting["too-weak"].rejection_reason == "below_min_supporting_affinity"
    assert supporting["budgeted-out"].fan_adjusted_affinity < supporting["budgeted-out"].raw_affinity
    assert neighborhood.risk_candidate_trace[0].model_id == "risk-model"
    assert neighborhood.risk_candidate_trace[0].selected is True


def test_route_trace_payload_surfaces_all_lanes_and_anti_echo() -> None:
    payload = {
        "audit_summary": {
            "routing_decisions": [
                {
                    "tendency_id": "anchoring-tendency",
                    "primary_model_id": "base-rates",
                    "sub_pattern": "general",
                    "antidote_model_ids": ["base-rates", "inversion"],
                    "supporting_model_ids": ["inversion"],
                    "risk_model_ids": [],
                    "supporting_candidate_trace": [
                        {
                            "model_id": "inversion",
                            "source_model_id": "base-rates",
                            "edge_type": "ally",
                            "raw_affinity": 0.9,
                            "fan_adjusted_affinity": 0.9,
                            "relevance_score": 0.0,
                            "selected": True,
                            "rejection_reason": "",
                        },
                        {
                            "model_id": "second-order-thinking",
                            "source_model_id": "base-rates",
                            "edge_type": "ally",
                            "raw_affinity": 0.7,
                            "fan_adjusted_affinity": 0.7,
                            "relevance_score": 0.0,
                            "selected": False,
                            "rejection_reason": "budget_drop",
                        },
                    ],
                    "risk_candidate_trace": [],
                    "tiebreaker_supporting": {
                        "fired": False,
                        "abort_reason": "outside_epsilon_window",
                        "top1_model": "inversion",
                        "top2_model": "second-order-thinking",
                        "delta": 0.2,
                    },
                    "tiebreaker_risk": None,
                }
            ],
            "companion_candidates": [
                {"model_id": "checklists", "recall_source": "keyword", "final_rank": 1},
                {"model_id": "premortem", "recall_source": "keyword", "final_rank": 2},
            ],
            "companion_verification_accepted_before_cap": [
                {"model_id": "checklists", "presence_mode": "executed"},
            ],
            "companion_rejected_models": [
                {"model_id": "premortem", "rejection_reason": "not actually used"},
            ],
            "companion_verification_capped_models": [],
            "companion_verification_duplicate_accepts": [],
            "companion_verification_quote_repairs": [],
            "companion_verification_silently_omitted": [],
            "companion_candidate_cap": 60,
        },
        "delta_card": {
            "findings": [
                {
                    "tendency_id": "anchoring-tendency",
                    "selected_model_ids": ["base-rates", "inversion"],
                }
            ]
        },
        "companion_cheat_sheet": {
            "anchors": [{"model_id": "checklists"}],
            "anti_echo_model_ids": ["base-rates"],
        },
        "frame_pressure_card": {
            "frame_elements": [
                {
                    "element_text": "Only one option is considered.",
                    "frame_pattern": "binary_collapse",
                }
            ],
            "routes": [
                {
                    "element_index": 0,
                    "frame_pattern": "binary_collapse",
                    "candidate_model_ids": ["inversion", "premortem"],
                    "excluded_model_ids": ["base-rates"],
                }
            ],
            "reframings": [
                {
                    "grounding_model": "inversion",
                    "source_element_index": 0,
                }
            ],
        },
        "structural_coverage_card": {
            "question_type": "decision-evaluation",
            "gap_routes": [
                {
                    "dimension_id": "stakeholder-alignment",
                    "dimension_name": "Stakeholder alignment",
                    "candidate_model_ids": ["principal-agent-problem"],
                    "excluded_model_ids": ["checklists"],
                }
            ],
            "anti_echo_model_ids": ["checklists"],
        },
    }

    trace = build_route_trace_payload(payload)

    assert trace["schema_version"] == ROUTE_TRACE_SCHEMA_VERSION
    assert trace["summary"]["lane1_route_count"] == 1
    assert trace["summary"]["lane2_rejected_candidate_count"] == 1
    assert trace["summary"]["lane3_route_count"] == 1
    assert trace["summary"]["lane4_route_count"] == 1
    assert trace["summary"]["anti_echo_exclusion_count"] == 2
    lane1_rejected = trace["lanes"]["lane1"]["routes"][0]["rejected_candidates"]
    assert lane1_rejected[0]["rejection_reason"] == "budget_drop"
    assert trace["lanes"]["lane2"]["rejected_candidates"][0]["stage"] == "verification"
    assert trace["anti_echo"]["exclusions"][0]["model_id"] == "base-rates"
