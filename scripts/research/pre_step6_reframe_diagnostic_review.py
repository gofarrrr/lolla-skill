#!/usr/bin/env python3
"""Research-only reviewer diagnostic for reframe-only Step 6 outputs.

This slice asks a narrow question after calibration stability sampling:
are Step 6 outputs with only ``reframed_emphasis`` useful enough to challenge
the answer-delta vocabulary, or are they correctly suppressed?

It uses saved Step 6 samples only. It does not run Step 6, edit SKILL.md, or
change runtime behavior.
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
    validate_step6_calibration_sample,
)


CONTRACT_SCHEMA_VERSION = "pre_step6_reframe_diagnostic_contract.v1"
JUDGMENT_SCHEMA_VERSION = "pre_step6_reframe_diagnostic_judgment.v1"
RESULT_SCHEMA_VERSION = "pre_step6_reframe_diagnostic_result.v1"
RUNTIME_POLICY = "runtime_dormant"
STATUS = "research_only"
EXPERIMENT_ID = "calibration_reframe_diagnostic_review_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-reframe-diagnostic-review")
DEFAULT_JUDGMENT_DIR = DEFAULT_OUT_DIR / "judgments"
DEFAULT_ORIGINAL_SAMPLE_DIR = Path("research/pre-step6-calibration-corpus/step6-samples")
DEFAULT_REPEAT_SAMPLE_DIR = Path("research/pre-step6-calibration-corpus-repeat-unstable/step6-samples")
DEFAULT_SEED = 2026052103
DEFAULT_REVIEWER_MODELS = (
    "openai/gpt-5.1-chat",
    "google/gemini-3.1-flash-lite",
)
QUESTION = (
    "Are reframe-only Step 6 outputs genuinely useful enough to challenge "
    "the answer-delta vocabulary, or correctly suppressed?"
)
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "question",
        "reviewer_rule",
        "diagnostic_cases",
        "gates",
        "notes",
    }
)
REVIEWER_RULE_FIELDS = frozenset(
    {"reviewer_count", "model_family_policy", "prompt_policy", "blind_shuffle_policy"}
)
CASE_FIELDS = frozenset(
    {
        "diagnostic_case_id",
        "source_case_id",
        "sample_ref",
        "sample_index",
        "diagnostic_role",
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
        "diagnostic_case_id",
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
        "diagnostic_label",
        "winner_label",
        "confidence",
        "rationale",
        "reframe_value_if_any",
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
        "diagnostic_case_id",
        "source_case_id",
        "diagnostic_role",
        "answer_delta_specificity",
        "reviewer_count",
        "reviewer_model_families",
        "diagnostic_labels",
        "reviewer_winner_arms",
        "reviewer_label_consistency",
        "confirmed_label",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "case_count",
        "reframe_case_count",
        "confirmed_reframe_useful_count",
        "confirmed_reframe_correctly_suppressed_count",
        "ambiguous_count",
        "tension_count",
        "control_case_count",
        "diagnostic_read",
        "recommended_next_action",
    }
)
ALLOWED_ROLES = frozenset(
    {"stable_positive_anchor", "stable_standdown_anchor", "reframe_only_diagnostic"}
)
ALLOWED_DIAGNOSTIC_LABELS = frozenset(
    {"step6_better", "step6_non_inferior", "anchor_better", "ambiguous", "not_observed"}
)
ALLOWED_CONFIRMED_LABELS = frozenset(
    {
        "reframe_useful",
        "reframe_correctly_suppressed",
        "control_step6_supported",
        "control_anchor_supported",
        "ambiguous",
        "not_observed",
    }
)
ALLOWED_WINNER_ARMS = frozenset({"anchor_visible", "step6_visible", "tie"})


class ReframeDiagnosticReviewError(ValueError):
    pass


def build_reframe_diagnostic_contract(*, root: Path) -> dict[str, object]:
    root = Path(root)
    cases = [
        _case_from_sample(
            root=root,
            sample_path=DEFAULT_ORIGINAL_SAMPLE_DIR
            / "bridge-sensitive-anchor-misses-tripwire.sample-0.calibration-step6.v1.json",
            diagnostic_role="stable_positive_anchor",
        ),
        _case_from_sample(
            root=root,
            sample_path=DEFAULT_ORIGINAL_SAMPLE_DIR
            / "mother-address-year.sample-0.calibration-step6.v1.json",
            diagnostic_role="stable_standdown_anchor",
        ),
        _case_from_sample(
            root=root,
            sample_path=DEFAULT_ORIGINAL_SAMPLE_DIR
            / "multi-offer-new-run2.sample-0.calibration-step6.v1.json",
            diagnostic_role="stable_positive_anchor",
        ),
    ]
    repeat_dir = root / DEFAULT_REPEAT_SAMPLE_DIR
    for sample_path in sorted(repeat_dir.glob("*.json")):
        sample = load_step6_calibration_sample(sample_path)
        if sample.get("answer_delta_specificity") != "reframe_only":
            continue
        source_case_id = _string(sample.get("case_id"))
        if source_case_id == "marker-entity-attempt-1-resource-generalization":
            continue
        cases.append(
            _case_from_sample(
                root=root,
                sample_path=sample_path.relative_to(root),
                diagnostic_role="reframe_only_diagnostic",
                loaded_sample=sample,
            )
        )
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "question": QUESTION,
        "reviewer_rule": {
            "reviewer_count": 2,
            "model_family_policy": "different_model_family_required",
            "prompt_policy": "same_rubric_saved_samples_only",
            "blind_shuffle_policy": "fresh_blind_shuffle_per_reviewer",
        },
        "diagnostic_cases": cases,
        "gates": _blocked_gates(),
        "notes": (
            "Saved-sample reviewer diagnostic. Reframe-only samples come from the "
            "same-prompt repeat pass; stable anchors come from the first calibration corpus."
        ),
    }
    validate_reframe_diagnostic_contract(payload)
    return payload


def validate_reframe_diagnostic_contract(payload: dict[str, object], *, path: Path = Path("<payload>")) -> None:
    errors = list(iter_reframe_diagnostic_contract_errors(payload, path=path))
    if errors:
        raise ReframeDiagnosticReviewError("; ".join(errors))


def iter_reframe_diagnostic_contract_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
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
    if payload.get("question") != QUESTION:
        yield f"{path / 'question'}: invalid question"
    yield from _validate_reviewer_rule(payload.get("reviewer_rule"), path / "reviewer_rule")
    cases = payload.get("diagnostic_cases")
    if not isinstance(cases, list) or not cases:
        yield f"{path / 'diagnostic_cases'}: must be non-empty list"
    else:
        roles = set()
        for index, case in enumerate(cases):
            if isinstance(case, dict):
                roles.add(_string(case.get("diagnostic_role")))
            yield from _validate_case(case, path / "diagnostic_cases" / str(index))
        if not {"stable_positive_anchor", "stable_standdown_anchor", "reframe_only_diagnostic"} <= roles:
            yield f"{path / 'diagnostic_cases'}: must include stable anchors and reframe diagnostics"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_reframe_diagnostic_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_reframe_diagnostic_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "reframe-diagnostic-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_reframe_diagnostic_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ReframeDiagnosticReviewError(f"{path}: payload must be an object")
    validate_reframe_diagnostic_contract(payload, path=path)
    return payload


def build_reviewer_packet(
    *,
    contract: dict[str, object],
    diagnostic_case_id: str,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    validate_reframe_diagnostic_contract(contract)
    case = _case_by_id(contract, diagnostic_case_id)
    arms = ["anchor_visible", "step6_visible"]
    rng = random.Random(seed + sum(ord(char) for char in diagnostic_case_id))
    rng.shuffle(arms)
    blind_map = dict(zip(("A", "B"), arms, strict=True))
    answer_by_arm = {
        "anchor_visible": _string(case["anchor_visible"]),
        "step6_visible": _string(case["step6_visible"]),
    }
    return {
        "experiment_id": EXPERIMENT_ID,
        "diagnostic_case_id": diagnostic_case_id,
        "source_case_id": case["source_case_id"],
        "diagnostic_role": case["diagnostic_role"],
        "case_brief": case["case_brief"],
        "ledger_signal": case["ledger_signal"],
        "answer_delta_specificity": case["answer_delta_specificity"],
        "answer_delta_summary": case["answer_delta_summary"],
        "reviewer_task": (
            "Compare two blinded visible answers. This is not a style contest. "
            "Judge whether the Step 6 saved-sample answer is better, non-inferior, "
            "or worse for the user's actual decision. For reframe-only diagnostics, "
            "the key question is whether a visible answer can be genuinely useful "
            "even though Step 6 recorded only reframed_emphasis and no concrete "
            "added/removed/reordered payload."
        ),
        "candidates_by_label": {
            label: {"answer_core": answer_by_arm[arm], "char_count": len(answer_by_arm[arm])}
            for label, arm in blind_map.items()
        },
        "blind_map_private": blind_map,
        "response_schema": {
            "diagnostic_label": (
                "step6_better | step6_non_inferior | anchor_better | ambiguous | not_observed"
            ),
            "winner_label": "A | B | tie",
            "confidence": "high | medium | low",
            "rationale": "Short rationale grounded in the two answers.",
            "reframe_value_if_any": ["Useful reframing, if any."],
            "anchor_strengths": ["Anchor strengths, if any."],
            "payload_loss_or_bloat": ["Specific payload loss or bloat, if any."],
        },
    }


def build_static_reframe_judgment(
    *,
    contract: dict[str, object],
    diagnostic_case_id: str,
    model: str,
    diagnostic_label: str,
    winner_arm: str,
) -> dict[str, object]:
    packet = build_reviewer_packet(contract=contract, diagnostic_case_id=diagnostic_case_id)
    blind_map = _string_dict(packet["blind_map_private"])
    winner_label = "tie"
    if winner_arm != "tie":
        winner_label = next(label for label, arm in blind_map.items() if arm == winner_arm)
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "diagnostic_case_id": diagnostic_case_id,
        "judgment_source": "static_test_reframe_judgment",
        "provider_metadata": {
            "provider": "static",
            "model": model,
            "model_family": _model_family(model),
            "status": "ok",
        },
        "blind_map": blind_map,
        "reviewer_output": {
            "diagnostic_label": diagnostic_label,
            "winner_label": winner_label,
            "confidence": "high",
            "rationale": "Static fixture judgment.",
            "reframe_value_if_any": ["Static reframe value."],
            "anchor_strengths": ["Static anchor strength."],
            "payload_loss_or_bloat": ["none"],
        },
        "gates": _blocked_gates(),
        "notes": "Static reframe diagnostic judgment.",
    }
    validate_reframe_diagnostic_judgment(payload)
    return payload


def run_live_reviewer(
    *,
    contract: dict[str, object],
    diagnostic_case_id: str,
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
    packet = build_reviewer_packet(contract=contract, diagnostic_case_id=diagnostic_case_id, seed=seed)
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
        stage="pre_step6_reframe_diagnostic_review",
        tendency_id=diagnostic_case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise ReframeDiagnosticReviewError(
            "live reframe diagnostic reviewer failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "diagnostic_case_id": diagnostic_case_id,
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": provider_metadata,
        "blind_map": private_blind_map,
        "reviewer_output": _normalize_reviewer_output(output, blind_map=private_blind_map),
        "gates": _blocked_gates(),
        "notes": "Live saved-sample reframe diagnostic judgment.",
    }
    return write_reframe_diagnostic_judgment(payload=payload, out_dir=out_dir)


def validate_reframe_diagnostic_judgment(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_reframe_diagnostic_judgment_errors(payload, path=path))
    if errors:
        raise ReframeDiagnosticReviewError("; ".join(errors))


def iter_reframe_diagnostic_judgment_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(JUDGMENT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, JUDGMENT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != JUDGMENT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {JUDGMENT_SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("diagnostic_case_id")).strip():
        yield f"{path / 'diagnostic_case_id'}: must be non-empty"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    blind_map = _validate_blind_map(payload.get("blind_map"), path / "blind_map")
    yield from blind_map[1]
    yield from _validate_reviewer_output(
        payload.get("reviewer_output"),
        blind_map=blind_map[0],
        path=path / "reviewer_output",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def write_reframe_diagnostic_judgment(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_reframe_diagnostic_judgment(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = _string(payload["provider_metadata"].get("model")).replace("/", "__")
    path = out_dir / f"{_string(payload['diagnostic_case_id'])}.{model_slug}.reframe-diagnostic-judgment.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_reframe_diagnostic_judgment(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ReframeDiagnosticReviewError(f"{path}: payload must be an object")
    validate_reframe_diagnostic_judgment(payload, path=path)
    return payload


def build_reframe_diagnostic_result(
    *,
    contract: dict[str, object],
    judgments: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_reframe_diagnostic_contract(contract)
    for judgment in judgments:
        validate_reframe_diagnostic_judgment(judgment)
    by_case: dict[str, list[dict[str, object]]] = {}
    for judgment in judgments:
        by_case.setdefault(_string(judgment.get("diagnostic_case_id")), []).append(judgment)
    case_results: list[dict[str, object]] = []
    for case in contract["diagnostic_cases"]:
        if not isinstance(case, dict):
            continue
        diagnostic_case_id = _string(case["diagnostic_case_id"])
        case_judgments = by_case.get(diagnostic_case_id, [])
        if not case_judgments:
            continue
        labels = [_string(judgment["reviewer_output"]["diagnostic_label"]) for judgment in case_judgments]
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
            role=_string(case["diagnostic_role"]),
            labels=labels,
            families=families,
            consistency=consistency,
        )
        case_results.append(
            {
                "diagnostic_case_id": diagnostic_case_id,
                "source_case_id": _string(case["source_case_id"]),
                "diagnostic_role": _string(case["diagnostic_role"]),
                "answer_delta_specificity": _string(case["answer_delta_specificity"]),
                "reviewer_count": len(case_judgments),
                "reviewer_model_families": families,
                "diagnostic_labels": labels,
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
        "notes": "Reviewer diagnostic over saved Step 6 samples only.",
    }
    validate_reframe_diagnostic_result(payload)
    return payload


def validate_reframe_diagnostic_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_reframe_diagnostic_result_errors(payload, path=path))
    if errors:
        raise ReframeDiagnosticReviewError("; ".join(errors))


def iter_reframe_diagnostic_result_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(RESULT_FIELDS - {"notes"})
    yield from _unknown_fields(payload, RESULT_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != RESULT_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {RESULT_SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
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


def write_reframe_diagnostic_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_reframe_diagnostic_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "reframe-diagnostic-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_reframe_diagnostic_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ReframeDiagnosticReviewError(f"{path}: payload must be an object")
    validate_reframe_diagnostic_result(payload, path=path)
    return payload


def _case_from_sample(
    *,
    root: Path,
    sample_path: Path,
    diagnostic_role: str,
    loaded_sample: dict[str, object] | None = None,
) -> dict[str, object]:
    full_path = root / sample_path
    sample = loaded_sample or load_step6_calibration_sample(full_path)
    validate_step6_calibration_sample(sample)
    source_case_id = _string(sample["case_id"])
    sample_index = int(sample["sample_index"])
    diagnostic_case_id = (
        f"{source_case_id}.sample-{sample_index}."
        f"{diagnostic_role.replace('_', '-')}"
    )
    input_packet = sample["input_packet"]
    step6_output = sample["step6_output"]
    return {
        "diagnostic_case_id": diagnostic_case_id,
        "source_case_id": source_case_id,
        "sample_ref": str(sample_path),
        "sample_index": sample_index,
        "diagnostic_role": diagnostic_role,
        "case_brief": _string(input_packet.get("case_brief")),
        "anchor_visible": _string(input_packet.get("anchor_visible_candidate")),
        "step6_visible": _string(step6_output.get("answer_core")),
        "ledger_signal": _string(sample.get("ledger_signal")),
        "answer_delta_specificity": _string(sample.get("answer_delta_specificity")),
        "answer_delta_summary": _answer_delta_summary(step6_output),
    }


def _answer_delta_summary(step6_output: object) -> dict[str, list[str]]:
    if not isinstance(step6_output, dict):
        return {}
    ledger = step6_output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return {}
    summary = {
        "added_entities": [],
        "removed_entities": [],
        "reordered_sequences": [],
        "reframed_emphasis": [],
    }
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
    reframe_results = [
        result
        for result in case_results
        if result.get("diagnostic_role") == "reframe_only_diagnostic"
    ]
    useful = sum(1 for result in reframe_results if result.get("confirmed_label") == "reframe_useful")
    suppressed = sum(
        1
        for result in reframe_results
        if result.get("confirmed_label") == "reframe_correctly_suppressed"
    )
    ambiguous = sum(1 for result in case_results if result.get("confirmed_label") == "ambiguous")
    tension = sum(
        1
        for result in case_results
        if result.get("reviewer_label_consistency") == "tension_detected"
    )
    if useful:
        read = "answer_delta_vocabulary_design_review_required"
        action = "review_answer_delta_vocabulary_for_structural_framing_delta"
    elif reframe_results and suppressed == len(reframe_results) and not ambiguous and not tension:
        read = "answer_delta_guardrail_supported"
        action = "keep_answer_delta_guardrail_and_continue_calibration"
    else:
        read = "diagnostic_inconclusive"
        action = "inspect_ambiguous_or_tense_reviewer_records_before_redesign"
    return {
        "case_count": len(case_results),
        "reframe_case_count": len(reframe_results),
        "confirmed_reframe_useful_count": useful,
        "confirmed_reframe_correctly_suppressed_count": suppressed,
        "ambiguous_count": ambiguous,
        "tension_count": tension,
        "control_case_count": len(case_results) - len(reframe_results),
        "diagnostic_read": read,
        "recommended_next_action": action,
    }


def _confirmed_label(
    *,
    role: str,
    labels: list[str],
    families: list[str],
    consistency: str,
) -> str:
    if len(families) < 2 or len(labels) < 2:
        return "not_observed"
    if consistency == "tension_detected":
        return "ambiguous"
    step6_positive = {"step6_better", "step6_non_inferior"}
    if role == "reframe_only_diagnostic":
        if all(label in step6_positive for label in labels):
            return "reframe_useful"
        if all(label == "anchor_better" for label in labels):
            return "reframe_correctly_suppressed"
        return "ambiguous"
    if all(label in step6_positive for label in labels):
        return "control_step6_supported"
    if all(label == "anchor_better" for label in labels):
        return "control_anchor_supported"
    return "ambiguous"


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
        if label == "step6_non_inferior" and winner_arm not in {"step6_visible", "tie", "anchor_visible"}:
            return "tension_detected"
    return "aligned"


def _normalize_reviewer_output(value: object, *, blind_map: dict[str, str]) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    label = _string(value.get("diagnostic_label"))
    if label not in ALLOWED_DIAGNOSTIC_LABELS:
        label = "ambiguous"
    winner = _string(value.get("winner_label"))
    if winner not in set(blind_map) | {"tie"}:
        winner = "tie"
    confidence = _string(value.get("confidence"))
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    return {
        "diagnostic_label": label,
        "winner_label": winner,
        "confidence": confidence,
        "rationale": _string(value.get("rationale")) or "Reviewer did not provide rationale.",
        "reframe_value_if_any": _string_list(value.get("reframe_value_if_any"), fallback="none"),
        "anchor_strengths": _string_list(value.get("anchor_strengths"), fallback="none"),
        "payload_loss_or_bloat": _string_list(value.get("payload_loss_or_bloat"), fallback="none"),
    }


def _reviewer_system_prompt() -> str:
    return (
        "You are a blind reviewer for a research-only calibration diagnostic. "
        "Return strict JSON only. Judge the observable usefulness of the two "
        "answers for the user's actual decision. Do not reward verbosity, clever "
        "framing, or private process labels. Prefer the answer that is more useful, "
        "grounded, and action-guiding without losing concrete payload."
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
    if _string(value.get("diagnostic_role")) not in ALLOWED_ROLES:
        yield f"{path / 'diagnostic_role'}: invalid role"
    if not _string(value.get("diagnostic_case_id")).strip():
        yield f"{path / 'diagnostic_case_id'}: must be non-empty"
    if not _string(value.get("source_case_id")).strip():
        yield f"{path / 'source_case_id'}: must be non-empty"
    if not _string(value.get("sample_ref")).startswith("research/"):
        yield f"{path / 'sample_ref'}: must point to research artifact"
    if not isinstance(value.get("sample_index"), int):
        yield f"{path / 'sample_index'}: must be integer"
    for field in ("case_brief", "anchor_visible", "step6_visible", "ledger_signal", "answer_delta_specificity"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if not isinstance(value.get("answer_delta_summary"), dict):
        yield f"{path / 'answer_delta_summary'}: must be object"


def _validate_provider_metadata(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: provider metadata must be object"
        return
    if "provider" not in value and "provider_name" not in value:
        yield f"{path}: provider or provider_name is required"
    if not _string(value.get("model")).strip():
        yield f"{path / 'model'}: must be non-empty"
    if not _string(value.get("model_family")).strip():
        yield f"{path / 'model_family'}: must be non-empty"
    if not _string(value.get("status")).strip():
        yield f"{path / 'status'}: must be non-empty"
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
    if _string(value.get("diagnostic_label")) not in ALLOWED_DIAGNOSTIC_LABELS:
        yield f"{path / 'diagnostic_label'}: invalid label"
    winner = _string(value.get("winner_label"))
    if winner != "tie" and winner not in blind_map:
        yield f"{path / 'winner_label'}: must be A, B, or tie"
    if _string(value.get("confidence")) not in {"high", "medium", "low"}:
        yield f"{path / 'confidence'}: invalid confidence"
    for field in ("reframe_value_if_any", "anchor_strengths", "payload_loss_or_bloat"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"


def _validate_case_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case result must be object"
        return
    yield from _unknown_fields(value, CASE_RESULT_FIELDS, path)
    yield from _missing_fields(value, CASE_RESULT_FIELDS, path)
    if _string(value.get("diagnostic_role")) not in ALLOWED_ROLES:
        yield f"{path / 'diagnostic_role'}: invalid role"
    if _string(value.get("confirmed_label")) not in ALLOWED_CONFIRMED_LABELS:
        yield f"{path / 'confirmed_label'}: invalid label"
    if _string(value.get("reviewer_label_consistency")) not in {"aligned", "tension_detected", "not_applicable"}:
        yield f"{path / 'reviewer_label_consistency'}: invalid consistency"
    for field in ("reviewer_model_families", "diagnostic_labels", "reviewer_winner_arms"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    for field in (
        "case_count",
        "reframe_case_count",
        "confirmed_reframe_useful_count",
        "confirmed_reframe_correctly_suppressed_count",
        "ambiguous_count",
        "tension_count",
        "control_case_count",
    ):
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    if _string(value.get("diagnostic_read")) not in {
        "answer_delta_vocabulary_design_review_required",
        "answer_delta_guardrail_supported",
        "diagnostic_inconclusive",
    }:
        yield f"{path / 'diagnostic_read'}: invalid diagnostic read"


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


def _case_by_id(contract: dict[str, object], diagnostic_case_id: str) -> dict[str, object]:
    cases = contract.get("diagnostic_cases")
    if not isinstance(cases, list):
        raise ReframeDiagnosticReviewError("diagnostic_cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("diagnostic_case_id") == diagnostic_case_id:
            return case
    raise ReframeDiagnosticReviewError(f"unknown diagnostic case: {diagnostic_case_id}")


def _blocked_gates() -> dict[str, bool]:
    return {"runtime_wiring_allowed": False, "skill_update_allowed": False}


def _provider_metadata_dict(metadata: object) -> dict[str, object]:
    if hasattr(metadata, "__dict__"):
        raw = dict(vars(metadata))
    elif isinstance(metadata, dict):
        raw = dict(metadata)
    else:
        raw = {}
    return {str(key): value for key, value in raw.items() if value is not None}


def _model_family(model: str) -> str:
    if "/" in model:
        return model.split("/", 1)[0].split(".", 1)[0]
    return model.split("-", 1)[0] if model else "unknown"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        raise ReframeDiagnosticReviewError(f"env file missing: {path}")
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
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--live-review", action="store_true")
    parser.add_argument("--rebuild-result", action="store_true")
    parser.add_argument("--diagnostic-case-id", action="append", default=[])
    parser.add_argument("--reviewer-model", action="append", default=[])
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise ReframeDiagnosticReviewError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_reframe_diagnostic_contract(payload, path=path)
            elif schema == JUDGMENT_SCHEMA_VERSION:
                validate_reframe_diagnostic_judgment(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_reframe_diagnostic_result(payload, path=path)
            else:
                raise ReframeDiagnosticReviewError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_reframe_diagnostic_contract(args.contract)
        if args.contract is not None
        else build_reframe_diagnostic_contract(root=Path.cwd())
    )
    if args.write_contract:
        print(write_reframe_diagnostic_contract(payload=contract, out_dir=args.out_dir))
        return 0

    if args.rebuild_result:
        judgment_paths = sorted(args.judgment_dir.glob("*.reframe-diagnostic-judgment.v1.json"))
        result = build_reframe_diagnostic_result(
            contract=contract,
            judgments=[load_reframe_diagnostic_judgment(path) for path in judgment_paths],
        )
        print(write_reframe_diagnostic_result(payload=result, out_dir=args.out_dir))
        return 0

    if args.live_review:
        case_ids = args.diagnostic_case_id or [
            _string(case["diagnostic_case_id"])
            for case in contract["diagnostic_cases"]
            if isinstance(case, dict)
        ]
        models = args.reviewer_model or list(DEFAULT_REVIEWER_MODELS)
        outputs = []
        for case_id in case_ids:
            for model in models:
                output = run_live_reviewer(
                    contract=contract,
                    diagnostic_case_id=case_id,
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
            result = build_reframe_diagnostic_result(
                contract=contract,
                judgments=[load_reframe_diagnostic_judgment(path) for path in outputs],
            )
            print(write_reframe_diagnostic_result(payload=result, out_dir=args.out_dir))
        return 0

    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
