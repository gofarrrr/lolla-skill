"""Build a visible offline review surface for the Mental Model Teacher pilot.

This builder turns the checked-in three-case Teacher product pilot into a
single static HTML app. It embeds already-reviewed local artifacts only. It does
not run Lolla, call providers, wire runtime behavior, or complete human review.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from pathlib import Path
from typing import Any

from .mental_model_teacher_pilot_page_builder import REPO_ROOT


VISIBLE_SURFACE_SCHEMA_VERSION = "lolla.mental_model_teacher.visible_review_surface.v0"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-visible-review-surface-v0"
PILOT_DIR = REPO_ROOT / "docs/product/mental-model-teacher-three-case-product-pilot-v0"
SOURCE_ROOT = REPO_ROOT / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2"

CASE_IDS = (
    "launch-public-enterprise-beta",
    "deploy-assisted-intake-routing",
    "ceo-remove-founding-cofounder",
)
REVIEW_CRITERIA = (
    ("educational_value", "Educational value"),
    ("clarity", "Clarity"),
    ("relation_understanding", "Relation understanding"),
    ("practice_usefulness", "Practice usefulness"),
    ("non_overclaiming", "Non-overclaiming"),
    ("separation_from_decision_work", "Separation from Decision Work"),
)
CASE_TITLES = {
    "launch-public-enterprise-beta": "Launch Public Enterprise Beta",
    "deploy-assisted-intake-routing": "Deploy Assisted Intake Routing",
    "ceo-remove-founding-cofounder": "CEO Removes Founding Cofounder",
}
DECISION_WORK_BRIEFS = {
    "launch-public-enterprise-beta": (
        "docs/conversation-understanding/"
        "decision-work-brief-rendered-launch-public-enterprise-beta-v0.md"
    ),
    "deploy-assisted-intake-routing": (
        "docs/conversation-understanding/"
        "decision-work-brief-rendered-deploy-assisted-intake-routing-v0.md"
    ),
    "ceo-remove-founding-cofounder": (
        "docs/conversation-understanding/"
        "decision-work-brief-rendered-ceo-remove-founding-cofounder-v0.md"
    ),
}


class MentalModelTeacherVisibleReviewSurfaceError(ValueError):
    """Raised when the visible review surface cannot be rendered safely."""


def build_visible_review_surface(
    root: Path | str | None = None,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    repo_root = Path(root) if root is not None else REPO_ROOT
    target_dir = Path(output_dir)
    cases = [_case_payload(repo_root, case_id, target_dir) for case_id in CASE_IDS]
    data = {
        "schema_version": VISIBLE_SURFACE_SCHEMA_VERSION,
        "product_lane": "Mental Model Teacher Product Surface And Visual Library",
        "status": "visible_review_surface_ready_for_human_review",
        "decision_gate": "needs_human_review_before_expansion",
        "cases": cases,
        "review_criteria": [
            {"id": criterion_id, "label": label}
            for criterion_id, label in REVIEW_CRITERIA
        ],
        "non_claims": {
            "product_proof": False,
            "human_validated": False,
            "answer_correctness": False,
            "advice_correctness": False,
            "runtime_integration_authorized": False,
            "graph_edges_are_proof": False,
            "agent_or_automatic_action_authorized": False,
        },
    }
    html_text = render_visible_review_surface(data)
    manifest = {
        "schema_version": VISIBLE_SURFACE_SCHEMA_VERSION,
        "builder": "engine.system_b.mental_model_teacher_visible_review_surface",
        "status": "visible_review_surface_ready_for_human_review",
        "output_dir": _safe_display_path(target_dir),
        "entrypoint": "index.html",
        "case_count": len(cases),
        "review_criteria": [criterion_id for criterion_id, _label in REVIEW_CRITERIA],
        "embedded_data": True,
        "external_network_required": False,
        "provider_or_model_calls_used": False,
        "runtime_integration_authorized": False,
        "human_review_completed": False,
        "human_validated": False,
        "product_proof": False,
        "decision_gate": "needs_human_review_before_expansion",
        "case_artifacts": [
            {
                "case_id": case["case_id"],
                "lesson_object": case["artifact_refs"]["lesson_object"],
                "graph_object": case["artifact_refs"]["graph_object"],
                "teacher_card": case["artifact_refs"]["teacher_card"],
                "teacher_note": case["artifact_refs"]["teacher_note"],
                "product_lesson_page": case["artifact_refs"]["product_lesson_page"],
            }
            for case in cases
        ],
        "non_claims": data["non_claims"],
        "stop_before": [
            "human validation claim",
            "product proof claim",
            "runtime integration",
            "provider or model calls",
            "full corpus graph",
        ],
    }
    _write(target_dir / "index.html", html_text)
    _write_json(target_dir / "manifest.json", manifest)
    return manifest


def render_visible_review_surface(data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True)
    payload = payload.replace("</", "<\\/")
    return _finish(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>Mental Model Teacher Pilot Review</title>",
            "  <style>",
            _CSS,
            "  </style>",
            "</head>",
            "<body>",
            '  <div id="app" class="app-shell"></div>',
            f'  <script id="surface-data" type="application/json">{payload}</script>',
            "  <script>",
            _JS,
            "  </script>",
            "</body>",
            "</html>",
        ]
    )


def _case_payload(repo_root: Path, case_id: str, output_dir: Path) -> dict[str, Any]:
    lesson_path = (
        repo_root
        / "docs/product/mental-model-teacher-three-case-product-pilot-v0/objects"
        / f"{case_id}.lesson.json"
    )
    graph_path = (
        repo_root
        / "docs/product/mental-model-teacher-three-case-product-pilot-v0/graphs"
        / f"{case_id}.graph.json"
    )
    source_dir = repo_root / "reviews/codex-assisted/mental-model-teacher-knowledge-mesh-v2" / case_id
    lesson = _load_json(lesson_path)
    graph = _load_json(graph_path)
    card_path = source_dir / "mental_model_teacher_card.md"
    note_path = source_dir / "mental_model_teacher.md"

    return {
        "case_id": case_id,
        "case_title": CASE_TITLES[case_id],
        "case_anchor": lesson["case_anchor"],
        "thinking_move": lesson["thinking_move"],
        "relation_story": lesson["relation_story"],
        "model_stack": lesson["model_stack"],
        "practice_rep": lesson["practice_rep"],
        "do_not_overlearn": lesson["do_not_overlearn"],
        "missingness": lesson["missingness"],
        "human_review_status": lesson["human_review_status"],
        "product_proof": lesson["product_proof"],
        "runtime_integration_authorized": lesson["runtime_integration_authorized"],
        "non_claims": lesson["non_claims"],
        "graph": _graph_payload(graph, graph_path, output_dir),
        "source_snapshots": _source_snapshots(card_path, note_path),
        "artifact_refs": {
            "lesson_object": _repo_rel(lesson_path),
            "graph_object": _repo_rel(graph_path),
            "teacher_card": _repo_rel(card_path),
            "teacher_note": _repo_rel(note_path),
            "product_lesson_page": (
                "docs/product/mental-model-teacher-three-case-product-pilot-v0/lessons/"
                f"{case_id}.md"
            ),
            "decision_work_boundary_reference": DECISION_WORK_BRIEFS[case_id],
        },
        "artifact_links": {
            "lesson": _relative_link(
                output_dir / "index.html",
                "docs/product/mental-model-teacher-three-case-product-pilot-v0/lessons/"
                f"{case_id}.md",
            ),
            "teacher_card": _relative_link(output_dir / "index.html", _repo_rel(card_path)),
            "teacher_note": _relative_link(output_dir / "index.html", _repo_rel(note_path)),
            "decision_work": _relative_link(output_dir / "index.html", DECISION_WORK_BRIEFS[case_id]),
        },
    }


def _graph_payload(graph: dict[str, Any], graph_path: Path, output_dir: Path) -> dict[str, Any]:
    return {
        "graph_id": graph["graph_id"],
        "default_focus": graph["default_focus"],
        "nodes": [
            {
                **node,
                "href": _relative_link(
                    output_dir / "index.html",
                    _repo_rel((graph_path.parent / node["href"]).resolve()),
                ),
            }
            for node in graph["nodes"]
        ],
        "edges": [
            {
                **edge,
                "href": _relative_link(
                    output_dir / "index.html",
                    _repo_rel((graph_path.parent / edge["href"]).resolve()),
                ),
            }
            for edge in graph["edges"]
        ],
        "missingness": graph["missingness"],
        "non_claims": graph["non_claims"],
    }


def _source_snapshots(card_path: Path, note_path: Path) -> dict[str, Any]:
    card = card_path.read_text(encoding="utf-8")
    note = note_path.read_text(encoding="utf-8")
    return {
        "card": {
            "thinking_move": _section(card, "The Thinking Move", limit=420),
            "why_it_mattered": _section(card, "Why It Mattered", limit=520),
            "models_together": _section(card, "How The Models Work Together", limit=620),
            "practice": _section(card, "Practice It", limit=760),
            "do_not_overlearn": _section(card, "Do Not Overlearn This", limit=320),
        },
        "note": {
            "what_to_learn": _section(note, "What To Learn", limit=520),
            "case_anchor": _section(note, "The Case Anchor", limit=520),
            "models_together": _section(note, "Why These Models Belong Together", limit=620),
            "where_it_stops": _section(note, "Where This Lesson Stops", limit=320),
        },
    }


def _section(markdown: str, heading: str, *, limit: int) -> str:
    pattern = re.compile(
        rf"^#+\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^#+\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return ""
    text = re.sub(r"^\s*#+\s+", "", match.group("body"), flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise MentalModelTeacherVisibleReviewSurfaceError("JSON root must be an object")
    return payload


def _repo_rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise MentalModelTeacherVisibleReviewSurfaceError(
            "path must stay inside the repository"
        ) from exc


def _safe_display_path(path: Path) -> str:
    try:
        return _repo_rel(path)
    except MentalModelTeacherVisibleReviewSurfaceError:
        return path.name


def _relative_link(from_path: Path, repo_relative_path: str) -> str:
    try:
        from_path.resolve().relative_to(REPO_ROOT.resolve())
    except ValueError:
        return repo_relative_path
    return os.path.relpath(REPO_ROOT / repo_relative_path, from_path.parent)


def _write(path: Path, text: str) -> None:
    _assert_no_local_paths(text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _assert_no_local_paths(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _finish(lines: list[str]) -> str:
    return "\n".join(str(line).rstrip() for line in lines).rstrip() + "\n"


def _assert_no_local_paths(payload: Any) -> None:
    rendered = json.dumps(payload, sort_keys=True) if not isinstance(payload, str) else payload
    markers = (
        "/" + "Users/",
        "Desktop/" + "Apps",
        "\\" + "Users\\",
    )
    if any(marker in rendered for marker in markers):
        raise MentalModelTeacherVisibleReviewSurfaceError(
            "visible review surface contains a local path marker"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the visible Mental Model Teacher pilot review surface.",
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    manifest = build_visible_review_surface(args.root, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


_CSS = r"""
:root {
  color-scheme: light;
  --bg: #f4f6f8;
  --surface: #ffffff;
  --surface-alt: #eef3f4;
  --ink: #172126;
  --muted: #63717a;
  --line: #d8e0e3;
  --teal: #0f766e;
  --teal-soft: #ddf3ef;
  --blue: #315a96;
  --blue-soft: #e3edf9;
  --amber: #b85c1d;
  --amber-soft: #fff0df;
  --rose: #954c65;
  --rose-soft: #f8e6ed;
  --green: #477244;
  --green-soft: #e6f2e4;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-height: 100vh;
  background: var(--bg);
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 14px;
  line-height: 1.45;
}

