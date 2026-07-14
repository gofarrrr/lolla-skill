from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from engine.system_b.r3_fresh_consumer import value_sha256
from engine.system_b.r3_reasoning_exclusion import inspect_reasoning_exclusion
from scripts.evals import build_r3_reasoning_exclusion_correction as builder


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("message", "status", "detail_count"),
    [
        ({}, "reasoning_absent", 0),
        ({"reasoning": None}, "reasoning_empty", 0),
        ({"reasoning": ""}, "reasoning_empty", 0),
        ({"reasoning": "   \n"}, "reasoning_empty", 0),
        ({"reasoning_content": None}, "reasoning_empty", 0),
        ({"reasoning_details": None}, "reasoning_empty", 0),
        ({"reasoning_details": []}, "reasoning_empty", 0),
        (
            {
                "reasoning_details": [
                    {
                        "type": "reasoning.text",
                        "format": "google-gemini-v1",
                        "index": 0,
                        "signature": "opaque",
                    }
                ]
            },
            "reasoning_metadata_only",
            1,
        ),
        (
            {
                "reasoning_details": [
                    {
                        "type": "reasoning.summary",
                        "id": "summary-1",
                        "format": "anthropic-claude-v1",
                        "index": 0,
                        "summary": " ",
                    },
                    {
                        "type": "reasoning.encrypted",
                        "id": None,
                        "format": "openai-responses-v1",
                        "index": 1,
                        "data": None,
                    },
                ]
            },
            "reasoning_metadata_only",
            2,
        ),
    ],
)
def test_absent_empty_and_metadata_only_shapes_pass(
    message: dict, status: str, detail_count: int
) -> None:
    inspection = inspect_reasoning_exclusion(message)

    assert inspection.status == status
    assert inspection.exclusion_satisfied is True
    assert inspection.content_present is False
    assert inspection.malformed is False
    assert inspection.detail_count == detail_count
    assert inspection.metadata_only is (status == "reasoning_metadata_only")


@pytest.mark.parametrize(
    ("message", "expected_location"),
    [
        ({"reasoning": "private chain"}, "/message/reasoning"),
        (
            {"reasoning_content": "private chain"},
            "/message/reasoning_content",
        ),
        (
            {
                "reasoning_details": [
                    {"type": "reasoning.text", "text": "private chain"}
                ]
            },
            "/message/reasoning_details/0/text",
        ),
        (
            {
                "reasoning_details": [
                    {"type": "reasoning.summary", "summary": "short chain"}
                ]
            },
            "/message/reasoning_details/0/summary",
        ),
        (
            {
                "reasoning_details": [
                    {"type": "reasoning.encrypted", "data": "encrypted"}
                ]
            },
            "/message/reasoning_details/0/data",
        ),
        (
            {
                "reasoning_details": [
                    {"type": "reasoning.text", "content": "compat-content"}
                ]
            },
            "/message/reasoning_details/0/content",
        ),
        (
            {
                "reasoning_details": [
                    {"type": "reasoning.text", "reasoning": "compat-reasoning"}
                ]
            },
            "/message/reasoning_details/0/reasoning",
        ),
    ],
)
def test_every_known_content_surface_blocks(
    message: dict, expected_location: str
) -> None:
    inspection = inspect_reasoning_exclusion(message)

    assert inspection.status == "reasoning_content_present"
    assert inspection.exclusion_satisfied is False
    assert inspection.content_present is True
    assert inspection.metadata_only is False
    assert expected_location in inspection.content_locations


@pytest.mark.parametrize(
    ("message", "expected_location"),
    [
        ({"reasoning": []}, "/message/reasoning"),
        ({"reasoning_details": {}}, "/message/reasoning_details"),
        ({"reasoning_details": "opaque"}, "/message/reasoning_details"),
        ({"reasoning_details": ["opaque"]}, "/message/reasoning_details/0"),
        ({"reasoning_details": [{}]}, "/message/reasoning_details/0/type"),
        (
            {"reasoning_details": [{"signature": "opaque"}]},
            "/message/reasoning_details/0/type",
        ),
        (
            {"reasoning_details": [{"type": "reasoning.future"}]},
            "/message/reasoning_details/0/type",
        ),
        (
            {
                "reasoning_details": [
                    {"type": "reasoning.text", "future_blob": "opaque"}
                ]
            },
            "/message/reasoning_details/0/future_blob",
        ),
        (
            {"reasoning_details": [{"type": "reasoning.text", "text": []}]},
            "/message/reasoning_details/0/text",
        ),
        (
            {"reasoning_details": [{"type": "reasoning.text", "index": -1}]},
            "/message/reasoning_details/0/index",
        ),
        (
            {"reasoning_details": [{"type": "reasoning.text", "index": True}]},
            "/message/reasoning_details/0/index",
        ),
        (
            {
                "reasoning_details": [
                    {"type": "reasoning.text", "signature": {"opaque": True}}
                ]
            },
            "/message/reasoning_details/0/signature",
        ),
    ],
)
def test_malformed_and_unknown_shapes_fail_closed(
    message: dict, expected_location: str
) -> None:
    inspection = inspect_reasoning_exclusion(message)

    assert inspection.status == "reasoning_shape_malformed"
    assert inspection.exclusion_satisfied is False
    assert inspection.malformed is True
    assert expected_location in inspection.malformed_locations


