#!/usr/bin/env python3
"""Phase 3b stance extraction — evaluation against the Phase 3.0 annotation gate.

For each of the 5 protected cases, runs `extract_stance_events` with a live
OpenRouter boundary, then compares LLM output to the 20 gold candidates from
`research/phase3-assistant-trajectory-annotation-gate-2026-04-24.md`.

Measures per case:
  - recall: how many gold candidate spans did the LLM find?
  - total LLM output
  - validation pass rate (how many LLM candidates passed the substring check)
  - relation agreement for matched spans (against Reviewer A/B agreed answer)

Writes `research/phase3b-stance-extraction-eval-2026-04-24.md` with aggregates.

Cost: ~$1-3 across 5 LLM calls.

Usage:
    python3 scripts/phase3b_stance_extraction_eval.py
"""
from __future__ import annotations

import json
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
from system_b.stance_extraction import extract_stance_events


# Gold candidates from the Phase 3.0 annotation gate.
# Each entry: (candidate_id, assistant_turn_index, expected_relation_agreed)
# where expected_relation_agreed is what both reviewers converged on,
# or the dominant relation if reviewers used single vs ambiguous.
GOLD = {
    "user_has_plan": [
        ("UHP-S1", 2, "revision"),
        ("UHP-S2", 3, "qualification"),
        ("UHP-S3", 7, "condition"),
        ("UHP-S4", 7, "condition"),
    ],
    "whistleblower": [
        ("WB-S1", 1, "commitment"),
        ("WB-S2", 4, "commitment"),
        ("WB-S3", 6, "commitment"),
        ("WB-S4", 8, "commitment"),
    ],
    "parenting_teen": [
        ("PT-S1", 2, "revision"),
        ("PT-S2", 3, "commitment"),  # also has deferral; primary = commitment
        ("PT-S3", 7, "commitment"),
        ("PT-S4", 11, "commitment"),
    ],
    "multi_offer": [
        ("MO-S1", 4, "revision"),
        ("MO-S2", 6, "revision"),
        ("MO-S3", 9, "revision"),
        ("MO-S4", 15, "condition"),
    ],
    "startup_pivot": [
        ("SP-S1", 2, "condition"),
        ("SP-S2", 4, "commitment"),
        ("SP-S3", 6, "deferral"),  # also has condition; primary = deferral
        ("SP-S4", 7, "revision"),
    ],
}

