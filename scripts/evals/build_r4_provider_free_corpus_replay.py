#!/usr/bin/env python3
"""Build and validate the provider-free R4 corpus/artifact replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.system_b.r3_fresh_consumer import value_sha256  # noqa: E402


CORPUS_ROOT = ROOT / "research/simulated-reliability-corpus-v1-2026-07-12"
SOURCE_MANIFEST = CORPUS_ROOT / "manifest.json"
NATURALIZED_REVIEW = CORPUS_ROOT / "naturalized-source-review.json"
PREFLIGHT_ROOT = CORPUS_ROOT / "provider-free-role-input-preflight"
PREFLIGHT_REPORT = PREFLIGHT_ROOT / "report.json"
TRANSFER_ROOT = ROOT / "research/simulated-reliability-v1-transfer-2026-07-12/t1"
BATCH_SEAL = TRANSFER_ROOT / "batch-seal.json"
RECEIPT_ROOT = ROOT / "research/simulated-reliability-v1-receipts-2026-07-13/t1"
RECEIPT_REPORT = RECEIPT_ROOT / "report.json"
RECEIPT_INTEGRITY = RECEIPT_ROOT / "integrity-report.json"
DIAGNOSTIC_REVIEW = ROOT / (
    "research/simulated-reliability-v1-review-2026-07-13/"
    "t1-diagnostic-source-review.json"
)
EVIDENCE_MATRIX = ROOT / (
    "research/simulated-reliability-v1-evaluation-2026-07-13/"
    "evidence-matrix.json"
)
MEASUREMENT_CONTRACT = ROOT / "docs/evals/lolla-r4-measurement-contract-v1.json"
OUTPUT_ROOT = ROOT / "research/lolla-r4-corpus-replay-2026-07-13"
INVENTORY_PATH = OUTPUT_ROOT / "r4-corpus-replay-manifest.json"
GAP_MATRIX_PATH = OUTPUT_ROOT / "r4-replay-gap-matrix.json"
RESULT_PATH = OUTPUT_ROOT / "r4-replay-result.json"
DOWNSTREAM_OUTPUT_ROOTS = (
    ROOT / "research/lolla-r4-conversation-state-fan-in-2026-07-13",
    ROOT / "research/lolla-r4-complementary-reader-preflight-2026-07-13",
    ROOT / "research/lolla-r4-complementary-reader-execution-2026-07-14-a1",
    ROOT / "research/lolla-r4-complementary-reader-token-correction-2026-07-14",
    ROOT / "research/lolla-r4-complementary-reader-token-correction-execution-2026-07-14-a2",
    ROOT / "research/lolla-r4-semantic-distinction-contract-2026-07-14",
    ROOT / "research/lolla-r4-semantic-distinction-holdout-execution-2026-07-14-a3",
    ROOT / "research/lolla-r4-semantic-distinction-causal-diagnosis-2026-07-14",
    ROOT / "research/lolla-r4-residual-task-contract-2026-07-14",
)
DOWNSTREAM_INPUT_PATHS = (
    ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-contract-v1.json",
    ROOT / "docs/evals/lolla-r4-complementary-reader-source-first-target-v1.json",
    ROOT / "docs/evals/lolla-r4-complementary-reader-experiment-authorization-a1.json",
    ROOT / "docs/evals/lolla-r4-complementary-reader-token-correction-contract-v1.json",
    ROOT / "docs/evals/lolla-r4-complementary-reader-token-correction-authorization-a2.json",
    ROOT / "docs/evals/lolla-r4-semantic-distinction-contract-v1.json",
    ROOT / "docs/evals/lolla-r4-semantic-distinction-holdout-target-v1.json",
    ROOT / "docs/evals/lolla-r4-semantic-distinction-holdout-authorization-a3.json",
)

EXPECTED_INPUT_HASHES = {
    "research/simulated-reliability-corpus-v1-2026-07-12/manifest.json": (
        "93fabb750960e9c3c2b683f8ae576ca61ca2c50204039718cde0aff7c9ffbb27"
    ),
    "research/simulated-reliability-corpus-v1-2026-07-12/naturalized-source-review.json": (
        "010e34ac9c8e5c558cb327403920f6f162c41ab9e5d5b441e4d93920a61caf33"
    ),
    (
        "research/simulated-reliability-corpus-v1-2026-07-12/"
        "provider-free-role-input-preflight/report.json"
    ): "45b1ffbe2d9402345e2fd9476fea1550acc8365235e77adeabac70005366ca8a",
}

COMPLETE_CASES = {
    "v1-case01-flood-infrastructure",
    "v1-case02-discharge-transport",
    "v1-case03-executive-hire",
    "v1-case04-component-sourcing",
    "v1-case05-ai-tutoring",
    "v1-case07-cooperative-scheduling",
    "v1-case08-museum-entry",
}
ROLE_JOIN_FAILURE = "v1-case06-industry-funded-lab"
TRANSPORT_FAILURES = {
    "v1-case09-software-migration",
    "v1-case10-restricted-funding",
    "v1-case11-elder-care-relocation",
    "v1-case12-newsroom-platform",
}
REQUIRED_SURFACES = [
    "authoritative_conversation",
    "source_review",
    "source_locator_custody",
    "starting_position",
    "current_position",
    "qualification",
    "unresolved_matter",
    "reopen_condition",
    "cross_thread_relationship",
    "mechanism_coverage",
    "direct_pressure",
    "graph_pressure",
    "final_consumer",
    "receipt",
    "failure_artifact",
]
SHARED_ARTIFACTS = [
    SOURCE_MANIFEST,
    NATURALIZED_REVIEW,
    PREFLIGHT_REPORT,
    BATCH_SEAL,
    RECEIPT_REPORT,
    RECEIPT_INTEGRITY,
    DIAGNOSTIC_REVIEW,
    EVIDENCE_MATRIX,
    MEASUREMENT_CONTRACT,
]


class R4ReplayError(RuntimeError):
    """Raised when the frozen R4 replay boundary or custody drifts."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4ReplayError(f"expected JSON object: {_relative(path)}")
    return value


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != field}


