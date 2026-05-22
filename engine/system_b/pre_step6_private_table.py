"""Step-6 private thinking-table transport.

This module renders a compact private context table from the current run's
lane outputs and V60 enrichment, optionally appending cached pre-Step-6 card
deck material when a cache hit exists. It does not call LLMs, generate live
cards, select a visible answer, or judge wisdom.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .pre_step6_shadow_portfolio import (
    CARD_DECK_SCHEMA_VERSION,
    _compiled_card_deck_key,
    _key_material,
    _load_cached_deck,
)

SCHEMA_VERSION = "pre_step6_private_table.v1"
LEDGER_SCHEMA_VERSION = "pre_step6_private_table_ledger.v1"

DEFAULT_MAX_CHARS = 9000
_MAX_ITEMS_PER_SECTION = 5
_MAX_TEXT = 420
_GATES = {
    "step6_private_context_allowed": True,
    "live_card_generation_allowed": False,
    "normal_runtime_reviewer_calls": 0,
    "code_visible_answer_selection_allowed": False,
}
_DETERMINISTIC_ROLE = [
    "render_current_run_private_table",
    "lookup_cached_deck_only",
    "cap_private_context_chars",
    "write_step6_private_sidecar",
    "leave_cognition_to_step6",
]


def build_pre_step6_private_table(
    *,
    result_payload: dict[str, Any],
    cache_dir: Path | str | None = None,
    max_chars: int = DEFAULT_MAX_CHARS,
) -> tuple[dict[str, Any], str]:
    """Build the private Step-6 table payload and rendered markdown.

    The table is always useful as a compact rendering of the current run. A
    cached deck, when present, is extra private pressure. Cache misses do not
    fail the run and do not trigger live card generation.
    """
    result = _as_mapping(result_payload)
    cache_dir_path = Path(cache_dir) if cache_dir is not None else None
    material = _key_material(result)
    compiled_key = _compiled_card_deck_key(material)
    cache_payload, cached_deck = _load_cached_deck(cache_dir_path, compiled_key)
    sources: list[dict[str, str]] = []
    rendered = _render_private_table(
        result,
        cached_deck=cached_deck,
        cache_state=str(cache_payload.get("state") or "cache_miss"),
        sources=sources,
    )
    rendered = _cap_rendered_table(rendered, max_chars=max(1200, int(max_chars or DEFAULT_MAX_CHARS)))
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "ready",
        "runtime_policy": "step6_private_context",
        "promotion_effect": "none_private_context_only",
        "compiled_card_deck_key": compiled_key,
        "key_material": material,
        "cache": cache_payload,
        "cached_card_deck_summary": _cached_deck_summary(cached_deck),
        "table_char_count": len(rendered),
        "table_section_count": len(sources),
        "source_items": sources,
        "consideration_ledger_skeleton": _ledger_skeleton(sources),
        "sidecars": {
            "markdown": "",
            "json": "",
        },
        "deterministic_role": list(_DETERMINISTIC_ROLE),
        "gates": dict(_GATES),
        "cost_envelope": {
            "normal_runtime_reviewer_calls": 0,
            "live_card_generation_allowed": False,
            "net_new_llm_calls": 0,
        },
    }
    validate_pre_step6_private_table(payload)
    return payload, rendered


def validate_pre_step6_private_table(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise ValueError("pre-Step-6 private table payload must be an object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("invalid pre-Step-6 private table schema_version")
    if payload.get("promotion_effect") != "none_private_context_only":
        raise ValueError("private table must not promote visible behavior")
    if payload.get("gates") != _GATES:
        raise ValueError("private table gates are invalid")
    if "rendered_private_table" in payload:
        raise ValueError("private table markdown belongs in the sidecar, not result.json")
    cache = _as_mapping(payload.get("cache"))
    if cache.get("live_card_generation_allowed") is not False:
        raise ValueError("private table must not generate live card decks")
    ledger = _as_mapping(payload.get("consideration_ledger_skeleton"))
    if ledger.get("schema_version") != LEDGER_SCHEMA_VERSION:
        raise ValueError("invalid private table ledger schema_version")


def write_pre_step6_private_table_sidecars(
    payload: dict[str, Any],
    rendered_markdown: str,
    *,
    tmp_dir: Path | str = "/tmp",
    run_id: str,
) -> dict[str, Path]:
    """Write markdown + JSON sidecars and return their paths."""
    validate_pre_step6_private_table(payload)
    tmp = Path(tmp_dir)
    markdown_path = tmp / f"lolla_{run_id}_pre_step6_private_table.md"
    json_path = tmp / f"lolla_{run_id}_pre_step6_private_table.json"
    markdown_path.write_text(rendered_markdown, encoding="utf-8")
    payload["sidecars"] = {
        "markdown": str(markdown_path),
        "json": str(json_path),
    }
    validate_pre_step6_private_table(payload)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"markdown": markdown_path, "json": json_path}


def _render_private_table(
    result: dict[str, Any],
    *,
    cached_deck: dict[str, Any],
    cache_state: str,
    sources: list[dict[str, str]],
) -> str:
    extraction = _as_mapping(result.get("extraction"))
    parts = [
        "# Pre-Step-6 Private Thinking Table",
        "",
        "Private context for Step 6. Hints, not commands. Code rendered and capped this table; it did not decide what is wise. Step 6 may use, reject, defer, combine, or keep any item private after serious consideration.",
        "",
        "## Problem Read",
        f"- Decision: {_text(extraction.get('decision_situation')) or 'Not supplied.'}",
        f"- Original framing: {_text(extraction.get('original_framing')) or 'Not supplied.'}",
        f"- Latest assistant position: {_clip(_text(extraction.get('synthesized_position')), 520) or 'Not supplied.'}",
    ]
    constraints = _extract_constraint_lines(extraction)
    if constraints:
        parts.extend(["- Live constraints:", *[f"  - {item}" for item in constraints]])
    dropped = _extract_dropped_thread_lines(extraction)
    if dropped:
        parts.extend(["- Dropped/open threads:", *[f"  - {item}" for item in dropped]])

    lane1 = _lane1_lines(result)
    if lane1:
        _append_section(parts, sources, "lane1_structural_challenge", "Lane 1 structural challenge", lane1)
    lane2 = _lane2_lines(result)
    if lane2:
        _append_section(parts, sources, "lane2_anchor_pressure", "Lane 2 anchor pressure", lane2)
    lane3 = _lane3_lines(result)
    if lane3:
        _append_section(parts, sources, "lane3_frame_pressure", "Lane 3 frame pressure", lane3)
    lane4 = _lane4_lines(result)
    if lane4:
        _append_section(parts, sources, "lane4_coverage_gaps", "Lane 4 coverage gaps", lane4)
    v60 = _v60_lines(result)
    if v60:
        _append_section(parts, sources, "v60_private_enrichment", "V60 private enrichment", v60)

    parts.extend(["", "## Cached Portfolio Cards"])
    if cached_deck:
        parts.append("Cache hit. Treat these as private pressure atoms, not an answer template.")
        for card in _as_list(cached_deck.get("cards"))[:_MAX_ITEMS_PER_SECTION]:
            card_map = _as_mapping(card)
            card_id = _text(card_map.get("card_id")) or "cached_card"
            label = _text(card_map.get("card_label")) or card_id
            role = _clip(_text(card_map.get("cognitive_role")), _MAX_TEXT)
            handling = _clip(_text(card_map.get("handling_rule")), _MAX_TEXT)
            anchor = _clip(_text(card_map.get("anchor_text")), 700)
            receipts = [_clip(_text(item), 260) for item in _as_list(card_map.get("receipts"))[:3] if _text(item)]
            sources.append(
                {
                    "source_id": f"cached_card::{card_id}",
                    "source_kind": "cached_portfolio_card",
                    "title": label,
                }
            )
            parts.extend(["", f"### {label}", f"- Card id: {card_id}"])
            if role:
                parts.append(f"- Cognitive role: {role}")
            if anchor:
                parts.append(f"- Anchor text: {anchor}")
            if receipts:
                parts.extend(["- Receipts:", *[f"  - {receipt}" for receipt in receipts]])
            if handling:
                parts.append(f"- Handling rule: {handling}")
    else:
        parts.append(
            f"Cache state: {cache_state}. No cached portfolio cards are added for this run; do not infer missing pressure from the cache miss."
        )

    parts.extend(
        [
            "",
            "## Private Consideration Instructions",
            "- Start from the ordinary audit evidence and V60 material; use cached portfolio cards only when they add concrete decision pressure.",
            "- Broad private edge is allowed. Public prose should stay small, concrete, and human.",
            "- If an item is useful only as a guardrail, keep it private and record that privately.",
            "- Do not expose internal labels, lane names, card ids, V60 ids, or this table in chat or memo.",
        ]
    )
    return "\n".join(parts).strip() + "\n"


def _append_section(
    parts: list[str],
    sources: list[dict[str, str]],
    source_id: str,
    title: str,
    lines: list[str],
) -> None:
    sources.append({"source_id": source_id, "source_kind": "current_run_section", "title": title})
    parts.extend(["", f"## {title}", *lines])


def _ledger_skeleton(sources: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "status": "pending",
        "items": [
            {
                **source,
                "disposition": "",
                "why": "",
                "visible_effect": "",
                "private_guardrail": "",
            }
            for source in sources
        ],
        "notes": ["Private telemetry only. Not rendered in chat."],
    }


def _cached_deck_summary(deck: dict[str, Any]) -> dict[str, Any]:
    if not deck:
        return {}
    return {
        "schema_version": _text(deck.get("schema_version")),
        "status": _text(deck.get("status")),
        "runtime_policy": _text(deck.get("runtime_policy")),
        "card_count": len(_as_list(deck.get("cards"))),
    }


def _lane1_lines(result: dict[str, Any]) -> list[str]:
    delta = _as_mapping(result.get("delta_card"))
    findings = _as_list(delta.get("top_findings")) or _as_list(delta.get("findings"))
    lines: list[str] = []
    for idx, finding in enumerate(findings[:_MAX_ITEMS_PER_SECTION], start=1):
        item = _as_mapping(finding)
        name = _text(item.get("tendency_name") or item.get("tendency_id")) or "structural pressure"
        severity = _text(item.get("severity")) or "unrated"
        challenge = _clip(_text(item.get("challenge_statement")), _MAX_TEXT)
        passage = _clip(_text(item.get("specific_passage")), 260)
        next_move = _clip(_text(item.get("next_move")), 240)
        line = f"- {idx}. [{severity}] {name}"
        if challenge:
            line += f": {challenge}"
        if passage:
            line += f" Evidence: \"{passage}\""
        if next_move:
            line += f" Next move: {next_move}"
        lines.append(line)
    summary = _text(delta.get("secondary_additional_pressures_note"))
    if summary:
        lines.append(f"- Secondary pressure summary: {_clip(summary, _MAX_TEXT)}")
    return lines


def _lane2_lines(result: dict[str, Any]) -> list[str]:
    companion = _as_mapping(result.get("companion_cheat_sheet"))
    anchors = _as_list(companion.get("anchors"))
    lines: list[str] = []
    for idx, anchor in enumerate(anchors[:_MAX_ITEMS_PER_SECTION], start=1):
        item = _as_mapping(anchor)
        label = _text(item.get("display_name") or item.get("model_id") or item.get("name"))
        reason = _clip(_text(item.get("why_it_matters") or item.get("fit_reason") or item.get("reason")), 320)
        chunks = _as_list(item.get("chunks"))
        chunk_bits: list[str] = []
        for chunk in chunks[:2]:
            chunk_map = _as_mapping(chunk)
            chunk_bits.append(
                _clip(
                    _text(
                        chunk_map.get("text")
                        or chunk_map.get("content")
                        or chunk_map.get("summary")
                        or chunk_map.get("chunk")
                    ),
                    180,
                )
            )
        line = f"- {idx}. {label or 'anchor'}"
        if reason:
            line += f": {reason}"
        chunk_bits = [bit for bit in chunk_bits if bit]
        if chunk_bits:
            line += " Supporting chunks: " + " | ".join(chunk_bits)
        lines.append(line)
    return lines


def _lane3_lines(result: dict[str, Any]) -> list[str]:
    frame = _as_mapping(result.get("frame_pressure_card"))
    lines: list[str] = []
    for idx, element in enumerate(_as_list(frame.get("frame_elements"))[:3], start=1):
        item = _as_mapping(element)
        kind = _text(item.get("element_type")) or "frame element"
        pattern = _text(item.get("frame_pattern"))
        text = _clip(_text(item.get("text") or item.get("description") or item.get("element")), 300)
        fragility = _clip(_text(item.get("fragility_signal")), 220)
        line = f"- {idx}. {kind}"
        if pattern:
            line += f" ({pattern})"
        if text:
            line += f": {text}"
        if fragility:
            line += f" Break/test: {fragility}"
        lines.append(line)
    for idx, reframe in enumerate(_as_list(frame.get("reframings"))[:2], start=1):
        item = _as_mapping(reframe)
        move = _text(item.get("reframe_move_type")) or "reframe"
        prompt = _clip(_text(item.get("question") or item.get("reframed_question") or item.get("text")), 300)
        if prompt:
            lines.append(f"- Reframe {idx} [{move}]: {prompt}")
    return lines


def _lane4_lines(result: dict[str, Any]) -> list[str]:
    coverage = _as_mapping(result.get("structural_coverage_card"))
    lines: list[str] = []
    dimensions = [_as_mapping(item) for item in _as_list(coverage.get("dimensions"))]
    gaps = [item for item in dimensions if item.get("covered") is False]
    for idx, dim in enumerate((gaps or dimensions)[:_MAX_ITEMS_PER_SECTION], start=1):
        name = _text(dim.get("dimension_name") or dim.get("dimension_id")) or "dimension"
        note = _clip(_text(dim.get("materiality_note") or dim.get("coverage_evidence")), 300)
        lines.append(f"- {idx}. {name}: {note or 'No note supplied.'}")
    for question in _as_list(coverage.get("gap_questions"))[:3]:
        qmap = _as_mapping(question)
        name = _text(qmap.get("dimension_name") or qmap.get("dimension_id")) or "gap"
        qs = [_clip(_text(q), 180) for q in _as_list(qmap.get("questions"))[:2] if _text(q)]
        if qs:
            lines.append(f"- User-answerable {name}: " + " | ".join(qs))
    return lines


def _v60_lines(result: dict[str, Any]) -> list[str]:
    v60 = _as_mapping(result.get("v60_enrichment"))
    if _text(v60.get("status")) != "active":
        return []
    lines: list[str] = []
    for idx, card in enumerate(_as_list(v60.get("selected_cards"))[:_MAX_ITEMS_PER_SECTION], start=1):
        item = _as_mapping(card)
        model = _text(item.get("display_name") or item.get("model_id") or item.get("card_id")) or "private card"
        reason = _clip(_text(item.get("selection_reason") or item.get("reason")), 220)
        lines.append(f"- {idx}. {model}: {reason or 'Selected for private consideration.'}")
        for affordance in _as_list(item.get("selected_affordance_cards"))[:1]:
            amap = _as_mapping(affordance)
            text = _clip(_text(amap.get("text") or amap.get("summary") or amap.get("chunk_text")), 240)
            cid = _text(amap.get("chunk_id") or amap.get("id"))
            if text:
                lines.append(f"  - Affordance {cid}: {text}")
        for absence in _as_list(item.get("selected_absence_records"))[:1]:
            amap = _as_mapping(absence)
            text = _clip(_text(amap.get("text") or amap.get("summary") or amap.get("chunk_text")), 240)
            cid = _text(amap.get("chunk_id") or amap.get("id"))
            if text:
                lines.append(f"  - Absence {cid}: {text}")
    return lines


def _extract_constraint_lines(extraction: dict[str, Any]) -> list[str]:
    lines = []
    for item in _as_list(extraction.get("live_constraints"))[:_MAX_ITEMS_PER_SECTION]:
        if isinstance(item, str):
            text = item
        else:
            text = _text(_as_mapping(item).get("constraint"))
        if text:
            lines.append(_clip(text, 220))
    return lines


def _extract_dropped_thread_lines(extraction: dict[str, Any]) -> list[str]:
    lines = []
    for item in _as_list(extraction.get("dropped_threads"))[:_MAX_ITEMS_PER_SECTION]:
        if isinstance(item, str):
            text = item
        else:
            text = _text(_as_mapping(item).get("thread"))
        if text:
            lines.append(_clip(text, 220))
    return lines


def _cap_rendered_table(value: str, *, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    suffix = "\n\n[Private table capped. Read result.json for full source artifacts if needed.]\n"
    return value[: max(0, max_chars - len(suffix))].rstrip() + suffix


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _clip(value: str, max_chars: int) -> str:
    text = " ".join(_text(value).split())
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "..."