a {
  color: var(--blue);
  font-weight: 650;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

button,
input,
textarea {
  font: inherit;
}

button {
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface);
  color: var(--ink);
  cursor: pointer;
}

button:hover,
button.is-active {
  border-color: var(--teal);
  background: var(--teal-soft);
}

button:focus-visible,
a:focus-visible,
textarea:focus-visible,
input:focus-visible,
.graph-node:focus-visible,
.graph-edge-hit:focus-visible {
  outline: 3px solid rgba(15, 118, 110, 0.22);
  outline-offset: 2px;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  grid-template-rows: auto 1fr;
}

.topbar {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 18px;
  align-items: center;
  padding: 14px 18px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}

.brand h1 {
  margin: 0;
  font-size: 19px;
  font-weight: 760;
  letter-spacing: 0;
}

.brand p {
  margin: 3px 0 0;
  color: var(--muted);
  font-size: 13px;
}

.status-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 9px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface-alt);
  color: var(--ink);
  font-size: 12px;
  font-weight: 720;
  white-space: nowrap;
}

.pill.teal {
  background: var(--teal-soft);
  border-color: #b5ddd7;
}

.pill.amber {
  background: var(--amber-soft);
  border-color: #efcaab;
}

.sidebar {
  border-right: 1px solid var(--line);
  background: var(--surface);
  min-height: 0;
  padding: 14px;
}

