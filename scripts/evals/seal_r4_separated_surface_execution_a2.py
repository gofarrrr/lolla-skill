#!/usr/bin/env python3
"""Seal the complete raw R4 separated-surface A2 execution provider-free."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Sequence

from scripts.evals import run_r4_separated_surface_experiment as runner


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "research/lolla-r4-separated-surface-experiment-v1-execution-2026-07-14-a2"
AUTHORIZATION_SHA256 = "e41321fec40af572ae643af73cb6a04a7624756d84c723b0c09bcb2829450edf"
CANONICAL_BASE = "f940f46e93b34608be291eeaebc56a4357ac7d36"
AUTHORIZATION_INSTANCE = "lolla-r4-separated-surface-experiment-v1-a2"


class R4SeparatedSurfaceA2SealError(RuntimeError):
    """Raised when immutable A2 raw execution custody does not reproduce."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SeparatedSurfaceA2SealError(f"expected object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write(path: Path, value: Any) -> None:
    path.write_bytes(_render(value))


def _git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def _canonical_base_is_ancestor() -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", CANONICAL_BASE, _git_head()],
        cwd=ROOT,
        check=False,
        capture_output=True,
    ).returncode == 0


def _validate_complete_result() -> dict[str, Any]:
    contract = runner.validate_contract()
    result = _load(OUTPUT / "result.json")
    rows = result.get("call_results")
    if (
        not _canonical_base_is_ancestor()
        or result.get("status") != "complete"
        or result.get("provider_calls") != 12
        or result.get("call_ordinals") != list(range(1, 13))
        or not isinstance(rows, list)
        or len(rows) != 12
        or any(row.get("operational_status") != "completed" for row in rows)
        or any(row.get("finish_reason") != "stop" for row in rows)
        or result.get("first_failure_stopped_further_transport") is not False
        or result.get("provider_reported_cost_usd", 1.0) > 0.3
    ):
        raise R4SeparatedSurfaceA2SealError("complete A2 execution state drifted")
    if set(result.get("case_costs_usd", {})) != {case["case_id"] for case in contract["cases"]}:
        raise R4SeparatedSurfaceA2SealError("case cost inventory drifted")
    if any(cost > 0.075 for cost in result["case_costs_usd"].values()):
        raise R4SeparatedSurfaceA2SealError("per-case cost ceiling drifted")
    for row, plan in zip(rows, contract["call_plan"], strict=True):
        if (
            row.get("ordinal") != plan["ordinal"]
            or row.get("request_body_sha256") != plan["request_body_sha256"]
            or row.get("served_model") not in contract["operator"]["allowed_served_model_ids"]
            or row.get("served_provider") not in contract["operator"]["allowed_served_provider_names"]
            or not row.get("generation_id")
            or row.get("first_terminal_provider_result_preserved_exactly") is not True
            or row.get("reasoning_custody", {}).get("exclusion_satisfied") is not True
        ):
            raise R4SeparatedSurfaceA2SealError("call custody drifted")
        raw = OUTPUT / str(row["raw_response_path"])
        if not raw.is_file() or _sha(raw) != row["raw_response_sha256"] or len(raw.read_bytes()) != row["raw_response_utf8_bytes"]:
            raise R4SeparatedSurfaceA2SealError("raw response drifted")
    return result


def _expected_consumption(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "lolla.r4_separated_surface_authorization_consumption.v1",
        "status": "consumed_complete_final_execution",
        "run_id": result["run_id"],
        "authorization_instance": AUTHORIZATION_INSTANCE,
        "founder_authorization_type": "new final full-execution authorization",
        "canonical_starting_commit": CANONICAL_BASE,
        "authorization_sha256": AUTHORIZATION_SHA256,
        "identical_machine_permissions_to_a1": True,
        "previous_a1_authorization": "consumed_and_not_reusable",
        "a2_authorization": "separately_issued_one_use_final_permitted_execution",
        "authorization_artifact_committed": False,
        "authorization_artifact_removed_before_raw_commit": True,
        "provider_calls": 12,
        "completed_calls": 12,
        "failed_ordinal": None,
        "unattempted_ordinals": [],
        "third_execution_authorized": False,
        "automatic_retries": 0,
        "semantic_retries": 0,
        "manual_replacement_calls": 0,
        "fallback_models": 0,
        "model_substitutions": 0,
        "response_healing": False,
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
    }


