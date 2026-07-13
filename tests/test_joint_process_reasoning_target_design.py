from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.reasoning_pattern_shadow import CONTROLLED_MECHANISMS


ROOT = Path(__file__).resolve().parents[1]
TARGET = (
    ROOT
    / "docs/conversation-understanding/joint-process-reasoning-target-v0.json"
)
DOC = ROOT / "docs/conversation-understanding/joint-process-reasoning-target-v0.md"


def test_joint_target_routes_only_unresolved_and_preserves_ambiguity() -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    assert target["audited_object"] == "complete_joint_conversation_trajectory"
    assert target["routing_target"] == (
        "reasoning_weakness_unresolved_after_complete_conversation"
    )
    assert target["controlled_mechanism_coverage"] == "exactly_once_each"
    assert target["status_effects"] == {
        "unresolved": "active_seed_routing",
        "ambiguous": "edge_reserve_no_active_seed",
        "resolved_in_conversation": "audit_only_no_seed",
        "not_observed": "audit_only_no_seed",
    }
    assert target["actor_observation_policy"][
        "actor_specific_presence_automatically_routes"
    ] is False
    assert target["actor_observation_policy"][
        "unresolved_joint_trajectory_judgment_is_probabilistic"
    ] is True


def test_joint_target_forbids_deterministic_resolution_semantics() -> None:
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    forbidden = set(target["deterministic_forbidden"])
    assert {
        "infer_resolution_from_keywords",
        "prefer_assistant_or_user_by_rule",
        "route_actor_local_presence_without_joint_status",
        "rewrite_semantic_status_for_stability",
    } <= forbidden
    text = DOC.read_text(encoding="utf-8").lower()
    assert "which abstract reasoning weakness" in text
    assert "remains unresolved" in text
    assert "the batch 3 result remains frozen" in text


def test_controlled_vocabulary_remains_small_and_declared() -> None:
    assert len(CONTROLLED_MECHANISMS) == 10
    assert "other_review_required" in CONTROLLED_MECHANISMS
