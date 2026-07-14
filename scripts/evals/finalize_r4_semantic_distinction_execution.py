#!/usr/bin/env python3
"""Seal and source-review the frozen R4 semantic-distinction execution."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.r4_complementary_readers import value_sha256
from scripts.evals.run_r4_semantic_distinction_experiment import (
    validate_authorization,
    validate_contract,
)


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/evals/lolla-r4-semantic-distinction-contract-v1.json"
AUTHORIZATION = ROOT / (
    "docs/evals/lolla-r4-semantic-distinction-holdout-authorization-a3.json"
)
TARGET = ROOT / "docs/evals/lolla-r4-semantic-distinction-holdout-target-v1.json"
OUTPUT = ROOT / (
    "research/lolla-r4-semantic-distinction-holdout-execution-2026-07-14-a3"
)
RUN_RESULT = OUTPUT / "result.json"
MANIFEST = OUTPUT / "evidence-manifest.json"
SOURCE_REVIEW = OUTPUT / "source-first-review.json"
CLOSEOUT = OUTPUT / "execution-closeout.json"

MODEL = "google/gemini-3.1-flash-lite"
PROVIDER = "Google"
TOTAL_COST_USD = 0.01107025
EXPECTED_CALLS = (
    {
        "case_id": "v1-case01-flood-infrastructure",
        "ordinal": 1,
        "task": "uncertainty",
        "cost": 0.00394925,
        "completion_tokens": 352,
        "prompt_tokens": 13685,
        "max_output_tokens": 1600,
        "request_body_sha256": (
            "08b80a4bb6c7d67a5becea7109837694cac0866c6edc5932365efaf65fa9b9c9"
        ),
        "raw_content_sha256": (
            "3615c5abb9abf6d82c1bbb1aa606e80a74d451d69e66800858f429070215fb25"
        ),
    },
    {
        "case_id": "v1-case01-flood-infrastructure",
        "ordinal": 2,
        "task": "relationship",
        "cost": 0.0014265,
        "completion_tokens": 180,
        "prompt_tokens": 4626,
        "max_output_tokens": 700,
        "request_body_sha256": (
            "762298c058ccba5637056be4090e895348deee437901d554a198fc21b2c3e679"
        ),
        "raw_content_sha256": (
            "d3c5043c630c30d35b2cdc75aaf479775b9cf586b9a41a827af9a1c480b76eb1"
        ),
    },
    {
        "case_id": "v1-case04-component-sourcing",
        "ordinal": 3,
        "task": "uncertainty",
        "cost": 0.003794,
        "completion_tokens": 416,
        "prompt_tokens": 12680,
        "max_output_tokens": 1600,
        "request_body_sha256": (
            "03b6c910d044c3ad1868d67db4785fb445bbdc741fce95f081575a3e814cd00b"
        ),
        "raw_content_sha256": (
            "4311c8c19c6d0e22cd586dd763240a3f117c901bd15549dab3e9cf0967d708ee"
        ),
    },
    {
        "case_id": "v1-case04-component-sourcing",
        "ordinal": 4,
        "task": "relationship",
        "cost": 0.0019005,
        "completion_tokens": 370,
        "prompt_tokens": 5382,
        "max_output_tokens": 700,
        "request_body_sha256": (
            "ba300245b164f61575776fb713caa1fcc3d1c633d55417b0ebc917083bd2a25d"
        ),
        "raw_content_sha256": (
            "499bf0b43492cd9119ce0e66ef8c7aadbd40817c7d7dacc5992a4521209aa279"
        ),
    },
)

EXPECTED_RECORD_IDS = {
    "v1-case01-flood-infrastructure": {
        "uncertainty": [
            "r4u-v1-case01-flood-infrastructure-unresolved_matter-01-7280ed2457de",
            "r4u-v1-case01-flood-infrastructure-reopen_condition-01-5b6698a3a632",
        ],
        "relationship": [
            "r4x-v1-case01-flood-infrastructure-01-a4329d3a81de",
        ],
    },
    "v1-case04-component-sourcing": {
        "uncertainty": [
            "r4u-v1-case04-component-sourcing-unresolved_matter-01-4f838513f370",
            "r4u-v1-case04-component-sourcing-reopen_condition-01-232f866a85e6",
            "r4u-v1-case04-component-sourcing-reopen_condition-02-98ccf8ae047a",
        ],
        "relationship": [
            "r4x-v1-case04-component-sourcing-01-c8e7611539c2",
            "r4x-v1-case04-component-sourcing-02-7508046b8860",
        ],
    },
}


class R4SemanticDistinctionCloseoutError(RuntimeError):
    """Raised when execution evidence or its locked review drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4SemanticDistinctionCloseoutError(f"expected JSON object: {path}")
    return value


