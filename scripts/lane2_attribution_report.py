#!/usr/bin/env python3
"""
Lane 2 attribution cross-case synthesizer.

Reads multiple per-case stability.json files (each produced by
scripts/stability_check.py rerun mode) and emits a single Markdown report
that puts cases side-by-side, grouped by embedding mode.

The report contract is set by the design memo at
research/lane2-attribution-design-2026-04-26.md. Specifically:

- Per-case rows × Lane 2 substage columns (Jaccard mean).
- Grouped by embedding_mode (on/off) so the embedding-induced variance
  question is answerable in a single glance.
- A `step6_consumption_baseline` column per case, recomputed at report time
  from ~/.local/share/lolla/runs (the archive sanity check). Cases whose
  Step 6 historically consumes few anchors get their Lane 2 variance read
  with that caveat already attached.
- Pre-registered decision-tree applied to each (case, mode) row, naming the
  most-likely fix region per the memo's bands.

Usage:
  python3 scripts/lane2_attribution_report.py \
      --stability research/stability-runs/marcus-lane2-on-2026-04-26/stability.json \
      research/stability-runs/marcus-lane2-off-2026-04-26/stability.json \
      research/stability-runs/whistleblower-lane2-on-2026-04-26/stability.json \
      ... \
      --output research/stability-runs/lane2-attribution-2026-04-26/synthesis.md

Designed to be diagnostic, not corrective. The report names where the
variance most plausibly enters; the fix decision is the human's.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Step 6 consumption baseline (recomputed from local archive)
# ---------------------------------------------------------------------------


def _archive_consumption_baseline(archive_root: Path) -> dict[str, dict]:
    """Walk archived full skill runs and compute per-case Step 6 anchor-naming
    rate. Returns {case_id: {named, total, rate, n_runs}}.

    Methodology mirrors the archive sanity check recorded in the design
    memo: case-insensitive `display_name` substring match in the persisted
    `revised_answer` (or sibling `revised.txt`).
    """
    out: dict[str, dict] = {}
    if not archive_root.exists():
        return out
    for case_dir in sorted(archive_root.iterdir()):
        if not case_dir.is_dir():
            continue
        named_total = 0
        anchor_total = 0
        n_runs = 0
        for run_dir in sorted(case_dir.iterdir()):
            if not run_dir.is_dir():
                continue
            result_path = run_dir / "result.json"
            if not result_path.exists():
                continue
            try:
                d = json.loads(result_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            anchors = (d.get("companion_cheat_sheet") or {}).get("anchors") or []
            if not anchors:
                continue
            revised = d.get("revised_answer") or ""
            if not revised:
                rev_path = run_dir / "revised.txt"
                if rev_path.exists():
                    revised = rev_path.read_text(encoding="utf-8")
            if not revised:
                continue
            names = [a.get("display_name", "") for a in anchors if a.get("display_name")]
            if not names:
                continue
            named = sum(1 for n in names if n and n.lower() in revised.lower())
            named_total += named
            anchor_total += len(names)
            n_runs += 1
        if anchor_total:
            out[case_dir.name] = {
                "named": named_total,
                "total": anchor_total,
                "rate": named_total / anchor_total,
                "n_runs": n_runs,
            }
    return out


def _match_baseline(case_id: str, baseline: dict[str, dict]) -> dict | None:
    """Best-effort match between a stability case_id (e.g. 'whistleblower-lane2-on')
    and an archive case_id (e.g. 'whistleblower-blowing-fortune-200'). Token
    overlap; returns the best match if any token overlaps, else None."""
    if not baseline:
        return None
    if case_id in baseline:
        return baseline[case_id]
    case_tokens = {t for t in case_id.lower().replace("_", "-").split("-") if len(t) > 2}
    best: tuple[float, str] | None = None
    for archive_id in baseline:
        archive_tokens = {t for t in archive_id.lower().replace("_", "-").split("-") if len(t) > 2}
        overlap = len(case_tokens & archive_tokens)
        if overlap > 0:
            score = overlap / max(1, len(case_tokens | archive_tokens))
            if best is None or score > best[0]:
                best = (score, archive_id)
    if best is not None:
        return baseline[best[1]]
    return None


# ---------------------------------------------------------------------------
# Decision tree (pre-registered in the design memo)
# ---------------------------------------------------------------------------


def _decision_call(stability: dict) -> str:
    """Map per-case Lane 2 substage stability to one of the memo's pre-registered
    bands. The first matching band wins; bands are ordered upstream-first."""

    def m(key: str) -> float | None:
        return (stability.get(key, {}) or {}).get("stability", {}).get("mean")

    fp = m("lane2_fingerprint_moves")
    cand = m("lane2_candidates")
    accepted = m("lane2_accepted_before_cap")
    detected = m("lane2_detected_after_cap")
    anchors = m("lane2_anchors")

    # All-stable null result (per memo: declare and look elsewhere).
    bands = [fp, cand, accepted, detected, anchors]
    if all(v is not None and v >= 0.85 for v in bands):
        return "null_result_lane2_stable"

    # Upstream-first cascade.
    if fp is not None and fp < 0.70 and cand is not None and cand < 0.70:
        return "fix_fingerprint_or_query_construction"
    if cand is not None and cand < 0.70:
        return "fix_recall_or_candidate_contract"
    if cand is not None and cand >= 0.85 and accepted is not None and accepted < 0.50:
        return "split_or_narrow_verifier"
    if accepted is not None and accepted >= 0.85 and detected is not None and detected < 0.50:
        return "top_5_ordering_truncation_amplifier"
    if detected is not None and detected >= 0.85 and anchors is not None and anchors < 0.85:
        return "diagnose_companion_selection_reranking"
    return "inconclusive_widen_n_or_cases"


# ---------------------------------------------------------------------------
# Loading + grouping
# ---------------------------------------------------------------------------


def _load_stability(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    # Stability files don't carry their own case_id; derive from output dir name
    # (e.g. 'marcus-lane2-on-2026-04-26' → 'marcus-lane2-on').
    parent = path.parent.name
    # Strip trailing -YYYY-MM-DD if present.
    case_id = parent
    if len(parent) > 11 and parent[-11] == "-" and parent[-10:].count("-") == 2:
        case_id = parent[:-11]
    raw["_case_id"] = case_id
    raw["_source"] = str(path)
    return raw


def _embedding_mode_of(stability: dict) -> str:
    modes = stability.get("embedding_mode_per_run", []) or []
    distinct = set(modes)
    if len(distinct) == 1:
        return next(iter(distinct))
    if not distinct:
        return "unknown"
    return "mixed"


def _fmt(v, digits=2) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    return str(v)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


_LANE2_COLUMNS = [
    ("FP moves",     "lane2_fingerprint_moves"),
    ("Candidates",   "lane2_candidates"),
    ("Accepted-pre", "lane2_accepted_before_cap"),
    ("Detected",     "lane2_detected_after_cap"),
    ("Capped",       "lane2_capped_models"),
    ("Anchors",      "lane2_anchors"),
]


def _row_for_case(stability: dict, baseline: dict[str, dict]) -> dict:
    case_id = stability["_case_id"]
    bl = _match_baseline(case_id, baseline)
    cells: dict[str, str] = {}
    for label, key in _LANE2_COLUMNS:
        st = (stability.get(key, {}) or {}).get("stability", {})
        cells[label] = _fmt(st.get("mean"))
    cost = sum(c.get("total_tokens", 0) for c in stability.get("cost_per_run", []) or [])
    return {
        "case_id": case_id,
        "embedding_mode": _embedding_mode_of(stability),
        "n_runs": stability.get("n_runs", 0),
        "cells": cells,
        "boundary_only_total_tokens": cost,
        "step6_consumption_rate": (bl or {}).get("rate"),
        "step6_baseline_runs": (bl or {}).get("n_runs"),
        "decision_call": _decision_call(stability),
    }


def render(rows: list[dict], generated_at: str, archive_root: Path) -> str:
    out: list[str] = []
    out.append("# Lane 2 attribution — cross-case synthesis")
    out.append("")
    out.append(f"Generated: {generated_at}")
    out.append(f"Archive root for Step 6 consumption baseline: `{archive_root}`")
    out.append("")
    out.append("Contract: research/lane2-attribution-design-2026-04-26.md")
    out.append("")
    out.append("Reading guide:")
    out.append("- Per-cell value = pairwise Jaccard mean across N runs (1.0 is a warning, not a target).")
    out.append("- Decision call applies the memo's pre-registered band rules; not a fix recommendation.")
    out.append("- Step 6 consumption baseline is derived from archived full skill runs at report time, "
               "matched to the case_id by token overlap. Read variance in cases with low consumption "
               "with that caveat — Lane 2 stability is an upper bound on user-visible quality there.")
    out.append("")

    # Group by embedding mode so the on/off question is answerable per case.
    modes = sorted({r["embedding_mode"] for r in rows})
    for mode in modes:
        out.append(f"## Embedding mode: `{mode}`")
        out.append("")
        out.append(
            "| Case | N | "
            + " | ".join(label for label, _ in _LANE2_COLUMNS)
            + " | Step 6 cons. | Boundary tok | Decision |"
        )
        out.append("|---|---|" + "|".join(["---"] * len(_LANE2_COLUMNS)) + "|---|---|---|")
        mode_rows = sorted([r for r in rows if r["embedding_mode"] == mode], key=lambda r: r["case_id"])
        for r in mode_rows:
            cells = " | ".join(r["cells"][label] for label, _ in _LANE2_COLUMNS)
            cons = r["step6_consumption_rate"]
            cons_cell = "—" if cons is None else f"{100 * cons:.0f}% (n={r['step6_baseline_runs']})"
            out.append(
                f"| `{r['case_id']}` | {r['n_runs']} | {cells} | "
                f"{cons_cell} | {r['boundary_only_total_tokens']} | `{r['decision_call']}` |"
            )
        out.append("")

    # Cross-mode delta (for cases that have BOTH on and off rows): Lane 2
    # candidates Jaccard improvement when embeddings drop. Direct evidence
    # for the "embedding-expansion temp=0.7 is the variance source" hypothesis.
    by_case: dict[str, dict[str, dict]] = {}
    for r in rows:
        by_case.setdefault(r["case_id"].rsplit("-", 1)[0], {})[r["embedding_mode"]] = r
    paired = {c: m for c, m in by_case.items() if "on" in m and "off" in m}
    if paired:
        out.append("## Embedding-induced delta (paired ON vs OFF)")
        out.append("")
        out.append("Difference of `Candidates` Jaccard mean (`off` − `on`). Positive = embeddings "
                   "destabilize recall. Negative = embeddings stabilize recall. Near zero = "
                   "embeddings not the dominant variance source for this case.")
        out.append("")
        out.append("| Case | ON candidates | OFF candidates | Δ (off − on) |")
        out.append("|---|---|---|---|")
        for case in sorted(paired):
            on_r = paired[case]["on"]
            off_r = paired[case]["off"]
            on_v = on_r["cells"].get("Candidates")
            off_v = off_r["cells"].get("Candidates")
            try:
                on_f = float(on_v)
                off_f = float(off_v)
                delta = f"{off_f - on_f:+.2f}"
            except (TypeError, ValueError):
                delta = "—"
            out.append(f"| `{case}` | {on_v} | {off_v} | {delta} |")
        out.append("")

    out.append("## Sources")
    out.append("")
    for r in rows:
        out.append(f"- `{r['case_id']}` ({r['embedding_mode']}): N={r['n_runs']}")
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument(
        "--stability",
        nargs="+",
        required=True,
        help="One or more stability.json paths (Mode B output of stability_check.py).",
    )
    ap.add_argument(
        "--output",
        default=None,
        help=(
            "Output Markdown path. Default: "
            "research/stability-runs/lane2-attribution-{date}/synthesis.md"
        ),
    )
    ap.add_argument(
        "--archive-root",
        default=str(Path.home() / ".local/share/lolla/runs"),
        help="Archive root for Step 6 consumption baseline (default: ~/.local/share/lolla/runs).",
    )
    args = ap.parse_args()

    paths = [Path(p).resolve() for p in args.stability]
    for p in paths:
        if not p.exists():
            ap.error(f"stability file not found: {p}")
    archive_root = Path(args.archive_root).expanduser().resolve()
    baseline = _archive_consumption_baseline(archive_root)

    stabilities = [_load_stability(p) for p in paths]
    rows = [_row_for_case(s, baseline) for s in stabilities]

    generated_at = _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_md = render(rows, generated_at, archive_root)

    if args.output:
        out_path = Path(args.output).resolve()
    else:
        date = _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%d")
        skill_dir = Path(__file__).resolve().parent.parent
        out_path = skill_dir / "research" / "stability-runs" / f"lane2-attribution-{date}" / "synthesis.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_md, encoding="utf-8")
    print(f"Wrote: {out_path}")
    print(f"Cases:        {len(rows)}")
    print(f"Embed modes:  {sorted({r['embedding_mode'] for r in rows})}")
    paired = {r['case_id'].rsplit('-', 1)[0] for r in rows
              if any(other['case_id'].rsplit('-', 1)[0] == r['case_id'].rsplit('-', 1)[0]
                     and other['embedding_mode'] != r['embedding_mode'] for other in rows)}
    print(f"Paired cases: {sorted(paired)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
