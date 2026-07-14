from engine.system_b.reasoning_mechanism_factored_portfolio_v1 import (
    join_factored_mechanism_portfolio_v1,
    materialize_not_applicable_coverage_v1,
    plan_assistant_coverage_calls_v1,
)
from engine.system_b.reasoning_mechanism_ontology import MECHANISMS
from engine.system_b.reasoning_mechanism_submicrotask_v1 import (
    COVERAGE_RESPONSE_SCHEMA,
    USER_RESPONSE_SCHEMA,
)
from engine.system_b.simulated_reliability_v1 import build_mechanism_input_v1


def _record(role, rid):
    return {
        "role": role,
        "role_record_id": rid,
        "observation_id": rid,
        "case_id": "case-1",
        "semantic_status": "supported",
        "role_interpretation": "bounded meaning",
        "fidelity_note": "bounded",
        "limitations": "",
        "source_evidence_ids": ["e001"],
        "stance_components": [{
            "stance_object_kind": "belief_or_assessment",
            "stance_object_interpretation": "bounded meaning",
            "stance_expression_kind": "held_assessment",
            "source_evidence_id": "e001",
        }],
    }


def _parent_packet():
    joined = {
        "role_observations": {
            "starting": [_record("starting", "starting-1")],
            "current": [_record("current", "current-1")],
            "qualification": [],
        },
        "qualification_review": {
            "outcome": "no_unresolved_qualification_observed",
            "evidence_ids": ["e001"],
            "interpretation": "none",
            "limitations": "",
        },
    }
    return build_mechanism_input_v1(
        case_id="case-1",
        arm_id="arm-1",
        joined=joined,
        conversation="[Turn 1] USER:\nA\n\n[Turn 1] ASSISTANT:\nUse a boundary.",
        source_refs=[{"path": "source", "sha256": "abc"}],
    )


def _user(mechanism_id, status):
    if status == "not_observed":
        state, ids = "not_applicable", []
    elif status == "resolved":
        state, ids = "not_applicable", ["starting-1", "current-1"]
    else:
        state, ids = "present", ["current-1"]
    return {
        "schema_version": USER_RESPONSE_SCHEMA,
        "status": "user_status_custody_complete_from_explicit_factors",
        "assessment": {
            "mechanism_id": mechanism_id,
            "user_process_status": status,
            "pattern_state": state,
            "source_role_record_ids": ids,
        },
    }


def _coverage(mechanism_id, coverage):
    ids = [] if coverage == "not_covered" else ["assistant-turn-001"]
    return {
        "schema_version": COVERAGE_RESPONSE_SCHEMA,
        "status": "assistant_coverage_custody_complete",
        "assessment": {
            "mechanism_id": mechanism_id,
            "vanilla_answer_coverage": coverage,
            "source_assistant_contribution_ids": ids,
        },
    }


def test_full_portfolio_calls_coverage_only_for_observed_statuses_and_routes_one():
    mechanisms = sorted(MECHANISMS)
    user_results = []
    coverage_results = []
    for index, mechanism_id in enumerate(mechanisms):
        status = "unresolved" if index == 0 else "resolved" if index == 1 else "not_observed"
        user_results.append(_user(mechanism_id, status))
        if status == "unresolved":
            coverage_results.append(_coverage(mechanism_id, "not_covered"))
        elif status == "resolved":
            coverage_results.append(_coverage(mechanism_id, "operationalized"))
    plan = plan_assistant_coverage_calls_v1(user_results)
    assert plan["assistant_coverage_call_count"] == 2
    result = join_factored_mechanism_portfolio_v1(
        parent_packet=_parent_packet(),
        user_results=user_results,
        assistant_coverage_results=coverage_results,
        producer_id="test",
    )
    assert result["counts"] == {
        "user_factor_model_calls": 9,
        "assistant_coverage_model_calls": 2,
        "materialized_not_applicable": 7,
        "total_model_calls": 11,
        "routing_mechanisms": 1,
    }
    assert len(result["compiled_mechanism_packet"]["pattern_hypotheses"]) == 9


def test_not_applicable_coverage_is_policy_materialized_without_semantics():
    user = _user(sorted(MECHANISMS)[0], "not_observed")
    result = materialize_not_applicable_coverage_v1(user_result=user)
    assert result["assessment"]["vanilla_answer_coverage"] == "not_applicable"
    assert result["boundary"]["conversation_prose_inspected"] is False
