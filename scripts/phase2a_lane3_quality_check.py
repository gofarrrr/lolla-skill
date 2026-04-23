#!/usr/bin/env python3
"""Phase 2a Lane 3 quality check — old-path vs new-path on the 10-case corpus.

Runs `run_extract.py` once per case (shared input), then runs `run_pipeline.py`
N times on the legacy path and N times on the --new-contract path. Parses
`frame_pressure_card` from each result and computes structural metrics.

Evidence output: markdown report with per-case tables + aggregate summary +
per-case regression flags, saved to a timestamped directory under
`research/test-cases/phase2a-lane3-equivalence-<YYYY-MM-DD>/`.

Usage (dry-run, one case N=1 to verify plumbing):
    python3 scripts/phase2a_lane3_quality_check.py --n 1 --cases oncologist

Usage (full measurement, N=3 across all 10 cases — costs ~$3-9 of API time):
    python3 scripts/phase2a_lane3_quality_check.py --n 3

Why shell-out (not in-process): running through the CLI verifies that
`--new-contract` dispatches correctly end-to-end, which is the actual user
path. Matches what PR 2a ships. Subprocess overhead is negligible vs the
30-60s per pipeline run.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = REPO_ROOT / "research" / "test-cases"
DEFAULT_OUTPUT_PARENT = REPO_ROOT / "research" / "test-cases"


@dataclass(frozen=True)
class RunMetrics:
    case: str
    path_label: str  # "old" | "new"
    run_index: int
    frame_elements_count: int
    frame_elements_type_counts: dict[str, int]
    dropped_frame_elements_count: int
    dropped_drop_reasons: dict[str, int]
    reframings_count: int
    reframings_move_type_counts: dict[str, int]
    error: str | None = None


@dataclass
class CaseMetrics:
    case: str
    old_runs: list[RunMetrics] = field(default_factory=list)
    new_runs: list[RunMetrics] = field(default_factory=list)


def _cases_from_corpus(subset: list[str] | None) -> list[tuple[str, Path]]:
    all_cases = sorted(CORPUS_DIR.glob("case_*_conversation.txt"))
    named = [(p.stem.replace("case_", "").replace("_conversation", ""), p) for p in all_cases]
    if subset is None:
        return named
    filtered = [(n, p) for (n, p) in named if n in subset]
    missing = set(subset) - {n for (n, _) in filtered}
    if missing:
        raise SystemExit(f"Unknown cases: {sorted(missing)}. Available: {[n for n, _ in named]}")
    return filtered


def _run_subprocess(cmd: list[str]) -> tuple[int, str, str]:
    """Run a subprocess; return (exit_code, stdout, stderr)."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def extract_once(conversation_path: Path, extraction_output: Path) -> None:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_extract.py"),
        "--conversation-file", str(conversation_path),
        "--output-file", str(extraction_output),
    ]
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        raise SystemExit(
            f"run_extract.py failed on {conversation_path.name} (exit {code}).\n"
            f"stdout: {out[:500]}\nstderr: {err[:500]}"
        )
    if not extraction_output.exists():
        raise SystemExit(f"run_extract.py returned 0 but {extraction_output} is absent")


def run_pipeline_once(
    extraction_path: Path,
    conversation_path: Path,
    result_output: Path,
    *,
    new_contract: bool,
) -> None:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--extraction-file", str(extraction_path),
        "--conversation-file", str(conversation_path),
        "--output-file", str(result_output),
        "--skip-revision",
    ]
    if new_contract:
        cmd.append("--new-contract")
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        raise SystemExit(
            f"run_pipeline.py failed ({'new' if new_contract else 'old'}-path) on "
            f"{conversation_path.name} (exit {code}).\nstdout: {out[:500]}\nstderr: {err[:500]}"
        )


