"""Freeze restart-safe packets for the bounded graph replication.

This helper deepens the existing offline Product Delta owner. It takes the two
exact request packets already frozen by the completed graph-variance
calibration, creates four new neutral samples per condition, and seals their
lineage and disjoint within/cross comparison plan separately.

It does not generate semantic output, call a provider, run the graph or live
skill, change the planner/compiler, inspect private archives, or judge graph
value.
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
    ProductDeltaGraphVarianceCalibrationError,
    build_graph_variance_calibration,
    validate_checked_in_calibration,
)
from engine.system_b.product_delta_graph_variance_calibration_result import (
    validate_checked_in_review_consolidation,
)


CONTRACT_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_replication_contract.v1"
)
GENERATION_PACKETS_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_replication_generation_packets.v1"
)
SEALED_MANIFEST_SCHEMA_VERSION = (
    "lolla.product_delta_agent_graph_replication_sealed_manifest.v1"
)
REPLICATION_ID = "agent-only-graph-replication-2026-07-23"
BLINDING_NAMESPACE = "lolla-product-delta-graph-replication-v1"

DEFAULT_CONTRACT_RELPATH = (
    "docs/evals/lolla-agent-only-graph-replication-contract-v1.json"
)
OUTPUT_DIR_RELPATH = "research/agent-only-graph-replication-2026-07-23"
DEFAULT_GENERATION_PACKETS_RELPATH = (
    f"{OUTPUT_DIR_RELPATH}/generation-packets.json"
)
DEFAULT_SEALED_MANIFEST_RELPATH = f"{OUTPUT_DIR_RELPATH}/sealed-manifest.json"

CONDITIONS = (
    REHEARSAL_DIRECT,
    REHEARSAL_DIRECT_PLUS_ONE_HOP,
)
DRAW_NUMBERS = (3, 4, 5, 6)
SAMPLE_ALIASES = (
    "sample-amber",
    "sample-birch",
    "sample-cobalt",
    "sample-dune",
    "sample-ember",
    "sample-flint",
    "sample-grove",
    "sample-harbor",
)

BOUNDARY = {
    "repository_provider_api_calls": 0,
    "repository_provider_api_cost_usd": 0.0,
    "repository_provider_execution_authorized": False,
    "codex_generation_contexts_predeclared": 8,
    "codex_blind_review_contexts_predeclared": 2,
    "codex_post_reveal_contexts_conditionally_predeclared": 2,
    "codex_maximum_contexts": 12,
    "codex_contexts_called_no_ai_calls_or_economically_free": False,
    "codex_platform_route_token_and_cost": "unavailable_to_repository_operator",
    "human_review_completed": False,
    "principal_human_target_completed": False,
    "private_archives_read": False,
    "runtime_invoked": False,
    "live_skill_invoked": False,
    "graph_traversal_invoked": False,
    "graph_source_or_relation_changed": False,
    "graph_policy_changed": False,
    "planner_changed": False,
    "compiler_changed": False,
    "answer_quality_scored": False,
    "graph_causation_established": False,
    "human_usefulness_established": False,
}

NON_CLAIMS = (
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
)

SECRET_MARKERS = (
    "/Users/",
    "\\Users\\",
    "BEGIN PRIVATE KEY",
    "client_secret",
    '"api_key"',
    '"password"',
    "sk-proj-",
)


class ProductDeltaGraphReplicationError(ValueError):
    """Sanitized deterministic contract or custody failure."""


def build_graph_replication(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build eight exact neutral packets and a separately sealed lineage map."""

    root = Path(repo_root).resolve()
    _validate_completed_predecessor(root)

    contract, contract_ref = _read_json_ref(root, DEFAULT_CONTRACT_RELPATH)
    if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        raise ProductDeltaGraphReplicationError(
            "graph-replication contract schema mismatch"
        )
    _validate_contract(contract)

    locked_refs: dict[str, dict[str, Any]] = {}
    locked_payloads: dict[str, Any] = {}
    for name, declared_value in _required_mapping(
        contract, "input_locks"
    ).items():
        declared = _as_mapping(declared_value, "input lock")
        relpath = _required_text(declared, "path")
        raw, actual_ref = _read_raw_ref(root, relpath)
        if actual_ref != dict(declared):
            raise ProductDeltaGraphReplicationError(
                f"locked predecessor drift:{name}"
            )
        locked_refs[str(name)] = actual_ref
        if relpath.endswith(".json"):
            try:
                locked_payloads[str(name)] = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ProductDeltaGraphReplicationError(
                    f"locked predecessor JSON invalid:{name}"
                ) from exc

    current_generation, current_sealed = build_graph_variance_calibration(
        repo_root=root
    )
    if (
        current_generation
        != locked_payloads["completed_variance_generation_packets"]
        or current_sealed
        != locked_payloads["completed_variance_sealed_manifest"]
    ):
        raise ProductDeltaGraphReplicationError(
            "completed variance packet builder no longer matches locked inputs"
        )

    packet_by_condition = _resolve_packet_by_condition(
        generation=current_generation,
        sealed=current_sealed,
    )
    assignments = _neutral_assignments()
    packets: list[dict[str, Any]] = []
    sample_map: dict[str, dict[str, Any]] = {}
    for sample_alias, condition, draw_number in assignments:
        source_packet = packet_by_condition[condition]
        request = _required_mapping(source_packet, "request_body_projection")
        wrapper = _required_mapping(source_packet, "codex_task_wrapper")
        execution = _required_mapping(source_packet, "execution")
        packets.append(
            {
                "sample_alias": sample_alias,
                "request_body_projection": copy.deepcopy(dict(request)),
                "inheritance": {
                    "messages_inherited_byte_for_byte_as_json_values": True,
                    "response_schema_inherited_byte_for_byte_as_json_value": True,
                    "generation_settings_inherited_without_repair": True,
                    "request_body_projection_sha256": _sha256_json_value(request),
                    "task_wrapper_object_sha256": _sha256_json_value(wrapper),
                    "task_wrapper_text_sha256": _required_text(wrapper, "sha256"),
                    "completed_variance_packet_is_payload_source_not_new_execution": True,
                },
                "codex_task_wrapper": copy.deepcopy(dict(wrapper)),
                "execution": {
                    **copy.deepcopy(dict(execution)),
                    "performed": False,
                    "retry_or_fallback_authorized": False,
                    "sample_alias_is_not_condition_lineage": True,
                    "all_predeclared_attempts_run_despite_earlier_failure": True,
                },
                "restart_safe_terminal_capture": {
                    "required": True,
                    "method": (
                        "codex_exec_output_last_message_direct_to_"
                        "predeclared_external_path"
                    ),
                    "first_terminal_payload_only": True,
                    "event_log_or_session_reconstruction_forbidden": True,
                    "retry_healing_fallback_or_replacement_forbidden": True,
                },
            }
        )
        sample_map[sample_alias] = {
            "condition": condition,
            "draw_number": draw_number,
            "source_variance_sample_alias": _required_text(
                source_packet, "sample_alias"
            ),
            "request_body_projection_sha256": _sha256_json_value(request),
            "messages_sha256": _sha256_json_value(
                _required_sequence(request, "messages")
            ),
            "response_schema_sha256": _sha256_json_value(
                _required_mapping(request, "response_schema")
            ),
            "predeclared_terminal_output_path": (
                f"{OUTPUT_DIR_RELPATH}/terminal-output-{sample_alias}.json"
            ),
            "predeclared_terminal_failure_path": (
                f"{OUTPUT_DIR_RELPATH}/terminal-failure-{sample_alias}.json"
            ),
        }

    generation_payload = {
        "schema_version": GENERATION_PACKETS_SCHEMA_VERSION,
        "replication_id": REPLICATION_ID,
        "status": "frozen_neutral_replication_packets_not_executed",
        "sample_count": 8,
        "sample_aliases": list(SAMPLE_ALIASES),
        "packets": packets,
        "execution_order": [item[0] for item in assignments],
        "blinding": {
            "sample_lineage_absent_from_public_packet_metadata": True,
            "semantic_packet_content_remains_exact_and_unredacted": True,
            "lineage_available_only_in_sealed_manifest": True,
        },
        "boundary": copy.deepcopy(BOUNDARY),
        "non_claims": list(NON_CLAIMS),
    }

    comparison_plan = _build_comparison_plan(
        contract=contract,
        sample_map=sample_map,
    )
    sealed_payload = {
        "schema_version": SEALED_MANIFEST_SCHEMA_VERSION,
        "replication_id": REPLICATION_ID,
        "status": "sealed_before_new_agent_outputs",
        "contract_ref": contract_ref,
        "locked_predecessor_refs": locked_refs,
        "sample_map": sample_map,
        "comparison_plan": comparison_plan,
        "mechanical_overall_availability_gate": copy.deepcopy(
            dict(
                _required_mapping(
                    _required_mapping(contract, "comparison_plan"),
                    "mechanical_overall_availability_gate",
                )
            )
        ),
        "review_plan": {
            "blind_review_contexts": 2,
            "conditional_post_reveal_contexts": 2,
            "post_reveal_requires_availability_gate": True,
            "reveal_only_after_both_blind_reviews_are_frozen": True,
            "post_reveal_context_receives_one_frozen_review_only": True,
            "deterministic_consolidation": copy.deepcopy(
                dict(_required_mapping(contract, "deterministic_consolidation"))
            ),
        },
        "execution_budget": {
            "unconditional_generation_contexts": 8,
            "unconditional_blind_review_contexts": 2,
            "conditional_post_reveal_contexts": 2,
            "maximum_codex_contexts": 12,
            "repository_provider_api_calls": 0,
            "repository_provider_api_cost_usd": 0.0,
            "retry_fallback_healing_or_replacement_contexts": 0,
            "platform_route_token_and_cost": (
                "unavailable_to_repository_operator"
            ),
        },
        "unblinding": {
            "generation_agents_receive_only_one_sample_packet": True,
            "blind_reviewers_receive_no_sample_map_or_pair_roles": True,
            "post_reveal_contexts_start_only_after_both_reviews_freeze": True,
            "post_reveal_contexts_receive_no_sibling_review": True,
        },
        "boundary": copy.deepcopy(BOUNDARY),
        "non_claims": list(NON_CLAIMS),
    }

    _validate_built_payloads(
        contract=contract,
        generation=generation_payload,
        sealed=sealed_payload,
        packet_by_condition=packet_by_condition,
    )
    _assert_safe_generated(
        {"generation": generation_payload, "sealed": sealed_payload}
    )
    return generation_payload, sealed_payload


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"


