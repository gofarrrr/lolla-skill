#!/usr/bin/env python3
"""Score exact-span semantic coverage both within and across reader families."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


SCHEMA_VERSION = "lolla.core_semantic_system_coverage.v0"
DEFAULT_MANIFEST = (
    REPO_ROOT / "tests/fixtures/core_semantic_validation/corpus-v0/manifest.json"
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
    observation: Mapping[str, Any],
) -> set[str]:
    return {
        family
        for family, items in families.items()
        if any(
            _matches(item, evidence)
            for item in items
            for evidence in observation.get("evidence", [])
        )
    }


def _metric_summary(
    recovered_sets: list[set[str]],
    *,
    observation_ids: set[str],
) -> dict[str, Any]:
    stable = set.intersection(*recovered_sets) if recovered_sets else set()
    ever = set.union(*recovered_sets) if recovered_sets else set()
    opportunities = len(observation_ids) * len(recovered_sets)
    recovered = sum(len(items) for items in recovered_sets)
    return {
        "weighted_recall": recovered / opportunities if opportunities else 0.0,
        "stable_observation_ids": sorted(stable),
        "ever_observation_ids": sorted(ever),
        "never_observation_ids": sorted(observation_ids - ever),
        "observation_count": len(observation_ids),
        "run_count": len(recovered_sets),
    }


def build_system_coverage(
    *,
    manifest_path: Path,
    artifact_root: Path,
    selected_case_ids: set[str] | None = None,
) -> dict[str, Any]:
    from engine.system_b.core_semantic_comparison import (
        _FAMILY_DIMENSIONS,
        _parse_turns,
        _shadow_run,
    )

    manifest = _load_json(manifest_path)
    cases = [
        case
        for case in manifest["cases"]
        if not selected_case_ids or case["case_id"] in selected_case_ids
    ]
    found_ids = {case["case_id"] for case in cases}
    if selected_case_ids and found_ids != selected_case_ids:
        raise ValueError(
            f"unknown case ids: {sorted(selected_case_ids - found_ids)}"
        )

    per_case: list[dict[str, Any]] = []
    all_system_sets: list[set[str]] = []
    all_aligned_sets: list[set[str]] = []
    all_observation_ids: set[str] = set()
    dimension_opportunities: dict[str, int] = defaultdict(int)
    dimension_system_recovered: dict[str, int] = defaultdict(int)
    dimension_aligned_recovered: dict[str, int] = defaultdict(int)
    dimension_observations: dict[str, set[str]] = defaultdict(set)
    rescue_family_counts: Counter[str] = Counter()
    cross_family_rescue_count = 0

    for case in cases:
        case_id = str(case["case_id"])
        conversation_path = REPO_ROOT / case["source_path"]
        gold_path = REPO_ROOT / case["gold_path"]
        gold = _load_json(gold_path)
        observations = [
            item
            for item in gold.get("required_observations", [])
            if isinstance(item, dict)
        ]
        observation_ids = {
            str(observation["observation_id"]) for observation in observations
        }
        all_observation_ids.update(
            f"{case_id}:{observation_id}" for observation_id in observation_ids
        )
        turns = _parse_turns(conversation_path.read_text(encoding="utf-8"))
        artifact_paths = [
            artifact_root / case_id / f"shadow-{repeat:02d}.json"
            for repeat in range(1, 4)
        ]
        missing = [str(path) for path in artifact_paths if not path.is_file()]
        if missing:
            raise ValueError(f"missing shadow artifacts for {case_id}: {missing}")
        runs = [_shadow_run(path, turns=turns) for path in artifact_paths]
        case_system_sets: list[set[str]] = []
        case_aligned_sets: list[set[str]] = []
        per_run: list[dict[str, Any]] = []
        for run_index, run in enumerate(runs, 1):
            system_recovered: set[str] = set()
            aligned_recovered: set[str] = set()
            rescue_records: list[dict[str, Any]] = []
            for observation in observations:
                observation_id = str(observation["observation_id"])
                dimension = str(observation["dimension"])
                qualified_id = f"{case_id}:{observation_id}"
                matching = _matching_families(run["families"], observation)
                aligned_families = {
                    family
                    for family in matching
                    if dimension in _FAMILY_DIMENSIONS.get(family, set())
                }
                dimension_opportunities[dimension] += 1
                dimension_observations[dimension].add(qualified_id)
                if matching:
                    system_recovered.add(observation_id)
                    dimension_system_recovered[dimension] += 1
                if aligned_families:
                    aligned_recovered.add(observation_id)
                    dimension_aligned_recovered[dimension] += 1
                if matching and not aligned_families:
                    cross_family_rescue_count += 1
                    rescue_family_counts.update(matching)
                    rescue_records.append(
                        {
                            "observation_id": observation_id,
                            "dimension": dimension,
                            "matching_families": sorted(matching),
                        }
                    )
            case_system_sets.append(system_recovered)
            case_aligned_sets.append(aligned_recovered)
            all_system_sets.append(
                {f"{case_id}:{item}" for item in system_recovered}
            )
            all_aligned_sets.append(
                {f"{case_id}:{item}" for item in aligned_recovered}
            )
            per_run.append(
                {
                    "run": run_index,
                    "artifact_path": str(artifact_paths[run_index - 1]),
                    "system_recovered_observation_ids": sorted(system_recovered),
                    "family_aligned_observation_ids": sorted(aligned_recovered),
                    "cross_family_rescues": rescue_records,
                }
            )
        per_case.append(
            {
                "case_id": case_id,
                "gold_observation_count": len(observation_ids),
                "system_level": _metric_summary(
                    case_system_sets,
                    observation_ids=observation_ids,
                ),
                "family_aligned": _metric_summary(
                    case_aligned_sets,
                    observation_ids=observation_ids,
                ),
                "per_run": per_run,
            }
        )

    # Stable corpus observations require stability within their own case, not
    # intersection across unrelated cases.
    system_stable = {
        f"{item['case_id']}:{observation_id}"
        for item in per_case
        for observation_id in item["system_level"]["stable_observation_ids"]
    }
    aligned_stable = {
        f"{item['case_id']}:{observation_id}"
        for item in per_case
        for observation_id in item["family_aligned"]["stable_observation_ids"]
    }
    opportunities = sum(
        item["gold_observation_count"] * item["system_level"]["run_count"]
        for item in per_case
    )
    system_recovered_count = sum(
        len(run["system_recovered_observation_ids"])
        for case in per_case
        for run in case["per_run"]
    )
    aligned_recovered_count = sum(
        len(run["family_aligned_observation_ids"])
        for case in per_case
        for run in case["per_run"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "corpus_id": manifest["corpus_id"],
        "artifact_root": str(artifact_root),
        "case_count": len(per_case),
        "gold_observation_count": len(all_observation_ids),
        "run_opportunity_count": opportunities,
        "system_level": {
            "weighted_recall": (
                system_recovered_count / opportunities if opportunities else 0.0
            ),
            "stable_observation_count": len(system_stable),
            "stable_observation_ids": sorted(system_stable),
        },
        "family_aligned": {
            "weighted_recall": (
                aligned_recovered_count / opportunities if opportunities else 0.0
            ),
            "stable_observation_count": len(aligned_stable),
            "stable_observation_ids": sorted(aligned_stable),
        },
        "cross_family": {
            "rescued_observation_run_count": cross_family_rescue_count,
            "rescue_family_counts": dict(sorted(rescue_family_counts.items())),
            "weighted_recall_delta": (
                (system_recovered_count - aligned_recovered_count) / opportunities
                if opportunities
                else 0.0
            ),
        },
        "dimensions": {
            dimension: {
                "observation_count": len(dimension_observations[dimension]),
                "run_opportunity_count": dimension_opportunities[dimension],
                "system_weighted_recall": (
                    dimension_system_recovered[dimension]
                    / dimension_opportunities[dimension]
                ),
                "family_aligned_weighted_recall": (
                    dimension_aligned_recovered[dimension]
                    / dimension_opportunities[dimension]
                ),
                "cross_family_delta": (
                    (dimension_system_recovered[dimension]
                    - dimension_aligned_recovered[dimension])
                    / dimension_opportunities[dimension]
                ),
            }
            for dimension in sorted(dimension_opportunities)
        },
        "per_case": per_case,
        "non_claims": [
            "cross_family_recovery_is_not_proof_of_correct_family_assignment",
            "exact_span_recovery_is_not_reasoning_quality",
            "system_coverage_does_not_replace_temporal_coverage",
            "three_repeats_are_not_production_reliability_proof",
        ],
    }


def render_markdown(result: Mapping[str, Any]) -> str:
    system = result["system_level"]
    aligned = result["family_aligned"]
    cross = result["cross_family"]
    lines = [
        "# Core Semantic System-Level Coverage",
        "",
        f"Corpus: `{result['corpus_id']}`  ",
        f"Cases: {result['case_count']}  ",
        f"Gold observations: {result['gold_observation_count']}",
        "",
        "| measure | family-aligned | system-level |",
        "| --- | ---: | ---: |",
        f"| weighted exact-span recall | {aligned['weighted_recall']:.3f} | {system['weighted_recall']:.3f} |",
        f"| stable observations | {aligned['stable_observation_count']} | {system['stable_observation_count']} |",
        "",
        f"Cross-family rescue opportunities: {cross['rescued_observation_run_count']}",
        "",
        "## Dimensions",
        "",
        "| dimension | family-aligned | system-level | delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for dimension, item in result["dimensions"].items():
        lines.append(
            f"| `{dimension}` | {item['family_aligned_weighted_recall']:.3f} | "
            f"{item['system_weighted_recall']:.3f} | {item['cross_family_delta']:.3f} |"
        )
    lines.extend(
        [
            "",
            "Family-aligned coverage diagnoses reader placement. System-level coverage asks whether the semantic packet preserved the source observation anywhere. Neither is a quality score.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--md-out", required=True, type=Path)
    args = parser.parse_args()

    result = build_system_coverage(
        manifest_path=args.manifest.expanduser().resolve(),
        artifact_root=args.artifact_root.expanduser().resolve(),
        selected_case_ids=set(args.case_ids or []) or None,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(result), encoding="utf-8")
    print(f"System coverage JSON written to {args.json_out}")
    print(f"System coverage Markdown written to {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