def _validate_frozen_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    for relative, expected in EXPECTED_INPUT_HASHES.items():
        path = ROOT / relative
        if not path.is_file() or _sha(path) != expected:
            raise R4ReplayError(f"frozen input hash drifted: {relative}")
    manifest = _load(SOURCE_MANIFEST)
    review = _load(NATURALIZED_REVIEW)
    preflight = _load(PREFLIGHT_REPORT)
    cases = manifest.get("transfer_cases")
    review_cases = review.get("cases")
    preflight_cases = [
        item for item in preflight.get("artifacts", []) if item.get("split") == "transfer"
    ]
    if (
        not isinstance(cases, list)
        or len(cases) != 12
        or not isinstance(review_cases, list)
        or len(review_cases) != 12
        or len(preflight_cases) != 12
        or preflight.get("summary", {}).get("provider_calls") != 0
    ):
        raise R4ReplayError("frozen 12-case corpus boundary drifted")
    ids = [str(item.get("case_id")) for item in cases]
    if len(ids) != len(set(ids)) or set(ids) != COMPLETE_CASES | {ROLE_JOIN_FAILURE} | TRANSPORT_FAILURES:
        raise R4ReplayError("case identity boundary drifted")
    review_by_id = {str(item.get("case_id")): item for item in review_cases}
    preflight_by_id = {str(item.get("case_id")): item for item in preflight_cases}
    for item in cases:
        case_id = str(item["case_id"])
        source = ROOT / str(item["path"])
        if (
            not source.is_file()
            or _sha(source) != item.get("sha256")
            or item.get("message_count") != 24
            or review_by_id.get(case_id, {}).get("naturalized_sha256") != item.get("sha256")
            or preflight_by_id.get(case_id, {}).get("source_sha256") != item.get("sha256")
            or preflight_by_id.get(case_id, {}).get("message_count") != 24
        ):
            raise R4ReplayError(f"source custody drifted: {case_id}")
    return manifest, review, preflight


def _surface_tags(path: Path) -> list[str]:
    name = path.name.lower()
    text = _relative(path).lower()
    tags: set[str] = set()
    if "source-review" in text or "source_review" in text or "review" in name:
        tags.add("source_review")
    if "position" in text or "role" in text:
        tags.add("position_role")
    if "qualification" in text:
        tags.add("qualification")
    if "unresolved" in text or "residual" in text:
        tags.add("unresolved_or_residual")
    if "reopen" in text:
        tags.add("reopen_condition")
    if "mechanism" in text or "coverage" in text:
        tags.add("mechanism_coverage")
    if "direct-ledger" in text or "direct_pressure" in text:
        tags.add("direct_pressure")
    if "graph" in text:
        tags.add("graph_pressure_or_attribution")
    if "consumer" in text or "three-arm" in text or "transcript_only" in text:
        tags.add("final_consumer")
    if "receipt" in text:
        tags.add("receipt")
    if "failure" in text or "error" in text:
        tags.add("failure")
    if "contract" in text or "authorization" in text:
        tags.add("contract_or_authorization")
    return sorted(tags or {"case_reference"})


