from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path

from engine.system_b.conversation_state_candidates import (
    ConstraintExtraction,
    EvidenceRef,
    PositionExtraction,
    ThreadExtraction,
    build_micro_contract,
    build_source_catalog,
    parse_typed,
    provider_schema,
    provider_compatibility_report,
    resolve_evidence,
    schema_metrics,
    validate_extraction_state,
)


ROOT = Path(__file__).resolve().parents[1]
CASE03 = (
    ROOT
    / "research/designed-ambiguous-pool-v1-2026-07-10/capture-ready-cases/amb1-case03-creative-partnership.txt"
)


def _catalog():
    return build_source_catalog(
        source_text=CASE03.read_text(encoding="utf-8"),
        source_path=str(CASE03.relative_to(ROOT)),
    )


def _span(turn_index: int, speaker: str, contains: str):
    return next(
        span
        for span in _catalog().spans
        if span.turn_index == turn_index
        and span.speaker == speaker
        and contains in span.text
    )


def test_source_catalog_is_stable_complete_and_exact() -> None:
    first = _catalog()
    second = _catalog()
    assert first == second
    assert first.message_count == 14
    assert len({span.span_id for span in first.spans}) == len(first.spans)
    assert sum(span.kind == "turn" for span in first.spans) == 14
    for span in first.spans:
        turn = next(
            item
            for item in first.spans
            if item.turn_id == span.turn_id and item.kind == "turn"
        )
        assert turn.text[span.char_start : span.char_end] == span.text


def test_evidence_ref_rejects_noncontiguous_quote_join() -> None:
    catalog = _catalog()
    span = _span(3, "user", "participant approved a cut")
    joined = (
        "the participant approved a cut three months ago. "
        "She also told us she did not want to supervise every edit."
    )
    _resolved, issues = resolve_evidence(
        EvidenceRef(span_id=span.span_id, excerpt=joined), catalog=catalog
    )
    assert [issue.code for issue in issues] == ["source_excerpt_not_exact"]


def test_evidence_ref_resolves_exact_excerpt_to_speaker_and_turn() -> None:
    catalog = _catalog()
    quote = "Early on we said major structural decisions would be mutual."
    span = _span(4, "user", quote)
    resolved, issues = resolve_evidence(
        EvidenceRef(span_id=span.span_id, excerpt=quote), catalog=catalog
    )
    assert issues == []
    assert resolved is not None
    assert resolved.speaker == "user"
    assert resolved.turn_index == 4


def test_provider_schemas_are_generated_from_typed_fields_with_descriptions() -> None:
    classes = {
        "positions": PositionExtraction,
        "threads": ThreadExtraction,
        "constraints": ConstraintExtraction,
    }
    for kind, cls in classes.items():
        schema = provider_schema(kind, provider="openai")
        assert list(schema["properties"]) == [item.name for item in fields(cls)]
        assert schema["required"] == [item.name for item in fields(cls)]
        assert schema["additionalProperties"] is False
        assert all(
            definition.get("description")
            for definition in schema["properties"].values()
        )
        encoded = json.dumps(schema)
        assert '"const"' not in encoded
        assert schema_metrics(schema)["bytes"] < 5000


def test_gemini_projection_uses_nullable_type_array_not_const() -> None:
    schema = provider_schema("threads", provider="gemini")
    nullable = schema["$defs"]["ThreadCandidate"]["properties"]["superseded_by"]
    assert nullable["type"] == ["string", "null"]
    assert "anyOf" not in nullable


def test_provider_projection_reuses_nested_types_by_reference() -> None:
    schema = provider_schema("positions", provider="gemini")
    assert schema["properties"]["positions"]["items"]["$ref"] == (
        "#/$defs/PositionCandidate"
    )
    assert schema["$defs"]["ContributionCandidate"]["properties"]["evidence"][
        "$ref"
    ] == "#/$defs/EvidenceRef"


def test_typed_position_parser_accepts_supported_candidate() -> None:
    user_span = _span(7, "user", "My provisional plan")
    assistant_span = _span(7, "assistant", "Listening before deciding")
    payload = {
        "status": "supported",
        "decision_summary": {
            "text": "Review the revised cut before deciding.",
            "evidence_mode": "multi_turn_derivation",
            "evidence": [
                {"span_id": user_span.span_id, "excerpt": "My provisional plan is to hear Jonah's revised cut before deciding about postponement."}
            ],
        },
        "positions": [
            {
                "text": "Review the cut before deciding and do not treat credit as proof of mutual process.",
                "ownership": "joint",
                "state": "conditional",
                "evidence_mode": "multi_turn_derivation",
                "contributions": [
                    {
                        "role": "developed",
                        "evidence": {"span_id": user_span.span_id, "excerpt": "My provisional plan is to hear Jonah's revised cut before deciding about postponement."},
                    },
                    {
                        "role": "qualified",
                        "evidence": {"span_id": assistant_span.span_id, "excerpt": "you may need to avoid using a harmonious credit line as evidence that the underlying process felt mutual"},
                    },
                ],
            }
        ],
    }
    parsed, issues = parse_typed(PositionExtraction, payload)
    assert issues == []
    assert parsed is not None
    assert validate_extraction_state(parsed) == []
    assert parsed.positions[0].ownership == "joint"


def test_explicit_not_found_is_valid_and_does_not_force_candidates() -> None:
    payload = {"status": "not_found", "decision_summary": None, "positions": []}
    parsed, issues = parse_typed(PositionExtraction, payload)
    assert issues == []
    assert parsed is not None
    assert validate_extraction_state(parsed) == []


def test_mixed_constraint_is_rejected_to_preserve_atomic_source_strength() -> None:
    span = _span(4, "user", "major structural decisions would be mutual")
    payload = {
        "status": "supported",
        "constraints": [
            {
                "text": "Mutual authority and availability history.",
                "state": "active",
                "claim_mode": "mixed",
                "evidence_mode": "exact_span",
                "evidence": [
                    {
                        "span_id": span.span_id,
                        "excerpt": "Early on we said major structural decisions would be mutual.",
                    }
                ],
            }
        ],
    }
    _parsed, issues = parse_typed(ConstraintExtraction, payload)
    assert "enum_value_invalid" in {issue.code for issue in issues}


def test_three_micro_contracts_are_narrow_complete_and_provider_free() -> None:
    catalog = _catalog()
    contracts = {
        kind: build_micro_contract(kind, catalog=catalog, provider="gemini")
        for kind in ("positions", "threads", "constraints")
    }
    assert "Do not extract threads or constraints" in contracts["positions"][
        "system_prompt"
    ]
    assert "Do not extract positions or constraints" in contracts["threads"][
        "system_prompt"
    ]
    assert "Do not extract positions or threads" in contracts["constraints"][
        "system_prompt"
    ]
    for contract in contracts.values():
        assert contract["provider_calls"] == 0
        assert "not_found" in contract["system_prompt"]
        assert "Never join non-contiguous text" in contract["system_prompt"]
        assert "SOURCE SPAN CATALOG" in contract["user_prompt"]
        assert "TYPED OUTPUT SCHEMA" in contract["user_prompt"]
        assert contract["schema_metrics"]["depth"] <= 8


def test_gemini_compatibility_report_is_explicit_not_semantic_proof() -> None:
    report = provider_compatibility_report(provider="gemini")
    assert report["all_compatible"] is True
    assert report["provider_calls"] == 0
    assert len(report["rows"]) == 3
    assert all(row["unsupported_keywords"] == [] for row in report["rows"])
    assert "schema_compatibility_is_not_semantic_quality" in report["non_claims"]
