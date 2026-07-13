#!/usr/bin/env python3
"""Build a non-scalar V1 completion matrix from preserved evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12/manifest.json"
CALIBRATION_TERMINAL = ROOT / "research/simulated-reliability-v1-calibration-2026-07-12/a13/terminal-review.json"
CALIBRATION_ROOT = ROOT / "research/simulated-reliability-v1-calibration-2026-07-12"
TRANSFER_SEAL = ROOT / "research/simulated-reliability-v1-transfer-2026-07-12/t1/batch-seal.json"
DIAGNOSTIC_REVIEW = ROOT / "research/simulated-reliability-v1-review-2026-07-13/t1-diagnostic-source-review.json"
RECEIPT_INTEGRITY = ROOT / "research/simulated-reliability-v1-receipts-2026-07-13/t1/integrity-report.json"
RUNTIME_CONTRACT = ROOT / "docs/evals/simulated-reliability-v1-runtime-contract-v14-transfer.json"
REVIEW_CONTRACT = ROOT / "docs/evals/simulated-reliability-v1-review-contract-v1.json"
COLD_READER_CONTRACT = ROOT / "docs/evals/simulated-reliability-v1-cold-reader-contract-v1.json"
REPEAT_CONTRACT = ROOT / "docs/evals/simulated-reliability-v1-repeat-contract-v1.json"
CREDIT_CONTINUATION_CONTRACT = ROOT / "docs/evals/simulated-reliability-v1-credit-continuation-contract-v1.json"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def calibration_usage() -> dict[str, Any]:
    artifacts = sorted(CALIBRATION_ROOT.rglob("call-*-result.json"))
    statuses: dict[str, int] = {}
    cost = 0.0
    for path in artifacts:
        row = load(path)
        status = str(row.get("operational_status", "missing"))
        statuses[status] = statuses.get(status, 0) + 1
        cost += float(row.get("provider_reported_cost_usd") or 0)
    return {
        "attempted_calls": len(artifacts),
        "operationally_ok": statuses.get("ok", 0),
        "status_counts": statuses,
        "provider_reported_cost_usd": round(cost, 12),
    }


def requirement(
    requirement_id: str,
    status: str,
    finding: str,
    evidence: list[str],
    remaining: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "status": status,
        "finding": finding,
        "evidence": evidence,
        "remaining": remaining or [],
    }


def build() -> dict[str, Any]:
    corpus = load(CORPUS)
    calibration = load(CALIBRATION_TERMINAL)
    transfer = load(TRANSFER_SEAL)
    diagnostic = load(DIAGNOSTIC_REVIEW)
    integrity = load(RECEIPT_INTEGRITY)
    review_contract = load(REVIEW_CONTRACT)
    cold_reader = load(COLD_READER_CONTRACT)
    repeat = load(REPEAT_CONTRACT)
    continuation = load(CREDIT_CONTINUATION_CONTRACT)
    calibration_calls = calibration_usage()

    total_attempts = calibration_calls["attempted_calls"] + transfer["provider_attempts"]
    total_ok = calibration_calls["operationally_ok"] + transfer["successful_provider_calls"]
    total_cost = round(
        calibration_calls["provider_reported_cost_usd"]
        + transfer["provider_reported_cost_usd"],
        12,
    )
    reviewed = len(diagnostic["cases"])
    complete = transfer["complete_cases"]
    if reviewed != complete:
        raise ValueError("diagnostic review must cover every complete transfer case")
    if integrity["receipt_count"] != transfer["attempted_cases"]:
        raise ValueError("receipt integrity must cover every attempted transfer case")

    requirements = [
        requirement(
            "naturalized_balanced_corpus",
            "supported",
            "The frozen corpus contains 20 simulated cases, including 12 naturalized transfer cases with 24 messages each and all three prospective public-behavior strata.",
            [str(CORPUS.relative_to(ROOT))],
        ),
        requirement(
            "bounded_hybrid_pipeline",
            "supported_as_mechanism",
            "Calibration exercised probabilistic role/mechanism interpretation, deterministic canonical recall and graph expansion, and fresh apply/reject/park reconsideration without semantic deterministic gating.",
            [str(CALIBRATION_TERMINAL.relative_to(ROOT))],
        ),
        requirement(
            "prospective_runtime_and_review_freeze",
            "partial",
            "Runtime, model, provider, prompts, schemas, graph policy, and transfer sources were frozen before T1. The exact comparative review contract was frozen only after T1 execution began.",
            [str(RUNTIME_CONTRACT.relative_to(ROOT)), str(REVIEW_CONTRACT.relative_to(ROOT))],
            ["T1 cannot support a clean prospectively blinded causal usefulness claim."],
        ),
        requirement(
            "untouched_transfer_execution",
            "partial",
            f"All {transfer['attempted_cases']} cases were attempted without tuning; {complete} completed, one failed the role join, and four stopped on HTTP 402 before inference.",
            [str(TRANSFER_SEAL.relative_to(ROOT))],
            [
                "Complete cases 09-12 under the frozen, separately identified credit-continuation contract or close V1 explicitly incomplete.",
                f"The continuation currently authorizes {continuation['activation_prerequisites']['provider_calls_currently_authorized']} calls.",
            ],
        ),
        requirement(
            "usefulness",
            "not_established",
            "No transfer pressure arm ran. Transcript-only outputs mostly added structured restatement, not a unique reasoning contribution. Synthetic calibration pressure cannot establish genuine user usefulness.",
            [str(DIAGNOSTIC_REVIEW.relative_to(ROOT)), str(CALIBRATION_TERMINAL.relative_to(ROOT))],
            ["Prospective blind review of pressure-bearing transfer outputs and human calibration."],
        ),
        requirement(
            "restraint",
            "mixed",
            f"Source-first diagnosis found {diagnostic['cross_case_findings']['correct_stand_downs']} correct stand-downs and {diagnostic['cross_case_findings']['false_stand_downs']} false stand-downs. Calibration also found graph output noisier, more verbose, and more directive than direct pressure.",
            [str(DIAGNOSTIC_REVIEW.relative_to(ROOT)), str(CALIBRATION_TERMINAL.relative_to(ROOT))],
            ["Improve residual-challenge representation without replacing probabilistic interpretation with brittle gates."],
        ),
        requirement(
            "graph_attribution",
            "calibration_only",
            "Deterministic direct and graph candidate custody is inspectable, but graph marginal value was not observed in transfer because every complete case stood down.",
            [str(CALIBRATION_TERMINAL.relative_to(ROOT)), str(DIAGNOSTIC_REVIEW.relative_to(ROOT))],
            ["A pressure-bearing untouched case reviewed under the prospective comparison contract."],
        ),
        requirement(
            "integrity",
            "supported",
            f"All {integrity['receipt_count']} receipts pass source, contract, call-artifact, usage, failure, and Markdown self-containment checks with zero healing, retries, or fallback models.",
            [str(RECEIPT_INTEGRITY.relative_to(ROOT))],
        ),
        requirement(
            "stability",
            "not_yet_measured",
            "Calibration showed sensitivity on the same source and supplied seed, but it was not a clean frozen repeat. V14 failed to name the planned cross-stratum repeat subset. A bounded post-T1 repair contract is now frozen but authorizes zero calls.",
            [str(CALIBRATION_TERMINAL.relative_to(ROOT)), str(REPEAT_CONTRACT.relative_to(ROOT))],
            ["Complete the selected primary park case and run repeat_2 only after the founder cost decision."],
        ),
        requirement(
            "operability",
            "partial",
            f"Across calibration and transfer, {total_ok}/{total_attempts} call artifacts were operationally ok at ${total_cost:.7f}. Case-level transfer completion was {complete}/{transfer['attempted_cases']}; one semantic join and four credit failures prevent a reliability claim.",
            [str(CALIBRATION_TERMINAL.relative_to(ROOT)), str(TRANSFER_SEAL.relative_to(ROOT))],
            ["Separate model capability, local admission, and funding-envelope failures in any production SLO."],
        ),
        requirement(
            "receipt_construction",
            "supported",
            "Every attempted case has a self-contained JSON and Markdown receipt, including terminal failures and explicit non-claims.",
            [str(RECEIPT_INTEGRITY.relative_to(ROOT))],
        ),
        requirement(
            "receipt_reconstruction",
            "not_yet_measured",
            "Receipt bytes and orientation are validated, but no fresh agent or human has reconstructed a V1 receipt under the frozen cold-reader contract.",
            [str(COLD_READER_CONTRACT.relative_to(ROOT)), str(RECEIPT_INTEGRITY.relative_to(ROOT))],
            ["Run fresh-agent review and founder/human review independently on the four-case representative sample."],
        ),
        requirement(
            "non_scalar_evaluation",
            "supported",
            "The transfer review, receipt integrity report, repeat contract, and cold-reader contract all forbid a composite quality, stability, proof-of-work, or trust score.",
            [
                str(REVIEW_CONTRACT.relative_to(ROOT)),
                str(RECEIPT_INTEGRITY.relative_to(ROOT)),
                str(REPEAT_CONTRACT.relative_to(ROOT)),
                str(COLD_READER_CONTRACT.relative_to(ROOT)),
            ],
        ),
    ]

    return {
        "schema_version": "lolla.simulated_reliability_v1_evidence_matrix.v1",
        "status": "v1_incomplete_evidence_matrix_current",
        "date": "2026-07-13",
        "claim_boundary": "This matrix reports what current artifacts support, contradict, or leave untested. It is not a scalar score, product authorization, or decision-quality certificate.",
        "evidence_locks": [
            {"path": str(path.relative_to(ROOT)), "sha256": digest(path)}
            for path in (
                CORPUS,
                CALIBRATION_TERMINAL,
                RUNTIME_CONTRACT,
                TRANSFER_SEAL,
                REVIEW_CONTRACT,
                DIAGNOSTIC_REVIEW,
                RECEIPT_INTEGRITY,
                COLD_READER_CONTRACT,
                REPEAT_CONTRACT,
                CREDIT_CONTINUATION_CONTRACT,
            )
        ],
        "usage": {
            "calibration": calibration_calls,
            "transfer": {
                "attempted_calls": transfer["provider_attempts"],
                "operationally_ok": transfer["successful_provider_calls"],
                "provider_reported_cost_usd": transfer["provider_reported_cost_usd"],
            },
            "total": {
                "attempted_calls": total_attempts,
                "operationally_ok": total_ok,
                "provider_reported_cost_usd": total_cost,
            },
        },
        "requirements": requirements,
        "constitutional_read": {
            "probabilistic_semantic_interpretation": "preserved",
            "deterministic_identity_graph_bounds_and_custody": "preserved",
            "deterministic_semantic_gating": "not_introduced",
            "pressure_as_hypothesis": "preserved_in_calibration",
            "freedom_of_conclusion": "preserved_in_calibration",
            "unknown_unknown_as_question": "not_reliably_represented_in_transfer",
            "receipt_as_process_not_wisdom": "preserved",
            "human_decision_authority": "preserved_in_all_seven_reviewed_cases",
        },
        "current_decision": {
            "v1_reliability_evaluation_complete": False,
            "runtime_integration_authorized": False,
            "production_model_selected": False,
            "gemini_3_5_flash_production_default_justified": False,
            "provider_free_v2_representation_design_supported": True,
            "additional_provider_calls_authorized": 0,
        },
        "missing_for_final_v1_reassessment": [
            "founder decision on identical paid continuation versus explicit incomplete closure",
            "pressure and park transfer coverage, currently absent from completed T1",
            "bounded repeat execution for stability",
            "prospective blind review of any new complete or repeat outputs",
            "fresh-agent receipt reconstruction",
            "human receipt usefulness review",
        ],
        "single_quality_score": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = build()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
