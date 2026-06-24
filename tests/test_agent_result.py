from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.system_b.agent_result import (
    AGENT_RESULT_SCHEMA_VERSION,
    build_agent_result,
    write_agent_result,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_agent_result_contract_for_healthy_archived_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "conversation.txt").write_text("conversation", encoding="utf-8")
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "ok",
            "extraction": {
                "decision_situation": "Founder deciding whether to pivot",
            },
        },
    )
    _write_json(
        run_dir / "result.json",
        {
            "status": "ok",
            "run_health": {
                "overall": "healthy",
                "product_output_health": "clean",
                "live_output_health": "not_checked",
                "issues": [],
                "issue_details": [],
            },
            "delta_card": {
                "findings": [
                    {
                        "severity": "medium",
                        "challenge_statement": "The answer treated customer interest as evidence before naming a reversal gate.",
                    }
                ]
            },
            "memo_what_changed": (
                "- Add a customer evidence gate before pivoting.\n"
                "- Keep the current product alive until the test fails."
            ),
            "memo_take_back_or_set_aside": (
                "I would take back the clean recommendation to pivot now."
            ),
            "structural_coverage_card": {
                "gap_questions": [
                    {
                        "questions": [
                            "What evidence would make the pivot unacceptable?",
                            "Which customer segment pays first?",
                        ]
                    }
                ]
            },
            "usage_summary": {
                "estimated_total_cost_usd": 0.42,
                "cost_estimate_state": "complete",
                "pricing_table_version": "2026-06-24",
            },
            "revised_answer": "Pivot only after a customer evidence gate.",
        },
    )
    (run_dir / "revised.txt").write_text(
        "Pivot only after a customer evidence gate.",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Decision memo\n", encoding="utf-8")
    (run_dir / "reasoning_trace.json").write_text("{}", encoding="utf-8")

    payload = build_agent_result(
        run_dir,
        run_id="run123",
        case_id="founder-pivot",
        created_at="2026-06-24T12:00:00Z",
        observatory_url="http://localhost:8080",
        observatory_status="live",
    )

    assert payload["schema_version"] == AGENT_RESULT_SCHEMA_VERSION
    assert payload["status"] == "ok"
    assert payload["run_health_overall"] == "healthy"
    assert payload["risk_mode"] == "standard"
    assert payload["caller_action"] == "use_revised_answer"
    assert payload["main_counter_pressure"] == (
        "The answer treated customer interest as evidence before naming a reversal gate."
    )
    assert payload["position_changed"] is True
    assert payload["changed_advice_summary"] == [
        "Add a customer evidence gate before pivoting.",
        "Keep the current product alive until the test fails.",
    ]
    assert payload["take_backs"] == [
        "I would take back the clean recommendation to pivot now."
    ]
    assert payload["human_questions"] == [
        "What evidence would make the pivot unacceptable?",
        "Which customer segment pays first?",
    ]
    assert payload["artifact_status"]["memo"] == "present"
    assert payload["artifact_paths"]["archive"] == str(run_dir)
    assert payload["artifact_paths"]["observatory_url"] == "http://localhost:8080"
    assert payload["usage"]["estimated_total_cost_usd"] == 0.42


def test_agent_result_blocks_automatic_use_for_partial_or_unsafe_run(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_json(
        run_dir / "extraction.json",
        {"status": "ok", "extraction": {"decision_situation": "Career decision"}},
    )
    _write_json(
        run_dir / "result.json",
        {
            "status": "ok",
            "run_health": {
                "overall": "partial",
                "product_output_health": "unsafe",
                "live_output_health": "not_checked",
                "issues": ["product_output_leak"],
            },
            "revised_answer": "Use the revised answer only after inspection.",
        },
    )
    (run_dir / "revised.txt").write_text(
        "Use the revised answer only after inspection.",
        encoding="utf-8",
    )
    (run_dir / "memo.md").write_text("# Memo\n", encoding="utf-8")

    payload = build_agent_result(
        run_dir,
        run_id="run456",
        created_at="2026-06-24T12:00:00Z",
    )

    assert payload["status"] == "degraded"
    assert payload["caller_action"] == "do_not_use_run_degraded"
    assert payload["do_not_act_before"] == [
        "Inspect or rerun Lolla before relying on this audit result."
    ]
    assert "not suitable for automatic agent action" in payload["notes"][0]


def test_agent_result_high_stakes_clean_run_asks_user_first(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_json(
        run_dir / "extraction.json",
        {"status": "ok", "extraction": {"decision_situation": "Legal decision"}},
    )
    _write_json(
        run_dir / "result.json",
        {
            "status": "ok",
            "risk_mode": "high_stakes",
            "run_health": {
                "overall": "healthy",
                "product_output_health": "clean",
                "live_output_health": "not_checked",
                "issues": [],
            },
            "revised_answer": "Ask counsel before signing.",
        },
    )
    (run_dir / "revised.txt").write_text("Ask counsel before signing.", encoding="utf-8")
    (run_dir / "memo.md").write_text("# Memo\n", encoding="utf-8")

    payload = build_agent_result(
        run_dir,
        run_id="run999",
        created_at="2026-06-24T12:00:00Z",
    )

    assert payload["status"] == "ok"
    assert payload["risk_mode"] == "high_stakes"
    assert payload["caller_action"] == "ask_user_first"


def test_agent_result_handles_capture_critical_without_result(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    _write_json(
        run_dir / "extraction.json",
        {
            "status": "capture_critical",
            "extraction": {"decision_situation": "Missing capture"},
        },
    )

    path, payload = write_agent_result(
        run_dir,
        run_id="run789",
        case_id="missing-capture",
        created_at="2026-06-24T12:00:00Z",
        tmp_copy_path=tmp_path / "lolla_run789_agent_result.json",
    )

    assert path == run_dir / "agent_result.json"
    assert path.exists()
    assert (tmp_path / "lolla_run789_agent_result.json").exists()
    assert payload["status"] == "incomplete"
    assert payload["status_reason"] == "conversation capture was marked critical"
    assert payload["caller_action"] == "do_not_use_run_degraded"
    assert payload["artifact_status"]["result"] == "missing"
    assert payload["artifact_status"]["memo"] == "missing"
