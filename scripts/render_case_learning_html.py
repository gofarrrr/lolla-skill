"""Deterministic HTML case-learning artifact renderer.

Reads a Lolla ``result.json`` and produces a standalone HTML file. The
artifact is intentionally not a prettier Markdown memo: it keeps the decision
note opening, then turns the run into a small learning surface around the
reasoning pattern, selected mental models, reusable questions, and a collapsed
technical trace.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from typing import Any


MAX_SHIFTS = 4
MAX_MODEL_CARDS = 4
MAX_FRAME_CARDS = 3
MAX_QUESTIONS = 6


def render_case_learning_html(result: dict[str, Any]) -> str:
    """Render a result dict into a self-contained HTML artifact."""
    title = _artifact_title(result)
    orientation = _orientation(result)
    shifts = _extract_shift_items(_first_text(result, ["memo_what_changed"]))
    if not shifts:
        shifts = _fallback_shift_items(result)
    model_cards = _model_cards(result)
    frame_cards = _frame_cards(result)
    questions = _open_questions(result)
    pattern = _reasoning_pattern(result, model_cards, frame_cards, questions)

    body = f"""
<header class="hero">
  <div class="eyebrow">Lolla case learning artifact</div>
  <h1>{_esc(title)}</h1>
  {_trust_strip(result)}
  {_orientation_html(orientation)}
</header>

<main>
  <section class="section" id="changed">
    <div class="section-kicker">01</div>
    <div class="section-head">
      <h2>What Changed</h2>
      <p>The artifact opens where the memo opens: the useful output is the shift in the advice.</p>
    </div>
    {_shift_grid(shifts)}
  </section>

  <section class="section learning" id="lesson">
    <div class="section-kicker">02</div>
    <div class="section-head">
      <h2>What This Case Teaches</h2>
      <p>A compact chain from observed reasoning pattern to reusable question.</p>
    </div>
    {_pattern_chain(pattern)}
  </section>

  <section class="section" id="models">
    <div class="section-kicker">03</div>
    <div class="section-head">
      <h2>Mental Models Worth Learning</h2>
      <p>Only the clearest lenses are shown. Each card explains why the model mattered here and how to reuse it.</p>
    </div>
    {_model_grid(model_cards)}
  </section>

  <section class="section" id="questions">
    <div class="section-kicker">04</div>
    <div class="section-head">
      <h2>Questions Still Open</h2>
      <p>These are user-answerable checks, not AI-filled blanks.</p>
    </div>
    {_question_grid(questions)}
  </section>

{_optional_frame_section(frame_cards)}
{_technical_trace(result)}
</main>
"""
    return _html_document(title, body, _structured_payload(result, title, shifts, model_cards, questions))


def _artifact_title(result: dict[str, Any]) -> str:
    title = _clean(result.get("memo_substantive_title")).lstrip("#").strip()
    if title:
        return title
    extraction = result.get("extraction") or {}
    decision = _clean(extraction.get("decision_situation"))
    if decision:
        return _truncate(decision, 110)
    first_user = next(
        (
            _clean(turn.get("text"))
            for turn in extraction.get("turns", [])
            if turn.get("speaker") == "user"
        ),
        "",
    )
    return _truncate(first_user, 110) if first_user else "Reasoning case learning artifact"


def _orientation(result: dict[str, Any]) -> str:
    direct = _first_text(result, ["memo_orientation_note", "memo_orientation_narrative"])
    if direct:
        return direct
    extraction = result.get("extraction") or {}
    decision = _clean(extraction.get("decision_situation"))
    if decision:
        return (
            "This artifact turns the audit into a compact learning surface. "
            f"The case was: {decision}"
        )
    return "This artifact turns the audit into a compact learning surface: what changed, why it changed, and what to ask next time."


def _trust_strip(result: dict[str, Any]) -> str:
    health = result.get("run_health") or {}
    bits = [
        ("Run", health.get("overall", result.get("status", "unknown"))),
        ("Capture", health.get("capture", "unknown")),
        ("Substrate", health.get("substrate", "unknown")),
        ("Product", health.get("product_output_health", "unknown")),
    ]
    tags = "".join(
        f'<span class="pill {_health_class(value)}"><span>{_esc(label)}</span>{_esc(value)}</span>'
        for label, value in bits
        if _clean(value)
    )
    return f'<div class="trust-strip">{tags}</div>' if tags else ""


def _orientation_html(text: str) -> str:
    return f'<div class="orientation">{_paragraphs(text)}</div>' if _clean(text) else ""


def _shift_grid(shifts: list[dict[str, str]]) -> str:
    if not shifts:
        return '<div class="empty">No decision-note shifts were persisted for this run.</div>'
    cards = []
    for index, shift in enumerate(shifts[:MAX_SHIFTS], start=1):
        cards.append(
            f"""
