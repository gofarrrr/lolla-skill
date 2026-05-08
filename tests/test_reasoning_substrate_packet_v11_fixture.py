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
V10_FIXTURE_PATH = FIXTURE_DIR / "pr46_v10_frame_correction_packet_review.json"
V11_FIXTURE_PATH = FIXTURE_DIR / "pr46_v11_frame_correction_packet_review.json"
V10_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v10.json"
)
V11_AFFORDANCES_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v11.json"
)
V10_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr46-v10-review-render-2026-05-07.md"
)
V11_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr46-v11-review-render-2026-05-07.md"
)
COMPARISON_RENDER = (
    REPO_ROOT
    / "research"
    / "reasoning-substrate-packet-pr46-v10-v11-comparison-render-2026-05-07.md"
)
LIVE_RUNTIME_PATHS = (
    REPO_ROOT / "engine" / "system_b" / "__init__.py",
    REPO_ROOT / "engine" / "system_b" / "pipeline.py",
    REPO_ROOT / "scripts" / "run_pipeline.py",
)

PR45_UPGRADED_MODEL_IDS = {
    "bias-blind-spot",
    "cognitive-gaps-assessment",
    "counterfactual-reasoning",
    "critical-thinking",
    "dialectical-reasoning",
    "einstellung-effect",
    "false-precision-avoidance",
    "metacognitive-questioning",
    "reasoning-mode-router",
    "reframing-perspective",
    "theory-induced-blindness",
    "wysiati",
}

TRANSACTION_CONTEXT = {
    "case_id": "pr46-frame-correction-review",
    "user_situation_summary": (
        "A leadership team is ready to act on a plausible AI-generated rescue "
        "memo for a stalled partnership, but the diagnosis may be overfit to "
        "visible evidence, familiar playbooks, precise dates, and one favored "
        "frame."
    ),
    "assistant_advice_summary": (
        "The assistant recommends a focused execution plan with crisp dates, "
        "a chosen root cause, a communication reset, and risk checks, but it "
        "does not test missing evidence, alternative frames, counterfactual "
        "paths, self-bias, false precision, or whether the current reasoning "
        "mode fits the case."
    ),
    "known_action_or_commitment": (
        "Use the memo to reset the partner plan, assign owners, and decide "
        "within thirty days whether to double down, reframe, or unwind."
    ),
    "capture_health": "synthetic_review",
    "transaction_sources": ["user_turn", "assistant_turn", "reviewer_note"],
}


def test_pr46_v10_and_v11_fixtures_match_dormant_packet_producer_output() -> None:
    assert _load_json(V10_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr46-v10-frame-correction-packet-review",
        affordances_path=V10_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v10.json",
    )
    assert _load_json(V11_FIXTURE_PATH) == _build_expected_packet(
        packet_id="pr46-v11-frame-correction-packet-review",
        affordances_path=V11_AFFORDANCES_PATH,
        affordances_artifact="data/compiled/model_affordances/affordances_v11.json",
    )


def test_pr46_v11_fixture_upgrades_same_nominations_without_changing_count() -> None:
    v10_packet = _load_json(V10_FIXTURE_PATH)
    v11_packet = _load_json(V11_FIXTURE_PATH)

    assert len(v10_packet["candidate_cards"]) == 12
    assert len(v11_packet["candidate_cards"]) == 12
    assert len(v10_packet["suppressed_candidates"]) == 1
    assert len(v11_packet["suppressed_candidates"]) == 1

    assert v10_packet["coverage_summary"]["reviewed_card_count"] == 0
    assert v10_packet["coverage_summary"]["graph_only_card_count"] == 12
    assert set(v10_packet["coverage_summary"]["missing_reviewed_model_ids"]) == (
        PR45_UPGRADED_MODEL_IDS
    )

    assert v11_packet["coverage_summary"]["reviewed_card_count"] == 12
    assert v11_packet["coverage_summary"]["graph_only_card_count"] == 0
    assert v11_packet["coverage_summary"]["conflicting_or_weak_support_count"] == 0
    assert v11_packet["coverage_summary"]["missing_reviewed_model_ids"] == []


