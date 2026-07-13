#!/usr/bin/env python3
"""Seal the provider-free R3 collapsed-outcome execution decision package."""

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

from scripts.evals import (  # noqa: E402
    build_r3_collapsed_outcome_case_selection as selection,
)
from scripts.evals.run_r3_collapsed_outcome_case import (  # noqa: E402
    AUTHORIZATION_SCHEMA,
    CASE_ID,
    EXECUTION_CONTRACT_SCHEMA,
    MODEL,
    REVIEW,
    RUN_ID,
    validate_execution_contract,
)


CONTRACT = ROOT / "docs/evals/lolla-r3-collapsed-outcome-case-execution-contract-v1.json"
AUTHORIZATION_TEMPLATE = ROOT / (
    "docs/evals/lolla-r3-collapsed-outcome-case-authorization-template-v1.json"
)
CURRENT_PRACTICE = ROOT / (
    "docs/conversation-understanding/"
    "lolla-r3-collapsed-outcome-current-practice-2026-07-13.md"
)
PREPARATION = ROOT / (
    "research/lolla-r3-collapsed-outcome-case-2026-07-13/preparation"
)
DECISION_NAME = "founder-decision.json"
SUMMARY_NAME = "preparation-summary.json"
RUNNER = ROOT / "scripts/evals/run_r3_collapsed_outcome_case.py"
BUILDER = ROOT / "scripts/evals/build_r3_collapsed_outcome_case_execution.py"
PROVIDER_BUDGET = ROOT / "engine/system_b/provider_budget.py"
TASK_SHAPE = ROOT / "engine/system_b/r3_task_shape_counterfactual.py"
REVIEW_COMMIT = "61da9dcd28090510ceec7aa70f339273ccdff1d2"


