from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.r3_task_shape_counterfactual import (
    OUTCOME_MAP,
    R3TaskShapeError,
    build_synthesis_packet,
    collapsed_disposition_schema,
    collapsed_one_pass_request_body,
    collapsed_one_pass_schema,
    compile_collapsed_one_pass_response,
    compile_disposition_stage_response,
    compile_separated_synthesis_response,
    disposition_stage_request_body,
    request_metrics,
    synthesis_response_schema,
    synthesis_stage_request_body,
)
from engine.system_b.r3_google_schema_projection import (
    lint_google_documented_schema_subset,
)
from scripts.evals.build_r3_task_shape_reassessment import validate


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / (
    "research/lolla-r3-fresh-consumer-2026-07-13/"
    "provider-free-repair-v1/prospective-pressure-bundle.json"
)
OUTPUT = ROOT / "research/lolla-r3-task-shape-reassessment-2026-07-13"


def _bundle() -> dict:
    return json.loads(BUNDLE.read_text(encoding="utf-8"))


def _response(packet: dict, *, with_synthesis: bool) -> dict:
    rows = []
    outcomes = ["apply_new_condition", "reject", "park"]
    for index, item in enumerate(
        packet["constitutional_graph_survival"]["active_pressure_items"]
    ):
        outcome = outcomes[index] if index < len(outcomes) else "reject"
        applied = outcome.startswith("apply_")
        rows.append(
            {
                "pressure_id": item["pressure_id"],
                "outcome": outcome,
                "source_turn_numbers": [1],
                "strongest_plausible_application": (
                    "Test the strongest source-grounded use of the pressure."
                ),
                "attempted_application_condition": (
                    "The supplied source must establish the pressure mechanism."
                ),
                "why": "Fixture judgment with exact source custody.",
                "disposition_boundary": (
                    "Reopen or falsify when the declared condition changes."
                ),
                "visible_effect": (
                    "Add one bounded source-grounded condition." if applied else ""
                ),
                "private_guardrail": "",
            }
        )
    response = {"candidate_dispositions": rows}
    if with_synthesis:
        response.update(
            {
                "reconsidered_answer": (
                    "Preserve the original recommendation with one earned condition."
                ),
                "change_summary": "One condition was added; other pressure stood down.",
                "original_answer_preservation": "preserved",
            }
        )
    return response


def test_collapsed_outcome_is_exact_controlled_mapping_not_semantic_gate() -> None:
    assert OUTCOME_MAP == {
        "apply_new_alternative": ("apply", "new_alternative"),
        "apply_new_condition": ("apply", "new_condition"),
        "apply_reframe": ("apply", "reframe"),
        "apply_reinforces_existing": ("apply", "reinforces_existing"),
        "apply_reversal_rule": ("apply", "reversal_rule"),
        "apply_uncertainty_change": ("apply", "uncertainty_change"),
        "reject": ("reject", "no_material_effect"),
        "park": ("park", "no_material_effect"),
    }


def test_all_counterfactual_schemas_pass_documented_subset() -> None:
    packet = _bundle()["packet"]
    for schema in (
        collapsed_disposition_schema(packet),
        collapsed_one_pass_schema(packet),
        synthesis_response_schema(),
    ):
        assert lint_google_documented_schema_subset(schema)["status"] == (
            "pass_documented_subset"
        )


def test_collapsed_one_pass_preserves_all_nine_and_all_disposition_paths() -> None:
    packet = _bundle()["packet"]
    response = _response(packet, with_synthesis=True)

    compiled = compile_collapsed_one_pass_response(
        response=response,
        packet=packet,
    )

    assert compiled["all_active_candidates_accounted_for"] is True
    assert len(compiled["candidate_dispositions"]) == 9
    assert compiled["disposition_counts"] == {"apply": 1, "park": 1, "reject": 7}
    assert [row["pressure_id"] for row in compiled["candidate_dispositions"]] == [
        row["pressure_id"]
        for row in packet["constitutional_graph_survival"]["active_pressure_items"]
    ]
    assert compiled["counterfactual_projection"] == {
        "schema_version": "lolla.r3_task_shape_counterfactual.v1",
        "wire_outcome_mapped_deterministically": True,
        "semantic_applicability_inferred_by_code": False,
        "candidate_deletion_allowed": False,
    }


def test_collapsed_contract_still_fails_effect_custody_instead_of_healing() -> None:
    packet = _bundle()["packet"]
    response = _response(packet, with_synthesis=True)
    response["candidate_dispositions"][1]["visible_effect"] = "Do something."

    with pytest.raises(R3TaskShapeError, match="reject claims effect custody"):
        compile_collapsed_one_pass_response(response=response, packet=packet)


def test_collapsed_contract_rejects_identity_and_outcome_tampering() -> None:
    packet = _bundle()["packet"]
    response = _response(packet, with_synthesis=True)
    response["candidate_dispositions"][0]["pressure_id"] = "invented"
    with pytest.raises(R3TaskShapeError, match="identity or order drifted"):
        compile_collapsed_one_pass_response(response=response, packet=packet)

    response = _response(packet, with_synthesis=True)
    response["candidate_dispositions"][0]["outcome"] = "apply_no_material_effect"
    with pytest.raises(R3TaskShapeError, match="outcome is invalid"):
        compile_collapsed_one_pass_response(response=response, packet=packet)