def parse_frame_pressure_metrics(
    result_path: Path,
    case: str,
    path_label: str,
    run_index: int,
) -> RunMetrics:
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    card = payload.get("frame_pressure_card") or {}

    elements = card.get("frame_elements") or []
    dropped = card.get("dropped_frame_elements") or []
    reframings = card.get("reframings") or []

    element_type_counts = dict(Counter(
        el.get("element_type") or "unknown" for el in elements
    ))
    reframe_move_counts = dict(Counter(
        r.get("reframe_move_type") or "unknown" for r in reframings
    ))
    drop_reason_counts = dict(Counter(
        d.get("drop_reason") or "unknown" for d in dropped
    ))

    return RunMetrics(
        case=case,
        path_label=path_label,
        run_index=run_index,
        frame_elements_count=len(elements),
        frame_elements_type_counts=element_type_counts,
        dropped_frame_elements_count=len(dropped),
        dropped_drop_reasons=drop_reason_counts,
        reframings_count=len(reframings),
        reframings_move_type_counts=reframe_move_counts,
    )


def _drop_rate(runs: list[RunMetrics]) -> float:
    """Aggregate drop rate: total_dropped / (total_elements + total_dropped). 0 when both are 0."""
    total_el = sum(r.frame_elements_count for r in runs)
    total_dr = sum(r.dropped_frame_elements_count for r in runs)
    denom = total_el + total_dr
    return (total_dr / denom) if denom > 0 else 0.0


def _median(values: list[int]) -> float:
    return statistics.median(values) if values else 0.0


