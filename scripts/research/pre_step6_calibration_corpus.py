#!/usr/bin/env python3
"""Research-only pre-Step-6 calibration corpus runner.

This is the corpus gate after the bridge and false-positive probes. It
pre-registers a 12-20 case corpus, runs repeated Step 6 samples, and reports
stability plus answer-delta specificity. Runtime and SKILL.md remain dormant.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import signal
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_bridge_step6_ledger_replay import (
    derive_answer_delta_specificity as derive_bridge_answer_delta_specificity,
)
from pre_step6_false_positive_visibility_probe import (
    build_false_positive_probe_contract,
)
from pre_step6_false_standdown_bridge_probe import build_bridge_probe_contract
from pre_step6_marker_entity_loss_followup import build_marker_entity_followup_contract
from pre_step6_raw_artifacts import validate_public_answer_hygiene


CONTRACT_SCHEMA_VERSION = "pre_step6_calibration_corpus.v1"
SAMPLE_SCHEMA_VERSION = "pre_step6_calibration_step6_sample.v1"
RESULT_SCHEMA_VERSION = "pre_step6_calibration_step6_result.v1"
STABILITY_REVIEW_SCHEMA_VERSION = "pre_step6_calibration_stability_review.v1"
RUNTIME_POLICY = "runtime_dormant"
STATUS = "research_only"
EXPERIMENT_ID = "pre_step6_calibration_corpus_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-calibration-corpus")
DEFAULT_SAMPLE_DIR = DEFAULT_OUT_DIR / "step6-samples"
DEFAULT_SAMPLES_PER_CASE = 3
CALIBRATION_STEP6_MODEL = "moonshotai/kimi-k2.6"
CASE_BUCKETS = (
    "high_clutter",
    "sequencing_or_problem_shape",
    "sensitive_safety_legal",
    "negative_control",
)
PAIR_BUCKET = "v60_on_off_pairs"
REQUIRED_BUCKETS = {
    "high_clutter": 3,
    "sequencing_or_problem_shape": 3,
    "sensitive_safety_legal": 3,
    "negative_control": 3,
    PAIR_BUCKET: 2,
}
ALLOWED_V60_MODES = frozenset({"off", "on", "not_applicable"})
ALLOWED_LEDGER_SIGNALS = frozenset(
    {"additive_pressure_present", "all_private_or_confirming", "missing_or_unclear"}
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
UNLOCKING_ANSWER_DELTA_SPECIFICITY = frozenset(
    {"concrete_delta_present", "structural_delta_present"}
)
SOURCE_IDS = ("anchor_visible_candidate", "deck_pressure_candidate")
DETERMINISTIC_ROLE = (
    "validate_calibration_case",
    "derive_ledger_signal",
    "derive_answer_delta_specificity",
    "preserve_repeated_sample_custody",
)
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "case_count",
        "sample_plan",
        "bucket_status",
        "floor_status",
        "cases",
        "gates",
        "notes",
    }
)
SAMPLE_PLAN_FIELDS = frozenset(
    {
        "samples_per_case",
        "step6_model",
        "reviewer_phase",
        "stability_rule",
        "tracked_metrics",
    }
)
CASE_FIELDS = frozenset(
    {
        "case_id",
        "base_case_id",
        "case_type_tags",
        "calibration_role",
        "selection_timing",
        "case_brief",
        "pre_registered_expectation",
        "v60_toggle_pair_id",
        "v60_mode",
        "v60_evidence_source",
        "v60_private_context",
        "answer_candidates",
    }
)
CANDIDATE_FIELDS = frozenset({"anchor_visible", "deck_pressure"})
BUCKET_STATUS_FIELDS = frozenset({"bucket", "required", "observed", "met"})
SAMPLE_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "case_id",
        "base_case_id",
        "sample_index",
        "provider_metadata",
        "input_packet",
        "step6_output",
        "ledger_signal",
        "answer_delta_specificity",
        "deterministic_role",
        "gates",
        "notes",
    }
)
INPUT_PACKET_FIELDS = frozenset(
    {
        "case_brief",
        "case_type_tags",
        "pre_registered_expectation",
        "v60_mode",
        "v60_private_context",
        "anchor_visible_candidate",
        "deck_pressure_candidate",
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
STEP6_OUTPUT_FIELDS = frozenset({"answer_core", "private_visibility_ledger"})
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
LEGACY_OPTIONAL_ANSWER_DELTA_FIELDS = frozenset({"structural_delta"})
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
        "sample_count",
        "ledger_signal_counts",
        "answer_delta_specificity_counts",
        "stability_label",
        "unlock_count",
        "reframe_only_count",
        "structural_delta_count",
        "structural_delta_field_count",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
STABILITY_CLASSIFICATIONS = frozenset(
    {
        "stable_positive",
        "stable_standdown",
        "borderline_unlock",
        "abstract_additive_only",
        "unstable_mixed",
        "incomplete_sampling",
    }
)
STABILITY_REVIEW_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "source_result_ref",
        "case_reviews",
        "aggregate",
        "gates",
        "notes",
    }
)
STABILITY_CASE_REVIEW_FIELDS = frozenset(
    {
        "case_id",
        "sample_count",
        "stability_classification",
        "reviewer_phase_eligibility",
        "ledger_signal_counts",
        "answer_delta_specificity_counts",
        "unlock_count",
        "reframe_only_count",
        "structural_delta_count",
        "structural_delta_field_count",
        "sample_refs",
        "rationale",
    }
)
STABILITY_AGGREGATE_FIELDS = frozenset(
    {
        "case_count",
        "stable_positive_count",
        "stable_standdown_count",
        "borderline_unlock_count",
        "abstract_additive_only_count",
        "unstable_mixed_count",
        "incomplete_sampling_count",
        "repeat_sample_case_ids",
        "reviewer_phase_decision",
        "recommended_next_action",
    }
)


class CalibrationCorpusError(ValueError):
    pass


def build_calibration_corpus_contract(*, root: Path) -> dict[str, object]:
    cases = _calibration_cases(Path(root))
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_calibration_only",
        "case_count": len(cases),
        "sample_plan": {
            "samples_per_case": DEFAULT_SAMPLES_PER_CASE,
            "step6_model": CALIBRATION_STEP6_MODEL,
            "reviewer_phase": (
                "Run after Step 6 stability sampling from saved samples; not mixed "
                "into the sampling call."
            ),
            "stability_rule": (
                "A case is stable only when all n=3 samples produce the same "
                "ledger_signal and the same answer_delta_specificity bucket."
            ),
            "tracked_metrics": [
                "ledger_signal_distribution",
                "answer_delta_specificity_distribution",
                "reframed_emphasis_only_frequency",
                "structural_delta_only_frequency",
                "structural_delta_field_usage_frequency",
                "unlock_count",
                "v60_on_off_pair_differences",
                "reviewer_tension_rate_after_reviewer_phase",
            ],
        },
        "bucket_status": _bucket_status(cases),
        "floor_status": _floor_status(cases),
        "cases": cases,
        "gates": _blocked_gates(),
        "notes": (
            "Pre-registered research-only calibration corpus. V60 pair cases use "
            "the current synthetic V60 pressure fixtures and are labeled as such; "
            "they do not by themselves promote runtime V60 integration."
        ),
    }
    validate_calibration_corpus_contract(payload, root=root)
    return payload


def load_calibration_corpus_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise CalibrationCorpusError(f"{path}: payload must be an object")
    return payload


def write_calibration_corpus_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_calibration_corpus_contract(payload, root=Path.cwd())
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "calibration-corpus.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def validate_calibration_corpus_contract(
    payload: dict[str, object],
    *,
    root: Path | None = None,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_calibration_corpus_contract_errors(payload, root=root, path=path))
    if errors:
        raise CalibrationCorpusError("; ".join(errors))


def iter_calibration_corpus_contract_errors(
    payload: dict[str, object],
    *,
    root: Path | None = None,
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
    if payload.get("promotion_effect") != "none_calibration_only":
        yield f"{path / 'promotion_effect'}: must be none_calibration_only"
    yield from _validate_sample_plan(payload.get("sample_plan"), path / "sample_plan")
    cases = payload.get("cases")
    if not isinstance(cases, list):
        yield f"{path / 'cases'}: must be a list"
        return
    if payload.get("case_count") != len(cases):
        yield f"{path / 'case_count'}: must match cases length"
    for index, case in enumerate(cases):
        yield from _validate_case(case, path / "cases" / str(index), root=root)
    expected_bucket_status = _bucket_status([case for case in cases if isinstance(case, dict)])
    if payload.get("bucket_status") != expected_bucket_status:
        yield f"{path / 'bucket_status'}: must match cases"
    for index, row in enumerate(payload.get("bucket_status", [])):
        if isinstance(row, dict):
            yield from _unknown_fields(row, BUCKET_STATUS_FIELDS, path / "bucket_status" / str(index))
            yield from _missing_fields(row, BUCKET_STATUS_FIELDS, path / "bucket_status" / str(index))
    if payload.get("floor_status") != _floor_status([case for case in cases if isinstance(case, dict)]):
        yield f"{path / 'floor_status'}: must match corpus coverage"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_step6_calibration_prompts(
    *,
    contract: dict[str, object],
    case_id: str,
    sample_index: int,
) -> dict[str, str]:
    validate_calibration_corpus_contract(contract, root=Path.cwd())
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    system_prompt = (
        "You are Step 6, the primary reasoning voice. You receive broad private "
        "context and decide what the user should see. Use your cognition; the "
        "private material is not a command. Return strict JSON only."
    )
    user_prompt = "\n\n".join(
        [
            "CALIBRATION CONTEXT",
            json.dumps(
                {
                    "case_id": case_id,
                    "sample_index": sample_index,
                    "case_type_tags": case["case_type_tags"],
                    "case_brief": case["case_brief"],
                    "pre_registered_expectation": case["pre_registered_expectation"],
                    "v60_mode": case["v60_mode"],
                    "v60_evidence_source": case["v60_evidence_source"],
                    "v60_private_context": case["v60_private_context"],
                    "anchor_visible_candidate": candidates["anchor_visible"],
                    "deck_pressure_candidate": candidates["deck_pressure"],
                },
                indent=2,
                ensure_ascii=False,
            ),
            "TASK",
            (
                "Write the best public-clean answer_core. You may keep the anchor, "
                "use the deck pressure, combine them, reject either, or keep pressure "
                "private. Broad private material is allowed; do not prematurely narrow "
                "your thinking. But do not overstate deck pressure as visibly additive "
                "unless it changes the public answer in a concrete or specific "
                "structural way. Preserve tripwires, actor sequence, named resources, "
                "dates/windows, evidence checks, and specific entities when they matter. "
                "Do not expose private labels or machinery."
            ),
            "RESPONSE JSON SHAPE",
            json.dumps(
                {
                    "answer_core": "Public-clean answer.",
                    "private_visibility_ledger": [
                        {
                            "source_id": "anchor_visible_candidate | deck_pressure_candidate",
                            "disposition": (
                                "used | combined | rejected | deferred | private_guardrail"
                            ),
                            "novelty_role": (
                                "visible_backbone | additive_pressure | "
                                "confirming_support | private_guardrail"
                            ),
                            "why": "Private rationale.",
                            "visible_effect": "Specific public change, or 'none'.",
                            "answer_delta": {
                                "added_entities": [
                                    "Concrete entities or payload newly added."
                                ],
                                "removed_entities": [
                                    "Concrete anchor entities removed, if any."
                                ],
                                "reordered_sequences": [
                                    "Concrete sequence/order changes, if any."
                                ],
                                "structural_delta": [
                                    (
                                        "Specific structural change such as a stop condition, "
                                        "unlock condition, decision boundary, test design, "
                                        "or commitment boundary. Do not use vague entries "
                                        "like 'added structural framing'."
                                    )
                                ],
                                "reframed_emphasis": [
                                    "Abstract emphasis, tone, or framing shifts."
                                ],
                            },
                        }
                    ],
                },
                indent=2,
            ),
        ]
    )
    return {"system_prompt": system_prompt, "user_prompt": user_prompt}


def build_static_step6_sample(
    *,
    contract: dict[str, object],
    case_id: str,
    sample_index: int,
    ledger_signal: str,
    answer_delta_specificity: str,
) -> dict[str, object]:
    validate_calibration_corpus_contract(contract, root=Path.cwd())
    case = _case_by_id(contract, case_id)
    candidates = _answer_candidates(case, case_id)
    step6_output = _static_step6_output(
        candidates=candidates,
        ledger_signal=ledger_signal,
        answer_delta_specificity=answer_delta_specificity,
    )
    payload = _sample_payload(
        case=case,
        sample_index=sample_index,
        provider_metadata={
            "provider": "static",
            "model": "static-calibration-fixture",
            "model_family": "static",
            "status": "ok",
        },
        step6_output=step6_output,
        notes="Static calibration sample fixture.",
    )
    validate_step6_calibration_sample(payload)
    return payload


def run_live_step6_sample(
    *,
    contract: dict[str, object],
    case_id: str,
    sample_index: int,
    provider: str,
    model: str,
    env_file: Path | None,
    out_dir: Path,
    dry_run: bool,
) -> Path | None:
    if env_file is not None:
        _load_env_file(env_file)
    if model:
        os.environ["LOLLA_OPENROUTER_MODEL"] = model
    prompts = build_step6_calibration_prompts(
        contract=contract,
        case_id=case_id,
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
    try:
        if hasattr(signal, "SIGALRM"):
            previous_handler = signal.getsignal(signal.SIGALRM)
            signal.signal(signal.SIGALRM, _raise_live_sample_timeout)
            signal.setitimer(signal.ITIMER_REAL, _live_sample_outer_timeout_seconds())
            try:
                output, metadata = client.run_json_with_metadata(
                    prompts["system_prompt"],
                    prompts["user_prompt"],
                    stage="pre_step6_calibration_corpus",
                    tendency_id=f"{case_id}:sample-{sample_index}",
                )
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, previous_handler)
        else:
            output, metadata = client.run_json_with_metadata(
                prompts["system_prompt"],
                prompts["user_prompt"],
                stage="pre_step6_calibration_corpus",
                tendency_id=f"{case_id}:sample-{sample_index}",
            )
    except CalibrationCorpusError:
        raise
    except Exception as exc:
        raise CalibrationCorpusError(
            "live calibration Step 6 sample raised "
            f"{type(exc).__name__}: {exc}"
        ) from exc
    provider_metadata = _provider_metadata_dict(metadata)
    if _string(provider_metadata.get("status")) != "ok":
        raise CalibrationCorpusError(
            "live calibration Step 6 sample failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    case = _case_by_id(contract, case_id)
    sample = _sample_payload(
        case=case,
        sample_index=sample_index,
        provider_metadata=provider_metadata,
        step6_output=_normalize_step6_output(output),
        notes="Live research-only Step 6 calibration sample.",
    )
    return write_step6_calibration_sample(payload=sample, out_dir=out_dir)


def write_step6_calibration_sample(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_step6_calibration_sample(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = calibration_sample_path(
        out_dir=out_dir,
        case_id=_string(payload["case_id"]),
        sample_index=int(payload["sample_index"]),
    )
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def calibration_sample_path(*, out_dir: Path, case_id: str, sample_index: int) -> Path:
    return out_dir / f"{case_id}.sample-{sample_index}.calibration-step6.v1.json"


def load_step6_calibration_sample(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise CalibrationCorpusError(f"{path}: payload must be an object")
    return payload


def validate_step6_calibration_sample(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_step6_calibration_sample_errors(payload, path=path))
    if errors:
        raise CalibrationCorpusError("; ".join(errors))


def iter_step6_calibration_sample_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(SAMPLE_FIELDS - {"notes"})
    yield from _unknown_fields(payload, SAMPLE_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != SAMPLE_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {SAMPLE_SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if not _string(payload.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if not isinstance(payload.get("sample_index"), int) or payload.get("sample_index") < 0:
        yield f"{path / 'sample_index'}: must be non-negative integer"
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    yield from _validate_input_packet(payload.get("input_packet"), path / "input_packet")
    step6_output = payload.get("step6_output")
    yield from _validate_step6_output(step6_output, path / "step6_output")
    expected_signal = derive_ledger_signal(step6_output)
    if payload.get("ledger_signal") != expected_signal:
        yield f"{path / 'ledger_signal'}: must be derived from Step 6 ledger"
    expected_specificity = derive_answer_delta_specificity(step6_output)
    if payload.get("answer_delta_specificity") != expected_specificity:
        yield f"{path / 'answer_delta_specificity'}: must be derived from Step 6 ledger"
    if payload.get("deterministic_role") != list(DETERMINISTIC_ROLE):
        yield f"{path / 'deterministic_role'}: invalid deterministic role"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def build_step6_calibration_result(
    *,
    contract: dict[str, object],
    samples: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_calibration_corpus_contract(contract, root=Path.cwd())
    for sample in samples:
        validate_step6_calibration_sample(sample)
    case_results = []
    by_case: dict[str, list[dict[str, object]]] = {}
    for sample in samples:
        by_case.setdefault(_string(sample.get("case_id")), []).append(sample)
    for case_id in sorted(by_case):
        case_samples = sorted(by_case[case_id], key=lambda item: int(item["sample_index"]))
        signal_counts = _counts(_string(sample.get("ledger_signal")) for sample in case_samples)
        specificity_counts = _counts(
            _string(sample.get("answer_delta_specificity")) for sample in case_samples
        )
        sample_count = len(case_samples)
        case_results.append(
            {
                "case_id": case_id,
                "sample_count": sample_count,
                "ledger_signal_counts": signal_counts,
                "answer_delta_specificity_counts": specificity_counts,
                "stability_label": _stability_label(signal_counts, specificity_counts, sample_count),
                "unlock_count": sum(
                    1
                    for sample in case_samples
                    if sample.get("ledger_signal") == "additive_pressure_present"
                    and sample.get("answer_delta_specificity")
                    in UNLOCKING_ANSWER_DELTA_SPECIFICITY
                ),
                "reframe_only_count": sum(
                    1
                    for sample in case_samples
                    if sample.get("answer_delta_specificity") == "reframe_only"
                ),
                "structural_delta_count": sum(
                    1
                    for sample in case_samples
                    if sample.get("answer_delta_specificity") == "structural_delta_present"
                ),
                "structural_delta_field_count": sum(
                    1 for sample in case_samples if _sample_has_structural_delta_field(sample)
                ),
            }
        )
    aggregate = {
        "case_count": len(case_results),
        "sample_count": len(samples),
        "unstable_case_count": sum(
            1 for result in case_results if result["stability_label"] == "unstable"
        ),
        "incomplete_case_count": sum(
            1 for result in case_results if result["stability_label"] == "incomplete_sampling"
        ),
        "stable_case_count": sum(
            1 for result in case_results if result["stability_label"] == "stable"
        ),
        "unlock_sample_count": sum(int(result["unlock_count"]) for result in case_results),
        "reframe_only_sample_count": sum(
            int(result["reframe_only_count"]) for result in case_results
        ),
        "structural_delta_sample_count": sum(
            int(result["structural_delta_count"]) for result in case_results
        ),
        "structural_delta_field_sample_count": sum(
            int(result["structural_delta_field_count"]) for result in case_results
        ),
        "reviewer_tension_status": "not_run",
        "calibration_read": _calibration_read(case_results, contract),
    }
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_calibration_only",
        "case_results": case_results,
        "aggregate": aggregate,
        "gates": _blocked_gates(),
        "notes": (
            "Step 6 stability phase only. Reviewer adjudication runs from saved "
            "samples after this phase."
        ),
    }
    validate_step6_calibration_result(payload)
    return payload


def write_step6_calibration_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_step6_calibration_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "calibration-step6-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def build_step6_calibration_stability_review(
    *,
    contract: dict[str, object],
    result: dict[str, object],
    samples: Sequence[dict[str, object]],
    source_result_ref: str = "calibration-step6-result.v1.json",
) -> dict[str, object]:
    validate_calibration_corpus_contract(contract, root=Path.cwd())
    validate_step6_calibration_result(result)
    for sample in samples:
        validate_step6_calibration_sample(sample)
    samples_by_case: dict[str, list[dict[str, object]]] = {}
    for sample in samples:
        samples_by_case.setdefault(_string(sample.get("case_id")), []).append(sample)
    case_reviews: list[dict[str, object]] = []
    for case_result in result.get("case_results", []):
        if not isinstance(case_result, dict):
            continue
        case_id = _string(case_result.get("case_id"))
        classification = _stability_classification(case_result)
        case_samples = sorted(
            samples_by_case.get(case_id, []),
            key=lambda sample: int(sample.get("sample_index") or 0),
        )
        case_reviews.append(
            {
                "case_id": case_id,
                "sample_count": int(case_result.get("sample_count") or 0),
                "stability_classification": classification,
                "reviewer_phase_eligibility": _reviewer_phase_eligibility(classification),
                "ledger_signal_counts": dict(case_result.get("ledger_signal_counts") or {}),
                "answer_delta_specificity_counts": dict(
                    case_result.get("answer_delta_specificity_counts") or {}
                ),
                "unlock_count": int(case_result.get("unlock_count") or 0),
                "reframe_only_count": int(case_result.get("reframe_only_count") or 0),
                "structural_delta_count": int(case_result.get("structural_delta_count") or 0),
                "structural_delta_field_count": int(
                    case_result.get("structural_delta_field_count") or 0
                ),
                "sample_refs": [
                    f"step6-samples/{case_id}.sample-{sample['sample_index']}.calibration-step6.v1.json"
                    for sample in case_samples
                ],
                "rationale": _stability_rationale(case_result, classification),
            }
        )
    aggregate = _stability_review_aggregate(case_reviews)
    payload = {
        "schema_version": STABILITY_REVIEW_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_calibration_only",
        "source_result_ref": source_result_ref,
        "case_reviews": case_reviews,
        "aggregate": aggregate,
        "gates": _blocked_gates(),
        "notes": (
            "No-redesign review of saved Step 6 calibration samples. This artifact "
            "classifies stability before any reviewer adjudication."
        ),
    }
    validate_step6_calibration_stability_review(payload)
    return payload


def write_step6_calibration_stability_review(
    *,
    payload: dict[str, object],
    out_dir: Path,
) -> Path:
    validate_step6_calibration_stability_review(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "calibration-stability-review.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_step6_calibration_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise CalibrationCorpusError(f"{path}: payload must be an object")
    validate_step6_calibration_result(payload, path=path)
    return payload


def load_step6_calibration_stability_review(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise CalibrationCorpusError(f"{path}: payload must be an object")
    validate_step6_calibration_stability_review(payload, path=path)
    return payload


def validate_step6_calibration_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_step6_calibration_result_errors(payload, path=path))
    if errors:
        raise CalibrationCorpusError("; ".join(errors))


def iter_step6_calibration_result_errors(
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
    if payload.get("promotion_effect") != "none_calibration_only":
        yield f"{path / 'promotion_effect'}: must be none_calibration_only"
    results = payload.get("case_results")
    if not isinstance(results, list):
        yield f"{path / 'case_results'}: must be a list"
    else:
        for index, result in enumerate(results):
            yield from _validate_case_result(result, path / "case_results" / str(index))
    aggregate = payload.get("aggregate")
    if not isinstance(aggregate, dict):
        yield f"{path / 'aggregate'}: must be an object"
    elif aggregate.get("reviewer_tension_status") != "not_run":
        yield f"{path / 'aggregate' / 'reviewer_tension_status'}: must be not_run"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_step6_calibration_stability_review(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_step6_calibration_stability_review_errors(payload, path=path))
    if errors:
        raise CalibrationCorpusError("; ".join(errors))


def iter_step6_calibration_stability_review_errors(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> Iterable[str]:
    if not isinstance(payload, dict):
        yield f"{path}: payload must be an object"
        return
    required = tuple(STABILITY_REVIEW_FIELDS - {"notes"})
    yield from _unknown_fields(payload, STABILITY_REVIEW_FIELDS, path)
    yield from _missing_fields(payload, required, path)
    if any(field not in payload for field in required):
        return
    if payload.get("schema_version") != STABILITY_REVIEW_SCHEMA_VERSION:
        yield f"{path / 'schema_version'}: must be {STABILITY_REVIEW_SCHEMA_VERSION}"
    if payload.get("status") != STATUS:
        yield f"{path / 'status'}: must be {STATUS}"
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("experiment_id") != EXPERIMENT_ID:
        yield f"{path / 'experiment_id'}: must be {EXPERIMENT_ID}"
    if payload.get("promotion_effect") != "none_calibration_only":
        yield f"{path / 'promotion_effect'}: must be none_calibration_only"
    if not _string(payload.get("source_result_ref")).strip():
        yield f"{path / 'source_result_ref'}: must be non-empty"
    reviews = payload.get("case_reviews")
    if not isinstance(reviews, list):
        yield f"{path / 'case_reviews'}: must be a list"
    else:
        for index, review in enumerate(reviews):
            yield from _validate_stability_case_review(review, path / "case_reviews" / str(index))
    yield from _validate_stability_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def derive_ledger_signal(step6_output: object) -> str:
    if not isinstance(step6_output, dict):
        return "missing_or_unclear"
    ledger = step6_output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return "missing_or_unclear"
    deck_items = [
        item
        for item in ledger
        if isinstance(item, dict) and item.get("source_id") == "deck_pressure_candidate"
    ]
    if not deck_items:
        return "missing_or_unclear"
    for item in deck_items:
        if (
            item.get("novelty_role") == "additive_pressure"
            and item.get("disposition") in {"used", "combined"}
        ):
            return "additive_pressure_present"
    if all(
        item.get("novelty_role") in {"confirming_support", "private_guardrail"}
        for item in deck_items
    ):
        return "all_private_or_confirming"
    return "missing_or_unclear"


def derive_answer_delta_specificity(step6_output: object) -> str:
    return derive_bridge_answer_delta_specificity(
        _bridge_shaped_step6_output(step6_output)
    )


def _calibration_cases(root: Path) -> list[dict[str, object]]:
    fixed = _fixed_suite_cases(root)
    bridge = _bridge_cases()
    false_positive = _false_positive_cases()
    marker = _marker_cases()
    scratch = _scratch_cases(root)
    return [
        _v60_variant(fixed["founder-grant-marcus-equity.high-clutter"], mode="off"),
        _v60_variant(fixed["founder-grant-marcus-equity.high-clutter"], mode="on"),
        _v60_variant(fixed["third-year-phd-student.v2"], mode="off"),
        _v60_variant(fixed["third-year-phd-student.v2"], mode="on"),
        fixed["mid-level-consultant-report-2"],
        fixed["mother-address-year"],
        bridge["bridge-high-clutter-sensitive-overlay"],
        bridge["bridge-sensitive-anchor-misses-tripwire"],
        bridge["bridge-sequencing-sensitive-boundary"],
        false_positive["fp-bevelin-irrelevant-incentives"],
        false_positive["fp-polya-true-but-useless"],
        false_positive["fp-marker-preserved-entity-lost"],
        marker["marker-entity-attempt-1-resource-generalization"],
        marker["marker-entity-attempt-2-tripwire-compression"],
        marker["marker-entity-attempt-3-actor-sequence-blur"],
        scratch["startup-pivot-new-run2"],
        scratch["multi-offer-new-run2"],
    ]


def _fixed_suite_cases(root: Path) -> dict[str, dict[str, object]]:
    specs = {
        "founder-grant-marcus-equity.high-clutter": {
            "tags": ["high_clutter"],
            "role": "positive_seed",
            "expectation": "deck_pressure_often_material_but_answer_delta_required",
            "anchor": (
                root
                / "research/pre-step6-rendered-hybrid-answer-cores/"
                "founder-grant-marcus-equity.high-clutter.native.rendered-hybrid-answer-core.v1.json"
            ),
            "deck": (
                root
                / "research/pre-step6-card-deck-replays/"
                "founder-grant-marcus-equity.high-clutter.card-deck-replay.v1.json"
            ),
            "problem": root / "research/pre-step6-problem-states/founder-grant-marcus-equity.high-clutter.problem-state.v1.json",
        },
        "third-year-phd-student.v2": {
            "tags": ["sequencing_or_problem_shape"],
            "role": "positive_seed",
            "expectation": "deck_pressure_may_add_sequence_but_should_not_bloat",
            "anchor": (
                root
                / "research/pre-step6-rendered-hybrid-answer-cores/"
                "third-year-phd-student.native.rendered-hybrid-answer-core.v1.json"
            ),
            "deck": (
                root
                / "research/pre-step6-card-deck-replays/"
                "third-year-phd-student.v2.card-deck-replay.v1.json"
            ),
            "problem": root / "research/pre-step6-problem-states/third-year-phd-student.problem-state.v1.json",
        },
        "mid-level-consultant-report-2": {
            "tags": ["sensitive_safety_legal"],
            "role": "positive_seed",
            "expectation": "counsel_first_sequence_must_survive",
            "anchor": (
                root
                / "research/pre-step6-rendered-hybrid-answer-cores/"
                "mid-level-consultant-report-2.native.rendered-hybrid-answer-core.v1.json"
            ),
            "deck": (
                root
                / "research/pre-step6-card-deck-replays/"
                "mid-level-consultant-report-2.card-deck-replay.v1.json"
            ),
            "problem": root / "research/pre-step6-problem-states/mid-level-consultant-report-2.problem-state.v1.json",
        },
        "mother-address-year": {
            "tags": ["sensitive_safety_legal", "negative_control"],
            "role": "standdown_seed",
            "expectation": "anchor_sufficient_deck_may_remain_private",
            "anchor": (
                root
                / "research/pre-step6-rendered-hybrid-answer-cores/"
                "mother-address-year.native.rendered-hybrid-answer-core.v1.json"
            ),
            "deck": (
                root
                / "research/pre-step6-card-deck-replays/"
                "mother-address-year.card-deck-replay.v1.json"
            ),
            "problem": root / "research/pre-step6-problem-states/mother-address-year.problem-state.v1.json",
        },
    }
    cases = {}
    for case_id, spec in specs.items():
        cases[case_id] = _case(
            case_id=case_id,
            base_case_id=case_id,
            tags=spec["tags"],
            role=spec["role"],
            brief=_problem_brief(Path(spec["problem"])),
            expectation=spec["expectation"],
            anchor=_json_answer(Path(spec["anchor"]), "answer_core"),
            deck=_json_answer(Path(spec["deck"]), "step6_output.answer_core"),
        )
    return cases


def _bridge_cases() -> dict[str, dict[str, object]]:
    contract = build_bridge_probe_contract()
    cases = {}
    tags_by_id = {
        "bridge-high-clutter-sensitive-overlay": ["high_clutter", "sensitive_safety_legal"],
        "bridge-sensitive-anchor-misses-tripwire": ["sensitive_safety_legal"],
        "bridge-sequencing-sensitive-boundary": ["sequencing_or_problem_shape", "sensitive_safety_legal"],
    }
    for item in contract["probe_cases"]:
        assert isinstance(item, dict)
        candidates = item["answer_candidates"]
        assert isinstance(candidates, dict)
        case_id = _string(item["case_id"])
        cases[case_id] = _case(
            case_id=case_id,
            base_case_id=case_id,
            tags=tags_by_id[case_id],
            role="positive_bridge",
            brief=_string(item["case_brief"]),
            expectation="known_false_standdown_bridge_should_survive_answer_delta",
            anchor=_string(candidates["anchor_visible"]),
            deck=_string(candidates["deck_visible"]),
        )
    return cases


def _false_positive_cases() -> dict[str, dict[str, object]]:
    contract = build_false_positive_probe_contract()
    tags_by_id = {
        "fp-bevelin-irrelevant-incentives": ["negative_control"],
        "fp-polya-true-but-useless": ["sequencing_or_problem_shape", "negative_control"],
        "fp-marker-preserved-entity-lost": ["sensitive_safety_legal", "negative_control"],
    }
    cases = {}
    for item in contract["probe_cases"]:
        assert isinstance(item, dict)
        candidates = item["answer_candidates"]
        assert isinstance(candidates, dict)
        case_id = _string(item["case_id"])
        cases[case_id] = _case(
            case_id=case_id,
            base_case_id=case_id,
            tags=tags_by_id[case_id],
            role="negative_control_seed",
            brief=_string(item["case_brief"]),
            expectation="deck_pressure_should_stand_down_unless_concrete_delta_exists",
            anchor=_string(candidates["anchor_visible"]),
            deck=_string(candidates["deck_pressure"]),
        )
    return cases


def _marker_cases() -> dict[str, dict[str, object]]:
    contract = build_marker_entity_followup_contract()
    tags_by_id = {
        "marker-entity-attempt-1-resource-generalization": ["negative_control"],
        "marker-entity-attempt-2-tripwire-compression": [
            "sensitive_safety_legal",
            "negative_control",
        ],
        "marker-entity-attempt-3-actor-sequence-blur": [
            "sequencing_or_problem_shape",
            "negative_control",
        ],
    }
    cases = {}
    for item in contract["attempt_cases"]:
        assert isinstance(item, dict)
        candidates = item["answer_candidates"]
        assert isinstance(candidates, dict)
        case_id = _string(item["attempt_id"])
        cases[case_id] = _case(
            case_id=case_id,
            base_case_id=case_id,
            tags=tags_by_id[case_id],
            role="negative_control_seed",
            brief=_string(item["case_brief"]),
            expectation="generic_marker_preserving_pressure_should_not_overpromote",
            anchor=_string(candidates["anchor_visible"]),
            deck=_string(candidates["deck_pressure"]),
        )
    return cases


def _scratch_cases(root: Path) -> dict[str, dict[str, object]]:
    scratch_root = root / "research/test-cases/phase2c-lane1-equivalence-2026-04-24/_scratch"
    specs = {
        "startup-pivot-new-run2": {
            "file": "startup_pivot_new_run2.json",
            "tags": ["high_clutter"],
            "role": "prior_run_calibration_seed",
            "expectation": "prior_revised_answer_may_add_concrete_test_design",
            "deck_pressure": (
                "Before pivoting, convert the three customer signals into a "
                "pre-buy test with a named price, three-month prepay, and a "
                "written pass/fail bar. Keep fairness to the passive co-founder "
                "separate from decision rights: tell her the plan, but do not "
                "treat courtesy as veto power. Check competitive dynamics and "
                "migration cost before declaring the new workflow the company."
            ),
        },
        "multi-offer-new-run2": {
            "file": "multi_offer_new_run2.json",
            "tags": ["high_clutter", "sequencing_or_problem_shape"],
            "role": "prior_run_calibration_seed",
            "expectation": "prior_revised_answer_may_add_sequence_and_family_constraints",
            "deck_pressure": (
                "Sequence the decision instead of choosing from the three labels. "
                "Ask all three companies for a deadline extension, run the wife "
                "conversation before committing to startup risk, negotiate a "
                "six-month ramp and remote/hybrid terms for the Series B option, "
                "and treat staying as an active plateau choice rather than a safe "
                "default."
            ),
        },
    }
    cases = {}
    for case_id, spec in specs.items():
        payload = _read_json(scratch_root / _string(spec["file"]))
        cases[case_id] = _case(
            case_id=case_id,
            base_case_id=case_id,
            tags=spec["tags"],
            role=spec["role"],
            brief=_string(payload.get("query")),
            expectation=_string(spec["expectation"]),
            anchor=_compact_answer(_string(payload.get("vanilla_answer"))),
            deck=_string(spec["deck_pressure"]),
        )
    return cases


def _case(
    *,
    case_id: str,
    base_case_id: str,
    tags: list[str],
    role: str,
    brief: str,
    expectation: str,
    anchor: str,
    deck: str,
) -> dict[str, object]:
    return {
        "case_id": case_id,
        "base_case_id": base_case_id,
        "case_type_tags": tags,
        "calibration_role": role,
        "selection_timing": "pre_run",
        "case_brief": brief,
        "pre_registered_expectation": expectation,
        "v60_toggle_pair_id": "",
        "v60_mode": "not_applicable",
        "v60_evidence_source": "not_applicable",
        "v60_private_context": "",
        "answer_candidates": {
            "anchor_visible": anchor,
            "deck_pressure": deck,
        },
    }


def _v60_variant(case: dict[str, object], *, mode: str) -> dict[str, object]:
    pair_id = f"{_string(case['base_case_id'])}.v60-pair"
    variant = dict(case)
    variant["case_id"] = f"{_string(case['base_case_id'])}.v60-{mode}"
    variant["v60_toggle_pair_id"] = pair_id
    variant["v60_mode"] = mode
    if mode == "on":
        variant["v60_evidence_source"] = "synthetic_pre_step6_private_consideration_ledger_fixture"
        variant["v60_private_context"] = _synthetic_v60_context(_string(case["base_case_id"]))
    else:
        variant["v60_evidence_source"] = "same_case_v60_withheld"
        variant["v60_private_context"] = ""
    return variant


def _synthetic_v60_context(base_case_id: str) -> str:
    if base_case_id.startswith("founder-grant-marcus"):
        return (
            "v60_chunk:overcommitment_without_evidence - Watch for informal "
            "promises becoming public commitments before written evidence and "
            "board process exist."
        )
    return (
        "v60_chunk:absence_blocker_false_precision - Watch for a plan that sounds "
        "decisive while missing feasibility checks, funding/data access, or a "
        "fallback window."
    )


def _sample_payload(
    *,
    case: dict[str, object],
    sample_index: int,
    provider_metadata: dict[str, object],
    step6_output: dict[str, object],
    notes: str,
) -> dict[str, object]:
    signal = derive_ledger_signal(step6_output)
    specificity = derive_answer_delta_specificity(step6_output)
    payload = {
        "schema_version": SAMPLE_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "case_id": case["case_id"],
        "base_case_id": case["base_case_id"],
        "sample_index": sample_index,
        "provider_metadata": provider_metadata,
        "input_packet": _input_packet(case),
        "step6_output": step6_output,
        "ledger_signal": signal,
        "answer_delta_specificity": specificity,
        "deterministic_role": list(DETERMINISTIC_ROLE),
        "gates": _blocked_gates(),
        "notes": notes,
    }
    validate_step6_calibration_sample(payload)
    return payload


def _input_packet(case: dict[str, object]) -> dict[str, object]:
    candidates = _answer_candidates(case, _string(case.get("case_id")))
    return {
        "case_brief": case["case_brief"],
        "case_type_tags": case["case_type_tags"],
        "pre_registered_expectation": case["pre_registered_expectation"],
        "v60_mode": case["v60_mode"],
        "v60_private_context": case["v60_private_context"],
        "anchor_visible_candidate": candidates["anchor_visible"],
        "deck_pressure_candidate": candidates["deck_pressure"],
    }


def _static_step6_output(
    *,
    candidates: dict[str, object],
    ledger_signal: str,
    answer_delta_specificity: str,
) -> dict[str, object]:
    deck_role = (
        "additive_pressure"
        if ledger_signal == "additive_pressure_present"
        else "confirming_support"
    )
    deck_disposition = "combined" if ledger_signal == "additive_pressure_present" else "deferred"
    delta = _answer_delta_for_specificity(answer_delta_specificity)
    return {
        "answer_core": (
            _string(candidates["deck_pressure"])
            if ledger_signal == "additive_pressure_present"
            else _string(candidates["anchor_visible"])
        ),
        "private_visibility_ledger": [
            {
                "source_id": "anchor_visible_candidate",
                "disposition": "used",
                "novelty_role": "visible_backbone",
                "why": "Anchor supplied the baseline.",
                "visible_effect": "Kept the baseline answer available.",
                "answer_delta": _empty_answer_delta(),
            },
            {
                "source_id": "deck_pressure_candidate",
                "disposition": deck_disposition,
                "novelty_role": deck_role,
                "why": "Static calibration sample.",
                "visible_effect": "Static visible effect." if deck_role == "additive_pressure" else "none",
                "answer_delta": delta if deck_role == "additive_pressure" else _empty_answer_delta(),
            },
        ],
    }


def _normalize_step6_output(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    ledger = value.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        ledger = []
    by_source = {
        _string(item.get("source_id")): item
        for item in ledger
        if isinstance(item, dict)
    }
    normalized = []
    for source_id in SOURCE_IDS:
        item = by_source.get(source_id, {})
        normalized.append(
            {
                "source_id": source_id,
                "disposition": _string(item.get("disposition")) or "deferred",
                "novelty_role": _string(item.get("novelty_role"))
                or (
                    "visible_backbone"
                    if source_id == "anchor_visible_candidate"
                    else "confirming_support"
                ),
                "why": _string(item.get("why")) or "Model did not explain this source.",
                "visible_effect": _string(item.get("visible_effect")) or "none",
                "answer_delta": _normalize_answer_delta(item.get("answer_delta")),
            }
        )
    return {
        "answer_core": _string(value.get("answer_core")),
        "private_visibility_ledger": normalized,
    }


def _bridge_shaped_step6_output(step6_output: object) -> dict[str, object]:
    if not isinstance(step6_output, dict):
        return {}
    return {
        "answer_core": step6_output.get("answer_core"),
        "private_bridge_consideration_ledger": step6_output.get("private_visibility_ledger"),
    }


def _answer_delta_for_specificity(specificity: str) -> dict[str, list[str]]:
    if specificity == "concrete_delta_present":
        return {
            "added_entities": ["static concrete payload"],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": [],
            "reframed_emphasis": [],
        }
    if specificity == "structural_delta_present":
        return {
            "added_entities": [],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": [
                "added stop condition: continue only if the static fixture passes"
            ],
            "reframed_emphasis": [],
        }
    if specificity == "reframe_only":
        return {
            "added_entities": [],
            "removed_entities": [],
            "reordered_sequences": [],
            "structural_delta": [],
            "reframed_emphasis": ["static reframe"],
        }
    return _empty_answer_delta()


def _bucket_status(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for bucket, required in REQUIRED_BUCKETS.items():
        observed = _observed_count(cases, bucket)
        rows.append(
            {
                "bucket": bucket,
                "required": required,
                "observed": observed,
                "met": observed >= required,
            }
        )
    return rows


def _observed_count(cases: list[dict[str, object]], bucket: str) -> int:
    if bucket == PAIR_BUCKET:
        pairs: dict[str, set[str]] = {}
        for case in cases:
            pair_id = _string(case.get("v60_toggle_pair_id"))
            mode = _string(case.get("v60_mode"))
            if pair_id:
                pairs.setdefault(pair_id, set()).add(mode)
        return sum(1 for modes in pairs.values() if {"on", "off"} <= modes)
    return sum(
        1
        for case in cases
        if isinstance(case.get("case_type_tags"), list)
        and bucket in case["case_type_tags"]
    )


def _floor_status(cases: list[dict[str, object]]) -> str:
    if 12 <= len(cases) <= 20 and all(row["met"] is True for row in _bucket_status(cases)):
        return "corpus_floor_met"
    return "corpus_floor_unmet"


def _stability_label(
    signal_counts: dict[str, int],
    specificity_counts: dict[str, int],
    sample_count: int,
) -> str:
    if sample_count == 0:
        return "not_sampled"
    if sample_count < DEFAULT_SAMPLES_PER_CASE:
        return "incomplete_sampling"
    if max(signal_counts.values(), default=0) == sample_count and max(
        specificity_counts.values(),
        default=0,
    ) == sample_count:
        return "stable"
    return "unstable"


def _calibration_read(case_results: list[dict[str, object]], contract: dict[str, object]) -> str:
    expected_cases = int(contract.get("case_count") or 0)
    if len(case_results) < expected_cases:
        return "sampling_incomplete"
    if any(result.get("stability_label") == "incomplete_sampling" for result in case_results):
        return "sampling_incomplete"
    if any(result.get("stability_label") == "unstable" for result in case_results):
        return "stability_review_required_before_reviewer_phase"
    return "step6_stability_phase_passed_reviewer_phase_next"


def _stability_classification(case_result: dict[str, object]) -> str:
    sample_count = int(case_result.get("sample_count") or 0)
    if sample_count < DEFAULT_SAMPLES_PER_CASE:
        return "incomplete_sampling"
    signal_counts = case_result.get("ledger_signal_counts")
    specificity_counts = case_result.get("answer_delta_specificity_counts")
    if not isinstance(signal_counts, dict) or not isinstance(specificity_counts, dict):
        return "unstable_mixed"
    unlock_count = int(case_result.get("unlock_count") or 0)
    reframe_only_count = int(case_result.get("reframe_only_count") or 0)
    additive_count = int(signal_counts.get("additive_pressure_present") or 0)
    private_count = int(signal_counts.get("all_private_or_confirming") or 0)
    concrete_count = int(specificity_counts.get("concrete_delta_present") or 0)
    structural_count = int(specificity_counts.get("structural_delta_present") or 0)
    not_applicable_count = int(specificity_counts.get("not_applicable") or 0)
    if sample_count > 0 and unlock_count == sample_count:
        return "stable_positive"
    if sample_count > 0 and private_count == sample_count and not_applicable_count == sample_count:
        return "stable_standdown"
    if sample_count >= 3 and unlock_count == sample_count - 1:
        return "borderline_unlock"
    if (
        additive_count > 0
        and concrete_count == 0
        and structural_count == 0
        and reframe_only_count > 0
    ):
        return "abstract_additive_only"
    return "unstable_mixed"


def _reviewer_phase_eligibility(classification: str) -> str:
    if classification == "stable_positive":
        return "eligible_stable_positive_candidate"
    if classification == "stable_standdown":
        return "eligible_stable_standdown_candidate"
    if classification == "borderline_unlock":
        return "blocked_borderline_repeat_sampling"
    if classification == "abstract_additive_only":
        return "blocked_abstract_additive"
    if classification == "incomplete_sampling":
        return "blocked_incomplete_sampling"
    return "blocked_unstable_mixed"


def _stability_rationale(case_result: dict[str, object], classification: str) -> str:
    sample_count = int(case_result.get("sample_count") or 0)
    unlock_count = int(case_result.get("unlock_count") or 0)
    reframe_count = int(case_result.get("reframe_only_count") or 0)
    signal_counts = case_result.get("ledger_signal_counts")
    specificity_counts = case_result.get("answer_delta_specificity_counts")
    if classification == "stable_positive":
        return (
            "All samples produced additive pressure with concrete or specific "
            "structural answer deltas."
        )
    if classification == "stable_standdown":
        return "All samples kept deck pressure private or confirming."
    if classification == "borderline_unlock":
        return f"{unlock_count}/{sample_count} samples unlocked; repeat before review."
    if classification == "abstract_additive_only":
        return (
            f"Additive pressure appeared with {reframe_count} reframe-only sample(s) "
            "and no concrete unlock."
        )
    if classification == "incomplete_sampling":
        return (
            f"Only {sample_count}/{DEFAULT_SAMPLES_PER_CASE} planned sample(s) landed; "
            "repeat missing samples before review."
        )
    return (
        "Ledger signal and answer-delta specificity varied: "
        f"signals={signal_counts}, specificity={specificity_counts}."
    )


def _sample_has_structural_delta_field(sample: dict[str, object]) -> bool:
    step6_output = sample.get("step6_output")
    if not isinstance(step6_output, dict):
        return False
    ledger = step6_output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return False
    for item in ledger:
        if not isinstance(item, dict):
            continue
        if item.get("source_id") != "deck_pressure_candidate":
            continue
        delta = item.get("answer_delta")
        if not isinstance(delta, dict):
            continue
        structural_delta = delta.get("structural_delta")
        if isinstance(structural_delta, list) and any(
            isinstance(entry, str) and entry.strip() for entry in structural_delta
        ):
            return True
    return False


def _stability_review_aggregate(case_reviews: list[dict[str, object]]) -> dict[str, object]:
    counts = {
        classification: sum(
            1
            for review in case_reviews
            if review.get("stability_classification") == classification
        )
        for classification in sorted(STABILITY_CLASSIFICATIONS)
    }
    repeat_ids = [
        _string(review.get("case_id"))
        for review in case_reviews
        if review.get("stability_classification")
        in {
            "borderline_unlock",
            "abstract_additive_only",
            "unstable_mixed",
            "incomplete_sampling",
        }
    ]
    if repeat_ids:
        decision = "blocked_for_full_calibration_repeat_or_partition_first"
        next_action = "repeat_sample_unstable_cases_same_prompt_before_reviewer_phase"
    else:
        decision = "stable_cases_ready_for_reviewer_phase"
        next_action = "run_reviewer_phase_from_saved_samples"
    return {
        "case_count": len(case_reviews),
        "stable_positive_count": counts.get("stable_positive", 0),
        "stable_standdown_count": counts.get("stable_standdown", 0),
        "borderline_unlock_count": counts.get("borderline_unlock", 0),
        "abstract_additive_only_count": counts.get("abstract_additive_only", 0),
        "unstable_mixed_count": counts.get("unstable_mixed", 0),
        "incomplete_sampling_count": counts.get("incomplete_sampling", 0),
        "repeat_sample_case_ids": repeat_ids,
        "reviewer_phase_decision": decision,
        "recommended_next_action": next_action,
    }


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def _validate_sample_plan(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, SAMPLE_PLAN_FIELDS, path)
    yield from _missing_fields(value, SAMPLE_PLAN_FIELDS, path)
    if value.get("samples_per_case") != DEFAULT_SAMPLES_PER_CASE:
        yield f"{path / 'samples_per_case'}: must be {DEFAULT_SAMPLES_PER_CASE}"
    if not _string(value.get("reviewer_phase")).strip():
        yield f"{path / 'reviewer_phase'}: must be non-empty"
    if not isinstance(value.get("tracked_metrics"), list) or not value["tracked_metrics"]:
        yield f"{path / 'tracked_metrics'}: must be non-empty list"


def _validate_case(value: object, path: Path, *, root: Path | None) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CASE_FIELDS, path)
    yield from _missing_fields(value, CASE_FIELDS, path)
    if not _string(value.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    tags = value.get("case_type_tags")
    if not isinstance(tags, list) or not tags:
        yield f"{path / 'case_type_tags'}: must be non-empty list"
    elif any(tag not in CASE_BUCKETS for tag in tags):
        yield f"{path / 'case_type_tags'}: unsupported tag"
    if value.get("selection_timing") != "pre_run":
        yield f"{path / 'selection_timing'}: must be pre_run"
    if _string(value.get("v60_mode")) not in ALLOWED_V60_MODES:
        yield f"{path / 'v60_mode'}: invalid v60 mode"
    yield from _validate_answer_candidates(value.get("answer_candidates"), path / "answer_candidates")


def _validate_answer_candidates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: must be an object"
        return
    yield from _unknown_fields(value, CANDIDATE_FIELDS, path)
    yield from _missing_fields(value, CANDIDATE_FIELDS, path)
    for field in CANDIDATE_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_provider_metadata(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: provider_metadata must be an object"
        return
    if "provider" not in value and "provider_name" not in value:
        yield f"{path}: provider or provider_name is required"
    if not _string(value.get("model")).strip():
        yield f"{path / 'model'}: must be non-empty"
    if not _string(value.get("status")).strip():
        yield f"{path / 'status'}: must be non-empty"
    yield from _unknown_fields(value, PROVIDER_METADATA_FIELDS, path)


def _validate_input_packet(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: input_packet must be an object"
        return
    yield from _unknown_fields(value, INPUT_PACKET_FIELDS, path)
    yield from _missing_fields(value, INPUT_PACKET_FIELDS, path)
    for field in ("case_brief", "anchor_visible_candidate", "deck_pressure_candidate"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"


def _validate_step6_output(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: step6_output must be an object"
        return
    yield from _unknown_fields(value, STEP6_OUTPUT_FIELDS, path)
    yield from _missing_fields(value, STEP6_OUTPUT_FIELDS, path)
    answer_core = _string(value.get("answer_core"))
    if not answer_core.strip():
        yield f"{path / 'answer_core'}: must be non-empty"
    else:
        try:
            validate_public_answer_hygiene(answer_core)
        except ValueError as exc:
            yield f"{path / 'answer_core'}: {exc}"
    ledger = value.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        yield f"{path / 'private_visibility_ledger'}: must be a list"
        return
    ids = [_string(item.get("source_id")) if isinstance(item, dict) else "" for item in ledger]
    if tuple(ids[:2]) != SOURCE_IDS:
        yield f"{path / 'private_visibility_ledger'}: must start with anchor/deck custody"
    for index, item in enumerate(ledger):
        if not isinstance(item, dict):
            yield f"{path / 'private_visibility_ledger' / str(index)}: must be object"
            continue
        item_path = path / "private_visibility_ledger" / str(index)
        yield from _unknown_fields(item, LEDGER_FIELDS, item_path)
        yield from _missing_fields(item, LEDGER_FIELDS, item_path)
        if "answer_delta" in item:
            yield from _validate_answer_delta(item["answer_delta"], item_path / "answer_delta")


def _validate_answer_delta(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: answer_delta must be an object"
        return
    yield from _unknown_fields(value, ANSWER_DELTA_FIELDS, path)
    yield from _missing_fields(
        value,
        ANSWER_DELTA_FIELDS - LEGACY_OPTIONAL_ANSWER_DELTA_FIELDS,
        path,
    )
    for field in ANSWER_DELTA_FIELDS:
        if field not in value:
            continue
        if not isinstance(value[field], list):
            yield f"{path / field}: must be list"


def _validate_case_result(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case result must be an object"
        return
    yield from _unknown_fields(value, CASE_RESULT_FIELDS, path)
    yield from _missing_fields(value, CASE_RESULT_FIELDS, path)
    if not _string(value.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if not isinstance(value.get("sample_count"), int):
        yield f"{path / 'sample_count'}: must be integer"
    if value.get("stability_label") not in {
        "stable",
        "unstable",
        "not_sampled",
        "incomplete_sampling",
    }:
        yield f"{path / 'stability_label'}: invalid stability label"


def _validate_stability_case_review(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case stability review must be an object"
        return
    yield from _unknown_fields(value, STABILITY_CASE_REVIEW_FIELDS, path)
    yield from _missing_fields(value, STABILITY_CASE_REVIEW_FIELDS, path)
    if not _string(value.get("case_id")).strip():
        yield f"{path / 'case_id'}: must be non-empty"
    if not isinstance(value.get("sample_count"), int) or value.get("sample_count") < 0:
        yield f"{path / 'sample_count'}: must be non-negative integer"
    if value.get("stability_classification") not in STABILITY_CLASSIFICATIONS:
        yield f"{path / 'stability_classification'}: invalid classification"
    if not _string(value.get("reviewer_phase_eligibility")).strip():
        yield f"{path / 'reviewer_phase_eligibility'}: must be non-empty"
    if not isinstance(value.get("ledger_signal_counts"), dict):
        yield f"{path / 'ledger_signal_counts'}: must be object"
    if not isinstance(value.get("answer_delta_specificity_counts"), dict):
        yield f"{path / 'answer_delta_specificity_counts'}: must be object"
    if not isinstance(value.get("unlock_count"), int):
        yield f"{path / 'unlock_count'}: must be integer"
    if not isinstance(value.get("reframe_only_count"), int):
        yield f"{path / 'reframe_only_count'}: must be integer"
    if not isinstance(value.get("structural_delta_count"), int):
        yield f"{path / 'structural_delta_count'}: must be integer"
    if not isinstance(value.get("structural_delta_field_count"), int):
        yield f"{path / 'structural_delta_field_count'}: must be integer"
    refs = value.get("sample_refs")
    if not isinstance(refs, list):
        yield f"{path / 'sample_refs'}: must be list"
    elif any(not _string(ref).strip() for ref in refs):
        yield f"{path / 'sample_refs'}: refs must be non-empty strings"
    if not _string(value.get("rationale")).strip():
        yield f"{path / 'rationale'}: must be non-empty"


def _validate_stability_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be an object"
        return
    yield from _unknown_fields(value, STABILITY_AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, STABILITY_AGGREGATE_FIELDS, path)
    int_fields = (
        "case_count",
        "stable_positive_count",
        "stable_standdown_count",
        "borderline_unlock_count",
        "abstract_additive_only_count",
        "unstable_mixed_count",
        "incomplete_sampling_count",
    )
    for field in int_fields:
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    repeat_ids = value.get("repeat_sample_case_ids")
    if not isinstance(repeat_ids, list):
        yield f"{path / 'repeat_sample_case_ids'}: must be list"
    elif any(not _string(case_id).strip() for case_id in repeat_ids):
        yield f"{path / 'repeat_sample_case_ids'}: ids must be non-empty"
    if value.get("reviewer_phase_decision") not in {
        "blocked_for_full_calibration_repeat_or_partition_first",
        "stable_cases_ready_for_reviewer_phase",
    }:
        yield f"{path / 'reviewer_phase_decision'}: invalid reviewer phase decision"
    if value.get("recommended_next_action") not in {
        "repeat_sample_unstable_cases_same_prompt_before_reviewer_phase",
        "run_reviewer_phase_from_saved_samples",
    }:
        yield f"{path / 'recommended_next_action'}: invalid next action"


def _validate_gates(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: gates must be an object"
        return
    yield from _unknown_fields(value, GATE_FIELDS, path)
    yield from _missing_fields(value, GATE_FIELDS, path)
    if value.get("runtime_wiring_allowed") is not False:
        yield f"{path / 'runtime_wiring_allowed'}: must be false"
    if value.get("skill_update_allowed") is not False:
        yield f"{path / 'skill_update_allowed'}: must be false"


def _blocked_gates() -> dict[str, bool]:
    return {"runtime_wiring_allowed": False, "skill_update_allowed": False}


def _case_by_id(contract: dict[str, object], case_id: str) -> dict[str, object]:
    cases = contract.get("cases")
    if not isinstance(cases, list):
        raise CalibrationCorpusError("cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("case_id") == case_id:
            return case
    raise CalibrationCorpusError(f"unknown calibration case: {case_id}")


def _answer_candidates(case: dict[str, object], case_id: str) -> dict[str, object]:
    candidates = case.get("answer_candidates")
    if not isinstance(candidates, dict):
        raise CalibrationCorpusError(f"{case_id}: answer_candidates missing")
    for field in CANDIDATE_FIELDS:
        if not _string(candidates.get(field)).strip():
            raise CalibrationCorpusError(f"{case_id}: {field} missing")
    return candidates


def _json_answer(path: Path, dotted_key: str) -> str:
    payload = _read_json(path)
    value: object = payload
    for part in dotted_key.split("."):
        if not isinstance(value, dict):
            return ""
        value = value.get(part)
    return _string(value)


def _problem_brief(path: Path) -> str:
    payload = _read_json(path)
    return " ".join(
        part
        for part in [
            _string(payload.get("user_goal")),
            _string(payload.get("problem_type")),
        ]
        if part.strip()
    )


def _compact_answer(value: str) -> str:
    if "FULL ASSISTANT REASONING:" in value:
        value = value.split("FULL ASSISTANT REASONING:", 1)[0]
    value = value.strip()
    return value[:2200].strip()


def _normalize_answer_delta(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        value = {}
    return {
        field: [
            item.strip()
            for item in value.get(field, [])
            if isinstance(item, str) and item.strip()
        ]
        for field in sorted(ANSWER_DELTA_FIELDS)
    }


def _empty_answer_delta() -> dict[str, list[str]]:
    return {field: [] for field in sorted(ANSWER_DELTA_FIELDS)}


def _provider_metadata_dict(metadata: object) -> dict[str, object]:
    if dataclasses.is_dataclass(metadata):
        result = dataclasses.asdict(metadata)
    elif isinstance(metadata, dict):
        result = dict(metadata)
    else:
        result = {}
    if "provider_name" in result and "provider" not in result:
        result["provider"] = result["provider_name"]
    if "model_family" not in result:
        result["model_family"] = _model_family(_string(result.get("model")))
    return result


def _live_sample_outer_timeout_seconds() -> float:
    raw = os.getenv("LOLLA_CALIBRATION_SAMPLE_TIMEOUT")
    if raw is None:
        raw = os.getenv("LOLLA_LLM_TIMEOUT", "60")
        try:
            provider_timeout = float(raw)
        except ValueError:
            provider_timeout = 60.0
        return max(10.0, min(provider_timeout + 25.0, 180.0))
    try:
        value = float(raw)
    except ValueError:
        value = 85.0
    return max(10.0, min(value, 300.0))


def _raise_live_sample_timeout(_signum: int, _frame: object) -> None:
    raise CalibrationCorpusError(
        "live calibration Step 6 sample exceeded outer timeout"
    )


def _model_family(model: str) -> str:
    if "/" in model:
        return model.split("/", 1)[0]
    if "-" in model:
        return model.split("-", 1)[0]
    return model or "unknown"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        raise CalibrationCorpusError(f"env file missing: {path}")
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


def _parse_case_ids(args: argparse.Namespace, contract: dict[str, object]) -> list[str]:
    if args.all:
        cases = contract.get("cases")
        if not isinstance(cases, list):
            raise CalibrationCorpusError("cases missing")
        return [_string(case.get("case_id")) for case in cases if isinstance(case, dict)]
    if args.case_id:
        return args.case_id
    raise CalibrationCorpusError("provide --case-id or --all for live sampling")


def _load_contract_arg(args: argparse.Namespace) -> dict[str, object]:
    if args.contract is not None:
        return load_calibration_corpus_contract(args.contract)
    return build_calibration_corpus_contract(root=Path.cwd())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--result", type=Path)
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--write-stability-review", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--samples-per-case", type=int, default=DEFAULT_SAMPLES_PER_CASE)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", default="")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--max-attempts", type=int, default=1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise CalibrationCorpusError(f"{path}: payload must be an object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_calibration_corpus_contract(payload, root=Path.cwd(), path=path)
            elif schema == SAMPLE_SCHEMA_VERSION:
                validate_step6_calibration_sample(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_step6_calibration_result(payload, path=path)
            elif schema == STABILITY_REVIEW_SCHEMA_VERSION:
                validate_step6_calibration_stability_review(payload, path=path)
            else:
                raise CalibrationCorpusError(f"{path}: unknown schema_version")
        return 0

    contract = _load_contract_arg(args)
    if args.write_contract:
        print(write_calibration_corpus_contract(payload=contract, out_dir=args.out_dir))
        return 0

    if args.write_stability_review:
        result_path = args.result or args.out_dir / "calibration-step6-result.v1.json"
        result = load_step6_calibration_result(result_path)
        sample_paths = sorted(args.sample_dir.glob("*.json"))
        samples = [load_step6_calibration_sample(path) for path in sample_paths]
        review = build_step6_calibration_stability_review(
            contract=contract,
            result=result,
            samples=samples,
            source_result_ref=str(result_path),
        )
        print(write_step6_calibration_stability_review(payload=review, out_dir=args.out_dir))
        return 0

    if args.live:
        case_ids = _parse_case_ids(args, contract)
        output_paths: list[Path] = []
        errors: list[str] = []
        for case_id in case_ids:
            for sample_index in range(args.samples_per_case):
                expected_path = calibration_sample_path(
                    out_dir=args.sample_dir,
                    case_id=case_id,
                    sample_index=sample_index,
                )
                if args.skip_existing and expected_path.exists():
                    output_paths.append(expected_path)
                    print(expected_path)
                    continue
                attempt_count = max(1, int(args.max_attempts or 1))
                for attempt_index in range(attempt_count):
                    try:
                        output = run_live_step6_sample(
                            contract=contract,
                            case_id=case_id,
                            sample_index=sample_index,
                            provider=args.provider,
                            model=args.model,
                            env_file=args.env_file,
                            out_dir=args.sample_dir,
                            dry_run=args.dry_run,
                        )
                    except CalibrationCorpusError as exc:
                        message = (
                            f"{case_id} sample-{sample_index} attempt "
                            f"{attempt_index + 1}/{attempt_count}: {exc}"
                        )
                        if attempt_index + 1 < attempt_count:
                            print(message, file=sys.stderr)
                            continue
                        if args.continue_on_error:
                            errors.append(message)
                            print(message, file=sys.stderr)
                            break
                        raise
                    if output is not None:
                        output_paths.append(output)
                        print(output)
                    break
        aggregate_paths = (
            sorted(args.sample_dir.glob("*.json"))
            if args.skip_existing or args.continue_on_error
            else output_paths
        )
        if aggregate_paths:
            samples = [load_step6_calibration_sample(path) for path in aggregate_paths]
            result = build_step6_calibration_result(contract=contract, samples=samples)
            print(write_step6_calibration_result(payload=result, out_dir=args.out_dir))
        if errors:
            error_path = args.out_dir / "calibration-live-errors.txt"
            args.out_dir.mkdir(parents=True, exist_ok=True)
            error_path.write_text("\n".join(errors) + "\n", encoding="utf-8")
            print(error_path)
        else:
            error_path = args.out_dir / "calibration-live-errors.txt"
            if error_path.exists():
                error_path.unlink()
        return 0

    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