def test_mixed_metadata_and_content_blocks_without_leaking_values() -> None:
    secret = "PRIVATE_REASONING_MUST_NOT_SURVIVE_9173"
    message = {
        "reasoning_details": [
            {
                "type": "reasoning.text",
                "format": "google-gemini-v1",
                "index": 0,
                "signature": "opaque-signature",
            },
            {
                "type": "reasoning.summary",
                "format": "anthropic-claude-v1",
                "index": 1,
                "summary": secret,
            },
        ]
    }

    inspection = inspect_reasoning_exclusion(message)
    serialized = json.dumps(inspection.to_dict())

    assert inspection.status == "reasoning_content_present"
    assert inspection.exclusion_satisfied is False
    assert inspection.detail_count == 2
    assert "/message/reasoning_details/1/summary" in inspection.content_locations
    assert secret not in serialized
    assert "opaque-signature" not in serialized
    assert inspection.to_dict()["provider_values_included"] is False


def test_content_and_malformed_conditions_are_both_preserved() -> None:
    inspection = inspect_reasoning_exclusion(
        {
            "reasoning_details": [
                {
                    "type": "reasoning.text",
                    "text": "returned reasoning",
                    "unknown": "future shape",
                }
            ]
        }
    )

    assert inspection.status == "reasoning_content_present"
    assert inspection.content_present is True
    assert inspection.malformed is True
    assert inspection.exclusion_satisfied is False


def test_checked_in_contract_and_result_preserve_historical_failure() -> None:
    contract = builder.validate_contract()
    result = builder.validate()
    call_result = json.loads(builder.CALL_RESULT.read_text(encoding="utf-8"))
    terminal = json.loads(builder.TERMINAL_RESULT.read_text(encoding="utf-8"))

    assert contract["frozen_evidence"] == builder.FROZEN_EVIDENCE
    assert contract["budget"]["provider_calls_authorized"] == 0
    assert contract["decision"] == builder.EXPECTED_DECISION
    assert call_result["mechanical_contract_valid"] is False
    assert call_result["reasoning_content_returned"] is True
    assert terminal["semantic_review_performed"] is False
    assert terminal["next_call_authorized"] is False
    assert result["provider_calls"] == 0
    assert result["provider_cost_usd"] == 0.0
    assert result["historical_result"]["historical_result_reclassified"] is False
    assert result["prospective_diagnostic"]["inspection"]["status"] == (
        "reasoning_metadata_only"
    )
    assert result["prospective_diagnostic"]["semantic_review_opened"] is False
    assert result["decision"]["paid_r3_status"] == "deferred"


def test_every_frozen_file_matches_the_immutable_contract() -> None:
    for relative, expected in builder.FROZEN_EVIDENCE.items():
        observed = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert observed == expected


def test_result_tampering_fails_even_with_recomputed_self_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    result = json.loads(builder.RESULT.read_text(encoding="utf-8"))
    result["prospective_diagnostic"]["semantic_review_opened"] = True
    result["result_sha256"] = value_sha256(
        {key: item for key, item in result.items() if key != "result_sha256"}
    )
    tampered = tmp_path / "validation-result.json"
    tampered.write_text(json.dumps(result), encoding="utf-8")
    monkeypatch.setattr(builder, "RESULT", tampered)

    with pytest.raises(
        builder.R3ReasoningCorrectionError,
        match="validation result boundary drifted",
    ):
        builder.validate()


def test_contract_tampering_fails_before_any_execution(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    contract = json.loads(builder.CONTRACT.read_text(encoding="utf-8"))
    contract["decision"]["paid_r3_status"] = "authorized"
    tampered = tmp_path / "contract.json"
    tampered.write_text(json.dumps(contract), encoding="utf-8")
    monkeypatch.setattr(builder, "CONTRACT", tampered)

    with pytest.raises(
        builder.R3ReasoningCorrectionError,
        match="prospective contract boundary drifted",
    ):
        builder.validate_contract()


def test_builder_has_no_provider_transport_path() -> None:
    source = Path(builder.__file__).read_text(encoding="utf-8")

    assert "urlopen" not in source
    assert "OPENROUTER_API_KEY" not in source
    assert "OPENAI_API_KEY" not in source
    assert "execute-pressure" not in source