.case-list {
  display: grid;
  gap: 9px;
}

.case-button {
  width: 100%;
  min-height: 88px;
  padding: 11px;
  text-align: left;
}

.case-title {
  display: block;
  font-weight: 760;
}

.case-move {
  display: block;
  margin-top: 6px;
  color: var(--muted);
  font-size: 12px;
}

.main {
  min-width: 0;
  min-height: 0;
  overflow: auto;
}

.case-header {
  padding: 18px 22px 14px;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
}

.case-header h2 {
  margin: 0;
  font-size: 24px;
  letter-spacing: 0;
}

.case-header p {
  max-width: 980px;
  margin: 8px 0 0;
  color: var(--muted);
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(340px, 0.75fr);
  gap: 16px;
  padding: 16px;
}

.column {
  display: grid;
  gap: 16px;
  align-content: start;
}

.panel {
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--line);
  background: #fbfcfd;
}

.panel-header h3 {
  margin: 0;
  font-size: 15px;
  letter-spacing: 0;
}

.panel-body {
  padding: 14px;
}

.lead {
  margin: 0;
  font-size: 18px;
  line-height: 1.35;
  font-weight: 760;
}

.muted {
  color: var(--muted);
}

.model-grid {
  display: grid;
  gap: 10px;
}

.model-card {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
  background: #fbfcfd;
}

