"""Deterministic graph-selection survival reports for archived Lolla runs.

The report is an operator/research artifact. It explains what the mental-model
graph selected, what the Step 6 ledgers used or rejected, and which plausible
signals were not adjudicated. It intentionally avoids calling unselected items
"noise"; later human review and outcome review decide that.
"""
from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


GRAPH_SURVIVAL_SCHEMA_VERSION = "lolla.graph_survival_report.v0.1"
GRAPH_SURVIVAL_JSON = "graph_survival_report.json"
GRAPH_SURVIVAL_MARKDOWN = "graph_survival_report.md"


def build_graph_survival_report(run_dir: Path | str) -> dict[str, Any]:
    """Build a JSON-safe report from an archived run directory."""
    run_path = Path(run_dir)
    result = _read_json_object(run_path / "result.json")
    v60_ledger = _read_json_object(run_path / "v60_ledger.json")
    pre_step6_ledger = _read_json_object(run_path / "pre_step6_private_table_ledger.json")

    v60 = _mapping(result.get("v60_enrichment"))
    candidate_pool = _mapping(v60.get("candidate_pool"))
    telemetry = _mapping(v60.get("telemetry"))
    selected_cards = [_mapping(item) for item in _list(v60.get("selected_cards"))]
    selected_by_model = {
        _text(card.get("model_id")): card
        for card in selected_cards
        if _text(card.get("model_id"))
    }
    selected_by_card = {
        _text(card.get("card_id")): card
        for card in selected_cards
        if _text(card.get("card_id"))
    }

    v60_transactions = [_mapping(item) for item in _list(v60_ledger.get("transactions"))]
    v60_by_model = _group_transactions_by_model(v60_transactions)
    pre_items = [_mapping(item) for item in _list(pre_step6_ledger.get("items"))]
    pre_by_model = _group_pre_step6_items_by_model(pre_items, selected_by_card=selected_by_card)

    embedding_hits = [_mapping(item) for item in _list(candidate_pool.get("embedding_model_hits"))]
    embedding_by_model = {
        _text(item.get("model_id")): (index, item)
        for index, item in enumerate(embedding_hits, start=1)
        if _text(item.get("model_id"))
    }
    skipped = [_mapping(item) for item in _list(telemetry.get("skipped_candidates"))]
    skipped_by_model = _group_by_model(skipped)
    lane_candidates = [_mapping(item) for item in _list(candidate_pool.get("lane_candidates"))]

    model_ids = set()
    model_ids.update(_text(item.get("model_id")) for item in lane_candidates)
    model_ids.update(_text(item.get("model_id")) for item in embedding_hits)
    model_ids.update(selected_by_model)
    model_ids.update(v60_by_model)
    model_ids.update(pre_by_model)
    model_ids.update(_text(item.get("model_id")) for item in skipped)
    model_ids.discard("")

    candidate_survival = [
        _model_survival_row(
            model_id=model_id,
            lane_candidates=lane_candidates,
            selected_card=selected_by_model.get(model_id),
            embedding_by_model=embedding_by_model,
            skipped=skipped_by_model.get(model_id, []),
            v60_transactions=v60_by_model.get(model_id, []),
            pre_items=pre_by_model.get(model_id, []),
        )
        for model_id in sorted(model_ids, key=lambda value: _model_sort_key(value, lane_candidates, embedding_by_model))
    ]

    embedding_selection = _embedding_selection_rows(
        embedding_hits=embedding_hits,
        selected_by_model=selected_by_model,
        v60_by_model=v60_by_model,
        skipped_by_model=skipped_by_model,
    )
    suppressed_signals = _suppressed_signal_rows(
        candidate_survival=candidate_survival,
        skipped=skipped,
        selected_by_model=selected_by_model,
    )
    private_table_survival = [_pre_step6_payload(item) for item in pre_items]
    summary = _summary(
        v60=v60,
        candidate_pool=candidate_pool,
        telemetry=telemetry,
        selected_cards=selected_cards,
        candidate_survival=candidate_survival,
        embedding_selection=embedding_selection,
        suppressed_signals=suppressed_signals,
        v60_transactions=v60_transactions,
        private_table_survival=private_table_survival,
    )

    return {
        "schema_version": GRAPH_SURVIVAL_SCHEMA_VERSION,
        "status": "ready",
        "artifact_role": "research_operator_report",
        "noise_policy": {
            "unselected_does_not_mean_noise": True,
            "unknown_noise_status": True,
            "reason": (
                "Graph candidates, embedding recalls, and antagonist models may "
                "change a user's view even when they do not change the revised answer. "
                "This report preserves suppressed and unadjudicated signals for later evals."
            ),
        },
        "source_refs": {
            "result": "result.json",
            "v60_ledger": "v60_ledger.json" if v60_transactions else "",
            "pre_step6_private_table_ledger": (
                "pre_step6_private_table_ledger.json" if private_table_survival else ""
            ),
        },
        "summary": summary,
        "candidate_survival": candidate_survival,
        "embedding_selection": {
            "mode": _text(candidate_pool.get("embedding_mode")) or "unknown",
            "error": _text(candidate_pool.get("embedding_error")),
            "hit_count": len(embedding_selection),
            "selected_hit_count": sum(1 for row in embedding_selection if row["selected_for_v60"]),
            "unselected_hit_count": sum(1 for row in embedding_selection if not row["selected_for_v60"]),
            "hits": embedding_selection,
        },
        "suppressed_signals": suppressed_signals,
        "private_table_survival": private_table_survival,
        "v60_ledger_summary": {
            "transaction_count": len(v60_transactions),
            "disposition_counts": _counter_dict(
                Counter(_text(item.get("disposition")) or "unknown" for item in v60_transactions)
            ),
            "route_counts": _counter_dict(
                Counter(_text(item.get("route")) or "unknown" for item in v60_transactions)
            ),
        },
    }


