"""Compact observability view of a Lolla pipeline run.

Reads a result JSON (the output of scripts/run_pipeline.py) and prints a
scannable summary of the observability surface: detection funnel, routing
traces including per-route tiebreaker status, delivery audit summary, and
card-level counts. Complementary to the Observatory UI — same data,
different surface, no browser required.

Usage:
    python3 scripts/inspect_run.py --result /tmp/lolla_<run_id>_result.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _short(text: str, limit: int = 80) -> str:
    text = (text or "").strip().replace("\n", " ")
    return text[:limit] + "\u2026" if len(text) > limit else text


def _fmt_trace(trace: dict | None, label: str) -> str:
    if trace is None:
        return f"  {label:<11} not traced"
    if not trace.get("attempted"):
        return f"  {label:<11} gate preconditions unmet"
    if trace.get("fired"):
        return (
            f"  {label:<11} FIRED  {trace.get('top1_model','?')} \u2192 {trace.get('top2_model','?')}  "
            f"(\u03b4={trace.get('delta',0):.4f}, max_sim={trace.get('max_sim',0):.2f})"
        )
    reason = trace.get("abort_reason", "unknown")
    extra = ""
    if reason == "outside_epsilon_window":
        extra = f"  (\u03b4={trace.get('delta',0):.4f})"
    elif reason == "below_noise_floor":
        extra = f"  (max_sim={trace.get('max_sim',0):.2f})"
    return f"  {label:<11} aborted \u00b7 {reason}{extra}"


def _card_count(name: str, data: dict) -> str:
    if name == "delta_card":
        return f"{len(data.get('top_findings', []) or [])} top findings"
    if name == "companion_cheat_sheet":
        return f"{len(data.get('anchors', []) or [])} anchors"
    if name == "frame_pressure_card":
        return f"{len(data.get('frame_elements', []) or [])} frame elements"
    if name == "structural_coverage_card":
        dims = data.get("dimensions", []) or []
        uncovered = [d for d in dims if not d.get("covered")]
        return f"{len(dims)} dimensions, {len(uncovered)} gaps"
    return "present"


def inspect(result_path: Path) -> None:
    with open(result_path) as f:
        result = json.load(f)

    audit = result.get("audit_summary", {}) or {}
    run_health = result.get("run_health", {}) or {}

    print("=" * 78)
    print(f"LOLLA RUN INSPECTION \u2014 {result_path.name}")
    print("=" * 78)

    # Overview
    print(f"\nQuery:  {_short(result.get('query', ''), 120)}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(
        f"Health: {run_health.get('overall', '?')}  "
        f"(substrate={run_health.get('substrate','?')}, "
        f"embeddings={run_health.get('embeddings','?')}, "
        f"tiebreaker={run_health.get('activation_tiebreaker','?')})"
    )
    issues = run_health.get("issues", []) or []
    warnings = run_health.get("warnings", []) or []
    if issues:
        print(f"Issues:  {', '.join(issues)}")
    if warnings:
        print(f"Warnings: {len(warnings)}")

    # Detection funnel
    triggered = audit.get("triggered_tendencies", []) or []
    deep_results = audit.get("deep_check_results", []) or []
    detected = [d for d in deep_results if d.get("detected")]
    routes = audit.get("routing_decisions", []) or []
    print("\n\u2500\u2500 Detection funnel \u2500\u2500")
    print(f"  Pass 1 triggered:     {len(triggered)}")
    print(f"  Pass 2 deep-checked:  {len(deep_results)}")
    print(f"  Pass 2 detected:      {len(detected)}")
    print(f"  Routed:               {len(routes)}")

    # Routing traces
    print(f"\n\u2500\u2500 Routing traces ({len(routes)} routes) \u2500\u2500")
    if not routes:
        print("  (no routes produced)")
    fired_count = 0
    aborted_reasons: dict[str, int] = {}
    for route in routes:
        tid = route.get("tendency_id", "?")
        primary = route.get("primary_model_id") or "\u2014"
        sub = route.get("sub_pattern") or "\u2014"
        print(f"\n  [{tid}]  primary={primary}  sub_pattern={sub}")
        for label in ("tiebreaker_supporting", "tiebreaker_risk"):
            trace = route.get(label)
            short_label = label.replace("tiebreaker_", "")
            print(_fmt_trace(trace, short_label))
            if isinstance(trace, dict) and trace.get("attempted"):
                if trace.get("fired"):
                    fired_count += 1
                else:
                    reason = trace.get("abort_reason", "unknown")
                    aborted_reasons[reason] = aborted_reasons.get(reason, 0) + 1

    if routes:
        total_attempts = fired_count + sum(aborted_reasons.values())
        print("\n  Tiebreaker summary:")
        print(f"    attempted: {total_attempts}")
        print(f"    fired:     {fired_count}")
        if aborted_reasons:
            print("    aborts:")
            for reason, count in sorted(aborted_reasons.items(), key=lambda x: -x[1]):
                print(f"      {reason}: {count}")

    # Delivery audit
    bs = result.get("bullshit_profile") or {}
    bs_summary = bs.get("summary", {}) or {}
    print("\n\u2500\u2500 Delivery audit \u2500\u2500")
    if bs_summary:
        print(f"  Passages audited:    {bs_summary.get('total_passages', 0)}")
        print(f"  Passages flagged:    {bs_summary.get('passages_with_detections', 0)}")
        print(f"  Clear detections:    {bs_summary.get('total_clear', 0)}")
        print(f"  Marginal detections: {bs_summary.get('total_marginal', 0)}")
    else:
        print("  (no delivery audit in this run)")

    # Cards
    print("\n\u2500\u2500 Cards \u2500\u2500")
    for card in ("delta_card", "companion_cheat_sheet", "frame_pressure_card", "structural_coverage_card"):
        data = result.get(card) or {}
        if data:
            print(f"  {card:<28} {_card_count(card, data)}")
        else:
            print(f"  {card:<28} \u2014")

    print("\n" + "=" * 78)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Print the observability surface of a Lolla run (detection funnel, routing traces, delivery audit)."
    )
    parser.add_argument("--result", type=Path, required=True, help="Path to a result JSON (from run_pipeline.py)")
    args = parser.parse_args()

    if not args.result.exists():
        print(f"ERROR: result file not found: {args.result}", file=sys.stderr)
        return 1

    inspect(args.result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
