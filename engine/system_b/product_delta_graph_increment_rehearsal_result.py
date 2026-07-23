"""Freeze blind review inputs for the agent-only graph-increment rehearsal.

This deterministic Product Delta helper validates the frozen source reads,
post-seal observations, and first terminal generation results. It then copies
the existing qualification, exact-duplicate, and stand-down controls into one
new blind packet and records lineage in a separate sealed manifest. It does not
call a provider, judge semantic quality, traverse the graph, or change runtime.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_graph_increment_rehearsal import (
    DEFAULT_GENERATION_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH as PREOUTPUT_SEALED_MANIFEST_RELPATH,
    ProductDeltaGraphIncrementRehearsalError,
    validate_checked_in_rehearsal,
)
from engine.system_b.product_delta_paired_screen import (
    DEFAULT_BLIND_PACKETS_RELPATH as CONTROL_BLIND_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH as CONTROL_SEALED_MANIFEST_RELPATH,
    validate_checked_in_screen,
)
from engine.system_b.product_delta_paired_screen_review import (
    FORBIDDEN_REVIEW_KEYS,
    _validate_pair_review,
    _validate_qualification_review,
    _walk_keys,
)
from engine.system_b.simulated_reliability_v1 import (
    SimulatedReliabilityError,
    compile_pressure_response,
)


BLIND_PACKET_SCHEMA_VERSION = (
    "lolla.product_delta_graph_increment_blind_review_packet.v1"
)
EXECUTION_SEALED_SCHEMA_VERSION = (
    "lolla.product_delta_graph_increment_execution_sealed_manifest.v1"
)
REVIEW_RESPONSE_SCHEMA_VERSION = (
    "lolla.product_delta_graph_increment_fresh_agent_review.v1"
)
CONSOLIDATION_SCHEMA_VERSION = (
    "lolla.product_delta_graph_increment_agent_consolidation.v1"
)
REHEARSAL_ID = "agent-only-graph-increment-rehearsal-2026-07-23"
BLINDING_NAMESPACE = "lolla-product-delta-graph-increment-review-v1"
OUTPUT_DIR_RELPATH = (
    "research/agent-only-graph-increment-rehearsal-2026-07-23"
)
REVIEW_DIR_RELPATH = (
    "reviews/codex-assisted/agent-only-graph-increment-rehearsal-v1"
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
TRAP_SET_RELPATH = "docs/evals/provisional-reviewer-trap-set-v0.json"
SOURCE_READ_RELPATHS = {
    "primary": f"{REVIEW_DIR_RELPATH}/source-read-primary.json",
    "skeptical": f"{REVIEW_DIR_RELPATH}/source-read-skeptical.json",
}
REFERENCE_OBSERVATION_RELPATHS = {
    "primary": f"{REVIEW_DIR_RELPATH}/reference-observation-primary.json",
    "skeptical": f"{REVIEW_DIR_RELPATH}/reference-observation-skeptical.json",
}
TERMINAL_OUTPUT_RELPATHS = {
    "condition-A": f"{OUTPUT_DIR_RELPATH}/terminal-output-condition-A.json",
    "condition-B": f"{OUTPUT_DIR_RELPATH}/terminal-output-condition-B.json",
}
PAIR_REVIEW_RELPATHS = {
    "primary": f"{REVIEW_DIR_RELPATH}/pair-review-primary.json",
    "skeptical": f"{REVIEW_DIR_RELPATH}/pair-review-skeptical.json",
}
CELL_TO_BUNDLE_ARM = {
    "f2_fresh_human_controlled_fact_free_direct_only": "direct_pressure",
    "f3_fresh_human_controlled_fact_free_plus_current_graph": (
        "graph_expanded_pressure"
    ),
}
EXPECTED_SOURCE_REVIEW_IDS = {
    "primary": "agent-source-read-primary-v1",
    "skeptical": "agent-source-read-skeptical-v1",
}
EXPECTED_REFERENCE_REVIEW_IDS = {
    "primary": "agent-reference-observation-primary-v1",
    "skeptical": "agent-reference-observation-skeptical-v1",
}
EXPECTED_PAIR_REVIEW_IDS = {
    "primary": "agent-graph-increment-pair-primary-v1",
    "skeptical": "agent-graph-increment-pair-skeptical-v1",
}
BOUNDARY = {
    "repository_provider_api_calls": 0,
    "repository_provider_api_cost_usd": 0.0,
    "codex_agent_contexts_used_before_blind_review": 4,
    "codex_blind_review_contexts_predeclared": 2,
    "codex_platform_route_token_and_cost": "unavailable_to_repository_operator",
    "called_no_ai_calls_or_economically_free": False,
    "private_archives_read": False,
    "human_validated": False,
    "ground_truth": False,
    "answer_quality_scored": False,
    "winner_selected": False,
    "graph_traversal_invoked": False,
    "graph_policy_changed": False,
    "runtime_changed": False,
    "skill_invoked": False,
}
NON_CLAIMS = [
    "not principal-human review",
    "not completed F2 or F3 provider execution",
    "not exact execution of a standalone provider envelope",
    "not evidence that either answer is better",
    "not graph relevance or causal graph-value evidence",
    "not expected model behavior",
    "not human usefulness or decision-quality evidence",
    "not authorization to change graph traversal, runtime, or the skill",
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


class ProductDeltaGraphIncrementResultError(ValueError):
    """Sanitized deterministic rehearsal-result custody failure."""


def build_blind_review_inputs(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the blind review packet and separate sealed lineage manifest."""

    root = Path(repo_root).resolve()
    _validate_frozen_predecessors(root)
    source, source_ref = _read_text_ref(root, SOURCE_RELPATH)
    control_blind, control_blind_ref = _read_json_ref(
        root, CONTROL_BLIND_PACKETS_RELPATH
    )
    _, control_sealed_ref = _read_json_ref(
        root, CONTROL_SEALED_MANIFEST_RELPATH
    )
    generation_packets, generation_ref = _read_json_ref(
        root, DEFAULT_GENERATION_PACKETS_RELPATH
    )
    preoutput_sealed, preoutput_sealed_ref = _read_json_ref(
        root, PREOUTPUT_SEALED_MANIFEST_RELPATH
    )
    bundle, bundle_ref = _read_json_ref(root, PORTFOLIO_BUNDLE_RELPATH)

    source_reads, source_read_refs = _validate_source_reads(root)
    reference_refs = _validate_reference_observations(
        root=root,
        source_read_refs=source_read_refs,
    )
    terminal_outputs, terminal_refs, compile_receipts = _validate_terminal_outputs(
        root=root,
        generation_packets=generation_packets,
        preoutput_sealed=preoutput_sealed,
        bundle=bundle,
    )
    new_pair, review_arm_map = _build_new_blind_pair(
        source=source,
        source_ref=source_ref,
        terminal_outputs=terminal_outputs,
        terminal_refs=terminal_refs,
    )

    qualification_cases = copy.deepcopy(
        _required_list(control_blind, "qualification_cases")
    )
    control_pairs = _required_list(control_blind, "paired_cases")
    duplicate_null = next(
        (
            copy.deepcopy(item)
            for item in control_pairs
            if isinstance(item, Mapping)
            and item.get("evidence_class") == "exact_duplicate_null"
        ),
        None,
    )
    if not isinstance(duplicate_null, dict):
        raise ProductDeltaGraphIncrementResultError(
            "existing exact-duplicate control is missing"
        )
    standdown_cases = copy.deepcopy(
        _required_list(control_blind, "standdown_cases")
    )
    if len(qualification_cases) != 10 or len(standdown_cases) != 1:
        raise ProductDeltaGraphIncrementResultError(
            "existing qualification or stand-down control count drifted"
        )

    pair_ids = [str(duplicate_null["case_id"]), str(new_pair["case_id"])]
    qualification_ids = [str(item["case_id"]) for item in qualification_cases]
    standdown_ids = [str(item["case_id"]) for item in standdown_cases]
    blind: dict[str, Any] = {
        "schema_version": BLIND_PACKET_SCHEMA_VERSION,
        "rehearsal_id": REHEARSAL_ID,
        "status": "blind_review_inputs_frozen_before_fresh_reviews",
        "purpose": (
            "Inspect one anonymized first-terminal answer pair while reusing the "
            "existing reviewer traps, exact-duplicate null, and legitimate "
            "stand-down control."
        ),
        "boundary": dict(BOUNDARY),
        "review_order": [
            "Read and answer every qualification case before reviewing either pair.",
            "Read each pair's source before either arm.",
            "Review the exact-duplicate null before the new rehearsal pair.",
            "Compare atomic reasoning moves, not fluency, length, or polish.",
            "Record preserved value, lost value, unsupported additions, and burden.",
            "Make an origin guess only after substantive review; indistinguishable is allowed.",
            "Review the stand-down independently.",
            "Do not rank, score, vote, certify, or choose an answer.",
        ],
        "visibility": {
            "lineage_included": False,
            "condition_aliases_included": False,
            "candidate_dispositions_included": False,
            "source_proxy_reads_included": False,
            "reference_observations_included": False,
            "sibling_review_included": False,
        },
        "review_contract": copy.deepcopy(control_blind["review_contract"]),
        "response_envelope_contract": {
            "schema_version": REVIEW_RESPONSE_SCHEMA_VERSION,
            "review_id": (
                "Use the exact ID assigned in the fresh-agent task wrapper."
            ),
            "fresh_context": True,
            "saw_lineage_before_freeze": False,
            "saw_source_proxy_reads_before_freeze": False,
            "saw_sibling_review_before_freeze": False,
            "qualification_reviews": {
                "exact_case_ids": qualification_ids,
                "exactly_one_each": True,
                "shape": control_blind["review_contract"][
                    "qualification_response_shape"
                ],
            },
            "paired_reviews": {
                "exact_case_ids": pair_ids,
                "exactly_one_each": True,
                "shape": control_blind["review_contract"][
                    "paired_response_shape"
                ],
            },
            "standdown_reviews": {
                "exact_case_ids": standdown_ids,
                "exactly_one_each": True,
                "shape": control_blind["review_contract"][
                    "standdown_response_shape"
                ],
            },
            "boundary": {
                "human_validated": False,
                "ground_truth": False,
                "answer_quality_scored": False,
                "winner_selected": False,
                "provider_calls": 0,
            },
        },
        "qualification_case_count": len(qualification_cases),
        "qualification_cases": qualification_cases,
        "paired_case_count": 2,
        "paired_cases": [duplicate_null, new_pair],
        "standdown_case_count": 1,
        "standdown_cases": standdown_cases,
        "non_claims": list(NON_CLAIMS),
    }
    blind_rendered = render_json(blind)
    sealed = {
        "schema_version": EXECUTION_SEALED_SCHEMA_VERSION,
        "rehearsal_id": REHEARSAL_ID,
        "status": "generation_outputs_valid_blind_review_inputs_frozen",
        "handling": {
            "show_to_generation_agents": False,
            "show_to_blind_reviewers": False,
            "unblind_only_after_both_substantive_reviews_are_frozen": True,
            "source_proxy_observations_change_routing": False,
        },
        "boundary": dict(BOUNDARY),
        "input_refs": {
            "authoritative_source": source_ref,
            "control_blind_packets": control_blind_ref,
            "control_sealed_manifest": control_sealed_ref,
            "generation_packets": generation_ref,
            "preoutput_sealed_manifest": preoutput_sealed_ref,
            "portfolio_bundle": bundle_ref,
            "source_reads": source_read_refs,
            "reference_observations": reference_refs,
            "terminal_outputs": terminal_refs,
        },
        "source_read_terminal_states": {
            key: payload["terminal_status"]
            for key, payload in sorted(source_reads.items())
        },
        "terminal_output_validation": compile_receipts,
        "review_arm_map": {
            review_arm: {
                "condition_alias": condition_alias,
                "terminal_output_ref": terminal_refs[condition_alias],
                "cell_id": preoutput_sealed["alias_map"][condition_alias][
                    "cell_id"
                ],
                "condition": preoutput_sealed["alias_map"][condition_alias][
                    "condition"
                ],
            }
            for review_arm, condition_alias in sorted(review_arm_map.items())
        },
        "control_lineage": {
            "qualification_and_null_and_standdown_source": control_blind_ref,
            "sealed_expectations_and_lineage": control_sealed_ref,
        },
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
        path = _resolve_repo_path(root, relpath)
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing generated artifact:{relpath}")
            continue
        if actual != render_json(payload):
            errors.append(f"generated artifact drift:{relpath}")
    return errors


def build_review_consolidation(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], list[str]]:
    """Validate frozen reviews and fan them in without semantic adjudication."""

    root = Path(repo_root).resolve()
    blind_input_errors = validate_checked_in_blind_review_inputs(repo_root=root)
    if blind_input_errors:
        raise ProductDeltaGraphIncrementResultError(
            "blind review input custody drifted"
        )
    blind, blind_ref = _read_json_ref(root, BLIND_REVIEW_PACKET_RELPATH)
    sealed, sealed_ref = _read_json_ref(
        root, EXECUTION_SEALED_MANIFEST_RELPATH
    )
    trap_set, trap_set_ref = _read_json_ref(root, TRAP_SET_RELPATH)
    source_reads = {
        lane: _read_json_ref(root, relpath)
        for lane, relpath in SOURCE_READ_RELPATHS.items()
    }
    reference_observations = {
        lane: _read_json_ref(root, relpath)
        for lane, relpath in REFERENCE_OBSERVATION_RELPATHS.items()
    }
    terminal_outputs = {
        alias: _read_json_ref(root, relpath)
        for alias, relpath in TERMINAL_OUTPUT_RELPATHS.items()
    }
    pair_reviews = {
        lane: _read_json_ref(root, relpath)
        for lane, relpath in PAIR_REVIEW_RELPATHS.items()
    }

    qualification_ids = _case_ids(
        _required_list(blind, "qualification_cases")
    )
    pair_cases = _required_list(blind, "paired_cases")
    pair_ids = _case_ids(pair_cases)
    standdown_ids = _case_ids(_required_list(blind, "standdown_cases"))
    errors: list[str] = []
    for lane, (payload, _) in pair_reviews.items():
        errors.extend(
            _validate_fresh_pair_review(
                payload,
                lane=lane,
                expected_qualification_ids=qualification_ids,
                expected_pair_ids=pair_ids,
                expected_standdown_ids=standdown_ids,
            )
        )

    lineage = _required_mapping(sealed, "review_arm_map")
    direct_arm = _arm_for_condition(lineage, "rehearsal_direct")
    graph_arm = _arm_for_condition(
        lineage, "rehearsal_direct_plus_current_one_hop"
    )
    pair_case_index = _index_cases(pair_cases)
    review_payloads = {
        lane: payload for lane, (payload, _) in pair_reviews.items()
    }
    qualification_fan_in = []
    for case_id in qualification_ids:
        qualification_fan_in.append(
            {
                "case_id": case_id,
                "reviewer_reads": [
                    {
                        "review_id": payload["review_id"],
                        "evidence_disposition": _index_cases(
                            payload["qualification_reviews"]
                        )[case_id]["evidence_disposition"],
                    }
                    for payload in review_payloads.values()
                ],
                "fan_in_policy": (
                    "Dispositions remain side by side and are not counted as "
                    "votes or compared with an answer key."
                ),
            }
        )

    paired_fan_in = []
    for case_id in pair_ids:
        case = _required_mapping(pair_case_index, case_id)
        reads = []
        material_reads = []
        for payload in review_payloads.values():
            review = _required_mapping(
                _index_cases(payload["paired_reviews"]), case_id
            )
            identity = _required_mapping(
                review, "identity_guess_after_substantive_review"
            )
            identity_guess = str(
                identity["arm_with_added_external_context"]
            )
            material_read = str(review["material_decision_difference"])
            material_reads.append(material_read)
            reads.append(
                {
                    "review_id": payload["review_id"],
                    "source_interpretation": copy.deepcopy(
                        review["source_interpretation"]
                    ),
                    "atomic_moves": copy.deepcopy(review["atomic_moves"]),
                    "arm_observations": copy.deepcopy(
                        review["arm_observations"]
                    ),
                    "material_decision_difference": material_read,
                    "inspection_limits": copy.deepcopy(
                        review["inspection_limits"]
                    ),
                    "identity_guess_after_substantive_review": copy.deepcopy(
                        identity
                    ),
                    "identity_guess_relation_to_graph_lineage": (
                        "declared_indistinguishable"
                        if identity_guess == "indistinguishable"
                        else (
                            "matches_graph_lineage"
                            if identity_guess == graph_arm
                            else "does_not_match_graph_lineage"
                        )
                    ),
                }
            )
        paired_fan_in.append(
            {
                "case_id": case_id,
                "evidence_class": case["evidence_class"],
                "lineage_revealed_after_both_reviews_froze": (
                    _lineage_for_pair(
                        case_id=case_id,
                        lineage=lineage,
                    )
                ),
                "reviewer_reads": reads,
                "material_difference_reads": material_reads,
                "material_difference_read_agreement": (
                    len(set(material_reads)) == 1
                ),
                "fan_in_policy": (
                    "Agreement is not truth and disagreement is not resolved "
                    "by ranking, voting, or averaging."
                ),
            }
        )

    standdown_fan_in = [
        {
            "case_id": case_id,
            "reviewer_reads": [
                {
                    "review_id": payload["review_id"],
                    **copy.deepcopy(
                        _required_mapping(
                            _index_cases(payload["standdown_reviews"]),
                            case_id,
                        )
                    ),
                }
                for payload in review_payloads.values()
            ],
        }
        for case_id in standdown_ids
    ]
    source_proxy_fan_in = [
        {
            "lane": lane,
            "source_read_ref": source_reads[lane][1],
            "source_read_terminal_status": source_reads[lane][0][
                "terminal_status"
            ],
            "post_seal_reference_ref": reference_observations[lane][1],
            "post_seal_candidate_reviews": copy.deepcopy(
                reference_observations[lane][0]["candidate_reviews"]
            ),
            "authority": (
                "Agent proxy observation only; it did not change routing or "
                "become the blank principal-human target."
            ),
        }
        for lane in SOURCE_READ_RELPATHS
    ]
    generated_arm_custody = {
        review_arm: {
            **copy.deepcopy(lineage[review_arm]),
            "candidate_dispositions": copy.deepcopy(
                terminal_outputs[
                    str(lineage[review_arm]["condition_alias"])
                ][0]["candidate_dispositions"]
            ),
        }
        for review_arm in ("A", "B")
    }
    duplicate_null_reads = next(
        item["material_difference_reads"]
        for item in paired_fan_in
        if item["evidence_class"] == "exact_duplicate_null"
    )
    new_pair_reads = next(
        item["material_difference_reads"]
        for item in paired_fan_in
        if item["case_id"] == "retailer-graph-increment-rehearsal-blind"
    )
    standdown_support_reads = [
        read["standdown_support"]
        for item in standdown_fan_in
        for read in item["reviewer_reads"]
    ]
    consolidation: dict[str, Any] = {
        "schema_version": CONSOLIDATION_SCHEMA_VERSION,
        "rehearsal_id": REHEARSAL_ID,
        "status": (
            "valid_frozen_agent_diagnostic"
            if not errors
            else "invalid_review_shape_first_terminal_outputs_preserved"
        ),
        "boundary": {
            **dict(BOUNDARY),
            "codex_agent_contexts_used_total": 6,
            "principal_human_target_changed": False,
            "source_proxy_became_human_authority": False,
            "semantic_adjudication_performed": False,
            "scalar_summary_created": False,
            "graph_causation_established": False,
            "graph_relevance_established": False,
            "human_usefulness_established": False,
            "permission_to_expand_graph_created": False,
        },
        "input_refs": {
            "blind_review_packet": blind_ref,
            "execution_sealed_manifest": sealed_ref,
            "trap_set": trap_set_ref,
            "source_reads": {
                lane: value[1] for lane, value in source_reads.items()
            },
            "post_seal_reference_observations": {
                lane: value[1]
                for lane, value in reference_observations.items()
            },
            "terminal_outputs": {
                alias: value[1]
                for alias, value in terminal_outputs.items()
            },
            "pair_reviews": {
                lane: value[1] for lane, value in pair_reviews.items()
            },
        },
        "validation": {
            "error_count": len(errors),
            "errors": errors,
            "shape_custody_and_declared_enum_validation_only": True,
            "semantic_correctness_validated": False,
            "trap_set_schema_version": trap_set.get("schema_version"),
        },
        "isolation_receipt": {
            "fresh_agent_context_count": 6,
            "source_first_contexts": 2,
            "isolated_generation_contexts": 2,
            "blind_review_contexts": 2,
            "first_terminal_outputs_preserved": True,
            "reviewers_saw_lineage_before_freeze": False,
            "reviewers_saw_source_proxy_reads_before_freeze": False,
            "reviewers_saw_each_other_before_freeze": False,
        },
        "source_proxy_observations_after_routing_freeze": source_proxy_fan_in,
        "generated_arm_custody_after_unblinding": generated_arm_custody,
        "qualification_reviews": qualification_fan_in,
        "paired_reviews": paired_fan_in,
        "standdown_reviews": standdown_fan_in,
        "bounded_observations": {
            "duplicate_null_material_reads": duplicate_null_reads,
            "new_pair_material_reads": new_pair_reads,
            "standdown_support_reads": standdown_support_reads,
            "direct_only_review_arm": direct_arm,
            "current_one_hop_graph_review_arm": graph_arm,
            "both_reviewers_declared_new_pair_lineage_indistinguishable": all(
                read[
                    "identity_guess_after_substantive_review"
                ]["arm_with_added_external_context"]
                == "indistinguishable"
                for item in paired_fan_in
                if item["case_id"]
                == "retailer-graph-increment-rehearsal-blind"
                for read in item["reviewer_reads"]
            ),
            "interpretation_limit": (
                "These are exact observations about two frozen Codex-assisted "
                "reviews. They are not a score, winner, answer-quality result, "
                "graph-value estimate, or substitute for a person."
            ),
        },
        "fan_in_policy": [
            "No reviewer is authoritative.",
            "Qualification reads remain case-by-case rather than becoming a score.",
            "The duplicate null and stand-down remain controls, not proof of reviewer calibration.",
            "All atomic moves and arm observations remain attributable to their reviewer.",
            "Lineage was revealed only after both substantive reviews froze.",
            "Source-proxy observations remain separate from blind reviewer reads.",
        ],
        "non_claims": list(NON_CLAIMS),
    }
    _assert_safe_generated({"consolidation": consolidation})
    return consolidation, errors


