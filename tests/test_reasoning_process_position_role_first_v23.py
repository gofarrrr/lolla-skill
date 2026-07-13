from __future__ import annotations

import copy
import json
from pathlib import Path

from engine.system_b.reasoning_process_position_role_first_v2 import ROLE_ORDER
from engine.system_b.reasoning_process_position_role_first_v22 import position_role_response_schema_v22
from engine.system_b.reasoning_process_position_role_first_v23 import (
    EXPRESSION_INTERPRETATION_CONTRACT, ROLE_BOUNDARY_CONTRACTS,
    build_position_role_packet_v23, build_position_role_prompts_v23,
    compile_position_role_response_v23, position_role_response_schema_v23,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reasoning-process-position-role-first-v23-2026-07-12/report.json"
COOPERATIVE = ROOT / "research/reasoning-process-position-role-first-v22-new-case-2026-07-12"
V22_PROBE = ROOT / "research/reasoning-process-position-role-first-v22-probe-2026-07-12"
MUSEUM = ROOT / "research/reasoning-process-position-role-first-v23-new-case-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_v23_provider_free_replays_eleven_cases_without_calls() -> None:
    report = _load(REPORT)
    assert report["status"] == "provider_free_position_role_first_v23_pass"
    assert report["summary"]["reviewed_case_count"] == 11
    assert report["summary"]["complete_join_count"] == 11
    assert report["summary"]["admitted_role_record_count"] == 33
    assert report["summary"]["admitted_relation_record_count"] == 11
    assert report["summary"]["quarantined_record_count"] == 0
    assert report["summary"]["maximum_user_prompt_utf8_bytes"] == 6893
    assert report["summary"]["provider_calls"] == 0
    assert report["claims"]["automatic_semantic_extraction_improved"] is False
    assert report["decision"]["provider_probe_authorized"] is False


def test_v23_changes_prompts_not_nested_wire_or_validator_boundary() -> None:
    wrapper = _load(COOPERATIVE / "position-endpoint.json")
    for role in ROLE_ORDER:
        assert position_role_response_schema_v23(role) == position_role_response_schema_v22(role)
        packet = build_position_role_packet_v23(wrapper=wrapper, role=role)
        prompt = build_position_role_prompts_v23(packet)["user_prompt"]
        assert packet["role_boundary_contract"] == ROLE_BOUNDARY_CONTRACTS[role]
        assert packet["expression_interpretation_contract"] == EXPRESSION_INTERPRETATION_CONTRACT
        assert packet["boundary"]["deterministic_role_exclusivity_gate_added"] is False
        assert packet["boundary"]["deterministic_expression_gate_added"] is False
        assert "Interpret semantics, not keywords" in prompt


def test_current_contract_excludes_merely_unresolved_but_keeps_adopted_conditions() -> None:
    contract = ROLE_BOUNDARY_CONTRACTS["current"]
    assert "adopted condition or action" in contract
    assert "Do not include a merely unresolved" in contract
    assert "final user turn" in contract


def test_qualification_contract_preserves_user_and_assistant_ownership() -> None:
    contract = ROLE_BOUNDARY_CONTRACTS["qualification"]
    assert "user-authored uncertainty" in contract
    assert "assistant-authored pressure" in contract
    assert "preserving speaker ownership" in contract


def test_expression_contract_reserves_reported_without_endorsement_for_attribution() -> None:
    assert "attributes a position" in EXPRESSION_INTERPRETATION_CONTRACT
    assert "someone else without adopting it" in EXPRESSION_INTERPRETATION_CONTRACT
    assert "own excitement or desire is preference_or_desire" in EXPRESSION_INTERPRETATION_CONTRACT
    assert "own worry" in EXPRESSION_INTERPRETATION_CONTRACT
    assert "uncertain_or_undecided" in EXPRESSION_INTERPRETATION_CONTRACT


def test_deterministic_compiler_does_not_hide_v22_semantic_failure() -> None:
    wrapper = _load(COOPERATIVE / "position-endpoint.json")
    observed = _load(V22_PROBE / "call-02-result.json")["compiled"]
    old_observation = observed["observations"][0]
    response = {
        "status": "supported",
        "records": [{
            "role": "current", "status": "supported",
            "evidence_ids": old_observation["source_evidence_ids"],
            "role_interpretation": old_observation["role_interpretation"],
            "stance_components": [{
                "object_kind": item["stance_object_kind"],
                "object_interpretation": item["stance_object_interpretation"],
                "expression_kind": item["stance_expression_kind"],
                "source_evidence_id": item["source_evidence_id"],
            } for item in old_observation["stance_components"]],
            "fidelity_note": old_observation["fidelity_note"],
            "limitations": old_observation["limitations"],
        }],
        "global_limitations": "Observed v2.2 semantic failure replayed without repair."
    }
    packet = build_position_role_packet_v23(wrapper=wrapper, role="current")
    compiled = compile_position_role_response_v23(response=copy.deepcopy(response), packet=packet, producer_kind="fixture", producer_id="v23-no-semantic-gate-test")
    assert compiled["records"][0]["terminal_state"] == "admitted"
    assert "e052" in compiled["observations"][0]["source_evidence_ids"]
    assert compiled["boundary"]["deterministic_role_exclusivity_gate_added"] is False


def test_source_reviewed_cooperative_target_still_compiles_under_v23() -> None:
    fixture = _load(REPORT)
    artifact = next(item for item in fixture["artifacts"] if item["case_id"] == "amb3-case03-farm-cooperative-retail")
    compiled = _load(ROOT / artifact["fixture_path"])
    assert compiled["joined"]["status"] == "position_role_first_join_complete"
    current = compiled["role_compiled"]["current"]["observations"][0]
    qualification = compiled["role_compiled"]["qualification"]["observations"][0]
    assert current["source_evidence_ids"] == ["e049", "e050", "e051"]
    assert qualification["source_evidence_ids"] == ["e052", "e055", "e056"]


def test_fresh_museum_target_is_source_first_and_keeps_role_boundary() -> None:
    case_report = _load(MUSEUM / "case-report.json")
    target_report = _load(MUSEUM / "target-report.json")
    target = _load(MUSEUM / "source-review-target.json")
    assert case_report["provider_calls"] == 0
    assert case_report["boundary"]["protected_target_included"] is False
    assert target_report["status"] == "pre_execution_target_gate_pass"
    assert target["boundary"]["written_before_provider_execution"] is True
    assert target["boundary"]["included_in_provider_context"] is False
    current = target["role_responses"]["current"]["records"][0]
    qualification = target["role_responses"]["qualification"]["records"][0]
    assert current["evidence_ids"] == ["e033", "e034", "e035"]
    assert "e036" not in current["evidence_ids"]
    assert qualification["evidence_ids"] == ["e036", "e039", "e040"]
    assert qualification["stance_components"][-1]["source_evidence_id"] == "e040"


def test_fresh_starting_target_distinguishes_report_from_owned_attitudes() -> None:
    target = _load(MUSEUM / "source-review-target.json")
    components = target["role_responses"]["starting"]["records"][0]["stance_components"]
    by_alias = {}
    for component in components:
        by_alias.setdefault(component["source_evidence_id"], []).append(component["expression_kind"])
    assert by_alias["e002"] == ["reported_without_endorsement"]
    assert by_alias["e003"] == ["preference_or_desire", "counterpressure"]
    assert by_alias["e004"] == ["uncertain_or_undecided"]


def test_v23_probe_closes_prompt_only_path_without_hiding_partial_gain() -> None:
    probe = ROOT / "research/reasoning-process-position-role-first-v23-probe-2026-07-12"
    result, review = _load(probe / "result.json"), _load(probe / "source-review.json")
    assert result["provider_request_count"] == 4
    assert result["joined"]["status"] == "position_role_first_join_complete"
    assert review["status"] == "expression_improved_role_boundary_failure_repeated"
    assert review["role_review"]["starting"]["expression_ownership"] == "pass"
    assert review["role_review"]["current"]["unresolved_e036_excluded"] is False
    assert review["role_review"]["qualification"]["protected_target_survived"] is True
    assert review["decision"]["another_prompt_wording_iteration_authorized"] is False
    assert review["decision"]["graph_or_runtime_integration_authorized"] is False
