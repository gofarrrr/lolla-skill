#!/usr/bin/env python3
"""Research-only reviewer phase for GPT-stable variable-case outputs.

This answers a narrow question from the calibration aftermath: when GPT appears
more stable than Kimi on formerly variable cases, is that stability aligned
with reviewer cognition, or just confident wrongness? It also checks whether
pure structural_delta unlocks are useful or a loophole.
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


CONTRACT_SCHEMA_VERSION = "pre_step6_gpt_stability_correctness_contract.v1"
JUDGMENT_SCHEMA_VERSION = "pre_step6_gpt_stability_correctness_judgment.v1"
RESULT_SCHEMA_VERSION = "pre_step6_gpt_stability_correctness_result.v1"
RUNTIME_POLICY = "runtime_dormant"
STATUS = "research_only"
EXPERIMENT_ID = "pre_step6_gpt_stability_correctness_review_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-gpt-stability-correctness-review")
DEFAULT_JUDGMENT_DIR = DEFAULT_OUT_DIR / "judgments"
DEFAULT_SAMPLE_DIR = Path("research/pre-step6-variable-case-alt-model-gpt51/step6-samples")
DEFAULT_SEED = 2026052105
DEFAULT_REVIEWER_MODELS = (
    "openai/gpt-5.1-chat",
    "google/gemini-3.1-flash-lite",
)
UNLOCKING_SPECIFICITY = frozenset({"concrete_delta_present", "structural_delta_present"})
EXCLUDED_UNSTABLE_CASE_IDS = frozenset({"founder-grant-marcus-equity.high-clutter.v60-on"})
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "source_sample_dir_ref",
        "model_under_review",
        "reviewer_rule",
        "precommitted_response_shapes",
        "review_cases",
        "excluded_case_ids",
        "gates",
        "notes",
    }
)
REVIEWER_RULE_FIELDS = frozenset(
    {
        "reviewer_count",
        "model_family_policy",
        "prompt_policy",
        "blind_shuffle_policy",
        "reviewer_question_split",
    }
)
RESPONSE_SHAPE_FIELDS = frozenset(
    {
        "gpt_visible_rejected",
        "gpt_anchor_rejected",
        "structural_delta_only_rejected",
        "ambiguous_visibility",
        "gpt_stability_supported",
    }
)
CASE_FIELDS = frozenset(
    {
        "review_case_id",
        "source_case_id",
        "sample_ref",
        "sample_index",
        "model_under_review",
        "expected_visibility_decision",
        "case_brief",
        "anchor_visible",
        "step6_visible",
        "ledger_signal",
        "answer_delta_specificity",
        "answer_delta_summary",
        "pure_structural_delta_only",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
JUDGMENT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "review_case_id",
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
        "output_label",
        "winner_label",
        "visibility_judgment",
        "confidence",
        "rationale",
        "answer_correctness_notes",
        "visibility_decision_notes",
        "payload_loss_or_bloat",
        "structural_delta_read",
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
        "review_case_id",
        "source_case_id",
        "sample_index",
        "expected_visibility_decision",
        "pure_structural_delta_only",
        "reviewer_count",
        "reviewer_model_families",
        "output_labels",
        "reviewer_winner_arms",
        "visibility_judgments",
        "reviewer_label_consistency",
        "confirmed_visibility_label",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "case_count",
        "gpt_visible_case_count",
        "gpt_anchor_case_count",
        "gpt_visible_supported_count",
        "gpt_visible_rejected_count",
        "gpt_anchor_supported_count",
        "gpt_anchor_rejected_count",
        "ambiguous_count",
        "tension_count",
        "structural_delta_only_reviewed_count",
        "structural_delta_only_supported_count",
        "structural_delta_only_rejected_count",
        "reviewer_read",
        "recommended_next_action",
    }
)
ALLOWED_OUTPUT_LABELS = frozenset(
    {"better", "non_inferior", "worse_but_visible", "worse_unwise", "tie", "ambiguous"}
)
ALLOWED_VISIBILITY_JUDGMENTS = frozenset(
    {"correct_visible", "correct_anchor", "wrong_visible", "wrong_anchor", "ambiguous"}
)
ALLOWED_WINNER_ARMS = frozenset({"anchor_visible", "step6_visible", "tie"})
ALLOWED_CONFIRMED_LABELS = frozenset(
    {
        "gpt_visible_supported",
        "gpt_visible_rejected",
        "gpt_anchor_supported",
        "gpt_anchor_rejected",
        "ambiguous",
        "not_observed",
    }
)


class GPTStabilityCorrectnessError(ValueError):
    pass


def build_gpt_stability_correctness_contract(
    *,
    root: Path,
    sample_dir: Path = DEFAULT_SAMPLE_DIR,
) -> dict[str, object]:
    root = Path(root)
    sample_paths = sorted((root / sample_dir).glob("*.calibration-step6.v1.json"))
    samples = [load_step6_calibration_sample(path) for path in sample_paths]
    for sample in samples:
        validate_step6_calibration_sample(sample)
    model_under_review = _dominant_model(samples)
    review_cases = [
        _case_from_sample(root=root, sample_path=path, sample=sample)
        for path, sample in zip(sample_paths, samples, strict=True)
        if _include_sample(sample)
    ]
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "source_sample_dir_ref": str(sample_dir),
        "model_under_review": model_under_review,
        "reviewer_rule": {
            "reviewer_count": 2,
            "model_family_policy": (
                "two_families_required_with_model_under_review_overlap_recorded"
            ),
            "prompt_policy": "same_split_rubric_saved_gpt_samples_only",
            "blind_shuffle_policy": "fresh_blind_shuffle_per_reviewer",
            "reviewer_question_split": [
                "answer_correctness",
                "visibility_decision_correctness",
            ],
        },
        "precommitted_response_shapes": {
            "gpt_visible_rejected": (
                "Do not route to GPT for stability alone; inspect whether GPT is "
                "confidently over-promoting before any model commitment."
            ),
            "gpt_anchor_rejected": (
                "Do not treat GPT stand-down stability as correctness; inspect "
                "whether Kimi variance was surfacing real borderline value."
            ),
            "structural_delta_only_rejected": (
                "Design review of answer_delta specificity vocabulary and Step 6 "
                "prompt; do not add another field as a quick fix."
            ),
            "ambiguous_visibility": (
                "Keep as calibration evidence; do not promote or model-shop from "
                "split reviewer evidence."
            ),
            "gpt_stability_supported": (
                "Model-family stability becomes a candidate input to the design "
                "discussion, not a runtime selector by itself."
            ),
        },
        "review_cases": review_cases,
        "excluded_case_ids": sorted(EXCLUDED_UNSTABLE_CASE_IDS),
        "gates": _blocked_gates(),
        "notes": (
            "Reviews GPT-stable saved outputs with answer correctness and "
            "visibility correctness separated. This does not make GPT the runtime "
            "model and does not add a deterministic wisdom gate."
        ),
    }
    validate_gpt_stability_correctness_contract(payload)
    return payload


def write_gpt_stability_correctness_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_gpt_stability_correctness_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "gpt-stability-correctness-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_gpt_stability_correctness_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise GPTStabilityCorrectnessError(f"{path}: payload must be object")
    validate_gpt_stability_correctness_contract(payload, path=path)
    return payload


def build_reviewer_packet(
    *,
    contract: dict[str, object],
    review_case_id: str,
    seed: int = DEFAULT_SEED,
) -> dict[str, object]:
    validate_gpt_stability_correctness_contract(contract)
    case = _case_by_id(contract, review_case_id)
    arms = ["anchor_visible", "step6_visible"]
    rng = random.Random(seed + sum(ord(char) for char in review_case_id))
    rng.shuffle(arms)
    blind_map = dict(zip(("A", "B"), arms, strict=True))
    answer_by_arm = {
        "anchor_visible": _string(case["anchor_visible"]),
        "step6_visible": _string(case["step6_visible"]),
    }
    return {
        "experiment_id": EXPERIMENT_ID,
        "review_case_id": review_case_id,
        "source_case_id": case["source_case_id"],
        "sample_index": case["sample_index"],
        "model_under_review": case["model_under_review"],
        "expected_visibility_decision_private": case["expected_visibility_decision"],
        "case_brief": case["case_brief"],
        "ledger_signal": case["ledger_signal"],
        "answer_delta_specificity": case["answer_delta_specificity"],
        "answer_delta_summary": case["answer_delta_summary"],
        "pure_structural_delta_only": case["pure_structural_delta_only"],
        "reviewer_task": (
            "Compare two blinded public answers for the user's actual decision. "
            "This review tests model-family stability, not model-family authority. "
            "Answer two distinct questions: first, is the saved GPT Step 6 output "
            "good relative to the anchor; second, was GPT's visibility decision "
            "correct (show Step 6 output vs keep anchor visible)? Penalize bloat, "
            "payload loss, invented certainty, and generic cleverness."
        ),
        "candidates_by_label": {
            label: {"answer_core": answer_by_arm[arm], "char_count": len(answer_by_arm[arm])}
            for label, arm in blind_map.items()
        },
        "blind_map_private": blind_map,
        "response_schema": {
            "output_label": "better | non_inferior | worse_but_visible | worse_unwise | tie | ambiguous",
            "winner_label": "A | B | tie",
            "visibility_judgment": (
                "correct_visible | correct_anchor | wrong_visible | wrong_anchor | ambiguous"
            ),
            "confidence": "high | medium | low",
            "rationale": "Short rationale grounded in the answers.",
            "answer_correctness_notes": ["Specific notes on answer quality."],
            "visibility_decision_notes": ["Specific notes on visibility decision correctness."],
            "payload_loss_or_bloat": ["Payload loss or bloat, if any."],
            "structural_delta_read": (
                "useful_structural_delta | loophole_or_vague | not_applicable | ambiguous"
            ),
        },
    }


def build_static_gpt_stability_judgment(
    *,
    contract: dict[str, object],
    review_case_id: str,
    model: str,
    output_label: str,
    winner_arm: str,
    visibility_judgment: str,
) -> dict[str, object]:
    packet = build_reviewer_packet(contract=contract, review_case_id=review_case_id)
    blind_map = _string_dict(packet["blind_map_private"])
    winner_label = "tie"
    if winner_arm != "tie":
        winner_label = next(label for label, arm in blind_map.items() if arm == winner_arm)
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "review_case_id": review_case_id,
        "judgment_source": "static_gpt_stability_correctness_judgment",
        "provider_metadata": {
            "provider": "static",
            "model": model,
            "model_family": _model_family(model),
            "status": "ok",
        },
        "blind_map": blind_map,
        "reviewer_output": {
            "output_label": output_label,
            "winner_label": winner_label,
            "visibility_judgment": visibility_judgment,
            "confidence": "high",
            "rationale": "Static split-rubric judgment.",
            "answer_correctness_notes": ["static answer note"],
            "visibility_decision_notes": ["static visibility note"],
            "payload_loss_or_bloat": ["none"],
            "structural_delta_read": "not_applicable",
        },
        "gates": _blocked_gates(),
        "notes": "Static GPT-stability correctness fixture.",
    }
    validate_gpt_stability_correctness_judgment(payload)
    return payload


def run_live_reviewer(
    *,
    contract: dict[str, object],
    review_case_id: str,
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
    packet = build_reviewer_packet(contract=contract, review_case_id=review_case_id, seed=seed)
    private_blind_map = _string_dict(packet.pop("blind_map_private"))
    expected_visibility = _string(packet.pop("expected_visibility_decision_private"))
    if dry_run:
        print(json.dumps(packet, indent=2, ensure_ascii=False))
        return None
    repo_root = Path.cwd()
    sys.path.insert(0, str(repo_root / "engine"))
    sys.path.insert(0, str(repo_root))
    from system_b.boundary_provider import load_boundary_client_from_env  # noqa: PLC0415

    client = load_boundary_client_from_env(provider)
    output, metadata = client.run_json_with_metadata(
        _reviewer_system_prompt(expected_visibility=expected_visibility),
        json.dumps(packet, indent=2, ensure_ascii=False),
        stage="pre_step6_gpt_stability_correctness_review",
        tendency_id=review_case_id,
    )
    provider_metadata = _provider_metadata_dict(metadata)
    provider_metadata["model_family"] = _model_family(_string(provider_metadata.get("model")))
    if _string(provider_metadata.get("status")) != "ok":
        raise GPTStabilityCorrectnessError(
            "live GPT-stability reviewer failed with status "
            f"{_string(provider_metadata.get('status')) or 'unknown'}"
        )
    payload = {
        "schema_version": JUDGMENT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "review_case_id": review_case_id,
        "judgment_source": "manual_llm_reviewer_judgment",
        "provider_metadata": provider_metadata,
        "blind_map": private_blind_map,
        "reviewer_output": _normalize_reviewer_output(output, blind_map=private_blind_map),
        "gates": _blocked_gates(),
        "notes": "Live saved-sample GPT-stability correctness judgment.",
    }
    return write_gpt_stability_correctness_judgment(payload=payload, out_dir=out_dir)


def build_gpt_stability_correctness_result(
    *,
    contract: dict[str, object],
    judgments: Sequence[dict[str, object]],
) -> dict[str, object]:
    validate_gpt_stability_correctness_contract(contract)
    for judgment in judgments:
        validate_gpt_stability_correctness_judgment(judgment)
    by_case: dict[str, list[dict[str, object]]] = {}
    for judgment in judgments:
        by_case.setdefault(_string(judgment.get("review_case_id")), []).append(judgment)
    case_results: list[dict[str, object]] = []
    for case in contract["review_cases"]:
        if not isinstance(case, dict):
            continue
        review_case_id = _string(case["review_case_id"])
        case_judgments = by_case.get(review_case_id, [])
        if not case_judgments:
            continue
        output_labels = [
            _string(judgment["reviewer_output"]["output_label"]) for judgment in case_judgments
        ]
        winner_arms = [_reviewer_winner_arm(judgment) for judgment in case_judgments]
        visibility_judgments = [
            _string(judgment["reviewer_output"]["visibility_judgment"])
            for judgment in case_judgments
        ]
        families = sorted(
            {
                _string(judgment["provider_metadata"].get("model_family"))
                for judgment in case_judgments
                if _string(judgment["provider_metadata"].get("model_family"))
            }
        )
        consistency = _reviewer_label_consistency(
            output_labels=output_labels,
            winner_arms=winner_arms,
        )
        confirmed = _confirmed_visibility_label(
            expected_visibility=_string(case["expected_visibility_decision"]),
            visibility_judgments=visibility_judgments,
            families=families,
            consistency=consistency,
        )
        case_results.append(
            {
                "review_case_id": review_case_id,
                "source_case_id": _string(case["source_case_id"]),
                "sample_index": int(case["sample_index"]),
                "expected_visibility_decision": _string(case["expected_visibility_decision"]),
                "pure_structural_delta_only": bool(case["pure_structural_delta_only"]),
                "reviewer_count": len(case_judgments),
                "reviewer_model_families": families,
                "output_labels": output_labels,
                "reviewer_winner_arms": winner_arms,
                "visibility_judgments": visibility_judgments,
                "reviewer_label_consistency": consistency,
                "confirmed_visibility_label": confirmed,
            }
        )
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_results": case_results,
        "aggregate": _aggregate_result(case_results, expected_case_count=len(contract["review_cases"])),
        "gates": _blocked_gates(),
        "notes": (
            "Split-rubric review of GPT-stable outputs. A supported result would "
            "make GPT stability evidence, not a model-shopping shortcut."
        ),
    }
    validate_gpt_stability_correctness_result(payload)
    return payload


def write_gpt_stability_correctness_judgment(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_gpt_stability_correctness_judgment(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = _string(payload["provider_metadata"].get("model")).replace("/", "__")
    path = out_dir / f"{_string(payload['review_case_id'])}.{model_slug}.gpt-stability-judgment.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_gpt_stability_correctness_judgment(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise GPTStabilityCorrectnessError(f"{path}: payload must be object")
    validate_gpt_stability_correctness_judgment(payload, path=path)
    return payload


def write_gpt_stability_correctness_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_gpt_stability_correctness_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "gpt-stability-correctness-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_gpt_stability_correctness_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise GPTStabilityCorrectnessError(f"{path}: payload must be object")
    validate_gpt_stability_correctness_result(payload, path=path)
    return payload


def validate_gpt_stability_correctness_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_gpt_stability_correctness_contract_errors(payload, path=path))
    if errors:
        raise GPTStabilityCorrectnessError("; ".join(errors))


def iter_gpt_stability_correctness_contract_errors(
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
    if payload.get("runtime_policy") != RUNTIME_POLICY:
        yield f"{path / 'runtime_policy'}: must be {RUNTIME_POLICY}"
    if payload.get("promotion_effect") != "none_research_only":
        yield f"{path / 'promotion_effect'}: must be none_research_only"
    yield from _validate_reviewer_rule(payload.get("reviewer_rule"), path / "reviewer_rule")
    response_shapes = payload.get("precommitted_response_shapes")
    if not isinstance(response_shapes, dict):
        yield f"{path / 'precommitted_response_shapes'}: must be object"
    else:
        yield from _unknown_fields(response_shapes, RESPONSE_SHAPE_FIELDS, path / "precommitted_response_shapes")
        yield from _missing_fields(response_shapes, RESPONSE_SHAPE_FIELDS, path / "precommitted_response_shapes")
    cases = payload.get("review_cases")
    if not isinstance(cases, list) or not cases:
        yield f"{path / 'review_cases'}: must be non-empty list"
    else:
        for index, case in enumerate(cases):
            yield from _validate_case(case, path / "review_cases" / str(index))
    excluded = payload.get("excluded_case_ids")
    if not isinstance(excluded, list):
        yield f"{path / 'excluded_case_ids'}: must be list"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_gpt_stability_correctness_judgment(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_gpt_stability_correctness_judgment_errors(payload, path=path))
    if errors:
        raise GPTStabilityCorrectnessError("; ".join(errors))


def iter_gpt_stability_correctness_judgment_errors(
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
    yield from _validate_provider_metadata(payload.get("provider_metadata"), path / "provider_metadata")
    blind_map, blind_errors = _validate_blind_map(payload.get("blind_map"), path / "blind_map")
    yield from blind_errors
    yield from _validate_reviewer_output(
        payload.get("reviewer_output"),
        blind_map=blind_map,
        path=path / "reviewer_output",
    )
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_gpt_stability_correctness_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_gpt_stability_correctness_result_errors(payload, path=path))
    if errors:
        raise GPTStabilityCorrectnessError("; ".join(errors))


def iter_gpt_stability_correctness_result_errors(
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
    results = payload.get("case_results")
    if not isinstance(results, list):
        yield f"{path / 'case_results'}: must be list"
    else:
        for index, result in enumerate(results):
            yield from _validate_case_result(result, path / "case_results" / str(index))
    yield from _validate_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _include_sample(sample: dict[str, object]) -> bool:
    case_id = _string(sample.get("case_id"))
    if case_id in EXCLUDED_UNSTABLE_CASE_IDS:
        return False
    if case_id == "mid-level-consultant-report-2":
        return sample.get("ledger_signal") == "all_private_or_confirming"
    if case_id in {"third-year-phd-student.v2.v60-off", "third-year-phd-student.v2.v60-on"}:
        return _sample_unlocks(sample)
    return False


def _case_from_sample(*, root: Path, sample_path: Path, sample: dict[str, object]) -> dict[str, object]:
    input_packet = sample["input_packet"]
    assert isinstance(input_packet, dict)
    output = sample["step6_output"]
    assert isinstance(output, dict)
    case_id = _string(sample["case_id"])
    sample_index = int(sample["sample_index"])
    expected = "step6_visible" if _sample_unlocks(sample) else "anchor_visible"
    answer_delta_summary = _answer_delta_summary(output)
    specificity = _string(sample.get("answer_delta_specificity"))
    return {
        "review_case_id": f"{case_id}.sample-{sample_index}.gpt-{expected.replace('_', '-')}",
        "source_case_id": case_id,
        "sample_ref": str(sample_path.relative_to(root)),
        "sample_index": sample_index,
        "model_under_review": _string(sample["provider_metadata"].get("model")),
        "expected_visibility_decision": expected,
        "case_brief": _string(input_packet.get("case_brief")),
        "anchor_visible": _string(input_packet.get("anchor_visible_candidate")),
        "step6_visible": _string(output.get("answer_core")),
        "ledger_signal": _string(sample.get("ledger_signal")),
        "answer_delta_specificity": specificity,
        "answer_delta_summary": answer_delta_summary,
        "pure_structural_delta_only": specificity == "structural_delta_present",
    }


def _sample_unlocks(sample: dict[str, object]) -> bool:
    return (
        sample.get("ledger_signal") == "additive_pressure_present"
        and sample.get("answer_delta_specificity") in UNLOCKING_SPECIFICITY
    )


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


def _dominant_model(samples: Sequence[dict[str, object]]) -> str:
    counts: dict[str, int] = {}
    for sample in samples:
        metadata = sample.get("provider_metadata")
        if isinstance(metadata, dict):
            model = _string(metadata.get("model"))
            if model:
                counts[model] = counts.get(model, 0) + 1
    if not counts:
        return "unknown"
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def _aggregate_result(case_results: list[dict[str, object]], *, expected_case_count: int) -> dict[str, object]:
    visible = [row for row in case_results if row.get("expected_visibility_decision") == "step6_visible"]
    anchor = [row for row in case_results if row.get("expected_visibility_decision") == "anchor_visible"]
    ambiguous = sum(1 for row in case_results if row.get("confirmed_visibility_label") in {"ambiguous", "not_observed"})
    tension = sum(1 for row in case_results if row.get("reviewer_label_consistency") == "tension_detected")
    visible_rejected = sum(1 for row in visible if row.get("confirmed_visibility_label") == "gpt_visible_rejected")
    anchor_rejected = sum(1 for row in anchor if row.get("confirmed_visibility_label") == "gpt_anchor_rejected")
    structural_rows = [row for row in case_results if row.get("pure_structural_delta_only") is True]
    structural_rejected = sum(
        1 for row in structural_rows if row.get("confirmed_visibility_label") == "gpt_visible_rejected"
    )
    if visible_rejected or anchor_rejected or structural_rejected:
        read = "gpt_stability_design_review_required"
        action = "do_not_model_route_for_stability_until_rejections_are_explained"
    elif len(case_results) < expected_case_count or ambiguous or tension:
        read = "gpt_stability_partial_or_incomplete"
        action = "complete_or_inspect_ambiguous_gpt_stability_reviews_before_architecture_choice"
    else:
        read = "gpt_stability_supported"
        action = "treat_model_family_stability_as_calibrated_evidence_not_runtime_selector"
    return {
        "case_count": len(case_results),
        "gpt_visible_case_count": len(visible),
        "gpt_anchor_case_count": len(anchor),
        "gpt_visible_supported_count": sum(
            1 for row in visible if row.get("confirmed_visibility_label") == "gpt_visible_supported"
        ),
        "gpt_visible_rejected_count": visible_rejected,
        "gpt_anchor_supported_count": sum(
            1 for row in anchor if row.get("confirmed_visibility_label") == "gpt_anchor_supported"
        ),
        "gpt_anchor_rejected_count": anchor_rejected,
        "ambiguous_count": ambiguous,
        "tension_count": tension,
        "structural_delta_only_reviewed_count": len(structural_rows),
        "structural_delta_only_supported_count": sum(
            1 for row in structural_rows if row.get("confirmed_visibility_label") == "gpt_visible_supported"
        ),
        "structural_delta_only_rejected_count": structural_rejected,
        "reviewer_read": read,
        "recommended_next_action": action,
    }


def _confirmed_visibility_label(
    *,
    expected_visibility: str,
    visibility_judgments: list[str],
    families: list[str],
    consistency: str,
) -> str:
    if len(families) < 2 or len(visibility_judgments) < 2:
        return "not_observed"
    if consistency == "tension_detected":
        return "ambiguous"
    visible_should_show = {"correct_visible", "wrong_anchor"}
    anchor_should_show = {"correct_anchor", "wrong_visible"}
    if expected_visibility == "step6_visible":
        if all(judgment in visible_should_show for judgment in visibility_judgments):
            return "gpt_visible_supported"
        if all(judgment in anchor_should_show for judgment in visibility_judgments):
            return "gpt_visible_rejected"
        return "ambiguous"
    if expected_visibility == "anchor_visible":
        if all(judgment in anchor_should_show for judgment in visibility_judgments):
            return "gpt_anchor_supported"
        if all(judgment in visible_should_show for judgment in visibility_judgments):
            return "gpt_anchor_rejected"
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


def _reviewer_label_consistency(*, output_labels: Sequence[str], winner_arms: Sequence[str]) -> str:
    if not output_labels:
        return "not_applicable"
    for label, winner_arm in zip(output_labels, winner_arms, strict=False):
        if label == "better" and winner_arm != "step6_visible":
            return "tension_detected"
        if label == "worse_unwise" and winner_arm != "anchor_visible":
            return "tension_detected"
        if label == "tie" and winner_arm != "tie":
            return "tension_detected"
        if label == "non_inferior" and winner_arm not in {
            "step6_visible",
            "anchor_visible",
            "tie",
        }:
            return "tension_detected"
    return "aligned"


def _normalize_reviewer_output(value: object, *, blind_map: dict[str, str]) -> dict[str, object]:
    if not isinstance(value, dict):
        value = {}
    output_label = _string(value.get("output_label"))
    if output_label not in ALLOWED_OUTPUT_LABELS:
        output_label = "ambiguous"
    winner = _string(value.get("winner_label"))
    if winner not in set(blind_map) | {"tie"}:
        winner = "tie"
    visibility = _string(value.get("visibility_judgment"))
    if visibility not in ALLOWED_VISIBILITY_JUDGMENTS:
        visibility = "ambiguous"
    confidence = _string(value.get("confidence"))
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"
    structural = _string(value.get("structural_delta_read"))
    if structural not in {
        "useful_structural_delta",
        "loophole_or_vague",
        "not_applicable",
        "ambiguous",
    }:
        structural = "ambiguous"
    return {
        "output_label": output_label,
        "winner_label": winner,
        "visibility_judgment": visibility,
        "confidence": confidence,
        "rationale": _string(value.get("rationale")) or "Reviewer did not provide rationale.",
        "answer_correctness_notes": _string_list(value.get("answer_correctness_notes"), fallback="none"),
        "visibility_decision_notes": _string_list(value.get("visibility_decision_notes"), fallback="none"),
        "payload_loss_or_bloat": _string_list(value.get("payload_loss_or_bloat"), fallback="none"),
        "structural_delta_read": structural,
    }


def _reviewer_system_prompt(*, expected_visibility: str) -> str:
    return (
        "You are a blind reviewer for a research-only GPT stability correctness "
        "review. Return strict JSON only. You will compare an anchor-visible "
        "answer with a saved GPT Step 6 answer. The private expected visibility "
        f"decision under review is {expected_visibility}. Judge answer quality "
        "and visibility decision separately. Do not reward model-family stability "
        "as correctness. Prefer grounded, concrete, action-guiding answers that "
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
    if not isinstance(value.get("reviewer_question_split"), list):
        yield f"{path / 'reviewer_question_split'}: must be list"


def _validate_case(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case must be object"
        return
    yield from _unknown_fields(value, CASE_FIELDS, path)
    yield from _missing_fields(value, CASE_FIELDS, path)
    if any(field not in value for field in CASE_FIELDS):
        return
    if value.get("expected_visibility_decision") not in {"anchor_visible", "step6_visible"}:
        yield f"{path / 'expected_visibility_decision'}: invalid expected visibility"
    for field in (
        "review_case_id",
        "source_case_id",
        "sample_ref",
        "model_under_review",
        "case_brief",
        "anchor_visible",
        "step6_visible",
        "ledger_signal",
        "answer_delta_specificity",
    ):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if not isinstance(value.get("sample_index"), int):
        yield f"{path / 'sample_index'}: must be integer"
    if not isinstance(value.get("answer_delta_summary"), dict):
        yield f"{path / 'answer_delta_summary'}: must be object"
    if not isinstance(value.get("pure_structural_delta_only"), bool):
        yield f"{path / 'pure_structural_delta_only'}: must be bool"


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
    if _string(value.get("output_label")) not in ALLOWED_OUTPUT_LABELS:
        yield f"{path / 'output_label'}: invalid output label"
    winner = _string(value.get("winner_label"))
    if winner != "tie" and winner not in blind_map:
        yield f"{path / 'winner_label'}: must be A, B, or tie"
    if _string(value.get("visibility_judgment")) not in ALLOWED_VISIBILITY_JUDGMENTS:
        yield f"{path / 'visibility_judgment'}: invalid visibility judgment"
    if _string(value.get("confidence")) not in {"high", "medium", "low"}:
        yield f"{path / 'confidence'}: invalid confidence"
    for field in ("answer_correctness_notes", "visibility_decision_notes", "payload_loss_or_bloat"):
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
    if value.get("expected_visibility_decision") not in {"anchor_visible", "step6_visible"}:
        yield f"{path / 'expected_visibility_decision'}: invalid expected visibility"
    if _string(value.get("confirmed_visibility_label")) not in ALLOWED_CONFIRMED_LABELS:
        yield f"{path / 'confirmed_visibility_label'}: invalid confirmed label"
    if not isinstance(value.get("sample_index"), int):
        yield f"{path / 'sample_index'}: must be integer"
    if not isinstance(value.get("reviewer_count"), int):
        yield f"{path / 'reviewer_count'}: must be integer"
    for field in ("reviewer_model_families", "output_labels", "reviewer_winner_arms", "visibility_judgments"):
        if not isinstance(value.get(field), list):
            yield f"{path / field}: must be list"


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


def _case_by_id(contract: dict[str, object], review_case_id: str) -> dict[str, object]:
    cases = contract.get("review_cases")
    if not isinstance(cases, list):
        raise GPTStabilityCorrectnessError("review_cases missing")
    for case in cases:
        if isinstance(case, dict) and case.get("review_case_id") == review_case_id:
            return case
    raise GPTStabilityCorrectnessError(f"unknown review case: {review_case_id}")


def _review_case_ids(args: argparse.Namespace, contract: dict[str, object]) -> list[str]:
    if args.review_case_id:
        return args.review_case_id
    cases = contract.get("review_cases")
    if not isinstance(cases, list):
        return []
    return [_string(case.get("review_case_id")) for case in cases if isinstance(case, dict)]


def _load_env_file(path: Path) -> None:
    if not path.exists():
        raise GPTStabilityCorrectnessError(f"env file missing: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _model_family(model: str) -> str:
    if "/" in model:
        return model.split("/", 1)[0].split(".", 1)[0]
    return model.split("-", 1)[0] if model else "unknown"


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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--judgment-dir", type=Path, default=DEFAULT_JUDGMENT_DIR)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--live-review", action="store_true")
    parser.add_argument("--rebuild-result", action="store_true")
    parser.add_argument("--review-case-id", action="append", default=[])
    parser.add_argument("--reviewer-model", action="append", default=[])
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise GPTStabilityCorrectnessError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_gpt_stability_correctness_contract(payload, path=path)
            elif schema == JUDGMENT_SCHEMA_VERSION:
                validate_gpt_stability_correctness_judgment(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_gpt_stability_correctness_result(payload, path=path)
            else:
                raise GPTStabilityCorrectnessError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_gpt_stability_correctness_contract(args.contract)
        if args.contract
        else build_gpt_stability_correctness_contract(root=Path.cwd(), sample_dir=args.sample_dir)
    )
    if args.write_contract:
        print(write_gpt_stability_correctness_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.live_review:
        models = args.reviewer_model or list(DEFAULT_REVIEWER_MODELS)
        for review_case_id in _review_case_ids(args, contract):
            for model in models:
                output = run_live_reviewer(
                    contract=contract,
                    review_case_id=review_case_id,
                    provider=args.provider,
                    model=model,
                    env_file=args.env_file,
                    out_dir=args.judgment_dir,
                    seed=DEFAULT_SEED,
                    dry_run=args.dry_run,
                )
                if output is not None:
                    print(output)
    if args.rebuild_result or args.live_review:
        judgments = [
            load_gpt_stability_correctness_judgment(path)
            for path in sorted(args.judgment_dir.glob("*.json"))
        ]
        result = build_gpt_stability_correctness_result(contract=contract, judgments=judgments)
        print(write_gpt_stability_correctness_result(payload=result, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
