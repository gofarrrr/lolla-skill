#!/usr/bin/env python3
"""
Stability harness for the Lolla pipeline.

Diagnostic, not gate. Measures per-stage stability (Jaccard over set-valued
outputs) across N runs of the same conversation. Two modes:

- Aggregate: given a set of existing result.json paths, compute stability.
- Rerun: given one extraction.json and conversation.txt, invoke
  run_pipeline.py --skip-revision N times through the default ConversationContext
  path, then aggregate the new result.json files. Pass --legacy-contract for an
  intentional CritiqueRequest rerun.

Design principles (from research/llm-decomposition-handover.md §3.6, §5c):
  * 1.0 Jaccard is a warning, not a target — signals a specialist that
    stopped doing semantic judgment.
  * Threshold band, not threshold line. Report; don't fail.
  * Holds extraction constant in rerun mode so pipeline variance is
    isolated from extraction variance.

Output: research/stability-runs/{case-id}-{date}/
  stability.json   — machine-readable per-stage metrics
  variance.md      — human-readable per-run diff
  runs.txt         — run_ids contributing to this report
  config.json      — prompt versions + skill paths in effect

Usage:
  # Mode A (aggregate existing runs — cheapest, highest-signal first):
  python3 scripts/stability_check.py \
      --case-id marcus-baseline \
      --runs /tmp/lolla_2026*_result.json

  # Mode B (rerun pipeline N times from one extraction):
  python3 scripts/stability_check.py \
      --case-id marcus-pipeline-variance \
      --extraction /tmp/lolla_XXX_extraction.json \
      --conversation /tmp/lolla_XXX_conversation.txt \
      -n 3

  # Mode B legacy compatibility rerun:
  python3 scripts/stability_check.py \
      --case-id marcus-pipeline-variance-legacy \
      --extraction /tmp/lolla_XXX_extraction.json \
      --legacy-contract \
      -n 3

  # Mode C (extraction-drift — re-run run_extract.py N times on same
  # conversation; measures which of the 6 extraction fields drift):
  python3 scripts/stability_check.py \
      --case-id marcus-extraction-drift \
      --drift \
      --conversation /tmp/lolla_XXX_conversation.txt \
      -n 3
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
import time
from itertools import combinations
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Embedding infrastructure (PR #1b — canonical_key semantic metric)
# ---------------------------------------------------------------------------
#
# Uses OpenAI `text-embedding-3-small` via the `openai` Python client.
# Chosen over local sentence-transformers because: (a) openai client already
# installed + configured, (b) OPENAI_API_KEY already in .env, (c) cost is
# negligible (~$0.00005 per slug; 50 slugs per full cross-capture run = ~$0.003).
# Embeddings are cached in-process to avoid duplicate API calls when the same
# slug appears multiple times.

_EMBED_MODEL = "text-embedding-3-small"
_EMBED_CACHE: dict[str, "list[float]"] = {}
_OPENAI_CLIENT = None


def _get_openai_client():
    """Lazy-init OpenAI client. Reads OPENAI_API_KEY from env. Loads .env if
    present so callers don't have to remember to source it."""
    global _OPENAI_CLIENT
    if _OPENAI_CLIENT is not None:
        return _OPENAI_CLIENT
    import os
    # Load .env best-effort (matches run_extract.py's pattern)
    env_path = SKILL_DIR / ".env"
    if env_path.exists() and not os.environ.get("OPENAI_API_KEY"):
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in {"'", '"'}:
                v = v[1:-1]
            if k not in os.environ:
                os.environ[k] = v
    from openai import OpenAI
    _OPENAI_CLIENT = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))
    return _OPENAI_CLIENT


def _get_embedding(text: str):
    """Fetch embedding vector for ``text`` with in-process cache.
    Returns a numpy array of floats. Raises on API failure (caller decides
    whether to retry or fall back)."""
    import numpy as np
    if text in _EMBED_CACHE:
        return np.asarray(_EMBED_CACHE[text], dtype=np.float32)
    client = _get_openai_client()
    resp = client.embeddings.create(model=_EMBED_MODEL, input=text)
    vec = resp.data[0].embedding
    _EMBED_CACHE[text] = vec
    return np.asarray(vec, dtype=np.float32)


def _cosine_similarity(a, b) -> float:
    """Cosine similarity between two vectors. Pure function.

    Returns value in [-1, 1]. Undefined (returns 0.0) for zero vectors."""
    import numpy as np
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _best_match_mean_cosine(vecs_a, vecs_b):
    """Given two lists of vectors, compute the best-match mean cosine.

    For each vector in the shorter list, find its highest-cosine partner in
    the other list (greedy matching; no partner re-use across items from the
    shorter list is not enforced — matching is independent per item, which
    gives a *most-generous* similarity and avoids complex bipartite solvers).
    Denominator = max(len_a, len_b), so unmatched items in the longer list
    drag the mean toward 0.

    Returns None when both lists are empty (undefined; caller distinguishes
    from zero). Returns 0.0 when one side is empty (no agreement possible).
    """
    if not vecs_a and not vecs_b:
        return None
    if not vecs_a or not vecs_b:
        return 0.0
    short, long_ = (vecs_a, vecs_b) if len(vecs_a) <= len(vecs_b) else (vecs_b, vecs_a)
    best_scores = []
    for s in short:
        best = max(_cosine_similarity(s, l) for l in long_)
        best_scores.append(best)
    # Penalize unmatched items in the longer list by counting them as 0.
    total = sum(best_scores)
    denom = max(len(vecs_a), len(vecs_b))
    return round(total / denom, 4)


