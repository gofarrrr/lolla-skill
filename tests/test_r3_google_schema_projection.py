from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.r3_google_schema_projection import (
    BOUNDARY_TEXT_MAX,
    EFFECT_TEXT_MAX,
    REQUIRED_ROW_TEXT_MAX,
    R3GoogleProjectionError,
    compile_projected_pressure_response,
    lint_google_documented_schema_subset,
    validate_projection_bundle,
)
from scripts.evals.build_r3_google_schema_repair import (
    build,
    validate_contract as validate_repair_contract,
)
from scripts.evals.run_r3_fresh_consumer_pressure import (
    validate_contract as validate_original_r3_contract,
)


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_CONTRACT = (
    ROOT / "docs/evals/lolla-r3-fresh-consumer-pressure-contract-v1.json"
)
ORIGINAL_AUTHORIZATION = (
    ROOT / "docs/evals/lolla-r3-fresh-consumer-pressure-authorization-v1.json"
)
REPAIR_CONTRACT = ROOT / "docs/evals/lolla-r3-google-schema-repair-contract-v1.json"
BASE_BUNDLE = ROOT / (
    "research/lolla-r3-fresh-consumer-2026-07-13/preflight/pressure-bundle.json"
)


def _base_bundle() -> dict:
    return json.loads(BASE_BUNDLE.read_text(encoding="utf-8"))


def _projection_bundle() -> dict:
    return build()["bundle"]


def _valid_response(bundle: dict) -> dict:
    rows = []
    active = bundle["packet"]["constitutional_graph_survival"][
        "active_pressure_items"
    ]
    for index, item in enumerate(active):
        disposition = "apply" if index == 0 else "park" if index == 1 else "reject"
        rows.append(
            {
                "pressure_id": item["pressure_id"],
                "disposition": disposition,
                "source_turn_numbers": [1, 2],
                "effect": "new_condition"
                if disposition == "apply"
                else "no_material_effect",
                "strongest_plausible_application": (
                    "This is the strongest source-grounded application to inspect."
                ),
                "attempted_application_condition": (
                    "The supplied turns would need to establish the proposed mechanism."
                ),
                "why": (
                    "The source supports a bounded use."
                    if disposition == "apply"
                    else "The source does not yet support a public change."
                ),
                "disposition_boundary": (
                    "Reopen if later evidence contradicts the condition."
                    if disposition != "reject"
                    else "No supplied turn establishes the required mechanism."
                ),
                "visible_effect": (
                    "Treat the condition as a reversal test." if disposition == "apply" else ""
                ),
                "private_guardrail": "",
            }
        )
    return {
        "candidate_dispositions": rows,
        "reconsidered_answer": "Preserve the source-grounded advice with one earned condition.",
        "change_summary": "One pressure added a condition; one was parked; seven were rejected.",
        "original_answer_preservation": "preserved",
    }


def test_projection_reduces_failed_schema_to_documented_subset_and_reference_size() -> None:
    artifacts = build()
    bundle = artifacts["bundle"]
    comparison = artifacts["comparison"]
    summary = artifacts["summary"]

    assert artifacts["lint"]["status"] == "pass_documented_subset"
    assert artifacts["lint"]["errors"] == []
    assert comparison["failed_r3_schema"]["total_object_properties"] == 18
    assert comparison["projected_schema"]["total_object_properties"] == 14
    assert comparison["projected_schema"]["string_length_constraint_count"] == 0
    reference = comparison["operational_smaller_reference"]
    assert reference["status"] == "historical_smaller_schema_operational_success"
    assert reference["metrics"]["total_object_properties"] == 14
    assert reference["documented_subset_lint"]["status"] == (
        "fail_documented_subset"
    )
    assert summary["provider_calls"] == 0
    assert summary["next_call_authorized"] is False
    assert summary["maximum_estimated_call_cost_usd"] <= 0.01
    assert bundle["request_contract"]["provider_calls_authorized"] == 0


def test_projection_preserves_source_portfolio_provider_and_no_recovery_policy() -> None:
    base = _base_bundle()
    bundle = _projection_bundle()

    validate_projection_bundle(bundle, base_bundle=base)
    assert bundle["packet"] == base["packet"]
    assert bundle["base_r3_bundle_sha256"] == base["bundle_sha256"]
    assert [
        item["pressure_id"]
        for item in bundle["packet"]["constitutional_graph_survival"][
            "active_pressure_items"
        ]
    ] == [
        item["pressure_id"]
        for item in base["packet"]["constitutional_graph_survival"][
            "active_pressure_items"
        ]
    ]
    assert len(
        bundle["packet"]["constitutional_graph_survival"]["active_pressure_items"]
    ) == 9
    assert bundle["request_body"]["provider"] == base["request_body"]["provider"]
    assert bundle["request_body"]["model"] == "google/gemini-3.1-flash-lite"
    assert bundle["request_contract"]["automatic_retries"] == 0
    assert bundle["request_contract"]["fallback_models"] == 0
    assert bundle["request_contract"]["response_healing"] is False
    assert bundle["provider_calls_made"] == 0
    assert bundle["next_call_authorized"] is False


