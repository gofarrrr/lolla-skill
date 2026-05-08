from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.reasoning_substrate_packet import (
    CandidateNomination,
    build_reasoning_substrate_packet,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "reasoning_substrate_packet"
    / "pr27_mixed_packet_review.json"
)


TRANSACTION_CONTEXT = {
    "case_id": "pr27-synthetic-renewal-rollout-review",
    "user_situation_summary": (
        "A team is about to renew a vendor contract and rush a product rollout "
        "after receiving plausible AI advice that frames speed as the main win."
    ),
    "assistant_advice_summary": (
        "The assistant recommends moving quickly, negotiating lightly, and "
        "tracking risks after launch, but it does not name the displaced "
        "alternative, kill criteria, or verification chain."
    ),
    "known_action_or_commitment": (
        "Renew the vendor and launch within two weeks unless a review changes "
        "the commitment."
    ),
    "capture_health": "synthetic_review",
    "transaction_sources": ["user_turn", "assistant_turn", "reviewer_note"],
}


def test_pr27_fixture_matches_dormant_packet_producer_output() -> None:
    fixture = _load_fixture()
    expected = _build_expected_packet()

    assert fixture == expected


def test_pr27_fixture_is_dormant_reasoning_substrate_packet_v1() -> None:
    packet = _load_fixture()

    assert packet["packet_version"] == "reasoning_substrate_packet.v1"
    assert packet["packet_id"] == "pr27-mixed-packet-review"
    assert packet["status"] == "draft_review_only"
    assert packet["runtime_policy"] == "runtime_dormant"
    assert packet["transaction_context"] == TRANSACTION_CONTEXT
    assert set(packet) >= {
        "source_artifacts",
        "candidate_cards",
        "suppressed_candidates",
        "coverage_summary",
        "packet_policy",
        "blocked_surfaces",
        "review_notes",
    }
    assert len(packet["candidate_cards"]) <= packet["packet_policy"][
        "candidate_card_target_max"
    ]
    assert packet["blocked_surfaces"] == [
        "live_observatory_rendering",
        "memo_integration",
        "step8_integration",
        "step6_integration",
        "lane4_integration",
        "lolla_runtime_use",
        "user_facing_decision_pressure_block",
        "prompt_changes",
        "generation_changes",
        "new_extraction",
        "batch_3b",
        "paid_gate4_reruns_by_default",
    ]


def test_pr27_fixture_mixes_v4_graph_only_and_suppressed_candidates() -> None:
    packet = _load_fixture()
    cards = _cards_by_model(packet)

    assert len(packet["candidate_cards"]) == 7
    assert packet["coverage_summary"]["candidate_card_count"] == 7
    assert packet["coverage_summary"]["reviewed_card_count"] == 3
    assert packet["coverage_summary"]["graph_only_card_count"] == 4
    assert packet["coverage_summary"]["high_value_graph_only_model_ids"] == [
        "chain-of-verification",
        "confirmation-bias",
        "constraints",
        "step-back",
    ]
    assert packet["coverage_summary"]["missing_reviewed_model_ids"] == [
        "chain-of-verification",
        "confirmation-bias",
        "constraints",
        "step-back",
    ]

    suppressed = packet["suppressed_candidates"]
    assert len(suppressed) == 1
    assert suppressed[0]["model_id"] == "opportunity-cost"
    assert suppressed[0]["suppression_reason"] == "duplicate_model_id"
    assert suppressed[0]["do_not_recover_as_pressure_without_review"] is True

    for model_id in (
        "opportunity-cost",
        "falsifiability",
        "probabilistic-thinking",
    ):
        card = cards[model_id]
        assert card["coverage_status"] == "reviewed_affordance_available"
        assert card["reviewed_affordance_fields"]["affordance_ids"]
        assert card["reviewed_affordance_fields"]["source_evidence"]
        assert card["source_custody"]["custody_status"] == "repo_source_custodied"
        assert card["source_custody"]["reviewed_record_available"] is True
        assert card["source_custody"]["reviewed_affordance_available"] is True

    for model_id in (
        "step-back",
        "constraints",
        "chain-of-verification",
        "confirmation-bias",
    ):
        card = cards[model_id]
        assert card["coverage_status"] == "graph_only_runtime_card"
        assert card["reviewed_affordance_fields"] == {}
        assert card["source_custody"]["custody_status"] == "repo_source_custodied"
        assert card["source_custody"]["reviewed_record_available"] is False
        assert card["source_custody"]["reviewed_affordance_available"] is False
        assert card["source_custody"]["manifest_path"].startswith("data/model_sources/")
        assert "No reviewed affordance record" in card["do_not_overclaim"][0]


