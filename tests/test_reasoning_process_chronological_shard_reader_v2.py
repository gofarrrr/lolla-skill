from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.conversation_state_candidates import build_source_catalog
from engine.system_b.reasoning_process_chronological_shard_reader import (
    build_shard_prompts,
    shard_response_schema,
)
from engine.system_b.reasoning_process_chronological_shard_reader_v2 import (
    build_shard_prompts_v2,
    compile_shard_response_recordwise_v2,
    shard_response_schema_v2,
    validate_shard_record_v2,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
from scripts.evals.run_reasoning_process_role_explicit_v2_position_probe import (
    validate_authorization as validate_position_probe_authorization,
    validate_contract as validate_position_probe_contract,
)

ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = ROOT / "research/reasoning-process-chronological-shard-role-explicit-v2-2026-07-12"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _wrapper(case_id: str, view: str, shard: str) -> dict:
    return _load(
        ROOT
        / "research/reasoning-process-chronological-shards-2026-07-11/cases"
        / case_id
        / view
        / shard
    )


def _alias_text(wrapper: dict) -> dict[str, str]:
    source_path = wrapper["packet"]["source"]["source_path"]
    source_text = (ROOT / source_path).read_text(encoding="utf-8")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    by_span = {span.span_id: span.text for span in catalog.spans if span.kind == "sentence"}
    return {
        item["alias"]: by_span[item["span_id"]]
        for item in [*wrapper["focal_alias_map"], *wrapper["context_alias_map"]]
    }


def _joined(record: dict, field: str, texts: dict[str, str]) -> str:
    return " ".join(texts[alias] for alias in record[field])


def test_v2_role_schemas_remove_ambiguous_generic_interpretation() -> None:
    position = shard_response_schema_v2("position_and_decision_trajectory")["properties"]["records"]["items"]["properties"]
    assert "interpretation" not in position
    assert {
        "starting_position_interpretation",
        "current_position_interpretation",
        "qualification_interpretation",
        "trajectory_interpretation",
    }.issubset(position)
    uncertainty = shard_response_schema_v2("uncertainty_and_unresolved_state")["properties"]["records"]["items"]["properties"]
    assert "interpretation" not in uncertainty
    assert {
        "unresolved_matter_interpretation",
        "preservation_or_reopen_interpretation",
        "relationship_interpretation",
    }.issubset(uncertainty)
    challenge = shard_response_schema_v2("challenge_and_revision_response")["properties"]["records"]["items"]["properties"]
    assert "interpretation" not in challenge
    assert {
        "prior_frame_interpretation",
        "challenge_interpretation",
        "response_interpretation",
        "revision_interpretation",
        "relationship_interpretation",
    }.issubset(challenge)


def test_evidence_contract_is_exactly_unchanged() -> None:
    wrapper = _wrapper(
        "amb1-case01-product-scope", "evidence_and_assumption_discipline", "shard-01.json"
    )
    assert shard_response_schema_v2("evidence_and_assumption_discipline") == shard_response_schema(
        "evidence_and_assumption_discipline"
    )
    assert build_shard_prompts_v2(wrapper) == build_shard_prompts(wrapper)


def test_all_twenty_reviewed_fixtures_compile_under_v2() -> None:
    report = _load(V2_ROOT / "report.json")
    assert report["summary"]["protected_fixture_count"] == 20
    assert report["summary"]["protected_admitted_record_count"] == 20
    assert report["summary"]["protected_quarantined_record_count"] == 0
    assert report["summary"]["evidence_schema_unchanged"] is True
    assert report["summary"]["evidence_prompt_unchanged"] is True
    assert report["decision"]["provider_free_role_contract_gate"] == "pass"
    for case in report["cases"]:
        for artifact in case["artifacts"]:
            if artifact["protected_fixture_path"]:
                fixture = _load(ROOT / artifact["protected_fixture_path"])
                assert fixture["compiled"]["shard_terminal_disposition"] == "compiled"


def test_position_v2_rejects_the_observed_missing_current_semantics() -> None:
    wrapper = _wrapper(
        "amb1-case05-family-archive", "position_and_decision_trajectory", "shard-01.json"
    )
    legacy = _load(
        ROOT
        / "research/reasoning-process-chronological-shard-family-batch-run-2026-07-11/calls"
        / "shard-family-batch-amb1-case05-family-archive-position_and_decision_trajectory.json"
    )["candidate_payload"]["records"][0]
    record = {
        "status": legacy["status"],
        "limitations": legacy["limitations"],
        "starting_position_interpretation": legacy["interpretation"],
        "starting_state_evidence_ids": legacy["starting_state_evidence_ids"],
        "current_position_interpretation": "",
        "current_position_evidence_ids": legacy["current_position_evidence_ids"],
        "qualification_interpretation": "The decision rule remains unresolved.",
        "qualification_evidence_ids": legacy["qualification_evidence_ids"],
        "trajectory_interpretation": "The position changed.",
        "trajectory_type": legacy["trajectory_type"],
    }
    with pytest.raises(ViewSpecificInterfaceError, match="current_position_interpretation"):
        validate_shard_record_v2(record, wrapper=wrapper)


def test_position_starting_text_and_evidence_must_move_together() -> None:
    fixture = _load(
        V2_ROOT
        / "protected-fixtures/amb1-case05-family-archive/position_and_decision_trajectory.json"
    )
    wrapper = _wrapper(
        "amb1-case05-family-archive", "position_and_decision_trajectory", "shard-01.json"
    )
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["starting_state_evidence_ids"] = []
    with pytest.raises(ViewSpecificInterfaceError, match="empty or present together"):
        validate_shard_record_v2(record, wrapper=wrapper)


def test_uncertainty_v2_requires_both_role_meanings_in_every_record() -> None:
    fixture = _load(
        V2_ROOT
        / "protected-fixtures/amb1-case05-family-archive/uncertainty_and_unresolved_state.json"
    )
    wrapper = _wrapper(
        "amb1-case05-family-archive", "uncertainty_and_unresolved_state", "shard-03.json"
    )
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["preservation_or_reopen_interpretation"] = ""
    with pytest.raises(ViewSpecificInterfaceError, match="preservation_or_reopen_interpretation"):
        validate_shard_record_v2(record, wrapper=wrapper)


def test_uncertainty_conceptual_split_remains_semantic_not_deterministic() -> None:
    wrapper = _wrapper(
        "amb1-case05-family-archive", "uncertainty_and_unresolved_state", "shard-03.json"
    )
    texts = _alias_text(wrapper)
    legacy_records = _load(
        ROOT
        / "research/reasoning-process-chronological-shard-family-batch-run-2026-07-11/calls"
        / "shard-family-batch-amb1-case05-family-archive-uncertainty_and_unresolved_state.json"
    )["candidate_payload"]["records"]
    projected = []
    for legacy in legacy_records:
        projected.append(
            {
                "status": legacy["status"],
                "limitations": legacy["limitations"],
                "unresolved_matter_interpretation": _joined(
                    legacy, "unresolved_evidence_ids", texts
                ),
                "unresolved_evidence_ids": legacy["unresolved_evidence_ids"],
                "preservation_or_reopen_interpretation": _joined(
                    legacy, "preservation_or_reopen_evidence_ids", texts
                ),
                "preservation_or_reopen_evidence_ids": legacy[
                    "preservation_or_reopen_evidence_ids"
                ],
                "relationship_interpretation": legacy["interpretation"],
            }
        )
    compiled = compile_shard_response_recordwise_v2(
        response={
            "status": "mixed",
            "records": projected,
            "global_limitations": "Conceptual split remains a semantic review question.",
        },
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="no_deterministic_semantic_merge",
        record_identity="uncertainty-split",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    assert len(compiled["observations"]) == 2
    assert compiled["boundary"]["semantic_role_correctness_inferred_by_code"] is False


def test_challenge_v2_exposes_but_does_not_deterministically_gate_semantic_inversion() -> None:
    wrapper = _wrapper(
        "amb1-case05-family-archive", "challenge_and_revision_response", "shard-01.json"
    )
    legacy = _load(
        ROOT
        / "research/reasoning-process-chronological-shard-family-batch-run-2026-07-11/calls"
        / "shard-family-batch-amb1-case05-family-archive-challenge_and_revision_response.json"
    )["candidate_payload"]["records"][1]
    texts = _alias_text(wrapper)
    inverted = {
        "status": legacy["status"],
        "limitations": legacy["limitations"],
        "prior_frame_interpretation": _joined(
            legacy, "prior_claim_or_frame_evidence_ids", texts
        ),
        "prior_claim_or_frame_evidence_ids": legacy[
            "prior_claim_or_frame_evidence_ids"
        ],
        "challenge_interpretation": _joined(legacy, "challenge_evidence_ids", texts),
        "challenge_evidence_ids": legacy["challenge_evidence_ids"],
        "response_interpretation": _joined(legacy, "response_evidence_ids", texts),
        "response_evidence_ids": legacy["response_evidence_ids"],
        "revision_interpretation": "",
        "revision_evidence_ids": [],
        "relationship_interpretation": legacy["interpretation"],
        "challenge_type": legacy["challenge_type"],
        "response_type": legacy["response_type"],
    }
    validated = validate_shard_record_v2(inverted, wrapper=wrapper)
    assert "Tomas says" in validated["role_interpretations"]["prior_frame_interpretation"]
    assert "Mara does not want" in validated["role_interpretations"]["challenge_interpretation"]
    compiled = compile_shard_response_recordwise_v2(
        response={
            "status": "supported",
            "records": [inverted],
            "global_limitations": "Semantic inversion remains source-reviewable.",
        },
        wrapper=wrapper,
        producer_kind="adversarial_fixture",
        producer_id="no_brittle_temporal_gate",
        record_identity="challenge-inversion",
    )
    assert compiled["shard_terminal_disposition"] == "compiled"
    assert compiled["boundary"]["semantic_role_correctness_inferred_by_code"] is False


def test_challenge_response_text_and_evidence_must_move_together() -> None:
    fixture = _load(
        V2_ROOT
        / "protected-fixtures/amb1-case05-family-archive/challenge_and_revision_response.json"
    )
    wrapper = _wrapper(
        "amb1-case05-family-archive", "challenge_and_revision_response", "shard-01.json"
    )
    record = copy.deepcopy(fixture["response"]["records"][0])
    record["response_interpretation"] = ""
    with pytest.raises(ViewSpecificInterfaceError, match="empty or present together"):
        validate_shard_record_v2(record, wrapper=wrapper)


def test_v2_record_level_custody_preserves_valid_sibling() -> None:
    fixture = _load(
        V2_ROOT
        / "protected-fixtures/amb1-case05-family-archive/position_and_decision_trajectory.json"
    )
    wrapper = _wrapper(
        "amb1-case05-family-archive", "position_and_decision_trajectory", "shard-01.json"
    )
    valid = fixture["response"]["records"][0]
    invalid = copy.deepcopy(valid)
    invalid["current_position_interpretation"] = ""
    compiled = compile_shard_response_recordwise_v2(
        response={
            "status": "supported",
            "records": [valid, invalid],
            "global_limitations": "Record custody fixture.",
        },
        wrapper=wrapper,
        producer_kind="fixture",
        producer_id="recordwise-v2",
        record_identity="v2-siblings",
    )
    assert [item["terminal_state"] for item in compiled["records"]] == [
        "admitted",
        "quarantined",
    ]
    assert len(compiled["observations"]) == 1
    assert compiled["boundary"]["display_interpretation_mechanically_formatted"] is True


def test_role_explicit_position_probe_contract_is_frozen_after_local_gates() -> None:
    directory = ROOT / "research/reasoning-process-role-explicit-v2-position-probe-2026-07-12"
    contract_path = directory / "contract.json"
    contract = _load(contract_path)
    result = validate_position_probe_contract(contract, contract_path)
    assert result["status"] == "role_explicit_v2_position_probe_contract_valid"
    assert result["provider_calls_made"] == 0
    validate_position_probe_authorization(
        _load(directory / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )
    assert contract["boundary"]["uncertainty_or_challenge_calls_authorized"] is False
    assert contract["boundary"]["full_case_calls_authorized"] is False


def test_role_explicit_position_probe_preserves_partial_result_and_stop_line() -> None:
    directory = ROOT / "research/reasoning-process-role-explicit-v2-position-probe-2026-07-12"
    result = _load(directory / "result.json")
    call = result["call"]
    assert call["operational_status"] == "ok"
    assert call["typed_status"] == "admitted"
    assert call["admitted_record_count"] == 1
    assert call["quarantined_record_count"] == 0
    review = _load(directory / "source-review.json")
    assert review["decision"]["role_explicit_relationship_representation"] == "pass"
    assert review["decision"]["frozen_probe_success_gate"] == "fail_source_strength_inflation"
    assert review["aggregate"]["required_role_interpretations_present"] == "4_of_4"
    assert review["aggregate"]["source_review_source_strength_inflation_count"] == 1
    assert review["decision"]["same_case_prompt_repair_or_retry_authorized"] is False
    assert review["decision"]["uncertainty_or_challenge_probe_authorized"] is False
    assert review["decision"]["full_case_calls_authorized"] is False
