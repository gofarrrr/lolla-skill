#!/usr/bin/env python3
"""Research-only replay for the Consultant cleaning variant.

This slice tests whether the cleaned Consultant table gives Step 6 clearer
material to think with. It is not a visibility gate and does not promote the
variant into runtime.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_consultant_deck_composition_review import (
    load_consultant_cleaning_variant,
    validate_consultant_cleaning_variant,
)
from pre_step6_raw_artifacts import validate_public_answer_hygiene


CONTRACT_SCHEMA_VERSION = "pre_step6_consultant_cleaning_variant_replay_contract.v1"
SAMPLE_SCHEMA_VERSION = "pre_step6_consultant_cleaning_variant_replay_sample.v1"
RESULT_SCHEMA_VERSION = "pre_step6_consultant_cleaning_variant_replay_result.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "consultant_cleaning_variant_replay_v0"
CASE_ID = "mid-level-consultant-report-2"
DEFAULT_OUT_DIR = Path("research/pre-step6-consultant-cleaning-variant-replay")
DEFAULT_SAMPLE_DIR = DEFAULT_OUT_DIR / "step6-samples"
DEFAULT_VARIANT_REF = (
    "research/pre-step6-consultant-deck-composition-review/"
    "consultant-cleaning-variant.v1.json"
)
DEFAULT_MODEL = "moonshotai/kimi-k2.6"
DEFAULT_SAMPLE_COUNT = 6
OLD_KIMI_UNLOCK_RATIO = 0.5
MICRO_CARD_IDS = (
    "counsel_independence_and_channel_bias_card",
    "wednesday_tripwire_preservation_card",
    "reversibility_until_counsel_boundary_card",
)
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "case_id",
        "source_refs",
        "sample_plan",
        "old_baseline",
        "gates",
        "notes",
    }
)
SOURCE_REF_FIELDS = frozenset({"consultant_cleaning_variant_ref"})
SAMPLE_PLAN_FIELDS = frozenset({"step6_model", "sample_count", "success_read"})
OLD_BASELINE_FIELDS = frozenset(
    {"old_kimi_unlock_ratio", "old_cleaning_read", "old_v60_status"}
)
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
        "protected_payload_presence",
        "deterministic_role",
        "gates",
        "notes",
    }
)
INPUT_PACKET_FIELDS = frozenset(
    {"anchor_visible_candidate", "cleaning_micro_cards", "success_read"}
)
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
        "protected_payload_presence",
        "used_micro_cards",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "sample_count",
        "micro_card_additive_count",
        "all_private_or_confirming_count",
        "missing_or_unclear_count",
        "unlock_ratio",
        "old_kimi_unlock_ratio",
        "consideration_stability_read",
        "cleaning_improvement_read",
        "protected_payload_all_present_count",
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
CONCRETE_DELTA_FIELDS = ("added_entities", "removed_entities", "reordered_sequences")
STRUCTURAL_MARKERS = (
    "boundary",
    "condition",
    "criteria",
    "gate",
    "preserve",
    "protocol",
    "sequence",
    "stop",
    "test",
    "tripwire",
    "until",
)
DETERMINISTIC_ROLE = (
    "validate_cleaning_variant",
    "derive_micro_card_signal",
    "derive_answer_delta_specificity",
    "check_protected_payload_presence",
    "preserve_replay_custody",
)


class ConsultantCleaningVariantReplayError(ValueError):
    pass


def build_consultant_cleaning_variant_replay_contract(*, root: Path) -> dict[str, object]:
    variant = load_consultant_cleaning_variant(Path(root) / DEFAULT_VARIANT_REF)
    validate_consultant_cleaning_variant(variant)
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_id": CASE_ID,
        "source_refs": {"consultant_cleaning_variant_ref": DEFAULT_VARIANT_REF},
        "sample_plan": {
            "step6_model": DEFAULT_MODEL,
            "sample_count": DEFAULT_SAMPLE_COUNT,
            "success_read": (
                "Compare consideration stability and protected payload preservation "
                "against the old Consultant deck; not a visibility-promotion gate."
            ),
        },
        "old_baseline": {
            "old_kimi_unlock_ratio": OLD_KIMI_UNLOCK_RATIO,
            "old_cleaning_read": "anchor_strong_deck_pressure_thin_but_useful",
            "old_v60_status": "not_active",
        },
        "gates": _blocked_gates(),
        "notes": (
            "Research-only replay contract for the Consultant cleaning variant. "
            "The replay measures Step 6 consideration clarity, not runtime visibility."
        ),
    }
    validate_consultant_cleaning_variant_replay_contract(payload, root=root)
    return payload


def write_consultant_cleaning_variant_replay_contract(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_cleaning_variant_replay_contract(payload, root=Path.cwd())
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consultant-cleaning-variant-replay-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_consultant_cleaning_variant_replay_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ConsultantCleaningVariantReplayError(f"{path}: payload must be object")
    return payload


def build_consultant_cleaning_variant_replay_prompts(
    *,
    contract: dict[str, object],
    sample_index: int,
) -> dict[str, str]:
    validate_consultant_cleaning_variant_replay_contract(contract, root=Path.cwd())
    variant = _variant_for_contract(contract, Path.cwd())
    micro_cards = [
        {
            "card_id": card["card_id"],
            "cognitive_role": card["cognitive_role"],
            "receipts": card["receipts"],
            "handling_rule": card["handling_rule"],
            "misuse_guard": card["misuse_guard"],
            "standdown_condition": card["standdown_condition"],
        }
        for card in variant["micro_cards"]
    ]
    system_prompt = (
        "You are Step 6, the primary reasoning voice. You receive a cleaned "
        "private table and decide what the user should see. Use your cognition; "
        "the cards are pressure atoms, not commands. Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            "CONSULTANT CLEANING VARIANT REPLAY",
            json.dumps(
                {
                    "case_id": CASE_ID,
                    "sample_index": sample_index,
                    "anchor_visible_candidate": _anchor_text(variant),
                    "cleaning_micro_cards": micro_cards,
                    "success_read": contract["sample_plan"]["success_read"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            "TASK",
            (
                "Write the best public-clean answer_core. Keep the anchor as "
                "backbone unless a micro-card improves it. You may use, combine, "
                "reject, defer, or keep private any micro-card. Preserve counsel-first "
                "sequencing, no-confrontation, no private investigation, attorney "
                "intake/channel-bias testing, Wednesday behavior, partner-encounter "
                "tripwires, and reversibility. Do not expose private labels."
            ),
            "RESPONSE JSON SHAPE",
            json.dumps(
                {
                    "answer_core": "Public-clean answer.",
                    "private_micro_card_ledger": [
                        {
                            "source_id": (
                                "counsel_independence_and_channel_bias_card | "
                                "wednesday_tripwire_preservation_card | "
                                "reversibility_until_counsel_boundary_card"
                            ),
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
                                "structural_delta": [
                                    (
                                        "Specific structural change such as a boundary, "
                                        "tripwire preservation, protocol, or stop condition."
                                    )
                                ],
                                "reframed_emphasis": ["Tone or emphasis shifts."],
                            },
                        }
                    ],
                },
                indent=2,
            ),
        ]
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def build_static_consultant_cleaning_variant_replay_sample(
    *,
    contract: dict[str, object],
    sample_index: int,
    micro_card_signal: str,
    answer_delta_specificity: str,
) -> dict[str, object]:
    validate_consultant_cleaning_variant_replay_contract(contract, root=Path.cwd())
    variant = _variant_for_contract(contract, Path.cwd())
    output = _static_output(
        variant=variant,
        micro_card_signal=micro_card_signal,
        answer_delta_specificity=answer_delta_specificity,
    )
    sample = _sample_payload(
        contract=contract,
        variant=variant,
        sample_index=sample_index,
        provider_metadata={
            "provider": "static",
            "provider_name": "static",
            "model": "static-consultant-cleaning-variant",
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
        notes="Static Consultant cleaning variant replay sample.",
    )
    validate_consultant_cleaning_variant_replay_sample(sample)
    return sample


def run_live_consultant_cleaning_variant_replay_sample(
    *,
    contract: dict[str, object],
    sample_index: int,
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    dry_run: bool,
) -> Path | None:
    validate_consultant_cleaning_variant_replay_contract(contract, root=Path.cwd())
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    prompts = build_consultant_cleaning_variant_replay_prompts(
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
        stage="pre_step6_consultant_cleaning_variant_replay",
        tendency_id=f"{CASE_ID}:sample-{sample_index}",
    )
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise ConsultantCleaningVariantReplayError(
            "live Consultant cleaning variant replay failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    variant = _variant_for_contract(contract, Path.cwd())
    sample = _sample_payload(
        contract=contract,
        variant=variant,
        sample_index=sample_index,
        provider_metadata=provider_metadata,
        step6_output=normalize_consultant_cleaning_variant_step6_output(output),
        notes="Live research-only Consultant cleaning variant replay sample.",
    )
    return write_consultant_cleaning_variant_replay_sample(payload=sample, out_dir=out_dir)


def build_consultant_cleaning_variant_replay_result(
    *,
    contract: dict[str, object],
    samples: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_consultant_cleaning_variant_replay_contract(contract, root=Path.cwd())
    for sample in samples:
        validate_consultant_cleaning_variant_replay_sample(sample)
    case_results = [
        {
            "case_id": _string(sample["case_id"]),
            "sample_index": sample["sample_index"],
            "micro_card_signal": sample["micro_card_signal"],
            "answer_delta_specificity": sample["answer_delta_specificity"],
            "protected_payload_presence": sample["protected_payload_presence"],
            "used_micro_cards": _used_micro_cards(sample["step6_output"]),
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
            "Aggregate for Consultant cleaning variant replay. Measures Step 6 "
            "consideration stability and payload preservation; does not choose visibility."
        ),
    }
    validate_consultant_cleaning_variant_replay_result(payload)
    return payload


def write_consultant_cleaning_variant_replay_result(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_cleaning_variant_replay_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consultant-cleaning-variant-replay-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_consultant_cleaning_variant_replay_sample(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_cleaning_variant_replay_sample(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = replay_sample_path(out_dir=out_dir, sample_index=int(payload["sample_index"]))
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def replay_sample_path(*, out_dir: Path, sample_index: int) -> Path:
    return out_dir / f"{CASE_ID}.sample-{sample_index}.consultant-cleaning-replay.v1.json"


def load_consultant_cleaning_variant_replay_sample(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ConsultantCleaningVariantReplayError(f"{path}: payload must be object")
    return payload


def validate_consultant_cleaning_variant_replay_contract(
    payload: dict[str, object],
    *,
    root: Path | None = None,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(
        iter_consultant_cleaning_variant_replay_contract_errors(payload, root=root, path=path)
    )
    if errors:
        raise ConsultantCleaningVariantReplayError("; ".join(errors))


def iter_consultant_cleaning_variant_replay_contract_errors(
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
    yield from _validate_header(payload, path=path, schema_version=CONTRACT_SCHEMA_VERSION)
    if payload.get("case_id") != CASE_ID:
        yield f"{path / 'case_id'}: must be {CASE_ID}"
    yield from _validate_source_refs(payload.get("source_refs"), path / "source_refs")
    if root is not None and isinstance(payload.get("source_refs"), dict):
        variant_ref = _string(payload["source_refs"].get("consultant_cleaning_variant_ref"))
        variant_path = Path(root) / variant_ref
        if not variant_path.exists():
            yield f"{path / 'source_refs' / 'consultant_cleaning_variant_ref'}: missing file"
    yield from _validate_sample_plan(payload.get("sample_plan"), path / "sample_plan")
    yield from _validate_old_baseline(payload.get("old_baseline"), path / "old_baseline")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_consultant_cleaning_variant_replay_sample(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_cleaning_variant_replay_sample_errors(payload, path=path))
    if errors:
        raise ConsultantCleaningVariantReplayError("; ".join(errors))


def iter_consultant_cleaning_variant_replay_sample_errors(
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
    if not isinstance(payload.get("protected_payload_presence"), dict):
        yield f"{path / 'protected_payload_presence'}: must be object"
    if payload.get("deterministic_role") != list(DETERMINISTIC_ROLE):
        yield f"{path / 'deterministic_role'}: must preserve deterministic role"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_consultant_cleaning_variant_replay_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_cleaning_variant_replay_result_errors(payload, path=path))
    if errors:
        raise ConsultantCleaningVariantReplayError("; ".join(errors))


def iter_consultant_cleaning_variant_replay_result_errors(
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
    yield from _validate_gates(payload.get("gates"), path / "gates")


def normalize_consultant_cleaning_variant_step6_output(value: object) -> dict[str, object]:
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
    for source_id in MICRO_CARD_IDS:
        item = by_source.get(source_id, {})
        normalized.append(
            {
                "source_id": source_id,
                "disposition": _string(item.get("disposition")) or "deferred",
                "novelty_role": _string(item.get("novelty_role")) or "confirming_support",
                "why": _string(item.get("why")) or "Model did not explain this micro-card.",
                "visible_effect": _string(item.get("visible_effect")) or "none",
                "answer_delta": _normalize_answer_delta(item.get("answer_delta")),
            }
        )
    return {"answer_core": _string(value.get("answer_core")), "private_micro_card_ledger": normalized}


def derive_micro_card_signal(step6_output: object) -> str:
    if not isinstance(step6_output, dict):
        return "missing_or_unclear"
    ledger = step6_output.get("private_micro_card_ledger")
    if not isinstance(ledger, list):
        return "missing_or_unclear"
    micro_items = [item for item in ledger if isinstance(item, dict)]
    if not micro_items:
        return "missing_or_unclear"
    for item in micro_items:
        if (
            item.get("novelty_role") == "additive_pressure"
            and item.get("disposition") in {"used", "combined"}
        ):
            return "micro_card_additive_present"
    if all(
        item.get("novelty_role") in {"confirming_support", "private_guardrail"}
        or item.get("disposition") in {"rejected", "deferred", "private_guardrail"}
        for item in micro_items
    ):
        return "all_private_or_confirming"
    return "missing_or_unclear"


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
        if any(_non_empty_string_list(delta.get(field)) for field in CONCRETE_DELTA_FIELDS):
            return "concrete_delta_present"
        if _specific_structural_delta_present(delta.get("structural_delta")):
            return "structural_delta_present"
        if _non_empty_string_list(delta.get("reframed_emphasis")):
            saw_reframe = True
    return "reframe_only" if saw_reframe else "missing_or_unclear"


def protected_payload_presence(answer_core: str) -> dict[str, bool]:
    lowered = answer_core.lower()
    return {
        "counsel_or_attorney_present": "counsel" in lowered or "attorney" in lowered,
        "no_confrontation_present": "confront" in lowered,
        "no_private_investigation_present": "investigat" in lowered,
        "channel_not_self_selected_present": "channel" in lowered
        or "internal" in lowered
        or "external" in lowered,
        "wednesday_protocol_present": "wednesday" in lowered,
        "deny_tripwire_present": "deny" in lowered,
        "reversibility_present": "reversible" in lowered or "until counsel" in lowered,
    }


def _sample_payload(
    *,
    contract: dict[str, object],
    variant: dict[str, object],
    sample_index: int,
    provider_metadata: dict[str, object],
    step6_output: dict[str, object],
    notes: str,
) -> dict[str, object]:
    normalized = normalize_consultant_cleaning_variant_step6_output(step6_output)
    signal = derive_micro_card_signal(normalized)
    specificity = derive_answer_delta_specificity(normalized)
    payload = {
        "schema_version": SAMPLE_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": CASE_ID,
        "sample_index": sample_index,
        "provider_metadata": _complete_provider_metadata(provider_metadata),
        "input_packet": {
            "anchor_visible_candidate": _anchor_text(variant),
            "cleaning_micro_cards": _prompt_micro_cards(variant),
            "success_read": contract["sample_plan"]["success_read"],
        },
        "step6_output": normalized,
        "micro_card_signal": signal,
        "answer_delta_specificity": specificity,
        "protected_payload_presence": protected_payload_presence(_string(normalized.get("answer_core"))),
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": _blocked_gates(),
        "notes": notes,
    }
    validate_consultant_cleaning_variant_replay_sample(payload)
    return payload


def _static_output(
    *,
    variant: dict[str, object],
    micro_card_signal: str,
    answer_delta_specificity: str,
) -> dict[str, object]:
    ledger = []
    for card_id in MICRO_CARD_IDS:
        additive = micro_card_signal == "micro_card_additive_present" and card_id == MICRO_CARD_IDS[0]
        ledger.append(
            {
                "source_id": card_id,
                "disposition": "combined" if additive else "deferred",
                "novelty_role": "additive_pressure" if additive else "confirming_support",
                "why": "Static replay fixture.",
                "visible_effect": "Added independent counsel and bias check." if additive else "none",
                "answer_delta": _static_delta(answer_delta_specificity if additive else "not_applicable"),
            }
        )
    return {"answer_core": _anchor_text(variant), "private_micro_card_ledger": ledger}


def _static_delta(answer_delta_specificity: str) -> dict[str, list[str]]:
    if answer_delta_specificity == "concrete_delta_present":
        return {
            "added_entities": ["independent counsel"],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": [],
            "reframed_emphasis": [],
        }
    if answer_delta_specificity == "structural_delta_present":
        return {
            "added_entities": [],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": ["added boundary: early steps stay reversible until counsel guides"],
            "reframed_emphasis": [],
        }
    if answer_delta_specificity == "reframe_only":
        return {
            "added_entities": [],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": [],
            "reframed_emphasis": ["clearer channel-bias framing"],
        }
    return _empty_answer_delta()


def _aggregate(case_results: Sequence[object]) -> dict[str, object]:
    rows = [row for row in case_results if isinstance(row, dict)]
    sample_count = len(rows)
    additive_count = sum(
        1 for row in rows if row.get("micro_card_signal") == "micro_card_additive_present"
    )
    private_count = sum(
        1 for row in rows if row.get("micro_card_signal") == "all_private_or_confirming"
    )
    missing_count = sum(1 for row in rows if row.get("micro_card_signal") == "missing_or_unclear")
    if sample_count and additive_count == sample_count:
        stability = "stable_additive"
    elif sample_count and private_count == sample_count:
        stability = "stable_private_or_confirming"
    elif sample_count:
        stability = "mixed"
    else:
        stability = "not_sampled"
    unlock_ratio = round(additive_count / sample_count, 3) if sample_count else 0.0
    if stability != "mixed" and sample_count:
        improvement = "cleaner_consideration_than_old_deck"
    elif unlock_ratio != OLD_KIMI_UNLOCK_RATIO:
        improvement = "changed_but_still_mixed"
    else:
        improvement = "no_stability_improvement_observed"
    protected_all = sum(
        1
        for row in rows
        if isinstance(row.get("protected_payload_presence"), dict)
        and all(row["protected_payload_presence"].values())
    )
    return {
        "sample_count": sample_count,
        "micro_card_additive_count": additive_count,
        "all_private_or_confirming_count": private_count,
        "missing_or_unclear_count": missing_count,
        "unlock_ratio": unlock_ratio,
        "old_kimi_unlock_ratio": OLD_KIMI_UNLOCK_RATIO,
        "consideration_stability_read": stability,
        "cleaning_improvement_read": improvement,
        "protected_payload_all_present_count": protected_all,
        "runtime_promotion": "blocked",
        "skill_update": "blocked",
    }


def _variant_for_contract(contract: dict[str, object], root: Path) -> dict[str, object]:
    refs = contract.get("source_refs")
    if not isinstance(refs, dict):
        raise ConsultantCleaningVariantReplayError("source_refs missing")
    variant = load_consultant_cleaning_variant(root / _string(refs.get("consultant_cleaning_variant_ref")))
    validate_consultant_cleaning_variant(variant)
    return variant


def _anchor_text(variant: dict[str, object]) -> str:
    refs = variant.get("source_refs")
    if isinstance(refs, dict):
        anchor_ref = _string(refs.get("anchor_ref"))
        if anchor_ref:
            anchor = _read_json(Path.cwd() / anchor_ref)
            if isinstance(anchor, dict):
                return _string(anchor.get("answer_core"))
    return ""


def _prompt_micro_cards(variant: dict[str, object]) -> list[dict[str, object]]:
    cards = variant.get("micro_cards")
    if not isinstance(cards, list):
        return []
    return [
        {
            "card_id": card.get("card_id"),
            "cognitive_role": card.get("cognitive_role"),
            "receipts": card.get("receipts"),
            "handling_rule": card.get("handling_rule"),
            "misuse_guard": card.get("misuse_guard"),
            "standdown_condition": card.get("standdown_condition"),
        }
        for card in cards
        if isinstance(card, dict)
    ]


def _used_micro_cards(step6_output: object) -> list[str]:
    if not isinstance(step6_output, dict):
        return []
    ledger = step6_output.get("private_micro_card_ledger")
    if not isinstance(ledger, list):
        return []
    return sorted(
        {
            _string(item.get("source_id"))
            for item in ledger
            if isinstance(item, dict) and item.get("disposition") in {"used", "combined"}
        }
    )


def _validate_header(
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
    if "promotion_effect" in payload and payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"


def _validate_source_refs(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, SOURCE_REF_FIELDS, path)
    yield from _missing_fields(value, SOURCE_REF_FIELDS, path)
    if not _string(value.get("consultant_cleaning_variant_ref")).strip():
        yield f"{path / 'consultant_cleaning_variant_ref'}: must be non-empty"


def _validate_sample_plan(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, SAMPLE_PLAN_FIELDS, path)
    yield from _missing_fields(value, SAMPLE_PLAN_FIELDS, path)
    if not _string(value.get("step6_model")).strip():
        yield f"{path / 'step6_model'}: must be non-empty"
    if not isinstance(value.get("sample_count"), int) or value.get("sample_count") <= 0:
        yield f"{path / 'sample_count'}: must be positive integer"
    if not _string(value.get("success_read")).strip():
        yield f"{path / 'success_read'}: must be non-empty"


def _validate_old_baseline(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, OLD_BASELINE_FIELDS, path)
    yield from _missing_fields(value, OLD_BASELINE_FIELDS, path)
    if not isinstance(value.get("old_kimi_unlock_ratio"), float):
        yield f"{path / 'old_kimi_unlock_ratio'}: must be float"


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
    if not isinstance(value.get("cleaning_micro_cards"), list) or not value.get("cleaning_micro_cards"):
        yield f"{path / 'cleaning_micro_cards'}: must be non-empty list"


def _validate_step6_output(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, STEP6_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, STEP6_OUTPUT_FIELDS, path)
    if not _string(value.get("answer_core")).strip():
        yield f"{path / 'answer_core'}: must be non-empty"
    try:
        validate_public_answer_hygiene(_string(value.get("answer_core")))
    except Exception as exc:  # pragma: no cover - only emits validation text
        yield f"{path / 'answer_core'}: public hygiene failed: {exc}"
    ledger = value.get("private_micro_card_ledger")
    if not isinstance(ledger, list) or len(ledger) != len(MICRO_CARD_IDS):
        yield f"{path / 'private_micro_card_ledger'}: must contain all micro cards"
        return
    for index, item in enumerate(ledger):
        yield from _validate_ledger_item(item, path / "private_micro_card_ledger" / str(index))


def _validate_ledger_item(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, LEDGER_FIELDS, path)
    yield from _missing_fields(value, LEDGER_FIELDS, path)
    if value.get("source_id") not in MICRO_CARD_IDS:
        yield f"{path / 'source_id'}: invalid micro-card id"
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
    if value.get("micro_card_signal") not in ALLOWED_MICRO_CARD_SIGNALS:
        yield f"{path / 'micro_card_signal'}: invalid signal"
    if value.get("answer_delta_specificity") not in ALLOWED_ANSWER_DELTA_SPECIFICITY:
        yield f"{path / 'answer_delta_specificity'}: invalid specificity"
    if not isinstance(value.get("protected_payload_presence"), dict):
        yield f"{path / 'protected_payload_presence'}: must be object"
    if not isinstance(value.get("used_micro_cards"), list):
        yield f"{path / 'used_micro_cards'}: must be list"


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


def _normalize_answer_delta(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return _empty_answer_delta()
    return {
        field: [_string(item) for item in value.get(field, []) if _string(item).strip()]
        if isinstance(value.get(field), list)
        else []
        for field in ANSWER_DELTA_FIELDS
    }


def _empty_answer_delta() -> dict[str, list[str]]:
    return {field: [] for field in ANSWER_DELTA_FIELDS}


def _specific_structural_delta_present(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return any(
        any(marker in _string(item).lower() for marker in STRUCTURAL_MARKERS)
        for item in value
    )


def _non_empty_string_list(value: object) -> bool:
    return isinstance(value, list) and any(_string(item).strip() for item in value)


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
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


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
                raise ConsultantCleaningVariantReplayError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_consultant_cleaning_variant_replay_contract(payload, root=Path.cwd(), path=path)
            elif schema == SAMPLE_SCHEMA_VERSION:
                validate_consultant_cleaning_variant_replay_sample(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_consultant_cleaning_variant_replay_result(payload, path=path)
            else:
                raise ConsultantCleaningVariantReplayError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_consultant_cleaning_variant_replay_contract(args.contract)
        if args.contract
        else build_consultant_cleaning_variant_replay_contract(root=Path.cwd())
    )
    if args.write_contract:
        print(write_consultant_cleaning_variant_replay_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.write_sample is not None:
        path = run_live_consultant_cleaning_variant_replay_sample(
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
            load_consultant_cleaning_variant_replay_sample(path)
            for path in sorted(args.sample_dir.glob("*.consultant-cleaning-replay.v1.json"))
        ]
        result = build_consultant_cleaning_variant_replay_result(
            contract=contract,
            samples=samples,
        )
        print(write_consultant_cleaning_variant_replay_result(payload=result, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