.model-card h4 {
  margin: 0 0 5px;
  font-size: 14px;
}

.model-card p {
  margin: 7px 0 0;
}

.boundary {
  border-left: 3px solid var(--amber);
  padding-left: 10px;
  color: #5e4026;
}

.practice-box {
  display: grid;
  gap: 8px;
  border: 1px solid #c9dfdb;
  border-radius: 8px;
  background: var(--teal-soft);
  padding: 12px;
}

.practice-box strong {
  font-size: 15px;
}

.graph-stage {
  min-height: 300px;
  background:
    linear-gradient(rgba(23, 33, 38, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23, 33, 38, 0.045) 1px, transparent 1px),
    #fbfcfd;
  background-size: 32px 32px;
}

.graph-stage svg {
  display: block;
  width: 100%;
  min-height: 300px;
}

.graph-edge {
  stroke: var(--blue);
  stroke-width: 3;
  stroke-linecap: round;
}

.graph-edge.is-selected {
  stroke: var(--amber);
  stroke-width: 5;
}

.graph-edge-hit {
  stroke: transparent;
  stroke-width: 22;
  cursor: pointer;
}

.graph-node circle {
  fill: var(--surface);
  stroke: var(--teal);
  stroke-width: 3;
}

.graph-node.is-selected circle {
  fill: var(--teal-soft);
  stroke: var(--amber);
  stroke-width: 4;
}

.graph-node text {
  fill: var(--ink);
  font-size: 12px;
  font-weight: 740;
  text-anchor: middle;
}

.detail-list {
  display: grid;
  gap: 8px;
}

.detail-list p {
  margin: 0;
}

.link-row {
  display: flex;
  gap: 9px;
  flex-wrap: wrap;
}

.link-button {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 10px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface);
}

.compare-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.source-box {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 12px;
  background: #fbfcfd;
}

.source-box h4 {
  margin: 0 0 8px;
  font-size: 14px;
}