<article class="shift-card">
  <div class="card-index">{index:02d}</div>
  <h3>{_esc(shift["title"])}</h3>
  <div class="card-body">{_paragraphs(shift["body"])}</div>
</article>
"""
        )
    return f'<div class="shift-grid">{"".join(cards)}</div>'


def _pattern_chain(pattern: dict[str, str]) -> str:
    nodes = [
        ("Observed pattern", pattern.get("observed", "")),
        ("Reasoning pressure", pattern.get("pressure", "")),
        ("Reusable check", pattern.get("reusable", "")),
    ]
    rendered = []
    for label, text in nodes:
        rendered.append(
            f"""
<div class="chain-node">
  <div class="chain-label">{_esc(label)}</div>
  <p>{_inline(text) if text else "Not enough structured material was available for this slot."}</p>
</div>
"""
        )
    return f'<div class="chain">{"".join(rendered)}</div>'


def _model_grid(cards: list[dict[str, str]]) -> str:
    if not cards:
        return '<div class="empty">No model-learning cards were available for this run.</div>'
    rendered = []
    for card in cards[:MAX_MODEL_CARDS]:
        rendered.append(
            f"""
<article class="model-card">
  <div class="model-name">{_esc(card["name"])}</div>
  <p class="model-core">{_inline(card["core"])}</p>
  {_fact_row("Why it activated here", card.get("why"))}
  {_fact_row("What it changed", card.get("changed"))}
  {_fact_row("Reusable question", card.get("question"))}
  {_fact_row("Guardrail", card.get("guardrail"))}
</article>
"""
        )
    return f'<div class="model-grid">{"".join(rendered)}</div>'


def _question_grid(questions: list[dict[str, str]]) -> str:
    if not questions:
        return '<div class="empty">No structural gap questions were available for this run.</div>'
    rendered = []
    for item in questions[:MAX_QUESTIONS]:
        rendered.append(
            f"""
<article class="question-card">
  <div class="question-dimension">{_esc(item.get("dimension") or "Open check")}</div>
  <p>{_inline(item["question"])}</p>
</article>
"""
        )
    return f'<div class="question-grid">{"".join(rendered)}</div>'


def _optional_frame_section(cards: list[dict[str, str]]) -> str:
    if not cards:
        return ""
    rendered = []
    for card in cards[:MAX_FRAME_CARDS]:
        rendered.append(
            f"""
<article class="frame-card">
  <h3>{_esc(card["question"])}</h3>
  <p>{_inline(card["opens"])}</p>
  {_small_meta("Grounding lens", card.get("model"))}
</article>
"""
        )
    return f"""
<section class="section" id="reframes">
  <div class="section-kicker">05</div>
  <div class="section-head">
    <h2>Alternative Frames</h2>
    <p>HTML earns its keep when suppressed options can sit beside the revised advice instead of being buried below it.</p>
  </div>
  <div class="frame-grid">{''.join(rendered)}</div>
</section>
"""


def _technical_trace(result: dict[str, Any]) -> str:
    health = result.get("run_health") or {}
    gap_check = result.get("gap_check") or {}
    usage = result.get("usage_summary") or {}
    v60 = result.get("v60_enrichment") or {}
    validation = result.get("v60_consideration_validation") or {}
    ledger = result.get("v60_consideration_ledger") or {}

    gap_rows = []
    for lane in gap_check.get("lanes") or []:
        gap_rows.append(
            "<tr>"
            f"<td>{_esc(lane.get('lane_name', ''))}</td>"
            f"<td>{_esc(lane.get('status', ''))}</td>"
            f"<td>{_esc(len(lane.get('divergences') or []))}</td>"
            "</tr>"
        )
    disposition_counts = ledger.get("disposition_counts") or health.get("v60_consideration_disposition_counts") or {}
    return f"""
