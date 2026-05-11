#!/usr/bin/env python3
"""Compare two archived Lolla runs with trace/product eligibility first."""
from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any, Mapping


UNTRUSTED_LEDGER_STATUSES = {"missing", "invalid"}
UNTRUSTED_OVERALL_STATUSES = {"critical", "degraded"}


def compare_archived_runs(left_path: Path | str, right_path: Path | str) -> dict[str, Any]:
    left = _load_archived_run(Path(left_path))
    right = _load_archived_run(Path(right_path))
    return {
        "schema_version": "archived_run_comparison.v1",
        "left": _run_summary(left),
        "right": _run_summary(right),
        "eligibility": _comparison_eligibility(left, right),
        "health": {
            "left": _health_summary(left.result),
            "right": _health_summary(right.result),
        },
        "v60": {
            "left": _v60_summary(left.result),
            "right": _v60_summary(right.result),
        },
        "usage": {
            "left": _usage_summary(left.result),
            "right": _usage_summary(right.result),
        },
        "diffs": {
            "revised_answer": _diff_text(left.revised_answer, right.revised_answer),
            "memo": _diff_text(left.memo_markdown, right.memo_markdown),
        },
    }


def render_markdown(report: Mapping[str, Any]) -> str:
    eligibility = _mapping(report.get("eligibility"))
    health = _mapping(report.get("health"))
    v60 = _mapping(report.get("v60"))
    usage = _mapping(report.get("usage"))
    diffs = _mapping(report.get("diffs"))

    lines = [
        "# Archived Run Comparison",
        "",
        "## Eligibility",
        "",
        f"- Trustworthy comparison: `{eligibility.get('trustworthy', False)}`",
        f"- Status: `{eligibility.get('status', 'unknown')}`",
    ]
    reasons = _list(eligibility.get("reasons"))
    if reasons:
        lines.append("- Reasons:")
        for reason in reasons:
            lines.append(f"  - {reason}")
    else:
        lines.append("- Reasons: none")

    lines.extend(
        [
            "",
            "## Health",
            "",
            "```json",
            json.dumps(health, indent=2, ensure_ascii=False, sort_keys=True),
            "```",
            "",
            "## V60 And Retrieval",
            "",
            "```json",
            json.dumps(v60, indent=2, ensure_ascii=False, sort_keys=True),
            "```",
            "",
            "## Usage",
            "",
            "```json",
            json.dumps(usage, indent=2, ensure_ascii=False, sort_keys=True),
            "```",
            "",
            "## Answer Diff",
            "",
            _render_diff_block(_mapping(diffs.get("revised_answer"))),
            "",
            "## Memo Diff",
            "",
            _render_diff_block(_mapping(diffs.get("memo"))),
            "",
        ]
    )
    return "\n".join(lines)


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True)


class ArchivedRun:
    def __init__(self, *, run_dir: Path, result: dict[str, Any], revised_answer: str, memo_markdown: str):
        self.run_dir = run_dir
        self.result = result
        self.revised_answer = revised_answer
        self.memo_markdown = memo_markdown


