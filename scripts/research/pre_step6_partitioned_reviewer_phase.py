#!/usr/bin/env python3
"""Research-only reviewer phase for stable pre-Step-6 calibration cases.

This runs after Step 6 stability sampling. It reviews only the stable partition
and deliberately excludes variable cases, so reviewer cognition judges stable
candidate behavior rather than sampling noise.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_calibration_corpus import (
    load_step6_calibration_sample,
    load_step6_calibration_stability_review,
    validate_step6_calibration_sample,
    validate_step6_calibration_stability_review,
)


CONTRACT_SCHEMA_VERSION = "pre_step6_partitioned_reviewer_contract.v1"
JUDGMENT_SCHEMA_VERSION = "pre_step6_partitioned_reviewer_judgment.v1"
RESULT_SCHEMA_VERSION = "pre_step6_partitioned_reviewer_result.v1"
RUNTIME_POLICY = "runtime_dormant"
STATUS = "research_only"
EXPERIMENT_ID = "pre_step6_partitioned_reviewer_phase_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-partitioned-reviewer-phase")
DEFAULT_JUDGMENT_DIR = DEFAULT_OUT_DIR / "judgments"
DEFAULT_SAMPLE_DIR = Path("research/pre-step6-calibration-corpus-kimi-structural-delta/step6-samples")
DEFAULT_STABILITY_REVIEW = Path(
    "research/pre-step6-calibration-corpus-kimi-structural-delta/calibration-stability-review.v1.json"
)
DEFAULT_SEED = 2026052104
DEFAULT_REVIEWER_MODELS = (
    "openai/gpt-5.1-chat",
    "google/gemini-3.1-flash-lite",
)
STABLE_CLASSIFICATIONS = frozenset({"stable_positive", "stable_standdown"})
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "source_stability_review_ref",
        "reviewer_rule",
        "stable_cases",
        "excluded_variable_case_ids",
        "gates",
        "notes",
    }
)
REVIEWER_RULE_FIELDS = frozenset(
    {"reviewer_count", "model_family_policy", "prompt_policy", "blind_shuffle_policy"}
)
CASE_FIELDS = frozenset(
    {
        "partition_case_id",
        "source_case_id",
        "stability_classification",
        "sample_ref",
        "sample_index",
        "case_brief",
        "anchor_visible",
        "step6_visible",
        "ledger_signal",
        "answer_delta_specificity",
        "answer_delta_summary",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
JUDGMENT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "partition_case_id",
        "judgment_source",
        "provider_metadata",
        "blind_map",
        "reviewer_output",
        "gates",
        "notes",
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
REVIEWER_OUTPUT_FIELDS = frozenset(
    {
        "review_label",
        "winner_label",
        "confidence",
        "rationale",
        "step6_value_if_any",
        "anchor_strengths",
        "payload_loss_or_bloat",
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
        "partition_case_id",
        "source_case_id",
        "stability_classification",
        "reviewer_count",
        "reviewer_model_families",
        "review_labels",
        "reviewer_winner_arms",
        "reviewer_label_consistency",
        "confirmed_label",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "case_count",
        "stable_positive_case_count",
        "stable_standdown_case_count",
        "stable_positive_supported_count",
        "stable_positive_rejected_count",
        "stable_standdown_supported_count",
        "stable_standdown_rejected_count",
        "ambiguous_count",
        "tension_count",
        "reviewer_read",
        "recommended_next_action",
    }
)
ALLOWED_REVIEW_LABELS = frozenset(
    {"step6_better", "step6_non_inferior", "anchor_better", "tie", "ambiguous", "not_observed"}
)
ALLOWED_WINNER_ARMS = frozenset({"anchor_visible", "step6_visible", "tie"})
ALLOWED_CONFIRMED_LABELS = frozenset(
    {
        "stable_positive_supported",
        "stable_positive_rejected",
        "stable_standdown_supported",
        "stable_standdown_rejected",
        "ambiguous",
        "not_observed",
    }
)


class PartitionedReviewerPhaseError(ValueError):
    pass


def build_partitioned_reviewer_contract(
    *,
    root: Path,
    stability_review_path: Path = DEFAULT_STABILITY_REVIEW,
    sample_dir: Path = DEFAULT_SAMPLE_DIR,
) -> dict[str, object]:
    root = Path(root)
    review = load_step6_calibration_stability_review(root / stability_review_path)
    validate_step6_calibration_stability_review(review)
    stable_cases: list[dict[str, object]] = []
    excluded: list[str] = []
    for row in review.get("case_reviews", []):
        if not isinstance(row, dict):
            continue
        classification = _string(row.get("stability_classification"))
        source_case_id = _string(row.get("case_id"))
        if classification not in STABLE_CLASSIFICATIONS:
            excluded.append(source_case_id)
            continue
        stable_cases.append(
            _case_from_sample(
                root=root,
                sample_path=_first_sample_path(
                    root=root,
                    sample_dir=sample_dir,
                    source_case_id=source_case_id,
                ),
                stability_classification=classification,
            )
        )
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "source_stability_review_ref": str(stability_review_path),
        "reviewer_rule": {
            "reviewer_count": 2,
            "model_family_policy": "different_model_family_required",
            "prompt_policy": "same_rubric_saved_stable_samples_only",
            "blind_shuffle_policy": "fresh_blind_shuffle_per_reviewer",
        },
        "stable_cases": stable_cases,
        "excluded_variable_case_ids": excluded,
        "gates": _blocked_gates(),
        "notes": (
            "Reviewer cognition is restricted to stable cases. A pass here does "
            "not unlock shadow implementation because variable cases remain "
            "quarantined."
        ),
    }
    validate_partitioned_reviewer_contract(payload)
    return payload


def write_partitioned_reviewer_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_partitioned_reviewer_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "partitioned-reviewer-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_partitioned_reviewer_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise PartitionedReviewerPhaseError(f"{path}: payload must be object")
    validate_partitioned_reviewer_contract(payload, path=path)
    return payload


def build_reviewer_packet(
    *,
    contract: dict[str, object],
    partition_case_id: str,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    validate_partitioned_reviewer_contract(contract)
    case = _case_by_id(contract, partition_case_id)
    arms = ["anchor_visible", "step6_visible"]
    rng = random.Random(seed + sum(ord(char) for char in partition_case_id))
    rng.shuffle(arms)
    blind_map = dict(zip(("A", "B"), arms, strict=True))
    answer_by_arm = {
        "anchor_visible": _string(case["anchor_visible"]),
        "step6_visible": _string(case["step6_visible"]),
    }
    return {
        "experiment_id": EXPERIMENT_ID,
        "partition_case_id": partition_case_id,
        "source_case_id": case["source_case_id"],
        "stability_classification": case["stability_classification"],
        "case_brief": case["case_brief"],
        "ledger_signal": case["ledger_signal"],
        "answer_delta_specificity": case["answer_delta_specificity"],
        "answer_delta_summary": case["answer_delta_summary"],
        "reviewer_task": (
            "Compare two blinded visible answers for the user's actual decision. "
            "This is the stable-case partition only. Do not infer runtime policy. "
            "Judge whether the saved Step 6 answer is better, non-inferior, tied, "
            "or worse than the anchor. Prefer useful, grounded, concrete, "
            "action-guiding answers; penalize bloat and payload loss."
        ),
        "candidates_by_label": {
            label: {"answer_core": answer_by_arm[arm], "char_count": len(answer_by_arm[arm])}
            for label, arm in blind_map.items()
        },
        "blind_map_private": blind_map,
        "response_schema": {
            "review_label": (
                "step6_better | step6_non_inferior | anchor_better | tie | ambiguous | not_observed"
            ),
            "winner_label": "A | B | tie",
            "confidence": "high | medium | low",
            "rationale": "Short rationale grounded in the two answers.",
            "step6_value_if_any": ["Concrete Step 6 value, if any."],
            "anchor_strengths": ["Anchor strengths, if any."],
            "payload_loss_or_bloat": ["Specific payload loss or bloat, if any."],
        },
    }


def build_static_partitioned_judgment(
    *,
    contract: dict[str, object],
    partition_case_id: str,
    model: str,
    review_label: str,
    winner_arm: str,
) -> dict[str, object]:
    packet = build_reviewer_packet(contract=contract, partition_case_id=partition_case_id)
    blind_map = _string_dict(packet["blind_map_private"])
    winner_label = "tie"
    if winner_arm != "tie":
        winner_label = next(label for label, arm in blind_map.items() if arm == winner_arm)
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "partition_case_id": partition_case_id,
        "judgment_source": "static_partitioned_reviewer_judgment",
        "provider_metadata": {
            "provider": "static",
            "model": model,
            "model_family": _model_family(model),
            "status": "ok",
        },
        "blind_map": blind_map,
        "reviewer_output": {
            "review_label": review_label,
            "winner_label": winner_label,
            "confidence": "high",
            "rationale": "Static fixture judgment.",
            "step6_value_if_any": ["Static Step 6 value."],
            "anchor_strengths": ["Static anchor strength."],
            "payload_loss_or_bloat": ["none"],
        },
        "gates": _blocked_gates(),
        "notes": "Static partitioned reviewer judgment.",
    }
    validate_partitioned_reviewer_judgment(payload)
    return payload


def run_live_reviewer(
    *,
    contract: dict[str, object],
    partition_case_id: str,
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    seed: int,
    dry_run: bool,
) -> Path | None:
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    packet = build_reviewer_packet(contract=contract, partition_case_id=partition_case_id, seed=seed)
    private_blind_map = _string_dict(packet.pop("blind_map_private"))
    if dry_run:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
        return None
    repo_root = Path.cwd()
    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    output, metadata = client.run_json_with_metadata(
        _reviewer_system_prompt(),
        json.dumps(packet, indent=2, ensure_ascii=False),
        stage="pre_step6_partitioned_reviewer_phase",
        tendency_id=partition_case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise PartitionedReviewerPhaseError(
            "live partitioned reviewer failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "partition_case_id": partition_case_id,
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": provider_metadata,
        "blind_map": private_blind_map,
        "reviewer_output": _normalize_reviewer_output(output, blind_map=private_blind_map),
        "gates": _blocked_gates(),
        "notes": "Live saved-sample partitioned reviewer judgment.",
    }
    return write_partitioned_reviewer_judgment(payload=payload, out_dir=out_dir)


def build_partitioned_reviewer_result(
    *,
    contract: dict[str, object],
    judgments: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_partitioned_reviewer_contract(contract)
    for judgment in judgments:
        validate_partitioned_reviewer_judgment(judgment)
    by_case: dict[str, list[dict[str, object]]] = {}
    for judgment in judgments:
        by_case.setdefault(_string(judgment.get("partition_case_id")), []).append(judgment)
    case_results: list[dict[str, object]] = []
    for case in contract["stable_cases"]:
        if not isinstance(case, dict):
            continue
        partition_case_id = _string(case["partition_case_id"])
        case_judgments = by_case.get(partition_case_id, [])
        if not case_judgments:
            continue
        labels = [_string(judgment["reviewer_output"]["review_label"]) for judgment in case_judgments]
        winner_arms = [_reviewer_winner_arm(judgment) for judgment in case_judgments]
        families = sorted(
            {
                _string(judgment["provider_metadata"].get("model_family"))
                for judgment in case_judgments
                if _string(judgment["provider_metadata"].get("model_family"))
            }
        )
        consistency = _reviewer_label_consistency(labels=labels, winner_arms=winner_arms)
        confirmed = _confirmed_label(
            classification=_string(case["stability_classification"]),
            labels=labels,
            families=families,
            consistency=consistency,
        )
        case_results.append(
            {
                "partition_case_id": partition_case_id,
                "source_case_id": _string(case["source_case_id"]),
                "stability_classification": _string(case["stability_classification"]),
                "reviewer_count": len(case_judgments),
                "reviewer_model_families": families,
                "review_labels": labels,
                "reviewer_winner_arms": winner_arms,
                "reviewer_label_consistency": consistency,
                "confirmed_label": confirmed,
            }
        )
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_results": case_results,
        "aggregate": _aggregate_result(case_results),
        "gates": _blocked_gates(),
        "notes": (
            "Reviewer result for stable cases only. This cannot promote shadow "
            "implementation while variable cases remain quarantined."
        ),
    }
    validate_partitioned_reviewer_result(payload)
    return payload


def write_partitioned_reviewer_judgment(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_partitioned_reviewer_judgment(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = _string(payload["provider_metadata"].get("model")).replace("/", "__")
    path = out_dir / f"{_string(payload['partition_case_id'])}.{model_slug}.partitioned-reviewer-judgment.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_partitioned_reviewer_judgment(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise PartitionedReviewerPhaseError(f"{path}: payload must be object")
    validate_partitioned_reviewer_judgment(payload, path=path)
    return payload


def write_partitioned_reviewer_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_partitioned_reviewer_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "partitioned-reviewer-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_partitioned_reviewer_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise PartitionedReviewerPhaseError(f"{path}: payload must be object")
    validate_partitioned_reviewer_result(payload, path=path)
    return payload


def validate_partitioned_reviewer_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_partitioned_reviewer_contract_errors(payload, path=path))
    if errors:
        raise PartitionedReviewerPhaseError("; ".join(errors))


def iter_partitioned_reviewer_contract_errors(
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
    if payload.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {CONTRACT_SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"
    yield from _validate_reviewer_rule(payload.get("reviewer_rule"), path / "reviewer_rule")
    cases = payload.get("stable_cases")
    if not isinstance(cases, list) or not cases:
        yield f"{path / 'stable_cases'}: must be non-empty list"
    else:
        classifications = {_string(case.get("stability_classification")) for case in cases if isinstance(case, dict)}
        if not STABLE_CLASSIFICATIONS <= classifications:
            yield f"{path / 'stable_cases'}: must include positive and stand-down cases"
        for index, case in enumerate(cases):
            yield from _validate_case(case, path / "stable_cases" / str(index))
    excluded = payload.get("excluded_variable_case_ids")
    if not isinstance(excluded, list):
        yield f"{path / 'excluded_variable_case_ids'}: must be list"
    elif any(not _string(case_id).strip() for case_id in excluded):
        yield f"{path / 'excluded_variable_case_ids'}: ids must be non-empty"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_partitioned_reviewer_judgment(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_partitioned_reviewer_judgment_errors(payload, path=path))
    if errors:
        raise PartitionedReviewerPhaseError("; ".join(errors))


def iter_partitioned_reviewer_judgment_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be object"
        return
    required = tuple(JUDGMENT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, JUDGMENT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != JUDGMENT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {JUDGMENT_SCHEMA_VERSION}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if not _string(payload.get("partition_case_id")).strip():
        yield f"{path / 'partition_case_id'}: must be non-empty"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    blind_map, blind_errors = _validate_blind_map(payload.get("blind_map"), path / "blind_map")
    yield from blind_errors
    yield from _validate_reviewer_output(
        payload.get("reviewer_output"),
        blind_map=blind_map,
        path=path / "reviewer_output",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_partitioned_reviewer_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_partitioned_reviewer_result_errors(payload, path=path))
    if errors:
        raise PartitionedReviewerPhaseError("; ".join(errors))


def iter_partitioned_reviewer_result_errors(
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
    if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {RESULT_SCHEMA_VERSION}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"
    results = payload.get("case_results")
    if not isinstance(results, list):
        yield f"{path / 'case_results'}: must be list"
    else:
        for index, result in enumerate(results):
            yield from _validate_case_result(result, path / "case_results" / str(index))
    yield from _validate_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _case_from_sample(
    *,
    root: Path,
    sample_path: Path,
    stability_classification: str,
) -> dict[str, object]:
    sample = load_step6_calibration_sample(root / sample_path)
    validate_step6_calibration_sample(sample)
    source_case_id = _string(sample["case_id"])
    sample_index = int(sample["sample_index"])
    input_packet = sample["input_packet"]
    step6_output = sample["step6_output"]
    return {
        "partition_case_id": f"{source_case_id}.sample-{sample_index}.{stability_classification.replace('_', '-')}",
        "source_case_id": source_case_id,
        "stability_classification": stability_classification,
        "sample_ref": str(sample_path),
        "sample_index": sample_index,
        "case_brief": _string(input_packet.get("case_brief")),
        "anchor_visible": _string(input_packet.get("anchor_visible_candidate")),
        "step6_visible": _string(step6_output.get("answer_core")),
        "ledger_signal": _string(sample.get("ledger_signal")),
        "answer_delta_specificity": _string(sample.get("answer_delta_specificity")),
        "answer_delta_summary": _answer_delta_summary(step6_output),
    }


def _first_sample_path(*, root: Path, sample_dir: Path, source_case_id: str) -> Path:
    candidates = sorted((root / sample_dir).glob(f"{source_case_id}.sample-*.calibration-step6.v1.json"))
    if not candidates:
        raise PartitionedReviewerPhaseError(f"{source_case_id}: no sample artifacts found")
    return candidates[0].relative_to(root)


def _answer_delta_summary(step6_output: object) -> dict[str, list[str]]:
    summary = {
        "added_entities": [],
        "removed_entities": [],
        "reordered_sequences": [],
        "structural_delta": [],
        "reframed_emphasis": [],
    }
    if not isinstance(step6_output, dict):
        return summary
    ledger = step6_output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return summary
    for item in ledger:
        if not isinstance(item, dict) or item.get("source_id") != "deck_pressure_candidate":
            continue
        delta = item.get("answer_delta")
        if not isinstance(delta, dict):
            continue
        for key in summary:
            values = delta.get(key)
            if isinstance(values, list):
                summary[key].extend(_string(value) for value in values if _string(value))
    return summary


def _aggregate_result(case_results: list[dict[str, object]]) -> dict[str, object]:
    positive = [r for r in case_results if r.get("stability_classification") == "stable_positive"]
    standdown = [r for r in case_results if r.get("stability_classification") == "stable_standdown"]
    tension = sum(1 for r in case_results if r.get("reviewer_label_consistency") == "tension_detected")
    ambiguous = sum(1 for r in case_results if r.get("confirmed_label") in {"ambiguous", "not_observed"})
    positive_rejected = sum(1 for r in case_results if r.get("confirmed_label") == "stable_positive_rejected")
    standdown_rejected = sum(1 for r in case_results if r.get("confirmed_label") == "stable_standdown_rejected")
    if positive_rejected or standdown_rejected:
        read = "stable_partition_design_review_required"
        action = "inspect_rejected_stable_cases_before_any_shadow_work"
    elif ambiguous or tension:
        read = "stable_partition_partial_or_ambiguous"
        action = "inspect_ambiguous_or_tense_reviewer_records_before_promotion"
    else:
        read = "stable_partition_supported"
        action = "continue_variable_case_diagnostic_before_shadow_implementation"
    return {
        "case_count": len(case_results),
        "stable_positive_case_count": len(positive),
        "stable_standdown_case_count": len(standdown),
        "stable_positive_supported_count": sum(
            1 for r in case_results if r.get("confirmed_label") == "stable_positive_supported"
        ),
        "stable_positive_rejected_count": positive_rejected,
        "stable_standdown_supported_count": sum(
            1 for r in case_results if r.get("confirmed_label") == "stable_standdown_supported"
        ),
        "stable_standdown_rejected_count": standdown_rejected,
        "ambiguous_count": ambiguous,
        "tension_count": tension,
        "reviewer_read": read,
        "recommended_next_action": action,
    }


def _confirmed_label(
    *,
    classification: str,
    labels: list[str],
    families: list[str],
    consistency: str,
) -> str:
    if len(families) < 2 or len(labels) < 2:
        return "not_observed"
    if consistency == "tension_detected":
        return "ambiguous"
    step6_positive = {"step6_better", "step6_non_inferior"}
    if classification == "stable_positive":
        if all(label in step6_positive for label in labels):
            return "stable_positive_supported"
        if all(label == "anchor_better" for label in labels):
            return "stable_positive_rejected"
        return "ambiguous"
    if classification == "stable_standdown":
        if all(label in {"anchor_better", "tie"} for label in labels):
            return "stable_standdown_supported"
        if all(label == "step6_better" for label in labels):
            return "stable_standdown_rejected"
        return "ambiguous"
    return "not_observed"


def _reviewer_winner_arm(judgment: dict[str, object]) -> str:
    blind_map = _string_dict(judgment.get("blind_map"))
    output = judgment.get("reviewer_output")
    if not isinstance(output, dict):
        return "unknown"
    winner = _string(output.get("winner_label"))
    if winner == "tie":
        return "tie"
    return blind_map.get(winner, "unknown")


def _reviewer_label_consistency(*, labels: Sequence[str], winner_arms: Sequence[str]) -> str:
    if not labels:
        return "not_applicable"
    for label, winner_arm in zip(labels, winner_arms, strict=False):
        if label == "step6_better" and winner_arm != "step6_visible":
            return "tension_detected"
        if label == "anchor_better" and winner_arm != "anchor_visible":
            return "tension_detected"
        if label == "tie" and winner_arm != "tie":
            return "tension_detected"
        if label == "step6_non_inferior" and winner_arm not in {
            "step6_visible",
            "tie",
            "anchor_visible",
        }:
            return "tension_detected"
    return "aligned"


def _normalize_reviewer_output(value: object, *, blind_map: dict[str, str]) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    label = _string(value.get("review_label"))
    if label not in ALLOWED_REVIEW_LABELS:
        label = "ambiguous"
    winner = _string(value.get("winner_label"))
    if winner not in set(blind_map) | {"tie"}:
        winner = "tie"
    confidence = _string(value.get("confidence"))
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    return {
        "review_label": label,
        "winner_label": winner,
        "confidence": confidence,
        "rationale": _string(value.get("rationale")) or "Reviewer did not provide rationale.",
        "step6_value_if_any": _string_list(value.get("step6_value_if_any"), fallback="none"),
        "anchor_strengths": _string_list(value.get("anchor_strengths"), fallback="none"),
        "payload_loss_or_bloat": _string_list(value.get("payload_loss_or_bloat"), fallback="none"),
    }


def _reviewer_system_prompt() -> str:
    return (
        "You are a blind reviewer for a research-only stable-partition calibration. "
        "Return strict JSON only. Judge the observable usefulness of two answers "
        "for the user's actual decision. Do not reward verbosity, clever framing, "
        "or private labels. Prefer grounded, concrete, action-guiding answers that "
        "preserve payload and avoid bloat."
    )


def _validate_reviewer_rule(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: reviewer_rule must be object"
        return
    yield from _unknown_fields(value, REVIEWER_RULE_FIELDS, path)
    yield from _missing_fields(value, REVIEWER_RULE_FIELDS, path)
    if value.get("reviewer_count") != 2:
        yield f"{path / 'reviewer_count'}: must be 2"
    if value.get("model_family_policy") != "different_model_family_required":
        yield f"{path / 'model_family_policy'}: invalid policy"
    if value.get("blind_shuffle_policy") != "fresh_blind_shuffle_per_reviewer":
        yield f"{path / 'blind_shuffle_policy'}: invalid policy"


def _validate_case(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case must be object"
        return
    yield from _unknown_fields(value, CASE_FIELDS, path)
    yield from _missing_fields(value, CASE_FIELDS, path)
    if any(field not in value for field in CASE_FIELDS):
        return
    if _string(value.get("stability_classification")) not in STABLE_CLASSIFICATIONS:
        yield f"{path / 'stability_classification'}: invalid classification"
    for field in ("partition_case_id", "source_case_id", "sample_ref", "case_brief", "anchor_visible", "step6_visible"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if not isinstance(value.get("sample_index"), int):
        yield f"{path / 'sample_index'}: must be integer"
    if not isinstance(value.get("answer_delta_summary"), dict):
        yield f"{path / 'answer_delta_summary'}: must be object"


def _validate_provider_metadata(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: provider metadata must be object"
        return
    if "provider" not in value and "provider_name" not in value:
        yield f"{path}: provider or provider_name is required"
    for field in ("model", "model_family", "status"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    yield from _unknown_fields(value, PROVIDER_METADATA_FIELDS, path)


def _validate_blind_map(value: object, path: Path) -> tuple[dict[str, str], list[str]]:
    if not isinstance(value, dict):
        return {}, [f"{path}: blind_map must be object"]
    blind_map = {str(key): _string(item) for key, item in value.items()}
    errors = []
    if set(blind_map) != {"A", "B"}:
        errors.append(f"{path}: blind_map must contain A and B")
    if set(blind_map.values()) != {"anchor_visible", "step6_visible"}:
        errors.append(f"{path}: blind_map must map to anchor_visible and step6_visible")
    return blind_map, errors


def _validate_reviewer_output(
    value: object,
    *,
    blind_map: dict[str, str],
    path: Path,
) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: reviewer_output must be object"
        return
    yield from _unknown_fields(value, REVIEWER_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, REVIEWER_OUTPUT_FIELDS, path)
    if _string(value.get("review_label")) not in ALLOWED_REVIEW_LABELS:
        yield f"{path / 'review_label'}: invalid label"
    winner = _string(value.get("winner_label"))
    if winner != "tie" and winner not in blind_map:
        yield f"{path / 'winner_label'}: must be A, B, or tie"
    if _string(value.get("confidence")) not in {"high", "medium", "low"}:
        yield f"{path / 'confidence'}: invalid confidence"
    for field in ("step6_value_if_any", "anchor_strengths", "payload_loss_or_bloat"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"


def _validate_case_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case result must be object"
        return
    yield from _unknown_fields(value, CASE_RESULT_FIELDS, path)
    yield from _missing_fields(value, CASE_RESULT_FIELDS, path)
    if any(field not in value for field in CASE_RESULT_FIELDS):
        return
    if _string(value.get("stability_classification")) not in STABLE_CLASSIFICATIONS:
        yield f"{path / 'stability_classification'}: invalid classification"
    if _string(value.get("confirmed_label")) not in ALLOWED_CONFIRMED_LABELS:
        yield f"{path / 'confirmed_label'}: invalid confirmed label"
    for field in ("review_labels", "reviewer_winner_arms", "reviewer_model_families"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"
    if not isinstance(value.get("reviewer_count"), int):
        yield f"{path / 'reviewer_count'}: must be integer"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    for field in AGGREGATE_FIELDS - {"reviewer_read", "recommended_next_action"}:
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    if not _string(value.get("reviewer_read")).strip():
        yield f"{path / 'reviewer_read'}: must be non-empty"
    if not _string(value.get("recommended_next_action")).strip():
        yield f"{path / 'recommended_next_action'}: must be non-empty"


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


def _provider_metadata_dict(metadata: object) -> dict[str, object]:
    if hasattr(metadata, "__dict__"):
        raw = dict(vars(metadata))
    elif isinstance(metadata, dict):
        raw = dict(metadata)
    else:
        raw = {}
    if "provider_name" in raw and "provider" not in raw:
        raw["provider"] = raw["provider_name"]
    return {str(key): value for key, value in raw.items() if value is not None}


def _model_family(model: str) -> str:
    if "/" in model:
        return model.split("/", 1)[0].split(".", 1)[0]
    return model.split("-", 1)[0] if model else "unknown"


def _case_by_id(contract: dict[str, object], partition_case_id: str) -> dict[str, object]:
    cases = contract.get("stable_cases")
    if not isinstance(cases, list):
        raise PartitionedReviewerPhaseError("stable_cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("partition_case_id") == partition_case_id:
            return case
    raise PartitionedReviewerPhaseError(f"unknown partition case: {partition_case_id}")


def _load_env_file(path: Path) -> None:
    if not path.exists():
        raise PartitionedReviewerPhaseError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _read_json(path: Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _unknown_fields(value: dict[str, object], allowed: frozenset[str], path: Path) -> Iterable[str]:
    for field in sorted(set(value) - allowed):
        yield f"{path / field}: unknown field"


def _missing_fields(value: dict[str, object], required: Iterable[str], path: Path) -> Iterable[str]:
    for field in sorted(set(required) - set(value)):
        yield f"{path / field}: missing required field"


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _string_dict(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _string(item) for key, item in value.items()}


def _string_list(value: object, *, fallback: str) -> list[str]:
    if isinstance(value, list):
        items = [_string(item) for item in value if _string(item)]
        return items or [fallback]
    text = _string(value)
    return [text] if text else [fallback]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--judgment-dir", type=Path, default=DEFAULT_JUDGMENT_DIR)
    parser.add_argument("--stability-review", type=Path, default=DEFAULT_STABILITY_REVIEW)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--live-review", action="store_true")
    parser.add_argument("--rebuild-result", action="store_true")
    parser.add_argument("--partition-case-id", action="append", default=[])
    parser.add_argument("--reviewer-model", action="append", default=[])
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise PartitionedReviewerPhaseError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_partitioned_reviewer_contract(payload, path=path)
            elif schema == JUDGMENT_SCHEMA_VERSION:
                validate_partitioned_reviewer_judgment(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_partitioned_reviewer_result(payload, path=path)
            else:
                raise PartitionedReviewerPhaseError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_partitioned_reviewer_contract(args.contract)
        if args.contract is not None
        else build_partitioned_reviewer_contract(
            root=Path.cwd(),
            stability_review_path=args.stability_review,
            sample_dir=args.sample_dir,
        )
    )
    if args.write_contract:
        print(write_partitioned_reviewer_contract(payload=contract, out_dir=args.out_dir))
        return 0

    if args.rebuild_result:
        judgment_paths = sorted(args.judgment_dir.glob("*.partitioned-reviewer-judgment.v1.json"))
        result = build_partitioned_reviewer_result(
            contract=contract,
            judgments=[load_partitioned_reviewer_judgment(path) for path in judgment_paths],
        )
        print(write_partitioned_reviewer_result(payload=result, out_dir=args.out_dir))
        return 0

    if args.live_review:
        case_ids = args.partition_case_id or [
            _string(case["partition_case_id"])
            for case in contract["stable_cases"]
            if isinstance(case, dict)
        ]
        models = args.reviewer_model or list(DEFAULT_REVIEWER_MODELS)
        outputs = []
        for case_id in case_ids:
            for model in models:
                output = run_live_reviewer(
                    contract=contract,
                    partition_case_id=case_id,
                    provider=args.provider,
                    model=model,
                    env_file=args.env_file,
                    out_dir=args.judgment_dir,
                    seed=DEFAULT_SEED + len(outputs),
                    dry_run=args.dry_run,
                )
                if output is not None:
                    outputs.append(output)
                    print(output)
        if outputs:
            result = build_partitioned_reviewer_result(
                contract=contract,
                judgments=[load_partitioned_reviewer_judgment(path) for path in outputs],
            )
            print(write_partitioned_reviewer_result(payload=result, out_dir=args.out_dir))
        return 0

    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
