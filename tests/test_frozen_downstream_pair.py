from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.evals import run_frozen_downstream_pair as pair


REQUIRED_ROLES = {
    "pair_runner",
    "source_conversation",
    "stage_a_contract",
    "stage_a_gate",
    "private_table_snapshot",
    "v60_snapshot",
    "preliminary_pressure_review",
    "pressure_packet",
    "two_stage_protocol",
    "downstream_experiment_protocol",
    "pricing",
}


def _write(path: Path, value: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.setattr(pair, "REPO_ROOT", tmp_path)
    source = tmp_path / "source.txt"
    source_hash = _write(
        source,
        "[Turn 1] USER:\nShould I choose?\n\n[Turn 1] ASSISTANT:\nVerify first.\n",
    )
    pressures = [
        {
            "pressure_id": "pressure-one",
            "source_turns": [1],
            "lineage_chunk_ids": ["aff::one"],
            "challenge": "Check whether evidence supports the current threshold.",
        }
    ]
    packet = tmp_path / "packet.json"
    packet_hash = _write(packet, json.dumps({"pressure_items": pressures}))
    locks = []
    for role in sorted(REQUIRED_ROLES):
        if role == "source_conversation":
            path, digest = source, source_hash
        elif role == "pressure_packet":
            path, digest = packet, packet_hash
        else:
            path = tmp_path / "locks" / f"{role}.txt"
            digest = _write(path, role)
        locks.append(
            {"role": role, "path": str(path.relative_to(tmp_path)), "sha256": digest}
        )
    output_dir = Path("research/pair/run")
    contract = {
        "schema_version": pair.CONTRACT_SCHEMA,
        "status": "frozen_before_calls",
        "run_id": "pair_test_a1",
        "case": {
            "case_id": "case-test",
            "source_path": "source.txt",
            "source_sha256": source_hash,
        },
        "treatment_pressure_packet_source": {
            "path": "packet.json",
            "sha256": packet_hash,
        },
        "treatment_pressure_packet": pressures,
        "system_prompt": "Reassess carefully and return only JSON.",
        "neutral_reconsideration_instruction": "Reassess the prior reasoning from scratch.",
        "output_contract": {
            "required_keys": [
                "decision_state_read",
                "updated_position",
                "what_survived",
                "take_backs_or_set_aside",
                "material_shifts",
                "pressure_dispositions",
                "next_actions",
                "uncertainties",
            ],
            "field_types": {
                "decision_state_read": "string",
                "updated_position": "string",
                "what_survived": "array_of_strings",
                "take_backs_or_set_aside": "array_of_strings",
                "material_shifts": "array_of_objects",
                "pressure_dispositions": "array_of_objects",
                "next_actions": "array_of_strings",
                "uncertainties": "array_of_strings",
            },
            "material_shift_required_keys": [
                "shift",
                "source_basis",
                "action_consequence",
            ],
            "maximum_material_shifts": 4,
            "object_array_contracts": {
                "pressure_dispositions": {
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
                        "pressure_id": ["pressure-one"],
                        "disposition": [
                            "use",
                            "reject",
                            "defer",
                            "private_guardrail",
                        ],
                    },
                    "id_custody": {
                        "source": "treatment_pressure_packet",
                        "source_id_field": "pressure_id",
                        "item_id_field": "pressure_id",
                        "coverage": "exactly_once_in_treatment_empty_in_control",
                    },
                }
            },
        },
        "call_configuration": {
            "provider": "openrouter",
            "model": "openai/gpt-5.1-chat",
            "temperature": 0.2,
            "max_output_tokens": 1800,
            "reasoning_effort": "none",
            "samples_per_arm": 1,
            "total_generation_calls": 2,
            "evaluator_calls": 0,
            "automatic_retries": 0,
            "provider_timeout_seconds": 5,
            "wall_clock_timeout_seconds": 10,
        },
        "call_budget": {
            "estimated_cost_ceiling_usd": 0.15,
            "pricing_table_version": "2026-05-25",
        },
        "blind_label_seed": "test-seed",
        "artifacts": {
            "output_dir": str(output_dir),
            "blind_outputs_path": str(output_dir / "blind-outputs.json"),
            "arm_key_path": str(output_dir / "arm-key.json"),
            "run_summary_path": str(output_dir / "run-summary.json"),
            "call_custody_path": str(output_dir / "call-custody.json"),
        },
        "hash_locks": locks,
        "source_red_lines": {
            "must_preserve": ["decision unresolved"],
            "must_not_invent": ["the correct decision"],
        },
        "stop_rules": ["exactly_one_call_per_arm"],
        "non_claims": ["not product proof"],
    }
    contract["prompt_hashes"] = pair._prompt_hashes(contract)
    return contract


