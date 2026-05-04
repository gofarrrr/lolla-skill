"""Serve a single Lolla pipeline result in the Observatory frontend.

Zero-dependency Python server (stdlib http.server). Takes a pipeline
result JSON file and serves it through the Observatory Svelte app.

Usage:
    python3 observatory/serve_result.py --result /tmp/lolla_result.json
    python3 observatory/serve_result.py --result /tmp/lolla_result.json --port 9000

SPA source: the bundle in ``observatory/build/`` is compiled output from
``Lolla-system-b/observatory/svelte-app`` (separate repo). To change SPA
behaviour, edit the Svelte source there, run ``npm run build``, and copy
``build/`` over the skill's ``observatory/build/``. The ``/audit/*`` and
``/usage`` panels rendered from this Python file are independent of the
SPA bundle and stay portable when ``observatory/build/`` is empty.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_DIR = SCRIPT_DIR / "build"
SKILL_DATA_DIR = SCRIPT_DIR.parent / "data"
ENGINE_DIR = SCRIPT_DIR.parent / "engine"
FAMILY_DIR = SKILL_DATA_DIR / "family_semantics"
if (ENGINE_DIR / "system_b" / "__init__.py").exists() and str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

# Loaded at startup, re-read on each request to pick up late writes (e.g. Step 6b)
_RESULT: dict = {}
_RESULT_PATH: Path | None = None
_RESULT_MTIME: float = 0.0
_CASE_ID: str = "lolla-audit"
_CASE_NAME: str = "Lolla Audit"
_KG_CACHE: dict | None = None
_FAMILY_CACHE: list[dict] | None = None


# ---------------------------------------------------------------------------
# Module-scope rendering helpers — shared across /usage and /audit/* panels.
# Each helper is small and stable so all server-rendered pages can rely on
# the same primitives without re-importing or wrapping. Lifting them out of
# the original `_render_usage_html` enclosure was the prerequisite for
# adding the audit panel family in PR 3 of the 2026-04-28 visibility roadmap.
# ---------------------------------------------------------------------------


def _esc(value) -> str:
    """HTML-escape any value before interpolation.

    Defends against injection from a crafted result.json: model names,
    rejection reasons, evidence quotes, dimension materiality notes, etc.
    Numeric helpers (``_fmt_int``, ``_fmt_usd``) already produce safe output;
    everything else flows through this.
    """
    return html.escape(str(value), quote=True)


def _fmt_int(value) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "—"


def _fmt_usd(value) -> str:
    try:
        return f"${float(value):.4f}"
    except (TypeError, ValueError):
        return "—"


def _fmt_pct(value, *, fraction: bool = False) -> str:
    """Format a number as a percentage. ``fraction=True`` if input is 0..1."""
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if fraction:
        n *= 100
    return f"{n:.1f}%"


# Audit panel routes, ordered for the top nav. The first column is the URL
# fragment (used in href + active-state matching); the second is the label
# the operator sees. Keep the index page (/audit) first so the nav reads
# left-to-right from "everything" to specific panels.
_AUDIT_NAV = (
    ("/audit", "Audit Index"),
    ("/audit/lane1", "Lane 1"),
    ("/audit/lane2", "Lane 2"),
    ("/audit/lane4", "Lane 4"),
    ("/audit/anti-echo", "Anti-echo"),
    ("/audit/routing", "Route Trace"),
    ("/audit/treatment-audit", "Treatment Audit"),
    ("/audit/expansions", "Expansions"),
    ("/audit/stakeholders", "Stakeholders"),
    ("/usage", "Usage"),
)


_SHARED_PANEL_CSS = """
body { font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #222; }
h1 { margin: 0 0 0.5rem; }
h2 { margin-top: 2rem; }
h3 { margin-top: 1.5rem; }
.meta { color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }
.hint { color: #666; font-size: 0.85rem; margin-top: -0.5rem; margin-bottom: 1rem; }
table { border-collapse: collapse; width: 100%; margin-bottom: 2rem; font-size: 0.92rem; }
th, td { text-align: left; padding: 0.5rem 0.75rem; border-bottom: 1px solid #eee; vertical-align: top; }
th { background: #f6f6f6; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.detected-true { color: #c2410c; font-weight: 600; }
.detected-false { color: #666; }
.empty { color: #777; font-style: italic; padding: 0.75rem 1rem; background: #fafafa; border-left: 3px solid #ccc; }
.tagrow { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag { display: inline-block; padding: 0.05rem 0.5rem; border-radius: 3px; background: #eef; font-size: 0.85rem; color: #336; border: 1px solid #ccd; }
.tag.warn { background: #fdecec; color: #832; border-color: #e5b8b8; }
.tag.ok { background: #eafde9; color: #246; border-color: #b8e5b8; }
blockquote.quote { margin: 0; padding: 0.35rem 0.6rem; background: #fafafa; border-left: 3px solid #ddd; color: #333; }
nav.audit-nav { font-size: 0.9rem; padding: 0.5rem 0 1rem; border-bottom: 1px solid #eee; margin-bottom: 1.5rem; }
nav.audit-nav a { color: #336; text-decoration: none; padding: 0.25rem 0.5rem; }
nav.audit-nav a.active { font-weight: 600; color: #222; background: #eef; border-radius: 3px; }
nav.audit-nav a:hover { text-decoration: underline; }
code { background: #f0f0f0; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.9em; }
details { margin: 0.5rem 0; }
details summary { cursor: pointer; color: #336; padding: 0.25rem 0; }
details[open] summary { margin-bottom: 0.5rem; }

/* Headline summary — one sentence after the run-header, before sections */
p.lede { font-size: 1rem; color: #222; margin: 0.5rem 0 1.5rem; line-height: 1.5; }
p.lede strong { color: #111; }

/* Run-header strip — case identity + back-link, on every /audit/* page */
.run-header { color: #666; font-size: 0.9rem; margin: 0 0 1rem; }
.run-header strong { color: #222; }
.run-header a { color: #336; text-decoration: none; }
.run-header a:hover { text-decoration: underline; }

/* Run-vitals strip on /audit index — at-a-glance pulse of this run */
.vitals { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.75rem 0 1.5rem; }
.vitals .tag { background: #f6f6f6; color: #222; border-color: #ddd; font-size: 0.9rem; padding: 0.2rem 0.6rem; }

"""


# Telemetry FAB — injected into the SPA's index.html on /, the *only* bridge
# from the case/factual product surface to the system-reasoning surface at
# /audit. Lives in its own constant (not in _SHARED_PANEL_CSS) because the
# FAB only renders on /; the audit panels and /usage never carry it.
_TELEMETRY_FAB_HTML = (
    '<a href="/audit" class="telemetry-fab" '
    'aria-label="View run telemetry">TELEMETRY <span aria-hidden="true">&rarr;</span></a>'
)

_TELEMETRY_FAB_STYLE = """
<style>
/* Telemetry FAB lives at bottom-right so it never sits in the lane of
   the SPA's right-side .sidebar (which fills the top-right vertical band)
   or its on-demand .drawer-panel close button. z-index 50 keeps it above
   ordinary page content but below any SPA modal/overlay (which sit at
   100/101). The original bug shipped at top-right z=9999 — that visually
   cropped the sidebar's first card and intercepted clicks on the drawer's
   close X. Bottom-right is empty real estate in the SPA bundle. */
/* Match the SPA's design tokens (deep indigo bg, teal accent, mono uppercase
   labels) so the FAB reads as part of the system, not a tacked-on add-on. */
.telemetry-fab {
  position: fixed; bottom: 20px; right: 20px; z-index: 50;
  padding: 0.55rem 1.1rem; border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #41FFA7;
  border: 1px solid rgba(255, 255, 255, 0.22);
  font-family: "JetBrains Mono", "Fira Code", ui-monospace, monospace;
  font-size: 12px; font-weight: 500; letter-spacing: 0.1em;
  text-transform: uppercase; text-decoration: none;
  backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  transition: background 120ms ease, border-color 120ms ease;
}
.telemetry-fab:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.4);
  color: #41FFA7; text-decoration: none;
}
.telemetry-fab:focus-visible { outline: 2px solid #41FFA7; outline-offset: 2px; }
@media (max-width: 600px) {
  .telemetry-fab { bottom: 14px; right: 14px; padding: 0.45rem 0.85rem; font-size: 11px; }
}
/* Belt-and-suspenders: when the SPA opens its modal drawer, hide the FAB
   entirely so it cannot intercept clicks on the drawer's close button even
   under unusual stacking contexts. */
body:has(.drawer-overlay) .telemetry-fab,
body:has(.drawer-panel) .telemetry-fab {
  display: none;
}
</style>
"""


def _inject_telemetry_fab(html_bytes: bytes) -> bytes:
    """Insert the Telemetry FAB anchor + style into the SPA's index.html.

    String-injection at the byte-stream layer — does NOT modify the bundle on
    disk and works whether the SPA was built recently or long ago. Idempotent
    via the ``telemetry-fab`` marker so accidental double-serves don't render
    two buttons. Falls back to appending if the bundle has no ``</body>`` tag.
    """
    try:
        text = html_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return html_bytes
    if "telemetry-fab" in text:
        return html_bytes
    inject = _TELEMETRY_FAB_STYLE + _TELEMETRY_FAB_HTML
    if "</body>" in text:
        text = text.replace("</body>", inject + "</body>", 1)
    else:
        text = text + inject
    return text.encode("utf-8")


def _render_scaffold(*, title: str, body: str, current_path: str = "") -> str:
    """Wrap a page body in the shared HTML scaffold (header, nav, footer).

    All audit panels and the existing /usage page use the same look so
    operators can move between them without re-orienting. ``current_path``
    is matched exactly against ``_AUDIT_NAV`` URLs to highlight the active
    tab.
    """
    nav_links = "".join(
        f'<a href="{_esc(href)}"'
        f'{" class=\"active\"" if current_path == href else ""}'
        f">{_esc(label)}</a>"
        for href, label in _AUDIT_NAV
    )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{_esc(title)}</title>
<style>{_SHARED_PANEL_CSS}</style></head><body>
<nav class="audit-nav">
  <a href="/">Observatory</a> ·
  {nav_links}
</nav>
{body}
</body></html>
"""


def _captured_at_str() -> str:
    """Derive a human run-capture timestamp from the result file path.

    Archived runs live at ``runs/<case-slug>/<UTC-stamp>/result.json`` where
    ``<UTC-stamp>`` is e.g. ``20260425T121607Z``. We surface that as the
    "Captured" field in the run-header. Returns ``""`` when no path is
    known (e.g. fixture-driven tests, ad-hoc result loads).
    """
    if _RESULT_PATH is None:
        return ""
    parent = _RESULT_PATH.parent.name
    if len(parent) == 16 and parent.endswith("Z") and parent[8:9] == "T":
        return f"{parent[0:4]}-{parent[4:6]}-{parent[6:8]} {parent[9:11]}:{parent[11:13]}:{parent[13:15]}Z"
    return parent


def _render_run_header() -> str:
    """Compact run identity strip rendered above the lede on every /audit/* panel.

    Defensive about field availability — older archived runs don't carry
    ``run_id`` or top-level ``fingerprint``. We always show the case name
    and the back-link to the SPA; the rest is best-effort.
    """
    bits: list[str] = []

    case_name = _CASE_NAME or "—"
    bits.append(f"Case: <strong>{_esc(case_name)}</strong>")

    captured = _captured_at_str()
    if captured:
        bits.append(f"Captured: <code>{_esc(captured)}</code>")

    rh = _RESULT.get("run_health") or {}
    overall = rh.get("overall")
    if overall:
        bits.append(f"Health: <code>{_esc(overall)}</code>")

    us = _RESULT.get("usage_summary") or {}
    run_id = us.get("run_id")
    if run_id:
        run_id_str = str(run_id)
        bits.append(
            f'Run: <code title="{_esc(run_id_str)}">{_esc(run_id_str[:24])}</code>'
        )

    bits.append('<a href="/">← back to result</a>')

    return f'<div class="run-header">{" · ".join(bits)}</div>'


def _empty_inline(message: str) -> str:
    """Inline empty-state block — keeps page chrome (nav + run-header + h1)."""
    return f'<div class="empty">{message}</div>'


def _reload_result_if_changed():
    """Re-read the result JSON from disk if the file has been modified."""
    global _RESULT, _RESULT_MTIME
    if _RESULT_PATH is None:
        return
    try:
        mtime = _RESULT_PATH.stat().st_mtime
    except OSError:
        return
    if mtime > _RESULT_MTIME:
        with open(_RESULT_PATH) as f:
            _RESULT = json.load(f)
        _RESULT_MTIME = mtime


def _joined_user_turns(extraction: dict) -> str:
    """Concatenate user-turn text from the serialized conversation."""
    return "\n\n".join(
        t.get("text", "")
        for t in extraction.get("turns", [])
        if t.get("speaker") == "user"
    )


def _joined_assistant_turns(extraction: dict) -> str:
    """Concatenate assistant-turn text from the serialized conversation."""
    return "\n\n".join(
        t.get("text", "")
        for t in extraction.get("turns", [])
        if t.get("speaker") == "assistant"
    )


def _derive_case_name(result: dict) -> str:
    """Derive a human-readable case name from the pipeline result.

    Prefers the extraction's decision_situation (a clean one-liner produced by
    the extraction step). Falls back to the first user turn's leading clause.
    """
    extraction = result.get("extraction", {})
    decision_situation = extraction.get("decision_situation", "").strip()
    if decision_situation:
        # decision_situation is already concise; just clip if abnormally long
        if len(decision_situation) > 140:
            return decision_situation[:140].rsplit(" ", 1)[0]
        return decision_situation

    first_user_turn = _joined_user_turns(extraction).split("\n\n", 1)[0].strip()
    if not first_user_turn:
        return "Lolla Audit"
    # Take first line
    first_line = first_user_turn.split("\n")[0].strip()
    # Try to find a natural sentence or clause break within 100 chars
    for sep in [". ", "; "]:
        idx = first_line.find(sep)
        if 20 < idx < 100:
            return first_line[:idx]
    # Try subordinate clause breaks for long sentences
    for sep in [", amid ", ", with stakes", ", with ", " in a "]:
        idx = first_line.find(sep)
        if 30 < idx < 140:
            return first_line[:idx]
    # Fallback: truncate at 90 chars on word boundary
    if len(first_line) > 90:
        truncated = first_line[:90].rsplit(" ", 1)[0]
        return truncated
    return first_line


def _load_kg() -> dict:
    global _KG_CACHE
    if _KG_CACHE is None:
        kg_path = SKILL_DATA_DIR / "knowledge_graph.json"
        if kg_path.exists():
            with open(kg_path) as f:
                _KG_CACHE = json.load(f)
        else:
            _KG_CACHE = {}
    return _KG_CACHE


def _get_kg_stats() -> dict:
    kg = _load_kg()
    models = kg.get("models", {})
    edges = kg.get("edges", [])
    tendencies = kg.get("tendencies", {})
    total_fm = sum(len(m.get("failure_modes", [])) for m in models.values())
    total_pm = sum(len(m.get("premortem_questions", [])) for m in models.values())
    total_h = sum(len(m.get("heuristics", [])) for m in models.values())
    return {
        "model_count": len(models),
        "tendency_count": len(tendencies),
        "edge_count": len(edges),
        "failure_mode_count": total_fm,
        "premortem_count": total_pm,
        "heuristic_count": total_h,
    }


def _get_model_detail(model_id: str) -> dict | None:
    kg = _load_kg()
    models = kg.get("models", {})
    model = models.get(model_id)
    if not model:
        return None

    edges = kg.get("edges", [])
    allies, antagonists, tensions = [], [], []
    seen: set[tuple[str, str]] = set()
    for e in edges:
        etype = e.get("type")
        if etype not in ("ally", "antagonist", "tension"):
            continue
        if e.get("source") == model_id:
            neighbor_id = e.get("target")
        elif e.get("target") == model_id:
            neighbor_id = e.get("source")
        else:
            continue
        dedup_key = (etype, neighbor_id)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        bucket = allies if etype == "ally" else antagonists if etype == "antagonist" else tensions
        neighbor_model = models.get(neighbor_id, {})
        bucket.append({
            "model_id": neighbor_id,
            "display_name": neighbor_model.get("display_name", neighbor_id),
            "affinity": 0.0,
        })

    def _normalize(items: list) -> list[dict]:
        out = []
        for item in items:
            if isinstance(item, str):
                out.append({"description": item})
            elif isinstance(item, dict):
                if "description" not in item:
                    item["description"] = item.get("question") or item.get("text") or str(item)
                out.append(item)
            else:
                out.append({"description": str(item)})
        return out

    raw_fm = model.get("failure_modes", [])
    raw_pm = model.get("premortem_questions", [])
    raw_h = model.get("heuristics", [])
    return {
        "model_id": model_id,
        "display_name": model.get("display_name", model_id),
        "select_when": model.get("select_when"),
        "danger_when": model.get("danger_when"),
        "failure_mode_count": len(raw_fm),
        "failure_modes_sample": raw_fm[:2],
        "premortem_count": len(raw_pm),
        "premortem_sample": _normalize(raw_pm[:2]),
        "heuristic_count": len(raw_h),
        "heuristics_sample": _normalize(raw_h[:2]),
        "reasoning_types": model.get("reasoning_types", []),
        "allies": sorted(allies, key=lambda x: x["display_name"]),
        "antagonists": sorted(antagonists, key=lambda x: x["display_name"]),
        "tensions": sorted(tensions, key=lambda x: x["display_name"]),
    }


def _load_json_safe(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _load_families() -> list[dict]:
    """Load family clusters, enriching members with display names from KG."""
    global _FAMILY_CACHE
    if _FAMILY_CACHE is not None:
        return _FAMILY_CACHE
    if not FAMILY_DIR.is_dir():
        _FAMILY_CACHE = []
        return _FAMILY_CACHE
    kg = _load_kg()
    models_db = kg.get("models", {})
    families = []
    for fp in sorted(FAMILY_DIR.iterdir()):
        if fp.suffix != ".json":
            continue
        data = _load_json_safe(fp)
        if not data or "family_id" not in data:
            continue
        members_enriched = []
        for mid in data.get("members", []):
            m = models_db.get(mid, {})
            members_enriched.append({
                "model_id": mid,
                "display_name": m.get("display_name", mid.replace("-", " ").title()),
            })
        families.append({
            "family_id": data["family_id"],
            "member_count": len(members_enriched),
            "members": members_enriched,
            "corrected_thesis": data.get("corrected_thesis") or data.get("original_thesis") or "",
            "what_this_stack_defeats": data.get("what_this_stack_defeats", ""),
            "density": data.get("density", 0.0),
            "validation_status": data.get("validation_status", ""),
        })
    _FAMILY_CACHE = families
    return _FAMILY_CACHE


def _get_family_detail(family_id: str) -> dict | None:
    """Return full family data including internal edges between members."""
    families = _load_families()
    family = None
    for f in families:
        if f["family_id"] == family_id:
            family = f
            break
    if family is None:
        return None
    member_ids = {m["model_id"] for m in family["members"]}
    kg = _load_kg()
    internal_edges = []
    seen: set[tuple[str, str, str]] = set()
    for e in kg.get("edges", []):
        src, tgt = e.get("source", ""), e.get("target", "")
        etype = e.get("type", "")
        if src in member_ids and tgt in member_ids:
            key = (src, tgt, etype)
            if key not in seen:
                seen.add(key)
                internal_edges.append({"source": src, "target": tgt, "type": etype})
    return {**family, "internal_edges": internal_edges}


def _build_graph_response() -> dict:
    """Build the reasoning graph for the current case.

    Nodes: companion models (large), chunk-referenced models (medium),
    KG neighbors (small). Edges: ally/antagonist/tension from KG.
    """
    _reload_result_if_changed()
    r = _RESULT
    kg = _load_kg()
    models_db = kg.get("models", {})
    kg_edges = kg.get("edges", [])
    tendencies_db = kg.get("tendencies", {})

    # 1. Companion model IDs (active in the answer)
    companion = r.get("companion_cheat_sheet", {})
    companion_ids = {a["model_id"] for a in companion.get("anchors", [])}

    # 2. Chunk-referenced model IDs (mentioned in provenance)
    chunk_ref_ids: set[str] = set()
    for a in companion.get("anchors", []):
        for c in a.get("chunks", []):
            rtid = c.get("provenance", {}).get("relation_target_id", "")
            if rtid and rtid not in companion_ids:
                chunk_ref_ids.add(rtid)

    # 3. Seed set = companion + chunk_ref
    seed_ids = companion_ids | chunk_ref_ids

    # 4. Find edges involving seed models (ally/antagonist/tension)
    TYPE_MAP = {"structured_tension": "tension"}
    GRAPH_TYPES = {"ally", "antagonist", "structured_tension"}
    neighbor_ids: set[str] = set()
    graph_edges: list[dict] = []
    seen_edges: set[tuple[str, str, str]] = set()

    for e in kg_edges:
        etype = e.get("type", "")
        if etype not in GRAPH_TYPES:
            continue
        src, tgt = e.get("source", ""), e.get("target", "")
        if not (src in seed_ids or tgt in seed_ids):
            continue
        edge_type = TYPE_MAP.get(etype, etype)
        key = (src, tgt, edge_type)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        graph_edges.append({
            "source": src,
            "target": tgt,
            "type": edge_type,
            "affinity": 0.5,
            "description": e.get("context", ""),
        })
        if src not in seed_ids:
            neighbor_ids.add(src)
        if tgt not in seed_ids:
            neighbor_ids.add(tgt)

    # Cap neighbors to avoid an overwhelming graph
    MAX_NEIGHBORS = 20
    if len(neighbor_ids) > MAX_NEIGHBORS:
        # Keep neighbors with most connections to seed nodes
        from collections import Counter
        neighbor_conn: Counter = Counter()
        for e in graph_edges:
            if e["source"] in neighbor_ids:
                neighbor_conn[e["source"]] += 1
            if e["target"] in neighbor_ids:
                neighbor_conn[e["target"]] += 1
        top = {nid for nid, _ in neighbor_conn.most_common(MAX_NEIGHBORS)}
        neighbor_ids = top
        graph_edges = [
            e for e in graph_edges
            if e["source"] in seed_ids | neighbor_ids
            and e["target"] in seed_ids | neighbor_ids
        ]

    # 5. Build nodes
    all_ids = companion_ids | chunk_ref_ids | neighbor_ids
    nodes: list[dict] = []
    for mid in all_ids:
        m = models_db.get(mid, {})
        if mid in companion_ids:
            role = "companion"
        elif mid in chunk_ref_ids:
            role = "chunk_ref"
        else:
            role = "neighbor"
        nodes.append({
            "id": mid,
            "label": m.get("display_name", mid.replace("-", " ").title()),
            "role": role,
        })

    # 6. Tendencies linked to detected tendency IDs
    detected_tids = r.get("detected_tendencies", [])
    if isinstance(detected_tids, list):
        detected_tids = [t if isinstance(t, str) else t.get("tendency_id", "") for t in detected_tids]
    else:
        detected_tids = []

    tendency_list: list[dict] = []
    for tid in detected_tids:
        t = tendencies_db.get(tid, {})
        if not t:
            continue
        tendency_list.append({
            "tendency_id": tid,
            "display_name": t.get("display_name", tid),
            "core_models": [m["model"] if isinstance(m, dict) else m for m in t.get("core_models", [])],
            "antidote_models": [m["model"] if isinstance(m, dict) else m for m in t.get("antidote_models", [])],
        })

    return {
        "stats": _get_kg_stats(),
        "tendencies": tendency_list,
        "nodes": nodes,
        "edges": graph_edges,
    }


def _get_tendency_catalog() -> list[dict]:
    kg = _load_kg()
    tendencies = kg.get("tendencies", {})
    result = []
    for tid, t in sorted(tendencies.items(), key=lambda x: x[1].get("number", 99)):
        result.append({
            "tendency_id": tid,
            "number": t.get("number"),
            "display_name": t.get("display_name", tid),
            "description": t.get("description", ""),
            "core_models": [m["model"] if isinstance(m, dict) else m for m in t.get("core_models", [])],
            "antidote_models": [m["model"] if isinstance(m, dict) else m for m in t.get("antidote_models", [])],
        })
    return result


def _build_case_response() -> dict:
    """Build the case response from the loaded pipeline result."""
    _reload_result_if_changed()
    r = _RESULT

    delta_card = r.get("delta_card")
    companion = r.get("companion_cheat_sheet")
    frame_pressure_card = r.get("frame_pressure_card")
    structural_coverage_card = r.get("structural_coverage_card")
    revised_answer = r.get("revised_answer")

    # Build case metadata from the serialized conversation. Observatory shows
    # query (joined user turns) and vanilla_answer (joined assistant turns)
    # in the case header for context alongside cards/audit data.
    extraction = r.get("extraction", {})
    case_meta = {
        "case_id": _CASE_ID,
        "query": _joined_user_turns(extraction),
        "vanilla_answer": _joined_assistant_turns(extraction),
    }

    audit_trace = r.get("audit_summary")

    response = {
        "case": case_meta,
        "delta_card": delta_card,
        "companion": companion,
        "frame_pressure_card": frame_pressure_card,
        "structural_coverage_card": structural_coverage_card,
        "audit_trace": audit_trace,
        "revised_answer": revised_answer,
        "revised_answer_source": r.get("revised_answer_source"),
        "revised_answer_present": r.get("revised_answer_present", revised_answer is not None),
        "gap_check": r.get("gap_check"),
        "gap_check_summary": r.get("gap_check_summary"),
        "has_gap_check": r.get("has_gap_check", False),
        "stakeholder_assumption_check": r.get("stakeholder_assumption_check"),
        "bullshit_profile": r.get("bullshit_profile"),
    }

    # Run health — surfaces capture, substrate, embeddings, fingerprint status
    run_health = r.get("run_health")
    if run_health:
        response["run_health"] = run_health

    # Usage summary — per-run cost & call-count telemetry. Built by
    # run_pipeline.py and (for sub-agent calls) topped up by SKILL Step 8b.
    usage_summary = r.get("usage_summary")
    if usage_summary:
        response["usage_summary"] = usage_summary

    # Prompt versions — per-stage hashes of the system prompts used in this
    # run. Useful for reproducibility (which prompt revision produced this
    # finding) and for diffing two runs of the same case. Include the field
    # whenever the key exists (even if `{}`) so consumers can distinguish
    # "supported but empty" from "not provided" — keeps the API shape stable.
    if "prompt_versions" in r:
        response["prompt_versions"] = r.get("prompt_versions") or {}

    return response


def _render_usage_html() -> str:
    """Standalone HTML page that visualizes usage_summary.

    Lives at /usage so the user can inspect cost/calls without depending on
    the React SPA being rebuilt to consume the new field. The SPA already
    receives ``usage_summary`` via /api/case/<id>; this page is a fallback
    that's guaranteed to render whatever the pipeline wrote.
    """
    _reload_result_if_changed()
    us = _RESULT.get("usage_summary") or {}
    if not us:
        return _render_scaffold(
            title="Lolla — Usage Summary",
            current_path="/usage",
            body=(
                "<h1>Usage Summary</h1>"
                "<div class=\"empty\">No <code>usage_summary</code> in this result. "
                "Re-run the pipeline with the updated <code>run_pipeline.py</code> "
                "to populate it.</div>"
            ),
        )
    vendors = us.get("vendors", {}) or {}

    rows = []
    rows.append(
        "<tr><th>Vendor</th><th>Calls</th><th>Tokens (in / cached / out)</th>"
        "<th>Cache hit</th><th>Estimated cost</th></tr>"
    )
    for key, label in [
        ("openrouter", "OpenRouter"),
        ("openai_embeddings", "OpenAI (embeddings + expansion)"),
        ("anthropic_subagents", "Anthropic (Step-7 sub-agents)"),
    ]:
        v = vendors.get(key) or {}
        if not v:
            continue
        if key == "openrouter":
            tokens = (
                f"{_fmt_int(v.get('prompt_tokens'))} / "
                f"{_fmt_int(v.get('cached_tokens'))} / "
                f"{_fmt_int(v.get('completion_tokens'))}"
            )
            cache = f"{(v.get('cache_hit_rate') or 0) * 100:.1f}%"
        elif key == "openai_embeddings":
            tokens = (
                f"{_fmt_int(v.get('input_tokens'))} / — / "
                f"{_fmt_int(v.get('output_tokens'))}"
            )
            cache = "n/a"
        else:
            tokens = f"{_fmt_int(v.get('total_tokens'))} (total only)"
            cache = "n/a"
        rows.append(
            f"<tr><td>{_esc(label)}</td><td>{_fmt_int(v.get('calls'))}</td>"
            f"<td>{tokens}</td><td>{cache}</td>"
            f"<td>{_fmt_usd(v.get('estimated_cost_usd'))}</td></tr>"
        )

    # OpenRouter per-stage breakdown — now includes cache-hit % per stage,
    # which is the key signal for "where is caching actually working." On a
    # typical Lolla run BI pulls high cache rates (shared system prompt
    # across passages); pipeline lanes pull low rates because each stage
    # has a different system prompt. Surfacing the gap directly tells the
    # operator where the next prompt-restructuring win lives.
    or_block = vendors.get("openrouter") or {}
    stage_rows = []
    for stage, totals in sorted(
        (or_block.get("stages") or {}).items(),
        key=lambda kv: -kv[1].get("calls", 0),
    ):
        prompt_tok = totals.get("prompt_tokens", 0) or 0
        cached_tok = totals.get("cached_tokens", 0) or 0
        hit_rate = (cached_tok / prompt_tok * 100) if prompt_tok else 0.0
        stage_rows.append(
            f"<tr><td>{_esc(stage)}</td>"
            f"<td>{_fmt_int(totals.get('calls'))}</td>"
            f"<td>{_fmt_int(prompt_tok)}</td>"
            f"<td>{_fmt_int(cached_tok)}</td>"
            f"<td>{hit_rate:.1f}%</td>"
            f"<td>{_fmt_int(totals.get('completion_tokens'))}</td></tr>"
        )

    # OpenAI by-model breakdown — surfaces the embed vs. expansion split
    # that the vendor row aggregates away.
    embed_block = vendors.get("openai_embeddings") or {}
    embed_rows = []
    for model, info in (embed_block.get("by_model") or {}).items():
        embed_rows.append(
            f"<tr><td>{_esc(model)}</td>"
            f"<td>{_fmt_int(info.get('calls'))}</td>"
            f"<td>{_fmt_int(info.get('input_tokens'))}</td>"
            f"<td>{_fmt_int(info.get('output_tokens'))}</td>"
            f"<td>{_fmt_usd(info.get('estimated_cost_usd'))}</td></tr>"
        )

    # Anthropic sub-agents by lane — built by the enhanced
    # _build_subagent_vendor_block. Tells the operator which Step-7 lane
    # (1=Delta, 2=Companion, 3=Frame, 4=Coverage) was actually spawned and
    # what each cost. Lanes that were skipped_empty / skipped_error are
    # absent because they shouldn't be in the input records (per the SKILL
    # Step 8b filter).
    sub_block = vendors.get("anthropic_subagents") or {}
    sub_rows = []
    LANE_NAMES = {
        "1": "DeltaCard",
        "2": "CompanionCheatSheet",
        "3": "FramePressureCard",
        "4": "StructuralCoverageCard",
    }
    for lane_key, info in (sub_block.get("by_lane") or {}).items():
        lane_label = f"{lane_key} ({LANE_NAMES.get(lane_key, '?')})" if lane_key in LANE_NAMES else lane_key
        sub_rows.append(
            f"<tr><td>{_esc(lane_label)}</td>"
            f"<td>{_esc(info.get('model'))}</td>"
            f"<td>{_esc(info.get('status'))}</td>"
            f"<td>{_fmt_int(info.get('calls'))}</td>"
            f"<td>{_fmt_int(info.get('total_tokens'))}</td>"
            f"<td>{_fmt_int(info.get('duration_ms'))} ms</td>"
            f"<td>{_fmt_usd(info.get('estimated_cost_usd'))}</td></tr>"
        )

    # Prompt versions — per-stage system-prompt hashes, useful for
    # reproducibility ("which prompt revision produced this finding?") and
    # for diffing two runs of the same case.
    prompt_versions = _RESULT.get("prompt_versions") or {}
    pv_rows = []
    for stage, ver_hash in sorted(prompt_versions.items()):
        # Display the documented 12-char hash form. Upstream currently emits
        # 12 chars already so this is a no-op today; truncating defensively
        # keeps the UI contract stable if upstream ever switches to longer
        # hashes. Full hash is preserved in the title attribute for hover.
        full = str(ver_hash)
        short = full[:12]
        pv_rows.append(
            f"<tr><td>{_esc(stage)}</td>"
            f"<td><code title=\"{_esc(full)}\">{_esc(short)}</code></td></tr>"
        )

    notes_html = "".join(f"<li>{_esc(n)}</li>" for n in (us.get("notes") or []))

    body = f"""
<h1>Usage Summary</h1>
<div class="meta">
  Run: <code>{_esc(us.get("run_id", "—"))}</code> ·
  Pricing table verified: <code>{_esc(us.get("pricing_table_version", "—"))}</code> ·
  <a href="/">back to Observatory</a> ·
  <a href="/audit">audit panels</a>
</div>
<div style="font-size:1.6rem;font-weight:600;margin:1rem 0 1.5rem;">Total estimated cost: <strong>{_fmt_usd(us.get("estimated_total_cost_usd"))}</strong></div>

<h2>By vendor</h2>
<table>{"".join(rows)}</table>

<h2>OpenRouter — by stage</h2>
<p class="hint">Cache-hit % per stage tells you where prompt-prefix sharing is actually working. Stages whose system prompt is identical across calls (e.g. <code>bullshit_index</code> across all passages) cache well; stages with per-call-varying system prompts (most pipeline lanes) cache poorly.</p>
<table>
<tr><th>Stage</th><th>Calls</th><th>Prompt tokens</th><th>Cached tokens</th><th>Cache hit %</th><th>Completion tokens</th></tr>
{"".join(stage_rows) if stage_rows else "<tr><td colspan='6'>No OpenRouter calls recorded.</td></tr>"}
</table>

<h2>OpenAI — by model</h2>
<table>
<tr><th>Model</th><th>Calls</th><th>Input tokens</th><th>Output tokens</th><th>Estimated cost</th></tr>
{"".join(embed_rows) if embed_rows else "<tr><td colspan='5'>No OpenAI calls recorded.</td></tr>"}
</table>

<h2>Anthropic Step-7 sub-agents — by lane</h2>
<p class="hint">Sub-agent token counts come from Claude Code task notifications, which expose <code>total_tokens</code> only — no prompt/completion split. The cost estimate treats the whole total as input (conservative over-estimate).</p>
<table>
<tr><th>Lane</th><th>Model</th><th>Status</th><th>Calls</th><th>Total tokens</th><th>Duration</th><th>Estimated cost</th></tr>
{"".join(sub_rows) if sub_rows else "<tr><td colspan='7'>No sub-agent calls recorded yet (added by SKILL Step 8b after Step 7 completes).</td></tr>"}
</table>

<h2>Prompt versions</h2>
<p class="hint">12-char hash of the system prompt used at each stage. Two runs of the same case with the same hashes received identical prompts. Different hashes mean a prompt revision happened in between.</p>
<table>
<tr><th>Stage</th><th>Prompt hash</th></tr>
{"".join(pv_rows) if pv_rows else "<tr><td colspan='2'>No prompt versions recorded.</td></tr>"}
</table>

<h2>Notes</h2>
<ul class="empty" style="list-style:disc;padding-left:1.5rem;">{notes_html}</ul>
"""
    return _render_scaffold(title="Lolla — Usage Summary", body=body, current_path="/usage")


# ---------------------------------------------------------------------------
# Audit panels (PR 3 of the 2026-04-28 visibility roadmap).
#
# Each panel is server-rendered HTML, mirrors the shape of `_render_usage_html`,
# and works whether or not the SPA bundle is present. They surface the
# `audit_summary` fields the React SPA never renders. Fields added by PR 1
# (raw_message_content per boundary call) and PR 2 (embedding_tendency_ranks,
# deep_check_results.reason, companion_verification_silently_omitted) are
# rendered when present and degrade silently when absent — so panels work
# against both fresh runs and older archived result.json files.
# ---------------------------------------------------------------------------


_TRIAGE_THRESHOLD_DEFAULT = 4
_EMBEDDING_PROMOTION_THRESHOLD = 0.30
_DETECTED_MODELS_CAP_LABEL = "5"  # mirrors engine.system_b.companion_routing._DETECTED_MODELS_CAP
_LANE2_AUTO_OPEN_THRESHOLD = 20  # candidates table opens by default if pool ≤ this; collapsed otherwise


def _audit_summary() -> dict:
    """Pull the audit_summary block, returning ``{}`` for ancient artifacts."""
    return _RESULT.get("audit_summary") or {}


def _route_trace() -> dict:
    audit = _audit_summary()
    trace = audit.get("route_trace")
    if isinstance(trace, dict):
        return trace
    try:
        from system_b.route_trace import build_route_trace_payload
        return build_route_trace_payload(_RESULT)
    except Exception:
        return {}


# ---------------- Panel 1: /audit/lane1 ----------------


def _render_lane1_html() -> str:
    _reload_result_if_changed()
    audit = _audit_summary()

    header = _render_run_header()

    if not audit:
        body = (
            "<h1>Lane 1 — Pass 1 + Pass 2 funnel</h1>"
            f"{header}"
            + _empty_inline(
                "This run was captured before Phase-7 audit observability — "
                "no <code>audit_summary</code> in the result. Re-run the "
                "pipeline to populate the Lane 1 trace."
            )
        )
        return _render_scaffold(title="Lolla — Lane 1", body=body, current_path="/audit/lane1")

    triage = audit.get("triage_scores") or []
    triggered_sources = audit.get("triggered_tendency_sources") or []
    deep_results = audit.get("deep_check_results") or []
    embedding_ranks = audit.get("embedding_tendency_ranks") or []

    # Pass 1 triage table — every scored tendency, sorted by score desc
    triage_rows = []
    for s in sorted(triage, key=lambda r: -int(r.get("score") or 0)):
        triage_rows.append(
            f"<tr><td>{_esc(s.get('tendency_id', ''))}</td>"
            f"<td class='num'>{_esc(s.get('score', 0))}</td>"
            f"<td>{_esc(s.get('evidence', ''))}</td></tr>"
        )

    # Triggered set with source attribution
    src_rows = []
    for t in triggered_sources:
        source = t.get("source", "")
        score = t.get("score", "")
        score_str = f"{float(score):.3f}" if isinstance(score, float) else _esc(score)
        src_rows.append(
            f"<tr><td>{_esc(t.get('tendency_id', ''))}</td>"
            f"<td><span class='tag'>{_esc(source)}</span></td>"
            f"<td class='num'>{score_str}</td></tr>"
        )

    # Pass 2 deep_check outcomes
    pass2_rows = []
    detected_count = 0
    for d in deep_results:
        detected = bool(d.get("detected"))
        if detected:
            detected_count += 1
        cls = "detected-true" if detected else "detected-false"
        verdict = "detected" if detected else "not detected"
        reason = d.get("reason") or ""
        sub_pattern = d.get("sub_pattern") or ""
        pass2_rows.append(
            f"<tr><td>{_esc(d.get('tendency_id', ''))}</td>"
            f"<td class='{cls}'>{verdict}</td>"
            f"<td>{_esc(sub_pattern)}</td>"
            f"<td>{_esc(reason)}</td></tr>"
        )

    # Embedding close-calls — full top-25 ranks (promoted + sub-threshold)
    close_call_rows = []
    for r in embedding_ranks:
        promoted = bool(r.get("promoted"))
        cls = "tag ok" if promoted else "tag"
        label = "promoted" if promoted else "close call"
        score = r.get("score")
        score_str = f"{float(score):.3f}" if isinstance(score, (int, float)) else _esc(score)
        close_call_rows.append(
            f"<tr><td>{_esc(r.get('tendency_id', ''))}</td>"
            f"<td class='num'>{score_str}</td>"
            f"<td><span class='{cls}'>{label}</span></td></tr>"
        )

    lede = (
        f"Of <strong>{len(triage)}</strong> tendencies the system triaged, "
        f"<strong>{len(triggered_sources)}</strong> crossed the Pass 1 threshold "
        f"and Pass 2 confirmed <strong>{detected_count}</strong>."
    )

    body = f"""
<h1>Lane 1 — Pass 1 + Pass 2 funnel</h1>
{header}
<p class="lede">{lede}</p>

<h2>Pass 1 — Triage scores ({len(triage_rows)} tendencies)</h2>
<p class="hint">Triage threshold: <code>{_TRIAGE_THRESHOLD_DEFAULT}</code>. Tendencies at or above this score advance to Pass 2 deep-check; the rest stay observed but unverified.</p>
<table>
<tr><th>Tendency</th><th class="num">Score</th><th>Evidence</th></tr>
{"".join(triage_rows) if triage_rows else "<tr><td colspan='3' class='empty'>No triage scores recorded for this run.</td></tr>"}
</table>

<h2>Triggered set ({len(src_rows)} advanced to Pass 2)</h2>
<p class="hint">Where each promotion came from — <code>triage</code> (Pass 1 score), <code>embedding</code> (cosine match against the catalog), or <code>always_include</code> (rules-based, surfaces regardless of score).</p>
<table>
<tr><th>Tendency</th><th>Source</th><th class="num">Score</th></tr>
{"".join(src_rows) if src_rows else "<tr><td colspan='3' class='empty'>The Pass 1 triage promoted no tendencies on this run.</td></tr>"}
</table>

<h2>Pass 2 — Deep check outcomes</h2>
<p class="hint">For each promoted tendency, the deep check returns a verdict, a sub-pattern label when relevant, and the model's reasoning for either outcome.</p>
<table>
<tr><th>Tendency</th><th>Verdict</th><th>Sub-pattern</th><th>Reason</th></tr>
{"".join(pass2_rows) if pass2_rows else "<tr><td colspan='4' class='empty'>No Pass 2 outcomes — the triage promoted nothing to deep-check.</td></tr>"}
</table>

<h2>Embedding close-calls — full top-25 ranks</h2>
<p class="hint">Cosine match scores for every catalog tendency, including those below the <code>{_EMBEDDING_PROMOTION_THRESHOLD}</code> promotion floor. Sub-threshold rows surface "almost-made-it" cases — useful when calibrating where the floor sits.</p>
<table>
<tr><th>Tendency</th><th class="num">Cosine</th><th>Status</th></tr>
{"".join(close_call_rows) if close_call_rows else "<tr><td colspan='3' class='empty'>No embedding ranks recorded (embeddings off for this run, or run pre-dates PR 2).</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Lane 1", body=body, current_path="/audit/lane1")


# ---------------- Panel 2: /audit/lane2 ----------------


def _render_lane2_html() -> str:
    _reload_result_if_changed()
    audit = _audit_summary()

    header = _render_run_header()

    if not audit:
        body = (
            "<h1>Lane 2 — Companion selection funnel</h1>"
            f"{header}"
            + _empty_inline(
                "This run was captured before Phase-7 audit observability — "
                "no <code>audit_summary</code> in the result."
            )
        )
        return _render_scaffold(title="Lolla — Lane 2", body=body, current_path="/audit/lane2")

    candidates = audit.get("companion_candidates") or []
    accepted_before_cap = audit.get("companion_verification_accepted_before_cap") or []

    if not candidates and not accepted_before_cap:
        body = (
            "<h1>Lane 2 — Companion selection funnel</h1>"
            f"{header}"
            + _empty_inline(
                "Lane 2 stayed quiet on this case — the system surfaced no "
                "companion-model candidates worth verifying."
            )
        )
        return _render_scaffold(title="Lolla — Lane 2", body=body, current_path="/audit/lane2")

    accepted = accepted_before_cap
    capped = audit.get("companion_verification_capped_models") or []
    rejected = audit.get("companion_rejected_models") or []
    duplicates = audit.get("companion_verification_duplicate_accepts") or []
    quote_repairs = audit.get("companion_verification_quote_repairs") or []
    silently_omitted = audit.get("companion_verification_silently_omitted") or []
    candidate_cap = audit.get("companion_candidate_cap", 0)

    final_anchors = (_RESULT.get("companion_cheat_sheet") or {}).get("anchors") or []

    cand_rows = []
    for c in candidates:
        cand_rows.append(
            f"<tr><td>{_esc(c.get('model_id', ''))}</td>"
            f"<td>{_esc(c.get('recall_source', ''))}</td>"
            f"<td class='num'>{_esc(c.get('keyword_rank', ''))}</td>"
            f"<td class='num'>{_esc(c.get('embedding_rank', ''))}</td>"
            f"<td class='num'>{_esc(c.get('final_rank', ''))}</td>"
            f"<td>{_esc(c.get('activation_trigger', ''))}</td></tr>"
        )

    acc_rows = []
    for a in accepted:
        acc_rows.append(
            f"<tr><td>{_esc(a.get('model_id', ''))}</td>"
            f"<td>{_esc(a.get('presence_mode', ''))}</td>"
            f"<td>{_esc(a.get('evidence_quote', ''))}</td>"
            f"<td>{_esc(a.get('presence_explanation', ''))}</td></tr>"
        )

    rej_rows = []
    for r in rejected:
        rej_rows.append(
            f"<tr><td>{_esc(r.get('model_id', ''))}</td>"
            f"<td>{_esc(r.get('rejection_reason', ''))}</td></tr>"
        )

    cap_rows = [
        f"<tr><td>{_esc(c.get('model_id', ''))}</td><td>{_esc(c.get('drop_reason', ''))}</td></tr>"
        for c in capped
    ]
    dup_rows = [
        f"<tr><td>{_esc(d.get('model_id', ''))}</td><td>{_esc(d.get('drop_reason', ''))}</td></tr>"
        for d in duplicates
    ]
    qr_rows = [
        f"<tr><td>{_esc(q.get('model_id', ''))}</td>"
        f"<td>{_esc(q.get('repair_method', ''))}</td>"
        f"<td>{_esc(q.get('original_evidence_quote', ''))}</td>"
        f"<td>{_esc(q.get('repaired_evidence_quote', ''))}</td></tr>"
        for q in quote_repairs
    ]
    so_rows = [
        f"<tr><td>{_esc(s.get('model_id', ''))}</td><td>{_esc(s.get('drop_reason', ''))}</td></tr>"
        for s in silently_omitted
    ]

    lede = (
        f"From <strong>{len(candidates)}</strong> companion candidates, the system "
        f"surfaced <strong>{len(final_anchors)}</strong> cheat-sheet anchors. "
        f"<strong>{len(quote_repairs)}</strong> arrived via verifier-repaired quotes; "
        f"<strong>{len(silently_omitted)}</strong> the verifier never named."
    )

    # Threshold-based collapse — small candidate pools open inline (operator
    # sees everything at a glance); larger ones collapse to keep the page
    # scannable. Threshold lives in _LANE2_AUTO_OPEN_THRESHOLD.
    cand_open_attr = " open" if len(candidates) <= _LANE2_AUTO_OPEN_THRESHOLD else ""
    cand_table = (
        "<table>"
        '<tr><th>Model</th><th>Recall source</th><th class="num">Kw rank</th>'
        '<th class="num">Emb rank</th><th class="num">Final rank</th>'
        "<th>Activation trigger</th></tr>"
        + ("".join(cand_rows) if cand_rows else "<tr><td colspan='6' class='empty'>No candidates on this run.</td></tr>")
        + "</table>"
    )

    body = f"""
<h1>Lane 2 — Companion selection funnel</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">Candidate pool cap: <code>{_esc(candidate_cap)}</code>. The system pulls candidates via keyword, embedding, and curated activation triggers, then verifies each against the conversation before promoting up to the top {_DETECTED_MODELS_CAP_LABEL} as cheat-sheet anchors.</p>

<details{cand_open_attr}>
<summary><strong>Candidates ({len(candidates)} sent to verifier)</strong>{" · click to expand" if not cand_open_attr else ""}</summary>
{cand_table}
</details>

<h2>Accepted before top-{_DETECTED_MODELS_CAP_LABEL} cap ({len(accepted)})</h2>
<p class="hint">Verifier-confirmed candidates that carried evidence the system could quote. The cap then trims to the strongest few; surplus rows show under <em>Capped</em>.</p>
<table>
<tr><th>Model</th><th>Mode</th><th>Evidence quote</th><th>Explanation</th></tr>
{"".join(acc_rows) if acc_rows else "<tr><td colspan='4' class='empty'>The verifier confirmed none of the candidates on this run.</td></tr>"}
</table>

<h2>Rejected ({len(rejected)})</h2>
<p class="hint">Candidates the verifier examined and declined to surface, with the reasoning the model gave.</p>
<table>
<tr><th>Model</th><th>Rejection reason</th></tr>
{"".join(rej_rows) if rej_rows else "<tr><td colspan='2' class='empty'>The verifier rejected none — every candidate it considered passed muster.</td></tr>"}
</table>

<h2>Capped — accepted but not surfaced ({len(capped)})</h2>
<p class="hint">Candidates the verifier accepted but the top-{_DETECTED_MODELS_CAP_LABEL} cap held back. Visible here so the operator can see what would have surfaced if the cap were higher.</p>
<table>
<tr><th>Model</th><th>Drop reason</th></tr>
{"".join(cap_rows) if cap_rows else "<tr><td colspan='2' class='empty'>The accepted set fit under the cap on this run.</td></tr>"}
</table>

<h2>Duplicate accepts ({len(duplicates)})</h2>
<p class="hint">When the verifier names the same model twice, only the first is kept. Duplicates often signal a verifier-prompt clarity issue worth tuning.</p>
<table>
<tr><th>Model</th><th>Drop reason</th></tr>
{"".join(dup_rows) if dup_rows else "<tr><td colspan='2' class='empty'>The verifier named each accepted model once.</td></tr>"}
</table>

<h2>Quote repairs ({len(quote_repairs)})</h2>
<p class="hint">When the verifier returns an evidence quote that doesn't match the source verbatim, the repair pass fixes it. Visible repairs are healthy — invisible ones would be drift.</p>
<table>
<tr><th>Model</th><th>Method</th><th>Original</th><th>Repaired</th></tr>
{"".join(qr_rows) if qr_rows else "<tr><td colspan='4' class='empty'>Every accepted quote matched its source on the first pass.</td></tr>"}
</table>

<h2>Silently omitted by verifier ({len(silently_omitted)})</h2>
<p class="hint">Candidates sent to the verifier that never appeared in either accepted or rejected. A verifier prompt-tuning signal — when this grows, the verifier is dropping context. Drop reason: <code>not_in_verifier_response</code>.</p>
<table>
<tr><th>Model</th><th>Drop reason</th></tr>
{"".join(so_rows) if so_rows else "<tr><td colspan='2' class='empty'>The verifier named every candidate it received (or the run pre-dates PR 2).</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Lane 2", body=body, current_path="/audit/lane2")


# ---------------- Panel 4: /audit/lane4 ----------------


def _load_lane4_dimension_catalog() -> list[dict[str, str]]:
    """Return the 15-dimension catalog from data/knowledge_graph.json.

    Cached at module level via ``_KG_CACHE``. Each row carries
    ``dimension_id`` + ``dimension_name``. Loaded at render time so the
    panel always reflects the live catalog.
    """
    global _KG_CACHE
    if _KG_CACHE is None:
        try:
            with open(SKILL_DATA_DIR / "knowledge_graph.json") as f:
                _KG_CACHE = json.load(f)
        except OSError:
            return []
    sc = (_KG_CACHE or {}).get("structural_coverage_routing", {}) or {}
    dims = sc.get("dimensions", {}) or {}
    return [
        {"dimension_id": d_id, "dimension_name": d.get("dimension_name", d_id)}
        for d_id, d in dims.items()
    ]


def _render_lane4_html() -> str:
    _reload_result_if_changed()
    coverage = _RESULT.get("structural_coverage_card") or {}
    catalog = _load_lane4_dimension_catalog()

    header = _render_run_header()

    if not catalog:
        body = (
            "<h1>Lane 4 — Dimension coverage</h1>"
            f"{header}"
            + _empty_inline(
                "Dimension catalog not found in "
                "<code>data/knowledge_graph.json</code>."
            )
        )
        return _render_scaffold(title="Lolla — Lane 4", body=body, current_path="/audit/lane4")

    detected_dims = coverage.get("dimensions") or []
    detected_by_id = {d.get("dimension_id"): d for d in detected_dims if d.get("dimension_id")}
    gap_questions_by_id: dict[str, list[str]] = {}
    for gq in coverage.get("gap_questions") or []:
        if isinstance(gq, dict) and gq.get("dimension_id"):
            qs = gq.get("questions") or []
            if isinstance(qs, list):
                gap_questions_by_id[gq["dimension_id"]] = [str(q) for q in qs]

    question_type = coverage.get("question_type", "")

    # 15-row dimension table
    dim_rows = []
    covered_count = 0
    gap_count = 0
    for cat in catalog:
        d_id = cat["dimension_id"]
        d_name = cat["dimension_name"]
        dim = detected_by_id.get(d_id)
        if not dim:
            status = "<span class='tag'>not detected</span>"
            covered = "—"
            note = "—"
        elif dim.get("covered"):
            covered_count += 1
            status = "<span class='tag ok'>covered</span>"
            covered = _esc(dim.get("coverage_evidence", ""))
            note = _esc(dim.get("materiality_note", ""))
        else:
            gap_count += 1
            status = "<span class='tag warn'>gap</span>"
            covered = "—"
            note = _esc(dim.get("materiality_note", ""))
        dim_rows.append(
            f"<tr><td>{_esc(d_id)}</td><td>{_esc(d_name)}</td>"
            f"<td>{status}</td><td>{covered}</td><td>{note}</td></tr>"
        )

    # Gap routes
    route_rows = []
    for r in (coverage.get("gap_routes") or []):
        cands = ", ".join(_esc(m) for m in (r.get("candidate_model_ids") or []))
        excluded = ", ".join(_esc(m) for m in (r.get("excluded_model_ids") or []))
        route_rows.append(
            f"<tr><td>{_esc(r.get('dimension_id', ''))}</td>"
            f"<td>{cands or '—'}</td><td>{excluded or '—'}</td></tr>"
        )

    # Gap questions
    gq_rows = []
    for d_id, qs in gap_questions_by_id.items():
        for q in qs:
            gq_rows.append(f"<tr><td>{_esc(d_id)}</td><td>{_esc(q)}</td></tr>")

    observed_count = len(detected_dims)

    lede = (
        f"Of <strong>{len(catalog)}</strong> catalog dimensions, the system "
        f"observed <strong>{observed_count}</strong> in this case — "
        f"<strong>{covered_count}</strong> covered, "
        f"<strong>{gap_count}</strong> flagged as gaps. "
        f"Question type: <code>{_esc(question_type) or '—'}</code>."
    )

    body = f"""
<h1>Lane 4 — Dimension coverage</h1>
{header}
<p class="lede">{lede}</p>

<h2>{len(catalog)}-dimension catalog</h2>
<p class="hint">Every catalog dimension, marked by status: <span class="tag ok">covered</span> when the answer addresses it, <span class="tag warn">gap</span> when the system observed but the answer didn't address, <span class="tag">not detected</span> when the case never raised it.</p>
<table>
<tr><th>Dimension ID</th><th>Name</th><th>Status</th><th>Coverage evidence</th><th>Materiality</th></tr>
{"".join(dim_rows)}
</table>

<h2>Gap routes</h2>
<p class="hint">For each gap dimension, the curated routing names corrective models. <em>Excluded</em> column shows models held back by anti-echo because earlier lanes already surfaced them — see <a href="/audit/anti-echo">/audit/anti-echo</a> for the cascade view.</p>
<table>
<tr><th>Dimension</th><th>Candidate models</th><th>Excluded (anti-echo)</th></tr>
{"".join(route_rows) if route_rows else "<tr><td colspan='3' class='empty'>No gap routes on this run — every observed dimension was covered or no gaps surfaced.</td></tr>"}
</table>

<h2>Gap questions</h2>
<p class="hint">Questions the user can pose to themselves to address each gap directly — generated from the curated dimension materiality.</p>
<table>
<tr><th>Dimension</th><th>Question</th></tr>
{"".join(gq_rows) if gq_rows else "<tr><td colspan='2' class='empty'>No gap questions on this run.</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Lane 4", body=body, current_path="/audit/lane4")


# ---------------- Panel: /audit/anti-echo ----------------


def _render_anti_echo_html() -> str:
    _reload_result_if_changed()
    coverage = _RESULT.get("structural_coverage_card") or {}
    excluded = coverage.get("anti_echo_model_ids") or []

    header = _render_run_header()

    if not excluded:
        body = (
            "<h1>Anti-echo cascade</h1>"
            f"{header}"
            + _empty_inline(
                "No anti-echo cascading on this run — every Lane 4 candidate "
                "stood on its own."
            )
        )
        return _render_scaffold(title="Lolla — Anti-echo", body=body, current_path="/audit/anti-echo")

    # Compute per-lane source attribution.
    # Lane 1: delta_card.findings[*].selected_model_ids
    lane1_models: set[str] = set()
    for f in (_RESULT.get("delta_card") or {}).get("findings") or []:
        for mid in (f.get("selected_model_ids") or []):
            if mid:
                lane1_models.add(mid)

    # Lane 2: companion_cheat_sheet.anchors[*].model_id
    lane2_models: set[str] = set()
    for a in (_RESULT.get("companion_cheat_sheet") or {}).get("anchors") or []:
        if a.get("model_id"):
            lane2_models.add(a["model_id"])

    # Lane 3: frame_pressure_card.reframings[*].grounding_model
    lane3_models: set[str] = set()
    for r in (_RESULT.get("frame_pressure_card") or {}).get("reframings") or []:
        gm = r.get("grounding_model")
        if gm:
            lane3_models.add(gm)

    rows = []
    for mid in excluded:
        sources = []
        if mid in lane1_models:
            sources.append("Lane 1")
        if mid in lane2_models:
            sources.append("Lane 2")
        if mid in lane3_models:
            sources.append("Lane 3")
        tag_html = (
            "".join(f"<span class='tag'>{s}</span>" for s in sources)
            if sources
            else "<span class='tag warn'>unattributed</span>"
        )
        rows.append(
            f"<tr><td>{_esc(mid)}</td><td><div class='tagrow'>{tag_html}</div></td></tr>"
        )

    lede = (
        f"<strong>{len(excluded)}</strong> models held back from Lane 4 because "
        "earlier lanes already surfaced them. Redundancy prevention, not defect."
    )

    body = f"""
<h1>Anti-echo cascade</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">Each row names a model the system removed from Lane 4's candidate pool because an upstream lane (1, 2, or 3) already surfaced it. The lane-of-origin tag is reconstructed at render time by intersecting <code>anti_echo_model_ids</code> against each upstream lane's surfaced models — no new telemetry needed.</p>

<table>
<tr><th>Excluded model</th><th>Source lane(s)</th></tr>
{"".join(rows)}
</table>
"""
    return _render_scaffold(title="Lolla — Anti-echo", body=body, current_path="/audit/anti-echo")


# ---------------- Panel: /audit/routing ----------------


_TIEBREAKER_ABORT_REASONS_HUMAN = {
    "fewer_than_2_candidates": "Fewer than 2 candidates — gate doesn't apply.",
    "fewer_than_2_after_dedup": "Fewer than 2 candidates after dedup — gate doesn't apply.",
    "outside_epsilon_window": "Outside near-tie window — affinity gap was decisive.",
    "matcher_exception": "Matcher raised an exception — gate aborted defensively.",
    "matcher_empty_result": "Matcher returned no activation match — fell back to top-1.",
    "below_noise_floor": "Both top-2 below the activation noise floor — fell back to top-1.",
    "no_improvement": "Activation match didn't favour top-2 — kept original top-1.",
}


def _render_tiebreaker_cell(trace: dict | None) -> str:
    if not trace:
        return "<span class='empty'>—</span>"
    if trace.get("fired"):
        return f"<span class='tag ok'>fired</span>"
    abort_reason = str(trace.get("abort_reason") or "")
    human = _TIEBREAKER_ABORT_REASONS_HUMAN.get(abort_reason, abort_reason or "—")
    return f"<span class='tag'>aborted</span> <small>{_esc(human)}</small>"


def _format_model_list(values) -> str:
    items = [str(value) for value in (values or []) if str(value or "").strip()]
    if not items:
        return "—"
    return ", ".join(f"<code>{_esc(item)}</code>" for item in items)


def _format_rejected_models(values, *, limit: int = 5) -> str:
    rows = []
    for item in list(values or [])[:limit]:
        if not isinstance(item, dict):
            continue
        model_id = item.get("model_id", "")
        reason = item.get("rejection_reason", "")
        stage = item.get("stage", "")
        label = f"{model_id}: {reason}" if reason else str(model_id)
        if stage:
            label = f"{label} ({stage})"
        rows.append(f"<div>{_esc(label)}</div>")
    remaining = max(len(values or []) - limit, 0)
    if remaining:
        rows.append(f"<div class='hint'>+{_esc(remaining)} more</div>")
    return "".join(rows) if rows else "—"


def _format_close_alternatives(values) -> str:
    rows = []
    for item in values or []:
        if not isinstance(item, dict):
            continue
        top1 = item.get("top1_model_id", "")
        top2 = item.get("top2_model_id", "")
        margin = item.get("margin", "")
        state = "fired" if item.get("tiebreaker_fired") else item.get("abort_reason", "")
        rows.append(
            f"<div>{_esc(item.get('candidate_type', ''))}: "
            f"{_esc(top1)} vs {_esc(top2)} "
            f"(margin {_esc(margin)}, {_esc(state)})</div>"
        )
    return "".join(rows) if rows else "—"


def _lane2_candidate_status(candidate: dict, lane2: dict) -> str:
    model_id = candidate.get("model_id", "")
    selected = set(lane2.get("selected_model_ids") or [])
    accepted = {
        item.get("model_id")
        for item in (lane2.get("accepted_before_cap") or [])
        if isinstance(item, dict)
    }
    rejected = [
        item
        for item in (lane2.get("rejected_candidates") or [])
        if isinstance(item, dict) and item.get("model_id") == model_id
    ]
    if model_id in selected:
        return "<span class='tag ok'>selected anchor</span>"
    if model_id in accepted:
        return "<span class='tag ok'>accepted before cap</span>"
    if rejected:
        return _format_rejected_models(rejected, limit=2)
    return "<span class='tag'>candidate only</span>"


def _render_routing_html() -> str:
    _reload_result_if_changed()
    audit = _audit_summary()
    trace = _route_trace()
    lanes = trace.get("lanes") or {}
    summary = trace.get("summary") or {}

    header = _render_run_header()

    if not audit and not any(int(v or 0) for v in summary.values()):
        body = (
            "<h1>Route trace — why this, why not that</h1>"
            f"{header}"
            + _empty_inline(
                "No route trace or audit summary exists in this result. Re-run "
                "the pipeline to persist routing diagnostics."
            )
        )
        return _render_scaffold(title="Lolla — Route Trace", body=body, current_path="/audit/routing")

    lane1 = lanes.get("lane1") or {}
    lane2 = lanes.get("lane2") or {}
    lane3 = lanes.get("lane3") or {}
    lane4 = lanes.get("lane4") or {}
    anti_echo = trace.get("anti_echo") or {}

    lane1_rows = []
    tiebreakers_fired = 0
    for route in lane1.get("routes") or []:
        close = route.get("close_alternatives") or []
        for alt in close:
            if alt.get("tiebreaker_fired"):
                tiebreakers_fired += 1
        selected = ", ".join(_esc(m) for m in (route.get("selected_model_ids") or []))
        antidotes = _format_model_list(route.get("antidote_model_ids") or [])
        rejected = _format_rejected_models(route.get("rejected_candidates") or [], limit=5)
        close_text = _format_close_alternatives(close)
        lane1_rows.append(
            f"<tr><td>{_esc(route.get('tendency_id', ''))}</td>"
            f"<td>{_esc(route.get('route_source', ''))}</td>"
            f"<td>{_esc(route.get('primary_model_id', ''))}</td>"
            f"<td>{selected or '—'}</td>"
            f"<td>{antidotes}</td>"
            f"<td>{close_text}</td>"
            f"<td>{rejected}</td></tr>"
        )

    lane2_rows = []
    for candidate in lane2.get("candidates") or []:
        lane2_rows.append(
            f"<tr><td>{_esc(candidate.get('model_id', ''))}</td>"
            f"<td>{_esc(candidate.get('recall_source', ''))}</td>"
            f"<td class='num'>{_esc(candidate.get('final_rank', ''))}</td>"
            f"<td>{_lane2_candidate_status(candidate, lane2)}</td></tr>"
        )
    if not lane2_rows:
        for rejected in lane2.get("rejected_candidates") or []:
            lane2_rows.append(
                f"<tr><td>{_esc(rejected.get('model_id', ''))}</td>"
                f"<td>—</td><td class='num'>—</td>"
                f"<td>{_format_rejected_models([rejected], limit=1)}</td></tr>"
            )

    lane3_rows = []
    for route in lane3.get("routes") or []:
        lane3_rows.append(
            f"<tr><td>{_esc(route.get('frame_pattern', ''))}</td>"
            f"<td>{_esc(route.get('element_text', ''))}</td>"
            f"<td>{_format_model_list(route.get('selected_model_ids') or [])}</td>"
            f"<td>{_format_model_list(route.get('candidate_model_ids') or [])}</td>"
            f"<td>{_format_rejected_models(route.get('rejected_candidates') or [], limit=5)}</td></tr>"
        )

    lane4_rows = []
    for route in lane4.get("routes") or []:
        lane4_rows.append(
            f"<tr><td>{_esc(route.get('dimension_id', ''))}</td>"
            f"<td>{_esc(route.get('dimension_name', ''))}</td>"
            f"<td>{_format_model_list(route.get('candidate_model_ids') or [])}</td>"
            f"<td>{_format_rejected_models(route.get('rejected_candidates') or [], limit=5)}</td></tr>"
        )

    anti_rows = []
    for exclusion in anti_echo.get("exclusions") or []:
        anti_rows.append(
            f"<tr><td>{_esc(exclusion.get('model_id', ''))}</td>"
            f"<td>{_esc(exclusion.get('excluded_from', ''))}</td>"
            f"<td>{_esc(exclusion.get('reason', ''))}</td>"
            f"<td>{_format_model_list(exclusion.get('source_lanes') or [])}</td></tr>"
        )

    lede = (
        f"Route trace version <code>{_esc(trace.get('schema_version', 'fallback'))}</code>: "
        f"<strong>{_esc(summary.get('lane1_route_count', 0))}</strong> Lane 1 routes, "
        f"<strong>{_esc(lane2.get('candidate_count', 0))}</strong> Lane 2 candidates, "
        f"<strong>{_esc(summary.get('lane3_route_count', 0))}</strong> Lane 3 frame routes, "
        f"<strong>{_esc(summary.get('lane4_route_count', 0))}</strong> Lane 4 gap routes, "
        f"and <strong>{_esc(summary.get('anti_echo_exclusion_count', 0))}</strong> anti-echo exclusions."
    )

    body = f"""
<h1>Route trace — why this, why not that</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">This page renders recorded route decisions. It does not infer missing reasons; when a lane did not record a reason, the table says so by omission.</p>

<h2>Lane 1 Route — tendency to corrective models</h2>
<p class="hint">Tendency bindings, selected corrective models, close alternatives from the activation tiebreaker, and relation-neighbor candidates dropped by budget, fan-adjusted ordering, or explicit route gates.</p>
<table>
<tr><th>Tendency</th><th>Route source</th><th>Primary model</th><th>Selected models</th><th>Antidotes</th><th>Close alternatives</th><th>Why-not candidates</th></tr>
{"".join(lane1_rows) if lane1_rows else "<tr><td colspan='7' class='empty'>No Lane 1 route trace on this run.</td></tr>"}
</table>

<h2>Lane 2 Route — companion detection and verification</h2>
<p class="hint">Candidates sent to verifier, accepted/rejected/capped outcomes, and silent omissions. Selected anchors: {_format_model_list(lane2.get('selected_model_ids') or [])}.</p>
<table>
<tr><th>Candidate model</th><th>Recall source</th><th class="num">Final rank</th><th>Verification path</th></tr>
{"".join(lane2_rows) if lane2_rows else "<tr><td colspan='4' class='empty'>No Lane 2 candidate trace on this run.</td></tr>"}
</table>

<h2>Lane 3 Route — frame patterns to models</h2>
<p class="hint">Frame elements route through the reframing table. Excluded rows are anti-echo against Lane 1 model overlap; unused candidates are candidates the returned reframing did not ground in.</p>
<table>
<tr><th>Frame pattern</th><th>Element</th><th>Grounding models</th><th>Candidates</th><th>Why-not candidates</th></tr>
{"".join(lane3_rows) if lane3_rows else "<tr><td colspan='5' class='empty'>No Lane 3 frame route trace on this run.</td></tr>"}
</table>

<h2>Lane 4 Route — dimensions to models</h2>
<p class="hint">Structural gaps route to corrective models after anti-echo exclusions from earlier lanes.</p>
<table>
<tr><th>Dimension</th><th>Name</th><th>Candidate models</th><th>Why-not candidates</th></tr>
{"".join(lane4_rows) if lane4_rows else "<tr><td colspan='4' class='empty'>No Lane 4 gap route trace on this run.</td></tr>"}
</table>

<h2>Anti-Echo / Why-Not</h2>
<p class="hint">Cross-lane exclusions. A model listed here was withheld from a later lane because an earlier lane already carried it.</p>
<table>
<tr><th>Model</th><th>Excluded from</th><th>Reason</th><th>Earlier source lanes</th></tr>
{"".join(anti_rows) if anti_rows else "<tr><td colspan='4' class='empty'>No cross-lane anti-echo exclusions recorded for this run.</td></tr>"}
</table>
"""
    return _render_scaffold(title="Lolla — Route Trace", body=body, current_path="/audit/routing")


# ---------------- Panel: /audit/treatment-audit ----------------


def _treatment_audit_dir() -> Path:
    return SKILL_DATA_DIR / "treatment_audits"


def _load_treatment_audit_summary() -> dict:
    path = _treatment_audit_dir() / "summary.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _load_treatment_audit(run_id: str) -> dict:
    safe_run_id = "".join(ch for ch in run_id if ch.isalnum() or ch in {"-", "_"})
    if safe_run_id != run_id:
        return {}
    path = _treatment_audit_dir() / f"{run_id}.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _render_treatment_audit_index_html() -> str:
    summary = _load_treatment_audit_summary()
    if not summary:
        body = (
            "<h1>Model Treatment Audit</h1>"
            + _empty_inline(
                "No treatment-audit summary exists in data/treatment_audits yet. "
                "Run scripts/run_model_treatment_audit.py to generate the Observatory-only prototype."
            )
        )
        return _render_scaffold(
            title="Lolla — Treatment Audit",
            body=body,
            current_path="/audit/treatment-audit",
        )

    rows = []
    for item in summary.get("new_findings") or []:
        rows.append(
            f"<tr><td><a href='/audit/treatment-audit/{_esc(item.get('run_id', ''))}'>{_esc(item.get('run_id', ''))}</a></td>"
            f"<td>{_esc(item.get('model_id', ''))}</td>"
            f"<td>{_esc(item.get('affordance_id', ''))}</td>"
            f"<td>{_esc(item.get('treatment_status', ''))}</td>"
            f"<td>{_esc(item.get('baseline_coverage', ''))}</td>"
            f"<td>{_esc(item.get('one_line_description', ''))}</td></tr>"
        )

    metadata = summary.get("metadata") or {}
    lede = (
        f"<strong>{_esc(summary.get('audited_run_count', 0))}</strong> runs, "
        f"<strong>{_esc(summary.get('audited_item_count', 0))}</strong> affordance audits, "
        f"<strong>{_esc(summary.get('new_finding_count', 0))}</strong> merge-gate candidate findings, "
        f"<strong>{_esc(summary.get('duplicate_of_existing_pressure_count', 0))}</strong> duplicates, "
        f"<strong>{_esc(summary.get('judge_rejection_count', 0))}</strong> judge-response rejections."
    )
    body = f"""
<h1>Model Treatment Audit</h1>
<p class="lede">{lede}</p>
<p class="hint">Judge: {_esc(metadata.get('judge_provider', ''))} / <code>{_esc(metadata.get('judge_model', ''))}</code>. This is Observatory-only; no chat, memo, lane, or runtime promotion is implied.</p>

<h2>Merge-Gate Candidate Findings</h2>
<table>
<tr><th>Run</th><th>Model</th><th>Affordance</th><th>Status</th><th>Baseline</th><th>One-line finding</th></tr>
{"".join(rows) if rows else "<tr><td colspan='6' class='empty'>No non-duplicative treatment-gap candidates in this run set.</td></tr>"}
</table>

<h2>Distributions</h2>
<table>
<tr><th>Bucket</th><th>Counts</th></tr>
<tr><td>Treatment status</td><td>{_esc(summary.get('treatment_status_distribution', {}))}</td></tr>
<tr><td>Baseline coverage</td><td>{_esc(summary.get('baseline_coverage_distribution', {}))}</td></tr>
<tr><td>Per model</td><td>{_esc(summary.get('per_model_audit_counts', {}))}</td></tr>
</table>
"""
    return _render_scaffold(
        title="Lolla — Treatment Audit",
        body=body,
        current_path="/audit/treatment-audit",
    )


def _render_treatment_audit_run_html(run_id: str) -> str:
    audit = _load_treatment_audit(run_id)
    if not audit:
        body = (
            "<h1>Model Treatment Audit</h1>"
            + _empty_inline(f"No treatment audit found for <code>{_esc(run_id)}</code>.")
        )
        return _render_scaffold(
            title="Lolla — Treatment Audit",
            body=body,
            current_path="/audit/treatment-audit",
        )

    metadata = audit.get("metadata") or {}
    rows = []
    for item in audit.get("items") or []:
        flag = (
            "<span class='tag warn'>do-not-promote</span>"
            if item.get("do_not_promote_without_rewrite_review")
            else ""
        )
        merge_candidate = (
            "<span class='tag ok'>merge-gate candidate</span>"
            if item.get("merge_gate_evidence_candidate")
            else ""
        )
        quote = item.get("output_quote") or ""
        rows.append(
            f"<tr><td>{_esc(item.get('model_id', ''))}<br><code>{_esc(item.get('affordance_id', ''))}</code><br>{flag} {merge_candidate}</td>"
            f"<td>{_esc(', '.join(item.get('selected_lanes') or []))}</td>"
            f"<td>{_esc(item.get('treatment_status', ''))}</td>"
            f"<td>{_esc(item.get('baseline_coverage', ''))}</td>"
            f"<td><blockquote class='quote'>{_esc(quote) if quote else '<span class=\"empty\">No quote required for this status.</span>'}</blockquote></td>"
            f"<td>{_esc(item.get('treatment_note', ''))}</td></tr>"
        )

    body = f"""
<h1>Model Treatment Audit — {_esc(audit.get('run_id', ''))}</h1>
<p class="meta">Source run: <code>{_esc(audit.get('source_run_ref', ''))}</code> · Judge: {_esc(metadata.get('judge_provider', ''))} / <code>{_esc(metadata.get('judge_model', ''))}</code> · Tokens: {_esc((metadata.get('token_usage') or {}).get('total_tokens', 0))}</p>
<p><a href="/audit/treatment-audit">Treatment audit summary</a> · <a href="/audit/routing">Route trace for the currently loaded Observatory result</a></p>

<h2>Per-Affordance Treatment</h2>
<table>
<tr><th>Affordance</th><th>Lanes</th><th>Status</th><th>Baseline</th><th>Quote</th><th>Note</th></tr>
{"".join(rows) if rows else "<tr><td colspan='6' class='empty'>No pilot affordances selected in this run.</td></tr>"}
</table>

<h2>Pressure Check Baseline</h2>
<pre>{_esc(audit.get('pressure_check_baseline', ''))}</pre>
"""
    return _render_scaffold(
        title="Lolla — Treatment Audit",
        body=body,
        current_path="/audit/treatment-audit",
    )


# ---------------- Panel: /audit/expansions ----------------


def _render_expansions_html() -> str:
    _reload_result_if_changed()
    expansions = (_RESULT.get("companion_card") or {}).get("expansions") or []

    header = _render_run_header()

    if not expansions:
        body = (
            "<h1>Companion expansions</h1>"
            f"{header}"
            + _empty_inline(
                "No companion expansions on this run — either Lane 2 stayed "
                "quiet or the surfaced anchors had no curated relations to "
                "traverse. See the <a href=\"/audit/lane2\">Lane 2 funnel</a> "
                "for the candidate picture."
            )
        )
        return _render_scaffold(title="Lolla — Expansions", body=body, current_path="/audit/expansions")

    by_anchor: dict[str, list[dict]] = {}
    for e in expansions:
        anchor = e.get("source_model_id") or "(unknown anchor)"
        by_anchor.setdefault(anchor, []).append(e)

    sections = []
    for anchor, entries in by_anchor.items():
        rows = []
        for e in entries:
            rows.append(
                f"<tr><td>{_esc(e.get('model_id', ''))}</td>"
                f"<td><span class='tag'>{_esc(e.get('relation_type', ''))}</span></td>"
                f"<td>{_esc(e.get('activation_condition', ''))}</td>"
                f"<td>{_esc(e.get('affinity_rationale', ''))}</td>"
                f"<td>{_esc(e.get('why_relevant', ''))}</td></tr>"
            )
        sections.append(
            f"<h3>From anchor: <code>{_esc(anchor)}</code> ({len(entries)} expansions)</h3>"
            f"<table><tr><th>Expanded model</th><th>Relation</th>"
            f"<th>Activation condition</th><th>Affinity rationale</th>"
            f"<th>Why relevant</th></tr>{''.join(rows)}</table>"
        )

    lede = (
        f"From <strong>{len(by_anchor)}</strong> anchors, the relation graph "
        f"traversed to <strong>{len(expansions)}</strong> expansions across "
        "allies, antagonists, and tensions."
    )

    body = f"""
<h1>Companion expansions</h1>
{header}
<p class="lede">{lede}</p>
<p class="hint">For each Lane 2 anchor, the system walks the curated relation graph one hop out — surfacing allies (mutually-reinforcing models), antagonists (corrective opposites), and tensions (sibling models that pull in different directions).</p>

{"".join(sections)}
"""
    return _render_scaffold(title="Lolla — Expansions", body=body, current_path="/audit/expansions")


def _render_stakeholder_html() -> str:
    """Render the optional Stakeholder Assumption Check panel."""
    _reload_result_if_changed()
    check = _RESULT.get("stakeholder_assumption_check") or {}
    header = _render_run_header()

    if not check or check.get("status") == "skipped":
        body = f"""
<h1>Stakeholder Assumption Check</h1>
{header}
{_empty_inline("No stakeholder assumption check was material for this run.")}
"""
        return _render_scaffold(
            title="Lolla — Stakeholder Assumptions",
            body=body,
            current_path="/audit/stakeholders",
        )

    status = check.get("status", "unknown")
    trigger_reason = check.get("trigger_reason", "")
    summary = check.get("summary", "")
    error = check.get("error", "")
    actors = [a for a in (check.get("critical_actors") or []) if isinstance(a, dict)]

    actor_rows = []
    for actor in actors:
        deps = actor.get("power_or_dependency") or []
        deps_html = " ".join(f'<span class="tag">{_esc(dep)}</span>' for dep in deps)
        surface_in_chat = bool(actor.get("surface_in_chat"))
        surface_label = "yes" if surface_in_chat else "no"
        surface_reason = actor.get("surface_block_reason") or (
            "available to chat" if surface_in_chat else "not selected for chat"
        )
        known = actor.get("known_to_actor") or []
        unknown = actor.get("unknown_to_actor") or []
        bridges = actor.get("bridging_facts") or []
        known_html = "<br>".join(_esc(item) for item in known) or "—"
        unknown_html = "<br>".join(_esc(item) for item in unknown) or "—"
        bridges_html = "<br>".join(_esc(item) for item in bridges) or "—"
        actor_rows.append(
            "<tr>"
            f"<td><strong>{_esc(actor.get('display_name') or actor.get('actor_id') or 'actor')}</strong>"
            f"<br><span class=\"hint\">{_esc(actor.get('role', ''))}</span>"
            f"<div class=\"tagrow\">{deps_html}</div></td>"
            f"<td>{_esc(actor.get('advice_assumption', ''))}</td>"
            f"<td><span class=\"tag\">{_esc(actor.get('grounding', 'unknown'))}</span></td>"
            f"<td><span class=\"tag\">{surface_label}</span><br>"
            f"<span class=\"hint\">{_esc(surface_reason)}</span></td>"
            f"<td>{_esc(actor.get('risk_if_wrong', ''))}</td>"
            f"<td>{_esc(actor.get('plan_change', ''))}</td>"
            "</tr>"
            "<tr>"
            "<td></td>"
            f"<td colspan=\"5\"><details><summary>Known / unknown / bridges</summary>"
            f"<p><strong>Known:</strong><br>{known_html}</p>"
            f"<p><strong>Unknown:</strong><br>{unknown_html}</p>"
            f"<p><strong>Bridging facts:</strong><br>{bridges_html}</p>"
            f"<p><strong>Open question:</strong> {_esc(actor.get('open_question', '—'))}</p>"
            "</details></td>"
            "</tr>"
        )

    if actor_rows:
        table = (
            "<table><thead><tr>"
            "<th>Actor</th><th>Advice assumption</th><th>Grounding</th>"
            "<th>Chat surface</th><th>Risk if wrong</th><th>Plan change</th>"
            "</tr></thead><tbody>"
            + "".join(actor_rows)
            + "</tbody></table>"
        )
    else:
        table = _empty_inline("The check ran but surfaced no actor-level plan change.")

    error_html = (
        f'<div class="empty">Checker error: <code>{_esc(error)}</code></div>'
        if status == "skipped_error" and error
        else ""
    )

    body = f"""
<h1>Stakeholder Assumption Check</h1>
{header}
<p class="lede">This panel shows where the advice depended on another actor's knowledge, cooperation, interpretation, or power. It is inspectable here; user-facing chat only gets a correction when it changes the plan.</p>
<div class="vitals">
  <span class="tag">status: {_esc(status)}</span>
  <span class="tag">surface: {_esc(check.get("surface", False))}</span>
  <span class="tag">triggered: {_esc(check.get("triggered", False))}</span>
</div>
{f'<p><strong>Trigger:</strong> {_esc(trigger_reason)}</p>' if trigger_reason else ''}
{f'<p><strong>Summary:</strong> {_esc(summary)}</p>' if summary else ''}
{error_html}
{table}
"""
    return _render_scaffold(
        title="Lolla — Stakeholder Assumptions",
        body=body,
        current_path="/audit/stakeholders",
    )


# ---------------- Index: /audit ----------------


def _render_audit_run_vitals() -> str:
    """Run-vitals strip for /audit index — at-a-glance pulse of this run.

    Pulls from audit_summary, structural_coverage_card, companion_cheat_sheet,
    and companion_card. Each tag is a single number with a label, in the
    panel order so operators can scan left-to-right and click into whichever
    catches their eye.
    """
    audit = _audit_summary()
    if not audit:
        return ""

    detected_count = sum(
        1 for d in (audit.get("deep_check_results") or []) if d.get("detected")
    )
    candidates_count = len(audit.get("companion_candidates") or [])
    anchors_count = len(
        (_RESULT.get("companion_cheat_sheet") or {}).get("anchors") or []
    )

    coverage = _RESULT.get("structural_coverage_card") or {}
    gaps_count = sum(
        1
        for d in (coverage.get("dimensions") or [])
        if d.get("dimension_id") and not d.get("covered")
    )
    anti_echo_count = len(coverage.get("anti_echo_model_ids") or [])
    expansions_count = len(
        (_RESULT.get("companion_card") or {}).get("expansions") or []
    )

    chips = [
        f"<strong>{detected_count}</strong> detected",
        f"<strong>{candidates_count}</strong> candidates → "
        f"<strong>{anchors_count}</strong> anchors",
        f"<strong>{gaps_count}</strong> dimension gaps",
        f"<strong>{anti_echo_count}</strong> anti-echo exclusions",
        f"<strong>{expansions_count}</strong> expansions",
    ]
    chip_html = "".join(f'<span class="tag">{c}</span>' for c in chips)
    return f'<div class="vitals">{chip_html}</div>'


def _render_audit_index_html() -> str:
    _reload_result_if_changed()
    audit_present = bool(_audit_summary())
    items = [
        ("/audit/lane1", "Lane 1 — Pass 1 + Pass 2 funnel",
         "Triage scores across the catalog, the threshold, the triggered set with source attribution, and Pass 2 outcomes with rationale."),
        ("/audit/lane2", "Lane 2 — Companion selection funnel",
         "Candidate pool → accepted-before-cap → final cheat-sheet anchors, with verifier accepts/rejects/capped/duplicates/quote-repairs/silently-omitted bucket views."),
        ("/audit/lane4", "Lane 4 — Dimension coverage",
         "Every catalog dimension marked covered / gap / not-detected, with gap routes (corrective models) and gap questions."),
        ("/audit/anti-echo", "Anti-echo cascade",
         "Models held back from Lane 4 because an upstream lane already surfaced them. Lane-of-origin attribution computed at render time."),
        ("/audit/routing", "Routing decisions",
         "For each detected tendency: primary lens, antidotes, and the activation-tiebreaker trace (fired, or which clause kept top-1)."),
        ("/audit/treatment-audit", "Model treatment audit",
         "Observatory-only affordance treatment checks: did selected models change the output, or merely get named?"),
        ("/audit/expansions", "Companion expansions",
         "Relation-graph traversal per Lane 2 anchor — allies, antagonists, and tensions, with activation conditions and why-relevant rationale."),
        ("/audit/stakeholders", "Stakeholder assumption check",
         "When enabled: actor dependencies, grounding tiers, known/unknown splits, and any plan-changing correction."),
    ]
    cards = []
    for href, title, desc in items:
        cards.append(
            f'<li><a href="{_esc(href)}"><strong>{_esc(title)}</strong></a><br>'
            f'<span style="color:#555">{_esc(desc)}</span></li>'
        )
    header = _render_run_header()
    vitals = _render_audit_run_vitals() if audit_present else ""

    if not audit_present:
        notice = (
            '<div class="empty">This result has no <code>audit_summary</code> '
            "block — likely a pre-Phase-7 artifact. Panels render their "
            "empty states; re-run the pipeline to populate the trace.</div>"
        )
    else:
        notice = ""
    body = f"""
<h1>Telemetry — how the system reasoned</h1>
{header}
<p class="lede">A separate lens on the same case. Each panel below shows what the system observed, considered, and surfaced — the reasoning trace behind the answer at <a href="/">/</a>.</p>
{vitals}
{notice}
<ul style="list-style:none;padding:0;">
{"".join(f'<div style="margin-bottom:1.5rem">{c}</div>' for c in cards)}
</ul>
"""
    return _render_scaffold(title="Lolla — Telemetry", body=body, current_path="/audit")


class ResultHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Pass STATIC_DIR even if it doesn't exist — SimpleHTTPRequestHandler
        # accepts a non-existent directory string. The /audit/* and /usage
        # routes do not depend on the SPA bundle being present (skill
        # portability — see PR 3 of the 2026-04-28 visibility roadmap); only
        # the SPA fallback path checks ``STATIC_DIR.is_dir()`` before serving.
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            _reload_result_if_changed()

        if path == "/api/cases":
            finding_count = len(_RESULT.get("detected_tendencies", []))
            self._json_response([{
                "id": _CASE_ID,
                "name": _CASE_NAME,
                "has_delta_card": finding_count > 0,
                "has_companion": bool(_RESULT.get("companion_cheat_sheet")),
                "has_audit_trace": bool(_RESULT.get("audit_summary")),
                "finding_count": finding_count,
            }])
            return

        if path.startswith("/api/case/"):
            parts = path.split("/")
            if len(parts) == 4:
                self._json_response(_build_case_response())
                return
            if len(parts) == 5 and parts[4] == "audit_trace":
                self._json_response(_RESULT.get("audit_summary") or {})
                return
            if len(parts) == 5 and parts[4] == "graph":
                self._json_response(_build_graph_response())
                return
            if len(parts) == 5 and parts[4] == "usage":
                self._json_response(_RESULT.get("usage_summary") or {})
                return

        if path == "/usage":
            self._html_response(_render_usage_html())
            return

        # Audit panels — server-rendered HTML, no SPA dependency.
        _audit_routes = {
            "/audit": _render_audit_index_html,
            "/audit/lane1": _render_lane1_html,
            "/audit/lane2": _render_lane2_html,
            "/audit/lane4": _render_lane4_html,
            "/audit/anti-echo": _render_anti_echo_html,
            "/audit/routing": _render_routing_html,
            "/audit/treatment-audit": _render_treatment_audit_index_html,
            "/audit/expansions": _render_expansions_html,
            "/audit/stakeholders": _render_stakeholder_html,
        }
        if path in _audit_routes:
            self._html_response(_audit_routes[path]())
            return

        if path.startswith("/audit/treatment-audit/"):
            run_id = path.rsplit("/", 1)[-1]
            self._html_response(_render_treatment_audit_run_html(run_id))
            return

        if path.startswith("/api/model/"):
            model_id = path.split("/")[3] if len(path.split("/")) >= 4 else ""
            data = _get_model_detail(model_id)
            if data is None:
                self._error_response(404, f"Model '{model_id}' not found")
                return
            self._json_response(data)
            return

        if path == "/api/kg/stats":
            self._json_response(_get_kg_stats())
            return

        if path == "/api/tendencies":
            self._json_response(_get_tendency_catalog())
            return

        if path == "/api/families":
            self._json_response(_load_families())
            return

        if path.startswith("/api/family/"):
            parts = path.split("/")
            if len(parts) >= 4:
                fid = parts[3]
                data = _get_family_detail(fid)
                if data is None:
                    self._error_response(404, f"Family '{fid}' not found")
                    return
                self._json_response(data)
                return

        # SPA root — inject the Telemetry FAB before serving index.html.
        # This is the only bridge from the case/product surface (/) to the
        # system-reasoning surface (/audit). Done as a byte-stream injection
        # so the SPA bundle on disk stays untouched and the skill remains
        # rebuildable-free.
        if path in ("/", "/index.html") and STATIC_DIR.is_dir():
            index_path = STATIC_DIR / "index.html"
            if index_path.is_file():
                try:
                    injected = _inject_telemetry_fab(index_path.read_bytes())
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(injected)))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(injected)
                    return
                except OSError:
                    pass  # fall through to default handler below

        # Static files / SPA fallback
        if STATIC_DIR.is_dir():
            file_path = STATIC_DIR / path.lstrip("/")
            if not file_path.exists() and not path.startswith("/api/"):
                self.path = "/index.html"
            super().do_GET()
        else:
            self._error_response(503, "Observatory frontend not built.")

    def _html_response(self, body_str: str, status: int = 200):
        body = body_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _json_response(self, data, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _error_response(self, status: int, message: str):
        self._json_response({"error": message}, status=status)

    def log_message(self, format, *args):
        msg = format % args
        if "/api/" in msg or "404" in msg or "500" in msg:
            sys.stderr.write(f"[lolla] {msg}\n")


def main():
    parser = argparse.ArgumentParser(description="Serve Lolla result in Observatory")
    parser.add_argument("--result", required=True, help="Path to pipeline result JSON")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument("--name", help="Display name for the case (auto-derived from query if omitted)")
    args = parser.parse_args()

    global _RESULT, _RESULT_PATH, _RESULT_MTIME, _CASE_NAME
    result_path = Path(args.result)
    if not result_path.exists():
        print(f"Error: result file not found: {result_path}", file=sys.stderr)
        sys.exit(1)

    _RESULT_PATH = result_path
    with open(result_path) as f:
        _RESULT = json.load(f)
    _RESULT_MTIME = result_path.stat().st_mtime

    _CASE_NAME = args.name if args.name else _derive_case_name(_RESULT)

    # SPA bundle is optional (skill portability): /audit/* and /usage are
    # server-rendered HTML and work without it. Only warn when the bundle is
    # absent so the operator knows the React app at /  won't render.
    if not STATIC_DIR.is_dir():
        print(
            f"Note: Observatory SPA bundle not found at {STATIC_DIR} — "
            "the React app at / will be unavailable, but /audit/* and /usage "
            "panels still work.",
            file=sys.stderr,
        )

    # Try ports starting from the requested one
    port = args.port
    server = None
    for attempt in range(10):
        try:
            server = HTTPServer(("", port), ResultHandler)
            break
        except OSError:
            print(f"Port {port} in use, trying {port + 1}...")
            port += 1

    if server is None:
        print(f"Error: could not find an open port (tried {args.port}-{port})", file=sys.stderr)
        sys.exit(1)

    print(f"Lolla Observatory at http://localhost:{port}")
    print(f"  Case:  {_CASE_NAME}")
    print(f"  Usage: http://localhost:{port}/usage  (per-run cost & call breakdown)")
    print(f"  Result: {result_path}")
    print(f"  Knowledge graph: {SKILL_DATA_DIR / 'knowledge_graph.json'}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
