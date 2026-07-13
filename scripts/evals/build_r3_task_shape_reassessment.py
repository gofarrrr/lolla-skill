#!/usr/bin/env python3
"""Build the provider-free R3 final-consumer task-shape reassessment."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.r3_fresh_consumer import value_sha256  # noqa: E402
from engine.system_b.r3_task_shape_counterfactual import (  # noqa: E402
    BOUNDARY_TEXT_MAX,
    EFFECT_TEXT_MAX,
    REQUIRED_ROW_TEXT_MAX,
    OUTCOME_MAP,
    build_synthesis_packet,
    canonical_json_bytes,
    collapsed_one_pass_request_body,
    compile_disposition_stage_response,
    describe_cross_field_surfaces,
    disposition_stage_request_body,
    frozen_responsibility_map,
    request_metrics,
    synthesis_stage_request_body,
)
from scripts.evals.finalize_r3_repaired_pressure_failure import (  # noqa: E402
    collect_mechanical_findings,
)
from scripts.evals.run_r3_repaired_pressure import (  # noqa: E402
    validate_execution_contract,
)


BASE_CONTRACT = ROOT / "docs/evals/lolla-r3-repaired-pressure-execution-contract-v1.json"
BASE_AUTHORIZATION = ROOT / "docs/evals/lolla-r3-repaired-pressure-authorization-v1.json"
CALL_RESULT = ROOT / (
    "research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/"
    "pressure-call-result.json"
)
FAILURE_CLOSEOUT = ROOT / (
    "research/lolla-r3-fresh-consumer-2026-07-13/pressure-r2-repaired/"
    "failure-closeout.json"
)
CURRENT_PRACTICE = ROOT / (
    "docs/conversation-understanding/"
    "lolla-r3-task-shape-current-practice-2026-07-13.md"
)
MODULE = ROOT / "engine/system_b/r3_task_shape_counterfactual.py"
BUILDER = ROOT / "scripts/evals/build_r3_task_shape_reassessment.py"

ARTIFACT_SCHEMA = "lolla.r3_task_shape_reassessment_artifact.v1"
SUMMARY_SCHEMA = "lolla.r3_task_shape_reassessment_summary.v1"


class R3TaskShapeBuildError(RuntimeError):
    """Raised when the provider-free reassessment cannot be sealed."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3TaskShapeBuildError(f"expected JSON object: {path}")
    return value


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _artifact(kind: str, value: dict[str, Any]) -> dict[str, Any]:
    result = {
        "schema_version": ARTIFACT_SCHEMA,
        "artifact_kind": kind,
        **value,
        "provider_calls": 0,
        "next_call_authorized": False,
    }
    result["artifact_sha256"] = value_sha256(result)
    return result


def _mechanical_stress_response(packet: Mapping[str, Any]) -> dict[str, Any]:
    """Maximum local text fixture; it is not semantic gold or model output."""

    rows = []
    for item in packet["constitutional_graph_survival"]["active_pressure_items"]:
        rows.append(
            {
                "pressure_id": item["pressure_id"],
                "outcome": "apply_new_condition",
                "source_turn_numbers": [packet["source_turn_numbers"][0]],
                "strongest_plausible_application": "s" * REQUIRED_ROW_TEXT_MAX,
                "attempted_application_condition": "a" * REQUIRED_ROW_TEXT_MAX,
                "why": "w" * REQUIRED_ROW_TEXT_MAX,
                "disposition_boundary": "b" * BOUNDARY_TEXT_MAX,
                "visible_effect": "v" * EFFECT_TEXT_MAX,
                "private_guardrail": "",
            }
        )
    return {"candidate_dispositions": rows}


def _responsibility_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    llm = [row for row in rows if row["owner"] == "llm"]
    deterministic = [row for row in rows if row["owner"] == "deterministic"]
    return {
        "current_one_pass_llm_responsibilities": sum(row["current"] for row in llm),
        "collapsed_one_pass_llm_responsibilities": sum(row["collapsed"] for row in llm),
        "separated_disposition_llm_responsibilities": sum(
            row["disposition_stage"] for row in llm
        ),
        "separated_synthesis_llm_responsibilities": sum(
            row["synthesis_stage"] for row in llm
        ),
        "deterministic_responsibility_count": len(deterministic),
        "interpretation": (
            "Collapsed outcome removes one independent coordination surface, not one "
            "semantic judgment. Separation redistributes responsibilities across calls."
        ),
    }


