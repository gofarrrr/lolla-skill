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
V8_FIXTURE_PATH = FIXTURE_DIR / "pr40_v8_execution_followthrough_packet_review.json"
V9_FIXTURE_PATH = FIXTURE_DIR / "pr40_v9_execution_followthrough_packet_review.json"
V8_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v8.json"
)
V9_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v9.json"
)
V8_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr40-v8-review-render-2026-05-07.md"
)
V9_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr40-v9-review-render-2026-05-07.md"
)
COMPARISON_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr40-v8-v9-comparison-render-2026-05-07.md"
)
LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)

PR39_UPGRADED_MODEL_IDS = {
    "algorithmic-thinking",
    "auditability-traceability",
    "baseline-establishment",
    "bottlenecks",
    "debugging-strategies",
    "devops-and-continuous-integration",
    "feedback-loops",
    "goal-setting",
    "habit-formation",
    "input-vs-output-goals",
    "iteration",
    "lean-startup-methodology",
}

TRANSACTION_CONTEXT = {
    "case_id": "pr40-execution-followthrough-review",
    "user_situation_summary": (
        "A small product team received AI advice for a six-week rescue plan "
        "after repeated launch slips, bug churn, weak adoption signals, and "
        "unclear ownership."
    ),
    "assistant_advice_summary": (
        "The assistant recommends setting goals, iterating weekly, getting "
        "feedback, improving CI, tracking progress, forming better habits, "
        "and focusing on the bottleneck, but it does not require baselines, "
        "audit trails, failure conditions, input/output separation, or "
        "stop-change thresholds."
    ),
    "known_action_or_commitment": (
        "Start the rescue plan Monday, assign owners, ship the next build in "
        "two weeks, and decide whether to continue after the first customer "
        "feedback cycle."
    ),
    "capture_health": "synthetic_review",
    "transaction_sources": ["user_turn", "assistant_turn", "reviewer_note"],
}


def test_pr40_v8_and_v9_fixtures_match_dormant_packet_producer_output() -> None:
    assert _load_json(V8_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr40-v8-execution-followthrough-packet-review",
        affordances_path=V8_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v8.json",
    )
    assert _load_json(V9_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr40-v9-execution-followthrough-packet-review",
        affordances_path=V9_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v9.json",
    )


def test_pr40_v9_fixture_upgrades_same_nominations_without_changing_count() -> None:
    v8_packet = _load_json(V8_FIXTURE_PATH)
    v9_packet = _load_json(V9_FIXTURE_PATH)

    assert len(v8_packet["candidate_cards"]) == 12
    assert len(v9_packet["candidate_cards"]) == 12
    assert len(v8_packet["suppressed_candidates"]) == 1
    assert len(v9_packet["suppressed_candidates"]) == 1

    assert v8_packet["coverage_summary"]["reviewed_card_count"] == 0
    assert v8_packet["coverage_summary"]["graph_only_card_count"] == 12
    assert set(v8_packet["coverage_summary"]["missing_reviewed_model_ids"]) == (
        PR39_UPGRADED_MODEL_IDS
    )

    assert v9_packet["coverage_summary"]["reviewed_card_count"] == 11
    assert v9_packet["coverage_summary"]["graph_only_card_count"] == 0
    assert v9_packet["coverage_summary"]["conflicting_or_weak_support_count"] == 1
    assert v9_packet["coverage_summary"]["missing_reviewed_model_ids"] == []


def test_pr40_v9_fixture_preserves_execution_depth_and_absence_signals() -> None:
    cards = _cards_by_model(_load_json(V9_FIXTURE_PATH))

    for model_id in PR39_UPGRADED_MODEL_IDS - {"devops-and-continuous-integration"}:
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

    devops = cards["devops-and-continuous-integration"]
    assert devops["coverage_status"] == "conflicting_or_weak_support"
    assert devops["source_custody"]["reviewed_record_available"] is True
    assert devops["reviewed_affordance_fields"]["affordance_ids"] == [
        "devops-and-continuous-integration.build-observe-adjust-loop"
    ]
    assert {
        str(absence["attempted_field"]) for absence in devops["absence_records"]
    } >= {"full-devops-ci-doctrine"}

    assert {
        str(absence["attempted_field"])
        for absence in cards["baseline-establishment"]["absence_records"]
    } >= {"obsolete-baseline-as-doctrine"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["bottlenecks"]["absence_records"]
    } >= {"noisiest-pain-point-as-bottleneck"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["iteration"]["absence_records"]
    } >= {"iteration-without-stop-rules"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["lean-startup-methodology"]["absence_records"]
    } >= {"vanity-metric-as-validated-learning"}


def test_pr40_review_renders_match_deterministic_renderer() -> None:
    v8_packet = _load_json(V8_FIXTURE_PATH)
    v9_packet = _load_json(V9_FIXTURE_PATH)

    assert V8_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v8_packet)
    )
    assert V9_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v9_packet)
    )
    assert COMPARISON_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_comparison_markdown(
            before_packet=v8_packet,
            after_packet=v9_packet,
        )
    )


