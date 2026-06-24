#!/usr/bin/env python3
"""Render the final user-facing receipt for a Lolla run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping


def build_final_receipt(
    *,
    result_payload: Mapping[str, Any],
    result_path: Path,
    observatory_url: str,
    observatory_status: str,
    archive_path: str,
) -> str:
    usage = result_payload.get("usage_summary") or {}
    cost = usage.get("estimated_total_cost_usd")
    cost_text = f"${float(cost):.2f}" if cost is not None else "unavailable"
    run_health = result_payload.get("run_health") or {}
    overall = str(run_health.get("overall") or "unknown")
    memo_path = result_path.with_name(result_path.name.replace("_result.json", "_memo.md"))

    prefix = _run_health_prefix(overall=overall, issues=set(run_health.get("issues") or []))
    observatory_text = _observatory_text(
        observatory_url=observatory_url,
        observatory_status=observatory_status,
    )
    return (
        f"{prefix}{observatory_text} "
        f"Memo at {memo_path}. Cost estimate: {cost_text}. "
        f"Archived to {archive_path}."
    )


def _run_health_prefix(*, overall: str, issues: set[str]) -> str:
    if overall in {"healthy", "ok"}:
        return ""
    if "quote_fabrication" in issues:
        return (
            "Run health is degraded: one extraction quote failed literal validation "
            "after retry; inspect the artifacts before treating this as decision-grade. "
        )
    if "vendor_boundary_reasoning_leak" in issues:
        return (
            "Run health is partial: the model provider returned reasoning details "
            "despite reasoning being disabled; product artifacts are present. "
        )
    if "pipeline_warnings" in issues:
        return (
            "Run health is partial: vendor boundary warnings were emitted; substantive "
            "artifacts are present. "
        )
    return f"Run health is {overall}; inspect the archived artifacts for details. "


def _observatory_text(*, observatory_url: str, observatory_status: str) -> str:
    status = (observatory_status or "").strip().lower()
    url = (observatory_url or "").strip()
    if status == "live" and url:
        return f"Observatory is live at {url}."
    if status == "skipped":
        return "Observatory was not launched."
    return "Observatory did not stay live; memo and archive are still available."


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("--result", required=True)
    parser.add_argument("--observatory-url", default="")
    parser.add_argument("--observatory-status", default="unavailable")
    parser.add_argument("--archive-path", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    result_path = Path(args.result)
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    receipt = build_final_receipt(
        result_payload=payload,
        result_path=result_path,
        observatory_url=args.observatory_url,
        observatory_status=args.observatory_status,
        archive_path=args.archive_path,
    )
    Path(args.output).write_text(receipt + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