def test_pr46_v11_fixture_preserves_frame_depth_and_absence_signals() -> None:
    cards = _cards_by_model(_load_json(V11_FIXTURE_PATH))

    for model_id in PR45_UPGRADED_MODEL_IDS:
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
        for absence in cards["cognitive-gaps-assessment"]["absence_records"]
    } >= {"gap-mapping-without-plan-change"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["counterfactual-reasoning"]["absence_records"]
    } >= {"counterfactual-fiction-as-discipline"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["reasoning-mode-router"]["absence_records"]
    } >= {"deterministic-case-type-mode-router"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["theory-induced-blindness"]["absence_records"]
    } >= {"endless-theory-shopping"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["false-precision-avoidance"]["absence_records"]
    } >= {"simplicity-that-hides-uncertainty"}
    assert {
        str(absence["attempted_field"])
        for absence in cards["wysiati"]["absence_records"]
    } >= {"coherent-story-as-proof"}


def test_pr46_review_renders_match_deterministic_renderer() -> None:
    v10_packet = _load_json(V10_FIXTURE_PATH)
    v11_packet = _load_json(V11_FIXTURE_PATH)

    assert V10_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v10_packet)
    )
    assert V11_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_review_markdown(v11_packet)
    )
    assert COMPARISON_RENDER.read_text(encoding="utf-8") == (
        render_reasoning_substrate_packet_comparison_markdown(
            before_packet=v10_packet,
            after_packet=v11_packet,
        )
    )


def test_pr46_comparison_render_checks_handoff_delta_not_final_answer() -> None:
    markdown = COMPARISON_RENDER.read_text(encoding="utf-8")

    assert "| Candidate cards | 12 | 12 | 0 |" in markdown
    assert "| Reviewed cards | 0 | 12 | +12 |" in markdown
    assert "| Graph-only cards | 12 | 0 | -12 |" in markdown
    assert "| Missing reviewed records | 12 | 0 | -12 |" in markdown
    assert "`cognitive-gaps-assessment`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`reasoning-mode-router`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`false-precision-avoidance`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "`wysiati`: `graph_only_runtime_card` -> `reviewed_affordance_available`" in markdown
    assert "Compare handoff usefulness only" in markdown
    assert "Do not answer the user case" in markdown
    assert "Do not choose user-visible output" in markdown
    assert "Pressure:" not in markdown
    assert "best pressure" not in markdown.lower()