.source-box p,
.source-box pre {
  margin: 0;
}

.source-box pre {
  white-space: pre-wrap;
  font-family: inherit;
  color: var(--muted);
}

.review-grid {
  display: grid;
  gap: 10px;
}

.criterion {
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px;
}

.criterion legend {
  padding: 0 4px;
  font-weight: 740;
}

.radio-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 6px;
  margin-top: 8px;
}

.radio-row label {
  display: flex;
  min-height: 30px;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: #fbfcfd;
  font-size: 12px;
  font-weight: 650;
}

textarea {
  width: 100%;
  min-height: 86px;
  margin-top: 10px;
  resize: vertical;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 9px;
  color: var(--ink);
  background: #fbfcfd;
}

.nonclaims {
  display: flex;
  gap: 7px;
  flex-wrap: wrap;
}

.nonclaims .pill {
  background: var(--rose-soft);
  border-color: #edc5d2;
}

@media (max-width: 1040px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .case-list {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .workspace {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .topbar {
    grid-template-columns: 1fr;
  }

  .status-row {
    justify-content: flex-start;
  }

  .case-list,
  .compare-grid,
  .radio-row {
    grid-template-columns: 1fr;
  }

  .case-header h2 {
    font-size: 20px;
  }
}
"""


_JS = r"""
const surface = JSON.parse(document.getElementById("surface-data").textContent);
let selectedCaseId = surface.cases[0].case_id;
let selectedGraphItem = { kind: "node", id: surface.cases[0].graph.default_focus };

const app = document.getElementById("app");

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function caseById(caseId) {
  return surface.cases.find((item) => item.case_id === caseId) || surface.cases[0];
}

function labelLines(label, maxChars = 18) {
  const words = String(label).split(/\s+/);
  const lines = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) lines.push(current);
  return lines.slice(0, 3);
}

function render() {
  const item = caseById(selectedCaseId);
  app.innerHTML = `
    <header class="topbar">
      <div class="brand">
        <h1>Mental Model Teacher Pilot</h1>
        <p>Case is the anchor. Reasoning move is the subject. Model relationship is the lesson. Practice rep is the product value.</p>
      </div>
      <div class="status-row">
        <span class="pill teal">${escapeHtml(surface.decision_gate)}</span>
        <span class="pill amber">human review pending</span>
        <span class="pill">offline static surface</span>
      </div>
    </header>
    <aside class="sidebar">
      <div class="case-list">
        ${surface.cases.map(renderCaseButton).join("")}
      </div>
    </aside>
    <main class="main">
      ${renderCaseHeader(item)}
      <div class="workspace">
        <section class="column">
          ${renderLessonPanel(item)}
          ${renderModelStack(item)}
          ${renderComparison(item)}
        </section>
        <section class="column">
          ${renderGraphPanel(item)}
          ${renderReviewPanel(item)}
          ${renderNonClaims(item)}
        </section>
      </div>
    </main>
  `;
  wireEvents();
}

function renderCaseButton(item) {
  const active = item.case_id === selectedCaseId ? " is-active" : "";
  return `
    <button class="case-button${active}" data-case-id="${escapeHtml(item.case_id)}">
      <span class="case-title">${escapeHtml(item.case_title)}</span>
      <span class="case-move">${escapeHtml(item.thinking_move)}</span>
    </button>
  `;
}

function renderCaseHeader(item) {
  return `
    <section class="case-header">
      <div class="status-row">
        <span class="pill teal">review status: ${escapeHtml(item.human_review_status)}</span>
        <span class="pill">product proof: ${String(item.product_proof)}</span>
        <span class="pill">runtime authorized: ${String(item.runtime_integration_authorized)}</span>
      </div>
      <h2>${escapeHtml(item.case_title)}</h2>
      <p>${escapeHtml(item.case_anchor)}</p>
    </section>
  `;
}

function renderLessonPanel(item) {
  return `
    <article class="panel">
      <div class="panel-header">
        <h3>Productized Lesson</h3>
        <div class="link-row">
          <a class="link-button" href="${escapeHtml(item.artifact_links.lesson)}">lesson page</a>
          <a class="link-button" href="${escapeHtml(item.artifact_links.decision_work)}">Decision Work boundary</a>
        </div>
      </div>
      <div class="panel-body">
        <p class="lead">${escapeHtml(item.thinking_move)}</p>
        <h4>Relation story</h4>
        <p>${escapeHtml(item.relation_story)}</p>
        <h4>Practice rep</h4>
        <div class="practice-box">
          <strong>${escapeHtml(item.practice_rep.prompt)}</strong>
          <span>${escapeHtml(item.practice_rep.user_action)}</span>
        </div>
        <h4>Do not overlearn</h4>
        <ul>
          ${item.do_not_overlearn.map((line) => `<li>${escapeHtml(line)}</li>`).join("")}
        </ul>
      </div>
    </article>
  `;
}

function renderModelStack(item) {
  return `
    <article class="panel">
      <div class="panel-header">
        <h3>Model Stack</h3>
        <span class="pill">${item.model_stack.length} models</span>
      </div>
      <div class="panel-body model-grid">
        ${item.model_stack.map((model) => `
          <div class="model-card">
            <h4>${escapeHtml(model.teaching_name)}</h4>
            <span class="pill">${escapeHtml(model.role)}</span>
            <p>${escapeHtml(model.teaching_note)}</p>
            <p class="boundary">${escapeHtml(model.boundary)}</p>
          </div>
        `).join("")}
      </div>
    </article>
  `;
}

function renderComparison(item) {
  const card = item.source_snapshots.card;
  const note = item.source_snapshots.note;
  return `
    <article class="panel">
      <div class="panel-header">
        <h3>Raw Teacher Comparison</h3>
        <div class="link-row">
          <a class="link-button" href="${escapeHtml(item.artifact_links.teacher_card)}">card</a>
          <a class="link-button" href="${escapeHtml(item.artifact_links.teacher_note)}">note</a>
        </div>
      </div>
      <div class="panel-body compare-grid">
        <div class="source-box">
          <h4>Teacher card snapshot</h4>
          <pre>${escapeHtml([card.thinking_move, card.why_it_mattered, card.models_together].filter(Boolean).join("\n\n"))}</pre>
        </div>
        <div class="source-box">
          <h4>Teacher note snapshot</h4>
          <pre>${escapeHtml([note.what_to_learn, note.case_anchor, note.models_together, note.where_it_stops].filter(Boolean).join("\n\n"))}</pre>
        </div>
      </div>
    </article>
  `;
}

function renderGraphPanel(item) {
  return `
    <article class="panel">
      <div class="panel-header">
        <h3>Lesson Graph</h3>
        <span class="pill">${escapeHtml(item.graph.edges[0]?.relation_type || "relation")}</span>
      </div>
      <div class="graph-stage">
        ${renderGraph(item)}
      </div>
      <div class="panel-body">
        ${renderGraphDetails(item)}
      </div>
    </article>
  `;
}

function renderGraph(item) {
  const nodes = item.graph.nodes;
  const positions = nodePositions(nodes.length);
  const byId = Object.fromEntries(nodes.map((node, index) => [node.node_id, { ...node, ...positions[index] }]));
  const edges = item.graph.edges.map((edge) => {
    const source = byId[edge.source_node_id];
    const target = byId[edge.target_node_id];
    if (!source || !target) return "";
    const selected = selectedGraphItem.kind === "edge" && selectedGraphItem.id === edge.edge_id ? " is-selected" : "";
    return `
      <g>
        <line class="graph-edge${selected}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"></line>
        <line class="graph-edge-hit" tabindex="0" data-edge-id="${escapeHtml(edge.edge_id)}" x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}"></line>
        <text x="${(source.x + target.x) / 2}" y="${(source.y + target.y) / 2 - 14}" text-anchor="middle" fill="#315a96" font-size="12" font-weight="740">${escapeHtml(edge.relation_type)}</text>
      </g>
    `;
  }).join("");
  const nodeMarkup = nodes.map((node, index) => {
    const position = positions[index];
    const selected = selectedGraphItem.kind === "node" && selectedGraphItem.id === node.node_id ? " is-selected" : "";
    const lines = labelLines(node.label);
    const startY = 124 - ((lines.length - 1) * 8);
    return `
      <g class="graph-node${selected}" tabindex="0" data-node-id="${escapeHtml(node.node_id)}" transform="translate(${position.x} ${position.y})">
        <circle r="58"></circle>
        ${lines.map((line, lineIndex) => `<text y="${startY + lineIndex * 16 - 100}">${escapeHtml(line)}</text>`).join("")}
      </g>
    `;
  }).join("");
  return `
    <svg viewBox="0 0 640 320" role="img" aria-label="Lesson graph neighborhood">
      ${edges}
      ${nodeMarkup}
    </svg>
  `;
}

function nodePositions(count) {
  if (count <= 2) {
    return [{ x: 190, y: 160 }, { x: 450, y: 160 }];
  }
  return [{ x: 150, y: 160 }, { x: 345, y: 88 }, { x: 490, y: 228 }, { x: 345, y: 250 }];
}

function renderGraphDetails(item) {
  if (selectedGraphItem.kind === "edge") {
    const edge = item.graph.edges.find((candidate) => candidate.edge_id === selectedGraphItem.id) || item.graph.edges[0];
    return `
      <div class="detail-list">
        <p><strong>${escapeHtml(edge.label)}</strong></p>
        <p class="muted">Relation type: ${escapeHtml(edge.relation_type)}. Confidence: ${escapeHtml(edge.confidence)}. Edges are navigation context, not proof.</p>
        <p><a href="${escapeHtml(edge.href)}">relation source view</a></p>
      </div>
    `;
  }
  const node = item.graph.nodes.find((candidate) => candidate.node_id === selectedGraphItem.id) || item.graph.nodes[0];
  return `
    <div class="detail-list">
      <p><strong>${escapeHtml(node.label)}</strong></p>
      <p class="muted">Role: ${escapeHtml(node.role)}. Source: ${escapeHtml(node.source_status)}. Missingness: ${escapeHtml(node.missingness_status)}.</p>
      <p><a href="${escapeHtml(node.href)}">model source view</a></p>
    </div>
  `;
}

function renderReviewPanel(item) {
  return `
    <article class="panel">
      <div class="panel-header">
        <h3>Human Review</h3>
        <span class="pill amber">blank</span>
      </div>
      <div class="panel-body review-grid">
        ${surface.review_criteria.map((criterion) => `
          <fieldset class="criterion">
            <legend>${escapeHtml(criterion.label)}</legend>
            <div class="radio-row">
              ${["strong", "adequate", "weak", "cannot judge"].map((option) => `
                <label>
                  <input type="radio" name="${escapeHtml(item.case_id)}-${escapeHtml(criterion.id)}" value="${escapeHtml(option)}">
                  ${escapeHtml(option)}
                </label>
              `).join("")}
            </div>
          </fieldset>
        `).join("")}
        <textarea aria-label="Review notes for selected case"></textarea>
      </div>
    </article>
  `;
}

function renderNonClaims(item) {
  return `
    <article class="panel">
      <div class="panel-header">
        <h3>Non-Claims</h3>
      </div>
      <div class="panel-body nonclaims">
        ${item.non_claims.map((claim) => `<span class="pill">${escapeHtml(claim)}</span>`).join("")}
      </div>
    </article>
  `;
}

function wireEvents() {
  document.querySelectorAll("[data-case-id]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedCaseId = button.dataset.caseId;
      const item = caseById(selectedCaseId);
      selectedGraphItem = { kind: "node", id: item.graph.default_focus };
      render();
    });
  });
  document.querySelectorAll("[data-node-id]").forEach((node) => {
    const activate = () => {
      selectedGraphItem = { kind: "node", id: node.dataset.nodeId };
      render();
    };
    node.addEventListener("click", activate);
    node.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activate();
      }
    });
  });
  document.querySelectorAll("[data-edge-id]").forEach((edge) => {
    const activate = () => {
      selectedGraphItem = { kind: "edge", id: edge.dataset.edgeId };
      render();
    };
    edge.addEventListener("click", activate);
    edge.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activate();
      }
    });
  });
}

render();
"""


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
