"""Preserve and consolidate the authorized graph-review-envelope v2 run.

This module stays inside the existing offline Product Delta owner. It imports
first-terminal Codex outputs without repair, validates them against the frozen
v2 schemas and the existing Product Delta validators, opens the deterministic
lineage-reveal gate only after both blind lanes pass, and preserves the two
review vectors without scoring or voting.

It does not invoke Codex, call a provider, generate or reinterpret answers,
change the graph, or authorize a retry.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_replication_result import (
    COMPARISON_CASE_IDS,
    NON_CLAIMS,
    POST_REVEAL_INTERPRETATION_SCHEMA_VERSION as POST_REVEAL_V1,
    REVIEW_SPECIFIC_PATTERN_STATES,
    _validate_post_reveal_interpretation,
)
from engine.system_b.product_delta_graph_review_envelope_v2 import (
    CONTRACT_RELPATH,
    EXECUTION_MANIFEST_RELPATH,
    FUTURE_CONSOLIDATION_RELPATH,
    FUTURE_INTERPRETATION_RELPATHS,
    FUTURE_POST_REVEAL_PACKET_RELPATHS,
    FUTURE_REVIEW_FAILURE_RELPATHS,
    FUTURE_REVIEW_RELPATHS,
    INTERPRETATION_IDS,
    LANES,
    PACKET_RELPATHS,
    POST_REVEAL_SCHEMA_RELPATHS,
    REVIEW_IDS,
    SCHEMA_RELPATHS,
    build_artifacts as build_frozen_envelope_artifacts,
    render_json,
    validate_json_schema_subset,
    validate_v2_review,
)


RESULT_ID = "lolla-agent-only-graph-review-envelope-v2"
DATE = "2026-07-24"
POST_REVEAL_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_graph_replication_post_reveal_packet.v2"
)
CONSOLIDATION_SCHEMA_VERSION = (
    "lolla.product_delta_graph_review_envelope_v2_consolidation.v1"
)
BLIND_TERMINAL_RECEIPT_RELPATHS = {
    lane: (
        "reviews/codex-assisted/agent-only-graph-review-envelope-v2/"
        f"pair-review-{lane}-terminal-receipt.json"
    )
    for lane in LANES
}
POST_TERMINAL_RECEIPT_RELPATHS = {
    lane: (
        "reviews/codex-assisted/agent-only-graph-review-envelope-v2/"
        f"pattern-interpretation-{lane}-terminal-receipt.json"
    )
    for lane in LANES
}
POST_FAILURE_RELPATHS = {
    lane: (
        "reviews/codex-assisted/agent-only-graph-review-envelope-v2/"
        f"pattern-interpretation-{lane}-terminal-failure.json"
    )
    for lane in LANES
}
EXPECTED_V1_INTERPRETATION_IDS = {
    "primary": "agent-graph-replication-pattern-primary-v1",
    "skeptical": "agent-graph-replication-pattern-skeptical-v1",
}
EXPECTED_V1_REVIEW_IDS = {
    "primary": "agent-graph-replication-pair-primary-v1",
    "skeptical": "agent-graph-replication-pair-skeptical-v1",
}
OVERALL_STATES = {
    "cross_condition_difference_more_consistent_than_"
    "observed_within_condition_variation",
    "cross_condition_difference_not_distinguishable_from_"
    "observed_within_condition_variation",
    "mixed_or_reviewer_disagreement",
    "not_evaluable",
}


class ProductDeltaGraphReviewEnvelopeV2ResultError(ValueError):
    """Sanitized deterministic v2 result-custody failure."""


def validate_preflight(*, repo_root: Path | str) -> list[str]:
    """Validate frozen semantic inputs while permitting authorized outputs."""

    root = Path(repo_root).resolve()
    errors: list[str] = []
    try:
        expected = build_frozen_envelope_artifacts(repo_root=root)
    except Exception as exc:  # sanitized at this deterministic boundary
        return [f"frozen envelope build failed:{type(exc).__name__}"]
    for relpath, payload in expected.items():
        target = _resolve_repo_path(root, relpath)
        try:
            actual = target.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing frozen envelope artifact:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"frozen envelope artifact drift:{relpath}")
    return errors


def import_blind_review(
    *,
    repo_root: Path | str,
    lane: str,
    source_path: Path | str,
    process_exit_code: int,
    codex_cli_version: str,
) -> str:
    """Preserve one blind lane's exact first-terminal state without repair."""

    root = Path(repo_root).resolve()
    _require_lane(lane)
    _require_clean_preflight(root)
    _assert_terminal_unclaimed(
        root,
        (
            FUTURE_REVIEW_RELPATHS[lane],
            FUTURE_REVIEW_FAILURE_RELPATHS[lane],
            BLIND_TERMINAL_RECEIPT_RELPATHS[lane],
        ),
    )
    packet = _read_json(root, PACKET_RELPATHS[lane])
    schema = _read_json(root, SCHEMA_RELPATHS[lane])
    raw, read_error = _read_external_first_terminal(source_path)
    errors: list[str] = []
    payload: Mapping[str, Any] | None = None
    if read_error:
        errors.append(read_error)
    else:
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            errors.append("terminal payload is not JSON")
        else:
            if not isinstance(decoded, Mapping):
                errors.append("terminal payload is not an object")
            else:
                payload = decoded
                errors.extend(
                    validate_v2_review(
                        decoded,
                        blind=packet,
                        lane=lane,
                        schema=schema,
                    )
                )
    if process_exit_code != 0:
        errors.append(f"codex exec exited nonzero:{process_exit_code}")

    output_ref: dict[str, Any] | None = None
    if raw is not None:
        output_target = _resolve_repo_path(root, FUTURE_REVIEW_RELPATHS[lane])
        output_target.parent.mkdir(parents=True, exist_ok=True)
        output_target.write_bytes(raw)
        output_ref = _ref_for_raw(FUTURE_REVIEW_RELPATHS[lane], raw)

    state = "failed" if errors else "complete"
    receipt = _terminal_receipt(
        stage="blind_review",
        lane=lane,
        state=state,
        process_exit_code=process_exit_code,
        codex_cli_version=codex_cli_version,
        output_ref=output_ref,
        errors=errors,
    )
    _write_json(
        root, BLIND_TERMINAL_RECEIPT_RELPATHS[lane], receipt
    )
    if errors:
        failure = _failure_receipt(
            stage="blind_review",
            lane=lane,
            output_ref=output_ref,
            errors=errors,
            result_effect="post_reveal_gate_closed_and_not_evaluable",
        )
        _write_json(
            root, FUTURE_REVIEW_FAILURE_RELPATHS[lane], failure
        )
    return state