def _partition(path: Path) -> tuple[str, list[str]]:
    relative = _relative(path)
    if relative.startswith("research/simulated-reliability-corpus-v1-2026-07-12/"):
        return "transfer_source_or_preflight", ["replayable", "transfer"]
    if relative.startswith("research/simulated-reliability-v1-transfer-2026-07-12/"):
        return "sealed_transfer_execution", ["replayable", "transfer"]
    if relative.startswith("research/simulated-reliability-v1-receipts-2026-07-13/"):
        return "sealed_transfer_receipt", ["replayable", "transfer"]
    if "simulated-reliability-v1-review-2026-07-13" in relative:
        return "diagnostic_review", ["replayable", "review-only"]
    if "simulated-reliability-v1-evaluation-2026-07-13" in relative:
        return "diagnostic_review", ["replayable", "review-only"]
    return "exposed_development_or_review", [
        "replayable",
        "exposed",
        "tuning-use-not-excluded",
        "review-only",
    ]


def _execution_state(path: Path, case_id: str, partition: str) -> str:
    if partition != "sealed_transfer_execution":
        return "preserved"
    if case_id in COMPLETE_CASES:
        return "complete"
    if case_id == ROLE_JOIN_FAILURE:
        return "partial" if "call-" in path.name else "failed"
    if case_id in TRANSPORT_FAILURES:
        return "failed"
    raise R4ReplayError(f"unknown transfer state: {case_id}")


def _artifact_record(path: Path, case_id: str) -> dict[str, Any]:
    partition, classifications = _partition(path)
    value = _load(path)
    state = _execution_state(path, case_id, partition)
    if state in {"partial", "failed"}:
        classifications = [*classifications, state]
    return {
        "path": _relative(path),
        "sha256": _sha(path),
        "utf8_bytes": len(path.read_bytes()),
        "schema_version": value.get("schema_version"),
        "declared_status": value.get("status"),
        "surface_tags": _surface_tags(path),
        "evidence_partition": partition,
        "execution_state": state,
        "classifications": classifications,
        "content_copied": False,
    }


def _discover_case_paths(case_ids: Sequence[str]) -> dict[str, set[Path]]:
    needles = {case_id: case_id.encode("utf-8") for case_id in case_ids}
    paths: dict[str, set[Path]] = {case_id: set() for case_id in case_ids}
    for base in (ROOT / "research", ROOT / "docs/evals"):
        for path in base.rglob("*.json"):
            if path in DOWNSTREAM_INPUT_PATHS or OUTPUT_ROOT in path.parents or any(
                downstream in path.parents for downstream in DOWNSTREAM_OUTPUT_ROOTS
            ):
                continue
            try:
                content = path.read_bytes()
                for case_id, needle in needles.items():
                    if needle in content:
                        paths[case_id].add(path)
            except OSError as exc:
                raise R4ReplayError(f"cannot inventory {_relative(path)}") from exc
    return paths


def _discover_case_artifacts(case_id: str, paths: set[Path]) -> list[dict[str, Any]]:
    return [_artifact_record(path, case_id) for path in sorted(paths)]


def _state(state: str, *, count: int | None = None, note: str = "") -> dict[str, Any]:
    value: dict[str, Any] = {"state": state}
    if count is not None:
        value["explicit_record_count"] = count
    if note:
        value["note"] = note
    return value


