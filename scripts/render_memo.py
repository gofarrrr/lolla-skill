"""Deterministic markdown memo renderer from Lolla pipeline result.json.

No API calls, no LLM — pure template rendering. Reads result JSON and
produces a standalone markdown memo prioritized by signal strength.
"""
from __future__ import annotations

import argparse
import json
import re
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
    if _has_decision_note(result):
        return _render_decision_note_memo(result)
    return _render_legacy_memo(result)


def _render_legacy_memo(result: dict) -> str:
    """Render the original deterministic memo shape for older result JSONs."""
    sections: list[str] = []
    sections.append(_legacy_heading(result))

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


def _legacy_heading(result: dict) -> str:
    # Heading with decision context — prefer the extraction's
    # decision_situation (concise one-liner). Fall back to the first user
    # turn's leading clause.
    extraction = result.get("extraction", {})
    decision_situation = extraction.get("decision_situation", "").strip()
    if decision_situation:
        heading_context = _truncate_to_sentences(decision_situation)
    else:
        first_user_turn = next(
            (t.get("text", "") for t in extraction.get("turns", []) if t.get("speaker") == "user"),
            "",
        )
        heading_context = _truncate_to_sentences(first_user_turn) if first_user_turn else "Reasoning Audit"
    return f"# Reasoning Audit: {heading_context}"


def _has_decision_note(result: dict) -> bool:
    return any(
        _clean_text(result.get(key))
        for key in (
            "memo_substantive_title",
            "memo_orientation_note",
            "memo_orientation_narrative",
            "memo_what_changed",
            "memo_what_still_holds",
            "memo_take_back_or_set_aside",
            "memo_pressure_check",
        )
    )


def _render_decision_note_memo(result: dict) -> str:
    """Render the upgraded memo: decision note first, audit trace second."""
    sections: list[str] = [_memo_heading(result)]

    orientation = _first_text(result, ["memo_orientation_note", "memo_orientation_narrative"])
    if orientation:
        sections.append(orientation)

    _append_markdown_section(
        sections,
        "What changed in the advice",
        _memo_field_or_revised_section(
            result,
            "memo_what_changed",
            ["What actually shifted"],
        ),
    )
    _append_markdown_section(
        sections,
        "What still holds",
        _memo_field_or_revised_section(
            result,
            "memo_what_still_holds",
            ["What survived"],
        ),
    )
    _append_markdown_section(
        sections,
        "What I'd take back or set aside",
        _memo_field_or_revised_section(
            result,
            "memo_take_back_or_set_aside",
            ["What I'd take back or set aside", "What I'd take back"],
        ),
    )

    pressure = _clean_text(result.get("memo_pressure_check"))
    if pressure:
        _append_markdown_section(sections, "One more pressure check", pressure)

    _render_unanswered_questions(result, sections)
    _render_audit_appendix(result, sections)

    return "\n\n".join(sections) + "\n"


def _memo_heading(result: dict) -> str:
    title = _clean_text(result.get("memo_substantive_title")).lstrip("#").strip()
    if title:
        return f"# {title}"
    return _legacy_heading(result)


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _first_text(result: dict, keys: list[str]) -> str:
    for key in keys:
        value = _clean_text(result.get(key))
        if value:
            return value
    return ""


def _memo_field_or_revised_section(result: dict, field: str, headings: list[str]) -> str:
    direct = _clean_text(result.get(field))
    if direct:
        return direct
    return extract_section(_clean_text(result.get("revised_answer")), headings)


def _append_markdown_section(sections: list[str], heading: str, body: str) -> None:
    body = _strip_duplicate_leading_heading(_clean_text(body), heading)
    if body:
        sections.append(f"## {heading}\n\n{body}")


def _strip_duplicate_leading_heading(text: str, heading: str) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines and _normalize_heading(lines[0]) == _normalize_heading(heading):
        return "\n".join(lines[1:]).strip()
    return text.strip()


def _render_unanswered_questions(result: dict, sections: list[str]) -> None:
    sc = result.get("structural_coverage_card") or {}
    gaps = sc.get("gap_questions") or []
    questions: list[str] = []
    for gap in gaps:
        for question in gap.get("questions") or []:
            question = _clean_text(question)
            if question and question not in questions:
                questions.append(question)
        single = _clean_text(gap.get("question"))
        if single and single not in questions:
            questions.append(single)
    if questions:
        lines = [f"- {q}" for q in questions]
        sections.append("## Questions still unanswered\n\n" + "\n".join(lines))


def _render_audit_appendix(result: dict, sections: list[str]) -> None:
    appendix_sections: list[str] = []
    _render_findings_appendix(result, appendix_sections)
    _render_companion_appendix(result, appendix_sections)
    _render_frame_appendix(result, appendix_sections)
    _render_delivery_profile_appendix(result, appendix_sections)
    if appendix_sections:
        sections.append("## Appendix: Audit trace\n\n" + "\n\n".join(appendix_sections))