def build_post_reveal_packets(
    *, repo_root: Path | str
) -> dict[str, dict[str, Any]]:
    """Build one deterministic reveal packet per valid frozen v2 review."""

    root = Path(repo_root).resolve()
    _require_clean_preflight(root)
    reviews, review_refs = _load_valid_blind_reviews(root)
    sealed = _read_json(root, EXECUTION_MANIFEST_RELPATH)
    sealed_ref = _ref_for_path(root, EXECUTION_MANIFEST_RELPATH)
    lineage = _required_mapping(sealed, "comparison_lineage")
    availability = _mechanical_availability(root, reviews_complete=True)
    if availability["gate_passes"] is not True:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            "post-reveal gate is closed"
        )

    packets: dict[str, dict[str, Any]] = {}
    for lane in LANES:
        review = reviews[lane]
        review_cases = _index_cases(
            _required_list(review, "comparison_reviews")
        )
        reveal_rows: list[dict[str, Any]] = []
        for case_id in COMPARISON_CASE_IDS:
            case_lineage = _required_mapping(lineage, case_id)
            frozen_review = _required_mapping(review_cases, case_id)
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
                        move["move_id"]
                        for move in _required_list(
                            frozen_review, "atomic_moves"
                        )
                    ],
                }
            )
        schema_ref = _ref_for_path(
            root, POST_REVEAL_SCHEMA_RELPATHS[lane]
        )
        packets[lane] = {
            "schema_version": POST_REVEAL_PACKET_SCHEMA_VERSION,
            "result_id": RESULT_ID,
            "lane": lane,
            "status": "frozen_v2_review_plus_deterministic_lineage_reveal",
            "purpose": (
                "Interpret recurrence only inside this frozen blind review. "
                "Do not create new answer or source judgments."
            ),
            "input_refs": {
                "frozen_envelope_contract": _ref_for_path(
                    root, CONTRACT_RELPATH
                ),
                "blind_review_packet": _ref_for_path(
                    root, PACKET_RELPATHS[lane]
                ),
                "blind_review_schema": _ref_for_path(
                    root, SCHEMA_RELPATHS[lane]
                ),
                "execution_sealed_manifest": sealed_ref,
                "frozen_review": review_refs[lane],
            },
            "mechanical_availability": copy.deepcopy(availability),
            "frozen_review": copy.deepcopy(review),
            "comparison_reveal": reveal_rows,
            "structured_output_contract": {
                "authoritative_schema": schema_ref,
                "execution_flag": "--output-schema",
                "schema_proves_shape_not_semantic_correctness": True,
                "first_terminal_payload_only": True,
                "retry_fallback_healing_replacement_or_reformatting": False,
            },
            "task_wrapper": _post_reveal_task_wrapper(lane=lane),
            "forbidden_behavior": [
                "Do not add, remove, rewrite, or reclassify atomic moves.",
                "Do not reinterpret the source or answers.",
                "Do not inspect or infer the sibling review.",
                "Do not score, rank, vote, choose a winner, or compute an effect size.",
                "Do not claim graph causation, relevance, correctness, value, answer quality, expected behavior, or human usefulness.",
            ],
            "non_claims": list(NON_CLAIMS),
        }
    return packets