def build(output: Path) -> dict[str, Any]:
    contract, bundle = validate_execution_contract(
        contract_path=BASE_CONTRACT,
        authorization_path=BASE_AUTHORIZATION,
    )
    call_result = _load(CALL_RESULT)
    closeout = _load(FAILURE_CLOSEOUT)
    if call_result.get("call_result_sha256") != value_sha256(
        {key: value for key, value in call_result.items() if key != "call_result_sha256"}
    ):
        raise R3TaskShapeBuildError("R3 call result self-hash drifted")
    if (
        call_result.get("status") != "pressure_response_invalid_preserved"
        or call_result.get("provider_calls") != 1
        or call_result.get("mechanical_contract_valid") is not False
    ):
        raise R3TaskShapeBuildError("R3 failure evidence drifted")
    if closeout.get("call_result_sha256") != call_result["call_result_sha256"]:
        raise R3TaskShapeBuildError("R3 failure closeout lost call custody")
    packet = bundle["packet"]
    candidate = call_result.get("candidate")
    if not isinstance(candidate, Mapping):
        raise R3TaskShapeBuildError("preserved provider candidate is missing")
    findings = collect_mechanical_findings(candidate=candidate, packet=packet)
    if findings != [
        {
            "path": "/candidate_dispositions/2",
            "code": "park_contract_violation",
            "observed": {
                "effect": "uncertainty_change",
                "visible_effect": "",
                "private_guardrail": "",
            },
            "expected": "no material effect, empty effects, and reopen condition",
        }
    ]:
        raise R3TaskShapeBuildError("exact R3 mechanical signature drifted")

    responsibilities = frozen_responsibility_map()
    responsibility_artifact = _artifact(
        "responsibility_map",
        {
            "status": "exact_current_and_counterfactual_responsibilities_mapped",
            "case_id": packet["case_id"],
            "rows": responsibilities,
            "summary": _responsibility_summary(responsibilities),
            "cross_field_surfaces": describe_cross_field_surfaces(),
            "non_claims": [
                "responsibility_count_is_not_difficulty",
                "one_failure_does_not_prove_overload",
                "smaller_schema_is_not_semantic_quality",
            ],
        },
    )

    failure_artifact = _artifact(
        "causal_failure_audit",
        {
            "status": "one_redundant_cross_field_conflict_observed_cause_not_overclaimed",
            "case_id": packet["case_id"],
            "call_result_sha256": call_result["call_result_sha256"],
            "rows_returned": len(candidate["candidate_dispositions"]),
            "rows_without_mechanical_findings": (
                len(candidate["candidate_dispositions"]) - len(findings)
            ),
            "mechanical_findings": findings,
            "lossless_collapsed_outcome_mapping": False,
            "why_lossless_mapping_is_impossible": (
                "The preserved row asserts park and uncertainty_change simultaneously; "
                "one controlled outcome cannot preserve both conflicting labels."
            ),
            "counterfactual_choices_not_taken": [
                {
                    "preserve": "disposition",
                    "would_require": "change uncertainty_change to no_material_effect",
                    "status": "semantic_choice_not_made_by_code",
                },
                {
                    "preserve": "effect",
                    "would_require": (
                        "change park to apply_uncertainty_change and add missing effect custody"
                    ),
                    "status": "semantic_choice_not_made_by_code",
                },
            ],
            "diagnosis_vector": {
                "redundant_wire_coordination": "directly_observed",
                "combined_task_overload": "possible_not_established",
                "model_capability_limit": "possible_not_established",
                "ontology_ambiguity": "possible_not_established",
                "provider_transport": "passed_for_exact_repaired_request",
            },
            "semantic_review_status": "prohibited_after_mechanical_failure",
        },
    )

    base_body = bundle["request_body"]
    current_metrics = request_metrics(base_body)
    collapsed_body = collapsed_one_pass_request_body(
        base_body=base_body, packet=packet
    )
    collapsed_metrics = request_metrics(collapsed_body)
    disposition_body = disposition_stage_request_body(
        base_body=base_body, packet=packet
    )
    disposition_metrics = request_metrics(disposition_body)
    stress_ledger = compile_disposition_stage_response(
        response=_mechanical_stress_response(packet), packet=packet
    )
    synthesis_packet = build_synthesis_packet(packet=packet, ledger=stress_ledger)
    synthesis_body = synthesis_stage_request_body(
        base_body=base_body, synthesis_packet=synthesis_packet
    )
    synthesis_metrics = request_metrics(synthesis_body)
    split_cost = round(
        disposition_metrics["maximum_estimated_cost_usd"]
        + synthesis_metrics["maximum_estimated_cost_usd"],
        9,
    )

    contracts_artifact = _artifact(
        "counterfactual_contracts",
        {
            "status": "three_provider_free_contracts_frozen_for_comparison",
            "case_id": packet["case_id"],
            "packet_sha256": packet["packet_sha256"],
            "outcome_vocabulary": [
                {
                    "outcome": outcome,
                    "canonical_disposition": pair[0],
                    "canonical_effect": pair[1],
                }
                for outcome, pair in OUTCOME_MAP.items()
            ],
            "current_one_pass": {
                "source_path": _relative(
                    ROOT
                    / "research/lolla-r3-fresh-consumer-2026-07-13/"
                    "provider-free-repair-v1/prospective-pressure-bundle.json"
                ),
                "metrics": current_metrics,
                "provider_acceptance_evidence": "one exact repaired call accepted",
            },
            "collapsed_outcome_one_pass": {
                "reconstruction_function": (
                    "engine.system_b.r3_task_shape_counterfactual."
                    "collapsed_one_pass_request_body"
                ),
                "metrics": collapsed_metrics,
                "provider_acceptance_evidence": "none_provider_free_only",
            },
            "separated_disposition_then_synthesis": {
                "disposition_reconstruction_function": (
                    "engine.system_b.r3_task_shape_counterfactual."
                    "disposition_stage_request_body"
                ),
                "disposition_metrics": disposition_metrics,
                "maximum_stress_ledger_sha256": stress_ledger["ledger_sha256"],
                "maximum_stress_ledger_bytes": canonical_json_bytes(stress_ledger),
                "synthesis_packet_sha256": synthesis_packet[
                    "synthesis_packet_sha256"
                ],
                "synthesis_reconstruction_function": (
                    "engine.system_b.r3_task_shape_counterfactual."
                    "synthesis_stage_request_body"
                ),
                "synthesis_metrics": synthesis_metrics,
                "combined_maximum_estimated_cost_usd": split_cost,
                "provider_acceptance_evidence": "none_provider_free_only",
            },
            "custody": {
                "all_variants_keep_complete_conversation": True,
                "all_variants_keep_all_nine_pressure_ids": True,
                "all_variants_allow_apply_reject_park": True,
                "collapsed_mapping_is_controlled_label_replay": True,
                "semantic_applicability_inferred_by_code": False,
                "candidate_deletion_allowed": False,
                "stress_fixture_is_semantic_gold": False,
                "stress_fixture_is_model_output": False,
            },
        },
    )

    comparison_artifact = _artifact(
        "comparison_vector",
        {
            "status": "provider_free_vector_complete_no_scalar_score",
            "case_id": packet["case_id"],
            "alternatives": [
                {
                    "alternative": "current_one_pass",
                    "provider_calls_per_run": 1,
                    "serial_call_depth": 1,
                    "transfer_boundaries": 0,
                    "active_candidates_at_fan_in": 9,
                    "semantic_visibility": (
                        "complete conversation, original answer, nine full pressure "
                        "items, and answer task in one context"
                    ),
                    "estimated_prompt_tokens": current_metrics[
                        "estimated_prompt_tokens"
                    ],
                    "prompt_fan_in_utf8_bytes": current_metrics[
                        "user_prompt_utf8_bytes"
                    ],
                    "independent_disposition_effect_fields": 2,
                    "schema_properties": current_metrics[
                        "response_schema_metrics"
                    ]["total_object_properties"],
                    "schema_bytes": current_metrics["response_schema_metrics"][
                        "canonical_bytes"
                    ],
                    "maximum_estimated_cost_usd": current_metrics[
                        "maximum_estimated_cost_usd"
                    ],
                    "exact_operational_cost_usd": call_result[
                        "provider_reported_cost_usd"
                    ],
                    "exact_observed_failure_prevented_by_shape": False,
                    "latency_consequence": "one provider round trip",
                    "deterministic_semantic_leakage": False,
                    "new_failure_surface": "none_existing_reference",
                },
                {
                    "alternative": "collapsed_outcome_one_pass",
                    "provider_calls_per_run": 1,
                    "serial_call_depth": 1,
                    "transfer_boundaries": 0,
                    "active_candidates_at_fan_in": 9,
                    "semantic_visibility": (
                        "complete conversation, original answer, nine full pressure "
                        "items, and answer task in one context"
                    ),
                    "estimated_prompt_tokens": collapsed_metrics[
                        "estimated_prompt_tokens"
                    ],
                    "prompt_fan_in_utf8_bytes": collapsed_metrics[
                        "user_prompt_utf8_bytes"
                    ],
                    "independent_disposition_effect_fields": 1,
                    "schema_properties": collapsed_metrics[
                        "response_schema_metrics"
                    ]["total_object_properties"],
                    "schema_bytes": collapsed_metrics["response_schema_metrics"][
                        "canonical_bytes"
                    ],
                    "maximum_estimated_cost_usd": collapsed_metrics[
                        "maximum_estimated_cost_usd"
                    ],
                    "exact_operational_cost_usd": None,
                    "exact_observed_failure_prevented_by_shape": True,
                    "latency_consequence": "one provider round trip",
                    "deterministic_semantic_leakage": False,
                    "new_failure_surface": "combined_label_can_still_be_semantically_wrong",
                },
                {
                    "alternative": "separated_disposition_then_synthesis",
                    "provider_calls_per_run": 2,
                    "serial_call_depth": 2,
                    "transfer_boundaries": 1,
                    "active_candidates_at_fan_in": 9,
                    "semantic_visibility": (
                        "disposition sees the complete packet; synthesis sees the complete "
                        "conversation, original answer, and frozen nine-row ledger"
                    ),
                    "estimated_prompt_tokens_by_serial_stage": [
                        disposition_metrics["estimated_prompt_tokens"],
                        synthesis_metrics["estimated_prompt_tokens"],
                    ],
                    "prompt_fan_in_utf8_bytes_by_serial_stage": [
                        disposition_metrics["user_prompt_utf8_bytes"],
                        synthesis_metrics["user_prompt_utf8_bytes"],
                    ],
                    "maximum_ledger_fan_in_bytes": canonical_json_bytes(stress_ledger),
                    "independent_disposition_effect_fields": 1,
                    "schema_properties": (
                        disposition_metrics["response_schema_metrics"][
                            "total_object_properties"
                        ]
                        + synthesis_metrics["response_schema_metrics"][
                            "total_object_properties"
                        ]
                    ),
                    "schema_bytes": (
                        disposition_metrics["response_schema_metrics"][
                            "canonical_bytes"
                        ]
                        + synthesis_metrics["response_schema_metrics"][
                            "canonical_bytes"
                        ]
                    ),
                    "maximum_estimated_cost_usd": split_cost,
                    "exact_operational_cost_usd": None,
                    "exact_observed_failure_prevented_by_shape": True,
                    "latency_consequence": (
                        "at least two sequential provider round trips plus local transfer"
                    ),
                    "deterministic_semantic_leakage": False,
                    "new_failure_surface": (
                        "second call plus ledger transfer and disposition absorption"
                    ),
                },
            ],
            "dimensions": [
                "responsibility_distribution",
                "cross_field_contradiction_surface",
                "semantic_visibility",
                "candidate_and_token_fan_in",
                "calls_cost_and_serial_latency",
                "custody_and_transfer_boundaries",
                "deterministic_semantic_leakage",
                "provider_acceptance_evidence",
            ],
            "scalar_quality_score": None,
        },
    )

    decision_artifact = _artifact(
        "decision",
        {
            "status": "redesign_wire_keep_one_pass_split_not_earned",
            "case_id": packet["case_id"],
            "decision": "select_collapsed_outcome_one_pass_for_future_empirical_test",
            "why": [
                "The only observed response failure is one disposition/effect conflict.",
                "Eight of nine returned rows had no mechanical finding; overload is unproven.",
                (
                    "One controlled outcome prevents that exact contradiction without "
                    "changing who judges applicability."
                ),
                (
                    "The collapsed design keeps all nine pressures, one call, and zero "
                    "transfer boundaries."
                ),
                (
                    "A split adds a second call and transfer fan-in before evidence "
                    "shows answer drafting caused the failure."
                ),
            ],
            "practices_adopted": [
                "validate schema-valid values locally and fail closed",
                "separate structural validity from semantic review",
                "collapse redundant controlled labels when mapping is exact",
                "measure fan-in and total call cost before adopting decomposition",
            ],
            "practices_rejected": [
                "post-hoc repair of the preserved provider response",
                "retry with validator feedback",
                "model shopping or premium escalation",
                "LLM judge or majority vote",
                "anyOf dependency for the exact OpenRouter Gemini 3.1 route without evidence",
                "two-call separation before a drafting-specific failure is observed",
                "deterministic inference of relevance or useful effect",
            ],
            "remaining_unknowns": [
                "whether the exact collapsed schema is accepted by the pinned route",
                "whether a cheap model chooses a source-grounded combined outcome",
                "whether a mechanically valid reconsidered answer adds non-forced value",
                "whether answer drafting causes over-absorption or bloat across cases",
            ],
            "future_experiment": {
                "status": "hypothesis_frozen_calls_not_authorized",
                "hypothesis": (
                    "On a prospectively frozen ambiguous multi-turn reliability case, "
                    "the collapsed one-pass contract returns all pressure outcomes under "
                    "mechanical custody without disposition/effect contradiction and "
                    "produces a source-reviewable answer."
                ),
                "required_case": (
                    "new safe ambiguous multi-turn case frozen before execution and not "
                    "used to alter the selected contract"
                ),
                "maximum_calls_if_separately_authorized_later": 1,
                "automatic_retries": 0,
                "fallbacks": 0,
                "response_healing": False,
                "premium_models": False,
                "current_provider_calls_authorized": 0,
                "success_gate": (
                    "mechanical pass followed by source-first vector review with at least "
                    "one non-forced contribution or valuable grounded rejection and no "
                    "unsupported leakage, private over-absorption, or public friction theater"
                ),
                "stop_rule": (
                    "Preserve the first failure. Do not automatically split, retry, or "
                    "change model. Reclassify the failure provider-free."
                ),
            },
            "r3_status": "redesign_selected_not_empirically_validated",
            "runtime_integration_authorized": False,
        },
    )

    artifacts = {
        "responsibility-map.json": responsibility_artifact,
        "failure-causal-audit.json": failure_artifact,
        "counterfactual-contracts.json": contracts_artifact,
        "comparison-vector.json": comparison_artifact,
        "decision.json": decision_artifact,
    }
    for name, artifact in artifacts.items():
        _write(output / name, artifact)

    sources = [
        BASE_CONTRACT,
        BASE_AUTHORIZATION,
        CALL_RESULT,
        FAILURE_CLOSEOUT,
        CURRENT_PRACTICE,
        MODULE,
        BUILDER,
    ]
    summary: dict[str, Any] = {
        "schema_version": SUMMARY_SCHEMA,
        "status": "r3_task_shape_reassessment_complete_provider_free",
        "case_id": packet["case_id"],
        "base_run_id": contract["run_id"],
        "frozen_inputs": [
            {"path": _relative(path), "sha256": _file_sha(path)} for path in sources
        ],
        "artifacts": [
            {
                "path": _relative(output / name),
                "file_sha256": _file_sha(output / name),
                "value_sha256": artifact["artifact_sha256"],
                "artifact_kind": artifact["artifact_kind"],
            }
            for name, artifact in artifacts.items()
        ],
        "selected_design": "collapsed_outcome_one_pass",
        "split_design_status": "not_earned_by_current_evidence",
        "provider_calls": 0,
        "next_call_authorized": False,
        "runtime_effect": "none",
        "semantic_applicability_inferred_by_code": False,
    }
    summary["summary_sha256"] = value_sha256(summary)
    _write(output / "summary.json", summary)
    return summary


