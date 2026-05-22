from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_cognitive_gate_live import (  # noqa: E402
    build_gate_packet,
    build_reviewer_packet,
    validate_gate_judgment_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_cognitive_gate_packet_blinds_candidates_and_omits_static_expectation() -> None:
    packet = build_gate_packet(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
        seed=2026052001,
    )

    assert packet["case_id"] == "founder-grant-marcus-equity.high-clutter"
    assert set(packet["candidates_by_label"]) == {"A", "B", "C", "D"}
    assert "static_expectation" not in json.dumps(packet)
    assert "bevelin_lens" not in json.dumps(packet["candidates_by_label"])
    assert "polya_lens" not in json.dumps(packet["candidates_by_label"])

    reviewer_packet = build_reviewer_packet(packet)
    reviewer_blob = json.dumps(reviewer_packet).lower()
    assert "blind_map" not in reviewer_packet
    assert "candidate_refs" not in reviewer_packet
    assert "do not judge which candidate is the best final answer" in reviewer_blob
    assert "promotion_read applies to the research layer" in reviewer_blob


def test_cognitive_gate_judgment_payload_validates_and_scores_static_agreement() -> None:
    packet = build_gate_packet(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
        seed=2026052001,
    )
    label_for_bevelin = next(
        label
        for label, arm in packet["blind_map"].items()
        if arm == "bevelin_lens"
    )
    payload = {
        "schema_version": "pre_step6_cognitive_gate_judgment.v1",
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": "founder-grant-marcus-equity.high-clutter",
        "gate_kind": "live_small_cognitive_comparison",
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": {
            "provider": "test",
            "model": "fixture",
            "status": "ok",
            "prompt_tokens": 1,
            "completion_tokens": 1,
            "total_tokens": 2
        },
        "candidate_refs": packet["candidate_refs"],
        "blind_map": packet["blind_map"],
        "reviewer_output": {
            "winner_label": label_for_bevelin,
            "promotion_read": "expand_replay",
            "confidence": "medium",
            "rationale": "The winning answer preserves the strongest incentive and dependency pressure without adding bloat.",
            "improvements": [
                "Names the decision-relevant edge pressure."
            ],
            "regressions_or_watch_items": [
                "Still a small fixture judgment."
            ],
            "stand_down_reason": "No stand-down because the lens materially improves the answer.",
            "composition_note": "Use this lens over the problem-shape lens for this case."
        },
        "static_expectation": {
            "allowed_winner_arms": ["bevelin_lens"],
            "allowed_promotion_reads": ["expand_replay"]
        },
        "agreement": {
            "winner_matches_static": True,
            "promotion_matches_static": True,
            "overall_match": True
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False
        },
        "notes": "Fixture payload."
    }

    validate_gate_judgment_payload(payload)
