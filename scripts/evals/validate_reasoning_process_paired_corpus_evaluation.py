#!/usr/bin/env python3
"""Validate the provider-free non-scalar paired-role corpus review."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DIMENSIONS = (
    "central_role_allocation", "protected_qualification_survival", "speaker_ownership",
    "evidence_precision", "expression_force", "object_category_precision",
    "relationship_preservation",
)
FORBIDDEN_AGGREGATE_KEYS = {"score", "rating", "weighted_score", "total_score", "average_score", "rank", "confidence_score"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _walk(value: object, path: str = "root") -> list[str]:
    errors = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_AGGREGATE_KEYS:
                errors.append(f"{path}.{key}: forbidden aggregate field")
            errors.extend(_walk(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk(child, f"{path}[{index}]"))
    return errors


def validate(contract_path: Path, review_path: Path) -> dict:
    contract, review = _load(contract_path), _load(review_path)
    errors = _walk(contract, "contract") + _walk(review, "review")
    if tuple(contract.get("dimensions", {}).keys()) != DIMENSIONS:
        errors.append("contract dimensions drifted")
    allowed = set(contract.get("allowed_dispositions", []))
    cases = review.get("reviewed_cases", [])
    if len(cases) != 4:
        errors.append("exactly four preserved provider cases are required")
    expected_architectures = {
        "independent_role_first_v22", "independent_role_first_v23",
        "paired_role_first_v24", "status_free_paired_role_first_v241",
    }
    if {case.get("architecture") for case in cases} != expected_architectures:
        errors.append("architecture corpus drifted")
    evidence = []
    for case in cases:
        dimensions = case.get("dimensions", {})
        if tuple(dimensions.keys()) != DIMENSIONS:
            errors.append(f"{case.get('case_id')}: dimension order or coverage drifted")
        for name, finding in dimensions.items():
            if finding.get("disposition") not in allowed or not finding.get("finding"):
                errors.append(f"{case.get('case_id')}.{name}: invalid disposition or empty finding")
        for key in ("source_target_path", "provider_result_path"):
            path = ROOT / case[key]
            if not path.is_file():
                errors.append(f"missing evidence: {case[key]}")
            else:
                evidence.append({"path": case[key], "sha256": _sha(path)})
        for key in ("source_review_path", "provider_paired_call_path"):
            if key in case:
                path = ROOT / case[key]
                if not path.is_file():
                    errors.append(f"missing evidence: {case[key]}")
                else:
                    evidence.append({"path": case[key], "sha256": _sha(path)})
    decision = review.get("decision", {})
    if decision.get("selected_next_experiment") != "read_only_shadow_graph_impact":
        errors.append("next experiment decision drifted")
    if decision.get("production_integration_authorized") is not False or decision.get("new_provider_calls_authorized") is not False:
        errors.append("unsafe authorization in corpus decision")
    boundary = review.get("boundary", {})
    for key in ("provider_calls", "evaluator_calls", "embedding_calls", "graph_calls", "runtime_calls"):
        if boundary.get(key) != 0:
            errors.append(f"{key} must remain zero")
    if boundary.get("scalar_score_computed") is not False or boundary.get("weighted_aggregation_computed") is not False:
        errors.append("non-scalar boundary drifted")
    return {
        "schema_version": "lolla.reasoning_process_paired_corpus_validation.v1",
        "status": "provider_free_paired_corpus_validation_pass" if not errors else "provider_free_paired_corpus_validation_fail",
        "contract_path": _display(contract_path),
        "contract_sha256": _sha(contract_path),
        "review_path": _display(review_path),
        "review_sha256": _sha(review_path),
        "reviewed_case_count": len(cases),
        "dimension_count": len(DIMENSIONS),
        "evidence_manifest": evidence,
        "errors": errors,
        "boundary": {"provider_calls": 0, "evaluator_calls": 0, "embedding_calls": 0, "graph_calls": 0, "runtime_calls": 0, "scalar_score_computed": False, "production_integration_authorized": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(args.contract.resolve(), args.review.resolve())
    args.output.resolve().write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "reviewed_case_count": report["reviewed_case_count"], "dimension_count": report["dimension_count"], "errors": report["errors"]}, indent=2))
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
