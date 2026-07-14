"""Provider-free contracts for reasoning-process custody and evaluation.

The validators in this module enforce shape, identity, lineage, budgets, and
product boundaries. They do not interpret conversation prose, decide semantic
relevance, score reasoning quality, evaluate a final memo, or route facts into
the mental-model graph.
"""
from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from typing import Any


PROCESS_LEDGER_SCHEMA_VERSION = "lolla.reasoning_process_ledger.v0"
BOUNDED_VIEW_SCHEMA_VERSION = "lolla.reasoning_process_bounded_view.v0"
PROCESS_ASSESSMENT_SCHEMA_VERSION = "lolla.reasoning_process_assessment.v0"
PHASE0_CONTRACT_SCHEMA_VERSION = "lolla.reasoning_process_phase0_contract.v0"

LEDGER_STATUS = "research_shadow"
VIEW_STATUS = "research_shadow"
ASSESSMENT_STATUS = "research_shadow"

OBSERVATION_FAMILIES = (
    "position_and_decision_trajectory",
    "exploration_and_alternatives",
    "evidence_and_assumption_discipline",
    "uncertainty_and_unresolved_state",
    "challenge_and_revision_response",
)
SEMANTIC_STATUSES = ("supported", "mixed", "unclear", "not_observed")
TERMINAL_STATES = (
    "admitted",
    "preserved_ambiguous",
    "quarantined_invalid_source",
    "quarantined_schema",
    "failed_operationally",
)
RELATION_TYPES = (
    "revises",
    "qualifies",
    "contradicts",
    "supersedes",
    "responds_to",
    "develops",
)
SEMANTIC_AUTHORITIES = ("probabilistic_reader", "source_reviewer")
MECHANICAL_AUTHORITIES = ("deterministic_validator",)
VIEW_DISPOSITIONS = (
    "included",
    "parked_not_applicable",
    "parked_redundant",
    "parked_unclear",
    "excluded_invalid_source",
    "excluded_schema_failure",
    "not_evaluated_budget",
)

ASSESSMENT_DIMENSIONS = (
    "exploration_and_alternative_coverage",
    "evidence_versus_assumption_discipline",
    "position_and_decision_trajectory",
    "challenge_and_revision_response",
    "uncertainty_and_reopen_conditions",
    "lolla_pressure_disposition",
    "assessment_limits",
)

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]*$")
_SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

_LEDGER_FIELDS = {
    "schema_version",
    "status",
    "ledger_id",
    "source",
    "observations",
    "failures",
    "boundary",
}
_SOURCE_FIELDS = {
    "conversation_id",
    "source_path",
    "source_sha256",
    "message_count",
    "authoritative_conversation_attached",
}
_OBSERVATION_FIELDS = {
    "observation_id",
    "family",
    "interpretation",
    "semantic_status",
    "source_span_ids",
    "provenance",
    "state_history",
    "terminal_state",
    "terminal_reason",
    "relations",
    "graph_routing_eligible",
}
_PROVENANCE_FIELDS = {
    "producer_kind",
    "producer_id",
    "call_id",
    "model",
    "prompt_sha256",
}
_STATE_FIELDS = {"state", "reason", "actor"}
_RELATION_FIELDS = {"relation_type", "target_observation_id", "authority"}
_FAILURE_FIELDS = {"failure_id", "stage", "code", "detail", "call_id", "terminal"}
_LEDGER_BOUNDARY_FIELDS = {
    "authoritative_conversation_referenced",
    "semantic_relevance_inferred_by_code",
    "final_output_evaluated",
    "quality_score_included",
    "direct_graph_routing_allowed",
}

_VIEW_FIELDS = {
    "schema_version",
    "status",
    "view_id",
    "view_kind",
    "question",
    "source_ledger_sha256",
    "input",
    "items",
    "dispositions",
    "budget",
    "boundary",
}
_VIEW_INPUT_FIELDS = {"ledger_observation_ids"}
_VIEW_ITEM_FIELDS = {
    "view_item_id",
    "interpretation",
    "status",
    "source_observation_ids",
    "source_span_ids",
    "limitations",
}
_DISPOSITION_FIELDS = {
    "observation_id",
    "disposition",
    "authority",
    "reason",
    "view_item_ids",
}
_BUDGET_FIELDS = {
    "max_input_observations",
    "max_input_utf8_bytes",
    "max_output_items",
    "observed_input_observations",
    "observed_input_utf8_bytes",
    "observed_output_items",
    "budget_exceeded",
}
_VIEW_BOUNDARY_FIELDS = {
    "authoritative_source",
    "semantic_selection_performed_by_code",
    "omissions_recoverable_from_ledger",
    "final_output_evaluated",
    "quality_score_included",
    "direct_graph_routing_allowed",
}

