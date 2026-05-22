#!/usr/bin/env python3
"""Research-only diagnostic for variable pre-Step-6 calibration cases.

This does not add a runtime gate. It reads saved samples for cases that stayed
unstable after same-prompt repeat sampling and characterizes the variance so
the next design discussion has evidence instead of vibes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from statistics import mean
from typing import Iterable, Sequence

from pre_step6_calibration_corpus import (
    load_calibration_corpus_contract,
    load_step6_calibration_sample,
    load_step6_calibration_stability_review,
    validate_calibration_corpus_contract,
    validate_step6_calibration_sample,
    validate_step6_calibration_stability_review,
)


CONTRACT_SCHEMA_VERSION = "pre_step6_variable_case_diagnostic_contract.v1"
RESULT_SCHEMA_VERSION = "pre_step6_variable_case_diagnostic_result.v1"
RUNTIME_POLICY = "runtime_dormant"
STATUS = "research_only"
EXPERIMENT_ID = "pre_step6_variable_case_diagnostic_v0"
DEFAULT_OUT_DIR = Path("research/pre-step6-variable-case-diagnostic")
DEFAULT_CORPUS_CONTRACT = Path(
    "research/pre-step6-calibration-corpus-kimi-structural-delta/calibration-corpus.v1.json"
)
DEFAULT_STABILITY_REVIEW = Path(
    "research/pre-step6-calibration-corpus-kimi-structural-delta/calibration-stability-review.v1.json"
)
DEFAULT_SAMPLE_DIR = Path("research/pre-step6-calibration-corpus-kimi-structural-delta/step6-samples")
VARIABLE_CLASSIFICATIONS = frozenset({"borderline_unlock", "unstable_mixed"})
CONTRACT_FIELDS = frozenset(
    {
        "schema_version",
        "status",
        "runtime_policy",
        "experiment_id",
        "promotion_effect",
        "source_corpus_ref",
        "source_stability_review_ref",
        "sample_dir_ref",
        "variable_case_ids",
        "diagnostic_questions",
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
        "case_diagnostics",
        "aggregate",
        "gates",
        "notes",
    }
)
CASE_DIAGNOSTIC_FIELDS = frozenset(
    {
        "case_id",
        "sample_count",
        "v60_mode",
        "case_type_tags",
        "ledger_signal_counts",
        "answer_delta_specificity_counts",
        "unlock_count",
        "unlock_ratio",
        "structural_delta_field_count",
        "answer_core_unique_digest_count",
        "answer_length_range",
        "answer_token_jaccard_min",
        "variance_read",
        "sample_observations",
    }
)
SAMPLE_OBSERVATION_FIELDS = frozenset(
    {
        "sample_index",
        "ledger_signal",
        "answer_delta_specificity",
        "answer_core_digest",
        "answer_core_char_count",
        "answer_delta_summary",
    }
)
AGGREGATE_FIELDS = frozenset(
    {
        "variable_case_count",
        "total_sample_count",
        "balanced_or_near_balanced_case_count",
        "strong_positive_tilt_case_count",
        "ledger_label_variance_dominant_count",
        "answer_and_ledger_variance_count",
        "v60_on_case_count",
        "v60_off_case_count",
        "v60_not_applicable_case_count",
        "diagnostic_read",
        "recommended_next_action",
    }
)
GATE_FIELDS = frozenset({"runtime_wiring_allowed", "skill_update_allowed"})
ALLOWED_VARIANCE_READS = frozenset(
    {"ledger_label_variance_dominant", "answer_and_ledger_variance", "insufficient_samples"}
)


class VariableCaseDiagnosticError(ValueError):
    pass


def build_variable_case_diagnostic_contract(
    *,
    root: Path,
    corpus_contract_path: Path = DEFAULT_CORPUS_CONTRACT,
    stability_review_path: Path = DEFAULT_STABILITY_REVIEW,
    sample_dir: Path = DEFAULT_SAMPLE_DIR,
) -> dict[str, object]:
    root = Path(root)
    corpus = load_calibration_corpus_contract(root / corpus_contract_path)
    validate_calibration_corpus_contract(corpus, root=root)
    review = load_step6_calibration_stability_review(root / stability_review_path)
    validate_step6_calibration_stability_review(review)
    variable_case_ids = [
        _string(row.get("case_id"))
        for row in review.get("case_reviews", [])
        if isinstance(row, dict)
        and _string(row.get("stability_classification")) in VARIABLE_CLASSIFICATIONS
    ]
    payload = {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "source_corpus_ref": str(corpus_contract_path),
        "source_stability_review_ref": str(stability_review_path),
        "sample_dir_ref": str(sample_dir),
        "variable_case_ids": variable_case_ids,
        "diagnostic_questions": [
            "Is variance only in Step 6's ledger label, or also in the answer content?",
            "Do variable cases cluster by V60 mode or case-shape tags?",
            "Which cases are balanced borderlines versus strong positive/negative tilts?",
            "What evidence is needed before any runtime policy can handle variable cases?",
        ],
        "gates": _blocked_gates(),
        "notes": (
            "This diagnostic characterizes unstable saved samples. It does not "
            "decide wisdom or add a deterministic runtime selector."
        ),
    }
    validate_variable_case_diagnostic_contract(payload)
    return payload


def write_variable_case_diagnostic_contract(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_variable_case_diagnostic_contract(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "variable-case-diagnostic-contract.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_variable_case_diagnostic_contract(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise VariableCaseDiagnosticError(f"{path}: payload must be object")
    validate_variable_case_diagnostic_contract(payload, path=path)
    return payload


def build_variable_case_diagnostic_result(
    *,
    root: Path,
    contract: dict[str, object],
) -> dict[str, object]:
    validate_variable_case_diagnostic_contract(contract)
    root = Path(root)
    corpus = load_calibration_corpus_contract(root / _string(contract["source_corpus_ref"]))
    cases_by_id = {
        _string(case.get("case_id")): case
        for case in corpus.get("cases", [])
        if isinstance(case, dict)
    }
    sample_dir = root / _string(contract["sample_dir_ref"])
    diagnostics = [
        _case_diagnostic(
            case_id=case_id,
            case=cases_by_id.get(case_id, {}),
            samples=[
                load_step6_calibration_sample(path)
                for path in sorted(sample_dir.glob(f"{case_id}.sample-*.calibration-step6.v1.json"))
            ],
        )
        for case_id in contract["variable_case_ids"]
    ]
    payload = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "experiment_id": EXPERIMENT_ID,
        "promotion_effect": "none_research_only",
        "case_diagnostics": diagnostics,
        "aggregate": _aggregate_result(diagnostics),
        "gates": _blocked_gates(),
        "notes": (
            "Variable-case diagnostic over saved calibration samples. Runtime and "
            "SKILL.md remain blocked."
        ),
    }
    validate_variable_case_diagnostic_result(payload)
    return payload


def write_variable_case_diagnostic_result(*, payload: dict[str, object], out_dir: Path) -> Path:
    validate_variable_case_diagnostic_result(payload)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "variable-case-diagnostic-result.v1.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_variable_case_diagnostic_result(path: Path) -> dict[str, object]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise VariableCaseDiagnosticError(f"{path}: payload must be object")
    validate_variable_case_diagnostic_result(payload, path=path)
    return payload


def validate_variable_case_diagnostic_contract(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_variable_case_diagnostic_contract_errors(payload, path=path))
    if errors:
        raise VariableCaseDiagnosticError("; ".join(errors))


def iter_variable_case_diagnostic_contract_errors(
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
    case_ids = payload.get("variable_case_ids")
    if not isinstance(case_ids, list) or not case_ids:
        yield f"{path / 'variable_case_ids'}: must be non-empty list"
    elif any(not _string(case_id).strip() for case_id in case_ids):
        yield f"{path / 'variable_case_ids'}: ids must be non-empty"
    questions = payload.get("diagnostic_questions")
    if not isinstance(questions, list) or not questions:
        yield f"{path / 'diagnostic_questions'}: must be non-empty list"
    yield from _validate_gates(payload.get("gates"), path / "gates")


def validate_variable_case_diagnostic_result(
    payload: dict[str, object],
    *,
    path: Path = Path("<payload>"),
) -> None:
    errors = list(iter_variable_case_diagnostic_result_errors(payload, path=path))
    if errors:
        raise VariableCaseDiagnosticError("; ".join(errors))


def iter_variable_case_diagnostic_result_errors(
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
    diagnostics = payload.get("case_diagnostics")
    if not isinstance(diagnostics, list):
        yield f"{path / 'case_diagnostics'}: must be list"
    else:
        for index, diagnostic in enumerate(diagnostics):
            yield from _validate_case_diagnostic(diagnostic, path / "case_diagnostics" / str(index))
    yield from _validate_aggregate(payload.get("aggregate"), path / "aggregate")
    yield from _validate_gates(payload.get("gates"), path / "gates")


def _case_diagnostic(
    *,
    case_id: str,
    case: dict[str, object],
    samples: Sequence[dict[str, object]],
) -> dict[str, object]:
    for sample in samples:
        validate_step6_calibration_sample(sample)
    observations = [_sample_observation(sample) for sample in sorted(samples, key=lambda s: int(s.get("sample_index") or 0))]
    ledger_counts = _counts(_string(sample.get("ledger_signal")) for sample in samples)
    specificity_counts = _counts(_string(sample.get("answer_delta_specificity")) for sample in samples)
    unlock_count = sum(
        1
        for sample in samples
        if sample.get("ledger_signal") == "additive_pressure_present"
        and sample.get("answer_delta_specificity") in {"concrete_delta_present", "structural_delta_present"}
    )
    answer_texts = [_answer_core(sample) for sample in samples]
    lengths = [len(text) for text in answer_texts]
    min_jaccard = _min_pairwise_jaccard(answer_texts)
    return {
        "case_id": case_id,
        "sample_count": len(samples),
        "v60_mode": _string(case.get("v60_mode")) or "unknown",
        "case_type_tags": _string_list(case.get("case_type_tags")),
        "ledger_signal_counts": ledger_counts,
        "answer_delta_specificity_counts": specificity_counts,
        "unlock_count": unlock_count,
        "unlock_ratio": round(unlock_count / len(samples), 3) if samples else 0.0,
        "structural_delta_field_count": sum(
            1 for sample in samples if _sample_has_structural_delta_field(sample)
        ),
        "answer_core_unique_digest_count": len({_digest(text) for text in answer_texts if text}),
        "answer_length_range": [min(lengths), max(lengths)] if lengths else [0, 0],
        "answer_token_jaccard_min": round(min_jaccard, 3) if min_jaccard is not None else None,
        "variance_read": _variance_read(sample_count=len(samples), min_jaccard=min_jaccard),
        "sample_observations": observations,
    }


def _sample_observation(sample: dict[str, object]) -> dict[str, object]:
    answer = _answer_core(sample)
    return {
        "sample_index": int(sample.get("sample_index") or 0),
        "ledger_signal": _string(sample.get("ledger_signal")),
        "answer_delta_specificity": _string(sample.get("answer_delta_specificity")),
        "answer_core_digest": _digest(answer),
        "answer_core_char_count": len(answer),
        "answer_delta_summary": _answer_delta_summary(sample.get("step6_output")),
    }


def _aggregate_result(diagnostics: list[dict[str, object]]) -> dict[str, object]:
    balanced = [
        diagnostic
        for diagnostic in diagnostics
        if 0.34 <= float(diagnostic.get("unlock_ratio") or 0.0) <= 0.67
    ]
    strong_positive = [
        diagnostic for diagnostic in diagnostics if float(diagnostic.get("unlock_ratio") or 0.0) > 0.67
    ]
    answer_and_ledger = [
        diagnostic
        for diagnostic in diagnostics
        if diagnostic.get("variance_read") == "answer_and_ledger_variance"
    ]
    label_dominant = [
        diagnostic
        for diagnostic in diagnostics
        if diagnostic.get("variance_read") == "ledger_label_variance_dominant"
    ]
    if answer_and_ledger:
        read = "variable_cases_include_answer_level_variance"
        action = "read_variable_outputs_before_architecture_decision"
    else:
        read = "variable_cases_look_like_ledger_label_variance"
        action = "design_review_step6_ledger_self_reporting_or_alternative_model_probe"
    return {
        "variable_case_count": len(diagnostics),
        "total_sample_count": sum(int(diagnostic.get("sample_count") or 0) for diagnostic in diagnostics),
        "balanced_or_near_balanced_case_count": len(balanced),
        "strong_positive_tilt_case_count": len(strong_positive),
        "ledger_label_variance_dominant_count": len(label_dominant),
        "answer_and_ledger_variance_count": len(answer_and_ledger),
        "v60_on_case_count": sum(1 for diagnostic in diagnostics if diagnostic.get("v60_mode") == "on"),
        "v60_off_case_count": sum(1 for diagnostic in diagnostics if diagnostic.get("v60_mode") == "off"),
        "v60_not_applicable_case_count": sum(
            1 for diagnostic in diagnostics if diagnostic.get("v60_mode") == "not_applicable"
        ),
        "diagnostic_read": read,
        "recommended_next_action": action,
    }


def _variance_read(*, sample_count: int, min_jaccard: float | None) -> str:
    if sample_count < 3 or min_jaccard is None:
        return "insufficient_samples"
    if min_jaccard >= 0.72:
        return "ledger_label_variance_dominant"
    return "answer_and_ledger_variance"


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


def _answer_core(sample: dict[str, object]) -> str:
    step6_output = sample.get("step6_output")
    if not isinstance(step6_output, dict):
        return ""
    return _string(step6_output.get("answer_core"))


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


def _sample_has_structural_delta_field(sample: dict[str, object]) -> bool:
    summary = _answer_delta_summary(sample.get("step6_output"))
    return any(summary.get("structural_delta") or [])


def _validate_case_diagnostic(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: case diagnostic must be object"
        return
    yield from _unknown_fields(value, CASE_DIAGNOSTIC_FIELDS, path)
    yield from _missing_fields(value, CASE_DIAGNOSTIC_FIELDS, path)
    if any(field not in value for field in CASE_DIAGNOSTIC_FIELDS):
        return
    for field in ("case_id", "v60_mode", "variance_read"):
        if not _string(value.get(field)).strip():
            yield f"{path / field}: must be non-empty"
    if value.get("variance_read") not in ALLOWED_VARIANCE_READS:
        yield f"{path / 'variance_read'}: invalid variance read"
    for field in (
        "sample_count",
        "unlock_count",
        "structural_delta_field_count",
        "answer_core_unique_digest_count",
    ):
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    if not isinstance(value.get("unlock_ratio"), float):
        yield f"{path / 'unlock_ratio'}: must be float"
    if not isinstance(value.get("case_type_tags"), list):
        yield f"{path / 'case_type_tags'}: must be list"
    if not isinstance(value.get("answer_length_range"), list) or len(value["answer_length_range"]) != 2:
        yield f"{path / 'answer_length_range'}: must be two-item list"
    observations = value.get("sample_observations")
    if not isinstance(observations, list):
        yield f"{path / 'sample_observations'}: must be list"
    else:
        for index, observation in enumerate(observations):
            yield from _validate_sample_observation(observation, path / "sample_observations" / str(index))


def _validate_sample_observation(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: sample observation must be object"
        return
    yield from _unknown_fields(value, SAMPLE_OBSERVATION_FIELDS, path)
    yield from _missing_fields(value, SAMPLE_OBSERVATION_FIELDS, path)
    if not isinstance(value.get("sample_index"), int):
        yield f"{path / 'sample_index'}: must be integer"
    if not _string(value.get("answer_core_digest")).strip():
        yield f"{path / 'answer_core_digest'}: must be non-empty"
    if not isinstance(value.get("answer_core_char_count"), int):
        yield f"{path / 'answer_core_char_count'}: must be integer"
    if not isinstance(value.get("answer_delta_summary"), dict):
        yield f"{path / 'answer_delta_summary'}: must be object"


def _validate_aggregate(value: object, path: Path) -> Iterable[str]:
    if not isinstance(value, dict):
        yield f"{path}: aggregate must be object"
        return
    yield from _unknown_fields(value, AGGREGATE_FIELDS, path)
    yield from _missing_fields(value, AGGREGATE_FIELDS, path)
    for field in AGGREGATE_FIELDS - {"diagnostic_read", "recommended_next_action"}:
        if not isinstance(value.get(field), int) or value.get(field) < 0:
            yield f"{path / field}: must be non-negative integer"
    if not _string(value.get("diagnostic_read")).strip():
        yield f"{path / 'diagnostic_read'}: must be non-empty"
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


def _digest(text: str) -> str:
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()[:16]


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


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_string(item) for item in value if _string(item)]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--corpus-contract", type=Path, default=DEFAULT_CORPUS_CONTRACT)
    parser.add_argument("--stability-review", type=Path, default=DEFAULT_STABILITY_REVIEW)
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--write-contract", action="store_true")
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)

    if args.paths:
        for path in args.paths:
            payload = _read_json(path)
            if not isinstance(payload, dict):
                raise VariableCaseDiagnosticError(f"{path}: payload must be object")
            schema = payload.get("schema_version")
            if schema == CONTRACT_SCHEMA_VERSION:
                validate_variable_case_diagnostic_contract(payload, path=path)
            elif schema == RESULT_SCHEMA_VERSION:
                validate_variable_case_diagnostic_result(payload, path=path)
            else:
                raise VariableCaseDiagnosticError(f"{path}: unknown schema_version")
        return 0

    contract = (
        load_variable_case_diagnostic_contract(args.contract)
        if args.contract is not None
        else build_variable_case_diagnostic_contract(
            root=Path.cwd(),
            corpus_contract_path=args.corpus_contract,
            stability_review_path=args.stability_review,
            sample_dir=args.sample_dir,
        )
    )
    if args.write_contract:
        print(write_variable_case_diagnostic_contract(payload=contract, out_dir=args.out_dir))
        return 0
    if args.write_result:
        result = build_variable_case_diagnostic_result(root=Path.cwd(), contract=contract)
        print(write_variable_case_diagnostic_result(payload=result, out_dir=args.out_dir))
        return 0
    print(json.dumps(contract, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