def write_post_reveal_packets(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    for lane, payload in build_post_reveal_packets(
        repo_root=root
    ).items():
        target = _resolve_repo_path(
            root, FUTURE_POST_REVEAL_PACKET_RELPATHS[lane]
        )
        if target.exists():
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                "post-reveal packet is already frozen"
            )
        _write_json(root, FUTURE_POST_REVEAL_PACKET_RELPATHS[lane], payload)


def validate_post_reveal_packets(
    *, repo_root: Path | str
) -> list[str]:
    root = Path(repo_root).resolve()
    try:
        expected = build_post_reveal_packets(repo_root=root)
    except ProductDeltaGraphReviewEnvelopeV2ResultError as exc:
        return [str(exc)]
    errors: list[str] = []
    for lane, payload in expected.items():
        relpath = FUTURE_POST_REVEAL_PACKET_RELPATHS[lane]
        try:
            actual = _resolve_repo_path(root, relpath).read_text(
                encoding="utf-8"
            )
        except OSError:
            errors.append(f"missing post-reveal packet:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"post-reveal packet drift:{relpath}")
    return errors


def import_post_reveal_interpretation(
    *,
    repo_root: Path | str,
    lane: str,
    source_path: Path | str,
    process_exit_code: int,
    codex_cli_version: str,
) -> str:
    """Preserve one post-reveal first-terminal state without repair."""

    root = Path(repo_root).resolve()
    _require_lane(lane)
    packet_errors = validate_post_reveal_packets(repo_root=root)
    if packet_errors:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            "post-reveal packet custody drifted"
        )
    _assert_terminal_unclaimed(
        root,
        (
            FUTURE_INTERPRETATION_RELPATHS[lane],
            POST_FAILURE_RELPATHS[lane],
            POST_TERMINAL_RECEIPT_RELPATHS[lane],
        ),
    )
    packet = _read_json(
        root, FUTURE_POST_REVEAL_PACKET_RELPATHS[lane]
    )
    schema = _read_json(root, POST_REVEAL_SCHEMA_RELPATHS[lane])
    raw, read_error = _read_external_first_terminal(source_path)
    errors: list[str] = []
    if read_error:
        errors.append(read_error)
    else:
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            errors.append("terminal payload is not JSON")
        else:
            if not isinstance(decoded, Mapping):
                errors.append("terminal payload is not an object")
            else:
                errors.extend(validate_json_schema_subset(decoded, schema))
                errors.extend(
                    _validate_v2_post_reveal(
                        decoded, packet=packet, lane=lane
                    )
                )
    if process_exit_code != 0:
        errors.append(f"codex exec exited nonzero:{process_exit_code}")

    output_ref: dict[str, Any] | None = None
    if raw is not None:
        output_target = _resolve_repo_path(
            root, FUTURE_INTERPRETATION_RELPATHS[lane]
        )
        output_target.parent.mkdir(parents=True, exist_ok=True)
        output_target.write_bytes(raw)
        output_ref = _ref_for_raw(
            FUTURE_INTERPRETATION_RELPATHS[lane], raw
        )

    state = "failed" if errors else "complete"
    receipt = _terminal_receipt(
        stage="post_reveal_interpretation",
        lane=lane,
        state=state,
        process_exit_code=process_exit_code,
        codex_cli_version=codex_cli_version,
        output_ref=output_ref,
        errors=errors,
    )
    _write_json(root, POST_TERMINAL_RECEIPT_RELPATHS[lane], receipt)
    if errors:
        _write_json(
            root,
            POST_FAILURE_RELPATHS[lane],
            _failure_receipt(
                stage="post_reveal_interpretation",
                lane=lane,
                output_ref=output_ref,
                errors=errors,
                result_effect="not_evaluable",
            ),
        )
    return state


