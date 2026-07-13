from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.conversation_state_fan_in import (
    ConversationStateFanInError,
    assemble_conversation_state_fan_in,
    build_reader_result,
)
from engine.system_b.r4_complementary_readers import (
    R4ComplementaryReaderError,
    build_relationship_packet_v1,
    build_relationship_prompts_v1,
    build_source_registry_v1,
    build_uncertainty_packet_v1,
    build_uncertainty_prompts_v1,
    canonical_json_bytes,
    compile_relationship_response_v1,
    compile_uncertainty_response_v1,
    existing_reader_results_v1,
    missing_complementary_reader_results_v1,
    planned_readers_v1,
    relationship_response_schema_v1,
    source_alias_catalog_v1,
    uncertainty_response_schema_v1,
)


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12"
TRANSFER = ROOT / "research/simulated-reliability-v1-transfer-2026-07-12/t1"
TARGET_PATH = ROOT / "docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json"
MODEL = "google/gemini-3.1-flash-lite"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _case(case_id: str) -> dict:
    wrapper_path = (
        CORPUS
        / "provider-free-role-input-preflight/transfer"
        / case_id
        / "position-wrapper.json"
    )
    source_path = CORPUS / "naturalized-transfer-sources" / f"{case_id}.txt"
    role_path = TRANSFER / f"{case_id}-primary" / "joined-role-records.json"
    wrapper = _load(wrapper_path)
    source_bytes = source_path.read_bytes()
    role_bytes = role_path.read_bytes()
    role = json.loads(role_bytes)
    source_registry = build_source_registry_v1(
        wrapper=wrapper, source_bytes=source_bytes
    )
    readers = planned_readers_v1(
        case_id=case_id,
        existing_producer_id="google/gemini-3.5-flash-20260519",
        complementary_producer_id=MODEL,
    )
    packet = build_uncertainty_packet_v1(
        wrapper=wrapper,
        source_bytes=source_bytes,
        role_portfolio=role,
        role_artifact_path=str(role_path.relative_to(ROOT)),
        role_artifact_bytes=role_bytes,
    )
    return {
        "case_id": case_id,
        "wrapper": wrapper,
        "source_path": source_path,
        "source_bytes": source_bytes,
        "source_registry": source_registry,
        "role_path": role_path,
        "role_bytes": role_bytes,
        "role": role,
        "readers": readers,
        "packet": packet,
        "alias_text": {
            row["alias"]: row["text"] for row in source_alias_catalog_v1(wrapper)
        },
    }


def _existing(case: dict) -> list[dict]:
    return existing_reader_results_v1(
        role_portfolio=case["role"],
        source_registry=case["source_registry"],
        planned_readers=case["readers"],
        role_artifact_path=str(case["role_path"].relative_to(ROOT)),
        role_artifact_bytes=case["role_bytes"],
    )


def _relationship_missing(case: dict) -> dict:
    return next(
        result
        for result in missing_complementary_reader_results_v1(
            planned_readers=case["readers"]
        )
        if result["surface"] == "cross_thread_relationship"
    )


def _assemble(
    case: dict,
    results: list[dict],
    artifacts: dict[str, bytes],
) -> dict:
    return assemble_conversation_state_fan_in(
        source_registry=case["source_registry"],
        planned_readers=case["readers"],
        reader_results=sorted(results, key=lambda item: item["reader_id"]),
        source_bytes=case["source_bytes"],
        artifact_bytes_by_path=artifacts,
    )


def _positive_uncertainty() -> dict:
    return {
        "reviews": [
            {
                "surface": "unresolved_matter",
                "outcome": "records_present",
                "records": [
                    {
                        "support": "supported",
                        "interpretation": "The two-ward pilot in the accessible-vehicle city does not establish transfer to the other settings.",
                        "evidence_ids": ["e019", "e032", "e048"],
                        "limitations": "The source does not report outcomes from the other cities.",
                    }
                ],
            },
            {
                "surface": "reopen_condition",
                "outcome": "records_present",
                "records": [
                    {
                        "support": "supported",
                        "interpretation": "Continuation requires a fresh staffing and privacy decision and should not inherit the pilot's temporary support automatically.",
                        "evidence_ids": ["e085", "e093", "e094", "e098"],
                        "limitations": "The exact steady-state staffing design remains unspecified.",
                    }
                ],
            },
        ],
        "global_limitations": "This read is confined to the supplied conversation.",
    }


def _quiet_uncertainty() -> dict:
    return {
        "reviews": [
            {
                "surface": "reopen_condition",
                "outcome": "no_supported_record_observed",
                "records": [],
            },
            {
                "surface": "unresolved_matter",
                "outcome": "no_supported_record_observed",
                "records": [],
            },
        ],
        "global_limitations": "The existing six-month review already operationalizes the visible uncertainty.",
    }