def test_pr40_comparison_render_checks_handoff_delta_not_final_answer() -> None:
    markdown = COMPARISON_RENDER.read_text(encoding="utf-8")

    assert "| Candidate cards | 12 | 12 | 0 |" in markdown
    assert "| Reviewed cards | 0 | 11 | +11 |" in markdown
    assert "| Graph-only cards | 12 | 0 | -12 |" in markdown
    assert "| Weak/conflicting cards | 0 | 1 | +1 |" in markdown
    assert "`algorithmic-thinking`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`devops-and-continuous-integration`: `graph_only_runtime_card` -> `conflicting_or_weak_support`" in markdown
    assert "`lean-startup-methodology`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "Compare handoff usefulness only" in markdown
    assert "Do not answer the user case" in markdown
    assert "Do not choose user-visible output" in markdown
    assert "Pressure:" not in markdown
    assert "best pressure" not in markdown.lower()


def test_pr40_v9_fixture_contains_no_final_surface_or_live_runtime_import() -> None:
    packet = _load_json(V9_FIXTURE_PATH)
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
        "affordances_v9",
        "model_affordances_v9",
        "pr40_v9_execution_followthrough_packet_review",
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
        candidate_card_target_max=12,
        snippet_target_max_per_card=1,
    )


def _nominations() -> list[CandidateNomination]:
    return [
        CandidateNomination(
            model_id="baseline-establishment",
            pulled_by=("lane4_gap_route", "reviewer_note"),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The plan claims improvement without naming the "
                        "starting condition, metric, time window, or "
                        "comparison baseline."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "track progress",
                    "route_or_artifact_id": "synthetic-pr40-baseline-gap",
                },
            ),
            lane_order=1,
            lane_score=0.92,
        ),
        CandidateNomination(
            model_id="bottlenecks",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The rescue plan says to focus on the bottleneck but "
                        "does not prove which constraint actually limits "
                        "throughput."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "focus on the bottleneck",
                    "route_or_artifact_id": "synthetic-pr40-binding-constraint",
                },
            ),
            lane_order=2,
            lane_score=0.88,
        ),
        CandidateNomination(
            model_id="auditability-traceability",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The team is about to assign owners and commit to "
                        "actions, but the advice does not leave a trail of "
                        "decision, evidence, owner, and change trigger."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "assign owners",
                    "route_or_artifact_id": "synthetic-pr40-audit-trail",
                },
            ),
            lane_order=3,
            lane_score=0.84,
        ),
        CandidateNomination(
            model_id="debugging-strategies",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The plan responds to bug churn but does not define "
                        "the failure condition, isolate observed behavior, or "
                        "verify the root cause before fixing."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "bug churn",
                    "route_or_artifact_id": "synthetic-pr40-debugging-gap",
                },
            ),
            lane_order=4,
            lane_score=0.8,
        ),
        CandidateNomination(
            model_id="feedback-loops",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The assistant says to get feedback but does not say "
                        "which signal arrives soon enough to change the next "
                        "action."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "getting feedback",
                    "route_or_artifact_id": "synthetic-pr40-feedback-loop",
                },
            ),
            lane_order=5,
            lane_score=0.76,
        ),
        CandidateNomination(
            model_id="input-vs-output-goals",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The plan mixes lagging output goals with controllable "
                        "inputs, so the team may count activity as value."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "setting goals",
                    "route_or_artifact_id": "synthetic-pr40-input-output-goals",
                },
            ),
            lane_order=6,
            lane_score=0.72,
        ),
        CandidateNomination(
            model_id="iteration",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "Weekly iteration needs a hypothesis, feedback signal, "
                        "adjustment rule, and stop/change threshold, not an "
                        "endless loop of local polishing."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "iterating weekly",
                    "route_or_artifact_id": "synthetic-pr40-iteration-boundary",
                },
            ),
            lane_order=7,
            lane_score=0.68,
        ),
        CandidateNomination(
            model_id="lean-startup-methodology",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The first customer feedback cycle should reduce "
                        "uncertainty with a real learning metric and a "
                        "pivot/persevere threshold, not vanity validation."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "first customer feedback cycle",
                    "route_or_artifact_id": "synthetic-pr40-validated-learning",
                },
            ),
            lane_order=8,
            lane_score=0.64,
        ),
        CandidateNomination(
            model_id="algorithmic-thinking",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The rescue plan needs an explicit repeatable "
                        "procedure with inputs, ordered steps, outputs, and "
                        "failure handling before it can be handed off."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr40-repeatable-procedure",
                },
            ),
            lane_order=9,
            lane_score=0.6,
        ),
        CandidateNomination(
            model_id="devops-and-continuous-integration",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The advice mentions improving CI, but the packet "
                        "must protect reliability and rollback instead of "
                        "optimizing local delivery speed alone."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "improving CI",
                    "route_or_artifact_id": "synthetic-pr40-delivery-loop",
                },
            ),
            lane_order=10,
            lane_score=0.56,
        ),
        CandidateNomination(
            model_id="goal-setting",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The plan asks for goals, but goals need purpose, "
                        "metric, time boundary, progress check, and conflict "
                        "with other objectives."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "setting goals",
                    "route_or_artifact_id": "synthetic-pr40-goal-alignment",
                },
            ),
            lane_order=11,
            lane_score=0.52,
        ),
        CandidateNomination(
            model_id="habit-formation",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The team wants better execution habits, but the "
                        "packet should ask for cue, routine, reward, "
                        "environment, friction, and repeatability."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr40-execution-habit",
                },
            ),
            lane_order=12,
            lane_score=0.48,
        ),
        CandidateNomination(
            model_id="iteration",
            pulled_by=("reviewer_note",),
            why_pulled=(
                {
                    "source": "reviewer_note",
                    "reason": (
                        "Duplicate nomination included to prove suppression "
                        "is visible instead of silently erased."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr40-duplicate-check",
                },
            ),
            lane_order=13,
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
