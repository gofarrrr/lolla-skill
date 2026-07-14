from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from engine.system_b.conversation_state_fan_in import build_source_registry
from engine.system_b.r4_complementary_readers import (
    RELATIONSHIP_PACKET_SCHEMA,
    UNCERTAINTY_PACKET_SCHEMA,
    canonical_json_bytes,
    compile_relationship_response_v1,
    compile_uncertainty_response_v1,
    planned_readers_v1,
)
from engine.system_b.r4_semantic_distinction import (
    SEMANTIC_DISTINCTION_PROMPT_CONTRACT,
    build_relationship_prompts_v2,
    build_uncertainty_prompts_v2,
    inspect_r4_reasoning_exclusion_v1,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = (
    ROOT / "tests/fixtures/r4_semantic_distinction/contract-fixtures-v1.json"
)
MODEL = "google/gemini-3.1-flash-lite"


def _load_fixtures() -> dict:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def _source_registry(case: dict) -> tuple[dict, bytes]:
    source_bytes = (
        "\n".join(row["text"] for row in case["source_evidence"]) + "\n"
    ).encode("utf-8")
    aliases = [
        {
            "alias": row["alias"],
            "span_id": f"span-{case['case_id']}-{index:02d}",
            "speaker": row["speaker"],
            "turn_index": row["turn_index"],
            "text_sha256": hashlib.sha256(row["text"].encode("utf-8")).hexdigest(),
        }
        for index, row in enumerate(case["source_evidence"], 1)
    ]
    return (
        build_source_registry(
            case_id=case["case_id"],
            source_path=f"development-fixtures/{case['case_id']}.txt",
            source_bytes=source_bytes,
            message_count=max(row["turn_index"] for row in case["source_evidence"]),
            aliases=aliases,
        ),
        source_bytes,
    )


def _readers(case_id: str) -> list[dict[str, str]]:
    return planned_readers_v1(
        case_id=case_id,
        existing_producer_id="human-authored-development-fixture",
        complementary_producer_id=MODEL,
    )


def _uncertainty_prompt_packet(case: dict) -> dict:
    return {
        "schema_version": UNCERTAINTY_PACKET_SCHEMA,
        "case_id": case["case_id"],
        "source": {
            "path": f"development-fixtures/{case['case_id']}.txt",
            "aliases": case["source_evidence"],
        },
        "prior_interpretation_context": {
            "authority": "fallible_prior_interpretation_not_source_truth",
            "records": [],
            "qualification_review": {
                "outcome": "no_material_qualification_observed",
                "evidence_ids": [case["source_evidence"][0]["alias"]],
                "interpretation": "Development fixture prior context.",
                "limitations": "Not provider output.",
            },
        },
    }


def _relationship_packet(case: dict) -> dict:
    return {
        "schema_version": RELATIONSHIP_PACKET_SCHEMA,
        "case_id": case["case_id"],
        "record_catalog": case["record_catalog"],
    }


def test_fixture_catalog_is_explicit_development_not_provider_evidence() -> None:
    fixtures = _load_fixtures()

    assert fixtures["status"] == (
        "human_authored_development_fixtures_not_provider_evidence"
    )
    assert fixtures["partition"] == "exposed_development_only"
    assert fixtures["provider_output"] is False
    assert fixtures["semantic_reliability_claim"] is False
    assert len(fixtures["uncertainty_cases"]) == 7
    assert len(fixtures["relationship_cases"]) == 2
    assert {row["category"] for row in fixtures["uncertainty_cases"]} == {
        "genuine_unresolved_matter",
        "genuine_reopen_condition",
        "earlier_gap_resolved_in_final_state",
        "adopted_condition_precedent",
        "existing_pause_and_no_renew_safeguard",
        "scheduled_review_with_benchmarks",
        "ambiguous_endpoint_state",
    }


@pytest.mark.parametrize("case", _load_fixtures()["uncertainty_cases"])
def test_uncertainty_development_gold_passes_existing_custody_compiler(
    case: dict,
) -> None:
    source_registry, _source_bytes = _source_registry(case)
    response = case["expected_response"]
    raw = canonical_json_bytes(response)

    compiled = compile_uncertainty_response_v1(
        response=response,
        packet={
            "schema_version": UNCERTAINTY_PACKET_SCHEMA,
            "case_id": case["case_id"],
        },
        source_registry=source_registry,
        planned_readers=_readers(case["case_id"]),
        artifact_path=f"development-fixtures/{case['case_id']}-expected.json",
        artifact_bytes=raw,
    )

    assert compiled["status"] == "paired_uncertainty_custody_complete"
    assert compiled["boundary"]["semantic_correctness_inferred_by_code"] is False
    assert compiled["boundary"]["keyword_or_chronology_gate"] is False


@pytest.mark.parametrize("case", _load_fixtures()["relationship_cases"])
def test_relationship_development_gold_passes_exact_id_compiler(case: dict) -> None:
    source_registry, _source_bytes = _source_registry(case)
    response = case["expected_response"]
    raw = canonical_json_bytes(response)

    compiled = compile_relationship_response_v1(
        response=response,
        packet=_relationship_packet(case),
        source_registry=source_registry,
        planned_readers=_readers(case["case_id"]),
        artifact_path=f"development-fixtures/{case['case_id']}-expected.json",
        artifact_bytes=raw,
    )

    assert compiled["status"] == "exact_id_relationship_custody_complete"
    assert compiled["boundary"]["relationship_meaning_inferred_by_code"] is False
    if response["outcome"] == "no_supported_record_observed":
        assert compiled["reader_result"]["state"] == "completed_zero"


def test_uncertainty_v2_prompt_puts_long_context_before_final_task() -> None:
    case = _load_fixtures()["uncertainty_cases"][0]
    prompts = build_uncertainty_prompts_v2(_uncertainty_prompt_packet(case))
    user = prompts["user_prompt"]
    system = prompts["system_prompt"]

    assert prompts["prompt_contract_version"] == SEMANTIC_DISTINCTION_PROMPT_CONTRACT
    assert user.index("<authoritative_source>") < user.index("<task>")
    assert user.index("<fallible_prior_interpretation_context>") < user.index(
        "<task>"
    )
    assert user.rstrip().endswith("</task>")
    assert "Do not infer resolution merely from turn order" in system
    assert "condition precedent" in system
    assert "scheduled review" in system
    assert "ambiguous_review" in system


def test_uncertainty_v2_prompt_contains_positive_and_negative_contrasts() -> None:
    case = _load_fixtures()["uncertainty_cases"][0]
    system = build_uncertainty_prompts_v2(_uncertainty_prompt_packet(case))[
        "system_prompt"
    ]

    assert "not an unresolved matter" in system
    assert "not a newly discovered reopen condition" in system
    assert "not a separate reopen condition" in system
    assert "transfer or generalization question" in system
    assert "steady-state burden" in system
    assert "outside facts are forbidden" in system


def test_relationship_v2_prompt_prefers_zero_over_endpoint_restatement() -> None:
    case = _load_fixtures()["relationship_cases"][1]
    prompts = build_relationship_prompts_v2(_relationship_packet(case))
    system = prompts["system_prompt"]

    assert prompts["prompt_contract_version"] == SEMANTIC_DISTINCTION_PROMPT_CONTRACT
    assert "Co-occurrence is not a relationship" in system
    assert "Do not paraphrase endpoints" in system
    assert "may be false positives" in system
    assert "complete with zero" in system
    assert prompts["user_prompt"].index("<exact_id_record_packet>") < prompts[
        "user_prompt"
    ].index("<task>")


@pytest.mark.parametrize(
    ("message", "status", "satisfied"),
    [
        ({}, "reasoning_absent", True),
        (
            {
                "reasoning_details": [
                    {
                        "type": "reasoning.text",
                        "format": "google-gemini-v1",
                        "index": 0,
                        "signature": "opaque-secret-signature",
                    }
                ]
            },
            "reasoning_metadata_only",
            True,
        ),
        ({"reasoning": "private chain"}, "reasoning_content_present", False),
        (
            {"reasoning_details": [{"type": "reasoning.future"}]},
            "reasoning_shape_malformed",
            False,
        ),
    ],
)
def test_future_r4_reasoning_custody_reuses_strict_r3_validator(
    message: dict, status: str, satisfied: bool
) -> None:
    result = inspect_r4_reasoning_exclusion_v1(message)
    serialized = json.dumps(result)

    assert result["status"] == status
    assert result["exclusion_satisfied"] is satisfied
    assert result["provider_values_included"] is False
    assert result["historical_r4_result_reclassified"] is False
    assert "opaque-secret-signature" not in serialized
    assert "private chain" not in serialized


def test_v2_is_additive_and_frozen_v1_files_are_unchanged() -> None:
    expected = {
        "engine/system_b/r4_complementary_readers.py": (
            "9253290093e62f62a9adbf8902ccf010ac4d4417c345222e4756e771496bf777"
        ),
        "scripts/evals/run_r4_complementary_reader_experiment.py": (
            "ec91fe1d4cfafa0366e1a0eeec1aef39a01f167297de11257f8889fcc30f4f2d"
        ),
    }
    observed = {
        relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        for relative in expected
    }

    assert observed == expected
