#!/usr/bin/env python3
"""Prepare an offline Observatory Decision Work process brief state."""
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
    from engine.system_b.observatory_process_brief_runner import (
        STATE_FILENAME,
        ObservatoryProcessBriefRunnerError,
        prepare_observatory_process_brief,
        render_observatory_process_brief_runner_json,
        write_observatory_process_brief_runner_json,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Prepare a no-provider Observatory process-brief state for a "
            "completed run. The command can optionally delegate to the "
            "existing offline operator runner when explicit generated-read "
            "and generated-triage refs are supplied. It does not create "
            "semantic reads, write sidecars, mutate archives, run Lolla, "
            "wire runtime, score advice, or authorize action."
        )
    )
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--completed-run-archive-dir", required=True, type=Path)
    parser.add_argument("--safe-output-dir", required=True, type=Path)
    parser.add_argument("--generated-read", type=Path)
    parser.add_argument("--generated-triage", type=Path)
    parser.add_argument(
        "--run-offline-operator",
        action="store_true",
        help="Run the existing offline operator runner when explicit refs exist.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help=(
            "Optional state JSON output. Defaults to "
            "<safe-output-dir>/observatory_process_brief_runner.json."
        ),
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        state = prepare_observatory_process_brief(
            selected_case_id=args.case_id,
            completed_run_archive_dir=args.completed_run_archive_dir,
            safe_output_dir=args.safe_output_dir,
            generated_read_path=args.generated_read,
            generated_triage_path=args.generated_triage,
            run_offline_operator=args.run_offline_operator,
        )
        payload = render_observatory_process_brief_runner_json(
            state,
            pretty=args.pretty,
        )
        output = args.out or args.safe_output_dir / STATE_FILENAME
        write_observatory_process_brief_runner_json(output, payload)
    except ObservatoryProcessBriefRunnerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
