#!/usr/bin/env python3
"""Phase 2d Lane 2 quality check — old-path vs new-path on the 10-case corpus.

Runs `run_extract.py` once per case, then `run_pipeline.py` N times on legacy
path + N times on --new-contract path. Parses Lane 2 outputs (companion_card,
fingerprint moves, detected_models) and computes:

- Lane 2 direct: fingerprint_validated count, fingerprint_dropped count,
  drop_rate (analog to Lane 3's drop rate — substring-validation signal),
  detected_models count, rejected_models count.
- Cascade: Lane 1/3/4 output sizes (should be unchanged since Lane 2
  output does not feed Lane 1/3/4 anti-echo directly — Lane 2 consumes
  Lane 1's anti-echo, not the other way around).

Drop-rate is the architectural evidence: on the new path, fingerprint
evidence_quotes must be substrings of ASSISTANT turns (not flattened
vanilla_answer). A drop-rate increase means the LLM is citing passages
from CONTEXT (user turns or extraction summaries) that are filtered out;
a drop-rate decrease means the LLM is grounding moves in actual assistant
text. Both outcomes are meaningful signal.

Usage (dry-run):
    python3 scripts/phase2d_lane2_quality_check.py --n 1 --cases oncologist

Usage (full measurement):
    python3 scripts/phase2d_lane2_quality_check.py --n 3
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
    fingerprint_raw_count: int
    fingerprint_validated_count: int
    fingerprint_dropped_count: int
    detected_models_count: int
    rejected_models_count: int
    # Cascade (should be stable; Lane 2 doesn't drive Lane 1/3/4 anti-echo)
    lane1_findings_count: int
    lane3_frame_elements_count: int
    lane4_gap_count: int
    error: str | None = None

    @property
    def drop_rate(self) -> float:
        denom = self.fingerprint_validated_count + self.fingerprint_dropped_count
        return self.fingerprint_dropped_count / denom if denom else 0.0


@dataclass
class CaseMetrics:
    case: str
    old_runs: list[RunMetrics] = field(default_factory=list)
    new_runs: list[RunMetrics] = field(default_factory=list)


def _empty_metrics(case: str, path_label: str, run_index: int, error: str) -> RunMetrics:
    return RunMetrics(
        case=case, path_label=path_label, run_index=run_index,
        fingerprint_raw_count=0, fingerprint_validated_count=0, fingerprint_dropped_count=0,
        detected_models_count=0, rejected_models_count=0,
        lane1_findings_count=0, lane3_frame_elements_count=0, lane4_gap_count=0,
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
        sys.executable, str(REPO_ROOT / "scripts" / "run_extract.py"),
        "--conversation-file", str(conversation_path),
        "--output-file", str(extraction_output),
    ]
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        return f"run_extract.py exit={code}. stderr: {err.strip()[:400]!r}"
    try:
        payload = json.loads(extraction_output.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return f"extraction unparseable: {exc}"
    if payload.get("status") != "ok":
        return f"extraction status={payload.get('status')!r}"
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
            if "companion_card" in existing or existing.get("status") == "ok":
                print(f"  [resume] skip {result_output.name}", flush=True)
                return None
        except json.JSONDecodeError:
            pass
    cmd = [
        sys.executable, str(REPO_ROOT / "scripts" / "run_pipeline.py"),
        "--extraction-file", str(extraction_path),
        "--conversation-file", str(conversation_path),
        "--output-file", str(result_output),
        "--skip-revision",
    ]
    if new_contract:
        cmd.append("--new-contract")
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        return f"run_pipeline.py exit={code} ({'new' if new_contract else 'old'}-path). stderr: {err.strip()[:400]!r}"
    return None


def parse_lane2_metrics(result_path: Path, case: str, path_label: str, run_index: int) -> RunMetrics:
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    audit = payload.get("audit_summary") or {}
    fp_raw = audit.get("companion_fingerprint_raw") or []
    fp_validated = audit.get("companion_fingerprint_validated") or []
    fp_dropped = audit.get("companion_fingerprint_dropped") or []
    detected = audit.get("companion_detected_models") or []
    rejected = audit.get("companion_rejected_models") or []

    # Cascade
    dc = payload.get("delta_card") or {}
    lane1_findings = dc.get("findings") or []
    fc = payload.get("frame_pressure_card") or {}
    frame_elements = fc.get("frame_elements") or []
    sc = payload.get("structural_coverage_card") or {}
    struct_dims = sc.get("dimensions") or []
    struct_gaps = [d for d in struct_dims if d.get("covered") is False]

    return RunMetrics(
        case=case, path_label=path_label, run_index=run_index,
        fingerprint_raw_count=len(fp_raw),
        fingerprint_validated_count=len(fp_validated),
        fingerprint_dropped_count=len(fp_dropped),
        detected_models_count=len(detected),
        rejected_models_count=len(rejected),
        lane1_findings_count=len(lane1_findings),
        lane3_frame_elements_count=len(frame_elements),
        lane4_gap_count=len(struct_gaps),
    )


def _regression_flags(case: CaseMetrics) -> list[str]:
    flags: list[str] = []
    old_det = [r.detected_models_count for r in case.old_runs if not r.error]
    new_det = [r.detected_models_count for r in case.new_runs if not r.error]
    if old_det and new_det and max(old_det) > 0 and max(new_det) == 0:
        flags.append("NEGATIVE_CHECK_empty_companion_card: old path detected models; new path always empty")

    # Fingerprint validated collapse
    old_fp = [r.fingerprint_validated_count for r in case.old_runs if not r.error]
    new_fp = [r.fingerprint_validated_count for r in case.new_runs if not r.error]
    if old_fp and new_fp and statistics.median(old_fp) >= 3 and statistics.median(new_fp) == 0:
        flags.append("NEGATIVE_CHECK_fingerprint_collapse: old fingerprint moves present; new path always empty")

    # Detected-model regression ≥ 2
    if old_det and new_det:
        omed, nmed = statistics.median(old_det), statistics.median(new_det)
        if omed - nmed >= 2:
            flags.append(f"detected_models_regression: new median={nmed} vs old={omed} (dropped ≥2)")

    # Drop-rate rise > 0.20 (rough threshold)
    old_dr = [r.drop_rate for r in case.old_runs if not r.error]
    new_dr = [r.drop_rate for r in case.new_runs if not r.error]
    if old_dr and new_dr:
        odr = statistics.mean(old_dr)
        ndr = statistics.mean(new_dr)
        if ndr - odr > 0.20:
            flags.append(f"drop_rate_rise: new drop_rate mean={ndr:.2f} vs old={odr:.2f} (+{ndr-odr:.2f})")

    return flags


def _aggregate_row(runs: list[RunMetrics]) -> dict[str, Any]:
    valid = [r for r in runs if not r.error]
    if not valid:
        return {
            "n": 0, "errored": len(runs),
            "fp_validated_mean": 0.0, "fp_dropped_mean": 0.0, "drop_rate_mean": 0.0,
            "detected_mean": 0.0, "rejected_mean": 0.0,
            "cascade_l1": 0.0, "cascade_l3": 0.0, "cascade_l4": 0.0,
            "zero_detected_count": 0,
        }
    return {
        "n": len(valid), "errored": len(runs) - len(valid),
        "fp_validated_mean": round(statistics.mean(r.fingerprint_validated_count for r in valid), 2),
        "fp_dropped_mean": round(statistics.mean(r.fingerprint_dropped_count for r in valid), 2),
        "drop_rate_mean": round(statistics.mean(r.drop_rate for r in valid), 3),
        "detected_mean": round(statistics.mean(r.detected_models_count for r in valid), 2),
        "rejected_mean": round(statistics.mean(r.rejected_models_count for r in valid), 2),
        "cascade_l1": round(statistics.mean(r.lane1_findings_count for r in valid), 2),
        "cascade_l3": round(statistics.mean(r.lane3_frame_elements_count for r in valid), 2),
        "cascade_l4": round(statistics.mean(r.lane4_gap_count for r in valid), 2),
        "zero_detected_count": sum(1 for r in valid if r.detected_models_count == 0),
    }


def _render_case_section(case: CaseMetrics, flags: list[str]) -> str:
    lines: list[str] = [f"### `{case.case}`", ""]
    if flags:
        lines.append("**Regression flags:**")
        for f in flags:
            lines.append(f"- `{f}`")
        lines.append("")
    old_agg = _aggregate_row(case.old_runs)
    new_agg = _aggregate_row(case.new_runs)
    lines.append("| path | n | fp_valid | fp_dropped | drop_rate | detected | rejected | cascade L1/L3/L4 |")
    lines.append("|------|---|----------|------------|-----------|----------|----------|-------------------|")
    for label, agg in (("old", old_agg), ("new", new_agg)):
        casc = f"{agg['cascade_l1']} / {agg['cascade_l3']} / {agg['cascade_l4']}"
        lines.append(
            f"| {label} | {agg['n']} | {agg['fp_validated_mean']} | {agg['fp_dropped_mean']} | "
            f"{agg['drop_rate_mean']} | {agg['detected_mean']} | {agg['rejected_mean']} | {casc} |"
        )
    lines.append("")
    lines.append("<details><summary>per-run detail</summary>")
    lines.append("")
    lines.append("| path | run | fp_raw | fp_valid | fp_drop | drop_rate | detected | rejected | L1/L3/L4 |")
    lines.append("|------|-----|--------|----------|---------|-----------|----------|----------|----------|")
    for r in case.old_runs + case.new_runs:
        if r.error:
            lines.append(f"| {r.path_label} | {r.run_index} | ERR | - | - | - | - | - | - |")
            continue
        lines.append(
            f"| {r.path_label} | {r.run_index} | {r.fingerprint_raw_count} | "
            f"{r.fingerprint_validated_count} | {r.fingerprint_dropped_count} | "
            f"{r.drop_rate:.2f} | {r.detected_models_count} | {r.rejected_models_count} | "
            f"{r.lane1_findings_count}/{r.lane3_frame_elements_count}/{r.lane4_gap_count} |"
        )
    lines.append("")
    lines.append("</details>")
    lines.append("")
    return "\n".join(lines)


def render_report(all_cases: list[CaseMetrics], *, n: int, duration_seconds: float, dry_run: bool) -> str:
    lines: list[str] = []
    today = date.today().isoformat()
    lines.append(f"# Phase 2d Lane 2 quality check — {today}")
    lines.append("")
    if dry_run:
        lines.append("**Mode: DRY RUN.**")
        lines.append("")
    lines.append(f"Measurement: {len(all_cases)} case(s) × 2 paths × N={n} runs. Wall time: {duration_seconds:.1f}s.")
    lines.append("")
    lines.append("**Lane 2 direct metrics:**")
    lines.append("- `fp_valid` / `fp_dropped`: fingerprint moves that passed/failed substring validation against the audit target (flattened `vanilla_answer` on old, joined assistant turns on new).")
    lines.append("- `drop_rate`: `fp_dropped / (fp_valid + fp_dropped)`. Analog to Lane 3's drop rate. A drop here means the LLM cited evidence from CONTEXT (user turns or extractor summaries), which is rejected under the new contract.")
    lines.append("- `detected`: verified candidate models accepted into `companion_card.detected_models`.")
    lines.append("- `rejected`: candidates rejected at verification.")
    lines.append("")
    lines.append("**Cascade L1/L3/L4:** Lane 2 does not feed Lanes 1/3/4 anti-echo — cascade numbers should be unchanged vs. old path. Any cascade drift signals noise from Lane 1's anti-echo shift rippling differently, not a Lane-2-induced change.")
    lines.append("")

    all_old = [r for c in all_cases for r in c.old_runs]
    all_new = [r for c in all_cases for r in c.new_runs]
    old_agg = _aggregate_row(all_old)
    new_agg = _aggregate_row(all_new)
    lines.append("## Aggregate across all cases")
    lines.append("")
    lines.append("| path | total | errored | fp_valid | fp_dropped | drop_rate | detected | rejected | 0-detected | L1/L3/L4 |")
    lines.append("|------|-------|---------|----------|------------|-----------|----------|----------|------------|----------|")
    for label, agg in (("old", old_agg), ("new", new_agg)):
        casc = f"{agg['cascade_l1']} / {agg['cascade_l3']} / {agg['cascade_l4']}"
        lines.append(
            f"| {label} | {agg['n']} | {agg['errored']} | {agg['fp_validated_mean']} | "
            f"{agg['fp_dropped_mean']} | {agg['drop_rate_mean']} | {agg['detected_mean']} | "
            f"{agg['rejected_mean']} | {agg['zero_detected_count']} | {casc} |"
        )
    lines.append("")

    regressions_total = sum(1 for c in all_cases if _regression_flags(c))
    if regressions_total == 0:
        lines.append("**Aggregate regression summary:** zero regressions flagged across all cases.")
    else:
        lines.append(f"**Aggregate regression summary:** {regressions_total} of {len(all_cases)} cases regressed. Diagnose in PR.")
    lines.append("")

    lines.append("## Per-case detail")
    lines.append("")
    for case in all_cases:
        flags = _regression_flags(case)
        lines.append(_render_case_section(case, flags))

    errored_runs = [r for c in all_cases for r in (c.old_runs + c.new_runs) if r.error is not None]
    if errored_runs:
        lines.append(f"## Errored runs ({len(errored_runs)})")
        lines.append("")
        for r in errored_runs:
            lines.append(f"- `{r.case}` {r.path_label} run {r.run_index}: {r.error[:200]}")
    lines.append("")
    return "\n".join(lines)


def run_measurement(*, cases: list[tuple[str, Path]], output_dir: Path, n: int, dry_run: bool = False) -> tuple[list[CaseMetrics], float]:
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
            print(f"  [errored] {extract_err}", flush=True)
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
                        metrics = parse_lane2_metrics(out_path, case_name, label, run_index)
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
        print(f"\n[warning] {len(errored_runs)} runs errored", flush=True)

    duration = time.monotonic() - started
    report = render_report(all_metrics, n=n, duration_seconds=duration, dry_run=dry_run)
    (output_dir / "lane2-quality-report.md").write_text(report, encoding="utf-8")
    (output_dir / "raw-metrics.json").write_text(
        json.dumps(
            [
                {
                    "case": c.case,
                    "old_runs": [r.__dict__ | {"drop_rate": r.drop_rate} for r in c.old_runs],
                    "new_runs": [r.__dict__ | {"drop_rate": r.drop_rate} for r in c.new_runs],
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
        args.output_dir = DEFAULT_OUTPUT_PARENT / f"phase2d-lane2-equivalence-{today}"

    cases = _cases_from_corpus(args.cases)
    if not cases:
        raise SystemExit("no cases resolved")

    dry_run = (args.n == 1 and len(cases) < 3)
    all_metrics, duration = run_measurement(
        cases=cases, output_dir=args.output_dir, n=args.n, dry_run=dry_run,
    )
    print()
    print(f"Report: {args.output_dir / 'lane2-quality-report.md'}")
    print(f"Wall time: {duration:.1f}s across {len(cases)} cases × 2 paths × N={args.n}.")

    regressions = sum(1 for c in all_metrics if _regression_flags(c))
    return 0 if regressions == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
