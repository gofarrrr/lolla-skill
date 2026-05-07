from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from engine.system_b.reasoning_substrate_packet import (
    CandidateNomination,
    build_reasoning_substrate_packet,
)
from engine.system_b.reasoning_substrate_packet_review import (
    render_reasoning_substrate_packet_comparison_markdown,
    render_reasoning_substrate_packet_review_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "reasoning_substrate_packet"
V7_FIXTURE_PATH = FIXTURE_DIR / "pr37_v7_trust_negotiation_packet_review.json"
V8_FIXTURE_PATH = FIXTURE_DIR / "pr37_v8_trust_negotiation_packet_review.json"
V7_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v7.json"
)
V8_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v8.json"
)
V7_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr37-v7-review-render-2026-05-07.md"
)
V8_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr37-v8-review-render-2026-05-07.md"
)
COMPARISON_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr37-v7-v8-comparison-render-2026-05-07.md"
)
LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)

PR36_UPGRADED_MODEL_IDS = {
    "authenticity",
    "boundaries",
    "emotional-intelligence",
    "hanlons-razor",
    "international-negotiation-and-diplomacy-models",
    "non-violent-communication",
    "persuasion-principles",
    "reciprocity-principle",
    "signaling",
    "understanding-motivations",
}

TRANSACTION_CONTEXT = {
    "case_id": "pr37-trust-repair-negotiation-review",
    "user_situation_summary": (
        "A founder must repair a damaged partner relationship, set boundaries "
        "with an internal lead, and negotiate a delayed rollout after AI advice "
        "frames the issue as communication cleanup plus stronger persuasion."
    ),
    "assistant_advice_summary": (
        "The assistant recommends being transparent, empathizing, setting "
        "expectations, making a reciprocal offer, and signaling commitment, "
        "but it does not separate needs from accusations, hidden motivations "
        "from mind-reading, boundaries from avoidance, or costly proof from "
        "cheap theater."
    ),
    "known_action_or_commitment": (
        "Send the partner repair note, reset internal ownership boundaries, "
        "offer a concession, and ask for a public commitment this week unless "
        "a review changes the plan."
    ),
    "capture_health": "synthetic_review",
    "transaction_sources": ["user_turn", "assistant_turn", "reviewer_note"],
}


def test_pr37_v7_and_v8_fixtures_match_dormant_packet_producer_output() -> None:
    assert _load_json(V7_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr37-v7-trust-negotiation-packet-review",
        affordances_path=V7_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v7.json",
    )
    assert _load_json(V8_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr37-v8-trust-negotiation-packet-review",
        affordances_path=V8_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v8.json",
    )


def test_pr37_v8_fixture_upgrades_same_nominations_without_changing_count() -> None:
    v7_packet = _load_json(V7_FIXTURE_PATH)
    v8_packet = _load_json(V8_FIXTURE_PATH)

    assert len(v7_packet["candidate_cards"]) == 10
    assert len(v8_packet["candidate_cards"]) == 10
    assert len(v7_packet["suppressed_candidates"]) == 1
    assert len(v8_packet["suppressed_candidates"]) == 1

    assert v7_packet["coverage_summary"]["reviewed_card_count"] == 0
    assert v7_packet["coverage_summary"]["graph_only_card_count"] == 10
    assert set(v7_packet["coverage_summary"]["missing_reviewed_model_ids"]) == (
        PR36_UPGRADED_MODEL_IDS
    )

    assert v8_packet["coverage_summary"]["reviewed_card_count"] == 10
    assert v8_packet["coverage_summary"]["graph_only_card_count"] == 0
    assert v8_packet["coverage_summary"]["missing_reviewed_model_ids"] == []


def test_pr37_v8_fixture_preserves_reviewed_depth_and_absence_signals() -> None:
    cards = _cards_by_model(_load_json(V8_FIXTURE_PATH))

    for model_id in PR36_UPGRADED_MODEL_IDS:
        card = cards[model_id]
        assert card["coverage_status"] == "reviewed_affordance_available"
        assert card["source_custody"]["custody_status"] == "repo_source_custodied"
        assert card["source_custody"]["reviewed_record_available"] is True
        assert card["source_custody"]["reviewed_affordance_available"] is True
        reviewed = card["reviewed_affordance_fields"]
        assert reviewed["affordance_ids"]
        assert reviewed["use_when"]
        assert reviewed["case_evidence_needed"]
        assert reviewed["do_not_use_when"]
        assert reviewed["treatment_requirements"]
        assert reviewed["diagnostic_questions"]
        assert reviewed["misuse_guards"]
        assert reviewed["source_evidence"]
        assert card["absence_records"]

    assert {
        str(absence["attempted_field"])
        for absence in cards["non-violent-communication"]["absence_records"]
    } >= {"conflict-avoidance-affordance"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["boundaries"]["absence_records"]
    } >= {"comfort-protection-boundary"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["persuasion-principles"]["absence_records"]
    } >= {"better-packaging-for-weak-answer"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["signaling"]["absence_records"]
    } >= {"cheap-symbolic-signal-as-proof"}


def test_pr37_review_renders_match_deterministic_renderer() -> None:
    v7_packet = _load_json(V7_FIXTURE_PATH)
    v8_packet = _load_json(V8_FIXTURE_PATH)

    assert V7_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v7_packet)
    )
    assert V8_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v8_packet)
    )
    assert COMPARISON_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_comparison_markdown(
            before_packet=v7_packet,
            after_packet=v8_packet,
        )
    )


