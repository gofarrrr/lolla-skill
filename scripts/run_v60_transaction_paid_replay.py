#!/usr/bin/env python3
"""Run a controlled paid replay for the v60 transaction packet lab.

This harness is intentionally outside the live /lolla runtime. It builds the
same Arm B / Arm C packets used by the local matrix, optionally calls
OpenRouter, validates the Arm C transaction ledger shape, and asks a blinded
judge to compare user-facing outputs without seeing the ledger.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import urllib.error
import urllib.request
import uuid
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from system_b.card_transaction_ledger import (  # noqa: E402
    CardTransactionLedgerValidationError,
    EVIDENCE_STATUSES,
    summarize_card_transactions,
    validate_card_transaction_ledger_payload,
)
from system_b.reasoning_substrate_packet import (  # noqa: E402
    build_reasoning_substrate_packet_from_files,
)

from scripts.run_v60_transaction_replay_lab import (  # noqa: E402
    DEFAULT_AFFORDANCES_PATH,
    LAB_VERSION,
    RUNTIME_POLICY,
    STATUS,
    V60_TRANSACTION_SYSTEM_PROMPT,
    ReplayLabError,
    build_arm_b,
    build_arm_c,
    build_case_artifact,
    build_dry_run_ledger_template,
    estimate_tokens,
    extract_nominations_from_result,
    load_case_specs,
    merge_nominations,
    packet_quality_counts,
)
from scripts.run_v60_transaction_replay_matrix import (  # noqa: E402
    MATRIX_CONFIGS,
    SOLUTION_MODES,
    MatrixConfig,
    SolutionMode,
)


PAID_REPLAY_VERSION = "v60_transaction_paid_replay.v1"
DEFAULT_CASE_MANIFEST = Path("research/v60-transaction-replay-case-manifest-2026-05-09.json")
DEFAULT_OUTPUT_DIR = Path("data/evaluations/v60_transaction_replay_lab/2026-05-09-paid-pilot")
DEFAULT_CONFIG_ID = "cap8_focused"
DEFAULT_CASE_IDS = (
    "user_has_plan",
    "real_estate",
    "whistleblower",
    "messy_three_problems",
)
DEFAULT_MODE_IDS = ("edge_audit", "question_gate")
DEFAULT_C_VARIANT = "transaction"
C_VARIANTS = frozenset(
    {
        "transaction",
        "hidden",
        "delta",
        "delta_gated",
        "delta_compact",
        "one_edge",
        "candidate_edge",
        "candidate_edge_hardened",
        "consideration_router",
    }
)
DELTA_VARIANTS = frozenset({"delta", "delta_gated", "delta_compact"})
ONE_EDGE_VARIANTS = frozenset({"one_edge", "candidate_edge", "candidate_edge_hardened"})
CANDIDATE_EDGE_VARIANTS = frozenset({"candidate_edge", "candidate_edge_hardened"})
CANDIDATE_EDGE_HARDENED_VARIANTS = frozenset({"candidate_edge_hardened"})
GATED_DELTA_VARIANTS = frozenset({"delta_gated", "delta_compact"})
CONSIDERATION_ROUTER_VARIANTS = frozenset({"consideration_router"})
COMPOSED_AUDIT_VARIANTS = DELTA_VARIANTS | ONE_EDGE_VARIANTS
PUBLIC_DELTA_GATE_POLICY_BY_VARIANT = {
    "delta_gated": "c3_5",
    "delta_compact": "c3_6_compact",
    "one_edge": "c4_one_edge",
    "candidate_edge": "c4_1_candidate_edge",
    "candidate_edge_hardened": "c4_2_hardened_edge",
}
PUBLIC_DELTA_GATE_VERSION_BY_POLICY = {
    "c3_5": "c3_5_public_delta_gate.v1",
    "c3_6_compact": "c3_6_compact_public_delta_gate.v1",
    "c4_one_edge": "c4_one_edge_public_delta_gate.v1",
    "c4_1_candidate_edge": "c4_1_candidate_edge_public_delta_gate.v1",
    "c4_2_hardened_edge": "c4_2_hardened_edge_public_delta_gate.v1",
}
PUBLIC_DELTA_TYPES = frozenset(
    {
        "evidence_gate",
        "concrete_next_move",
        "risk_caveat",
        "option_space_expansion",
    }
)
CONSIDERATION_USEFULNESS_LEVELS = frozenset({"high", "medium", "low", "none"})
CONSIDERATION_PACKET_USEFULNESS = frozenset(
    {"useful", "mixed", "not_useful", "overfed", "underfed"}
)
CONSIDERATION_OPPORTUNITY_ROLES = frozenset(
    {
        "frame_changer",
        "evidence_gate",
        "diagnostic_question",
        "guardrail",
        "tension_maker",
        "boundary_marker",
        "compression_aid",
        "rejection_aid",
    }
)
CONSIDERATION_ROUTES = frozenset(
    {
        "private_reasoning",
        "public_answer_delta",
        "diagnostic_question",
        "evidence_gate",
        "guardrail",
        "defer_missing_evidence",
        "reject_irrelevant",
        "reject_duplicate",
    }
)
CONSIDERATION_SELECTED_ROUTES = frozenset(
    {
        "public_answer_delta",
        "diagnostic_question",
        "evidence_gate",
        "guardrail",
        "private_reasoning",
    }
)
PUBLIC_DELTA_GATE_MAX = 2
PUBLIC_DELTA_GATE_MAX_BY_POLICY = {
    "c3_5": 2,
    "c3_6_compact": 1,
}
PUBLIC_DELTA_TYPE_PRIORITY = {
    "evidence_gate": 0,
    "concrete_next_move": 1,
    "risk_caveat": 2,
    "option_space_expansion": 3,
}
DEFAULT_GENERATOR_MODEL = "x-ai/grok-4.1-fast"
DEFAULT_JUDGE_MODEL = "moonshotai/kimi-k2.6"
DEFAULT_SEED = 60
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_TIMEOUT_S = 240
OUTPUT_DISCIPLINE_SUFFIX = """\
Output discipline:
- Return every requested output_contract key.
- Use [] for empty lists, not null.
- Do not include markdown.
"""
LEDGER_DISCIPLINE_SUFFIX = """\
Ledger discipline:
- Use only enum values shown in card_transaction_ledger_schema.
- Do not use final_answer_visibility values as effect_type values.
- If a card merely confirms the vanilla answer and causes no concrete delta,
  reject it as duplicate_of_existing_pressure or defer it; do not mark it used.
- A used card must have an allowed effect_type and a concrete final_answer_delta.
"""
HIDDEN_VARIANT_SUFFIX = """\
Hidden-ledger discipline:
- The transaction packet is private audit material, not user-facing content.
- Fill private_transaction_ledger with one transaction per candidate card.
- Fill private_delta_notes with what changed, what did not, and why.
- The user_visible_answer and user_visible_edges must not mention cards,
  substrate, packets, ledgers, affordance IDs, model IDs, mental-model names,
  or review machinery.
- If the cards create no useful user-facing delta, produce a shorter and
  clearer answer rather than a meta-answer.
- final_answer must be the same public prose as user_visible_answer.
- edge_findings must be the same public list as user_visible_edges.
"""
DELTA_VARIANT_SUFFIX = """\
C3 delta-only discipline:
- The transaction packet is private audit material, not user-facing content.
- You are not the final-answer writer. Do not return final_answer,
  user_visible_answer, mode_output, answerable_now, or rewritten prose.
- Return private_transaction_ledger with one transaction per candidate card.
- Return delta_candidate_report with only bounded deltas that a separate
  deterministic composer may apply to the baseline answer.
- An accepted_delta must be concrete, public-safe, grounded in the case, and
  traceable to used card IDs and affordance IDs.
- A deferred_question is allowed when the right outcome is to block a stronger
  claim until missing evidence is supplied.
- If cards only duplicate the baseline pressure, reject/defer them and set
  no_delta_reason. Do not manufacture a delta just to use a card.
- Public delta text must not mention cards, substrate, packets, ledgers,
  affordance IDs, model IDs, mental-model names, or review machinery.
"""
C35_VARIANT_SUFFIX = """\
C3.5 public-delta gate discipline:
- Return at most two accepted_deltas.
- Every accepted_delta must include delta_type, one of:
  evidence_gate, concrete_next_move, risk_caveat, option_space_expansion.
- Prefer concrete user moves, evidence gates, risk caveats, and option-space
  expansion over analytical descriptions.
- Do not surface analytical-framework language in public text: no payoff maps,
  game trees, principal/agent diagnostics, leverage maps, branch diagrams, or
  incentive-alignment labels.
- public_delta_text must be directly useful to the user, not a description of
  the reasoning tool.
- If the useful contribution is only private reasoning pressure, reject it or
  keep it in the ledger; do not promote it to public copy.
"""
C36_VARIANT_SUFFIX = """\
C3.6 compact public-delta gate discipline:
- Return at most one public addition total across accepted_deltas,
  deferred_questions, and risk_warnings.
- Every accepted_delta must include delta_type, one of:
  evidence_gate, concrete_next_move, risk_caveat, option_space_expansion.
- Prefer evidence_gate or concrete_next_move. Use risk_caveat or
  option_space_expansion only when it directly changes the user's next move.
- Every accepted_delta must include an exact case_quote. If the case evidence is
  missing, use deferred_questions instead of accepted_deltas.
- Do not propose a public delta when the baseline answer already contains the
  same move, check, or caveat in clearer form. Set no_delta_reason instead.
- public_delta_text should be one concise, user-useful sentence. No payoff maps,
  game trees, principal/agent diagnostics, leverage maps, branch diagrams,
  incentive-alignment labels, or private review terms.
"""
C4_ONE_EDGE_SUFFIX = """\
C4 one-edge transaction discipline:
- The transaction packet is private audit material, not user-facing content.
- Do not return a formal card_transaction_ledger or private_transaction_ledger.
  Deterministic code will build the ledger from your trace.
- Return private_consideration_trace with one lightweight consideration row per
  candidate card: card_id, disposition, affordance_ids_considered, reason,
  case_quote, evidence_status, missing_evidence, and risk_if_forced when useful.
- Return one_edge_report. It may propose at most one public delta, or no delta.
- If proposing a public delta, include should_add_public_delta=true, delta_type,
  source_card_ids, affordance_ids, exact case_quote, public_delta_text,
  why_this_changes_the_decision, and confidence.
- If no public delta should be added, set should_add_public_delta=false and
  no_delta_reason. Do not manufacture a delta just to use a card.
- public_delta_text must be one concise, user-useful sentence. No payoff maps,
  game trees, principal/agent diagnostics, leverage maps, branch diagrams,
  incentive-alignment labels, card/substrate/packet/ledger/model language, or
	  private review terms.
"""
C41_CANDIDATE_EDGE_SUFFIX = """\
C4.1 candidate-edge transaction discipline:
- The transaction packet is private audit material, not user-facing content.
- Do not return a formal card_transaction_ledger or private_transaction_ledger.
  Deterministic code will build the ledger from your trace.
- Return private_consideration_trace with one lightweight consideration row per
  candidate card: card_id, disposition, affordance_ids_considered, reason,
  case_quote, evidence_status, missing_evidence, and risk_if_forced when useful.
- Return one_edge_report with best_candidate_edge always present. Do not decide
  that the baseline is merely "good enough"; identify the strongest plausible
  underweighted edge from the cards.
- best_candidate_edge must include delta_type, source_card_ids, affordance_ids,
  exact case_quote, public_delta_text, why_this_changes_the_decision,
  confidence, and admission_risk.
- Also include recommend_public_admission=true or false and admission_rationale.
  This is advisory only; deterministic code decides whether public text ships.
- public_delta_text must be one concise, user-useful sentence. No payoff maps,
  game trees, principal/agent diagnostics, leverage maps, branch diagrams,
  incentive-alignment labels, card/substrate/packet/ledger/model language, or
	  private review terms.
"""
C42_HARDENED_EDGE_SUFFIX = """\
C4.2 hardened candidate-edge discipline:
- The transaction packet is private audit material, not user-facing content.
- Do not return a formal card_transaction_ledger or private_transaction_ledger.
  Deterministic code will build the ledger from your trace.
- Return private_consideration_trace with one lightweight consideration row per
  candidate card: card_id, disposition, affordance_ids_considered, reason,
  case_quote, evidence_status, missing_evidence, and risk_if_forced when useful.
- Return one_edge_report with best_candidate_edge always present. Do not decide
  that the baseline is merely "good enough"; identify the strongest plausible
  underweighted edge from the cards.
- best_candidate_edge must include delta_type, source_card_ids, affordance_ids,
  exact case_quote, evidence_status, public_delta_text,
  why_this_changes_the_decision, confidence, and admission_risk.
- case_quote must be an exact substring from the provided case material when
  evidence_status is quoted_exact. If the edge is inferred rather than directly
  quoted, use evidence_status=inferred_from_turn and explain admission_risk.
- Also include recommend_public_admission=true or false and admission_rationale.
  This is advisory only; deterministic code decides whether public text ships.
- public_delta_text must be one concise, user-useful sentence. Prefer concrete
  moves, evidence gates, or option-preserving actions the user can actually do.
  No payoff maps, game trees, principal/agent diagnostics, leverage maps, branch
  diagrams, incentive-alignment labels, card/substrate/packet/ledger/model
  language, or private review terms.
"""

C43_CONSIDERATION_ROUTER_SUFFIX = """\
C4.3 consideration-router discipline:
- The transaction packet is private enrichment for the reasoning model, not
  user-facing content.
- Do not optimize for visible v60 uptake. Useful consideration may lead to a
  visible answer delta, a better question, a private guardrail, a deferred
  claim, or a correct rejection.
- Return private_transaction_ledger with one transaction per candidate card.
- Return consideration_usefulness_report with one assessment per candidate
  card. Judge whether the card was useful to consider, not whether it deserved
  public mention.
