from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.evals.replay_conversation_state_candidate_recovery import (
    CandidateRecoveryReplayError,
    run_replay,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/conversation-state-recovery-v1-2026-07-11"
CONTRACT_PATH = PACKAGE / "contract.json"
RESULT_PATH = PACKAGE / "replay-result.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_frozen_candidate_recovery_replay_passes_all_gates_provider_free() -> None:
    result = run_replay(_load(CONTRACT_PATH), repo_root=ROOT)
    assert result["status"] == "passed"
    assert result["failed_gates"] == []
    assert result["observed"]["case_count"] == 5
    assert result["observed"]["constraint_count"] == 45
    assert result["observed"]["candidate_count"] == 60
    assert result["observed"]["late_trajectory_case_count"] == 5
    assert result["observed"]["invalid_candidate_count"] == 0
    assert result["observed"]["direct_graph_seed_count"] == 0
    assert result["provider_calls"] == 0
    assert result["graph_calls"] == 0
    assert result["runtime_modified"] is False


def test_checked_in_replay_result_matches_frozen_contract() -> None:
    observed = run_replay(_load(CONTRACT_PATH), repo_root=ROOT)
    checked_in = _load(RESULT_PATH)
    assert checked_in == observed


def test_all_adversarial_fixtures_fail_closed_at_the_expected_boundary() -> None:
    result = run_replay(_load(CONTRACT_PATH), repo_root=ROOT)
    assert [row["terminal_outcome"] for row in result["adversarial_results"]] == [
        "ledger_quarantined",
        "parser_rejected",
        "ledger_quarantined",
        "absence_preserved",
    ]
    assert all(
        row["accepted_observed_path_allowed"] is False
        for row in result["adversarial_results"]
    )


def test_replay_rejects_mutated_artifact_before_semantic_use() -> None:
    contract = copy.deepcopy(_load(CONTRACT_PATH))
    contract["artifact_locks"][0]["sha256"] = "0" * 64
    with pytest.raises(CandidateRecoveryReplayError, match="hash mismatch"):
        run_replay(contract, repo_root=ROOT)


def test_provider_compatibility_is_recorded_as_non_semantic_evidence() -> None:
    result = run_replay(_load(CONTRACT_PATH), repo_root=ROOT)
    for provider in ("openai", "gemini"):
        report = result["provider_compatibility"][provider]
        assert report["all_compatible"] is True
        assert report["provider_calls"] == 0
        assert all(row["compatible"] for row in report["rows"])
    assert result["interpretation"]["provider_acceptance"] == "not_tested"
    assert result["interpretation"]["automatic_extraction_quality"] == "not_tested"
