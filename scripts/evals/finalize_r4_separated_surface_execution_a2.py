#!/usr/bin/env python3
"""Finalize the provider-free semantic closeout for separated-surface A2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from scripts.evals import seal_r4_separated_surface_execution_a2 as sealer


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-execution-2026-07-14-a2"
CONTRACT = ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json"
RAW_CHECKPOINT = "407109cd64be31c92efa31a76362091b2c5943a9"
DECISION = "separated_tasks_ineffective_companions_persist"


class R4SeparatedSurfaceA2FinalizeError(RuntimeError):
    """Raised when the final A2 evidence package no longer reproduces."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SeparatedSurfaceA2FinalizeError(f"expected object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write(path: Path, value: Any) -> None:
    path.write_bytes(_render(value))


def _validate_review() -> dict[str, Any]:
    review = _load(OUTPUT / "source-first-review.json")
    verdicts = review.get("record_verdicts")
    if (
        review.get("status") != "complete_source_first_review"
        or review.get("decision") != DECISION
        or review.get("record_count") != 18
        or review.get("supported_record_count") != 4
        or review.get("false_positive_record_count") != 14
        or review.get("paired_false_positive_records") != 7
        or review.get("separated_false_positive_records") != 7
        or review.get("correct_zero_reviews") != [2, 4]
        or review.get("positive_case_findings_preserved") is not True
        or review.get("paired_positive_companions") != [8, 10]
        or review.get("separated_positive_companions") != [7, 12]
        or review.get("scalar_score") is not None
        or review.get("provider_evaluator_calls") != 0
        or not isinstance(verdicts, list)
        or len(verdicts) != 18
    ):
        raise R4SeparatedSurfaceA2FinalizeError("source-first review drifted")
    supported = [row for row in verdicts if str(row.get("verdict", "")).startswith("supported")]
    false_positives = [row for row in verdicts if str(row.get("verdict", "")).startswith("false_positive")]
    if len(supported) != 4 or len(false_positives) != 14:
        raise R4SeparatedSurfaceA2FinalizeError("record verdict inventory drifted")
    return review


def _closeout() -> dict[str, Any]:
    result = _load(OUTPUT / "result.json")
    review = _validate_review()
    return {
        "schema_version": "lolla.r4_separated_surface_execution_closeout.v1",
        "status": "closed_complete_final_execution",
        "decision": DECISION,
        "decision_reason": review["decision_basis"],
        "run_id": result["run_id"],
        "authorization_instance": sealer.AUTHORIZATION_INSTANCE,
        "canonical_start": sealer.CANONICAL_BASE,
        "raw_execution_checkpoint": RAW_CHECKPOINT,
        "contract_path": str(CONTRACT.relative_to(ROOT)),
        "contract_sha256": _sha(CONTRACT),
        "calls_attempted": 12,
        "calls_completed": 12,
        "call_ordinals": list(range(1, 13)),
        "failed_ordinal": None,
        "unattempted_ordinals": [],
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
        "case_costs_usd": result["case_costs_usd"],
        "authorization_sha256": sealer.AUTHORIZATION_SHA256,
        "authorization_consumed": True,
        "authorization_artifact_exists": False,
        "current_provider_authorization": {"maximum_calls": 0, "maximum_cost_usd": 0.0},
        "third_execution_authorized": False,
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
        "records_reviewed": 18,
        "supported_records": 4,
        "false_positive_records": 14,
        "paired_false_positive_records": 7,
        "separated_false_positive_records": 7,
        "correct_zero_reviews": [2, 4],
        "positive_case_findings_preserved": True,
        "positive_case_companions_suppressed_by_separation": False,
        "a1_and_a2_combined_as_one_sample": False,
        "no_further_r4_provider_run_authorized": True,
        "evidence_published": False,
        "runtime_or_graph_integration": False,
        "product_usefulness_claim": False,
    }


def _manifest() -> dict[str, Any]:
    excluded = {"evidence-manifest.json"}
    records = [
        {
            "path": str(path.relative_to(ROOT)),
            "sha256": _sha(path),
            "bytes": len(path.read_bytes()),
        }
        for path in sorted(p for p in OUTPUT.iterdir() if p.is_file() and p.name not in excluded)
    ]
    return {
        "schema_version": "lolla.r4_separated_surface_execution_evidence_manifest.v1",
        "status": "execution_and_source_first_review_frozen",
        "decision": DECISION,
        "files": records,
        "file_count": len(records),
        "raw_execution_checkpoint": RAW_CHECKPOINT,
        "provider_calls": 12,
        "provider_reported_cost_usd": 0.02148425,
        "authorization_consumed": True,
        "no_further_r4_provider_run_authorized": True,
        "evidence_published": False,
    }


def write() -> dict[str, Any]:
    sealer.validate()
    _validate_review()
    _write(OUTPUT / "execution-closeout.json", _closeout())
    _write(OUTPUT / "evidence-manifest.json", _manifest())
    return validate()


def validate() -> dict[str, Any]:
    sealer.validate()
    _validate_review()
    closeout = _load(OUTPUT / "execution-closeout.json")
    manifest = _load(OUTPUT / "evidence-manifest.json")
    if closeout != _closeout() or manifest != _manifest():
        raise R4SeparatedSurfaceA2FinalizeError("execution closeout drifted")
    for row in manifest["files"]:
        path = ROOT / row["path"]
        if not path.is_file() or _sha(path) != row["sha256"] or len(path.read_bytes()) != row["bytes"]:
            raise R4SeparatedSurfaceA2FinalizeError("evidence artifact drifted")
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
        raise R4SeparatedSurfaceA2FinalizeError("choose exactly one mode")
    summary = write() if args.write else validate()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
