from __future__ import annotations

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "research"))

from pre_step6_context_composition_gate import (  # noqa: E402
    build_composition_packet,
    validate_composition_gate_judgment_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_composition_packet_compares_private_context_not_public_answer_cores() -> None:
    packet = build_composition_packet(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
        seed=2026052002,
    )

    assert packet["case_id"] == "founder-grant-marcus-equity.high-clutter"
    assert set(packet["candidates_by_label"]) == {"A", "B", "C", "D"}
    assert "bevelin" not in json.dumps(packet["candidates_by_label"]).lower()
    assert "polya" not in json.dumps(packet["candidates_by_label"]).lower()
    assert "do not judge which candidate is the best final answer" in json.dumps(
        packet
    ).lower()
    assert "smallest sufficient packet" in json.dumps(packet).lower()
    assert "extra receipt carries a complexity tax" in json.dumps(packet).lower()

    rendered_label = next(
        label
        for label, arm in packet["blind_map"].items()
        if arm == "rendered_only"
    )
    dual_label = next(
        label
        for label, arm in packet["blind_map"].items()
        if arm == "rendered_plus_dual_receipts"
    )
    rendered_chars = packet["candidates_by_label"][rendered_label]["char_count"]
    dual_chars = packet["candidates_by_label"][dual_label]["char_count"]
    assert dual_chars > rendered_chars


def test_composition_gate_judgment_payload_validates_static_agreement() -> None:
    packet = build_composition_packet(
        case_id="founder-grant-marcus-equity.high-clutter",
        repo_root=REPO_ROOT,
        seed=2026052002,
    )
    dual_label = next(
        label
        for label, arm in packet["blind_map"].items()
        if arm == "rendered_plus_dual_receipts"
    )
    payload = {
        "schema_version": "pre_step6_context_composition_gate_judgment.v1",
        "status": "research_only",
        "runtime_policy": "runtime_dormant",
        "case_id": "founder-grant-marcus-equity.high-clutter",
        "gate_kind": "live_context_composition_comparison",
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": {
            "provider": "test",
            "model": "fixture",
            "status": "ok",
            "prompt_tokens": 1,
            "completion_tokens": 1,
            "total_tokens": 2,
        },
        "candidate_refs": packet["candidate_refs"],
        "blind_map": packet["blind_map"],
        "reviewer_output": {
            "winner_label": dual_label,
            "research_action": "expand_replay",
            "confidence": "medium",
            "rationale": "The composed packet keeps the concrete anchor and adds protected receipts without replacing Step 6.",
            "protected_value": [
                "Preserves concrete team-risk pressure.",
                "Keeps false-precision caution visible.",
            ],
            "bloat_or_pruning_risk": [
                "Needs Step 6 to ignore receipts that do not help."
            ],
            "composition_note": "Pass as private enrichment, not as a final answer template.",
        },
        "static_expectation": {
            "allowed_winner_arms": [
                "rendered_plus_bevelin_receipts",
                "rendered_plus_dual_receipts",
            ],
            "allowed_research_actions": ["expand_replay"],
        },
        "agreement": {
            "winner_matches_static": True,
            "action_matches_static": True,
            "overall_match": True,
        },
        "gates": {
            "runtime_wiring_allowed": False,
            "skill_update_allowed": False,
        },
        "notes": "Fixture payload.",
    }

    validate_composition_gate_judgment_payload(payload)