def _case_surfaces(case_id: str, role_counts: Mapping[str, int]) -> dict[str, Any]:
    complete = case_id in COMPLETE_CASES
    join_failed = case_id == ROLE_JOIN_FAILURE
    surfaces: dict[str, Any] = {
        "authoritative_conversation": _state("complete"),
        "source_review": _state("complete"),
        "source_locator_custody": _state("complete"),
        "unresolved_matter": _state(
            "missing",
            note="No distinct primary unresolved-matter contract; qualification is not reclassified.",
        ),
        "reopen_condition": _state(
            "missing",
            note="No distinct primary reopen-condition contract.",
        ),
        "cross_thread_relationship": _state(
            "missing",
            note="No distinct primary system relationship surface; source-review prose is not system output.",
        ),
        "receipt": _state("complete"),
    }
    if complete:
        for role in ("starting", "current", "qualification"):
            surfaces[f"{role}_position" if role != "qualification" else role] = _state(
                "complete", count=int(role_counts.get(role, 0))
            )
        for name in ("mechanism_coverage", "direct_pressure", "graph_pressure", "final_consumer"):
            surfaces[name] = _state("complete")
        surfaces["failure_artifact"] = _state("not_applicable")
    elif join_failed:
        surfaces["starting_position"] = _state(
            "failed", count=0, note="Provider output was quarantined; zero admitted records is not a semantic empty result."
        )
        surfaces["current_position"] = _state("partial", count=int(role_counts.get("current", 0)))
        surfaces["qualification"] = _state("partial", count=int(role_counts.get("qualification", 0)))
        for name in ("mechanism_coverage", "direct_pressure", "graph_pressure", "final_consumer"):
            surfaces[name] = _state("missing", note="Not produced after the role join failed closed.")
        surfaces["failure_artifact"] = _state("complete")
    else:
        surfaces["starting_position"] = _state(
            "failed", note="Transport failed before semantic inference; this is not an empty role result."
        )
        for name in (
            "current_position",
            "qualification",
            "mechanism_coverage",
            "direct_pressure",
            "graph_pressure",
            "final_consumer",
        ):
            surfaces[name] = _state("missing", note="Not produced after the starting transport failure.")
        surfaces["failure_artifact"] = _state("complete")
    if set(surfaces) != set(REQUIRED_SURFACES):
        raise R4ReplayError(f"surface inventory drifted: {case_id}")
    return surfaces


def _role_metrics(case_id: str) -> tuple[dict[str, int], dict[str, Any]]:
    wrapper = _load(PREFLIGHT_ROOT / "transfer" / case_id / "position-wrapper.json")
    aliases = wrapper.get("focal_alias_map")
    if not isinstance(aliases, list):
        raise R4ReplayError(f"missing alias map: {case_id}")
    alias_by_id = {str(item.get("alias")): item for item in aliases if isinstance(item, Mapping)}
    if len(alias_by_id) != len(aliases):
        raise R4ReplayError(f"duplicate or malformed aliases: {case_id}")
    for item in aliases:
        if (
            item.get("speaker") not in {"user", "assistant"}
            or not isinstance(item.get("turn_index"), int)
            or not 1 <= item["turn_index"] <= 24
            or len(str(item.get("text_sha256", ""))) != 64
        ):
            raise R4ReplayError(f"invalid source locator: {case_id}")
    role_counts = {"starting": 0, "current": 0, "qualification": 0}
    refs = 0
    orphans = 0
    text_hash_mismatches = 0
    role_alias_sets: dict[str, list[set[str]]] = {role: [] for role in role_counts}
    speakers: Counter[str] = Counter()
    if case_id in COMPLETE_CASES:
        joined = _load(TRANSFER_ROOT / f"{case_id}-primary" / "joined-role-records.json")
        role_counts = {key: int(joined.get("record_counts", {}).get(key, 0)) for key in role_counts}
        observations = joined.get("role_observations", {})
        for role in role_counts:
            for record in observations.get(role, []):
                declared_aliases = {str(alias) for alias in record.get("source_evidence_ids", [])}
                evidence_rows = record.get("source_evidence", [])
                row_aliases = {str(item.get("alias")) for item in evidence_rows}
                if declared_aliases != row_aliases:
                    raise R4ReplayError(f"role evidence identity drifted: {case_id}")
                role_alias_sets[role].append(declared_aliases)
                for evidence in evidence_rows:
                    alias = str(evidence.get("alias"))
                    refs += 1
                    locator = alias_by_id.get(alias)
                    if locator is None:
                        orphans += 1
                    else:
                        speakers[str(locator["speaker"])] += 1
                        observed_hash = hashlib.sha256(
                            str(evidence.get("text", "")).encode("utf-8")
                        ).hexdigest()
                        if observed_hash != locator["text_sha256"]:
                            text_hash_mismatches += 1
    elif case_id == ROLE_JOIN_FAILURE:
        result = _load(TRANSFER_ROOT / f"{case_id}-primary" / "result.json")
        for call in result.get("calls", []):
            compiled = call.get("compiled", {})
            for observation in compiled.get("observations", []):
                role = str(observation.get("role"))
                if role in role_counts:
                    role_counts[role] += 1
                    for evidence in observation.get("source_evidence", []):
                        alias = str(evidence.get("alias"))
                        role_alias_sets[role].append({alias})
                        refs += 1
                        locator = alias_by_id.get(alias)
                        if locator is None:
                            orphans += 1
                        else:
                            speakers[str(locator["speaker"])] += 1
                            observed_hash = hashlib.sha256(
                                str(evidence.get("text", "")).encode("utf-8")
                            ).hexdigest()
                            if observed_hash != locator["text_sha256"]:
                                text_hash_mismatches += 1
    if orphans or text_hash_mismatches:
        raise R4ReplayError(f"role source locator drifted: {case_id}")
    overlap_count = 0
    for record_sets in role_alias_sets.values():
        for index, left in enumerate(record_sets):
            overlap_count += sum(bool(left & right) for right in record_sets[index + 1 :])
    return role_counts, {
        "alias_count": len(aliases),
        "alias_turn_range": [min(item["turn_index"] for item in aliases), max(item["turn_index"] for item in aliases)],
        "alias_speaker_counts": dict(sorted(Counter(str(item["speaker"]) for item in aliases).items())),
        "admitted_role_source_reference_count": refs,
        "admitted_role_source_reference_speaker_counts": dict(sorted(speakers.items())),
        "orphan_role_source_reference_count": 0,
        "role_source_text_hash_mismatch_count": 0,
        "same_role_record_alias_overlap_pair_count": overlap_count,
        "semantic_grounding_inferred": False,
    }


