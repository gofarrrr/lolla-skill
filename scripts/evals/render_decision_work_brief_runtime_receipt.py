#!/usr/bin/env python3
"""Render a short Decision Work Brief runtime receipt."""
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
    from engine.system_b.decision_work_brief_runtime_receipt import (
        DecisionWorkBriefRuntimeReceiptError,
        load_status_json,
        render_decision_work_brief_runtime_receipt,
        render_receipt_from_status,
    )

    parser = argparse.ArgumentParser(
        description=(
            "Render the compact Decision Work Brief runtime receipt. This "
            "command does not run Lolla, call models, inspect raw conversation "
            "text, score advice, or authorize action."
        )
    )
    parser.add_argument("--status-json", type=Path)
    parser.add_argument("--state")
    parser.add_argument("--action-consequence")
    parser.add_argument("--full-brief-ref")
    parser.add_argument("--evidence-ref")
    parser.add_argument("--reason", action="append", default=[])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    try:
        if args.status_json:
            receipt = render_receipt_from_status(
                load_status_json(args.status_json),
                action_consequence=args.action_consequence,
            )
        else:
            if not args.state:
                parser.error("--state is required when --status-json is omitted")
            receipt = render_decision_work_brief_runtime_receipt(
                attachment_state=args.state,
                action_consequence=args.action_consequence,
                full_brief_ref=args.full_brief_ref,
                evidence_ref=args.evidence_ref,
                reasons=args.reason,
            )
    except DecisionWorkBriefRuntimeReceiptError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(receipt, encoding="utf-8")
    else:
        print(receipt, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