def write_checked_in_replication(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    payloads = build_graph_replication(repo_root=root)
    for relpath, payload in zip(_output_relpaths(), payloads, strict=True):
        path = _resolve_repo_path(root, relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_json(payload), encoding="utf-8")


def validate_checked_in_replication(*, repo_root: Path | str) -> list[str]:
    root = Path(repo_root).resolve()
    payloads = build_graph_replication(repo_root=root)
    errors: list[str] = []
    for relpath, payload in zip(_output_relpaths(), payloads, strict=True):
        path = _resolve_repo_path(root, relpath)
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing generated artifact:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"generated artifact drift:{relpath}")
    return errors


def evaluate_mechanical_availability(
    *,
    sealed_manifest: Mapping[str, Any],
    sample_terminal_states: Mapping[str, str],
    both_blind_reviews_complete: bool,
) -> dict[str, Any]:
    """Evaluate only predeclared missingness, never semantic difference."""

    sample_map = _required_mapping(sealed_manifest, "sample_map")
    if set(sample_terminal_states) != set(sample_map):
        raise ProductDeltaGraphReplicationError(
            "terminal-state aliases do not match the frozen sample map"
        )
    allowed_states = {"complete", "partial", "failed", "missing"}
    if any(state not in allowed_states for state in sample_terminal_states.values()):
        raise ProductDeltaGraphReplicationError(
            "terminal-state value is outside the frozen state vocabulary"
        )

    pair_receipts: list[dict[str, Any]] = []
    available_within_direct = 0
    available_within_graph = 0
    available_cross = 0
    for value in _required_sequence(sealed_manifest, "comparison_plan"):
        pair = _as_mapping(value, "comparison")
        left = _required_mapping(pair, "left")
        right = _required_mapping(pair, "right")
        left_alias = _required_text(left, "sample_alias")
        right_alias = _required_text(right, "sample_alias")
        left_state = sample_terminal_states[left_alias]
        right_state = sample_terminal_states[right_alias]
        available = left_state == "complete" and right_state == "complete"
        role = _required_text(pair, "sealed_pair_role")
        if available and role == "cross_condition":
            available_cross += 1
        elif available and role == "within_condition":
            condition = _required_text(left, "condition")
            if condition != _required_text(right, "condition"):
                raise ProductDeltaGraphReplicationError(
                    "within-condition pair has mismatched lineage"
                )
            if condition == REHEARSAL_DIRECT:
                available_within_direct += 1
            elif condition == REHEARSAL_DIRECT_PLUS_ONE_HOP:
                available_within_graph += 1
            else:
                raise ProductDeltaGraphReplicationError(
                    "within-condition pair has unknown condition"
                )
        pair_receipts.append(
            {
                "blind_case_id": _required_text(pair, "blind_case_id"),
                "sealed_pair_id": _required_text(pair, "sealed_pair_id"),
                "sealed_pair_role": role,
                "left_terminal_state": left_state,
                "right_terminal_state": right_state,
                "availability": "available" if available else "not_evaluable",
            }
        )

    requirements = {
        "at_least_one_available_within_direct_pair": (
            available_within_direct >= 1
        ),
        "at_least_one_available_within_graph_pair": (
            available_within_graph >= 1
        ),
        "at_least_three_available_cross_condition_pairs": available_cross >= 3,
        "both_blind_reviews_complete": both_blind_reviews_complete,
    }
    gate_passes = all(requirements.values())
    return {
        "schema_version": (
            "lolla.product_delta_agent_graph_replication_"
            "mechanical_availability.v1"
        ),
        "purpose": (
            "missingness_gate_only_not_semantic_score_effect_threshold_or_vote"
        ),
        "pair_receipts": pair_receipts,
        "available_counts": {
            "within_direct": available_within_direct,
            "within_graph": available_within_graph,
            "cross_condition": available_cross,
        },
        "requirements": requirements,
        "gate_passes": gate_passes,
        "result_if_closed_now": (
            "eligible_for_post_reveal_interpretation"
            if gate_passes
            else "not_evaluable"
        ),
    }


