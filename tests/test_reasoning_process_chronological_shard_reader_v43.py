from __future__ import annotations

import copy
import json
from pathlib import Path

from engine.system_b.reasoning_process_chronological_shard_reader_v42 import (
    build_shard_prompts_v42,
    shard_response_schema_v42,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v43 import (
    ROLE_COMPONENT_COVERAGE_INSTRUCTION_V43,
    build_shard_prompts_v43,
    compile_shard_response_recordwise_v43,
    shard_response_schema_v43,
)
from scripts.evals.run_reasoning_process_model_operator_v43_development import (
    validate_authorization,
    validate_contract,
)
from scripts.evals.run_reasoning_process_model_operator_v43_controls import (
    validate_authorization as validate_controls_authorization,
    validate_contract as validate_controls_contract,
)

ROOT = Path(__file__).resolve().parents[1]
SELECTION_ROOT = ROOT / "research/reasoning-process-model-operator-selection-2026-07-12"
DEEPSEEK_ROOT = ROOT / "research/reasoning-process-deepseek-alibaba-compatibility-2026-07-12"
V43_DEVELOPMENT_ROOT = (
    ROOT / "research/reasoning-process-model-operator-v43-development-2026-07-12"
)
V43_CONTROLS_ROOT = ROOT / "research/reasoning-process-model-operator-v43-controls-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_v43_provider_schema_is_identical_to_v42() -> None:
    for view in (
        "position_and_decision_trajectory",
        "evidence_and_assumption_discipline",
        "uncertainty_and_unresolved_state",
        "challenge_and_revision_response",
    ):
        assert shard_response_schema_v43(view) == shard_response_schema_v42(view)


def test_v43_changes_only_position_user_prompt_with_explicit_role_coverage() -> None:
    wrapper = _load(SELECTION_ROOT / "synthetic-compatibility-packet.json")
    v42 = build_shard_prompts_v42(wrapper)
    v43 = build_shard_prompts_v43(wrapper)
    assert v43["system_prompt"] == v42["system_prompt"]
    assert v43["system_prompt_sha256"] == v42["system_prompt_sha256"]
    assert ROLE_COMPONENT_COVERAGE_INSTRUCTION_V43 not in v42["user_prompt"]
    assert ROLE_COMPONENT_COVERAGE_INSTRUCTION_V43 in v43["user_prompt"]
    assert v43["user_prompt"] == v42["user_prompt"].replace(
        "\nQuestion: ",
        "\nRole-component coverage contract: "
        + ROLE_COMPONENT_COVERAGE_INSTRUCTION_V43
        + "\nQuestion: ",
        1,
    )


def test_deepseek_record_admits_when_implicit_starting_component_is_added() -> None:
    wrapper = _load(SELECTION_ROOT / "synthetic-compatibility-packet.json")
    response = copy.deepcopy(_load(DEEPSEEK_ROOT / "result.json")["call"]["candidate_payload"])
    record = response["records"][0]
    record["stance_temporal_roles"].insert(0, "starting")
    record["stance_object_kinds"].insert(0, "action_or_proposal")
    record["stance_object_interpretations"].insert(0, "blue for the prototype")
    record["stance_expression_kinds"].insert(0, "preference_or_desire")
    record["stance_source_evidence_ids"].insert(0, "e002")

    compiled = compile_shard_response_recordwise_v43(
        response=response,
        wrapper=wrapper,
        producer_kind="provider_free_alignment_fixture",
        producer_id="deepseek-record-plus-explicit-starting-component",
        record_identity="v43-role-component-coverage",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    assert compiled["records"][0]["terminal_state"] == "admitted"
    assert compiled["boundary"]["provider_schema_changed_from_v42"] is False
    assert compiled["boundary"]["record_validator_changed_from_v42"] is False
    assert compiled["boundary"]["role_component_coverage_made_explicit"] is True


def test_compatibility_review_does_not_promote_wire_success_to_model_quality() -> None:
    review = _load(
        ROOT
        / "research/reasoning-process-model-operator-compatibility-2026-07-12/compatibility-review.json"
    )
    assert review["hypothesis_updates"]["v42_schema_universally_invalid_or_too_complex"] is False
    assert review["hypothesis_updates"]["deepseek_or_glm_semantic_quality_proven"] is False
    assert review["decision"]["semantic_case_comparison_ready"] is False
    assert review["decision"]["v43_prompt_only_alignment_correction_authorized"] is True


def test_frozen_v43_model_pair_contract_validates_without_calls() -> None:
    contract_path = V43_DEVELOPMENT_ROOT / "contract.json"
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_authorization(
        _load(V43_DEVELOPMENT_ROOT / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert contract["request_contract"]["provider_schema_changed_from_v42"] is False
    assert contract["request_contract"]["validator_changed_from_v42"] is False
    assert contract["budget"]["maximum_provider_calls"] == 2


def test_stronger_controls_are_selected_from_current_evidence_not_promoted() -> None:
    snapshot = _load(SELECTION_ROOT / "stronger-controls-snapshot.json")
    assert [(item["model_id"], item["provider_slug"]) for item in snapshot["selected_pairs"]] == [
        ("deepseek/deepseek-v4-pro", "alibaba"),
        ("minimax/minimax-m3", "parasail"),
    ]
    assert snapshot["boundary"]["benchmark_is_selection_hint_not_lolla_evidence"] is True

    contract_path = V43_CONTROLS_ROOT / "contract.json"
    contract = _load(contract_path)
    validation = validate_controls_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_controls_authorization(
        _load(V43_CONTROLS_ROOT / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert contract["boundary"]["agency_acquisition_call_authorized"] is False


def test_v43_development_and_stronger_control_results_preserve_stop_line() -> None:
    development = _load(V43_DEVELOPMENT_ROOT / "result.json")
    development_review = _load(V43_DEVELOPMENT_ROOT / "source-review.json")
    controls = _load(V43_CONTROLS_ROOT / "result.json")
    terminal = _load(SELECTION_ROOT / "terminal-review.json")

    assert development["provider_request_count"] == 2
    assert development["wire_accepted_count"] == 2
    assert development["admitted_pair_count"] == 1
    assert development_review["decision"]["flash_pair_ready_for_reserved_semantic_case"] is False

    assert controls["provider_request_count"] == 2
    assert controls["wire_accepted_count"] == 2
    assert controls["admitted_pair_count"] == 0
    assert terminal["status"] == (
        "provider_compatibility_resolved_no_model_passes_combined_semantic_contract"
    )
    assert terminal["known_cost_custody"][
        "provider_reported_cost_usd_for_preserved_successful_calls"
    ] == 0.005799432
    assert terminal["decision"]["production_model_selected"] is False
    assert terminal["decision"]["agency_acquisition_case_called"] is False
    assert terminal["decision"]["additional_model_calls_authorized"] is False
    assert terminal["decision"]["next_work"] == (
        "provider_free_decomposition_of_role_trajectory_extraction_from_stance_object_decomposition"
    )