- Route every useful item as one of: private_reasoning, public_answer_delta,
  diagnostic_question, evidence_gate, guardrail, defer_missing_evidence,
  reject_irrelevant, reject_duplicate.
- Use opportunity roles from this closed set: frame_changer, evidence_gate,
  diagnostic_question, guardrail, tension_maker, boundary_marker,
  compression_aid, rejection_aid.
- final_answer and edge_findings are public prose. They must not mention cards,
  substrate, packet, ledger, affordance IDs, model IDs, mental-model names, or
  review machinery.
- If the packet created only private caution, final_answer may be identical in
  substance to the baseline. Explain that privately in the usefulness report;
  do not force a public delta.
"""


JUDGE_SYSTEM_PROMPT = """\
You are the blinded judge for a Lolla v60 transaction replay.

You receive two labeled outputs for the same case and product mode. The labels
are shuffled. Do not infer which output is the generic reconsideration and
which output received v60 transaction cards. Judge the user-facing value only.

Reward:
- concrete decision usefulness;
- non-obvious edge detection;
- missing-evidence discipline;
- confidence sizing;
- concise clarity.

Penalize:
- invented facts;
- overclaiming from thin evidence;
- fake sophistication or mental-model name-dropping;
- needless complexity when the case is narrow;
- generic restatement without an actionable delta.