<section class="section trace" id="trace">
  <details>
    <summary>Technical trace</summary>
    <div class="trace-grid">
      <div>
        <h3>Run health</h3>
        {_definition_list({
            "overall": health.get("overall"),
            "issues": ", ".join(health.get("issues") or []),
            "quote fabrication": health.get("quote_fabrication_count"),
            "capture truncated": health.get("capture_truncated"),
            "product output": health.get("product_output_health"),
        })}
      </div>
      <div>
        <h3>Private enrichment</h3>
        {_definition_list({
            "status": v60.get("status"),
            "selected chunks": health.get("v60_selected_chunk_count"),
            "ledger": health.get("v60_consideration_ledger") or validation.get("status"),
            "dispositions": ", ".join(f"{key}: {value}" for key, value in disposition_counts.items()),
        })}
      </div>
      <div>
        <h3>Cost</h3>
        {_definition_list({
            "estimated total": _fmt_usd(usage.get("estimated_total_cost_usd")),
            "calls": usage.get("total_calls"),
        })}
      </div>
    </div>
    {_gap_check_table(gap_rows)}
  </details>
</section>
"""


def _gap_check_table(rows: list[str]) -> str:
    if not rows:
        return '<p class="muted">No pressure-check lane summary was persisted.</p>'
    return (
        '<h3>Pressure-check summary</h3>'
        '<table><thead><tr><th>Source</th><th>Status</th><th>Divergences</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def _reasoning_pattern(
    result: dict[str, Any],
    model_cards: list[dict[str, str]],
    frame_cards: list[dict[str, str]],
    questions: list[dict[str, str]],
) -> dict[str, str]:
    finding = _first_finding(result)
    observed = _clean(finding.get("challenge_statement") or finding.get("specific_passage"))
    if not observed and model_cards:
        observed = model_cards[0].get("why", "")
    if not observed and frame_cards:
        observed = frame_cards[0].get("question", "")

    pressure = ""
    if model_cards:
        pressure = f"{model_cards[0]['name']}: {model_cards[0].get('core', '')}"
    elif frame_cards:
        pressure = frame_cards[0].get("opens", "")

    reusable = ""
    if model_cards:
        reusable = model_cards[0].get("question", "")
    if not reusable and questions:
        reusable = questions[0].get("question", "")

    return {
        "observed": _truncate(observed, 260),
        "pressure": _truncate(pressure, 260),
        "reusable": _truncate(reusable, 260),
    }


def _model_cards(result: dict[str, Any]) -> list[dict[str, str]]:
    anchors = ((result.get("companion_cheat_sheet") or {}).get("anchors") or [])[:MAX_MODEL_CARDS]
    shifts = _extract_shift_items(_first_text(result, ["memo_what_changed"]))
    cards = []
    for index, anchor in enumerate(anchors):
        chunks = anchor.get("chunks") or []
        cards.append(
            {
                "name": _clean(anchor.get("display_name") or anchor.get("model_id") or "Model"),
                "core": _core_idea(anchor, chunks),
                "why": _clean(anchor.get("presence_explanation") or anchor.get("evidence_quote")),
                "changed": shifts[index]["title"] if index < len(shifts) else _changed_from_revised(result),
                "question": _chunk_text(chunks, "premortem") or _fallback_question(anchor),
                "guardrail": _chunk_text(chunks, "failure_mode") or _guardrail_from_v60(result, anchor.get("model_id")),
            }
        )
    return [card for card in cards if card["name"]]


def _core_idea(anchor: dict[str, Any], chunks: list[dict[str, Any]]) -> str:
    identity = _chunk_text(chunks, "identity")
    if identity:
        return _clean_identity(identity)
    heuristic = _chunk_text(chunks, "heuristic")
    if heuristic:
        return heuristic
    explanation = _clean(anchor.get("presence_explanation"))
    if explanation:
        return explanation
    return "Use this lens to make the reasoning pattern explicit before acting."


def _clean_identity(text: str) -> str:
    text = _clean(text)
    if " | " in text:
        parts = [part.strip() for part in text.split(" | ") if part.strip()]
        for part in parts:
            if part.lower().startswith("select when:"):
                return part.split(":", 1)[1].strip()
        return parts[0]
    return text


def _chunk_text(chunks: list[dict[str, Any]], chunk_type: str) -> str:
    for chunk in chunks:
        if chunk.get("chunk_type") == chunk_type:
            return _clean(chunk.get("text"))
    return ""


def _guardrail_from_v60(result: dict[str, Any], model_id: object) -> str:
    if not model_id:
        return ""
    selected = ((result.get("v60_enrichment") or {}).get("selected_cards") or [])
    for card in selected:
        if card.get("model_id") != model_id:
            continue
        absence = card.get("selected_absence_chunk") or {}
        return _clean(absence.get("blocker") or absence.get("text") or absence.get("absence_text"))
    return ""


def _fallback_question(anchor: dict[str, Any]) -> str:
    name = _clean(anchor.get("display_name") or anchor.get("model_id") or "this lens")
    return f"What would have to be true for {name} to change the decision, not just decorate the explanation?"


def _changed_from_revised(result: dict[str, Any]) -> str:
    changed = _first_text(result, ["memo_what_changed"])
    if changed:
        return _truncate(_strip_markdown(changed), 160)
    return "It helped separate the decision-relevant mechanism from background explanation."


def _frame_cards(result: dict[str, Any]) -> list[dict[str, str]]:
    reframings = ((result.get("frame_pressure_card") or {}).get("reframings") or [])[:MAX_FRAME_CARDS]
    cards = []
    for item in reframings:
        question = _clean(item.get("reframed_question"))
        if not question:
            continue
        cards.append(
            {
                "question": question,
                "opens": _clean(item.get("what_opens")),
                "model": _clean(item.get("grounding_model")),
            }
        )
    return cards


def _open_questions(result: dict[str, Any]) -> list[dict[str, str]]:
    gaps = (result.get("structural_coverage_card") or {}).get("gap_questions") or []
    questions = []
    seen = set()
    for gap in gaps:
        dimension = _clean(gap.get("dimension_name") or gap.get("dimension_id"))
        candidates = list(gap.get("questions") or [])
        if gap.get("question"):
            candidates.append(gap.get("question"))
        for question in candidates:
            question = _clean(question)
            if not question or question in seen:
                continue
            seen.add(question)
            questions.append({"dimension": dimension, "question": question})
            if len(questions) >= MAX_QUESTIONS:
                return questions
    return questions


def _first_finding(result: dict[str, Any]) -> dict[str, Any]:
    delta = result.get("delta_card") or {}
    for key in ("top_findings", "findings", "secondary_findings_full", "secondary_findings"):
        values = delta.get(key) or []
        if values:
            return values[0]
    return {}


def _fallback_shift_items(result: dict[str, Any]) -> list[dict[str, str]]:
    revised = _clean(result.get("revised_answer"))
    if revised:
        return [{"title": "Updated position", "body": _truncate(_strip_markdown(revised), 520)}]
    finding = _first_finding(result)
    if finding:
        return [
            {
                "title": _clean(finding.get("tendency_name") or "Reasoning pressure"),
                "body": _clean(finding.get("challenge_statement") or finding.get("specific_passage")),
            }
        ]
    return []


def _extract_shift_items(text: str) -> list[dict[str, str]]:
    text = _clean(text)
    if not text:
        return []

    heading_items = _extract_heading_items(text)
    if heading_items:
        return heading_items[:MAX_SHIFTS]

    items = []
    for paragraph in _paragraph_chunks(text):
        title = ""
        body = paragraph
        match = re.match(r"^\*\*(.+?)\*\*[.:]?\s*(.*)$", paragraph, flags=re.S)
        if match:
            title = _strip_markdown(match.group(1))
            body = match.group(2).strip()
        elif paragraph.startswith("- "):
            title = _strip_markdown(paragraph[2:].split(".", 1)[0])
        if not title:
            title = _truncate(_strip_markdown(paragraph), 72)
        items.append({"title": title, "body": body or paragraph})
        if len(items) >= MAX_SHIFTS:
            break
    return items


def _extract_heading_items(text: str) -> list[dict[str, str]]:
    matches = list(re.finditer(r"(?m)^#{2,4}\s+(.+?)\s*$", text))
    if not matches:
        return []
    items = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        title = _strip_markdown(match.group(1))
        if title and body:
            items.append({"title": title, "body": body})
    return items


def _paragraph_chunks(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]


def _html_document(title: str, body: str, payload: dict[str, Any]) -> str:
    payload_json = _json_for_script(payload)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_esc(title)}</title>
  <style>{_CSS}</style>
</head>
<body>
{body}
<script type="application/json" id="lolla-artifact-data">{payload_json}</script>
</body>
</html>
"""


