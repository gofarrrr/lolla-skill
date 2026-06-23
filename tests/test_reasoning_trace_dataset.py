from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from engine.system_b.reasoning_trace_dataset import (
    build_dataset_records,
    summarize_dataset_records,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "export_reasoning_trace_dataset.py"


def _write_trace(
    archive_root: Path,
    *,
    case_id: str,
    run_id: str,
    adequacy_status: str,
    future_review_ready: bool,
    lenses: list[dict[str, object]],
    candidate_commitments: list[dict[str, object]] | None = None,
) -> Path:
    run_dir = archive_root / case_id / run_id
    run_dir.mkdir(parents=True)
    trace = {
        "schema_version": "lolla.reasoning_trace.v0.2",
        "trace_id": f"trace_{run_id}",
        "created_at": "2026-06-22T12:00:00Z",
        "case": {
            "case_id": case_id,
            "run_id": run_id,
            "decision_situation": f"Decision for {case_id}",
        },
        "capture": {"capture_health": "good"},
        "process": {
            "run_health": {"overall": "healthy"},
            "audit_summary": {
                "triggered_tendency_ids": ["inconsistency-avoidance"],
                "detected_tendency_ids": ["inconsistency-avoidance"],
            },
            "graph_survival": {
                "status": "ready",
                "lane_candidate_count": 4,
                "raw_lane_signal_count": 6,
                "embedding_hit_count": 3,
                "selected_card_count": 2,
                "answer_delta_model_count": 1,
                "private_guardrail_model_count": 1,
                "confirming_support_model_count": 0,
                "suppressed_signal_count": 2,
                "suppressed_model_count": 2,
                "budget_suppressed_signal_count": 1,
                "budget_suppressed_model_count": 1,
                "unadjudicated_candidate_count": 1,
                "top_budget_suppressed_lenses": [
                    {"model_id": "risk-vs-uncertainty"},
                ],
            },
            "usage": {"estimated_total_cost_usd": 0.05},
        },
        "user_usefulness_review": {
            "status": "collected" if future_review_ready else "not_collected",
            "rating": 4 if future_review_ready else None,
            "helped_change_view": True if future_review_ready else None,
            "would_reuse": True if future_review_ready else None,
        },
        "outcome_review_state": {
            "status": "available" if future_review_ready else "not_started",
            "review_count": 1 if future_review_ready else 0,
        },
        "trace_adequacy": {
            "status": adequacy_status,
            "future_review_ready": future_review_ready,
            "error_analysis_ready": True,
            "missing_context": [] if future_review_ready else ["thin evidence"],
        },
        "artifacts": [{"path": "result.json"}],
        "missing_artifacts": [],
        "reasoning_lenses": lenses,
        "model_calls": [{"stage": "lane2.companion"}],
        "candidate_commitments": candidate_commitments or [],
        "decision_packets": [],
        "outcome_reviews": [],
    }
    path = run_dir / "reasoning_trace.json"
    path.write_text(json.dumps(trace), encoding="utf-8")
    return path


def test_reasoning_trace_dataset_records_and_summary(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    _write_trace(
        archive_root,
        case_id="case-a",
        run_id="run-a",
        adequacy_status="sufficient",
        future_review_ready=True,
        lenses=[
            {
                "lens_id": "opportunity-cost",
                "selected": True,
                "surfaced": True,
                "rejection_reasons": [],
            },
            {
                "lens_id": "premortem",
                "selected": False,
                "surfaced": False,
                "rejection_reasons": ["not actually used"],
            },
        ],
        candidate_commitments=[
            {
                "candidate_id": "commitment_run-a_001",
                "kind": "recommendation",
                "escalation_recommended": True,
            }
        ],
    )
    _write_trace(
        archive_root,
        case_id="case-b",
        run_id="run-b",
        adequacy_status="thin",
        future_review_ready=False,
        lenses=[
            {
                "lens_id": "opportunity-cost",
                "selected": True,
                "surfaced": False,
                "rejection_reasons": [],
            }
        ],
    )

    records = build_dataset_records(archive_root)
    summary = summarize_dataset_records(records)

    assert [record["run_id"] for record in records] == ["run-a", "run-b"]
    assert records[0]["source_trace_path"] == "case-a/run-a/reasoning_trace.json"
    assert records[0]["selected_reasoning_lens_ids"] == ["opportunity-cost"]
    assert records[0]["rejected_reasoning_lens_ids"] == ["premortem"]
    assert records[0]["model_call_count"] == 1
    assert records[0]["model_call_record_count"] == 1
    assert records[0]["candidate_commitment_count"] == 1
    assert records[0]["graph_survival_status"] == "ready"
    assert records[0]["graph_suppressed_signal_count"] == 2
    assert records[0]["graph_suppressed_model_count"] == 2
    assert records[0]["graph_budget_suppressed_signal_count"] == 1
    assert records[0]["graph_budget_suppressed_model_count"] == 1
    assert records[0]["top_budget_suppressed_lens_ids"] == ["risk-vs-uncertainty"]
    assert records[0]["user_usefulness_status"] == "collected"
    assert records[0]["user_usefulness_rating"] == 4
    assert records[0]["outcome_review_status"] == "available"
    assert summary["trace_count"] == 2
    assert summary["future_review_ready_count"] == 1
    assert summary["traces_with_candidate_commitments_count"] == 1
    assert summary["candidate_commitment_count"] == 1
    assert summary["decision_packet_count"] == 0
    assert summary["outcome_review_count"] == 0
    assert summary["traces_with_graph_survival_count"] == 2
    assert summary["graph_lane_candidate_count"] == 8
    assert summary["graph_raw_lane_signal_count"] == 12
    assert summary["graph_embedding_hit_count"] == 6
    assert summary["graph_selected_card_count"] == 4
    assert summary["graph_answer_delta_model_count"] == 2
    assert summary["graph_private_guardrail_model_count"] == 2
    assert summary["graph_suppressed_signal_count"] == 4
    assert summary["graph_suppressed_model_count"] == 4
    assert summary["graph_budget_suppressed_signal_count"] == 2
    assert summary["graph_budget_suppressed_model_count"] == 2
    assert summary["graph_unadjudicated_candidate_count"] == 2
    assert summary["user_usefulness_status_counts"] == {
        "collected": 1,
        "not_collected": 1,
    }
    assert summary["outcome_review_status_counts"] == {
        "available": 1,
        "not_started": 1,
    }
    assert summary["user_usefulness_rating_average"] == 4.0
    assert summary["user_usefulness_rating_count"] == 1
    assert summary["trace_adequacy_status_counts"] == {"sufficient": 1, "thin": 1}
    assert summary["reasoning_lens_trace_counts"]["opportunity-cost"] == 2
    assert summary["selected_reasoning_lens_trace_counts"]["opportunity-cost"] == 2
    assert summary["rejected_reasoning_lens_trace_counts"]["premortem"] == 1
    assert summary["triggered_tendency_trace_counts"] == {
        "inconsistency-avoidance": 2
    }


def test_export_reasoning_trace_dataset_cli_writes_outputs(tmp_path: Path) -> None:
    archive_root = tmp_path / "runs"
    out_path = tmp_path / "dataset.jsonl"
    summary_path = tmp_path / "summary.json"
    _write_trace(
        archive_root,
        case_id="case-a",
        run_id="run-a",
        adequacy_status="sufficient",
        future_review_ready=True,
        lenses=[
            {
                "lens_id": "opportunity-cost",
                "selected": True,
                "surfaced": True,
                "rejection_reasons": [],
            }
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            str(archive_root),
            "--out",
            str(out_path),
            "--summary-out",
            str(summary_path),
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "exported 1 traces" in result.stdout
    records = [
        json.loads(line)
        for line in out_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert records[0]["trace_id"] == "trace_run-a"
    assert summary["selected_reasoning_lens_trace_counts"] == {
        "opportunity-cost": 1
    }