Return only JSON. Do not include markdown.
"""


@dataclass(frozen=True)
class ReplayItem:
    case_id: str
    mode_id: str
    case_stem: str

    @property
    def item_id(self) -> str:
        return f"{self.case_stem}__{self.mode_id}"


class ReplayCallError(ReplayLabError):
    def __init__(self, message: str, *, stage: str, raw_content: str = "") -> None:
        super().__init__(message)
        self.stage = stage
        self.raw_content = raw_content


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = REPO_ROOT
    manifest_path = _resolve(root, args.case_manifest)
    affordances_path = _resolve(root, args.affordances_path)
    output_dir = _resolve(root, args.output_dir)
    if affordances_path.name != "affordances_v60.json":
        raise ReplayLabError("The paid v60 replay requires explicit affordances_v60.json")

    config = _selected_config(args.config_id)
    modes = _selected_modes(args.modes)
    manifest = _load_json(manifest_path)
    cases = _selected_cases(
        load_case_specs(manifest, root=root),
        case_ids=args.cases,
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.dry_run:
        _load_dotenv(root / ".env")
        api_key = os.getenv("LOLLA_OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ReplayLabError(
                "Missing OpenRouter API key: set LOLLA_OPENROUTER_API_KEY or OPENROUTER_API_KEY"
            )
    else:
        api_key = ""

    rows: list[dict[str, Any]] = []
    call_records: list[dict[str, Any]] = []
    item_count = 0
    for case in cases:
        case_artifact = build_case_artifact(case, root=root)
        nominations = (
            *case.explicit_nominations,
            *extract_nominations_from_result(
                case_artifact.get("result", {}),
                max_nominations=config.max_nominations,
            ),
        )
        nominations = merge_nominations(nominations)[: config.max_nominations]
        packet = build_reasoning_substrate_packet_from_files(
            root=root,
            packet_id=f"paid-{config.config_id}-{case.file_stem}",
            transaction_context={
                "case_id": case.case_id,
                "lab_version": LAB_VERSION,
                "paid_replay_version": PAID_REPLAY_VERSION,
                "config_id": config.config_id,
                "include_reason": case.include_reason,
                "risk_notes": list(case.risk_notes),
                "tags": list(case.tags),
                "dry_run": bool(args.dry_run),
            },
            nominations=list(nominations),
            affordances_path=affordances_path,
            candidate_card_target_max=config.card_cap,
            snippet_target_max_per_card=config.snippet_cap,
        )
        ledger_template = build_dry_run_ledger_template(packet)
        validate_card_transaction_ledger_payload(ledger_template, packet=packet)

        _write_json(output_dir / "cases" / f"{case.file_stem}.json", case_artifact)
        _write_json(output_dir / "packets" / f"{case.file_stem}.json", packet)
        _write_json(output_dir / "ledger_templates" / f"{case.file_stem}.json", ledger_template)

        for mode in modes:
            if args.max_items and item_count >= args.max_items:
                break
            item_count += 1
            item = ReplayItem(
                case_id=case.case_id,
                case_stem=case.file_stem,
                mode_id=mode.mode_id,
            )
            print(f"running {item.item_id}", flush=True)
            row, records = _run_item(
                item=item,
                case_artifact=case_artifact,
                packet=packet,
                mode=mode,
                config=config,
                output_dir=output_dir,
                dry_run=bool(args.dry_run),
                api_key=api_key,
                generator_model=args.generator_model,
                judge_model=args.judge_model,
                skip_judge=bool(args.skip_judge),
                c_variant=args.c_variant,
                seed=args.seed,
            )
            print(f"finished {item.item_id}: {row.get('status')}", flush=True)
            rows.append(row)
            call_records.extend(records)
        if args.max_items and item_count >= args.max_items:
            break

    summary = {
        "paid_replay_version": PAID_REPLAY_VERSION,
        "lab_version": LAB_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "dry_run": bool(args.dry_run),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_manifest": str(manifest_path),
        "affordances_path": str(affordances_path),
        "config": asdict(config),
        "case_ids": [case.case_id for case in cases],
        "mode_ids": [mode.mode_id for mode in modes],
        "generator_model": args.generator_model,
        "judge_model": "" if args.skip_judge else args.judge_model,
        "c_variant": args.c_variant,
        "paid_calls_made": bool(call_records) and not args.dry_run,
        "item_count": len(rows),
        "items": rows,
        "aggregate": _aggregate(rows, call_records),
        "call_records": call_records,
    }
    _write_json(output_dir / "summary.json", summary)
    (output_dir / "paid_replay_report.md").write_text(
        render_report(summary),
        encoding="utf-8",
    )
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'paid_replay_report.md'}")
    return 0


def _run_item(
    *,
    item: ReplayItem,
    case_artifact: Mapping[str, Any],
    packet: Mapping[str, Any],
    mode: SolutionMode,
    config: MatrixConfig,
    output_dir: Path,
    dry_run: bool,
    api_key: str,
    generator_model: str,
    judge_model: str,
    skip_judge: bool,
    c_variant: str,
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    arm_b = _arm_b_for_mode(case_artifact, mode=mode)
    arm_c = _arm_c_for_mode(
        case_artifact,
        packet,
        config=config,
        mode=mode,
        c_variant=c_variant,
    )
    prompt_dir = output_dir / "prompt_packets" / item.item_id
    _write_json(prompt_dir / "arm_b.json", arm_b)
    _write_json(prompt_dir / "arm_c.json", arm_c)

    records: list[dict[str, Any]] = []
    item_status = "ok"
    item_error: dict[str, Any] = {}
    arm_c_raw_output: dict[str, Any] | None = None
    if dry_run:
        arm_b_output = _dry_run_output(item=item, arm="B", prompt=arm_b)
        arm_c_output = _dry_run_output(item=item, arm="C", prompt=arm_c)
        judge_output = _dry_run_judge(item=item)
    else:
        try:
            arm_b_output, b_meta = call_openrouter_json(
                api_key=api_key,
                model=generator_model,
                system_prompt=_text(arm_b.get("system_prompt")),
                user_packet=_mapping(arm_b.get("user_packet")),
                stage=f"{item.item_id}:arm_b",
            )
            records.append({"item_id": item.item_id, "arm": "B", **b_meta})
        except ReplayCallError as exc:
            arm_b_output = _error_output(exc)
            arm_c_output = {"status": "skipped_due_to_arm_b_error"}
            judge_output = {"status": "skipped_due_to_arm_b_error"}
            item_status = "error"
            item_error = _error_summary(exc)
        else:
            try:
                arm_c_output, c_meta = call_openrouter_json(
                    api_key=api_key,
                    model=generator_model,
                    system_prompt=_text(arm_c.get("system_prompt")),
                    user_packet=_mapping(arm_c.get("user_packet")),
                    stage=f"{item.item_id}:arm_c",
                )
                records.append({"item_id": item.item_id, "arm": "C", **c_meta})
                arm_c_raw_output = arm_c_output
                if c_variant in DELTA_VARIANTS:
                    public_delta_gate_policy = PUBLIC_DELTA_GATE_POLICY_BY_VARIANT.get(
                        c_variant, ""
                    )
                    arm_c_output = compose_delta_audit_output(
                        arm_b_output=arm_b_output,
                        delta_output=arm_c_raw_output,
                        mode=mode,
                        public_delta_gate=bool(public_delta_gate_policy),
                        public_delta_gate_policy=public_delta_gate_policy,
                        case_evidence_text=_case_evidence_text(case_artifact),
                    )
                elif c_variant in ONE_EDGE_VARIANTS:
                    public_delta_gate_policy = PUBLIC_DELTA_GATE_POLICY_BY_VARIANT.get(
                        c_variant, "c4_one_edge"
                    )
                    arm_c_output = compose_one_edge_output(
                        arm_b_output=arm_b_output,
                        one_edge_output=arm_c_raw_output,
                        packet=packet,
                        mode=mode,
                        public_delta_gate_policy=public_delta_gate_policy,
                        case_evidence_text=_case_evidence_text(case_artifact),
                    )
            except ReplayCallError as exc:
                arm_c_output = _error_output(exc)
                judge_output = {"status": "skipped_due_to_arm_c_error"}
                item_status = "error"
                item_error = _error_summary(exc)
            else:
                if skip_judge:
                    judge_output = {"status": "skipped"}
                else:
                    judge_packet, blind_map = build_judge_packet(
                        item=item,
                        mode=mode,
                        case_artifact=case_artifact,
                        arm_b_output=arm_b_output,
                        arm_c_output=arm_c_output,
                        seed=seed,
                    )
                    _write_json(prompt_dir / "judge.json", judge_packet)
                    if judge_packet_outputs_are_identical(judge_packet):
                        judge_output = deterministic_identical_judge_output(
                            blind_map=blind_map
                        )
                    else:
                        try:
                            judge_payload, judge_meta = call_openrouter_json(
                                api_key=api_key,
                                model=judge_model,
                                system_prompt=JUDGE_SYSTEM_PROMPT,
                                user_packet=judge_packet,
                                stage=f"{item.item_id}:judge",
                            )
                        except ReplayCallError as exc:
                            judge_output = _error_output(exc)
                            item_status = "judge_error"
                            item_error = _error_summary(exc)
                        else:
                            records.append({"item_id": item.item_id, "arm": "judge", **judge_meta})
                            judge_output = normalize_judge_output(judge_payload, blind_map=blind_map)

    output_item_dir = output_dir / "outputs" / item.item_id
    _write_json(output_item_dir / "arm_b.json", arm_b_output)
    _write_json(output_item_dir / "arm_c.json", arm_c_output)
    if arm_c_raw_output is not None and c_variant in DELTA_VARIANTS:
        _write_json(output_item_dir / "arm_c_delta_raw.json", arm_c_raw_output)
    if arm_c_raw_output is not None and c_variant in ONE_EDGE_VARIANTS:
        _write_json(output_item_dir / "arm_c_one_edge_raw.json", arm_c_raw_output)
    if arm_c_raw_output is not None and c_variant in CONSIDERATION_ROUTER_VARIANTS:
        _write_json(output_item_dir / "arm_c_consideration_raw.json", arm_c_raw_output)
    _write_json(output_item_dir / "judge.json", judge_output)

    ledger_validation = (
        {"status": "not_run_dry_run"}
        if dry_run
        else validate_arm_c_ledger_output(arm_c_output, packet=packet)
    )
    delta_validation = (
        {"status": "not_applicable"}
        if c_variant not in COMPOSED_AUDIT_VARIANTS
        else (
            {"status": "not_run_dry_run"}
            if dry_run
            else validate_one_edge_report_output(
                arm_c_output,
                packet=packet,
                case_evidence_text=_case_evidence_text(case_artifact),
                require_exact_case_quote=c_variant in CANDIDATE_EDGE_HARDENED_VARIANTS,
                public_delta_gate_policy=PUBLIC_DELTA_GATE_POLICY_BY_VARIANT.get(
                    c_variant, ""
                ),
            )
            if c_variant in ONE_EDGE_VARIANTS
            else validate_delta_candidate_report_output(
                arm_c_output,
                packet=packet,
                require_public_delta_gate=c_variant in GATED_DELTA_VARIANTS,
                require_compact_public_gate=c_variant == "delta_compact",
            )
        )
    )
    consideration_validation = (
        {"status": "not_applicable"}
        if c_variant not in CONSIDERATION_ROUTER_VARIANTS
        else (
            {"status": "not_run_dry_run"}
            if dry_run
            else validate_consideration_usefulness_output(
                arm_c_output,
                packet=packet,
            )
        )
    )
    packet_quality = packet_quality_counts(packet)
    output_paths = {
        "arm_b": f"outputs/{item.item_id}/arm_b.json",
        "arm_c": f"outputs/{item.item_id}/arm_c.json",
        "judge": f"outputs/{item.item_id}/judge.json",
    }
    if arm_c_raw_output is not None and c_variant in DELTA_VARIANTS:
        output_paths["arm_c_delta_raw"] = f"outputs/{item.item_id}/arm_c_delta_raw.json"
    if arm_c_raw_output is not None and c_variant in ONE_EDGE_VARIANTS:
        output_paths["arm_c_one_edge_raw"] = f"outputs/{item.item_id}/arm_c_one_edge_raw.json"
    if arm_c_raw_output is not None and c_variant in CONSIDERATION_ROUTER_VARIANTS:
        output_paths["arm_c_consideration_raw"] = (
            f"outputs/{item.item_id}/arm_c_consideration_raw.json"
        )
    row = {
        "status": item_status,
        "item_id": item.item_id,
        "case_id": item.case_id,
        "mode_id": item.mode_id,
        "c_variant": c_variant,
        "candidate_model_ids": [
            _text(card.get("model_id"))
            for card in (_mapping(raw) for raw in _list(packet.get("candidate_cards")))
        ],
        "suppressed_candidate_count": len(_list(packet.get("suppressed_candidates"))),
        "packet_quality_counts": packet_quality,
        "token_estimates": {
            "arm_b_prompt": estimate_tokens(arm_b),
            "arm_c_prompt": estimate_tokens(arm_c),
            "arm_c_packet_view": estimate_tokens(
                _mapping(_mapping(arm_c.get("user_packet")).get("reasoning_substrate_packet"))
            ),
        },
        "ledger_validation": ledger_validation,
        "delta_validation": delta_validation,
        "consideration_validation": consideration_validation,
        "judge": judge_output,
        "error": item_error,
        "output_paths": output_paths,
    }
    c3_composition = _mapping(_mapping(arm_c_output).get("c3_composition"))
    if c3_composition:
        row["c3_composition"] = c3_composition
    return row, records


def _arm_b_for_mode(case_artifact: Mapping[str, Any], *, mode: SolutionMode) -> dict[str, Any]:
    arm = build_arm_b(case_artifact)
    arm["solution_mode"] = mode.mode_id
    arm["role"] = mode.role
    arm["system_prompt"] = f"{_text(arm.get('system_prompt')).rstrip()}\n\n{mode.system_suffix}\n"
    arm["system_prompt"] += f"\n{OUTPUT_DISCIPLINE_SUFFIX}"
    arm["user_packet"]["output_contract"] = {
        **_mapping(arm["user_packet"].get("output_contract")),
        **mode.output_contract,
    }
    return arm


def _arm_c_for_mode(
    case_artifact: Mapping[str, Any],
    packet: Mapping[str, Any],
    *,
    config: MatrixConfig,
    mode: SolutionMode,
    c_variant: str = DEFAULT_C_VARIANT,
) -> dict[str, Any]:
    arm = build_arm_c(
        case_artifact,
        packet,
        decoder_snippet_cap=config.decoder_snippet_cap,
    )
    arm["solution_mode"] = mode.mode_id
    arm["role"] = mode.role
    arm["system_prompt"] = (
        f"{V60_TRANSACTION_SYSTEM_PROMPT.rstrip()}\n\n{mode.system_suffix}\n"
    )
    arm["system_prompt"] += f"\n{OUTPUT_DISCIPLINE_SUFFIX}"
    if c_variant not in ONE_EDGE_VARIANTS:
        arm["system_prompt"] += f"\n{LEDGER_DISCIPLINE_SUFFIX}"
    ledger_schema = {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": _text(packet.get("packet_id")),
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "card_transactions": [
            {
                "card_id": "must match one candidate card",
                "model_id": "must match packet card",
                "disposition": "used | rejected | deferred",
                "effect_type": (
                    "direct_answer_delta | diagnostic_question | guardrail | "
                    "counterframe | speculative_probe | no_effect"
                ),
                "affordance_ids_considered": [
                    "only affordance IDs present on that card"
                ],
                "merged_with_card_ids": ["optional packet card IDs"],
                "strongest_plausible_application": "required for rejected/deferred",
                "grounding_check": {
                    "case_quote": "exact case substring or empty",
                    "evidence_status": (
                        "quoted_exact | inferred_from_turn | missing | "
                        "conflicting | not_needed"
                    ),
                    "missing_evidence": ["required when deferred and evidence is missing"],
                },
                "decision_reason": "why this disposition is right",
                "rejection_ground": (
                    "missing_case_evidence | wrong_object | guardrail_triggered | "
                    "stronger_competing_structure | scope_mismatch | "
                    "user_facing_risk | duplicate_of_existing_pressure | "
                    "low_source_support"
                ),
                "risk_if_forced": "required for rejected",
                "residue": "what remains worth asking or watching",
                "final_answer_delta": "required when used",
                "final_answer_visibility": (
                    "silent_application | visible_question | visible_caveat | "
                    "visible_reframe | not_visible"
                ),
            },
        ],
        "summary": {
            "used_count": "integer",
            "rejected_count": "integer",
            "deferred_count": "integer",
            "visible_delta_count": "integer",
            "silent_delta_count": "integer",
            "no_effect_count": "integer",
        },
    }
    if c_variant in ONE_EDGE_VARIANTS:
        if c_variant in CANDIDATE_EDGE_VARIANTS:
            if c_variant in CANDIDATE_EDGE_HARDENED_VARIANTS:
                arm["system_prompt"] += f"\n{C42_HARDENED_EDGE_SUFFIX}"
            else:
                arm["system_prompt"] += f"\n{C41_CANDIDATE_EDGE_SUFFIX}"
        else:
            arm["system_prompt"] += f"\n{C4_ONE_EDGE_SUFFIX}"
        arm["user_packet"]["output_contract"] = {
            "private_consideration_trace": [
                {
                    "card_id": "must match one candidate card",
                    "disposition": "used | rejected | deferred",
                    "affordance_ids_considered": [
                        "only affordance IDs present on that card"
                    ],
                    "reason": "short private reason for the disposition",
                    "case_quote": "exact case substring or empty",
                    "evidence_status": (
                        "quoted_exact | inferred_from_turn | missing | "
                        "conflicting | not_needed"
                    ),
                    "missing_evidence": ["specific missing evidence when deferred"],
                    "risk_if_forced": "why public use would be risky when rejected",
                }
            ],
            "one_edge_report": (
                {
                    "best_candidate_edge": {
                        "delta_type": (
                            "evidence_gate | concrete_next_move | risk_caveat | "
                            "option_space_expansion"
                        ),
                        "source_card_ids": ["packet card IDs supporting the best edge"],
                        "affordance_ids": [
                            "affordance IDs considered for the best edge"
                        ],
                        "case_quote": "exact case substring required",
                        "evidence_status": (
                            "quoted_exact | inferred_from_turn; quoted_exact "
                            "must use an exact case substring"
                        ),
                        "public_delta_text": (
                            "one concise public-safe sentence the composer may add"
                        ),
                        "why_this_changes_the_decision": "decision consequence",
                        "confidence": "low | medium | high",
                        "admission_risk": (
                            "why this edge may still be duplicate, unsupported, or noisy"
                        ),
                    },
                    "recommend_public_admission": "true | false",
                    "admission_rationale": "short private rationale for recommendation",
                }
                if c_variant in CANDIDATE_EDGE_VARIANTS
                else {
                    "should_add_public_delta": "true | false",
                    "delta_type": (
                        "evidence_gate | concrete_next_move | risk_caveat | "
                        "option_space_expansion; required if true"
                    ),
                    "source_card_ids": ["packet card IDs supporting the one edge"],
                    "affordance_ids": ["affordance IDs considered for the one edge"],
                    "case_quote": "exact case substring required if true",
                    "public_delta_text": (
                        "one concise public-safe sentence the composer may add"
                    ),
                    "why_this_changes_the_decision": "decision consequence",
                    "confidence": "low | medium | high",
                    "no_delta_reason": "required if should_add_public_delta=false",
                }
            ),
        }
    elif c_variant in DELTA_VARIANTS:
        arm["system_prompt"] += f"\n{DELTA_VARIANT_SUFFIX}"
        if c_variant == "delta_gated":
            arm["system_prompt"] += f"\n{C35_VARIANT_SUFFIX}"
        elif c_variant == "delta_compact":
            arm["system_prompt"] += f"\n{C36_VARIANT_SUFFIX}"
        arm["user_packet"]["output_contract"] = {
            "private_transaction_ledger": (
                "required; one transaction per candidate card; never user-facing"
            ),
            "delta_candidate_report": {
                "accepted_deltas": [
                    {
                        "delta_id": "stable short ID",
                        "delta_type": (
                            "evidence_gate | concrete_next_move | risk_caveat | "
                            "option_space_expansion"
                        ),
                        "source_card_ids": ["packet card IDs with used disposition"],
                        "affordance_ids": ["affordance IDs considered for the delta"],
                        "public_delta_text": (
                            "concise public-safe delta the composer may add"
                        ),
                        "public_edge_text": (
                            "optional edge-audit wording; no private machinery"
                        ),
                        "evidence_status": (
                            "quoted_exact | inferred_from_turn | missing | "
                            "conflicting | not_needed"
                        ),
                        "case_quote": "exact case substring or empty",
                        "why_user_should_care": "decision consequence",
                        "confidence": "low | medium | high",
                    }
                ],
                "deferred_questions": [
                    {
                        "source_card_ids": ["packet card IDs"],
                        "question": "private wording of missing evidence question",
                        "public_question_text": "public-safe question or gate",
                        "missing_evidence": ["specific missing evidence"],
                        "why_it_blocks_claim": "claim this evidence should block",
                    }
                ],
                "risk_warnings": [
                    {
                        "source_card_ids": ["packet card IDs"],
                        "public_warning_text": "public-safe risk warning",
                        "severity": "low | medium | high",
                    }
                ],
                "rejected_cards": [
                    {
                        "card_id": "packet card ID",
                        "reason": "why it created no public delta",
                    }
                ],
                "no_delta_reason": "required when accepted_deltas is empty",
            },
            "card_transaction_ledger_schema": ledger_schema,
        }
    elif c_variant == "hidden":
        arm["system_prompt"] += f"\n{HIDDEN_VARIANT_SUFFIX}"
        arm["user_packet"]["output_contract"] = {
            "final_answer": "same public prose as user_visible_answer",
            "edge_findings": "same public list as user_visible_edges",
            "rewrite_required": "yes / no / only small caveat",
            "risk_register": [
                "invented fact risk",
                "overclaim risk",
                "model theater risk",
            ],
            "private_transaction_ledger": (
                "required; one transaction per candidate card; never user-facing"
            ),
            "private_delta_notes": {
                "changed": ["public deltas caused by the private card review"],
                "not_changed": ["pressures considered but not adopted"],
                "why_no_visible_delta": (
                    "required if the private review does not alter the public answer"
                ),
            },
            "user_visible_answer": (
                "concise public answer; no card/substrate/ledger/model language"
            ),
            "user_visible_edges": [
                "public non-obvious edges only; no card/substrate/ledger/model language"
            ],
            "card_transaction_ledger_schema": ledger_schema,
        }
    elif c_variant in CONSIDERATION_ROUTER_VARIANTS:
        arm["system_prompt"] += f"\n{C43_CONSIDERATION_ROUTER_SUFFIX}"
        arm["user_packet"]["output_contract"] = {
            "final_answer": (
                "public prose for the user; may preserve the baseline when "
                "v60 only created private caution"
            ),
            "edge_findings": [
                "public non-obvious edges only; omit if v60 was useful only privately"
            ],
            "rewrite_required": "yes | no | only small caveat",
            "reasoning_delta_summary": [
                "what changed from the baseline",
                "what v60 helped reject, defer, or keep private",
            ],
            "risk_register": [
                "invented fact risk",
                "overclaim risk",
                "model theater risk",
            ],
            "private_transaction_ledger": (
                "required; one transaction per candidate card; never user-facing"
            ),
            "consideration_usefulness_report": {
                "packet_usefulness": (
                    "useful | mixed | not_useful | overfed | underfed"
                ),
                "chunk_assessments": [
                    {
                        "card_id": "must match one candidate card",
                        "model_id": "must match packet card",
                        "usefulness_to_consider": "high | medium | low | none",
                        "opportunity_role": (
                            "frame_changer | evidence_gate | diagnostic_question | "
                            "guardrail | tension_maker | boundary_marker | "
                            "compression_aid | rejection_aid"
                        ),
                        "route": (
                            "private_reasoning | public_answer_delta | "
                            "diagnostic_question | evidence_gate | guardrail | "
                            "defer_missing_evidence | reject_irrelevant | "
                            "reject_duplicate"
                        ),
                        "affordance_ids_considered": [
                            "only affordance IDs present on that card"
                        ],
                        "what_it_helped_notice": "private reasoning effect or empty",
                        "why_not_used_publicly": (
                            "required when route is private/reject/defer"
                        ),
                        "evidence_status": (
                            "quoted_exact | inferred_from_turn | missing | "
                            "conflicting | not_needed"
                        ),
                    }
                ],
                "selected_opportunities": [
                    {
                        "opportunity_id": "stable short ID",
                        "route": (
                            "public_answer_delta | diagnostic_question | "
                            "evidence_gate | guardrail | private_reasoning"
                        ),
                        "source_card_ids": ["packet card IDs"],
                        "public_surface": (
                            "empty when private_only; otherwise public-safe wording"
                        ),
                        "private_value": (
                            "why this was worth considering even if not public"
                        ),
                    }
                ],
                "retrieval_feedback": [
                    "what would have made the selected packet more useful"
                ],
                "no_public_delta_reason": (
                    "required when final answer does not materially change"
                ),
            },
            "card_transaction_ledger_schema": ledger_schema,
        }
    else:
        arm["user_packet"]["output_contract"] = {
            **_mapping(arm["user_packet"].get("output_contract")),
            **mode.output_contract,
            "card_transaction_ledger_schema": ledger_schema,
        }
    return arm


def build_judge_packet(
    *,
    item: ReplayItem,
    mode: SolutionMode,
    case_artifact: Mapping[str, Any],
    arm_b_output: Mapping[str, Any],
    arm_c_output: Mapping[str, Any],
    seed: int,
) -> tuple[dict[str, Any], dict[str, str]]:
    labels = ["A", "B"]
    actual = ["B", "C"]
    rng = random.Random(f"{seed}:{item.case_id}:{item.mode_id}")
    rng.shuffle(actual)
    blind_map = dict(zip(labels, actual))
    actual_outputs = {
        "B": sanitize_output_for_judge(arm_b_output),
        "C": sanitize_output_for_judge(arm_c_output),
    }
    packet = {
        "paid_replay_version": PAID_REPLAY_VERSION,
        "case_id": item.case_id,
        "mode_id": item.mode_id,
        "mode_role": mode.role,
        "query": _text(case_artifact.get("query")),
        "conversation_excerpt": _text(case_artifact.get("conversation_excerpt"))[:8000],
        "vanilla_answer": _text(case_artifact.get("vanilla_answer"))[:6000],
        "evaluation_focus": [
            "Which output gives the user a more useful decision delta?",
            "Which output surfaces a non-obvious but grounded edge?",
            "Which output handles missing evidence more responsibly?",
            "Which output avoids needless complexity and model theater?",
        ],
        "output_labels": [
            {"label": label, "output": actual_outputs[actual_arm]}
            for label, actual_arm in blind_map.items()
        ],
        "return_schema": {
            "winner_label": "A | B | tie | both_bad",
            "constructive_edge_label": "A | B | tie | neither",
            "missing_evidence_discipline_label": "A | B | tie | neither",
            "overburdened_label": "A | B | neither | both",
            "model_theater_label": "A | B | neither | both",
            "scores": {
                "A": {
                    "decision_usefulness": "1-5 integer",
                    "evidence_discipline": "1-5 integer",
                    "non_obvious_edge": "1-5 integer",
                    "clarity": "1-5 integer",
                    "rationale": "string",
                },
                "B": {
                    "decision_usefulness": "1-5 integer",
                    "evidence_discipline": "1-5 integer",
                    "non_obvious_edge": "1-5 integer",
                    "clarity": "1-5 integer",
                    "rationale": "string",
                },
            },
            "best_user_visible_delta": "string",
            "main_failure_mode": "string",
            "promotion_read": "promote | retest | reject",
            "rationale": "string",
        },
    }
    return packet, blind_map


def judge_packet_outputs_are_identical(packet: Mapping[str, Any]) -> bool:
    outputs = [_mapping(item).get("output") for item in _list(packet.get("output_labels"))]
    return len(outputs) == 2 and outputs[0] == outputs[1]


def deterministic_identical_judge_output(*, blind_map: Mapping[str, str]) -> dict[str, Any]:
    payload = {
        "winner_label": "tie",
        "constructive_edge_label": "tie",
        "missing_evidence_discipline_label": "tie",
        "overburdened_label": "neither",
        "model_theater_label": "neither",
        "promotion_read": "retest",
        "best_user_visible_delta": "None; public outputs are identical after sanitization.",
        "main_failure_mode": "no_user_visible_delta",
        "rationale": (
            "The two public outputs are identical after removing private audit "
            "material, so the replay must be treated as a deterministic tie."
        ),
        "scores": {},
        "status": "deterministic_identical_output_tie",
    }
    return normalize_judge_output(payload, blind_map=blind_map)


def sanitize_output_for_judge(payload: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = dict(payload)
    if _text(sanitized.get("user_visible_answer")) and not _text(sanitized.get("final_answer")):
        sanitized["final_answer"] = _text(sanitized.get("user_visible_answer"))
    if _list(sanitized.get("user_visible_edges")) and not _list(sanitized.get("edge_findings")):
        sanitized["edge_findings"] = _list(sanitized.get("user_visible_edges"))
    sanitized.pop("card_transaction_ledger", None)
    sanitized.pop("private_transaction_ledger", None)
    sanitized.pop("private_delta_notes", None)
    sanitized.pop("delta_candidate_report", None)
    sanitized.pop("one_edge_report", None)
    sanitized.pop("consideration_usefulness_report", None)
    sanitized.pop("private_consideration_trace", None)
    sanitized.pop("c3_composition", None)
    sanitized.pop("private_delta_audit", None)
    sanitized.pop("card_transactions", None)
    sanitized.pop("ledger_version", None)
    sanitized.pop("packet_id", None)
    sanitized.pop("user_visible_answer", None)
    sanitized.pop("user_visible_edges", None)
    return sanitized


def compose_delta_audit_output(
    *,
    arm_b_output: Mapping[str, Any],
    delta_output: Mapping[str, Any],
    mode: SolutionMode,
    public_delta_gate: bool = False,
    public_delta_gate_policy: str = "",
    case_evidence_text: str = "",
) -> dict[str, Any]:
    """Compose public Arm C from Arm B plus accepted C3 deltas.

    The C3 model is deliberately not trusted to rewrite the final answer. It can
    only provide bounded public-safe deltas; this deterministic composer decides
    how those deltas become the judged public surface.
    """

    base_public = sanitize_output_for_judge(arm_b_output)
    report = _mapping(delta_output.get("delta_candidate_report"))
    accepted = [_mapping(item) for item in _list(report.get("accepted_deltas"))]
    deferred = [_mapping(item) for item in _list(report.get("deferred_questions"))]
    warnings = [_mapping(item) for item in _list(report.get("risk_warnings"))]
    gate_policy = _public_delta_gate_policy(
        public_delta_gate=public_delta_gate,
        public_delta_gate_policy=public_delta_gate_policy,
    )
    gate_result = gate_public_delta_report(
        accepted=accepted,
        deferred=deferred,
        warnings=warnings,
        base_public=base_public,
        enabled=bool(gate_policy),
        policy=gate_policy,
        case_evidence_text=case_evidence_text,
    )
    public_accepted = gate_result["accepted"]
    public_deferred = gate_result["deferred"]
    public_warnings = gate_result["warnings"]

    accepted_items = _accepted_delta_public_items(public_accepted)
    deferred_items = _deferred_question_public_items(public_deferred)
    warning_items = _risk_warning_public_items(public_warnings)
    accepted_texts = _dedupe_texts(_public_item_to_text(item) for item in accepted_items)
    deferred_texts = _dedupe_texts(_public_item_to_text(item) for item in deferred_items)
    warning_texts = _dedupe_texts(_public_item_to_text(item) for item in warning_items)

    composed = dict(base_public)
    base_final = (
        _text(base_public.get("final_answer"))
        or _text(base_public.get("mode_output"))
        or _text(base_public.get("answer"))
    )
    if base_final:
        composed["final_answer"] = base_final

    existing_edges = _public_items(base_public.get("edge_findings"))
    if mode.mode_id == "edge_audit":
        composed_edges = _dedupe_public_items(
            [*existing_edges, *accepted_items, *deferred_items, *warning_items]
        )
        if composed_edges:
            composed["edge_findings"] = composed_edges
    elif accepted_texts:
        addition = "\n".join(f"- {text}" for text in accepted_texts)
        composed["final_answer"] = f"{base_final}\n\nAdditional decision deltas:\n{addition}".strip()

    if deferred_texts:
        composed["gated_questions"] = _dedupe_texts(
            [*_public_text_list(base_public.get("gated_questions")), *deferred_texts]
        )
    if warning_texts:
        composed["risk_register"] = _dedupe_texts(
            [*_public_text_list(base_public.get("risk_register")), *warning_texts]
        )
    if accepted_texts or deferred_texts or warning_texts:
        composed["rewrite_required"] = "only small caveat"
    elif _text(base_public.get("rewrite_required")):
        composed["rewrite_required"] = _text(base_public.get("rewrite_required"))

    composed["private_transaction_ledger"] = _mapping(
        delta_output.get("private_transaction_ledger")
    )
    composed["delta_candidate_report"] = report
    composed["c3_composition"] = {
        "composition_version": "c3_delta_only_composer.v1",
        "mode_id": mode.mode_id,
        "baseline_preserved": True,
        "public_delta_gate": bool(gate_policy),
        "public_delta_gate_policy": gate_policy,
        "public_delta_gate_version": PUBLIC_DELTA_GATE_VERSION_BY_POLICY.get(
            gate_policy, ""
        ),
        "accepted_delta_count": len(accepted_items),
        "deferred_question_count": len(deferred_items),
        "risk_warning_count": len(warning_items),
        "raw_accepted_delta_count": len(accepted),
        "raw_deferred_question_count": len(deferred),
        "raw_risk_warning_count": len(warnings),
        "dropped_public_delta_count": len(gate_result["dropped"]),
        "dropped_public_deltas": gate_result["dropped"],
        "no_delta_collapse_to_b": not bool(accepted_items or deferred_items or warning_items),
    }
    return composed


def compose_one_edge_output(
    *,
    arm_b_output: Mapping[str, Any],
    one_edge_output: Mapping[str, Any],
    packet: Mapping[str, Any],
    mode: SolutionMode,
    public_delta_gate_policy: str = "c4_one_edge",
    case_evidence_text: str = "",
) -> dict[str, Any]:
    """Compose public Arm C from a C4 one-edge report.

    C4 deliberately asks the model for judgment and trace, not ledger
    bookkeeping. This composer converts the one-edge report into the existing
    public-delta path, then builds a deterministic card transaction ledger from
    the lightweight consideration trace.
    """

    report = _mapping(one_edge_output.get("one_edge_report"))
    trace = [_mapping(item) for item in _list(one_edge_output.get("private_consideration_trace"))]
    delta = _one_edge_report_to_delta(report)
    synthetic_delta_output = {
        "private_transaction_ledger": {},
        "delta_candidate_report": {
            "accepted_deltas": [delta] if delta else [],
            "deferred_questions": [],
            "risk_warnings": [],
            "rejected_cards": [],
            "no_delta_reason": _text(report.get("no_delta_reason")) if not delta else "",
        },
    }
    composed = compose_delta_audit_output(
        arm_b_output=arm_b_output,
        delta_output=synthetic_delta_output,
        mode=mode,
        public_delta_gate=True,
        public_delta_gate_policy=public_delta_gate_policy,
        case_evidence_text=case_evidence_text,
    )
    drop_reason = ""
    dropped = [_mapping(item) for item in _list(_mapping(composed.get("c3_composition")).get("dropped_public_deltas"))]
    if dropped:
        drop_reason = _text(dropped[0].get("reason"))
    admitted_delta = delta if _mapping(composed.get("c3_composition")).get("accepted_delta_count") else {}
    composed["private_transaction_ledger"] = build_one_edge_transaction_ledger(
        packet=packet,
        consideration_trace=trace,
        one_edge_report=report,
        admitted_delta=admitted_delta,
        drop_reason=drop_reason,
    )
    composed["private_consideration_trace"] = trace
    composed["one_edge_report"] = report
    composition = _mapping(composed.get("c3_composition"))
    if composition:
        updated_composition = dict(composition)
        if public_delta_gate_policy == "c4_2_hardened_edge":
            composition_version = "c4_2_hardened_edge_composer.v1"
        elif public_delta_gate_policy == "c4_1_candidate_edge":
            composition_version = "c4_1_candidate_edge_composer.v1"
        else:
            composition_version = "c4_one_edge_composer.v1"
        updated_composition["composition_version"] = composition_version
        updated_composition["raw_accepted_delta_count"] = 1 if delta else 0
        updated_composition["one_edge_report_present"] = bool(report)
        if public_delta_gate_policy in {"c4_1_candidate_edge", "c4_2_hardened_edge"}:
            updated_composition["best_candidate_edge_present"] = bool(
                _mapping(report.get("best_candidate_edge"))
            )
            updated_composition["model_recommend_public_admission"] = _boolish(
                report.get("recommend_public_admission")
            )
        composed["c3_composition"] = updated_composition
    return composed


def gate_public_delta_report(
    *,
    accepted: list[Mapping[str, Any]],
    deferred: list[Mapping[str, Any]],
    warnings: list[Mapping[str, Any]],
    base_public: Mapping[str, Any],
    enabled: bool,
    policy: str = "",
    case_evidence_text: str = "",
) -> dict[str, Any]:
    if not enabled:
        return {
            "accepted": accepted,
            "deferred": deferred,
            "warnings": warnings,
            "dropped": [],
        }

    gate_policy = policy or "c3_5"
    if gate_policy in {
        "c3_6_compact",
        "c4_one_edge",
        "c4_1_candidate_edge",
        "c4_2_hardened_edge",
    }:
        return _gate_compact_public_delta_report(
            accepted=accepted,
            deferred=deferred,
            warnings=warnings,
            base_public=base_public,
            policy=gate_policy,
            case_evidence_text=case_evidence_text,
        )

    remaining_slots = PUBLIC_DELTA_GATE_MAX_BY_POLICY.get(gate_policy, PUBLIC_DELTA_GATE_MAX)
    kept_accepted: list[Mapping[str, Any]] = []
    kept_deferred: list[Mapping[str, Any]] = []
    kept_warnings: list[Mapping[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    baseline_text = _baseline_public_text(base_public)

    for index, delta in enumerate(accepted):
        reason = _public_delta_drop_reason(
            delta,
            baseline_text=baseline_text,
            policy=gate_policy,
            case_evidence_text=case_evidence_text,
        )
        if reason:
            dropped.append(
                {
                    "kind": "accepted_delta",
                    "index": index,
                    "delta_id": _text(delta.get("delta_id")),
                    "reason": reason,
                }
            )
            continue
        if remaining_slots <= 0:
            dropped.append(
                {
                    "kind": "accepted_delta",
                    "index": index,
                    "delta_id": _text(delta.get("delta_id")),
                    "reason": "public_delta_cap_exceeded",
                }
            )
            continue
        kept_accepted.append(delta)
        remaining_slots -= 1

    for index, question in enumerate(deferred):
        reason = _deferred_question_drop_reason(question, baseline_text=baseline_text)
        if reason:
            dropped.append(
                {
                    "kind": "deferred_question",
                    "index": index,
                    "reason": reason,
                }
            )
            continue
        if remaining_slots <= 0:
            dropped.append(
                {
                    "kind": "deferred_question",
                    "index": index,
                    "reason": "public_delta_cap_exceeded",
                }
            )
            continue
        kept_deferred.append(question)
        remaining_slots -= 1

    for index, warning in enumerate(warnings):
        reason = _risk_warning_drop_reason(warning, baseline_text=baseline_text)
        if reason:
            dropped.append(
                {
                    "kind": "risk_warning",
                    "index": index,
                    "reason": reason,
                }
            )
            continue
        if remaining_slots <= 0:
            dropped.append(
                {
                    "kind": "risk_warning",
                    "index": index,
                    "reason": "public_delta_cap_exceeded",
                }
            )
            continue
        kept_warnings.append(warning)
        remaining_slots -= 1

    return {
        "accepted": kept_accepted,
        "deferred": kept_deferred,
        "warnings": kept_warnings,
        "dropped": dropped,
    }


def _gate_compact_public_delta_report(
    *,
    accepted: list[Mapping[str, Any]],
    deferred: list[Mapping[str, Any]],
    warnings: list[Mapping[str, Any]],
    base_public: Mapping[str, Any],
    policy: str = "c3_6_compact",
    case_evidence_text: str = "",
) -> dict[str, Any]:
    kept_accepted: list[Mapping[str, Any]] = []
    kept_deferred: list[Mapping[str, Any]] = []
    kept_warnings: list[Mapping[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    baseline_text = _baseline_public_text(base_public)

    for index, delta in enumerate(accepted):
        reason = _public_delta_drop_reason(
            delta,
            baseline_text=baseline_text,
            policy=policy,
            case_evidence_text=case_evidence_text,
        )
        if reason:
            dropped.append(
                {
                    "kind": "accepted_delta",
                    "index": index,
                    "delta_id": _text(delta.get("delta_id")),
                    "reason": reason,
                }
            )
            continue
        candidates.append(
            {
                "kind": "accepted_delta",
                "index": index,
                "delta_id": _text(delta.get("delta_id")),
                "priority": PUBLIC_DELTA_TYPE_PRIORITY.get(
                    _text(delta.get("delta_type")),
                    99,
                ),
                "payload": delta,
            }
        )

    for index, question in enumerate(deferred):
        reason = _deferred_question_drop_reason(question, baseline_text=baseline_text)
        if reason:
            dropped.append(
                {
                    "kind": "deferred_question",
                    "index": index,
                    "reason": reason,
                }
            )
            continue
        candidates.append(
            {
                "kind": "deferred_question",
                "index": index,
                "priority": 0,
                "payload": question,
            }
        )

    for index, warning in enumerate(warnings):
        reason = _risk_warning_drop_reason(warning, baseline_text=baseline_text)
        if reason:
            dropped.append(
                {
                    "kind": "risk_warning",
                    "index": index,
                    "reason": reason,
                }
            )
            continue
        candidates.append(
            {
                "kind": "risk_warning",
                "index": index,
                "priority": 2,
                "payload": warning,
            }
        )

    candidates.sort(key=lambda item: (_int(item.get("priority")), _int(item.get("index"))))
    selected = candidates[:1]
    for candidate in selected:
        kind = _text(candidate.get("kind"))
        payload = _mapping(candidate.get("payload"))
        if kind == "accepted_delta":
            kept_accepted.append(payload)
        elif kind == "deferred_question":
            kept_deferred.append(payload)
        elif kind == "risk_warning":
            kept_warnings.append(payload)

    for candidate in candidates[1:]:
        item = {
            "kind": _text(candidate.get("kind")),
            "index": _int(candidate.get("index")),
            "reason": "public_delta_cap_exceeded",
        }
        if _text(candidate.get("delta_id")):
            item["delta_id"] = _text(candidate.get("delta_id"))
        dropped.append(item)

    return {
        "accepted": kept_accepted,
        "deferred": kept_deferred,
        "warnings": kept_warnings,
        "dropped": dropped,
    }


def build_one_edge_transaction_ledger(
    *,
    packet: Mapping[str, Any],
    consideration_trace: list[Mapping[str, Any]],
    one_edge_report: Mapping[str, Any],
    admitted_delta: Mapping[str, Any],
    drop_reason: str = "",
) -> dict[str, Any]:
    cards = _packet_cards_by_id(packet)
    trace_by_card_id = {
        _text(item.get("card_id")): _mapping(item)
        for item in consideration_trace
        if _text(item.get("card_id"))
    }
    candidate_edge = _one_edge_candidate_payload(one_edge_report)
    source_card_ids = _strings(candidate_edge.get("source_card_ids"))
    admitted_source_ids = set(_strings(admitted_delta.get("source_card_ids")))
    transactions: list[dict[str, Any]] = []
    for card_id, card in cards.items():
        trace = trace_by_card_id.get(card_id, {})
        is_admitted_source = card_id in admitted_source_ids
        trace_disposition = _text(trace.get("disposition"))
        if is_admitted_source:
            transactions.append(
                _one_edge_used_transaction(
                    card=card,
                    trace=trace,
                    one_edge_report=candidate_edge,
                    admitted_delta=admitted_delta,
                )
            )
        elif trace_disposition == "deferred":
            transactions.append(_one_edge_deferred_transaction(card=card, trace=trace))
        else:
            transactions.append(
                _one_edge_rejected_transaction(
                    card=card,
                    trace=trace,
                    was_source=card_id in source_card_ids,
                    drop_reason=drop_reason,
                )
            )

    return {
        "ledger_version": "card_transaction_ledger.v1",
        "packet_id": _text(packet.get("packet_id")),
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "card_transactions": transactions,
        "summary": summarize_card_transactions(transactions),
    }


def _one_edge_used_transaction(
    *,
    card: Mapping[str, Any],
    trace: Mapping[str, Any],
    one_edge_report: Mapping[str, Any],
    admitted_delta: Mapping[str, Any],
) -> dict[str, Any]:
    delta_type = _text(admitted_delta.get("delta_type"))
    public_delta_text = _text(admitted_delta.get("public_delta_text"))
    case_quote = _text(admitted_delta.get("case_quote")) or _text(trace.get("case_quote"))
    return {
        "card_id": _text(card.get("card_id")),
        "model_id": _text(card.get("model_id")),
        "disposition": "used",
        "effect_type": _one_edge_effect_type(delta_type),
        "affordance_ids_considered": _one_edge_affordance_ids(
            card=card,
            trace=trace,
            report_or_delta=admitted_delta,
            require_one=True,
        ),
        "merged_with_card_ids": [],
        "strongest_plausible_application": _text(trace.get("reason"))
        or "The card supports the admitted one-edge public delta.",
        "grounding_check": {
            "case_quote": case_quote,
            "evidence_status": _one_edge_evidence_status(trace, case_quote=case_quote),
            "missing_evidence": _strings(trace.get("missing_evidence")),
        },
        "decision_reason": _text(one_edge_report.get("why_this_changes_the_decision"))
        or "The one-edge report changed the public answer.",
        "rejection_ground": "",
        "risk_if_forced": "",
        "residue": "",
        "final_answer_delta": public_delta_text,
        "final_answer_visibility": _one_edge_visibility(delta_type),
    }


def _one_edge_rejected_transaction(
    *,
    card: Mapping[str, Any],
    trace: Mapping[str, Any],
    was_source: bool,
    drop_reason: str,
) -> dict[str, Any]:
    reason = _text(trace.get("reason")) or "No public one-edge delta survived for this card."
    if was_source and drop_reason:
        reason = f"Deterministic public gate rejected the proposed one-edge delta: {drop_reason}."
    return {
        "card_id": _text(card.get("card_id")),
        "model_id": _text(card.get("model_id")),
        "disposition": "rejected",
        "effect_type": "no_effect",
        "affordance_ids_considered": _one_edge_affordance_ids(
            card=card,
            trace=trace,
            report_or_delta={},
        ),
        "merged_with_card_ids": [],
        "strongest_plausible_application": _text(trace.get("strongest_plausible_application"))
        or "The card could have contributed a public edge if it survived the gate.",
        "grounding_check": {
            "case_quote": _text(trace.get("case_quote")),
            "evidence_status": _one_edge_evidence_status(trace),
            "missing_evidence": _strings(trace.get("missing_evidence")),
        },
        "decision_reason": reason,
        "rejection_ground": _one_edge_rejection_ground(drop_reason),
        "risk_if_forced": _text(trace.get("risk_if_forced"))
        or "Would add an ungrounded, duplicate, or low-value public edge.",
        "residue": _text(trace.get("residue")),
        "final_answer_delta": "",
        "final_answer_visibility": "not_visible",
    }


def _one_edge_deferred_transaction(
    *,
    card: Mapping[str, Any],
    trace: Mapping[str, Any],
) -> dict[str, Any]:
    missing_evidence = _strings(trace.get("missing_evidence"))
    residue = _text(trace.get("residue")) or _text(trace.get("reason")) or (
        "Needs missing evidence before public use."
    )
    return {
        "card_id": _text(card.get("card_id")),
        "model_id": _text(card.get("model_id")),
        "disposition": "deferred",
        "effect_type": "no_effect",
        "affordance_ids_considered": _one_edge_affordance_ids(
            card=card,
            trace=trace,
            report_or_delta={},
        ),
        "merged_with_card_ids": [],
        "strongest_plausible_application": _text(trace.get("strongest_plausible_application"))
        or "The card may become useful if missing evidence is supplied.",
        "grounding_check": {
            "case_quote": _text(trace.get("case_quote")),
            "evidence_status": _one_edge_deferred_evidence_status(trace),
            "missing_evidence": missing_evidence,
        },
        "decision_reason": _text(trace.get("reason")) or residue,
        "rejection_ground": "",
        "risk_if_forced": _text(trace.get("risk_if_forced")),
        "residue": residue,
        "final_answer_delta": "",
        "final_answer_visibility": "not_visible",
    }


def normalize_judge_output(payload: Mapping[str, Any], *, blind_map: Mapping[str, str]) -> dict[str, Any]:
    normalized = dict(payload)
    normalized["blind_map_for_audit_only"] = dict(blind_map)
    normalized["unblinded"] = {
        "winner": _unblind(_text(normalized.get("winner_label")), blind_map),
        "constructive_edge": _unblind(
            _text(normalized.get("constructive_edge_label")),
            blind_map,
        ),
        "missing_evidence_discipline": _unblind(
            _text(normalized.get("missing_evidence_discipline_label")),
            blind_map,
        ),
        "overburdened": _unblind(_text(normalized.get("overburdened_label")), blind_map),
        "model_theater": _unblind(_text(normalized.get("model_theater_label")), blind_map),
    }
    return normalized


def validate_arm_c_ledger_output(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    ledger = _mapping(payload.get("private_transaction_ledger")) or _mapping(
        payload.get("card_transaction_ledger")
    )
    if not ledger and _list(payload.get("card_transactions")):
        ledger = payload
    if not ledger:
        return {"status": "missing_ledger"}
    try:
        validate_card_transaction_ledger_payload(ledger, packet=packet)
    except CardTransactionLedgerValidationError as exc:
        repaired = dict(ledger)
        transactions = [_mapping(item) for item in _list(repaired.get("card_transactions"))]
        if transactions:
            repaired["summary"] = summarize_card_transactions(transactions)
            try:
                validate_card_transaction_ledger_payload(repaired, packet=packet)
            except CardTransactionLedgerValidationError:
                pass
            else:
                return {
                    "status": "valid_after_summary_repair",
                    "original_error": str(exc),
                    "transaction_count": len(transactions),
                    "summary": _mapping(repaired.get("summary")),
                }
        return {
            "status": "invalid",
            "error": str(exc),
            "transaction_count": len(_list(ledger.get("card_transactions"))),
        }
    return {
        "status": "valid",
        "transaction_count": len(_list(ledger.get("card_transactions"))),
        "summary": _mapping(ledger.get("summary")),
    }


def validate_delta_candidate_report_output(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    require_public_delta_gate: bool = False,
    require_compact_public_gate: bool = False,
) -> dict[str, Any]:
    report = _mapping(payload.get("delta_candidate_report"))
    if not report:
        return {"status": "missing_delta_candidate_report"}

    errors: list[str] = []
    cards = _packet_cards_by_id(packet)
    accepted = [_mapping(item) for item in _list(report.get("accepted_deltas"))]
    deferred = [_mapping(item) for item in _list(report.get("deferred_questions"))]
    warnings = [_mapping(item) for item in _list(report.get("risk_warnings"))]
    if require_compact_public_gate and len(accepted) + len(deferred) + len(warnings) > 1:
        errors.append("compact public gate allows at most one public addition")

    for index, delta in enumerate(accepted):
        prefix = f"accepted_deltas[{index}]"
        source_card_ids = _strings(delta.get("source_card_ids"))
        if not source_card_ids:
            errors.append(f"{prefix}.source_card_ids is required")
        errors.extend(_unknown_card_errors(prefix, source_card_ids, cards))
        public_text = _text(delta.get("public_delta_text")) or _text(
            delta.get("public_edge_text")
        )
        if not public_text:
            errors.append(f"{prefix}.public_delta_text or public_edge_text is required")
        if _has_private_mechanism_language(public_text):
            errors.append(f"{prefix}.public text leaks private mechanism language")
        if require_public_delta_gate:
            delta_type = _text(delta.get("delta_type"))
            if delta_type not in PUBLIC_DELTA_TYPES:
                errors.append(f"{prefix}.delta_type is invalid")
            if _has_framework_shaped_public_language(public_text):
                errors.append(f"{prefix}.public text is analytical-framework shaped")
            if not _is_directly_user_actionable(delta):
                errors.append(f"{prefix}.public text is not directly user-actionable")
        evidence_status = _text(delta.get("evidence_status"))
        if evidence_status not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status is invalid")
        case_quote = _text(delta.get("case_quote"))
        if require_compact_public_gate and not case_quote:
            errors.append(f"{prefix}.case_quote is required for compact public delta")
        elif require_public_delta_gate and evidence_status not in {"missing", "not_needed"}:
            if not case_quote:
                errors.append(f"{prefix}.case_quote is required for grounded public delta")
        affordance_ids = _strings(delta.get("affordance_ids"))
        allowed_affordance_ids = _allowed_affordance_ids_for_cards(source_card_ids, cards)
        unknown_affordance_ids = sorted(set(affordance_ids) - allowed_affordance_ids)
        if unknown_affordance_ids:
            errors.append(
                f"{prefix}.affordance_ids contains unknown IDs: {unknown_affordance_ids}"
            )

    for index, question in enumerate(deferred):
        prefix = f"deferred_questions[{index}]"
        source_card_ids = _strings(question.get("source_card_ids"))
        errors.extend(_unknown_card_errors(prefix, source_card_ids, cards))
        public_text = _text(question.get("public_question_text")) or _text(
            question.get("question")
        )
        if not public_text:
            errors.append(f"{prefix}.public_question_text or question is required")
        if _has_private_mechanism_language(public_text):
            errors.append(f"{prefix}.public text leaks private mechanism language")
        if require_public_delta_gate and _has_framework_shaped_public_language(public_text):
            errors.append(f"{prefix}.public text is analytical-framework shaped")
        if not _strings(question.get("missing_evidence")):
            errors.append(f"{prefix}.missing_evidence is required")

    for index, warning in enumerate(warnings):
        prefix = f"risk_warnings[{index}]"
        source_card_ids = _strings(warning.get("source_card_ids"))
        errors.extend(_unknown_card_errors(prefix, source_card_ids, cards))
        public_text = _text(warning.get("public_warning_text"))
        if not public_text:
            errors.append(f"{prefix}.public_warning_text is required")
        if _has_private_mechanism_language(public_text):
            errors.append(f"{prefix}.public text leaks private mechanism language")
        if require_public_delta_gate and _has_framework_shaped_public_language(public_text):
            errors.append(f"{prefix}.public text is analytical-framework shaped")

    if not accepted and not _text(report.get("no_delta_reason")):
        errors.append("no_delta_reason is required when accepted_deltas is empty")

    ledger = _mapping(payload.get("private_transaction_ledger")) or _mapping(
        payload.get("card_transaction_ledger")
    )
    if not ledger:
        errors.append("private_transaction_ledger is required for C3 delta consistency")
    else:
        transactions = [_mapping(item) for item in _list(ledger.get("card_transactions"))]
        used_card_ids = {
            _text(item.get("card_id"))
            for item in transactions
            if _text(item.get("disposition")) == "used"
        }
        visible_used_card_ids = {
            _text(item.get("card_id"))
            for item in transactions
            if _text(item.get("disposition")) == "used"
            and _text(item.get("final_answer_visibility"))
            in {"visible_question", "visible_caveat", "visible_reframe"}
        }
        accepted_card_ids = {
            card_id
            for delta in accepted
            for card_id in _strings(delta.get("source_card_ids"))
        }
        accepted_without_used = sorted(accepted_card_ids - used_card_ids)
        visible_used_without_delta = sorted(visible_used_card_ids - accepted_card_ids)
        if accepted_without_used:
            errors.append(
                f"accepted deltas reference non-used card transactions: {accepted_without_used}"
            )
        if visible_used_without_delta:
            errors.append(
                f"visible used card transactions lack accepted deltas: {visible_used_without_delta}"
            )

    if errors:
        return {
            "status": "invalid",
            "errors": errors,
            "accepted_delta_count": len(accepted),
            "deferred_question_count": len(deferred),
            "risk_warning_count": len(warnings),
        }
    return {
        "status": "valid",
        "accepted_delta_count": len(accepted),
        "deferred_question_count": len(deferred),
        "risk_warning_count": len(warnings),
    }


def validate_consideration_usefulness_output(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
) -> dict[str, Any]:
    report = _mapping(payload.get("consideration_usefulness_report"))
    if not report:
        return {"status": "missing_consideration_usefulness_report"}

    errors: list[str] = []
    cards = _packet_cards_by_id(packet)
    assessments = [_mapping(item) for item in _list(report.get("chunk_assessments"))]
    selected = [_mapping(item) for item in _list(report.get("selected_opportunities"))]
    packet_usefulness = _text(report.get("packet_usefulness"))
    if packet_usefulness not in CONSIDERATION_PACKET_USEFULNESS:
        errors.append("consideration_usefulness_report.packet_usefulness is invalid")
    if not isinstance(report.get("chunk_assessments"), list):
        errors.append("consideration_usefulness_report.chunk_assessments must be a list")

    assessment_card_ids = [_text(item.get("card_id")) for item in assessments]
    missing_assessments = sorted(set(cards) - set(assessment_card_ids))
    unknown_assessments = sorted(set(assessment_card_ids) - set(cards))
    duplicate_assessments = sorted(
        card_id
        for card_id, count in Counter(assessment_card_ids).items()
        if card_id and count > 1
    )
    if missing_assessments:
        errors.append(f"chunk_assessments missing card IDs: {missing_assessments}")
    if unknown_assessments:
        errors.append(f"chunk_assessments contains unknown card IDs: {unknown_assessments}")
    if duplicate_assessments:
        errors.append(f"chunk_assessments duplicates card IDs: {duplicate_assessments}")

    public_routes = {"public_answer_delta", "diagnostic_question", "evidence_gate", "guardrail"}
    private_or_blocked_routes = {
        "private_reasoning",
        "defer_missing_evidence",
        "reject_irrelevant",
        "reject_duplicate",
    }
    selected_public_route_count = 0
    for index, item in enumerate(assessments):
        prefix = f"chunk_assessments[{index}]"
        card_id = _text(item.get("card_id"))
        card = cards.get(card_id)
        if card and _text(item.get("model_id")) != _text(card.get("model_id")):
            errors.append(f"{prefix}.model_id must match packet card")
        usefulness = _text(item.get("usefulness_to_consider"))
        if usefulness not in CONSIDERATION_USEFULNESS_LEVELS:
            errors.append(f"{prefix}.usefulness_to_consider is invalid")
        role = _text(item.get("opportunity_role"))
        if role not in CONSIDERATION_OPPORTUNITY_ROLES:
            errors.append(f"{prefix}.opportunity_role is invalid")
        route = _text(item.get("route"))
        if route not in CONSIDERATION_ROUTES:
            errors.append(f"{prefix}.route is invalid")
        if route in public_routes:
            selected_public_route_count += 1
        if route in private_or_blocked_routes and not _text(item.get("why_not_used_publicly")):
            errors.append(f"{prefix}.why_not_used_publicly is required for private/defer/reject routes")
        evidence_status = _text(item.get("evidence_status"))
        if evidence_status not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status is invalid")
        if card:
            allowed_affordance_ids = _card_affordance_ids(card)
            unknown_affordance_ids = sorted(
                set(_strings(item.get("affordance_ids_considered"))) - allowed_affordance_ids
            )
            if unknown_affordance_ids:
                errors.append(
                    f"{prefix}.affordance_ids_considered contains unknown IDs: {unknown_affordance_ids}"
                )

    if len(selected) > 3:
        errors.append("selected_opportunities allows at most 3 items")
    for index, opportunity in enumerate(selected):
        prefix = f"selected_opportunities[{index}]"
        route = _text(opportunity.get("route"))
        if route not in CONSIDERATION_SELECTED_ROUTES:
            errors.append(f"{prefix}.route is invalid")
        source_card_ids = _strings(opportunity.get("source_card_ids"))
        if not source_card_ids:
            errors.append(f"{prefix}.source_card_ids is required")
        errors.extend(_unknown_card_errors(prefix, source_card_ids, cards))
        public_surface = _text(opportunity.get("public_surface"))
        if route != "private_reasoning" and not public_surface:
            errors.append(f"{prefix}.public_surface is required for public routes")
        if public_surface and _has_private_mechanism_language(public_surface):
            errors.append(f"{prefix}.public_surface leaks private mechanism language")
        if not _text(opportunity.get("private_value")):
            errors.append(f"{prefix}.private_value is required")

    if selected_public_route_count == 0 and not _text(report.get("no_public_delta_reason")):
        errors.append("no_public_delta_reason is required when no assessment routes publicly")

    public_fields = [
        _text(payload.get("final_answer")),
        _text(payload.get("mode_output")),
        *_public_text_list(payload.get("edge_findings")),
        *_public_text_list(payload.get("reasoning_delta_summary")),
        *_public_text_list(payload.get("risk_register")),
    ]
    if not (_text(payload.get("final_answer")) or _text(payload.get("mode_output"))):
        errors.append("final_answer or mode_output is required")
    leaks = [text for text in public_fields if _has_private_mechanism_language(text)]
    if leaks:
        errors.append("public output leaks private mechanism language")

    if errors:
        return {
            "status": "invalid",
            "errors": errors,
            "assessment_count": len(assessments),
            "selected_opportunity_count": len(selected),
        }
    return {
        "status": "valid",
        "assessment_count": len(assessments),
        "selected_opportunity_count": len(selected),
        "packet_usefulness": packet_usefulness,
    }


def validate_one_edge_report_output(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    case_evidence_text: str = "",
    require_exact_case_quote: bool = False,
    public_delta_gate_policy: str = "",
) -> dict[str, Any]:
    report = _mapping(payload.get("one_edge_report"))
    if not report:
        return {"status": "missing_one_edge_report"}

    errors: list[str] = []
    cards = _packet_cards_by_id(packet)
    trace = [_mapping(item) for item in _list(payload.get("private_consideration_trace"))]
    if not isinstance(payload.get("private_consideration_trace"), list):
        errors.append("private_consideration_trace must be a list")

    trace_card_ids = [_text(item.get("card_id")) for item in trace]
    missing_trace_ids = sorted(set(cards) - set(trace_card_ids))
    unknown_trace_ids = sorted(set(trace_card_ids) - set(cards))
    duplicate_trace_ids = sorted(
        card_id for card_id, count in Counter(trace_card_ids).items() if card_id and count > 1
    )
    if missing_trace_ids:
        errors.append(f"private_consideration_trace missing card IDs: {missing_trace_ids}")
    if unknown_trace_ids:
        errors.append(f"private_consideration_trace contains unknown card IDs: {unknown_trace_ids}")
    if duplicate_trace_ids:
        errors.append(f"private_consideration_trace duplicates card IDs: {duplicate_trace_ids}")

    for index, item in enumerate(trace):
        prefix = f"private_consideration_trace[{index}]"
        card_id = _text(item.get("card_id"))
        card = cards.get(card_id)
        disposition = _text(item.get("disposition"))
        if disposition not in {"used", "rejected", "deferred"}:
            errors.append(f"{prefix}.disposition is invalid")
        evidence_status = _text(item.get("evidence_status"))
        if evidence_status and evidence_status not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status is invalid")
        if card:
            unknown_affordance_ids = sorted(
                set(_strings(item.get("affordance_ids_considered")))
                - _card_affordance_ids(card)
            )
            if unknown_affordance_ids:
                errors.append(
                    f"{prefix}.affordance_ids_considered contains unknown IDs: {unknown_affordance_ids}"
                )

    is_candidate_edge_report = "best_candidate_edge" in report
    candidate_edge = _one_edge_candidate_payload(report)
    should_add = is_candidate_edge_report or _boolish(report.get("should_add_public_delta"))
    if is_candidate_edge_report and not candidate_edge:
        errors.append("one_edge_report.best_candidate_edge is required")
    if is_candidate_edge_report:
        if "recommend_public_admission" not in report:
            errors.append("one_edge_report.recommend_public_admission is required")
        if not _text(report.get("admission_rationale")):
            errors.append("one_edge_report.admission_rationale is required")

    if should_add:
        delta = _one_edge_report_to_delta(report)
        source_card_ids = _strings(candidate_edge.get("source_card_ids"))
        prefix = (
            "one_edge_report.best_candidate_edge"
            if is_candidate_edge_report
            else "one_edge_report"
        )
        if not source_card_ids:
            errors.append(f"{prefix}.source_card_ids is required")
        errors.extend(_unknown_card_errors(prefix, source_card_ids, cards))
        delta_type = _text(candidate_edge.get("delta_type"))
        if delta_type not in PUBLIC_DELTA_TYPES:
            errors.append(f"{prefix}.delta_type is invalid")
        case_quote = _text(candidate_edge.get("case_quote"))
        if not case_quote:
            errors.append(f"{prefix}.case_quote is required")
        elif require_exact_case_quote and not _case_quote_is_supported(
            case_quote,
            case_evidence_text,
        ):
            errors.append(f"{prefix}.case_quote is not an exact case substring")
        public_text = _text(candidate_edge.get("public_delta_text"))
        if not public_text:
            errors.append(f"{prefix}.public_delta_text is required")
        if _has_private_mechanism_language(public_text):
            errors.append(f"{prefix}.public text leaks private mechanism language")
        if _has_framework_shaped_public_language(public_text):
            errors.append(f"{prefix}.public text is analytical-framework shaped")
        if public_text and not _is_directly_user_actionable(
            delta,
            policy=public_delta_gate_policy,
        ):
            errors.append(f"{prefix}.public text is not directly user-actionable")
        if not _text(candidate_edge.get("why_this_changes_the_decision")):
            errors.append(f"{prefix}.why_this_changes_the_decision is required")
        allowed_affordance_ids = _allowed_affordance_ids_for_cards(source_card_ids, cards)
        unknown_affordance_ids = sorted(
            set(_strings(candidate_edge.get("affordance_ids"))) - allowed_affordance_ids
        )
        if unknown_affordance_ids:
            errors.append(
                f"{prefix}.affordance_ids contains unknown IDs: {unknown_affordance_ids}"
            )
    elif not _text(report.get("no_delta_reason")):
        errors.append("one_edge_report.no_delta_reason is required when false")

    if errors:
        return {
            "status": "invalid",
            "errors": errors,
            "trace_count": len(trace),
            "public_delta_count": 1 if should_add else 0,
        }
    return {
        "status": "valid",
        "trace_count": len(trace),
        "public_delta_count": 1 if should_add else 0,
    }


def call_openrouter_json(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_packet: Mapping[str, Any],
    stage: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_packet, ensure_ascii=False)},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    if model.lower().startswith("x-ai/grok-4.1-fast"):
        body["reasoning"] = {"effort": "none"}

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    referer = os.getenv("LOLLA_OPENROUTER_HTTP_REFERER") or os.getenv(
        "LOLLA_OPENROUTER_SITE_URL",
        "",
    )
    title = os.getenv("LOLLA_OPENROUTER_X_TITLE") or os.getenv(
        "LOLLA_OPENROUTER_APP_NAME",
        "",
    )
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title
    if model.startswith("x-ai/grok"):
        run_id = os.getenv("LOLLA_RUN_ID") or f"v60-paid-{datetime.now(timezone.utc).date()}"
        headers["x-grok-conv-id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, run_id))

    req = urllib.request.Request(
        OPENROUTER_URL,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(req, timeout=OPENROUTER_TIMEOUT_S) as response:
            raw_response = response.read().decode("utf-8", errors="replace")
            response_payload = json.loads(raw_response)
    except urllib.error.HTTPError as exc:
        body_preview = exc.read().decode(errors="replace")[:1000]
        raise ReplayCallError(
            f"OpenRouter HTTP {exc.code} at {stage}: {body_preview}",
            stage=stage,
            raw_content=body_preview,
        ) from exc
    except urllib.error.URLError as exc:
        raise ReplayCallError(
            f"OpenRouter URL error at {stage}: {exc.reason}",
            stage=stage,
        ) from exc
    except json.JSONDecodeError as exc:
        raise ReplayCallError(
            f"OpenRouter returned malformed JSON at {stage}: {raw_response[:1000]}",
            stage=stage,
            raw_content=raw_response[:4000],
        ) from exc
    except TimeoutError as exc:
        raise ReplayCallError(f"OpenRouter timeout at {stage}", stage=stage) from exc

    choices = _list(response_payload.get("choices"))
    if not choices:
        raise ReplayCallError(f"OpenRouter response has no choices at {stage}", stage=stage)
    message = _mapping(_mapping(choices[0]).get("message"))
    content = message.get("content", "")
    if isinstance(content, list):
        content = "\n".join(
            str(part.get("text", ""))
            for part in content
            if isinstance(part, Mapping)
        )
    text = str(content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ReplayCallError(
            f"Model returned non-JSON at {stage}: {text[:1000]}",
            stage=stage,
            raw_content=text,
        ) from exc

    usage = _mapping(response_payload.get("usage"))
    metadata = {
        "provider": "openrouter",
        "model": model,
        "stage": stage,
        "started_at": started_at,
        "input_tokens": _int(usage.get("prompt_tokens")),
        "output_tokens": _int(usage.get("completion_tokens")),
        "total_tokens": _int(usage.get("total_tokens")),
        "cost_usd": float(usage.get("cost") or usage.get("total_cost") or 0.0),
    }
    return payload, metadata


def _dry_run_output(*, item: ReplayItem, arm: str, prompt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "dry_run_placeholder": True,
        "item_id": item.item_id,
        "arm": arm,
        "estimated_prompt_tokens": estimate_tokens(prompt),
    }


def _dry_run_judge(*, item: ReplayItem) -> dict[str, Any]:
    return {"dry_run_placeholder": True, "item_id": item.item_id}


def _error_output(exc: ReplayCallError) -> dict[str, Any]:
    return {
        "status": "error",
        "stage": exc.stage,
        "error": str(exc),
        "raw_content": exc.raw_content,
    }


def _error_summary(exc: ReplayCallError) -> dict[str, Any]:
    return {
        "stage": exc.stage,
        "error": str(exc),
        "raw_content_preview": exc.raw_content[:1000],
    }


def _aggregate(rows: list[Mapping[str, Any]], call_records: list[Mapping[str, Any]]) -> dict[str, Any]:
    judge_winners = Counter(
        _text(_mapping(_mapping(row.get("judge")).get("unblinded")).get("winner"))
        for row in rows
    )
    ledger_statuses = Counter(
        _text(_mapping(row.get("ledger_validation")).get("status"))
        for row in rows
    )
    delta_statuses = Counter(
        _text(_mapping(row.get("delta_validation")).get("status"))
        for row in rows
    )
    consideration_statuses = Counter(
        _text(_mapping(row.get("consideration_validation")).get("status"))
        for row in rows
    )
    consideration_packet_usefulness = Counter(
        _text(_mapping(row.get("consideration_validation")).get("packet_usefulness"))
        for row in rows
    )
    compositions = [
        _mapping(row.get("c3_composition"))
        for row in rows
        if _mapping(row.get("c3_composition"))
    ]
    public_gate_counts: dict[str, int] = {}
    public_gate_drop_reasons: dict[str, int] = {}
    if compositions:
        drop_reason_counts = Counter(
            _text(_mapping(drop).get("reason"))
            for composition in compositions
            for drop in _list(composition.get("dropped_public_deltas"))
        )
        public_gate_counts = {
            "gate_enabled_items": sum(
                1 for composition in compositions if composition.get("public_delta_gate") is True
            ),
            "accepted_delta_count": sum(
                _int(composition.get("accepted_delta_count")) for composition in compositions
            ),
            "deferred_question_count": sum(
                _int(composition.get("deferred_question_count")) for composition in compositions
            ),
            "risk_warning_count": sum(
                _int(composition.get("risk_warning_count")) for composition in compositions
            ),
            "raw_accepted_delta_count": sum(
                _int(composition.get("raw_accepted_delta_count")) for composition in compositions
            ),
            "raw_deferred_question_count": sum(
                _int(composition.get("raw_deferred_question_count")) for composition in compositions
            ),
            "raw_risk_warning_count": sum(
                _int(composition.get("raw_risk_warning_count")) for composition in compositions
            ),
            "dropped_public_delta_count": sum(
                _int(composition.get("dropped_public_delta_count")) for composition in compositions
            ),
            "collapse_to_b_count": sum(
                1 for composition in compositions if composition.get("no_delta_collapse_to_b") is True
            ),
        }
        public_gate_drop_reasons = dict(
            sorted((reason, count) for reason, count in drop_reason_counts.items() if reason)
        )

    aggregate = {
        "judge_winner_counts": dict(sorted((k, v) for k, v in judge_winners.items() if k)),
        "ledger_validation_counts": dict(sorted((k, v) for k, v in ledger_statuses.items() if k)),
        "delta_validation_counts": dict(sorted((k, v) for k, v in delta_statuses.items() if k)),
        "consideration_validation_counts": dict(
            sorted((k, v) for k, v in consideration_statuses.items() if k)
        ),
        "call_count": len(call_records),
        "input_tokens": sum(_int(record.get("input_tokens")) for record in call_records),
        "output_tokens": sum(_int(record.get("output_tokens")) for record in call_records),
        "total_tokens": sum(_int(record.get("total_tokens")) for record in call_records),
        "cost_usd": round(sum(float(record.get("cost_usd") or 0.0) for record in call_records), 6),
    }
    filtered_packet_usefulness = dict(
        sorted((k, v) for k, v in consideration_packet_usefulness.items() if k)
    )
    if filtered_packet_usefulness:
        aggregate["consideration_packet_usefulness_counts"] = filtered_packet_usefulness
    if public_gate_counts:
        aggregate["public_delta_gate_counts"] = public_gate_counts
        aggregate["public_delta_gate_drop_reasons"] = public_gate_drop_reasons
    return aggregate


def render_report(summary: Mapping[str, Any]) -> str:
    aggregate = _mapping(summary.get("aggregate"))
    lines = [
        "# V60 Transaction Paid Replay Report",
        "",
        f"Date: {datetime.now(timezone.utc).date().isoformat()}",
        f"Status: {'dry run' if summary.get('dry_run') else 'paid replay'}",
        f"Config: `{_text(_mapping(summary.get('config')).get('config_id'))}`",
        f"Generator: `{_text(summary.get('generator_model'))}`",
        f"Judge: `{_text(summary.get('judge_model')) or 'skipped'}`",
        f"C variant: `{_text(summary.get('c_variant')) or DEFAULT_C_VARIANT}`",
        "",
        "## Aggregate",
        "",
        f"- Items: {len(_list(summary.get('items')))}",
        f"- Paid calls: {_text(aggregate.get('call_count')) or '0'}",
        f"- Estimated reported cost: ${float(aggregate.get('cost_usd') or 0.0):.6f}",
        f"- Judge winners: `{json.dumps(aggregate.get('judge_winner_counts', {}), sort_keys=True)}`",
        f"- Ledger validation: `{json.dumps(aggregate.get('ledger_validation_counts', {}), sort_keys=True)}`",
        f"- Delta validation: `{json.dumps(aggregate.get('delta_validation_counts', {}), sort_keys=True)}`",
        f"- Consideration validation: `{json.dumps(aggregate.get('consideration_validation_counts', {}), sort_keys=True)}`",
    ]
    if aggregate.get("consideration_packet_usefulness_counts"):
        lines.append(
            f"- Consideration usefulness: `{json.dumps(aggregate.get('consideration_packet_usefulness_counts', {}), sort_keys=True)}`"
        )
    if aggregate.get("public_delta_gate_counts"):
        lines.extend(
            [
                f"- Public delta gate: `{json.dumps(aggregate.get('public_delta_gate_counts', {}), sort_keys=True)}`",
                f"- Public delta drops: `{json.dumps(aggregate.get('public_delta_gate_drop_reasons', {}), sort_keys=True)}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Items",
            "",
            "| Item | Cards | Suppressed | Ledger | Judge Winner | Promotion |",
            "| --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in (_mapping(item) for item in _list(summary.get("items"))):
        judge = _mapping(row.get("judge"))
        unblinded = _mapping(judge.get("unblinded"))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_text(row.get('item_id'))}`",
                    str(len(_list(row.get("candidate_model_ids")))),
                    str(_int(row.get("suppressed_candidate_count"))),
                    f"`{_text(_mapping(row.get('ledger_validation')).get('status'))}`",
                    f"`{_text(unblinded.get('winner')) or 'n/a'}`",
                    f"`{_text(judge.get('promotion_read')) or 'n/a'}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "This report is evidence for replay behavior only. It does not promote v60 into live /lolla.",
            "Treat Arm C wins as candidates for human inspection, not automatic proof of product readiness.",
        ]
    )
    return "\n".join(lines) + "\n"


def _selected_config(config_id: str) -> MatrixConfig:
    for config in MATRIX_CONFIGS:
        if config.config_id == config_id:
            return config
    allowed = ", ".join(config.config_id for config in MATRIX_CONFIGS)
    raise ReplayLabError(f"Unknown config_id {config_id!r}; allowed: {allowed}")


def _selected_modes(mode_ids: list[str]) -> list[SolutionMode]:
    by_id = {mode.mode_id: mode for mode in SOLUTION_MODES}
    selected = []
    for mode_id in mode_ids:
        if mode_id not in by_id:
            raise ReplayLabError(f"Unknown mode {mode_id!r}; allowed: {sorted(by_id)}")
        selected.append(by_id[mode_id])
    return selected


def _selected_cases(cases: list[Any], *, case_ids: list[str]) -> list[Any]:
    by_id = {case.case_id: case for case in cases}
    selected = []
    for case_id in case_ids:
        if case_id not in by_id:
            raise ReplayLabError(f"Unknown case_id {case_id!r}; allowed: {sorted(by_id)}")
        selected.append(by_id[case_id])
    return selected


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-manifest", default=str(DEFAULT_CASE_MANIFEST))
    parser.add_argument("--affordances-path", default=str(DEFAULT_AFFORDANCES_PATH))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--config-id", default=DEFAULT_CONFIG_ID)
    parser.add_argument("--cases", nargs="+", default=list(DEFAULT_CASE_IDS))
    parser.add_argument("--modes", nargs="+", default=list(DEFAULT_MODE_IDS))
    parser.add_argument("--generator-model", default=DEFAULT_GENERATOR_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--c-variant", choices=sorted(C_VARIANTS), default=DEFAULT_C_VARIANT)
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-items", type=int, default=0)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser.parse_args(argv)


def _resolve(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _unblind(label: str, blind_map: Mapping[str, str]) -> str:
    if label in {"tie", "neither", "both", "both_bad"}:
        return label
    return _text(blind_map.get(label))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _public_text_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [_text(value)] if _text(value) else []
    output: list[str] = []
    for item in _list(value):
        if isinstance(item, Mapping):
            text = (
                _text(item.get("public_edge_text"))
                or _text(item.get("public_delta_text"))
                or _text(item.get("why it matters"))
                or _text(item.get("why_it_matters"))
                or _text(item.get("question"))
                or _text(item.get("claim"))
                or json.dumps(item, ensure_ascii=False, sort_keys=True)
            )
        else:
            text = _text(item)
        if text:
            output.append(text)
    return output


def _public_items(value: Any) -> list[Any]:
    if isinstance(value, str):
        return [_text(value)] if _text(value) else []
    if isinstance(value, list):
        return [item for item in value if item not in ("", None)]
    return []


def _accepted_delta_public_items(deltas: list[Mapping[str, Any]]) -> list[Any]:
    output: list[Any] = []
    for delta in deltas:
        edge = _text(delta.get("public_edge_text")) or _text(delta.get("public_delta_text"))
        why = _text(delta.get("why_user_should_care"))
        action = _text(delta.get("public_delta_text"))
        if not edge:
            continue
        if why or (action and action != edge):
            item = [edge]
            if why:
                item.append(why)
            if action and action != edge:
                item.append(action)
            output.append(item)
        else:
            output.append(edge)
    return output


def _deferred_question_public_items(questions: list[Mapping[str, Any]]) -> list[Any]:
    output: list[Any] = []
    for question in questions:
        public_question = _text(question.get("public_question_text")) or _text(
            question.get("question")
        )
        why_blocks = _text(question.get("why_it_blocks_claim"))
        missing = ", ".join(_strings(question.get("missing_evidence")))
        if not public_question:
            continue
        item = [public_question]
        if why_blocks:
            item.append(why_blocks)
        if missing:
            item.append(f"Missing evidence: {missing}")
        output.append(item if len(item) > 1 else public_question)
    return output


def _risk_warning_public_items(warnings: list[Mapping[str, Any]]) -> list[Any]:
    output: list[Any] = []
    for warning in warnings:
        public_warning = _text(warning.get("public_warning_text"))
        severity = _text(warning.get("severity"))
        if not public_warning:
            continue
        output.append([public_warning, f"Severity: {severity}"] if severity else public_warning)
    return output


def _public_delta_drop_reason(
    delta: Mapping[str, Any],
    *,
    baseline_text: str,
    policy: str = "c3_5",
    case_evidence_text: str = "",
) -> str:
    delta_type = _text(delta.get("delta_type"))
    if delta_type not in PUBLIC_DELTA_TYPES:
        return "invalid_or_missing_delta_type"
    public_text = _delta_public_text(delta)
    if not public_text:
        return "missing_public_delta_text"
    compact_policies = {
        "c3_6_compact",
        "c4_one_edge",
        "c4_1_candidate_edge",
        "c4_2_hardened_edge",
    }
    case_quote = _text(delta.get("case_quote"))
    if policy in compact_policies and not case_quote:
        return "missing_case_quote"
    if policy == "c4_2_hardened_edge" and not _case_quote_is_supported(
        case_quote,
        case_evidence_text,
    ):
        return "case_quote_not_exact"
    if policy in {"c3_6_compact", "c4_one_edge", "c4_1_candidate_edge"} and not _text(
        delta.get("case_quote")
    ):
        return "missing_case_quote"
    if _has_private_mechanism_language(public_text):
        return "private_mechanism_language"
    if _has_framework_shaped_public_language(public_text):
        return "analytical_framework_language"
    if not _is_directly_user_actionable(delta, policy=policy):
        return "not_directly_user_actionable"
    duplicate_threshold = (
        0.68
        if policy in compact_policies
        else 0.82
    )
    duplicate_checks = [
        public_text,
        _text(delta.get("public_delta_text")),
        _text(delta.get("public_edge_text")),
    ]
    if any(
        _is_duplicate_of_baseline(
            candidate,
            baseline_text,
            overlap_threshold=duplicate_threshold,
        )
        for candidate in duplicate_checks
        if candidate
    ):
        return "duplicate_of_baseline_public_output"
    return ""


def _deferred_question_drop_reason(question: Mapping[str, Any], *, baseline_text: str) -> str:
    public_text = _text(question.get("public_question_text")) or _text(question.get("question"))
    if not public_text:
        return "missing_public_question_text"
    if _has_private_mechanism_language(public_text):
        return "private_mechanism_language"
    if _has_framework_shaped_public_language(public_text):
        return "analytical_framework_language"
    if not _strings(question.get("missing_evidence")):
        return "missing_evidence_required"
    if _is_duplicate_of_baseline(public_text, baseline_text):
        return "duplicate_of_baseline_public_output"
    return ""


def _risk_warning_drop_reason(warning: Mapping[str, Any], *, baseline_text: str) -> str:
    public_text = _text(warning.get("public_warning_text"))
    if not public_text:
        return "missing_public_warning_text"
    if _has_private_mechanism_language(public_text):
        return "private_mechanism_language"
    if _has_framework_shaped_public_language(public_text):
        return "analytical_framework_language"
    if _is_duplicate_of_baseline(public_text, baseline_text):
        return "duplicate_of_baseline_public_output"
    return ""


def _one_edge_report_to_delta(report: Mapping[str, Any]) -> dict[str, Any]:
    candidate = _one_edge_candidate_payload(report)
    if not candidate:
        return {}
    if "best_candidate_edge" not in report and not _boolish(report.get("should_add_public_delta")):
        return {}
    return {
        "delta_id": _text(candidate.get("delta_id")) or "one-edge",
        "delta_type": _text(candidate.get("delta_type")),
        "source_card_ids": _strings(candidate.get("source_card_ids")),
        "affordance_ids": _strings(candidate.get("affordance_ids")),
        "public_delta_text": _text(candidate.get("public_delta_text")),
        "public_edge_text": _text(candidate.get("public_edge_text"))
        or _text(candidate.get("public_delta_text")),
        "evidence_status": _text(candidate.get("evidence_status"))
        or ("quoted_exact" if _text(candidate.get("case_quote")) else "inferred_from_turn"),
        "case_quote": _text(candidate.get("case_quote")),
        "why_user_should_care": _text(candidate.get("why_this_changes_the_decision"))
        or _text(candidate.get("why_user_should_care")),
        "confidence": _text(candidate.get("confidence")),
    }


def _one_edge_candidate_payload(report: Mapping[str, Any]) -> dict[str, Any]:
    candidate = _mapping(report.get("best_candidate_edge"))
    if candidate:
        return candidate
    return _mapping(report)


def _one_edge_affordance_ids(
    *,
    card: Mapping[str, Any],
    trace: Mapping[str, Any],
    report_or_delta: Mapping[str, Any],
    require_one: bool = False,
) -> list[str]:
    allowed = _card_affordance_ids(card)
    candidates = [
        aff_id
        for aff_id in [
            *_strings(report_or_delta.get("affordance_ids")),
            *_strings(trace.get("affordance_ids_considered")),
        ]
        if aff_id in allowed
    ]
    deduped = _dedupe_texts(candidates)
    if deduped or not require_one or not allowed:
        return deduped
    return [sorted(allowed)[0]]


def _one_edge_effect_type(delta_type: str) -> str:
    if delta_type == "evidence_gate":
        return "diagnostic_question"
    if delta_type == "risk_caveat":
        return "guardrail"
    if delta_type == "option_space_expansion":
        return "counterframe"
    return "direct_answer_delta"


def _one_edge_visibility(delta_type: str) -> str:
    if delta_type == "evidence_gate":
        return "visible_question"
    if delta_type == "risk_caveat":
        return "visible_caveat"
    return "visible_reframe"


def _one_edge_evidence_status(
    trace: Mapping[str, Any],
    *,
    case_quote: str = "",
) -> str:
    status = _text(trace.get("evidence_status"))
    if status in EVIDENCE_STATUSES:
        return status
    return "quoted_exact" if case_quote or _text(trace.get("case_quote")) else "not_needed"


def _one_edge_deferred_evidence_status(trace: Mapping[str, Any]) -> str:
    status = _text(trace.get("evidence_status"))
    if status in {"missing", "conflicting", "inferred_from_turn"}:
        return status
    return "missing"


def _one_edge_rejection_ground(drop_reason: str) -> str:
    if drop_reason == "duplicate_of_baseline_public_output":
        return "duplicate_of_existing_pressure"
    if drop_reason in {"missing_case_quote", "case_quote_not_exact"}:
        return "missing_case_evidence"
    if drop_reason in {
        "private_mechanism_language",
        "analytical_framework_language",
        "not_directly_user_actionable",
        "invalid_or_missing_delta_type",
        "missing_public_delta_text",
    }:
        return "user_facing_risk"
    return "duplicate_of_existing_pressure"


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1"}
    return bool(value)


def _delta_public_text(delta: Mapping[str, Any]) -> str:
    return " ".join(
        part
        for part in (
            _text(delta.get("public_edge_text")),
            _text(delta.get("why_user_should_care")),
            _text(delta.get("public_delta_text")),
        )
        if part
    )


def _is_directly_user_actionable(delta: Mapping[str, Any], *, policy: str = "") -> bool:
    text = _delta_public_text(delta).lower()
    delta_type = _text(delta.get("delta_type"))
    if delta_type == "evidence_gate":
        return bool(
            re.search(r"\b(verify|confirm|check|ask|until|before|unless|missing|evidence)\b", text)
        )
    if delta_type == "concrete_next_move":
        return bool(
            re.search(
                r"\b(ask|call|document|write|submit|set|request|check|run|schedule|tell|draft|send|decide)\b",
                text,
            )
        )
    if delta_type == "risk_caveat":
        return bool(re.search(r"\b(risk|caveat|unless|if|may|could|before|do not|don't)\b", text))
    if delta_type == "option_space_expansion":
        if policy == "c4_2_hardened_edge":
            if re.search(r"\bconsider(?:ing)?\b", text) and not re.search(
                r"\b(ask|request|call|negotiate|extend|delay|defer|hold|run|test|pilot|schedule|create|preserve|keep|sequence|set)\b",
                text,
            ):
                return False
            return bool(
                re.search(
                    r"\b(ask|request|call|negotiate|extend|extension|delay|defer|hold|run|test|pilot|schedule|create|preserve|keep|sequence|set|option|options|path|alternative)\b",
                    text,
                )
            )
        return bool(
            re.search(r"\b(option|path|alternative|instead|third path|sequence|extension|escalation)\b", text)
        )
    return False


def _has_framework_shaped_public_language(text: str) -> bool:
    return bool(
        re.search(
            r"\b("
            r"payoff map|payoffs?|game tree|principal[-/ ]agent|principal\b|"
            r"leverage map|branch(?:es|ing)?|counterparty|incentive alignment|"
            r"agent controls|agent .* principal|framework"
            r")",
            text,
            flags=re.IGNORECASE,
        )
    )


def _baseline_public_text(base_public: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for key in ("final_answer", "mode_output", "answer", "confidence_shift"):
        if _text(base_public.get(key)):
            parts.append(_text(base_public.get(key)))
    for key in ("edge_findings", "gated_questions", "risk_register", "answerable_now"):
        parts.extend(_public_item_to_text(item) for item in _public_items(base_public.get(key)))
    return " ".join(parts).lower()


def _case_evidence_text(case_artifact: Mapping[str, Any]) -> str:
    parts = [
        _text(case_artifact.get("query")),
        _text(case_artifact.get("conversation_excerpt")),
    ]
    return "\n".join(part for part in parts if part)


def _case_quote_is_supported(case_quote: str, case_evidence_text: str) -> bool:
    quote = _text(case_quote)
    evidence = _text(case_evidence_text)
    if not quote:
        return False
    if not evidence:
        return True
    if quote in evidence:
        return True
    return _squash_ws(quote) in _squash_ws(evidence)


def _squash_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _public_delta_gate_policy(
    *,
    public_delta_gate: bool,
    public_delta_gate_policy: str,
) -> str:
    if public_delta_gate_policy:
        return public_delta_gate_policy
    if public_delta_gate:
        return "c3_5"
    return ""


def _is_duplicate_of_baseline(
    public_text: str,
    baseline_text: str,
    *,
    overlap_threshold: float = 0.82,
) -> bool:
    normalized = _normalize_for_overlap(public_text)
    if not normalized or len(normalized) < 24:
        return False
    if normalized in _normalize_for_overlap(baseline_text):
        return True
    words = {word for word in normalized.split() if len(word) > 4}
    if len(words) < 5:
        return False
    baseline_words = {word for word in _normalize_for_overlap(baseline_text).split() if len(word) > 4}
    return len(words & baseline_words) / len(words) >= overlap_threshold


def _normalize_for_overlap(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _public_item_to_text(item: Any) -> str:
    if isinstance(item, list):
        return " | ".join(_text(part) for part in item if _text(part))
    if isinstance(item, Mapping):
        return json.dumps(item, ensure_ascii=False, sort_keys=True)
    return _text(item)


def _dedupe_texts(values: Any) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        text = _text(raw)
        key = text.lower()
        if text and key not in seen:
            seen.add(key)
            output.append(text)
    return output


def _dedupe_public_items(values: Any) -> list[Any]:
    seen: set[str] = set()
    output: list[Any] = []
    for item in values:
        if item in ("", None):
            continue
        key = (
            item.lower()
            if isinstance(item, str)
            else json.dumps(item, ensure_ascii=False, sort_keys=True)
        )
        if key not in seen:
            seen.add(key)
            output.append(item)
    return output


def _packet_cards_by_id(packet: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        _text(card.get("card_id")): _mapping(card)
        for card in (_mapping(raw) for raw in _list(packet.get("candidate_cards")))
        if _text(card.get("card_id"))
    }


def _allowed_affordance_ids_for_cards(
    card_ids: list[str],
    cards: Mapping[str, Mapping[str, Any]],
) -> set[str]:
    allowed: set[str] = set()
    for card_id in card_ids:
        card = cards.get(card_id)
        if card:
            allowed.update(_card_affordance_ids(card))
    return allowed


def _card_affordance_ids(card: Mapping[str, Any]) -> set[str]:
    grouped_ids = {
        _text(item.get("affordance_id"))
        for item in (_mapping(row) for row in _list(card.get("reviewed_affordance_cards")))
        if _text(item.get("affordance_id"))
    }
    if grouped_ids:
        return grouped_ids
    reviewed = _mapping(card.get("reviewed_affordance_fields"))
    return set(_strings(reviewed.get("affordance_ids")))


def _unknown_card_errors(
    prefix: str,
    card_ids: list[str],
    cards: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    unknown = sorted(set(card_ids) - set(cards))
    return [f"{prefix}.source_card_ids contains unknown cards: {unknown}"] if unknown else []


def _has_private_mechanism_language(text: str) -> bool:
    return bool(
        re.search(
            r"\b(substrate|packet|ledger|affordance|model_id|mental model|review machinery)\b",
            text,
            flags=re.IGNORECASE,
        )
    )


def _text(value: Any) -> str:
    return str(value or "").strip()


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
