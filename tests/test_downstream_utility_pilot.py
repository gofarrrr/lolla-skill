from __future__ import annotations

import json
from pathlib import Path

from scripts.evals.run_downstream_utility_pilot import (
    _validate_response,
    build_call_specs,
    run_pilot,
    validate_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT / "research/downstream-utility-pilot-2026-07-10/pilot-contract.json"
)
QUIET_CONTRACT_PATH = (
    REPO_ROOT
    / "research/downstream-utility-quiet-pilot-2026-07-10/pilot-contract.json"
)


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_pilot_contract_is_hash_locked_and_exactly_two_calls() -> None:
    contract = _contract()
    validate_contract(contract)
    assert contract["status"] == "frozen_before_calls"
    assert contract["call_configuration"]["total_generation_calls"] == 2
    assert contract["call_configuration"]["evaluator_calls"] == 0
    assert contract["call_configuration"]["samples_per_arm"] == 1
    assert "no_automatic_retry" in contract["stop_rules"]


def test_control_and_treatment_share_source_and_neutral_instruction() -> None:
    specs = build_call_specs(_contract())
    assert {spec["arm_id"] for spec in specs} == {
        "strong_reconsideration_control",
        "lolla_pressure_treatment",
    }
    by_arm = {spec["arm_id"]: spec for spec in specs}
    control = by_arm["strong_reconsideration_control"]["user_prompt"]
    treatment = by_arm["lolla_pressure_treatment"]["user_prompt"]
    assert "COMPLETE CONVERSATION" in control
    assert "COMPLETE CONVERSATION" in treatment
    assert "Reassess the prior reasoning from scratch" in control
    assert "Reassess the prior reasoning from scratch" in treatment
    assert "SOURCE-GROUNDED CHALLENGE PRESSURE" not in control
    assert "SOURCE-GROUNDED CHALLENGE PRESSURE" in treatment
    assert "Treat these as questions to consider, not conclusions or commands" in treatment


def test_generation_does_not_receive_expected_delta_or_review_label() -> None:
    for spec in build_call_specs(_contract()):
        prompt = spec["system_prompt"] + spec["user_prompt"]
        assert "human_review" not in prompt
        assert "expected_delta" not in prompt
        assert "Both prospects get the same written paid pilot shape" not in prompt


def test_quiet_case_explicitly_treats_public_bloat_as_failure() -> None:
    contract = json.loads(QUIET_CONTRACT_PATH.read_text(encoding="utf-8"))
    validate_contract(contract)
    assert contract["case"]["case_role"] == "quiet_standdown_and_non_bloat_pilot"
    assert "public_bloat_or_manufactured_shifts_fail_the_quiet_case" in contract[
        "stop_rules"
    ]
    specs = build_call_specs(contract)
    for spec in specs:
        assert "do not manufacture shifts" in spec["user_prompt"]


def test_runner_reports_cost_without_changing_call_budget(monkeypatch) -> None:
    contract = _contract()
    monkeypatch.setattr(
        "scripts.evals.run_downstream_utility_pilot._call_openrouter",
        lambda spec, _contract: {
            "blind_label": spec["blind_label"],
            "status": "ok",
            "response": {},
            "validation_errors": [],
            "metadata": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        },
    )
    _, _, summary = run_pilot(contract)
    assert summary["call_count"] == 2
    assert summary["prompt_tokens"] == 200
    assert summary["completion_tokens"] == 100
    assert summary["estimated_cost_usd"] == 0.00125
    assert summary["pricing_table_version"] == "2026-05-25"


def test_prospective_contract_can_enforce_value_types() -> None:
    contract = _contract()
    contract["output_contract"]["field_types"] = {
        "updated_position": "string",
        "what_survived": "array_of_strings",
        "take_backs_or_set_aside": "array_of_strings",
        "material_shifts": "array_of_objects",
        "uncertainties": "array_of_strings",
    }
    valid = {
        "updated_position": "conditional",
        "what_survived": ["one"],
        "take_backs_or_set_aside": ["two"],
        "material_shifts": [
            {
                "shift": "change",
                "source_basis": "turn 2",
                "action_consequence": "verify",
            }
        ],
        "uncertainties": ["three"],
    }
    assert _validate_response(valid, contract) == []
    invalid = dict(valid, what_survived="• one")
    assert "what_survived must be an array of strings" in _validate_response(
        invalid, contract
    )


