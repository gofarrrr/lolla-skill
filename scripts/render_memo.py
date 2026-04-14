"""Deterministic markdown memo renderer from Lolla pipeline result.json.

No API calls, no LLM — pure template rendering. Reads result JSON and
produces a standalone markdown memo prioritized by signal strength.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _truncate_to_sentences(text: str, max_sentences: int = 2, max_chars: int = 120) -> str:
    """Truncate text to the first N sentences, with a hard character limit."""
    sentences = []
    for part in text.replace("? ", "?\n").replace(". ", ".\n").split("\n"):
        part = part.strip()
        if part:
            sentences.append(part)
            if len(sentences) >= max_sentences:
                break
    result = " ".join(sentences)
    # Hard truncate long single-sentence queries on clause boundaries
    if len(result) > max_chars:
        for sep in ["; ", ", where ", ", amid ", ", with "]:
            idx = result.find(sep)
            if 30 < idx <= max_chars:
                return result[:idx]
        # Word-boundary fallback
        return result[:max_chars].rsplit(" ", 1)[0]
    return result


_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def render_memo(result: dict) -> str:
    """Render a pipeline result dict into a standalone markdown memo."""
    sections: list[str] = []

    # Heading with decision context
    query = result.get("query", "")
    heading_context = _truncate_to_sentences(query) if query else "Reasoning Audit"
    sections.append(f"# Reasoning Audit: {heading_context}")

    # Key Findings — sorted by severity
    _render_findings(result, sections)

    # Mental Model Connections
    _render_companion(result, sections)

    # Frame Alternatives
    _render_frame_alternatives(result, sections)

    # Structural Gaps
    _render_structural_gaps(result, sections)

    # Delivery Check
    _render_delivery_check(result, sections)

    # Updated Position
    _render_updated_position(result, sections)

    # Pressure Check
    _render_pressure_check(result, sections)

    return "\n\n".join(sections) + "\n"


def _render_findings(result: dict, sections: list[str]) -> None:
    delta = result.get("delta_card")
    if not delta:
        return
    findings = delta.get("findings", [])
    if not findings:
        return
    sorted_findings = sorted(findings, key=lambda f: _SEVERITY_ORDER.get(f.get("severity", "low"), 2))
    lines = ["## Key Findings"]
    seen_passages: set[str] = set()
    for f in sorted_findings:
        name = f.get("tendency_name", "Unknown")
        severity = f.get("severity", "unknown")
        passage = f.get("specific_passage", "")
        challenge = f.get("challenge_statement", "")
        lines.append(f"**{name}** ({severity})")
        if passage and passage not in seen_passages:
            lines.append(f"> {passage[:200]}")
            seen_passages.add(passage)
        if challenge:
            lines.append(f"{challenge}")
    sections.append("\n\n".join(lines))


def _render_companion(result: dict, sections: list[str]) -> None:
    cs = result.get("companion_cheat_sheet")
    if not cs:
        return
    anchors = cs.get("anchors", [])
    if not anchors:
        return
    lines = ["## Mental Model Connections"]
    for a in anchors:
        name = a.get("display_name", "Unknown")
        explanation = a.get("presence_explanation", "")
        mode = a.get("presence_mode", "")
        entry = f"**{name}**"
        if mode:
            entry += f" ({mode})"
        entry += f" — {explanation}"
        lines.append(entry)
    sections.append("\n\n".join(lines))


def _render_frame_alternatives(result: dict, sections: list[str]) -> None:
    fp = result.get("frame_pressure_card")
    if not fp:
        return
    reframings = fp.get("reframings", [])
    if not reframings:
        return
    lines = ["## Frame Alternatives"]
    for r in reframings:
        question = r.get("reframed_question", "")
        opens = r.get("what_opens", "")
        lines.append(f"**{question}**")
        if opens:
            lines.append(f"{opens}")
    sections.append("\n\n".join(lines))


def _render_structural_gaps(result: dict, sections: list[str]) -> None:
    sc = result.get("structural_coverage_card")
    if not sc:
        return
    gaps = sc.get("gap_questions", [])
    if not gaps:
        return
    lines = ["## Structural Gaps"]
    for g in gaps:
        dim_name = g.get("dimension_name", g.get("dimension_id", "Unknown"))
        questions = g.get("questions", [])
        for q in questions:
            lines.append(f"**{dim_name}:** {q}")
    sections.append("\n\n".join(lines))


_BI_SUBTYPES = ("empty_rhetoric", "paltering", "weasel_words", "unverified_claims")


def _render_delivery_check(result: dict, sections: list[str]) -> None:
    bp = result.get("bullshit_profile")
    if not bp:
        return
    summary = bp.get("summary", {})
    total_clear = summary.get("total_clear", 0)
    if not total_clear:
        return
    # Find dominant subtype — handle both passage formats
    passages = bp.get("passages", [])
    subtype_counts: dict[str, int] = {}
    for p in passages:
        # Format A: subtype keys at passage level (real data)
        for st in _BI_SUBTYPES:
            det = p.get(st)
            if isinstance(det, dict) and det.get("detected") and det.get("severity") == "clear":
                subtype_counts[st] = subtype_counts.get(st, 0) + 1
        # Format B: detections array (test fixtures)
        for d in p.get("detections", []):
            if d.get("severity") == "clear":
                st = d.get("subtype", "unknown")
                subtype_counts[st] = subtype_counts.get(st, 0) + 1
    dominant = max(subtype_counts, key=subtype_counts.get) if subtype_counts else "unknown"
    dominant_display = dominant.replace("_", " ")
    sections.append(
        f"## Delivery Check\n\n"
        f"{total_clear} clear detections across {summary.get('passages_with_detections', 0)} passages. "
        f"Dominant pattern: **{dominant_display}**."
    )


def _render_updated_position(result: dict, sections: list[str]) -> None:
    revised = result.get("revised_answer")
    if not revised:
        return
    sections.append(f"## Updated Position\n\n{revised}")


_LANE_DISPLAY_NAMES = {
    "DeltaCard": "Structural Findings",
    "CompanionCheatSheet": "Mental Model Review",
    "FramePressureCard": "Frame Pressure Review",
    "StructuralCoverageCard": "Structural Coverage Review",
}


def _render_pressure_check(result: dict, sections: list[str]) -> None:
    gc = result.get("gap_check")
    if not gc:
        return
    lanes = gc.get("lanes", [])
    divergent_lanes = [l for l in lanes if l.get("divergences")]
    if not divergent_lanes:
        return
    lines = ["## Pressure Check"]
    for lane in divergent_lanes:
        raw_name = lane.get("lane_name", "Unknown")
        name = _LANE_DISPLAY_NAMES.get(raw_name, raw_name)
        lines.append(f"### {name}")
        for d in lane.get("divergences", []):
            # Handle both formats: {finding, explanation} and {description}
            description = d.get("description", "")
            finding = d.get("finding", "")
            explanation = d.get("explanation", "")
            if description:
                lines.append(f"- {description}")
            elif finding:
                lines.append(f"- **{finding}**: {explanation}")
    sections.append("\n\n".join(lines))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Lolla memo from result JSON")
    parser.add_argument("--result", required=True, help="Path to result JSON file")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")
    args = parser.parse_args()

    with open(args.result) as f:
        result = json.load(f)

    memo = render_memo(result)

    if args.output:
        Path(args.output).write_text(memo, encoding="utf-8")
        print(f"Memo written to {args.output}", file=sys.stderr)
    else:
        print(memo)