def build_consolidation(
    *, repo_root: Path | str
) -> dict[str, Any]:
    """Preserve every vector and derive only the declared alignment state."""

    root = Path(repo_root).resolve()
    _require_clean_preflight(root)
    blind_receipts = _load_terminal_receipts(
        root, BLIND_TERMINAL_RECEIPT_RELPATHS
    )
    blind_failures = [
        lane
        for lane in LANES
        if blind_receipts[lane]["terminal_state"] != "complete"
    ]
    reviews: dict[str, dict[str, Any]] = {}
    review_refs: dict[str, dict[str, Any]] = {}
    if not blind_failures:
        reviews, review_refs = _load_valid_blind_reviews(root)

    post_receipts: dict[str, dict[str, Any]] = {}
    interpretations: dict[str, dict[str, Any]] = {}
    interpretation_refs: dict[str, dict[str, Any]] = {}
    post_failures: list[str] = []
    if not blind_failures:
        packet_errors = validate_post_reveal_packets(repo_root=root)
        if packet_errors:
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                "post-reveal packet custody drifted"
            )
        post_receipts = _load_terminal_receipts(
            root, POST_TERMINAL_RECEIPT_RELPATHS
        )
        post_failures = [
            lane
            for lane in LANES
            if post_receipts[lane]["terminal_state"] != "complete"
        ]
        if not post_failures:
            for lane in LANES:
                payload = _read_json(
                    root, FUTURE_INTERPRETATION_RELPATHS[lane]
                )
                packet = _read_json(
                    root, FUTURE_POST_REVEAL_PACKET_RELPATHS[lane]
                )
                errors = _validate_v2_post_reveal(
                    payload, packet=packet, lane=lane
                )
                errors.extend(
                    validate_json_schema_subset(
                        payload,
                        _read_json(
                            root, POST_REVEAL_SCHEMA_RELPATHS[lane]
                        ),
                    )
                )
                if errors:
                    raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                        f"{lane} post-reveal interpretation drifted"
                    )
                interpretations[lane] = payload
                interpretation_refs[lane] = _ref_for_path(
                    root, FUTURE_INTERPRETATION_RELPATHS[lane]
                )

    availability = _mechanical_availability(
        root, reviews_complete=not blind_failures
    )
    if blind_failures or post_failures:
        overall_state = "not_evaluable"
    else:
        states = [interpretations[lane]["state"] for lane in LANES]
        if (
            len(set(states)) == 1
            and states[0] != "review_specific_pattern_mixed_or_uncertain"
        ):
            overall_state = states[0]
        else:
            overall_state = "mixed_or_reviewer_disagreement"
    if overall_state not in OVERALL_STATES:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            "invalid overall state"
        )

    consolidation: dict[str, Any] = {
        "schema_version": CONSOLIDATION_SCHEMA_VERSION,
        "result_id": RESULT_ID,
        "date": DATE,
        "status": (
            "complete_agent_only_v2_review_diagnostic"
            if not blind_failures and not post_failures
            else "complete_not_evaluable_terminal_failure_preserved"
        ),
        "evidence_class": (
            "checked_in_safe_agent_only_single_case_product_delta_review_"
            "not_human_provider_causal_quality_usefulness_or_runtime_evidence"
        ),
        "boundary": {
            "frozen_generation_outputs_reused": 8,
            "new_generation_contexts": 0,
            "blind_review_contexts_attempted": 2,
            "conditional_post_reveal_contexts_attempted": (
                0 if blind_failures else 2
            ),
            "maximum_codex_contexts": 4,
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_usd": 0.0,
            "codex_platform_route_tokens_and_economic_cost": (
                "unavailable_to_repository_operator_not_claimed_zero"
            ),
            "retry_fallback_healing_replacement_reformatting_or_salvage": 0,
            "principal_human_review_completed": False,
            "graph_planner_compiler_runtime_skill_or_interface_changed": False,
            "score_vote_winner_or_graph_decision_created": False,
        },
        "input_refs": {
            "frozen_envelope_contract": _ref_for_path(
                root, CONTRACT_RELPATH
            ),
            "execution_sealed_manifest": _ref_for_path(
                root, EXECUTION_MANIFEST_RELPATH
            ),
            "blind_packets": {
                lane: _ref_for_path(root, PACKET_RELPATHS[lane])
                for lane in LANES
            },
            "blind_schemas": {
                lane: _ref_for_path(root, SCHEMA_RELPATHS[lane])
                for lane in LANES
            },
            "blind_reviews": review_refs,
            "blind_terminal_receipts": {
                lane: _ref_for_path(
                    root, BLIND_TERMINAL_RECEIPT_RELPATHS[lane]
                )
                for lane in LANES
            },
            "post_reveal_packets": (
                {}
                if blind_failures
                else {
                    lane: _ref_for_path(
                        root, FUTURE_POST_REVEAL_PACKET_RELPATHS[lane]
                    )
                    for lane in LANES
                }
            ),
            "post_reveal_schemas": (
                {}
                if blind_failures
                else {
                    lane: _ref_for_path(
                        root, POST_REVEAL_SCHEMA_RELPATHS[lane]
                    )
                    for lane in LANES
                }
            ),
            "post_reveal_interpretations": interpretation_refs,
            "post_terminal_receipts": (
                {}
                if blind_failures
                else {
                    lane: _ref_for_path(
                        root, POST_TERMINAL_RECEIPT_RELPATHS[lane]
                    )
                    for lane in LANES
                }
            ),
        },
        "mechanical_availability": availability,
        "terminal_state_summary": {
            "blind_reviews": {
                lane: blind_receipts[lane]["terminal_state"]
                for lane in LANES
            },
            "post_reveal_interpretations": (
                {lane: "not_started" for lane in LANES}
                if blind_failures
                else {
                    lane: post_receipts[lane]["terminal_state"]
                    for lane in LANES
                }
            ),
            "failed_blind_lanes": blind_failures,
            "failed_post_reveal_lanes": post_failures,
        },
        "blind_review_vectors": _fan_in_blind_vectors(reviews),
        "post_reveal_vectors": [
            {"lane": lane, **copy.deepcopy(interpretations[lane])}
            for lane in LANES
            if lane in interpretations
        ],
        "interpretation": {
            "state": overall_state,
            "review_specific_states": {
                lane: interpretations[lane]["state"]
                for lane in LANES
                if lane in interpretations
            },
            "fan_in_rule": (
                "If a required first-terminal result fails, report "
                "not_evaluable. If both post-reveal lanes return the same "
                "non-mixed state, preserve that alignment; otherwise report "
                "mixed_or_reviewer_disagreement. This is custody, not a vote "
                "or semantic truth."
            ),
            "every_available_vector_preserved": True,
            "no_graph_decision_created": True,
        },
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe(consolidation)
    return consolidation


def write_consolidation(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    target = _resolve_repo_path(root, FUTURE_CONSOLIDATION_RELPATH)
    if target.exists():
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            "consolidation is already frozen"
        )
    _write_json(
        root,
        FUTURE_CONSOLIDATION_RELPATH,
        build_consolidation(repo_root=root),
    )


def validate_complete_result(*, repo_root: Path | str) -> list[str]:
    root = Path(repo_root).resolve()
    errors = validate_preflight(repo_root=root)
    if errors:
        return errors
    try:
        expected = build_consolidation(repo_root=root)
    except ProductDeltaGraphReviewEnvelopeV2ResultError as exc:
        return [str(exc)]
    target = _resolve_repo_path(root, FUTURE_CONSOLIDATION_RELPATH)
    try:
        actual = target.read_text(encoding="utf-8")
    except OSError:
        return [f"missing consolidation:{FUTURE_CONSOLIDATION_RELPATH}"]
    if actual != render_json(expected):
        errors.append("consolidation drift")
    return errors


def _load_valid_blind_reviews(
    root: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    reviews: dict[str, dict[str, Any]] = {}
    refs: dict[str, dict[str, Any]] = {}
    for lane in LANES:
        if _resolve_repo_path(
            root, FUTURE_REVIEW_FAILURE_RELPATHS[lane]
        ).exists():
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                f"{lane} blind review failed"
            )
        payload = _read_json(root, FUTURE_REVIEW_RELPATHS[lane])
        errors = validate_v2_review(
            payload,
            blind=_read_json(root, PACKET_RELPATHS[lane]),
            lane=lane,
            schema=_read_json(root, SCHEMA_RELPATHS[lane]),
        )
        if errors:
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                f"{lane} blind review failed {len(errors)} checks"
            )
        reviews[lane] = payload
        refs[lane] = _ref_for_path(root, FUTURE_REVIEW_RELPATHS[lane])
    return reviews, refs


