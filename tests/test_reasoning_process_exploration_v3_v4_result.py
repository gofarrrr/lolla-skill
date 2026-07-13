from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.reasoning_process_exploration_v3 import response_schema_v3


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_v3_provider_schema_removes_model_authorship_of_mechanical_parking() -> None:
    schema = response_schema_v3()
    assert "park_unselected_auxiliary_observations" not in schema["properties"]
    assert "park_unselected_auxiliary_observations" not in schema["required"]
    assert schema["properties"]["records"]["maxItems"] == 4


def test_targeted_v3_recovers_alternative_but_not_attached_minority_limit() -> None:
    call = _load(
        ROOT / "research/reasoning-process-exploration-v3-probe-2026-07-11/call.json"
    )
    assert call["operational_status"] == "ok"
    assert call["typed_status"] == "admitted"
    assert call["provider_calls"] == 1
    records = call["candidate_payload"]["records"]
    named_role = next(record for record in records if "e026" in record["alternative_evidence_ids"])
    assert "e027" not in named_role["attached_condition_or_limit_evidence_ids"]
    review = _load(
        ROOT
        / "research/reasoning-process-exploration-v3-probe-2026-07-11/source-review.json"
    )
    assert review["status"] == "source_review_complete_gate_failed"
    assert review["protected_target"]["alternative_visible"] is True
    assert review["protected_target"]["attached_not_all_ownership_limit_visible"] is False


def test_conversation_only_ablation_does_not_support_ledger_anchoring_hypothesis() -> None:
    packet = _load(
        ROOT
        / "research/reasoning-process-exploration-v4-conversation-only-2026-07-11/reader-packet.json"
    )
    assert packet["reader_packet"]["auxiliary_phase1_ledger"]["included"] is False
    assert packet["reader_packet"]["auxiliary_phase1_ledger"]["observations"] == []
    assert packet["metrics"]["source_content_complete"] is True
    call = _load(
        ROOT / "research/reasoning-process-exploration-v4-ablation-2026-07-11/call.json"
    )
    assert call["operational_status"] == "ok"
    assert call["typed_status"] == "quarantined"
    assert "unknown IDs" in call["validation_error"]
    records = call["candidate_payload"]["records"]
    assert all("e026" not in record["alternative_evidence_ids"] for record in records)
    review = _load(
        ROOT
        / "research/reasoning-process-exploration-v4-ablation-2026-07-11/source-review.json"
    )
    assert review["decision"]["auxiliary_ledger_is_root_cause"] is False
    assert review["decision"]["additional_provider_call_authorized"] is False
    assert review["decision"]["phase4_transfer_authorized"] is False


def test_v2_result_keeps_four_semantic_passes_separate_from_full_gate() -> None:
    review = _load(
        ROOT
        / "research/reasoning-process-view-specific-v2-probe-2026-07-11/source-review.json"
    )
    assert review["evidence_vector"]["semantic_relationship_view_pass"] == "4/5"
    assert review["evidence_vector"]["protected_target_visibility"] == "4/5"
    assert review["decision"]["v2_development_gate_passed"] is False
    assert review["decision"]["five-view_rerun_authorized"] is False


def test_terminal_decision_freezes_narrow_next_work_and_complete_accounting() -> None:
    decision = _load(
        ROOT
        / "research/reasoning-process-view-specific-development-2026-07-11/decision.json"
    )
    assert decision["status"] == (
        "development_sequence_complete_exploration_only_redesign_required"
    )
    assert decision["outcome"]["exploration_and_alternatives"] == (
        "material_local_path_redesign_required"
    )
    assert decision["outcome"]["phase4_transfer_authorized"] is False
    assert decision["provider_sequence"]["total_requests"] == 12
    assert decision["provider_sequence"]["estimated_cost_usd"] == 0.0280115
    assert decision["provider_free_evidence"]["focused_test_pass"] == "94/94"
    assert decision["next_authorized_work"]["kind"] == (
        "provider_free_exploration_only_local_chronological_pair_harvester_design"
    )
