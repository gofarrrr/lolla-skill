from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_position_role_first_v24 import (
    build_position_current_qualification_packet_v24,
    build_position_current_qualification_prompts_v24,
    compile_position_current_qualification_response_v24,
    position_current_qualification_response_schema_v24,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reasoning-process-position-role-first-v24-2026-07-12/report.json"
MUSEUM = ROOT / "research/reasoning-process-position-role-first-v23-new-case-2026-07-12"
REGISTRY = ROOT / "research/reasoning-process-position-role-first-v24-new-case-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _museum_pair() -> tuple[dict, dict]:
    wrapper = _load(MUSEUM / "position-endpoint.json")
    target = _load(MUSEUM / "source-review-target.json")
    response = {
        "current_status": "supported", "qualification_status": "supported",
        "records": [*target["role_responses"]["current"]["records"], *target["role_responses"]["qualification"]["records"]],
        "allocation_note": "Current and qualification allocated comparatively.",
        "global_limitations": "Synthetic reviewed target.",
    }
    return wrapper, response


def test_v24_provider_free_replays_twelve_cases_at_three_call_ceiling() -> None:
    report = _load(REPORT)
    assert report["status"] == "provider_free_position_role_first_v24_pass"
    assert report["summary"]["reviewed_case_count"] == 12
    assert report["summary"]["complete_join_count"] == 12
    assert report["summary"]["admitted_role_record_count"] == 36
    assert report["summary"]["admitted_relation_record_count"] == 12
    assert report["summary"]["quarantined_record_count"] == 0
    assert report["summary"]["maximum_provider_calls_per_case"] == 3
    assert report["summary"]["maximum_user_prompt_utf8_bytes"] == 7378
    assert report["summary"]["provider_calls"] == 0
    assert report["claims"]["automatic_semantic_allocation_improved"] is False


def test_paired_schema_is_bounded_and_uses_one_role_labeled_record_list() -> None:
    schema = position_current_qualification_response_schema_v24()
    assert set(schema["properties"]) == {"current_status", "qualification_status", "records", "allocation_note", "global_limitations"}
    assert schema["properties"]["records"]["maxItems"] == 4
    record = schema["properties"]["records"]["items"]
    assert record["properties"]["role"]["enum"] == ["current", "qualification"]
    assert "current_records" not in json.dumps(schema)
    assert "qualification_records" not in json.dumps(schema)


def test_packet_rejects_hard_alias_exclusivity_and_semantic_code_gates() -> None:
    wrapper, _ = _museum_pair()
    packet = build_position_current_qualification_packet_v24(wrapper=wrapper)
    assert packet["boundary"]["hard_alias_exclusivity_required"] is False
    assert packet["boundary"]["deterministic_alias_subtraction_added"] is False
    assert packet["boundary"]["deterministic_semantic_role_gate_added"] is False
    assert packet["boundary"]["semantic_score_added"] is False
    assert packet["boundary"]["maximum_pipeline_calls"] == 3
    prompt = build_position_current_qualification_prompts_v24(packet)["user_prompt"]
    assert "If one alias genuinely contains both" in prompt


def test_source_reviewed_museum_pair_compiles_to_two_role_custody_streams() -> None:
    wrapper, response = _museum_pair()
    compiled = compile_position_current_qualification_response_v24(response=response, wrapper=wrapper, producer_kind="source_reviewer", producer_id="v24-test")
    current = compiled["role_compiled"]["current"]["observations"][0]
    qualification = compiled["role_compiled"]["qualification"]["observations"][0]
    assert current["source_evidence_ids"] == ["e033", "e034", "e035"]
    assert qualification["source_evidence_ids"] == ["e036", "e039", "e040"]
    assert compiled["boundary"]["model_role_labels_split_mechanically"] is True
    assert compiled["boundary"]["semantic_role_correctness_inferred_by_code"] is False


def test_shared_alias_with_distinct_meanings_is_allowed_not_subtracted() -> None:
    wrapper, response = _museum_pair()
    current = response["records"][0]
    qualification = response["records"][1]
    current["evidence_ids"].append("e036")
    current["stance_components"].append({"object_kind": "intended_outcome_or_policy", "object_interpretation": "Keep contributor exit meaningful as an adopted approval objective.", "expression_kind": "conditional_willingness", "source_evidence_id": "e036"})
    qualification["evidence_ids"] = ["e036"]
    qualification["stance_components"] = [qualification["stance_components"][0]]
    qualification["role_interpretation"] = "The feasibility of meaningful contributor exit remains unresolved."
    compiled = compile_position_current_qualification_response_v24(response=response, wrapper=wrapper, producer_kind="fixture", producer_id="v24-shared-alias")
    assert "e036" in compiled["role_compiled"]["current"]["observations"][0]["source_evidence_ids"]
    assert "e036" in compiled["role_compiled"]["qualification"]["observations"][0]["source_evidence_ids"]
    assert compiled["boundary"]["hard_alias_exclusivity_enforced"] is False


def test_duplicate_unresolved_meaning_is_admitted_for_source_review_not_hidden() -> None:
    wrapper, response = _museum_pair()
    current = response["records"][0]
    unresolved = copy.deepcopy(response["records"][1]["stance_components"][0])
    current["evidence_ids"].append("e036")
    current["stance_components"].append(unresolved)
    compiled = compile_position_current_qualification_response_v24(response=response, wrapper=wrapper, producer_kind="fixture", producer_id="v24-no-semantic-gate")
    assert compiled["role_compiled"]["current"]["records"][0]["terminal_state"] == "admitted"
    assert compiled["boundary"]["semantic_role_correctness_inferred_by_code"] is False


def test_unknown_role_label_fails_before_role_compilation() -> None:
    wrapper, response = _museum_pair()
    response["records"][0]["role"] = "uncertainty"
    with pytest.raises(ViewSpecificInterfaceError, match="record role"):
        compile_position_current_qualification_response_v24(response=response, wrapper=wrapper, producer_kind="fixture", producer_id="v24-bad-role")


def test_qualification_component_limit_remains_role_specific_after_split() -> None:
    wrapper, response = _museum_pair()
    qualification = response["records"][1]
    qualification["stance_components"].extend(copy.deepcopy(qualification["stance_components"][:2]))
    compiled = compile_position_current_qualification_response_v24(response=response, wrapper=wrapper, producer_kind="fixture", producer_id="v24-limit")
    assert compiled["role_compiled"]["qualification"]["records"][0]["terminal_state"] == "quarantined"


def test_fresh_registry_target_is_source_first_and_compiles_shared_alias() -> None:
    case_report, target_report = _load(REGISTRY / "case-report.json"), _load(REGISTRY / "target-report.json")
    target, compiled = _load(REGISTRY / "source-review-target.json"), _load(REGISTRY / "compiled-source-review-target.json")
    assert case_report["provider_calls"] == 0
    assert case_report["boundary"]["protected_target_included"] is False
    assert target_report["status"] == "pre_execution_target_gate_pass"
    assert target["boundary"]["written_before_provider_execution"] is True
    current, qualification = target["paired_response"]["records"]
    assert "e036" in current["evidence_ids"]
    assert "e036" in qualification["evidence_ids"]
    assert current["stance_components"][-1]["expression_kind"] == "conditional_willingness"
    assert qualification["stance_components"][0]["expression_kind"] == "uncertain_or_undecided"
    assert compiled["joined"]["status"] == "position_role_first_join_complete"
    assert compiled["paired_compiled"]["boundary"]["hard_alias_exclusivity_enforced"] is False
