#!/usr/bin/env python3
"""Research-only founder V60 symmetry check.

This artifact tests whether the founder residual variance is plausibly tied to
V60-on context, or whether the base founder case is itself borderline. It does
not select an answer and does not add a runtime gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable, Sequence

from pre_step6_calibration_corpus import (
    load_step6_calibration_sample,
    validate_step6_calibration_sample,
)


CONTRACT_SCHEMA_VERSION = "pre_step6_founder_v60_symmetry_contract.v1"
RESULT_SCHEMA_VERSION = "pre_step6_founder_v60_symmetry_result.v1"
RUNTIME_POLICY = "runtime_dormant"
STATUS = "research_only"
EXPERIMENT_ID = "pre_step6_founder_v60_symmetry_check_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-founder-v60-symmetry-check")
CASE_FAMILY = "founder-grant-marcus-equity.high-clutter"
FOUNDER_V60_ON = f"{CASE_FAMILY}.v60-on"
FOUNDER_V60_OFF = f"{CASE_FAMILY}.v60-off"
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
        "case_id": FOUNDER_V60_OFF,
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
        "case_id": FOUNDER_V60_OFF,
        "sample_dir": "research/pre-step6-founder-v60-symmetry-gpt51/step6-samples",
    },
)
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "case_family",
        "sample_sets",
        "precommitted_outcomes",
        "gates",
        "notes",
    }
)
SAMPLE_SET_FIELDS = frozenset({"model_family", "model", "v60_mode", "case_id", "sample_dir"})
RESULT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "comparison_matrix",
        "aggregate",
        "gates",
        "notes",
    }
)
MATRIX_FIELDS = frozenset(
    {
        "model_family",
        "model",
        "v60_mode",
        "case_id",
        "sample_dir",
        "sample_count",
        "unlock_count",
        "unlock_ratio",
        "visibility_classification",
        "ledger_signal_counts",
        "answer_delta_specificity_counts",
        "structural_delta_count",
        "structural_delta_field_count",
        "answer_core_unique_digest_count",
        "answer_token_jaccard_min",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "founder_family_count",
        "complete_family_count",
        "v60_on_variable_family_count",
        "v60_off_variable_family_count",
        "v60_on_stable_positive_family_count",
        "v60_off_stable_positive_family_count",
        "missing_sample_set_count",
        "symmetry_read",
        "recommended_next_action",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
UNLOCKING_SPECIFICITY = frozenset({"concrete_delta_present", "structural_delta_present"})
ALLOWED_VISIBILITY_CLASSIFICATIONS = frozenset(
    {"stable_positive", "stable_standdown", "variable", "not_sampled"}
)


class FounderV60SymmetryError(ValueError):
    pass


def build_founder_v60_symmetry_contract(*, root: Path | None = None) -> dict[str, object]:
    _ = root
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_family": CASE_FAMILY,
        "sample_sets": [dict(item) for item in DEFAULT_SAMPLE_SETS],
        "precommitted_outcomes": {
            "v60_on_specific_destabilization": (
                "V60-on is variable while same-model V60-off is stable; audit V60 "
                "private context before treating founder variance as portfolio-policy evidence."
            ),
            "base_case_borderline_or_model_noise": (
                "V60-off is also variable for a model family; treat founder as a "
                "case-shape/model-stability issue before architecture changes."
            ),
            "missing_symmetry_samples": (
                "One or more sample sets is absent; do not infer symmetry until "
                "the missing family/mode samples land."
            ),
            "no_founder_specific_architecture_change": (
                "No V60-specific destabilization pattern appears; keep founder in "
                "the broader variable-case analysis."
            ),
        },
        "gates": _blocked_gates(),
        "notes": (
            "Research-only comparison of saved founder V60-on/off samples. "
            "The deterministic layer compares stability shape only; it does not "
            "decide which answer is wiser."
        ),
    }
    validate_founder_v60_symmetry_contract(payload)
    return payload


def write_founder_v60_symmetry_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_founder_v60_symmetry_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "founder-v60-symmetry-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_founder_v60_symmetry_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise FounderV60SymmetryError(f"{path}: payload must be object")
    validate_founder_v60_symmetry_contract(payload, path=path)
    return payload


def build_founder_v60_symmetry_result(
    *,
    root: Path,
    contract: dict[str, object],
) -> dict[str, object]:
    validate_founder_v60_symmetry_contract(contract)
    root = Path(root)
    matrix = [_matrix_row(root=root, sample_set=sample_set) for sample_set in contract["sample_sets"]]
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "comparison_matrix": matrix,
        "aggregate": _aggregate(matrix),
        "gates": _blocked_gates(),
        "notes": (
            "Founder symmetry check over saved samples. Missing sample sets are "
            "reported as missing rather than interpreted."
        ),
    }
    validate_founder_v60_symmetry_result(payload)
    return payload


def write_founder_v60_symmetry_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_founder_v60_symmetry_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "founder-v60-symmetry-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_founder_v60_symmetry_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise FounderV60SymmetryError(f"{path}: payload must be object")
    validate_founder_v60_symmetry_result(payload, path=path)
    return payload


def validate_founder_v60_symmetry_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_founder_v60_symmetry_contract_errors(payload, path=path))
    if errors:
        raise FounderV60SymmetryError("; ".join(errors))


def iter_founder_v60_symmetry_contract_errors(
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
    if payload.get("case_family") != CASE_FAMILY:
        yield f"{path / 'case_family'}: must be {CASE_FAMILY}"
    sample_sets = payload.get("sample_sets")
    if not isinstance(sample_sets, list) or not sample_sets:
        yield f"{path / 'sample_sets'}: must be non-empty list"
    else:
        for index, sample_set in enumerate(sample_sets):
            yield from _validate_sample_set(sample_set, path / "sample_sets" / str(index))
    outcomes = payload.get("precommitted_outcomes")
    if not isinstance(outcomes, dict):
        yield f"{path / 'precommitted_outcomes'}: must be object"
    elif not {
        "v60_on_specific_destabilization",
        "base_case_borderline_or_model_noise",
        "missing_symmetry_samples",
        "no_founder_specific_architecture_change",
    } <= set(outcomes):
        yield f"{path / 'precommitted_outcomes'}: missing expected outcomes"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_founder_v60_symmetry_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_founder_v60_symmetry_result_errors(payload, path=path))
    if errors:
        raise FounderV60SymmetryError("; ".join(errors))


def iter_founder_v60_symmetry_result_errors(
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
    matrix = payload.get("comparison_matrix")
    if not isinstance(matrix, list):
        yield f"{path / 'comparison_matrix'}: must be list"
    else:
        for index, row in enumerate(matrix):
            yield from _validate_matrix_row(row, path / "comparison_matrix" / str(index))
    yield from _validate_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _matrix_row(*, root: Path, sample_set: object) -> dict[str, object]:
    if not isinstance(sample_set, dict):
        sample_set = {}
    sample_dir = root / _string(sample_set.get("sample_dir"))
    case_id = _string(sample_set.get("case_id"))
    samples = []
    if sample_dir.exists():
        samples = [
            load_step6_calibration_sample(path)
            for path in sorted(sample_dir.glob(f"{case_id}.sample-*.calibration-step6.v1.json"))
        ]
    for sample in samples:
        validate_step6_calibration_sample(sample)
    unlock_count = sum(1 for sample in samples if _sample_unlocks(sample))
    answer_texts = [_answer_core(sample) for sample in samples]
    return {
        "model_family": _string(sample_set.get("model_family")),
        "model": _string(sample_set.get("model")),
        "v60_mode": _string(sample_set.get("v60_mode")),
        "case_id": case_id,
        "sample_dir": _string(sample_set.get("sample_dir")),
        "sample_count": len(samples),
        "unlock_count": unlock_count,
        "unlock_ratio": round(unlock_count / len(samples), 3) if samples else 0.0,
        "visibility_classification": _visibility_classification(
            sample_count=len(samples),
            unlock_count=unlock_count,
        ),
        "ledger_signal_counts": _counts(_string(sample.get("ledger_signal")) for sample in samples),
        "answer_delta_specificity_counts": _counts(
            _string(sample.get("answer_delta_specificity")) for sample in samples
        ),
        "structural_delta_count": sum(
            1 for sample in samples if sample.get("answer_delta_specificity") == "structural_delta_present"
        ),
        "structural_delta_field_count": sum(1 for sample in samples if _has_structural_delta_field(sample)),
        "answer_core_unique_digest_count": len({_digest(text) for text in answer_texts if text}),
        "answer_token_jaccard_min": _rounded_min_jaccard(answer_texts),
    }


def _aggregate(matrix: list[dict[str, object]]) -> dict[str, object]:
    complete_families = _complete_families(matrix)
    on_variable = [
        row
        for row in matrix
        if row.get("v60_mode") == "on" and row.get("visibility_classification") == "variable"
    ]
    off_variable = [
        row
        for row in matrix
        if row.get("v60_mode") == "off" and row.get("visibility_classification") == "variable"
    ]
    on_stable_positive = [
        row
        for row in matrix
        if row.get("v60_mode") == "on" and row.get("visibility_classification") == "stable_positive"
    ]
    off_stable_positive = [
        row
        for row in matrix
        if row.get("v60_mode") == "off" and row.get("visibility_classification") == "stable_positive"
    ]
    missing = [row for row in matrix if row.get("visibility_classification") == "not_sampled"]
    if missing:
        read = "missing_symmetry_samples"
        action = "complete_missing_symmetry_samples_before_interpretation"
    elif on_variable and not off_variable:
        read = "v60_on_specific_destabilization_plausible"
        action = "audit_v60_private_context_before_architecture_choice"
    elif off_variable:
        read = "base_case_borderline_or_model_noise"
        action = "treat_founder_as_case_shape_borderline_before_architecture_choice"
    else:
        read = "no_founder_specific_v60_destabilization"
        action = "no_founder_specific_architecture_change"
    return {
        "founder_family_count": len({row.get("model_family") for row in matrix if row.get("model_family")}),
        "complete_family_count": len(complete_families),
        "v60_on_variable_family_count": len({row.get("model_family") for row in on_variable}),
        "v60_off_variable_family_count": len({row.get("model_family") for row in off_variable}),
        "v60_on_stable_positive_family_count": len({row.get("model_family") for row in on_stable_positive}),
        "v60_off_stable_positive_family_count": len({row.get("model_family") for row in off_stable_positive}),
        "missing_sample_set_count": len(missing),
        "symmetry_read": read,
        "recommended_next_action": action,
    }


def _complete_families(matrix: list[dict[str, object]]) -> set[str]:
    modes_by_family: dict[str, set[str]] = {}
    for row in matrix:
        if row.get("visibility_classification") == "not_sampled":
            continue
        family = _string(row.get("model_family"))
        if family:
            modes_by_family.setdefault(family, set()).add(_string(row.get("v60_mode")))
    return {family for family, modes in modes_by_family.items() if {"on", "off"} <= modes}


def _visibility_classification(*, sample_count: int, unlock_count: int) -> str:
    if sample_count == 0:
        return "not_sampled"
    if unlock_count == sample_count:
        return "stable_positive"
    if unlock_count == 0:
        return "stable_standdown"
    return "variable"


def _sample_unlocks(sample: dict[str, object]) -> bool:
    return (
        sample.get("ledger_signal") == "additive_pressure_present"
        and sample.get("answer_delta_specificity") in UNLOCKING_SPECIFICITY
    )


def _answer_core(sample: dict[str, object]) -> str:
    output = sample.get("step6_output")
    if not isinstance(output, dict):
        return ""
    return _string(output.get("answer_core"))


def _has_structural_delta_field(sample: dict[str, object]) -> bool:
    output = sample.get("step6_output")
    if not isinstance(output, dict):
        return False
    ledger = output.get("private_visibility_ledger")
    if not isinstance(ledger, list):
        return False
    for item in ledger:
        if not isinstance(item, dict) or item.get("source_id") != "deck_pressure_candidate":
            continue
        delta = item.get("answer_delta")
        if not isinstance(delta, dict):
            continue
        values = delta.get("structural_delta")
        if isinstance(values, list) and any(_string(value).strip() for value in values):
            return True
    return False


def _rounded_min_jaccard(texts: Sequence[str]) -> float | None:
    value = _min_pairwise_jaccard(texts)
    return round(value, 3) if value is not None else None


def _min_pairwise_jaccard(texts: Sequence[str]) -> float | None:
    token_sets = [_tokens(text) for text in texts if text.strip()]
    if len(token_sets) < 2:
        return None
    scores = []
    for left_index, left in enumerate(token_sets):
        for right in token_sets[left_index + 1 :]:
            if not left and not right:
                scores.append(1.0)
            elif not left or not right:
                scores.append(0.0)
            else:
                scores.append(len(left & right) / len(left | right))
    return min(scores) if scores else None


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def _digest(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()[:16]


def _validate_sample_set(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: sample set must be object"
        return
    yield from _unknown_fields(value, SAMPLE_SET_FIELDS, path)
    yield from _missing_fields(value, SAMPLE_SET_FIELDS, path)
    for field in SAMPLE_SET_FIELDS:
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if value.get("v60_mode") not in {"on", "off"}:
        yield f"{path / 'v60_mode'}: must be on or off"


def _validate_matrix_row(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: matrix row must be object"
        return
    yield from _unknown_fields(value, MATRIX_FIELDS, path)
    yield from _missing_fields(value, MATRIX_FIELDS, path)
    if any(field not in value for field in MATRIX_FIELDS):
        return
    for field in ("model_family", "model", "v60_mode", "case_id", "sample_dir"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if value.get("visibility_classification") not in ALLOWED_VISIBILITY_CLASSIFICATIONS:
        yield f"{path / 'visibility_classification'}: invalid visibility classification"
    for field in (
        "sample_count",
        "unlock_count",
        "structural_delta_count",
        "structural_delta_field_count",
        "answer_core_unique_digest_count",
    ):
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    if not isinstance(value.get("unlock_ratio"), float):
        yield f"{path / 'unlock_ratio'}: must be float"
    if not isinstance(value.get("ledger_signal_counts"), dict):
        yield f"{path / 'ledger_signal_counts'}: must be object"
    if not isinstance(value.get("answer_delta_specificity_counts"), dict):
        yield f"{path / 'answer_delta_specificity_counts'}: must be object"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    for field in AGGREGATE_FIELDS - {"symmetry_read", "recommended_next_action"}:
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    if not _string(value.get("symmetry_read")).strip():
        yield f"{path / 'symmetry_read'}: must be non-empty"
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


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        if value:
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


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
                raise FounderV60SymmetryError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_founder_v60_symmetry_contract(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_founder_v60_symmetry_result(payload, path=path)
            else:
                raise FounderV60SymmetryError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_founder_v60_symmetry_contract(args.contract)
        if args.contract
        else build_founder_v60_symmetry_contract(root=Path.cwd())
    )
    if args.write_contract:
        print(write_founder_v60_symmetry_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.write_result:
        result = build_founder_v60_symmetry_result(root=Path.cwd(), contract=contract)
        print(write_founder_v60_symmetry_result(payload=result, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