def _render(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


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
        raise R4SemanticDistinctionCloseoutError(
            f"usage missing: {case_id}/{task}"
        )
    details = usage.get("completion_tokens_details")
    custody = result.get("reasoning_custody")
    raw_content = result.get("raw_content")
    candidate = result.get("candidate")
    if (
        not isinstance(details, Mapping)
        or not isinstance(custody, Mapping)
        or not isinstance(raw_content, str)
        or not isinstance(candidate, Mapping)
    ):
        raise R4SemanticDistinctionCloseoutError(
            f"call payload incomplete: {case_id}/{task}"
        )
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
        or result.get("reasoning_values_preserved") is not False
        or result.get("max_output_tokens") != expected["max_output_tokens"]
        or result.get("provider_reported_cost_usd") != expected["cost"]
        or usage.get("cost") != expected["cost"]
        or usage.get("completion_tokens") != expected["completion_tokens"]
        or usage.get("prompt_tokens") != expected["prompt_tokens"]
        or details.get("reasoning_tokens") != 0
        or custody.get("status") != "reasoning_metadata_only"
        or custody.get("exclusion_satisfied") is not True
        or custody.get("content_present") is not False
        or custody.get("metadata_only") is not True
        or custody.get("provider_values_included") is not False
        or result.get("request_body_sha256") != expected["request_body_sha256"]
        or started.get("request_body_sha256") != expected["request_body_sha256"]
        or result.get("raw_content_sha256") != expected["raw_content_sha256"]
        or hashlib.sha256(raw_content.encode("utf-8")).hexdigest()
        != expected["raw_content_sha256"]
        or value_sha256(candidate)
        != value_sha256(_load(case_dir / f"{task}-candidate.json"))
    ):
        raise R4SemanticDistinctionCloseoutError(
            f"frozen call evidence drifted: {case_id}/{task}"
        )
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
        "reasoning_envelope_status": "reasoning_metadata_only",
        "reasoning_values_preserved": False,
        "prompt_tokens": expected["prompt_tokens"],
        "provider_reported_cost_usd": expected["cost"],
        "request_body_sha256": expected["request_body_sha256"],
        "raw_content_sha256": expected["raw_content_sha256"],
    }


