#!/usr/bin/env python3
"""Phase 2b Lane 4 quality check over the conversation-first runtime.

Runs `run_extract.py` once per case (shared input), then runs `run_pipeline.py`
N times on the ConversationContext path. Parses `structural_coverage_card` from
each result and computes structural metrics.

Why shell-out (same rationale as Phase 2a): verifies the ConversationContext
runtime end-to-end, matching the actual user path. Subprocess overhead is
negligible vs the ~30-60s per pipeline run.

Usage (dry-run, one case N=1):
    python3 scripts/phase2b_lane4_quality_check.py --n 1 --cases oncologist

Usage (full measurement):
    python3 scripts/phase2b_lane4_quality_check.py --n 3

Phase 2b-specific notes:
- Lane 4 has NO evidence-substring validation (unlike Lane 3). There is no
  drop-rate metric here. Signal comes from: question_type stability across
  N runs; gap count / dimension detection differences between paths; and
  qualitative read of whether gap_questions reference the user's situation.
- Script is resilient to extraction + pipeline failures (same as 2a — one
  flaky run doesn't kill the whole measurement).
"""
from __future__ import annotations

import argparse
import json
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
    question_type: str
    dimensions_total: int
    dimensions_covered: int
    dimensions_gap: int
    gap_dimension_ids: tuple[str, ...]
    gap_questions_total: int  # sum of questions across all gaps
    gap_questions_per_dim: dict[str, int]
    error: str | None = None


@dataclass
class CaseMetrics:
    case: str
    old_runs: list[RunMetrics] = field(default_factory=list)
    new_runs: list[RunMetrics] = field(default_factory=list)


def _empty_metrics(case: str, path_label: str, run_index: int, error: str) -> RunMetrics:
    return RunMetrics(
        case=case,
        path_label=path_label,
        run_index=run_index,
        question_type="",
        dimensions_total=0,
        dimensions_covered=0,
        dimensions_gap=0,
        gap_dimension_ids=(),
        gap_questions_total=0,
        gap_questions_per_dim={},
        error=error,
    )


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
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def extract_once(conversation_path: Path, extraction_output: Path, *, resume: bool = True) -> str | None:
    """Extract; skip if output already exists and parses cleanly."""
    if resume and extraction_output.exists():
        try:
            payload = json.loads(extraction_output.read_text(encoding="utf-8"))
            if payload.get("status") == "ok":
                print(f"  [resume] extraction exists: {extraction_output.name}", flush=True)
                return None
        except json.JSONDecodeError:
            pass
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_extract.py"),
        "--conversation-file", str(conversation_path),
        "--output-file", str(extraction_output),
    ]
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        return f"run_extract.py exit={code} on {conversation_path.name}. stdout: {out.strip()[:400]!r} stderr: {err.strip()[:400]!r}"
    if not extraction_output.exists():
        return f"run_extract.py returned 0 but {extraction_output} is absent"
    try:
        payload = json.loads(extraction_output.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"extraction output not parseable: {exc}"
    if payload.get("status") != "ok":
        return f"extraction status={payload.get('status')!r}; error={payload.get('error','(none)')[:200]!r}"
    return None


def run_pipeline_once(
    extraction_path: Path,
    conversation_path: Path,
    result_output: Path,
    *,
    new_contract: bool,
    resume: bool = True,
) -> str | None:
    """Run pipeline once; return None on success, error string on failure."""
    if resume and result_output.exists():
        try:
            existing = json.loads(result_output.read_text(encoding="utf-8"))
            if "structural_coverage_card" in existing or existing.get("status") == "ok":
                print(f"  [resume] skip {result_output.name} (already present)", flush=True)
                return None
        except json.JSONDecodeError:
            pass
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--extraction-file", str(extraction_path),
        "--conversation-file", str(conversation_path),
        "--output-file", str(result_output),
        "--skip-revision",
    ]
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        return (
            f"run_pipeline.py exit={code} on {conversation_path.name} "
            f"({'new' if new_contract else 'old'}-path). "
            f"stdout: {out.strip()[:400]!r} stderr: {err.strip()[:400]!r}"
        )
    return None


