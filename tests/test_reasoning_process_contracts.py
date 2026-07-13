from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_contracts import (
    ASSESSMENT_STATUS,
    BOUNDED_VIEW_SCHEMA_VERSION,
    LEDGER_STATUS,
    PROCESS_ASSESSMENT_SCHEMA_VERSION,
    PROCESS_LEDGER_SCHEMA_VERSION,
    VIEW_STATUS,
    ReasoningProcessContractError,
    model_facing_schema,
    phase0_contract,
    schema_metrics,
    validate_bounded_view,
    validate_process_assessment,
    validate_process_ledger,
)


ROOT = Path(__file__).resolve().parents[1]
FROZEN_CONTRACT = ROOT / "docs/evals/reasoning-process-phase0-contract-v0.json"
FROZEN_VIEW_SCHEMA = (
    ROOT / "docs/evals/reasoning-process-bounded-view-provider-schema-v0.json"
)
FROZEN_ASSESSMENT_SCHEMA = (
    ROOT / "docs/evals/reasoning-process-assessment-provider-schema-v0.json"
)
SOURCE_SHA = "sha256:" + "a" * 64
LEDGER_SHA = "sha256:" + "b" * 64
PROMPT_SHA = "sha256:" + "c" * 64
SPAN_ID = "span-source-a"
OBSERVATION_ID = "observation-a"
VIEW_ID = "view-a"
VIEW_ITEM_ID = "view-item-a"