def _source_review(manifest_sha256: str) -> dict[str, Any]:
    case01 = EXPECTED_RECORD_IDS["v1-case01-flood-infrastructure"]
    case04 = EXPECTED_RECORD_IDS["v1-case04-component-sourcing"]
    case_reviews = [
        {
            "case_id": "v1-case01-flood-infrastructure",
            "selection_role": "unseen_false_stand_down_target",
            "verdict": "narrow_material_recovery_with_precision_and_overgeneration_failures",
            "record_reviews": [
                {
                    "record_id": case01["uncertainty"][0],
                    "verdict": "narrow_operating_dependency_recovered_with_imprecise_custody",
                    "why": "The record recognizes that long-term barrier performance depends on future city execution and staffing, which narrowly recovers the sustainable operating-capability pressure. It does not identify the central recurring funding and ownership gap, and its cited aliases mostly describe safeguards already adopted rather than the direct crew, storage, shuttle, and support evidence.",
                    "decisive_aliases": [
                        "e005",
                        "e074",
                        "e078",
                        "e099",
                        "e103",
                        "e104",
                        "e105",
                        "e106",
                        "e113",
                    ],
                },
                {
                    "record_id": case01["uncertainty"][1],
                    "verdict": "false_positive_precondition_and_existing_process_recast_as_reopen",
                    "why": "The hydraulic no-go rule was a pre-installation condition, while the peer review, deployment exercise, partial-installation procedure, and incident publication were incorporated into the final position. This record does not recover the frozen condition that continued reliance should reopen when recurring operating capability cannot be sustained.",
                    "decisive_aliases": [
                        "e041",
                        "e045",
                        "e073",
                        "e104",
                        "e106",
                    ],
                },
                {
                    "record_id": case01["relationship"][0],
                    "verdict": "exact_endpoints_with_partial_target_meaning",
                    "why": "The exact endpoints add a real post-installation accountability dependency to the current position, but the relationship inherits the imprecise unresolved record and misses the frozen distinction between grant-funded installation and recurring city ownership and funding.",
                    "decisive_aliases": [
                        "e005",
                        "e099",
                        "e103",
                        "e104",
                        "e106",
                        "e113",
                    ],
                },
            ],
            "missed_target_material": [
                "who funds and owns recurring deployment crews and readiness work after installation attention recedes",
                "storage-route, shuttle-staffing, training, incident-support, and after-action capacity as one sustained operating system",
                "continued-reliance reopening when exercises, incidents, staffing budgets, or shuttle availability show that the assumed capability cannot be sustained",
                "the explicit limiting relationship between grant-funded installation and longer-lived city operating ownership",
            ],
        },
        {
            "case_id": "v1-case04-component-sourcing",
            "selection_role": "unseen_restraint_control",
            "verdict": "restraint_failed",
            "record_reviews": [
                {
                    "record_id": case04["uncertainty"][0],
                    "verdict": "false_positive_deferred_choice_and_existing_process_recast_as_unresolved",
                    "why": "The final position funds a shared interface, requests parallel proposals, preserves competition, and fixes a twelve-month decision using redesign progress. The record cites no evidence that milestone ownership is absent and explicitly treats the pending proposals and scheduled review as the gap the contract said not to manufacture.",
                    "decisive_aliases": ["e094", "e096", "e097", "e098", "e101"],
                },
                {
                    "record_id": case04["uncertainty"][1],
                    "verdict": "false_positive_predefined_thresholds_recast_as_reopen",
                    "why": "Quality, delivery, and support thresholds, fixed reviews, and the exit from a nominal backup are already explicit operating gates in the adopted one-year structure.",
                    "decisive_aliases": ["e036", "e047", "e052", "e054", "e058"],
                },
                {
                    "record_id": case04["uncertainty"][2],
                    "verdict": "false_positive_existing_fallback_and_review_recast_as_reopen",
                    "why": "Milestone evidence, alternatives, fallback on slippage, redesign progress, and the twelve-month decision are already the current transition process rather than a distinct newly recovered reopen condition.",
                    "decisive_aliases": ["e094", "e096", "e098", "e101"],
                },
                {
                    "record_id": case04["relationship"][0],
                    "verdict": "manufactured_from_false_reopen_and_existing_qualification",
                    "why": "The endpoint IDs are exact, but the relation only states that an existing technical qualification supplies the existing exit criteria represented by the false-positive reopen record.",
                    "decisive_aliases": ["e088", "e094", "e098"],
                },
                {
                    "record_id": case04["relationship"][1],
                    "verdict": "dependent_on_false_unresolved_and_paraphrases_current_mechanism",
                    "why": "The relation inherits the manufactured milestone gap and paraphrases the already adopted shared-interface and parallel-proposal mechanism.",
                    "decisive_aliases": ["e096", "e097", "e098"],
                },
            ],
        },
    ]
    dimensions = [
        {
            "dimension": "material_pressure_recovered",
            "verdict": "pass_narrowly",
            "why": "Case 01 recognized a durable city-execution and staffing dependency, but missed the central recurring funding and ownership gap and most of the frozen operating-system detail.",
        },
        {
            "dimension": "false_positive_restraint",
            "verdict": "fail",
            "why": "The Case 04 restraint control produced three uncertainty records and two relationships from deferred choice, predefined thresholds, fallbacks, and a scheduled review. Case 01 also recast a precondition and adopted process as a reopen condition.",
        },
        {
            "dimension": "evidence_precision",
            "verdict": "fail",
            "why": "All aliases resolved mechanically, but the Case 01 operating-dependency record cited final safeguards rather than the strongest direct ownership and funding evidence, and the Case 04 milestone claim treated the absence of detail as source-supported unresolved meaning.",
        },
        {
            "dimension": "role_placement",
            "verdict": "pass_structurally_fail_semantically",
            "why": "Current position, unresolved matter, reopen condition, and relationship stayed separately inspectable, but adopted preconditions, safeguards, and reviews were placed into unresolved and reopen roles.",
        },
        {
            "dimension": "relationship_fidelity",
            "verdict": "fail_semantic_restraint",
            "why": "Every relationship used exact admitted IDs. Case 01 preserved only part of the target limiting dependency, while Case 04 manufactured two relationships from false-positive or already represented endpoints.",
        },
        {
            "dimension": "operational_load_and_cost",
            "verdict": "pass_observed_exactly",
            "why": "Four attributable calls completed for $0.01107025 with strict local admission and no retry, fallback, healing, evaluator, embedding, graph, pipeline, or runtime work.",
        },
    ]
    review: dict[str, Any] = {
        "schema_version": "lolla.r4_semantic_distinction_source_first_review.v1",
        "status": "semantic_hypothesis_not_supported_restraint_failed",
        "date": "2026-07-14",
        "source_first_target_path": _relative(TARGET),
        "source_first_target_sha256": _file_sha(TARGET),
        "source_first_target_visible_to_provider": False,
        "target_opened_only_after_provider_execution_completed": True,
        "run_result_file_sha256": _file_sha(RUN_RESULT),
        "evidence_manifest_sha256": manifest_sha256,
        "semantic_review_performed": True,
        "relationship_review_performed": True,
        "case_reviews": case_reviews,
        "dimensions": dimensions,
        "scalar_quality_score": None,
        "conclusion": "The v2 prompt preserved a narrow operating-capability signal but did not establish the required distinction. It still converted deferred work, adopted preconditions, safeguards, fallback procedures, and fixed review criteria into new uncertainty, so sensitivity and restraint are not jointly supported.",
        "non_claims": [
            "This two-case simulated diagnostic is not a reliability, usefulness, production-model, graph-value, or real-user claim.",
            "A semantic failure does not imply that Gemini 3.1 Flash-Lite is generally incapable.",
            "Mechanical schema, identity, and fan-in success do not imply semantic correctness.",
            "The review does not establish that a revised answer or human decision would be better.",
        ],
    }
    review["result_sha256"] = value_sha256(review)
    return review


