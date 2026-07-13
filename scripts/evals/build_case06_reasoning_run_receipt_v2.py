#!/usr/bin/env python3
"""Build the closed Case 06 Reasoning Run Receipt v2 provider-free."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]

from scripts.evals.validate_reasoning_run_receipt_v2 import (  # noqa: E402
    validate_reasoning_run_receipt,
)


class Case06ReceiptError(RuntimeError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Case06ReceiptError(f"expected JSON object: {path}")
    return value


def _hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _repo_path(raw: object) -> Path:
    path = Path(str(raw))
    if path.is_absolute():
        raise Case06ReceiptError("contract paths must be repository-relative")
    resolved = (REPO_ROOT / path).resolve()
    if REPO_ROOT.resolve() not in resolved.parents and resolved != REPO_ROOT.resolve():
        raise Case06ReceiptError("contract path escaped repository")
    return resolved


def _validate_hash(path: Path, expected: object, *, role: str) -> None:
    if not path.is_file() or _hash(path) != str(expected):
        raise Case06ReceiptError(f"hash mismatch: {role}")


def _validate_contracts(
    repaired_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    repaired = _load(repaired_path)
    if repaired.get("status") != "frozen_after_v2_application_repair_before_receipt_assembly":
        raise Case06ReceiptError("repaired contract is not frozen")
    if repaired.get("provider_call_budget") != 0:
        raise Case06ReceiptError("provider_call_budget must be zero")
    base_ref = repaired["base_input_contract"]
    base_path = _repo_path(base_ref["path"])
    _validate_hash(base_path, base_ref["sha256"], role="base_input_contract")
    base = _load(base_path)
    superseded = set(base_ref["superseded_input_roles"])
    paths: dict[str, Path] = {}
    for item in base["inputs"]:
        role = str(item["role"])
        path = _repo_path(item["path"])
        if role not in superseded:
            _validate_hash(path, item["sha256"], role=role)
        paths[role] = path
    audit_ref = repaired["application_audit"]
    audit_path = _repo_path(audit_ref["path"])
    _validate_hash(audit_path, audit_ref["sha256"], role="v2_application_audit")
    paths["v2_application_audit"] = audit_path
    for item in repaired["repaired_contract_artifacts"]:
        role = str(item["role"])
        path = _repo_path(item["path"])
        _validate_hash(path, item["sha256"], role=role)
        paths[role] = path
    paths["receipt_contract_initial"] = base_path
    paths["receipt_contract_repaired"] = repaired_path
    return repaired, base, paths


def _source_index(conversation: str) -> list[dict[str, Any]]:
    pattern = re.compile(r"^\[Turn (\d+)\] (USER|ASSISTANT):$")
    rows = []
    message_index = 0
    for line in conversation.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        message_index += 1
        turn = int(match.group(1))
        speaker = match.group(2).lower()
        rows.append(
            {
                "source_ref": f"turn-{turn:02d}-{speaker}",
                "turn_index": message_index,
                "speaker": speaker,
                "source_kind": "conversation_message",
            }
        )
    if len(rows) != 20:
        raise Case06ReceiptError("expected exact 20-message Case 06 conversation")
    return rows


def _artifact_manifest(
    *,
    repaired: Mapping[str, Any],
    base: Mapping[str, Any],
    paths: Mapping[str, Path],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    superseded = set(repaired["base_input_contract"]["superseded_input_roles"])
    for item in base["inputs"]:
        role = str(item["role"])
        if role in superseded:
            continue
        rows.append(
            {
                "role": role,
                "path": str(item["path"]),
                "sha256": f"sha256:{item['sha256']}",
            }
        )
    for item in repaired["repaired_contract_artifacts"]:
        rows.append(
            {
                "role": str(item["role"]),
                "path": str(item["path"]),
                "sha256": f"sha256:{item['sha256']}",
            }
        )
    for role, path in (
        ("receipt_contract_initial", paths["receipt_contract_initial"]),
        ("v2_application_audit", paths["v2_application_audit"]),
        ("receipt_contract_repaired", paths["receipt_contract_repaired"]),
    ):
        rows.append(
            {
                "role": role,
                "path": str(path.relative_to(REPO_ROOT)),
                "sha256": f"sha256:{_hash(path)}",
            }
        )
    if len({row["role"] for row in rows}) != len(rows):
        raise Case06ReceiptError("artifact manifest roles are not unique")
    return rows


def _anonymous_outputs(blind: Mapping[str, Any]) -> list[dict[str, Any]]:
    result = []
    for row in blind["outputs"]:
        metadata = row["metadata"]
        result.append(
            {
                "blind_label": row["blind_label"],
                "status": row["status"],
                "response": row["response"],
                "response_sha256": f"sha256:{metadata['response_sha256']}",
                "prompt_tokens": metadata["prompt_tokens"],
                "completion_tokens": metadata["completion_tokens"],
                "total_tokens": metadata["total_tokens"],
            }
        )
    return result


def build_receipt(
    *, repaired: Mapping[str, Any], base: Mapping[str, Any], paths: Mapping[str, Path]
) -> dict[str, Any]:
    conversation = paths["source_conversation"].read_text(encoding="utf-8")
    stage_a = _load(paths["stage_a_gate"])
    edge_packet = _load(paths["protected_edge_packet"])
    edge_review = _load(paths["protected_edge_admission_review"])
    stage_b_summary = _load(paths["stage_b_run_summary"])
    blind = _load(paths["stage_b_blind_outputs"])
    arm_key = _load(paths["stage_b_arm_key"])
    review = _load(paths["stage_b_review"])
    graph_inventory = _load(paths["graph_candidate_inventory"])
    frozen_pressure = edge_packet["items"][0]
    edge_result = review["edge_disposition"]
    returned_treatment = next(
        row for row in blind["outputs"] if row["blind_label"] == "B"
    )["response"]
    returned_disposition = returned_treatment["edge_dispositions"][0]
    estimated_cost = round(
        float(stage_a["observed"]["estimated_total_cost_usd"])
        + float(stage_b_summary["estimated_cost_usd"]),
        8,
    )
    provider_calls = (
        int(stage_a["observed"]["openrouter_calls"])
        + int(stage_a["observed"]["openai_embedding_and_expansion_calls"])
        + int(stage_b_summary["call_count"])
    )
    manifest = _artifact_manifest(repaired=repaired, base=base, paths=paths)
    freeze_time = str(repaired["frozen_at_utc"])

    return {
        "schema_version": "lolla.reasoning_run_receipt.v2",
        "status": "frozen_for_reader",
        "receipt_metadata": {
            "receipt_id": "receipt::case-06-friendship-money::v2",
            "case_id": "case-06-friendship-money",
            "run_id": "case06-closed-batch2-receipt-v2",
            "frozen_at_utc": freeze_time,
            "as_of_event_id": "case06_receipt_frozen",
            "as_of_event_sequence": 1,
            "artifact_state": "frozen_immutable_snapshot",
        },
        "complete_conversation": conversation,
        "source_index": _source_index(conversation),
        "source_end_state": {
            "as_of_source_ref": "turn-10-assistant",
            "decision_status": "stated_plan_pending_execution",
            "stated_next_action": {
                "status": "present",
                "summary": "The user says they will decline the 10000-dollar request, offer 2000 dollars, and help with legal-aid and city-resource exploration.",
                "source_refs": ["turn-10-user"],
            },
            "deadline_or_time_constraint": {
                "status": "not_stated",
                "summary": "",
                "source_refs": [],
            },
            "unresolved_items": [
                "Whether the user can sustainably afford the 2000-dollar offer",
                "Whether legal-aid or city resources are actually available",
                "How the friend will respond",
                "Whether the friendship changes after the conversation",
            ],
        },
        "reasoning_process": {
            "interpretations": [
                {
                    "interpretation_id": "boundary-and-friendship-both-matter",
                    "summary": "The user wants to refuse 10000 dollars without abandoning a fifteen-year friendship.",
                    "epistemic_status": "source_supported",
                    "source_refs": ["turn-01-user", "turn-07-user"],
                    "artifact_refs": ["source_conversation"],
                },
                {
                    "interpretation_id": "intent-diagnosis-rejected-by-user",
                    "summary": "The user explicitly rejects the assistant's characterization of the friend as using or manipulating them.",
                    "epistemic_status": "source_supported",
                    "source_refs": ["turn-09-user", "turn-09-assistant"],
                    "artifact_refs": ["source_conversation"],
                },
                {
                    "interpretation_id": "resource-and-outcome-claims-unresolved",
                    "summary": "Resource availability, legal processes, housing outcomes, and friendship outcomes are not established by the conversation.",
                    "epistemic_status": "unresolved",
                    "source_refs": ["turn-05-assistant", "turn-10-user"],
                    "artifact_refs": ["source_conversation", "stage_b_review"],
                },
            ],
            "stage_a": {
                "status": stage_a["status"],
                "summary": "The closed Stage A run passed its mechanical gates and admitted one protected confirmable-empathy edge for mandatory downstream disposition.",
                "transformations": [
                    {
                        "transformation_id": "complete-capture-and-quote-custody",
                        "kind": "capture",
                        "summary": "Fresh extraction preserved the full 10-turn-pair conversation with no surviving quote fabrication.",
                        "source_refs": ["turn-01-user", "turn-10-assistant"],
                        "artifact_refs": ["stage_a_gate"],
                    },
                    {
                        "transformation_id": "protected-empathy-edge-admission",
                        "kind": "selection",
                        "summary": "Source-first review admitted a confirmable-empathy edge while naming risks of both forcing and ignoring it.",
                        "source_refs": [
                            "turn-04-user",
                            "turn-07-user",
                            "turn-08-user",
                            "turn-09-user",
                            "turn-10-user",
                        ],
                        "artifact_refs": [
                            "protected_edge_packet",
                            "protected_edge_admission_review",
                        ],
                    },
                ],
                "artifact_refs": ["stage_a_contract", "stage_a_gate"],
            },
            "attribution_repairs": [
                {
                    "repair_id": "exact-pressure-identity-failure-preserved",
                    "failure": "The treatment was required to return batch2-edge-empathy-confirm-before-diagnosis but returned confirmable-empathy-lens.",
                    "repair": "The receipt stores the expected and observed IDs separately and labels the identity mismatch while preserving the substantive semantic hearing.",
                    "residual_limit": "The completed treatment is not repaired or regraded as exact custody success.",
                    "artifact_refs": ["stage_b_contract", "stage_b_blind_outputs", "stage_b_review"],
                },
                {
                    "repair_id": "private-visible-effect-inconsistency-preserved",
                    "failure": "The treatment labeled the edge private_guardrail and left visible_effect empty while its material shifts and next actions visibly emphasized confirmable empathy.",
                    "repair": "The receipt records the returned disposition and the separate inconsistent effect-consistency review.",
                    "residual_limit": "The receipt does not infer how much of the visible empathy came uniquely from treatment because the control also recovered it.",
                    "artifact_refs": ["stage_b_blind_outputs", "stage_b_review"],
                },
                {
                    "repair_id": "graph-attribution-limit-preserved",
                    "failure": "The complete companion graph surface was not preserved for Case 06.",
                    "repair": "The receipt identifies the protected edge as V60-affordance pressure and marks graph exposure unknown rather than absent.",
                    "residual_limit": "Case 06 cannot identify graph contribution or non-contribution.",
                    "artifact_refs": ["graph_candidate_inventory", "v60_snapshot"],
                },
                {
                    "repair_id": "receipt-v2-first-application-repair",
                    "failure": "The first synthetic v2 contract could not carry exact anonymous outputs, identity mismatch, effect consistency, or partial token scope.",
                    "repair": "The contract was repaired before this receipt was assembled and before any reader call.",
                    "residual_limit": "This remains the first real receipt using the repaired fields and still requires a cold-reader test.",
                    "artifact_refs": ["v2_application_audit", "receipt_contract_repaired"],
                },
            ],
        },
        "pressure_accountability": [
            {
                "pressure_id": frozen_pressure["pressure_id"],
                "observed_consumer_pressure_id": edge_result[
                    "returned_pressure_id"
                ],
                "identity_status": "mismatch",
                "semantic_hearing_status": "substantive",
                "effect_consistency_status": "inconsistent",
                "origin": "v60_affordance",
                "admission_status": "admitted",
                "consumer_disposition": returned_disposition["disposition"],
                "challenge": frozen_pressure["challenge"],
                "strongest_plausible_application": returned_disposition[
                    "strongest_plausible_application"
                ],
                "why": "The consumer heard a semantic analogue and chose a private guardrail, but renamed the exact frozen pressure and described effects inconsistently.",
                "source_refs": [
                    "turn-04-user",
                    "turn-07-user",
                    "turn-08-user",
                    "turn-09-user",
                    "turn-10-user",
                ],
                "lineage_ids": frozen_pressure["trace_ids"],
                "graph_pressure_ids": [],
                "visible_effect": returned_disposition["visible_effect"],
                "private_guardrail": returned_disposition["private_guardrail"],
                "risk_if_forced": returned_disposition["risk_if_forced"],
                "risk_if_ignored": returned_disposition["risk_if_ignored"],
            }
        ],
        "comparison_evidence": {
            "status": "complete",
            "blind_review_before_key": True,
            "control_summary": "The control independently removed intent and outcome claims, preserved the no-10000 boundary and friendship value, and proposed a clear caring refusal.",
            "treatment_summary": "The treatment reached the same public action, returned a renamed empathy pressure as a private guardrail, and visibly emphasized the same empathy mechanism.",
            "observed_difference": "No material unique public treatment delta was observed; correct public stand-down coexists with exact identity and effect-accounting failures.",
            "limits": "The review was blind-first development-agent review but lacks the separate pre-key sealed hash used in Case 10; it is provisional and not human ground truth.",
            "anonymous_outputs": _anonymous_outputs(blind),
            "reveal_mapping": arm_key["mapping"],
            "blind_review_summary": "Before using the key, the reviewer found both arms source-faithful, no material unique treatment delta, correct public stand-down, and no public bloat. After reveal, treatment was B; exact pressure identity and effect consistency failed.",
            "artifact_refs": [
                "stage_b_contract",
                "stage_b_run_summary",
                "stage_b_blind_outputs",
                "stage_b_arm_key",
                "stage_b_review",
            ],
        },
        "graph_attribution": {
            "exposure_status": "unknown",
            "exposed_graph_pressure_ids": [],
            "exact_lineage_status": "none",
            "exact_lineage_pressure_ids": [],
            "individual_disposition_status": "none",
            "individually_dispositioned_graph_pressure_ids": [],
            "causal_contribution_status": "not_tested",
            "statement_scope": "exposure_only",
            "summary": "The protected empathy edge is traced to V60 candidate and affordance material, not an exact relationship-graph pressure. The complete companion graph surface was not preserved, so indirect graph exposure remains unknown.",
            "limits": [
                "No exact graph pressure appears in the frozen treatment packet",
                "Missing complete graph-surface custody prevents an absence claim",
                "No graph-disabled or shuffled-edge arm was run",
            ],
        },
        "custody_boundary": {
            "claim_level": "recorded_artifact_integrity_only",
            "summary": "The listed hashes, exact payloads, IDs, and reviews support the recorded closed-case artifact relationships represented here.",
            "artifacts_support": [
                "The complete source conversation used by the closed case",
                "The exact expected and returned pressure identities",
                "The exact anonymous paired response objects and reveal mapping",
                "The recorded call, cost, and partial token scope",
                "The provisional source and accountability review findings",
            ],
            "artifacts_do_not_establish": [
                "Answer correctness or decision improvement",
                "Human validation",
                "Independent verification of real-world execution or outcomes",
                "Graph contribution or absence",
                "A clean accountability process win",
            ],
            "external_execution_independently_verified": False,
            "reasoning_quality_inferred": False,
        },
        "claim_boundary": {
            "supported": [
                {
                    "claim_id": "stage-a-mechanical-pass",
                    "text": "The closed Case 06 Stage A run passed its frozen mechanical gate.",
                    "basis_artifact_refs": ["stage_a_gate"],
                },
                {
                    "claim_id": "correct-public-standdown",
                    "text": "Both downstream arms preserved the boundary and produced no material unique public treatment delta in provisional review.",
                    "basis_artifact_refs": ["stage_b_blind_outputs", "stage_b_review"],
                },
                {
                    "claim_id": "exact-pressure-identity-failed",
                    "text": "The treatment returned a different pressure ID from the frozen expected ID.",
                    "basis_artifact_refs": ["stage_b_contract", "stage_b_blind_outputs", "stage_b_review"],
                },
                {
                    "claim_id": "effect-consistency-failed",
                    "text": "The private-guardrail label was inconsistent with visible empathy emphasis recorded in the treatment output.",
                    "basis_artifact_refs": ["stage_b_blind_outputs", "stage_b_review"],
                },
            ],
            "unsupported_or_forbidden": [
                {
                    "claim_id": "unique-answer-improvement-unproven",
                    "text": "The Lolla treatment improved the public answer beyond the strong control.",
                },
                {
                    "claim_id": "clean-accountability-unproven",
                    "text": "Case 06 demonstrated a clean accountable-consideration process.",
                },
                {
                    "claim_id": "graph-absence-unproven",
                    "text": "The graph had no influence on Case 06.",
                },
                {
                    "claim_id": "human-usefulness-unproven",
                    "text": "This receipt is useful to a human reviewer.",
                },
            ],
        },
        "operability": {
            "provider_calls": provider_calls,
            "evaluator_calls": 0,
            "automatic_retries": 0,
            "total_tokens": int(stage_b_summary["total_tokens"]),
            "token_evidence_state": "partial",
            "token_scope": "Stage B control-and-treatment pair only; Stage A preserves calls and cost but no whole-run token aggregate in its gate result",
            "estimated_cost_usd": estimated_cost,
            "cost_evidence_state": "complete",
            "wall_time_seconds": None,
            "notes": [
                "Stage A recorded 29 OpenRouter calls and 7 direct OpenAI embedding or expansion calls",
                "Stage B recorded 2 OpenRouter calls and 6587 total tokens",
                "Whole-run wall time was not preserved in the selected gate artifacts",
                "No experiment retry or evaluator model call was used",
            ],
        },
        "authorization_snapshot": {
            "scope_label": "receipt_freeze_snapshot_not_current_state",
            "as_of_event_id": "case06_receipt_frozen",
            "as_of_utc": freeze_time,
            "as_of_event_sequence": 1,
            "authorizations": {
                "receipt_assembly": True,
                "reader_contract_construction": False,
                "reader_call": False,
                "pipeline_rerun": False,
                "graph_promotion": False,
                "runtime_integration": False,
            },
            "future_events_not_covered": ["reader_call", "human_review"],
            "post_reader_status_artifact_required": True,
        },
        "questions": {
            "case_domain_unknowns": [
                "Can the user sustainably afford the smaller offer?",
                "Which legal-aid or city resources are actually available?",
                "How will the friend respond to the boundary?",
                "How will the friendship evolve after the conversation?",
            ],
            "reader_reconstruction_checks": [
                "Can the reader preserve the final 2000-dollar-plus-help plan without calling it financially validated?",
                "Can the reader explain why correct public stand-down is not a clean accountability win?",
                "Can the reader distinguish semantic hearing from exact pressure identity custody?",
                "Can the reader identify the private-versus-visible effect inconsistency?",
                "Can the reader explain why graph exposure is unknown rather than absent?",
                "Can the reader preserve the partial token scope?",
            ],
            "human_product_review_questions": [
                "Does this receipt make the useful stand-down and the hidden accountability failures equally easy to understand?"
            ],
        },
        "artifact_manifest": manifest,
        "non_claims": [
            {
                "non_claim_id": "not_human_validation",
                "text": "This receipt is not human validation.",
            },
            {
                "non_claim_id": "not_answer_quality_proof",
                "text": "This receipt is not proof of answer quality or decision improvement.",
            },
            {
                "non_claim_id": "not_graph_value_proof",
                "text": "This receipt does not establish graph value, absence, or necessity.",
            },
            {
                "non_claim_id": "not_runtime_authority",
                "text": "This receipt does not authorize runtime integration or graph promotion.",
            },
            {
                "non_claim_id": "not_autonomous_action_authority",
                "text": "This receipt does not authorize financial, legal, housing, relationship, or autonomous action.",
            },
        ],
    }


def _json_block(value: object) -> str:
    return "```json\n" + json.dumps(value, indent=2, ensure_ascii=False) + "\n```"


def render_markdown(receipt: Mapping[str, Any]) -> str:
    lines = [
        "# Case 06 Reasoning Run Receipt v2",
        "",
        "Status: **frozen for one prospective cold-reader contract; not human validated**  ",
        "Date: 2026-07-10",
        "",
        "## How to read this",
        "",
        "- The complete conversation below is authoritative for what the user and assistant said.",
        "- Interpretations remain reviewable summaries, not source facts.",
        "- Correct public stand-down and failed private accountability are both preserved.",
        "- Recorded custody is not answer quality, human validation, or external verification.",
        "",
        "## Complete conversation — authoritative source",
        "",
        str(receipt["complete_conversation"]).rstrip(),
        "",
        "## Source-end decision state",
        "",
        _json_block(receipt["source_end_state"]),
        "",
        "## Interpretation and Stage A",
        "",
        _json_block(receipt["reasoning_process"]),
        "",
        "## Pressure accountability",
        "",
        _json_block(receipt["pressure_accountability"]),
        "",
        "## Exact anonymous pair, reveal, and comparison",
        "",
        _json_block(receipt["comparison_evidence"]),
        "",
        "## Graph attribution boundary",
        "",
        _json_block(receipt["graph_attribution"]),
        "",
        "## Custody and claim boundary",
        "",
        _json_block(receipt["custody_boundary"]),
        "",
        _json_block(receipt["claim_boundary"]),
        "",
        "## Operability and authorization snapshot",
        "",
        _json_block(receipt["operability"]),
        "",
        _json_block(receipt["authorization_snapshot"]),
        "",
        "## Questions by audience",
        "",
        _json_block(receipt["questions"]),
        "",
        "## Artifact manifest",
        "",
        _json_block(receipt["artifact_manifest"]),
        "",
        "## Non-claims",
        "",
    ]
    lines.extend(f"- {row['text']}" for row in receipt["non_claims"])
    return "\n".join(lines).rstrip() + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    contract_path = args.contract
    if not contract_path.is_absolute():
        contract_path = REPO_ROOT / contract_path
    repaired, base, paths = _validate_contracts(contract_path.resolve())
    receipt = build_receipt(repaired=repaired, base=base, paths=paths)
    validation = validate_reasoning_run_receipt(receipt)
    if args.dry_run:
        print(json.dumps({**validation, "outputs_written": False}, indent=2))
        return 0
    outputs = repaired["outputs"]
    json_path = _repo_path(outputs["json"])
    markdown_path = _repo_path(outputs["markdown"])
    if json_path.exists() or markdown_path.exists():
        raise Case06ReceiptError("refusing to overwrite existing receipt output")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    markdown_path.write_text(render_markdown(receipt), encoding="utf-8")
    print(
        json.dumps(
            {
                **validation,
                "receipt_json_sha256": _hash(json_path),
                "receipt_markdown_sha256": _hash(markdown_path),
                "outputs_written": True,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
