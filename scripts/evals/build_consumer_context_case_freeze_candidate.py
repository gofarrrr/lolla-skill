#!/usr/bin/env python3
"""Build the provider-free consumer-context case-freeze candidate.

This builder deliberately reuses the published substrate reader, constitutional
pressure planner, graph-survival serializer, prospective portfolio custody, and
simulated-reliability packet compiler. It does not create semantic meaning,
call a provider, fill principal-human fields, or change runtime behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.canonical_model_selection import build_assessment_cards
from engine.system_b.constitutional_pressure_survival import (
    build_constitutional_graph_survival_from_snapshot,
)
from engine.system_b.constitutional_pressure_planner import (
    ConstitutionalPressurePlanner,
)
from engine.system_b.prospective_portfolio_custody import (
    build_prospective_portfolio_custody,
)
from engine.system_b.published_knowledge_substrate import PublishedKnowledgeSubstrate
from engine.system_b.simulated_reliability_v1 import build_three_arm_bundle


SCHEMA_VERSION = "lolla.consumer_context_role_attribution_case_candidate.v1"
OUTPUT_RELATIVE = (
    "research/consumer-context-role-attribution-case-candidate-2026-07-23"
)
CONTRACT_RELATIVE = (
    "docs/evals/lolla-consumer-context-pressure-ablation-contract-v1.json"
)
SOURCE_RELATIVE = (
    "research/independent-phase5-cases-2026-07-12/useful-pressure-case.txt"
)
HISTORICAL_TARGET_RELATIVE = (
    "docs/evals/independent-useful-fresh-pressure-pair-target-v1.json"
)
HISTORICAL_RESULT_RELATIVE = (
    "docs/conversation-understanding/"
    "independent-useful-fresh-pressure-result-2026-07-12.md"
)
HISTORICAL_PORTFOLIO_RELATIVE = (
    "research/independent-useful-fresh-pressure-pair-2026-07-12/portfolio.json"
)
HISTORICAL_SOURCE_REVIEW_RELATIVE = (
    "research/independent-phase5-useful-role-case-2026-07-12/"
    "source-review-target.json"
)
CASE_ID = "phase5-independent-useful-retailer-pilot"
CELL_IDS = (
    "f0_fresh_transcript_only",
    "f1_fresh_current_live_bridge_plus_current_graph",
    "f2_fresh_human_controlled_fact_free_direct_only",
    "f3_fresh_human_controlled_fact_free_plus_current_graph",
    "t0_trajectory_continuation_transcript_only",
    "t3_trajectory_continuation_human_controlled_plus_current_graph",
)
CORE_CONTEXT_CELLS = (
    "f0_fresh_transcript_only",
    "f3_fresh_human_controlled_fact_free_plus_current_graph",
    "t0_trajectory_continuation_transcript_only",
    "t3_trajectory_continuation_human_controlled_plus_current_graph",
)
NON_SCALAR_CATEGORIES = (
    "new_source_grounded_leverage",
    "grounded_rejection",
    "grounded_park",
    "circular_restatement_or_coherence_defense_candidate",
    "forced_absorption",
    "unsupported_fact_or_causation",
    "useful_original_value_preserved",
    "useful_original_value_lost",
    "public_friction_or_cognitive_burden",
    "reviewer_uncertainty_and_disagreement",
)
REJECTION_JUDGMENTS = (
    "strongest_plausible_application_was_attempted",
    "failed_condition_is_specific_and_source_supported",
    "forcing_risk_or_harm_is_concrete",
    "rationale_adds_a_source_grounded_test_rather_than_repeating_the_prior_answer",
    "park_condition_is_actionable_and_genuinely_reopenable",
    "semantic_non_consideration_laundering_is_absent_or_named",
    "reviewer_uncertainty_and_disagreement_are_preserved",
)
REQUEST_SYSTEM_FALLBACK = (
    "You are a reconsidering reasoner. Treat the supplied conversation as the "
    "authoritative source and every supplied mental-model item as an intentionally "
    "noisy pressure hypothesis, not evidence about the case. Preserve strong "
    "existing reasoning, inspect every presented item exactly once, and do not "
    "manufacture facts, causation, or quantitative precision."
)


class CaseFreezeCandidateError(ValueError):
    """Raised when the provider-free case candidate cannot be reproduced."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CaseFreezeCandidateError(f"expected JSON object: {path}")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _canonical_text(value: Any) -> str:
    return _canonical_bytes(value).decode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_value(value: Any) -> str:
    return _sha_bytes(_canonical_bytes(value))