def _response(*, treatment: bool) -> dict:
    dispositions = []
    if treatment:
        dispositions = [
            {
                "pressure_id": "pressure-one",
                "strongest_plausible_application": "verify the threshold",
                "disposition": "private_guardrail",
                "why": "evidence remains incomplete",
                "visible_effect": "",
                "private_guardrail": "do not claim certainty",
                "risk_if_forced": "process bloat",
                "risk_if_ignored": "unsupported threshold",
            }
        ]
    return {
        "decision_state_read": "unresolved",
        "updated_position": "verify first",
        "what_survived": ["preserve useful advice"],
        "take_backs_or_set_aside": [],
        "material_shifts": [],
        "pressure_dispositions": dispositions,
        "next_actions": ["verify"],
        "uncertainties": ["outcome"],
    }


def test_contract_freezes_hashes_prompts_and_exact_two_call_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)
    pair.validate_contract(contract)
    assert contract["call_configuration"]["total_generation_calls"] == 2
    assert contract["call_configuration"]["evaluator_calls"] == 0
    assert contract["call_configuration"]["automatic_retries"] == 0


def test_control_is_isolated_and_treatment_receives_question_not_expected_answer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)
    specs = {item["arm_id"]: item for item in pair.build_call_specs(contract)}
    control = specs["strong_reconsideration_control"]["user_prompt"]
    treatment = specs["lolla_pressure_treatment"]["user_prompt"]
    assert "SOURCE-GROUNDED CHALLENGE PRESSURE" not in control
    assert "pressure-one" not in control
    assert "SOURCE-GROUNDED CHALLENGE PRESSURE" in treatment
    assert "pressure-one" in treatment
    assert "questions to consider, not conclusions or commands" in treatment
    assert "expected answer" not in treatment.lower()


def test_typed_pressure_custody_is_exact_and_control_must_be_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)
    assert pair._validate_response(
        _response(treatment=True), contract, arm_id="lolla_pressure_treatment"
    ) == []
    assert pair._validate_response(
        _response(treatment=False), contract, arm_id="strong_reconsideration_control"
    ) == []
    renamed = _response(treatment=True)
    renamed["pressure_dispositions"][0]["pressure_id"] = "renamed"
    assert pair._validate_response(
        renamed, contract, arm_id="lolla_pressure_treatment"
    )


def test_runner_persists_two_blind_calls_and_passes_all_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)

    def fake_call(spec: dict, _contract: dict) -> dict:
        treatment = spec["arm_id"] == "lolla_pressure_treatment"
        return {
            "blind_label": spec["blind_label"],
            "call_attempted": True,
            "requested_model": "openai/gpt-5.1-chat",
            "served_model": "openai/gpt-5.1-chat-20260701",
            "model_attribution_status": "served_version_alias",
            "status": "ok",
            "response": _response(treatment=treatment),
            "validation_errors": [],
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150,
            "reasoning_tokens": 0,
            "usage_evidence_state": "complete",
            "raw_provider_content_included": False,
        }

    monkeypatch.setattr(pair, "_call_openrouter", fake_call)
    observed = []
    blind, key, summary = pair.run_pair(contract, on_call=observed.append)
    assert summary["status"] == "passed"
    assert summary["call_count"] == 2
    assert len(observed) == 2
    assert blind["arm_identity_included"] is False
    assert all("arm_id" not in output for output in blind["outputs"])
    assert {item["arm_id"] for item in key["mapping"]} == {
        "strong_reconsideration_control",
        "lolla_pressure_treatment",
    }


def test_contract_rejects_transitive_hash_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _fixture(tmp_path, monkeypatch)
    locked = tmp_path / contract["hash_locks"][0]["path"]
    locked.write_text("drift", encoding="utf-8")
    with pytest.raises(pair.PairContractError, match="hash lock mismatch"):
        pair.validate_contract(contract)