def write_review_consolidation(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    consolidation, errors = build_review_consolidation(repo_root=root)
    if errors:
        raise ProductDeltaGraphIncrementResultError(
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
    path = _resolve_repo_path(root, CONSOLIDATION_RELPATH)
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError:
        return [f"missing generated artifact:{CONSOLIDATION_RELPATH}"]
    if actual != render_json(consolidation):
        return [f"generated artifact drift:{CONSOLIDATION_RELPATH}"]
    return []


def _validate_frozen_predecessors(root: Path) -> None:
    try:
        rehearsal_errors = validate_checked_in_rehearsal(repo_root=root)
    except ProductDeltaGraphIncrementRehearsalError as exc:
        raise ProductDeltaGraphIncrementResultError(
            "pre-output rehearsal validation failed"
        ) from exc
    screen_errors = validate_checked_in_screen(repo_root=root)
    if rehearsal_errors or screen_errors:
        raise ProductDeltaGraphIncrementResultError(
            "frozen predecessor artifact drifted"
        )


def _validate_source_reads(
    root: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    refs: dict[str, dict[str, Any]] = {}
    for lane, relpath in SOURCE_READ_RELPATHS.items():
        payload, ref = _read_json_ref(root, relpath)
        if payload.get("review_id") != EXPECTED_SOURCE_REVIEW_IDS[lane]:
            raise ProductDeltaGraphIncrementResultError(
                "source-read identity drifted"
            )
        if payload.get("terminal_status") != "complete":
            raise ProductDeltaGraphIncrementResultError(
                "source-read lane did not complete; stop before blind review"
            )
        if payload.get("source_read_complete") is not True:
            raise ProductDeltaGraphIncrementResultError(
                "source-read completion receipt drifted"
            )
        receipt = payload.get("terminal_receipt")
        if receipt != {
            "first_terminal_result_preserved": True,
            "source_only_visibility_preserved": True,
            "post_seal_stage_eligible": True,
            "state_reason": None,
        }:
            raise ProductDeltaGraphIncrementResultError(
                "source-read terminal receipt drifted"
            )
        if payload.get("boundary") != {
            "human_validated": False,
            "ground_truth": False,
            "routing_authority": False,
            "provider_calls": 0,
        }:
            raise ProductDeltaGraphIncrementResultError(
                "source-read authority boundary drifted"
            )
        payloads[lane] = payload
        refs[lane] = ref
    return payloads, refs


def _validate_reference_observations(
    *,
    root: Path,
    source_read_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    refs: dict[str, dict[str, Any]] = {}
    for lane, relpath in REFERENCE_OBSERVATION_RELPATHS.items():
        payload, ref = _read_json_ref(root, relpath)
        if payload.get("review_id") != EXPECTED_REFERENCE_REVIEW_IDS[lane]:
            raise ProductDeltaGraphIncrementResultError(
                "reference-observation identity drifted"
            )
        if payload.get("source_first_review_sha256") != source_read_refs[lane][
            "sha256"
        ]:
            raise ProductDeltaGraphIncrementResultError(
                "reference observation points to the wrong source read"
            )
        reviews = payload.get("candidate_reviews")
        if not isinstance(reviews, list) or len(reviews) != 2:
            raise ProductDeltaGraphIncrementResultError(
                "reference-observation candidate count drifted"
            )
        if sorted(str(item.get("model_id")) for item in reviews) != [
            "signaling",
            "social-proof",
        ]:
            raise ProductDeltaGraphIncrementResultError(
                "reference observation does not cover both direct candidates"
            )
        if payload.get("boundary") != {
            "human_validated": False,
            "ground_truth": False,
            "routing_changed": False,
            "provider_calls": 0,
        }:
            raise ProductDeltaGraphIncrementResultError(
                "reference-observation authority boundary drifted"
            )
        refs[lane] = ref
    return refs


def _validate_terminal_outputs(
    *,
    root: Path,
    generation_packets: Mapping[str, Any],
    preoutput_sealed: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    packet_by_alias = {
        str(item["condition_alias"]): item
        for item in _required_list(generation_packets, "packets")
        if isinstance(item, Mapping)
    }
    outputs: dict[str, dict[str, Any]] = {}
    refs: dict[str, dict[str, Any]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    for alias, relpath in TERMINAL_OUTPUT_RELPATHS.items():
        response, ref = _read_json_ref(root, relpath)
        lineage = _required_mapping(
            _required_mapping(preoutput_sealed, "alias_map"), alias
        )
        cell_id = str(lineage.get("cell_id"))
        bundle_arm = CELL_TO_BUNDLE_ARM.get(cell_id)
        if bundle_arm is None:
            raise ProductDeltaGraphIncrementResultError(
                "terminal output has unknown frozen lineage"
            )
        packet = _required_mapping(
            _required_mapping(
                _required_mapping(bundle, "arms"), bundle_arm
            ),
            "packet",
        )
        try:
            compiled = compile_pressure_response(
                response=response,
                packet=packet,
            )
        except (SimulatedReliabilityError, KeyError, TypeError) as exc:
            raise ProductDeltaGraphIncrementResultError(
                f"first terminal output failed deterministic compilation:{alias}"
            ) from exc
        packet_record = _required_mapping(packet_by_alias, alias)
        response_schema = _required_mapping(
            _required_mapping(packet_record, "request_body_projection"),
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
            raise ProductDeltaGraphIncrementResultError(
                "terminal output candidate identity set drifted"
            )
        outputs[alias] = response
        refs[alias] = ref
        receipts[alias] = {
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
    return outputs, refs, receipts


def _validate_response_lengths(
    response: Mapping[str, Any], schema: Mapping[str, Any]
) -> None:
    properties = _required_mapping(schema, "properties")
    for name in ("reconsidered_answer", "change_summary"):
        spec = _required_mapping(properties, name)
        value = response.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ProductDeltaGraphIncrementResultError(
                "terminal output has an empty public field"
            )
        maximum = spec.get("maxLength")
        if isinstance(maximum, int) and len(value) > maximum:
            raise ProductDeltaGraphIncrementResultError(
                "terminal output public field exceeds frozen schema"
            )
    row_schema = _required_mapping(
        _required_mapping(properties, "candidate_dispositions"),
        "items",
    )
    row_properties = _required_mapping(row_schema, "properties")
    for row in _required_list(response, "candidate_dispositions"):
        for name in (
            "strongest_plausible_application",
            "disposition_reason",
            "risk_if_forced",
            "reopen_condition",
        ):
            value = row.get(name) if isinstance(row, Mapping) else None
            spec = _required_mapping(row_properties, name)
            if not isinstance(value, str) or not value.strip():
                raise ProductDeltaGraphIncrementResultError(
                    "terminal output has an empty disposition field"
                )
            maximum = spec.get("maxLength")
            if isinstance(maximum, int) and len(value) > maximum:
                raise ProductDeltaGraphIncrementResultError(
                    "terminal output disposition exceeds frozen schema"
                )


def _build_new_blind_pair(
    *,
    source: str,
    source_ref: Mapping[str, Any],
    terminal_outputs: Mapping[str, Mapping[str, Any]],
    terminal_refs: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, str]]:
    seed = _sha256_text(
        "|".join(
            (
                BLINDING_NAMESPACE,
                str(source_ref["sha256"]),
                str(terminal_refs["condition-A"]["sha256"]),
                str(terminal_refs["condition-B"]["sha256"]),
            )
        )
    )
    condition_for_a = (
        "condition-A" if bytes.fromhex(seed)[0] % 2 == 0 else "condition-B"
    )
    condition_for_b = (
        "condition-B" if condition_for_a == "condition-A" else "condition-A"
    )
    review_arm_map = {"A": condition_for_a, "B": condition_for_b}
    pair: dict[str, Any] = {
        "case_id": "retailer-graph-increment-rehearsal-blind",
        "evidence_class": "complete_checked_in_agent_rehearsal_pair",
        "source": {
            "coverage": "complete_checked_in_conversation",
            "content": source,
            "content_sha256": source_ref["sha256"],
            "known_limit": (
                "This is a synthetic checked-in case and cannot provide human "
                "usefulness evidence."
            ),
        },
        "arms": {
            review_arm: {
                "content": str(
                    terminal_outputs[condition_alias]["reconsidered_answer"]
                ),
                "format": "text",
            }
            for review_arm, condition_alias in sorted(review_arm_map.items())
        },
        "review_warning": (
            "Arm labels are deterministic and neutral. They do not identify "
            "lineage. Compare atomic reasoning moves, not fluency or length."
        ),
    }
    pair["packet_sha256"] = _sha256_json_value(pair)
    return pair, review_arm_map


def _validate_fresh_pair_review(
    payload: Mapping[str, Any],
    *,
    lane: str,
    expected_qualification_ids: list[str],
    expected_pair_ids: list[str],
    expected_standdown_ids: list[str],
) -> list[str]:
    path = PAIR_REVIEW_RELPATHS[lane]
    errors: list[str] = []
    expected_top_level = {
        "schema_version",
        "review_id",
        "fresh_context",
        "saw_lineage_before_freeze",
        "saw_source_proxy_reads_before_freeze",
        "saw_sibling_review_before_freeze",
        "boundary",
        "qualification_reviews",
        "paired_reviews",
        "standdown_reviews",
    }
    if set(payload) != expected_top_level:
        errors.append(f"{path}:top-level keys mismatch")
    if payload.get("schema_version") != REVIEW_RESPONSE_SCHEMA_VERSION:
        errors.append(f"{path}:schema version mismatch")
    if payload.get("review_id") != EXPECTED_PAIR_REVIEW_IDS[lane]:
        errors.append(f"{path}:review id mismatch")
    if payload.get("fresh_context") is not True:
        errors.append(f"{path}:fresh_context must be true")
    for key in (
        "saw_lineage_before_freeze",
        "saw_source_proxy_reads_before_freeze",
        "saw_sibling_review_before_freeze",
    ):
        if payload.get(key) is not False:
            errors.append(f"{path}:{key} must be false")
    if payload.get("boundary") != {
        "answer_quality_scored": False,
        "ground_truth": False,
        "human_validated": False,
        "provider_calls": 0,
        "winner_selected": False,
    }:
        errors.append(f"{path}:authority boundary mismatch")
    forbidden = _walk_keys(payload) & FORBIDDEN_REVIEW_KEYS
    if forbidden:
        errors.append(
            f"{path}:forbidden keys:{','.join(sorted(forbidden))}"
        )
    rendered = json.dumps(payload, ensure_ascii=False)
    for marker in SECRET_MARKERS:
        if marker in rendered:
            errors.append(f"{path}:privacy marker:{marker}")
    for marker in (
        "condition-A",
        "condition-B",
        "f2_fresh_human_controlled_fact_free_direct_only",
        "f3_fresh_human_controlled_fact_free_plus_current_graph",
        "rehearsal_direct_plus_current_one_hop",
    ):
        if marker in rendered:
            errors.append(f"{path}:sealed lineage marker:{marker}")
    errors.extend(
        _validate_qualification_review(
            payload,
            expected_case_ids=expected_qualification_ids,
            path=path,
        )
    )
    errors.extend(
        _validate_pair_review(
            payload,
            expected_pair_ids=expected_pair_ids,
            expected_standdown_ids=expected_standdown_ids,
            path=path,
        )
    )
    return errors


def _arm_for_condition(
    lineage: Mapping[str, Any], condition: str
) -> str:
    labels = [
        str(label)
        for label, record in lineage.items()
        if isinstance(record, Mapping)
        and record.get("condition") == condition
    ]
    if len(labels) != 1:
        raise ProductDeltaGraphIncrementResultError(
            "sealed review lineage is not bijective"
        )
    return labels[0]


def _lineage_for_pair(
    *,
    case_id: str,
    lineage: Mapping[str, Any],
) -> dict[str, Any]:
    if case_id == "retailer-pilot-exact-duplicate-null":
        return {
            "A": "same_baseline_answer",
            "B": "same_baseline_answer",
        }
    if case_id == "retailer-graph-increment-rehearsal-blind":
        return {
            label: copy.deepcopy(record)
            for label, record in lineage.items()
        }
    raise ProductDeltaGraphIncrementResultError(
        "unexpected paired review case"
    )


def _case_ids(value: list[Any]) -> list[str]:
    ids = [
        str(item.get("case_id"))
        for item in value
        if isinstance(item, Mapping) and item.get("case_id")
    ]
    if len(ids) != len(value) or len(ids) != len(set(ids)):
        raise ProductDeltaGraphIncrementResultError(
            "case identity set is malformed"
        )
    return ids


def _index_cases(value: list[Any]) -> dict[str, Mapping[str, Any]]:
    result = {
        str(item.get("case_id")): item
        for item in value
        if isinstance(item, Mapping) and item.get("case_id")
    }
    if len(result) != len(value):
        raise ProductDeltaGraphIncrementResultError(
            "case identity set is malformed"
        )
    return result


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProductDeltaGraphIncrementResultError(
            f"invalid rehearsal JSON input:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaGraphIncrementResultError(
            f"rehearsal JSON input is not an object:{relpath}"
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
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProductDeltaGraphIncrementResultError(
            f"rehearsal text input is not UTF-8:{relpath}"
        ) from exc
    return text, {
        "path": relpath,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    if Path(relpath).is_absolute():
        raise ProductDeltaGraphIncrementResultError(
            "absolute repository path is forbidden"
        )
    path = (root / relpath).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ProductDeltaGraphIncrementResultError(
            "rehearsal path escapes the project root"
        ) from exc
    return path


def _required_mapping(
    value: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    result = value.get(key)
    if not isinstance(result, Mapping):
        raise ProductDeltaGraphIncrementResultError(
            f"rehearsal input is missing mapping:{key}"
        )
    return result


def _required_list(value: Mapping[str, Any], key: str) -> list[Any]:
    result = value.get(key)
    if not isinstance(result, list):
        raise ProductDeltaGraphIncrementResultError(
            f"rehearsal input is missing list:{key}"
        )
    return result


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
            raise ProductDeltaGraphIncrementResultError(
                "generated rehearsal artifact contains a forbidden marker"
            )
