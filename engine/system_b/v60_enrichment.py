from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
import logging
from pathlib import Path
from typing import Any, Mapping, Sequence

from .conversation_context import ConversationContext

_LOGGER = logging.getLogger("system_b.v60_enrichment")


SCHEMA_VERSION = "v60_runtime_enrichment.v1"
LEDGER_SCHEMA_VERSION = "v60_skill_consideration_ledger.v1"
RUNTIME_POLICY = "private_skill_enrichment"
DEFAULT_MAX_CARDS = 8
DEFAULT_LANE_SLOTS = 4
DEFAULT_EMBEDDING_AFFORDANCE_SLOTS = 2
DEFAULT_EMBEDDING_ABSENCE_SLOTS = 1
DEFAULT_HYBRID_SLOTS = 1
DEFAULT_SNIPPET_CAP = 2

DISPOSITIONS = frozenset({"used", "rejected", "deferred", "not_considered"})
ROUTES = frozenset(
    {
        "updated_position",
        "pressure_check",
        "private_guardrail",
        "evidence_gate",
        "diagnostic_question",
        "set_aside",
        "already_covered",
        "irrelevant",
        "missing_evidence",
        "duplicate",
    }
)


@dataclass(frozen=True)
class V60Candidate:
    model_id: str
    source: str
    lane_order: int
    reason: str = ""
    evidence: str = ""
    route_or_artifact_id: str = ""
    score: float | None = None


