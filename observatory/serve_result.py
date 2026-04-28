"""Serve a single Lolla pipeline result in the Observatory frontend.

Zero-dependency Python server (stdlib http.server). Takes a pipeline
result JSON file and serves it through the Observatory Svelte app.

Usage:
    python3 observatory/serve_result.py --result /tmp/lolla_result.json
    python3 observatory/serve_result.py --result /tmp/lolla_result.json --port 9000
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
FAMILY_DIR = SKILL_DATA_DIR / "family_semantics"

# Loaded at startup, re-read on each request to pick up late writes (e.g. Step 6b)
_RESULT: dict = {}
_RESULT_PATH: Path | None = None
_RESULT_MTIME: float = 0.0
_CASE_ID: str = "lolla-audit"
_CASE_NAME: str = "Lolla Audit"
_KG_CACHE: dict | None = None
_FAMILY_CACHE: list[dict] | None = None


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
    # finding) and for diffing two runs of the same case.
    prompt_versions = r.get("prompt_versions")
    if prompt_versions:
        response["prompt_versions"] = prompt_versions

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
        return (
            "<!doctype html><html><body style='font-family:system-ui;padding:2rem'>"
            "<h1>Usage Summary</h1>"
            "<p>No <code>usage_summary</code> in this result. "
            "Re-run the pipeline with the updated <code>run_pipeline.py</code> "
            "to populate it.</p></body></html>"
        )
    vendors = us.get("vendors", {}) or {}

    def _fmt_usd(x):
        try:
            return f"${float(x):.4f}"
        except (TypeError, ValueError):
            return "—"

    def _fmt_int(x):
        try:
            return f"{int(x):,}"
        except (TypeError, ValueError):
            return "—"

    def _esc(x) -> str:
        """HTML-escape any value before interpolation to prevent injection
        from a crafted result.json. Numeric-formatted helpers above already
        produce safe output; everything else flows through this."""
        return html.escape(str(x), quote=True)

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
        pv_rows.append(
            f"<tr><td>{_esc(stage)}</td><td><code>{_esc(ver_hash)}</code></td></tr>"
        )

    notes_html = "".join(f"<li>{_esc(n)}</li>" for n in (us.get("notes") or []))

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Lolla — Usage Summary</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 980px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
h1 {{ margin: 0 0 0.5rem; }}
.meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }}
.total {{ font-size: 1.6rem; font-weight: 600; margin: 1rem 0 1.5rem; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; font-size: 0.95rem; }}
th, td {{ text-align: left; padding: 0.5rem 0.75rem; border-bottom: 1px solid #eee; }}
th {{ background: #f6f6f6; font-weight: 600; }}
td:nth-child(n+2) {{ font-variant-numeric: tabular-nums; }}
h2 {{ margin-top: 2rem; }}
.notes {{ background: #fafafa; border-left: 3px solid #ccc; padding: 0.5rem 1rem; font-size: 0.9rem; }}
.notes li {{ margin: 0.4rem 0; }}
code {{ background: #f0f0f0; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.9em; }}
.hint {{ color: #666; font-size: 0.85rem; margin-top: -1.5rem; margin-bottom: 1rem; }}
</style></head><body>
<h1>Usage Summary</h1>
<div class="meta">
  Run: <code>{_esc(us.get("run_id", "—"))}</code> ·
  Pricing table verified: <code>{_esc(us.get("pricing_table_version", "—"))}</code> ·
  <a href="/">back to Observatory</a>
</div>
<div class="total">Total estimated cost: <strong>{_fmt_usd(us.get("estimated_total_cost_usd"))}</strong></div>

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
<ul class="notes">{notes_html}</ul>
</body></html>
"""


class ResultHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
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
            body = _render_usage_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
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

        # Static files / SPA fallback
        if STATIC_DIR.is_dir():
            file_path = STATIC_DIR / path.lstrip("/")
            if not file_path.exists() and not path.startswith("/api/"):
                self.path = "/index.html"
            super().do_GET()
        else:
            self._error_response(503, "Observatory frontend not built.")

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

    if not STATIC_DIR.is_dir():
        print(f"Error: Observatory build not found at {STATIC_DIR}", file=sys.stderr)
        print("Expected: observatory/build/index.html", file=sys.stderr)
        sys.exit(1)

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