class R3CollapsedExecutionBuildError(RuntimeError):
    """Raised when the prospective one-call package cannot be sealed."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R3CollapsedExecutionBuildError(f"expected JSON object: {path}")
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


def construct() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    selection.validate(selection.SELECTION.parent)
    artifacts = selection.construct(include_runtime=True)
    bundle = artifacts[selection.BUNDLE_NAME]
    summary = artifacts[selection.SUMMARY_NAME]
    runtime = artifacts["_runtime_material"]
    review = _load(REVIEW)
    if review.get("pressure_selection_commit") != (
        "89ca89d7dcebfef7fa79b42993efdcbb913c8349"
    ):
        raise R3CollapsedExecutionBuildError("review lost selection chronology")
    if summary.get("next_call_authorized") is not False:
        raise R3CollapsedExecutionBuildError("selection unexpectedly authorized work")
    maximum_estimated = runtime["request_contract"][
        "maximum_estimated_call_cost_usd"
    ]
    if maximum_estimated > 0.01:
        raise R3CollapsedExecutionBuildError("request exceeds one-cent envelope")
    frozen_inputs = [
        selection.SOURCE,
        selection.SOURCE_FREEZE,
        selection.SELECTION,
        selection.SELECTION.parent / selection.RESULT_NAME,
        selection.SELECTION.parent / selection.BUNDLE_NAME,
        selection.SELECTION.parent / selection.SUMMARY_NAME,
        selection.KNOWLEDGE,
        selection.RELATIONSHIPS,
        selection.BUILDER,
        REVIEW,
        CURRENT_PRACTICE,
        TASK_SHAPE,
        PROVIDER_BUDGET,
        RUNNER,
        BUILDER,
    ]
    request_body = runtime["request_body"]
    provider = request_body["provider"]
    contract: dict[str, Any] = {
        "schema_version": EXECUTION_CONTRACT_SCHEMA,
        "status": "frozen_awaiting_founder_authorization",
        "date": "2026-07-13",
        "run_id": RUN_ID,
        "case_id": CASE_ID,
        "case_kind": "prospectively_authored_synthetic_reliability_case",
        "freeze_chronology": {
            "source_commit": summary["source_freeze_commit"],
            "pressure_selection_commit": review["pressure_selection_commit"],
            "protected_review_commit": REVIEW_COMMIT,
            "source_preceded_pressure_selection": True,
            "pressure_selection_preceded_protected_review": True,
            "protected_review_preceded_provider_execution": True,
        },
        "frozen_inputs": [
            {"path": _relative(path), "sha256": _file_sha(path)}
            for path in frozen_inputs
        ],
        "selection": {
            "bundle_path": _relative(
                selection.SELECTION.parent / selection.BUNDLE_NAME
            ),
            "bundle_file_sha256": _file_sha(
                selection.SELECTION.parent / selection.BUNDLE_NAME
            ),
            "bundle_sha256": bundle["bundle_sha256"],
            "active_pressure_count": len(summary["active_pressure_ids"]),
            "direct_count": summary["path_counts"]["direct_active"],
            "graph_count": summary["path_counts"]["graph_active"],
            "candidate_deletion": False,
        },
        "protected_review": {
            "path": _relative(REVIEW),
            "sha256": _file_sha(REVIEW),
            "supplied_to_provider": False,
            "review_only_after_mechanical_pass": True,
            "not_an_answer_key": True,
            "independent_human_gold": False,
        },
        "request_attestation": {
            **bundle["hashes"],
            "bundle_sha256": bundle["bundle_sha256"],
            "packet_sha256": bundle["packet_sha256"],
        },
        "operator": {
            "provider": "openrouter",
            "endpoint": runtime["request_contract"]["endpoint"],
            "model": MODEL,
            "provider_order": provider["order"],
            "provider_only": provider["only"],
            "allow_fallbacks": provider["allow_fallbacks"],
            "require_parameters": provider["require_parameters"],
            "data_collection": provider["data_collection"],
            "zdr_claimed": False,
            "wire_mode": "strict_json_schema",
            "reasoning_effort": request_body["reasoning"]["effort"],
            "reasoning_content_excluded": request_body["reasoning"]["exclude"],
            "seed": request_body["seed"],
            "maximum_output_tokens": request_body["max_tokens"],
        },
        "price_guard": {
            "maximum_prompt_price_per_million_usd": provider["max_price"][
                "prompt"
            ],
            "maximum_completion_price_per_million_usd": provider["max_price"][
                "completion"
            ],
            "current_practice_path": _relative(CURRENT_PRACTICE),
            "checked_on": "2026-07-13",
        },
        "budget": {
            "maximum_provider_calls": 1,
            "maximum_provider_reported_cost_usd": 0.01,
            "maximum_estimated_call_cost_usd": maximum_estimated,
            "automatic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "premium_models": 0,
            "quiet_control_calls": 0,
        },
        "execution_policy": {
            "explicit_execute_flag_required": True,
            "separate_exact_authorization_required": True,
            "durable_budget_reservation_before_transport": True,
            "started_record_before_transport": True,
            "exact_json_only": True,
            "collapsed_outcome_compiler_required": True,
            "complete_nine_pressure_coverage_required": True,
            "raw_payload_or_failure_preserved": True,
            "private_provider_identifiers_excluded_from_git": True,
            "source_review_only_after_mechanical_pass": True,
            "protected_review_never_supplied_to_provider": True,
            "first_failure_stops": True,
            "semantic_failure_allows_retry": False,
        },
        "decision_state": {
            "founder_decision": "pending",
            "provider_calls_made": 0,
            "provider_calls_authorized_now": 0,
            "execution_requires_separate_authorization": True,
            "available_account_balance_does_not_expand_budget": True,
        },
        "success_interpretation": {
            "mechanical_pass_required_before_source_review": True,
            "minimum_semantic_signal": (
                "one_non_forced_source_grounded_contribution_or_valuable_"
                "grounded_rejection"
            ),
            "recommendation_change_required": False,
            "graph_application_required": False,
            "public_pressure_dump_allowed": False,
            "scalar_quality_score": None,
        },
        "stop_rule": (
            "Preserve the first transport, provider, mechanical, cost, or semantic "
            "result. Do not retry, heal, switch model/provider, run a judge, run a "
            "quiet control, or alter frozen source, pressure, or review targets."
        ),
        "non_claims": [
            "provider_acceptance_is_not_known_before_execution",
            "mechanical_validity_is_not_semantic_quality",
            "protected_review_is_not_independent_human_gold",
            "one_semantic_pass_would_not_prove_product_reliability",
            "a_valuable_rejection_does_not_prove_graph_relevance_in_general",
            "available_account_balance_does_not_expand_this_budget",
        ],
    }
    authorization_template = {
        "schema_version": AUTHORIZATION_SCHEMA,
        "status": "not_authorized_template",
        "founder_decision": "not_decided",
        "authorization_basis": "",
        "contract_path": _relative(CONTRACT),
        "contract_sha256": "",
        "authorized_run_id": RUN_ID,
        "authorized_case_id": CASE_ID,
        "maximum_provider_calls": 1,
        "maximum_provider_reported_cost_usd": 0.01,
        "automatic_retries": 0,
        "fallback_models": 0,
        "response_healing": False,
        "premium_models_authorized": False,
        "quiet_control_authorized": False,
        "model_switch_authorized": False,
        "llm_judge_authorized": False,
    }
    decision = {
        "schema_version": "lolla.r3_collapsed_outcome_founder_decision.v1",
        "status": "founder_decision_required_after_provider_free_gates",
        "case_id": CASE_ID,
        "provider_calls_made": 0,
        "provider_calls_authorized": 0,
        "decision": "pending",
        "choice_authorize": {
            "meaning": "execute_exactly_one_frozen_gemini_flash_lite_call",
            "maximum_cost_usd": 0.01,
            "automatic_follow_on_calls": 0,
        },
        "choice_decline": {
            "meaning": "preserve_the_provider_free_package_and_defer_r3_evidence",
            "cost_usd": 0.0,
        },
        "what_the_call_can_answer": [
            "whether_the_collapsed_wire_contract_passes_mechanical_custody_once",
            "whether_the_result_contains_non_forced_source_grounded_friction_or_restraint",
        ],
        "what_the_call_cannot_answer": [
            "product_reliability",
            "real_user_usefulness",
            "correct_business_advice",
            "whether_a_premium_model_would_be_better",
        ],
    }
    return contract, authorization_template, decision


def build() -> dict[str, Any]:
    contract, authorization_template, decision = construct()
    _write(CONTRACT, contract)
    authorization_template["contract_sha256"] = _file_sha(CONTRACT)
    _write(AUTHORIZATION_TEMPLATE, authorization_template)
    _write(PREPARATION / DECISION_NAME, decision)
    validate_execution_contract(CONTRACT)
    summary = {
        "schema_version": "lolla.r3_collapsed_outcome_preparation_summary.v1",
        "status": "provider_free_gates_passed_founder_decision_required",
        "case_id": CASE_ID,
        "provider_calls_made": 0,
        "provider_calls_authorized": 0,
        "maximum_future_call_cost_usd_if_authorized": 0.01,
        "maximum_estimated_call_cost_usd": contract["budget"][
            "maximum_estimated_call_cost_usd"
        ],
        "contract": {
            "path": _relative(CONTRACT),
            "sha256": _file_sha(CONTRACT),
        },
        "authorization_template": {
            "path": _relative(AUTHORIZATION_TEMPLATE),
            "sha256": _file_sha(AUTHORIZATION_TEMPLATE),
            "authorizes_execution": False,
        },
        "decision": {
            "path": _relative(PREPARATION / DECISION_NAME),
            "sha256": _file_sha(PREPARATION / DECISION_NAME),
        },
        "review": {
            "path": _relative(REVIEW),
            "sha256": _file_sha(REVIEW),
            "hidden_from_provider": True,
        },
        "request_body_sha256": contract["request_attestation"][
            "request_body_sha256"
        ],
        "stop_rule": contract["stop_rule"],
    }
    summary["summary_sha256"] = value_sha256(summary)
    _write(PREPARATION / SUMMARY_NAME, summary)
    return summary


def value_sha256(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate() -> dict[str, Any]:
    expected_contract, expected_template, expected_decision = construct()
    if _load(CONTRACT) != expected_contract:
        raise R3CollapsedExecutionBuildError("execution contract drifted")
    expected_template["contract_sha256"] = _file_sha(CONTRACT)
    if _load(AUTHORIZATION_TEMPLATE) != expected_template:
        raise R3CollapsedExecutionBuildError("authorization template drifted")
    if _load(PREPARATION / DECISION_NAME) != expected_decision:
        raise R3CollapsedExecutionBuildError("founder decision artifact drifted")
    validate_execution_contract(CONTRACT)
    summary = _load(PREPARATION / SUMMARY_NAME)
    observed = summary.get("summary_sha256")
    without_hash = {key: value for key, value in summary.items() if key != "summary_sha256"}
    if observed != value_sha256(without_hash):
        raise R3CollapsedExecutionBuildError("preparation summary hash drifted")
    for key in ("contract", "authorization_template", "decision", "review"):
        item = summary[key]
        if _file_sha(ROOT / item["path"]) != item["sha256"]:
            raise R3CollapsedExecutionBuildError(f"summary artifact drifted: {key}")
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    summary = validate() if args.validate_only else build()
    print(
        json.dumps(
            {
                "status": summary["status"],
                "provider_calls_made": summary["provider_calls_made"],
                "provider_calls_authorized": summary["provider_calls_authorized"],
                "maximum_estimated_call_cost_usd": summary[
                    "maximum_estimated_call_cost_usd"
                ],
                "summary_sha256": summary["summary_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
