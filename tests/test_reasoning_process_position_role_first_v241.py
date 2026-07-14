from __future__ import annotations

import copy
import json
from pathlib import Path

from engine.system_b.reasoning_process_position_role_first_v241 import (
    build_position_current_qualification_packet_v241,
    compile_position_current_qualification_response_v241,
    position_current_qualification_response_schema_v241,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reasoning-process-position-role-first-v241-2026-07-12/report.json"
REGISTRY = ROOT / "research/reasoning-process-position-role-first-v24-new-case-2026-07-12"
V24_PROBE = ROOT / "research/reasoning-process-position-role-first-v24-probe-2026-07-12"
HOUSING = ROOT / "research/reasoning-process-position-role-first-v241-new-case-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_v241_provider_free_gate_passes_without_calls() -> None:
    report = _load(REPORT)
    assert report["status"] == "provider_free_position_role_first_v241_pass"
    assert report["summary"]["reviewed_case_count"] == 12
    assert report["summary"]["complete_join_count"] == 12
    assert report["summary"]["maximum_provider_calls_per_case"] == 3
    assert report["summary"]["maximum_user_prompt_utf8_bytes"] == 7497
    assert report["summary"]["provider_calls"] == 0
    assert report["claims"]["v24_status_contradiction_removed_by_construction"] is True
    assert report["claims"]["automatic_semantic_allocation_improved"] is False


def test_v241_schema_removes_only_redundant_envelope_statuses() -> None:
    schema = position_current_qualification_response_schema_v241()
    assert set(schema["properties"]) == {"records", "allocation_note", "global_limitations"}
    assert "current_status" not in schema["required"]
    assert "qualification_status" not in schema["required"]
    assert schema["properties"]["records"]["maxItems"] == 4


def test_exact_v24_semantic_candidate_compiles_after_status_fields_are_absent() -> None:
    wrapper = _load(REGISTRY / "position-endpoint.json")
    candidate = copy.deepcopy(_load(V24_PROBE / "call-02-result.json")["candidate_payload"])
    assert candidate.pop("current_status") == "not_found"
    assert candidate.pop("qualification_status") == "not_found"
    compiled = compile_position_current_qualification_response_v241(response=candidate, wrapper=wrapper, producer_kind="preserved_provider_replay", producer_id="v24-candidate-no-repair")
    assert len(compiled["role_compiled"]["current"]["observations"]) == 1
    assert len(compiled["role_compiled"]["qualification"]["observations"]) == 1
    assert compiled["derived_envelope_status"] == {"current": "supported", "qualification": "supported"}
    assert compiled["boundary"]["semantic_repair_performed"] is False
    current = compiled["role_compiled"]["current"]["observations"][0]
    qualification = compiled["role_compiled"]["qualification"]["observations"][0]
    assert "e036" in current["source_evidence_ids"]
    assert "e036" in qualification["source_evidence_ids"]


def test_empty_role_status_is_derived_from_absent_role_records() -> None:
    wrapper = _load(REGISTRY / "position-endpoint.json")
    target = _load(REGISTRY / "source-review-target.json")["paired_response"]
    response = {"records": [target["records"][0]], "allocation_note": "No supported qualification record.", "global_limitations": "Reviewed both roles."}
    compiled = compile_position_current_qualification_response_v241(response=response, wrapper=wrapper, producer_kind="fixture", producer_id="v241-empty")
    assert compiled["derived_envelope_status"] == {"current": "supported", "qualification": "not_found"}
    assert compiled["role_compiled"]["qualification"]["role_terminal_disposition"] == "reviewed_empty"


def test_packet_declares_mechanical_status_derivation_without_semantic_repair() -> None:
    wrapper = _load(REGISTRY / "position-endpoint.json")
    packet = build_position_current_qualification_packet_v241(wrapper=wrapper)
    assert packet["response_contract"]["per_role_envelope_status_requested"] is False
    assert packet["boundary"]["envelope_status_derived_mechanically"] is True
    assert packet["boundary"]["semantic_repair_performed"] is False
    assert packet["boundary"]["deterministic_alias_subtraction_added"] is False


def test_fresh_housing_target_is_source_first_status_free_and_shared_meaning() -> None:
    case_report, target_report = _load(HOUSING / "case-report.json"), _load(HOUSING / "target-report.json")
    target, compiled = _load(HOUSING / "source-review-target.json"), _load(HOUSING / "compiled-source-review-target.json")
    assert case_report["provider_calls"] == 0
    assert target_report["status"] == "pre_execution_target_gate_pass"
    assert target["boundary"]["written_before_provider_execution"] is True
    assert set(target["paired_response"]) == {"records", "allocation_note", "global_limitations"}
    current, qualification = target["paired_response"]["records"]
    assert "e034" in current["evidence_ids"]
    assert "e034" in qualification["evidence_ids"]
    assert current["stance_components"][-1]["expression_kind"] == "conditional_willingness"
    assert qualification["stance_components"][0]["expression_kind"] == "uncertain_or_undecided"
    assert compiled["paired_compiled"]["derived_envelope_status"] == {"current": "supported", "qualification": "supported"}


def test_v241_probe_is_preserved_as_architecture_pass_not_production_proof() -> None:
    probe = ROOT / "research/reasoning-process-position-role-first-v241-probe-2026-07-12"
    result, review = _load(probe / "result.json"), _load(probe / "source-review.json")
    assert result["provider_request_count"] == 3
    assert result["joined"]["status"] == "position_role_first_join_complete"
    assert review["status"] == "paired_architecture_development_pass_with_residual_fidelity_defects"
    assert review["paired_allocation_review"]["central_hypothesis"] == "pass"
    assert review["paired_allocation_review"]["shared_e034_meanings_are_distinct"] is True
    assert review["role_review"]["qualification"]["protected_target_survived"] is True
    assert review["success_requirement_disposition"]["complete_component_force_and_category_fidelity"] is False
    assert review["decision"]["graph_or_runtime_integration_authorized"] is False
