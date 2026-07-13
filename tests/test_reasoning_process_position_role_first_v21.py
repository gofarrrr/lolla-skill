from __future__ import annotations

import json
from pathlib import Path

from engine.system_b.reasoning_process_position_role_first_v2 import (
    ROLE_ORDER,
    position_relation_response_schema_v2,
    position_role_response_schema_v2,
)
from engine.system_b.reasoning_process_position_role_first_v21 import (
    build_position_relation_packet_v21,
    build_position_relation_prompts_v21,
    build_position_role_packet_v21,
    build_position_role_prompts_v21,
    compile_position_relation_response_v21,
    compile_position_role_response_v21,
    join_position_role_first_v21,
    position_relation_response_schema_v21,
    position_role_response_schema_v21,
)
from scripts.evals.run_reasoning_process_position_role_first_v21_probe import (
    validate_authorization,
    validate_contract,
)

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "research/reasoning-process-position-role-first-v21-2026-07-12/report.json"
NEW_CASE = (
    ROOT / "research/reasoning-process-position-role-first-v2-new-case-2026-07-12"
)
V21_NEW_CASE = (
    ROOT / "research/reasoning-process-position-role-first-v21-new-case-2026-07-12"
)
V21_PROBE = (
    ROOT / "research/reasoning-process-position-role-first-v21-probe-2026-07-12"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_v21_changes_visible_semantic_contract_not_response_schema() -> None:
    for role in ROLE_ORDER:
        assert position_role_response_schema_v21(role) == position_role_response_schema_v2(role)
    assert position_relation_response_schema_v21() == position_relation_response_schema_v2()


def test_starting_contract_means_earliest_visible_endpoint_not_preconversation() -> None:
    wrapper = _load(NEW_CASE / "position-endpoint.json")
    packet = build_position_role_packet_v21(wrapper=wrapper, role="starting")
    assert "earliest visible working position" in packet["endpoint_definition"]
    assert "does not require a stance before the conversation" in packet["endpoint_definition"]
    assert packet["boundary"]["validator_changed_from_v2"] is False


def test_record_contract_distinguishes_records_aliases_and_components() -> None:
    wrapper = _load(NEW_CASE / "position-endpoint.json")
    packet = build_position_role_packet_v21(wrapper=wrapper, role="current")
    contract = packet["record_identity_contract"]
    assert "One record is one coherent position thread" in contract
    assert "Do not create one record per alias" in contract
    assert "aligned component index inside that same record" in contract
    prompt = build_position_role_prompts_v21(packet)["user_prompt"]
    assert len(prompt.encode("utf-8")) <= 5188


def test_qualification_contract_includes_assistant_pressure_without_endorsement() -> None:
    wrapper = _load(NEW_CASE / "position-endpoint.json")
    packet = build_position_role_packet_v21(wrapper=wrapper, role="qualification")
    assert "introduced by the assistant" in packet["endpoint_definition"]
    assert "does not imply user endorsement" in packet["endpoint_definition"]
    assert "Review every focal alias" in packet["source_coverage_contract"]


def test_v21_compiles_pre_execution_target_and_exact_relation_without_semantic_merge() -> None:
    wrapper = _load(NEW_CASE / "position-endpoint.json")
    target = _load(NEW_CASE / "source-review-target.json")
    frozen = _load(NEW_CASE / "compiled-source-review-target.json")
    roles = {}
    for role in ROLE_ORDER:
        packet = build_position_role_packet_v21(wrapper=wrapper, role=role)
        roles[role] = compile_position_role_response_v21(
            response=target["role_responses"][role],
            packet=packet,
            producer_kind="fixture",
            producer_id="v21-test",
        )
        assert roles[role]["records"][0]["terminal_state"] == "admitted"
        assert roles[role]["boundary"]["validator_changed_from_v2"] is False
    relation_packet = build_position_relation_packet_v21(
        role_compiled_by_role=roles
    )
    relation_prompt = build_position_relation_prompts_v21(relation_packet)["user_prompt"]
    assert "array order" in relation_packet["relationship_identity_contract"]
    assert len(relation_prompt.encode("utf-8")) <= 5188
    relation = compile_position_relation_response_v21(
        response=frozen["relation_response"],
        packet=relation_packet,
        producer_kind="fixture",
        producer_id="v21-test",
    )
    joined = join_position_role_first_v21(
        role_compiled_by_role=roles,
        relation_compiled=relation,
    )
    assert joined["status"] == "position_role_first_join_complete"
    assert joined["boundary"]["semantic_join_inferred_by_code"] is False


def test_provider_free_report_keeps_calls_blocked_and_claims_bounded() -> None:
    report = _load(REPORT)
    assert report["status"] == "provider_free_position_role_first_v21_pass"
    assert report["summary"]["reviewed_case_count"] == 9
    assert report["summary"]["complete_join_count"] == 9
    assert report["summary"]["response_schemas_byte_identical_to_v2"] is True
    assert report["summary"]["maximum_user_prompt_utf8_bytes"] == 5188
    assert report["summary"]["provider_calls"] == 0
    assert report["claims"]["automatic_extraction_improved"] is False
    assert report["decision"]["provider_probe_authorized"] is False


def test_v21_new_case_target_is_frozen_coherent_and_protects_irreversibility() -> None:
    case = _load(V21_NEW_CASE / "case-report.json")
    target = _load(V21_NEW_CASE / "source-review-target.json")
    target_report = _load(V21_NEW_CASE / "target-report.json")
    compiled = _load(V21_NEW_CASE / "compiled-source-review-target.json")
    wrapper = _load(V21_NEW_CASE / "position-endpoint.json")
    assert case["conversation_message_count"] == 14
    assert case["provider_calls"] == 0
    assert target["status"] == "source_reviewed_and_frozen_before_provider_execution"
    assert target["protected_target"]["evidence_id"] == "e056"
    assert target["boundary"]["included_in_provider_context"] is False
    assert target_report["status"] == "pre_execution_target_gate_pass"
    assert target_report["provider_calls"] == 0
    assert compiled["joined"]["status"] == "position_role_first_join_complete"
    for role in ROLE_ORDER:
        packet = build_position_role_packet_v21(wrapper=wrapper, role=role)
        prompt = build_position_role_prompts_v21(packet)["user_prompt"]
        assert "One record is one coherent position thread" in prompt
        assert len(prompt.encode("utf-8")) <= 5300


def test_v21_probe_contract_freezes_new_case_target_route_and_stop_rule() -> None:
    contract_path = V21_PROBE / "contract.json"
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    validate_authorization(
        _load(V21_PROBE / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert validation["provider_calls_made"] == 0
    assert contract["job"]["case_id"] == "amb3-case02-architecture-firm-succession"
    assert contract["protected_source_review"]["included_in_provider_context"] is False
    assert contract["budget"]["maximum_provider_calls"] == 4
    assert contract["stop_rules"]["if_protected_qualification_loss_repeats_stop_direct_structured_extraction"] is True
    assert contract["boundary"]["response_schemas_and_validators_unchanged_from_v2"] is True