def _json_for_script(payload: dict[str, Any]) -> str:
    """Serialize JSON safely inside a script tag without changing values."""
    return (
        json.dumps(payload, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def _structured_payload(
    result: dict[str, Any],
    title: str,
    shifts: list[dict[str, str]],
    models: list[dict[str, str]],
    questions: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "artifact": "lolla_case_learning_html",
        "title": title,
        "run_health": (result.get("run_health") or {}).get("overall"),
        "shifts": shifts[:MAX_SHIFTS],
        "models": models[:MAX_MODEL_CARDS],
        "questions": questions[:MAX_QUESTIONS],
    }


def _fact_row(label: str, value: object) -> str:
    text = _clean(value)
    if not text:
        return ""
    return f'<div class="fact-row"><span>{_esc(label)}</span><p>{_inline(text)}</p></div>'


def _small_meta(label: str, value: object) -> str:
    text = _clean(value)
    if not text:
        return ""
    return f'<div class="small-meta"><span>{_esc(label)}</span>{_esc(text)}</div>'


def _definition_list(items: dict[str, object]) -> str:
    rows = []
    for key, value in items.items():
        text = _clean(value)
        if text:
            rows.append(f"<dt>{_esc(key)}</dt><dd>{_esc(text)}</dd>")
    return f"<dl>{''.join(rows)}</dl>" if rows else '<p class="muted">No data.</p>'


def _paragraphs(text: str) -> str:
    chunks = _paragraph_chunks(_clean(text))
    if not chunks:
        return ""
    rendered = []
    for chunk in chunks:
        if _looks_like_list(chunk):
            rendered.append(_list_html(chunk))
        else:
            rendered.append(f"<p>{_inline(chunk)}</p>")
    return "".join(rendered)


def _looks_like_list(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return bool(lines) and all(line.startswith(("- ", "* ")) for line in lines)


def _list_html(text: str) -> str:
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(("- ", "* ")):
            items.append(f"<li>{_inline(line[2:])}</li>")
    return f"<ul>{''.join(items)}</ul>" if items else ""


def _inline(text: object) -> str:
    escaped = _esc(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    return escaped.replace("\n", "<br>")


def _strip_markdown(text: str) -> str:
    text = _clean(text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"^\s*[-*]\s+", "", text, flags=re.M)
    return re.sub(r"\s+", " ", text).strip()


def _first_text(result: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        text = _clean(result.get(key))
        if text:
            return text
    return ""


def _clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _esc(value: object) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _truncate(text: str, max_chars: int) -> str:
    text = _clean(text)
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0].rstrip(".,;:") + "..."


def _fmt_usd(value: object) -> str:
    try:
        return f"${float(value):.4f}"
    except (TypeError, ValueError):
        return ""


def _health_class(value: object) -> str:
    value_s = _clean(value).lower()
    if value_s in {"healthy", "good", "ok", "clean", "active", "valid"}:
        return "ok"
    if value_s in {"degraded", "partial", "unsafe", "critical"}:
        return "warn"
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Lolla case-learning HTML artifact")
    parser.add_argument("--result", required=True, type=Path, help="Path to result.json")
    parser.add_argument("--output", type=Path, help="Output HTML path; defaults to stdout")
    args = parser.parse_args()

    result = json.loads(args.result.read_text(encoding="utf-8"))
    rendered = render_case_learning_html(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


_CSS = """
:root {
  color-scheme: light;
  --ink: #1d2528;
  --muted: #667175;
  --line: #d8e1e4;
  --soft: #f6f8f8;
  --paper: #ffffff;
  --accent: #0f766e;
  --accent-soft: #dff4ef;
  --warn: #a04d12;
  --warn-soft: #fff1df;
  --blue: #315b7d;
  --blue-soft: #e7f0f7;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--ink);
  background: #eef3f2;
  line-height: 1.5;
}
.hero, main {
  width: min(1120px, calc(100vw - 32px));
  margin: 0 auto;
}
.hero {
  padding: 48px 0 28px;
}
.eyebrow, .section-kicker {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--accent);
  font-weight: 700;
}
h1 {
  margin: 10px 0 18px;
  max-width: 900px;
  font-size: 42px;
  line-height: 1.06;
  letter-spacing: 0;
}
h2 {
  margin: 0;
  font-size: 26px;
  line-height: 1.15;
}
h3 {
  margin: 0 0 8px;
  font-size: 17px;
  line-height: 1.25;
}
p { margin: 0 0 12px; }
.trust-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 22px;
}
.pill {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 6px 10px;
  background: var(--paper);
  color: var(--muted);
  font-size: 13px;
}
.pill span {
  color: var(--ink);
  font-weight: 700;
}
.pill.ok {
  background: var(--accent-soft);
  border-color: #a6d9d0;
}
.pill.warn {
  background: var(--warn-soft);
  border-color: #f0c999;
  color: var(--warn);
}
.orientation {
  max-width: 860px;
  font-size: 18px;
  color: #334044;
}
.section {
  position: relative;
  margin: 18px 0;
  padding: 28px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
}
.section-head {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  align-items: end;
  margin: 6px 0 22px;
}
.section-head p {
  max-width: 520px;
  color: var(--muted);
  margin: 0;
}
.shift-grid, .model-grid, .question-grid, .frame-grid, .trace-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.shift-card, .model-card, .question-card, .frame-card, .chain-node {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px;
  background: var(--soft);
}
.shift-card {
  background: linear-gradient(180deg, #ffffff 0%, #f4faf8 100%);
}
.card-index, .chain-label, .question-dimension, .small-meta span, .fact-row span {
  font-size: 12px;
  color: var(--accent);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.card-body {
  color: #3b474b;
}
.card-body ul {
  padding-left: 18px;
  margin: 8px 0 0;
}
.chain {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}
.chain-node {
  min-height: 150px;
  background: var(--blue-soft);
  border-color: #c4d8e8;
}
.chain-node p {
  margin-top: 12px;
}
.model-card {
  background: #fffefa;
}
.model-name {
  font-size: 19px;
  font-weight: 800;
  margin-bottom: 8px;
}
.model-core {
  color: #334044;
  font-weight: 600;
}
.fact-row {
  border-top: 1px solid var(--line);
  padding-top: 10px;
  margin-top: 10px;
}
.fact-row p {
  margin: 4px 0 0;
  color: #3f4b4f;
}
.question-card {
  background: #fbfcfd;
}
.question-card p {
  font-size: 16px;
}
.frame-card {
  background: #f9fbff;
}
.small-meta {
  margin-top: 12px;
  color: var(--muted);
  font-size: 13px;
}
.trace {
  background: #192225;
  color: #e6eeee;
  border-color: #192225;
}
.trace summary {
  cursor: pointer;
  font-weight: 800;
  font-size: 18px;
}
.trace h3 {
  color: #ffffff;
}
.trace-grid {
  margin-top: 20px;
}
dl {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 6px 12px;
  margin: 0;
}
dt {
  color: #9eb4bb;
}
dd {
  margin: 0;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}
th, td {
  text-align: left;
  padding: 8px 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.16);
}
.empty, .muted {
  color: var(--muted);
  background: var(--soft);
  border: 1px dashed var(--line);
  border-radius: 8px;
  padding: 18px;
}
.trace .muted {
  color: #b8c9ce;
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.16);
}
code {
  background: rgba(15, 118, 110, 0.12);
  padding: 1px 4px;
  border-radius: 4px;
}
@media (max-width: 780px) {
  .hero, main {
    width: min(100vw - 20px, 1120px);
  }
  .hero {
    padding-top: 28px;
  }
  h1 {
    font-size: 31px;
  }
  .section {
    padding: 18px;
  }
  .section-head {
    display: block;
  }
  .section-head p {
    margin-top: 8px;
  }
  .shift-grid, .model-grid, .question-grid, .frame-grid, .trace-grid, .chain {
    grid-template-columns: 1fr;
  }
}
"""


if __name__ == "__main__":
    main()