def test_pr37_comparison_render_checks_handoff_delta_not_final_answer() -> None:
    markdown = COMPARISON_RENDER.read_text(encoding="utf-8")

    assert "| Reviewed cards | 0 | 10 | +10 |" in markdown
    assert "| Graph-only cards | 10 | 0 | -10 |" in markdown
    assert "`non-violent-communication`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`signaling`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "Compare handoff usefulness only" in markdown
    assert "Do not answer the user case" in markdown
    assert "Do not choose user-visible output" in markdown
    assert "Pressure:" not in markdown
    assert "best pressure" not in markdown.lower()


def test_pr37_v8_fixture_contains_no_final_surface_or_live_runtime_import() -> None:
    packet = _load_json(V8_FIXTURE_PATH)
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

    forbidden_fragments = (
        "affordances_v8",
        "model_affordances_v8",
        "pr37_v8_trust_negotiation_packet_review",
        "reasoning_substrate_packet_review",
    )
    for path in LIVE_RUNTIME_PATHS:
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in forbidden_fragments)


def _build_expected_packet(
    *,
    packet_id: str,
    affordances_path: Path,
    affordances_artifact: str,
) -> dict[str, Any]:
    return build_reasoning_substrate_packet(
        packet_id=packet_id,
        transaction_context=TRANSACTION_CONTEXT,
        nominations=_nominations(),
        knowledge_graph=_load_json(REPO_ROOT / "data" / "knowledge_graph.json"),
        affordances=_load_json(affordances_path),
        source_manifest=_load_json(
            REPO_ROOT / "data" / "model_sources" / "manifest.json"
        ),
        source_artifacts=[
            "data/knowledge_graph.json",
            affordances_artifact,
            "data/model_sources/manifest.json",
        ],
        candidate_card_target_max=10,
        snippet_target_max_per_card=1,
    )


def _nominations() -> list[CandidateNomination]:
    return [
        CandidateNomination(
            model_id="non-violent-communication",
            pulled_by=("lane1_tendency_route", "reviewer_note"),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The repair note risks mixing accusation, need, and "
                        "request instead of making the relationship concern "
                        "observable and actionable."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "be transparent and empathize",
                    "route_or_artifact_id": "synthetic-pr37-repair-note",
                },
            ),
            lane_order=1,
            lane_score=0.9,
        ),
        CandidateNomination(
            model_id="emotional-intelligence",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The plan treats emotional landing as style rather "
                        "than evidence about adoption, fairness, and trust."
                    ),
                    "evidence_source_type": "user_turn",
                    "route_or_artifact_id": "synthetic-pr37-emotional-landing",
                },
            ),
            lane_order=2,
            lane_score=0.86,
        ),
        CandidateNomination(
            model_id="understanding-motivations",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The assistant infers resistance but does not test "
                        "hidden drivers against observable behavior or "
                        "disconfirming evidence."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "they may need more reassurance",
                    "route_or_artifact_id": "synthetic-pr37-hidden-driver",
                },
            ),
            lane_order=3,
            lane_score=0.82,
        ),
        CandidateNomination(
            model_id="boundaries",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The internal reset needs a line between ownership, "
                        "influence, and excluded work instead of a vague "
                        "expectation reset."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "reset internal ownership boundaries",
                    "route_or_artifact_id": "synthetic-pr37-ownership-boundary",
                },
            ),
            lane_order=4,
            lane_score=0.78,
        ),
        CandidateNomination(
            model_id="authenticity",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The founder wants candor that rebuilds trust, but "
                        "candor must stay congruent with evidence and "
                        "accountability."
                    ),
                    "evidence_source_type": "user_turn",
                    "route_or_artifact_id": "synthetic-pr37-candor-substance",
                },
            ),
            lane_order=5,
            lane_score=0.74,
        ),
        CandidateNomination(
            model_id="hanlons-razor",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The partner delay may be malice, overload, incentives, "
                        "or coordination failure; the plan should not jump to "
                        "intent attribution."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "they keep stalling",
                    "route_or_artifact_id": "synthetic-pr37-intent-attribution",
                },
            ),
            lane_order=6,
            lane_score=0.7,
        ),
        CandidateNomination(
            model_id="reciprocity-principle",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The concession is meant to rebuild trust before an "
                        "ask, but the packet needs to distinguish real value "
                        "from obligation pressure."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "offer a concession",
                    "route_or_artifact_id": "synthetic-pr37-reciprocal-value",
                },
            ),
            lane_order=7,
            lane_score=0.66,
        ),
        CandidateNomination(
            model_id="persuasion-principles",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The adoption plan may need better framing, but only "
                        "if persuasion preserves evidence, autonomy, and "
                        "substance."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "make the case more compelling",
                    "route_or_artifact_id": "synthetic-pr37-substance-preserving-adoption",
                },
            ),
            lane_order=8,
            lane_score=0.62,
        ),
        CandidateNomination(
            model_id="international-negotiation-and-diplomacy-models",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The rollout delay involves substance, signaling, "
                        "stakeholders, concessions, and sequencing across more "
                        "than one party."
                    ),
                    "evidence_source_type": "lane_gap",
                    "route_or_artifact_id": "synthetic-pr37-settlement-map",
                },
            ),
            lane_order=9,
            lane_score=0.58,
        ),
        CandidateNomination(
            model_id="signaling",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The public commitment request needs costly proof of "
                        "intent rather than a cheap symbolic promise."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "ask for a public commitment",
                    "route_or_artifact_id": "synthetic-pr37-costly-proof",
                },
            ),
            lane_order=10,
            lane_score=0.54,
        ),
        CandidateNomination(
            model_id="signaling",
            pulled_by=("reviewer_note",),
            why_pulled=(
                {
                    "source": "reviewer_note",
                    "reason": (
                        "Duplicate nomination included to prove suppression "
                        "is visible instead of silently erased."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr37-duplicate-check",
                },
            ),
            lane_order=11,
            lane_score=0.2,
        ),
    ]


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