def test_pr46_v11_fixture_contains_no_final_surface_or_live_runtime_import() -> None:
    packet = _load_json(V11_FIXTURE_PATH)
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
        "affordances_v11",
        "model_affordances_v11",
        "pr46_v11_frame_correction_packet_review",
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
            model_id="cognitive-gaps-assessment",
            pulled_by=("lane4_gap_route", "reviewer_note"),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The plan assumes the team has enough context to act, "
                        "but the missing evidence, capability, perspective, "
                        "or transfer gap may be the real blocker."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "we have enough context to move",
                    "route_or_artifact_id": "synthetic-pr46-reality-gap-audit",
                },
            ),
            lane_order=1,
            lane_score=0.94,
        ),
        CandidateNomination(
            model_id="critical-thinking",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The memo treats its explanation as clear, but claim, "
                        "evidence, assumption, authority, emotion, and story "
                        "may be doing different work."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "the right answer is clear",
                    "route_or_artifact_id": "synthetic-pr46-claim-evidence-check",
                },
            ),
            lane_order=2,
            lane_score=0.9,
        ),
        CandidateNomination(
            model_id="counterfactual-reasoning",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The advice narrows quickly to one path without "
                        "testing plausible alternatives, failure branches, or "
                        "paths not taken before commitment."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "option B is unlikely",
                    "route_or_artifact_id": "synthetic-pr46-counterfactual-branch",
                },
            ),
            lane_order=3,
            lane_score=0.86,
        ),
        CandidateNomination(
            model_id="metacognitive-questioning",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The team is ready to execute, but the next "
                        "discriminating question could still change the path "
                        "if it is bounded and action-linked."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "we should just execute",
                    "route_or_artifact_id": "synthetic-pr46-next-question-gate",
                },
            ),
            lane_order=4,
            lane_score=0.82,
        ),
        CandidateNomination(
            model_id="reasoning-mode-router",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The same response is trying to diagnose, design, "
                        "critique, and execute; the packet should check which "
                        "reasoning mode fits the current task stage."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "evidence_quote": "diagnose, design, and execute all in one pass",
                    "route_or_artifact_id": "synthetic-pr46-mode-fit-check",
                },
            ),
            lane_order=5,
            lane_score=0.78,
        ),
        CandidateNomination(
            model_id="reframing-perspective",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The case is framed as a pricing problem, but a "
                        "different decision variable could expose a better "
                        "action path."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "pricing problem",
                    "route_or_artifact_id": "synthetic-pr46-decision-variable-reframe",
                },
            ),
            lane_order=6,
            lane_score=0.74,
        ),
        CandidateNomination(
            model_id="theory-induced-blindness",
            pulled_by=("lane2_companion_chunk",),
            why_pulled=(
                {
                    "source": "lane2_companion_chunk",
                    "reason": (
                        "The favored framework may explain the visible facts "
                        "while filtering out disconfirming signals or a better "
                        "cut of the problem."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "the chosen framework explains it",
                    "route_or_artifact_id": "synthetic-pr46-framework-blindness",
                },
            ),
            lane_order=7,
            lane_score=0.7,
        ),
        CandidateNomination(
            model_id="einstellung-effect",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The team is reusing a familiar playbook, so the "
                        "packet should test whether fluency is being mistaken "
                        "for real fit."
                    ),
                    "evidence_source_type": "user_turn",
                    "evidence_quote": "reuse last quarter's playbook",
                    "route_or_artifact_id": "synthetic-pr46-familiar-template-lock-in",
                },
            ),
            lane_order=8,
            lane_score=0.66,
        ),
        CandidateNomination(
            model_id="dialectical-reasoning",
            pulled_by=("lane3_frame_route",),
            why_pulled=(
                {
                    "source": "lane3_frame_route",
                    "reason": (
                        "The advice collapses tension into one side winning, "
                        "but both positions may preserve partial truths that "
                        "should shape the next move."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "evidence_quote": "one side must be right",
                    "route_or_artifact_id": "synthetic-pr46-bounded-antithesis",
                },
            ),
            lane_order=9,
            lane_score=0.62,
        ),
        CandidateNomination(
            model_id="bias-blind-spot",
            pulled_by=("lane1_tendency_route",),
            why_pulled=(
                {
                    "source": "lane1_tendency_route",
                    "reason": (
                        "The memo diagnoses the partner as biased while not "
                        "testing the advising team's own incentives, status, "
                        "or self-protective interpretation."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "they are being irrational",
                    "route_or_artifact_id": "synthetic-pr46-self-bias-check",
                },
            ),
            lane_order=10,
            lane_score=0.58,
        ),
        CandidateNomination(
            model_id="false-precision-avoidance",
            pulled_by=("lane2_detected_model",),
            why_pulled=(
                {
                    "source": "lane2_detected_model",
                    "reason": (
                        "The recommendation uses crisp dates and uplift "
                        "claims, but the exactness may create confidence "
                        "without changing the decision."
                    ),
                    "evidence_source_type": "assistant_turn",
                    "evidence_quote": "ship by June 30 with 35% uplift",
                    "route_or_artifact_id": "synthetic-pr46-precision-boundary",
                },
            ),
            lane_order=11,
            lane_score=0.54,
        ),
        CandidateNomination(
            model_id="wysiati",
            pulled_by=("lane4_gap_route",),
            why_pulled=(
                {
                    "source": "lane4_gap_route",
                    "reason": (
                        "The visible story is coherent, but the packet should "
                        "force attention to missing evidence, denominators, "
                        "disconfirming cases, and absent briefing sides."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "evidence_quote": "we only have the visible wins",
                    "route_or_artifact_id": "synthetic-pr46-missing-denominator",
                },
            ),
            lane_order=12,
            lane_score=0.5,
        ),
        CandidateNomination(
            model_id="reasoning-mode-router",
            pulled_by=("reviewer_note",),
            why_pulled=(
                {
                    "source": "reviewer_note",
                    "reason": (
                        "Duplicate nomination included to prove suppression "
                        "is visible instead of silently erased."
                    ),
                    "evidence_source_type": "reviewer_note",
                    "route_or_artifact_id": "synthetic-pr46-duplicate-check",
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