def _stddev(values: list[int]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def _regression_flags(case: CaseMetrics) -> list[str]:
    """Apply the Phase 2a per-case regression policy.

    Per `research/phase2-lane-migration-plan.md`:
    - Drop-rate threshold: new ≤ old within 5% tolerance band
    - frame_elements_count stability: within ±2 of old-path median
    - Negative-check trips: (a) old non-empty → new empty; (b) drop rate > 50%
      on a case where old was < 20%.
    """
    flags: list[str] = []
    old_drop = _drop_rate(case.old_runs)
    new_drop = _drop_rate(case.new_runs)
    if new_drop > old_drop + 0.05:
        flags.append(
            f"drop_rate_regression: new={new_drop:.3f} > old={old_drop:.3f} + 0.05 tolerance"
        )
    if new_drop > 0.5 and old_drop < 0.2:
        flags.append(
            f"NEGATIVE_CHECK_drop_rate_collapse: new={new_drop:.3f} > 0.5 while old={old_drop:.3f} < 0.2"
        )

    old_counts = [r.frame_elements_count for r in case.old_runs]
    new_counts = [r.frame_elements_count for r in case.new_runs]
    if old_counts and new_counts:
        old_med = _median(old_counts)
        for c in new_counts:
            if abs(c - old_med) > 2:
                flags.append(
                    f"frame_elements_count_drift: new run had {c} elements; old median {old_med} (>±2)"
                )
                break

    any_old_non_empty = any(r.frame_elements_count > 0 for r in case.old_runs)
    all_new_empty = all(r.frame_elements_count == 0 for r in case.new_runs)
    if any_old_non_empty and all_new_empty:
        flags.append("NEGATIVE_CHECK_empty_card: old path produced elements, new path always empty")

    return flags


def _aggregate_row(runs: list[RunMetrics]) -> dict[str, Any]:
    counts = [r.frame_elements_count for r in runs]
    drops = [r.dropped_frame_elements_count for r in runs]
    reframes = [r.reframings_count for r in runs]
    return {
        "n": len(runs),
        "elements_mean": round(statistics.mean(counts), 2) if counts else 0.0,
        "elements_stddev": round(_stddev(counts), 2),
        "dropped_mean": round(statistics.mean(drops), 2) if drops else 0.0,
        "dropped_stddev": round(_stddev(drops), 2),
        "drop_rate": round(_drop_rate(runs), 3),
        "reframings_mean": round(statistics.mean(reframes), 2) if reframes else 0.0,
    }


def _render_case_section(case: CaseMetrics, flags: list[str]) -> str:
    lines: list[str] = []
    lines.append(f"### `{case.case}`")
    lines.append("")
    if flags:
        lines.append("**Regression flags:**")
        for f in flags:
            lines.append(f"- `{f}`")
        lines.append("")

    old_agg = _aggregate_row(case.old_runs)
    new_agg = _aggregate_row(case.new_runs)
    lines.append("| path | n | elements (mean ± sd) | dropped (mean ± sd) | drop_rate | reframings (mean) |")
    lines.append("|------|---|----------------------|---------------------|-----------|-------------------|")
    lines.append(
        f"| old  | {old_agg['n']} | {old_agg['elements_mean']} ± {old_agg['elements_stddev']} | "
        f"{old_agg['dropped_mean']} ± {old_agg['dropped_stddev']} | {old_agg['drop_rate']} | "
        f"{old_agg['reframings_mean']} |"
    )
    lines.append(
        f"| new  | {new_agg['n']} | {new_agg['elements_mean']} ± {new_agg['elements_stddev']} | "
        f"{new_agg['dropped_mean']} ± {new_agg['dropped_stddev']} | {new_agg['drop_rate']} | "
        f"{new_agg['reframings_mean']} |"
    )
    lines.append("")

    # Per-run detail
    lines.append("<details><summary>per-run detail</summary>")
    lines.append("")
    lines.append("| path | run | elements | types | dropped | drop_reasons | reframings | move_types |")
    lines.append("|------|-----|----------|-------|---------|--------------|------------|------------|")
    for run in case.old_runs + case.new_runs:
        types_str = ", ".join(f"{k}:{v}" for k, v in sorted(run.frame_elements_type_counts.items())) or "-"
        reasons_str = ", ".join(f"{k}:{v}" for k, v in sorted(run.dropped_drop_reasons.items())) or "-"
        moves_str = ", ".join(f"{k}:{v}" for k, v in sorted(run.reframings_move_type_counts.items())) or "-"
        lines.append(
            f"| {run.path_label} | {run.run_index} | {run.frame_elements_count} | {types_str} | "
            f"{run.dropped_frame_elements_count} | {reasons_str} | {run.reframings_count} | {moves_str} |"
        )
    lines.append("")
    lines.append("</details>")
    lines.append("")
    return "\n".join(lines)


def render_report(
    all_cases: list[CaseMetrics],
    *,
    n: int,
    duration_seconds: float,
    dry_run: bool,
) -> str:
    lines: list[str] = []
    today = date.today().isoformat()
    lines.append(f"# Phase 2a Lane 3 quality check — {today}")
    lines.append("")
    if dry_run:
        lines.append("**Mode: DRY RUN** — N=1 on a subset of cases. Not an acceptance-gate run.")
        lines.append("")
    lines.append(
        f"Measurement: {len(all_cases)} case(s) × 2 paths × N={n} runs. "
        f"Wall time: {duration_seconds:.1f}s."
    )
    lines.append("")
    lines.append("**Metrics definitions:**")
    lines.append("- `elements`: `frame_pressure_card.frame_elements` count (0-5)")
    lines.append("- `dropped`: `frame_pressure_card.dropped_frame_elements` count — LOWER IS BETTER")
    lines.append("- `drop_rate`: dropped / (elements + dropped) aggregated across N runs for this path")
    lines.append("- `reframings`: `frame_pressure_card.reframings` count (0-2)")
    lines.append("")

    # Aggregate summary across all cases
    all_old = [r for c in all_cases for r in c.old_runs]
    all_new = [r for c in all_cases for r in c.new_runs]
    old_agg = _aggregate_row(all_old)
    new_agg = _aggregate_row(all_new)
    lines.append("## Aggregate across all cases")
    lines.append("")
    lines.append("| path | total runs | elements (mean) | dropped (mean) | drop_rate | reframings (mean) |")
    lines.append("|------|-----------|-----------------|----------------|-----------|-------------------|")
    lines.append(
        f"| old  | {old_agg['n']} | {old_agg['elements_mean']} | {old_agg['dropped_mean']} | "
        f"{old_agg['drop_rate']} | {old_agg['reframings_mean']} |"
    )
    lines.append(
        f"| new  | {new_agg['n']} | {new_agg['elements_mean']} | {new_agg['dropped_mean']} | "
        f"{new_agg['drop_rate']} | {new_agg['reframings_mean']} |"
    )
    lines.append("")

    # Gate check on aggregate
    drop_delta = new_agg["drop_rate"] - old_agg["drop_rate"]
    if drop_delta <= 0.05:
        lines.append(
            f"**Aggregate drop-rate gate:** PASS (new={new_agg['drop_rate']}, old={old_agg['drop_rate']}, "
            f"delta={drop_delta:+.3f}; ≤ 0.05 tolerance)."
        )
    else:
        lines.append(
            f"**Aggregate drop-rate gate:** FAIL (new={new_agg['drop_rate']}, old={old_agg['drop_rate']}, "
            f"delta={drop_delta:+.3f}; > 0.05 tolerance)."
        )
    lines.append("")

    # Per-case sections
    lines.append("## Per-case detail")
    lines.append("")
    regressions_total = 0
    for case in all_cases:
        flags = _regression_flags(case)
        if flags:
            regressions_total += 1
        lines.append(_render_case_section(case, flags))

    if regressions_total == 0:
        lines.append("**Per-case regression summary:** zero regressions flagged.")
    else:
        lines.append(
            f"**Per-case regression summary:** {regressions_total} of {len(all_cases)} cases regressed. "
            "Each must be diagnosed in the PR description before shipping (diagnosis-required policy)."
        )
    lines.append("")
    return "\n".join(lines)


def run_measurement(
    *,
    cases: list[tuple[str, Path]],
    output_dir: Path,
    n: int,
    dry_run: bool = False,
) -> tuple[list[CaseMetrics], float]:
    output_dir.mkdir(parents=True, exist_ok=True)
    scratch_dir = output_dir / "_scratch"
    scratch_dir.mkdir(exist_ok=True)

    started = time.monotonic()
    all_metrics: list[CaseMetrics] = []

    for case_name, conversation_path in cases:
        print(f"[{case_name}] extracting...", flush=True)
        extraction_path = scratch_dir / f"{case_name}_extraction.json"
        extract_once(conversation_path, extraction_path)

        case = CaseMetrics(case=case_name)
        for run_index in range(n):
            for label, new_contract in (("old", False), ("new", True)):
                out_path = scratch_dir / f"{case_name}_{label}_run{run_index}.json"
                print(f"[{case_name}] pipeline path={label} run={run_index}...", flush=True)
                run_pipeline_once(
                    extraction_path=extraction_path,
                    conversation_path=conversation_path,
                    result_output=out_path,
                    new_contract=new_contract,
                )
                metrics = parse_frame_pressure_metrics(out_path, case_name, label, run_index)
                if label == "old":
                    case.old_runs.append(metrics)
                else:
                    case.new_runs.append(metrics)
        all_metrics.append(case)

    duration = time.monotonic() - started
    report = render_report(all_metrics, n=n, duration_seconds=duration, dry_run=dry_run)
    (output_dir / "lane3-quality-report.md").write_text(report, encoding="utf-8")
    (output_dir / "raw-metrics.json").write_text(
        json.dumps(
            [
                {
                    "case": c.case,
                    "old_runs": [r.__dict__ for r in c.old_runs],
                    "new_runs": [r.__dict__ for r in c.new_runs],
                }
                for c in all_metrics
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    return all_metrics, duration


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=3, help="samples per path per case (default 3)")
    parser.add_argument(
        "--cases",
        nargs="*",
        default=None,
        help="subset of case names to run (default: all 10). E.g. --cases oncologist startup_pivot",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="report output dir (default: research/test-cases/phase2a-lane3-equivalence-<YYYY-MM-DD>)",
    )
    args = parser.parse_args()

    if args.output_dir is None:
        today = date.today().isoformat()
        args.output_dir = DEFAULT_OUTPUT_PARENT / f"phase2a-lane3-equivalence-{today}"

    cases = _cases_from_corpus(args.cases)
    if not cases:
        raise SystemExit("no cases resolved")

    dry_run = (args.n == 1 and len(cases) < 3)
    all_metrics, duration = run_measurement(
        cases=cases,
        output_dir=args.output_dir,
        n=args.n,
        dry_run=dry_run,
    )
    report_path = args.output_dir / "lane3-quality-report.md"
    print()
    print(f"Report: {report_path}")
    print(f"Wall time: {duration:.1f}s across {len(cases)} cases × 2 paths × N={args.n}.")

    # Exit 1 if any regression flags surfaced — helps catch failures in CI
    regressions = sum(1 for c in all_metrics if _regression_flags(c))
    return 0 if regressions == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
