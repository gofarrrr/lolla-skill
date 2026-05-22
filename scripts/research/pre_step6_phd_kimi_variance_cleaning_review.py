#!/usr/bin/env python3
"""Research-only PhD Kimi variance cleaning review.

This slice tests whether the Kimi variance on the PhD case becomes legible when
the old Bevelin/Polya deck pressure is decomposed into atomic pressure cards.
It is not a model-router, visibility gate, or runtime promotion.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_raw_artifacts import validate_public_answer_hygiene


SCHEMA_VERSION = "pre_step6_phd_kimi_variance_cleaning_review.v1"
SAMPLE_SCHEMA_VERSION = "pre_step6_phd_kimi_variance_cleaning_sample.v1"
RESULT_SCHEMA_VERSION = "pre_step6_phd_kimi_variance_cleaning_result.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "phd_kimi_variance_cleaning_review_v0"
CASE_ID = "third-year-phd-student.v2.v60-off"
BASE_CASE_ID = "third-year-phd-student.v2"
DEFAULT_MODEL = "moonshotai/kimi-k2.6"
DEFAULT_SAMPLE_COUNT = 6
DEFAULT_OUT_DIR = Path("research/pre-step6-phd-kimi-variance-cleaning-review")
DEFAULT_SAMPLE_DIR = DEFAULT_OUT_DIR / "step6-samples"
ANCHOR_REF = (
    "research/pre-step6-rendered-hybrid-answer-cores/"
    "third-year-phd-student.conflict.native.rendered-hybrid-answer-core.v1.json"
)
SOURCE_DECK_REF = "research/pre-step6-step6-card-decks/third-year-phd-student.v2.step6-card-deck.v1.json"
SOURCE_KIMI_SAMPLE_DIR = "research/pre-step6-calibration-corpus-kimi-structural-delta/step6-samples"
CARD_IDS = (
    "bounded_probe_not_commitment_card",
    "single_cell_collaborator_feasibility_card",
    "fallback_reentry_readiness_card",
    "visible_stop_date_conditions_card",
)
CARD_SPECS = {
    "bounded_probe_not_commitment_card": {
        "cognitive_role": "Keep the Silva path as a bounded probe, not a hidden commitment.",
        "receipts": [
            "Treat the next two weeks as a short, low-cost test rather than a commitment.",
            "Do dated evidence checks instead of building a finished proposal.",
            "Do not let a reality check become an implicit dissertation choice.",
        ],
        "handling_rule": (
            "Use if the answer's timebox or commitment boundary is too soft; "
            "keep private if the anchor already makes the probe bounded."
        ),
    },
    "single_cell_collaborator_feasibility_card": {
        "cognitive_role": "Make the single-cell capability gap a concrete feasibility check.",
        "receipts": [
            "Identify a collaborator who can compensate for the lab's single-cell gaps.",
            "Ask what technical work would still be yours.",
            "A hot field plus uncertain data is not enough without capability coverage.",
        ],
        "handling_rule": (
            "Use if the answer lacks a concrete technical capability check; keep "
            "private if this would add false specificity."
        ),
    },
    "fallback_reentry_readiness_card": {
        "cognitive_role": "Make fallback viability depend on being ready for re-entry.",
        "receipts": [
            "The fallback only remains real if it is resourced, available, and ready for you to re-enter.",
            "Advisor backing must preserve the fallback path while Silva is tested.",
            "Fallback viability is not just psychological comfort; it is operational continuity.",
        ],
        "handling_rule": (
            "Use if the fallback is described too vaguely; keep private if the "
            "anchor already names advisor-backed, resourced, and technically ready."
        ),
    },
    "visible_stop_date_conditions_card": {
        "cognitive_role": "Turn stop-loss into a dated condition with visible no-go criteria.",
        "receipts": [
            "Set a clear stop date with visible conditions for saying no.",
            "Decide in advance what evidence makes you continue or stop.",
            "Do not rely on broad PhD success-rate claims as calibrated probabilities.",
        ],
        "handling_rule": (
            "Use if stop-loss is abstract; keep private if the anchor already "
            "contains a specific date and visible conditions."
        ),
    },
}
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "case_id",
        "scope",
        "source_refs",
        "sample_plan",
        "micro_cards",
        "gates",
        "notes",
    }
)
SCOPE_FIELDS = frozenset({"primary_question", "v60_mode", "reason"})
SOURCE_REF_FIELDS = frozenset({"anchor_ref", "source_deck_ref", "source_kimi_sample_dir_ref"})
SAMPLE_PLAN_FIELDS = frozenset({"step6_model", "sample_count", "success_read"})
MICRO_CARD_FIELDS = frozenset({"card_id", "cognitive_role", "receipts", "handling_rule"})
SAMPLE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "sample_index",
        "provider_metadata",
        "input_packet",
        "step6_output",
        "micro_card_signal",
        "answer_delta_specificity",
        "additive_card_ids",
        "protected_payload_presence",
        "deterministic_role",
        "gates",
        "notes",
    }
)
INPUT_PACKET_FIELDS = frozenset({"anchor_visible_candidate", "phd_cleaning_micro_cards", "success_read"})
PROVIDER_METADATA_FIELDS = frozenset(
    {
        "provider",
        "provider_name",
        "model",
        "model_family",
        "status",
        "finish_reason",
        "raw_message_content",
        "temperature",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "cached_tokens",
        "cache_write_tokens",
        "reasoning_tokens",
        "reasoning_disabled",
        "reasoning_details_present",
    }
)
STEP6_OUTPUT_FIELDS = frozenset({"answer_core", "private_micro_card_ledger"})
LEDGER_FIELDS = frozenset(
    {"source_id", "disposition", "novelty_role", "why", "visible_effect", "answer_delta"}
)
ANSWER_DELTA_FIELDS = frozenset(
    {
        "added_entities",
        "removed_entities",
        "reordered_sequences",
        "structural_delta",
        "reframed_emphasis",
    }
)
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "case_results",
        "aggregate",
        "gates",
        "notes",
    }
)
CASE_RESULT_FIELDS = frozenset(
    {
        "case_id",
        "sample_index",
        "micro_card_signal",
        "answer_delta_specificity",
        "additive_card_ids",
        "protected_payload_presence",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "sample_count",
        "micro_card_additive_count",
        "all_private_or_confirming_count",
        "missing_or_unclear_count",
        "card_additive_counts",
        "protected_payload_all_present_count",
        "atomic_discrimination_read",
        "runtime_promotion",
        "skill_update",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
ALLOWED_MICRO_CARD_SIGNALS = frozenset(
    {"micro_card_additive_present", "all_private_or_confirming", "missing_or_unclear"}
)
ALLOWED_ANSWER_DELTA_SPECIFICITY = frozenset(
    {
        "concrete_delta_present",
        "structural_delta_present",
        "reframe_only",
        "missing_or_unclear",
        "not_applicable",
    }
)
DETERMINISTIC_ROLE = (
    "validate_phd_atomic_cleaning_contract",
    "derive_micro_card_signal",
    "derive_additive_card_ids",
    "derive_answer_delta_specificity",
    "check_protected_payload_presence",
    "preserve_cleaning_review_custody",
)


class PhdKimiVarianceCleaningReviewError(ValueError):
    pass


def build_phd_kimi_variance_cleaning_review_contract(*, root: Path) -> dict[str, object]:
    _ = _anchor_text(root=root)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_id": CASE_ID,
        "scope": {
            "primary_question": (
                "Does atomic decomposition explain Kimi's PhD variance without "
                "adding a gate or changing model family?"
            ),
            "v60_mode": "off",
            "reason": "Avoid conflating atomic-deck discrimination with V60 effects.",
        },
        "source_refs": {
            "anchor_ref": ANCHOR_REF,
            "source_deck_ref": SOURCE_DECK_REF,
            "source_kimi_sample_dir_ref": SOURCE_KIMI_SAMPLE_DIR,
        },
        "sample_plan": {
            "step6_model": DEFAULT_MODEL,
            "sample_count": DEFAULT_SAMPLE_COUNT,
            "success_read": (
                "Test whether Kimi discriminates among atomic PhD pressure cards "
                "instead of oscillating on the old monolithic deck."
            ),
        },
        "micro_cards": _micro_cards(),
        "gates": _blocked_gates(),
        "notes": (
            "Research-only cleaning review. Uses v60-off to isolate card "
            "granularity from V60 effects."
        ),
    }
    validate_phd_kimi_variance_cleaning_review_contract(payload, root=root)
    return payload


def write_phd_kimi_variance_cleaning_review_contract(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_phd_kimi_variance_cleaning_review_contract(payload, root=Path.cwd())
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "phd-kimi-variance-cleaning-review-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_phd_kimi_variance_cleaning_review_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise PhdKimiVarianceCleaningReviewError(f"{path}: payload must be object")
    return payload


def build_phd_kimi_variance_cleaning_review_prompts(
    *,
    contract: dict[str, object],
    sample_index: int,
) -> dict[str, str]:
    validate_phd_kimi_variance_cleaning_review_contract(contract, root=Path.cwd())
    system_prompt = (
        "You are Step 6, the primary reasoning voice. You receive a clean PhD "
        "anchor plus private atomic pressure cards. Use cognition; the cards are "
        "not commands. Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            "PHD KIMI VARIANCE CLEANING REVIEW",
            json.dumps(
                {
                    "case_id": CASE_ID,
                    "sample_index": sample_index,
                    "v60_mode": "off",
                    "anchor_visible_candidate": _anchor_text(root=Path.cwd()),
                    "phd_cleaning_micro_cards": _micro_cards(),
                    "success_read": contract["sample_plan"]["success_read"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            "TASK",
            (
                "Write the best public-clean answer_core using the anchor as the "
                "visible backbone. Consider each atomic card separately. Use a card "
                "only if it adds concrete public value; otherwise keep it private or "
                "confirming. Preserve broad private edge and do not expose source "
                "labels or card mechanics."
            ),
            "RESPONSE JSON SHAPE",
            json.dumps(
                {
                    "answer_core": "Public-clean answer.",
                    "private_micro_card_ledger": [
                        {
                            "source_id": "one of the phd_cleaning_micro_cards card_id values",
                            "disposition": (
                                "used | combined | rejected | deferred | private_guardrail"
                            ),
                            "novelty_role": (
                                "additive_pressure | confirming_support | private_guardrail"
                            ),
                            "why": "Private rationale.",
                            "visible_effect": "Specific public change, or 'none'.",
                            "answer_delta": {
                                "added_entities": ["Concrete payload newly added."],
                                "removed_entities": ["Concrete payload removed, if any."],
                                "reordered_sequences": ["Order changes, if any."],
                                "structural_delta": ["Specific boundary, gate, or stop condition."],
                                "reframed_emphasis": ["Tone or emphasis shifts."],
                            },
                        }
                    ],
                },
                indent=2,
                ensure_ascii=False,
            ),
        ]
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def build_static_phd_kimi_variance_cleaning_review_sample(
    *,
    contract: dict[str, object],
    sample_index: int,
    additive_cards: Sequence[str],
) -> dict[str, object]:
    validate_phd_kimi_variance_cleaning_review_contract(contract, root=Path.cwd())
    output = _static_output(additive_cards=additive_cards)
    sample = _sample_payload(
        contract=contract,
        sample_index=sample_index,
        provider_metadata={
            "provider": "static",
            "provider_name": "static",
            "model": "static-phd-cleaning-review",
            "model_family": "static",
            "status": "ok",
            "finish_reason": "static",
            "raw_message_content": "",
            "temperature": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "reasoning_disabled": True,
            "reasoning_details_present": False,
        },
        step6_output=output,
        notes="Static PhD atomic cleaning review sample.",
    )
    validate_phd_kimi_variance_cleaning_review_sample(sample)
    return sample


def run_live_phd_kimi_variance_cleaning_review_sample(
    *,
    contract: dict[str, object],
    sample_index: int,
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    dry_run: bool,
) -> Path | None:
    validate_phd_kimi_variance_cleaning_review_contract(contract, root=Path.cwd())
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    os.environ.setdefault("LOLLA_OPENROUTER_DISABLE_REASONING", "1")
    prompts = build_phd_kimi_variance_cleaning_review_prompts(
        contract=contract,
        sample_index=sample_index,
    )
    if dry_run:
        print(prompts["user_prompt"])
        return None
    repo_root = Path.cwd()
    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    output, metadata = client.run_json_with_metadata(
        prompts["system_prompt"],
        prompts["user_prompt"],
        stage="pre_step6_phd_kimi_variance_cleaning_review",
        tendency_id=f"{CASE_ID}:sample-{sample_index}",
    )
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise PhdKimiVarianceCleaningReviewError(
            "live PhD cleaning review failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    sample = _sample_payload(
        contract=contract,
        sample_index=sample_index,
        provider_metadata=provider_metadata,
        step6_output=normalize_phd_cleaning_step6_output(output),
        notes="Live research-only PhD Kimi variance cleaning review sample.",
    )
    return write_phd_kimi_variance_cleaning_review_sample(payload=sample, out_dir=out_dir)


def build_phd_kimi_variance_cleaning_review_result(
    *,
    contract: dict[str, object],
    samples: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_phd_kimi_variance_cleaning_review_contract(contract, root=Path.cwd())
    for sample in samples:
        validate_phd_kimi_variance_cleaning_review_sample(sample)
    case_results = [
        {
            "case_id": _string(sample["case_id"]),
            "sample_index": sample["sample_index"],
            "micro_card_signal": sample["micro_card_signal"],
            "answer_delta_specificity": sample["answer_delta_specificity"],
            "additive_card_ids": sample["additive_card_ids"],
            "protected_payload_presence": sample["protected_payload_presence"],
        }
        for sample in sorted(samples, key=lambda item: int(item["sample_index"]))
    ]
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_results": case_results,
        "aggregate": _aggregate(case_results),
        "gates": _blocked_gates(),
        "notes": (
            "Aggregate for the PhD atomic cleaning review. It tests card "
            "granularity, not runtime visibility."
        ),
    }
    validate_phd_kimi_variance_cleaning_review_result(payload)
    return payload


def write_phd_kimi_variance_cleaning_review_result(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_phd_kimi_variance_cleaning_review_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "phd-kimi-variance-cleaning-review-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_phd_kimi_variance_cleaning_review_sample(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_phd_kimi_variance_cleaning_review_sample(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = phd_cleaning_sample_path(out_dir=out_dir, sample_index=int(payload["sample_index"]))
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def phd_cleaning_sample_path(*, out_dir: Path, sample_index: int) -> Path:
    return out_dir / f"{CASE_ID}.sample-{sample_index}.phd-cleaning-review.v1.json"


def load_phd_kimi_variance_cleaning_review_sample(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise PhdKimiVarianceCleaningReviewError(f"{path}: payload must be object")
    return payload


def normalize_phd_cleaning_step6_output(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    ledger = value.get("private_micro_card_ledger")
    if not isinstance(ledger, list):
        ledger = []
    by_source = {
        _string(item.get("source_id")): item
        for item in ledger
        if isinstance(item, dict)
    }
    normalized = []
    for source_id in CARD_IDS:
        item = by_source.get(source_id, {})
        normalized.append(
            {
                "source_id": source_id,
                "disposition": _string(item.get("disposition")) or "deferred",
                "novelty_role": _string(item.get("novelty_role")) or "confirming_support",
                "why": _string(item.get("why")) or "Model did not explain this card.",
                "visible_effect": _string(item.get("visible_effect")) or "none",
                "answer_delta": _normalize_answer_delta(item.get("answer_delta")),
            }
        )
    return {"answer_core": _string(value.get("answer_core")), "private_micro_card_ledger": normalized}


def validate_phd_kimi_variance_cleaning_review_contract(
    payload: dict[str, object],
    *,
    root: Path | None = None,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_phd_kimi_variance_cleaning_review_contract_errors(payload, root=root, path=path))
    if errors:
        raise PhdKimiVarianceCleaningReviewError("; ".join(errors))


def iter_phd_kimi_variance_cleaning_review_contract_errors(
    payload: dict[str, object],
    *,
    root: Path | None = None,
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
    yield from _validate_header(payload, path=path, schema_version=SCHEMA_VERSION)
    if payload.get("case_id") != CASE_ID:
        yield f"{path / 'case_id'}: must be {CASE_ID}"
    yield from _validate_scope(payload.get("scope"), path / "scope")
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    if root is not None and isinstance(payload.get("source_refs"), dict):
        for field in ("anchor_ref", "source_deck_ref"):
            ref = _string(payload["source_refs"].get(field))
            if not (Path(root) / ref).exists():
                yield f"{path / 'source_refs' / field}: missing file"
    yield from _validate_sample_plan(payload.get("sample_plan"), path / "sample_plan")
    yield from _validate_micro_cards(payload.get("micro_cards"), path / "micro_cards")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_phd_kimi_variance_cleaning_review_sample(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_phd_kimi_variance_cleaning_review_sample_errors(payload, path=path))
    if errors:
        raise PhdKimiVarianceCleaningReviewError("; ".join(errors))


def iter_phd_kimi_variance_cleaning_review_sample_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be object"
        return
    required = tuple(SAMPLE_FIELDS - {"notes"})
    yield from _unknown_fields(payload, SAMPLE_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    yield from _validate_header(payload, path=path, schema_version=SAMPLE_SCHEMA_VERSION)
    if payload.get("case_id") != CASE_ID:
        yield f"{path / 'case_id'}: must be {CASE_ID}"
    if not isinstance(payload.get("sample_index"), int) or payload.get("sample_index") < 0:
        yield f"{path / 'sample_index'}: must be non-negative integer"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    yield from _validate_input_packet(payload.get("input_packet"), path / "input_packet")
    yield from _validate_step6_output(payload.get("step6_output"), path / "step6_output")
    if payload.get("micro_card_signal") not in ALLOWED_MICRO_CARD_SIGNALS:
        yield f"{path / 'micro_card_signal'}: invalid signal"
    if payload.get("answer_delta_specificity") not in ALLOWED_ANSWER_DELTA_SPECIFICITY:
        yield f"{path / 'answer_delta_specificity'}: invalid specificity"
    additive = payload.get("additive_card_ids")
    if not isinstance(additive, list) or any(card_id not in CARD_IDS for card_id in additive):
        yield f"{path / 'additive_card_ids'}: must be list of known card ids"
    if not isinstance(payload.get("protected_payload_presence"), dict):
        yield f"{path / 'protected_payload_presence'}: must be object"
    if payload.get("deterministic_role") != list(DETERMINISTIC_ROLE):
        yield f"{path / 'deterministic_role'}: must preserve deterministic role"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_phd_kimi_variance_cleaning_review_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_phd_kimi_variance_cleaning_review_result_errors(payload, path=path))
    if errors:
        raise PhdKimiVarianceCleaningReviewError("; ".join(errors))


def iter_phd_kimi_variance_cleaning_review_result_errors(
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
    yield from _validate_header(payload, path=path, schema_version=RESULT_SCHEMA_VERSION)
    results = payload.get("case_results")
    if not isinstance(results, list):
        yield f"{path / 'case_results'}: must be list"
    else:
        for index, result in enumerate(results):
            yield from _validate_case_result(result, path / "case_results" / str(index))
        if payload.get("aggregate") != _aggregate(results):
            yield f"{path / 'aggregate'}: must match case_results"
    yield from _validate_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _sample_payload(
    *,
    contract: dict[str, object],
    sample_index: int,
    provider_metadata: dict[str, object],
    step6_output: dict[str, object],
    notes: str,
) -> dict[str, object]:
    normalized = normalize_phd_cleaning_step6_output(step6_output)
    answer_core = _string(normalized.get("answer_core"))
    additive_ids = additive_card_ids(normalized)
    payload = {
        "schema_version": SAMPLE_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": CASE_ID,
        "sample_index": sample_index,
        "provider_metadata": _complete_provider_metadata(provider_metadata),
        "input_packet": {
            "anchor_visible_candidate": _anchor_text(root=Path.cwd()),
            "phd_cleaning_micro_cards": contract["micro_cards"],
            "success_read": contract["sample_plan"]["success_read"],
        },
        "step6_output": normalized,
        "micro_card_signal": "micro_card_additive_present"
        if additive_ids
        else "all_private_or_confirming",
        "answer_delta_specificity": derive_answer_delta_specificity(normalized),
        "additive_card_ids": additive_ids,
        "protected_payload_presence": protected_payload_presence(answer_core),
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": _blocked_gates(),
        "notes": notes,
    }
    validate_phd_kimi_variance_cleaning_review_sample(payload)
    return payload


def additive_card_ids(step6_output: object) -> list[str]:
    if not isinstance(step6_output, dict):
        return []
    ledger = step6_output.get("private_micro_card_ledger")
    if not isinstance(ledger, list):
        return []
    return [
        _string(item.get("source_id"))
        for item in ledger
        if isinstance(item, dict)
        and item.get("source_id") in CARD_IDS
        and item.get("novelty_role") == "additive_pressure"
        and item.get("disposition") in {"used", "combined"}
    ]


def derive_answer_delta_specificity(step6_output: object) -> str:
    if not isinstance(step6_output, dict):
        return "missing_or_unclear"
    ledger = step6_output.get("private_micro_card_ledger")
    if not isinstance(ledger, list):
        return "missing_or_unclear"
    additive_items = [
        item
        for item in ledger
        if isinstance(item, dict)
        and item.get("source_id") in CARD_IDS
        and item.get("novelty_role") == "additive_pressure"
        and item.get("disposition") in {"used", "combined"}
    ]
    if not additive_items:
        return "not_applicable"
    saw_reframe = False
    for item in additive_items:
        delta = item.get("answer_delta")
        if not isinstance(delta, dict):
            return "missing_or_unclear"
        if any(_non_empty_string_list(delta.get(field)) for field in ("added_entities", "removed_entities", "reordered_sequences")):
            return "concrete_delta_present"
        if _non_empty_string_list(delta.get("structural_delta")):
            return "structural_delta_present"
        if _non_empty_string_list(delta.get("reframed_emphasis")):
            saw_reframe = True
    return "reframe_only" if saw_reframe else "missing_or_unclear"


def protected_payload_presence(answer_core: str) -> dict[str, bool]:
    text = answer_core.lower()
    return {
        "silva_present": "silva" in text,
        "advisor_present": "advisor" in text,
        "committee_present": "committee" in text,
        "fallback_present": "fallback" in text,
        "two_gates_or_gate_present": "gate" in text,
        "no_parallel_options_present": "parallel" in text,
        "success_rate_humility_present": "success-rate" in text or "success rate" in text,
    }


def _static_output(*, additive_cards: Sequence[str]) -> dict[str, object]:
    anchor = _anchor_text(root=Path.cwd())
    ledger = []
    for card_id in CARD_IDS:
        additive = card_id in additive_cards
        ledger.append(
            {
                "source_id": card_id,
                "disposition": "combined" if additive else "private_guardrail",
                "novelty_role": "additive_pressure" if additive else "confirming_support",
                "why": "Static PhD cleaning review fixture.",
                "visible_effect": f"Used {card_id}" if additive else "none",
                "answer_delta": _static_delta(card_id if additive else ""),
            }
        )
    return {"answer_core": anchor, "private_micro_card_ledger": ledger}


def _static_delta(card_id: str) -> dict[str, list[str]]:
    if card_id == "single_cell_collaborator_feasibility_card":
        return {
            "added_entities": ["single-cell gaps"],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": ["Added technical feasibility gate for collaborator coverage."],
            "reframed_emphasis": [],
        }
    if card_id == "visible_stop_date_conditions_card":
        return {
            "added_entities": ["clear stop date with visible conditions"],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": ["Converted stop-loss into a dated no-go condition."],
            "reframed_emphasis": [],
        }
    return {field: [] for field in ANSWER_DELTA_FIELDS}


def _aggregate(case_results: Sequence[object]) -> dict[str, object]:
    rows = [row for row in case_results if isinstance(row, dict)]
    sample_count = len(rows)
    additive_count = sum(1 for row in rows if row.get("micro_card_signal") == "micro_card_additive_present")
    private_count = sum(1 for row in rows if row.get("micro_card_signal") == "all_private_or_confirming")
    missing_count = sum(1 for row in rows if row.get("micro_card_signal") == "missing_or_unclear")
    card_counts = {card_id: 0 for card_id in CARD_IDS}
    for row in rows:
        for card_id in row.get("additive_card_ids", []):
            if card_id in card_counts:
                card_counts[card_id] += 1
    protected_count = sum(
        1
        for row in rows
        if isinstance(row.get("protected_payload_presence"), dict)
        and all(row["protected_payload_presence"].values())
    )
    additive_card_sets = [
        set(row.get("additive_card_ids", []))
        for row in rows
        if row.get("micro_card_signal") == "micro_card_additive_present"
    ]
    has_proper_subset_use = any(0 < len(card_set) < len(CARD_IDS) for card_set in additive_card_sets)
    all_additive_rows_use_full_deck = bool(additive_card_sets) and all(
        len(card_set) == len(CARD_IDS) for card_set in additive_card_sets
    )
    if additive_count and has_proper_subset_use:
        discrimination = "discriminated"
    elif additive_count == sample_count and all_additive_rows_use_full_deck:
        discrimination = "bundle_like"
    elif private_count == sample_count:
        discrimination = "all_private"
    else:
        discrimination = "inconclusive"
    return {
        "sample_count": sample_count,
        "micro_card_additive_count": additive_count,
        "all_private_or_confirming_count": private_count,
        "missing_or_unclear_count": missing_count,
        "card_additive_counts": card_counts,
        "protected_payload_all_present_count": protected_count,
        "atomic_discrimination_read": discrimination,
        "runtime_promotion": "blocked",
        "skill_update": "blocked",
    }


def _micro_cards() -> list[dict[str, object]]:
    return [
        {
            "card_id": card_id,
            "cognitive_role": CARD_SPECS[card_id]["cognitive_role"],
            "receipts": list(CARD_SPECS[card_id]["receipts"]),
            "handling_rule": CARD_SPECS[card_id]["handling_rule"],
        }
        for card_id in CARD_IDS
    ]


def _anchor_text(*, root: Path) -> str:
    anchor = _read_json(Path(root) / ANCHOR_REF)
    if not isinstance(anchor, dict):
        raise PhdKimiVarianceCleaningReviewError("anchor payload must be object")
    return _string(anchor.get("answer_core"))


def _validate_header(payload: dict[str, object], *, path: Path, schema_version: str) -> Iterable[str]:
    if payload.get("schema_version") != schema_version:
        yield f"{path / 'schema_version'}: must be {schema_version}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if "promotion_effect" in payload and payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"


def _validate_scope(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, SCOPE_FIELDS, path)
    yield from _missing_fields(value, SCOPE_FIELDS, path)
    if value.get("v60_mode") != "off":
        yield f"{path / 'v60_mode'}: must be off"


def _validate_source_refs(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, SOURCE_REF_FIELDS, path)
    yield from _missing_fields(value, SOURCE_REF_FIELDS, path)


def _validate_sample_plan(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, SAMPLE_PLAN_FIELDS, path)
    yield from _missing_fields(value, SAMPLE_PLAN_FIELDS, path)
    if value.get("step6_model") != DEFAULT_MODEL:
        yield f"{path / 'step6_model'}: must be {DEFAULT_MODEL}"
    if value.get("sample_count") != DEFAULT_SAMPLE_COUNT:
        yield f"{path / 'sample_count'}: must be {DEFAULT_SAMPLE_COUNT}"


def _validate_micro_cards(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, list) or len(value) != len(CARD_IDS):
        yield f"{path}: must contain exactly {len(CARD_IDS)} cards"
        return
    ids = []
    for index, card in enumerate(value):
        card_path = path / str(index)
        if not isinstance(card, dict):
            yield f"{card_path}: must be object"
            continue
        yield from _unknown_fields(card, MICRO_CARD_FIELDS, card_path)
        yield from _missing_fields(card, MICRO_CARD_FIELDS, card_path)
        ids.append(card.get("card_id"))
        if not isinstance(card.get("receipts"), list) or not card.get("receipts"):
            yield f"{card_path / 'receipts'}: must be non-empty list"
    if ids != list(CARD_IDS):
        yield f"{path}: card ids must match expected order"


def _validate_provider_metadata(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, PROVIDER_METADATA_FIELDS, path)
    yield from _missing_fields(value, PROVIDER_METADATA_FIELDS, path)
    if not _string(value.get("status")).strip():
        yield f"{path / 'status'}: must be non-empty"


def _validate_input_packet(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, INPUT_PACKET_FIELDS, path)
    yield from _missing_fields(value, INPUT_PACKET_FIELDS, path)
    if not _string(value.get("anchor_visible_candidate")).strip():
        yield f"{path / 'anchor_visible_candidate'}: must be non-empty"
    if not isinstance(value.get("phd_cleaning_micro_cards"), list):
        yield f"{path / 'phd_cleaning_micro_cards'}: must be list"


def _validate_step6_output(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, STEP6_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, STEP6_OUTPUT_FIELDS, path)
    answer_core = _string(value.get("answer_core"))
    if not answer_core.strip():
        yield f"{path / 'answer_core'}: must be non-empty"
    try:
        validate_public_answer_hygiene(answer_core)
    except Exception as exc:  # pragma: no cover
        yield f"{path / 'answer_core'}: public hygiene failed: {exc}"
    ledger = value.get("private_micro_card_ledger")
    if not isinstance(ledger, list) or len(ledger) != len(CARD_IDS):
        yield f"{path / 'private_micro_card_ledger'}: must contain all cards"
        return
    for index, item in enumerate(ledger):
        yield from _validate_ledger_item(item, path / "private_micro_card_ledger" / str(index))


def _validate_ledger_item(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, LEDGER_FIELDS, path)
    yield from _missing_fields(value, LEDGER_FIELDS, path)
    if value.get("source_id") not in CARD_IDS:
        yield f"{path / 'source_id'}: invalid card id"
    for field in ("disposition", "novelty_role", "why", "visible_effect"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    yield from _validate_answer_delta(value.get("answer_delta"), path / "answer_delta")


def _validate_answer_delta(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, ANSWER_DELTA_FIELDS, path)
    yield from _missing_fields(value, ANSWER_DELTA_FIELDS, path)
    for field in ANSWER_DELTA_FIELDS:
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"


def _validate_case_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, CASE_RESULT_FIELDS, path)
    yield from _missing_fields(value, CASE_RESULT_FIELDS, path)
    if value.get("case_id") != CASE_ID:
        yield f"{path / 'case_id'}: must be {CASE_ID}"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    if not isinstance(value.get("card_additive_counts"), dict):
        yield f"{path / 'card_additive_counts'}: must be object"


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


def _normalize_answer_delta(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {field: [] for field in ANSWER_DELTA_FIELDS}
    return {
        field: [_string(item) for item in value.get(field, []) if _string(item).strip()]
        if isinstance(value.get(field), list)
        else []
        for field in ANSWER_DELTA_FIELDS
    }


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and any(_string(item).strip() for item in value)


def _complete_provider_metadata(metadata: dict[str, object]) -> dict[str, object]:
    completed = {
        "provider": "",
        "provider_name": "",
        "model": "",
        "model_family": "",
        "status": "",
        "finish_reason": "",
        "raw_message_content": "",
        "temperature": 0.0,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "cached_tokens": 0,
        "cache_write_tokens": 0,
        "reasoning_tokens": 0,
        "reasoning_disabled": False,
        "reasoning_details_present": False,
    }
    completed.update(metadata)
    if not completed["model_family"] and completed["model"]:
        completed["model_family"] = _string(completed["model"]).split("/", 1)[0]
    if not completed["provider_name"] and completed["provider"]:
        completed["provider_name"] = completed["provider"]
    return completed


def _provider_metadata_dict(metadata: object) -> dict[str, object]:
    if isinstance(metadata, dict):
        source = metadata
    else:
        source = {
            "provider": getattr(metadata, "provider", "openrouter"),
            "provider_name": getattr(metadata, "provider_name", "openrouter"),
            "model": getattr(metadata, "model", ""),
            "model_family": getattr(metadata, "model_family", ""),
            "status": getattr(metadata, "status", "ok"),
            "finish_reason": getattr(metadata, "finish_reason", ""),
            "raw_message_content": getattr(metadata, "raw_message_content", ""),
            "temperature": getattr(metadata, "temperature", 0.2),
            "prompt_tokens": getattr(metadata, "prompt_tokens", 0),
            "completion_tokens": getattr(metadata, "completion_tokens", 0),
            "total_tokens": getattr(metadata, "total_tokens", 0),
            "cached_tokens": getattr(metadata, "cached_tokens", 0),
            "cache_write_tokens": getattr(metadata, "cache_write_tokens", 0),
            "reasoning_tokens": getattr(metadata, "reasoning_tokens", 0),
            "reasoning_disabled": getattr(metadata, "reasoning_disabled", False),
            "reasoning_details_present": getattr(metadata, "reasoning_details_present", False),
        }
    return _complete_provider_metadata(dict(source))


def _blocked_gates() -> dict[str, bool]:
    return {"runtime_wiring_allowed": False, "skill_update_allowed": False}


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


def _load_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--write-sample", type=int)
    parser.add_argument("--write-result", action="store_true")
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise PhdKimiVarianceCleaningReviewError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == SCHEMA_VERSION:
                validate_phd_kimi_variance_cleaning_review_contract(payload, root=Path.cwd(), path=path)
            elif schema == SAMPLE_SCHEMA_VERSION:
                validate_phd_kimi_variance_cleaning_review_sample(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_phd_kimi_variance_cleaning_review_result(payload, path=path)
            else:
                raise PhdKimiVarianceCleaningReviewError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_phd_kimi_variance_cleaning_review_contract(args.contract)
        if args.contract
        else build_phd_kimi_variance_cleaning_review_contract(root=Path.cwd())
    )
    if args.write_contract:
        print(write_phd_kimi_variance_cleaning_review_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.write_sample is not None:
        path = run_live_phd_kimi_variance_cleaning_review_sample(
            contract=contract,
            sample_index=args.write_sample,
            provider=args.provider,
            model=args.model,
            env_file=args.env_file,
            out_dir=args.sample_dir,
            dry_run=args.dry_run,
        )
        if path is not None:
            print(path)
        return 0
    if args.write_result:
        samples = [
            load_phd_kimi_variance_cleaning_review_sample(path)
            for path in sorted(args.sample_dir.glob("*.phd-cleaning-review.v1.json"))
        ]
        result = build_phd_kimi_variance_cleaning_review_result(contract=contract, samples=samples)
        print(write_phd_kimi_variance_cleaning_review_result(payload=result, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
