#!/usr/bin/env python3
"""Seal and source-review the corrected R4 complementary-reader execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals.run_r4_complementary_reader_token_correction import (
    validate_authorization,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/evals/lolla-r4-complementary-reader-token-correction-contract-v1.json"
AUTHORIZATION = ROOT / "docs/evals/lolla-r4-complementary-reader-token-correction-authorization-a2.json"
TARGET = ROOT / "docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json"
OUTPUT = ROOT / "research/lolla-r4-complementary-reader-token-correction-execution-2026-07-14-a2"
RUN_RESULT = OUTPUT / "result.json"
MANIFEST = OUTPUT / "evidence-manifest.json"
SOURCE_REVIEW = OUTPUT / "source-first-review.json"
CLOSEOUT = OUTPUT / "execution-closeout.json"

MODEL = "google/gemini-3.1-flash-lite"
PROVIDER = "Google"
EXPECTED_CALLS = (
    {
        "case_id": "v1-case02-discharge-transport",
        "ordinal": 1,
        "task": "uncertainty",
        "cost": 0.0036835,
        "completion_tokens": 416,
        "prompt_tokens": 12238,
        "max_output_tokens": 1600,
        "request_body_sha256": "d432643c8c0fed6a6e4c4203b43810dfc2f4c461fdf74beefbb2eba5666167ac",
        "raw_content_sha256": "68f0db1abb884280fb3d8c93e6d73d9dd2a8b2677013b25d4b4bd736dcccf904",
    },
    {
        "case_id": "v1-case02-discharge-transport",
        "ordinal": 2,
        "task": "relationship",
        "cost": 0.001651,
        "completion_tokens": 391,
        "prompt_tokens": 4258,
        "max_output_tokens": 700,
        "request_body_sha256": "7b15f13523b0a7dbca96899584de46cf8331e7cd5f990fee8a7e6e74363389c2",
        "raw_content_sha256": "f9ac50576be21a29967907e1f5065ad474acd7cff06753b8a531c2d7ec31daee",
    },
    {
        "case_id": "v1-case03-executive-hire",
        "ordinal": 3,
        "task": "uncertainty",
        "cost": 0.003977,
        "completion_tokens": 438,
        "prompt_tokens": 13280,
        "max_output_tokens": 1600,
        "request_body_sha256": "a3d85785c98b730b5c5261ce7711a7a83739c8e70ee9fc7262dd1ad52c678e59",
        "raw_content_sha256": "b0472a3ed02547937ba47328305ca4dbffbb130fe43dd4516d7753c5181d324f",
    },
    {
        "case_id": "v1-case03-executive-hire",
        "ordinal": 4,
        "task": "relationship",
        "cost": 0.0015235,
        "completion_tokens": 309,
        "prompt_tokens": 4240,
        "max_output_tokens": 700,
        "request_body_sha256": "a461c09631a93a47f1691728ca0c8d886364b03105be79b780cf406e11654c6b",
        "raw_content_sha256": "a8558626728df9c8dbaa212b30037fc70da7940617d9d4c56a3fe4721f350e6b",
    },
)

EXPECTED_RECORD_IDS = {
    "v1-case02-discharge-transport": {
        "uncertainty": [
            "r4u-v1-case02-discharge-transport-unresolved_matter-01-9d45dc6b2204",
            "r4u-v1-case02-discharge-transport-reopen_condition-01-dea75ee8962a",
            "r4u-v1-case02-discharge-transport-reopen_condition-02-5f7cb38ebde9",
        ],
        "relationship": [
            "r4x-v1-case02-discharge-transport-01-ce6968b05151",
            "r4x-v1-case02-discharge-transport-02-ace9d1ab4ef9",
        ],
    },
    "v1-case03-executive-hire": {
        "uncertainty": [
            "r4u-v1-case03-executive-hire-unresolved_matter-01-2e69d587ce79",
            "r4u-v1-case03-executive-hire-reopen_condition-01-c30441abb93b",
            "r4u-v1-case03-executive-hire-reopen_condition-02-df5f4c24a2c4",
        ],
        "relationship": [
            "r4x-v1-case03-executive-hire-01-b85d67f8a9bf",
            "r4x-v1-case03-executive-hire-02-8ead6c68fa40",
        ],
    },
}


class R4TokenCorrectionCloseoutError(RuntimeError):
    """Raised when execution evidence or its locked review drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4TokenCorrectionCloseoutError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_render(value))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _record_ids(case_id: str, task: str) -> list[str]:
    value = _load(OUTPUT / case_id / f"{task}-compiled.json")
    if task == "uncertainty":
        rows = [
            record
            for reader in value.get("reader_results", [])
            for record in reader.get("records", [])
        ]
    else:
        rows = value.get("reader_result", {}).get("records", [])
    return [str(row.get("record_id")) for row in rows]