def _validate_v2_post_reveal(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    lane: str,
) -> list[str]:
    adapted = copy.deepcopy(dict(payload))
    adapted["schema_version"] = POST_REVEAL_V1
    adapted["interpretation_id"] = EXPECTED_V1_INTERPRETATION_IDS[lane]
    adapted["source_review_id"] = EXPECTED_V1_REVIEW_IDS[lane]
    return _validate_post_reveal_interpretation(
        adapted,
        packet=packet,
        expected_id=EXPECTED_V1_INTERPRETATION_IDS[lane],
        expected_review_id=EXPECTED_V1_REVIEW_IDS[lane],
    )


def _mechanical_availability(
    root: Path, *, reviews_complete: bool
) -> dict[str, Any]:
    packet = _read_json(root, PACKET_RELPATHS["primary"])
    availability = copy.deepcopy(
        _required_mapping(packet, "pre_review_mechanical_availability")
    )
    pair_receipts = _required_list(availability, "pair_receipts")
    all_pairs_available = all(
        isinstance(row, Mapping)
        and row.get("availability") == "available"
        for row in pair_receipts
    )
    availability["both_blind_reviews_complete"] = reviews_complete
    availability["gate_passes"] = (
        all_pairs_available and reviews_complete
    )
    availability["result_if_closed_now"] = (
        "eligible_for_post_reveal"
        if availability["gate_passes"]
        else "not_evaluable"
    )
    availability["v2_review_envelope_applied"] = True
    return availability