def _ledger() -> dict:
    return {
        "schema_version": PROCESS_LEDGER_SCHEMA_VERSION,
        "status": LEDGER_STATUS,
        "ledger_id": "ledger-a",
        "source": {
            "conversation_id": "conversation-a",
            "source_path": "fixtures/conversation-a.txt",
            "source_sha256": SOURCE_SHA,
            "message_count": 2,
            "authoritative_conversation_attached": True,
        },
        "observations": [
            {
                "observation_id": OBSERVATION_ID,
                "family": "position_and_decision_trajectory",
                "interpretation": "The user qualified the earlier direction.",
                "semantic_status": "supported",
                "source_span_ids": [SPAN_ID],
                "provenance": {
                    "producer_kind": "model",
                    "producer_id": "reader-a",
                    "call_id": "call-a",
                    "model": "model-a",
                    "prompt_sha256": PROMPT_SHA,
                },
                "state_history": [
                    {
                        "state": "proposed",
                        "reason": "returned by semantic reader",
                        "actor": "probabilistic_reader",
                    },
                    {
                        "state": "admitted",
                        "reason": "source identity and shape validated",
                        "actor": "deterministic_validator",
                    },
                ],
                "terminal_state": "admitted",
                "terminal_reason": "source identity and shape validated",
                "relations": [],
                "graph_routing_eligible": False,
            }
        ],
        "failures": [],
        "boundary": {
            "authoritative_conversation_referenced": True,
            "semantic_relevance_inferred_by_code": False,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
    }


def _view() -> dict:
    return {
        "schema_version": BOUNDED_VIEW_SCHEMA_VERSION,
        "status": VIEW_STATUS,
        "view_id": VIEW_ID,
        "view_kind": "position_and_decision_trajectory",
        "question": "How did the working position change?",
        "source_ledger_sha256": LEDGER_SHA,
        "input": {"ledger_observation_ids": [OBSERVATION_ID]},
        "items": [
            {
                "view_item_id": VIEW_ITEM_ID,
                "interpretation": "The position became conditional.",
                "status": "supported",
                "source_observation_ids": [OBSERVATION_ID],
                "source_span_ids": [SPAN_ID],
                "limitations": "This records the captured exchange only.",
            }
        ],
        "dispositions": [
            {
                "observation_id": OBSERVATION_ID,
                "disposition": "included",
                "authority": "probabilistic_reader",
                "reason": "The observation directly answers the view question.",
                "view_item_ids": [VIEW_ITEM_ID],
            }
        ],
        "budget": {
            "max_input_observations": 32,
            "max_input_utf8_bytes": 24000,
            "max_output_items": 12,
            "observed_input_observations": 1,
            "observed_input_utf8_bytes": 320,
            "observed_output_items": 1,
            "budget_exceeded": False,
        },
        "boundary": {
            "authoritative_source": False,
            "semantic_selection_performed_by_code": False,
            "omissions_recoverable_from_ledger": True,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
    }


def _assessment() -> dict:
    return {
        "schema_version": PROCESS_ASSESSMENT_SCHEMA_VERSION,
        "status": ASSESSMENT_STATUS,
        "assessment_id": "assessment-a",
        "source_ledger_sha256": LEDGER_SHA,
        "source_view_ids": [VIEW_ID],
        "observations": [
            {
                "assessment_observation_id": "assessment-observation-a",
                "dimension": "position_and_decision_trajectory",
                "status": "supported",
                "statement": "The captured process contains a qualification.",
                "source_view_item_ids": [VIEW_ITEM_ID],
                "source_observation_ids": [OBSERVATION_ID],
                "scope_limitation": "This does not establish whether the final position is correct.",
            },
            {
                "assessment_observation_id": "assessment-observation-b",
                "dimension": "lolla_pressure_disposition",
                "status": "not_observed",
                "statement": "No Lolla pressure disposition is present in the supplied views.",
                "source_view_item_ids": [],
                "source_observation_ids": [],
                "scope_limitation": "Absence in these views is not proof about material outside the captured run.",
            },
        ],
        "telemetry": {
            "model_calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "wall_time_ms": 0,
            "treated_as_quality_evidence": False,
        },
        "boundary": {
            "final_output_evaluated": False,
            "scalar_quality_score_included": False,
            "effort_score_included": False,
            "trust_score_included": False,
            "correctness_claimed": False,
        },
    }


def _assert_strict_object_shapes(value: object) -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            assert value.get("additionalProperties") is False
            assert value.get("required") == list(value.get("properties", {}))
            assert value.get("description")
        for child in value.values():
            _assert_strict_object_shapes(child)
    elif isinstance(value, list):
        for child in value:
            _assert_strict_object_shapes(child)


def test_frozen_phase0_snapshot_matches_code_and_forbids_calls() -> None:
    frozen = json.loads(FROZEN_CONTRACT.read_text(encoding="utf-8"))
    assert frozen == phase0_contract()
    assert frozen["provider_envelope"]["phase_0_to_2_calls"] == 0
    assert frozen["provider_envelope"]["paid_calls_authorized"] is False
    assert frozen["provider_envelope"]["automatic_retries"] == 0
    assert frozen["provider_envelope"]["response_healing"] is False
    assert frozen["provider_envelope"]["graph_calls"] == 0
    assert "not_final_memo_evaluation" in frozen["non_claims"]
    assert "not_a_trust_score" in frozen["non_claims"]


def test_model_facing_schemas_are_shallow_strict_described_and_score_free() -> None:
    gates = phase0_contract()["numeric_gates"]
    frozen_paths = {
        "bounded_view": FROZEN_VIEW_SCHEMA,
        "process_assessment": FROZEN_ASSESSMENT_SCHEMA,
    }
    for kind, frozen_path in frozen_paths.items():
        schema = model_facing_schema(kind)
        assert schema == json.loads(frozen_path.read_text(encoding="utf-8"))
        _assert_strict_object_shapes(schema)
        metrics = schema_metrics(schema)
        assert metrics["depth"] <= gates["max_provider_schema_depth"]
        assert metrics["bytes"] <= gates["max_provider_schema_bytes"]
        encoded = json.dumps(schema).lower()
        assert "final_answer" not in encoded
        assert "recommendation" not in encoded
        assert "quality_score" not in encoded
        assert "trust_score" not in encoded


def test_valid_ledger_preserves_source_lineage_without_semantic_claims() -> None:
    result = validate_process_ledger(
        _ledger(), known_span_ids={SPAN_ID}, expected_source_sha256=SOURCE_SHA
    )
    assert result["source_custody_validated"] is True
    assert result["semantic_correctness_validated"] is False
    assert result["final_output_evaluated"] is False
    assert result["runtime_integration_authorized"] is False


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda payload: payload["observations"][0].update(
                {"source_span_ids": ["span-unknown"]}
            ),
            "unknown span",
        ),
        (
            lambda payload: payload["observations"][0].update(
                {"graph_routing_eligible": True}
            ),
            "graph_routing_eligible must be false",
        ),
        (
            lambda payload: payload["boundary"].update(
                {"final_output_evaluated": True}
            ),
            "final_output_evaluated must be false",
        ),
        (
            lambda payload: payload["observations"][0].update(
                {
                    "relations": [
                        {
                            "relation_type": "revises",
                            "target_observation_id": OBSERVATION_ID,
                            "authority": "deterministic_validator",
                        }
                    ]
                }
            ),
            "authority must be semantic",
        ),
        (
            lambda payload: payload["observations"][0].update(
                {
                    "relations": [
                        {
                            "relation_type": "revises",
                            "target_observation_id": OBSERVATION_ID,
                            "authority": "probabilistic_reader",
                        }
                    ]
                }
            ),
            "cannot target itself",
        ),
    ],
)
def test_ledger_rejects_custody_and_product_boundary_breaches(mutate, message) -> None:
    payload = copy.deepcopy(_ledger())
    mutate(payload)
    with pytest.raises(ReasoningProcessContractError, match=message):
        validate_process_ledger(payload, known_span_ids={SPAN_ID})