def write_graph_survival_artifacts(run_dir: Path | str) -> tuple[Path, Path, dict[str, Any]]:
    """Write JSON and Markdown graph survival reports into ``run_dir``."""
    run_path = Path(run_dir)
    report = build_graph_survival_report(run_path)
    json_path = run_path / GRAPH_SURVIVAL_JSON
    md_path = run_path / GRAPH_SURVIVAL_MARKDOWN
    json_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_graph_survival_markdown(report), encoding="utf-8")
    return json_path, md_path, report


def render_graph_survival_markdown(report: Mapping[str, Any]) -> str:
    """Render a compact operator-facing Markdown report."""
    summary = _mapping(report.get("summary"))
    lines = [
        "# Graph Survival Report",
        "",
        "Research/operator artifact. Unselected signals are preserved as unknown, not labeled as noise.",
        "",
        "## Summary",
        "",
        f"- Status: {_text(report.get('status')) or 'unknown'}",
        f"- Lane candidates: {_safe_int(summary.get('lane_candidate_count'))}",
        f"- Raw lane signals: {_safe_int(summary.get('raw_lane_signal_count'))}",
        f"- Embedding hits: {_safe_int(summary.get('embedding_hit_count'))}",
        f"- Selected V60 cards: {_safe_int(summary.get('selected_card_count'))}",
        f"- Answer-delta models: {_safe_int(summary.get('answer_delta_model_count'))}",
        f"- Private-guardrail models: {_safe_int(summary.get('private_guardrail_model_count'))}",
        f"- Confirming/private-table models: {_safe_int(summary.get('confirming_support_model_count'))}",
        f"- Suppressed models: {_safe_int(summary.get('suppressed_model_count'))}",
        f"- Suppressed or unadjudicated signals: {_safe_int(summary.get('suppressed_signal_count'))}",
        "",
        "## Candidate Survival",
        "",
        "| Model | State | Sources | Embedding | Visible Effect | Private Guardrail |",
        "|---|---|---|---:|---|---|",
    ]
    for row in _list(report.get("candidate_survival")):
        item = _mapping(row)
        embedding_rank = item.get("embedding_rank")
        embedding_cell = (
            f"{embedding_rank} / {item.get('embedding_score')}"
            if embedding_rank
            else ""
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_cell(_text(item.get("model_id"))),
                    _md_cell(_text(item.get("survival_state"))),
                    _md_cell(", ".join(_strings(item.get("sources")))),
                    _md_cell(embedding_cell),
                    _md_cell("; ".join(_strings(item.get("visible_effects")))[:260]),
                    _md_cell("; ".join(_strings(item.get("private_guardrails")))[:260]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Suppressed Signals",
            "",
            "| Model | Reason | Source | Research Status |",
            "|---|---|---|---|",
        ]
    )
    for row in _list(report.get("suppressed_signals")):
        item = _mapping(row)
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_cell(_text(item.get("model_id"))),
                    _md_cell(_text(item.get("reason"))),
                    _md_cell(_text(item.get("source"))),
                    _md_cell(_text(item.get("research_status"))),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def graph_survival_summary_for_trace(run_dir: Path | str) -> dict[str, Any]:
    """Return a compact summary suitable for ``reasoning_trace.json``."""
    report = _read_json_object(Path(run_dir) / GRAPH_SURVIVAL_JSON)
    if not report:
        return {"status": "missing", "artifact_path": ""}
    summary = _mapping(report.get("summary"))
    budget_suppressed = _budget_suppressed_lenses(report, limit=12)
    return {
        "status": _text(report.get("status")) or "unknown",
        "artifact_path": GRAPH_SURVIVAL_JSON,
        "unknown_noise_status": True,
        "lane_candidate_count": _safe_int(summary.get("lane_candidate_count")),
        "raw_lane_signal_count": _safe_int(summary.get("raw_lane_signal_count")),
        "embedding_hit_count": _safe_int(summary.get("embedding_hit_count")),
        "selected_card_count": _safe_int(summary.get("selected_card_count")),
        "answer_delta_model_count": _safe_int(summary.get("answer_delta_model_count")),
        "private_guardrail_model_count": _safe_int(summary.get("private_guardrail_model_count")),
        "confirming_support_model_count": _safe_int(summary.get("confirming_support_model_count")),
        "suppressed_signal_count": _safe_int(summary.get("suppressed_signal_count")),
        "suppressed_model_count": _safe_int(summary.get("suppressed_model_count")),
        "budget_suppressed_signal_count": _safe_int(
            summary.get("budget_suppressed_signal_count")
        ),
        "budget_suppressed_model_count": _safe_int(
            summary.get("budget_suppressed_model_count")
        ),
        "unadjudicated_candidate_count": _safe_int(summary.get("unadjudicated_candidate_count")),
        "top_budget_suppressed_lenses": budget_suppressed,
    }