_ASSESSMENT_FIELDS = {
    "schema_version",
    "status",
    "assessment_id",
    "source_ledger_sha256",
    "source_view_ids",
    "observations",
    "telemetry",
    "boundary",
}
_ASSESSMENT_OBSERVATION_FIELDS = {
    "assessment_observation_id",
    "dimension",
    "status",
    "statement",
    "source_view_item_ids",
    "source_observation_ids",
    "scope_limitation",
}
_TELEMETRY_FIELDS = {
    "model_calls",
    "input_tokens",
    "output_tokens",
    "wall_time_ms",
    "treated_as_quality_evidence",
}
_ASSESSMENT_BOUNDARY_FIELDS = {
    "final_output_evaluated",
    "scalar_quality_score_included",
    "effort_score_included",
    "trust_score_included",
    "correctness_claimed",
}


class ReasoningProcessContractError(ValueError):
    """Raised when an artifact violates a reasoning-process contract."""


def phase0_contract() -> dict[str, Any]:
    """Return the frozen Phase-0 evidence and spending envelope."""

    return {
        "schema_version": PHASE0_CONTRACT_SCHEMA_VERSION,
        "status": "frozen_before_provider_calls",
        "date": "2026-07-11",
        "scope": "reasoning_process_representation_and_evaluation_only",
        "view_kinds": list(OBSERVATION_FAMILIES),
        "numeric_gates": {
            "authoritative_message_custody_rate": 1.0,
            "exact_source_reference_validity_rate": 1.0,
            "candidate_terminal_custody_rate": 1.0,
            "reviewed_material_present_or_disputed_rate": 1.0,
            "protected_item_accounting_rate": 1.0,
            "protected_item_visible_rate": 1.0,
            "invalid_admitted_item_count": 0,
            "source_strength_inflation_count": 0,
            "context_invisible_label_count": 0,
            "direct_graph_seed_count": 0,
            "critical_dimension_zero_count": 0,
            "max_view_input_observations": 32,
            "max_view_input_utf8_bytes": 24000,
            "max_view_output_items": 12,
            "max_provider_schema_depth": 8,
            "max_provider_schema_bytes": 12000,
        },
        "provider_envelope": {
            "phase_0_to_2_calls": 0,
            "development_baseline_calls_max": 5,
            "one_generic_repair_calls_max": 5,
            "two_case_transfer_calls_max": 10,
            "conditional_stability_calls_max": 10,
            "total_calls_hard_ceiling": 30,
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "evaluator_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
            "temperature": 0,
            "reasoning_enabled": False,
            "cost_ceiling_usd": 0.30,
            "paid_calls_authorized": False,
        },
        "failure_taxonomy": {
            "RP0": "contract_or_hash_mismatch",
            "RP1": "source_or_message_custody_failure",
            "RP2": "candidate_or_failure_terminal_custody_loss",
            "RP3": "material_process_concept_omitted",
            "RP4": "semantic_placement_or_role_failure",
            "RP5": "temporal_trajectory_failure",
            "RP6": "source_strength_inflation",
            "RP7": "context_invisible_semantic_label",
            "RP8": "fan_in_budget_or_overload_failure",
            "RP9": "protected_minority_signal_lost_to_compactness",
            "RP10": "provider_schema_or_transport_failure",
            "RP11": "transfer_or_repeat_stability_failure",
            "RP12": "gold_scorer_or_fixture_mismatch",
            "RP13": "process_assessment_overclaim_or_missing_lineage",
            "RP14": "deterministic_semantic_gate_or_silent_repair",
            "RP15": "final_output_graph_or_runtime_boundary_breach",
        },
        "stop_rules": [
            "no_provider_calls_before_phase_0_to_2_pass",
            "no_gate_weakening_after_output_is_seen",
            "no_case_specific_prompt_or_example",
            "no_silent_source_id_or_semantic_repair",
            "no_fallback_retry_or_response_healing",
            "one_generic_repair_maximum",
            "stop_after_same_load_bearing_failure_on_two_cases",
            "stop_if_protected_signals_are_lost_to_compactness",
            "stop_if_broad_capture_reappears_as_overloaded_fan_in",
            "stop_if_task_context_cannot_support_requested_label",
        ],
        "non_claims": [
            "not_final_memo_evaluation",
            "not_a_reasoning_quality_score",
            "not_an_effort_score",
            "not_a_trust_score",
            "not_proof_of_correctness",
            "not_graph_integration_authority",
            "not_runtime_integration_authority",
        ],
    }


