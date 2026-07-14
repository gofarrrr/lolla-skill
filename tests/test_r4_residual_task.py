from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from engine.system_b.conversation_state_fan_in import build_source_registry
from engine.system_b.r4_complementary_readers import (
    canonical_json_bytes,
    planned_readers_v1,
    uncertainty_response_schema_v1,
    value_sha256,
)
from engine.system_b.r4_residual_task import (
    RESIDUAL_PROVIDER_SURFACES,
    RESIDUAL_SURFACE_TO_CANONICAL_ROLE,
    RESIDUAL_TASK_PROMPT_CONTRACT,
    build_residual_prompts_v1,
    compile_residual_response_v1,
    map_residual_response_to_canonical_v1,
    residual_response_schema_v1,
)


ROOT = Path(__file__).resolve().parents[1]
CASE_01_PACKET = ROOT / (
    "research/lolla-r4-semantic-distinction-contract-2026-07-14/cases/"
    "v1-case01-flood-infrastructure/uncertainty-packet.json"
)
CASE_01_REGISTRY = CASE_01_PACKET.with_name("source-registry.json")
HISTORICAL_FIXTURES = ROOT / (
    "tests/fixtures/r4_semantic_distinction/contract-fixtures-v1.json"
)
RESIDUAL_FIXTURES = ROOT / "tests/fixtures/r4_residual_task/contract-fixtures-v1.json"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _shape_only(value: object) -> object:
    """Remove provider wording while retaining every structural constraint."""

    if isinstance(value, dict):
        return {
            key: _shape_only(item)
            for key, item in value.items()
            if key != "description"
        }
    if isinstance(value, list):
        if value in (
            ["unresolved_matter", "reopen_condition"],
            list(RESIDUAL_PROVIDER_SURFACES),
        ):
            return ["surface_one", "surface_two"]
        return [_shape_only(item) for item in value]
    return value


def test_provider_contract_is_residual_only_with_unchanged_wire_shape() -> None:
    packet = _load(CASE_01_PACKET)
    prompts = build_residual_prompts_v1(packet)
    schema = residual_response_schema_v1()
    provider_visible = "\n".join(
        (
            prompts["system_prompt"],
            prompts["user_prompt"],
            json.dumps(schema, sort_keys=True),
        )
    )

    assert prompts["prompt_contract_version"] == RESIDUAL_TASK_PROMPT_CONTRACT
    assert RESIDUAL_PROVIDER_SURFACES == (
        "residual_decision_gap",
        "residual_reconsideration_dependency",
    )
    assert RESIDUAL_SURFACE_TO_CANONICAL_ROLE == {
        "residual_decision_gap": "unresolved_matter",
        "residual_reconsideration_dependency": "reopen_condition",
    }
    assert "unresolved_matter" not in provider_visible
    assert "reopen_condition" not in provider_visible
    assert "residual_decision_gap" in provider_visible
    assert "residual_reconsideration_dependency" in provider_visible
    assert _shape_only(schema) == _shape_only(uncertainty_response_schema_v1())

    source = canonical_json_bytes(packet["source"]).decode("utf-8")
    prior = canonical_json_bytes(packet["prior_interpretation_context"]).decode(
        "utf-8"
    )
    user = prompts["user_prompt"]
    assert user.count(source) == 1
    assert user.count(prior) == 1
    assert user.index(source) < user.index(prior) < user.index("<task>")
    assert user.rstrip().endswith("</task>")

    system = prompts["system_prompt"]
    for required in (
        "residual discovery",
        "Pending does not equal residual",
        "Deferred does not equal unowned",
        "Omitted implementation detail is not affirmative evidence of absence",
        "exact source aliases",
        "no_supported_record_observed",
        "ambiguous_review",
    ):
        assert required in system


def test_schema_builder_does_not_mutate_the_historical_schema() -> None:
    historical_before = uncertainty_response_schema_v1()
    expected = copy.deepcopy(historical_before)

    residual_response_schema_v1()

    assert uncertainty_response_schema_v1() == expected


def _readers_for(case_id: str) -> list[dict[str, str]]:
    return planned_readers_v1(
        case_id=case_id,
        existing_producer_id="frozen-existing-reader",
        complementary_producer_id="prospective-provider",
    )


def _readers() -> list[dict[str, str]]:
    return _readers_for("v1-case01-flood-infrastructure")