def _build_values() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract = validate_contract(CONTRACT)
    validate_authorization(
        AUTHORIZATION, contract=contract, contract_path=CONTRACT
    )
    result = _load(RUN_RESULT)
    if (
        result.get("status")
        != "provider_calls_preserved_source_first_review_required"
        or result.get("provider_calls") != 4
        or result.get("provider_reported_cost_usd") != TOTAL_COST_USD
        or result.get("cost_ceiling_met") is not True
        or result.get("cost_custody_known") is not True
        or result.get("fallback_models") != 0
        or result.get("automatic_retries") != 0
        or result.get("semantic_retries") != 0
        or result.get("response_healing") is not False
        or any(
            result.get(field) != 0
            for field in (
                "evaluator_calls",
                "embedding_calls",
                "graph_calls",
                "pipeline_calls",
                "runtime_calls",
            )
        )
    ):
        raise R4SemanticDistinctionCloseoutError("terminal runner result drifted")
    observations = [_call_observation(row) for row in EXPECTED_CALLS]
    expected_fan_in = {
        "v1-case01-flood-infrastructure": 6,
        "v1-case04-component-sourcing": 8,
    }
    for case_id, tasks in EXPECTED_RECORD_IDS.items():
        for task, record_ids in tasks.items():
            if _record_ids(case_id, task) != record_ids:
                raise R4SemanticDistinctionCloseoutError(
                    f"compiled records drifted: {case_id}/{task}"
                )
        fan_in = _load(OUTPUT / case_id / "final-fan-in.json")
        counts = fan_in.get("fan_in", {}).get("reader_state_counts")
        if (
            fan_in.get("status") != "conversation_state_fan_in_complete"
            or counts
            != {
                "complete": 6,
                "completed_zero": 0,
                "failed": 0,
                "missing": 0,
                "partial": 0,
            }
            or fan_in.get("fan_in", {}).get("total_record_count")
            != expected_fan_in[case_id]
        ):
            raise R4SemanticDistinctionCloseoutError(
                f"final fan-in drifted: {case_id}"
            )

    excluded = {MANIFEST.resolve(), SOURCE_REVIEW.resolve(), CLOSEOUT.resolve()}
    evidence_paths = [CONTRACT, AUTHORIZATION, TARGET]
    evidence_paths.extend(
        ROOT / path
        for path in (
            "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case01-flood-infrastructure.txt",
            "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-transfer-sources/v1-case04-component-sourcing.txt",
            "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case01-flood-infrastructure-primary/joined-role-records.json",
            "research/simulated-reliability-v1-transfer-2026-07-12/t1/v1-case04-component-sourcing-primary/joined-role-records.json",
        )
    )
    evidence_paths.extend(
        path
        for path in sorted(OUTPUT.rglob("*.json"))
        if path.resolve() not in excluded
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
            raise R4SemanticDistinctionCloseoutError(
                f"evidence missing: {_relative(path)}"
            )
        evidence_rows.append(
            {
                "path": _relative(path),
                "sha256": _file_sha(path),
                "utf8_bytes": len(path.read_bytes()),
            }
        )
    manifest: dict[str, Any] = {
        "schema_version": "lolla.r4_semantic_distinction_execution_manifest.v1",
        "status": "exact_semantic_distinction_execution_evidence_preserved",
        "date": "2026-07-14",
        "files": evidence_rows,
        "file_count": len(evidence_rows),
        "provider_calls": 4,
        "provider_reported_cost_usd": TOTAL_COST_USD,
    }
    manifest["manifest_sha256"] = value_sha256(manifest)
    source_review = _source_review(manifest["manifest_sha256"])
    closeout: dict[str, Any] = {
        "schema_version": "lolla.r4_semantic_distinction_execution_closeout.v1",
        "status": "attempt_closed_mechanically_complete_semantic_restraint_failed",
        "date": "2026-07-14",
        "run_id": contract["run_id"],
        "contract_sha256": _file_sha(CONTRACT),
        "authorization_sha256": _file_sha(AUTHORIZATION),
        "holdout_target_sha256": _file_sha(TARGET),
        "run_result_file_sha256": _file_sha(RUN_RESULT),
        "evidence_manifest_sha256": manifest["manifest_sha256"],
        "source_first_review_sha256": source_review["result_sha256"],
        "provider_calls": 4,
        "relationship_calls": 2,
        "provider_reported_cost_usd": TOTAL_COST_USD,
        "conservative_estimated_total_cost_usd": 0.0280125,
        "maximum_provider_reported_cost_total_usd": 0.03,
        "cost_ceiling_met": True,
        "call_observations": observations,
        "mechanical_conclusion": {
            "frozen_contract_executed_without_drift": True,
            "strict_json_candidates_parsed": True,
            "candidates_locally_admitted": True,
            "relationship_dependencies_opened": True,
            "fan_in_completed": True,
            "reasoning_detail_custody": "All four calls report zero reasoning tokens. The strict value-free inspector classified each returned envelope as metadata-only, preserved no provider reasoning values, and satisfied the exclusion contract.",
        },
        "semantic_conclusion": {
            "material_pressure_recovered": "pass_narrowly",
            "restraint_control": "fail",
            "evidence_precision": "fail",
            "semantic_hypothesis_supported": False,
            "bounded_diagnosis": "The v2 prompt still rewarded finding source-supported future conditions even when the final position had already converted them into preconditions, safeguards, fallback procedures, or scheduled review criteria. It preserved a narrow operating-capability signal but did not balance sensitivity with restraint.",
        },
        "preserved_boundaries": {
            "automatic_retry_performed": False,
            "semantic_retry_performed": False,
            "fallback_or_model_switch_performed": False,
            "response_healing_performed": False,
            "evaluator_call_performed": False,
            "embedding_call_performed": False,
            "runtime_or_graph_integration_performed": False,
            "scalar_quality_score_created": False,
        },
        "decision": {
            "this_attempt_may_be_retried": False,
            "additional_provider_call_authorized": False,
            "runtime_or_graph_integration_authorized": False,
            "wider_corpus_execution_authorized": False,
            "r5_product_evidence_authorized": False,
            "production_model_selected": False,
            "case01_and_case04_now_exposed_development_evidence": True,
            "future_provider_validation_requires_new_holdout_and_authorization": True,
            "next_goal": "Provider-free causal diagnosis of why the zero, resolution, safeguard, and scheduled-review distinctions did not survive the Case 04 endpoint. Use this consumed holdout only as exposed development evidence, decide whether a task-shape redesign or an R4 stop is earned, and freeze a genuinely new holdout before proposing any future paid validation.",
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
            raise R4SemanticDistinctionCloseoutError(
                f"closeout artifact drifted: {_relative(path)}"
            )
    for path, hash_field in (
        (MANIFEST, "manifest_sha256"),
        (SOURCE_REVIEW, "result_sha256"),
        (CLOSEOUT, "result_sha256"),
    ):
        value = _load(path)
        if value.get(hash_field) != value_sha256(_without(value, hash_field)):
            raise R4SemanticDistinctionCloseoutError(
                f"self-hash drifted: {_relative(path)}"
            )
    return expected[-1]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    result = validate() if args.validate_only else build()
    print(
        json.dumps(
            {
                "status": result["status"],
                "provider_calls": result["provider_calls"],
                "provider_reported_cost_usd": result[
                    "provider_reported_cost_usd"
                ],
                "semantic_hypothesis_supported": result[
                    "semantic_conclusion"
                ]["semantic_hypothesis_supported"],
                "additional_provider_call_authorized": result["decision"][
                    "additional_provider_call_authorized"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
