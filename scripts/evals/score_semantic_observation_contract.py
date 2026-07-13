#!/usr/bin/env python3
"""Score reviewed semantic observations by concept, role, and temporal need."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


SCHEMA_VERSION = "lolla.semantic_observation_contract_result.v0"
DEFAULT_CONTRACT = (
    REPO_ROOT
    / "research/core-semantic-observation-contract-v1-2026-07-10/semantic-observation-contract.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _matches(item: Mapping[str, Any], evidence: Mapping[str, Any]) -> bool:
    from engine.system_b.core_semantic_comparison import _quotes_overlap

    return (
        item.get("grounding") == "span"
        and int(item.get("turn_index") or 0)
        == int(evidence.get("turn_index") or -1)
        and str(item.get("speaker") or "") == str(evidence.get("speaker") or "")
        and _quotes_overlap(
            str(item.get("quote") or ""),
            str(evidence.get("quote") or ""),
        )
    )


def _matching_families(
    families: Mapping[str, list[dict[str, Any]]],
    evidence: Mapping[str, Any],
) -> set[str]:
    return {
        family
        for family, items in families.items()
        if any(_matches(item, evidence) for item in items)
    }


def _summary(
    sets: list[set[str]],
    *,
    observation_ids: set[str],
) -> dict[str, Any]:
    stable = set.intersection(*sets) if sets else set()
    ever = set.union(*sets) if sets else set()
    opportunities = len(observation_ids) * len(sets)
    recovered = sum(len(items) for items in sets)
    return {
        "weighted_recall": recovered / opportunities if opportunities else 0.0,
        "stable_observation_ids": sorted(stable),
        "ever_observation_ids": sorted(ever),
        "never_observation_ids": sorted(observation_ids - ever),
        "observation_count": len(observation_ids),
        "run_count": len(sets),
    }


def build_contract_result(
    *,
    contract_path: Path,
    artifact_root: Path,
    reviewed_only: bool = True,
) -> dict[str, Any]:
    from engine.system_b.core_semantic_comparison import _parse_turns, _shadow_run

    contract = _load_json(contract_path)
    observations = [
        item
        for item in contract.get("observations", [])
        if isinstance(item, dict)
        and (
            not reviewed_only
            or item.get("review_status") == "source_reviewed"
        )
    ]
    if not observations:
        raise ValueError("semantic observation contract has no selected observations")
    by_case: dict[str, list[dict[str, Any]]] = {}
    for observation in observations:
        by_case.setdefault(str(observation["case_id"]), []).append(observation)

    per_case: list[dict[str, Any]] = []
    concept_any_sets: list[set[str]] = []
    concept_role_sets: list[set[str]] = []
    first_sets: list[set[str]] = []
    later_sets: list[set[str]] = []
    audit_sets: list[set[str]] = []
    observation_ids = {
        str(observation["qualified_observation_id"])
        for observation in observations
    }
    first_required_ids = {
        str(observation["qualified_observation_id"])
        for observation in observations
        if any(
            evidence.get("temporal_role") == "first_introduction"
            for evidence in observation.get("evidence", [])
        )
    }
    later_required_ids = {
        str(observation["qualified_observation_id"])
        for observation in observations
        if any(
            evidence.get("temporal_role") == "later_strengthening"
            for evidence in observation.get("evidence", [])
        )
    }
    for case_id, case_observations in sorted(by_case.items()):
        source_path = REPO_ROOT / case_observations[0]["source"]["source_path"]
        turns = _parse_turns(source_path.read_text(encoding="utf-8"))
        artifact_paths = [
            artifact_root / case_id / f"shadow-{repeat:02d}.json"
            for repeat in range(1, 4)
        ]
        missing = [str(path) for path in artifact_paths if not path.is_file()]
        if missing:
            raise ValueError(f"missing artifacts for {case_id}: {missing}")
        runs = [_shadow_run(path, turns=turns) for path in artifact_paths]
        case_runs: list[dict[str, Any]] = []
        for run_index, run in enumerate(runs, 1):
            concept_any: set[str] = set()
            concept_role: set[str] = set()
            first: set[str] = set()
            later: set[str] = set()
            audit: set[str] = set()
            evidence_matches: dict[str, list[dict[str, Any]]] = {}
            for observation in case_observations:
                qualified_id = str(observation["qualified_observation_id"])
                per_evidence: list[dict[str, Any]] = []
                for evidence in observation.get("evidence", []):
                    matching = _matching_families(run["families"], evidence)
                    acceptable = set(evidence.get("acceptable_families", []))
                    acceptable_matching = matching & acceptable
                    per_evidence.append(
                        {
                            "evidence_id": evidence["evidence_id"],
                            "temporal_role": evidence["temporal_role"],
                            "matching_families": sorted(matching),
                            "acceptable_matching_families": sorted(
                                acceptable_matching
                            ),
                        }
                    )
                evidence_matches[qualified_id] = per_evidence
                if any(item["matching_families"] for item in per_evidence):
                    concept_any.add(qualified_id)
                if any(
                    item["acceptable_matching_families"] for item in per_evidence
                ):
                    concept_role.add(qualified_id)
                first_items = [
                    item
                    for item in per_evidence
                    if item["temporal_role"] == "first_introduction"
                ]
                later_items = [
                    item
                    for item in per_evidence
                    if item["temporal_role"] == "later_strengthening"
                ]
                if first_items and any(
                    item["acceptable_matching_families"] for item in first_items
                ):
                    first.add(qualified_id)
                if later_items and any(
                    item["acceptable_matching_families"] for item in later_items
                ):
                    later.add(qualified_id)
                required_items = first_items + later_items
                if required_items and all(
                    item["acceptable_matching_families"] for item in required_items
                ):
                    audit.add(qualified_id)
            concept_any_sets.append(concept_any)
            concept_role_sets.append(concept_role)
            first_sets.append(first)
            later_sets.append(later)
            audit_sets.append(audit)
            case_runs.append(
                {
                    "run": run_index,
                    "artifact_path": str(artifact_paths[run_index - 1]),
                    "concept_anywhere_observation_ids": sorted(concept_any),
                    "concept_acceptable_role_observation_ids": sorted(concept_role),
                    "first_introduction_observation_ids": sorted(first),
                    "later_strengthening_observation_ids": sorted(later),
                    "audit_complete_observation_ids": sorted(audit),
                    "evidence_matches": evidence_matches,
                }
            )
        per_case.append(
            {
                "case_id": case_id,
                "observation_count": len(case_observations),
                "runs": case_runs,
            }
        )

    # Each observation belongs to one case, but the flat run lists contain
    # unrelated cases. Aggregate counts directly and compute stable IDs per
    # case to avoid intersecting unrelated observations.
    def aggregate(
        field: str,
        *,
        eligible_observation_ids: set[str] = observation_ids,
    ) -> dict[str, Any]:
        opportunities = len(eligible_observation_ids) * 3
        recovered = sum(
            len(set(run[field]) & eligible_observation_ids)
            for case in per_case
            for run in case["runs"]
        )
        stable = {
            observation_id
            for case in per_case
            for observation_id in set.intersection(
                *(set(run[field]) for run in case["runs"])
            )
            if observation_id in eligible_observation_ids
        }
        ever = {
            observation_id
            for case in per_case
            for run in case["runs"]
            for observation_id in run[field]
            if observation_id in eligible_observation_ids
        }
        return {
            "weighted_recall": recovered / opportunities if opportunities else 0.0,
            "stable_observation_ids": sorted(stable),
            "ever_observation_ids": sorted(ever),
            "never_observation_ids": sorted(eligible_observation_ids - ever),
            "observation_count": len(eligible_observation_ids),
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "contract_path": str(contract_path),
        "contract_status": contract["contract_status"],
        "reviewed_only": reviewed_only,
        "artifact_root": str(artifact_root),
        "case_count": len(by_case),
        "observation_count": len(observations),
        "metrics": {
            "reasoning_concept_anywhere": aggregate(
                "concept_anywhere_observation_ids"
            ),
            "reasoning_concept_acceptable_role": aggregate(
                "concept_acceptable_role_observation_ids"
            ),
            "audit_first_introduction": aggregate(
                "first_introduction_observation_ids",
                eligible_observation_ids=first_required_ids,
            ),
            "audit_later_strengthening": aggregate(
                "later_strengthening_observation_ids",
                eligible_observation_ids=later_required_ids,
            ),
            "audit_temporal_complete": aggregate(
                "audit_complete_observation_ids"
            ),
        },
        "per_case": per_case,
        "non_claims": [
            "reviewed_subset_is_not_full_corpus_quality",
            "concept_anywhere_does_not_prove_acceptable_role",
            "acceptable_role_does_not_prove_temporal_completeness",
            "contract_scoring_does_not_change_prior_results",
        ],
    }


def render_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Semantic Observation Contract Result",
        "",
        f"Reviewed observations: {result['observation_count']} across {result['case_count']} cases",
        "",
        "| capability | weighted recall | stable |",
        "| --- | ---: | ---: |",
    ]
    for name, metric in result["metrics"].items():
        lines.append(
            f"| `{name}` | {metric['weighted_recall']:.3f} | "
            f"{len(metric['stable_observation_ids'])} / {metric['observation_count']} |"
        )
    lines.extend(
        [
            "",
            "This reviewed subset is a prospective ontology check, not a full-corpus quality score.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--include-pending", action="store_true")
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--md-out", required=True, type=Path)
    args = parser.parse_args()

    result = build_contract_result(
        contract_path=args.contract.expanduser().resolve(),
        artifact_root=args.artifact_root.expanduser().resolve(),
        reviewed_only=not args.include_pending,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(result), encoding="utf-8")
    print(f"Observation contract JSON written to {args.json_out}")
    print(f"Observation contract Markdown written to {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