# ---------------------------------------------------------------------------
# Result-JSON field extractors
# ---------------------------------------------------------------------------

def _load_result(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def _run_id_from_path(path: Path) -> str:
    m = re.match(r"lolla_(\d{8}T\d{6}Z\w*)_result\.json$", path.name)
    return m.group(1) if m else path.stem


def _tendency_set(d: dict) -> set[str]:
    """Pass 1 — the full union of detected tendencies (triage + embedding)."""
    items = d.get("detected_tendencies", []) or []
    out: set[str] = set()
    for t in items:
        if isinstance(t, str):
            out.add(t)
        elif isinstance(t, dict):
            tid = t.get("tendency_id") or t.get("id") or t.get("name") or ""
            if tid:
                out.add(tid)
    return out


def _anchor_set(d: dict) -> set[str]:
    """Lane 2 — cheat-sheet anchor model_ids."""
    cc = d.get("companion_cheat_sheet", {}) or {}
    anchors = cc.get("anchors", []) or []
    return {a.get("model_id", "") for a in anchors if a.get("model_id")}


def _anchor_display_names(d: dict) -> list[str]:
    cc = d.get("companion_cheat_sheet", {}) or {}
    return [a.get("display_name", "") for a in (cc.get("anchors", []) or []) if a.get("display_name")]


def _reframing_set(d: dict) -> set[str]:
    """Lane 3 — reframing grounding_model ids."""
    fp = d.get("frame_pressure_card", {}) or {}
    out: set[str] = set()
    for r in (fp.get("reframings", []) or []):
        mid = r.get("grounding_model") or r.get("model_id") or ""
        if mid:
            out.add(mid)
    return out


def _gap_dimension_set(d: dict) -> set[str]:
    """Lane 4 — uncovered dimension_ids (the actual gaps)."""
    sc = d.get("structural_coverage_card", {}) or {}
    dims = sc.get("dimensions", []) or []
    return {x.get("dimension_id", "") for x in dims
            if not x.get("covered") and x.get("dimension_id")}


def _step6_anchor_mentions(d: dict) -> dict:
    """Step 6 anchor-naming rate — relies on revised_answer being persisted."""
    revised = d.get("revised_answer", "") or ""
    names = _anchor_display_names(d)
    if not revised:
        return {"present": False, "per_anchor": [], "named": 0,
                "total": len(names), "rate": 0.0}
    lower = revised.lower()
    per_anchor = []
    for n in names:
        hit = n.lower() in lower
        per_anchor.append({"display_name": n, "named": hit})
    named = sum(1 for a in per_anchor if a["named"])
    total = len(names)
    return {
        "present": True,
        "per_anchor": per_anchor,
        "named": named,
        "total": total,
        "rate": (named / total) if total else 0.0,
    }


def _cost_and_timing(d: dict) -> dict:
    """Sum per-call tokens from audit_summary.boundary_calls."""
    summ = d.get("audit_summary", {}) or {}
    calls = summ.get("boundary_calls", []) or []
    prompt_tokens = sum((c.get("prompt_tokens") or 0) for c in calls)
    completion_tokens = sum((c.get("completion_tokens") or 0) for c in calls)
    total_tokens = sum((c.get("total_tokens") or 0) for c in calls)
    return {
        "n_boundary_calls": len(calls),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


# ---------------------------------------------------------------------------
# Stability math
# ---------------------------------------------------------------------------

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def pairwise_stability(sets: list[set]) -> dict:
    if len(sets) < 2:
        return {"mean": None, "min": None, "max": None, "pairs": []}
    pairs = []
    for i, j in combinations(range(len(sets)), 2):
        pairs.append({
            "i": i, "j": j,
            "jaccard": round(jaccard(sets[i], sets[j]), 4),
            "shared": sorted(sets[i] & sets[j]),
            "only_i": sorted(sets[i] - sets[j]),
            "only_j": sorted(sets[j] - sets[i]),
        })
    vals = [p["jaccard"] for p in pairs]
    return {
        "mean": round(sum(vals) / len(vals), 4),
        "min": round(min(vals), 4),
        "max": round(max(vals), 4),
        "pairs": pairs,
    }


def compute_stability(results: list[tuple[str, dict]]) -> dict:
    tendency_sets = [_tendency_set(r) for _, r in results]
    anchor_sets = [_anchor_set(r) for _, r in results]
    reframing_sets = [_reframing_set(r) for _, r in results]
    gap_sets = [_gap_dimension_set(r) for _, r in results]
    return {
        "n_runs": len(results),
        "run_ids": [rid for rid, _ in results],
        "pass1_tendencies": {
            "per_run": [sorted(s) for s in tendency_sets],
            "stability": pairwise_stability(tendency_sets),
        },
        "lane2_anchors": {
            "per_run": [sorted(s) for s in anchor_sets],
            "stability": pairwise_stability(anchor_sets),
        },
        "lane3_reframings": {
            "per_run": [sorted(s) for s in reframing_sets],
            "stability": pairwise_stability(reframing_sets),
        },
        "lane4_gaps": {
            "per_run": [sorted(s) for s in gap_sets],
            "stability": pairwise_stability(gap_sets),
        },
        "step6_anchor_mentions": [
            {"run_id": rid, **_step6_anchor_mentions(r)}
            for rid, r in results
        ],
        "cost_per_run": [
            {"run_id": rid, **_cost_and_timing(r)}
            for rid, r in results
        ],
    }


def prompt_versions_across(results: list[tuple[str, dict]]) -> dict:
    per_run = {rid: (r.get("prompt_versions") or {}) for rid, r in results}
    unique = {json.dumps(pv, sort_keys=True) for pv in per_run.values()}
    return {"per_run": per_run, "all_agree": len(unique) == 1}


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _fmt(v, digits=2) -> str:
    return "—" if v is None else (f"{v:.{digits}f}" if isinstance(v, float) else str(v))


def render_markdown(stability: dict, prompt_cfg: dict, case_id: str,
                    generated_at: str) -> str:
    out: list[str] = []
    out.append(f"# Stability report — {case_id}")
    out.append("")
    out.append(f"Generated: {generated_at}")
    out.append(f"Runs: {stability['n_runs']}")
    out.append(f"Run IDs: {', '.join(stability['run_ids'])}")
    out.append(f"Prompt versions consistent across runs: {prompt_cfg.get('all_agree')}")
    out.append("")
    out.append("## Per-stage stability (Jaccard)")
    out.append("")
    out.append("> 1.0 is a WARNING, not a target — signals a specialist that stopped doing semantic judgment. "
               "Acceptance is a threshold band: stability moved up from baseline, no neighboring stage regressed, "
               "qualitative review confirms cards still do structural work.")
    out.append("")
    out.append("| Stage | Mean | Min | Max |")
    out.append("|---|---|---|---|")
    for label, key in [
        ("Pass 1 (tendencies)", "pass1_tendencies"),
        ("Lane 2 (anchors)",    "lane2_anchors"),
        ("Lane 3 (reframings)", "lane3_reframings"),
        ("Lane 4 (gap dims)",   "lane4_gaps"),
    ]:
        st = stability[key]["stability"]
        out.append(f"| {label} | {_fmt(st['mean'])} | {_fmt(st['min'])} | {_fmt(st['max'])} |")
    out.append("")
    # Step 6 table
    out.append("## Step 6 anchor naming (per-run)")
    out.append("")
    out.append("| Run | Named | Total | Rate |")
    out.append("|---|---|---|---|")
    total_n = 0; total_t = 0
    for s in stability["step6_anchor_mentions"]:
        if not s["present"]:
            out.append(f"| `{s['run_id']}` | (no revised_answer) | — | — |")
        else:
            rate = f"{100*s['rate']:.0f}%"
            out.append(f"| `{s['run_id']}` | {s['named']} | {s['total']} | {rate} |")
            total_n += s["named"]; total_t += s["total"]
    if total_t:
        out.append(f"| **AGGREGATE** | **{total_n}** | **{total_t}** | **{100*total_n//total_t}%** |")
    out.append("")
    # Per-run diff per stage
    out.append("## Per-run item diff")
    out.append("")
    for label, key in [
        ("Pass 1 tendencies", "pass1_tendencies"),
        ("Lane 2 anchors",    "lane2_anchors"),
        ("Lane 3 reframings", "lane3_reframings"),
        ("Lane 4 gap dims",   "lane4_gaps"),
    ]:
        out.append(f"### {label}")
        for rid, items in zip(stability["run_ids"], stability[key]["per_run"]):
            out.append(f"- `{rid}`: {items if items else '[]'}")
        out.append("")
    # Cost / tokens table
    out.append("## Cost per run (boundary-call tokens)")
    out.append("")
    out.append("| Run | Calls | Prompt tok | Completion tok | Total tok |")
    out.append("|---|---|---|---|---|")
    for c in stability["cost_per_run"]:
        out.append(f"| `{c['run_id']}` | {c['n_boundary_calls']} | "
                   f"{c['prompt_tokens']} | {c['completion_tokens']} | {c['total_tokens']} |")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Rerun driver
# ---------------------------------------------------------------------------

def _rerun_pipeline(
    extraction: Path,
    conversation: Path | None,
    n: int,
    skill_dir: Path,
    *,
    legacy_contract: bool = False,
) -> list[Path]:
    paths: list[Path] = []
    for i in range(n):
        # Spacing-safe run id so parallel/rapid runs don't collide.
        rid = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + f"stab{i}"
        result_path = Path(f"/tmp/lolla_{rid}_result.json")
        cmd = [
            "python3", str(skill_dir / "scripts" / "run_pipeline.py"),
            "--extraction-file", str(extraction),
            "--output-file", str(result_path),
            "--skip-revision",
        ]
        if conversation:
            cmd.extend(["--conversation-file", str(conversation)])
        if legacy_contract:
            cmd.append("--legacy-contract")
        print(f"  [{i+1}/{n}] rid={rid}", file=sys.stderr)
        subprocess.run(cmd, check=True, cwd=str(skill_dir))
        paths.append(result_path)
        time.sleep(1)
    return paths


# ---------------------------------------------------------------------------
# Mode C — extraction drift (re-extract N times from same conversation)
# ---------------------------------------------------------------------------

def _text_similarity(a: str, b: str) -> float:
    """difflib SequenceMatcher ratio — 0.0 = nothing in common, 1.0 = identical.

    Character-level, not semantic. Suitable for detecting paraphrase-level
    drift in free-text extraction fields.
    """
    from difflib import SequenceMatcher
    return SequenceMatcher(None, (a or "").strip(), (b or "").strip()).ratio()


def _list_jaccard_keyed(a: list, b: list, key) -> float:
    """Jaccard on list items after applying key() to each item (typically
    a text-normalizer like `lambda c: c['text'].strip().lower()`)."""
    sa = {key(x) for x in a if key(x)}
    sb = {key(x) for x in b if key(x)}
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _list_jaccard_keyed_nonempty(a: list, b: list, key) -> float | None:
    """Jaccard on list items after applying key(), EXCLUDING empty-string values
    from both sets before intersection. Returns None if both filtered sets are
    empty (undefined — caller should interpret as "no valid data").

    This variant is for canonical_key-style metrics where an empty string means
    "LLM failed the format rule" and two empty strings in different runs MUST
    NOT count as a trivial match. Reports the "why" via a separate
    invalid_key_rate metric, not via an inflated Jaccard.
    """
    sa = {k for x in a if (k := key(x))}
    sb = {k for x in b if (k := key(x))}
    if not sa and not sb:
        return None
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _rerun_extractions(conversation: Path, n: int, skill_dir: Path) -> list[Path]:
    """Invoke run_extract.py N times on the same conversation.txt. Holds
    conversation constant so only extractor sampling contributes to drift."""
    paths: list[Path] = []
    for i in range(n):
        rid = _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + f"drift{i}"
        extraction_path = Path(f"/tmp/lolla_{rid}_extraction.json")
        cmd = [
            "python3", str(skill_dir / "scripts" / "run_extract.py"),
            "--conversation-file", str(conversation),
            "--output-file", str(extraction_path),
        ]
        print(f"  [{i+1}/{n}] rid={rid}", file=sys.stderr)
        subprocess.run(cmd, check=True, cwd=str(skill_dir))
        paths.append(extraction_path)
        time.sleep(1)
    return paths


def _run_id_from_extraction_path(path: Path) -> str:
    m = re.match(r"lolla_(\d{8}T\d{6}Z\w*)_extraction\.json$", path.name)
    return m.group(1) if m else path.stem


def _load_extraction(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def compute_extraction_drift(extractions: list[tuple[str, dict]]) -> dict:
    """Given N extraction payloads, compute per-field drift metrics across
    every pair of runs."""
    if len(extractions) < 2:
        return {"n_runs": len(extractions),
                "run_ids": [rid for rid, _ in extractions],
                "pairs": [], "aggregate": {}}

    from itertools import combinations as _comb

    pairs = []
    for (a_idx, a), (b_idx, b) in _comb(enumerate(extractions), 2):
        rid_a, ea = a
        rid_b, eb = b
        xa = ea.get("extraction", {}) or {}
        xb = eb.get("extraction", {}) or {}

        pair = {"a": rid_a, "b": rid_b}
        # Free-text fields — SequenceMatcher ratio
        for field in ("decision_situation", "original_framing", "synthesized_position"):
            va = xa.get(field, "") or ""
            vb = xb.get(field, "") or ""
            pair[field] = {
                "similarity": round(_text_similarity(va, vb), 3),
                "len_a": len(va),
                "len_b": len(vb),
            }
        # live_constraints — Jaccard on normalized constraint text
        ca = xa.get("live_constraints", []) or []
        cb = xb.get("live_constraints", []) or []
        pair["live_constraints"] = {
            "count_a": len(ca), "count_b": len(cb),
            "jaccard": round(_list_jaccard_keyed(
                ca, cb,
                key=lambda c: (c.get("constraint", "") or "").strip().lower()
            ), 3),
        }
        # live_constraints_canonical_key — Jaccard on canonical_key slugs with
        # empty-string exclusion. None when both runs have no valid keys
        # (captured in invalid_key_rate below). See PR #1 of the extraction
        # contract roadmap.
        ck_jaccard = _list_jaccard_keyed_nonempty(
            ca, cb,
            key=lambda c: (c.get("canonical_key", "") or "").strip().lower()
        )
        pair["live_constraints_canonical_key"] = {
            "count_a": len(ca), "count_b": len(cb),
            "jaccard": None if ck_jaccard is None else round(ck_jaccard, 3),
        }
        # live_constraints_canonical_key_embedding — semantic similarity via
        # embedding cosine. Treats `marcus-comp` and `marcus-comp-below-market`
        # as close; see PR #1b rationale. Filters empty keys before embedding.
        keys_a = [(c.get("canonical_key", "") or "").strip().lower()
                  for c in ca
                  if (c.get("canonical_key", "") or "").strip()]
        keys_b = [(c.get("canonical_key", "") or "").strip().lower()
                  for c in cb
                  if (c.get("canonical_key", "") or "").strip()]
        if not keys_a and not keys_b:
            ck_embedding = None
        elif not keys_a or not keys_b:
            ck_embedding = 0.0
        else:
            vecs_a = [_get_embedding(k) for k in keys_a]
            vecs_b = [_get_embedding(k) for k in keys_b]
            ck_embedding = _best_match_mean_cosine(vecs_a, vecs_b)
        pair["live_constraints_canonical_key_embedding"] = {
            "count_a": len(keys_a), "count_b": len(keys_b),
            "mean_cosine": None if ck_embedding is None else round(ck_embedding, 3),
        }
        # reasoning_passages — Jaccard on normalized quote strings
        pa = xa.get("reasoning_passages", []) or []
        pb = xb.get("reasoning_passages", []) or []
        pair["reasoning_passages"] = {
            "count_a": len(pa), "count_b": len(pb),
            "jaccard": round(_list_jaccard_keyed(
                pa, pb, key=lambda s: (s or "").strip().lower()
            ), 3),
        }
        # dropped_threads — Jaccard on normalized thread text
        ta = xa.get("dropped_threads", []) or []
        tb = xb.get("dropped_threads", []) or []
        pair["dropped_threads"] = {
            "count_a": len(ta), "count_b": len(tb),
            "jaccard": round(_list_jaccard_keyed(
                ta, tb,
                key=lambda t: (t.get("thread", "") or "").strip().lower()
            ), 3),
        }
        # _quote_validation — fabricated quote counts
        qa = xa.get("_quote_validation", {}) or {}
        qb = xb.get("_quote_validation", {}) or {}
        pair["fabricated_count"] = {"a": qa.get("fabricated", 0), "b": qb.get("fabricated", 0)}
        pairs.append(pair)

    # Aggregate per-field statistics (mean/min/max across all pairs)
    def _mean(values: list[float]) -> float:
        return round(sum(values) / len(values), 3) if values else 0.0

    agg: dict = {}
    for field in ("decision_situation", "original_framing", "synthesized_position"):
        sims = [p[field]["similarity"] for p in pairs]
        agg[field] = {
            "mean_similarity": _mean(sims),
            "min_similarity": round(min(sims), 3) if sims else 0.0,
            "max_similarity": round(max(sims), 3) if sims else 0.0,
        }
    # canonical_key aggregate: filter None (both-empty pairs) before mean/min/max.
    ck_vals = [p["live_constraints_canonical_key"]["jaccard"]
               for p in pairs
               if p["live_constraints_canonical_key"]["jaccard"] is not None]
    agg["live_constraints_canonical_key"] = {
        "mean_jaccard": _mean(ck_vals) if ck_vals else None,
        "min_jaccard": round(min(ck_vals), 3) if ck_vals else None,
        "max_jaccard": round(max(ck_vals), 3) if ck_vals else None,
        "undefined_pair_count": sum(
            1 for p in pairs if p["live_constraints_canonical_key"]["jaccard"] is None
        ),
    }
    # canonical_key embedding aggregate: same shape, filter None pairs.
    cke_vals = [p["live_constraints_canonical_key_embedding"]["mean_cosine"]
                for p in pairs
                if p["live_constraints_canonical_key_embedding"]["mean_cosine"] is not None]
    agg["live_constraints_canonical_key_embedding"] = {
        "mean_cosine": round(sum(cke_vals) / len(cke_vals), 3) if cke_vals else None,
        "min_cosine": round(min(cke_vals), 3) if cke_vals else None,
        "max_cosine": round(max(cke_vals), 3) if cke_vals else None,
        "undefined_pair_count": sum(
            1 for p in pairs if p["live_constraints_canonical_key_embedding"]["mean_cosine"] is None
        ),
    }
    for field in ("live_constraints", "reasoning_passages", "dropped_threads"):
        js = [p[field]["jaccard"] for p in pairs]
        agg[field] = {
            "mean_jaccard": _mean(js),
            "min_jaccard": round(min(js), 3) if js else 0.0,
            "max_jaccard": round(max(js), 3) if js else 0.0,
        }
    agg["fabricated_count_per_run"] = [
        (e.get("extraction", {}).get("_quote_validation", {}) or {}).get("fabricated", 0)
        for _, e in extractions
    ]
    agg["capture_health_per_run"] = [e.get("capture_health", "?") for _, e in extractions]

    # canonical_key invalid rate — count constraints with missing or empty
    # canonical_key, divide by total. Per-run and overall. See PR #1
    # acceptance gate: overall rate must stay ≤ 10%.
    invalid_per_run: list[float] = []
    invalid_counts: list[int] = []
    total_counts: list[int] = []
    for _, e in extractions:
        constraints = (e.get("extraction", {}) or {}).get("live_constraints", []) or []
        total = len(constraints)
        invalid = sum(
            1 for c in constraints
            if not (c.get("canonical_key", "") or "").strip()
        )
        invalid_counts.append(invalid)
        total_counts.append(total)
        invalid_per_run.append(round(invalid / total, 3) if total else 0.0)
    agg["invalid_key_rate_per_run"] = invalid_per_run
    agg["invalid_key_counts_per_run"] = invalid_counts
    agg["total_key_counts_per_run"] = total_counts
    total_all = sum(total_counts)
    invalid_all = sum(invalid_counts)
    agg["invalid_key_rate_overall"] = (
        round(invalid_all / total_all, 3) if total_all else 0.0
    )

    return {
        "n_runs": len(extractions),
        "run_ids": [rid for rid, _ in extractions],
        "aggregate": agg,
        "pairs": pairs,
    }


def render_drift_markdown(drift: dict, case_id: str, generated_at: str,
                          conversation: Path) -> str:
    out: list[str] = []
    out.append(f"# Extraction drift report — {case_id}")
    out.append("")
    out.append(f"Generated: {generated_at}")
    conv_size = conversation.stat().st_size if conversation.exists() else "?"
    out.append(f"Conversation: `{conversation}` ({conv_size} bytes)")
    out.append(f"Runs: {drift['n_runs']}")
    out.append(f"Run IDs: {', '.join(drift['run_ids'])}")
    out.append("")
    out.append("**Reading the metrics:**")
    out.append("- Free-text fields (`decision_situation`, `original_framing`, `synthesized_position`) — difflib SequenceMatcher ratio (character-level). 1.0 = identical; 0.7+ = very similar; 0.4–0.7 = material drift (paraphrase or reshape); <0.4 = shape-shift.")
    out.append("- List fields (`live_constraints`, `reasoning_passages`, `dropped_threads`) — Jaccard on normalized item text (strip, lowercase).")
    out.append("- `live_constraints_canonical_key` — Jaccard on `canonical_key` slugs with empty-string exclusion: empty/missing keys are filtered from BOTH sets before intersection so two failed extractions do not trivially match. A pair with all-empty keys on both sides is reported as `—` (undefined); the failure rate lives in `invalid_key_rate`.")
    out.append("- `invalid_key_rate` — share of constraints where `canonical_key` is missing or empty (the LLM failed the slug format rule). Per-run + overall. Acceptance gate target: ≤ 10%.")
    out.append("- `fabricated_count_per_run` — passages the extractor marked as not-a-literal-substring. Higher is worse.")
    out.append("")
    out.append("## Aggregate drift")
    out.append("")
    out.append("| Field | Metric | Mean | Min | Max |")
    out.append("|---|---|---|---|---|")
    agg = drift.get("aggregate", {}) or {}
    for field in ("decision_situation", "original_framing", "synthesized_position"):
        a = agg.get(field, {})
        out.append(f"| `{field}` | similarity | {_fmt(a.get('mean_similarity'), 3)} | {_fmt(a.get('min_similarity'), 3)} | {_fmt(a.get('max_similarity'), 3)} |")
    for field in ("live_constraints", "reasoning_passages", "dropped_threads"):
        a = agg.get(field, {})
        out.append(f"| `{field}` | jaccard | {_fmt(a.get('mean_jaccard'), 3)} | {_fmt(a.get('min_jaccard'), 3)} | {_fmt(a.get('max_jaccard'), 3)} |")
    # canonical_key row — may be None across all pairs if every pair was
    # fully-degenerate; render as "—" in that case.
    ck = agg.get("live_constraints_canonical_key", {}) or {}
    out.append(
        f"| `live_constraints_canonical_key` | jaccard (empty-excl) | "
        f"{_fmt(ck.get('mean_jaccard'), 3)} | {_fmt(ck.get('min_jaccard'), 3)} | "
        f"{_fmt(ck.get('max_jaccard'), 3)} |"
    )
    if ck.get("undefined_pair_count", 0):
        out.append(
            f"> `live_constraints_canonical_key` has "
            f"{ck['undefined_pair_count']} undefined pair(s) — both runs had "
            f"no valid canonical_keys. See `invalid_key_rate` below."
        )
    # canonical_key_embedding row — PR #1b primary metric for semantic agreement.
    cke = agg.get("live_constraints_canonical_key_embedding", {}) or {}
    out.append(
        f"| `live_constraints_canonical_key_embedding` | cosine (empty-excl) | "
        f"{_fmt(cke.get('mean_cosine'), 3)} | {_fmt(cke.get('min_cosine'), 3)} | "
        f"{_fmt(cke.get('max_cosine'), 3)} |"
    )
    out.append("")
    out.append(
        f"**`invalid_key_rate` per run:** {agg.get('invalid_key_rate_per_run', [])}"
    )
    out.append(
        f"**`invalid_key_rate` overall:** "
        f"{_fmt(agg.get('invalid_key_rate_overall'), 3)} "
        f"({sum(agg.get('invalid_key_counts_per_run', []) or [0])} invalid of "
        f"{sum(agg.get('total_key_counts_per_run', []) or [0])} total constraints)"
    )
    out.append(f"**Fabricated-quote counts per run:** {agg.get('fabricated_count_per_run', [])}")
    out.append(f"**Capture health per run:** {agg.get('capture_health_per_run', [])}")
    out.append("")
    out.append("## Pairwise detail")
    out.append("")
    for p in drift.get("pairs", []):
        out.append(f"### `{p['a']}` vs `{p['b']}`")
        for field in ("decision_situation", "original_framing", "synthesized_position"):
            d = p[field]
            out.append(f"- **{field}**: similarity={d['similarity']:.3f}, lengths {d['len_a']} ↔ {d['len_b']}")
        for field in ("live_constraints", "reasoning_passages", "dropped_threads"):
            d = p[field]
            out.append(f"- **{field}**: jaccard={d['jaccard']:.3f}, counts {d['count_a']} ↔ {d['count_b']}")
        ck_d = p.get("live_constraints_canonical_key", {}) or {}
        ck_j = ck_d.get("jaccard")
        ck_str = "undefined (both-empty)" if ck_j is None else f"{ck_j:.3f}"
        out.append(
            f"- **live_constraints_canonical_key**: jaccard={ck_str}, "
            f"counts {ck_d.get('count_a', 0)} ↔ {ck_d.get('count_b', 0)}"
        )
        fc = p.get("fabricated_count", {})
        out.append(f"- **fabricated**: a={fc.get('a',0)}, b={fc.get('b',0)}")
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--case-id", required=True, help="case identifier, e.g., marcus-baseline")
    ap.add_argument("--runs", nargs="*", help="existing result.json paths (aggregate mode)")
    ap.add_argument("--extraction", help="extraction.json path (rerun mode)")
    ap.add_argument("--conversation",
                    help="conversation.txt path. Required for --drift mode and for default --extraction reruns.")
    ap.add_argument("--legacy-contract", action="store_true",
                    help="Mode B only: rerun the legacy CritiqueRequest path explicitly.")
    ap.add_argument("--drift", action="store_true",
                    help="extraction-drift mode — re-run run_extract.py N times on --conversation, measure per-field drift")
    ap.add_argument("--from-extractions", nargs="*", dest="from_extractions",
                    help="cross-capture mode — compute drift across pre-extracted JSON paths "
                         "(no re-running). Used for acceptance-gate cross-capture axis.")
    ap.add_argument("-n", type=int, default=3, help="rerun count for --extraction or --drift (1-5)")
    ap.add_argument("--output-dir", help="override research/stability-runs/{case-id}-{date}/")
    ap.add_argument("--skill-dir", default=str(SKILL_DIR), help="path to skill root")
    args = ap.parse_args()

    if args.n < 1 or args.n > 5:
        ap.error("-n must be in [1, 5]")

    skill_dir = Path(args.skill_dir).resolve()
    date = _dt.datetime.utcnow().strftime("%Y-%m-%d")
    generated_at = _dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    out_dir = Path(args.output_dir) if args.output_dir else (
        skill_dir / "research" / "stability-runs" / f"{args.case_id}-{date}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- Mode C: extraction drift ---
    if args.drift:
        if not args.conversation:
            ap.error("--drift requires --conversation <path>")
        conv = Path(args.conversation).resolve()
        if not conv.exists():
            ap.error(f"conversation file not found: {conv}")
        print(f"[drift] {args.n} extractions from {conv.name}", file=sys.stderr)
        extraction_paths = _rerun_extractions(conv, args.n, skill_dir)
        extractions = [(_run_id_from_extraction_path(p), _load_extraction(p)) for p in extraction_paths]
        drift = compute_extraction_drift(extractions)

        (out_dir / "drift.json").write_text(json.dumps(drift, indent=2))
        (out_dir / "runs.txt").write_text("\n".join(drift["run_ids"]) + "\n")
        (out_dir / "config.json").write_text(json.dumps({
            "case_id": args.case_id,
            "mode": "extraction_drift",
            "generated_at": generated_at,
            "conversation": str(conv),
            "extraction_paths": [str(p) for p in extraction_paths],
        }, indent=2))
        (out_dir / "drift.md").write_text(
            render_drift_markdown(drift, args.case_id, generated_at, conv))

        # Terminal summary
        print(f"\n=== Extraction drift report: {args.case_id} ===")
        print(f"Output dir: {out_dir}")
        print(f"N runs:     {drift['n_runs']}")
        agg = drift.get("aggregate", {}) or {}
        for field in ("decision_situation", "original_framing", "synthesized_position"):
            a = agg.get(field, {})
            print(f"  {field:22s} similarity mean={_fmt(a.get('mean_similarity'),3)} "
                  f"min={_fmt(a.get('min_similarity'),3)}")
        for field in ("live_constraints", "reasoning_passages", "dropped_threads"):
            a = agg.get(field, {})
            print(f"  {field:22s} jaccard    mean={_fmt(a.get('mean_jaccard'),3)} "
                  f"min={_fmt(a.get('min_jaccard'),3)}")
        ck = agg.get("live_constraints_canonical_key", {}) or {}
        print(f"  {'canonical_key':22s} jaccard    mean={_fmt(ck.get('mean_jaccard'),3)} "
              f"min={_fmt(ck.get('min_jaccard'),3)}")
        cke = agg.get("live_constraints_canonical_key_embedding", {}) or {}
        print(f"  {'canonical_key_embed':22s} cosine     mean={_fmt(cke.get('mean_cosine'),3)} "
              f"min={_fmt(cke.get('min_cosine'),3)}")
        print(f"  invalid_key_rate:     per_run={agg.get('invalid_key_rate_per_run', [])} "
              f"overall={_fmt(agg.get('invalid_key_rate_overall'),3)}")
        print(f"  fabricated counts:    {agg.get('fabricated_count_per_run', [])}")
        return 0

    # --- Cross-capture mode: compute drift across pre-extracted JSONs ---
    if args.from_extractions:
        ext_paths = [Path(p).resolve() for p in args.from_extractions]
        for p in ext_paths:
            if not p.exists():
                ap.error(f"extraction file not found: {p}")
        if len(ext_paths) < 2:
            ap.error("--from-extractions requires at least 2 paths")
        print(f"[cross-capture] {len(ext_paths)} pre-extracted JSONs", file=sys.stderr)
        extractions = [(_run_id_from_extraction_path(p), _load_extraction(p)) for p in ext_paths]
        drift = compute_extraction_drift(extractions)

        (out_dir / "drift.json").write_text(json.dumps(drift, indent=2))
        (out_dir / "runs.txt").write_text("\n".join(drift["run_ids"]) + "\n")
        (out_dir / "config.json").write_text(json.dumps({
            "case_id": args.case_id,
            "mode": "cross_capture_from_extractions",
            "generated_at": generated_at,
            "extraction_paths": [str(p) for p in ext_paths],
        }, indent=2))
        # render_drift_markdown requires a conversation path for its header;
        # pass a stub since cross-capture has no single conversation.
        stub_conv = Path("cross-capture (no single conversation)")
        (out_dir / "drift.md").write_text(
            render_drift_markdown(drift, args.case_id, generated_at, stub_conv))

        # Terminal summary (mirrors --drift summary)
        print(f"\n=== Cross-capture drift report: {args.case_id} ===")
        print(f"Output dir: {out_dir}")
        print(f"N runs:     {drift['n_runs']}")
        agg = drift.get("aggregate", {}) or {}
        for field in ("decision_situation", "original_framing", "synthesized_position"):
            a = agg.get(field, {})
            print(f"  {field:22s} similarity mean={_fmt(a.get('mean_similarity'),3)} "
                  f"min={_fmt(a.get('min_similarity'),3)}")
        for field in ("live_constraints", "reasoning_passages", "dropped_threads"):
            a = agg.get(field, {})
            print(f"  {field:22s} jaccard    mean={_fmt(a.get('mean_jaccard'),3)} "
                  f"min={_fmt(a.get('min_jaccard'),3)}")
        ck = agg.get("live_constraints_canonical_key", {}) or {}
        print(f"  {'canonical_key':22s} jaccard    mean={_fmt(ck.get('mean_jaccard'),3)} "
              f"min={_fmt(ck.get('min_jaccard'),3)}")
        cke = agg.get("live_constraints_canonical_key_embedding", {}) or {}
        print(f"  {'canonical_key_embed':22s} cosine     mean={_fmt(cke.get('mean_cosine'),3)} "
              f"min={_fmt(cke.get('min_cosine'),3)}")
        print(f"  invalid_key_rate:     per_run={agg.get('invalid_key_rate_per_run', [])} "
              f"overall={_fmt(agg.get('invalid_key_rate_overall'),3)}")
        print(f"  fabricated counts:    {agg.get('fabricated_count_per_run', [])}")
        return 0

    # --- Mode A/B: stability (aggregate + optional rerun) ---
    if not args.runs and not args.extraction:
        ap.error("provide --runs <paths...>, --extraction <path>, --drift --conversation <path>, or --from-extractions <paths...>")

    run_paths: list[Path] = []
    if args.extraction:
        ext = Path(args.extraction).resolve()
        conv = Path(args.conversation).resolve() if args.conversation else None
        if conv is None and not args.legacy_contract:
            ap.error("--extraction rerun mode requires --conversation unless --legacy-contract is supplied")
        print(f"[rerun] {args.n} pipeline runs from {ext.name}", file=sys.stderr)
        run_paths.extend(
            _rerun_pipeline(
                ext,
                conv,
                args.n,
                skill_dir,
                legacy_contract=args.legacy_contract,
            )
        )
    if args.runs:
        for p in args.runs:
            run_paths.append(Path(p).resolve())

    if not run_paths:
        print("No run paths collected.", file=sys.stderr)
        return 1
    if len(run_paths) < 2:
        print("Need at least 2 runs for a stability report.", file=sys.stderr)
        return 1

    results = [(_run_id_from_path(p), _load_result(p)) for p in run_paths]
    stability = compute_stability(results)
    prompt_cfg = prompt_versions_across(results)

    (out_dir / "stability.json").write_text(json.dumps(stability, indent=2))
    (out_dir / "runs.txt").write_text("\n".join(stability["run_ids"]) + "\n")
    (out_dir / "config.json").write_text(json.dumps({
        "case_id": args.case_id,
        "generated_at": generated_at,
        "skill_dir": str(skill_dir),
        "run_paths": [str(p) for p in run_paths],
        "prompt_versions": prompt_cfg,
    }, indent=2))
    (out_dir / "variance.md").write_text(
        render_markdown(stability, prompt_cfg, args.case_id, generated_at))

    # Terminal summary
    print(f"\n=== Stability report: {args.case_id} ===")
    print(f"Output dir: {out_dir}")
    print(f"N runs:     {stability['n_runs']}  ({', '.join(stability['run_ids'])})")
    for label, key in [
        ("Pass 1 (tendencies) Jaccard", "pass1_tendencies"),
        ("Lane 2 (anchors)    Jaccard", "lane2_anchors"),
        ("Lane 3 (reframings) Jaccard", "lane3_reframings"),
        ("Lane 4 (gap dims)   Jaccard", "lane4_gaps"),
    ]:
        mean = stability[key]["stability"]["mean"]
        print(f"  {label}: {_fmt(mean)}")
    step6 = stability["step6_anchor_mentions"]
    tn = sum(s["named"] for s in step6 if s["present"])
    tt = sum(s["total"] for s in step6 if s["present"])
    pc = sum(1 for s in step6 if s["present"])
    if tt:
        print(f"  Step 6 anchor naming: {tn}/{tt} = {100*tn//tt}% "
              f"({pc}/{len(step6)} runs had revised_answer)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
