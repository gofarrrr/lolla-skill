#!/usr/bin/env python3
"""Build the provider-free leakage-corrected R4 matched holdout v2 package."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INPUT_ROOT = (
    ROOT / "research/lolla-r4-matched-holdout-v2-source-freeze-2026-07-14"
)
CASE_IDS = (
    "r4h2-case01-community-audio-archive",
    "r4h2-case02-serialized-essay-pilot",
    "r4h2-case03-research-workspace-service",
    "r4h2-case04-shared-language-course",
)
FORBIDDEN_ANSWER_LANGUAGE = (
    "residual",
    "residual decision gap",
    "residual reconsideration dependency",
    "outside adopted machinery",
    "inside adopted machinery",
    "should stay quiet",
    "should not be emitted",
    "broad inventory",
    "source-first review",
    "belongs on the surface",
    "newly discovered gap",
    "unresolved_matter",
    "reopen_condition",
    "emit",
    "emitted",
    "suppress",
    "suppressed",
    "keep quiet",
    "expected result",
    "structured answer",
    "reopen the decision",
)


class R4MatchedHoldoutV2Error(RuntimeError):
    """Raised when v2 evidence or custody violates the frozen design."""


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise R4MatchedHoldoutV2Error(f"expected JSON object: {path}")
    return value


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _string_leaves(value: Any, pointer: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield pointer or "/", value
    elif isinstance(value, Mapping):
        for key, child in value.items():
            yield from _string_leaves(child, f"{pointer}/{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _string_leaves(child, f"{pointer}/{index}")


def load_v2_source_prior() -> dict[str, dict[str, Any]]:
    """Load new v2 sources and fallible priors without semantic inference."""

    result: dict[str, dict[str, Any]] = {}
    for case_id in CASE_IDS:
        source_path = INPUT_ROOT / "sources" / f"{case_id}.json"
        prior_path = INPUT_ROOT / "priors" / f"{case_id}.json"
        source = _load(source_path)
        prior = _load(prior_path)
        if source.get("case_id") != case_id or prior.get("case_id") != case_id:
            raise R4MatchedHoldoutV2Error(f"case identity drifted: {case_id}")
        result[case_id] = {
            "source": source,
            "prior": prior,
            "source_path": str(source_path.relative_to(ROOT)),
            "prior_path": str(prior_path.relative_to(ROOT)),
            "source_sha256": _sha(source_path),
            "prior_sha256": _sha(prior_path),
        }
    return result


def lint_v2_source_prior(
    cases: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Record exact forbidden vocabulary matches without judging meaning."""

    matches: list[dict[str, str]] = []
    for case_id, case in cases.items():
        for artifact_kind in ("source", "prior"):
            for pointer, text in _string_leaves(case[artifact_kind]):
                lowered = text.casefold()
                for term in FORBIDDEN_ANSWER_LANGUAGE:
                    pattern = rf"(?<![\w]){re.escape(term.casefold())}(?![\w])"
                    if re.search(pattern, lowered):
                        matches.append(
                            {
                                "case_id": case_id,
                                "artifact_kind": artifact_kind,
                                "json_pointer": pointer,
                                "term": term,
                            }
                        )
    return {
        "schema_version": "lolla.r4_matched_holdout_vocabulary_lint.v2",
        "status": (
            "deterministic_vocabulary_lint_passed"
            if not matches
            else "deterministic_vocabulary_lint_failed"
        ),
        "terms": list(FORBIDDEN_ANSWER_LANGUAGE),
        "exact_match_count": len(matches),
        "matches": matches,
        "semantic_sufficiency_decided": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def build_pre_target_audit(
    cases: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Record text custody and pending declarations before any target exists."""

    target_path = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target.json"
    contract_path = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
    return {
        "schema_version": "lolla.r4_matched_holdout_pre_target_audit.v2",
        "status": "awaiting_founder_pm_human_semantic_review",
        "deterministic_vocabulary_lint": lint_v2_source_prior(cases),
        "human_review_required_before_target": True,
        "deterministic_semantic_sufficiency_decided": False,
        "target_authored": target_path.exists(),
        "request_preview_authored": contract_path.exists(),
        "cases": [
            {
                "case_id": case_id,
                "source_sha256": case["source_sha256"],
                "prior_sha256": case["prior_sha256"],
                "last_four_message_indices": [25, 26, 27, 28],
                "last_four_canonical_sha256": hashlib.sha256(
                    _canonical_bytes(case["source"]["messages"][-4:])
                ).hexdigest(),
                "human_semantic_leakage_review": "pending",
                "last_four_sufficient_for_both_surfaces": None,
                "assistant_states_expected_category": None,
                "prior_self_discounting": None,
                "source_instructs_emit_or_suppress": None,
            }
            for case_id, case in cases.items()
        ],
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
