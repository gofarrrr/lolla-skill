"""Read-only Product Delta specialist packet construction.

This module packetizes existing Product Delta eval artifacts for future
specialist review. It reads only checked-in safe JSON inputs, emits source-aware
input scaffolds, and does not run Lolla, call models, mutate archives, read raw
transcripts, score answer quality, create labels, or fill specialist reads.
"""
from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PRODUCT_DELTA_SPECIALIST_PACKETS_SCHEMA_VERSION = (
    "lolla.product_delta_specialist_packets.v0"
)
SPECIALIST_CONTRACT_SCHEMA_VERSION = (
    "lolla.product_delta_specialist_review_contracts.v0"
)
DEFAULT_CONTRACT_SCHEMA_RELPATH = (
    "docs/evals/product-delta-specialist-review-contracts-v0.json"
)
DEFAULT_CONTRACT_DOC_RELPATH = (
    "docs/evals/product-delta-specialist-review-contracts-v0.md"
)

INPUT_MODES = ("checked_in_safe_mode", "local_private_mode")
SPECIALIST_ROLES = (
    "conversation_interpretation",
    "vanilla_likely_next_action",
    "lolla_likely_next_action",
    "structural_delta",
    "friction_lost_value",
    "interpretation_adequacy",
    "advisory_overclaim",
    "conservative_fan_in",
)

BOUNDARY = {
    "human_validated": False,
    "ground_truth": False,
    "judge_calibration_eligible": False,
    "product_proof": False,
    "answer_quality_scored": False,
    "agent_action_authorized": False,
    "model_calls": 0,
    "archive_mutated": False,
    "runtime_invoked": False,
    "skill_invoked": False,
    "raw_private_content_included": False,
    "automatic_labels_created": False,
}

NON_CLAIMS = (
    "not human review",
    "not ground truth",
    "not judge calibration data",
    "not product proof",
    "not agent approval",
    "not answer-quality scoring",
    "not automatic labeling",
    "not runtime integration",
)

FORBIDDEN_OUTPUTS = (
    "human-validation claim",
    "ground-truth claim",
    "judge-calibration claim",
    "product-proof claim",
    "answer-quality measurement",
    "agent-action authorization",
    "automatic label creation",
    "runtime integration claim",
    "filled specialist conclusion inside the packet",
)


class ProductDeltaSpecialistPacketInputError(ValueError):
    """Deterministic, sanitized input error."""