def _call_observation(expected: Mapping[str, Any]) -> dict[str, Any]:
    case_id = str(expected["case_id"])
    task = str(expected["task"])
    ordinal = int(expected["ordinal"])
    case_dir = OUTPUT / case_id
    started = _load(case_dir / f"call-{ordinal:02d}-{task}-started.json")
    result = _load(case_dir / f"call-{ordinal:02d}-{task}-result.json")
    usage = result.get("usage")
    if not isinstance(usage, Mapping):
        raise R4TokenCorrectionCloseoutError(f"usage missing: {case_id}/{task}")
    details = usage.get("completion_tokens_details")
    raw_content = result.get("raw_content")
    candidate = result.get("candidate")
    if not isinstance(details, Mapping) or not isinstance(raw_content, str):
        raise R4TokenCorrectionCloseoutError(f"call payload incomplete: {case_id}/{task}")
    if not isinstance(candidate, Mapping):
        raise R4TokenCorrectionCloseoutError(f"candidate missing: {case_id}/{task}")
    if (
        started.get("status") != "started_before_network_transport"
        or result.get("operational_status") != "candidate_parsed"
        or result.get("provider_calls") != 1
        or result.get("served_model") != MODEL
        or result.get("served_provider") != PROVIDER
        or result.get("operator_attribution_ok") is not True
        or result.get("finish_reason") != "stop"
        or result.get("parse_error") != ""
        or result.get("reasoning_effort") != "minimal"
        or result.get("reasoning_content_excluded") is not True
        or result.get("reasoning_content_returned") is not True
        or result.get("max_output_tokens") != expected["max_output_tokens"]
        or result.get("provider_reported_cost_usd") != expected["cost"]
        or usage.get("cost") != expected["cost"]
        or usage.get("completion_tokens") != expected["completion_tokens"]
        or usage.get("prompt_tokens") != expected["prompt_tokens"]
        or details.get("reasoning_tokens") != 0
        or result.get("request_body_sha256") != expected["request_body_sha256"]
        or started.get("request_body_sha256") != expected["request_body_sha256"]
        or result.get("raw_content_sha256") != expected["raw_content_sha256"]
        or hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
        != expected["raw_content_sha256"]
        or value_sha256(candidate)
        != value_sha256(_load(case_dir / f"{task}-candidate.json"))
    ):
        raise R4TokenCorrectionCloseoutError(f"frozen call evidence drifted: {case_id}/{task}")
    return {
        "case_id": case_id,
        "call_ordinal": ordinal,
        "task": task,
        "requested_and_served_model": MODEL,
        "served_provider": PROVIDER,
        "operator_attribution_ok": True,
        "finish_reason": "stop",
        "operational_status": "candidate_parsed",
        "candidate_admitted": True,
        "completion_tokens": expected["completion_tokens"],
        "reasoning_tokens": 0,
        "reasoning_content_exclusion_requested": True,
        "runner_broad_reasoning_field_presence_flag": True,
        "reasoning_field_contents_preserved": False,
        "prompt_tokens": expected["prompt_tokens"],
        "provider_reported_cost_usd": expected["cost"],
        "request_body_sha256": expected["request_body_sha256"],
        "raw_content_sha256": expected["raw_content_sha256"],
    }


