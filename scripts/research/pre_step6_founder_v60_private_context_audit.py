#!/usr/bin/env python3
"""Research-only audit of Founder V60 private context.

This slice exits the pre-Step-6 portfolio perimeter and inspects the V60
private context that plausibly destabilized the Founder case. It characterizes
evidence shape only: code does not decide the correct Founder answer, does not
resolve Consultant or PhD variance, and does not add a runtime gate.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_calibration_corpus import (
    load_step6_calibration_sample,
    validate_step6_calibration_sample,
)
from pre_step6_founder_v60_symmetry_check import (
    load_founder_v60_symmetry_result,
    validate_founder_v60_symmetry_result,
)


CONTRACT_SCHEMA_VERSION = "pre_step6_founder_v60_private_context_audit_contract.v1"
RESULT_SCHEMA_VERSION = "pre_step6_founder_v60_private_context_audit_result.v1"
RUNTIME_POLICY = "runtime_dormant"
STATUS = "research_only"
EXPERIMENT_ID = "pre_step6_founder_v60_private_context_audit_v0"
PROGRAM_SCOPE = "v60_private_context_audit_not_pre_step6_portfolio"
DEFAULT_OUT_DIR = Path("research/pre-step6-founder-v60-private-context-audit")
DEFAULT_SYMMETRY_RESULT_REF = (
    "research/pre-step6-founder-v60-symmetry-check/founder-v60-symmetry-result.v1.json"
)
CASE_FAMILY = "founder-grant-marcus-equity.high-clutter"
FOUNDER_V60_ON = f"{CASE_FAMILY}.v60-on"
DEFAULT_SAMPLE_SETS = (
    {
        "model_family": "moonshotai",
        "model": "moonshotai/kimi-k2.6",
        "v60_mode": "on",
        "case_id": FOUNDER_V60_ON,
        "sample_dir": "research/pre-step6-calibration-corpus-kimi-structural-delta/step6-samples",
    },
    {
        "model_family": "moonshotai",
        "model": "moonshotai/kimi-k2.6",
        "v60_mode": "off",
        "case_id": f"{CASE_FAMILY}.v60-off",
        "sample_dir": "research/pre-step6-founder-v60-symmetry-kimi/step6-samples",
    },
    {
        "model_family": "openai",
        "model": "openai/gpt-5.1-chat",
        "v60_mode": "on",
        "case_id": FOUNDER_V60_ON,
        "sample_dir": "research/pre-step6-variable-case-alt-model-gpt51/step6-samples",
    },
    {
        "model_family": "openai",
        "model": "openai/gpt-5.1-chat",
        "v60_mode": "off",
        "case_id": f"{CASE_FAMILY}.v60-off",
        "sample_dir": "research/pre-step6-founder-v60-symmetry-gpt51/step6-samples",
    },
)
PRECOMMITTED_OUTCOME_KEYS = (
    "genuine_edge_pressure_structurally_borderline",
    "selection_noise",
    "joint_overload",
    "cross_chunk_consideration_gap",
)
QUEUED_FOLLOWUPS = (
    "consultant_case_ambiguity_design_review_v0",
    "kimi_phd_variance_diagnostic_v0",
)
EXPLICIT_LIMITS = (
    "does_not_decide_founder_answer_correctness",
    "does_not_resolve_consultant",
    "does_not_resolve_phd",
    "does_not_promote_runtime_or_skill",
)
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "program_scope",
        "case_family",
        "source_refs",
        "sample_sets",
        "precommitted_outcomes",
        "queued_followups",
        "explicit_limits",
        "gates",
        "notes",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "program_scope",
        "case_family",
        "source_refs",
        "v60_private_context",
        "context_relevance",
        "mode_comparison",
        "outcome_evidence",
        "aggregate",
        "gates",
        "notes",
    }
)
SOURCE_REF_FIELDS = frozenset(
    {
        "source_symmetry_result_ref",
        "ledger_overlap_ref",
        "problem_state_ref",
        "anchor_ref",
        "deck_ref",
    }
)
SAMPLE_SET_FIELDS = frozenset({"model_family", "model", "v60_mode", "case_id", "sample_dir"})
CONTEXT_FIELDS = frozenset(
    {
        "raw_text",
        "chunk_ids",
        "chunk_count",
        "source_ref",
        "source_note",
        "present_in_v60_on_samples",
        "present_in_v60_off_samples",
    }
)
RELEVANCE_FIELDS = frozenset(
    {
        "case_surface_terms",
        "v60_terms",
        "overlap_terms",
        "overlap_count",
        "relevance_read",
    }
)
MODE_ROW_FIELDS = frozenset(
    {
        "model_family",
        "model",
        "v60_mode",
        "case_id",
        "sample_count",
        "unlock_count",
        "visibility_classification",
        "answer_token_jaccard_min",
        "ledger_signal_counts",
        "answer_delta_specificity_counts",
        "deck_visible_effects",
        "deck_answer_delta_summary",
    }
)
EVIDENCE_FIELDS = frozenset(
    {"evidence_state", "evidence_points", "response_if_confirmed"}
)
AGGREGATE_FIELDS = frozenset(
    {
        "v60_on_variable_family_count",
        "v60_off_variable_family_count",
        "audit_read",
        "recommended_next_action",
        "founder_answer_correctness",
        "consultant_followup_status",
        "phd_followup_status",
        "structural_delta_validation_scope",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
ALLOWED_EVIDENCE_STATES = frozenset({"weak", "plausible", "strong", "insufficient"})


class FounderV60PrivateContextAuditError(ValueError):
    pass


def build_founder_v60_private_context_audit_contract(
    *,
    root: Path | None = None,
) -> dict[str, object]:
    _ = root
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "program_scope": PROGRAM_SCOPE,
        "case_family": CASE_FAMILY,
        "source_refs": {
            "source_symmetry_result_ref": DEFAULT_SYMMETRY_RESULT_REF,
            "ledger_overlap_ref": (
                "research/pre-step6-private-consideration-ledgers/"
                "founder-grant-marcus-equity.high-clutter.ledger-overlap.v1.json"
            ),
            "problem_state_ref": (
                "research/pre-step6-problem-states/"
                "founder-grant-marcus-equity.high-clutter.problem-state.v1.json"
            ),
            "anchor_ref": (
                "research/pre-step6-rendered-hybrid-answer-cores/"
                "founder-grant-marcus-equity.high-clutter.native."
                "rendered-hybrid-answer-core.v1.json"
            ),
            "deck_ref": (
                "research/pre-step6-card-deck-replays/"
                "founder-grant-marcus-equity.high-clutter.card-deck-replay.v1.json"
            ),
        },
        "sample_sets": [dict(item) for item in DEFAULT_SAMPLE_SETS],
        "precommitted_outcomes": {
            "genuine_edge_pressure_structurally_borderline": (
                "V60-on adds genuine edge pressure and Founder remains a "
                "structurally borderline case; accept variance as information."
            ),
            "selection_noise": (
                "V60-on adds pressure not substantively related to the Founder "
                "reasoning shape; inspect V60 selection logic before architecture."
            ),
            "joint_overload": (
                "The V60 item is individually defensible, but the combined private "
                "packet destabilizes Step 6; inspect packet cap or ordering."
            ),
            "cross_chunk_consideration_gap": (
                "The issue is not selection but Step 6's ability to consider V60 "
                "items together; inspect cross-chunk consideration prompts."
            ),
        },
        "queued_followups": list(QUEUED_FOLLOWUPS),
        "explicit_limits": list(EXPLICIT_LIMITS),
        "gates": _blocked_gates(),
        "notes": (
            "Research-only V60/private-context audit. This exits the pre-Step-6 "
            "portfolio perimeter and characterizes V60 evidence without deciding "
            "Founder correctness or adding runtime behavior."
        ),
    }
    validate_founder_v60_private_context_audit_contract(payload)
    return payload


def write_founder_v60_private_context_audit_contract(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_founder_v60_private_context_audit_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "founder-v60-private-context-audit-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_founder_v60_private_context_audit_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise FounderV60PrivateContextAuditError(f"{path}: payload must be object")
    validate_founder_v60_private_context_audit_contract(payload, path=path)
    return payload


def build_founder_v60_private_context_audit_result(
    *,
    root: Path,
    contract: dict[str, object],
) -> dict[str, object]:
    validate_founder_v60_private_context_audit_contract(contract)
    root = Path(root)
    source_refs = contract["source_refs"]
    assert isinstance(source_refs, dict)
    symmetry = load_founder_v60_symmetry_result(
        root / _string(source_refs["source_symmetry_result_ref"])
    )
    validate_founder_v60_symmetry_result(symmetry)
    sample_sets = contract["sample_sets"]
    assert isinstance(sample_sets, list)
    samples_by_mode = _samples_by_mode(root=root, sample_sets=sample_sets)
    v60_context = _v60_context(samples_by_mode=samples_by_mode)
    relevance = _context_relevance(samples_by_mode=samples_by_mode, v60_context=v60_context)
    mode_comparison = _mode_comparison(
        symmetry_matrix=symmetry["comparison_matrix"],
        samples_by_mode=samples_by_mode,
    )
    outcome_evidence = _outcome_evidence(
        symmetry=symmetry,
        relevance=relevance,
        v60_context=v60_context,
    )
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "program_scope": PROGRAM_SCOPE,
        "case_family": CASE_FAMILY,
        "source_refs": dict(source_refs),
        "v60_private_context": v60_context,
        "context_relevance": relevance,
        "mode_comparison": mode_comparison,
        "outcome_evidence": outcome_evidence,
        "aggregate": _aggregate(symmetry=symmetry, outcome_evidence=outcome_evidence),
        "gates": _blocked_gates(),
        "notes": (
            "Deterministic audit over saved V60-on/off samples. Evidence channels "
            "remain separate so this cannot collapse into a hidden answer selector."
        ),
    }
    validate_founder_v60_private_context_audit_result(payload)
    return payload


def write_founder_v60_private_context_audit_result(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_founder_v60_private_context_audit_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "founder-v60-private-context-audit-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_founder_v60_private_context_audit_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise FounderV60PrivateContextAuditError(f"{path}: payload must be object")
    validate_founder_v60_private_context_audit_result(payload, path=path)
    return payload


def validate_founder_v60_private_context_audit_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_founder_v60_private_context_audit_contract_errors(payload, path=path))
    if errors:
        raise FounderV60PrivateContextAuditError("; ".join(errors))


def iter_founder_v60_private_context_audit_contract_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be object"
        return
    required = tuple(CONTRACT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, CONTRACT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    yield from _validate_common_header(payload, path=path, schema_version=CONTRACT_SCHEMA_VERSION)
    if payload.get("program_scope") != PROGRAM_SCOPE:
        yield f"{path / 'program_scope'}: must be {PROGRAM_SCOPE}"
    if payload.get("case_family") != CASE_FAMILY:
        yield f"{path / 'case_family'}: must be {CASE_FAMILY}"
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    yield from _validate_sample_sets(payload.get("sample_sets"), path / "sample_sets")
    outcomes = payload.get("precommitted_outcomes")
    if not isinstance(outcomes, dict):
        yield f"{path / 'precommitted_outcomes'}: must be object"
    elif set(outcomes) != set(PRECOMMITTED_OUTCOME_KEYS):
        yield f"{path / 'precommitted_outcomes'}: must have exactly expected outcome keys"
    if payload.get("queued_followups") != list(QUEUED_FOLLOWUPS):
        yield f"{path / 'queued_followups'}: must preserve queued followups"
    if payload.get("explicit_limits") != list(EXPLICIT_LIMITS):
        yield f"{path / 'explicit_limits'}: must preserve explicit limits"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_founder_v60_private_context_audit_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_founder_v60_private_context_audit_result_errors(payload, path=path))
    if errors:
        raise FounderV60PrivateContextAuditError("; ".join(errors))


def iter_founder_v60_private_context_audit_result_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be object"
        return
    required = tuple(RESULT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, RESULT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    yield from _validate_common_header(payload, path=path, schema_version=RESULT_SCHEMA_VERSION)
    if payload.get("program_scope") != PROGRAM_SCOPE:
        yield f"{path / 'program_scope'}: must be {PROGRAM_SCOPE}"
    if payload.get("case_family") != CASE_FAMILY:
        yield f"{path / 'case_family'}: must be {CASE_FAMILY}"
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    yield from _validate_v60_context(payload.get("v60_private_context"), path / "v60_private_context")
    yield from _validate_relevance(payload.get("context_relevance"), path / "context_relevance")
    yield from _validate_mode_comparison(payload.get("mode_comparison"), path / "mode_comparison")
    yield from _validate_outcome_evidence(payload.get("outcome_evidence"), path / "outcome_evidence")
    yield from _validate_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _samples_by_mode(
    *,
    root: Path,
    sample_sets: list[object],
) -> dict[tuple[str, str], list[dict[str, object]]]:
    samples: dict[tuple[str, str], list[dict[str, object]]] = {}
    for sample_set in sample_sets:
        if not isinstance(sample_set, dict):
            continue
        sample_dir = root / _string(sample_set.get("sample_dir"))
        case_id = _string(sample_set.get("case_id"))
        model_family = _string(sample_set.get("model_family"))
        mode = _string(sample_set.get("v60_mode"))
        loaded = [
            load_step6_calibration_sample(path)
            for path in sorted(sample_dir.glob(f"{case_id}.sample-*.calibration-step6.v1.json"))
        ]
        for sample in loaded:
            validate_step6_calibration_sample(sample)
        samples[(model_family, mode)] = loaded
    return samples


def _v60_context(
    *,
    samples_by_mode: dict[tuple[str, str], list[dict[str, object]]],
) -> dict[str, object]:
    on_contexts = _context_texts(samples_by_mode=samples_by_mode, mode="on")
    off_contexts = _context_texts(samples_by_mode=samples_by_mode, mode="off")
    raw_text = next((text for text in on_contexts if text), "")
    chunk_ids = _chunk_ids(raw_text)
    return {
        "raw_text": raw_text,
        "chunk_ids": chunk_ids,
        "chunk_count": len(chunk_ids),
        "source_ref": "synthetic_pre_step6_private_consideration_ledger_fixture",
        "source_note": (
            "Context is read from saved Step 6 calibration samples; this audit "
            "does not run live V60 selection."
        ),
        "present_in_v60_on_samples": sum(1 for text in on_contexts if text),
        "present_in_v60_off_samples": sum(1 for text in off_contexts if text),
    }


def _context_texts(
    *,
    samples_by_mode: dict[tuple[str, str], list[dict[str, object]]],
    mode: str,
) -> list[str]:
    texts: list[str] = []
    for (model_family, sample_mode), samples in sorted(samples_by_mode.items()):
        _ = model_family
        if sample_mode != mode:
            continue
        for sample in samples:
            packet = sample.get("input_packet")
            if isinstance(packet, dict):
                texts.append(_string(packet.get("v60_private_context")))
    return texts


def _context_relevance(
    *,
    samples_by_mode: dict[tuple[str, str], list[dict[str, object]]],
    v60_context: dict[str, object],
) -> dict[str, object]:
    case_text = "\n".join(_case_surface_texts(samples_by_mode=samples_by_mode))
    case_terms = _terms(case_text)
    v60_terms = _terms(_string(v60_context.get("raw_text")))
    overlap = sorted(case_terms & v60_terms)
    if len(overlap) >= 3:
        read = "related_surface_terms_present"
    elif overlap:
        read = "weak_surface_overlap_present"
    else:
        read = "no_surface_overlap_detected"
    return {
        "case_surface_terms": sorted(case_terms),
        "v60_terms": sorted(v60_terms),
        "overlap_terms": overlap,
        "overlap_count": len(overlap),
        "relevance_read": read,
    }


def _case_surface_texts(
    *,
    samples_by_mode: dict[tuple[str, str], list[dict[str, object]]],
) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()
    for samples in samples_by_mode.values():
        for sample in samples:
            packet = sample.get("input_packet")
            if not isinstance(packet, dict):
                continue
            for field in ("case_brief", "anchor_visible_candidate", "deck_pressure_candidate"):
                value = _string(packet.get(field))
                if value and value not in seen:
                    texts.append(value)
                    seen.add(value)
    return texts


def _mode_comparison(
    *,
    symmetry_matrix: object,
    samples_by_mode: dict[tuple[str, str], list[dict[str, object]]],
) -> list[dict[str, object]]:
    if not isinstance(symmetry_matrix, list):
        return []
    rows: list[dict[str, object]] = []
    for row in symmetry_matrix:
        if not isinstance(row, dict):
            continue
        samples = samples_by_mode.get(
            (_string(row.get("model_family")), _string(row.get("v60_mode"))),
            [],
        )
        rows.append(
            {
                "model_family": _string(row.get("model_family")),
                "model": _string(row.get("model")),
                "v60_mode": _string(row.get("v60_mode")),
                "case_id": _string(row.get("case_id")),
                "sample_count": _non_negative_int(row.get("sample_count")),
                "unlock_count": _non_negative_int(row.get("unlock_count")),
                "visibility_classification": _string(row.get("visibility_classification")),
                "answer_token_jaccard_min": row.get("answer_token_jaccard_min"),
                "ledger_signal_counts": dict(row.get("ledger_signal_counts", {})),
                "answer_delta_specificity_counts": dict(row.get("answer_delta_specificity_counts", {})),
                "deck_visible_effects": _unique_strings(
                    _deck_ledger_field(sample, "visible_effect") for sample in samples
                ),
                "deck_answer_delta_summary": _answer_delta_summaries(samples),
            }
        )
    return rows


def _outcome_evidence(
    *,
    symmetry: dict[str, object],
    relevance: dict[str, object],
    v60_context: dict[str, object],
) -> dict[str, dict[str, object]]:
    aggregate = symmetry.get("aggregate")
    if not isinstance(aggregate, dict):
        aggregate = {}
    on_variable = _non_negative_int(aggregate.get("v60_on_variable_family_count"))
    off_variable = _non_negative_int(aggregate.get("v60_off_variable_family_count"))
    related = _non_negative_int(relevance.get("overlap_count")) > 0
    one_chunk = _non_negative_int(v60_context.get("chunk_count")) <= 1
    return {
        "genuine_edge_pressure_structurally_borderline": {
            "evidence_state": "plausible" if on_variable and related else "insufficient",
            "evidence_points": [
                "V60 context shares surface terms with Founder case material.",
                "Both model families became variable on V60-on samples.",
                "V60-off stabilizes each family but does not settle the correct answer direction.",
            ],
            "response_if_confirmed": (
                "Treat Founder as borderline under useful edge pressure; do not "
                "add a deterministic wisdom selector."
            ),
        },
        "selection_noise": {
            "evidence_state": "weak" if related else "plausible",
            "evidence_points": [
                "The V60 chunk is mechanically related to evidence, commitments, and board process.",
                "This audit cannot prove selection quality; it only weakens the claim that the chunk is unrelated noise.",
            ],
            "response_if_confirmed": (
                "Audit V60 selection logic for Founder-like cases before any "
                "pre-Step-6 architecture change."
            ),
        },
        "joint_overload": {
            "evidence_state": "plausible" if on_variable and off_variable == 0 else "weak",
            "evidence_points": [
                "V60-on is variable for both model families while V60-off is not variable.",
                "The chunk can be individually defensible and still destabilize the private packet.",
            ],
            "response_if_confirmed": (
                "Inspect V60 packet cap, ordering, and presentation interaction "
                "with card/deck pressure."
            ),
        },
        "cross_chunk_consideration_gap": {
            "evidence_state": "insufficient" if one_chunk else "plausible",
            "evidence_points": [
                "Saved Founder samples expose only one synthetic V60 chunk.",
                "A cross-chunk diagnosis needs multi-chunk V60 packets, which this audit does not have.",
            ],
            "response_if_confirmed": (
                "Inspect Step 6 cross-chunk consideration prompt behavior before "
                "changing V60 selection."
            ),
        },
    }


def _aggregate(
    *,
    symmetry: dict[str, object],
    outcome_evidence: dict[str, dict[str, object]],
) -> dict[str, object]:
    symmetry_aggregate = symmetry.get("aggregate")
    if not isinstance(symmetry_aggregate, dict):
        symmetry_aggregate = {}
    on_variable = _non_negative_int(symmetry_aggregate.get("v60_on_variable_family_count"))
    off_variable = _non_negative_int(symmetry_aggregate.get("v60_off_variable_family_count"))
    if (
        on_variable >= 2
        and off_variable == 0
        and outcome_evidence["joint_overload"]["evidence_state"] == "plausible"
        and outcome_evidence["selection_noise"]["evidence_state"] == "weak"
    ):
        audit_read = "v60_context_related_but_destabilizing"
        action = "review_v60_selection_packet_before_architecture_choice"
    elif outcome_evidence["selection_noise"]["evidence_state"] == "plausible":
        audit_read = "v60_selection_noise_plausible"
        action = "review_v60_selection_packet_before_architecture_choice"
    elif outcome_evidence["cross_chunk_consideration_gap"]["evidence_state"] == "plausible":
        audit_read = "cross_chunk_consideration_gap_plausible"
        action = "inspect_step6_cross_chunk_consideration_before_architecture_choice"
    else:
        audit_read = "founder_structurally_borderline_under_edge_pressure"
        action = "treat_founder_as_structurally_borderline_and_continue_queued_followups"
    return {
        "v60_on_variable_family_count": on_variable,
        "v60_off_variable_family_count": off_variable,
        "audit_read": audit_read,
        "recommended_next_action": action,
        "founder_answer_correctness": "not_decided",
        "consultant_followup_status": "queued_not_addressed",
        "phd_followup_status": "queued_not_addressed",
        "structural_delta_validation_scope": (
            "small_n_viable_on_gpt_phd_samples_not_global_robustness"
        ),
    }


def _answer_delta_summaries(samples: Sequence[dict[str, object]]) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {
        "added_entities": [],
        "removed_entities": [],
        "reordered_sequences": [],
        "structural_delta": [],
        "reframed_emphasis": [],
    }
    for sample in samples:
        delta = _deck_answer_delta(sample)
        for field in summary:
            values = delta.get(field) if isinstance(delta, dict) else None
            if isinstance(values, list):
                summary[field].extend(_string(value) for value in values if _string(value).strip())
    return {field: _unique_strings(values) for field, values in summary.items()}


def _deck_ledger_field(sample: dict[str, object], field: str) -> str:
    item = _deck_ledger_item(sample)
    return _string(item.get(field)) if item else ""


def _deck_answer_delta(sample: dict[str, object]) -> dict[str, object]:
    item = _deck_ledger_item(sample)
    if not item:
        return {}
    delta = item.get("answer_delta")
    return delta if isinstance(delta, dict) else {}


def _deck_ledger_item(sample: dict[str, object]) -> dict[str, object] | None:
    output = sample.get("step6_output")
    if not isinstance(output, dict):
        return None
    ledger = output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return None
    for item in ledger:
        if isinstance(item, dict) and item.get("source_id") == "deck_pressure_candidate":
            return item
    return None


def _chunk_ids(raw_text: str) -> list[str]:
    return sorted(set(re.findall(r"\bv60_chunk:[a-z0-9_\-]+", raw_text)))


def _terms(text: str) -> set[str]:
    stopwords = {
        "about",
        "after",
        "before",
        "being",
        "those",
        "through",
        "under",
        "until",
        "which",
        "would",
        "without",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) >= 5 and token not in stopwords
    }


def _validate_common_header(
    payload: dict[str, object],
    *,
    path: Path,
    schema_version: str,
) -> Iterable[str]:
    if payload.get("schema_version") != schema_version:
        yield f"{path / 'schema_version'}: must be {schema_version}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"


def _validate_source_refs(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, SOURCE_REF_FIELDS, path)
    yield from _missing_fields(value, SOURCE_REF_FIELDS, path)
    for field in SOURCE_REF_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_sample_sets(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or not value:
        yield f"{path}: must be non-empty list"
        return
    for index, sample_set in enumerate(value):
        if not isinstance(sample_set, dict):
            yield f"{path / str(index)}: sample set must be object"
            continue
        yield from _unknown_fields(sample_set, SAMPLE_SET_FIELDS, path / str(index))
        yield from _missing_fields(sample_set, SAMPLE_SET_FIELDS, path / str(index))
        if sample_set.get("v60_mode") not in {"on", "off"}:
            yield f"{path / str(index) / 'v60_mode'}: must be on or off"
        for field in SAMPLE_SET_FIELDS:
            if not _string(sample_set.get(field)).strip():
                yield f"{path / str(index) / field}: must be non-empty"


def _validate_v60_context(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, CONTEXT_FIELDS, path)
    yield from _missing_fields(value, CONTEXT_FIELDS, path)
    if not _string(value.get("raw_text")).strip():
        yield f"{path / 'raw_text'}: must be non-empty"
    if not isinstance(value.get("chunk_ids"), list):
        yield f"{path / 'chunk_ids'}: must be list"
    for field in ("chunk_count", "present_in_v60_on_samples", "present_in_v60_off_samples"):
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"


def _validate_relevance(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, RELEVANCE_FIELDS, path)
    yield from _missing_fields(value, RELEVANCE_FIELDS, path)
    for field in ("case_surface_terms", "v60_terms", "overlap_terms"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"
    if not isinstance(value.get("overlap_count"), int) or value.get("overlap_count") < 0:
        yield f"{path / 'overlap_count'}: must be non-negative integer"
    if not _string(value.get("relevance_read")).strip():
        yield f"{path / 'relevance_read'}: must be non-empty"


def _validate_mode_comparison(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or not value:
        yield f"{path}: must be non-empty list"
        return
    for index, row in enumerate(value):
        row_path = path / str(index)
        if not isinstance(row, dict):
            yield f"{row_path}: row must be object"
            continue
        yield from _unknown_fields(row, MODE_ROW_FIELDS, row_path)
        yield from _missing_fields(row, MODE_ROW_FIELDS, row_path)
        for field in ("sample_count", "unlock_count"):
            if not isinstance(row.get(field), int) or row.get(field) < 0:
                yield f"{row_path / field}: must be non-negative integer"
        if not isinstance(row.get("ledger_signal_counts"), dict):
            yield f"{row_path / 'ledger_signal_counts'}: must be object"
        if not isinstance(row.get("answer_delta_specificity_counts"), dict):
            yield f"{row_path / 'answer_delta_specificity_counts'}: must be object"
        if not isinstance(row.get("deck_visible_effects"), list):
            yield f"{row_path / 'deck_visible_effects'}: must be list"
        if not isinstance(row.get("deck_answer_delta_summary"), dict):
            yield f"{row_path / 'deck_answer_delta_summary'}: must be object"


def _validate_outcome_evidence(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    if set(value) != set(PRECOMMITTED_OUTCOME_KEYS):
        yield f"{path}: must have exactly precommitted outcome keys"
        return
    for key, item in value.items():
        item_path = path / key
        if not isinstance(item, dict):
            yield f"{item_path}: must be object"
            continue
        yield from _unknown_fields(item, EVIDENCE_FIELDS, item_path)
        yield from _missing_fields(item, EVIDENCE_FIELDS, item_path)
        if item.get("evidence_state") not in ALLOWED_EVIDENCE_STATES:
            yield f"{item_path / 'evidence_state'}: invalid evidence state"
        if not isinstance(item.get("evidence_points"), list) or not item.get("evidence_points"):
            yield f"{item_path / 'evidence_points'}: must be non-empty list"
        if not _string(item.get("response_if_confirmed")).strip():
            yield f"{item_path / 'response_if_confirmed'}: must be non-empty"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    for field in ("v60_on_variable_family_count", "v60_off_variable_family_count"):
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    for field in AGGREGATE_FIELDS - {"v60_on_variable_family_count", "v60_off_variable_family_count"}:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, GATE_FIELDS, path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _blocked_gates() -> dict[str, bool]:
    return {"runtime_wiring_allowed": False, "skill_update_allowed": False}


def _unique_strings(values: Iterable[str]) -> list[str]:
    return sorted({value.strip() for value in values if value.strip()})


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _read_json(path: Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _non_negative_int(value: object) -> int:
    return value if isinstance(value, int) and value >= 0 else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise FounderV60PrivateContextAuditError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_founder_v60_private_context_audit_contract(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_founder_v60_private_context_audit_result(payload, path=path)
            else:
                raise FounderV60PrivateContextAuditError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_founder_v60_private_context_audit_contract(args.contract)
        if args.contract
        else build_founder_v60_private_context_audit_contract(root=Path.cwd())
    )
    if args.write_contract:
        print(write_founder_v60_private_context_audit_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.write_result:
        result = build_founder_v60_private_context_audit_result(root=Path.cwd(), contract=contract)
        print(write_founder_v60_private_context_audit_result(payload=result, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
