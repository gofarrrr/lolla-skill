"""Provider-free coverage and bounded-view construction for Phase 2.

Deterministic code owns hashes, exact source resolution, lineage, accounting,
and budgets.  Semantic coverage and dispositions must be supplied by a
prospectively frozen source-review artifact; this module never infers them from
family labels, keywords, embeddings, or transcript prose.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .conversation_state_candidates import SourceCatalog, SourceSpan, build_source_catalog
from .reasoning_process_contracts import (
    BOUNDED_VIEW_SCHEMA_VERSION,
    OBSERVATION_FAMILIES,
    VIEW_STATUS,
    phase0_contract,
    validate_bounded_view,
)


COVERAGE_CONTRACT_SCHEMA = "lolla.reasoning_process_phase2_coverage_contract.v1"
COVERAGE_CANDIDATES_SCHEMA = "lolla.reasoning_process_phase2_coverage_candidates.v1"
COVERAGE_REVIEW_SCHEMA = "lolla.reasoning_process_phase2_coverage_review.v1"
SOURCE_REVIEW_ADDENDUM_SCHEMA = "lolla.reasoning_process_source_review_addendum.v1"
COMBINED_MANIFEST_SCHEMA = "lolla.reasoning_process_combined_manifest.v1"
PHASE2_REPORT_SCHEMA = "lolla.reasoning_process_phase2_report.v1"
FAN_IN_STRESS_SCHEMA = "lolla.reasoning_process_phase2_fan_in_stress.v1"
PROBE_INPUT_SCHEMA = "lolla.reasoning_process_probe_input.v1"

_COVERAGE_STATES = {"ready", "partial", "blocked"}
_REVIEW_DECISIONS = {"covered_by_phase1", "addendum_required", "blocked"}


class ReasoningProcessViewError(ValueError):
    """Raised when Phase-2 custody, review, or view accounting is invalid."""


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def resolve_target_evidence(
    *, catalog: SourceCatalog, speaker: str, turn_index: int, quote: str
) -> SourceSpan:
    """Resolve a frozen quote to the smallest exact catalog span.

    Sentence spans are preferred over the containing turn.  Resolution fails
    rather than guessing when no unique smallest span exists.
    """

    matches = [
        span
        for span in catalog.spans
        if span.speaker == speaker
        and span.turn_index == turn_index
        and quote in span.text
    ]
    if not matches:
        raise ReasoningProcessViewError(
            f"target quote not found for {speaker} turn {turn_index}: {quote!r}"
        )
    minimum_length = min(len(span.text) for span in matches)
    shortest = [span for span in matches if len(span.text) == minimum_length]
    if len(shortest) != 1:
        raise ReasoningProcessViewError(
            f"target quote has ambiguous smallest source span: {quote!r}"
        )
    return shortest[0]


def build_coverage_candidates(
    *, contract: Mapping[str, Any], repo_root: Path
) -> dict[str, Any]:
    """Build mechanical overlap candidates without judging semantic coverage."""

    _validate_contract_shape(contract)
    base = contract["base_phase1_contract"]
    _require_file_hash(repo_root / base["path"], base["sha256"], "Phase-1 contract")

    cases: list[dict[str, Any]] = []
    for case in contract["cases"]:
        source_path = repo_root / case["source_path"]
        ledger_path = repo_root / case["phase1_ledger_path"]
        _require_file_hash(source_path, case["source_sha256"], "conversation source")
        _require_file_hash(ledger_path, case["phase1_ledger_sha256"], "Phase-1 ledger")
        source_text = source_path.read_text(encoding="utf-8")
        catalog = build_source_catalog(
            source_text=source_text, source_path=case["source_path"]
        )
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        if ledger.get("source", {}).get("conversation_id") != case["case_id"]:
            raise ReasoningProcessViewError("case ID does not match Phase-1 ledger")

        targets: list[dict[str, Any]] = []
        for target in case["targets"]:
            resolved_evidence: list[dict[str, Any]] = []
            target_span_ids: list[str] = []
            for evidence in target["source_evidence"]:
                span = resolve_target_evidence(
                    catalog=catalog,
                    speaker=evidence["speaker"],
                    turn_index=evidence["turn_index"],
                    quote=evidence["quote"],
                )
                target_span_ids.append(span.span_id)
                resolved_evidence.append(
                    {
                        **evidence,
                        "span_id": span.span_id,
                        "span_kind": span.kind,
                        "resolved_span_text": span.text,
                    }
                )
            target_span_set = set(target_span_ids)
            overlapping = [
                observation
                for observation in ledger["observations"]
                if target_span_set.intersection(observation["source_span_ids"])
            ]
            targets.append(
                {
                    "target_id": target["target_id"],
                    "view_kind": target["view_kind"],
                    "description": target["description"],
                    "resolved_evidence": resolved_evidence,
                    "target_span_ids": list(dict.fromkeys(target_span_ids)),
                    "mechanical_overlap_observations": [
                        {
                            "observation_id": item["observation_id"],
                            "family": item["family"],
                            "interpretation": item["interpretation"],
                            "semantic_status": item["semantic_status"],
                            "source_span_ids": item["source_span_ids"],
                        }
                        for item in overlapping
                    ],
                    "mechanical_overlap_count": len(overlapping),
                    "semantic_coverage_decided_by_code": False,
                }
            )
        cases.append(
            {
                "case_id": case["case_id"],
                "source_path": case["source_path"],
                "source_sha256": case["source_sha256"],
                "phase1_ledger_path": case["phase1_ledger_path"],
                "phase1_ledger_sha256": case["phase1_ledger_sha256"],
                "phase1_observation_count": len(ledger["observations"]),
                "targets": targets,
            }
        )
    return {
        "schema_version": COVERAGE_CANDIDATES_SCHEMA,
        "status": "mechanical_candidates_only_source_review_required",
        "coverage_contract_sha256": sha256_bytes(canonical_json_bytes(contract)),
        "case_count": len(cases),
        "target_count": sum(len(case["targets"]) for case in cases),
        "cases": cases,
        "boundary": {
            "exact_source_resolution_deterministic": True,
            "overlap_is_semantic_coverage": False,
            "semantic_coverage_decided_by_code": False,
            "provider_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
    }


def build_phase2_artifacts(
    *,
    contract: Mapping[str, Any],
    candidates: Mapping[str, Any],
    review: Mapping[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    """Build append-only addenda, combined manifests, and provider-free views."""

    _validate_review(contract=contract, candidates=candidates, review=review)
    hard_gates = phase0_contract()["numeric_gates"]
    case_outputs: list[dict[str, Any]] = []
    review_cases = {case["case_id"]: case for case in review["cases"]}
    candidate_cases = {case["case_id"]: case for case in candidates["cases"]}

    for contract_case in contract["cases"]:
        case_id = contract_case["case_id"]
        review_case = review_cases[case_id]
        candidate_case = candidate_cases[case_id]
        source_text = (repo_root / contract_case["source_path"]).read_text(encoding="utf-8")
        catalog = build_source_catalog(
            source_text=source_text, source_path=contract_case["source_path"]
        )
        ledger = json.loads(
            (repo_root / contract_case["phase1_ledger_path"]).read_text(encoding="utf-8")
        )
        target_candidates = {
            target["target_id"]: target for target in candidate_case["targets"]
        }
        target_contracts = {
            target["target_id"]: target for target in contract_case["targets"]
        }

        addendum_observations: list[dict[str, Any]] = []
        target_sources: dict[str, list[str]] = {}
        target_spans: dict[str, list[str]] = {}
        for decision in review_case["targets"]:
            target_id = decision["target_id"]
            candidate = target_candidates[target_id]
            target_spans[target_id] = candidate["target_span_ids"]
            if decision["decision"] == "covered_by_phase1":
                target_sources[target_id] = decision["phase1_observation_ids"]
            elif decision["decision"] == "addendum_required":
                observation_id = f"phase2-source-review-{target_id}"
                target_sources[target_id] = [observation_id]
                addendum_observations.append(
                    _source_review_observation(
                        observation_id=observation_id,
                        target=target_contracts[target_id],
                        span_ids=candidate["target_span_ids"],
                        reason=decision["reason"],
                    )
                )
            else:
                target_sources[target_id] = []

        addendum = {
            "schema_version": SOURCE_REVIEW_ADDENDUM_SCHEMA,
            "status": "prospective_provider_free_source_review",
            "case_id": case_id,
            "base_ledger_path": contract_case["phase1_ledger_path"],
            "base_ledger_sha256": "sha256:" + contract_case["phase1_ledger_sha256"],
            "coverage_contract_sha256": "sha256:" + candidates["coverage_contract_sha256"],
            "coverage_review_sha256": "sha256:" + sha256_bytes(canonical_json_bytes(review)),
            "observations": addendum_observations,
            "boundary": {
                "phase1_ledger_modified": False,
                "source_review_is_independent_gold": False,
                "semantic_relevance_inferred_by_code": False,
                "direct_graph_routing_allowed": False,
                "provider_calls": 0,
            },
        }
        addendum_sha = sha256_bytes(canonical_json_bytes(addendum))
        combined_observations = [*ledger["observations"], *addendum_observations]
        manifest = {
            "schema_version": COMBINED_MANIFEST_SCHEMA,
            "status": "provider_free_append_only_overlay",
            "case_id": case_id,
            "authoritative_source_path": contract_case["source_path"],
            "authoritative_source_sha256": "sha256:" + contract_case["source_sha256"],
            "base_ledger_path": contract_case["phase1_ledger_path"],
            "base_ledger_sha256": "sha256:" + contract_case["phase1_ledger_sha256"],
            "addendum_sha256": "sha256:" + addendum_sha,
            "observation_ids": [item["observation_id"] for item in combined_observations],
            "boundary": {
                "append_only": True,
                "phase1_ledger_modified": False,
                "authoritative_conversation_replaced": False,
                "direct_graph_routing_allowed": False,
            },
        }
        manifest_sha = sha256_bytes(canonical_json_bytes(manifest))

        views: list[dict[str, Any]] = []
        validations: list[dict[str, Any]] = []
        probe_inputs: list[dict[str, Any]] = []
        for target_decision in review_case["targets"]:
            target_id = target_decision["target_id"]
            target = target_contracts[target_id]
            if target_decision["decision"] == "blocked":
                continue
            probe_inputs.append(
                build_probe_input_packet(
                    case_id=case_id,
                    source_path=contract_case["source_path"],
                    source_sha256=contract_case["source_sha256"],
                    source_text=source_text,
                    base_observations=ledger["observations"],
                    view_kind=target["view_kind"],
                )
            )
            # Every view receives the complete immutable Phase-1 ledger plus
            # only its own prospectively reviewed addendum observation.  This
            # avoids both a deterministic relevance gate over the base ledger
            # and cross-view addendum fan-in.
            view_input_observations = list(ledger["observations"])
            if target_decision["decision"] == "addendum_required":
                target_source_ids = set(target_sources[target_id])
                view_input_observations.extend(
                    item
                    for item in addendum_observations
                    if item["observation_id"] in target_source_ids
                )
            input_projection = [
                {
                    "observation_id": item["observation_id"],
                    "family": item["family"],
                    "interpretation": item["interpretation"],
                    "semantic_status": item["semantic_status"],
                    "source_span_ids": item["source_span_ids"],
                }
                for item in view_input_observations
            ]
            input_bytes = len(canonical_json_bytes({"observations": input_projection}))
            item_id = f"view-item-{target_id}"
            included_ids = target_sources[target_id]
            view = {
                "schema_version": BOUNDED_VIEW_SCHEMA_VERSION,
                "status": VIEW_STATUS,
                "view_id": f"phase2-view-{target_id}",
                "view_kind": target["view_kind"],
                "question": _view_question(target["view_kind"]),
                "source_ledger_sha256": "sha256:" + manifest_sha,
                "input": {
                    "ledger_observation_ids": [
                        item["observation_id"] for item in view_input_observations
                    ]
                },
                "items": [
                    {
                        "view_item_id": item_id,
                        "interpretation": target["description"],
                        "status": target_decision["semantic_status"],
                        "source_observation_ids": included_ids,
                        "source_span_ids": target_spans[target_id],
                        "limitations": "Source-reviewed development fixture, not independent gold and not a model-quality result.",
                    }
                ],
                "dispositions": [
                    {
                        "observation_id": observation["observation_id"],
                        "disposition": (
                            "included"
                            if observation["observation_id"] in included_ids
                            else "parked_not_applicable"
                        ),
                        "authority": "source_reviewer",
                        "reason": (
                            "Source reviewer linked this observation to the protected target."
                            if observation["observation_id"] in included_ids
                            else "Source reviewer did not require this observation for this bounded question; it remains recoverable from the combined manifest."
                        ),
                        "view_item_ids": (
                            [item_id] if observation["observation_id"] in included_ids else []
                        ),
                    }
                    for observation in view_input_observations
                ],
                "budget": {
                    "max_input_observations": hard_gates["max_view_input_observations"],
                    "max_input_utf8_bytes": hard_gates["max_view_input_utf8_bytes"],
                    "max_output_items": hard_gates["max_view_output_items"],
                    "observed_input_observations": len(view_input_observations),
                    "observed_input_utf8_bytes": input_bytes,
                    "observed_output_items": 1,
                    "budget_exceeded": (
                        len(view_input_observations) > hard_gates["max_view_input_observations"]
                        or input_bytes > hard_gates["max_view_input_utf8_bytes"]
                        or 1 > hard_gates["max_view_output_items"]
                    ),
                },
                "boundary": {
                    "authoritative_source": False,
                    "semantic_selection_performed_by_code": False,
                    "omissions_recoverable_from_ledger": True,
                    "final_output_evaluated": False,
                    "quality_score_included": False,
                    "direct_graph_routing_allowed": False,
                },
            }
            validation = validate_bounded_view(
                view,
                known_ledger_observation_ids=[
                    item["observation_id"] for item in combined_observations
                ],
                known_span_ids=catalog.by_id(),
                expected_ledger_sha256="sha256:" + manifest_sha,
            )
            views.append(view)
            validations.append(validation)

        case_outputs.append(
            {
                "case_id": case_id,
                "coverage_state": review_case["coverage_state"],
                "addendum": addendum,
                "addendum_sha256": addendum_sha,
                "combined_manifest": manifest,
                "combined_manifest_sha256": manifest_sha,
                "views": views,
                "view_validations": validations,
                "probe_inputs": probe_inputs,
            }
        )

    return {
        "schema_version": PHASE2_REPORT_SCHEMA,
        "status": "provider_free_pass",
        "case_count": len(case_outputs),
        "view_count": sum(len(case["views"]) for case in case_outputs),
        "addendum_observation_count": sum(
            len(case["addendum"]["observations"]) for case in case_outputs
        ),
        "cases": case_outputs,
        "calls": {
            "provider": 0,
            "embedding": 0,
            "evaluator": 0,
            "graph": 0,
            "pipeline": 0,
            "runtime": 0,
        },
        "non_claims": [
            "provider_free_views_are_not_model_quality_evidence",
            "source_review_is_not_independent_gold",
            "coverage_is_not_reasoning_quality",
            "fan_in_compliance_is_not_reasoning_quality",
            "phase2_pass_is_not_graph_or_runtime_authority",
        ],
    }


def build_probe_input_packet(
    *,
    case_id: str,
    source_path: str,
    source_sha256: str,
    source_text: str,
    base_observations: Sequence[Mapping[str, Any]],
    view_kind: str,
) -> dict[str, Any]:
    """Build the target-blind packet a future bounded reader may receive.

    The authoritative conversation is never dropped or semantically pruned.
    The auxiliary Phase-1 ledger is included whole when it fits and omitted
    whole when it does not.  This avoids deterministic relevance selection and
    prevents protected-target or source-review-answer leakage.
    """

    if view_kind not in OBSERVATION_FAMILIES:
        raise ReasoningProcessViewError("probe input has invalid view kind")
    if sha256_bytes(source_text.encode("utf-8")) != source_sha256:
        raise ReasoningProcessViewError("probe input source hash mismatch")
    compact_observations = [
        {
            "observation_id": item["observation_id"],
            "family": item["family"],
            "interpretation": item["interpretation"],
            "semantic_status": item["semantic_status"],
            "source_span_ids": item["source_span_ids"],
        }
        for item in base_observations
    ]
    base = {
        "schema_version": PROBE_INPUT_SCHEMA,
        "status": "provider_free_target_blind_fixture",
        "case_id": case_id,
        "view_kind": view_kind,
        "question": _view_question(view_kind),
        "authoritative_conversation": {
            "source_path": source_path,
            "source_sha256": "sha256:" + source_sha256,
            "exact_text": source_text,
        },
        "auxiliary_phase1_ledger": {
            "policy": "include_whole_or_omit_whole_by_mechanical_byte_budget",
            "included": True,
            "observations": compact_observations,
        },
        "response_source_contract": {
            "speaker_turn_and_exact_quote_required": True,
            "stable_span_ids_attached_after_exact_deterministic_resolution": True,
            "unresolved_or_empty_output_allowed": True,
        },
        "boundary": {
            "protected_target_included": False,
            "source_review_addendum_included": False,
            "semantic_prefilter_performed": False,
            "authoritative_conversation_dropped": False,
            "final_output_evaluated": False,
            "direct_graph_routing_allowed": False,
        },
    }
    max_bytes = phase0_contract()["numeric_gates"]["max_view_input_utf8_bytes"]
    packet = base
    included_bytes = len(canonical_json_bytes(packet))
    auxiliary_omitted = False
    if included_bytes > max_bytes:
        packet = json.loads(json.dumps(base))
        packet["auxiliary_phase1_ledger"] = {
            "policy": "include_whole_or_omit_whole_by_mechanical_byte_budget",
            "included": False,
            "observations": [],
            "omission_reason": "complete auxiliary ledger would exceed the frozen input-byte ceiling; no semantic subset was selected",
        }
        auxiliary_omitted = True
    observed_bytes = len(canonical_json_bytes(packet))
    if observed_bytes > max_bytes:
        raise ReasoningProcessViewError(
            "authoritative conversation alone exceeds the frozen input-byte ceiling"
        )
    return {
        "packet": packet,
        "metrics": {
            "observed_input_utf8_bytes": observed_bytes,
            "max_input_utf8_bytes": max_bytes,
            "budget_exceeded": False,
            "source_message_count": build_source_catalog(
                source_text=source_text, source_path=source_path
            ).message_count,
            "auxiliary_observation_count_available": len(compact_observations),
            "auxiliary_observation_count_included": (
                0 if auxiliary_omitted else len(compact_observations)
            ),
            "auxiliary_ledger_omitted_whole": auxiliary_omitted,
        },
    }


def build_fan_in_stress_fixture(
    *, source_text: str, source_path: str, source_sha256: str
) -> dict[str, Any]:
    """Exercise the hard view ceiling on a real 24-message source.

    This is a representation and budget stress only.  It deliberately makes
    no semantic-quality claim about the selected source sentences.
    """

    if sha256_bytes(source_text.encode("utf-8")) != source_sha256:
        raise ReasoningProcessViewError("fan-in stress source hash mismatch")
    catalog = build_source_catalog(source_text=source_text, source_path=source_path)
    if catalog.message_count <= 14:
        raise ReasoningProcessViewError("fan-in stress source must exceed 14 messages")
    sentence_spans = [span for span in catalog.spans if span.kind == "sentence"][:32]
    if len(sentence_spans) != 32:
        raise ReasoningProcessViewError("fan-in stress source requires 32 sentence spans")
    observations = [
        {
            "observation_id": f"phase2-stress-observation-{index:03d}",
            "family": OBSERVATION_FAMILIES[(index - 1) % len(OBSERVATION_FAMILIES)],
            "interpretation": span.text,
            "semantic_status": "unclear",
            "source_span_ids": [span.span_id],
        }
        for index, span in enumerate(sentence_spans, start=1)
    ]
    input_bytes = len(canonical_json_bytes({"observations": observations}))
    hard_gates = phase0_contract()["numeric_gates"]
    first = observations[0]
    item_id = "phase2-stress-view-item-001"
    source_manifest = {
        "source_path": source_path,
        "source_sha256": "sha256:" + source_sha256,
        "message_count": catalog.message_count,
        "observation_ids": [item["observation_id"] for item in observations],
    }
    source_manifest_sha = sha256_bytes(canonical_json_bytes(source_manifest))
    view = {
        "schema_version": BOUNDED_VIEW_SCHEMA_VERSION,
        "status": VIEW_STATUS,
        "view_id": "phase2-fan-in-stress-view",
        "view_kind": "uncertainty_and_unresolved_state",
        "question": "Can the bounded-view representation retain exact custody at the Phase-0 observation ceiling on a conversation longer than fourteen messages?",
        "source_ledger_sha256": "sha256:" + source_manifest_sha,
        "input": {"ledger_observation_ids": [item["observation_id"] for item in observations]},
        "items": [
            {
                "view_item_id": item_id,
                "interpretation": first["interpretation"],
                "status": "unclear",
                "source_observation_ids": [first["observation_id"]],
                "source_span_ids": first["source_span_ids"],
                "limitations": "Fan-in and custody stress only; semantic selection and reasoning quality are not evaluated.",
            }
        ],
        "dispositions": [
            {
                "observation_id": item["observation_id"],
                "disposition": "included" if index == 0 else "parked_unclear",
                "authority": "source_reviewer",
                "reason": (
                    "One item is retained solely to exercise valid view lineage."
                    if index == 0
                    else "Parked because this fixture tests fan-in accounting, not semantic applicability."
                ),
                "view_item_ids": [item_id] if index == 0 else [],
            }
            for index, item in enumerate(observations)
        ],
        "budget": {
            "max_input_observations": hard_gates["max_view_input_observations"],
            "max_input_utf8_bytes": hard_gates["max_view_input_utf8_bytes"],
            "max_output_items": hard_gates["max_view_output_items"],
            "observed_input_observations": len(observations),
            "observed_input_utf8_bytes": input_bytes,
            "observed_output_items": 1,
            "budget_exceeded": (
                len(observations) > hard_gates["max_view_input_observations"]
                or input_bytes > hard_gates["max_view_input_utf8_bytes"]
            ),
        },
        "boundary": {
            "authoritative_source": False,
            "semantic_selection_performed_by_code": False,
            "omissions_recoverable_from_ledger": True,
            "final_output_evaluated": False,
            "quality_score_included": False,
            "direct_graph_routing_allowed": False,
        },
    }
    validation = validate_bounded_view(
        view,
        known_ledger_observation_ids=[item["observation_id"] for item in observations],
        known_span_ids=catalog.by_id(),
        expected_ledger_sha256="sha256:" + source_manifest_sha,
    )
    probe_input = build_probe_input_packet(
        case_id="phase2-fan-in-stress",
        source_path=source_path,
        source_sha256=source_sha256,
        source_text=source_text,
        base_observations=observations,
        view_kind="uncertainty_and_unresolved_state",
    )
    return {
        "schema_version": FAN_IN_STRESS_SCHEMA,
        "status": "provider_free_representation_pass",
        "source_manifest": source_manifest,
        "observations": observations,
        "view": view,
        "validation": validation,
        "probe_input": probe_input,
        "boundary": {
            "semantic_quality_evaluated": False,
            "final_output_evaluated": False,
            "provider_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "runtime_calls": 0,
        },
    }


def _source_review_observation(
    *, observation_id: str, target: Mapping[str, Any], span_ids: Sequence[str], reason: str
) -> dict[str, Any]:
    raw_record = {
        "target_id": target["target_id"],
        "view_kind": target["view_kind"],
        "description": target["description"],
        "source_evidence": target["source_evidence"],
        "review_reason": reason,
    }
    return {
        "observation_id": observation_id,
        "family": target["view_kind"],
        "family_projection_status": "prospective_source_review_not_deterministic_projection",
        "interpretation": target["description"],
        "semantic_status": "supported",
        "source_span_ids": list(span_ids),
        "source_artifact_id": "phase2-coverage-source-review",
        "source_record_id": target["target_id"],
        "source_family": "protected_target_review",
        "raw_record_sha256": "sha256:" + sha256_bytes(canonical_json_bytes(raw_record)),
        "raw_record": raw_record,
        "provenance": {
            "producer_kind": "source_reviewer",
            "producer_id": "phase2-same-session-nonblind-review",
            "call_id": "",
            "model": "",
            "prompt_sha256": "",
        },
        "state_history": [
            {
                "state": "proposed",
                "reason": "prospectively frozen protected target required source-review coverage",
                "actor": "source_reviewer",
            },
            {
                "state": "admitted",
                "reason": "exact source custody and prospective review decision validated",
                "actor": "deterministic_validator",
            },
        ],
        "terminal_state": "admitted",
        "terminal_reason": "append-only source-review observation with exact source lineage",
        "relations": [],
        "graph_routing_eligible": False,
    }


def _view_question(view_kind: str) -> str:
    questions = {
        "position_and_decision_trajectory": "How did the working position or decision change, and what qualifications remain?",
        "exploration_and_alternatives": "Which concrete alternative was explored, and what limited it?",
        "evidence_and_assumption_discipline": "How was evidence bounded rather than promoted into a stronger claim?",
        "uncertainty_and_unresolved_state": "What material uncertainty remained unresolved or capable of reopening the decision?",
        "challenge_and_revision_response": "What challenge was raised, and how did the subsequent reasoning respond or revise?",
    }
    return questions[view_kind]


def _validate_contract_shape(contract: Mapping[str, Any]) -> None:
    if contract.get("schema_version") != COVERAGE_CONTRACT_SCHEMA:
        raise ReasoningProcessViewError("invalid Phase-2 coverage contract schema")
    if contract.get("review_boundary", {}).get("semantic_coverage_is_inferred_by_code") is not False:
        raise ReasoningProcessViewError("contract must prohibit deterministic semantic coverage")
    cases = contract.get("cases")
    if not isinstance(cases, list) or len(cases) != 5:
        raise ReasoningProcessViewError("coverage contract requires five cases")
    case_ids: list[str] = []
    target_ids: list[str] = []
    view_counts: Counter[str] = Counter()
    for case in cases:
        case_ids.append(case.get("case_id", ""))
        for field in (
            "source_path",
            "source_sha256",
            "phase1_ledger_path",
            "phase1_ledger_sha256",
        ):
            if not isinstance(case.get(field), str) or not case[field]:
                raise ReasoningProcessViewError(f"case {case.get('case_id')} lacks {field}")
        targets = case.get("targets")
        if not isinstance(targets, list) or len(targets) != len(OBSERVATION_FAMILIES):
            raise ReasoningProcessViewError("each case requires one target per view kind")
        for target in targets:
            target_ids.append(target.get("target_id", ""))
            view_kind = target.get("view_kind")
            if view_kind not in OBSERVATION_FAMILIES:
                raise ReasoningProcessViewError("target has invalid view kind")
            view_counts[view_kind] += 1
            evidence = target.get("source_evidence")
            if not isinstance(evidence, list) or not evidence:
                raise ReasoningProcessViewError("target requires source evidence")
    if len(case_ids) != len(set(case_ids)) or len(target_ids) != len(set(target_ids)):
        raise ReasoningProcessViewError("case and target IDs must be unique")
    if set(view_counts) != set(OBSERVATION_FAMILIES) or set(view_counts.values()) != {5}:
        raise ReasoningProcessViewError("view targets must be balanced across five cases")


def _validate_review(
    *, contract: Mapping[str, Any], candidates: Mapping[str, Any], review: Mapping[str, Any]
) -> None:
    if review.get("schema_version") != COVERAGE_REVIEW_SCHEMA:
        raise ReasoningProcessViewError("invalid coverage-review schema")
    expected_contract_sha = sha256_bytes(canonical_json_bytes(contract))
    if review.get("coverage_contract_sha256") != expected_contract_sha:
        raise ReasoningProcessViewError("coverage-review contract hash mismatch")
    expected_candidates_sha = sha256_bytes(canonical_json_bytes(candidates))
    if review.get("coverage_candidates_sha256") != expected_candidates_sha:
        raise ReasoningProcessViewError("coverage-review candidates hash mismatch")
    if review.get("reviewer_independence") != "same_project_session_not_blind":
        raise ReasoningProcessViewError("review must disclose non-independent status")
    contract_cases = {case["case_id"]: case for case in contract["cases"]}
    candidate_cases = {case["case_id"]: case for case in candidates["cases"]}
    review_cases = review.get("cases")
    if not isinstance(review_cases, list) or {case.get("case_id") for case in review_cases} != set(contract_cases):
        raise ReasoningProcessViewError("review cases do not match coverage contract")
    for review_case in review_cases:
        case_id = review_case["case_id"]
        if review_case.get("coverage_state") not in _COVERAGE_STATES:
            raise ReasoningProcessViewError("invalid case coverage state")
        contract_targets = {item["target_id"]: item for item in contract_cases[case_id]["targets"]}
        candidate_targets = {item["target_id"]: item for item in candidate_cases[case_id]["targets"]}
        decisions = review_case.get("targets")
        if not isinstance(decisions, list) or {item.get("target_id") for item in decisions} != set(contract_targets):
            raise ReasoningProcessViewError("review targets do not match contract")
        for decision in decisions:
            if decision.get("decision") not in _REVIEW_DECISIONS:
                raise ReasoningProcessViewError("invalid coverage decision")
            if decision.get("semantic_status") not in {"supported", "mixed", "unclear"}:
                raise ReasoningProcessViewError("invalid reviewed semantic status")
            if not isinstance(decision.get("reason"), str) or not decision["reason"]:
                raise ReasoningProcessViewError("review decision requires a reason")
            phase1_ids = decision.get("phase1_observation_ids")
            if not isinstance(phase1_ids, list):
                raise ReasoningProcessViewError("phase1_observation_ids must be an array")
            allowed_ids = {
                item["observation_id"]
                for item in candidate_targets[decision["target_id"]]["mechanical_overlap_observations"]
            }
            if not set(phase1_ids).issubset(allowed_ids):
                raise ReasoningProcessViewError("review cites a non-overlapping Phase-1 observation")
            if decision["decision"] == "covered_by_phase1" and not phase1_ids:
                raise ReasoningProcessViewError("Phase-1 coverage requires cited observations")
            if decision["decision"] != "covered_by_phase1" and phase1_ids:
                raise ReasoningProcessViewError("non-coverage decision cannot claim Phase-1 coverage")


def _require_file_hash(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise ReasoningProcessViewError(f"{label} is missing: {path}")
    actual = sha256_file(path)
    if actual != expected.removeprefix("sha256:"):
        raise ReasoningProcessViewError(f"{label} hash mismatch: {path}")