def _fan_in_blind_vectors(
    reviews: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    if not reviews:
        return {
            "qualification_reviews": [],
            "duplicate_null_review": [],
            "comparison_reviews": [],
            "standdown_reviews": [],
            "reason": "required blind review pair was not valid",
        }
    primary_packet = None
    qualification_ids = [
        row["case_id"]
        for row in reviews["primary"]["qualification_reviews"]
    ]
    comparison_ids = list(COMPARISON_CASE_IDS)
    standdown_ids = [
        row["case_id"]
        for row in reviews["primary"]["standdown_reviews"]
    ]

    def fan_in(key: str, case_ids: Sequence[str]) -> list[dict[str, Any]]:
        return [
            {
                "case_id": case_id,
                "reviewer_reads": [
                    {
                        "lane": lane,
                        "review_id": reviews[lane]["review_id"],
                        **copy.deepcopy(
                            dict(
                                _required_mapping(
                                    _index_cases(
                                        _required_list(
                                            reviews[lane], key
                                        )
                                    ),
                                    case_id,
                                )
                            )
                        ),
                    }
                    for lane in LANES
                ],
            }
            for case_id in case_ids
        ]

    del primary_packet
    return {
        "qualification_reviews": fan_in(
            "qualification_reviews", qualification_ids
        ),
        "duplicate_null_review": [
            {
                "lane": lane,
                "review_id": reviews[lane]["review_id"],
                **copy.deepcopy(
                    dict(
                        _required_mapping(
                            reviews[lane], "duplicate_null_review"
                        )
                    )
                ),
            }
            for lane in LANES
        ],
        "comparison_reviews": fan_in(
            "comparison_reviews", comparison_ids
        ),
        "standdown_reviews": fan_in(
            "standdown_reviews", standdown_ids
        ),
        "fan_in_policy": (
            "Every read remains attributable to its lane. Agreement is not "
            "truth and disagreement is not resolved by scoring or voting."
        ),
    }


def _terminal_receipt(
    *,
    stage: str,
    lane: str,
    state: str,
    process_exit_code: int,
    codex_cli_version: str,
    output_ref: Mapping[str, Any] | None,
    errors: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema_version": (
            "lolla.product_delta_graph_review_envelope_v2_terminal_receipt.v1"
        ),
        "result_id": RESULT_ID,
        "stage": stage,
        "lane": lane,
        "terminal_state": state,
        "process_exit_code": process_exit_code,
        "codex_cli_version": codex_cli_version,
        "output_ref": (
            None if output_ref is None else copy.deepcopy(dict(output_ref))
        ),
        "validation_error_count": len(errors),
        "validation_error_kinds": sorted(set(errors)),
        "first_terminal_state_preserved": True,
        "retry_fallback_healing_replacement_reformatting_or_salvage": False,
        "repository_provider_api_calls": 0,
        "repository_provider_api_cost_usd": 0.0,
        "codex_platform_route_tokens_and_economic_cost": (
            "unavailable_to_repository_operator_not_claimed_zero"
        ),
    }


