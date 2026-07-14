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
HUMAN_REVIEW_PATH = (
    ROOT / "docs/evals/lolla-r4-matched-holdout-v2-human-leakage-review.md"
)
LEAKAGE_AUDIT_PATH = INPUT_ROOT / "leakage-audit.json"
FREEZE_MANIFEST_PATH = INPUT_ROOT / "freeze-manifest.json"
TARGET_PATH = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target.json"
CONTRACT_PATH = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
CASE_IDS = (
    "r4h2-case01-community-audio-archive",
    "r4h2-case02-serialized-essay-pilot",
    "r4h2-case03-research-workspace-service",
    "r4h2-case04-shared-language-course",
)
HUMAN_LEAKAGE_DECLARATION = "human leakage review passes"
SOURCE_PRIOR_CHECKPOINT = "1d02d2abc1f416178fbd00a9f0b93aad353c24b2"
REVIEWED_HASHES = {
    "r4h2-case01-community-audio-archive": {
        "source_sha256": "4af8f39ce9cc8e4b7edbb80111c2cfabac09037e176895ae380392308a4ac3c1",
        "prior_sha256": "e77baaf2378d8cfc3cc29371b4dc5e472b585a09f29b29d8725ff49d99ae7095",
    },
    "r4h2-case02-serialized-essay-pilot": {
        "source_sha256": "922228b8371d9536464adc402390f6e50d894927e0b9a7f9c60518d9a68bdb80",
        "prior_sha256": "b5706dc359957e92fb25ee9535d3981835f7496fc4f138eae12885f18f3a3543",
    },
    "r4h2-case03-research-workspace-service": {
        "source_sha256": "9c3c979fbe79e6a573f9dc316e1e03c7a1ffc29dc0b5abd7c139825ef2a652ad",
        "prior_sha256": "53aff0c8c41fd7c1504718f4190a736addad67d0f150ddbaa6482cfb71c95e52",
    },
    "r4h2-case04-shared-language-course": {
        "source_sha256": "ce8f1652612467e83589b9073b6a8c83273044fb4c5ab611852e1d916cdb0783",
        "prior_sha256": "9e0ec28e5094b7c68560db1af1e231c6859972317a0dd2204cfa3914ad202ac5",
    },
}
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


