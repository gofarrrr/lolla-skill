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
V9_FIXTURE_PATH = FIXTURE_DIR / "pr43_v9_risk_reversibility_packet_review.json"
V10_FIXTURE_PATH = FIXTURE_DIR / "pr43_v10_risk_reversibility_packet_review.json"
V9_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v9.json"
)
V10_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v10.json"
)
V9_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr43-v9-review-render-2026-05-07.md"
)
V10_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr43-v10-review-render-2026-05-07.md"
)
COMPARISON_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr43-v9-v10-comparison-render-2026-05-07.md"
)
LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)

PR42_UPGRADED_MODEL_IDS = {
    "risk-vs-uncertainty",
    "redundancy",
    "regulatory-horizon-scanning",
    "cybersecurity-thinking-models",
    "non-linear-dynamics",
    "tipping-points",
    "butterfly-effect",
    "chaos-theory",
    "combinatorial-effects",
    "critical-mass",
    "switching-costs",
    "prospect-theory",
}

TRANSACTION_CONTEXT = {
    "case_id": "pr43-risk-reversibility-review",
    "user_situation_summary": (
        "A founder is considering AI advice to commit to a regulated market "
        "entry, migrate a core workflow to a new vendor, and accelerate launch "
        "after early customer interest."
    ),
    "assistant_advice_summary": (
        "The assistant recommends a staged launch, monitoring regulatory news, "
        "adding backups, improving security, and moving fast while learning, "
        "but it does not require commitment sizing, independent fallback tests, "
        "weak-signal triggers, cascade paths, threshold evidence, exit "
        "governance, or loss-frame checks."
    ),
    "known_action_or_commitment": (
        "Approve the market-entry budget, start vendor migration, and decide "
        "within six weeks whether to double down or unwind."
    ),
    "capture_health": "synthetic_review",
    "transaction_sources": ["user_turn", "assistant_turn", "reviewer_note"],
}


def test_pr43_v9_and_v10_fixtures_match_dormant_packet_producer_output() -> None:
    assert _load_json(V9_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr43-v9-risk-reversibility-packet-review",
        affordances_path=V9_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v9.json",
    )
    assert _load_json(V10_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr43-v10-risk-reversibility-packet-review",
        affordances_path=V10_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v10.json",
    )


def test_pr43_v10_fixture_upgrades_same_nominations_without_changing_count() -> None:
    v9_packet = _load_json(V9_FIXTURE_PATH)
    v10_packet = _load_json(V10_FIXTURE_PATH)

    assert len(v9_packet["candidate_cards"]) == 12
    assert len(v10_packet["candidate_cards"]) == 12
    assert len(v9_packet["suppressed_candidates"]) == 1
    assert len(v10_packet["suppressed_candidates"]) == 1

    assert v9_packet["coverage_summary"]["reviewed_card_count"] == 0
    assert v9_packet["coverage_summary"]["graph_only_card_count"] == 12
    assert set(v9_packet["coverage_summary"]["missing_reviewed_model_ids"]) == (
        PR42_UPGRADED_MODEL_IDS
    )

    assert v10_packet["coverage_summary"]["reviewed_card_count"] == 12
    assert v10_packet["coverage_summary"]["graph_only_card_count"] == 0
    assert v10_packet["coverage_summary"]["conflicting_or_weak_support_count"] == 0
    assert v10_packet["coverage_summary"]["missing_reviewed_model_ids"] == []


def test_pr43_v10_fixture_preserves_risk_depth_and_absence_signals() -> None:
    cards = _cards_by_model(_load_json(V10_FIXTURE_PATH))

    for model_id in PR42_UPGRADED_MODEL_IDS:
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
        for absence in cards["risk-vs-uncertainty"]["absence_records"]
    } >= {"uncertainty-as-execution-avoidance"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["redundancy"]["absence_records"]
    } >= {"duplication-as-free-insurance"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["cybersecurity-thinking-models"]["absence_records"]
    } >= {"control-enumeration-as-security"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["switching-costs"]["absence_records"]
    } >= {"license-price-as-switching-cost"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["prospect-theory"]["absence_records"]
    } >= {"manipulative-loss-framing"}


def test_pr43_review_renders_match_deterministic_renderer() -> None:
    v9_packet = _load_json(V9_FIXTURE_PATH)
    v10_packet = _load_json(V10_FIXTURE_PATH)

    assert V9_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v9_packet)
    )
    assert V10_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v10_packet)
    )
    assert COMPARISON_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_comparison_markdown(
            before_packet=v9_packet,
            after_packet=v10_packet,
        )
    )


def test_pr43_comparison_render_checks_handoff_delta_not_final_answer() -> None:
    markdown = COMPARISON_RENDER.read_text(encoding="utf-8")

    assert "| Candidate cards | 12 | 12 | 0 |" in markdown
    assert "| Reviewed cards | 0 | 12 | +12 |" in markdown
    assert "| Graph-only cards | 12 | 0 | -12 |" in markdown
    assert "| Missing reviewed records | 12 | 0 | -12 |" in markdown
    assert "`risk-vs-uncertainty`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`switching-costs`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`prospect-theory`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "Compare handoff usefulness only" in markdown
    assert "Do not answer the user case" in markdown
    assert "Do not choose user-visible output" in markdown
    assert "Pressure:" not in markdown
    assert "best pressure" not in markdown.lower()


