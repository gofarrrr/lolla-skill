#!/usr/bin/env python3
"""Phase 5.5 dropped_threads specialist — evaluation against Phase 5.5 gold.

For each of the 8 gate cases (parenting_teen and startup_pivot excluded
since they have zero dropped_threads in monolith output), runs
`extract_dropped_threads` with a live OpenRouter boundary, then compares
LLM output to the 9 gold items from
`research/phase5.5-dropped-threads-annotation-gate-2026-04-24.md`.

Measures per case:
  - recall
  - speaker agreement on matched events
  - kind agreement on matched events
  - validation pass rate
  - extras

Writes `research/phase5.5-dropped-threads-eval-2026-04-24.md`.

Cost: ~$1-3 across 8 LLM calls.

Usage:
    python3 scripts/phase5.5_dropped_threads_eval.py
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
from system_b.dropped_threads_extraction import extract_dropped_threads


# Gold items from the Phase 5.5 gate.
# Tuple form: (item_id, turn_index, speaker, kind, snippet)
GOLD: dict[str, list[dict]] = {
    "user_has_plan": [
        {"id": "UHP-D1", "turn": 1, "speaker": "user", "kind": "open_loop",
         "snippet": "help me think through the launch plan"},
    ],
    "whistleblower": [
        {"id": "WB-D1", "turn": 7, "speaker": "user", "kind": "open_loop",
         "snippet": "implicate her for not reporting"},
    ],
    "multi_offer": [
        {"id": "MO-D1", "turn": 4, "speaker": "user", "kind": "open_loop",
         "snippet": "80% of startups don't exit"},
    ],
    "oncologist": [
        {"id": "ONC-D1", "turn": 2, "speaker": "user", "kind": "open_loop",
         "snippet": "feeling a little stuck"},
        {"id": "ONC-D2", "turn": 2, "speaker": "user", "kind": "open_loop",
         "snippet": "David who could take them but he's already slammed"},
    ],
    "phd_research": [
        {"id": "PHD-D1", "turn": 3, "speaker": "assistant", "kind": "open_loop",
         "snippet": "the latter isn't, based on what you've described"},
    ],
    "real_estate": [
        {"id": "RE-D1", "turn": 4, "speaker": "user", "kind": "open_loop",
         "snippet": "we'll regret walking away over $45K"},
    ],
    "friendship_money": [
        {"id": "FRI-D1", "turn": 4, "speaker": "user", "kind": "open_loop",
         "snippet": "going to be homeless"},
    ],
    "messy_three_problems": [
        {"id": "MSY-D1", "turn": 2, "speaker": "user", "kind": "open_loop",
         "snippet": "I love DC and my whole life is here"},
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
    user_raised_count: int = 0
    assistant_raised_count: int = 0
    gold_found: list[str] = field(default_factory=list)
    gold_missed: list[str] = field(default_factory=list)
    gold_speaker_match: list[str] = field(default_factory=list)
    gold_speaker_mismatch: list[tuple[str, str, str]] = field(default_factory=list)
    gold_kind_match: list[str] = field(default_factory=list)
    gold_kind_mismatch: list[tuple[str, str, str]] = field(default_factory=list)
    extra_events: int = 0
    events_dump: list[dict] = field(default_factory=list)


def _event_turn(event) -> int:
    return event.provenance.span_ref.turn_index


def _event_speaker(event) -> str:
    return event.provenance.span_ref.speaker


def _match_gold(gold_item, events, consumed):
    snippet_lc = gold_item["snippet"].lower()
    gold_turn = gold_item["turn"]
    for i, event in enumerate(events):
        if i in consumed:
            continue
        if _event_turn(event) != gold_turn:
            continue
        event_text_lc = event.text.lower()
        # Bidirectional substring — LLM span may be tighter or broader than gold snippet
        if snippet_lc in event_text_lc or event_text_lc in snippet_lc:
            return i
        # Fallback: any 4-consecutive-word overlap
        gold_words = snippet_lc.split()
        for start in range(len(gold_words) - 3):
            chunk = " ".join(gold_words[start:start + 4])
            if chunk in event_text_lc:
                return i
    return None


def _match_case(gold_case, events):
    result = CaseResult(case=gold_case[0]["id"].split("-")[0])
    consumed: set[int] = set()
    for gold in gold_case:
        idx = _match_gold(gold, events, consumed)
        if idx is None:
            result.gold_missed.append(gold["id"])
            continue
        consumed.add(idx)
        result.gold_found.append(gold["id"])
        event = events[idx]
        ev_speaker = _event_speaker(event)
        if ev_speaker == gold["speaker"]:
            result.gold_speaker_match.append(gold["id"])
        else:
            result.gold_speaker_mismatch.append((gold["id"], gold["speaker"], ev_speaker))
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

        try:
            events, stats = extract_dropped_threads(context=context, boundary=boundary)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            continue

        result = _match_case(GOLD[case], events)
        result.case = case
        result.raw_count = stats.raw_count
        result.validated_count = stats.validated_count
        result.user_raised_count = stats.user_raised_count
        result.assistant_raised_count = stats.assistant_raised_count
        result.dropped_count = (
            stats.dropped_invalid_kind
            + stats.dropped_invalid_speaker
            + stats.dropped_invalid_turn
            + stats.dropped_not_substring
            + stats.dropped_speaker_mismatch
        )
        result.events_dump = [
            {
                "text": e.text[:120],
                "turn": _event_turn(e),
                "speaker": _event_speaker(e),
                "kind": e.kind,
                "kind_ambiguity": e.kind_ambiguity,
                "superseded_by": (e.superseded_by or "")[:100],
            }
            for e in events
        ]
        results.append(result)

        print(f"  raw={stats.raw_count} validated={stats.validated_count} "
              f"(user={stats.user_raised_count}, assistant={stats.assistant_raised_count}) "
              f"dropped={result.dropped_count}")
        print(f"  gold_found={len(result.gold_found)}/{len(GOLD[case])} "
              f"missed={result.gold_missed}")
        print(f"  speaker_match={len(result.gold_speaker_match)}/{len(result.gold_found)} "
              f"kind_match={len(result.gold_kind_match)}/{len(result.gold_found)}")
        print(f"  extras={result.extra_events}")

    duration = time.monotonic() - started
    _write_report(results, duration)


def _write_report(results: list[CaseResult], duration: float) -> None:
    out_path = REPO_ROOT / "research" / "phase5.5-dropped-threads-eval-2026-04-24.md"
    lines: list[str] = []
    lines.append("# Phase 5.5 dropped_threads — evaluation vs Phase 5.5 gold")
    lines.append("")
    lines.append(f"**Date:** 2026-04-24  **Cases:** {len(results)} / 8  **Wall time:** {duration:.1f}s")
    lines.append("")

    total_gold = sum(len(GOLD[r.case]) for r in results)
    total_found = sum(len(r.gold_found) for r in results)
    total_speaker = sum(len(r.gold_speaker_match) for r in results)
    total_kind = sum(len(r.gold_kind_match) for r in results)
    total_raw = sum(r.raw_count for r in results)
    total_validated = sum(r.validated_count for r in results)
    total_extras = sum(r.extra_events for r in results)
    total_dropped = sum(r.dropped_count for r in results)
    total_user = sum(r.user_raised_count for r in results)
    total_assistant = sum(r.assistant_raised_count for r in results)

    recall = (total_found / total_gold) if total_gold else 0.0
    speaker_rate = (total_speaker / total_found) if total_found else 0.0
    kind_rate = (total_kind / total_found) if total_found else 0.0
    validation_rate = (total_validated / total_raw) if total_raw else 0.0

    lines.append("## Aggregate")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Gold items total | {total_gold} |")
    lines.append(f"| Gold recovered | {total_found} ({100*recall:.0f}%) |")
    lines.append(f"| Speaker agreement on matched | {total_speaker}/{total_found} ({100*speaker_rate:.0f}%) |")
    lines.append(f"| Kind agreement on matched | {total_kind}/{total_found} ({100*kind_rate:.0f}%) |")
    lines.append(f"| Validation pass rate | {total_validated}/{total_raw} ({100*validation_rate:.0f}%) |")
    lines.append(f"| User-raised events | {total_user} |")
    lines.append(f"| Assistant-raised events | {total_assistant} |")
    lines.append(f"| Events beyond gold | {total_extras} |")
    lines.append(f"| Validation dropped | {total_dropped} |")
    lines.append("")

    lines.append("## Gate thresholds")
    lines.append("")
    lines.append("| Metric | Result | Threshold | Verdict |")
    lines.append("|---|---:|---:|:---:|")
    lines.append(f"| Recall | {100*recall:.0f}% | ≥55% | {'PASS' if recall >= 0.55 else 'FAIL'} |")
    lines.append(f"| Validation pass rate | {100*validation_rate:.0f}% | ≥90% | {'PASS' if validation_rate >= 0.90 else 'FAIL'} |")
    lines.append(f"| Speaker agreement | {100*speaker_rate:.0f}% | ≥90% | {'PASS' if speaker_rate >= 0.90 else 'FAIL'} |")
    lines.append(f"| Kind agreement | {100*kind_rate:.0f}% | ≥75% | {'PASS' if kind_rate >= 0.75 else 'FAIL'} |")
    lines.append("")

    lines.append("## Per-case")
    lines.append("")
    for r in results:
        lines.append(f"### `{r.case}`")
        lines.append("")
        lines.append(f"- raw: {r.raw_count}, validated: {r.validated_count} "
                     f"(user={r.user_raised_count}, assistant={r.assistant_raised_count}), "
                     f"dropped: {r.dropped_count}")
        lines.append(f"- gold recovered: {len(r.gold_found)}/{len(GOLD[r.case])} — "
                     f"found={r.gold_found}, missed={r.gold_missed}")
        lines.append(f"- speaker: {len(r.gold_speaker_match)}/{len(r.gold_found)}, "
                     f"kind: {len(r.gold_kind_match)}/{len(r.gold_found)}")
        if r.gold_speaker_mismatch:
            for gid, gs, ls in r.gold_speaker_mismatch:
                lines.append(f"  - speaker mismatch `{gid}`: gold=`{gs}` llm=`{ls}`")
        if r.gold_kind_mismatch:
            for gid, gk, lk in r.gold_kind_mismatch:
                lines.append(f"  - kind mismatch `{gid}`: gold=`{gk}` llm=`{lk}`")
        lines.append(f"- extras: {r.extra_events}")
        lines.append("")
        lines.append("<details><summary>all validated events</summary>")
        lines.append("")
        for i, e in enumerate(r.events_dump):
            amb = " [ambiguous]" if e["kind_ambiguity"] else ""
            lines.append(f"{i+1}. [turn {e['turn']} / {e['speaker']} / {e['kind']}{amb}] "
                         f"{e['text']!r} → superseded_by: {e['superseded_by']!r}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport: {out_path}")


if __name__ == "__main__":
    run()
