#!/usr/bin/env python3
"""Run a private exact-chunk v60 replay.

C4.4 isolates the retrieval question from the public-writing problem. It feeds
the decoder exact v60 affordance/absence chunks selected by the embedding lab
and asks only for a private consideration trace. No final answer, no judge, no
runtime integration.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_DIR = REPO_ROOT / "engine"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from scripts.run_v60_embedding_retrieval_lab import (  # noqa: E402
    build_case_embedding_text,
    build_v60_chunks,
)
from scripts.run_v60_transaction_paid_replay import (  # noqa: E402
    DEFAULT_GENERATOR_MODEL,
    ReplayCallError,
    call_openrouter_json,
    estimate_tokens,
)
from scripts.run_v60_transaction_replay_lab import (  # noqa: E402
    DEFAULT_AFFORDANCES_PATH,
    LAB_VERSION,
    RUNTIME_POLICY,
    STATUS,
    build_case_artifact,
    load_case_specs,
)
from scripts.run_v60_transaction_paid_replay import DEFAULT_CASE_MANIFEST  # noqa: E402


CHUNK_EXACT_REPLAY_VERSION = "v60_chunk_exact_private_replay.v1"
DEFAULT_EMBEDDING_SUMMARY = Path(
    "data/evaluations/v60_transaction_embedding_lab/"
    "2026-05-10-v60-embedding-pickup-absence-view/summary.json"
)
DEFAULT_OUTPUT_DIR = Path(
    "data/evaluations/v60_transaction_replay_lab/"
    "2026-05-10-c44-exact-chunk-private-replay"
)
ROUTES = frozenset(
    {
        "private_reasoning",
        "public_delta_candidate",
        "diagnostic_question_candidate",
        "evidence_gate",
        "guardrail",
        "defer_missing_evidence",
        "reject_irrelevant",
        "reject_duplicate",
    }
)
USEFULNESS = frozenset({"high", "medium", "low", "none"})
PACKET_USEFULNESS = frozenset({"useful", "mixed", "not_useful", "overfed", "underfed"})
ASSESSMENT_LEVELS = frozenset({"card", "chunk"})
CARD_SELECTED_OPPORTUNITY_MAX = 3
CHUNK_SELECTED_OPPORTUNITY_MAX = 5
ROLES = frozenset(
    {
        "frame_changer",
        "evidence_gate",
        "diagnostic_question",
        "guardrail",
        "tension_maker",
        "boundary_marker",
        "compression_aid",
        "rejection_aid",
        "absence_blocker",
        "none",
    }
)
EVIDENCE_STATUSES = frozenset(
    {"quoted_exact", "inferred_from_turn", "missing", "conflicting", "not_needed"}
)
BLOCKED_REASON_REQUIRED_ROUTES = frozenset(
    {"private_reasoning", "guardrail", "defer_missing_evidence", "reject_irrelevant", "reject_duplicate"}
)
PRIVATE_LANGUAGE = (
    "substrate",
    "packet",
    "card-",
    "affordance",
    "ledger",
    "v60",
    "mental model",
)


SYSTEM_PROMPT = """\
You are a private reasoning-substrate consideration router.

You receive exact v60 affordance and absence chunks selected for a case. These
chunks are private enrichment for a reasoning model. They are not instructions
to mention mental models, and they are not proof that a public answer should
change.

Your job:
- assess every chunk card;
- decide whether it was useful to consider;
- route it to private reasoning, public delta candidate, diagnostic question
  candidate, evidence gate, guardrail, deferral, rejection as irrelevant, or
  rejection as duplicate;
- preserve absence chunks as possible blockers;
- never manufacture usefulness just because a chunk was selected;
- do not write a final answer.

