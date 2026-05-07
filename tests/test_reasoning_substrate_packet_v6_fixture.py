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
V5_FIXTURE_PATH = FIXTURE_DIR / "pr33_v5_capability_gap_packet_review.json"
V6_FIXTURE_PATH = FIXTURE_DIR / "pr33_v6_capability_gap_packet_review.json"
V5_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v5.json"
)
V6_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v6.json"
)
V5_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr33-v5-review-render-2026-05-07.md"
)
V6_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr33-v6-review-render-2026-05-07.md"
)
COMPARISON_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr33-v5-v6-comparison-render-2026-05-07.md"
)
LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)

PR32_UPGRADED_MODEL_IDS = {
    "batna",
    "cross-cultural-communication-frameworks",
    "delays",
    "game-theory-payoffs",
    "jobs-to-be-done",
    "lock-in",
    "obligations-controls-mapping",
    "path-dependence",
    "red-queen-effect",
}

TRANSACTION_CONTEXT = {
    "case_id": "pr33-international-platform-renewal-review",
    "user_situation_summary": (
        "A team is considering renewing an incumbent platform, entering two "
        "international segments, and accelerating roadmap commitments after "
        "receiving plausible AI advice that favors speed and continuity."
    ),
    "assistant_advice_summary": (
        "The assistant recommends staying with the incumbent vendor, launching "
        "quickly, and handling adoption issues after rollout, but it does not "
        "price lock-in, fallback credibility, counterparty response, customer "
        "job evidence, cross-cultural interpretation, or delayed feedback."
    ),
    "known_action_or_commitment": (
        "Renew the platform and commit the international rollout plan unless "
        "reviewed shelf evidence changes the decision record."
    ),
    "capture_health": "synthetic_review",
    "transaction_sources": ["user_turn", "assistant_turn", "reviewer_note"],
}


def test_pr33_v5_and_v6_fixtures_match_dormant_packet_producer_output() -> None:
    assert _load_json(V5_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr33-v5-capability-gap-packet-review",
        affordances_path=V5_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v5.json",
    )
    assert _load_json(V6_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr33-v6-capability-gap-packet-review",
        affordances_path=V6_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v6.json",
    )


def test_pr33_v6_fixture_upgrades_same_nominations_without_changing_count() -> None:
    v5_packet = _load_json(V5_FIXTURE_PATH)
    v6_packet = _load_json(V6_FIXTURE_PATH)

    assert len(v5_packet["candidate_cards"]) == 10
    assert len(v6_packet["candidate_cards"]) == 10
    assert len(v5_packet["suppressed_candidates"]) == 1
    assert len(v6_packet["suppressed_candidates"]) == 1

    assert v5_packet["coverage_summary"]["reviewed_card_count"] == 1
    assert v5_packet["coverage_summary"]["graph_only_card_count"] == 9
    assert set(v5_packet["coverage_summary"]["missing_reviewed_model_ids"]) == (
        PR32_UPGRADED_MODEL_IDS
    )

    assert v6_packet["coverage_summary"]["reviewed_card_count"] == 10
    assert v6_packet["coverage_summary"]["graph_only_card_count"] == 0
    assert v6_packet["coverage_summary"]["missing_reviewed_model_ids"] == []


def test_pr33_v6_fixture_preserves_reviewed_depth_and_absence_signals() -> None:
    cards = _cards_by_model(_load_json(V6_FIXTURE_PATH))

    for model_id in PR32_UPGRADED_MODEL_IDS:
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

    assert cards["batna"]["reviewed_affordance_fields"]["confidence"] == "medium"
    assert {
        str(absence["attempted_field"]) for absence in cards["batna"]["absence_records"]
    } >= {"textbook-batna-definition-affordance"}
    assert {
        str(absence["attempted_field"]) for absence in cards["delays"]["absence_records"]
    } >= {"romanticized-waiting-affordance"}


def test_pr33_review_renders_match_deterministic_renderer() -> None:
    v5_packet = _load_json(V5_FIXTURE_PATH)
    v6_packet = _load_json(V6_FIXTURE_PATH)

    assert V5_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v5_packet)
    )
    assert V6_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v6_packet)
    )
    assert COMPARISON_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_comparison_markdown(
            before_packet=v5_packet,
            after_packet=v6_packet,
        )
    )