def _sha_path(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _repo_ref(relative: str, root: Path) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise CaseFreezeCandidateError(f"missing source: {relative}")
    return {
        "path": relative,
        "sha256": _sha_path(path),
        "bytes": len(path.read_bytes()),
    }


def _parse_conversation(source: str) -> tuple[str, list[dict[str, Any]]]:
    pattern = re.compile(
        r"(?m)^\[Turn (?P<turn>\d+)\] (?P<role>USER|ASSISTANT):\n"
        r"(?P<content>.*?)(?=\n\n\[Turn \d+\] (?:USER|ASSISTANT):\n|\Z)",
        re.DOTALL,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 14:
        raise CaseFreezeCandidateError(
            f"expected 14 source messages, observed {len(matches)}"
        )
    preamble = source[: matches[0].start()].rstrip("\n")
    messages = [
        {
            "turn": int(match.group("turn")),
            "role": match.group("role").lower(),
            "content": match.group("content").rstrip("\n"),
        }
        for match in matches
    ]
    if [row["role"] for row in messages] != ["user", "assistant"] * 7:
        raise CaseFreezeCandidateError("source roles are not seven user/assistant pairs")
    return preamble, messages


def _prompt_tail(prompt: str) -> str:
    parts = prompt.split("\n\n", 1)
    if len(parts) != 2 or not parts[1].strip():
        raise CaseFreezeCandidateError("existing prompt owner has no instruction tail")
    return parts[1].strip()


def _presented_item(
    live_item: Mapping[str, Any],
    packet_item: Mapping[str, Any],
) -> dict[str, Any]:
    if live_item.get("model_id") != packet_item.get("model_id"):
        raise CaseFreezeCandidateError("live pressure and packet model identities differ")
    return {
        "pressure_id": live_item["pressure_id"],
        "model_id": live_item["model_id"],
        "candidate_origin": live_item["candidate_origin"],
        "consumer_locator": live_item["consumer_locator"],
        "pressure_content": dict(packet_item),
    }


def _pressure_components(
    *,
    live_portfolio: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> dict[str, Any]:
    active = list(live_portfolio["active_pressure_items"])
    direct_packet_items = list(
        bundle["arms"]["direct_pressure"]["packet"]["pressure_portfolio"]
    )
    complete_packet_items = list(
        bundle["arms"]["graph_expanded_pressure"]["packet"]["pressure_portfolio"]
    )
    complete_by_model = {row["model_id"]: row for row in complete_packet_items}
    direct_models = [row["model_id"] for row in direct_packet_items]
    if direct_packet_items != complete_packet_items[: len(direct_packet_items)]:
        raise CaseFreezeCandidateError(
            "existing bundle direct component is not byte-identical across arms"
        )
    direct_live = [
        row
        for row in active
        if row["candidate_origin"] == "direct_seed"
    ]
    graph_live = [
        row
        for row in active
        if row["candidate_origin"] == "graph_expansion"
    ]
    if [row["model_id"] for row in direct_live] != direct_models:
        raise CaseFreezeCandidateError("direct packet drifted from live active order")
    direct_items = [
        _presented_item(row, complete_by_model[row["model_id"]])
        for row in direct_live
    ]
    graph_items = [
        _presented_item(row, complete_by_model[row["model_id"]])
        for row in graph_live
    ]
    direct_json = _canonical_text(direct_items)
    graph_json = _canonical_text(graph_items)
    null_graph_json = _canonical_text([])
    complete_block = (
        "EXTERNAL PRESSURE PACKAGE\n"
        "Authority: intentionally noisy hypotheses; graph recall is not relevance proof.\n"
        "DIRECT_COMPONENT_CANONICAL_JSON:\n"
        f"{direct_json}\n"
        "GRAPH_INCREMENT_CANONICAL_JSON:\n"
        f"{graph_json}"
    )
    direct_only_block = (
        "EXTERNAL PRESSURE PACKAGE\n"
        "Authority: intentionally noisy hypotheses; graph recall is not relevance proof.\n"
        "DIRECT_COMPONENT_CANONICAL_JSON:\n"
        f"{direct_json}\n"
        "GRAPH_INCREMENT_CANONICAL_JSON:\n"
        f"{null_graph_json}"
    )
    return {
        "schema_version": "lolla.consumer_context_pressure_components.v1",
        "status": "provider_free_current_policy_projection",
        "direct_component": {
            "items": direct_items,
            "canonical_json": direct_json,
            "sha256": _sha_bytes(direct_json.encode("utf-8")),
            "source_packet_component_sha256": _sha_value(direct_packet_items),
            "complete_packet_prefix_sha256": _sha_value(
                complete_packet_items[: len(direct_packet_items)]
            ),
        },
        "graph_increment": {
            "items": graph_items,
            "canonical_json": graph_json,
            "sha256": _sha_bytes(graph_json.encode("utf-8")),
        },
        "presentations": {
            "direct_only": {
                "text": direct_only_block,
                "sha256": _sha_bytes(direct_only_block.encode("utf-8")),
            },
            "complete": {
                "text": complete_block,
                "sha256": _sha_bytes(complete_block.encode("utf-8")),
            },
        },
        "non_claims": [
            "historical_source_review_is_not_principal_human_approval",
            "active_admission_is_not_relevance_proof",
            "one_hop_relation_is_not_transitive_truth",
            "payload_projection_is_not_runtime_promotion",
        ],
    }


def _base_messages(
    *,
    mode: str,
    system_prompt: str,
    source: str,
    preamble: str,
    source_messages: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    if mode == "fresh_reconstruction":
        return [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    "ATTRIBUTED SOURCE EVIDENCE\n"
                    "The USER and ASSISTANT labels below are evidence attribution. "
                    "You did not author any prior assistant answer in this context. "
                    "The last assistant response is the prior answer to reconsider.\n\n"
                    f"{source}"
                ),
            },
        ]
    if mode != "trajectory_continuation":
        raise CaseFreezeCandidateError(f"unknown context mode: {mode}")
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "SOURCE FILE PREAMBLE — attributed metadata, not a conversation turn\n"
                f"{preamble}"
            ),
        },
    ]
    messages.extend(
        {
            "role": str(row["role"]),
            "content": str(row["content"]),
        }
        for row in source_messages
    )
    return messages


