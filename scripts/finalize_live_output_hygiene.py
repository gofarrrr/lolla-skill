#!/usr/bin/env python3
"""Finalize live transcript hygiene for an in-flight Lolla result."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.output_hygiene import finalize_live_output_hygiene  # noqa: E402
from engine.system_b.run_state import assert_expected_run_state  # noqa: E402


_RESULT_RE = re.compile(r"^lolla_(?P<run_id>.+)_result\.json$")


def _infer_result_path(run_id: str | None, result: str | None) -> Path:
    if result:
        return Path(result)
    if not run_id:
        raise SystemExit("Either --result or --run-id is required")
    return Path("/tmp") / f"lolla_{run_id}_result.json"


def _infer_transcript_path(
    result_path: Path,
    run_id: str | None,
    transcript: str | None,
) -> Path | None:
    if transcript:
        return Path(transcript)
    if run_id:
        return Path("/tmp") / f"lolla_{run_id}_live_transcript.txt"
    match = _RESULT_RE.match(result_path.name)
    if not match:
        return None
    return result_path.with_name(f"lolla_{match.group('run_id')}_live_transcript.txt")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--run-id", default=None, help="Run ID used for /tmp/lolla_{RUN_ID}_*.json")
    parser.add_argument("--result", default=None, help="Explicit result JSON path")
    parser.add_argument("--transcript", default=None, help="Explicit live transcript text path")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output for user-facing skill runs")
    parser.add_argument(
        "--require-live-output-clean",
        action="store_true",
        help="Return non-zero unless the live transcript exists, is trusted, and is clean.",
    )
    parser.add_argument(
        "--trusted-transcript",
        action="store_true",
        help="Treat --transcript as a complete captured live transcript, not a manual artifact.",
    )
    args = parser.parse_args()

    result_path = _infer_result_path(args.run_id, args.result)
    if not result_path.exists():
        print(f"Live output hygiene finalization skipped: missing result {result_path}", file=sys.stderr)
        return 1

    transcript_path = _infer_transcript_path(result_path, args.run_id, args.transcript)
    inferred_run_id = args.run_id
    if not inferred_run_id:
        match = _RESULT_RE.match(result_path.name)
        inferred_run_id = match.group("run_id") if match else None
    try:
        assert_expected_run_state(
            actual_run_id=inferred_run_id,
            artifact_paths=[result_path, transcript_path],
            phase="finalize_live_output_hygiene",
        )
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 1
    transcript_text = None
    if transcript_path and transcript_path.exists():
        transcript_text = transcript_path.read_text(encoding="utf-8")

    result = json.loads(result_path.read_text(encoding="utf-8"))
    finalized = finalize_live_output_hygiene(
        result,
        transcript_text,
        require_live_output_clean=args.require_live_output_clean,
        trusted_capture=args.trusted_transcript,
    )
    result_path.write_text(json.dumps(finalized, indent=2, ensure_ascii=False), encoding="utf-8")

    health = finalized.get("run_health") or {}
    status = health.get("live_output_health", "unknown")
    if not args.quiet:
        if transcript_path:
            print(f"Live output hygiene finalized: {status} ({transcript_path})")
        else:
            print(f"Live output hygiene finalized: {status}")

    if args.require_live_output_clean and status != "clean":
        print(
            f"Live output hygiene is {status}; preserve a clean live transcript before continuing.",
            file=sys.stderr,
        )
        for leak in health.get("live_output_leaks") or []:
            surface = leak.get("surface", "unknown")
            line = leak.get("line", "?")
            term = leak.get("term", "unknown")
            match = leak.get("match", "")
            print(f"- {surface}:{line}: {term} ({match})", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