def test_pr33_comparison_render_checks_handoff_delta_not_final_answer() -> None:
    markdown = COMPARISON_RENDER.read_text(encoding="utf-8")

    assert "| Reviewed cards | 1 | 10 | +9 |" in markdown
    assert "| Graph-only cards | 9 | 0 | -9 |" in markdown
    assert "`batna`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`lock-in`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "Compare handoff usefulness only" in markdown
    assert "Do not answer the user case" in markdown
    assert "Do not choose user-visible output" in markdown
    assert "Pressure:" not in markdown
    assert "best pressure" not in markdown.lower()


def test_pr33_v6_fixture_contains_no_final_surface_or_live_runtime_import() -> None:
    packet = _load_json(V6_FIXTURE_PATH)
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
        "affordances_v6",
        "model_affordances_v6",
        "pr33_v6_capability_gap_packet_review",
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
            model_id="opportunity-cost",
            pulled_by=("lane4_gap_route", "reviewer_note"),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The advice commits the same team and launch window "
                        "without naming the displaced alternative."
                    ),
                    "evidence_source_type": "lane_gap",
                    "route_or_artifact_id": "synthetic-pr33-displaced-alternative",
                },
            ),
            lane_order=1,
            lane_score=0.91,
        ),
        CandidateNomination(
            model_id="batna",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The renewal advice treats staying with the incumbent "
                        "as the only credible path without testing a walk-away option."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "renew the platform",
                    "route_or_artifact_id": "synthetic-pr33-fallback-gap",
                },
            ),
            lane_order=2,
            lane_score=0.86,
        ),
        CandidateNomination(
            model_id="game-theory-payoffs",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The assistant assumes vendor and competitor responses "
                        "will stay stable after the team commits publicly."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "route_or_artifact_id": "synthetic-pr33-counterparty-response",
                },
            ),
            lane_order=3,
            lane_score=0.82,
        ),
        CandidateNomination(
            model_id="red-queen-effect",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The user frame treats speed as advantage without "
                        "separating genuine progress from keeping up."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "we cannot afford to stand still",
                    "route_or_artifact_id": "synthetic-pr33-relative-position",
                },
            ),
            lane_order=4,
            lane_score=0.78,
        ),
        CandidateNomination(
            model_id="delays",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The advice postpones adoption learning until after "
                        "launch without naming the feedback lag or review window."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "handle adoption issues after rollout",
                    "route_or_artifact_id": "synthetic-pr33-feedback-lag",
                },
            ),
            lane_order=5,
            lane_score=0.74,
        ),
        CandidateNomination(
            model_id="obligations-controls-mapping",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The plan names international commitments without "
                        "mapping the obligation owner, control, evidence, or cadence."
                    ),
                    "evidence_source_type": "lane_gap",
                    "route_or_artifact_id": "synthetic-pr33-control-gap",
                },
            ),
            lane_order=6,
            lane_score=0.71,
        ),
        CandidateNomination(
            model_id="jobs-to-be-done",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The advice treats requested features as demand without "
                        "checking the customer progress job behind adoption."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "customers asked for easier integration",
                    "route_or_artifact_id": "synthetic-pr33-customer-job",
                },
            ),
            lane_order=7,
            lane_score=0.68,
        ),
        CandidateNomination(
            model_id="lock-in",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The renewal advice defers reversal-cost analysis until "
                        "after another integration cycle."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "route_or_artifact_id": "synthetic-pr33-lock-in-risk",
                },
            ),
            lane_order=8,
            lane_score=0.66,
        ),
        CandidateNomination(
            model_id="path-dependence",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The assistant treats the current installed path as "
                        "neutral rather than as a constraint on future options."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "route_or_artifact_id": "synthetic-pr33-installed-path",
                },
            ),
            lane_order=9,
            lane_score=0.63,
        ),
        CandidateNomination(
            model_id="cross-cultural-communication-frameworks",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The international rollout assumes the same message "
                        "will carry across regions without translating frames into action."
                    ),
                    "evidence_source_type": "user_turn",
                    "route_or_artifact_id": "synthetic-pr33-cross-cultural-frame",
                },
            ),
            lane_order=10,
            lane_score=0.59,
        ),
        CandidateNomination(
            model_id="opportunity-cost",
            pulled_by=("reviewer_note",),
            why_pulled=(
                {
                    "source": "reviewer_note",
                    "reason": (
                        "Duplicate nomination included to prove suppression "
                        "is visible instead of silently erased."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr33-duplicate-check",
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