def _render_findings_appendix(result: dict, sections: list[str]) -> None:
    delta = result.get("delta_card")
    if not delta:
        return
    findings = delta.get("findings", [])
    if not findings:
        return
    sorted_findings = sorted(findings, key=lambda f: _SEVERITY_ORDER.get(f.get("severity", "low"), 2))
    lines = ["### Challenge points"]
    seen_passages: set[str] = set()
    for f in sorted_findings:
        name = f.get("tendency_name", "Unknown")
        severity = f.get("severity", "unknown")
        challenge = _clean_text(f.get("challenge_statement"))
        passage = _clean_text(f.get("specific_passage"))
        if challenge:
            lines.append(f"- **{name}** ({severity}): {challenge}")
        else:
            lines.append(f"- **{name}** ({severity})")
        if passage and passage not in seen_passages:
            lines.append(f"  > {passage[:200]}")
            seen_passages.add(passage)
    sections.append("\n".join(lines))


def _render_companion_appendix(result: dict, sections: list[str]) -> None:
    cs = result.get("companion_cheat_sheet")
    if not cs:
        return
    anchors = cs.get("anchors", [])
    if not anchors:
        return
    lines = ["### Model connections"]
    for a in anchors:
        name = a.get("display_name", "Unknown")
        explanation = _clean_text(a.get("presence_explanation"))
        mode = _clean_text(a.get("presence_mode"))
        suffix = f" ({mode})" if mode else ""
        if explanation:
            lines.append(f"- **{name}**{suffix}: {explanation}")
        else:
            lines.append(f"- **{name}**{suffix}")
    sections.append("\n".join(lines))


def _render_frame_appendix(result: dict, sections: list[str]) -> None:
    fp = result.get("frame_pressure_card")
    if not fp:
        return
    reframings = fp.get("reframings", [])
    if not reframings:
        return
    lines = ["### Alternative frames"]
    for r in reframings:
        question = _clean_text(r.get("reframed_question"))
        opens = _clean_text(r.get("what_opens"))
        if question and opens:
            lines.append(f"- **{question}** {opens}")
        elif question:
            lines.append(f"- **{question}**")
    sections.append("\n".join(lines))


def _render_delivery_profile_appendix(result: dict, sections: list[str]) -> None:
    text = _delivery_check_text(result)
    if text:
        sections.append(f"### Delivery profile\n\n{text}")


def _delivery_check_text(result: dict) -> str:
    bp = result.get("bullshit_profile")
    if not bp:
        return ""
    summary = bp.get("summary", {})
    total_clear = summary.get("total_clear", 0)
    if not total_clear:
        return ""
    passages = bp.get("passages", [])
    subtype_counts: dict[str, int] = {}
    for p in passages:
        for st in _BI_SUBTYPES:
            det = p.get(st)
            if isinstance(det, dict) and det.get("detected") and det.get("severity") == "clear":
                subtype_counts[st] = subtype_counts.get(st, 0) + 1
        for d in p.get("detections", []):
            if d.get("severity") == "clear":
                st = d.get("subtype", "unknown")
                subtype_counts[st] = subtype_counts.get(st, 0) + 1
    dominant = max(subtype_counts, key=subtype_counts.get) if subtype_counts else "unknown"
    dominant_display = dominant.replace("_", " ")
    return (
        f"{total_clear} clear detections across {summary.get('passages_with_detections', 0)} passages. "
        f"Dominant pattern: **{dominant_display}**."
    )


def extract_section(markdown: str, possible_headings: list[str]) -> str:
    """Extract a markdown or §N section by heading text.

    Accepts headings like ``### What actually shifted`` and
    ``§3 What actually shifted``. Returns an empty string when absent.
    """
    if not markdown:
        return ""
    wanted = {_normalize_heading(h) for h in possible_headings}
    lines = markdown.splitlines()
    for i, line in enumerate(lines):
        info = _heading_info(line)
        if not info:
            continue
        _, level, title = info
        if _normalize_heading(title) not in wanted:
            continue
        end = len(lines)
        for j in range(i + 1, len(lines)):
            next_info = _heading_info(lines[j])
            if not next_info:
                continue
            next_kind, next_level, _ = next_info
            if next_kind == "section" or next_level <= level:
                end = j
                break
        return "\n".join(lines[i + 1:end]).strip()
    return ""


def _heading_info(line: str) -> tuple[str, int, str] | None:
    md = re.match(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$", line)
    if md:
        return ("markdown", len(md.group(1)), md.group(2).strip())
    section = re.match(r"^\s*§\s*\d+\s+(.+?)\s*$", line)
    if section:
        return ("section", 3, section.group(1).strip())
    return None


def _normalize_heading(text: str) -> str:
    text = _clean_text(text).replace("’", "'")
    text = re.sub(r"^\s*#+\s*", "", text)
    text = re.sub(r"^\s*§\s*\d+\s*", "", text)
    text = re.sub(r"[^a-zA-Z0-9']+", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


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