def _compile_uncertainty(case: dict, response: dict, path: str) -> tuple[dict, bytes]:
    raw = canonical_json_bytes(response)
    return (
        compile_uncertainty_response_v1(
            response=response,
            packet=case["packet"],
            source_registry=case["source_registry"],
            planned_readers=case["readers"],
            artifact_path=path,
            artifact_bytes=raw,
        ),
        raw,
    )


def _schema_depth(value: object, depth: int = 1) -> int:
    if isinstance(value, dict):
        return max([depth, *(_schema_depth(item, depth + 1) for item in value.values())])
    if isinstance(value, list):
        return max([depth, *(_schema_depth(item, depth + 1) for item in value)])
    return depth


def _assert_provider_schema_subset(value: object) -> None:
    allowed = {
        "type",
        "description",
        "properties",
        "required",
        "additionalProperties",
        "enum",
        "minItems",
        "maxItems",
        "items",
    }

    def walk(node: object, *, schema_node: bool) -> None:
        if isinstance(node, dict):
            if schema_node:
                assert set(node).issubset(allowed)
                if node.get("type") == "object":
                    assert node.get("additionalProperties") is False
            for key, item in node.items():
                if key == "properties":
                    for child in item.values():
                        walk(child, schema_node=True)
                elif key == "items":
                    walk(item, schema_node=True)
        elif isinstance(node, list):
            for item in node:
                walk(item, schema_node=False)

    walk(value, schema_node=True)


def test_schemas_are_small_shallow_strict_and_google_subset_only() -> None:
    uncertainty = uncertainty_response_schema_v1()
    relationship = relationship_response_schema_v1()
    assert len(canonical_json_bytes(uncertainty)) == 1653
    assert len(canonical_json_bytes(relationship)) == 1442
    assert _schema_depth(uncertainty) <= 14
    assert _schema_depth(relationship) <= 12
    _assert_provider_schema_subset(uncertainty)
    _assert_provider_schema_subset(relationship)


def test_full_source_packet_preserves_exact_aliases_and_keeps_gold_out_of_prompts() -> None:
    targets = _load(TARGET_PATH)
    for case_target in targets["cases"]:
        case = _case(case_target["case_id"])
        packet = case["packet"]
        prompts = build_uncertainty_prompts_v1(packet)
        assert packet["source"]["sha256"] == case_target["source"]["sha256"]
        assert len(packet["source"]["aliases"]) in {102, 113}
        assert packet["boundary"]["semantic_meaning_decided_by_model"] is True
        assert packet["boundary"]["keyword_or_chronology_gate"] is False
        prompt_text = prompts["system_prompt"] + prompts["user_prompt"]
        for target_text in case_target["frozen_source_first_target"].values():
            if isinstance(target_text, str):
                assert target_text not in prompt_text


def test_pre_call_fan_in_exposes_not_run_as_missing_not_semantic_zero() -> None:
    case = _case("v1-case02-discharge-transport")
    results = [
        *_existing(case),
        *missing_complementary_reader_results_v1(planned_readers=case["readers"]),
    ]
    fan_in = _assemble(
        case,
        results,
        {str(case["role_path"].relative_to(ROOT)): case["role_bytes"]},
    )
    states = {row["surface"]: row["state"] for row in fan_in["reader_results"]}
    assert states == {
        "starting_position": "complete",
        "current_position": "complete",
        "qualification": "completed_zero",
        "unresolved_matter": "missing",
        "reopen_condition": "missing",
        "cross_thread_relationship": "missing",
    }
    assert fan_in["boundary"]["completed_zero_treated_as_semantic_absence"] is False


