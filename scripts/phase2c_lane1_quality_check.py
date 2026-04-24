#!/usr/bin/env python3
"""Phase 2c Lane 1 quality check — old-path vs new-path on the 10-case corpus.

Runs `run_extract.py` once per case (shared input), then runs `run_pipeline.py`
N times on the legacy path and N times on the --new-contract path. Parses
Lane 1 outputs (detected_tendencies, delta_card) AND downstream cascade
metrics (Lane 2/3/4 sizes) from each result.

Why both: Lane 1's output drives anti-echo in Lanes 2/3/4 and compound
detection. If Lane 1 migration shifts the selected_model_ids set, it can
cascade downstream. The measurement must capture both direct Lane 1 metrics
and the cascade metrics — per the phase2c plan's "downstream propagation"
requirement.

Usage (dry-run, one case N=1):
    python3 scripts/phase2c_lane1_quality_check.py --n 1 --cases oncologist

Usage (full measurement):
    python3 scripts/phase2c_lane1_quality_check.py --n 3

Phase 2c-specific notes:
- Lane 1 has no evidence-substring validation downstream (Pass 2
  specific_passage is not validated via fuzzy match), so there is no
  drop-rate metric. Signal comes from: triage-score stability; tendency
  detection stability; finding counts; compound-group formation; and
  downstream-lane cascade magnitude.
- 0-findings rate tracked per my addition: any new-path run producing
  zero detected_tendencies where old path produced some counts as an
  anomaly — report in the PR description.
- Script is resilient to extraction + pipeline failures (same as 2a/2b
  — one flaky run doesn't kill the whole measurement).
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
    # Lane 1 direct metrics
    detected_tendency_ids: tuple[str, ...]
    findings_count: int
    top_findings_count: int
    secondary_findings_count: int
    compound_groups_count: int
    selected_model_ids_count: int
    sub_patterns: tuple[str, ...]
    # Downstream cascade metrics
    companion_model_count: int
    frame_element_count: int
    structural_gap_count: int
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
        detected_tendency_ids=(),
        findings_count=0,
        top_findings_count=0,
        secondary_findings_count=0,
        compound_groups_count=0,
        selected_model_ids_count=0,
        sub_patterns=(),
        companion_model_count=0,
        frame_element_count=0,
        structural_gap_count=0,
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
    if resume and result_output.exists():
        try:
            existing = json.loads(result_output.read_text(encoding="utf-8"))
            # Lane 1 lives in delta_card + detected_tendencies — any of these
            # present implies a real pipeline result.
            if "delta_card" in existing or existing.get("status") == "ok":
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
    if new_contract:
        cmd.append("--new-contract")
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        return (
            f"run_pipeline.py exit={code} on {conversation_path.name} "
            f"({'new' if new_contract else 'old'}-path). "
            f"stdout: {out.strip()[:400]!r} stderr: {err.strip()[:400]!r}"
        )
    return None


def parse_lane1_metrics(
    result_path: Path,
    case: str,
    path_label: str,
    run_index: int,
) -> RunMetrics:
    payload = json.loads(result_path.read_text(encoding="utf-8"))

    detected = tuple(payload.get("detected_tendencies") or ())
    delta_card = payload.get("delta_card") or {}
    findings = delta_card.get("findings") or []
    top = delta_card.get("top_findings") or []
    secondary = delta_card.get("secondary_findings") or []
    compound_groups = delta_card.get("compound_groups") or []
    selected_model_ids = delta_card.get("selected_model_ids") or []
    sub_patterns = tuple(sorted(
        f.get("sub_pattern", "")
        for f in findings
        if f.get("sub_pattern")
    ))

    # Downstream cascade metrics.
    companion = payload.get("companion_card") or {}
    # Count model IDs that show up in the companion_card candidates / detected_models
    companion_models = companion.get("detected_models") or companion.get("candidates") or []
    companion_model_count = len(companion_models)

    frame_card = payload.get("frame_pressure_card") or {}
    frame_elements = frame_card.get("frame_elements") or []

    struct_card = payload.get("structural_coverage_card") or {}
    struct_dims = struct_card.get("dimensions") or []
    struct_gaps = [d for d in struct_dims if d.get("covered") is False]

    return RunMetrics(
        case=case,
        path_label=path_label,
        run_index=run_index,
        detected_tendency_ids=tuple(sorted(detected)),
        findings_count=len(findings),
        top_findings_count=len(top),
        secondary_findings_count=len(secondary),
        compound_groups_count=len(compound_groups),
        selected_model_ids_count=len(selected_model_ids),
        sub_patterns=sub_patterns,
        companion_model_count=companion_model_count,
        frame_element_count=len(frame_elements),
        structural_gap_count=len(struct_gaps),
    )


def _detected_stable(runs: list[RunMetrics], *, jaccard_floor: float = 0.50) -> bool:
    """True if detected_tendencies sets agree (Jaccard ≥ floor) across all
    non-errored runs. Instability threshold from task file: >50% disagreement."""
    sets = [set(r.detected_tendency_ids) for r in runs if not r.error]
    if len(sets) < 2:
        return True
    # pairwise min Jaccard
    min_j = 1.0
    for i, a in enumerate(sets):
        for b in sets[i + 1:]:
            union = a | b
            if not union:
                continue
            j = len(a & b) / len(union)
            min_j = min(min_j, j)
    return min_j >= jaccard_floor


def _regression_flags(case: CaseMetrics) -> list[str]:
    """Apply the Phase 2c regression policy (task file 8.0 negative-check).

    Criteria:
    - (a) findings_count > 0 on old → 0 on every new-path run (card emptied)
    - (b) detected_tendency_ids instability >50% disagreement across N=3 new-path runs
    - (c) compound group collapse (old had compound groups → new had zero across all runs)
    - (d) cascade: downstream lanes materially empty where old path had output
    """
    flags: list[str] = []

    old_findings = [r.findings_count for r in case.old_runs if not r.error]
    new_findings = [r.findings_count for r in case.new_runs if not r.error]

    if old_findings and max(old_findings) > 0 and new_findings and max(new_findings) == 0:
        flags.append("NEGATIVE_CHECK_empty_delta_card: old path produced findings; new path always empty")

    if not _detected_stable(case.new_runs):
        flags.append("NEGATIVE_CHECK_tendency_instability: new-path detected_tendency_ids disagree >50% across runs")

    old_compounds = [r.compound_groups_count for r in case.old_runs if not r.error]
    new_compounds = [r.compound_groups_count for r in case.new_runs if not r.error]
    if old_compounds and max(old_compounds) > 0 and new_compounds and max(new_compounds) == 0:
        flags.append(
            f"NEGATIVE_CHECK_compound_collapse: old max compound_groups={max(old_compounds)} → new always 0"
        )

    # Cascade: if any downstream lane was populated on old path and always empty on new path.
    for attr, label in (
        ("companion_model_count", "Lane 2 (companion)"),
        ("frame_element_count", "Lane 3 (frame pressure)"),
        ("structural_gap_count", "Lane 4 (structural coverage)"),
    ):
        old_vals = [getattr(r, attr) for r in case.old_runs if not r.error]
        new_vals = [getattr(r, attr) for r in case.new_runs if not r.error]
        if old_vals and new_vals and max(old_vals) > 0 and max(new_vals) == 0:
            flags.append(
                f"NEGATIVE_CHECK_cascade_empty: {label} populated on old (max={max(old_vals)}) → always 0 on new"
            )

    # Findings regression >= 2 (analog to 2b gap_count_regression)
    old_fmedian = statistics.median(old_findings) if old_findings else 0
    new_fmedian = statistics.median(new_findings) if new_findings else 0
    if old_fmedian - new_fmedian >= 2:
        flags.append(
            f"findings_count_regression: new-path median findings={new_fmedian} vs old={old_fmedian} (dropped ≥2)"
        )

    return flags


def _aggregate_row(runs: list[RunMetrics]) -> dict[str, Any]:
    valid = [r for r in runs if not r.error]
    return {
        "n": len(valid),
        "errored": len(runs) - len(valid),
        "detected_mean": round(statistics.mean([len(r.detected_tendency_ids) for r in valid]), 2) if valid else 0.0,
        "findings_mean": round(statistics.mean([r.findings_count for r in valid]), 2) if valid else 0.0,
        "top_findings_mean": round(statistics.mean([r.top_findings_count for r in valid]), 2) if valid else 0.0,
        "compounds_mean": round(statistics.mean([r.compound_groups_count for r in valid]), 2) if valid else 0.0,
        "selected_models_mean": round(statistics.mean([r.selected_model_ids_count for r in valid]), 2) if valid else 0.0,
        "zero_findings_runs": sum(1 for r in valid if r.findings_count == 0),
        "cascade_lane2_mean": round(statistics.mean([r.companion_model_count for r in valid]), 2) if valid else 0.0,
        "cascade_lane3_mean": round(statistics.mean([r.frame_element_count for r in valid]), 2) if valid else 0.0,
        "cascade_lane4_mean": round(statistics.mean([r.structural_gap_count for r in valid]), 2) if valid else 0.0,
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
    lines.append("| path | n | detected | findings | top | compounds | cascade L2/L3/L4 |")
    lines.append("|------|---|----------|----------|-----|-----------|-------------------|")
    for label, agg in (("old", old_agg), ("new", new_agg)):
        cascade = f"{agg['cascade_lane2_mean']} / {agg['cascade_lane3_mean']} / {agg['cascade_lane4_mean']}"
        lines.append(
            f"| {label} | {agg['n']} | {agg['detected_mean']} | {agg['findings_mean']} | "
            f"{agg['top_findings_mean']} | {agg['compounds_mean']} | {cascade} |"
        )
    lines.append("")

    lines.append("<details><summary>per-run detail</summary>")
    lines.append("")
    lines.append("| path | run | detected_ids | findings | top | compounds | L2/L3/L4 cascade |")
    lines.append("|------|-----|--------------|----------|-----|-----------|-------------------|")
    for run in case.old_runs + case.new_runs:
        if run.error:
            lines.append(f"| {run.path_label} | {run.run_index} | ERR | - | - | - | - |")
            continue
        ids_short = ", ".join(
            t.replace("-tendency", "") for t in run.detected_tendency_ids[:4]
        ) + ("…" if len(run.detected_tendency_ids) > 4 else "")
        cascade = f"{run.companion_model_count}/{run.frame_element_count}/{run.structural_gap_count}"
        lines.append(
            f"| {run.path_label} | {run.run_index} | {ids_short or '-'} | {run.findings_count} | "
            f"{run.top_findings_count} | {run.compound_groups_count} | {cascade} |"
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
    lines.append(f"# Phase 2c Lane 1 quality check — {today}")
    lines.append("")
    if dry_run:
        lines.append("**Mode: DRY RUN** — N=1 on a subset of cases. Not an acceptance-gate run.")
        lines.append("")
    lines.append(
        f"Measurement: {len(all_cases)} case(s) × 2 paths × N={n} runs. "
        f"Wall time: {duration_seconds:.1f}s."
    )
    lines.append("")
    lines.append("**Metrics definitions (Lane 1 direct):**")
    lines.append("- `detected`: size of `detected_tendencies` set (tendencies that passed triage + routing)")
    lines.append("- `findings`: total `delta_card.findings` count (each finding = one routed tendency)")
    lines.append("- `top`: `delta_card.top_findings` count (tier-1 findings surfaced)")
    lines.append("- `compounds`: `delta_card.compound_groups` count (lollapalooza-style confluence)")
    lines.append("- `selected_models`: `delta_card.selected_model_ids` count — this is lane1's anti-echo input to Lanes 2/3/4")
    lines.append("")
    lines.append("**Metrics definitions (downstream cascade):**")
    lines.append("- `L2/L3/L4`: companion detected models / frame elements / structural gaps")
    lines.append("- These change only if Lane 1's anti-echo set changes enough to shift downstream lane outputs — the cascade signal.")
    lines.append("")
    lines.append(
        "**Note on Lane 1 signal shape:** there is no drop-rate metric (no evidence-substring "
        "validation downstream of Pass 2). Quality evidence comes from per-case stability of "
        "detected tendencies + findings counts + downstream cascade magnitude. The 0-findings "
        "rate across all new-path runs is tracked separately below."
    )
    lines.append("")

    all_old = [r for c in all_cases for r in c.old_runs]
    all_new = [r for c in all_cases for r in c.new_runs]
    old_agg = _aggregate_row(all_old)
    new_agg = _aggregate_row(all_new)
    lines.append("## Aggregate across all cases")
    lines.append("")
    lines.append("| path | total runs | errored | detected (mean) | findings (mean) | compounds (mean) | selected_models (mean) | 0-findings count | cascade L2/L3/L4 |")
    lines.append("|------|-----------|---------|-----------------|-----------------|------------------|------------------------|------------------|-------------------|")
    for label, agg in (("old", old_agg), ("new", new_agg)):
        cascade = f"{agg['cascade_lane2_mean']} / {agg['cascade_lane3_mean']} / {agg['cascade_lane4_mean']}"
        lines.append(
            f"| {label} | {agg['n']} | {agg['errored']} | {agg['detected_mean']} | "
            f"{agg['findings_mean']} | {agg['compounds_mean']} | "
            f"{agg['selected_models_mean']} | {agg['zero_findings_runs']} | {cascade} |"
        )
    lines.append("")

    regressions_total = sum(1 for c in all_cases if _regression_flags(c))
    if regressions_total == 0:
        lines.append("**Aggregate regression summary:** zero regressions flagged across all cases.")
    else:
        lines.append(
            f"**Aggregate regression summary:** {regressions_total} of {len(all_cases)} cases regressed. "
            "Each must be diagnosed in the PR description (diagnosis-required policy)."
        )
    lines.append("")

    # Track 0-findings rate explicitly, per PM directive.
    zero_old = old_agg["zero_findings_runs"]
    zero_new = new_agg["zero_findings_runs"]
    total_old = old_agg["n"] + old_agg["errored"]
    total_new = new_agg["n"] + new_agg["errored"]
    lines.append("## 0-findings anomaly tracking")
    lines.append("")
    lines.append(
        f"- old path: {zero_old} zero-findings runs / {total_old} total ({(100*zero_old/total_old):.1f}%)"
        if total_old else "- old path: n/a"
    )
    lines.append(
        f"- new path: {zero_new} zero-findings runs / {total_new} total ({(100*zero_new/total_new):.1f}%)"
        if total_new else "- new path: n/a"
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
                        metrics = parse_lane1_metrics(out_path, case_name, label, run_index)
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
    (output_dir / "lane1-quality-report.md").write_text(report, encoding="utf-8")
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
        args.output_dir = DEFAULT_OUTPUT_PARENT / f"phase2c-lane1-equivalence-{today}"

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
    report_path = args.output_dir / "lane1-quality-report.md"
    print()
    print(f"Report: {report_path}")
    print(f"Wall time: {duration:.1f}s across {len(cases)} cases × 2 paths × N={args.n}.")

    regressions = sum(1 for c in all_metrics if _regression_flags(c))
    return 0 if regressions == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