def _diagnostic_by_id() -> dict[str, dict[str, Any]]:
    review = _load(DIAGNOSTIC_REVIEW)
    return {str(item["case_id"]): item for item in review.get("cases", [])}


def _first_gap(case_id: str, diagnostic: Mapping[str, Any] | None) -> dict[str, Any]:
    if case_id == ROLE_JOIN_FAILURE:
        return {
            "stage": "starting_role_custody_join",
            "kind": "custody_failure",
            "observation": "Starting output existed but was quarantined because component aliases did not satisfy the parent-record alias contract.",
            "semantic_cause_proven": False,
        }
    if case_id in TRANSPORT_FAILURES:
        return {
            "stage": "starting_role_transport",
            "kind": "provider_credit_envelope_failure",
            "observation": "The starting request stopped at HTTP 402 before semantic inference.",
            "semantic_cause_proven": False,
        }
    if diagnostic and diagnostic.get("stand_down_assessment") == "false_stand_down":
        return {
            "stage": "upstream_semantic_representation_before_deterministic_recall",
            "kind": "reviewed_false_stand_down",
            "observation": "Frozen diagnostic review found material pressure absent from the representation that reached controlled-mechanism routing.",
            "semantic_cause_proven": True,
            "review_limit": "Same-project diagnostic source review; not independent or cleanly blinded.",
        }
    if diagnostic:
        return {
            "stage": "none_observed_in_reviewed_path",
            "kind": "reviewed_stand_down_correct",
            "observation": "Frozen diagnostic review found the stand-down proportionate for this completed path.",
            "semantic_cause_proven": False,
        }
    return {
        "stage": "not_semantically_reviewed",
        "kind": "evidence_gap",
        "observation": "No frozen diagnostic source review exists for this case's semantic output.",
        "semantic_cause_proven": False,
    }


def _shared_inventory() -> list[dict[str, Any]]:
    records = []
    for path in SHARED_ARTIFACTS:
        if not path.is_file():
            raise R4ReplayError(f"missing shared artifact: {_relative(path)}")
        records.append(
            {
                "path": _relative(path),
                "sha256": _sha(path),
                "utf8_bytes": len(path.read_bytes()),
                "classifications": ["replayable", "shared", "review-only"],
                "content_copied": False,
            }
        )
    return records