def build_v60_enrichment(
    *,
    root: Path,
    result_payload: Mapping[str, Any],
    conversation_context: ConversationContext,
    affordances_path: Path,
    embedding_retriever: Any = None,
    embedding_api_key: str = "",
    enable_embeddings: bool = True,
    max_cards: int = DEFAULT_MAX_CARDS,
    lane_slots: int = DEFAULT_LANE_SLOTS,
    embedding_affordance_slots: int = DEFAULT_EMBEDDING_AFFORDANCE_SLOTS,
    embedding_absence_slots: int = DEFAULT_EMBEDDING_ABSENCE_SLOTS,
    hybrid_slots: int = DEFAULT_HYBRID_SLOTS,
    snippet_cap: int = DEFAULT_SNIPPET_CAP,
) -> dict[str, Any]:
    """Build the private v60 enrichment block attached to result.json.

    This is a product-runtime transport layer, not a final-answer selector. The
    deterministic side preserves candidates, caps, source custody, selected
    chunks, and skipped material; the skill-using LLM decides whether each
    chunk matters in the current conversation.
    """

    root = Path(root)
    affordances_path = Path(affordances_path)
    payload = _load_json(affordances_path)
    artifact_id = _text(payload.get("artifact"))
    artifact_status = _text(payload.get("status"))
    if affordances_path.name != "affordances_v60.json" or artifact_id != "model_affordances_v60":
        raise ValueError("v60 enrichment requires explicit affordances_v60.json")

    records_by_model = {
        _text(record.get("model_id")): _mapping(record)
        for record in _list(payload.get("model_records"))
        if _text(_mapping(record).get("model_id"))
    }
    graph_names = _load_graph_display_names(root)

    raw_candidates = extract_v60_candidates(result_payload)
    merged_candidates = merge_candidates(raw_candidates)
    lane_rank = [candidate.model_id for candidate in merged_candidates]

    embedding_rows, embedding_mode, embedding_error = _embedding_model_hits(
        conversation_context=conversation_context,
        result_payload=result_payload,
        embedding_retriever=embedding_retriever,
        embedding_api_key=embedding_api_key,
        enable_embeddings=enable_embeddings,
    )
    embedding_rank = [_text(row.get("model_id")) for row in embedding_rows]
    hybrid_rank = _hybrid_rrf_rank(lane_rank, embedding_rank)

    selected_specs: list[tuple[str, str, str, Mapping[str, Any]]] = []
    skipped: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_model(
        model_id: str,
        *,
        source: str,
        reason: str,
        retrieval: Mapping[str, Any] | None = None,
    ) -> None:
        mid = _slug(model_id)
        if not mid:
            return
        if mid not in records_by_model:
            skipped.append(
                {
                    "model_id": mid,
                    "source": source,
                    "reason": "missing_v60_record",
                    "stage": "selection",
                }
            )
            return
        if mid in seen:
            skipped.append(
                {
                    "model_id": mid,
                    "source": source,
                    "reason": "duplicate_model_id",
                    "stage": "selection",
                }
            )
            return
        if len(selected_specs) >= max_cards:
            skipped.append(
                {
                    "model_id": mid,
                    "source": source,
                    "reason": "packet_cap",
                    "stage": "selection",
                }
            )
            return
        seen.add(mid)
        selected_specs.append((mid, source, reason, retrieval or {}))

    lane_by_model = {candidate.model_id: candidate for candidate in merged_candidates}
    for candidate in merged_candidates[:lane_slots]:
        add_model(
            candidate.model_id,
            source="lane_preserved",
            reason=candidate.reason or "Preserve high-provenance lane candidate.",
            retrieval={},
        )

    embedding_by_model = {_text(row.get("model_id")): row for row in embedding_rows}
    before = len(selected_specs)
    for row in embedding_rows:
        if len(selected_specs) >= before + embedding_affordance_slots:
            break
        add_model(
            _text(row.get("model_id")),
            source="embedding_model_recall",
            reason="Add embedding-recalled model as low-trust semantic recall.",
            retrieval=row,
        )

    before = len(selected_specs)
    for row in embedding_rows:
        if len(selected_specs) >= before + embedding_absence_slots:
            break
        model_id = _text(row.get("model_id"))
        record = records_by_model.get(model_id) or {}
        if not _list(record.get("absence_records")):
            continue
        add_model(
            model_id,
            source="embedding_absence_reserved",
            reason="Reserve one embedding-recalled model with absence blockers.",
            retrieval=row,
        )

    before = len(selected_specs)
    for model_id in hybrid_rank:
        if len(selected_specs) >= before + hybrid_slots:
            break
        add_model(
            model_id,
            source="hybrid_rrf",
            reason="Add hybrid lane-plus-embedding model.",
            retrieval=embedding_by_model.get(model_id, {}),
        )

    for candidate in merged_candidates:
        if len(selected_specs) >= max_cards:
            skipped.append(
                {
                    "model_id": candidate.model_id,
                    "source": "lane_fill",
                    "reason": "not_presented_packet_cap",
                    "stage": "fill",
                }
            )
            continue
        add_model(
            candidate.model_id,
            source="lane_fill",
            reason=candidate.reason or "Fill remaining capacity from lane rank.",
            retrieval={},
        )

    if enable_embeddings:
        for row in embedding_rows:
            if len(selected_specs) >= max_cards:
                skipped.append(
                    {
                        "model_id": _text(row.get("model_id")),
                        "source": "embedding_fill",
                        "reason": "not_presented_packet_cap",
                        "stage": "fill",
                        "score": row.get("score"),
                    }
                )
                continue
            add_model(
                _text(row.get("model_id")),
                source="embedding_fill",
                reason="Fill remaining capacity from embedding rank.",
                retrieval=row,
            )

    cards: list[dict[str, Any]] = []
    for model_id, source, reason, retrieval in selected_specs:
        record = records_by_model.get(model_id)
        if record is None:
            skipped.append(
                {
                    "model_id": model_id,
                    "source": source,
                    "reason": "missing_v60_record",
                    "stage": "card_build",
                }
            )
            continue
        card = _build_card(
            model_id=model_id,
            display_name=graph_names.get(model_id, model_id),
            record=record,
            selection_source=source,
            selection_reason=reason,
            lane_candidate=lane_by_model.get(model_id),
            retrieval=retrieval,
            card_index=len(cards),
            snippet_cap=snippet_cap,
        )
        if not card["selected_affordance_cards"] and not card["selected_absence_records"]:
            skipped.append(
                {
                    "model_id": model_id,
                    "source": source,
                    "reason": "no_v60_chunks_available",
                    "stage": "card_build",
                }
            )
            continue
        cards.append(card)

    selected_chunk_ids = _selected_chunk_ids(cards)
    selection_counts = Counter(_text(card.get("selection_source")) for card in cards)
    lane_sources = Counter(candidate.source for candidate in raw_candidates)

    not_presented_models = sorted(
        {
            _text(item.get("model_id"))
            for item in skipped
            if _text(item.get("reason")) in {"packet_cap", "not_presented_packet_cap"}
        }
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "active",
        "runtime_policy": RUNTIME_POLICY,
        "artifact": {
            "artifact_id": artifact_id,
            "status": artifact_status,
            "path": str(affordances_path),
            "sha256": _file_sha256(affordances_path),
            "model_record_count": len(records_by_model),
            "affordance_count": len(_list(payload.get("affordances"))),
            "absence_record_count": len(_list(payload.get("absence_records"))),
        },
        "selection_policy": {
            "max_cards": max_cards,
            "lane_slots": lane_slots,
            "embedding_affordance_slots": embedding_affordance_slots,
            "embedding_absence_slots": embedding_absence_slots,
            "hybrid_slots": hybrid_slots,
            "snippet_cap": snippet_cap,
            "affordance_selection": "record_order_first",
            "absence_selection": "record_order_first",
        },
        "candidate_pool": {
            "lane_candidate_count": len(merged_candidates),
            "raw_lane_signal_count": len(raw_candidates),
            "lane_source_counts": dict(sorted(lane_sources.items())),
            "lane_candidates": [_candidate_payload(candidate) for candidate in merged_candidates],
            "embedding_mode": embedding_mode,
            "embedding_error": embedding_error,
            "embedding_model_hits": embedding_rows,
            "hybrid_rrf_rank": hybrid_rank[:max_cards],
        },
        "selected_cards": cards,
        "telemetry": {
            "selected_card_count": len(cards),
            "selected_model_ids": [_text(card.get("model_id")) for card in cards],
            "selected_chunk_ids": selected_chunk_ids,
            "selected_chunk_count": len(selected_chunk_ids),
            "selection_source_counts": dict(sorted(selection_counts.items())),
            "skipped_candidates": skipped,
            "skipped_candidate_count": len(skipped),
            "not_presented_model_ids": not_presented_models,
            "not_presented_candidate_count": len(not_presented_models),
            "consideration_ledger_expected": True,
        },
        "llm_instruction": (
            "Private only. Consider each selected chunk seriously, but do not "
            "force use. Use, reject, defer, or keep as a guardrail. Do not "
            "mention v60, affordances, packets, cards, ledgers, or internal IDs "
            "in user-facing prose."
        ),
        "expected_ledger_schema": {
            "schema_version": LEDGER_SCHEMA_VERSION,
            "transactions": [
                {
                    "chunk_id": "must match selected chunk id",
                    "card_id": "parent card id",
                    "model_id": "parent model id",
                    "disposition": "used | rejected | deferred | not_considered",
                    "route": "updated_position | pressure_check | private_guardrail | evidence_gate | diagnostic_question | set_aside | already_covered | irrelevant | missing_evidence | duplicate",
                    "strongest_plausible_application": "best honest way the chunk could apply",
                    "risk_if_forced": "required for rejected/deferred/not_considered chunks",
                    "why": "short private rationale",
                    "visible_effect": "empty unless this changed user-facing prose",
                }
            ],
        },
    }