def test_pr27_fixture_preserves_provenance_and_contains_no_final_surface() -> None:
    packet = _load_fixture()
    cards = _cards_by_model(packet)

    assert cards["opportunity-cost"]["pulled_by"] == [
        "lane4_gap_route",
        "reviewer_note",
    ]
    assert cards["opportunity-cost"]["why_pulled"][0] == {
        "source": "lane4_gap_route",
        "reason": (
            "The advice commits the same budget and launch window without "
            "naming the displaced alternative."
        ),
        "evidence_source_type": "lane_gap",
        "route_or_artifact_id": "synthetic-lane4-resource-commitment",
    }
    assert cards["chain-of-verification"]["why_pulled"][0]["evidence_quote"] == (
        "track risks after launch"
    )

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
    assert "user-facing prose" not in serialized
    assert "memo copy" not in serialized
    assert "rendered_html" not in serialized


def _build_expected_packet() -> dict[str, Any]:
    return build_reasoning_substrate_packet(
        packet_id="pr27-mixed-packet-review",
        transaction_context=TRANSACTION_CONTEXT,
        nominations=_nominations(),
        knowledge_graph=_load_json(REPO_ROOT / "data" / "knowledge_graph.json"),
        affordances=_load_json(
            REPO_ROOT
            / "data"
            / "compiled"
            / "model_affordances"
            / "affordances_v4.json"
        ),
        source_manifest=_load_json(
            REPO_ROOT / "data" / "model_sources" / "manifest.json"
        ),
        source_artifacts=[
            "data/knowledge_graph.json",
            "data/compiled/model_affordances/affordances_v4.json",
            "data/model_sources/manifest.json",
        ],
        candidate_card_target_max=8,
        snippet_target_max_per_card=1,
    )


def _nominations() -> list[CandidateNomination]:
    return [
        CandidateNomination(
            model_id="opportunity-cost",
            pulled_by=("lane4_gap_route", "reviewer_note"),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The advice commits the same budget and launch window "
                        "without naming the displaced alternative."
                    ),
                    "evidence_source_type": "lane_gap",
                    "route_or_artifact_id": "synthetic-lane4-resource-commitment",
                },
            ),
            lane_order=1,
            lane_score=0.91,
        ),
        CandidateNomination(
            model_id="falsifiability",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The assistant treats the rollout thesis as plausible "
                        "without naming what evidence would reverse it."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "move quickly",
                    "route_or_artifact_id": "synthetic-lane2-thesis-test",
                },
            ),
            lane_order=2,
            lane_score=0.84,
        ),
        CandidateNomination(
            model_id="probabilistic-thinking",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The user frame collapses uncertain renewal and "
                        "launch outcomes into a go/no-go decision."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "we probably just need to decide now",
                    "route_or_artifact_id": "synthetic-lane3-binary-frame",
                },
            ),
            lane_order=3,
            lane_score=0.8,
        ),
        CandidateNomination(
            model_id="step-back",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The case is moving from urgency into commitment "
                        "before restating the governing purpose."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "we are running out of time",
                    "route_or_artifact_id": "synthetic-lane3-urgency-frame",
                },
            ),
            lane_order=4,
            lane_score=0.72,
        ),
        CandidateNomination(
            model_id="constraints",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The plan does not state which scope, budget, or "
                        "launch constraints govern the trade-off."
                    ),
                    "evidence_source_type": "lane_gap",
                    "route_or_artifact_id": "synthetic-lane4-constraint-gap",
                },
            ),
            lane_order=5,
            lane_score=0.69,
        ),
        CandidateNomination(
            model_id="chain-of-verification",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The assistant defers verification until after action "
                        "even though several premises must hold in sequence."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "track risks after launch",
                    "route_or_artifact_id": "synthetic-lane2-verification-chain",
                },
            ),
            lane_order=6,
            lane_score=0.66,
        ),
        CandidateNomination(
            model_id="confirmation-bias",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The transaction suggests convergence on the preferred "
                        "renewal answer before disconfirming evidence is named."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "route_or_artifact_id": "synthetic-lane1-confirming-evidence",
                },
            ),
            lane_order=7,
            lane_score=0.61,
        ),
        CandidateNomination(
            model_id="opportunity-cost",
            pulled_by=("reviewer_note",),
            why_pulled=(
                {
                    "source": "reviewer_note",
                    "reason": (
                        "Duplicate nomination included to prove suppression is "
                        "visible instead of silently erased."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-duplicate-check",
                },
            ),
            lane_order=8,
            lane_score=0.2,
        ),
    ]


def _load_fixture() -> dict[str, Any]:
    return _load_json(FIXTURE_PATH)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path}: expected JSON object")
    return payload


def _cards_by_model(packet: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(card["model_id"]): card for card in packet["candidate_cards"]}


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