def _render(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


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


def _review_hashes_match(
    cases: Mapping[str, Mapping[str, Any]],
) -> bool:
    return tuple(cases) == CASE_IDS and all(
        cases[case_id].get("source_sha256")
        == REVIEWED_HASHES[case_id]["source_sha256"]
        and cases[case_id].get("prior_sha256")
        == REVIEWED_HASHES[case_id]["prior_sha256"]
        for case_id in CASE_IDS
    )


def build_human_review_record(
    cases: Mapping[str, Mapping[str, Any]],
    *,
    declaration: str,
) -> dict[str, Any]:
    """Bind the founder/PM semantic decision to the reviewed evidence bytes."""

    if declaration != HUMAN_LEAKAGE_DECLARATION:
        raise R4MatchedHoldoutV2Error("exact human declaration is required")
    if not _review_hashes_match(cases):
        raise R4MatchedHoldoutV2Error("reviewed source/prior hash changed")
    lint = lint_v2_source_prior(cases)
    if lint["status"] != "deterministic_vocabulary_lint_passed":
        raise R4MatchedHoldoutV2Error("deterministic vocabulary lint failed")
    return {
        "schema_version": "lolla.r4_matched_holdout_human_leakage_review.v2",
        "status": "human_semantic_leakage_review_passed",
        "date": "2026-07-14",
        "human_declaration": declaration,
        "reviewer_authority": "founder_pm_human",
        "review_scope": "all_four_complete_v2_source_prior_pairs",
        "source_prior_checkpoint_commit": SOURCE_PRIOR_CHECKPOINT,
        "human_review_required_before_target": "satisfied",
        "target_authorship_may_begin": True,
        "human_semantic_sufficiency_decided": True,
        "deterministic_semantic_sufficiency_decided": False,
        "deterministic_vocabulary_lint": lint,
        "byte_change_invalidates_review": True,
        "cases": [
            {
                "case_id": case_id,
                "source_sha256": cases[case_id]["source_sha256"],
                "prior_sha256": cases[case_id]["prior_sha256"],
                "human_semantic_leakage_review": "passed",
                "last_four_message_indices": [25, 26, 27, 28],
                "last_four_canonical_sha256": hashlib.sha256(
                    _canonical_bytes(cases[case_id]["source"]["messages"][-4:])
                ).hexdigest(),
                "last_four_sufficient_for_both_surfaces": False,
                "assistant_states_expected_category": False,
                "prior_self_discounting": False,
                "source_instructs_emit_or_suppress": False,
            }
            for case_id in CASE_IDS
        ],
        "evaluation_limitations": [
            {
                "case_ids": [CASE_IDS[0], CASE_IDS[1]],
                "kind": "recent_summary_assistance",
                "statement": (
                    "The final messages summarize several adopted documents and "
                    "controls, providing some recency assistance, but do not disclose "
                    "the expected classification and are not independently sufficient "
                    "to evaluate both surfaces."
                ),
            },
            {
                "case_ids": list(CASE_IDS),
                "kind": "human_semantic_judgment",
                "statement": (
                    "The human decision establishes leakage sufficiency only for the "
                    "reviewed bytes; deterministic lint is supporting evidence, not a "
                    "substitute for semantic review."
                ),
            },
        ],
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "provider_authorization": False,
    }


def validate_human_review_record(
    review: Mapping[str, Any],
    *,
    cases: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Reject any declaration or reviewed-byte drift before target authorship."""

    expected = build_human_review_record(
        cases,
        declaration=str(review.get("human_declaration", "")),
    )
    if dict(review) != expected:
        raise R4MatchedHoldoutV2Error("human review record drifted")
    return expected


def build_human_review_freeze_files() -> dict[str, bytes]:
    """Build the exact pre-target human-review and source/prior freeze files."""

    cases = load_v2_source_prior()
    review = build_human_review_record(
        cases,
        declaration=HUMAN_LEAKAGE_DECLARATION,
    )
    review_packet = HUMAN_REVIEW_PATH.read_bytes()
    required_review_phrases = (
        "Status: passed by founder/PM human review",
        f"> {HUMAN_LEAKAGE_DECLARATION}",
        "Any byte change to a reviewed",
        "Cases 01 and 02 end with summaries",
    )
    review_text = review_packet.decode("utf-8")
    if not all(phrase in review_text for phrase in required_review_phrases):
        raise R4MatchedHoldoutV2Error("human review packet does not record the pass")
    audit_raw = _render(review)
    manifest = {
        "schema_version": "lolla.r4_matched_holdout_source_prior_freeze.v2",
        "status": "source_prior_and_human_review_frozen_before_target",
        "date": "2026-07-14",
        "source_prior_checkpoint_commit": SOURCE_PRIOR_CHECKPOINT,
        "freeze_order": [
            "new_v2_source_and_prior_artifacts",
            "source_prior_hashes_and_leakage_audit",
            "protected_source_first_target",
            "matched_request_previews",
            "exact_request_delta_manifests",
            "execution_contract_call_order_runner_budget_and_non_authorizing_authorization_shape",
        ],
        "completed_freeze_steps": [
            "new_v2_source_and_prior_artifacts",
            "source_prior_hashes_and_leakage_audit",
        ],
        "cases": [
            {
                "case_id": case_id,
                "source": {
                    "path": cases[case_id]["source_path"],
                    "sha256": cases[case_id]["source_sha256"],
                    "utf8_bytes": len(
                        (ROOT / cases[case_id]["source_path"]).read_bytes()
                    ),
                },
                "prior": {
                    "path": cases[case_id]["prior_path"],
                    "sha256": cases[case_id]["prior_sha256"],
                    "utf8_bytes": len(
                        (ROOT / cases[case_id]["prior_path"]).read_bytes()
                    ),
                },
                "last_four_canonical_sha256": next(
                    row["last_four_canonical_sha256"]
                    for row in review["cases"]
                    if row["case_id"] == case_id
                ),
                "human_semantic_leakage_review": "passed",
                "last_four_sufficient_for_both_surfaces": False,
            }
            for case_id in CASE_IDS
        ],
        "leakage_audit": {
            "path": _relative(LEAKAGE_AUDIT_PATH),
            "sha256": hashlib.sha256(audit_raw).hexdigest(),
            "utf8_bytes": len(audit_raw),
        },
        "human_review_packet": {
            "path": _relative(HUMAN_REVIEW_PATH),
            "sha256": hashlib.sha256(review_packet).hexdigest(),
            "utf8_bytes": len(review_packet),
        },
        "target_existed_when_frozen": False,
        "request_preview_existed_when_frozen": False,
        "provider_output_existed_when_frozen": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "authorization_existed": False,
        "byte_change_requires_new_human_review": True,
    }
    return {
        _relative(LEAKAGE_AUDIT_PATH): audit_raw,
        _relative(FREEZE_MANIFEST_PATH): _render(manifest),
    }


def write_human_review_freeze() -> dict[str, Any]:
    """Write the pre-target freeze only while target/request artifacts are absent."""

    if TARGET_PATH.exists() or CONTRACT_PATH.exists():
        raise R4MatchedHoldoutV2Error(
            "human review freeze must predate target and request artifacts"
        )
    files = build_human_review_freeze_files()
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return validate_human_review_freeze()


def validate_human_review_freeze() -> dict[str, Any]:
    """Validate the exact hash-bound human gate without semantic inference."""

    expected = build_human_review_freeze_files()
    for relative, raw in expected.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != raw:
            raise R4MatchedHoldoutV2Error(
                f"human review freeze artifact drifted: {relative}"
            )
    review = json.loads(LEAKAGE_AUDIT_PATH.read_text(encoding="utf-8"))
    return validate_human_review_record(review, cases=load_v2_source_prior())
