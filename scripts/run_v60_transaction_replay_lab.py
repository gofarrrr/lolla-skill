#!/usr/bin/env python3
"""Build local v60 transaction replay-lab artifacts.

This is an offline preflight harness. It assembles case context, candidate
nominations, grouped v60 reasoning-substrate packets, prompt packets, and
ledger templates. It does not change live Lolla runtime behavior.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.card_transaction_ledger import (  # noqa: E402
    LEDGER_VERSION,
    RUNTIME_POLICY,
    STATUS,
    summarize_card_transactions,
    validate_card_transaction_ledger_payload,
)
from system_b.reasoning_substrate_packet import (  # noqa: E402
    CandidateNomination,
    build_reasoning_substrate_packet_from_files,
)


LAB_VERSION = "v60_transaction_replay_lab.v1"
DEFAULT_AFFORDANCES_PATH = Path("data/compiled/model_affordances/affordances_v60.json")
DEFAULT_OUTPUT_DIR = Path("data/evaluations/v60_transaction_replay_lab")
DEFAULT_CARD_CAP = 12
DEFAULT_SNIPPET_CAP = 2
DEFAULT_DECODER_SNIPPET_CAP = 1
DEFAULT_MAX_NOMINATIONS = 18


class ReplayLabError(RuntimeError):
    pass


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    result_path: Path | None
    conversation_path: Path | None
    extraction_path: Path | None
    query: str
    vanilla_answer: str
    include_reason: str
    risk_notes: tuple[str, ...]
    tags: tuple[str, ...]
    explicit_nominations: tuple[CandidateNomination, ...]

    @property
    def file_stem(self) -> str:
        return _slug(self.case_id)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = REPO_ROOT
    manifest_path = _resolve(root, args.case_manifest)
    affordances_path = _resolve(root, args.affordances_path)
    output_dir = _resolve(root, args.output_dir)
    if not args.dry_run:
        raise ReplayLabError("Only --dry-run is implemented for the first local lab slice")
    if affordances_path.name != "affordances_v60.json":
        raise ReplayLabError("The v60 replay lab requires explicit affordances_v60.json")

    manifest = _load_json(manifest_path)
    cases = load_case_specs(manifest, root=root)
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, Any]] = []
    for case in cases:
        case_artifact = build_case_artifact(case, root=root)
        nominations = (
            *case.explicit_nominations,
            *extract_nominations_from_result(
                case_artifact.get("result", {}),
                max_nominations=args.max_nominations,
            ),
        )
        nominations = merge_nominations(nominations)[: args.max_nominations]
        packet = build_reasoning_substrate_packet_from_files(
            root=root,
            packet_id=f"v60-local-replay-{case.file_stem}",
            transaction_context={
                "case_id": case.case_id,
                "lab_version": LAB_VERSION,
                "include_reason": case.include_reason,
                "risk_notes": list(case.risk_notes),
                "tags": list(case.tags),
                "dry_run": True,
            },
            nominations=list(nominations),
            affordances_path=affordances_path,
            candidate_card_target_max=args.card_cap,
            snippet_target_max_per_card=args.snippet_cap,
        )
        ledger_template = build_dry_run_ledger_template(packet)
        validate_card_transaction_ledger_payload(ledger_template, packet=packet)

        arm_a = build_arm_a(case_artifact)
        arm_b = build_arm_b(case_artifact)
        arm_c = build_arm_c(
            case_artifact,
            packet,
            decoder_snippet_cap=args.decoder_snippet_cap,
        )

        _write_json(output_dir / "cases" / f"{case.file_stem}.json", case_artifact)
        _write_json(output_dir / "packets" / f"{case.file_stem}.json", packet)
        _write_json(output_dir / "ledger_templates" / f"{case.file_stem}.json", ledger_template)
        _write_json(output_dir / "arms" / "arm_a" / f"{case.file_stem}.json", arm_a)
        _write_json(output_dir / "arms" / "arm_b" / f"{case.file_stem}.json", arm_b)
        _write_json(output_dir / "arms" / "arm_c" / f"{case.file_stem}.json", arm_c)

        quality_counts = packet_quality_counts(packet)
        summaries.append(
            {
                "case_id": case.case_id,
                "tags": list(case.tags),
                "nomination_count": len(nominations),
                "candidate_card_count": len(packet["candidate_cards"]),
                "suppressed_candidate_count": len(packet["suppressed_candidates"]),
                "coverage_summary": packet["coverage_summary"],
                "packet_quality_counts": quality_counts,
                "token_estimates": {
                    "packet": estimate_tokens(packet),
                    "arm_b_prompt_packet": estimate_tokens(arm_b),
                    "arm_c_packet_view": estimate_tokens(
                        arm_c["user_packet"]["reasoning_substrate_packet"]
                    ),
                    "arm_c_prompt_packet": estimate_tokens(arm_c),
                },
                "arm_a_path": f"arms/arm_a/{case.file_stem}.json",
                "arm_b_path": f"arms/arm_b/{case.file_stem}.json",
                "arm_c_path": f"arms/arm_c/{case.file_stem}.json",
                "packet_path": f"packets/{case.file_stem}.json",
                "ledger_template_path": f"ledger_templates/{case.file_stem}.json",
            }
        )

    summary = {
        "lab_version": LAB_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "dry_run": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_manifest": str(manifest_path),
        "affordances_path": str(affordances_path),
        "case_count": len(cases),
        "card_cap": args.card_cap,
        "snippet_cap": args.snippet_cap,
        "decoder_snippet_cap": args.decoder_snippet_cap,
        "max_nominations": args.max_nominations,
        "provider_plan": {
            "generator_model": args.generator_model,
            "judge_model": args.judge_model,
            "deepseek_policy": "avoid_for_first_replay_unless_explicitly_retesting",
            "paid_calls_made": False,
        },
        "cases": summaries,
    }
    _write_json(output_dir / "summary.json", summary)
    (output_dir / "preflight_report.md").write_text(
        render_preflight_report(summary), encoding="utf-8"
    )
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'preflight_report.md'}")
    return 0


def load_case_specs(manifest: Mapping[str, Any], *, root: Path) -> list[CaseSpec]:
    if str(manifest.get("lab_version")) != LAB_VERSION:
        raise ReplayLabError(f"case manifest must use lab_version {LAB_VERSION}")
    cases: list[CaseSpec] = []
    for index, raw_case in enumerate(_list(manifest.get("cases"))):
        row = _mapping(raw_case)
        case_id = _text(row.get("case_id"))
        if not case_id:
            raise ReplayLabError(f"cases[{index}].case_id is required")
        cases.append(
            CaseSpec(
                case_id=case_id,
                result_path=_optional_path(root, row.get("result_path")),
                conversation_path=_optional_path(root, row.get("conversation_path")),
                extraction_path=_optional_path(root, row.get("extraction_path")),
                query=_text(row.get("query")),
                vanilla_answer=_text(row.get("vanilla_answer")),
                include_reason=_text(row.get("include_reason")),
                risk_notes=tuple(_strings(row.get("risk_notes"))),
                tags=tuple(_strings(row.get("tags"))),
                explicit_nominations=tuple(_candidate_nominations(row.get("nominations"))),
            )
        )
    if not cases:
        raise ReplayLabError("case manifest has no cases")
    return cases


def build_case_artifact(case: CaseSpec, *, root: Path) -> dict[str, Any]:
    result = _load_json(case.result_path) if case.result_path else {}
    extraction = _load_json(case.extraction_path) if case.extraction_path else {}
    conversation = (
        case.conversation_path.read_text(encoding="utf-8") if case.conversation_path else ""
    )
    query = case.query or _text(result.get("query"))
    vanilla_answer = case.vanilla_answer or _text(result.get("vanilla_answer"))
    if not query and extraction:
        query = _extraction_query(extraction)
    return {
        "lab_version": LAB_VERSION,
        "case_id": case.case_id,
        "include_reason": case.include_reason,
        "risk_notes": list(case.risk_notes),
        "tags": list(case.tags),
        "source_paths": {
            "result_path": _relative(root, case.result_path),
            "conversation_path": _relative(root, case.conversation_path),
            "extraction_path": _relative(root, case.extraction_path),
        },
        "query": query,
        "vanilla_answer": vanilla_answer,
        "conversation_excerpt": conversation[:12000],
        "extraction": extraction,
        "result": result,
    }


def extract_nominations_from_result(
    result: Mapping[str, Any],
    *,
    max_nominations: int,
) -> tuple[CandidateNomination, ...]:
    rows: list[CandidateNomination] = []
    delta = _mapping(result.get("delta_card"))
    for model_id in _strings(delta.get("selected_model_ids")):
        rows.append(
            _nomination(
                model_id=model_id,
                source="lane1_delta_card",
                reason="Selected by Lane 1 structural pressure.",
                lane_order=1,
            )
        )
    for finding in (_mapping(item) for item in _list(delta.get("findings"))):
        reason = _text(finding.get("tendency_id")) or "Lane 1 finding"
        for model_id in _strings(finding.get("selected_model_ids")):
            rows.append(
                _nomination(
                    model_id=model_id,
                    source="lane1_finding",
                    reason=reason,
                    evidence_quote=_text(finding.get("specific_passage")),
                    lane_order=1,
                )
            )

    companion = _mapping(result.get("companion_cheat_sheet"))
    for anchor in (_mapping(item) for item in _list(companion.get("anchors"))):
        model_id = _text(anchor.get("model_id"))
        if model_id:
            rows.append(
                _nomination(
                    model_id=model_id,
                    source="lane2_companion_anchor",
                    reason=_text(anchor.get("presence_explanation")) or "Lane 2 anchor.",
                    evidence_quote=_text(anchor.get("evidence_quote")),
                    lane_order=2,
                )
            )

    frame = _mapping(result.get("frame_pressure_card"))
    for item in (_mapping(row) for row in _list(frame.get("reframings"))):
        model_id = _text(item.get("grounding_model") or item.get("model_id"))
        if model_id:
            rows.append(
                _nomination(
                    model_id=model_id,
                    source="lane3_frame_reframing",
                    reason=_text(item.get("what_opens")) or "Lane 3 reframing.",
                    evidence_quote=_text(item.get("reframed_question")),
                    lane_order=3,
                )
            )

    coverage = _mapping(result.get("structural_coverage_card"))
    for route in (_mapping(item) for item in _list(coverage.get("gap_routes"))):
        route_id = _text(route.get("dimension_id"))
        route_name = _text(route.get("dimension_name")) or route_id
        for model_id in _strings(route.get("candidate_model_ids")):
            rows.append(
                _nomination(
                    model_id=model_id,
                    source="lane4_gap_route",
                    reason=f"Candidate for structural gap: {route_name}.",
                    route_or_artifact_id=route_id,
                    lane_order=4,
                )
            )
    return tuple(rows[: max(max_nominations * 3, max_nominations)])


def merge_nominations(
    nominations: tuple[CandidateNomination, ...] | list[CandidateNomination],
) -> tuple[CandidateNomination, ...]:
    by_model: dict[str, list[CandidateNomination]] = defaultdict(list)
    order: list[str] = []
    for nomination in nominations:
        model_id = _slug(nomination.model_id)
        if model_id not in by_model:
            order.append(model_id)
        by_model[model_id].append(nomination)

    merged: list[CandidateNomination] = []
    for model_id in order:
        rows = by_model[model_id]
        pulled_by: list[str] = []
        why_pulled: list[Mapping[str, Any]] = []
        lane_orders = [row.lane_order for row in rows if row.lane_order is not None]
        lane_scores = [row.lane_score for row in rows if row.lane_score is not None]
        for row in rows:
            pulled_by.extend(row.pulled_by)
            why_pulled.extend(row.why_pulled)
        merged.append(
            CandidateNomination(
                model_id=model_id,
                pulled_by=tuple(dict.fromkeys(pulled_by)),
                why_pulled=tuple(why_pulled),
                lane_order=min(lane_orders) if lane_orders else None,
                lane_score=max(lane_scores) if lane_scores else None,
            )
        )
    return tuple(
        sorted(
            merged,
            key=lambda item: (
                item.lane_order if item.lane_order is not None else 10**9,
                order.index(_slug(item.model_id)),
            ),
        )
    )


def build_dry_run_ledger_template(packet: Mapping[str, Any]) -> dict[str, Any]:
    transactions = []
    for card in (_mapping(item) for item in _list(packet.get("candidate_cards"))):
        transactions.append(
            {
                "card_id": _text(card.get("card_id")),
                "model_id": _text(card.get("model_id")),
                "disposition": "deferred",
                "effect_type": "no_effect",
                "affordance_ids_considered": [],
                "merged_with_card_ids": [],
                "strongest_plausible_application": "Dry-run placeholder; decoder not run.",
                "grounding_check": {
                    "case_quote": "",
                    "evidence_status": "missing",
                    "missing_evidence": ["decoder_not_run_dry_run"],
                },
                "decision_reason": "Dry-run placeholder for shape validation only.",
                "risk_if_forced": "Would pretend semantic card handling occurred.",
                "residue": "Run the decoder before interpreting this ledger.",
                "final_answer_delta": "",
                "final_answer_visibility": "not_visible",
            }
        )
    return {
        "ledger_version": LEDGER_VERSION,
        "packet_id": _text(packet.get("packet_id")),
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "dry_run_placeholder": True,
        "card_transactions": transactions,
        "summary": summarize_card_transactions(transactions),
    }


def packet_quality_counts(packet: Mapping[str, Any]) -> dict[str, int]:
    counts = {
        "reviewed_affordance_card_count": 0,
        "absence_record_count": 0,
        "medium_confidence_affordance_count": 0,
        "weak_support_affordance_count": 0,
    }
    for card in (_mapping(item) for item in _list(packet.get("candidate_cards"))):
        affordance_cards = [_mapping(item) for item in _list(card.get("reviewed_affordance_cards"))]
        counts["reviewed_affordance_card_count"] += len(affordance_cards)
        counts["absence_record_count"] += len(_list(card.get("absence_records")))
        for affordance in affordance_cards:
            if _text(affordance.get("confidence")) == "medium":
                counts["medium_confidence_affordance_count"] += 1
            if _text(affordance.get("status")) == "weak_support":
                counts["weak_support_affordance_count"] += 1
    return counts


def estimate_tokens(payload: Any) -> int:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return max(1, (len(text) + 3) // 4)


def build_arm_a(case_artifact: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "lab_version": LAB_VERSION,
        "arm": "A",
        "role": "vanilla_or_archived_baseline",
        "case_id": _text(case_artifact.get("case_id")),
        "query": _text(case_artifact.get("query")),
        "baseline_answer": _text(case_artifact.get("vanilla_answer")),
        "instructions": "No generation is needed in dry-run mode; this is the baseline answer.",
    }


def build_arm_b(case_artifact: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "lab_version": LAB_VERSION,
        "arm": "B",
        "role": "strong_generic_reconsideration",
        "system_prompt": STRONG_GENERIC_SYSTEM_PROMPT,
        "user_packet": {
            "case_id": _text(case_artifact.get("case_id")),
            "query": _text(case_artifact.get("query")),
            "vanilla_answer": _text(case_artifact.get("vanilla_answer")),
            "conversation_excerpt": _text(case_artifact.get("conversation_excerpt")),
            "output_contract": REPLAY_OUTPUT_CONTRACT,
        },
    }


def build_arm_c(
    case_artifact: Mapping[str, Any],
    packet: Mapping[str, Any],
    *,
    decoder_snippet_cap: int,
) -> dict[str, Any]:
    return {
        "lab_version": LAB_VERSION,
        "arm": "C",
        "role": "grouped_v60_transaction_reconsideration",
        "system_prompt": V60_TRANSACTION_SYSTEM_PROMPT,
        "user_packet": {
            "case_id": _text(case_artifact.get("case_id")),
            "query": _text(case_artifact.get("query")),
            "vanilla_answer": _text(case_artifact.get("vanilla_answer")),
            "conversation_excerpt": _text(case_artifact.get("conversation_excerpt")),
            "reasoning_substrate_packet": decoder_packet_view(
                packet,
                decoder_snippet_cap=decoder_snippet_cap,
            ),
            "output_contract": {
                **REPLAY_OUTPUT_CONTRACT,
                "card_transaction_ledger": "required; one transaction per candidate card",
            },
        },
    }


def decoder_packet_view(
    packet: Mapping[str, Any],
    *,
    decoder_snippet_cap: int,
) -> dict[str, Any]:
    """Project the rich audit packet into a compact decoder-facing shape."""

    cap = max(1, decoder_snippet_cap)
    return {
        "packet_id": _text(packet.get("packet_id")),
        "packet_version": _text(packet.get("packet_version")),
        "status": _text(packet.get("status")),
        "runtime_policy": _text(packet.get("runtime_policy")),
        "view": "decoder_compact_v1",
        "source_artifacts": _strings(packet.get("source_artifacts")),
        "transaction_context": _mapping(packet.get("transaction_context")),
        "coverage_summary": _mapping(packet.get("coverage_summary")),
        "candidate_cards": [
            _decoder_candidate_card(_mapping(card), decoder_snippet_cap=cap)
            for card in _list(packet.get("candidate_cards"))
        ],
        "suppressed_candidates": [
            {
                "model_id": _text(item.get("model_id")),
                "suppression_reason": _text(item.get("suppression_reason")),
                "coverage_status": _text(item.get("coverage_status")),
            }
            for item in (_mapping(row) for row in _list(packet.get("suppressed_candidates")))
        ],
    }


def _decoder_candidate_card(
    card: Mapping[str, Any],
    *,
    decoder_snippet_cap: int,
) -> dict[str, Any]:
    custody = _mapping(card.get("source_custody"))
    return {
        "card_id": _text(card.get("card_id")),
        "model_id": _text(card.get("model_id")),
        "display_name": _text(card.get("display_name")),
        "coverage_status": _text(card.get("coverage_status")),
        "pulled_by": _strings(card.get("pulled_by")),
        "why_pulled": [
            {
                "source": _text(item.get("source")),
                "reason": _text(item.get("reason")),
                "evidence_quote": _text(item.get("evidence_quote")),
                "route_or_artifact_id": _text(item.get("route_or_artifact_id")),
            }
            for item in (_mapping(row) for row in _list(card.get("why_pulled"))[:decoder_snippet_cap])
        ],
        "nomination_metadata": _mapping(card.get("nomination_metadata")),
        "source_custody": {
            "custody_status": _text(custody.get("custody_status")),
            "source_file": _text(custody.get("source_file")),
            "reviewed_record_available": bool(custody.get("reviewed_record_available")),
        },
        "reviewed_affordance_cards": [
            _decoder_affordance_card(_mapping(item), decoder_snippet_cap=decoder_snippet_cap)
            for item in _list(card.get("reviewed_affordance_cards"))[:decoder_snippet_cap]
        ],
        "absence_records": [
            {
                "attempted_field": _text(item.get("attempted_field")),
                "status": _text(item.get("status")),
                "reason": _text(item.get("reason")),
                "runtime_policy": _text(item.get("runtime_policy")),
            }
            for item in (_mapping(row) for row in _list(card.get("absence_records"))[:decoder_snippet_cap])
        ],
        "do_not_overclaim": _strings(card.get("do_not_overclaim"))[:decoder_snippet_cap],
        "llm_instruction": _text(card.get("llm_instruction")),
    }


def _decoder_affordance_card(
    affordance: Mapping[str, Any],
    *,
    decoder_snippet_cap: int,
) -> dict[str, Any]:
    activation = _mapping(affordance.get("activation_shape"))
    return {
        "affordance_id": _text(affordance.get("affordance_id")),
        "status": _text(affordance.get("status")),
        "confidence": _text(affordance.get("confidence")),
        "mechanism": _text(affordance.get("mechanism")),
        "activation_shape": {
            "use_when": _strings(activation.get("use_when"))[:decoder_snippet_cap],
            "case_evidence_needed": _strings(activation.get("case_evidence_needed"))[
                :decoder_snippet_cap
            ],
            "do_not_use_when": _strings(activation.get("do_not_use_when"))[
                :decoder_snippet_cap
            ],
        },
        "treatment_requirements": [
            {
                "affordance_id": _text(item.get("affordance_id")),
                "requirement_id": _text(item.get("requirement_id")),
                "description": _text(item.get("description")),
                "evidence_required": _strings(item.get("evidence_required"))[
                    :decoder_snippet_cap
                ],
                "good_output_shape": _strings(item.get("good_output_shape"))[
                    :decoder_snippet_cap
                ],
            }
            for item in (
                _mapping(row)
                for row in _list(affordance.get("treatment_requirements"))[
                    :decoder_snippet_cap
                ]
            )
        ],
        "diagnostic_questions": _strings(affordance.get("diagnostic_questions"))[
            :decoder_snippet_cap
        ],
        "misuse_guards": _strings(affordance.get("misuse_guards"))[:decoder_snippet_cap],
        "source_evidence": [
            {
                "affordance_id": _text(item.get("affordance_id")),
                "source_file": _text(item.get("source_file")),
                "source_quote": _text(item.get("source_quote")),
                "source_custody": _text(item.get("source_custody")),
            }
            for item in (
                _mapping(row)
                for row in _list(affordance.get("source_evidence"))[:decoder_snippet_cap]
            )
        ],
    }


STRONG_GENERIC_SYSTEM_PROMPT = """\
You are revising a decision answer. Be concrete, case-faithful, and skeptical
of fluent overconfidence. Surface hidden trade-offs, missing evidence, useful
questions, and confidence limits. Do not use mental-model name-dropping.
Return JSON only.
"""


V60_TRANSACTION_SYSTEM_PROMPT = """\
You are revising a decision answer using reviewed reasoning-substrate cards.
The cards are not instructions to mention mental models and are not final
conclusions. For each card, use, reject, or defer it. Use a card only if it
causes a concrete reasoning delta. Reject or defer with grounded reasons, and
name the risk if the card were forced. Preserve absence records as blockers and
overclaim rails. Return JSON only.
"""


REPLAY_OUTPUT_CONTRACT = {
    "final_answer": "revised answer for the user; concise and decision-useful",
    "reasoning_delta_summary": [
        "what changed from the vanilla answer",
        "what was deliberately not changed",
    ],
    "risk_register": [
        "invented fact risk",
        "overclaim risk",
        "model theater risk",
    ],
}


def render_preflight_report(summary: Mapping[str, Any]) -> str:
    lines = [
        "# V60 Transaction Replay Lab Preflight",
        "",
        "## Boundary",
        "",
        "- Dry run only; no model calls were made.",
        f"- Runtime policy: `{_text(summary.get('runtime_policy'))}`.",
        f"- Affordance artifact: `{_text(summary.get('affordances_path'))}`.",
        "- Live `/lolla`, Step 6, Step 8, memo, and Observatory behavior are unchanged.",
        "",
        "## Cases",
        "",
        "| Case | Cards | Suppressed | Reviewed | Weak/conflicting | Absence-only | Medium aff. | Weak aff. | Absence records |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for case in _list(summary.get("cases")):
        row = _mapping(case)
        coverage = _mapping(row.get("coverage_summary"))
        quality = _mapping(row.get("packet_quality_counts"))
        lines.append(
            "| "
            f"`{_text(row.get('case_id'))}` | "
            f"{int(row.get('candidate_card_count') or 0)} | "
            f"{int(row.get('suppressed_candidate_count') or 0)} | "
            f"{int(coverage.get('reviewed_card_count') or 0)} | "
            f"{int(coverage.get('conflicting_or_weak_support_count') or 0)} | "
            f"{int(coverage.get('absence_only_card_count') or 0)} | "
            f"{int(quality.get('medium_confidence_affordance_count') or 0)} | "
            f"{int(quality.get('weak_support_affordance_count') or 0)} | "
            f"{int(quality.get('absence_record_count') or 0)} |"
        )

    lines.extend(
        [
            "",
            "## Token Pressure",
            "",
            "| Case | Stored packet est. | Arm C view est. | Arm B est. | Arm C est. |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for case in _list(summary.get("cases")):
        row = _mapping(case)
        estimates = _mapping(row.get("token_estimates"))
        lines.append(
            "| "
            f"`{_text(row.get('case_id'))}` | "
            f"{int(estimates.get('packet') or 0)} | "
            f"{int(estimates.get('arm_c_packet_view') or 0)} | "
            f"{int(estimates.get('arm_b_prompt_packet') or 0)} | "
            f"{int(estimates.get('arm_c_prompt_packet') or 0)} |"
        )

    lines.extend(
        [
            "",
            "## Architecture Read",
            "",
            "- The lab uses explicit v60 path selection and grouped packet artifacts.",
            "- Arm C uses a compact decoder-facing packet projection; full packets remain available for audit.",
            "- Python validates IDs, shape, caps, and ledger traceability; it does not judge semantic use.",
            "- Dry-run ledger templates are placeholders and must not be interpreted as evidence.",
            "",
            "## User Read",
            "",
            "- The future user value being tested is extra cognitive leverage, not more model names.",
            "- Good Arm C output should be clearer about evidence, trade-offs, missing facts, and commitment thresholds.",
            "- A useful outcome may reject or defer most cards.",
            "",
            "## Product Read",
            "",
            "- The first product question is whether grouped cards beat a strong generic prompt.",
            "- Stability matters: rerun drift and cheap rejection must be measured before promotion.",
            "- The next integration, if earned, is review-only artifacts rather than user-facing copy.",
            "",
            "## Monetization Read",
            "",
            "- If the lab works, the monetizable unit is higher-trust decision review, not a longer answer.",
            "- Likely premium surfaces: audit trail, edge discovery, source-backed challenge, and team decision memos.",
            "- Cost must be controlled by caps, dry-run preflight, and separating generator from judge calls.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _candidate_nominations(value: Any) -> list[CandidateNomination]:
    rows: list[CandidateNomination] = []
    for index, raw in enumerate(_list(value)):
        item = _mapping(raw)
        model_id = _text(item.get("model_id"))
        if not model_id:
            raise ReplayLabError(f"nominations[{index}].model_id is required")
        rows.append(
            CandidateNomination(
                model_id=model_id,
                pulled_by=tuple(_strings(item.get("pulled_by")) or ["manifest"]),
                why_pulled=tuple(
                    _mapping(row) for row in _list(item.get("why_pulled"))
                )
                or (
                    {
                        "source": "manifest",
                        "reason": _text(item.get("reason")) or "Explicit manifest nomination.",
                    },
                ),
                lane_order=int(item["lane_order"]) if "lane_order" in item else None,
                lane_score=float(item["lane_score"]) if "lane_score" in item else None,
            )
        )
    return rows


def _nomination(
    *,
    model_id: str,
    source: str,
    reason: str,
    lane_order: int,
    evidence_quote: str = "",
    route_or_artifact_id: str = "",
) -> CandidateNomination:
    why: dict[str, Any] = {"source": source, "reason": reason}
    if evidence_quote:
        why["evidence_quote"] = evidence_quote
    if route_or_artifact_id:
        why["route_or_artifact_id"] = route_or_artifact_id
    return CandidateNomination(
        model_id=model_id,
        pulled_by=(source,),
        why_pulled=(why,),
        lane_order=lane_order,
    )


def _extraction_query(extraction: Mapping[str, Any]) -> str:
    parts = []
    for key in ("decision_situation", "original_framing"):
        value = _text(extraction.get(key))
        if value:
            parts.append(value)
    return "\n\n".join(parts)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-manifest", required=True, type=Path)
    parser.add_argument("--affordances-path", type=Path, default=DEFAULT_AFFORDANCES_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--card-cap", type=int, default=DEFAULT_CARD_CAP)
    parser.add_argument("--snippet-cap", type=int, default=DEFAULT_SNIPPET_CAP)
    parser.add_argument("--decoder-snippet-cap", type=int, default=DEFAULT_DECODER_SNIPPET_CAP)
    parser.add_argument("--max-nominations", type=int, default=DEFAULT_MAX_NOMINATIONS)
    parser.add_argument("--generator-model", default="x-ai/grok-4.1-fast")
    parser.add_argument("--judge-model", default="moonshotai/kimi-k2.6")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _resolve(root: Path, path: Path) -> Path:
    path = Path(path).expanduser()
    return path if path.is_absolute() else root / path


def _optional_path(root: Path, value: Any) -> Path | None:
    text = _text(value)
    if not text:
        return None
    path = _resolve(root, Path(text))
    if not path.exists():
        raise ReplayLabError(f"missing path: {path}")
    return path


def _relative(root: Path, path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReplayLabError(f"{path}: expected JSON object")
    return payload


def _slug(value: str) -> str:
    return _text(value).replace("_", "-").lower()


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