def _load_archived_run(path: Path) -> ArchivedRun:
    run_dir = path.parent if path.name == "result.json" else path
    result_path = run_dir / "result.json"
    if not result_path.exists():
        raise FileNotFoundError(f"Missing result.json under {run_dir}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    revised_path = run_dir / "revised.txt"
    memo_path = run_dir / "memo.md"
    revised_answer = (
        revised_path.read_text(encoding="utf-8")
        if revised_path.exists()
        else str(result.get("revised_answer") or "")
    )
    memo_markdown = memo_path.read_text(encoding="utf-8") if memo_path.exists() else ""
    return ArchivedRun(
        run_dir=run_dir,
        result=result,
        revised_answer=revised_answer.strip(),
        memo_markdown=memo_markdown.strip(),
    )


def _comparison_eligibility(left: ArchivedRun, right: ArchivedRun) -> dict[str, Any]:
    reasons: list[str] = []
    for side, run in (("left", left), ("right", right)):
        health = _mapping(run.result.get("run_health"))
        overall = _text(health.get("overall")) or "unknown"
        if overall in UNTRUSTED_OVERALL_STATUSES:
            reasons.append(f"{side}: run_health.overall={overall}")
        capture = _text(health.get("capture"))
        if capture in {"critical", "degraded"}:
            reasons.append(f"{side}: capture={capture}")
        product = _text(health.get("product_output_health"))
        if product == "unsafe":
            reasons.append(f"{side}: product_output_health=unsafe")
        ledger = _text(health.get("v60_consideration_ledger"))
        if ledger in UNTRUSTED_LEDGER_STATUSES:
            reasons.append(f"{side}: v60_consideration_ledger={ledger}")
        for detail in _list(health.get("issue_details")):
            detail_map = _mapping(detail)
            severity = _text(detail_map.get("severity"))
            code = _text(detail_map.get("code"))
            if severity in UNTRUSTED_OVERALL_STATUSES and code:
                reasons.append(f"{side}: issue {code} severity={severity}")

    return {
        "trustworthy": not reasons,
        "status": "trustworthy" if not reasons else "not_trustworthy",
        "reasons": reasons,
    }


def _run_summary(run: ArchivedRun) -> dict[str, Any]:
    return {
        "run_dir": str(run.run_dir),
        "result_path": str(run.run_dir / "result.json"),
    }


def _health_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    health = _mapping(result.get("run_health"))
    return {
        "overall": health.get("overall"),
        "capture": health.get("capture"),
        "issues": _list(health.get("issues")),
        "issue_details": _list(health.get("issue_details")),
        "product_output_health": health.get("product_output_health"),
        "product_output_leak_count": health.get("product_output_leak_count"),
        "quote_fabrication_count": health.get("quote_fabrication_count"),
        "v60_consideration_ledger": health.get("v60_consideration_ledger"),
    }


def _v60_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    enrichment = _mapping(result.get("v60_enrichment"))
    telemetry = _mapping(enrichment.get("telemetry"))
    candidate_pool = _mapping(enrichment.get("candidate_pool"))
    validation = _mapping(result.get("v60_consideration_validation"))
    return {
        "status": enrichment.get("status"),
        "embedding_mode": candidate_pool.get("embedding_mode"),
        "selected_model_ids": _list(telemetry.get("selected_model_ids")),
        "selected_chunk_count": telemetry.get("selected_chunk_count"),
        "selected_chunk_effect_types": _mapping(telemetry.get("selected_chunk_effect_types")),
        "ledger_status": validation.get("status"),
        "ledger_disposition_counts": _mapping(validation.get("disposition_counts")),
    }


def _usage_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    usage = _mapping(result.get("usage_summary"))
    return {
        "estimated_total_cost_usd": usage.get("estimated_total_cost_usd"),
        "run_id": usage.get("run_id"),
    }


def _diff_text(left: str, right: str) -> dict[str, Any]:
    left_lines = (left or "").splitlines()
    right_lines = (right or "").splitlines()
    diff = list(
        difflib.unified_diff(
            left_lines,
            right_lines,
            fromfile="left",
            tofile="right",
            lineterm="",
        )
    )
    return {
        "changed": left_lines != right_lines,
        "unified_diff": diff,
    }


def _render_diff_block(diff_payload: Mapping[str, Any]) -> str:
    diff = _list(diff_payload.get("unified_diff"))
    if not diff:
        return "_No textual diff._"
    return "```diff\n" + "\n".join(str(line) for line in diff) + "\n```"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _text(value: Any) -> str:
    return str(value or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument("left", type=Path, help="Left archived run dir or result.json")
    parser.add_argument("right", type=Path, help="Right archived run dir or result.json")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    report = compare_archived_runs(args.left, args.right)
    rendered = render_json(report) if args.format == "json" else render_markdown(report)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
