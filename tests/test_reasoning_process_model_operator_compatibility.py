from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_reasoning_process_model_operator_compatibility import (
    validate_authorization,
    validate_contract,
)
from scripts.evals.run_reasoning_process_model_operator_compatibility_v2 import (
    validate_authorization as validate_recovery_authorization,
    validate_contract as validate_recovery_contract,
)
from scripts.evals.run_reasoning_process_model_operator_single_compatibility import (
    validate_authorization as validate_single_authorization,
    validate_contract as validate_single_contract,
)

ROOT = Path(__file__).resolve().parents[1]
COMPATIBILITY_ROOT = (
    ROOT / "research/reasoning-process-model-operator-compatibility-2026-07-12"
)
SELECTION_ROOT = ROOT / "research/reasoning-process-model-operator-selection-2026-07-12"
RECOVERY_ROOT = (
    ROOT / "research/reasoning-process-model-operator-compatibility-recovery-2026-07-12"
)
DEEPSEEK_ALIBABA_ROOT = (
    ROOT / "research/reasoning-process-deepseek-alibaba-compatibility-2026-07-12"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_current_practice_shortlist_separates_cost_and_strength() -> None:
    snapshot = _load(SELECTION_ROOT / "current-practice-snapshot.json")
    assert snapshot["status"] == "frozen_july_2026_shortlist_before_compatibility_calls"
    pairs = snapshot["selected_compatibility_pairs"]
    assert [(item["model_id"], item["provider_slug"]) for item in pairs] == [
        ("deepseek/deepseek-v4-flash", "deepinfra"),
        ("z-ai/glm-5.2", "deepinfra"),
    ]
    assert pairs[0]["role"] == "cost_performance_candidate"
    assert pairs[1]["role"] == "stronger_reasoning_candidate"
    assert all(item["advertised_required_parameters_present"] for item in pairs)
    assert snapshot["nonclaims"]


def test_synthetic_packet_does_not_spend_a_semantic_case() -> None:
    packet = _load(SELECTION_ROOT / "synthetic-compatibility-packet.json")
    assert packet["packet"]["case_id"] == "synthetic-wire-compatibility-color-choice"
    assert packet["packet"]["boundary"]["protected_target_included"] is False
    assert packet["packet"]["boundary"]["source_review_fixture_included"] is False
    assert packet["packet"]["view_kind"] == "position_and_decision_trajectory"


def test_frozen_compatibility_contract_and_authorization_validate_without_calls() -> None:
    contract_path = COMPATIBILITY_ROOT / "contract.json"
    contract = _load(contract_path)
    validation = validate_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_authorization(
        _load(COMPATIBILITY_ROOT / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert contract["budget"]["maximum_provider_calls"] == 2
    assert contract["boundary"]["v42_schema_changed"] is False
    assert contract["boundary"]["semantic_accuracy_measured"] is False


def test_interrupted_batch_is_preserved_as_unknown_not_zero() -> None:
    incident = _load(COMPATIBILITY_ROOT / "custody-incident.json")
    assert incident["observation"]["exact_external_call_count_known"] is False
    assert incident["observation"]["provider_calls_possible"] == {
        "minimum": 0,
        "maximum": 2,
    }
    assert incident["decision"]["rerun_original_contract"] is False
    assert incident["decision"]["claim_zero_calls"] is False
    assert incident["decision"]["reserved_semantic_case_spent"] is False


def test_recovery_contract_requires_durable_per_call_custody() -> None:
    contract_path = RECOVERY_ROOT / "contract.json"
    contract = _load(contract_path)
    validation = validate_recovery_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_recovery_authorization(
        _load(RECOVERY_ROOT / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert contract["custody"]["write_started_marker_before_each_call"] is True
    assert contract["custody"]["never_rerun_if_started_marker_exists"] is True
    assert contract["custody"]["write_result_before_next_call"] is True
    assert contract["budget"]["maximum_total_possible_calls_including_unknown_incident"] == 4


def test_new_deepseek_alibaba_pair_is_not_a_deepinfra_retry() -> None:
    addendum = _load(SELECTION_ROOT / "deepseek-provider-addendum.json")
    assert addendum["failed_pair"]["provider_slug"] == "deepinfra"
    assert addendum["failed_pair"]["retry_authorized"] is False
    assert addendum["selected_new_pair"]["provider_slug"] == "alibaba"
    assert addendum["boundary"]["new_model_provider_pair"] is True
    assert addendum["boundary"]["deepinfra_retry"] is False

    contract_path = DEEPSEEK_ALIBABA_ROOT / "contract.json"
    contract = _load(contract_path)
    validation = validate_single_contract(contract, contract_path)
    assert validation["provider_calls_made"] == 0
    validate_single_authorization(
        _load(DEEPSEEK_ALIBABA_ROOT / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert contract["job"]["provider_slug"] == "alibaba"
    assert contract["budget"]["maximum_provider_calls"] == 1