def test_prospective_contract_validates_pressure_packet_and_upstream_hashes(
    tmp_path: Path, monkeypatch
) -> None:
    contract = _contract()
    packet = {
        "items": contract["treatment_pressure_packet"],
    }
    packet_path = tmp_path / "packet.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    artifact_path = tmp_path / "upstream.json"
    artifact_path.write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    import hashlib

    monkeypatch.setattr(
        "scripts.evals.run_downstream_utility_pilot.REPO_ROOT", tmp_path
    )
    contract["protocol"]["path"] = "protocol.json"
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text("{}", encoding="utf-8")
    contract["protocol"]["sha256"] = hashlib.sha256(
        protocol_path.read_bytes()
    ).hexdigest()
    contract["case"]["source_path"] = "source.txt"
    source_path = tmp_path / "source.txt"
    source_path.write_text("conversation", encoding="utf-8")
    contract["case"]["source_sha256"] = hashlib.sha256(
        source_path.read_bytes()
    ).hexdigest()
    contract["treatment_pressure_packet_source"] = {
        "path": "packet.json",
        "sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
    }
    contract["source_artifacts"] = [
        {
            "path": "upstream.json",
            "sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
        }
    ]
    validate_contract(contract)
    contract["source_artifacts"][0]["sha256"] = "0" * 64
    try:
        validate_contract(contract)
    except Exception as exc:
        assert "source artifact hash mismatch" in str(exc)
    else:
        raise AssertionError("expected source artifact hash mismatch")


def test_prospective_contract_validates_accountable_edge_disposition() -> None:
    contract = _contract()
    contract["output_contract"]["required_keys"].append("edge_dispositions")
    contract["output_contract"]["field_types"] = {
        "updated_position": "string",
        "what_survived": "array_of_strings",
        "take_backs_or_set_aside": "array_of_strings",
        "material_shifts": "array_of_objects",
        "uncertainties": "array_of_strings",
        "edge_dispositions": "array_of_objects",
    }
    edge_keys = [
        "pressure_id",
        "strongest_plausible_application",
        "disposition",
        "why",
        "visible_effect",
        "private_guardrail",
        "risk_if_forced",
        "risk_if_ignored",
    ]
    contract["output_contract"]["object_array_contracts"] = {
        "edge_dispositions": {
            "required_keys": edge_keys,
            "maximum_items": 1,
            "allowed_values": {
                "disposition": ["use", "reject", "defer", "private_guardrail"]
            },
        }
    }
    response = {
        "updated_position": "hold boundary without diagnosis",
        "what_survived": [],
        "take_backs_or_set_aside": [],
        "material_shifts": [],
        "uncertainties": [],
        "edge_dispositions": [
            {
                "pressure_id": "edge-empathy",
                "strongest_plausible_application": "reflect pain as a guess",
                "disposition": "private_guardrail",
                "why": "prevents mind-reading",
                "visible_effect": "remove character diagnosis",
                "private_guardrail": "keep the financial boundary",
                "risk_if_forced": "self-erasure",
                "risk_if_ignored": "relationship becomes a character test",
            }
        ],
    }
    assert _validate_response(response, contract) == []
    response["edge_dispositions"][0]["disposition"] = "not_considered"
    assert (
        "edge_dispositions[0].disposition has invalid value"
        in _validate_response(response, contract)
    )


