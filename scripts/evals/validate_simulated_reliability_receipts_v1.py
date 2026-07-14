#!/usr/bin/env python3
"""Validate V1 receipt custody without claiming cold-reader comprehension."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


class ReceiptValidationError(ValueError):
    pass


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha_bytes(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha_without(value: dict[str, Any], field: str) -> str:
    copy = dict(value)
    copy.pop(field, None)
    encoded = json.dumps(copy, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_one(receipt_path: Path, markdown_path: Path) -> dict[str, Any]:
    receipt = load(receipt_path)
    checks: dict[str, bool] = {}
    checks["schema"] = receipt.get("schema_version") == "lolla.simulated_reliability_case_receipt.v1"
    checks["receipt_hash"] = receipt.get("receipt_sha256") == canonical_sha_without(receipt, "receipt_sha256")

    source = ROOT / receipt["source"]["path"]
    checks["source_exists"] = source.exists()
    checks["source_hash"] = checks["source_exists"] and sha_bytes(source) == receipt["source"]["sha256"]
    checks["source_text_exact"] = checks["source_exists"] and source.read_text(encoding="utf-8") == receipt["source"]["authoritative_conversation"]

    contract = ROOT / receipt["runtime_contract"]["path"]
    checks["contract_hash"] = contract.exists() and sha_bytes(contract) == receipt["runtime_contract"]["sha256"]

    call_checks = []
    for call in receipt["call_custody"]:
        path = ROOT / call["artifact_path"]
        call_checks.append(path.exists() and sha_bytes(path) == call["artifact_sha256"])
    checks["call_artifact_hashes"] = all(call_checks)

    attempts = sum(int(call["provider_calls"] or 0) for call in receipt["call_custody"])
    successes = sum(call["operational_status"] == "ok" for call in receipt["call_custody"])
    cost = round(sum(float(call["provider_reported_cost_usd"] or 0) for call in receipt["call_custody"]), 12)
    checks["usage_attempts"] = attempts == receipt["usage"]["provider_attempts"]
    checks["usage_successes"] = successes == receipt["usage"]["successful_calls"]
    checks["usage_cost"] = cost == receipt["usage"]["provider_reported_cost_usd"]
    checks["no_hidden_repair"] = (
        receipt["usage"]["automatic_retries"] == 0
        and receipt["usage"]["response_healing"] is False
        and receipt["usage"]["fallback_models"] == 0
    )

    status = receipt["attempt_status"]
    if status == "transfer_case_execution_complete_source_review_required":
        checks["complete_role_custody"] = receipt["interpretation"]["joined_role_records"] is not None
        checks["complete_mechanism_custody"] = len(receipt["interpretation"]["mechanism_assessments"]) == 9
        checks["complete_arm_custody"] = set(receipt["public_arms"]) == {
            "transcript_only",
            "direct_pressure",
            "graph_expanded_pressure",
        }
        checks["failure_custody"] = receipt["failures"] == []
    else:
        checks["complete_role_custody"] = True
        checks["complete_mechanism_custody"] = True
        checks["complete_arm_custody"] = True
        checks["failure_custody"] = bool(receipt["failures"])

    markdown_text = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else ""
    checks["markdown_exists"] = bool(markdown_text)
    checks["markdown_contains_source"] = receipt["source"]["authoritative_conversation"] in markdown_text
    checks["markdown_orientation"] = all(
        heading in markdown_text
        for heading in (
            "## How to read this receipt",
            "## Probabilistic interpretation",
            "## Deterministic pressure custody",
            "## Public arms",
            "## Failures",
            "## Usage",
            "## Non-claims",
        )
    )
    checks["no_badge_claim"] = "proof of work score" not in markdown_text.lower() and "trust score" not in markdown_text.lower()
    passed = all(checks.values())
    return {
        "case_id": receipt["case_id"],
        "attempt_status": status,
        "status": "integrity_pass" if passed else "integrity_fail",
        "checks": checks,
        "receipt_path": str(receipt_path.relative_to(ROOT)),
        "markdown_path": str(markdown_path.relative_to(ROOT)),
        "cold_reader_comprehension_tested": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipts-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.receipts_root.resolve()
    output = args.output.resolve()
    rows = [
        validate_one(path, path.with_suffix(".md"))
        for path in sorted(root.glob("*/receipt.json"))
    ]
    if not rows:
        raise ReceiptValidationError("no receipts found")
    report = {
        "schema_version": "lolla.simulated_reliability_receipt_integrity_report.v1",
        "status": "integrity_pass" if all(row["status"] == "integrity_pass" for row in rows) else "integrity_fail",
        "receipt_count": len(rows),
        "integrity_pass_count": sum(row["status"] == "integrity_pass" for row in rows),
        "cases": rows,
        "tested": [
            "source custody",
            "runtime-contract custody",
            "call-artifact custody",
            "usage reconciliation",
            "stage and failure preservation",
            "Markdown self-containment",
            "orientation and non-claim presence",
        ],
        "not_tested": [
            "fresh human comprehension",
            "independent semantic accuracy",
            "reasoning quality",
            "decision correctness",
            "user trust calibration",
        ],
        "single_quality_score": None,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "integrity_pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