def test_valid_bounded_view_accounts_for_every_input_without_becoming_source() -> None:
    result = validate_bounded_view(
        _view(),
        known_ledger_observation_ids={OBSERVATION_ID},
        known_span_ids={SPAN_ID},
        expected_ledger_sha256=LEDGER_SHA,
    )
    assert result["exact_input_accounting"] is True
    assert result["semantic_correctness_validated"] is False
    assert result["final_output_evaluated"] is False


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload.update({"dispositions": []}), "exactly once"),
        (
            lambda payload: payload["dispositions"][0].update(
                {"authority": "deterministic_validator"}
            ),
            "semantic disposition requires",
        ),
        (
            lambda payload: payload["budget"].update(
                {"max_input_observations": 0, "budget_exceeded": True}
            ),
            "exceeds its frozen",
        ),
        (
            lambda payload: payload["budget"].update(
                {"max_input_observations": 33}
            ),
            "exceeds the Phase-0 hard ceiling",
        ),
        (
            lambda payload: payload["boundary"].update(
                {"quality_score_included": True}
            ),
            "quality_score_included must be false",
        ),
    ],
)
def test_bounded_view_rejects_hidden_loss_gating_bloat_and_score_claims(
    mutate, message
) -> None:
    payload = copy.deepcopy(_view())
    mutate(payload)
    with pytest.raises(ReasoningProcessContractError, match=message):
        validate_bounded_view(
            payload,
            known_ledger_observation_ids={OBSERVATION_ID},
            known_span_ids={SPAN_ID},
        )


def test_valid_process_assessment_is_an_evidence_vector_not_a_score() -> None:
    result = validate_process_assessment(
        _assessment(),
        known_view_ids={VIEW_ID},
        known_view_item_ids={VIEW_ITEM_ID},
        known_observation_ids={OBSERVATION_ID},
        expected_ledger_sha256=LEDGER_SHA,
    )
    assert result["lineage_validated"] is True
    assert result["semantic_correctness_validated"] is False
    assert result["quality_or_trust_score_emitted"] is False


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda payload: payload["observations"][0].update(
                {"source_view_item_ids": []}
            ),
            "requires both lineage levels",
        ),
        (
            lambda payload: payload["telemetry"].update(
                {"treated_as_quality_evidence": True}
            ),
            "must not be treated as quality evidence",
        ),
        (
            lambda payload: payload["boundary"].update(
                {"trust_score_included": True}
            ),
            "trust_score_included must be false",
        ),
        (
            lambda payload: payload["observations"][1].update(
                {"source_observation_ids": [OBSERVATION_ID]}
            ),
            "not_observed must not invent",
        ),
    ],
)
def test_assessment_rejects_ungrounded_or_certifying_claims(mutate, message) -> None:
    payload = copy.deepcopy(_assessment())
    mutate(payload)
    with pytest.raises(ReasoningProcessContractError, match=message):
        validate_process_assessment(
            payload,
            known_view_ids={VIEW_ID},
            known_view_item_ids={VIEW_ITEM_ID},
            known_observation_ids={OBSERVATION_ID},
        )
