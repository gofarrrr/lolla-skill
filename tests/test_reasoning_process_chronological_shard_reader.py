from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_chronological_shard_reader import (
    build_shard_prompts,
    compile_shard_response_recordwise,
    shard_response_schema,
    validate_shard_record,
)
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
from scripts.evals.run_reasoning_process_chronological_shard_probe import validate as validate_probe
from scripts.evals.build_reasoning_process_chronological_shard_family_batch import validate as validate_family_batch
from scripts.evals.run_reasoning_process_chronological_shard_family_batch import validate_authorization as validate_family_authorization

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "research/reasoning-process-chronological-shards-2026-07-11/protected-target-review.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _packet(case_id: str, view_kind: str) -> dict:
    review = _load(REVIEW)
    case = next(item for item in review["cases"] if item["case_id"] == case_id)
    target = next(item for item in case["targets"] if item["view_kind"] == view_kind)
    return _load(ROOT / target["matching_shard_paths"][0])


def _protected_response(case_id: str, view_kind: str) -> dict:
    if view_kind in {"position_and_decision_trajectory", "challenge_and_revision_response"}:
        response = _load(
            ROOT
            / "research/reasoning-process-view-specific-v2-2026-07-11/fixtures"
            / case_id
            / f"{view_kind}.json"
        )["response"]
    else:
        response = _load(
            ROOT
            / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
            / case_id
            / view_kind
            / "protected-fixture-response.json"
        )
    projected = copy.deepcopy(response)
    projected.pop("park_unselected_auxiliary_observations")
    for record in projected["records"]:
        record.pop("auxiliary_observation_ids")
    return projected


def test_shard_schemas_remove_auxiliary_and_mechanical_model_jobs() -> None:
    for view in (
        "position_and_decision_trajectory",
        "evidence_and_assumption_discipline",
        "uncertainty_and_unresolved_state",
        "challenge_and_revision_response",
    ):
        schema = shard_response_schema(view)
        assert set(schema["properties"]) == {"status", "records", "global_limitations"}
        record_fields = schema["properties"]["records"]["items"]["properties"]
        assert "auxiliary_observation_ids" not in record_fields
        assert schema["properties"]["records"]["maxItems"] == 2


def test_all_protected_family_records_validate_in_their_colocated_shards() -> None:
    for case_id in (
        "amb1-case01-product-scope",
        "amb1-case02-nonprofit-scale",
        "amb1-case03-creative-partnership",
        "amb1-case04-research-tool-release",
        "amb1-case05-family-archive",
    ):
        for view in (
            "position_and_decision_trajectory",
            "evidence_and_assumption_discipline",
            "uncertainty_and_unresolved_state",
            "challenge_and_revision_response",
        ):
            wrapper = _packet(case_id, view)
            response = _protected_response(case_id, view)
            assert len(response["records"]) == 1
            validated = validate_shard_record(response["records"][0], wrapper=wrapper)
            assert set(validated["source_span_ids"])


def test_future_prompt_puts_context_before_final_contract_and_question() -> None:
    wrapper = _packet("amb1-case05-family-archive", "evidence_and_assumption_discipline")
    prompt = build_shard_prompts(wrapper)["user_prompt"]
    assert prompt.startswith("Chronological shard packet:\n")
    assert prompt.rfind("Relationship contract:") > prompt.find("annotated_sentence_text")
    assert prompt.rfind("Question:") > prompt.rfind("Relationship contract:")


def test_challenge_prior_context_is_role_limited() -> None:
    report = _load(ROOT / "research/reasoning-process-chronological-shards-2026-07-11/report.json")
    case = next(item for item in report["cases"] if item["case_id"] == "amb1-case05-family-archive")
    artifact = next(
        item
        for item in case["artifacts"]
        if item["view_kind"] == "challenge_and_revision_response"
        and item["focal_turn_indices"] == [4, 5]
    )
    wrapper = _load(ROOT / artifact["path"])
    context_alias = wrapper["packet"]["prior_context"]["evidence_aliases"][0]
    focal = wrapper["packet"]["focal_region"]["evidence_aliases"]
    record = {
        "interpretation": "A focal challenge responds to the prior visible frame.",
        "status": "supported",
        "limitations": "Provider-free role-boundary fixture.",
        "prior_claim_or_frame_evidence_ids": [context_alias],
        "challenge_evidence_ids": [focal[0]],
        "response_evidence_ids": [focal[1]],
        "revision_evidence_ids": [],
        "challenge_type": "correction",
        "response_type": "acknowledge",
    }
    validate_shard_record(record, wrapper=wrapper)
    invalid = copy.deepcopy(record)
    invalid["challenge_evidence_ids"] = [context_alias]
    with pytest.raises(ViewSpecificInterfaceError, match="role-forbidden"):
        validate_shard_record(invalid, wrapper=wrapper)


def test_record_level_custody_preserves_valid_sibling() -> None:
    wrapper = _packet("amb1-case05-family-archive", "evidence_and_assumption_discipline")
    valid = _protected_response("amb1-case05-family-archive", "evidence_and_assumption_discipline")["records"][0]
    invalid = copy.deepcopy(valid)
    invalid["claim_or_input_evidence_ids"] = ["e999"]
    compiled = compile_shard_response_recordwise(
        response={"status": "supported", "records": [valid, invalid], "global_limitations": "Fixture."},
        wrapper=wrapper,
        producer_kind="fixture",
        producer_id="provider-free",
        record_identity="sibling-custody",
    )
    assert compiled["shard_terminal_disposition"] == "partially_compiled"
    assert [item["terminal_state"] for item in compiled["records"]] == ["admitted", "quarantined"]
    assert len(compiled["observations"]) == 1


def test_smallest_probe_contract_and_authorization_are_frozen() -> None:
    directory = ROOT / "research/reasoning-process-chronological-shard-probe-2026-07-11"
    contract_path = directory / "contract.json"
    result = validate_probe(
        _load(contract_path),
        contract_path,
        _load(directory / "authorization.json"),
    )
    assert result == {
        "status": "chronological_shard_probe_contract_valid",
        "provider_calls_made": 0,
    }


def test_representative_family_batch_contract_and_authorization_are_frozen() -> None:
    directory = ROOT / "research/reasoning-process-chronological-shard-family-batch-2026-07-11"
    contract_path = directory / "contract.json"
    contract = _load(contract_path)
    assert validate_family_batch(contract) == {
        "status": "family_batch_contract_valid",
        "job_count": 4,
        "provider_calls_made": 0,
    }
    validate_family_authorization(
        _load(directory / "authorization.json"),
        contract=contract,
        contract_path=contract_path,
    )


def test_representative_family_batch_stops_full_case_scale_up() -> None:
    review = _load(
        ROOT
        / "research/reasoning-process-chronological-shard-family-batch-run-2026-07-11/source-review.json"
    )
    assert review["decision"]["representative_family_batch_gate"] == "fail"
    assert review["decision"]["full_nineteen_call_case_authorized"] is False
    assert review["aggregate"]["protected_relationships_supported"] == 2
    assert review["aggregate"]["protected_relationships_partial"] == 2
    assert review["aggregate"]["source_review_semantic_role_mismatch_records"] == 2
    assert review["aggregate"]["source_strength_inflation_count"] == 0
