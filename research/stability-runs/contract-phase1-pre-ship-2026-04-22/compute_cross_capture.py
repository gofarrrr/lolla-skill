#!/usr/bin/env python3
"""Pre-ship cross-capture baseline: compute drift metrics across 9 Marcus
extractions produced by the current extractor on main.

Reuses compute_extraction_drift + render_drift_markdown from scripts/stability_check.py
as a library. Writes drift.json + drift.md to cross-capture/.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from stability_check import (  # noqa: E402
    compute_extraction_drift,
    render_drift_markdown,
    _load_extraction,
    _run_id_from_extraction_path,
)


def main() -> int:
    cross_dir = HERE / "cross-capture"
    paths = sorted(cross_dir.glob("extraction_*.json"))
    if len(paths) != 9:
        print(f"Expected 9 extraction files, found {len(paths)}", file=sys.stderr)
        return 1

    extractions = [(_run_id_from_extraction_path(p), _load_extraction(p)) for p in paths]
    drift = compute_extraction_drift(extractions)

    (cross_dir / "drift.json").write_text(json.dumps(drift, indent=2))
    generated_at = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # render_drift_markdown expects a conversation path for its header; pass the
    # first capture path as a stand-in since this report is cross-capture, not
    # single-conversation.
    stub_conv = SKILL_ROOT / "tmp_placeholder"  # not read, just displayed
    md = render_drift_markdown(drift, "contract-phase1-pre-ship-cross", generated_at, stub_conv)
    (cross_dir / "drift.md").write_text(md)

    # Terminal summary
    print(f"Cross-capture drift: N={drift['n_runs']} extractions")
    agg = drift.get("aggregate", {}) or {}
    for field in ("decision_situation", "original_framing", "synthesized_position"):
        a = agg.get(field, {})
        print(f"  {field:22s} similarity mean={a.get('mean_similarity', 0):.3f} "
              f"min={a.get('min_similarity', 0):.3f}")
    for field in ("live_constraints", "reasoning_passages", "dropped_threads"):
        a = agg.get(field, {})
        print(f"  {field:22s} jaccard    mean={a.get('mean_jaccard', 0):.3f} "
              f"min={a.get('min_jaccard', 0):.3f}")
    print(f"  fabricated counts: {agg.get('fabricated_count_per_run', [])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