def parse_structural_coverage_metrics(
    result_path: Path,
    case: str,
    path_label: str,
    run_index: int,
) -> RunMetrics:
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    card = payload.get("structural_coverage_card") or {}

    qtype = card.get("question_type") or ""
    dims = card.get("dimensions") or []
    gap_questions = card.get("gap_questions") or []

    covered = [d for d in dims if d.get("covered") is True]
    gaps = [d for d in dims if d.get("covered") is False]
    gap_dim_ids = tuple(sorted(d.get("dimension_id", "") for d in gaps))
    gq_per_dim: dict[str, int] = {}
    gq_total = 0
    for gq in gap_questions:
        dim_id = gq.get("dimension_id", "")
        qs = gq.get("questions") or []
        gq_per_dim[dim_id] = len(qs)
        gq_total += len(qs)

    return RunMetrics(
        case=case,
        path_label=path_label,
        run_index=run_index,
        question_type=qtype,
        dimensions_total=len(dims),
        dimensions_covered=len(covered),
        dimensions_gap=len(gaps),
        gap_dimension_ids=gap_dim_ids,
        gap_questions_total=gq_total,
        gap_questions_per_dim=gq_per_dim,
    )


def _qtype_stable(runs: list[RunMetrics]) -> bool:
    """True if all non-errored runs agree on question_type."""
    qtypes = {r.question_type for r in runs if not r.error and r.question_type}
    return len(qtypes) <= 1


def _regression_flags(case: CaseMetrics) -> list[str]:
    """Apply the Phase 2b regression policy.

    Criteria (from task file):
    - (a) non-empty StructuralCoverageCard on old → empty card on new (dimensions all empty)
    - (b) question_class disagreement across N=3 new-path runs (instability introduced)
    - (c) gap count reduces >= 2 on new vs old median (suppression of real structural gaps)
    """
    flags: list[str] = []

    any_old_dims = any(r.dimensions_total > 0 for r in case.old_runs if not r.error)
    all_new_empty = all(r.dimensions_total == 0 for r in case.new_runs if not r.error)
    if any_old_dims and all_new_empty:
        flags.append("NEGATIVE_CHECK_empty_card: old path produced dimensions; new path always empty")

    if not _qtype_stable(case.new_runs):
        nt = Counter(r.question_type for r in case.new_runs if not r.error)
        flags.append(f"NEGATIVE_CHECK_qtype_instability: new-path classification varied across runs ({dict(nt)})")

    old_gap_counts = [r.dimensions_gap for r in case.old_runs if not r.error]
    new_gap_counts = [r.dimensions_gap for r in case.new_runs if not r.error]
    if old_gap_counts and new_gap_counts:
        old_median = statistics.median(old_gap_counts)
        new_median = statistics.median(new_gap_counts)
        if old_median - new_median >= 2:
            flags.append(
                f"gap_count_regression: new-path median gaps={new_median} vs old={old_median} (dropped >=2)"
            )

    return flags


