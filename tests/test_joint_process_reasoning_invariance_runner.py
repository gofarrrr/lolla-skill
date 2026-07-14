from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.joint_process_reasoning_shadow import (
    route_joint_projection,
    seal_joint_process_response,
)
from engine.system_b.reasoning_pattern_shadow import (
    CONTROLLED_MECHANISMS,
    conversation_turn_numbers,
)
from scripts.evals.run_joint_process_reasoning_invariance import (
    _build_prompts,
    evaluate_comparisons,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/joint_process_reasoning_invariance"


def _response(statuses: dict[str, str]) -> dict:
    rows = []
    for mechanism in sorted(CONTROLLED_MECHANISMS):
        status = statuses.get(mechanism, "not_observed")
        source_turns = [] if status == "not_observed" else [1]
        resolution_turns = [2] if status == "resolved_in_conversation" else []
        rows.append(
            {
                "mechanism_id": mechanism,
                "joint_status": status,
                "source_turns": source_turns,
                "resolution_turns": resolution_turns,
            }
        )
    return {"mechanisms": rows}


def _result(statuses: dict[str, str], fixture_id: str) -> dict:
    packet = seal_joint_process_response(
        _response(statuses),
        packet_id=fixture_id,
        source_ref=f"fixture:{fixture_id}",
        source_sha256="a" * 64,
        valid_turn_numbers={1, 2, 3},
    )
    routing_contract = json.loads(
        (
            ROOT
            / "docs/conversation-understanding/reasoning-pattern-shadow-routing-v0.json"
        ).read_text()
    )
    known = {
        item["model_id"]
        for item in json.loads(
            (ROOT / "data/compiled/model_affordances/affordances_v60.json").read_text()
        )["model_records"]
    }
    return {
        "status": "ok",
        "packet": packet,
        "routing": route_joint_projection(
            packet,
            routing_contract=routing_contract,
            known_model_ids=known,
        ),
    }


def test_runner_prompt_targets_complete_joint_trajectory_and_full_vocabulary() -> None:
    conversation = (FIXTURES / "facts_c.txt").read_text()
    system_prompt, user_prompt = _build_prompts(conversation)
    assert "complete joint reasoning trajectory" in system_prompt
    assert "Do not diagnose an isolated user or assistant turn" in system_prompt
    assert "every controlled mechanism exactly once" in user_prompt
    assert "resolved_in_conversation" in user_prompt
    for mechanism in CONTROLLED_MECHANISMS:
        assert f"- {mechanism}" in user_prompt


def test_new_fixtures_all_have_three_addressable_turns() -> None:
    for name in ("facts_c.txt", "facts_d.txt", "reasoning_repaired.txt"):
        assert conversation_turn_numbers((FIXTURES / name).read_text()) == {1, 2, 3}


def test_comparison_scorer_requires_fact_invariance_and_resolved_repair() -> None:
    base_statuses = {
        "ambiguous_signal_treated_as_commitment": "unresolved",
        "acknowledged_constraint_not_gated": "unresolved",
        "missing_reversal_condition": "unresolved",
        "reversible_path_not_considered": "unresolved",
    }
    repaired_statuses = {
        mechanism: "resolved_in_conversation" for mechanism in base_statuses
    }
    results = {
        "facts_c": _result(base_statuses, "facts_c"),
        "facts_d": _result(base_statuses, "facts_d"),
        "reasoning_repaired": _result(repaired_statuses, "reasoning_repaired"),
    }
    contract = {
        "comparisons": [
            {
                "comparison_id": "fact_invariance",
                "comparison_type": "same_unresolved_reasoning_different_facts",
                "fixture_ids": ["facts_c", "facts_d"],
                "expect_projection_equal": True,
                "expect_active_candidates_equal": True,
                "expect_edge_candidates_equal": True,
                "required_left_statuses": base_statuses,
                "required_right_statuses": base_statuses,
            },
            {
                "comparison_id": "joint_repair_sensitivity",
                "comparison_type": "same_facts_reasoning_repaired",
                "fixture_ids": ["facts_c", "reasoning_repaired"],
                "expect_projection_equal": False,
                "expect_active_candidates_equal": False,
                "expect_edge_candidates_equal": True,
                "required_left_statuses": base_statuses,
                "required_right_statuses": repaired_statuses,
            },
        ]
    }
    reviews = evaluate_comparisons(results, contract)
    assert [review["status"] for review in reviews] == ["passed", "passed"]
