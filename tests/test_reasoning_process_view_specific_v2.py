from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from engine.system_b.reasoning_process_contracts import schema_metrics
from engine.system_b.reasoning_process_view_specific import ViewSpecificInterfaceError
from engine.system_b.reasoning_process_view_specific_v2 import (
    response_schema_v2,
    validate_response_v2,
)
from scripts.evals.build_reasoning_process_view_specific_v2 import build


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "research/reasoning-process-view-specific-v2-2026-07-11"
CASE = "amb1-case02-nonprofit-scale"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fixture(view_kind: str) -> tuple[dict, dict]:
    artifact = _load(OUTPUT / "fixtures" / CASE / f"{view_kind}.json")
    wrapper = _load(
        ROOT
        / "research/reasoning-process-view-specific-interface-2026-07-11/cases"
        / CASE
        / view_kind
        / "reader-packet.json"
    )
    return artifact["response"], wrapper


def test_v2_builds_15_relationship_fixtures_and_append_only_views(
    tmp_path: Path,
) -> None:
    report = build(root=ROOT, output=tmp_path / "v2")
    summary = report["summary"]
    assert report["status"] == "provider_free_relationship_contract_pass"
    assert summary["failure_derived_relationship_fixture_count"] == 15
    assert summary["fixture_pass_count"] == 15
    assert summary["append_only_compile_pass_count"] == 15
    assert summary["provider_calls"] == 0
    assert summary["graph_calls"] == 0
    assert report["decision"]["ready_for_another_model_call"] is True
    assert report["decision"]["phase4_transfer_authorized"] is False


def test_v2_schemas_remain_shallow_and_quote_free() -> None:
    for view_kind in (
        "position_and_decision_trajectory",
        "exploration_and_alternatives",
        "evidence_and_assumption_discipline",
        "uncertainty_and_unresolved_state",
        "challenge_and_revision_response",
    ):
        schema = response_schema_v2(view_kind)
        metrics = schema_metrics(schema)
        assert metrics["bytes"] <= 12000
        assert metrics["depth"] <= 8
        assert '"quote"' not in json.dumps(schema)


def test_trajectory_claim_requires_starting_state_evidence() -> None:
    response, wrapper = _fixture("position_and_decision_trajectory")
    invalid = copy.deepcopy(response)
    invalid["records"][0]["starting_state_evidence_ids"] = []
    with pytest.raises(
        ViewSpecificInterfaceError, match="trajectory claim requires starting-state evidence"
    ):
        validate_response_v2(invalid, wrapper=wrapper)


def test_current_only_position_can_honestly_omit_starting_state() -> None:
    response, wrapper = _fixture("position_and_decision_trajectory")
    current_only = copy.deepcopy(response)
    current_only["records"][0]["trajectory_type"] = "qualified_current_only"
    current_only["records"][0]["starting_state_evidence_ids"] = []
    validated = validate_response_v2(current_only, wrapper=wrapper)
    assert validated["source_alias_custody_validated"] is True


def test_alternative_requires_attached_limit_evidence_and_statement() -> None:
    response, wrapper = _fixture("exploration_and_alternatives")
    missing_evidence = copy.deepcopy(response)
    missing_evidence["records"][0]["attached_condition_or_limit_evidence_ids"] = []
    with pytest.raises(ViewSpecificInterfaceError, match="must not be empty"):
        validate_response_v2(missing_evidence, wrapper=wrapper)
    missing_statement = copy.deepcopy(response)
    missing_statement["records"][0][
        "attached_condition_or_limit_interpretation"
    ] = ""
    with pytest.raises(ViewSpecificInterfaceError, match="must be stated"):
        validate_response_v2(missing_statement, wrapper=wrapper)


def test_challenge_requires_prior_frame_and_revision_evidence() -> None:
    response, wrapper = _fixture("challenge_and_revision_response")
    mere_proposal = copy.deepcopy(response)
    mere_proposal["records"][0]["prior_claim_or_frame_evidence_ids"] = []
    with pytest.raises(ViewSpecificInterfaceError, match="must not be empty"):
        validate_response_v2(mere_proposal, wrapper=wrapper)
    missing_revision = copy.deepcopy(response)
    missing_revision["records"][0]["revision_evidence_ids"] = []
    with pytest.raises(ViewSpecificInterfaceError, match="revise requires revision"):
        validate_response_v2(missing_revision, wrapper=wrapper)


def test_unanswered_challenge_remains_representable() -> None:
    response, wrapper = _fixture("challenge_and_revision_response")
    unanswered = copy.deepcopy(response)
    unanswered["records"][0]["response_type"] = "no_response"
    unanswered["records"][0]["response_evidence_ids"] = []
    unanswered["records"][0]["revision_evidence_ids"] = []
    validated = validate_response_v2(unanswered, wrapper=wrapper)
    assert validated["records"][0]["source_span_ids"]


def test_v2_compiler_preserves_raw_relationship_roles_and_zero_graph_routing() -> None:
    artifact = _load(
        OUTPUT
        / "fixtures"
        / CASE
        / "challenge_and_revision_response.json"
    )
    compiled = artifact["compiled"]
    observation = compiled["model_addendum"]["observations"][0]
    raw = observation["raw_record"]["v2_record"]
    assert raw["prior_claim_or_frame_evidence_ids"]
    assert raw["challenge_evidence_ids"]
    assert raw["response_evidence_ids"]
    assert compiled["boundary"]["v2_raw_relationship_roles_preserved"] is True
    assert compiled["boundary"]["direct_graph_routing_allowed"] is False
    assert observation["graph_routing_eligible"] is False
