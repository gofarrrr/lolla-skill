from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.reasoning_substrate_packet import (
    CandidateNomination,
    build_reasoning_substrate_packet,
    build_reasoning_substrate_packet_from_files,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _build_packet(
    nominations: list[CandidateNomination],
    *,
    card_cap: int = 12,
) -> dict[str, object]:
    return build_reasoning_substrate_packet_from_files(
        root=REPO_ROOT,
        packet_id="pr25-fixture-review",
        transaction_context={
            "case_id": "pr25-fixture",
            "capture_health": "thin",
            "transaction_sources": ["user_turn", "assistant_turn"],
        },
        nominations=nominations,
        candidate_card_target_max=card_cap,
        snippet_target_max_per_card=2,
    )


def _cards_by_model(packet: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(card["model_id"]): card
        for card in packet["candidate_cards"]  # type: ignore[index]
    }


def test_reviewed_candidate_gets_compact_snippets_and_source_references() -> None:
    packet = _build_packet(
        [
            CandidateNomination(
                model_id="opportunity-cost",
                pulled_by=("lane4_gap_route",),
                why_pulled=(
                    {
                        "source": "lane4_gap_route",
                        "reason": "The route named scarce-resource tradeoff.",
                        "evidence_source_type": "lane_gap",
                        "route_or_artifact_id": "resource-allocation",
                    },
                ),
                lane_order=1,
            )
        ]
    )

    card = _cards_by_model(packet)["opportunity-cost"]
    assert card["coverage_status"] == "reviewed_affordance_available"
    assert card["pulled_by"] == ["lane4_gap_route"]
    assert card["why_pulled"][0]["route_or_artifact_id"] == "resource-allocation"  # type: ignore[index]
    reviewed = card["reviewed_affordance_fields"]  # type: ignore[index]
    assert reviewed["affordance_ids"] == [  # type: ignore[index]
        "opportunity-cost.displaced-alternative-commitment-gate"
    ]
    assert reviewed["case_evidence_needed"]  # type: ignore[index]
    assert reviewed["source_evidence"][0]["source_file"] == "Opportunity_Cost_rag.md"  # type: ignore[index]
    assert card["runtime_graph_fields"]["select_when"]  # type: ignore[index]


def test_graph_only_candidate_remains_eligible_with_graph_only_label() -> None:
    packet = _build_packet(
        [
            CandidateNomination(
                model_id="chain-of-verification",
                pulled_by=("lane2_companion_chunk",),
                why_pulled=(
                    {
                        "source": "lane2_companion_chunk",
                        "reason": "Assistant answer depends on sequential checks.",
                        "evidence_source_type": "assistant_turn",
                        "evidence_quote": "verify each assumption before committing",
                    },
                ),
                lane_order=1,
            )
        ]
    )

    card = _cards_by_model(packet)["chain-of-verification"]
    assert card["coverage_status"] == "graph_only_runtime_card"
    assert card["runtime_graph_fields"]["reasoning_types"] == ["causal", "deductive"]  # type: ignore[index]
    assert card["reviewed_affordance_fields"] == {}
    assert "No reviewed affordance record" in card["do_not_overclaim"][0]  # type: ignore[index]


def test_candidate_missing_from_runtime_graph_is_suppressed_honestly() -> None:
    packet = _build_packet(
        [
            CandidateNomination(
                model_id="imaginary-model",
                pulled_by=("reviewer_note",),
                why_pulled=(
                    {
                        "source": "reviewer_note",
                        "reason": "Deliberately invalid fixture candidate.",
                        "evidence_source_type": "reviewer_note",
                    },
                ),
                lane_order=1,
            )
        ]
    )

    assert packet["candidate_cards"] == []
    suppressed = packet["suppressed_candidates"]
    assert suppressed[0]["model_id"] == "imaginary-model"  # type: ignore[index]
    assert suppressed[0]["suppression_reason"] == "model_id_not_in_runtime_graph"  # type: ignore[index]
    assert suppressed[0]["do_not_recover_as_pressure_without_review"] is True  # type: ignore[index]


def test_missing_reviewed_record_status_is_counted_in_coverage_summary() -> None:
    packet = build_reasoning_substrate_packet(
        packet_id="synthetic-missing-reviewed-record",
        transaction_context={"case_id": "synthetic"},
        nominations=[
            CandidateNomination(
                model_id="empty-reviewed-record",
                pulled_by=("reviewer_note",),
                why_pulled=(
                    {
                        "source": "reviewer_note",
                        "reason": "Synthetic record with neither affordance nor absence support.",
                    },
                ),
                lane_order=1,
            )
        ],
        knowledge_graph={
            "models": {
                "empty-reviewed-record": {
                    "display_name": "Empty Reviewed Record",
                    "source_file": "Empty_Reviewed_Record.md",
                    "reasoning_types": ["diagnostic"],
                    "select_when": ["A synthetic graph-only recall condition."],
                    "danger_when": ["A synthetic overclaim condition."],
                    "failure_modes": ["A synthetic failure mode."],
                    "premortem_questions": ["A synthetic premortem question."],
                    "heuristics": ["A synthetic heuristic."],
                }
            }
        },
        affordances={
            "model_records": [
                {
                    "model_id": "empty-reviewed-record",
                    "status": "supported",
                    "affordances": [],
                    "absence_records": [],
                }
            ]
        },
        source_manifest={"files": []},
    )

    card = packet["candidate_cards"][0]
    assert card["coverage_status"] == "missing_reviewed_record"  # type: ignore[index]
    assert packet["coverage_summary"]["missing_reviewed_record_count"] == 1  # type: ignore[index]
    assert packet["coverage_summary"]["missing_reviewed_model_ids"] == [  # type: ignore[index]
        "empty-reviewed-record"
    ]
    assert packet["coverage_summary"]["high_value_graph_only_model_ids"] == []  # type: ignore[index]


def test_caps_dedupe_provenance_and_forbidden_fields() -> None:
    packet = _build_packet(
        [
            CandidateNomination(
                model_id="opportunity-cost",
                pulled_by=("lane4_gap_route",),
                why_pulled=(
                    {
                        "source": "lane4_gap_route",
                        "reason": "First nomination wins.",
                        "evidence_source_type": "lane_gap",
                    },
                ),
                lane_order=1,
            ),
            CandidateNomination(
                model_id="opportunity-cost",
                pulled_by=("reviewer_note",),
                why_pulled=(
                    {
                        "source": "reviewer_note",
                        "reason": "Duplicate nomination.",
                        "evidence_source_type": "reviewer_note",
                    },
                ),
                lane_order=2,
            ),
            CandidateNomination(
                model_id="chain-of-verification",
                pulled_by=("lane2_companion_chunk",),
                why_pulled=(
                    {
                        "source": "lane2_companion_chunk",
                        "reason": "Graph-only candidate should not be swallowed.",
                        "evidence_source_type": "assistant_turn",
                    },
                ),
                lane_order=3,
            ),
            CandidateNomination(
                model_id="game-theory-payoffs",
                pulled_by=("lane4_gap_route",),
                why_pulled=(
                    {
                        "source": "lane4_gap_route",
                        "reason": "Over cap candidate.",
                        "evidence_source_type": "lane_gap",
                    },
                ),
                lane_order=4,
            ),
        ],
        card_cap=2,
    )

    assert [card["model_id"] for card in packet["candidate_cards"]] == [  # type: ignore[index]
        "opportunity-cost",
        "chain-of-verification",
    ]
    assert packet["coverage_summary"]["candidate_card_count"] == 2  # type: ignore[index]
    assert packet["coverage_summary"]["reviewed_card_count"] == 1  # type: ignore[index]
    assert packet["coverage_summary"]["graph_only_card_count"] == 1  # type: ignore[index]

    suppressed_reasons = {
        item["model_id"]: item["suppression_reason"]
        for item in packet["suppressed_candidates"]  # type: ignore[index]
    }
    assert suppressed_reasons["opportunity-cost"] == "duplicate_model_id"
    assert suppressed_reasons["game-theory-payoffs"] == "packet_cap"

    forbidden_keys = {
        "final_decision_pressure",
        "selected_pressure",
        "best_pressure",
        "pressure",
        "user_facing_prose",
        "memo_copy",
        "rendered_html",
    }
    serialized = json.dumps(packet).lower()
    assert forbidden_keys.isdisjoint(_all_keys(packet))
    assert "final decision pressure" not in serialized
    assert "user_facing_prose" not in serialized


def test_live_runtime_paths_do_not_import_dormant_packet_producer() -> None:
    runtime_paths = [
        REPO_ROOT / "engine" / "system_b" / "pipeline.py",
        REPO_ROOT / "scripts" / "run_pipeline.py",
        REPO_ROOT / "engine" / "system_b" / "__init__.py",
    ]

    for path in runtime_paths:
        assert "reasoning_substrate_packet" not in path.read_text(encoding="utf-8")


def _all_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_all_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_all_keys(child))
    return keys
