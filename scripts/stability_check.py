#!/usr/bin/env python3
"""
Stability harness for the Lolla pipeline.

Diagnostic, not gate. Measures per-stage stability (Jaccard over set-valued
outputs) across N runs of the same conversation. Two modes:

- Aggregate: given a set of existing result.json paths, compute stability.
- Rerun: given one extraction.json, invoke run_pipeline.py --skip-revision
  N times, then aggregate the new result.json files.

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

def _rerun_pipeline(extraction: Path, conversation: Path | None,
                    n: int, skill_dir: Path) -> list[Path]:
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
        print(f"  [{i+1}/{n}] rid={rid}", file=sys.stderr)
        subprocess.run(cmd, check=True, cwd=str(skill_dir))
        paths.append(result_path)
        time.sleep(1)
    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--case-id", required=True, help="case identifier, e.g., marcus-baseline")
    ap.add_argument("--runs", nargs="*", help="existing result.json paths (aggregate mode)")
    ap.add_argument("--extraction", help="extraction.json path (rerun mode)")
    ap.add_argument("--conversation",
                    help="optional conversation.txt (enables bullshit fact-registry in rerun mode)")
    ap.add_argument("-n", type=int, default=3, help="rerun count when --extraction is given (1-5)")
    ap.add_argument("--output-dir", help="override research/stability-runs/{case-id}-{date}/")
    ap.add_argument("--skill-dir", default=str(SKILL_DIR), help="path to skill root")
    args = ap.parse_args()

    if not args.runs and not args.extraction:
        ap.error("provide --runs <paths...> and/or --extraction <path>")
    if args.n < 1 or args.n > 5:
        ap.error("-n must be in [1, 5]")

    skill_dir = Path(args.skill_dir).resolve()
    date = _dt.datetime.utcnow().strftime("%Y-%m-%d")
    generated_at = _dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    out_dir = Path(args.output_dir) if args.output_dir else (
        skill_dir / "research" / "stability-runs" / f"{args.case_id}-{date}")
    out_dir.mkdir(parents=True, exist_ok=True)

    run_paths: list[Path] = []
    if args.extraction:
        ext = Path(args.extraction).resolve()
        conv = Path(args.conversation).resolve() if args.conversation else None
        print(f"[rerun] {args.n} pipeline runs from {ext.name}", file=sys.stderr)
        run_paths.extend(_rerun_pipeline(ext, conv, args.n, skill_dir))
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