def test_positive_path_compiles_separate_surfaces_then_exact_id_relationship() -> None:
    case = _case("v1-case02-discharge-transport")
    uncertainty_path = "research/r4-preflight/case02/fixture-uncertainty.json"
    compiled, uncertainty_raw = _compile_uncertainty(
        case, _positive_uncertainty(), uncertainty_path
    )
    pre_relationship = _assemble(
        case,
        [*_existing(case), *compiled["reader_results"], _relationship_missing(case)],
        {
            str(case["role_path"].relative_to(ROOT)): case["role_bytes"],
            uncertainty_path: uncertainty_raw,
        },
    )
    packet = build_relationship_packet_v1(
        fan_in=pre_relationship, source_text_by_alias=case["alias_text"]
    )
    prompts = build_relationship_prompts_v1(packet)
    assert packet["record_catalog"] == sorted(
        packet["record_catalog"], key=lambda item: item["record_id"]
    )
    assert compiled["record_ids"][0] in prompts["user_prompt"]
    current_id = next(
        row["record_id"]
        for row in packet["record_catalog"]
        if row["surface"] == "current_position"
    )
    unresolved_id = next(
        row["record_id"]
        for row in packet["record_catalog"]
        if row["surface"] == "unresolved_matter"
    )
    reopen_id = next(
        row["record_id"]
        for row in packet["record_catalog"]
        if row["surface"] == "reopen_condition"
    )
    relationship_response = {
        "outcome": "records_present",
        "records": [
            {
                "support": "supported",
                "related_record_ids": [current_id, unresolved_id, reopen_id],
                "relationship": "The bounded current pilot does not by itself resolve transfer, and continuation is the point at which those dependencies must be reconsidered.",
                "evidence_ids": ["e032", "e048", "e094", "e098"],
                "limitations": "This relationship does not predict pilot outcomes.",
            }
        ],
        "global_limitations": "Only exact admitted records were related.",
    }
    relationship_path = "research/r4-preflight/case02/fixture-relationship.json"
    relationship_raw = canonical_json_bytes(relationship_response)
    relationship = compile_relationship_response_v1(
        response=relationship_response,
        packet=packet,
        source_registry=case["source_registry"],
        planned_readers=case["readers"],
        artifact_path=relationship_path,
        artifact_bytes=relationship_raw,
    )
    final = _assemble(
        case,
        [*_existing(case), *compiled["reader_results"], relationship["reader_result"]],
        {
            str(case["role_path"].relative_to(ROOT)): case["role_bytes"],
            uncertainty_path: uncertainty_raw,
            relationship_path: relationship_raw,
        },
    )
    relation_record = relationship["reader_result"]["records"][0]
    assert relation_record["related_record_ids"] == sorted(
        [current_id, unresolved_id, reopen_id]
    )
    assert final["status"] == "conversation_state_fan_in_complete"
    assert final["fan_in"]["reader_state_counts"] == {
        "complete": 5,
        "completed_zero": 1,
        "partial": 0,
        "failed": 0,
        "missing": 0,
    }
    assert final["boundary"]["relationship_meaning_inferred_by_code"] is False


def test_restraint_path_preserves_four_completed_zero_results() -> None:
    case = _case("v1-case03-executive-hire")
    uncertainty_path = "research/r4-preflight/case03/fixture-uncertainty-zero.json"
    compiled, uncertainty_raw = _compile_uncertainty(
        case, _quiet_uncertainty(), uncertainty_path
    )
    pre_relationship = _assemble(
        case,
        [*_existing(case), *compiled["reader_results"], _relationship_missing(case)],
        {
            str(case["role_path"].relative_to(ROOT)): case["role_bytes"],
            uncertainty_path: uncertainty_raw,
        },
    )
    packet = build_relationship_packet_v1(
        fan_in=pre_relationship, source_text_by_alias=case["alias_text"]
    )
    assert {row["surface"] for row in packet["record_catalog"]} == {
        "starting_position",
        "current_position",
    }
    response = {
        "outcome": "no_supported_record_observed",
        "records": [],
        "global_limitations": "No complementary uncertainty record exists to relate.",
    }
    relationship_path = "research/r4-preflight/case03/fixture-relationship-zero.json"
    relationship_raw = canonical_json_bytes(response)
    relationship = compile_relationship_response_v1(
        response=response,
        packet=packet,
        source_registry=case["source_registry"],
        planned_readers=case["readers"],
        artifact_path=relationship_path,
        artifact_bytes=relationship_raw,
    )
    final = _assemble(
        case,
        [*_existing(case), *compiled["reader_results"], relationship["reader_result"]],
        {
            str(case["role_path"].relative_to(ROOT)): case["role_bytes"],
            uncertainty_path: uncertainty_raw,
            relationship_path: relationship_raw,
        },
    )
    assert final["fan_in"]["reader_state_counts"]["completed_zero"] == 4
    assert final["fan_in"]["total_record_count"] == 2
    assert final["status"] == "conversation_state_fan_in_complete"