def _request_preview(
    *,
    cell_id: str,
    mode: str,
    system_prompt: str,
    instruction_tail: str,
    pressure_block: str,
    pressure_state: str,
    response_schema: Mapping[str, Any] | None,
    source: str,
    preamble: str,
    source_messages: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    blocked = pressure_state == "missing_current_live_semantic_bridge_supply"
    messages = _base_messages(
        mode=mode,
        system_prompt=system_prompt,
        source=source,
        preamble=preamble,
        source_messages=source_messages,
    )
    final_content = (
        f"{pressure_block}\n\n"
        f"{instruction_tail}\n\n"
        "Return only the declared structured response."
    )
    messages.append({"role": "user", "content": final_content})
    return {
        "schema_version": "lolla.consumer_context_request_preview.v1",
        "cell_id": cell_id,
        "status": (
            "blocked_missing_current_live_semantic_bridge_supply"
            if blocked
            else "complete_provider_neutral_envelope_execution_blocked"
        ),
        "consumer_context_mode": mode,
        "context_implementation": "prompt_level_role_attribution_representation",
        "claim_boundary": (
            "Tests assistant-role history versus attributed transcript evidence "
            "through one future endpoint; it is not an exact live host trajectory."
        ),
        "pressure_supply_state": pressure_state,
        "provider_request_eligible": False,
        "provider_execution_authorized": False,
        "request_body_projection": {
            "model": None,
            "messages": messages,
            "response_schema": dict(response_schema) if response_schema else None,
            "generation": {
                "temperature": None,
                "top_p": None,
                "seed": None,
                "max_output_tokens": None,
                "state": "missing_until_exact_provider_contract_is_authorized",
            },
        },
        "injection": {
            "message_index": len(messages) - 1,
            "message_role": "user",
            "pressure_block_utf8_bytes": len(pressure_block.encode("utf-8")),
            "pressure_block_sha256": _sha_bytes(pressure_block.encode("utf-8")),
            "final_instruction_sha256": _sha_bytes(final_content.encode("utf-8")),
        },
        "custody": {
            "message_count": len(messages),
            "messages_canonical_sha256": _sha_value(messages),
            "response_schema_canonical_sha256": (
                _sha_value(response_schema) if response_schema is not None else None
            ),
            "request_body_projection_canonical_sha256": _sha_value(
                {
                    "model": None,
                    "messages": messages,
                    "response_schema": (
                        dict(response_schema) if response_schema else None
                    ),
                    "generation": {
                        "temperature": None,
                        "top_p": None,
                        "seed": None,
                        "max_output_tokens": None,
                        "state": "missing_until_exact_provider_contract_is_authorized",
                    },
                }
            ),
            "request_utf8_bytes": len(_canonical_bytes(messages)),
            "provider_token_count": None,
            "provider_token_count_state": "missing_unselected_provider_tokenizer",
        },
        "non_claims": [
            "preview_is_not_provider_authorization",
            "preview_is_not_a_completed_provider_request",
            "role_attribution_representation_is_not_an_exact_live_trajectory",
            "one_future_output_is_only_a_single_draw_case_diagnostic",
        ],
    }


def _execution_order(source_sha256: str, contract_sha256: str) -> dict[str, Any]:
    seed_material = (
        f"lolla-consumer-context-order-v1|{source_sha256}|{contract_sha256}"
    )
    seed_sha256 = _sha_bytes(seed_material.encode("utf-8"))
    order = sorted(
        CELL_IDS,
        key=lambda cell_id: _sha_bytes(
            f"{seed_sha256}|{cell_id}".encode("utf-8")
        ),
    )
    return {
        "method": "predeclared_sha256_keyed_pseudorandom_permutation",
        "seed_material_disclosure": (
            "sha256(lolla-consumer-context-order-v1|source_sha256|contract_sha256)"
        ),
        "seed_sha256": seed_sha256,
        "cell_order": order,
        "provider_drift_record_required_per_cell": True,
        "isolation_required": True,
    }


def _forms(
    *,
    source_ref: Mapping[str, Any],
    order: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    target = {
        "schema_version": "lolla.consumer_context_principal_human_target.v1",
        "status": "missing_principal_human_source_first_target",
        "authority": "principal_human",
        "source_first_sequence": [
            "Open only the authoritative source named below.",
            "Complete and sign the source-only fields before opening graph candidates, historical targets, prior outputs, or request previews.",
            "After sealing the source-only target, disclose any prior exposure and review the proposed reference condition.",
            "Do not turn model names, graph paths, or prior successful output into source facts.",
        ],
        "authoritative_source": dict(source_ref),
        "source_only_fields": {
            "reviewer_identity": None,
            "reviewer_role_and_authority": None,
            "source_read_from_start_to_end": None,
            "current_decision_or_position": None,
            "strong_original_reasoning_to_preserve": [],
            "material_unresolved_questions": [],
            "what_would_count_as_new_decision_leverage": [],
            "what_would_count_as_circular_restatement": [],
            "what_would_count_as_forced_absorption_or_harm": [],
            "uncertainty_and_alternative_readings": [],
            "sealed_at": None,
            "signature": None,
        },
        "post_seal_disclosure_fields": {
            "prior_case_source_exposure": None,
            "prior_candidate_or_graph_exposure": None,
            "prior_output_exposure": None,
            "proposed_direct_candidate_disposition": None,
            "corrections_or_rejections": [],
            "disagreement_to_preserve": [],
        },
        "grounded_rejection_vs_coherence_defense_rubric": {
            judgment: None for judgment in REJECTION_JUDGMENTS
        },
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "principal_human_fields_filled_by_builder": False,
    }
    aliases = [f"output_{index:02d}" for index in range(1, 7)]
    review = {
        "schema_version": "lolla.consumer_context_blind_non_scalar_review.v1",
        "status": "template_waiting_for_outputs_and_principal_human_review",
        "review_authority": "principal_human_source_first",
        "execution_order": dict(order),
        "blinding_protocol": {
            "source_target_must_be_signed_before_candidate_or_output_review": True,
            "output_aliases": aliases,
            "alias_to_cell_mapping": None,
            "mapping_state": "missing_until_terminal_outputs_exist",
            "mapping_owner": "nonreviewing_execution_operator",
            "mapping_commitment_required_before_review": True,
            "mapping_sha256_commitment": None,
            "output_display_order_randomized_separately": True,
            "arm_identity_guess_required_before_reveal": True,
            "reveal_only_after_signed_review": True,
        },
        "per_output_reviews": [
            {
                "output_alias": alias,
                "source_fidelity_notes": [],
                "candidate_reviews": [],
                "answer_level_categories": {
                    category: [] for category in NON_SCALAR_CATEGORIES
                },
                "arm_identity_guess": None,
                "guess_reason": None,
                "reviewer_uncertainty": [],
            }
            for alias in aliases
        ],
        "pairwise_reviews": [
            {
                "comparison_id": comparison_id,
                "left_output_alias": None,
                "right_output_alias": None,
                "source_linked_differences": {
                    category: [] for category in NON_SCALAR_CATEGORIES
                },
                "disagreement_and_uncertainty": [],
            }
            for comparison_id in (
                "fresh_current_bridge_distortion",
                "fresh_graph_relationship_increment",
                "fresh_graph_pressure_increment",
                "trajectory_pressure_increment",
                "consumer_context_representation_interaction",
            )
        ],
        "winner_score": None,
        "scalar_score_forbidden": True,
        "provider_calls": 0,
    }
    return target, review


def build(output: Path, *, root: Path = ROOT) -> dict[str, Any]:
    root = root.resolve()
    output = output.resolve()
    source_path = root / SOURCE_RELATIVE
    source = source_path.read_text(encoding="utf-8")
    preamble, source_messages = _parse_conversation(source)
    if f"Case ID: {CASE_ID}" not in preamble:
        raise CaseFreezeCandidateError("authoritative source case ID drifted")

    contract = _load_json(root / CONTRACT_RELATIVE)
    historical_target = _load_json(root / HISTORICAL_TARGET_RELATIVE)
    protected_ids = list(
        historical_target["source_reviewed_expectations"]["protected_candidate_ids"]
    )
    if protected_ids != ["signaling", "social-proof"]:
        raise CaseFreezeCandidateError("historical protected candidate set drifted")
    candidates = [
        {
            "model_id": model_id,
            "recalled_by_mechanism_ids": ["status_signal_used_as_evidence"],
            "reference_status": (
                "historical_source_review_projection_awaiting_principal_human_approval"
            ),
        }
        for model_id in protected_ids
    ]

    load_result = PublishedKnowledgeSubstrate.open(root)
    snapshot = load_result.require_snapshot()
    plan = ConstitutionalPressurePlanner().plan(
        candidates=candidates,
        substrate=snapshot,
    )
    live_portfolio = build_constitutional_graph_survival_from_snapshot(
        candidates=candidates,
        substrate=snapshot,
    )
    portfolio_custody = build_prospective_portfolio_custody(
        candidates=candidates,
        substrate=snapshot,
    )
    challenge_cards = build_assessment_cards(
        {model_id: model.payload for model_id, model in snapshot.models.items()}
    )
    plan_direct = [
        row
        for row in live_portfolio["active_pressure_items"]
        if row["candidate_origin"] == "direct_seed"
    ]
    plan_graph = [
        row
        for row in live_portfolio["active_pressure_items"]
        if row["candidate_origin"] == "graph_expansion"
    ]
    direct_ledger = dict(plan.direct_ledger)
    graph_ledger = dict(plan.graph_ledger)
    source_refs = [
        _repo_ref(SOURCE_RELATIVE, root),
        _repo_ref(HISTORICAL_TARGET_RELATIVE, root),
    ]
    bundle = build_three_arm_bundle(
        case_id=CASE_ID,
        conversation=source,
        direct_ledger=direct_ledger,
        graph_ledger=graph_ledger,
        challenge_cards=challenge_cards,
        source_refs=[
            {"path": row["path"], "sha256": row["sha256"]} for row in source_refs
        ],
    )
    components = _pressure_components(
        live_portfolio=live_portfolio,
        bundle=bundle,
    )

    control_arm = bundle["arms"]["transcript_only"]
    direct_arm = bundle["arms"]["direct_pressure"]
    graph_arm = bundle["arms"]["graph_expanded_pressure"]
    control_system = control_arm["prompts"]["system_prompt"]
    pressure_system = graph_arm["prompts"]["system_prompt"]
    if pressure_system != direct_arm["prompts"]["system_prompt"]:
        raise CaseFreezeCandidateError("direct and graph pressure system prompts differ")
    control_tail = _prompt_tail(control_arm["prompts"]["user_prompt"])
    pressure_tail = _prompt_tail(graph_arm["prompts"]["user_prompt"])
    if pressure_tail != _prompt_tail(direct_arm["prompts"]["user_prompt"]):
        raise CaseFreezeCandidateError("direct and graph pressure instruction tails differ")

    null_pressure = (
        "EXTERNAL PRESSURE PACKAGE\n"
        "PRESSURE_SUPPLY_CANONICAL_JSON:\n"
        '{"pressure_supply":"none_transcript_only"}'
    )
    missing_f1 = (
        "EXTERNAL PRESSURE PACKAGE\n"
        "PRESSURE_SUPPLY_CANONICAL_JSON:\n"
        '{"pressure_supply":"missing_current_live_semantic_bridge",'
        '"execution_prohibited":true}'
    )
    previews: dict[str, dict[str, Any]] = {}
    preview_specs = {
        "f0_fresh_transcript_only": (
            "fresh_reconstruction",
            control_system,
            control_tail,
            null_pressure,
            "none_transcript_only",
            control_arm["response_schema"],
        ),
        "f1_fresh_current_live_bridge_plus_current_graph": (
            "fresh_reconstruction",
            REQUEST_SYSTEM_FALLBACK,
            pressure_tail,
            missing_f1,
            "missing_current_live_semantic_bridge_supply",
            None,
        ),
        "f2_fresh_human_controlled_fact_free_direct_only": (
            "fresh_reconstruction",
            pressure_system,
            pressure_tail,
            components["presentations"]["direct_only"]["text"],
            "historical_source_review_reference_direct_only_awaiting_principal_human",
            direct_arm["response_schema"],
        ),
        "f3_fresh_human_controlled_fact_free_plus_current_graph": (
            "fresh_reconstruction",
            pressure_system,
            pressure_tail,
            components["presentations"]["complete"]["text"],
            "historical_source_review_reference_plus_current_graph_awaiting_principal_human",
            graph_arm["response_schema"],
        ),
        "t0_trajectory_continuation_transcript_only": (
            "trajectory_continuation",
            control_system,
            control_tail,
            null_pressure,
            "none_transcript_only",
            control_arm["response_schema"],
        ),
        "t3_trajectory_continuation_human_controlled_plus_current_graph": (
            "trajectory_continuation",
            pressure_system,
            pressure_tail,
            components["presentations"]["complete"]["text"],
            "historical_source_review_reference_plus_current_graph_awaiting_principal_human",
            graph_arm["response_schema"],
        ),
    }
    for cell_id in CELL_IDS:
        mode, system_prompt, tail, block, state, schema = preview_specs[cell_id]
        previews[cell_id] = _request_preview(
            cell_id=cell_id,
            mode=mode,
            system_prompt=system_prompt,
            instruction_tail=tail,
            pressure_block=block,
            pressure_state=state,
            response_schema=schema,
            source=source,
            preamble=preamble,
            source_messages=source_messages,
        )

    active_ids = [row["pressure_id"] for row in live_portfolio["active_pressure_items"]]
    presented = (
        components["direct_component"]["items"]
        + components["graph_increment"]["items"]
    )
    presented_ids = [row["pressure_id"] for row in presented]
    direct_identity = (
        components["direct_component"]["source_packet_component_sha256"]
        == components["direct_component"]["complete_packet_prefix_sha256"]
        and components["presentations"]["direct_only"]["text"].count(
            components["direct_component"]["canonical_json"]
        )
        == 1
        and components["presentations"]["complete"]["text"].count(
            components["direct_component"]["canonical_json"]
        )
        == 1
    )
    f3_t3_identity = (
        previews["f3_fresh_human_controlled_fact_free_plus_current_graph"][
            "injection"
        ]["pressure_block_sha256"]
        == previews[
            "t3_trajectory_continuation_human_controlled_plus_current_graph"
        ]["injection"]["pressure_block_sha256"]
    )
    f0_t0_null_identity = (
        previews["f0_fresh_transcript_only"]["injection"]["pressure_block_sha256"]
        == previews["t0_trajectory_continuation_transcript_only"]["injection"][
            "pressure_block_sha256"
        ]
    )
    f3_t3_final_identity = (
        previews["f3_fresh_human_controlled_fact_free_plus_current_graph"][
            "injection"
        ]["final_instruction_sha256"]
        == previews[
            "t3_trajectory_continuation_human_controlled_plus_current_graph"
        ]["injection"]["final_instruction_sha256"]
    )
    f3_t3_schema_identity = (
        previews["f3_fresh_human_controlled_fact_free_plus_current_graph"][
            "custody"
        ]["response_schema_canonical_sha256"]
        == previews[
            "t3_trajectory_continuation_human_controlled_plus_current_graph"
        ]["custody"]["response_schema_canonical_sha256"]
    )
    f0_t0_final_identity = (
        previews["f0_fresh_transcript_only"]["injection"][
            "final_instruction_sha256"
        ]
        == previews["t0_trajectory_continuation_transcript_only"]["injection"][
            "final_instruction_sha256"
        ]
    )
    f0_t0_schema_identity = (
        previews["f0_fresh_transcript_only"]["custody"][
            "response_schema_canonical_sha256"
        ]
        == previews["t0_trajectory_continuation_transcript_only"]["custody"][
            "response_schema_canonical_sha256"
        ]
    )
    receipts = {
        "schema_version": "lolla.consumer_context_case_custody_receipts.v1",
        "status": "mechanical_controls_pass",
        "f2_f3_direct_component_identity": {
            "passed": direct_identity,
            "direct_component_sha256": components["direct_component"]["sha256"],
            "method": (
                "F2 and F3 serialize the same canonical direct-component string; "
                "F3 adds only the separately serialized graph increment."
            ),
        },
        "f3_t3_pressure_presentation_identity": {
            "passed": (
                f3_t3_identity and f3_t3_final_identity and f3_t3_schema_identity
            ),
            "pressure_block_sha256": previews[
                "f3_fresh_human_controlled_fact_free_plus_current_graph"
            ]["injection"]["pressure_block_sha256"],
            "final_instruction_sha256": previews[
                "f3_fresh_human_controlled_fact_free_plus_current_graph"
            ]["injection"]["final_instruction_sha256"],
            "response_schema_sha256": previews[
                "f3_fresh_human_controlled_fact_free_plus_current_graph"
            ]["custody"]["response_schema_canonical_sha256"],
        },
        "f0_t0_null_pressure_identity": {
            "passed": (
                f0_t0_null_identity and f0_t0_final_identity and f0_t0_schema_identity
            ),
            "pressure_block_sha256": previews["f0_fresh_transcript_only"][
                "injection"
            ]["pressure_block_sha256"],
            "final_instruction_sha256": previews["f0_fresh_transcript_only"][
                "injection"
            ]["final_instruction_sha256"],
            "response_schema_sha256": previews["f0_fresh_transcript_only"][
                "custody"
            ]["response_schema_canonical_sha256"],
        },
        "active_candidate_to_presented_payload_bijection": {
            "passed": (
                active_ids == presented_ids
                and len(active_ids) == len(set(active_ids))
                and len(presented_ids) == len(set(presented_ids))
            ),
            "planner_active_pressure_ids": active_ids,
            "presented_pressure_ids": presented_ids,
            "missing": sorted(set(active_ids) - set(presented_ids)),
            "extra": sorted(set(presented_ids) - set(active_ids)),
            "duplicate_presented_ids": sorted(
                {
                    pressure_id
                    for pressure_id in presented_ids
                    if presented_ids.count(pressure_id) > 1
                }
            ),
        },
        "source_content_custody": {
            "source_sha256": _sha_path(source_path),
            "source_utf8_bytes": len(source.encode("utf-8")),
            "message_count": len(source_messages),
            "last_assistant_answer_sha256": _sha_bytes(
                str(source_messages[-1]["content"]).encode("utf-8")
            ),
            "coverage": "complete",
            "omissions": [],
        },
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "semantic_correctness_certified": False,
    }
    if not all(
        (
            direct_identity,
            receipts["f3_t3_pressure_presentation_identity"]["passed"],
            receipts["f0_t0_null_pressure_identity"]["passed"],
            receipts["active_candidate_to_presented_payload_bijection"]["passed"],
        )
    ):
        raise CaseFreezeCandidateError("one or more mechanical equality gates failed")

    order = _execution_order(
        _sha_path(source_path),
        _sha_path(root / CONTRACT_RELATIVE),
    )
    principal_target, blind_review = _forms(
        source_ref=_repo_ref(SOURCE_RELATIVE, root),
        order=order,
    )
    complete_preview_count = sum(
        preview["status"].startswith("complete_") for preview in previews.values()
    )
    readiness = {
        "schema_version": "lolla.consumer_context_case_readiness.v1",
        "status": "provider_free_case_candidate_valid_execution_not_ready",
        "design_shape_valid": True,
        "case_selected": True,
        "context_implementation_selected": True,
        "context_implementation": "prompt_level_role_attribution_representation",
        "request_preview_count": len(previews),
        "complete_provider_neutral_preview_count": complete_preview_count,
        "blocked_preview_count": len(previews) - complete_preview_count,
        "mechanical_gates": {
            "authoritative_source_hash_locked": True,
            "current_substrate_and_policy_locked": True,
            "f2_f3_direct_component_identity": direct_identity,
            "f3_t3_pressure_presentation_identity": receipts[
                "f3_t3_pressure_presentation_identity"
            ]["passed"],
            "f0_t0_null_pressure_identity": receipts[
                "f0_t0_null_pressure_identity"
            ]["passed"],
            "active_candidate_to_presented_payload_bijection": receipts[
                "active_candidate_to_presented_payload_bijection"
            ]["passed"],
            "non_scalar_review_form_frozen": True,
            "stochasticity_and_order_policy_frozen": True,
            "blind_review_protocol_frozen": True,
        },
        "execution_ready": False,
        "causal_interaction_identified": False,
        "self_justification_mechanism_identified": False,
        "single_draw_evidence_class": "single_draw_case_diagnostic",
        "blocking_prerequisites": [
            {
                "id": "principal_human_source_first_target",
                "state": "missing",
                "owner": "principal_human",
            },
            {
                "id": "principal_human_reference_condition_approval",
                "state": "missing",
                "owner": "principal_human",
            },
            {
                "id": "f1_current_live_semantic_bridge_supply",
                "state": "missing",
                "owner": "future_separately_authorized_semantic_bridge_run",
                "reason": (
                    "No checked-in current-live bridge output exists for this "
                    "exact source. Older role/mechanism readers are not substitutes."
                ),
            },
            {
                "id": "exact_provider_model_interface_and_generation_contract",
                "state": "missing",
                "owner": "founder_and_execution_operator",
            },
            {
                "id": "provider_call_and_usd_ceiling_authorization",
                "state": "missing",
                "owner": "founder",
            },
            {
                "id": "provider_token_counts_and_request_cost_estimate",
                "state": "missing_until_provider_contract_is_selected",
                "owner": "execution_operator",
            },
        ],
        "stop_rule": (
            "Do not execute any cell, create the F1 semantic supply, fill human "
            "fields, or call the case evidence causal until every blocking "
            "prerequisite is separately satisfied."
        ),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "runtime_change": False,
        "graph_policy_change": False,
    }

    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    _write_json(output / "portfolio-custody.json", portfolio_custody)
    _write_json(output / "portfolio-bundle.json", bundle)
    _write_json(output / "pressure-components.json", components)
    _write_json(output / "custody-receipts.json", receipts)
    _write_json(output / "principal-human-target-template.json", principal_target)
    _write_json(output / "blind-review-form.json", blind_review)
    _write_json(output / "readiness.json", readiness)
    for cell_id, preview in previews.items():
        _write_json(output / "request-previews" / f"{cell_id}.json", preview)

    artifact_paths = sorted(
        path
        for path in output.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    )
    output_reference = OUTPUT_RELATIVE
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "date": "2026-07-23",
        "status": "provider_free_case_candidate_valid_execution_not_ready",
        "evidence_class": (
            "retrospective_mechanism_replay_case_preparation_not_new_graph_value_"
            "evidence_not_principal_human_or_provider_evidence"
        ),
        "falsifiable_question": contract["falsifiable_question"],
        "allowed_causal_change": (
            "Represent the same declared source and prior answer as assistant-role "
            "history versus explicitly attributed transcript evidence while holding "
            "the complete F3/T3 pressure presentation byte-identical."
        ),
        "case": {
            "case_id": CASE_ID,
            "authoritative_source": _repo_ref(SOURCE_RELATIVE, root),
            "source_coverage": "complete",
            "processing_omissions": [],
            "checked_in_safe_synthetic_case": True,
            "retrospective_case_rule_applied": True,
            "retrospective_reason": (
                "The case and historically protected signaling/social-proof delta "
                "were already reviewed after an earlier successful fresh-pressure "
                "result. This preparation cannot be new prospective graph-value evidence."
            ),
        },
        "selected_context_implementation": {
            "id": "prompt_level_role_attribution_representation",
            "same_future_endpoint_for_core_cells_required": True,
            "exact_live_trajectory_claimed": False,
            "fresh_independent_truth_claimed": False,
        },
        "reference_condition_candidate": {
            "status": (
                "historical_source_review_projection_awaiting_principal_human_approval"
            ),
            "protected_direct_model_ids": protected_ids,
            "fact_free_mechanism": "status_signal_used_as_evidence",
            "historical_refs": [
                _repo_ref(HISTORICAL_TARGET_RELATIVE, root),
                _repo_ref(HISTORICAL_SOURCE_REVIEW_RELATIVE, root),
                _repo_ref(HISTORICAL_PORTFOLIO_RELATIVE, root),
                _repo_ref(HISTORICAL_RESULT_RELATIVE, root),
            ],
            "author_identity": "historical_source_reviewer_artifact",
            "principal_human_authority_established": False,
            "prior_graph_or_output_exposure": "yes_case_selected_after_prior_success",
            "not_an_oracle": True,
        },
        "current_graph_projection": {
            "substrate_release_id": snapshot.release_id,
            "substrate_release_identity": portfolio_custody[
                "substrate_identity"
            ]["release_identity"],
            "policy": portfolio_custody["policy_identity"],
            "direct_active_model_ids": [row["model_id"] for row in plan_direct],
            "graph_active_model_ids": [row["model_id"] for row in plan_graph],
            "active_pressure_count": len(active_ids),
            "direct_reserve_count": len(
                plan.direct_ledger["reserve_candidates"]
            ),
            "graph_reserve_count": len(
                plan.graph_ledger["reserve_candidates"]
            ),
            "direction": "outgoing_authored_relations",
            "hop_depth": 1,
            "policy_changed": False,
        },
        "request_previews": {
            "cell_ids": list(CELL_IDS),
            "core_context_cell_ids": list(CORE_CONTEXT_CELLS),
            "count": len(previews),
            "complete_provider_neutral_count": complete_preview_count,
            "blocked_cell_ids": [
                cell_id
                for cell_id, preview in previews.items()
                if preview["status"].startswith("blocked_")
            ],
            "provider_route_selected": False,
            "provider_execution_authorized": False,
        },
        "stochasticity_policy": {
            "classification": "single_draw_case_diagnostic",
            "draws_per_cell": 1,
            "automatic_retry": False,
            "semantic_retry": False,
            "fallback": False,
            "response_healing": False,
            "replacement_call": False,
            "first_terminal_result_preserved": True,
            "expected_causal_effect_identified": False,
        },
        "execution_order": order,
        "readiness_ref": f"{output_reference}/readiness.json",
        "receipt_ref": f"{output_reference}/custody-receipts.json",
        "principal_human_target_ref": (
            f"{output_reference}/principal-human-target-template.json"
        ),
        "blind_review_form_ref": f"{output_reference}/blind-review-form.json",
        "artifacts": [
            {
                "path": (
                    f"{output_reference}/"
                    f"{path.relative_to(output).as_posix()}"
                ),
                "sha256": _sha_path(path),
                "bytes": len(path.read_bytes()),
            }
            for path in artifact_paths
        ],
        "authorization": {
            "provider_calls": 0,
            "provider_cost_usd": 0.0,
            "private_archive_inspection": False,
            "principal_human_fields_filled": False,
            "runtime_change": False,
            "graph_policy_change": False,
            "live_skill_change": False,
            "fresh_context_promotion": False,
            "product_claim": False,
        },
        "next_decision": {
            "owner": "principal_human",
            "question": (
                "After reading only the authoritative source, does the proposed "
                "source-first target and the signaling/social-proof reference "
                "condition deserve approval, correction, or rejection?"
            ),
            "provider_execution_is_not_the_next_automatic_step": True,
        },
    }
    _write_json(output / "manifest.json", manifest)
    return manifest


def _compare_directories(expected: Path, observed: Path) -> list[str]:
    expected_files = {
        path.relative_to(expected).as_posix(): path
        for path in expected.rglob("*")
        if path.is_file()
    }
    observed_files = {
        path.relative_to(observed).as_posix(): path
        for path in observed.rglob("*")
        if path.is_file()
    }
    errors: list[str] = []
    if set(expected_files) != set(observed_files):
        errors.append(
            "case-candidate artifact set drifted: "
            f"expected={sorted(expected_files)} observed={sorted(observed_files)}"
        )
    for relative in sorted(set(expected_files) & set(observed_files)):
        if expected_files[relative].read_bytes() != observed_files[relative].read_bytes():
            errors.append(f"case-candidate artifact drifted: {relative}")
    return errors


def validate_checked_in(*, root: Path = ROOT) -> tuple[list[str], dict[str, Any]]:
    root = root.resolve()
    observed = root / OUTPUT_RELATIVE
    errors: list[str] = []
    if not observed.is_dir():
        return [f"missing case-candidate directory: {OUTPUT_RELATIVE}"], {
            "status": "invalid",
            "execution_ready": False,
        }
    with tempfile.TemporaryDirectory(prefix="lolla-case-candidate-") as temp:
        expected = Path(temp) / "candidate"
        manifest = build(expected, root=root)
        errors.extend(_compare_directories(expected, observed))
    readiness_path = observed / "readiness.json"
    readiness = _load_json(readiness_path) if readiness_path.is_file() else {}
    receipt = {
        "status": "valid" if not errors else "invalid",
        "schema_version": manifest.get("schema_version"),
        "case_id": manifest.get("case", {}).get("case_id"),
        "request_preview_count": readiness.get("request_preview_count"),
        "complete_provider_neutral_preview_count": readiness.get(
            "complete_provider_neutral_preview_count"
        ),
        "blocked_preview_count": readiness.get("blocked_preview_count"),
        "mechanical_gates_pass": all(
            readiness.get("mechanical_gates", {}).values()
        ),
        "execution_ready": readiness.get("execution_ready"),
        "provider_calls": readiness.get("provider_calls"),
        "provider_cost_usd": readiness.get("provider_cost_usd"),
    }
    return errors, receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.validate_only:
        errors, receipt = validate_checked_in(root=root)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0
    output = (
        args.output.resolve()
        if args.output is not None
        else root / OUTPUT_RELATIVE
    )
    manifest = build(output, root=root)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "case_id": manifest["case"]["case_id"],
                "direct_active_model_ids": manifest["current_graph_projection"][
                    "direct_active_model_ids"
                ],
                "graph_active_model_ids": manifest["current_graph_projection"][
                    "graph_active_model_ids"
                ],
                "request_preview_count": manifest["request_previews"]["count"],
                "complete_provider_neutral_count": manifest["request_previews"][
                    "complete_provider_neutral_count"
                ],
                "blocked_cell_ids": manifest["request_previews"][
                    "blocked_cell_ids"
                ],
                "provider_calls": manifest["authorization"]["provider_calls"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
