#!/usr/bin/env python3
"""Run C4.5 system-bound v60 enrichment replay.

C4.5 treats v60 as part of the larger Lolla system instead of a standalone
feature. It starts from real replay artifacts, preserves lane provenance, uses
embedding-assisted exact v60 chunks, consumes a private chunk trace, and asks a
composer-boundary model to admit at most small, safe answer deltas.

The run is dormant lab evidence only. It does not attach v60 to live /lolla.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from scripts.run_v60_chunk_exact_private_replay import (  # noqa: E402
    DEFAULT_EMBEDDING_SUMMARY,
    build_exact_chunk_packet,
    build_v60_index,
    call_json_with_timeout,
    has_private_language,
    load_dotenv,
    validate_private_trace,
)
from scripts.run_v60_transaction_paid_replay import (  # noqa: E402
    DEFAULT_CASE_MANIFEST,
    DEFAULT_GENERATOR_MODEL,
    ReplayCallError,
    estimate_tokens,
)
from scripts.run_v60_transaction_replay_lab import (  # noqa: E402
    DEFAULT_AFFORDANCES_PATH,
    LAB_VERSION,
    RUNTIME_POLICY,
    STATUS,
    build_case_artifact,
    extract_nominations_from_result,
    load_case_specs,
    merge_nominations,
)


SYSTEM_BOUND_REPLAY_VERSION = "v60_system_bound_enrichment_replay.v1"
DEFAULT_PRIVATE_TRACE_DIR = Path(
    "data/evaluations/v60_transaction_replay_lab/"
    "2026-05-10-c44c-exact-chunk-private-replay-hardened-paid"
)
DEFAULT_OUTPUT_DIR = Path(
    "data/evaluations/v60_transaction_replay_lab/"
    "2026-05-10-c45-system-bound-enrichment"
)
DEFAULT_MAX_NOMINATIONS = 18
DEFAULT_MAX_ADMITTED = 2
DEFAULT_CONVERSATION_CHARS = 9000
DEFAULT_VANILLA_CHARS = 6500

ADMISSION_DECISIONS = frozenset(
    {
        "admit_delta",
        "no_delta",
        "diagnostic_only",
        "evidence_gate_only",
        "guardrail_only",
        "mixed",
        "public_delta_candidate",
    }
)
DELTA_TYPES = frozenset(
    {
        "option_space_expansion",
        "evidence_gate",
        "diagnostic_question",
        "risk_caveat",
        "concrete_next_move",
        "answer_clarification",
        "no_public_delta",
    }
)
QUALITY_VALUES = frozenset({"high", "medium", "low"})
FRICTION_VALUES = frozenset({"low", "medium", "high"})
PUBLIC_PRIVATE_TERMS = (
    "substrate",
    "packet",
    "card-",
    "affordance",
    "ledger",
    "v60",
    "mental model",
    "aff::",
    "abs::",
)

COMPOSER_SYSTEM_PROMPT = """\
You are a private Lolla answer-composition boundary.

You receive:
- the existing Lolla answer;
- a private, validated opportunity summary created from lane nominations,
  embedding recall, and exact v60 affordance/absence consideration;
- source and friction metadata.

Your job is not to use everything. Quality comes first, but friction matters:
admit at most two small public deltas only when they clearly improve the
existing answer. Good outcomes include admitting no public delta, preserving a
private guardrail, asking for evidence, or rejecting overfit opportunities.

Never reveal private machinery. Public text must not mention v60, packets,
cards, affordances, ledgers, chunks, mental models, or internal source IDs.