def _quiet_review(surface: str) -> dict:
    return {
        "surface": surface,
        "outcome": "no_supported_record_observed",
        "records": [],
    }


def test_declared_mapping_changes_only_surface_values() -> None:
    response = {
        "reviews": [
            {
                "surface": "residual_decision_gap",
                "outcome": "records_present",
                "records": [
                    {
                        "support": "supported",
                        "interpretation": (
                            "Recurring operating funding and ownership remain outside "
                            "the adopted installation safeguards."
                        ),
                        "evidence_ids": ["e005", "e078", "e099", "e103"],
                        "limitations": "The source does not name a recurring budget owner.",
                    }
                ],
            },
            _quiet_review("residual_reconsideration_dependency"),
        ],
        "global_limitations": "Exposed local expectation; not provider output.",
    }
    original = copy.deepcopy(response)

    mapped = map_residual_response_to_canonical_v1(response)

    assert response == original
    assert mapped["reviews"][0]["surface"] == "unresolved_matter"
    assert mapped["reviews"][1]["surface"] == "reopen_condition"
    for index in range(2):
        assert mapped["reviews"][index]["outcome"] == original["reviews"][index][
            "outcome"
        ]
        assert mapped["reviews"][index]["records"] == original["reviews"][index][
            "records"
        ]
    assert mapped["global_limitations"] == original["global_limitations"]


def test_zero_and_ambiguity_compile_as_separate_existing_canonical_roles() -> None:
    packet = _load(CASE_01_PACKET)
    registry = _load(CASE_01_REGISTRY)
    zero = {
        "reviews": [
            _quiet_review("residual_decision_gap"),
            _quiet_review("residual_reconsideration_dependency"),
        ],
        "global_limitations": "No distinct residual remains.",
    }
    ambiguous = {
        "reviews": [
            {
                "surface": "residual_decision_gap",
                "outcome": "ambiguous_review",
                "records": [
                    {
                        "support": "ambiguous",
                        "interpretation": (
                            "A material operating owner may remain outside the current "
                            "machinery, but the source does not establish that absence."
                        ),
                        "evidence_ids": ["e099", "e103"],
                        "limitations": "Omission alone does not establish absence.",
                    }
                ],
            },
            _quiet_review("residual_reconsideration_dependency"),
        ],
        "global_limitations": "The material remainder is plausible but unestablished.",
    }

    compiled_zero = compile_residual_response_v1(
        response=zero,
        packet=packet,
        source_registry=registry,
        planned_readers=_readers(),
        artifact_path="local/zero.json",
        artifact_bytes=canonical_json_bytes(zero),
    )
    compiled_ambiguous = compile_residual_response_v1(
        response=ambiguous,
        packet=packet,
        source_registry=registry,
        planned_readers=_readers(),
        artifact_path="local/ambiguous.json",
        artifact_bytes=canonical_json_bytes(ambiguous),
    )

    zero_results = {row["surface"]: row for row in compiled_zero["reader_results"]}
    ambiguous_results = {
        row["surface"]: row for row in compiled_ambiguous["reader_results"]
    }
    assert set(zero_results) == {"unresolved_matter", "reopen_condition"}
    assert all(row["state"] == "completed_zero" for row in zero_results.values())
    assert ambiguous_results["unresolved_matter"]["state"] == "complete"
    assert ambiguous_results["reopen_condition"]["state"] == "completed_zero"
    assert compiled_zero["boundary"]["provider_surface_values_mapped"] is True
    assert compiled_zero["boundary"]["mapping_inspected_free_text"] is False


def _fixture_registry(case: dict) -> dict:
    source_bytes = (
        "\n".join(row["text"] for row in case["source_evidence"]) + "\n"
    ).encode("utf-8")
    return build_source_registry(
        case_id=case["case_id"],
        source_path=f"development-fixtures/{case['case_id']}.txt",
        source_bytes=source_bytes,
        message_count=max(row["turn_index"] for row in case["source_evidence"]),
        aliases=[
            {
                "alias": row["alias"],
                "span_id": f"span-{case['case_id']}-{index:02d}",
                "speaker": row["speaker"],
                "turn_index": row["turn_index"],
                "text_sha256": hashlib.sha256(row["text"].encode("utf-8")).hexdigest(),
            }
            for index, row in enumerate(case["source_evidence"], 1)
        ],
    )


