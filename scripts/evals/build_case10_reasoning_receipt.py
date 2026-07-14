#!/usr/bin/env python3
"""Build the self-contained Case 10 Gate 7 reasoning receipt provider-free."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_SCHEMA = "lolla.case10_reasoning_receipt_contract.v1"
RECEIPT_SCHEMA = "lolla.case10_reasoning_receipt.v1"
REQUIRED_ROLES = frozenset(
    {
        "source_conversation",
        "stage_a_decision",
        "stage_a_preliminary_review",
        "stage_a_pressure_packet",
        "stage_b_contract",
        "stage_b_run_summary",
        "stage_b_blind_outputs",
        "stage_b_blind_review",
        "stage_b_arm_key",
        "stage_b_revealed_comparison",
        "stage_b_decision",
        "gate6_v1_completion_audit",
        "gate6_v2_result",
        "gate6_graph_source_review",
        "gate6_case10_decision",
        "gate6_inventory_decision",
        "gate6_shadow_custody",
        "product_constitution",
        "public_private_eval_boundary",
    }
)


class ContractError(ValueError):
    pass


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ContractError(f"expected JSON object: {path}")
    return payload


def _resolve(root: Path, raw: str) -> Path:
    path = Path(raw)
    return path if path.is_absolute() else root / path


def validate_contract(contract: Mapping[str, Any], *, root: Path) -> dict[str, Path]:
    if _text(contract.get("schema_version")) != CONTRACT_SCHEMA:
        raise ContractError(f"schema_version must be {CONTRACT_SCHEMA}")
    if _text(contract.get("status")) != "frozen_before_build":
        raise ContractError("status must be frozen_before_build")
    if int(contract.get("provider_call_budget", -1)) != 0:
        raise ContractError("provider_call_budget must be zero")
    if bool(contract.get("runtime_change_authorized")):
        raise ContractError("runtime_change_authorized must be false")

    rows = [_mapping(row) for row in _list(contract.get("inputs"))]
    roles = [_text(row.get("role")) for row in rows]
    if len(roles) != len(set(roles)):
        raise ContractError("input roles must be unique")
    missing = sorted(REQUIRED_ROLES - set(roles))
    if missing:
        raise ContractError(f"missing required input roles: {missing}")
    resolved = {}
    for row in rows:
        role = _text(row.get("role"))
        path = _resolve(root, _text(row.get("path")))
        expected = _text(row.get("sha256"))
        if not path.is_file():
            raise ContractError(f"missing {role}: {path}")
        actual = _sha256(path)
        if actual != expected:
            raise ContractError(
                f"hash drift for {role}: expected {expected}, observed {actual}"
            )
        resolved[role] = path

    outputs = _mapping(contract.get("outputs"))
    for role in ("json", "markdown"):
        raw = _text(outputs.get(role))
        if not raw:
            raise ContractError(f"outputs.{role} is required")
        resolved[f"output_{role}"] = _resolve(root, raw)
    return resolved


def _arm_mapping(arm_key: Mapping[str, Any]) -> dict[str, str]:
    return {
        _text(row.get("blind_label")): _text(row.get("arm_id"))
        for row in (_mapping(value) for value in _list(arm_key.get("mapping")))
    }


def _blind_outputs(blind: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for value in _list(blind.get("outputs")):
        row = _mapping(value)
        rows.append(
            {
                "blind_label": _text(row.get("blind_label")),
                "status": _text(row.get("status")),
                "response": row.get("response"),
                "served_model": _text(row.get("served_model")),
                "prompt_tokens": row.get("prompt_tokens"),
                "completion_tokens": row.get("completion_tokens"),
                "total_tokens": row.get("total_tokens"),
                "response_sha256": _text(row.get("response_sha256")),
            }
        )
    return rows


def build_receipt(
    contract: Mapping[str, Any], *, paths: Mapping[str, Path]
) -> dict[str, Any]:
    source = paths["source_conversation"].read_text(encoding="utf-8")
    stage_a_decision = _load_json(paths["stage_a_decision"])
    stage_a_review = _load_json(paths["stage_a_preliminary_review"])
    pressure_packet = _load_json(paths["stage_a_pressure_packet"])
    stage_b_contract = _load_json(paths["stage_b_contract"])
    run_summary = _load_json(paths["stage_b_run_summary"])
    blind_outputs = _load_json(paths["stage_b_blind_outputs"])
    blind_review = _load_json(paths["stage_b_blind_review"])
    arm_key = _load_json(paths["stage_b_arm_key"])
    revealed = _load_json(paths["stage_b_revealed_comparison"])
    stage_b_decision = _load_json(paths["stage_b_decision"])
    v1_audit = _load_json(paths["gate6_v1_completion_audit"])
    v2_result = _load_json(paths["gate6_v2_result"])
    graph_review = _load_json(paths["gate6_graph_source_review"])
    gate6_case10 = _load_json(paths["gate6_case10_decision"])
    inventory = _load_json(paths["gate6_inventory_decision"])
    shadow = _load_json(paths["gate6_shadow_custody"])

    observed_a = _mapping(stage_a_decision.get("observed_operability"))
    stage_b_claims = _mapping(
        _mapping(stage_b_decision.get("gate_5")).get("claim_vector")
    )
    v2_evidence = _mapping(v2_result.get("decision_evidence"))
    graph_review_decision = _mapping(graph_review.get("decision"))
    arm_map = _arm_mapping(arm_key)
    exact_outputs = _blind_outputs(blind_outputs)

    total_estimated_cost = round(
        float(observed_a.get("estimated_total_cost_usd", 0) or 0)
        + float(run_summary.get("estimated_cost_usd", 0) or 0),
        6,
    )
    total_recorded_tokens = int(
        observed_a.get("total_recorded_tokens_across_openrouter_and_openai", 0) or 0
    ) + int(run_summary.get("total_tokens", 0) or 0)

    input_rows = [
        {
            "role": _text(row.get("role")),
            "path": _text(row.get("path")),
            "sha256": _text(row.get("sha256")),
        }
        for row in (_mapping(value) for value in _list(contract.get("inputs")))
    ]
    return {
        "schema_version": RECEIPT_SCHEMA,
        "status": "complete_self_contained_synthetic_case",
        "case_id": "case-10-real-estate-bid",
        "date": "2026-07-10",
        "reader_guide": [
            "The complete conversation is the authority for what the user and assistant said.",
            "Interpretations and pressure questions are reviewable hypotheses, not source facts.",
            "Deterministic hashes, IDs, call counts, and schemas prove custody and execution shape, not reasoning quality.",
            "The blind review is Codex-assisted provisional review, not human validation or ground truth.",
            "A negative or no-op result remains useful evidence when preserved without regrading."
        ],
        "complete_conversation": source,
        "source_fidelity_contract": _mapping(stage_b_contract.get("source_red_lines")),
        "decision_state_at_source_end": {
            "user_position": "The user says 925000 dollars is the ceiling they can honestly accept and plans to discuss it with their husband before raising or walking.",
            "unknowns": [
                "whether the husband agrees",
                "whether 925000 dollars is submitted",
                "whether the offer wins",
                "verified repair costs and insurance requirements",
                "complete household finances and affordability"
            ],
            "not_a_conclusion": "The source does not establish the correct bid or whether the household can afford the home."
        },
        "stage_a": {
            "formal_status": _text(stage_a_decision.get("formal_stage_a_status")),
            "selection_method": "Case 10 was selected by a digest order frozen before source review after the earlier Case 05 formal failure and prospective execution-field repair.",
            "capture": {
                "captured_messages": observed_a.get("captured_messages"),
                "omitted_messages": observed_a.get("omitted_messages"),
                "verified_reasoning_passages": observed_a.get("verified_reasoning_passages"),
                "remaining_quote_failures": observed_a.get("remaining_quote_failures")
            },
            "operations": observed_a,
            "semantic_admission": _mapping(stage_a_decision.get("semantic_admission")),
            "admitted_pressures": _list(stage_a_review.get("admitted_pressures")),
            "rejected_or_already_covered": _list(
                stage_a_review.get("rejected_or_already_covered")
            ),
            "generator_packet": _list(pressure_packet.get("pressure_items")),
            "important_diagnostic": _mapping(stage_a_review.get("diagnostics"))
        },
        "stage_b": {
            "contract_shape": {
                "purpose": _text(stage_b_contract.get("purpose")),
                "call_configuration": _mapping(stage_b_contract.get("call_configuration")),
                "stop_rules": _list(stage_b_contract.get("stop_rules")),
                "non_claims": _list(stage_b_contract.get("non_claims"))
            },
            "mechanical_run": run_summary,
            "anonymous_outputs": exact_outputs,
            "blind_review_before_key": {
                "status": _text(blind_review.get("status")),
                "sealed_at_utc": _text(blind_review.get("sealed_at_utc")),
                "substantive_preference": _text(
                    _mapping(blind_review.get("blind_overall_read")).get(
                        "substantive_preference"
                    )
                ),
                "action_difference": _mapping(
                    blind_review.get("blind_overall_read")
                ).get("action_difference_between_outputs"),
                "accountability_difference": _mapping(
                    blind_review.get("blind_overall_read")
                ).get("accountability_difference_between_outputs"),
                "shared_failures_or_omissions": _list(
                    blind_review.get("shared_failures_or_omissions")
                ),
                "blind_decision": _mapping(blind_review.get("blind_decision")),
                "sha256_before_key_reveal": _text(
                    _mapping(revealed.get("blind_review")).get(
                        "sha256_before_key_reveal"
                    )
                )
            },
            "reveal_mapping": arm_map,
            "comparison_after_reveal_without_regrading": _mapping(
                revealed.get("comparison")
            ),
            "claim_classification": _mapping(revealed.get("claim_classification")),
            "gate_5_claim_vector": stage_b_claims,
            "measurement_correction": _mapping(
                _load_json(paths["gate6_case10_decision"]).get(
                    "gate_5_measurement_correction"
                )
            )
        },
        "graph_attribution": {
            "v1_preserved_failure": {
                "status": _text(v1_audit.get("status")),
                "finding": _text(v1_audit.get("finding")),
                "invalid_or_too_broad": _list(v1_audit.get("invalid_or_too_broad")),
                "prospective_repair": _list(v1_audit.get("prospective_repair"))
            },
            "v2_complete_consumer_result": {
                "decision_evidence": v2_evidence,
                "consumer_surface": _mapping(
                    v2_result.get("complete_step6_consumer_surface")
                ),
                "interpretation_boundary": _mapping(
                    v2_result.get("interpretation_boundary")
                )
            },
            "source_first_chunk_review": {
                "chunks": _list(graph_review.get("chunks")),
                "decision": graph_review_decision
            },
            "case10_gate6_decision": _mapping(gate6_case10.get("gate_6_decision")),
            "six_case_inventory_decision": _mapping(inventory.get("gate_6_decision")),
            "shadow_exact_identities": [
                {
                    "graph_pressure_id": _text(row.get("graph_pressure_id")),
                    "source_anchor_model_id": _text(row.get("source_anchor_model_id")),
                    "relation_type": _text(row.get("relation_type")),
                    "target_model_id": _text(row.get("target_model_id")),
                    "chunk_text_sha256": _text(row.get("chunk_text_sha256")),
                    "source_json_pointer": _text(row.get("source_json_pointer")),
                    "source_review_status": _text(row.get("source_review_status")),
                    "disposition": _text(row.get("disposition"))
                }
                for row in (
                    _mapping(value) for value in _list(shadow.get("graph_pressures"))
                )
            ]
        },
        "current_claims": {
            "supported": [
                "Case 10 Stage A and Stage B executed within their frozen mechanical contracts.",
                "The treatment created provisional accountable-consideration value and correctly deferred one pressure.",
                "The treatment did not demonstrate unique immediate-answer improvement over the strong control.",
                "Graph relationships reached ordinary reconsideration indirectly inside companion anchors.",
                "The completed Stage B pair did not isolate graph contribution.",
                "No eligible graph-specific case exists in the comparable six-case July inventory."
            ],
            "unsupported_or_forbidden": [
                "Lolla improves real-world decisions.",
                "The graph is necessary or useless.",
                "More calls or a longer receipt prove deeper reasoning.",
                "The receipt is human validation, certification, or approval.",
                "Any bid, financial, repair, insurance, legal, or relationship outcome is correct."
            ]
        },
        "whole_run_operability": {
            "stage_a_openrouter_calls": observed_a.get("total_openrouter_calls"),
            "stage_a_direct_openai_calls": observed_a.get(
                "direct_openai_embedding_and_expansion_calls"
            ),
            "stage_b_openrouter_calls": run_summary.get("call_count"),
            "total_recorded_tokens_stage_a_plus_stage_b": total_recorded_tokens,
            "estimated_cost_usd_stage_a_plus_stage_b": total_estimated_cost,
            "stage_b_wall_time_seconds": run_summary.get("wall_time_seconds"),
            "experiment_retries_stage_a": observed_a.get("experiment_retries"),
            "experiment_retries_stage_b": run_summary.get("experiment_retries"),
            "evaluator_calls_stage_b": run_summary.get("evaluator_calls")
        },
        "current_authorizations": {
            "gate_7_agent_reader_contract_construction": True,
            "gate_7_reader_call": False,
            "human_validation": False,
            "paid_graph_ablation": False,
            "runtime_integration": False,
            "graph_promotion": False
        },
        "open_questions_for_cold_reader": [
            "Can the reader distinguish source facts from assistant claims and later interpretations?",
            "Can the reader reconstruct why the treatment did not earn an answer-improvement claim?",
            "Can the reader explain the narrower accountability value without calling it quality proof?",
            "Can the reader explain the v1 attribution error and v2 repair?",
            "Can the reader state why paid graph testing remains blocked and what would unblock it?",
            "Can the reader identify which conclusions still require human judgment?"
        ],
        "artifact_manifest": input_rows,
        "non_claims": [
            "not human review",
            "not ground truth",
            "not a quality score",
            "not product proof",
            "not proof of reasoning depth",
            "not financial real-estate insurance legal renovation or bidding advice",
            "not graph promotion",
            "not runtime-integration authority",
            "not autonomous-action authority"
        ]
    }


def _json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, indent=2, ensure_ascii=False) + "\n```"


def render_markdown(receipt: Mapping[str, Any]) -> str:
    stage_a = _mapping(receipt.get("stage_a"))
    stage_b = _mapping(receipt.get("stage_b"))
    graph = _mapping(receipt.get("graph_attribution"))
    claims = _mapping(receipt.get("current_claims"))
    operations = _mapping(stage_a.get("operations"))
    mechanical = _mapping(stage_b.get("mechanical_run"))
    lines = [
        "# Case 10 self-contained reasoning receipt",
        "",
        "Status: **agent-reader candidate; not human validated**  ",
        "Date: 2026-07-10",
        "",
        "## How to read this",
        "",
    ]
    lines.extend(f"- {item}" for item in _list(receipt.get("reader_guide")))
    lines.extend(
        [
            "",
            "## Complete conversation — authoritative source",
            "",
            _text(receipt.get("complete_conversation")),
            "",
            "## Source-end decision state",
            "",
            _json_block(receipt.get("decision_state_at_source_end")),
            "",
            "## Frozen source-fidelity contract",
            "",
            _json_block(receipt.get("source_fidelity_contract")),
            "",
            "## Stage A — capture, interpretation, and pressure construction",
            "",
            f"Formal status: `{_text(stage_a.get('formal_status'))}`.",
            "",
            _text(stage_a.get("selection_method")),
            "",
            "Mechanical observations:",
            "",
            f"- {operations.get('captured_messages')}/12 messages captured; {operations.get('omitted_messages')} omitted.",
            f"- {operations.get('verified_reasoning_passages')} exact reasoning passages; {operations.get('remaining_quote_failures')} remaining quote failures.",
            f"- {operations.get('total_openrouter_calls')} OpenRouter calls and {operations.get('direct_openai_embedding_and_expansion_calls')} direct OpenAI calls.",
            f"- Estimated Stage A cost: `${float(operations.get('estimated_total_cost_usd', 0)):.6f}`.",
            f"- Main delta findings produced: `{_mapping(stage_a.get('semantic_admission')).get('main_delta_findings_produced')}`.",
            "",
            "Admitted pressures:",
            "",
            _json_block(stage_a.get("generator_packet")),
            "",
            "Rejected, deferred, or already covered candidates:",
            "",
            _json_block(stage_a.get("rejected_or_already_covered")),
            "",
            "## Stage B — frozen pair and blind review",
            "",
            f"Mechanical status: `{_text(mechanical.get('status'))}`; {mechanical.get('call_count')} calls; {mechanical.get('experiment_retries')} retries; estimated cost `${float(mechanical.get('estimated_cost_usd', 0)):.6f}`.",
            "",
            "Anonymous output A:",
            "",
            _json_block(_list(stage_b.get("anonymous_outputs"))[0]),
            "",
            "Anonymous output B:",
            "",
            _json_block(_list(stage_b.get("anonymous_outputs"))[1]),
            "",
            "Blind review sealed before key:",
            "",
            _json_block(stage_b.get("blind_review_before_key")),
            "",
            "Reveal mapping:",
            "",
            _json_block(stage_b.get("reveal_mapping")),
            "",
            "Post-reveal comparison without regrading:",
            "",
            _json_block(stage_b.get("comparison_after_reveal_without_regrading")),
            "",
            "Claim classification:",
            "",
            _json_block(stage_b.get("claim_classification")),
            "",
            "Measurement correction:",
            "",
            _json_block(stage_b.get("measurement_correction")),
            "",
            "## Graph attribution and repair",
            "",
            "The first provider-free attribution was preserved as incomplete:",
            "",
            _json_block(graph.get("v1_preserved_failure")),
            "",
            "The prospective v2 repair inspected the complete Step 6 surface:",
            "",
            _json_block(graph.get("v2_complete_consumer_result")),
            "",
            "Source-first review of exact graph chunks:",
            "",
            _json_block(graph.get("source_first_chunk_review")),
            "",
            "Metadata-only exact graph identities:",
            "",
            _json_block(graph.get("shadow_exact_identities")),
            "",
            "## What may and may not be claimed",
            "",
            "Supported:",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in _list(claims.get("supported")))
    lines.extend(["", "Unsupported or forbidden:", ""])
    lines.extend(f"- {item}" for item in _list(claims.get("unsupported_or_forbidden")))
    lines.extend(
        [
            "",
            "## Whole-run operability",
            "",
            _json_block(receipt.get("whole_run_operability")),
            "",
            "## Current authorizations",
            "",
            _json_block(receipt.get("current_authorizations")),
            "",
            "## Questions for a cold reader",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in _list(receipt.get("open_questions_for_cold_reader")))
    lines.extend(["", "## Artifact manifest", "", _json_block(receipt.get("artifact_manifest"))])
    lines.extend(["", "## Non-claims", ""])
    lines.extend(f"- {item}" for item in _list(receipt.get("non_claims")))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    contract_path = _resolve(root, args.contract)
    contract = _load_json(contract_path)
    paths = validate_contract(contract, root=root)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry_run_valid",
                    "input_count": len(_list(contract.get("inputs"))),
                    "provider_calls": 0,
                },
                indent=2,
            )
        )
        return 0
    receipt = build_receipt(contract, paths=paths)
    markdown = render_markdown(receipt)
    for role in ("output_json", "output_markdown"):
        if paths[role].exists():
            raise ContractError(f"refusing to overwrite existing output: {paths[role]}")
        paths[role].parent.mkdir(parents=True, exist_ok=True)
    paths["output_json"].write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    paths["output_markdown"].write_text(markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": receipt["status"],
                "conversation_sha256": _text(
                    next(
                        row["sha256"]
                        for row in receipt["artifact_manifest"]
                        if row["role"] == "source_conversation"
                    )
                ),
                "receipt_json_sha256": _sha256(paths["output_json"]),
                "receipt_markdown_sha256": _sha256(paths["output_markdown"]),
                "provider_calls": 0,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