def disabled_v60_enrichment(reason: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "disabled",
        "runtime_policy": RUNTIME_POLICY,
        "reason": reason,
        "selected_cards": [],
        "telemetry": {
            "selected_card_count": 0,
            "selected_model_ids": [],
            "selected_chunk_ids": [],
            "selected_chunk_count": 0,
            "skipped_candidates": [],
            "not_presented_model_ids": [],
            "consideration_ledger_expected": False,
        },
    }


def error_v60_enrichment(error: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "skipped_error",
        "runtime_policy": RUNTIME_POLICY,
        "error": error,
        "selected_cards": [],
        "telemetry": {
            "selected_card_count": 0,
            "selected_model_ids": [],
            "selected_chunk_ids": [],
            "selected_chunk_count": 0,
            "skipped_candidates": [],
            "not_presented_model_ids": [],
            "consideration_ledger_expected": False,
        },
    }


def extract_v60_candidates(result_payload: Mapping[str, Any]) -> list[V60Candidate]:
    candidates: list[V60Candidate] = []
    delta = _mapping(result_payload.get("delta_card"))
    for model_id in _strings(delta.get("selected_model_ids")):
        candidates.append(
            V60Candidate(
                model_id=_slug(model_id),
                source="lane1_delta_selected",
                lane_order=1,
                reason="Lane 1 selected this model as structural pressure.",
            )
        )

    for finding in (_mapping(item) for item in _list(delta.get("findings")) + _list(delta.get("top_findings"))):
        finding_reason = _compact(
            " | ".join(
                part
                for part in [
                    _text(finding.get("tendency_id")),
                    _text(finding.get("sub_pattern")),
                    _text(finding.get("challenge_statement")),
                    _text(finding.get("next_move")),
                ]
                if part
            ),
            max_chars=400,
        )
        for field, source in (
            ("primary_model_id", "lane1_primary"),
            ("selected_model_ids", "lane1_selected"),
            ("supporting_model_ids", "lane1_supporting"),
            ("risk_model_ids", "lane1_risk"),
        ):
            values = [_text(finding.get(field))] if field == "primary_model_id" else _strings(finding.get(field))
            for model_id in values:
                candidates.append(
                    V60Candidate(
                        model_id=_slug(model_id),
                        source=source,
                        lane_order=1,
                        reason=finding_reason or f"Lane 1 finding field {field}.",
                        evidence=_text(finding.get("specific_passage")),
                        route_or_artifact_id=_text(finding.get("tendency_id")),
                    )
                )

    companion = _mapping(result_payload.get("companion_cheat_sheet"))
    for anchor in (_mapping(item) for item in _list(companion.get("anchors"))):
        candidates.append(
            V60Candidate(
                model_id=_slug(anchor.get("model_id")),
                source="lane2_companion_anchor",
                lane_order=2,
                reason=_text(anchor.get("presence_explanation")) or "Lane 2 final companion anchor.",
                evidence=_text(anchor.get("evidence_quote")),
            )
        )

    frame = _mapping(result_payload.get("frame_pressure_card"))
    for reframing in (_mapping(item) for item in _list(frame.get("reframings"))):
        candidates.append(
            V60Candidate(
                model_id=_slug(reframing.get("grounding_model")),
                source="lane3_reframing_grounding",
                lane_order=3,
                reason=_text(reframing.get("what_opens")) or _text(reframing.get("reframed_question")),
                route_or_artifact_id=str(reframing.get("source_element_index", "")),
            )
        )
    for route in (_mapping(item) for item in _list(frame.get("routes"))):
        for model_id in _strings(route.get("candidate_model_ids")):
            candidates.append(
                V60Candidate(
                    model_id=_slug(model_id),
                    source="lane3_frame_route_candidate",
                    lane_order=3,
                    reason=_text(route.get("frame_pattern")),
                    route_or_artifact_id=_text(route.get("frame_pattern")),
                )
            )

    coverage = _mapping(result_payload.get("structural_coverage_card"))
    for route in (_mapping(item) for item in _list(coverage.get("gap_routes"))):
        for model_id in _strings(route.get("candidate_model_ids")):
            candidates.append(
                V60Candidate(
                    model_id=_slug(model_id),
                    source="lane4_gap_route_candidate",
                    lane_order=4,
                    reason=_text(route.get("dimension_name")),
                    route_or_artifact_id=_text(route.get("dimension_id")),
                )
            )

    return [candidate for candidate in candidates if candidate.model_id]