def _source_review(manifest_sha256: str) -> dict[str, Any]:
    case_reviews = [
        {
            "case_id": "v1-case02-discharge-transport",
            "selection_role": "exposed_false_stand_down_target",
            "verdict": "narrow_material_recovery_with_overgeneration",
            "record_reviews": [
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case02-discharge-transport"]["uncertainty"][0],
                    "verdict": "false_positive_already_operationalized_precondition",
                    "why": "The signed subcontractor amendment is already an explicit condition of the current position, not a distinct unresolved reasoning matter.",
                    "decisive_aliases": ["e068", "e071", "e095"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case02-discharge-transport"]["uncertainty"][1],
                    "verdict": "material_target_pressure_recovered",
                    "why": "The record preserves the temporary-support and hidden steady-state labor problem, one of the two alternatives required by the frozen material-recovery criterion.",
                    "decisive_aliases": ["e085", "e086", "e092", "e093"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case02-discharge-transport"]["uncertainty"][2],
                    "verdict": "false_positive_already_operationalized_safeguard",
                    "why": "Privacy failure, pausing, and no automatic renewal are already explicit safeguards and continuation conditions in the current position.",
                    "decisive_aliases": ["e049", "e071", "e098"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case02-discharge-transport"]["relationship"][0],
                    "verdict": "source_supported_but_dependent_on_false_positive",
                    "why": "The exact endpoints are valid, but the relationship only restates the already adopted amendment precondition.",
                    "decisive_aliases": ["e095"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case02-discharge-transport"]["relationship"][1],
                    "verdict": "exact_endpoints_but_target_relationship_not_recovered",
                    "why": "The relationship says the pilot adopts coordinator requirements; it does not preserve the frozen limiting relationship between a bounded pilot and continuation or generalization.",
                    "decisive_aliases": ["e086", "e096"],
                },
            ],
            "missed_target_material": [
                "cross-setting generalization from two wards in one participating city",
                "accessible-vehicle supply outside the bounded pilot setting",
            ],
        },
        {
            "case_id": "v1-case03-executive-hire",
            "selection_role": "matched_restraint_control",
            "verdict": "restraint_failed",
            "record_reviews": [
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case03-executive-hire"]["uncertainty"][0],
                    "verdict": "false_positive_later_source_not_integrated",
                    "why": "The record relies on the earlier writing gap at e061 while the final position says disputed commitments follow the written boundary process at e105.",
                    "decisive_aliases": ["e061", "e105"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case03-executive-hire"]["uncertainty"][1],
                    "verdict": "false_positive_existing_review_recast_as_reopen_condition",
                    "why": "The founder-president relationship diagnostic is already part of the explicit six-month review structure.",
                    "decisive_aliases": ["e103", "e104", "e113"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case03-executive-hire"]["uncertainty"][2],
                    "verdict": "false_positive_existing_benchmark_recast_as_reopen_condition",
                    "why": "Whether unwelcome information travels upward is already an explicit six-month evaluative benchmark, not a newly recovered uncertainty.",
                    "decisive_aliases": ["e111"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case03-executive-hire"]["relationship"][0],
                    "verdict": "manufactured_from_existing_review_structure",
                    "why": "The exact endpoint relationship merely restates a review component already present in the current position.",
                    "decisive_aliases": ["e104"],
                },
                {
                    "record_id": EXPECTED_RECORD_IDS["v1-case03-executive-hire"]["relationship"][1],
                    "verdict": "dependent_on_false_positive_and_overstates_gap",
                    "why": "The relationship inherits the disputed-promise false positive and overlooks the final written-boundary-process statement.",
                    "decisive_aliases": ["e061", "e105"],
                },
            ],
        },
    ]
    dimensions = [
        {
            "dimension": "material_pressure_recovered",
            "verdict": "pass_narrowly",
            "why": "One target record recovered the temporary-support and steady-state labor gap. The cross-setting and accessible-supply parts of the broader frozen target were missed.",
        },
        {
            "dimension": "false_positive_restraint",
            "verdict": "fail",
            "why": "The restraint control produced three uncertainty records and two relationships by recasting an earlier gap and already operationalized review criteria as new uncertainty.",
        },
        {
            "dimension": "evidence_precision",
            "verdict": "fail",
            "why": "Exact aliases were mechanically valid, but the control's unresolved record did not integrate later e105 evidence that materially changes its claim.",
        },
        {
            "dimension": "role_placement",
            "verdict": "pass_structurally",
            "why": "Unresolved matter, reopen condition, and relationship remained separately inspectable; this is a representation result, not semantic correctness.",
        },
        {
            "dimension": "relationship_fidelity",
            "verdict": "fail_semantic_restraint",
            "why": "All endpoints used exact admitted IDs, but the target limiting relationship was missed and the control manufactured relationships from false-positive or already operationalized records.",
        },
        {
            "dimension": "operational_load_and_cost",
            "verdict": "pass_observed_exactly",
            "why": "Four attributable calls completed for $0.010835 with no retry, fallback, healing, evaluator, embedding, graph, pipeline, or runtime work.",
        },
    ]
    review: dict[str, Any] = {
        "schema_version": "lolla.r4_complementary_reader_source_first_review.v2",
        "status": "semantic_hypothesis_not_supported_restraint_failed",
        "date": "2026-07-14",
        "source_first_target_path": _relative(TARGET),
        "source_first_target_sha256": _file_sha(TARGET),
        "source_first_target_visible_to_provider": False,
        "evidence_manifest_sha256": manifest_sha256,
        "semantic_review_performed": True,
        "relationship_review_performed": True,
        "case_reviews": case_reviews,
        "dimensions": dimensions,
        "scalar_quality_score": None,
        "conclusion": "The corrected reader can recover a missing pressure, but this prompt contract cannot yet distinguish distinct remaining uncertainty from preconditions, safeguards, and review criteria already incorporated into the current position.",
        "non_claims": [
            "This two-case simulated diagnostic is not a reliability, usefulness, production-model, graph-value, or real-user claim.",
            "A semantic failure does not imply that Gemini 3.1 Flash-Lite is generally incapable.",
            "The review does not establish that a revised answer or human decision would be better.",
        ],
    }
    review["result_sha256"] = value_sha256(review)
    return review


def _build_values() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = validate_contract(CONTRACT)
    validate_authorization(AUTHORIZATION, contract=contract, contract_path=CONTRACT)
    result = _load(RUN_RESULT)
    if (
        result.get("status") != "provider_calls_preserved_source_first_review_required"
        or result.get("provider_calls") != 4
        or result.get("provider_reported_cost_usd") != 0.010835
        or result.get("cost_ceiling_met") is not True
        or result.get("cost_custody_known") is not True
        or result.get("fallback_models") != 0
        or result.get("automatic_retries") != 0
        or result.get("semantic_retries") != 0
        or result.get("response_healing") is not False
        or any(result.get(field) != 0 for field in ("evaluator_calls", "embedding_calls", "graph_calls", "pipeline_calls", "runtime_calls"))
    ):
        raise R4TokenCorrectionCloseoutError("terminal runner result drifted")
    observations = [_call_observation(row) for row in EXPECTED_CALLS]
    for case_id, tasks in EXPECTED_RECORD_IDS.items():
        for task, record_ids in tasks.items():
            if _record_ids(case_id, task) != record_ids:
                raise R4TokenCorrectionCloseoutError(f"compiled records drifted: {case_id}/{task}")
        fan_in = _load(OUTPUT / case_id / "final-fan-in.json")
        counts = fan_in.get("fan_in", {}).get("reader_state_counts")
        if (
            fan_in.get("status") != "conversation_state_fan_in_complete"
            or counts != {"complete": 5, "completed_zero": 1, "failed": 0, "missing": 0, "partial": 0}
            or fan_in.get("fan_in", {}).get("total_record_count") != 7
        ):
            raise R4TokenCorrectionCloseoutError(f"final fan-in drifted: {case_id}")

    excluded = {MANIFEST.resolve(), SOURCE_REVIEW.resolve(), CLOSEOUT.resolve()}
    evidence_paths = [CONTRACT, AUTHORIZATION, TARGET]
    evidence_paths.extend(
        ROOT / path
        for path in (
            "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case02-discharge-transport.txt",
            "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case03-executive-hire.txt",
            "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case02-discharge-transport-primary/joined-role-records.json",
            "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case03-executive-hire-primary/joined-role-records.json",
        )
    )
    evidence_paths.extend(
        path for path in sorted(OUTPUT.rglob("*.json")) if path.resolve() not in excluded
    )
    seen: set[Path] = set()
    unique_paths = []
    for path in evidence_paths:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_paths.append(path)
    evidence_rows = []
    for path in unique_paths:
        if not path.is_file():
            raise R4TokenCorrectionCloseoutError(f"evidence missing: {_relative(path)}")
        evidence_rows.append({"path": _relative(path), "sha256": _file_sha(path), "utf8_bytes": len(path.read_bytes())})
    manifest: dict[str, Any] = {
        "schema_version": "lolla.r4_complementary_reader_execution_manifest.v2",
        "status": "exact_corrected_execution_evidence_preserved",
        "date": "2026-07-14",
        "files": evidence_rows,
        "file_count": len(evidence_rows),
        "provider_calls": 4,
        "provider_reported_cost_usd": 0.010835,
    }
    manifest["manifest_sha256"] = value_sha256(manifest)
    source_review = _source_review(manifest["manifest_sha256"])
    closeout: dict[str, Any] = {
        "schema_version": "lolla.r4_complementary_reader_execution_closeout.v2",
        "status": "attempt_closed_operational_correction_passed_semantic_restraint_failed",
        "date": "2026-07-14",
        "run_id": contract["run_id"],
        "contract_sha256": _file_sha(CONTRACT),
        "authorization_sha256": _file_sha(AUTHORIZATION),
        "evidence_manifest_sha256": manifest["manifest_sha256"],
        "source_first_review_sha256": source_review["result_sha256"],
        "provider_calls": 4,
        "relationship_calls": 2,
        "provider_reported_cost_usd": 0.010835,
        "maximum_provider_reported_cost_total_usd": 0.03,
        "cost_ceiling_met": True,
        "call_observations": observations,
        "mechanical_conclusion": {
            "token_allocation_correction_succeeded": True,
            "strict_json_candidates_parsed": True,
            "candidates_locally_admitted": True,
            "relationship_dependency_opened": True,
            "fan_in_completed": True,
            "reasoning_detail_custody": "All four calls report zero reasoning tokens while the frozen runner's broad field-presence flag is true. Provider reasoning-detail values were not preserved, so the historical calls are not reclassified and no content-shape claim is made.",
        },
        "semantic_conclusion": {
            "material_pressure_recovered": "pass_narrowly",
            "restraint_control": "fail",
            "semantic_hypothesis_supported": False,
            "bounded_diagnosis": "The prompt contract rewards finding any source-supported future condition, but does not yet reliably separate genuinely unresolved or reopening reasoning from a precondition, safeguard, boundary process, or review criterion already absorbed into the current position.",
        },
        "preserved_boundaries": {
            "automatic_retry_performed": False,
            "semantic_retry_performed": False,
            "fallback_or_model_switch_performed": False,
            "response_healing_performed": False,
            "runtime_or_graph_integration_performed": False,
            "scalar_quality_score_created": False,
        },
        "decision": {
            "this_attempt_may_be_retried": False,
            "additional_provider_call_authorized": False,
            "runtime_or_graph_integration_authorized": False,
            "wider_corpus_execution_authorized": False,
            "production_model_selected": False,
            "next_goal": "provider-free semantic-distinction contract for distinct uncertainty versus already operationalized preconditions, safeguards, and review criteria; reuse the corrected reasoning-detail validator in future runners, validate on fixtures, and reserve a new holdout before any call",
        },
    }
    closeout["result_sha256"] = value_sha256(closeout)
    return manifest, source_review, closeout


def build() -> dict[str, Any]:
    manifest, source_review, closeout = _build_values()
    _write(MANIFEST, manifest)
    _write(SOURCE_REVIEW, source_review)
    _write(CLOSEOUT, closeout)
    return closeout


def validate() -> dict[str, Any]:
    expected = _build_values()
    for path, value in zip((MANIFEST, SOURCE_REVIEW, CLOSEOUT), expected):
        if not path.is_file() or path.read_bytes() != _render(value):
            raise R4TokenCorrectionCloseoutError(f"closeout artifact drifted: {_relative(path)}")
    for path, hash_field in ((MANIFEST, "manifest_sha256"), (SOURCE_REVIEW, "result_sha256"), (CLOSEOUT, "result_sha256")):
        value = _load(path)
        if value.get(hash_field) != value_sha256(_without(value, hash_field)):
            raise R4TokenCorrectionCloseoutError(f"self-hash drifted: {_relative(path)}")
    return expected[-1]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    result = validate() if args.validate_only else build()
    print(json.dumps({
        "status": result["status"],
        "provider_calls": result["provider_calls"],
        "provider_reported_cost_usd": result["provider_reported_cost_usd"],
        "semantic_hypothesis_supported": result["semantic_conclusion"]["semantic_hypothesis_supported"],
        "additional_provider_call_authorized": result["decision"]["additional_provider_call_authorized"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
