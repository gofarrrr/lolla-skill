#!/usr/bin/env python3
"""Path D D0 — Lane 2 single-run proxy validation report.

Reads the 8 baseline campaign stability runs (post PR #39 / PR-A, pre v2/v3/B)
and the per-run /tmp result.json files. For every cheat-sheet anchor across
all runs, computes single-run proxies and validates them against multi-run
stability labels.

Substrate (locked in design conversation):

- Inputs: research/stability-runs/*-lane2-{on,off}-2026-04-26/ + the per-run
  /tmp/lolla_*_result.json files those stability runs reference.
- Labels:
    stable_anchor   — model_id appeared in cheat_sheet.anchors in >= 2 of 3 runs
    stable_accepted — model_id appeared in audit_summary.companion_verification_accepted_before_cap
                      in >= 2 of 3 runs
  Primary target = stable_anchor (Step 6 consumes cheat-sheet anchors).
- Proxies (single-run, computable from main-only fields):
    is_broad_overlay         — uses engine.system_b.companion_routing._BROAD_OVERLAY_MODELS
                               OR optional model_payload.is_broad_overlay (forward-compat hook).
                               NOT derived from reasoning_types.
    final_rank               — 1-indexed candidate rank in recall.
    final_rank_bucket        — top10 / top20 / top30 / tail.
    evidence_quote_length    — char count of evidence_quote on the accepted entry (when present).
    quote_collision_count    — number of OTHER accepted models in the same run with substantial
                               substring overlap on the evidence quote.
    accepted_before_cap_position — 1-indexed position in the run's accepted_before_cap list.
    recall_source            — sanity field; expected ~100% "keyword" in current dataset.

  Exploratory metadata (NOT gate-eligible):
    primary_reasoning_type, all_reasoning_types, model_display_name.

D0 gates:
- Pooled AUROC >= 0.70 against stable_anchor.
- Direction consistent in >= 6 of 8 case-mode groups.
- Threshold rule with precision >= 0.75 AND recall >= 0.50.
- Coverage:
    Numeric:  non-null rows / all rows >= 20%.
    Binary:   computable rows / all rows >= 20% AND 0.05 <= positive_rate <= 0.95.
              positive_rate < 0.05 -> "sparse, not promotable without manual caveat."
    Categorical: >= 2 categories with meaningful support.
- Marcus stress test: per-case Marcus AUROC >= (pooled AUROC - 0.15), else
  promotable only with explicit "Marcus-like ambiguity" caveat.

Output:
- research/stability-runs/lane2-pathD-proxy-validation-2026-04-26/proxy_rows.json
  (one row per anchor-instance: case_id, embedding_mode, run_id, model_id, label,
   all proxy values, all exploratory metadata)
- research/stability-runs/lane2-pathD-proxy-validation-2026-04-26/report.md
  (human-readable verdicts + tables)

Verdict per proxy:
  PROMOTABLE                — clears all D0 gates for stable_anchor.
  WORDING_ONLY_EVIDENCE     — directionally informative but doesn't clear AUROC/threshold gates;
                               supports wording-only Step 6 changes, not tiered metadata.
  NO_SIGNAL                 — no usable predictive power; do not invest further.
  COVERAGE_INELIGIBLE       — coverage too low or positive_rate too sparse/saturated.

No LLM calls. Pure analysis of existing artifacts.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "engine"))

# Mirrors engine.system_b.companion_routing._BROAD_OVERLAY_MODELS — imported
# (not duplicated) so any production change to the set propagates here.
from system_b.companion_routing import _BROAD_OVERLAY_MODELS  # type: ignore


# ---------------------------------------------------------------------------
# Inputs: walk the 8 baseline campaigns
# ---------------------------------------------------------------------------

BASELINE_CAMPAIGN_GLOBS = [
    "*-lane2-on-2026-04-26",
    "*-lane2-off-2026-04-26",
]


def discover_baseline_runs(stability_root: Path) -> list[tuple[str, str, Path]]:
    """Return [(case_id, embedding_mode, stability_dir), ...] for the 8 baseline campaigns."""
    out: list[tuple[str, str, Path]] = []
    for pattern in BASELINE_CAMPAIGN_GLOBS:
        for d in sorted(stability_root.glob(pattern)):
            if not d.is_dir():
                continue
            stab_path = d / "stability.json"
            if not stab_path.exists():
                continue
            name = d.name  # e.g. marcus-equity-lane2-on-2026-04-26
            mode = "on" if name.endswith("-on-2026-04-26") else (
                "off" if name.endswith("-off-2026-04-26") else "unknown"
            )
            # Strip the -lane2-{mode}-DATE suffix to get the case_id.
            case_id = re.sub(r"-lane2-(on|off)-\d{4}-\d{2}-\d{2}$", "", name)
            out.append((case_id, mode, d))
    return out


def load_per_run_result(run_id: str, tmp_root: Path = Path("/tmp")) -> dict | None:
    p = tmp_root / f"lolla_{run_id}_result.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_knowledge_graph() -> dict[str, dict]:
    """Best-effort load of the production knowledge graph for reasoning_types
    and is_broad_overlay-future-flag lookup. Returns empty if unavailable —
    proxies that need it gracefully report missing values."""
    for candidate in (SKILL_DIR / "data" / "knowledge_graph.json", SKILL_DIR / "build" / "knowledge_graph.json"):
        if candidate.exists():
            try:
                kg = json.loads(candidate.read_text(encoding="utf-8"))
                return kg.get("models", {}) or {}
            except Exception:
                continue
    return {}


# ---------------------------------------------------------------------------
# Per-anchor row construction
# ---------------------------------------------------------------------------


def _model_payload(models: dict[str, dict], mid: str) -> dict:
    p = models.get(mid)
    return p if isinstance(p, dict) else {}


def _is_broad_overlay(mid: str, models: dict[str, dict]) -> bool:
    """Locked: hardcoded _BROAD_OVERLAY_MODELS + optional substrate flag.
    NOT derived from reasoning_types."""
    if mid in _BROAD_OVERLAY_MODELS:
        return True
    payload = _model_payload(models, mid)
    return bool(payload.get("is_broad_overlay", False))


def _primary_reasoning_type(mid: str, models: dict[str, dict]) -> str:
    """Exploratory metadata — NOT used as broadness classifier."""
    types = _model_payload(models, mid).get("reasoning_types")
    if isinstance(types, list) and types and isinstance(types[0], str):
        return types[0].strip()
    return ""


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) >= 3}


def _quote_collision(quote: str, others: list[str]) -> int:
    """Count how many other quotes share substantial substring overlap (≥0.6
    token Jaccard or substring containment). Mirrors the verifier's
    _quotes_overlap heuristic."""
    if not quote:
        return 0
    qt = _tokenize(quote)
    n = 0
    for o in others:
        if not o or o == quote:
            continue
        if quote in o or o in quote:
            n += 1
            continue
        ot = _tokenize(o)
        if not qt or not ot:
            continue
        if len(qt & ot) / min(len(qt), len(ot)) >= 0.6:
            n += 1
    return n


def build_anchor_rows(
    case_id: str,
    embedding_mode: str,
    stability: dict,
    models: dict[str, dict],
) -> list[dict]:
    """One row per (run_id, model_id) where model_id appeared in either
    cheat_sheet.anchors OR companion_verification_accepted_before_cap on
    that run. Both labels are computed from the multi-run union.
    """
    run_ids: list[str] = stability.get("run_ids", []) or []
    if len(run_ids) < 2:
        return []

    # Multi-run anchor + accepted sets (for labels).
    anchor_per_run: list[set[str]] = [set(s) for s in (stability.get("lane2_anchors", {}) or {}).get("per_run", [])]
    accepted_per_run: list[set[str]] = [
        set(s) for s in (stability.get("lane2_accepted_before_cap", {}) or {}).get("per_run", [])
    ]
    # Stable labels: appeared in >=2/N runs.
    threshold = math.ceil(len(run_ids) * 2 / 3)  # >=2/3 runs

    def _stability_label(per_run_sets: list[set[str]], mid: str) -> bool:
        return sum(1 for s in per_run_sets if mid in s) >= threshold

    rows: list[dict] = []
    for ri, rid in enumerate(run_ids):
        # Per-run candidates + accepted + cheat-sheet anchors with full details
        result = load_per_run_result(rid)
        if not result:
            continue
        summ = result.get("audit_summary", {}) or {}
        candidates = summ.get("companion_candidates", []) or []
        candidate_by_id: dict[str, dict] = {c.get("model_id", ""): c for c in candidates if c.get("model_id")}
        accepted_list = summ.get("companion_verification_accepted_before_cap", []) or []
        # Position in the accepted list (1-indexed).
        accepted_position: dict[str, int] = {}
        # Evidence quote per accepted model_id (we may have multiple positions; first wins)
        accepted_quote: dict[str, str] = {}
        all_quotes: list[str] = []
        for pos, a in enumerate(accepted_list, start=1):
            mid = a.get("model_id", "")
            if not mid:
                continue
            if mid not in accepted_position:
                accepted_position[mid] = pos
            q = a.get("evidence_quote", "") or ""
            if mid not in accepted_quote:
                accepted_quote[mid] = q
            if q:
                all_quotes.append(q)

        # Cheat-sheet anchors: the consumer surface.
        cs = result.get("companion_cheat_sheet", {}) or {}
        anchor_ids: set[str] = {
            a.get("model_id", "") for a in (cs.get("anchors", []) or []) if a.get("model_id")
        }

        # Build rows for any model_id in EITHER anchor_ids OR accepted_position
        # (anchor-instance row regardless of which surface it lives on, so we
        # can compute proxies for accepted-but-not-surfaced models too).
        seen_ids = anchor_ids | set(accepted_position.keys())
        for mid in sorted(seen_ids):
            cand = candidate_by_id.get(mid, {})
            quote = accepted_quote.get(mid, "")
            other_quotes = [q for k, q in accepted_quote.items() if k != mid and q]
            row = {
                "case_id": case_id,
                "embedding_mode": embedding_mode,
                "run_id": rid,
                "run_index": ri,
                "model_id": mid,
                # Labels
                "stable_anchor": _stability_label(anchor_per_run, mid),
                "stable_accepted": _stability_label(accepted_per_run, mid),
                "appeared_in_anchors_this_run": mid in anchor_ids,
                "appeared_in_accepted_this_run": mid in accepted_position,
                # Proxies — gate-eligible
                "is_broad_overlay": _is_broad_overlay(mid, models),
                "final_rank": cand.get("final_rank") if isinstance(cand.get("final_rank"), int) else None,
                "final_rank_bucket": _bucket_rank(cand.get("final_rank")),
                "evidence_quote_length": len(quote) if quote else None,
                "quote_collision_count": _quote_collision(quote, other_quotes) if quote else None,
                "accepted_before_cap_position": accepted_position.get(mid),
                "recall_source": cand.get("recall_source") or None,
                # Exploratory metadata
                "primary_reasoning_type": _primary_reasoning_type(mid, models) or None,
                "all_reasoning_types": _model_payload(models, mid).get("reasoning_types") or None,
                "model_display_name": _model_payload(models, mid).get("display_name") or mid,
            }
            rows.append(row)
    return rows


def _bucket_rank(rank) -> str | None:
    if not isinstance(rank, int):
        return None
    if rank <= 10:
        return "top10"
    if rank <= 20:
        return "top20"
    if rank <= 30:
        return "top30"
    return "tail"


# ---------------------------------------------------------------------------
# AUROC + threshold metrics
# ---------------------------------------------------------------------------


def _auroc(scores: list[float], labels: list[bool]) -> float | None:
    """Wilcoxon-Mann-Whitney AUROC. Returns None on degenerate input.

    Higher score should predict True label. Ties get half-credit.
    """
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    n = len(pos) * len(neg)
    if n == 0:
        return None
    wins = 0.0
    for ps in pos:
        for ns in neg:
            if ps > ns:
                wins += 1
            elif ps == ns:
                wins += 0.5
    return wins / n


def _threshold_precision_recall(
    scores: list[float], labels: list[bool], threshold: float, direction: str = "ge"
) -> tuple[float, float]:
    """Precision/recall for the rule (score >= threshold) when direction='ge';
    (score <= threshold) when direction='le'. Returns (precision, recall)."""
    if direction == "ge":
        predictions = [s >= threshold for s in scores]
    else:
        predictions = [s <= threshold for s in scores]
    tp = sum(1 for p, l in zip(predictions, labels) if p and l)
    fp = sum(1 for p, l in zip(predictions, labels) if p and not l)
    fn = sum(1 for p, l in zip(predictions, labels) if not p and l)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return precision, recall


def _per_case_auroc(rows: list[dict], score_key: str, label_key: str = "stable_anchor") -> dict[str, float | None]:
    """AUROC per (case_id, embedding_mode) group."""
    by_group: dict[tuple[str, str], list[tuple[float, bool]]] = defaultdict(list)
    for r in rows:
        v = r.get(score_key)
        l = r.get(label_key)
        if v is None or l is None:
            continue
        if isinstance(v, bool):
            v = 1.0 if v else 0.0
        elif not isinstance(v, (int, float)):
            continue
        by_group[(r["case_id"], r["embedding_mode"])].append((float(v), bool(l)))
    out: dict[str, float | None] = {}
    for (case, mode), scores_labels in sorted(by_group.items()):
        if not scores_labels:
            out[f"{case}/{mode}"] = None
            continue
        scores = [s for s, _ in scores_labels]
        labels = [l for _, l in scores_labels]
        out[f"{case}/{mode}"] = _auroc(scores, labels)
    return out


# ---------------------------------------------------------------------------
# Proxy evaluation
# ---------------------------------------------------------------------------


def _coverage(rows: list[dict], proxy_key: str) -> float:
    """Fraction of rows where the proxy has a non-null value."""
    if not rows:
        return 0.0
    return sum(1 for r in rows if r.get(proxy_key) is not None) / len(rows)


def _binary_positive_rate(rows: list[dict], proxy_key: str) -> float:
    """For binary proxies: fraction of computable rows where the value is True."""
    computable = [r for r in rows if r.get(proxy_key) is not None]
    if not computable:
        return 0.0
    return sum(1 for r in computable if r.get(proxy_key) is True) / len(computable)


def _scores_for_auroc(rows: list[dict], proxy_key: str, direction: str) -> list[float]:
    """Convert proxy values to scores where higher = predicting True label."""
    out: list[float] = []
    for r in rows:
        v = r.get(proxy_key)
        if v is None:
            continue
        if isinstance(v, bool):
            out.append(1.0 if v else 0.0)
        elif isinstance(v, (int, float)):
            out.append(float(v) if direction == "higher_is_stable" else -float(v))
        else:
            continue
    return out


def _labels_for_auroc(rows: list[dict], proxy_key: str, label_key: str) -> list[bool]:
    out: list[bool] = []
    for r in rows:
        v = r.get(proxy_key)
        if v is None:
            continue
        if isinstance(v, (bool, int, float)):
            out.append(bool(r.get(label_key)))
    return out


PROXY_DIRECTIONS = {
    # higher_is_stable: high values predict stable_anchor=True
    # lower_is_stable: low values predict stable_anchor=True
    # binary_true_predicts_unstable: True predicts stable_anchor=False (negate semantics in report)
    "is_broad_overlay":              "binary_true_predicts_unstable",
    "final_rank":                    "lower_is_stable",
    "evidence_quote_length":         "higher_is_stable",  # exploratory; weak prior
    "quote_collision_count":         "lower_is_stable",   # exploratory; collisions = ambiguity
    "accepted_before_cap_position":  "lower_is_stable",
}


def evaluate_proxy(
    rows: list[dict],
    proxy_key: str,
    label_key: str = "stable_anchor",
) -> dict:
    """Full evaluation: coverage, AUROC pooled + per-case, threshold rule, verdict."""
    direction = PROXY_DIRECTIONS.get(proxy_key, "higher_is_stable")
    coverage = _coverage(rows, proxy_key)

    # For binary, also compute positive rate.
    sample_value = next((r.get(proxy_key) for r in rows if r.get(proxy_key) is not None), None)
    is_binary = isinstance(sample_value, bool)
    is_categorical = isinstance(sample_value, str)

    metrics: dict[str, Any] = {
        "proxy": proxy_key,
        "direction": direction,
        "coverage": round(coverage, 4),
        "is_binary": is_binary,
        "is_categorical": is_categorical,
    }
    if is_binary:
        metrics["positive_rate"] = round(_binary_positive_rate(rows, proxy_key), 4)

    # Categorical proxies skip AUROC (no natural ordering).
    if is_categorical:
        from collections import Counter
        dist = Counter(r.get(proxy_key) for r in rows if r.get(proxy_key) is not None)
        metrics["distribution"] = dict(dist)
        metrics["verdict"] = _categorical_verdict(coverage, dist)
        metrics["pooled_auroc"] = None
        metrics["per_case_auroc"] = {}
        return metrics

    # Coverage / positive-rate eligibility checks (pre-AUROC).
    if coverage < 0.20:
        metrics["pooled_auroc"] = None
        metrics["per_case_auroc"] = {}
        metrics["verdict"] = "COVERAGE_INELIGIBLE"
        metrics["verdict_reason"] = f"coverage {coverage:.2f} < 0.20"
        return metrics
    if is_binary:
        pr = metrics["positive_rate"]
        if pr < 0.05 or pr > 0.95:
            metrics["pooled_auroc"] = None
            metrics["per_case_auroc"] = {}
            severity = "sparse" if pr < 0.05 else "saturated"
            metrics["verdict"] = "COVERAGE_INELIGIBLE"
            metrics["verdict_reason"] = f"positive_rate {pr:.2f} {severity} (outside [0.05, 0.95])"
            return metrics

    # AUROC: scores oriented so higher predicts True label.
    scores = _scores_for_auroc(rows, proxy_key, "higher_is_stable" if direction == "higher_is_stable" else "lower_is_stable")
    labels = _labels_for_auroc(rows, proxy_key, label_key)
    if direction == "binary_true_predicts_unstable":
        # Invert: True (broad) predicts stable_anchor=False, so flip the label
        # we test against. We test against ¬stable_anchor — i.e. the proxy is
        # higher (1.0) for unstable.
        labels = [not l for l in labels]

    pooled = _auroc(scores, labels)
    metrics["pooled_auroc"] = round(pooled, 4) if pooled is not None else None

    # Per-case AUROC
    per_case_keyed = _per_case_auroc(rows, proxy_key, label_key)
    if direction == "binary_true_predicts_unstable":
        # Invert per-case as well by recomputing
        per_case_keyed = {}
        by_group: dict[tuple[str, str], list[tuple[float, bool]]] = defaultdict(list)
        for r in rows:
            v = r.get(proxy_key)
            if v is None:
                continue
            score = 1.0 if v else 0.0
            label = not bool(r.get(label_key))
            by_group[(r["case_id"], r["embedding_mode"])].append((score, label))
        for (case, mode), sl in sorted(by_group.items()):
            scores_g = [s for s, _ in sl]
            labels_g = [l for _, l in sl]
            per_case_keyed[f"{case}/{mode}"] = _auroc(scores_g, labels_g)
    metrics["per_case_auroc"] = {k: (round(v, 4) if v is not None else None) for k, v in per_case_keyed.items()}

    # Direction consistency: count groups where AUROC > 0.50 (predicting in
    # the expected direction). Need >= 6 of 8 per locked gate.
    measurable = [v for v in per_case_keyed.values() if v is not None]
    direction_consistent = sum(1 for v in measurable if v > 0.50)
    metrics["direction_consistent_groups"] = direction_consistent
    metrics["measurable_groups"] = len(measurable)

    # Threshold rule. Critical: test against the ORIGINAL proxy values, not
    # the AUROC-inverted scores. The threshold semantics are "predict stable=True
    # when proxy meets the rule (e.g. final_rank ≤ 10)" — so labels for the
    # threshold check stay as-is (no inversion), and we feed raw proxy values.
    raw_proxy_values: list[float] = []
    raw_proxy_labels: list[bool] = []
    for r in rows:
        v = r.get(proxy_key)
        if v is None:
            continue
        if isinstance(v, bool):
            raw_proxy_values.append(1.0 if v else 0.0)
        elif isinstance(v, (int, float)):
            raw_proxy_values.append(float(v))
        else:
            continue
        raw_proxy_labels.append(bool(r.get(label_key)))
    if direction == "binary_true_predicts_unstable":
        # The threshold test "is_broad_overlay >= 0.5 predicts unstable" so flip the label.
        raw_proxy_labels = [not l for l in raw_proxy_labels]
    thresholds = _suggest_thresholds(rows, proxy_key, direction)
    threshold_results = []
    for t, t_dir in thresholds:
        precision, recall = _threshold_precision_recall(raw_proxy_values, raw_proxy_labels, t, t_dir)
        threshold_results.append({
            "threshold": t,
            "direction": t_dir,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
        })
    metrics["threshold_rules"] = threshold_results

    # Marcus stress test
    marcus_aurocs = [v for k, v in per_case_keyed.items() if k.startswith("marcus") and v is not None]
    metrics["marcus_auroc"] = round(min(marcus_aurocs), 4) if marcus_aurocs else None
    if pooled is not None and metrics["marcus_auroc"] is not None:
        marcus_gap = pooled - metrics["marcus_auroc"]
        metrics["marcus_gap_vs_pooled"] = round(marcus_gap, 4)
        metrics["marcus_collapse"] = marcus_gap >= 0.15
    else:
        metrics["marcus_gap_vs_pooled"] = None
        metrics["marcus_collapse"] = None

    # D0 verdict
    metrics["verdict"], metrics["verdict_reason"] = _gate_verdict(metrics)
    return metrics


def _suggest_thresholds(rows: list[dict], proxy_key: str, direction: str) -> list[tuple[float, str]]:
    """Pick a small set of threshold candidates per proxy. Returns
    [(threshold_value, direction_for_threshold_check), ...]. Direction here
    is "ge" (predicts True if score >= threshold) or "le" (score <= threshold)."""
    if proxy_key == "is_broad_overlay":
        # Binary: positive=True predicts unstable, so the "rule" is
        # is_broad_overlay==True -> not stable_anchor.
        return [(0.5, "ge")]
    if proxy_key == "final_rank":
        return [(10, "le"), (20, "le"), (30, "le")]
    if proxy_key == "accepted_before_cap_position":
        return [(2, "le"), (3, "le"), (5, "le")]
    if proxy_key == "evidence_quote_length":
        return [(40, "ge"), (80, "ge"), (120, "ge")]
    if proxy_key == "quote_collision_count":
        return [(0, "le"), (1, "le")]
    return []


def _gate_verdict(metrics: dict) -> tuple[str, str]:
    """Apply D0 gates from the design conversation. Returns (verdict, reason)."""
    pooled = metrics.get("pooled_auroc")
    if pooled is None:
        return "NO_SIGNAL", "AUROC undefined (degenerate label distribution)"
    direction_groups = metrics.get("direction_consistent_groups", 0)
    measurable = metrics.get("measurable_groups", 0)
    marcus_collapse = metrics.get("marcus_collapse")
    threshold_rules = metrics.get("threshold_rules", []) or []
    best_p, best_r = 0.0, 0.0
    for tr in threshold_rules:
        if tr["precision"] >= 0.75 and tr["recall"] >= 0.50:
            best_p = max(best_p, tr["precision"])
            best_r = max(best_r, tr["recall"])

    pass_auroc = pooled >= 0.70
    pass_direction = measurable >= 6 and direction_groups >= 6
    pass_threshold = best_p >= 0.75 and best_r >= 0.50
    pass_marcus = (marcus_collapse is not True)

    if pass_auroc and pass_direction and pass_threshold and pass_marcus:
        return "PROMOTABLE", f"AUROC {pooled:.2f}; direction {direction_groups}/{measurable}; threshold p≥0.75/r≥0.50 met; Marcus OK"
    # If AUROC is clearly above 0.55 in the right direction but below the 0.70 gate, flag as wording-only evidence
    if pooled >= 0.55:
        reason = (
            f"AUROC {pooled:.2f} (gate 0.70); direction {direction_groups}/{measurable}; "
            f"threshold best precision/recall {best_p:.2f}/{best_r:.2f}; "
            f"Marcus collapse: {marcus_collapse}"
        )
        return "WORDING_ONLY_EVIDENCE", reason
    return "NO_SIGNAL", f"AUROC {pooled:.2f} below directional threshold (0.55)"


def _categorical_verdict(coverage: float, distribution: dict[str, int]) -> str:
    if coverage < 0.20:
        return "COVERAGE_INELIGIBLE"
    nonzero = [c for c in distribution.values() if c > 0]
    if len(nonzero) < 2:
        return "NO_SIGNAL"
    return "EXPLORATORY"


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def render_report(rows: list[dict], evaluations: list[dict], generated_at: str) -> str:
    out: list[str] = []
    out.append("# Lane 2 Path D — proxy validation report")
    out.append("")
    out.append(f"Generated: {generated_at}")
    out.append(f"Rows: {len(rows)} anchor-instances across {len({(r['case_id'], r['embedding_mode']) for r in rows})} case-mode groups, "
               f"{len({r['run_id'] for r in rows})} runs, "
               f"{len({r['model_id'] for r in rows})} unique models.")
    out.append("")
    # Label balance
    n_stable = sum(1 for r in rows if r.get("stable_anchor"))
    n_total = len(rows)
    out.append(f"Label balance (stable_anchor): {n_stable}/{n_total} = {100*n_stable/max(1,n_total):.1f}%")
    n_stable_acc = sum(1 for r in rows if r.get("stable_accepted"))
    out.append(f"Label balance (stable_accepted): {n_stable_acc}/{n_total} = {100*n_stable_acc/max(1,n_total):.1f}%")
    out.append("")

    out.append("## D0 verdicts")
    out.append("")
    out.append("| Proxy | Verdict | Pooled AUROC | Coverage | Pos rate | Direction OK | Marcus collapse | Reason |")
    out.append("|---|---|---|---|---|---|---|---|")
    for ev in evaluations:
        cov = ev.get("coverage")
        pr = ev.get("positive_rate")
        marcus_coll = ev.get("marcus_collapse")
        marcus_str = "—" if marcus_coll is None else ("YES" if marcus_coll else "no")
        direction_str = (
            f"{ev.get('direction_consistent_groups', '—')}/{ev.get('measurable_groups', '—')}"
            if ev.get("measurable_groups") else "—"
        )
        pooled = ev.get("pooled_auroc")
        out.append(
            f"| `{ev['proxy']}` | **{ev['verdict']}** | "
            f"{pooled if pooled is not None else '—'} | "
            f"{cov if cov is not None else '—'} | "
            f"{pr if pr is not None else '—'} | "
            f"{direction_str} | {marcus_str} | {ev.get('verdict_reason', '')} |"
        )
    out.append("")

    out.append("## Per-case AUROC (conversation-independence diagnostic)")
    out.append("")
    out.append("A proxy with similar AUROCs across all case-modes is conversation-independent. Wide swings = case-coupled.")
    out.append("")
    case_modes = sorted({k for ev in evaluations for k in (ev.get("per_case_auroc") or {})})
    if case_modes:
        out.append("| Proxy | " + " | ".join(case_modes) + " |")
        out.append("|" + "|".join(["---"] * (1 + len(case_modes))) + "|")
        for ev in evaluations:
            if ev.get("verdict") == "COVERAGE_INELIGIBLE":
                continue
            row = [f"`{ev['proxy']}`"]
            pca = ev.get("per_case_auroc") or {}
            for cm in case_modes:
                v = pca.get(cm)
                row.append(f"{v:.2f}" if isinstance(v, (int, float)) else "—")
            out.append("| " + " | ".join(row) + " |")
        out.append("")

    out.append("## Threshold rules per proxy")
    out.append("")
    for ev in evaluations:
        if ev.get("is_categorical") or ev.get("verdict") == "COVERAGE_INELIGIBLE":
            continue
        trs = ev.get("threshold_rules") or []
        if not trs:
            continue
        out.append(f"### `{ev['proxy']}`")
        out.append("")
        out.append("| Threshold | Direction | Precision | Recall |")
        out.append("|---|---|---|---|")
        for tr in trs:
            out.append(f"| {tr['threshold']} | `{tr['direction']}` | {tr['precision']:.2f} | {tr['recall']:.2f} |")
        out.append("")

    out.append("## Path D D1 routing decision")
    out.append("")
    promotable = [ev["proxy"] for ev in evaluations if ev["verdict"] == "PROMOTABLE"]
    wording_evidence = [ev["proxy"] for ev in evaluations if ev["verdict"] == "WORDING_ONLY_EVIDENCE"]
    if promotable:
        out.append(f"**At least one proxy promotable: {promotable}.** Path D D1 may proceed with tiered Step 6 anchor metadata.")
    elif wording_evidence:
        out.append(f"**No proxy clears D0 gates.** Wording-only Step 6 changes supported by directional evidence from: {wording_evidence}.")
    else:
        out.append("**No proxy clears D0 gates and none provides directional evidence.** Path D D1 should proceed with wording-only Step 6 changes WITHOUT proxy-driven differentiation.")
    out.append("")
    out.append("## Methodology")
    out.append("")
    out.append("- Inputs: 8 baseline campaigns under `research/stability-runs/*-lane2-{on,off}-2026-04-26/`. "
               "Per-run details from `/tmp/lolla_*_result.json` (still present at audit time).")
    out.append(f"- Stable label threshold: appeared in ≥2 of 3 runs per case-mode.")
    out.append(f"- `is_broad_overlay` source: `engine.system_b.companion_routing._BROAD_OVERLAY_MODELS` "
               f"({len(_BROAD_OVERLAY_MODELS)} models) plus optional `model_payload.is_broad_overlay` flag (forward-compat).")
    out.append("- AUROC: Wilcoxon-Mann-Whitney with tie correction.")
    out.append("- Marcus stress: per-case Marcus AUROC must be within 0.15 of pooled AUROC, else verdict carries explicit caveat.")
    out.append("- No LLM calls.")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument(
        "--stability-root",
        default=str(SKILL_DIR / "research" / "stability-runs"),
        help="Root of stability-runs directory.",
    )
    ap.add_argument(
        "--output-dir",
        default=str(SKILL_DIR / "research" / "stability-runs" / "lane2-pathD-proxy-validation-2026-04-26"),
        help="Where to write report.md and proxy_rows.json.",
    )
    args = ap.parse_args()

    stability_root = Path(args.stability_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Stability root: {stability_root}", file=sys.stderr)
    runs = discover_baseline_runs(stability_root)
    print(f"Discovered {len(runs)} baseline campaigns:", file=sys.stderr)
    for case, mode, _ in runs:
        print(f"  {case} {mode}", file=sys.stderr)

    models = load_knowledge_graph()
    print(f"Loaded {len(models)} models from knowledge_graph", file=sys.stderr)

    rows: list[dict] = []
    for case_id, mode, stab_dir in runs:
        stability = json.loads((stab_dir / "stability.json").read_text(encoding="utf-8"))
        case_rows = build_anchor_rows(case_id, mode, stability, models)
        rows.extend(case_rows)
        print(f"  {case_id}/{mode}: {len(case_rows)} anchor-instance rows", file=sys.stderr)

    print(f"\nTotal rows: {len(rows)}", file=sys.stderr)

    # Evaluate each proxy
    proxies_to_evaluate = [
        "is_broad_overlay",
        "final_rank",
        "evidence_quote_length",
        "quote_collision_count",
        "accepted_before_cap_position",
        "recall_source",
    ]
    evaluations = [evaluate_proxy(rows, p) for p in proxies_to_evaluate]

    # Write outputs
    rows_path = output_dir / "proxy_rows.json"
    rows_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"\nWrote {rows_path} ({len(rows)} rows)", file=sys.stderr)

    import datetime as _dt
    generated_at = _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_md = render_report(rows, evaluations, generated_at)
    report_path = output_dir / "report.md"
    report_path.write_text(report_md, encoding="utf-8")
    print(f"Wrote {report_path}", file=sys.stderr)

    # Brief stdout summary
    print("\n=== verdicts ===", file=sys.stderr)
    for ev in evaluations:
        print(f"  {ev['proxy']:35} {ev['verdict']:25} pooled_AUROC={ev.get('pooled_auroc')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