def merge_candidates(candidates: Sequence[V60Candidate]) -> list[V60Candidate]:
    merged: dict[str, V60Candidate] = {}
    source_sets: dict[str, set[str]] = {}
    reason_sets: dict[str, list[str]] = {}
    evidence_sets: dict[str, list[str]] = {}
    first_index: dict[str, int] = {}

    for index, candidate in enumerate(candidates):
        if candidate.model_id not in merged:
            merged[candidate.model_id] = candidate
            source_sets[candidate.model_id] = set()
            reason_sets[candidate.model_id] = []
            evidence_sets[candidate.model_id] = []
            first_index[candidate.model_id] = index
        existing = merged[candidate.model_id]
        if candidate.lane_order < existing.lane_order:
            merged[candidate.model_id] = candidate
        source_sets[candidate.model_id].add(candidate.source)
        if candidate.reason and candidate.reason not in reason_sets[candidate.model_id]:
            reason_sets[candidate.model_id].append(candidate.reason)
        if candidate.evidence and candidate.evidence not in evidence_sets[candidate.model_id]:
            evidence_sets[candidate.model_id].append(candidate.evidence)

    rows = []
    for model_id, candidate in merged.items():
        rows.append(
            V60Candidate(
                model_id=model_id,
                source="+".join(sorted(source_sets[model_id])),
                lane_order=candidate.lane_order,
                reason=" | ".join(reason_sets[model_id][:3]),
                evidence=" | ".join(evidence_sets[model_id][:2]),
                route_or_artifact_id=candidate.route_or_artifact_id,
                score=candidate.score,
            )
        )
    rows.sort(key=lambda item: (item.lane_order, first_index[item.model_id], item.model_id))
    return rows