def _failure_receipt(
    *,
    stage: str,
    lane: str,
    output_ref: Mapping[str, Any] | None,
    errors: Sequence[str],
    result_effect: str,
) -> dict[str, Any]:
    return {
        "schema_version": (
            "lolla.product_delta_graph_review_envelope_v2_failure.v1"
        ),
        "result_id": RESULT_ID,
        "stage": stage,
        "lane": lane,
        "status": "failed",
        "terminal_state": "failed",
        "failure_class": "first_terminal_or_shape_validation_failed",
        "raw_first_terminal_payload": (
            None if output_ref is None else copy.deepcopy(dict(output_ref))
        ),
        "validation_error_count": len(errors),
        "validation_error_kinds": sorted(set(errors)),
        "retry_fallback_healing_replacement_reformatting_or_salvage": False,
        "result_effect": result_effect,
        "non_claims": list(NON_CLAIMS),
    }


def _post_reveal_task_wrapper(*, lane: str) -> str:
    return (
        "Run one isolated post-reveal interpretation over exactly one already-"
        "frozen v2 blind review. Use only this packet. Address all eight "
        "comparisons in order and cite only frozen move IDs. Do not add or "
        "change answer judgments, inspect or infer a sibling review, count "
        "into a score or effect size, rank, vote, or choose a winner. The JSON "
        "Schema supplied through --output-schema is the sole response-shape "
        "authority. Return exactly one JSON object with interpretation_id "
        f"{INTERPRETATION_IDS[lane]!r}, source_review_id "
        f"{REVIEW_IDS[lane]!r}, and no markdown."
    )