def test_projection_compiles_apply_park_reject_into_original_canonical_shape() -> None:
    bundle = _projection_bundle()
    response = _valid_response(bundle)
    compiled = compile_projected_pressure_response(
        response=response,
        packet=bundle["packet"],
    )
    active = bundle["packet"]["constitutional_graph_survival"][
        "active_pressure_items"
    ]

    assert compiled["disposition_counts"] == {"apply": 1, "park": 1, "reject": 7}
    assert compiled["all_active_candidates_accounted_for"] is True
    assert compiled["candidate_dispositions"][0]["model_id"] == active[0]["model_id"]
    assert compiled["candidate_dispositions"][0]["reopen_condition"]
    assert compiled["candidate_dispositions"][0]["failed_condition"] == ""
    assert compiled["candidate_dispositions"][1]["reopen_condition"]
    assert compiled["candidate_dispositions"][2]["failed_condition"]
    assert compiled["candidate_dispositions"][2]["reopen_condition"] == ""
    for row, source in zip(compiled["candidate_dispositions"], active):
        assert row["risk_if_forced"] == source["force_boundary"]
        assert row["risk_if_ignored"] == source["ignore_boundary"]
    custody = compiled["provider_projection"]
    assert custody["semantic_applicability_inferred_by_code"] is False
    assert custody["keyword_or_chronology_gate_added"] is False
    assert custody["deterministically_restored_fields"] == [
        "model_id",
        "risk_if_forced",
        "risk_if_ignored",
        "failed_condition_or_reopen_condition_name",
    ]


@pytest.mark.parametrize(
    ("field", "maximum"),
    [
        ("strongest_plausible_application", REQUIRED_ROW_TEXT_MAX),
        ("attempted_application_condition", REQUIRED_ROW_TEXT_MAX),
        ("why", REQUIRED_ROW_TEXT_MAX),
        ("disposition_boundary", BOUNDARY_TEXT_MAX),
        ("visible_effect", EFFECT_TEXT_MAX),
        ("private_guardrail", EFFECT_TEXT_MAX),
    ],
)
def test_projection_enforces_provider_removed_text_lengths_locally(
    field: str, maximum: int
) -> None:
    bundle = _projection_bundle()
    response = _valid_response(bundle)
    response["candidate_dispositions"][0][field] = "x" * (maximum + 1)
    with pytest.raises(R3GoogleProjectionError, match="length boundary"):
        compile_projected_pressure_response(
            response=response,
            packet=bundle["packet"],
        )


def test_projection_rejects_identity_drift_and_forced_reject_effect() -> None:
    bundle = _projection_bundle()
    response = _valid_response(bundle)
    wrong_identity = copy.deepcopy(response)
    wrong_identity["candidate_dispositions"][0]["pressure_id"] = (
        wrong_identity["candidate_dispositions"][1]["pressure_id"]
    )
    with pytest.raises(R3GoogleProjectionError, match="identity or order"):
        compile_projected_pressure_response(
            response=wrong_identity,
            packet=bundle["packet"],
        )

    forced = copy.deepcopy(response)
    forced["candidate_dispositions"][2]["visible_effect"] = "Force public prose."
    with pytest.raises(R3GoogleProjectionError, match="reject cannot claim"):
        compile_projected_pressure_response(
            response=forced,
            packet=bundle["packet"],
        )


def test_documented_subset_lint_rejects_undocumented_string_constraints() -> None:
    schema = {
        "type": "object",
        "properties": {
            "value": {
                "type": "string",
                "minLength": 1,
                "maxLength": 10,
                "pattern": "^x$",
            }
        },
        "required": ["value"],
        "additionalProperties": False,
    }
    lint = lint_google_documented_schema_subset(schema)
    assert lint["status"] == "fail_documented_subset"
    assert {item["code"] for item in lint["errors"]} == {"undocumented_keyword"}
    assert {item["path"] for item in lint["errors"]} == {
        "/properties/value/minLength",
        "/properties/value/maxLength",
        "/properties/value/pattern",
    }


def test_projection_bundle_tamper_and_original_r3_mutation_are_detected() -> None:
    base = _base_bundle()
    bundle = _projection_bundle()
    tampered = copy.deepcopy(bundle)
    tampered["request_body"]["provider"]["allow_fallbacks"] = True
    with pytest.raises(R3GoogleProjectionError, match="hash"):
        validate_projection_bundle(tampered, base_bundle=base)

    original_contract, original_bundle = validate_original_r3_contract(
        contract_path=ORIGINAL_CONTRACT,
        authorization_path=ORIGINAL_AUTHORIZATION,
    )
    assert original_contract["status"] == "frozen_before_one_pressure_call"
    assert original_bundle["bundle_sha256"] == base["bundle_sha256"]


def test_frozen_repair_contract_authorizes_zero_calls() -> None:
    contract, bundle = validate_repair_contract(REPAIR_CONTRACT)
    assert contract["provider_boundary"] == {
        "provider_calls_made": 0,
        "provider_calls_authorized": 0,
        "next_call_authorized": False,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models_authorized": False,
        "maximum_future_attempts_without_new_authorization": 0,
    }
    assert bundle["provider_calls_made"] == 0
    assert bundle["next_call_authorized"] is False
