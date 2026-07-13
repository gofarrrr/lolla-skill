"""Provider-free orchestration for a full portfolio of factored mechanisms."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .reasoning_mechanism_ontology import MECHANISMS
from .reasoning_mechanism_submicrotask_v1 import (
    COVERAGE_RESPONSE_SCHEMA,
    USER_RESPONSE_SCHEMA,
    join_split_mechanism_assessment_v1,
)
from .simulated_reliability_v1 import (
    SimulatedReliabilityError,
    compile_mechanism_response_v1,
    validate_mechanism_input_v1,
)


PORTFOLIO_SCHEMA = "lolla.reasoning_mechanism_factored_portfolio.v1"


def _index_results(
    values: Sequence[Mapping[str, Any]], *, schema: str, label: str
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for value in values:
        if value.get("schema_version") != schema:
            raise SimulatedReliabilityError(f"invalid {label} result schema")
        mechanism_id = value.get("assessment", {}).get("mechanism_id")
        if mechanism_id not in MECHANISMS or mechanism_id in result:
            raise SimulatedReliabilityError(f"invalid or duplicate {label} mechanism")
        result[mechanism_id] = value
    return result


def plan_assistant_coverage_calls_v1(
    user_results: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Plan calls from explicit model-authored status, never from conversation prose."""

    users = _index_results(user_results, schema=USER_RESPONSE_SCHEMA, label="user-status")
    if set(users) != set(MECHANISMS):
        raise SimulatedReliabilityError("full user-status mechanism coverage is incomplete")
    call_ids = sorted(
        mechanism_id
        for mechanism_id, result in users.items()
        if result["assessment"]["user_process_status"] != "not_observed"
    )
    not_applicable_ids = sorted(set(MECHANISMS) - set(call_ids))
    return {
        "schema_version": "lolla.reasoning_mechanism_coverage_call_plan.v1",
        "assistant_coverage_call_mechanism_ids": call_ids,
        "materialize_not_applicable_mechanism_ids": not_applicable_ids,
        "assistant_coverage_call_count": len(call_ids),
        "boundary": {
            "plan_reads_model_authored_status_only": True,
            "conversation_prose_inspected": False,
            "keyword_or_chronology_gate_added": False,
            "deterministic_semantic_inference": False,
            "coverage_semantics_inferred": False,
        },
    }


def materialize_not_applicable_coverage_v1(
    *, user_result: Mapping[str, Any]
) -> dict[str, Any]:
    if user_result.get("schema_version") != USER_RESPONSE_SCHEMA:
        raise SimulatedReliabilityError("invalid not-applicable user result")
    assessment = user_result.get("assessment", {})
    if assessment.get("user_process_status") != "not_observed":
        raise SimulatedReliabilityError("coverage is applicable for observed mechanism")
    return {
        "schema_version": COVERAGE_RESPONSE_SCHEMA,
        "status": "assistant_coverage_not_applicable_from_explicit_user_status",
        "assessment": {
            "mechanism_id": assessment["mechanism_id"],
            "vanilla_answer_coverage": "not_applicable",
            "source_assistant_contribution_ids": [],
        },
        "producer_id": "deterministic_not_applicable_policy_v1",
        "boundary": {
            "semantic_fields_model_authored": False,
            "not_applicable_derived_from_explicit_not_observed_status": True,
            "conversation_prose_inspected": False,
            "deterministic_semantic_inference": False,
            "semantic_repair_performed": False,
            "routing_disposition_authored": False,
        },
    }


def join_factored_mechanism_portfolio_v1(
    *,
    parent_packet: Mapping[str, Any],
    user_results: Sequence[Mapping[str, Any]],
    assistant_coverage_results: Sequence[Mapping[str, Any]],
    producer_id: str,
) -> dict[str, Any]:
    validate_mechanism_input_v1(parent_packet)
    users = _index_results(user_results, schema=USER_RESPONSE_SCHEMA, label="user-status")
    if set(users) != set(MECHANISMS):
        raise SimulatedReliabilityError("full user-status mechanism coverage is incomplete")
    coverage = _index_results(
        assistant_coverage_results,
        schema=COVERAGE_RESPONSE_SCHEMA,
        label="assistant-coverage",
    )
    plan = plan_assistant_coverage_calls_v1(user_results)
    required_calls = set(plan["assistant_coverage_call_mechanism_ids"])
    if set(coverage) != required_calls:
        raise SimulatedReliabilityError("assistant-coverage results do not match call plan")
    all_coverage = dict(coverage)
    for mechanism_id in plan["materialize_not_applicable_mechanism_ids"]:
        all_coverage[mechanism_id] = materialize_not_applicable_coverage_v1(
            user_result=users[mechanism_id]
        )
    rows = []
    split_results = []
    for mechanism_id in sorted(MECHANISMS):
        split = join_split_mechanism_assessment_v1(
            user_result=users[mechanism_id],
            coverage_result=all_coverage[mechanism_id],
        )
        split_results.append(split)
        rows.append(split["assessment"])
    compiled = compile_mechanism_response_v1(
        response={"assessments": rows},
        packet=parent_packet,
        producer_kind="factored_mechanism_portfolio_v1",
        producer_id=producer_id,
    )
    return {
        "schema_version": PORTFOLIO_SCHEMA,
        "status": "full_factored_mechanism_portfolio_joined",
        "coverage_call_plan": plan,
        "split_results": split_results,
        "compiled_mechanism_packet": compiled,
        "counts": {
            "user_factor_model_calls": len(MECHANISMS),
            "assistant_coverage_model_calls": len(required_calls),
            "materialized_not_applicable": len(MECHANISMS) - len(required_calls),
            "total_model_calls": len(MECHANISMS) + len(required_calls),
            "routing_mechanisms": len(
                compiled["routing_projection"]["pattern_nodes"]
            ),
        },
        "boundary": {
            "all_nine_mechanisms_present": True,
            "coverage_calls_conditioned_on_model_authored_status": True,
            "routing_dispositions_derived_from_explicit_semantic_fields": True,
            "conversation_prose_inspected_by_join": False,
            "deterministic_semantic_inference": False,
            "keyword_or_chronology_gate_added": False,
            "semantic_repair_performed": False,
            "direct_graph_routing_allowed": False,
        },
    }