def _load_terminal_receipts(
    root: Path, relpaths: Mapping[str, str]
) -> dict[str, dict[str, Any]]:
    receipts: dict[str, dict[str, Any]] = {}
    for lane in LANES:
        receipt = _read_json(root, relpaths[lane])
        if receipt.get("lane") != lane:
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                f"{lane} terminal receipt identity drifted"
            )
        if receipt.get("terminal_state") not in {"complete", "failed"}:
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                f"{lane} terminal receipt state invalid"
            )
        receipts[lane] = receipt
    return receipts


def _require_clean_preflight(root: Path) -> None:
    errors = validate_preflight(repo_root=root)
    if errors:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            f"frozen envelope preflight failed {len(errors)} checks"
        )


def _read_external_first_terminal(
    source_path: Path | str,
) -> tuple[bytes | None, str | None]:
    try:
        return Path(source_path).resolve().read_bytes(), None
    except OSError:
        return None, "first-terminal output is unavailable"


def _assert_terminal_unclaimed(
    root: Path, relpaths: Sequence[str]
) -> None:
    if any(_resolve_repo_path(root, relpath).exists() for relpath in relpaths):
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            "terminal state is already frozen"
        )


def _write_json(root: Path, relpath: str, payload: Mapping[str, Any]) -> None:
    _assert_safe(payload)
    target = _resolve_repo_path(root, relpath)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_json(payload), encoding="utf-8")


def _read_json(root: Path, relpath: str) -> dict[str, Any]:
    target = _resolve_repo_path(root, relpath)
    try:
        payload = json.loads(target.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            f"required JSON unavailable or invalid:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            f"required JSON is not an object:{relpath}"
        )
    return payload


def _ref_for_path(root: Path, relpath: str) -> dict[str, Any]:
    try:
        raw = _resolve_repo_path(root, relpath).read_bytes()
    except OSError as exc:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            f"required artifact unavailable:{relpath}"
        ) from exc
    return _ref_for_raw(relpath, raw)


def _ref_for_raw(relpath: str, raw: bytes) -> dict[str, Any]:
    return {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            f"required object missing:{key}"
        )
    return result


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    result = value.get(key)
    if not isinstance(result, list):
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            f"required array missing:{key}"
        )
    return result


def _index_cases(
    records: Sequence[Any],
) -> dict[str, Mapping[str, Any]]:
    indexed: dict[str, Mapping[str, Any]] = {}
    for item in records:
        if not isinstance(item, Mapping) or not item.get("case_id"):
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                "case record malformed"
            )
        case_id = str(item["case_id"])
        if case_id in indexed:
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                "duplicate case identity"
            )
        indexed[case_id] = item
    return indexed


def _require_lane(lane: str) -> None:
    if lane not in LANES:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            "unknown review lane"
        )


def _assert_safe(payload: Mapping[str, Any]) -> None:
    rendered = json.dumps(payload, ensure_ascii=False)
    for marker in (
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "ANTHROPIC_API_KEY",
        "BEGIN PRIVATE KEY",
        "client_secret",
        '"api_key"',
        '"password"',
        "sk-proj-",
        "/Users/",
        "/home/",
        "\\Users\\",
    ):
        if marker in rendered:
            raise ProductDeltaGraphReviewEnvelopeV2ResultError(
                "generated artifact contains a secret or local-path marker"
            )


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    target = (root / relpath).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphReviewEnvelopeV2ResultError(
            "repository-relative path escaped root"
        ) from exc
    return target