def test_separated_synthesis_cannot_change_frozen_dispositions() -> None:
    packet = _bundle()["packet"]
    disposition_response = _response(packet, with_synthesis=False)
    ledger = compile_disposition_stage_response(
        response=disposition_response,
        packet=packet,
    )
    synthesis_packet = build_synthesis_packet(packet=packet, ledger=ledger)
    synthesis_response = {
        "reconsidered_answer": "Preserve the bounded recommendation.",
        "change_summary": "No additional public change.",
        "original_answer_preservation": "preserved",
    }

    compiled = compile_separated_synthesis_response(
        response=synthesis_response,
        packet=packet,
        ledger=ledger,
    )

    assert compiled["separated_synthesis"]["dispositions_changed_by_synthesis"] is False
    assert compiled["candidate_dispositions"] == ledger["candidate_dispositions"]
    assert synthesis_packet["disposition_ledger"]["ledger_sha256"] == (
        ledger["ledger_sha256"]
    )

    tampered = copy.deepcopy(ledger)
    tampered["candidate_dispositions"][0]["disposition"] = "park"
    with pytest.raises(R3TaskShapeError, match="hash drifted"):
        build_synthesis_packet(packet=packet, ledger=tampered)


def test_comparison_request_metrics_expose_split_cost_and_fan_in() -> None:
    bundle = _bundle()
    packet = bundle["packet"]
    base = bundle["request_body"]
    collapsed = request_metrics(
        collapsed_one_pass_request_body(base_body=base, packet=packet)
    )
    disposition = request_metrics(
        disposition_stage_request_body(base_body=base, packet=packet)
    )
    ledger = compile_disposition_stage_response(
        response=_response(packet, with_synthesis=False),
        packet=packet,
    )
    synthesis_packet = build_synthesis_packet(packet=packet, ledger=ledger)
    synthesis = request_metrics(
        synthesis_stage_request_body(
            base_body=base,
            synthesis_packet=synthesis_packet,
        )
    )

    assert collapsed["maximum_estimated_cost_usd"] < 0.01
    assert disposition["maximum_output_tokens"] == 3200
    assert synthesis["maximum_output_tokens"] == 1400
    assert collapsed["response_schema_metrics"]["total_object_properties"] == 13
    assert disposition["response_schema_metrics"]["total_object_properties"] == 10
    assert synthesis["response_schema_metrics"]["total_object_properties"] == 3


def test_checked_in_reassessment_is_hash_locked_zero_call_decision() -> None:
    summary = validate(OUTPUT)
    decision = json.loads((OUTPUT / "decision.json").read_text(encoding="utf-8"))
    comparison = json.loads(
        (OUTPUT / "comparison-vector.json").read_text(encoding="utf-8")
    )
    failure = json.loads(
        (OUTPUT / "failure-causal-audit.json").read_text(encoding="utf-8")
    )

    assert summary["selected_design"] == "collapsed_outcome_one_pass"
    assert summary["provider_calls"] == 0
    assert summary["next_call_authorized"] is False
    assert decision["status"] == "redesign_wire_keep_one_pass_split_not_earned"
    assert decision["future_experiment"]["current_provider_calls_authorized"] == 0
    assert comparison["scalar_quality_score"] is None
    alternatives = {
        row["alternative"]: row for row in comparison["alternatives"]
    }
    current = alternatives["current_one_pass"]
    collapsed = alternatives["collapsed_outcome_one_pass"]
    separated = alternatives["separated_disposition_then_synthesis"]
    assert current["active_candidates_at_fan_in"] == 9
    assert collapsed["active_candidates_at_fan_in"] == 9
    assert collapsed["provider_calls_per_run"] == 1
    assert collapsed["transfer_boundaries"] == 0
    assert collapsed["deterministic_semantic_leakage"] is False
    assert separated["provider_calls_per_run"] == 2
    assert separated["serial_call_depth"] == 2
    assert separated["transfer_boundaries"] == 1
    assert separated["maximum_estimated_cost_usd"] > (
        collapsed["maximum_estimated_cost_usd"]
    )
    assert failure["lossless_collapsed_outcome_mapping"] is False
    assert failure["diagnosis_vector"]["combined_task_overload"] == (
        "possible_not_established"
    )

    contracts_path = OUTPUT / "counterfactual-contracts.json"
    contracts_text = contracts_path.read_text(encoding="utf-8")
    contracts = json.loads(contracts_text)
    assert contracts_path.stat().st_size < 20_000
    assert "authoritative_conversation" not in contracts_text
    assert contracts["current_one_pass"]["source_path"].endswith(
        "prospective-pressure-bundle.json"
    )
    assert contracts["collapsed_outcome_one_pass"]["reconstruction_function"].endswith(
        "collapsed_one_pass_request_body"
    )