def test_pr43_v10_fixture_contains_no_final_surface_or_live_runtime_import() -> None:
    packet = _load_json(V10_FIXTURE_PATH)
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
        "affordances_v10",
        "model_affordances_v10",
        "pr43_v10_risk_reversibility_packet_review",
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
            model_id="risk-vs-uncertainty",
            pulled_by=("lane1_tendency_route", "reviewer_note"),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The advice treats the regulated market entry as "
                        "measurable enough to fund, but the key drivers may "
                        "still be ambiguous or unstable."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "approve the market-entry budget",
                    "route_or_artifact_id": "synthetic-pr43-risk-classification",
                },
            ),
            lane_order=1,
            lane_score=0.93,
        ),
        CandidateNomination(
            model_id="switching-costs",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The vendor migration is described as reversible, but "
                        "the advice does not name dual-run drag, data history, "
                        "integration dependencies, or unwind governance."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "start vendor migration",
                    "route_or_artifact_id": "synthetic-pr43-reversibility-decay",
                },
            ),
            lane_order=2,
            lane_score=0.9,
        ),
        CandidateNomination(
            model_id="redundancy",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The plan says to add backups, but does not test "
                        "whether the backup is independent, owned, usable, "
                        "and worth the added cost."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "adding backups",
                    "route_or_artifact_id": "synthetic-pr43-fallback-independence",
                },
            ),
            lane_order=3,
            lane_score=0.86,
        ),
        CandidateNomination(
            model_id="regulatory-horizon-scanning",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The advice says to monitor regulatory news but does "
                        "not specify weak-signal thresholds, owners, response "
                        "triggers, or present-day options."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "monitoring regulatory news",
                    "route_or_artifact_id": "synthetic-pr43-regulatory-trigger",
                },
            ),
            lane_order=4,
            lane_score=0.82,
        ),
        CandidateNomination(
            model_id="cybersecurity-thinking-models",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The migration and launch plan mentions security, but "
                        "does not map adversarial incentives, control owners, "
                        "or cross-layer failure chains."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "improving security",
                    "route_or_artifact_id": "synthetic-pr43-adversarial-chain",
                },
            ),
            lane_order=5,
            lane_score=0.78,
        ),
        CandidateNomination(
            model_id="non-linear-dynamics",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "A local launch acceleration could amplify downstream "
                        "support load, regulatory exposure, or adoption loops "
                        "instead of producing a linear gain."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr43-feedback-threshold",
                },
            ),
            lane_order=6,
            lane_score=0.74,
        ),
        CandidateNomination(
            model_id="tipping-points",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "Early customer interest is being treated as a "
                        "possible breakthrough without naming the controlling "
                        "threshold or prerequisite buildup."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "early customer interest",
                    "route_or_artifact_id": "synthetic-pr43-threshold-evidence",
                },
            ),
            lane_order=7,
            lane_score=0.7,
        ),
        CandidateNomination(
            model_id="butterfly-effect",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The advice could understate how one small migration "
                        "or compliance choice propagates through dependencies "
                        "unless a plausible cascade path is named."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr43-cascade-path",
                },
            ),
            lane_order=8,
            lane_score=0.66,
        ),
        CandidateNomination(
            model_id="chaos-theory",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The environment may be too unstable for exact "
                        "six-week forecasts, so the packet should favor "
                        "robustness, monitoring, slack, and reversibility."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "within six weeks",
                    "route_or_artifact_id": "synthetic-pr43-resilience-over-precision",
                },
            ),
            lane_order=9,
            lane_score=0.62,
        ),
        CandidateNomination(
            model_id="combinatorial-effects",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "Regulation, vendor migration, security exposure, and "
                        "early demand may interact non-additively, so the "
                        "packet should find make-or-break combinations."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr43-interaction-map",
                },
            ),
            lane_order=10,
            lane_score=0.58,
        ),
        CandidateNomination(
            model_id="critical-mass",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "Early adoption may not become self-sustaining unless "
                        "the minimum density of customers, workflow, trust, or "
                        "support exists."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "early customer interest",
                    "route_or_artifact_id": "synthetic-pr43-critical-density",
                },
            ),
            lane_order=11,
            lane_score=0.54,
        ),
        CandidateNomination(
            model_id="prospect-theory",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The team may double down or unwind under loss-frame "
                        "pressure, so the packet should distinguish decision "
                        "quality from reference-point distortion."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "double down or unwind",
                    "route_or_artifact_id": "synthetic-pr43-loss-frame-check",
                },
            ),
            lane_order=12,
            lane_score=0.5,
        ),
        CandidateNomination(
            model_id="switching-costs",
            pulled_by=("reviewer_note",),
            why_pulled=(
                {
                    "source": "reviewer_note",
                    "reason": (
                        "Duplicate nomination included to prove suppression "
                        "is visible instead of silently erased."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr43-duplicate-check",
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
