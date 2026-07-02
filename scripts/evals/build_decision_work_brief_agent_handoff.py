#!/usr/bin/env python3
"""Build a Decision Work Brief agent handoff packet from safe bundle refs."""
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
    from engine.system_b.decision_work_brief_agent_handoff import (
        DecisionWorkBriefAgentHandoffError,
        build_decision_work_brief_agent_handoff,
        load_json_object,
        render_agent_handoff_json,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Build a checked-in-safe Decision Work Brief agent handoff packet. "
            "This command does not run Lolla, call models, export raw/private "
            "content, score advice, or authorize action."
        )
    )
    parser.add_argument("--source-run-ref", required=True)
    parser.add_argument("--attachment-status", required=True, type=Path)
    parser.add_argument("--eligibility", type=Path)
    parser.add_argument("--triage-read", type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        handoff = build_decision_work_brief_agent_handoff(
            source_run_ref=args.source_run_ref,
            attachment_status=load_json_object(args.attachment_status),
            eligibility_result=load_json_object(args.eligibility)
            if args.eligibility
            else None,
            triage_read=load_json_object(args.triage_read) if args.triage_read else None,
            case_id=args.case_id,
        )
    except DecisionWorkBriefAgentHandoffError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        render_agent_handoff_json(handoff, pretty=args.pretty),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
