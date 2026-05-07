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
V6_FIXTURE_PATH = FIXTURE_DIR / "pr35_v6_communication_competition_packet_review.json"
V7_FIXTURE_PATH = FIXTURE_DIR / "pr35_v7_communication_competition_packet_review.json"
V6_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v6.json"
)
V7_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v7.json"
)
V6_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr35-v6-review-render-2026-05-07.md"
)
V7_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr35-v7-review-render-2026-05-07.md"
)
COMPARISON_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr35-v6-v7-comparison-render-2026-05-07.md"
)
LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)

PR34_UPGRADED_MODEL_IDS = {
    "active-listening",
    "analogies-and-metaphors",
    "constructive-feedback-models",
    "feedback-models-sbi",
    "nash-equilibrium",
    "natural-selection-analogy",
    "prisoners-dilemma",
}

TRANSACTION_CONTEXT = {
    "case_id": "pr35-partner-feedback-competition-review",
    "user_situation_summary": (
        "A product team is deciding whether to confront a strategic partner, "
        "copy a competitor move, and deliver performance feedback after AI "
        "advice frames the situation as simple misalignment plus urgency."
    ),
    "assistant_advice_summary": (
        "The assistant recommends clarifying expectations, giving feedback, "
        "and matching the competitor quickly, but it does not test hidden "
        "incentives, equilibrium stability, mutual defection risk, listening "
        "quality, feedback specificity, or analogy fit."
    ),
    "known_action_or_commitment": (
        "Escalate the partner conversation, issue manager feedback, and copy "
        "the competitor launch pattern unless a review changes the plan."
    ),
    "capture_health": "synthetic_review",
    "transaction_sources": ["user_turn", "assistant_turn", "reviewer_note"],
}


def test_pr35_v6_and_v7_fixtures_match_dormant_packet_producer_output() -> None:
    assert _load_json(V6_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr35-v6-communication-competition-packet-review",
        affordances_path=V6_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v6.json",
    )
    assert _load_json(V7_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr35-v7-communication-competition-packet-review",
        affordances_path=V7_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v7.json",
    )


def test_pr35_v7_fixture_upgrades_same_nominations_without_changing_count() -> None:
    v6_packet = _load_json(V6_FIXTURE_PATH)
    v7_packet = _load_json(V7_FIXTURE_PATH)

    assert len(v6_packet["candidate_cards"]) == 9
    assert len(v7_packet["candidate_cards"]) == 9
    assert len(v6_packet["suppressed_candidates"]) == 1
    assert len(v7_packet["suppressed_candidates"]) == 1

    assert v6_packet["coverage_summary"]["reviewed_card_count"] == 2
    assert v6_packet["coverage_summary"]["graph_only_card_count"] == 7
    assert set(v6_packet["coverage_summary"]["missing_reviewed_model_ids"]) == (
        PR34_UPGRADED_MODEL_IDS
    )

    assert v7_packet["coverage_summary"]["reviewed_card_count"] == 9
    assert v7_packet["coverage_summary"]["graph_only_card_count"] == 0
    assert v7_packet["coverage_summary"]["missing_reviewed_model_ids"] == []


def test_pr35_v7_fixture_preserves_reviewed_depth_and_absence_signals() -> None:
    cards = _cards_by_model(_load_json(V7_FIXTURE_PATH))

    for model_id in PR34_UPGRADED_MODEL_IDS:
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
        for absence in cards["nash-equilibrium"]["absence_records"]
    } >= {"stable-outcome-equals-good-affordance"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["active-listening"]["absence_records"]
    } >= {"performative-listening-affordance"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["analogies-and-metaphors"]["absence_records"]
    } >= {"analogy-as-proof-affordance"}


def test_pr35_review_renders_match_deterministic_renderer() -> None:
    v6_packet = _load_json(V6_FIXTURE_PATH)
    v7_packet = _load_json(V7_FIXTURE_PATH)

    assert V6_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v6_packet)
    )
    assert V7_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v7_packet)
    )
    assert COMPARISON_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_comparison_markdown(
            before_packet=v6_packet,
            after_packet=v7_packet,
        )
    )