def validate_v60_consideration_ledger(
    ledger: Mapping[str, Any],
    *,
    enrichment: Mapping[str, Any],
) -> dict[str, Any]:
    errors: list[str] = []
    if _text(ledger.get("schema_version")) != LEDGER_SCHEMA_VERSION:
        errors.append("schema_version is invalid")
    selected_chunks = set(_strings(_mapping(enrichment.get("telemetry")).get("selected_chunk_ids")))
    transactions = [_mapping(item) for item in _list(ledger.get("transactions"))]
    if not isinstance(ledger.get("transactions"), list):
        errors.append("transactions must be a list")

    seen: list[str] = []
    for index, transaction in enumerate(transactions):
        prefix = f"transactions[{index}]"
        chunk_id = _text(transaction.get("chunk_id"))
        seen.append(chunk_id)
        if chunk_id not in selected_chunks:
            errors.append(f"{prefix}.chunk_id is unknown")
        if _text(transaction.get("disposition")) not in DISPOSITIONS:
            errors.append(f"{prefix}.disposition is invalid")
        if _text(transaction.get("route")) not in ROUTES:
            errors.append(f"{prefix}.route is invalid")
        if not _text(transaction.get("strongest_plausible_application")):
            errors.append(f"{prefix}.strongest_plausible_application is required")
        if _text(transaction.get("disposition")) in {"rejected", "deferred", "not_considered"}:
            if not _text(transaction.get("risk_if_forced")):
                errors.append(f"{prefix}.risk_if_forced is required for non-used chunks")
        if not _text(transaction.get("why")):
            errors.append(f"{prefix}.why is required")

    missing = sorted(selected_chunks - set(seen))
    duplicate = sorted(chunk_id for chunk_id, count in Counter(seen).items() if chunk_id and count > 1)
    if missing:
        errors.append(f"transactions missing selected chunk IDs: {missing}")
    if duplicate:
        errors.append(f"transactions duplicate chunk IDs: {duplicate}")

    disposition_counts = Counter(_text(item.get("disposition")) for item in transactions)
    return {
        "status": "invalid" if errors else "valid",
        "transaction_count": len(transactions),
        "selected_chunk_count": len(selected_chunks),
        "disposition_counts": dict(sorted((key, value) for key, value in disposition_counts.items() if key)),
        "used_chunk_ids": [
            _text(item.get("chunk_id"))
            for item in transactions
            if _text(item.get("disposition")) == "used"
        ],
        "presented_but_not_used_chunk_ids": [
            _text(item.get("chunk_id"))
            for item in transactions
            if _text(item.get("disposition")) in {"rejected", "deferred", "not_considered"}
        ],
        **({"errors": errors} if errors else {}),
    }


def _embedding_model_hits(
    *,
    conversation_context: ConversationContext,
    result_payload: Mapping[str, Any],
    embedding_retriever: Any,
    embedding_api_key: str,
    enable_embeddings: bool,
) -> tuple[list[dict[str, Any]], str, str]:
    if not enable_embeddings:
        return [], "off_config", ""
    if embedding_retriever is None:
        return [], "off_no_retriever", ""
    if not embedding_api_key:
        return [], "off_no_api_key", ""
    query_text = _build_query_text(conversation_context, result_payload)
    try:
        ranked = embedding_retriever.rank_models_expanded(query_text, embedding_api_key, top_k=24)
    except Exception as exc:
        _LOGGER.warning("v60 embedding model recall failed", exc_info=True)
        return [], "error", f"{type(exc).__name__}: {exc}"

    rows = []
    for index, row in enumerate(ranked, start=1):
        model_id = _slug(row.get("model_id"))
        if not model_id:
            continue
        rows.append(
            {
                "rank": index,
                "model_id": model_id,
                "score": row.get("score"),
                "signal_type": _text(row.get("signal_type")),
            }
        )
    return rows, "on", ""


