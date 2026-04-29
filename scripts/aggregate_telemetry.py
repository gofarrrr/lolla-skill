"""Cross-run aggregation of audit_summary telemetry.

Walks the local archived-runs directory, extracts one slice at a time, and
summarizes how the system behaves across the corpus. Writes a Markdown
report to stdout and a JSON aggregate to the user data directory for later
consumption (e.g. an /aggregate Observatory panel).

Per-run telemetry tells you what the system did on a single case. This
script tells you how it behaves across cases — which signals are stable,
which drift, which catalog regions never surface.

Slices:
    lane2-pool    Companion candidate-pool stability across runs:
                  universal set, run-unique tail, pairwise Jaccard,
                  recall-source decomposition, catalog dead-zones,
                  rank stability for the universal models.

Usage:
    python3 scripts/aggregate_telemetry.py --slice lane2-pool
    python3 scripts/aggregate_telemetry.py --slice lane2-pool --runs-dir <path>
    python3 scripts/aggregate_telemetry.py --slice lane2-pool --json-out <file>
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from itertools import combinations
from pathlib import Path

DEFAULT_RUNS_DIR = Path.home() / ".local/share/lolla/runs"
DEFAULT_AGGREGATES_DIR = Path.home() / ".local/share/lolla/aggregates"
SKILL_ROOT = Path(__file__).resolve().parent.parent
KG_PATH = SKILL_ROOT / "data" / "knowledge_graph.json"


# ---------------------------------------------------------------------------
# Corpus loader — common to every slice
# ---------------------------------------------------------------------------


def _load_runs(runs_dir: Path) -> list[dict]:
    """Walk runs_dir and return one entry per result.json that carries an
    ``audit_summary`` block. Older artifacts are skipped silently — they
    pre-date Phase-7 and have nothing useful for aggregation.
    """
    found: list[dict] = []
    for result_path in sorted(runs_dir.glob("*/*/result.json")):
        try:
            with open(result_path) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        audit = (data.get("audit_summary") or {})
        if not audit:
            continue
        found.append({
            "case_slug": result_path.parent.parent.name,
            "captured_at": result_path.parent.name,
            "path": str(result_path),
            "result": data,
        })
    return found


def _load_catalog_model_ids() -> set[str]:
    if not KG_PATH.exists():
        return set()
    try:
        with open(KG_PATH) as f:
            kg = json.load(f)
    except (OSError, json.JSONDecodeError):
        return set()
    return set((kg.get("models") or {}).keys())


# ---------------------------------------------------------------------------
# Slice: lane2-pool
# ---------------------------------------------------------------------------


def _candidates_for_run(run: dict) -> list[dict]:
    audit = run["result"].get("audit_summary") or {}
    return [c for c in (audit.get("companion_candidates") or []) if c.get("model_id")]


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def analyze_lane2_pool(runs: list[dict]) -> dict:
    """Produce an aggregate report on Lane 2 candidate-pool behaviour.

    Two layers of bookkeeping:
      • surveyed = every run we walked (audit_summary present, including
        legacy artifacts whose pools are empty). Surfaced as the run table.
      • analyzed = runs whose pool is non-empty. Universal/Jaccard/etc.
        run only over this subset; mixing 0-size pools into the math
        produces 0/0=1.0 noise that floods the real signal.
    """
    pools: list[dict] = []
    for run in runs:
        cands = _candidates_for_run(run)
        ids = {c["model_id"] for c in cands}
        by_source: dict[str, set[str]] = {}
        ranks_by_id: dict[str, int] = {}
        for c in cands:
            src = c.get("recall_source") or "unknown"
            by_source.setdefault(src, set()).add(c["model_id"])
            rank = c.get("final_rank")
            if isinstance(rank, int):
                ranks_by_id[c["model_id"]] = rank
        pools.append({
            "case_slug": run["case_slug"],
            "captured_at": run["captured_at"],
            "size": len(ids),
            "ids": ids,
            "ids_by_source": by_source,
            "ranks_by_id": ranks_by_id,
        })

    surveyed = pools
    analyzed = [p for p in pools if p["size"] > 0]

    if not analyzed:
        return {
            "slice": "lane2-pool",
            "n_surveyed": len(surveyed),
            "n_analyzed": 0,
            "note": (
                "No runs with non-empty audit_summary.companion_candidates. "
                "Re-run cases against the current pipeline to populate the pool."
            ),
            "surveyed": [
                {"case_slug": p["case_slug"], "captured_at": p["captured_at"], "pool_size": p["size"]}
                for p in surveyed
            ],
        }

    all_ids: set[str] = set().union(*[p["ids"] for p in analyzed])
    universal: set[str] = (
        set.intersection(*[p["ids"] for p in analyzed]) if len(analyzed) > 1 else set(analyzed[0]["ids"])
    )

    run_unique: dict[str, list[str]] = {}
    for p in analyzed:
        others = set().union(*[q["ids"] for q in analyzed if q is not p]) if len(analyzed) > 1 else set()
        run_unique[p["case_slug"]] = sorted(p["ids"] - others)

    pairwise: list[dict] = []
    for a, b in combinations(analyzed, 2):
        pairwise.append({
            "a": a["case_slug"],
            "b": b["case_slug"],
            "intersection": len(a["ids"] & b["ids"]),
            "union": len(a["ids"] | b["ids"]),
            "jaccard": round(_jaccard(a["ids"], b["ids"]), 3),
        })

    # Source decomposition — only over analyzed runs, and only over sources
    # that have at least one non-empty set somewhere in the corpus.
    source_keys: set[str] = set()
    for p in analyzed:
        source_keys.update(p["ids_by_source"].keys())

    source_decomp: dict[str, dict] = {}
    for src in sorted(source_keys):
        src_pools = [p["ids_by_source"].get(src, set()) for p in analyzed]
        non_empty = [s for s in src_pools if s]
        if not non_empty:
            continue
        src_universal = set.intersection(*non_empty) if len(non_empty) > 1 else non_empty[0]
        src_union: set[str] = set().union(*non_empty)
        src_pairs = [_jaccard(a, b) for a, b in combinations(non_empty, 2)]
        source_decomp[src] = {
            "size_per_run": [len(s) for s in src_pools],
            "non_empty_runs": len(non_empty),
            "universal_count": len(src_universal),
            "union_count": len(src_union),
            "mean_jaccard": round(statistics.mean(src_pairs), 3) if src_pairs else None,
        }

    catalog = _load_catalog_model_ids()
    dead_zones = sorted(catalog - all_ids) if catalog else []

    rank_stability: list[dict] = []
    for mid in sorted(universal):
        ranks = [p["ranks_by_id"].get(mid) for p in analyzed if p["ranks_by_id"].get(mid) is not None]
        if len(ranks) >= 2:
            rank_stability.append({
                "model_id": mid,
                "ranks": ranks,
                "mean": round(statistics.mean(ranks), 1),
                "stdev": round(statistics.stdev(ranks), 1),
            })
    rank_stability.sort(key=lambda r: r["stdev"])  # most stable first

    return {
        "slice": "lane2-pool",
        "n_surveyed": len(surveyed),
        "n_analyzed": len(analyzed),
        "surveyed": [
            {"case_slug": p["case_slug"], "captured_at": p["captured_at"], "pool_size": p["size"]}
            for p in surveyed
        ],
        "analyzed": [
            {"case_slug": p["case_slug"], "captured_at": p["captured_at"], "pool_size": p["size"]}
            for p in analyzed
        ],
        "catalog_size": len(catalog),
        "all_ids_seen": len(all_ids),
        "universal": sorted(universal),
        "universal_count": len(universal),
        "run_unique": run_unique,
        "pairwise": pairwise,
        "mean_jaccard": round(statistics.mean(p["jaccard"] for p in pairwise), 3) if pairwise else None,
        "source_decomposition": source_decomp,
        "dead_zones_count": len(dead_zones),
        "dead_zones": dead_zones,
        "rank_stability": rank_stability,
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_lane2_pool_md(report: dict) -> str:
    if report["n_analyzed"] == 0:
        lines = [
            "# Lane 2 candidate-pool stability",
            "",
            f"Surveyed **{report['n_surveyed']}** run(s) — "
            "none carry a non-empty `audit_summary.companion_candidates` pool.",
            "",
            report.get("note", ""),
        ]
        if report.get("surveyed"):
            lines.append("")
            lines.append("## Surveyed runs")
            lines.append("")
            lines.append("| Case | Captured | Pool size |")
            lines.append("|---|---|---|")
            for r in report["surveyed"]:
                lines.append(f"| {r['case_slug']} | {r['captured_at']} | {r['pool_size']} |")
        return "\n".join(lines) + "\n"

    lines: list[str] = []
    lines.append("# Lane 2 candidate-pool stability")
    lines.append("")
    lines.append(
        f"Surveyed **{report['n_surveyed']}** run(s) · "
        f"analysed **{report['n_analyzed']}** with non-empty pools."
    )
    if report.get("catalog_size"):
        coverage = (report["all_ids_seen"] / report["catalog_size"]) * 100
        lines.append(
            f"Catalog: **{report['catalog_size']}** models · "
            f"**{report['all_ids_seen']}** seen across the analysed pools "
            f"({coverage:.1f}% catalog coverage) · "
            f"**{report['dead_zones_count']}** never surfaced."
        )
    lines.append("")

    lines.append("## Surveyed runs")
    lines.append("")
    lines.append("Empty pools are pre-Phase-7 artifacts (re-run to populate).")
    lines.append("")
    lines.append("| Case | Captured | Pool size |")
    lines.append("|---|---|---|")
    for r in report["surveyed"]:
        marker = "" if r["pool_size"] > 0 else " *(empty — not analysed)*"
        lines.append(f"| {r['case_slug']} | {r['captured_at']} | {r['pool_size']}{marker} |")
    lines.append("")

    lines.append("## Universal set — models in every analysed pool")
    lines.append("")
    pct = (report["universal_count"] / report["all_ids_seen"] * 100) if report["all_ids_seen"] else 0
    lines.append(
        f"**{report['universal_count']}** model(s) "
        f"({pct:.0f}% of the union) appear in all "
        f"{report['n_analyzed']} pools."
    )
    lines.append("")
    if report["universal"]:
        for mid in report["universal"]:
            lines.append(f"- `{mid}`")
        lines.append("")

    if report["pairwise"]:
        lines.append("## Pairwise Jaccard")
        lines.append("")
        lines.append(f"Mean Jaccard across the {len(report['pairwise'])} pair(s): **{report['mean_jaccard']}**")
        lines.append("")
        lines.append("| Run A | Run B | Overlap | Union | Jaccard |")
        lines.append("|---|---|---|---|---|")
        for p in report["pairwise"]:
            lines.append(f"| {p['a']} | {p['b']} | {p['intersection']} | {p['union']} | {p['jaccard']} |")
        lines.append("")

    if report["source_decomposition"]:
        lines.append("## Recall-source decomposition")
        lines.append("")
        lines.append(
            "Same overlap math, sliced by where each candidate came from "
            "(`keyword`, `embedding`, curated activation triggers)."
        )
        lines.append("")
        lines.append("| Source | Non-empty runs | Sizes | Universal | Union | Mean Jaccard |")
        lines.append("|---|---|---|---|---|---|")
        for src, info in report["source_decomposition"].items():
            sizes = ", ".join(str(s) for s in info["size_per_run"] if s)
            mj = info["mean_jaccard"] if info["mean_jaccard"] is not None else "—"
            lines.append(
                f"| `{src}` | {info['non_empty_runs']} | {sizes} | "
                f"{info['universal_count']} | {info['union_count']} | {mj} |"
            )
        lines.append("")

    lines.append("## Run-unique tail")
    lines.append("")
    lines.append("Models in exactly one analysed pool — the case-specific reach of retrieval.")
    lines.append("")
    for case_slug, ids in report["run_unique"].items():
        lines.append(f"**{case_slug}** — {len(ids)} model(s) only in this run:")
        if ids:
            for mid in ids:
                lines.append(f"  - `{mid}`")
        lines.append("")

    if report["rank_stability"]:
        lines.append("## Rank stability for universal models")
        lines.append("")
        lines.append("Lower stdev = more stable position across runs.")
        lines.append("")
        lines.append("| Model | Ranks | Mean | Stdev |")
        lines.append("|---|---|---|---|")
        for r in report["rank_stability"]:
            ranks_str = ", ".join(str(x) for x in r["ranks"])
            lines.append(f"| `{r['model_id']}` | {ranks_str} | {r['mean']} | {r['stdev']} |")
        lines.append("")

    if report["dead_zones"]:
        lines.append("## Catalog dead-zones — models that never surfaced in any analysed pool")
        lines.append("")
        lines.append(
            f"{report['dead_zones_count']} of {report['catalog_size']} catalog "
            "models did not appear as a candidate in any analysed run. "
            "May indicate retrieval blind-spots or genuinely off-domain models."
        )
        lines.append("")
        sample = report["dead_zones"][:30]
        for mid in sample:
            lines.append(f"- `{mid}`")
        if len(report["dead_zones"]) > 30:
            lines.append(f"- … and {len(report['dead_zones']) - 30} more")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


SLICES = {
    "lane2-pool": (analyze_lane2_pool, render_lane2_pool_md),
}


def _serialize_for_json(report: dict) -> dict:
    """Convert any sets in the report to sorted lists for JSON output."""
    if isinstance(report, dict):
        return {k: _serialize_for_json(v) for k, v in report.items()}
    if isinstance(report, set):
        return sorted(report)
    if isinstance(report, list):
        return [_serialize_for_json(v) for v in report]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--slice",
        required=True,
        choices=sorted(SLICES.keys()),
        help="Which aggregation to compute.",
    )
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=DEFAULT_RUNS_DIR,
        help=f"Archived runs directory (default: {DEFAULT_RUNS_DIR}).",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help=(
            "Path to write the aggregate JSON. Default: "
            "<aggregates>/<slice>.json under the user data directory."
        ),
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip the Markdown report on stdout (useful when piping the JSON).",
    )
    args = parser.parse_args()

    if not args.runs_dir.is_dir():
        print(f"Error: runs directory not found: {args.runs_dir}", file=sys.stderr)
        return 1

    runs = _load_runs(args.runs_dir)

    analyzer, renderer = SLICES[args.slice]
    report = analyzer(runs)

    if not args.no_markdown:
        print(renderer(report))

    json_out = args.json_out or (DEFAULT_AGGREGATES_DIR / f"{args.slice}.json")
    json_out.parent.mkdir(parents=True, exist_ok=True)
    with open(json_out, "w") as f:
        json.dump(_serialize_for_json(report), f, indent=2)
    print(f"\nAggregate JSON written: {json_out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
