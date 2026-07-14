#!/usr/bin/env python3
"""Finalize the provider-free semantic closeout for separated-surface A1."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from scripts.evals import seal_r4_separated_surface_execution_a1 as sealer


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-execution-2026-07-14-a1"
CONTRACT = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json"
RAW_CHECKPOINT = "9f1b308ca852b86d640e481a32bc6efc8f5320e9"


class R4SeparatedSurfaceFinalizeError(RuntimeError):
    """Raised when the execution closeout no longer reproduces."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SeparatedSurfaceFinalizeError(f"expected object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write(path: Path, value: Any) -> None:
    path.write_bytes(_render(value))


def _closeout() -> dict[str, Any]:
    result = _load(OUTPUT / "result.json")
    review = _load(OUTPUT / "source-first-review.json")
    return {
        "schema_version": "lolla.r4_separated_surface_execution_closeout.v1",
        "status": "closed_terminal_mechanical_failure",
        "decision": "semantic_result_not_evaluable",
        "decision_reason": review["decision_basis"],
        "run_id": result["run_id"],
        "canonical_start": "5bc8408341c11513a335977c9922d4971a78701b",
        "raw_execution_checkpoint": RAW_CHECKPOINT,
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": _sha(CONTRACT),
        "calls_attempted": 7,
        "calls_completed": 6,
        "call_ordinals": list(range(1, 8)),
        "failed_ordinal": 7,
        "unattempted_ordinals": [8, 9, 10, 11, 12],
        "failure_class": "terminal_status_failure",
        "failure_detail": result["call_results"][6]["failure_detail"],
        "finish_reason": "error",
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
        "failed_call_provider_reported_cost_available": False,
        "case_costs_usd": result["case_costs_usd"],
        "authorization_sha256": sealer.AUTHORIZATION_SHA256,
        "authorization_consumed": True,
        "authorization_artifact_exists": False,
        "current_provider_authorization": {"maximum_calls": 0, "maximum_cost_usd": 0.0},
        "second_execution_authorized": False,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "manual_replacement_calls": 0,
        "fallback_models": 0,
        "model_substitutions": 0,
        "response_healing": False,
        "relationship_calls": 0,
        "evaluator_calls": 0,
        "embedding_calls": 0,
        "graph_calls": 0,
        "pipeline_calls": 0,
        "runtime_calls": 0,
        "records_reviewed": review["record_count"],
        "paired_false_positive_records": review["paired_false_positive_records"],
        "separated_false_positive_records": review["separated_false_positive_records"],
        "positive_case_matched_comparison_completed": False,
        "companion_pressure_conclusion": review["companion_pressure_conclusion"],
        "evidence_published": False,
        "runtime_or_graph_integration": False,
        "product_usefulness_claim": False,
    }


def _manifest() -> dict[str, Any]:
    excluded = {"evidence-manifest.json"}
    records = []
    for path in sorted(p for p in OUTPUT.iterdir() if p.is_file() and p.name not in excluded):
        records.append({
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha(path),
            "bytes": len(path.read_bytes()),
        })
    return {
        "schema_version": "lolla.r4_separated_surface_execution_evidence_manifest.v1",
        "status": "execution_and_source_first_review_frozen",
        "decision": "semantic_result_not_evaluable",
        "files": records,
        "file_count": len(records),
        "raw_execution_checkpoint": RAW_CHECKPOINT,
        "provider_calls": 7,
        "provider_reported_cost_usd": 0.0105715,
        "evidence_published": False,
    }


def write() -> dict[str, Any]:
    sealer.validate()
    review = _load(OUTPUT / "source-first-review.json")
    if review.get("decision") != "semantic_result_not_evaluable" or review.get("record_count") != 9:
        raise R4SeparatedSurfaceFinalizeError("source-first review drifted")
    _write(OUTPUT / "execution-closeout.json", _closeout())
    _write(OUTPUT / "evidence-manifest.json", _manifest())
    return validate()


def validate() -> dict[str, Any]:
    sealer.validate()
    closeout = _load(OUTPUT / "execution-closeout.json")
    manifest = _load(OUTPUT / "evidence-manifest.json")
    if closeout != _closeout() or manifest != _manifest():
        raise R4SeparatedSurfaceFinalizeError("execution closeout drifted")
    return {
        "status": closeout["status"],
        "decision": closeout["decision"],
        "provider_calls": closeout["calls_attempted"],
        "provider_reported_cost_usd": closeout["provider_reported_cost_usd"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if args.write == args.validate_only:
        raise R4SeparatedSurfaceFinalizeError("choose exactly one mode")
    summary = write() if args.write else validate()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
