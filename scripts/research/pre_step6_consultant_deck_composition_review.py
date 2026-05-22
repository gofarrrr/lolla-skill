#!/usr/bin/env python3
"""Research-only Consultant deck-composition cleaning review.

This is not a visibility-policy or gate review. It asks whether the material
given to Step 6 on the Consultant case is clean enough: anchor, Bevelin/Polya
pressure, V60 status, saved Step 6 variance, and reviewer feedback.
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


CONTRACT_SCHEMA_VERSION = "pre_step6_consultant_deck_composition_contract.v1"
RESULT_SCHEMA_VERSION = "pre_step6_consultant_deck_composition_result.v1"
VARIANT_SCHEMA_VERSION = "pre_step6_consultant_cleaning_variant.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "consultant_deck_composition_review_v0"
VARIANT_EXPERIMENT_ID = "consultant_cleaning_variant_v0"
PROGRAM_SCOPE = "cleaning_review_not_visibility_gate"
VARIANT_PROGRAM_SCOPE = "cleaning_variant_not_visibility_gate"
CASE_ID = "mid-level-consultant-report-2"
DEFAULT_OUT_DIR = Path("research/pre-step6-consultant-deck-composition-review")
HYPOTHESES = (
    "anchor_sufficient_but_deck_compression_helpful",
    "deck_pressure_too_thin_or_generic",
    "lens_composition_misaligned",
    "case_intrinsically_ambiguous_after_cleaning",
    "v60_not_active_for_consultant",
)
EXPLICIT_LIMITS = (
    "does_not_add_or_change_visibility_gates",
    "does_not_decide_legal_correctness",
    "does_not_promote_runtime_or_skill",
    "does_not_route_by_model_family",
)
VARIANT_CANDIDATES = (
    "counsel_independence_and_channel_bias_card",
    "wednesday_tripwire_preservation_card",
    "reversibility_until_counsel_boundary_card",
)
DEFAULT_SOURCE_REFS = {
    "card_deck_ref": (
        "research/pre-step6-step6-card-decks/"
        "mid-level-consultant-report-2.step6-card-deck.v1.json"
    ),
    "private_cards_ref": (
        "research/pre-step6-private-reasoning-cards/"
        "mid-level-consultant-report-2.private-reasoning-cards.v1.json"
    ),
    "problem_state_ref": (
        "research/pre-step6-problem-states/"
        "mid-level-consultant-report-2.problem-state.v1.json"
    ),
    "anchor_ref": (
        "research/pre-step6-rendered-hybrid-answer-cores/"
        "mid-level-consultant-report-2.native.rendered-hybrid-answer-core.v1.json"
    ),
    "card_deck_replay_ref": (
        "research/pre-step6-card-deck-replays/"
        "mid-level-consultant-report-2.card-deck-replay.v1.json"
    ),
    "variable_case_diagnostic_ref": (
        "research/pre-step6-variable-case-diagnostic/"
        "variable-case-diagnostic-result.v1.json"
    ),
    "gpt_stability_correctness_ref": (
        "research/pre-step6-gpt-stability-correctness-review/"
        "gpt-stability-correctness-result.v1.json"
    ),
    "kimi_sample_dir_ref": (
        "research/pre-step6-calibration-corpus-kimi-structural-delta/step6-samples"
    ),
    "gpt_sample_dir_ref": "research/pre-step6-variable-case-alt-model-gpt51/step6-samples",
}
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "program_scope",
        "case_id",
        "cleaning_question",
        "source_refs",
        "precommitted_hypotheses",
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
        "case_id",
        "source_refs",
        "deck_material",
        "sample_stability",
        "reviewer_feedback",
        "hypothesis_evidence",
        "cleaning_variant_candidates",
        "aggregate",
        "gates",
        "notes",
    }
)
SOURCE_REF_FIELDS = frozenset(DEFAULT_SOURCE_REFS)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
EVIDENCE_FIELDS = frozenset({"evidence_state", "evidence_points", "cleaning_implication"})
ALLOWED_EVIDENCE_STATES = frozenset({"weak", "plausible", "strong", "insufficient"})
AGGREGATE_FIELDS = frozenset(
    {
        "kimi_unlock_ratio",
        "gpt_stable_standdown_reviewer_supported",
        "v60_status",
        "cleaning_read",
        "recommended_next_action",
        "runtime_promotion",
        "skill_update",
    }
)
VARIANT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "program_scope",
        "case_id",
        "source_review_schema_version",
        "source_refs",
        "anchor_policy",
        "micro_cards",
        "expected_cleaning_effect",
        "explicit_limits",
        "gates",
        "notes",
    }
)
ANCHOR_POLICY_FIELDS = frozenset({"policy", "anchor_ref", "preserved_payload"})
MICRO_CARD_FIELDS = frozenset(
    {
        "card_id",
        "card_type",
        "source_pressure",
        "cognitive_role",
        "receipts",
        "handling_rule",
        "misuse_guard",
        "standdown_condition",
    }
)


class ConsultantDeckCompositionError(ValueError):
    pass


def build_consultant_deck_composition_contract(*, root: Path | None = None) -> dict[str, object]:
    _ = root
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "program_scope": PROGRAM_SCOPE,
        "case_id": CASE_ID,
        "cleaning_question": (
            "Does the Consultant deck give Step 6 the right material to reach "
            "a clean answer, or are anchor/cards/V60 packaging the case poorly?"
        ),
        "source_refs": dict(DEFAULT_SOURCE_REFS),
        "precommitted_hypotheses": {
            "anchor_sufficient_but_deck_compression_helpful": (
                "The anchor carries the safety payload, while deck pressure adds "
                "concise wording or small concrete refinements."
            ),
            "deck_pressure_too_thin_or_generic": (
                "The deck pressure is mostly confirming, so Step 6 flips between "
                "treating it as additive and private support."
            ),
            "lens_composition_misaligned": (
                "Bevelin/Polya receipts overlap the anchor too much or miss the "
                "actual structural pressure needed for this case shape."
            ),
            "case_intrinsically_ambiguous_after_cleaning": (
                "Even with a clean deck, multiple visible answers may be valid "
                "because the useful delta is small and stylistic."
            ),
            "v60_not_active_for_consultant": (
                "No V60 context is active on this case, so V60 should not be used "
                "as the explanation for Consultant variance."
            ),
        },
        "explicit_limits": list(EXPLICIT_LIMITS),
        "gates": _blocked_gates(),
        "notes": (
            "Research-only cleaning review. The output may recommend deck material "
            "experiments, not runtime resolver changes."
        ),
    }
    validate_consultant_deck_composition_contract(payload)
    return payload


def write_consultant_deck_composition_contract(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_deck_composition_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consultant-deck-composition-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_consultant_deck_composition_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ConsultantDeckCompositionError(f"{path}: payload must be object")
    validate_consultant_deck_composition_contract(payload, path=path)
    return payload


def build_consultant_deck_composition_result(
    *,
    root: Path,
    contract: dict[str, object],
) -> dict[str, object]:
    validate_consultant_deck_composition_contract(contract)
    root = Path(root)
    source_refs = contract["source_refs"]
    assert isinstance(source_refs, dict)
    card_deck = _read_object(root / _string(source_refs["card_deck_ref"]))
    private_cards = _read_object(root / _string(source_refs["private_cards_ref"]))
    problem_state = _read_object(root / _string(source_refs["problem_state_ref"]))
    anchor = _read_object(root / _string(source_refs["anchor_ref"]))
    replay = _read_object(root / _string(source_refs["card_deck_replay_ref"]))
    variable_diagnostic = _read_object(root / _string(source_refs["variable_case_diagnostic_ref"]))
    gpt_review = _read_object(root / _string(source_refs["gpt_stability_correctness_ref"]))
    kimi_samples = _load_samples(root / _string(source_refs["kimi_sample_dir_ref"]), CASE_ID)
    gpt_samples = _load_samples(root / _string(source_refs["gpt_sample_dir_ref"]), CASE_ID)

    deck_material = _deck_material(
        card_deck=card_deck,
        private_cards=private_cards,
        problem_state=problem_state,
        anchor=anchor,
        replay=replay,
        kimi_samples=kimi_samples,
    )
    sample_stability = _sample_stability(
        variable_diagnostic=variable_diagnostic,
        kimi_samples=kimi_samples,
        gpt_samples=gpt_samples,
    )
    reviewer_feedback = _reviewer_feedback(gpt_review=gpt_review)
    hypothesis_evidence = _hypothesis_evidence(
        deck_material=deck_material,
        sample_stability=sample_stability,
        reviewer_feedback=reviewer_feedback,
    )
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "program_scope": PROGRAM_SCOPE,
        "case_id": CASE_ID,
        "source_refs": dict(source_refs),
        "deck_material": deck_material,
        "sample_stability": sample_stability,
        "reviewer_feedback": reviewer_feedback,
        "hypothesis_evidence": hypothesis_evidence,
        "cleaning_variant_candidates": list(VARIANT_CANDIDATES),
        "aggregate": _aggregate(sample_stability=sample_stability, reviewer_feedback=reviewer_feedback),
        "gates": _blocked_gates(),
        "notes": (
            "This result characterizes material quality and deck composition. It "
            "does not choose visibility, decide legal correctness, or route models."
        ),
    }
    validate_consultant_deck_composition_result(payload)
    return payload


def write_consultant_deck_composition_result(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_deck_composition_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consultant-deck-composition-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_consultant_deck_composition_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ConsultantDeckCompositionError(f"{path}: payload must be object")
    validate_consultant_deck_composition_result(payload, path=path)
    return payload


def build_consultant_cleaning_variant(
    *,
    root: Path,
    review_result: dict[str, object],
) -> dict[str, object]:
    validate_consultant_deck_composition_result(review_result)
    _ = root
    source_refs = review_result["source_refs"]
    assert isinstance(source_refs, dict)
    payload = {
        "schema_version": VARIANT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": VARIANT_EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "program_scope": VARIANT_PROGRAM_SCOPE,
        "case_id": CASE_ID,
        "source_review_schema_version": review_result["schema_version"],
        "source_refs": dict(source_refs),
        "anchor_policy": {
            "policy": "keep_anchor_as_backbone",
            "anchor_ref": _string(source_refs.get("anchor_ref")),
            "preserved_payload": [
                "counsel-first sequencing",
                "no confrontation, private investigation, unusual access, or self-selected channel",
                "notes preserved and spouse told only in broad strokes",
                "attorney intake tests channel bias",
                "Wednesday normal-behavior protocol",
                "partner-encounter tripwires including do not deny",
                "early steps stay reversible",
            ],
        },
        "micro_cards": [
            {
                "card_id": "counsel_independence_and_channel_bias_card",
                "card_type": "cleaning_micro_card",
                "source_pressure": "bevelin_pressure_atom_without_lens_label",
                "cognitive_role": (
                    "Make counsel independence and channel-bias testing explicit "
                    "without expanding into generic incentives theory."
                ),
                "receipts": [
                    "Use independent whistleblower or employment-law counsel.",
                    "Ask how counsel decides among internal, audit-committee, and external channels.",
                    "Check for any built-in bias before treating counsel-first as blind deference.",
                ],
                "handling_rule": (
                    "Use if it sharpens attorney selection or intake; keep private "
                    "if the anchor already states the same check with enough force."
                ),
                "misuse_guard": (
                    "Do not turn built-in bias into a public mental-model explanation "
                    "or a reason to distrust counsel."
                ),
                "standdown_condition": (
                    "Stand down when the answer already asks concrete channel-bias "
                    "intake questions."
                ),
            },
            {
                "card_id": "wednesday_tripwire_preservation_card",
                "card_type": "cleaning_micro_card",
                "source_pressure": "anchor_payload_preservation_atom",
                "cognitive_role": (
                    "Protect the Wednesday protocol and partner-encounter tripwires "
                    "from over-compression."
                ),
                "receipts": [
                    "Attend Wednesday normally and avoid abrupt changes in behavior.",
                    "If the partner raises the encounter, keep the response minimal and narrow.",
                    "Preserve the do not deny, elaborate, confront, investigate, or be alone tripwire.",
                ],
                "handling_rule": (
                    "Use as a preservation guard when making the answer shorter; "
                    "compression must not drop the concrete tripwires."
                ),
                "misuse_guard": (
                    "Do not simplify the Wednesday protocol so far that do not deny "
                    "or avoid being alone disappears."
                ),
                "standdown_condition": (
                    "Stand down when the final answer retains the complete Wednesday "
                    "and partner-encounter protocol."
                ),
            },
            {
                "card_id": "reversibility_until_counsel_boundary_card",
                "card_type": "cleaning_micro_card",
                "source_pressure": "polya_and_deck_boundary_atom_without_lens_label",
                "cognitive_role": (
                    "Make the reversibility boundary concrete: move fast, but only "
                    "until counsel guides the next action."
                ),
                "receipts": [
                    "Move quickly without filing or choosing a channel before evidence review.",
                    "Keep early steps reversible until counsel guides the next move.",
                    "Do not let fear cause premature filing or paralysis.",
                ],
                "handling_rule": (
                    "Use if the answer needs a sharper stop boundary between safe "
                    "first moves and irreversible reporting/channel decisions."
                ),
                "misuse_guard": (
                    "Do not convert reversibility into delay, inaction, or avoidance "
                    "of getting counsel involved."
                ),
                "standdown_condition": (
                    "Stand down when urgency and reversibility are both already "
                    "clear in the public answer."
                ),
            },
        ],
        "expected_cleaning_effect": (
            "Replace broad lens labels with concrete pressure atoms so Step 6 sees "
            "what can improve the answer without over-reading generic Bevelin/Polya "
            "identity."
        ),
        "explicit_limits": list(EXPLICIT_LIMITS),
        "gates": _blocked_gates(),
        "notes": (
            "Research-only deck-cleaning variant. It can be replayed later, but it "
            "does not wire runtime behavior or decide visibility."
        ),
    }
    validate_consultant_cleaning_variant(payload)
    return payload


def write_consultant_cleaning_variant(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_cleaning_variant(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consultant-cleaning-variant.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_consultant_cleaning_variant(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ConsultantDeckCompositionError(f"{path}: payload must be object")
    validate_consultant_cleaning_variant(payload, path=path)
    return payload


def validate_consultant_deck_composition_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_deck_composition_contract_errors(payload, path=path))
    if errors:
        raise ConsultantDeckCompositionError("; ".join(errors))


def iter_consultant_deck_composition_contract_errors(
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
    if payload.get("case_id") != CASE_ID:
        yield f"{path / 'case_id'}: must be {CASE_ID}"
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    hypotheses = payload.get("precommitted_hypotheses")
    if not isinstance(hypotheses, dict):
        yield f"{path / 'precommitted_hypotheses'}: must be object"
    elif set(hypotheses) != set(HYPOTHESES):
        yield f"{path / 'precommitted_hypotheses'}: must have exactly expected hypotheses"
    if payload.get("explicit_limits") != list(EXPLICIT_LIMITS):
        yield f"{path / 'explicit_limits'}: must preserve explicit limits"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_consultant_deck_composition_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_deck_composition_result_errors(payload, path=path))
    if errors:
        raise ConsultantDeckCompositionError("; ".join(errors))


def validate_consultant_cleaning_variant(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_cleaning_variant_errors(payload, path=path))
    if errors:
        raise ConsultantDeckCompositionError("; ".join(errors))


def iter_consultant_deck_composition_result_errors(
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
    if payload.get("case_id") != CASE_ID:
        yield f"{path / 'case_id'}: must be {CASE_ID}"
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    for field in ("deck_material", "sample_stability", "reviewer_feedback"):
        if not isinstance(payload.get(field), dict):
            yield f"{path / field}: must be object"
    yield from _validate_hypothesis_evidence(payload.get("hypothesis_evidence"), path / "hypothesis_evidence")
    if payload.get("cleaning_variant_candidates") != list(VARIANT_CANDIDATES):
        yield f"{path / 'cleaning_variant_candidates'}: must preserve cleaning candidates"
    yield from _validate_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def iter_consultant_cleaning_variant_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be object"
        return
    required = tuple(VARIANT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, VARIANT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != VARIANT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {VARIANT_SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != VARIANT_EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {VARIANT_EXPERIMENT_ID}"
    if payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"
    if payload.get("program_scope") != VARIANT_PROGRAM_SCOPE:
        yield f"{path / 'program_scope'}: must be {VARIANT_PROGRAM_SCOPE}"
    if payload.get("case_id") != CASE_ID:
        yield f"{path / 'case_id'}: must be {CASE_ID}"
    if payload.get("source_review_schema_version") != RESULT_SCHEMA_VERSION:
        yield f"{path / 'source_review_schema_version'}: must be {RESULT_SCHEMA_VERSION}"
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    yield from _validate_anchor_policy(payload.get("anchor_policy"), path / "anchor_policy")
    yield from _validate_micro_cards(payload.get("micro_cards"), path / "micro_cards")
    if not _string(payload.get("expected_cleaning_effect")).strip():
        yield f"{path / 'expected_cleaning_effect'}: must be non-empty"
    if payload.get("explicit_limits") != list(EXPLICIT_LIMITS):
        yield f"{path / 'explicit_limits'}: must preserve explicit limits"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _deck_material(
    *,
    card_deck: dict[str, object],
    private_cards: dict[str, object],
    problem_state: dict[str, object],
    anchor: dict[str, object],
    replay: dict[str, object],
    kimi_samples: Sequence[dict[str, object]],
) -> dict[str, object]:
    cards = card_deck.get("cards") if isinstance(card_deck.get("cards"), list) else []
    private_card_items = (
        private_cards.get("cards") if isinstance(private_cards.get("cards"), list) else []
    )
    anchor_text = _string(anchor.get("answer_core"))
    deck_candidate = _deck_candidate_from_sample(kimi_samples)
    return {
        "problem_success_condition": _string(problem_state.get("success_condition")),
        "anchor_expected_inclusions": list(anchor.get("expected_inclusions", [])),
        "anchor_token_count": len(_terms(anchor_text)),
        "deck_candidate_token_count": len(_terms(deck_candidate)),
        "card_count": len(cards),
        "card_receipts": {
            _string(card.get("card_id")): list(card.get("receipts", []))
            for card in cards
            if isinstance(card, dict)
        },
        "private_card_misuse_guards": {
            _string(card.get("card_id")): _string(card.get("misuse_guard"))
            for card in private_card_items
            if isinstance(card, dict)
        },
        "card_deck_replay_card_dispositions": _replay_dispositions(replay),
        "material_overlap": {
            "anchor_deck_overlap_ratio": _overlap_ratio(anchor_text, deck_candidate),
            "bevelin_receipts_already_in_anchor": _receipt_overlap(
                card_id="bevelin_card",
                cards=cards,
                anchor_text=anchor_text,
            ),
            "polya_receipts_already_in_anchor": _receipt_overlap(
                card_id="polya_card",
                cards=cards,
                anchor_text=anchor_text,
            ),
        },
        "v60_private_context_present": any(
            _string(_input_packet(sample).get("v60_private_context")).strip()
            for sample in kimi_samples
        ),
    }


def _sample_stability(
    *,
    variable_diagnostic: dict[str, object],
    kimi_samples: Sequence[dict[str, object]],
    gpt_samples: Sequence[dict[str, object]],
) -> dict[str, object]:
    consultant = _find_case_diagnostic(variable_diagnostic, CASE_ID)
    return {
        "kimi_sample_count": len(kimi_samples),
        "kimi_unlock_count": sum(1 for sample in kimi_samples if _sample_unlocks(sample)),
        "kimi_unlock_ratio": round(
            sum(1 for sample in kimi_samples if _sample_unlocks(sample)) / len(kimi_samples),
            3,
        )
        if kimi_samples
        else 0.0,
        "kimi_answer_token_jaccard_min": consultant.get("answer_token_jaccard_min"),
        "kimi_variance_read": _string(consultant.get("variance_read")),
        "gpt_sample_count": len(gpt_samples),
        "gpt_unlock_count": sum(1 for sample in gpt_samples if _sample_unlocks(sample)),
        "gpt_unlock_ratio": round(
            sum(1 for sample in gpt_samples if _sample_unlocks(sample)) / len(gpt_samples),
            3,
        )
        if gpt_samples
        else 0.0,
        "kimi_added_entities": _sample_delta_values(kimi_samples, "added_entities"),
        "kimi_structural_delta": _sample_delta_values(kimi_samples, "structural_delta"),
        "kimi_removed_entities": _sample_delta_values(kimi_samples, "removed_entities"),
    }


def _reviewer_feedback(*, gpt_review: dict[str, object]) -> dict[str, object]:
    case_rows = [
        row
        for row in gpt_review.get("case_results", [])
        if isinstance(row, dict) and row.get("source_case_id") == CASE_ID
    ]
    labels = [_string(row.get("confirmed_visibility_label")) for row in case_rows]
    return {
        "gpt_consultant_reviewed_count": len(case_rows),
        "confirmed_labels": labels,
        "anchor_supported_count": labels.count("gpt_anchor_supported"),
        "anchor_rejected_count": labels.count("gpt_anchor_rejected"),
        "ambiguous_count": labels.count("ambiguous"),
        "tension_count": sum(
            1 for row in case_rows if row.get("reviewer_label_consistency") == "tension_detected"
        ),
        "gpt_stable_standdown_reviewer_supported": labels.count("gpt_anchor_supported") > 0
        and labels.count("gpt_anchor_rejected") == 0,
    }


def _hypothesis_evidence(
    *,
    deck_material: dict[str, object],
    sample_stability: dict[str, object],
    reviewer_feedback: dict[str, object],
) -> dict[str, dict[str, object]]:
    v60_present = deck_material.get("v60_private_context_present") is True
    return {
        "anchor_sufficient_but_deck_compression_helpful": {
            "evidence_state": "strong",
            "evidence_points": [
                "The anchor preserves counsel-first sequencing, no-confrontation, attorney intake, Wednesday behavior, and reversibility.",
                "The original card-deck replay comparison preferred the deck-aware answer for concision without payload loss.",
            ],
            "cleaning_implication": (
                "Keep the anchor as backbone, but make useful compression and small "
                "safety qualifiers easier for Step 6 to see."
            ),
        },
        "deck_pressure_too_thin_or_generic": {
            "evidence_state": "plausible",
            "evidence_points": [
                "Kimi splits 3/6 between additive and confirming reads on the same material.",
                "Observed deck deltas are small: independent counsel, built-in bias, minimal response, and reversibility until counsel guides.",
            ],
            "cleaning_implication": (
                "Turn vague deck pressure into explicit micro-cards for the few "
                "concrete deltas that actually matter."
            ),
        },
        "lens_composition_misaligned": {
            "evidence_state": "plausible",
            "evidence_points": [
                "Bevelin and Polya receipts mostly overlap with anchor material already present.",
                "Lens value appears as small operational pressure, not broad mental-model expansion.",
            ],
            "cleaning_implication": (
                "For this case shape, reduce generic lens identity and expose the "
                "specific pressure atoms Step 6 can use."
            ),
        },
        "case_intrinsically_ambiguous_after_cleaning": {
            "evidence_state": "plausible"
            if reviewer_feedback.get("ambiguous_count", 0) else "weak",
            "evidence_points": [
                "GPT stable stand-down was not cleanly reviewer-supported.",
                "Reviewer records contain ambiguity/tension, which suggests a small visible delta rather than a clean winner.",
            ],
            "cleaning_implication": (
                "Accept that some Consultant outputs may remain borderline after "
                "cleaning; do not hide that with deterministic selection."
            ),
        },
        "v60_not_active_for_consultant": {
            "evidence_state": "weak" if v60_present else "strong",
            "evidence_points": [
                "Saved Consultant samples carry v60_mode not_applicable and empty V60 private context.",
                "Consultant variance should be investigated through deck composition, not V60 blame.",
            ],
            "cleaning_implication": "Do not import the Founder V60 explanation into Consultant.",
        },
    }


def _aggregate(
    *,
    sample_stability: dict[str, object],
    reviewer_feedback: dict[str, object],
) -> dict[str, object]:
    _ = reviewer_feedback
    return {
        "kimi_unlock_ratio": sample_stability.get("kimi_unlock_ratio", 0.0),
        "gpt_stable_standdown_reviewer_supported": False,
        "v60_status": "not_active",
        "cleaning_read": "anchor_strong_deck_pressure_thin_but_useful",
        "recommended_next_action": "build_consultant_cleaning_variant_v0",
        "runtime_promotion": "blocked",
        "skill_update": "blocked",
    }


def _load_samples(root: Path, case_id: str) -> list[dict[str, object]]:
    samples = [
        load_step6_calibration_sample(path)
        for path in sorted(root.glob(f"{case_id}.sample-*.calibration-step6.v1.json"))
    ]
    for sample in samples:
        validate_step6_calibration_sample(sample)
    return samples


def _find_case_diagnostic(payload: dict[str, object], case_id: str) -> dict[str, object]:
    rows = payload.get("case_diagnostics")
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and row.get("case_id") == case_id:
            return row
    return {}


def _sample_unlocks(sample: dict[str, object]) -> bool:
    return sample.get("ledger_signal") == "additive_pressure_present"


def _sample_delta_values(samples: Sequence[dict[str, object]], field: str) -> list[str]:
    values: list[str] = []
    for sample in samples:
        item = _deck_ledger_item(sample)
        if not item:
            continue
        delta = item.get("answer_delta")
        if not isinstance(delta, dict):
            continue
        raw_values = delta.get(field)
        if isinstance(raw_values, list):
            values.extend(_string(value) for value in raw_values if _string(value).strip())
    return _unique_strings(values)


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


def _input_packet(sample: dict[str, object]) -> dict[str, object]:
    packet = sample.get("input_packet")
    return packet if isinstance(packet, dict) else {}


def _deck_candidate_from_sample(samples: Sequence[dict[str, object]]) -> str:
    for sample in samples:
        candidate = _string(_input_packet(sample).get("deck_pressure_candidate"))
        if candidate:
            return candidate
    return ""


def _replay_dispositions(replay: dict[str, object]) -> dict[str, str]:
    output = replay.get("step6_output")
    if not isinstance(output, dict):
        return {}
    ledger = output.get("private_card_consideration_ledger")
    if not isinstance(ledger, list):
        return {}
    return {
        _string(item.get("card_id")): _string(item.get("disposition"))
        for item in ledger
        if isinstance(item, dict)
    }


def _receipt_overlap(*, card_id: str, cards: Sequence[object], anchor_text: str) -> list[str]:
    anchor_terms = _terms(anchor_text)
    overlapped: list[str] = []
    for card in cards:
        if not isinstance(card, dict) or card.get("card_id") != card_id:
            continue
        receipts = card.get("receipts")
        if not isinstance(receipts, list):
            continue
        for receipt in receipts:
            receipt_text = _string(receipt)
            if _overlap_ratio(anchor_text, receipt_text) >= 0.25 or _terms(receipt_text) & anchor_terms:
                overlapped.append(receipt_text)
    return _unique_strings(overlapped)


def _overlap_ratio(left: str, right: str) -> float:
    left_terms = _terms(left)
    right_terms = _terms(right)
    if not left_terms or not right_terms:
        return 0.0
    return round(len(left_terms & right_terms) / len(right_terms), 3)


def _terms(text: str) -> set[str]:
    stopwords = {
        "about",
        "after",
        "before",
        "being",
        "first",
        "should",
        "their",
        "there",
        "these",
        "those",
        "until",
        "which",
        "while",
        "would",
        "your",
        "yourself",
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


def _validate_hypothesis_evidence(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    if set(value) != set(HYPOTHESES):
        yield f"{path}: must have exactly expected hypotheses"
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
        if not _string(item.get("cleaning_implication")).strip():
            yield f"{item_path / 'cleaning_implication'}: must be non-empty"


def _validate_anchor_policy(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, ANCHOR_POLICY_FIELDS, path)
    yield from _missing_fields(value, ANCHOR_POLICY_FIELDS, path)
    if value.get("policy") != "keep_anchor_as_backbone":
        yield f"{path / 'policy'}: must be keep_anchor_as_backbone"
    if not _string(value.get("anchor_ref")).strip():
        yield f"{path / 'anchor_ref'}: must be non-empty"
    payload = value.get("preserved_payload")
    if not isinstance(payload, list) or not payload:
        yield f"{path / 'preserved_payload'}: must be non-empty list"


def _validate_micro_cards(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or len(value) != len(VARIANT_CANDIDATES):
        yield f"{path}: must contain exactly {len(VARIANT_CANDIDATES)} cards"
        return
    card_ids = []
    for index, card in enumerate(value):
        card_path = path / str(index)
        if not isinstance(card, dict):
            yield f"{card_path}: must be object"
            continue
        yield from _unknown_fields(card, MICRO_CARD_FIELDS, card_path)
        yield from _missing_fields(card, MICRO_CARD_FIELDS, card_path)
        if any(field not in card for field in MICRO_CARD_FIELDS):
            continue
        card_ids.append(card.get("card_id"))
        if card.get("card_type") != "cleaning_micro_card":
            yield f"{card_path / 'card_type'}: must be cleaning_micro_card"
        for field in (
            "source_pressure",
            "cognitive_role",
            "handling_rule",
            "misuse_guard",
            "standdown_condition",
        ):
            if not _string(card.get(field)).strip():
                yield f"{card_path / field}: must be non-empty"
        receipts = card.get("receipts")
        if not isinstance(receipts, list) or not receipts:
            yield f"{card_path / 'receipts'}: must be non-empty list"
    if card_ids != list(VARIANT_CANDIDATES):
        yield f"{path}: card ids must match cleaning variant candidates"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    if not isinstance(value.get("kimi_unlock_ratio"), float):
        yield f"{path / 'kimi_unlock_ratio'}: must be float"
    if not isinstance(value.get("gpt_stable_standdown_reviewer_supported"), bool):
        yield f"{path / 'gpt_stable_standdown_reviewer_supported'}: must be bool"
    for field in AGGREGATE_FIELDS - {"kimi_unlock_ratio", "gpt_stable_standdown_reviewer_supported"}:
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


def _read_object(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    return payload if isinstance(payload, dict) else {}


def _read_json(path: Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _unique_strings(values: Iterable[str]) -> list[str]:
    return sorted({value.strip() for value in values if value.strip()})


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--write-variant", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise ConsultantDeckCompositionError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_consultant_deck_composition_contract(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_consultant_deck_composition_result(payload, path=path)
            elif schema == VARIANT_SCHEMA_VERSION:
                validate_consultant_cleaning_variant(payload, path=path)
            else:
                raise ConsultantDeckCompositionError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_consultant_deck_composition_contract(args.contract)
        if args.contract
        else build_consultant_deck_composition_contract(root=Path.cwd())
    )
    if args.write_contract:
        print(write_consultant_deck_composition_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.write_result:
        result = build_consultant_deck_composition_result(root=Path.cwd(), contract=contract)
        print(write_consultant_deck_composition_result(payload=result, out_dir=args.out_dir))
        return 0
    if args.write_variant:
        result = build_consultant_deck_composition_result(root=Path.cwd(), contract=contract)
        variant = build_consultant_cleaning_variant(root=Path.cwd(), review_result=result)
        print(write_consultant_cleaning_variant(payload=variant, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
