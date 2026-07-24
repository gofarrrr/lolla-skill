"""Freeze and consolidate the bounded graph replication result.

The helper imports eight externally captured first-terminal JSON payloads,
validates them through the inherited schema and existing pressure compiler,
builds eight neutrally named answer pairs plus existing Product Delta controls,
validates two blind reviews, prepares two review-specific post-reveal packets,
and preserves the non-scalar fan-in.

It does not call a provider, traverse or change the graph, run the live skill,
inspect private archives, judge answer quality, or authorize product behavior.
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
from engine.system_b.product_delta_graph_replication import (
    DEFAULT_GENERATION_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH,
    REPLICATION_ID,
    SAMPLE_ALIASES,
    ProductDeltaGraphReplicationError,
    evaluate_mechanical_availability,
    validate_checked_in_replication,
)
from engine.system_b.product_delta_graph_variance_calibration_result import (
    ProductDeltaGraphVarianceResultError,
    _validate_response_lengths,
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
    "lolla.product_delta_graph_replication_blind_review_packet.v1"
)
EXECUTION_SEALED_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_execution_sealed_manifest.v1"
)
REVIEW_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_fresh_agent_review.v1"
)
POST_REVEAL_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_post_reveal_packet.v1"
)
POST_REVEAL_INTERPRETATION_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_post_reveal_interpretation.v1"
)
CONSOLIDATION_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_agent_consolidation.v1"
)
BLINDING_NAMESPACE = "lolla-product-delta-graph-replication-result-v1"

OUTPUT_DIR_RELPATH = "research/agent-only-graph-replication-2026-07-23"
REVIEW_DIR_RELPATH = (
    "reviews/codex-assisted/agent-only-graph-replication-v1"
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

REVIEW_RELPATHS = {
    "primary": f"{REVIEW_DIR_RELPATH}/pair-review-primary.json",
    "skeptical": f"{REVIEW_DIR_RELPATH}/pair-review-skeptical.json",
}
REVIEW_FAILURE_RELPATHS = {
    lane: f"{REVIEW_DIR_RELPATH}/pair-review-{lane}-terminal-failure.json"
    for lane in REVIEW_RELPATHS
}
EXPECTED_REVIEW_IDS = {
    "primary": "agent-graph-replication-pair-primary-v1",
    "skeptical": "agent-graph-replication-pair-skeptical-v1",
}
POST_REVEAL_PACKET_RELPATHS = {
    lane: f"{OUTPUT_DIR_RELPATH}/post-reveal-packet-{lane}.json"
    for lane in REVIEW_RELPATHS
}
POST_REVEAL_INTERPRETATION_RELPATHS = {
    "primary": f"{REVIEW_DIR_RELPATH}/pattern-interpretation-primary.json",
    "skeptical": (
        f"{REVIEW_DIR_RELPATH}/pattern-interpretation-skeptical.json"
    ),
}
EXPECTED_INTERPRETATION_IDS = {
    "primary": "agent-graph-replication-pattern-primary-v1",
    "skeptical": "agent-graph-replication-pattern-skeptical-v1",
}
CONDITION_TO_BUNDLE_ARM = {
    REHEARSAL_DIRECT: "direct_pressure",
    REHEARSAL_DIRECT_PLUS_ONE_HOP: "graph_expanded_pressure",
}
COMPARISON_CASE_IDS = tuple(f"replication-pair-{index:02d}" for index in range(1, 9))
REVIEW_SPECIFIC_PATTERN_STATES = {
    (
        "cross_condition_difference_more_consistent_than_"
        "observed_within_condition_variation"
    ),
    (
        "cross_condition_difference_not_distinguishable_from_"
        "observed_within_condition_variation"
    ),
    "review_specific_pattern_mixed_or_uncertain",
}
OVERALL_PATTERN_STATES = {
    (
        "cross_condition_difference_more_consistent_than_"
        "observed_within_condition_variation"
    ),
    (
        "cross_condition_difference_not_distinguishable_from_"
        "observed_within_condition_variation"
    ),
    "mixed_or_reviewer_disagreement",
    "not_evaluable",
}

BOUNDARY = {
    "repository_provider_api_calls": 0,
    "repository_provider_api_cost_usd": 0.0,
    "repository_provider_execution_authorized": False,
    "codex_generation_contexts_attempted": 8,
    "codex_blind_review_contexts_predeclared": 2,
    "codex_post_reveal_contexts_conditionally_predeclared": 2,
    "codex_contexts_called_no_ai_calls_or_economically_free": False,
    "codex_platform_route_token_and_cost": "unavailable_to_repository_operator",
    "human_review_completed": False,
    "principal_human_target_completed": False,
    "private_archives_read": False,
    "answer_quality_scored": False,
    "winner_selected": False,
    "graph_traversal_invoked": False,
    "graph_source_or_relation_changed": False,
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
    "not principal-human review or a source-first human target",
    "not provider execution or an exact standalone provider envelope",
    "not a provider or model comparison",
    "not a statistically powered variance estimate",
    "not deterministic replay or expected model behavior",
    "not graph causation relevance correctness value or usefulness evidence",
    "not proof that either condition or answer is better",
    "not completion of F2 or F3",
    "not permission to expand traversal",
    "not a live skill runtime graph planner compiler or interface change",
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
    *SAMPLE_ALIASES,
    "within-direct",
    "within-graph",
    "cross-3",
    "cross-4",
    "cross-5",
    "cross-6",
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
)


class ProductDeltaGraphReplicationResultError(ValueError):
    """Sanitized deterministic replication-result custody failure."""


def import_terminal_output(
    *,
    repo_root: Path | str,
    sample_alias: str,
    source_path: Path | str,
) -> None:
    """Validate and preserve one external first-terminal payload verbatim."""

    root = Path(repo_root).resolve()
    _validate_frozen_inputs(root)
    if sample_alias not in SAMPLE_ALIASES:
        raise ProductDeltaGraphReplicationResultError(
            "unknown replication sample alias"
        )
    generation, _ = _read_json_ref(root, DEFAULT_GENERATION_PACKETS_RELPATH)
    sealed, _ = _read_json_ref(root, DEFAULT_SEALED_MANIFEST_RELPATH)
    bundle, _ = _read_json_ref(root, PORTFOLIO_BUNDLE_RELPATH)
    sample_map = _required_mapping(sealed, "sample_map")
    lineage = _required_mapping(sample_map, sample_alias)
    target_relpath = _required_text(
        lineage, "predeclared_terminal_output_path"
    )
    failure_relpath = _required_text(
        lineage, "predeclared_terminal_failure_path"
    )
    target = _resolve_repo_path(root, target_relpath)
    failure_target = _resolve_repo_path(root, failure_relpath)
    if target.exists() or failure_target.exists():
        raise ProductDeltaGraphReplicationResultError(
            "terminal state is already frozen and cannot be overwritten"
        )

    external = Path(source_path).resolve()
    try:
        raw = external.read_bytes()
    except OSError as exc:
        raise ProductDeltaGraphReplicationResultError(
            "external first-terminal payload is unavailable"
        ) from exc
    try:
        response = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProductDeltaGraphReplicationResultError(
            "external first-terminal payload is not JSON"
        ) from exc
    if not isinstance(response, dict):
        raise ProductDeltaGraphReplicationResultError(
            "external first-terminal payload is not an object"
        )
    packets = {
        _required_text(item, "sample_alias"): item
        for item in _required_list(generation, "packets")
        if isinstance(item, Mapping)
    }
    _validate_single_generation(
        response=response,
        packet_record=_required_mapping(packets, sample_alias),
        condition=_required_text(lineage, "condition"),
        bundle=bundle,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


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
        source_ref=source_ref,
        preoutput_sealed=preoutput_sealed,
        states=states,
        state_refs=state_refs,
    )

    qualification_cases = copy.deepcopy(
        _required_list(controls, "qualification_cases")
    )
    duplicate_null = next(
        (
            copy.deepcopy(item)
            for item in _required_list(controls, "paired_cases")
            if isinstance(item, Mapping)
            and item.get("evidence_class") == "exact_duplicate_null"
        ),
        None,
    )
    standdown_cases = copy.deepcopy(
        _required_list(controls, "standdown_cases")
    )
    if not isinstance(duplicate_null, dict):
        raise ProductDeltaGraphReplicationResultError(
            "existing exact-duplicate null is missing"
        )
    if len(qualification_cases) != 10 or len(standdown_cases) != 1:
        raise ProductDeltaGraphReplicationResultError(
            "existing reviewer control count drifted"
        )

    terminal_state_names = {
        alias: str(value["terminal_status"])
        for alias, value in states.items()
    }
    availability = evaluate_mechanical_availability(
        sealed_manifest=preoutput_sealed,
        sample_terminal_states=terminal_state_names,
        both_blind_reviews_complete=False,
    )
    public_availability = {
        "schema_version": availability["schema_version"],
        "purpose": availability["purpose"],
        "pair_receipts": [
            {
                "blind_case_id": receipt["blind_case_id"],
                "left_terminal_state": receipt["left_terminal_state"],
                "right_terminal_state": receipt["right_terminal_state"],
                "availability": receipt["availability"],
            }
            for receipt in _required_list(availability, "pair_receipts")
            if isinstance(receipt, Mapping)
        ],
        "available_pair_count": sum(
            receipt.get("availability") == "available"
            for receipt in _required_list(availability, "pair_receipts")
            if isinstance(receipt, Mapping)
        ),
        "total_pair_count": len(
            _required_list(availability, "pair_receipts")
        ),
        "both_blind_reviews_complete": False,
        "gate_passes": False,
        "result_if_closed_now": "not_evaluable",
    }
    qualification_ids = _case_ids(qualification_cases)
    standdown_ids = _case_ids(standdown_cases)
    duplicate_id = str(duplicate_null["case_id"])
    blind: dict[str, Any] = {
        "schema_version": BLIND_PACKET_SCHEMA_VERSION,
        "replication_id": REPLICATION_ID,
        "status": "blind_review_inputs_frozen_after_generation_admission",
        "purpose": (
            "Inspect every available neutral comparison plus the existing "
            "qualification, exact-duplicate, and stand-down controls without "
            "condition or pair-role lineage."
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
            "Review the exact-duplicate null before replication comparisons.",
            "For each available pair, use one to four concise atomic moves and compare reasoning rather than fluency, length, or polish.",
            "For an unavailable pair, record not_evaluable without reconstruction or imputation.",
            "Preserve source value, lost value, unsupported additions, burden, and uncertainty separately.",
            "Review the legitimate stand-down independently.",
            "Do not rank, score, vote, certify, select a winner, or infer lineage.",
        ],
        "visibility": {
            "condition_lineage_included": False,
            "pair_roles_included": False,
            "sample_aliases_included": False,
            "candidate_dispositions_included": False,
            "previous_variance_reads_included": False,
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
                "unavailability_basis": (
                    "first_terminal_generation_result_unavailable"
                ),
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
            "top_level_keys": [
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
            ],
            "review_id": "Use the exact ID in the task wrapper.",
            "fresh_context": True,
            "saw_lineage_before_freeze": False,
            "saw_sibling_review_before_freeze": False,
            "qualification_case_ids": qualification_ids,
            "duplicate_null_case_id": duplicate_id,
            "comparison_case_ids": list(COMPARISON_CASE_IDS),
            "standdown_case_ids": standdown_ids,
            "boundary": _review_boundary(),
        },
        "fresh_context_task_wrappers": {
            lane: _blind_review_task_wrapper(
                review_id=EXPECTED_REVIEW_IDS[lane]
            )
            for lane in REVIEW_RELPATHS
        },
        "qualification_cases": qualification_cases,
        "exact_duplicate_null": duplicate_null,
        "comparison_case_count": 8,
        "comparison_cases": comparison_cases,
        "standdown_cases": standdown_cases,
        "pre_review_mechanical_availability": public_availability,
        "non_claims": list(NON_CLAIMS),
    }
    blind_rendered = render_json(blind)
    sealed: dict[str, Any] = {
        "schema_version": EXECUTION_SEALED_SCHEMA_VERSION,
        "replication_id": REPLICATION_ID,
        "status": "generation_outputs_admitted_blind_inputs_frozen",
        "handling": {
            "show_to_generation_agents": False,
            "show_to_blind_reviewers": False,
            "unblind_only_after_both_reviews_are_frozen": True,
            "generation_retried_healed_replaced_or_imputed": False,
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
        "pre_review_mechanical_availability": availability,
        "blind_review_packet": {
            "path": BLIND_REVIEW_PACKET_RELPATH,
            "sha256": _sha256_text(blind_rendered),
            "bytes": len(blind_rendered.encode("utf-8")),
        },
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe_public(blind)
    _assert_safe_generated(sealed)
    return blind, sealed


def write_blind_review_inputs(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    for relpath, payload in zip(
        (BLIND_REVIEW_PACKET_RELPATH, EXECUTION_SEALED_MANIFEST_RELPATH),
        build_blind_review_inputs(repo_root=root),
        strict=True,
    ):
        target = _resolve_repo_path(root, relpath)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_blind_review_inputs(
    *, repo_root: Path | str
) -> list[str]:
    root = Path(repo_root).resolve()
    expected = build_blind_review_inputs(repo_root=root)
    errors: list[str] = []
    for relpath, payload in zip(
        (BLIND_REVIEW_PACKET_RELPATH, EXECUTION_SEALED_MANIFEST_RELPATH),
        expected,
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
) -> str:
    """Validate and preserve one external first-terminal blind review."""

    root = Path(repo_root).resolve()
    if lane not in REVIEW_RELPATHS:
        raise ProductDeltaGraphReplicationResultError(
            "unknown blind-review lane"
        )
    if validate_checked_in_blind_review_inputs(repo_root=root):
        raise ProductDeltaGraphReplicationResultError(
            "blind-review input custody drifted"
        )
    blind, _ = _read_json_ref(root, BLIND_REVIEW_PACKET_RELPATH)
    target = _resolve_repo_path(root, REVIEW_RELPATHS[lane])
    failure_target = _resolve_repo_path(root, REVIEW_FAILURE_RELPATHS[lane])
    if target.exists() or failure_target.exists():
        raise ProductDeltaGraphReplicationResultError(
            "blind review terminal state is already frozen"
        )

    external = Path(source_path).resolve()
    try:
        raw = external.read_bytes()
    except OSError as exc:
        raise ProductDeltaGraphReplicationResultError(
            "external blind review is unavailable"
        ) from exc
    errors: list[str] = []
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = None
        errors.append("terminal payload is not JSON")
    if not isinstance(payload, dict):
        errors.append("terminal payload is not an object")
    else:
        errors.extend(
            _validate_review(
                payload,
                expected_review_id=EXPECTED_REVIEW_IDS[lane],
                blind=blind,
            )
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    if errors:
        failure = {
            "schema_version": (
                "lolla.product_delta_graph_replication_review_failure.v1"
            ),
            "replication_id": REPLICATION_ID,
            "lane": lane,
            "status": "failed",
            "terminal_state": "failed",
            "failure_class": "review_shape_validation_failed",
            "raw_first_terminal_payload": {
                "path": REVIEW_RELPATHS[lane],
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            },
            "validation_error_count": len(errors),
            "validation_error_kinds": sorted(set(errors)),
            "retry_fallback_healing_replacement_or_imputation": False,
            "post_reveal_context_authorized": False,
            "result_effect": "not_evaluable",
            "non_claims": list(NON_CLAIMS),
        }
        _assert_safe_generated(failure)
        failure_target.write_text(render_json(failure), encoding="utf-8")
        return "failed"
    return "complete"


def build_post_reveal_packets(
    *, repo_root: Path | str
) -> dict[str, dict[str, Any]]:
    """Build one lineage-reveal packet for each already-frozen review."""

    root = Path(repo_root).resolve()
    if validate_checked_in_blind_review_inputs(repo_root=root):
        raise ProductDeltaGraphReplicationResultError(
            "blind-review input custody drifted"
        )
    blind, blind_ref = _read_json_ref(root, BLIND_REVIEW_PACKET_RELPATH)
    sealed, sealed_ref = _read_json_ref(
        root, EXECUTION_SEALED_MANIFEST_RELPATH
    )
    failed_review_lanes = [
        lane
        for lane, relpath in REVIEW_FAILURE_RELPATHS.items()
        if _resolve_repo_path(root, relpath).exists()
    ]
    if failed_review_lanes:
        raise ProductDeltaGraphReplicationResultError(
            "mechanical availability gate failed; a required blind review "
            "has no valid terminal result"
        )
    review_payloads, review_refs = _load_and_validate_reviews(
        root=root, blind=blind
    )
    terminal_states = {
        alias: str(receipt["terminal_status"])
        for alias, receipt in _required_mapping(
            sealed, "generation_state_validation"
        ).items()
    }
    preoutput_sealed, _ = _read_json_ref(
        root, DEFAULT_SEALED_MANIFEST_RELPATH
    )
    availability = evaluate_mechanical_availability(
        sealed_manifest=preoutput_sealed,
        sample_terminal_states=terminal_states,
        both_blind_reviews_complete=True,
    )
    if availability["gate_passes"] is not True:
        raise ProductDeltaGraphReplicationResultError(
            "mechanical availability gate failed; post-reveal work is forbidden"
        )

    lineage = _required_mapping(sealed, "comparison_lineage")
    packets: dict[str, dict[str, Any]] = {}
    for lane, review in review_payloads.items():
        review_comparisons = _index_cases(
            _required_list(review, "comparison_reviews")
        )
        reveal_rows = []
        for case_id in COMPARISON_CASE_IDS:
            case_lineage = _required_mapping(lineage, case_id)
            frozen_review = _required_mapping(review_comparisons, case_id)
            reveal_rows.append(
                {
                    "case_id": case_id,
                    "sealed_pair_id": case_lineage["sealed_pair_id"],
                    "sealed_pair_role": case_lineage["sealed_pair_role"],
                    "condition_and_draw_lineage": {
                        "A": copy.deepcopy(
                            case_lineage["review_arm_map"]["A"]
                        ),
                        "B": copy.deepcopy(
                            case_lineage["review_arm_map"]["B"]
                        ),
                    },
                    "frozen_material_decision_difference": (
                        frozen_review["material_decision_difference"]
                    ),
                    "frozen_move_ids": [
                        item["move_id"]
                        for item in _required_list(
                            frozen_review, "atomic_moves"
                        )
                    ],
                }
            )
        packet = {
            "schema_version": POST_REVEAL_PACKET_SCHEMA_VERSION,
            "replication_id": REPLICATION_ID,
            "lane": lane,
            "status": "frozen_review_plus_deterministic_lineage_reveal",
            "purpose": (
                "Interpret recurrence only inside this frozen blind review. "
                "Do not create new answer or source judgments."
            ),
            "input_refs": {
                "blind_review_packet": blind_ref,
                "execution_sealed_manifest": sealed_ref,
                "frozen_review": review_refs[lane],
            },
            "mechanical_availability": copy.deepcopy(availability),
            "frozen_review": copy.deepcopy(review),
            "comparison_reveal": reveal_rows,
            "response_contract": {
                "schema_version": (
                    POST_REVEAL_INTERPRETATION_SCHEMA_VERSION
                ),
                "interpretation_id": EXPECTED_INTERPRETATION_IDS[lane],
                "source_review_id": EXPECTED_REVIEW_IDS[lane],
                "fresh_post_reveal_context": True,
                "saw_sibling_review_or_interpretation": False,
                "state": sorted(REVIEW_SPECIFIC_PATTERN_STATES),
                "pair_assessment_shape": {
                    "case_id": "exact comparison case ID",
                    "sealed_pair_role": [
                        "within_condition",
                        "cross_condition",
                    ],
                    "frozen_material_decision_difference": sorted(
                        MATERIAL_DIFFERENCE_VALUES
                    ),
                    "cited_frozen_move_ids": [
                        "zero or more exact IDs from this frozen review"
                    ],
                    "recurrence_observation": "brief text",
                    "burden_harm_or_lost_value_observation": "brief text",
                    "uncertainty": "brief text",
                },
                "pair_assessment_case_ids": list(COMPARISON_CASE_IDS),
                "rationale": "brief non-scalar pattern explanation",
                "nonclaims_acknowledged": list(NON_CLAIMS),
            },
            "task_wrapper": _post_reveal_task_wrapper(
                interpretation_id=EXPECTED_INTERPRETATION_IDS[lane],
                source_review_id=EXPECTED_REVIEW_IDS[lane],
            ),
            "forbidden_behavior": [
                "Do not add, remove, rewrite, or reclassify atomic moves.",
                "Do not reinterpret the source or answers.",
                "Do not see or infer the sibling review.",
                "Do not score, count into an effect size, rank, vote, or choose a winner.",
                "Do not claim graph causation, relevance, correctness, value, answer quality, expected behavior, or human usefulness.",
            ],
            "non_claims": list(NON_CLAIMS),
        }
        _assert_safe_generated(packet)
        packets[lane] = packet
    return packets


def write_post_reveal_packets(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    for lane, payload in build_post_reveal_packets(repo_root=root).items():
        target = _resolve_repo_path(root, POST_REVEAL_PACKET_RELPATHS[lane])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_post_reveal_packets(
    *, repo_root: Path | str
) -> list[str]:
    root = Path(repo_root).resolve()
    expected = build_post_reveal_packets(repo_root=root)
    errors: list[str] = []
    for lane, payload in expected.items():
        relpath = POST_REVEAL_PACKET_RELPATHS[lane]
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


def import_post_reveal_interpretation(
    *,
    repo_root: Path | str,
    lane: str,
    source_path: Path | str,
) -> None:
    """Validate and preserve one review-specific post-reveal interpretation."""

    root = Path(repo_root).resolve()
    if lane not in POST_REVEAL_INTERPRETATION_RELPATHS:
        raise ProductDeltaGraphReplicationResultError(
            "unknown post-reveal lane"
        )
    if validate_checked_in_post_reveal_packets(repo_root=root):
        raise ProductDeltaGraphReplicationResultError(
            "post-reveal packet custody drifted"
        )
    packet, _ = _read_json_ref(root, POST_REVEAL_PACKET_RELPATHS[lane])
    external = Path(source_path).resolve()
    try:
        raw = external.read_bytes()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductDeltaGraphReplicationResultError(
            "external post-reveal interpretation is unavailable or invalid"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphReplicationResultError(
            "external post-reveal interpretation is not an object"
        )
    errors = _validate_post_reveal_interpretation(
        payload,
        packet=packet,
        expected_id=EXPECTED_INTERPRETATION_IDS[lane],
        expected_review_id=EXPECTED_REVIEW_IDS[lane],
    )
    if errors:
        raise ProductDeltaGraphReplicationResultError(
            f"external post-reveal interpretation failed {len(errors)} checks"
        )
    target = _resolve_repo_path(
        root, POST_REVEAL_INTERPRETATION_RELPATHS[lane]
    )
    if target.exists():
        raise ProductDeltaGraphReplicationResultError(
            "post-reveal interpretation is already frozen"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)


def build_consolidation(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], list[str]]:
    """Preserve both review vectors and interpretation states without voting."""

    root = Path(repo_root).resolve()
    errors = validate_checked_in_blind_review_inputs(repo_root=root)
    if errors:
        raise ProductDeltaGraphReplicationResultError(
            "result input custody drifted"
        )
    blind, blind_ref = _read_json_ref(root, BLIND_REVIEW_PACKET_RELPATH)
    sealed, sealed_ref = _read_json_ref(
        root, EXECUTION_SEALED_MANIFEST_RELPATH
    )
    failed_review_lanes = [
        lane
        for lane, relpath in REVIEW_FAILURE_RELPATHS.items()
        if _resolve_repo_path(root, relpath).exists()
    ]
    if failed_review_lanes:
        return _build_review_failure_consolidation(
            root=root,
            blind=blind,
            blind_ref=blind_ref,
            sealed=sealed,
            sealed_ref=sealed_ref,
            failed_review_lanes=failed_review_lanes,
        ), []

    errors.extend(validate_checked_in_post_reveal_packets(repo_root=root))
    if errors:
        raise ProductDeltaGraphReplicationResultError(
            "result input custody drifted"
        )
    review_payloads, review_refs = _load_and_validate_reviews(
        root=root, blind=blind
    )
    interpretations: dict[str, dict[str, Any]] = {}
    interpretation_refs: dict[str, dict[str, Any]] = {}
    for lane, relpath in POST_REVEAL_INTERPRETATION_RELPATHS.items():
        payload, ref = _read_json_ref(root, relpath)
        packet, _ = _read_json_ref(root, POST_REVEAL_PACKET_RELPATHS[lane])
        errors.extend(
            _validate_post_reveal_interpretation(
                payload,
                packet=packet,
                expected_id=EXPECTED_INTERPRETATION_IDS[lane],
                expected_review_id=EXPECTED_REVIEW_IDS[lane],
            )
        )
        interpretations[lane] = payload
        interpretation_refs[lane] = ref

    comparison_lineage = _required_mapping(sealed, "comparison_lineage")
    comparison_fan_in = []
    for case_id in COMPARISON_CASE_IDS:
        reviewer_reads = []
        for lane, payload in review_payloads.items():
            review = _required_mapping(
                _index_cases(
                    _required_list(payload, "comparison_reviews")
                ),
                case_id,
            )
            reviewer_reads.append(
                {
                    "lane": lane,
                    "review_id": payload["review_id"],
                    **copy.deepcopy(dict(review)),
                }
            )
        comparison_fan_in.append(
            {
                "case_id": case_id,
                "lineage_revealed_after_both_reviews_froze": copy.deepcopy(
                    comparison_lineage[case_id]
                ),
                "reviewer_reads": reviewer_reads,
                "fan_in_policy": (
                    "Reads remain side by side; agreement is not truth and "
                    "disagreement is not resolved by ranking or voting."
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
                    "lane": lane,
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
                for lane, payload in review_payloads.items()
            ],
        }
        for case_id in qualification_ids
    ]
    duplicate_id = str(
        _required_mapping(blind, "exact_duplicate_null")["case_id"]
    )
    duplicate_reads = [
        {
            "lane": lane,
            "review_id": payload["review_id"],
            **copy.deepcopy(
                dict(_required_mapping(payload, "duplicate_null_review"))
            ),
        }
        for lane, payload in review_payloads.items()
    ]
    standdown_ids = _case_ids(_required_list(blind, "standdown_cases"))
    standdown_fan_in = [
        {
            "case_id": case_id,
            "reviewer_reads": [
                {
                    "lane": lane,
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
                for lane, payload in review_payloads.items()
            ],
        }
        for case_id in standdown_ids
    ]

    terminal_states = {
        alias: str(receipt["terminal_status"])
        for alias, receipt in _required_mapping(
            sealed, "generation_state_validation"
        ).items()
    }
    preoutput_sealed, _ = _read_json_ref(
        root, DEFAULT_SEALED_MANIFEST_RELPATH
    )
    availability = evaluate_mechanical_availability(
        sealed_manifest=preoutput_sealed,
        sample_terminal_states=terminal_states,
        both_blind_reviews_complete=True,
    )
    states = [payload["state"] for payload in interpretations.values()]
    if availability["gate_passes"] is not True:
        overall_state = "not_evaluable"
    elif (
        len(set(states)) == 1
        and states[0] != "review_specific_pattern_mixed_or_uncertain"
    ):
        overall_state = states[0]
    else:
        overall_state = "mixed_or_reviewer_disagreement"
    if overall_state not in OVERALL_PATTERN_STATES:
        errors.append("overall interpretation state is invalid")

    consolidation = {
        "schema_version": CONSOLIDATION_SCHEMA_VERSION,
        "replication_id": REPLICATION_ID,
        "status": (
            "valid_frozen_agent_replication_diagnostic"
            if not errors
            else "invalid_review_or_interpretation_shape"
        ),
        "boundary": {
            **copy.deepcopy(BOUNDARY),
            "codex_blind_review_contexts_completed": 2,
            "codex_post_reveal_contexts_completed": 2,
            "principal_human_review_completed": False,
            "semantic_adjudication_performed": False,
            "scalar_summary_created": False,
            "permission_to_expand_graph_created": False,
        },
        "input_refs": {
            "blind_review_packet": blind_ref,
            "execution_sealed_manifest": sealed_ref,
            "blind_reviews": review_refs,
            "post_reveal_packets": {
                lane: _read_json_ref(
                    root, POST_REVEAL_PACKET_RELPATHS[lane]
                )[1]
                for lane in REVIEW_RELPATHS
            },
            "post_reveal_interpretations": interpretation_refs,
        },
        "validation": {
            "error_count": len(errors),
            "errors": errors,
            "shape_custody_and_declared_enum_validation_only": True,
            "semantic_correctness_validated": False,
        },
        "isolation_receipt": {
            "generation_contexts_attempted": 8,
            "generation_first_terminal_outputs_complete": sum(
                state == "complete" for state in terminal_states.values()
            ),
            "generation_first_terminal_failures": sum(
                state != "complete" for state in terminal_states.values()
            ),
            "generation_retries_fallbacks_healing_replacements_or_imputations": 0,
            "blind_review_contexts_completed": 2,
            "post_reveal_contexts_completed": 2,
            "reviewers_saw_lineage_before_freeze": False,
            "reviewers_saw_each_other_before_freeze": False,
            "post_reveal_contexts_saw_sibling_review": False,
            "codex_platform_route_token_and_cost": (
                "unavailable_to_repository_operator"
            ),
        },
        "mechanical_availability": availability,
        "qualification_reviews": qualification_fan_in,
        "duplicate_null_review": {
            "case_id": duplicate_id,
            "reviewer_reads": duplicate_reads,
            "control_only": True,
        },
        "comparison_reviews": comparison_fan_in,
        "standdown_reviews": standdown_fan_in,
        "post_reveal_interpretations": [
            {
                "lane": lane,
                **copy.deepcopy(payload),
            }
            for lane, payload in interpretations.items()
        ],
        "replication_interpretation": {
            "state": overall_state,
            "review_specific_states": {
                lane: payload["state"]
                for lane, payload in interpretations.items()
            },
            "fan_in_rule": (
                "Aligned non-mixed reviewer-specific states remain aligned; "
                "otherwise the result is mixed_or_reviewer_disagreement. "
                "This is an alignment receipt, not a vote or semantic truth."
            ),
            "every_pair_and_review_observation_preserved": True,
            "no_graph_decision_created": True,
            "interpretation_limit": (
                "This is a bounded one-case agent replication diagnostic, "
                "not a score, winner, answer-quality result, graph-value "
                "estimate, expected-model-behavior claim, or substitute for "
                "a person."
            ),
        },
        "fan_in_policy": [
            "No reviewer or post-reveal interpretation is authoritative.",
            "Qualification reads remain case-specific rather than becoming a score.",
            "The duplicate null and stand-down are controls, not proof of calibration.",
            "Every comparison observation remains attributable to each reviewer.",
            "Lineage was revealed only after both blind reviews froze.",
            "The two post-reveal contexts each received one frozen review and no sibling work.",
            "No score, majority vote, statistical inference, or answer winner is produced.",
        ],
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe_generated(consolidation)
    return consolidation, errors


def _build_review_failure_consolidation(
    *,
    root: Path,
    blind: Mapping[str, Any],
    blind_ref: Mapping[str, Any],
    sealed: Mapping[str, Any],
    sealed_ref: Mapping[str, Any],
    failed_review_lanes: Sequence[str],
) -> dict[str, Any]:
    """Close honestly when a required blind review has no valid result."""

    failure_set = set(failed_review_lanes)
    if not failure_set or not failure_set.issubset(REVIEW_RELPATHS):
        raise ProductDeltaGraphReplicationResultError(
            "blind review failure lane set is malformed"
        )
    review_terminal_states: list[dict[str, Any]] = []
    valid_reviews: list[dict[str, Any]] = []
    for lane in REVIEW_RELPATHS:
        raw, raw_ref = _read_raw_ref(root, REVIEW_RELPATHS[lane])
        if lane not in failure_set:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ProductDeltaGraphReplicationResultError(
                    f"{lane} blind review is not an object"
                )
            review_errors = _validate_review(
                payload,
                expected_review_id=EXPECTED_REVIEW_IDS[lane],
                blind=blind,
            )
            if review_errors:
                raise ProductDeltaGraphReplicationResultError(
                    f"{lane} blind review failed {len(review_errors)} checks"
                )
            review_terminal_states.append(
                {
                    "lane": lane,
                    "terminal_state": "complete",
                    "review_ref": raw_ref,
                    "retry_fallback_healing_replacement_or_imputation": False,
                }
            )
            valid_reviews.append(
                {
                    "lane": lane,
                    "review_id": payload["review_id"],
                    "review": copy.deepcopy(payload),
                }
            )
            continue

        failure, failure_ref = _read_json_ref(
            root, REVIEW_FAILURE_RELPATHS[lane]
        )
        expected_failure_keys = {
            "schema_version",
            "replication_id",
            "lane",
            "status",
            "terminal_state",
            "failure_class",
            "raw_first_terminal_payload",
            "validation_error_count",
            "validation_error_kinds",
            "retry_fallback_healing_replacement_or_imputation",
            "post_reveal_context_authorized",
            "result_effect",
            "non_claims",
        }
        if (
            set(failure) != expected_failure_keys
            or failure.get("lane") != lane
            or failure.get("status") != "failed"
            or failure.get("terminal_state") != "failed"
            or failure.get("failure_class")
            != "review_shape_validation_failed"
            or failure.get(
                "retry_fallback_healing_replacement_or_imputation"
            )
            is not False
            or failure.get("post_reveal_context_authorized") is not False
            or failure.get("result_effect") != "not_evaluable"
            or failure.get("non_claims") != list(NON_CLAIMS)
        ):
            raise ProductDeltaGraphReplicationResultError(
                f"{lane} blind review failure receipt is malformed"
            )
        output_ref = _required_mapping(
            failure, "raw_first_terminal_payload"
        )
        if (
            output_ref.get("path") != REVIEW_RELPATHS[lane]
            or output_ref.get("sha256") != hashlib.sha256(raw).hexdigest()
            or output_ref.get("bytes") != len(raw)
            or not isinstance(failure.get("validation_error_count"), int)
            or failure.get("validation_error_count", 0) < 1
            or not isinstance(failure.get("validation_error_kinds"), list)
        ):
            raise ProductDeltaGraphReplicationResultError(
                f"{lane} blind review failure custody drifted"
            )
        review_terminal_states.append(
            {
                "lane": lane,
                "terminal_state": "failed",
                "failure_class": failure["failure_class"],
                "raw_first_terminal_payload": raw_ref,
                "failure_receipt": failure_ref,
                "validation_error_count": failure[
                    "validation_error_count"
                ],
                "retry_fallback_healing_replacement_or_imputation": False,
            }
        )

    generation_states = {
        alias: str(receipt["terminal_status"])
        for alias, receipt in _required_mapping(
            sealed, "generation_state_validation"
        ).items()
    }
    preoutput_sealed, _ = _read_json_ref(
        root, DEFAULT_SEALED_MANIFEST_RELPATH
    )
    availability = evaluate_mechanical_availability(
        sealed_manifest=preoutput_sealed,
        sample_terminal_states=generation_states,
        both_blind_reviews_complete=False,
    )
    if availability["gate_passes"] is not False:
        raise ProductDeltaGraphReplicationResultError(
            "review failure did not close the mechanical availability gate"
        )

    consolidation = {
        "schema_version": CONSOLIDATION_SCHEMA_VERSION,
        "replication_id": REPLICATION_ID,
        "status": (
            "valid_frozen_agent_replication_not_evaluable_"
            "required_blind_review_failure"
        ),
        "boundary": {
            **copy.deepcopy(BOUNDARY),
            "codex_blind_review_contexts_completed": 2,
            "codex_post_reveal_contexts_completed": 0,
            "principal_human_review_completed": False,
            "semantic_adjudication_performed": False,
            "scalar_summary_created": False,
            "permission_to_expand_graph_created": False,
        },
        "input_refs": {
            "blind_review_packet": copy.deepcopy(blind_ref),
            "execution_sealed_manifest": copy.deepcopy(sealed_ref),
        },
        "validation": {
            "artifact_error_count": 0,
            "required_review_terminal_failures": len(failure_set),
            "shape_custody_and_declared_enum_validation_only": True,
            "semantic_correctness_validated": False,
        },
        "isolation_receipt": {
            "generation_contexts_attempted": 8,
            "generation_first_terminal_outputs_complete": sum(
                state == "complete" for state in generation_states.values()
            ),
            "generation_first_terminal_failures": sum(
                state != "complete" for state in generation_states.values()
            ),
            "generation_retries_fallbacks_healing_replacements_or_imputations": 0,
            "blind_review_contexts_attempted": 2,
            "blind_review_valid_terminal_results": (
                len(REVIEW_RELPATHS) - len(failure_set)
            ),
            "blind_review_terminal_failures": len(failure_set),
            "blind_review_retries_fallbacks_healing_replacements_or_imputations": 0,
            "post_reveal_contexts_started": 0,
            "reviewers_saw_lineage_before_freeze": False,
            "reviewers_saw_each_other_before_freeze": False,
            "lineage_reveal_performed": False,
            "codex_platform_route_token_and_cost": (
                "unavailable_to_repository_operator"
            ),
        },
        "mechanical_availability": availability,
        "review_terminal_states": review_terminal_states,
        "valid_blind_reviews": valid_reviews,
        "post_reveal": {
            "started": False,
            "reason": (
                "A required blind review lacked a valid first-terminal "
                "result, so the frozen availability gate failed."
            ),
            "contexts_used": 0,
        },
        "replication_interpretation": {
            "state": "not_evaluable",
            "reason": "required_blind_review_terminal_failure",
            "graph_decision_created": False,
            "answer_winner_created": False,
            "interpretation_limit": (
                "The generation pairs were mechanically available, but one "
                "of two required blind reviews failed its frozen response "
                "shape. No recurrence comparison or graph inference is valid."
            ),
        },
        "fan_in_policy": [
            "The valid blind review is preserved but is not sufficient alone.",
            "The invalid first-terminal review payload and its failure receipt are preserved without repair.",
            "Lineage remains sealed because the post-reveal gate did not open.",
            "No post-reveal context, score, vote, winner, or graph decision exists.",
        ],
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe_generated(consolidation)
    return consolidation


def write_consolidation(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    payload, errors = build_consolidation(repo_root=root)
    if errors:
        raise ProductDeltaGraphReplicationResultError(
            f"result validation failed with {len(errors)} error(s)"
        )
    target = _resolve_repo_path(root, CONSOLIDATION_RELPATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_consolidation(
    *, repo_root: Path | str
) -> list[str]:
    root = Path(repo_root).resolve()
    payload, errors = build_consolidation(repo_root=root)
    if errors:
        return errors
    try:
        actual = _resolve_repo_path(root, CONSOLIDATION_RELPATH).read_text(
            encoding="utf-8"
        )
    except OSError:
        return [f"missing generated artifact:{CONSOLIDATION_RELPATH}"]
    if actual != render_json(payload):
        return [f"generated artifact drift:{CONSOLIDATION_RELPATH}"]
    return []


def validate_checked_in_complete_result(
    *, repo_root: Path | str
) -> list[str]:
    """Validate either the gated post-reveal result or honest early closeout."""

    root = Path(repo_root).resolve()
    errors = validate_checked_in_blind_review_inputs(repo_root=root)
    failed_review_lanes = [
        lane
        for lane, relpath in REVIEW_FAILURE_RELPATHS.items()
        if _resolve_repo_path(root, relpath).exists()
    ]
    if failed_review_lanes:
        forbidden_after_failure = [
            *POST_REVEAL_PACKET_RELPATHS.values(),
            *POST_REVEAL_INTERPRETATION_RELPATHS.values(),
        ]
        for relpath in forbidden_after_failure:
            if _resolve_repo_path(root, relpath).exists():
                errors.append(
                    f"post-reveal artifact exists after review failure:{relpath}"
                )
        errors.extend(validate_checked_in_consolidation(repo_root=root))
        return errors
    errors.extend(validate_checked_in_post_reveal_packets(repo_root=root))
    errors.extend(validate_checked_in_consolidation(repo_root=root))
    return errors


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"


def _validate_frozen_inputs(root: Path) -> None:
    try:
        replication_errors = validate_checked_in_replication(repo_root=root)
    except ProductDeltaGraphReplicationError as exc:
        raise ProductDeltaGraphReplicationResultError(
            "pre-output replication validation failed"
        ) from exc
    control_errors = validate_checked_in_screen(repo_root=root)
    if replication_errors or control_errors:
        raise ProductDeltaGraphReplicationResultError(
            "frozen replication or reviewer controls drifted"
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
        _required_text(item, "sample_alias"): item
        for item in _required_list(generation, "packets")
        if isinstance(item, Mapping)
    }
    states: dict[str, dict[str, Any]] = {}
    refs: dict[str, dict[str, Any]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    for alias, lineage_value in _required_mapping(
        preoutput_sealed, "sample_map"
    ).items():
        lineage = _as_mapping(lineage_value, "sample lineage")
        output_relpath = _required_text(
            lineage, "predeclared_terminal_output_path"
        )
        failure_relpath = _required_text(
            lineage, "predeclared_terminal_failure_path"
        )
        output_exists = _resolve_repo_path(root, output_relpath).exists()
        failure_exists = _resolve_repo_path(root, failure_relpath).exists()
        if output_exists == failure_exists:
            raise ProductDeltaGraphReplicationResultError(
                "sample must have exactly one first-terminal state"
            )
        if failure_exists:
            failure, ref = _read_json_ref(root, failure_relpath)
            if (
                failure.get("sample_alias") != alias
                or failure.get("status") != "failed"
                or failure.get("attempt") != 1
            ):
                raise ProductDeltaGraphReplicationResultError(
                    "terminal failure custody drifted"
                )
            states[str(alias)] = {"terminal_status": "failed"}
            refs[str(alias)] = ref
            receipts[str(alias)] = {
                "terminal_status": "failed",
                "first_terminal_result_preserved": False,
                "retry_fallback_healing_replacement_or_imputation": False,
                "semantic_correctness_validated": False,
            }
            continue
        response, ref = _read_json_ref(root, output_relpath)
        compiled, expected_ids, response_schema = _validate_single_generation(
            response=response,
            packet_record=_required_mapping(packets, str(alias)),
            condition=_required_text(lineage, "condition"),
            bundle=bundle,
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
            "answer_quality_validated": False,
        }
    if set(states) != set(SAMPLE_ALIASES):
        raise ProductDeltaGraphReplicationResultError(
            "generation state coverage drifted"
        )
    return states, refs, receipts


def _validate_single_generation(
    *,
    response: Mapping[str, Any],
    packet_record: Mapping[str, Any],
    condition: str,
    bundle: Mapping[str, Any],
) -> tuple[dict[str, Any], list[str], Mapping[str, Any]]:
    bundle_arm_name = CONDITION_TO_BUNDLE_ARM.get(condition)
    if bundle_arm_name is None:
        raise ProductDeltaGraphReplicationResultError(
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
        raise ProductDeltaGraphReplicationResultError(
            "first-terminal output failed deterministic compilation"
        ) from exc
    response_schema = _required_mapping(
        _required_mapping(packet_record, "request_body_projection"),
        "response_schema",
    )
    try:
        _validate_response_lengths(response, response_schema)
    except ProductDeltaGraphVarianceResultError as exc:
        raise ProductDeltaGraphReplicationResultError(
            "first-terminal output failed inherited response bounds"
        ) from exc
    expected_ids = sorted(
        str(item["model_id"])
        for item in _required_list(packet, "pressure_portfolio")
    )
    observed_ids = sorted(
        str(item["model_id"])
        for item in _required_list(response, "candidate_dispositions")
    )
    if observed_ids != expected_ids:
        raise ProductDeltaGraphReplicationResultError(
            "first-terminal output candidate identities drifted"
        )
    return compiled, expected_ids, response_schema


def _build_comparison_cases(
    *,
    source_ref: Mapping[str, Any],
    preoutput_sealed: Mapping[str, Any],
    states: Mapping[str, Mapping[str, Any]],
    state_refs: Mapping[str, Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    plan = _required_list(preoutput_sealed, "comparison_plan")
    if len(plan) != len(COMPARISON_CASE_IDS):
        raise ProductDeltaGraphReplicationResultError(
            "predeclared comparison count drifted"
        )
    cases: list[dict[str, Any]] = []
    lineage: dict[str, Any] = {}
    for case_id, value in zip(COMPARISON_CASE_IDS, plan, strict=True):
        planned = _as_mapping(value, "comparison plan item")
        left = _resolve_new_endpoint(
            endpoint=_required_mapping(planned, "left"),
            states=states,
            state_refs=state_refs,
        )
        right = _resolve_new_endpoint(
            endpoint=_required_mapping(planned, "right"),
            states=states,
            state_refs=state_refs,
        )
        available = left["status"] == right["status"] == "complete"
        pair_lineage: dict[str, Any] = {
            "sealed_pair_id": planned["sealed_pair_id"],
            "sealed_pair_role": planned["sealed_pair_role"],
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
                        "complete_checked_in_agent_replication_pair"
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


def _resolve_new_endpoint(
    *,
    endpoint: Mapping[str, Any],
    states: Mapping[str, Mapping[str, Any]],
    state_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    alias = _required_text(endpoint, "sample_alias")
    state = _required_mapping(states, alias)
    ref = _required_mapping(state_refs, alias)
    result = {
        "status": state["terminal_status"],
        "ref": ref,
        "lineage": {
            "condition": _required_text(endpoint, "condition"),
            "draw_number": endpoint["draw_number"],
            "sample_alias": alias,
            "terminal_state_path": ref["path"],
        },
    }
    if state["terminal_status"] == "complete":
        result["answer"] = str(
            _required_mapping(state, "response")["reconsidered_answer"]
        )
    return result


def _load_and_validate_reviews(
    *, root: Path, blind: Mapping[str, Any]
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    refs: dict[str, dict[str, Any]] = {}
    for lane, relpath in REVIEW_RELPATHS.items():
        payload, ref = _read_json_ref(root, relpath)
        errors = _validate_review(
            payload,
            expected_review_id=EXPECTED_REVIEW_IDS[lane],
            blind=blind,
        )
        if errors:
            raise ProductDeltaGraphReplicationResultError(
                f"{lane} blind review failed {len(errors)} checks"
            )
        payloads[lane] = payload
        refs[lane] = ref
    return payloads, refs


def _validate_review(
    payload: Mapping[str, Any],
    *,
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
        errors.append("top-level keys mismatch")
    if payload.get("schema_version") != REVIEW_SCHEMA_VERSION:
        errors.append("schema version mismatch")
    if payload.get("review_id") != expected_review_id:
        errors.append("review id mismatch")
    if payload.get("fresh_context") is not True:
        errors.append("fresh_context must be true")
    for key in (
        "saw_lineage_before_freeze",
        "saw_sibling_review_before_freeze",
    ):
        if payload.get(key) is not False:
            errors.append(f"{key} must be false")
    if payload.get("boundary") != _review_boundary():
        errors.append("authority boundary mismatch")
    rendered = json.dumps(payload, ensure_ascii=False)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            errors.append(f"privacy marker:{marker}")
    for marker in SEALED_LINEAGE_MARKERS:
        if marker in rendered:
            errors.append(f"sealed lineage marker:{marker}")

    qualification_reviews = payload.get("qualification_reviews")
    if not isinstance(qualification_reviews, list):
        errors.append("qualification_reviews must be an array")
        qualification_reviews = []
    errors.extend(
        _validate_exact_case_ids(
            qualification_reviews,
            _case_ids(_required_list(blind, "qualification_cases")),
        )
    )
    for value in qualification_reviews:
        review = _as_mapping(value, "qualification review")
        evidence_disposition = review.get("evidence_disposition")
        if (
            not isinstance(evidence_disposition, str)
            or evidence_disposition not in QUALIFICATION_DISPOSITIONS
        ):
            errors.append("invalid qualification evidence disposition")
        for key in (
            "supported_observations",
            "missing_evidence",
            "inferences_explicitly_not_made",
            "uncertainty_notes",
        ):
            if not isinstance(review.get(key), list):
                errors.append(f"qualification {key} must be an array")

    duplicate = payload.get("duplicate_null_review")
    if not isinstance(duplicate, Mapping):
        errors.append("duplicate_null_review must be an object")
    else:
        errors.extend(
            _validate_available_review(
                duplicate,
                expected_case_id=str(
                    _required_mapping(blind, "exact_duplicate_null")["case_id"]
                ),
            )
        )

    comparison_reviews = payload.get("comparison_reviews")
    if not isinstance(comparison_reviews, list):
        errors.append("comparison_reviews must be an array")
        comparison_reviews = []
    errors.extend(
        _validate_exact_case_ids(
            comparison_reviews, list(COMPARISON_CASE_IDS)
        )
    )
    blind_cases = _index_cases(_required_list(blind, "comparison_cases"))
    for value in comparison_reviews:
        review = _as_mapping(value, "comparison review")
        case_id = str(review.get("case_id"))
        blind_case = blind_cases.get(case_id)
        if not isinstance(blind_case, Mapping):
            continue
        if blind_case["review_status_required"] == "reviewed":
            errors.extend(
                _validate_available_review(
                    review, expected_case_id=case_id
                )
            )
        else:
            if set(review) != {
                "case_id",
                "review_status",
                "semantic_comparison_attempted",
                "unavailability_basis",
            }:
                errors.append("unavailable review keys mismatch")
            if review.get("review_status") != "not_evaluable":
                errors.append("unavailable review must be not_evaluable")
            if review.get("semantic_comparison_attempted") is not False:
                errors.append("unavailable semantic comparison must be false")

    standdown_reviews = payload.get("standdown_reviews")
    if not isinstance(standdown_reviews, list):
        errors.append("standdown_reviews must be an array")
        standdown_reviews = []
    errors.extend(
        _validate_exact_case_ids(
            standdown_reviews,
            _case_ids(_required_list(blind, "standdown_cases")),
        )
    )
    for value in standdown_reviews:
        review = _as_mapping(value, "standdown review")
        standdown_support = review.get("standdown_support")
        if (
            not isinstance(standdown_support, str)
            or standdown_support not in STANDDOWN_SUPPORT_VALUES
        ):
            errors.append("invalid standdown support")
        for key in (
            "source_basis",
            "risk_of_forced_additional_analysis",
            "semantic_limits_of_mechanical_observation",
        ):
            if not isinstance(review.get(key), list):
                errors.append(f"standdown {key} must be an array")
    return errors


def _validate_available_review(
    review: Mapping[str, Any], *, expected_case_id: str
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
        errors.append(f"{expected_case_id}:available review keys mismatch")
    if review.get("case_id") != expected_case_id:
        errors.append(f"{expected_case_id}:case id mismatch")
    if review.get("review_status") != "reviewed":
        errors.append(f"{expected_case_id}:review_status must be reviewed")
    source_interpretation = review.get("source_interpretation")
    if not isinstance(source_interpretation, Mapping):
        errors.append(f"{expected_case_id}:missing source interpretation")
    else:
        if not isinstance(
            source_interpretation.get("decision_or_question"), str
        ):
            errors.append(f"{expected_case_id}:decision question must be text")
        for key in ("material_constraints", "source_limits"):
            if not isinstance(source_interpretation.get(key), list):
                errors.append(f"{expected_case_id}:{key} must be an array")
    moves = review.get("atomic_moves")
    if not isinstance(moves, list) or not moves:
        errors.append(f"{expected_case_id}:atomic moves are empty")
        moves = []
    move_ids: list[str] = []
    for value in moves:
        move = _as_mapping(value, "atomic move")
        move_id = str(move.get("move_id", ""))
        move_ids.append(move_id)
        presence = move.get("presence")
        if not isinstance(presence, str) or presence not in PRESENCE_VALUES:
            errors.append(f"{expected_case_id}:{move_id}:bad presence")
        reasoning_operation = move.get("reasoning_operation")
        if (
            not isinstance(reasoning_operation, str)
            or reasoning_operation not in REASONING_OPERATION_VALUES
        ):
            errors.append(
                f"{expected_case_id}:{move_id}:bad reasoning operation"
            )
        source_grounding = move.get("source_grounding")
        if (
            not isinstance(source_grounding, str)
            or source_grounding not in SOURCE_GROUNDING_VALUES
        ):
            errors.append(
                f"{expected_case_id}:{move_id}:bad source grounding"
            )
        cognitive_effect = move.get("cognitive_effect")
        if (
            not isinstance(cognitive_effect, str)
            or cognitive_effect not in COGNITIVE_EFFECT_VALUES
        ):
            errors.append(
                f"{expected_case_id}:{move_id}:bad cognitive effect"
            )
        if not isinstance(move.get("source_evidence"), list):
            errors.append(
                f"{expected_case_id}:{move_id}:source evidence must be an array"
            )
    if len(move_ids) != len(set(move_ids)):
        errors.append(f"{expected_case_id}:duplicate move id")
    observations = review.get("arm_observations")
    if not isinstance(observations, Mapping) or set(observations) != {"A", "B"}:
        errors.append(f"{expected_case_id}:arm observations invalid")
    else:
        for label in ("A", "B"):
            observation = observations[label]
            if not isinstance(observation, Mapping):
                errors.append(f"{expected_case_id}:{label}:invalid observation")
                continue
            for key in (
                "preserved_source_value",
                "lost_or_weakened_source_value",
                "unsupported_additions",
                "cognitive_burden",
            ):
                if not isinstance(observation.get(key), list):
                    errors.append(
                        f"{expected_case_id}:{label}:{key} must be an array"
                    )
    material_difference = review.get("material_decision_difference")
    if (
        not isinstance(material_difference, str)
        or material_difference not in MATERIAL_DIFFERENCE_VALUES
    ):
        errors.append(f"{expected_case_id}:invalid material difference")
    if not isinstance(review.get("inspection_limits"), list):
        errors.append(f"{expected_case_id}:inspection limits must be an array")
    return errors


def _validate_post_reveal_interpretation(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    expected_id: str,
    expected_review_id: str,
) -> list[str]:
    errors: list[str] = []
    expected_keys = {
        "schema_version",
        "interpretation_id",
        "source_review_id",
        "fresh_post_reveal_context",
        "saw_sibling_review_or_interpretation",
        "state",
        "pair_assessments",
        "rationale",
        "nonclaims_acknowledged",
    }
    if set(payload) != expected_keys:
        errors.append("post-reveal top-level keys mismatch")
    if (
        payload.get("schema_version")
        != POST_REVEAL_INTERPRETATION_SCHEMA_VERSION
    ):
        errors.append("post-reveal schema mismatch")
    if payload.get("interpretation_id") != expected_id:
        errors.append("post-reveal interpretation id mismatch")
    if payload.get("source_review_id") != expected_review_id:
        errors.append("post-reveal source review id mismatch")
    if payload.get("fresh_post_reveal_context") is not True:
        errors.append("post-reveal fresh context must be true")
    if payload.get("saw_sibling_review_or_interpretation") is not False:
        errors.append("post-reveal sibling visibility must be false")
    state = payload.get("state")
    if (
        not isinstance(state, str)
        or state not in REVIEW_SPECIFIC_PATTERN_STATES
    ):
        errors.append("post-reveal state is invalid")
    if payload.get("nonclaims_acknowledged") != list(NON_CLAIMS):
        errors.append("post-reveal nonclaims drifted")
    if not isinstance(payload.get("rationale"), str):
        errors.append("post-reveal rationale must be text")

    assessments = payload.get("pair_assessments")
    if not isinstance(assessments, list):
        errors.append("post-reveal pair assessments must be an array")
        assessments = []
    errors.extend(
        _validate_exact_case_ids(assessments, list(COMPARISON_CASE_IDS))
    )
    reveal_by_id = _index_cases(
        _required_list(packet, "comparison_reveal")
    )
    for value in assessments:
        assessment = _as_mapping(value, "post-reveal pair assessment")
        case_id = str(assessment.get("case_id"))
        reveal = reveal_by_id.get(case_id)
        if not isinstance(reveal, Mapping):
            continue
        expected_assessment_keys = {
            "case_id",
            "sealed_pair_role",
            "frozen_material_decision_difference",
            "cited_frozen_move_ids",
            "recurrence_observation",
            "burden_harm_or_lost_value_observation",
            "uncertainty",
        }
        if set(assessment) != expected_assessment_keys:
            errors.append(f"{case_id}:post-reveal pair keys mismatch")
        if assessment.get("sealed_pair_role") != reveal.get(
            "sealed_pair_role"
        ):
            errors.append(f"{case_id}:sealed pair role mismatch")
        if assessment.get(
            "frozen_material_decision_difference"
        ) != reveal.get("frozen_material_decision_difference"):
            errors.append(f"{case_id}:frozen material read mismatch")
        cited = assessment.get("cited_frozen_move_ids")
        if not isinstance(cited, list) or not set(cited).issubset(
            set(_required_list(reveal, "frozen_move_ids"))
        ):
            errors.append(f"{case_id}:cited move IDs are not frozen")
        for key in (
            "recurrence_observation",
            "burden_harm_or_lost_value_observation",
            "uncertainty",
        ):
            if not isinstance(assessment.get(key), str):
                errors.append(f"{case_id}:{key} must be text")
    rendered = json.dumps(payload, ensure_ascii=False)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            errors.append(f"post-reveal privacy marker:{marker}")
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
            label: {
                "preserved_source_value": ["string"],
                "lost_or_weakened_source_value": ["string"],
                "unsupported_additions": ["string"],
                "cognitive_burden": ["string"],
            }
            for label in ("A", "B")
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


def _blind_review_task_wrapper(*, review_id: str) -> str:
    return (
        "Run one isolated blind Product Delta review. Use only the supplied "
        "packet; do not inspect the repository, condition lineage, previous "
        "results, or sibling work. Complete every qualification, duplicate, "
        "comparison, and stand-down record in the exact declared order. Use "
        "one to four concise atomic moves per available comparison. Return "
        f"only one JSON object with review_id {review_id!r}, the exact response "
        "envelope keys and enums, and no markdown. Do not score, rank, vote, "
        "select a winner, infer graph lineage, or claim quality or usefulness."
    )


def _post_reveal_task_wrapper(
    *, interpretation_id: str, source_review_id: str
) -> str:
    return (
        "Run one isolated post-reveal interpretation over exactly one already-"
        "frozen blind review. Use only the supplied packet. Address every "
        "comparison in order and cite only frozen move IDs. Do not add or "
        "change answer judgments, inspect a sibling review, count into a score "
        "or effect size, rank, vote, or choose a winner. Return only one JSON "
        f"object with interpretation_id {interpretation_id!r}, source_review_id "
        f"{source_review_id!r}, the exact response-contract keys, and no "
        "markdown."
    )


def _validate_exact_case_ids(
    records: Sequence[Any], expected: Sequence[str]
) -> list[str]:
    actual = [
        str(item.get("case_id"))
        for item in records
        if isinstance(item, Mapping)
    ]
    if actual != list(expected):
        return ["case ids or order mismatch"]
    return []


def _case_ids(value: Sequence[Any]) -> list[str]:
    ids = [
        str(item.get("case_id"))
        for item in value
        if isinstance(item, Mapping) and item.get("case_id")
    ]
    if len(ids) != len(value) or len(ids) != len(set(ids)):
        raise ProductDeltaGraphReplicationResultError(
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
        raise ProductDeltaGraphReplicationResultError(
            "case identity set is malformed"
        )
    return result


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw, ref = _read_raw_ref(root, relpath)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProductDeltaGraphReplicationResultError(
            f"invalid JSON input:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphReplicationResultError(
            f"JSON input is not an object:{relpath}"
        )
    return payload, ref


def _read_text_ref(
    root: Path, relpath: str
) -> tuple[str, dict[str, Any]]:
    raw, ref = _read_raw_ref(root, relpath)
    try:
        return raw.decode("utf-8"), ref
    except UnicodeDecodeError as exc:
        raise ProductDeltaGraphReplicationResultError(
            f"text input is not UTF-8:{relpath}"
        ) from exc


def _read_raw_ref(
    root: Path, relpath: str
) -> tuple[bytes, dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProductDeltaGraphReplicationResultError(
            f"missing input:{relpath}"
        ) from exc
    return raw, {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    if not relpath or Path(relpath).is_absolute():
        raise ProductDeltaGraphReplicationResultError(
            "repository-relative path required"
        )
    resolved = (root / relpath).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphReplicationResultError(
            "path escapes repository root"
        ) from exc
    return resolved


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise ProductDeltaGraphReplicationResultError(
            f"required object missing:{key}"
        )
    return item


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise ProductDeltaGraphReplicationResultError(
            f"required list missing:{key}"
        )
    return item


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ProductDeltaGraphReplicationResultError(
            f"required text missing:{key}"
        )
    return item


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProductDeltaGraphReplicationResultError(
            f"{label} is not an object"
        )
    return value


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json_value(value: Any) -> str:
    canonical = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    return _sha256_text(canonical)


def _assert_safe_public(payload: Mapping[str, Any]) -> None:
    rendered = render_json(payload)
    for marker in SECRET_MARKERS + SEALED_LINEAGE_MARKERS:
        if marker in rendered:
            raise ProductDeltaGraphReplicationResultError(
                "blind packet contains secret or sealed-lineage marker"
            )


def _assert_safe_generated(payload: Mapping[str, Any]) -> None:
    rendered = render_json(payload)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            raise ProductDeltaGraphReplicationResultError(
                "generated artifact contains forbidden secret or local path"
            )
