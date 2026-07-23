"""Validate and fan in fresh-agent Product Delta paired-screen reviews.

The validator checks declared blind-review custody and response shape. The
consolidator records reviewer observations side by side and adds only exact
lineage facts from the sealed manifest. It does not vote, rank, score, choose
an arm, adjudicate semantic truth, or convert agent reads into human evidence.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.product_delta_paired_screen import (
    DEFAULT_BLIND_PACKETS_RELPATH,
    DEFAULT_SEALED_MANIFEST_RELPATH,
    NON_CLAIMS,
    PAIRED_SCREEN_SCHEMA_VERSION,
    SEALED_MANIFEST_SCHEMA_VERSION,
)


FRESH_REVIEW_SCHEMA_VERSION = "lolla.product_delta_fresh_agent_review.v1"
CONSOLIDATION_SCHEMA_VERSION = (
    "lolla.product_delta_agent_paired_screen_consolidation.v1"
)
DEFAULT_REVIEW_DIR_RELPATH = (
    "reviews/codex-assisted/agent-only-paired-delta-screen-v1"
)
DEFAULT_QUALIFICATION_REVIEW_RELPATH = (
    f"{DEFAULT_REVIEW_DIR_RELPATH}/qualification-review.json"
)
DEFAULT_PRIMARY_REVIEW_RELPATH = (
    f"{DEFAULT_REVIEW_DIR_RELPATH}/pair-review-primary.json"
)
DEFAULT_SKEPTICAL_REVIEW_RELPATH = (
    f"{DEFAULT_REVIEW_DIR_RELPATH}/pair-review-skeptical.json"
)
DEFAULT_CONSOLIDATION_RELPATH = (
    "research/agent-only-paired-delta-screen-2026-07-23/"
    "consolidated-diagnostic.json"
)

QUALIFICATION_DISPOSITIONS = {
    "sufficient_for_bounded_comparison",
    "blocked_thin_context",
    "inconclusive",
    "needs_human_review",
}
MATERIAL_DIFFERENCE_VALUES = {"present", "absent", "uncertain"}
PRESENCE_VALUES = {
    "shared",
    "a_exclusive",
    "b_exclusive",
    "contradictory",
    "uncertain_equivalence",
}
REASONING_OPERATION_VALUES = {
    "question",
    "option",
    "counterframe",
    "falsifier",
    "reversal",
    "evidence_gate",
    "stop_rule",
    "premortem",
    "stakeholder_view",
    "time_horizon",
    "preserved_value",
    "lost_value",
    "restatement",
    "generic_caution",
    "unsupported_specificity",
    "other",
}
SOURCE_GROUNDING_VALUES = {
    "supported",
    "partly_supported",
    "unsupported",
    "unclear",
}
COGNITIVE_EFFECT_VALUES = {
    "opens_path",
    "narrows_path",
    "adds_test",
    "adds_caution",
    "preserves_option",
    "removes_option",
    "repeats",
    "adds_burden",
    "unclear",
}
IDENTITY_GUESS_VALUES = {"A", "B", "indistinguishable"}
STANDDOWN_SUPPORT_VALUES = {"supported", "unsupported", "uncertain"}
FORBIDDEN_REVIEW_KEYS = {
    "winner",
    "score",
    "rating",
    "rank",
    "approved",
    "approval",
    "certified",
    "pass",
    "passed",
    "pass_fail",
    "better_arm",
    "quality_score",
    "improvement_score",
    "answer_quality_score",
}


class ProductDeltaPairedScreenReviewError(ValueError):
    """Deterministic, sanitized paired-screen review error."""


def build_review_consolidation(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], list[str]]:
    """Validate three frozen reviews and build a non-adjudicating fan-in."""

    root = Path(repo_root).resolve()
    blind, blind_ref = _read_json_ref(root, DEFAULT_BLIND_PACKETS_RELPATH)
    sealed, sealed_ref = _read_json_ref(root, DEFAULT_SEALED_MANIFEST_RELPATH)
    qualification, qualification_ref = _read_json_ref(
        root, DEFAULT_QUALIFICATION_REVIEW_RELPATH
    )
    primary, primary_ref = _read_json_ref(root, DEFAULT_PRIMARY_REVIEW_RELPATH)
    skeptical, skeptical_ref = _read_json_ref(
        root, DEFAULT_SKEPTICAL_REVIEW_RELPATH
    )

    errors: list[str] = []
    if blind.get("schema_version") != PAIRED_SCREEN_SCHEMA_VERSION:
        errors.append("blind packet schema mismatch")
    if sealed.get("schema_version") != SEALED_MANIFEST_SCHEMA_VERSION:
        errors.append("sealed manifest schema mismatch")
    blind_expected_sha = (
        sealed.get("blind_packets", {}).get("sha256")
        if isinstance(sealed.get("blind_packets"), Mapping)
        else None
    )
    if blind_expected_sha != blind_ref["sha256"]:
        errors.append("sealed blind packet hash mismatch")

    qualification_ids = _case_ids(blind.get("qualification_cases"))
    paired_ids = _case_ids(blind.get("paired_cases"))
    standdown_ids = _case_ids(blind.get("standdown_cases"))
    screen_id = _text(blind.get("screen_id"))

    errors.extend(
        _validate_common_review(
            qualification,
            expected_review_id="fresh-qualification-review",
            screen_id=screen_id,
            path=DEFAULT_QUALIFICATION_REVIEW_RELPATH,
        )
    )
    errors.extend(
        _validate_qualification_review(
            qualification,
            expected_case_ids=qualification_ids,
            path=DEFAULT_QUALIFICATION_REVIEW_RELPATH,
        )
    )
    for payload, review_id, path in (
        (
            primary,
            "fresh-pair-primary",
            DEFAULT_PRIMARY_REVIEW_RELPATH,
        ),
        (
            skeptical,
            "fresh-pair-skeptical",
            DEFAULT_SKEPTICAL_REVIEW_RELPATH,
        ),
    ):
        errors.extend(
            _validate_common_review(
                payload,
                expected_review_id=review_id,
                screen_id=screen_id,
                path=path,
            )
        )
        errors.extend(
            _validate_pair_review(
                payload,
                expected_pair_ids=paired_ids,
                expected_standdown_ids=standdown_ids,
                path=path,
            )
        )

    sealed_index = _index_cases(sealed.get("paired_cases"))
    pair_review_payloads = (primary, skeptical)
    paired_consolidation: list[dict[str, Any]] = []
    for case_id in paired_ids:
        sealed_case = sealed_index.get(case_id, {})
        actual_label = _actual_added_context_label(sealed_case)
        reviewer_reads = []
        material_reads = []
        for payload in pair_review_payloads:
            review = _index_cases(payload.get("paired_reviews")).get(case_id, {})
            identity = review.get("identity_guess_after_substantive_review")
            identity_guess = (
                identity.get("arm_with_added_external_context")
                if isinstance(identity, Mapping)
                else None
            )
            material = review.get("material_decision_difference")
            material_reads.append(material)
            reviewer_reads.append(
                {
                    "review_id": payload.get("review_id"),
                    "material_decision_difference": material,
                    "identity_guess_after_substantive_review": identity_guess,
                    "identity_guess_relation_to_lineage": (
                        "matches_lineage"
                        if identity_guess == actual_label
                        else (
                            "declared_indistinguishable"
                            if identity_guess == "indistinguishable"
                            else "does_not_match_lineage"
                        )
                    ),
                    "atomic_move_count": len(_list(review.get("atomic_moves"))),
                }
            )
        paired_consolidation.append(
            {
                "case_id": case_id,
                "evidence_class": sealed_case.get("evidence_class"),
                "actual_arm_with_added_external_context": actual_label,
                "reviewer_reads": reviewer_reads,
                "material_difference_reads": material_reads,
                "material_difference_read_agreement": (
                    len(set(material_reads)) == 1
                ),
                "semantic_disagreement_policy": (
                    "Reviewer reads remain side by side. Agreement is not truth; "
                    "disagreement is not resolved by vote."
                ),
            }
        )

    qualification_records = _list(qualification.get("qualification_reviews"))
    qualification_counts = Counter(
        _text(item.get("evidence_disposition"))
        for item in qualification_records
        if isinstance(item, Mapping)
    )
    qualification_summary = {
        "review_id": qualification.get("review_id"),
        "case_count": len(qualification_records),
        "disposition_counts": {
            key: qualification_counts[key]
            for key in sorted(QUALIFICATION_DISPOSITIONS)
        },
        "case_dispositions": [
            {
                "case_id": item.get("case_id"),
                "evidence_disposition": item.get("evidence_disposition"),
            }
            for item in qualification_records
            if isinstance(item, Mapping)
        ],
        "interpretation_limit": (
            "These are fresh-agent diagnostic dispositions. Comparing them with "
            "sealed trap expectations is a maintainer interpretation, not a score "
            "or human validation."
        ),
    }

    material_disagreements = [
        item["case_id"]
        for item in paired_consolidation
        if not item["material_difference_read_agreement"]
    ]
    identity_relations = Counter(
        read["identity_guess_relation_to_lineage"]
        for item in paired_consolidation
        for read in item["reviewer_reads"]
        if item["evidence_class"] != "exact_duplicate_null"
    )
    standdown_reads = [
        {
            "review_id": payload.get("review_id"),
            "standdown_support": (
                _list(payload.get("standdown_reviews"))[0].get(
                    "standdown_support"
                )
                if _list(payload.get("standdown_reviews"))
                and isinstance(_list(payload.get("standdown_reviews"))[0], Mapping)
                else None
            ),
        }
        for payload in pair_review_payloads
    ]

    consolidation: dict[str, Any] = {
        "schema_version": CONSOLIDATION_SCHEMA_VERSION,
        "screen_id": screen_id,
        "status": (
            "valid_frozen_agent_diagnostic"
            if not errors
            else "invalid_review_shape"
        ),
        "boundary": {
            "new_provider_calls": 0,
            "new_provider_cost_usd": 0,
            "historical_provider_outputs_consumed_as_checked_in_inputs": True,
            "private_archives_read": False,
            "live_lolla_skill_invoked": False,
            "runtime_invoked": False,
            "graph_traversal_invoked": False,
            "graph_or_runtime_changed": False,
            "human_validated": False,
            "ground_truth": False,
            "product_proof": False,
            "answer_quality_scored": False,
            "scalar_judgment_created": False,
        },
        "review_contexts": {
            "fresh_agent_context_count": 2,
            "qualification_context_also_supplied_skeptical_pair_review": True,
            "primary_pair_review_was_separate_context": True,
            "pair_reviewers_saw_each_other": False,
            "reviewers_saw_sealed_manifest_before_freeze": False,
            "pair_review_independence_limit": (
                "The skeptical pair reviewer first completed the qualification "
                "traps in the same fresh context. The primary pair reviewer was "
                "separate. Both were blind to lineage and prior outcomes."
            ),
        },
        "input_refs": {
            "blind_packets": blind_ref,
            "sealed_manifest": sealed_ref,
            "qualification_review": qualification_ref,
            "primary_pair_review": primary_ref,
            "skeptical_pair_review": skeptical_ref,
        },
        "validation": {
            "error_count": len(errors),
            "errors": errors,
            "shape_and_custody_only": True,
            "semantic_correctness_validated": False,
        },
        "qualification": qualification_summary,
        "paired_cases": paired_consolidation,
        "cross_case_observations": {
            "material_difference_disagreement_case_ids": material_disagreements,
            "material_difference_agreement_case_count": (
                len(paired_consolidation) - len(material_disagreements)
            ),
            "identity_guess_relation_counts_excluding_null": {
                key: identity_relations[key]
                for key in (
                    "matches_lineage",
                    "does_not_match_lineage",
                    "declared_indistinguishable",
                )
            },
            "duplicate_null_material_reads": next(
                (
                    item["material_difference_reads"]
                    for item in paired_consolidation
                    if item["evidence_class"] == "exact_duplicate_null"
                ),
                [],
            ),
            "standdown_reads": standdown_reads,
        },
        "fan_in_policy": [
            "No reviewer was selected as authoritative.",
            "No semantic disagreement was resolved by voting.",
            "Lineage reveal checks provenance guesses only; it does not adjudicate the reasoning moves.",
            "Historical comparison artifacts remain context, not an answer key.",
            "Partial-source cases remain partial after unblinding.",
        ],
        "non_claims": list(NON_CLAIMS),
    }
    return consolidation, errors


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def validate_checked_in_consolidation(*, repo_root: Path | str) -> list[str]:
    root = Path(repo_root).resolve()
    consolidation, errors = build_review_consolidation(repo_root=root)
    if errors:
        return list(errors)
    expected = render_json(consolidation)
    path = _resolve_repo_path(root, DEFAULT_CONSOLIDATION_RELPATH)
    try:
        actual = path.read_text(encoding="utf-8")
    except OSError:
        return [f"missing generated artifact:{DEFAULT_CONSOLIDATION_RELPATH}"]
    if actual != expected:
        return [f"generated artifact drift:{DEFAULT_CONSOLIDATION_RELPATH}"]
    return []


def write_checked_in_consolidation(*, repo_root: Path | str) -> None:
    root = Path(repo_root).resolve()
    consolidation, errors = build_review_consolidation(repo_root=root)
    if errors:
        raise ProductDeltaPairedScreenReviewError(
            f"review validation failed with {len(errors)} error(s)"
        )
    path = _resolve_repo_path(root, DEFAULT_CONSOLIDATION_RELPATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_json(consolidation), encoding="utf-8")


def _validate_common_review(
    payload: Mapping[str, Any],
    *,
    expected_review_id: str,
    screen_id: str,
    path: str,
) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != FRESH_REVIEW_SCHEMA_VERSION:
        errors.append(f"{path}:schema version mismatch")
    if payload.get("review_id") != expected_review_id:
        errors.append(f"{path}:review id mismatch")
    if payload.get("screen_id") != screen_id:
        errors.append(f"{path}:screen id mismatch")
    if payload.get("input_path") != DEFAULT_BLIND_PACKETS_RELPATH:
        errors.append(f"{path}:input path mismatch")
    for key in (
        "sealed_manifest_seen",
        "other_repository_material_seen",
        "human_validated",
    ):
        if payload.get(key) is not False:
            errors.append(f"{path}:{key} must be false")
    if payload.get("provider_calls") != 0:
        errors.append(f"{path}:provider_calls must be zero")
    if payload.get("provider_cost_usd") != 0:
        errors.append(f"{path}:provider_cost_usd must be zero")
    forbidden = _walk_keys(payload) & FORBIDDEN_REVIEW_KEYS
    if forbidden:
        errors.append(f"{path}:forbidden keys:{','.join(sorted(forbidden))}")
    rendered = json.dumps(payload, ensure_ascii=False)
    for marker in ("/Users/", "client_secret", "api_key", "password"):
        if marker in rendered:
            errors.append(f"{path}:privacy marker:{marker}")
    return errors


def _validate_qualification_review(
    payload: Mapping[str, Any],
    *,
    expected_case_ids: list[str],
    path: str,
) -> list[str]:
    errors: list[str] = []
    records = _list(payload.get("qualification_reviews"))
    errors.extend(_validate_exact_case_ids(records, expected_case_ids, path))
    for record in records:
        if not isinstance(record, Mapping):
            errors.append(f"{path}:qualification record is not an object")
            continue
        case_id = _text(record.get("case_id"))
        if record.get("evidence_disposition") not in QUALIFICATION_DISPOSITIONS:
            errors.append(f"{path}:{case_id}:invalid evidence disposition")
        for key in (
            "supported_observations",
            "missing_evidence",
            "inferences_explicitly_not_made",
            "uncertainty_notes",
        ):
            if not isinstance(record.get(key), list):
                errors.append(f"{path}:{case_id}:{key} must be an array")
    return errors


def _validate_pair_review(
    payload: Mapping[str, Any],
    *,
    expected_pair_ids: list[str],
    expected_standdown_ids: list[str],
    path: str,
) -> list[str]:
    errors: list[str] = []
    paired = _list(payload.get("paired_reviews"))
    standdowns = _list(payload.get("standdown_reviews"))
    errors.extend(_validate_exact_case_ids(paired, expected_pair_ids, path))
    errors.extend(
        _validate_exact_case_ids(standdowns, expected_standdown_ids, path)
    )
    for review in paired:
        if not isinstance(review, Mapping):
            errors.append(f"{path}:paired review is not an object")
            continue
        case_id = _text(review.get("case_id"))
        source_interpretation = review.get("source_interpretation")
        if not isinstance(source_interpretation, Mapping):
            errors.append(f"{path}:{case_id}:missing source interpretation")
        moves = _list(review.get("atomic_moves"))
        if not moves:
            errors.append(f"{path}:{case_id}:atomic moves are empty")
        move_ids: list[str] = []
        for move in moves:
            if not isinstance(move, Mapping):
                errors.append(f"{path}:{case_id}:atomic move is not an object")
                continue
            move_id = _text(move.get("move_id"))
            move_ids.append(move_id)
            if move.get("presence") not in PRESENCE_VALUES:
                errors.append(f"{path}:{case_id}:{move_id}:invalid presence")
            if move.get("reasoning_operation") not in REASONING_OPERATION_VALUES:
                errors.append(
                    f"{path}:{case_id}:{move_id}:invalid reasoning operation"
                )
            if move.get("source_grounding") not in SOURCE_GROUNDING_VALUES:
                errors.append(
                    f"{path}:{case_id}:{move_id}:invalid source grounding"
                )
            if move.get("cognitive_effect") not in COGNITIVE_EFFECT_VALUES:
                errors.append(
                    f"{path}:{case_id}:{move_id}:invalid cognitive effect"
                )
            if not isinstance(move.get("source_evidence"), list):
                errors.append(
                    f"{path}:{case_id}:{move_id}:source_evidence must be an array"
                )
        if len(move_ids) != len(set(move_ids)):
            errors.append(f"{path}:{case_id}:duplicate move id")
        arm_observations = review.get("arm_observations")
        if not isinstance(arm_observations, Mapping) or set(
            arm_observations
        ) != {"A", "B"}:
            errors.append(f"{path}:{case_id}:arm observations must contain A and B")
        else:
            for label in ("A", "B"):
                observation = arm_observations.get(label)
                if not isinstance(observation, Mapping):
                    errors.append(
                        f"{path}:{case_id}:{label}:arm observation is invalid"
                    )
                    continue
                for key in (
                    "preserved_source_value",
                    "lost_or_weakened_source_value",
                    "unsupported_additions",
                    "cognitive_burden",
                ):
                    if not isinstance(observation.get(key), list):
                        errors.append(
                            f"{path}:{case_id}:{label}:{key} must be an array"
                        )
        if review.get("material_decision_difference") not in (
            MATERIAL_DIFFERENCE_VALUES
        ):
            errors.append(f"{path}:{case_id}:invalid material difference")
        identity = review.get("identity_guess_after_substantive_review")
        if not isinstance(identity, Mapping) or identity.get(
            "arm_with_added_external_context"
        ) not in IDENTITY_GUESS_VALUES:
            errors.append(f"{path}:{case_id}:invalid identity guess")
        if not isinstance(review.get("inspection_limits"), list):
            errors.append(f"{path}:{case_id}:inspection_limits must be an array")

    for review in standdowns:
        if not isinstance(review, Mapping):
            errors.append(f"{path}:standdown review is not an object")
            continue
        case_id = _text(review.get("case_id"))
        if review.get("standdown_support") not in STANDDOWN_SUPPORT_VALUES:
            errors.append(f"{path}:{case_id}:invalid standdown support")
        for key in (
            "source_basis",
            "risk_of_forced_additional_analysis",
            "semantic_limits_of_mechanical_observation",
        ):
            if not isinstance(review.get(key), list):
                errors.append(f"{path}:{case_id}:{key} must be an array")
    return errors


def _actual_added_context_label(sealed_case: Mapping[str, Any]) -> str:
    arm_map = sealed_case.get("arm_map")
    if not isinstance(arm_map, Mapping):
        return "indistinguishable"
    labels = [
        label
        for label, record in arm_map.items()
        if isinstance(record, Mapping)
        and record.get("origin")
        == "reconsideration_with_added_external_context"
    ]
    if len(labels) == 1:
        return str(labels[0])
    return "indistinguishable"


def _validate_exact_case_ids(
    records: Sequence[Any], expected: Sequence[str], path: str
) -> list[str]:
    actual = [
        _text(record.get("case_id"))
        for record in records
        if isinstance(record, Mapping)
    ]
    if actual != list(expected):
        return [f"{path}:case ids or order mismatch"]
    return []


def _case_ids(value: Any) -> list[str]:
    return [
        _text(item.get("case_id"))
        for item in _list(value)
        if isinstance(item, Mapping)
    ]


def _index_cases(value: Any) -> dict[str, Mapping[str, Any]]:
    return {
        _text(item.get("case_id")): item
        for item in _list(value)
        if isinstance(item, Mapping) and _text(item.get("case_id"))
    }


def _walk_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, Mapping):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_walk_keys(child))
    return keys


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProductDeltaPairedScreenReviewError(
            f"review input is invalid JSON:{relpath}"
        ) from exc
    except OSError as exc:
        raise ProductDeltaPairedScreenReviewError(
            f"review input could not be read:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaPairedScreenReviewError(
            f"review input is not an object:{relpath}"
        )
    return payload, {
        "path": relpath,
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    path = (root / relpath).resolve()
    if path != root and root not in path.parents:
        raise ProductDeltaPairedScreenReviewError("path escapes repository root")
    return path


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""