def _exact_pressure_custody_contract() -> dict:
    contract = _contract()
    contract["treatment_pressure_packet"] = [
        {
            "pressure_id": "pressure-opaque-001",
            "source_turns": [1, 2],
            "challenge": "Test this pressure without assuming it is correct.",
        }
    ]
    contract["output_contract"]["required_keys"].append("edge_dispositions")
    contract["output_contract"]["field_types"] = {
        "updated_position": "string",
        "what_survived": "array_of_strings",
        "take_backs_or_set_aside": "array_of_strings",
        "material_shifts": "array_of_objects",
        "uncertainties": "array_of_strings",
        "edge_dispositions": "array_of_objects",
    }
    contract["output_contract"]["object_array_contracts"] = {
        "edge_dispositions": {
            "required_keys": [
                "pressure_id",
                "strongest_plausible_application",
                "disposition",
                "why",
                "visible_effect",
                "private_guardrail",
                "risk_if_forced",
                "risk_if_ignored",
            ],
            "maximum_items": 1,
            "allowed_values": {
                "pressure_id": ["pressure-opaque-001"],
                "disposition": ["use", "reject", "defer", "private_guardrail"],
            },
            "id_custody": {
                "source": "treatment_pressure_packet",
                "source_id_field": "pressure_id",
                "item_id_field": "pressure_id",
                "coverage": "exactly_once_in_treatment_empty_in_control",
            },
        }
    }
    return contract


def _exact_pressure_response(pressure_id: str) -> dict:
    return {
        "updated_position": "conditional",
        "what_survived": [],
        "take_backs_or_set_aside": [],
        "material_shifts": [],
        "uncertainties": [],
        "edge_dispositions": [
            {
                "pressure_id": pressure_id,
                "strongest_plausible_application": "check one dependency",
                "disposition": "private_guardrail",
                "why": "it is useful privately",
                "visible_effect": "",
                "private_guardrail": "do not overstate the evidence",
                "risk_if_forced": "manufactured friction",
                "risk_if_ignored": "missed dependency",
            }
        ],
    }


def test_exact_pressure_custody_is_frozen_into_contract_and_prompts() -> None:
    contract = _exact_pressure_custody_contract()
    validate_contract(contract)
    specs = {spec["arm_id"]: spec for spec in build_call_specs(contract)}
    control_prompt = specs["strong_reconsideration_control"]["user_prompt"]
    treatment_prompt = specs["lolla_pressure_treatment"]["user_prompt"]
    assert "pressure-opaque-001" not in control_prompt
    assert "must be an empty array" in control_prompt
    assert "pressure-opaque-001" in treatment_prompt
    assert "copy each pressure_id exactly" in treatment_prompt


def test_exact_pressure_custody_rejects_renaming_missing_and_control_leakage() -> None:
    contract = _exact_pressure_custody_contract()
    valid = _exact_pressure_response("pressure-opaque-001")
    assert _validate_response(
        valid,
        contract,
        arm_id="lolla_pressure_treatment",
    ) == []

    renamed = _exact_pressure_response("renamed-pressure")
    errors = _validate_response(
        renamed,
        contract,
        arm_id="lolla_pressure_treatment",
    )
    assert "edge_dispositions[0].pressure_id has invalid value" in errors
    assert (
        "edge_dispositions must cover treatment pressure IDs exactly once in packet order"
        in errors
    )

    missing = dict(valid, edge_dispositions=[])
    assert (
        "edge_dispositions must cover treatment pressure IDs exactly once in packet order"
        in _validate_response(
            missing,
            contract,
            arm_id="lolla_pressure_treatment",
        )
    )
    assert "edge_dispositions must be empty in control arm" in _validate_response(
        valid,
        contract,
        arm_id="strong_reconsideration_control",
    )


def test_exact_pressure_custody_contract_rejects_drifted_id_list() -> None:
    contract = _exact_pressure_custody_contract()
    contract["output_contract"]["object_array_contracts"]["edge_dispositions"][
        "allowed_values"
    ]["pressure_id"] = ["renamed-pressure"]
    try:
        validate_contract(contract)
    except Exception as exc:
        assert "allowed values must exactly match" in str(exc)
    else:
        raise AssertionError("expected pressure ID custody contract failure")
