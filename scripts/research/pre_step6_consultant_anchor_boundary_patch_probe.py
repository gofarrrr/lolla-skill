#!/usr/bin/env python3
"""Research-only Consultant anchor-boundary patch probe.

This slice tests a graduation hypothesis for one recurring pressure atom:
whether the Consultant anchor already carrying "until counsel guides the next
action" lets the same reversibility micro-card stand down. The patch is an
experimental instrument, not a proposed per-case architecture.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_consultant_cleaning_variant_replay import (
    DEFAULT_MODEL,
    DEFAULT_SAMPLE_COUNT,
    MICRO_CARD_IDS,
    derive_answer_delta_specificity,
    derive_micro_card_signal,
    normalize_consultant_cleaning_variant_step6_output,
    protected_payload_presence,
)
from pre_step6_consultant_deck_composition_review import (
    load_consultant_cleaning_variant,
    validate_consultant_cleaning_variant,
)
from pre_step6_raw_artifacts import validate_public_answer_hygiene


CONTRACT_SCHEMA_VERSION = "pre_step6_consultant_anchor_boundary_patch_probe_contract.v1"
SAMPLE_SCHEMA_VERSION = "pre_step6_consultant_anchor_boundary_patch_probe_sample.v1"
RESULT_SCHEMA_VERSION = "pre_step6_consultant_anchor_boundary_patch_probe_result.v1"
STATUS = "research_only"
RUNTIME_POLICY = "runtime_dormant"
EXPERIMENT_ID = "consultant_anchor_boundary_patch_probe_v0"
CASE_ID = "mid-level-consultant-report-2"
DEFAULT_OUT_DIR = Path("research/pre-step6-consultant-anchor-boundary-patch-probe")
DEFAULT_SAMPLE_DIR = DEFAULT_OUT_DIR / "step6-samples"
DEFAULT_VARIANT_REF = (
    "research/pre-step6-consultant-deck-composition-review/"
    "consultant-cleaning-variant.v1.json"
)
PATCH_PHRASE = "keep the first moves reversible until counsel guides the next action"
ORIGINAL_BOUNDARY_PHRASE = "keep the first moves reversible"
PREFLIGHT_CHECKLIST = (
    "makes_step6_table_better",
    "preserves_broad_private_edge",
    "keeps_cognition_in_step6_or_human_review",
    "avoids_automatic_wisdom_from_recurrence",
    "learns_upstream_rather_than_suppressing_context",
)
OUTCOME_STATES = frozenset({"yes", "no", "mixed", "unobserved"})
NEXT_INVESTIGATIONS = frozenset(
    {"substrate", "lane", "synthesis", "anchor_wording", "further_probe_needed", "none"}
)
CONSULTANT_CLASSIFICATIONS = frozenset(
    {"graduation_candidate", "card_needed", "borderline_by_design", "inconclusive_parked"}
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
        "patch",
        "sample_plan",
        "preflight_checklist",
        "decision_tree",
        "gates",
        "notes",
    }
)
SOURCE_REF_FIELDS = frozenset({"consultant_cleaning_variant_ref", "source_replay_result_ref"})
PATCH_FIELDS = frozenset(
    {
        "patch_phrase",
        "original_phrase",
        "placement",
        "allowed_change",
        "non_purpose",
    }
)
SAMPLE_PLAN_FIELDS = frozenset(
    {"step6_model", "sample_count", "max_wording_reruns_on_unobserved", "success_read"}
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
        "reversibility_card_additive",
        "patched_boundary_in_answer",
        "protected_payload_presence",
        "deterministic_role",
        "gates",
        "notes",
    }
)
INPUT_PACKET_FIELDS = frozenset(
    {
        "original_anchor_visible_candidate",
        "patched_anchor_visible_candidate",
        "patch_phrase",
        "cleaning_micro_cards",
        "success_read",
    }
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
        "reversibility_card_additive",
        "patched_boundary_in_answer",
        "protected_payload_presence",
        "used_micro_cards",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "sample_count",
        "micro_card_standdown_count",
        "micro_card_standdown_rate",
        "micro_card_additive_count",
        "missing_or_unclear_count",
        "reversibility_card_additive_count",
        "reversibility_card_additive_rate",
        "patched_boundary_present_count",
        "protected_payload_all_present_count",
        "protected_payload_preserved",
        "upstream_pressure_carried",
        "next_investigation",
        "consultant_classification",
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
    "validate_cleaning_variant",
    "apply_minimal_anchor_patch_for_hypothesis_test",
    "derive_micro_card_signal",
    "derive_reversibility_card_additive",
    "check_patched_boundary_presence",
    "check_protected_payload_presence",
    "preserve_patch_probe_custody",
)


class ConsultantAnchorBoundaryPatchProbeError(ValueError):
    pass


def build_consultant_anchor_boundary_patch_probe_contract(*, root: Path) -> dict[str, object]:
    variant = _load_variant(root=root)
    original_anchor = _anchor_text(variant, root=root)
    patched_anchor = patched_consultant_anchor(original_anchor)
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_id": CASE_ID,
        "source_refs": {
            "consultant_cleaning_variant_ref": DEFAULT_VARIANT_REF,
            "source_replay_result_ref": (
                "research/pre-step6-consultant-cleaning-variant-replay/"
                "consultant-cleaning-variant-replay-result.v1.json"
            ),
        },
        "patch": {
            "patch_phrase": PATCH_PHRASE,
            "original_phrase": ORIGINAL_BOUNDARY_PHRASE,
            "placement": "hypothesis_test_not_architecture",
            "allowed_change": "one_phrase_only_no_style_rewrite",
            "non_purpose": [
                "not_a_per_case_patch_architecture",
                "not_visibility_policy",
                "not_runtime_promotion",
                "not_skill_update",
            ],
        },
        "sample_plan": {
            "step6_model": DEFAULT_MODEL,
            "sample_count": DEFAULT_SAMPLE_COUNT,
            "max_wording_reruns_on_unobserved": 1,
            "success_read": (
                "Test whether the recurring reversibility-until-counsel pressure is "
                "carried by the patched anchor so the same micro-card can stand down."
            ),
        },
        "preflight_checklist": list(PREFLIGHT_CHECKLIST),
        "decision_tree": {
            "yes": "classify Consultant as graduation_candidate and investigate upstream origin.",
            "no": "classify Consultant as card_needed or anchor_wording_failed; no permanent patch layer.",
            "mixed": "classify Consultant as borderline_by_design and stop Consultant refinement.",
            "unobserved": "allow at most one operator-reviewed wording rerun; if still unobserved, park.",
        },
        "gates": _blocked_gates(),
        "notes": (
            "The patched anchor is a hypothesis-test input. If it works, the next "
            "question is why the existing pipeline did not surface this pressure "
            "naturally."
        ),
    }
    if PATCH_PHRASE not in patched_anchor:
        raise ConsultantAnchorBoundaryPatchProbeError("patched anchor did not include patch phrase")
    validate_consultant_anchor_boundary_patch_probe_contract(payload, root=root)
    return payload


def patched_consultant_anchor(original_anchor: str) -> str:
    phrase = ORIGINAL_BOUNDARY_PHRASE
    patched = PATCH_PHRASE
    if patched in original_anchor:
        return original_anchor
    exact_sentence = f"{phrase}."
    if exact_sentence in original_anchor:
        return original_anchor.replace(exact_sentence, f"{patched}.", 1)
    if phrase in original_anchor:
        return original_anchor.replace(phrase, patched, 1)
    return original_anchor.rstrip() + f" Keep the first moves reversible until counsel guides the next action."


def write_consultant_anchor_boundary_patch_probe_contract(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_anchor_boundary_patch_probe_contract(payload, root=Path.cwd())
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consultant-anchor-boundary-patch-probe-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_consultant_anchor_boundary_patch_probe_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ConsultantAnchorBoundaryPatchProbeError(f"{path}: payload must be object")
    return payload


def build_consultant_anchor_boundary_patch_probe_prompts(
    *,
    contract: dict[str, object],
    sample_index: int,
) -> dict[str, str]:
    validate_consultant_anchor_boundary_patch_probe_contract(contract, root=Path.cwd())
    variant = _variant_for_contract(contract=contract, root=Path.cwd())
    original_anchor = _anchor_text(variant, root=Path.cwd())
    patched_anchor = patched_consultant_anchor(original_anchor)
    system_prompt = (
        "You are Step 6, the primary reasoning voice. You receive a patched "
        "anchor candidate and private micro-cards. Use cognition; the patch is "
        "only an experiment. Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            "CONSULTANT ANCHOR BOUNDARY PATCH PROBE",
            json.dumps(
                {
                    "case_id": CASE_ID,
                    "sample_index": sample_index,
                    "probe_frame": (
                        "This is a hypothesis test, not a patch architecture. "
                        "If the patched anchor already carries a micro-card's "
                        "pressure, keep that card private or confirming."
                    ),
                    "original_anchor_visible_candidate": original_anchor,
                    "patched_anchor_visible_candidate": patched_anchor,
                    "patch_phrase": PATCH_PHRASE,
                    "cleaning_micro_cards": _prompt_micro_cards(variant),
                    "success_read": contract["sample_plan"]["success_read"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            "TASK",
            (
                "Write the best public-clean answer_core using the patched anchor "
                "as the visible backbone. Keep the same three micro-cards available "
                "as private pressure atoms. Preserve broad private edge: you may "
                "use, combine, reject, defer, or keep private each micro-card. "
                "Do not expose private labels. Do not add legal certainty. Preserve "
                "counsel-first sequencing, no confrontation, no private investigation, "
                "attorney intake/channel-bias testing, Wednesday behavior, partner "
                "tripwires, and reversibility."
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
                                    "Specific boundary, protocol, tripwire, or stop condition."
                                ],
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


def build_static_consultant_anchor_boundary_patch_probe_sample(
    *,
    contract: dict[str, object],
    sample_index: int,
    micro_card_signal: str,
    reversibility_card_additive: bool,
    patched_boundary_in_answer: bool,
) -> dict[str, object]:
    validate_consultant_anchor_boundary_patch_probe_contract(contract, root=Path.cwd())
    variant = _variant_for_contract(contract=contract, root=Path.cwd())
    output = _static_output(
        variant=variant,
        micro_card_signal=micro_card_signal,
        reversibility_card_additive=reversibility_card_additive,
        patched_boundary_in_answer=patched_boundary_in_answer,
    )
    sample = _sample_payload(
        contract=contract,
        variant=variant,
        sample_index=sample_index,
        provider_metadata={
            "provider": "static",
            "provider_name": "static",
            "model": "static-consultant-anchor-boundary-patch",
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
        notes="Static Consultant anchor boundary patch probe sample.",
    )
    validate_consultant_anchor_boundary_patch_probe_sample(sample)
    return sample


def run_live_consultant_anchor_boundary_patch_probe_sample(
    *,
    contract: dict[str, object],
    sample_index: int,
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    dry_run: bool,
) -> Path | None:
    validate_consultant_anchor_boundary_patch_probe_contract(contract, root=Path.cwd())
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    prompts = build_consultant_anchor_boundary_patch_probe_prompts(
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
        stage="pre_step6_consultant_anchor_boundary_patch_probe",
        tendency_id=f"{CASE_ID}:sample-{sample_index}",
    )
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise ConsultantAnchorBoundaryPatchProbeError(
            "live Consultant anchor boundary patch probe failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    variant = _variant_for_contract(contract=contract, root=Path.cwd())
    sample = _sample_payload(
        contract=contract,
        variant=variant,
        sample_index=sample_index,
        provider_metadata=provider_metadata,
        step6_output=normalize_consultant_cleaning_variant_step6_output(output),
        notes="Live research-only Consultant anchor boundary patch probe sample.",
    )
    return write_consultant_anchor_boundary_patch_probe_sample(payload=sample, out_dir=out_dir)


def build_consultant_anchor_boundary_patch_probe_result(
    *,
    contract: dict[str, object],
    samples: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_consultant_anchor_boundary_patch_probe_contract(contract, root=Path.cwd())
    for sample in samples:
        validate_consultant_anchor_boundary_patch_probe_sample(sample)
    case_results = [
        {
            "case_id": _string(sample["case_id"]),
            "sample_index": sample["sample_index"],
            "micro_card_signal": sample["micro_card_signal"],
            "answer_delta_specificity": sample["answer_delta_specificity"],
            "reversibility_card_additive": sample["reversibility_card_additive"],
            "patched_boundary_in_answer": sample["patched_boundary_in_answer"],
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
            "Aggregate for the Consultant anchor-boundary patch probe. It tests "
            "whether a recurring pressure atom looks graduation-eligible; it does "
            "not propose a runtime patch layer."
        ),
    }
    validate_consultant_anchor_boundary_patch_probe_result(payload)
    return payload


def write_consultant_anchor_boundary_patch_probe_result(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_anchor_boundary_patch_probe_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "consultant-anchor-boundary-patch-probe-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_consultant_anchor_boundary_patch_probe_sample(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_consultant_anchor_boundary_patch_probe_sample(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = patch_probe_sample_path(out_dir=out_dir, sample_index=int(payload["sample_index"]))
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def patch_probe_sample_path(*, out_dir: Path, sample_index: int) -> Path:
    return out_dir / f"{CASE_ID}.sample-{sample_index}.anchor-boundary-patch-probe.v1.json"


def load_consultant_anchor_boundary_patch_probe_sample(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ConsultantAnchorBoundaryPatchProbeError(f"{path}: payload must be object")
    return payload


def validate_consultant_anchor_boundary_patch_probe_contract(
    payload: dict[str, object],
    *,
    root: Path | None = None,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_anchor_boundary_patch_probe_contract_errors(payload, root=root, path=path))
    if errors:
        raise ConsultantAnchorBoundaryPatchProbeError("; ".join(errors))


def iter_consultant_anchor_boundary_patch_probe_contract_errors(
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
        if not (Path(root) / variant_ref).exists():
            yield f"{path / 'source_refs' / 'consultant_cleaning_variant_ref'}: missing file"
    yield from _validate_patch(payload.get("patch"), path / "patch")
    yield from _validate_sample_plan(payload.get("sample_plan"), path / "sample_plan")
    if payload.get("preflight_checklist") != list(PREFLIGHT_CHECKLIST):
        yield f"{path / 'preflight_checklist'}: must preserve preflight checklist"
    decision_tree = payload.get("decision_tree")
    if not isinstance(decision_tree, dict) or set(decision_tree) != OUTCOME_STATES:
        yield f"{path / 'decision_tree'}: must contain yes/no/mixed/unobserved"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_consultant_anchor_boundary_patch_probe_sample(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_anchor_boundary_patch_probe_sample_errors(payload, path=path))
    if errors:
        raise ConsultantAnchorBoundaryPatchProbeError("; ".join(errors))


def iter_consultant_anchor_boundary_patch_probe_sample_errors(
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
    if not isinstance(payload.get("reversibility_card_additive"), bool):
        yield f"{path / 'reversibility_card_additive'}: must be bool"
    if not isinstance(payload.get("patched_boundary_in_answer"), bool):
        yield f"{path / 'patched_boundary_in_answer'}: must be bool"
    if not isinstance(payload.get("protected_payload_presence"), dict):
        yield f"{path / 'protected_payload_presence'}: must be object"
    if payload.get("deterministic_role") != list(DETERMINISTIC_ROLE):
        yield f"{path / 'deterministic_role'}: must preserve deterministic role"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_consultant_anchor_boundary_patch_probe_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_consultant_anchor_boundary_patch_probe_result_errors(payload, path=path))
    if errors:
        raise ConsultantAnchorBoundaryPatchProbeError("; ".join(errors))


def iter_consultant_anchor_boundary_patch_probe_result_errors(
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
    variant: dict[str, object],
    sample_index: int,
    provider_metadata: dict[str, object],
    step6_output: dict[str, object],
    notes: str,
) -> dict[str, object]:
    original_anchor = _anchor_text(variant, root=Path.cwd())
    patched_anchor = patched_consultant_anchor(original_anchor)
    normalized = normalize_consultant_cleaning_variant_step6_output(step6_output)
    answer_core = _string(normalized.get("answer_core"))
    payload = {
        "schema_version": SAMPLE_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": CASE_ID,
        "sample_index": sample_index,
        "provider_metadata": _complete_provider_metadata(provider_metadata),
        "input_packet": {
            "original_anchor_visible_candidate": original_anchor,
            "patched_anchor_visible_candidate": patched_anchor,
            "patch_phrase": PATCH_PHRASE,
            "cleaning_micro_cards": _prompt_micro_cards(variant),
            "success_read": contract["sample_plan"]["success_read"],
        },
        "step6_output": normalized,
        "micro_card_signal": derive_micro_card_signal(normalized),
        "answer_delta_specificity": derive_answer_delta_specificity(normalized),
        "reversibility_card_additive": reversibility_card_additive(normalized),
        "patched_boundary_in_answer": patched_boundary_in_answer(answer_core),
        "protected_payload_presence": protected_payload_presence(answer_core),
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": _blocked_gates(),
        "notes": notes,
    }
    validate_consultant_anchor_boundary_patch_probe_sample(payload)
    return payload


def reversibility_card_additive(step6_output: object) -> bool:
    if not isinstance(step6_output, dict):
        return False
    ledger = step6_output.get("private_micro_card_ledger")
    if not isinstance(ledger, list):
        return False
    for item in ledger:
        if not isinstance(item, dict):
            continue
        if item.get("source_id") != "reversibility_until_counsel_boundary_card":
            continue
        return item.get("novelty_role") == "additive_pressure" and item.get("disposition") in {
            "used",
            "combined",
        }
    return False


def patched_boundary_in_answer(answer_core: str) -> bool:
    return "until counsel guides" in answer_core.lower()


def _static_output(
    *,
    variant: dict[str, object],
    micro_card_signal: str,
    reversibility_card_additive: bool,
    patched_boundary_in_answer: bool,
) -> dict[str, object]:
    original_anchor = _anchor_text(variant, root=Path.cwd())
    answer_core = (
        patched_consultant_anchor(original_anchor)
        if patched_boundary_in_answer
        else original_anchor
    )
    ledger = []
    for card_id in MICRO_CARD_IDS:
        is_reversibility = card_id == "reversibility_until_counsel_boundary_card"
        additive = (
            micro_card_signal == "micro_card_additive_present"
            and reversibility_card_additive
            and is_reversibility
        )
        ledger.append(
            {
                "source_id": card_id,
                "disposition": "combined" if additive else "private_guardrail",
                "novelty_role": "additive_pressure" if additive else "confirming_support",
                "why": "Static patch-probe fixture.",
                "visible_effect": "Re-added counsel-gated reversibility boundary." if additive else "none",
                "answer_delta": _static_delta(additive),
            }
        )
    return {"answer_core": answer_core, "private_micro_card_ledger": ledger}


def _static_delta(additive: bool) -> dict[str, list[str]]:
    if additive:
        return {
            "added_entities": ["until counsel guides the next action"],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": [
                "Added counsel-gated boundary to the reversible first-move sequence."
            ],
            "reframed_emphasis": [],
        }
    return {field: [] for field in ANSWER_DELTA_FIELDS}


def _aggregate(case_results: Sequence[object]) -> dict[str, object]:
    rows = [row for row in case_results if isinstance(row, dict)]
    sample_count = len(rows)
    standdown_count = sum(
        1 for row in rows if row.get("micro_card_signal") == "all_private_or_confirming"
    )
    additive_count = sum(
        1 for row in rows if row.get("micro_card_signal") == "micro_card_additive_present"
    )
    missing_count = sum(1 for row in rows if row.get("micro_card_signal") == "missing_or_unclear")
    reversibility_count = sum(1 for row in rows if row.get("reversibility_card_additive") is True)
    boundary_count = sum(1 for row in rows if row.get("patched_boundary_in_answer") is True)
    protected_count = sum(
        1
        for row in rows
        if isinstance(row.get("protected_payload_presence"), dict)
        and all(row["protected_payload_presence"].values())
    )
    standdown_rate = round(standdown_count / sample_count, 3) if sample_count else 0.0
    reversibility_rate = round(reversibility_count / sample_count, 3) if sample_count else 0.0
    protected_preserved = bool(sample_count and protected_count == sample_count)
    upstream = _upstream_pressure_carried(
        sample_count=sample_count,
        boundary_count=boundary_count,
        protected_preserved=protected_preserved,
        standdown_rate=standdown_rate,
        reversibility_rate=reversibility_rate,
    )
    return {
        "sample_count": sample_count,
        "micro_card_standdown_count": standdown_count,
        "micro_card_standdown_rate": standdown_rate,
        "micro_card_additive_count": additive_count,
        "missing_or_unclear_count": missing_count,
        "reversibility_card_additive_count": reversibility_count,
        "reversibility_card_additive_rate": reversibility_rate,
        "patched_boundary_present_count": boundary_count,
        "protected_payload_all_present_count": protected_count,
        "protected_payload_preserved": protected_preserved,
        "upstream_pressure_carried": upstream,
        "next_investigation": _next_investigation(upstream),
        "consultant_classification": _consultant_classification(upstream),
        "runtime_promotion": "blocked",
        "skill_update": "blocked",
    }


def _upstream_pressure_carried(
    *,
    sample_count: int,
    boundary_count: int,
    protected_preserved: bool,
    standdown_rate: float,
    reversibility_rate: float,
) -> str:
    if not sample_count or boundary_count == 0 or not protected_preserved:
        return "unobserved"
    if standdown_rate >= 0.75 and reversibility_rate <= 0.25:
        return "yes"
    if reversibility_rate >= 0.667:
        return "no"
    return "mixed"


def _next_investigation(upstream: str) -> str:
    if upstream == "yes":
        return "synthesis"
    if upstream == "no":
        return "anchor_wording"
    if upstream == "mixed":
        return "further_probe_needed"
    return "anchor_wording"


def _consultant_classification(upstream: str) -> str:
    if upstream == "yes":
        return "graduation_candidate"
    if upstream == "no":
        return "card_needed"
    if upstream == "mixed":
        return "borderline_by_design"
    return "inconclusive_parked"


def _variant_for_contract(*, contract: dict[str, object], root: Path) -> dict[str, object]:
    refs = contract.get("source_refs")
    if not isinstance(refs, dict):
        raise ConsultantAnchorBoundaryPatchProbeError("source_refs missing")
    variant = load_consultant_cleaning_variant(root / _string(refs.get("consultant_cleaning_variant_ref")))
    validate_consultant_cleaning_variant(variant)
    return variant


def _load_variant(*, root: Path) -> dict[str, object]:
    variant = load_consultant_cleaning_variant(Path(root) / DEFAULT_VARIANT_REF)
    validate_consultant_cleaning_variant(variant)
    return variant


def _anchor_text(variant: dict[str, object], *, root: Path) -> str:
    refs = variant.get("source_refs")
    if isinstance(refs, dict):
        anchor_ref = _string(refs.get("anchor_ref"))
        if anchor_ref:
            anchor = _read_json(Path(root) / anchor_ref)
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
    for field in SOURCE_REF_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_patch(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be object"
        return
    yield from _unknown_fields(value, PATCH_FIELDS, path)
    yield from _missing_fields(value, PATCH_FIELDS, path)
    if value.get("patch_phrase") != PATCH_PHRASE:
        yield f"{path / 'patch_phrase'}: must be {PATCH_PHRASE}"
    if value.get("original_phrase") != ORIGINAL_BOUNDARY_PHRASE:
        yield f"{path / 'original_phrase'}: must be {ORIGINAL_BOUNDARY_PHRASE}"
    if value.get("placement") != "hypothesis_test_not_architecture":
        yield f"{path / 'placement'}: must be hypothesis_test_not_architecture"
    if value.get("allowed_change") != "one_phrase_only_no_style_rewrite":
        yield f"{path / 'allowed_change'}: must be one_phrase_only_no_style_rewrite"
    non_purpose = value.get("non_purpose")
    if not isinstance(non_purpose, list) or not non_purpose:
        yield f"{path / 'non_purpose'}: must be non-empty list"


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
    if value.get("max_wording_reruns_on_unobserved") != 1:
        yield f"{path / 'max_wording_reruns_on_unobserved'}: must be 1"
    if not _string(value.get("success_read")).strip():
        yield f"{path / 'success_read'}: must be non-empty"


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
    if not _string(value.get("original_anchor_visible_candidate")).strip():
        yield f"{path / 'original_anchor_visible_candidate'}: must be non-empty"
    patched = _string(value.get("patched_anchor_visible_candidate"))
    if PATCH_PHRASE not in patched:
        yield f"{path / 'patched_anchor_visible_candidate'}: must include patch phrase"
    if value.get("patch_phrase") != PATCH_PHRASE:
        yield f"{path / 'patch_phrase'}: must be {PATCH_PHRASE}"
    if not isinstance(value.get("cleaning_micro_cards"), list) or not value.get("cleaning_micro_cards"):
        yield f"{path / 'cleaning_micro_cards'}: must be non-empty list"


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
    except Exception as exc:  # pragma: no cover - validation message only
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
    if not isinstance(value.get("reversibility_card_additive"), bool):
        yield f"{path / 'reversibility_card_additive'}: must be bool"
    if not isinstance(value.get("patched_boundary_in_answer"), bool):
        yield f"{path / 'patched_boundary_in_answer'}: must be bool"
    if not isinstance(value.get("protected_payload_presence"), dict):
        yield f"{path / 'protected_payload_presence'}: must be object"
    if not isinstance(value.get("used_micro_cards"), list):
        yield f"{path / 'used_micro_cards'}: must be list"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    if value.get("upstream_pressure_carried") not in OUTCOME_STATES:
        yield f"{path / 'upstream_pressure_carried'}: invalid outcome"
    if value.get("next_investigation") not in NEXT_INVESTIGATIONS:
        yield f"{path / 'next_investigation'}: invalid next investigation"
    if value.get("consultant_classification") not in CONSULTANT_CLASSIFICATIONS:
        yield f"{path / 'consultant_classification'}: invalid classification"


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
                raise ConsultantAnchorBoundaryPatchProbeError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_consultant_anchor_boundary_patch_probe_contract(payload, root=Path.cwd(), path=path)
            elif schema == SAMPLE_SCHEMA_VERSION:
                validate_consultant_anchor_boundary_patch_probe_sample(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_consultant_anchor_boundary_patch_probe_result(payload, path=path)
            else:
                raise ConsultantAnchorBoundaryPatchProbeError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_consultant_anchor_boundary_patch_probe_contract(args.contract)
        if args.contract
        else build_consultant_anchor_boundary_patch_probe_contract(root=Path.cwd())
    )
    if args.write_contract:
        print(write_consultant_anchor_boundary_patch_probe_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.write_sample is not None:
        path = run_live_consultant_anchor_boundary_patch_probe_sample(
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
            load_consultant_anchor_boundary_patch_probe_sample(path)
            for path in sorted(args.sample_dir.glob("*.anchor-boundary-patch-probe.v1.json"))
        ]
        result = build_consultant_anchor_boundary_patch_probe_result(
            contract=contract,
            samples=samples,
        )
        print(write_consultant_anchor_boundary_patch_probe_result(payload=result, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
