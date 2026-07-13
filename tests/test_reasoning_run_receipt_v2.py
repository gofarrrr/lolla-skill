from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.evals.validate_reasoning_run_receipt_v2 import (
    RECEIPT_SCHEMA_VERSION,
    ReasoningRunReceiptValidationError,
    validate_reasoning_run_receipt,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs/evals/reasoning-run-receipt-v2.json"
DOC_PATH = ROOT / "docs/evals/reasoning-run-receipt-v2.md"
FIXTURE_PATH = (
    ROOT / "tests/fixtures/reasoning_run_receipt_v2/prospective-valid.json"
)


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _fixture() -> dict:
    return deepcopy(_json(FIXTURE_PATH))


def _assert_error(receipt: dict, text: str) -> None:
    with pytest.raises(ReasoningRunReceiptValidationError) as caught:
        validate_reasoning_run_receipt(receipt)
    assert text in str(caught.value)


def test_schema_pins_repaired_top_level_contract_and_no_pressure_floor() -> None:
    schema = _json(SCHEMA_PATH)
    fixture = _fixture()
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == RECEIPT_SCHEMA_VERSION
    assert set(schema["required"]) == set(fixture)
    pressure = schema["properties"]["pressure_accountability"]
    assert pressure["maxItems"] == 12
    assert "minItems" not in pressure
    pressure_required = set(schema["$defs"]["pressure_item"]["required"])
    assert {
        "observed_consumer_pressure_id",
        "identity_status",
        "semantic_hearing_status",
        "effect_consistency_status",
    } <= pressure_required
    comparison_required = set(schema["$defs"]["comparison_evidence"]["required"])
    assert {"anonymous_outputs", "reveal_mapping", "blind_review_summary"} <= (
        comparison_required
    )
    operability_required = set(schema["$defs"]["operability"]["required"])
    assert {"token_evidence_state", "token_scope"} <= operability_required


def test_valid_prospective_fixture_passes_provider_free_cross_field_checks() -> None:
    result = validate_reasoning_run_receipt(_fixture())
    assert result["status"] == "cross_field_valid"
    assert result["provider_calls"] == 0
    assert result["semantic_quality_scored"] is False
    assert result["runtime_change_authorized"] is False


def test_source_action_and_deadline_cannot_be_silently_omitted() -> None:
    receipt = _fixture()
    receipt["source_end_state"]["stated_next_action"] = {
        "status": "present",
        "summary": "",
        "source_refs": [],
    }
    _assert_error(receipt, "stated_next_action present requires")

    receipt = _fixture()
    receipt["source_end_state"]["deadline_or_time_constraint"] = {
        "status": "unknown",
        "summary": "still has prose",
        "source_refs": [],
    }
    _assert_error(receipt, "deadline_or_time_constraint unknown")


def test_source_and_artifact_references_must_exist() -> None:
    receipt = _fixture()
    receipt["reasoning_process"]["interpretations"][0]["source_refs"] = [
        "missing-source"
    ]
    _assert_error(receipt, "unknown references")

    receipt = _fixture()
    receipt["comparison_evidence"]["artifact_refs"] = ["missing-artifact"]
    _assert_error(receipt, "unknown references")


def test_custody_support_cannot_be_upgraded_to_proof() -> None:
    receipt = _fixture()
    receipt["custody_boundary"]["summary"] = "The hashes prove execution completeness."
    _assert_error(receipt, "custody support language must not use proof terminology")


def test_graph_exposure_cannot_be_rewritten_as_absolute_non_use() -> None:
    receipt = _fixture()
    receipt["graph_attribution"]["summary"] = (
        "Graph chunks were not used in pressures."
    )
    _assert_error(receipt, "graph summary overclaims absent influence")


def test_causal_graph_claim_requires_exact_lineage_and_complete_disposition() -> None:
    receipt = _fixture()
    graph = receipt["graph_attribution"]
    graph["causal_contribution_status"] = "directional_only"
    graph["statement_scope"] = "causal_ablation"
    _assert_error(receipt, "causal graph claims require exact lineage")


def test_pressure_identity_mismatch_can_be_preserved_without_laundering() -> None:
    receipt = _fixture()
    pressure = receipt["pressure_accountability"][0]
    pressure["observed_consumer_pressure_id"] = "renamed-pressure"
    pressure["identity_status"] = "mismatch"
    pressure["origin"] = "v60_affordance"
    pressure["semantic_hearing_status"] = "substantive"
    pressure["effect_consistency_status"] = "inconsistent"
    assert validate_reasoning_run_receipt(receipt)["status"] == "cross_field_valid"

    pressure["identity_status"] = "exact_match"
    _assert_error(receipt, "exact identity must match pressure_id")


def test_anonymous_outputs_and_reveal_mapping_must_share_labels() -> None:
    receipt = _fixture()
    receipt["comparison_evidence"]["reveal_mapping"][1]["blind_label"] = "C"
    _assert_error(receipt, "anonymous output and reveal mapping labels must match")


def test_partial_token_evidence_is_explicit_and_unknown_is_not_zero() -> None:
    receipt = _fixture()
    receipt["operability"]["token_evidence_state"] = "partial"
    receipt["operability"]["total_tokens"] = 42
    receipt["operability"]["token_scope"] = "paired reader calls only"
    assert validate_reasoning_run_receipt(receipt)["status"] == "cross_field_valid"

    receipt["operability"]["token_evidence_state"] = "unknown"
    _assert_error(receipt, "unknown or not-applicable token evidence must use null total")


def test_authorization_snapshot_must_be_temporally_scoped() -> None:
    receipt = _fixture()
    receipt["authorization_snapshot"]["as_of_event_sequence"] += 1
    _assert_error(receipt, "authorization sequence must match")

    receipt = _fixture()
    receipt["authorization_snapshot"]["future_events_not_covered"] = [
        "reader_call"
    ]
    _assert_error(receipt, "must exclude reader_call and human_review")


def test_question_audiences_are_separate_and_human_surface_is_capped() -> None:
    receipt = _fixture()
    repeated = receipt["questions"]["human_product_review_questions"][0]
    receipt["questions"]["case_domain_unknowns"].append(repeated)
    _assert_error(receipt, "question categories must not overlap")

    receipt = _fixture()
    receipt["questions"]["human_product_review_questions"] = [
        "Question one?",
        "Question two?",
        "Question three?",
        "Question four?",
    ]
    _assert_error(receipt, "human_product_review_questions exceeds maximum 3")


def test_normalized_duplicate_claims_fail() -> None:
    receipt = _fixture()
    original = receipt["claim_boundary"]["supported"][0]
    receipt["claim_boundary"]["supported"].append(
        {
            "claim_id": "source-plan-preserved-copy",
            "text": "  " + original["text"].upper() + "  ",
            "basis_artifact_refs": ["conversation"],
        }
    )
    _assert_error(receipt, "claim_boundary.supported contains duplicate claims")


def test_empty_pressure_portfolio_remains_valid_to_preserve_true_stand_down() -> None:
    receipt = _fixture()
    receipt["pressure_accountability"] = []
    result = validate_reasoning_run_receipt(receipt)
    assert result["status"] == "cross_field_valid"


def test_non_use_disposition_cannot_claim_an_effect() -> None:
    receipt = _fixture()
    pressure = receipt["pressure_accountability"][0]
    pressure["consumer_disposition"] = "deferred"
    _assert_error(receipt, "non-use disposition must not claim an effect")


def test_required_non_claims_are_not_optional() -> None:
    receipt = _fixture()
    receipt["non_claims"] = receipt["non_claims"][:-1]
    _assert_error(receipt, "required non-claim ids are missing")


def test_contract_document_keeps_runtime_and_semantic_judgment_out() -> None:
    text = DOC_PATH.read_text(encoding="utf-8")
    assert "It does not judge whether the answer or decision is correct." in text
    assert "It allows an\nempty pressure list" in text
    assert "The deterministic validator cannot decide" in text or (
        "The validator does not read prose to decide which mental model is relevant."
        in text
    )
    assert "changing the live skill or runtime" in text
    assert "rewriting Case 10" in text