# Gold span texts (first ~40 chars each, for fuzzy matching to LLM output)
# These are substrings within the candidate texts used to identify matches.
GOLD_SPAN_SNIPPETS = {
    "UHP-S1": '"if you were independent, we\'d consider you"',
    "UHP-S2": "the tactical advice — pricing, positioning",
    "UHP-S3": "Launching in 6 weeks is viable",
    "UHP-S4": "If after 4 weeks you have zero fractional commitments",
    "WB-S1": "I cannot give you legal advice",
    "WB-S2": "your most protected path is probably a whistleblower attorney",
    "WB-S3": "At 60-65% confidence in internal handling",
    "WB-S4": "Within 7-14 days: with attorney, make the filing",
    "PT-S1": "The first move here isn't to push on the 19-year-old",
    "PT-S2": "you don't call the police today",
    "PT-S3": "if your goal is protecting her, not reporting",
    "PT-S4": "This week: DON'T report to police",
    "MO-S1": "It's not actually a financial decision",
    "MO-S2": 'So it\'s not really "B is risky for the marriage',
    "MO-S3": "So A answers a question you probably already know",
    "MO-S4": "If the wife conversation goes well, take B",
    "SP-S1": "If two of three say yes, you have enough signal",
    "SP-S2": "option three, then option one if the pivot confirms",
    "SP-S3": "Give yourself 14 days",
    "SP-S4": "Those conversations are the bottleneck",
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
    gold_found: list[str] = field(default_factory=list)
    gold_missed: list[str] = field(default_factory=list)
    gold_relation_match: list[tuple[str, str, str]] = field(default_factory=list)  # (gold_id, gold_rel, llm_rel)
    gold_relation_mismatch: list[tuple[str, str, str]] = field(default_factory=list)
    extra_llm_events: int = 0  # LLM found valid stance events not in gold set
    llm_events_dump: list[dict] = field(default_factory=list)


def _match_gold_to_llm(gold_case: list, llm_stances: list) -> CaseResult:
    """For each gold candidate, see if any LLM stance's text contains the gold snippet.
    Score relation agreement on matched pairs."""
    result = CaseResult(case=gold_case[0][0].split("-")[0])
    consumed_llm_indices: set[int] = set()

    for gold_id, gold_turn, gold_rel in gold_case:
        snippet = GOLD_SPAN_SNIPPETS[gold_id]
        matched_idx = None
        for i, stance in enumerate(llm_stances):
            if i in consumed_llm_indices:
                continue
            if stance.turn_index != gold_turn:
                continue
            # Substring match: gold snippet appears in LLM's text OR vice versa
            if snippet.lower() in stance.text.lower() or stance.text.lower() in snippet.lower():
                matched_idx = i
                break
        if matched_idx is not None:
            result.gold_found.append(gold_id)
            consumed_llm_indices.add(matched_idx)
            llm_rel = llm_stances[matched_idx].stance
            if llm_rel == gold_rel:
                result.gold_relation_match.append((gold_id, gold_rel, llm_rel))
            else:
                result.gold_relation_mismatch.append((gold_id, gold_rel, llm_rel))
        else:
            result.gold_missed.append(gold_id)

    result.extra_llm_events = len(llm_stances) - len(consumed_llm_indices)
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
            print(f"  SKIP: missing artifacts")
            continue

        context = load_conversation_context(ext_path, conv_path)

        try:
            llm_stances, stats = extract_stance_events(context=context, boundary=boundary)
        except Exception as exc:
            print(f"  ERROR: {exc}")
            continue

        gold_case = GOLD[case]
        result = _match_gold_to_llm(gold_case, llm_stances)
        result.case = case
        result.raw_count = stats.raw_count
        result.validated_count = stats.validated_count
        result.dropped_count = (
            stats.dropped_invalid_turn
            + stats.dropped_invalid_relation
            + stats.dropped_not_substring
        )
        result.llm_events_dump = [
            {
                "text": s.text[:120],
                "turn_index": s.turn_index,
                "relation": s.stance,
                "relation_ambiguity": s.relation_ambiguity,
            }
            for s in llm_stances
        ]
        results.append(result)

        print(
            f"  raw={stats.raw_count} validated={stats.validated_count} "
            f"dropped={result.dropped_count}"
        )
        print(f"  gold_found={len(result.gold_found)}/{len(gold_case)} "
              f"gold_missed={result.gold_missed}")
        print(f"  relation_match={len(result.gold_relation_match)}/"
              f"{len(result.gold_found)}")
        if result.gold_relation_mismatch:
            for gid, gr, lr in result.gold_relation_mismatch:
                print(f"    mismatch {gid}: gold={gr} llm={lr}")
        print(f"  extra_llm_events={result.extra_llm_events}")

    duration = time.monotonic() - started
    _write_report(results, duration)


def _write_report(results: list[CaseResult], duration: float) -> None:
    out_path = REPO_ROOT / "research" / "phase3b-stance-extraction-eval-2026-04-24.md"
    lines: list[str] = []
    lines.append("# Phase 3b stance extraction — evaluation vs Phase 3.0 gold")
    lines.append("")
    lines.append(
        f"**Date:** 2026-04-24  "
        f"**Cases:** {len(results)} / 5  **Wall time:** {duration:.1f}s"
    )
    lines.append("")
    lines.append(
        "Runs `extract_stance_events` on each of the 5 annotation-gate cases and "
        "compares LLM output to the 20 gold candidate spans. Measures recall of the "
        "gold candidates, relation-label agreement on matched spans, and the count "
        "of additional LLM-produced stance events (which may be legitimate and just "
        "not in the 4-per-case gold sampling)."
    )
    lines.append("")

    # Aggregate
    total_gold = sum(len(GOLD[r.case]) for r in results)
    total_found = sum(len(r.gold_found) for r in results)
    total_rel_match = sum(len(r.gold_relation_match) for r in results)
    total_extra = sum(r.extra_llm_events for r in results)
    total_raw = sum(r.raw_count for r in results)
    total_validated = sum(r.validated_count for r in results)
    total_dropped = sum(r.dropped_count for r in results)
    recall = (total_found / total_gold) if total_gold else 0.0
    rel_agree = (total_rel_match / total_found) if total_found else 0.0
    validation_rate = (total_validated / total_raw) if total_raw else 0.0

    lines.append("## Aggregate")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Gold candidates total | {total_gold} |")
    lines.append(f"| Gold candidates recovered by LLM | {total_found} ({100*recall:.0f}%) |")
    lines.append(f"| Relation agreement on matched spans | {total_rel_match}/{total_found} ({100*rel_agree:.0f}%) |")
    lines.append(f"| LLM stance events beyond gold | {total_extra} (may be legit — gold was 4-per-case sample) |")
    lines.append(f"| LLM validation pass rate | {total_validated}/{total_raw} ({100*validation_rate:.0f}%) |")
    lines.append(f"| LLM validation dropped | {total_dropped} |")
    lines.append("")

    lines.append("## Per-case")
    lines.append("")
    for r in results:
        lines.append(f"### `{r.case}`")
        lines.append("")
        lines.append(f"- raw LLM events: {r.raw_count}")
        lines.append(f"- validated: {r.validated_count} (dropped: {r.dropped_count})")
        lines.append(f"- gold recovered: {len(r.gold_found)}/{len(GOLD[r.case])} — found={r.gold_found}, missed={r.gold_missed}")
        lines.append(f"- relation match: {len(r.gold_relation_match)}/{len(r.gold_found)}")
        if r.gold_relation_mismatch:
            for gid, gr, lr in r.gold_relation_mismatch:
                lines.append(f"  - `{gid}`: gold=`{gr}` llm=`{lr}`")
        lines.append(f"- extra LLM events (not in gold): {r.extra_llm_events}")
        lines.append("")
        lines.append("<details><summary>all LLM events this run</summary>")
        lines.append("")
        for i, e in enumerate(r.llm_events_dump):
            amb = " [ambiguous]" if e["relation_ambiguity"] else ""
            lines.append(f"{i+1}. [turn {e['turn_index']} / {e['relation']}{amb}] {e['text']!r}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport: {out_path}")


if __name__ == "__main__":
    run()
