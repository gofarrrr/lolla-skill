"""Deterministic, provider-free Product Delta paired-screen corpus builder.

This module deepens the existing Product Delta evaluation owner. It assembles
checked-in source conversations and answer pairs into a freshly blinded review
corpus plus a separate sealed lineage manifest. It does not run Lolla, call a
provider, traverse the graph, change runtime behavior, read private archives,
score answer quality, or create human-validated evidence.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PAIRED_SCREEN_SCHEMA_VERSION = "lolla.product_delta_agent_paired_screen.v1"
SEALED_MANIFEST_SCHEMA_VERSION = (
    "lolla.product_delta_agent_paired_screen_sealed_manifest.v1"
)
CONTRACT_SCHEMA_VERSION = "lolla.product_delta_agent_paired_screen_contract.v1"
BLINDING_NAMESPACE = "lolla-product-delta-agent-screen-v1"

DEFAULT_CONTRACT_RELPATH = (
    "docs/evals/lolla-agent-only-paired-delta-screen-contract-v1.json"
)
DEFAULT_OUTPUT_DIR_RELPATH = (
    "research/agent-only-paired-delta-screen-2026-07-23"
)
DEFAULT_BLIND_PACKETS_RELPATH = (
    f"{DEFAULT_OUTPUT_DIR_RELPATH}/blind-packets.json"
)
DEFAULT_SEALED_MANIFEST_RELPATH = (
    f"{DEFAULT_OUTPUT_DIR_RELPATH}/sealed-manifest.json"
)

BOUNDARY = {
    "provider_calls": 0,
    "provider_cost_usd": 0,
    "private_archives_read": False,
    "runtime_invoked": False,
    "graph_traversal_invoked": False,
    "graph_or_runtime_changed": False,
    "skill_invoked": False,
    "human_validated": False,
    "ground_truth": False,
    "product_proof": False,
    "answer_quality_scored": False,
    "scalar_judgment_created": False,
    "automatic_agent_authority_created": False,
}

NON_CLAIMS = (
    "not human review",
    "not ground truth",
    "not judge calibration data",
    "not product proof",
    "not evidence that either answer is better for a human",
    "not evidence that the graph caused any observed difference",
    "not answer-quality scoring",
    "not agent authority",
    "not runtime or graph integration",
)

PAIR_SPECS: tuple[dict[str, Any], ...] = (
    {
        "case_id": "retailer-pilot-exact",
        "evidence_class": "complete_exact_pair",
        "source_mode": "packet_conversation",
        "source_path": (
            "research/independent-useful-fresh-pressure-pair-2026-07-12/"
            "control-packet.json"
        ),
        "result_path": (
            "research/independent-useful-fresh-pressure-pair-probe-2026-07-12/"
            "result.json"
        ),
        "baseline_locator": {"call_task_id": "control"},
        "added_context_locator": {"call_task_id": "pressure"},
        "historical_refs": [
            "research/independent-useful-fresh-pressure-pair-2026-07-12/report.json",
            (
                "docs/conversation-understanding/"
                "lolla-independent-phase5-pressure-pair-result-2026-07-12.md"
            ),
        ],
    },
    {
        "case_id": "museum-license-exact",
        "evidence_class": "complete_exact_pair",
        "source_mode": "packet_conversation",
        "source_path": (
            "research/fresh-reasoning-pressure-museum-packet-2026-07-12/"
            "control-packet.json"
        ),
        "result_path": (
            "research/fresh-reasoning-pressure-museum-pair-probe-2026-07-12/"
            "result.json"
        ),
        "baseline_locator": {"call_task_id": "control"},
        "added_context_locator": {"call_task_id": "pressure"},
        "historical_refs": [
            "research/fresh-reasoning-pressure-museum-packet-2026-07-12/report.json",
            (
                "docs/conversation-understanding/"
                "lolla-fresh-reasoning-pressure-museum-result-2026-07-12.md"
            ),
        ],
    },
    {
        "case_id": "consulting-launch-exact",
        "evidence_class": "complete_exact_pair",
        "source_mode": "plain_text",
        "source_path": "research/test-cases/case_user_has_plan_conversation.txt",
        "result_path": (
            "research/downstream-utility-quiet-pilot-2026-07-10/run/"
            "blind-outputs.json"
        ),
        "arm_key_path": (
            "research/downstream-utility-quiet-pilot-2026-07-10/run/"
            "arm-key.json"
        ),
        "baseline_locator": {"arm_id": "strong_reconsideration_control"},
        "added_context_locator": {"arm_id": "lolla_pressure_treatment"},
        "historical_refs": [
            (
                "research/downstream-utility-quiet-pilot-2026-07-10/"
                "provisional-review.json"
            ),
            (
                "research/downstream-utility-quiet-pilot-2026-07-10/"
                "pilot-result.md"
            ),
        ],
    },
    {
        "case_id": "founder-equity-partial",
        "evidence_class": "partial_source_view_research_calibration",
        "source_mode": "source_excerpts",
        "source_path": (
            "research/pre-step6-raw-artifact-fixtures/"
            "founder-grant-marcus-equity.raw-artifact-handoff.v1.json"
        ),
        "baseline_path": (
            "research/pre-step6-raw-artifact-answer-cores/"
            "founder-grant-marcus-equity.raw-answer-core.v1.json"
        ),
        "added_context_path": (
            "research/pre-step6-pressure-card-answer-cores/"
            "founder-grant-marcus-equity.native.pressure-answer-core.v1.json"
        ),
        "historical_refs": [
            (
                "research/pre-step6-pressure-vs-raw-comparisons/"
                "founder-grant-marcus-equity.pressure-vs-raw-comparison.v1.json"
            )
        ],
    },
    {
        "case_id": "consultant-report-partial",
        "evidence_class": "partial_source_view_research_calibration",
        "source_mode": "source_excerpts",
        "source_path": (
            "research/pre-step6-raw-artifact-fixtures/"
            "mid-level-consultant-report-2.raw-artifact-handoff.v1.json"
        ),
        "baseline_path": (
            "research/pre-step6-raw-artifact-answer-cores/"
            "mid-level-consultant-report-2.raw-answer-core.v1.json"
        ),
        "added_context_path": (
            "research/pre-step6-pressure-card-answer-cores/"
            "mid-level-consultant-report-2.native.pressure-answer-core.v1.json"
        ),
        "historical_refs": [
            (
                "research/pre-step6-pressure-vs-raw-comparisons/"
                "mid-level-consultant-report-2.pressure-vs-raw-comparison.v1.json"
            )
        ],
    },
    {
        "case_id": "phd-direction-partial",
        "evidence_class": "partial_source_view_research_calibration",
        "source_mode": "source_excerpts",
        "source_path": (
            "research/pre-step6-raw-artifact-fixtures/"
            "third-year-phd-student.raw-artifact-handoff.v1.json"
        ),
        "baseline_path": (
            "research/pre-step6-raw-artifact-answer-cores/"
            "third-year-phd-student.raw-answer-core.v1.json"
        ),
        "added_context_path": (
            "research/pre-step6-pressure-card-answer-cores/"
            "third-year-phd-student.native.pressure-answer-core.v1.json"
        ),
        "historical_refs": [
            (
                "research/pre-step6-pressure-vs-raw-comparisons/"
                "third-year-phd-student.pressure-vs-raw-comparison.v1.json"
            )
        ],
    },
)

NULL_CASE_ID = "retailer-pilot-exact-duplicate-null"
STANDDOWN_CASE_ID = "library-laptop-standdown"
TRAP_SET_RELPATH = "docs/evals/provisional-reviewer-trap-set-v0.json"
SEED_CASES_RELPATH = "docs/evals/product-delta-seed-cases-v0.json"
STANDDOWN_SOURCE_RELPATH = (
    "research/independent-phase5-cases-2026-07-12/"
    "quiet-library-laptop-case.txt"
)
STANDDOWN_RESULT_RELPATH = (
    "research/independent-quiet-library-standdown-2026-07-12/result.json"
)


class ProductDeltaPairedScreenInputError(ValueError):
    """Deterministic, sanitized paired-screen input error."""


def build_product_delta_paired_screen(
    *, repo_root: Path | str
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build the blind corpus and separate sealed lineage manifest."""

    root = Path(repo_root).resolve()
    contract, contract_ref = _read_json_ref(root, DEFAULT_CONTRACT_RELPATH)
    if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        raise ProductDeltaPairedScreenInputError(
            "paired-screen contract schema version mismatch"
        )

    blind_pairs: list[dict[str, Any]] = []
    sealed_pairs: list[dict[str, Any]] = []
    for spec in PAIR_SPECS:
        blind_case, sealed_case = _build_pair(root=root, spec=spec)
        blind_pairs.append(blind_case)
        sealed_pairs.append(sealed_case)

    null_blind, null_sealed = _build_null_pair(root=root)
    blind_pairs.append(null_blind)
    sealed_pairs.append(null_sealed)

    qualification_cases, trap_ref = _build_qualification_cases(root=root)
    standdown_case, standdown_sealed = _build_standdown_case(root=root)
    exclusions, seed_ref = _build_exclusions(root=root)

    blind_payload: dict[str, Any] = {
        "schema_version": PAIRED_SCREEN_SCHEMA_VERSION,
        "screen_id": "agent-only-paired-delta-screen-2026-07-23",
        "purpose": (
            "Test whether fresh agents can identify source-grounded, atomic "
            "differences between paired answers while preserving repetition, "
            "lost value, unsupported additions, ambiguity, and legitimate "
            "stand-down."
        ),
        "boundary": dict(BOUNDARY),
        "review_order": [
            "Read the source before either answer.",
            "Review qualification cases without access to their sealed expectations.",
            "Review each paired case without guessing what process produced either arm.",
            "Record atomic moves, grounding, lost value, unsupported additions, and cognitive burden.",
            "Record an arm-origin guess only after the substantive read; indistinguishable is allowed.",
            "Do not rank, score, vote, certify, or choose a better answer.",
            "Review the stand-down independently and preserve uncertainty.",
        ],
        "review_contract": contract["blind_review_contract"],
        "qualification_case_count": len(qualification_cases),
        "qualification_cases": qualification_cases,
        "paired_case_count": len(blind_pairs),
        "paired_cases": blind_pairs,
        "standdown_case_count": 1,
        "standdown_cases": [standdown_case],
        "non_claims": list(NON_CLAIMS),
    }
    blind_rendered = render_json(blind_payload)

    sealed_payload: dict[str, Any] = {
        "schema_version": SEALED_MANIFEST_SCHEMA_VERSION,
        "screen_id": blind_payload["screen_id"],
        "handling": {
            "show_to_fresh_reviewers": False,
            "unblind_only_after_substantive_reviews_are_frozen": True,
            "historical_refs_are_context_not_truth": True,
            "do_not_convert_disagreement_into_a_vote": True,
        },
        "boundary": dict(BOUNDARY),
        "contract_ref": contract_ref,
        "trap_set_ref": trap_ref,
        "seed_case_list_ref": seed_ref,
        "blind_packets": {
            "path": DEFAULT_BLIND_PACKETS_RELPATH,
            "sha256": _sha256_text(blind_rendered),
        },
        "paired_cases": sealed_pairs,
        "standdown_case": standdown_sealed,
        "excluded_checked_in_product_delta_cases": exclusions,
        "exclusion_policy": (
            "Existing summary-only Product Delta cases are not silently treated "
            "as exact pairs. They remain outside this checked-in-safe screen "
            "until source-complete paired content is available under a separately "
            "authorized review."
        ),
        "non_claims": list(NON_CLAIMS),
    }
    return blind_payload, sealed_payload


