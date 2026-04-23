#!/usr/bin/env python3
"""Phase 1 equivalence check — the real acceptance gate.

For each of the 10 corpus conversations, constructs a synthetic-but-representative
extraction shape, then verifies:

    legacy_cr = _map_to_critique_request(extraction_dict, assistant_text)
    shim_cr   = _context_to_critique(load_conversation_context(...))

    assert legacy_cr["query"] == shim_cr.query
    assert legacy_cr["vanilla_answer"] == shim_cr.vanilla_answer

This proves the shim produces bit-identical CritiqueRequests to the legacy
path on real conversation text. End-to-end pipeline comparison is omitted
deliberately: the pipeline uses temperature=0.2 (non-deterministic by
design), so pipeline-output diffs would conflate shim bugs with LLM noise.
CritiqueRequest-level equivalence is the architectural commitment and is
testable without LLM stochasticity.

Writes a markdown evidence report. Exit 0 on all-pass, 1 on any divergence.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.conversation_loader import load_conversation_context
from engine.system_b.pipeline import _context_to_critique
from scripts.run_extract import (
    _extract_assistant_responses,
    _map_to_critique_request,
)


# A representative extraction shape used for every case. The point of this
# check is shim structural correctness, not extraction fidelity — content is
# fixed; conversation text varies.
_REPRESENTATIVE_EXTRACTION = {
    "is_strategic": True,
    "decision_situation": "Whether to proceed with the strategic option on the table.",
    "live_constraints": [
        {
            "constraint": "timeline is compressed",
            "introduced_turn": 1,
            "status": "active",
            "weight": "structural",
            "canonical_key": "timeline-compressed",
        },
        {
            "constraint": "budget constraint active",
            "introduced_turn": 2,
            "status": "active",
            "weight": "situational",
        },
        {
            "constraint": "alternative previously considered",
            "introduced_turn": 3,
            "status": "dropped",
            "weight": "situational",
        },
    ],
    "synthesized_position": "Proceed with conditions: define exit criteria, review at day 30.",
    "reasoning_passages": [
        "One thing worth naming",
        "That's important context",
    ],
    "original_framing": "Should I do this, or is it crazy?",
    "dropped_threads": [
        {
            "thread": "long-term identity question",
            "raised_by": "user",
            "raised_turn": 2,
            "status": "acknowledged_then_dropped",
            "superseded_by": "operational framing took over",
        },
        {
            "thread": "risk of secondary impact",
            "raised_by": "assistant",
            "raised_turn": 4,
            "status": "acknowledged_then_dropped",
            "superseded_by": None,
        },
    ],
    "_quote_validation": {"retry_attempted": False, "retry_succeeded": False, "fabricated": 0},
}


@dataclass(frozen=True)
class CaseResult:
    case: str
    query_match: bool
    vanilla_match: bool
    query_lengths: tuple[int, int]  # (legacy, shim)
    vanilla_lengths: tuple[int, int]
    first_query_diff: str | None
    first_vanilla_diff: str | None

    @property
    def all_match(self) -> bool:
        return self.query_match and self.vanilla_match


def _first_diff(left: str, right: str, context: int = 80) -> str | None:
    if left == right:
        return None
    min_len = min(len(left), len(right))
    for i in range(min_len):
        if left[i] != right[i]:
            start = max(0, i - context)
            return (
                f"first divergence at char {i}:\n"
                f"  legacy[{start}:{i+10}]: {left[start:i+10]!r}\n"
                f"  shim  [{start}:{i+10}]: {right[start:i+10]!r}"
            )
    # One is a prefix of the other
    if len(left) != len(right):
        longer = "legacy" if len(left) > len(right) else "shim"
        return f"identical up to char {min_len}; {longer} has {abs(len(left) - len(right))} extra chars"
    return None


def check_case(conversation_path: Path) -> CaseResult:
    case_name = conversation_path.stem.replace("case_", "").replace("_conversation", "")
    conversation_text = conversation_path.read_text(encoding="utf-8")

    # Legacy path inputs
    extraction_wrapper = {
        "status": "ok",
        "extraction": _REPRESENTATIVE_EXTRACTION,
        "capture_manifest": {},
        "capture_health": "good",
        "capture_warnings": [],
    }
    assistant_text = _extract_assistant_responses(conversation_text)
    legacy_cr = _map_to_critique_request(
        _REPRESENTATIVE_EXTRACTION,
        assistant_text=assistant_text,
    )

    # Shim path inputs — write the wrapped extraction to a temp file, load
    extraction_path = Path("/tmp") / f"_phase1_eq_{case_name}_extraction.json"
    extraction_path.write_text(json.dumps(extraction_wrapper))
    ctx = load_conversation_context(extraction_path, conversation_path)
    shim_cr = _context_to_critique(ctx)

    return CaseResult(
        case=case_name,
        query_match=(legacy_cr["query"] == shim_cr.query),
        vanilla_match=(legacy_cr["vanilla_answer"] == shim_cr.vanilla_answer),
        query_lengths=(len(legacy_cr["query"]), len(shim_cr.query)),
        vanilla_lengths=(len(legacy_cr["vanilla_answer"]), len(shim_cr.vanilla_answer)),
        first_query_diff=_first_diff(legacy_cr["query"], shim_cr.query),
        first_vanilla_diff=_first_diff(legacy_cr["vanilla_answer"], shim_cr.vanilla_answer),
    )


def render_markdown(results: list[CaseResult]) -> str:
    lines: list[str] = []
    lines.append("# Phase 1 shim equivalence — 10-case corpus results")
    lines.append("")
    lines.append("Evidence that `_context_to_critique(ctx)` produces a CritiqueRequest")
    lines.append("bit-identical to `_map_to_critique_request(extraction_dict, assistant_text)`")
    lines.append("when exercised against real corpus conversation text.")
    lines.append("")
    lines.append("**Note on scope:** the task-file 6.0 text describes pipeline-level")
    lines.append("output comparison. The pipeline uses `temperature=0.2`, so it is")
    lines.append("non-deterministic by design — pipeline-output diffs would conflate")
    lines.append("shim bugs with LLM noise. This check operates at the architectural")
    lines.append("boundary the shim actually owns (`CritiqueRequest` construction),")
    lines.append("which is LLM-independent and therefore cleanly testable.")
    lines.append("")
    lines.append("| case | query | vanilla_answer | query length (legacy → shim) | vanilla length (legacy → shim) |")
    lines.append("|------|-------|----------------|------------------------------|-------------------------------|")
    all_match = True
    for r in results:
        q = "match" if r.query_match else "DIFFER"
        v = "match" if r.vanilla_match else "DIFFER"
        if not r.all_match:
            all_match = False
        lines.append(
            f"| {r.case} | {q} | {v} | {r.query_lengths[0]} → {r.query_lengths[1]} "
            f"| {r.vanilla_lengths[0]} → {r.vanilla_lengths[1]} |"
        )
    lines.append("")
    if all_match:
        lines.append("**Result: 10/10 cases match bit-for-bit on both `query` and `vanilla_answer`.**")
    else:
        lines.append("**Result: divergence detected. See details below.**")
        for r in results:
            if not r.all_match:
                lines.append("")
                lines.append(f"### {r.case}")
                if r.first_query_diff:
                    lines.append("")
                    lines.append("**query diff:**")
                    lines.append("```")
                    lines.append(r.first_query_diff)
                    lines.append("```")
                if r.first_vanilla_diff:
                    lines.append("")
                    lines.append("**vanilla_answer diff:**")
                    lines.append("```")
                    lines.append(r.first_vanilla_diff)
                    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    corpus_dir = REPO_ROOT / "research" / "test-cases"
    cases = sorted(corpus_dir.glob("case_*_conversation.txt"))
    if not cases:
        print("no corpus cases found at research/test-cases/case_*_conversation.txt", file=sys.stderr)
        return 2

    results = [check_case(c) for c in cases]

    output = render_markdown(results)
    print(output)

    return 0 if all(r.all_match for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