def _aggregate_row(runs: list[RunMetrics]) -> dict[str, Any]:
    valid = [r for r in runs if not r.error]
    dtotal = [r.dimensions_total for r in valid]
    dcov = [r.dimensions_covered for r in valid]
    dgap = [r.dimensions_gap for r in valid]
    gqtot = [r.gap_questions_total for r in valid]
    qtypes = Counter(r.question_type for r in valid if r.question_type)
    return {
        "n": len(valid),
        "errored": len(runs) - len(valid),
        "dimensions_total_mean": round(statistics.mean(dtotal), 2) if dtotal else 0.0,
        "dimensions_covered_mean": round(statistics.mean(dcov), 2) if dcov else 0.0,
        "dimensions_gap_mean": round(statistics.mean(dgap), 2) if dgap else 0.0,
        "gap_questions_total_mean": round(statistics.mean(gqtot), 2) if gqtot else 0.0,
        "question_types": dict(qtypes),
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
    lines.append("| path | n | qtype(s) | dims total | covered | gaps | gap_qs total |")
    lines.append("|------|---|----------|------------|---------|------|--------------|")
    for label, agg in (("old", old_agg), ("new", new_agg)):
        qts = ", ".join(f"{k}:{v}" for k, v in agg["question_types"].items()) or "-"
        lines.append(
            f"| {label} | {agg['n']} | {qts} | {agg['dimensions_total_mean']} | "
            f"{agg['dimensions_covered_mean']} | {agg['dimensions_gap_mean']} | "
            f"{agg['gap_questions_total_mean']} |"
        )
    lines.append("")

    # Per-run detail
    lines.append("<details><summary>per-run detail</summary>")
    lines.append("")
    lines.append("| path | run | qtype | dims | covered | gaps | gap_dim_ids | gap_qs |")
    lines.append("|------|-----|-------|------|---------|------|-------------|--------|")
    for run in case.old_runs + case.new_runs:
        if run.error:
            lines.append(f"| {run.path_label} | {run.run_index} | ERR | - | - | - | - | - |")
            continue
        gap_ids = ", ".join(run.gap_dimension_ids[:4]) + ("…" if len(run.gap_dimension_ids) > 4 else "")
        lines.append(
            f"| {run.path_label} | {run.run_index} | {run.question_type} | {run.dimensions_total} | "
            f"{run.dimensions_covered} | {run.dimensions_gap} | {gap_ids or '-'} | "
            f"{run.gap_questions_total} |"
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
    lines.append(f"# Phase 2b Lane 4 quality check — {today}")
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
    lines.append("- `qtype`: `structural_coverage_card.question_type` (4-class, per run)")
    lines.append("- `dims total`: total dimensions detected per run (covered + gaps)")
    lines.append("- `covered`: dimensions marked covered (the answer addressed them)")
    lines.append("- `gaps`: dimensions marked uncovered (potentially material gaps)")
    lines.append("- `gap_qs total`: sum of discovery questions generated across all gaps")
    lines.append("")
    lines.append(
        "**Note on Lane 4 signal shape:** Lane 4 has no evidence-substring validation, "
        "so there is no drop-rate metric (unlike Phase 2a's Lane 3 measurement). Quality "
        "evidence for this migration comes from per-case behavior comparison + qualitative "
        "read of whether gap_questions reference the user's actual situation particulars."
    )
    lines.append("")

    all_old = [r for c in all_cases for r in c.old_runs]
    all_new = [r for c in all_cases for r in c.new_runs]
    old_agg = _aggregate_row(all_old)
    new_agg = _aggregate_row(all_new)
    lines.append("## Aggregate across all cases")
    lines.append("")
    lines.append("| path | total runs | errored | dims (mean) | covered (mean) | gaps (mean) | gap_qs (mean) |")
    lines.append("|------|-----------|---------|-------------|----------------|-------------|---------------|")
    for label, agg in (("old", old_agg), ("new", new_agg)):
        lines.append(
            f"| {label} | {agg['n']} | {agg['errored']} | {agg['dimensions_total_mean']} | "
            f"{agg['dimensions_covered_mean']} | {agg['dimensions_gap_mean']} | "
            f"{agg['gap_questions_total_mean']} |"
        )
    lines.append("")
    lines.append(f"**question_type distribution (old):** {old_agg['question_types']}")
    lines.append("")
    lines.append(f"**question_type distribution (new):** {new_agg['question_types']}")
    lines.append("")

    regressions_total = 0
    for case in all_cases:
        flags = _regression_flags(case)
        if flags:
            regressions_total += 1
    if regressions_total == 0:
        lines.append("**Aggregate regression summary:** zero regressions flagged across all cases.")
    else:
        lines.append(
            f"**Aggregate regression summary:** {regressions_total} of {len(all_cases)} cases regressed. "
            "Each must be diagnosed in the PR description (diagnosis-required policy)."
        )
    lines.append("")

    lines.append("## Per-case detail")
    lines.append("")
    for case in all_cases:
        flags = _regression_flags(case)
        lines.append(_render_case_section(case, flags))

    errored_runs = [
        r for c in all_cases for r in (c.old_runs + c.new_runs) if r.error is not None
    ]
    if errored_runs:
        lines.append("")
        lines.append(f"## Errored runs ({len(errored_runs)} of {len(all_cases) * 2 * n})")
        lines.append("")
        lines.append("| case | path | run | error |")
        lines.append("|------|------|-----|-------|")
        for r in errored_runs:
            lines.append(f"| `{r.case}` | {r.path_label} | {r.run_index} | `{r.error[:150]}` |")
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
    errored_runs: list[str] = []

    for case_name, conversation_path in cases:
        print(f"[{case_name}] extracting...", flush=True)
        extraction_path = scratch_dir / f"{case_name}_extraction.json"
        extract_err = extract_once(conversation_path, extraction_path)
        if extract_err is not None:
            print(f"  [errored] extraction failed — skipping case's pipeline runs: {extract_err}", flush=True)
            errored_runs.append(f"[{case_name}] EXTRACTION: {extract_err}")
            case = CaseMetrics(case=case_name)
            for run_index in range(n):
                case.old_runs.append(_empty_metrics(case_name, "old", run_index, error=extract_err))
                case.new_runs.append(_empty_metrics(case_name, "new", run_index, error=extract_err))
            all_metrics.append(case)
            continue

        case = CaseMetrics(case=case_name)
        for run_index in range(n):
            for label, new_contract in (("old", False), ("new", True)):
                out_path = scratch_dir / f"{case_name}_{label}_run{run_index}.json"
                print(f"[{case_name}] pipeline path={label} run={run_index}...", flush=True)
                err = run_pipeline_once(
                    extraction_path=extraction_path,
                    conversation_path=conversation_path,
                    result_output=out_path,
                    new_contract=new_contract,
                )
                if err is not None:
                    print(f"  [errored] {err}", flush=True)
                    errored_runs.append(err)
                    metrics = _empty_metrics(case_name, label, run_index, error=err)
                else:
                    try:
                        metrics = parse_structural_coverage_metrics(out_path, case_name, label, run_index)
                    except (json.JSONDecodeError, KeyError) as parse_exc:
                        parse_err = f"parse_error on {out_path.name}: {parse_exc}"
                        print(f"  [errored] {parse_err}", flush=True)
                        errored_runs.append(parse_err)
                        metrics = _empty_metrics(case_name, label, run_index, error=parse_err)
                if label == "old":
                    case.old_runs.append(metrics)
                else:
                    case.new_runs.append(metrics)
        all_metrics.append(case)

    if errored_runs:
        print(f"\n[warning] {len(errored_runs)} runs errored — metrics for those runs are empty-stubbed.", flush=True)
        for e in errored_runs:
            print(f"  - {e}", flush=True)

    duration = time.monotonic() - started
    report = render_report(all_metrics, n=n, duration_seconds=duration, dry_run=dry_run)
    (output_dir / "lane4-quality-report.md").write_text(report, encoding="utf-8")
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
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--cases", nargs="*", default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    if args.output_dir is None:
        today = date.today().isoformat()
        args.output_dir = DEFAULT_OUTPUT_PARENT / f"phase2b-lane4-equivalence-{today}"

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
    report_path = args.output_dir / "lane4-quality-report.md"
    print()
    print(f"Report: {report_path}")
    print(f"Wall time: {duration:.1f}s across {len(cases)} cases × 2 paths × N={args.n}.")

    regressions = sum(1 for c in all_metrics if _regression_flags(c))
    return 0 if regressions == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
