#!/usr/bin/env python3
"""Run the Decision Work offline operator runner."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ensure_repo_root_on_path() -> None:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    _ensure_repo_root_on_path()
    from engine.system_b.decision_work_offline_operator_runner import (
        DecisionWorkOfflineOperatorRunnerError,
        render_offline_operator_runner_summary_json,
        run_decision_work_offline_operator,
        write_offline_operator_runner_summary,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Run a one-shot offline Decision Work operator flow from explicit "
            "paths. This command orchestrates existing deterministic CLIs up "
            "to dry-run readiness only; it does not run Lolla, call models, "
            "generate semantic interpretation, approve resolver refs, write "
            "sidecars, mutate archives, wire runtime, score advice, or "
            "authorize action."
        )
    )
    parser.add_argument("--completed-run-archive-dir", required=True, type=Path)
    parser.add_argument("--generated-read", required=True, type=Path)
    parser.add_argument("--generated-triage", required=True, type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--safe-output-dir", required=True, type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        help=(
            "Optional runner summary path. Defaults to "
            "<safe-output-dir>/runner_summary.json."
        ),
    )
    parser.add_argument(
        "--operator-confirm-real-archive-write",
        action="store_true",
        help="Accepted for future compatibility; PR226 still stops before write.",
    )
    parser.add_argument(
        "--write-sidecar",
        action="store_true",
        help="Requests a future write, but PR226 always stops before writing.",
    )
    parser.add_argument(
        "--stop-before-write",
        action="store_true",
        help="Explicitly stop before any real archive write.",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        summary = run_decision_work_offline_operator(
            completed_run_archive_dir=args.completed_run_archive_dir,
            generated_read_path=args.generated_read,
            generated_triage_path=args.generated_triage,
            case_id=args.case_id,
            safe_output_dir=args.safe_output_dir,
            out_path=args.out,
            write_sidecar=args.write_sidecar,
            operator_confirm_real_archive_write=(
                args.operator_confirm_real_archive_write
            ),
            stop_before_write=args.stop_before_write,
        )
        payload = render_offline_operator_runner_summary_json(
            summary,
            pretty=args.pretty,
        )
        out_path = args.out or args.safe_output_dir / "runner_summary.json"
        write_offline_operator_runner_summary(out_path, payload)
    except DecisionWorkOfflineOperatorRunnerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
