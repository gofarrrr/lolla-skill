from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from system_b.decision_pressure_trace_validation import (  # noqa: E402
    DecisionPressureTraceValidationError,
    validate_decision_pressure_trace_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "data" / "schemas" / "decision_pressure_trace.schema.json"
FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "decision_pressure_trace"
    / "gate4_3case_pr18_valid.json"
)
AFFORDANCES_V4_PATH = (
    REPO_ROOT / "data" / "compiled" / "model_affordances" / "affordances_v4.json"
)


def _load_fixture() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_schema_contract_file_exists_and_names_required_enums() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["status"]["enum"] == ["draft_review_only"]
    assert schema["properties"]["runtime_policy"]["enum"] == ["runtime_dormant"]
    assert set(schema["$defs"]["coverageStatus"]["enum"]) == {
        "fully_source_backed",
        "partially_source_backed",
        "coverage_transparency",
        "no_substrate_backed_pressure",
    }
    assert set(schema["$defs"]["provenanceClass"]["enum"]) == {
        "source_backed",
        "case_grounded",
        "llm_synthesized",
        "user_to_verify",
    }
    assert set(schema["$defs"]["userFacingReadiness"]["enum"]) == {
        "not_ready",
        "maybe_later",
        "candidate_after_review",
    }
    assert set(schema["$defs"]["v4Contribution"]["enum"]) == {
        "none",
        "minor",
        "material",
    }
    assert set(schema["$defs"]["suppressedDisposition"]["enum"]) == {
        "merged_support",
        "observatory_only",
        "still_suppressed",
        "needs_generation_test",
    }


def test_pr18_golden_fixture_validates_against_v4_affordances() -> None:
    validate_decision_pressure_trace_payload(
        _load_fixture(),
        path=FIXTURE_PATH,
        compiled_affordances_path=AFFORDANCES_V4_PATH,
    )


def test_runtime_policy_must_remain_dormant() -> None:
    payload = _load_fixture()
    payload["runtime_policy"] = "observatory_live"

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="runtime_policy must be runtime_dormant",
    ):
        validate_decision_pressure_trace_payload(
            payload,
            path=Path("live_trace.json"),
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_trace_rejects_more_than_three_selected_pressures() -> None:
    payload = _load_fixture()
    fourth = copy.deepcopy(payload["selected_pressures"][0])
    fourth["pressure_id"] = "extra-pressure-that-would-create-bloat"
    payload["selected_pressures"].append(fourth)

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="selected_pressures must not exceed 3",
    ):
        validate_decision_pressure_trace_payload(
            payload,
            path=Path("bloated_trace.json"),
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_selected_pressure_requires_provenance_for_user_visible_fields() -> None:
    payload = _load_fixture()
    del payload["selected_pressures"][0]["provenance_by_field"]["what_to_verify"]

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="what_to_verify",
    ):
        validate_decision_pressure_trace_payload(
            payload,
            path=Path("missing_provenance.json"),
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_selected_pressure_rejects_unknown_source_affordance_ids() -> None:
    payload = _load_fixture()
    payload["selected_pressures"][0]["source_affordances"].append(
        "imaginary-model.imaginary-affordance"
    )

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="unknown source_affordance",
    ):
        validate_decision_pressure_trace_payload(
            payload,
            path=Path("unknown_affordance_trace.json"),
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_no_substrate_backed_panel_requires_missing_model_ids() -> None:
    payload = _load_fixture()
    payload["coverage_transparency_panels"][0]["missing_model_ids"] = []

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="missing_model_ids.*must not be empty",
    ):
        validate_decision_pressure_trace_payload(
            payload,
            path=Path("empty_coverage_gap_trace.json"),
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_merged_support_candidate_references_existing_selected_pressure() -> None:
    payload = _load_fixture()
    payload["suppressed_candidates"][0][
        "related_selected_pressure_id"
    ] = "missing-selected-pressure"

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="merged_support candidate must reference an existing selected pressure",
    ):
        validate_decision_pressure_trace_payload(
            payload,
            path=Path("broken_merged_support_trace.json"),
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )


def test_principal_agent_support_preserves_medium_confidence_caution() -> None:
    payload = _load_fixture()
    payload["selected_pressures"][1][
        "operator_note"
    ] = "This card describes signal quality without adding the required confidence warning."
    payload["review_notes"][
        "principal_agent_medium_confidence_caution"
    ] = "Principal-agent support is useful when delegated evidence can drift."

    with pytest.raises(
        DecisionPressureTraceValidationError,
        match="medium-confidence caution",
    ):
        validate_decision_pressure_trace_payload(
            payload,
            path=Path("principal_agent_without_caution.json"),
            compiled_affordances_path=AFFORDANCES_V4_PATH,
        )