def build() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest, review, preflight = _validate_frozen_inputs()
    source_review = {str(item["case_id"]): item for item in review["cases"]}
    preflight_by_id = {
        str(item["case_id"]): item
        for item in preflight["artifacts"]
        if item.get("split") == "transfer"
    }
    diagnostic_by_id = _diagnostic_by_id()
    receipt_by_id = {str(item["case_id"]): item for item in _load(RECEIPT_REPORT)["cases"]}
    case_ids = [str(item["case_id"]) for item in manifest["transfer_cases"]]
    discovered_paths = _discover_case_paths(case_ids)
    cases = []
    gap_cases = []
    total_inventory_records = 0
    unique_inventory_paths: set[str] = set()
    for source in manifest["transfer_cases"]:
        case_id = str(source["case_id"])
        role_counts, locator_metrics = _role_metrics(case_id)
        artifacts = _discover_case_artifacts(case_id, discovered_paths[case_id])
        total_inventory_records += len(artifacts)
        unique_inventory_paths.update(str(item["path"]) for item in artifacts)
        surfaces = _case_surfaces(case_id, role_counts)
        primary_dir = TRANSFER_ROOT / f"{case_id}-primary"
        primary_result = _load(primary_dir / "result.json")
        direct_candidates = int(primary_result.get("direct_candidate_count", 0))
        direct_reserve = int(primary_result.get("direct_reserve_count", 0))
        graph_candidates = int(primary_result.get("graph_candidate_count", 0))
        graph_reserve = int(primary_result.get("graph_reserve_count", 0))
        diagnostic = diagnostic_by_id.get(case_id)
        receipt = receipt_by_id[case_id]
        receipt_artifacts = [
            {
                "path": receipt["receipt_path"],
                "sha256": receipt["receipt_file_sha256"],
                "utf8_bytes": len((ROOT / receipt["receipt_path"]).read_bytes()),
                "format": "json",
                "classifications": ["replayable", "transfer"],
                "content_copied": False,
            },
            {
                "path": receipt["markdown_path"],
                "sha256": receipt["markdown_sha256"],
                "utf8_bytes": len((ROOT / receipt["markdown_path"]).read_bytes()),
                "format": "markdown",
                "classifications": ["replayable", "transfer"],
                "content_copied": False,
            },
        ]
        if any(_sha(ROOT / item["path"]) != item["sha256"] for item in receipt_artifacts):
            raise R4ReplayError(f"receipt custody drifted: {case_id}")
        case_record = {
            "case_id": case_id,
            "authoritative_source": {
                "path": source["path"],
                "sha256": source["sha256"],
                "utf8_bytes": len((ROOT / source["path"]).read_bytes()),
                "word_count": source["word_count"],
                "message_count": source["message_count"],
            },
            "expected_public_behavior": source_review[case_id]["expected_public_behavior"],
            "transfer_attempt_status": primary_result.get("status"),
            "evidence_partition": (
                "sealed_transfer_complete"
                if case_id in COMPLETE_CASES
                else "sealed_transfer_partial_or_failed"
            ),
            "source_locator_metrics": locator_metrics,
            "role_record_counts": role_counts,
            "fan_in_load": {
                "annotated_role_input_utf8_bytes": preflight_by_id[case_id]["annotated_input_utf8_bytes"],
                "source_alias_count": preflight_by_id[case_id]["evidence_alias_count"],
                "admitted_role_record_count": sum(role_counts.values()),
                "admitted_role_source_reference_count": locator_metrics["admitted_role_source_reference_count"],
                "unresolved_mechanism_id_count": len(primary_result.get("unresolved_mechanism_ids", [])),
                "direct_active_candidate_count": direct_candidates,
                "direct_reserve_candidate_count": direct_reserve,
                "graph_active_candidate_count": graph_candidates,
                "graph_reserve_candidate_count": graph_reserve,
                "interpretation": "load vector only; no direction of quality is inferred",
            },
            "surfaces": surfaces,
            "receipt_artifacts": receipt_artifacts,
            "relevant_artifact_count": len(artifacts),
            "relevant_artifacts": artifacts,
        }
        cases.append(case_record)
        gap_cases.append(
            {
                "case_id": case_id,
                "expected_public_behavior": source_review[case_id]["expected_public_behavior"],
                "transfer_attempt_status": primary_result.get("status"),
                "runtime_behavior": diagnostic.get("runtime_behavior") if diagnostic else None,
                "source_review_disposition": diagnostic.get("stand_down_assessment") if diagnostic else "not_reviewed",
                "material_concept_coverage": diagnostic.get("material_concept_coverage") if diagnostic else "not_reviewed",
                "surface_states": {key: value["state"] for key, value in surfaces.items()},
                "first_observable_gap": _first_gap(case_id, diagnostic),
                "evidence_limit": (
                    "Same-project diagnostic review, not independent or blinded."
                    if diagnostic
                    else "No semantic diagnosis is inferred from artifacts or source labels."
                ),
            }
        )
    inventory: dict[str, Any] = {
        "schema_version": "lolla.r4_corpus_replay_manifest.v1",
        "status": "provider_free_inventory_complete",
        "measurement_contract_path": _relative(MEASUREMENT_CONTRACT),
        "measurement_contract_sha256": _sha(MEASUREMENT_CONTRACT),
        "frozen_input_hashes": EXPECTED_INPUT_HASHES,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "case_count": len(cases),
        "case_artifact_record_count": total_inventory_records,
        "case_artifact_link_count": total_inventory_records,
        "unique_case_linked_json_artifact_count": len(unique_inventory_paths),
        "shared_artifacts": _shared_inventory(),
        "cases": cases,
        "inventory_method": {
            "case_relevance_rule": "Valid JSON under research/ or docs/evals/ whose bytes contain the exact case_id, excluding this R4 output root.",
            "authoritative_non_json_added": "Each source text and receipt markdown is represented through the frozen source/receipt reports; raw content is not copied.",
            "metadata_only": True,
            "private_provider_values_copied": False,
            "semantic_classification_by_keywords": False,
            "path_tags_are_discovery_metadata_not_semantic_judgments": True,
        },
        "non_claims": [
            "artifact presence is not semantic coverage",
            "valid source locator is not semantic grounding",
            "exposed artifacts are not transfer evidence",
            "missing contract surface is not an empty semantic finding",
        ],
    }
    inventory["result_sha256"] = value_sha256(inventory)
    gap_matrix: dict[str, Any] = {
        "schema_version": "lolla.r4_replay_gap_matrix.v1",
        "status": "provider_free_gap_matrix_complete",
        "source_inventory_result_sha256": inventory["result_sha256"],
        "provider_calls": 0,
        "summary": {
            "case_count": 12,
            "sealed_transfer_complete": 7,
            "role_join_failed": 1,
            "starting_transport_failed": 4,
            "diagnostically_reviewed": 7,
            "reviewed_false_stand_down": 2,
            "reviewed_correct_stand_down": 5,
            "distinct_unresolved_matter_contract_present": 0,
            "distinct_reopen_condition_contract_present": 0,
            "distinct_cross_thread_relationship_contract_present": 0,
            "graph_pressure_provider_calls": 0,
            "primary_graph_active_candidates": 0,
            "composite_quality_score": None,
        },
        "cases": gap_cases,
        "repeated_observable_gaps": [
            {
                "gap": "system-level semantic fan-in can silently omit a material thread before controlled-mechanism routing",
                "observed_cases": ["v1-case01-flood-infrastructure", "v1-case02-discharge-transport"],
                "evidence": "Frozen diagnostic source review identifies two false stand-downs whose missing pressure was absent upstream of deterministic recall.",
                "limit": "The diagnosis is same-project, diagnostic, and not cleanly blinded.",
            },
            {
                "gap": "unresolved matter, reopen condition, and cross-thread relationship have no distinct primary contract surface",
                "observed_cases": [item["case_id"] for item in manifest["transfer_cases"]],
                "evidence": "Interface availability fact across the twelve sealed inputs and outputs.",
                "limit": "Absence of a surface does not prove every conversation contains such semantics.",
            },
            {
                "gap": "transport credit envelope prevented inference",
                "observed_cases": sorted(TRANSPORT_FAILURES),
                "evidence": "Four preserved HTTP 402 failures before the starting read.",
                "limit": "Historical operability finding; no provider retry or budget change is authorized by R4.",
            },
        ],
        "non_claims": [
            "not a corpus score",
            "not a model comparison",
            "not a fresh holdout",
            "not an architecture authorization",
        ],
    }
    gap_matrix["result_sha256"] = value_sha256(gap_matrix)
    result: dict[str, Any] = {
        "schema_version": "lolla.r4_provider_free_replay_result.v1",
        "status": "r4_provider_free_replay_complete_one_next_repair_earned",
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "inventory_result_sha256": inventory["result_sha256"],
        "gap_matrix_result_sha256": gap_matrix["result_sha256"],
        "measurement_contract_sha256": _sha(MEASUREMENT_CONTRACT),
        "what_is_exactly_measurable": [
            "source and artifact custody",
            "completed, partial, failed, missing, empty, and not-applicable states",
            "explicit role labels and record counts",
            "source alias resolution, speaker, and turn locators",
            "fan-in byte and record vectors",
            "declared direct and graph routing activity",
        ],
        "what_still_requires_probabilistic_or_human_review": [
            "material conversation-thread coverage",
            "semantic role correctness",
            "temporal and speaker interpretation correctness",
            "cross-thread relationships",
            "false stand-down and over-fragmentation judgments",
            "whether pressure improves a future answer",
        ],
        "selected_next_repair": {
            "name": "missingness-aware system-level conversation-state fan-in contract",
            "scope": "Design one typed assembly boundary that preserves complementary provider-authored starting, current, qualification, unresolved-matter, reopen-condition, and relationship records with source locators and explicit missing, empty, partial, and failed states.",
            "expected_changed_measurement": "A downstream consumer can inspect every reader's explicit output and absence state without one missing read becoming stand-down evidence.",
            "deterministic_limits": [
                "do not fill a missing role",
                "do not infer semantic equivalence",
                "do not infer roles from time, keywords, or order",
                "do not decide model relevance or pressure",
            ],
            "implementation_authorized_by_this_result": False,
            "provider_call_authorized_by_this_result": False,
        },
        "repair_selection_reason": "Two reviewed false stand-downs share an upstream representation gap; the corpus also lacks distinct missingness-aware surfaces for unresolved and reopen semantics. A fan-in contract addresses observability and preservation without adding a brittle semantic gate.",
        "alternatives_not_selected": [
            "prompt tuning before system-level visibility exists",
            "new deterministic semantic gates",
            "graph changes before a fresh pressure consumer has been exercised",
            "provider retry of historical credit failures",
        ],
        "claims": [
            "The existing artifacts can audit custody and several mechanical representation properties.",
            "They cannot establish genuine real-user usefulness or overall answer quality.",
            "One bounded fan-in contract is earned as the next design task; no runtime implementation or model call is yet authorized.",
        ],
    }
    result["result_sha256"] = value_sha256(result)
    _write(INVENTORY_PATH, inventory)
    _write(GAP_MATRIX_PATH, gap_matrix)
    _write(RESULT_PATH, result)
    return validate()


