#!/usr/bin/env python3
"""Validate and freeze the provider-free R4 separated-surface source/prior set."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
FREEZE_ROOT = (
    ROOT
    / "research/lolla-r4-separated-surface-experiment-v1-source-freeze-2026-07-14"
)
SOURCE_ROOT = FREEZE_ROOT / "sources"
PRIOR_ROOT = FREEZE_ROOT / "priors"
MANIFEST_PATH = FREEZE_ROOT / "freeze-manifest.json"
HUMAN_CUSTODY_PATH = FREEZE_ROOT / "human-leakage-review-custody.json"
HUMAN_REVIEW_PACKET = (
    ROOT
    / "docs/evals/lolla-r4-separated-surface-experiment-v1-human-leakage-review.md"
)
CANONICAL_BASE = "1f092177670980963118c70b47097c379c3bbef9"
BRANCH = "agent/r4-separated-surface-experiment-design"

CASE_SPECS: dict[str, dict[str, str]] = {
    "r4s1-case01-cave-rescue-readiness": {
        "domain": "volunteer_cave_rescue_training_readiness",
        "source": "sources/r4s1-case01-cave-rescue-readiness.json",
        "prior": "priors/r4s1-case01-cave-rescue-readiness.json",
    },
    "r4s1-case02-neighborhood-observatory-winter-access": {
        "domain": "neighborhood_observatory_winter_public_access",
        "source": "sources/r4s1-case02-neighborhood-observatory-winter-access.json",
        "prior": "priors/r4s1-case02-neighborhood-observatory-winter-access.json",
    },
    "r4s1-case03-relaxed-performance-tour": {
        "domain": "independent_dance_relaxed_performance_tour",
        "source": "sources/r4s1-case03-relaxed-performance-tour.json",
        "prior": "priors/r4s1-case03-relaxed-performance-tour.json",
    },
    "r4s1-case04-native-seed-cryopreservation": {
        "domain": "native_seed_cryopreservation_collection",
        "source": "sources/r4s1-case04-native-seed-cryopreservation.json",
        "prior": "priors/r4s1-case04-native-seed-cryopreservation.json",
    },
}

PROHIBITED_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(pattern, re.IGNORECASE))
    for name, pattern in (
        ("residual", r"\bresidual\b"),
        ("reconsideration_dependency", r"\breconsideration dependency\b"),
        ("quiet_control", r"\bquiet control\b"),
        ("companion_record", r"\bcompanion record\b"),
        ("paired_task", r"\bpaired task\b"),
        ("separated_task", r"\bseparated task\b"),
        ("emit", r"\bemit(?:s|ted|ting)?\b"),
        ("suppress", r"\bsuppress(?:es|ed|ing|ion)?\b"),
        ("expected_classification", r"\bexpected classification\b"),
        ("target", r"\btarget(?:s|ed|ing)?\b"),
        ("source_first", r"\bsource[- ]first\b"),
        ("holdout", r"\bholdout\b"),
        ("outside_adopted_machinery", r"\boutside adopted machinery\b"),
        ("inside_adopted_machinery", r"\binside adopted machinery\b"),
        ("should_stay_quiet", r"\bshould stay quiet\b"),
        ("should_not_be_emitted", r"\bshould not be emitted\b"),
        ("broad_inventory", r"\bbroad inventory\b"),
        ("belongs_on_surface", r"\bbelongs on (?:the )?surface\b"),
        ("newly_discovered_gap", r"\bnewly discovered gap\b"),
        ("reader_output", r"\breader output\b"),
        ("return_zero", r"\breturn zero\b"),
        ("remain_quiet", r"\bremain quiet\b"),
    )
)


class R4SeparatedSurfaceSourceFreezeError(RuntimeError):
    """Raised when deterministic source/prior custody is invalid."""


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise R4SeparatedSurfaceSourceFreezeError(
            f"cannot load JSON: {_relative(path)}"
        ) from exc
    if not isinstance(value, dict):
        raise R4SeparatedSurfaceSourceFreezeError(
            f"JSON root must be an object: {_relative(path)}"
        )
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _value_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _render(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def _expected_paths() -> tuple[set[Path], set[Path]]:
    sources = {FREEZE_ROOT / spec["source"] for spec in CASE_SPECS.values()}
    priors = {FREEZE_ROOT / spec["prior"] for spec in CASE_SPECS.values()}
    return sources, priors


def _validate_source(case_id: str, source: Mapping[str, Any], domain: str) -> None:
    messages = source.get("messages")
    if source.get("schema_version") != "lolla.r4.simulated_conversation_source.v1":
        raise R4SeparatedSurfaceSourceFreezeError(f"source schema drifted: {case_id}")
    if source.get("case_id") != case_id or source.get("domain") != domain:
        raise R4SeparatedSurfaceSourceFreezeError(f"source identity drifted: {case_id}")
    if source.get("evidence_kind") != "simulated_reliability_not_real_user_evidence":
        raise R4SeparatedSurfaceSourceFreezeError(f"source evidence kind drifted: {case_id}")
    if source.get("message_count") != 28 or not isinstance(messages, list) or len(messages) != 28:
        raise R4SeparatedSurfaceSourceFreezeError(f"source must have 28 messages: {case_id}")
    for index, row in enumerate(messages, start=1):
        if not isinstance(row, dict):
            raise R4SeparatedSurfaceSourceFreezeError(f"message is not an object: {case_id}")
        expected_speaker = "user" if index % 2 else "assistant"
        if row.get("message_index") != index:
            raise R4SeparatedSurfaceSourceFreezeError(f"message index drifted: {case_id}")
        if row.get("alias") != f"e{index:03d}":
            raise R4SeparatedSurfaceSourceFreezeError(f"message alias drifted: {case_id}")
        if row.get("speaker") != expected_speaker:
            raise R4SeparatedSurfaceSourceFreezeError(f"speaker alternation drifted: {case_id}")
        if not isinstance(row.get("text"), str) or not row["text"].strip():
            raise R4SeparatedSurfaceSourceFreezeError(f"blank message text: {case_id}")


def _validate_prior(case_id: str, prior: Mapping[str, Any]) -> None:
    if prior.get("schema_version") != "lolla.r4.fallible_prior_interpretation.v1":
        raise R4SeparatedSurfaceSourceFreezeError(f"prior schema drifted: {case_id}")
    if prior.get("case_id") != case_id:
        raise R4SeparatedSurfaceSourceFreezeError(f"prior identity drifted: {case_id}")
    if prior.get("artifact_kind") != "fallible_prior_interpretation":
        raise R4SeparatedSurfaceSourceFreezeError(f"prior kind drifted: {case_id}")
    if prior.get("authority") != "fallible_prior_interpretation_not_source_truth":
        raise R4SeparatedSurfaceSourceFreezeError(f"prior authority drifted: {case_id}")
    records = prior.get("records")
    if not isinstance(records, list) or len(records) != 3:
        raise R4SeparatedSurfaceSourceFreezeError(f"prior record count drifted: {case_id}")
    expected_surfaces = ["starting_position", "current_position", "qualification"]
    if [row.get("surface") for row in records] != expected_surfaces:
        raise R4SeparatedSurfaceSourceFreezeError(f"prior surfaces drifted: {case_id}")
    record_ids = []
    valid_aliases = {f"e{index:03d}" for index in range(1, 29)}
    for row in records:
        if not isinstance(row, dict):
            raise R4SeparatedSurfaceSourceFreezeError(f"prior record invalid: {case_id}")
        record_ids.append(row.get("record_id"))
        for field in ("interpretation", "limitations"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise R4SeparatedSurfaceSourceFreezeError(
                    f"prior {field} missing: {case_id}"
                )
        aliases = row.get("source_aliases")
        if not isinstance(aliases, list) or not aliases or not set(aliases) <= valid_aliases:
            raise R4SeparatedSurfaceSourceFreezeError(f"prior aliases invalid: {case_id}")
    if len(set(record_ids)) != 3 or any(not isinstance(value, str) for value in record_ids):
        raise R4SeparatedSurfaceSourceFreezeError(f"prior record IDs invalid: {case_id}")
    review = prior.get("qualification_review")
    if not isinstance(review, dict) or review.get("outcome") != "qualification_present":
        raise R4SeparatedSurfaceSourceFreezeError(
            f"qualification review invalid: {case_id}"
        )
    evidence_ids = review.get("evidence_ids")
    if (
        not isinstance(evidence_ids, list)
        or not evidence_ids
        or not set(evidence_ids) <= valid_aliases
    ):
        raise R4SeparatedSurfaceSourceFreezeError(
            f"qualification aliases invalid: {case_id}"
        )
    for field in ("interpretation", "limitations"):
        if not isinstance(review.get(field), str) or not review[field].strip():
            raise R4SeparatedSurfaceSourceFreezeError(
                f"qualification {field} missing: {case_id}"
            )


def load_and_validate_cases() -> dict[str, dict[str, Any]]:
    expected_sources, expected_priors = _expected_paths()
    actual_sources = set(SOURCE_ROOT.glob("*.json"))
    actual_priors = set(PRIOR_ROOT.glob("*.json"))
    if actual_sources != expected_sources:
        raise R4SeparatedSurfaceSourceFreezeError("source file set drifted")
    if actual_priors != expected_priors:
        raise R4SeparatedSurfaceSourceFreezeError("prior file set drifted")

    cases: dict[str, dict[str, Any]] = {}
    domains: set[str] = set()
    for case_id, spec in CASE_SPECS.items():
        source_path = FREEZE_ROOT / spec["source"]
        prior_path = FREEZE_ROOT / spec["prior"]
        source = _load(source_path)
        prior = _load(prior_path)
        _validate_source(case_id, source, spec["domain"])
        _validate_prior(case_id, prior)
        if source["domain"] in domains:
            raise R4SeparatedSurfaceSourceFreezeError("source domains must be unique")
        domains.add(source["domain"])
        cases[case_id] = {
            "source": source,
            "source_path": source_path,
            "prior": prior,
            "prior_path": prior_path,
        }
    return cases


def lint_cases(cases: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for case_id, case in cases.items():
        for artifact_kind in ("source", "prior"):
            text = json.dumps(case[artifact_kind], ensure_ascii=False, sort_keys=True)
            for pattern_id, pattern in PROHIBITED_PATTERNS:
                if pattern.search(text):
                    matches.append(
                        {
                            "case_id": case_id,
                            "artifact_kind": artifact_kind,
                            "pattern_id": pattern_id,
                        }
                    )
    return matches


def validate_forbidden_artifact_absence() -> None:
    expected_sources, expected_priors = _expected_paths()
    allowed = expected_sources | expected_priors | {MANIFEST_PATH, HUMAN_CUSTODY_PATH}
    actual = {path for path in FREEZE_ROOT.rglob("*") if path.is_file()}
    if not actual <= allowed:
        unexpected = sorted(_relative(path) for path in actual - allowed)
        raise R4SeparatedSurfaceSourceFreezeError(
            f"unexpected freeze artifact: {unexpected}"
        )
    forbidden = (
        ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target.json",
        ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-target-review.json",
        ROOT / "docs/evals/lolla-r4-separated-surface-experiment-v1-contract.json",
        ROOT / "scripts/evals/run_r4_separated_surface_experiment.py",
    )
    existing = [_relative(path) for path in forbidden if path.exists()]
    if existing:
        raise R4SeparatedSurfaceSourceFreezeError(
            f"forbidden pre-target artifact exists: {existing}"
        )


def build_manifest() -> dict[str, Any]:
    cases = load_and_validate_cases()
    matches = lint_cases(cases)
    if matches:
        raise R4SeparatedSurfaceSourceFreezeError(
            f"prohibited source/prior language: {matches}"
        )
    validate_forbidden_artifact_absence()

    rows = []
    for case_id, case in cases.items():
        source_path = case["source_path"]
        prior_path = case["prior_path"]
        source = case["source"]
        prior = case["prior"]
        rows.append(
            {
                "case_id": case_id,
                "domain": source["domain"],
                "source_prior_order": ["authoritative_source", "fallible_prior_interpretation"],
                "source": {
                    "path": _relative(source_path),
                    "sha256": _sha256(source_path),
                    "utf8_bytes": len(source_path.read_bytes()),
                    "message_count": 28,
                    "user_message_count": 14,
                    "assistant_message_count": 14,
                    "alias_count": 28,
                    "first_alias": "e001",
                    "last_alias": "e028",
                    "last_four_canonical_sha256": _value_sha256(source["messages"][-4:]),
                },
                "prior": {
                    "path": _relative(prior_path),
                    "sha256": _sha256(prior_path),
                    "utf8_bytes": len(prior_path.read_bytes()),
                    "record_count": 3,
                    "qualification_review_count": 1,
                },
                "deterministic_prohibited_language_matches": 0,
                "human_semantic_leakage_review": "pending",
                "human_last_four_sufficiency_review": "pending",
            }
        )

    return {
        "schema_version": "lolla.r4_separated_surface_source_prior_freeze.v1",
        "status": "source_prior_frozen_human_review_pending_before_target",
        "date": "2026-07-14",
        "canonical_base_commit": CANONICAL_BASE,
        "local_branch": BRANCH,
        "cases": rows,
        "case_count": 4,
        "source_count": 4,
        "prior_count": 4,
        "source_prior_order": ["authoritative_source", "fallible_prior_interpretation"],
        "deterministic_language_scan": {
            "status": "passed_zero_exact_matches_supporting_evidence_only",
            "pattern_ids": [name for name, _ in PROHIBITED_PATTERNS],
            "match_count": 0,
            "semantic_judgment_performed": False,
        },
        "freeze_order": [
            "authoritative_sources_and_fallible_priors",
            "source_prior_hashes_and_deterministic_scan",
            "human_semantic_leakage_review",
            "protected_source_first_target",
            "provider_visible_task_shape_package",
        ],
        "completed_freeze_steps": [
            "authoritative_sources_and_fallible_priors",
            "source_prior_hashes_and_deterministic_scan",
        ],
        "human_semantic_leakage_review": "pending",
        "target_authorship_allowed": False,
        "byte_change_requires_new_human_review": True,
        "target_existed_when_frozen": False,
        "target_review_existed_when_frozen": False,
        "request_preview_existed_when_frozen": False,
        "provider_visible_prompt_or_schema_existed_when_frozen": False,
        "execution_contract_existed_when_frozen": False,
        "authorization_existed_when_frozen": False,
        "runner_existed_when_frozen": False,
        "provider_output_existed_when_frozen": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def write() -> dict[str, Any]:
    manifest = build_manifest()
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_bytes(_render(manifest))
    return manifest


def validate() -> dict[str, Any]:
    expected = build_manifest()
    if not MANIFEST_PATH.is_file() or MANIFEST_PATH.read_bytes() != _render(expected):
        raise R4SeparatedSurfaceSourceFreezeError("freeze manifest drifted")
    if not HUMAN_REVIEW_PACKET.is_file():
        raise R4SeparatedSurfaceSourceFreezeError("human review packet missing")
    packet = HUMAN_REVIEW_PACKET.read_text(encoding="utf-8")
    if "Status: human semantic-leakage review passed" not in packet:
        raise R4SeparatedSurfaceSourceFreezeError("human review pass is not recorded")
    if "Human finding: `pending`" in packet:
        raise R4SeparatedSurfaceSourceFreezeError("human review remains pending")
    for row in expected["cases"]:
        for artifact_kind in ("source", "prior"):
            artifact = row[artifact_kind]
            if artifact["path"] not in packet or artifact["sha256"] not in packet:
                raise R4SeparatedSurfaceSourceFreezeError(
                    f"review packet custody missing: {row['case_id']} {artifact_kind}"
                )
    return expected


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    manifest = write() if args.write else validate()
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "case_count": manifest["case_count"],
                "source_count": manifest["source_count"],
                "prior_count": manifest["prior_count"],
                "deterministic_prohibited_language_matches": manifest[
                    "deterministic_language_scan"
                ]["match_count"],
                "human_semantic_leakage_review": manifest[
                    "human_semantic_leakage_review"
                ],
                "target_authorship_allowed": manifest["target_authorship_allowed"],
                "provider_calls": manifest["provider_calls"],
                "provider_cost_usd": manifest["provider_cost_usd"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
