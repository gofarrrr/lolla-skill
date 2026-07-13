#!/usr/bin/env python3
"""Build the prospective corpus-wide semantic observation contract scaffold."""
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


SCHEMA_VERSION = "lolla.semantic_observation_contract.v1"
DEFAULT_MANIFEST = (
    REPO_ROOT / "tests/fixtures/core_semantic_validation/corpus-v0/manifest.json"
)
DEFAULT_OVERRIDES = (
    REPO_ROOT
    / "research/core-semantic-observation-contract-v1-2026-07-10/reviewed-overrides.json"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "research/core-semantic-observation-contract-v1-2026-07-10/semantic-observation-contract.json"
)


_PRIMARY_FAMILIES_BY_DIMENSION = {
    "operative_question": ["question_events"],
    "user_corrections_and_pressure": ["user_pressure_events"],
    "constraints_and_options": ["live_constraint_events", "option_events"],
    "uncertainty_and_evidence_boundaries": ["evidence_boundary_events"],
    "assistant_positions_and_revisions": ["assistant_stance_events"],
    "dropped_or_under_carried_threads": ["dropped_thread_events"],
}


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
    qualified_observation_id: str,
) -> None:
    key = (
        int(evidence.get("turn_index") or 0),
        str(evidence.get("speaker") or ""),
    )
    quote = str(evidence.get("quote") or "")
    turn = turns.get(key)
    if not quote or turn is None or quote not in turn:
        raise ValueError(
            f"evidence is not an exact source span for "
            f"{qualified_observation_id}: {evidence}"
        )


def _inherited_evidence(
    raw: Mapping[str, Any],
    *,
    dimension: str,
    index: int,
) -> dict[str, Any]:
    return {
        "evidence_id": f"provisional_gold_{index:02d}",
        "turn_index": int(raw.get("turn_index") or 0),
        "speaker": str(raw.get("speaker") or ""),
        "quote": str(raw.get("quote") or ""),
        "temporal_role": "not_source_reviewed",
        "semantic_roles": [],
        "acceptable_families": list(
            _PRIMARY_FAMILIES_BY_DIMENSION.get(dimension, [])
        ),
    }


def build_contract(
    *,
    manifest_path: Path,
    overrides_path: Path,
) -> dict[str, Any]:
    manifest = _load_json(manifest_path)
    overrides_payload = _load_json(overrides_path)
    overrides = overrides_payload.get("observations", {})
    if not isinstance(overrides, dict):
        raise ValueError("review overrides must be an observation mapping")

    observations: list[dict[str, Any]] = []
    seen_overrides: set[str] = set()
    case_sources: dict[str, dict[str, str]] = {}
    for case in manifest["cases"]:
        case_id = str(case["case_id"])
        source_path = REPO_ROOT / case["source_path"]
        gold_path = REPO_ROOT / case["gold_path"]
        if _sha256(source_path) != case["source_file_sha256"]:
            raise ValueError(f"source hash drifted: {case_id}")
        turns = _turn_map(source_path)
        gold = _load_json(gold_path)
        case_sources[case_id] = {
            "source_path": str(source_path.relative_to(REPO_ROOT)),
            "source_sha256": _sha256(source_path),
            "gold_path": str(gold_path.relative_to(REPO_ROOT)),
            "gold_sha256": _sha256(gold_path),
            "gold_annotation_status": str(gold.get("annotation_status") or ""),
        }
        for raw_observation in gold.get("required_observations", []):
            if not isinstance(raw_observation, dict):
                continue
            observation_id = str(raw_observation["observation_id"])
            qualified_id = f"{case_id}:{observation_id}"
            dimension = str(raw_observation["dimension"])
            override = overrides.get(qualified_id)
            if override is not None and not isinstance(override, dict):
                raise ValueError(f"invalid reviewed override: {qualified_id}")
            if isinstance(override, dict):
                seen_overrides.add(qualified_id)
                evidence = [dict(item) for item in override.get("evidence", [])]
                concept = str(
                    override.get("concept")
                    or raw_observation.get("description")
                    or ""
                )
                review_status = str(
                    override.get("review_status") or "source_reviewed"
                )
                consumer_requirements = dict(
                    override.get("consumer_requirements", {})
                )
            else:
                evidence = [
                    _inherited_evidence(item, dimension=dimension, index=index)
                    for index, item in enumerate(
                        raw_observation.get("evidence", []), 1
                    )
                    if isinstance(item, dict)
                ]
                concept = str(raw_observation.get("description") or "")
                review_status = "inherited_provisional_gold_not_source_reviewed"
                consumer_requirements = {
                    "reasoning_substrate": {
                        "requirement": "concept_coverage_review_pending"
                    },
                    "audit_trail": {
                        "requirement": "semantic_and_temporal_review_pending"
                    },
                }
            for item in evidence:
                _validate_evidence(
                    item,
                    turns=turns,
                    qualified_observation_id=qualified_id,
                )
            observations.append(
                {
                    "qualified_observation_id": qualified_id,
                    "case_id": case_id,
                    "observation_id": observation_id,
                    "legacy_dimension": dimension,
                    "concept": concept,
                    "review_status": review_status,
                    "evidence": evidence,
                    "consumer_requirements": consumer_requirements,
                    "legacy_primary_families": list(
                        _PRIMARY_FAMILIES_BY_DIMENSION.get(dimension, [])
                    ),
                    "source": case_sources[case_id],
                }
            )

    unknown_overrides = set(overrides) - seen_overrides
    if unknown_overrides:
        raise ValueError(f"unknown reviewed overrides: {sorted(unknown_overrides)}")
    reviewed_count = sum(
        observation["review_status"] == "source_reviewed"
        for observation in observations
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_status": "prospective_scaffold_not_ready_for_promotion",
        "manifest": {
            "path": str(manifest_path.relative_to(REPO_ROOT)),
            "sha256": _sha256(manifest_path),
            "corpus_id": manifest["corpus_id"],
        },
        "review_overrides": {
            "path": str(overrides_path.relative_to(REPO_ROOT)),
            "sha256": _sha256(overrides_path),
            "annotation_status": overrides_payload.get("annotation_status"),
        },
        "case_count": len(case_sources),
        "observation_count": len(observations),
        "review_summary": {
            "source_reviewed_observation_count": reviewed_count,
            "pending_source_review_observation_count": len(observations)
            - reviewed_count,
        },
        "observations": observations,
        "scoring_policy": {
            "reasoning_substrate": (
                "score concept recovery across evidence/families declared by "
                "source review"
            ),
            "audit_trail": (
                "score temporal and semantic-role requirements separately"
            ),
            "pending_observations": (
                "may be used for legacy diagnostics but not promotion"
            ),
            "semantic_runtime_judge_allowed": False,
            "embedding_match_allowed": False,
            "deterministic_exact_span_scoring": True,
        },
        "non_claims": [
            "legacy_dimensions_are_not_final_product_ontology",
            "pending_observations_are_not_promotion_ready",
            "acceptable_families_are_not_deterministic_classifiers",
            "contract_does_not_change_prior_experiment_results",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = build_contract(
        manifest_path=args.manifest.expanduser().resolve(),
        overrides_path=args.overrides.expanduser().resolve(),
    )
    output = args.out.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Semantic observation contract written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