Return JSON only. Do not include markdown.
"""


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = REPO_ROOT
    manifest_path = resolve(root, args.case_manifest)
    affordances_path = resolve(root, args.affordances_path)
    embedding_summary_path = resolve(root, args.embedding_summary)
    output_dir = resolve(root, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if affordances_path.name != "affordances_v60.json":
        raise RuntimeError("This replay requires explicit affordances_v60.json")
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
    embedding_rows = {_text(row.get("case_id")): _mapping(row) for row in _list(embedding_summary.get("cases"))}

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
        prompt = build_prompt(
            case_artifact=case_artifact,
            packet=packet,
            assessment_level=args.assessment_level,
        )
        item_id = f"{case.file_stem}__private_trace"
        print(f"running {item_id}", flush=True)
        if args.dry_run:
            output = {
                "dry_run_placeholder": True,
                "item_id": item_id,
                "estimated_prompt_tokens": estimate_tokens(prompt),
            }
            validation = {"status": "not_run_dry_run"}
        else:
            try:
                output, meta = call_json_with_timeout(
                    api_key=api_key,
                    model=args.generator_model,
                    system_prompt=SYSTEM_PROMPT,
                    user_packet=prompt,
                    stage=f"{item_id}:private_trace",
                    timeout_seconds=args.call_timeout_seconds,
                )
            except ReplayCallError as exc:
                output = {
                    "status": "error",
                    "stage": exc.stage,
                    "error": str(exc),
                    "raw_content": exc.raw_content,
                }
                validation = {"status": "error", "error": str(exc)}
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
                output = {
                    "status": "error",
                    "stage": f"{item_id}:private_trace",
                    "error": error,
                    "raw_content": "",
                }
                validation = {"status": "error", "error": error}
            else:
                calls.append({"item_id": item_id, **meta})
                validation = validate_private_trace(
                    output,
                    packet=packet,
                    assessment_level=args.assessment_level,
                )
        print(f"finished {item_id}: {validation.get('status')}", flush=True)

        write_json(output_dir / "packets" / f"{case.file_stem}.json", packet)
        write_json(output_dir / "prompts" / f"{case.file_stem}.json", prompt)
        write_json(output_dir / "outputs" / f"{case.file_stem}.json", output)
        row = {
            "item_id": item_id,
            "case_id": case.case_id,
            "case_stem": case.file_stem,
            "status": "ok" if validation.get("status") != "error" else "error",
            "packet_card_count": len(_list(packet.get("chunk_cards"))),
            "selection_sources": dict(
                Counter(_text(card.get("selection_source")) for card in _list(packet.get("chunk_cards")))
            ),
            "model_ids": [_text(card.get("model_id")) for card in _list(packet.get("chunk_cards"))],
            "prompt_tokens_estimate": estimate_tokens(prompt),
            "validation": validation,
            "output_path": f"outputs/{case.file_stem}.json",
            "packet_path": f"packets/{case.file_stem}.json",
        }
        rows.append(row)

    summary = {
        "chunk_exact_replay_version": CHUNK_EXACT_REPLAY_VERSION,
        "lab_version": LAB_VERSION,
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "dry_run": bool(args.dry_run),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_manifest": str(manifest_path),
        "affordances_path": str(affordances_path),
        "embedding_summary": str(embedding_summary_path),
        "generator_model": "" if args.dry_run else args.generator_model,
        "assessment_level": args.assessment_level,
        "item_count": len(rows),
        "items": rows,
        "aggregate": aggregate(rows, calls, output_dir=output_dir),
        "call_records": calls,
    }
    write_json(output_dir / "summary.json", summary)
    (output_dir / "private_replay_report.md").write_text(render_report(summary), encoding="utf-8")
    print(f"wrote {output_dir / 'summary.json'}")
    print(f"wrote {output_dir / 'private_replay_report.md'}")
    return 0


def build_v60_index(payload: Mapping[str, Any]) -> dict[str, Any]:
    chunks = build_v60_chunks(payload)
    affordances = {
        _text(item.get("affordance_id")): _mapping(item)
        for item in _list(payload.get("affordances"))
        if _text(_mapping(item).get("affordance_id"))
    }
    absences = {
        f"{_text(item.get('model_id'))}::{_text(item.get('attempted_field'))}": _mapping(item)
        for item in _list(payload.get("absence_records"))
        if _text(_mapping(item).get("model_id")) and _text(_mapping(item).get("attempted_field"))
    }
    affordances_by_model: dict[str, list[Mapping[str, Any]]] = {}
    absences_by_model: dict[str, list[Mapping[str, Any]]] = {}
    for affordance in affordances.values():
        affordances_by_model.setdefault(_text(affordance.get("model_id")), []).append(affordance)
    for absence in absences.values():
        absences_by_model.setdefault(_text(absence.get("model_id")), []).append(absence)
    return {
        "chunks": {chunk.chunk_id: chunk for chunk in chunks},
        "affordances": affordances,
        "absences": absences,
        "affordances_by_model": affordances_by_model,
        "absences_by_model": absences_by_model,
    }


def build_exact_chunk_packet(
    *,
    case_id: str,
    case_stem: str,
    embedding_row: Mapping[str, Any],
    index: Mapping[str, Any],
) -> dict[str, Any]:
    selected: list[dict[str, Any]] = []
    selected_models: set[str] = set()
    top_embedding_by_model = {
        _text(item.get("model_id")): _mapping(item)
        for item in _list(embedding_row.get("top_embedding_models"))
    }
    top_absence_by_model = {
        _text(item.get("model_id")): _mapping(item)
        for item in _list(embedding_row.get("top_absence_models"))
    }

    def add_model(model_id: str, *, source: str, reason: str) -> None:
        if not model_id or model_id in selected_models or len(selected) >= 8:
            return
        selected_models.add(model_id)
        selected.append(
            build_exact_card(
                model_id=model_id,
                source=source,
                reason=reason,
                embedding_hit=top_embedding_by_model.get(model_id, {}),
                absence_hit=top_absence_by_model.get(model_id, {}),
                index=index,
                card_index=len(selected),
            )
        )

    for model_id in _list(embedding_row.get("lane_selected_cap8"))[:4]:
        add_model(
            _text(model_id),
            source="lane_preserved",
            reason="Preserve high-provenance lane candidate in exact-chunk test.",
        )

    before = len(selected)
    for row in (_mapping(item) for item in _list(embedding_row.get("top_embedding_models"))):
        if len(selected) >= before + 2:
            break
        add_model(
            _text(row.get("model_id")),
            source="embedding_affordance_exact",
            reason="Add exact embedding-selected affordance chunk as low-trust recall.",
        )

    before = len(selected)
    for row in (_mapping(item) for item in _list(embedding_row.get("top_absence_models"))):
        if len(selected) >= before + 1:
            break
        add_model(
            _text(row.get("model_id")),
            source="embedding_absence_exact",
            reason="Add exact embedding-selected absence chunk as blocker/guardrail recall.",
        )

    before = len(selected)
    for model_id in _list(embedding_row.get("hybrid_rrf_top8")):
        if len(selected) >= before + 1:
            break
        add_model(
            _text(model_id),
            source="hybrid_rrf_exact",
            reason="Add hybrid lane-plus-embedding candidate.",
        )

    for source_key, source, reason in [
        ("top_embedding_models", "embedding_affordance_fill", "Fill from embedding affordance rank."),
        ("top_absence_models", "embedding_absence_fill", "Fill from absence rank."),
        ("lane_selected_cap8", "lane_fill", "Fill from lane-selected rank."),
    ]:
        rows = _list(embedding_row.get(source_key))
        values = [_text(item.get("model_id")) for item in rows] if rows and isinstance(rows[0], Mapping) else [_text(item) for item in rows]
        for model_id in values:
            add_model(model_id, source=source, reason=reason)
            if len(selected) >= 8:
                break
        if len(selected) >= 8:
            break

    return {
        "packet_version": "v60_exact_chunk_packet.v1",
        "packet_id": f"c44-exact-{case_stem}",
        "status": STATUS,
        "runtime_policy": RUNTIME_POLICY,
        "transaction_context": {
            "case_id": case_id,
            "case_stem": case_stem,
            "chunk_exact_replay_version": CHUNK_EXACT_REPLAY_VERSION,
            "selection_policy": "4 lane + 2 exact embedding affordance + 1 exact absence + 1 hybrid/fill",
        },
        "packet_policy": {
            "semantic_selection_role": "llm_or_reviewer",
            "deterministic_role": "preserve_exact_chunk_identity_and_validate_trace",
            "forbid_public_copy": True,
            "forbid_final_answer_generation": True,
        },
        "chunk_cards": selected,
    }


def build_exact_card(
    *,
    model_id: str,
    source: str,
    reason: str,
    embedding_hit: Mapping[str, Any],
    absence_hit: Mapping[str, Any],
    index: Mapping[str, Any],
    card_index: int,
) -> dict[str, Any]:
    affordance_ids: list[str] = []
    absence_fields: list[str] = []
    if _text(embedding_hit.get("best_affordance_id")):
        affordance_ids.append(_text(embedding_hit.get("best_affordance_id")))
    if _text(absence_hit.get("best_absence_field")):
        absence_fields.append(_text(absence_hit.get("best_absence_field")))

    if not affordance_ids:
        for affordance in _list(_mapping(index.get("affordances_by_model")).get(model_id))[:1]:
            affordance_ids.append(_text(_mapping(affordance).get("affordance_id")))
    if not absence_fields:
        for absence in _list(_mapping(index.get("absences_by_model")).get(model_id))[:1]:
            absence_fields.append(_text(_mapping(absence).get("attempted_field")))

    affordances = [
        compact_affordance(_mapping(_mapping(index.get("affordances")).get(affordance_id)))
        for affordance_id in affordance_ids
        if _mapping(_mapping(index.get("affordances")).get(affordance_id))
    ]
    absences = [
        compact_absence(_mapping(_mapping(index.get("absences")).get(f"{model_id}::{field}")))
        for field in absence_fields
        if _mapping(_mapping(index.get("absences")).get(f"{model_id}::{field}"))
    ]
    return {
        "card_id": f"card-{card_index + 1:03d}-{model_id}",
        "model_id": model_id,
        "selection_source": source,
        "selection_reason": reason,
        "retrieval_trace": {
            "embedding_best_chunk_id": _text(embedding_hit.get("best_chunk_id")),
            "embedding_score": embedding_hit.get("score"),
            "absence_best_chunk_id": _text(absence_hit.get("best_chunk_id")),
            "absence_score": absence_hit.get("score"),
        },
        "selected_affordance_cards": affordances,
        "selected_absence_records": absences,
        "llm_instruction": (
            "Consider, reject, defer, or keep private. Do not force use. "
            "Absence records are blockers, not affordances."
        ),
    }


def compact_affordance(affordance: Mapping[str, Any]) -> dict[str, Any]:
    activation = _mapping(affordance.get("activation_shape"))
    return {
        "chunk_id": f"aff::{_text(affordance.get('affordance_id'))}",
        "affordance_id": _text(affordance.get("affordance_id")),
        "status": _text(affordance.get("status")),
        "confidence": _text(affordance.get("confidence")),
        "mechanism": _text(affordance.get("mechanism")),
        "activation_shape": {
            "use_when": _strings(activation.get("use_when"))[:3],
            "case_evidence_needed": _strings(activation.get("case_evidence_needed"))[:3],
            "do_not_use_when": _strings(activation.get("do_not_use_when"))[:3],
        },
        "diagnostic_questions": _strings(affordance.get("diagnostic_questions"))[:3],
        "misuse_guards": _strings(affordance.get("misuse_guards"))[:3],
        "source_evidence": [
            {
                "source_file": _text(item.get("source_file")),
                "source_quote": _text(item.get("source_quote")),
            }
            for item in (_mapping(row) for row in _list(affordance.get("source_evidence"))[:2])
        ],
    }


def compact_absence(absence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "chunk_id": f"abs::{_text(absence.get('model_id'))}::{_text(absence.get('attempted_field'))}",
        "attempted_field": _text(absence.get("attempted_field")),
        "status": _text(absence.get("status")),
        "reason": _text(absence.get("reason")),
        "runtime_policy": _text(absence.get("runtime_policy")),
        "source_evidence": [
            {
                "source_file": _text(item.get("source_file")),
                "source_quote": _text(item.get("source_quote")),
            }
            for item in (_mapping(row) for row in _list(absence.get("source_evidence"))[:2])
        ],
    }


def build_prompt(
    *,
    case_artifact: Mapping[str, Any],
    packet: Mapping[str, Any],
    assessment_level: str = "card",
) -> dict[str, Any]:
    if assessment_level not in ASSESSMENT_LEVELS:
        raise ValueError(f"unsupported assessment_level: {assessment_level}")
    output_contract = (
        build_chunk_output_contract() if assessment_level == "chunk" else build_card_output_contract()
    )
    return {
        "case_id": _text(case_artifact.get("case_id")),
        "query": _text(case_artifact.get("query")),
        "case_retrieval_text": build_case_embedding_text(case_artifact),
        "conversation_excerpt": _text(case_artifact.get("conversation_excerpt"))[:10000],
        "vanilla_answer": _text(case_artifact.get("vanilla_answer"))[:7000],
        "exact_v60_packet": packet,
        "assessment_level": assessment_level,
        "output_contract": output_contract,
    }


def build_card_output_contract() -> dict[str, Any]:
    return {
        "packet_usefulness": "useful | mixed | not_useful | overfed | underfed",
        "chunk_assessments": [
            {
                "card_id": "must match exact_v60_packet.chunk_cards[*].card_id",
                "model_id": "must match packet card",
                "selected_chunk_ids_considered": [
                    "chunk IDs present on that card only"
                ],
                "usefulness_to_consider": "high | medium | low | none",
                "opportunity_role": (
                    "frame_changer | evidence_gate | diagnostic_question | guardrail | "
                        "tension_maker | boundary_marker | compression_aid | rejection_aid | "
                        "absence_blocker | none"
                ),
                "route": (
                    "private_reasoning | public_delta_candidate | "
                    "diagnostic_question_candidate | evidence_gate | guardrail | "
                    "defer_missing_evidence | reject_irrelevant | reject_duplicate"
                ),
                "evidence_status": (
                    "quoted_exact | inferred_from_turn | missing | conflicting | not_needed"
                ),
                "what_it_helped_notice": "private reasoning effect or empty",
                "why_not_used_publicly_or_why_blocked": (
                    "required unless route is public_delta_candidate"
                ),
                "risk_if_forced": "risk of forcing this card into public reasoning",
            }
        ],
        "selected_opportunities": [
            {
                "opportunity_id": "stable short ID",
                "route": (
                    "public_delta_candidate | diagnostic_question_candidate | "
                    "evidence_gate | guardrail | private_reasoning"
                ),
                "source_card_ids": ["packet card IDs"],
                "private_value": "why this was worth considering",
                "public_candidate": (
                    "empty unless this could become public after deterministic composition"
                ),
                "public_admission_risk": "why public composition may reject it",
            }
        ],
        "retrieval_feedback": [
            "what exact chunk was missing, redundant, too broad, or surprisingly useful"
        ],
        "no_public_delta_reason": "required if no selected opportunity is public_delta_candidate",
    }


def build_chunk_output_contract() -> dict[str, Any]:
    return {
        "packet_usefulness": "useful | mixed | not_useful | overfed | underfed",
        "assessment_rule": (
            "Return exactly one chunk_assessments item for every selected affordance "
            "and absence chunk_id inside exact_v60_packet.chunk_cards. If a chunk is "
            "irrelevant, still include it with route reject_irrelevant, "
            "usefulness_to_consider low or none, and opportunity_role none."
        ),
        "chunk_assessments": [
            {
                "chunk_id": (
                    "must match exactly one selected affordance or absence chunk_id "
                    "inside exact_v60_packet.chunk_cards"
                ),
                "card_id": "parent card_id for this chunk",
                "model_id": "parent model_id for this chunk",
                "usefulness_to_consider": "high | medium | low | none",
                "opportunity_role": (
                    "frame_changer | evidence_gate | diagnostic_question | guardrail | "
                    "tension_maker | boundary_marker | compression_aid | rejection_aid | "
                    "absence_blocker | none"
                ),
                "route": (
                    "private_reasoning | public_delta_candidate | "
                    "diagnostic_question_candidate | evidence_gate | guardrail | "
                    "defer_missing_evidence | reject_irrelevant | reject_duplicate"
                ),
                "evidence_status": (
                    "quoted_exact | inferred_from_turn | missing | conflicting | not_needed"
                ),
                "what_it_helped_notice": "private reasoning effect or empty",
                "why_not_used_publicly_or_why_blocked": (
                    "required unless route is public_delta_candidate"
                ),
                "risk_if_forced": "risk of forcing this exact chunk into public reasoning",
            }
        ],
        "selected_opportunities": [
            {
                "opportunity_id": "stable short ID",
                "route": (
                    "public_delta_candidate | diagnostic_question_candidate | "
                    "evidence_gate | guardrail | private_reasoning"
                ),
                "source_chunk_ids": ["exact chunk IDs that generated this opportunity"],
                "source_card_ids": ["parent packet card IDs"],
                "private_value": "why this was worth considering",
                "public_candidate": (
                    "empty unless this could become public after deterministic composition"
                ),
                "public_admission_risk": "why public composition may reject it",
            }
        ],
        "retrieval_feedback": [
            "what exact chunk was missing, redundant, too broad, or surprisingly useful"
        ],
        "no_public_delta_reason": "required if no selected opportunity is public_delta_candidate",
    }


def validate_private_trace(
    payload: Mapping[str, Any],
    *,
    packet: Mapping[str, Any],
    assessment_level: str = "card",
) -> dict[str, Any]:
    if assessment_level == "chunk":
        return validate_private_chunk_trace(payload, packet=packet)
    errors: list[str] = []
    cards = {
        _text(card.get("card_id")): _mapping(card)
        for card in _list(packet.get("chunk_cards"))
        if _text(_mapping(card).get("card_id"))
    }
    packet_usefulness = _text(payload.get("packet_usefulness"))
    if packet_usefulness not in PACKET_USEFULNESS:
        errors.append("packet_usefulness is invalid")
    assessments = [_mapping(item) for item in _list(payload.get("chunk_assessments"))]
    if not isinstance(payload.get("chunk_assessments"), list):
        errors.append("chunk_assessments must be a list")
    assessment_ids = [_text(item.get("card_id")) for item in assessments]
    missing = sorted(set(cards) - set(assessment_ids))
    unknown = sorted(set(assessment_ids) - set(cards))
    duplicate = sorted(card_id for card_id, count in Counter(assessment_ids).items() if count > 1)
    if missing:
        errors.append(f"chunk_assessments missing card IDs: {missing}")
    if unknown:
        errors.append(f"chunk_assessments contains unknown card IDs: {unknown}")
    if duplicate:
        errors.append(f"chunk_assessments duplicates card IDs: {duplicate}")

    routes = Counter()
    usefulness = Counter()
    for index, assessment in enumerate(assessments):
        prefix = f"chunk_assessments[{index}]"
        card = cards.get(_text(assessment.get("card_id")), {})
        if card and _text(assessment.get("model_id")) != _text(card.get("model_id")):
            errors.append(f"{prefix}.model_id must match packet card")
        usefulness_value = _text(assessment.get("usefulness_to_consider"))
        if usefulness_value not in USEFULNESS:
            errors.append(f"{prefix}.usefulness_to_consider is invalid")
        usefulness[usefulness_value] += 1
        role = _text(assessment.get("opportunity_role"))
        if role not in ROLES:
            errors.append(f"{prefix}.opportunity_role is invalid")
        route = _text(assessment.get("route"))
        routes[route] += 1
        if route not in ROUTES:
            errors.append(f"{prefix}.route is invalid")
        if route in BLOCKED_REASON_REQUIRED_ROUTES and not _text(
            assessment.get("why_not_used_publicly_or_why_blocked")
        ):
            errors.append(f"{prefix}.why_not_used_publicly_or_why_blocked is required")
        if _text(assessment.get("evidence_status")) not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status is invalid")
        allowed_chunk_ids = card_chunk_ids(card)
        unknown_chunks = sorted(
            set(_strings(assessment.get("selected_chunk_ids_considered"))) - allowed_chunk_ids
        )
        if unknown_chunks:
            errors.append(f"{prefix}.selected_chunk_ids_considered unknown: {unknown_chunks}")

    selected = validate_selected_opportunities(
        payload,
        errors=errors,
        cards=cards,
        chunks={},
        max_items=CARD_SELECTED_OPPORTUNITY_MAX,
        require_chunk_sources=False,
    )

    selected_public_candidate_count = sum(
        1
        for opportunity in selected
        if _text(opportunity.get("route")) == "public_delta_candidate"
        or _text(opportunity.get("public_candidate"))
    )
    if selected_public_candidate_count == 0 and not _text(payload.get("no_public_delta_reason")):
        errors.append("no_public_delta_reason is required with no public candidates")

    status = "invalid" if errors else "valid"
    result = {
        "status": status,
        "assessment_count": len(assessments),
        "selected_opportunity_count": len(selected),
        "packet_usefulness": packet_usefulness,
        "route_counts": dict(sorted((key, value) for key, value in routes.items() if key)),
        "usefulness_counts": dict(sorted((key, value) for key, value in usefulness.items() if key)),
    }
    if errors:
        result["errors"] = errors
    return result


def call_json_with_timeout(
    *,
    api_key: str,
    model: str,
    system_prompt: str,
    user_packet: Mapping[str, Any],
    stage: str,
    timeout_seconds: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if timeout_seconds <= 0:
        return call_openrouter_json(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_packet=user_packet,
            stage=stage,
        )

    def handle_timeout(_signum: int, _frame: Any) -> None:
        raise TimeoutError(f"local call timeout after {timeout_seconds}s at {stage}")

    previous_handler = signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(timeout_seconds)
    try:
        return call_openrouter_json(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_packet=user_packet,
            stage=stage,
        )
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


def validate_private_chunk_trace(payload: Mapping[str, Any], *, packet: Mapping[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    cards = {
        _text(card.get("card_id")): _mapping(card)
        for card in _list(packet.get("chunk_cards"))
        if _text(_mapping(card).get("card_id"))
    }
    chunks = packet_chunk_index(packet)
    packet_usefulness = _text(payload.get("packet_usefulness"))
    if packet_usefulness not in PACKET_USEFULNESS:
        errors.append("packet_usefulness is invalid")
    assessments = [_mapping(item) for item in _list(payload.get("chunk_assessments"))]
    if not isinstance(payload.get("chunk_assessments"), list):
        errors.append("chunk_assessments must be a list")

    assessment_ids = [_text(item.get("chunk_id")) for item in assessments]
    missing = sorted(set(chunks) - set(assessment_ids))
    unknown = sorted(set(assessment_ids) - set(chunks))
    duplicate = sorted(chunk_id for chunk_id, count in Counter(assessment_ids).items() if count > 1)
    if missing:
        errors.append(f"chunk_assessments missing chunk IDs: {missing}")
    if unknown:
        errors.append(f"chunk_assessments contains unknown chunk IDs: {unknown}")
    if duplicate:
        errors.append(f"chunk_assessments duplicates chunk IDs: {duplicate}")

    routes = Counter()
    usefulness = Counter()
    for index, assessment in enumerate(assessments):
        prefix = f"chunk_assessments[{index}]"
        chunk = chunks.get(_text(assessment.get("chunk_id")), {})
        if chunk and _text(assessment.get("card_id")) != _text(chunk.get("card_id")):
            errors.append(f"{prefix}.card_id must match parent packet card")
        if chunk and _text(assessment.get("model_id")) != _text(chunk.get("model_id")):
            errors.append(f"{prefix}.model_id must match parent packet card")
        usefulness_value = _text(assessment.get("usefulness_to_consider"))
        if usefulness_value not in USEFULNESS:
            errors.append(f"{prefix}.usefulness_to_consider is invalid")
        usefulness[usefulness_value] += 1
        role = _text(assessment.get("opportunity_role"))
        if role not in ROLES:
            errors.append(f"{prefix}.opportunity_role is invalid")
        route = _text(assessment.get("route"))
        routes[route] += 1
        if route not in ROUTES:
            errors.append(f"{prefix}.route is invalid")
        if route in BLOCKED_REASON_REQUIRED_ROUTES and not _text(
            assessment.get("why_not_used_publicly_or_why_blocked")
        ):
            errors.append(f"{prefix}.why_not_used_publicly_or_why_blocked is required")
        if _text(assessment.get("evidence_status")) not in EVIDENCE_STATUSES:
            errors.append(f"{prefix}.evidence_status is invalid")

    selected = validate_selected_opportunities(
        payload,
        errors=errors,
        cards=cards,
        chunks=chunks,
        max_items=CHUNK_SELECTED_OPPORTUNITY_MAX,
        require_chunk_sources=True,
    )

    selected_public_candidate_count = sum(
        1
        for opportunity in selected
        if _text(opportunity.get("route")) == "public_delta_candidate"
        or _text(opportunity.get("public_candidate"))
    )
    if selected_public_candidate_count == 0 and not _text(payload.get("no_public_delta_reason")):
        errors.append("no_public_delta_reason is required with no public candidates")

    status = "invalid" if errors else "valid"
    result = {
        "status": status,
        "assessment_level": "chunk",
        "assessment_count": len(assessments),
        "selected_opportunity_count": len(selected),
        "packet_usefulness": packet_usefulness,
        "route_counts": dict(sorted((key, value) for key, value in routes.items() if key)),
        "usefulness_counts": dict(sorted((key, value) for key, value in usefulness.items() if key)),
    }
    if errors:
        result["errors"] = errors
    return result


def validate_selected_opportunities(
    payload: Mapping[str, Any],
    *,
    errors: list[str],
    cards: Mapping[str, Any],
    chunks: Mapping[str, Any],
    max_items: int,
    require_chunk_sources: bool,
) -> list[Mapping[str, Any]]:
    selected = [_mapping(item) for item in _list(payload.get("selected_opportunities"))]
    if len(selected) > max_items:
        errors.append(f"selected_opportunities allows at most {max_items} items")
    for index, opportunity in enumerate(selected):
        prefix = f"selected_opportunities[{index}]"
        route = _text(opportunity.get("route"))
        if route not in {
            "public_delta_candidate",
            "diagnostic_question_candidate",
            "evidence_gate",
            "guardrail",
            "private_reasoning",
        }:
            errors.append(f"{prefix}.route is invalid")
        source_ids = _strings(opportunity.get("source_card_ids"))
        if not source_ids:
            errors.append(f"{prefix}.source_card_ids is required")
        unknown_sources = sorted(set(source_ids) - set(cards))
        if unknown_sources:
            errors.append(f"{prefix}.source_card_ids unknown: {unknown_sources}")
        chunk_ids = _strings(opportunity.get("source_chunk_ids"))
        if require_chunk_sources and not chunk_ids:
            errors.append(f"{prefix}.source_chunk_ids is required")
        unknown_chunks = sorted(set(chunk_ids) - set(chunks))
        if unknown_chunks:
            errors.append(f"{prefix}.source_chunk_ids unknown: {unknown_chunks}")
        if not _text(opportunity.get("private_value")):
            errors.append(f"{prefix}.private_value is required")
        public_candidate = _text(opportunity.get("public_candidate"))
        if public_candidate and has_private_language(public_candidate):
            errors.append(f"{prefix}.public_candidate leaks private language")
    return selected


def card_chunk_ids(card: Mapping[str, Any]) -> set[str]:
    ids = set()
    for affordance in (_mapping(item) for item in _list(card.get("selected_affordance_cards"))):
        ids.add(_text(affordance.get("chunk_id")))
    for absence in (_mapping(item) for item in _list(card.get("selected_absence_records"))):
        ids.add(_text(absence.get("chunk_id")))
    return {item for item in ids if item}


def packet_chunk_index(packet: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    chunks: dict[str, dict[str, str]] = {}
    for card in (_mapping(item) for item in _list(packet.get("chunk_cards"))):
        card_id = _text(card.get("card_id"))
        model_id = _text(card.get("model_id"))
        for affordance in (_mapping(item) for item in _list(card.get("selected_affordance_cards"))):
            chunk_id = _text(affordance.get("chunk_id"))
            if chunk_id:
                chunks[chunk_id] = {
                    "card_id": card_id,
                    "model_id": model_id,
                    "chunk_kind": "affordance",
                }
        for absence in (_mapping(item) for item in _list(card.get("selected_absence_records"))):
            chunk_id = _text(absence.get("chunk_id"))
            if chunk_id:
                chunks[chunk_id] = {
                    "card_id": card_id,
                    "model_id": model_id,
                    "chunk_kind": "absence",
                }
    return chunks


def has_private_language(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in PRIVATE_LANGUAGE)


def aggregate(
    rows: list[Mapping[str, Any]],
    calls: list[Mapping[str, Any]],
    *,
    output_dir: Path,
) -> dict[str, Any]:
    validation_counts = Counter(_text(_mapping(row.get("validation")).get("status")) for row in rows)
    packet_usefulness = Counter(
        _text(_mapping(row.get("validation")).get("packet_usefulness")) for row in rows
    )
    route_counts: Counter[str] = Counter()
    usefulness_counts: Counter[str] = Counter()
    for row in rows:
        validation = _mapping(row.get("validation"))
        route_counts.update(_mapping(validation.get("route_counts")))
        usefulness_counts.update(_mapping(validation.get("usefulness_counts")))
    return {
        "validation_counts": dict(sorted((k, v) for k, v in validation_counts.items() if k)),
        "packet_usefulness_counts": dict(sorted((k, v) for k, v in packet_usefulness.items() if k)),
        "route_counts": dict(sorted(route_counts.items())),
        "usefulness_counts": dict(sorted(usefulness_counts.items())),
        "call_count": len(calls),
        "input_tokens": sum(_int(record.get("input_tokens")) for record in calls),
        "output_tokens": sum(_int(record.get("output_tokens")) for record in calls),
        "total_tokens": sum(_int(record.get("total_tokens")) for record in calls),
        "cost_usd": round(sum(float(record.get("cost_usd") or 0.0) for record in calls), 6),
    }


def render_report(summary: Mapping[str, Any]) -> str:
    aggregate_payload = _mapping(summary.get("aggregate"))
    lines = [
        "# V60 Exact-Chunk Private Replay Report",
        "",
        f"Date: {_text(summary.get('generated_at'))[:10]}",
        "Status: dormant private replay evidence only",
        f"Generator: `{_text(summary.get('generator_model')) or 'not run'}`",
        "",
        "## Aggregate",
        "",
        f"- Items: {_int(summary.get('item_count'))}",
        f"- Assessment level: `{_text(summary.get('assessment_level')) or 'card'}`",
        f"- Paid calls: {_int(aggregate_payload.get('call_count'))}",
        f"- Estimated reported cost: `${aggregate_payload.get('cost_usd', 0)}`",
        f"- Validation: `{json.dumps(_mapping(aggregate_payload.get('validation_counts')), sort_keys=True)}`",
        f"- Packet usefulness: `{json.dumps(_mapping(aggregate_payload.get('packet_usefulness_counts')), sort_keys=True)}`",
        f"- Routes: `{json.dumps(_mapping(aggregate_payload.get('route_counts')), sort_keys=True)}`",
        f"- Usefulness: `{json.dumps(_mapping(aggregate_payload.get('usefulness_counts')), sort_keys=True)}`",
        "",
        "## Items",
        "",
        "| Item | Cards | Sources | Validation | Packet Usefulness |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in (_mapping(item) for item in _list(summary.get("items"))):
        validation = _mapping(row.get("validation"))
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_text(row.get('item_id'))}`",
                    str(_int(row.get("packet_card_count"))),
                    f"`{json.dumps(_mapping(row.get('selection_sources')), sort_keys=True)}`",
                    f"`{_text(validation.get('status'))}`",
                    f"`{_text(validation.get('packet_usefulness'))}`",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "This run tests exact v60 chunk consideration only. It intentionally",
            "does not ask for a final answer, judge comparison, or product-facing",
            "copy. Treat public candidates as private composer inputs, not user",
            "text.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-manifest", type=Path, default=DEFAULT_CASE_MANIFEST)
    parser.add_argument("--affordances-path", type=Path, default=DEFAULT_AFFORDANCES_PATH)
    parser.add_argument("--embedding-summary", type=Path, default=DEFAULT_EMBEDDING_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--generator-model", default=DEFAULT_GENERATOR_MODEL)
    parser.add_argument("--assessment-level", choices=sorted(ASSESSMENT_LEVELS), default="card")
    parser.add_argument("--call-timeout-seconds", type=int, default=300)
    parser.add_argument("--cases", nargs="*", default=[])
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