def validate_process_ledger(
    payload: Mapping[str, Any],
    *,
    known_span_ids: Iterable[str],
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    _require_fields(payload, _LEDGER_FIELDS, "ledger", errors)
    if errors:
        raise ReasoningProcessContractError("; ".join(errors))
    if payload.get("schema_version") != PROCESS_LEDGER_SCHEMA_VERSION:
        errors.append("ledger.schema_version is invalid")
    if payload.get("status") != LEDGER_STATUS:
        errors.append("ledger.status is invalid")
    _require_id(payload.get("ledger_id"), "ledger.ledger_id", errors)

    source = payload.get("source")
    if not isinstance(source, Mapping):
        errors.append("ledger.source must be an object")
    else:
        _require_fields(source, _SOURCE_FIELDS, "ledger.source", errors)
        _require_id(source.get("conversation_id"), "ledger.source.conversation_id", errors)
        _require_text(source.get("source_path"), "ledger.source.source_path", errors)
        _require_sha(source.get("source_sha256"), "ledger.source.source_sha256", errors)
        if expected_source_sha256 and source.get("source_sha256") != expected_source_sha256:
            errors.append("ledger.source.source_sha256 does not match custody")
        if not _is_nonnegative_int(source.get("message_count"), minimum=1):
            errors.append("ledger.source.message_count must be a positive integer")
        if source.get("authoritative_conversation_attached") is not True:
            errors.append("ledger.source.authoritative_conversation_attached must be true")

    known_spans = set(known_span_ids)
    observations = payload.get("observations")
    if not isinstance(observations, list):
        errors.append("ledger.observations must be an array")
        observations = []
    observation_ids: list[str] = []
    admitted_count = 0
    ambiguous_count = 0
    for index, observation in enumerate(observations):
        prefix = f"ledger.observations[{index}]"
        if not isinstance(observation, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _require_fields(observation, _OBSERVATION_FIELDS, prefix, errors)
        if set(observation) != _OBSERVATION_FIELDS:
            continue
        observation_id = observation.get("observation_id")
        _require_id(observation_id, f"{prefix}.observation_id", errors)
        observation_ids.append(str(observation_id))
        if observation.get("family") not in OBSERVATION_FAMILIES:
            errors.append(f"{prefix}.family is invalid")
        if observation.get("semantic_status") not in SEMANTIC_STATUSES:
            errors.append(f"{prefix}.semantic_status is invalid")
        terminal_state = observation.get("terminal_state")
        if terminal_state not in TERMINAL_STATES:
            errors.append(f"{prefix}.terminal_state is invalid")
        _require_text(observation.get("terminal_reason"), f"{prefix}.terminal_reason", errors)
        if observation.get("graph_routing_eligible") is not False:
            errors.append(f"{prefix}.graph_routing_eligible must be false")

        source_span_ids = _string_array(
            observation.get("source_span_ids"), f"{prefix}.source_span_ids", errors
        )
        if terminal_state in {"admitted", "preserved_ambiguous"}:
            if not source_span_ids:
                errors.append(f"{prefix} admitted observations require source spans")
            for span_id in source_span_ids:
                if span_id not in known_spans:
                    errors.append(f"{prefix}.source_span_ids contains unknown span")
            _require_text(observation.get("interpretation"), f"{prefix}.interpretation", errors)
            admitted_count += 1
        if terminal_state == "preserved_ambiguous":
            ambiguous_count += 1
            if observation.get("semantic_status") not in {"mixed", "unclear"}:
                errors.append(f"{prefix} preserved ambiguity requires mixed or unclear status")
        if terminal_state == "failed_operationally" and observation.get("interpretation"):
            errors.append(f"{prefix} operational failure must not claim an interpretation")

        _validate_provenance(observation.get("provenance"), prefix, errors)
        _validate_state_history(observation.get("state_history"), terminal_state, prefix, errors)
        _validate_relations(observation.get("relations"), prefix, errors)

    if len(observation_ids) != len(set(observation_ids)):
        errors.append("ledger.observation_id values must be unique")
    observation_id_set = set(observation_ids)
    for index, observation in enumerate(observations):
        if not isinstance(observation, Mapping):
            continue
        for relation in observation.get("relations", []):
            if not isinstance(relation, Mapping):
                continue
            target = relation.get("target_observation_id")
            if target not in observation_id_set:
                errors.append(f"ledger.observations[{index}].relations contains unknown target")
            if target == observation.get("observation_id"):
                errors.append(f"ledger.observations[{index}].relations cannot target itself")

    failures = payload.get("failures")
    if not isinstance(failures, list):
        errors.append("ledger.failures must be an array")
        failures = []
    failure_ids: list[str] = []
    for index, failure in enumerate(failures):
        prefix = f"ledger.failures[{index}]"
        if not isinstance(failure, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _require_fields(failure, _FAILURE_FIELDS, prefix, errors)
        if set(failure) != _FAILURE_FIELDS:
            continue
        _require_id(failure.get("failure_id"), f"{prefix}.failure_id", errors)
        failure_ids.append(str(failure.get("failure_id")))
        for field in ("stage", "code", "detail"):
            _require_text(failure.get(field), f"{prefix}.{field}", errors)
        if not isinstance(failure.get("call_id"), str):
            errors.append(f"{prefix}.call_id must be a string")
        if failure.get("terminal") is not True:
            errors.append(f"{prefix}.terminal must be true")
    if len(failure_ids) != len(set(failure_ids)):
        errors.append("ledger.failure_id values must be unique")

    boundary = payload.get("boundary")
    _validate_exact_boolean_boundary(
        boundary,
        _LEDGER_BOUNDARY_FIELDS,
        {
            "authoritative_conversation_referenced": True,
            "semantic_relevance_inferred_by_code": False,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
        "ledger.boundary",
        errors,
    )
    if errors:
        raise ReasoningProcessContractError("; ".join(errors))
    return {
        "status": "structurally_valid_for_provider_free_research",
        "observation_count": len(observations),
        "admitted_observation_count": admitted_count,
        "preserved_ambiguous_count": ambiguous_count,
        "failure_count": len(failures),
        "source_custody_validated": True,
        "semantic_correctness_validated": False,
        "final_output_evaluated": False,
        "runtime_integration_authorized": False,
    }


def validate_bounded_view(
    payload: Mapping[str, Any],
    *,
    known_ledger_observation_ids: Iterable[str],
    known_span_ids: Iterable[str],
    expected_ledger_sha256: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    _require_fields(payload, _VIEW_FIELDS, "view", errors)
    if errors:
        raise ReasoningProcessContractError("; ".join(errors))
    if payload.get("schema_version") != BOUNDED_VIEW_SCHEMA_VERSION:
        errors.append("view.schema_version is invalid")
    if payload.get("status") != VIEW_STATUS:
        errors.append("view.status is invalid")
    _require_id(payload.get("view_id"), "view.view_id", errors)
    if payload.get("view_kind") not in OBSERVATION_FAMILIES:
        errors.append("view.view_kind is invalid")
    _require_text(payload.get("question"), "view.question", errors)
    _require_sha(payload.get("source_ledger_sha256"), "view.source_ledger_sha256", errors)
    if expected_ledger_sha256 and payload.get("source_ledger_sha256") != expected_ledger_sha256:
        errors.append("view.source_ledger_sha256 does not match custody")

    known_observations = set(known_ledger_observation_ids)
    input_object = payload.get("input")
    if not isinstance(input_object, Mapping):
        errors.append("view.input must be an object")
        input_ids: list[str] = []
    else:
        _require_fields(input_object, _VIEW_INPUT_FIELDS, "view.input", errors)
        input_ids = _string_array(
            input_object.get("ledger_observation_ids"),
            "view.input.ledger_observation_ids",
            errors,
        )
        if len(input_ids) != len(set(input_ids)):
            errors.append("view.input.ledger_observation_ids must be unique")
        if any(item not in known_observations for item in input_ids):
            errors.append("view.input references unknown ledger observations")

    known_spans = set(known_span_ids)
    items = payload.get("items")
    if not isinstance(items, list):
        errors.append("view.items must be an array")
        items = []
    view_item_ids: list[str] = []
    item_source_ids: set[str] = set()
    for index, item in enumerate(items):
        prefix = f"view.items[{index}]"
        if not isinstance(item, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _require_fields(item, _VIEW_ITEM_FIELDS, prefix, errors)
        if set(item) != _VIEW_ITEM_FIELDS:
            continue
        _require_id(item.get("view_item_id"), f"{prefix}.view_item_id", errors)
        view_item_ids.append(str(item.get("view_item_id")))
        _require_text(item.get("interpretation"), f"{prefix}.interpretation", errors)
        if item.get("status") not in {"supported", "mixed", "unclear"}:
            errors.append(f"{prefix}.status is invalid")
        source_observation_ids = _string_array(
            item.get("source_observation_ids"),
            f"{prefix}.source_observation_ids",
            errors,
        )
        if not source_observation_ids:
            errors.append(f"{prefix} requires source observations")
        if any(item_id not in input_ids for item_id in source_observation_ids):
            errors.append(f"{prefix} references observations outside the declared input")
        item_source_ids.update(source_observation_ids)
        source_span_ids = _string_array(
            item.get("source_span_ids"), f"{prefix}.source_span_ids", errors
        )
        if not source_span_ids:
            errors.append(f"{prefix} requires source spans")
        if any(span_id not in known_spans for span_id in source_span_ids):
            errors.append(f"{prefix} references unknown source spans")
        if not isinstance(item.get("limitations"), str):
            errors.append(f"{prefix}.limitations must be a string")
    if len(view_item_ids) != len(set(view_item_ids)):
        errors.append("view.view_item_id values must be unique")

    dispositions = payload.get("dispositions")
    if not isinstance(dispositions, list):
        errors.append("view.dispositions must be an array")
        dispositions = []
    disposition_ids: list[str] = []
    for index, disposition in enumerate(dispositions):
        prefix = f"view.dispositions[{index}]"
        if not isinstance(disposition, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _require_fields(disposition, _DISPOSITION_FIELDS, prefix, errors)
        if set(disposition) != _DISPOSITION_FIELDS:
            continue
        observation_id = str(disposition.get("observation_id", ""))
        disposition_ids.append(observation_id)
        if observation_id not in input_ids:
            errors.append(f"{prefix}.observation_id is outside the declared input")
        disposition_value = disposition.get("disposition")
        if disposition_value not in VIEW_DISPOSITIONS:
            errors.append(f"{prefix}.disposition is invalid")
        authority = disposition.get("authority")
        semantic_dispositions = {
            "included",
            "parked_not_applicable",
            "parked_redundant",
            "parked_unclear",
        }
        if disposition_value in semantic_dispositions and authority not in SEMANTIC_AUTHORITIES:
            errors.append(f"{prefix} semantic disposition requires probabilistic or source-review authority")
        if disposition_value not in semantic_dispositions and authority not in MECHANICAL_AUTHORITIES:
            errors.append(f"{prefix} mechanical disposition requires deterministic validator authority")
        _require_text(disposition.get("reason"), f"{prefix}.reason", errors)
        linked_view_items = _string_array(
            disposition.get("view_item_ids"), f"{prefix}.view_item_ids", errors
        )
        if disposition_value == "included":
            if not linked_view_items:
                errors.append(f"{prefix} included disposition requires view item lineage")
            if observation_id not in item_source_ids:
                errors.append(f"{prefix} claims inclusion without item source lineage")
        elif linked_view_items:
            errors.append(f"{prefix} non-included disposition must not claim view items")
        if any(item_id not in view_item_ids for item_id in linked_view_items):
            errors.append(f"{prefix}.view_item_ids contains an unknown item")
    if Counter(disposition_ids) != Counter(input_ids):
        errors.append("view.dispositions must account for every input observation exactly once")

    budget = payload.get("budget")
    if not isinstance(budget, Mapping):
        errors.append("view.budget must be an object")
    else:
        _require_fields(budget, _BUDGET_FIELDS, "view.budget", errors)
        for field in _BUDGET_FIELDS - {"budget_exceeded"}:
            if not _is_nonnegative_int(budget.get(field)):
                errors.append(f"view.budget.{field} must be a nonnegative integer")
        hard_gates = phase0_contract()["numeric_gates"]
        for field, hard_gate in (
            ("max_input_observations", "max_view_input_observations"),
            ("max_input_utf8_bytes", "max_view_input_utf8_bytes"),
            ("max_output_items", "max_view_output_items"),
        ):
            if _safe_int(budget.get(field)) > int(hard_gates[hard_gate]):
                errors.append(f"view.budget.{field} exceeds the Phase-0 hard ceiling")
        if budget.get("observed_input_observations") != len(input_ids):
            errors.append("view.budget.observed_input_observations does not match input")
        if budget.get("observed_output_items") != len(items):
            errors.append("view.budget.observed_output_items does not match items")
        exceeded = any(
            _safe_int(budget.get(observed)) > _safe_int(budget.get(maximum))
            for observed, maximum in (
                ("observed_input_observations", "max_input_observations"),
                ("observed_input_utf8_bytes", "max_input_utf8_bytes"),
                ("observed_output_items", "max_output_items"),
            )
        )
        if budget.get("budget_exceeded") is not exceeded:
            errors.append("view.budget.budget_exceeded does not match measurements")
        if exceeded:
            errors.append("view exceeds its frozen fan-in or output budget")

    _validate_exact_boolean_boundary(
        payload.get("boundary"),
        _VIEW_BOUNDARY_FIELDS,
        {
            "authoritative_source": False,
            "semantic_selection_performed_by_code": False,
            "omissions_recoverable_from_ledger": True,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
        "view.boundary",
        errors,
    )
    if errors:
        raise ReasoningProcessContractError("; ".join(errors))
    return {
        "status": "structurally_valid_for_provider_free_research",
        "view_kind": payload["view_kind"],
        "input_observation_count": len(input_ids),
        "output_item_count": len(items),
        "disposition_count": len(dispositions),
        "exact_input_accounting": True,
        "semantic_correctness_validated": False,
        "final_output_evaluated": False,
        "runtime_integration_authorized": False,
    }


def validate_process_assessment(
    payload: Mapping[str, Any],
    *,
    known_view_ids: Iterable[str],
    known_view_item_ids: Iterable[str],
    known_observation_ids: Iterable[str],
    expected_ledger_sha256: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    _require_fields(payload, _ASSESSMENT_FIELDS, "assessment", errors)
    if errors:
        raise ReasoningProcessContractError("; ".join(errors))
    if payload.get("schema_version") != PROCESS_ASSESSMENT_SCHEMA_VERSION:
        errors.append("assessment.schema_version is invalid")
    if payload.get("status") != ASSESSMENT_STATUS:
        errors.append("assessment.status is invalid")
    _require_id(payload.get("assessment_id"), "assessment.assessment_id", errors)
    _require_sha(payload.get("source_ledger_sha256"), "assessment.source_ledger_sha256", errors)
    if expected_ledger_sha256 and payload.get("source_ledger_sha256") != expected_ledger_sha256:
        errors.append("assessment.source_ledger_sha256 does not match custody")

    view_ids = _string_array(payload.get("source_view_ids"), "assessment.source_view_ids", errors)
    if not view_ids:
        errors.append("assessment.source_view_ids must not be empty")
    if len(view_ids) != len(set(view_ids)):
        errors.append("assessment.source_view_ids must be unique")
    if any(view_id not in set(known_view_ids) for view_id in view_ids):
        errors.append("assessment.source_view_ids contains an unknown view")

    known_items = set(known_view_item_ids)
    known_observations = set(known_observation_ids)
    observations = payload.get("observations")
    if not isinstance(observations, list):
        errors.append("assessment.observations must be an array")
        observations = []
    assessment_ids: list[str] = []
    dimensions: list[str] = []
    for index, observation in enumerate(observations):
        prefix = f"assessment.observations[{index}]"
        if not isinstance(observation, Mapping):
            errors.append(f"{prefix} must be an object")
            continue
        _require_fields(observation, _ASSESSMENT_OBSERVATION_FIELDS, prefix, errors)
        if set(observation) != _ASSESSMENT_OBSERVATION_FIELDS:
            continue
        _require_id(
            observation.get("assessment_observation_id"),
            f"{prefix}.assessment_observation_id",
            errors,
        )
        assessment_ids.append(str(observation.get("assessment_observation_id")))
        dimension = observation.get("dimension")
        dimensions.append(str(dimension))
        if dimension not in ASSESSMENT_DIMENSIONS:
            errors.append(f"{prefix}.dimension is invalid")
        status = observation.get("status")
        if status not in SEMANTIC_STATUSES:
            errors.append(f"{prefix}.status is invalid")
        _require_text(observation.get("statement"), f"{prefix}.statement", errors)
        _require_text(
            observation.get("scope_limitation"), f"{prefix}.scope_limitation", errors
        )
        source_view_item_ids = _string_array(
            observation.get("source_view_item_ids"),
            f"{prefix}.source_view_item_ids",
            errors,
        )
        source_observation_ids = _string_array(
            observation.get("source_observation_ids"),
            f"{prefix}.source_observation_ids",
            errors,
        )
        if any(item not in known_items for item in source_view_item_ids):
            errors.append(f"{prefix} references unknown view items")
        if any(item not in known_observations for item in source_observation_ids):
            errors.append(f"{prefix} references unknown ledger observations")
        if status in {"supported", "mixed", "unclear"} and (
            not source_view_item_ids or not source_observation_ids
        ):
            errors.append(f"{prefix} evidence-bearing status requires both lineage levels")
        if status == "not_observed" and (source_view_item_ids or source_observation_ids):
            errors.append(f"{prefix} not_observed must not invent item-level evidence")
    if len(assessment_ids) != len(set(assessment_ids)):
        errors.append("assessment observation IDs must be unique")
    if len(dimensions) != len(set(dimensions)):
        errors.append("assessment dimensions must not be duplicated")

    telemetry = payload.get("telemetry")
    if not isinstance(telemetry, Mapping):
        errors.append("assessment.telemetry must be an object")
    else:
        _require_fields(telemetry, _TELEMETRY_FIELDS, "assessment.telemetry", errors)
        for field in _TELEMETRY_FIELDS - {"treated_as_quality_evidence"}:
            if not _is_nonnegative_int(telemetry.get(field)):
                errors.append(f"assessment.telemetry.{field} must be a nonnegative integer")
        if telemetry.get("treated_as_quality_evidence") is not False:
            errors.append("assessment.telemetry must not be treated as quality evidence")

    _validate_exact_boolean_boundary(
        payload.get("boundary"),
        _ASSESSMENT_BOUNDARY_FIELDS,
        {
            "final_output_evaluated": False,
            "scalar_quality_score_included": False,
            "effort_score_included": False,
            "trust_score_included": False,
            "correctness_claimed": False,
        },
        "assessment.boundary",
        errors,
    )
    if errors:
        raise ReasoningProcessContractError("; ".join(errors))
    return {
        "status": "structurally_valid_for_provider_free_research",
        "assessment_observation_count": len(observations),
        "dimensions_observed": sorted(set(dimensions)),
        "lineage_validated": True,
        "semantic_correctness_validated": False,
        "final_output_evaluated": False,
        "quality_or_trust_score_emitted": False,
        "runtime_integration_authorized": False,
    }


def model_facing_schema(kind: str) -> dict[str, Any]:
    """Return a shallow strict-output-compatible schema projection.

    These schemas constrain transport shape only. Local validators remain the
    admission authority and semantic evaluation remains separate.
    """

    if kind == "bounded_view":
        item = _object_schema(
            "One source-linked interpretation for a bounded process question.",
            {
                "view_item_id": _string_schema("Stable view-local item ID."),
                "interpretation": _string_schema("Neutral process interpretation."),
                "status": _enum_schema("Evidence status.", ("supported", "mixed", "unclear")),
                "source_observation_ids": _array_schema(
                    "Ledger observations supporting the item.", _string_schema("Ledger observation ID."), 1, 8
                ),
                "source_span_ids": _array_schema(
                    "Exact source spans supporting the item.", _string_schema("Source span ID."), 1, 12
                ),
                "limitations": _string_schema("Uncertainty or missing context; empty only when none is known."),
            },
        )
        disposition = _object_schema(
            "Terminal per-view accounting for one input observation.",
            {
                "observation_id": _string_schema("Input ledger observation ID."),
                "disposition": _enum_schema("How this view treated the observation.", VIEW_DISPOSITIONS),
                "authority": _enum_schema(
                    "Who made the disposition.", SEMANTIC_AUTHORITIES + MECHANICAL_AUTHORITIES
                ),
                "reason": _string_schema("Concrete reason for the disposition."),
                "view_item_ids": _array_schema(
                    "Resulting view item IDs; empty unless included.", _string_schema("View item ID."), 0, 4
                ),
            },
        )
        return _object_schema(
            "Bounded reasoning-process view response.",
            {
                "items": _array_schema("Process-view items.", item, 0, 12),
                "dispositions": _array_schema("Exact input-observation accounting.", disposition, 0, 32),
            },
        )
    if kind == "process_assessment":
        observation = _object_schema(
            "One evidence-linked observation about the reasoning process, not the final answer.",
            {
                "assessment_observation_id": _string_schema("Stable assessment-local ID."),
                "dimension": _enum_schema("Process dimension being observed.", ASSESSMENT_DIMENSIONS),
                "status": _enum_schema("Evidence status.", SEMANTIC_STATUSES),
                "statement": _string_schema("Bounded statement about the observed process."),
                "source_view_item_ids": _array_schema(
                    "Supporting view items; empty only for not_observed.", _string_schema("View item ID."), 0, 12
                ),
                "source_observation_ids": _array_schema(
                    "Supporting ledger observations; empty only for not_observed.", _string_schema("Ledger observation ID."), 0, 16
                ),
                "scope_limitation": _string_schema("Why the statement must not be generalized beyond the captured process."),
            },
        )
        return _object_schema(
            "Evidence vector about the reasoning process; never a scalar score.",
            {"observations": _array_schema("Process assessment observations.", observation, 1, 7)},
        )
    raise ValueError("kind must be bounded_view or process_assessment")


def schema_metrics(schema: Mapping[str, Any]) -> dict[str, int]:
    import json

    def depth(value: object, level: int = 1) -> int:
        if isinstance(value, Mapping):
            return max([level] + [depth(item, level + 1) for item in value.values()])
        if isinstance(value, list):
            return max([level] + [depth(item, level + 1) for item in value])
        return level

    return {
        "bytes": len(json.dumps(schema, sort_keys=True, separators=(",", ":")).encode("utf-8")),
        "depth": depth(schema),
    }


def _validate_provenance(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{prefix}.provenance must be an object")
        return
    _require_fields(value, _PROVENANCE_FIELDS, f"{prefix}.provenance", errors)
    if set(value) != _PROVENANCE_FIELDS:
        return
    if value.get("producer_kind") not in {"model", "human_review", "fixture"}:
        errors.append(f"{prefix}.provenance.producer_kind is invalid")
    _require_text(value.get("producer_id"), f"{prefix}.provenance.producer_id", errors)
    for field in ("call_id", "model"):
        if not isinstance(value.get(field), str):
            errors.append(f"{prefix}.provenance.{field} must be a string")
    prompt_hash = value.get("prompt_sha256")
    if prompt_hash != "" and not (isinstance(prompt_hash, str) and _SHA_RE.fullmatch(prompt_hash)):
        errors.append(f"{prefix}.provenance.prompt_sha256 is invalid")
    if value.get("producer_kind") == "model":
        for field in ("call_id", "model", "prompt_sha256"):
            _require_text(value.get(field), f"{prefix}.provenance.{field}", errors)


def _validate_state_history(value: object, terminal_state: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, list) or len(value) < 2:
        errors.append(f"{prefix}.state_history must contain proposed and terminal states")
        return
    states: list[str] = []
    for index, row in enumerate(value):
        row_prefix = f"{prefix}.state_history[{index}]"
        if not isinstance(row, Mapping):
            errors.append(f"{row_prefix} must be an object")
            continue
        _require_fields(row, _STATE_FIELDS, row_prefix, errors)
        if set(row) != _STATE_FIELDS:
            continue
        state = str(row.get("state", ""))
        states.append(state)
        if state not in {"proposed", *TERMINAL_STATES}:
            errors.append(f"{row_prefix}.state is invalid")
        _require_text(row.get("reason"), f"{row_prefix}.reason", errors)
        _require_text(row.get("actor"), f"{row_prefix}.actor", errors)
    if states and states[0] != "proposed":
        errors.append(f"{prefix}.state_history must start with proposed")
    if states and states[-1] != terminal_state:
        errors.append(f"{prefix}.state_history must end with terminal_state")


def _validate_relations(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{prefix}.relations must be an array")
        return
    for index, relation in enumerate(value):
        relation_prefix = f"{prefix}.relations[{index}]"
        if not isinstance(relation, Mapping):
            errors.append(f"{relation_prefix} must be an object")
            continue
        _require_fields(relation, _RELATION_FIELDS, relation_prefix, errors)
        if set(relation) != _RELATION_FIELDS:
            continue
        if relation.get("relation_type") not in RELATION_TYPES:
            errors.append(f"{relation_prefix}.relation_type is invalid")
        _require_id(relation.get("target_observation_id"), f"{relation_prefix}.target_observation_id", errors)
        if relation.get("authority") not in SEMANTIC_AUTHORITIES:
            errors.append(f"{relation_prefix}.authority must be semantic")


def _validate_exact_boolean_boundary(
    value: object,
    fields: set[str],
    expected: Mapping[str, bool],
    prefix: str,
    errors: list[str],
) -> None:
    if not isinstance(value, Mapping):
        errors.append(f"{prefix} must be an object")
        return
    _require_fields(value, fields, prefix, errors)
    for field, expected_value in expected.items():
        if value.get(field) is not expected_value:
            errors.append(f"{prefix}.{field} must be {str(expected_value).lower()}")


def _require_fields(value: Mapping[str, Any], fields: set[str], prefix: str, errors: list[str]) -> None:
    missing = sorted(fields - set(value))
    extra = sorted(set(value) - fields)
    if missing:
        errors.append(f"{prefix} missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix} unknown fields: {', '.join(extra)}")


def _require_id(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        errors.append(f"{prefix} must be a stable lowercase ID")


def _require_sha(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not _SHA_RE.fullmatch(value):
        errors.append(f"{prefix} must be a prefixed lowercase SHA-256")


def _require_text(value: object, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix} must be a non-empty string")


def _string_array(value: object, prefix: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        errors.append(f"{prefix} must be an array of non-empty strings")
        return []
    return list(value)


def _is_nonnegative_int(value: object, *, minimum: int = 0) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def _safe_int(value: object) -> int:
    return value if _is_nonnegative_int(value) else 0


def _object_schema(description: str, properties: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "description": description,
        "properties": dict(properties),
        "required": list(properties),
        "additionalProperties": False,
    }


def _string_schema(description: str) -> dict[str, Any]:
    return {"type": "string", "description": description}


def _enum_schema(description: str, values: Sequence[str]) -> dict[str, Any]:
    return {"type": "string", "description": description, "enum": list(values)}


def _array_schema(
    description: str,
    items: Mapping[str, Any],
    minimum: int,
    maximum: int,
) -> dict[str, Any]:
    return {
        "type": "array",
        "description": description,
        "items": dict(items),
        "minItems": minimum,
        "maxItems": maximum,
    }
