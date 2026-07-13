from __future__ import annotations

import copy
import json
from pathlib import Path

from engine.system_b.reasoning_process_chronological_shard_reader_v43 import (
    shard_response_schema_v43,
)
from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_position_decomposition_v1 import (
    build_stance_role_packet_v1,
    compile_stance_role_response_v1,
    join_position_decomposition_v1,
    role_trajectory_response_schema_v1,
    stance_role_response_schema_v1,
)
from scripts.evals.build_reasoning_process_position_decomposition_v1 import build
from scripts.evals.run_reasoning_process_position_decomposition_probe import (
    validate_authorization,
    validate_contract,
)

ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "research/reasoning-process-position-decomposition-v1-2026-07-12/report.json"
)
PROBE_CONTRACT = (
    ROOT / "research/reasoning-process-position-decomposition-probe-2026-07-12/contract.json"
)
PROBE_AUTHORIZATION = (
    ROOT
    / "research/reasoning-process-position-decomposition-probe-2026-07-12/authorization.json"
)
FIXTURE = (
    ROOT
    / "research/reasoning-process-position-decomposition-v1-2026-07-12/fixtures/amb1-case01-product-scope.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fixture() -> dict:
    return _load(FIXTURE)


def _compile(role: str, response: dict, packet: dict) -> dict:
    return compile_stance_role_response_v1(
        response=response,
        packet=packet,
        producer_kind="fixture",
        producer_id="adversarial-local-test",
    )


def test_each_decomposed_schema_is_smaller_than_the_v43_monolith() -> None:
    monolithic = schema_metrics(shard_response_schema_v43("position_and_decision_trajectory"))
    schemas = [
        role_trajectory_response_schema_v1(),
        stance_role_response_schema_v1("starting"),
        stance_role_response_schema_v1("current"),
        stance_role_response_schema_v1("qualification"),
    ]
    assert all(schema_metrics(schema)["bytes"] < monolithic["bytes"] for schema in schemas)
    assert "uniqueItems" not in json.dumps(schemas, sort_keys=True)


def test_provider_free_replay_preserves_capacity_and_keeps_reserved_case_untouched(
    tmp_path: Path,
) -> None:
    report = build(tmp_path / "decomposition")
    assert report["status"] == "provider_free_position_decomposition_pass"
    assert report["summary"]["reviewed_input_fixture_count"] == 23
    assert report["summary"]["reviewed_position_fixture_count"] == 8
    assert report["summary"]["provider_free_decomposition_fixture_count"] == 7
    assert report["summary"]["complete_join_count"] == 7
    assert report["summary"]["quarantined_record_count"] == 0
    assert report["summary"]["missing_role_record_count"] == 0
    assert report["summary"]["maximum_planned_calls_per_shard"] == 4
    assert report["reserved_case"]["case_id"] == "amb2-case03-agency-acquisition"
    assert report["reserved_case"]["projection_performed"] is False
    assert report["summary"]["provider_calls"] == 0


def test_role_packet_contains_only_fixed_role_evidence_with_verified_text() -> None:
    fixture = _fixture()
    packet = fixture["stance_packets"]["starting"]
    assert packet["role"] == "starting"
    assert packet["boundary"]["other_roles_included"] is False
    assert packet["boundary"]["source_text_hash_verified"] is True
    assert [item["alias"] for item in packet["records"][0]["evidence"]] == ["e005"]
    assert "Northline" not in packet["records"][0]["evidence"][0]["text"]


def test_unknown_trajectory_id_is_quarantined_and_expected_id_remains_missing() -> None:
    fixture = _fixture()
    packet = fixture["stance_packets"]["current"]
    response = copy.deepcopy(fixture["stance_responses"]["current"])
    response["records"][0]["trajectory_record_id"] = "unknown-trajectory"
    compiled = _compile("current", response, packet)
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert compiled["missing_trajectory_record_ids"] == [
        packet["records"][0]["trajectory_record_id"]
    ]


def test_cross_role_evidence_is_quarantined() -> None:
    fixture = _fixture()
    packet = fixture["stance_packets"]["current"]
    response = copy.deepcopy(fixture["stance_responses"]["current"])
    response["records"][0]["source_evidence_ids"][0] = "e005"
    compiled = _compile("current", response, packet)
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert "role-packet alias" in compiled["records"][0]["reason"]


def test_unequal_component_columns_are_quarantined() -> None:
    fixture = _fixture()
    packet = fixture["stance_packets"]["qualification"]
    response = copy.deepcopy(fixture["stance_responses"]["qualification"])
    response["records"][0]["object_kinds"].pop()
    compiled = _compile("qualification", response, packet)
    assert compiled["records"][0]["terminal_state"] == "quarantined"
    assert "equal bounded lengths" in compiled["records"][0]["reason"]


def test_valid_but_semantically_dubious_category_pair_is_not_gated_by_code() -> None:
    fixture = _fixture()
    packet = fixture["stance_packets"]["current"]
    response = copy.deepcopy(fixture["stance_responses"]["current"])
    response["records"][0]["object_kinds"][0] = "acceptance_or_willingness"
    response["records"][0]["expression_kinds"][0] = "commitment"
    compiled = _compile("current", response, packet)
    assert compiled["records"][0]["terminal_state"] == "admitted"
    assert compiled["boundary"]["object_expression_compatibility_gate_added"] is False
    assert compiled["boundary"]["semantic_category_correctness_inferred_by_code"] is False


def test_join_preserves_missing_role_instead_of_filling_it() -> None:
    fixture = _fixture()
    stance = copy.deepcopy(fixture["stance_compiled"])
    stance["starting"] = None
    joined = join_position_decomposition_v1(
        trajectory_compiled=fixture["trajectory_compiled"],
        stance_compiled_by_role=stance,
    )
    assert joined["status"] == "position_decomposition_incomplete"
    assert joined["role_disposition_counts"]["missing"] == 1
    assert joined["records"][0]["stance_by_role"]["starting"]["disposition"] == "missing"
    assert joined["boundary"]["missing_or_quarantined_roles_filled"] is False


def test_empty_starting_role_requires_no_stance_call() -> None:
    candidate = _fixture()
    trajectory = copy.deepcopy(candidate["trajectory_compiled"])
    raw = trajectory["observations"][0]["raw_record"]["record"]
    raw["starting_state_evidence_ids"] = []
    raw["starting_position_interpretation"] = ""
    packet = build_stance_role_packet_v1(
        trajectory_compiled=trajectory,
        wrapper=_load(ROOT / candidate["source"]["packet_path"]),
        role="starting",
    )
    assert packet["records"] == []
    assert packet["call_required"] is False
    stance = copy.deepcopy(candidate["stance_compiled"])
    stance["starting"] = None
    joined = join_position_decomposition_v1(
        trajectory_compiled=trajectory,
        stance_compiled_by_role=stance,
    )
    assert joined["role_disposition_counts"]["not_applicable"] == 1


def test_result_claims_only_local_representational_capacity() -> None:
    report = _load(RESULT)
    assert report["claims"]["representational_capacity_preserved_on_reviewed_position_fixtures"] is True
    assert report["claims"]["automatic_extraction_improved"] is False
    assert report["claims"]["provider_acceptance_proven"] is False
    assert report["claims"]["semantic_quality_improved"] is False
    assert report["decision"]["provider_probe_authorized"] is False


def test_probe_contract_freezes_reserved_case_route_budget_and_inputs() -> None:
    contract = _load(PROBE_CONTRACT)
    validation = validate_contract(contract, PROBE_CONTRACT)
    validate_authorization(
        _load(PROBE_AUTHORIZATION),
        contract=contract,
        contract_path=PROBE_CONTRACT,
    )
    assert validation["provider_calls_made"] == 0
    assert contract["job"]["case_id"] == "amb2-case03-agency-acquisition"
    assert contract["job"]["model"] == "deepseek/deepseek-v4-flash"
    assert contract["job"]["provider_slug"] == "alibaba"
    assert contract["budget"]["maximum_provider_calls"] == 4
    assert contract["budget"]["maximum_estimated_cost_usd"] == 0.01
    assert contract["protected_source_review"]["included_in_provider_context"] is False
    assert contract["boundary"]["deterministic_semantic_gate_added"] is False