def test_pr35_comparison_render_checks_handoff_delta_not_final_answer() -> None:
    markdown = COMPARISON_RENDER.read_text(encoding="utf-8")

    assert "| Reviewed cards | 2 | 9 | +7 |" in markdown
    assert "| Graph-only cards | 7 | 0 | -7 |" in markdown
    assert "`nash-equilibrium`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`active-listening`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "Compare handoff usefulness only" in markdown
    assert "Do not answer the user case" in markdown
    assert "Do not choose user-visible output" in markdown
    assert "Pressure:" not in markdown
    assert "best pressure" not in markdown.lower()


def test_pr35_v7_fixture_contains_no_final_surface_or_live_runtime_import() -> None:
    packet = _load_json(V7_FIXTURE_PATH)
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
        "affordances_v7",
        "model_affordances_v7",
        "pr35_v7_communication_competition_packet_review",
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
        candidate_card_target_max=9,
        snippet_target_max_per_card=1,
    )


def _nominations() -> list[CandidateNomination]:
    return [
        CandidateNomination(
            model_id="game-theory-payoffs",
            pulled_by=("lane2_companion_chunk", "reviewer_note"),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The assistant assumes partner and competitor responses "
                        "will stay stable after the team escalates."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "route_or_artifact_id": "synthetic-pr35-payoff-response",
                },
            ),
            lane_order=1,
            lane_score=0.9,
        ),
        CandidateNomination(
            model_id="nash-equilibrium",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The plan assumes unilateral clarification will shift "
                        "behavior without checking whether each party's current "
                        "move is already a stable best response."
                    ),
                    "evidence_source_type": "lane_gap",
                    "route_or_artifact_id": "synthetic-pr35-stable-response",
                },
            ),
            lane_order=2,
            lane_score=0.84,
        ),
        CandidateNomination(
            model_id="prisoners-dilemma",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The partner conversation is framed as alignment, but "
                        "both sides may have incentives to defect or withhold."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "they say they are aligned but keep delaying",
                    "route_or_artifact_id": "synthetic-pr35-mutual-defection",
                },
            ),
            lane_order=3,
            lane_score=0.81,
        ),
        CandidateNomination(
            model_id="cross-cultural-communication-frameworks",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The feedback and partner messages must carry across "
                        "function, status, and regional frames."
                    ),
                    "evidence_source_type": "user_turn",
                    "route_or_artifact_id": "synthetic-pr35-frame-translation",
                },
            ),
            lane_order=4,
            lane_score=0.78,
        ),
        CandidateNomination(
            model_id="active-listening",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The team plans to give feedback before proving it has "
                        "heard the partner's actual constraint or disagreement."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "clarify expectations",
                    "route_or_artifact_id": "synthetic-pr35-listening-gap",
                },
            ),
            lane_order=5,
            lane_score=0.74,
        ),
        CandidateNomination(
            model_id="constructive-feedback-models",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The manager feedback plan lacks a specific behavior, "
                        "standard, and correction path."
                    ),
                    "evidence_source_type": "lane_gap",
                    "route_or_artifact_id": "synthetic-pr35-feedback-specificity",
                },
            ),
            lane_order=6,
            lane_score=0.7,
        ),
        CandidateNomination(
            model_id="feedback-models-sbi",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The assistant recommends feedback without separating "
                        "situation, behavior, impact, and invitation."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "give feedback",
                    "route_or_artifact_id": "synthetic-pr35-sbi-gap",
                },
            ),
            lane_order=7,
            lane_score=0.67,
        ),
        CandidateNomination(
            model_id="analogies-and-metaphors",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The team is tempted to copy the competitor launch as "
                        "an analogy without testing structural fit."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "their launch playbook worked",
                    "route_or_artifact_id": "synthetic-pr35-analogy-fit",
                },
            ),
            lane_order=8,
            lane_score=0.64,
        ),
        CandidateNomination(
            model_id="natural-selection-analogy",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The competitive story treats survival of a pattern as "
                        "proof it is optimal rather than testing variation, "
                        "selection, and retention conditions."
                    ),
                    "evidence_source_type": "user_turn",
                    "route_or_artifact_id": "synthetic-pr35-adaptive-pattern",
                },
            ),
            lane_order=9,
            lane_score=0.6,
        ),
        CandidateNomination(
            model_id="game-theory-payoffs",
            pulled_by=("reviewer_note",),
            why_pulled=(
                {
                    "source": "reviewer_note",
                    "reason": (
                        "Duplicate nomination included to prove suppression "
                        "is visible instead of silently erased."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr35-duplicate-check",
                },
            ),
            lane_order=10,
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