Return JSON only. Do not include markdown.
"""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = REPO_ROOT
    manifest_path = resolve(root, args.case_manifest)
    affordances_path = resolve(root, args.affordances_path)
    embedding_summary_path = resolve(root, args.embedding_summary)
    private_trace_dir = resolve(root, args.private_trace_dir)
    output_dir = resolve(root, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if affordances_path.name != "affordances_v60.json":
        raise RuntimeError("C4.5 requires explicit affordances_v60.json")

    if not args.dry_run:
        load_dotenv(resolve(root, args.env_file) if args.env_file else root / ".env")
        api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required unless --dry-run is set")
    else:
        api_key = ""

    manifest = load_json(manifest_path)
    affordances = load_json(affordances_path)
    embedding_summary = load_json(embedding_summary_path)
    cases = load_case_specs(manifest, root=root)
    if args.cases:
        wanted = set(args.cases)
        cases = [case for case in cases if case.case_id in wanted]

    embedding_rows = {
        text(row.get("case_id")): mapping(row)
        for row in list_of(embedding_summary.get("cases"))
    }
    index = build_v60_index(affordances)

    rows: list[dict[str, Any]] = []
    calls: list[dict[str, Any]] = []
    for case in cases:
        case_artifact = build_case_artifact(case, root=root)
        embedding_row = embedding_rows.get(case.case_id)
        if not embedding_row:
            raise RuntimeError(f"Missing embedding row for case {case.case_id}")
        packet = build_exact_chunk_packet(
            case_id=case.case_id,
            case_stem=case.file_stem,
            embedding_row=embedding_row,
            index=index,
        )
        private_trace = load_private_trace(private_trace_dir, case.file_stem)
        private_validation = validate_private_trace(
            private_trace,
            packet=packet,
            assessment_level="chunk",
        )
        system_profile = build_system_profile(
            case=case,
            case_artifact=case_artifact,
            embedding_row=embedding_row,
            packet=packet,
            private_trace=private_trace,
            private_validation=private_validation,
            max_nominations=args.max_nominations,
        )
        composer_prompt = build_composer_prompt(
            case_artifact=case_artifact,
            system_profile=system_profile,
            max_admitted=args.max_admitted,
            conversation_chars=args.conversation_chars,
            vanilla_chars=args.vanilla_chars,
        )

        item_id = f"{case.file_stem}__system_bound_composer"
        print(f"running {item_id}", flush=True)
        if args.dry_run:
            composer_output = {
                "dry_run_placeholder": True,
                "item_id": item_id,
                "estimated_prompt_tokens": estimate_tokens(composer_prompt),
            }
            composer_validation = {"status": "not_run_dry_run"}
        elif private_validation.get("status") != "valid":
            composer_output = {
                "status": "skipped",
                "reason": "private_trace_invalid",
                "private_validation": private_validation,
            }
            composer_validation = {
                "status": "skipped_private_trace_invalid",
                "private_validation": private_validation,
            }
        else:
            try:
                composer_output, meta = call_json_with_timeout(
                    api_key=api_key,
                    model=args.generator_model,
                    system_prompt=COMPOSER_SYSTEM_PROMPT,
                    user_packet=composer_prompt,
                    stage=f"{item_id}:composer_boundary",
                    timeout_seconds=args.call_timeout_seconds,
                )
            except ReplayCallError as exc:
                composer_output = {
                    "status": "error",
                    "stage": exc.stage,
                    "error": str(exc),
                    "raw_content": exc.raw_content,
                }
                composer_validation = {"status": "error", "error": str(exc)}
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                composer_output = {
                    "status": "error",
                    "stage": f"{item_id}:composer_boundary",
                    "error": error,
                    "raw_content": "",
                }
                composer_validation = {"status": "error", "error": error}
            else:
                calls.append({"item_id": item_id, **meta})
                composer_validation = validate_composer_output(
                    composer_output,
                    system_profile=system_profile,
                    max_admitted=args.max_admitted,
                    allowed_numeric_text=json.dumps(composer_prompt, ensure_ascii=False),
                )
        print(f"finished {item_id}: {composer_validation.get('status')}", flush=True)

        write_json(output_dir / "packets" / f"{case.file_stem}.json", packet)
        write_json(output_dir / "system_profiles" / f"{case.file_stem}.json", system_profile)
        write_json(output_dir / "composer_prompts" / f"{case.file_stem}.json", composer_prompt)
        write_json(output_dir / "composer_outputs" / f"{case.file_stem}.json", composer_output)
        row = {
            "item_id": item_id,
            "case_id": case.case_id,
            "case_stem": case.file_stem,
            "status": "ok" if composer_validation.get("status") not in {"error"} else "error",
            "private_trace_validation": private_validation,
            "composer_validation": composer_validation,
            "system_profile_path": f"system_profiles/{case.file_stem}.json",
            "composer_prompt_path": f"composer_prompts/{case.file_stem}.json",
            "composer_output_path": f"composer_outputs/{case.file_stem}.json",
            "packet_path": f"packets/{case.file_stem}.json",
            "prompt_tokens_estimate": estimate_tokens(composer_prompt),
            "opportunity_count": len(list_of(system_profile.get("composer_opportunities"))),
            "packet_source_counts": mapping(system_profile.get("packet_source_counts")),
        }
        rows.append(row)

    summary = {
        "system_bound_replay_version": SYSTEM_BOUND_REPLAY_VERSION,
        "lab_version": LAB_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "dry_run": bool(args.dry_run),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_manifest": str(manifest_path),
        "affordances_path": str(affordances_path),
        "embedding_summary": str(embedding_summary_path),
        "private_trace_dir": str(private_trace_dir),
        "generator_model": "" if args.dry_run else args.generator_model,
        "max_admitted": args.max_admitted,
        "item_count": len(rows),
        "items": rows,
        "aggregate": aggregate(rows, calls),
        "call_records": calls,
    }
    write_json(output_dir / "summary.json", summary)
    (output_dir / "system_bound_enrichment_report.md").write_text(
        render_report(summary),
        encoding="utf-8",
    )
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'system_bound_enrichment_report.md'}")
    return 0


def build_system_profile(
    *,
    case: Any,
    case_artifact: Mapping[str, Any],
    embedding_row: Mapping[str, Any],
    packet: Mapping[str, Any],
    private_trace: Mapping[str, Any],
    private_validation: Mapping[str, Any],
    max_nominations: int,
) -> dict[str, Any]:
    nominations = merge_nominations(
        (
            *case.explicit_nominations,
            *extract_nominations_from_result(
                case_artifact.get("result", {}),
                max_nominations=max_nominations,
            ),
        )
    )
    nominations = nominations[:max_nominations]
    cards = {text(card.get("card_id")): mapping(card) for card in list_of(packet.get("chunk_cards"))}
    chunk_index = packet_chunk_index(packet)
    assessments = [mapping(item) for item in list_of(private_trace.get("chunk_assessments"))]
    selected = [mapping(item) for item in list_of(private_trace.get("selected_opportunities"))]

    lane_order_counts = Counter(
        str(nomination.lane_order if nomination.lane_order is not None else "manual")
        for nomination in nominations
    )
    packet_source_counts = Counter(text(card.get("selection_source")) for card in cards.values())
    assessment_routes = Counter(text(item.get("route")) for item in assessments)
    assessment_usefulness = Counter(text(item.get("usefulness_to_consider")) for item in assessments)

    composer_opportunities = []
    for opportunity in selected:
        source_chunk_ids = strings(opportunity.get("source_chunk_ids"))
        source_card_ids = strings(opportunity.get("source_card_ids"))
        source_details = []
        for chunk_id in source_chunk_ids:
            chunk = chunk_index.get(chunk_id, {})
            card = cards.get(text(chunk.get("card_id")), {})
            source_details.append(
                {
                    "chunk_kind": text(chunk.get("chunk_kind")),
                    "model_id": text(chunk.get("model_id")),
                    "selection_source": text(card.get("selection_source")),
                    "route": route_for_chunk(assessments, chunk_id),
                }
            )
        if not source_details:
            for card_id in source_card_ids:
                card = cards.get(card_id, {})
                source_details.append(
                    {
                        "chunk_kind": "",
                        "model_id": text(card.get("model_id")),
                        "selection_source": text(card.get("selection_source")),
                        "route": text(opportunity.get("route")),
                    }
                )
        composer_opportunities.append(
            {
                "opportunity_id": text(opportunity.get("opportunity_id")),
                "route": text(opportunity.get("route")),
                "private_value": text(opportunity.get("private_value")),
                "public_candidate": text(opportunity.get("public_candidate")),
                "public_admission_risk": text(opportunity.get("public_admission_risk")),
                "source_mix": sorted(
                    {
                        text(item.get("selection_source"))
                        for item in source_details
                        if text(item.get("selection_source"))
                    }
                ),
                "chunk_kind_mix": sorted(
                    {
                        text(item.get("chunk_kind"))
                        for item in source_details
                        if text(item.get("chunk_kind"))
                    }
                ),
                "model_ids": sorted(
                    {text(item.get("model_id")) for item in source_details if text(item.get("model_id"))}
                ),
                "source_chunk_count": len(source_chunk_ids),
            }
        )

    return {
        "profile_version": "c45_system_profile.v1",
        "case_id": text(case_artifact.get("case_id")),
        "system_role": "private_v60_enrichment_inside_existing_lolla_pipeline",
        "lane_profile": {
            "nomination_count": len(nominations),
            "lane_order_counts": dict(sorted(lane_order_counts.items())),
            "nominated_model_ids": [nomination.model_id for nomination in nominations],
            "lane_selected_cap8": strings(embedding_row.get("lane_selected_cap8")),
        },
        "embedding_profile": {
            "top_embedding_models": [
                {
                    "model_id": text(item.get("model_id")),
                    "best_chunk_id": text(item.get("best_chunk_id")),
                    "score": item.get("score"),
                }
                for item in (mapping(row) for row in list_of(embedding_row.get("top_embedding_models"))[:8])
            ],
            "top_absence_models": [
                {
                    "model_id": text(item.get("model_id")),
                    "best_chunk_id": text(item.get("best_chunk_id")),
                    "score": item.get("score"),
                }
                for item in (mapping(row) for row in list_of(embedding_row.get("top_absence_models"))[:8])
            ],
            "hybrid_rrf_top8": strings(embedding_row.get("hybrid_rrf_top8")),
        },
        "packet_source_counts": dict(sorted(packet_source_counts.items())),
        "private_trace_summary": {
            "validation": private_validation,
            "packet_usefulness": text(private_trace.get("packet_usefulness")),
            "assessment_count": len(assessments),
            "selected_opportunity_count": len(selected),
            "route_counts": dict(sorted((key, value) for key, value in assessment_routes.items() if key)),
            "usefulness_counts": dict(
                sorted((key, value) for key, value in assessment_usefulness.items() if key)
            ),
            "retrieval_feedback": strings(private_trace.get("retrieval_feedback")),
        },
        "composer_opportunities": composer_opportunities,
        "integration_policy": {
            "quality_first": True,
            "max_public_deltas": DEFAULT_MAX_ADMITTED,
            "allow_no_delta": True,
            "public_language_must_hide_private_machinery": True,
            "v60_role": "private_enrichment_not_user_feature",
        },
    }


def build_composer_prompt(
    *,
    case_artifact: Mapping[str, Any],
    system_profile: Mapping[str, Any],
    max_admitted: int,
    conversation_chars: int,
    vanilla_chars: int,
) -> dict[str, Any]:
    return {
        "case_id": text(case_artifact.get("case_id")),
        "query": text(case_artifact.get("query")),
        "conversation_excerpt": text(case_artifact.get("conversation_excerpt"))[:conversation_chars],
        "existing_lolla_answer": text(case_artifact.get("vanilla_answer"))[:vanilla_chars],
        "private_system_enrichment": {
            "lane_profile": mapping(system_profile.get("lane_profile")),
            "embedding_profile": mapping(system_profile.get("embedding_profile")),
            "packet_source_counts": mapping(system_profile.get("packet_source_counts")),
            "private_trace_summary": mapping(system_profile.get("private_trace_summary")),
            "composer_opportunities": list_of(system_profile.get("composer_opportunities")),
        },
        "composer_policy": {
            "max_admitted_public_deltas": max_admitted,
            "prefer_no_delta_over_low_value_addition": True,
            "treat_absence_and_guardrail_items_as_possible_private_only_controls": True,
            "do_not_explain_internal_mechanism_to_user": True,
            "do_not_force_opportunities_into_the_answer": True,
            "optimize_for_system_value_per_friction": True,
        },
        "output_contract": {
            "admission_decision": (
                "admit_delta | no_delta | diagnostic_only | evidence_gate_only | "
                "guardrail_only | mixed"
            ),
            "admitted_items": [
                {
                    "item_id": "stable short ID",
                    "source_opportunity_ids": ["must match composer_opportunities[*].opportunity_id"],
                    "delta_type": (
                        "option_space_expansion | evidence_gate | diagnostic_question | "
                        "risk_caveat | concrete_next_move | answer_clarification | no_public_delta"
                    ),
                    "public_delta": "short user-visible addition, or empty for private-only item",
                    "why_admitted": "why value exceeds friction",
                    "quality_value": "high | medium | low",
                    "friction_cost": "low | medium | high",
                    "risk_if_added": "how this could make the answer worse",
                }
            ],
            "rejected_items": [
                {
                    "source_opportunity_ids": ["opportunity IDs"],
                    "reason": "duplicate | too speculative | already covered | too much friction | unsafe",
                }
            ],
            "private_guardrails_preserved": [
                "private-only constraints worth preserving during composition"
            ],
            "user_visible_delta": (
                "combined short amendment only; empty if nothing should be surfaced"
            ),
            "no_delta_reason": "required if user_visible_delta is empty",
            "integration_feedback": [
                "what this test says about baking v60 into the larger system"
            ],
        },
    }


def validate_composer_output(
    payload: Mapping[str, Any],
    *,
    system_profile: Mapping[str, Any],
    max_admitted: int,
    allowed_numeric_text: str = "",
) -> dict[str, Any]:
    errors: list[str] = []
    opportunities = {
        text(item.get("opportunity_id")): mapping(item)
        for item in list_of(system_profile.get("composer_opportunities"))
        if text(mapping(item).get("opportunity_id"))
    }
    admission_decision = text(payload.get("admission_decision"))
    if admission_decision not in ADMISSION_DECISIONS:
        errors.append("admission_decision is invalid")
    admitted = [mapping(item) for item in list_of(payload.get("admitted_items"))]
    if not isinstance(payload.get("admitted_items"), list):
        errors.append("admitted_items must be a list")
    if len(admitted) > max_admitted:
        errors.append(f"admitted_items allows at most {max_admitted} items")
    public_delta_count = 0
    admitted_route_counts: Counter[str] = Counter()
    admitted_source_counts: Counter[str] = Counter()
    for index, item in enumerate(admitted):
        prefix = f"admitted_items[{index}]"
        source_ids = strings(item.get("source_opportunity_ids"))
        if not source_ids:
            errors.append(f"{prefix}.source_opportunity_ids is required")
        unknown = sorted(set(source_ids) - set(opportunities))
        if unknown:
            errors.append(f"{prefix}.source_opportunity_ids unknown: {unknown}")
        delta_type = text(item.get("delta_type"))
        if delta_type not in DELTA_TYPES:
            errors.append(f"{prefix}.delta_type is invalid")
        if text(item.get("quality_value")) not in QUALITY_VALUES:
            errors.append(f"{prefix}.quality_value is invalid")
        if text(item.get("friction_cost")) not in FRICTION_VALUES:
            errors.append(f"{prefix}.friction_cost is invalid")
        if not text(item.get("why_admitted")):
            errors.append(f"{prefix}.why_admitted is required")
        public_delta = text(item.get("public_delta"))
        if public_delta:
            public_delta_count += 1
            if leaks_private_language(public_delta):
                errors.append(f"{prefix}.public_delta leaks private language")
            novel_numbers = novel_numeric_tokens(public_delta, allowed_numeric_text)
            if novel_numbers:
                errors.append(f"{prefix}.public_delta has novel numeric claims: {novel_numbers}")
        for source_id in source_ids:
            opportunity = opportunities.get(source_id, {})
            admitted_route_counts[text(opportunity.get("route"))] += 1
            for source in strings(opportunity.get("source_mix")):
                admitted_source_counts[source] += 1

    rejected = [mapping(item) for item in list_of(payload.get("rejected_items"))]
    if not isinstance(payload.get("rejected_items"), list):
        errors.append("rejected_items must be a list")
    for index, item in enumerate(rejected):
        prefix = f"rejected_items[{index}]"
        unknown = sorted(set(strings(item.get("source_opportunity_ids"))) - set(opportunities))
        if unknown:
            errors.append(f"{prefix}.source_opportunity_ids unknown: {unknown}")
        if not text(item.get("reason")):
            errors.append(f"{prefix}.reason is required")

    user_visible_delta = text(payload.get("user_visible_delta"))
    if user_visible_delta:
        if leaks_private_language(user_visible_delta):
            errors.append("user_visible_delta leaks private language")
        novel_numbers = novel_numeric_tokens(user_visible_delta, allowed_numeric_text)
        if novel_numbers:
            errors.append(f"user_visible_delta has novel numeric claims: {novel_numbers}")
        if public_delta_count == 0:
            errors.append("user_visible_delta is present but no admitted public deltas exist")
    else:
        if not text(payload.get("no_delta_reason")):
            errors.append("no_delta_reason is required when user_visible_delta is empty")
    if admission_decision == "no_delta" and user_visible_delta:
        errors.append("no_delta decision cannot include user_visible_delta")

    status = "invalid" if errors else "valid"
    result = {
        "status": status,
        "admission_decision": admission_decision,
        "admitted_item_count": len(admitted),
        "public_delta_count": public_delta_count,
        "rejected_item_count": len(rejected),
        "admitted_route_counts": dict(sorted((k, v) for k, v in admitted_route_counts.items() if k)),
        "admitted_source_counts": dict(sorted(admitted_source_counts.items())),
        "user_visible_delta_chars": len(user_visible_delta),
    }
    if errors:
        result["errors"] = errors
    return result


def aggregate(rows: list[Mapping[str, Any]], calls: list[Mapping[str, Any]]) -> dict[str, Any]:
    private_counts = Counter(
        text(mapping(row.get("private_trace_validation")).get("status")) for row in rows
    )
    composer_counts = Counter(
        text(mapping(row.get("composer_validation")).get("status")) for row in rows
    )
    admission_counts = Counter()
    admitted_route_counts: Counter[str] = Counter()
    admitted_source_counts: Counter[str] = Counter()
    public_delta_count = 0
    opportunity_count = 0
    prompt_tokens = 0
    for row in rows:
        validation = mapping(row.get("composer_validation"))
        admission_counts[text(validation.get("admission_decision"))] += 1
        admitted_route_counts.update(mapping(validation.get("admitted_route_counts")))
        admitted_source_counts.update(mapping(validation.get("admitted_source_counts")))
        public_delta_count += integer(validation.get("public_delta_count"))
        opportunity_count += integer(row.get("opportunity_count"))
        prompt_tokens += integer(row.get("prompt_tokens_estimate"))
    return {
        "private_trace_validation_counts": dict(sorted((k, v) for k, v in private_counts.items() if k)),
        "composer_validation_counts": dict(sorted((k, v) for k, v in composer_counts.items() if k)),
        "admission_decision_counts": dict(sorted((k, v) for k, v in admission_counts.items() if k)),
        "admitted_route_counts": dict(sorted(admitted_route_counts.items())),
        "admitted_source_counts": dict(sorted(admitted_source_counts.items())),
        "opportunity_count": opportunity_count,
        "public_delta_count": public_delta_count,
        "estimated_prompt_tokens": prompt_tokens,
        "call_count": len(calls),
        "input_tokens": sum(integer(record.get("input_tokens")) for record in calls),
        "output_tokens": sum(integer(record.get("output_tokens")) for record in calls),
        "total_tokens": sum(integer(record.get("total_tokens")) for record in calls),
        "cost_usd": round(sum(float(record.get("cost_usd") or 0.0) for record in calls), 6),
    }


def render_report(summary: Mapping[str, Any]) -> str:
    aggregate_payload = mapping(summary.get("aggregate"))
    lines = [
        "# V60 C4.5 System-Bound Enrichment Report",
        "",
        f"Date: {text(summary.get('generated_at'))[:10]}",
        "Status: dormant integration replay evidence only",
        f"Generator: `{text(summary.get('generator_model')) or 'not run'}`",
        "",
        "## Aggregate",
        "",
        f"- Items: {integer(summary.get('item_count'))}",
        f"- Paid calls: {integer(aggregate_payload.get('call_count'))}",
        f"- Cost: `${aggregate_payload.get('cost_usd', 0)}`",
        f"- Private trace validation: `{json.dumps(mapping(aggregate_payload.get('private_trace_validation_counts')), sort_keys=True)}`",
        f"- Composer validation: `{json.dumps(mapping(aggregate_payload.get('composer_validation_counts')), sort_keys=True)}`",
        f"- Admission decisions: `{json.dumps(mapping(aggregate_payload.get('admission_decision_counts')), sort_keys=True)}`",
        f"- Public deltas admitted: {integer(aggregate_payload.get('public_delta_count'))}",
        f"- Admitted routes: `{json.dumps(mapping(aggregate_payload.get('admitted_route_counts')), sort_keys=True)}`",
        f"- Admitted sources: `{json.dumps(mapping(aggregate_payload.get('admitted_source_counts')), sort_keys=True)}`",
        "",
        "## Items",
        "",
        "| Item | Opportunities | Composer | Decision | Public Deltas | Sources |",
        "| --- | ---: | --- | --- | ---: | --- |",
    ]
    for row in (mapping(item) for item in list_of(summary.get("items"))):
        validation = mapping(row.get("composer_validation"))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{text(row.get('item_id'))}`",
                    str(integer(row.get("opportunity_count"))),
                    f"`{text(validation.get('status'))}`",
                    f"`{text(validation.get('admission_decision'))}`",
                    str(integer(validation.get("public_delta_count"))),
                    f"`{json.dumps(mapping(validation.get('admitted_source_counts')), sort_keys=True)}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "This run checks whether v60 can behave as an internal enrichment",
            "layer inside the existing lane/embedding/composer pipeline. It",
            "does not expose v60 chunks to users and does not attach behavior",
            "to live `/lolla`.",
            "",
        ]
    )
    return "\n".join(lines)


def load_private_trace(private_trace_dir: Path, case_stem: str) -> dict[str, Any]:
    path = private_trace_dir / "outputs" / f"{case_stem}.json"
    if not path.exists():
        raise RuntimeError(f"Missing private trace output: {path}")
    return load_json(path)


def packet_chunk_index(packet: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    chunks: dict[str, dict[str, str]] = {}
    for card in (mapping(item) for item in list_of(packet.get("chunk_cards"))):
        card_id = text(card.get("card_id"))
        model_id = text(card.get("model_id"))
        for affordance in (mapping(item) for item in list_of(card.get("selected_affordance_cards"))):
            chunk_id = text(affordance.get("chunk_id"))
            if chunk_id:
                chunks[chunk_id] = {
                    "card_id": card_id,
                    "model_id": model_id,
                    "chunk_kind": "affordance",
                }
        for absence in (mapping(item) for item in list_of(card.get("selected_absence_records"))):
            chunk_id = text(absence.get("chunk_id"))
            if chunk_id:
                chunks[chunk_id] = {
                    "card_id": card_id,
                    "model_id": model_id,
                    "chunk_kind": "absence",
                }
    return chunks


def route_for_chunk(assessments: list[Mapping[str, Any]], chunk_id: str) -> str:
    for assessment in assessments:
        if text(assessment.get("chunk_id")) == chunk_id:
            return text(assessment.get("route"))
    return ""


def leaks_private_language(value: str) -> bool:
    if has_private_language(value):
        return True
    lowered = value.lower()
    return any(term in lowered for term in PUBLIC_PRIVATE_TERMS)


def novel_numeric_tokens(public_text: str, allowed_text: str) -> list[str]:
    if not allowed_text:
        return []
    allowed_numbers = set(extract_numeric_tokens(allowed_text))
    return sorted(set(extract_numeric_tokens(public_text)) - allowed_numbers)


def extract_numeric_tokens(value: str) -> list[str]:
    tokens = []
    for match in re.finditer(r"\$\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(k|m|b)?", value, re.IGNORECASE):
        suffix = (match.group(3) or "").lower()
        tokens.append(f"${normalize_number(match.group(1))}{suffix}")
        tokens.append(f"${normalize_number(match.group(2))}{suffix}")
    for match in re.finditer(r"(?<![\w$])(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*%", value):
        tokens.append(f"{normalize_number(match.group(1))}%")
        tokens.append(f"{normalize_number(match.group(2))}%")
    pattern = re.compile(
        r"(?P<money>\$\s*\d+(?:\.\d+)?\s*(?:k|m|b)?)"
        r"|(?P<percent>\d+(?:\.\d+)?\s*%)"
        r"|(?P<plain>\d+(?:\.\d+)?)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(value):
        raw = match.group(0)
        normalized = re.sub(r"\s+", "", raw).lower()
        normalized = re.sub(r"(\d)\.0+($|[^\d])", r"\1\2", normalized)
        tokens.append(normalized)
    return tokens


def normalize_number(value: str) -> str:
    normalized = value.strip()
    if "." in normalized:
        normalized = normalized.rstrip("0").rstrip(".")
    return normalized


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-manifest", type=Path, default=DEFAULT_CASE_MANIFEST)
    parser.add_argument("--affordances-path", type=Path, default=DEFAULT_AFFORDANCES_PATH)
    parser.add_argument("--embedding-summary", type=Path, default=DEFAULT_EMBEDDING_SUMMARY)
    parser.add_argument("--private-trace-dir", type=Path, default=DEFAULT_PRIVATE_TRACE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--generator-model", default=DEFAULT_GENERATOR_MODEL)
    parser.add_argument("--max-nominations", type=int, default=DEFAULT_MAX_NOMINATIONS)
    parser.add_argument("--max-admitted", type=int, default=DEFAULT_MAX_ADMITTED)
    parser.add_argument("--conversation-chars", type=int, default=DEFAULT_CONVERSATION_CHARS)
    parser.add_argument("--vanilla-chars", type=int, default=DEFAULT_VANILLA_CHARS)
    parser.add_argument("--call-timeout-seconds", type=int, default=300)
    parser.add_argument("--cases", nargs="*", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def list_of(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def strings(value: Any) -> list[str]:
    return [text(item) for item in list_of(value) if text(item)]


def text(value: Any) -> str:
    return str(value or "").strip()


def integer(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