def render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def validate_checked_in_screen(*, repo_root: Path | str) -> list[str]:
    """Return deterministic mismatch messages for the two generated artifacts."""

    root = Path(repo_root).resolve()
    blind, sealed = build_product_delta_paired_screen(repo_root=root)
    expected = {
        DEFAULT_BLIND_PACKETS_RELPATH: render_json(blind),
        DEFAULT_SEALED_MANIFEST_RELPATH: render_json(sealed),
    }
    errors: list[str] = []
    for relpath, rendered in expected.items():
        path = _resolve_repo_path(root, relpath)
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing generated artifact:{relpath}")
            continue
        if actual != rendered:
            errors.append(f"generated artifact drift:{relpath}")
    return errors


def write_checked_in_screen(*, repo_root: Path | str) -> None:
    """Write the deterministic artifacts after explicit operator invocation."""

    root = Path(repo_root).resolve()
    blind, sealed = build_product_delta_paired_screen(repo_root=root)
    for relpath, payload in (
        (DEFAULT_BLIND_PACKETS_RELPATH, blind),
        (DEFAULT_SEALED_MANIFEST_RELPATH, sealed),
    ):
        path = _resolve_repo_path(root, relpath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_json(payload), encoding="utf-8")


def _build_pair(
    *, root: Path, spec: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    source, source_ref = _load_source(
        root=root,
        mode=_required_text(spec, "source_mode"),
        relpath=_required_text(spec, "source_path"),
    )
    baseline, added_context, answer_refs = _load_answers(root=root, spec=spec)
    case_id = _required_text(spec, "case_id")
    source_content_sha256 = _sha256_json_value(source)
    blind_seed = _blind_seed(
        case_id=case_id,
        source_content_sha256=source_content_sha256,
    )
    blind_arms, arm_map = _blind_arms(
        baseline=baseline,
        added_context=added_context,
        blind_seed=blind_seed,
    )
    evidence_class = _required_text(spec, "evidence_class")
    source_limit = (
        "The complete checked-in conversation is supplied."
        if evidence_class == "complete_exact_pair"
        else (
            "Only checked-in source excerpts are supplied. Treat missing context "
            "as a hard limit and do not infer full-conversation adequacy."
        )
    )
    blind_case: dict[str, Any] = {
        "case_id": case_id,
        "evidence_class": evidence_class,
        "source": {
            "coverage": (
                "complete_checked_in_conversation"
                if evidence_class == "complete_exact_pair"
                else "partial_checked_in_source_excerpts"
            ),
            "content_sha256": source_content_sha256,
            "content": source,
            "known_limit": source_limit,
        },
        "arms": blind_arms,
        "review_warning": (
            "Arm labels are deterministic and freshly randomized. They do not "
            "identify provenance. Compare atomic reasoning moves, not fluency or length."
        ),
    }
    blind_case["packet_sha256"] = _sha256_json_value(blind_case)
    sealed_case = {
        "case_id": case_id,
        "evidence_class": evidence_class,
        "blind_seed_sha256": blind_seed,
        "source_ref": source_ref,
        "answer_refs": answer_refs,
        "arm_map": arm_map,
        "historical_refs": [
            _file_ref(root, str(path))
            for path in _string_list(spec.get("historical_refs"))
            if _resolve_repo_path(root, str(path)).exists()
        ],
        "historical_ref_policy": (
            "These references may contain prior provisional judgments. They are "
            "not an answer key and must remain hidden until fresh reviews are frozen."
        ),
    }
    return blind_case, sealed_case


def _build_null_pair(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    retailer_spec = PAIR_SPECS[0]
    source, source_ref = _load_source(
        root=root,
        mode=_required_text(retailer_spec, "source_mode"),
        relpath=_required_text(retailer_spec, "source_path"),
    )
    baseline, _, answer_refs = _load_answers(root=root, spec=retailer_spec)
    source_content_sha256 = _sha256_json_value(source)
    blind_seed = _blind_seed(
        case_id=NULL_CASE_ID,
        source_content_sha256=source_content_sha256,
    )
    content = _answer_content(baseline)
    blind_case: dict[str, Any] = {
        "case_id": NULL_CASE_ID,
        "evidence_class": "exact_duplicate_null",
        "source": {
            "coverage": "complete_checked_in_conversation",
            "content_sha256": source_content_sha256,
            "content": source,
            "known_limit": "The complete checked-in conversation is supplied.",
        },
        "arms": {
            "A": content,
            "B": json.loads(json.dumps(content, ensure_ascii=False)),
        },
        "review_warning": (
            "Arm labels are deterministic and freshly randomized. They do not "
            "identify provenance. Exact equivalence is an allowed finding."
        ),
    }
    blind_case["packet_sha256"] = _sha256_json_value(blind_case)
    sealed_case = {
        "case_id": NULL_CASE_ID,
        "evidence_class": "exact_duplicate_null",
        "blind_seed_sha256": blind_seed,
        "source_ref": source_ref,
        "answer_refs": [answer_refs[0]],
        "arm_map": {
            "A": {
                "origin": "same_baseline_answer",
                "content_sha256": _sha256_json_value(baseline),
            },
            "B": {
                "origin": "same_baseline_answer",
                "content_sha256": _sha256_json_value(baseline),
            },
        },
        "historical_refs": [],
        "historical_ref_policy": "No semantic answer key exists for the duplicate null.",
    }
    return blind_case, sealed_case


def _build_qualification_cases(
    *, root: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    trap_set, trap_ref = _read_json_ref(root, TRAP_SET_RELPATH)
    traps = trap_set.get("traps")
    if not isinstance(traps, list):
        raise ProductDeltaPairedScreenInputError("trap set is missing traps array")
    qualification_cases: list[dict[str, Any]] = []
    for item in traps:
        if not isinstance(item, Mapping):
            raise ProductDeltaPairedScreenInputError("trap record is not an object")
        qualification_cases.append(
            {
                "case_id": _required_text(item, "trap_id"),
                "case_shape": _required_text(item, "case_shape"),
                "safe_context": item.get("safe_context"),
                "available_review_roles": _string_list(
                    item.get("specialist_roles_targeted")
                ),
                "instruction": (
                    "State what can and cannot be concluded from this safe context. "
                    "Do not invent missing evidence or treat artifact health, length, "
                    "polish, caution, or reviewer agreement as decision value."
                ),
            }
        )
    return qualification_cases, trap_ref


def _build_standdown_case(
    *, root: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    source, source_ref = _read_text_ref(root, STANDDOWN_SOURCE_RELPATH)
    result, result_ref = _read_json_ref(root, STANDDOWN_RESULT_RELPATH)
    observation = {
        "candidate_count": result.get("candidate_count"),
        "unresolved_mechanism_ids": result.get("unresolved_mechanism_ids"),
        "graph_calls": result.get("graph_calls"),
        "graph_traversal_required": result.get("graph_traversal_required"),
        "semantic_prefilter_performed": result.get("semantic_prefilter_performed"),
        "standdown_reason": (
            result.get("standdown", {}).get("reason")
            if isinstance(result.get("standdown"), Mapping)
            else None
        ),
    }
    blind_case: dict[str, Any] = {
        "case_id": STANDDOWN_CASE_ID,
        "evidence_class": "complete_conversation_deterministic_standdown",
        "source": {
            "coverage": "complete_checked_in_conversation",
            "content_sha256": _sha256_text(source),
            "content": source,
        },
        "mechanical_observation": observation,
        "review_question": (
            "Does the supplied evidence support preserving the existing reasoning "
            "without adding a public revision? Record support, ambiguity, and any "
            "risk of forcing unnecessary additional analysis."
        ),
    }
    blind_case["packet_sha256"] = _sha256_json_value(blind_case)
    sealed_case = {
        "case_id": STANDDOWN_CASE_ID,
        "source_ref": source_ref,
        "result_ref": result_ref,
        "historical_ref_policy": (
            "The deterministic zero-candidate result establishes what machinery "
            "did, not that the conversation was semantically perfect."
        ),
    }
    return blind_case, sealed_case


def _build_exclusions(
    *, root: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seed_cases, seed_ref = _read_json_ref(root, SEED_CASES_RELPATH)
    cases = seed_cases.get("cases")
    if not isinstance(cases, list):
        raise ProductDeltaPairedScreenInputError("seed case list is missing cases")
    exclusions: list[dict[str, Any]] = []
    for item in cases:
        if not isinstance(item, Mapping):
            continue
        exclusions.append(
            {
                "case_id": _required_text(item, "case_id"),
                "archive_relpath": _required_text(item, "archive_relpath"),
                "reason": (
                    "checked_in_safe_material_does_not_supply_an_exact_"
                    "source_complete_answer_pair"
                ),
            }
        )
    return exclusions, seed_ref


def _load_source(
    *, root: Path, mode: str, relpath: str
) -> tuple[str | dict[str, Any], dict[str, Any]]:
    if mode == "plain_text":
        return _read_text_ref(root, relpath)
    payload, ref = _read_json_ref(root, relpath)
    if mode == "packet_conversation":
        conversation = payload.get("authoritative_conversation")
        if not isinstance(conversation, str) or not conversation:
            raise ProductDeltaPairedScreenInputError(
                "source packet is missing authoritative conversation"
            )
        return conversation, ref
    if mode == "source_excerpts":
        excerpts = payload.get("source_excerpts")
        if not isinstance(excerpts, list) or not excerpts:
            raise ProductDeltaPairedScreenInputError(
                "source handoff is missing excerpts"
            )
        safe_excerpts: list[dict[str, str]] = []
        for item in excerpts:
            if not isinstance(item, Mapping):
                raise ProductDeltaPairedScreenInputError(
                    "source excerpt is not an object"
                )
            safe_excerpts.append(
                {
                    "excerpt_id": _required_text(item, "excerpt_id"),
                    "text": _required_text(item, "text"),
                }
            )
        return {
            "coverage_notice": (
                "Partial source view only. These excerpts are not the complete "
                "conversation and cannot establish omitted context."
            ),
            "excerpts": safe_excerpts,
        }, ref
    raise ProductDeltaPairedScreenInputError("unsupported source mode")


def _load_answers(
    *, root: Path, spec: Mapping[str, Any]
) -> tuple[Any, Any, list[dict[str, Any]]]:
    if "baseline_path" in spec:
        baseline_payload, baseline_ref = _read_json_ref(
            root, _required_text(spec, "baseline_path")
        )
        added_payload, added_ref = _read_json_ref(
            root, _required_text(spec, "added_context_path")
        )
        baseline = baseline_payload.get("answer_core")
        added_context = added_payload.get("answer_core")
        if not isinstance(baseline, str) or not isinstance(added_context, str):
            raise ProductDeltaPairedScreenInputError(
                "answer-core artifact is missing answer_core"
            )
        return baseline, added_context, [baseline_ref, added_ref]

    result, result_ref = _read_json_ref(
        root, _required_text(spec, "result_path")
    )
    if "arm_key_path" in spec:
        arm_key, arm_key_ref = _read_json_ref(
            root, _required_text(spec, "arm_key_path")
        )
        by_arm_id: dict[str, Any] = {}
        output_by_label: dict[str, Any] = {}
        outputs = result.get("outputs")
        mappings = arm_key.get("mapping")
        if not isinstance(outputs, list) or not isinstance(mappings, list):
            raise ProductDeltaPairedScreenInputError(
                "blind output or arm key has invalid shape"
            )
        for output in outputs:
            if isinstance(output, Mapping) and isinstance(
                output.get("blind_label"), str
            ):
                output_by_label[str(output["blind_label"])] = output.get("response")
        for mapping in mappings:
            if not isinstance(mapping, Mapping):
                continue
            label = mapping.get("blind_label")
            arm_id = mapping.get("arm_id")
            if isinstance(label, str) and isinstance(arm_id, str):
                by_arm_id[arm_id] = output_by_label.get(label)
        baseline_id = _required_text(
            _required_mapping(spec, "baseline_locator"), "arm_id"
        )
        added_id = _required_text(
            _required_mapping(spec, "added_context_locator"), "arm_id"
        )
        baseline = by_arm_id.get(baseline_id)
        added_context = by_arm_id.get(added_id)
        if not isinstance(baseline, Mapping) or not isinstance(
            added_context, Mapping
        ):
            raise ProductDeltaPairedScreenInputError(
                "resolved blind output arm is missing structured response"
            )
        return baseline, added_context, [result_ref, arm_key_ref]

    calls = result.get("calls")
    if not isinstance(calls, list):
        raise ProductDeltaPairedScreenInputError("result is missing calls array")
    by_task: dict[str, Any] = {}
    for call in calls:
        if not isinstance(call, Mapping):
            continue
        task_id = call.get("task_id")
        payload = call.get("candidate_payload")
        if isinstance(task_id, str) and isinstance(payload, Mapping):
            by_task[task_id] = payload.get("reconsidered_answer")
    baseline_task = _required_text(
        _required_mapping(spec, "baseline_locator"), "call_task_id"
    )
    added_task = _required_text(
        _required_mapping(spec, "added_context_locator"), "call_task_id"
    )
    baseline = by_task.get(baseline_task)
    added_context = by_task.get(added_task)
    if not isinstance(baseline, str) or not isinstance(added_context, str):
        raise ProductDeltaPairedScreenInputError(
            "result is missing reconsidered answer"
        )
    return baseline, added_context, [result_ref]


def _blind_arms(
    *, baseline: Any, added_context: Any, blind_seed: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    swap = bytes.fromhex(blind_seed)[0] % 2 == 1
    origins = (
        (
            ("A", "reconsideration_with_added_external_context", added_context),
            ("B", "baseline_without_added_external_context", baseline),
        )
        if swap
        else (
            ("A", "baseline_without_added_external_context", baseline),
            ("B", "reconsideration_with_added_external_context", added_context),
        )
    )
    blind: dict[str, Any] = {}
    sealed: dict[str, Any] = {}
    for label, origin, content in origins:
        blind[label] = _answer_content(content)
        sealed[label] = {
            "origin": origin,
            "content_sha256": _sha256_json_value(content),
        }
    return blind, sealed


def _answer_content(content: Any) -> dict[str, Any]:
    if isinstance(content, str):
        return {"format": "text", "content": content}
    if isinstance(content, Mapping):
        return {
            "format": "structured_response",
            "content": json.loads(json.dumps(content, ensure_ascii=False)),
        }
    raise ProductDeltaPairedScreenInputError("unsupported answer content")


def _blind_seed(*, case_id: str, source_content_sha256: str) -> str:
    return _sha256_text(
        f"{BLINDING_NAMESPACE}|{case_id}|{source_content_sha256}"
    )


def _read_json_ref(
    root: Path, relpath: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        text = path.read_text(encoding="utf-8")
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProductDeltaPairedScreenInputError(
            f"checked-in JSON is invalid:{relpath}"
        ) from exc
    except OSError as exc:
        raise ProductDeltaPairedScreenInputError(
            f"checked-in input could not be read:{relpath}"
        ) from exc
    if not isinstance(payload, dict):
        raise ProductDeltaPairedScreenInputError(
            f"checked-in JSON is not an object:{relpath}"
        )
    return payload, {
        "path": relpath,
        "sha256": _sha256_text(text),
    }


def _read_text_ref(root: Path, relpath: str) -> tuple[str, dict[str, Any]]:
    path = _resolve_repo_path(root, relpath)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProductDeltaPairedScreenInputError(
            f"checked-in input could not be read:{relpath}"
        ) from exc
    return text, {
        "path": relpath,
        "sha256": _sha256_text(text),
    }


def _file_ref(root: Path, relpath: str) -> dict[str, Any]:
    path = _resolve_repo_path(root, relpath)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProductDeltaPairedScreenInputError(
            f"historical reference could not be read:{relpath}"
        ) from exc
    return {"path": relpath, "sha256": _sha256_text(text)}


def _resolve_repo_path(root: Path, relpath: str) -> Path:
    path = (root / relpath).resolve()
    if path != root and root not in path.parents:
        raise ProductDeltaPairedScreenInputError("path escapes repository root")
    return path


def _required_mapping(
    payload: Mapping[str, Any], key: str
) -> Mapping[str, Any]:
    value = payload.get(key)
    if not isinstance(value, Mapping):
        raise ProductDeltaPairedScreenInputError(f"missing object:{key}")
    return value


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ProductDeltaPairedScreenInputError(f"missing text:{key}")
    return value


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str) and item]


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_json_value(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return _sha256_text(encoded)