def validate(output: Path) -> dict[str, Any]:
    summary = _load(output / "summary.json")
    observed = summary.get("summary_sha256")
    without = {key: value for key, value in summary.items() if key != "summary_sha256"}
    if observed != value_sha256(without):
        raise R3TaskShapeBuildError("summary self-hash drifted")
    if (
        summary.get("status") != "r3_task_shape_reassessment_complete_provider_free"
        or summary.get("provider_calls") != 0
        or summary.get("next_call_authorized") is not False
        or summary.get("runtime_effect") != "none"
    ):
        raise R3TaskShapeBuildError("summary boundary drifted")
    for item in summary.get("frozen_inputs", []):
        path = ROOT / item["path"]
        if _file_sha(path) != item["sha256"]:
            raise R3TaskShapeBuildError(f"frozen input drifted: {item['path']}")
    for item in summary.get("artifacts", []):
        path = ROOT / item["path"]
        value = _load(path)
        if (
            _file_sha(path) != item["file_sha256"]
            or value.get("artifact_sha256") != item["value_sha256"]
            or value_sha256(
                {key: val for key, val in value.items() if key != "artifact_sha256"}
            )
            != value["artifact_sha256"]
            or value.get("provider_calls") != 0
            or value.get("next_call_authorized") is not False
        ):
            raise R3TaskShapeBuildError(f"artifact custody drifted: {item['path']}")
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    summary = validate(output) if args.validate_only else build(output)
    print(
        json.dumps(
            {
                "status": summary["status"],
                "selected_design": summary["selected_design"],
                "provider_calls": summary["provider_calls"],
                "next_call_authorized": summary["next_call_authorized"],
                "summary_sha256": summary["summary_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
