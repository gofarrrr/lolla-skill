from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.compare_archived_runs import (
    compare_archived_runs,
    render_markdown,
)


def _write_run(
    run_dir: Path,
    *,
    revised: str,
    memo: str,
    run_health: dict,
    cost: float = 0.0,
) -> None:
    run_dir.mkdir(parents=True)
    (run_dir / "result.json").write_text(
        json.dumps(
            {
                "run_health": run_health,
                "revised_answer": revised,
                "v60_enrichment": {
                    "status": "active",
                    "telemetry": {
                        "selected_chunk_count": 2,
                        "selected_model_ids": ["opportunity-cost"],
                        "selected_chunk_effect_types": {"missing_option": 1},
                    },
                    "candidate_pool": {"embedding_mode": "off"},
                },
                "v60_consideration_validation": {
                    "status": run_health.get("v60_consideration_ledger", "valid"),
                    "disposition_counts": {"used": 1, "rejected": 1},
                },
                "usage_summary": {"estimated_total_cost_usd": cost},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "revised.txt").write_text(revised, encoding="utf-8")
    (run_dir / "memo.md").write_text(memo, encoding="utf-8")


def test_compare_archived_runs_starts_with_eligibility_before_answer_diff(tmp_path: Path) -> None:
    left = tmp_path / "case" / "run-a"
    right = tmp_path / "case" / "run-b"
    _write_run(
        left,
        revised="Ask what option disappears if we accept.",
        memo="# Decision note\n\nThe advice now names the displaced option.",
        run_health={
            "overall": "healthy",
            "capture": "good",
            "product_output_health": "clean",
            "product_output_leak_count": 0,
            "v60_consideration_ledger": "valid",
            "issues": [],
            "issue_details": [],
        },
        cost=0.21,
    )
    _write_run(
        right,
        revised="The answer cites a V60 chunk.",
        memo="# Decision note\n\nThe advice now leaks a ledger.",
        run_health={
            "overall": "degraded",
            "capture": "good",
            "product_output_health": "unsafe",
            "product_output_leak_count": 2,
            "v60_consideration_ledger": "valid",
            "issues": ["product_output_leak"],
            "issue_details": [
                {"code": "product_output_leak", "severity": "degraded", "axis": "product_output"}
            ],
        },
        cost=0.32,
    )

    report = compare_archived_runs(left, right)
    markdown = render_markdown(report)

    assert report["eligibility"]["trustworthy"] is False
    assert any("product_output_health=unsafe" in reason for reason in report["eligibility"]["reasons"])
    assert markdown.index("## Eligibility") < markdown.index("## Answer Diff")
    assert "## Memo Diff" in markdown
    assert "selected_chunk_effect_types" in markdown
    assert "estimated_total_cost_usd" in markdown


def test_compare_archived_runs_cli_emits_json(tmp_path: Path) -> None:
    left = tmp_path / "left"
    right = tmp_path / "right"
    clean_health = {
        "overall": "healthy",
        "capture": "good",
        "product_output_health": "clean",
        "product_output_leak_count": 0,
        "v60_consideration_ledger": "valid",
        "issues": [],
    }
    _write_run(left, revised="A", memo="# Memo\n\nA", run_health=clean_health)
    _write_run(right, revised="B", memo="# Memo\n\nB", run_health=clean_health)

    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "compare_archived_runs.py"),
            str(left),
            str(right),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["eligibility"]["trustworthy"] is True
    assert payload["diffs"]["revised_answer"]["changed"] is True
