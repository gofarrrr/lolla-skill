#!/usr/bin/env python3
"""Render the final user-facing receipt for a Lolla run."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.system_b.private_runtime import atomic_private_write_text  # noqa: E402


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
    prefix = _run_health_prefix(
        overall=overall,
        issues=set(run_health.get("issues") or []),
        run_health=run_health,
    )
    live_output_note = _live_output_note(run_health=run_health)
    observatory_text = _observatory_text(
        observatory_url=observatory_url,
        observatory_status=observatory_status,
    )
    return (
        f"{prefix}{live_output_note}Reconsideration stayed in this conversation's context; "
        f"it was not an external check. {observatory_text} "
        f"The memo and archive were saved privately. Cost estimate: {cost_text}."
    )


def _run_health_prefix(
    *,
    overall: str,
    issues: set[str],
    run_health: Mapping[str, Any],
) -> str:
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
    if "provider_call_terminal_loss" in issues:
        count = int(run_health.get("provider_failed_call_count") or 0)
        stages = [
            str(value).strip()
            for value in (run_health.get("provider_failed_call_stages") or [])
            if str(value).strip()
        ]
        tendency_ids = [
            str(value).strip()
            for value in (run_health.get("provider_failed_tendency_ids") or [])
            if str(value).strip()
        ]
        call_text = f"{count} provider-backed reasoning call"
        if count != 1:
            call_text += "s"
        details: list[str] = []
        if stages:
            details.append("stage " + ", ".join(stages))
        if tendency_ids:
            details.append("check " + ", ".join(tendency_ids))
        detail_text = f" ({'; '.join(details)})" if details else ""
        return (
            f"Run health is partial: {call_text} ended without a usable result"
            f"{detail_text} and was not retried; other product artifacts are present. "
        )
    if "bullshit_index_partial" in issues:
        failures = int(run_health.get("bullshit_index_evaluation_failures") or 0)
        total = int(run_health.get("bullshit_index_evaluation_count") or 0)
        if total > 0:
            check_text = (
                f"{failures} of {total} passage-quality "
                f"{'check' if total == 1 else 'checks'}"
            )
        else:
            check_text = (
                f"{failures} passage-quality "
                f"{'check' if failures == 1 else 'checks'}"
            )
        return (
            f"Run health is partial: {check_text} returned no usable judgment "
            "and was not retried; the core audit and revised answer are present, "
            "but the passage profile is incomplete. "
        )
    if "pipeline_warnings" in issues:
        return (
            "Run health is partial: vendor boundary warnings were emitted; substantive "
            "artifacts are present. "
        )
    return f"Run health is {overall}; inspect the archived artifacts for details. "


def _live_output_note(*, run_health: Mapping[str, Any]) -> str:
    status = str(run_health.get("live_output_health") or "").strip()
    if status == "not_checked":
        return (
            "The saved narration does not independently verify everything shown "
            "in the live terminal. "
        )
    if status == "missing":
        return "No saved live-terminal narration was available for hygiene review. "
    if status == "unsafe":
        return "The live terminal output was marked unsafe; inspect it before reuse. "
    return ""


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
    atomic_private_write_text(Path(args.output), receipt + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