def _model_survival_row(
    *,
    model_id: str,
    lane_candidates: Sequence[Mapping[str, Any]],
    selected_card: Mapping[str, Any] | None,
    embedding_by_model: Mapping[str, tuple[int, Mapping[str, Any]]],
    skipped: Sequence[Mapping[str, Any]],
    v60_transactions: Sequence[Mapping[str, Any]],
    pre_items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    candidates = [
        _mapping(item)
        for item in lane_candidates
        if _text(_mapping(item).get("model_id")) == model_id
    ]
    effective_skipped = [
        _mapping(item)
        for item in skipped
        if _text(_mapping(item).get("reason")) != "duplicate_model_id"
    ]
    sources = sorted(
        {
            source
            for candidate in candidates
            for source in _source_parts(_text(candidate.get("source")))
        }
        | {_text(selected_card.get("selection_source")) if selected_card else ""}
        | {_text(item.get("source")) for item in effective_skipped}
    )
    sources = [source for source in sources if source]
    visible_effects = _unique(
        _text(item.get("visible_effect"))
        for item in list(v60_transactions) + list(pre_items)
        if _text(item.get("visible_effect"))
    )
    private_guardrails = _unique(
        _text(item.get("private_guardrail"))
        for item in list(v60_transactions) + list(pre_items)
        if _text(item.get("private_guardrail"))
    )
    v60_dispositions = Counter(
        _text(item.get("disposition")) or "unknown" for item in v60_transactions
    )
    pre_dispositions = Counter(
        _text(item.get("disposition")) or "unknown" for item in pre_items
    )
    route_counts = Counter(_text(item.get("route")) or "unknown" for item in v60_transactions)
    embedding_rank = None
    embedding_score = None
    embedding_signal_type = ""
    if model_id in embedding_by_model:
        embedding_rank, embedding_row = embedding_by_model[model_id]
        embedding_score = embedding_row.get("score")
        embedding_signal_type = _text(embedding_row.get("signal_type"))

    return {
        "model_id": model_id,
        "display_name": _text(selected_card.get("display_name")) if selected_card else "",
        "sources": sources,
        "lane_candidate_count": len(candidates),
        "lane_reasons": _unique(_text(item.get("reason")) for item in candidates),
        "evidence": _unique(_text(item.get("evidence")) for item in candidates),
        "selected_for_v60": bool(selected_card),
        "selected_card_id": _text(selected_card.get("card_id")) if selected_card else "",
        "selection_source": _text(selected_card.get("selection_source")) if selected_card else "",
        "selection_reason": _text(selected_card.get("selection_reason")) if selected_card else "",
        "selected_chunk_count": _selected_chunk_count(selected_card),
        "embedding_rank": embedding_rank,
        "embedding_score": embedding_score,
        "embedding_signal_type": embedding_signal_type,
        "v60_transaction_count": len(v60_transactions),
        "v60_disposition_counts": _counter_dict(v60_dispositions),
        "v60_route_counts": _counter_dict(route_counts),
        "pre_step6_item_count": len(pre_items),
        "pre_step6_disposition_counts": _counter_dict(pre_dispositions),
        "visible_effects": visible_effects,
        "private_guardrails": private_guardrails,
        "skipped_reasons": _unique(_text(item.get("reason")) for item in effective_skipped),
        "survival_state": _survival_state(
            selected=bool(selected_card),
            visible_effects=visible_effects,
            private_guardrails=private_guardrails,
            v60_dispositions=v60_dispositions,
            pre_dispositions=pre_dispositions,
            skipped=effective_skipped,
            has_candidate=bool(candidates),
            has_embedding_hit=model_id in embedding_by_model,
        ),
        "unknown_noise_status": True,
    }


def _embedding_selection_rows(
    *,
    embedding_hits: Sequence[Mapping[str, Any]],
    selected_by_model: Mapping[str, Mapping[str, Any]],
    v60_by_model: Mapping[str, Sequence[Mapping[str, Any]]],
    skipped_by_model: Mapping[str, Sequence[Mapping[str, Any]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, raw_hit in enumerate(embedding_hits, start=1):
        hit = _mapping(raw_hit)
        model_id = _text(hit.get("model_id"))
        if not model_id:
            continue
        selected = model_id in selected_by_model
        selected_card = selected_by_model.get(model_id, {})
        transactions = v60_by_model.get(model_id, [])
        rows.append(
            {
                "model_id": model_id,
                "embedding_rank": index,
                "score": hit.get("score"),
                "signal_type": _text(hit.get("signal_type")),
                "selected_for_v60": selected,
                "selection_source": _text(selected_card.get("selection_source")),
                "selection_reason": _text(selected_card.get("selection_reason")),
                "ledger_disposition_counts": _counter_dict(
                    Counter(_text(item.get("disposition")) or "unknown" for item in transactions)
                ),
                "skipped_reasons": _unique(
                    _text(item.get("reason")) for item in skipped_by_model.get(model_id, [])
                ),
                "research_status": "adjudicated" if transactions else "unadjudicated",
                "unknown_noise_status": not bool(transactions),
            }
        )
    return rows


def _suppressed_signal_rows(
    *,
    candidate_survival: Sequence[Mapping[str, Any]],
    skipped: Sequence[Mapping[str, Any]],
    selected_by_model: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw_item in skipped:
        item = _mapping(raw_item)
        model_id = _text(item.get("model_id"))
        reason = _text(item.get("reason")) or "not_selected"
        source = _text(item.get("source"))
        if reason == "duplicate_model_id":
            continue
        if not model_id:
            continue
        key = (model_id, reason)
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "model_id": model_id,
                "reason": reason,
                "source": source,
                "stage": _text(item.get("stage")),
                "score": item.get("score"),
                "selected_for_v60": model_id in selected_by_model,
                "research_status": _suppression_research_status(reason),
                "unknown_noise_status": True,
            }
        )
    for raw_row in candidate_survival:
        row = _mapping(raw_row)
        if row.get("selected_for_v60") or row.get("v60_transaction_count") or row.get("pre_step6_item_count"):
            continue
        if _list(row.get("skipped_reasons")):
            continue
        model_id = _text(row.get("model_id"))
        if not model_id:
            continue
        key = (model_id, "unadjudicated_candidate")
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            {
                "model_id": model_id,
                "reason": "unadjudicated_candidate",
                "source": ",".join(_strings(row.get("sources"))),
                "stage": "post_selection",
                "score": row.get("embedding_score"),
                "selected_for_v60": False,
                "research_status": "plausible_unadjudicated",
                "unknown_noise_status": True,
            }
        )
    return rows


def _summary(
    *,
    v60: Mapping[str, Any],
    candidate_pool: Mapping[str, Any],
    telemetry: Mapping[str, Any],
    selected_cards: Sequence[Mapping[str, Any]],
    candidate_survival: Sequence[Mapping[str, Any]],
    embedding_selection: Sequence[Mapping[str, Any]],
    suppressed_signals: Sequence[Mapping[str, Any]],
    v60_transactions: Sequence[Mapping[str, Any]],
    private_table_survival: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    answer_delta = [row for row in candidate_survival if _list(_mapping(row).get("visible_effects"))]
    guardrail = [row for row in candidate_survival if _list(_mapping(row).get("private_guardrails"))]
    confirming = [
        row for row in candidate_survival
        if _safe_int(_mapping(_mapping(row).get("pre_step6_disposition_counts")).get("confirming_support"))
    ]
    unadjudicated = [
        row for row in candidate_survival
        if _text(_mapping(row).get("survival_state")) == "unadjudicated_candidate"
    ]
    budget_suppressed = [
        row for row in suppressed_signals
        if _text(_mapping(row).get("research_status")) == "plausible_budget_suppressed"
    ]
    return {
        "v60_status": _text(v60.get("status")) or "unknown",
        "lane_candidate_count": _safe_int(candidate_pool.get("lane_candidate_count")),
        "raw_lane_signal_count": _safe_int(candidate_pool.get("raw_lane_signal_count")),
        "embedding_mode": _text(candidate_pool.get("embedding_mode")) or "unknown",
        "embedding_hit_count": len(embedding_selection),
        "selected_card_count": len(selected_cards),
        "selected_model_ids": [_text(card.get("model_id")) for card in selected_cards if _text(card.get("model_id"))],
        "selected_chunk_count": _safe_int(telemetry.get("selected_chunk_count")),
        "skipped_candidate_count": len(_list(telemetry.get("skipped_candidates"))),
        "not_presented_candidate_count": _safe_int(telemetry.get("not_presented_candidate_count")),
        "suppressed_signal_count": len(suppressed_signals),
        "suppressed_model_count": len(
            {
                _text(_mapping(item).get("model_id"))
                for item in suppressed_signals
                if _text(_mapping(item).get("model_id"))
            }
        ),
        "budget_suppressed_signal_count": len(budget_suppressed),
        "budget_suppressed_model_count": len(
            {
                _text(_mapping(item).get("model_id"))
                for item in budget_suppressed
                if _text(_mapping(item).get("model_id"))
            }
        ),
        "candidate_survival_count": len(candidate_survival),
        "answer_delta_model_count": len(answer_delta),
        "private_guardrail_model_count": len(guardrail),
        "confirming_support_model_count": len(confirming),
        "unadjudicated_candidate_count": len(unadjudicated),
        "v60_transaction_count": len(v60_transactions),
        "v60_disposition_counts": _counter_dict(
            Counter(_text(item.get("disposition")) or "unknown" for item in v60_transactions)
        ),
        "private_table_item_count": len(private_table_survival),
        "private_table_disposition_counts": _counter_dict(
            Counter(_text(item.get("disposition")) or "unknown" for item in private_table_survival)
        ),
        "selection_source_counts": dict(_mapping(telemetry.get("selection_source_counts"))),
    }


def _survival_state(
    *,
    selected: bool,
    visible_effects: Sequence[str],
    private_guardrails: Sequence[str],
    v60_dispositions: Counter[str],
    pre_dispositions: Counter[str],
    skipped: Sequence[Mapping[str, Any]],
    has_candidate: bool,
    has_embedding_hit: bool,
) -> str:
    if visible_effects:
        return "answer_delta"
    if private_guardrails:
        return "private_guardrail"
    if pre_dispositions.get("used") or v60_dispositions.get("used"):
        return "used_no_visible_effect"
    if pre_dispositions.get("confirming_support"):
        return "confirming_support"
    if v60_dispositions and set(v60_dispositions).issubset({"rejected"}):
        return "rejected_after_consideration"
    if pre_dispositions and set(pre_dispositions).issubset({"rejected"}):
        return "rejected_after_consideration"
    if selected:
        return "selected_unaccounted"
    if skipped:
        reasons = {_text(item.get("reason")) for item in skipped}
        if reasons & {"packet_cap", "not_presented_packet_cap"}:
            return "suppressed_by_packet_cap"
        if "duplicate_model_id" in reasons:
            return "suppressed_duplicate"
        if "missing_v60_record" in reasons:
            return "suppressed_missing_record"
        return "suppressed_other"
    if has_candidate or has_embedding_hit:
        return "unadjudicated_candidate"
    return "unknown"


def _group_transactions_by_model(
    transactions: Sequence[Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for item in transactions:
        model_id = _text(item.get("model_id"))
        if model_id:
            grouped.setdefault(model_id, []).append(item)
    return grouped


def _group_pre_step6_items_by_model(
    items: Sequence[Mapping[str, Any]],
    *,
    selected_by_card: Mapping[str, Mapping[str, Any]],
) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for item in items:
        model_id = _pre_step6_model_id(item, selected_by_card=selected_by_card)
        if model_id:
            grouped.setdefault(model_id, []).append(item)
    return grouped


def _pre_step6_model_id(
    item: Mapping[str, Any],
    *,
    selected_by_card: Mapping[str, Mapping[str, Any]],
) -> str:
    source_kind = _text(item.get("source_kind"))
    source_atom_id = _text(item.get("source_atom_id"))
    source_id = _text(item.get("source_id"))
    if source_kind == "lane2_anchor":
        return source_atom_id
    if source_kind == "v60_selected_card":
        card_id = source_atom_id or source_id.rsplit("::", 1)[-1]
        return _text(_mapping(selected_by_card.get(card_id)).get("model_id"))
    return ""


def _pre_step6_payload(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": _text(item.get("source_id")),
        "source_kind": _text(item.get("source_kind")),
        "title": _text(item.get("title")),
        "source_atom_id": _text(item.get("source_atom_id")),
        "disposition": _text(item.get("disposition")),
        "why": _text(item.get("why")),
        "visible_effect": _text(item.get("visible_effect")),
        "private_guardrail": _text(item.get("private_guardrail")),
    }


def _group_by_model(items: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for item in items:
        model_id = _text(item.get("model_id"))
        if model_id:
            grouped.setdefault(model_id, []).append(item)
    return grouped


def _selected_chunk_count(card: Mapping[str, Any] | None) -> int:
    if not card:
        return 0
    return len(_list(card.get("selected_affordance_cards"))) + len(
        _list(card.get("selected_absence_records"))
    )


def _model_sort_key(
    model_id: str,
    lane_candidates: Sequence[Mapping[str, Any]],
    embedding_by_model: Mapping[str, tuple[int, Mapping[str, Any]]],
) -> tuple[int, int, str]:
    lane_indexes = [
        index
        for index, item in enumerate(lane_candidates)
        if _text(_mapping(item).get("model_id")) == model_id
    ]
    lane_index = min(lane_indexes) if lane_indexes else 10_000
    embedding_rank = embedding_by_model.get(model_id, (10_000, {}))[0]
    return (lane_index, embedding_rank, model_id)


def _source_parts(source: str) -> list[str]:
    return [part for part in source.split("+") if part]


def _suppression_research_status(reason: str) -> str:
    if reason in {"packet_cap", "not_presented_packet_cap"}:
        return "plausible_budget_suppressed"
    if reason == "duplicate_model_id":
        return "duplicate_not_noise"
    if reason == "missing_v60_record":
        return "unavailable_not_adjudicated"
    if reason in {"no_v60_chunks_available"}:
        return "no_source_chunk_available"
    return "unadjudicated"


def _budget_suppressed_lenses(report: Mapping[str, Any], *, limit: int) -> list[dict[str, Any]]:
    """Return top budget-suppressed lens rows for direct trace visibility."""
    rows: list[dict[str, Any]] = []
    for raw_item in _list(report.get("suppressed_signals")):
        item = _mapping(raw_item)
        if _text(item.get("research_status")) != "plausible_budget_suppressed":
            continue
        rows.append(
            {
                "model_id": _text(item.get("model_id")),
                "reason": _text(item.get("reason")),
                "source": _text(item.get("source")),
                "stage": _text(item.get("stage")),
                "score": item.get("score"),
                "research_status": _text(item.get("research_status")),
                "unknown_noise_status": True,
            }
        )
    return sorted(
        rows,
        key=lambda item: (
            -_safe_float(item.get("score")),
            _text(item.get("model_id")),
            _text(item.get("reason")),
        ),
    )[:limit]


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _unique(values: Sequence[str] | Any) -> list[str]:
    seen: set[str] = set()
    rows: list[str] = []
    for raw_value in values:
        value = _text(raw_value)
        if value and value not in seen:
            seen.add(value)
            rows.append(value)
    return rows


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return {
        key: count
        for key, count in sorted(
            ((key, count) for key, count in counter.items() if key),
            key=lambda item: (-item[1], item[0]),
        )
    }


def _md_cell(value: str) -> str:
    return _text(value).replace("|", "\\|").replace("\n", " ")
