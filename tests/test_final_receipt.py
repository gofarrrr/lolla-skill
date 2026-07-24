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
    assert (
        "Reconsideration stayed in this conversation's context; "
        "it was not an external check."
    ) in receipt
    assert "Cost estimate: $0.06." in receipt
    assert receipt.endswith(
        "The memo and archive were saved privately. Cost estimate: $0.06."
    )
    assert "/tmp/" not in receipt


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
    assert "it was not an external check" in receipt
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


def test_final_receipt_names_terminal_provider_call_loss_directly() -> None:
    receipt = build_final_receipt(
        result_payload={
            "run_health": {
                "overall": "partial",
                "issues": ["provider_call_terminal_loss"],
                "provider_failed_call_count": 1,
                "provider_failed_call_stages": ["pass2"],
                "provider_failed_tendency_ids": [
                    "availability-misweighing-tendency"
                ],
            },
            "usage_summary": {"estimated_total_cost_usd": 0.055599},
        },
        result_path=Path("/tmp/lolla_run_result.json"),
        observatory_url="",
        observatory_status="unavailable",
        archive_path="/tmp/archive/run",
    )

    assert "Run health is partial" in receipt
    assert "1 provider-backed reasoning call ended without a usable result" in receipt
    assert "pass2" in receipt
    assert "availability-misweighing-tendency" in receipt
    assert "was not retried" in receipt


def test_final_receipt_names_partial_passage_quality_check_exactly() -> None:
    receipt = build_final_receipt(
        result_payload={
            "run_health": {
                "overall": "partial",
                "issues": ["bullshit_index_partial"],
                "bullshit_index_evaluation_failures": 1,
                "bullshit_index_evaluation_count": 12,
            },
            "usage_summary": {"estimated_total_cost_usd": 0.055599},
        },
        result_path=Path("/tmp/lolla_run_result.json"),
        observatory_url="",
        observatory_status="unavailable",
        archive_path="/tmp/archive/run",
    )

    assert (
        "1 of 12 passage-quality checks returned no usable judgment and was "
        "not retried"
    ) in receipt
    assert "core audit and revised answer are present" in receipt
    assert "inspect the archived artifacts for details" not in receipt


def test_final_receipt_discloses_untrusted_live_terminal_capture() -> None:
    receipt = build_final_receipt(
        result_payload={
            "run_health": {
                "overall": "healthy",
                "issues": [],
                "live_output_health": "not_checked",
            },
            "usage_summary": {"estimated_total_cost_usd": 0.01},
        },
        result_path=Path("/tmp/lolla_run_result.json"),
        observatory_url="",
        observatory_status="skipped",
        archive_path="/tmp/archive/run",
    )

    assert (
        "The saved narration does not independently verify everything shown "
        "in the live terminal."
    ) in receipt
