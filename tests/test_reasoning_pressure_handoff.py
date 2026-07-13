from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_pressure_handoff import (
    ReasoningPressureHandoffValidationError,
    build_reasoning_pressure_disposition_skeleton,
    validate_reasoning_pressure_disposition_ledger,
    validate_reasoning_pressure_handoff,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = (
    REPO_ROOT
    / "tests/fixtures/core_semantic_validation/case_01_enterprise_logo_beta/reasoning-pressure-handoff.example.json"
)


def _example() -> dict[str, object]:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def _source_ids(payload: dict[str, object]) -> set[str]:
    ids: set[str] = set()
    for key in ("pressure_items", "preservation_items"):
        for item in payload[key]:
            ids.update(item["source_event_ids"])
    return ids


def _graph_refs(payload: dict[str, object]) -> set[str]:
    return {
        ref
        for item in payload["pressure_items"]
        for ref in item["graph_trace_refs"]
    }


def _validate(payload: dict[str, object]) -> dict[str, object]:
    return validate_reasoning_pressure_handoff(
        payload,
        known_source_event_ids=_source_ids(_example()),
        known_graph_trace_refs=_graph_refs(_example()),
        expected_conversation_sha256=payload["source"]["conversation_sha256"],
        expected_reasoning_pattern_packet_sha256=payload["lineage"][
            "reasoning_pattern_packet_sha256"
        ],
        expected_graph_version=payload["lineage"]["graph_version"],
        expected_graph_trace_artifact_sha256=payload["lineage"][
            "graph_trace_artifact_sha256"
        ],
        expected_routing_projection_sha256=payload["lineage"][
            "routing_projection_sha256"
        ],
    )


def test_example_is_valid_for_shadow_evaluation_only() -> None:
    report = _validate(_example())
    assert report["status"] == "valid_for_shadow_evaluation_only"
    assert report["pressure_item_count"] == 3
    assert report["preservation_item_count"] == 2
    assert report["model_calls"] == 0
    assert report["semantic_relevance_validated"] is False
    assert report["answer_quality_validated"] is False
    assert report["runtime_integration_authorized"] is False


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda p: p["pressure_items"].append(copy.deepcopy(p["pressure_items"][0])),
            "pressure_items must not exceed 4",
        ),
        (
            lambda p: p["pressure_items"][0]["source_event_ids"].append("missing.event"),
            "not present in the custodied reference set",
        ),
        (
            lambda p: p["pressure_items"][0]["graph_trace_refs"].append("missing.route"),
            "not present in the custodied reference set",
        ),
        (
            lambda p: p["boundary"].update({"quality_score_included": True}),
            "boundary.quality_score_included must be false",
        ),
        (
            lambda p: p["non_claims"].remove("not_graph_integration_authority"),
            "non_claims is missing not_graph_integration_authority",
        ),
    ],
)
def test_invalid_handoff_is_rejected(mutation, message: str) -> None:
    payload = _example()
    if message == "pressure_items must not exceed 4":
        mutation(payload)
        mutation(payload)
    else:
        mutation(payload)
    with pytest.raises(ReasoningPressureHandoffValidationError, match=message):
        _validate(payload)


def test_lineage_mismatch_is_rejected() -> None:
    payload = _example()
    with pytest.raises(
        ReasoningPressureHandoffValidationError,
        match="conversation_sha256 does not match",
    ):
        validate_reasoning_pressure_handoff(
            payload,
            known_source_event_ids=_source_ids(payload),
            known_graph_trace_refs=_graph_refs(payload),
            expected_conversation_sha256="sha256:" + "0" * 64,
        )


def test_validator_does_not_apply_keyword_semantics() -> None:
    payload = _example()
    payload["pressure_items"][0]["challenge"] = (
        "This prose deliberately contains no domain keyword or mental-model label."
    )
    report = _validate(payload)
    assert report["semantic_relevance_validated"] is False


def _completed_disposition_ledger() -> dict[str, object]:
    handoff = _example()
    ledger = build_reasoning_pressure_disposition_skeleton(
        handoff,
        handoff_sha256="sha256:" + "a" * 64,
    )
    ledger["status"] = "completed"
    for item in ledger["items"]:
        item.update(
            {
                "disposition": "rejected",
                "strongest_plausible_application": "Test the strongest case.",
                "why": "The condition is not established.",
                "visible_effect": "",
                "private_guardrail": "",
                "risk_if_forced": "It would manufacture a conclusion.",
                "risk_if_ignored": "A valid challenge could be missed.",
            }
        )
    return ledger


def test_disposition_ledger_preserves_every_pressure_id_exactly() -> None:
    handoff = _example()
    ledger = _completed_disposition_ledger()
    report = validate_reasoning_pressure_disposition_ledger(
        ledger,
        handoff=handoff,
        expected_handoff_sha256="sha256:" + "a" * 64,
    )
    assert [item["pressure_id"] for item in ledger["items"]] == [
        item["pressure_id"] for item in handoff["pressure_items"]
    ]
    assert report["status"] == "structurally_valid"
    assert report["exact_pressure_id_coverage"] is True
    assert report["semantic_effect_review_status"] == "pending"
    assert report["semantic_effect_consistency_inferred_by_code"] is False


def test_disposition_ledger_rejects_renamed_missing_and_inconsistent_effect_claims() -> None:
    handoff = _example()
    ledger = _completed_disposition_ledger()
    ledger["items"][0]["pressure_id"] = "renamed-pressure"
    ledger["items"].pop()
    ledger["items"][0].update(
        {
            "disposition": "private_guardrail",
            "visible_effect": "Changed the public answer.",
            "private_guardrail": "Keep this private.",
        }
    )
    with pytest.raises(
        ReasoningPressureHandoffValidationError,
        match="copy every handoff pressure_id exactly once",
    ) as exc:
        validate_reasoning_pressure_disposition_ledger(
            ledger,
            handoff=handoff,
            expected_handoff_sha256="sha256:" + "a" * 64,
        )
    assert "must not claim visible_effect" in str(exc.value)


def test_disposition_ledger_records_independent_effect_review_without_inferring_it() -> None:
    handoff = _example()
    ledger = _completed_disposition_ledger()
    ledger["semantic_effect_review"] = {
        "status": "accepted",
        "reviewer": "reviewer-001",
        "reviewed_output_sha256": "sha256:" + "b" * 64,
        "findings": ["Claimed effects match the reviewed output."],
    }
    report = validate_reasoning_pressure_disposition_ledger(
        ledger,
        handoff=handoff,
        expected_handoff_sha256="sha256:" + "a" * 64,
    )
    assert report["semantic_effect_review_status"] == "accepted"
    assert report["semantic_effect_consistency_inferred_by_code"] is False
