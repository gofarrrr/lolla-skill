#!/usr/bin/env python3
"""Phase 5 live_constraints specialist — evaluation against the Phase 5.0 gold.

For each of the 5 gate cases, runs `extract_live_constraints` with a live
OpenRouter boundary, then compares LLM output to the 20 gold items from
`research/phase5-user-side-specialist-annotation-gate-2026-04-24.md`.

Measures per case:
  - recall: how many of the 4 gold items did the LLM find?
  - mode fidelity: when gold says derivation, did LLM emit derivation?
  - kind agreement: on matched events, does kind match?
  - validation pass rate: raw vs validated (from stats)
  - extras: valid LLM events that don't correspond to any gold item

Writes `research/phase5-live-constraints-eval-2026-04-24.md`.

Cost: ~$1-3 across 5 LLM calls.

Usage:
    python3 scripts/phase5_live_constraints_eval.py
"""
from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "engine"))

for line in (REPO_ROOT / ".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    if line.startswith("export "):
        line = line[7:].strip()
    k, _, v = line.partition("=")
    k = k.strip()
    v = v.strip().strip('"').strip("'")
    if k and k not in os.environ:
        os.environ[k] = v

from system_b.boundary_provider import load_boundary_client_from_env
from system_b.conversation_loader import load_conversation_context
from system_b.ir import DerivationProvenance, SpanProvenance
from system_b.live_constraints_extraction import extract_live_constraints


# Gold items from the Phase 5.0 gate.
# Tuple form: (item_id, mode, turn_or_turns, kind, snippet)
#   mode: "span" or "derivation"
#   turn_or_turns: int for span; tuple[int, ...] for derivation
#   snippet: distinctive 6-10 token substring from the reviewer-convergent span
GOLD: dict[str, list[dict]] = {
    "user_has_plan": [
        {"id": "UHP-C1", "mode": "span", "turn": 2, "kind": "constraint",
         "snippet": "informal conversations with 4-5 former colleagues"},
        {"id": "UHP-C2", "mode": "derivation", "turns": (1, 2), "kind": "constraint",
         "snippet": "8 months"},
        {"id": "UHP-C3", "mode": "derivation", "turns": (1, 2), "kind": "constraint",
         "snippet": "6 weeks"},
        {"id": "UHP-C4", "mode": "span", "turn": 5, "kind": "constraint",
         "snippet": "Spouse is on board with the independent plan"},
    ],
    "whistleblower": [
        {"id": "WB-C1", "mode": "span", "turn": 1, "kind": "constraint",
         "snippet": "active audit with a major regulator"},
        {"id": "WB-C2", "mode": "span", "turn": 2, "kind": "constraint",
         "snippet": "three of them, labeled with the client's internal project code"},
        {"id": "WB-C3", "mode": "span", "turn": 6, "kind": "constraint",
         "snippet": "60-65%"},
        {"id": "WB-C4", "mode": "span", "turn": 4, "kind": "constraint",
         "snippet": "mortgage, two kids about to start high school"},
    ],
    "parenting_teen": [
        {"id": "PT-C1", "mode": "span", "turn": 1, "kind": "constraint",
         "snippet": "shut down completely"},
        {"id": "PT-C2", "mode": "span", "turn": 1, "kind": "constraint",
         "snippet": "I'm overreacting and this is teenage stuff"},
        {"id": "PT-C3", "mode": "span", "turn": 5, "kind": "constraint",
         "snippet": "going through her phone for months"},
        {"id": "PT-C4", "mode": "span", "turn": 7, "kind": "constraint",
         "snippet": "it becomes a legal case, she becomes a witness"},
    ],
    "multi_offer": [
        {"id": "MO-C1", "mode": "span", "turn": 1, "kind": "constraint",
         "snippet": "I have to pick one within 7 days"},
        {"id": "MO-C2", "mode": "derivation", "turns": (1, 4), "kind": "constraint",
         "snippet": "80% base cut"},
        {"id": "MO-C3", "mode": "derivation", "turns": (1, 2), "kind": "constraint",
         "snippet": "no clear path to staff"},
        {"id": "MO-C4", "mode": "span", "turn": 5, "kind": "constraint",
         "snippet": "primary earner"},
    ],
    "startup_pivot": [
        {"id": "SP-C1", "mode": "span", "turn": 1, "kind": "constraint",
         "snippet": "14 months of runway"},
        {"id": "SP-C2", "mode": "span", "turn": 1, "kind": "constraint",
         "snippet": "flat for four months"},
        {"id": "SP-C3", "mode": "derivation", "turns": (1, 4), "kind": "constraint",
         "snippet": "two full-time employees"},
        {"id": "SP-C4", "mode": "span", "turn": 2, "kind": "constraint",
         "snippet": "None of them have given me a specific price or timeline"},
    ],
}

CASES = list(GOLD.keys())

CORPUS = REPO_ROOT / "research" / "test-cases"
SCRATCH = CORPUS / "phase2a-lane3-equivalence-2026-04-23" / "_scratch"


@dataclass
class CaseResult:
    case: str
    raw_count: int = 0
    validated_count: int = 0
    dropped_count: int = 0
    span_mode_count: int = 0
    derivation_mode_count: int = 0
    gold_found: list[str] = field(default_factory=list)
    gold_missed: list[str] = field(default_factory=list)
    gold_mode_match: list[str] = field(default_factory=list)   # gold mode and LLM mode agree
    gold_mode_mismatch: list[tuple[str, str, str]] = field(default_factory=list)  # (id, gold_mode, llm_mode)
    gold_kind_match: list[str] = field(default_factory=list)
    gold_kind_mismatch: list[tuple[str, str, str]] = field(default_factory=list)
    extra_events: int = 0
    events_dump: list[dict] = field(default_factory=list)


def _event_turns(event) -> set[int]:
    if isinstance(event.provenance, SpanProvenance):
        return {event.provenance.span_ref.turn_index}
    if isinstance(event.provenance, DerivationProvenance):
        return {r.turn_index for r in event.provenance.turn_refs}
    return set()


def _event_mode(event) -> str:
    if isinstance(event.provenance, SpanProvenance):
        return "span"
    if isinstance(event.provenance, DerivationProvenance):
        return "derivation"
    return "unknown"


def _find_snippet_in_event(event, snippet_lc: str, user_turn_map: dict[int, str]) -> bool:
    """Check whether the snippet appears in event.text OR in any of the
    user-turn texts referenced by the event's provenance."""
    if snippet_lc in event.text.lower():
        return True
    # For derivation events, event.text is a label — check the referenced
    # turn texts' overlap (these are user turns we already have).
    for turn_index in _event_turns(event):
        turn_text = user_turn_map.get(turn_index, "")
        if snippet_lc in turn_text.lower():
            # Turn contains the snippet. This is a weak match — the event's
            # span might not actually carry the snippet. For SpanProvenance
            # we can be stricter: the span_ref must actually cover the snippet.
            if isinstance(event.provenance, SpanProvenance):
                ref = event.provenance.span_ref
                span_text = turn_text[ref.start_char:ref.end_char].lower()
                if snippet_lc in span_text:
                    return True
                # Span doesn't cover the snippet even though the turn does — skip.
                continue
            # For derivation, allow the turn-level match (excerpt info lost after validation).
            return True
    return False


def _match_gold(
    gold_item: dict,
    events: list,
    user_turn_map: dict[int, str],
    consumed: set[int],
) -> tuple[int | None, str]:
    """Return (llm_event_index, match_kind). match_kind in
    {'exact', 'turn_only', 'none'}."""
    gold_turns = (
        {gold_item["turn"]} if gold_item["mode"] == "span" else set(gold_item["turns"])
    )
    snippet_lc = gold_item["snippet"].lower()
    # First pass: require snippet-in-event-OR-span and turn overlap.
    for i, event in enumerate(events):
        if i in consumed:
            continue
        if not (_event_turns(event) & gold_turns):
            continue
        if _find_snippet_in_event(event, snippet_lc, user_turn_map):
            return i, "exact"
    # Second pass (lenient): turn-only match (no snippet). Used for derivation.
    if gold_item["mode"] == "derivation":
        for i, event in enumerate(events):
            if i in consumed:
                continue
            if _event_mode(event) != "derivation":
                continue
            if _event_turns(event) & gold_turns:
                return i, "turn_only"
    return None, "none"


def _match_case(gold_case: list[dict], events: list, user_turn_map: dict[int, str]) -> CaseResult:
    result = CaseResult(case=gold_case[0]["id"].split("-")[0])
    consumed: set[int] = set()
    for gold in gold_case:
        idx, how = _match_gold(gold, events, user_turn_map, consumed)
        if idx is None:
            result.gold_missed.append(gold["id"])
            continue
        consumed.add(idx)
        result.gold_found.append(gold["id"])
        event = events[idx]
        llm_mode = _event_mode(event)
        if llm_mode == gold["mode"]:
            result.gold_mode_match.append(gold["id"])
        else:
            result.gold_mode_mismatch.append((gold["id"], gold["mode"], llm_mode))
        if event.kind == gold["kind"]:
            result.gold_kind_match.append(gold["id"])
        else:
            result.gold_kind_mismatch.append((gold["id"], gold["kind"], event.kind))
    result.extra_events = len(events) - len(consumed)
    return result


def run() -> None:
    boundary = load_boundary_client_from_env("openrouter")
    results: list[CaseResult] = []
    started = time.monotonic()

    for case in CASES:
        print(f"\n=== {case} ===", flush=True)
        conv_path = CORPUS / f"case_{case}_conversation.txt"
        ext_path = SCRATCH / f"{case}_extraction.json"
        if not conv_path.exists() or not ext_path.exists():
            print("  SKIP: missing artifacts")
            continue
        context = load_conversation_context(ext_path, conv_path)
        user_turn_map = {t.turn_index: t.text for t in context.turns if t.speaker == "user"}

        try:
            events, stats = extract_live_constraints(context=context, boundary=boundary)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            continue

        result = _match_case(GOLD[case], events, user_turn_map)
        result.case = case
        result.raw_count = stats.raw_count
        result.validated_count = stats.validated_count
        result.dropped_count = (
            stats.dropped_invalid_kind
            + stats.dropped_invalid_turn
            + stats.dropped_not_substring
            + stats.dropped_derivation_no_valid_excerpt
            + stats.dropped_invalid_mode
        )
        result.span_mode_count = stats.span_mode_count
        result.derivation_mode_count = stats.derivation_mode_count
        result.events_dump = [
            {
                "mode": _event_mode(e),
                "text": e.text[:120],
                "turns": sorted(_event_turns(e)),
                "kind": e.kind,
                "kind_ambiguity": e.kind_ambiguity,
            }
            for e in events
        ]
        results.append(result)

        print(
            f"  raw={stats.raw_count} validated={stats.validated_count} "
            f"(span={stats.span_mode_count} derivation={stats.derivation_mode_count}) "
            f"dropped={result.dropped_count}"
        )
        print(f"  gold_found={len(result.gold_found)}/{len(GOLD[case])} "
              f"missed={result.gold_missed}")
        print(f"  mode_match={len(result.gold_mode_match)}/{len(result.gold_found)} "
              f"kind_match={len(result.gold_kind_match)}/{len(result.gold_found)}")
        if result.gold_mode_mismatch:
            for gid, gm, lm in result.gold_mode_mismatch:
                print(f"    mode mismatch {gid}: gold={gm} llm={lm}")
        if result.gold_kind_mismatch:
            for gid, gk, lk in result.gold_kind_mismatch:
                print(f"    kind mismatch {gid}: gold={gk} llm={lk}")
        print(f"  extras={result.extra_events}")

    duration = time.monotonic() - started
    _write_report(results, duration)


def _write_report(results: list[CaseResult], duration: float) -> None:
    out_path = REPO_ROOT / "research" / "phase5-live-constraints-eval-2026-04-24.md"
    lines: list[str] = []
    lines.append("# Phase 5 live_constraints — evaluation vs Phase 5.0 gold")
    lines.append("")
    lines.append(
        f"**Date:** 2026-04-24  **Cases:** {len(results)} / 5  **Wall time:** {duration:.1f}s"
    )
    lines.append("")
    lines.append(
        "Runs `extract_live_constraints` on each of the 5 annotation-gate cases and "
        "compares LLM output to the 20 gold items. Measures recall, output-mode "
        "fidelity (span vs derivation), kind agreement on matched events, "
        "validation pass rate, and extras (valid events not in gold)."
    )
    lines.append("")

    total_gold = sum(len(GOLD[r.case]) for r in results)
    total_found = sum(len(r.gold_found) for r in results)
    total_mode_match = sum(len(r.gold_mode_match) for r in results)
    total_kind_match = sum(len(r.gold_kind_match) for r in results)
    total_extras = sum(r.extra_events for r in results)
    total_raw = sum(r.raw_count for r in results)
    total_validated = sum(r.validated_count for r in results)
    total_span = sum(r.span_mode_count for r in results)
    total_derivation = sum(r.derivation_mode_count for r in results)
    total_dropped = sum(r.dropped_count for r in results)
    recall = (total_found / total_gold) if total_gold else 0.0
    mode_rate = (total_mode_match / total_found) if total_found else 0.0
    kind_rate = (total_kind_match / total_found) if total_found else 0.0
    validation_rate = (total_validated / total_raw) if total_raw else 0.0

    # Span-only and derivation-only recall
    span_gold_ids = {
        g["id"] for case in results for g in GOLD[case.case] if g["mode"] == "span"
    }
    deriv_gold_ids = {
        g["id"] for case in results for g in GOLD[case.case] if g["mode"] == "derivation"
    }
    found_ids = {gid for r in results for gid in r.gold_found}
    span_recall = (len(span_gold_ids & found_ids) / len(span_gold_ids)) if span_gold_ids else 0.0
    deriv_recall = (len(deriv_gold_ids & found_ids) / len(deriv_gold_ids)) if deriv_gold_ids else 0.0

    lines.append("## Aggregate")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Gold items total | {total_gold} |")
    lines.append(f"| Gold recovered | {total_found} ({100*recall:.0f}%) |")
    lines.append(f"| Span-only recall (15 items) | {len(span_gold_ids & found_ids)}/{len(span_gold_ids)} ({100*span_recall:.0f}%) |")
    lines.append(f"| Derivation-only recall (5 items) | {len(deriv_gold_ids & found_ids)}/{len(deriv_gold_ids)} ({100*deriv_recall:.0f}%) |")
    lines.append(f"| Mode fidelity on matched | {total_mode_match}/{total_found} ({100*mode_rate:.0f}%) |")
    lines.append(f"| Kind agreement on matched | {total_kind_match}/{total_found} ({100*kind_rate:.0f}%) |")
    lines.append(f"| LLM validation pass rate | {total_validated}/{total_raw} ({100*validation_rate:.0f}%) |")
    lines.append(f"| Total validated events | {total_validated} ({total_span} span, {total_derivation} derivation) |")
    lines.append(f"| LLM events beyond gold | {total_extras} |")
    lines.append(f"| LLM validation dropped | {total_dropped} |")
    lines.append("")

    # Gate thresholds
    lines.append("## Gate thresholds")
    lines.append("")
    lines.append("| Metric | Result | Threshold | Verdict |")
    lines.append("|---|---:|---:|:---:|")
    lines.append(f"| Recall | {100*recall:.0f}% | ≥55% | {'PASS' if recall >= 0.55 else 'FAIL'} |")
    lines.append(f"| Validation pass rate | {100*validation_rate:.0f}% | ≥90% | {'PASS' if validation_rate >= 0.90 else 'FAIL'} |")
    lines.append(f"| Kind agreement | {100*kind_rate:.0f}% | ≥75% | {'PASS' if kind_rate >= 0.75 else 'FAIL'} |")
    lines.append(f"| Span recall | {100*span_recall:.0f}% | ≥60% | {'PASS' if span_recall >= 0.60 else 'FAIL'} |")
    lines.append(f"| Derivation recall | {100*deriv_recall:.0f}% | ≥40% | {'PASS' if deriv_recall >= 0.40 else 'FAIL'} |")
    lines.append("")

    lines.append("## Per-case")
    lines.append("")
    for r in results:
        lines.append(f"### `{r.case}`")
        lines.append("")
        lines.append(f"- raw: {r.raw_count}, validated: {r.validated_count} "
                     f"(span={r.span_mode_count}, derivation={r.derivation_mode_count}), "
                     f"dropped: {r.dropped_count}")
        lines.append(f"- gold recovered: {len(r.gold_found)}/{len(GOLD[r.case])} — "
                     f"found={r.gold_found}, missed={r.gold_missed}")
        lines.append(f"- mode match: {len(r.gold_mode_match)}/{len(r.gold_found)}")
        if r.gold_mode_mismatch:
            for gid, gm, lm in r.gold_mode_mismatch:
                lines.append(f"  - `{gid}`: gold=`{gm}` llm=`{lm}`")
        lines.append(f"- kind match: {len(r.gold_kind_match)}/{len(r.gold_found)}")
        if r.gold_kind_mismatch:
            for gid, gk, lk in r.gold_kind_mismatch:
                lines.append(f"  - `{gid}`: gold=`{gk}` llm=`{lk}`")
        lines.append(f"- extras (not in gold): {r.extra_events}")
        lines.append("")
        lines.append("<details><summary>all validated events</summary>")
        lines.append("")
        for i, e in enumerate(r.events_dump):
            amb = " [ambiguous]" if e["kind_ambiguity"] else ""
            turns_str = ",".join(str(t) for t in e["turns"])
            lines.append(
                f"{i+1}. [{e['mode']} / turns={turns_str} / {e['kind']}{amb}] {e['text']!r}"
            )
        lines.append("")
        lines.append("</details>")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport: {out_path}")


if __name__ == "__main__":
    run()
