from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_ROOT = ROOT / "research/reasoning-process-phase3-development-2026-07-11"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_phase3_terminal_decision_preserves_failed_gate() -> None:
    decision = _load(RESULT_ROOT / "decision.json")
    assert decision["status"] == "complete_material_redesign_required"
    assert decision["model_route"] == "google/gemini-3.1-flash-lite via OpenRouter"
    assert decision["decision"]["phase3_gate_passed"] is False
    assert decision["decision"]["phase4_transfer_authorized"] is False
    assert decision["decision"]["second_generic_repair_authorized"] is False
    assert decision["decision"]["next_work_class"] == (
        "provider_free_view_specific_contract_redesign"
    )


def test_phase3_call_and_cost_custody_is_complete() -> None:
    decision = _load(RESULT_ROOT / "decision.json")
    assert decision["baseline"]["provider_calls"] == 3
    assert decision["generic_repair"]["provider_calls"] == 5
    assert decision["total_custody"]["provider_calls"] == 8
    assert decision["total_custody"]["estimated_cost_usd"] == 0.018682
    for field in (
        "automatic_retries",
        "fallback_models",
        "evaluator_calls",
        "embedding_calls",
        "graph_calls",
        "pipeline_calls",
        "runtime_calls",
    ):
        assert decision["total_custody"][field] == 0
    assert decision["total_custody"]["protected_targets_seen_by_model"] is False
    assert decision["total_custody"]["source_review_addenda_seen_by_model"] is False


def test_phase3_repair_evidence_vector_does_not_hide_partial_failure() -> None:
    review = _load(RESULT_ROOT / "repair/source-review.json")
    aggregate = review["aggregate"]
    assert aggregate["operational_success_count"] == 5
    assert aggregate["typed_admission_count"] == 4
    assert aggregate["protected_target_visible_count"] == 4
    assert aggregate["protected_target_visibility_rate"] == 0.8
    assert aggregate["exact_source_reference_validity_rate"] == 0.9655
    assert aggregate["invalid_admitted_item_count"] == 1
    assert aggregate["source_strength_inflation_count"] == 1
    assert aggregate["context_invisible_label_count"] == 1
    assert aggregate["critical_dimension_zero_count"] == 1
    assert aggregate["repair_gate_passed"] is False


def test_phase3_all_artifact_references_match_bytes() -> None:
    decision = _load(RESULT_ROOT / "decision.json")
    references = [
        decision["baseline"]["result"],
        decision["baseline"]["source_review"],
        decision["generic_repair"]["result"],
        decision["generic_repair"]["source_review"],
        *decision["frozen_inputs"],
    ]
    for reference in references:
        assert _sha(ROOT / reference["path"]) == reference["sha256"]


def test_phase3_repair_calls_use_gemini_and_attempt_unique_observation_ids() -> None:
    admitted_ids: set[str] = set()
    calls = sorted((RESULT_ROOT / "repair/calls").glob("*.json"))
    assert len(calls) == 5
    for path in calls:
        call = _load(path)
        assert call["requested_model"] == "google/gemini-3.1-flash-lite"
        assert call["served_model"] == "google/gemini-3.1-flash-lite-20260507"
        assert call["provider_calls"] == 1
        assert call["automatic_retries"] == 0
        assert call["fallback_models"] == 0
        if call["typed_status"] == "admitted":
            for observation in call["compiled"]["model_addendum"]["observations"]:
                observation_id = observation["observation_id"]
                assert observation_id.startswith("phase3-repair-")
                assert observation_id not in admitted_ids
                admitted_ids.add(observation_id)
                assert observation["graph_routing_eligible"] is False
    assert len(admitted_ids) == 14


def test_phase3_exploration_failure_is_quarantined_not_healed() -> None:
    call = _load(RESULT_ROOT / "repair/calls/exploration_and_alternatives.json")
    assert call["operational_status"] == "ok"
    assert call["typed_status"] == "quarantined"
    assert "not exact source evidence" in call["validation_error"]
    assert "..." in call["candidate_payload"]["evidence"][4]["quote"]
    assert call["compiled"] is None


def test_phase1_ledger_remained_immutable_through_phase3() -> None:
    path = (
        ROOT
        / "research/reasoning-process-phase1-ledger-2026-07-11/cases"
        / "amb1-case02-nonprofit-scale/ledger.json"
    )
    assert _sha(path) == "8c4b9a419d781d76d493eb859a02a6510735a74ae3606872f5af58aff653ca23"