def test_additive_catalog_reuses_all_nine_historical_fixtures() -> None:
    historical = _load(HISTORICAL_FIXTURES)
    residual = _load(RESIDUAL_FIXTURES)
    reuse = residual["historical_fixture_reuse"]

    assert residual["schema_version"] == "lolla.r4_residual_task_fixture_catalog.v1"
    assert residual["partition"] == "exposed_development_only"
    assert residual["provider_output"] is False
    assert residual["provider_calls"] == 0
    assert residual["provider_cost_usd"] == 0.0
    assert residual["model_semantic_validation"] is False
    assert reuse["path"] == str(HISTORICAL_FIXTURES.relative_to(ROOT))
    assert reuse["sha256"] == hashlib.sha256(HISTORICAL_FIXTURES.read_bytes()).hexdigest()
    assert [row["case_id"] for row in reuse["uncertainty_cases"]] == [
        row["case_id"] for row in historical["uncertainty_cases"]
    ]
    assert [row["case_id"] for row in reuse["relationship_cases"]] == [
        row["case_id"] for row in historical["relationship_cases"]
    ]
    assert all(
        row["relationship_contract_changed"] is False
        for row in reuse["relationship_cases"]
    )

    by_id = {row["case_id"]: row for row in historical["uncertainty_cases"]}
    projection = reuse["canonical_to_provider_surface_projection"]
    for reference in reuse["uncertainty_cases"]:
        case = by_id[reference["case_id"]]
        response = copy.deepcopy(case["expected_response"])
        for review in response["reviews"]:
            review["surface"] = projection[review["surface"]]
        compiled = compile_residual_response_v1(
            response=response,
            packet={
                "schema_version": "lolla.r4_complementary_uncertainty_packet.v1",
                "case_id": case["case_id"],
            },
            source_registry=_fixture_registry(case),
            planned_readers=_readers_for(case["case_id"]),
            artifact_path=f"development-fixtures/{case['case_id']}-residual.json",
            artifact_bytes=canonical_json_bytes(response),
        )
        assert compiled["status"] == "paired_uncertainty_custody_complete"

    historical_relationships = {
        row["case_id"]: row for row in historical["relationship_cases"]
    }
    for reference in reuse["relationship_cases"]:
        assert reference["historical_case_sha256"] == value_sha256(
            historical_relationships[reference["case_id"]]
        )


def test_exposed_case04_is_zero_and_case01_preserves_only_operating_residual() -> None:
    catalog = _load(RESIDUAL_FIXTURES)
    exposed = {
        row["case_id"]: row for row in catalog["exposed_case_expectations"]
    }
    assert set(exposed) == {
        "v1-case01-flood-infrastructure",
        "v1-case04-component-sourcing",
    }

    case01 = exposed["v1-case01-flood-infrastructure"]
    case01_response = case01["expected_response"]
    gap, reconsideration = case01_response["reviews"]
    assert gap["surface"] == "residual_decision_gap"
    assert gap["outcome"] == "records_present"
    assert len(gap["records"]) == 1
    assert set(gap["records"][0]["evidence_ids"]).issuperset(
        {"e005", "e078", "e099", "e103"}
    )
    assert reconsideration == _quiet_review(
        "residual_reconsideration_dependency"
    )

    case04 = exposed["v1-case04-component-sourcing"]
    assert case04["expectation_role"] == "primary_false_positive_restraint_defect"
    assert case04["expected_response"]["reviews"] == [
        _quiet_review("residual_decision_gap"),
        _quiet_review("residual_reconsideration_dependency"),
    ]

    for case in exposed.values():
        packet = _load(ROOT / case["packet_path"])
        registry = _load(ROOT / case["source_registry_path"])
        response = case["expected_response"]
        compiled = compile_residual_response_v1(
            response=response,
            packet=packet,
            source_registry=registry,
            planned_readers=_readers_for(case["case_id"]),
            artifact_path=f"local/{case['case_id']}-expected.json",
            artifact_bytes=canonical_json_bytes(response),
        )
        results = {row["surface"]: row for row in compiled["reader_results"]}
        if case["case_id"] == "v1-case04-component-sourcing":
            assert all(row["state"] == "completed_zero" for row in results.values())
        else:
            assert results["unresolved_matter"]["state"] == "complete"
            assert results["reopen_condition"]["state"] == "completed_zero"
