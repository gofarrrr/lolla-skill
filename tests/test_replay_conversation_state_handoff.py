from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.evals.replay_conversation_state_handoff import (
    ConversationStateReplayError,
    run_replay,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "research/conversation-state-handoff-v1-2026-07-10/contract.json"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_checked_in_five_case_replay_passes_without_graph_seeds() -> None:
    result = run_replay(_contract(), repo_root=ROOT)
    assert result["status"] == "passed"
    assert result["observed"]["case_count"] == 5
    assert result["observed"]["joint_position_count"] == 5
    assert result["observed"]["constraint_count"] == 43
    assert result["observed"]["direct_graph_seed_count"] == 0
    assert result["observed"]["thread_disposition_counts"] == {
        "addressed_unresolved": 4,
        "resolved": 1,
    }
    assert result["provider_calls"] == 0
    assert result["runtime_modified"] is False


def test_replay_preserves_baseline_as_comparison_not_false_improvement() -> None:
    result = run_replay(_contract(), repo_root=ROOT)
    assert result["comparison_kind"] == (
        "representation_capacity_against_reviewed_failures_not_new_extractor_output"
    )
    assert result["baseline"]["proposal_provenance_case_precision"] == 0.0
    assert result["baseline"]["thread_status_precision"] == 0.0
    assert result["interpretation"]["production_extractor_can_populate_state"] == "not_tested"


def test_replay_rejects_mutated_case_hash_before_semantic_use() -> None:
    contract = copy.deepcopy(_contract())
    contract["cases"][0]["sha256"] = "0" * 64
    with pytest.raises(ConversationStateReplayError, match="case hash mismatch"):
        run_replay(contract, repo_root=ROOT)
