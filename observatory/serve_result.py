"""Serve a single Lolla pipeline result in the Observatory frontend.

Zero-dependency Python server (stdlib http.server). Takes a pipeline
result JSON file and serves it through the Observatory Svelte app.

Usage:
    python3 observatory/serve_result.py --result /tmp/lolla_result.json
    python3 observatory/serve_result.py --result /tmp/lolla_result.json --port 9000
"""
from __future__ import annotations

import argparse
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


def _derive_case_name(result: dict) -> str:
    """Derive a human-readable case name from the pipeline result."""
    query = result.get("query", "")
    if not query:
        return "Lolla Audit"
    # Take first line
    first_line = query.split("\n")[0].strip()
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

    # Build case metadata from extraction if available
    extraction = r.get("extraction", {})
    case_meta = {
        "case_id": _CASE_ID,
        "query": r.get("query", extraction.get("query", "")),
        "vanilla_answer": r.get("vanilla_answer", extraction.get("vanilla_answer", "")),
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

    return response


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
    print(f"  Case: {_CASE_NAME}")
    print(f"  Result: {result_path}")
    print(f"  Knowledge graph: {SKILL_DATA_DIR / 'knowledge_graph.json'}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