def test_ambiguous_review_is_an_explicit_record_not_a_fabricated_zero() -> None:
    case = _case("v1-case02-discharge-transport")
    response = _quiet_uncertainty()
    response["reviews"][1] = {
        "surface": "unresolved_matter",
        "outcome": "ambiguous_review",
        "records": [
            {
                "support": "ambiguous",
                "interpretation": "The source may leave a transfer question open, but the endpoint meaning is not decisive.",
                "evidence_ids": ["e019", "e032"],
                "limitations": "No cross-city result is available.",
            }
        ],
    }
    compiled, _raw = _compile_uncertainty(
        case, response, "research/r4-preflight/case02/fixture-ambiguous.json"
    )
    unresolved = next(
        row for row in compiled["reader_results"] if row["surface"] == "unresolved_matter"
    )
    assert unresolved["state"] == "complete"
    assert unresolved["records"][0]["semantic_payload"]["review_outcome"] == "ambiguous_review"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("duplicate_surface", "invalid or duplicated"),
        ("quiet_with_record", "quiet outcome must be empty"),
        ("present_without_supported", "needs a supported record"),
        ("unknown_alias", "unknown identity"),
        ("extra_field", "fields do not match"),
    ],
)
def test_uncertainty_adversarial_outputs_fail_closed(mutation: str, message: str) -> None:
    case = _case("v1-case02-discharge-transport")
    response = _positive_uncertainty()
    if mutation == "duplicate_surface":
        response["reviews"][1]["surface"] = "unresolved_matter"
    elif mutation == "quiet_with_record":
        response["reviews"][0]["outcome"] = "no_supported_record_observed"
    elif mutation == "present_without_supported":
        response["reviews"][0]["records"][0]["support"] = "ambiguous"
    elif mutation == "unknown_alias":
        response["reviews"][0]["records"][0]["evidence_ids"] = ["e999"]
    elif mutation == "extra_field":
        response["reviews"][0]["records"][0]["score"] = 1
    with pytest.raises(R4ComplementaryReaderError, match=message):
        _compile_uncertainty(
            case, response, f"research/r4-preflight/case02/{mutation}.json"
        )


def test_relationship_unknown_or_duplicate_endpoint_fails_closed() -> None:
    case = _case("v1-case02-discharge-transport")
    compiled, raw = _compile_uncertainty(
        case,
        _positive_uncertainty(),
        "research/r4-preflight/case02/fixture-uncertainty.json",
    )
    fan_in = _assemble(
        case,
        [*_existing(case), *compiled["reader_results"], _relationship_missing(case)],
        {
            str(case["role_path"].relative_to(ROOT)): case["role_bytes"],
            "research/r4-preflight/case02/fixture-uncertainty.json": raw,
        },
    )
    packet = build_relationship_packet_v1(
        fan_in=fan_in, source_text_by_alias=case["alias_text"]
    )
    known = packet["record_catalog"][0]["record_id"]
    base = {
        "outcome": "records_present",
        "records": [
            {
                "support": "supported",
                "related_record_ids": [known, "unknown-record"],
                "relationship": "A claimed relationship.",
                "evidence_ids": ["e001"],
                "limitations": "",
            }
        ],
        "global_limitations": "",
    }
    for ids, message in (
        ([known, "unknown-record"], "unknown identity"),
        ([known, known], "is invalid"),
    ):
        response = copy.deepcopy(base)
        response["records"][0]["related_record_ids"] = ids
        raw_response = canonical_json_bytes(response)
        with pytest.raises(R4ComplementaryReaderError, match=message):
            compile_relationship_response_v1(
                response=response,
                packet=packet,
                source_registry=case["source_registry"],
                planned_readers=case["readers"],
                artifact_path="research/r4-preflight/case02/bad-relationship.json",
                artifact_bytes=raw_response,
            )


def test_fan_in_rejects_reader_artifact_drift_after_valid_compilation() -> None:
    case = _case("v1-case02-discharge-transport")
    path = "research/r4-preflight/case02/fixture-uncertainty.json"
    compiled, raw = _compile_uncertainty(case, _positive_uncertainty(), path)
    with pytest.raises(ConversationStateFanInError, match="artifact custody drifted"):
        _assemble(
            case,
            [*_existing(case), *compiled["reader_results"], _relationship_missing(case)],
            {
                str(case["role_path"].relative_to(ROOT)): case["role_bytes"],
                path: raw + b"drift",
            },
        )


def test_failed_relationship_dependency_is_not_rewritten_as_quiet() -> None:
    case = _case("v1-case03-executive-hire")
    relationship_reader = next(
        reader
        for reader in case["readers"]
        if reader["surface"] == "cross_thread_relationship"
    )
    failure_raw = b'{"status":"dependency_failed"}'
    failure = build_reader_result(
        reader=relationship_reader,
        state="failed",
        records=[],
        artifact_path="research/r4-preflight/case03/dependency-failure.json",
        artifact_bytes=failure_raw,
        issue_code="dependency_failed",
        issue_stage="relationship_packet_build",
        safe_detail="The uncertainty result did not admit a usable artifact.",
    )
    missing = missing_complementary_reader_results_v1(
        planned_readers=case["readers"]
    )
    uncertainty_missing = [
        row for row in missing if row["surface"] in {"unresolved_matter", "reopen_condition"}
    ]
    fan_in = _assemble(
        case,
        [*_existing(case), *uncertainty_missing, failure],
        {
            str(case["role_path"].relative_to(ROOT)): case["role_bytes"],
            "research/r4-preflight/case03/dependency-failure.json": failure_raw,
        },
    )
    assert fan_in["fan_in"]["reader_state_counts"]["failed"] == 1
    assert fan_in["fan_in"]["reader_state_counts"]["completed_zero"] == 1
    assert fan_in["status"] == "conversation_state_fan_in_partial"