def load_json_object(path: Path | str) -> dict[str, Any]:
    input_path = Path(path)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProductDeltaSpecialistPacketInputError("input JSON is not valid JSON") from exc
    except OSError as exc:
        raise ProductDeltaSpecialistPacketInputError(
            f"input JSON could not be read:{type(exc).__name__}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaSpecialistPacketInputError("input JSON is not an object")
    return payload


def build_product_delta_specialist_packets(
    *,
    seed_cases: Mapping[str, Any],
    provisional_review: Mapping[str, Any],
    codex_batch: Mapping[str, Any],
    case_list_relpath: str,
    provisional_review_relpath: str,
    codex_batch_relpath: str,
    mode: str = "checked_in_safe_mode",
    limit: int | None = None,
    case_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Build checked-in safe specialist input packets.

    The output is packet scaffolding only. It contains task questions, safe
    source references, known limits, and PR80 contract references. It does not
    fill any specialist read fields.
    """

    if mode not in INPUT_MODES:
        raise ProductDeltaSpecialistPacketInputError("unsupported input mode")
    if mode != "checked_in_safe_mode":
        raise ProductDeltaSpecialistPacketInputError(
            "local_private_mode is documented but deferred for PR81"
        )
    if limit is not None and limit < 1:
        raise ProductDeltaSpecialistPacketInputError("limit must be positive")

    selected_case_ids = {case_id for case_id in (case_ids or []) if case_id}
    seed_records = []
    for seed_index, raw_case in enumerate(_case_items(seed_cases.get("cases"))):
        normalized = _normalize_seed_case(raw_case)
        normalized["_seed_index"] = seed_index
        seed_records.append(normalized)
    if selected_case_ids:
        seed_records = [
            case for case in seed_records if case["case_id"] in selected_case_ids
        ]
    if limit is not None:
        seed_records = seed_records[:limit]

    readiness_index = _index_cases(
        provisional_review.get("cases"),
        path=provisional_review_relpath,
    )
    batch_index = _index_cases(
        codex_batch.get("cases"),
        path=codex_batch_relpath,
    )

    cases: list[dict[str, Any]] = []
    for case in seed_records:
        readiness_ref = readiness_index.get(case["archive_relpath"])
        if readiness_ref is None:
            readiness_ref = readiness_index.get(case["case_id"])
        batch_ref = batch_index.get(case["archive_relpath"])
        if batch_ref is None:
            batch_ref = batch_index.get(case["case_id"])
        cases.append(
            _build_case_packet_bundle(
                case=case,
                seed_index=_safe_int(case.get("_seed_index")),
                seed_path=case_list_relpath,
                readiness_ref=readiness_ref,
                batch_ref=batch_ref,
                mode=mode,
            )
        )

    return {
        "schema_version": PRODUCT_DELTA_SPECIALIST_PACKETS_SCHEMA_VERSION,
        "generated_by": "product_delta_specialist_packets",
        "mode": mode,
        "input_refs": {
            "case_list": case_list_relpath,
            "provisional_review": provisional_review_relpath,
            "codex_batch": codex_batch_relpath,
            "contract_schema": DEFAULT_CONTRACT_SCHEMA_RELPATH,
            "contract_doc": DEFAULT_CONTRACT_DOC_RELPATH,
        },
        "boundary": dict(BOUNDARY),
        "packet_policy": {
            "packet_type": "input_scaffold_only",
            "specialist_reads_filled": False,
            "checked_in_safe_mode_only": True,
            "raw_transcripts_included": False,
            "raw_revised_answers_included": False,
            "raw_memos_included": False,
            "provider_private_text_included": False,
            "local_absolute_paths_included": False,
            "prior_broad_read_policy": (
                "Prior PR76 broad reads may be referenced as source context, "
                "but PR81 does not copy their semantic conclusions into packet "
                "answers or treat them as truth."
            ),
        },
        "case_count": len(cases),
        "cases": cases,
        "non_claims": list(NON_CLAIMS),
    }


def render_product_delta_specialist_packets_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_text(path: Path | str, payload: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(payload, encoding="utf-8")


def _build_case_packet_bundle(
    *,
    case: Mapping[str, Any],
    seed_index: int,
    seed_path: str,
    readiness_ref: Mapping[str, Any] | None,
    batch_ref: Mapping[str, Any] | None,
    mode: str,
) -> dict[str, Any]:
    readiness_case = _mapping(readiness_ref.get("case")) if readiness_ref else {}
    batch_case = _mapping(batch_ref.get("case")) if batch_ref else {}
    readiness_status = _text(readiness_case.get("readiness_state")) or "not_supplied"
    source_refs = _case_source_refs(
        case=case,
        seed_index=seed_index,
        seed_path=seed_path,
        readiness_ref=readiness_ref,
        batch_ref=batch_ref,
    )
    missing_or_thin = _missing_or_thin_context(
        readiness_case=readiness_case,
        batch_ref=batch_ref,
    )
    available_context = _available_context(
        case=case,
        readiness_case=readiness_case,
        batch_ref=batch_ref,
        readiness_status=readiness_status,
    )
    packets = {
        role: _build_specialist_packet(
            role=role,
            case=case,
            mode=mode,
            readiness_status=readiness_status,
            source_refs=source_refs,
            available_context=available_context,
            missing_or_thin_context=missing_or_thin,
            batch_available=batch_ref is not None,
        )
        for role in SPECIALIST_ROLES
    }
    return {
        "case_id": case["case_id"],
        "run_id": case["run_id"],
        "archive_relpath": case["archive_relpath"],
        "readiness_status": readiness_status,
        "source_refs": source_refs,
        "available_context": available_context,
        "missing_or_thin_context": missing_or_thin,
        "packets": packets,
        "packetization_notes": [
            "PR81 prepared input packets only.",
            "Specialist reads remain unfilled until a later provisional review slice.",
        ],
    }


def _build_specialist_packet(
    *,
    role: str,
    case: Mapping[str, Any],
    mode: str,
    readiness_status: str,
    source_refs: Sequence[Mapping[str, Any]],
    available_context: Mapping[str, Any],
    missing_or_thin_context: Sequence[str],
    batch_available: bool,
) -> dict[str, Any]:
    role_spec = ROLE_SPECS[role]
    return {
        "specialist_role": role,
        "contract_ref": {
            "schema_ref": (
                f"{DEFAULT_CONTRACT_SCHEMA_RELPATH}#/$defs/"
                f"{role_spec['contract_def']}"
            ),
            "contract_schema_version": SPECIALIST_CONTRACT_SCHEMA_VERSION,
            "doc_ref": role_spec["doc_ref"],
        },
        "mode": mode,
        "allowed_inputs": _allowed_inputs(
            role=role,
            source_refs=source_refs,
            batch_available=batch_available,
        ),
        "forbidden_outputs": list(FORBIDDEN_OUTPUTS),
        "review_questions": list(role_spec["review_questions"]),
        "source_refs": list(source_refs),
        "context": {
            "case_id": case["case_id"],
            "archive_relpath": case["archive_relpath"],
            "readiness_status": readiness_status,
            "safe_context_available": bool(
                _text(available_context.get("review_safe_summary_status"))
                == "available"
            ),
            "prior_provisional_broad_read_available": batch_available,
            "prior_provisional_broad_read_use": (
                "source context only; not a specialist answer and not truth"
            ),
        },
        "known_limits": _packet_known_limits(
            role=role,
            missing_or_thin_context=missing_or_thin_context,
            batch_available=batch_available,
        ),
        "required_non_claims": list(NON_CLAIMS),
        "expected_output_contract": {
            "schema_ref": (
                f"{DEFAULT_CONTRACT_SCHEMA_RELPATH}#/$defs/"
                f"{role_spec['contract_def']}"
            ),
            "required_field_names": list(role_spec["expected_fields"]),
            "filled_by_packet_builder": False,
            "must_be_filled_by_future_specialist": True,
            "candidate_only": True,
        },
    }


def _allowed_inputs(
    *,
    role: str,
    source_refs: Sequence[Mapping[str, Any]],
    batch_available: bool,
) -> list[dict[str, Any]]:
    allowed = [
        {
            "artifact_ref": ref["artifact_ref"],
            "content_policy": ref["content_policy"],
        }
        for ref in source_refs
    ]
    if batch_available:
        allowed.append(
            {
                "artifact_ref": "reviews/codex-assisted/product-delta-batch-v0/review.json",
                "content_policy": (
                    "May be inspected as prior broad provisional context only; "
                    "do not copy its conclusions as the specialist read."
                ),
            }
        )
    allowed.append(
        {
            "artifact_ref": DEFAULT_CONTRACT_SCHEMA_RELPATH,
            "content_policy": f"Use only the PR80 contract for `{role}` output shape.",
        }
    )
    return _dedupe_dicts(allowed)


def _case_source_refs(
    *,
    case: Mapping[str, Any],
    seed_index: int,
    seed_path: str,
    readiness_ref: Mapping[str, Any] | None,
    batch_ref: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    refs = [
        {
            "artifact_ref": f"{seed_path}#/cases/{seed_index}",
            "source_status": "explicit",
            "content_policy": "case identity and review-safe source metadata",
        },
    ]
    if readiness_ref:
        refs.append(
            {
                "artifact_ref": f"{readiness_ref['path']}#/cases/{readiness_ref['index']}",
                "source_status": "explicit",
                "content_policy": (
                    "readiness status, artifact presence metadata, structured "
                    "signals, and review-safe context only"
                ),
            }
        )
    else:
        refs.append(
            {
                "artifact_ref": "missing:provisional_review_case",
                "source_status": "unavailable_missing_artifact",
                "content_policy": "readiness record unavailable",
            }
        )
    if batch_ref:
        refs.append(
            {
                "artifact_ref": f"{batch_ref['path']}#/cases/{batch_ref['index']}",
                "source_status": "explicit",
                "content_policy": (
                    "prior broad provisional context only; not ground truth and "
                    "not a specialist answer"
                ),
            }
        )
    else:
        refs.append(
            {
                "artifact_ref": "missing:codex_batch_case",
                "source_status": "unavailable_missing_artifact",
                "content_policy": "prior broad provisional context unavailable",
            }
        )
    refs.append(
        {
            "artifact_ref": DEFAULT_CONTRACT_SCHEMA_RELPATH,
            "source_status": "explicit",
            "content_policy": "PR80 output contract definitions",
        }
    )
    return refs


def _available_context(
    *,
    case: Mapping[str, Any],
    readiness_case: Mapping[str, Any],
    batch_ref: Mapping[str, Any] | None,
    readiness_status: str,
) -> dict[str, Any]:
    return {
        "vanilla_baseline_status": case["vanilla_baseline_status"],
        "review_safe_summary_status": case["review_safe_summary_status"],
        "review_safe_sources": list(case["review_safe_sources"]),
        "readiness_status": readiness_status,
        "ready_for_codex_provisional_review": (
            readiness_status == "ready_for_codex_provisional_review"
        ),
        "artifact_presence_summary": _artifact_presence_summary(
            readiness_case.get("artifact_presence")
        ),
        "structured_signals": _structured_signals(
            readiness_case.get("structured_signals")
        ),
        "review_safe_context": _safe_review_context(
            readiness_case.get("review_safe_context")
        ),
        "prior_provisional_broad_read_context": {
            "available": batch_ref is not None,
            "artifact_ref": (
                f"{batch_ref['path']}#/cases/{batch_ref['index']}"
                if batch_ref
                else ""
            ),
            "authority": "prior_codex_assisted_broad_read_only",
            "semantic_values_copied_into_packets": False,
            "use_policy": (
                "A future specialist may inspect the source artifact, but PR81 "
                "does not treat prior broad reads as truth or fill specialist "
                "answers from them."
            ),
        },
    }


def _missing_or_thin_context(
    *,
    readiness_case: Mapping[str, Any],
    batch_ref: Mapping[str, Any] | None,
) -> list[str]:
    notes: list[str] = []
    readiness_status = _text(readiness_case.get("readiness_state"))
    if not readiness_status:
        notes.append("readiness_record_missing")
    elif readiness_status != "ready_for_codex_provisional_review":
        notes.append(f"readiness_status:{readiness_status}")
    notes.extend(f"blocking:{item}" for item in _strings(readiness_case.get("blocking_reasons")))
    notes.extend(f"weakening:{item}" for item in _strings(readiness_case.get("weakening_reasons")))
    if batch_ref is None:
        notes.append("prior_provisional_broad_read_missing")
    if not notes:
        notes.append("safe_context_available_with_provisional_caveats")
    return notes


def _packet_known_limits(
    *,
    role: str,
    missing_or_thin_context: Sequence[str],
    batch_available: bool,
) -> list[str]:
    limits = [
        "checked-in packet excludes raw transcript, raw revised answer, raw memo, provider text, and private reasoning",
        "packet builder does not infer likely actions, deltas, friction, lost value, interpretation adequacy, or net read",
    ]
    limits.extend(missing_or_thin_context)
    if not batch_available and role in {
        "structural_delta",
        "friction_lost_value",
        "conservative_fan_in",
    }:
        limits.append("prior broad Product Delta context unavailable for this role")
    return list(dict.fromkeys(limits))


def _artifact_presence_summary(value: Any) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for item in _case_items(value):
        summary.append(
            {
                "artifact": _text(item.get("artifact")),
                "status": _text(item.get("status")) or "not_supplied",
                "schema_version": _text(item.get("schema_version")) or None,
                "raw_content_read": bool(item.get("raw_content_read")),
            }
        )
    return summary


def _structured_signals(value: Any) -> dict[str, Any]:
    signals = _mapping(value)
    allowed = (
        "evaluation_overall",
        "caller_readiness",
        "agent_caller_action",
        "reasoning_trace_schema_version",
        "extraction_adequacy_status",
    )
    return {key: signals.get(key) for key in allowed if key in signals}


def _safe_review_context(value: Any) -> dict[str, Any]:
    context = _mapping(value)
    allowed = (
        "review_safe_summary_available",
        "review_safe_sources",
        "prior_review_record_found",
        "prior_review_authority",
        "review_readiness_tier",
        "artifact_sufficiency",
        "review_status",
        "actionable_delta_label_count",
    )
    return {key: context.get(key) for key in allowed if key in context}


def _index_cases(value: Any, *, path: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for case_index, case in enumerate(_case_items(value)):
        ref = {
            "case": case,
            "index": case_index,
            "path": path,
        }
        archive_relpath = _text(case.get("archive_relpath") or case.get("case_relpath"))
        case_id = _text(case.get("case_id"))
        if archive_relpath:
            index[archive_relpath] = ref
        if case_id and case_id not in index:
            index[case_id] = ref
    return index


def _normalize_seed_case(raw_case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = _text(raw_case.get("case_id"))
    run_id = _text(raw_case.get("run_id"))
    archive_relpath = _text(raw_case.get("archive_relpath")) or f"{case_id}/{run_id}"
    if not case_id:
        raise ProductDeltaSpecialistPacketInputError("case entry is missing case_id")
    if not run_id:
        raise ProductDeltaSpecialistPacketInputError("case entry is missing run_id")
    if archive_relpath.startswith("/") or ".." in archive_relpath.split("/"):
        raise ProductDeltaSpecialistPacketInputError("case entry has unsafe archive_relpath")
    return {
        "case_id": case_id,
        "run_id": run_id,
        "archive_relpath": archive_relpath,
        "vanilla_baseline_status": _text(raw_case.get("vanilla_baseline_status")),
        "review_safe_summary_status": _text(raw_case.get("review_safe_summary_status")),
        "review_safe_sources": _strings(raw_case.get("review_safe_sources")),
    }


def _case_items(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    return 0


def _dedupe_dicts(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = json.dumps(item, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(item))
    return result


ROLE_SPECS: dict[str, dict[str, Any]] = {
    "conversation_interpretation": {
        "contract_def": "conversation_interpretation_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#conversation-interpretation",
        "review_questions": (
            "What is the decision question visible from review-safe sources?",
            "What options, constraints, stakeholders, values, assistant influence, and dropped threads should a future reviewer check?",
            "What would make this interpretation wrong?",
        ),
        "expected_fields": (
            "read_status",
            "decision_question",
            "live_options",
            "option_status",
            "constraints",
            "stakeholders",
            "values_or_priorities",
            "assistant_influence",
            "dropped_threads",
            "unresolved_questions",
            "uncertainty_notes",
            "source_refs",
            "field_status",
            "what_would_make_this_wrong",
        ),
    },
    "vanilla_likely_next_action": {
        "contract_def": "vanilla_likely_next_action_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#vanilla-likely-next-action",
        "review_questions": (
            "What action would the vanilla conversation or final answer likely have led the user toward?",
            "Which parts are explicit, inferred, unclear, contradicted, or not supplied?",
            "What alternative plausible actions remain?",
        ),
        "expected_fields": (
            "read_status",
            "likely_next_action",
            "action_source_status",
            "explicit_or_inferred",
            "uncertainty_notes",
            "source_refs",
            "alternative_plausible_actions",
            "what_would_make_this_wrong",
        ),
    },
    "lolla_likely_next_action": {
        "contract_def": "lolla_likely_next_action_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#lolla-likely-next-action",
        "review_questions": (
            "What action would the Lolla revised answer likely lead the user toward?",
            "Which parts are explicit, inferred, unclear, contradicted, or not supplied?",
            "What alternative plausible actions remain after the revised answer?",
        ),
        "expected_fields": (
            "read_status",
            "likely_next_action",
            "action_source_status",
            "explicit_or_inferred",
            "uncertainty_notes",
            "source_refs",
            "alternative_plausible_actions",
            "what_would_make_this_wrong",
        ),
    },
    "structural_delta": {
        "contract_def": "structural_delta_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#structural-delta",
        "review_questions": (
            "Did the future specialist find a change in action, threshold, sequence, evidence gate, stop rule, scope, stakeholder treatment, user-answerable question, overclaim handling, or reversibility?",
            "Which source refs support or weaken each candidate change?",
            "What uncertainty should be carried forward?",
        ),
        "expected_fields": (
            "read_status",
            "action_changed",
            "threshold_changed",
            "sequence_changed",
            "evidence_gate_added_or_changed",
            "stop_rule_added_or_changed",
            "scope_changed",
            "stakeholder_treatment_changed",
            "user_answerable_question_added",
            "overclaim_retracted",
            "reversibility_or_bounding_changed",
        ),
    },
    "friction_lost_value": {
        "contract_def": "friction_lost_value_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#usefulnoisy-friction-and-lost-value",
        "review_questions": (
            "Was any added friction grounded, actionable, and proportionate?",
            "Where might the revised answer add process, caution, or hesitation without decision leverage?",
            "What useful original value, momentum, clarity, simplicity, courage, or user-specific ambition might be weaker?",
        ),
        "expected_fields": (
            "read_status",
            "useful_friction",
            "noisy_friction",
            "lost_value",
            "overcorrection_risk",
            "momentum_or_simplicity_loss",
            "generic_prudence_substitution",
            "decision_burden_added",
            "uncertainty_notes",
            "source_refs",
            "what_would_make_this_wrong",
        ),
    },
    "interpretation_adequacy": {
        "contract_def": "interpretation_adequacy_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#interpretation-adequacy",
        "review_questions": (
            "Did Lolla appear to preserve the decision question, options, constraints, stakeholders, values, assistant influence, dropped threads, grounding, uncertainty, and risk mode?",
            "Which interpretation failure modes should a future reviewer inspect?",
            "Would better interpretation plausibly change the later answer?",
        ),
        "expected_fields": (
            "read_status",
            "decision_question_drift",
            "option_loss",
            "constraint_flattening",
            "stakeholder_erasure",
            "value_overwrite",
            "transient_emotion_hardening",
            "assistant_influence_blindness",
            "false_consensus",
            "dropped_thread_blindness",
            "quote_or_grounding_misread",
            "uncertainty_collapse",
            "risk_mode_mismatch",
            "overall_interpretation_adequacy",
        ),
    },
    "advisory_overclaim": {
        "contract_def": "advisory_overclaim_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#advisory-overclaim",
        "review_questions": (
            "Does any artifact language sound more certain than the metadata supports?",
            "Which non-claims should be made clearer before a future review packet is trusted?",
            "What should PR78 lint enforce deterministically instead of leaving to advisory prose?",
        ),
        "expected_fields": (
            "read_status",
            "overclaim_risks",
            "language_to_soften",
            "missing_non_claims",
            "advisory_only",
            "requires_pr78_lint",
        ),
    },
    "conservative_fan_in": {
        "contract_def": "conservative_fan_in_read",
        "doc_ref": f"{DEFAULT_CONTRACT_DOC_RELPATH}#conservative-fan-in",
        "review_questions": (
            "What can be synthesized while preserving specialist disagreement, uncertainty, missingness, and non-claims?",
            "Which fields should be downgraded or sent to human review first?",
            "What would change the candidate read?",
        ),
        "expected_fields": (
            "read_status",
            "specialist_agreements",
            "specialist_disagreements",
            "downgraded_fields",
            "high_uncertainty_fields",
            "human_review_priorities",
            "net_decision_read_candidate",
            "why_not_stronger",
            "what_would_change_this_read",
            "non_claims",
        ),
    },
}