def _build_query_text(
    conversation_context: ConversationContext,
    result_payload: Mapping[str, Any],
) -> str:
    ext = conversation_context.extraction
    user_turns = "\n\n".join(
        turn.text.strip()
        for turn in conversation_context.turns
        if turn.speaker == "user" and turn.text.strip()
    )
    assistant_turns = "\n\n".join(
        turn.text.strip()
        for turn in conversation_context.turns
        if turn.speaker == "assistant" and turn.text.strip()
    )
    delta = _mapping(result_payload.get("delta_card"))
    challenges = " | ".join(
        _text(item.get("challenge_statement"))
        for item in (_mapping(row) for row in _list(delta.get("findings"))[:3])
        if _text(item.get("challenge_statement"))
    )
    return _compact(
        "\n\n".join(
            [
                "Retrieval goal: find source-backed reasoning affordances and absence blockers worth private consideration. Favor non-obvious frame changes, evidence gates, diagnostic questions, guardrails, boundary markers, and rejection aids.",
                f"Decision situation: {ext.decision_situation}",
                f"Original framing: {ext.original_framing}",
                f"Live constraints: {' | '.join(c.constraint for c in ext.live_constraints)}",
                f"Dropped threads: {' | '.join(d.thread for d in ext.dropped_threads)}",
                f"Lane 1 challenge statements: {challenges}",
                f"User turns: {user_turns[:6000]}",
                f"Assistant turns: {assistant_turns[:5000]}",
            ]
        ),
        max_chars=16000,
    )


def _build_card(
    *,
    model_id: str,
    display_name: str,
    record: Mapping[str, Any],
    selection_source: str,
    selection_reason: str,
    lane_candidate: V60Candidate | None,
    retrieval: Mapping[str, Any],
    card_index: int,
    snippet_cap: int,
) -> dict[str, Any]:
    affordances = [_mapping(item) for item in _list(record.get("affordances"))[:1]]
    absences = [_mapping(item) for item in _list(record.get("absence_records"))[:1]]
    return {
        "card_id": f"v60-card-{card_index + 1:03d}-{model_id}",
        "model_id": model_id,
        "display_name": display_name,
        "selection_source": selection_source,
        "selection_reason": selection_reason,
        "pulled_by": sorted(set(_text(lane_candidate.source).split("+"))) if lane_candidate else [],
        "why_pulled": [
            part
            for part in [
                _text(lane_candidate.reason) if lane_candidate else "",
                _text(lane_candidate.evidence) if lane_candidate else "",
            ]
            if part
        ],
        "retrieval_trace": {
            "embedding_model_rank": retrieval.get("rank"),
            "embedding_model_score": retrieval.get("score"),
            "embedding_signal_type": _text(retrieval.get("signal_type")),
        },
        "record_status": _text(record.get("status")),
        "source_file": _text(record.get("source_file")),
        "selected_affordance_cards": [
            _compact_affordance(affordance, snippet_cap=snippet_cap)
            for affordance in affordances
        ],
        "selected_absence_records": [
            _compact_absence(absence, parent_model_id=model_id, snippet_cap=snippet_cap)
            for absence in absences
        ],
        "do_not_overclaim": _do_not_overclaim(record),
        "llm_instruction": (
            "Consider, reject, defer, or keep private. Do not force use. "
            "Absence records are blockers or guardrails, not positive affordances."
        ),
    }


def _compact_affordance(affordance: Mapping[str, Any], *, snippet_cap: int) -> dict[str, Any]:
    affordance_id = _text(affordance.get("affordance_id"))
    activation = _mapping(affordance.get("activation_shape"))
    return {
        "chunk_id": f"aff::{affordance_id}",
        "chunk_kind": "affordance",
        "affordance_id": affordance_id,
        "status": _text(affordance.get("status")),
        "confidence": _text(affordance.get("confidence")),
        "mechanism": _text(affordance.get("mechanism")),
        "activation_shape": {
            "use_when": _strings(activation.get("use_when"))[:snippet_cap],
            "case_evidence_needed": _strings(activation.get("case_evidence_needed"))[:snippet_cap],
            "do_not_use_when": _strings(activation.get("do_not_use_when"))[:snippet_cap],
        },
        "treatment_requirements": [
            {
                "requirement_id": _text(item.get("requirement_id")),
                "description": _text(item.get("description")),
                "evidence_required": _strings(item.get("evidence_required"))[:snippet_cap],
                "good_output_shape": _strings(item.get("good_output_shape"))[:snippet_cap],
            }
            for item in (_mapping(row) for row in _list(affordance.get("treatment_requirements"))[:snippet_cap])
        ],
        "diagnostic_questions": _strings(affordance.get("diagnostic_questions"))[:snippet_cap],
        "misuse_guards": _strings(affordance.get("misuse_guards"))[:snippet_cap],
        "source_evidence": [
            {
                "source_file": _text(item.get("source_file")),
                "source_quote": _text(item.get("source_quote")),
            }
            for item in (_mapping(row) for row in _list(affordance.get("source_evidence"))[:snippet_cap])
        ],
    }


