from __future__ import annotations

from pathlib import Path

from scripts.skill.render_final_receipt import build_final_receipt


def test_final_receipt_reports_live_observatory_when_liveness_checked() -> None:
    receipt = build_final_receipt(
        result_payload={
            "run_health": {"overall": "healthy", "issues": []},
            "usage_summary": {"estimated_total_cost_usd": 0.055599},
        },
        result_path=Path("/tmp/lolla_run_result.json"),
        observatory_url="http://localhost:8084",
        observatory_status="live",
        archive_path="/tmp/archive/run",
    )

    assert "Observatory is live at http://localhost:8084." in receipt
    assert "Cost estimate: $0.06." in receipt
    assert receipt.endswith("Archived to /tmp/archive/run.")


def test_final_receipt_does_not_claim_dead_observatory_is_live() -> None:
    receipt = build_final_receipt(
        result_payload={
            "run_health": {"overall": "healthy", "issues": []},
            "usage_summary": {"estimated_total_cost_usd": 0.01},
        },
        result_path=Path("/tmp/lolla_run_result.json"),
        observatory_url="http://localhost:8084",
        observatory_status="unavailable",
        archive_path="/tmp/archive/run",
    )

    assert "Observatory is live at" not in receipt
    assert "Observatory did not stay live; memo and archive are still available." in receipt


def test_final_receipt_names_vendor_boundary_partial_health_directly() -> None:
    receipt = build_final_receipt(
        result_payload={
            "run_health": {
                "overall": "partial",
                "issues": ["vendor_boundary_reasoning_leak"],
            },
            "usage_summary": {"estimated_total_cost_usd": 0.055599},
        },
        result_path=Path("/tmp/lolla_run_result.json"),
        observatory_url="",
        observatory_status="unavailable",
        archive_path="/tmp/archive/run",
    )

    assert "Run health is partial" in receipt
    assert "reasoning details despite reasoning being disabled" in receipt
    assert "inspect the Observatory" not in receipt