def validate() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _validate_frozen_inputs()
    contract = _load(MEASUREMENT_CONTRACT)
    if (
        contract.get("status") != "frozen_provider_free_non_scalar_contract"
        or contract.get("aggregation", {}).get("composite_score") is not None
        or contract.get("budget", {}).get("provider_calls_authorized") != 0
        or len(contract.get("dimensions", [])) != 10
    ):
        raise R4ReplayError("measurement contract drifted")
    inventory = _load(INVENTORY_PATH)
    gap_matrix = _load(GAP_MATRIX_PATH)
    result = _load(RESULT_PATH)
    for value, field in (
        (inventory, "result_sha256"),
        (gap_matrix, "result_sha256"),
        (result, "result_sha256"),
    ):
        if value.get(field) != value_sha256(_without(value, field)):
            raise R4ReplayError(f"self-hash drifted: {value.get('schema_version')}")
    if (
        inventory.get("provider_calls") != 0
        or inventory.get("case_count") != 12
        or inventory.get("measurement_contract_sha256") != _sha(MEASUREMENT_CONTRACT)
        or gap_matrix.get("source_inventory_result_sha256") != inventory["result_sha256"]
        or result.get("inventory_result_sha256") != inventory["result_sha256"]
        or result.get("gap_matrix_result_sha256") != gap_matrix["result_sha256"]
        or result.get("provider_calls") != 0
        or result.get("selected_next_repair", {}).get("implementation_authorized_by_this_result") is not False
        or result.get("selected_next_repair", {}).get("provider_call_authorized_by_this_result") is not False
    ):
        raise R4ReplayError("R4 output boundary drifted")
    cases = inventory.get("cases", [])
    if len(cases) != 12:
        raise R4ReplayError("inventory case count drifted")
    discovered_paths = _discover_case_paths([str(case.get("case_id")) for case in cases])
    for case in cases:
        case_id = str(case.get("case_id"))
        artifacts = case.get("relevant_artifacts", [])
        recorded_paths = {str(item.get("path")) for item in artifacts}
        current_paths = {_relative(path) for path in discovered_paths[case_id]}
        if (
            set(case.get("surfaces", {})) != set(REQUIRED_SURFACES)
            or case.get("source_locator_metrics", {}).get("orphan_role_source_reference_count") != 0
            or case.get("source_locator_metrics", {}).get("role_source_text_hash_mismatch_count") != 0
            or any(artifact.get("content_copied") is not False for artifact in artifacts)
            or recorded_paths != current_paths
        ):
            raise R4ReplayError(f"case inventory drifted: {case_id}")
        for artifact in [*artifacts, *case.get("receipt_artifacts", [])]:
            path = ROOT / str(artifact.get("path"))
            if (
                not path.is_file()
                or _sha(path) != artifact.get("sha256")
                or len(path.read_bytes()) != artifact.get("utf8_bytes")
            ):
                raise R4ReplayError(f"artifact custody drifted: {artifact.get('path')}")
    if inventory.get("shared_artifacts") != _shared_inventory():
        raise R4ReplayError("shared artifact inventory drifted")
    return inventory, gap_matrix, result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    inventory, gaps, result = validate() if args.validate_only else build()
    print(
        json.dumps(
            {
                "status": result["status"],
                "case_count": inventory["case_count"],
                "artifact_records": inventory["case_artifact_record_count"],
                "unique_json_artifacts": inventory["unique_case_linked_json_artifact_count"],
                "reviewed_false_stand_down": gaps["summary"]["reviewed_false_stand_down"],
                "provider_calls": result["provider_calls"],
                "result_sha256": result["result_sha256"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