def _compact_absence(
    absence: Mapping[str, Any],
    *,
    parent_model_id: str,
    snippet_cap: int,
) -> dict[str, Any]:
    model_id = _text(absence.get("model_id")) or _text(parent_model_id)
    attempted_field = _text(absence.get("attempted_field"))
    return {
        "chunk_id": f"abs::{model_id}::{attempted_field}",
        "chunk_kind": "absence",
        "attempted_field": attempted_field,
        "status": _text(absence.get("status")),
        "reason": _text(absence.get("reason")),
        "runtime_policy": _text(absence.get("runtime_policy")),
        "source_evidence": [
            {
                "source_file": _text(item.get("source_file")),
                "source_quote": _text(item.get("source_quote")),
            }
            for item in (_mapping(row) for row in _list(absence.get("source_evidence"))[:snippet_cap])
        ],
    }


def _do_not_overclaim(record: Mapping[str, Any]) -> list[str]:
    warnings: list[str] = []
    status = _text(record.get("status"))
    if status in {"weak_support", "deferred_for_review"}:
        warnings.append("Weak or deferred support: treat as cautionary, not authoritative.")
    if not _list(record.get("affordances")) and _list(record.get("absence_records")):
        warnings.append("Absence-only material: do not invent a positive affordance.")
    if _list(record.get("absence_records")):
        warnings.append("Absence records may block tempting but unsupported uses.")
    return warnings


def _selected_chunk_ids(cards: Sequence[Mapping[str, Any]]) -> list[str]:
    ids: list[str] = []
    for card in cards:
        for affordance in (_mapping(item) for item in _list(card.get("selected_affordance_cards"))):
            if _text(affordance.get("chunk_id")):
                ids.append(_text(affordance.get("chunk_id")))
        for absence in (_mapping(item) for item in _list(card.get("selected_absence_records"))):
            if _text(absence.get("chunk_id")):
                ids.append(_text(absence.get("chunk_id")))
    return ids


def _candidate_payload(candidate: V60Candidate) -> dict[str, Any]:
    return {
        "model_id": candidate.model_id,
        "source": candidate.source,
        "lane_order": candidate.lane_order,
        "reason": candidate.reason,
        "evidence": candidate.evidence,
        "route_or_artifact_id": candidate.route_or_artifact_id,
    }


def _hybrid_rrf_rank(lane_rank: Sequence[str], embedding_rank: Sequence[str], *, k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    lane_index = {model_id: index for index, model_id in enumerate(dict.fromkeys(lane_rank))}
    for rank, model_id in enumerate(dict.fromkeys(lane_rank), start=1):
        if model_id:
            scores[model_id] = scores.get(model_id, 0.0) + 1.0 / (k + rank)
    for rank, model_id in enumerate(dict.fromkeys(embedding_rank), start=1):
        if model_id:
            scores[model_id] = scores.get(model_id, 0.0) + 1.0 / (k + rank)
    return [
        model_id
        for model_id, _score in sorted(
            scores.items(),
            key=lambda item: (-item[1], lane_index.get(item[0], 10**6), item[0]),
        )
    ]


def _load_graph_display_names(root: Path) -> dict[str, str]:
    path = Path(root) / "data" / "knowledge_graph.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    models = _mapping(payload.get("models"))
    return {
        model_id: _text(_mapping(model).get("display_name"))
        or _text(_mapping(model).get("name"))
        or model_id
        for model_id, model in models.items()
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _file_sha256(path: Path) -> str:
    return sha256(Path(path).read_bytes()).hexdigest()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_text(item) for item in value if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _slug(value: Any) -> str:
    return _text(value).lower().replace("_", "-")


def _compact(value: str, *, max_chars: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."
