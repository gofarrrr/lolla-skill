"""Freeze and consolidate the bounded graph-variance calibration.

This deterministic helper validates the four first-attempt generation states,
builds five neutrally named comparison cases plus the existing reviewer
controls, and fans two blind reviews into a non-scalar diagnostic. A failed
first terminal attempt remains failed: the helper does not retry, heal, replace,
or impute it. It does not call a provider, traverse the graph, judge answer
quality, or change runtime.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_increment_rehearsal import (
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
)
from engine.system_b.product_delta_graph_variance_calibration import (
    CALIBRATION_ID,
    DEFAULT_GENERATION_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH,
    ProductDeltaGraphVarianceCalibrationError,
    validate_checked_in_calibration,
)
from engine.system_b.product_delta_paired_screen import (
    DEFAULT_BLIND_PACKETS_RELPATH as CONTROL_BLIND_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH as CONTROL_SEALED_MANIFEST_RELPATH,
    validate_checked_in_screen,
)
from engine.system_b.product_delta_paired_screen_review import (
    COGNITIVE_EFFECT_VALUES,
    MATERIAL_DIFFERENCE_VALUES,
    PRESENCE_VALUES,
    QUALIFICATION_DISPOSITIONS,
    REASONING_OPERATION_VALUES,
    SOURCE_GROUNDING_VALUES,
    STANDDOWN_SUPPORT_VALUES,
)
from engine.system_b.simulated_reliability_v1 import (
    SimulatedReliabilityError,
    compile_pressure_response,
)


BLIND_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_graph_variance_blind_review_packet.v1"
)
EXECUTION_SEALED_SCHEMA_VERSION = (
    "lolla.product_delta_graph_variance_execution_sealed_manifest.v1"
)
REVIEW_SCHEMA_VERSION = (
    "lolla.product_delta_graph_variance_fresh_agent_review.v1"
)
CONSOLIDATION_SCHEMA_VERSION = (
    "lolla.product_delta_graph_variance_agent_consolidation.v1"
)
FAILURE_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_variance_generation_failure.v1"
)
BLINDING_NAMESPACE = "lolla-product-delta-graph-variance-result-v1"
OUTPUT_DIR_RELPATH = (
    "research/agent-only-graph-variance-calibration-2026-07-23"
)
REVIEW_DIR_RELPATH = (
    "reviews/codex-assisted/agent-only-graph-variance-calibration-v1"
)
SOURCE_RELPATH = (
    "research/independent-phase5-cases-2026-07-12/useful-pressure-case.txt"
)
PORTFOLIO_BUNDLE_RELPATH = (
    "research/consumer-context-role-attribution-case-candidate-2026-07-23/"
    "portfolio-bundle.json"
)
BLIND_REVIEW_PACKET_RELPATH = f"{OUTPUT_DIR_RELPATH}/blind-review-packet.json"
EXECUTION_SEALED_MANIFEST_RELPATH = (
    f"{OUTPUT_DIR_RELPATH}/execution-sealed-manifest.json"
)
CONSOLIDATION_RELPATH = f"{OUTPUT_DIR_RELPATH}/consolidated-diagnostic.json"
FAILURE_RELPATHS = {
    "sample-moss": f"{OUTPUT_DIR_RELPATH}/terminal-failure-sample-moss.json",
}
REVIEW_RELPATHS = {
    "primary": f"{REVIEW_DIR_RELPATH}/pair-review-primary.json",
    "skeptical": f"{REVIEW_DIR_RELPATH}/pair-review-skeptical.json",
}
EXPECTED_REVIEW_IDS = {
    "primary": "agent-graph-variance-pair-primary-v1",
    "skeptical": "agent-graph-variance-pair-skeptical-v1",
}
CONDITION_TO_BUNDLE_ARM = {
    REHEARSAL_DIRECT: "direct_pressure",
    REHEARSAL_DIRECT_PLUS_ONE_HOP: "graph_expanded_pressure",
}
COMPARISON_CASE_IDS = (
    "calibration-pair-01",
    "calibration-pair-02",
    "calibration-pair-03",
    "calibration-pair-04",
    "calibration-pair-05",
)
BOUNDARY = {
    "repository_provider_api_calls": 0,
    "repository_provider_api_cost_usd": 0.0,
    "repository_provider_execution_authorized": False,
    "codex_generation_contexts_attempted": 4,
    "codex_blind_review_contexts_predeclared": 2,
    "codex_contexts_called_no_ai_calls_or_economically_free": False,
    "codex_platform_route_token_and_cost": "unavailable_to_repository_operator",
    "human_review_completed": False,
    "private_archives_read": False,
    "answer_quality_scored": False,
    "winner_selected": False,
    "graph_traversal_invoked": False,
    "graph_policy_changed": False,
    "planner_changed": False,
    "compiler_changed": False,
    "runtime_invoked": False,
    "live_skill_invoked": False,
    "graph_causation_established": False,
    "graph_relevance_established": False,
    "human_usefulness_established": False,
}
NON_CLAIMS = [
    "not principal-human review",
    "not provider execution or an exact standalone provider envelope",
    "not a provider or model comparison",
    "not a statistically powered variance estimate",
    "not graph causation, relevance, value, or usefulness evidence",
    "not proof that either answer is better",
    "not expected model behavior",
    "not completion of F2 or F3",
    "not permission to expand traversal",
    "not a live skill, runtime, planner, compiler, graph, or interface change",
]
SECRET_MARKERS = (
    "/Users/",
    "\\Users\\",
    "BEGIN PRIVATE KEY",
    "client_secret",
    '"api_key"',
    '"password"',
    "sk-proj-",
)
SEALED_LINEAGE_MARKERS = (
    "sample-cinder",
    "sample-linen",
    "sample-moss",
    "sample-slate",
    "within-direct-fresh",
    "within-graph-fresh",
    "cross-historical",
    "cross-fresh-1",
    "cross-fresh-2",
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
)


class ProductDeltaGraphVarianceResultError(ValueError):
    """Sanitized deterministic graph-variance result custody failure."""


def build_blind_review_inputs(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the blind packet and separately sealed execution lineage."""

    root = Path(repo_root).resolve()
    _validate_frozen_inputs(root)
    source, source_ref = _read_text_ref(root, SOURCE_RELPATH)
    generation, generation_ref = _read_json_ref(
        root, DEFAULT_GENERATION_PACKETS_RELPATH
    )
    preoutput_sealed, preoutput_ref = _read_json_ref(
        root, DEFAULT_SEALED_MANIFEST_RELPATH
    )
    controls, controls_ref = _read_json_ref(
        root, CONTROL_BLIND_PACKETS_RELPATH
    )
    _, controls_sealed_ref = _read_json_ref(
        root, CONTROL_SEALED_MANIFEST_RELPATH
    )
    bundle, bundle_ref = _read_json_ref(root, PORTFOLIO_BUNDLE_RELPATH)

    states, state_refs, compile_receipts = _validate_generation_states(
        root=root,
        generation=generation,
        preoutput_sealed=preoutput_sealed,
        bundle=bundle,
    )
    comparison_cases, sealed_pairs = _build_comparison_cases(
        root=root,
        source_ref=source_ref,
        preoutput_sealed=preoutput_sealed,
        states=states,
        state_refs=state_refs,
    )

    qualification_cases = copy.deepcopy(
        _required_list(controls, "qualification_cases")
    )
    control_pairs = _required_list(controls, "paired_cases")
    duplicate_null = next(
        (
            copy.deepcopy(item)
            for item in control_pairs
            if isinstance(item, Mapping)
            and item.get("evidence_class") == "exact_duplicate_null"
        ),
        None,
    )
    standdown_cases = copy.deepcopy(
        _required_list(controls, "standdown_cases")
    )
    if not isinstance(duplicate_null, dict):
        raise ProductDeltaGraphVarianceResultError(
            "existing exact-duplicate null is missing"
        )
    if len(qualification_cases) != 10 or len(standdown_cases) != 1:
        raise ProductDeltaGraphVarianceResultError(
            "existing reviewer control count drifted"
        )

    available_case_ids = [
        str(item["case_id"])
        for item in comparison_cases
        if item["review_status_required"] == "reviewed"
    ]
    unavailable_case_ids = [
        str(item["case_id"])
        for item in comparison_cases
        if item["review_status_required"] == "not_evaluable"
    ]
    qualification_ids = _case_ids(qualification_cases)
    standdown_ids = _case_ids(standdown_cases)
    duplicate_id = str(duplicate_null["case_id"])
    blind: dict[str, Any] = {
        "schema_version": BLIND_PACKET_SCHEMA_VERSION,
        "calibration_id": CALIBRATION_ID,
        "status": (
            "blind_review_inputs_frozen_with_one_generation_failure"
        ),
        "purpose": (
            "Inspect the exact-duplicate null and every evaluable neutral "
            "comparison while preserving unavailable comparisons as "
            "not-evaluable first-terminal failures."
        ),
        "boundary": copy.deepcopy(BOUNDARY),
        "authoritative_source": {
            "coverage": "complete_checked_in_conversation",
            "content": source,
            "content_sha256": source_ref["sha256"],
            "known_limit": (
                "This is a synthetic checked-in case and cannot establish "
                "human usefulness."
            ),
        },
        "review_order": [
            "Answer every qualification case before reviewing answer pairs.",
            "Read the authoritative source before either arm.",
            "Review the exact-duplicate null before calibration comparisons.",
            "For available pairs, compare atomic reasoning moves rather than fluency, length, or polish.",
            "For unavailable pairs, record not_evaluable without inventing, imputing, or comparing an arm.",
            "Preserve source value, lost value, unsupported additions, burden, and uncertainty separately.",
            "Review the legitimate stand-down independently.",
            "Do not rank, score, vote, certify, select a winner, or infer lineage.",
        ],
        "visibility": {
            "condition_lineage_included": False,
            "pair_roles_included": False,
            "sample_aliases_included": False,
            "candidate_dispositions_included": False,
            "sibling_review_included": False,
        },
        "review_contract": {
            "qualification_response_shape": copy.deepcopy(
                controls["review_contract"]["qualification_response_shape"]
            ),
            "available_pair_response_shape": _available_pair_shape(),
            "unavailable_pair_response_shape": {
                "case_id": "string",
                "review_status": "not_evaluable",
                "semantic_comparison_attempted": False,
                "unavailability_basis": [
                    "first_terminal_generation_result_unavailable"
                ],
            },
            "standdown_response_shape": copy.deepcopy(
                controls["review_contract"]["standdown_response_shape"]
            ),
            "forbidden_review_behavior": [
                "Do not select a better arm.",
                "Do not emit a score, ranking, vote, pass/fail, certification, or product recommendation.",
                "Do not infer condition, pair role, sample lineage, or graph lineage.",
                "Do not compare, reconstruct, or impute an unavailable arm.",
                "Do not treat a clean schema or reviewer agreement as semantic correctness.",
                "Do not claim graph causation, relevance, value, human usefulness, or production readiness.",
            ],
        },
        "response_envelope_contract": {
            "schema_version": REVIEW_SCHEMA_VERSION,
            "review_id": "Use the exact ID in the fresh-context task wrapper.",
            "fresh_context": True,
            "saw_lineage_before_freeze": False,
            "saw_sibling_review_before_freeze": False,
            "qualification_case_ids": qualification_ids,
            "duplicate_null_case_id": duplicate_id,
            "comparison_case_ids": list(COMPARISON_CASE_IDS),
            "available_comparison_case_ids": available_case_ids,
            "unavailable_comparison_case_ids": unavailable_case_ids,
            "standdown_case_ids": standdown_ids,
            "boundary": _review_boundary(),
        },
        "qualification_cases": qualification_cases,
        "exact_duplicate_null": duplicate_null,
        "comparison_case_count": 5,
        "comparison_cases": comparison_cases,
        "standdown_cases": standdown_cases,
        "non_claims": list(NON_CLAIMS),
    }
    blind_rendered = render_json(blind)
    sealed: dict[str, Any] = {
        "schema_version": EXECUTION_SEALED_SCHEMA_VERSION,
        "calibration_id": CALIBRATION_ID,
        "status": (
            "three_generation_outputs_valid_one_first_terminal_failure_"
            "blind_inputs_frozen"
        ),
        "handling": {
            "show_to_generation_agents": False,
            "show_to_blind_reviewers": False,
            "unblind_only_after_both_reviews_are_frozen": True,
            "failed_sample_retried_healed_replaced_or_imputed": False,
        },
        "boundary": copy.deepcopy(BOUNDARY),
        "input_refs": {
            "authoritative_source": source_ref,
            "generation_packets": generation_ref,
            "preoutput_sealed_manifest": preoutput_ref,
            "control_blind_packets": controls_ref,
            "control_sealed_manifest": controls_sealed_ref,
            "portfolio_bundle": bundle_ref,
            "generation_states": state_refs,
        },
        "generation_state_validation": compile_receipts,
        "comparison_lineage": sealed_pairs,
        "blind_review_packet": {
            "path": BLIND_REVIEW_PACKET_RELPATH,
            "sha256": _sha256_text(blind_rendered),
            "bytes": len(blind_rendered.encode("utf-8")),
        },
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe_generated({"blind": blind, "sealed": sealed})
    return blind, sealed


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_blind_review_inputs(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    for relpath, payload in zip(
        (BLIND_REVIEW_PACKET_RELPATH, EXECUTION_SEALED_MANIFEST_RELPATH),
        build_blind_review_inputs(repo_root=root),
        strict=True,
    ):
        path = _resolve_repo_path(root, relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_blind_review_inputs(
    *, repo_root: Path | str
) -> list[str]:
    root = Path(repo_root).resolve()
    errors: list[str] = []
    for relpath, payload in zip(
        (BLIND_REVIEW_PACKET_RELPATH, EXECUTION_SEALED_MANIFEST_RELPATH),
        build_blind_review_inputs(repo_root=root),
        strict=True,
    ):
        try:
            actual = _resolve_repo_path(root, relpath).read_text(
                encoding="utf-8"
            )
        except OSError:
            errors.append(f"missing generated artifact:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"generated artifact drift:{relpath}")
    return errors


def import_frozen_review(
    *,
    repo_root: Path | str,
    lane: str,
    source_path: Path | str,
) -> None:
    """Validate and preserve one external first-terminal blind review verbatim."""

    root = Path(repo_root).resolve()
    if lane not in REVIEW_RELPATHS:
        raise ProductDeltaGraphVarianceResultError(
            "unknown graph-variance review lane"
        )
    if validate_checked_in_blind_review_inputs(repo_root=root):
        raise ProductDeltaGraphVarianceResultError(
            "blind review input custody drifted"
        )
    blind, _ = _read_json_ref(root, BLIND_REVIEW_PACKET_RELPATH)
    source = Path(source_path).resolve()
    try:
        raw = source.read_bytes()
        payload = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProductDeltaGraphVarianceResultError(
            "external blind review is not valid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphVarianceResultError(
            "external blind review is not an object"
        )
    errors = _validate_review(
        payload,
        path=f"external-{lane}-review",
        expected_review_id=EXPECTED_REVIEW_IDS[lane],
        blind=blind,
    )
    if errors:
        raise ProductDeltaGraphVarianceResultError(
            f"external blind review failed validation with {len(errors)} error(s)"
        )
    target = _resolve_repo_path(root, REVIEW_RELPATHS[lane])
    if target.exists():
        raise ProductDeltaGraphVarianceResultError(
            "frozen blind review already exists; overwrite forbidden"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def build_review_consolidation(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], list[str]]:
    """Validate both reviews and preserve observations without adjudication."""

    root = Path(repo_root).resolve()
    if validate_checked_in_blind_review_inputs(repo_root=root):
        raise ProductDeltaGraphVarianceResultError(
            "blind review input custody drifted"
        )
    blind, blind_ref = _read_json_ref(root, BLIND_REVIEW_PACKET_RELPATH)
    sealed, sealed_ref = _read_json_ref(
        root, EXECUTION_SEALED_MANIFEST_RELPATH
    )
    review_payloads: dict[str, dict[str, Any]] = {}
    review_refs: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for lane, relpath in REVIEW_RELPATHS.items():
        payload, ref = _read_json_ref(root, relpath)
        review_payloads[lane] = payload
        review_refs[lane] = ref
        errors.extend(
            _validate_review(
                payload,
                path=relpath,
                expected_review_id=EXPECTED_REVIEW_IDS[lane],
                blind=blind,
            )
        )

    comparison_cases = _required_list(blind, "comparison_cases")
    comparison_by_id = _index_cases(comparison_cases)
    comparison_lineage = _required_mapping(sealed, "comparison_lineage")
    comparison_fan_in: list[dict[str, Any]] = []
    for case_id in COMPARISON_CASE_IDS:
        blind_case = _required_mapping(comparison_by_id, case_id)
        reads = []
        for lane, payload in review_payloads.items():
            review = _required_mapping(
                _index_cases(_required_list(payload, "comparison_reviews")),
                case_id,
            )
            reads.append(
                {
                    "review_id": payload["review_id"],
                    "lane": lane,
                    **copy.deepcopy(dict(review)),
                }
            )
        comparison_fan_in.append(
            {
                "case_id": case_id,
                "availability": blind_case["availability"],
                "lineage_revealed_after_both_reviews_froze": copy.deepcopy(
                    comparison_lineage[case_id]
                ),
                "reviewer_reads": reads,
                "fan_in_policy": (
                    "Reads remain side by side; agreement is not truth and "
                    "disagreement is not resolved by ranking, voting, or averaging."
                ),
            }
        )

    qualification_ids = _case_ids(
        _required_list(blind, "qualification_cases")
    )
    qualification_fan_in = [
        {
            "case_id": case_id,
            "reviewer_reads": [
                {
                    "review_id": payload["review_id"],
                    **copy.deepcopy(
                        dict(
                            _required_mapping(
                                _index_cases(
                                    _required_list(
                                        payload, "qualification_reviews"
                                    )
                                ),
                                case_id,
                            )
                        )
                    ),
                }
                for payload in review_payloads.values()
            ],
        }
        for case_id in qualification_ids
    ]
    duplicate_id = str(
        _required_mapping(blind, "exact_duplicate_null")["case_id"]
    )
    duplicate_reads = [
        {
            "review_id": payload["review_id"],
            **copy.deepcopy(
                dict(_required_mapping(payload, "duplicate_null_review"))
            ),
        }
        for payload in review_payloads.values()
    ]
    standdown_ids = _case_ids(_required_list(blind, "standdown_cases"))
    standdown_fan_in = [
        {
            "case_id": case_id,
            "reviewer_reads": [
                {
                    "review_id": payload["review_id"],
                    **copy.deepcopy(
                        dict(
                            _required_mapping(
                                _index_cases(
                                    _required_list(
                                        payload, "standdown_reviews"
                                    )
                                ),
                                case_id,
                            )
                        )
                    ),
                }
                for payload in review_payloads.values()
            ],
        }
        for case_id in standdown_ids
    ]

    unavailable = [
        item["case_id"]
        for item in comparison_fan_in
        if item["availability"] != "available"
    ]
    available = [
        item["case_id"]
        for item in comparison_fan_in
        if item["availability"] == "available"
    ]
    consolidation: dict[str, Any] = {
        "schema_version": CONSOLIDATION_SCHEMA_VERSION,
        "calibration_id": CALIBRATION_ID,
        "status": (
            "valid_frozen_agent_diagnostic_not_evaluable_terminal_failure"
            if not errors
            else "invalid_review_shape_first_terminal_states_preserved"
        ),
        "boundary": {
            **copy.deepcopy(BOUNDARY),
            "codex_blind_review_contexts_completed": 2,
            "principal_human_review_completed": False,
            "semantic_adjudication_performed": False,
            "scalar_summary_created": False,
            "permission_to_expand_graph_created": False,
        },
        "input_refs": {
            "blind_review_packet": blind_ref,
            "execution_sealed_manifest": sealed_ref,
            "blind_reviews": review_refs,
        },
        "validation": {
            "error_count": len(errors),
            "errors": errors,
            "shape_custody_and_declared_enum_validation_only": True,
            "semantic_correctness_validated": False,
        },
        "isolation_receipt": {
            "generation_contexts_attempted": 4,
            "generation_first_terminal_outputs_complete": 3,
            "generation_first_terminal_failures": 1,
            "generation_retries_fallbacks_healing_replacements_or_imputations": 0,
            "blind_review_contexts_completed": 2,
            "reviewers_saw_lineage_before_freeze": False,
            "reviewers_saw_each_other_before_freeze": False,
            "codex_platform_route_token_and_cost": (
                "unavailable_to_repository_operator"
            ),
        },
        "qualification_reviews": qualification_fan_in,
        "duplicate_null_review": {
            "case_id": duplicate_id,
            "reviewer_reads": duplicate_reads,
            "control_only": True,
        },
        "comparison_reviews": comparison_fan_in,
        "standdown_reviews": standdown_fan_in,
        "calibration_interpretation": {
            "state": "not_evaluable",
            "available_comparison_case_ids": available,
            "unavailable_comparison_case_ids": unavailable,
            "reason": (
                "One direct-condition fresh draw has no recoverable first "
                "terminal result. The predeclared within-direct comparison and "
                "one predeclared cross-condition comparison are therefore "
                "unavailable. The frozen question requires both within-condition "
                "comparisons and all three cross-condition comparisons, so the "
                "cross-condition pattern cannot be compared with the full "
                "observed within-condition variation."
            ),
            "available_reviews_remain_inspectable": True,
            "failed_draw_retried_healed_replaced_or_imputed": False,
            "no_graph_decision_created": True,
            "interpretation_limit": (
                "This is a bounded automation and variance-calibration result, "
                "not a score, winner, answer-quality result, graph-value estimate, "
                "expected-model-behavior claim, or substitute for a person."
            ),
        },
        "fan_in_policy": [
            "No reviewer is authoritative.",
            "Qualification reads remain case-by-case rather than becoming a score.",
            "The duplicate null and stand-down are controls, not proof of calibration.",
            "Available comparison observations remain attributable to each reviewer.",
            "Unavailable comparisons remain not evaluable rather than being imputed.",
            "Lineage was revealed only after both substantive reviews froze.",
        ],
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe_generated({"consolidation": consolidation})
    return consolidation, errors


def write_review_consolidation(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    consolidation, errors = build_review_consolidation(repo_root=root)
    if errors:
        raise ProductDeltaGraphVarianceResultError(
            f"review validation failed with {len(errors)} error(s)"
        )
    path = _resolve_repo_path(root, CONSOLIDATION_RELPATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_json(consolidation), encoding="utf-8")


def validate_checked_in_review_consolidation(
    *, repo_root: Path | str
) -> list[str]:
    root = Path(repo_root).resolve()
    consolidation, errors = build_review_consolidation(repo_root=root)
    if errors:
        return errors
    try:
        actual = _resolve_repo_path(root, CONSOLIDATION_RELPATH).read_text(
            encoding="utf-8"
        )
    except OSError:
        return [f"missing generated artifact:{CONSOLIDATION_RELPATH}"]
    if actual != render_json(consolidation):
        return [f"generated artifact drift:{CONSOLIDATION_RELPATH}"]
    return []


def _validate_frozen_inputs(root: Path) -> None:
    try:
        calibration_errors = validate_checked_in_calibration(repo_root=root)
    except ProductDeltaGraphVarianceCalibrationError as exc:
        raise ProductDeltaGraphVarianceResultError(
            "pre-output calibration validation failed"
        ) from exc
    control_errors = validate_checked_in_screen(repo_root=root)
    if calibration_errors or control_errors:
        raise ProductDeltaGraphVarianceResultError(
            "frozen calibration or reviewer controls drifted"
        )


def _validate_generation_states(
    *,
    root: Path,
    generation: Mapping[str, Any],
    preoutput_sealed: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    packets = {
        str(item["sample_alias"]): item
        for item in _required_list(generation, "packets")
        if isinstance(item, Mapping)
    }
    sample_map = _required_mapping(preoutput_sealed, "sample_map")
    states: dict[str, dict[str, Any]] = {}
    refs: dict[str, dict[str, Any]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    for alias, lineage_value in sample_map.items():
        lineage = _as_mapping(lineage_value, "sample lineage")
        output_relpath = str(lineage["predeclared_terminal_output_path"])
        output_path = _resolve_repo_path(root, output_relpath)
        failure_relpath = FAILURE_RELPATHS.get(str(alias))
        failure_exists = (
            failure_relpath is not None
            and _resolve_repo_path(root, failure_relpath).exists()
        )
        output_exists = output_path.exists()
        if output_exists and failure_exists:
            raise ProductDeltaGraphVarianceResultError(
                "sample has both terminal output and terminal failure"
            )
        if not output_exists and not failure_exists:
            raise ProductDeltaGraphVarianceResultError(
                "sample has no preserved first terminal state"
            )
        if failure_exists:
            failure, ref = _read_json_ref(root, str(failure_relpath))
            expected_failure = {
                "schema_version": FAILURE_SCHEMA_VERSION,
                "sample_alias": alias,
                "status": "failed",
                "attempt": 1,
                "failure_class": "terminal_result_unavailable",
            }
            for key, expected in expected_failure.items():
                if failure.get(key) != expected:
                    raise ProductDeltaGraphVarianceResultError(
                        "terminal failure custody drifted"
                    )
            boundary = _required_mapping(failure, "boundary")
            if boundary != {
                "replacement_authorized": False,
                "repository_provider_api_calls": 0,
                "repository_provider_api_cost_usd": 0.0,
                "retry_authorized": False,
            }:
                raise ProductDeltaGraphVarianceResultError(
                    "terminal failure boundary drifted"
                )
            states[str(alias)] = {
                "terminal_status": "failed",
                "failure_class": failure["failure_class"],
            }
            refs[str(alias)] = ref
            receipts[str(alias)] = {
                "terminal_status": "failed",
                "first_terminal_result_preserved": False,
                "retry_fallback_healing_replacement_or_imputation": False,
                "semantic_correctness_validated": False,
            }
            continue

        response, ref = _read_json_ref(root, output_relpath)
        condition = str(lineage["condition"])
        bundle_arm_name = CONDITION_TO_BUNDLE_ARM.get(condition)
        if bundle_arm_name is None:
            raise ProductDeltaGraphVarianceResultError(
                "sample has unknown condition lineage"
            )
        bundle_arm = _required_mapping(
            _required_mapping(bundle, "arms"), bundle_arm_name
        )
        packet = _required_mapping(bundle_arm, "packet")
        try:
            compiled = compile_pressure_response(
                response=response,
                packet=packet,
            )
        except (SimulatedReliabilityError, KeyError, TypeError) as exc:
            raise ProductDeltaGraphVarianceResultError(
                "first terminal output failed deterministic compilation"
            ) from exc
        response_schema = _required_mapping(
            _required_mapping(
                _required_mapping(packets, str(alias)),
                "request_body_projection",
            ),
            "response_schema",
        )
        _validate_response_lengths(response, response_schema)
        expected_ids = sorted(
            str(item["model_id"])
            for item in _required_list(packet, "pressure_portfolio")
        )
        observed_ids = sorted(
            str(item["model_id"])
            for item in _required_list(response, "candidate_dispositions")
        )
        if observed_ids != expected_ids:
            raise ProductDeltaGraphVarianceResultError(
                "terminal output candidate identities drifted"
            )
        states[str(alias)] = {
            "terminal_status": "complete",
            "response": response,
        }
        refs[str(alias)] = ref
        receipts[str(alias)] = {
            "terminal_status": "complete",
            "first_terminal_result_preserved": True,
            "compiled_schema_version": compiled["schema_version"],
            "all_active_candidates_accounted_for": compiled[
                "all_active_candidates_accounted_for"
            ],
            "expected_candidate_count": len(expected_ids),
            "response_schema_sha256": _sha256_json_value(response_schema),
            "semantic_correctness_validated": False,
            "invented_high_stakes_fact_or_causation_detected": False,
        }
    if sorted(item["terminal_status"] for item in states.values()) != [
        "complete",
        "complete",
        "complete",
        "failed",
    ]:
        raise ProductDeltaGraphVarianceResultError(
            "expected three complete samples and one failed sample"
        )
    return states, refs, receipts


def _build_comparison_cases(
    *,
    root: Path,
    source_ref: Mapping[str, Any],
    preoutput_sealed: Mapping[str, Any],
    states: Mapping[str, Mapping[str, Any]],
    state_refs: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    plan = _required_list(preoutput_sealed, "comparison_plan")
    if len(plan) != 5:
        raise ProductDeltaGraphVarianceResultError(
            "predeclared comparison count drifted"
        )
    cases: list[dict[str, Any]] = []
    lineage: dict[str, Any] = {}
    for case_id, planned in zip(COMPARISON_CASE_IDS, plan, strict=True):
        item = _as_mapping(planned, "comparison plan item")
        left = _resolve_endpoint(
            root=root,
            endpoint=_required_mapping(item, "left"),
            states=states,
            state_refs=state_refs,
        )
        right = _resolve_endpoint(
            root=root,
            endpoint=_required_mapping(item, "right"),
            states=states,
            state_refs=state_refs,
        )
        available = left["status"] == right["status"] == "complete"
        pair_lineage: dict[str, Any] = {
            "predeclared_pair_id": item["pair_id"],
            "sealed_pair_role": item["sealed_pair_role"],
            "left": copy.deepcopy(left["lineage"]),
            "right": copy.deepcopy(right["lineage"]),
            "availability": "available" if available else "not_evaluable",
        }
        if available:
            seed = _sha256_text(
                "|".join(
                    (
                        BLINDING_NAMESPACE,
                        case_id,
                        str(source_ref["sha256"]),
                        str(left["ref"]["sha256"]),
                        str(right["ref"]["sha256"]),
                    )
                )
            )
            a_endpoint = left if bytes.fromhex(seed)[0] % 2 == 0 else right
            b_endpoint = right if a_endpoint is left else left
            cases.append(
                {
                    "case_id": case_id,
                    "evidence_class": (
                        "complete_checked_in_agent_rehearsal_pair"
                    ),
                    "availability": "available",
                    "review_status_required": "reviewed",
                    "arms": {
                        "A": {
                            "content": a_endpoint["answer"],
                            "format": "text",
                        },
                        "B": {
                            "content": b_endpoint["answer"],
                            "format": "text",
                        },
                    },
                    "review_warning": (
                        "Arm labels are deterministic and neutral. Compare "
                        "atomic reasoning moves, not fluency or length."
                    ),
                }
            )
            pair_lineage["review_arm_map"] = {
                "A": copy.deepcopy(a_endpoint["lineage"]),
                "B": copy.deepcopy(b_endpoint["lineage"]),
            }
            pair_lineage["terminal_refs"] = {
                "A": a_endpoint["ref"],
                "B": b_endpoint["ref"],
            }
        else:
            cases.append(
                {
                    "case_id": case_id,
                    "evidence_class": (
                        "first_terminal_generation_result_unavailable"
                    ),
                    "availability": "not_evaluable",
                    "review_status_required": "not_evaluable",
                    "arms": {},
                    "unavailability_basis": (
                        "first_terminal_generation_result_unavailable"
                    ),
                    "review_warning": (
                        "Do not reconstruct, impute, compare, or infer a "
                        "missing arm."
                    ),
                }
            )
            pair_lineage["terminal_refs"] = {
                "left": left["ref"],
                "right": right["ref"],
            }
        cases[-1]["packet_sha256"] = _sha256_json_value(cases[-1])
        lineage[case_id] = pair_lineage
    return cases, lineage


def _resolve_endpoint(
    *,
    root: Path,
    endpoint: Mapping[str, Any],
    states: Mapping[str, Mapping[str, Any]],
    state_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    relpath = str(endpoint["terminal_output_path"])
    draw_number = int(endpoint["draw_number"])
    condition = str(endpoint["condition"])
    if draw_number == 0:
        payload, ref = _read_json_ref(root, relpath)
        return {
            "status": "complete",
            "answer": str(payload["reconsidered_answer"]),
            "ref": ref,
            "lineage": {
                "condition": condition,
                "draw_number": 0,
                "terminal_output_path": relpath,
            },
        }
    aliases = [
        alias
        for alias, ref in state_refs.items()
        if ref["path"] == relpath
        or relpath.endswith(f"terminal-output-{alias}.json")
        or relpath.endswith(f"terminal-failure-{alias}.json")
    ]
    if len(aliases) != 1:
        raise ProductDeltaGraphVarianceResultError(
            "new comparison endpoint cannot be resolved"
        )
    alias = aliases[0]
    state = _required_mapping(states, alias)
    result = {
        "status": state["terminal_status"],
        "ref": state_refs[alias],
        "lineage": {
            "condition": condition,
            "draw_number": draw_number,
            "sample_alias": alias,
            "terminal_state_path": state_refs[alias]["path"],
        },
    }
    if state["terminal_status"] == "complete":
        result["answer"] = str(
            _required_mapping(state, "response")["reconsidered_answer"]
        )
    return result


def _validate_response_lengths(
    response: Mapping[str, Any], schema: Mapping[str, Any]
) -> None:
    properties = _required_mapping(schema, "properties")
    for name in ("reconsidered_answer", "change_summary"):
        spec = _required_mapping(properties, name)
        value = response.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ProductDeltaGraphVarianceResultError(
                "terminal output has an empty public field"
            )
        maximum = spec.get("maxLength")
        if isinstance(maximum, int) and len(value) > maximum:
            raise ProductDeltaGraphVarianceResultError(
                "terminal output public field exceeds frozen schema"
            )
    rows_spec = _required_mapping(properties, "candidate_dispositions")
    row_properties = _required_mapping(
        _required_mapping(rows_spec, "items"), "properties"
    )
    for row in _required_list(response, "candidate_dispositions"):
        if not isinstance(row, Mapping):
            raise ProductDeltaGraphVarianceResultError(
                "terminal output disposition is not an object"
            )
        for name in (
            "strongest_plausible_application",
            "disposition_reason",
            "risk_if_forced",
            "reopen_condition",
        ):
            spec = _required_mapping(row_properties, name)
            value = row.get(name)
            if not isinstance(value, str) or not value.strip():
                raise ProductDeltaGraphVarianceResultError(
                    "terminal output has an empty disposition field"
                )
            maximum = spec.get("maxLength")
            if isinstance(maximum, int) and len(value) > maximum:
                raise ProductDeltaGraphVarianceResultError(
                    "terminal output disposition exceeds frozen schema"
                )


def _validate_review(
    payload: Mapping[str, Any],
    *,
    path: str,
    expected_review_id: str,
    blind: Mapping[str, Any],
) -> list[str]:
    errors: list[str] = []
    expected_keys = {
        "schema_version",
        "review_id",
        "fresh_context",
        "saw_lineage_before_freeze",
        "saw_sibling_review_before_freeze",
        "boundary",
        "qualification_reviews",
        "duplicate_null_review",
        "comparison_reviews",
        "standdown_reviews",
    }
    if set(payload) != expected_keys:
        errors.append(f"{path}:top-level keys mismatch")
    if payload.get("schema_version") != REVIEW_SCHEMA_VERSION:
        errors.append(f"{path}:schema version mismatch")
    if payload.get("review_id") != expected_review_id:
        errors.append(f"{path}:review id mismatch")
    if payload.get("fresh_context") is not True:
        errors.append(f"{path}:fresh_context must be true")
    for key in ("saw_lineage_before_freeze", "saw_sibling_review_before_freeze"):
        if payload.get(key) is not False:
            errors.append(f"{path}:{key} must be false")
    if payload.get("boundary") != _review_boundary():
        errors.append(f"{path}:authority boundary mismatch")
    rendered = json.dumps(payload, ensure_ascii=False)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            errors.append(f"{path}:privacy marker:{marker}")
    for marker in SEALED_LINEAGE_MARKERS:
        if marker in rendered:
            errors.append(f"{path}:sealed lineage marker:{marker}")

    qualification_ids = _case_ids(
        _required_list(blind, "qualification_cases")
    )
    qualification_reviews = payload.get("qualification_reviews")
    if not isinstance(qualification_reviews, list):
        errors.append(f"{path}:qualification_reviews must be an array")
        qualification_reviews = []
    errors.extend(
        _validate_exact_case_ids(
            qualification_reviews, qualification_ids, path
        )
    )
    for review in qualification_reviews:
        if not isinstance(review, Mapping):
            errors.append(f"{path}:qualification review is not an object")
            continue
        case_id = str(review.get("case_id"))
        if review.get("evidence_disposition") not in QUALIFICATION_DISPOSITIONS:
            errors.append(f"{path}:{case_id}:invalid evidence disposition")
        for key in (
            "supported_observations",
            "missing_evidence",
            "inferences_explicitly_not_made",
            "uncertainty_notes",
        ):
            if not isinstance(review.get(key), list):
                errors.append(f"{path}:{case_id}:{key} must be an array")

    duplicate = payload.get("duplicate_null_review")
    expected_duplicate_id = str(
        _required_mapping(blind, "exact_duplicate_null")["case_id"]
    )
    if not isinstance(duplicate, Mapping):
        errors.append(f"{path}:duplicate_null_review must be an object")
    else:
        errors.extend(
            _validate_available_review(
                duplicate,
                expected_case_id=expected_duplicate_id,
                path=path,
            )
        )

    comparison_reviews = payload.get("comparison_reviews")
    if not isinstance(comparison_reviews, list):
        errors.append(f"{path}:comparison_reviews must be an array")
        comparison_reviews = []
    errors.extend(
        _validate_exact_case_ids(
            comparison_reviews, list(COMPARISON_CASE_IDS), path
        )
    )
    blind_cases = _index_cases(_required_list(blind, "comparison_cases"))
    for review in comparison_reviews:
        if not isinstance(review, Mapping):
            errors.append(f"{path}:comparison review is not an object")
            continue
        case_id = str(review.get("case_id"))
        blind_case = blind_cases.get(case_id)
        if not isinstance(blind_case, Mapping):
            continue
        if blind_case["review_status_required"] == "reviewed":
            errors.extend(
                _validate_available_review(
                    review,
                    expected_case_id=case_id,
                    path=path,
                )
            )
        else:
            if set(review) != {
                "case_id",
                "review_status",
                "semantic_comparison_attempted",
                "unavailability_basis",
            }:
                errors.append(
                    f"{path}:{case_id}:unavailable review keys mismatch"
                )
            if review.get("review_status") != "not_evaluable":
                errors.append(f"{path}:{case_id}:must be not_evaluable")
            if review.get("semantic_comparison_attempted") is not False:
                errors.append(
                    f"{path}:{case_id}:semantic comparison must be false"
                )
            if review.get("unavailability_basis") != (
                "first_terminal_generation_result_unavailable"
            ):
                errors.append(
                    f"{path}:{case_id}:unavailability basis drifted"
                )

    standdown_ids = _case_ids(_required_list(blind, "standdown_cases"))
    standdowns = payload.get("standdown_reviews")
    if not isinstance(standdowns, list):
        errors.append(f"{path}:standdown_reviews must be an array")
        standdowns = []
    errors.extend(_validate_exact_case_ids(standdowns, standdown_ids, path))
    for review in standdowns:
        if not isinstance(review, Mapping):
            errors.append(f"{path}:standdown review is not an object")
            continue
        case_id = str(review.get("case_id"))
        if review.get("standdown_support") not in STANDDOWN_SUPPORT_VALUES:
            errors.append(f"{path}:{case_id}:invalid standdown support")
        for key in (
            "source_basis",
            "risk_of_forced_additional_analysis",
            "semantic_limits_of_mechanical_observation",
        ):
            if not isinstance(review.get(key), list):
                errors.append(f"{path}:{case_id}:{key} must be an array")
    return errors


def _validate_available_review(
    review: Mapping[str, Any],
    *,
    expected_case_id: str,
    path: str,
) -> list[str]:
    errors: list[str] = []
    expected_keys = {
        "case_id",
        "review_status",
        "source_interpretation",
        "atomic_moves",
        "arm_observations",
        "material_decision_difference",
        "inspection_limits",
    }
    if set(review) != expected_keys:
        errors.append(f"{path}:{expected_case_id}:available review keys mismatch")
    if review.get("case_id") != expected_case_id:
        errors.append(f"{path}:{expected_case_id}:case id mismatch")
    if review.get("review_status") != "reviewed":
        errors.append(f"{path}:{expected_case_id}:review_status must be reviewed")
    source_interpretation = review.get("source_interpretation")
    if not isinstance(source_interpretation, Mapping):
        errors.append(f"{path}:{expected_case_id}:missing source interpretation")
    else:
        if not isinstance(source_interpretation.get("decision_or_question"), str):
            errors.append(
                f"{path}:{expected_case_id}:decision_or_question must be text"
            )
        for key in ("material_constraints", "source_limits"):
            if not isinstance(source_interpretation.get(key), list):
                errors.append(
                    f"{path}:{expected_case_id}:{key} must be an array"
                )
    moves = review.get("atomic_moves")
    if not isinstance(moves, list) or not moves:
        errors.append(f"{path}:{expected_case_id}:atomic moves are empty")
        moves = []
    move_ids: list[str] = []
    for move in moves:
        if not isinstance(move, Mapping):
            errors.append(f"{path}:{expected_case_id}:move is not an object")
            continue
        move_id = str(move.get("move_id", ""))
        move_ids.append(move_id)
        if move.get("presence") not in PRESENCE_VALUES:
            errors.append(f"{path}:{expected_case_id}:{move_id}:bad presence")
        if move.get("reasoning_operation") not in REASONING_OPERATION_VALUES:
            errors.append(
                f"{path}:{expected_case_id}:{move_id}:bad reasoning operation"
            )
        if move.get("source_grounding") not in SOURCE_GROUNDING_VALUES:
            errors.append(
                f"{path}:{expected_case_id}:{move_id}:bad source grounding"
            )
        if move.get("cognitive_effect") not in COGNITIVE_EFFECT_VALUES:
            errors.append(
                f"{path}:{expected_case_id}:{move_id}:bad cognitive effect"
            )
        if not isinstance(move.get("source_evidence"), list):
            errors.append(
                f"{path}:{expected_case_id}:{move_id}:source_evidence must be an array"
            )
    if len(move_ids) != len(set(move_ids)):
        errors.append(f"{path}:{expected_case_id}:duplicate move id")
    observations = review.get("arm_observations")
    if not isinstance(observations, Mapping) or set(observations) != {"A", "B"}:
        errors.append(
            f"{path}:{expected_case_id}:arm observations must contain A and B"
        )
    else:
        for label in ("A", "B"):
            observation = observations[label]
            if not isinstance(observation, Mapping):
                errors.append(
                    f"{path}:{expected_case_id}:{label}:invalid observation"
                )
                continue
            for key in (
                "preserved_source_value",
                "lost_or_weakened_source_value",
                "unsupported_additions",
                "cognitive_burden",
            ):
                if not isinstance(observation.get(key), list):
                    errors.append(
                        f"{path}:{expected_case_id}:{label}:{key} must be an array"
                    )
    if review.get("material_decision_difference") not in (
        MATERIAL_DIFFERENCE_VALUES
    ):
        errors.append(
            f"{path}:{expected_case_id}:invalid material decision difference"
        )
    if not isinstance(review.get("inspection_limits"), list):
        errors.append(
            f"{path}:{expected_case_id}:inspection_limits must be an array"
        )
    return errors


def _available_pair_shape() -> dict[str, Any]:
    return {
        "case_id": "string",
        "review_status": "reviewed",
        "source_interpretation": {
            "decision_or_question": "string",
            "material_constraints": ["string"],
            "source_limits": ["string"],
        },
        "atomic_moves": [
            {
                "move_id": "case-local stable string",
                "summary": "one reasoning move only",
                "presence": sorted(PRESENCE_VALUES),
                "reasoning_operation": sorted(REASONING_OPERATION_VALUES),
                "source_evidence": ["short source-grounded paraphrase"],
                "source_grounding": sorted(SOURCE_GROUNDING_VALUES),
                "cognitive_effect": sorted(COGNITIVE_EFFECT_VALUES),
                "decision_effect": "what this move could change, or none",
            }
        ],
        "arm_observations": {
            "A": {
                "preserved_source_value": ["string"],
                "lost_or_weakened_source_value": ["string"],
                "unsupported_additions": ["string"],
                "cognitive_burden": ["string"],
            },
            "B": {
                "preserved_source_value": ["string"],
                "lost_or_weakened_source_value": ["string"],
                "unsupported_additions": ["string"],
                "cognitive_burden": ["string"],
            },
        },
        "material_decision_difference": sorted(MATERIAL_DIFFERENCE_VALUES),
        "inspection_limits": ["string"],
    }


def _review_boundary() -> dict[str, Any]:
    return {
        "answer_quality_scored": False,
        "ground_truth": False,
        "human_validated": False,
        "provider_calls": 0,
        "winner_selected": False,
    }


def _validate_exact_case_ids(
    records: Sequence[Any], expected: Sequence[str], path: str
) -> list[str]:
    actual = [
        str(item.get("case_id"))
        for item in records
        if isinstance(item, Mapping)
    ]
    if actual != list(expected):
        return [f"{path}:case ids or order mismatch"]
    return []


def _case_ids(value: Sequence[Any]) -> list[str]:
    ids = [
        str(item.get("case_id"))
        for item in value
        if isinstance(item, Mapping) and item.get("case_id")
    ]
    if len(ids) != len(value) or len(ids) != len(set(ids)):
        raise ProductDeltaGraphVarianceResultError(
            "case identity set is malformed"
        )
    return ids


def _index_cases(value: Sequence[Any]) -> dict[str, Mapping[str, Any]]:
    result = {
        str(item.get("case_id")): item
        for item in value
        if isinstance(item, Mapping) and item.get("case_id")
    }
    if len(result) != len(value):
        raise ProductDeltaGraphVarianceResultError(
            "case identity set is malformed"
        )
    return result


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        raw = path.read_bytes()
        payload = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProductDeltaGraphVarianceResultError(
            f"invalid graph-variance JSON input:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphVarianceResultError(
            f"graph-variance JSON input is not an object:{relpath}"
        )
    return payload, {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _read_text_ref(
    root: Path, relpath: str
) -> tuple[str, dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ProductDeltaGraphVarianceResultError(
            f"invalid graph-variance text input:{relpath}"
        ) from exc
    return text, {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    if Path(relpath).is_absolute():
        raise ProductDeltaGraphVarianceResultError(
            "absolute repository path is forbidden"
        )
    path = (root / relpath).resolve()
    if path != root and root not in path.parents:
        raise ProductDeltaGraphVarianceResultError(
            "graph-variance path escapes repository root"
        )
    return path


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise ProductDeltaGraphVarianceResultError(
            f"graph-variance input is missing mapping:{key}"
        )
    return result


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    result = value.get(key)
    if not isinstance(result, list):
        raise ProductDeltaGraphVarianceResultError(
            f"graph-variance input is missing list:{key}"
        )
    return result


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProductDeltaGraphVarianceResultError(
            f"{label} is not an object"
        )
    return value


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json_value(value: Any) -> str:
    return _sha256_text(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def _assert_safe_generated(payloads: Mapping[str, Any]) -> None:
    rendered = render_json(payloads)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            raise ProductDeltaGraphVarianceResultError(
                "generated graph-variance artifact contains a forbidden marker"
            )