def _output_relpaths() -> tuple[str, str]:
    return DEFAULT_GENERATION_PACKETS_RELPATH, DEFAULT_SEALED_MANIFEST_RELPATH


def _validate_completed_predecessor(root: Path) -> None:
    try:
        preoutput_errors = validate_checked_in_calibration(repo_root=root)
        result_errors = validate_checked_in_review_consolidation(repo_root=root)
    except (
        ProductDeltaGraphVarianceCalibrationError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise ProductDeltaGraphReplicationError(
            "completed variance predecessor validation failed"
        ) from exc
    if preoutput_errors or result_errors:
        raise ProductDeltaGraphReplicationError(
            "completed variance predecessor artifact drifted"
        )


def _validate_contract(contract: Mapping[str, Any]) -> None:
    authorization = _required_mapping(contract, "authorization")
    expected_false = (
        "provider_backed_execution",
        "human_review",
        "principal_human_target_completion",
        "private_archive_inspection",
        "live_skill_invocation",
        "runtime_change",
        "graph_policy_change",
        "graph_source_or_relation_change",
        "planner_or_compiler_change",
        "traversal_expansion",
        "answer_quality_scoring",
        "human_usefulness_claim",
        "product_claim",
    )
    if any(authorization.get(key) is not False for key in expected_false):
        raise ProductDeltaGraphReplicationError(
            "contract authorizes an out-of-scope action"
        )
    if (
        authorization.get("provider_api_calls") != 0
        or authorization.get("provider_api_cost_usd") != 0.0
    ):
        raise ProductDeltaGraphReplicationError(
            "contract provider boundary drifted"
        )
    if authorization.get("unconditional_generation_contexts") != 8:
        raise ProductDeltaGraphReplicationError(
            "generation context budget drifted"
        )
    if authorization.get("unconditional_blind_review_contexts") != 2:
        raise ProductDeltaGraphReplicationError(
            "blind-review context budget drifted"
        )
    if authorization.get("conditional_post_reveal_interpretation_contexts") != 2:
        raise ProductDeltaGraphReplicationError(
            "post-reveal context budget drifted"
        )
    if authorization.get("maximum_codex_contexts") != 12:
        raise ProductDeltaGraphReplicationError(
            "maximum Codex context budget drifted"
        )

    generation = _required_mapping(contract, "generation_replication")
    if (
        generation.get("new_draws_per_condition") != 4
        or generation.get("total_new_generation_attempts") != 8
        or generation.get("new_draw_numbers") != list(DRAW_NUMBERS)
    ):
        raise ProductDeltaGraphReplicationError(
            "generation replication design drifted"
        )
    if generation.get("retry_fallback_healing_or_replacement") is not False:
        raise ProductDeltaGraphReplicationError(
            "contract permits retry or response repair"
        )
    capture = _required_mapping(generation, "restart_safe_terminal_capture")
    if capture.get("required") is not True:
        raise ProductDeltaGraphReplicationError(
            "restart-safe terminal capture is not required"
        )

    comparison = _required_mapping(contract, "comparison_plan")
    if (
        comparison.get("pair_count") != 8
        or comparison.get("within_condition_pair_count") != 4
        or comparison.get("cross_condition_pair_count") != 4
    ):
        raise ProductDeltaGraphReplicationError(
            "comparison allocation drifted"
        )
    gate = _required_mapping(
        comparison, "mechanical_overall_availability_gate"
    )
    if (
        gate.get("requires_at_least_one_available_within_direct_pair")
        is not True
        or gate.get("requires_at_least_one_available_within_graph_pair")
        is not True
        or gate.get("requires_at_least_three_available_cross_condition_pairs")
        is not True
        or gate.get("requires_both_blind_reviews_complete") is not True
    ):
        raise ProductDeltaGraphReplicationError(
            "mechanical availability gate drifted"
        )

    blind = _required_mapping(contract, "blind_review_contract")
    if blind.get("fresh_context_count") != 2:
        raise ProductDeltaGraphReplicationError(
            "blind-review count drifted"
        )
    if (
        blind.get("scalar_score_forbidden") is not True
        or blind.get("winner_forbidden") is not True
        or blind.get("ranking_or_vote_forbidden") is not True
    ):
        raise ProductDeltaGraphReplicationError(
            "blind-review non-scalar boundary drifted"
        )

    post_reveal = _required_mapping(
        contract, "post_reveal_interpretation_contract"
    )
    if (
        post_reveal.get("conditional_context_count") != 2
        or post_reveal.get("one_context_per_frozen_review") is not True
        or post_reveal.get("context_identity_continuity_claimed") is not False
    ):
        raise ProductDeltaGraphReplicationError(
            "post-reveal interpretation boundary drifted"
        )
    consolidation = _required_mapping(
        contract, "deterministic_consolidation"
    )
    if (
        consolidation.get("scalar_score_forbidden") is not True
        or consolidation.get("statistical_inference_authorized") is not False
        or consolidation.get("automatic_graph_decision_forbidden") is not True
    ):
        raise ProductDeltaGraphReplicationError(
            "deterministic consolidation boundary drifted"
        )


def _resolve_packet_by_condition(
    *, generation: Mapping[str, Any], sealed: Mapping[str, Any]
) -> dict[str, Mapping[str, Any]]:
    sample_map = _required_mapping(sealed, "sample_map")
    packets = {
        _required_text(item, "sample_alias"): item
        for item in _required_sequence(generation, "packets")
        if isinstance(item, Mapping)
    }
    by_condition: dict[str, list[Mapping[str, Any]]] = {
        condition: [] for condition in CONDITIONS
    }
    for alias, lineage_value in sample_map.items():
        lineage = _as_mapping(lineage_value, "variance sample lineage")
        condition = _required_text(lineage, "condition")
        if condition not in by_condition:
            raise ProductDeltaGraphReplicationError(
                "unexpected completed variance condition"
            )
        by_condition[condition].append(_required_mapping(packets, str(alias)))

    result: dict[str, Mapping[str, Any]] = {}
    for condition, condition_packets in by_condition.items():
        if len(condition_packets) != 2:
            raise ProductDeltaGraphReplicationError(
                "completed variance allocation drifted"
            )
        first, second = condition_packets
        for field in (
            "request_body_projection",
            "codex_task_wrapper",
        ):
            if first.get(field) != second.get(field):
                raise ProductDeltaGraphReplicationError(
                    f"completed variance packets disagree within condition:{field}"
                )
        result[condition] = first
    return result


def _neutral_assignments() -> list[tuple[str, str, int]]:
    assignments = [
        (condition, draw_number)
        for condition in CONDITIONS
        for draw_number in DRAW_NUMBERS
    ]
    assignments.sort(
        key=lambda item: _sha256_text(
            f"{BLINDING_NAMESPACE}|{item[0]}|{item[1]}"
        )
    )
    return [
        (sample_alias, condition, draw_number)
        for sample_alias, (condition, draw_number) in zip(
            SAMPLE_ALIASES, assignments, strict=True
        )
    ]


def _build_comparison_plan(
    *,
    contract: Mapping[str, Any],
    sample_map: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    alias_by_endpoint = {
        (
            "direct" if item["condition"] == REHEARSAL_DIRECT else "graph",
            int(item["draw_number"]),
        ): alias
        for alias, item in sample_map.items()
    }
    contract_pairs = _required_sequence(
        _required_mapping(contract, "comparison_plan"), "pairs"
    )
    result: list[dict[str, Any]] = []
    for index, value in enumerate(contract_pairs, start=1):
        pair = _as_mapping(value, "comparison pair")
        left_key = _parse_endpoint(_required_text(pair, "left"))
        right_key = _parse_endpoint(_required_text(pair, "right"))
        try:
            left_alias = alias_by_endpoint[left_key]
            right_alias = alias_by_endpoint[right_key]
        except KeyError as exc:
            raise ProductDeltaGraphReplicationError(
                "comparison endpoint is not a predeclared sample"
            ) from exc
        result.append(
            {
                "blind_case_id": f"replication-pair-{index:02d}",
                "sealed_pair_id": _required_text(pair, "sealed_pair_id"),
                "sealed_pair_role": _required_text(pair, "sealed_pair_role"),
                "left": {
                    "sample_alias": left_alias,
                    "condition": sample_map[left_alias]["condition"],
                    "draw_number": sample_map[left_alias]["draw_number"],
                    "terminal_output_path": sample_map[left_alias][
                        "predeclared_terminal_output_path"
                    ],
                    "terminal_failure_path": sample_map[left_alias][
                        "predeclared_terminal_failure_path"
                    ],
                },
                "right": {
                    "sample_alias": right_alias,
                    "condition": sample_map[right_alias]["condition"],
                    "draw_number": sample_map[right_alias]["draw_number"],
                    "terminal_output_path": sample_map[right_alias][
                        "predeclared_terminal_output_path"
                    ],
                    "terminal_failure_path": sample_map[right_alias][
                        "predeclared_terminal_failure_path"
                    ],
                },
                "blind_arm_orientation": (
                    "derived_deterministically_after_terminal_states_exist"
                ),
            }
        )
    return result


def _parse_endpoint(value: str) -> tuple[str, int]:
    parts = value.split("_draw_")
    if len(parts) != 2 or parts[0] not in {"direct", "graph"}:
        raise ProductDeltaGraphReplicationError(
            "invalid comparison endpoint"
        )
    try:
        draw_number = int(parts[1])
    except ValueError as exc:
        raise ProductDeltaGraphReplicationError(
            "invalid comparison draw number"
        ) from exc
    if draw_number not in DRAW_NUMBERS:
        raise ProductDeltaGraphReplicationError(
            "comparison draw is outside frozen replication"
        )
    return parts[0], draw_number


def _validate_built_payloads(
    *,
    contract: Mapping[str, Any],
    generation: Mapping[str, Any],
    sealed: Mapping[str, Any],
    packet_by_condition: Mapping[str, Mapping[str, Any]],
) -> None:
    packets = _required_sequence(generation, "packets")
    if len(packets) != 8:
        raise ProductDeltaGraphReplicationError(
            "built sample count drifted"
        )
    if list(generation.get("sample_aliases", [])) != list(SAMPLE_ALIASES):
        raise ProductDeltaGraphReplicationError(
            "sample aliases drifted"
        )
    if list(generation.get("execution_order", [])) != list(SAMPLE_ALIASES):
        raise ProductDeltaGraphReplicationError(
            "execution order drifted"
        )

    sample_map = _required_mapping(sealed, "sample_map")
    counts = {condition: 0 for condition in CONDITIONS}
    draws = {condition: set() for condition in CONDITIONS}
    for value in packets:
        packet = _as_mapping(value, "replication packet")
        alias = _required_text(packet, "sample_alias")
        lineage = _required_mapping(sample_map, alias)
        condition = _required_text(lineage, "condition")
        counts[condition] += 1
        draws[condition].add(lineage.get("draw_number"))
        source = _required_mapping(packet_by_condition, condition)
        if packet.get("request_body_projection") != source.get(
            "request_body_projection"
        ):
            raise ProductDeltaGraphReplicationError(
                "replication request differs from completed variance packet"
            )
        if packet.get("codex_task_wrapper") != source.get(
            "codex_task_wrapper"
        ):
            raise ProductDeltaGraphReplicationError(
                "replication wrapper differs from completed variance packet"
            )
        capture = _required_mapping(
            packet, "restart_safe_terminal_capture"
        )
        if (
            capture.get("required") is not True
            or capture.get("retry_healing_fallback_or_replacement_forbidden")
            is not True
        ):
            raise ProductDeltaGraphReplicationError(
                "terminal capture boundary drifted"
            )
    if counts != {condition: 4 for condition in CONDITIONS}:
        raise ProductDeltaGraphReplicationError(
            "replication allocation is not four per condition"
        )
    if draws != {condition: set(DRAW_NUMBERS) for condition in CONDITIONS}:
        raise ProductDeltaGraphReplicationError(
            "replication draw numbers drifted"
        )

    comparison = _required_sequence(sealed, "comparison_plan")
    if len(comparison) != 8:
        raise ProductDeltaGraphReplicationError(
            "built comparison count drifted"
        )
    roles = [
        _required_text(_as_mapping(item, "comparison"), "sealed_pair_role")
        for item in comparison
    ]
    if roles.count("within_condition") != 4 or roles.count(
        "cross_condition"
    ) != 4:
        raise ProductDeltaGraphReplicationError(
            "built comparison role allocation drifted"
        )
    endpoint_usage = {
        alias: {"within": 0, "cross": 0} for alias in SAMPLE_ALIASES
    }
    for item in comparison:
        pair = _as_mapping(item, "comparison")
        role = "within" if pair["sealed_pair_role"] == "within_condition" else "cross"
        for side in ("left", "right"):
            alias = _required_text(
                _required_mapping(pair, side), "sample_alias"
            )
            endpoint_usage[alias][role] += 1
    if any(
        usage != {"within": 1, "cross": 1}
        for usage in endpoint_usage.values()
    ):
        raise ProductDeltaGraphReplicationError(
            "comparison pairs are not disjoint within role and aligned cross role"
        )

    declared_paths = _required_mapping(contract, "predeclared_paths")
    if (
        declared_paths.get("generation_packets")
        != DEFAULT_GENERATION_PACKETS_RELPATH
        or declared_paths.get("preoutput_sealed_manifest")
        != DEFAULT_SEALED_MANIFEST_RELPATH
    ):
        raise ProductDeltaGraphReplicationError(
            "predeclared output path drifted"
        )


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    raw, ref = _read_raw_ref(root, relpath)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProductDeltaGraphReplicationError(
            f"invalid JSON input:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphReplicationError(
            f"JSON input is not an object:{relpath}"
        )
    return payload, ref


def _read_raw_ref(
    root: Path, relpath: str
) -> tuple[bytes, dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ProductDeltaGraphReplicationError(
            f"missing input:{relpath}"
        ) from exc
    return raw, {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    if not relpath or Path(relpath).is_absolute():
        raise ProductDeltaGraphReplicationError(
            "repository-relative path required"
        )
    resolved = (root / relpath).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphReplicationError(
            "path escapes repository root"
        ) from exc
    return resolved


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    item = value.get(key)
    if not isinstance(item, Mapping):
        raise ProductDeltaGraphReplicationError(
            f"required object missing:{key}"
        )
    return item


def _required_sequence(
    value: Mapping[str, Any], key: str
) -> Sequence[Any]:
    item = value.get(key)
    if not isinstance(item, list):
        raise ProductDeltaGraphReplicationError(
            f"required list missing:{key}"
        )
    return item


def _required_text(value: Mapping[str, Any], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ProductDeltaGraphReplicationError(
            f"required text missing:{key}"
        )
    return item


def _as_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProductDeltaGraphReplicationError(
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


def _assert_safe_generated(payloads: Mapping[str, Any]) -> None:
    rendered = render_json(payloads)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            raise ProductDeltaGraphReplicationError(
                "generated artifact contains forbidden secret or local-path marker"
            )
