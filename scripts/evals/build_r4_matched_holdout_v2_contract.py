#!/usr/bin/env python3
"""Build the provider-free leakage-corrected R4 matched holdout v2 package."""

from __future__ import annotations

import argparse
import hashlib
import copy
import json
import re
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any

from engine.system_b.conversation_state_fan_in import build_source_registry
from engine.system_b.r4_complementary_readers import (
    UNCERTAINTY_PACKET_SCHEMA,
    canonical_json_bytes,
    uncertainty_response_schema_v1,
    value_sha256,
)
from engine.system_b.r4_residual_task import (
    build_residual_prompts_v1,
    residual_response_schema_v1,
)
from engine.system_b.r4_semantic_distinction import build_uncertainty_prompts_v2


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
TARGET_REVIEW_PATH = (
    ROOT / "docs/evals/lolla-r4-matched-holdout-v2-target-review.json"
)
CONTRACT_PATH = ROOT / "docs/evals/lolla-r4-matched-holdout-v2-contract.json"
REQUEST_OUTPUT_ROOT = (
    ROOT / "research/lolla-r4-matched-holdout-v2-contract-2026-07-14"
)
PRACTICE_PATH = ROOT / (
    "docs/conversation-understanding/"
    "lolla-r4-matched-holdout-v2-current-practice-2026-07-14.md"
)
RUNNER_PATH = ROOT / "scripts/evals/run_r4_matched_holdout_v2_experiment.py"
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
SEEDS = {
    "r4h2-case01-community-audio-archive": 10101,
    "r4h2-case02-serialized-essay-pilot": 10201,
    "r4h2-case03-research-workspace-service": 10301,
    "r4h2-case04-shared-language-course": 10401,
}
PROVIDER = {
    "allow_fallbacks": False,
    "data_collection": "deny",
    "max_price": {"completion": 1.5, "prompt": 0.25},
    "only": ["google-vertex"],
    "order": ["google-vertex"],
    "require_parameters": True,
    "zdr": True,
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
    """Report the current human-gate state without deciding semantic meaning."""

    review = build_human_review_record(
        cases,
        declaration=HUMAN_LEAKAGE_DECLARATION,
    )
    return {
        "schema_version": "lolla.r4_matched_holdout_pre_target_audit.v2",
        "status": "human_review_passed_target_authorship_unlocked",
        "deterministic_vocabulary_lint": lint_v2_source_prior(cases),
        "human_review_required_before_target": "satisfied",
        "deterministic_semantic_sufficiency_decided": False,
        "human_semantic_sufficiency_decided": True,
        "human_declaration": HUMAN_LEAKAGE_DECLARATION,
        "target_authored": TARGET_PATH.exists(),
        "request_preview_authored": CONTRACT_PATH.exists(),
        "cases": review["cases"],
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


def load_source_first_target() -> dict[str, Any]:
    """Load protected human targets after exact pre-target custody validation."""

    validate_human_review_freeze()
    target = _load(TARGET_PATH)
    if target.get("status") != "frozen_after_human_review_before_request_previews":
        raise R4MatchedHoldoutV2Error("source-first target status drifted")
    if target.get("human_leakage_review", {}).get("declaration") != (
        HUMAN_LEAKAGE_DECLARATION
    ):
        raise R4MatchedHoldoutV2Error("source-first target human declaration drifted")
    freeze = target.get("source_prior_freeze_manifest", {})
    if (
        freeze.get("path") != _relative(FREEZE_MANIFEST_PATH)
        or freeze.get("sha256") != _sha(FREEZE_MANIFEST_PATH)
    ):
        raise R4MatchedHoldoutV2Error("source-first target freeze reference drifted")
    review = target.get("human_leakage_review", {})
    if (
        review.get("path") != _relative(LEAKAGE_AUDIT_PATH)
        or review.get("sha256") != _sha(LEAKAGE_AUDIT_PATH)
    ):
        raise R4MatchedHoldoutV2Error("source-first target review reference drifted")

    cases = load_v2_source_prior()
    rows = target.get("cases")
    if not isinstance(rows, list) or [row.get("case_id") for row in rows] != list(
        CASE_IDS
    ):
        raise R4MatchedHoldoutV2Error("source-first target case identity drifted")
    for row in rows:
        case_id = str(row["case_id"])
        case = cases[case_id]
        if (
            row.get("source_sha256") != case["source_sha256"]
            or row.get("prior_sha256") != case["prior_sha256"]
        ):
            raise R4MatchedHoldoutV2Error(
                f"source-first target input drifted: {case_id}"
            )
        aliases = {
            f"e{int(message['message_index']):03d}"
            for message in case["source"]["messages"]
        }
        surfaces = row.get("canonical_surface_targets")
        if not isinstance(surfaces, Mapping) or set(surfaces) != {
            "unresolved_matter",
            "reopen_condition",
        }:
            raise R4MatchedHoldoutV2Error(
                f"source-first target surfaces drifted: {case_id}"
            )
        for surface, surface_target in surfaces.items():
            if not isinstance(surface_target, Mapping):
                raise R4MatchedHoldoutV2Error(
                    f"source-first target surface is invalid: {case_id}/{surface}"
                )
            required = {
                "disposition",
                "expected_modal_force",
                "expected_result",
                "expected_speaker_ownership",
                "outside_adopted_machinery_reason",
                "strongest_source_aliases",
            }
            if set(surface_target) != required:
                raise R4MatchedHoldoutV2Error(
                    f"source-first target fields drifted: {case_id}/{surface}"
                )
            strongest = surface_target["strongest_source_aliases"]
            if (
                not isinstance(strongest, list)
                or len(strongest) < 3
                or len(strongest) != len(set(strongest))
                or not set(strongest).issubset(aliases)
            ):
                raise R4MatchedHoldoutV2Error(
                    f"source-first target aliases drifted: {case_id}/{surface}"
                )
            result = surface_target["expected_result"]
            disposition = surface_target["disposition"]
            if disposition == "supported":
                indices = [int(alias[1:]) for alias in strongest]
                if len(indices) < 3 or any(
                    right - left <= 1
                    for left, right in zip(indices, indices[1:])
                ):
                    raise R4MatchedHoldoutV2Error(
                        f"supported target evidence is not distributed: {case_id}/{surface}"
                    )
                if (
                    not isinstance(result, Mapping)
                    or result.get("outcome") != "records_present"
                    or not isinstance(result.get("records"), list)
                    or len(result["records"]) != 1
                    or set(result["records"][0].get("evidence_ids", []))
                    != set(strongest)
                ):
                    raise R4MatchedHoldoutV2Error(
                        f"supported target result drifted: {case_id}/{surface}"
                    )
            elif disposition == "quiet":
                if result != {
                    "outcome": "no_supported_record_observed",
                    "records": [],
                }:
                    raise R4MatchedHoldoutV2Error(
                        f"quiet target result drifted: {case_id}/{surface}"
                    )
            else:
                raise R4MatchedHoldoutV2Error(
                    f"unexpected target disposition: {case_id}/{surface}"
                )
    return target


def build_source_first_target_review() -> dict[str, Any]:
    """Hash-bind the protected target after review and before request previews."""

    load_source_first_target()
    return {
        "schema_version": "lolla.r4_matched_holdout_target_review.v2",
        "status": "protected_target_frozen_before_requests",
        "date": "2026-07-14",
        "human_review_checkpoint_commit": (
            "04706f67620b2548754454178a594d30228925ac"
        ),
        "target": {
            "path": _relative(TARGET_PATH),
            "sha256": _sha(TARGET_PATH),
            "utf8_bytes": len(TARGET_PATH.read_bytes()),
            "review_method": (
                "human_source_first_product_ontology_before_any_provider_output"
            ),
        },
        "source_prior_freeze_manifest": {
            "path": _relative(FREEZE_MANIFEST_PATH),
            "sha256": _sha(FREEZE_MANIFEST_PATH),
        },
        "human_leakage_review": {
            "path": _relative(LEAKAGE_AUDIT_PATH),
            "sha256": _sha(LEAKAGE_AUDIT_PATH),
            "declaration": HUMAN_LEAKAGE_DECLARATION,
        },
        "request_previews_existed_when_target_frozen": False,
        "provider_outputs_existed_when_target_frozen": False,
        "provider_visible": False,
        "runner_may_load_review_metadata": False,
        "semantic_judgment_owner": "human_source_first_review",
        "deterministic_code_owns_only": [
            "artifact_identity",
            "exact_hashes",
            "source_alias_admission",
            "freeze_order",
        ],
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "authorization_existed": False,
    }


def write_source_first_target_review() -> dict[str, Any]:
    """Write protected review metadata only before request artifacts exist."""

    request_root = (
        ROOT / "research/lolla-r4-matched-holdout-v2-contract-2026-07-14"
    )
    if request_root.exists() or CONTRACT_PATH.exists():
        raise R4MatchedHoldoutV2Error(
            "protected target review must predate request artifacts"
        )
    TARGET_REVIEW_PATH.write_bytes(_render(build_source_first_target_review()))
    return validate_source_first_target_freeze()


def validate_source_first_target_freeze() -> dict[str, Any]:
    """Validate protected target and review metadata without exposing either."""

    expected = build_source_first_target_review()
    if not TARGET_REVIEW_PATH.is_file() or _load(TARGET_REVIEW_PATH) != expected:
        raise R4MatchedHoldoutV2Error("protected target review metadata drifted")
    return expected


def _packet(case: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    source = case["source"]
    prior = case["prior"]
    aliases: list[dict[str, Any]] = []
    registry_aliases: list[dict[str, Any]] = []
    for row in source["messages"]:
        message_index = int(row["message_index"])
        alias = f"e{message_index:03d}"
        text_value = str(row["text"])
        text_sha = hashlib.sha256(text_value.encode("utf-8")).hexdigest()
        turn_index = (message_index + 1) // 2
        aliases.append(
            {
                "alias": alias,
                "speaker": row["speaker"],
                "text": text_value,
                "text_sha256": text_sha,
                "turn_index": turn_index,
            }
        )
        registry_aliases.append(
            {
                "alias": alias,
                "span_id": f"span-{source['case_id']}-{message_index:03d}",
                "speaker": row["speaker"],
                "text_sha256": text_sha,
                "turn_index": turn_index,
            }
        )
    source_path = str(case["source_path"])
    source_bytes = (ROOT / source_path).read_bytes()
    registry = build_source_registry(
        case_id=str(source["case_id"]),
        source_path=source_path,
        source_bytes=source_bytes,
        message_count=int(source["message_count"]),
        aliases=registry_aliases,
    )
    packet_body = {
        "schema_version": UNCERTAINTY_PACKET_SCHEMA,
        "status": "provider_free_matched_holdout_v2_input_frozen",
        "case_id": source["case_id"],
        "source": {
            "path": source_path,
            "sha256": case["source_sha256"],
            "message_count": source["message_count"],
            "aliases": aliases,
        },
        "prior_interpretation_context": {
            "artifact_path": case["prior_path"],
            "artifact_sha256": case["prior_sha256"],
            "records": copy.deepcopy(prior["records"]),
            "qualification_review": copy.deepcopy(prior["qualification_review"]),
            "authority": prior["authority"],
        },
        "task_contract": {
            "surfaces": ["unresolved_matter", "reopen_condition"],
            "maximum_records_per_surface": 2,
            "valid_zero_output": True,
            "valid_ambiguous_output": True,
            "source_supported_inference_allowed": True,
            "external_fact_invention_allowed": False,
        },
        "boundary": {
            "authoritative_source_precedes_prior_interpretation_in_prompt": True,
            "semantic_meaning_decided_by_model": True,
            "prior_interpretations_may_be_incomplete": True,
            "deterministic_semantic_absence_inference": False,
            "keyword_or_chronology_gate": False,
            "quality_or_pressure_decision": False,
        },
    }
    return {**packet_body, "packet_sha256": value_sha256(packet_body)}, registry


def _request_preview(
    *,
    case_id: str,
    arm: str,
    prompts: Mapping[str, str],
    schema: Mapping[str, Any],
    schema_name: str,
) -> dict[str, Any]:
    body = {
        "max_tokens": 1600,
        "messages": [
            {"role": "system", "content": prompts["system_prompt"]},
            {"role": "user", "content": prompts["user_prompt"]},
        ],
        "model": "google/gemini-3.1-flash-lite",
        "provider": copy.deepcopy(PROVIDER),
        "reasoning": {"effort": "minimal", "exclude": True},
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "strict": True,
                "schema": copy.deepcopy(schema),
            },
        },
        "seed": SEEDS[case_id],
        "stream": False,
    }
    return {
        "schema_version": "lolla.r4_matched_residual_request_preview.v2",
        "status": "provider_free_preview_not_authorized_for_transport",
        "case_id": case_id,
        "arm": arm,
        "body": body,
        "body_sha256": value_sha256(body),
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
        "authorization_present": False,
    }


def _estimated_tokens(utf8_bytes: int) -> int:
    return (utf8_bytes + 1) // 2


def _component(name: str, raw: bytes) -> dict[str, Any]:
    return {
        "name": name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "utf8_bytes": len(raw),
        "estimated_tokens": _estimated_tokens(len(raw)),
    }


def _context_manifest(
    *,
    case: Mapping[str, Any],
    packet: Mapping[str, Any],
    preview: Mapping[str, Any],
    prompts: Mapping[str, str],
    schema: Mapping[str, Any],
) -> dict[str, Any]:
    body = preview["body"]
    user = prompts["user_prompt"]
    source_text = canonical_json_bytes(packet["source"]).decode("utf-8")
    prior_text = canonical_json_bytes(
        packet["prior_interpretation_context"]
    ).decode("utf-8")
    task_start = user.index("<task>\n") + len("<task>\n")
    task_end = user.index("\n</task>", task_start)
    task = user[task_start:task_end]
    source_raw = source_text.encode("utf-8")
    prior_raw = prior_text.encode("utf-8")
    system_raw = prompts["system_prompt"].encode("utf-8")
    task_raw = task.encode("utf-8")
    schema_raw = canonical_json_bytes(schema)
    message_bytes = sum(
        len(row["content"].encode("utf-8")) for row in body["messages"]
    )
    complete = (
        user.count(source_text) == 1
        and len(packet["source"]["aliases"])
        == len(case["source"]["messages"])
        and [row["text"] for row in packet["source"]["aliases"]]
        == [row["text"] for row in case["source"]["messages"]]
    )
    return {
        "schema_version": "lolla.r4_matched_residual_context_manifest.v2",
        "case_id": packet["case_id"],
        "arm": preview["arm"],
        "section_order": [
            "system_instruction",
            "authoritative_source",
            "fallible_prior_interpretation_context",
            "task",
        ],
        "context_components": [
            _component("system_instruction", system_raw),
            _component("authoritative_source", source_raw),
            _component("fallible_prior_interpretation_context", prior_raw),
            _component("task", task_raw),
            _component("schema", schema_raw),
        ],
        "source": {
            "artifact_path": case["source_path"],
            "artifact_sha256": case["source_sha256"],
            "artifact_utf8_bytes": len((ROOT / case["source_path"]).read_bytes()),
            "canonical_context_sha256": hashlib.sha256(source_raw).hexdigest(),
            "canonical_context_utf8_bytes": len(source_raw),
            "estimated_tokens": _estimated_tokens(len(source_raw)),
            "message_count": packet["source"]["message_count"],
            "alias_count": len(packet["source"]["aliases"]),
            "included_exactly_once": user.count(source_text) == 1,
            "summarized_or_chunked": False,
        },
        "prior": {
            "artifact_path": case["prior_path"],
            "artifact_sha256": case["prior_sha256"],
            "artifact_utf8_bytes": len((ROOT / case["prior_path"]).read_bytes()),
            "canonical_context_sha256": hashlib.sha256(prior_raw).hexdigest(),
            "canonical_context_utf8_bytes": len(prior_raw),
            "estimated_tokens": _estimated_tokens(len(prior_raw)),
            "record_count": len(packet["prior_interpretation_context"]["records"]),
            "included_exactly_once": user.count(prior_text) == 1,
            "summarized_or_reordered": False,
            "fallible_authority": packet["prior_interpretation_context"]["authority"],
        },
        "complete_source_inclusion": complete,
        "source_then_prior_order": user.index(source_text) < user.index(prior_text),
        "task_at_end_invariant": user.rstrip().endswith("</task>"),
        "fallible_prior_declaration": "fallible" in prompts["system_prompt"].lower(),
        "schema_labels_and_descriptions_are_model_context": True,
        "request_estimate": {
            "message_utf8_bytes": message_bytes,
            "schema_utf8_bytes": len(schema_raw),
            "total_context_utf8_bytes": message_bytes + len(schema_raw),
            "estimated_input_tokens": _estimated_tokens(
                message_bytes + len(schema_raw)
            ),
            "estimator": "ceil((message_utf8_bytes+schema_utf8_bytes)/2); deterministic conservative estimate, not provider tokenization",
            "maximum_output_tokens": body["max_tokens"],
            "canonical_body_utf8_bytes": len(canonical_json_bytes(body)),
            "canonical_body_sha256": value_sha256(body),
        },
        "matched_equal_request_fields": [
            "/max_tokens",
            "/model",
            "/provider",
            "/reasoning",
            "/seed",
            "/stream",
        ],
        "changed_provider_visible_semantic_fields": [
            "system role",
            "task operation",
            "surface vocabulary",
            "schema name",
            "schema enum labels and semantic descriptions",
            "minimal examples",
            "evidence wording",
            "output rules",
        ],
        "unchanged_dimensions": [
            "authoritative source bytes and canonical context",
            "fallible prior bytes, records, and canonical context",
            "source then prior then task order",
            "paired two-surface task shape",
            "record fields and bounds",
            "model and pinned provider route",
            "seed within each matched pair",
            "1600-token output allocation",
            "minimal excluded-reasoning envelope",
            "nonstreaming strict-JSON policy",
            "privacy and routing controls",
            "relationship, graph, runtime, and operator",
        ],
        "no_summary_chunking_filter_or_semantic_gate": True,
        "declared_omissions": [
            "protected review evidence",
            "provider output and provider authorization",
            "relationship, evaluator, embedding, graph, pipeline, and runtime calls",
            "retries, semantic retries, fallbacks, healing, and model substitution",
            "summaries, chunks, relevance filters, and deterministic semantic gates",
            "governed-pending output surface and task split",
        ],
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def build_request_preview_files() -> dict[str, bytes]:
    """Build provider-blind matched previews after protected review freeze."""

    validate_source_first_target_freeze()
    inputs = load_v2_source_prior()
    v2_schema = uncertainty_response_schema_v1()
    residual_schema = residual_response_schema_v1()
    files: dict[str, bytes] = {}
    for case_id in CASE_IDS:
        packet, registry = _packet(inputs[case_id])
        prompts_a = build_uncertainty_prompts_v2(packet)
        prompts_b = build_residual_prompts_v1(packet)
        arm_a = _request_preview(
            case_id=case_id,
            arm="A_frozen_v2_semantic_distinction",
            prompts=prompts_a,
            schema=v2_schema,
            schema_name="lolla_r4_uncertainty_v1",
        )
        arm_b = _request_preview(
            case_id=case_id,
            arm="B_frozen_residual_task",
            prompts=prompts_b,
            schema=residual_schema,
            schema_name="lolla_r4_residual_task_v1",
        )
        case_root = REQUEST_OUTPUT_ROOT / "cases" / case_id
        values = {
            "source-registry.json": registry,
            "uncertainty-packet.json": packet,
            "arm-a-prompts.json": prompts_a,
            "arm-a-request-preview.json": arm_a,
            "arm-b-prompts.json": prompts_b,
            "arm-b-request-preview.json": arm_b,
            "arm-a-context-manifest.json": _context_manifest(
                case=inputs[case_id],
                packet=packet,
                preview=arm_a,
                prompts=prompts_a,
                schema=v2_schema,
            ),
            "arm-b-context-manifest.json": _context_manifest(
                case=inputs[case_id],
                packet=packet,
                preview=arm_b,
                prompts=prompts_b,
                schema=residual_schema,
            ),
        }
        for name, value in values.items():
            files[_relative(case_root / name)] = _render(value)
    protected_terms = (
        "lolla-r4-matched-holdout-v2-target",
        "target-review",
        "leakage-audit",
        HUMAN_LEAKAGE_DECLARATION,
        '"target_role"',
    )
    for relative, raw in files.items():
        text_value = raw.decode("utf-8").lower()
        if any(term in text_value for term in protected_terms):
            raise R4MatchedHoldoutV2Error(
                f"protected review evidence leaked into preview: {relative}"
            )
    return files


def write_request_preview_files() -> dict[str, Any]:
    """Write request previews after protected review and before delta artifacts."""

    files = build_request_preview_files()
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return validate_request_preview_files()


def validate_request_preview_files() -> dict[str, Any]:
    """Validate exact preview bytes without provider transport."""

    expected = build_request_preview_files()
    for relative, raw in expected.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != raw:
            raise R4MatchedHoldoutV2Error(f"request preview drifted: {relative}")
    return {
        "status": "provider_blind_request_previews_valid",
        "case_count": len(CASE_IDS),
        "request_count": len(CASE_IDS) * 2,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def _json_difference_paths(left: Any, right: Any, path: str = "") -> list[str]:
    if type(left) is not type(right):
        return [path]
    if isinstance(left, dict):
        result: list[str] = []
        for key in sorted(set(left) | set(right)):
            child = f"{path}/{key}"
            if key not in left or key not in right:
                result.append(child)
            else:
                result.extend(_json_difference_paths(left[key], right[key], child))
        return result
    if isinstance(left, list):
        if len(left) != len(right):
            return [path]
        result = []
        for index, (left_value, right_value) in enumerate(zip(left, right)):
            result.extend(
                _json_difference_paths(left_value, right_value, f"{path}/{index}")
            )
        return result
    return [] if left == right else [path]


def validate_matched_request_pair(
    *,
    packet: Mapping[str, Any],
    arm_a: Mapping[str, Any],
    arm_b: Mapping[str, Any],
) -> dict[str, Any]:
    """Rebuild both arms and reject every difference outside the intervention."""

    case_id = str(packet["case_id"])
    v2_schema = uncertainty_response_schema_v1()
    residual_schema = residual_response_schema_v1()
    expected_a = _request_preview(
        case_id=case_id,
        arm="A_frozen_v2_semantic_distinction",
        prompts=build_uncertainty_prompts_v2(packet),
        schema=v2_schema,
        schema_name="lolla_r4_uncertainty_v1",
    )
    expected_b = _request_preview(
        case_id=case_id,
        arm="B_frozen_residual_task",
        prompts=build_residual_prompts_v1(packet),
        schema=residual_schema,
        schema_name="lolla_r4_residual_task_v1",
    )
    if dict(arm_a) != expected_a:
        raise R4MatchedHoldoutV2Error(
            "arm A request does not equal the exact frozen v2 construction"
        )
    if dict(arm_b) != expected_b:
        raise R4MatchedHoldoutV2Error(
            "arm B request does not equal the exact frozen residual construction"
        )
    allowed_schema_differences = [
        "/description",
        "/properties/reviews/description",
        "/properties/reviews/items/description",
        "/properties/reviews/items/properties/outcome/description",
        "/properties/reviews/items/properties/records/description",
        "/properties/reviews/items/properties/records/items/description",
        "/properties/reviews/items/properties/records/items/properties/evidence_ids/description",
        "/properties/reviews/items/properties/records/items/properties/interpretation/description",
        "/properties/reviews/items/properties/records/items/properties/limitations/description",
        "/properties/reviews/items/properties/records/items/properties/support/description",
        "/properties/reviews/items/properties/surface/description",
        "/properties/reviews/items/properties/surface/enum/0",
        "/properties/reviews/items/properties/surface/enum/1",
    ]
    schema_differences = _json_difference_paths(v2_schema, residual_schema)
    undeclared = sorted(set(schema_differences) - set(allowed_schema_differences))
    equal_fields = [
        f"/{field}"
        for field in (
            "max_tokens",
            "model",
            "provider",
            "reasoning",
            "seed",
            "stream",
        )
        if arm_a["body"][field] == arm_b["body"][field]
    ]
    if len(equal_fields) != 6 or undeclared:
        raise R4MatchedHoldoutV2Error("undeclared matched request delta")
    source_text = canonical_json_bytes(packet["source"]).decode("utf-8")
    prior_text = canonical_json_bytes(
        packet["prior_interpretation_context"]
    ).decode("utf-8")
    users = [
        arm_a["body"]["messages"][1]["content"],
        arm_b["body"]["messages"][1]["content"],
    ]
    matched_context = all(
        user.count(source_text) == 1
        and user.count(prior_text) == 1
        and user.index(source_text) < user.index(prior_text) < user.index("<task>")
        for user in users
    )
    if not matched_context:
        raise R4MatchedHoldoutV2Error("undeclared matched request delta")
    return {
        "schema_version": "lolla.r4_matched_request_delta.v2",
        "case_id": case_id,
        "matched_source_and_prior": True,
        "equal_body_fields": equal_fields,
        "allowed_provider_visible_change_categories": [
            "role",
            "task operation",
            "surface vocabulary",
            "schema name and enum descriptions",
            "examples",
            "evidence wording",
            "output rules",
        ],
        "changed_body_paths": [
            "/messages/0/content",
            "/messages/1/content/task_operation_and_vocabulary_only",
            "/response_format/json_schema/name",
            "/response_format/json_schema/schema/declared_semantic_labels_and_descriptions_only",
        ],
        "schema_difference_paths": schema_differences,
        "undeclared_differences": [],
        "paired_task_shape_unchanged": True,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def build_matched_delta_files() -> dict[str, bytes]:
    """Build declared matched deltas only after exact previews are frozen."""

    validate_request_preview_files()
    files: dict[str, bytes] = {}
    for case_id in CASE_IDS:
        case_root = REQUEST_OUTPUT_ROOT / "cases" / case_id
        delta = validate_matched_request_pair(
            packet=_load(case_root / "uncertainty-packet.json"),
            arm_a=_load(case_root / "arm-a-request-preview.json"),
            arm_b=_load(case_root / "arm-b-request-preview.json"),
        )
        files[_relative(case_root / "matched-request-delta.json")] = _render(delta)
    return files


def write_matched_delta_files() -> dict[str, Any]:
    files = build_matched_delta_files()
    for relative, raw in files.items():
        (ROOT / relative).write_bytes(raw)
    return validate_matched_delta_files()


def validate_matched_delta_files() -> dict[str, Any]:
    expected = build_matched_delta_files()
    for relative, raw in expected.items():
        if not (ROOT / relative).is_file() or (ROOT / relative).read_bytes() != raw:
            raise R4MatchedHoldoutV2Error(
                f"matched request delta drifted: {relative}"
            )
    return {
        "status": "exact_matched_request_deltas_valid",
        "case_count": len(CASE_IDS),
        "undeclared_difference_count": 0,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }


def _request_case_records() -> dict[str, dict[str, Any]]:
    inputs = load_v2_source_prior()
    records: dict[str, dict[str, Any]] = {}
    for case_id in CASE_IDS:
        case_root = REQUEST_OUTPUT_ROOT / "cases" / case_id
        arm_records: dict[str, dict[str, Any]] = {}
        for key, label in (
            ("A", "A_frozen_v2_semantic_distinction"),
            ("B", "B_frozen_residual_task"),
        ):
            preview_path = case_root / f"arm-{key.lower()}-request-preview.json"
            context_path = case_root / f"arm-{key.lower()}-context-manifest.json"
            preview = _load(preview_path)
            context = _load(context_path)
            estimated_input = context["request_estimate"]["estimated_input_tokens"]
            estimated_cost = round(
                estimated_input * 0.25 / 1_000_000
                + 1600 * 1.5 / 1_000_000,
                9,
            )
            if preview.get("arm") != label:
                raise R4MatchedHoldoutV2Error(f"request arm drifted: {case_id}/{key}")
            arm_records[key] = {
                "arm": label,
                "request_preview_path": _relative(preview_path),
                "request_body_sha256": preview["body_sha256"],
                "context_manifest_path": _relative(context_path),
                "estimated_input_tokens": estimated_input,
                "maximum_output_tokens": 1600,
                "conservative_estimated_cost_usd": estimated_cost,
            }
        packet_path = case_root / "uncertainty-packet.json"
        records[case_id] = {
            "case_id": case_id,
            "source_path": inputs[case_id]["source_path"],
            "source_sha256": inputs[case_id]["source_sha256"],
            "prior_path": inputs[case_id]["prior_path"],
            "prior_sha256": inputs[case_id]["prior_sha256"],
            "packet_path": _relative(packet_path),
            "packet_sha256": _sha(packet_path),
            "source_registry_path": _relative(case_root / "source-registry.json"),
            "matched_request_delta_path": _relative(
                case_root / "matched-request-delta.json"
            ),
            "arms": arm_records,
            "matched_case_cost_usd": round(
                sum(
                    arm["conservative_estimated_cost_usd"]
                    for arm in arm_records.values()
                ),
                9,
            ),
        }
    return records


def build_contract_files() -> dict[str, bytes]:
    """Build the non-authorizing execution package after all request deltas."""

    validate_matched_delta_files()
    validate_source_first_target_freeze()
    if not PRACTICE_PATH.is_file() or not RUNNER_PATH.is_file():
        raise R4MatchedHoldoutV2Error("practice note or future runner is absent")
    runner_source = RUNNER_PATH.read_text(encoding="utf-8").lower()
    if any(
        phrase in runner_source
        for phrase in ("target", "leakage-audit", HUMAN_LEAKAGE_DECLARATION)
    ):
        raise R4MatchedHoldoutV2Error("future runner can discover protected review")

    case_records = _request_case_records()
    order = (
        (CASE_IDS[0], "A"),
        (CASE_IDS[0], "B"),
        (CASE_IDS[1], "B"),
        (CASE_IDS[1], "A"),
        (CASE_IDS[2], "B"),
        (CASE_IDS[2], "A"),
        (CASE_IDS[3], "A"),
        (CASE_IDS[3], "B"),
    )
    call_plan: list[dict[str, Any]] = []
    for ordinal, (case_id, arm_key) in enumerate(order, 1):
        arm = case_records[case_id]["arms"][arm_key]
        call_plan.append(
            {
                "ordinal": ordinal,
                "case_id": case_id,
                "arm": arm["arm"],
                "request_preview_path": arm["request_preview_path"],
                "request_body_sha256": arm["request_body_sha256"],
                "conservative_estimated_cost_usd": arm[
                    "conservative_estimated_cost_usd"
                ],
            }
        )
    total_estimate = round(
        sum(row["conservative_estimated_cost_usd"] for row in call_plan), 9
    )
    if total_estimate != 0.040521:
        raise R4MatchedHoldoutV2Error("v2 conservative cost estimate drifted")

    v2_schema = uncertainty_response_schema_v1()
    residual_schema = residual_response_schema_v1()
    frozen_history = {
        "v1_module_sha256": _sha(
            ROOT / "engine/system_b/r4_complementary_readers.py"
        ),
        "v2_module_sha256": _sha(
            ROOT / "engine/system_b/r4_semantic_distinction.py"
        ),
        "residual_module_sha256": _sha(
            ROOT / "engine/system_b/r4_residual_task.py"
        ),
        "v2_schema_sha256": value_sha256(v2_schema),
        "residual_schema_sha256": value_sha256(residual_schema),
        "rejected_v1_checkpoint": "b46464278e86f4c5d6c53e154bc272d93f09b116",
        "provider_free_corpus_replay": {
            "cases": 12,
            "case_artifact_links": 543,
            "unique_frozen_json_artifacts": 400,
        },
    }
    expected_history = {
        "v1_module_sha256": "9253290093e62f62a9adbf8902ccf010ac4d4417c345222e4756e771496bf777",
        "v2_module_sha256": "e774b19cd2bac461e6d586dffbde48515ab23d6f73e1eb158ed87bdcdccdf3c8",
        "residual_module_sha256": "726d4bc649e8e488b5783906785fc3b481ba3ce295dac5155fcff8cd0a83616a",
        "v2_schema_sha256": "12327510a78c24bcc1b89e874112517288e1a2054159def729da094de1404a65",
        "residual_schema_sha256": "70e62d8faa27fcff6517ebaf54433ecd8f534690d86cfc6d219a1e8420b42087",
        "rejected_v1_checkpoint": "b46464278e86f4c5d6c53e154bc272d93f09b116",
        "provider_free_corpus_replay": {
            "cases": 12,
            "case_artifact_links": 543,
            "unique_frozen_json_artifacts": 400,
        },
    }
    if frozen_history != expected_history:
        raise R4MatchedHoldoutV2Error("historical v1/v2/residual boundary drifted")

    visible_paths = sorted(
        path
        for path in REQUEST_OUTPUT_ROOT.glob("cases/**/*.json")
        if path.name
        in {
            "source-registry.json",
            "uncertainty-packet.json",
            "arm-a-request-preview.json",
            "arm-b-request-preview.json",
            "arm-a-context-manifest.json",
            "arm-b-context-manifest.json",
            "matched-request-delta.json",
        }
    )
    execution_manifest = {
        "schema_version": "lolla.r4_matched_residual_execution_manifest.v2",
        "status": "frozen_runner_visible_inputs_no_authorization",
        "files": [
            {
                "path": _relative(path),
                "sha256": _sha(path),
                "utf8_bytes": len(path.read_bytes()),
            }
            for path in visible_paths
        ],
        "protected_review_reference_present": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    execution_path = REQUEST_OUTPUT_ROOT / "execution-manifest.json"
    execution_raw = _render(execution_manifest)

    contract = {
        "schema_version": "lolla.r4_matched_residual_holdout_contract.v2",
        "status": "provider_free_matched_holdout_v2_frozen_no_authorization",
        "date": "2026-07-14",
        "run_id": "lolla-r4-matched-residual-holdout-v2",
        "falsifiable_question": "On the same new hidden long-form evidence, does the residual-task contract improve false-positive restraint over frozen v2 while preserving sensitivity to materially distinct residuals?",
        "cases": [case_records[case_id] for case_id in CASE_IDS],
        "call_plan": call_plan,
        "counterbalancing": {
            "fixed_before_execution": True,
            "arm_a_first_cases": [CASE_IDS[0], CASE_IDS[3]],
            "arm_b_first_cases": [CASE_IDS[1], CASE_IDS[2]],
            "same_seed_within_each_case": True,
        },
        "operator": {
            "endpoint": "https://openrouter.ai/api/v1/chat/completions",
            "model": "google/gemini-3.1-flash-lite",
            "allowed_served_model_ids": [
                "google/gemini-3.1-flash-lite",
                "google/gemini-3.1-flash-lite-20260507",
            ],
            "provider_slug": "google-vertex",
            "allowed_served_provider_names": ["Google"],
            "provider_order": ["google-vertex"],
            "provider_only": ["google-vertex"],
            "allow_fallbacks": False,
            "require_parameters": True,
            "data_collection": "deny",
            "zdr": True,
            "maximum_price_usd_per_million_tokens": {
                "prompt": 0.25,
                "completion": 1.5,
            },
            "seed_policy": "one fixed seed per case, byte-identical between arms",
            "maximum_output_tokens": 1600,
            "reasoning": {"effort": "minimal", "exclude": True},
            "stream": False,
            "strict_json_schema": True,
        },
        "budget": {
            "maximum_provider_calls": 8,
            "hard_provider_reported_cost_per_case_usd": 0.03,
            "hard_provider_reported_cost_total_usd": 0.12,
            "conservative_estimated_total_cost_usd": total_estimate,
            "automatic_retries": 0,
            "semantic_retries": 0,
            "fallback_models": 0,
            "response_healing": False,
            "relationship_calls": 0,
            "evaluator_calls": 0,
            "embedding_calls": 0,
            "graph_calls": 0,
            "pipeline_calls": 0,
            "runtime_calls": 0,
        },
        "execution_envelope": {
            "first_terminal_provider_result_preserved_exactly": True,
            "stop_on_transport_failure": True,
            "stop_on_provider_identity_failure": True,
            "stop_on_budget_failure": True,
            "stop_on_schema_or_local_admission_failure": True,
            "stop_on_reasoning_custody_failure": True,
            "stop_on_authorization_failure": True,
            "generation_identity_required": True,
            "exact_usage_and_provider_reported_cost_required": True,
            "request_and_raw_response_hashes_required": True,
            "no_retry_fallback_healing_or_substitution": True,
            "no_relationship_evaluator_embedding_graph_pipeline_or_runtime_calls": True,
            "execution_manifest_path": _relative(execution_path),
            "execution_manifest_sha256": hashlib.sha256(execution_raw).hexdigest(),
            "protected_review_access_possible": False,
        },
        "evaluation_contract": {
            "vector": [
                "mechanical_execution_and_exact_provider_attribution",
                "false_positive_restraint",
                "genuine_residual_sensitivity",
                "zero_versus_ambiguity_behavior",
                "evidence_precision",
                "semantic_surface_placement",
                "speaker_and_modal_fidelity",
                "prior_anchoring_resistance",
                "long_context_and_late_evidence_use",
                "operational_cost_and_custody",
            ],
            "scalar_quality_score": None,
            "mixed_findings_must_not_be_collapsed": True,
        },
        "decision_matrix": {
            "residual_task_identity_supported": "Residual passes all restraint and sensitivity gates while v2 repeats predicted broad-inventory errors.",
            "holdout_non_discriminating": "Both arms pass.",
            "residual_task_overcorrected": "Residual quiets controls but misses either genuine residual.",
            "residual_task_repair_insufficient": "Residual repeats safeguard, fallback, or review false positives.",
            "residual_task_regressed": "Residual performs materially worse than v2.",
            "semantic_result_not_evaluable": "Mechanical or custody failure prevents matched comparison.",
        },
        "current_official_practice": {
            "path": _relative(PRACTICE_PATH),
            "sha256": _sha(PRACTICE_PATH),
            "date_checked": "2026-07-14",
            "primary_sources_only": True,
        },
        "future_runner": {
            "path": _relative(RUNNER_PATH),
            "sha256": _sha(RUNNER_PATH),
            "network_transport_created_only_after_authorization": True,
            "dry_run_provider_calls": 0,
        },
        "future_authorization_shape": {
            "schema_version": "lolla.r4_matched_residual_holdout_authorization.v2",
            "artifact_created": False,
            "must_match_contract_sha256": True,
            "must_match_all_eight_request_hashes": True,
            "must_match_counterbalanced_order": True,
            "maximum_provider_calls": 8,
            "hard_provider_reported_cost_per_case_usd": 0.03,
            "hard_provider_reported_cost_total_usd": 0.12,
            "all_other_call_classes_zero": True,
        },
        "frozen_history": frozen_history,
        "decision_boundary": {
            "provider_calls_authorized": False,
            "authorization_file_present": False,
            "package_grants_authorization": False,
            "package_requests_authorization": False,
            "holdout_execution_authorized": False,
            "relationship_validation_authorized": False,
            "runtime_or_graph_integration_authorized": False,
            "model_comparison_authorized": False,
            "r5_authorized": False,
            "product_usefulness_claim_authorized": False,
        },
        "provider_calls_made": 0,
        "provider_cost_usd": 0.0,
        "non_claims": [
            "This design does not authorize or request a provider call.",
            "Provider-free contract and fixture validity are not model semantic validation.",
            "The four cases are simulated reliability evidence, not real-user evidence.",
            "A future matched result does not establish product usefulness or authorize integration.",
        ],
    }
    contract_raw = _render(contract)
    package_paths = sorted(
        [*visible_paths, PRACTICE_PATH, RUNNER_PATH]
    )
    package_manifest = {
        "schema_version": "lolla.r4_matched_residual_artifact_manifest.v2",
        "status": "provider_free_exact_holdout_v2_artifacts_frozen",
        "date": "2026-07-14",
        "files": [
            {
                "path": _relative(path),
                "sha256": _sha(path),
                "utf8_bytes": len(path.read_bytes()),
            }
            for path in package_paths
        ]
        + [
            {
                "path": _relative(execution_path),
                "sha256": hashlib.sha256(execution_raw).hexdigest(),
                "utf8_bytes": len(execution_raw),
            },
            {
                "path": _relative(CONTRACT_PATH),
                "sha256": hashlib.sha256(contract_raw).hexdigest(),
                "utf8_bytes": len(contract_raw),
            },
        ],
        "protected_review_reference_present": False,
        "provider_calls": 0,
        "provider_cost_usd": 0.0,
    }
    return {
        _relative(CONTRACT_PATH): contract_raw,
        _relative(execution_path): execution_raw,
        _relative(REQUEST_OUTPUT_ROOT / "manifest.json"): _render(package_manifest),
    }


def write_contract_package() -> dict[str, Any]:
    files = build_contract_files()
    for relative, raw in files.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    return validate_contract_package()


def validate_contract_package() -> dict[str, Any]:
    expected = build_contract_files()
    for relative, raw in expected.items():
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != raw:
            raise R4MatchedHoldoutV2Error(f"contract artifact drifted: {relative}")
    contract = _load(CONTRACT_PATH)
    if (
        contract.get("provider_calls_made") != 0
        or contract.get("provider_cost_usd") != 0.0
        or contract.get("decision_boundary", {}).get("provider_calls_authorized")
        is not False
    ):
        raise R4MatchedHoldoutV2Error("contract decision boundary drifted")
    return contract


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    contract = validate_contract_package() if args.validate_only else write_contract_package()
    print(
        json.dumps(
            {
                "status": contract["status"],
                "provider_calls_made": contract["provider_calls_made"],
                "provider_cost_usd": contract["provider_cost_usd"],
                "provider_calls_authorized": contract["decision_boundary"][
                    "provider_calls_authorized"
                ],
                "conservative_estimated_total_cost_usd": contract["budget"][
                    "conservative_estimated_total_cost_usd"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
