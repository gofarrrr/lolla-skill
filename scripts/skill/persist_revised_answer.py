#!/usr/bin/env python3
"""Persist Claude's Step 6 revised answer into the in-flight result JSON."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.run_events import append_run_event  # noqa: E402
from engine.system_b.run_state import assert_expected_run_state  # noqa: E402


def _run_id(value: str | None) -> str:
    run_id = value or os.environ.get("LOLLA_RUN_ID", "")
    if not run_id:
        raise SystemExit("FATAL: LOLLA_RUN_ID is not set. Re-run /lolla setup before Step 6b.")
    return run_id


def _record_event(run_id: str, *, word_count: int) -> None:
    try:
        append_run_event(
            run_id=run_id,
            event_type="revised_answer_persisted",
            details={"word_count": word_count},
        )
    except Exception:
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--revised-file", "--file", dest="revised_file", default=None)
    args = parser.parse_args()

    run_id = _run_id(args.run_id)
    result_path = Path(f"/tmp/lolla_{run_id}_result.json")
    revised_path = Path(args.revised_file or f"/tmp/lolla_{run_id}_revised.txt")
    assert_expected_run_state(
        actual_run_id=run_id,
        artifact_paths=[result_path, revised_path],
        phase="step6b_revised_answer",
    )

    if not result_path.exists():
        raise SystemExit(f"FATAL: result JSON missing at {result_path}. Step 3 did not complete.")
    if not revised_path.exists() or not revised_path.read_text(encoding="utf-8").strip():
        raise SystemExit(f"FATAL: revised answer file missing or empty at {revised_path}.")

    revised_text = revised_path.read_text(encoding="utf-8").strip()
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    payload["revised_answer"] = revised_text
    payload["revised_answer_source"] = "claude_step6"
    payload["revised_answer_present"] = True
    payload["revised_answer_written_at"] = dt.datetime.now(dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    result_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    transcript_path = Path(os.environ.get("LOLLA_LIVE_TRANSCRIPT") or f"/tmp/lolla_{run_id}_live_transcript.txt")
    transcript = transcript_path.read_text(encoding="utf-8") if transcript_path.exists() else ""
    if revised_text and revised_text not in transcript:
        with transcript_path.open("a", encoding="utf-8") as handle:
            if transcript and not transcript.endswith("\n\n"):
                handle.write("\n\n")
            handle.write(revised_text + "\n")
    _record_event(run_id, word_count=len(revised_text.split()))
    print(f"Revised answer persisted to {result_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