def _expected_closeout(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "lolla.r4_separated_surface_raw_execution_closeout.v1",
        "status": "raw_execution_sealed_before_protected_review",
        "canonical_base": CANONICAL_BASE,
        "authorization_instance": AUTHORIZATION_INSTANCE,
        "run_id": result["run_id"],
        "calls_attempted": 12,
        "calls_completed": 12,
        "call_ordinals": list(range(1, 13)),
        "failed_ordinal": None,
        "unattempted_ordinals": [],
        "no_retry_or_replacement": True,
        "all_raw_terminal_responses_preserved": True,
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
        "case_costs_usd": result["case_costs_usd"],
        "authorization_consumed": True,
        "no_further_r4_provider_run_authorized": True,
        "protected_semantic_evidence_opened_before_seal": False,
        "a1_evidence_used_as_a2_call_substitute": False,
        "provider_calls_outside_runner": 0,
        "provider_key_printed_or_committed": False,
    }


def _build_manifest(result: dict[str, Any]) -> dict[str, Any]:
    excluded = {"raw-evidence-manifest.json"}
    records = [
        {"path": path.name, "sha256": _sha(path), "bytes": len(path.read_bytes())}
        for path in sorted(p for p in OUTPUT.iterdir() if p.is_file() and p.name not in excluded)
    ]
    return {
        "schema_version": "lolla.r4_separated_surface_raw_evidence_manifest.v1",
        "status": "raw_evidence_frozen_before_protected_review",
        "run_id": result["run_id"],
        "authorization_instance": AUTHORIZATION_INSTANCE,
        "files": records,
        "file_count": len(records),
        "provider_calls": 12,
        "completed_calls": 12,
        "failed_ordinal": None,
        "unattempted_ordinals": [],
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
        "authorization_sha256": AUTHORIZATION_SHA256,
        "protected_semantic_evidence_included": False,
        "a1_evidence_included": False,
    }


def write(authorization: Path) -> dict[str, Any]:
    result = _validate_complete_result()
    runner.validate_authorization(authorization, contract=runner.validate_contract())
    if _sha(authorization) != AUTHORIZATION_SHA256:
        raise R4SeparatedSurfaceA2SealError("authorization byte hash drifted")
    _write(OUTPUT / "authorization-consumption.json", _expected_consumption(result))
    _write(OUTPUT / "raw-execution-closeout.json", _expected_closeout(result))
    _write(OUTPUT / "raw-evidence-manifest.json", _build_manifest(result))
    return validate()


def validate() -> dict[str, Any]:
    result = _validate_complete_result()
    consumption = _load(OUTPUT / "authorization-consumption.json")
    closeout = _load(OUTPUT / "raw-execution-closeout.json")
    manifest = _load(OUTPUT / "raw-evidence-manifest.json")
    if consumption != _expected_consumption(result) or closeout != _expected_closeout(result):
        raise R4SeparatedSurfaceA2SealError("raw closeout drifted")
    expected = {
        "status": "raw_evidence_frozen_before_protected_review",
        "authorization_instance": AUTHORIZATION_INSTANCE,
        "provider_calls": 12,
        "completed_calls": 12,
        "failed_ordinal": None,
        "unattempted_ordinals": [],
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
        "authorization_sha256": AUTHORIZATION_SHA256,
        "protected_semantic_evidence_included": False,
        "a1_evidence_included": False,
    }
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise R4SeparatedSurfaceA2SealError("raw evidence manifest custody drifted")
    if manifest.get("file_count") != len(manifest.get("files", [])):
        raise R4SeparatedSurfaceA2SealError("raw evidence manifest count drifted")
    for row in manifest["files"]:
        artifact = OUTPUT / row["path"]
        if not artifact.is_file() or _sha(artifact) != row["sha256"] or len(artifact.read_bytes()) != row["bytes"]:
            raise R4SeparatedSurfaceA2SealError("raw evidence artifact drifted")
    return {
        "status": "raw_execution_sealed_before_protected_review",
        "provider_calls": 12,
        "completed_calls": 12,
        "failed_ordinal": None,
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if args.write == args.validate_only:
        raise R4SeparatedSurfaceA2SealError("choose exactly one mode")
    if args.write:
        if args.authorization is None:
            raise R4SeparatedSurfaceA2SealError("write requires authorization")
        summary = write(args.authorization)
    else:
        summary = validate()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
