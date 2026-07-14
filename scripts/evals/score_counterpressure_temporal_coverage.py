#!/usr/bin/env python3
"""Deterministically score first-introduction and concept coverage.

All semantic equivalence is declared in a frozen, researcher-reviewed contract.
This scorer only validates exact source custody and matches declared spans.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


RESULT_SCHEMA_VERSION = "lolla.counterpressure_temporal_coverage_result.v0"


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _turn_map(source_path: Path) -> dict[tuple[int, str], str]:
    from engine.system_b.conversation_loader import _parse_turns

    return {
        (turn.turn_index, turn.speaker): turn.text
        for turn in _parse_turns(source_path.read_text(encoding="utf-8"))
    }


def _validate_evidence(
    evidence: Mapping[str, Any],
    *,
    turns: Mapping[tuple[int, str], str],
) -> None:
    key = (int(evidence.get("turn_index") or 0), str(evidence.get("speaker") or ""))
    quote = str(evidence.get("quote") or "")
    turn = turns.get(key)
    if not quote or turn is None or quote not in turn:
        raise ValueError(f"declared evidence is not an exact source span: {evidence}")


def _event_matches(
    event: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> bool:
    from engine.system_b.core_semantic_comparison import _quotes_overlap

    source = event.get("source") if isinstance(event.get("source"), Mapping) else {}
    return (
        int(source.get("turn_index") or 0) == int(evidence.get("turn_index") or -1)
        and str(source.get("speaker") or "") == str(evidence.get("speaker") or "")
        and _quotes_overlap(
            str(source.get("quote") or ""),
            str(evidence.get("quote") or ""),
        )
    )


def _event_is_exact_source(
    event: Mapping[str, Any],
    *,
    turns: Mapping[tuple[int, str], str],
) -> bool:
    source = event.get("source") if isinstance(event.get("source"), Mapping) else {}
    key = (int(source.get("turn_index") or 0), str(source.get("speaker") or ""))
    quote = str(source.get("quote") or "")
    turn = turns.get(key)
    return bool(quote and turn is not None and quote in turn)


def _recovered(
    events: list[Mapping[str, Any]],
    evidence: list[Mapping[str, Any]],
) -> bool:
    return any(
        _event_matches(event, span)
        for event in events
        for span in evidence
    )


def _artifact_events(
    artifact: Mapping[str, Any],
    *,
    family_scope: str,
) -> list[dict[str, Any]]:
    semantic = artifact.get("semantic_events", {})
    if not isinstance(semantic, Mapping):
        return []
    if family_scope == "user_pressure_only":
        families = ["user_pressure_events"]
    elif family_scope == "all_source_grounded_families":
        families = sorted(str(family) for family in semantic)
    else:
        raise ValueError(f"unsupported family scope: {family_scope}")
    events: list[dict[str, Any]] = []
    for family in families:
        raw_items = semantic.get(family, [])
        if not isinstance(raw_items, list):
            continue
        for item in raw_items:
            if not isinstance(item, Mapping) or not isinstance(
                item.get("source"), Mapping
            ):
                continue
            event = dict(item)
            event["_evaluation_family"] = family
            events.append(event)
    return events


def _matching_families(
    events: list[Mapping[str, Any]],
    evidence: list[Mapping[str, Any]],
) -> list[str]:
    return sorted(
        {
            str(event.get("_evaluation_family") or "unknown")
            for event in events
            if any(_event_matches(event, span) for span in evidence)
        }
    )


def _metric_summary(
    per_run_sets: list[set[str]],
    *,
    observation_count: int,
) -> dict[str, Any]:
    stable = set.intersection(*per_run_sets) if per_run_sets else set()
    ever = set.union(*per_run_sets) if per_run_sets else set()
    opportunities = observation_count * len(per_run_sets)
    recovered = sum(len(items) for items in per_run_sets)
    return {
        "weighted_recall": recovered / opportunities if opportunities else 0.0,
        "stable_observation_ids": sorted(stable),
        "ever_observation_ids": sorted(ever),
        "never_observation_count": observation_count - len(ever),
        "observation_count": observation_count,
    }


def build_temporal_coverage_result(
    *,
    contract_path: Path,
    case_id: str,
    arm_name: str,
    artifact_paths: list[Path],
    family_scope: str = "user_pressure_only",
) -> dict[str, Any]:
    contract = _load_json(contract_path)
    observations = [
        item
        for item in contract.get("observations", [])
        if isinstance(item, dict) and item.get("case_id") == case_id
    ]
    if not observations:
        raise ValueError(f"contract has no observations for case: {case_id}")
    source_paths = {
        REPO_ROOT / str(observation["source_path"])
        for observation in observations
    }
    if len(source_paths) != 1:
        raise ValueError("one case must resolve to exactly one source file")
    source_path = next(iter(source_paths))
    expected_hashes = {
        str(observation["source_file_sha256"])
        for observation in observations
    }
    if expected_hashes != {_sha256(source_path)}:
        raise ValueError("source hash does not match the temporal contract")
    turns = _turn_map(source_path)
    for observation in observations:
        for field in (
            "first_introduction_evidence",
            "later_strengthening_evidence",
        ):
            for evidence in observation.get(field, []):
                _validate_evidence(evidence, turns=turns)

    first_sets: list[set[str]] = []
    concept_sets: list[set[str]] = []
    later_sets: list[set[str]] = []
    per_run: list[dict[str, Any]] = []
    exact_event_count = 0
    event_count = 0
    for path in artifact_paths:
        artifact = _load_json(path)
        events = _artifact_events(artifact, family_scope=family_scope)
        event_count += len(events)
        exact_event_count += sum(
            _event_is_exact_source(event, turns=turns) for event in events
        )
        first: set[str] = set()
        concept: set[str] = set()
        later: set[str] = set()
        matching_families: dict[str, dict[str, list[str]]] = {}
        for observation in observations:
            observation_id = str(observation["observation_id"])
            first_evidence = list(observation.get("first_introduction_evidence", []))
            later_evidence = list(observation.get("later_strengthening_evidence", []))
            if _recovered(events, first_evidence):
                first.add(observation_id)
            if _recovered(events, first_evidence + later_evidence):
                concept.add(observation_id)
            if _recovered(events, later_evidence):
                later.add(observation_id)
            matching_families[observation_id] = {
                "first_introduction": _matching_families(
                    events, first_evidence
                ),
                "concept": _matching_families(
                    events, first_evidence + later_evidence
                ),
                "later_strengthening": _matching_families(
                    events, later_evidence
                ),
            }
        first_sets.append(first)
        concept_sets.append(concept)
        later_sets.append(later)
        per_run.append(
            {
                "artifact_path": str(path),
                "artifact_sha256": _sha256(path),
                "selected_event_count": len(events),
                "first_introduction_observation_ids": sorted(first),
                "concept_observation_ids": sorted(concept),
                "later_strengthening_observation_ids": sorted(later),
                "matching_families_by_observation": matching_families,
            }
        )

    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "evaluation_status": contract["current_artifact_use"],
        "contract_id": contract["contract_id"],
        "contract_sha256": _sha256(contract_path),
        "case_id": case_id,
        "arm_name": arm_name,
        "family_scope": family_scope,
        "run_count": len(artifact_paths),
        "source": {
            "path": str(source_path.relative_to(REPO_ROOT)),
            "sha256": _sha256(source_path),
        },
        "metrics": {
            "first_introduction_coverage": _metric_summary(
                first_sets, observation_count=len(observations)
            ),
            "concept_coverage": _metric_summary(
                concept_sets, observation_count=len(observations)
            ),
            "later_strengthening_coverage": _metric_summary(
                later_sets, observation_count=len(observations)
            ),
            "exact_source_validity": (
                exact_event_count / event_count if event_count else 0.0
            ),
            "selected_event_count": event_count,
        },
        "per_run": per_run,
        "non_claims": [
            "diagnostic_rescore_does_not_change_prior_gate_result",
            "concept_coverage_does_not_substitute_for_first_introduction_coverage",
            "declared_span_overlap_is_not_semantic_truth",
        ],
    }


def render_markdown(result: Mapping[str, Any]) -> str:
    metrics = result["metrics"]
    lines = [
        "# Counter-Pressure Temporal Coverage",
        "",
        f"Case: `{result['case_id']}`  ",
        f"Arm: `{result['arm_name']}`  ",
        f"Status: `{result['evaluation_status']}`",
        "",
        "| metric | weighted recall | stable |",
        "| --- | ---: | ---: |",
    ]
    for name in (
        "first_introduction_coverage",
        "concept_coverage",
        "later_strengthening_coverage",
    ):
        metric = metrics[name]
        lines.append(
            f"| `{name}` | {metric['weighted_recall']:.3f} | "
            f"{len(metric['stable_observation_ids'])} / {metric['observation_count']} |"
        )
    lines.extend(
        [
            "",
            f"Exact-source validity: {metrics['exact_source_validity']:.3f}",
            "",
            "This diagnostic rescore does not change the prior locked gate result.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--arm-name", required=True)
    parser.add_argument("--artifact", required=True, action="append", type=Path)
    parser.add_argument(
        "--family-scope",
        choices=["user_pressure_only", "all_source_grounded_families"],
        default="user_pressure_only",
    )
    parser.add_argument("--json-out", required=True, type=Path)
    parser.add_argument("--md-out", required=True, type=Path)
    args = parser.parse_args()

    result = build_temporal_coverage_result(
        contract_path=args.contract.expanduser().resolve(),
        case_id=args.case_id,
        arm_name=args.arm_name,
        artifact_paths=[path.expanduser().resolve() for path in args.artifact],
        family_scope=args.family_scope,
    )
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.md_out.write_text(render_markdown(result), encoding="utf-8")
    print(f"Temporal coverage JSON written to {args.json_out}")
    print(f"Temporal coverage Markdown written to {args.md_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
